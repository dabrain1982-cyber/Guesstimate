from __future__ import annotations

from lobby_overview import render_overview

import json
import secrets
import sqlite3
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable

from flask import abort, current_app, flash, g, redirect, render_template, request, session, send_from_directory, url_for
from lobby_view import lobby_player_profiles
from player_portrait import public_portrait
from conquest_turns import COLORS, apply_action, hydrate, public_game
from conquest_victory import COLOR_SEATS, check_victory


CONQUEST_MAX_PLAYERS = 6
CONQUEST_MIN_PLAYERS = 2
COLOR_NAMES = ('Gold', 'Rot', 'Blau', 'Grün', 'Violett', 'Orange')
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
    "automatic": "Länder automatisch zuteilen",
    "classic": "Gebiete reihum wählen",
}
INITIAL_ARMIES = {2: 40, 3: 35, 4: 30, 5: 25, 6: 20}
WORLD_PATH = Path(__file__).with_name("static") / "conquest" / "world.json"
TABLE_PATH = Path(__file__).parent / "offline-preview" / "conquest-2-5d-v1"


def _developer_enabled() -> bool:
    if not current_app.config.get("LOCAL_DEVELOPMENT") or g.user["username"] != current_app.config["OWNER_USERNAME"]:
        return False
    row = _db().execute("SELECT developer_enabled FROM user_cosmetics WHERE user_id = ?", (g.user["id"],)).fetchone()
    return bool(row and row["developer_enabled"])


def _world() -> dict:
    return json.loads(WORLD_PATH.read_text(encoding="utf-8"))


def _game(lobby: sqlite3.Row, member: sqlite3.Row, members: list) -> dict:
    world = _world()
    state = hydrate(json.loads(lobby["state_json"]), world, members, lobby["victory_mode"])
    return _public_state(lobby, member, members, state, world)


def _waiting_member(state: dict, members: list) -> str | None:
    if state.get('winner'):
        return None
    active = {str(row['id']) for row in members}
    required = [str(state['current_member_id'])]
    if state.get('battle_request'):
        required.append(str(state['battle_request']['defender']))
    for participant in state.get('participants', []):
        key = str(participant['id'])
        if key in required and key not in active and not (state.get('developer_test') and key.startswith('test-')):
            return participant['name']
    return None


def _public_state(lobby, member, members, state, world):
    developer = bool(state.get('developer_test') and lobby['host_user_id'] == g.user['id'] and _developer_enabled())
    game = public_game(state, world, member['id'], developer)
    profiles = {str(row['id']): row for row in _members(lobby['id'], include_left=True)}
    color_names = ('Gold', 'Rot', 'Blau', 'Grün', 'Violett', 'Orange')
    for index, army in enumerate(game['armies']):
        profile = profiles.get(army['id'])
        army['color_name'] = 'Neutral' if army['id'] == 'neutral' else color_names[army.get('color_index', index)]
        army['kind'] = 'player' if profile else 'neutral' if army['id'] == 'neutral' else 'test'
        army['portrait'] = public_portrait(profile['avatar_id'], is_self=profile['user_id'] == g.user['id']) if profile else None
        if profile:
            army['name'] = profile['display_name']
    game['waiting_for_member'] = _waiting_member(state, members)
    if game['waiting_for_member']:
        game.update(can_act=False, can_defend=False)
        game['trade'] = dict(game['trade'], can_trade=False, mandatory=False)
    game['lobby'] = {
        'is_host': lobby['host_user_id'] == g.user['id'],
        'room_url': url_for('conquest_room', lobby_id=lobby['id']),
        'leave_url': url_for('conquest_leave', lobby_id=lobby['id']),
        'rematch_url': url_for('conquest_rematch', lobby_id=lobby['id']),
    }
    return game


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

        CREATE TABLE IF NOT EXISTS conquest_game_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lobby_id INTEGER NOT NULL,
            completed_revision INTEGER NOT NULL,
            state_json TEXT NOT NULL,
            started_at TEXT,
            completed_at TEXT,
            UNIQUE(lobby_id, completed_revision),
            UNIQUE(lobby_id, started_at),
            FOREIGN KEY(lobby_id) REFERENCES conquest_lobbies(id)
        );
        """
    )
    if 'color_index' not in {row['name'] for row in database.execute('PRAGMA table_info(conquest_members)')}:
        database.execute('ALTER TABLE conquest_members ADD COLUMN color_index INTEGER')
    database.commit()


def _lobby(lobby_id: int) -> sqlite3.Row | None:
    return _db().execute("SELECT * FROM conquest_lobbies WHERE id = ?", (lobby_id,)).fetchone()


def _member(lobby_id: int, user_id: int) -> sqlite3.Row | None:
    return _db().execute(
        "SELECT * FROM conquest_members WHERE lobby_id = ? AND user_id = ?",
        (lobby_id, user_id),
    ).fetchone()


def _members(lobby_id: int, include_left: bool = False) -> list[sqlite3.Row]:
    return _db().execute(
        """
        SELECT cm.*, u.display_name, COALESCE(uc.avatar_id, 'a00') AS avatar_id,
               COALESCE(uc.plaque_id, 'p00') AS plaque_id
        FROM conquest_members cm JOIN users u ON u.id = cm.user_id
        LEFT JOIN user_cosmetics uc ON uc.user_id = u.id
        WHERE cm.lobby_id = ? AND (? OR cm.status = 'active')
        ORDER BY cm.joined_at, cm.id
        """,
        (lobby_id, int(include_left)),
    ).fetchall()


def _member_colors(members):
    """Resolve old seats and new preferences without modifying saved games."""
    result = {}
    for row in members:
        preferred = dict(row).get('color_index')
        available = [index for index in range(6) if index not in result.values()]
        result[str(row['id'])] = preferred if preferred in available else available[0]
    return result


def _require_member(lobby_id: int) -> tuple[sqlite3.Row, sqlite3.Row]:
    lobby = _lobby(lobby_id)
    member = _member(lobby_id, g.user["id"])
    if not lobby or not member or member["status"] != "active":
        abort(404)
    return lobby, member


def _lobby_rows(user_id: int) -> list[dict[str, Any]]:
    rows = _db().execute(
        """
        SELECT cl.*, u.display_name AS host_name,
               COUNT(CASE WHEN cm.status = 'active' THEN 1 END) AS member_count,
               MAX(CASE WHEN cm.user_id = ? AND cm.status = 'active' THEN 1 ELSE 0 END) AS is_member,
               MAX(CASE WHEN cm.user_id = ? AND cm.status = 'left' AND cl.status = 'playing'
                    AND EXISTS (SELECT 1 FROM json_each(cl.state_json, '$.participants') p
                        WHERE CAST(json_extract(p.value, '$.id') AS TEXT) = CAST(cm.id AS TEXT))
                    THEN 1 ELSE 0 END) AS is_reserved
        FROM conquest_lobbies cl
        JOIN users u ON u.id = cl.host_user_id
        LEFT JOIN conquest_members cm ON cm.lobby_id = cl.id
        WHERE cl.status IN ('waiting', 'playing') OR (cl.status = 'completed' AND EXISTS (
            SELECT 1 FROM conquest_members mine WHERE mine.lobby_id = cl.id AND mine.user_id = ? AND mine.status = 'active'))
        GROUP BY cl.id
        ORDER BY cl.created_at DESC
        """,
        (user_id, user_id, user_id),
    ).fetchall()
    # A legacy configured limit must not override the number of actual joins.
    return [{key: row[key] for key in row.keys() if key != 'player_limit'} for row in rows]


def _archive_game(lobby):
    if lobby['status'] == 'completed' and lobby['state_json']:
        _db().execute('''INSERT OR IGNORE INTO conquest_game_history
            (lobby_id,completed_revision,state_json,started_at,completed_at) VALUES (?,?,?,?,?)''',
            (lobby['id'], lobby['revision'], lobby['state_json'], lobby['started_at'], lobby['completed_at']))


def _overview_signature(rows):
    # Only refresh when information actually shown in the overview changes.
    fields = ('id', 'name', 'status', 'member_count', 'host_user_id', 'host_name',
              'victory_mode', 'is_member', 'is_reserved')
    return json.dumps([[row[key] for key in fields] for row in rows], ensure_ascii=False, separators=(',', ':'))


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
    """Assign countries automatically, then let players place their remaining armies."""
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
    first_member_id, opening_rolls = _first_player(members)
    missions: dict[str, str] = {}
    if victory_mode == "missions":
        active_colors = set(_member_colors(members).values())
        mission_rows = [
            row for row in world["missions"]
            if row["id"] not in COLOR_SEATS or COLOR_SEATS[row["id"]] in active_colors
        ]
        secrets.SystemRandom().shuffle(mission_rows)
        missions = {str(row["id"]): mission_rows[index]["id"] for index, row in enumerate(members)}
    return {
        "phase": "setup",
        "participants": [dict(id=str(row['id']), name=row['display_name'], color_index=_member_colors(members)[str(row['id'])]) for row in members],
        "round": 1,
        "current_member_id": first_member_id,
        "opening_rolls": opening_rolls,
        "territories": assignments,
        "missions": missions,
        "victory_mode": victory_mode,
        "captured_this_turn": False,
        "trade_count": 0,
        "hands": {str(row["id"]): [] for row in members},
        "remaining": army_count - len(owned[first_member_id]),
        "reinforcement": {"base": 0, "continents": [], "total": 0},
        "setup": {"remaining": {str(row["id"]): army_count - len(owned[row["id"]]) for row in members},
                  "initial_armies": army_count, "first_member_id": first_member_id,
                  "neutral_remaining": army_count - len(owned["neutral"]) if len(members) == 2 else 0,
                  "neutral_due": False, "own_in_turn": 0, "placed": 0, "complete": False},
    }


def _private_inventory(state: dict[str, Any], member_id: int) -> dict[str, Any]:
    """Expose only this member's persisted hand and assigned mission."""
    world = json.loads(WORLD_PATH.read_text(encoding="utf-8"))
    territories = {row["id"]: row for row in world["territories"]}
    own_cards = state.get("hands", {}).get(str(member_id), [])
    mission_id = state.get("missions", {}).get(str(member_id))
    return {
        "territory_cards": [
            {"id": card_id, "name": territories[card_id]["name"]}
            for card_id in own_cards
            if card_id in territories
        ],
        "mission": next((row for row in world["missions"] if row["id"] == mission_id), None),
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
        rows = _lobby_rows(g.user['id'])
        return render_overview('conquest_index.html', lobbies=rows)

    @app.get('/karten/welteroberung/uebersicht')
    @login_required
    def conquest_overview_status():
        return {'signature': _overview_signature(_lobby_rows(g.user['id']))}

    def render_room(lobby, member):
        members = _members(lobby['id'])
        state = json.loads(lobby['state_json'] or '{}')
        roster = []
        colors = _member_colors(members)
        known = {str(row['id']): dict(row) for row in _members(lobby['id'], include_left=True)}
        participants = state.get('participants') if lobby['status'] in ('playing', 'completed') else None
        for index, participant in enumerate(participants or [dict(row, name=row['display_name']) for row in members]):
            key = str(participant['id'])
            player = known.get(key)
            if not player:
                player = dict(id=key, user_id=None, display_name=participant['name'], status='active',
                              avatar_id='a00', plaque_id='p00', virtual=True)
            color_index = participant.get('color_index', index) if participants else colors[key]
            roster.append(dict(player, seat=index + 1, color=COLORS[color_index][0], color_index=color_index,
                               army_name=COLOR_NAMES[color_index]))
        return render_template('conquest_lobby.html', lobby=lobby, member=member,
            members=members, roster=roster, lobby_players=lobby_player_profiles(roster), figures=CONQUEST_FIGURES, styles=CONQUEST_STYLES,
            dice_choices=CONQUEST_DICE, victories=CONQUEST_VICTORIES, setups=CONQUEST_SETUPS, color_names=COLOR_NAMES,
            winner=state.get('winner'), is_active=member['status'] == 'active',
            can_develop=_developer_enabled() and len(members) == 1,
            waiting_for=_waiting_member(state, members) if state else None,
            history_count=_db().execute('SELECT COUNT(*) FROM conquest_game_history WHERE lobby_id=?', (lobby['id'],)).fetchone()[0])

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
        _db().execute('BEGIN IMMEDIATE')
        lobby = _lobby(lobby_id)
        existing = _member(lobby_id, g.user['id'])
        state = json.loads(lobby['state_json'] or '{}') if lobby else {}
        returning = bool(lobby and lobby['status'] == 'playing' and existing and
                         any(str(row['id']) == str(existing['id']) for row in state.get('participants', [])))
        if not lobby or (lobby['status'] != 'waiting' and not returning) or (not returning and len(_members(lobby_id)) >= CONQUEST_MAX_PLAYERS):
            _db().rollback()
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
            _db().rollback()
            return redirect(url_for("conquest_lobby", lobby_id=own["id"]))
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
        _db().execute('BEGIN IMMEDIATE')
        lobby = _lobby(lobby_id)
        if lobby["host_user_id"] != g.user["id"] or lobby["status"] != "waiting":
            abort(403)
        values = {
            key: request.form.get(key, lobby[key]) for key in
            ('board_style', 'card_style', 'figure_style', 'dice_style', 'victory_mode', 'setup_mode')
        }
        if values["board_style"] not in CONQUEST_STYLES or values["card_style"] not in CONQUEST_STYLES:
            abort(400)
        if values["figure_style"] not in CONQUEST_FIGURES or values["dice_style"] not in CONQUEST_DICE:
            abort(400)
        if values["victory_mode"] not in CONQUEST_VICTORIES or values["setup_mode"] not in CONQUEST_SETUPS:
            abort(400)
        name = ' '.join(request.form.get('name', lobby['name']).split())
        if not name or len(name) > 40 or any(ord(char) < 32 for char in name):
            abort(400)
        members = _members(lobby_id)
        try:
            colors = _member_colors(members)
            colors = {str(row['id']): int(request.form.get(f'color_{row["id"]}', colors[str(row['id'])])) for row in members}
        except (TypeError, ValueError):
            abort(400)
        if len(set(colors.values())) != len(colors) or any(color not in range(6) for color in colors.values()):
            return {'error': 'Wähle jede Armeefarbe nur einmal.'}, 400
        _db().execute(
            """
            UPDATE conquest_lobbies
            SET board_style = ?, card_style = ?, figure_style = ?, dice_style = ?,
                victory_mode = ?, setup_mode = ?, name = ?, revision = revision + 1
            WHERE id = ?
            """,
            (*values.values(), name, lobby_id),
        )
        for member_id, color in colors.items():
            _db().execute('UPDATE conquest_members SET color_index=? WHERE id=?', (color, member_id))
        _db().commit()
        if request.accept_mimetypes.best == 'application/json':
            return {'revision': lobby['revision'] + 1, 'name': name}
        return redirect(url_for("conquest_lobby", lobby_id=lobby_id))

    @app.post("/karten/welteroberung/<int:lobby_id>/starten")
    @login_required
    @active_view
    def conquest_start(lobby_id: int) -> Any:
        require_csrf()
        _db().execute("BEGIN IMMEDIATE")
        lobby = _lobby(lobby_id)
        members = _members(lobby_id)
        if lobby["host_user_id"] != g.user["id"] or lobby["status"] != "waiting":
            abort(403)
        developer_test = request.form.get("developer_test") == "1"
        if developer_test and (not _developer_enabled() or len(members) != 1):
            abort(403)
        if len(members) < CONQUEST_MIN_PLAYERS and not developer_test:
            _db().rollback()
            flash("Zum Start werden mindestens zwei Personen benötigt.", "error")
            return redirect(url_for("conquest_lobby", lobby_id=lobby_id))
        if lobby["setup_mode"] != "automatic":
            _db().rollback()
            flash("Die klassische Gebietswahl folgt als nächster Regelbaustein. Bitte vorerst automatisch verteilen.", "error")
            return redirect(url_for("conquest_lobby", lobby_id=lobby_id))
        participants = members if not developer_test else [dict(members[0]),
            {"id": "test-rot", "display_name": "Testarmee Rot"},
            {"id": "test-blau", "display_name": "Testarmee Blau"}]
        state = _prepare_automatic_state(participants, lobby["victory_mode"])
        state["developer_test"] = developer_test
        if developer_test:
            state["current_member_id"] = members[0]["id"]
            state["setup"]["first_member_id"] = members[0]["id"]
            state["remaining"] = state["setup"]["remaining"][str(members[0]["id"])]
        world = _world()
        hydrate(state, world, participants)
        check_victory(state, world)
        _db().execute(
            """
            UPDATE conquest_lobbies
            SET status = ?, state_json = ?, started_at = ?, completed_at = ?, revision = revision + 1
            WHERE id = ?
            """,
            ("completed" if state.get("winner") else "playing",
             json.dumps(state, ensure_ascii=False, separators=(",", ":")), _iso(),
             _iso() if state.get("winner") else None, lobby_id),
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
            return render_room(lobby, member)
        if lobby["status"] not in ("playing", "completed"):
            return redirect(url_for("conquest_index"))
        game = _game(lobby, member, members)
        return render_template(
            "conquest_table.html",
            lobby=lobby,
            member=member,
            members=members,
            table_config={"game": game, "revision": lobby["revision"],
                          "gameKey": f"{lobby_id}:{lobby['started_at']}",
                          "statusUrl": url_for("conquest_status", lobby_id=lobby_id),
                          "actionUrl": url_for("conquest_action", lobby_id=lobby_id),
                          "worldUrl": url_for("static", filename="conquest/world.json"),
                          "backUrl": url_for('conquest_room', lobby_id=lobby_id),
                          "overviewUrl": url_for('conquest_index'),
                          "csrfToken": session.setdefault("csrf_token", secrets.token_urlsafe(24))},
        )

    @app.get('/karten/welteroberung/<int:lobby_id>/lobby')
    @login_required
    def conquest_room(lobby_id):
        lobby, member = _lobby(lobby_id), _member(lobby_id, g.user['id'])
        if not lobby or not member:
            abort(404)
        return render_room(lobby, member)

    @app.get("/karten/welteroberung/<int:lobby_id>/status")
    @login_required
    def conquest_status(lobby_id: int) -> Any:
        lobby, member = _lobby(lobby_id), _member(lobby_id, g.user['id'])
        if not lobby or not member or (member['status'] != 'active' and lobby['status'] != 'closed'):
            abort(404)
        members = _members(lobby_id)
        colors = _member_colors(members)
        payload: dict[str, Any] = {
            "status": lobby["status"],
            "revision": lobby["revision"],
            'host_user_id': lobby['host_user_id'],
            'name': lobby['name'],
            "members": [{"id": row["id"], "name": row["display_name"], "seat": index + 1,
                         "color": COLORS[colors[str(row["id"])]][0], "army_name": COLOR_NAMES[colors[str(row["id"])]]} for index, row in enumerate(members)],
        }
        if lobby["status"] in ("playing", "completed") and lobby["state_json"]:
            payload["game"] = _game(lobby, member, members)
        return payload

    @app.get("/karten/welteroberung/tisch-assets/<path:filename>")
    @login_required
    def conquest_table_asset(filename: str) -> Any:
        shared_buttons = {
            'button-renderer.js': ('button-workshop-v1', 'renderer.js'),
            'geometry.js': ('button-workshop-v1', 'geometry.js'),
            'components.js': ('comic-ui-v1', 'components.js'),
            'button-materials.css': ('button-workshop-v1', 'materials.css'),
            'button-sound.js': ('button-workshop-v1', 'sound.js'),
            'button-assets/slate-v1.png': ('button-workshop-v1', 'assets/slate-v1.png'),
            'button-assets/audio/catalog.json': ('button-workshop-v1', 'assets/audio/catalog.json'),
            'button-assets/audio/wood-light.ogg': ('button-workshop-v1', 'assets/audio/wood-light.ogg'),
        }
        if filename in shared_buttons:
            folder, asset = shared_buttons[filename]
            response = send_from_directory(TABLE_PATH.parent / folder, asset)
            response.cache_control.no_cache = True
            return response
        if filename == 'player-portrait.js':
            response = send_from_directory(current_app.static_folder, filename)
            response.cache_control.no_cache = True
            return response
        allowed = {"scene.js", "camera.js", "territories.js", "territory-model.js", "table-surface.js",
                   "turn-controls.js", "turn-model.js", "remote-turn.js", "attack.js", "fortify.js", "cards.js", "style.css", "game-buttons.js", "button-profile.json",
                   "vendor/three/three.module.js", "vendor/three/three.core.js",
                   "assets/karte.png", "assets/raum-wand-v2.png", "assets/moebel-v2.png", "assets/teppich.png"}
        if filename not in allowed:
            abort(404)
        response = send_from_directory(TABLE_PATH, filename)
        response.cache_control.no_cache = True
        return response

    @app.post("/karten/welteroberung/<int:lobby_id>/aktion")
    @login_required
    @active_view
    def conquest_action(lobby_id: int) -> Any:
        require_csrf()
        database = _db()
        database.execute("BEGIN IMMEDIATE")
        lobby, member = _require_member(lobby_id)
        if lobby["status"] != "playing":
            database.rollback()
            return {"error": "Dieser Feldzug ist beendet. Weitere Züge sind nicht möglich."}, 409
        if request.form.get("revision") != str(lobby["revision"]):
            database.rollback()
            return {"error": "Der Spielstand wurde inzwischen geändert. Bitte erneut wählen."}, 409
        members = _members(lobby_id)
        world = _world()
        state = hydrate(json.loads(lobby["state_json"]), world, members, lobby["victory_mode"])
        waiting = _waiting_member(state, members)
        if waiting:
            database.rollback()
            return {'error': f'Warte auf {waiting}. Der Platz bleibt für die Rückkehr reserviert.'}, 409
        developer = bool(state.get("developer_test") and lobby["host_user_id"] == g.user["id"] and _developer_enabled())
        try:
            result = apply_action(state, world, request.form.get("action", ""), request.form, member["id"], developer)
        except (ValueError, PermissionError) as error:
            database.rollback()
            return {"error": str(error)}, 403 if isinstance(error, PermissionError) else 400
        status = "completed" if state.get("winner") else "playing"
        database.execute("UPDATE conquest_lobbies SET state_json = ?, status = ?, completed_at = ?, revision = revision + 1 WHERE id = ?",
                         (json.dumps(state, ensure_ascii=False, separators=(",", ":")), status,
                          _iso() if status == "completed" else None, lobby_id))
        fresh_lobby = _lobby(lobby_id)
        if status == 'completed':
            _archive_game(fresh_lobby)
        database.commit()
        return {"status": status, "revision": lobby["revision"] + 1,
                "game": _public_state(fresh_lobby, member, members, state, world), "result": result}

    @app.post("/karten/welteroberung/<int:lobby_id>/verlassen")
    @login_required
    @active_view
    def conquest_leave(lobby_id: int) -> Any:
        require_csrf()
        _db().execute('BEGIN IMMEDIATE')
        lobby, member = _require_member(lobby_id)
        _archive_game(lobby)
        _db().execute("UPDATE conquest_members SET status = 'left' WHERE id = ?", (member["id"],))
        remaining = _members(lobby_id)
        if not remaining:
            _db().execute(
                "UPDATE conquest_lobbies SET status = 'closed', completed_at = COALESCE(completed_at, ?), revision=revision+1 WHERE id = ?",
                (_iso(), lobby_id),
            )
        elif remaining and lobby["host_user_id"] == g.user["id"]:
            _db().execute(
                "UPDATE conquest_lobbies SET host_user_id = ?, revision = revision + 1 WHERE id = ?",
                (remaining[0]["user_id"], lobby_id),
            )
        else:
            _db().execute("UPDATE conquest_lobbies SET revision = revision + 1 WHERE id = ?", (lobby_id,))
        _db().commit()
        return lifecycle_redirect(url_for('conquest_index'))

    def lifecycle_redirect(destination):
        if request.accept_mimetypes.best == 'application/json':
            return {'redirect': destination}
        return redirect(destination)

    @app.post('/karten/welteroberung/<int:lobby_id>/beenden')
    @login_required
    def conquest_close(lobby_id):
        require_csrf()
        _db().execute('BEGIN IMMEDIATE')
        lobby, member = _require_member(lobby_id)
        if lobby['host_user_id'] != g.user['id']:
            abort(403)
        _archive_game(lobby)
        _db().execute("UPDATE conquest_members SET status='left' WHERE lobby_id=?", (lobby_id,))
        _db().execute("UPDATE conquest_lobbies SET status='closed',completed_at=COALESCE(completed_at,?),revision=revision+1 WHERE id=?", (_iso(), lobby_id))
        _db().commit()
        return lifecycle_redirect(url_for('conquest_index'))

    @app.post('/karten/welteroberung/<int:lobby_id>/nochmal')
    @login_required
    def conquest_rematch(lobby_id):
        require_csrf()
        _db().execute('BEGIN IMMEDIATE')
        lobby, member = _require_member(lobby_id)
        if lobby['host_user_id'] != g.user['id']:
            abort(403)
        if lobby['status'] != 'completed':
            _db().rollback()
            return {'error': 'Eine weitere Partie ist erst nach Spielende möglich.'}, 409
        if request.form.get('revision') != str(lobby['revision']):
            _db().rollback()
            return {'error': 'Die Lobby wurde inzwischen geändert. Bitte erneut wählen.'}, 409
        _archive_game(lobby)
        _db().execute("UPDATE conquest_lobbies SET status='waiting',state_json=NULL,started_at=NULL,completed_at=NULL,revision=revision+1 WHERE id=?", (lobby_id,))
        _db().commit()
        return lifecycle_redirect(url_for('conquest_room', lobby_id=lobby_id))
