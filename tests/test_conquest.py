import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from app import create_app


class ConquestTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.app = create_app({
            "TESTING": True,
            "SECRET_KEY": "conquest-test",
            "CARD_TABLE_ENABLED": True,
            "DATABASE": str(Path(self.tempdir.name) / "test.sqlite3"),
        })
        self.clients = []
        with self.app.app_context():
            database = self.app.get_db()
            for index, name in enumerate(("Host", "Gast", "Dritter"), 1):
                user_id = database.execute(
                    "INSERT INTO users (username, display_name, pin_hash, created_at) VALUES (?, ?, 'unused', ?)",
                    (name.casefold(), name, datetime.now().isoformat()),
                ).lastrowid
                client = self.app.test_client()
                token = f"conquest-token-{index}"
                with client.session_transaction() as player_session:
                    player_session["user_id"] = user_id
                    player_session["csrf_token"] = token
                    player_session["login_recorded_on"] = datetime.now().date().isoformat()
                self.clients.append((client, token))
            database.commit()

    def tearDown(self):
        self.tempdir.cleanup()

    def create_lobby(self):
        response = self.clients[0][0].post(
            "/karten/welteroberung/erstellen",
            data={"csrf_token": self.clients[0][1]},
        )
        self.assertEqual(response.status_code, 302)
        return int(response.headers["Location"].rstrip("/").split("/")[-1])

    def test_every_sea_connection_is_an_existing_bidirectional_neighbor_pair(self):
        world = json.loads((Path(__file__).parents[1] / "static" / "conquest" / "world.json").read_text(encoding="utf-8"))
        territories = {territory["id"]: territory for territory in world["territories"]}
        connections = {frozenset(connection) for connection in world["seaConnections"]}
        self.assertEqual(len(connections), len(world["seaConnections"]))
        for first, second in world["seaConnections"]:
            self.assertIn(second, territories[first]["neighbors"])
            self.assertIn(first, territories[second]["neighbors"])

    def test_lobby_create_join_and_independent_skin_choices(self):
        lobby_id = self.create_lobby()
        self.clients[1][0].post(
            f"/karten/welteroberung/{lobby_id}/beitreten",
            data={"csrf_token": self.clients[1][1]},
        )
        response = self.clients[0][0].post(
            f"/karten/welteroberung/{lobby_id}/einstellungen",
            data={
                "csrf_token": self.clients[0][1],
                "board_style": "taktisch",
                "card_style": "farbenfroh",
                "figure_style": "fantasy",
                "dice_style": "modern",
                "victory_mode": "missions",
                "setup_mode": "automatic",
            },
        )
        self.assertEqual(response.status_code, 302)
        page = self.clients[0][0].get(f"/karten/welteroberung/{lobby_id}").get_data(as_text=True)
        self.assertIn("2/6 Plätze belegt", page)
        self.assertNotIn('name="figure_style"', page)
        self.assertNotIn('name="card_style"', page)
        self.assertNotIn('Länderzuteilung', page)
        with self.app.app_context():
            row = self.app.get_db().execute('SELECT * FROM conquest_lobbies WHERE id=?', (lobby_id,)).fetchone()
            self.assertEqual(row['figure_style'], 'fantasy')
            self.assertEqual(row['card_style'], 'farbenfroh')

    def test_start_builds_complete_private_mission_game_state(self):
        lobby_id = self.create_lobby()
        self.clients[1][0].post(
            f"/karten/welteroberung/{lobby_id}/beitreten",
            data={"csrf_token": self.clients[1][1]},
        )
        with patch("conquest.secrets.SystemRandom") as random_source:
            # An unavailable orange mission would be dealt first without filtering.
            random_source.return_value.shuffle.side_effect = lambda rows: rows.sort(key=lambda row: row["id"] != "mission-orange")
            response = self.clients[0][0].post(
                f"/karten/welteroberung/{lobby_id}/starten",
                data={"csrf_token": self.clients[0][1]},
            )
        self.assertEqual(response.status_code, 302)
        page = self.clients[0][0].get(response.headers["Location"]).get_data(as_text=True)
        self.assertIn('id="conquest-config"', page)
        self.assertIn("tisch-assets/scene.js", page)
        self.assertIn("conquest/world.json", page)
        self.assertNotIn("data-deck=", page)
        self.assertNotIn("data-conquest-dice", page)
        self.assertNotIn('data-style="taktisch"', page)
        status = self.clients[0][0].get(f"/karten/welteroberung/{lobby_id}/status").get_json()
        self.assertEqual(status["status"], "playing")
        self.assertEqual(len(status["game"]["territories"]), 42)
        self.assertTrue(status["game"]["own_mission"].startswith("mission-"))
        self.assertEqual(status["game"]["inventory"]["territory_cards"], [])
        self.assertEqual(status["game"]["inventory"]["mission"]["id"], status["game"]["own_mission"])
        self.assertIn("neutral", {str(item["owner"]) for item in status["game"]["territories"].values()})
        with self.app.app_context():
            stored = json.loads(self.app.get_db().execute("SELECT state_json FROM conquest_lobbies WHERE id = ?", (lobby_id,)).fetchone()[0])
            self.assertEqual(stored['phase'], 'setup')
            self.assertEqual(sum(item["armies"] for item in stored["territories"].values()), 42)
            self.assertEqual(sum(stored['setup']['remaining'].values()), 52)
            self.assertEqual(stored['setup']['neutral_remaining'], 26)
            self.assertTrue(all(mission not in {"mission-blau", "mission-gruen", "mission-violett", "mission-orange"} for mission in stored["missions"].values()))

    def test_only_own_secret_mission_is_exposed(self):
        lobby_id = self.create_lobby()
        self.clients[1][0].post(
            f"/karten/welteroberung/{lobby_id}/beitreten",
            data={"csrf_token": self.clients[1][1]},
        )
        self.clients[0][0].post(
            f"/karten/welteroberung/{lobby_id}/starten",
            data={"csrf_token": self.clients[0][1]},
        )
        host_state = self.clients[0][0].get(f"/karten/welteroberung/{lobby_id}/status").get_json()["game"]
        guest_state = self.clients[1][0].get(f"/karten/welteroberung/{lobby_id}/status").get_json()["game"]
        self.assertNotEqual(host_state["own_mission"], guest_state["own_mission"])
        self.assertNotIn("missions", host_state)

    def test_inventory_uses_persisted_private_hands_and_survives_reload(self):
        lobby_id = self.create_lobby()
        self.clients[1][0].post(
            f"/karten/welteroberung/{lobby_id}/beitreten",
            data={"csrf_token": self.clients[1][1]},
        )
        self.clients[0][0].post(
            f"/karten/welteroberung/{lobby_id}/starten",
            data={"csrf_token": self.clients[0][1]},
        )
        with self.app.app_context():
            database = self.app.get_db()
            members = database.execute("SELECT id FROM conquest_members WHERE lobby_id = ? ORDER BY id", (lobby_id,)).fetchall()
            state = json.loads(database.execute("SELECT state_json FROM conquest_lobbies WHERE id = ?", (lobby_id,)).fetchone()[0])
            state["hands"] = {str(members[0]["id"]): ["alaska"], str(members[1]["id"]): ["brasilien", "peru"]}
            database.execute("UPDATE conquest_lobbies SET state_json = ?, revision = revision + 1 WHERE id = ?", (json.dumps(state), lobby_id))
            database.commit()
        host = self.clients[0][0]
        guest = self.clients[1][0]
        host_inventory = host.get(f"/karten/welteroberung/{lobby_id}/status").get_json()["game"]["inventory"]
        guest_inventory = guest.get(f"/karten/welteroberung/{lobby_id}/status").get_json()["game"]["inventory"]
        self.assertEqual(host_inventory["territory_cards"], [{"id": "alaska", "name": "Alaska", "symbol": "infantry", "type": "Infanterie"}])
        self.assertEqual([card["id"] for card in guest_inventory["territory_cards"]], ["brasilien", "peru"])
        self.assertNotEqual(host_inventory["mission"], guest_inventory["mission"])
        host.get(f"/karten/welteroberung/{lobby_id}")
        self.assertEqual(host_inventory, host.get(f"/karten/welteroberung/{lobby_id}/status").get_json()["game"]["inventory"])

    def test_old_saved_start_state_without_hands_has_empty_inventory(self):
        from conquest import _private_inventory

        self.assertEqual(_private_inventory({"missions": {}}, 1), {"territory_cards": [], "mission": None})

    def start_game(self, developer=False, finish_setup=True):
        lobby_id = self.create_lobby()
        if developer:
            self.app.config['LOCAL_DEVELOPMENT'] = True
            with self.app.app_context():
                db = self.app.get_db()
                db.execute("UPDATE users SET username = 'stormseed' WHERE username = 'host'")
                db.execute("INSERT INTO user_cosmetics (user_id, developer_enabled, updated_at) SELECT id, 1, ? FROM users WHERE username = 'stormseed'", (datetime.now().isoformat(),))
                db.commit()
        else:
            self.clients[1][0].post(f'/karten/welteroberung/{lobby_id}/beitreten', data={'csrf_token': self.clients[1][1]})
        with self.app.app_context():
            self.app.get_db().execute("UPDATE conquest_lobbies SET victory_mode='world' WHERE id=?", (lobby_id,))
            self.app.get_db().commit()
        result = self.clients[0][0].post(f'/karten/welteroberung/{lobby_id}/starten',
            data={'csrf_token': self.clients[0][1], 'developer_test': '1' if developer else '0'})
        self.assertEqual(result.status_code, 302)
        if finish_setup:
            for _ in range(160):
                game = self.clients[0][0].get(f'/karten/welteroberung/{lobby_id}/status').get_json()['game']
                if game['phase'] != 'setup': break
                client_index = 0 if developer or str(game['current_member_id']) == game['armies'][0]['id'] else 1
                target = next(key for key, row in game['territories'].items() if str(row['owner']) == game['setup']['target_owner'])
                self.assertEqual(self.action(lobby_id, 'place', client_index=client_index, to=target, count=1).status_code, 200)
            else: self.fail('Startaufstellung wurde nicht beendet.')
        return lobby_id

    def action(self, lobby_id, action, client_index=0, **fields):
        client, token = self.clients[client_index]
        state = client.get(f'/karten/welteroberung/{lobby_id}/status').get_json()
        return client.post(f'/karten/welteroberung/{lobby_id}/aktion',
            data={'csrf_token': token, 'revision': state['revision'], 'action': action, **fields})

    def test_initial_placement_is_saved_in_join_order_and_duplicate_requests_do_not_place_twice(self):
        lobby_id = self.start_game(developer=True, finish_setup=False)
        client, token = self.clients[0]
        before = client.get(f'/karten/welteroberung/{lobby_id}/status').get_json()
        actor = str(before['game']['current_member_id'])
        target = next(key for key, row in before['game']['territories'].items() if str(row['owner']) == actor)
        body = dict(csrf_token=token, revision=before['revision'], action='place', to=target, count=1)
        saved = client.post(f'/karten/welteroberung/{lobby_id}/aktion', data=body)
        self.assertEqual(saved.status_code, 200)
        self.assertEqual(client.post(f'/karten/welteroberung/{lobby_id}/aktion', data=body).status_code, 409)
        payload = client.get(f'/karten/welteroberung/{lobby_id}/status').get_json()
        self.assertEqual(payload['game']['territories'][target]['armies'], 2)
        self.assertEqual(payload['game']['setup']['remaining'][actor], before['game']['setup']['remaining'][actor] - 1)
        self.assertEqual(payload['game']['current_member_id'], 'test-rot')
        client.get(f'/karten/welteroberung/{lobby_id}')
        self.assertEqual(client.get(f'/karten/welteroberung/{lobby_id}/status').get_json(), payload)

    def test_developer_start_uses_virtual_armies_without_creating_users(self):
        lobby_id = self.start_game(developer=True)
        status = self.clients[0][0].get(f'/karten/welteroberung/{lobby_id}/status').get_json()
        game = status['game']
        self.assertTrue(game['developer'])
        self.assertTrue(game['can_act'])
        self.assertEqual(len(game['armies']), 3)
        self.assertEqual(game['remaining'], game['reinforcement']['total'])
        self.assertGreaterEqual(game['remaining'], 4)
        self.assertEqual(sum(row['armies'] for row in game['territories'].values()), 105)
        with self.app.app_context():
            self.assertEqual(self.app.get_db().execute('SELECT COUNT(*) FROM users').fetchone()[0], 3)
            self.assertEqual(self.app.get_db().execute('SELECT COUNT(*) FROM conquest_members').fetchone()[0], 1)

    def test_developer_start_requires_local_mode_owner_and_enabled_flag(self):
        lobby_id = self.create_lobby()
        client, token = self.clients[0]
        for local in (False, True):
            self.app.config['LOCAL_DEVELOPMENT'] = local
            self.assertEqual(client.post(f'/karten/welteroberung/{lobby_id}/starten',
                data={'csrf_token': token, 'developer_test': '1'}).status_code, 403)
        with self.app.app_context():
            self.app.get_db().execute("UPDATE users SET username = 'stormseed' WHERE username = 'host'")
            self.app.get_db().commit()
        self.assertEqual(client.post(f'/karten/welteroberung/{lobby_id}/starten',
            data={'csrf_token': token, 'developer_test': '1'}).status_code, 403)

    def test_place_persists_and_rejects_duplicate_revision_foreign_and_excess(self):
        lobby_id = self.start_game(developer=True)
        client, token = self.clients[0]
        before = client.get(f'/karten/welteroberung/{lobby_id}/status').get_json()
        game = before['game']
        own = next(key for key, row in game['territories'].items() if str(row['owner']) == str(game['current_member_id']))
        foreign = next(key for key, row in game['territories'].items() if str(row['owner']) != str(game['current_member_id']))
        for target, count in ((foreign, 1), (own, game['remaining'] + 1)):
            self.assertEqual(self.action(lobby_id, 'place', to=target, count=count).status_code, 400)
        self.assertEqual(self.action(lobby_id, 'advance').status_code, 400)
        result = self.action(lobby_id, 'place', to=own, count=1)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(client.post(f'/karten/welteroberung/{lobby_id}/aktion',
            data={'csrf_token': token, 'revision': before['revision'], 'action': 'place', 'to': own, 'count': 1}).status_code, 409)
        client.get(f'/karten/welteroberung/{lobby_id}')
        after = client.get(f'/karten/welteroberung/{lobby_id}/status').get_json()['game']
        self.assertEqual(after['remaining'], game['remaining'] - 1)
        self.assertEqual(after['territories'][own]['armies'], game['territories'][own]['armies'] + 1)

    def test_complete_developer_turn_and_handoff_survive_reload(self):
        lobby_id = self.start_game(developer=True)
        client = self.clients[0][0]
        game = client.get(f'/karten/welteroberung/{lobby_id}/status').get_json()['game']
        own = next(key for key, row in game['territories'].items() if str(row['owner']) == str(game['current_member_id']))
        self.assertEqual(self.action(lobby_id, 'place', to=own, count=game['remaining']).status_code, 200)
        self.assertEqual(self.action(lobby_id, 'advance').get_json()['game']['phase'], 'attack')
        self.assertEqual(self.action(lobby_id, 'advance').get_json()['game']['phase'], 'fortify')
        ended = self.action(lobby_id, 'advance').get_json()['game']
        self.assertEqual(ended['phase'], 'ended')
        self.assertEqual(ended['inventory']['territory_cards'], [])
        self.assertEqual(self.action(lobby_id, 'advance').status_code, 400)
        next_game = self.action(lobby_id, 'pass').get_json()['game']
        self.assertNotEqual(str(next_game['current_member_id']), str(game['current_member_id']))
        self.assertEqual(next_game['phase'], 'reinforce')
        self.assertTrue(next_game['can_act'])
        self.assertEqual(next_game['territories'], ended['territories'])
        self.assertEqual(client.get(f'/karten/welteroberung/{lobby_id}/status').get_json()['game'], next_game)

    def test_non_current_player_cannot_move_and_defense_resolves_automatically(self):
        lobby_id = self.start_game()
        with self.app.app_context():
            db = self.app.get_db()
            state = json.loads(db.execute('SELECT state_json FROM conquest_lobbies WHERE id=?', (lobby_id,)).fetchone()[0])
            members = db.execute('SELECT id FROM conquest_members ORDER BY id').fetchall()
            state.update(current_member_id=members[0][0], phase='attack')
            state['territories']['alaska'] = {'owner': members[0][0], 'armies': 5}
            state['territories']['alberta'] = {'owner': members[1][0], 'armies': 2}
            db.execute('UPDATE conquest_lobbies SET state_json=? WHERE id=?', (json.dumps(state), lobby_id)); db.commit()
        self.assertEqual(self.action(lobby_id, 'advance', client_index=1).status_code, 403)
        with patch('conquest_turns.secrets.randbelow', side_effect=[5, 4, 3, 0, 0]):
            defended = self.action(lobby_id, 'attack', **{'from': 'alaska', 'to': 'alberta', 'dice': 3}).get_json()
        self.assertTrue(defended['result']['conquered'])
        self.assertIsNone(defended['game']['battle_request'])
        self.assertFalse(defended['game']['can_defend'])
        self.assertEqual(len(defended['result']['defenseRolls']), 2)
        self.assertEqual(defended['result']['defenderId'], str(members[1][0]))
        self.assertEqual(self.action(lobby_id, 'defend', client_index=1, dice=1).status_code, 403)
        self.assertEqual(defended['result']['attackRolls'], [6, 5, 4])
        self.assertEqual(self.action(lobby_id, 'advance').status_code, 400)
        self.assertEqual(self.action(lobby_id, 'occupy', count=2).status_code, 400)
        occupied = self.action(lobby_id, 'occupy', count=3).get_json()['game']
        self.assertEqual(occupied['territories']['alaska']['armies'], 2)
        self.assertEqual(occupied['territories']['alberta']['armies'], 3)
        self.action(lobby_id, 'advance')
        ended = self.action(lobby_id, 'advance').get_json()['game']
        self.assertEqual(len(ended['inventory']['territory_cards']), 1)
        guest = self.clients[1][0].get(f'/karten/welteroberung/{lobby_id}/status').get_json()['game']
        self.assertEqual(guest['inventory']['territory_cards'], [])
        self.assertIsNone(guest['end_result']['card'])

    def test_automatic_defense_uses_one_or_two_dice_from_actual_garrison(self):
        lobby_id = self.start_game()
        with self.app.app_context():
            db = self.app.get_db()
            original = json.loads(db.execute('SELECT state_json FROM conquest_lobbies WHERE id=?', (lobby_id,)).fetchone()[0])
            host, guest = [row['id'] for row in original['participants']]
        for armies in (1, 2, 5):
            with self.subTest(armies=armies):
                state = json.loads(json.dumps(original))
                state.update(current_member_id=host, phase='attack')
                state['territories']['alaska'] = {'owner': host, 'armies': 5}
                state['territories']['alberta'] = {'owner': guest, 'armies': armies}
                with self.app.app_context():
                    db = self.app.get_db()
                    db.execute('UPDATE conquest_lobbies SET state_json=? WHERE id=?', (json.dumps(state), lobby_id)); db.commit()
                with patch('conquest_turns.secrets.randbelow', return_value=5):
                    response = self.action(lobby_id, 'attack', **{'from':'alaska','to':'alberta','dice':3})
                self.assertEqual(response.status_code, 200)
                payload = response.get_json()
                self.assertEqual(len(payload['result']['defenseRolls']), min(2, armies))
                self.assertIsNone(payload['game']['battle_request'])
                self.assertFalse(payload['game']['can_defend'])

    def test_saved_pending_defense_resumes_at_maximum_without_client_choice(self):
        lobby_id = self.start_game()
        with self.app.app_context():
            db = self.app.get_db()
            original = json.loads(db.execute('SELECT state_json FROM conquest_lobbies WHERE id=?', (lobby_id,)).fetchone()[0])
            host, guest = [row['id'] for row in original['participants']]
        for armies, submitted in ((1, 99), (2, 1), (5, 0)):
            with self.subTest(armies=armies, submitted=submitted):
                state = json.loads(json.dumps(original))
                state.update(current_member_id=host, phase='attack', battle_request={'from':'alaska','to':'alberta','dice':3,'defender':guest})
                state['territories']['alaska'] = {'owner':host,'armies':5}
                state['territories']['alberta'] = {'owner':guest,'armies':armies}
                with self.app.app_context():
                    db = self.app.get_db()
                    db.execute('UPDATE conquest_lobbies SET state_json=? WHERE id=?', (json.dumps(state), lobby_id)); db.commit()
                with patch('conquest_turns.secrets.randbelow', return_value=5):
                    response = self.action(lobby_id, 'defend', client_index=1, dice=submitted)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.get_json()['result']['defenseRolls']), min(2, armies))
                self.assertIsNone(response.get_json()['game']['battle_request'])

    def test_table_assets_are_allowlisted_and_use_same_component_as_preview(self):
        client = self.clients[0][0]
        for filename in ('scene.js', 'table-surface.js', 'remote-turn.js', 'style.css', 'assets/karte.png'):
            response = client.get('/karten/welteroberung/tisch-assets/' + filename)
            self.assertEqual(response.status_code, 200)
            response.close()
        for filename in ('README.md', 'attack.test.js', 'assets/world.json', '../../app.py'):
            self.assertEqual(client.get('/karten/welteroberung/tisch-assets/' + filename).status_code, 404)

    def test_finish_is_atomic_advances_once_and_keeps_reward_private_after_reload(self):
        lobby_id = self.start_game()
        client, token = self.clients[0]
        with self.app.app_context():
            db = self.app.get_db()
            state = json.loads(db.execute('SELECT state_json FROM conquest_lobbies WHERE id=?', (lobby_id,)).fetchone()[0])
            host, guest = [row['id'] for row in state['participants']]
            state.update(current_member_id=host, phase='fortify', conquered_count=1, remaining=0)
            db.execute('UPDATE conquest_lobbies SET state_json=? WHERE id=?', (json.dumps(state), lobby_id)); db.commit()
        revision = client.get(f'/karten/welteroberung/{lobby_id}/status').get_json()['revision']
        data = {'csrf_token':token,'revision':revision,'action':'finish'}
        completed = client.post(f'/karten/welteroberung/{lobby_id}/aktion', data=data)
        self.assertEqual(completed.status_code, 200)
        payload = completed.get_json()
        self.assertEqual(payload['revision'], revision + 1)
        self.assertEqual(str(payload['game']['current_member_id']), str(guest))
        self.assertEqual(payload['game']['phase'], 'reinforce')
        self.assertIsNone(payload['game']['end_result'])
        reward = payload['result']['endResult']['card']
        self.assertEqual(payload['game']['last_turn_result']['card'], reward)
        self.assertEqual(len(payload['game']['inventory']['territory_cards']), 1)
        self.assertEqual(client.post(f'/karten/welteroberung/{lobby_id}/aktion', data=data).status_code, 409)
        reloaded = client.get(f'/karten/welteroberung/{lobby_id}/status').get_json()
        self.assertEqual(reloaded['revision'], revision + 1)
        self.assertEqual(reloaded['game']['last_turn_result']['card'], reward)
        self.assertEqual(len(reloaded['game']['inventory']['territory_cards']), 1)
        other = self.clients[1][0].get(f'/karten/welteroberung/{lobby_id}/status').get_json()['game']
        self.assertIsNone(other['last_turn_result'])
        self.assertEqual(other['inventory']['territory_cards'], [])

    def test_finish_resumes_an_already_awarded_old_turn_without_another_card(self):
        lobby_id = self.start_game()
        with self.app.app_context():
            db = self.app.get_db()
            state = json.loads(db.execute('SELECT state_json FROM conquest_lobbies WHERE id=?', (lobby_id,)).fetchone()[0])
            state.update(current_member_id=state['participants'][0]['id'], phase='fortify', conquered_count=1)
            db.execute('UPDATE conquest_lobbies SET state_json=? WHERE id=?', (json.dumps(state), lobby_id)); db.commit()
        old = self.action(lobby_id, 'advance').get_json()['game']
        self.assertEqual(old['phase'], 'ended')
        reward = old['end_result']['card']
        finished = self.action(lobby_id, 'finish').get_json()['game']
        self.assertEqual(finished['phase'], 'reinforce')
        self.assertEqual(len(finished['inventory']['territory_cards']), 1)
        self.assertEqual(finished['last_turn_result']['card'], reward)

    def test_victory_is_atomic_persistent_public_and_prevents_further_moves(self):
        lobby_id = self.start_game()
        client, token = self.clients[0]
        with self.app.app_context():
            db = self.app.get_db()
            state = json.loads(db.execute('SELECT state_json FROM conquest_lobbies WHERE id=?', (lobby_id,)).fetchone()[0])
            host, guest = [row['id'] for row in state['participants']]
            state.update(current_member_id=host, phase='reinforce', remaining=1, victory_mode='missions',
                         missions={host: 'mission-18-doppelt', guest: 'mission-gelb'})
            for index, row in enumerate(state['territories'].values()):
                row.update(owner=host if index < 18 else guest, armies=2 if index < 17 else 1)
            target = list(state['territories'])[17]
            db.execute('UPDATE conquest_lobbies SET state_json=? WHERE id=?', (json.dumps(state), lobby_id)); db.commit()
        before = client.get(f'/karten/welteroberung/{lobby_id}/status').get_json()
        body = dict(csrf_token=token, revision=before['revision'], action='place', to=target, count=1)
        response = client.post(f'/karten/welteroberung/{lobby_id}/aktion', data=body)
        self.assertEqual(response.status_code, 200)
        saved = response.get_json()
        self.assertEqual(saved['status'], 'completed')
        self.assertEqual(saved['game']['winner']['member_id'], host)
        self.assertFalse(saved['game']['can_act'])
        self.assertEqual(client.post(f'/karten/welteroberung/{lobby_id}/aktion', data=body).status_code, 409)
        for player, _ in self.clients[:2]:
            payload = player.get(f'/karten/welteroberung/{lobby_id}/status').get_json()
            self.assertEqual(payload['status'], 'completed')
            self.assertEqual(payload['revision'], before['revision'] + 1)
            self.assertEqual(payload['game']['winner'], saved['game']['winner'])
            self.assertEqual(player.get(f'/karten/welteroberung/{lobby_id}').status_code, 200)
            self.assertIn('ergebnis ansehen', player.get('/karten/welteroberung').get_data(as_text=True))
        self.assertEqual(self.clients[2][0].get(f'/karten/welteroberung/{lobby_id}').status_code, 404)
        self.assertNotIn('ergebnis ansehen', self.clients[2][0].get('/karten/welteroberung').get_data(as_text=True))
        with self.app.app_context():
            row = self.app.get_db().execute('SELECT status, completed_at, state_json FROM conquest_lobbies WHERE id=?', (lobby_id,)).fetchone()
            self.assertEqual(row['status'], 'completed')
            self.assertTrue(row['completed_at'])
            self.assertEqual(json.loads(row['state_json'])['winner'], saved['game']['winner'])
        self.assertNotEqual(self.create_lobby(), lobby_id)

    def test_card_exchange_is_saved_once_and_blocks_placement_until_required_trade(self):
        lobby_id = self.start_game(developer=True)
        with self.app.app_context():
            db = self.app.get_db()
            state = json.loads(db.execute('SELECT state_json FROM conquest_lobbies WHERE id=?', (lobby_id,)).fetchone()[0])
            actor = str(state['current_member_id'])
            world = json.loads((Path(__file__).parents[1] / 'static/conquest/world.json').read_text(encoding='utf-8'))
            selected = [key for key, value in world['cardSymbols'].items() if value == 'infantry'][:3]
            extra = [key for key, value in world['cardSymbols'].items() if value == 'cavalry'][:2]
            state['hands'][actor] = selected + extra
            state['card_deck'] = [key for key in state['card_deck'] if key not in selected + extra]
            state['territories'][selected[0]]['owner'] = state['current_member_id']
            before_armies = state['territories'][selected[0]]['armies']
            before_reserve = state['remaining']
            db.execute('UPDATE conquest_lobbies SET state_json=? WHERE id=?', (json.dumps(state), lobby_id)); db.commit()
        self.assertEqual(self.action(lobby_id, 'place', to=selected[0], count=1).status_code, 400)
        client, token = self.clients[0]
        before = client.get(f'/karten/welteroberung/{lobby_id}/status').get_json()
        body = {'csrf_token': token, 'revision': before['revision'], 'action': 'trade',
                'cards': json.dumps(selected), 'bonus_territory': selected[0]}
        result = client.post(f'/karten/welteroberung/{lobby_id}/aktion', data=body)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.get_json()['result']['units'], 4)
        self.assertEqual(client.post(f'/karten/welteroberung/{lobby_id}/aktion', data=body).status_code, 409)
        client.get(f'/karten/welteroberung/{lobby_id}')
        saved = client.get(f'/karten/welteroberung/{lobby_id}/status').get_json()['game']
        self.assertEqual(saved['remaining'], before_reserve + 4)
        self.assertEqual(saved['territories'][selected[0]]['armies'], before_armies + 2)
        self.assertEqual(len(saved['inventory']['territory_cards']), 2)
        self.assertEqual(saved['trade']['next_value'], 6)


if __name__ == "__main__":
    unittest.main()
