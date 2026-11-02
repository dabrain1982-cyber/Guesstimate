"""Source coverage, inert previews and durable window variants in isolated maps."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import build_opener, ProxyHandler

from tests.test_game_workshop import serve, TEST_ROOT
from tests.test_workshop_collections import empty_project, payload
from library_store import InvalidDesign
from source_windows import SourceWindows, Fragments, InertMarkup
from workspace_store import ProjectLibrary


class SourceWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SourceWindows()

    def test_each_game_and_all_four_families_have_collectable_uses(self):
        assets = self.source.assets()
        self.assertTrue({'Guesstimate', 'Guesstimate Party', 'Perfect', 'Playtable', 'Würfeltisch',
                         'Kniffel', 'Mäxchen', 'Conquest', 'Profil', 'Shop'} <= {a['game'] for a in assets})
        self.assertEqual({a['family'] for a in assets}, {'rules', 'decisions', 'inventory', 'actions'})
        self.assertEqual(len(assets), len({a['id'] for a in assets}))
        self.assertTrue(all(not a['editable'] and a['snapshot']['example_values'] for a in assets))

    def test_shared_windows_keep_individual_contents_and_source_markup(self):
        assets = self.source.assets()
        rules = [a for a in assets if a['model_id'] == 'window-rules-dialog']
        self.assertEqual(len({a['model_id'] for a in rules}), 1)
        self.assertEqual(len(rules), 8)
        maexchen = next(a for a in rules if a['game'] == 'Mäxchen')
        self.assertIn('Zwei Würfel bilden einen Wert', maexchen['snapshot']['rendered_markup'])
        perfect = next(a for a in rules if a['game'] == 'Perfect')
        self.assertIn('seltenen Begriff', perfect['snapshot']['rendered_markup'])
        self.assertNotEqual(maexchen['id'], perfect['id'])
        for asset in assets:
            raw = (serve.ROOT / asset['snapshot']['source']['path']).read_text(encoding='utf-8-sig')
            self.assertIn(asset['snapshot']['markup'], raw)
            self.assertNotIn('static/conquest-table.js', [p['path'] for p in asset['snapshot']['evidence']])

    def test_all_actual_html_dialogs_are_accounted_for(self):
        found = set()
        for name in self.source.buttons.active_templates:
            path = 'templates/' + name
            for element in Fragments(self.source.read(path)).elements:
                if element['tag'] == 'dialog':
                    found.add((path, element['attrs'].get('id') or element['attrs'].get('class')))
        for element in Fragments(self.source.read('offline-preview/conquest-2-5d-v1/table-surface.js')).elements:
            if element['tag'] == 'dialog':
                found.add(('offline-preview/conquest-2-5d-v1/table-surface.js', element['attrs']['id']))
        recorded = {(a['snapshot']['source']['path'],
                     a['snapshot']['source']['target'].get('id') or a['snapshot']['source']['target'].get('class'))
                    for a in self.source.assets()}
        self.assertFalse(found - recorded, found - recorded)

    def test_perfect_roles_and_phases_are_real_template_branches(self):
        assets = self.source.assets()
        settings = [a for a in assets if a['model_id'] == 'window-perfect-settings']
        self.assertEqual(len(settings), 3)
        readonly = next(a for a in settings if a['context_state'] == 'Mitspieler')
        self.assertIn('is-readonly', readonly['snapshot']['rendered_markup'])
        self.assertNotIn('<fieldset', readonly['snapshot']['rendered_markup'])
        vote = next(a for a in assets if a['game'] == 'Perfect' and a['usage'] == 'Antwort wählen')
        self.assertIn('Beispielantwort A', vote['snapshot']['rendered_markup'])
        self.assertIn('perfect-vote-card', vote['snapshot']['markup'])

    def test_dynamic_contents_use_current_factory_captures(self):
        assets = self.source.assets()
        hand = next(a for a in assets if a['model_id'] == 'window-card-hand' and a['context_state'].startswith('Vergrößert'))
        self.assertIn('country-card', hand['snapshot']['rendered_markup'])
        self.assertIn('is-selected', hand['snapshot']['rendered_markup'])
        self.assertIn('data-expanded="true"', hand['snapshot']['rendered_markup'])
        block = next(a for a in assets if a['model_id'] == 'window-kniffel-sheet')
        self.assertIn('Endsumme', block['snapshot']['rendered_markup'])
        self.assertIn('Musterplatz 2', block['snapshot']['rendered_markup'])
        self.assertIn('kniffel', block['snapshot']['captures'])
        self.assertTrue(any(p['path'] == 'static/dice-table.js' for p in block['snapshot']['evidence']))

    def test_previews_cannot_execute_handlers_or_submit_game_actions(self):
        for asset in self.source.assets():
            page = self.source.preview(asset['id'])
            self.assertIn('<!doctype html>', page)
            self.assertIn('<body inert', page)
            self.assertNotIn('<script', page)
            self.assertNotIn('csrf_token', page)
            self.assertNotIn(' action=', page)
            self.assertNotIn(' onchange=', page)
        clean = ''.join(InertMarkup('<form action="/danger"><input type="hidden" value="private"><button onclick="danger()">OK</button><script>danger()</script></form>').parts)
        self.assertNotIn('private', clean)
        self.assertNotIn('danger', clean)
        with self.assertRaises(InvalidDesign):
            self.source.preview('../../app.py')

    def test_stale_sources_are_rejected_without_mutating_saved_snapshots(self):
        first = next(iter(self.source.records.values()))
        before = deepcopy(first['snapshot'])
        first['snapshot']['evidence'][0]['sha256'] = '0' * 64
        try:
            with self.assertRaisesRegex(InvalidDesign, 'geändert'):
                self.source.preview(first['id'])
        finally:
            first['snapshot'] = before

    def test_exact_variant_survives_reload_reuse_and_handoff(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as directory:
            store = ProjectLibrary(Path(directory) / 'library', Path(directory) / 'buttons')
            variants = [a for a in store.assets() if a.get('model_id') == 'window-card-hand']
            original = next(a for a in variants if a['context_state'].startswith('Vergrößert'))
            p = empty_project('Fensterprüfung')
            p['items'] = [dict(kind='windows', id=a['id']) for a in variants]
            first = store.save_project(p)
            q = empty_project('Wiederverwendung')
            q['items'] = [dict(kind='windows', id=original['id'])]
            second = store.save_project(q)
            self.assertEqual(second['items'][0]['snapshot'], original['snapshot'])
            reopened = ProjectLibrary(store.directory, store.buttons_directory)
            project = next(g['project'] for g in reopened.project_groups() if g['project']['project_key'] == first['project_key'])
            self.assertEqual(project['items'], first['items'])
            self.assertEqual(reopened.handoff(first['id'])['project']['items'], first['items'])
            self.assertEqual(list((Path(directory) / 'library/elements').glob('*.json')), [])
            update = payload(first)
            update['items'] = []
            newer = store.save_project(update)
            self.assertNotEqual(newer['id'], first['id'])
            self.assertEqual(json.loads((store.directory / 'projects' / (first['id'] + '.json')).read_text(encoding='utf-8'))['items'], first['items'])

    def test_http_host_boundary_and_preview_security(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as directory:
            server = serve.make_server(0, Path(directory) / 'library', Path(directory) / 'buttons')
            Thread(target=server.serve_forever, daemon=True).start()
            base = 'http://127.0.0.1:' + str(server.server_port)
            opener = build_opener(ProxyHandler({}))
            try:
                with opener.open(base + '/api/library', timeout=8) as response:
                    data = json.load(response)
                window = next(a for a in data['assets'] if a['kind'] == 'windows')
                with opener.open(base + window['preview'], timeout=5) as response:
                    self.assertIn("script-src 'none'", response.headers['Content-Security-Policy'])
                    self.assertIn("form-action 'none'", response.headers['Content-Security-Policy'])
                    self.assertIn('<body inert', response.read().decode())
                with self.assertRaises(HTTPError):
                    opener.open(base + '/api/game-windows/unknown/preview', timeout=5)
            finally:
                server.shutdown()
                server.server_close()


if __name__ == '__main__':
    unittest.main()
