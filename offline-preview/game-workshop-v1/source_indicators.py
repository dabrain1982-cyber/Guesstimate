"""Frozen score/time/status examples from the canonical local game components."""
from copy import deepcopy
from html import escape
import json
from pathlib import Path
import re

from library_store import ROOT, InvalidDesign
from source_windows import SourceWindows, Fragments, SURFACE, digest, matches

FAMILIES = dict(points='Punkte und Werte', timer='Timer', progress='Fortschritt',
                status='Status', counter='Zähler und Reserven', results='Ergebnisse')


def definitions():
    rows = []
    def add(model, family, title, template, target, game, state='', **options):
        rows.append(dict(model=model, family=family, title=title, template=template,
                         target=target, game=game, state=state, **options))
    for game, template in [('Guesstimate', 'question.html'), ('Guesstimate Party', 'party_question.html')]:
        add('quiz-round', 'progress', 'Fragenfortschritt und Punktestand', template, {'class': 'round-status'}, game,
            values=dict(feedback=None), preview_root_width=584, preview_overflow='visible')
        for elapsed, title in [(0, 'Volle Zeitpunkte'), (60, 'Zeitpunkte am Minimum')]:
            add('quiz-time', 'timer', 'Zeitpunkte', template, {'class': 'time-factor'}, game, title,
                values=dict(feedback=None), timer_capture='quiz-time-' + str(elapsed), evidence_paths=['static/timer.js'])
        for credit, title in [(1, 'Richtig'), (0.5, 'Teilweise richtig'), (0, 'Falsch')]:
            add('quiz-feedback', 'results', 'Punkte und Antwortzeit', template, {'class': 'feedback-panel'}, game,
                title, values=dict(workshop_credit=credit))
    for score in (100, 320, 500):
        add('quiz-score', 'points', 'Rundenergebnis', 'result.html', {'class': 'score-orbit'}, 'Guesstimate',
            str(score) + ' Punkte', values=dict(workshop_score=score))
    add('quiz-reward', 'points', 'Verdiente iKühe', 'result.html', {'class': 'currency-earned'}, 'Guesstimate')
    for movement, title in [(2, 'Aufgestiegen'), (-1, 'Abgestiegen'), (0, 'Unverändert')]:
        add('quiz-ranking-change', 'progress', 'Platzierung', 'result.html', {'class': 'result-belt'}, 'Guesstimate',
            title, values=dict(movement=movement))
    for template, game in [('home.html', 'Guesstimate'), ('result.html', 'Guesstimate')]:
        add('ranking-points', 'points', 'Ranglistenpunkte', template, {'class': 'identity-points'}, game,
            'Startseite' if template == 'home.html' else 'Ergebnisseite', source='templates/_player_identity.html')
    add('ranking-points', 'points', 'Gewonnene Wochen', 'home.html', {'class': 'identity-points'}, 'Guesstimate',
        'Siege statt Punkte', source='templates/_player_identity.html', within={'data-leaderboard-panel': 'weekly_wins'})
    add('ranking-rank', 'counter', 'Rangplatz', 'home.html', {'class': 'identity-rank'}, 'Guesstimate',
        source='templates/_player_identity.html')
    add('ranking-week-tally', 'progress', 'Gespielte Wochenrunden', 'home.html', {'class': 'player-week-tally'}, 'Guesstimate',
        source='templates/_player_identity.html', within={'data-leaderboard-panel': 'weekly'})
    add('profile-total', 'points', 'Insgesamt erspielte Punkte', 'profile.html', {'_tag': 'strong'}, 'Profil',
        within={'class': 'profile-hero-actions'})
    add('profile-trophies', 'counter', 'Erfolge und Titel', 'profile.html', {'class': 'trophy-grid'}, 'Profil', source='templates/_profile_trophies.html')
    for target, title in [({'class': 'shop-top-balance'}, 'Guthaben in der Navigation'), ({'class': 'shop-wallet'}, 'Guthaben im Shop')]:
        add('shop-wallet' if 'shop-wallet' in target.values() else 'shop-nav-balance', 'points', title, 'shop.html', target, 'Shop')
    for template, game, values in [('home.html', 'Guesstimate', {}), ('profile.html', 'Profil', {}),
                                    ('dice_table_game.html', 'Würfeltisch', dict(game_mode='sandbox')),
                                    ('dice_table_game.html', 'Kniffel', dict(game_mode='kniffel')),
                                    ('dice_table_game.html', 'Mäxchen', dict(game_mode='maexchen')),
                                    ('nerd_mode.html', 'Perfect', dict(phase='question'))]:
        add('profile-values', 'points', 'Spielerfenster mit Werten', template, {'class': 'variant-a-profile-canonical'}, game,
            'Spielpunkte' if game == 'Perfect' else 'Guthaben und vorhandener Kontext',
            values=values, source='templates/_profile_window.html', preview_size=(640, 960), preview_root_width=430)
    lobbies = [('party_lobby.html', 'Guesstimate Party', 'sandbox'), ('card_table_lobby.html', 'Playtable', 'sandbox'),
               ('dice_table_lobby.html', 'Würfeltisch', 'sandbox'), ('dice_table_lobby.html', 'Kniffel', 'kniffel'),
               ('dice_table_lobby.html', 'Mäxchen', 'maexchen'), ('conquest_lobby.html', 'Conquest', 'sandbox')]
    for template, game, mode in lobbies:
        for state, title in [('waiting', 'Offen'), ('playing', 'Partie läuft'), ('completed', 'Beendet')]:
            add('lobby-state', 'status', 'Lobbystatus', template, {'class': 'lobby-state'}, game, title,
                source='templates/_lobby_room.html', values=dict(game_mode=mode, workshop_lobby_state=state))
        add('lobby-occupancy', 'counter', 'Belegte Plätze', template, {'data-lobby-occupancy': None}, game,
            source='templates/_lobby_room.html', values=dict(game_mode=mode))
        for away, title in [(False, 'Am Tisch'), (True, 'Platz reserviert')]:
            add('profile-status', 'status', 'Spielerstatus im gemeinsamen Fenster', template, {'data-profile-status': None}, game,
                title, source='templates/_profile_window.html', values=dict(game_mode=mode, workshop_away=away))
    add('lobby-state', 'status', 'Lobbystatus', 'conquest_lobby.html', {'class': 'lobby-state'}, 'Conquest', 'Geschlossen',
        source='templates/_lobby_room.html', values=dict(workshop_lobby_state='closed'))
    for template, game, mode in [('party_index.html', 'Guesstimate Party', 'sandbox'), ('card_table_index.html', 'Playtable', 'sandbox'),
                                ('nerd_index.html', 'Perfect', 'sandbox'), ('dice_table_index.html', 'Würfeltisch', 'sandbox'),
                                ('dice_table_index.html', 'Kniffel', 'kniffel'), ('dice_table_index.html', 'Mäxchen', 'maexchen'),
                                ('conquest_index.html', 'Conquest', 'sandbox')]:
        for state, title in [('waiting', 'Offen'), ('full', 'Voll'), ('countdown', 'Startet gleich'), ('playing', 'Läuft'),
                              ('completed', 'Beendet'), ('closed', 'Geschlossen')]:
            add('overview-state', 'status', 'Status in der Lobbyübersicht', template, {'class': 'lobby-browser-state'}, game, title,
                source='templates/_lobby_overview.html', values=dict(game_mode=mode, workshop_overview_state=state))
        add('overview-error', 'status', 'Übersicht vorübergehend nicht aktualisiert', template, {'data-overview-error': None}, game,
            source='templates/_lobby_overview.html', values=dict(game_mode=mode))
    for template, game in [('party_lobby.html', 'Guesstimate Party'), ('card_table_lobby.html', 'Playtable'),
                            ('dice_table_lobby.html', 'Würfeltisch'), ('conquest_lobby.html', 'Conquest')]:
        add('lobby-save', 'status', 'Speicherhinweis', template, {'data-lobby-autosave': None}, game)
    for template, game in [('question.html', 'Guesstimate'), ('party_question.html', 'Guesstimate Party'),
                            ('card_table_game.html', 'Playtable'), ('dice_table_game.html', 'Würfeltisch'),
                            ('conquest_lobby.html', 'Conquest'), ('profile.html', 'Profil'), ('shop.html', 'Shop')]:
        add('shared-flash', 'status', 'Allgemeine Rückmeldung', template, {'class': 'flash-stack'}, game,
            source='templates/base.html', values=dict(workshop_flash=True))
    for count in (3, 1):
        add('party-countdown', 'timer', 'Start-Countdown', 'party_countdown.html', {'class': 'party-countdown-card'},
            'Guesstimate Party', str(count), sample_text=[({'data-party-countdown-number': None}, str(count))],
            evidence_paths=['static/party.js'])
    add('party-score-list', 'results', 'Vorhandene Ergebnisliste', 'party_result.html', {'class': 'party-podium'},
        'Guesstimate Party', 'Altbestand · keine neue Podiumgestaltung', preview_size=(960, 720))
    for phase, title in [('question', 'Antwort verfassen'), ('vote', 'Antwort wählen')]:
        for seconds, state in [(135, 'Normal'), (12, 'Dringend')]:
            add('perfect-timer', 'timer', 'Fragentimer', 'nerd_mode.html', {'data-timer': None}, 'Perfect', title + ' · ' + state,
                source_target={'class': 'perfect-timer'}, values=dict(phase=phase), clock_seconds=seconds,
                evidence_paths=['static/stormseeds-perfect.js'])
        add('perfect-warning', 'status', '30-Sekunden-Warnung', 'nerd_mode.html', {'data-time-warning': None}, 'Perfect', title,
            values=dict(phase=phase), visible_warning=True, evidence_paths=['static/stormseeds-perfect.js'])
    for seconds, title in [(95, 'Restzeit'), (0, 'Abgelaufen')]:
        add('perfect-game-timer', 'timer', 'Gesamte Spielzeit', 'nerd_mode.html', {'data-game-timer': None}, 'Perfect', title,
            values=dict(phase='question', workshop_goal='time'), game_clock_seconds=seconds, evidence_paths=['static/stormseeds-perfect.js'])
    add('perfect-pause', 'status', 'Spielpause', 'nerd_mode.html', {'class': 'perfect-paused-notice'}, 'Perfect',
        values=dict(phase='question', is_paused=True))
    add('perfect-countdown', 'timer', 'Start-Countdown', 'nerd_mode.html', {'data-countdown': None}, 'Perfect',
        values=dict(phase='countdown'))
    add('perfect-round-scores', 'points', 'Punkte der Runde', 'nerd_mode.html', {'class': 'perfect-round-scores'}, 'Perfect',
        values=dict(phase='resolution'))
    add('perfect-final-scores', 'results', 'Abschlusspunkte', 'nerd_mode.html', {'class': 'perfect-leaderboard'}, 'Perfect',
        values=dict(phase='finale'))
    add('perfect-flash', 'status', 'Rückmeldung', 'nerd_mode.html', {'class': 'perfect-flashes'}, 'Perfect',
        values=dict(phase='question', workshop_flash=True))
    for phase, title in [('lobby', 'Bereit / wartet'), ('question', 'Antwortstatus'), ('vote', 'Wahlstatus'), ('review', 'Gastgeber prüft')]:
        add('perfect-player-status', 'status', 'Spielerstatus', 'nerd_mode.html', {'class': 'perfect-player-status'}, 'Perfect',
            title, values=dict(phase=phase))
        add('perfect-player-status', 'status', 'Spielerstatus', 'nerd_mode.html', {'class': 'perfect-player-status'}, 'Perfect',
            title + ' · Mitspieler', values=dict(phase=phase), within={'data-member-id': '2'})
    add('perfect-player-status', 'status', 'Spielerstatus', 'nerd_mode.html', {'class': 'perfect-player-status'}, 'Perfect',
        'Mitspieler bereit', values=dict(phase='lobby', workshop_guest_ready=True), within={'data-member-id': '2'})
    add('perfect-answer-locked', 'status', 'Antwort eingeloggt', 'nerd_mode.html', {'class': 'perfect-locked-answer'}, 'Perfect',
        values=dict(phase='question', workshop_locked='answer'))
    add('perfect-vote-locked', 'status', 'Wahl eingeloggt', 'nerd_mode.html', {'class': 'perfect-vote-locked-note'}, 'Perfect',
        values=dict(phase='vote', workshop_locked='vote'))
    for selector, title, value, model, family in [
        ({'class': 'card-bankroll'}, 'Eigener Punktebestand', '100', 'card-bankroll', 'points'),
        ({'class': 'card-player-bid'}, 'Eigene gebotene Punkte', '10', 'card-bid', 'points'),
        ({'class': 'card-pot'}, 'Punkte im Pot', '30', 'card-pot', 'points'),
        ({'data-bet-output': None}, 'Ausgewähltes Gebot', '5', 'card-bet-output', 'points'),
        ({'data-deal-count-output': None}, 'Karten pro Person', '1', 'card-deal-output', 'counter'),
        ({'data-deck-count': None}, 'Karten im Stapel', '40', 'card-pile-count', 'counter'),
        ({'data-discard-count': None}, 'Karten auf der Ablage', '12', 'card-pile-count', 'counter')]:
        add(model, family, title, 'card_table_game.html', selector, 'Playtable', number_text=value,
            evidence_paths=['static/card-table.js'])
    for action, text in [('Einsammeln', 'Karten werden eingesammelt …'), ('Mischen', 'Ablagestapel wird gemischt …')]:
        add('card-action-status', 'status', 'Aktuelle Kartenaktion', 'card_table_game.html', {'data-action-banner': None},
            'Playtable', action, root_text=text, evidence_paths=['static/card-table.js'])
    add('card-pot-status', 'status', 'Rückmeldung zur Potfreigabe', 'card_table_game.html', {'data-pot-request-text': None},
        'Playtable', root_text='Warte auf die einstimmige Freigabe für 30 Punkte.', evidence_paths=['static/card-table.js'])
    for mode, game in [('sandbox', 'Würfeltisch'), ('kniffel', 'Kniffel'), ('maexchen', 'Mäxchen')]:
        add('dice-engine-status', 'status', 'Würfeltechnik', 'dice_table_game.html', {'data-dice-engine-status': None}, game,
            'Bereit', values=dict(game_mode=mode), root_text='3D-Würfel bereit · Kamera fixiert', evidence_paths=['static/dice-table.js'])
        for title, text in [('Bereit', 'Der Tisch ist bereit.'), ('Aktion fehlgeschlagen', 'Die Aktion konnte gerade nicht ausgeführt werden.')]:
            add('dice-message', 'status', 'Tischmeldung', 'dice_table_game.html', {'data-dice-message': None}, game, title,
                values=dict(game_mode=mode), root_text=text, evidence_paths=['static/dice-table.js'])
        add('dice-roll-result', 'results', 'Würfelergebnis', 'dice_table_game.html', {'data-dice-fallback': None}, game,
            'Neutrales Würfelergebnis', values=dict(game_mode=mode),
            capture_inner=({'data-dice-fallback': None}, 'dice-result-2' if mode == 'maexchen' else 'dice-result-5'),
            evidence_paths=['static/dice-table.js'])
    add('dice-history', 'results', 'Wurfnotizen', 'dice_table_game.html', {'aria-label': 'Notizzettel der Würfe'}, 'Würfeltisch',
        capture_inner=({'data-dice-history': None}, 'dice-history'), evidence_paths=['static/dice-table.js'])
    add('kniffel-sheet', 'points', 'Kniffelblock', 'dice_table_game.html', {'class': 'is-kniffel-sheet'}, 'Kniffel',
        values=dict(game_mode='kniffel'), capture_inner=({'data-kniffel-sheet': None}, 'kniffel-table'),
        evidence_paths=['static/dice-table.js'], preview_size=(640, 600))
    for count in (3, 2, 1):
        add('kniffel-rolls-left', 'counter', 'Verbleibende Würfe', 'dice_table_game.html', {'data-kniffel-lights': None}, 'Kniffel',
            str(count), values=dict(game_mode='kniffel'), capture_inner=({'data-kniffel-lights': None}, 'kniffel-lights-' + str(count)),
            evidence_paths=['static/dice-table.js'])
    for key, title in [('three', 'Drei Leben'), ('two', 'Zwei Leben'), ('swimming', 'Schwimmt'), ('out', 'Ausgeschieden')]:
        add('maexchen-lives', 'counter', 'Leben', 'dice_table_game.html', {'class': 'maexchen-life'}, 'Mäxchen', title,
            values=dict(game_mode='maexchen'), life_capture='maexchen-life-' + key, evidence_paths=['static/dice-table.js'])
    for target, title, text in [({'data-maexchen-announcement': None}, 'Ansage', 'Ansage: 42'),
                               ({'data-maexchen-order': None}, 'Zugreihenfolge', 'Musterplatz 1  →  Musterplatz 2')]:
        add('maexchen-announcement' if 'data-maexchen-announcement' in target else 'maexchen-order', 'status', title,
            'dice_table_game.html', target, 'Mäxchen', values=dict(game_mode='maexchen'), root_text=text, evidence_paths=['static/dice-table.js'])
    for identifier, model, family, title in [
        ('reinforcements-left', 'conquest-reserve', 'counter', 'Verfügbare Truppen'),
        ('turn-phase', 'conquest-phase', 'status', 'Aktuelle Phase'),
        ('battle-result', 'conquest-battle', 'results', 'Kampfergebnis'),
        ('turn-notice', 'turn-notice', 'status', 'Zugbeginn'),
        ('turn-receipt', 'turn-receipt', 'status', 'Erhaltene Länderkarte'),
        ('trade-feedback', 'conquest-trade-feedback', 'status', 'Kartentausch-Rückmeldung'),
        ('deployment-error', 'conquest-deployment-error', 'status', 'Mengenfehler'),
        ('victory-result', 'conquest-final', 'results', 'Endstand'),
        ('loading', 'conquest-loading', 'status', 'Tisch wird geladen'),
        ('error', 'conquest-error', 'status', 'Tisch nicht erreichbar'),
        ('angle-value', 'conquest-angle', 'counter', 'Aktueller Blickwinkel')]:
        target = {'class': 'reinforcement-reserve'} if identifier == 'reinforcements-left' else {'id': identifier}
        add(model, family, title, 'conquest_table.html', target, 'Conquest', source=SURFACE,
            evidence_paths=['offline-preview/conquest-2-5d-v1/turn-controls.js'])
    for title in ('Startaufstellung', 'Angreifen', 'Festigen', 'Zug beendet', 'Spiel beendet'):
        add('conquest-phase', 'status', 'Aktuelle Phase', 'conquest_table.html', {'id': 'turn-phase'}, 'Conquest', title,
            source=SURFACE, root_text=title, evidence_paths=['offline-preview/conquest-2-5d-v1/turn-controls.js'])
    for key, title in [('active', 'Am Zug'), ('waiting', 'Nicht am Zug'), ('out', 'Ausgeschieden')]:
        add('conquest-army-values', 'counter', 'Öffentliche Armeewerte', 'conquest_table.html', {'factory': 'createPlayerPortrait'},
            'Conquest', title, source='static/player-portrait.js', factory_capture='conquest-portrait-' + key,
            source_metadata=dict(factory='createPlayerPortrait', generated=True), preview_overflow='visible',
            evidence_paths=['offline-preview/conquest-2-5d-v1/turn-controls.js'])
    return rows


class SourceIndicators(SourceWindows):
    element_kind = 'indicators'
    record_type = 'game-indicator'
    identifier_prefix = 'gameindicator-'
    model_prefix = 'indicator-'
    api_prefix = '/api/game-indicators/'
    preview_size = (640, 360)
    families = FAMILIES
    model_names = {'quiz-round': 'Quiz · Fragenfortschritt und Punkte', 'quiz-time': 'Quiz · Zeitpunkte',
                   'quiz-feedback': 'Quiz · Punkte und Antwortzeit', 'profile-values': 'Gemeinsames Spielerfenster mit Werten',
                   'lobby-state': 'Gemeinsamer Lobbystatus', 'lobby-occupancy': 'Gemeinsame Lobbybelegung',
                   'overview-state': 'Status in der gemeinsamen Lobbyübersicht', 'overview-error': 'Aktualisierung der Lobbyübersicht',
                   'profile-status': 'Status im gemeinsamen Spielerfenster', 'lobby-save': 'Speicherhinweis der Lobby',
                   'shared-flash': 'Gemeinsame Rückmeldung', 'perfect-timer': 'Perfect · Fragentimer',
                   'perfect-game-timer': 'Perfect · Spielzeit', 'card-pile-count': 'Playtable · Kartenanzahl',
                   'dice-engine-status': 'Würfelspiele · Technikstatus', 'dice-message': 'Würfelspiele · Tischmeldung',
                   'dice-roll-result': 'Würfelspiele · Ergebnistext', 'conquest-army-values': 'Conquest · Öffentliche Armeewerte'}

    def __init__(self, buttons=None, root=ROOT):
        self.indicator_captures = json.loads(Path(__file__).with_name('generated-indicators.json').read_text(encoding='utf-8'))['captures']
        for capture in self.indicator_captures.values():
            for source in capture['evidence']:
                if digest(Path(root) / source['path']) != source['sha256']:
                    raise InvalidDesign('Die Anzeigenquelle wurde geändert. Bitte die Aufnahme erneuern.')
        super().__init__(buttons, root, definitions_list=definitions())

    def fragment(self, text, definition, original=False):
        parser = Fragments(text)
        target = definition.get('source_target', definition['target']) if original else definition['target']
        within = definition.get('source_within') if original else definition.get('within')
        tag = target.get('_tag')
        attrs = {k: v for k, v in target.items() if k != '_tag'}
        rows = [p for p in parser.elements if (not tag or p['tag'] == tag) and matches(p['attrs'], attrs)]
        if within:
            parent = parser.find(within)
            rows = [p for p in rows if parent['start'] <= p['start'] < parent['start'] + len(parent['markup'])]
        if not rows:
            raise InvalidDesign('Die erwartete Anzeige fehlt: ' + str(target))
        occurrence = definition.get('source_occurrence', 0) if original else 0
        return deepcopy(sorted(rows, key=lambda p: p['start'])[occurrence])

    def context(self, definition):
        value = super().context(definition)
        patch = definition.get('values', {})
        value.update(attempt=dict(score=patch.get('workshop_score', 320), status='completed'), current_position=4,
                     total_points=1230, currency_balance=250, headline='Gleich geht es los', detail='Neutrales Countdown-Beispiel',
                     remaining_ms=3000, visual_seconds=3)
        value['lobby'].update(host_name='Musterperson', member_count=2, is_member=False, is_reserved=False)
        if 'workshop_lobby_state' in patch:
            value['lobby']['status'] = patch['workshop_lobby_state']
        for i, player in enumerate(value['members']):
            player.update(points=180 - i * 20, score=180 - i * 20, rank=i + 1, rounds=3)
        value['leaderboards'] = {k: [dict(p) for p in value['members']] for k in ('daily', 'weekly', 'all', 'weekly_wins')}
        for p in value['leaderboards']['weekly_wins']:
            p['points'] = 2
        value['member_states'] = {1: dict(ready=True, answered=True, voted=True), 2: dict(ready=False, answered=False, voted=False)}
        if patch.get('workshop_guest_ready'):
            value['member_states'][2]['ready'] = True
        if patch.get('workshop_locked'):
            value['answer'] = dict(answer_locked_at='example' if patch['workshop_locked'] == 'answer' else None,
                                   vote_locked_at='example' if patch['workshop_locked'] == 'vote' else None, draft_vote_key='one')
            value['answer_text'] = 'Beispielantwort'
        if patch.get('workshop_away'):
            value['lobby_players'][0]['status'] = 'away'
        value['victories'] = dict(world='Welteroberung', missions='Geheime Aufträge')
        if 'workshop_overview_state' in patch:
            state = patch['workshop_overview_state']
            capacity = 10 if definition['game'] == 'Guesstimate Party' else 7 if definition['game'] == 'Perfect' else 6
            value['lobby'].update(status='waiting' if state == 'full' else state,
                                  member_count=capacity if state == 'full' else 2, player_limit=capacity)
        value['lobbies'] = [value['lobby']]
        value['get_flashed_messages'] = lambda **_: [('error', 'Beispiel: Die Aktion konnte nicht abgeschlossen werden.')] if patch.get('workshop_flash') else []
        return value

    def register(self, definition):
        key = definition.get('factory_capture')
        if not key:
            return super().register(definition)
        capture = self.indicator_captures[key]
        d = deepcopy(definition)
        d['evidence_paths'] = list(set(d.get('evidence_paths', []) + [p['path'] for p in capture['evidence']]))
        source = self.read(d['source'])
        line = source[:source.index('export function createPlayerPortrait')].count('\n') + 1
        original = dict(line=line, markup=capture['markup'])
        rendered = dict(markup=capture['markup'], ancestors=[dict(tag='main', attrs={'class': 'prototype'})])
        self.remember(d, original, rendered, [])

    def decorate(self, definition, rendered):
        def inner(target, value):
            fragment = Fragments(rendered['markup']).find(target)
            raw = fragment['markup']
            replacement = raw[:raw.find('>') + 1] + value + raw[raw.rfind('</'):]
            rendered['markup'] = rendered['markup'].replace(raw, replacement, 1)
        d = definition
        if 'root_text' in d:
            fragment = min(Fragments(rendered['markup']).elements, key=lambda p: p['start'])
            raw = fragment['markup']
            rendered['markup'] = raw[:raw.find('>') + 1] + escape(d['root_text']) + raw[raw.rfind('</'):]
        for target, text in d.get('sample_text', []):
            inner(target, escape(text))
        if d.get('capture_inner'):
            target, key = d['capture_inner']
            inner(target, self.indicator_captures[key]['markup'])
        if d.get('life_capture'):
            return self.decorate({**{k: v for k, v in d.items() if k != 'life_capture'},
                                  'root_text': self.indicator_captures[d['life_capture']]['values']['text']}, rendered)
        if d.get('timer_capture'):
            values = self.indicator_captures[d['timer_capture']]['values']
            inner({'id': 'time-factor-value'}, str(values['points']) + ' PKT')
            fragment = Fragments(rendered['markup']).find({'id': 'time-factor-bar'})
            raw = fragment['markup']
            rendered['markup'] = rendered['markup'].replace(raw, raw.replace('id="time-factor-bar"',
                'id="time-factor-bar" style="width:' + str(values['percent']) + '%;background-color:hsl(' + str(values['hue']) + ' 92% 61%)"'))
            rendered['markup'] = re.sub(r'aria-valuenow="[^"]*"', 'aria-valuenow="' + str(values['percent']) + '"', rendered['markup'])
        if 'clock_seconds' in d:
            seconds = d['clock_seconds']
            inner({'data-timer': None}, f'{seconds // 60}:{seconds % 60:02d}')
            if seconds <= 15:
                rendered['markup'] = rendered['markup'].replace('class="perfect-timer"', 'class="perfect-timer is-urgent"')
        if 'game_clock_seconds' in d:
            seconds = d['game_clock_seconds']
            inner({'data-game-timer': None}, f'Noch {seconds // 60}:{seconds % 60:02d}' if seconds else 'Zeit abgelaufen')
        if d.get('visible_warning'):
            rendered['markup'] = rendered['markup'].replace('class="perfect-time-warning"', 'class="perfect-time-warning is-visible"')
        if 'number_text' in d:
            parts = Fragments(rendered['markup']).elements
            outputs = [p for p in parts if p['tag'] == 'output']
            if outputs:
                raw = outputs[0]['markup']
                rendered['markup'] = rendered['markup'].replace(raw, raw[:raw.find('>') + 1] + escape(d['number_text']) + raw[raw.rfind('</'):], 1)
        if d['model'] == 'conquest-trade-feedback':
            return self.decorate({**d, 'model': '', 'root_text': 'Beispiel: Kartensatz getauscht.'}, rendered)
        if d['model'] == 'conquest-deployment-error':
            return self.decorate({**d, 'model': '', 'root_text': 'Beispiel: Bitte eine gültige Truppenanzahl wählen.'}, rendered)
        if d['model'] == 'conquest-battle':
            inner({'id': 'attacker-rolls'}, self.indicator_captures['conquest-roll-attack']['markup'])
            inner({'id': 'defender-rolls'}, self.indicator_captures['conquest-roll-defense']['markup'])
            inner({'id': 'battle-summary'}, 'Verluste: Angriff 1 · Verteidigung 1')
            inner({'id': 'battle-outcome'}, 'Du kannst erneut angreifen oder ein anderes Ziel wählen.')
            d.setdefault('evidence_paths', []).append('offline-preview/conquest-2-5d-v1/attack.js')
        return rendered

    def report(self):
        assets = self.assets()
        semantic = []
        for path in [*('templates/' + n for n in sorted(self.buttons.active_templates)), SURFACE]:
            for element in Fragments(self.read(path)).elements:
                a = element['attrs']
                if not (a.get('role') in ('status', 'alert', 'progressbar') or 'aria-live' in a or element['tag'] == 'output' or
                        any(k in a for k in ('data-timer', 'data-game-timer', 'data-countdown'))):
                    continue
                refs = [v['id'] for v in assets if v['snapshot']['source']['path'] == path and element['markup'] in v['snapshot']['markup']]
                reason = None
                if not refs and any(c in (a.get('class') or '') for c in ('sr-only', 'visually-hidden')):
                    reason = 'Assistive Statusmeldung ohne eigenständige sichtbare Gestaltung.'
                if not refs and 'perfect-show' in (a.get('class') or ''):
                    reason = 'Gesamter dynamischer Spielbereich; dessen konkrete Anzeigen sind separat zugeordnet.'
                semantic.append(dict(path=path, line=element['line'], tag=element['tag'], id=a.get('id'),
                                     classes=a.get('class'), refs=refs, exclusion=reason))
        entries = [{**{k: v for k, v in a.items() if k not in ('snapshot', 'preview')},
                    'source': a['snapshot']['source'], 'evidence': a['snapshot']['evidence']} for a in assets]
        return dict(schema=1, uses=len(assets), models=len({a['model_id'] for a in assets}), families=FAMILIES,
                    games=sorted({a['game'] for a in assets}), assets=entries, semantic_sources=semantic,
                    uncovered=[v for v in semantic if not v['refs'] and not v['exclusion']],
                    scope='Local canonical display sources and frozen neutral samples; no game DB or accounts.',
                    limits=['Static examples: timers do not run; no clock, scoring, game actions, writes or private states are executed.',
                            'Party result podium is retained source inventory, not a new or approved design.',
                            'Whole shared player components keep their canonical composition; samples do not load personal equipment.',
                            'ARIA-only status channels remain source evidence, not invented visible components.',
                            'No indicator editor or editor-option approval is included.'])
