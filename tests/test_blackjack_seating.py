from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from threading import Barrier
import json
import tempfile
import unittest

from app import create_app

TEST_ROOT = Path(__file__).resolve().parents[1] / 'runtime/blackjack-seating-tests'


class BlackjackSeatingTests(unittest.TestCase):
    def setUp(self):
        TEST_ROOT.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=TEST_ROOT)
        self.config = dict(TESTING=True, SECRET_KEY='blackjack-seating-test', CARD_TABLE_ENABLED=True,
                           DATABASE=str(Path(self.temp.name) / 'seating.sqlite3'))
        self.app = create_app(self.config)
        self.clients, self.ids = [], []
        with self.app.app_context():
            db = self.app.get_db()
            for index, (name, avatar) in enumerate(zip(('Host', 'Gast', 'Dritter', 'Zuschauer'), ('a05', 'a01', 'a09', 'a00'))):
                uid = db.execute("INSERT INTO users (username, display_name, pin_hash, created_at) VALUES (?, ?, 'unused', ?)",
                                 (name.lower(), name, datetime.now().isoformat())).lastrowid
                db.execute('INSERT INTO user_cosmetics (user_id, avatar_id, updated_at) VALUES (?, ?, ?)', (uid, avatar, datetime.now().isoformat()))
                self.ids.append(uid)
                self.clients.append(self.client(uid, f'token-{index}'))
            db.commit()

    def tearDown(self):
        self.assertTrue(Path(self.temp.name).resolve().is_relative_to(TEST_ROOT.resolve()))
        self.temp.cleanup()

    def client(self, uid, token):
        client = self.app.test_client()
        with client.session_transaction() as session:
            session.update(user_id=uid, csrf_token=token, login_recorded_on=datetime.now().date().isoformat())
        return client, token

    def join(self, index, seat, **extra):
        client, token = self.clients[index]
        return client.post('/karten/blackjack/platz', data=dict(csrf_token=token, seat=seat, **extra))

    def leave(self, index, **extra):
        client, token = self.clients[index]
        return client.post('/karten/blackjack/verlassen', data=dict(csrf_token=token, **extra))

    def state(self, index=0):
        return self.clients[index][0].get('/karten/blackjack/status').get_json()

    def test_authentication_csrf_and_exactly_three_valid_seats(self):
        anonymous = self.app.test_client()
        for url in ('/karten/blackjack', '/karten/blackjack/status'):
            self.assertEqual(anonymous.get(url).status_code, 302)
        self.assertEqual(anonymous.post('/karten/blackjack/platz', data=dict(seat='1')).status_code, 302)
        self.assertEqual(self.clients[0][0].post('/karten/blackjack/platz', data=dict(seat='1', csrf_token='wrong')).status_code, 400)
        for seat in ('0', '4', '-1', '1.0', '', 'true'):
            self.assertEqual(self.join(0, seat).status_code, 400)
        self.assertEqual(self.state()['occupied'], 0)

    def test_direct_table_read_does_not_take_a_seat_or_show_example_hands(self):
        response = self.clients[0][0].get('/karten/blackjack')
        self.assertEqual(response.status_code, 200)
        page = response.get_data(as_text=True)
        for text in ('data-seating', 'blackjack-tisch-sitzansicht-v1.webp', 'blackjack-seating.js', 'Drei Spielerplätze'):
            self.assertIn(text, page)
        self.assertNotIn('Beispieldaten', page)
        self.assertNotIn('Mira', page)
        self.assertEqual(self.state()['viewer_seat'], None)
        self.assertEqual(len(self.state()['seats']), 3)
        self.assertEqual(response.headers['Cache-Control'], 'no-store')
        tiles = self.clients[0][0].get('/karten/kartentische').get_data(as_text=True)
        self.assertIn('href="/karten/blackjack"', tiles)

    def test_public_profile_binding_uses_authenticated_user_and_updates_from_profile(self):
        state = self.join(0, '2', user_id=self.ids[1]).get_json()
        player = state['seats'][1]['player']
        self.assertEqual(player['name'], 'Host')
        self.assertEqual(player['portrait']['avatar_id'], 'a05')
        self.assertTrue(player['is_self'])
        self.assertFalse(self.state(1)['seats'][1]['player']['is_self'])
        with self.app.app_context():
            db = self.app.get_db()
            db.execute('UPDATE users SET display_name=? WHERE id=?', ('<b>Neuer Name</b>', self.ids[0]))
            db.execute('UPDATE user_cosmetics SET avatar_id=? WHERE user_id=?', ('a09', self.ids[0]))
            db.commit()
        self.assertEqual(self.state()['seats'][1]['player']['name'], '<b>Neuer Name</b>')
        self.assertEqual(self.state()['seats'][1]['player']['portrait']['avatar_id'], 'a09')
        page = self.clients[0][0].get('/karten/blackjack').get_data(as_text=True)
        self.assertNotIn('<b>Neuer Name</b>', page)
        for secret in ('pin_hash', 'created_at', 'username', 'user_id', 'score'):
            self.assertNotIn(secret, json.dumps(self.state()))

    def test_idempotent_join_conflict_and_leave_only_own_seat(self):
        self.assertEqual(self.join(0, '2').status_code, 200)
        self.assertEqual(self.join(0, '2').status_code, 200)
        self.assertEqual(self.join(0, '3').status_code, 409)
        self.assertEqual(self.join(1, '2').status_code, 409)
        self.assertEqual(self.state()['viewer_seat'], 2)
        self.leave(1, user_id=self.ids[0])
        self.assertEqual(self.state()['occupied'], 1)
        self.assertEqual(self.clients[0][0].post('/karten/blackjack/verlassen', data=dict(csrf_token='wrong')).status_code, 400)
        self.assertEqual(self.leave(0).get_json()['occupied'], 0)
        self.assertEqual(self.join(1, '2').status_code, 200)
        self.assertEqual(self.state(1)['viewer_seat'], 2)

    def test_three_people_fill_table_and_fourth_stays_a_spectator(self):
        for index in range(3):
            self.assertEqual(self.join(index, str(index+1)).status_code, 200)
        state = self.state(3)
        self.assertEqual(state['occupied'], 3)
        self.assertIsNone(state['viewer_seat'])
        self.assertEqual([s['player']['name'] for s in state['seats']], ['Host', 'Gast', 'Dritter'])
        self.assertEqual(self.join(3, '1').status_code, 409)
        self.assertEqual(self.leave(3).get_json()['occupied'], 3)

    def test_seating_survives_new_application_and_authenticated_session(self):
        self.join(0, '2')
        self.app = create_app(self.config)
        client, token = self.client(self.ids[0], 'reopened')
        state = client.get('/karten/blackjack/status').get_json()
        self.assertEqual(state['viewer_seat'], 2)
        self.assertEqual(state['occupied'], 1)
        self.assertEqual(client.post('/karten/blackjack/platz', data=dict(csrf_token=token, seat='1')).status_code, 409)

    def test_concurrent_claim_has_one_winner_and_no_overwritten_player(self):
        barrier = Barrier(2)
        def claim(index):
            barrier.wait(timeout=5)
            return self.join(index, '2').status_code
        with ThreadPoolExecutor(max_workers=2) as pool:
            responses = list(pool.map(claim, (0, 1)))
        self.assertEqual(sorted(responses), [200, 409])
        state = self.state()
        self.assertEqual(state['occupied'], 1)
        self.assertIn(state['seats'][1]['player']['name'], ('Host', 'Gast'))


if __name__ == '__main__':
    unittest.main()
