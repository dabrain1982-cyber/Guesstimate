from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import json
from pathlib import Path
import tempfile
from threading import Barrier
import unittest
from unittest.mock import patch

from app import create_app, player_currency_balance, PHRASE_CATALOG
from blackjack import take_seat
from blackjack_clock import tick_clock
import blackjack_game as game
import blackjack_store as store
import account_wallet
from leaderboard_views import currency_rankings

class BlackjackAccountWalletTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.app = create_app(dict(TESTING=True,SECRET_KEY='disposable-wallet-test',
            DATABASE=str(Path(self.directory.name)/'wallet.sqlite3'),CARD_TABLE_ENABLED=True,
            BLACKJACK_CURRENCY=store.ACCOUNT_CURRENCY,BLACKJACK_FIXED_STAKE=500,
            BLACKJACK_DEALER_PEEK=False,PREVIEW_CURRENCY_BONUS=5000))
        self.ids=[]
        with self.app.app_context():
            db=self.app.get_db()
            for name in ['Wallet-Test','Other-Test']:
                self.ids.append(db.execute("INSERT INTO users(username,display_name,pin_hash,created_at) VALUES(?,?,?,?)",
                    (name.lower(),name,'unused-test-hash',datetime.now().isoformat())).lastrowid)
            db.commit()
        self.clients=[self.client(uid) for uid in self.ids]
        tick_clock(self.app)

    def client(self,uid):
        client=self.app.test_client()
        with client.session_transaction() as session:
            session.update(user_id=uid,csrf_token='wallet-csrf',login_recorded_on=datetime.now().date().isoformat())
        return client

    def status(self,index=0):
        return self.clients[index].get('/karten/blackjack/status').get_json()

    def join(self,index=0,seat='2',accept=True):
        return self.clients[index].post('/karten/blackjack/platz',
            data=dict(csrf_token='wallet-csrf',seat=seat,accept_risk='1' if accept else ''))

    def leave(self,index=0):
        return self.clients[index].post('/karten/blackjack/verlassen',data=dict(csrf_token='wallet-csrf'))

    def act(self,command,index=0,revision=None):
        if revision is None:revision=self.status(index)['revision']
        return self.clients[index].post('/karten/blackjack/aktion',
            data=dict(csrf_token='wallet-csrf',revision=revision,action=command,amount='500' if command=='bet' else ''))

    def rig(self,opening,*,automatic=None):
        with self.app.app_context():
            db=self.app.get_db()
            with db:
                db.execute('BEGIN IMMEDIATE')
                state,balances,_=store.load(db)
                shoe=[r+s for _ in range(6) for s in game.SUITS for r in game.RANKS]
                for card in opening:shoe.remove(card)
                state['shoe']=shoe+list(reversed(opening))
                if automatic is not None:state['clock']['automatic']=automatic
                store.save(db,state,balances,command='fixture')

    def money(self):
        with self.app.app_context():
            db=self.app.get_db()
            current,high=currency_rankings(db,self.app.config['PREVIEW_CURRENCY_BONUS'])
            return dict(balance=player_currency_balance(self.ids[0]),
                current=next(p['points'] for p in current if p['id']==self.ids[0]),
                peak=next(p['points'] for p in high if p['id']==self.ids[0]),
                entries=[row['amount'] for row in db.execute('SELECT * FROM currency_entries WHERE user_id=? ORDER BY id',(self.ids[0],))])

    def begin(self,opening):
        self.assertEqual(self.join().status_code,200)
        self.rig(opening)
        response=self.act('bet')
        self.assertEqual(response.status_code,200,response.get_json())
        return response.get_json()

    def test_seating_requires_warning_each_time_without_charging(self):
        self.assertEqual(self.join(accept=False).status_code,409)
        self.assertIsNone(self.status()['viewer_seat'])
        self.assertEqual(self.money()['entries'],[])
        self.assertEqual(self.join().status_code,200)
        self.assertEqual(self.status()['game']['bankroll'],5000)
        self.leave()
        self.assertEqual(self.join(accept=False).status_code,409)
        self.assertIsNone(self.status()['viewer_seat'])
        self.assertEqual(self.money()['balance'],5000)

    def test_test_balance_is_not_granted_or_imported_and_refill_is_rejected(self):
        with self.app.app_context():
            db=self.app.get_db()
            db.execute('INSERT INTO blackjack_balances(user_id,balance) VALUES(?,999999)',(self.ids[0],));db.commit()
        self.join()
        self.assertEqual(self.status()['game']['bankroll'],5000)
        self.assertEqual(self.act('refill').status_code,409)
        self.assertEqual(self.money()['balance'],5000)
        self.assertEqual(self.money()['entries'],[])

    def test_win_is_same_account_in_table_profile_and_ranking(self):
        self.begin(['10S','9H','9D','8C'])
        revision=self.status()['revision']
        self.assertEqual(self.act('stand',revision=revision).status_code,200)
        self.assertEqual(self.act('stand',revision=revision).status_code,409)
        money=self.money()
        self.assertEqual(money['entries'],[-500,1000])
        self.assertEqual((money['balance'],money['current'],money['peak']),(5500,5500,5500))
        self.assertEqual(self.status()['game']['bankroll'],5500)

    def test_loss_push_surrender_and_blackjack_amounts(self):
        cases=[(['10S','9H','7D','9C'],'stand',4500,[-500]),
               (['10S','10H','8D','8C'],'stand',5000,[-500,500]),
               (['10S','10H','6D','9C'],'surrender',4750,[-500,250]),
               (['AS','9H','KD','8C'],None,5750,[-500,1250])]
        # One persistent table/account: compare each hand's delta and entry slice.
        expected=5000
        for opening,command,closing,entries in cases:
            with self.subTest(command=command,opening=opening):
                before=self.money()
                if self.status()['viewer_seat'] is None:self.join()
                self.rig(opening)
                self.assertEqual(self.act('bet').status_code,200)
                if command:self.assertEqual(self.act(command).status_code,200)
                expected += closing-5000
                self.assertEqual(self.money()['balance'],expected)
                self.assertEqual(self.money()['entries'][len(before['entries']):],entries)

    def test_double_split_and_insurance_keep_all_ledger_movements(self):
        self.begin(['5S','9H','6D','8C','10D'])
        self.assertEqual(self.act('double').status_code,200)
        self.assertEqual(self.money()['entries'],[-500,-500,2000])
        self.assertEqual(self.money()['balance'],6000)
        self.rig(['8S','9H','8D','8C','3S','10D','10S'])
        self.act('bet');self.assertEqual(self.act('split').status_code,200)
        self.act('hit');self.act('stand')
        self.assertEqual(self.money()['entries'][-4:],[-500,-500,1000,1000])
        self.assertEqual(self.money()['balance'],7000)
        self.rig(['10S','AH','8D','KS'])
        self.act('bet')
        self.assertEqual(self.status()['phase'],'insurance')
        self.assertEqual(self.act('insurance').status_code,200)
        self.assertEqual(self.status()['phase'],'turn')
        self.assertEqual(self.act('stand').status_code,200)
        self.assertEqual(self.money()['entries'][-3:],[-500,-250,750])
        self.assertEqual(self.money()['balance'],7000)

    def test_nopeek_bank_blackjack_returns_only_additional_wager(self):
        self.begin(['5S','KS','6D','AS','10D'])
        self.assertEqual(self.status()['phase'],'turn')
        self.assertEqual(self.act('double').status_code,200)
        self.assertEqual(self.money()['entries'],[-500,-500,500])
        self.assertEqual(self.money()['balance'],4500)

    def test_leaving_loses_held_bet_without_second_debit(self):
        self.join();self.join(1,'3')
        self.act('bet')
        self.assertEqual(self.leave().status_code,200)
        self.leave()
        self.assertEqual(self.money()['entries'],[-500])
        self.assertEqual(self.money()['balance'],4500)

    def test_failed_state_save_rolls_back_wallet_and_peak(self):
        self.join();self.join(1,'3')
        with patch('blackjack_store.game.save',side_effect=RuntimeError('simulated disk error')):
            with self.assertRaisesRegex(RuntimeError,'simulated disk error'):self.act('bet')
        self.assertEqual(self.money()['entries'],[])
        self.assertEqual(self.money()['balance'],5000)
        self.assertEqual(self.status()['game']['own_bet'],0)

    def test_duplicate_parallel_bets_charge_once(self):
        self.join();self.join(1,'3')
        revision=self.status()['revision']
        barrier=Barrier(2)
        def request():
            client=self.client(self.ids[0]);barrier.wait()
            return client.post('/karten/blackjack/aktion',data=dict(csrf_token='wallet-csrf',revision=revision,action='bet',amount='500')).status_code
        with ThreadPoolExecutor(max_workers=2) as workers:codes=list(workers.map(lambda _:request(),range(2)))
        self.assertEqual(sorted(codes),[200,409])
        self.assertEqual(self.money()['entries'],[-500])

    def test_shop_and_table_cannot_spend_same_funds(self):
        self.app.config['PREVIEW_CURRENCY_BONUS']=500
        self.join();self.join(1,'3')
        revision=self.status()['revision']
        item=next(item for item in PHRASE_CATALOG if item['price']==250)
        barrier=Barrier(2)
        def bet():
            client=self.client(self.ids[0]);barrier.wait()
            return client.post('/karten/blackjack/aktion',data=dict(csrf_token='wallet-csrf',revision=revision,action='bet',amount='500')).status_code
        def buy():
            client=self.client(self.ids[0]);barrier.wait()
            return client.post('/shop/kaufen/phrase/'+item['id'],data=dict(csrf_token='wallet-csrf')).status_code
        with ThreadPoolExecutor(max_workers=2) as workers:
            a=workers.submit(bet);b=workers.submit(buy);a.result();b.result()
        with self.app.app_context():
            db=self.app.get_db()
            purchases=db.execute('SELECT COUNT(*) FROM shop_purchases WHERE user_id=?',(self.ids[0],)).fetchone()[0]
        placed=bool(self.status()['game']['own_bet'])
        self.assertEqual(int(placed)+purchases,1)
        self.assertEqual(self.money()['balance'],0 if placed else 250)

    def test_two_clock_workers_pay_blackjack_only_once(self):
        self.join();self.rig(['AS','9H','KD','8C'],automatic=False)
        self.assertEqual(self.act('bet').status_code,200)
        barrier=Barrier(2)
        def tick():
            barrier.wait();return tick_clock(self.app)
        with ThreadPoolExecutor(max_workers=2) as workers:list(workers.map(lambda _:tick(),range(2)))
        self.assertEqual(self.money()['entries'],[-500,1250])
        self.assertEqual(self.money()['balance'],5750)

    def test_pending_test_table_finishes_without_conversion(self):
        # Construct a pre-update test table, retaining its original test balance.
        self.app.config['BLACKJACK_CURRENCY']='test-ikuehe'
        self.app.config['BLACKJACK_TEST_START_BALANCE']=10000
        with self.app.app_context():
            db=self.app.get_db()
            with db:
                db.execute('BEGIN IMMEDIATE')
                state=game.initial_state()
                state['table_rules']=dict(fixed_bet=500,currency='test-ikuehe',test_refill=10000,dealer_peek=False)
                db.execute('UPDATE blackjack_game SET state_json=?',(json.dumps(state),))
        tick_clock(self.app)
        self.join();self.join(1,'3')
        self.rig(['10S','9H','7D','9C'])
        self.act('bet')
        self.app.config['BLACKJACK_CURRENCY']=store.ACCOUNT_CURRENCY
        tick_clock(self.app)
        status=self.status()
        self.assertTrue(status['game']['currency_change_pending'])
        self.assertEqual(status['game']['currency'],'test-ikuehe')
        self.assertEqual(self.money()['balance'],5000)
        self.assertEqual(self.join(1,'3').status_code,200) # Existing seat is idempotent.
        self.leave();self.leave(1);tick_clock(self.app)
        self.assertEqual(self.status()['game']['currency'],store.ACCOUNT_CURRENCY)
        self.assertEqual(self.status()['game']['bankroll'],5000)
        self.assertEqual(self.money()['entries'],[])
        with self.app.app_context():
            amount=self.app.get_db().execute('SELECT balance FROM blackjack_balances WHERE user_id=?',(self.ids[0],)).fetchone()[0]
        self.assertEqual(amount,9500)

    def test_shop_and_bet_each_observe_prior_committed_spend(self):
        self.app.config['PREVIEW_CURRENCY_BONUS']=500
        self.join();self.join(1,'3')
        item=next(item for item in PHRASE_CATALOG if item['price']==250)
        path='/shop/kaufen/phrase/'+item['id']
        self.clients[0].post(path,data=dict(csrf_token='wallet-csrf'))
        self.assertEqual(self.act('bet').status_code,409)
        self.assertEqual(self.act('bet',index=1).status_code,200)
        self.clients[1].post(path,data=dict(csrf_token='wallet-csrf'))
        with self.app.app_context():
            db=self.app.get_db()
            self.assertEqual(account_wallet.balance(db,self.ids[0],500),250)
            self.assertEqual(account_wallet.balance(db,self.ids[1],500),0)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM shop_purchases WHERE user_id=?',(self.ids[0],)).fetchone()[0],1)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM shop_purchases WHERE user_id=?',(self.ids[1],)).fetchone()[0],0)

    def test_adding_ledger_schema_preserves_existing_accounts_and_game_records(self):
        tables=['users','attempts','shop_purchases','question_usage','blackjack_balances','blackjack_seats','blackjack_game']
        self.join()
        with self.app.app_context():
            db=self.app.get_db()
            self.assertEqual(db.execute('SELECT COUNT(*) FROM currency_entries').fetchone()[0],0)
            # Disposable fixture only: reproduce a pre-ledger schema.
            db.execute('DROP TABLE currency_entries');db.commit()
            before={name:[tuple(row) for row in db.execute('SELECT * FROM '+name)] for name in tables}
        restarted=create_app(dict(self.app.config))
        with restarted.app_context():
            db=restarted.get_db()
            after={name:[tuple(row) for row in db.execute('SELECT * FROM '+name)] for name in tables}
            self.assertEqual(after,before)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM currency_entries').fetchone()[0],0)
            self.assertEqual(player_currency_balance(self.ids[0]),5000)

    def test_other_game_lobbies_use_the_same_updated_account_balance(self):
        from dice_table import _members as dice_members
        from nerd_mode import _members as perfect_members
        self.begin(['10S','9H','9D','8C']);self.act('stand')
        dice=self.clients[0].post('/karten/wuerfeltisch/erstellen',data=dict(csrf_token='wallet-csrf'))
        perfect=self.clients[0].post('/nerd/erstellen',data=dict(csrf_token='wallet-csrf'))
        self.assertEqual(dice.status_code,302)
        self.assertEqual(perfect.status_code,302)
        dice_id=int(dice.headers['Location'].rstrip('/').split('/')[-1])
        perfect_id=int(perfect.headers['Location'].rstrip('/').split('/')[-1])
        with self.app.app_context():
            self.assertEqual(dice_members(dice_id)[0]['currency_balance'],5500)
            self.assertEqual(perfect_members(perfect_id)[0]['currency_balance'],5500)
        self.assertEqual(self.money()['entries'],[-500,1000])
