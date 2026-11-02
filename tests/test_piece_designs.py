"""Equipment authoring: visible comparisons are temporary, saved sets are immutable."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import build_opener, ProxyHandler, Request
from tests.test_game_workshop import serve, TEST_ROOT
from tests.test_workshop_collections import empty_project
from piece_designs import PieceDesigns, DEFAULTS
from library_store import InvalidDesign
from workspace_store import ProjectLibrary


class PieceDesignTests(unittest.TestCase):
    def setUp(self):self.temp=tempfile.TemporaryDirectory(dir=TEST_ROOT);self.root=Path(self.temp.name);self.store=PieceDesigns(self.root)
    def tearDown(self):self.temp.cleanup()
    def payload(self,**changes):return dict(name='Eigener Figurensatz',settings={**DEFAULTS,**changes},parent_id=None)

    def test_invalid_geometry_types_colours_and_unknown_properties_are_rejected(self):
        for change in (dict(set='conquest'),dict(size=True),dict(size=181),dict(base=.66),dict(height=float('nan')),dict(light='url(https://example.com)'),dict(style='unknown')):
            with self.subTest(change=change),self.assertRaises(InvalidDesign):self.store.save(self.payload(**change))
        invalid=self.payload();invalid['settings']['role']='pawn'
        with self.assertRaises(InvalidDesign):self.store.save(invalid)

    def test_preview_comparison_role_and_zoom_are_not_saved_as_equipment(self):
        view=dict(role='king',side='both',fit=False,comparison=True,scale=125)
        page=self.store.preview(self.payload(size=150)['settings'],view=view)
        raw=page.split('<script id="piece-config" type="application/json">')[1].split('</script>')[0];cfg=json.loads(raw)
        self.assertEqual(cfg['view'],view);self.assertEqual(cfg['settings']['figure']['size'],150)
        record=self.store.save(self.payload(size=150));self.assertNotIn('view',record);self.assertNotIn('role',record['settings'])
        for change in (dict(role='../../file'),dict(scale=True),dict(comparison=1),dict(side='invalid')):
            with self.assertRaises(InvalidDesign):self.store.preview(DEFAULTS,view={**view,**change})
        source=(serve.HERE/'piece-authoring.js').read_text(encoding='utf-8')
        self.assertIn("from '/models.js'",source);self.assertIn('buildPiece(role,s,side,1,flat)',source)
        self.assertIn('const box=v.fit?actual:fixed',source)

    def test_colours_and_proportions_remain_independent(self):
        settings=self.store.settings(self.payload(size=140,head=.8,base=1.1,light='#debe71',dark='#214a39')['settings'])
        self.assertEqual((settings['height'],settings['stem']),(1,1));self.assertEqual(settings['dark'],'#214a39')
        self.assertEqual(settings['light'],'#debe71');self.assertEqual(settings['size'],140)
        checkers=self.store.save(self.payload(set='checkers',representation='2d'))
        self.assertEqual(self.store.asset(checkers)['model_id'],'pieces-checkers-v1')

    def test_versions_exact_reopen_and_project_handoff(self):
        first=self.store.save(self.payload());path=self.store.directory/(first['id']+'.json');before=path.read_bytes()
        second=self.store.save({**self.payload(size=135,light='#c29b64'),'parent_id':first['id']})
        self.assertEqual(path.read_bytes(),before);self.assertEqual(PieceDesigns(self.root).get(second['id']),second)
        library=ProjectLibrary(self.root,self.root/'buttons');asset=next(a for a in library.assets() if a['id']==second['id']);self.assertEqual(asset['snapshot'],second)
        project=empty_project('Figurensätze');project['items']=[dict(kind='pieces',id=second['id'])];saved=library.save_project(project)
        self.assertEqual(library.handoff(saved['id'])['project']['items'][0]['snapshot'],second)

    def test_corrupt_records_are_kept_and_mismatched_ids_rejected(self):
        good=self.store.save(self.payload());bad=self.store.directory/('piece-'+'0'*32+'.json');bad.write_text('{',encoding='utf-8')
        rows,count=self.store.list();self.assertEqual(rows,[good]);self.assertEqual(count,1);self.assertEqual(bad.read_text(encoding='utf-8'),'{')
        wrong=deepcopy(good);wrong['id']='piece-'+'1'*32;(self.store.directory/(good['id']+'.json')).write_text(json.dumps(wrong),encoding='utf-8')
        with self.assertRaises(InvalidDesign):self.store.get(good['id'])
        with self.assertRaises(InvalidDesign):self.store.get('../../private')

    def test_local_http_editor_preview_save_and_origin_guard(self):
        server=serve.make_server(0,self.root/'library',self.root/'buttons');thread=Thread(target=server.serve_forever,daemon=True);thread.start()
        opener=build_opener(ProxyHandler({}));base='http://127.0.0.1:'+str(server.server_port)
        def post(path,value,origin=None):return Request(base+path,data=json.dumps(value).encode(),headers={'Content-Type':'application/json','Origin':origin or base})
        try:
            with opener.open(base+'/api/piece-designs') as response:self.assertEqual(json.load(response)['defaults'],DEFAULTS)
            with opener.open(post('/api/piece-designs/preview',dict(settings=DEFAULTS))) as response:self.assertIn('piece-config',json.load(response)['html'])
            with opener.open(post('/api/piece-designs',self.payload())) as response:asset=json.load(response)['asset'];self.assertEqual(response.status,201)
            with opener.open(base+asset['preview']) as response:self.assertIn("script-src 'self'",response.headers['Content-Security-Policy']);response.read()
            for path in ('/piece-editor.js','/piece-editor.css','/piece-components/authoring.js'):
                with opener.open(base+path) as response:self.assertEqual(response.status,200);response.read()
            with self.assertRaises(HTTPError) as error:opener.open(post('/api/piece-designs',self.payload(),origin='https://example.com'))
            self.assertEqual(error.exception.code,403);error.exception.close()
        finally:server.shutdown();server.server_close();thread.join(3)


if __name__=='__main__':unittest.main()
