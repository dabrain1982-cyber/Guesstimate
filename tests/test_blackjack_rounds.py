from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import unittest
from app import create_app

import blackjack_game as engine
from tests.test_blackjack_seating import BlackjackSeatingTests


class BlackjackRoundTests(BlackjackSeatingTests):
    def play(self, command, index=0, amount=None, revision=None):
        client, token = self.clients[index]
        data = dict(csrf_token=token, action=command, revision=self.state(index)['revision'] if revision is None else revision)
        if amount is not None:
            data['amount'] = amount
        return client.post('/karten/blackjack/aktion', data=data)

    def prepare(self, cards, count=1, bet=50):
        for index in range(count):
            self.join(index, str(index+1) if count>1 else '2')
            self.assertEqual(self.play('bet', index, bet).status_code, 200)
        with self.app.app_context():
            db = self.app.get_db()
            state, balances, _ = engine.load(db)
            state['shoe'] = ['2C']*156 + list(reversed(cards))
            engine.save(db, state, balances)
            db.commit()
        self.assertEqual(self.play('deal').status_code, 200)
        return self.state()['game']

    def test_values_soft_aces_and_real_six_deck_shuffle(self):
        self.assertEqual(engine.value(['AS','AH','9C']), (21,True))
        self.assertEqual(engine.value(['AS','AH','9C','10H']), (21,False))
        self.join(0,'2');self.play('bet',amount=50);self.play('deal')
        with self.app.app_context():
            state, _, _ = engine.load(self.app.get_db())
        cards=state['shoe']+state['dealer']+[c for p in state['players'] for h in p['hands'] for c in h['cards']]
        self.assertEqual(len(cards),312)
        self.assertEqual(set(Counter(cards).values()),{6})
        self.assertEqual(len(set(cards)),52)

    def test_natural_pays_three_to_two_and_cannot_be_paid_twice(self):
        result=self.prepare(['AS','10H','KH','7C'])
        self.assertEqual(result['phase'],'result');self.assertEqual(result['bankroll'],1075)
        self.assertEqual(result['players'][0]['hands'][0]['result'],'Blackjack')
        self.assertEqual(self.play('stand').status_code,409)
        self.assertEqual(self.state()['game']['bankroll'],1075)

    def test_dealer_soft_seventeen_stands_and_push_refunds(self):
        self.prepare(['10S','AS','7H','6C'])
        self.play('no-insurance');result=self.play('stand').get_json()['game']
        self.assertEqual(result['dealer'],['AS','6C']);self.assertEqual(result['bankroll'],1000)
        self.assertEqual(result['players'][0]['hands'][0]['result'],'Gleichstand')

    def test_dealer_hole_and_shoe_never_leak_before_resolution(self):
        view=self.prepare(['10S','6H','7D','KC'])
        self.assertEqual(view['dealer'],['6H',None]);self.assertEqual(view['dealer_total'],6)
        self.assertNotIn('shoe',view)
        watcher=self.state(1)['game'];self.assertEqual(watcher['dealer'],['6H',None])
        self.assertEqual(self.play('hit',1).status_code,409)
        self.assertEqual(self.state()['game']['bankroll'],950)

    def test_insurance_dealer_blackjack_and_natural_push(self):
        self.prepare(['9S','AS','7D','KC'])
        view=self.play('insurance').get_json()['game']
        self.assertEqual(view['phase'],'result');self.assertEqual(view['bankroll'],1000)
        self.assertEqual(view['players'][0]['insurance_net'],50)
        self.play('next')
        self.prepare(['AH','AS','QD','KC'])
        view=self.play('no-insurance').get_json()['game'];self.assertEqual(view['bankroll'],1000)

    def test_insurance_loss_double_exactly_one_card_and_stale_replay(self):
        self.prepare(['5S','AS','6D','5C','10D','2H'])
        self.play('insurance');revision=self.state()['revision']
        result=self.play('double',revision=revision).get_json()['game']
        self.assertEqual(result['phase'],'result')
        self.assertEqual(result['players'][0]['hands'][0]['cards'],['5S','6D','10D'])
        self.assertEqual(result['bankroll'],1075)
        self.assertEqual(self.play('double',revision=revision).status_code,409)
        self.assertEqual(self.state()['game']['bankroll'],1075)

    def test_late_surrender_refunds_half(self):
        self.prepare(['10S','10H','6D','7C'])
        result=self.play('surrender').get_json()['game']
        self.assertEqual(result['bankroll'],975)
        self.assertEqual(result['players'][0]['hands'][0]['result'],'Aufgegeben')

    def test_split_then_double_and_second_hand_in_order(self):
        self.prepare(['8S','10H','8D','7C','3S','2H','10C'])
        result=self.play('split').get_json()['game']
        self.assertEqual(len(result['players'][0]['hands']),2)
        self.assertNotIn('surrender',result['actions']);self.assertNotIn('split',result['actions'])
        self.play('double');result=self.play('stand').get_json()['game']
        self.assertEqual(result['phase'],'result');self.assertEqual(result['bankroll'],1050)

    def test_split_aces_get_one_card_and_twenty_one_is_not_natural(self):
        self.prepare(['AS','10H','AD','7C','KS','QH'])
        result=self.play('split').get_json()['game']
        self.assertEqual(result['phase'],'result');self.assertEqual(result['bankroll'],1100)
        self.assertTrue(all(len(h['cards'])==2 for h in result['players'][0]['hands']))
        self.assertTrue(all(h['result']=='Gewonnen' for h in result['players'][0]['hands']))

    def test_three_players_are_serialized_and_waiting_player_joins_next_round(self):
        self.prepare(['10S','9S','8S','10H','7D','8D','9D','7C'],3)
        self.assertEqual(self.state()['game']['active_seat'],1)
        self.assertEqual(self.play('hit',1).status_code,409)
        self.play('stand',0);self.assertEqual(self.state()['game']['active_seat'],2)
        self.play('stand',1);self.assertEqual(self.state()['game']['active_seat'],3)
        self.play('stand',2);self.assertEqual(self.state()['game']['phase'],'result')
        self.play('next');self.play('bet',amount=50);self.play('deal')
        self.assertTrue(self.state(1)['game']['waiting_next'])

    def test_pending_leave_forfeits_hand_and_releases_after_settlement(self):
        self.prepare(['10S','9S','10H','7D','8D','7C'],2)
        result=self.leave(0).get_json()
        self.assertTrue(result['game']['leaving']);self.assertEqual(result['occupied'],2)
        self.assertEqual(result['game']['active_seat'],2)
        self.assertEqual(self.join(2,'1').status_code,409)
        self.play('stand',1);state=self.state()
        self.assertEqual(state['game']['phase'],'result');self.assertEqual(state['occupied'],1)
        self.assertIsNone(state['viewer_seat']);self.assertEqual(self.join(2,'1').status_code,200)

    def test_placed_bet_is_locked_and_leaving_forfeits_once(self):
        self.join(0,'2');self.play('bet',amount=100)
        self.assertEqual(self.state()['game']['bankroll'],900)
        self.assertEqual(self.play('bet',amount=200).status_code,409)
        self.assertEqual(self.play('cancel-bet').status_code,409)
        self.assertEqual(self.state()['game']['bankroll'],900)
        self.leave(0);self.assertEqual(self.state()['game']['bankroll'],900)
        self.join(0,'2')
        self.play('bet',amount=50);self.leave(0);self.assertEqual(self.state()['game']['bankroll'],850)
        self.join(0,'2');self.assertEqual(self.play('refill').status_code,409)
        for bet in ('-10','11','501','10000','1.5'):
            self.assertIn(self.play('bet',amount=bet).status_code,(400,409))
        self.assertEqual(self.state()['game']['bankroll'],850)

    def test_duplicate_concurrent_draw_changes_state_once(self):
        self.prepare(['2S','10H','3D','7C','2D','3C'])
        revision=self.state()['revision'];barrier=Barrier(2)
        # Two independent sessions for the same user, as with two tabs.
        second=self.client(self.ids[0],'second-tab')
        def send(index):
            client,token=self.clients[0] if index==0 else second
            barrier.wait(timeout=5)
            return client.post('/karten/blackjack/aktion',data=dict(csrf_token=token,action='hit',revision=revision)).status_code
        with ThreadPoolExecutor(max_workers=2) as pool:responses=list(pool.map(send,(0,1)))
        self.assertEqual(sorted(responses),[200,409])
        self.assertEqual(len(self.state()['game']['players'][0]['hands'][0]['cards']),3)

    def test_bust_loses_once_and_next_round_keeps_persistent_balance(self):
        self.prepare(['10S','6H','6D','9C','KC'])
        result=self.play('hit').get_json()['game']
        self.assertEqual(result['bankroll'],950);self.assertEqual(result['players'][0]['hands'][0]['result'],'Überkauft')
        self.assertEqual(self.play('hit').status_code,409)
        self.play('next');self.app=create_app(self.config)
        self.assertEqual(self.state()['game']['bankroll'],950)
        self.assertEqual(self.state()['game']['phase'],'betting')

    def test_insurance_waits_for_all_and_bank_blackjack_blocks_player_moves(self):
        self.prepare(['9S','8S','AH','7D','9D','KC'],2)
        self.play('no-insurance',0)
        self.assertEqual(self.state()['game']['phase'],'insurance')
        self.assertEqual(self.state()['game']['dealer'],['AH',None])
        self.assertEqual(self.play('surrender').status_code,409)
        self.play('insurance',1)
        self.assertEqual(self.state()['game']['phase'],'result')
        self.assertEqual(self.state(1)['game']['bankroll'],1000)
        self.assertEqual(self.play('hit',1).status_code,409)

    def test_request_guards_and_refill_do_not_touch_account_tables(self):
        self.join(0,'2')
        client,_=self.clients[0]
        self.assertEqual(client.post('/karten/blackjack/aktion',data=dict(action='bet',amount='50',revision=self.state()['revision'])).status_code,400)
        self.assertEqual(self.play('bet',1,amount=50).status_code,409)
        with self.app.app_context():
            db=self.app.get_db();db.execute('UPDATE blackjack_balances SET balance=5 WHERE user_id=?',(self.ids[0],));db.commit()
            before=[tuple(r) for r in db.execute('SELECT * FROM users')]
        result=self.play('refill').get_json()['game'];self.assertEqual(result['bankroll'],1000)
        self.assertEqual(self.play('refill').status_code,409)
        with self.app.app_context():
            self.assertEqual([tuple(r) for r in self.app.get_db().execute('SELECT * FROM users')],before)


if __name__=='__main__':unittest.main()
