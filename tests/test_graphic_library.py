"""Finite graphic families, original sources, whole sets and protected local storage."""
from copy import deepcopy
from pathlib import Path
import tempfile
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import build_opener, ProxyHandler
from tests.test_game_workshop import serve, TEST_ROOT
from tests.test_workshop_collections import empty_project
from graphic_library import GraphicLibrary, GAMES, CONQUEST
from source_buttons import SourceButtons
from dice_library import fragment
from library_store import InvalidDesign
from workspace_store import ProjectLibrary


class GraphicLibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.graphics=GraphicLibrary(SourceButtons())

    def test_finite_symbol_sets_and_shared_motifs_cover_games_without_personal_content(self):
        assets=self.graphics.assets();report=self.graphics.report()
        self.assertEqual(report['areas'],{'titles':dict(configurations=9,models=2),'flyers':dict(configurations=13,models=3),'icons':dict(configurations=6,models=6)})
        self.assertEqual({game for a in assets for game in a['games']},set(GAMES))
        sets=[a for a in assets if a['snapshot'].get('symbol_set')]
        self.assertEqual(sorted(a['snapshot']['symbol_set']['member_count'] for a in sets),[2,3,4,5,15])
        self.assertNotIn('birthday',str(assets).lower());self.assertNotIn('Jenny',str(assets));self.assertNotIn('schweinchen',str(assets).lower())
        for a in assets:
            self.assertFalse(a['editable']);self.assertEqual(a['snapshot']['editor_review'],'deferred')
            self.assertFalse(a['snapshot']['game_integration'])
        shared=next(a for a in assets if a['id']=='graphics-artwork-dice')
        self.assertEqual(shared['games'],['Würfeltisch','Mäxchen'])
        assets[0]['snapshot']['settings']['asset']='changed'
        self.assertNotEqual(self.graphics.assets()[0]['snapshot']['settings']['asset'],'changed')

    def test_original_compositions_and_symbol_factory_are_bound_to_sources(self):
        asset=self.graphics.records['graphics-tile-perfect']
        original=self.graphics.buttons.env.get_template('_game_flyers.html').module.perfect_flyer()
        self.assertIn('carousel-stormseeds-perfect-v1.png',asset['snapshot']['settings']['markup'])
        self.assertIn('Oder weißt du etwa, was eine Mansube ist?',asset['snapshot']['settings']['markup'])
        self.assertIn('tabletop-perfect-flyer',original)
        factory=self.graphics.equipment_factory();source=(CONQUEST/'cards.js').read_text(encoding='utf-8')
        self.assertIn(fragment(source,'const ICONS = {','export function createCountryCard'),factory)
        self.assertNotIn('createCountryCard(',factory);self.assertNotIn('fetch(',factory)
        old=deepcopy(asset['snapshot'])
        try:
            asset['snapshot']['evidence'][0]['sha256']='0'*64
            with self.assertRaises(InvalidDesign):self.graphics.preview(asset['id'])
        finally:asset['snapshot']=old
        with self.assertRaises(InvalidDesign):self.graphics.preview('graphics-icons-quiz','infantry')

    def test_whole_symbol_set_survives_collection_reuse_and_handoff(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as folder:
            store=ProjectLibrary(Path(folder)/'library',Path(folder)/'buttons')
            p=empty_project('Bildbausteine');p['items']=[dict(kind=kind,id=key) for kind,key in [('titles','graphics-artwork-conquest'),('flyers','graphics-tile-perfect'),('icons','graphics-icons-quiz')]]
            saved=store.save_project(p);other=empty_project('Wiederverwenden');other['items']=p['items']
            self.assertEqual(store.save_project(other)['items'],saved['items'])
            again=ProjectLibrary(store.directory,store.buttons_directory)
            handoff=again.handoff(saved['id'])['project'];self.assertEqual(handoff['items'],saved['items'])
            symbols=next(a for a in handoff['items'] if a['kind']=='icons')['snapshot']['symbol_set']
            self.assertEqual(symbols['member_count'],5);self.assertEqual(len(symbols['members']),5)
            self.assertEqual(len(handoff['items']),3)
            self.assertFalse(list((store.directory/'images').rglob('*')))

    def test_local_routes_and_preview_only_member_selection(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as folder:
            server=serve.make_server(0,Path(folder)/'library',Path(folder)/'buttons');thread=Thread(target=server.serve_forever,daemon=True);thread.start()
            opener=build_opener(ProxyHandler({}));base='http://127.0.0.1:'+str(server.server_port)
            try:
                for path in ('/api/graphics/graphics-icons-quiz/preview?member=match','/api/graphics/graphics-tile-perfect/preview','/graphic-components/stage.js','/graphic-source/equipment.js','/graphic-source/comic.js','/graphic-source/player-portrait.js','/shared/maexchen-logo-v1.svg'):
                    with opener.open(base+path) as response:
                        self.assertEqual(response.status,200)
                        if path.startswith('/api/'):
                            self.assertIn("form-action 'none'",response.headers['Content-Security-Policy'])
                            body=response.read().decode('utf-8');self.assertNotIn('<form',body);self.assertNotIn('csrf',body)
                for path in ('/api/graphics/graphics-icons-quiz/preview?member=infantry','/api/graphics/personal-greeting/preview','/graphic-source/../../PROJEKTLOG.md'):
                    with self.assertRaises(HTTPError) as error:opener.open(base+path)
                    self.assertIn(error.exception.code,(400,404));error.exception.close()
            finally:server.shutdown();server.server_close();thread.join(3)


if __name__=='__main__':unittest.main()
