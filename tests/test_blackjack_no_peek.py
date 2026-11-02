import unittest

import blackjack_game as game


class NoPeekTests(unittest.TestCase):
    def deal(self, cards, count=1):
        state = game.initial_state()
        state['table_rules'] = dict(dealer_peek=False, fixed_bet=500)
        balances = {str(i): 10000 for i in range(1, count + 1)}
        seats = {str(i): i for i in range(1, count + 1)}
        for uid in seats:
            game.action(state, balances, seats, uid, 'bet', 500)
        state['shoe'] = ['2C'] * 156 + list(reversed(cards))
        game.action(state, balances, seats, '1', 'deal')
        return state, balances, seats

    def test_ten_up_blackjack_waits_for_player_to_stand(self):
        state, balances, seats = self.deal(['9S', '10H', '7D', 'AC'])
        self.assertEqual(state['phase'], 'turn')
        self.assertIn('hit', game.legal_actions(state, balances, '1'))
        view = game.public_game(state, balances, 1, {'1': 'Spieler'}, seats)
        self.assertEqual(view['dealer'], ['10H', None])
        self.assertEqual(balances['1'], 9500)
        game.action(state, balances, seats, '1', 'stand')
        self.assertEqual(state['phase'], 'result')
        self.assertEqual(balances['1'], 9500)

    def test_insurance_decision_does_not_end_player_turn(self):
        state, balances, seats = self.deal(['9S', 'AH', '7D', 'KC'])
        self.assertEqual(state['phase'], 'insurance')
        game.action(state, balances, seats, '1', 'no-insurance')
        self.assertEqual(state['phase'], 'turn')
        self.assertIn('stand', game.legal_actions(state, balances, '1'))
        game.action(state, balances, seats, '1', 'stand')
        self.assertEqual(state['phase'], 'result')

    def test_every_player_gets_a_turn_before_bank_reveal(self):
        state, balances, seats = self.deal(['9S', '8S', '10H', '7D', '8D', 'AC'], 2)
        game.action(state, balances, seats, '1', 'stand')
        self.assertEqual(state['phase'], 'turn')
        self.assertEqual(game.current(state)[0]['uid'], '2')
        self.assertEqual(game.public_game(state, balances, 2, {}, seats)['dealer'], ['10H', None])
        game.action(state, balances, seats, '2', 'stand')
        self.assertEqual(state['phase'], 'result')

    def test_natural_does_not_skip_another_players_decision(self):
        state, balances, seats = self.deal(['AS', '9S', '10H', 'KD', '7D', 'AC'], 2)
        self.assertEqual(state['phase'], 'turn')
        self.assertEqual(game.current(state)[0]['uid'], '2')
        game.action(state, balances, seats, '2', 'stand')
        self.assertEqual(balances, {'1': 10000, '2': 9500})

    def test_rule_is_latched_for_the_dealt_round(self):
        state, balances, seats = self.deal(['9S', '10H', '7D', 'AC'])
        state['table_rules']['dealer_peek'] = True
        self.assertFalse(game.dealer_peeks(state))
        self.assertEqual(state['phase'], 'turn')

    def test_doubled_addition_returns_when_bank_has_blackjack(self):
        state, balances, seats = self.deal(['5S', '10H', '6D', 'AC', '10C'])
        game.action(state, balances, seats, '1', 'double')
        self.assertEqual(state['phase'], 'result')
        self.assertEqual(state['players'][0]['hands'][0]['net'], -500)
        self.assertEqual(balances['1'], 9500)
        game.settle(state, balances)
        self.assertEqual(balances['1'], 9500, 'no duplicate refund')

    def test_split_addition_returns_and_original_is_lost_only_once(self):
        state, balances, seats = self.deal(['8S', '10H', '8D', 'AC', '2H', '3C'])
        game.action(state, balances, seats, '1', 'split')
        game.action(state, balances, seats, '1', 'stand')
        game.action(state, balances, seats, '1', 'stand')
        self.assertEqual(balances['1'], 9500)
        self.assertEqual([h['net'] for h in state['players'][0]['hands']], [-500, 0])

    def test_both_split_hands_doubled_still_lose_only_original(self):
        state, balances, seats = self.deal(['8S', '10H', '8D', 'AC', '2H', '3C', '7S', '6H'])
        game.action(state, balances, seats, '1', 'split')
        game.action(state, balances, seats, '1', 'double')
        game.action(state, balances, seats, '1', 'double')
        self.assertEqual(balances['1'], 9500)
        self.assertEqual([h['bet'] for h in state['players'][0]['hands']], [1000, 1000])
        self.assertEqual(sum(h['net'] for h in state['players'][0]['hands']), -500)

    def test_doubled_bust_does_not_consume_the_added_wager_against_blackjack(self):
        state, balances, seats = self.deal(['9S', '10H', '7D', 'AC', '10C'])
        game.action(state, balances, seats, '1', 'double')
        self.assertEqual(state['players'][0]['hands'][0]['status'], 'bust')
        self.assertEqual(balances['1'], 9500)

    def test_surrender_loses_original_if_bank_has_blackjack(self):
        state, balances, seats = self.deal(['9S', '10H', '7D', 'AC'])
        game.action(state, balances, seats, '1', 'surrender')
        self.assertEqual(balances['1'], 9500)
        self.assertEqual(state['players'][0]['hands'][0]['net'], -500)

    def test_surrender_returns_half_when_bank_has_no_blackjack(self):
        state, balances, seats = self.deal(['9S', '10H', '7D', '7C'])
        game.action(state, balances, seats, '1', 'surrender')
        self.assertEqual(balances['1'], 9750)

    def test_insurance_pays_only_after_player_decision(self):
        state, balances, seats = self.deal(['9S', 'AH', '7D', 'KC'])
        game.action(state, balances, seats, '1', 'insurance')
        self.assertEqual(state['phase'], 'turn')
        self.assertEqual(balances['1'], 9250)
        game.action(state, balances, seats, '1', 'stand')
        self.assertEqual(balances['1'], 10000)
        self.assertEqual(state['players'][0]['insurance_net'], 500)

    def test_insurance_and_surrender_are_settled_separately(self):
        state, balances, seats = self.deal(['9S', 'AH', '7D', 'KC'])
        game.action(state, balances, seats, '1', 'insurance')
        game.action(state, balances, seats, '1', 'surrender')
        self.assertEqual(balances['1'], 10000)
        self.assertEqual(state['players'][0]['hands'][0]['net'], -500)

    def test_leaving_still_forfeits_all_placed_wagers(self):
        state, balances, seats = self.deal(['5S', '9S', '10H', '6D', '7D', 'AC', '10C'], 2)
        game.action(state, balances, seats, '1', 'double')
        game.leave_round(state, balances, '1')
        game.action(state, balances, seats, '2', 'stand')
        self.assertEqual(balances, {'1': 9000, '2': 9500})

    def test_public_rule_for_existing_round_does_not_follow_new_table_setting(self):
        state = game.initial_state()
        state.update(phase='turn', dealer=['8H', '10S'])
        state['table_rules'] = dict(dealer_peek=False)
        view = game.public_game(state, {}, 1, {}, {})
        self.assertTrue(view['dealer_peek'])
        self.assertFalse(view['next_dealer_peek'])


if __name__ == '__main__':
    unittest.main()
