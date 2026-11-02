"""Resume the saved local Conquest preview; never seed a replacement game."""
from __future__ import annotations

import argparse
from datetime import date
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "runtime/conquest-hud-20261025"


def saved_cases(data=DATA):
    if not all((data / name).is_file() for name in ("walkthrough.sqlite3", "preview-cases.json")):
        raise RuntimeError("Die gespeicherte Conquest-Vorschau fehlt. Es wurde keine neue Partie angelegt.")
    cases = json.loads((data / "preview-cases.json").read_text(encoding="utf-8"))
    if not cases.get("four", {}).get("users"):
        raise RuntimeError("Die gespeicherte Spielerzuordnung der Conquest-Vorschau fehlt.")
    return cases


def current_room(db, user_id):
    # Follow the host's latest actual lobby, including a rematch/waiting lobby.
    # Do not choose a different fixture merely because its file was modified.
    row = db.execute("""SELECT cl.id, cl.status FROM conquest_lobbies cl
        JOIN conquest_members cm ON cm.lobby_id=cl.id
        WHERE cm.user_id=? AND cm.status='active'
          AND cl.status IN ('waiting','playing','completed')
        ORDER BY cl.id DESC LIMIT 1""", (user_id,)).fetchone()
    if not row:
        return "/karten/welteroberung"
    return f"/karten/welteroberung/{row[0]}" + ("/lobby" if row[1] == "waiting" else "")


def register_entries(app, cases):
    from flask import redirect, session

    def sign_in(user_id):
        # This is the existing local test identity, with its separate cookie.
        session.clear()
        session.update(user_id=user_id, csrf_token="portrait-test", login_recorded_on=date.today().isoformat())

    @app.get("/local/current")
    def current_preview():
        user_id = cases["four"]["users"][0]
        sign_in(user_id)
        return redirect(current_room(app.get_db(), user_id))

    # Keep the already-running local opponent helper compatible. This does not
    # start any simulator or issue a game action from the double-click launcher.
    @app.get("/test/<case>/<int:seat>")
    def preview_player(case, seat):
        from flask import abort
        if case not in cases or seat >= len(cases[case]["users"]):
            abort(404)
        sign_in(cases[case]["users"][seat])
        return redirect(cases[case]["room"])


def main():
    parser = argparse.ArgumentParser(description="Gespeicherte aktuelle Conquest-Vorschau fortsetzen")
    parser.add_argument("--port", type=int, default=8767)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("Der Port muss zwischen 1024 und 65535 liegen.")
    try:
        cases = saved_cases()
    except (OSError, ValueError, RuntimeError) as error:
        parser.exit(1, str(error) + "\n")
    sys.path[:0] = [str(ROOT / ".deps"), str(ROOT)]
    os.environ.update(
        QUIZ_DATABASE=str(DATA / "walkthrough.sqlite3"), QUIZ_URL_PREFIX="/",
        QUIZ_PUBLIC_URL=f"http://127.0.0.1:{args.port}",
        QUIZ_MAIL_USER="", QUIZ_MAIL_TO="", QUIZ_MAIL_PASSWORD_FILE="",
        QUIZ_ENABLE_CARD_TABLE="1", QUIZ_LOCAL_DEVELOPMENT="1",
    )
    from app import app
    from waitress import serve
    # Same identity and session signing as the existing saved preview.
    app.config.update(SESSION_COOKIE_NAME="conquest_hud_test", SECRET_KEY="disposable-local-test")
    register_entries(app, cases)
    print(f"Gespeicherte Conquest-Vorschau: http://127.0.0.1:{args.port}/local/current", flush=True)
    serve(app, host="127.0.0.1", port=args.port, threads=4)


if __name__ == "__main__":
    main()
