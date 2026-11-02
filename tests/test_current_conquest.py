"""The current preview entry follows saved lobbies, never starts a new round."""
import importlib.util
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".deps"))
from flask import Flask

SPEC = importlib.util.spec_from_file_location("current_conquest", ROOT / "deploy/run_current_conquest.py")
preview = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(preview)


class CurrentConquestTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.executescript("""CREATE TABLE conquest_lobbies(id INTEGER,status TEXT);
            CREATE TABLE conquest_members(lobby_id INTEGER,user_id INTEGER,status TEXT);
            INSERT INTO conquest_lobbies VALUES(3,'completed'),(6,'playing'),(7,'playing');
            INSERT INTO conquest_members VALUES(3,6,'active'),(6,6,'active'),(7,99,'active');""")

    def tearDown(self):
        self.db.close()

    def test_latest_own_game_selected_without_modifying_memberships(self):
        changes = self.db.total_changes
        self.assertEqual(preview.current_room(self.db, 6), "/karten/welteroberung/6")
        self.assertEqual(self.db.total_changes, changes)

    def test_waiting_rematch_opens_lobby_and_departed_membership_is_ignored(self):
        self.db.executescript("""INSERT INTO conquest_lobbies VALUES(8,'waiting'),(9,'playing');
            INSERT INTO conquest_members VALUES(8,6,'active'),(9,6,'left');""")
        self.assertEqual(preview.current_room(self.db, 6), "/karten/welteroberung/8/lobby")

    def test_missing_save_cannot_generate_data(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "runtime") as directory:
            data = Path(directory)
            with self.assertRaisesRegex(RuntimeError, "keine neue Partie"):
                preview.saved_cases(data)
            self.assertEqual(list(data.iterdir()), [])

    def test_fresh_browser_opens_current_game_as_existing_local_player(self):
        app = Flask(__name__)
        app.secret_key = "test-only"
        app.get_db = lambda: self.db
        preview.register_entries(app, {"four": {"users": [6,7,8,9], "room": "/karten/welteroberung/3"}})
        changes = self.db.total_changes
        with app.test_client() as client:
            response = client.get("/local/current")
            self.assertEqual(response.location, "/karten/welteroberung/6")
            with client.session_transaction() as session:
                self.assertEqual(session["user_id"], 6)
                self.assertEqual(session["csrf_token"], "portrait-test")
            response = client.get("/test/four/1")
            self.assertEqual(response.status_code, 302)
            with client.session_transaction() as session:
                self.assertEqual(session["user_id"], 7)
            self.assertEqual(client.get("/test/four/99").status_code, 404)
        self.assertEqual(self.db.total_changes, changes)


if __name__ == "__main__":
    unittest.main()
