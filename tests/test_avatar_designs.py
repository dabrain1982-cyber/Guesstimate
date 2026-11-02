"""Avatar source fidelity, pixel reuse, immutable versions and local HTTP."""
import base64
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import tempfile
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import build_opener,ProxyHandler,Request
from tests.test_game_workshop import serve,TEST_ROOT
from tests.test_image_workshop import fixture
from tests.test_workshop_collections import empty_project
from avatar_designs import AvatarDesigns,DEFAULTS
from image_store import ImageStore
from library_store import InvalidDesign
from workspace_store import ProjectLibrary

class AvatarDesignTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=TEST_ROOT);self.root=Path(self.temp.name);self.images=ImageStore(self.root)
        self.source=self.images.import_image(fixture(),'Original.png','avatars');self.store=AvatarDesigns(self.root,self.images)
    def tearDown(self):self.temp.cleanup()
    def payload(self,**settings):return dict(name='Mein Avatar',source_id=self.source['id'],recipe=dict(x=400,y=0,width=300,height=300,output_width=512),settings={**DEFAULTS,**settings},parent_id=None)
    def test_preview_uses_the_exact_shared_crop_pixels(self):
        p=self.payload();page=self.store.preview(p['source_id'],p['recipe'],p['settings']);cfg=json.loads(page.split('<script id="avatar-config" type="application/json">')[1].split('</script>')[0])
        raw,_,_=self.images.render(p['source_id'],p['recipe']);self.assertEqual(base64.b64decode(cfg['image'].split(',')[1]),raw)
        self.assertIn('/avatar-renderer.js',page);self.assertTrue(cfg['interactive'])
        self.assertFalse(json.loads(self.store.preview(p['source_id'],p['recipe'],p['settings'],False).split('type="application/json">')[1].split('</script>')[0])['interactive'])
    def test_invalid_shapes_colours_sizes_and_crop_rejected(self):
        for patch in (dict(shape='url(x)'),dict(frame='red'),dict(size=True),dict(size=181),dict(size=102),dict(frame_width=-1)):
            with self.subTest(patch=patch),self.assertRaises(InvalidDesign):self.store.save(self.payload(**patch))
        for recipe in (dict(x=0,y=0,width=500,height=400,output_width=512),dict(x=0,y=0,width=300,height=300,output_width=600),dict(x=750,y=0,width=300,height=300,output_width=512)):
            with self.assertRaises(InvalidDesign):self.store.save({**self.payload(),'recipe':recipe})
        with self.assertRaises(InvalidDesign):self.store.save({**self.payload(),'profile_id':42})
    def test_immutable_versions_and_handoff_preserve_whole_design(self):
        first=self.store.save(self.payload(shape='round',size=150));path=self.store.directory/(first['id']+'.json');before=path.read_bytes()
        second=self.store.save({**self.payload(frame='#b39f49',size=60),'parent_id':first['id']});self.assertEqual(path.read_bytes(),before)
        self.assertEqual(AvatarDesigns(self.root,ImageStore(self.root)).get(second['id']),second)
        library=ProjectLibrary(self.root,self.root/'buttons');asset=next(a for a in library.assets() if a['id']==second['id']);self.assertEqual(asset['snapshot'],second)
        project=empty_project('Avatare');project['items']=[dict(kind='avatars',id=second['id'])];saved=library.save_project(project)
        self.assertEqual(library.handoff(saved['id'])['project']['items'][0]['snapshot'],second);self.assertNotIn('view',second)
    def test_original_bytes_and_saved_variant_are_not_rewritten(self):
        original=(self.root/self.source['file']).read_bytes();variant=self.images.save_variant(dict(source_id=self.source['id'],name='Alter Ausschnitt',kind='avatars',recipe=dict(x=0,y=0,width=400,height=400,output_width=200)))
        before=(self.root/variant['file']).read_bytes();record=self.store.save({**self.payload(),'source_id':variant['id']})
        self.assertEqual(record['source_id'],self.source['id']);self.assertEqual(record['source_snapshot']['sha256'],sha256(original).hexdigest())
        self.assertEqual((self.root/self.source['file']).read_bytes(),original);self.assertEqual((self.root/variant['file']).read_bytes(),before)
        (self.root/self.source['file']).write_bytes(original+b'changed')
        with self.assertRaises(InvalidDesign):self.store.get(record['id'])
        self.assertEqual(self.store.list()[1],1)
    def test_corruption_and_traversal_are_preserved_or_rejected(self):
        self.store.save(self.payload());bad=self.store.directory/('avatar-'+'0'*32+'.json');bad.write_text('{',encoding='utf-8');self.assertEqual(self.store.list()[1],1);self.assertEqual(bad.read_text(),'{')
        with self.assertRaises(InvalidDesign):self.store.get('../../private')
    def test_public_crop_metadata_and_canonical_component_are_reused(self):
        images=ImageStore(self.root,serve.EXISTING_ASSETS);store=AvatarDesigns(self.root,images)
        self.assertEqual(store.config()['crops']['avatar-a01'],dict(scale=1.7,top=-48))
        renderer=(serve.HERE/'avatar-renderer.js').read_text(encoding='utf-8');self.assertIn("import {createPlayerPortrait} from '/shared/player-portrait.js'",renderer)
        self.assertNotIn('player-portrait-frame',renderer)
    def test_local_http_config_save_preview_and_origin(self):
        server=serve.make_server(0,self.root/'http-library',self.root/'buttons');thread=Thread(target=server.serve_forever,daemon=True);thread.start();opener=build_opener(ProxyHandler({}));base='http://127.0.0.1:'+str(server.server_port)
        def post(path,value,origin=None):return Request(base+path,data=json.dumps(value).encode(),headers={'Content-Type':'application/json','Origin':origin or base})
        p=self.payload();p['source_id']='avatar-a01';p['recipe']=dict(x=288,y=395,width=824,height=824,output_width=512)
        try:
            with opener.open(base+'/api/avatar-designs') as response:self.assertEqual(json.load(response)['defaults'],DEFAULTS)
            with opener.open(post('/api/avatar-designs/preview',{k:p[k] for k in ('source_id','recipe','settings')})) as response:self.assertIn('avatar-config',json.load(response)['html'])
            with opener.open(post('/api/avatar-designs',p)) as response:asset=json.load(response)['asset'];self.assertEqual(response.status,201)
            with opener.open(base+asset['preview']+'?interactive=1') as response:self.assertIn('avatar-config',response.read().decode());self.assertIn("script-src 'self'",response.headers['Content-Security-Policy'])
            for path in ('/avatar-editor.js','/avatar-renderer.js','/shared/player-portrait.js'):
                with opener.open(base+path) as response:self.assertEqual(response.status,200);response.read()
            with self.assertRaises(HTTPError) as error:opener.open(post('/api/avatar-designs',p,origin='https://example.com'))
            self.assertEqual(error.exception.code,403);error.exception.close()
        finally:server.shutdown();server.server_close();thread.join(3)

if __name__=='__main__':unittest.main()
