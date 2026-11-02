import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from flask import render_template, session

from app import create_app
from dice_table import _score_kniffel


class DiceTableLobbyTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "dice-table-test",
                "CARD_TABLE_ENABLED": True,
                "DATABASE": str(Path(self.tempdir.name) / "test.sqlite3"),
            }
        )
        self.clients = []
        with self.app.app_context():
            database = self.app.get_db()
            for index, name in enumerate(("Host", "Gast"), 1):
                user_id = database.execute(
                    """
                    INSERT INTO users (username, display_name, pin_hash, created_at)
                    VALUES (?, ?, 'unused', ?)
                    """,
                    (name.casefold(), name, datetime.now().isoformat()),
                ).lastrowid
                client = self.app.test_client()
                token = f"dice-token-{index}"
                with client.session_transaction() as player_session:
                    player_session["user_id"] = user_id
                    player_session["csrf_token"] = token
                    player_session["login_recorded_on"] = datetime.now().date().isoformat()
                self.clients.append((client, token))
            database.commit()

    def tearDown(self):
        self.tempdir.cleanup()

    def create_lobby(self):
        host, token = self.clients[0]
        response = host.post(
            "/karten/wuerfeltisch/erstellen", data={"csrf_token": token}
        )
        self.assertEqual(response.status_code, 302)
        return int(response.headers["Location"].rstrip("/").split("/")[-1])

    def test_tabletop_dice_family_tile_is_clickable(self):
        page = self.clients[0][0].get("/karten").get_data(as_text=True)
        self.assertEqual(page.count('class="tabletop-game-tile'), 3)
        self.assertIn('href="/karten/wuerfeltische"', page)
        self.assertNotIn('href="/karten/wuerfeltisch"', page)

        dice_page = self.clients[0][0].get("/karten/wuerfeltische").get_data(as_text=True)
        self.assertIn('href="/karten/wuerfeltisch"', dice_page)
        self.assertIn('href="/karten/maexchen"', dice_page)
        self.assertIn("schweinchen", dice_page)
        self.assertIn('href="/karten/kniffel"', dice_page)

    def test_maexchen_private_roll_challenge_and_double_life_loss(self):
        host, host_token = self.clients[0]
        guest, guest_token = self.clients[1]
        created = host.post("/karten/maexchen/erstellen", data={"csrf_token": host_token})
        lobby_id = int(created.headers["Location"].rstrip("/").split("/")[-1])
        guest.post(
            f"/karten/maexchen/{lobby_id}/beitreten",
            data={"csrf_token": guest_token},
        )
        waiting = host.get(f"/karten/maexchen/{lobby_id}").get_data(as_text=True)
        self.assertIn("spiel starten", waiting)
        self.assertIn("3", waiting)
        host.post(
            f"/karten/maexchen/{lobby_id}/starten",
            data={"csrf_token": host_token},
        )
        game_page = host.get(f"/karten/maexchen/{lobby_id}").get_data(as_text=True)
        self.assertIn('data-game-mode="maexchen"', game_page)
        self.assertIn("maexchen-logo-v1.svg", game_page)
        self.assertIn('mäxchen glauben · 1 leben', game_page)
        self.assertIn("Spielregeln", game_page)

        host.post(
            f"/karten/wuerfeltisch/{lobby_id}/aktion",
            data={"csrf_token": host_token, "action": "roll"},
        )
        host_state = host.get(f"/karten/wuerfeltisch/{lobby_id}/status").get_json()
        guest_state = guest.get(f"/karten/wuerfeltisch/{lobby_id}/status").get_json()
        self.assertTrue(all(die["value"] is not None for die in host_state["dice"]))
        self.assertTrue(all(die["value"] is None for die in guest_state["dice"]))
        self.assertEqual(host_state["maexchen"]["phase"], "awaiting_claim")

        with self.app.app_context():
            database = self.app.get_db()
            row = database.execute(
                "SELECT state_json FROM dice_table_lobbies WHERE id = ?", (lobby_id,)
            ).fetchone()
            state = json.loads(row["state_json"])
            state["dice"][0]["value"] = 2
            state["dice"][1]["value"] = 1
            database.execute(
                "UPDATE dice_table_lobbies SET state_json = ? WHERE id = ?",
                (json.dumps(state), lobby_id),
            )
            database.commit()

        claimed = host.post(
            f"/karten/wuerfeltisch/{lobby_id}/aktion",
            data={"csrf_token": host_token, "action": "claim", "claim": "21"},
        )
        self.assertEqual(claimed.status_code, 200)
        revealed = guest.post(
            f"/karten/wuerfeltisch/{lobby_id}/aktion",
            data={"csrf_token": guest_token, "action": "reveal"},
        )
        self.assertEqual(revealed.status_code, 200)
        public_host = host.get(f"/karten/wuerfeltisch/{lobby_id}/status").get_json()
        public_guest = guest.get(f"/karten/wuerfeltisch/{lobby_id}/status").get_json()
        self.assertEqual([die["value"] for die in public_host["dice"]], [2, 1])
        self.assertEqual([die["value"] for die in public_guest["dice"]], [2, 1])
        guest_player = next(
            player for player in public_guest["maexchen"]["players"] if player["name"] == "Gast"
        )
        self.assertEqual(guest_player["lives"], 1)
        self.assertTrue(guest_player["swimming"])
        self.assertEqual(public_guest["maexchen"]["current_member_id"], public_guest["members"][1]["id"])

    def test_maexchen_believed_max_costs_one_life_and_gives_lead(self):
        host, host_token = self.clients[0]
        guest, guest_token = self.clients[1]
        created = host.post("/karten/maexchen/erstellen", data={"csrf_token": host_token})
        lobby_id = int(created.headers["Location"].rstrip("/").split("/")[-1])
        guest.post(f"/karten/maexchen/{lobby_id}/beitreten", data={"csrf_token": guest_token})
        host.post(f"/karten/maexchen/{lobby_id}/starten", data={"csrf_token": host_token})
        host.post(f"/karten/wuerfeltisch/{lobby_id}/aktion", data={"csrf_token": host_token, "action": "roll"})
        host.post(
            f"/karten/wuerfeltisch/{lobby_id}/aktion",
            data={"csrf_token": host_token, "action": "claim", "claim": "21"},
        )
        accepted = guest.post(
            f"/karten/wuerfeltisch/{lobby_id}/aktion",
            data={"csrf_token": guest_token, "action": "believe_maexchen"},
        )
        self.assertEqual(accepted.status_code, 200)
        state = guest.get(f"/karten/wuerfeltisch/{lobby_id}/status").get_json()
        guest_player = next(player for player in state["maexchen"]["players"] if player["name"] == "Gast")
        self.assertEqual(guest_player["lives"], 2)
        self.assertEqual(state["maexchen"]["current_member_id"], state["members"][1]["id"])
        self.assertEqual(state["maexchen"]["round_result"]["loss"], 1)
        self.assertIsNone(state["roll"])

    def test_maexchen_requires_a_strictly_higher_claim(self):
        host, host_token = self.clients[0]
        guest, guest_token = self.clients[1]
        created = host.post("/karten/maexchen/erstellen", data={"csrf_token": host_token})
        lobby_id = int(created.headers["Location"].rstrip("/").split("/")[-1])
        guest.post(f"/karten/maexchen/{lobby_id}/beitreten", data={"csrf_token": guest_token})
        host.post(f"/karten/maexchen/{lobby_id}/starten", data={"csrf_token": host_token})
        host.post(f"/karten/wuerfeltisch/{lobby_id}/aktion", data={"csrf_token": host_token, "action": "roll"})
        host.post(
            f"/karten/wuerfeltisch/{lobby_id}/aktion",
            data={"csrf_token": host_token, "action": "claim", "claim": "43"},
        )
        guest.post(
            f"/karten/wuerfeltisch/{lobby_id}/aktion",
            data={"csrf_token": guest_token, "action": "believe"},
        )
        guest.post(f"/karten/wuerfeltisch/{lobby_id}/aktion", data={"csrf_token": guest_token, "action": "roll"})
        equal = guest.post(
            f"/karten/wuerfeltisch/{lobby_id}/aktion",
            data={"csrf_token": guest_token, "action": "claim", "claim": "43"},
        )
        higher = guest.post(
            f"/karten/wuerfeltisch/{lobby_id}/aktion",
            data={"csrf_token": guest_token, "action": "claim", "claim": "51"},
        )
        self.assertEqual(equal.status_code, 409)
        self.assertEqual(higher.status_code, 200)

    def test_old_process_without_kniffel_route_keeps_tabletop_connection_available(self):
        old_flag = self.app.config.pop("KNIFFEL_AVAILABLE", None)
        family_flag = self.app.config.pop("TABLETOP_FAMILY_HUBS_AVAILABLE", None)
        try:
            page_response = self.clients[0][0].get("/karten")
            self.assertEqual(page_response.status_code, 200)
            page = page_response.get_data(as_text=True)
            self.assertNotIn('href="/karten/kniffel"', page)
            self.assertNotIn('href="/karten/wuerfeltisch"', page)
            self.assertIn('href="/karten/wuerfeltische"', page)
        finally:
            if old_flag is not None:
                self.app.config["KNIFFEL_AVAILABLE"] = old_flag
            if family_flag is not None:
                self.app.config["TABLETOP_FAMILY_HUBS_AVAILABLE"] = family_flag

    def test_old_process_can_render_dice_browser_without_new_template_context(self):
        with self.app.test_request_context("/karten/wuerfeltisch"):
            session["user_id"] = 1
            session["csrf_token"] = "old-process-token"
            self.app.preprocess_request()
            page = render_template("dice_table_index.html", lobbies=[])
        self.assertIn("würfeltisch", page)
        self.assertIn('action="/karten/wuerfeltisch/erstellen"', page)
        self.assertIn(
            '<a class="secondary-button lobby-browser-back" href="/karten/wuerfeltische">zurück zu würfeltischen</a>',
            page,
        )

    def test_create_and_join_lobby_render_canonical_profile_windows(self):
        host, host_token = self.clients[0]
        lobby_id = self.create_lobby()

        guest, guest_token = self.clients[1]
        browser = guest.get("/karten/wuerfeltisch").get_data(as_text=True)
        self.assertIn("Host´s Würfeltisch", browser)
        self.assertIn("beitreten", browser)
        guest.post(
            f"/karten/wuerfeltisch/{lobby_id}/beitreten",
            data={"csrf_token": guest_token},
        )

        room = host.get(f"/karten/wuerfeltisch/{lobby_id}").get_data(as_text=True)
        self.assertEqual(room.count("variant-a-profile-canonical"), 2)
        self.assertIn("Host", room)
        self.assertIn("Gast", room)
        self.assertIn("Anzahl der Würfel", room)
        self.assertIn('spiel starten', room)
        with host.get("/static/dice-table.css") as response:
            stylesheet = response.get_data(as_text=True)
        self.assertIn("dice-table-background-v2.png", stylesheet)

        state = host.get(f"/karten/wuerfeltisch/{lobby_id}/status").get_json()
        self.assertEqual([member["name"] for member in state["members"]], ["Host", "Gast"])

    def test_host_can_configure_and_start_the_table(self):
        host, token = self.clients[0]
        lobby_id = self.create_lobby()
        response = host.post(
            f"/karten/wuerfeltisch/{lobby_id}/einstellungen",
            data={"csrf_token": token, "dice_count": "5", "use_cup": "1"},
        )
        self.assertEqual(response.status_code, 302)
        response = host.post(
            f"/karten/wuerfeltisch/{lobby_id}/starten",
            data={"csrf_token": token, "dice_count": "5", "use_cup": "1"},
        )
        self.assertEqual(response.status_code, 302)
        game = host.get(f"/karten/wuerfeltisch/{lobby_id}").get_data(as_text=True)
        self.assertIn("data-dice-room", game)
        self.assertIn("vendor/dddice-0.21.8.js", game)
        self.assertIn("vendor/dddice-outgunned/theme.json", game)
        self.assertIn("vendor/dddice-outgunned/", game)
        self.assertIn("outgunned-reimagined-ma8o1nit", game)
        self.assertIn("65d8ad5d-ed69-4c48-8ac6-8ff0a1636979", game)
        self.assertIn('data-dice-count="5"', game)
        self.assertIn('data-hidden-roll="1"', game)
        self.assertIn("verdecktes Würfeln", game)
        self.assertIn("Kamera fixieren", game)

        with host.get("/static/dice-table.js") as response:
            script = response.get_data(as_text=True)
        self.assertIn("localizeThemeAssets", script)
        self.assertIn("guesstimate-player-${memberId}", script)
        self.assertIn("call % 5 === 0", script)
        self.assertIn("savedCamera?.position || { x: 5, y: 18, z: 26 }", script)
        self.assertIn("quaternion: null", script)
        self.assertNotIn('fetch("https://dddice.com', script)

    def test_hidden_roll_stays_private_to_roller_and_is_written_to_note(self):
        host, host_token = self.clients[0]
        guest, guest_token = self.clients[1]
        lobby_id = self.create_lobby()
        guest.post(
            f"/karten/wuerfeltisch/{lobby_id}/beitreten",
            data={"csrf_token": guest_token},
        )
        host.post(
            f"/karten/wuerfeltisch/{lobby_id}/starten",
            data={"csrf_token": host_token, "dice_count": "3", "use_cup": "1"},
        )
        roll_response = host.post(
            f"/karten/wuerfeltisch/{lobby_id}/aktion",
            data={"csrf_token": host_token, "action": "roll"},
        )
        self.assertEqual(roll_response.status_code, 200)

        host_state = host.get(f"/karten/wuerfeltisch/{lobby_id}/status").get_json()
        guest_state = guest.get(f"/karten/wuerfeltisch/{lobby_id}/status").get_json()
        self.assertEqual(len(host_state["dice"]), 3)
        self.assertTrue(all(die["value"] is not None for die in host_state["dice"]))
        self.assertEqual(host_state["roll"]["phase"], "covered")
        self.assertTrue(all(die["value"] is None for die in guest_state["dice"]))
        self.assertIsNotNone(host_state["history"][0]["rolls"][0]["values"])
        self.assertIsNone(guest_state["history"][0]["rolls"][0]["values"])

        reveal_response = host.post(
            f"/karten/wuerfeltisch/{lobby_id}/aktion",
            data={"csrf_token": host_token, "action": "reveal"},
        )
        self.assertEqual(reveal_response.status_code, 200)
        self.assertTrue(host.get(f"/karten/wuerfeltisch/{lobby_id}/status").get_json()["roll"]["visible"])
        self.assertFalse(guest.get(f"/karten/wuerfeltisch/{lobby_id}/status").get_json()["roll"]["visible"])

    def test_open_roll_is_shared_and_can_be_collected_by_roller(self):
        host, token = self.clients[0]
        lobby_id = self.create_lobby()
        host.post(
            f"/karten/wuerfeltisch/{lobby_id}/starten",
            data={"csrf_token": token, "dice_count": "2", "use_cup": "0"},
        )
        host.post(
            f"/karten/wuerfeltisch/{lobby_id}/aktion",
            data={"csrf_token": token, "action": "roll"},
        )
        state = host.get(f"/karten/wuerfeltisch/{lobby_id}/status").get_json()
        self.assertEqual(len(state["dice"]), 2)
        self.assertTrue(state["roll"]["visible"])
        collected = host.post(
            f"/karten/wuerfeltisch/{lobby_id}/aktion",
            data={"csrf_token": token, "action": "collect"},
        )
        self.assertEqual(collected.status_code, 200)
        collected_state = host.get(f"/karten/wuerfeltisch/{lobby_id}/status").get_json()
        self.assertIsNotNone(collected_state["roll"])
        self.assertTrue(all(die["zone"] == "tray" for die in collected_state["dice"]))

    def test_selected_dice_are_rerolled_and_unselected_dice_move_to_held_zone(self):
        host, token = self.clients[0]
        lobby_id = self.create_lobby()
        host.post(
            f"/karten/wuerfeltisch/{lobby_id}/starten",
            data={"csrf_token": token, "dice_count": "5", "use_cup": "0"},
        )
        host.post(
            f"/karten/wuerfeltisch/{lobby_id}/aktion",
            data={"csrf_token": token, "action": "roll"},
        )
        first = host.get(f"/karten/wuerfeltisch/{lobby_id}/status").get_json()
        self.assertEqual([die["zone"] for die in first["dice"]], ["active"] * 5)

        for die in first["dice"][:3]:
            response = host.post(
                f"/karten/wuerfeltisch/{lobby_id}/aktion",
                data={"csrf_token": token, "action": "toggle", "die_id": die["id"]},
            )
            self.assertEqual(response.status_code, 200)
        selected = host.get(f"/karten/wuerfeltisch/{lobby_id}/status").get_json()
        self.assertEqual(sum(die["zone"] == "tray" for die in selected["dice"]), 3)

        host.post(
            f"/karten/wuerfeltisch/{lobby_id}/aktion",
            data={"csrf_token": token, "action": "roll"},
        )
        second = host.get(f"/karten/wuerfeltisch/{lobby_id}/status").get_json()
        self.assertEqual(sum(die["zone"] == "held" for die in second["dice"]), 2)
        self.assertEqual(sum(die["zone"] == "active" for die in second["dice"]), 3)
        self.assertEqual(len(second["roll"]["rolled_ids"]), 3)

        active_die = next(die for die in second["dice"] if die["zone"] == "active")
        host.post(
            f"/karten/wuerfeltisch/{lobby_id}/aktion",
            data={"csrf_token": token, "action": "toggle", "die_id": active_die["id"]},
        )
        host.post(
            f"/karten/wuerfeltisch/{lobby_id}/aktion",
            data={"csrf_token": token, "action": "roll"},
        )
        third = host.get(f"/karten/wuerfeltisch/{lobby_id}/status").get_json()
        self.assertEqual(sum(die["zone"] == "held" for die in third["dice"]), 4)
        self.assertEqual(sum(die["zone"] == "active" for die in third["dice"]), 1)
        self.assertEqual(len(third["roll"]["rolled_ids"]), 1)

        host.post(
            f"/karten/wuerfeltisch/{lobby_id}/aktion",
            data={"csrf_token": token, "action": "collect"},
        )
        tray = host.get(f"/karten/wuerfeltisch/{lobby_id}/status").get_json()
        self.assertTrue(all(die["zone"] == "tray" for die in tray["dice"]))
        formerly_held = tray["dice"][0]
        host.post(
            f"/karten/wuerfeltisch/{lobby_id}/aktion",
            data={"csrf_token": token, "action": "toggle", "die_id": formerly_held["id"]},
        )
        returned = host.get(f"/karten/wuerfeltisch/{lobby_id}/status").get_json()
        returned_die = next(die for die in returned["dice"] if die["id"] == formerly_held["id"])
        self.assertEqual(returned_die["zone"], "active")
        host.post(
            f"/karten/wuerfeltisch/{lobby_id}/aktion",
            data={"csrf_token": token, "action": "toggle", "die_id": formerly_held["id"]},
        )
        host.post(
            f"/karten/wuerfeltisch/{lobby_id}/aktion",
            data={"csrf_token": token, "action": "roll"},
        )
        reset = host.get(f"/karten/wuerfeltisch/{lobby_id}/status").get_json()
        self.assertEqual([die["zone"] for die in reset["dice"]], ["active"] * 5)

    def test_camera_lock_is_saved_only_for_the_current_account(self):
        host, token = self.clients[0]
        camera = {
            "position": {"x": 5.25, "y": 18, "z": 26},
            "target": {"x": 0, "y": 0, "z": 0},
        }
        response = host.post(
            "/karten/wuerfeltisch/kamera",
            data={"csrf_token": token, "locked": "1", "camera": json.dumps(camera)},
        )
        self.assertEqual(response.status_code, 200)
        lobby_id = self.create_lobby()
        host.post(
            f"/karten/wuerfeltisch/{lobby_id}/starten",
            data={"csrf_token": token, "dice_count": "2", "use_cup": "0"},
        )
        game = host.get(f"/karten/wuerfeltisch/{lobby_id}").get_data(as_text=True)
        self.assertIn('data-camera-locked="1"', game)
        self.assertIn("5.25", game)

        guest, guest_token = self.clients[1]
        invalid = guest.post(
            "/karten/wuerfeltisch/kamera",
            data={
                "csrf_token": guest_token,
                "locked": "1",
                "camera": '{"position":{"x":999,"y":0,"z":0},"target":{"x":0,"y":0,"z":0}}',
            },
        )
        self.assertEqual(invalid.status_code, 400)
        with self.app.app_context():
            row = self.app.get_db().execute(
                "SELECT camera_locked FROM dice_table_preferences WHERE user_id = 2"
            ).fetchone()
            self.assertIsNone(row)

    def test_kniffel_uses_own_lobby_and_dynamic_score_columns(self):
        host, host_token = self.clients[0]
        guest, guest_token = self.clients[1]
        response = host.post("/karten/kniffel/erstellen", data={"csrf_token": host_token})
        self.assertEqual(response.status_code, 302)
        lobby_id = int(response.headers["Location"].rstrip("/").split("/")[-1])
        self.assertIn("/karten/kniffel/", response.headers["Location"])
        guest.post(
            f"/karten/kniffel/{lobby_id}/beitreten",
            data={"csrf_token": guest_token},
        )
        waiting = host.get(f"/karten/kniffel/{lobby_id}").get_data(as_text=True)
        self.assertIn("spiel starten", waiting)
        self.assertIn("5", waiting)
        self.assertIn("3", waiting)

        host.post(
            f"/karten/kniffel/{lobby_id}/starten",
            data={"csrf_token": host_token},
        )
        game = host.get(f"/karten/kniffel/{lobby_id}").get_data(as_text=True)
        self.assertIn('data-game-mode="kniffel"', game)
        self.assertIn("data-kniffel-sheet", game)
        self.assertIn("data-kniffel-lights", game)
        self.assertLess(game.index("is-kniffel-sheet"), game.index("is-kniffel-console"))
        with host.get("/static/dice-table.css") as response:
            stylesheet = response.get_data(as_text=True)
        self.assertIn("width: 720px", stylesheet)
        self.assertIn("bottom: 22px", stylesheet)
        self.assertIn("left: 92px", stylesheet)
        self.assertIn("repeating-linear-gradient(7deg", stylesheet)
        state = host.get(f"/karten/wuerfeltisch/{lobby_id}/status").get_json()
        self.assertEqual(state["game_mode"], "kniffel")
        self.assertEqual([card["name"] for card in state["kniffel"]["scorecards"]], ["Host", "Gast"])
        self.assertEqual(state["kniffel"]["rolls_left"], 3)

        standard_browser = host.get("/karten/wuerfeltisch").get_data(as_text=True)
        self.assertNotIn("Host´s Kniffeltisch", standard_browser)

    def test_kniffel_allows_three_rolls_then_scores_and_changes_player(self):
        host, host_token = self.clients[0]
        guest, guest_token = self.clients[1]
        create = host.post("/karten/kniffel/erstellen", data={"csrf_token": host_token})
        lobby_id = int(create.headers["Location"].rstrip("/").split("/")[-1])
        guest.post(
            f"/karten/kniffel/{lobby_id}/beitreten",
            data={"csrf_token": guest_token},
        )
        host.post(
            f"/karten/kniffel/{lobby_id}/starten",
            data={"csrf_token": host_token},
        )

        blocked_guest = guest.post(
            f"/karten/wuerfeltisch/{lobby_id}/aktion",
            data={"csrf_token": guest_token, "action": "roll"},
        )
        self.assertEqual(blocked_guest.status_code, 409)
        for expected_left in (2, 1, 0):
            response = host.post(
                f"/karten/wuerfeltisch/{lobby_id}/aktion",
                data={"csrf_token": host_token, "action": "roll"},
            )
            self.assertEqual(response.status_code, 200)
            state = host.get(f"/karten/wuerfeltisch/{lobby_id}/status").get_json()
            self.assertEqual(state["kniffel"]["rolls_left"], expected_left)
        fourth = host.post(
            f"/karten/wuerfeltisch/{lobby_id}/aktion",
            data={"csrf_token": host_token, "action": "roll"},
        )
        self.assertEqual(fourth.status_code, 409)

        before_score = host.get(f"/karten/wuerfeltisch/{lobby_id}/status").get_json()
        expected_chance = sum(die["value"] for die in before_score["dice"])
        scored = host.post(
            f"/karten/wuerfeltisch/{lobby_id}/aktion",
            data={"csrf_token": host_token, "action": "score", "category": "chance"},
        )
        self.assertEqual(scored.status_code, 200)
        after_score = host.get(f"/karten/wuerfeltisch/{lobby_id}/status").get_json()
        self.assertIsNone(after_score["roll"])
        self.assertEqual(after_score["dice"], [])
        self.assertEqual(after_score["kniffel"]["scorecards"][0]["scores"]["chance"], expected_chance)
        self.assertEqual(after_score["kniffel"]["current_member_id"], after_score["members"][1]["id"])
        self.assertEqual(after_score["kniffel"]["rolls_left"], 3)

    def test_dice_zone_animation_is_not_restarted_by_every_status_poll(self):
        with self.clients[0][0].get("/static/dice-table.js") as response:
            script = response.get_data(as_text=True)
        self.assertIn("nextSignature !== zoneSignature", script)
        self.assertIn("nextSignature === concealedSignature", script)
        self.assertIn("state.revision) < latestRevision", script)
        self.assertIn('appendSection("Zweiter Teil")', script)
        self.assertIn('appendTotal("Endsumme"', script)

    def test_kniffel_scoring_matches_the_standard_categories(self):
        values = [3, 3, 3, 4, 5]
        self.assertEqual(_score_kniffel("threes", values), 9)
        self.assertEqual(_score_kniffel("fours", values), 4)
        self.assertEqual(_score_kniffel("three_kind", values), 18)
        self.assertEqual(_score_kniffel("four_kind", values), 0)
        self.assertEqual(_score_kniffel("chance", values), 18)
        self.assertEqual(_score_kniffel("full_house", [2, 2, 5, 5, 5]), 25)
        self.assertEqual(_score_kniffel("small_straight", [1, 2, 3, 4, 6]), 30)
        self.assertEqual(_score_kniffel("large_straight", [2, 3, 4, 5, 6]), 40)
        self.assertEqual(_score_kniffel("five_kind", [6, 6, 6, 6, 6]), 50)


if __name__ == "__main__":
    unittest.main()
