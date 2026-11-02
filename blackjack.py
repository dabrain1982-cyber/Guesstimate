"""One shared Blackjack table with authenticated seating and server-owned rounds."""
from datetime import datetime, timezone
import sqlite3
import time
from pathlib import Path

from flask import abort, current_app, g, jsonify, redirect, render_template, request, send_file, url_for
from player_portrait import public_portrait
import blackjack_game as game
import blackjack_store as store


def init_blackjack_db(get_db):
    database = get_db()
    database.execute("""
        CREATE TABLE IF NOT EXISTS blackjack_seats (
            seat INTEGER PRIMARY KEY CHECK (seat BETWEEN 1 AND 3),
            user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
            joined_at TEXT NOT NULL
        )
    """)
    database.commit()
    game.init_game_db(database)


def seating_snapshot(database, viewer_id):
    own_transaction = not database.in_transaction
    if own_transaction:
        database.execute('BEGIN')
    try:
        return _snapshot(database, viewer_id)
    finally:
        if own_transaction:
            database.commit()


def _snapshot(database, viewer_id):
    state, balances, revision = store.load(database)
    rows = {row['seat']: row for row in database.execute("""
        SELECT s.seat, s.user_id, u.display_name, COALESCE(c.avatar_id, 'a00') AS avatar_id
        FROM blackjack_seats s JOIN users u ON u.id = s.user_id
        LEFT JOIN user_cosmetics c ON c.user_id = u.id ORDER BY s.seat
    """)}
    seats, own = [], None
    for number, slot in enumerate(('left', 'self', 'right'), 1):
        row = rows.get(number)
        player = None
        if row:
            is_self = row['user_id'] == viewer_id
            if is_self:
                own = number
            player = dict(name=row['display_name'], is_self=is_self, leaving=str(row['user_id']) in state['pending_leaves'],
                          portrait=public_portrait(row['avatar_id'], is_self=is_self))
            uid = str(row['user_id'])
            participant = game.participant(state, uid)
            player.update(table_points=balances.get(uid, 0),
                          wager=sum(hand['bet'] for hand in participant['hands']) if participant else state['bets'].get(uid, 0) if state['phase']=='betting' else 0,
                          next_bet=state['bets'].get(uid, 0) if state['phase']!='betting' else 0)
        seats.append(dict(number=number, slot=slot, player=player))
    names = {str(r['id']): r['display_name'] for r in database.execute('SELECT id,display_name FROM users')}
    seat_map = {str(row['user_id']): number for number,row in rows.items()}
    return dict(seats=seats, viewer_seat=own, occupied=len(rows), phase=state['phase'], revision=revision, server_time=time.time(),
                game=game.public_game(state,balances,viewer_id,names,seat_map))


class SeatUnavailable(ValueError):
    pass


def take_seat(database, user_id, seat, *, risk_accepted=False):
    with database:
        database.execute('BEGIN IMMEDIATE')
        own = database.execute('SELECT seat FROM blackjack_seats WHERE user_id = ?', (user_id,)).fetchone()
        if own:
            if own['seat'] == seat:
                return
            raise SeatUnavailable('Du hast bereits einen Platz. Verlasse ihn, bevor du wechselst.')
        if database.execute('SELECT 1 FROM blackjack_seats WHERE seat = ?', (seat,)).fetchone():
            raise SeatUnavailable('Dieser Platz ist inzwischen belegt. Wähle einen freien Platz.')
        state, balances, _ = store.load(database)
        if store.joining_blocked(state):
            raise SeatUnavailable('Der bisherige Testtisch wird beendet. Bitte warte, bis alle aufgestanden sind.')
        if store.account_mode(state) and not risk_accepted:
            raise SeatUnavailable('Bestätige zuerst: Hier kannst du deine eingesetzten iKühe verlieren.')
        database.execute('INSERT INTO blackjack_seats (seat, user_id, joined_at) VALUES (?, ?, ?)',
                         (seat, user_id, datetime.now(timezone.utc).isoformat()))
        if not store.account_mode(state):
            database.execute('INSERT OR IGNORE INTO blackjack_balances VALUES (?, ?)',
                             (user_id, current_app.config.get('BLACKJACK_TEST_START_BALANCE', 1000)))
        state, balances, _ = store.load(database)
        if state['phase']=='result' and database.execute('SELECT COUNT(*) FROM blackjack_seats').fetchone()[0]==1:
            game.begin_betting(state)
        store.save(database, state, balances)


def register_blackjack_routes(app, login_required, require_csrf):
    def database():
        return current_app.get_db()

    def reply(error=None, status=200):
        snapshot = seating_snapshot(database(), g.user['id'])
        if error:
            snapshot['error'] = error
        response = jsonify(snapshot)
        response.status_code = status
        response.headers['Cache-Control'] = 'no-store'
        return response

    @app.get('/karten/blackjack')
    @login_required
    def blackjack_table():
        response = current_app.make_response(render_template(
            'blackjack_table.html', live_table=True,
            scene_image=url_for('static', filename='blackjack-tisch-sitzansicht-v1.webp'),
            seating=seating_snapshot(database(), g.user['id'])))
        response.headers['Cache-Control'] = 'no-store'
        return response

    @app.get('/karten/blackjack/status')
    @login_required
    def blackjack_status():
        return reply()

    @app.post('/karten/blackjack/platz')
    @login_required
    def blackjack_join():
        require_csrf()
        seat = request.form.get('seat')
        if seat not in ('1', '2', '3'):
            return reply('Bitte wähle einen der drei Plätze.', 400)
        try:
            take_seat(database(), g.user['id'], int(seat), risk_accepted=request.form.get('accept_risk') == '1')
        except (SeatUnavailable, sqlite3.IntegrityError) as error:
            return reply(str(error) if isinstance(error, SeatUnavailable) else 'Dieser Platz ist inzwischen belegt.', 409)
        return reply()

    @app.post('/karten/blackjack/verlassen')
    @login_required
    def blackjack_leave():
        require_csrf()
        with database():
            database().execute('BEGIN IMMEDIATE')
            state, balances, _ = store.load(database())
            uid = str(g.user['id'])
            seated = database().execute('SELECT 1 FROM blackjack_seats WHERE user_id=?', (g.user['id'],)).fetchone()
            if seated and uid in balances:
                pending = game.leave_round(state, balances, uid)
                if not pending:
                    database().execute('DELETE FROM blackjack_seats WHERE user_id = ?', (g.user['id'],))
                store.save(database(), state, balances, command='leave')
        if request.form.get('navigate') == 'card_tables':
            return redirect(url_for('card_tables'))
        return reply()

    @app.post('/karten/blackjack/aktion')
    @login_required
    def blackjack_action():
        require_csrf()
        try:
            revision = int(request.form.get('revision', ''))
            amount = int(request.form['amount']) if request.form.get('amount') else None
        except ValueError:
            return reply('Bitte verwende einen gültigen Einsatz und aktualisiere den Tisch.', 400)
        try:
            with database():
                database().execute('BEGIN IMMEDIATE')
                state, balances, actual_revision = store.load(database())
                if revision != actual_revision:
                    raise game.GameError('Der Tisch hat sich geändert. Die aktuelle Ansicht wurde geladen.')
                seats = {str(r['user_id']):r['seat'] for r in database().execute('SELECT * FROM blackjack_seats')}
                command = request.form.get('action')
                if store.joining_blocked(state) and command in ('bet','refill'):
                    raise game.GameError('Der Testtisch wird beendet. Bitte stehe nach der laufenden Hand auf.')
                game.action(state, balances, seats, g.user['id'], command, amount)
                store.save(database(), state, balances, command=command)
        except game.GameError as error:
            return reply(str(error), 409)
        return reply()

    @app.get('/karten/blackjack/karte/<code>')
    def blackjack_card(code):
        if code not in {rank+suit for rank in game.RANKS for suit in game.SUITS}:
            abort(404)
        suit = dict(S='Spades', H='Hearts', D='Diamonds', C='Clubs')[code[-1]]
        path = Path(__file__).resolve().parent / 'offline-preview/card-comparison-v1/assets/kenney' / f'card{suit}{code[:-1]}.png'
        return send_file(path, mimetype='image/png', max_age=3600)
