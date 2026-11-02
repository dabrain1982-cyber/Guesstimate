"""Boards are two representations with finite source configurations and property contracts."""
from copy import deepcopy
from pathlib import Path
import tempfile
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import build_opener, ProxyHandler
from tests.test_game_workshop import serve, TEST_ROOT, project as legacy_project
from tests.test_workshop_collections import empty_project, payload
from board_library import BoardLibrary, COVERAGE, CONQUEST
from dice_library import fragment
from library_store import InvalidDesign
from workspace_store import ProjectLibrary


class BoardLibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.boards=BoardLibrary()

    def test_two_models_and_shared_sources_cover_all_existing_games(self):
        assets=self.boards.assets()
        self.assertEqual({a['model_id'] for a in assets},{'board-2d-v1','board-3d-v1'})
        self.assertEqual(len(assets),6)
        self.assertEqual({c['game'] for c in COVERAGE},{'Guesstimate','Guesstimate Party','Perfect','Playtable','Würfeltisch','Kniffel','Mäxchen','Conquest'})
        dice=next(a for a in assets if a['snapshot']['source_key']=='dice-table')
        self.assertEqual(dice['games'],['Würfeltisch','Kniffel','Mäxchen'])
        self.assertEqual(dice['snapshot']['settings']['size'],dict(width=1290,depth=685,unit='Quellpixel'))
        for asset in assets:
            self.assertEqual(set(asset['snapshot']['parameters']),{'size','shape','image'})
            self.assertNotIn('territories',asset['snapshot'])
            self.assertFalse(asset['editable'])
        for c in COVERAGE:self.assertTrue((CONQUEST.parents[1]/c['source']).is_file())
        assets[0]['snapshot']['settings']['size']['width']=99
        self.assertNotEqual(self.boards.assets()[0]['snapshot']['settings']['size']['width'],99)

    def test_original_table_factory_and_source_drift_guard(self):
        source=(CONQUEST/'scene.js').read_text(encoding='utf-8')
        factory=self.boards.conquest_factory()
        self.assertIn(fragment(source,'function seededRandom(seed)','// Each visible surface has one material.'),factory)
        self.assertNotIn('createRemoteTurn(',factory)
        self.assertNotIn('mountTableSurface(',factory)
        asset=self.boards.records['boards-3d-conquest'];before=deepcopy(asset['snapshot'])
        try:
            asset['snapshot']['evidence'][0]['sha256']='0'*64
            with self.assertRaises(InvalidDesign):self.boards.preview(asset['id'])
        finally:asset['snapshot']=before
        page=self.boards.preview('boards-2d-playtable')
        self.assertIn('card-free-area',page)
        self.assertNotIn('data-status-url',page)
        self.assertNotIn('data-csrf',page)
        self.assertNotIn('<form',page)

    def test_exact_board_configurations_reuse_handoff_and_legacy_drafts(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as folder:
            store=ProjectLibrary(Path(folder)/'library',Path(folder)/'buttons')
            project=empty_project('Bretter')
            project['items']=[dict(kind='board',id=key) for key in ('boards-3d-conquest','boards-2d-playtable','boards-2d-dice-table')]
            saved=store.save_project(project)
            other=empty_project('Wiederverwendung');other['items']=project['items']
            self.assertEqual(store.save_project(other)['items'],saved['items'])
            reopened=ProjectLibrary(store.directory,store.buttons_directory)
            self.assertEqual(reopened.handoff(saved['id'])['project']['items'],saved['items'])
            old=store.save_project(legacy_project());view=store.project_view(old)
            original=deepcopy(next(a for a in view['items'] if a['kind']=='board'))
            self.assertEqual(next(a for a in store.save_project(payload(view))['items'] if a['kind']=='board'),original)
            draft=store.save_element(dict(kind='board',name='Eigener Brettentwurf',settings=deepcopy(original['snapshot']['settings'])))
            before=(store.directory/'elements'/(draft['id']+'.json')).read_bytes()
            asset=next(a for a in store.assets() if a['id']==draft['id'])
            self.assertEqual(asset['model_id'],'board-3d-v1')
            self.assertEqual(asset['snapshot'],draft)
            self.assertEqual((store.directory/'elements'/(draft['id']+'.json')).read_bytes(),before)

    def test_http_routes_are_local_and_not_per_game_state(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as folder:
            server=serve.make_server(0,Path(folder)/'library',Path(folder)/'buttons')
            thread=Thread(target=server.serve_forever,daemon=True);thread.start()
            opener=build_opener(ProxyHandler({}));base='http://127.0.0.1:'+str(server.server_port)
            try:
                for path in ('/api/boards/boards-3d-conquest/preview?interactive=1','/board-source/conquest.js','/board-source/map.png','/board-source/camera.js','/api/boards/boards-2d-dice-table/preview'):
                    with opener.open(base+path) as response:
                        self.assertEqual(response.status,200)
                        if path.startswith('/api/'):
                            self.assertIn("connect-src 'self'",response.headers['Content-Security-Policy'])
                for path in ('/api/boards/game-123/preview','/board-source/../../PROJEKTLOG.md'):
                    with self.assertRaises(HTTPError) as error:opener.open(base+path)
                    self.assertIn(error.exception.code,(400,404));error.exception.close()
            finally:server.shutdown();server.server_close();thread.join(3)


if __name__=='__main__':unittest.main()
