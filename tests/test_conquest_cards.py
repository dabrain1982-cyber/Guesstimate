import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from conquest_cards import catalog, exchange_value, valid_set, trade_info
from conquest_turns import apply_action, hydrate, public_game


class CardExchangeTests(unittest.TestCase):
    def setUp(self):
        self.world = json.loads((Path(__file__).parents[1] / 'static/conquest/world.json').read_text(encoding='utf-8'))
        self.cards = catalog(self.world)
        self.groups = {symbol: [key for key, card in self.cards.items() if card['symbol'] == symbol]
                       for symbol in ('infantry', 'cavalry', 'artillery', 'wild')}
        self.state = hydrate({
            'phase': 'reinforce', 'round': 1, 'current_member_id': 1, 'opening_rolls': [],
            'participants': [{'id': str(i), 'name': str(i)} for i in (1, 2, 3)],
            'territories': {row['id']: {'owner': index % 3 + 1, 'armies': 5}
                            for index, row in enumerate(self.world['territories'])},
            'hands': {'1': [], '2': [], '3': []},
        }, self.world, [])

    def seed(self, own, other=()):
        self.state['hands'] = {'1': list(own), '2': list(other), '3': []}
        self.state['card_deck'] = [key for key in self.cards if key not in own and key not in other]
        self.state['card_discard'] = []

    def act(self, action, member=1, **fields):
        working = copy.deepcopy(self.state)
        result = apply_action(working, self.world, action, fields, member, False)
        self.state = working
        return result

    def trade(self, keys, bonus='', member=1):
        return self.act('trade', member=member, cards=json.dumps(keys), bonus_territory=bonus)

    def test_catalog_has_42_stable_country_cards_and_two_distinct_jokers(self):
        self.assertEqual(len(self.cards), 44)
        self.assertEqual([len(self.groups[key]) for key in ('infantry', 'cavalry', 'artillery', 'wild')], [14, 14, 14, 2])
        self.assertEqual(self.cards['japan']['symbol'], 'artillery')
        self.assertEqual(self.cards['joker-1']['type'], 'Joker')

    def test_same_different_and_joker_sets_and_invalid_mix(self):
        for symbol in ('infantry', 'cavalry', 'artillery'):
            self.assertTrue(valid_set([symbol] * 3))
            self.assertTrue(valid_set([symbol, symbol, 'wild']))
            self.assertTrue(valid_set([symbol, 'wild', 'wild']))
        self.assertTrue(valid_set(['infantry', 'cavalry', 'artillery']))
        self.assertTrue(valid_set(['infantry', 'cavalry', 'wild']))
        self.assertFalse(valid_set(['infantry', 'infantry', 'cavalry']))
        self.assertFalse(valid_set(['infantry', 'invalid', 'wild']))

    def test_trade_offer_requires_an_actual_set_and_closes_after_first_placement(self):
        self.seed(self.groups['infantry'][:2] + self.groups['cavalry'][:1])
        self.assertFalse(trade_info(self.state, self.world)['can_trade'])
        self.seed(self.groups['infantry'][:3])
        self.assertTrue(trade_info(self.state, self.world)['can_trade'])
        own = next(key for key, row in self.state['territories'].items() if str(row['owner']) == '1')
        self.act('place', to=own, count=1)
        self.assertFalse(trade_info(self.state, self.world)['can_trade'])

    def test_exchange_values_increase_globally_across_players(self):
        self.assertEqual([exchange_value(i) for i in range(10)], [4, 6, 8, 10, 12, 15, 20, 25, 30, 35])
        first = self.groups['infantry'][:3]
        second = self.groups['cavalry'][:3]
        self.seed(first, second)
        self.assertEqual(self.trade(first, first[0])['units'], 4)
        self.act('place', to=first[0], count=str(self.state['remaining']))
        for _ in range(3): self.act('advance')
        self.act('pass')
        self.assertEqual(self.trade(second, second[0], member=2)['units'], 6)
        self.assertEqual(self.state['trade_count'], 2)

    def test_trade_conserves_all_cards_and_only_removes_selected_own_cards(self):
        selected = self.groups['infantry'][:3]
        self.seed(selected + ['joker-1'], self.groups['cavalry'][:3])
        self.trade(selected, selected[0])
        self.assertEqual(self.state['hands']['1'], ['joker-1'])
        self.assertEqual(self.state['hands']['2'], self.groups['cavalry'][:3])
        self.assertEqual(self.state['card_discard'], selected)
        all_cards = self.state['card_deck'] + self.state['card_discard'] + sum(self.state['hands'].values(), [])
        self.assertEqual(len(all_cards), 44)
        self.assertEqual(len(set(all_cards)), 44)

    def test_duplicate_foreign_invalid_and_malformed_selections_leave_state_unchanged(self):
        own = self.groups['infantry'][:3]
        self.seed(own)
        before = copy.deepcopy(self.state)
        for selected in ([own[0]] * 3, own[:2], own[:2] + ['joker-1'], 'alaska', [None, 2, 3]):
            with self.assertRaises(ValueError): self.trade(selected)
            self.assertEqual(self.state, before)
        with self.assertRaises(ValueError): self.act('trade', cards='[')
        self.assertEqual(self.state, before)

    def test_mixed_set_with_joker_earns_same_payout(self):
        selected = [self.groups['infantry'][0], self.groups['cavalry'][0], 'joker-1']
        self.seed(selected)
        result = self.trade(selected)
        self.assertEqual((result['units'], result['bonus']), (4, 2))
        self.assertIn('joker-1', self.state['card_discard'])

    def test_only_start_of_own_turn_before_first_placement_allows_optional_trade(self):
        selected = self.groups['infantry'][:3]
        self.seed(selected)
        with self.assertRaises(PermissionError): self.trade(selected, member=2)
        self.act('place', to=selected[0], count='1')
        with self.assertRaises(ValueError): self.trade(selected, selected[0])
        self.state.update(phase='attack', placement_started=False)
        with self.assertRaises(ValueError): self.trade(selected, selected[0])
        self.assertEqual(self.state['trade_count'], 0)

    def test_five_cards_require_trade_before_placing_or_advancing(self):
        own = self.groups['infantry'][:5]
        self.seed(own)
        self.assertTrue(public_game(self.state, self.world, 1, False)['trade']['mandatory'])
        with self.assertRaises(ValueError): self.act('place', to=own[0], count='1')
        with self.assertRaises(ValueError): self.act('advance')
        self.trade(own[:3], own[0])
        self.assertFalse(public_game(self.state, self.world, 1, False)['trade']['mandatory'])
        self.act('place', to=own[0], count='1')

    def test_each_owned_country_in_a_traded_set_automatically_receives_two(self):
        original=copy.deepcopy(self.state)
        selected=self.groups['infantry'][:3]
        for count in range(4):
            with self.subTest(owned=count):
                self.state=copy.deepcopy(original);self.seed(selected)
                for index,key in enumerate(selected):self.state['territories'][key]['owner']=1 if index<count else 2
                before={key:row['armies'] for key,row in self.state['territories'].items()}
                reserve=self.state['remaining']
                result=self.trade(selected)
                self.assertEqual(result['bonus'],2*count)
                self.assertEqual(result['bonus_territories'],selected[:count])
                self.assertEqual(self.state['remaining'],reserve+4)
                for key,row in self.state['territories'].items():
                    self.assertEqual(row['armies'],before[key]+(2 if key in selected[:count] else 0))

    def test_owned_country_bonuses_apply_to_each_trade_even_with_an_old_turn_cap_flag(self):
        own=self.groups['infantry'][:6];self.seed(own)
        for key in own:self.state['territories'][key]['owner']=1
        self.state['territory_bonus_received']=True
        before={key:row['armies'] for key,row in self.state['territories'].items()}
        self.assertEqual(self.trade(own[:3])['bonus'],6)
        self.assertEqual(self.trade(own[3:])['bonus'],6)
        self.assertEqual(self.state['remaining'],14)
        self.assertEqual(sum(row['armies'] for row in self.state['territories'].values())-sum(before.values()),12)

    def test_old_bonus_choice_cannot_redirect_or_suppress_the_automatic_payout(self):
        selected=self.groups['infantry'][:3];self.seed(selected)
        for key in selected:self.state['territories'][key]['owner']=1
        unrelated=self.groups['cavalry'][0];before=self.state['territories'][unrelated]['armies']
        result=self.trade(selected,unrelated)
        self.assertEqual(result['bonus_territories'],selected)
        self.assertEqual(result['bonus'],6)
        self.assertEqual(self.state['territories'][unrelated]['armies'],before)

    def test_joker_is_drawable_and_private_in_status(self):
        self.state.update(phase='fortify', conquered_count=1)
        with patch('conquest_turns.secrets.choice', return_value='joker-1'):
            self.act('advance')
        owner = public_game(self.state, self.world, 1, False)
        other = public_game(self.state, self.world, 2, False)
        self.assertEqual(owner['inventory']['territory_cards'][0]['symbol'], 'wild')
        self.assertEqual(other['inventory']['territory_cards'], [])
        self.assertIsNone(other['end_result']['card'])

    def test_empty_deck_reuses_discarded_cards(self):
        discard = self.groups['infantry'][:3]
        self.seed([], [key for key in self.cards if key not in discard])
        self.state.update(phase='fortify', conquered_count=1, card_deck=[], card_discard=discard.copy())
        self.act('advance')
        self.assertIn(self.state['hands']['1'][0], discard)
        self.assertEqual(len(self.state['card_deck']), 2)
        self.assertEqual(self.state['card_discard'], [])

    def prepare_elimination(self, own_count, other_count):
        cards = self.groups['infantry']
        self.seed(cards[:own_count], cards[own_count:own_count + other_count])
        for row in self.state['territories'].values(): row['owner'] = 3
        self.state['territories']['alaska'] = {'owner': 1, 'armies': 6}
        self.state['territories']['alberta'] = {'owner': 1, 'armies': 0}
        self.state.update(phase='attack', placement_started=True, remaining=0,
                          pending_conquest={'from': 'alaska', 'to': 'alberta', 'min': 1, 'max': 5, 'defeated_owner': 2})

    def test_elimination_with_six_cards_forces_trade_then_placement_before_attack(self):
        self.prepare_elimination(4, 2)
        self.act('occupy', count='1')
        self.assertEqual(self.state['phase'], 'reinforce')
        self.assertEqual(self.state['hands']['2'], [])
        self.assertEqual(len(self.state['hands']['1']), 6)
        with self.assertRaises(ValueError): self.act('advance')
        selected = self.state['hands']['1'][:3]
        self.trade(selected, 'alaska')
        self.assertFalse(public_game(self.state, self.world, 1, False)['trade']['can_trade'])
        with self.assertRaises(ValueError): self.trade(self.state['hands']['1'])
        self.act('place', to='alaska', count='4')
        self.act('advance')
        self.assertEqual(self.state['phase'], 'attack')
        self.assertEqual(len(self.state['hands']['1']), 3)

    def test_elimination_with_five_cards_waits_until_next_turn(self):
        self.prepare_elimination(3, 2)
        self.act('occupy', count='1')
        self.assertEqual(self.state['phase'], 'attack')
        self.assertEqual(len(self.state['hands']['1']), 5)
        with self.assertRaises(ValueError): self.trade(self.state['hands']['1'][:3])

    def test_large_inherited_hand_requires_multiple_sets_until_four_or_fewer(self):
        self.prepare_elimination(9, 3)
        self.act('occupy', count='1')
        for payout, expected in ((4, 9), (6, 6), (8, 3)):
            self.assertTrue(public_game(self.state, self.world, 1, False)['trade']['mandatory'])
            selected = self.state['hands']['1'][:3]
            result = self.trade(selected, 'alaska' if 'alaska' in selected else '')
            self.assertEqual(result['units'], payout)
            self.assertEqual(len(self.state['hands']['1']), expected)
        self.assertEqual(self.state['remaining'], 18)
        self.assertFalse(public_game(self.state, self.world, 1, False)['trade']['can_trade'])

    def test_old_game_gets_two_jokers_once_without_changing_existing_hands_or_board(self):
        self.seed(['japan'])
        self.state['card_deck'] = [key for key in self.state['card_deck'] if not key.startswith('joker-')]
        del self.state['card_rules_version']
        before = copy.deepcopy(self.state)
        hydrate(self.state, self.world, [])
        hydrate(self.state, self.world, [])
        self.assertEqual(self.state['territories'], before['territories'])
        self.assertEqual(self.state['hands'], before['hands'])
        self.assertEqual(self.state['remaining'], before['remaining'])
        self.assertEqual(self.state['card_deck'].count('joker-1'), 1)
        self.assertEqual(self.state['card_deck'].count('joker-2'), 1)


if __name__ == '__main__':
    unittest.main()
