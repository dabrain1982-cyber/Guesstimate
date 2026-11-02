"""Local server clock; GETs stay read-only and browsers never advance rounds."""
import atexit
import json
from threading import Event, Thread
import time

import blackjack_game as game
import blackjack_store as store

BETTING_SECONDS = 20
RESULT_SECONDS = 10


def tick_clock(app, now=None, *, betting_seconds=BETTING_SECONDS, result_seconds=RESULT_SECONDS):
    now = time.time() if now is None else now
    with app.app_context():
        db = app.get_db()
        with db:
            db.execute('BEGIN IMMEDIATE')
            state, balances, revision = store.load(db)
            before = json.dumps(state, sort_keys=True)
            was_account = store.account_mode(state)
            store.configure_rules(db,state)
            if store.account_mode(state) != was_account:
                balances = store.balances_for(db,state,revision)
            if not state.get('clock', {}).get('automatic'):
                state['clock'] = dict(automatic=True, betting_seconds=betting_seconds,
                                      result_seconds=result_seconds)
            seats = {str(r['user_id']):r['seat'] for r in db.execute('SELECT * FROM blackjack_seats')}
            game.sync_clock(state, seats, now)
            clock = state['clock']
            ready = game.start_if_ready(state, balances, seats)
            if not ready and clock['deadline'] is not None and now >= clock['deadline']:
                if state['phase'] == 'betting':
                    if state['bets']:
                        game.start(state, balances, seats)
                    else:
                        clock['deadline'] = None
                elif state['phase'] == 'result':
                    game.begin_betting(state)
                    game.start_if_ready(state, balances, seats)
                game.sync_clock(state, seats, now)
            elif ready:
                game.sync_clock(state, seats, now)
            changed = before != json.dumps(state, sort_keys=True)
            if changed:
                store.save(db, state, balances)
            return changed


def start_blackjack_clock(app):
    if app.testing or not app.config.get('CARD_TABLE_ENABLED'):
        return None
    if 'blackjack_clock' in app.extensions:
        return app.extensions['blackjack_clock']
    stop = Event()
    # Initialize before accepting requests, including on a saved-table restart.
    tick_clock(app)

    def run():
        while not stop.wait(.5):
            try:
                tick_clock(app)
            except Exception:
                app.logger.exception('Die lokale Black-Jack-Tischuhr konnte nicht fortgesetzt werden.')
                stop.wait(5)

    thread = Thread(target=run, name='blackjack-table-clock', daemon=True)
    app.extensions['blackjack_clock'] = stop
    atexit.register(stop.set)
    thread.start()
    return stop
