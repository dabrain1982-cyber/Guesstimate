#!/usr/bin/env python3
"""Reset quiz progress while preserving registered users."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path


def reset(database_path: str) -> None:
    database = sqlite3.connect(Path(database_path))
    try:
        database.execute("PRAGMA foreign_keys = ON")
        with database:
            # Usage and pending notifications are permanent history. A game reset
            # must never make an already played question look unused again.
            for table in ("party_answers", "party_members", "party_lobbies"):
                if database.execute(
                    "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (table,)
                ).fetchone():
                    database.execute(f"DELETE FROM {table}")
            database.execute("DELETE FROM answers")
            database.execute("DELETE FROM attempts")
            database.execute("DELETE FROM daily_rounds")
            database.execute(
                "DELETE FROM sqlite_sequence "
                "WHERE name IN ('answers', 'attempts', 'daily_rounds', 'party_answers', 'party_members', 'party_lobbies')"
            )
    finally:
        database.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Aufruf: reset_game.py DATENBANK")
    reset(sys.argv[1])
