"""Public portrait descriptors from the existing avatar catalog; no profile writes."""
from flask import current_app, url_for


def register_portraits(app, avatars):
    # All registered stage images use the same 1400px canvas, with the figure
    # beginning at y=400. Crop the existing art; never generate another avatar.
    app.extensions['player_portraits'] = {
        avatar['id']: dict(avatar, crop={'scale': 1 if avatar['id'] == 'a00' else 1.7,
                                       'top': 0 if avatar['id'] == 'a00' else -48})
        for avatar in avatars
    }


def public_portrait(avatar_id, *, is_self=False):
    catalog = current_app.extensions['player_portraits']
    avatar = catalog.get(avatar_id, catalog['a00'])
    asset = avatar['stage_asset']
    if avatar['id'] == 'a00' and not is_self:
        asset = avatar['public_asset']
    return {'avatar_id': avatar['id'], 'url': url_for('static', filename='avatars/' + asset),
            'alt': 'Avatar ' + avatar['name'], 'crop': dict(avatar['crop'])}
