import json
import re
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from app import create_app


class CardTableTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "card-table-test",
                "CARD_TABLE_ENABLED": True,
                "DATABASE": str(Path(self.tempdir.name) / "test.sqlite3"),
            }
        )
        self.clients = []
        self.lobby_id = None
        with self.app.app_context():
            database = self.app.get_db()
            for index, name in enumerate(("Host", "Gast", "Dritter"), 1):
                user_id = database.execute(
                    """
                    INSERT INTO users (username, display_name, pin_hash, created_at)
                    VALUES (?, ?, 'unused', ?)
                    """,
                    (name.casefold(), name, datetime.now().isoformat()),
                ).lastrowid
                client = self.app.test_client()
                token = f"card-token-{index}"
                with client.session_transaction() as player_session:
                    player_session["user_id"] = user_id
                    player_session["csrf_token"] = token
                    player_session["login_recorded_on"] = datetime.now().date().isoformat()
                self.clients.append((client, token))
            database.commit()

    def tearDown(self):
        self.tempdir.cleanup()

    def create_lobby(self, *, deck_size=52, guests=1, starting_points=None):
        host, token = self.clients[0]
        response = host.post("/karten/erstellen", data={"csrf_token": token})
        self.assertEqual(response.status_code, 302)
        self.lobby_id = int(response.headers["Location"].rstrip("/").split("/")[-1])
        for client, guest_token in self.clients[1 : guests + 1]:
            client.post(f"/karten/{self.lobby_id}/beitreten", data={"csrf_token": guest_token})
        host.post(
            f"/karten/{self.lobby_id}/einstellungen",
            data={"csrf_token": token, "deck_size": str(deck_size), "starting_points": "" if starting_points is None else str(starting_points)},
        )

    def start_lobby(self, *, deck_size=52, guests=1, starting_points=None):
        self.create_lobby(deck_size=deck_size, guests=guests, starting_points=starting_points)
        host, token = self.clients[0]
        response = host.post(
            f"/karten/{self.lobby_id}/starten",
            data={"csrf_token": token, "deck_size": str(deck_size), "starting_points": "" if starting_points is None else str(starting_points)},
        )
        self.assertEqual(response.status_code, 302)

    def action(self, client_index, **values):
        client, token = self.clients[client_index]
        values["csrf_token"] = token
        return client.post(f"/karten/{self.lobby_id}/aktion", data=values)

    def state(self):
        return self.clients[0][0].get(f"/karten/{self.lobby_id}/status").get_json()

    def finish_animation(self):
        with self.app.app_context():
            database = self.app.get_db()
            action = json.loads(
                database.execute(
                    "SELECT action_json FROM card_table_lobbies WHERE id = ?",
                    (self.lobby_id,),
                ).fetchone()[0]
            )
            action["ends_at"] = (datetime.now() - timedelta(seconds=1)).isoformat()
            database.execute(
                "UPDATE card_table_lobbies SET action_json = ? WHERE id = ?",
                (json.dumps(action), self.lobby_id),
            )
            database.commit()

    def test_lobby_uses_only_deck_choice_and_lists_members(self):
        self.create_lobby(deck_size=110, guests=2)
        page = self.clients[0][0].get("/karten/1").get_data(as_text=True)
        self.assertIn("110 Karten + 6 Joker", page)
        self.assertIn("Playtable starten", page)
        self.assertIn("Host", page)
        self.assertIn("Gast", page)
        self.assertIn("Dritter", page)
        self.assertNotIn('class="game-header"', page)
        self.assertNotIn("Anzahl der Runden", page)

    def test_lobby_revision_and_member_count_change_when_player_joins(self):
        host, host_token = self.clients[0]
        response = host.post("/karten/erstellen", data={"csrf_token": host_token})
        self.lobby_id = int(response.headers["Location"].rstrip("/").split("/")[-1])
        before = host.get(f"/karten/{self.lobby_id}/status").get_json()
        page = host.get(f"/karten/{self.lobby_id}").get_data(as_text=True)
        self.assertIn('data-member-count="1"', page)

        guest, guest_token = self.clients[1]
        guest.post(f"/karten/{self.lobby_id}/beitreten", data={"csrf_token": guest_token})
        after = host.get(f"/karten/{self.lobby_id}/status").get_json()
        self.assertGreater(after["revision"], before["revision"])
        self.assertEqual(len(after["members"]), 2)

    def test_tabletop_connection_groups_card_and_dice_tables(self):
        page = self.clients[0][0].get("/karten").get_data(as_text=True)
        self.assertIn("Tabletop Connection", page)
        self.assertIn("tabletop-connection-shell", page)
        self.assertNotIn('class="game-header"', page)
        self.assertEqual(page.count('class="tabletop-game-tile'), 4)
        self.assertIn("tabletop-perfect-flyer", page)
        self.assertIn("carousel-stormseeds-perfect-v1.png", page)
        self.assertIn("stormseed´s</small>perfect", page)
        self.assertIn("Oder weißt du etwa, was eine Mansube ist?", page)
        self.assertIn("Zu den Kartentischen", page)
        self.assertIn("Zu den Würfeltischen", page)
        self.assertIn("Stormseed’s Conquest", page)
        self.assertEqual(page.count("is-available"), 4)
        self.assertNotIn('class="tabletop-game-tile is-coming"', page)
        self.assertIn('href="/nerd"', page)
        self.assertIn('href="/karten/kartentische"', page)
        self.assertIn('href="/karten/wuerfeltische"', page)
        self.assertIn('href="/karten/welteroberung"', page)
        self.assertNotIn('href="/karten/kartentisch"', page)
        self.assertNotIn('href="/karten/maexchen"', page)
        self.assertNotIn('href="/karten/wuerfeltisch"', page)

    def test_conquest_entry_opens_lobby_browser(self):
        page = self.clients[0][0].get("/karten/welteroberung").get_data(as_text=True)
        self.assertIn("Stormseed’s Conquest", page)
        self.assertIn("Lobby erstellen", page)
        self.assertIn("conquest-lobby.css", page)
        self.assertTrue(Path("static/conquest-lobby-background-v1.png").is_file())
        self.assertNotIn("conquest-table.js", page)

    def test_card_tables_page_opens_free_standard_card_play(self):
        page = self.clients[0][0].get("/karten/kartentische").get_data(as_text=True)
        self.assertIn("Kartentische", page)
        self.assertIn("tabletop-family-page is-cards", page)
        self.assertEqual(page.count('class="tabletop-game-tile'), 1)
        self.assertIn('href="/karten/kartentisch"', page)
        self.assertIn("Freies Spiel mit allen Standardkarten", page)
        self.assertIn("tabletop-card-table-tile-v1.png", page)
        self.assertIn(
            '<a class="back-link" href="/karten">zurück zu tabletop connection</a>',
            page,
        )

    def test_dice_tables_page_lists_all_four_dice_tables(self):
        page = self.clients[0][0].get("/karten/wuerfeltische").get_data(as_text=True)
        self.assertIn("Würfeltische", page)
        self.assertIn("tabletop-family-page is-dice", page)
        self.assertEqual(page.count('class="tabletop-game-tile'), 4)
        self.assertIn('href="/karten/wuerfeltisch"', page)
        self.assertIn('href="/karten/kniffel"', page)
        self.assertIn('href="/karten/maexchen"', page)
        self.assertIn("Schweinchen", page)
        self.assertEqual(page.count('class="tabletop-game-tile is-coming"'), 1)
        self.assertIn(
            '<a class="back-link" href="/karten">zurück zu tabletop connection</a>',
            page,
        )

    def test_every_viewer_sees_the_same_circular_seat_order(self):
        self.start_lobby(guests=2)
        host_page = self.clients[0][0].get(f"/karten/{self.lobby_id}").get_data(as_text=True)
        guest_page = self.clients[1][0].get(f"/karten/{self.lobby_id}").get_data(as_text=True)
        self.assertIn('data-seat-order="1,2,3"', host_page)
        self.assertIn('data-seat-order="1,2,3"', guest_page)
        self.assertRegex(host_page, re.compile(r"seat-other-1[^>]*>.*?<strong>Gast</strong>", re.S))
        self.assertRegex(host_page, re.compile(r"seat-other-2[^>]*>.*?<strong>Dritter</strong>", re.S))
        self.assertRegex(guest_page, re.compile(r"seat-other-1[^>]*>.*?<strong>Dritter</strong>", re.S))
        self.assertRegex(guest_page, re.compile(r"seat-other-2[^>]*>.*?<strong>Host</strong>", re.S))

    def test_card_table_tile_opens_the_existing_lobby_browser(self):
        page = self.clients[0][0].get("/karten/kartentisch").get_data(as_text=True)
        self.assertIn("Aktive Playtables", page)
        self.assertIn("Lobby erstellen", page)
        self.assertNotIn('class="game-header"', page)
        self.assertIn(
            '<a class="back-link" href="/karten">zurück zu tabletop connection</a>',
            page,
        )
        self.assertNotIn("Zurück zur Übersicht", page)

    def test_every_deck_choice_builds_the_exact_requested_pack(self):
        for deck_size in (32, 52, 55, 104, 110):
            with self.subTest(deck_size=deck_size):
                self.start_lobby(deck_size=deck_size, guests=0)
                state = self.state()
                self.assertEqual(len(state["cards"]), deck_size)
                self.assertEqual(len({card["id"] for card in state["cards"]}), deck_size)
                self.assertTrue(all(card["zone"] == "deck" for card in state["cards"]))
                self.assertTrue(all(not card["face_up"] for card in state["cards"]))
                with self.app.app_context():
                    self.app.get_db().execute("DELETE FROM card_table_members")
                    self.app.get_db().execute("DELETE FROM card_table_lobbies")
                    self.app.get_db().commit()

    def test_game_page_contains_all_areas_a_through_i(self):
        self.start_lobby(guests=2)
        page = self.clients[0][0].get("/karten/1").get_data(as_text=True)
        for letter in "ABCDEFGHI":
            self.assertIn(f">{letter}<", page)
        self.assertIn("data-drop-zone=\"table\"", page)
        self.assertEqual(page.count("data-drop-zone=\"player:"), 3)
        self.assertIn('class="card-player-desk seat-self is-you"', page)
        self.assertIn('data-call-button>Mitgehen</button>', page)
        self.assertEqual(page.count("data-collect-pot="), 1)
        guest_page = self.clients[1][0].get("/karten/1").get_data(as_text=True)
        self.assertIn('data-drop-zone="player:2"', guest_page)
        self.assertRegex(guest_page, r'seat-self is-you" data-drop-zone="player:2"')

    def test_only_top_stack_card_moves_and_zone_controls_visibility(self):
        self.start_lobby()
        cards = self.state()["cards"]
        bottom = min(cards, key=lambda card: card["z"])
        top = max(cards, key=lambda card: card["z"])
        blocked = self.action(1, action="move", card_id=bottom["id"], zone="table", x="20", y="20")
        self.assertEqual(blocked.status_code, 409)
        moved = self.action(1, action="move", card_id=top["id"], zone="table", x="25", y="40")
        self.assertEqual(moved.status_code, 200)
        table_card = next(card for card in self.state()["cards"] if card["id"] == top["id"])
        self.assertEqual(table_card["zone"], "table")
        self.assertFalse(table_card["face_up"])
        self.assertEqual(self.action(0, action="flip", card_id=top["id"]).status_code, 200)
        self.assertTrue(next(card for card in self.state()["cards"] if card["id"] == top["id"])["face_up"])
        self.assertEqual(self.action(1, action="move", card_id=top["id"], zone="player:2", x="50", y="50").status_code, 200)
        desk_card = next(card for card in self.state()["cards"] if card["id"] == top["id"])
        self.assertFalse(desk_card["face_up"])

    def test_only_the_desk_owner_receives_the_card_face(self):
        self.start_lobby()
        initial_host_view = self.state()
        top = max(initial_host_view["cards"], key=lambda card: card["z"])
        self.assertFalse(top["face_up"])
        self.assertIsNone(top["rank"])
        self.assertIsNone(top["suit"])
        self.assertEqual(
            self.action(1, action="move", card_id=top["id"], zone="player:2", x="50", y="50").status_code,
            200,
        )
        host_view = self.clients[0][0].get("/karten/1/status").get_json()
        guest_view = self.clients[1][0].get("/karten/1/status").get_json()
        host_card = next(card for card in host_view["cards"] if card["id"] == top["id"])
        guest_card = next(card for card in guest_view["cards"] if card["id"] == top["id"])
        self.assertFalse(host_card["face_up"])
        self.assertIsNone(host_card["rank"])
        self.assertIsNone(host_card["suit"])
        self.assertTrue(guest_card["face_up"])
        self.assertIsNotNone(guest_card["rank"])
        self.assertIsNotNone(guest_card["suit"])

    def test_deal_gives_each_active_player_one_private_card(self):
        self.start_lobby(deck_size=32, guests=2)
        self.assertEqual(self.action(1, action="deal").status_code, 200)
        state = self.state()
        self.assertEqual(sum(card["zone"] == "deck" for card in state["cards"]), 29)
        for member_id in (1, 2, 3):
            self.assertEqual(
                sum(card["zone"] == f"player:{member_id}" for card in state["cards"]),
                1,
            )
            dealt = next(
                card for card in state["cards"] if card["zone"] == f"player:{member_id}"
            )
            self.assertEqual(dealt["x"], 10)
        self.assertEqual(self.action(0, action="deal").status_code, 200)
        second_state = self.state()
        for member_id in (1, 2, 3):
            x_positions = sorted(
                card["x"]
                for card in second_state["cards"]
                if card["zone"] == f"player:{member_id}"
            )
            self.assertEqual(x_positions, [10, 15])
        page = self.clients[0][0].get("/karten/1").get_data(as_text=True)
        self.assertIn('data-table-action="deal"', page)
        self.assertIn("data-deck-count", page)
        self.assertIn("data-discard-count", page)

    def test_deal_slider_distributes_selected_equal_share(self):
        self.start_lobby(deck_size=32, guests=2)
        response = self.action(0, action="deal", count="4")
        self.assertEqual(response.status_code, 200)
        state = self.state()
        self.assertEqual(sum(card["zone"] == "deck" for card in state["cards"]), 20)
        for member_id in (1, 2, 3):
            hand = [card for card in state["cards"] if card["zone"] == f"player:{member_id}"]
            self.assertEqual(len(hand), 4)
            self.assertEqual(sorted(card["x"] for card in hand), [10, 15, 20, 25])
        self.assertEqual(self.action(0, action="deal", count="7").status_code, 409)
        page = self.clients[0][0].get("/karten/1").get_data(as_text=True)
        self.assertIn("Karten pro Person", page)
        self.assertIn("data-deal-count", page)

    def test_face_down_table_card_is_unknown_until_someone_flips_it(self):
        self.start_lobby()
        top = max(self.state()["cards"], key=lambda card: card["z"])
        self.action(0, action="move", card_id=top["id"], zone="table", x="40", y="50")
        for client, _ in self.clients[:2]:
            hidden = next(
                card
                for card in client.get("/karten/1/status").get_json()["cards"]
                if card["id"] == top["id"]
            )
            self.assertFalse(hidden["face_up"])
            self.assertIsNone(hidden["rank"])
            self.assertIsNone(hidden["symbol"])
        self.action(1, action="flip", card_id=top["id"])
        for client, _ in self.clients[:2]:
            revealed = next(
                card
                for card in client.get("/karten/1/status").get_json()["cards"]
                if card["id"] == top["id"]
            )
            self.assertTrue(revealed["face_up"])
            self.assertIsNotNone(revealed["rank"])
            self.assertIsNotNone(revealed["symbol"])

    def test_collect_then_shuffle_returns_every_card_to_deck_face_down(self):
        self.start_lobby(deck_size=32)
        self.assertEqual(self.action(0, action="collect").status_code, 200)
        self.assertTrue(all(card["face_up"] for card in self.state()["cards"]))
        self.finish_animation()
        collected = self.state()
        self.assertTrue(all(card["zone"] == "discard" for card in collected["cards"]))
        self.assertTrue(all(card["face_up"] for card in collected["cards"]))
        self.assertEqual(self.action(1, action="shuffle").status_code, 200)
        self.finish_animation()
        shuffled = self.state()
        self.assertTrue(all(card["zone"] == "deck" for card in shuffled["cards"]))
        self.assertTrue(all(not card["face_up"] for card in shuffled["cards"]))

    def test_clear_table_moves_only_area_f_to_discard(self):
        self.start_lobby(deck_size=32)
        cards = self.state()["cards"]
        first, second = sorted(cards, key=lambda card: card["z"], reverse=True)[:2]
        self.action(0, action="move", card_id=first["id"], zone="table", x="30", y="40")
        self.action(0, action="move", card_id=second["id"], zone="player:1", x="40", y="50")
        self.assertEqual(self.action(1, action="clear_table").status_code, 200)
        state = self.state()
        cleared = next(card for card in state["cards"] if card["id"] == first["id"])
        hand = next(card for card in state["cards"] if card["id"] == second["id"])
        self.assertEqual(cleared["zone"], "discard")
        self.assertTrue(cleared["face_up"])
        self.assertEqual(hand["zone"], "player:1")

    def test_optional_points_support_private_bids_and_shared_pot(self):
        self.start_lobby(starting_points=1000, guests=2)
        state = self.state()
        self.assertEqual(state["bankroll"]["pot"], 0)
        self.assertEqual(state["bankroll"]["balances"], {"1": 1000, "2": 1000, "3": 1000})
        self.assertEqual(self.action(1, action="bid", amount="10").status_code, 200)
        updated = self.state()["bankroll"]
        self.assertEqual(updated["balances"]["2"], 990)
        self.assertEqual(updated["bids"]["2"], 10)
        self.assertEqual(updated["pot"], 10)
        self.assertEqual(self.action(1, action="bid", amount="991").status_code, 409)
        page = self.clients[0][0].get("/karten/1").get_data(as_text=True)
        self.assertIn("data-bet-control", page)
        self.assertIn("data-card-pot", page)

    def test_pot_collection_requires_unanimous_other_players(self):
        self.start_lobby(starting_points=1000, guests=2)
        self.assertEqual(self.action(0, action="bid", amount="10").status_code, 200)
        self.assertEqual(self.action(1, action="bid", amount="20").status_code, 200)
        self.assertEqual(self.action(1, action="claim_pot").status_code, 200)
        claim = self.state()["bankroll"]["claim"]
        self.assertEqual(claim["requester"], "2")
        self.assertEqual(claim["approvals"], ["2"])
        self.assertEqual(self.action(0, action="vote_pot", vote="approve").status_code, 200)
        self.assertEqual(self.state()["bankroll"]["pot"], 30)
        self.assertEqual(self.action(2, action="vote_pot", vote="approve").status_code, 200)
        bankroll = self.state()["bankroll"]
        self.assertEqual(bankroll["pot"], 0)
        self.assertIsNone(bankroll["claim"])
        self.assertEqual(bankroll["balances"]["2"], 1010)
        self.assertTrue(all(value == 0 for value in bankroll["bids"].values()))

    def test_only_owner_moves_pult_cards_and_destinations_are_limited(self):
        self.start_lobby()
        top = max(self.state()["cards"], key=lambda card: card["z"])
        self.assertEqual(self.action(1, action="move", card_id=top["id"], zone="player:2").status_code, 200)
        self.assertEqual(self.action(0, action="move", card_id=top["id"], zone="table").status_code, 403)
        self.assertEqual(self.action(1, action="move", card_id=top["id"], zone="discard").status_code, 400)
        self.assertEqual(self.action(1, action="move", card_id=top["id"], zone="player:1").status_code, 400)
        self.assertEqual(self.action(1, action="move", card_id=top["id"], zone="table").status_code, 200)

    def test_points_are_absent_when_lobby_field_is_blank(self):
        self.start_lobby(starting_points=None)
        self.assertIsNone(self.state()["bankroll"])
        self.assertEqual(self.action(0, action="bid", amount="1").status_code, 400)

    def test_note_is_shared_and_limited_to_eight_lines_of_forty(self):
        self.start_lobby()
        note = "\n".join(["123456789012345678901234567890123456789012345"] * 10)
        self.assertEqual(self.action(1, action="note", note=note).status_code, 200)
        saved = self.state()["note"]
        self.assertEqual(len(saved.splitlines()), 8)
        self.assertTrue(all(len(line) == 40 for line in saved.splitlines()))

    def test_only_host_can_end_the_lobby(self):
        self.start_lobby()
        guest, guest_token = self.clients[1]
        self.assertEqual(guest.post("/karten/1/beenden", data={"csrf_token": guest_token}).status_code, 403)
        host, host_token = self.clients[0]
        self.assertEqual(host.post("/karten/1/beenden", data={"csrf_token": host_token}).status_code, 302)
        self.assertEqual(host.get("/karten/1/status").status_code, 410)

    def test_stale_members_remain_in_every_lobby_and_presence_writes_are_throttled(self):
        self.create_lobby(guests=1)
        old = (datetime.now() - timedelta(minutes=2)).isoformat()
        with self.app.app_context():
            database = self.app.get_db()
            database.execute(
                "UPDATE card_table_members SET last_seen_at = ? WHERE id = 2",
                (old,),
            )
            database.commit()
        host = self.clients[0][0]
        first = host.get("/karten/1/status")
        self.assertEqual(first.status_code, 200)
        with self.app.app_context():
            database = self.app.get_db()
            self.assertEqual(
                database.execute(
                    "SELECT status FROM card_table_members WHERE id = 2"
                ).fetchone()[0],
                "active",
            )
            touched = database.execute(
                "SELECT last_seen_at FROM card_table_members WHERE id = 1"
            ).fetchone()[0]
        host.get("/karten/1/status")
        with self.app.app_context():
            self.assertEqual(
                self.app.get_db().execute(
                    "SELECT last_seen_at FROM card_table_members WHERE id = 1"
                ).fetchone()[0],
                touched,
            )


if __name__ == "__main__":
    unittest.main()
