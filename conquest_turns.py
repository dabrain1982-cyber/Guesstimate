"""Persisted Conquest turns; the browser only requests actions and draws state."""
from __future__ import annotations

import secrets
from typing import Any
from conquest_cards import catalog, exchange, inherit_cards, initialize_cards, trade_info
from conquest_victory import check_victory
from conquest_setup import place_initial_army, public_setup

COLORS = [('#dab249', '#24190b'), ('#ad3935', '#fff8e1'), ('#326fa5', '#fff8e1'),
          ('#57934b', '#fff8e1'), ('#8a5ba2', '#fff8e1'), ('#d78032', '#24190b')]


def reinforcement(state: dict, world: dict) -> dict:
    owner = str(state['current_member_id'])
    owned = {key for key, value in state['territories'].items() if str(value['owner']) == owner}
    base = max(3, len(owned) // 3)
    bonuses = [continent for continent in world['continents'] if all(
        row['id'] in owned for row in world['territories'] if row['continent'] == continent['id'])]
    return {'base': base, 'continents': [{'name': row['name'], 'bonus': row['bonus']} for row in bonuses],
            'total': base + sum(row['bonus'] for row in bonuses)}


def hydrate(state: dict, world: dict, members: list, victory_mode: str | None = None) -> dict:
    state.setdefault('participants', [{'id': str(row['id']), 'name': row['display_name']} for row in members])
    state.setdefault('turn_number', 1)
    state.setdefault('conquered_count', int(state.get('captured_this_turn', False)))
    state.setdefault('fortified', False)
    state.setdefault('pending_conquest', None)
    state.setdefault('battle_request', None)
    state.setdefault('last_battle', None)
    state.setdefault('end_result', None)
    state.setdefault('last_turn_results', {})
    state.setdefault('victory_mode', victory_mode or ('missions' if state.get('missions') else 'world'))
    state.setdefault('winner', None)
    state.setdefault('hands', {str(row['id']): [] for row in members})
    used = {card for hand in state['hands'].values() for card in hand}
    state.setdefault('card_deck', [row['id'] for row in world['territories'] if row['id'] not in used])
    state.setdefault('reinforcement', reinforcement(state, world))
    state.setdefault('remaining', state['reinforcement']['total'])
    initialize_cards(state, world)
    return state


def next_owner(state: dict) -> str:
    order = [str(row['id']) for row in state['participants']]
    current = order.index(str(state['current_member_id']))
    alive = {str(row['owner']) for row in state['territories'].values()}
    return next(order[(current + offset) % len(order)] for offset in range(1, len(order) + 1)
                if order[(current + offset) % len(order)] in alive)


def ended_result(state: dict) -> dict:
    # Older saved end states may predate the explicit receipt; never draw again.
    return dict(state.get('end_result') or {
        'ownerId': str(state['current_member_id']), 'turnNumber': state['turn_number'],
        'conqueredCount': state.get('conquered_count', 0), 'card': None,
        'nextOwnerId': next_owner(state),
    })


def public_game(state: dict, world: dict, member_id: int, developer: bool) -> dict:
    actor = str(state['current_member_id'])
    viewer = str(member_id)
    can_act = not state.get('winner') and (actor == viewer or developer)
    inventory_owner = actor if developer else viewer
    alive = {str(row['owner']) for row in state['territories'].values()}
    armies = [dict(row, id=str(row['id']), color=COLORS[row.get('color_index', index)][0], ink=COLORS[row.get('color_index', index)][1],
                   eliminated=str(row['id']) not in alive, card_count=len(state['hands'].get(str(row['id']), [])))
              for index, row in enumerate(state['participants'])]
    if any(str(row['owner']) == 'neutral' for row in state['territories'].values()):
        armies.append({'id': 'neutral', 'name': 'Neutral', 'color': '#858575', 'ink': '#fff8e1'})
    cards = catalog(world)
    trade = trade_info(state, world)
    if not can_act:
        trade = dict(trade, can_trade=False, mandatory=False, territory_bonus_available=False)
    end = state['end_result']
    if end:
        end = dict(end)
        if not can_act:
            end['card'] = None
    return {
        'phase': state['phase'], 'round': state['round'], 'current_member_id': state['current_member_id'],
        'territories': state['territories'], 'opening_rolls': state['opening_rolls'],
        'own_mission': state.get('missions', {}).get(inventory_owner),
        'inventory': {
            'territory_cards': [cards[key] for key in state['hands'].get(inventory_owner, []) if key in cards],
            'mission': next((row for row in world['missions']
                             if row['id'] == state.get('missions', {}).get(inventory_owner)), None),
        },
        'armies': armies, 'can_act': can_act, 'developer': developer,
        'inventory_owner_id': inventory_owner, 'remaining': state['remaining'],
        'reinforcement': state['reinforcement'], 'conquered_count': state['conquered_count'],
        'fortified': state['fortified'], 'pending_conquest': state['pending_conquest'],
        'battle_request': state['battle_request'], 'last_battle': state['last_battle'],
        'can_defend': bool(not state.get('winner') and state['battle_request'] and str(state['battle_request']['defender']) == viewer),
        'turn_number': state['turn_number'], 'next_owner_id': None if state.get('winner') else next_owner(state), 'end_result': end,
        'last_turn_result': state.get('last_turn_results', {}).get(inventory_owner),
        'winner': state.get('winner'),
        'setup': public_setup(state),
        'trade': trade,
    }


def apply_action(state: dict, world: dict, action: str, fields: Any, member_id: int, developer: bool) -> dict | None:
    """Mutate only a caller-owned transaction copy. Invalid requests are rolled back."""
    if state.get('winner') or state['phase'] == 'completed':
        raise ValueError('Dieser Feldzug ist beendet. Weitere Züge sind nicht möglich.')
    result = _apply_action(state, world, action, fields, member_id, developer)
    check_victory(state, world)
    return result


def _apply_action(state: dict, world: dict, action: str, fields: Any, member_id: int, developer: bool) -> dict | None:
    actor = str(state['current_member_id'])
    viewer = str(member_id)
    board = state['territories']
    by_id = {row['id']: row for row in world['territories']}
    from_id, to_id = fields.get('from', ''), fields.get('to', '')

    def number(key: str) -> int:
        try:
            value = int(fields.get(key, ''))
        except (TypeError, ValueError):
            raise ValueError('Bitte eine gültige ganze Zahl wählen.') from None
        if not 1 <= value <= 1_000_000:
            raise ValueError('Die gewählte Anzahl ist nicht zulässig.')
        return value

    def adjacent(own_target: bool) -> None:
        if from_id not in by_id or to_id not in by_id or to_id not in by_id[from_id]['neighbors']:
            raise ValueError('Die beiden Länder müssen direkte Nachbarn sein.')
        if str(board[from_id]['owner']) != actor or board[from_id]['armies'] < 2:
            raise ValueError('Wähle ein eigenes Land mit mindestens zwei Truppen.')
        if (str(board[to_id]['owner']) == actor) != own_target:
            raise ValueError('Dieses Zielland ist für die Aktion nicht zulässig.')

    def battle(request: dict, defense: int) -> dict:
        source, target = board[request['from']], board[request['to']]
        attackers = sorted([secrets.randbelow(6) + 1 for _ in range(request['dice'])], reverse=True)
        defenders = sorted([secrets.randbelow(6) + 1 for _ in range(defense)], reverse=True)
        lost_attack = sum(a <= d for a, d in zip(attackers, defenders))
        lost_defense = min(len(attackers), len(defenders)) - lost_attack
        source['armies'] -= lost_attack
        target['armies'] -= lost_defense
        conquered = target['armies'] == 0
        if conquered:
            defeated_owner = target['owner']
            target['owner'] = state['current_member_id']
            state['pending_conquest'] = {'from': request['from'], 'to': request['to'],
                                        'min': request['dice'], 'max': source['armies'] - 1, 'defeated_owner': defeated_owner}
        result = {'from': request['from'], 'to': request['to'], 'attackRolls': attackers,
                  'defenseRolls': defenders, 'attackerLoss': lost_attack, 'defenderLoss': lost_defense,
                  'conquered': conquered, 'sequence': state.get('battle_sequence', 0) + 1,
                  'attackerId': str(state['current_member_id']), 'defenderId': str(request['defender'])}
        state['battle_sequence'] = result['sequence']
        state['last_battle'] = result
        state['battle_request'] = None
        return result

    if action == 'defend':
        request = state['battle_request']
        if not request or (str(request['defender']) != viewer and not developer):
            raise PermissionError('Du verteidigst dieses Land gerade nicht.')
        # Compatibility for already saved attacks; defense has no manual choice.
        return battle(request, min(2, board[request['to']]['armies']))
    if actor != viewer and not developer:
        raise PermissionError('Die andere Person ist am Zug.')
    if state['phase'] == 'setup':
        if action != 'place':
            raise ValueError('Verteilt zuerst alle Starttruppen, bevor das reguläre Spiel beginnt.')
        if place_initial_army(state, to_id, number('count')):
            state['reinforcement'] = reinforcement(state, world)
            state['remaining'] = state['reinforcement']['total']
            state['placement_started'] = False
        return {'initial_placement': True}
    if state['battle_request']:
        raise ValueError('Warte auf die Würfelwahl der Verteidigung.')
    if state['pending_conquest'] and action != 'occupy':
        raise ValueError('Lass zuerst Truppen in das eroberte Land einrücken.')
    if action == 'finish':
        if state['phase'] not in ('fortify', 'ended'):
            raise ValueError('Beende zuerst deine Angriffe und die notwendige Besetzung.')
        if state['phase'] == 'fortify':
            _apply_action(state, world, 'advance', fields, member_id, developer)
            check_victory(state, world)
        result = ended_result(state)
        if not state.get('winner'):
            _apply_action(state, world, 'pass', fields, member_id, developer)
        return {'endResult': result}
    if action == 'trade':
        return exchange(state, world, fields)
    if action in ('place', 'advance') and trade_info(state, world)['mandatory']:
        raise ValueError('Bei fünf oder mehr Karten musst du zuerst einen gültigen Satz eintauschen.')
    if action == 'place':
        count = number('count')
        if state['phase'] != 'reinforce' or to_id not in board or str(board[to_id]['owner']) != actor:
            raise ValueError('Du kannst jetzt nur eigene Länder verstärken.')
        if count > state['remaining']:
            raise ValueError('So viele Verstärkungen sind nicht mehr verfügbar.')
        board[to_id]['armies'] += count
        state['remaining'] -= count
        state['placement_started'] = True
    elif action == 'advance':
        if state['phase'] == 'reinforce' and state['remaining'] == 0:
            state['phase'] = state.get('trade_resume_phase') or 'attack'
            state['trade_resume_phase'] = None
        elif state['phase'] == 'attack':
            state['phase'] = 'fortify'
        elif state['phase'] == 'fortify':
            card = None
            if state['conquered_count']:
                if not state['card_deck'] and state['card_discard']:
                    state['card_deck'] = list(state['card_discard'])
                    secrets.SystemRandom().shuffle(state['card_deck'])
                    state['card_discard'] = []
                if not state['card_deck']:
                    raise ValueError('Der Kartenstapel ist leer; der Kartentausch folgt noch.')
                card = secrets.choice(state['card_deck'])
                state['card_deck'].remove(card)
                state['hands'].setdefault(actor, []).append(card)
            state['phase'] = 'ended'
            state['end_result'] = {'ownerId': actor, 'turnNumber': state['turn_number'],
                                   'conqueredCount': state['conquered_count'], 'card': card,
                                   'nextOwnerId': next_owner(state)}
        else:
            raise ValueError('Verteile zuerst alle Verstärkungen oder beende die laufende Aktion.')
    elif action == 'attack':
        if state['phase'] != 'attack':
            raise ValueError('Angriffe sind nur in der Angriffsphase möglich.')
        adjacent(False)
        count = number('dice')
        if count > min(3, board[from_id]['armies'] - 1):
            raise ValueError('Diese Zahl an Angriffswürfeln ist nicht möglich.')
        request = {'from': from_id, 'to': to_id, 'dice': count, 'defender': board[to_id]['owner']}
        # Until manual dice exist, resolve both sides in this one transaction.
        return battle(request, min(2, board[to_id]['armies']))
    elif action == 'occupy':
        pending = state['pending_conquest']
        count = number('count')
        if not pending or not pending['min'] <= count <= pending['max']:
            raise ValueError('Bitte die zulässige Zahl an Truppen einrücken lassen.')
        board[pending['from']]['armies'] -= count
        board[pending['to']]['armies'] = count
        state['pending_conquest'] = None
        state['conquered_count'] += 1
        state['captured_this_turn'] = True
        inherit_cards(state, pending.get('defeated_owner', 'neutral'))
    elif action == 'fortify':
        if state['phase'] != 'fortify' or state['fortified']:
            raise ValueError('Festigen ist nur einmal pro Zug möglich.')
        adjacent(True)
        count = number('count')
        if count >= board[from_id]['armies']:
            raise ValueError('Mindestens eine Truppe muss zurückbleiben.')
        board[from_id]['armies'] -= count
        board[to_id]['armies'] += count
        state['fortified'] = True
    elif action == 'pass':
        if state['phase'] != 'ended':
            raise ValueError('Beende zuerst den aktuellen Zug.')
        state.setdefault('last_turn_results', {})[actor] = ended_result(state)
        state['current_member_id'] = next_owner(state)
        state['turn_number'] += 1
        state['round'] = (state['turn_number'] - 1) // len(state['participants']) + 1
        state.update(phase='reinforce', conquered_count=0, fortified=False,
                     pending_conquest=None, end_result=None, last_battle=None, captured_this_turn=False,
                     placement_started=False, trade_resume_phase=None)
        state['reinforcement'] = reinforcement(state, world)
        state['remaining'] = state['reinforcement']['total']
    else:
        raise ValueError('Unbekannte Zugaktion.')
    return None
