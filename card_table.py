from __future__ import annotations

import json
import secrets
import sqlite3
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable

from flask import abort, current_app, flash, g, redirect, render_template, request, url_for


CARD_TABLE_MAX_PLAYERS = 6
CARD_TABLE_ACTION_SECONDS = 1
CARD_TABLE_PRESENCE_WRITE_SECONDS = 3
CARD_TABLE_DECKS = {
    32: "32 Karten",
    52: "52 Karten",
    55: "52 Karten + 3 Joker",
    104: "104 Karten",
    110: "110 Karten + 6 Joker",
}
SUITS = (
    ("clubs", "♣", "black"),
    ("spades", "♠", "black"),
    ("hearts", "♥", "red"),
    ("diamonds", "♦", "red"),
)
RANKS = ("2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A")


def _db() -> sqlite3.Connection:
    return current_app.get_db()  # type: ignore[attr-defined]


def _now() -> datetime:
    return datetime.now()


def _iso(value: datetime | None = None) -> str:
    return (value or _now()).isoformat(timespec="microseconds")


def init_card_table_db(get_db: Callable[[], sqlite3.Connection]) -> None:
    database = get_db()
    database.executescript(
        """
        CREATE TABLE IF NOT EXISTS card_table_lobbies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            host_user_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'waiting',
            deck_size INTEGER NOT NULL DEFAULT 52,
            starting_points INTEGER,
            state_json TEXT,
            note_text TEXT NOT NULL DEFAULT '',
            action_json TEXT,
            revision INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            started_at TEXT,
            completed_at TEXT,
            FOREIGN KEY(host_user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS card_table_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lobby_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            joined_at TEXT NOT NULL,
            last_seen_at TEXT,
            UNIQUE(lobby_id, user_id),
            FOREIGN KEY(lobby_id) REFERENCES card_table_lobbies(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE INDEX IF NOT EXISTS card_table_members_lobby_idx
            ON card_table_members(lobby_id);
        """
    )
    lobby_columns = {
        row["name"]
        for row in database.execute("PRAGMA table_info(card_table_lobbies)").fetchall()
    }
    if "starting_points" not in lobby_columns:
        database.execute("ALTER TABLE card_table_lobbies ADD COLUMN starting_points INTEGER")
    database.commit()


def _lobby(lobby_id: int) -> sqlite3.Row | None:
    return _db().execute(
        "SELECT * FROM card_table_lobbies WHERE id = ?", (lobby_id,)
    ).fetchone()


def _member(lobby_id: int, user_id: int) -> sqlite3.Row | None:
    return _db().execute(
        "SELECT * FROM card_table_members WHERE lobby_id = ? AND user_id = ?",
        (lobby_id, user_id),
    ).fetchone()


def _members(lobby_id: int) -> list[sqlite3.Row]:
    return _db().execute(
        """
        SELECT cm.*, u.display_name
        FROM card_table_members cm JOIN users u ON u.id = cm.user_id
        WHERE cm.lobby_id = ? AND cm.status = 'active'
        ORDER BY cm.joined_at, cm.id
        """,
        (lobby_id,),
    ).fetchall()


def _touch(lobby_id: int, user_id: int) -> None:
    now = _now()
    member = _db().execute(
        """
        SELECT COALESCE(last_seen_at, joined_at) AS seen_at
        FROM card_table_members
        WHERE lobby_id = ? AND user_id = ? AND status = 'active'
        """,
        (lobby_id, user_id),
    ).fetchone()
    if member and now - datetime.fromisoformat(member["seen_at"]) >= timedelta(
        seconds=CARD_TABLE_PRESENCE_WRITE_SECONDS
    ):
        _db().execute(
            """
            UPDATE card_table_members SET last_seen_at = ?
            WHERE lobby_id = ? AND user_id = ? AND status = 'active'
            """,
            (_iso(now), lobby_id, user_id),
        )
        _db().commit()


def _refresh_presence(lobby_id: int | None = None) -> None:
    """Card-table seats persist until a player explicitly leaves the lobby."""

    database = _db()
    lobby_filter = " AND ctl.id = ?" if lobby_id is not None else ""
    params = (lobby_id,) if lobby_id is not None else ()
    database.execute(
        f"""
        UPDATE card_table_members
        SET status = 'active'
        WHERE status = 'away' AND lobby_id IN (
            SELECT ctl.id FROM card_table_lobbies ctl
            WHERE ctl.status IN ('waiting', 'playing'){lobby_filter}
        )
        """,
        params,
    )
    database.commit()


def _require_active(lobby_id: int) -> tuple[sqlite3.Row, sqlite3.Row]:
    lobby = _lobby(lobby_id)
    member = _member(lobby_id, g.user["id"])
    if not lobby or not member or member["status"] != "active":
        abort(404)
    _touch(lobby_id, g.user["id"])
    _refresh_presence(lobby_id)
    lobby = _lobby(lobby_id)
    return lobby, member


def _build_deck(size: int) -> list[dict[str, Any]]:
    copies = 2 if size in (104, 110) else 1
    ranks = RANKS[-8:] if size == 32 else RANKS
    cards: list[dict[str, Any]] = []
    for copy in range(1, copies + 1):
        for suit, symbol, color in SUITS:
            for rank in ranks:
                cards.append(
                    {
                        "id": f"d{copy}-{suit}-{rank}",
                        "rank": rank,
                        "suit": suit,
                        "symbol": symbol,
                        "color": color,
                        "joker": False,
                        "zone": "deck",
                        "face_up": False,
                        "x": 50,
                        "y": 50,
                        "z": len(cards) + 1,
                        "rotation": 0,
                    }
                )
        joker_count = 3 if size in (55, 110) else 0
        for joker in range(1, joker_count + 1):
            cards.append(
                {
                    "id": f"d{copy}-joker-{joker}",
                    "rank": "JOKER",
                    "suit": "joker",
                    "symbol": "★",
                    "color": "red" if joker % 2 else "black",
                    "joker": True,
                    "zone": "deck",
                    "face_up": False,
                    "x": 50,
                    "y": 50,
                    "z": len(cards) + 1,
                    "rotation": 0,
                }
            )
    secrets.SystemRandom().shuffle(cards)
    for index, card in enumerate(cards, 1):
        card["z"] = index
    return cards


def _state(lobby: sqlite3.Row) -> dict[str, Any]:
    if not lobby["state_json"]:
        return {"cards": []}
    return json.loads(lobby["state_json"])


def _cards_for_viewer(
    cards: list[dict[str, Any]], viewer_member_id: int, *, reveal_all: bool = False
) -> list[dict[str, Any]]:
    """Expose a player's desk only to that player, including at JSON level."""

    visible: list[dict[str, Any]] = []
    own_zone = f"player:{viewer_member_id}"
    for source in cards:
        card = dict(source)
        if not reveal_all and card["zone"] == own_zone:
            card["face_up"] = True
        elif not reveal_all and (
            card["zone"].startswith("player:") or not card["face_up"]
        ):
            card["face_up"] = False
            card.update(
                rank=None,
                suit=None,
                symbol=None,
                color="black",
                joker=False,
            )
        visible.append(card)
    return visible


def _save_state(lobby_id: int, state: dict[str, Any], *, action: Any = None) -> None:
    _db().execute(
        """
        UPDATE card_table_lobbies
        SET state_json = ?, action_json = ?, revision = revision + 1
        WHERE id = ?
        """,
        (
            json.dumps(state, ensure_ascii=False, separators=(",", ":")),
            json.dumps(action, ensure_ascii=False) if action else None,
            lobby_id,
        ),
    )
    _db().commit()


def _finish_action(lobby: sqlite3.Row) -> sqlite3.Row:
    if not lobby["action_json"]:
        return lobby
    action = json.loads(lobby["action_json"])
    if _now() < datetime.fromisoformat(action["ends_at"]):
        return lobby
    state = _state(lobby)
    cards = state["cards"]
    if action["type"] == "collect":
        for index, card in enumerate(cards, 1):
            card.update(
                zone="discard",
                face_up=True,
                x=50,
                y=50,
                z=index,
                rotation=secrets.randbelow(13) - 6,
            )
    elif action["type"] == "shuffle":
        shuffled = [card for card in cards if card["zone"] == "discard"]
        secrets.SystemRandom().shuffle(shuffled)
        for index, card in enumerate(shuffled, 1):
            card.update(
                zone="deck", face_up=False, x=50, y=50, z=index, rotation=0
            )
    _save_state(lobby["id"], state)
    return _lobby(lobby["id"])  # type: ignore[return-value]


def _lobby_rows(user_id: int) -> list[sqlite3.Row]:
    return _db().execute(
        """
        SELECT ctl.*, u.display_name AS host_name,
               COUNT(CASE WHEN ctm.status = 'active' THEN 1 END) AS member_count,
               MAX(CASE WHEN ctm.user_id = ? AND ctm.status = 'active' THEN 1 ELSE 0 END) AS is_member
        FROM card_table_lobbies ctl
        JOIN users u ON u.id = ctl.host_user_id
        LEFT JOIN card_table_members ctm ON ctm.lobby_id = ctl.id
        WHERE ctl.status IN ('waiting', 'playing')
        GROUP BY ctl.id
        ORDER BY ctl.created_at DESC
        """,
        (user_id,),
    ).fetchall()


def register_card_table_routes(
    app: Any,
    login_required: Callable[[Callable[..., Any]], Callable[..., Any]],
    require_csrf: Callable[[], None],
) -> None:
    def active_view(view: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(view)
        def wrapped(lobby_id: int, *args: Any, **kwargs: Any) -> Any:
            _require_active(lobby_id)
            return view(lobby_id, *args, **kwargs)

        return wrapped

    @app.get("/karten")
    @login_required
    def tabletop_connection() -> Any:
        return render_template("tabletop_connection.html")

    @app.get("/karten/kartentische")
    @login_required
    def card_tables() -> Any:
        return render_template("tabletop_family.html", family="cards")

    @app.get("/karten/kartentisch")
    @login_required
    def card_table_index() -> Any:
        _refresh_presence()
        return render_template("card_table_index.html", lobbies=_lobby_rows(g.user["id"]))

    @app.post("/karten/erstellen")
    @login_required
    def card_table_create() -> Any:
        require_csrf()
        database = _db()
        own = database.execute(
            """
            SELECT ctl.id FROM card_table_lobbies ctl
            JOIN card_table_members ctm ON ctm.lobby_id = ctl.id
            WHERE ctm.user_id = ? AND ctm.status = 'active'
              AND ctl.status IN ('waiting', 'playing')
            """,
            (g.user["id"],),
        ).fetchone()
        if own:
            return redirect(url_for("card_table_lobby", lobby_id=own["id"]))
        now = _iso()
        lobby_id = database.execute(
            """
            INSERT INTO card_table_lobbies (name, host_user_id, created_at)
            VALUES (?, ?, ?)
            """,
            (f"{g.user['display_name']}´s Playtable", g.user["id"], now),
        ).lastrowid
        database.execute(
            """
            INSERT INTO card_table_members (lobby_id, user_id, joined_at, last_seen_at)
            VALUES (?, ?, ?, ?)
            """,
            (lobby_id, g.user["id"], now, now),
        )
        database.commit()
        return redirect(url_for("card_table_lobby", lobby_id=lobby_id))

    @app.post("/karten/<int:lobby_id>/beitreten")
    @login_required
    def card_table_join(lobby_id: int) -> Any:
        require_csrf()
        lobby = _lobby(lobby_id)
        members = _members(lobby_id) if lobby else []
        if not lobby or lobby["status"] != "waiting" or len(members) >= CARD_TABLE_MAX_PLAYERS:
            flash("Diese Playtable ist gerade nicht verfügbar.", "error")
            return redirect(url_for("card_table_index"))
        own = _db().execute(
            """
            SELECT ctl.id FROM card_table_lobbies ctl
            JOIN card_table_members ctm ON ctm.lobby_id = ctl.id
            WHERE ctm.user_id = ? AND ctm.status = 'active'
              AND ctl.status IN ('waiting', 'playing') AND ctl.id != ?
            """,
            (g.user["id"], lobby_id),
        ).fetchone()
        if own:
            return redirect(url_for("card_table_lobby", lobby_id=own["id"]))
        existing = _member(lobby_id, g.user["id"])
        now = _iso()
        if existing:
            _db().execute(
                "UPDATE card_table_members SET status = 'active', last_seen_at = ? WHERE id = ?",
                (now, existing["id"]),
            )
        else:
            _db().execute(
                """
                INSERT INTO card_table_members (lobby_id, user_id, joined_at, last_seen_at)
                VALUES (?, ?, ?, ?)
                """,
                (lobby_id, g.user["id"], now, now),
            )
        _db().execute(
            "UPDATE card_table_lobbies SET revision = revision + 1 WHERE id = ?",
            (lobby_id,),
        )
        _db().commit()
        return redirect(url_for("card_table_lobby", lobby_id=lobby_id))

    @app.post("/karten/<int:lobby_id>/einstellungen")
    @login_required
    @active_view
    def card_table_settings(lobby_id: int) -> Any:
        require_csrf()
        lobby = _lobby(lobby_id)
        if not lobby or lobby["host_user_id"] != g.user["id"] or lobby["status"] != "waiting":
            abort(403)
        deck_size = request.form.get("deck_size", type=int)
        if deck_size not in CARD_TABLE_DECKS:
            abort(400)
        points_text = request.form.get("starting_points", "").strip()
        starting_points = None if not points_text else request.form.get("starting_points", type=int)
        if starting_points is not None and not 1 <= starting_points <= 1_000_000_000:
            abort(400)
        _db().execute(
            "UPDATE card_table_lobbies SET deck_size = ?, starting_points = ?, revision = revision + 1 WHERE id = ?",
            (deck_size, starting_points, lobby_id),
        )
        _db().commit()
        return redirect(url_for("card_table_lobby", lobby_id=lobby_id))

    @app.post("/karten/<int:lobby_id>/starten")
    @login_required
    @active_view
    def card_table_start(lobby_id: int) -> Any:
        require_csrf()
        lobby = _lobby(lobby_id)
        if not lobby or lobby["host_user_id"] != g.user["id"] or lobby["status"] != "waiting":
            abort(403)
        deck_size = request.form.get("deck_size", type=int) or lobby["deck_size"]
        if deck_size not in CARD_TABLE_DECKS:
            abort(400)
        points_text = request.form.get("starting_points", "").strip()
        starting_points = None if not points_text else request.form.get("starting_points", type=int)
        if starting_points is not None and not 1 <= starting_points <= 1_000_000_000:
            abort(400)
        members = _members(lobby_id)
        state: dict[str, Any] = {"cards": _build_deck(deck_size)}
        if starting_points is not None:
            state["bankroll"] = {
                "balances": {str(row["id"]): starting_points for row in members},
                "bids": {str(row["id"]): 0 for row in members},
                "pot": 0,
                "claim": None,
            }
        _db().execute(
            """
            UPDATE card_table_lobbies
            SET status = 'playing', deck_size = ?, starting_points = ?, state_json = ?, started_at = ?, revision = revision + 1
            WHERE id = ?
            """,
            (deck_size, starting_points, json.dumps(state, ensure_ascii=False), _iso(), lobby_id),
        )
        _db().commit()
        return redirect(url_for("card_table_lobby", lobby_id=lobby_id))

    @app.get("/karten/<int:lobby_id>")
    @login_required
    @active_view
    def card_table_lobby(lobby_id: int) -> Any:
        lobby = _finish_action(_lobby(lobby_id))  # type: ignore[arg-type]
        members = _members(lobby_id)
        if lobby["status"] == "waiting":
            return render_template(
                "card_table_lobby.html",
                lobby=lobby,
                members=members,
                deck_choices=CARD_TABLE_DECKS,
            )
        if lobby["status"] != "playing":
            return redirect(url_for("card_table_index"))
        current_member = _member(lobby_id, g.user["id"])
        own_index = next(
            index for index, row in enumerate(members) if row["id"] == current_member["id"]
        )
        # Every screen keeps its owner at the lower edge, but rotates the same
        # canonical join order around that owner. This preserves who sits next
        # to whom instead of shifting unrelated players into arbitrary seats.
        other_members = members[own_index + 1 :] + members[:own_index]
        return render_template(
            "card_table_game.html",
            lobby=lobby,
            members=members,
            other_members=other_members,
            member=current_member,
        )

    @app.get("/karten/<int:lobby_id>/status")
    @login_required
    @active_view
    def card_table_status(lobby_id: int) -> Any:
        lobby = _finish_action(_lobby(lobby_id))  # type: ignore[arg-type]
        member = _member(lobby_id, g.user["id"])
        if lobby["status"] not in ("waiting", "playing"):
            return {"status": "completed"}, 410
        members = _members(lobby_id)
        payload: dict[str, Any] = {
            "status": lobby["status"],
            "revision": lobby["revision"],
            "host_user_id": lobby["host_user_id"],
            "deck_size": lobby["deck_size"],
            "note": lobby["note_text"],
            "action": json.loads(lobby["action_json"]) if lobby["action_json"] else None,
            "members": [{"id": row["id"], "name": row["display_name"]} for row in members],
        }
        if lobby["status"] == "playing":
            action = payload["action"]
            state = _state(lobby)
            payload["cards"] = _cards_for_viewer(
                state["cards"],
                member["id"],
                reveal_all=bool(action and action["type"] == "collect"),
            )
            payload["bankroll"] = state.get("bankroll")
        return payload

    @app.post("/karten/<int:lobby_id>/aktion")
    @login_required
    @active_view
    def card_table_action(lobby_id: int) -> Any:
        require_csrf()
        database = _db()
        database.execute("BEGIN IMMEDIATE")
        lobby = _finish_action(_lobby(lobby_id))  # type: ignore[arg-type]
        if lobby["status"] != "playing" or lobby["action_json"]:
            database.rollback()
            return {"ok": False}, 409
        state = _state(lobby)
        cards = state["cards"]
        action_type = request.form.get("action", "")
        if action_type == "move":
            card = next((item for item in cards if item["id"] == request.form.get("card_id")), None)
            zone = request.form.get("zone", "")
            current_member = _member(lobby_id, g.user["id"])
            own_zone = f"player:{current_member['id']}"
            allowed_zones = {"table", own_zone}
            if not card or zone not in allowed_zones:
                database.rollback()
                abort(400)
            if card["zone"].startswith("player:") and card["zone"] != own_zone:
                database.rollback()
                abort(403)
            if card["zone"] in ("deck", "discard"):
                top = max((item for item in cards if item["zone"] == card["zone"]), key=lambda item: item["z"], default=None)
                if not top or top["id"] != card["id"]:
                    database.rollback()
                    return {"ok": False, "reason": "top-card-only"}, 409
            try:
                x = max(5.0, min(95.0, float(request.form.get("x", "50"))))
                y = max(8.0, min(92.0, float(request.form.get("y", "50"))))
            except ValueError:
                x, y = 50.0, 50.0
            card.update(
                zone=zone,
                x=x,
                y=y,
                z=max((item["z"] for item in cards), default=0) + 1,
                rotation=secrets.randbelow(9) - 4 if zone in ("table", "discard") else 0,
            )
            if zone in ("deck", "table") or zone.startswith("player:"):
                card["face_up"] = False
            elif zone == "discard":
                card["face_up"] = True
            _save_state(lobby_id, state)
        elif action_type == "flip":
            card = next((item for item in cards if item["id"] == request.form.get("card_id")), None)
            if not card or card["zone"] != "table":
                database.rollback()
                abort(400)
            card["face_up"] = not card["face_up"]
            card["z"] = max((item["z"] for item in cards), default=0) + 1
            _save_state(lobby_id, state)
        elif action_type == "deal":
            members = _members(lobby_id)
            deck = sorted(
                (card for card in cards if card["zone"] == "deck"),
                key=lambda card: card["z"],
                reverse=True,
            )
            count = request.form.get("count", default=1, type=int) or 1
            maximum = len(deck) // len(members) if members else 0
            if count < 1 or count > maximum:
                database.rollback()
                return {"ok": False, "reason": "not-enough-cards"}, 409
            next_z = max((item["z"] for item in cards), default=0)
            deck_index = 0
            for round_index in range(count):
                for member_row in members:
                    zone = f"player:{member_row['id']}"
                    hand_size = sum(item["zone"] == zone for item in cards)
                    card = deck[deck_index]
                    deck_index += 1
                    next_z += 1
                    card.update(
                        zone=zone,
                        face_up=False,
                        x=min(94, 10 + hand_size * 5),
                        y=58,
                        z=next_z,
                        rotation=0,
                    )
            _save_state(lobby_id, state)
        elif action_type == "clear_table":
            table_cards = [card for card in cards if card["zone"] == "table"]
            if not table_cards:
                database.rollback()
                return {"ok": False, "reason": "table-empty"}, 409
            next_z = max((item["z"] for item in cards), default=0)
            for card in table_cards:
                next_z += 1
                card.update(
                    zone="discard",
                    face_up=True,
                    x=50,
                    y=50,
                    z=next_z,
                    rotation=secrets.randbelow(13) - 6,
                )
            _save_state(lobby_id, state)
        elif action_type == "bid":
            bankroll = state.get("bankroll")
            amount = request.form.get("amount", type=int)
            member = _member(lobby_id, g.user["id"])
            member_key = str(member["id"])
            if not bankroll or amount is None or amount < 1:
                database.rollback()
                abort(400)
            balance = int(bankroll["balances"].get(member_key, 0))
            if amount > balance:
                database.rollback()
                return {"ok": False, "reason": "insufficient-balance"}, 409
            bankroll["balances"][member_key] = balance - amount
            bankroll["bids"][member_key] = int(bankroll["bids"].get(member_key, 0)) + amount
            bankroll["pot"] = int(bankroll.get("pot", 0)) + amount
            _save_state(lobby_id, state)
        elif action_type in ("claim_pot", "vote_pot"):
            bankroll = state.get("bankroll")
            member = _member(lobby_id, g.user["id"])
            if not bankroll or int(bankroll.get("pot", 0)) < 1:
                database.rollback()
                return {"ok": False, "reason": "empty-pot"}, 409
            active_ids = {str(row["id"]) for row in _members(lobby_id)}
            member_key = str(member["id"])
            claim = bankroll.get("claim")
            if action_type == "claim_pot":
                if claim:
                    database.rollback()
                    return {"ok": False, "reason": "claim-active"}, 409
                claim = {"requester": member_key, "approvals": [member_key]}
                bankroll["claim"] = claim
            else:
                if not claim or member_key == str(claim["requester"]):
                    database.rollback()
                    abort(400)
                vote = request.form.get("vote")
                if vote == "reject":
                    bankroll["claim"] = None
                    _save_state(lobby_id, state)
                    return {"ok": True}
                if vote != "approve":
                    database.rollback()
                    abort(400)
                approvals = {str(value) for value in claim.get("approvals", [])}
                approvals.add(member_key)
                claim["approvals"] = sorted(approvals)
            approvals = {str(value) for value in claim.get("approvals", [])}
            if active_ids.issubset(approvals):
                requester = str(claim["requester"])
                bankroll["balances"][requester] = int(bankroll["balances"].get(requester, 0)) + int(bankroll["pot"])
                bankroll["pot"] = 0
                bankroll["bids"] = {key: 0 for key in bankroll["balances"]}
                bankroll["claim"] = None
            _save_state(lobby_id, state)
        elif action_type == "collect":
            for card in cards:
                card["face_up"] = True
            timed = {"type": "collect", "started_at": _iso(), "ends_at": _iso(_now() + timedelta(seconds=CARD_TABLE_ACTION_SECONDS))}
            _save_state(lobby_id, state, action=timed)
        elif action_type == "shuffle":
            if not any(card["zone"] == "discard" for card in cards):
                database.rollback()
                return {"ok": False}, 409
            timed = {"type": "shuffle", "started_at": _iso(), "ends_at": _iso(_now() + timedelta(seconds=CARD_TABLE_ACTION_SECONDS))}
            _save_state(lobby_id, state, action=timed)
        elif action_type == "note":
            lines = request.form.get("note", "").replace("\r", "").split("\n")[:8]
            note = "\n".join(line[:40] for line in lines)
            database.execute(
                "UPDATE card_table_lobbies SET note_text = ?, revision = revision + 1 WHERE id = ?",
                (note, lobby_id),
            )
            database.commit()
        else:
            database.rollback()
            abort(400)
        return {"ok": True}

    @app.post("/karten/<int:lobby_id>/verlassen")
    @login_required
    @active_view
    def card_table_leave(lobby_id: int) -> Any:
        require_csrf()
        lobby = _lobby(lobby_id)
        member = _member(lobby_id, g.user["id"])
        _db().execute("UPDATE card_table_members SET status = 'left' WHERE id = ?", (member["id"],))
        remaining = _members(lobby_id)
        if not remaining:
            _db().execute(
                "UPDATE card_table_lobbies SET status = 'abandoned', completed_at = ? WHERE id = ?",
                (_iso(), lobby_id),
            )
        elif lobby["host_user_id"] == g.user["id"]:
            _db().execute(
                "UPDATE card_table_lobbies SET host_user_id = ?, revision = revision + 1 WHERE id = ?",
                (remaining[0]["user_id"], lobby_id),
            )
        else:
            _db().execute(
                "UPDATE card_table_lobbies SET revision = revision + 1 WHERE id = ?",
                (lobby_id,),
            )
        _db().commit()
        return redirect(url_for("card_table_index"))

    @app.post("/karten/<int:lobby_id>/beenden")
    @login_required
    @active_view
    def card_table_end(lobby_id: int) -> Any:
        require_csrf()
        lobby = _lobby(lobby_id)
        if lobby["host_user_id"] != g.user["id"]:
            abort(403)
        _db().execute(
            "UPDATE card_table_lobbies SET status = 'completed', completed_at = ?, revision = revision + 1 WHERE id = ?",
            (_iso(), lobby_id),
        )
        _db().commit()
        return redirect(url_for("card_table_index"))
