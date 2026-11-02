import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from app import create_app
from nerd_mode import (
    PERFECT_ANSWER_SECONDS,
    PERFECT_MAX_PLAYERS,
    PERFECT_VOTE_SECONDS,
    QUESTION_BANKS,
    _pick_question,
)


class StormseedsPerfectTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "perfect-test",
                "DATABASE": str(Path(self.tempdir.name) / "test.sqlite3"),
            }
        )
        self.clients = []
        with self.app.app_context():
            database = self.app.get_db()
            for index, name in enumerate(("Host", "Bluffer", "Wähler"), 1):
                user_id = database.execute(
                    """
                    INSERT INTO users (username, display_name, pin_hash, created_at)
                    VALUES (?, ?, 'unused', ?)
                    """,
                    (name.casefold(), name, datetime.now().isoformat()),
                ).lastrowid
                client = self.app.test_client()
                token = f"token-{index}"
                with client.session_transaction() as player_session:
                    player_session["user_id"] = user_id
                    player_session["csrf_token"] = token
                    player_session["login_recorded_on"] = datetime.now().date().isoformat()
                self.clients.append((client, token))
            database.commit()

    def tearDown(self):
        self.tempdir.cleanup()

    def create_lobby(self):
        host, host_token = self.clients[0]
        host.post("/nerd/erstellen", data={"csrf_token": host_token})
        for client, token in self.clients[1:]:
            client.post("/nerd/1/beitreten", data={"csrf_token": token})

    def ready_guests_and_start(self):
        host, host_token = self.clients[0]
        for client, token in self.clients[1:]:
            client.post("/nerd/1/ready", data={"csrf_token": token})
        host.post("/nerd/1/start", data={"csrf_token": host_token})
        with self.app.app_context():
            database = self.app.get_db()
            database.execute(
                "UPDATE nerd_lobbies SET countdown_ends_at = ? WHERE id = 1",
                ((datetime.now() - timedelta(seconds=1)).isoformat(),),
            )
            database.commit()
        host.get("/nerd/1")

    def create_started_lobby(self):
        self.create_lobby()
        self.ready_guests_and_start()

    def force_phase_end(self):
        with self.app.app_context():
            database = self.app.get_db()
            database.execute(
                "UPDATE nerd_rounds SET early_advance_at = ? WHERE lobby_id = 1",
                ((datetime.now() - timedelta(seconds=1)).isoformat(),),
            )
            database.commit()
        self.clients[0][0].get("/nerd/1")

    def submit_answers(self):
        answers = (
            "Ein seltenes Werkzeug für sehr kleine Uhren.",
            "Eine alte Bezeichnung für den Schatten eines Turms.",
            "Ein Messverfahren für die Dichte von Nebel.",
        )
        for (client, token), answer in zip(self.clients, answers):
            client.post(
                "/nerd/1/antwort",
                data={"csrf_token": token, "answer": answer},
            )
        return answers

    def test_only_the_two_researched_perfect_banks_are_loaded(self):
        root = Path(__file__).resolve().parents[1]
        expected = {
            "term": len(
                json.loads(
                    (root / "fragen/stormseedsperfekt/begriffe/fragen.json").read_text()
                )
            ),
            "curiosity": len(
                json.loads(
                    (root / "fragen/stormseedsperfekt/kuriositaeten/fragen.json").read_text()
                )
            ),
        }
        self.assertEqual({key: len(value) for key, value in QUESTION_BANKS.items()}, expected)
        self.assertEqual(expected, {"term": 355, "curiosity": 158})

    def test_questions_repeat_only_after_the_global_category_pool_is_used(self):
        with self.app.app_context():
            database = self.app.get_db()
            bank_size = len(QUESTION_BANKS["term"])
            first_cycle = [_pick_question(database, "term")["id"] for _ in range(bank_size)]
            next_question = _pick_question(database, "term")["id"]
            database.commit()
        self.assertEqual(len(set(first_cycle)), bank_size)
        self.assertIn(next_question, first_cycle)

    def test_skipped_question_is_not_immediately_repeated_after_pool_reset(self):
        with self.app.app_context():
            database = self.app.get_db()
            bank = QUESTION_BANKS["curiosity"]
            database.executemany(
                """
                INSERT INTO perfect_question_usage(category, question_id, used_at)
                VALUES ('curiosity', ?, ?)
                """,
                [(item["id"], datetime.now().isoformat()) for item in bank],
            )
            replacement = _pick_question(
                database, "curiosity", {bank[0]["id"]}
            )
        self.assertNotEqual(replacement["id"], bank[0]["id"])

    def test_lobby_browser_lists_rounds_without_codes(self):
        self.create_lobby()
        with self.app.app_context():
            database = self.app.get_db()
            spectator_id = database.execute(
                """
                INSERT INTO users (username, display_name, pin_hash, created_at)
                VALUES ('zuschauer', 'Zuschauer', 'unused', ?)
                """,
                (datetime.now().isoformat(),),
            ).lastrowid
            database.commit()
        spectator = self.app.test_client()
        with spectator.session_transaction() as spectator_session:
            spectator_session["user_id"] = spectator_id
            spectator_session["csrf_token"] = "spectator-token"
            spectator_session["login_recorded_on"] = datetime.now().date().isoformat()
        browser_page = spectator.get("/nerd").data.decode()
        self.assertIn("beitreten", browser_page)
        self.assertIn("<dt>Host</dt><dd>Host</dd>", browser_page)
        self.assertNotIn('class="game-header"', browser_page)
        self.assertIn("was ein Apotropaion ist?", browser_page)
        self.assertNotIn("Welche Runde darf es sein?", browser_page)
        self.assertNotIn("8 Runden", browser_page)
        self.assertNotIn("Lobby-Code", browser_page)
        self.assertIn(
            '<a class="secondary-button lobby-browser-back" href="/karten/brettspiele">zurück zu brettspielen</a>',
            browser_page,
        )

        response = self.clients[0][0].get("/nerd/1")
        page = response.data.decode()
        self.assertEqual(page.count('<article class="perfect-player-window'), 3)
        self.assertNotIn("Freier Platz", page)
        self.assertIn("stormseed´s perfect", page)

    def test_lobby_accepts_eight_players_and_rejects_a_ninth(self):
        self.assertEqual(PERFECT_MAX_PLAYERS, 8)
        self.create_lobby()
        extra_clients = []
        with self.app.app_context():
            database = self.app.get_db()
            for index in range(4, 10):
                user_id = database.execute(
                    """
                    INSERT INTO users (username, display_name, pin_hash, created_at)
                    VALUES (?, ?, 'unused', ?)
                    """,
                    (f"gast{index}", f"Gast {index}", datetime.now().isoformat()),
                ).lastrowid
                client = self.app.test_client()
                token = f"token-{index}"
                with client.session_transaction() as player_session:
                    player_session["user_id"] = user_id
                    player_session["csrf_token"] = token
                    player_session["login_recorded_on"] = datetime.now().date().isoformat()
                extra_clients.append((client, token))
            database.commit()

        for client, token in extra_clients[:5]:
            response = client.post(
                "/nerd/1/beitreten",
                data={"csrf_token": token},
                follow_redirects=False,
            )
            self.assertTrue(response.headers["Location"].endswith("/nerd/1"))

        full_page = self.clients[0][0].get("/nerd/1").data.decode()
        self.assertIn("8/8 Spieler", full_page)
        self.assertEqual(full_page.count('<article class="perfect-player-window'), 8)
        self.assertEqual(full_page.count('class="perfect-player-wall is-'), 2)
        self.assertEqual(full_page.count("variant-a-profile-canonical"), 8)

        ninth, ninth_token = extra_clients[5]
        response = ninth.post(
            "/nerd/1/beitreten",
            data={"csrf_token": ninth_token},
            follow_redirects=False,
        )
        self.assertTrue(response.headers["Location"].endswith("/nerd"))
        with self.app.app_context():
            count = self.app.get_db().execute(
                "SELECT COUNT(*) FROM nerd_members WHERE lobby_id = 1 AND status = 'active'"
            ).fetchone()[0]
        self.assertEqual(count, 8)

    def test_host_starts_explicitly_after_all_guests_are_ready(self):
        self.create_lobby()
        host, host_token = self.clients[0]
        host.post("/nerd/1/start", data={"csrf_token": host_token})
        with self.app.app_context():
            status = self.app.get_db().execute(
                "SELECT status FROM nerd_lobbies WHERE id = 1"
            ).fetchone()[0]
        self.assertEqual(status, "waiting")

        self.clients[1][0].post(
            "/nerd/1/ready", data={"csrf_token": self.clients[1][1]}
        )
        host.post("/nerd/1/start", data={"csrf_token": host_token})
        with self.app.app_context():
            status = self.app.get_db().execute(
                "SELECT status FROM nerd_lobbies WHERE id = 1"
            ).fetchone()[0]
        self.assertEqual(status, "waiting")

        self.clients[2][0].post(
            "/nerd/1/ready", data={"csrf_token": self.clients[2][1]}
        )
        host.post("/nerd/1/start", data={"csrf_token": host_token})
        with self.app.app_context():
            status = self.app.get_db().execute(
                "SELECT status FROM nerd_lobbies WHERE id = 1"
            ).fetchone()[0]
        self.assertEqual(status, "countdown")

    def test_stale_guest_keeps_their_seat_in_waiting_lobby(self):
        self.create_lobby()
        old = (datetime.now() - timedelta(minutes=2)).isoformat()
        with self.app.app_context():
            database = self.app.get_db()
            database.execute(
                "UPDATE nerd_members SET last_seen_at = ? WHERE id = 2",
                (old,),
            )
            database.commit()
        self.clients[0][0].get("/nerd/1")
        with self.app.app_context():
            self.assertEqual(
                self.app.get_db().execute(
                    "SELECT status FROM nerd_members WHERE id = 2"
                ).fetchone()[0],
                "active",
            )

    def test_host_can_choose_points_or_time_and_change_resets_guests(self):
        self.create_lobby()
        for client, token in self.clients[1:]:
            client.post("/nerd/1/ready", data={"csrf_token": token})
        host, host_token = self.clients[0]
        host.post(
            "/nerd/1/einstellungen",
            data={
                "csrf_token": host_token,
                "name": "Freitagabend",
                "goal_mode": "time",
                "goal_value": "30",
            },
        )
        with self.app.app_context():
            database = self.app.get_db()
            lobby = database.execute(
                "SELECT name, goal_mode, goal_value FROM nerd_lobbies WHERE id = 1"
            ).fetchone()
            guest_readiness = [
                row[0]
                for row in database.execute(
                    "SELECT ready FROM nerd_members WHERE user_id != 1 ORDER BY id"
                )
            ]
        self.assertEqual(tuple(lobby), ("Freitagabend", "time", 30))
        self.assertEqual(guest_readiness, [0, 0])
        page = host.get("/nerd/1").data.decode()
        self.assertIn("Nach Punkten", page)
        self.assertIn("Nach Zeit", page)
        self.assertIn("30 Minuten", page)

    def test_lobby_is_room_interface_with_podiums_buzzer_and_points(self):
        self.create_lobby()
        host, host_token = self.clients[0]
        page = host.get("/nerd/1").data.decode()
        self.assertIn('class="perfect-lobby-name-editor"', page)
        self.assertIn("Host´s Runde", page)
        self.assertIn('class="perfect-settings-paper"', page)
        self.assertIn('class="perfect-buzzer"', page)
        self.assertIn("spiel starten", page)
        self.assertNotIn('class="perfect-podium-body"', page)
        self.assertIn("p00-startpult-tall-v2.png", page)
        self.assertIn("stormseeds-perfect-start-buzzer-v2.png", page)
        self.assertIn('class="variant-a-profile variant-a-profile-canonical', page)
        self.assertIn('class="perfect-player-wall is-left"', page)
        self.assertIn('class="perfect-player-wall is-right"', page)
        self.assertIn('class="perfect-player-status"', page)
        self.assertNotIn("perfect-avatar-wrap", page)
        self.assertNotIn("perfect-crown", page)
        self.assertIn('data-member-count="3"', page)
        self.assertNotIn("perfect-ready-lamp", page)
        self.assertIn("0 Punkte", page)
        self.assertNotIn("iKühe", page)
        self.assertIn("game_points=player.score", (Path(__file__).parents[1] / "templates/nerd_mode.html").read_text())
        self.assertNotIn('class="perfect-lobby-chat"', page)
        self.assertNotIn('value="like"', page)
        self.assertNotIn("Einstellungen speichern", page)
        self.assertNotIn("perfect-lobby-panel", page)

        guest_page = self.clients[1][0].get("/nerd/1").data.decode()
        self.assertIn('class="perfect-buzzer', guest_page)
        self.assertIn('bereit drücken', guest_page)
        self.assertIn("stormseeds-perfect-start-buzzer-v2.png", guest_page)

        response = host.post(
            "/nerd/1/chat",
            data={"csrf_token": host_token, "message": "Gute Runde euch!"},
        )
        self.assertEqual(response.status_code, 404)

    def test_lobby_navigation_leaves_and_last_member_closes_room(self):
        host, token = self.clients[0]
        host.post("/nerd/erstellen", data={"csrf_token": token})
        page = host.get("/nerd/1").data.decode()
        self.assertIn('action="/nerd/1/verlassen"', page)
        self.assertIn('data-member-count="1"', page)

        response = host.post(
            "/nerd/1/verlassen", data={"csrf_token": token}, follow_redirects=False
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith("/nerd"))
        with self.app.app_context():
            database = self.app.get_db()
            self.assertEqual(
                database.execute(
                    "SELECT status FROM nerd_lobbies WHERE id = 1"
                ).fetchone()[0],
                "abandoned",
            )

    def test_question_screen_uses_deine_antwort_and_no_old_mechanics(self):
        self.create_started_lobby()
        response = self.clients[0][0].get("/nerd/1")
        page = response.data.decode()
        self.assertIn("Deine Antwort", page)
        self.assertIn("<textarea", page)
        self.assertNotIn("Risiko", page)
        self.assertNotIn("Hold’em", page)
        self.assertNotIn("Kategorien", page)
        with self.app.app_context():
            row = self.app.get_db().execute(
                "SELECT category FROM nerd_rounds WHERE lobby_id = 1"
            ).fetchone()
        self.assertIn(row["category"], ("term", "curiosity"))

    def test_players_cannot_choose_their_own_answer_and_votes_stay_secret(self):
        self.create_started_lobby()
        self.submit_answers()
        self.force_phase_end()
        with self.app.app_context():
            answer_id = self.app.get_db().execute(
                "SELECT id FROM nerd_answers WHERE member_id = 1"
            ).fetchone()[0]
        host, token = self.clients[0]
        preview_page = host.get("/nerd/1").data.decode()
        self.assertIn("Deine Antwort – nicht wählbar", preview_page)
        self.assertIn(f'value="answer:{answer_id}"  disabled', preview_page)
        self.assertNotIn('data-vote-roster', preview_page)
        self.assertNotIn('data-voter-id=', preview_page)

        host.post(
            "/nerd/1/wahl",
            data={"csrf_token": token, "vote_key": f"answer:{answer_id}"},
        )
        with self.app.app_context():
            vote = self.app.get_db().execute(
                "SELECT draft_vote_key, vote_key, vote_locked_at FROM nerd_answers WHERE member_id = 1"
            ).fetchone()
        self.assertIsNone(vote[0])
        self.assertIsNone(vote[1])
        self.assertIsNone(vote[2])
        vote_page = self.clients[1][0].get("/nerd/1").data.decode()
        self.assertNotIn("Host hat diese Antwort eingeloggt", vote_page)
        self.assertIn('class="perfect-answer-options"', vote_page)
        self.assertIn("antwort einloggen", vote_page)

        status = self.clients[1][0].get("/nerd/1/status").get_json()
        self.assertTrue(all("draft_vote_key" not in row for row in status["answers"]))

        for client, player_token in self.clients[1:]:
            client.post(
                "/nerd/1/wahl",
                data={"csrf_token": player_token, "vote_key": "solution"},
            )
        self.force_phase_end()
        host.post("/nerd/1/host-pruefung", data={"csrf_token": token})
        with self.app.app_context():
            own_result = self.app.get_db().execute(
                "SELECT bluff_count, points_awarded FROM nerd_answers WHERE member_id = 1"
            ).fetchone()
        self.assertEqual(tuple(own_result), (0, 0))

    def test_round_timers_warning_and_host_pause(self):
        self.create_started_lobby()
        self.assertEqual(PERFECT_ANSWER_SECONDS, 180)
        self.assertEqual(PERFECT_VOTE_SECONDS, 105)
        host, token = self.clients[0]
        page = host.get("/nerd/1").data.decode()
        self.assertIn("Spiel pausieren", page)
        self.assertIn("Noch 30 Sekunden!", page)
        host.post(
            "/nerd/1/antwort-entwurf",
            data={"csrf_token": token, "answer": "Nur ein Entwurf"},
        )
        with self.app.app_context():
            before = self.app.get_db().execute(
                "SELECT phase_ends_at FROM nerd_rounds WHERE lobby_id = 1"
            ).fetchone()[0]
        host.post("/nerd/1/pause", data={"csrf_token": token})
        paused_page = host.get("/nerd/1").data.decode()
        self.assertIn("Spiel pausiert", paused_page)
        self.assertIn("Spiel fortsetzen", paused_page)
        self.assertIn(">Nur ein Entwurf</textarea>", paused_page)
        self.assertNotIn("Eingeloggt – warte auf die anderen.", paused_page)
        host.post(
            "/nerd/1/antwort",
            data={"csrf_token": token, "answer": "Während Pause"},
        )
        with self.app.app_context():
            database = self.app.get_db()
            draft = database.execute(
                "SELECT answer_json, answer_locked_at FROM nerd_answers WHERE member_id = 1"
            ).fetchone()
            self.assertEqual(json.loads(draft[0]), "Nur ein Entwurf")
            self.assertIsNone(draft[1])
            database.execute(
                "UPDATE nerd_lobbies SET paused_at = ? WHERE id = 1",
                ((datetime.now() - timedelta(seconds=10)).isoformat(),),
            )
            database.commit()
        host.post("/nerd/1/pause", data={"csrf_token": token})
        with self.app.app_context():
            after = self.app.get_db().execute(
                "SELECT phase_ends_at FROM nerd_rounds WHERE lobby_id = 1"
            ).fetchone()[0]
        self.assertGreater((datetime.fromisoformat(after) - datetime.fromisoformat(before)).total_seconds(), 9)

    def test_host_can_replace_a_known_question_in_the_same_round(self):
        self.create_started_lobby()
        host, token = self.clients[0]
        host_page = host.get("/nerd/1").data.decode()
        guest_page = self.clients[1][0].get("/nerd/1").data.decode()
        self.assertIn("nächste frage", host_page)
        self.assertIn("perfect-host-round-controls", host_page)
        self.assertNotIn("nächste frage", guest_page)

        with self.app.app_context():
            database = self.app.get_db()
            before = database.execute(
                "SELECT * FROM nerd_rounds WHERE lobby_id = 1"
            ).fetchone()
            before_signature = host.get("/nerd/1/status").get_json()["lobby_signature"]
        host.post(
            "/nerd/1/antwort-entwurf",
            data={"csrf_token": token, "answer": "Diesen Entwurf verwerfen"},
        )
        forbidden = self.clients[1][0].post(
            "/nerd/1/naechste-frage",
            data={"csrf_token": self.clients[1][1]},
        )
        self.assertEqual(forbidden.status_code, 403)

        response = host.post(
            "/nerd/1/naechste-frage",
            data={"csrf_token": token},
        )
        self.assertEqual(response.status_code, 302)
        with self.app.app_context():
            database = self.app.get_db()
            after = database.execute(
                "SELECT * FROM nerd_rounds WHERE lobby_id = 1"
            ).fetchone()
            used_ids = {
                row[0]
                for row in database.execute(
                    "SELECT question_id FROM perfect_question_usage WHERE category = ?",
                    (before["category"],),
                )
            }
            answer_count = database.execute(
                "SELECT COUNT(*) FROM nerd_answers WHERE round_id = ?",
                (after["id"],),
            ).fetchone()[0]
        after_signature = host.get("/nerd/1/status").get_json()["lobby_signature"]
        self.assertEqual(after["id"], before["id"])
        self.assertEqual(after["round_number"], before["round_number"])
        self.assertEqual(after["category"], before["category"])
        self.assertEqual(after["phase"], "question")
        self.assertNotEqual(after["question_id"], before["question_id"])
        self.assertIn(before["question_id"], used_ids)
        self.assertIn(after["question_id"], used_ids)
        self.assertEqual(answer_count, 0)
        self.assertNotEqual(after_signature, before_signature)
        self.assertAlmostEqual(
            (
                datetime.fromisoformat(after["phase_ends_at"])
                - datetime.fromisoformat(after["phase_started_at"])
            ).total_seconds(),
            PERFECT_ANSWER_SECONDS,
            delta=0.1,
        )

    def test_timeout_locks_saved_answer_and_vote_drafts(self):
        self.create_started_lobby()
        host, token = self.clients[0]
        response = host.post(
            "/nerd/1/antwort-entwurf",
            data={"csrf_token": token, "answer": "Mein nicht abgesendeter Entwurf"},
        )
        self.assertEqual(response.status_code, 200)
        self.force_phase_end()
        with self.app.app_context():
            database = self.app.get_db()
            saved = database.execute(
                "SELECT answer_json, answer_locked_at FROM nerd_answers WHERE member_id = 1"
            ).fetchone()
        self.assertEqual(json.loads(saved[0]), "Mein nicht abgesendeter Entwurf")
        self.assertIsNotNone(saved[1])
        vote_page = host.get("/nerd/1").data.decode()
        self.assertIn("Mein nicht abgesendeter Entwurf", vote_page)

        response = host.post(
            "/nerd/1/wahl-entwurf",
            data={"csrf_token": token, "vote_key": "solution"},
        )
        self.assertEqual(response.status_code, 200)
        host.post("/nerd/1/pause", data={"csrf_token": token})
        with self.app.app_context():
            paused_vote = self.app.get_db().execute(
                "SELECT draft_vote_key, vote_key, vote_locked_at FROM nerd_answers WHERE member_id = 1"
            ).fetchone()
        self.assertEqual(tuple(paused_vote), ("solution", None, None))
        host.post("/nerd/1/pause", data={"csrf_token": token})
        self.force_phase_end()
        with self.app.app_context():
            locked_vote = self.app.get_db().execute(
                "SELECT vote_key, vote_locked_at FROM nerd_answers WHERE member_id = 1"
            ).fetchone()
        self.assertEqual(locked_vote[0], "solution")
        self.assertIsNotNone(locked_vote[1])

    def test_correct_choice_and_successful_bluff_score_100_points_each(self):
        self.create_started_lobby()
        self.submit_answers()
        self.force_phase_end()
        with self.app.app_context():
            database = self.app.get_db()
            bluffer_answer_id = database.execute(
                "SELECT id FROM nerd_answers WHERE member_id = 2"
            ).fetchone()[0]
        choices = ("solution", "solution", f"answer:{bluffer_answer_id}")
        for (client, token), choice in zip(self.clients, choices):
            client.post(
                "/nerd/1/wahl",
                data={"csrf_token": token, "vote_key": choice},
            )
        self.force_phase_end()
        host, host_token = self.clients[0]
        review_page = host.get("/nerd/1").data.decode()
        self.assertIn("ENTSCHEIDUNG DES GASTGEBERS", review_page)
        guest_review_page = self.clients[1][0].get("/nerd/1").data.decode()
        self.assertIn("Offizielle Auflösung", guest_review_page)
        self.assertIn("Antwort von Bluffer", guest_review_page)
        self.assertIn("Der Gastgeber prüft", guest_review_page)
        host.post("/nerd/1/host-pruefung", data={"csrf_token": host_token})
        with self.app.app_context():
            awards = [
                row[0]
                for row in self.app.get_db().execute(
                    "SELECT points_awarded FROM nerd_answers ORDER BY member_id"
                )
            ]
        self.assertEqual(awards, [100, 200, 0])
        points_page = host.get("/nerd/1").data.decode()
        self.assertIn("Die richtige Auflösung", points_page)
        self.assertIn("+200 Punkte", points_page)
        self.assertIn("Offizielle richtige Antwort", points_page)
        self.assertIn('class="perfect-voters"', points_page)
        self.assertIn("starter-neutral.svg", points_page)

    def test_host_can_mark_an_additional_answer_correct(self):
        self.create_started_lobby()
        self.submit_answers()
        self.force_phase_end()
        with self.app.app_context():
            database = self.app.get_db()
            bluffer_answer_id = database.execute(
                "SELECT id FROM nerd_answers WHERE member_id = 2"
            ).fetchone()[0]
        choices = ("solution", "solution", f"answer:{bluffer_answer_id}")
        for (client, token), choice in zip(self.clients, choices):
            client.post(
                "/nerd/1/wahl",
                data={"csrf_token": token, "vote_key": choice},
            )
        self.force_phase_end()
        host, host_token = self.clients[0]
        host.post(
            "/nerd/1/host-pruefung",
            data={
                "csrf_token": host_token,
                f"equivalent_{bluffer_answer_id}": "on",
            },
        )
        with self.app.app_context():
            awards = [
                row[0]
                for row in self.app.get_db().execute(
                    "SELECT points_awarded FROM nerd_answers ORDER BY member_id"
                )
            ]
        self.assertEqual(awards, [100, 200, 100])

    def test_reaching_the_point_goal_shows_the_final_result(self):
        self.create_started_lobby()
        with self.app.app_context():
            database = self.app.get_db()
            database.execute(
                "UPDATE nerd_lobbies SET goal_mode = 'points', goal_value = 500 WHERE id = 1"
            )
            database.execute("UPDATE nerd_members SET score = 400 WHERE id = 1")
            database.commit()
        self.submit_answers()
        self.force_phase_end()
        for client, token in self.clients:
            client.post(
                "/nerd/1/wahl", data={"csrf_token": token, "vote_key": "solution"}
            )
        self.force_phase_end()
        host, host_token = self.clients[0]
        host.post("/nerd/1/host-pruefung", data={"csrf_token": host_token})
        points_page = host.get("/nerd/1").data.decode()
        self.assertIn("endergebnis zeigen", points_page)
        host.post("/nerd/1/weiter", data={"csrf_token": host_token})
        final_page = host.get("/nerd/1").data.decode()
        self.assertIn("ENDERGEBNIS", final_page)
        self.assertIn("Zurück zu den Lobbys", final_page)

    def test_first_round_does_not_end_a_1500_point_game(self):
        self.create_started_lobby()
        self.submit_answers()
        self.force_phase_end()
        for client, token in self.clients:
            client.post(
                "/nerd/1/wahl", data={"csrf_token": token, "vote_key": "solution"}
            )
        self.force_phase_end()
        host, host_token = self.clients[0]
        host.post("/nerd/1/host-pruefung", data={"csrf_token": host_token})
        points_page = host.get("/nerd/1").data.decode()
        self.assertIn("nächste runde", points_page)
        self.assertNotIn("endergebnis zeigen", points_page)
        host.post("/nerd/1/weiter", data={"csrf_token": host_token})
        with self.app.app_context():
            lobby = self.app.get_db().execute(
                "SELECT status, goal_mode, goal_value, round_index FROM nerd_lobbies WHERE id = 1"
            ).fetchone()
        self.assertEqual(tuple(lobby), ("playing", "points", 1500, 2))

    def test_stale_players_are_not_removed_from_a_running_game(self):
        self.create_started_lobby()
        old = (datetime.now() - timedelta(minutes=2)).isoformat()
        with self.app.app_context():
            database = self.app.get_db()
            database.execute(
                "UPDATE nerd_members SET last_seen_at = ? WHERE lobby_id = 1",
                (old,),
            )
            database.commit()
        self.clients[0][0].get("/nerd/1")
        with self.app.app_context():
            statuses = [
                row[0]
                for row in self.app.get_db().execute(
                    "SELECT status FROM nerd_members WHERE lobby_id = 1 ORDER BY id"
                )
            ]
        self.assertEqual(statuses, ["active", "active", "active"])

    def test_round_eight_is_not_a_fixed_ending_anymore(self):
        self.create_started_lobby()
        self.submit_answers()
        self.force_phase_end()
        for client, token in self.clients:
            client.post(
                "/nerd/1/wahl", data={"csrf_token": token, "vote_key": "solution"}
            )
        self.force_phase_end()
        host, host_token = self.clients[0]
        host.post("/nerd/1/host-pruefung", data={"csrf_token": host_token})
        with self.app.app_context():
            database = self.app.get_db()
            database.execute(
                "UPDATE nerd_lobbies SET round_index = 8, goal_mode = 'points', goal_value = 5000 WHERE id = 1"
            )
            database.commit()
        host.post("/nerd/1/weiter", data={"csrf_token": host_token})
        with self.app.app_context():
            lobby = self.app.get_db().execute(
                "SELECT status, round_index FROM nerd_lobbies WHERE id = 1"
            ).fetchone()
        self.assertEqual(tuple(lobby), ("playing", 9))

    def test_time_game_ends_after_the_current_round(self):
        self.create_started_lobby()
        with self.app.app_context():
            database = self.app.get_db()
            expired = (datetime.now() - timedelta(minutes=6)).isoformat()
            database.execute(
                """
                UPDATE nerd_lobbies SET goal_mode = 'time', goal_value = 5,
                       started_at = ? WHERE id = 1
                """,
                (expired,),
            )
            database.commit()
        self.submit_answers()
        self.force_phase_end()
        for client, token in self.clients:
            client.post(
                "/nerd/1/wahl", data={"csrf_token": token, "vote_key": "solution"}
            )
        self.force_phase_end()
        host, host_token = self.clients[0]
        host.post("/nerd/1/host-pruefung", data={"csrf_token": host_token})
        points_page = host.get("/nerd/1").data.decode()
        self.assertIn("endergebnis zeigen", points_page)
        host.post("/nerd/1/weiter", data={"csrf_token": host_token})
        with self.app.app_context():
            status = self.app.get_db().execute(
                "SELECT status FROM nerd_lobbies WHERE id = 1"
            ).fetchone()[0]
        self.assertEqual(status, "completed")


if __name__ == "__main__":
    unittest.main()
