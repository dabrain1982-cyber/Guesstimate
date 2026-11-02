import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from conquest_turns import apply_action, hydrate, next_owner, public_game
from conquest_victory import check_victory, mission_complete, COLOR_SEATS, CONTINENT_MISSIONS


class VictoryTests(unittest.TestCase):
    def setUp(self):
        self.world = json.loads((Path(__file__).parents[1] / 'static/conquest/world.json').read_text(encoding='utf8'))
        self.keys = [row['id'] for row in self.world['territories']]
        self.state = hydrate({
            'phase': 'attack', 'round': 1, 'turn_number': 1, 'current_member_id': 1,
            'opening_rolls': [], 'victory_mode': 'missions', 'missions': {},
            'participants': [{'id': str(i), 'name': f'Spieler {i}'} for i in range(1, 7)],
            'hands': {str(i): [] for i in range(1, 7)},
            'territories': {key: {'owner': index % 6 + 1, 'armies': 1} for index, key in enumerate(self.keys)},
        }, self.world, [])

    def act(self, action, **fields):
        return apply_action(self.state, self.world, action, fields, 1, True)

    def own(self, keys, owner=1, armies=1):
        for key in keys:
            self.state['territories'][key] = {'owner': owner, 'armies': armies}

    def split(self, count, armies=1):
        self.own(self.keys, 2)
        self.own(self.keys[:count], 1, armies)

    def test_all_existing_missions_have_an_explicit_check(self):
        self.assertEqual({row['id'] for row in self.world['missions']},
                         set(CONTINENT_MISSIONS) | set(COLOR_SEATS) | {'mission-18-doppelt', 'mission-24-laender'})

    def test_continent_missions_require_every_territory_in_both_continents(self):
        for mission, continents in CONTINENT_MISSIONS.items():
            with self.subTest(mission=mission):
                self.own(self.keys, 2)
                needed = [row['id'] for row in self.world['territories'] if row['continent'] in continents]
                self.own(needed)
                self.assertTrue(mission_complete(self.state, self.world, '1', mission))
                for missing in (needed[0], needed[-1]):
                    self.own([missing], 2)
                    self.assertFalse(mission_complete(self.state, self.world, '1', mission))
                    self.own([missing])

    def test_24_territories_boundary(self):
        self.split(23)
        self.assertFalse(mission_complete(self.state, self.world, '1', 'mission-24-laender'))
        self.own([self.keys[23]])
        self.assertTrue(mission_complete(self.state, self.world, '1', 'mission-24-laender'))

    def test_18_double_territories_counts_only_sufficient_garrisons(self):
        self.split(22)
        self.own(self.keys[:17], armies=2)
        self.assertFalse(mission_complete(self.state, self.world, '1', 'mission-18-doppelt'))
        self.state.update(phase='reinforce', remaining=1, missions={'1': 'mission-18-doppelt'})
        self.act('place', to=self.keys[17], count=1)
        self.assertEqual(self.state['winner']['member_id'], '1')
        self.assertEqual(self.state['phase'], 'completed')

    def test_fortification_can_complete_18_double_territories(self):
        self.split(18, armies=2)
        self.state['territories']['alaska'] = {'owner': 1, 'armies': 3}
        self.state['territories']['alberta'] = {'owner': 1, 'armies': 1}
        # Exactly 18 owned territories, with Alaska and Alberta included.
        own = ['alaska', 'alberta'] + [key for key in self.keys if key not in ('alaska', 'alberta')][:16]
        self.own(self.keys, 2); self.own(own, armies=2)
        self.state['territories']['alaska']['armies'] = 3
        self.state['territories']['alberta']['armies'] = 1
        self.state.update(phase='fortify', missions={'1': 'mission-18-doppelt'})
        self.act('fortify', **{'from': 'alaska', 'to': 'alberta', 'count': 1})
        self.assertEqual(self.state['winner']['member_id'], '1')

    def test_card_territory_bonus_can_complete_mission(self):
        self.split(18, armies=2)
        cards = [key for key, symbol in self.world['cardSymbols'].items() if symbol == 'infantry'][:3]
        self.own([cards[0]], armies=1)
        # Restrict the qualifying countries to 17 until the bank bonus is applied.
        doubled = [key for key, row in self.state['territories'].items() if row['owner'] == 1 and row['armies'] >= 2]
        for key in doubled[17:]: self.state['territories'][key]['armies'] = 1
        self.state.update(phase='reinforce', placement_started=False, hands={'1': cards},
                          missions={'1': 'mission-18-doppelt'})
        self.assertFalse(mission_complete(self.state, self.world, '1', 'mission-18-doppelt'))
        self.act('trade', cards=json.dumps(cards), bonus_territory=cards[0])
        self.assertEqual(self.state['winner']['member_id'], '1')

    def test_all_colour_missions_bind_to_original_seats_and_self_means_24(self):
        for mission, seat in COLOR_SEATS.items():
            with self.subTest(mission=mission):
                target = str(seat + 1)
                self.own(self.keys, 1 if target != '1' else 2)
                owner = '1' if target != '1' else '2'
                self.assertTrue(mission_complete(self.state, self.world, owner, mission))
                self.own([self.keys[-1]], seat + 1)
                self.assertFalse(mission_complete(self.state, self.world, owner, mission))
                self.own(self.keys, 6 if target != '6' else 5)
                self.own(self.keys[:23], seat + 1)
                self.assertFalse(mission_complete(self.state, self.world, target, mission))
                self.own([self.keys[23]], seat + 1)
                self.assertTrue(mission_complete(self.state, self.world, target, mission))

    def test_absent_colour_and_unknown_mission_never_complete(self):
        self.state['participants'] = self.state['participants'][:3]
        self.assertFalse(mission_complete(self.state, self.world, '1', 'mission-orange'))
        self.assertFalse(mission_complete(self.state, self.world, '1', 'mission-unknown'))

    def prepare_capture(self):
        self.own(self.keys, 1)
        self.state['territories']['alaska'] = {'owner': 1, 'armies': 4}
        self.state['territories']['alberta'] = {'owner': 2, 'armies': 1}
        self.state.update(victory_mode='world', remaining=0)

    def test_world_victory_waits_for_mandatory_occupation_and_blocks_further_actions(self):
        self.prepare_capture()
        with patch('conquest_turns.secrets.randbelow', side_effect=[5, 0]):
            self.act('attack', **{'from': 'alaska', 'to': 'alberta', 'dice': 1})
        self.assertIsNone(self.state['winner'])
        self.assertIsNotNone(self.state['pending_conquest'])
        self.act('occupy', count=1)
        winner = copy.deepcopy(self.state['winner'])
        self.assertEqual(winner['member_id'], '1')
        self.assertEqual(self.state['phase'], 'completed')
        self.assertTrue(all(row['armies'] >= 1 for row in self.state['territories'].values()))
        for action in ('place', 'trade', 'attack', 'occupy', 'defend', 'fortify', 'advance', 'pass'):
            with self.subTest(action=action), self.assertRaises(ValueError): self.act(action)
        self.assertEqual(self.state['winner'], winner)
        self.assertEqual(self.state['hands']['1'], [])
        self.assertIsNone(public_game(self.state, self.world, 1, True)['next_owner_id'])

    def test_41_territories_do_not_win_world_game(self):
        self.prepare_capture()
        self.assertIsNone(check_victory(self.state, self.world))

    def test_duel_win_does_not_require_neutral_territories(self):
        self.prepare_capture()
        self.state['participants'] = self.state['participants'][:2]
        self.own([self.keys[-1]], 'neutral', 3)
        with patch('conquest_turns.secrets.randbelow', side_effect=[5, 0]):
            self.act('attack', **{'from': 'alaska', 'to': 'alberta', 'dice': 1})
        self.act('occupy', count=1)
        self.assertEqual(self.state['winner']['member_id'], '1')
        self.assertIn('Neutrale', self.state['winner']['reason'])
        self.assertEqual(self.state['territories'][self.keys[-1]]['owner'], 'neutral')

    def test_another_players_attack_can_complete_a_living_players_colour_mission(self):
        self.own(self.keys, 2)
        self.own(['alaska'], 1, 4)
        self.own(['alberta'], 3)
        self.state['missions'] = {'1': 'mission-asien-afrika', '2': 'mission-blau', '3': 'mission-gelb'}
        self.state['hands'] = {'1': ['japan'], '2': ['peru'], '3': ['brasilien']}
        with patch('conquest_turns.secrets.randbelow', side_effect=[5, 0]):
            self.act('attack', **{'from': 'alaska', 'to': 'alberta', 'dice': 1})
        self.assertIsNone(self.state['winner'])
        self.act('occupy', count=1)
        self.assertEqual(self.state['winner']['member_id'], '2')
        public = public_game(self.state, self.world, 1, False)
        self.assertEqual(public['winner']['mission']['id'], 'mission-blau')
        self.assertEqual(public['own_mission'], 'mission-asien-afrika')
        self.assertEqual([card['id'] for card in public['inventory']['territory_cards']], ['japan', 'brasilien'])
        self.assertNotIn('missions', public)
        self.assertNotIn('hands', public)
        self.assertFalse(public['can_act'])
        self.assertTrue(next(row for row in public['armies'] if row['id'] == '3')['eliminated'])

    def test_eliminated_mission_holder_cannot_win(self):
        self.own(self.keys, 2)
        self.own([self.keys[0]], 4)
        self.state.update(current_member_id=2, missions={'1': 'mission-blau'})
        self.assertIsNone(check_victory(self.state, self.world))

    def test_world_mode_ignores_secret_mission_assignments(self):
        self.split(24)
        self.state.update(victory_mode='world', missions={'1': 'mission-24-laender'})
        self.assertIsNone(check_victory(self.state, self.world))

    def test_handoff_keeps_join_order_and_skips_eliminated_players(self):
        self.state['participants'] = self.state['participants'][:3]
        self.own(self.keys, 1); self.own([self.keys[-1]], 3)
        self.state.update(phase='ended', victory_mode='world')
        self.assertEqual(next_owner(self.state), '3')
        self.act('pass')
        self.assertEqual(self.state['current_member_id'], '3')
        self.state['phase'] = 'ended'; self.act('pass')
        self.assertEqual(self.state['current_member_id'], '1')
        self.assertEqual([row['id'] for row in self.state['participants']], ['1', '2', '3'])

    def test_hydrating_legacy_save_keeps_mission_hands_board_and_turn(self):
        self.state['missions'] = {'1': 'mission-gelb'}
        self.state['hands'] = {'1': ['japan']}
        del self.state['winner']; del self.state['victory_mode']
        before = copy.deepcopy(self.state)
        hydrate(self.state, self.world, [], 'missions')
        for key, value in before.items(): self.assertEqual(self.state[key], value, key)
        self.assertIsNone(self.state['winner'])
        self.assertEqual(self.state['victory_mode'], 'missions')



    def test_color_mission_tracks_chosen_color_instead_of_seat(self):
        self.state['participants'][1]['color_index']=5
        self.state['participants'][5]['color_index']=1
        self.own(self.keys,1);self.own(self.keys[:1],6)
        self.assertTrue(mission_complete(self.state,self.world,'1','mission-orange'))
        self.own(self.keys[:1],2)
        self.assertFalse(mission_complete(self.state,self.world,'1','mission-orange'))


if __name__ == '__main__':
    unittest.main()
