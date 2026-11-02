"""Isolated local Guesstimate walkthrough with one explicitly simulated player."""
from argparse import ArgumentParser
from datetime import date, datetime
import os
from pathlib import Path
import secrets
import sqlite3
import sys
from threading import Thread
import time

ROOT = Path(__file__).resolve().parents[1]


def public_player():
    source = ROOT / 'runtime/pc-local/quiz.sqlite3'
    with sqlite3.connect(source.resolve().as_uri()+'?mode=ro', uri=True) as db:
        db.row_factory = sqlite3.Row
        row = db.execute("""SELECT u.display_name, c.avatar_id, c.plaque_id, c.background_id
                            FROM users u LEFT JOIN user_cosmetics c ON c.user_id=u.id
                            WHERE u.username='stormseed'""").fetchone()
        return dict(row) if row else dict(display_name='Stormseed', avatar_id='a05', plaque_id='p00', background_id='b00')


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8780)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error('Ungültiger lokaler Port.')
    directory = ROOT / 'runtime/blackjack-join-simulation'
    directory.mkdir(parents=True, exist_ok=True)
    database = directory / 'quiz.sqlite3'
    assert database.resolve().is_relative_to(directory.resolve())
    os.environ.update(QUIZ_DATABASE=str(database), QUIZ_MAIL_USER='', QUIZ_MAIL_TO='', QUIZ_LOCAL_DEVELOPMENT='0')
    sys.path[:0] = [str(ROOT), str(ROOT / '.deps')]
    from app import create_app
    from blackjack import take_seat
    import blackjack_game as game
    from blackjack_clock import start_blackjack_clock
    from flask import session
    from waitress import serve

    app = create_app(dict(DATABASE=str(database), SECRET_KEY=secrets.token_hex(32),
                          CARD_TABLE_ENABLED=True, LOCAL_DEVELOPMENT=False, BLACKJACK_SIMULATION=True,
                          BLACKJACK_FIXED_STAKE=500, BLACKJACK_TEST_START_BALANCE=10000, BLACKJACK_DEALER_PEEK=False,
                          SESSION_COOKIE_NAME='blackjack-join-simulation'))
    profile = public_player()
    with app.app_context():
        db = app.get_db()
        for username,name,avatar,plaque,background in [
            ('viewer-test',profile['display_name']+' · Test',profile['avatar_id'] or 'a00',profile['plaque_id'] or 'p00',profile['background_id'] or 'b00'),
            ('hugo-simulation','Hugo · simuliert','a01','p00','b00')]:
            if not db.execute('SELECT 1 FROM users WHERE username=?',(username,)).fetchone():
                uid = db.execute('INSERT INTO users (username,display_name,pin_hash,created_at) VALUES (?,?,?,?)',
                                 (username,name,'simulation-only',datetime.now().isoformat())).lastrowid
                db.execute('INSERT INTO user_cosmetics (user_id,avatar_id,plaque_id,background_id,updated_at) VALUES (?,?,?,?,?)',
                           (uid,avatar,plaque,background,datetime.now().isoformat()))
        db.commit()
        viewer = db.execute("SELECT id FROM users WHERE username='viewer-test'").fetchone()[0]
        bot = db.execute("SELECT id FROM users WHERE username='hugo-simulation'").fetchone()[0]
        state,balances,_ = game.load(db)
        if state['round']==0 and not state['players']:
            take_seat(db,bot,1)
            state,balances,_ = game.load(db)
            shoe = [rank+suit for _ in range(6) for suit in game.SUITS for rank in game.RANKS]
            opening = ['9S','6H','7D','KC']
            for card in opening:
                shoe.remove(card)
            game.SystemRandom().shuffle(shoe)
            state['shoe']=shoe+list(reversed(opening))
            seats={str(bot):1}
            game.action(state,balances,seats,bot,'bet',500)
            game.start(state,balances,seats)
            state['simulation_gate']=True
            game.save(db,state,balances);db.commit()

    def simulated_viewer():
        # This app owns a fresh test identity/cookie. It never reads or changes
        # the personal app's session key, PIN hashes or login cookie.
        session['user_id']=viewer
        session['login_recorded_on']=date.today().isoformat()
        session['show_catchup_prompt']=False
        session['missed_week_days']=[]
    app.before_request_funcs.setdefault(None,[]).insert(0,simulated_viewer)
    stop = start_blackjack_clock(app)

    def run_bot():
        waiting_until = 0
        last_turn = None
        while not stop.wait(.5):
            try:
                with app.app_context():
                    db=app.get_db()
                    with db:
                        db.execute('BEGIN IMMEDIATE')
                        state,balances,_=game.load(db)
                        seats={str(r['user_id']):r['seat'] for r in db.execute('SELECT * FROM blackjack_seats')}
                        if str(viewer) not in seats:
                            waiting_until=0
                            continue
                        if state.get('simulation_gate'):
                            if str(viewer) not in state['bets']:
                                waiting_until=0
                                continue
                            waiting_until=waiting_until or time.time()+4
                            if time.time()<waiting_until:
                                continue
                            state['simulation_gate']=False
                            game.action(state,balances,seats,bot,'stand')
                            game.save(db,state,balances)
                            last_turn=None
                            continue
                        turn=game.current(state)
                        player=game.participant(state,bot)
                        if (state['phase']=='insurance' and player and player['insurance'] is None):
                            command='no-insurance'
                        elif turn and turn[0]['uid']==str(bot):
                            command='stand' if game.value(turn[2]['cards'])[0]>=17 else 'hit'
                        else:
                            command=None
                        if command:
                            key=(state['round'],state['phase'],len(turn[2]['cards']) if turn else 0)
                            if key!=last_turn:
                                last_turn=key;waiting_until=time.time()+3
                            if time.time()>=waiting_until:
                                game.action(state,balances,seats,bot,command)
                                game.save(db,state,balances)
                                last_turn=None
                        elif str(bot) in seats and game.can_place_bet(state,bot):
                            if balances[str(bot)]<500 and state['phase'] in ('betting','result'):
                                game.action(state,balances,seats,bot,'refill')
                            amount=500
                            if balances[str(bot)]>=amount:
                                game.action(state,balances,seats,bot,'bet',amount)
                                game.save(db,state,balances)
            except Exception:
                app.logger.exception('Der simulierte Mitspieler konnte nicht weiterspielen.')
                stop.wait(3)

    Thread(target=run_bot,name='blackjack-simulated-hugo',daemon=True).start()
    print(f'Guesstimate Beitrittstest: http://127.0.0.1:{args.port}/',flush=True)
    print('Getrennter Teststand mit Hugo. Persönlicher Spielbestand unverändert.',flush=True)
    serve(app,host='127.0.0.1',port=args.port,threads=4)


if __name__=='__main__':
    main()
