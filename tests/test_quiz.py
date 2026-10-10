import json
import re
import sqlite3
import tempfile
import unittest
from datetime import date, datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from markupsafe import escape

from app import (
    create_app,
    daily_questions,
    estimate_points,
    evaluate,
    get_or_create_round,
    match_option_order,
    missed_current_week_dates,
    order_credit,
    partial_credit,
    question_fingerprint,
    question_time_factor,
    question_subject_keys,
    reserve_question_sets,
    send_pool_exhausted_email,
    timed_question_points,
)
from deploy.reset_game import reset
from deploy.validate_question_library import validate_library
from questions import (
    KNOWLEDGE_CATEGORY_DEFINITIONS,
    KNOWLEDGE_CATEGORY_LABELS,
    QUESTION_BANK,
    QUESTION_LIBRARY_ROOT,
    QUESTION_TYPE_DEFINITIONS,
)


class ScoringTests(unittest.TestCase):
    def test_question_library_uses_question_types_without_category_quotas(self):
        for question_type, questions in QUESTION_BANK.items():
            self.assertTrue(questions, question_type)
            for question in questions:
                self.assertEqual(question["question_type"], question_type)
                for required in ("id", "prompt", "answer", "explanation", "source"):
                    self.assertIn(required, question)

    def test_complete_question_library_matches_the_required_profiles(self):
        self.assertEqual(validate_library(), [])

    def test_true_false_questions_have_no_category_fields(self):
        forbidden = {"primary_category", "knowledge_category", "subtopic", "topics", "tags"}
        for question in QUESTION_BANK["true_false"]:
            self.assertFalse(forbidden & question.keys(), question["id"])
            self.assertIsInstance(question["answer"], bool, question["id"])

    def test_non_true_false_categories_are_present_and_valid(self):
        for question_type, questions in QUESTION_BANK.items():
            if question_type == "true_false":
                continue
            for question in questions:
                self.assertIn(question["knowledge_category"], KNOWLEDGE_CATEGORY_LABELS)
                self.assertTrue(question["subtopic"], question["id"])
                self.assertEqual(
                    set(question["tags"]),
                    {"topics", "entities", "genres", "regions", "eras"},
                    question["id"],
                )

    def test_every_new_question_has_a_verified_https_source(self):
        new_questions = [
            question
            for questions in QUESTION_BANK.values()
            for question in questions
            if int(re.search(r"\d+", question["id"]).group()) >= 151
        ]
        self.assertTrue(new_questions)
        for question in new_questions:
            self.assertEqual(question["source"]["status"], "verified", question["id"])
            self.assertRegex(question["source"]["verified_on"], r"^\d{4}-\d{2}-\d{2}$")
            references = question["source"]["references"]
            self.assertTrue(references, question["id"])
            self.assertTrue(
                all(reference["url"].startswith("https://") for reference in references),
                question["id"],
            )

    def test_physical_library_is_flat_by_question_type(self):
        for question_type, definition in QUESTION_TYPE_DEFINITIONS.items():
            path = QUESTION_LIBRARY_ROOT / definition["directory"] / "fragen.json"
            self.assertTrue(path.is_file(), path)
            questions = json.loads(path.read_text(encoding="utf-8"))
            if question_type in ("word_scramble", "binary_sort"):
                self.assertFalse(definition["active"])
                self.assertEqual(questions, [])
            else:
                self.assertTrue(questions)

    def test_physical_library_reserves_both_future_question_types(self):
        for question_type in ("word_scramble", "binary_sort"):
            definition = QUESTION_TYPE_DEFINITIONS[question_type]
            self.assertFalse(definition["active"])
            path = QUESTION_LIBRARY_ROOT / definition["directory"] / "fragen.json"
            self.assertTrue(path.is_file(), path)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), [])

    def test_hemingway_mentions_share_an_entity_key(self):
        questions = [
            question
            for bank in QUESTION_BANK.values()
            for question in bank
            if "hemingway"
            in (question.get("prompt", "") + question.get("explanation", "")).casefold()
        ]
        self.assertGreaterEqual(len(questions), 3)
        self.assertTrue(
            all("entity:ernest hemingway" in question_subject_keys(question) for question in questions)
        )

    def test_relative_error_is_scale_independent(self):
        self.assertEqual(estimate_points(9_000, 8_000)[0], estimate_points(3.9375, 3.5)[0])

    def test_estimate_scale_boundaries(self):
        self.assertEqual(estimate_points(8_000, 8_000)[0], 100)
        self.assertEqual(estimate_points(16_000, 8_000)[0], 10)
        self.assertEqual(estimate_points(20_000, 8_000)[0], 10)

    def test_calendar_year_uses_a_century_as_percentage_base(self):
        points, relative_error = estimate_points(1865, 1945, percentage_base=100)
        self.assertEqual(points, 20)
        self.assertEqual(relative_error, 0.8)

        evaluated = evaluate(
            {"category": "estimate", "answer": 1945, "unit": "Jahr"},
            {"answer": "1865"},
        )
        self.assertEqual(evaluated["accuracy_points"], 20)

    def test_order_credit_awards_each_correctly_ordered_pair(self):
        correct = ["A", "B", "C", "D"]
        self.assertEqual(order_credit(correct, correct), 1.0)
        self.assertEqual(order_credit(["D", "C", "B", "A"], correct), 0.0)
        self.assertAlmostEqual(order_credit(["A", "C", "D", "B"], correct), 4 / 6)
        self.assertAlmostEqual(order_credit(["A", "B", "D", "C"], correct), 5 / 6)

    def test_order_credit_survives_a_wrong_first_event(self):
        correct = ["A", "B", "C", "D"]
        self.assertEqual(order_credit(["B", "C", "D", "A"], correct), 0.5)

        evaluated = evaluate(
            {"category": "order", "answer": correct},
            {"answer": json.dumps(["B", "C", "D", "A"])},
        )
        self.assertEqual(evaluated["accuracy_points"], 50)

    def test_question_plan_uses_every_question_before_repeating(self):
        seen = {}
        start = date(2026, 9, 30)
        for offset in range(max(len(questions) for questions in QUESTION_BANK.values())):
            questions = daily_questions((start + timedelta(days=offset)).isoformat())
            for question in questions:
                seen.setdefault(question["category"], set()).add(question["id"])
        self.assertEqual(
            {question_type: len(question_ids) for question_type, question_ids in seen.items()},
            {question_type: len(questions) for question_type, questions in QUESTION_BANK.items()},
        )

    def test_time_factor_holds_then_reaches_zero_at_each_limit(self):
        self.assertEqual(question_time_factor(0, 0), 1.0)
        self.assertEqual(question_time_factor(5, 0), 1.0)
        self.assertEqual(question_time_factor(5.99, 0), 1.0)
        self.assertEqual(question_time_factor(6, 0), 0.8)
        self.assertEqual(question_time_factor(7, 0), 0.6)
        self.assertEqual(question_time_factor(10, 0), 0.0)
        self.assertEqual(question_time_factor(12, 1), 0.0)
        self.assertAlmostEqual(question_time_factor(15, 4), 0.5)

    def test_question_points_are_zero_when_wrong_and_time_never_halves_more(self):
        self.assertEqual(timed_question_points(100, 1.0), 100)
        self.assertEqual(timed_question_points(100, 0.5), 75)
        self.assertEqual(timed_question_points(100, 0.0), 50)
        self.assertEqual(timed_question_points(75, 0.0), 38)
        self.assertEqual(timed_question_points(50, 0.0), 25)
        self.assertEqual(timed_question_points(25, 0.0), 13)
        self.assertEqual(timed_question_points(10, 1.0), 10)
        self.assertEqual(timed_question_points(0, 0.0), 0)

    def test_partial_credit_preserves_the_number_of_subanswers(self):
        self.assertEqual(partial_credit(1, 4), 0.25)
        self.assertEqual(partial_credit(2, 4), 0.5)
        self.assertEqual(partial_credit(3, 4), 0.75)
        self.assertAlmostEqual(partial_credit(1, 3), 1 / 3)
        self.assertAlmostEqual(partial_credit(2, 3), 2 / 3)

    def test_wrong_answer_scores_zero_and_match_points_stay_proportional(self):
        binary = {"category": "true_false", "answer": True}
        wrong = evaluate(binary, {"answer": "false"})
        self.assertEqual(wrong["accuracy_points"], 0)
        self.assertEqual(timed_question_points(wrong["accuracy_points"], 1.0), 0)

        matching = {
            "category": "match",
            "left": ["A", "B", "C"],
            "right": ["1", "2", "3"],
            "answer": {"A": "1", "B": "2", "C": "3"},
        }
        one_correct = evaluate(
            matching,
            {"pair_0": "1", "pair_1": "3", "pair_2": "2"},
        )
        self.assertAlmostEqual(one_correct["credit"], 1 / 3)
        self.assertEqual(one_correct["accuracy_points"], 33)

    def test_match_options_never_reveal_row_to_option_position(self):
        for offset in range(len(QUESTION_BANK["match"])):
            questions = daily_questions(
                (date(2026, 9, 30) + timedelta(days=offset)).isoformat()
            )
            question = next(item for item in questions if item["category"] == "match")
            correct_order = [question["answer"][left] for left in question["left"]]
            options = match_option_order(question, f"seed-{offset}")
            self.assertEqual(set(options), set(correct_order))
            self.assertTrue(
                all(option != correct for option, correct in zip(options, correct_order))
            )


class GameFlowTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "test-key",
                "DATABASE": str(Path(self.tempdir.name) / "test.sqlite3"),
                "PUBLIC_URL": "https://example.test/guesstimate",
            }
        )
        self.client = self.app.test_client()

    def tearDown(self):
        self.tempdir.cleanup()

    def csrf(self):
        with self.client.session_transaction() as session:
            return session["csrf_token"]

    def register(self, username="Jan", pin="1001"):
        self.client.get("/registrieren")
        return self.client.post(
            "/registrieren",
            data={
                "username": username,
                "pin": pin,
                "pin_confirm": pin,
                "csrf_token": self.csrf(),
            },
        )

    def register_client(self, client, username, pin):
        client.get("/registrieren")
        with client.session_transaction() as client_session:
            token = client_session["csrf_token"]
        response = client.post(
            "/registrieren",
            data={
                "username": username,
                "pin": pin,
                "pin_confirm": pin,
                "csrf_token": token,
            },
        )
        with client.session_transaction() as client_session:
            return response, client_session["csrf_token"]

    def test_mail_configuration_is_never_shown_to_players(self):
        self.register("stormseed")
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"GMX", response.data)
        self.assertNotIn(b"E-Mail-Warnung", response.data)
        self.assertNotIn(b"Fragen-Nachschub", response.data)

    def finish_party_start_countdown(self, lobby_id):
        with self.app.app_context():
            database = self.app.get_db()
            past = (datetime.now() - timedelta(seconds=1)).isoformat(
                timespec="microseconds"
            )
            database.execute(
                "UPDATE party_lobbies SET countdown_ends_at = ? WHERE id = ?",
                (past, lobby_id),
            )
            database.commit()
        self.client.get(f"/party/{lobby_id}/status")

    def test_login_rejects_wrong_pin(self):
        self.register()
        self.client.post("/logout", data={"csrf_token": self.csrf()})
        self.client.get("/login")
        response = self.client.post(
            "/login",
            data={"username": "jan", "pin": "9999", "csrf_token": self.csrf()},
        )
        self.assertIn("stimmen nicht".encode(), response.data)

    def test_login_uses_requested_branding_and_registration_copy(self):
        response = self.client.get("/login")
        self.assertIn("Stormseed´s".encode(), response.data)
        self.assertIn(b"<strong>Guesstimate</strong>", response.data)
        self.assertNotIn(b"<em>daily</em>", response.data)
        self.assertIn(b'placeholder="Dein Name"', response.data)
        self.assertIn('placeholder="••••"'.encode(), response.data)
        self.assertNotIn(b'placeholder="z. B. jan"', response.data)
        self.assertIn(b"Neu hier?", response.data)
        self.assertIn(b"Spielregeln", response.data)
        self.assertIn("Verpasste Runden der laufenden Woche".encode(), response.data)
        self.assertNotIn(b"Urlaub", response.data)
        self.assertIn(b'<meta property="og:title" content="Guesstimate">', response.data)
        self.assertIn(
            b'<meta property="og:image" content="https://example.test/guesstimate/static/guesstimate-share.jpg">',
            response.data,
        )
        self.assertIn(b'<meta name="twitter:card" content="summary_large_image">', response.data)

    def test_login_offers_every_missed_day_of_the_current_week(self):
        self.register()
        self.client.post("/logout", data={"csrf_token": self.csrf()})
        self.client.get("/login")
        response = self.client.post(
            "/login",
            data={"username": "jan", "pin": "1001", "csrf_token": self.csrf()},
            follow_redirects=True,
        )
        if date.today().weekday() > 0:
            self.assertIn("HÖCHST UNTREU".encode(), response.data)
            response = self.client.post(
                "/woche/auswahl",
                data={"choice": "all", "csrf_token": self.csrf()},
                follow_redirects=True,
            )
            self.assertIn(b"Nachholrunde vom", response.data)
        self.assertNotIn(b"Urlaub nehmen", response.data)

    def test_sunday_login_can_replay_every_missed_day_of_the_week(self):
        self.register()
        with self.app.app_context():
            database = self.app.get_db()
            user_id = database.execute(
                "SELECT id FROM users WHERE username = 'jan'"
            ).fetchone()[0]
            missed = missed_current_week_dates(user_id, date(2026, 10, 4))
        self.assertEqual(
            missed,
            [
                "2026-09-28",
                "2026-09-29",
                "2026-09-30",
                "2026-10-01",
                "2026-10-02",
                "2026-10-03",
            ],
        )

    def test_perfect_round_scores_500_and_cannot_repeat(self):
        self.register()
        self.client.post("/runde/starten", data={"csrf_token": self.csrf()})

        with self.app.app_context():
            database = self.app.get_db()
            round_row = database.execute("SELECT * FROM daily_rounds").fetchone()
            questions = json.loads(round_row["questions_json"])

        for question in questions:
            category = question["category"]
            if category == "multiple_choice":
                data = {"answer": question["answer"]}
            elif category == "true_false":
                data = {"answer": str(question["answer"]).lower()}
            elif category == "estimate":
                data = {"answer": str(question["answer"])}
            elif category == "order":
                data = {"answer": json.dumps(question["answer"])}
            else:
                data = {
                    f"pair_{index}": question["answer"][left]
                    for index, left in enumerate(question["left"])
                }
            data["csrf_token"] = self.csrf()
            response = self.client.post("/runde/antwort", data=data)
            self.assertEqual(response.status_code, 302)
            with self.app.app_context():
                database = self.app.get_db()
                database.execute(
                    "UPDATE answers SET created_at = ? WHERE id = (SELECT MAX(id) FROM answers)",
                    (
                        (datetime.now() - timedelta(seconds=5)).isoformat(
                            timespec="microseconds"
                        ),
                    ),
                )
                database.commit()
            self.client.post("/runde/weiter", data={"csrf_token": self.csrf()})

        response = self.client.get("/ergebnis")
        self.assertIn(b"500", response.data)
        self.assertIn(b"DEIN AKTUELLER PLATZ", response.data)
        self.assertIn(b"Deine Antworten", response.data)
        self.assertIn("Du hast <strong>500 Ikühe</strong> verdient".encode(), response.data)
        self.assertIn("Du hast 500 Ikühe".encode(), response.data)
        self.assertIn(b"Tagessieger", response.data)
        self.assertIn(b"Wochenliga", response.data)
        self.assertIn(b"Hall of Fame", response.data)
        self.assertIn("Punkte nach Zeitabzug".encode(), response.data)
        self.assertIn(str(escape(questions[0]["prompt"])).encode(), response.data)

        with self.app.app_context():
            self.app.get_db().execute("UPDATE attempts SET rank_after = 99")
            self.app.get_db().commit()
        response = self.client.get("/ergebnis")
        self.assertIn(b"#1", response.data)
        self.assertNotIn(b"#99", response.data)

        self.client.post("/runde/starten", data={"csrf_token": self.csrf()})
        with self.app.app_context():
            count = self.app.get_db().execute("SELECT COUNT(*) FROM attempts").fetchone()[0]
            attempt = self.app.get_db().execute("SELECT * FROM attempts").fetchone()
        self.assertEqual(count, 1)
        self.assertEqual(attempt["status"], "completed")

    def test_server_applies_time_factor_to_question_points(self):
        self.register()
        self.client.post("/runde/starten", data={"csrf_token": self.csrf()})
        response = self.client.get("/runde")
        self.assertIn(b'data-limit="10"', response.data)

        with self.app.app_context():
            database = self.app.get_db()
            attempt = database.execute("SELECT * FROM attempts").fetchone()
            round_row = database.execute("SELECT * FROM daily_rounds").fetchone()
            question = json.loads(round_row["questions_json"])[0]
            started_at = (datetime.now() - timedelta(seconds=8.2)).isoformat(
                timespec="microseconds"
            )
            database.execute(
                "UPDATE attempts SET question_started_at = ? WHERE id = ?",
                (started_at, attempt["id"]),
            )
            database.commit()

        answer = "true" if question["answer"] else "false"
        self.client.post(
            "/runde/antwort",
            data={"answer": answer, "csrf_token": self.csrf()},
        )
        with self.app.app_context():
            stored = self.app.get_db().execute("SELECT * FROM answers").fetchone()
            attempt = self.app.get_db().execute("SELECT * FROM attempts").fetchone()
        self.assertEqual(stored["time_factor"], 0.4)
        self.assertEqual(stored["accuracy_points"], 100)
        self.assertEqual(stored["points"], 70)

    def test_used_content_cannot_return_under_a_different_id(self):
        with self.app.app_context():
            database = self.app.get_db()
            original = QUESTION_BANK["true_false"][0]
            database.execute(
                """
                INSERT INTO question_usage
                    (question_id, content_hash, category, source_type, source_id, used_at)
                VALUES (?, ?, ?, 'test', 'historic-alias', ?)
                """,
                (
                    "historic-id-for-same-question",
                    question_fingerprint(original, "true_false"),
                    "true_false",
                    datetime.now().isoformat(),
                ),
            )
            database.commit()
            selected = reserve_question_sets("test", "fresh-round")[0]
        self.assertNotIn(original["id"], {question["id"] for question in selected})

    def test_game_reset_preserves_permanent_question_history(self):
        database_path = self.app.config["DATABASE"]
        with self.app.app_context():
            database = self.app.get_db()
            question = QUESTION_BANK["true_false"][0]
            database.execute(
                """
                INSERT INTO question_usage
                    (question_id, content_hash, category, source_type, source_id, used_at)
                VALUES (?, ?, 'true_false', 'test', 'before-reset', ?)
                """,
                (
                    question["id"],
                    question_fingerprint(question, "true_false"),
                    datetime.now().isoformat(),
                ),
            )
            database.commit()

        reset(database_path)
        database = sqlite3.connect(database_path)
        try:
            self.assertEqual(
                database.execute("SELECT COUNT(*) FROM question_usage").fetchone()[0],
                1,
            )
            self.assertEqual(
                database.execute("SELECT COUNT(*) FROM daily_rounds").fetchone()[0],
                0,
            )
        finally:
            database.close()

    def test_feedback_stays_visible_for_four_seconds_before_advancing(self):
        self.register()
        self.client.post("/runde/starten", data={"csrf_token": self.csrf()})
        with self.app.app_context():
            database = self.app.get_db()
            round_row = database.execute("SELECT * FROM daily_rounds").fetchone()
            question = json.loads(round_row["questions_json"])[0]

        answer = "true" if question["answer"] else "false"
        self.client.post(
            "/runde/antwort",
            data={"answer": answer, "csrf_token": self.csrf()},
        )

        feedback = self.client.get("/runde")
        self.assertIn(b"data-feedback-delay", feedback.data)
        self.assertIn(b"feedback.js?v=1", feedback.data)
        self.assertRegex(feedback.data, rb"data-remaining-ms=\"[1-9][0-9]+\"")

        self.client.post("/runde/weiter", data={"csrf_token": self.csrf()})
        with self.app.app_context():
            database = self.app.get_db()
            attempt = database.execute("SELECT * FROM attempts").fetchone()
            self.assertEqual(attempt["current_index"], 0)
            database.execute(
                "UPDATE answers SET created_at = ?",
                (
                    (datetime.now() - timedelta(seconds=5)).isoformat(
                        timespec="microseconds"
                    ),
                ),
            )
            database.commit()

        self.client.post("/runde/weiter", data={"csrf_token": self.csrf()})
        with self.app.app_context():
            attempt = self.app.get_db().execute("SELECT * FROM attempts").fetchone()
        self.assertEqual(attempt["current_index"], 1)

    def test_match_rendering_is_deranged_and_order_uses_drag_and_drop(self):
        self.register()
        self.client.post("/runde/starten", data={"csrf_token": self.csrf()})
        with self.app.app_context():
            database = self.app.get_db()
            database.execute(
                "UPDATE attempts SET current_index = 2, question_started_at = NULL"
            )
            database.commit()
            round_row = database.execute("SELECT * FROM daily_rounds").fetchone()
            match_question = json.loads(round_row["questions_json"])[2]

        response = self.client.get("/runde")
        rendered_values = [
            value.decode()
            for value in re.findall(rb'data-match-value="([^"]+)"', response.data)
        ]
        rendered_orders = [
            rendered_values[index : index + len(match_question["right"])]
            for index in range(0, len(rendered_values), len(match_question["right"]))
        ]
        self.assertEqual(len(rendered_orders), 3)
        self.assertTrue(all(order == rendered_orders[0] for order in rendered_orders))
        self.assertNotIn(b"<select", response.data)
        self.assertIn(b"match.js?v=1", response.data)
        self.assertEqual(response.data.count(b"data-match-row"), 3)
        correct_order = [
            match_question["answer"][left] for left in match_question["left"]
        ]
        self.assertTrue(
            all(
                option != correct
                for option, correct in zip(rendered_orders[0], correct_order)
            )
        )

        with self.app.app_context():
            database = self.app.get_db()
            database.execute(
                "UPDATE attempts SET current_index = 3, question_started_at = NULL"
            )
            database.commit()
        response = self.client.get("/runde")
        self.assertIn(b"drag-handle", response.data)
        self.assertIn("↔".encode(), response.data)
        self.assertNotIn("↕".encode(), response.data)
        self.assertIn(b"Spielregeln", response.data)
        self.assertIn("Du hast 0 Ikühe".encode(), response.data)
        self.assertIn(b"game.js?v=3", response.data)
        self.assertNotIn(b"move-up", response.data)
        self.assertNotIn(b"move-down", response.data)

    def test_friends_can_choose_their_own_login(self):
        response = self.register("Quiz Königin", "mein-geheimnis")
        self.assertEqual(response.status_code, 302)
        with self.app.app_context():
            user = self.app.get_db().execute(
                "SELECT * FROM users WHERE username = ?", ("quiz königin",)
            ).fetchone()
        self.assertEqual(user["display_name"], "Quiz Königin")

        self.client.post("/logout", data={"csrf_token": self.csrf()})
        self.client.get("/login")
        response = self.client.post(
            "/login",
            data={
                "username": "QUIZ KÖNIGIN",
                "pin": "mein-geheimnis",
                "csrf_token": self.csrf(),
            },
        )
        self.assertEqual(response.status_code, 302)

    def test_registration_is_limited_to_100_players(self):
        with self.app.app_context():
            database = self.app.get_db()
            database.executemany(
                "INSERT INTO users (username, display_name, pin_hash, created_at) VALUES (?, ?, ?, ?)",
                [(f"user{index}", f"User {index}", "unused", "now") for index in range(100)],
            )
            database.commit()
            with self.assertRaises(sqlite3.IntegrityError):
                database.execute(
                    "INSERT INTO users (username, display_name, pin_hash, created_at) VALUES (?, ?, ?, ?)",
                    ("user101", "User 101", "unused", "now"),
                )
            database.rollback()

        self.client.get("/registrieren")
        response = self.client.post(
            "/registrieren",
            data={
                "username": "User 101",
                "pin": "1234",
                "pin_confirm": "1234",
                "csrf_token": self.csrf(),
            },
        )
        self.assertIn("100 Spielern".encode(), response.data)

    def test_leaderboard_contains_every_player_and_scrolls_after_five(self):
        self.register("Spieler 1")
        with self.app.app_context():
            database = self.app.get_db()
            database.executemany(
                """
                INSERT INTO users (username, display_name, pin_hash, created_at)
                VALUES (?, ?, ?, ?)
                """,
                [
                    (f"spieler {index}", f"Spieler {index}", "unused", datetime.now().isoformat())
                    for index in range(2, 8)
                ],
            )
            database.commit()

        response = self.client.get("/")
        self.assertIn(b"is-scrollable", response.data)
        self.assertIn("Spieler 7".encode(), response.data)
        self.assertIn("7 Spielern".encode(), response.data)

    def test_party_lobby_reserves_questions_without_affecting_regular_scores(self):
        self.register("Partyhost")
        response = self.client.post(
            "/party/erstellen",
            data={"csrf_token": self.csrf()},
        )
        self.assertEqual(response.status_code, 302)
        lobby_id = int(response.headers["Location"].rstrip("/").split("/")[-1])
        self.client.post(
            f"/party/{lobby_id}/einstellungen",
            data={"csrf_token": self.csrf(), "name": "Freitagsparty", "rounds": "5"},
        )
        response = self.client.post(
            f"/party/{lobby_id}/starten",
            data={"csrf_token": self.csrf()},
            follow_redirects=True,
        )
        self.assertIn("Die Party startet".encode(), response.data)
        self.assertIn(b'data-visual-seconds="6"', response.data)
        self.finish_party_start_countdown(lobby_id)
        response = self.client.get(f"/party/{lobby_id}")
        self.assertIn(b"PARTYFRAGE 1 VON 25", response.data)
        with self.app.app_context():
            database = self.app.get_db()
            party_ids = {
                row["question_id"]
                for row in database.execute(
                    "SELECT question_id FROM question_usage WHERE source_type = 'party'"
                ).fetchall()
            }
            self.assertEqual(
                len(party_ids),
                25,
            )
            lobby_questions = json.loads(
                database.execute(
                    "SELECT questions_json FROM party_lobbies WHERE id = ?", (lobby_id,)
                ).fetchone()[0]
            )
            seen_subjects = set()
            for question in lobby_questions:
                subjects = question_subject_keys(question)
                self.assertFalse(subjects & seen_subjects)
                seen_subjects.update(subjects)
            self.assertEqual(database.execute("SELECT COUNT(*) FROM attempts").fetchone()[0], 0)

        self.client.get("/")
        with self.app.app_context():
            database = self.app.get_db()
            daily_ids = {
                row["question_id"]
                for row in database.execute(
                    "SELECT question_id FROM question_usage WHERE source_type = 'daily'"
                ).fetchall()
            }
            self.assertEqual(len(daily_ids), 5)
            self.assertTrue(party_ids.isdisjoint(daily_ids))
            self.assertEqual(database.execute("SELECT COUNT(*) FROM attempts").fetchone()[0], 0)

    def test_party_advances_only_after_every_active_player_answered(self):
        self.register("Host")
        response = self.client.post(
            "/party/erstellen", data={"csrf_token": self.csrf()}
        )
        lobby_id = int(response.headers["Location"].rstrip("/").split("/")[-1])

        guest = self.app.test_client()
        guest.get("/registrieren")
        with guest.session_transaction() as guest_session:
            guest_csrf = guest_session["csrf_token"]
        guest.post(
            "/registrieren",
            data={
                "username": "Gast",
                "pin": "2002",
                "pin_confirm": "2002",
                "csrf_token": guest_csrf,
            },
        )
        with guest.session_transaction() as guest_session:
            guest_csrf = guest_session["csrf_token"]
        guest.post(
            f"/party/{lobby_id}/beitreten", data={"csrf_token": guest_csrf}
        )
        waiting_lobby = self.client.get(f"/party/{lobby_id}")
        self.assertIn(b"data-party-lobby", waiting_lobby.data)
        self.assertIn(b"party.js?v=2", waiting_lobby.data)
        self.client.post(
            f"/party/{lobby_id}/starten", data={"csrf_token": self.csrf()}
        )
        self.finish_party_start_countdown(lobby_id)

        with self.app.app_context():
            database = self.app.get_db()
            lobby = database.execute(
                "SELECT * FROM party_lobbies WHERE id = ?", (lobby_id,)
            ).fetchone()
            question = json.loads(lobby["questions_json"])[0]
        answer = "true" if question["answer"] else "false"

        self.client.post(
            f"/party/{lobby_id}/antwort",
            data={"answer": answer, "csrf_token": self.csrf()},
        )
        with self.app.app_context():
            current = self.app.get_db().execute(
                "SELECT current_question_index FROM party_lobbies WHERE id = ?", (lobby_id,)
            ).fetchone()[0]
        self.assertEqual(current, 0)

        guest.post(
            f"/party/{lobby_id}/antwort",
            data={"answer": answer, "csrf_token": guest_csrf},
        )
        with self.app.app_context():
            database = self.app.get_db()
            current = database.execute(
                "SELECT current_question_index FROM party_lobbies WHERE id = ?", (lobby_id,)
            ).fetchone()[0]
            regular_attempts = database.execute("SELECT COUNT(*) FROM attempts").fetchone()[0]
        self.assertEqual(current, 1)
        self.assertEqual(regular_attempts, 0)
        transition = self.client.get(f"/party/{lobby_id}")
        self.assertIn("Nächste Frage".encode(), transition.data)
        self.assertIn(b'data-visual-seconds="2"', transition.data)

    def test_last_party_answer_shows_estimate_difference_before_podium(self):
        self.register("Finalhost")
        response = self.client.post(
            "/party/erstellen", data={"csrf_token": self.csrf()}
        )
        lobby_id = int(response.headers["Location"].rstrip("/").split("/")[-1])
        self.client.post(
            f"/party/{lobby_id}/starten", data={"csrf_token": self.csrf()}
        )
        self.finish_party_start_countdown(lobby_id)
        with self.app.app_context():
            database = self.app.get_db()
            lobby = database.execute(
                "SELECT * FROM party_lobbies WHERE id = ?", (lobby_id,)
            ).fetchone()
            questions = json.loads(lobby["questions_json"])
            estimate = questions[4]
            database.execute(
                """
                UPDATE party_lobbies
                SET status = 'playing', current_question_index = 4,
                    question_started_at = ?
                WHERE id = ?
                """,
                (
                    (datetime.now() - timedelta(seconds=1)).isoformat(
                        timespec="microseconds"
                    ),
                    lobby_id,
                ),
            )
            database.commit()

        response = self.client.post(
            f"/party/{lobby_id}/antwort",
            data={
                "answer": str(float(estimate["answer"]) + 1),
                "csrf_token": self.csrf(),
            },
            follow_redirects=True,
        )
        self.assertIn("Deine Schätzung".encode(), response.data)
        self.assertIn(b"Richtiger Wert", response.data)
        self.assertIn(b"Abweichung", response.data)
        self.assertIn(b"Endergebnis jetzt ansehen", response.data)
        self.assertIn(b"bleibt 8 Sekunden sichtbar", response.data)
        self.assertNotIn(b"Das Podest", response.data)

        status = self.client.get(f"/party/{lobby_id}/status")
        self.assertGreater(status.json["completion_feedback_remaining_ms"], 6000)
        result = self.client.get(f"/party/{lobby_id}")
        self.assertIn(b"Das Podest", result.data)

    def test_started_party_rejects_new_members_and_lobby_limit_is_two(self):
        self.register("Host eins")
        first = self.client.post(
            "/party/erstellen", data={"csrf_token": self.csrf()}
        )
        first_id = int(first.headers["Location"].rstrip("/").split("/")[-1])

        second_client = self.app.test_client()
        _, second_csrf = self.register_client(second_client, "Host zwei", "2002")
        second = second_client.post(
            "/party/erstellen", data={"csrf_token": second_csrf}
        )
        self.assertEqual(second.status_code, 302)

        third_client = self.app.test_client()
        _, third_csrf = self.register_client(third_client, "Host drei", "3003")
        third_client.post(
            "/party/erstellen", data={"csrf_token": third_csrf}
        )
        with self.app.app_context():
            database = self.app.get_db()
            self.assertEqual(
                database.execute(
                    "SELECT COUNT(*) FROM party_lobbies WHERE status IN ('waiting', 'countdown', 'playing')"
                ).fetchone()[0],
                2,
            )

        self.client.post(
            f"/party/{first_id}/starten", data={"csrf_token": self.csrf()}
        )
        party_overview = self.client.get("/party")
        self.assertIn("Zurück ins Spiel".encode(), party_overview.data)
        self.assertIn(f'href="/party/{first_id}"'.encode(), party_overview.data)
        guest = self.app.test_client()
        _, guest_csrf = self.register_client(guest, "Zu spät", "4004")
        guest.post(
            f"/party/{first_id}/beitreten", data={"csrf_token": guest_csrf}
        )
        with self.app.app_context():
            database = self.app.get_db()
            guest_id = database.execute(
                "SELECT id FROM users WHERE username = 'zu spät'"
            ).fetchone()[0]
            self.assertIsNone(
                database.execute(
                    "SELECT id FROM party_members WHERE lobby_id = ? AND user_id = ?",
                    (first_id, guest_id),
                ).fetchone()
            )

    def test_host_can_remove_stuck_member_and_the_party_advances(self):
        self.register("Host")
        response = self.client.post(
            "/party/erstellen", data={"csrf_token": self.csrf()}
        )
        lobby_id = int(response.headers["Location"].rstrip("/").split("/")[-1])
        guest = self.app.test_client()
        _, guest_csrf = self.register_client(guest, "Bummelgast", "2002")
        guest.post(
            f"/party/{lobby_id}/beitreten", data={"csrf_token": guest_csrf}
        )
        self.client.post(
            f"/party/{lobby_id}/starten", data={"csrf_token": self.csrf()}
        )
        self.finish_party_start_countdown(lobby_id)
        with self.app.app_context():
            database = self.app.get_db()
            lobby = database.execute(
                "SELECT * FROM party_lobbies WHERE id = ?", (lobby_id,)
            ).fetchone()
            question = json.loads(lobby["questions_json"])[0]
            guest_member_id = database.execute(
                """
                SELECT pm.id FROM party_members pm JOIN users u ON u.id = pm.user_id
                WHERE pm.lobby_id = ? AND u.username = 'bummelgast'
                """,
                (lobby_id,),
            ).fetchone()[0]
        answer = "true" if question["answer"] else "false"
        self.client.post(
            f"/party/{lobby_id}/antwort",
            data={"answer": answer, "csrf_token": self.csrf()},
        )
        self.client.post(
            f"/party/{lobby_id}/mitglied/{guest_member_id}/entfernen",
            data={"csrf_token": self.csrf()},
        )
        with self.app.app_context():
            database = self.app.get_db()
            lobby = database.execute(
                "SELECT * FROM party_lobbies WHERE id = ?", (lobby_id,)
            ).fetchone()
            member_status = database.execute(
                "SELECT status FROM party_members WHERE id = ?", (guest_member_id,)
            ).fetchone()[0]
        self.assertEqual(lobby["current_question_index"], 1)
        self.assertEqual(member_status, "removed")

    def test_empty_stale_party_is_closed_and_cannot_be_joined(self):
        self.register("Geisterhost")
        response = self.client.post(
            "/party/erstellen", data={"csrf_token": self.csrf()}
        )
        lobby_id = int(response.headers["Location"].rstrip("/").split("/")[-1])
        with self.app.app_context():
            database = self.app.get_db()
            old = (datetime.now() - timedelta(minutes=2)).isoformat(
                timespec="microseconds"
            )
            database.execute(
                "UPDATE party_members SET last_seen_at = ? WHERE lobby_id = ?",
                (old, lobby_id),
            )
            database.commit()

        guest = self.app.test_client()
        _, guest_csrf = self.register_client(guest, "Später Gast", "2002")
        overview = guest.get("/party")
        self.assertNotIn("Geisterhosts Party".encode(), overview.data)
        guest.post(
            f"/party/{lobby_id}/beitreten", data={"csrf_token": guest_csrf}
        )
        with self.app.app_context():
            database = self.app.get_db()
            lobby_status = database.execute(
                "SELECT status FROM party_lobbies WHERE id = ?", (lobby_id,)
            ).fetchone()[0]
            active_members = database.execute(
                "SELECT COUNT(*) FROM party_members WHERE lobby_id = ? AND status = 'active'",
                (lobby_id,),
            ).fetchone()[0]
        self.assertEqual(lobby_status, "abandoned")
        self.assertEqual(active_members, 0)

    def test_vanished_host_disappears_and_guest_takes_over_live(self):
        self.register("Alter Host")
        response = self.client.post(
            "/party/erstellen", data={"csrf_token": self.csrf()}
        )
        lobby_id = int(response.headers["Location"].rstrip("/").split("/")[-1])
        guest = self.app.test_client()
        _, guest_csrf = self.register_client(guest, "Neuer Host", "2002")
        guest.post(
            f"/party/{lobby_id}/beitreten", data={"csrf_token": guest_csrf}
        )
        with self.app.app_context():
            database = self.app.get_db()
            old = (datetime.now() - timedelta(minutes=2)).isoformat(
                timespec="microseconds"
            )
            original_host_id = database.execute(
                "SELECT host_user_id FROM party_lobbies WHERE id = ?", (lobby_id,)
            ).fetchone()[0]
            database.execute(
                """
                UPDATE party_members SET last_seen_at = ?
                WHERE lobby_id = ? AND user_id = ?
                """,
                (old, lobby_id, original_host_id),
            )
            database.commit()

        status = guest.get(f"/party/{lobby_id}/status")
        self.assertEqual(status.status_code, 200)
        self.assertEqual([member["name"] for member in status.json["members"]], ["Neuer Host"])
        guest_lobby = guest.get(f"/party/{lobby_id}")
        self.assertIn(b"Einstellungen speichern", guest_lobby.data)
        self.assertEqual(self.client.get(f"/party/{lobby_id}/status").status_code, 404)

    def test_last_player_leaving_closes_the_party(self):
        self.register("Allein")
        response = self.client.post(
            "/party/erstellen", data={"csrf_token": self.csrf()}
        )
        lobby_id = int(response.headers["Location"].rstrip("/").split("/")[-1])
        response = self.client.post(
            f"/party/{lobby_id}/verlassen",
            data={"csrf_token": self.csrf()},
            follow_redirects=True,
        )
        self.assertIn("Noch keine Party".encode(), response.data)
        with self.app.app_context():
            status = self.app.get_db().execute(
                "SELECT status FROM party_lobbies WHERE id = ?", (lobby_id,)
            ).fetchone()[0]
        self.assertEqual(status, "abandoned")

    def test_party_lobby_is_limited_to_ten_active_players(self):
        self.register("Host")
        response = self.client.post(
            "/party/erstellen", data={"csrf_token": self.csrf()}
        )
        lobby_id = int(response.headers["Location"].rstrip("/").split("/")[-1])
        with self.app.app_context():
            database = self.app.get_db()
            now = datetime.now().isoformat()
            for index in range(2, 11):
                user_id = database.execute(
                    """
                    INSERT INTO users (username, display_name, pin_hash, created_at)
                    VALUES (?, ?, 'unused', ?)
                    """,
                    (f"spieler {index}", f"Spieler {index}", now),
                ).lastrowid
                database.execute(
                    "INSERT INTO party_members (lobby_id, user_id, joined_at) VALUES (?, ?, ?)",
                    (lobby_id, user_id, now),
                )
            database.commit()

        eleventh = self.app.test_client()
        _, eleventh_csrf = self.register_client(eleventh, "Spieler elf", "1111")
        eleventh.post(
            f"/party/{lobby_id}/beitreten", data={"csrf_token": eleventh_csrf}
        )
        with self.app.app_context():
            database = self.app.get_db()
            self.assertEqual(
                database.execute(
                    "SELECT COUNT(*) FROM party_members WHERE lobby_id = ? AND status = 'active'",
                    (lobby_id,),
                ).fetchone()[0],
                10,
            )

    def test_equal_party_scores_share_the_same_podium_place(self):
        self.register("Host")
        response = self.client.post(
            "/party/erstellen", data={"csrf_token": self.csrf()}
        )
        lobby_id = int(response.headers["Location"].rstrip("/").split("/")[-1])
        guest = self.app.test_client()
        _, guest_csrf = self.register_client(guest, "Gleichstand", "2002")
        guest.post(
            f"/party/{lobby_id}/beitreten", data={"csrf_token": guest_csrf}
        )
        with self.app.app_context():
            database = self.app.get_db()
            database.execute(
                "UPDATE party_lobbies SET status = 'completed' WHERE id = ?", (lobby_id,)
            )
            database.execute(
                "UPDATE party_members SET score = 321 WHERE lobby_id = ?", (lobby_id,)
            )
            database.commit()
        response = self.client.get(f"/party/{lobby_id}")
        self.assertEqual(response.data.count(b'class="podium-1"'), 2)

    def test_pool_exhaustion_mail_is_marked_sent_only_after_delivery(self):
        secret_path = Path(self.tempdir.name) / "mail.secret"
        secret_path.write_text("test-password", encoding="utf-8")
        self.app.config.update(
            MAIL_USER="DaBrain@gmx.net",
            MAIL_TO="DaBrain@gmx.net",
            MAIL_PASSWORD_FILE=str(secret_path),
        )
        with self.app.app_context():
            database = self.app.get_db()
            database.execute(
                "INSERT INTO system_notifications (kind, created_at) VALUES (?, ?)",
                ("question_pool_exhausted", datetime.now().isoformat()),
            )
            database.commit()
            with patch("app.smtplib.SMTP") as smtp_class:
                smtp = smtp_class.return_value.__enter__.return_value
                self.assertTrue(send_pool_exhausted_email())
                smtp.starttls.assert_called_once()
                smtp.login.assert_called_once_with("DaBrain@gmx.net", "test-password")
                smtp.send_message.assert_called_once()
            sent_at = database.execute(
                "SELECT sent_at FROM system_notifications WHERE kind = ?",
                ("question_pool_exhausted",),
            ).fetchone()[0]
            self.assertIsNotNone(sent_at)

    def test_consuming_the_last_complete_round_queues_the_notification(self):
        with self.app.app_context():
            database = self.app.get_db()
            for category, questions in QUESTION_BANK.items():
                database.executemany(
                    """
                    INSERT INTO question_usage
                        (question_id, category, source_type, source_id, used_at)
                    VALUES (?, ?, 'test', 'already-used', ?)
                    """,
                    [
                        (question["id"], category, datetime.now().isoformat())
                        for question in questions[:-1]
                    ],
                )
            database.commit()
            get_or_create_round("2099-12-31")
            status = database.execute(
                "SELECT sent_at FROM system_notifications WHERE kind = 'question_pool_exhausted'"
            ).fetchone()
            remaining = database.execute(
                "SELECT COUNT(*) FROM question_usage"
            ).fetchone()[0]
        self.assertIsNotNone(status)
        self.assertIsNone(status["sent_at"])
        self.assertEqual(remaining, sum(len(questions) for questions in QUESTION_BANK.values()))


if __name__ == "__main__":
    unittest.main()
