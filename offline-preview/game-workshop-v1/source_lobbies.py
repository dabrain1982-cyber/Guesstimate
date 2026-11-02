"""Original lobby rooms and shared overviews, with frozen local fixtures."""
from copy import deepcopy
import re

from library_store import ROOT
from source_windows import SourceWindows, Fragments
from source_indicators import SourceIndicators

FAMILIES = dict(rooms='Standardlobbys', perfect='Perfect-Raum', overviews='Lobbyübersichten',
                rows='Lobbyzeilen', access='Erstellen und Rückwege', feedback='Leer- und Fehlerzustände')
GAMES = [('Guesstimate Party', 'party_index.html', 'party_lobby.html', 'party', 10),
         ('Playtable', 'card_table_index.html', 'card_table_lobby.html', 'cards', 6),
         ('Würfeltisch', 'dice_table_index.html', 'dice_table_lobby.html', 'sandbox', 6),
         ('Kniffel', 'dice_table_index.html', 'dice_table_lobby.html', 'kniffel', 6),
         ('Mäxchen', 'dice_table_index.html', 'dice_table_lobby.html', 'maexchen', 6),
         ('Perfect', 'nerd_index.html', 'nerd_mode.html', 'perfect', 7),
         ('Conquest', 'conquest_index.html', 'conquest_lobby.html', 'conquest', 6)]
ROW_STATES = [('open', 'Offen · beitreten'), ('full', 'Voll · kein Beitritt'), ('own', 'Eigene wartende Lobby'),
              ('playing', 'Fremde laufende Partie'), ('own-playing', 'Eigene laufende Partie'),
              ('completed', 'Fremde beendete Partie'), ('own-completed', 'Eigenes Ergebnis')]
ROOM_STATES = [('host', 'Host · Einstellungen'), ('guest', 'Mitspieler · lesend'),
               ('alone', 'Host · allein'), ('full', 'Voll besetzte Lobby')]


def definitions():
    rows = []
    def add(model, family, title, template, target, game, mode, capacity, state, **options):
        values = dict(game_mode=mode, workshop_lobby_sample=state, workshop_capacity=capacity, **options.pop('values', {}))
        rows.append(dict(model=model, family=family, title=title, template=template, target=target, game=game,
                         state=options.pop('label', state), values=values, **options))
    for game, index, room, mode, capacity in GAMES:
        for state, label in [('mixed', 'Mehrere Lobbys und Zugänge'), ('empty', 'Keine Lobby'), ('error', 'Aktualisierung fehlgeschlagen')]:
            add('overview', 'overviews', 'Gemeinsame Lobbyübersicht', index, {'class': 'lobby-browser'}, game, mode, capacity, state,
                label=label, source='templates/_lobby_overview.html', preview_size=(1280, 1900 if state != 'empty' else 780),
                preview_root_width=1180, preview_background='source', preview_overflow='source', evidence_paths=['lobby_overview.py', 'static/lobby-overview.js'])
        states = ROW_STATES + ([('countdown', 'Startet gleich')] if game in ('Guesstimate Party', 'Perfect') else [])
        if game == 'Conquest':states += [('reserved', 'Reservierter Platz · zurückkehren'), ('closed', 'Geschlossen')]
        for state, label in states:
            add('overview-row', 'rows', 'Gemeinsame Lobbyzeile', index, {'class': 'lobby-browser-row'}, game, mode, capacity, state,
                label=label, source='templates/_lobby_overview.html', preview_root_width=1100, preview_size=(1200, 420))
        for model, family, title, target, state, label in [
            ('overview-toolbar', 'access', 'Listenheader mit Erstellen-Aktion', {'class': 'lobby-browser-toolbar'}, 'open', 'Lobby erstellen'),
            ('overview-empty', 'feedback', 'Leere Lobbyliste', {'class': 'lobby-browser-empty'}, 'empty', 'Keine Lobby'),
            ('overview-error', 'feedback', 'Fehler beim Aktualisieren', {'class': 'lobby-overview-error'}, 'error', 'Letzte Liste bleibt sichtbar')]:
            add(model, family, title, index, target, game, mode, capacity, state, label=label,
                source='templates/_lobby_overview.html', preview_root_width=1100, preview_size=(1200, 420))
        if game != 'Perfect':
            states = ROOM_STATES + ([('reserved', 'Platz reserviert'), ('return', 'Eigene Partie fortsetzen'),
                                     ('playing', 'Laufende Partie'), ('completed-host', 'Beendet · Host'),
                                     ('completed-guest', 'Beendet · Mitspieler'), ('closed', 'Lobby geschlossen')] if game == 'Conquest' else [])
            for state, label in states:
                add('standard-room', 'rooms', 'Gemeinsamer Lobbyraum', room, {'class': 'game-lobby'}, game, mode, capacity, state,
                    label=label, source='templates/_lobby_room.html', preview_root_width=1384,
                    preview_size=(1440, 1900 if game == 'Conquest' else 1600 if state == 'full' else 1350), preview_background='source', preview_overflow='source',
                    evidence_paths=['lobby_view.py', 'static/lobby.js'])
    for state, label, host, goal, ready, count in [
        ('host-waiting', 'Host · wartet auf Bereitschaft', True, 'points', False, 2),
        ('host-ready', 'Host · alle bereit', True, 'points', True, 2),
        ('host-time', 'Host · Spielzeit', True, 'time', True, 2),
        ('guest-waiting', 'Mitspieler · noch nicht bereit', False, 'points', False, 2),
        ('guest-ready', 'Mitspieler · bereit', False, 'points', True, 2),
        ('guest-time', 'Mitspieler · Spielzeit', False, 'time', False, 2),
        ('host-alone', 'Host · allein', True, 'points', False, 1),
        ('host-full', 'Voll besetzt · alle bereit', True, 'time', True, 7),
        ('countdown', 'Start-Countdown · feste 3', True, 'points', True, 2)]:
        add('perfect-room', 'perfect', 'Vorhandener Perfect-Raum', 'nerd_mode.html', {'class': 'perfect-room'},
            'Perfect', 'perfect', 7, state, label=label,
            values=dict(workshop_host=host, workshop_goal=goal, workshop_ready=ready, workshop_count=count,
                        phase='countdown' if state == 'countdown' else 'lobby'),
            preview_root_width=1384, preview_size=(1440, 1000), preview_background='source', preview_overflow='source',
            evidence_paths=['static/stormseeds-perfect.js'])
    return rows


class SourceLobbies(SourceIndicators):
    element_kind = 'lobby'
    record_type = 'game-lobby'
    identifier_prefix = 'gamelobby-'
    model_prefix = 'lobby-'
    api_prefix = '/api/game-lobbies/'
    families = FAMILIES
    model_names = {'overview': 'Gemeinsame Lobbyübersicht', 'overview-row': 'Gemeinsame Lobbyzeile',
                   'overview-toolbar': 'Gemeinsamer Listenheader', 'overview-empty': 'Gemeinsame leere Liste',
                   'overview-error': 'Gemeinsamer Aktualisierungshinweis', 'standard-room': 'Gemeinsamer Standardraum',
                   'perfect-room': 'Perfect · Raum mit Zettel und Buzzer'}

    def __init__(self, buttons=None, root=ROOT):
        SourceWindows.__init__(self, buttons, root, definitions_list=definitions())

    def context(self, definition):
        value = super().context(definition)
        patch = definition['values'];sample = patch['workshop_lobby_sample'];capacity = patch['workshop_capacity']
        mode = patch['game_mode'];game = definition['game'];lobby = value['lobby']
        if definition['model'].startswith('overview'):
            def entry(state, number=1):
                row = deepcopy(lobby)
                row.update(id=number, name='Beispiellobby ' + str(number), host_name='Musterhost', member_count=2,
                           player_limit=capacity, status='waiting', is_member=False, is_reserved=False)
                if state == 'full':row['member_count'] = capacity
                if state.startswith('own'):row['is_member'] = True
                if state in ('playing', 'own-playing', 'reserved'):row['status'] = 'playing'
                if state in ('completed', 'own-completed'):row['status'] = 'completed'
                if state in ('closed', 'countdown'):row['status'] = state
                if state == 'reserved':row['is_reserved'] = True
                return row
            value['lobbies'] = ([] if sample == 'empty' else
                                 [entry(s, i + 1) for i, s in enumerate(('open', 'full', 'own', 'playing', 'own-playing', 'own-completed'))]
                                 if sample in ('mixed', 'error') else [entry(sample)])
            if game == 'Conquest' and sample in ('mixed', 'error'):value['lobbies'].append(entry('reserved', 7))
            if mode in ('sandbox', 'kniffel', 'maexchen'):
                prefix = {'sandbox': 'dice_table', 'kniffel': 'kniffel', 'maexchen': 'maexchen'}[mode]
                value.update(lobby_endpoint=prefix + '_lobby', join_endpoint=prefix + '_join', create_endpoint=prefix + '_create')
            return value
        count = patch.get('workshop_count', capacity if sample == 'full' else 1 if sample == 'alone' else 2)
        players = []
        for index in range(count):
            p = deepcopy(value['members'][0]);identifier = index + 1
            p.update(id=identifier, user_id=identifier, display_name='Musterplatz ' + str(identifier),
                     name='Musterplatz ' + str(identifier), seat=identifier, ready=patch.get('workshop_ready', False), status='active')
            players.append(p)
        host = patch.get('workshop_host', sample not in ('guest', 'completed-guest'))
        current = players[0 if host or count == 1 else 1]
        value.update(members=players, lobby_players=players, players=players, other_members=players[1:], member=current,
                     roster=[{**p, 'color_index': i} for i, p in enumerate(players)], color_names=['Grün', 'Blau', 'Rot', 'Gelb', 'Violett', 'Orange'],
                     member_states={p['id']: dict(ready=p['ready'], answered=False, voted=False) for p in players},
                     capacity=capacity, active_count=count, is_host=host, history_count=0, waiting_for=None)
        value['g']['user']['id'] = current['user_id']
        lobby.update(host_user_id=1, member_count=count, player_limit=capacity, status='waiting', paused_at=None)
        if game == 'Conquest':
            if sample == 'reserved':players[1]['status'] = 'away'
            if sample in ('playing', 'return'):lobby['status'] = 'playing'
            if sample == 'return':value['is_active'] = False
            if sample.startswith('completed'):
                lobby['status'] = 'completed';value['winner'] = dict(name='Musterplatz 1', reason='Welteroberung · Beispiel')
            if sample == 'closed':lobby['status'] = 'closed'
        if game == 'Perfect':
            if sample == 'countdown':lobby['status'] = 'countdown';value['round'] = None
            value['can_start'] = len(players) >= 2 and all(p['ready'] for p in players[1:])
        return value

    def decorate(self, definition, rendered):
        if definition['values']['workshop_lobby_sample'] == 'error' and definition['model'] == 'overview':
            raw = Fragments(rendered['markup']).find({'class': 'lobby-overview-error'})['markup']
            opening, rest = raw.split('>', 1)
            rendered['markup'] = rendered['markup'].replace(raw, re.sub(r'\s+hidden(?:="[^"]*")?', '', opening) + '>' + rest, 1)
        return rendered

    def remember(self, definition, original, rendered, capture_keys=()):
        d = deepcopy(definition)
        body_style = ' '.join(p['attrs'].get('style', '') for p in rendered['ancestors'] if p['tag'] == 'body')
        paths = ['static/' + p for p in re.findall(r'/static/([^\s\"\'()<>]+)', rendered['markup'] + body_style)]
        d['evidence_paths'] = sorted(set(d.get('evidence_paths', []) + [p for p in paths if (self.root / p).is_file()]))
        return super().remember(d, original, rendered, list(capture_keys))

    def report(self):
        assets = self.assets();calls = []
        for template in sorted(self.buttons.active_templates):
            path = 'templates/' + template
            for match in re.finditer(r'{%\s*call\([^%]*?\)\s*(lobby_room|lobby_overview)\(', self.read(path)):
                refs = [r['id'] for r in self.records.values() if r['definition']['template'] == template]
                calls.append(dict(path=path, line=self.read(path)[:match.start()].count('\n') + 1, component=match[1], refs=refs))
        perfect = [a['id'] for a in assets if a['model_id'] == 'lobby-perfect-room']
        calls.append(dict(path='templates/nerd_mode.html', component='perfect-room', refs=perfect))
        return dict(schema=1, uses=len(assets), models=len({a['model_id'] for a in assets}), families=FAMILIES,
                    games=sorted({a['game'] for a in assets}), component_calls=calls, uncovered=[c for c in calls if not c['refs']],
                    assets=[{**{k: v for k, v in a.items() if k not in ('snapshot', 'preview')},
                             'source': a['snapshot']['source'], 'evidence': a['snapshot']['evidence']} for a in assets],
                    exclusions=[dict(game='Guesstimate', reason='Daily Quiz has no multiplayer lobby or lobby list; home/player components remain in their existing categories.')],
                    limits=['Frozen neutral rooms and lists; no DB, accounts, membership, polling, start or join actions.',
                            'Standard room and overview use their original shared macros; Perfect keeps its own room, paper and buzzer.',
                            'Source backgrounds and profile interiors preserved; workshop scales the whole preview.',
                            'Displayed source states do not certify backend transitions or every possible live state.',
                            'Existing generic lobby drafts/editor remain available; source rooms have no editor or option review.'])
