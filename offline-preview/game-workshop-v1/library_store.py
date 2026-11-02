"""Personal, append-only game designs. Deliberately independent of app and game DBs."""
from copy import deepcopy
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re
from uuid import uuid4

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCHEMA = json.loads((HERE / 'schema.json').read_text(encoding='utf-8'))
KINDS = SCHEMA['kinds']
ID = re.compile(r'^[a-z]+-[a-f0-9]{32}$')


class InvalidDesign(ValueError):
    pass


def text_value(value, maximum, label, required=False):
    if not isinstance(value, str) or len(value) > maximum or (required and not value.strip()):
        raise InvalidDesign(f'{label}: Bitte einen passenden Text eingeben.')
    return value


def settings(kind, value):
    if not isinstance(kind, str) or kind not in KINDS or not isinstance(value, dict):
        raise InvalidDesign('Unbekannter Baustein.')
    fields = KINDS[kind]['fields']
    if set(value) != {f['key'] for f in fields}:
        raise InvalidDesign('Die Eigenschaften des Bausteins sind unvollständig oder unbekannt.')
    for field in fields:
        v, t = value[field['key']], field['type']
        valid = True
        if t in ('number', 'range'):
            valid = type(v) in (int, float) and math.isfinite(v) and field['min'] <= v <= field['max']
            if valid:
                step = (v - field['min']) / field['step']
                valid = abs(step - round(step)) < 0.00001
        elif t == 'select':
            valid = isinstance(v, str) and v in field['options']
        elif t == 'checkbox':
            valid = type(v) is bool
        elif t == 'color':
            valid = isinstance(v, str) and re.fullmatch(r'#[a-fA-F0-9]{6}', v) is not None
        else:
            text_value(v, field['maxLength'], field['label'], t == 'text')
        if not valid:
            raise InvalidDesign(f'{field["label"]}: Ungültiger Wert.')
    return deepcopy(value)


def defaults():
    return {k: {f['key']: f['default'] for f in v['fields']} for k, v in KINDS.items()}


def presets():
    definitions = [
        ('board', 'Klassisches Schachbrett', {}),
        ('board', 'Schiefer & Creme', {'dark':'#3b454b', 'light':'#e8e4d9', 'frame':'#283137'}),
        ('pieces', 'Gedrechseltes Schach', {}),
        ('pieces', 'Dame · gleicher Baukasten', {'set':'checkers', 'light':'#e5ba7c', 'dark':'#413731'}),
        ('pieces', 'Geometrischer Figurensatz', {'style':'geometric', 'dark':'#354a6e'}),
        ('background', 'Ruhiger Arbeitstisch', {}),
        ('background', 'Raum ohne Tisch', {'image':'room'}),
        ('camera', 'Perspektive am Tisch', {}),
        ('camera', 'Draufsicht ohne Kameraeffekt', {'mode':'2d'}),
        ('camera', '2,5D · parallele Ansicht', {'mode':'2.5d'}),
        ('room', 'Licht & sanfte Bewegung', {}),
        ('room', 'Ohne Objektbewegung', {'pieces':'off', 'cards':'off', 'dice':False}),
        ('lobby', 'Gemeinsame Guesstimate-Lobby', {}),
        ('dice', 'Zwei helle Würfel', {}),
        ('dice', 'Dunkler Einzelwürfel', {'count':1, 'color':'#233e38', 'pips':'#fff0c8'}),
        ('cards', 'Eigene Spielkarte', {}),
        ('cards', 'Ereigniskarte', {'title':'Unerwarteter Besuch', 'symbol':'star', 'back':'#5b3850'})
    ]
    base = defaults()
    return [dict(id=f'preset-{i}', kind=k, name=n, settings={**base[k], **patch}, builtin=True)
            for i, (k, n, patch) in enumerate(definitions)]


PRESETS = presets()


class Library:
    def __init__(self, directory=None, buttons_directory=None):
        self.directory = Path(directory or ROOT / 'design-library').resolve()
        self.buttons_directory = Path(buttons_directory or ROOT / 'design-library/recipes/button-workshop').resolve()

    def list(self, group):
        records, unreadable = [], 0
        for path in (self.directory / group).glob('*.json'):
            try:
                record = json.loads(path.read_text(encoding='utf-8'))
                if not isinstance(record, dict) or record.get('id') != path.stem or not ID.fullmatch(path.stem):
                    raise ValueError('Invalid record')
                if group == 'projects' and record.get('schema') == 2 and hasattr(self, 'validate_saved_project'):
                    self.validate_saved_project(record)
                    records.append(record)
                    continue
                if not path.stem.startswith(group[:-1]+'-') or record.get('schema') != 1:
                    raise ValueError('Unknown record version')
                text_value(record.get('name'), 100, 'Name', True)
                if group == 'elements':
                    settings(record.get('kind'), record.get('settings'))
                if group == 'projects':
                    for key in ('elements', 'included', 'sources'):
                        if not isinstance(record.get(key), dict) or set(record[key]) != set(KINDS):
                            raise ValueError('Incomplete project')
                    for kind in KINDS:
                        settings(kind, record['elements'][kind])
                        if type(record['included'][kind]) is not bool:
                            raise ValueError('Invalid selection')
                    text_value(record.get('notes'), 10000, 'Wünsche')
                    if not isinstance(record.get('buttons'),list) or not isinstance(record.get('button_snapshots'),list):
                        raise ValueError('Invalid buttons')
                records.append(record)
            except (OSError, ValueError):
                unreadable += 1
        return sorted(records, key=lambda r: r.get('created', ''), reverse=True), unreadable

    def buttons(self):
        records = []
        for path in self.buttons_directory.glob('*.json'):
            try:
                value = json.loads(path.read_text(encoding='utf-8'))
                # Only full saved buttons, not contour-only recipes.
                if value.get('kind') == 'button' and isinstance(value.get('id'), str) and isinstance(value.get('name'), str):
                    records.append(value)
            except (OSError, ValueError, AttributeError):
                continue
        return records

    def write(self, group, payload):
        record = {**deepcopy(payload), 'id':f'{group[:-1]}-{uuid4().hex}',
                  'created':datetime.now(timezone.utc).isoformat()}
        if group == 'projects' and record.get('schema') == 2 and record.get('project_key') is None:
            record['project_key'] = record['id']
        directory = self.directory / group
        directory.mkdir(parents=True, exist_ok=True)
        with (directory / (record['id'] + '.json')).open('x', encoding='utf-8') as out:
            json.dump(record, out, ensure_ascii=False, indent=2, allow_nan=False)
        return record

    def save_element(self, value):
        if not isinstance(value, dict) or set(value) != {'kind', 'name', 'settings'}:
            raise InvalidDesign('Kein vollständiger Baustein.')
        name = text_value(value['name'], 100, 'Name', True)
        return self.write('elements', dict(schema=1, name=name, kind=value['kind'], settings=settings(value['kind'], value['settings'])))

    def validate_project(self, value):
        if not isinstance(value, dict) or set(value) != {'schema', 'name', 'notes', 'elements', 'included', 'sources', 'buttons'} or type(value['schema']) is not int or value['schema'] != 1:
            raise InvalidDesign('Keine vollständige Projektmappe.')
        text_value(value['name'], 100, 'Projektname', True)
        text_value(value['notes'], 10000, 'Projektwünsche')
        for key in ('elements', 'included', 'sources'):
            if not isinstance(value[key], dict) or set(value[key]) != set(KINDS):
                raise InvalidDesign('Die Projektmappe benötigt alle acht Bausteinplätze.')
        known = {v['id']:v for v in [*PRESETS, *self.list('elements')[0]]}
        for kind in KINDS:
            settings(kind, value['elements'][kind])
            if type(value['included'][kind]) is not bool:
                raise InvalidDesign('Die Auswahl der Bausteine ist ungültig.')
            source = value['sources'][kind]
            if source is not None and (not isinstance(source, str) or source not in known or
                known[source].get('kind') != kind or known[source].get('settings') != value['elements'][kind]):
                raise InvalidDesign('Eine Bibliotheksreferenz passt nicht zu ihrem Baustein. Bitte den geänderten Entwurf neu speichern.')
        buttons = value['buttons']
        known_buttons = {v['id']:v for v in self.buttons()}
        if not isinstance(buttons, list) or len(buttons) > 10 or any(not isinstance(v, str) or v not in known_buttons for v in buttons) or len(set(buttons)) != len(buttons):
            raise InvalidDesign('Die Buttonauswahl ist ungültig.')
        return deepcopy(value)

    def save_project(self, value):
        value = self.validate_project(value)
        selected = set(value['buttons'])
        return self.write('projects', {**value, 'button_snapshots':[v for v in self.buttons() if v['id'] in selected]})

    def handoff(self, project_id):
        if not isinstance(project_id, str) or not ID.fullmatch(project_id):
            raise InvalidDesign('Ungültige Projektkennung.')
        projects, _ = self.list('projects')
        project = next((v for v in projects if v['id'] == project_id), None)
        if project is None:
            raise InvalidDesign('Diese gespeicherte Projektmappe wurde nicht gefunden.')
        lines = [f'# Projektübergabe: {project["name"]}', '', f'Gespeicherter Stand: {project_id}',
                 '', 'Diese Ausstattung soll als Grundlage für das neue Spiel dienen.',
                 'Spielregeln, Abläufe und offene Wünsche werden mit dem Nutzer abgestimmt.', '']
        for k, meta in KINDS.items():
            if project['included'][k]:
                lines += [f'## {meta["title"]}', f'Quelle: {project["sources"][k] or "Eigener Entwurf (Werte vollständig in der Projektdatei)"}', '']
                for f in meta['fields']:
                    v = project['elements'][k][f['key']]
                    label = f.get('options', {}).get(v, v) if not isinstance(v, bool) else ('Ja' if v else 'Nein')
                    lines.append(f'- {f["label"]}: {label}')
                lines.append('')
        lines += ['## Weitere Wünsche und Regeln', project['notes'] or 'Noch mit dem Nutzer zu ergänzen.', '',
                  '## Gespeicherte Buttons', *[f'- {v.get("name", v["id"])} · {v["id"]}' for v in project['button_snapshots']], '',
                  '## Stand der Vorschau', 'Gestaltungs- und Bewegungsprobe. Keine spielbare Schachpartie.',
                  'Fallprobe mit Tischkontakt; keine vollständige Kollision zwischen allen Objekten.',
                  'Die Lobby nutzt die gemeinsame Komponente mit Musterdaten. Keine Online-Lobby oder Kontenanbindung.']
        record = self.write('handoffs', {'schema':1, 'name':project['name'], 'project_id':project_id, 'project':project, 'brief':'\n'.join(lines)})
        with (self.directory/'handoffs'/(record['id']+'.md')).open('x', encoding='utf-8') as out:
            out.write(record['brief'])
        return record
