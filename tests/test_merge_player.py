import sqlite3
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from app import create_app
from deploy.merge_player import inspect_merge, merge
from werkzeug.security import check_password_hash, generate_password_hash


class MergePlayerTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.database_path = str(Path(self.tempdir.name) / "quiz.sqlite3")
        self.app = create_app({"TESTING": True, "DATABASE": self.database_path})

    def tearDown(self):
        self.tempdir.cleanup()

    def test_different_days_are_merged_and_source_is_deleted(self):
        with self.app.app_context():
            db = self.app.get_db()
            now = datetime.now().isoformat()
            db.executemany(
                "INSERT INTO users (username, display_name, pin_hash, created_at) VALUES (?, ?, ?, ?)",
                [
                    ("pearlyde", "Pearlyde", generate_password_hash("old"), now),
                    ("pearlyde1", "Pearlyde1", generate_password_hash("other"), now),
                ],
            )
            users = db.execute("SELECT * FROM users ORDER BY id").fetchall()
            for index, (day, score) in enumerate((("2026-10-01", 220), ("2026-10-02", 330)), 1):
                round_id = db.execute(
                    "INSERT INTO daily_rounds (round_date, questions_json, created_at) VALUES (?, '[]', ?)",
                    (day, now),
                ).lastrowid
                db.execute(
                    """
                    INSERT INTO attempts (user_id, round_id, status, score, started_at, completed_at)
                    VALUES (?, ?, 'completed', ?, ?, ?)
                    """,
                    (users[index - 1]["id"], round_id, score, now, now),
                )
            db.commit()

        plan = inspect_merge(self.database_path, "Pearlyde", "Pearlyde1")
        self.assertEqual(plan["target_points"], 220)
        self.assertEqual(plan["source_points"], 330)
        result = merge(self.database_path, "Pearlyde", "Pearlyde1", "1234")
        self.assertEqual(result["transferred_points"], 330)
        self.assertEqual(result["total_points"], 550)
        db = sqlite3.connect(self.database_path)
        db.row_factory = sqlite3.Row
        rows = db.execute("SELECT * FROM users").fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["display_name"], "Pearlyde")
        self.assertTrue(check_password_hash(rows[0]["pin_hash"], "1234"))
        self.assertEqual(
            db.execute("SELECT COUNT(DISTINCT user_id) FROM attempts").fetchone()[0], 1
        )
        db.close()

    def test_same_day_overlap_aborts_without_changing_accounts(self):
        with self.app.app_context():
            db = self.app.get_db()
            now = datetime.now().isoformat()
            db.executemany(
                "INSERT INTO users (username, display_name, pin_hash, created_at) VALUES (?, ?, ?, ?)",
                [
                    ("pearlyde", "Pearlyde", generate_password_hash("old"), now),
                    ("pearlyde1", "Pearlyde1", generate_password_hash("other"), now),
                ],
            )
            users = db.execute("SELECT * FROM users ORDER BY id").fetchall()
            round_id = db.execute(
                "INSERT INTO daily_rounds (round_date, questions_json, created_at) VALUES ('2026-10-02', '[]', ?)",
                (now,),
            ).lastrowid
            db.executemany(
                """
                INSERT INTO attempts (user_id, round_id, status, score, started_at, completed_at)
                VALUES (?, ?, 'completed', ?, ?, ?)
                """,
                [(users[0]["id"], round_id, 200, now, now), (users[1]["id"], round_id, 300, now, now)],
            )
            db.commit()

        with self.assertRaises(RuntimeError):
            inspect_merge(self.database_path, "Pearlyde", "Pearlyde1")
        with self.assertRaises(RuntimeError):
            merge(self.database_path, "Pearlyde", "Pearlyde1", "1234")
        db = sqlite3.connect(self.database_path)
        self.assertEqual(db.execute("SELECT COUNT(*) FROM users").fetchone()[0], 2)
        self.assertEqual(db.execute("SELECT COUNT(*) FROM attempts").fetchone()[0], 2)
        db.close()


if __name__ == "__main__":
    unittest.main()
