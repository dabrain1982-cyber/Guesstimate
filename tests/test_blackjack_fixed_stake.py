import unittest

from blackjack_clock import tick_clock
from tests.test_blackjack_rounds import BlackjackRoundTests
import blackjack_game as engine


class FixedStakeTests(unittest.TestCase):
    client = BlackjackRoundTests.client
    join = BlackjackRoundTests.join
    leave = BlackjackRoundTests.leave
    state = BlackjackRoundTests.state
    play = BlackjackRoundTests.play
    tearDown = BlackjackRoundTests.tearDown

    def setUp(self):
        BlackjackRoundTests.setUp(self)
        self.app.config.update(BLACKJACK_FIXED_STAKE=500, BLACKJACK_TEST_START_BALANCE=10000)
        tick_clock(self.app)

    def test_fixed_stake_and_separate_wallet_survive_rejected_edits(self):
        self.join(0, '2'); self.join(1, '1')
        before = self.state()['game']
        self.assertEqual(before['bankroll'], 10000)
        self.assertEqual(before['fixed_bet'], 500)
        self.assertEqual(before['currency'], 'test-ikuehe')
        for amount in (50, 490, 510, 1000):
            self.assertEqual(self.play('bet', amount=amount).status_code, 409)
        self.assertEqual(self.play('bet', amount=500).status_code, 200)
        self.assertFalse(self.state()['game']['can_bet'])
        self.assertEqual(self.play('cancel-bet').status_code, 409)
        self.assertEqual(self.state()['game']['bankroll'], 9500)

    def test_card_tables_navigation_forfeits_once_and_frees_seat(self):
        self.join(0, '2'); self.join(1, '1'); self.play('bet', amount=500)
        response = self.leave(0, navigate='card_tables')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith('/karten/kartentische'))
        self.assertIsNone(self.state()['viewer_seat'])
        self.assertEqual(self.state()['game']['bankroll'], 9500)
        self.leave(0, navigate='card_tables')
        self.assertEqual(self.state()['game']['bankroll'], 9500)
        self.assertEqual(self.state()['game']['bets'], [])

    def test_existing_balance_and_legacy_bet_are_not_reset_or_repriced(self):
        self.join(0, '2'); self.join(1, '1')
        with self.app.app_context():
            db = self.app.get_db()
            state, balances, _ = engine.load(db)
            balances[str(self.ids[0])] = 925
            state['bets'][str(self.ids[0])] = 50
            engine.save(db, state, balances); db.commit()
        tick_clock(self.app)
        self.assertEqual(self.state()['game']['bankroll'], 925)
        self.assertEqual(self.state()['game']['own_bet'], 50)
        self.assertEqual(self.play('bet', amount=500).status_code, 409)

    def test_refill_requires_explicit_action_and_insufficient_test_funds(self):
        self.join(0, '2')
        self.assertEqual(self.play('refill').status_code, 409)
        with self.app.app_context():
            db = self.app.get_db()
            db.execute('UPDATE blackjack_balances SET balance=425 WHERE user_id=?', (self.ids[0],)); db.commit()
        tick_clock(self.app)
        self.assertEqual(self.state()['game']['bankroll'], 425)
        self.assertFalse(self.state()['game']['can_bet'])
        self.assertEqual(self.play('refill').status_code, 200)
        self.assertEqual(self.state()['game']['bankroll'], 10000)

    def test_leaving_live_hand_forfeits_even_when_it_would_have_won(self):
        self.join(0, '2'); self.join(1, '1')
        with self.app.app_context():
            db = self.app.get_db()
            state, balances, _ = engine.load(db)
            state['shoe'] = ['2C'] * 156 + list(reversed(['10S','10H','9D','7S','8C','8D']))
            engine.save(db, state, balances); db.commit()
        self.play('bet', amount=500); self.play('bet', index=1, amount=500)
        self.leave(0)
        self.play('stand', index=1)
        self.assertEqual(self.state()['game']['phase'], 'result')
        self.assertEqual(self.state()['game']['bankroll'], 9500)
        self.assertIsNone(self.state()['viewer_seat'])

    def test_exit_forfeits_placed_insurance_even_if_bank_has_blackjack(self):
        self.join(0, '2'); self.join(1, '1')
        with self.app.app_context():
            db = self.app.get_db()
            state, balances, _ = engine.load(db)
            state['shoe'] = ['2C'] * 156 + list(reversed(['AS','9S','AH','KD','8D','KC']))
            engine.save(db, state, balances); db.commit()
        self.play('bet', amount=500); self.play('bet', index=1, amount=500)
        self.play('insurance')
        self.leave(0)
        self.play('no-insurance', index=1)
        self.assertEqual(self.state()['game']['phase'], 'result')
        self.assertEqual(self.state()['game']['bankroll'], 9250)

    def test_pair_reports_missing_split_funds_then_enables_with_enough_funds(self):
        self.join(0, '2')
        with self.app.app_context():
            db = self.app.get_db()
            state, balances, _ = engine.load(db)
            balances[str(self.ids[0])] = 750
            state['shoe'] = ['2C'] * 156 + list(reversed(['4D','5H','4D','10S','2S','3H']))
            engine.save(db, state, balances); db.commit()
        self.play('bet', amount=500)
        view = self.state()['game']
        self.assertEqual(view['blocked_actions'], {'split': {'required': 500, 'available': 250}})
        self.assertNotIn('split', view['actions'])
        self.assertEqual(self.play('split').status_code, 409)
        self.assertEqual(self.state()['game']['bankroll'], 250)
        with self.app.app_context():
            db = self.app.get_db()
            db.execute('UPDATE blackjack_balances SET balance=500 WHERE user_id=?', (self.ids[0],)); db.commit()
        self.assertEqual(self.state()['game']['blocked_actions'], {})
        self.assertIn('split', self.state()['game']['actions'])
        self.assertEqual(self.play('split').status_code, 200)
        self.assertEqual(self.state()['game']['bankroll'], 0)

    def test_no_peek_config_keeps_decision_and_returns_double_addition(self):
        self.app.config['BLACKJACK_DEALER_PEEK'] = False
        tick_clock(self.app)
        self.join(0, '2')
        with self.app.app_context():
            db = self.app.get_db()
            state, balances, _ = engine.load(db)
            state['shoe'] = ['2C'] * 156 + list(reversed(['5S','10H','6D','AC','10C']))
            engine.save(db, state, balances); db.commit()
        view = self.play('bet', amount=500).get_json()['game']
        self.assertFalse(view['dealer_peek'])
        self.assertEqual(view['phase'], 'turn')
        self.assertEqual(view['dealer'], ['10H', None])
        self.assertIn('double', view['actions'])
        result = self.play('double').get_json()['game']
        self.assertEqual(result['dealer'], ['10H', 'AC'])
        self.assertEqual(result['bankroll'], 9500)
        self.assertEqual(result['players'][0]['hands'][0]['net'], -500)

    def test_new_rule_does_not_rewrite_the_running_round(self):
        self.join(0, '2')
        with self.app.app_context():
            db = self.app.get_db()
            state, balances, _ = engine.load(db)
            state['shoe'] = ['2C'] * 156 + list(reversed(['9S','8H','7D','10C']))
            engine.save(db, state, balances); db.commit()
        self.play('bet', amount=500)
        self.assertTrue(self.state()['game']['dealer_peek'])
        self.app.config['BLACKJACK_DEALER_PEEK'] = False
        tick_clock(self.app)
        view = self.state()['game']
        self.assertTrue(view['dealer_peek'])
        self.assertFalse(view['next_dealer_peek'])
        self.play('stand')
        tick_clock(self.app, now=view.get('clock', {}).get('deadline') or engine.clock_now())
        result = self.state()['game']
        tick_clock(self.app, now=result['clock']['deadline'] + 1)
        self.assertEqual(self.state()['game']['phase'], 'betting')
        self.assertFalse(self.state()['game']['dealer_peek'])
        self.play('bet', amount=500)
        self.assertFalse(self.state()['game']['dealer_peek'])
