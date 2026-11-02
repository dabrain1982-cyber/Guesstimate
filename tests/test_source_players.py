"""Player composition, role variants, source evidence and exact collection reuse."""
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
from source_players import SourcePlayers
from source_windows import SourceWindows
from workspace_store import ProjectLibrary
from library_store import InvalidDesign


class SourcePlayerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SourcePlayers()

    def rows(self, model):
        return [a for a in self.source.assets() if a['model_id'] == 'player-' + model]

    def test_connected_games_components_and_source_hooks_are_covered(self):
        report = self.source.report()
        self.assertFalse(report['uncovered'])
        self.assertTrue({'Guesstimate', 'Guesstimate Party', 'Perfect', 'Playtable', 'Würfeltisch',
                         'Kniffel', 'Mäxchen', 'Conquest', 'Profil', 'Shop'} <= set(report['games']))
        self.assertEqual(len(report['component_uses']), 16)
        self.assertEqual(len(report['source_hooks']), 7)
        for a in self.source.assets():
            if not a['snapshot']['source'].get('generated'):
                self.assertIn(a['snapshot']['markup'], self.source.read(a['snapshot']['source']['path']))

    def test_new_unassigned_player_call_is_detected(self):
        read = self.source.read
        with patch.object(self.source, 'read', lambda p: read(p) + ('{{ player_identity("new") }}' if p == 'templates/register.html' else '')):
            self.assertTrue(any(u['path'] == 'templates/register.html' for u in self.source.report()['uncovered']))

    def test_all_pult_families_keep_their_canonical_scene_and_old_selection(self):
        ids = self.source.report()['plaque_ids']
        self.assertEqual(len(ids), 14)
        for plaque_id in ids:
            high = [a for a in self.rows('profile-window') if 'plaque-' + plaque_id in a['snapshot']['rendered_markup']]
            old = [a for a in self.rows('equipment-preview') if 'plaque-' + plaque_id in a['snapshot']['rendered_markup']]
            self.assertTrue(high, plaque_id)
            self.assertEqual({a['game'] for a in old}, {'Profil'} if plaque_id == 'p00' else {'Profil', 'Shop'})
            self.assertIn('variant-a-avatar', high[0]['snapshot']['rendered_markup'])
            self.assertIn('variant-a-podium', high[0]['snapshot']['rendered_markup'])
            self.assertEqual(high[0]['snapshot']['source']['path'], 'templates/_profile_window.html')

    def test_lobby_roles_and_perfect_ready_states_remain_distinct(self):
        rows = self.rows('lobby-player')
        self.assertEqual(len(rows), 19)
        reserved = next(a for a in rows if a['game'] == 'Conquest' and a['context_state'] == 'Reservierter Platz')
        self.assertIn('Platz reserviert · kommt zurück', reserved['snapshot']['rendered_markup'])
        virtual = next(a for a in rows if a['context_state'] == 'Testarmee')
        self.assertIn('Virtuelle Armee im lokalen Entwicklertest', virtual['snapshot']['rendered_markup'])
        ready = next(a for a in self.rows('perfect-player') if a['context_state'] == 'Mitspieler · Antwort steht')
        waiting = next(a for a in self.rows('perfect-player') if a['context_state'] == 'Antworten · Mitspieler')
        self.assertIn('is-ready', ready['snapshot']['rendered_markup'])
        self.assertIn('Antwort steht', ready['snapshot']['rendered_markup'])
        self.assertIn('Denkt nach', waiting['snapshot']['rendered_markup'])
        for a in self.rows('perfect-player'):
            markup = a['snapshot']['rendered_markup']
            self.assertTrue(markup.startswith('<article class="perfect-player-window'))
            self.assertEqual(markup.count('data-profile-window'), 1)
            self.assertNotIn('perfect-settings', markup)

    def test_real_other_desk_and_result_branch_are_captured(self):
        rows = self.rows('playtable-desk')
        self.assertEqual(len(rows), 6)
        for a in rows:
            self.assertNotIn('variant-a-avatar', a['snapshot']['rendered_markup'])
            if 'Fremdes' in a['context_state']:
                self.assertIn('{{ player.display_name }}', a['snapshot']['markup'])
                self.assertNotIn('card-bet-control', a['snapshot']['rendered_markup'])
        result = next(a for a in self.rows('ranking-player') if a['context_state'] == 'Ergebnisseite · daily · Eigener Eintrag')
        self.assertGreater(result['snapshot']['source']['line'], 50)
        life = next(a for a in self.rows('dice-player') if a['context_state'] == 'Schwimmt · am Zug')
        self.assertIn('♥ ♡ ♡ · schwimmt', life['snapshot']['rendered_markup'])
        self.assertIn('is-current-turn', life['snapshot']['rendered_markup'])

    def test_public_portraits_retain_crop_privacy_badges_and_winner_layout(self):
        source = self.source
        own = source.player_captures['self-active']['markup']
        other = source.player_captures['other-waiting']['markup']
        self.assertNotEqual(own.split('src="')[1].split('"')[0], other.split('src="')[1].split('"')[0])
        self.assertNotIn('disabled=', own)
        self.assertIn('disabled=', other)
        self.assertIn('--portrait-scale: 1.7;', source.player_captures['avatar-a01']['markup'])
        self.assertIn('--portrait-top: -48%;', source.player_captures['avatar-a01']['markup'])
        self.assertIn('data-layout="default"', source.player_captures['winner-player']['markup'])
        neutral = source.player_captures['neutral']['markup']
        self.assertNotIn('src=', neutral)
        self.assertIn('data-kind="neutral"', neutral)

    def test_shared_previews_are_inert_and_reject_stale_factory_sources(self):
        self.assertIs(SourcePlayers.preview, SourceWindows.preview)
        for a in self.source.assets():
            page = self.source.preview(a['id'])
            self.assertIn('<body inert', page)
            for forbidden in ('<script', ' action=', ' onclick=', 'csrf_token'):
                self.assertNotIn(forbidden, page)
        with patch('source_players.digest', return_value='0' * 64):
            with self.assertRaises(InvalidDesign):
                SourcePlayers()

    def test_exact_role_variants_survive_multiple_projects_reload_and_handoff(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as directory:
            store = ProjectLibrary(Path(directory) / 'library', Path(directory) / 'buttons')
            rows = [a for a in store.assets() if a.get('model_id') == 'player-conquest-portrait']
            a = next(a for a in rows if a['context_state'] == 'Eigener Platz · am Zug')
            b = next(a for a in rows if a['context_state'] == 'Testarmee')
            p = empty_project('Spielerprüfung');p['items'] = [dict(kind='players', id=v['id']) for v in (a, b)]
            saved = store.save_project(p)
            q = empty_project('Wiederverwendung');q['items'] = p['items']
            self.assertEqual(store.save_project(q)['items'][0]['snapshot'], a['snapshot'])
            reopened = ProjectLibrary(store.directory, store.buttons_directory)
            self.assertEqual(reopened.handoff(saved['id'])['project']['items'], saved['items'])
            self.assertEqual(list((store.directory / 'elements').glob('*.json')), [])

    def test_http_host_boundary_and_preview_policy(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as directory:
            server = serve.make_server(0, Path(directory) / 'library', Path(directory) / 'buttons')
            thread = Thread(target=server.serve_forever, daemon=True);thread.start()
            opener = build_opener(ProxyHandler({}));base = 'http://127.0.0.1:' + str(server.server_port)
            try:
                with opener.open(base + '/api/library', timeout=15) as response:data = json.load(response)
                self.assertEqual(len(data['kinds']), 17)
                a = next(a for a in data['assets'] if a['kind'] == 'players')
                with opener.open(base + a['preview'], timeout=5) as response:
                    self.assertIn("script-src 'none'", response.headers['Content-Security-Policy'])
                    self.assertIn("form-action 'none'", response.headers['Content-Security-Policy'])
                for address, headers in [('/api/game-players/unknown/preview', {}), (a['preview'], {'Host': 'external.example'})]:
                    with self.assertRaises(HTTPError) as error:opener.open(Request(base + address, headers=headers), timeout=5)
                    self.assertIn(error.exception.code, (400, 403));error.exception.close()
            finally:
                server.shutdown();server.server_close();thread.join(3)


if __name__ == '__main__':
    unittest.main()
