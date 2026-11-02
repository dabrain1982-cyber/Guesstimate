"""Whole room/source windows, neutral growing data and scoped final coverage."""
from copy import deepcopy
from pathlib import Path
import tempfile
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import build_opener, ProxyHandler
from tests.test_game_workshop import serve, TEST_ROOT
from tests.test_workshop_collections import empty_project
from workspace_store import ProjectLibrary
from room_library import RoomLibrary, CONQUEST
from completion_library import CompletionLibrary
from source_buttons import SourceButtons
from source_windows import SourceWindows
from dice_library import fragment
from library_store import InvalidDesign
from question_bindings import annotate_assets
from deploy.audit_workshop_completeness import collect, classify


class RoomCompletionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(dir=TEST_ROOT)
        cls.store=ProjectLibrary(Path(cls.temp.name)/'library',Path(cls.temp.name)/'buttons',serve.EXISTING_ASSETS)
        cls.rooms=cls.store.rooms;cls.completion=cls.store.completion

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def test_whole_rooms_cover_eight_games_in_exactly_two_models(self):
        assets=self.rooms.assets()
        self.assertEqual(len(assets),9)
        self.assertEqual({a['model_id'] for a in assets},{'room-2d-v1','room-3d-v1'})
        self.assertEqual(len({g for a in assets for g in a['games']}),8)
        room=self.rooms.records['rooms-conquest']
        self.assertEqual(room['snapshot']['settings']['layers'],['raum-wand-v2.png','moebel-v2.png','teppich.png'])
        factory=self.rooms.conquest_factory()
        original=(CONQUEST/'scene.js').read_text(encoding='utf-8')
        self.assertIn(fragment(original,'function buildRoom(wallTexture, furnitureTexture, rugTexture)','function frameView()'),factory)
        for forbidden in ('buildTable(', 'fetch(', 'setInterval(', 'createTerritoryLayer(', 'sqlite'):
            self.assertNotIn(forbidden,factory)
        for a in assets:
            self.assertFalse(a['editable']);self.assertFalse(a['snapshot']['game_integration'])
            self.assertEqual(a['snapshot']['editor_review'],'deferred')
            self.assertNotIn('<form',a['snapshot']['settings']['markup'])
        decor=self.rooms.records['rooms-perfect']['snapshot']['settings']['markup']
        for part in ('perfect-curtain-left','perfect-curtain-right','perfect-lights','perfect-window','perfect-fireplace'):
            self.assertIn(part,decor)

    def test_background_and_existing_window_references_stay_exact(self):
        assets=self.store.assets()
        before={a['id']:a['snapshot'] for a in serve.EXISTING_ASSETS if a['kind']=='background'}
        self.assertEqual(len(before),15)
        after={a['id']:a['snapshot'] for a in assets if a['id'] in before}
        self.assertEqual(before,after)
        old=SourceWindows(self.store.source_buttons).assets()
        old_catalog={a['id']:a for a in assets if a['id'] in {b['id'] for b in old}}
        self.assertEqual(len(old_catalog),84)
        for a in old:
            # Binding metadata exists only on catalog copies and never changes their stable IDs.
            copy=deepcopy(old_catalog[a['id']]['snapshot']);copy.pop('data_binding',None)
            self.assertEqual(a['snapshot'],copy)

    def test_only_five_extra_models_with_neutral_questions_and_whole_results(self):
        extras=annotate_assets(self.completion.assets())
        self.assertEqual(len(extras),30);self.assertEqual(len({a['model_id'] for a in extras}),5)
        questions=[a for a in extras if a['model_id']=='window-quiz-question-card']
        self.assertEqual(len(questions),16)
        for a in questions:
            self.assertIn('question-card',a['snapshot']['rendered_markup'])
            self.assertEqual(a['snapshot']['data_binding']['kind'],'question_bank_reference')
            self.assertNotIn('content',a['snapshot'])
        reviews=[a for a in extras if a['model_id']=='window-quiz-answer-review']
        self.assertEqual(len(reviews),3)
        for a in reviews:
            self.assertIn('Beispielantwort',a['snapshot']['rendered_markup'])
            self.assertEqual(a['snapshot']['data_binding']['loader'],'questions.py')
        rankings=[a for a in extras if a['model_id']=='window-quiz-ranking-window']
        self.assertEqual(len(rankings),7)
        for a in rankings:
            self.assertEqual(a['snapshot']['rendered_markup'].count('aria-selected="true"'),1)
        for a in extras:
            if a['model_id']=='window-quiz-result-window':
                score=a['context_state'].split()[0]
                self.assertIn('>'+score+'</span>',a['snapshot']['rendered_markup'])

    def test_sources_are_guarded_and_catalog_copies_are_independent(self):
        record=self.rooms.records['rooms-dice-table'];original=deepcopy(record['snapshot'])
        try:
            record['snapshot']['evidence'][0]['sha256']='0'*64
            with self.assertRaises(InvalidDesign):self.rooms.preview('rooms-dice-table')
        finally:record['snapshot']=original
        assets=self.rooms.assets();assets[0]['snapshot']['settings']['markup']='changed'
        self.assertNotEqual(assets[0]['snapshot'],self.rooms.assets()[0]['snapshot'])
        with self.assertRaises(InvalidDesign):self.rooms.preview('rooms-not-registered')

    def test_whole_room_and_question_window_roundtrip_without_game_or_question_data(self):
        question=next(a for a in self.store.assets() if a.get('model_id')=='window-quiz-question-card')
        p=empty_project('Raum und Fragenfenster');p['items']=[dict(kind='background',id='rooms-conquest'),dict(kind='windows',id=question['id'])]
        saved=self.store.save_project(p)
        again=ProjectLibrary(self.store.directory,self.store.buttons_directory,serve.EXISTING_ASSETS)
        handoff=again.handoff(saved['id'])['project']
        self.assertEqual(handoff['items'],saved['items']);self.assertEqual(len(handoff['items']),2)
        self.assertEqual(len(handoff['items'][0]['snapshot']['settings']['layers']),3)
        self.assertEqual(handoff['items'][1]['snapshot']['data_binding']['kind'],'question_bank_reference')

    def test_final_source_scan_has_no_unclassified_containers_and_detects_new_ones(self):
        report=collect(self.store)
        self.assertEqual(len(report['games']),8);self.assertEqual(report['remaining_unreviewed'],[])
        self.assertEqual(len(report['factories']),13)
        for row in report['factories']:self.assertEqual(row['status'],'reviewed')
        rows=classify('<section class="new-unregistered-window"><p>Neu</p></section>',{},self.store.assets())
        self.assertEqual(rows[0]['status'],'unreviewed')
        rows=classify('<aside class="prototype-note">Offline-Vorschau</aside>',{},self.store.assets())
        self.assertEqual(rows[0]['status'],'excluded')

    def test_local_routes_inert_windows_and_restricted_room_resources(self):
        server=serve.make_server(0,self.store.directory,self.store.buttons_directory)
        thread=Thread(target=server.serve_forever,daemon=True);thread.start()
        opener=build_opener(ProxyHandler({}));base='http://127.0.0.1:'+str(server.server_port)
        try:
            paths=['/api/rooms/'+a['id']+'/preview' for a in self.rooms.assets()]
            paths+=['/api/completion-windows/'+a['id']+'/preview' for a in self.completion.assets()]
            paths+=['/room-components/stage.js','/room-components/stage.css','/room-source/conquest.js','/room-source/territory-model.js','/room-source/moebel-v2.png']
            for path in paths:
                with opener.open(base+path) as response:
                    self.assertEqual(response.status,200)
                    raw=response.read()
                    if path.startswith('/api/'):
                        self.assertIn("form-action 'none'",response.headers['Content-Security-Policy'])
                        body=raw.decode('utf-8')
                        self.assertNotIn('csrf',body)
                        if path.startswith('/api/rooms/'):
                            self.assertNotIn('<form',body)
                        else:
                            self.assertIn('<body inert',body)
                            self.assertNotIn('action="',body);self.assertNotIn('method="post"',body)
                            self.assertNotIn('<script',body)
            for path in ('/api/rooms/unknown/preview','/api/completion-windows/unknown/preview','/room-source/../../PROJEKTLOG.md'):
                with self.assertRaises(HTTPError) as error:opener.open(base+path)
                self.assertIn(error.exception.code,(400,404));error.exception.close()
        finally:server.shutdown();server.server_close();thread.join(3)


if __name__=='__main__':unittest.main()
