"""Shared card metadata, increasing exchange values and automatic country bonuses."""
from __future__ import annotations

import json
from itertools import combinations

SYMBOL_LABELS = {'infantry': 'Infanterie', 'cavalry': 'Reiter', 'artillery': 'Geschütz', 'wild': 'Joker'}
JOKERS = ('joker-1', 'joker-2')


def catalog(world: dict) -> dict:
    names = {row['id']: row['name'] for row in world['territories']}
    names.update({'joker-1': 'Joker I', 'joker-2': 'Joker II'})
    return {key: {'id': key, 'name': names[key], 'symbol': symbol, 'type': SYMBOL_LABELS[symbol]}
            for key, symbol in world['cardSymbols'].items()}


def exchange_value(count: int) -> int:
    return [4, 6, 8, 10, 12, 15][count] if count < 6 else 15 + (count - 5) * 5


def valid_set(symbols: list[str]) -> bool:
    if len(symbols) != 3 or any(symbol not in SYMBOL_LABELS for symbol in symbols):
        return False
    normal = [symbol for symbol in symbols if symbol != 'wild']
    return len(set(normal)) == 1 or len(set(normal)) == len(normal)


def initialize_cards(state: dict, world: dict) -> None:
    state.setdefault('card_discard', [])
    state.setdefault('trade_count', 0)
    state.setdefault('trade_resume_phase', None)
    state.setdefault('placement_started', state['remaining'] < state['reinforcement']['total'])
    if state.get('card_rules_version') != 1:
        held = {key for hand in state['hands'].values() for key in hand}
        placed = held | set(state['card_deck']) | set(state['card_discard'])
        state['card_deck'].extend(key for key in JOKERS if key not in placed)
        state['card_rules_version'] = 1


def trade_info(state: dict, world: dict) -> dict:
    hand = state['hands'].get(str(state['current_member_id']), [])
    count = len(hand)
    symbols = world['cardSymbols']
    available = any(valid_set([symbols[key] for key in group])
                    for group in combinations(hand, 3) if all(key in symbols for key in group))
    elimination = state.get('trade_resume_phase') == 'attack'
    window = state['phase'] == 'reinforce' and not state['placement_started']
    return {'count': state['trade_count'], 'next_value': exchange_value(state['trade_count']),
            'can_trade': window and available and count >= (5 if elimination else 3),
            'mandatory': window and count >= 5,
            'territory_bonus_available': True,
            'elimination': elimination}


def exchange(state: dict, world: dict, fields) -> dict:
    info = trade_info(state, world)
    if not info['can_trade']:
        raise ValueError('Kartensätze kannst du nur zu Beginn deines Zugs vor dem Platzieren tauschen.')
    try:
        selected = json.loads(fields.get('cards', '[]'))
    except (ValueError, TypeError):
        raise ValueError('Wähle genau drei unterschiedliche eigene Karten.') from None
    if not isinstance(selected, list) or len(selected) != 3 or any(not isinstance(key, str) for key in selected) or len(set(selected)) != 3:
        raise ValueError('Wähle genau drei unterschiedliche eigene Karten.')
    owner = str(state['current_member_id'])
    hand = state['hands'].get(owner, [])
    cards = catalog(world)
    if any(key not in hand or key not in cards for key in selected):
        raise ValueError('Du kannst nur Karten aus deiner eigenen Hand eintauschen.')
    if not valid_set([cards[key]['symbol'] for key in selected]):
        raise ValueError('Ein Satz benötigt drei gleiche oder drei unterschiedliche Symbole. Joker ersetzen jedes Symbol.')
    eligible = [key for key in selected if key in state['territories']
                and str(state['territories'][key]['owner']) == owner]
    # Old clients may still send a bonus choice; ownership of every traded
    # country determines the automatic payout instead.
    value = info['next_value']
    state['hands'][owner] = [key for key in hand if key not in selected]
    state['card_discard'].extend(selected)
    state['trade_count'] += 1
    state['remaining'] += value
    state['reinforcement']['total'] += value
    state['reinforcement']['cards'] = state['reinforcement'].get('cards', 0) + value
    for territory in eligible:
        state['territories'][territory]['armies'] += 2
    return {'units': value, 'bonus': 2 * len(eligible), 'bonus_territories': eligible,
            'bonus_territory': eligible[0] if eligible else None,
            'trade_number': state['trade_count']}


def inherit_cards(state: dict, defeated_owner) -> None:
    """Resolve an eliminated player's hand after mandatory occupation."""
    defeated = str(defeated_owner)
    if defeated == 'neutral' or any(str(row['owner']) == defeated for row in state['territories'].values()):
        return
    owner = str(state['current_member_id'])
    won = state['hands'].get(defeated, [])
    if not won:
        return
    state['hands'].setdefault(owner, []).extend(won)
    state['hands'][defeated] = []
    if len(state['hands'][owner]) >= 6:
        state.update(phase='reinforce', trade_resume_phase='attack', placement_started=False, remaining=0)
        state['reinforcement'] = {'base': 0, 'continents': [], 'cards': 0, 'total': 0}
