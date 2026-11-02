"""Authoring contracts: independent layers, safe local images and immutable versions."""
from copy import deepcopy
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import tempfile
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import build_opener, ProxyHandler, Request
from PIL import Image

from tests.test_game_workshop import serve, TEST_ROOT
from tests.test_workshop_collections import empty_project
from board_designs import BoardDesigns, DEFAULTS
from image_store import ImageStore
from library_store import InvalidDesign
from workspace_store import ProjectLibrary


class BoardDesignTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=TEST_ROOT);self.root=Path(self.temp.name)
        self.images=ImageStore(self.root);self.store=BoardDesigns(self.root,self.images)

    def tearDown(self):self.temp.cleanup()

    def payload(self,**settings):return dict(name='Mein eigenes Brett',settings={**DEFAULTS,**settings},parent_id=None)

    def test_shapes_ranges_and_css_or_url_injection_are_checked_before_preview_and_save(self):
        for change in [dict(width=True),dict(height=161),dict(thickness=.35),dict(shape='hexagon'),dict(width=60,height=61,shape='round'),
                       dict(surface='url(https://example.com)'),dict(image_id='../../private.png'),dict(pattern_opacity=101),dict(rows=2.5)]:
            with self.subTest(change=change),self.assertRaises(InvalidDesign):self.store.preview(self.payload(**change)['settings'])
        with self.assertRaises(InvalidDesign):self.store.save({**self.payload(), 'url':'https://example.com/image.png'})

    def test_surface_image_and_fields_remain_independent_and_use_one_factory(self):
        settings=self.payload(image_id='conquest-map',pattern='grid',surface='#18332f',pattern_opacity=40)['settings']
        page=self.store.preview(settings)
        raw=page.split('<script id="board-config" type="application/json">')[1].split('</script>')[0]
        cfg=json.loads(raw)
        self.assertEqual(cfg['settings']['design'],settings)
        self.assertEqual(cfg['settings']['image']['url'],'/board-source/map.png')
        self.assertEqual(settings['surface'],'#18332f')
        self.assertIn('src="/board-components/stage.js"',page)
        self.assertNotIn('<form',page)
        stage=(serve.HERE/'board-stage.js').read_text(encoding='utf-8')
        self.assertIn("import('/models.js')",stage)
        self.assertIn("buildBoard(design,cfg.representation==='2d')",stage)

    def test_comparison_and_view_scale_are_temporary_and_not_part_of_the_board(self):
        settings=self.payload(width=90,height=60)['settings'];view=dict(fit=False,comparison=True,scale=120)
        page=self.store.preview(settings,view=view)
        raw=page.split('<script id="board-config" type="application/json">')[1].split('</script>')[0]
        self.assertEqual(json.loads(raw)['view'],view)
        record=self.store.save(self.payload(width=90,height=60))
        self.assertNotIn('view',record)
        self.assertNotIn('comparison',record['settings'])
        with self.assertRaises(InvalidDesign):self.store.preview(settings,view={**view,'scale':True})
        with self.assertRaises(InvalidDesign):self.store.preview(settings,view={**view,'scale':1000})

    def test_saved_versions_and_project_handoff_keep_exact_settings(self):
        first=self.store.save(self.payload(shape='round',width=70,height=70,pattern='none'))
        path=self.store.directory/(first['id']+'.json');before=path.read_bytes()
        second=self.store.save({**self.payload(width=90,height=60,image_id='slate'), 'parent_id':first['id']})
        self.assertEqual(path.read_bytes(),before)
        reopened=BoardDesigns(self.root,self.images)
        self.assertEqual(reopened.get(first['id']),first)
        self.assertEqual(reopened.get(second['id'])['parent_id'],first['id'])
        library=ProjectLibrary(self.root,self.root/'buttons');asset=next(a for a in library.assets() if a['id']==second['id'])
        self.assertEqual(asset['snapshot'],second)
        project=empty_project('Bretter prüfen');project['items']=[dict(kind='board',id=second['id'])]
        saved=library.save_project(project)
        handoff=library.handoff(saved['id'])
        self.assertEqual(handoff['project']['items'][0]['snapshot'],second)

    def test_uploaded_image_is_local_and_tampering_is_detected(self):
        raw=BytesIO();Image.new('RGB',(100,70),'green').save(raw,format='PNG')
        image=self.images.import_image(raw.getvalue(),'Brettbild.png','background')
        record=self.store.save(self.payload(image_id=image['id'],pattern='none'))
        self.assertEqual(record['image_snapshot']['sha256'],sha256(raw.getvalue()).hexdigest())
        changed=deepcopy(record);changed['image_snapshot']['url']='https://example.com/image.png'
        with self.assertRaises(InvalidDesign):self.store.validate_record(changed)
        image_path=self.root/image['file'];image_path.write_bytes(b'changed')
        with self.assertRaises(InvalidDesign):self.store.get(record['id'])

    def test_malformed_record_is_preserved_and_does_not_hide_good_records(self):
        good=self.store.save(self.payload())
        bad=self.store.directory/('board-'+'0'*32+'.json');bad.write_text('{',encoding='utf-8')
        rows,count=self.store.list();self.assertEqual(count,1);self.assertEqual(rows,[good]);self.assertEqual(bad.read_text(encoding='utf-8'),'{')
        with self.assertRaises(InvalidDesign):self.store.get('../../etc')

    def test_http_preview_save_and_origin_rejection(self):
        server=serve.make_server(0,self.root/'library',self.root/'buttons');thread=Thread(target=server.serve_forever,daemon=True);thread.start()
        opener=build_opener(ProxyHandler({}));base='http://127.0.0.1:'+str(server.server_port)
        def post(path,value,origin=None):return Request(base+path,data=json.dumps(value).encode(),headers={'Content-Type':'application/json','Origin':origin or base})
        try:
            with opener.open(base+'/api/board-designs') as response:self.assertEqual(json.load(response)['defaults'],DEFAULTS)
            with opener.open(post('/api/board-designs/preview',dict(settings=DEFAULTS))) as response:self.assertIn('board-config',json.load(response)['html'])
            with opener.open(post('/api/board-designs',self.payload())) as response:asset=json.load(response)['asset'];self.assertEqual(response.status,201)
            with opener.open(base+asset['preview']+'?interactive=1') as response:self.assertIn("script-src 'self'",response.headers['Content-Security-Policy'])
            with opener.open(base+'/api/library') as response:self.assertTrue(any(a['id']==asset['id'] for a in json.load(response)['assets']))
            for path in ('/board-editor.js','/board-editor.css'):
                with opener.open(base+path) as response:self.assertEqual(response.status,200)
            with self.assertRaises(HTTPError) as error:opener.open(post('/api/board-designs',self.payload(),origin='https://example.com'))
            self.assertEqual(error.exception.code,403);error.exception.close()
        finally:server.shutdown();server.server_close();thread.join(3)


if __name__=='__main__':unittest.main()
