"""Shared lobby behavior with separate host/guest sessions and disposable data."""
import copy
import re
import unittest
from datetime import datetime

from lobby_view import lobby_player_profiles
import test_card_table as fixtures


class LobbyLayoutTests(unittest.TestCase):
    setUp = fixtures.CardTableTests.setUp
    tearDown = fixtures.CardTableTests.tearDown
    games = ('/party', '/karten', '/karten/wuerfeltisch', '/karten/kniffel',
             '/karten/maexchen', '/karten/welteroberung')

    def create_room(self, base, guest=True):
        host, token = self.clients[0]
        response = host.post(base + '/erstellen', data={'csrf_token': token})
        self.assertEqual(response.status_code, 302)
        room = response.headers['Location']
        if guest:
            client, token = self.clients[1]
            response = client.post(room + '/beitreten', data={'csrf_token': token})
            self.assertEqual(response.status_code, 302)
        return room

    def test_every_standard_lobby_shares_profiles_and_host_guest_control_positions(self):
        with self.app.app_context():
            db = self.app.get_db()
            for uid, avatar, plaque, background in [(1, 'a01', 'p01', 'b01'), (2, 'a02', 'p02', 'b02')]:
                db.execute('INSERT INTO user_cosmetics (user_id,avatar_id,plaque_id,background_id,phrase_id,updated_at) VALUES (?,?,?,?,?,?)',
                           (uid, avatar, plaque, background, '', datetime.now().isoformat()))
            db.commit()
        for base in self.games:
            with self.subTest(game=base):
                room = self.create_room(base)
                for index in (0, 1):
                    page = self.clients[index][0].get(room).get_data(as_text=True)
                    self.assertEqual(page.count('class="game-lobby"'), 1)
                    self.assertEqual(page.count('data-profile-window>'), 2)
                    self.assertIn('avatar-a01 plaque-p01', page)
                    self.assertIn('avatar-a02 plaque-p02', page)
                    self.assertIn('data-lobby-title', page)
                    controls = re.search(r'<aside class="game-lobby-panel game-lobby-controls".*?</aside>', page, re.S)[0]
                    footer = re.search(r'<footer class="game-lobby-footer">.*?</footer>', page, re.S)[0]
                    self.assertIn('Spieleinstellungen', controls)
                    self.assertIn('lobby verlassen', footer)
                    self.assertEqual('data-lobby-start' in controls, index == 0)
                    if index == 1:
                        self.assertIn('class="lobby-summary"', controls)
                        self.assertNotIn('name="csrf_token"', controls)

    def test_profiles_are_current_and_helper_does_not_change_inputs_or_database(self):
        with self.app.app_context():
            db = self.app.get_db()
            db.execute('INSERT INTO user_cosmetics (user_id,avatar_id,plaque_id,background_id,phrase_id,updated_at) VALUES (1,?,?,?,?,?)',
                       ('a03', 'p03', 'b03', '', datetime.now().isoformat()))
            db.commit()
            players = [{'id': 8, 'user_id': 1, 'avatar_id': 'a00', 'display_name': 'Host'},
                       {'id': 'virtual', 'user_id': None, 'virtual': True},
                       {'id': 9, 'user_id': 2, 'avatar_id': 'a02'}]
            original = copy.deepcopy(players)
            changes = db.total_changes
            result = lobby_player_profiles(players)
            self.assertEqual(db.total_changes, changes)
            self.assertEqual(players, original)
            self.assertEqual([p['id'] for p in result], [8, 'virtual', 9])
            self.assertEqual(result[0]['cosmetics'], dict(avatar_id='a03', plaque_id='p03', background_id='b03', phrase_id=''))
            self.assertEqual(result[1]['cosmetics']['avatar_id'], 'a00')
            self.assertEqual(result[2]['cosmetics']['avatar_id'], 'a02')
            db.execute("UPDATE user_cosmetics SET plaque_id='p04' WHERE user_id=1")
            self.assertEqual(lobby_player_profiles(players)[0]['cosmetics']['plaque_id'], 'p04')

    def test_join_and_leave_fill_and_remove_the_same_profile_slots(self):
        for base in self.games:
            with self.subTest(game=base):
                room = self.create_room(base, guest=False)
                host = self.clients[0][0]
                page = host.get(room).get_data(as_text=True)
                self.assertEqual(page.count('data-profile-window>'), 1)
                button = re.search(r'<button[^>]*data-lobby-start[^>]*>', page)[0]
                self.assertEqual(' disabled' in button, base.endswith(('maexchen', 'welteroberung')))
                guest, token = self.clients[1]
                guest.post(room + '/beitreten', data={'csrf_token': token})
                page = host.get(room).get_data(as_text=True)
                self.assertEqual(page.count('data-profile-window>'), 2)
                self.assertNotIn(' disabled', re.search(r'<button[^>]*data-lobby-start[^>]*>', page)[0])
                # All dice modes deliberately use the same leave endpoint.
                leave = re.search(r'<footer class="game-lobby-footer">.*?action="([^"]+)"', page, re.S)[1]
                guest.post(leave, data={'csrf_token': token})
                self.assertEqual(host.get(room).get_data(as_text=True).count('data-profile-window>'), 1)

    def test_perfect_keeps_its_paper_and_buzzer_layout(self):
        room = self.create_room('/nerd')
        page = self.clients[0][0].get(room).get_data(as_text=True)
        self.assertNotIn('class="game-lobby"', page)
        self.assertIn('perfect-settings-paper', page)
        self.assertIn('perfect-buzzer', page)
