"""Initial army placement after the random territory assignment.

Players place one army at a time in fixed seat order. The classic two-player
exception is two own placements followed by one neutral placement per turn.
"""
from __future__ import annotations


def setup_target(state: dict) -> str:
    return 'neutral' if state['setup'].get('neutral_due') else str(state['current_member_id'])


def setup_remaining(state: dict) -> int:
    setup = state['setup']
    return setup['neutral_remaining'] if setup.get('neutral_due') else setup['remaining'][str(state['current_member_id'])]


def place_initial_army(state: dict, territory_id: str, count: int) -> bool:
    """Place exactly one unit; return True when every army is deployed."""
    setup = state['setup']
    actor = str(state['current_member_id'])
    target = setup_target(state)
    board = state['territories']
    if count != 1:
        raise ValueError('Bei der Startaufstellung setzt du jeweils genau eine Einheit.')
    if territory_id not in board or str(board[territory_id]['owner']) != target:
        raise ValueError('Wähle ein neutrales Land für die neutrale Einheit.' if target == 'neutral'
                         else 'Wähle eines deiner eigenen Länder für die Starteinheit.')
    if setup_remaining(state) <= 0:
        raise ValueError('Für diese Armee sind keine Starttruppen mehr übrig.')
    board[territory_id]['armies'] += 1
    setup['placed'] += 1
    if target == 'neutral':
        setup['neutral_remaining'] -= 1
        setup['neutral_due'] = False
        setup['own_in_turn'] = 0
    else:
        setup['remaining'][actor] -= 1
        setup['own_in_turn'] += 1
        if len(state['participants']) == 2:
            if setup['own_in_turn'] < 2 and setup['remaining'][actor] > 0:
                state['remaining'] = setup_remaining(state)
                return False
            if setup['neutral_remaining'] > 0:
                setup['neutral_due'] = True
                state['remaining'] = setup_remaining(state)
                return False
        setup['own_in_turn'] = 0
    if not any(setup['remaining'].values()) and setup['neutral_remaining'] == 0:
        state['current_member_id'] = setup['first_member_id']
        state['phase'] = 'reinforce'
        setup['complete'] = True
        return True
    order = [str(row['id']) for row in state['participants']]
    current = order.index(actor)
    state['current_member_id'] = next(order[(current + offset) % len(order)]
                                      for offset in range(1, len(order) + 1)
                                      if setup['remaining'][order[(current + offset) % len(order)]] > 0)
    state['remaining'] = setup_remaining(state)
    return False


def public_setup(state: dict) -> dict | None:
    if state['phase'] != 'setup':
        return None
    setup = state['setup']
    return {'remaining': setup['remaining'], 'initial_armies': setup['initial_armies'],
            'target_owner': setup_target(state), 'neutral_remaining': setup['neutral_remaining'],
            'own_in_turn': setup['own_in_turn'], 'duel': len(state['participants']) == 2}
