"""Classic Risk victory checks, independent of the table presentation.

Hasbro risk.pdf pp. 10, 12, 14: missions win immediately, including help
from another player. In a duel, neutral armies need not be eliminated.
Existing mission IDs and assignments remain unchanged.
"""
from __future__ import annotations

CONTINENT_MISSIONS = {
    'mission-europa-australien': ('europa', 'australien'),
    'mission-asien-afrika': ('asien', 'afrika'),
    'mission-nordamerika-afrika': ('nordamerika', 'afrika'),
    'mission-nordamerika-australien': ('nordamerika', 'australien'),
    'mission-asien-suedamerika': ('asien', 'suedamerika'),
}
COLOR_SEATS = {'mission-gelb': 0, 'mission-blau': 2, 'mission-gruen': 3,
               'mission-violett': 4, 'mission-orange': 5}


def mission_complete(state: dict, world: dict, owner: str, mission_id: str) -> bool:
    board = state['territories']
    owned = {row['id'] for row in world['territories']
             if str(board[row['id']]['owner']) == owner and board[row['id']]['armies'] > 0}
    if mission_id == 'mission-24-laender':
        return len(owned) >= 24
    if mission_id == 'mission-18-doppelt':
        return sum(board[key]['armies'] >= 2 for key in owned) >= 18
    if mission_id in CONTINENT_MISSIONS:
        return all(all(row['id'] in owned for row in world['territories'] if row['continent'] == continent)
                   for continent in CONTINENT_MISSIONS[mission_id])
    if mission_id in COLOR_SEATS:
        seat = COLOR_SEATS[mission_id]
        participants = state['participants']
        # Unused colours must never cause an instant win in an old save.
        target_player = next((row for index, row in enumerate(participants) if row.get('color_index', index) == seat), None)
        if target_player is None:
            return False
        target = str(target_player['id'])
        if target == owner:
            return len(owned) >= 24
        return not any(str(row['owner']) == target for row in board.values())
    return False


def check_victory(state: dict, world: dict) -> dict | None:
    """Finish only a fully occupied board, never the intermediate capture state."""
    if state.get('winner'):
        return state['winner']
    if state['phase'] == 'setup' or state.get('pending_conquest') or state.get('battle_request'):
        return None
    board = state['territories']
    if any(row['id'] not in board or board[row['id']]['armies'] < 1 for row in world['territories']):
        return None
    alive = {str(row['owner']) for row in board.values()}
    participants = state['participants']
    actor = str(state['current_member_id'])
    # The acting player has priority if one atomic move completes two missions.
    start = next(i for i, row in enumerate(participants) if str(row['id']) == actor)
    order = participants[start:] + participants[:start]
    mode = state.get('victory_mode', 'missions' if state.get('missions') else 'world')
    for player in order:
        owner = str(player['id'])
        if owner not in alive:
            continue
        mission_id = state.get('missions', {}).get(owner)
        mission = next((row for row in world['missions'] if row['id'] == mission_id), None)
        fulfilled = mode == 'missions' and mission and mission_complete(state, world, owner, mission_id)
        world_won = alive == {owner}
        duel_won = len(participants) == 2 and not any(
            str(row['id']) in alive for row in participants if str(row['id']) != owner)
        if not (fulfilled or world_won or duel_won):
            continue
        reason = mission['text'] if fulfilled else (
            'Alle gegnerischen Armeen besiegt. Neutrale Gebiete dürfen im Zweierspiel bestehen bleiben.'
            if duel_won and 'neutral' in alive else 'Alle 42 Länder erobert.')
        winner = {'member_id': owner, 'name': player['name'], 'mode': mode, 'reason': reason,
                  'mission': dict(mission) if fulfilled else None, 'turn_number': state['turn_number']}
        state.update(phase='completed', winner=winner)
        return winner
    return None
