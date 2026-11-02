"""Join and play the requested local lobby; the host always starts manually."""
from argparse import ArgumentParser
from http.cookiejar import CookieJar
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPCookieProcessor, ProxyHandler, Request, build_opener
import json
import os
import sqlite3
import time

from runner import ROOT, WORLD
from policy import choose_action

BASE = 'http://127.0.0.1:8767'
DATABASE = ROOT / 'runtime/conquest-hud-20261025/walkthrough.sqlite3'
OUT = ROOT / 'runtime/conquest-lobby6-20261025'
ROOM = '/karten/welteroberung/6'
HUMAN_USER = 6
BOT_USERS = (7, 8, 9)


def members():
    with sqlite3.connect(DATABASE.as_uri() + '?mode=ro', uri=True) as db:
        db.row_factory = sqlite3.Row
        lobby = db.execute('SELECT * FROM conquest_lobbies WHERE id=6').fetchone()
        if not lobby or lobby['host_user_id'] != HUMAN_USER:
            raise RuntimeError('Die erwartete lokale Stormseed-Lobby fehlt.')
        rows = db.execute('''SELECT cm.*, u.username FROM conquest_members cm
            JOIN users u ON u.id=cm.user_id WHERE cm.lobby_id=6 AND cm.status='active'
            ORDER BY cm.joined_at,cm.id''').fetchall()
        if any(row['user_id'] not in (HUMAN_USER, *BOT_USERS) or
               row['username'] != f'portrait-four-{row["user_id"] - 6}' for row in rows):
            raise RuntimeError('Die Lobby enthält andere als die freigegebenen Testkonten.')
        if not any(row['user_id'] == HUMAN_USER for row in rows):
            raise RuntimeError('Stormseed ist nicht mehr in der Testlobby.')
        return dict(lobby), [dict(row) for row in rows]


class Player:
    def __init__(self, seat, member=None):
        self.member = str(member) if member is not None else None
        self.client = build_opener(ProxyHandler({}), HTTPCookieProcessor(CookieJar()))
        with self.client.open(BASE + f'/test/four/{seat}', timeout=8) as response:
            if response.geturl() != BASE + '/karten/welteroberung/3':
                raise RuntimeError('Die Testanmeldung führte nicht zur ursprünglichen Prüfrunde.')

    def join(self):
        request = Request(BASE + ROOM + '/beitreten', data=urlencode({'csrf_token': 'portrait-test'}).encode())
        with self.client.open(request, timeout=8) as response:
            if response.geturl() != BASE + ROOM:
                raise RuntimeError('Der Testspieler konnte nicht beitreten.')

    def status(self):
        with self.client.open(BASE + ROOM + '/status', timeout=8) as response:
            return json.load(response)

    def act(self, revision, action, fields, human):
        if self.member is None or self.member == str(human):
            raise RuntimeError('Ein menschlicher Zug darf nicht automatisch gespielt werden.')
        request = Request(BASE + ROOM + '/aktion', data=urlencode(dict(
            fields, csrf_token='portrait-test', revision=revision, action=action)).encode(),
            headers={'Accept': 'application/json'})
        with self.client.open(request, timeout=8) as response:
            return json.load(response)


def prepare():
    lobby, rows = members()
    if lobby['status'] != 'waiting' or lobby['started_at'] or lobby['state_json']:
        raise RuntimeError('Die Runde läuft bereits; Vorbereitung ohne Änderung abgebrochen.')
    present = {row['user_id'] for row in rows}
    for seat, user in enumerate(BOT_USERS, 1):
        if user not in present:
            Player(seat).join()
    lobby, rows = members()
    if {row['user_id'] for row in rows} != {HUMAN_USER, *BOT_USERS}:
        raise RuntimeError('Die Testmitspieler sind noch nicht vollständig beigetreten.')
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'members.json').write_text(json.dumps(rows, indent=2), encoding='utf-8')
    print('Robin, Bela und Alex sind beigetreten. Die Lobby bleibt ungestartet.', flush=True)


def run():
    import msvcrt
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / 'runner.lock').open('a+b') as lock:
        if lock.tell() == 0:
            lock.write(b'0'); lock.flush()
        lock.seek(0)
        msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        lobby, rows = members()
        if {row['user_id'] for row in rows} != {HUMAN_USER, *BOT_USERS}:
            raise RuntimeError('Bitte zuerst die drei Testmitspieler beitreten lassen.')
        human = str(next(row['id'] for row in rows if row['user_id'] == HUMAN_USER))
        expected = {str(row['id']) for row in rows}
        players = {str(row['id']): Player(row['user_id'] - 6, row['id']) for row in rows if row['user_id'] in BOT_USERS}
        observer = next(iter(players.values()))
        (OUT / 'runner.pid').write_text(str(os.getpid()), encoding='ascii')
        print('Bereit: Warte auf Spiel starten durch Stormseed. Eigene Züge bleiben manuell.', flush=True)
        counters = {}; failures = 0; last_state = None
        while not (OUT / 'stop').exists():
            try:
                payload = observer.status()
                if payload['status'] in ('closed', 'abandoned'):
                    print('Lobby geschlossen; Simulation beendet.', flush=True); return
                if payload['status'] == 'waiting':
                    failures = 0
                else:
                    game = payload['game']
                    if game.get('winner'):
                        print('Partie beendet; Simulation stoppt.', flush=True); return
                    if {row['id'] for row in game['armies'] if row['id'] != 'neutral'} != expected:
                        raise RuntimeError('Die Teilnehmer der gestarteten Partie stimmen nicht überein.')
                    if last_state != 'playing':
                        print('Der Host hat gestartet. Simuliere nur Robin, Bela und Alex.', flush=True)
                    request = game.get('battle_request')
                    owner = str(request['defender'] if request else game['current_member_id'])
                    if owner in players:
                        player = players[owner]
                        if player is not observer:
                            payload = player.status(); game = payload['game']
                        key = (game['turn_number'], str(game['current_member_id']))
                        decision = choose_action(game, WORLD, human, counters.get(key, 0))
                        if decision:
                            member, action, fields = decision
                            if member != owner or member == human:
                                continue
                            result = player.act(payload['revision'], action, fields, human)
                            if action == 'attack': counters[key] = counters.get(key, 0) + 1
                            if action == 'pass': counters.pop(key, None)
                            print(json.dumps({'member': member, 'action': action, 'revision': result['revision']}), flush=True)
                    failures = 0
                last_state = payload['status']
            except HTTPError as error:
                if error.code != 409: raise
            except (URLError, TimeoutError, ConnectionError):
                failures += 1
                if failures >= 30: raise RuntimeError('Die lokale Vorschau ist nicht mehr erreichbar.')
            time.sleep(1)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--prepare', action='store_true')
    args = parser.parse_args()
    prepare() if args.prepare else run()
