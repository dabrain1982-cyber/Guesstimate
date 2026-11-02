"""Whole equipment sets, shared renderers, old selections and local HTTP boundary."""
from copy import deepcopy
from pathlib import Path
import tempfile
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import Request, build_opener, ProxyHandler
import json
from tests.test_game_workshop import serve, TEST_ROOT
from tests.test_workshop_collections import empty_project
from card_library import CardLibrary
from library_store import InvalidDesign
from workspace_store import ProjectLibrary

class CardLibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.cards=CardLibrary()

    def test_component_set_member_hierarchy_and_legacy_choices(self):
        assets=self.cards.assets()
        self.assertEqual(len(assets),14)
        self.assertEqual(sum(a['record_role']=='finite_set' for a in assets),12)
        self.assertEqual({a['model_id'] for a in assets},{'cards-movable-v1','cards-display-v1'})
        for size in (32,52,55,104,110):
            for mode in ('movable','display'):
                pack=self.cards.records[f'cards-set-{mode}-standard-{size}']['snapshot']['set']
                self.assertEqual(len(pack['members']),size)
                self.assertEqual(len({m['id'] for m in pack['members']}),size)
                self.assertEqual(sum(m['original']['joker'] for m in pack['members']),{55:3,110:6}.get(size,0))
        self.assertEqual(self.cards.records['cards-component-movable']['snapshot']['geometry']['triangles'],44)
        self.assertIsNone(self.cards.records['cards-component-display']['snapshot']['geometry'])
        self.assertNotIn('cards-display-joker',self.cards.records)
        self.assertIn('data-card-key="Joker"',self.cards.preview('cards-display-joker'))
        self.assertIn('data-card-back="cardBack_red5.png"',self.cards.preview('cards-movable-red5'))
        with self.assertRaises(InvalidDesign):self.cards.preview('cards-display-perfect-term-ssp-begriff-001')

    def test_member_preview_validated_and_shared_renderer(self):
        key='cards-set-display-standard-55'
        member=self.cards.records[key]['snapshot']['set']['members'][-1]['id']
        page=self.cards.preview(key,True,member)
        self.assertIn('data-card-key="Joker"',page)
        self.assertIn('src="/card-components/stage.js"',page)
        with self.assertRaises(InvalidDesign):self.cards.preview(key,member='alaska')
        original=deepcopy(self.cards.records[key]['snapshot'])
        try:
            self.cards.records[key]['snapshot']['evidence'][0]['sha256']='0'*64
            with self.assertRaises(InvalidDesign):self.cards.preview(key)
        finally:self.cards.records[key]['snapshot']=original
        for path in ('/assets/kenney/../../../PROJEKTLOG.md','/assets/mehrasaur/../../serve.py'):
            self.assertIsNone(self.cards.file_path(path))

    def test_whole_set_survives_reuse_reload_and_handoff(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as folder:
            store=ProjectLibrary(Path(folder)/'library',Path(folder)/'buttons')
            chosen=[store.cards.records['cards-set-movable-standard-32'],store.cards.records['cards-set-display-conquest-countries']]
            project=empty_project('Kartensätze');project['items']=[dict(kind='cards',id=a['id']) for a in chosen]
            saved=store.save_project(project)
            other=empty_project('Wiederverwendung');other['items']=project['items']
            self.assertEqual(store.save_project(other)['items'],saved['items'])
            reopened=ProjectLibrary(store.directory,store.buttons_directory)
            self.assertEqual(reopened.handoff(saved['id'])['project']['items'],saved['items'])
            self.assertEqual([a['snapshot']['set'] for a in saved['items']],[a['snapshot']['set'] for a in chosen])
            self.assertFalse(list((store.directory/'elements').glob('*.json')))

    def test_http_member_routes_and_local_boundary(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as folder:
            server=serve.make_server(0,Path(folder)/'library',Path(folder)/'buttons')
            thread=Thread(target=server.serve_forever,daemon=True);thread.start()
            base='http://127.0.0.1:'+str(server.server_port);opener=build_opener(ProxyHandler({}))
            try:
                with opener.open(base+'/api/library') as response:data=json.load(response)
                self.assertEqual(sum(a.get('component')=='approved-card-v1' for a in data['assets']),14)
                with opener.open(base+'/api/cards/cards-set-display-conquest-countries/preview?member=joker-1&interactive=1') as response:
                    self.assertIn("form-action 'none'",response.headers['Content-Security-Policy'])
                    self.assertIn('Joker',response.read().decode())
                for path,headers in [('/api/cards/cards-set-display-standard-32/preview?member=alaska',{}),('/api/library',{'Host':'external.example'})]:
                    with self.assertRaises(HTTPError) as error:opener.open(Request(base+path,headers=headers))
                    self.assertIn(error.exception.code,(400,403));error.exception.close()
            finally:server.shutdown();server.server_close();thread.join(3)

if __name__=='__main__':unittest.main()