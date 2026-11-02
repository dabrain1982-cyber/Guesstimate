from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import unittest
from app import create_app

import blackjack_game as engine
from tests.test_blackjack_clock import BlackjackClockTests


class BlackjackPrebetTests(BlackjackClockTests):
    def test_only_player_starts_on_bet_without_countdown(self):
        self.join(0,'2');self.seed_cards(['10S','10H','7D','7C']);self.arm()
        self.assertIsNone(self.state()['game']['clock']['deadline'])
        result=self.play('bet',amount=50).get_json()['game']
        self.assertEqual(result['phase'],'turn');self.assertEqual(result['round'],1)
        self.assertEqual(result['bankroll'],950)
        self.assertIsNone(result['clock']['deadline'])

    def test_all_seated_players_ready_starts_before_shared_deadline(self):
        self.join(0,'2');self.join(1,'1');self.seed_cards(['10S','9S','10H','7D','8D','7C']);self.arm()
        self.play('bet',amount=50)
        self.assertEqual(self.state()['game']['phase'],'betting')
        result=self.play('bet',index=1,amount=20).get_json()['game']
        self.assertEqual(result['phase'],'turn');self.assertEqual(result['round'],1)
        self.assertEqual(len(result['players']),2)

    def test_newcomer_reserves_during_running_hand_and_carries_bet_to_deal(self):
        self.prepare(['10S','10H','7D','7C']);self.arm();self.join(1,'1')
        before=self.state(1)['game']['players']
        result=self.play('bet',index=1,amount=30).get_json()['game']
        self.assertEqual(result['phase'],'turn');self.assertEqual(result['players'],before)
        self.assertEqual(result['next_bet'],30);self.assertEqual(result['own_wager'],0)
        self.assertEqual(result['bankroll'],970)
        self.app=create_app(self.config)
        self.assertEqual(self.state(1)['game']['next_bet'],30)
        self.play('stand');self.tick(1010)
        self.assertEqual(self.state(1)['game']['own_bet'],30)
        self.play('bet',amount=50)
        view=self.state(1)['game'];self.assertEqual(view['round'],2)
        self.assertTrue(any(p['own'] for p in view['players']))
        self.assertEqual(view['own_wager'],30);self.assertEqual(view['next_bet'],0)
        self.assertEqual(view['bankroll'],970)

    def test_future_bet_is_locked_and_leaving_forfeits_reservation(self):
        self.prepare(['10S','10H','7D','7C']);self.arm();self.join(1,'1')
        self.play('bet',index=1,amount=40)
        self.assertEqual(self.play('bet',index=1,amount=20).status_code,409)
        self.assertEqual(self.play('cancel-bet',index=1).status_code,409)
        self.assertEqual(self.state(1)['game']['bankroll'],960)
        self.leave(1)
        self.assertEqual(self.state(1)['game']['bankroll'],960)
        self.assertEqual(self.state()['game']['phase'],'turn')
        self.assertEqual(self.play('bet',amount=20).status_code,409)
        self.assertEqual(self.state()['game']['bankroll'],950)
        self.assertEqual(self.play('cancel-bet').status_code,409)
        self.assertEqual(self.state()['game']['bankroll'],950)
        self.assertEqual(self.play('cancel-bet').status_code,409)

    def test_solo_new_bet_skips_result_pause_and_is_not_repeated(self):
        self.prepare(['10S','10H','7D','7C']);self.arm();self.play('stand')
        self.assertEqual(self.state()['game']['phase'],'result')
        result=self.play('bet',amount=20).get_json()['game']
        self.assertEqual(result['round'],2);self.assertNotEqual(result['phase'],'betting')
        self.assertEqual(result['own_wager'],20);self.assertEqual(result['own_bet'],0)

    def test_pending_leave_rejects_future_bet_and_keeps_forfeiture(self):
        self.prepare(['10S','9S','10H','7D','8D','7C'],2);self.arm()
        self.assertEqual(self.play('bet',amount=20).status_code,409)
        self.assertEqual(self.state()['game']['bankroll'],950)
        self.leave(0)
        self.assertEqual(self.state()['game']['bankroll'],950)
        self.assertEqual(self.play('bet',amount=30).status_code,409)
        self.play('stand',1)
        self.assertEqual(self.state()['game']['bankroll'],950)

    def test_live_hand_cannot_place_another_initial_bet_but_double_remains_separate(self):
        self.prepare(['5S','10H','6D','7C'],bet=500);self.arm()
        self.assertEqual(self.play('bet',amount=500).status_code,409)
        self.assertEqual(self.state()['game']['bankroll'],500)
        self.assertIn('double',self.state()['game']['actions'])
        self.assertEqual(self.play('cancel-bet').status_code,409)
        self.assertEqual(self.play('double').status_code,200)
        self.assertEqual(self.state()['game']['own_wager'],1000)

    def test_button_availability_tracks_unset_placed_live_and_finished_hand(self):
        self.join(0,'2');self.join(1,'1');self.arm()
        self.seed_cards(['10S','10H','7D','7C'])
        self.assertTrue(self.state()['game']['can_bet'])
        self.play('bet',amount=50)
        self.assertFalse(self.state()['game']['can_bet'])
        self.tick(1020)
        self.assertFalse(self.state()['game']['can_bet'])
        self.assertEqual(self.play('bet',amount=20).status_code,409)
        self.assertTrue(self.state(1)['game']['can_bet'])
        self.play('bet',index=1,amount=20)
        self.assertFalse(self.state(1)['game']['can_bet'])
        self.play('stand')
        self.assertTrue(self.state()['game']['can_bet'])
        self.assertFalse(self.state(1)['game']['can_bet'])

    def test_insurance_does_not_offer_a_second_initial_bet_to_participants(self):
        self.prepare(['9S','AS','7D','6C']);self.arm();self.join(1,'1')
        self.assertEqual(self.state()['game']['phase'],'insurance')
        self.assertFalse(self.state()['game']['can_bet'])
        self.assertTrue(self.state(1)['game']['can_bet'])
        self.assertEqual(self.play('bet',amount=20).status_code,409)
        self.play('no-insurance')
        self.assertEqual(self.state()['game']['phase'],'turn')
        self.assertFalse(self.state()['game']['can_bet'])

    def test_duplicate_solo_bet_requests_cannot_create_two_rounds(self):
        self.join(0,'2');self.seed_cards(['10S','10H','7D','7C']);self.arm()
        revision=self.state()['revision'];barrier=Barrier(2);second=self.client(self.ids[0],'prebet-second')
        def send(index):
            client,token=self.clients[0] if index==0 else second
            barrier.wait(timeout=5)
            return client.post('/karten/blackjack/aktion',data=dict(csrf_token=token,action='bet',amount='50',revision=revision)).status_code
        with ThreadPoolExecutor(max_workers=2) as pool:responses=list(pool.map(send,(0,1)))
        self.assertEqual(sorted(responses),[200,409])
        self.assertEqual(self.state()['game']['round'],1)
        self.assertEqual(self.state()['game']['bankroll'],950)


if __name__=='__main__':unittest.main()
