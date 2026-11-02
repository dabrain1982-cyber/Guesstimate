"""Read local UI sources; report occurrences without importing the game or its DB.

Counts are source locations, not rendered controls or saved library designs.
"""
from __future__ import annotations

import ast
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs' / 'WERKSTATT_BESTAND.json'
CONQUEST = 'offline-preview/conquest-2-5d-v1/'
TAG = re.compile(r'<(?P<tag>button|a|input|dialog|select|textarea|div|section|aside|span)\b(?P<attrs>(?:"[^"]*"|\x27[^\x27]*\x27|[^\x27">])*)>', re.I)
ATTR = re.compile(r'([\w:-]+)\s*=\s*(["\x27])(.*?)\2', re.S)
CSS = re.compile(r'([^{}]+)\{')

# These families are conclusions from the inspected sources, not new editor promises.
FAMILIES = [
    ('buttons', 'Buttons', 'gestaltbar', 'Mehrere Grundlagen; Spieleinbindungen noch nicht vollständig registriert', [
        ('templates/home.html', 'class="primary-button"'),
        ('static/style.css', '.primary-button {'),
        ('offline-preview/conquest-2-5d-v1/game-buttons.js', 'recipe.source_id'),
        ('offline-preview/button-workshop-v1/renderer.js', 'renderButton'),
        ('templates/nerd_mode.html', 'class="perfect-buzzer'),
        ('templates/card_table_game.html', 'data-table-action'),
        ('templates/dice_table_game.html', 'data-dice-action')]),
    ('windows', 'Fenster und Inhaltsflächen', 'ansehen und Projekten zuordnen; Editor später', 'Fensterbibliothek mit gemeinsamen Modellen und getrennten Spiel-/Inhalts-/Zustandsvarianten', [
        ('offline-preview/game-workshop-v1/source_windows.py', 'class SourceWindows'),
        ('templates/base.html', '<dialog class="rules-dialog"'),
        ('static/rules.js', 'dialog.showModal'),
        ('templates/home.html', '<dialog class="catchup-dialog"'),
        (CONQUEST+'table-surface.js', '<dialog id="mission-reveal"'),
        (CONQUEST+'table-surface.js', 'id="deployment-controls"'),
        (CONQUEST+'table-surface.js', 'id="card-hand"'),
        ('templates/profile.html', 'profile-inventory')]),
    ('inputs', 'Eingaben und Auswahlfelder', 'ansehen und Projekten zuordnen; Editor später', 'Eingabebibliothek mit gemeinsamen Modellen und getrennten Beschriftungs-/Grenzwert-/Zustandsvarianten', [
        ('offline-preview/game-workshop-v1/source_inputs.py', 'class SourceInputs'),
        ('templates/question.html', '<input'), ('templates/nerd_mode.html', '<textarea'),
        ('templates/card_table_lobby.html', '<select')]),
    ('indicators', 'Punkte, Timer und Zustandsanzeigen', 'ansehen und Projekten zuordnen; Editor später', 'Anzeigenbibliothek mit gemeinsamen Modellen und getrennten Spiel-/Wert-/Zustandsvarianten; Zeitwerte sind eingefroren', [
        ('offline-preview/game-workshop-v1/source_indicators.py', 'class SourceIndicators'),
        ('templates/nerd_mode.html', 'perfect-timer'),
        ('templates/dice_table_game.html', 'dice-score-note'),
        (CONQUEST+'table-surface.js', 'id="reinforcements-left"'),
        (CONQUEST+'table-surface.js', 'id="battle-result"')]),
    ('players', 'Spieleranzeigen und Pulte', 'ansehen und Projekten zuordnen; Editor später', 'Spielerbibliothek mit Profilfenstern, Lobbyplätzen, Porträts, Ranglisten, Namenspulten und allen registrierten Pultfamilien', [
        ('offline-preview/game-workshop-v1/source_players.py', 'class SourcePlayers'),
        ('templates/_profile_window.html', 'macro profile_window'),
        ('static/player-portrait.js', 'createPlayerPortrait'),
        ('templates/_leaderboard.html', 'leaderboard')]),
    ('lobby', 'Lobbys und Lobbyübersichten', 'ansehen und zuordnen; bisheriger allgemeiner Entwurf bleibt gestaltbar', '134 Quellvarianten in sieben gemeinsamen Modellen aus allen sieben Mehrspielerspielen; Perfect behält seinen eigenen Raum', [
        ('offline-preview/game-workshop-v1/source_lobbies.py', 'class SourceLobbies'),
        ('templates/_lobby_room.html', 'macro lobby_room'),
        ('templates/_lobby_overview.html', 'macro lobby_overview'),
        ('templates/nerd_mode.html', 'perfect-buzzer')]),
    ('board', 'Bretter und Spielflächen', '2D/3D zuordenbar; Editoroptionen später', 'Zwei Grundvarianten mit Größe, Form und Bild; Conquest, Playtable und gemeinsame Würfelfläche aufgenommen', [
        ('offline-preview/game-workshop-v1/models.js', 'buildBoard'),
        (CONQUEST+'table-surface.js', 'id="territories"'),
        ('templates/card_table_game.html', 'card-table'),
        ('templates/dice_table_game.html', 'dice-table')]),
    ('pieces', 'Figuren, Spielsteine und Truppenmarken', 'ansehen und zuordnen; Editoroptionen später', 'Drei Formfamilien mit sieben Konfigurationen: Schach, Dame und vorhandene Conquest-Truppenmarke; Eigenschaften statt einzelner Bestände', [
        ('offline-preview/game-workshop-v1/piece_library.py', 'class PieceLibrary'),
        ('offline-preview/game-workshop-v1/models.js', 'buildPiece'),
        (CONQUEST+'territories.js', 'createElement')]),
    ('dice', 'Würfel', 'zwei Varianten zuordenbar; Editoroptionen später', 'Vorhandene Würfeltisch-Physik und flache Conquest-Anzeige; Anzahl und Aufdrucke als Parameter', [
        ('static/dice-table.js', 'dddice'),
        ('offline-preview/comic-ui-v1/components.js', 'dice'),
        ('offline-preview/game-workshop-v1/models.js', 'buildDie')]),
    ('cards', 'Karten und Kartenhände', 'Grundmodelle zuordenbar; neue Editoroptionen später', 'Zwei Grundbausteine und zwölf ganze Kartensätze; Fragen nur als Datenquellen der Fenster; keine Spielumstellung', [
        ('offline-preview/game-workshop-v1/card_library.py', 'MODELS'),
        ('static/card-table.js', 'createElement'),
        (CONQUEST+'cards.js', 'createCountryCard'),
        (CONQUEST+'turn-controls.js', 'createCountryCard'),
        ('offline-preview/game-workshop-v1/models.js', 'buildCard')]),
    ('background', 'Hintergründe', 'Bildmotive und ganze Räume ansehen und zuordnen; Editoroptionen später', '15 bestehende Bildmotive plus neun ganze Raumkonfigurationen in 2D/3D; ursprüngliche Raumkompositionen aus allen acht Spielen zugeordnet', [
        ('offline-preview/game-workshop-v1/room_library.py', 'class RoomLibrary'),
        (CONQUEST+'scene.js', 'function buildRoom'),
        ('app.py', 'BACKGROUND_CATALOG'),
        ('offline-preview/game-workshop-v1/workshop_catalog.py', 'background-room-')]),
    ('titles', 'Titelbilder', 'ansehen und zuordnen; eigene Bilder importieren', 'Acht vorhandene Bildmotive und Mäxchen-Logo als Konfigurationen zweier Bildfamilien; Editoroptionen später', [
        ('offline-preview/game-workshop-v1/graphic_library.py', 'def capture_artwork'),
        ('templates/_game_flyers.html', '<')]),
    ('flyers', 'Flyer und Spielpräsentation', 'ansehen und zuordnen; eigene Bilder importieren', '13 Konfigurationen in drei gemeinsamen Kompositionen aufgenommen; Bildmotive getrennt verwendbar; Editoroptionen später', [
        ('offline-preview/game-workshop-v1/graphic_library.py', 'def capture_flyers'),
        ('templates/_game_flyers.html', 'macro'),
        ('templates/tabletop_family.html', '<'),
        ('templates/tabletop_connection.html', '<')]),
    ('icons', 'Icons und Symbole', 'Symbolsätze ansehen und zuordnen; eigener Bildeditor bleibt', 'Fünf endliche Symbolsätze und App-Symbol aus Originalquellen aufgenommen; keine Einträge je Einsatz; Editoroptionen später', [
        ('offline-preview/game-workshop-v1/graphic_library.py', 'def capture_icons'),
        ('templates/_icons.html', 'macro category_icon'),
        ('offline-preview/comic-ui-v1/components.js', 'icon')]),
    ('avatars', 'Avatare', 'vorhandener Bildeditor', 'Bildvarianten; kein freier Figureneditor; Profilausrüstung erhalten', [
        ('app.py', 'AVATAR_CATALOG'),
        ('static/player-portrait.js', 'createPlayerPortrait')]),
    ('sounds', 'Geräusche und Musik', 'lokal probehören und zuordnen; Editor später', '13 neu recherchierte kurze CC0-Klänge für Bedienung, Tischaktionen, Rundenbeginn, Sieg und Niederlage; bestehende Zuordnungen unverändert', [
        ('offline-preview/game-workshop-v1/media_library.py', 'SOUND_FAMILIES'),
        ('offline-preview/button-workshop-v1/assets/audio/catalog.json', 'sounds'),
        ('offline-preview/button-workshop-v1/sound.js', 'createSound'),
        ('static/vendor/dddice-outgunned/theme.json', '.mp3'),
        (CONQUEST+'game-buttons.js', 'createSound')]),
    ('fonts', 'Schriften', 'passende Stilvorlagen ansehen und zuordnen; Editor später', 'Sieben freie lokale Schrift-/Oberflächenkombinationen einschließlich Kreide, Stein und Metall; keine universelle Effektmatrix', [
        ('offline-preview/game-workshop-v1/media_library.py', 'FONT_STYLES'),
        ('static/typography-v1.css', '@font-face'),
        ('offline-preview/button-workshop-v1/fonts.css', '@font-face')]),
    ('materials', 'Materialien und Stile', 'gemeinsame Projekteigenschaft', 'Neun Materialfamilien mit Originalbeispielen; Projektwünsche ohne Änderung der Originalelemente, Editoroptionen später', [
        ('offline-preview/game-workshop-v1/property_catalog.py', 'class PropertyCatalog'),
        ('offline-preview/button-workshop-v1/catalog.json', '"id": "material"'),
        ('offline-preview/button-workshop-v1/materials.css', 'material'),
        (CONQUEST+'scene.js', 'Material')]),
    ('presentation', 'Kamera, Licht und Bewegung', 'gemeinsame Projektentscheidungen und Originalbeispiele', 'Drei Ansichtsbeispiele, Licht und Bewegung separat; 2,5D als Ansicht räumlicher Elemente, keine neuen Einzelobjekte', [
        ('offline-preview/game-workshop-v1/property_catalog.py', 'self.views'),
        ('offline-preview/game-workshop-v1/workshop_catalog.py', 'PRESENTATION'),
        (CONQUEST+'camera.js', 'camera'),
        ('offline-preview/game-workshop-v1/motion.js', 'export')]),
]


def relative(path):
    return path.relative_to(ROOT).as_posix()


def read(path):
    return path.read_text(encoding='utf-8-sig')


def source_evidence(path, needle):
    file = ROOT / path
    if not file.is_file():
        raise ValueError('Missing family source: '+path)
    for line, text in enumerate(read(file).splitlines(), 1):
        if needle in text:
            return {'path': path, 'line': line, 'match': text.strip()[:220]}
    raise ValueError('Missing family evidence: '+path+' / '+needle)


def collect():
    files = sorted([*ROOT.joinpath('templates').rglob('*.html'),
                    *ROOT.joinpath('static').glob('*.js'),
                    *ROOT.joinpath('static').glob('*.css'),
                    *ROOT.joinpath(CONQUEST).glob('*.js'),
                    *ROOT.joinpath(CONQUEST).glob('*.css')])
    files = [p for p in files if not p.name.endswith(('.test.js', '-check.js'))]
    source_files = {relative(p): {'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in files}
    records, definitions, factories = [], [], []
    for file in files:
        text, path = read(file), relative(file)
        for match in TAG.finditer(text):
            tag = match['tag'].lower()
            attrs = {a[0]: a[2] for a in ATTR.findall(match['attrs'])}
            classes = attrs.get('class', '')
            if tag == 'a' and not re.search(r'button|btn|buzzer|action', classes):
                continue
            if tag == 'input' and attrs.get('type') == 'hidden':
                continue
            role = attrs.get('role')
            if tag in ('div', 'section', 'aside', 'span') and role not in ('button', 'tab', 'menuitem', 'radio', 'dialog', 'alertdialog'):
                continue
            kind = ('windows' if tag == 'dialog' or role in ('dialog', 'alertdialog') else
                    'inputs' if tag in ('select', 'textarea') or role == 'radio' or (tag == 'input' and attrs.get('type') not in ('button', 'submit', 'reset')) else 'buttons')
            end = text.find('</'+tag, match.end())
            label = re.sub('<[^>]+>', ' ', text[match.end():end]) if end >= 0 and tag != 'input' else ''
            records.append({'kind': kind, 'path': path, 'line': text.count('\n', 0, match.start())+1,
                            'tag': tag, 'id': attrs.get('id'), 'classes': classes,
                            'label': re.sub(r'\s+', ' ', attrs.get('aria-label') or label).strip()[:140],
                            'attributes': {k:v for k,v in attrs.items() if k.startswith('data-') or k in ('type', 'name', 'role')},
                            'status': 'source_occurrence_not_library_asset'})
        if file.suffix == '.js':
            for match in re.finditer(r'createElement\(\s*(["\x27])(button|dialog|select|textarea)\1\s*\)', text):
                factories.append({'path': path, 'line': text.count('\n', 0, match.start())+1, 'tag': match[2]})
        if file.suffix == '.css':
            for match in CSS.finditer(text):
                selector = re.sub(r'/\*.*?\*/', '', match[1], flags=re.S).strip()
                if re.search(r'button|buzzer|dialog|inventory|modal', selector):
                    definitions.append({'path': path, 'line': text.count('\n', 0, match.start())+1, 'selector': selector[:350]})
    template_entries = set()
    for file in ROOT.glob('*.py'):
        tree = ast.parse(read(file))
        for call in ast.walk(tree):
            if isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id == 'render_template' and call.args:
                name = call.args[0]
                if isinstance(name, ast.Constant) and isinstance(name.value, str):
                    template_entries.add(name.value)
    families = [{'id': identifier, 'name': name, 'capability': capability, 'finding': finding,
                 'evidence': [source_evidence(path, needle) for path, needle in evidence]}
                for identifier, name, capability, finding, evidence in FAMILIES]
    for family in families:
        for evidence in family['evidence']:
            path = evidence['path']
            source_files.setdefault(path, {'sha256': hashlib.sha256((ROOT/path).read_bytes()).hexdigest()})
    return {'schema': 1, 'created_utc': datetime.now(timezone.utc).isoformat(),
            'scope': 'Current local source inventory; no running game or remote server inspected; no application/DB import.',
            'coverage': ['Daily Quiz', 'Party', 'Perfect', 'Playtable', 'Würfeltisch', 'Kniffel', 'Mäxchen', 'Conquest', 'Startseite/Profil/Sammlung'],
            'limits': ['Source occurrences can be conditional, repeated, or legacy.',
                       'CSS selectors are evidence locations, not resolved browser styling.',
                       'createElement locations count factories, not generated instances.',
                       'Only registered workshop records are saved editable assets; this report creates none.',
                       'Conquest table-surface.js is used by the current game despite its offline-preview directory.',
                       'static/conquest-table.js is retained legacy source; conquest_table.html loads scene.js instead.'],
            'source_files': source_files, 'template_entries': sorted(template_entries), 'families': families,
            'button_surface_coverage': [
                {'surface':'plain','available':'shared_workshop_renderer','evidence':[
                    source_evidence('static/lobby-overview.css','.lobby-browser .primary-button {')]},
                {'surface':'gradient','available':'shared_workshop_renderer','evidence':[
                    source_evidence('static/card-table.css','.card-command-row button, .card-room-actions button {'),
                    source_evidence('static/dice-table.css','.dice-console-actions button.is-danger')]},
                {'surface':'translucent','available':'shared_workshop_renderer','evidence':[
                    source_evidence('static/dice-table.css','.dice-game-leave button {')]},
                {'surface':'image_button','available':'existing_asset_not_yet_registered_as_button_recipe','evidence':[
                    source_evidence('templates/nerd_mode.html','class="perfect-buzzer')]}],
            'occurrences': records, 'factories': factories, 'style_definitions': definitions,
            'summary': {'scanned_ui_files': len(files), 'evidence_files': len(source_files), 'families': len(families), 'source_occurrences': dict(Counter(r['kind'] for r in records)),
                        'dynamic_factories': len(factories), 'style_definitions': len(definitions)}}


def main():
    report = collect()
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report['summary'], ensure_ascii=False))


if __name__ == '__main__':
    main()
