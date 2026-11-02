"""Preview opponents must use legal actions and leave human decisions untouched."""
import copy
import importlib.util
import json
from pathlib import Path
import random
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / '.deps'), str(ROOT)]
from conquest import _prepare_automatic_state
from conquest_turns import apply_action, hydrate, public_game

SPEC = importlib.util.spec_from_file_location('conquest_opponent_policy', ROOT / 'offline-preview/conquest-opponents/policy.py')
policy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(policy)
WORLD = json.loads((ROOT / 'static/conquest/world.json').read_text(encoding='utf-8'))
MEMBERS = [dict(id=i, display_name=f'Player {i}') for i in range(6, 10)]


def new_state():
    with patch('conquest._first_player', return_value=(6, [])):
        return hydrate(_prepare_automatic_state(MEMBERS, 'world'), WORLD, MEMBERS, 'world')


def view(state):
    request = state.get('battle_request')
    member = request['defender'] if request else state['current_member_id']
    return public_game(state, WORLD, member, False)


class ConquestOpponentTests(unittest.TestCase):
    def test_human_setup_is_never_placed(self):
        state = new_state()
        before = copy.deepcopy(state)
        self.assertIsNone(policy.choose_action(view(state), WORLD, 6))
        self.assertEqual(state, before)

    def test_bots_place_exactly_one_own_initial_unit(self):
        state = new_state()
        member, action, fields = policy.choose_action(view(state), WORLD, 'other')
        self.assertEqual(action, 'place')
        self.assertEqual(fields['count'], 1)
        self.assertEqual(str(state['territories'][fields['to']]['owner']), member)
        apply_action(state, WORLD, action, fields, int(member), False)
        self.assertEqual(state['setup']['placed'], 1)

    def test_human_defense_waits_but_opponent_defense_is_automatic(self):
        state = new_state()
        state['phase'] = 'attack'
        board = state['territories']
        source = next(key for key, row in board.items() if str(row['owner']) == '6')
        target = next(key for key, row in board.items() if str(row['owner']) == '7')
        state['battle_request'] = {'from': source, 'to': target, 'defender': 7, 'dice': 1}
        member, action, fields = policy.choose_action(view(state), WORLD, 6)
        self.assertEqual((member, action, fields['dice']), ('7', 'defend', 1))
        state['battle_request'].update(to=source, defender=6)
        self.assertIsNone(policy.choose_action(view(state), WORLD, 6))

    def test_required_card_trade_is_accepted_by_game_rules(self):
        state = new_state()
        state.update(phase='reinforce', placement_started=False)
        hand = state['card_deck'][:5]
        state['hands']['6'] = hand
        state['card_deck'] = state['card_deck'][5:]
        member, action, fields = policy.choose_action(view(state), WORLD, 'other')
        self.assertEqual(action, 'trade')
        apply_action(state, WORLD, action, fields, int(member), False)
        self.assertEqual(len(state['hands']['6']), 2)
        self.assertEqual(state['trade_count'], 1)

    def test_occupation_obeys_mandatory_minimum(self):
        state = new_state()
        state.update(phase='attack', pending_conquest={'from':'alaska', 'to':'alberta', 'min':3, 'max':5, 'defeated_owner':7})
        state['territories']['alaska'] = {'owner':6,'armies':6}
        state['territories']['alberta'] = {'owner':6,'armies':0}
        member, action, fields = policy.choose_action(view(state), WORLD, 'other')
        self.assertEqual((action, fields['count']), ('occupy', 3))
        apply_action(state, WORLD, action, fields, int(member), False)
        self.assertEqual(state['territories']['alaska']['armies'], 3)
        self.assertEqual(state['territories']['alberta']['armies'], 3)

    def test_complete_start_and_multiple_rounds_validate_every_move(self):
        state = new_state()
        counters = {}
        actions = set()
        choices = random.Random(42)
        dice = random.Random(53)
        with patch('conquest_turns.secrets.randbelow', side_effect=lambda maximum: dice.randrange(maximum)):
            for _ in range(350):
                game = view(state)
                key = (state['turn_number'], str(state['current_member_id']))
                # A manual actor is only simulated inside this isolated rule test.
                if str(game.get('battle_request', {}).get('defender', game['current_member_id']) if game.get('battle_request') else game['current_member_id']) == '6':
                    self.assertIsNone(policy.choose_action(game, WORLD, 6))
                decision = policy.choose_action(game, WORLD, 'no-human-in-this-test', counters.get(key, 0), choices)
                if decision is None:
                    break
                member, action, fields = decision
                if action == 'attack':
                    counters[key] = counters.get(key, 0) + 1
                    self.assertLessEqual(counters[key], 2)
                apply_action(state, WORLD, action, fields, int(member), False)
                actions.add(action)
                self.assertTrue(all(row['armies'] >= 1 or state.get('pending_conquest') and state['pending_conquest']['to'] == name
                                    for name, row in state['territories'].items()))
        self.assertTrue(state['setup']['complete'])
        self.assertGreater(state['turn_number'], 8)
        self.assertTrue({'place','advance','attack','occupy','fortify','pass'} <= actions, actions)

    def test_finished_game_and_reserved_absent_player_are_not_played(self):
        game = view(new_state())
        game['winner'] = {'name':'Player 6'}
        self.assertIsNone(policy.choose_action(game, WORLD, 'other'))
        game['winner'] = None
        game['waiting_for_member'] = 'Player 7'
        self.assertIsNone(policy.choose_action(game, WORLD, 'other'))


    def test_new_lobby_member_ids_leave_host_manual_and_play_only_other_seats(self):
        members=[dict(id=i,display_name=f'Player {i}') for i in range(17,21)]
        with patch('conquest._first_player',return_value=(17,[])):
            state=hydrate(_prepare_automatic_state(members,'world'),WORLD,members,'world')
        self.assertIsNone(policy.choose_action(public_game(state,WORLD,17,False),WORLD,17))
        target=next(key for key,row in state['territories'].items() if str(row['owner'])=='17')
        # Only this isolated unit test supplies the manual host action.
        apply_action(state,WORLD,'place',{'to':target,'count':1},17,False)
        self.assertEqual(str(state['current_member_id']),'18')
        decision=policy.choose_action(public_game(state,WORLD,18,False),WORLD,17)
        member,action,fields=decision
        self.assertEqual(member,'18')
        apply_action(state,WORLD,action,fields,18,False)
        self.assertEqual(str(state['current_member_id']),'19')


if __name__ == '__main__':
    unittest.main()
