#!/usr/bin/env python3
"""Read-only audit of finalized trophy results for one player."""

from __future__ import annotations

import sqlite3
import sys
from datetime import date
from pathlib import Path


def daily_wins(database_path: str, player_name: str) -> tuple[str, list[sqlite3.Row]]:
    path = Path(database_path).resolve()
    database = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    database.row_factory = sqlite3.Row
    try:
        normalized = " ".join(player_name.strip().casefold().split())
        players = database.execute(
            """
            SELECT id, display_name
            FROM users
            WHERE username = ? OR lower(display_name) = ?
            """,
            (normalized, normalized),
        ).fetchall()
        if len(players) != 1:
            raise RuntimeError(
                f"Spieler {player_name!r} wurde nicht eindeutig gefunden."
            )
        player = players[0]
        wins = database.execute(
            """
            WITH finalized AS (
                SELECT r.round_date, a.user_id, a.score,
                       DENSE_RANK() OVER (
                           PARTITION BY r.round_date ORDER BY a.score DESC
                       ) AS place
                FROM attempts a
                JOIN daily_rounds r ON r.id = a.round_id
                WHERE a.status = 'completed' AND r.round_date < ?
            )
            SELECT round_date, score
            FROM finalized
            WHERE user_id = ? AND place = 1
            ORDER BY round_date
            """,
            (date.today().isoformat(), player["id"]),
        ).fetchall()
        return str(player["display_name"]), wins
    finally:
        database.close()


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit(
            "Aufruf: audit_player_trophies.py DATENBANK SPIELERNAME"
        )
    display_name, wins = daily_wins(sys.argv[1], sys.argv[2])
    print(f"Tagessiege für {display_name}: {len(wins)}")
    for win in wins:
        print(f"- {win['round_date']}: {int(win['score'])} Punkte")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
