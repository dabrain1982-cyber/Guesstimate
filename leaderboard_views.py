"""Account currency peaks and finalized quiz victories; never change balances."""
from collections import defaultdict
from datetime import date, datetime, timedelta


def _players(db):
    return db.execute("""
        SELECT u.id, u.display_name, COALESCE(c.avatar_id, 'a00') AS avatar_id,
               COALESCE(c.plaque_id, 'p00') AS plaque_id
        FROM users u LEFT JOIN user_cosmetics c ON c.user_id = u.id
    """).fetchall()


def _rank(players, values):
    ordered = sorted(players, key=lambda p: (-values.get(p['id'], 0), p['display_name'].casefold()))
    result, previous, rank = [], None, 0
    for index, player in enumerate(ordered, 1):
        value = int(values.get(player['id'], 0))
        if value != previous:
            rank, previous = index, value
        result.append(dict(player, points=value, rounds=0, rank=rank))
    return result


def currency_history(db, bonus=0):
    """Reconstruct certain closing balances at each recorded timestamp.

    Old timestamps only have second precision. Net simultaneous records instead
    of inventing an intrasecond transaction order and an unproven higher peak.
    New exact peaks are captured at the credit/debit boundary as well.
    """
    movements = defaultdict(lambda: defaultdict(int))
    for row in db.execute("""
        SELECT user_id, COALESCE(completed_at, started_at) AS stamp, COALESCE(score, 0) AS delta
        FROM attempts WHERE status = 'completed'
        UNION ALL
        SELECT user_id, purchased_at AS stamp, -price AS delta FROM shop_purchases
    """):
        movements[row['user_id']][row['stamp']] += int(row['delta'])
    current, peaks = {}, {}
    for player in _players(db):
        user_id = player['id']
        balance = int(bonus)
        high = max(0, balance)
        for _, delta in sorted(movements[user_id].items()):
            balance += delta
            high = max(high, balance)
        current[user_id] = max(0, balance)
        peaks[user_id] = max(high, current[user_id])
    return current, peaks


def record_currency_peak(db, user_id, balance):
    db.execute("""
        INSERT INTO currency_peaks(user_id, peak, recorded_at) VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET peak = excluded.peak, recorded_at = excluded.recorded_at
        WHERE excluded.peak > currency_peaks.peak
    """, (user_id, max(0, int(balance)), datetime.now().isoformat(timespec='seconds')))


def init_currency_peaks(db, bonus=0):
    db.execute("""
        CREATE TABLE IF NOT EXISTS currency_peaks (
            user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
            peak INTEGER NOT NULL CHECK (peak >= 0), recorded_at TEXT NOT NULL
        )
    """)
    _, peaks = currency_history(db, bonus)
    with db:
        for user_id, high in peaks.items():
            record_currency_peak(db, user_id, high)


def currency_rankings(db, bonus=0):
    current, peaks = currency_history(db, bonus)
    for row in db.execute('SELECT user_id, peak FROM currency_peaks'):
        peaks[row['user_id']] = max(peaks.get(row['user_id'], 0), int(row['peak']))
    players = _players(db)
    return _rank(players, current), _rank(players, peaks)


def winner_rows(db, period, reference_day):
    """Shared victories count for closed days/weeks, including tied first places."""
    if period not in ('daily', 'weekly'):
        raise ValueError('Unknown victory period')
    today = date.fromisoformat(reference_day)
    cutoff = today if period == 'daily' else today - timedelta(days=today.weekday())
    scores = defaultdict(lambda: defaultdict(int))
    for row in db.execute("""
        SELECT r.round_date, a.user_id, COALESCE(a.score, 0) AS score
        FROM attempts a JOIN daily_rounds r ON r.id = a.round_id
        WHERE a.status = 'completed' AND r.round_date < ?
    """, (cutoff.isoformat(),)):
        day = date.fromisoformat(row['round_date'])
        key = row['round_date'] if period == 'daily' else day.isocalendar()[:2]
        scores[key][row['user_id']] += int(row['score'])
    victories = defaultdict(int)
    for participants in scores.values():
        best = max(participants.values())
        for user_id, score in participants.items():
            if score == best:
                victories[user_id] += 1
    return _rank(_players(db), victories)
