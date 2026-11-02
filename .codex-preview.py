from datetime import date, datetime, timedelta
import json
from pathlib import Path

from flask import redirect, render_template, send_from_directory, session
from werkzeug.security import generate_password_hash

from app import DEFAULT_PLAQUE, PLAQUE_CATALOG, create_app, get_or_create_round, today_iso
from card_table import _build_deck
from conquest import _prepare_automatic_state


PREVIEW_DATABASE = Path(__file__).resolve().parent / "runtime" / "codex-preview.sqlite3"
PREVIEW_DATABASE.parent.mkdir(parents=True, exist_ok=True)
preview_app = create_app(
    {
        "DATABASE": str(PREVIEW_DATABASE),
        "SECRET_KEY": "quiz-arena-preview",
        "PREVIEW_CURRENCY_BONUS": 0,
        "CARD_TABLE_ENABLED": True,
    }
)

with preview_app.app_context():
    database = preview_app.get_db()
    players = [
        ("stormseed", "Stormseed", 450, "a10", "p03"),
        ("pearlyde", "Pearlyde", 424, "a00", "p00"),
        ("sehr-langer-name", "Professorin Unfassbarlanger Quizzington", 393, "a12", "p11"),
        ("jule", "Jule", 487, "a09", "p10"),
        ("theo", "Theo", 364, "a10", "p13"),
        ("mira", "Mira", 313, "a00", "p00"),
    ]
    round_row = get_or_create_round(today_iso())
    for username, display_name, score, avatar_id, plaque_id in players:
        row = database.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        if row:
            user_id = row["id"]
        else:
            user_id = database.execute(
                "INSERT INTO users (username, display_name, pin_hash, created_at) VALUES (?, ?, ?, ?)",
                (username, display_name, generate_password_hash("preview"), datetime.now().isoformat()),
            ).lastrowid
        database.execute(
            """
            INSERT INTO attempts
                (user_id, round_id, status, current_index, multiplier, score, started_at, completed_at)
            VALUES (?, ?, 'completed', 5, 1, ?, ?, ?)
            ON CONFLICT(user_id, round_id) DO UPDATE SET score = excluded.score, status = 'completed'
            """,
            (user_id, round_row["id"], score, datetime.now().isoformat(), datetime.now().isoformat()),
        )
        database.execute(
            """
            INSERT INTO user_cosmetics (user_id, avatar_id, plaque_id, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET avatar_id=excluded.avatar_id, plaque_id=excluded.plaque_id
            """,
            (user_id, avatar_id, plaque_id, datetime.now().isoformat()),
        )
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    database.execute(
        "INSERT OR IGNORE INTO daily_rounds (round_date, questions_json, created_at) VALUES (?, '[]', ?)",
        (yesterday, datetime.now().isoformat()),
    )
    yesterday_round_id = database.execute(
        "SELECT id FROM daily_rounds WHERE round_date = ?", (yesterday,)
    ).fetchone()[0]
    jule_id = database.execute("SELECT id FROM users WHERE username='jule'").fetchone()[0]
    database.execute(
        """
        INSERT INTO attempts
            (user_id, round_id, status, current_index, multiplier, score, started_at, completed_at)
        VALUES (?, ?, 'completed', 5, 1, 500, ?, ?)
        ON CONFLICT(user_id, round_id) DO UPDATE SET score=500, status='completed'
        """,
        (jule_id, yesterday_round_id, datetime.now().isoformat(), datetime.now().isoformat()),
    )
    database.commit()


def ensure_card_table_preview():
    database = preview_app.get_db()
    lobby = database.execute(
        "SELECT id FROM card_table_lobbies WHERE name = 'Lokale Kartentisch-Vorschau'"
    ).fetchone()
    if lobby:
        lobby_id = lobby["id"]
        database.execute("DELETE FROM card_table_members WHERE lobby_id = ?", (lobby_id,))
        database.execute("DELETE FROM card_table_lobbies WHERE id = ?", (lobby_id,))
    host_id = database.execute("SELECT id FROM users WHERE username='stormseed'").fetchone()[0]
    now = datetime.now().isoformat(timespec="microseconds")
    state = {"cards": _build_deck(52)}
    lobby_id = database.execute(
        """
        INSERT INTO card_table_lobbies
            (name, host_user_id, status, deck_size, state_json, created_at, started_at)
        VALUES ('Lokale Kartentisch-Vorschau', ?, 'playing', 52, ?, ?, ?)
        """,
        (host_id, json.dumps(state, ensure_ascii=False), now, now),
    ).lastrowid
    preview_names = ("stormseed", "pearlyde", "jule", "theo")
    for offset, username in enumerate(preview_names):
        user_id = database.execute(
            "SELECT id FROM users WHERE username = ?", (username,)
        ).fetchone()[0]
        database.execute(
            """
            INSERT INTO card_table_members (lobby_id, user_id, joined_at, last_seen_at)
            VALUES (?, ?, ?, ?)
            """,
            (lobby_id, user_id, f"{now}-{offset}", now),
        )
    database.commit()
    return lobby_id


def ensure_conquest_preview():
    database = preview_app.get_db()
    existing = database.execute(
        "SELECT id FROM conquest_lobbies WHERE name = 'Lokale Conquest-Vorschau'"
    ).fetchone()
    if existing:
        database.execute("DELETE FROM conquest_members WHERE lobby_id = ?", (existing["id"],))
        database.execute("DELETE FROM conquest_lobbies WHERE id = ?", (existing["id"],))
    host_id = database.execute("SELECT id FROM users WHERE username='stormseed'").fetchone()[0]
    guest_id = database.execute("SELECT id FROM users WHERE username='pearlyde'").fetchone()[0]
    now = datetime.now().isoformat(timespec="microseconds")
    lobby_id = database.execute(
        """
        INSERT INTO conquest_lobbies
            (name, host_user_id, status, board_style, card_style, figure_style,
             dice_style, victory_mode, setup_mode, created_at, started_at)
        VALUES ('Lokale Conquest-Vorschau', ?, 'playing', 'klassisch', 'klassisch',
                'klassisch', 'klassisch', 'missions', 'automatic', ?, ?)
        """,
        (host_id, now, now),
    ).lastrowid
    for offset, user_id in enumerate((host_id, guest_id)):
        database.execute(
            "INSERT INTO conquest_members (lobby_id, user_id, joined_at) VALUES (?, ?, ?)",
            (lobby_id, user_id, f"{now}-{offset}"),
        )
    members = database.execute(
        """
        SELECT cm.*, u.display_name
        FROM conquest_members cm JOIN users u ON u.id = cm.user_id
        WHERE cm.lobby_id = ? ORDER BY cm.joined_at, cm.id
        """,
        (lobby_id,),
    ).fetchall()
    state = _prepare_automatic_state(members, "missions")
    database.execute(
        "UPDATE conquest_lobbies SET state_json = ? WHERE id = ?",
        (json.dumps(state, ensure_ascii=False, separators=(",", ":")), lobby_id),
    )
    database.commit()
    return lobby_id


@preview_app.get("/preview/anmelden/stormseed")
def preview_login():
    database = preview_app.get_db()
    user_id = database.execute("SELECT id FROM users WHERE username='stormseed'").fetchone()[0]
    session.clear()
    session["user_id"] = user_id
    session["csrf_token"] = "preview-token"
    session["show_yesterday_winner"] = True
    return redirect("/")


@preview_app.get("/preview/spielregeln-leiste")
def preview_rules_navigation():
    """Real application with only the isolated rules-navigation proposal."""
    database = preview_app.get_db()
    user_id = database.execute("SELECT id FROM users WHERE username='stormseed'").fetchone()[0]
    session.clear()
    session["user_id"] = user_id
    session["csrf_token"] = "preview-token"
    session["rules_navigation_preview"] = True
    session["show_yesterday_winner"] = False
    return redirect("/")


@preview_app.get("/preview/spielregeln-assets/<path:filename>")
def preview_rules_navigation_assets(filename):
    preview_root = Path(__file__).resolve().parent / "offline-preview" / "rules-nav-v1"
    return send_from_directory(preview_root, filename)


@preview_app.after_request
def inject_rules_navigation_preview(response):
    if not session.get("rules_navigation_preview") or not response.content_type.startswith("text/html"):
        return response
    html = response.get_data(as_text=True)
    html = html.replace(
        "</head>",
        '<link rel="stylesheet" href="/preview/spielregeln-assets/preview.css?v=7">\n</head>',
    )
    html = html.replace(
        "</body>",
        '<script src="/preview/spielregeln-assets/preview.js?v=7" defer></script>\n</body>',
    )
    response.set_data(html)
    response.headers.pop("Content-Length", None)
    return response


@preview_app.get("/preview/kartentisch")
def preview_card_table():
    database = preview_app.get_db()
    user_id = database.execute("SELECT id FROM users WHERE username='stormseed'").fetchone()[0]
    session.clear()
    session["user_id"] = user_id
    session["csrf_token"] = "preview-token"
    return redirect(f"/karten/{ensure_card_table_preview()}")


@preview_app.get("/preview/conquest")
def preview_conquest():
    database = preview_app.get_db()
    user_id = database.execute("SELECT id FROM users WHERE username='stormseed'").fetchone()[0]
    session.clear()
    session["user_id"] = user_id
    session["csrf_token"] = "preview-token"
    return redirect(f"/karten/welteroberung/{ensure_conquest_preview()}")


@preview_app.get("/preview/conquest/brett")
def preview_conquest_board_surface():
    return render_template("conquest_board_preview.html")


@preview_app.get("/preview/nerdiger-modus")
def preview_nerd_mode():
    """Standalone, database-free interaction prototype; never mounted in production."""
    question_files = {
        "truth": "wahroderunwahr/fragen.json",
        "estimate": "schaetzung/fragen.json",
        "binary": "zweigruppenzuordnen/fragen.json",
    }
    question_root = Path(__file__).resolve().parent / "fragen"
    nerd_bank = {
        key: json.loads((question_root / relative_path).read_text(encoding="utf-8"))
        for key, relative_path in question_files.items()
    }
    nerd_skins = [DEFAULT_PLAQUE, *PLAQUE_CATALOG]
    return render_template("nerd_preview.html", nerd_bank=nerd_bank, nerd_skins=nerd_skins)


if __name__ == "__main__":
    preview_app.run(host="127.0.0.1", port=54506, debug=False)
