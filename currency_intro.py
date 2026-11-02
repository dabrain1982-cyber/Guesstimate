"""One announcement per account, independent of browser cookies."""
from datetime import datetime, timezone
from flask import g, jsonify, request

NOTICE='ikuehe-introduction'

def init_notices(db):
    db.execute("""CREATE TABLE IF NOT EXISTS user_notice_views (
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        notice_id TEXT NOT NULL, shown_at TEXT NOT NULL,
        PRIMARY KEY(user_id,notice_id))""")
    db.commit()

def register_currency_intro(app, login_required, require_csrf):
    @app.context_processor
    def intro_context():
        user=getattr(g,'user',None)
        pending=bool(user and request.endpoint=='home' and not app.get_db().execute(
            'SELECT 1 FROM user_notice_views WHERE user_id=? AND notice_id=?',
            (user['id'],NOTICE)).fetchone())
        return dict(currency_intro_pending=pending)

    @app.post('/ikuehe/einfuehrung')
    @login_required
    def claim_currency_intro():
        require_csrf()
        db=app.get_db()
        with db:
            inserted=db.execute('INSERT OR IGNORE INTO user_notice_views VALUES(?,?,?)',
                (g.user['id'],NOTICE,datetime.now(timezone.utc).isoformat())).rowcount
        response=jsonify(show=bool(inserted))
        response.headers['Cache-Control']='private, no-store'
        return response
