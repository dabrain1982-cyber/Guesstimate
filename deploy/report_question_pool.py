#!/usr/bin/env python3
"""Read round counters; optionally retry the explicitly requested pool email.

Default mode opens SQLite read-only. --notify only changes the notification
record, using the application's normal SMTP sender and active service settings.
No player, answer, round, or question-usage records are changed by this tool.
"""

from __future__ import annotations

import argparse
from contextlib import closing
import json
import os
from pathlib import Path
import shlex
import smtplib
import sqlite3
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def read_report(path: Path) -> dict:
    with closing(sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True)) as db:
        db.row_factory = sqlite3.Row
        daily = dict(db.execute("""
            SELECT COUNT(*) AS reserved_day_sets,
                   MIN(round_date) AS first_day, MAX(round_date) AS last_day
            FROM daily_rounds
        """).fetchone())
        daily["player_attempts_by_status"] = {
            row["status"]: row["n"] for row in db.execute(
                "SELECT status, COUNT(*) AS n FROM attempts GROUP BY status"
            )
        }
        daily["days_with_completed_play"] = db.execute(
            "SELECT COUNT(DISTINCT round_id) FROM attempts WHERE status = 'completed'"
        ).fetchone()[0]
        party = dict(db.execute("""
            SELECT COUNT(CASE WHEN questions_json IS NOT NULL THEN 1 END) AS started_lobbies,
                   COUNT(CASE WHEN status = 'completed' THEN 1 END) AS completed_lobbies,
                   COALESCE(SUM(CASE WHEN questions_json IS NOT NULL
                                    THEN json_array_length(questions_json) / 5 ELSE 0 END), 0)
                       AS reserved_five_question_sets,
                   COALESCE(SUM(current_question_index / 5), 0) AS completed_five_question_sets
            FROM party_lobbies
        """).fetchone())
        usage = [dict(row) for row in db.execute("""
            SELECT source_type, category, COUNT(*) AS reserved_questions,
                   MIN(used_at) AS first_reserved_at, MAX(used_at) AS last_reserved_at
            FROM question_usage GROUP BY source_type, category ORDER BY source_type, category
        """)]
        perfect = {}
        for category, directory in (("term", "begriffe"), ("curiosity", "kuriositaeten")):
            bank = json.loads((ROOT / "fragen" / "stormseedsperfekt" / directory / "fragen.json")
                              .read_text(encoding="utf-8"))
            used = {row[0] for row in db.execute(
                "SELECT question_id FROM perfect_question_usage WHERE category = ?", (category,)
            )}
            perfect[category] = {
                "total": len(bank),
                "unused_in_current_cycle": sum(card["id"] not in used for card in bank),
                "rounds": db.execute("SELECT COUNT(*) FROM nerd_rounds WHERE category = ?",
                                     (category,)).fetchone()[0],
                "completed_rounds": db.execute(
                    "SELECT COUNT(*) FROM nerd_rounds WHERE category = ? AND completed_at IS NOT NULL",
                    (category,),
                ).fetchone()[0],
            }
        notification = db.execute(
            "SELECT kind, created_at, sent_at FROM system_notifications WHERE kind = 'question_pool_exhausted'"
        ).fetchone()
        return {"daily": daily, "party_classic": party, "question_reservations": usage,
                "perfect": perfect, "notification_before": dict(notification) if notification else None}


def notify(path: Path, resend: bool) -> int:
    # Obtain configuration from the running service without printing it or secrets.
    environment = subprocess.check_output(
        ["systemctl", "show", "guesstimate.service", "-p", "Environment", "--value"], text=True
    )
    for assignment in shlex.split(environment):
        key, separator, value = assignment.partition("=")
        if separator and key.startswith("QUIZ_"):
            os.environ[key] = value
    # Import application functions without running application initialization on
    # the live DB: startup migrations are outside this diagnostic's scope.
    import tempfile
    with tempfile.TemporaryDirectory(prefix="pool-mail-") as temporary:
        os.environ["QUIZ_DATABASE"] = str(Path(temporary) / "isolated.sqlite3")
        sys.path[:0] = [str(ROOT), str(ROOT / ".deps")]
        from app import app, get_db, question_pool_status, send_pool_exhausted_email
        app.config["DATABASE"] = str(path.resolve())
        with app.app_context():
            pool = question_pool_status()
            print(json.dumps({"current_pool": pool}, ensure_ascii=False))
            if not pool["exhausted"]:
                print("Keine Leerstandsmail: Es sind neue vollständige Runden verfügbar.")
                return 0
            from datetime import datetime
            db = get_db()
            db.execute("""INSERT OR IGNORE INTO system_notifications(kind, created_at)
                          VALUES ('question_pool_exhausted', ?)""",
                       (datetime.now().isoformat(timespec="seconds"),))
            if resend:
                db.execute("UPDATE system_notifications SET sent_at = NULL, created_at = ? "
                           "WHERE kind = 'question_pool_exhausted'",
                           (datetime.now().isoformat(timespec="seconds"),))
            db.commit()
            try:
                sent = send_pool_exhausted_email()
            except (OSError, smtplib.SMTPException) as error:
                print(f"Mailversand fehlgeschlagen ({type(error).__name__}): {error}")
                return 1
            print("SMTP-Versand bestätigt." if sent else "Mail nicht versendet: Konfiguration prüfen.")
            return 0 if sent else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=ROOT / "runtime" / "quiz.sqlite3")
    parser.add_argument("--notify", action="store_true", help="Vorgemerkte Leerstandsmail versenden")
    parser.add_argument("--resend", action="store_true", help="Auch eine frühere Versandmarkierung zurücksetzen")
    args = parser.parse_args()
    if args.resend and not args.notify:
        parser.error("--resend erfordert --notify")
    print(json.dumps(read_report(args.database), ensure_ascii=False, indent=2))
    return notify(args.database, args.resend) if args.notify else 0


if __name__ == "__main__":
    raise SystemExit(main())
