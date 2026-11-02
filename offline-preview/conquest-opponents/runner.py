"""Local opponents for the existing four-player fixture on port 8767 only.

Moves go through the running game's normal authenticated action route.
This never opens the normal PC database and never starts/reseeds the fixture.
"""
from argparse import ArgumentParser
from contextlib import contextmanager
from datetime import datetime
from http.cookiejar import CookieJar
import json
import os
from pathlib import Path
import sqlite3
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPCookieProcessor, ProxyHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / '.deps'), str(ROOT)]
from policy import choose_action

DATABASE = ROOT / 'runtime/conquest-hud-20261025/walkthrough.sqlite3'
OUT = ROOT / 'runtime/conquest-opponents-20261025'
BASE = 'http://127.0.0.1:8767'
ROOM = '/karten/welteroberung/3'
HUMAN = '6'
WORLD = json.loads((ROOT / 'static/conquest/world.json').read_text(encoding='utf-8'))


@contextmanager
def single_runner():
    import msvcrt
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / 'runner.lock').open('a+b') as handle:
        if handle.tell() == 0:
            handle.write(b'0')
            handle.flush()
        handle.seek(0)
        try:
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            raise RuntimeError('Die simulierten Mitspieler laufen bereits.') from None
        try:
            yield
        finally:
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)


def fixture_members(db):
    members = db.execute('''SELECT cm.*, u.username, u.display_name FROM conquest_members cm
        JOIN users u ON u.id=cm.user_id WHERE cm.lobby_id=3 ORDER BY cm.id''').fetchall()
    expected = [(6, 6, 'portrait-four-0'), (7, 7, 'portrait-four-1'),
                (8, 8, 'portrait-four-2'), (9, 9, 'portrait-four-3')]
    if [(row['id'], row['user_id'], row['username']) for row in members] != expected or any(row['status'] != 'active' for row in members):
        raise RuntimeError('Abgebrochen: Dies ist nicht die erwartete Vier-Personen-Testrunde.')
    return members


def check_fixture(restart=False):
    # mode=rw refuses to create a missing database or silently pick another one.
    with sqlite3.connect(DATABASE.as_uri() + '?mode=rw', uri=True) as db:
        db.row_factory = sqlite3.Row
        db.execute('BEGIN IMMEDIATE')
        members = fixture_members(db)
        lobby = db.execute('SELECT * FROM conquest_lobbies WHERE id=3').fetchone()
        if not lobby or lobby['host_user_id'] not in {row['user_id'] for row in members}:
            raise RuntimeError('Abgebrochen: Gastgeber der Testrunde stimmt nicht überein.')
        if restart:
            from conquest import _prepare_automatic_state
            from conquest_turns import hydrate
            state = hydrate(_prepare_automatic_state(members, lobby['victory_mode']), WORLD, members, lobby['victory_mode'])
            state['developer_test'] = False
            db.execute('''UPDATE conquest_lobbies SET status='playing',state_json=?,
                started_at=?,completed_at=NULL,revision=revision+1 WHERE id=3''',
                (json.dumps(state, ensure_ascii=False, separators=(',', ':')),
                 datetime.now().isoformat(timespec='microseconds')))
            print('Testrunde neu gestartet: normale Startaufstellung, gleiche vier Spieler.', flush=True)
        db.commit()


class Player:
    def __init__(self, seat):
        self.member = str(6 + seat)
        self.client = build_opener(ProxyHandler({}), HTTPCookieProcessor(CookieJar()))
        # This fixture's explicit test-login creates a separate cookie jar per bot.
        with self.client.open(BASE + f'/test/four/{seat}', timeout=8) as response:
            if response.geturl() != BASE + ROOM:
                raise RuntimeError('Die lokale Testanmeldung führte nicht zur erwarteten Partie.')

    def status(self):
        with self.client.open(BASE + ROOM + '/status', timeout=8) as response:
            return json.load(response)

    def act(self, revision, action, fields):
        if self.member == HUMAN:
            raise RuntimeError('Eigene Züge werden nicht automatisiert.')
        payload = dict(fields, action=action, revision=revision, csrf_token='portrait-test')
        request = Request(BASE + ROOM + '/aktion', data=urlencode(payload).encode(), headers={'Accept': 'application/json'})
        with self.client.open(request, timeout=8) as response:
            return json.load(response)


def run(restart=False, interval=0.9):
    with single_runner():
        check_fixture(restart)
        players = {str(6 + seat): Player(seat) for seat in (1, 2, 3)}
        (OUT / 'runner.pid').write_text(str(os.getpid()), encoding='ascii')
        counters = {}
        failures = 0
        print('Robin, Bela und Alex spielen automatisch. Stormseed bleibt manuell.', flush=True)
        while not (OUT / 'stop').exists():
            try:
                payload = players['7'].status()
                game = payload.get('game')
                if not game:
                    raise RuntimeError('Die Testrunde ist nicht mehr aktiv.')
                if game.get('winner'):
                    print('Partie beendet; Simulation stoppt.', flush=True)
                    return
                request = game.get('battle_request')
                owner = str(request['defender'] if request else game['current_member_id'])
                if owner in players:
                    player = players[owner]
                    if owner != '7':
                        payload = player.status()
                        game = payload['game']
                    key = (game['round'], game['turn_number'], str(game['current_member_id']))
                    decision = choose_action(game, WORLD, HUMAN, counters.get(key, 0))
                    if decision:
                        member, action, fields = decision
                        if member != owner or member == HUMAN:
                            # Another request may have arrived between the two reads.
                            continue
                        result = player.act(payload['revision'], action, fields)
                        if action == 'attack':
                            counters[key] = counters.get(key, 0) + 1
                        if action == 'pass':
                            counters.pop(key, None)
                        print(json.dumps({'time': datetime.now().isoformat(timespec='seconds'), 'member': member,
                                          'action': action, 'fields': fields, 'revision': result['revision']}, ensure_ascii=False), flush=True)
                failures = 0
            except HTTPError as error:
                if error.code != 409:
                    raise RuntimeError(f'Spielaktion abgelehnt ({error.code}): {error.read().decode(errors="replace")[:500]}') from error
            except (URLError, TimeoutError, ConnectionError) as error:
                failures += 1
                if failures >= 10:
                    raise RuntimeError('Die lokale Testrunde ist nicht erreichbar. Simulation beendet.') from error
            time.sleep(interval)
        print('Simulation angehalten.', flush=True)


if __name__ == '__main__':
    parser = ArgumentParser(description='Lokale Mitspieler der Vier-Personen-Testrunde simulieren')
    parser.add_argument('--restart', action='store_true', help='Nur diese Testrunde mit den bisherigen Spielern neu starten')
    args = parser.parse_args()
    try:
        run(args.restart)
    except KeyboardInterrupt:
        print('Simulation angehalten.', flush=True)
    except Exception as error:
        print(str(error), file=sys.stderr, flush=True)
        raise SystemExit(1)
