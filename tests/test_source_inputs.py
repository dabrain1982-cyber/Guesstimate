"""Input-source coverage, neutral states and exact collection roundtrips."""
from copy import deepcopy
import json
from pathlib import Path
import re
import tempfile
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import Request, build_opener, ProxyHandler

from tests.test_game_workshop import serve, TEST_ROOT
from tests.test_workshop_collections import empty_project
from source_inputs import SourceInputs
from source_windows import SourceWindows
from workspace_store import ProjectLibrary
from library_store import InvalidDesign


class SourceInputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SourceInputs()

    def test_every_connected_source_control_is_covered(self):
        report = self.source.report()
        self.assertFalse(report['uncovered'])
        self.assertGreater(len(report['source_controls']), 40)
        self.assertTrue({'Guesstimate', 'Guesstimate Party', 'Perfect', 'Playtable', 'Würfeltisch',
                         'Kniffel', 'Mäxchen', 'Conquest', 'Profil', 'Zugang'} <= set(report['games']))
        self.assertEqual(set(report['families']), {'text', 'selection', 'toggle', 'range', 'compound'})
        for asset in self.source.assets():
            self.assertIn(asset['snapshot']['markup'], self.source.read(asset['snapshot']['source']['path']))
            self.assertFalse(asset['editable'])
            self.assertEqual(asset['snapshot']['type'], 'game-input')

    def test_shared_toggle_preserves_checked_and_unchecked_variants_per_game(self):
        rows = [a for a in self.source.assets() if a['model_id'] == 'input-dice-camera-lock']
        self.assertEqual(len(rows), 6)
        self.assertEqual(len({a['id'] for a in rows}), 6)
        for game in ('Würfeltisch', 'Kniffel', 'Mäxchen'):
            selected = next(a for a in rows if a['game'] == game and a['context_state'] == 'Ein')
            blank = next(a for a in rows if a['game'] == game and a['context_state'] == 'Aus')
            self.assertRegex(selected['snapshot']['rendered_markup'], r'<input[^>]* checked')
            self.assertNotRegex(blank['snapshot']['rendered_markup'], r'<input[^>]* checked')

    def test_source_constraints_and_labels_survive_without_credentials(self):
        pin = next(a for a in self.source.assets() if a['usage'] == 'PIN' and a['context_state'] == 'Anmeldung')
        html = pin['snapshot']['rendered_markup']
        self.assertIn('type="password"', html)
        self.assertIn('maxlength="12"', html)
        self.assertIn('PIN', html)
        self.assertNotRegex(html, r'<input[^>]*\bvalue=')
        estimate = next(a for a in self.source.assets() if a['model_id'] == 'input-quiz-estimate')
        self.assertIn('Einheiten', estimate['snapshot']['rendered_markup'])
        amount = next(a for a in self.source.assets() if a['model_id'] == 'input-conquest-troop-amount')
        self.assertIn('min="1"', amount['snapshot']['rendered_markup'])
        self.assertIn('max="6"', amount['snapshot']['rendered_markup'])

    def test_selected_and_unselected_quiz_choices_are_distinct_samples(self):
        rows = [a for a in self.source.assets() if a['game'] == 'Guesstimate' and a['usage'] == 'Antwortauswahl']
        self.assertEqual(len(rows), 2)
        sample = next(a for a in rows if a['context_state'] == 'Beispielauswahl')
        blank = next(a for a in rows if a['context_state'] == 'Ausgangszustand')
        self.assertEqual(sample['model_id'], blank['model_id'])
        self.assertIn(' checked', sample['snapshot']['rendered_markup'])
        self.assertNotIn(' checked', blank['snapshot']['rendered_markup'])
        self.assertEqual(sample['snapshot']['markup'], blank['snapshot']['markup'])

    def test_sort_match_review_and_dynamic_icons_keep_original_compositions(self):
        assets = self.source.assets()
        for model, marker in [('quiz-order', 'order-position'), ('quiz-match', 'match-options'),
                              ('conquest-dice-choice', '<svg')]:
            a = next(a for a in assets if a['model_id'] == 'input-' + model)
            self.assertIn(marker, a['snapshot']['rendered_markup'])
        readonly = next(a for a in assets if a['model_id'] == 'input-perfect-review' and 'Mitspieler' in a['context_state'])
        self.assertIn('is-readonly', readonly['snapshot']['markup'])
        self.assertIn(' disabled', readonly['snapshot']['rendered_markup'])
        colors = next(a for a in assets if a['model_id'] == 'input-conquest-color')
        self.assertIn('Musterarmee 2', colors['snapshot']['rendered_markup'])

    def test_previews_share_the_window_engine_and_cannot_run_actions(self):
        self.assertIs(SourceInputs.preview, SourceWindows.preview)
        self.assertIs(SourceInputs.http_get, SourceWindows.http_get)
        for a in self.source.assets():
            html = self.source.preview(a['id'])
            self.assertIn('width=640', html)
            self.assertIn('<body inert', html)
            self.assertNotIn('<script', html)
            self.assertNotIn('csrf_token', html)
            self.assertNotIn(' onchange=', html)
            self.assertNotIn(' action=', html)
        with self.assertRaises(InvalidDesign):
            self.source.preview('../../app.py')

    def test_specific_state_can_be_collected_twice_and_survives_reopen_and_handoff(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as directory:
            store = ProjectLibrary(Path(directory) / 'library', Path(directory) / 'buttons')
            rows = [a for a in store.assets() if a.get('model_id') == 'input-dice-camera-lock' and a['game'] == 'Kniffel']
            p = empty_project('Eingabeprüfung')
            p['items'] = [dict(kind='inputs', id=a['id']) for a in rows]
            saved = store.save_project(p)
            q = empty_project('Wiederverwendung')
            q['items'] = p['items'][:1]
            second = store.save_project(q)
            self.assertEqual(second['items'][0]['snapshot'], saved['items'][0]['snapshot'])
            reopened = ProjectLibrary(store.directory, store.buttons_directory)
            project = next(g['project'] for g in reopened.project_groups() if g['project']['project_key'] == saved['project_key'])
            self.assertEqual(project['items'], saved['items'])
            self.assertEqual(reopened.handoff(saved['id'])['project']['items'], saved['items'])
            self.assertEqual(list((store.directory / 'elements').glob('*.json')), [])

    def test_stale_evidence_is_rejected(self):
        record = next(iter(self.source.records.values()))
        original = deepcopy(record['snapshot'])
        record['snapshot']['evidence'][0]['sha256'] = '0' * 64
        try:
            with self.assertRaises(InvalidDesign):
                self.source.preview(record['id'])
        finally:
            record['snapshot'] = original

    def test_http_security_and_host_boundary(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as directory:
            server = serve.make_server(0, Path(directory) / 'library', Path(directory) / 'buttons')
            Thread(target=server.serve_forever, daemon=True).start()
            base = 'http://127.0.0.1:' + str(server.server_port)
            opener = build_opener(ProxyHandler({}))
            try:
                with opener.open(base + '/api/library', timeout=8) as response:
                    data = json.load(response)
                self.assertEqual(len(data['kinds']), 15)
                a = next(a for a in data['assets'] if a['kind'] == 'inputs')
                with opener.open(base + a['preview'], timeout=5) as response:
                    self.assertIn("script-src 'none'", response.headers['Content-Security-Policy'])
                    self.assertIn("form-action 'none'", response.headers['Content-Security-Policy'])
                for url, host in [(base + '/api/game-inputs/unknown/preview', None),
                                  (base + a['preview'], 'external.example')]:
                    request = Request(url, headers={'Host': host} if host else {})
                    with self.assertRaises(HTTPError) as caught:
                        opener.open(request, timeout=5)
                    self.assertIn(caught.exception.code, (400, 403))
                    caught.exception.close()
            finally:
                server.shutdown()
                server.server_close()


if __name__ == '__main__':
    unittest.main()
