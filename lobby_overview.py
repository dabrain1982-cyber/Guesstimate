"""Shared overview rendering; membership and game transitions remain in each game."""
import hashlib
import json

from flask import render_template, request, url_for


DISPLAY_FIELDS = (
    'id', 'name', 'host_user_id', 'host_name', 'member_count', 'is_member',
    'is_reserved', 'status', 'rounds', 'deck_size', 'starting_points',
    'dice_count', 'use_cup', 'goal_mode', 'goal_value', 'victory_mode', 'player_limit',
)


def overview_signature(lobbies):
    """Only visible room facts change the overview, never individual game moves."""
    rows = [dict(row) for row in lobbies]
    visible = [{key: row.get(key) for key in DISPLAY_FIELDS} for row in rows]
    return hashlib.sha256(json.dumps(visible, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def render_overview(template, lobbies, **context):
    rows = list(lobbies)
    signature = overview_signature(rows)
    if request.accept_mimetypes.best == 'application/json':
        return {'signature': signature}
    return render_template(template, lobbies=rows, overview_signature=signature,
                           overview_status_url=url_for(request.endpoint, **(request.view_args or {})), **context)
