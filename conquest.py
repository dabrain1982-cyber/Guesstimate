from __future__ import annotations

import json
import secrets
import sqlite3
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable

from flask import abort, current_app, flash, g, redirect, render_template, request, url_for


CONQUEST_MAX_PLAYERS = 6
CONQUEST_MIN_PLAYERS = 2
CONQUEST_STYLES = {
    "klassisch": "Klassisch alt",
    "taktisch": "Taktisch modern",
    "farbenfroh": "Modern bunt",
}
CONQUEST_FIGURES = {
    "klassisch": "Klassische Plastiktruppen",
    "modern": "Abgerundete moderne Truppen",
    "fantasy": "Fantasy-Heere",
}
CONQUEST_DICE = {
    "klassisch": "Klassische Würfel",
    "modern": "Moderne Würfel",
    "fantasy": "Fantasy-Würfel",
}
CONQUEST_VICTORIES = {
    "missions": "Geheime Missionen",
    "world": "Welteroberung",
}
CONQUEST_SETUPS = {
    "automatic": "Automatisch verteilen",
    "classic": "Gebiete reihum wählen",
}
INITIAL_ARMIES = {2: 40, 3: 35, 4: 30, 5: 25, 6: 20}
WORLD_PATH = Path(__file__).with_name("static") / "conquest" / "world.json"


def _db() -> sqlite3.Connection:
    return current_app.get_db()  # type: ignore[attr-defined]


def _iso() -> str:
    return datetime.now().isoformat(timespec="microseconds")


def init_conquest_db(get_db: Callable[[], sqlite3.Connection]) -> None:
    database = get_db()
    database.executescript(
        """
        CREATE TABLE IF NOT EXISTS conquest_lobbies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            host_user_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'waiting',
            board_style TEXT NOT NULL DEFAULT 'klassisch',
            card_style TEXT NOT NULL DEFAULT 'klassisch',
            figure_style TEXT NOT NULL DEFAULT 'klassisch',
            dice_style TEXT NOT NULL DEFAULT 'klassisch',
            victory_mode TEXT NOT NULL DEFAULT 'missions',
            setup_mode TEXT NOT NULL DEFAULT 'automatic',
            state_json TEXT,
            revision INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            started_at TEXT,
            completed_at TEXT,
            FOREIGN KEY(host_user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS conquest_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lobby_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            joined_at TEXT NOT NULL,
            UNIQUE(lobby_id, user_id),
            FOREIGN KEY(lobby_id) REFERENCES conquest_lobbies(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE INDEX IF NOT EXISTS conquest_members_lobby_idx
            ON conquest_members(lobby_id);
        """
    )
    database.commit()


def _lobby(lobby_id: int) -> sqlite3.Row | None:
    return _db().execute("SELECT * FROM conquest_lobbies WHERE id = ?", (lobby_id,)).fetchone()


def _member(lobby_id: int, user_id: int) -> sqlite3.Row | None:
    return _db().execute(
        "SELECT * FROM conquest_members WHERE lobby_id = ? AND user_id = ?",
        (lobby_id, user_id),
    ).fetchone()


def _members(lobby_id: int) -> list[sqlite3.Row]:
    return _db().execute(
        """
        SELECT cm.*, u.display_name
        FROM conquest_members cm JOIN users u ON u.id = cm.user_id
        WHERE cm.lobby_id = ? AND cm.status = 'active'
        ORDER BY cm.joined_at, cm.id
        """,
        (lobby_id,),
    ).fetchall()


def _require_member(lobby_id: int) -> tuple[sqlite3.Row, sqlite3.Row]:
    lobby = _lobby(lobby_id)
    member = _member(lobby_id, g.user["id"])
    if not lobby or not member or member["status"] != "active":
        abort(404)
    return lobby, member


def _lobby_rows(user_id: int) -> list[sqlite3.Row]:
    return _db().execute(
        """
        SELECT cl.*, u.display_name AS host_name,
               COUNT(CASE WHEN cm.status = 'active' THEN 1 END) AS member_count,
               MAX(CASE WHEN cm.user_id = ? AND cm.status = 'active' THEN 1 ELSE 0 END) AS is_member
        FROM conquest_lobbies cl
        JOIN users u ON u.id = cl.host_user_id
        LEFT JOIN conquest_members cm ON cm.lobby_id = cl.id
        WHERE cl.status IN ('waiting', 'playing')
        GROUP BY cl.id
        ORDER BY cl.created_at DESC
        """,
        (user_id,),
    ).fetchall()


def _first_player(members: list[sqlite3.Row]) -> tuple[int, list[dict[str, Any]]]:
    remaining = list(members)
    rolls: list[dict[str, Any]] = []
    while True:
        round_rolls = [(row, secrets.randbelow(6) + 1) for row in remaining]
        rolls.extend({"member_id": row["id"], "name": row["display_name"], "roll": value} for row, value in round_rolls)
        highest = max(value for _, value in round_rolls)
        winners = [row for row, value in round_rolls if value == highest]
        if len(winners) == 1:
            return winners[0]["id"], rolls
        remaining = winners


def _prepare_automatic_state(members: list[sqlite3.Row], victory_mode: str) -> dict[str, Any]:
    world = json.loads(WORLD_PATH.read_text(encoding="utf-8"))
    territories = list(world["territories"])
    secrets.SystemRandom().shuffle(territories)
    participant_ids: list[str | int] = [row["id"] for row in members]
    if len(members) == 2:
        participant_ids.append("neutral")
    assignments: dict[str, dict[str, Any]] = {}
    owned: dict[str | int, list[str]] = {participant_id: [] for participant_id in participant_ids}
    for index, territory in enumerate(territories):
        owner = participant_ids[index % len(participant_ids)]
        territory_id = territory["id"]
        assignments[territory_id] = {"owner": owner, "armies": 1}
        owned[owner].append(territory_id)
    army_count = INITIAL_ARMIES[len(members)]
    for owner in participant_ids:
        remaining = army_count - len(owned[owner])
        for _ in range(remaining):
            territory_id = secrets.choice(owned[owner])
            assignments[territory_id]["armies"] += 1
    first_member_id, opening_rolls = _first_player(members)
    missions: dict[str, str] = {}
    if victory_mode == "missions":
        mission_rows = list(world["missions"])
        secrets.SystemRandom().shuffle(mission_rows)
        missions = {str(row["id"]): mission_rows[index]["id"] for index, row in enumerate(members)}
    return {
        "phase": "reinforce",
        "round": 1,
        "current_member_id": first_member_id,
        "opening_rolls": opening_rolls,
        "territories": assignments,
        "missions": missions,
        "captured_this_turn": False,
        "trade_count": 0,
    }


def register_conquest_routes(
    app: Any,
    login_required: Callable[[Callable[..., Any]], Callable[..., Any]],
    require_csrf: Callable[[], None],
) -> None:
    def active_view(view: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(view)
        def wrapped(lobby_id: int, *args: Any, **kwargs: Any) -> Any:
            _require_member(lobby_id)
            return view(lobby_id, *args, **kwargs)

        return wrapped

    @app.get("/karten/welteroberung")
    @login_required
    def conquest_index() -> Any:
        return render_template("conquest_index.html", lobbies=_lobby_rows(g.user["id"]))

    @app.post("/karten/welteroberung/erstellen")
    @login_required
    def conquest_create() -> Any:
        require_csrf()
        own = _db().execute(
            """
            SELECT cl.id FROM conquest_lobbies cl
            JOIN conquest_members cm ON cm.lobby_id = cl.id
            WHERE cm.user_id = ? AND cm.status = 'active'
              AND cl.status IN ('waiting', 'playing')
            """,
            (g.user["id"],),
        ).fetchone()
        if own:
            return redirect(url_for("conquest_lobby", lobby_id=own["id"]))
        now = _iso()
        lobby_id = _db().execute(
            "INSERT INTO conquest_lobbies (name, host_user_id, created_at) VALUES (?, ?, ?)",
            (f"{g.user['display_name']}s Feldzug", g.user["id"], now),
        ).lastrowid
        _db().execute(
            "INSERT INTO conquest_members (lobby_id, user_id, joined_at) VALUES (?, ?, ?)",
            (lobby_id, g.user["id"], now),
        )
        _db().commit()
        return redirect(url_for("conquest_lobby", lobby_id=lobby_id))

    @app.post("/karten/welteroberung/<int:lobby_id>/beitreten")
    @login_required
    def conquest_join(lobby_id: int) -> Any:
        require_csrf()
        lobby = _lobby(lobby_id)
        if not lobby or lobby["status"] != "waiting" or len(_members(lobby_id)) >= CONQUEST_MAX_PLAYERS:
            flash("Dieser Feldzug ist gerade nicht verfügbar.", "error")
            return redirect(url_for("conquest_index"))
        own = _db().execute(
            """
            SELECT cl.id FROM conquest_lobbies cl
            JOIN conquest_members cm ON cm.lobby_id = cl.id
            WHERE cm.user_id = ? AND cm.status = 'active'
              AND cl.status IN ('waiting', 'playing') AND cl.id != ?
            """,
            (g.user["id"], lobby_id),
        ).fetchone()
        if own:
            return redirect(url_for("conquest_lobby", lobby_id=own["id"]))
        existing = _member(lobby_id, g.user["id"])
        if existing:
            _db().execute("UPDATE conquest_members SET status = 'active' WHERE id = ?", (existing["id"],))
        else:
            _db().execute(
                "INSERT INTO conquest_members (lobby_id, user_id, joined_at) VALUES (?, ?, ?)",
                (lobby_id, g.user["id"], _iso()),
            )
        _db().execute("UPDATE conquest_lobbies SET revision = revision + 1 WHERE id = ?", (lobby_id,))
        _db().commit()
        return redirect(url_for("conquest_lobby", lobby_id=lobby_id))

    @app.post("/karten/welteroberung/<int:lobby_id>/einstellungen")
    @login_required
    @active_view
    def conquest_settings(lobby_id: int) -> Any:
        require_csrf()
        lobby = _lobby(lobby_id)
        if lobby["host_user_id"] != g.user["id"] or lobby["status"] != "waiting":
            abort(403)
        values = {
            "board_style": request.form.get("board_style", ""),
            "card_style": request.form.get("card_style", ""),
            "figure_style": request.form.get("figure_style", ""),
            "dice_style": request.form.get("dice_style", ""),
            "victory_mode": request.form.get("victory_mode", ""),
            "setup_mode": request.form.get("setup_mode", ""),
        }
        if values["board_style"] not in CONQUEST_STYLES or values["card_style"] not in CONQUEST_STYLES:
            abort(400)
        if values["figure_style"] not in CONQUEST_FIGURES or values["dice_style"] not in CONQUEST_DICE:
            abort(400)
        if values["victory_mode"] not in CONQUEST_VICTORIES or values["setup_mode"] not in CONQUEST_SETUPS:
            abort(400)
        _db().execute(
            """
            UPDATE conquest_lobbies
            SET board_style = ?, card_style = ?, figure_style = ?, dice_style = ?,
                victory_mode = ?, setup_mode = ?, revision = revision + 1
            WHERE id = ?
            """,
            (*values.values(), lobby_id),
        )
        _db().commit()
        return redirect(url_for("conquest_lobby", lobby_id=lobby_id))

    @app.post("/karten/welteroberung/<int:lobby_id>/starten")
    @login_required
    @active_view
    def conquest_start(lobby_id: int) -> Any:
        require_csrf()
        lobby = _lobby(lobby_id)
        members = _members(lobby_id)
        if lobby["host_user_id"] != g.user["id"] or lobby["status"] != "waiting":
            abort(403)
        if len(members) < CONQUEST_MIN_PLAYERS:
            flash("Zum Start werden mindestens zwei Personen benötigt.", "error")
            return redirect(url_for("conquest_lobby", lobby_id=lobby_id))
        if lobby["setup_mode"] != "automatic":
            flash("Die klassische Gebietswahl folgt als nächster Regelbaustein. Bitte vorerst automatisch verteilen.", "error")
            return redirect(url_for("conquest_lobby", lobby_id=lobby_id))
        state = _prepare_automatic_state(members, lobby["victory_mode"])
        _db().execute(
            """
            UPDATE conquest_lobbies
            SET status = 'playing', state_json = ?, started_at = ?, revision = revision + 1
            WHERE id = ?
            """,
            (json.dumps(state, ensure_ascii=False, separators=(",", ":")), _iso(), lobby_id),
        )
        _db().commit()
        return redirect(url_for("conquest_lobby", lobby_id=lobby_id))

    @app.get("/karten/welteroberung/<int:lobby_id>")
    @login_required
    @active_view
    def conquest_lobby(lobby_id: int) -> Any:
        lobby, member = _require_member(lobby_id)
        members = _members(lobby_id)
        if lobby["status"] == "waiting":
            return render_template(
                "conquest_lobby.html",
                lobby=lobby,
                members=members,
                styles=CONQUEST_STYLES,
                figures=CONQUEST_FIGURES,
                dice_choices=CONQUEST_DICE,
                victories=CONQUEST_VICTORIES,
                setups=CONQUEST_SETUPS,
            )
        if lobby["status"] != "playing":
            return redirect(url_for("conquest_index"))
        state = json.loads(lobby["state_json"])
        current_name = next(row["display_name"] for row in members if row["id"] == state["current_member_id"])
        own_mission = state.get("missions", {}).get(str(member["id"]))
        return render_template(
            "conquest_table.html",
            lobby=lobby,
            member=member,
            members=members,
            state=state,
            current_name=current_name,
            own_mission=own_mission,
        )

    @app.get("/karten/welteroberung/<int:lobby_id>/status")
    @login_required
    @active_view
    def conquest_status(lobby_id: int) -> Any:
        lobby, member = _require_member(lobby_id)
        members = _members(lobby_id)
        payload: dict[str, Any] = {
            "status": lobby["status"],
            "revision": lobby["revision"],
            "members": [{"id": row["id"], "name": row["display_name"]} for row in members],
        }
        if lobby["status"] == "playing" and lobby["state_json"]:
            state = json.loads(lobby["state_json"])
            payload["game"] = {
                "phase": state["phase"],
                "round": state["round"],
                "current_member_id": state["current_member_id"],
                "territories": state["territories"],
                "opening_rolls": state["opening_rolls"],
                "own_mission": state.get("missions", {}).get(str(member["id"])),
            }
        return payload

    @app.post("/karten/welteroberung/<int:lobby_id>/verlassen")
    @login_required
    @active_view
    def conquest_leave(lobby_id: int) -> Any:
        require_csrf()
        lobby, member = _require_member(lobby_id)
        _db().execute("UPDATE conquest_members SET status = 'left' WHERE id = ?", (member["id"],))
        remaining = _members(lobby_id)
        if not remaining:
            _db().execute(
                "UPDATE conquest_lobbies SET status = 'abandoned', completed_at = ? WHERE id = ?",
                (_iso(), lobby_id),
            )
        elif lobby["host_user_id"] == g.user["id"]:
            _db().execute(
                "UPDATE conquest_lobbies SET host_user_id = ?, revision = revision + 1 WHERE id = ?",
                (remaining[0]["user_id"], lobby_id),
            )
        else:
            _db().execute("UPDATE conquest_lobbies SET revision = revision + 1 WHERE id = ?", (lobby_id,))
        _db().commit()
        return redirect(url_for("conquest_index"))
