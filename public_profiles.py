"""Profiles visible to signed-in players; no inventory or account writes."""
from flask import abort, g, render_template, request


def register_public_profiles(app, login_required, cosmetics_for, points_for, trophies_for, ranks):
    @app.get('/spieler')
    @login_required
    def players():
        query=request.args.get('q','').strip()[:100]
        rows=sorted(ranks('all'),key=lambda p:(p['display_name'].casefold(),p['id']))
        visible=[p for p in rows if query.casefold() in p['display_name'].casefold()]
        response=app.make_response(render_template('players.html',players=visible,query=query,player_count=len(rows)))
        response.headers['Cache-Control']='private, no-store'
        response.headers['X-Robots-Tag']='noindex, nofollow'
        return response

    @app.get('/spieler/<int:user_id>')
    @login_required
    def public_profile(user_id):
        user=app.get_db().execute('SELECT id, display_name FROM users WHERE id=?',(user_id,)).fetchone()
        if user is None:abort(404)
        # Only equipped appearance and aggregate game results form the public view.
        appearance=cosmetics_for(user_id)
        appearance={k:appearance[k] for k in ('avatar_id','plaque_id','background_id','phrase_id')}
        stats=app.get_db().execute('SELECT COUNT(*) AS rounds, COALESCE(MAX(score),0) AS best, COALESCE(AVG(score),0) AS average FROM attempts WHERE user_id=? AND status=?',(user_id,'completed')).fetchone()
        profile=dict(user,points=points_for(user_id),stats=dict(rounds=stats['rounds'],best=int(stats['best']),average=round(stats['average'])),rank=next(p['rank'] for p in ranks('all') if p['id']==user_id))
        response=app.make_response(render_template('public_profile.html',profile=profile,cosmetics=appearance,trophies=trophies_for(user_id),is_self=user_id==g.user['id']))
        response.headers['Cache-Control']='private, no-store'
        response.headers['X-Robots-Tag']='noindex, nofollow'
        return response
