"""Canonical player components and desks, with inert local example states."""
from copy import deepcopy
import json
from pathlib import Path
import re

from library_store import ROOT, InvalidDesign
from source_windows import SourceWindows, Fragments, digest
from source_indicators import SourceIndicators

FAMILIES = dict(profile='Profilfenster', lobby='Lobbyplätze', portrait='Kompakte Porträts',
                ranking='Ranglisten und Ergebnisse', desk='Spielerpulte', equipment='Pultmotive')
LOBBIES = [('party_lobby.html', 'Guesstimate Party', 'sandbox'), ('card_table_lobby.html', 'Playtable', 'sandbox'),
           ('dice_table_lobby.html', 'Würfeltisch', 'sandbox'), ('dice_table_lobby.html', 'Kniffel', 'kniffel'),
           ('dice_table_lobby.html', 'Mäxchen', 'maexchen'), ('conquest_lobby.html', 'Conquest', 'sandbox')]


def definitions(catalogs, captures):
    rows = []
    def add(model, family, title, template, target, game, state='', **options):
        rows.append(dict(model=model, family=family, title=title, template=template, target=target,
                         game=game, state=state, **options))
    for template, game in [('home.html', 'Guesstimate'), ('profile.html', 'Profil')]:
        add('profile-window', 'profile', 'Gemeinsames Profilfenster', template, {'class': 'variant-a-profile-canonical'}, game,
            'Mit Pokalen' if template == 'home.html' else 'Ausrüstung ansehen', source='templates/_profile_window.html',
            preview_root_width=430, preview_size=(640, 960))
    add('profile-window', 'profile', 'Gemeinsames Profilfenster', 'public_profile.html', {'class':'variant-a-profile-canonical'}, 'Spielerprofile',
        'Öffentlicher Auftritt', source='templates/_profile_window.html', preview_root_width=430, preview_size=(640,960),
        values=dict(profile=dict(id=2,display_name='Musterplatz 2',points=200,rank=2,stats=dict(rounds=2,best=120,average=100)),is_self=False))
    add('ranking-player', 'ranking', 'Gemeinsamer Ranglisteneintrag', 'players.html', {'class':'public-player-card'}, 'Spielerprofile',
        'Spielerübersicht', preview_root_width=560, preview_size=(640,360), values=dict(query='',player_count=2))
    plaques = {p['id']: p for p in [catalogs['DEFAULT_PLAQUE'], *catalogs['PLAQUE_CATALOG']]}
    for plaque in plaques.values():
        values = dict(workshop_plaque=plaque['id'])
        add('profile-window', 'profile', 'Gemeinsames Profilfenster', 'home.html', {'class': 'variant-a-profile-canonical'},
            'Guesstimate', 'Pultmotiv · ' + plaque['name'], source='templates/_profile_window.html', values=values,
            preview_root_width=430, preview_size=(640, 960))
        for template, game, cls in [('profile.html', 'Profil', 'profile-plaque-preview'), ('shop.html', 'Shop', 'plaque-only-preview')]:
            if template == 'shop.html' and plaque['id'] == catalogs['DEFAULT_PLAQUE']['id']:
                continue
            add('equipment-preview', 'equipment', 'Vorhandene Pultauswahl', template, {'class': cls}, game,
                plaque['name'], values=values, preview_root_width=340, preview_size=(640, 600))
    for template, game, mode in LOBBIES:
        roles = ['Host', 'Mitspieler', 'Reservierter Platz'] + (['Testarmee'] if game == 'Conquest' else [])
        for role in roles:
            add('lobby-player', 'lobby', 'Gemeinsamer Lobbyplatz', template,
                {'data-lobby-member': '1' if role == 'Host' else '2'}, game, role,
                source='templates/_lobby_room.html', source_target={'class': 'game-lobby-player'},
                values=dict(game_mode=mode, workshop_role=role), preview_root_width=280, preview_size=(640, 800))
    for phase, state in [('lobby', 'Lobby'), ('question', 'Antworten'), ('vote', 'Abstimmen'), ('review', 'Prüfen'), ('finale', 'Ergebnis')]:
        for member_id, role in [('1', 'Eigener Hostplatz'), ('2', 'Mitspieler')]:
            add('perfect-player', 'profile', 'Perfect-Spielerfenster', 'nerd_mode.html', {'class': 'perfect-player-window', 'data-member-id': member_id},
                'Perfect', state + ' · ' + role, source_target={'class': 'perfect-player-window'},
                values=dict(phase=phase), preview_size=(640, 360))
    for phase, label in [('lobby', 'Bereit'), ('question', 'Antwort steht'), ('vote', 'Gewählt')]:
        add('perfect-player', 'profile', 'Perfect-Spielerfenster', 'nerd_mode.html', {'class': 'perfect-player-window', 'data-member-id': '2'},
            'Perfect', 'Mitspieler · ' + label, source_target={'class': 'perfect-player-window'},
            values=dict(phase=phase, workshop_player_done=True), preview_size=(640, 360))
    for mode, game in [('sandbox', 'Würfeltisch'), ('kniffel', 'Kniffel'), ('maexchen', 'Mäxchen')]:
        for member_id, role in [('1', 'Eigener Hostplatz'), ('2', 'Mitspieler')]:
            add('dice-player', 'profile', 'Spielerfenster am Würfeltisch', 'dice_table_game.html', {'data-dice-player': member_id},
                game, role, source_target={'class': 'dice-game-player'}, values=dict(game_mode=mode), preview_size=(640, 600))
        add('dice-console', 'desk', 'Würfelpult', 'dice_table_game.html', {'class': 'dice-player-console'}, game,
            'Vorhandener Grundzustand', values=dict(game_mode=mode), preview_size=(960, 720))
    for key, title, cls in [('swimming', 'Schwimmt · am Zug', 'is-current-turn'),
                            ('two', 'Zwei Leben · reagiert', 'is-responder'), ('out', 'Ausgeschieden', 'is-eliminated')]:
        add('dice-player', 'profile', 'Spielerfenster am Würfeltisch', 'dice_table_game.html', {'data-dice-player': '2'},
            'Mäxchen', title, source_target={'class': 'dice-game-player'}, values=dict(game_mode='maexchen', workshop_life=key),
            player_life=key, player_class=cls, evidence_paths=['static/dice-table.js'], preview_size=(640, 600))
    add('kniffel-scores', 'ranking', 'Spielerwertung im Kniffelblock', 'dice_table_game.html', {'class': 'is-kniffel-sheet'},
        'Kniffel', 'Zwei Beispielspieler', values=dict(game_mode='kniffel'),
        capture_inner=({'data-kniffel-sheet': None}, 'kniffel-table'), evidence_paths=['static/dice-table.js'], preview_size=(640, 700))
    for count in (2, 4, 6):
        for role, target in [('Eigenes Pult', {'class': 'card-player-desk is-you'}), ('Fremdes Pult', {'class': 'card-player-desk seat-other-1'})]:
            add('playtable-desk', 'desk', 'Namenspult am Kartentisch', 'card_table_game.html', target, 'Playtable',
                str(count) + ' Plätze · ' + role, source_target=({'class': 'card-player-desk is-you'} if role == 'Eigenes Pult' else {'data-drop-zone': 'player:{{ player.id }}'}),
                values=dict(workshop_seats=count, workshop_desk_role=role), preview_root_width=460, preview_size=(960, 720))
    for template in ('home.html', 'result.html'):
        for board in ('daily', 'weekly', 'all', 'weekly_wins') if template == 'home.html' else ('daily', 'weekly', 'all'):
            for rank, state in [(1, 'Eigener Eintrag'), (2, 'Mitspieler'), (3, 'Freier Rang')]:
                add('ranking-player', 'ranking', 'Gemeinsamer Ranglisteneintrag', template,
                    {'class': 'rank-row ' + ('is-empty' if rank == 3 else 'rank-' + str(rank))}, 'Guesstimate',
                    ('Startseite' if template == 'home.html' else 'Ergebnisseite') + ' · ' + board + ' · ' + state,
                    source='templates/_leaderboard.html', source_target={'class': 'rank-row' + (' is-empty' if rank == 3 else '')},
                    source_occurrence=(1 if rank == 3 else 2) if template == 'result.html' else 0,
                    within={'data-leaderboard-panel': board}, values=dict(workshop_board=board), preview_root_width=560,
                    preview_size=(640, 360), preview_overflow='visible')
    for rank in (1, 2):
        add('party-result-player', 'ranking', 'Vorhandener Party-Ergebnisplatz', 'party_result.html', {'class': 'podium-' + str(rank)},
            'Guesstimate Party', 'Platz ' + str(rank) + ' · Altbestand', source_target={'_tag': 'li'},
            source_within={'class': 'party-podium'}, preview_root_width=320, preview_size=(640, 800))
    for own in (True, False):
        add('perfect-ranking-player', 'ranking', 'Perfect-Ergebniseintrag', 'nerd_mode.html',
            {'_tag': 'li', **({'class': 'is-you'} if own else {})}, 'Perfect', 'Eigener Eintrag' if own else 'Mitspieler',
            within={'class': 'perfect-leaderboard'}, source_target={'class': 'perfect-leaderboard'},
            values=dict(phase='finale', workshop_result_other=not own), preview_root_width=500)
    for key, capture in captures.items():
        add('conquest-winner' if key.startswith('winner-') else 'conquest-portrait', 'portrait',
            'Siegerporträt' if key.startswith('winner-') else 'Gemeinsames Armeeporträt', 'conquest_table.html',
            {'factory': 'createPlayerPortrait'}, 'Conquest', capture['label'], factory_capture=key,
            source='static/player-portrait.js', source_metadata=dict(factory='createPlayerPortrait', generated=True),
            evidence_paths=['offline-preview/conquest-2-5d-v1/turn-controls.js'], preview_overflow='visible')
    return rows


class SourcePlayers(SourceIndicators):
    element_kind = 'players'
    record_type = 'game-player'
    identifier_prefix = 'gameplayer-'
    model_prefix = 'player-'
    api_prefix = '/api/game-players/'
    preview_size = (640, 360)
    families = FAMILIES
    model_names = {'profile-window': 'Gemeinsames Profilfenster', 'equipment-preview': 'Gemeinsame Pultauswahl',
                   'lobby-player': 'Gemeinsamer Lobbyplatz', 'perfect-player': 'Perfect · Spielerfenster',
                   'dice-player': 'Würfelspiele · Spielerfenster', 'dice-console': 'Würfelspiele · Aktionspult',
                   'kniffel-scores': 'Kniffel · Spielerwertung', 'playtable-desk': 'Playtable · Namenspult',
                   'ranking-player': 'Gemeinsamer Ranglisteneintrag', 'party-result-player': 'Party · Ergebnisplatz (Altbestand)',
                   'perfect-ranking-player': 'Perfect · Ergebniseintrag', 'conquest-portrait': 'Conquest · Armeeporträt',
                   'conquest-winner': 'Conquest · Siegerporträt'}

    def __init__(self, buttons=None, root=ROOT):
        self.player_captures = json.loads(Path(__file__).with_name('generated-players.json').read_text(encoding='utf-8'))['captures']
        self.indicator_captures = json.loads(Path(__file__).with_name('generated-indicators.json').read_text(encoding='utf-8'))['captures']
        for capture in [*self.player_captures.values(), *self.indicator_captures.values()]:
            for source in capture['evidence']:
                if digest(Path(root) / source['path']) != source['sha256']:
                    raise InvalidDesign('Die Spielerquelle wurde geändert. Bitte die Aufnahme erneuern.')
        SourceWindows.__init__(self, buttons, root, definitions_list=[])
        self.definitions = definitions(self.catalogs, self.player_captures)
        for definition in self.definitions:
            self.register(definition)

    def context(self, definition):
        value = super().context(definition)
        patch = definition.get('values', {})
        if patch.get('workshop_plaque'):
            plaque = value['plaque_catalog'][patch['workshop_plaque']]
            value['cosmetics']['plaque_id'] = plaque['id']
            value['player_cosmetics']['plaque_id'] = plaque['id']
            value['owned_plaques'] = [plaque] if definition['template'] == 'profile.html' else []
            value['plaques'] = [plaque]
        if patch.get('workshop_role') == 'Reservierter Platz':
            value['lobby_players'][1]['status'] = 'away'
        if patch.get('workshop_role') == 'Testarmee':
            value['lobby_players'][1].update(virtual=True, user_id=None, army_name='Testarmee', color='#82c3ff')
        if patch.get('workshop_result_other'):
            value['leaderboard'] = list(reversed(value['leaderboard']))
        if patch.get('workshop_player_done'):
            value['member_states'][2].update(ready=True, answered=True, voted=True)
        if patch.get('workshop_seats'):
            count = patch['workshop_seats']
            players = [{**deepcopy(value['members'][0]), 'id': i, 'user_id': i,
                        'display_name': 'Musterplatz ' + str(i), 'seat': i} for i in range(1, count + 1)]
            value.update(members=players, member=players[0], other_members=players[1:])
        return value

    def register(self, definition):
        key = definition.get('factory_capture')
        if not key:
            return super().register(definition)
        capture = self.player_captures[key]
        d = deepcopy(definition)
        d['evidence_paths'] = sorted(set(d.get('evidence_paths', []) + [p['path'] for p in capture['evidence']]))
        source = self.read(d['source'])
        original = dict(line=source[:source.index('export function createPlayerPortrait')].count('\n') + 1, markup=capture['markup'])
        rendered = dict(markup=capture['markup'], ancestors=[dict(tag='main', attrs={'class': 'prototype'})])
        self.remember(d, original, rendered, [])

    def decorate(self, definition, rendered):
        rendered = super().decorate(definition, rendered)
        if definition.get('player_life'):
            fragment = Fragments(rendered['markup']).find({'data-maexchen-life': '2'})['markup']
            text = self.indicator_captures['maexchen-life-' + definition['player_life']]['values']['text']
            rendered['markup'] = rendered['markup'].replace(fragment, fragment[:fragment.find('>') + 1] + text + fragment[fragment.rfind('</'):])
            rendered['markup'] = rendered['markup'].replace('class="dice-game-player ', 'class="dice-game-player ' + definition['player_class'] + ' ', 1)
        return rendered

    def remember(self, definition, original, rendered, capture_keys=()):
        d = deepcopy(definition)
        images = ['static/' + p for p in re.findall(r'/static/([^\s\"\'()<>]+)', rendered['markup'])]
        d['evidence_paths'] = sorted(set(d.get('evidence_paths', []) +
                                        [p for p in images if (self.root / p).is_file()]))
        return super().remember(d, original, rendered, capture_keys)

    def report(self):
        assets = self.assets()
        uses = []
        for template in sorted(self.buttons.active_templates):
            path = 'templates/' + template
            for match in re.finditer(r'{{\s*(profile_window|player_identity|player_card)\(', self.read(path)):
                refs = [r['id'] for r in self.records.values() if r['definition']['template'] == template or
                        (r['snapshot']['source']['path'] == path and match[0] in r['snapshot']['markup'])]
                uses.append(dict(path=path, line=self.read(path)[:match.start()].count('\n') + 1,
                                 component=match[1], refs=refs))
        hooks = []
        classes = ('card-player-desk', 'dice-game-player', 'dice-player-console', 'perfect-player-window', 'rank-row')
        for template in sorted(self.buttons.active_templates):
            path = 'templates/' + template
            for element in Fragments(self.read(path)).elements:
                if not set((element['attrs'].get('class') or '').split()).intersection(classes):
                    continue
                refs = [a['id'] for a in assets if a['snapshot']['source']['path'] == path and element['markup'] in a['snapshot']['markup']]
                hooks.append(dict(path=path, line=element['line'], refs=refs))
        entries = [{**{k: v for k, v in a.items() if k not in ('snapshot', 'preview')},
                    'source': a['snapshot']['source'], 'evidence': a['snapshot']['evidence']} for a in assets]
        plaques = [self.catalogs['DEFAULT_PLAQUE'], *self.catalogs['PLAQUE_CATALOG']]
        return dict(schema=1, uses=len(assets), models=len({a['model_id'] for a in assets}), families=FAMILIES,
                    games=sorted({a['game'] for a in assets}), assets=entries, component_uses=uses, source_hooks=hooks,
                    uncovered=[u for u in [*uses, *hooks] if not u['refs']],
                    plaque_ids=sorted({p['id'] for p in plaques}), factory_examples=len(self.player_captures),
                    limits=['Neutral frozen samples; no accounts, equipment, games or DBs read or changed.',
                            'Canonical profile scene and portraits keep their whole composition.',
                            'Playtable keeps name-only desks; no new avatars in running quiz questions or countdowns.',
                            'Party result podium remains retained source inventory, not a new approved design.',
                            'Card hands, controls and values may also appear in their own element categories.',
                            'No editor or editor-option review; no game actions or automatic text fitting executed.'])
