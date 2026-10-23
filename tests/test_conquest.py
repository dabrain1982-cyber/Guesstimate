import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

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
        self.assertIn('value="fantasy" selected', page)
        self.assertIn('value="farbenfroh" selected', page)

    def test_start_builds_complete_private_mission_game_state(self):
        lobby_id = self.create_lobby()
        self.clients[1][0].post(
            f"/karten/welteroberung/{lobby_id}/beitreten",
            data={"csrf_token": self.clients[1][1]},
        )
        response = self.clients[0][0].post(
            f"/karten/welteroberung/{lobby_id}/starten",
            data={"csrf_token": self.clients[0][1]},
        )
        self.assertEqual(response.status_code, 302)
        page = self.clients[0][0].get(response.headers["Location"]).get_data(as_text=True)
        self.assertIn("PHASE 1 · VERSTÄRKEN", page)
        self.assertIn("Deine geheime Mission", page)
        self.assertIn("conquest/boards/welt-klassisch.webp", page)
        status = self.clients[0][0].get(f"/karten/welteroberung/{lobby_id}/status").get_json()
        self.assertEqual(status["status"], "playing")
        self.assertEqual(len(status["game"]["territories"]), 42)
        self.assertTrue(status["game"]["own_mission"].startswith("mission-"))
        self.assertIn("neutral", {str(item["owner"]) for item in status["game"]["territories"].values()})
        with self.app.app_context():
            stored = json.loads(self.app.get_db().execute("SELECT state_json FROM conquest_lobbies WHERE id = ?", (lobby_id,)).fetchone()[0])
            self.assertEqual(sum(item["armies"] for item in stored["territories"].values()), 120)

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


if __name__ == "__main__":
    unittest.main()
