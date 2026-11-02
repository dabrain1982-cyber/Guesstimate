"""Finite Conquest content versus growing question data and immutable source IDs."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tests.test_game_workshop import TEST_ROOT
from tests.test_workshop_collections import empty_project
from card_library import CardLibrary
from card_contents import WORLD
from library_store import ROOT
from workspace_store import ProjectLibrary
from question_bindings import annotate_assets

class CardContentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(dir=TEST_ROOT)
        cls.store=ProjectLibrary(Path(cls.temp.name)/'library',Path(cls.temp.name)/'buttons')
        cls.cards=cls.store.cards
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def test_conquest_two_sets_with_exact_original_members(self):
        world=json.loads((ROOT/WORLD).read_text(encoding='utf-8'))
        countries=self.cards.records['cards-set-display-conquest-countries']['snapshot']['set']
        self.assertEqual(len(countries['members']),42)
        self.assertEqual(len(countries['supplements']),2)
        self.assertEqual({m['id'] for m in countries['members']},{r['id'] for r in world['territories']})
        self.assertEqual({m['id']:m['original']['symbol'] for m in countries['members']+countries['supplements']},world['cardSymbols'])
        missions=self.cards.records['cards-set-display-conquest-missions']['snapshot']['set']
        self.assertEqual([m['original'] for m in missions['members']],world['missions'])

    def test_question_growth_does_not_create_assets_or_change_window_ids(self):
        before=self.store.assets();original=Path.read_text;read_banks=[]
        def enlarged(path,*args,**kwargs):
            text=original(path,*args,**kwargs)
            if path.name=='fragen.json':
                read_banks.append(path)
                return json.dumps(json.loads(text)+[dict(id='simulated-question-'+str(n),prompt='Beispiel') for n in range(2000)])
            return text
        with patch.object(Path,'read_text',enlarged):
            after=ProjectLibrary(self.store.directory,self.store.buttons_directory).assets()
            self.assertEqual([a['id'] for a in CardLibrary().assets()],[a['id'] for a in self.cards.assets()])
        self.assertEqual(before,after)
        self.assertEqual(read_banks,[],'Der Katalog darf wachsende Fragenbanken gar nicht einlesen.')
        for source in (self.store.source_buttons,self.store.source_windows,self.store.source_inputs,self.store.source_indicators,self.store.source_players,self.store.source_lobbies):
            raw=source.assets();annotated=annotate_assets(deepcopy(raw))
            self.assertEqual([a['id'] for a in raw],[a['id'] for a in annotated])
            self.assertEqual([a['model_id'] for a in raw],[a['model_id'] for a in annotated])

    def test_question_windows_keep_reference_contract_through_handoff(self):
        asset=next(a for a in self.store.assets() if a['kind']=='windows' and a['game']=='Perfect' and a['snapshot'].get('data_binding'))
        binding=asset['snapshot']['data_binding']
        self.assertEqual({s['type'] for s in binding['sources']},{'term','curiosity'})
        self.assertNotIn('questions',binding)
        project=empty_project('Fragenfenster');project['items']=[dict(kind='windows',id=asset['id'])]
        saved=self.store.save_project(project)
        self.assertEqual(self.store.handoff(saved['id'])['project']['items'][0]['snapshot']['data_binding'],binding)
        self.assertNotIn('ssp-begriff-',json.dumps(saved))
        private=dict(kind='cards',source='saved',snapshot={'content':{'kind':'question','prompt':'Eigener Entwurf'}})
        self.assertEqual(annotate_assets([deepcopy(private)]),[private])
        with self.assertRaises(ValueError):annotate_assets([dict(private,source='preset')])

    def test_mission_text_is_inert_and_question_renderer_removed(self):
        asset=self.cards.records['cards-set-display-conquest-missions'];pack=asset['snapshot']['set'];original=deepcopy(pack)
        try:
            pack['members'][0]['content']['prompt']='</script><img src=x onerror=alert(1)>'
            page=self.cards.preview(asset['id'],True)
            self.assertNotIn('</script><img',page);self.assertIn('\\u003c/script\\u003e',page)
        finally:asset['snapshot']['set']=original
        renderer=(ROOT/'offline-preview/game-workshop-v1/content-card.js').read_text(encoding='utf-8')
        self.assertNotIn("content.kind==='question'",renderer)

if __name__=='__main__':unittest.main()
