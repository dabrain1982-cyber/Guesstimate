from __future__ import annotations

from account_wallet import balance as account_balance

from lobby_overview import render_overview

import json
import secrets
import sqlite3
from datetime import datetime
from functools import wraps
from typing import Any, Callable

from flask import abort, current_app, flash, g, redirect, render_template, request, url_for
from lobby_view import lobby_player_profiles


DICE_TABLE_MAX_PLAYERS = 6
DICE_TABLE_THEME_ID = "outgunned-reimagined-ma8o1nit"
DICE_TABLE_D6_TYPE = "65d8ad5d-ed69-4c48-8ac6-8ff0a1636979"
KNIFFEL_CATEGORIES = (
    ("ones", "Einser"),
    ("twos", "Zweier"),
    ("threes", "Dreier"),
    ("fours", "Vierer"),
    ("fives", "Fünfer"),
    ("sixes", "Sechser"),
    ("three_kind", "Dreierpasch"),
    ("four_kind", "Viererpasch"),
    ("full_house", "Full House"),
    ("small_straight", "Kleine Straße"),
    ("large_straight", "Große Straße"),
    ("five_kind", "Fünferpasch"),
    ("chance", "Chance"),
)
MAEXCHEN_VALUES = (
    "31", "32", "41", "42", "43", "51", "52", "53", "54",
    "61", "62", "63", "64", "65", "11", "22", "33", "44",
    "55", "66", "21",
)


def _db() -> sqlite3.Connection:
    return current_app.get_db()  # type: ignore[attr-defined]


def _now() -> str:
    return datetime.now().isoformat(timespec="microseconds")


def init_dice_table_db(get_db: Callable[[], sqlite3.Connection]) -> None:
    database = get_db()
    database.executescript(
        """
        CREATE TABLE IF NOT EXISTS dice_table_lobbies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            host_user_id INTEGER NOT NULL,
            game_type TEXT NOT NULL DEFAULT 'sandbox',
            status TEXT NOT NULL DEFAULT 'waiting',
            dice_count INTEGER NOT NULL DEFAULT 2,
            use_cup INTEGER NOT NULL DEFAULT 0,
            state_json TEXT,
            revision INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            started_at TEXT,
            completed_at TEXT,
            FOREIGN KEY(host_user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS dice_table_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lobby_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            joined_at TEXT NOT NULL,
            UNIQUE(lobby_id, user_id),
            FOREIGN KEY(lobby_id) REFERENCES dice_table_lobbies(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE INDEX IF NOT EXISTS dice_table_members_lobby_idx
            ON dice_table_members(lobby_id);

        CREATE TABLE IF NOT EXISTS dice_table_preferences (
            user_id INTEGER PRIMARY KEY,
            camera_locked INTEGER NOT NULL DEFAULT 0,
            camera_json TEXT,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """
    )
    lobby_columns = {
        row["name"]
        for row in database.execute("PRAGMA table_info(dice_table_lobbies)").fetchall()
    }
    migrations = {
        "dice_count": "ALTER TABLE dice_table_lobbies ADD COLUMN dice_count INTEGER NOT NULL DEFAULT 2",
        "use_cup": "ALTER TABLE dice_table_lobbies ADD COLUMN use_cup INTEGER NOT NULL DEFAULT 0",
        "state_json": "ALTER TABLE dice_table_lobbies ADD COLUMN state_json TEXT",
        "started_at": "ALTER TABLE dice_table_lobbies ADD COLUMN started_at TEXT",
        "game_type": "ALTER TABLE dice_table_lobbies ADD COLUMN game_type TEXT NOT NULL DEFAULT 'sandbox'",
    }
    for column, statement in migrations.items():
        if column not in lobby_columns:
            database.execute(statement)
    database.commit()


def _lobby(lobby_id: int) -> sqlite3.Row | None:
    return _db().execute(
        "SELECT * FROM dice_table_lobbies WHERE id = ?", (lobby_id,)
    ).fetchone()


def _member(lobby_id: int, user_id: int) -> sqlite3.Row | None:
    return _db().execute(
        "SELECT * FROM dice_table_members WHERE lobby_id = ? AND user_id = ? AND status = 'active'",
        (lobby_id, user_id),
    ).fetchone()


def _members(lobby_id: int) -> list[dict[str, Any]]:
    rows = _db().execute(
        """
        SELECT dm.*, u.display_name,
               COALESCE(uc.avatar_id, 'a00') AS avatar_id,
               COALESCE(uc.plaque_id, 'p00') AS plaque_id,
               COALESCE(uc.background_id, 'b00') AS background_id,
               COALESCE(uc.phrase_id, '') AS phrase_id
        FROM dice_table_members dm
        JOIN users u ON u.id = dm.user_id
        LEFT JOIN user_cosmetics uc ON uc.user_id = u.id
        WHERE dm.lobby_id = ? AND dm.status = 'active'
        ORDER BY dm.joined_at, dm.id
        """,
        (lobby_id,),
    ).fetchall()
    members: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        item["currency_balance"] = account_balance(_db(),row["user_id"],
            current_app.config.get("PREVIEW_CURRENCY_BONUS",0))
        item["cosmetics"] = {
            "avatar_id": row["avatar_id"],
            "plaque_id": row["plaque_id"],
            "background_id": row["background_id"],
            "phrase_id": row["phrase_id"],
        }
        members.append(item)
    return members


def _lobby_rows(user_id: int, game_type: str = "sandbox") -> list[sqlite3.Row]:
    return _db().execute(
        """
        SELECT dl.*, u.display_name AS host_name,
               COUNT(CASE WHEN dm.status = 'active' THEN 1 END) AS member_count,
               MAX(CASE WHEN dm.user_id = ? AND dm.status = 'active' THEN 1 ELSE 0 END) AS is_member
        FROM dice_table_lobbies dl
        JOIN users u ON u.id = dl.host_user_id
        LEFT JOIN dice_table_members dm ON dm.lobby_id = dl.id
        WHERE dl.game_type = ? AND (dl.status = 'waiting'
           OR (dl.status = 'playing' AND EXISTS (
               SELECT 1 FROM dice_table_members own
               WHERE own.lobby_id = dl.id AND own.user_id = ? AND own.status = 'active'
           )))
        GROUP BY dl.id
        ORDER BY dl.created_at DESC
        """,
        (user_id, game_type, user_id),
    ).fetchall()


def _kniffel_state(members: list[dict[str, Any]]) -> dict[str, Any]:
    member_ids = [int(member["id"]) for member in members]
    return {
        "turn_order": member_ids,
        "turn_index": 0,
        "roll_count": 0,
        "scores": {str(member_id): {} for member_id in member_ids},
        "completed": False,
    }


def _maexchen_state(members: list[dict[str, Any]]) -> dict[str, Any]:
    member_ids = [int(member["id"]) for member in members]
    return {
        "turn_order": member_ids,
        "current_member_id": member_ids[0] if member_ids else None,
        "phase": "awaiting_roll",
        "claim": None,
        "claimant_id": None,
        "responder_id": None,
        "lives": {str(member_id): 3 for member_id in member_ids},
        "round_number": 1,
        "round_result": None,
        "winner_id": None,
    }


def _maexchen_value(values: list[int]) -> str:
    high, low = sorted((int(values[0]), int(values[1])), reverse=True)
    return f"{high}{low}"


def _maexchen_rank(value: str) -> int:
    return MAEXCHEN_VALUES.index(value)


def _next_maexchen_member(
    state: dict[str, Any], member_id: int, *, include_swimming: bool = True
) -> int | None:
    order = [int(item) for item in state.get("turn_order", [])]
    if not order:
        return None
    lives = state.setdefault("lives", {})
    start = order.index(member_id) if member_id in order else -1
    for offset in range(1, len(order) + 1):
        candidate = order[(start + offset) % len(order)]
        if int(lives.get(str(candidate), 0)) > 0:
            return candidate
    return None


def _maexchen_apply_loss(
    state: dict[str, Any], loser_id: int, amount: int, members: list[dict[str, Any]]
) -> None:
    lives = state.setdefault("lives", {})
    lives[str(loser_id)] = max(0, int(lives.get(str(loser_id), 3)) - amount)
    alive = [
        int(member["id"])
        for member in members
        if int(lives.get(str(member["id"]), 0)) > 0
    ]
    if len(alive) <= 1:
        state["phase"] = "finished"
        state["winner_id"] = alive[0] if alive else None
        state["current_member_id"] = alive[0] if alive else None
        return
    if int(lives.get(str(loser_id), 0)) > 0:
        state["current_member_id"] = loser_id
    else:
        state["current_member_id"] = _next_maexchen_member(state, loser_id)
    state["phase"] = "round_result"


def _score_kniffel(category: str, values: list[int]) -> int:
    counts = {value: values.count(value) for value in range(1, 7)}
    if category in {"ones", "twos", "threes", "fours", "fives", "sixes"}:
        face = ("ones", "twos", "threes", "fours", "fives", "sixes").index(category) + 1
        return face * counts[face]
    if category == "three_kind":
        return sum(values) if max(counts.values()) >= 3 else 0
    if category == "four_kind":
        return sum(values) if max(counts.values()) >= 4 else 0
    if category == "full_house":
        return 25 if sorted(count for count in counts.values() if count) == [2, 3] else 0
    unique = set(values)
    if category == "small_straight":
        return 30 if any(run <= unique for run in ({1, 2, 3, 4}, {2, 3, 4, 5}, {3, 4, 5, 6})) else 0
    if category == "large_straight":
        return 40 if unique in ({1, 2, 3, 4, 5}, {2, 3, 4, 5, 6}) else 0
    if category == "five_kind":
        return 50 if max(counts.values()) == 5 else 0
    if category == "chance":
        return sum(values)
    raise ValueError("unknown Kniffel category")


def _kniffel_totals(scores: dict[str, int]) -> dict[str, int]:
    upper_keys = ("ones", "twos", "threes", "fours", "fives", "sixes")
    upper = sum(int(scores.get(key, 0)) for key in upper_keys)
    bonus = 35 if upper >= 63 else 0
    lower = sum(int(value) for key, value in scores.items() if key not in upper_keys)
    return {
        "upper": upper,
        "bonus": bonus,
        "upper_total": upper + bonus,
        "lower": lower,
        "total": upper + bonus + lower,
    }


def _normalize_kniffel_turn(
    kniffel: dict[str, Any], members: list[dict[str, Any]]
) -> list[int]:
    old_order = [int(member_id) for member_id in kniffel.get("turn_order", [])]
    old_index = int(kniffel.get("turn_index", 0)) % max(1, len(old_order))
    old_current = old_order[old_index] if old_order else None
    active_ids = [int(item["id"]) for item in members]
    order = [member_id for member_id in old_order if member_id in active_ids]
    order.extend(member_id for member_id in active_ids if member_id not in order)
    kniffel["turn_order"] = order
    if old_current in order:
        kniffel["turn_index"] = order.index(old_current)
    elif order:
        following = [
            old_order[(old_index + offset) % len(old_order)]
            for offset in range(1, len(old_order) + 1)
        ] if old_order else []
        next_member = next((member_id for member_id in following if member_id in order), order[0])
        kniffel["turn_index"] = order.index(next_member)
    else:
        kniffel["turn_index"] = 0
    return order


def _state(lobby: sqlite3.Row) -> dict[str, Any]:
    if not lobby["state_json"]:
        return {"roll": None, "dice": [], "history": {}}
    state = json.loads(lobby["state_json"])
    state.setdefault("dice", [])
    if not state["dice"] and (state.get("roll") or {}).get("values"):
        state["dice"] = [
            {"id": secrets.token_hex(8), "value": value, "zone": "active"}
            for value in state["roll"]["values"]
        ]
        state["roll"]["rolled_ids"] = [die["id"] for die in state["dice"]]
    return state


def _camera_preference(user_id: int) -> dict[str, Any]:
    row = _db().execute(
        "SELECT camera_locked, camera_json FROM dice_table_preferences WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    if not row:
        return {"locked": False, "camera": None}
    try:
        camera = json.loads(row["camera_json"]) if row["camera_json"] else None
    except (TypeError, json.JSONDecodeError):
        camera = None
    return {"locked": bool(row["camera_locked"]), "camera": camera}


def _save_state(lobby_id: int, state: dict[str, Any]) -> None:
    _db().execute(
        "UPDATE dice_table_lobbies SET state_json = ?, revision = revision + 1 WHERE id = ?",
        (json.dumps(state, ensure_ascii=False, separators=(",", ":")), lobby_id),
    )
    _db().commit()


def _history_for_viewer(
    state: dict[str, Any], members: list[dict[str, Any]], viewer_member_id: int
) -> list[dict[str, Any]]:
    history = state.get("history", {})
    rows: list[dict[str, Any]] = []
    for member in members:
        member_id = int(member["id"])
        entries = []
        for entry in history.get(str(member_id), [])[-6:]:
            values = entry.get("values")
            entries.append(
                {
                    "private": bool(entry.get("private")),
                    "values": values
                    if not entry.get("private") or member_id == viewer_member_id
                    else None,
                }
            )
        rows.append({"id": member_id, "name": member["display_name"], "rolls": entries})
    return rows


def register_dice_table_routes(
    app: Any,
    login_required: Callable[[Callable[..., Any]], Callable[..., Any]],
    require_csrf: Callable[[], None],
) -> None:
    def active_view(view: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(view)
        def wrapped(lobby_id: int, *args: Any, **kwargs: Any) -> Any:
            if not _lobby(lobby_id) or not _member(lobby_id, g.user["id"]):
                abort(404)
            return view(lobby_id, *args, **kwargs)

        return wrapped

    @app.get("/karten/wuerfeltische")
    @login_required
    def dice_tables() -> Any:
        return render_template("tabletop_family.html", family="dice")

    @app.get("/karten/wuerfeltisch")
    @login_required
    def dice_table_index() -> Any:
        return render_overview(
            "dice_table_index.html",
            lobbies=_lobby_rows(g.user["id"], "sandbox"),
            game_mode="sandbox",
            lobby_endpoint="dice_table_lobby",
            join_endpoint="dice_table_join",
            create_endpoint="dice_table_create",
        )

    @app.get("/karten/kniffel")
    @login_required
    def kniffel_index() -> Any:
        return render_overview(
            "dice_table_index.html",
            lobbies=_lobby_rows(g.user["id"], "kniffel"),
            game_mode="kniffel",
            lobby_endpoint="kniffel_lobby",
            join_endpoint="kniffel_join",
            create_endpoint="kniffel_create",
        )

    @app.get("/karten/maexchen")
    @login_required
    def maexchen_index() -> Any:
        return render_overview(
            "dice_table_index.html",
            lobbies=_lobby_rows(g.user["id"], "maexchen"),
            game_mode="maexchen",
            lobby_endpoint="maexchen_lobby",
            join_endpoint="maexchen_join",
            create_endpoint="maexchen_create",
        )

    @app.post("/karten/wuerfeltisch/erstellen")
    @login_required
    def dice_table_create() -> Any:
        require_csrf()
        own = _db().execute(
            """
            SELECT dl.id FROM dice_table_lobbies dl
            JOIN dice_table_members dm ON dm.lobby_id = dl.id
            WHERE dm.user_id = ? AND dm.status = 'active'
              AND dl.status IN ('waiting', 'playing') AND dl.game_type = 'sandbox'
            """,
            (g.user["id"],),
        ).fetchone()
        if own:
            return redirect(url_for("dice_table_lobby", lobby_id=own["id"]))
        now = _now()
        lobby_id = _db().execute(
            "INSERT INTO dice_table_lobbies (name, host_user_id, game_type, created_at) VALUES (?, ?, 'sandbox', ?)",
            (f"{g.user['display_name']}´s Würfeltisch", g.user["id"], now),
        ).lastrowid
        _db().execute(
            "INSERT INTO dice_table_members (lobby_id, user_id, joined_at) VALUES (?, ?, ?)",
            (lobby_id, g.user["id"], now),
        )
        _db().commit()
        return redirect(url_for("dice_table_lobby", lobby_id=lobby_id))

    @app.post("/karten/kniffel/erstellen")
    @login_required
    def kniffel_create() -> Any:
        require_csrf()
        own = _db().execute(
            """
            SELECT dl.id FROM dice_table_lobbies dl
            JOIN dice_table_members dm ON dm.lobby_id = dl.id
            WHERE dm.user_id = ? AND dm.status = 'active'
              AND dl.status IN ('waiting', 'playing') AND dl.game_type = 'kniffel'
            """,
            (g.user["id"],),
        ).fetchone()
        if own:
            return redirect(url_for("kniffel_lobby", lobby_id=own["id"]))
        now = _now()
        lobby_id = _db().execute(
            """
            INSERT INTO dice_table_lobbies
                (name, host_user_id, game_type, dice_count, use_cup, created_at)
            VALUES (?, ?, 'kniffel', 5, 0, ?)
            """,
            (f"{g.user['display_name']}´s Kniffeltisch", g.user["id"], now),
        ).lastrowid
        _db().execute(
            "INSERT INTO dice_table_members (lobby_id, user_id, joined_at) VALUES (?, ?, ?)",
            (lobby_id, g.user["id"], now),
        )
        _db().commit()
        return redirect(url_for("kniffel_lobby", lobby_id=lobby_id))

    @app.post("/karten/maexchen/erstellen")
    @login_required
    def maexchen_create() -> Any:
        require_csrf()
        own = _db().execute(
            """
            SELECT dl.id FROM dice_table_lobbies dl
            JOIN dice_table_members dm ON dm.lobby_id = dl.id
            WHERE dm.user_id = ? AND dm.status = 'active'
              AND dl.status IN ('waiting', 'playing') AND dl.game_type = 'maexchen'
            """,
            (g.user["id"],),
        ).fetchone()
        if own:
            return redirect(url_for("maexchen_lobby", lobby_id=own["id"]))
        now = _now()
        lobby_id = _db().execute(
            """
            INSERT INTO dice_table_lobbies
                (name, host_user_id, game_type, dice_count, use_cup, created_at)
            VALUES (?, ?, 'maexchen', 2, 1, ?)
            """,
            (f"{g.user['display_name']}´s Mäxchenrunde", g.user["id"], now),
        ).lastrowid
        _db().execute(
            "INSERT INTO dice_table_members (lobby_id, user_id, joined_at) VALUES (?, ?, ?)",
            (lobby_id, g.user["id"], now),
        )
        _db().commit()
        return redirect(url_for("maexchen_lobby", lobby_id=lobby_id))

    @app.post("/karten/wuerfeltisch/<int:lobby_id>/beitreten")
    @login_required
    def dice_table_join(lobby_id: int) -> Any:
        require_csrf()
        lobby = _lobby(lobby_id)
        members = _members(lobby_id) if lobby else []
        if (
            not lobby
            or lobby["game_type"] != "sandbox"
            or lobby["status"] != "waiting"
            or len(members) >= DICE_TABLE_MAX_PLAYERS
        ):
            flash("Dieser Würfeltisch ist gerade nicht verfügbar.", "error")
            return redirect(url_for("dice_table_index"))
        own = _db().execute(
            """
            SELECT dl.id FROM dice_table_lobbies dl
            JOIN dice_table_members dm ON dm.lobby_id = dl.id
            WHERE dm.user_id = ? AND dm.status = 'active'
              AND dl.status IN ('waiting', 'playing') AND dl.game_type = 'sandbox' AND dl.id != ?
            """,
            (g.user["id"], lobby_id),
        ).fetchone()
        if own:
            return redirect(url_for("dice_table_lobby", lobby_id=own["id"]))
        existing = _db().execute(
            "SELECT * FROM dice_table_members WHERE lobby_id = ? AND user_id = ?",
            (lobby_id, g.user["id"]),
        ).fetchone()
        if existing:
            _db().execute(
                "UPDATE dice_table_members SET status = 'active' WHERE id = ?",
                (existing["id"],),
            )
        else:
            _db().execute(
                "INSERT INTO dice_table_members (lobby_id, user_id, joined_at) VALUES (?, ?, ?)",
                (lobby_id, g.user["id"], _now()),
            )
        _db().execute(
            "UPDATE dice_table_lobbies SET revision = revision + 1 WHERE id = ?",
            (lobby_id,),
        )
        _db().commit()
        return redirect(url_for("dice_table_lobby", lobby_id=lobby_id))

    @app.post("/karten/kniffel/<int:lobby_id>/beitreten")
    @login_required
    def kniffel_join(lobby_id: int) -> Any:
        require_csrf()
        lobby = _lobby(lobby_id)
        members = _members(lobby_id) if lobby else []
        if (
            not lobby
            or lobby["game_type"] != "kniffel"
            or lobby["status"] != "waiting"
            or len(members) >= DICE_TABLE_MAX_PLAYERS
        ):
            flash("Dieser Kniffeltisch ist gerade nicht verfügbar.", "error")
            return redirect(url_for("kniffel_index"))
        own = _db().execute(
            """
            SELECT dl.id FROM dice_table_lobbies dl
            JOIN dice_table_members dm ON dm.lobby_id = dl.id
            WHERE dm.user_id = ? AND dm.status = 'active'
              AND dl.status IN ('waiting', 'playing') AND dl.game_type = 'kniffel' AND dl.id != ?
            """,
            (g.user["id"], lobby_id),
        ).fetchone()
        if own:
            return redirect(url_for("kniffel_lobby", lobby_id=own["id"]))
        existing = _db().execute(
            "SELECT * FROM dice_table_members WHERE lobby_id = ? AND user_id = ?",
            (lobby_id, g.user["id"]),
        ).fetchone()
        if existing:
            _db().execute(
                "UPDATE dice_table_members SET status = 'active' WHERE id = ?",
                (existing["id"],),
            )
        else:
            _db().execute(
                "INSERT INTO dice_table_members (lobby_id, user_id, joined_at) VALUES (?, ?, ?)",
                (lobby_id, g.user["id"], _now()),
            )
        _db().execute(
            "UPDATE dice_table_lobbies SET revision = revision + 1 WHERE id = ?",
            (lobby_id,),
        )
        _db().commit()
        return redirect(url_for("kniffel_lobby", lobby_id=lobby_id))

    @app.post("/karten/maexchen/<int:lobby_id>/beitreten")
    @login_required
    def maexchen_join(lobby_id: int) -> Any:
        require_csrf()
        lobby = _lobby(lobby_id)
        members = _members(lobby_id) if lobby else []
        if (
            not lobby
            or lobby["game_type"] != "maexchen"
            or lobby["status"] != "waiting"
            or len(members) >= DICE_TABLE_MAX_PLAYERS
        ):
            flash("Diese Mäxchenrunde ist gerade nicht verfügbar.", "error")
            return redirect(url_for("maexchen_index"))
        own = _db().execute(
            """
            SELECT dl.id FROM dice_table_lobbies dl
            JOIN dice_table_members dm ON dm.lobby_id = dl.id
            WHERE dm.user_id = ? AND dm.status = 'active'
              AND dl.status IN ('waiting', 'playing') AND dl.game_type = 'maexchen' AND dl.id != ?
            """,
            (g.user["id"], lobby_id),
        ).fetchone()
        if own:
            return redirect(url_for("maexchen_lobby", lobby_id=own["id"]))
        existing = _db().execute(
            "SELECT * FROM dice_table_members WHERE lobby_id = ? AND user_id = ?",
            (lobby_id, g.user["id"]),
        ).fetchone()
        if existing:
            _db().execute(
                "UPDATE dice_table_members SET status = 'active' WHERE id = ?",
                (existing["id"],),
            )
        else:
            _db().execute(
                "INSERT INTO dice_table_members (lobby_id, user_id, joined_at) VALUES (?, ?, ?)",
                (lobby_id, g.user["id"], _now()),
            )
        _db().execute(
            "UPDATE dice_table_lobbies SET revision = revision + 1 WHERE id = ?",
            (lobby_id,),
        )
        _db().commit()
        return redirect(url_for("maexchen_lobby", lobby_id=lobby_id))

    @app.get("/karten/wuerfeltisch/<int:lobby_id>")
    @login_required
    @active_view
    def dice_table_lobby(lobby_id: int) -> Any:
        lobby = _lobby(lobby_id)
        if lobby["game_type"] != "sandbox":
            abort(404)
        members = _members(lobby_id)
        if lobby["status"] == "playing":
            current_member = _member(lobby_id, g.user["id"])
            return render_template(
                "dice_table_game.html",
                lobby=lobby,
                members=members,
                member=current_member,
                dddice_theme=DICE_TABLE_THEME_ID,
                dddice_die_type=DICE_TABLE_D6_TYPE,
                camera_preference=_camera_preference(g.user["id"]),
                game_mode="sandbox",
            )
        return render_template(
            "dice_table_lobby.html",
            lobby_players=lobby_player_profiles(members),
            lobby=lobby,
            members=members,
            game_mode="sandbox",
        )

    @app.get("/karten/kniffel/<int:lobby_id>")
    @login_required
    @active_view
    def kniffel_lobby(lobby_id: int) -> Any:
        lobby = _lobby(lobby_id)
        if lobby["game_type"] != "kniffel":
            abort(404)
        members = _members(lobby_id)
        if lobby["status"] == "playing":
            return render_template(
                "dice_table_game.html",
                lobby=lobby,
                members=members,
                member=_member(lobby_id, g.user["id"]),
                dddice_theme=DICE_TABLE_THEME_ID,
                dddice_die_type=DICE_TABLE_D6_TYPE,
                camera_preference=_camera_preference(g.user["id"]),
                game_mode="kniffel",
            )
        return render_template(
            "dice_table_lobby.html",
            lobby_players=lobby_player_profiles(members),
            lobby=lobby,
            members=members,
            game_mode="kniffel",
        )

    @app.get("/karten/maexchen/<int:lobby_id>")
    @login_required
    @active_view
    def maexchen_lobby(lobby_id: int) -> Any:
        lobby = _lobby(lobby_id)
        if lobby["game_type"] != "maexchen":
            abort(404)
        members = _members(lobby_id)
        if lobby["status"] == "playing":
            return render_template(
                "dice_table_game.html",
                lobby=lobby,
                members=members,
                member=_member(lobby_id, g.user["id"]),
                dddice_theme=DICE_TABLE_THEME_ID,
                dddice_die_type=DICE_TABLE_D6_TYPE,
                camera_preference=_camera_preference(g.user["id"]),
                game_mode="maexchen",
                maexchen_values=MAEXCHEN_VALUES,
            )
        return render_template(
            "dice_table_lobby.html",
            lobby_players=lobby_player_profiles(members),
            lobby=lobby,
            members=members,
            game_mode="maexchen",
        )

    @app.post("/karten/wuerfeltisch/<int:lobby_id>/einstellungen")
    @login_required
    @active_view
    def dice_table_settings(lobby_id: int) -> Any:
        require_csrf()
        lobby = _lobby(lobby_id)
        if (
            lobby["game_type"] != "sandbox"
            or lobby["host_user_id"] != g.user["id"]
            or lobby["status"] != "waiting"
        ):
            abort(403)
        dice_count = request.form.get("dice_count", type=int)
        if dice_count not in range(1, 6):
            abort(400)
        use_cup = 1 if request.form.get("use_cup") == "1" else 0
        _db().execute(
            "UPDATE dice_table_lobbies SET dice_count = ?, use_cup = ?, revision = revision + 1 WHERE id = ?",
            (dice_count, use_cup, lobby_id),
        )
        _db().commit()
        return redirect(url_for("dice_table_lobby", lobby_id=lobby_id))

    @app.post("/karten/wuerfeltisch/<int:lobby_id>/starten")
    @login_required
    @active_view
    def dice_table_start(lobby_id: int) -> Any:
        require_csrf()
        lobby = _lobby(lobby_id)
        if (
            lobby["game_type"] != "sandbox"
            or lobby["host_user_id"] != g.user["id"]
            or lobby["status"] != "waiting"
        ):
            abort(403)
        dice_count = request.form.get("dice_count", type=int) or lobby["dice_count"]
        if dice_count not in range(1, 6):
            abort(400)
        use_cup = 1 if request.form.get("use_cup") == "1" else 0
        members = _members(lobby_id)
        state = {"roll": None, "dice": [], "history": {str(item["id"]): [] for item in members}}
        _db().execute(
            """
            UPDATE dice_table_lobbies
            SET status = 'playing', dice_count = ?, use_cup = ?, state_json = ?,
                started_at = ?, revision = revision + 1
            WHERE id = ?
            """,
            (
                dice_count,
                use_cup,
                json.dumps(state, ensure_ascii=False, separators=(",", ":")),
                _now(),
                lobby_id,
            ),
        )
        _db().commit()
        return redirect(url_for("dice_table_lobby", lobby_id=lobby_id))

    @app.post("/karten/kniffel/<int:lobby_id>/starten")
    @login_required
    @active_view
    def kniffel_start(lobby_id: int) -> Any:
        require_csrf()
        lobby = _lobby(lobby_id)
        if (
            lobby["game_type"] != "kniffel"
            or lobby["host_user_id"] != g.user["id"]
            or lobby["status"] != "waiting"
        ):
            abort(403)
        members = _members(lobby_id)
        state = {
            "roll": None,
            "dice": [],
            "history": {str(item["id"]): [] for item in members},
            "kniffel": _kniffel_state(members),
        }
        _db().execute(
            """
            UPDATE dice_table_lobbies
            SET status = 'playing', dice_count = 5, use_cup = 0, state_json = ?,
                started_at = ?, revision = revision + 1
            WHERE id = ?
            """,
            (json.dumps(state, ensure_ascii=False, separators=(",", ":")), _now(), lobby_id),
        )
        _db().commit()
        return redirect(url_for("kniffel_lobby", lobby_id=lobby_id))

    @app.post("/karten/maexchen/<int:lobby_id>/starten")
    @login_required
    @active_view
    def maexchen_start(lobby_id: int) -> Any:
        require_csrf()
        lobby = _lobby(lobby_id)
        members = _members(lobby_id)
        if (
            lobby["game_type"] != "maexchen"
            or lobby["host_user_id"] != g.user["id"]
            or lobby["status"] != "waiting"
        ):
            abort(403)
        if len(members) < 2:
            flash("Für Mäxchen werden mindestens zwei Personen benötigt.", "error")
            return redirect(url_for("maexchen_lobby", lobby_id=lobby_id))
        state = {
            "roll": None,
            "dice": [],
            "history": {},
            "maexchen": _maexchen_state(members),
        }
        _db().execute(
            """
            UPDATE dice_table_lobbies
            SET status = 'playing', dice_count = 2, use_cup = 1, state_json = ?,
                started_at = ?, revision = revision + 1
            WHERE id = ?
            """,
            (json.dumps(state, ensure_ascii=False, separators=(",", ":")), _now(), lobby_id),
        )
        _db().commit()
        return redirect(url_for("maexchen_lobby", lobby_id=lobby_id))

    @app.get("/karten/wuerfeltisch/<int:lobby_id>/status")
    @login_required
    @active_view
    def dice_table_status(lobby_id: int) -> Any:
        lobby = _lobby(lobby_id)
        members = _members(lobby_id)
        payload: dict[str, Any] = {
            "status": lobby["status"],
            "game_mode": lobby["game_type"],
            "revision": lobby["revision"],
            "dice_count": lobby["dice_count"],
            "use_cup": bool(lobby["use_cup"]),
            "members": [{"id": item["id"], "name": item["display_name"]} for item in members],
        }
        if lobby["status"] == "playing":
            viewer = _member(lobby_id, g.user["id"])
            state = _state(lobby)
            roll = state.get("roll")
            payload["history"] = _history_for_viewer(state, members, int(viewer["id"]))
            if lobby["game_type"] == "maexchen":
                maexchen = state.setdefault("maexchen", _maexchen_state(members))
                lives = maexchen.setdefault("lives", {})
                member_lookup = {int(item["id"]): item for item in members}
                payload["maexchen"] = {
                    "phase": maexchen.get("phase", "awaiting_roll"),
                    "turn_order": [int(item) for item in maexchen.get("turn_order", [])],
                    "current_member_id": maexchen.get("current_member_id"),
                    "claim": maexchen.get("claim"),
                    "claimant_id": maexchen.get("claimant_id"),
                    "responder_id": maexchen.get("responder_id"),
                    "round_number": int(maexchen.get("round_number", 1)),
                    "round_result": maexchen.get("round_result"),
                    "winner_id": maexchen.get("winner_id"),
                    "values": list(MAEXCHEN_VALUES),
                    "players": [
                        {
                            "id": member_id,
                            "name": member_lookup[member_id]["display_name"],
                            "lives": int(lives.get(str(member_id), 3)),
                            "swimming": int(lives.get(str(member_id), 3)) == 1,
                            "eliminated": int(lives.get(str(member_id), 3)) <= 0,
                        }
                        for member_id in maexchen.get("turn_order", [])
                        if int(member_id) in member_lookup
                    ],
                }
            if lobby["game_type"] == "kniffel":
                kniffel = state.setdefault("kniffel", _kniffel_state(members))
                order = _normalize_kniffel_turn(kniffel, members)
                turn_index = int(kniffel.get("turn_index", 0)) % max(1, len(order))
                current_id = order[turn_index] if order else None
                scores = kniffel.setdefault("scores", {})
                scorecards = []
                for item in members:
                    member_scores = scores.setdefault(str(item["id"]), {})
                    scorecards.append(
                        {
                            "id": item["id"],
                            "name": item["display_name"],
                            "scores": member_scores,
                            "totals": _kniffel_totals(member_scores),
                        }
                    )
                values = [int(die["value"]) for die in state.get("dice", [])]
                own_scores = scores.setdefault(str(viewer["id"]), {})
                available = {}
                if current_id == int(viewer["id"]) and len(values) == 5 and not kniffel.get("completed"):
                    available = {
                        key: _score_kniffel(key, values)
                        for key, _label in KNIFFEL_CATEGORIES
                        if key not in own_scores
                    }
                payload["kniffel"] = {
                    "categories": [{"key": key, "label": label} for key, label in KNIFFEL_CATEGORIES],
                    "scorecards": scorecards,
                    "current_member_id": current_id,
                    "roll_count": int(kniffel.get("roll_count", 0)),
                    "rolls_left": max(0, 3 - int(kniffel.get("roll_count", 0))),
                    "available_scores": available,
                    "completed": bool(kniffel.get("completed")),
                }
            if roll:
                is_roller = int(roll["roller_id"]) == int(viewer["id"])
                is_public_maexchen_roll = (
                    lobby["game_type"] == "maexchen" and roll["phase"] == "public"
                )
                may_receive_values = not lobby["use_cup"] or is_roller or is_public_maexchen_roll
                payload["dice"] = [
                    {
                        "id": die["id"],
                        "value": die["value"] if may_receive_values else None,
                        "zone": die.get("zone", "active"),
                        "return_zone": die.get("return_zone"),
                    }
                    for die in state.get("dice", [])
                ]
                payload["roll"] = {
                    "id": roll["id"],
                    "roller_id": roll["roller_id"],
                    "roller_name": roll["roller_name"],
                    "phase": roll["phase"],
                    "rolled_ids": roll.get("rolled_ids", []),
                    "visible": (
                        roll["phase"] in ("revealed", "private", "public")
                        and may_receive_values
                    ),
                }
            else:
                payload["roll"] = None
                payload["dice"] = []
        return payload

    @app.post("/karten/wuerfeltisch/kamera")
    @login_required
    def dice_table_camera() -> Any:
        require_csrf()
        locked = request.form.get("locked") == "1"
        camera = None
        if locked:
            try:
                camera = json.loads(request.form.get("camera", ""))
                position = camera["position"]
                target = camera["target"]
                numbers = [position[key] for key in ("x", "y", "z")] + [target[key] for key in ("x", "y", "z")]
                if not all(isinstance(value, (int, float)) and abs(value) <= 200 for value in numbers):
                    raise ValueError
            except (KeyError, TypeError, ValueError, json.JSONDecodeError):
                abort(400)
        _db().execute(
            """
            INSERT INTO dice_table_preferences (user_id, camera_locked, camera_json, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                camera_locked = excluded.camera_locked,
                camera_json = excluded.camera_json,
                updated_at = excluded.updated_at
            """,
            (
                g.user["id"],
                1 if locked else 0,
                json.dumps(camera, separators=(",", ":")) if camera else None,
                _now(),
            ),
        )
        _db().commit()
        return {"ok": True, "locked": locked}

    @app.post("/karten/wuerfeltisch/<int:lobby_id>/aktion")
    @login_required
    @active_view
    def dice_table_action(lobby_id: int) -> Any:
        require_csrf()
        database = _db()
        database.execute("BEGIN IMMEDIATE")
        lobby = _lobby(lobby_id)
        member = _member(lobby_id, g.user["id"])
        if lobby["status"] != "playing":
            database.rollback()
            return {"ok": False}, 409
        state = _state(lobby)
        action = request.form.get("action", "")
        roll = state.get("roll")
        is_roller = bool(roll) and int(roll["roller_id"]) == int(member["id"])
        is_maexchen = lobby["game_type"] == "maexchen"
        if is_maexchen:
            members = _members(lobby_id)
            maexchen = state.setdefault("maexchen", _maexchen_state(members))
            member_id = int(member["id"])
            current_id = int(maexchen.get("current_member_id") or 0)
            phase = maexchen.get("phase")

            def reject(status: int = 409) -> Any:
                database.rollback()
                return {"ok": False}, status

            def member_name(target_id: int) -> str:
                target = next((item for item in members if int(item["id"]) == target_id), None)
                return target["display_name"] if target else "Unbekannt"

            def record_loss(
                loser_id: int,
                amount: int,
                reason: str,
                *,
                actual: str | None = None,
                claim: str | None = None,
            ) -> None:
                _maexchen_apply_loss(maexchen, loser_id, amount, members)
                remaining = int(maexchen["lives"].get(str(loser_id), 0))
                maexchen["round_result"] = {
                    "loser_id": loser_id,
                    "loser_name": member_name(loser_id),
                    "loss": amount,
                    "remaining_lives": remaining,
                    "swimming": remaining == 1,
                    "eliminated": remaining <= 0,
                    "reason": reason,
                    "actual": actual,
                    "claim": claim,
                    "next_member_id": maexchen.get("current_member_id"),
                }

            if action == "roll":
                if phase != "awaiting_roll" or current_id != member_id:
                    return reject()
                new_dice = [
                    {"id": secrets.token_hex(8), "value": secrets.randbelow(6) + 1, "zone": "active"}
                    for _ in range(2)
                ]
                state["dice"] = new_dice
                state["roll"] = {
                    "id": secrets.token_hex(8),
                    "roller_id": member_id,
                    "roller_name": g.user["display_name"],
                    "rolled_ids": [die["id"] for die in new_dice],
                    "phase": "private",
                }
                maexchen["phase"] = "awaiting_claim"
                maexchen["claimant_id"] = member_id
                maexchen["responder_id"] = None
            elif action == "claim":
                claim = request.form.get("claim", "")
                previous = maexchen.get("claim")
                if (
                    phase != "awaiting_claim"
                    or current_id != member_id
                    or not roll
                    or not is_roller
                    or claim not in MAEXCHEN_VALUES
                    or (previous in MAEXCHEN_VALUES and _maexchen_rank(claim) <= _maexchen_rank(previous))
                ):
                    return reject()
                responder_id = _next_maexchen_member(maexchen, member_id)
                if responder_id is None or responder_id == member_id:
                    return reject()
                maexchen["claim"] = claim
                maexchen["claimant_id"] = member_id
                maexchen["responder_id"] = responder_id
                maexchen["phase"] = "awaiting_response"
            elif action == "believe":
                if (
                    phase != "awaiting_response"
                    or int(maexchen.get("responder_id") or 0) != member_id
                    or maexchen.get("claim") == "21"
                ):
                    return reject()
                maexchen["current_member_id"] = member_id
                maexchen["claimant_id"] = None
                maexchen["responder_id"] = None
                maexchen["phase"] = "awaiting_roll"
                state["roll"] = None
                state["dice"] = []
            elif action == "believe_maexchen":
                if (
                    phase != "awaiting_response"
                    or int(maexchen.get("responder_id") or 0) != member_id
                    or maexchen.get("claim") != "21"
                ):
                    return reject()
                record_loss(
                    member_id,
                    1,
                    "Mäxchen geglaubt – ein Leben abgegeben und Vorlegerecht erhalten.",
                    claim="21",
                )
                state["roll"] = None
                state["dice"] = []
            elif action == "reveal":
                if (
                    phase != "awaiting_response"
                    or int(maexchen.get("responder_id") or 0) != member_id
                    or not roll
                ):
                    return reject()
                actual = _maexchen_value([int(die["value"]) for die in state.get("dice", [])])
                claim = str(maexchen.get("claim"))
                claimant_id = int(maexchen.get("claimant_id") or 0)
                if _maexchen_rank(actual) >= _maexchen_rank(claim):
                    loss = 2 if actual == "21" and claim == "21" else 1
                    record_loss(
                        member_id,
                        loss,
                        "Das Aufdecken war falsch – die Ansage war gedeckt.",
                        actual=actual,
                        claim=claim,
                    )
                else:
                    record_loss(
                        claimant_id,
                        1,
                        "Der Bluff wurde aufgedeckt.",
                        actual=actual,
                        claim=claim,
                    )
                roll["phase"] = "public"
            elif action == "next_round":
                if phase != "round_result" or current_id != member_id:
                    return reject()
                maexchen["round_number"] = int(maexchen.get("round_number", 1)) + 1
                maexchen["phase"] = "awaiting_roll"
                maexchen["claim"] = None
                maexchen["claimant_id"] = None
                maexchen["responder_id"] = None
                maexchen["round_result"] = None
                state["roll"] = None
                state["dice"] = []
            else:
                database.rollback()
                abort(400)
            _save_state(lobby_id, state)
            return {"ok": True}

        is_kniffel = lobby["game_type"] == "kniffel"
        kniffel = state.setdefault("kniffel", _kniffel_state(_members(lobby_id))) if is_kniffel else None
        if is_kniffel:
            _normalize_kniffel_turn(kniffel, _members(lobby_id))
        if action == "score":
            if not is_kniffel or kniffel.get("completed"):
                database.rollback()
                return {"ok": False}, 409
            order = [int(item) for item in kniffel.get("turn_order", [])]
            current_id = order[int(kniffel.get("turn_index", 0)) % len(order)] if order else None
            category = request.form.get("category", "")
            valid_categories = {key for key, _label in KNIFFEL_CATEGORIES}
            member_scores = kniffel.setdefault("scores", {}).setdefault(str(member["id"]), {})
            values = [int(die["value"]) for die in state.get("dice", [])]
            if (
                current_id != int(member["id"])
                or category not in valid_categories
                or category in member_scores
                or len(values) != 5
                or int(kniffel.get("roll_count", 0)) < 1
            ):
                database.rollback()
                return {"ok": False}, 409
            member_scores[category] = _score_kniffel(category, values)
            active_ids = {int(item["id"]) for item in _members(lobby_id)}
            kniffel["completed"] = bool(active_ids) and all(
                len(kniffel["scores"].setdefault(str(member_id), {})) == len(KNIFFEL_CATEGORIES)
                for member_id in active_ids
            )
            if not kniffel["completed"]:
                next_index = int(kniffel.get("turn_index", 0))
                for _ in range(max(1, len(order))):
                    next_index = (next_index + 1) % len(order)
                    if order[next_index] in active_ids:
                        break
                kniffel["turn_index"] = next_index
            kniffel["roll_count"] = 0
            state["dice"] = []
            state["roll"] = None
        elif action == "collect":
            if roll and not is_roller:
                database.rollback()
                return {"ok": False}, 403
            if roll and roll["phase"] != "revealed":
                database.rollback()
                return {"ok": False}, 409
            for die in state.get("dice", []):
                if die.get("zone") != "tray":
                    die["return_zone"] = "active"
                    die["zone"] = "tray"
        elif action == "toggle":
            if not roll or not is_roller or roll["phase"] != "revealed":
                database.rollback()
                return {"ok": False}, 409
            die_id = request.form.get("die_id", "")
            die = next((item for item in state.get("dice", []) if item["id"] == die_id), None)
            if not die:
                database.rollback()
                return {"ok": False}, 404
            if die.get("zone") == "tray":
                die["zone"] = die.pop("return_zone", "active")
            else:
                die["return_zone"] = die.get("zone", "active")
                die["zone"] = "tray"
        elif action == "roll":
            if is_kniffel:
                order = [int(item) for item in kniffel.get("turn_order", [])]
                current_id = order[int(kniffel.get("turn_index", 0)) % len(order)] if order else None
                if (
                    current_id != int(member["id"])
                    or kniffel.get("completed")
                    or int(kniffel.get("roll_count", 0)) >= 3
                ):
                    database.rollback()
                    return {"ok": False}, 409
            if roll and is_roller and roll["phase"] != "revealed":
                database.rollback()
                return {"ok": False, "reason": "reveal-first"}, 409
            dice = state.get("dice", []) if is_roller else []
            selected = [die for die in dice if die.get("zone") == "tray"]
            if selected:
                kept = [
                    {"id": die["id"], "value": die["value"], "zone": "held"}
                    for die in dice
                    if die.get("zone") != "tray"
                ]
                roll_count = len(selected)
            else:
                kept = []
                roll_count = int(lobby["dice_count"])
            new_dice = [
                {
                    "id": secrets.token_hex(8),
                    "value": secrets.randbelow(6) + 1,
                    "zone": "active",
                }
                for _ in range(roll_count)
            ]
            state["dice"] = kept + new_dice
            state["roll"] = {
                "id": secrets.token_hex(8),
                "roller_id": member["id"],
                "roller_name": g.user["display_name"],
                "rolled_ids": [die["id"] for die in new_dice],
                "phase": "covered" if lobby["use_cup"] else "revealed",
            }
            history = state.setdefault("history", {})
            history.setdefault(str(member["id"]), []).append(
                {"values": [die["value"] for die in new_dice], "private": bool(lobby["use_cup"])}
            )
            history[str(member["id"])] = history[str(member["id"])][-6:]
            if is_kniffel:
                kniffel["roll_count"] = int(kniffel.get("roll_count", 0)) + 1
        elif action == "reveal":
            if (
                not lobby["use_cup"]
                or not roll
                or roll["phase"] != "covered"
                or int(roll["roller_id"]) != int(member["id"])
            ):
                database.rollback()
                return {"ok": False}, 409
            roll["phase"] = "revealed"
        else:
            database.rollback()
            abort(400)
        _save_state(lobby_id, state)
        return {"ok": True}

    @app.post("/karten/wuerfeltisch/<int:lobby_id>/verlassen")
    @login_required
    @active_view
    def dice_table_leave(lobby_id: int) -> Any:
        require_csrf()
        lobby = _lobby(lobby_id)
        departing = _member(lobby_id, g.user["id"])
        _db().execute(
            "UPDATE dice_table_members SET status = 'left' WHERE lobby_id = ? AND user_id = ?",
            (lobby_id, g.user["id"]),
        )
        remaining = _members(lobby_id)
        if lobby["game_type"] == "maexchen" and lobby["status"] == "playing" and lobby["state_json"]:
            state = _state(lobby)
            maexchen = state.setdefault("maexchen", _maexchen_state(remaining))
            departed_id = int(departing["id"])
            maexchen.setdefault("lives", {})[str(departed_id)] = 0
            alive_ids = [
                int(item["id"])
                for item in remaining
                if int(maexchen["lives"].get(str(item["id"]), 3)) > 0
            ]
            if len(alive_ids) <= 1:
                maexchen["phase"] = "finished"
                maexchen["winner_id"] = alive_ids[0] if alive_ids else None
                maexchen["current_member_id"] = alive_ids[0] if alive_ids else None
            elif departed_id in {
                int(maexchen.get("current_member_id") or 0),
                int(maexchen.get("claimant_id") or 0),
                int(maexchen.get("responder_id") or 0),
            }:
                maexchen["current_member_id"] = _next_maexchen_member(maexchen, departed_id)
                maexchen["phase"] = "awaiting_roll"
                maexchen["claim"] = None
                maexchen["claimant_id"] = None
                maexchen["responder_id"] = None
                maexchen["round_result"] = None
                state["roll"] = None
                state["dice"] = []
            _db().execute(
                "UPDATE dice_table_lobbies SET state_json = ?, revision = revision + 1 WHERE id = ?",
                (json.dumps(state, ensure_ascii=False, separators=(",", ":")), lobby_id),
            )
        if not remaining:
            _db().execute(
                "UPDATE dice_table_lobbies SET status = 'abandoned', completed_at = ?, revision = revision + 1 WHERE id = ?",
                (_now(), lobby_id),
            )
        elif lobby["host_user_id"] == g.user["id"]:
            _db().execute(
                "UPDATE dice_table_lobbies SET host_user_id = ?, revision = revision + 1 WHERE id = ?",
                (remaining[0]["user_id"], lobby_id),
            )
        else:
            _db().execute(
                "UPDATE dice_table_lobbies SET revision = revision + 1 WHERE id = ?",
                (lobby_id,),
            )
        _db().commit()
        index_endpoint = {
            "kniffel": "kniffel_index",
            "maexchen": "maexchen_index",
        }.get(lobby["game_type"], "dice_table_index")
        return redirect(url_for(index_endpoint))
