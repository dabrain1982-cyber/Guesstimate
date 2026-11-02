"""Read current profile equipment for lobby displays without changing membership or play state."""

from flask import current_app


def lobby_player_profiles(members):
    players = [dict(member) for member in members]
    user_ids = list(dict.fromkeys(player.get('user_id') for player in players if player.get('user_id') is not None))
    profiles = {}
    if user_ids:
        placeholders = ','.join('?' for _ in user_ids)
        rows = current_app.get_db().execute(
            f'SELECT user_id, avatar_id, plaque_id, background_id, phrase_id FROM user_cosmetics WHERE user_id IN ({placeholders})',
            user_ids,
        ).fetchall()
        profiles = {row['user_id']: dict(row) for row in rows}
    defaults = {'avatar_id': 'a00', 'plaque_id': 'p00', 'background_id': 'b00', 'phrase_id': ''}
    for player in players:
        profile = profiles.get(player.get('user_id'))
        source = profile if profile is not None else player.get('cosmetics', player)
        player['cosmetics'] = {key: source.get(key) if source.get(key) is not None else default
                               for key, default in defaults.items()}
    return players
