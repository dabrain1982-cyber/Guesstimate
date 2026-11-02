import copy
import json
from pathlib import Path
import unittest

from conquest import INITIAL_ARMIES, _prepare_automatic_state
from conquest_turns import apply_action, hydrate, reinforcement, public_game


class InitialPlacementTests(unittest.TestCase):
    def setUp(self):
        self.world = json.loads((Path(__file__).parents[1] / 'static/conquest/world.json').read_text(encoding='utf8'))

    def game(self, count=3):
        members = [{'id': i, 'display_name': f'Person {i}'} for i in range(1, count + 1)]
        return hydrate(_prepare_automatic_state(members, 'world'), self.world, members)

    def place(self, state):
        game = public_game(state, self.world, 1, True)
        target = next(key for key, row in state['territories'].items() if str(row['owner']) == game['setup']['target_owner'])
        actor = str(state['current_member_id'])
        before = state['territories'][target]['armies']
        apply_action(state, self.world, 'place', {'to': target, 'count': 1}, 1, True)
        self.assertEqual(state['territories'][target]['armies'], before + 1)
        return actor, target

    def test_all_player_counts_start_with_one_army_per_assigned_territory(self):
        for count in range(2, 7):
            with self.subTest(count=count):
                state = self.game(count)
                self.assertEqual(state['phase'], 'setup')
                self.assertEqual(len(state['territories']), 42)
                self.assertTrue(all(row['armies'] == 1 for row in state['territories'].values()))
                for player in state['participants']:
                    owner = player['id']
                    owned = sum(str(row['owner']) == owner for row in state['territories'].values())
                    self.assertEqual(owned + state['setup']['remaining'][owner], INITIAL_ARMIES[count])
                self.assertEqual(state['reinforcement']['total'], 0)
                self.assertFalse(any(state['hands'].values()))

    def test_regular_setup_rotates_after_each_army_and_leaves_choices_unrestricted(self):
        state = self.game()
        order = [row['id'] for row in state['participants']]
        index = order.index(str(state['current_member_id']))
        targets = {}
        for offset in range(9):
            actor, target = self.place(state)
            self.assertEqual(actor, order[(index + offset) % 3])
            if actor in targets: self.assertEqual(target, targets[actor])
            targets[actor] = target
        self.assertTrue(all(state['territories'][key]['armies'] == 4 for key in targets.values()))
        self.assertEqual(state['turn_number'], 1)

    def test_invalid_placement_and_other_actions_leave_setup_unchanged(self):
        state = self.game()
        actor = str(state['current_member_id'])
        own = next(key for key, row in state['territories'].items() if str(row['owner']) == actor)
        foreign = next(key for key, row in state['territories'].items() if str(row['owner']) != actor)
        cases = [('place', {'to': own, 'count': n}) for n in (0, 2, -1, 'bad')]
        cases += [('place', {'to': foreign, 'count': 1}), ('place', {'to': 'missing', 'count': 1})]
        cases += [(action, {}) for action in ('attack', 'trade', 'advance', 'pass', 'fortify', 'occupy')]
        for action, fields in cases:
            with self.subTest(action=action, fields=fields):
                working = copy.deepcopy(state)
                with self.assertRaises(ValueError): apply_action(working, self.world, action, fields, int(actor), False)
                self.assertEqual(working, state)
        other = next(row['id'] for row in state['participants'] if row['id'] != actor)
        with self.assertRaises(PermissionError):
            apply_action(state, self.world, 'place', {'to': own, 'count': 1}, int(other), False)

    def test_full_setup_for_two_through_six_players_preserves_all_initial_army_totals(self):
        for count in range(2, 7):
            with self.subTest(count=count):
                state = self.game(count)
                first = str(state['current_member_id'])
                remaining = sum(state['setup']['remaining'].values()) + state['setup']['neutral_remaining']
                original_owners = {key: row['owner'] for key, row in state['territories'].items()}
                for _ in range(remaining):
                    self.assertEqual(state['phase'], 'setup')
                    self.place(state)
                self.assertEqual(state['phase'], 'reinforce')
                self.assertTrue(state['setup']['complete'])
                self.assertEqual(str(state['current_member_id']), first)
                for owner in {str(row['owner']) for row in state['territories'].values()}:
                    self.assertEqual(sum(row['armies'] for row in state['territories'].values() if str(row['owner']) == owner), INITIAL_ARMIES[count])
                self.assertEqual({key: row['owner'] for key, row in state['territories'].items()}, original_owners)
                self.assertEqual(state['remaining'], reinforcement(state, self.world)['total'])
                self.assertIsNone(public_game(state, self.world, 1, True)['setup'])
                self.assertEqual(state['turn_number'], 1)
                self.assertFalse(state['placement_started'])

    def test_duel_places_two_own_then_one_neutral_before_switching(self):
        state = self.game(2)
        first = str(state['current_member_id'])
        self.place(state)
        self.assertEqual(str(state['current_member_id']), first)
        self.assertEqual(public_game(state, self.world, 1, True)['setup']['target_owner'], first)
        self.place(state)
        self.assertEqual(str(state['current_member_id']), first)
        self.assertEqual(public_game(state, self.world, 1, True)['setup']['target_owner'], 'neutral')
        own = next(key for key, row in state['territories'].items() if str(row['owner']) == first)
        with self.assertRaises(ValueError): apply_action(state, self.world, 'place', {'to': own, 'count': 1}, 1, True)
        self.place(state)
        self.assertNotEqual(str(state['current_member_id']), first)
        self.assertEqual(state['setup']['neutral_remaining'], 25)

    def test_setup_never_awards_an_early_mission_win(self):
        state = self.game(3)
        state.update(victory_mode='missions', missions={str(state['current_member_id']): 'mission-24-laender'})
        actor = str(state['current_member_id'])
        keys = list(state['territories'])
        for key in keys[:24]: state['territories'][key]['owner'] = actor
        self.place(state)
        self.assertIsNone(state['winner'])
        self.assertEqual(state['phase'], 'setup')

    def test_existing_playing_save_is_not_restarted_or_redistributed(self):
        state = self.game()
        state.pop('setup')
        state.update(phase='attack', remaining=0, hands={'1': ['japan']}, conquered_count=2, turn_number=4)
        before = copy.deepcopy(state)
        hydrate(state, self.world, [])
        self.assertEqual(state, before)
        self.assertIsNone(public_game(state, self.world, 1, True)['setup'])


if __name__ == '__main__':
    unittest.main()
