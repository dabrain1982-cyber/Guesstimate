"""Existing physics/flat dice are two configurable components, never individual rolls."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import build_opener, ProxyHandler
from tests.test_game_workshop import serve, TEST_ROOT, project as legacy_project
from tests.test_workshop_collections import empty_project, payload
from dice_library import DiceLibrary, TABLE, CONQUEST, fragment
from library_store import InvalidDesign
from workspace_store import ProjectLibrary


class DiceLibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.dice=DiceLibrary()

    def test_exactly_two_renderers_with_count_and_faces_as_properties(self):
        assets=self.dice.assets()
        self.assertEqual({a['id'] for a in assets},{'dice-physics-v1','dice-display-v1'})
        self.assertEqual({a['representation'] for a in assets},{'2d','3d'})
        for a in assets:
            self.assertEqual(a['record_role'],'component')
            self.assertEqual(a['snapshot']['settings']['count'],2)
            self.assertEqual(len(a['snapshot']['settings']['imprints']),6)
            self.assertEqual(set(a['snapshot']['parameters']),{'count','imprints','palette'})
            self.assertFalse(a['editable'])
        assets[0]['snapshot']['settings']['count']=5
        self.assertEqual(len(self.dice.assets()),2)
        self.assertEqual(self.dice.assets()[0]['snapshot']['settings']['count'],2)

    def test_adapters_reuse_exact_source_functions_and_refuse_source_drift(self):
        factory=self.dice.physics_factory();source=TABLE.read_text(encoding='utf-8')
        self.assertIn(fragment(source,'const animateRoll =','const renderConcealed ='),factory)
        self.assertIn(fragment(source,'const localizeThemeAssets =','const makeMiniDie ='),factory)
        self.assertNotIn('performAction(',factory)
        self.assertNotIn('room.dataset.stateUrl',factory)
        self.assertIn(fragment((CONQUEST/'attack.js').read_text(encoding='utf-8'),'function showRolls(','function record('),self.dice.flat_factory())
        record=self.dice.records['dice-physics-v1'];before=deepcopy(record['snapshot'])
        try:
            record['snapshot']['evidence'][0]['sha256']='0'*64
            with self.assertRaises(InvalidDesign):self.dice.preview(record['id'])
        finally:record['snapshot']=before
        self.assertNotIn('dddice.js',self.dice.preview('dice-display-v1'))

    def test_project_reuse_handoff_and_legacy_dice_keep_exact_snapshots(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as folder:
            store=ProjectLibrary(Path(folder)/'library',Path(folder)/'buttons')
            dice=[a for a in store.assets() if a['kind']=='dice']
            self.assertEqual(len(dice),2)
            project=empty_project('Zwei Würfelvarianten');project['items']=[dict(kind='dice',id=a['id']) for a in dice]
            saved=store.save_project(project)
            other=empty_project('Wiederverwendung');other['items']=project['items']
            self.assertEqual(store.save_project(other)['items'],saved['items'])
            reopened=ProjectLibrary(store.directory,store.buttons_directory)
            self.assertEqual(reopened.handoff(saved['id'])['project']['items'],saved['items'])
            old=store.save_project(legacy_project());view=store.project_view(old)
            original=deepcopy(next(a for a in view['items'] if a['kind']=='dice'))
            again=store.save_project(payload(view))
            self.assertEqual(next(a for a in again['items'] if a['kind']=='dice'),original)
            self.assertFalse(list((store.directory/'elements').glob('*.json')))

    def test_local_http_serves_existing_models_and_inert_flat_preview(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as folder:
            server=serve.make_server(0,Path(folder)/'library',Path(folder)/'buttons')
            thread=Thread(target=server.serve_forever,daemon=True);thread.start()
            opener=build_opener(ProxyHandler({}));base='http://127.0.0.1:'+str(server.server_port)
            try:
                for path in ('/api/dice/dice-physics-v1/preview?interactive=1','/dice-source/physics.js','/dice-source/flat.js','/dice-source/assets/d6.fbx','/dice-source/assets/theme.json'):
                    with opener.open(base+path) as response:
                        self.assertEqual(response.status,200)
                        if path.startswith('/api/'):
                            self.assertIn("connect-src 'self'",response.headers['Content-Security-Policy'])
                            self.assertNotIn('data-state-url',response.read().decode())
                for path in ('/api/dice/dice-result-6/preview','/dice-source/assets/../../../PROJEKTLOG.md'):
                    with self.assertRaises(HTTPError) as error:opener.open(base+path)
                    self.assertIn(error.exception.code,(400,404));error.exception.close()
            finally:server.shutdown();server.server_close();thread.join(3)


if __name__=='__main__':unittest.main()
