#!/usr/bin/env python3
"""Merge one accidental duplicate player into another, preserving dated rounds."""

from __future__ import annotations

import getpass
import os
import sqlite3
import sys
from pathlib import Path

from werkzeug.security import generate_password_hash


def find_user(database: sqlite3.Connection, name: str) -> sqlite3.Row:
    normalized = " ".join(name.strip().casefold().split())
    rows = database.execute(
        """
        SELECT * FROM users
        WHERE username = ? OR lower(display_name) = ?
        """,
        (normalized, normalized),
    ).fetchall()
    if len(rows) != 1:
        raise RuntimeError(f"Spieler {name!r} wurde nicht eindeutig gefunden.")
    return rows[0]


def inspect_merge(database_path: str, target_name: str, source_name: str) -> dict:
    """Verify both accounts and prove that their played dates do not overlap."""

    database = sqlite3.connect(Path(database_path))
    database.row_factory = sqlite3.Row
    try:
        target = find_user(database, target_name)
        source = find_user(database, source_name)
        if target["id"] == source["id"]:
            raise RuntimeError("Quelle und Ziel sind derselbe Spieler.")
        overlaps = database.execute(
            """
            SELECT r.round_date
            FROM attempts source_attempt
            JOIN attempts target_attempt
              ON target_attempt.round_id = source_attempt.round_id
             AND target_attempt.user_id = ?
            JOIN daily_rounds r ON r.id = source_attempt.round_id
            WHERE source_attempt.user_id = ?
            ORDER BY r.round_date
            """,
            (target["id"], source["id"]),
        ).fetchall()
        if overlaps:
            dates = ", ".join(row["round_date"] for row in overlaps)
            raise RuntimeError(
                f"Beide Konten besitzen Runden für: {dates}. Abbruch ohne Änderung."
            )
        target_points = database.execute(
            "SELECT COALESCE(SUM(score), 0) FROM attempts WHERE user_id = ? AND status = 'completed'",
            (target["id"],),
        ).fetchone()[0]
        source_points = database.execute(
            "SELECT COALESCE(SUM(score), 0) FROM attempts WHERE user_id = ? AND status = 'completed'",
            (source["id"],),
        ).fetchone()[0]
        return {
            "target": target["display_name"],
            "source": source["display_name"],
            "target_points": int(target_points),
            "source_points": int(source_points),
        }
    finally:
        database.close()


def merge(database_path: str, target_name: str, source_name: str, new_pin: str) -> dict:
    if len(new_pin) < 4:
        raise RuntimeError("Die neue PIN muss mindestens vier Zeichen lang sein.")
    database = sqlite3.connect(Path(database_path))
    database.row_factory = sqlite3.Row
    database.execute("PRAGMA foreign_keys = ON")
    try:
        database.execute("BEGIN IMMEDIATE")
        target = find_user(database, target_name)
        source = find_user(database, source_name)
        if target["id"] == source["id"]:
            raise RuntimeError("Quelle und Ziel sind derselbe Spieler.")

        overlaps = database.execute(
            """
            SELECT r.round_date
            FROM attempts source_attempt
            JOIN attempts target_attempt
              ON target_attempt.round_id = source_attempt.round_id
             AND target_attempt.user_id = ?
            JOIN daily_rounds r ON r.id = source_attempt.round_id
            WHERE source_attempt.user_id = ?
            """,
            (target["id"], source["id"]),
        ).fetchall()
        if overlaps:
            dates = ", ".join(row["round_date"] for row in overlaps)
            raise RuntimeError(f"Beide Konten besitzen Runden für: {dates}. Abbruch ohne Änderung.")

        target_before = database.execute(
            "SELECT COALESCE(SUM(score), 0) FROM attempts WHERE user_id = ? AND status = 'completed'",
            (target["id"],),
        ).fetchone()[0]
        source_points = database.execute(
            "SELECT COALESCE(SUM(score), 0) FROM attempts WHERE user_id = ? AND status = 'completed'",
            (source["id"],),
        ).fetchone()[0]

        database.execute(
            "UPDATE attempts SET user_id = ? WHERE user_id = ?",
            (target["id"], source["id"]),
        )
        database.execute(
            """
            INSERT OR IGNORE INTO login_days (user_id, login_date, created_at)
            SELECT ?, login_date, created_at FROM login_days WHERE user_id = ?
            """,
            (target["id"], source["id"]),
        )
        database.execute("DELETE FROM login_days WHERE user_id = ?", (source["id"],))
        database.execute("DELETE FROM vacation_uses WHERE user_id = ?", (source["id"],))
        database.execute(
            "UPDATE users SET pin_hash = ? WHERE id = ?",
            (generate_password_hash(new_pin), target["id"]),
        )
        database.execute("DELETE FROM users WHERE id = ?", (source["id"],))

        target_after = database.execute(
            "SELECT COALESCE(SUM(score), 0) FROM attempts WHERE user_id = ? AND status = 'completed'",
            (target["id"],),
        ).fetchone()[0]
        expected = int(target_before) + int(source_points)
        if int(target_after) != expected:
            raise RuntimeError("Punkteprüfung fehlgeschlagen; Abbruch ohne Änderung.")
        database.commit()
        return {
            "target": target["display_name"],
            "source": source["display_name"],
            "transferred_points": int(source_points),
            "total_points": int(target_after),
        }
    except Exception:
        database.rollback()
        raise
    finally:
        database.close()


if __name__ == "__main__":
    if len(sys.argv) == 5 and sys.argv[1] == "--check":
        plan = inspect_merge(sys.argv[2], sys.argv[3], sys.argv[4])
        print(
            f"Geprüft: {plan['source']} ({plan['source_points']} Punkte) kann in "
            f"{plan['target']} ({plan['target_points']} Punkte) übernommen werden."
        )
        raise SystemExit(0)
    if len(sys.argv) != 4:
        raise SystemExit(
            "Aufruf: merge_player.py [--check] DATENBANK ZIEL QUELLE"
        )
    pin = os.environ.get("MERGE_NEW_PIN", "")
    if not pin:
        pin = getpass.getpass("Neue PIN für das Zielkonto: ")
        confirmation = getpass.getpass("Neue PIN wiederholen: ")
        if pin != confirmation:
            raise SystemExit("Die PINs stimmen nicht überein.")
    result = merge(sys.argv[1], sys.argv[2], sys.argv[3], pin)
    print(
        f"{result['source']} wurde in {result['target']} zusammengeführt: "
        f"+{result['transferred_points']} Punkte, neu {result['total_points']} Punkte."
    )
