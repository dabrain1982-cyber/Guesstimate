"""Canonical room/list coverage, role boundaries, inert previews and collections."""
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
from source_lobbies import SourceLobbies, GAMES
from source_windows import SourceWindows
from workspace_store import ProjectLibrary
from library_store import InvalidDesign


class SourceLobbyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.source = SourceLobbies()

    def rows(self, model):return [a for a in self.source.assets() if a['model_id'] == 'lobby-' + model]

    def test_all_connected_rooms_and_overviews_are_covered(self):
        report = self.source.report()
        self.assertFalse(report['uncovered'])
        self.assertEqual(set(report['games']), {g[0] for g in GAMES})
        self.assertEqual(len(report['component_calls']), 10)
        self.assertTrue(any(e['game'] == 'Guesstimate' for e in report['exclusions']))
        for a in self.source.assets():
            self.assertIn(a['snapshot']['markup'], self.source.read(a['snapshot']['source']['path']))
            self.assertFalse(a['editable'])

    def test_new_unassigned_lobby_call_is_detected(self):
        read = self.source.read
        with patch.object(self.source, 'read', lambda p: read(p) + ('{% call(lobby) lobby_overview(lobbies) %}{% endcall %}' if p == 'templates/home.html' else '')):
            self.assertTrue(any(c['path'] == 'templates/home.html' for c in self.source.report()['uncovered']))

    def test_join_return_and_result_actions_remain_specific_variants(self):
        rows = self.rows('overview-row')
        for game, *_ in GAMES:
            def markup(state):return next(a['snapshot']['rendered_markup'] for a in rows if a['game'] == game and a['context_state'] == state)
            self.assertIn('>beitreten</button>', markup('Offen · beitreten'))
            self.assertNotIn('>beitreten</button>', markup('Voll · kein Beitritt'))
            self.assertIn('Lobby voll', markup('Voll · kein Beitritt'))
            self.assertIn('>zur lobby</a>', markup('Eigene wartende Lobby'))
            self.assertIn('>zurück ins spiel</a>', markup('Eigene laufende Partie'))
            self.assertIn('>ergebnis ansehen</a>', markup('Eigenes Ergebnis'))
            self.assertIn('Bereits gestartet', markup('Fremde laufende Partie'))
        reserved = next(a for a in rows if a['context_state'] == 'Reservierter Platz · zurückkehren')
        self.assertIn('Dein Platz ist reserviert.', reserved['snapshot']['rendered_markup'])
        self.assertIn('>zurückkehren</button>', reserved['snapshot']['rendered_markup'])

    def test_empty_and_failed_updates_keep_the_original_list_composition(self):
        for game, *_ in GAMES:
            rows = [a for a in self.rows('overview') if a['game'] == game]
            empty = next(a for a in rows if a['context_state'] == 'Keine Lobby')
            error = next(a for a in rows if a['context_state'] == 'Aktualisierung fehlgeschlagen')
            self.assertIn('Noch keine Lobby.', empty['snapshot']['rendered_markup'])
            self.assertNotIn('data-overview-lobby=', empty['snapshot']['rendered_markup'])
            self.assertGreater(error['snapshot']['rendered_markup'].count('data-overview-lobby='), 5)
            self.assertNotRegex(error['snapshot']['rendered_markup'], r'<div[^>]*class="lobby-overview-error"[^>]* hidden')
            self.assertIn('zuletzt geladenen Lobbys bleiben sichtbar', error['snapshot']['rendered_markup'])

    def test_standard_rooms_preserve_guest_controls_capacity_and_reserved_places(self):
        rows = self.rows('standard-room')
        for game, _, _, _, capacity in GAMES:
            if game == 'Perfect':continue
            host = next(a for a in rows if a['game'] == game and a['context_state'] == 'Host · Einstellungen')
            guest = next(a for a in rows if a['game'] == game and a['context_state'] == 'Mitspieler · lesend')
            full = next(a for a in rows if a['game'] == game and a['context_state'] == 'Voll besetzte Lobby')
            self.assertTrue(host['snapshot']['rendered_markup'].startswith('<section class="game-lobby '))
            self.assertEqual(full['snapshot']['rendered_markup'].count('data-profile-window'), capacity)
            self.assertIn('data-lobby-start', host['snapshot']['rendered_markup'])
            self.assertNotIn('data-lobby-start', guest['snapshot']['rendered_markup'])
        reserved = next(a for a in rows if a['game'] == 'Conquest' and a['context_state'] == 'Platz reserviert')
        self.assertIn('Platz reserviert · kommt zurück', reserved['snapshot']['rendered_markup'])
        closed = next(a for a in rows if a['context_state'] == 'Lobby geschlossen')
        self.assertNotIn('data-profile-window', closed['snapshot']['rendered_markup'])
        self.assertIn('Für heute ist der Tisch geschlossen', closed['snapshot']['rendered_markup'])

    def test_perfect_keeps_paper_buzzer_readiness_and_all_player_windows(self):
        rows = self.rows('perfect-room')
        waiting = next(a for a in rows if a['context_state'] == 'Host · wartet auf Bereitschaft')['snapshot']['rendered_markup']
        ready = next(a for a in rows if a['context_state'] == 'Host · alle bereit')['snapshot']['rendered_markup']
        self.assertRegex(waiting, r'<button class="perfect-buzzer"[^>]* disabled')
        self.assertNotRegex(ready, r'<button class="perfect-buzzer"[^>]* disabled')
        self.assertIn('perfect-settings-paper', ready)
        self.assertIn('stormseeds-perfect-start-buzzer-v2.png', ready)
        full = next(a for a in rows if a['context_state'] == 'Voll besetzt · alle bereit')
        self.assertEqual(full['snapshot']['rendered_markup'].count('data-profile-window'), 7)
        guest = next(a for a in rows if a['context_state'] == 'Mitspieler · bereit')['snapshot']['rendered_markup']
        self.assertIn('perfect-settings-paper is-readonly', guest)
        self.assertIn('bereit ✓', guest)
        countdown = next(a for a in rows if a['context_state'] == 'Start-Countdown · feste 3')
        self.assertIn('data-countdown>3', countdown['snapshot']['rendered_markup'])

    def test_shared_inert_preview_keeps_room_backgrounds_and_rejects_stale_sources(self):
        self.assertIs(SourceLobbies.preview, SourceWindows.preview)
        for a in self.source.assets():
            page = self.source.preview(a['id'])
            self.assertIn('<body inert', page)
            self.assertNotIn('<script', page)
            self.assertNotIn(' action=', page)
            self.assertNotIn('csrf_token', page)
            if a['model_id'] in ('lobby-overview', 'lobby-standard-room', 'lobby-perfect-room'):
                self.assertNotIn('background:#142439!important', page)
                self.assertNotRegex(page, r'max-height:\d+px!important;overflow:auto!important')
        record = next(iter(self.source.records.values()));snapshot = deepcopy(record['snapshot'])
        record['snapshot']['evidence'][0]['sha256'] = '0' * 64
        try:
            with self.assertRaises(InvalidDesign):self.source.preview(record['id'])
        finally:record['snapshot'] = snapshot

    def test_concrete_return_variant_survives_reuse_reload_and_handoff_with_old_lobby(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as directory:
            store = ProjectLibrary(Path(directory) / 'library', Path(directory) / 'buttons')
            a = next(a for a in store.assets() if a.get('model_id') == 'lobby-overview-row' and a['context_state'] == 'Reservierter Platz · zurückkehren')
            old = next(a for a in store.assets() if a['kind'] == 'lobby' and a['source'] == 'preset')
            p = empty_project('Lobbyprüfung');p['items'] = [dict(kind='lobby', id=v['id']) for v in (a, old)]
            saved = store.save_project(p)
            q = empty_project('Wiederverwendung');q['items'] = p['items']
            self.assertEqual(store.save_project(q)['items'][0]['snapshot'], a['snapshot'])
            reopened = ProjectLibrary(store.directory, store.buttons_directory)
            self.assertEqual(reopened.handoff(saved['id'])['project']['items'], saved['items'])
            self.assertEqual(list((store.directory / 'elements').glob('*.json')), [])

    def test_http_policy_and_existing_lobby_renderer_remain_available(self):
        with tempfile.TemporaryDirectory(dir=TEST_ROOT) as directory:
            server = serve.make_server(0, Path(directory) / 'library', Path(directory) / 'buttons')
            thread = Thread(target=server.serve_forever, daemon=True);thread.start()
            base = 'http://127.0.0.1:' + str(server.server_port);opener = build_opener(ProxyHandler({}))
            try:
                with opener.open(base + '/api/library', timeout=15) as response:data = json.load(response)
                self.assertEqual(len(data['kinds']), 15)
                self.assertEqual(data['kinds']['lobby']['editor'], 'lobby')
                a = next(a for a in data['assets'] if a['kind'] == 'lobby' and a['source'] == 'game')
                with opener.open(base + a['preview'], timeout=5) as response:
                    self.assertIn("script-src 'none'", response.headers['Content-Security-Policy'])
                    self.assertIn("form-action 'none'", response.headers['Content-Security-Policy'])
                for address, headers in [('/api/game-lobbies/unknown/preview', {}), (a['preview'], {'Host': 'external.example'})]:
                    with self.assertRaises(HTTPError) as error:opener.open(Request(base + address, headers=headers), timeout=5)
                    self.assertIn(error.exception.code, (400, 403));error.exception.close()
            finally:server.shutdown();server.server_close();thread.join(3)


if __name__ == '__main__':unittest.main()
