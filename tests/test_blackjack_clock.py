from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest.mock import patch
import unittest

from app import create_app
from blackjack_clock import tick_clock, start_blackjack_clock
import blackjack_game as engine
from tests.test_blackjack_rounds import BlackjackRoundTests


class BlackjackClockTests(BlackjackRoundTests):
    def arm(self, now=1000):
        self.now=now
        timer=patch('blackjack_game.clock_now',side_effect=lambda:self.now)
        timer.start();self.addCleanup(timer.stop)
        tick_clock(self.app,self.now)

    def tick(self, now):
        self.now=now
        return tick_clock(self.app,self.now)

    def seed_cards(self, cards):
        with self.app.app_context():
            db=self.app.get_db();state,balances,_=engine.load(db)
            state['shoe']=['2C']*156+list(reversed(cards))
            engine.save(db,state,balances);db.commit()

    def ready(self):
        self.join(0,'2');self.join(1,'1');self.play('bet',amount=50)
        self.seed_cards(['10S','10H','7D','7C'])
        self.arm()

    def test_automatic_deal_at_deadline_and_locked_bet_does_not_extend_it(self):
        self.ready()
        self.assertEqual(self.state()['game']['clock']['deadline'],1020)
        self.tick(1005);self.assertEqual(self.play('bet',amount=60).status_code,409)
        self.assertEqual(self.state()['game']['clock']['deadline'],1020)
        self.assertFalse(self.tick(1019))
        self.assertTrue(self.tick(1020))
        view=self.state()['game'];self.assertEqual(view['round'],1)
        self.assertEqual(view['phase'],'turn');self.assertEqual(view['own_wager'],50)
        self.assertEqual(view['bankroll'],950);self.assertIsNone(view['clock']['deadline'])

    def test_result_pause_opens_next_window_without_repeating_any_bet(self):
        self.ready();self.tick(1020);self.play('stand')
        view=self.state()['game'];self.assertEqual(view['phase'],'result')
        self.assertEqual(view['bankroll'],1000);self.assertEqual(view['clock']['deadline'],1030)
        self.assertFalse(self.tick(1029));self.tick(1030)
        view=self.state()['game'];self.assertEqual(view['phase'],'betting')
        self.assertEqual(view['clock']['deadline'],1050);self.assertEqual(view['own_bet'],0)
        self.tick(1050);self.assertIsNone(self.state()['game']['clock']['deadline'])
        self.tick(100000)
        view=self.state()['game'];self.assertEqual(view['round'],1);self.assertEqual(view['bankroll'],1000)

    def test_empty_window_waits_then_explicit_bet_restarts_countdown(self):
        self.join(0,'2');self.join(1,'1');self.arm();self.tick(1020)
        self.assertIsNone(self.state()['game']['clock']['deadline'])
        self.assertFalse(self.tick(1500))
        self.play('bet',amount=50)
        self.assertEqual(self.state()['game']['clock']['deadline'],1520)
        self.assertEqual(self.state()['game']['bankroll'],950)

    def test_empty_table_stops_clock_and_leaving_forfeits_reserved_bet(self):
        self.arm();self.assertIsNone(self.state()['game']['clock']['deadline'])
        self.tick(2000);self.join(0,'2');self.join(1,'1');self.play('bet',amount=50)
        self.assertEqual(self.state()['game']['clock']['deadline'],2020)
        self.leave(0)
        self.leave(1)
        self.assertIsNone(self.state()['game']['clock']['deadline'])
        self.assertEqual(self.state()['game']['bankroll'],950)
        self.tick(3000);self.assertEqual(self.state()['game']['round'],0)

    def test_two_clock_workers_cannot_deal_twice(self):
        self.ready();self.now=1020;barrier=Barrier(2)
        def tick(index):
            barrier.wait(timeout=5);return tick_clock(self.app,1020)
        with ThreadPoolExecutor(max_workers=2) as pool:outcomes=list(pool.map(tick,(0,1)))
        self.assertEqual(sorted(outcomes),[False,True])
        self.assertEqual(self.state()['game']['round'],1)
        self.assertEqual(self.state()['game']['bankroll'],950)

    def test_predeal_bets_remain_available_and_status_is_readonly(self):
        self.ready()
        self.assertEqual(self.play('deal').status_code,409)
        revision=self.state()['revision'];self.now=1021
        self.assertEqual(self.state()['revision'],revision)
        self.assertEqual(self.state()['game']['phase'],'betting')
        self.assertEqual(self.play('bet',index=1,amount=100).status_code,200)
        self.assertEqual(self.state(1)['game']['bankroll'],900)
        self.tick(1021);self.play('stand')
        self.assertEqual(self.play('next').status_code,409)

    def test_restart_preserves_deadline_and_missed_time_does_not_create_extra_rounds(self):
        self.ready();deadline=self.state()['game']['clock']['deadline']
        self.app=create_app(self.config)
        self.assertEqual(self.state()['game']['clock']['deadline'],deadline)
        self.tick(100000)
        self.assertEqual(self.state()['game']['round'],1)
        self.assertEqual(self.state()['game']['phase'],'turn')
        self.play('stand')
        self.assertEqual(self.state()['game']['clock']['deadline'],100010)

    def test_newcomer_waits_for_next_window_and_no_background_threads_in_tests(self):
        self.ready();self.tick(1020);self.join(2,'3')
        self.assertTrue(self.state(2)['game']['waiting_next'])
        self.play('stand');self.tick(1030);self.play('bet',index=2,amount=20)
        self.tick(1050);view=self.state(2)['game']
        self.assertEqual(view['round'],2)
        self.assertEqual([p['seat'] for p in view['players']],[3])
        self.assertEqual(view['own_wager'],20)
        self.assertIsNone(start_blackjack_clock(self.app))


if __name__=='__main__':unittest.main()
