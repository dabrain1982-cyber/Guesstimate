"""Input library using the same original-source preview as the window library."""
from copy import deepcopy
import json
import re

from library_store import ROOT, InvalidDesign
from source_windows import SourceWindows, Fragments, SURFACE, digest

FAMILIES = dict(text='Text und Zahlen', selection='Auswahlfelder', toggle='Schalter',
                range='Regler', compound='Zusammengesetzte Auswahl')


def definitions():
    rows = []
    def add(model, family, title, template, target, game, state='', **options):
        rows.append(dict(model=model, family=family, title=title, template=template,
                         target=target, game=game, state=state, **options))
    for template, usage, fields in [('login.html', 'Anmeldung', [('username', 'Spielername'), ('pin', 'PIN')]),
                                     ('register.html', 'Registrierung', [('username', 'Spielername'), ('pin', 'PIN'), ('pin_confirm', 'PIN wiederholen')])]:
        for name, title in fields:
            add('auth-field', 'text', title, template, {'name': name}, 'Zugang', usage, wrap='label')
    for template, game, fields in [
        ('party_lobby.html', 'Guesstimate Party', [('name', 'Lobbyname', 'text'), ('rounds', 'Anzahl der Runden', 'selection')]),
        ('card_table_lobby.html', 'Playtable', [('deck_size', 'Kartensatz', 'selection'), ('starting_points', 'Startpunkte', 'text')]),
        ('dice_table_lobby.html', 'Würfeltisch', [('dice_count', 'Würfelanzahl', 'selection'), ('use_cup', 'Verdecktes Würfeln', 'selection')]),
        ('conquest_lobby.html', 'Conquest', [('name', 'Lobbyname', 'text')])]:
        for name, title, family in fields:
            model = 'lobby-select' if family == 'selection' else 'lobby-number' if name == 'starting_points' else 'lobby-text'
            add(model, family, title, template, {'name': name}, game, wrap='label')
    add('conquest-victory', 'selection', 'Siegziel wählen', 'conquest_lobby.html', {'name': 'victory_mode'}, 'Conquest', wrap='fieldset')
    add('conquest-color', 'selection', 'Armeefarben wählen', 'conquest_lobby.html', {'name': 'color_1'}, 'Conquest',
        source_target={'name': 'color_{{ player.id }}'}, wrap='fieldset')
    add('perfect-name', 'text', 'Lobbyname', 'nerd_mode.html', {'class': 'perfect-lobby-name-editor'}, 'Perfect')
    add('perfect-goal-mode', 'selection', 'Spielende wählen', 'nerd_mode.html', {'class': 'perfect-goal-mode'}, 'Perfect')
    for mode, title in [('points', 'Zielpunktzahl'), ('time', 'Spielzeit')]:
        add('perfect-goal-value', 'selection', title, 'nerd_mode.html', {'data-goal-value-panel': mode}, 'Perfect',
            values=dict(workshop_goal=mode))
    for game, template in [('Guesstimate', 'question.html'), ('Guesstimate Party', 'party_question.html')]:
        for category, target, title, family, model in [
            ('multiple_choice', 'choice-grid', 'Antwortauswahl', 'selection', 'quiz-choice'),
            ('true_false', 'binary-grid', 'Wahr oder Falsch', 'selection', 'quiz-choice'),
            ('estimate', 'estimate-input', 'Schätzwert mit Einheit', 'text', 'quiz-estimate'),
            ('order', 'order-list', 'Reihenfolge sortieren', 'compound', 'quiz-order'),
            ('match', 'match-list', 'Begriffe zuordnen', 'compound', 'quiz-match')]:
            add(model, family, title, template, {'class': target}, game, 'Ausgangszustand',
                values=dict(workshop_category=category, feedback=None))
            if category in ('multiple_choice', 'true_false'):
                add(model, family, title, template, {'class': target}, game, 'Beispielauswahl',
                    checked_value='A' if category == 'multiple_choice' else 'true',
                    values=dict(workshop_category=category, feedback=None))
    add('perfect-answer', 'text', 'Antwort verfassen', 'nerd_mode.html', {'class': 'perfect-answer-form'}, 'Perfect',
        values=dict(phase='question'))
    for selected in (False, True):
        add('perfect-vote', 'selection', 'Antwort wählen', 'nerd_mode.html', {'class': 'perfect-answer-options'}, 'Perfect',
            'Beispielauswahl' if selected else 'Ungewählt', values=dict(phase='vote', workshop_vote=selected))
    for host in (True, False):
        add('perfect-review', 'selection', 'Weitere richtige Antworten anerkennen', 'nerd_mode.html',
            {'class': 'perfect-review-list'}, 'Perfect', 'Gastgeber' if host else 'Mitspieler · gesperrt',
            source_target={'class': 'perfect-review-list' if host else 'perfect-review-list is-readonly'},
            values=dict(phase='review', is_host=host))
    for target, model, family, title, wrap in [
        ({'data-bet-amount': None}, 'card-bet-range', 'range', 'Punkte bieten', None),
        ({'data-deal-count': None}, 'card-deal-range', 'range', 'Karten pro Person', 'label'),
        ({'class': 'card-note'}, 'card-note-input', 'text', 'Gemeinsamer Notizzettel', None)]:
        add(model, family, title, 'card_table_game.html', target, 'Playtable', wrap=wrap)
    for mode, game in [('sandbox', 'Würfeltisch'), ('kniffel', 'Kniffel'), ('maexchen', 'Mäxchen')]:
        for locked in (True, False):
            add('dice-camera-lock', 'toggle', 'Kamera fixieren', 'dice_table_game.html', {'class': 'dice-camera-lock'},
                game, 'Ein' if locked else 'Aus', values=dict(game_mode=mode, workshop_camera=locked))
    add('maexchen-claim', 'selection', 'Ansage wählen', 'dice_table_game.html', {'class': 'maexchen-claim-control'},
        'Mäxchen', values=dict(game_mode='maexchen'))
    for enabled in (False, True):
        add('profile-developer-toggle', 'toggle', 'Entwicklermodus', 'profile.html', {'name': 'developer_enabled'},
            'Profil', 'Ein' if enabled else 'Aus', wrap='label', values=dict(workshop_developer=enabled))
    add('conquest-camera-angle', 'range', 'Blickwinkel einstellen', 'conquest_table.html', {'id': 'angle'}, 'Conquest', source=SURFACE)
    add('conquest-country-picker', 'selection', 'Land mit Tastatur auswählen', 'conquest_table.html',
        {'id': 'territory-picker'}, 'Conquest', 'Vorhandener Initialzustand · gesperrt', source=SURFACE)
    for state in ('Verstärken', 'Einrücken', 'Festigen'):
        add('conquest-troop-amount', 'compound', 'Truppenanzahl mit Minus und Plus', 'conquest_table.html',
            {'class': 'amount-control'}, 'Conquest', state, source=SURFACE)
        add('conquest-deployment-range', 'range', 'Truppenanzahl mit Regler', 'conquest_table.html',
            {'id': 'deployment-slider'}, 'Conquest', state, source=SURFACE)
    add('conquest-dice-choice', 'selection', 'Angriffswürfel wählen', 'conquest_table.html',
        {'id': 'attack-dice-choice'}, 'Conquest', source=SURFACE,
        evidence_paths=['offline-preview/comic-ui-v1/components.js'])
    return rows


class SourceInputs(SourceWindows):
    element_kind = 'inputs'
    record_type = 'game-input'
    identifier_prefix = 'gameinput-'
    model_prefix = 'input-'
    api_prefix = '/api/game-inputs/'
    preview_size = (640, 360)
    families = FAMILIES
    model_names = {
        'auth-field': 'Zugang · Eingabefeld', 'lobby-text': 'Gemeinsames Lobbytextfeld',
        'lobby-number': 'Lobby · Zahlenfeld', 'lobby-select': 'Gemeinsame Lobbyauswahl',
        'perfect-goal-value': 'Perfect · Zielwert auswählen', 'quiz-choice': 'Quiz · Antwortauswahl',
        'quiz-estimate': 'Quiz · Schätzwert', 'quiz-order': 'Quiz · Reihenfolge', 'quiz-match': 'Quiz · Zuordnung',
        'dice-camera-lock': 'Würfelspiele · Kameraschalter', 'profile-developer-toggle': 'Profil · Schalter',
        'conquest-troop-amount': 'Conquest · Truppenanzahl mit Minus und Plus',
        'conquest-deployment-range': 'Conquest · Truppenregler'}

    def __init__(self, buttons=None, root=ROOT):
        super().__init__(buttons, root, definitions_list=definitions())

    def fragment(self, text, definition, original=False):
        parser = Fragments(text)
        target = definition.get('source_target', definition['target']) if original else definition['target']
        control = parser.find(target)
        wrap = definition.get('wrap')
        if not wrap:
            return control
        containers = [p for p in parser.elements if p['tag'] == wrap and p['start'] <= control['start'] and
                      p['start'] + len(p['markup']) >= control['start'] + len(control['markup'])]
        if not containers:
            raise InvalidDesign('Die ursprüngliche Eingabehülle wurde nicht gefunden.')
        return deepcopy(min(containers, key=lambda p: len(p['markup'])))

    def context(self, definition):
        value = super().context(definition)
        value['victories'] = dict(world='Welteroberung', missions='Geheime Aufträge')
        value['color_names'] = ['Gold', 'Rot', 'Blau']
        value['roster'] = [dict(id=1, display_name='Musterarmee 1', color_index=0),
                           dict(id=2, display_name='Musterarmee 2', color_index=1)]
        patch = definition.get('values', {})
        if 'workshop_camera' in patch:
            value['camera_preference']['locked'] = patch['workshop_camera']
        if 'workshop_developer' in patch:
            value['cosmetics']['developer_enabled'] = patch['workshop_developer']
        if patch.get('workshop_vote'):
            value['answer'] = dict(vote_locked_at=None, draft_vote_key='one')
        return value

    def decorate(self, definition, rendered):
        value = definition.get('checked_value')
        if value:
            rendered['markup'] = re.sub(r'(<input\b[^>]*\bvalue="' + re.escape(value) + r'"[^>]*)(>)',
                                        r'\1 checked\2', rendered['markup'], count=1)
        if definition['model'] == 'conquest-dice-choice':
            icons = json.loads(self.read('offline-preview/game-workshop-v1/generated-buttons.json'))['icons']
            if any(digest(self.root / p['path']) != p['sha256'] for p in icons['evidence']):
                raise InvalidDesign('Die vorhandenen Würfelsymbole müssen neu erfasst werden.')
            rendered['markup'] = rendered['markup'].replace('</button>', icons['dice'] + '</button>')
        return rendered

    def report(self):
        assets = self.assets()
        controls = []
        for path in [*('templates/' + name for name in sorted(self.buttons.active_templates)), SURFACE]:
            for control in Fragments(self.read(path)).elements:
                attrs = control['attrs']
                native = control['tag'] in ('input', 'select', 'textarea') and attrs.get('type') not in ('hidden', 'submit', 'button', 'reset')
                role = attrs.get('role') in ('radio', 'radiogroup', 'checkbox', 'switch', 'listbox', 'combobox')
                if native or role:
                    refs = [a['id'] for a in assets if a['snapshot']['source']['path'] == path and
                            control['markup'] in a['snapshot']['markup']]
                    controls.append(dict(path=path, line=control['line'], tag=control['tag'],
                                         type=attrs.get('type'), name=attrs.get('name'), id=attrs.get('id'), refs=refs))
        entries = [{**{k: v for k, v in a.items() if k not in ('snapshot', 'preview')},
                    'source': a['snapshot']['source'], 'evidence': a['snapshot']['evidence']} for a in assets]
        return dict(schema=1, uses=len(assets), models=len({a['model_id'] for a in assets}), families=FAMILIES,
                    scope='Local source controls and neutral examples; no game database, account or authentication action.',
                    games=sorted({a['game'] for a in assets}), assets=entries, source_controls=controls,
                    uncovered=[c for c in controls if not c['refs']],
                    grouping='Shared existing component or base class; constraints, content and states remain separate variants.',
                    limits=['Inert previews; no field interaction, validation, drag behavior, autosave or game actions run.',
                            'Password fields remain empty. No account, PIN, player input or game state is read.',
                            'Hidden transport fields are not design elements. Native browser controls retain platform appearance.',
                            'Source default bounds and disabled states are recorded as found; live game bounds may depend on state.',
                            'No input editor or editor-option approval is included.'])
