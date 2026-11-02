"""Run the normal game on this PC with its own persistent, local-only data."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import secrets
import sys


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Guesstimate auf diesem PC starten")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("Der Port muss zwischen 1024 und 65535 liegen.")

    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / ".deps"))
    try:
        from waitress import serve
        import flask  # noqa: F401
    except ImportError:
        parser.exit(
            1,
            "Abhaengigkeiten fehlen. Im Projektordner ausfuehren:\n"
            "python -m pip install --target .deps -r requirements-local.txt\n",
        )

    data = ROOT / "runtime" / "pc-local"
    data.mkdir(parents=True, exist_ok=True)
    secret_file = data / "session.secret"
    try:
        with secret_file.open("x", encoding="utf-8") as handle:
            handle.write(secrets.token_hex(32))
    except FileExistsError:
        pass
    if not secret_file.read_text(encoding="utf-8").strip():
        parser.exit(1, "Der lokale Sitzungsschluessel ist leer. Start abgebrochen.\n")

    # Configure before importing app: its module creates an application at import.
    # This also prevents inherited server settings from opening another database.
    os.environ.update(
        QUIZ_DATABASE=str(data / "quiz.sqlite3"),
        QUIZ_SECRET_KEY_FILE=str(secret_file),
        QUIZ_URL_PREFIX="/",
        QUIZ_PUBLIC_URL=f"http://127.0.0.1:{args.port}",
        QUIZ_MAIL_USER="",
        QUIZ_MAIL_TO="",
        QUIZ_MAIL_PASSWORD_FILE="",
        QUIZ_PREVIEW_CURRENCY_BONUS="0",
        QUIZ_ENABLE_CARD_TABLE="1",
        QUIZ_LOCAL_DEVELOPMENT="1",
        QUIZ_OFFLINE_VERSION=os.environ.get('QUIZ_OFFLINE_VERSION', '1.1'),
    )
    from app import app
    from workshop_buttons import register_workshop_buttons
    register_workshop_buttons(app)

    app.config.update(DEBUG=False, TESTING=False, BLACKJACK_FIXED_STAKE=500,
                      BLACKJACK_TEST_START_BALANCE=10000, BLACKJACK_DEALER_PEEK=False)
    from blackjack_clock import start_blackjack_clock
    start_blackjack_clock(app)
    print(f"Guesstimate: http://127.0.0.1:{args.port}/", flush=True)
    print(f"Eigene PC-Spielstaende: {data / 'quiz.sqlite3'}", flush=True)
    print("Nur auf diesem PC erreichbar. Beenden mit Strg+C.", flush=True)
    serve(app, host="127.0.0.1", port=args.port, threads=4)


if __name__ == "__main__":
    main()
