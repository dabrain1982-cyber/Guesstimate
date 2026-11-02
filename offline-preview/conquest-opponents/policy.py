"""Small legal-move selector for disposable Conquest preview players."""
from itertools import combinations
import json
import random

from conquest_cards import valid_set


def choose_action(game, world, human_id, attacks=0, rng=None):
    """Return (member, action, fields); never submit decisions for the human."""
    rng = rng or random
    human = str(human_id)
    if game.get('winner') or game['phase'] == 'completed' or game.get('waiting_for_member'):
        return None
    board = game['territories']
    request = game.get('battle_request')
    if request:
        defender = str(request['defender'])
        return None if defender == human else (
            defender, 'defend', {'dice': min(2, board[request['to']]['armies'])})
    actor = str(game['current_member_id'])
    if actor == human:
        return None
    pending = game.get('pending_conquest')
    if pending:
        return actor, 'occupy', {'count': pending['min']}
    phase = game['phase']
    own = [key for key, row in board.items() if str(row['owner']) == actor]
    if phase == 'setup':
        target = str(game['setup']['target_owner'])
        choices = [key for key, row in board.items() if str(row['owner']) == target]
        # Spread initial armies rather than building one giant stack.
        weakest = min(board[key]['armies'] for key in choices)
        return actor, 'place', {'to': rng.choice([key for key in choices if board[key]['armies'] == weakest]), 'count': 1}
    if phase == 'reinforce':
        if game['trade']['mandatory']:
            cards = game['inventory']['territory_cards']
            selected = next((rows for rows in combinations(cards, 3) if valid_set([row['symbol'] for row in rows])), None)
            if not selected:
                raise ValueError('Kein regelkonformer Pflichtkartensatz gefunden.')
            fields = {'cards': json.dumps([row['id'] for row in selected])}
            return actor, 'trade', fields
        if game['remaining']:
            return actor, 'place', {'to': rng.choice(own), 'count': game['remaining']}
        return actor, 'advance', {}
    neighbors = {row['id']: row['neighbors'] for row in world['territories']}
    if phase == 'attack':
        pairs = [(source, target) for source in own if board[source]['armies'] >= 2
                 for target in neighbors[source] if str(board[target]['owner']) != actor]
        if pairs and attacks < 2:
            source, target = rng.choice(pairs)
            return actor, 'attack', {'from': source, 'to': target, 'dice': min(3, board[source]['armies'] - 1)}
        return actor, 'advance', {}
    if phase == 'fortify':
        pairs = [(source, target) for source in own if board[source]['armies'] >= 2
                 for target in neighbors[source] if str(board[target]['owner']) == actor]
        if pairs and not game['fortified']:
            source, target = rng.choice(pairs)
            return actor, 'fortify', {'from': source, 'to': target, 'count': 1}
        return actor, 'advance', {}
    if phase == 'ended':
        return actor, 'pass', {}
    raise ValueError(f'Unbekannte Zugphase: {phase}')
