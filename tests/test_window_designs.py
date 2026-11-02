"""Window authoring preserves canonical contents and older saved versions."""
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
from window_designs import WindowDesigns, DEFAULTS
from source_buttons import SourceButtons
from source_windows import SourceWindows
from library_store import InvalidDesign
from workspace_store import ProjectLibrary


class WindowDesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.sources=SourceWindows(SourceButtons())

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=TEST_ROOT);self.base=Path(self.temp.name)
        self.store=WindowDesigns(self.base,self.sources);self.source=self.store.config()['sources'][0]

    def tearDown(self):self.temp.cleanup()

    def payload(self,**settings):return dict(source_id=self.source['id'],name='Mein grünes Nachholfenster',settings={**DEFAULTS,**settings},parent_id=None)

    def test_only_first_explicit_window_model_is_editable_and_defaults_keep_original_markup(self):
        self.assertEqual(len(self.store.config()['sources']),1)
        self.assertEqual(self.store.style(DEFAULTS),'')
        preview=self.store.preview(self.source['id'],DEFAULTS)
        self.assertIn(self.source['snapshot']['rendered_markup'],preview)
        self.assertIn('body inert',preview)
        self.assertIn('alle 3 verpassten runden nachholen',preview)
        self.assertNotIn('<script',preview)

    def test_design_changes_only_window_frame_and_copy_colours_without_replacing_child_buttons(self):
        before=(serve.ROOT/'templates/home.html').read_bytes()
        changed=self.store.preview(self.source['id'],self.payload(scale=110,radius=8,surface='#234b3d',heading='#fff2d6',text='#efe6d1',border='#9caf88',border_width=2)['settings'])
        self.assertIn('transform:scale(1.1)!important',changed)
        self.assertIn('background:#234b3d!important',changed)
        self.assertIn('.catchup-panel h2{color:#fff2d6!important}',changed)
        self.assertIn(self.source['snapshot']['rendered_markup'],changed)
        self.assertEqual((serve.ROOT/'templates/home.html').read_bytes(),before)

    def test_invalid_css_ranges_unknown_sources_and_tampered_records_are_rejected(self):
        for settings in (dict(surface='url(https://example.com)'),dict(scale=True),dict(scale=101),dict(radius=41),dict(border_width=-1)):
            with self.assertRaises(InvalidDesign):self.store.save(self.payload(**settings))
        wrong=self.payload();wrong['source_id']='../../home.html'
        with self.assertRaises(InvalidDesign):self.store.save(wrong)
        record=self.store.save(self.payload());changed=deepcopy(record);changed['source_snapshot']['rendered_markup']='<script>bad()</script>'
        with self.assertRaises(InvalidDesign):self.store.validate_record(changed)

    def test_saved_versions_reopen_and_project_handoff_keep_exact_selection(self):
        library=ProjectLibrary(self.base/'library',self.base/'buttons');store=library.window_designs
        first=store.save(self.payload(surface='#234b3d'));path=store.directory/(first['id']+'.json');before=path.read_bytes()
        value=self.payload(radius=4);value['parent_id']=first['id'];second=store.save(value)
        reopened=ProjectLibrary(library.directory,library.buttons_directory)
        records,bad=reopened.window_designs.list();self.assertEqual(bad,0);self.assertEqual(len(records),2)
        self.assertEqual(reopened.window_designs.get(second['id']),second)
        project=empty_project('Fensterprobe');project['items']=[dict(kind='windows',id=second['id'])]
        saved=reopened.save_project(project);self.assertEqual(saved['items'][0]['snapshot'],second)
        self.assertEqual(reopened.handoff(saved['id'])['project']['items'],saved['items'])
        self.assertEqual(path.read_bytes(),before)

    def test_http_preview_save_assets_and_origin_boundary(self):
        server=serve.make_server(0,self.base/'http-library',self.base/'http-buttons');thread=Thread(target=server.serve_forever,daemon=True);thread.start()
        opener=build_opener(ProxyHandler({}));root=f'http://127.0.0.1:{server.server_port}'
        def post(path,payload,origin=None):
            headers={'Content-Type':'application/json'}
            if origin:headers['Origin']=origin
            return opener.open(Request(root+path,data=json.dumps(payload).encode(),headers=headers),timeout=10)
        try:
            with opener.open(root+'/api/window-designs') as response:self.assertEqual(len(json.load(response)['sources']),1)
            with post('/api/window-designs/preview',dict(source_id=self.source['id'],settings=DEFAULTS)) as response:self.assertIn('body inert',json.load(response)['html'])
            with self.assertRaises(HTTPError) as caught:post('/api/window-designs',self.payload(),'https://example.com')
            self.assertEqual(caught.exception.code,403);caught.exception.close()
            with post('/api/window-designs',self.payload(surface='#234b3d')) as response:asset=json.load(response)['asset']
            with opener.open(root+asset['preview']) as response:
                self.assertIn('script-src \'none\'',response.headers['Content-Security-Policy'])
                self.assertIn('background:#234b3d!important',response.read().decode())
            with opener.open(root+'/api/library') as response:self.assertTrue(any(a['id']==asset['id'] for a in json.load(response)['assets']))
            for filename in ('window-editor.js','window-editor.css'):
                with opener.open(root+'/'+filename) as response:self.assertEqual(response.status,200)
        finally:server.shutdown();server.server_close();thread.join(3)


if __name__=='__main__':unittest.main()
