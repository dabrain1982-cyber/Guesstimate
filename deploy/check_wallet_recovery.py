"""Exercise the old 1.1 application against a new wallet on disposable data."""
from datetime import date
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
def check():
    import account_wallet
    import production_runtime as runtime
    import app as application
    app=runtime.app
    with app.app_context():
        db=app.get_db()
        uid=db.execute("INSERT INTO users(username,display_name,pin_hash,created_at) VALUES('recovery-fixture','Recovery-Fixture','not-a-login','2026-11-02')").lastrowid
        rid=db.execute("INSERT INTO daily_rounds(round_date,questions_json,created_at) VALUES('2026-10-01','[]','2026-10-01')").lastrowid
        db.execute("INSERT INTO attempts(user_id,round_id,status,score,started_at,completed_at) VALUES(?,?,'completed',1500,'2026-10-01T10:00:00','2026-10-01T10:01:00')",(uid,rid))
        db.execute("INSERT INTO shop_purchases VALUES(?,'avatar','a01',100,'2026-10-02T10:00:00')",(uid,))
        account_wallet.post_entry(db,uid,-500,'recovery-fixture','{}')
        db.commit()
        before=[tuple(row) for row in db.execute('SELECT * FROM currency_entries')]
        assert application.player_currency_balance(uid)==900
        boards=application.leaderboard_sets(date.today().isoformat())
        assert next(p['points'] for p in boards['currency_current'] if p['id']==uid)==900
    client=app.test_client()
    with client.session_transaction() as session:
        session.update(user_id=uid,login_recorded_on=date.today().isoformat(),csrf_token='recovery-fixture')
    assert client.get('/health').get_json()['deployment']=='1.1-wallet-recovery.1'
    page=client.get('/shop')
    assert page.status_code==200 and b'900' in page.data
    assert client.get('/karten/blackjack').status_code==503
    assert client.post('/karten/blackjack/aktion',data={'csrf_token':'recovery-fixture','action':'bet','amount':500}).status_code==503
    with app.app_context():
        db=app.get_db()
        assert [tuple(row) for row in db.execute('SELECT * FROM currency_entries')]==before
        assert application.player_currency_balance(uid)==900
    print(json.dumps({'old_code':'1.1','balance':900,'ranking_balance':900,
        'blackjack_get_post':503,'ledger_preserved':True,'database_restored':False}))

if __name__=='__main__':check()
