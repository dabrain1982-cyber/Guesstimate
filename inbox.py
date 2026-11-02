"""Private in-game notes: players to owner, owner to one player or all."""
from datetime import datetime
from flask import abort, flash, g, jsonify, redirect, render_template, request, url_for


def init_inbox(db):
    db.executescript("""
        CREATE TABLE IF NOT EXISTS inbox_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL REFERENCES users(id),
            subject TEXT NOT NULL, body TEXT NOT NULL, created_at TEXT NOT NULL,
            broadcast INTEGER NOT NULL DEFAULT 0 CHECK (broadcast IN (0, 1))
        );
        CREATE TABLE IF NOT EXISTS inbox_deliveries (
            message_id INTEGER NOT NULL REFERENCES inbox_messages(id),
            user_id INTEGER NOT NULL REFERENCES users(id), read_at TEXT,
            PRIMARY KEY (message_id, user_id)
        );
        CREATE INDEX IF NOT EXISTS inbox_recipient ON inbox_deliveries(user_id, message_id);
        CREATE TABLE IF NOT EXISTS inbox_attention (
            user_id INTEGER PRIMARY KEY REFERENCES users(id),
            seen_through INTEGER NOT NULL DEFAULT 0
        );
    """)


def inbox_summary(db, user_id):
    row = db.execute("""
        SELECT COUNT(CASE WHEN read_at IS NULL THEN 1 END) AS unread,
               COALESCE(MAX(message_id), 0) AS latest
        FROM inbox_deliveries WHERE user_id = ?
    """, (user_id,)).fetchone()
    seen = db.execute('SELECT seen_through FROM inbox_attention WHERE user_id = ?',
                      (user_id,)).fetchone()
    return dict(unread=row['unread'], latest=row['latest'],
                attention=row['latest'] > (seen['seen_through'] if seen else 0))


def add_latest_broadcast_sender_copy(db, sender_id):
    """Add only the sender's missing receipt; never resend other deliveries."""
    if not db.in_transaction:
        raise ValueError('Die Kontrollkopie benötigt eine gemeinsame Transaktion.')
    row = db.execute("""
        SELECT id FROM inbox_messages WHERE sender_id = ? AND broadcast = 1
        ORDER BY id DESC LIMIT 1
    """, (sender_id,)).fetchone()
    if row is None:
        return dict(message_id=None, copy_added=False)
    inserted = db.execute(
        'INSERT OR IGNORE INTO inbox_deliveries(message_id, user_id) VALUES (?, ?)',
        (row['id'], sender_id)).rowcount
    if inserted:
        # A newly delivered older note must also attract its recipient's attention.
        # Existing read states and all other accounts remain untouched.
        db.execute("""
            UPDATE inbox_attention SET seen_through = MIN(seen_through, ?)
            WHERE user_id = ?
        """, (row['id'] - 1, sender_id))
    return dict(message_id=row['id'], copy_added=bool(inserted))


def register_inbox(app, login_required, require_csrf, is_owner):
    def owner():
        return app.get_db().execute(
            'SELECT id, display_name FROM users WHERE username = ?',
            (app.config['OWNER_USERNAME'],)
        ).fetchone()

    @app.context_processor
    def mail_globals():
        user = getattr(g, 'user', None)
        return {'mail_status': inbox_summary(app.get_db(), user['id']) if user else None}

    @app.after_request
    def private_mail(response):
        if request.endpoint in ('mailbox', 'mail_status', 'mail_open', 'mail_read', 'mail_send'):
            response.headers['Cache-Control'] = 'private, no-store'
            response.headers['X-Robots-Tag'] = 'noindex, nofollow'
        return response

    def show_mailbox(error=None, form=None, status=200):
        db, user_id = app.get_db(), g.user['id']
        sent = request.args.get('folder') == 'sent'
        if sent:
            notes = db.execute("""
                SELECT m.*, u.display_name AS sender_name,
                       CASE WHEN m.broadcast THEN 'alle Spieler'
                            ELSE (SELECT r.display_name FROM inbox_deliveries d
                                  JOIN users r ON r.id = d.user_id
                                  WHERE d.message_id = m.id LIMIT 1) END AS recipient_name
                FROM inbox_messages m JOIN users u ON u.id = m.sender_id
                WHERE m.sender_id = ? ORDER BY m.id DESC
            """, (user_id,)).fetchall()
        else:
            notes = db.execute("""
                SELECT m.*, u.display_name AS sender_name, d.read_at
                FROM inbox_deliveries d JOIN inbox_messages m ON m.id = d.message_id
                JOIN users u ON u.id = m.sender_id
                WHERE d.user_id = ? ORDER BY m.id DESC
            """, (user_id,)).fetchall()
        selected = None
        note_id = request.args.get('note', type=int)
        if note_id is not None:
            selected = db.execute("""
                SELECT m.*, u.display_name AS sender_name, d.read_at,
                       CASE WHEN m.broadcast THEN 'alle Spieler'
                            ELSE (SELECT r.display_name FROM inbox_deliveries x
                                  JOIN users r ON r.id = x.user_id
                                  WHERE x.message_id = m.id LIMIT 1) END AS recipient_name
                FROM inbox_messages m JOIN users u ON u.id = m.sender_id
                LEFT JOIN inbox_deliveries d ON d.message_id = m.id AND d.user_id = ?
                WHERE m.id = ? AND (m.sender_id = ? OR d.user_id = ?)
            """, (user_id, note_id, user_id, user_id)).fetchone()
            if selected is None:
                abort(404)
        owner_user, owner_mode = owner(), is_owner(user_id)
        recipients = db.execute(
            'SELECT id, display_name FROM users WHERE id != ? ORDER BY display_name COLLATE NOCASE',
            (user_id,)
        ).fetchall() if owner_mode else []
        return render_template('mail.html', notes=notes, selected=selected, sent=sent,
                               owner_mode=owner_mode, owner_user=owner_user,
                               recipients=recipients, mail_error=error,
                               mail_form=form or {}), status

    @app.get('/mail')
    @login_required
    def mailbox():
        return show_mailbox()

    @app.get('/mail/status')
    @login_required
    def mail_status():
        return jsonify(inbox_summary(app.get_db(), g.user['id']))

    @app.post('/mail/oeffnen')
    @login_required
    def mail_open():
        require_csrf()
        db = app.get_db()
        through = request.form.get('through', type=int)
        if through is None or through < 0:
            abort(400)
        through = min(through, inbox_summary(db, g.user['id'])['latest'])
        with db:
            db.execute("""
                INSERT INTO inbox_attention(user_id, seen_through) VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE
                    SET seen_through = MAX(seen_through, excluded.seen_through)
            """, (g.user['id'], through))
        return redirect(url_for('mailbox'), code=303)

    @app.post('/mail/<int:message_id>/lesen')
    @login_required
    def mail_read(message_id):
        require_csrf()
        db = app.get_db()
        if db.execute('SELECT 1 FROM inbox_deliveries WHERE message_id = ? AND user_id = ?',
                      (message_id, g.user['id'])).fetchone() is None:
            abort(404)
        with db:
            db.execute("""
                UPDATE inbox_deliveries SET read_at = COALESCE(read_at, ?)
                WHERE message_id = ? AND user_id = ?
            """, (datetime.now().isoformat(timespec='seconds'), message_id, g.user['id']))
        return redirect(url_for('mailbox', note=message_id), code=303)

    @app.post('/mail/senden')
    @login_required
    def mail_send():
        require_csrf()
        db, owner_user = app.get_db(), owner()
        if owner_user is None:
            return show_mailbox('Der Empfänger ist noch nicht verfügbar.', request.form, 400)
        recipient, broadcast = request.form.get('recipient', ''), False
        if is_owner(g.user['id']):
            if recipient == 'all':
                broadcast = True
                recipient_ids = [r['id'] for r in db.execute('SELECT id FROM users')]
            else:
                target_id = request.form.get('recipient', type=int)
                target = db.execute('SELECT id FROM users WHERE id = ? AND id != ?',
                                    (target_id, g.user['id'])).fetchone()
                if target is None:
                    return show_mailbox('Bitte wähle einen Empfänger.', request.form, 400)
                recipient_ids = [target['id']]
        else:
            if recipient not in ('', str(owner_user['id'])):
                abort(403)
            recipient_ids = [owner_user['id']]
        subject, body = request.form.get('subject', '').strip(), request.form.get('body', '').strip()
        if not subject or not body or len(subject) > 120 or len(body) > 12000:
            return show_mailbox('Bitte fülle Betreff und Nachricht aus. Der Betreff darf höchstens '
                                '120 Zeichen, die Nachricht 12.000 Zeichen lang sein.', request.form, 400)
        if not recipient_ids:
            return show_mailbox('Es sind noch keine Empfänger vorhanden.', request.form, 400)
        with db:
            message_id = db.execute("""
                INSERT INTO inbox_messages(sender_id, subject, body, created_at, broadcast)
                VALUES (?, ?, ?, ?, ?)
            """, (g.user['id'], subject, body,
                  datetime.now().isoformat(timespec='seconds'), int(broadcast))).lastrowid
            db.executemany('INSERT INTO inbox_deliveries(message_id, user_id) VALUES (?, ?)',
                           [(message_id, user_id) for user_id in recipient_ids])
        flash('Dein Zettel wurde verschickt.', 'success')
        return redirect(url_for('mailbox', folder='sent', note=message_id), code=303)
