"""Real storage roundtrips and loopback HTTP boundaries, with isolated test data."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import Request, ProxyHandler, build_opener

HERE = Path(__file__).resolve().parents[1]/'offline-preview/game-workshop-v1'
TEST_ROOT = HERE.parents[1]/'runtime/game-workshop-unit-tests'
TEST_ROOT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(HERE))
SPEC = importlib.util.spec_from_file_location('game_workshop_serve', HERE/'serve.py')
serve = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(serve)
from library_store import Library, defaults, KINDS, PRESETS, settings, InvalidDesign
sys.path.pop(0)


def project():
    return dict(schema=1, name='Schachprobe', notes='Brett später auch für Dame.', elements=defaults(),
                included={k:True for k in KINDS}, sources={k:None for k in KINDS}, buttons=[])


class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=TEST_ROOT)
        self.directory = Path(self.temp.name)
        self.store = Library(self.directory/'library', self.directory/'buttons')

    def tearDown(self):
        self.assertTrue(self.directory.resolve().is_relative_to(TEST_ROOT.resolve()))
        self.temp.cleanup()

    def test_all_eight_presets_and_defaults_validate(self):
        self.assertEqual(len(KINDS), 8)
        for kind, cfg in defaults().items():
            self.assertEqual(settings(kind, cfg), cfg)
        for preset in PRESETS:
            settings(preset['kind'], preset['settings'])

    def test_variant_project_reopen_and_handoff_freeze_the_exact_selection(self):
        p = project()
        p['elements']['board']['columns'] = 10
        e = self.store.save_element(dict(name='Zehn Spalten',kind='board',settings=p['elements']['board']))
        p['sources']['board'] = e['id']
        first = self.store.save_project(p)
        original = (self.store.directory/'projects'/(first['id']+'.json')).read_bytes()
        p['elements']['board']['columns'] = 8
        p['sources']['board'] = None
        second = self.store.save_project(p)
        reopened = Library(self.store.directory,self.store.buttons_directory)
        self.assertEqual(len(reopened.list('projects')[0]), 2)
        self.assertNotEqual(first['id'],second['id'])
        self.assertEqual((self.store.directory/'projects'/(first['id']+'.json')).read_bytes(), original)
        handoff = reopened.handoff(first['id'])
        self.assertEqual(handoff['project']['elements']['board']['columns'],10)
        self.assertIn('Zehn', e['name'])
        self.assertIn('Spalten: 10',handoff['brief'])
        self.assertTrue((self.store.directory/'handoffs'/(handoff['id']+'.md')).is_file())

    def test_changed_or_wrong_kind_reference_is_rejected(self):
        p = project()
        p['sources']['board'] = PRESETS[0]['id']
        p['elements']['board']['columns'] = 10
        with self.assertRaises(InvalidDesign): self.store.save_project(p)
        p['elements']['board']['columns'] = 8
        p['sources']['board'] = next(v['id'] for v in PRESETS if v['kind']=='pieces')
        with self.assertRaises(InvalidDesign): self.store.save_project(p)

    def test_nan_wrong_types_unknown_fields_and_path_traversal_rejected(self):
        for key, value in [('columns',float('nan')),('columns',True),('rows',4.2),('rows',1000),('light','red')]:
            cfg = defaults()['board'];cfg[key] = value
            with self.assertRaises(InvalidDesign): settings('board', cfg)
        cfg=defaults()['board'];cfg['secret']='x'
        with self.assertRaises(InvalidDesign): settings('board',cfg)
        with self.assertRaises(InvalidDesign): self.store.handoff('../../app')
        with self.assertRaises(InvalidDesign): self.store.handoff([])
        p=project();del p['included']['room']
        with self.assertRaises(InvalidDesign): self.store.save_project(p)
        self.assertFalse(self.store.directory.exists())

    def test_button_snapshots_are_read_only_and_complete(self):
        self.store.buttons_directory.mkdir()
        button=dict(id='original-button',kind='button',name='Mein Holz',settings={'material':'wood'},contour={'points':[1,2,3]})
        path=self.store.buttons_directory/'button.json';path.write_text(json.dumps(button),encoding='utf-8')
        before=path.read_bytes()
        p=project();p['buttons']=[button['id']]
        saved=self.store.save_project(p)
        self.assertEqual(saved['button_snapshots'],[button])
        self.assertEqual(path.read_bytes(),before)
        p['buttons']=['missing']
        with self.assertRaises(InvalidDesign): self.store.save_project(p)

    def test_corrupt_record_survives_and_is_reported(self):
        target=self.store.directory/'elements';target.mkdir(parents=True)
        path=target/'broken.json';path.write_text('{',encoding='utf-8')
        records, unreadable=self.store.list('elements')
        self.assertEqual((records,unreadable),([],1))
        self.assertEqual(path.read_text(),'{')


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(dir=TEST_ROOT)
        cls.server=serve.make_server(0,Path(cls.temp.name)/'library',Path(cls.temp.name)/'buttons')
        cls.thread=Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.url=f'http://127.0.0.1:{cls.server.server_port}'
        cls.opener=build_opener(ProxyHandler({}))

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join(3)
        assert Path(cls.temp.name).resolve().is_relative_to(TEST_ROOT.resolve())
        cls.temp.cleanup()

    def request(self,path,body=None,origin=None):
        headers={'Content-Type':'application/json'}
        if origin:headers['Origin']=origin
        request=Request(self.url+path,data=json.dumps(body).encode() if body is not None else None,headers=headers)
        return self.opener.open(request,timeout=3)

    def test_http_save_and_handoff_roundtrip(self):
        with self.request('/api/projects',project()) as response:
            saved=json.load(response)['project'];self.assertEqual(response.status,201)
        with self.request('/api/handoff',{'project_id':saved['id']}) as response:
            value=json.load(response);self.assertEqual(value['handoff']['project_id'],saved['id'])
        with self.request('/api/library') as response:
            self.assertTrue(any(v['id']==saved['id'] for v in json.load(response)['projects']))

    def test_foreign_origins_cannot_write(self):
        with self.assertRaises(HTTPError) as error:self.request('/api/projects',project(),'https://elsewhere.example')
        self.assertEqual(error.exception.code,403)
        error.exception.close()

    def test_private_and_source_paths_not_served(self):
        for path in ['/../app.py','/library_store.py','/shared/../app.py','/design-library/projects/a.json']:
            with self.assertRaises(HTTPError) as error:self.request(path)
            self.assertEqual(error.exception.code,404)
            error.exception.close()

    def test_lobby_renders_canonical_profile_and_escapes_text(self):
        cfg=defaults()['lobby'];cfg['title']='<img src=x onerror=alert(1)>'
        with self.request('/api/lobby',cfg) as response:html=json.load(response)['html']
        self.assertIn('variant-a-profile-canonical',html)
        self.assertIn('data-lobby-game="workshop"',html)
        self.assertNotIn('<img src=x',html)
        self.assertIn('&lt;img src=x',html)


if __name__=='__main__':unittest.main()
