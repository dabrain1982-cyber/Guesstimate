"""The workshop creates independent assets; projects collect many exact variants."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from tests.test_game_workshop import serve, project as legacy_project, TEST_ROOT
from workspace_store import ProjectLibrary
from button_bridge import storage
from workshop_catalog import PRESENTATION
from library_store import InvalidDesign


def empty_project(name='Meine neue Idee'):
    return dict(schema=2,project_key=None,name=name,notes='',items=[],presentation={k:'undecided' for k in PRESENTATION})


def payload(record):
    return {**{k:deepcopy(record[k]) for k in ('schema','project_key','name','notes','presentation')},
            'items':[dict(kind=a['kind'],id=a['id']) for a in record['items']]}


def button(name='Eigener Button'):
    catalog=storage.CATALOG
    return dict(schema_version=2,name=name,notes='',kind='button',parent_id=None,settings=deepcopy(catalog['defaults']),
                review={key:'open' for key,_ in catalog['review_dimensions']},
                contour=dict(template='comic',points=[dict(x=x,y=y,round=r) for x,y,r in catalog['contours']['comic']]))


class CollectionsTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=TEST_ROOT)
        self.root=Path(self.temp.name)
        self.store=ProjectLibrary(self.root/'library',self.root/'buttons')

    def tearDown(self):
        self.assertTrue(self.root.resolve().is_relative_to(TEST_ROOT.resolve()))
        self.temp.cleanup()

    def test_empty_project_has_no_prefabricated_game_or_assets(self):
        saved=self.store.save_project(empty_project())
        self.assertEqual(saved['items'],[])
        self.assertEqual(saved['project_key'],saved['id'])
        self.assertEqual(set(saved['presentation'].values()),{'undecided'})
        self.assertEqual(len(self.store.project_groups()),1)

    def test_many_buttons_and_shared_variants_keep_original_snapshots(self):
        a=self.store.button_store.save(button('Start'))
        b=self.store.button_store.save(button('Zurück'))
        original=(self.store.buttons_directory/(a['id']+'.json')).read_bytes()
        p=empty_project();p['items']=[dict(kind='buttons',id=v['id']) for v in [a,b]]
        first=self.store.save_project(p)
        self.assertEqual(len(first['items']),2)
        self.assertEqual(first['items'][0]['snapshot'],json.loads(original))
        q=empty_project('Eine andere Idee');q['items']=[dict(kind='buttons',id=a['id'])]
        second=self.store.save_project(q)
        self.assertEqual(second['items'][0]['snapshot'],first['items'][0]['snapshot'])
        update=payload(first);update['notes']='Fragen im Interview ergänzen.'
        revised=self.store.save_project(update)
        self.assertEqual(revised['project_key'],first['project_key'])
        self.assertNotEqual(revised['id'],first['id'])
        self.assertEqual(len(self.store.project_groups()),2)
        self.assertEqual((self.store.buttons_directory/(a['id']+'.json')).read_bytes(),original)
        handoff=self.store.handoff(revised['id'])
        self.assertEqual(len(handoff['project']['items']),2)
        self.assertIn('Interview',handoff['brief'])

    def test_old_chess_map_is_read_without_mutation_and_only_migrated_on_save(self):
        old=self.store.save_project(legacy_project())
        path=self.store.directory/'projects'/(old['id']+'.json');before=path.read_bytes()
        groups=self.store.project_groups()
        self.assertEqual(len(groups),1)
        adapted=groups[0]['project']
        self.assertEqual(adapted['schema'],2)
        self.assertEqual(adapted['project_key'],old['id'])
        self.assertEqual(path.read_bytes(),before)
        self.assertEqual(len(list(path.parent.glob('*.json'))),1)
        new=self.store.save_project(payload(adapted))
        self.assertEqual(new['legacy_source'],old)
        self.assertEqual(path.read_bytes(),before)
        self.assertEqual(len(self.store.project_groups()),1)

    def test_unknown_duplicate_and_forged_items_are_rejected(self):
        p=empty_project();p['items']=[dict(kind='buttons',id='missing')]
        with self.assertRaises(InvalidDesign):self.store.save_project(p)
        a=self.store.button_store.save(button())
        p['items']=[dict(kind='buttons',id=a['id'])]*2
        with self.assertRaises(InvalidDesign):self.store.save_project(p)
        p['items']=[dict(kind='buttons',id=a['id'],snapshot={'forged':True})]
        with self.assertRaises(InvalidDesign):self.store.save_project(p)

    def test_removal_creates_new_version_without_erasing_older_collection(self):
        a=self.store.button_store.save(button());p=empty_project();p['items']=[dict(kind='buttons',id=a['id'])]
        first=self.store.save_project(p);update=payload(first);update['items']=[]
        latest=self.store.save_project(update)
        self.assertEqual(latest['items'],[])
        stored=json.loads((self.store.directory/'projects'/(first['id']+'.json')).read_text(encoding='utf-8'))
        self.assertEqual(len(stored['items']),1)
        self.assertEqual(len(self.store.project_groups()[0]['versions']),2)

    def test_project_choices_and_identity_are_validated(self):
        p=empty_project();p['presentation']['mode']='automatic-chess'
        with self.assertRaises(InvalidDesign):self.store.save_project(p)
        p=empty_project();p['project_key']='../../elsewhere'
        with self.assertRaises(InvalidDesign):self.store.save_project(p)

    def test_legacy_item_can_be_restored_from_an_older_project_version(self):
        old=self.store.save_project(legacy_project())
        adapted=self.store.project_view(old)
        first=self.store.save_project(payload(adapted))
        empty=payload(first);empty['items']=[]
        self.store.save_project(empty)
        restored=self.store.save_project(payload(first))
        self.assertEqual(restored['items'],first['items'])


class IntegratedHTTPTests(unittest.TestCase):
    def test_embedded_button_files_and_save_share_the_existing_store(self):
        from threading import Thread
        from urllib.request import Request,build_opener,ProxyHandler
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as directory:
            server=serve.make_server(0,Path(directory)/'library',Path(directory)/'buttons')
            thread=Thread(target=server.serve_forever,daemon=True);thread.start()
            base='http://127.0.0.1:'+str(server.server_port);opener=build_opener(ProxyHandler({}))
            try:
                with opener.open(base+'/button-editor/renderer.js',timeout=3) as r:
                    self.assertEqual(hashlib.sha256(r.read()).digest(),hashlib.sha256((serve.ROOT/'offline-preview/button-workshop-v1/renderer.js').read_bytes()).digest())
                request=Request(base+'/api/recipes',data=json.dumps(button()).encode(),headers={'Content-Type':'application/json'})
                with opener.open(request,timeout=3) as r:saved=json.load(r)['recipe']
                with opener.open(base+'/api/library',timeout=3) as r:library=json.load(r)
                self.assertTrue(any(a['kind']=='buttons' and a['id']==saved['id'] for a in library['assets']))
                self.assertEqual(library['project_groups'],[])
                self.assertTrue((Path(directory)/'buttons'/(saved['id']+'.json')).is_file())
            finally:
                server.shutdown();server.server_close();thread.join(3)
            self.assertTrue(Path(directory).resolve().is_relative_to(TEST_ROOT.resolve()))


if __name__=='__main__':unittest.main()
