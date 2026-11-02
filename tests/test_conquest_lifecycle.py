"""Multiplayer room lifecycle, using separate authenticated players and a fresh DB."""
import json
import unittest

import test_conquest as fixtures


class ConquestLifecycleTests(unittest.TestCase):
    setUp = fixtures.ConquestTests.setUp
    tearDown = fixtures.ConquestTests.tearDown
    create_lobby = fixtures.ConquestTests.create_lobby
    action = fixtures.ConquestTests.action

    def post(self, lobby_id, endpoint, player=0, **values):
        client, token = self.clients[player]
        return client.post(f'/karten/welteroberung/{lobby_id}/{endpoint}',
                           data={'csrf_token': token, **values})

    def status(self, lobby_id, player=0):
        return self.clients[player][0].get(f'/karten/welteroberung/{lobby_id}/status').get_json()

    def stored(self, lobby_id):
        with self.app.app_context():
            return dict(self.app.get_db().execute('SELECT * FROM conquest_lobbies WHERE id=?', (lobby_id,)).fetchone())

    def members(self, lobby_id):
        with self.app.app_context():
            return [dict(row) for row in self.app.get_db().execute(
                'SELECT * FROM conquest_members WHERE lobby_id=? ORDER BY joined_at,id', (lobby_id,))]

    def start(self):
        return fixtures.ConquestTests.start_game(self, finish_setup=False)

    def completed_fixture(self):
        lobby_id = self.start()
        row = self.stored(lobby_id)
        state = json.loads(row['state_json'])
        state.update(phase='completed', winner={'member_id': state['participants'][0]['id'],
                     'name': 'Host', 'reason': 'Welteroberung', 'mission': None})
        with self.app.app_context():
            db = self.app.get_db()
            db.execute("UPDATE conquest_lobbies SET status='completed',state_json=?,completed_at=? WHERE id=?",
                       (json.dumps(state), '2026-10-24T12:00:00', lobby_id))
            db.commit()
        return lobby_id

    def test_host_moves_to_next_present_seat_and_last_leave_closes(self):
        lobby_id = self.create_lobby()
        self.post(lobby_id, 'beitreten', player=1)
        self.post(lobby_id, 'beitreten', player=2)
        seats = self.members(lobby_id)
        self.post(lobby_id, 'verlassen')
        self.assertEqual(self.stored(lobby_id)['host_user_id'], seats[1]['user_id'])
        self.post(lobby_id, 'beitreten')
        self.assertEqual(self.members(lobby_id)[0]['id'], seats[0]['id'])
        self.assertEqual(self.stored(lobby_id)['host_user_id'], seats[1]['user_id'])
        self.post(lobby_id, 'verlassen', player=1)
        self.assertEqual(self.stored(lobby_id)['host_user_id'], seats[0]['user_id'])
        self.post(lobby_id, 'verlassen')
        self.post(lobby_id, 'verlassen', player=2)
        self.assertEqual(self.stored(lobby_id)['status'], 'closed')
        self.assertEqual(self.status(lobby_id)['status'], 'closed')
        self.assertTrue(all(row['status'] == 'left' for row in self.members(lobby_id)))

    def test_leave_preserves_entire_game_and_return_restores_same_actor(self):
        lobby_id = self.start()
        before = self.stored(lobby_id)
        seats = self.members(lobby_id)
        actor = str(json.loads(before['state_json'])['current_member_id'])
        absent = next(i for i, row in enumerate(seats) if str(row['id']) == actor)
        viewer = 1 - absent
        self.post(lobby_id, 'verlassen', player=absent)
        self.assertEqual(self.stored(lobby_id)['state_json'], before['state_json'])
        game = self.status(lobby_id, viewer)['game']
        self.assertEqual(game['waiting_for_member'], 'Host' if absent == 0 else 'Gast')
        self.assertFalse(game['can_act'])
        self.assertFalse(game['can_defend'])
        response = self.action(lobby_id, 'advance', client_index=viewer)
        self.assertEqual(response.status_code, 409)
        self.assertEqual(self.stored(lobby_id)['state_json'], before['state_json'])
        overview = self.clients[absent][0].get('/karten/welteroberung').get_data(as_text=True)
        self.assertIn('Dein Platz ist reserviert', overview)
        self.assertIn('zurückkehren', overview)
        room = self.clients[viewer][0].get(f'/karten/welteroberung/{lobby_id}/lobby').get_data(as_text=True)
        self.assertIn('Platz reserviert', room)
        self.post(lobby_id, 'beitreten', player=2)
        self.assertEqual(len(self.members(lobby_id)), 2)
        self.post(lobby_id, 'beitreten', player=absent)
        self.assertEqual([(r['id'], r['joined_at']) for r in self.members(lobby_id)],
                         [(r['id'], r['joined_at']) for r in seats])
        self.assertEqual(self.stored(lobby_id)['state_json'], before['state_json'])
        resumed = self.status(lobby_id, absent)['game']
        self.assertIsNone(resumed['waiting_for_member'])
        self.assertTrue(resumed['can_act'])
        target = next(key for key, row in resumed['territories'].items() if str(row['owner']) == resumed['setup']['target_owner'])
        self.assertEqual(self.action(lobby_id, 'place', client_index=absent, to=target, count=1).status_code, 200)

    def test_absent_defender_pauses_even_when_attacker_stays(self):
        lobby_id = self.start()
        before = self.stored(lobby_id)
        state = json.loads(before['state_json'])
        seats = self.members(lobby_id)
        state['current_member_id'] = str(seats[0]['id'])
        state['phase'] = 'attack'
        state['battle_request'] = {'from': 'alaska', 'to': 'kamtschatka', 'defender': str(seats[1]['id']), 'dice': 3}
        with self.app.app_context():
            self.app.get_db().execute('UPDATE conquest_lobbies SET state_json=? WHERE id=?', (json.dumps(state), lobby_id))
            self.app.get_db().commit()
        self.post(lobby_id, 'verlassen', player=1)
        self.assertEqual(self.status(lobby_id)['game']['waiting_for_member'], 'Gast')
        self.assertEqual(self.action(lobby_id, 'attack', to='kamtschatka', **{'from': 'alaska'}, dice=3).status_code, 409)
        self.post(lobby_id, 'beitreten', player=1)
        self.assertIsNone(self.status(lobby_id)['game']['waiting_for_member'])

    def test_only_host_can_close_and_known_viewers_observe_closure(self):
        lobby_id = self.start()
        self.assertEqual(self.post(lobby_id, 'beenden', player=1).status_code, 403)
        self.assertEqual(self.clients[2][0].get(f'/karten/welteroberung/{lobby_id}/lobby').status_code, 404)
        before = self.stored(lobby_id)['state_json']
        self.assertEqual(self.post(lobby_id, 'beenden').status_code, 302)
        self.assertEqual(self.status(lobby_id, 1)['status'], 'closed')
        self.assertEqual(self.stored(lobby_id)['state_json'], before)
        self.post(lobby_id, 'beitreten', player=1)
        self.assertEqual(self.stored(lobby_id)['status'], 'closed')
        self.assertTrue(all(row['status'] == 'left' for row in self.members(lobby_id)))

    def test_rematch_keeps_seats_archives_final_game_and_starts_fresh(self):
        lobby_id = self.completed_fixture()
        finished = self.stored(lobby_id)
        seats = self.members(lobby_id)
        self.assertEqual(self.post(lobby_id, 'nochmal', player=1, revision=finished['revision']).status_code, 403)
        self.assertEqual(self.post(lobby_id, 'nochmal', revision=finished['revision'] - 1).status_code, 409)
        self.assertEqual(self.post(lobby_id, 'nochmal', revision=finished['revision']).status_code, 302)
        room = self.stored(lobby_id)
        self.assertEqual(room['status'], 'waiting')
        self.assertIsNone(room['state_json'])
        self.assertIsNone(room['completed_at'])
        self.assertEqual(self.members(lobby_id), seats)
        with self.app.app_context():
            history = self.app.get_db().execute('SELECT * FROM conquest_game_history WHERE lobby_id=?', (lobby_id,)).fetchall()
            self.assertEqual(len(history), 1)
            self.assertEqual(history[0]['state_json'], finished['state_json'])
        self.assertEqual(self.status(lobby_id, 1)['status'], 'waiting')
        self.assertEqual(self.post(lobby_id, 'nochmal', revision=finished['revision']).status_code, 409)
        self.post(lobby_id, 'starten')
        self.assertEqual(self.status(lobby_id)['game']['phase'], 'setup')
        self.assertIsNone(self.status(lobby_id)['game']['winner'])

    def test_completed_host_handoff_does_not_duplicate_history_or_reactivate_left_player(self):
        lobby_id = self.completed_fixture()
        self.post(lobby_id, 'verlassen')
        now = self.stored(lobby_id)
        self.post(lobby_id, 'nochmal', player=1, revision=now['revision'])
        self.assertEqual(self.members(lobby_id)[0]['status'], 'left')
        with self.app.app_context():
            count = self.app.get_db().execute('SELECT COUNT(*) FROM conquest_game_history WHERE lobby_id=?', (lobby_id,)).fetchone()[0]
            self.assertEqual(count, 1)

    def test_no_midgame_reset_and_csrf_still_required(self):
        lobby_id = self.start()
        before = self.stored(lobby_id)
        self.assertEqual(self.post(lobby_id, 'nochmal', revision=before['revision']).status_code, 409)
        for endpoint in ('beenden', 'nochmal', 'verlassen'):
            response = self.clients[0][0].post(f'/karten/welteroberung/{lobby_id}/{endpoint}', data={})
            self.assertEqual(response.status_code, 400)
        self.assertEqual(self.stored(lobby_id)['state_json'], before['state_json'])

    def test_settings_save_room_name_and_guests_see_same_rules(self):
        lobby_id = self.create_lobby()
        self.post(lobby_id, 'beitreten', player=1)
        response = self.post(lobby_id, 'einstellungen', name='Freitagsrunde', board_style='klassisch',
                             card_style='klassisch', figure_style='klassisch', dice_style='klassisch',
                             victory_mode='world', setup_mode='automatic')
        self.assertEqual(response.status_code, 302)
        guest = self.clients[1][0].get(f'/karten/welteroberung/{lobby_id}/lobby').get_data(as_text=True)
        self.assertIn('Freitagsrunde', guest)
        self.assertIn('Welteroberung', guest)
        self.assertIn('data-profile-window', guest)
        self.assertEqual(self.status(lobby_id, 1)['name'], 'Freitagsrunde')


    def test_player_count_follows_joins_and_ignores_a_legacy_configured_limit(self):
        lobby_id=self.create_lobby()
        with self.app.app_context():
            db=self.app.get_db()
            db.execute('ALTER TABLE conquest_lobbies ADD COLUMN player_limit INTEGER NOT NULL DEFAULT 2')
            db.commit()
        self.post(lobby_id,'beitreten',player=1)
        self.post(lobby_id,'beitreten',player=2)
        self.assertEqual(len(self.members(lobby_id)),3)
        page=self.clients[0][0].get(f'/karten/welteroberung/{lobby_id}').get_data(as_text=True)
        self.assertNotIn('name="player_limit"',page)
        self.assertIn('3/6 Plätze belegt',page)
        overview=self.clients[2][0].get('/karten/welteroberung').get_data(as_text=True)
        self.assertIn('3/6 Spieler',overview)
        self.assertNotIn('player_limit',self.status(lobby_id))
        self.assertEqual(self.post(lobby_id,'einstellungen',player_limit=1).status_code,302)
        self.assertEqual(self.stored(lobby_id)['player_limit'],2)
        self.assertEqual(self.post(lobby_id,'starten').status_code,302)
        self.assertEqual(len(self.status(lobby_id)['game']['armies']),3)

    def test_selected_colors_follow_the_armies_and_color_missions_use_actual_colors(self):
        from conquest_turns import COLORS
        lobby_id=self.create_lobby();self.post(lobby_id,'beitreten',player=1)
        members=self.members(lobby_id)
        self.assertEqual(self.post(lobby_id,'einstellungen',**{f"color_{members[0]['id']}":5,f"color_{members[1]['id']}":3}).status_code,302)
        before=self.stored(lobby_id)
        self.assertEqual(self.post(lobby_id,'einstellungen',**{f"color_{members[1]['id']}":5}).status_code,400)
        self.assertEqual(self.stored(lobby_id)['revision'],before['revision'])
        self.assertEqual(self.post(lobby_id,'starten').status_code,302)
        game=self.status(lobby_id)['game']
        self.assertEqual([row['color'] for row in game['armies'][:2]],[COLORS[5][0],COLORS[3][0]])
        state=json.loads(self.stored(lobby_id)['state_json'])
        self.assertEqual([row['color_index'] for row in state['participants']],[5,3])
        self.assertTrue(all(mission not in ('mission-gelb','mission-blau','mission-violett') for mission in state['missions'].values()))
