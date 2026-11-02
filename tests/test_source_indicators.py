"""Frozen display states, canonical sources and exact project roundtrips."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
from threading import Thread
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, build_opener, ProxyHandler

from tests.test_game_workshop import serve, TEST_ROOT
from tests.test_workshop_collections import empty_project
from source_indicators import SourceIndicators
from source_windows import SourceWindows
from workspace_store import ProjectLibrary
from library_store import InvalidDesign


class SourceIndicatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SourceIndicators()

    def test_games_families_and_semantic_source_coverage(self):
        report = self.source.report()
        self.assertFalse(report['uncovered'])
        self.assertTrue({'Guesstimate', 'Guesstimate Party', 'Perfect', 'Playtable', 'Würfeltisch',
                         'Kniffel', 'Mäxchen', 'Conquest', 'Profil', 'Shop'} <= set(report['games']))
        self.assertEqual(set(report['families']), {'points', 'timer', 'progress', 'status', 'counter', 'results'})
        self.assertEqual(len(report['assets']), len({a['id'] for a in report['assets']}))
        for a in self.source.assets():
            if not a['snapshot']['source'].get('generated'):
                self.assertIn(a['snapshot']['markup'], self.source.read(a['snapshot']['source']['path']))

    def test_new_unassigned_output_is_reported(self):
        read = self.source.read
        def changed(path):
            text = read(path)
            return text + '<output id="new-unassigned-display">123</output>' if path == 'templates/question.html' else text
        with patch.object(self.source, 'read', changed):
            missing = self.source.report()['uncovered']
        self.assertTrue(any(v['id'] == 'new-unassigned-display' for v in missing))

    def test_perfect_timer_states_are_distinct_frozen_values(self):
        assets = [a for a in self.source.assets() if a['model_id'] == 'indicator-perfect-timer']
        self.assertEqual(len(assets), 4)
        normal = next(a for a in assets if a['context_state'] == 'Antwort verfassen · Normal')
        urgent = next(a for a in assets if a['context_state'] == 'Antwort verfassen · Dringend')
        self.assertIn('2:15', normal['snapshot']['rendered_markup'])
        self.assertIn('0:12', urgent['snapshot']['rendered_markup'])
        self.assertIn('is-urgent', urgent['snapshot']['rendered_markup'])
        self.assertNotIn('is-urgent', normal['snapshot']['rendered_markup'])
        self.assertNotEqual(normal['id'], urgent['id'])
        expired = next(a for a in self.source.assets() if a['model_id'] == 'indicator-perfect-game-timer' and a['context_state'] == 'Abgelaufen')
        self.assertIn('Zeit abgelaufen', expired['snapshot']['rendered_markup'])

    def test_quiz_timepoints_use_the_existing_calculation(self):
        rows = [a for a in self.source.assets() if a['model_id'] == 'indicator-quiz-time' and a['game'] == 'Guesstimate']
        full = next(a for a in rows if a['context_state'] == 'Volle Zeitpunkte')
        low = next(a for a in rows if a['context_state'] == 'Zeitpunkte am Minimum')
        self.assertIn('100 PKT', full['snapshot']['rendered_markup'])
        self.assertIn('50 PKT', low['snapshot']['rendered_markup'])
        self.assertIn('aria-valuenow="50"', low['snapshot']['rendered_markup'])
        self.assertTrue(any(p['path'] == 'static/timer.js' for p in low['snapshot']['evidence']))

    def test_lobby_states_and_game_uses_remain_individual_variants(self):
        rows = [a for a in self.source.assets() if a['model_id'] == 'indicator-overview-state']
        self.assertEqual(len({a['model_id'] for a in rows}), 1)
        self.assertEqual(len(rows), 42)
        for game in ('Guesstimate Party', 'Perfect', 'Playtable', 'Würfeltisch', 'Kniffel', 'Mäxchen', 'Conquest'):
            full = next(a for a in rows if a['game'] == game and a['context_state'] == 'Voll')
            self.assertIn('Lobby voll', full['snapshot']['rendered_markup'])
            self.assertIn('is-full', full['snapshot']['rendered_markup'])

    def test_dynamic_lives_rolls_and_battle_come_from_current_factories(self):
        assets = self.source.assets()
        swimming = next(a for a in assets if a['model_id'] == 'indicator-maexchen-lives' and a['context_state'] == 'Schwimmt')
        self.assertIn('♥ ♡ ♡ · schwimmt', swimming['snapshot']['rendered_markup'])
        two = next(a for a in assets if a['model_id'] == 'indicator-maexchen-lives' and a['context_state'] == 'Zwei Leben')
        self.assertIn('♥ ♥ ♡', two['snapshot']['rendered_markup'])
        rolls = next(a for a in assets if a['model_id'] == 'indicator-kniffel-rolls-left' and a['context_state'] == '2')
        self.assertEqual(rolls['snapshot']['rendered_markup'].count('class="is-lit"'), 2)
        result = next(a for a in assets if a['model_id'] == 'indicator-dice-roll-result' and a['game'] == 'Mäxchen')
        self.assertEqual(result['snapshot']['rendered_markup'].count('<span>'), 2)
        battle = next(a for a in assets if a['model_id'] == 'indicator-conquest-battle')
        self.assertEqual(battle['snapshot']['rendered_markup'].count('class="battle-die"'), 5)
        self.assertIn('Verluste: Angriff 1 · Verteidigung 1', battle['snapshot']['rendered_markup'])

    def test_player_components_keep_their_whole_canonical_composition(self):
        assets = self.source.assets()
        profile = next(a for a in assets if a['model_id'] == 'indicator-profile-values')
        self.assertEqual(profile['snapshot']['source']['path'], 'templates/_profile_window.html')
        self.assertIn('variant-a-profile-canonical', profile['snapshot']['rendered_markup'])
        self.assertIn('variant-a-avatar', profile['snapshot']['rendered_markup'])
        self.assertIn('variant-a-podium', profile['snapshot']['rendered_markup'])
        self.assertIn('.workshop-window-root{width:430px!important;', self.source.preview(profile['id']))
        army = next(a for a in assets if a['model_id'] == 'indicator-conquest-army-values' and a['context_state'] == 'Am Zug')
        self.assertEqual(army['snapshot']['source']['factory'], 'createPlayerPortrait')
        self.assertIn('data-current="true"', army['snapshot']['rendered_markup'])
        self.assertIn('>18</strong>', army['snapshot']['rendered_markup'])
        self.assertIn('>6</strong>', army['snapshot']['rendered_markup'])
        self.assertIn('max-height:304px!important;overflow:visible!important', self.source.preview(army['id']))

    def test_every_preview_uses_the_shared_inert_renderer(self):
        self.assertIs(SourceIndicators.preview, SourceWindows.preview)
        for a in self.source.assets():
            page = self.source.preview(a['id'])
            self.assertIn('<body inert', page)
            self.assertNotIn('<script', page)
            self.assertNotIn('csrf_token', page)
            self.assertNotIn(' action=', page)
            self.assertNotIn(' onchange=', page)
        with self.assertRaises(InvalidDesign):
            self.source.preview('../../app.py')

    def test_stale_sources_are_rejected(self):
        record = next(iter(self.source.records.values()))
        original = deepcopy(record['snapshot'])
        record['snapshot']['evidence'][0]['sha256'] = '0' * 64
        try:
            with self.assertRaises(InvalidDesign):
                self.source.preview(record['id'])
        finally:
            record['snapshot'] = original

    def test_exact_timer_variant_survives_reuse_reload_and_handoff(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as directory:
            store = ProjectLibrary(Path(directory) / 'library', Path(directory) / 'buttons')
            a = next(a for a in store.assets() if a.get('model_id') == 'indicator-perfect-timer' and a['context_state'] == 'Antwort verfassen · Dringend')
            p = empty_project('Anzeigenprüfung')
            p['items'] = [dict(kind='indicators', id=a['id'])]
            saved = store.save_project(p)
            q = empty_project('Wiederverwendung')
            q['items'] = p['items']
            second = store.save_project(q)
            self.assertEqual(second['items'][0]['snapshot'], a['snapshot'])
            reopened = ProjectLibrary(store.directory, store.buttons_directory)
            view = next(g['project'] for g in reopened.project_groups() if g['project']['project_key'] == saved['project_key'])
            self.assertEqual(view['items'], saved['items'])
            self.assertEqual(reopened.handoff(saved['id'])['project']['items'], saved['items'])
            self.assertEqual(list((store.directory / 'elements').glob('*.json')), [])

    def test_http_host_boundary_and_preview_policy(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as directory:
            server = serve.make_server(0, Path(directory) / 'library', Path(directory) / 'buttons')
            Thread(target=server.serve_forever, daemon=True).start()
            base = 'http://127.0.0.1:' + str(server.server_port)
            opener = build_opener(ProxyHandler({}))
            try:
                with opener.open(base + '/api/library', timeout=12) as response:
                    data = json.load(response)
                self.assertEqual(len(data['kinds']), 17)
                a = next(a for a in data['assets'] if a['kind'] == 'indicators')
                with opener.open(base + a['preview'], timeout=5) as response:
                    self.assertIn("script-src 'none'", response.headers['Content-Security-Policy'])
                    self.assertIn("form-action 'none'", response.headers['Content-Security-Policy'])
                for url, host in [(base + '/api/game-indicators/unknown/preview', None),
                                  (base + a['preview'], 'external.example')]:
                    with self.assertRaises(HTTPError) as caught:
                        opener.open(Request(url, headers={'Host': host} if host else {}), timeout=5)
                    self.assertIn(caught.exception.code, (400, 403))
                    caught.exception.close()
            finally:
                server.shutdown()
                server.server_close()


if __name__ == '__main__':
    unittest.main()
