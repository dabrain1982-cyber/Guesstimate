"""Public presentation data only; no account, score or seating writes."""
import ast
import base64
from io import BytesIO
from pathlib import Path
import sqlite3

from flask import Flask
from PIL import Image
from player_portrait import register_portraits, public_portrait


def build_players(root):
    catalogs = {}
    for node in ast.parse((root / 'app.py').read_text(encoding='utf-8-sig')).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in ('AVATAR_CATALOG', 'DEFAULT_AVATAR'):
                    catalogs[target.id] = ast.literal_eval(node.value)
    app = Flask('blackjack_portrait_preview', static_folder=str(root / 'static'))
    register_portraits(app, [catalogs['DEFAULT_AVATAR'], *catalogs['AVATAR_CATALOG']])
    database = root / 'runtime/pc-local/quiz.sqlite3'
    own_name, own_avatar = 'Du', 'a00'
    if database.is_file():
        connection = sqlite3.connect(database.resolve().as_uri() + '?mode=ro', uri=True)
        try:
            row = connection.execute("SELECT u.display_name,coalesce(c.avatar_id,'a00') FROM users u LEFT JOIN user_cosmetics c ON c.user_id=u.id ORDER BY u.id LIMIT 1").fetchone()
            if row:
                own_name, own_avatar = row
        finally:
            connection.close()
    selections = [('left', 'Mira', 'a01', True), ('self', own_name, own_avatar, False), ('right', 'Jan', 'a09', True)]
    players, sources = [], []
    with app.test_request_context('/'):
        for slot, name, avatar, example in selections:
            portrait = public_portrait(avatar, is_self=slot == 'self')
            path = root / portrait['url'].lstrip('/')
            if path.suffix == '.svg':
                raw = path.read_bytes()
                portrait['url'] = 'data:image/svg+xml;base64,' + base64.b64encode(raw).decode('ascii')
            else:
                # Same full canvas and the shared crop, only delivery resolution changes.
                with Image.open(path) as image:
                    image.thumbnail((192,192), Image.Resampling.LANCZOS)
                    output = BytesIO(); image.save(output, format='WEBP', quality=85, method=6)
                portrait['url'] = 'data:image/webp;base64,' + base64.b64encode(output.getvalue()).decode('ascii')
            players.append(dict(slot=slot, name=name, portrait=portrait, example=example))
            sources.append(path.relative_to(root).as_posix())
    return players, sources
