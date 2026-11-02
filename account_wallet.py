"""Shared iKühe balance: existing quiz/shop history plus immutable game entries."""
from datetime import datetime

class WalletError(ValueError):
    pass

def init_wallet(db):
    db.execute("""
        CREATE TABLE IF NOT EXISTS currency_entries (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            amount INTEGER NOT NULL CHECK(amount != 0),
            source TEXT NOT NULL,
            reference TEXT NOT NULL UNIQUE,
            detail_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    db.execute('CREATE INDEX IF NOT EXISTS currency_entries_user ON currency_entries(user_id, id)')

def balances(db, bonus=0):
    rows = db.execute("""
        SELECT u.id,
            COALESCE(q.earned,0) - COALESCE(s.spent,0) + COALESCE(e.delta,0) AS amount
        FROM users u
        LEFT JOIN (SELECT user_id,SUM(score) AS earned FROM attempts
                   WHERE status='completed' GROUP BY user_id) q ON q.user_id=u.id
        LEFT JOIN (SELECT user_id,SUM(price) AS spent FROM shop_purchases
                   GROUP BY user_id) s ON s.user_id=u.id
        LEFT JOIN (SELECT user_id,SUM(amount) AS delta FROM currency_entries
                   GROUP BY user_id) e ON e.user_id=u.id
    """)
    return {row['id']: max(0,int(row['amount'])+int(bonus)) for row in rows}

def balance(db, user_id, bonus=0):
    return balances(db, bonus).get(int(user_id), 0)

def movements(db):
    return db.execute("""
        SELECT user_id, COALESCE(completed_at, started_at) AS stamp, COALESCE(score,0) AS delta
        FROM attempts WHERE status='completed'
        UNION ALL
        SELECT user_id, purchased_at AS stamp, -price AS delta FROM shop_purchases
        UNION ALL
        SELECT user_id, created_at AS stamp, amount AS delta FROM currency_entries
    """)

def record_peak(db, user_id, amount):
    db.execute("""
        INSERT INTO currency_peaks(user_id,peak,recorded_at) VALUES(?,?,?)
        ON CONFLICT(user_id) DO UPDATE SET peak=excluded.peak,recorded_at=excluded.recorded_at
        WHERE excluded.peak > currency_peaks.peak
    """,(user_id,max(0,int(amount)),datetime.now().isoformat(timespec='seconds')))

def post_entry(db, user_id, amount, reference, detail_json, *, bonus=0):
    if not db.in_transaction:
        raise WalletError('Eine Kontobuchung benötigt eine gesperrte Transaktion.')
    if type(amount) is not int or not amount:
        raise WalletError('Ungültige Kontobuchung.')
    existing = db.execute('SELECT * FROM currency_entries WHERE reference=?',(reference,)).fetchone()
    if existing:
        if (existing['user_id'],existing['amount'],existing['source'],existing['detail_json']) != (int(user_id),amount,'blackjack',detail_json):
            raise WalletError('Widersprüchliche Wiederholung einer Kontobuchung.')
        return
    before = balance(db,user_id,bonus)
    if before+amount < 0:
        raise WalletError('Dafür reicht dein iKühe-Kontostand nicht.')
    record_peak(db,user_id,before)
    db.execute("""INSERT INTO currency_entries(user_id,amount,source,reference,detail_json,created_at)
                  VALUES(?,?,'blackjack',?,?,?)""",
               (int(user_id),amount,reference,detail_json,datetime.now().isoformat(timespec='microseconds')))
    record_peak(db,user_id,balance(db,user_id,bonus))
