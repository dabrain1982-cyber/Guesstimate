from __future__ import annotations

import hashlib
import json
import secrets
import sqlite3
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from typing import Any, Callable

from flask import (
    abort,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)


ROOT = Path(__file__).resolve().parent
PERFECT_MAX_PLAYERS = 8
PERFECT_DEFAULT_POINTS = 1500
PERFECT_DEFAULT_MINUTES = 30
PERFECT_MIN_POINTS = 500
PERFECT_MAX_POINTS = 5000
PERFECT_MIN_MINUTES = 5
PERFECT_MAX_MINUTES = 120
PERFECT_START_SECONDS = 4
PERFECT_ANSWER_SECONDS = 180
PERFECT_VOTE_SECONDS = 105
PERFECT_EARLY_SECONDS = 2
PERFECT_PRESENCE_WRITE_SECONDS = 3


def _load_json(relative: str) -> list[dict[str, Any]]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


QUESTION_BANKS: dict[str, list[dict[str, Any]]] = {
    "term": _load_json("fragen/stormseedsperfekt/begriffe/fragen.json"),
    "curiosity": _load_json("fragen/stormseedsperfekt/kuriositaeten/fragen.json"),
}


def init_nerd_db(get_db: Callable[[], sqlite3.Connection]) -> None:
    database = get_db()
    database.executescript(
        """
        CREATE TABLE IF NOT EXISTS nerd_lobbies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            host_user_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'waiting',
            goal_mode TEXT NOT NULL DEFAULT 'points',
            goal_value INTEGER NOT NULL DEFAULT 1500,
            round_index INTEGER NOT NULL DEFAULT 0,
            current_round_id INTEGER,
            last_category TEXT,
            next_category TEXT,
            countdown_ends_at TEXT,
            created_at TEXT NOT NULL,
            started_at TEXT,
            completed_at TEXT,
            paused_at TEXT,
            mode_version TEXT NOT NULL DEFAULT 'perfect-v1',
            FOREIGN KEY(host_user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS nerd_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lobby_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            score INTEGER NOT NULL DEFAULT 0,
            ready INTEGER NOT NULL DEFAULT 0,
            joined_at TEXT NOT NULL,
            last_seen_at TEXT,
            reaction TEXT,
            reaction_at TEXT,
            UNIQUE(lobby_id, user_id),
            FOREIGN KEY(lobby_id) REFERENCES nerd_lobbies(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS nerd_rounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lobby_id INTEGER NOT NULL,
            round_number INTEGER NOT NULL,
            category TEXT NOT NULL,
            question_id TEXT NOT NULL,
            question_json TEXT NOT NULL,
            phase TEXT NOT NULL DEFAULT 'question',
            options_json TEXT,
            resolution_json TEXT,
            phase_started_at TEXT NOT NULL,
            phase_ends_at TEXT NOT NULL,
            early_advance_at TEXT,
            completed_at TEXT,
            UNIQUE(lobby_id, round_number),
            FOREIGN KEY(lobby_id) REFERENCES nerd_lobbies(id)
        );

        CREATE TABLE IF NOT EXISTS nerd_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lobby_id INTEGER NOT NULL,
            round_id INTEGER NOT NULL,
            member_id INTEGER NOT NULL,
            answer_json TEXT,
            answer_locked_at TEXT,
            draft_vote_key TEXT,
            vote_key TEXT,
            vote_locked_at TEXT,
            host_equivalent INTEGER NOT NULL DEFAULT 0,
            base_points INTEGER NOT NULL DEFAULT 0,
            bluff_count INTEGER NOT NULL DEFAULT 0,
            points_awarded INTEGER NOT NULL DEFAULT 0,
            UNIQUE(round_id, member_id),
            FOREIGN KEY(lobby_id) REFERENCES nerd_lobbies(id),
            FOREIGN KEY(round_id) REFERENCES nerd_rounds(id),
            FOREIGN KEY(member_id) REFERENCES nerd_members(id)
        );

        CREATE TABLE IF NOT EXISTS nerd_chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lobby_id INTEGER NOT NULL,
            member_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(lobby_id) REFERENCES nerd_lobbies(id),
            FOREIGN KEY(member_id) REFERENCES nerd_members(id)
        );

        CREATE INDEX IF NOT EXISTS nerd_members_lobby_idx ON nerd_members(lobby_id);
        CREATE INDEX IF NOT EXISTS nerd_rounds_lobby_idx ON nerd_rounds(lobby_id);
        CREATE INDEX IF NOT EXISTS nerd_answers_round_idx ON nerd_answers(round_id);
        CREATE INDEX IF NOT EXISTS nerd_chat_lobby_idx ON nerd_chat_messages(lobby_id, id);

        CREATE TABLE IF NOT EXISTS perfect_question_usage (
            category TEXT NOT NULL,
            question_id TEXT NOT NULL,
            used_at TEXT NOT NULL,
            PRIMARY KEY(category, question_id)
        );
        """
    )
    database.execute(
        """
        INSERT OR IGNORE INTO perfect_question_usage(category, question_id, used_at)
        SELECT category, question_id, MIN(phase_started_at)
        FROM nerd_rounds
        WHERE category IN ('term', 'curiosity')
        GROUP BY category, question_id
        """
    )
    lobby_columns = {
        row["name"] for row in database.execute("PRAGMA table_info(nerd_lobbies)").fetchall()
    }
    if "mode_version" not in lobby_columns:
        database.execute("ALTER TABLE nerd_lobbies ADD COLUMN mode_version TEXT")
        database.execute(
            """
            UPDATE nerd_lobbies SET status = 'abandoned', completed_at = ?
            WHERE status IN ('waiting', 'countdown', 'playing')
            """,
            (_iso(),),
        )
        database.execute(
            "UPDATE nerd_lobbies SET mode_version = 'legacy-nerd' WHERE mode_version IS NULL"
        )
    if "paused_at" not in lobby_columns:
        database.execute("ALTER TABLE nerd_lobbies ADD COLUMN paused_at TEXT")
    answer_columns = {
        row["name"] for row in database.execute("PRAGMA table_info(nerd_answers)").fetchall()
    }
    if "draft_vote_key" not in answer_columns:
        database.execute("ALTER TABLE nerd_answers ADD COLUMN draft_vote_key TEXT")
    for table, legacy_columns in (
        ("nerd_lobbies", ("categories_json", "holdem_enabled")),
        ("nerd_members", ("chat_text", "chat_at")),
        ("nerd_answers", ("stake", "risk_points")),
    ):
        existing_columns = {
            row["name"]
            for row in database.execute(f"PRAGMA table_info({table})").fetchall()
        }
        for column in legacy_columns:
            if column in existing_columns:
                database.execute(f"ALTER TABLE {table} DROP COLUMN {column}")
    database.execute(
        """
        UPDATE nerd_lobbies SET goal_mode = 'points', goal_value = ?
        WHERE mode_version = 'perfect-v1' AND goal_mode = 'rounds'
        """,
        (PERFECT_DEFAULT_POINTS,),
    )
    database.execute(
        """
        UPDATE nerd_lobbies
        SET name = (
            SELECT u.display_name || '´s Runde'
            FROM users u WHERE u.id = nerd_lobbies.host_user_id
        )
        WHERE mode_version = 'perfect-v1' AND status = 'waiting'
          AND EXISTS (
              SELECT 1 FROM users u
              WHERE u.id = nerd_lobbies.host_user_id
                AND nerd_lobbies.name IN (
                    u.display_name || 's Lobby',
                    u.display_name || 's Runde',
                    u.display_name || ' Runde'
                )
          )
        """
    )
    database.commit()


def _now() -> datetime:
    return datetime.now()


def _iso(value: datetime | None = None) -> str:
    return (value or _now()).isoformat(timespec="microseconds")


def _csrf() -> None:
    token = request.form.get("csrf_token", "")
    if not token or not secrets.compare_digest(token, session.get("csrf_token", "")):
        abort(400)


def _login_required(view):
    @wraps(view)
    def wrapped(**kwargs):
        if g.user is None:
            return redirect(url_for("login"))
        return view(**kwargs)

    return wrapped


def _db() -> sqlite3.Connection:
    from flask import current_app

    return current_app.get_db()  # type: ignore[attr-defined]


def _lobby(lobby_id: int) -> sqlite3.Row | None:
    return _db().execute(
        "SELECT * FROM nerd_lobbies WHERE id = ? AND mode_version = 'perfect-v1'",
        (lobby_id,),
    ).fetchone()


def _member(lobby_id: int, user_id: int) -> sqlite3.Row | None:
    return _db().execute(
        "SELECT * FROM nerd_members WHERE lobby_id = ? AND user_id = ?",
        (lobby_id, user_id),
    ).fetchone()


def _members(lobby_id: int, *, active_only: bool = True) -> list[dict[str, Any]]:
    active = "AND nm.status = 'active'" if active_only else ""
    rows = _db().execute(
        f"""
        SELECT nm.*, u.display_name,
               COALESCE(uc.avatar_id, 'a00') AS avatar_id,
               COALESCE(uc.plaque_id, 'p00') AS plaque_id,
               COALESCE(uc.background_id, 'b00') AS background_id,
               COALESCE(uc.phrase_id, '') AS phrase_id
        FROM nerd_members nm
        JOIN users u ON u.id = nm.user_id
        LEFT JOIN user_cosmetics uc ON uc.user_id = u.id
        WHERE nm.lobby_id = ? {active}
        ORDER BY nm.joined_at, nm.id
        """,
        (lobby_id,),
    ).fetchall()
    members: list[dict[str, Any]] = []
    for row in rows:
        spent = _db().execute(
            "SELECT COALESCE(SUM(price), 0) FROM shop_purchases WHERE user_id = ?",
            (row["user_id"],),
        ).fetchone()[0]
        earned = _db().execute(
            """
            SELECT COALESCE(SUM(score), 0) FROM attempts
            WHERE user_id = ? AND status = 'completed'
            """,
            (row["user_id"],),
        ).fetchone()[0]
        item = dict(row)
        item["currency_balance"] = max(
            0,
            int(earned)
            - int(spent)
            + int(current_app.config.get("PREVIEW_CURRENCY_BONUS", 0)),
        )
        item["cosmetics"] = {
            "avatar_id": row["avatar_id"],
            "plaque_id": row["plaque_id"],
            "background_id": row["background_id"],
            "phrase_id": row["phrase_id"],
        }
        members.append(item)
    return members


def _round(lobby: sqlite3.Row | None) -> sqlite3.Row | None:
    if not lobby or not lobby["current_round_id"]:
        return None
    return _db().execute(
        "SELECT * FROM nerd_rounds WHERE id = ?", (lobby["current_round_id"],)
    ).fetchone()


def _touch(lobby_id: int, user_id: int) -> None:
    now = _now()
    member = _db().execute(
        """
        SELECT COALESCE(last_seen_at, joined_at) AS seen_at
        FROM nerd_members
        WHERE lobby_id = ? AND user_id = ? AND status = 'active'
        """,
        (lobby_id, user_id),
    ).fetchone()
    if member and now - datetime.fromisoformat(member["seen_at"]) >= timedelta(
        seconds=PERFECT_PRESENCE_WRITE_SECONDS
    ):
        _db().execute(
            """
            UPDATE nerd_members SET last_seen_at = ?
            WHERE lobby_id = ? AND user_id = ? AND status = 'active'
            """,
            (_iso(now), lobby_id, user_id),
        )
        _db().commit()


def _pick_question(
    database: sqlite3.Connection,
    category: str,
    excluded_ids: set[str] | None = None,
) -> dict[str, Any]:
    excluded_ids = excluded_ids or set()
    used = {
        row["question_id"]
        for row in database.execute(
            "SELECT question_id FROM perfect_question_usage WHERE category = ?",
            (category,),
        ).fetchall()
    }
    bank = QUESTION_BANKS[category]
    available = [
        item for item in bank
        if item["id"] not in used and item["id"] not in excluded_ids
    ]
    if not available:
        database.execute(
            "DELETE FROM perfect_question_usage WHERE category = ?", (category,)
        )
        available = [item for item in bank if item["id"] not in excluded_ids] or bank
    question = dict(secrets.choice(available))
    database.execute(
        """
        INSERT INTO perfect_question_usage(category, question_id, used_at)
        VALUES (?, ?, ?)
        """,
        (category, question["id"], _iso()),
    )
    return question


def _start_round(database: sqlite3.Connection, lobby: sqlite3.Row) -> None:
    round_number = int(lobby["round_index"]) + 1
    if round_number == 1:
        category = secrets.choice(("term", "curiosity"))
    else:
        category = "curiosity" if lobby["last_category"] == "term" else "term"
    question = _pick_question(database, category)
    now = _now()
    cursor = database.execute(
        """
        INSERT INTO nerd_rounds
            (lobby_id, round_number, category, question_id, question_json,
             phase, phase_started_at, phase_ends_at)
        VALUES (?, ?, ?, ?, ?, 'question', ?, ?)
        """,
        (
            lobby["id"],
            round_number,
            category,
            question["id"],
            json.dumps(question, ensure_ascii=False),
            _iso(now),
            _iso(now + timedelta(seconds=PERFECT_ANSWER_SECONDS)),
        ),
    )
    database.execute(
        """
        UPDATE nerd_lobbies SET status = 'playing',
               round_index = ?, current_round_id = ?,
               last_category = ?, next_category = NULL, countdown_ends_at = NULL
        WHERE id = ?
        """,
        (round_number, cursor.lastrowid, category, lobby["id"]),
    )
    database.execute(
        "UPDATE nerd_members SET ready = 0 WHERE lobby_id = ? AND status = 'active'",
        (lobby["id"],),
    )


def _ensure_answer_rows(
    database: sqlite3.Connection, lobby_id: int, round_id: int
) -> None:
    database.execute(
        """
        INSERT OR IGNORE INTO nerd_answers
            (lobby_id, round_id, member_id, answer_json, answer_locked_at)
        SELECT ?, ?, id, 'null', ? FROM nerd_members
        WHERE lobby_id = ? AND status = 'active'
        """,
        (lobby_id, round_id, _iso(), lobby_id),
    )


def _make_vote_options(
    database: sqlite3.Connection, nerd_round: sqlite3.Row
) -> list[dict[str, Any]]:
    question = json.loads(nerd_round["question_json"])
    options: list[dict[str, Any]] = [
        {"key": "solution", "text": str(question["answer"]), "author_member_id": None}
    ]
    rows = database.execute(
        """
        SELECT id, member_id, answer_json FROM nerd_answers
        WHERE round_id = ? AND answer_json IS NOT NULL AND answer_json != 'null'
        ORDER BY id
        """,
        (nerd_round["id"],),
    ).fetchall()
    for row in rows:
        text = str(json.loads(row["answer_json"]))
        if text.strip():
            options.append(
                {
                    "key": f"answer:{row['id']}",
                    "text": text,
                    "author_member_id": row["member_id"],
                }
            )
    options.sort(
        key=lambda item: hashlib.sha256(
            f"{nerd_round['id']}:{item['key']}".encode()
        ).hexdigest()
    )
    return options


def _resolve_round(
    database: sqlite3.Connection, lobby: sqlite3.Row, nerd_round: sqlite3.Row
) -> None:
    _ensure_answer_rows(database, lobby["id"], nerd_round["id"])
    question = json.loads(nerd_round["question_json"])
    rows = database.execute(
        """
        SELECT na.*, u.display_name, COALESCE(uc.avatar_id, 'a00') AS avatar_id
        FROM nerd_answers na
        JOIN nerd_members nm ON nm.id = na.member_id
        JOIN users u ON u.id = nm.user_id
        LEFT JOIN user_cosmetics uc ON uc.user_id = u.id
        WHERE na.round_id = ? AND nm.status = 'active'
        ORDER BY na.id
        """,
        (nerd_round["id"],),
    ).fetchall()
    by_id = {row["id"]: row for row in rows}
    bluff_counts = {row["id"]: 0 for row in rows}
    voters_by_key: dict[str, list[dict[str, str]]] = {}
    for voter in rows:
        key = voter["vote_key"] or ""
        if not key:
            continue
        voters_by_key.setdefault(key, []).append(
            {"name": voter["display_name"], "avatar_id": voter["avatar_id"]}
        )
        if key.startswith("answer:"):
            try:
                chosen = by_id.get(int(key.split(":", 1)[1]))
            except ValueError:
                chosen = None
            if chosen and chosen["member_id"] != voter["member_id"]:
                bluff_counts[chosen["id"]] += 1

    results: list[dict[str, Any]] = []
    for row in rows:
        chosen_key = row["vote_key"] or ""
        correct_vote = chosen_key == "solution"
        if chosen_key.startswith("answer:"):
            try:
                selected = by_id.get(int(chosen_key.split(":", 1)[1]))
            except ValueError:
                selected = None
            correct_vote = bool(selected and selected["host_equivalent"])
        fooled = bluff_counts[row["id"]]
        points = (100 if correct_vote else 0) + fooled * 100
        database.execute(
            "UPDATE nerd_members SET score = score + ? WHERE id = ?",
            (points, row["member_id"]),
        )
        database.execute(
            """
            UPDATE nerd_answers SET base_points = ?, bluff_count = ?,
                   points_awarded = ? WHERE id = ?
            """,
            (100 if correct_vote else 0, fooled, points, row["id"]),
        )
        results.append(
            {
                "member_id": row["member_id"],
                "answer_id": row["id"],
                "name": row["display_name"],
                "answer": json.loads(row["answer_json"] or "null"),
                "vote_key": chosen_key,
                "correct_vote": correct_vote,
                "host_equivalent": bool(row["host_equivalent"]),
                "bluffs": fooled,
                "points": points,
                "voters": voters_by_key.get(f"answer:{row['id']}", []),
            }
        )

    now = _now()
    resolution = {
        "answer": question["answer"],
        "explanation": question.get("explanation", ""),
        "solution_voters": voters_by_key.get("solution", []),
        "results": results,
    }
    database.execute(
        """
        UPDATE nerd_rounds SET phase = 'resolution', resolution_json = ?,
               phase_started_at = ?, phase_ends_at = ?, early_advance_at = NULL,
               completed_at = ? WHERE id = ?
        """,
        (
            json.dumps(resolution, ensure_ascii=False),
            _iso(now),
            _iso(now + timedelta(days=1)),
            _iso(now),
            nerd_round["id"],
        ),
    )


def refresh_nerd_lobby(lobby_id: int) -> sqlite3.Row | None:
    database = _db()
    try:
        database.execute("BEGIN IMMEDIATE")
    except sqlite3.OperationalError:
        return _lobby(lobby_id)
    lobby = database.execute(
        "SELECT * FROM nerd_lobbies WHERE id = ? AND mode_version = 'perfect-v1'",
        (lobby_id,),
    ).fetchone()
    if not lobby:
        database.rollback()
        return None
    now = _now()
    # "away" was only ever produced by the removed presence timeout. Restore
    # those seats; only an explicit leave action may remove a player now.
    database.execute(
        "UPDATE nerd_members SET status = 'active' WHERE lobby_id = ? AND status = 'away'",
        (lobby_id,),
    )
    members = database.execute(
        "SELECT * FROM nerd_members WHERE lobby_id = ? AND status = 'active' ORDER BY id",
        (lobby_id,),
    ).fetchall()
    if not members and lobby["status"] in ("waiting", "countdown", "playing"):
        database.execute(
            "UPDATE nerd_lobbies SET status = 'abandoned', completed_at = ? WHERE id = ?",
            (_iso(now), lobby_id),
        )
        database.commit()
        return _lobby(lobby_id)
    if members and not any(row["user_id"] == lobby["host_user_id"] for row in members):
        database.execute(
            "UPDATE nerd_lobbies SET host_user_id = ? WHERE id = ?",
            (members[0]["user_id"], lobby_id),
        )
        lobby = database.execute(
            "SELECT * FROM nerd_lobbies WHERE id = ?", (lobby_id,)
        ).fetchone()

    if lobby["paused_at"]:
        database.commit()
        return _lobby(lobby_id)

    if (
        lobby["status"] == "countdown"
        and lobby["countdown_ends_at"]
        and now >= datetime.fromisoformat(lobby["countdown_ends_at"])
    ):
        _start_round(database, lobby)
    elif lobby["status"] == "playing":
        nerd_round = database.execute(
            "SELECT * FROM nerd_rounds WHERE id = ?", (lobby["current_round_id"],)
        ).fetchone()
        if nerd_round:
            active_count = len(members)
            phase = nerd_round["phase"]
            if phase == "question":
                locked = database.execute(
                    """
                    SELECT COUNT(*) FROM nerd_answers na
                    JOIN nerd_members nm ON nm.id = na.member_id
                    WHERE na.round_id = ? AND nm.status = 'active'
                      AND na.answer_locked_at IS NOT NULL
                    """,
                    (nerd_round["id"],),
                ).fetchone()[0]
                if active_count and locked >= active_count and not nerd_round["early_advance_at"]:
                    database.execute(
                        "UPDATE nerd_rounds SET early_advance_at = ? WHERE id = ?",
                        (_iso(now + timedelta(seconds=PERFECT_EARLY_SECONDS)), nerd_round["id"]),
                    )
                    nerd_round = database.execute(
                        "SELECT * FROM nerd_rounds WHERE id = ?", (nerd_round["id"],)
                    ).fetchone()
                deadline = min(
                    datetime.fromisoformat(nerd_round["phase_ends_at"]),
                    datetime.fromisoformat(nerd_round["early_advance_at"])
                    if nerd_round["early_advance_at"]
                    else datetime.max,
                )
                if now >= deadline:
                    database.execute(
                        """
                        UPDATE nerd_answers SET answer_locked_at = ?
                        WHERE round_id = ? AND answer_locked_at IS NULL
                          AND answer_json IS NOT NULL AND answer_json != 'null'
                        """,
                        (_iso(now), nerd_round["id"]),
                    )
                    _ensure_answer_rows(database, lobby_id, nerd_round["id"])
                    options = _make_vote_options(database, nerd_round)
                    database.execute(
                        """
                        UPDATE nerd_rounds SET phase = 'vote', options_json = ?,
                               phase_started_at = ?, phase_ends_at = ?,
                               early_advance_at = NULL WHERE id = ?
                        """,
                        (
                            json.dumps(options, ensure_ascii=False),
                            _iso(now),
                            _iso(now + timedelta(seconds=PERFECT_VOTE_SECONDS)),
                            nerd_round["id"],
                        ),
                    )
            elif phase == "vote":
                voted = database.execute(
                    """
                    SELECT COUNT(*) FROM nerd_answers na
                    JOIN nerd_members nm ON nm.id = na.member_id
                    WHERE na.round_id = ? AND nm.status = 'active'
                      AND na.vote_locked_at IS NOT NULL
                    """,
                    (nerd_round["id"],),
                ).fetchone()[0]
                if active_count and voted >= active_count and not nerd_round["early_advance_at"]:
                    database.execute(
                        "UPDATE nerd_rounds SET early_advance_at = ? WHERE id = ?",
                        (_iso(now + timedelta(seconds=PERFECT_EARLY_SECONDS)), nerd_round["id"]),
                    )
                    nerd_round = database.execute(
                        "SELECT * FROM nerd_rounds WHERE id = ?", (nerd_round["id"],)
                    ).fetchone()
                deadline = min(
                    datetime.fromisoformat(nerd_round["phase_ends_at"]),
                    datetime.fromisoformat(nerd_round["early_advance_at"])
                    if nerd_round["early_advance_at"]
                    else datetime.max,
                )
                if now >= deadline:
                    database.execute(
                        """
                        UPDATE nerd_answers
                        SET vote_key = draft_vote_key, vote_locked_at = ?
                        WHERE round_id = ? AND vote_locked_at IS NULL
                          AND draft_vote_key IS NOT NULL
                        """,
                        (_iso(now), nerd_round["id"]),
                    )
                    database.execute(
                        """
                        UPDATE nerd_rounds SET phase = 'review',
                               phase_started_at = ?, phase_ends_at = ?,
                               early_advance_at = NULL WHERE id = ?
                        """,
                        (_iso(now), _iso(now + timedelta(days=1)), nerd_round["id"]),
                    )
    database.commit()
    return _lobby(lobby_id)


def _active_lobbies(user_id: int) -> list[sqlite3.Row]:
    return _db().execute(
        """
        SELECT nl.*, u.display_name AS host_name,
               COALESCE(uc.avatar_id, 'a00') AS host_avatar_id,
               COUNT(CASE WHEN nm.status = 'active' THEN 1 END) AS member_count,
               MAX(CASE WHEN nm.user_id = ? AND nm.status = 'active' THEN 1 ELSE 0 END)
                   AS is_member
        FROM nerd_lobbies nl
        JOIN users u ON u.id = nl.host_user_id
        LEFT JOIN user_cosmetics uc ON uc.user_id = u.id
        LEFT JOIN nerd_members nm ON nm.lobby_id = nl.id
        WHERE nl.status IN ('waiting','countdown','playing')
          AND nl.mode_version = 'perfect-v1'
        GROUP BY nl.id
        ORDER BY nl.created_at DESC
        """,
        (user_id,),
    ).fetchall()


def _goal_reached(database: sqlite3.Connection, lobby: sqlite3.Row) -> bool:
    if lobby["goal_mode"] == "points":
        highest = database.execute(
            """
            SELECT COALESCE(MAX(score), 0) FROM nerd_members
            WHERE lobby_id = ? AND status = 'active'
            """,
            (lobby["id"],),
        ).fetchone()[0]
        return int(highest) >= int(lobby["goal_value"])
    if lobby["goal_mode"] == "time" and lobby["started_at"]:
        game_end = datetime.fromisoformat(lobby["started_at"]) + timedelta(
            minutes=int(lobby["goal_value"])
        )
        return _now() >= game_end
    return False


def _game_deadline(lobby: sqlite3.Row) -> str | None:
    if lobby["goal_mode"] != "time" or not lobby["started_at"]:
        return None
    return _iso(
        datetime.fromisoformat(lobby["started_at"])
        + timedelta(minutes=int(lobby["goal_value"]))
    )


def _lobby_signature(lobby: sqlite3.Row, members: list[dict[str, Any]]) -> str:
    round_state = None
    if lobby["current_round_id"]:
        round_state = _db().execute(
            "SELECT question_id, phase FROM nerd_rounds WHERE id = ?",
            (lobby["current_round_id"],),
        ).fetchone()
    source = "|".join(
        (
            str(lobby["host_user_id"]),
            lobby["name"],
            lobby["status"],
            lobby["paused_at"] or "",
            str(lobby["round_index"]),
            lobby["goal_mode"],
            str(lobby["goal_value"]),
            (
                f"{round_state['question_id']}:{round_state['phase']}"
                if round_state else ""
            ),
            ",".join(
                f"{row['id']}:{row['ready']}:{row['score']}"
                for row in members
            ),
        )
    )
    return hashlib.sha256(source.encode()).hexdigest()[:16]


def _view_data(lobby: sqlite3.Row, member: sqlite3.Row) -> dict[str, Any]:
    members = _members(lobby["id"])
    member = next(row for row in members if row["user_id"] == member["user_id"])
    nerd_round = _round(lobby)
    answer = None
    answer_text = None
    question = None
    options: list[dict[str, Any]] = []
    resolution = None
    if nerd_round:
        question = json.loads(nerd_round["question_json"])
        options = json.loads(nerd_round["options_json"] or "[]")
        resolution = json.loads(nerd_round["resolution_json"] or "null")
        answer = _db().execute(
            "SELECT * FROM nerd_answers WHERE round_id = ? AND member_id = ?",
            (nerd_round["id"], member["id"]),
        ).fetchone()
        if answer and answer["answer_json"] not in (None, "null"):
            answer_text = json.loads(answer["answer_json"])
    leaderboard = sorted(
        members, key=lambda row: (-int(row["score"]), row["joined_at"], row["id"])
    )
    member_states = {
        row["id"]: {
            "answered": False,
            "voted": False,
            "ready": bool(row["ready"]),
        }
        for row in members
    }
    if nerd_round:
        vote_rows = _db().execute(
            """
            SELECT member_id, answer_locked_at, draft_vote_key, vote_locked_at
            FROM nerd_answers WHERE round_id = ?
            """,
            (nerd_round["id"],),
        ).fetchall()
        for row in vote_rows:
            if row["member_id"] in member_states:
                member_states[row["member_id"]]["answered"] = bool(row["answer_locked_at"])
                member_states[row["member_id"]]["voted"] = bool(row["vote_locked_at"])
    host_review_answers: list[dict[str, Any]] = []
    if nerd_round and nerd_round["phase"] == "review":
        host_review_answers = [
            {**dict(row), "answer_text": json.loads(row["answer_json"])}
            for row in _db().execute(
                """
                SELECT na.*, u.display_name FROM nerd_answers na
                JOIN nerd_members nm ON nm.id = na.member_id
                JOIN users u ON u.id = nm.user_id
                WHERE na.round_id = ? AND na.answer_json IS NOT NULL
                  AND na.answer_json != 'null'
                ORDER BY na.id
                """,
                (nerd_round["id"],),
            ).fetchall()
        ]
    deadline = None
    if lobby["status"] == "countdown":
        deadline = lobby["countdown_ends_at"]
    elif nerd_round and nerd_round["phase"] in ("question", "vote"):
        deadline = nerd_round["early_advance_at"] or nerd_round["phase_ends_at"]
    return {
        "lobby": lobby,
        "member": member,
        "members": members,
        "round": nerd_round,
        "question": question,
        "answer": answer,
        "answer_text": answer_text,
        "options": options,
        "resolution": resolution,
        "leaderboard": leaderboard,
        "member_states": member_states,
        "host_review_answers": host_review_answers,
        "deadline": deadline,
        "lobby_signature": _lobby_signature(lobby, members),
        "goal_reached": bool(
            nerd_round
            and nerd_round["phase"] == "resolution"
            and _goal_reached(_db(), lobby)
        ),
        "game_deadline": _game_deadline(lobby),
        "is_paused": bool(lobby["paused_at"]),
    }


def register_nerd_routes(app) -> None:
    app.config["PERFECT_MAX_PLAYERS"] = PERFECT_MAX_PLAYERS

    @app.get("/nerd")
    @_login_required
    def nerd_index():
        lobbies = _active_lobbies(g.user["id"])
        for lobby in lobbies:
            refresh_nerd_lobby(lobby["id"])
        lobbies = _active_lobbies(g.user["id"])
        own = next((row for row in lobbies if row["is_member"]), None)
        if own:
            return redirect(url_for("nerd_lobby", lobby_id=own["id"]))
        return render_template("nerd_index.html", lobbies=lobbies)

    @app.post("/nerd/erstellen")
    @_login_required
    def nerd_create():
        _csrf()
        database = _db()
        database.execute("BEGIN IMMEDIATE")
        own = database.execute(
            """
            SELECT nl.id FROM nerd_lobbies nl
            JOIN nerd_members nm ON nm.lobby_id = nl.id
            WHERE nm.user_id = ? AND nm.status = 'active'
              AND nl.status IN ('waiting','countdown','playing')
              AND nl.mode_version = 'perfect-v1'
            """,
            (g.user["id"],),
        ).fetchone()
        if own:
            database.rollback()
            return redirect(url_for("nerd_lobby", lobby_id=own["id"]))
        now = _iso()
        lobby_id = database.execute(
            """
            INSERT INTO nerd_lobbies
                (name, host_user_id, goal_mode, goal_value, created_at, mode_version)
            VALUES (?, ?, 'points', ?, ?, 'perfect-v1')
            """,
            (
                f"{g.user['display_name']}´s Runde",
                g.user["id"],
                PERFECT_DEFAULT_POINTS,
                now,
            ),
        ).lastrowid
        database.execute(
            """
            INSERT INTO nerd_members
                (lobby_id, user_id, ready, joined_at, last_seen_at)
            VALUES (?, ?, 1, ?, ?)
            """,
            (lobby_id, g.user["id"], now, now),
        )
        database.commit()
        return redirect(url_for("nerd_lobby", lobby_id=lobby_id))

    @app.post("/nerd/<int:lobby_id>/beitreten")
    @_login_required
    def nerd_join(lobby_id: int):
        _csrf()
        database = _db()
        database.execute("BEGIN IMMEDIATE")
        lobby = database.execute(
            "SELECT * FROM nerd_lobbies WHERE id = ? AND mode_version = 'perfect-v1'",
            (lobby_id,),
        ).fetchone()
        count = database.execute(
            "SELECT COUNT(*) FROM nerd_members WHERE lobby_id = ? AND status = 'active'",
            (lobby_id,),
        ).fetchone()[0]
        existing = database.execute(
            "SELECT * FROM nerd_members WHERE lobby_id = ? AND user_id = ?",
            (lobby_id, g.user["id"]),
        ).fetchone()
        other = database.execute(
            """
            SELECT nl.id FROM nerd_lobbies nl
            JOIN nerd_members nm ON nm.lobby_id = nl.id
            WHERE nm.user_id = ? AND nm.status = 'active' AND nl.id != ?
              AND nl.status IN ('waiting','countdown','playing')
              AND nl.mode_version = 'perfect-v1'
            """,
            (g.user["id"], lobby_id),
        ).fetchone()
        can_return = bool(
            existing
            and existing["status"] in ("left", "away")
            and lobby
            and lobby["status"] == "waiting"
        )
        if (
            other
            or not lobby
            or lobby["status"] != "waiting"
            or count >= PERFECT_MAX_PLAYERS
            or (existing and not can_return)
        ):
            database.rollback()
            flash("Dieser Runde kannst du gerade nicht beitreten.", "error")
            return redirect(url_for("nerd_index"))
        now = _iso()
        if can_return:
            database.execute(
                """
                UPDATE nerd_members SET status = 'active', score = 0, ready = 0,
                       last_seen_at = ? WHERE id = ?
                """,
                (now, existing["id"]),
            )
        else:
            database.execute(
                """
                INSERT INTO nerd_members
                    (lobby_id, user_id, ready, joined_at, last_seen_at)
                VALUES (?, ?, 0, ?, ?)
                """,
                (lobby_id, g.user["id"], now, now),
            )
        database.commit()
        return redirect(url_for("nerd_lobby", lobby_id=lobby_id))

    @app.get("/nerd/<int:lobby_id>")
    @_login_required
    def nerd_lobby(lobby_id: int):
        member = _member(lobby_id, g.user["id"])
        if member and member["status"] == "active":
            _touch(lobby_id, g.user["id"])
        lobby = refresh_nerd_lobby(lobby_id)
        member = _member(lobby_id, g.user["id"])
        if not lobby or not member or member["status"] != "active":
            return redirect(url_for("nerd_index"))
        return render_template("nerd_mode.html", **_view_data(lobby, member))

    @app.get("/nerd/<int:lobby_id>/status")
    @_login_required
    def nerd_status(lobby_id: int):
        member = _member(lobby_id, g.user["id"])
        if member and member["status"] == "active":
            _touch(lobby_id, g.user["id"])
        lobby = refresh_nerd_lobby(lobby_id)
        member = _member(lobby_id, g.user["id"])
        if not lobby or not member or member["status"] != "active":
            return {"status": "unavailable"}, 404
        nerd_round = _round(lobby)
        members = _members(lobby_id)
        answers = []
        if nerd_round:
            answers = [
                dict(row)
                for row in _db().execute(
                    """
                    SELECT na.member_id, na.answer_locked_at,
                           na.vote_locked_at
                    FROM nerd_answers na
                    JOIN nerd_members nm ON nm.id = na.member_id
                    JOIN users u ON u.id = nm.user_id
                    WHERE na.round_id = ?
                    """,
                    (nerd_round["id"],),
                ).fetchall()
            ]
        phase = (
            "finale"
            if lobby["status"] == "completed"
            else nerd_round["phase"]
            if nerd_round
            else ("lobby" if lobby["status"] == "waiting" else lobby["status"])
        )
        return {
            "status": lobby["status"],
            "phase": phase,
            "round_id": nerd_round["id"] if nerd_round else None,
            "lobby_signature": _lobby_signature(lobby, members),
            "deadline": (
                nerd_round["early_advance_at"] or nerd_round["phase_ends_at"]
                if nerd_round and phase in ("question", "vote")
                else lobby["countdown_ends_at"]
                if lobby["status"] == "countdown"
                else None
            ),
            "members": [
                {
                    "id": row["id"],
                    "score": row["score"],
                    "ready": bool(row["ready"]),
                }
                for row in members
            ],
            "answers": answers,
        }

    @app.post("/nerd/<int:lobby_id>/einstellungen")
    @_login_required
    def nerd_settings(lobby_id: int):
        _csrf()
        lobby = _lobby(lobby_id)
        if (
            not lobby
            or lobby["host_user_id"] != g.user["id"]
            or lobby["status"] != "waiting"
        ):
            abort(403)
        name = " ".join(request.form.get("name", "").strip().split())[:36]
        goal_mode = request.form.get("goal_mode", "")
        if goal_mode not in ("points", "time"):
            abort(400)
        try:
            submitted_goal = int(request.form.get("goal_value", ""))
        except ValueError:
            abort(400)
        if goal_mode == "points":
            goal_value = max(
                PERFECT_MIN_POINTS,
                min(PERFECT_MAX_POINTS, (submitted_goal // 100) * 100),
            )
        else:
            goal_value = max(
                PERFECT_MIN_MINUTES,
                min(PERFECT_MAX_MINUTES, (submitted_goal // 5) * 5),
            )
        goal_changed = (
            goal_mode != lobby["goal_mode"] or goal_value != int(lobby["goal_value"])
        )
        _db().execute(
            "UPDATE nerd_lobbies SET name = ?, goal_mode = ?, goal_value = ? WHERE id = ?",
            (name or lobby["name"], goal_mode, goal_value, lobby_id),
        )
        if goal_changed:
            _db().execute(
                """
                UPDATE nerd_members SET ready = 0
                WHERE lobby_id = ? AND status = 'active' AND user_id != ?
                """,
                (lobby_id, g.user["id"]),
            )
        _db().commit()
        if request.accept_mimetypes.best == "application/json":
            return {"saved": True}
        return redirect(url_for("nerd_lobby", lobby_id=lobby_id))

    @app.post("/nerd/<int:lobby_id>/ready")
    @_login_required
    def nerd_ready(lobby_id: int):
        _csrf()
        lobby = _lobby(lobby_id)
        member = _member(lobby_id, g.user["id"])
        if (
            lobby
            and member
            and member["status"] == "active"
            and lobby["status"] == "waiting"
            and lobby["host_user_id"] != g.user["id"]
        ):
            _db().execute(
                "UPDATE nerd_members SET ready = ? WHERE id = ?",
                (0 if member["ready"] else 1, member["id"]),
            )
            _db().commit()
        return redirect(url_for("nerd_lobby", lobby_id=lobby_id))

    @app.post("/nerd/<int:lobby_id>/start")
    @_login_required
    def nerd_start(lobby_id: int):
        _csrf()
        lobby = _lobby(lobby_id)
        members = _members(lobby_id) if lobby else []
        if (
            not lobby
            or lobby["host_user_id"] != g.user["id"]
            or lobby["status"] != "waiting"
        ):
            abort(403)
        guests = [row for row in members if row["user_id"] != g.user["id"]]
        if not guests:
            flash("Zum Start wird mindestens ein Mitspieler benötigt.", "error")
        elif not all(row["ready"] for row in guests):
            flash("Noch sind nicht alle Mitspieler bereit.", "error")
        else:
            end = _now() + timedelta(seconds=PERFECT_START_SECONDS)
            _db().execute(
                """
                UPDATE nerd_lobbies SET status = 'countdown',
                       countdown_ends_at = ?, started_at = ? WHERE id = ?
                """,
                (_iso(end), _iso(end), lobby_id),
            )
            _db().commit()
        return redirect(url_for("nerd_lobby", lobby_id=lobby_id))

    @app.post("/nerd/<int:lobby_id>/antwort")
    @_login_required
    def nerd_answer(lobby_id: int):
        _csrf()
        lobby = refresh_nerd_lobby(lobby_id)
        member = _member(lobby_id, g.user["id"])
        nerd_round = _round(lobby)
        if (
            not lobby
            or lobby["paused_at"]
            or not member
            or member["status"] != "active"
            or not nerd_round
            or nerd_round["phase"] != "question"
        ):
            return redirect(url_for("nerd_lobby", lobby_id=lobby_id))
        submitted = " ".join(request.form.get("answer", "").strip().split())[:220]
        if not submitted:
            flash("Bitte gib zuerst deine Antwort ein.", "error")
            return redirect(url_for("nerd_lobby", lobby_id=lobby_id))
        cursor = _db().execute(
            """
            INSERT INTO nerd_answers
                (lobby_id, round_id, member_id, answer_json, answer_locked_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(round_id, member_id) DO UPDATE SET
                answer_json = excluded.answer_json,
                answer_locked_at = excluded.answer_locked_at
            WHERE nerd_answers.answer_locked_at IS NULL
            """,
            (
                lobby_id,
                nerd_round["id"],
                member["id"],
                json.dumps(submitted, ensure_ascii=False),
                _iso(),
            ),
        )
        _db().commit()
        if not cursor.rowcount:
            return redirect(url_for("nerd_lobby", lobby_id=lobby_id))
        refresh_nerd_lobby(lobby_id)
        return redirect(url_for("nerd_lobby", lobby_id=lobby_id))

    @app.post("/nerd/<int:lobby_id>/antwort-entwurf")
    @_login_required
    def nerd_answer_draft(lobby_id: int):
        _csrf()
        lobby = _lobby(lobby_id)
        member = _member(lobby_id, g.user["id"])
        nerd_round = _round(lobby)
        if (
            not lobby
            or lobby["paused_at"]
            or not member
            or member["status"] != "active"
            or not nerd_round
            or nerd_round["phase"] != "question"
        ):
            return {"saved": False}, 409
        submitted = " ".join(request.form.get("answer", "").strip().split())[:220]
        _db().execute(
            """
            INSERT INTO nerd_answers
                (lobby_id, round_id, member_id, answer_json, answer_locked_at)
            VALUES (?, ?, ?, ?, NULL)
            ON CONFLICT(round_id, member_id) DO UPDATE SET answer_json = excluded.answer_json
            WHERE nerd_answers.answer_locked_at IS NULL
            """,
            (
                lobby_id,
                nerd_round["id"],
                member["id"],
                json.dumps(submitted, ensure_ascii=False) if submitted else "null",
            ),
        )
        _db().commit()
        return {"saved": True}

    @app.post("/nerd/<int:lobby_id>/wahl")
    @_login_required
    def nerd_vote(lobby_id: int):
        _csrf()
        lobby = refresh_nerd_lobby(lobby_id)
        member = _member(lobby_id, g.user["id"])
        nerd_round = _round(lobby)
        if (
            not lobby
            or lobby["paused_at"]
            or not member
            or not nerd_round
            or nerd_round["phase"] != "vote"
        ):
            return redirect(url_for("nerd_lobby", lobby_id=lobby_id))
        answer = _db().execute(
            "SELECT * FROM nerd_answers WHERE round_id = ? AND member_id = ?",
            (nerd_round["id"], member["id"]),
        ).fetchone()
        options = json.loads(nerd_round["options_json"] or "[]")
        allowed = {
            item["key"]
            for item in options
            if item.get("author_member_id") != member["id"]
        }
        choice = request.form.get("vote_key", "")
        if answer and answer["vote_locked_at"] is None and choice in allowed:
            _db().execute(
                """
                UPDATE nerd_answers SET draft_vote_key = ?, vote_key = ?,
                       vote_locked_at = ? WHERE id = ?
                """,
                (choice, choice, _iso(), answer["id"]),
            )
            _db().commit()
            refresh_nerd_lobby(lobby_id)
        return redirect(url_for("nerd_lobby", lobby_id=lobby_id))

    @app.post("/nerd/<int:lobby_id>/wahl-entwurf")
    @_login_required
    def nerd_vote_draft(lobby_id: int):
        _csrf()
        lobby = _lobby(lobby_id)
        member = _member(lobby_id, g.user["id"])
        nerd_round = _round(lobby)
        if (
            not lobby
            or lobby["paused_at"]
            or not member
            or not nerd_round
            or nerd_round["phase"] != "vote"
        ):
            return {"saved": False}, 409
        answer = _db().execute(
            "SELECT * FROM nerd_answers WHERE round_id = ? AND member_id = ?",
            (nerd_round["id"], member["id"]),
        ).fetchone()
        options = json.loads(nerd_round["options_json"] or "[]")
        allowed = {
            item["key"]
            for item in options
            if item.get("author_member_id") != member["id"]
        }
        choice = request.form.get("vote_key", "")
        if not answer or answer["vote_locked_at"] is not None or choice not in allowed:
            return {"saved": False}, 400
        _db().execute(
            "UPDATE nerd_answers SET draft_vote_key = ? WHERE id = ?",
            (choice, answer["id"]),
        )
        _db().commit()
        return {"saved": True}

    @app.post("/nerd/<int:lobby_id>/pause")
    @_login_required
    def nerd_pause(lobby_id: int):
        _csrf()
        database = _db()
        database.execute("BEGIN IMMEDIATE")
        lobby = database.execute(
            "SELECT * FROM nerd_lobbies WHERE id = ? AND mode_version = 'perfect-v1'",
            (lobby_id,),
        ).fetchone()
        if (
            not lobby
            or lobby["host_user_id"] != g.user["id"]
            or lobby["status"] not in ("countdown", "playing")
        ):
            database.rollback()
            abort(403)
        now = _now()
        if lobby["paused_at"]:
            pause_delta = now - datetime.fromisoformat(lobby["paused_at"])
            if lobby["countdown_ends_at"]:
                database.execute(
                    "UPDATE nerd_lobbies SET countdown_ends_at = ? WHERE id = ?",
                    (_iso(datetime.fromisoformat(lobby["countdown_ends_at"]) + pause_delta), lobby_id),
                )
            if lobby["started_at"]:
                database.execute(
                    "UPDATE nerd_lobbies SET started_at = ? WHERE id = ?",
                    (_iso(datetime.fromisoformat(lobby["started_at"]) + pause_delta), lobby_id),
                )
            nerd_round = _round(lobby)
            if nerd_round:
                database.execute(
                    """
                    UPDATE nerd_rounds SET phase_ends_at = ?,
                           early_advance_at = CASE WHEN early_advance_at IS NULL THEN NULL ELSE ? END
                    WHERE id = ?
                    """,
                    (
                        _iso(datetime.fromisoformat(nerd_round["phase_ends_at"]) + pause_delta),
                        _iso(datetime.fromisoformat(nerd_round["early_advance_at"]) + pause_delta)
                        if nerd_round["early_advance_at"] else None,
                        nerd_round["id"],
                    ),
                )
            database.execute("UPDATE nerd_lobbies SET paused_at = NULL WHERE id = ?", (lobby_id,))
        else:
            database.execute("UPDATE nerd_lobbies SET paused_at = ? WHERE id = ?", (_iso(now), lobby_id))
        database.commit()
        return redirect(url_for("nerd_lobby", lobby_id=lobby_id))

    @app.post("/nerd/<int:lobby_id>/naechste-frage")
    @_login_required
    def nerd_next_question(lobby_id: int):
        _csrf()
        refresh_nerd_lobby(lobby_id)
        database = _db()
        database.execute("BEGIN IMMEDIATE")
        lobby = database.execute(
            "SELECT * FROM nerd_lobbies WHERE id = ? AND mode_version = 'perfect-v1'",
            (lobby_id,),
        ).fetchone()
        nerd_round = _round(lobby)
        if (
            not lobby
            or lobby["host_user_id"] != g.user["id"]
            or lobby["status"] != "playing"
            or not nerd_round
            or nerd_round["phase"] != "question"
        ):
            database.rollback()
            abort(403)

        question = _pick_question(
            database,
            nerd_round["category"],
            {nerd_round["question_id"]},
        )
        phase_start = (
            datetime.fromisoformat(lobby["paused_at"])
            if lobby["paused_at"] else _now()
        )
        database.execute(
            "DELETE FROM nerd_answers WHERE round_id = ?",
            (nerd_round["id"],),
        )
        database.execute(
            """
            UPDATE nerd_rounds
            SET question_id = ?, question_json = ?, phase = 'question',
                options_json = NULL, resolution_json = NULL,
                phase_started_at = ?, phase_ends_at = ?,
                early_advance_at = NULL, completed_at = NULL
            WHERE id = ?
            """,
            (
                question["id"],
                json.dumps(question, ensure_ascii=False),
                _iso(phase_start),
                _iso(phase_start + timedelta(seconds=PERFECT_ANSWER_SECONDS)),
                nerd_round["id"],
            ),
        )
        database.commit()
        return redirect(url_for("nerd_lobby", lobby_id=lobby_id))

    @app.post("/nerd/<int:lobby_id>/host-pruefung")
    @_login_required
    def nerd_host_review(lobby_id: int):
        _csrf()
        lobby = refresh_nerd_lobby(lobby_id)
        nerd_round = _round(lobby)
        if (
            not lobby
            or lobby["host_user_id"] != g.user["id"]
            or not nerd_round
            or nerd_round["phase"] != "review"
        ):
            abort(403)
        answer_ids = {
            row["id"]
            for row in _db().execute(
                "SELECT id FROM nerd_answers WHERE round_id = ?",
                (nerd_round["id"],),
            ).fetchall()
        }
        for answer_id in answer_ids:
            _db().execute(
                "UPDATE nerd_answers SET host_equivalent = ? WHERE id = ?",
                (
                    int(bool(request.form.get(f"equivalent_{answer_id}"))),
                    answer_id,
                ),
            )
        _resolve_round(_db(), lobby, nerd_round)
        _db().commit()
        return redirect(url_for("nerd_lobby", lobby_id=lobby_id))

    @app.post("/nerd/<int:lobby_id>/weiter")
    @_login_required
    def nerd_continue(lobby_id: int):
        _csrf()
        lobby = refresh_nerd_lobby(lobby_id)
        nerd_round = _round(lobby)
        if (
            not lobby
            or lobby["host_user_id"] != g.user["id"]
            or not nerd_round
            or nerd_round["phase"] != "resolution"
        ):
            abort(403)
        if _goal_reached(_db(), lobby):
            _db().execute(
                "UPDATE nerd_lobbies SET status = 'completed', completed_at = ? WHERE id = ?",
                (_iso(), lobby_id),
            )
        else:
            _start_round(_db(), lobby)
        _db().commit()
        return redirect(url_for("nerd_lobby", lobby_id=lobby_id))

    @app.post("/nerd/<int:lobby_id>/verlassen")
    @_login_required
    def nerd_leave(lobby_id: int):
        _csrf()
        lobby = _lobby(lobby_id)
        member = _member(lobby_id, g.user["id"])
        if not lobby or not member or member["status"] != "active":
            return redirect(url_for("nerd_index"))
        _db().execute(
            "UPDATE nerd_members SET status = 'left', ready = 0 WHERE id = ?",
            (member["id"],),
        )
        _db().commit()
        refresh_nerd_lobby(lobby_id)
        flash("Du hast Stormseed´s Perfect verlassen.", "success")
        return redirect(url_for("nerd_index"))
