from datetime import date
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from app import AVATAR_CATALOG, create_app, leaderboard_sets, player_currency_balance
from leaderboard_views import currency_rankings, init_currency_peaks, record_currency_peak, winner_rows


class LeaderboardViewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.app = create_app(dict(TESTING=True, SECRET_KEY='rank-test',
            DATABASE=str(Path(self.temp.name)/'test.sqlite3')))
        with self.app.app_context():
            db = self.app.get_db()
            for name in ('Mira','Jan','Kea'):
                db.execute('INSERT INTO users(username,display_name,pin_hash,created_at) VALUES(?,?,?,?)',
                    (name.casefold(),name,'test','2026-01-01'))
            db.commit()

    def tearDown(self):
        self.temp.cleanup()

    def score(self, db, uid, day, score, completed=None, status='completed'):
        db.execute('INSERT OR IGNORE INTO daily_rounds(round_date,questions_json,created_at) VALUES(?,?,?)',(day,'[]',day))
        rid = db.execute('SELECT id FROM daily_rounds WHERE round_date=?',(day,)).fetchone()[0]
        db.execute('INSERT INTO attempts(user_id,round_id,status,score,started_at,completed_at) VALUES(?,?,?,?,?,?)',
            (uid,rid,status,score,day+'T10:00:00',completed or day+'T10:01:00'))

    def test_peak_preserves_earned_then_spent_currency_and_excludes_test_blackjack(self):
        with self.app.app_context():
            db=self.app.get_db()
            self.score(db,1,'2026-10-01',1000)
            db.execute("INSERT INTO shop_purchases VALUES(1,'avatar','a01',800,'2026-10-02T10:00:00')")
            self.score(db,1,'2026-10-03',100)
            self.score(db,2,'2026-10-03',500)
            db.execute('INSERT OR REPLACE INTO blackjack_balances(user_id,balance) VALUES(1,999999)')
            db.commit()
            current,high=currency_rankings(db)
            self.assertEqual([(p['id'],p['points']) for p in current],[(2,500),(1,300),(3,0)])
            self.assertEqual([(p['id'],p['points']) for p in high],[(1,1000),(2,500),(3,0)])
            self.assertEqual(player_currency_balance(1),300)

    def test_exact_recorded_peak_survives_same_second_transactions_and_restart_backfill(self):
        with self.app.app_context():
            db=self.app.get_db()
            self.score(db,1,'2026-10-01',1000)
            record_currency_peak(db,1,1000)
            db.execute("INSERT INTO shop_purchases VALUES(1,'avatar','a01',800,'2026-10-01T10:01:00')")
            db.commit()
            init_currency_peaks(db)
            current,high=currency_rankings(db)
            self.assertEqual(next(p['points'] for p in current if p['id']==1),200)
            self.assertEqual(next(p['points'] for p in high if p['id']==1),1000)

    def test_unordered_old_same_second_history_does_not_invent_a_peak(self):
        with self.app.app_context():
            db=self.app.get_db()
            self.score(db,1,'2026-10-01',1000)
            db.execute("INSERT INTO shop_purchases VALUES(1,'avatar','a01',800,'2026-10-01T10:01:00')")
            db.commit()
            self.assertEqual(next(p['points'] for p in currency_rankings(db)[1] if p['id']==1),200)

    def test_victories_count_ties_but_only_closed_days_and_weeks(self):
        with self.app.app_context():
            db=self.app.get_db()
            self.score(db,1,'2026-10-19',100)
            self.score(db,2,'2026-10-19',100)
            self.score(db,1,'2026-10-20',100)
            self.score(db,2,'2026-10-20',200)
            self.score(db,3,'2026-10-21',999,status='playing')
            self.score(db,3,'2026-11-01',999)
            db.commit()
            daily=winner_rows(db,'daily','2026-11-01')
            weekly=winner_rows(db,'weekly','2026-11-01')
            self.assertEqual({p['id']:p['points'] for p in daily},{1:1,2:2,3:0})
            self.assertEqual({p['id']:p['points'] for p in weekly},{1:0,2:1,3:0})

    def test_year_boundary_and_equal_currency_receive_shared_ranks(self):
        with self.app.app_context():
            db=self.app.get_db()
            self.score(db,1,'2025-12-29',100)
            self.score(db,2,'2026-01-01',100)
            db.commit()
            winners=winner_rows(db,'weekly','2026-01-05')
            self.assertEqual([(p['points'],p['rank']) for p in winners[:2]],[(1,1),(1,1)])
            self.assertEqual(currency_rankings(db)[0][-1]['rank'],3)

    def test_reading_all_six_views_does_not_write_history(self):
        with self.app.app_context():
            db=self.app.get_db()
            before=list(db.iterdump())
            result=leaderboard_sets('2026-11-01')
            self.assertTrue({'daily','weekly','currency_current','currency_high','daily_wins','weekly_wins'} <= result.keys())
            self.assertEqual(before,list(db.iterdump()))

    def test_real_shop_purchase_records_balance_before_debit(self):
        item=AVATAR_CATALOG[0]
        with self.app.app_context():
            db=self.app.get_db()
            self.score(db,1,'2026-10-01',item['price']+100)
            db.commit()
        client=self.app.test_client()
        with client.session_transaction() as session:
            session.update(user_id=1,csrf_token='rank-token',login_recorded_on=date.today().isoformat())
        response=client.post('/shop/kaufen/avatar/'+item['id'],data={'csrf_token':'rank-token'})
        self.assertEqual(response.status_code,302)
        with self.app.app_context():
            self.assertEqual(player_currency_balance(1),100)
            self.assertEqual(self.app.get_db().execute('SELECT peak FROM currency_peaks WHERE user_id=1').fetchone()[0],item['price']+100)

    def test_hall_of_fame_stays_current_while_viewing_an_old_catchup_round(self):
        with self.app.app_context(), patch('app.today_iso',return_value='2026-11-01'):
            db=self.app.get_db()
            self.score(db,1,'2026-10-19',100)
            self.score(db,1,'2026-10-25',100)
            db.commit()
            boards=leaderboard_sets('2026-10-19')
            self.assertEqual(next(p['points'] for p in boards['daily_wins'] if p['id']==1),2)
            self.assertEqual(next(p['points'] for p in boards['weekly_wins'] if p['id']==1),1)
            self.assertEqual(next(p['points'] for p in boards['daily'] if p['id']==1),100)


if __name__=='__main__': unittest.main()
