"""Read-only window library from mounted game sources, without app/DB imports.

Models refer to an existing component, never to visual similarity alone. Each
use/state keeps its own source evidence and rendered example in project snapshots.
"""
from __future__ import annotations

import ast
from copy import deepcopy
import hashlib
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re

from library_store import ROOT, InvalidDesign
from source_buttons import SourceButtons, VOID

SURFACE = 'offline-preview/conquest-2-5d-v1/table-surface.js'
FAMILIES = {'rules': 'Regeldialoge', 'decisions': 'Entscheidungsfenster',
            'inventory': 'Inventare', 'actions': 'Aktionsflächen'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def matches(attrs, target):
    return all(all(token in re.sub(r'{[%{].*?[%}]}', ' ', attrs.get(key) or '', flags=re.S).split() for token in value.split()) if key == 'class'
               else key in attrs if value is None else attrs.get(key) == value
               for key, value in target.items())


class Fragments(HTMLParser):
    """Keep exact original slices and ancestry, including nested same-tag nodes."""
    def __init__(self, text):
        super().__init__(convert_charrefs=False)
        self.text = text
        self.starts = [0] + [m.end() for m in re.finditer('\n', text)]
        self.stack, self.elements = [], []
        self.feed(text)

    def absolute_offset(self):
        line, column = self.getpos()
        return self.starts[line - 1] + column

    def handle_starttag(self, tag, attrs):
        row = dict(tag=tag, attrs=dict(attrs), start=self.absolute_offset(), line=self.getpos()[0],
                   ancestors=[dict(tag=p['tag'], attrs=p['attrs']) for p in self.stack])
        if tag in VOID:
            row['markup'] = self.get_starttag_text()
            self.elements.append(row)
        else:
            self.stack.append(row)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]['tag'] == tag:
                row = self.stack[i]
                row['markup'] = self.text[row['start']:self.text.find('>', self.absolute_offset()) + 1]
                self.elements.append(row)
                self.stack = self.stack[:i]
                break

    def find(self, target):
        rows = sorted((p for p in self.elements if matches(p['attrs'], target)), key=lambda p: p['start'])
        if not rows:
            raise InvalidDesign('Die Fensterquelle enthält den erwarteten Baustein nicht: ' + str(target))
        return deepcopy(rows[0])


class InertMarkup(HTMLParser):
    """Strip scripts, events, active URLs and hidden tokens from example markup."""
    def __init__(self, text, root=False):
        super().__init__(convert_charrefs=False)
        self.parts, self.skip, self.first = [], 0, root
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'iframe', 'object', 'embed'):
            self.skip += 1
        if self.skip:
            return
        attrs = dict(attrs)
        if tag == 'input' and attrs.get('type') == 'hidden':
            return
        attrs = {k: v for k, v in attrs.items()
                 if not k.lower().startswith('on') and k not in ('action', 'formaction', 'autofocus', 'srcdoc')}
        if tag == 'form':
            attrs.pop('method', None)
        if tag == 'a':
            attrs['href'] = '#'
        if self.first:
            self.first = False
            attrs.pop('hidden', None)
            attrs['class'] = (attrs.get('class', '') + ' workshop-window-root').strip()
            if tag == 'dialog':
                attrs['open'] = None
        self.parts.append('<' + tag + ''.join(' ' + k + ('' if v is None else '="' + escape(v, quote=True) + '"')
                                             for k, v in attrs.items()) + '>')

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if self.skip:
            if tag in ('script', 'iframe', 'object', 'embed'):
                self.skip -= 1
            return
        self.parts.append('</' + tag + '>')

    def handle_data(self, text):
        if not self.skip:
            self.parts.append(text)

    def handle_entityref(self, name):
        if not self.skip:
            self.parts.append('&' + name + ';')

    def handle_charref(self, name):
        if not self.skip:
            self.parts.append('&#' + name + ';')


def definitions():
    rows = []

    def add(model, family, title, template, target, game, state='', **options):
        rows.append(dict(model=model, family=family, title=title, template=template,
                         target=target, game=game, state=state, **options))

    for game, template, endpoint in [
        ('Guesstimate', 'home.html', 'home'), ('Guesstimate Party', 'party_lobby.html', 'party_lobby'),
        ('Perfect', 'nerd_index.html', 'nerd_index'), ('Playtable', 'card_table_game.html', 'card_table_game'),
        ('Würfeltisch', 'dice_table_game.html', 'dice_table_game'), ('Kniffel', 'dice_table_game.html', 'kniffel_game'),
        ('Mäxchen', 'dice_table_game.html', 'maexchen_game'), ('Conquest', 'conquest_lobby.html', 'conquest_lobby')]:
        add('rules-dialog', 'rules', 'Spielregeln', template, {'id': 'rules-dialog'}, game,
            'Vorhandener Regeltext', source='templates/base.html', endpoint=endpoint)
    add('catchup-dialog', 'decisions', 'Verpasste Runden wählen', 'home.html', {'class': 'catchup-dialog'}, 'Guesstimate')
    for tab, title in [('avatar', 'Avatare'), ('plaque', 'Pulte & Plaketten'),
                       ('background', 'Hintergründe'), ('phrase', 'Sprüche')]:
        add('profile-inventory', 'inventory', 'Profilinventar · ' + title, 'profile.html',
            {'data-profile-panel': tab}, 'Profil', title)
    for tab, title in [('avatars', 'Avatare'), ('plaques', 'Pulte & Plaketten'),
                       ('backgrounds', 'Hintergründe'), ('phrases', 'Sprüche')]:
        add('shop-inventory', 'inventory', 'Shopauswahl · ' + title, 'shop.html',
            {'data-shop-panel': tab}, 'Shop', title)
    for game, template, mode in [('Guesstimate Party', 'party_lobby.html', 'sandbox'),
                                  ('Playtable', 'card_table_lobby.html', 'sandbox'),
                                  ('Würfeltisch', 'dice_table_lobby.html', 'sandbox'),
                                  ('Kniffel', 'dice_table_lobby.html', 'kniffel'),
                                  ('Mäxchen', 'dice_table_lobby.html', 'maexchen'),
                                  ('Conquest', 'conquest_lobby.html', 'sandbox')]:
        for host in (True, False):
            add('lobby-controls', 'actions', 'Lobbyeinstellungen', template, {'class': 'game-lobby-controls'},
                game, 'Gastgeber' if host else 'Mitspieler', source='templates/_lobby_room.html',
                values=dict(game_mode=mode, workshop_host=host))
    for host, mode in [(True, 'points'), (True, 'time'), (False, 'points')]:
        add('perfect-settings', 'actions', 'Einstellungszettel', 'nerd_mode.html', {'class': 'perfect-settings-paper'},
            'Perfect', ('Gastgeber · ' + ('Punkte' if mode == 'points' else 'Zeit')) if host else 'Mitspieler',
            values=dict(is_host=host, workshop_goal=mode),
            source_target={'class': 'perfect-settings-paper'} if host else {'class': 'is-readonly'})
    for phase, title in [('countdown', 'Spielbeginn'), ('question', 'Antwort verfassen'), ('vote', 'Antwort wählen'),
                          ('review', 'Antworten anerkennen'), ('resolution', 'Auflösung'), ('finale', 'Endergebnis')]:
        add('perfect-card', 'decisions' if phase in ('vote', 'review') else 'actions', title,
            'nerd_mode.html', {'class': 'perfect-' + {'resolution': 'points', 'finale': 'final'}.get(phase, phase) + '-card'}, 'Perfect', title, values=dict(phase=phase))
    add('perfect-card', 'decisions', 'Antworten anerkennen', 'nerd_mode.html', {'class': 'perfect-review-card'},
        'Perfect', 'Mitspieler · wartet auf Gastgeber', values=dict(phase='review', is_host=False))
    for phase, paused, state in [('question', False, 'Frage läuft'), ('question', True, 'Pausiert'),
                                  ('vote', False, 'Antwortwahl läuft')]:
        add('perfect-host-controls', 'actions', 'Gastgeber-Aktionen', 'nerd_mode.html',
            {'class': 'perfect-host-round-controls'}, 'Perfect', state,
            values=dict(phase=phase, is_paused=paused))
    for game, template in [('Guesstimate', 'question.html'), ('Guesstimate Party', 'party_question.html')]:
        for category in ('true_false', 'multiple_choice', 'match', 'order', 'estimate'):
            add('quiz-answer-form', 'actions', 'Antwortfläche', template, {'class': 'answer-form'}, game,
                dict(true_false='Wahr / Falsch', multiple_choice='Auswahl', match='Zuordnen', order='Reihenfolge', estimate='Schätzen')[category],
                values=dict(workshop_category=category, feedback=None))
        for credit, title in [(1, 'Richtig'), (0.5, 'Teilweise richtig'), (0, 'Falsch')]:
            add('quiz-feedback', 'actions', 'Antwortauflösung', template, {'class': 'feedback-panel'}, game,
                title, values=dict(workshop_credit=credit))
    for target, model, family, title in [
        ({'class': 'card-player-desk'}, 'card-player-desk', 'inventory', 'Eigener Kartenbereich'),
        ({'class': 'card-piles'}, 'card-piles', 'actions', 'Karten austeilen und verwalten'),
        ({'class': 'card-bet-control'}, 'card-bet-control', 'actions', 'Punkte bieten'),
        ({'data-pot-request': None}, 'card-pot-request', 'decisions', 'Potübernahme bestätigen'),
        ({'class': 'card-note'}, 'card-note', 'actions', 'Gemeinsamer Notizzettel'),
        ({'class': 'card-room-actions'}, 'card-room-actions', 'actions', 'Tisch verlassen oder beenden')]:
        add(model, family, title, 'card_table_game.html', target, 'Playtable')
    for mode, game in [('sandbox', 'Würfeltisch'), ('kniffel', 'Kniffel'), ('maexchen', 'Mäxchen')]:
        add('dice-console', 'actions', 'Würfelaktionen', 'dice_table_game.html', {'class': 'dice-player-console'},
            game, game, values=dict(game_mode=mode))
        if mode != 'maexchen':
            add('dice-held', 'inventory', 'Behaltene Würfel', 'dice_table_game.html', {'class': 'dice-held-zone'},
                game, game, values=dict(game_mode=mode))
    add('kniffel-sheet', 'actions', 'Kniffelblock', 'dice_table_game.html', {'class': 'is-kniffel-sheet'},
        'Kniffel', 'Ergebniseintrag', values=dict(game_mode='kniffel'), dynamic='kniffel')
    for identifier, model, family, title in [
        ('mission-reveal', 'mission-reveal', 'decisions', 'Geheimer Auftrag'),
        ('turn-bar', 'turn-bar', 'actions', 'Kompakte Zugleiste'),
        ('combat-intent', 'combat-intent', 'actions', 'Angriff vorbereiten'),
        ('battle-result', 'battle-result', 'actions', 'Kampfergebnis'),
        ('turn-notice', 'turn-notice', 'actions', 'Zugbeginn'),
        ('turn-receipt', 'turn-receipt', 'inventory', 'Neue Länderkarte'),
        ('trade-panel', 'trade-panel', 'actions', 'Länderkarten tauschen'),
        ('victory-result', 'victory-result', 'actions', 'Endstand und nächste Partie'),
        ('error', 'conquest-error', 'actions', 'Ansicht erneut laden')]:
        add(model, family, title, 'conquest_table.html', {'id': identifier}, 'Conquest', source=SURFACE)
    for state in ('Verstärken', 'Einrücken', 'Festigen'):
        add('deployment-controls', 'actions', 'Truppen verschieben', 'conquest_table.html',
            {'id': 'deployment-controls'}, 'Conquest', state, source=SURFACE, deployment=state)
    for expanded in (False, True):
        add('card-hand', 'inventory', 'Eigene Länderkarten', 'conquest_table.html', {'id': 'card-hand'},
            'Conquest', 'Vergrößert · Karten auswählen' if expanded else 'Am eigenen Avatar',
            source=SURFACE, expanded=expanded)
    return rows


class SourceWindows:
    element_kind = 'windows'
    record_type = 'game-window'
    identifier_prefix = 'gamewindow-'
    model_prefix = 'window-'
    api_prefix = '/api/game-windows/'
    preview_size = (960, 720)
    families = FAMILIES
    model_names = {}

    def __init__(self, buttons=None, root=ROOT, definitions_list=None):
        self.root = Path(root)
        self.buttons = buttons or SourceButtons(self.root)
        self.env = self.buttons.env.overlay()
        self.env.globals = {**self.buttons.env.globals, 'get_flashed_messages': lambda **_: []}
        self.records, self.pages = {}, {}
        self.captures = json.loads(Path(__file__).with_name('generated-windows.json').read_text(encoding='utf-8'))['captures']
        for capture in self.captures.values():
            for source in capture['evidence']:
                if digest(self.root / source['path']) != source['sha256']:
                    raise InvalidDesign('Die dynamische Fensterquelle wurde geändert. Bitte die Fensteraufnahme erneuern.')
        self.catalogs = {}
        for statement in ast.parse(self.read('app.py')).body:
            if isinstance(statement, ast.Assign):
                for target in statement.targets:
                    if isinstance(target, ast.Name) and target.id in (
                        'AVATAR_CATALOG', 'PLAQUE_CATALOG', 'BACKGROUND_CATALOG',
                        'DEFAULT_AVATAR', 'DEFAULT_PLAQUE', 'DEFAULT_BACKGROUND'):
                        self.catalogs[target.id] = ast.literal_eval(statement.value)
        self.catalogs['PHRASE_CATALOG'] = [dict(id='example', name='Beispielspruch', text='Ein guter Zug beginnt hier.', price=250)]
        self.definitions = definitions() if definitions_list is None else definitions_list
        for definition in self.definitions:
            self.register(definition)

    def read(self, path):
        return (self.root / path).read_text(encoding='utf-8-sig')

    def context(self, definition):
        c = self.catalogs
        cosmetics = dict(avatar_id=c['DEFAULT_AVATAR']['id'], plaque_id=c['DEFAULT_PLAQUE']['id'],
                         background_id=c['DEFAULT_BACKGROUND']['id'], phrase_id='', developer_enabled=False)
        player = dict(id=1, user_id=1, display_name='Musterperson', name='Musterperson', seat=1,
                      cosmetics=cosmetics, currency_balance=0, score=100, ready=True, active=True,
                      avatar_id=cosmetics['avatar_id'], plaque_id=cosmetics['plaque_id'], rank=1, points=100)
        second = {**player, 'id': 2, 'user_id': 2, 'display_name': 'Musterplatz 2', 'name': 'Musterplatz 2', 'seat': 2}
        lobby = dict(id=1, name='Werkstatt-Beispiel', host_user_id=1, status='waiting', rounds=2, dice_count=5,
                     use_cup=True, deck_size=52, starting_points=100, revision=1, goal_mode='points', goal_value=1000,
                     army_count=3, setup_mode='random', victory_mode='world', max_players=6)
        result = dict(member_id=1, name='Musterperson', answer='Beispielantwort', points=100,
                      bluffs=1, voters=[], correct_vote=True, host_equivalent=False)
        values = dict(game_name='Stormseed´s Guesstimate', public_url='', share_image_url='', today_display='Werkstatt',
                      g=dict(user=dict(id=1, display_name='Musterperson')), request=dict(endpoint=definition.get('endpoint',
                      {'home.html': 'home', 'nerd_mode.html': 'nerd_mode'}.get(definition['template'], definition['template'].removesuffix('.html')))),
                      config=dict(PERFECT_MAX_PLAYERS=7, CARD_TABLE_ENABLED=True), player_cosmetics=cosmetics, cosmetics=cosmetics,
                      is_owner=True, is_host=True, is_active=True, phase='lobby', is_paused=False, lobby=lobby, member=player,
                      members=[player, second], lobby_players=[player, second], other_members=[second], players=[player, second],
                      capacity=6, active_count=2, can_start=True, can_develop=False, winner=None, total_points=0, currency_balance=0,
                      trophies=dict(daily=0, weekly=0, monthly=0, party=0), default_phrase='Beispielspruch',
                      owned_avatars=[c['DEFAULT_AVATAR'], c['AVATAR_CATALOG'][0]],
                      owned_plaques=[c['DEFAULT_PLAQUE'], c['PLAQUE_CATALOG'][0]],
                      owned_backgrounds=[c['DEFAULT_BACKGROUND'], c['BACKGROUND_CATALOG'][0]],
                      owned_phrases=[dict(id='example', name='Beispielspruch', text='Ein guter Zug beginnt hier.')],
                      avatars=c['AVATAR_CATALOG'][:2], plaques=c['PLAQUE_CATALOG'][:2], backgrounds=c['BACKGROUND_CATALOG'][:2],
                      phrases=c.get('PHRASE_CATALOG', [])[:2], owned_avatar_ids=[], owned_plaque_ids=[], owned_background_ids=[], owned_phrase_ids=[],
                      shop_avatars=c['AVATAR_CATALOG'][:2], shop_plaques=c['PLAQUE_CATALOG'][:2],
                      shop_backgrounds=c['BACKGROUND_CATALOG'][:2], shop_phrases=c.get('PHRASE_CATALOG', [])[:2],
                      deck_choices={32: '32 Karten', 52: '52 Karten'}, army_choices={3: 'Drei Armeen'},
                      camera_preference=dict(locked=True, camera={}), game_mode='sandbox', maexchen_values=['31', '42', '65', '11', '21'],
                      show_catchup_prompt=True, missed_week_days=[1, 2, 3], attempt=None, round_available=False,
                      leaderboards={k: [] for k in ('daily', 'weekly', 'all', 'weekly_wins')}, leaderboard=[player, second],
                      index=0, total=5, running_points=100, elapsed_seconds=0, timer_limit=60, timer_hold=5,
                      feedback_remaining_ms=0, equipped_phrase='Ein Beispiel in der Werkstatt.', category_label='Beispiel',
                      question=dict(category='multiple_choice', prompt='Beispielfrage in der Werkstatt',
                                    answer='Beispielauflösung', explanation='Beispiel für einen erklärenden Text.',
                                    options={'A':'Beispiel A', 'B':'Beispiel B'}, items=['Beispiel A', 'Beispiel B'],
                                    left=['Beispiel A', 'Beispiel B'], right=['Zuordnung A', 'Zuordnung B'], unit='Einheiten'),
                      feedback=dict(credit=1, points=100, order_correct_count=2, submitted_display='100', correct_display='100',
                                    difference_display='0', response_seconds=4.2), round=dict(category='term'), answer=None, answer_text='',
                      table_config={}, display_items=['Beispiel A', 'Beispiel B', 'Beispiel C'],
                      match_options=['Zuordnung A', 'Zuordnung B'],
                      host_review_answers=[dict(id=1, answer_text='Beispielantwort', display_name='Musterperson')],
                      options=[dict(key='one', text='Beispielantwort A', author_member_id=2), dict(key='two', text='Beispielantwort B', author_member_id=3)],
                      resolution=dict(answer='Beispielauflösung', explanation='Erklärung des Beispiels.', solution_voters=[], results=[result]), goal_reached=False)
        for name, key, default in [('avatar_catalog', 'AVATAR_CATALOG', 'DEFAULT_AVATAR'),
                                   ('plaque_catalog', 'PLAQUE_CATALOG', 'DEFAULT_PLAQUE'),
                                   ('background_catalog', 'BACKGROUND_CATALOG', 'DEFAULT_BACKGROUND')]:
            values[name] = {v['id']: v for v in [c[default], *c[key]]}
        values['phrase_catalog'] = {}
        patch = definition.get('values', {})
        values.update(patch)
        if 'workshop_host' in patch:
            values['g']['user']['id'] = 1 if patch['workshop_host'] else 2
        if 'is_host' in patch:
            values['g']['user']['id'] = 1 if patch['is_host'] else 2
        if patch.get('phase', 'lobby') != 'lobby':
            lobby['status'] = 'completed' if patch['phase'] == 'finale' else 'playing'
            values['round']['phase'] = patch['phase']
        if 'workshop_goal' in patch:
            lobby['goal_mode'] = patch['workshop_goal']
            lobby['goal_value'] = 15 if patch['workshop_goal'] == 'time' else 1000
        if 'workshop_category' in patch:
            values['question']['category'] = patch['workshop_category']
        if 'workshop_credit' in patch:
            values['feedback']['credit'] = patch['workshop_credit']
        return values

    def dependencies(self, template):
        todo, seen = [template], set()
        while todo:
            name = todo.pop()
            if name in seen:
                continue
            seen.add(name)
            todo.extend(self.buttons.template_dependencies.get(name, ()))
        return ['templates/' + name for name in sorted(seen)]

    def fragment(self, text, definition, original=False):
        return Fragments(text).find(definition.get('source_target', definition['target']) if original else definition['target'])

    def decorate(self, definition, rendered):
        return rendered

    def register(self, definition):
        d = definition
        source_path = d.get('source', 'templates/' + d['template'])
        original = self.fragment(self.read(source_path), d, original=True)
        if source_path == SURFACE:
            rendered = deepcopy(original)
            markup = rendered['markup']
            texts = {'mission-text': 'Beispielauftrag · nur eine Vorschau, kein persönlicher Auftrag.',
                     'deployment-land': 'Beispielland', 'deployment-available': '6 Truppen verfügbar',
                     'deployment-preview': 'Vorschau: 1 Truppe', 'attack-source-name': 'Eigenes Land',
                     'attack-target-name': 'Nachbarland', 'attack-source-strength': '5', 'attack-target-strength': '2',
                     'battle-summary': 'Beispielwurf', 'battle-outcome': 'Beispiel für das Kampfergebnis.',
                     'turn-notice-detail': 'Dein Zug beginnt. Dies ist ein neutrales Beispiel.',
                     'turn-receipt-detail': 'Beispiel für eine erhaltene Länderkarte.',
                     'victory-title': 'Musterperson gewinnt!', 'victory-reason': 'Beispiel für einen abgeschlossenen Feldzug.',
                     'victory-stats': '42 Länder · Beispielwerte', 'error-detail': 'Beispiel für einen Ladefehler.'}
            for identifier, text in texts.items():
                markup = re.sub(r'(<[\w-]+\b[^>]*\bid="' + identifier + r'"[^>]*>)(.*?)(</[\w-]+>)',
                                lambda m: m[1] + escape(text) + m[3], markup, flags=re.S)
            if 'expanded' in d:
                markup = markup.replace('data-expanded="false"', 'data-expanded="' + str(d['expanded']).lower() + '"')
            if d.get('deployment'):
                markup = markup.replace('Eigenes Land verstärken', d['deployment'])
                markup = markup.replace('1 Truppe setzen', {'Verstärken': '1 Truppe setzen', 'Einrücken': 'Einrücken', 'Festigen': 'Verschieben'}[d['deployment']])
            rendered['markup'] = markup
            rendered['ancestors'] = [dict(tag='main', attrs={'class': 'prototype'}), *rendered['ancestors']]
        else:
            context = self.context(d)
            key = (d['template'], json.dumps(d.get('values', {}), sort_keys=True), d.get('endpoint'))
            if key not in self.pages:
                self.pages[key] = self.env.get_template(d['template']).render(**context)
            rendered = self.fragment(self.pages[key], d)
        capture_keys = []
        def content(target, capture_key):
            nonlocal rendered
            fragment = Fragments(rendered['markup']).find(target)
            opening = fragment['markup'].find('>') + 1
            closing = fragment['markup'].rfind('</')
            replacement = fragment['markup'][:opening] + self.captures[capture_key]['markup'] + fragment['markup'][closing:]
            rendered['markup'] = rendered['markup'].replace(fragment['markup'], replacement, 1)
            capture_keys.append(capture_key)
        if d['model'] == 'card-hand':
            content({'id': 'hand-cards'}, 'hand-expanded' if d['expanded'] else 'hand-collapsed')
            if d['expanded']:
                rendered['markup'] = re.sub(r'(<(?:button|section)\b[^>]*id="(?:cards-toggle|trade-panel)"[^>]*?)\s+hidden', r'\1', rendered['markup'])
                rendered['markup'] = rendered['markup'].replace('Drei Karten auswählen', 'Tauschen · +4')
        elif d['model'] == 'turn-receipt':
            content({'id': 'awarded-card'}, 'awarded-card')
        elif d['model'] == 'kniffel-sheet':
            content({'data-kniffel-sheet': None}, 'kniffel')
        elif d['model'] == 'dice-held':
            content({'data-dice-held': None}, 'dice-held')
        elif d['model'] == 'dice-console' and d['game'] != 'Mäxchen':
            content({'data-dice-tray': None}, 'dice-tray')
        elif d['model'] == 'card-player-desk':
            content({'data-card-layer': 'player:1'}, 'playtable-card')
        rendered = self.decorate(d, rendered)
        self.remember(d, original, rendered, capture_keys)

    def remember(self, d, original, rendered, capture_keys=()):
        source_path = d.get('source', 'templates/' + d['template'])
        styles = self.buttons.styles(d['template'])
        paths = set(self.dependencies(d['template']) + styles + [source_path] + d.get('evidence_paths', []))
        for key in capture_keys:
            paths.update(p['path'] for p in self.captures[key]['evidence'])
        evidence = [dict(path=p, sha256=digest(self.root / p)) for p in sorted(paths)]
        snapshot = dict(type=self.record_type, family=d['family'], model=d['model'],
                        source=dict(path=source_path, line=original['line'], target=d['target'], **d.get('source_metadata', {})),
                        markup=original['markup'], rendered_markup=''.join(InertMarkup(rendered['markup'], root=True).parts),
                        ancestors=rendered['ancestors'], captures=capture_keys,
                        styles=[dict(path=p, sha256=digest(self.root / p)) for p in styles],
                        evidence=evidence, example_values=True, game=d['game'], state=d['state'])
        identifier = self.identifier_prefix + hashlib.sha256(json.dumps(snapshot, sort_keys=True).encode()).hexdigest()[:24]
        self.records[identifier] = dict(id=identifier, definition=d, snapshot=snapshot)

    def assets(self):
        return [dict(kind=self.element_kind, id=r['id'], name=(r['definition']['game'] + ' · ' + r['definition']['title'] +
                     (' · ' + r['definition']['state'] if r['definition']['state'] and
                      r['definition']['state'] != r['definition']['game'] and
                      not r['definition']['title'].endswith(r['definition']['state']) else ''))[:100],
                     representation='2d', source='game', variant='source', family=r['definition']['family'],
                     family_name=self.families[r['definition']['family']], model_id=self.model_prefix + r['definition']['model'],
                     model_name=self.model_name(r['definition']['model']), game=r['definition']['game'],
                     games=[r['definition']['game']], usage=r['definition']['title'], context_state=r['definition']['state'],
                     preview=self.api_prefix + r['id'] + '/preview', editable=False,
                     preview_width=self.preview_size_for(r['definition'])[0], preview_height=self.preview_size_for(r['definition'])[1],
                     snapshot=deepcopy(r['snapshot'])) for r in self.records.values()]

    def preview_size_for(self, definition):
        return tuple(definition.get("preview_size", self.preview_size))

    def model_name(self, model):
        names = {'rules-dialog': 'Gemeinsamer Regeldialog', 'profile-inventory': 'Profilinventar',
                 'shop-inventory': 'Shopauswahl', 'lobby-controls': 'Gemeinsame Lobbyeinstellungen',
                 'perfect-settings': 'Perfect · Einstellungszettel', 'perfect-card': 'Perfect · Spielkarte',
                 'quiz-answer-form': 'Quiz · Antwortfläche', 'quiz-feedback': 'Quiz · Antwortauflösung',
                 'dice-console': 'Würfelspiele · Aktionspult', 'dice-held': 'Würfelspiele · Behaltene Würfel',
                 'deployment-controls': 'Conquest · Truppen verschieben', 'card-hand': 'Conquest · Eigene Länderkarten'}
        return self.model_names.get(model) or names.get(model) or next(d['game'] + ' · ' + d['title'] for d in self.definitions if d['model'] == model)

    def preview(self, identifier):
        record = self.records.get(identifier)
        if record is None:
            raise InvalidDesign('Dieses Fenster ist nicht registriert. Bitte die Bibliothek neu laden.')
        snapshot = record['snapshot']
        for source in snapshot['evidence']:
            if digest(self.root / source['path']) != source['sha256']:
                raise InvalidDesign('Die Fensterquelle wurde geändert. Bitte die Werkstatt neu laden.')
        def url(path):
            if path.startswith('static/'):
                return '/shared/' + path.removeprefix('static/')
            if path == 'offline-preview/button-workshop-v1/materials.css':
                return '/button-editor/materials.css'
            return '/conquest-source/' + path.removeprefix('offline-preview/conquest-2-5d-v1/')
        links = ''.join('<link rel="stylesheet" href="' + escape(url(s['path'])) + '?source_sha=' + s['sha256'] + '">' for s in snapshot['styles'])
        ancestors = [p for p in snapshot['ancestors'] if p['tag'] not in ('html', 'head', 'body', 'script', 'style')]
        wrappers = ''.join('<' + p['tag'] + ' class="window-ancestor ' + escape(p['attrs'].get('class', ''), quote=True) + '"' +
                           (' id="' + escape(p['attrs']['id'], quote=True) + '"' if p['attrs'].get('id') else '') + '>' for p in ancestors)
        ends = ''.join('</' + p['tag'] + '>' for p in reversed(ancestors))
        body_class = next((p['attrs'].get('class', '') for p in snapshot['ancestors'] if p['tag'] == 'body'), '')
        page = '<!doctype html><html lang="de"><meta charset="utf-8"><meta name="viewport" content="width=960"><title>' + escape(record['definition']['title']) + '</title>' + links + '''<style>
html,body{margin:0!important;width:960px!important;min-height:720px!important;height:auto!important;background:#142439!important;overflow:auto!important}body{padding:28px!important;box-sizing:border-box!important;display:grid!important;place-items:center!important}body:before,body:after{display:none!important}.window-ancestor{display:contents!important}.window-ancestor:before,.window-ancestor:after{display:none!important}.workshop-window-root{position:relative!important;inset:auto!important;margin:0!important;transform:none!important;max-height:664px!important;overflow:auto!important}.workshop-window-root[hidden]{display:block!important}dialog.workshop-window-root{display:block!important}#card-hand.workshop-window-root{--hand-x:0px;--hand-y:0px} .workshop-window-root:empty:after{content:'Leere Ablage · Inhalt entsteht im Spiel';display:block;padding:30px}
</style><body inert class="''' + escape(body_class, quote=True) + '">' + wrappers + snapshot['rendered_markup'] + ends + '</body></html>'
        if record['definition'].get('preview_background') == 'source':
            body_style = next((p['attrs'].get('style', '') for p in snapshot['ancestors'] if p['tag'] == 'body'), '')
            page = page.replace('background:#142439!important;', '').replace('body:before,body:after{display:none!important}', '')
            page = page.replace('<body inert class=', '<body inert style="' + escape(body_style, quote=True) + '" class=')
        if record['definition'].get('preview_overflow') == 'visible':
            page = page.replace('max-height:664px!important;overflow:auto!important', 'max-height:664px!important;overflow:visible!important')
        elif record['definition'].get('preview_overflow') == 'source':
            page = page.replace('max-height:664px!important;overflow:auto!important', 'max-height:664px!important')
        # Size only the outer slot: query containers need the width their game
        # layout normally provides. Their canonical interior stays untouched.
        if record['definition'].get('preview_root_width'):
            root_width = int(record['definition']['preview_root_width'])
            page = page.replace('.workshop-window-root{position:', '.workshop-window-root{width:' + str(root_width) + 'px!important;position:')
        width, height = self.preview_size_for(record["definition"])
        return page.replace('width=960', 'width=' + str(width)).replace('width:960px', 'width:' + str(width) + 'px').replace('min-height:720px', 'min-height:' + str(height) + 'px').replace('max-height:664px', 'max-height:' + str(height - 56) + 'px')

    def http_get(self, handler, path):
        if not path.startswith(self.api_prefix):
            return False
        try:
            if not path.endswith('/preview'):
                raise InvalidDesign('Unbekannte Fensteransicht.')
            raw = self.preview(path.removeprefix(self.api_prefix).removesuffix('/preview')).encode('utf-8')
            handler.send_response(200)
            handler.send_header('Content-Type', 'text/html; charset=utf-8')
            handler.send_header('Content-Length', str(len(raw)))
            handler.send_header('Content-Security-Policy', "default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; script-src 'none'; form-action 'none'; frame-ancestors 'self'")
            handler.end_headers()
            handler.wfile.write(raw)
        except (ValueError, OSError) as error:
            handler.json_response({'error': str(error)}, 400)
        return True

    def report(self):
        assets = self.assets()
        dialogs = []
        for path in [*('templates/' + name for name in sorted(self.buttons.active_templates)), SURFACE]:
            for element in Fragments(self.read(path)).elements:
                if element['tag'] == 'dialog':
                    dialogs.append(dict(path=path, line=element['line'],
                                        identifier=element['attrs'].get('id') or element['attrs'].get('class')))
        registered = {(a['snapshot']['source']['path'],
                       a['snapshot']['source']['target'].get('id') or a['snapshot']['source']['target'].get('class')) for a in assets}
        entries = [{**{k: v for k, v in a.items() if k not in ('snapshot', 'preview')},
                    'source': a['snapshot']['source'], 'evidence': a['snapshot']['evidence'],
                    'captures': a['snapshot']['captures']} for a in assets]
        return dict(schema=1, scope='Local mounted sources and neutral examples; no app, account or game database opened.',
                    uses=len(assets), models=len({a['model_id'] for a in assets}), families=FAMILIES,
                    games=sorted({a['game'] for a in assets}), assets=entries,
                    mounted_templates=sorted(self.buttons.active_templates), dialogs=dialogs,
                    missing_dialogs=[d for d in dialogs if (d['path'], d['identifier']) not in registered],
                    grouping='Shared existing component/class; game, content and state stay individually selectable.',
                    limits=['Examples are inert component previews, not running game scenes.',
                            'Dynamic contents come from source-verified factory captures. Game event handlers and runtime button mounts do not run.',
                            'The existing rule texts are recorded as found; this task does not rewrite or correct game rules.',
                            'Window editing and editorial review of editor options remain separate work.'],
                    exclusions=[dict(path='static/conquest-table.js', reason='Unmounted legacy inventory; current table uses table-surface.js.'),
                                dict(path='static/card-table.js', reason='Native browser confirmations are behavior, not a designable HTML window.'),
                                dict(path='static/stormseeds-perfect.js', reason='Native leave confirmation belongs to browser behavior.'),
                                dict(reason='Profile portraits, whole lobbies/boards, individual cards, inputs, timers and loading indicators keep their own element families.')])
