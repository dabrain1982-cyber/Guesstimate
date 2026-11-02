"""Validate and append local design recipes. Never imports the game or its DB."""
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re
import threading
import uuid
from source_recipe import validate_source_recipe
from unified_recipe import validate_base

CATALOG = json.loads(Path(__file__).with_name('catalog.json').read_text(encoding='utf-8'))
CATALOG['sounds'] = json.loads((Path(__file__).parent/'assets/audio/catalog.json').read_text(encoding='utf-8'))['sounds']
from media_selection import extend_catalog
extend_catalog(CATALOG)
FIELDS = {field['key']: field for field in CATALOG['fields']}
REVIEW_KEYS = {row[0] for row in CATALOG['review_dimensions']}
REVIEW_VALUES = {row[0] for row in CATALOG['review_states']}


class InvalidRecipe(ValueError):
    pass


def validate_contour(contour):
    if not isinstance(contour, dict) or set(contour) != {'template', 'points'} or not isinstance(contour.get('template'), str) or contour['template'] not in CATALOG['contours']:
        raise InvalidRecipe('Die Konturvorlage ist ungültig.')
    points = contour.get('points')
    if not isinstance(points, list) or not 3 <= len(points) <= 32:
        raise InvalidRecipe('Eine Kontur braucht 3 bis 32 Randpunkte.')
    for point in points:
        if not isinstance(point, dict) or set(point) != {'x', 'y', 'round'}:
            raise InvalidRecipe('Ungültiger Randpunkt.')
        for key, maximum in [('x', 100), ('y', 100), ('round', 50)]:
            value = point[key]
            if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= maximum:
                raise InvalidRecipe('Randpunkte und Rundungen liegen außerhalb der Fläche.')
    def cross(a, b, c):
        return (b['x']-a['x'])*(c['y']-a['y'])-(b['y']-a['y'])*(c['x']-a['x'])
    def on_segment(a, b, p):
        return (abs(cross(a,b,p)) < 1e-7 and min(a['x'],b['x'])-1e-7 <= p['x'] <= max(a['x'],b['x'])+1e-7
                and min(a['y'],b['y'])-1e-7 <= p['y'] <= max(a['y'],b['y'])+1e-7)
    area = 0
    for i, a in enumerate(points):
        b = points[(i+1) % len(points)]
        area += a['x']*b['y']-b['x']*a['y']
        if math.hypot(a['x']-b['x'], a['y']-b['y']) < .5:
            raise InvalidRecipe('Zwei Randpunkte liegen zu dicht beieinander.')
        for j in range(i+1, len(points)):
            if j == i+1 or (i == 0 and j == len(points)-1):
                continue
            c, d = points[j], points[(j+1) % len(points)]
            if ((cross(a,b,c)*cross(a,b,d) < 0 and cross(c,d,a)*cross(c,d,b) < 0)
                    or on_segment(a,b,c) or on_segment(a,b,d) or on_segment(c,d,a) or on_segment(c,d,b)):
                raise InvalidRecipe('Die Kontur darf sich nicht selbst kreuzen.')
    if abs(area) < 20:
        raise InvalidRecipe('Die Kontur braucht eine größere Fläche.')
    return {'template': contour['template'], 'points': [dict(point) for point in points]}


def validate_recipe(payload):
    if isinstance(payload,dict) and type(payload.get('schema_version')) is int and payload['schema_version']==3:
        return validate_source_recipe(payload,InvalidRecipe)
    if not isinstance(payload, dict) or type(payload.get('schema_version')) is not int or payload['schema_version'] not in (1, 2, 4):
        raise InvalidRecipe('Diese Entwurfsdatei hat ein unbekanntes Format.')
    name = payload.get('name', '')
    notes = payload.get('notes', '')
    if not isinstance(name, str) or not 1 <= len(name.strip()) <= 80:
        raise InvalidRecipe('Bitte gib dem Entwurf einen Namen mit höchstens 80 Zeichen.')
    if not isinstance(notes, str) or len(notes) > 1500:
        raise InvalidRecipe('Die Notiz darf höchstens 1.500 Zeichen enthalten.')
    settings = payload.get('settings')
    legacy = payload['schema_version'] == 1
    expected = set(FIELDS) - {'style'} if legacy else set(FIELDS)
    optional = {'font_link', 'gradient_to', 'opacity', 'font_scale', 'shadow','height_ratio','ink_mode','ink_color','depth_mode','depth_color','depth_x','font_bold','font_italic'}
    if not isinstance(settings, dict) or not expected-optional <= set(settings) <= expected:
        raise InvalidRecipe('Die Einstellungen sind unvollständig oder enthalten unbekannte Felder.')
    settings = dict(settings)
    for key in optional-{'font_link','font_bold','font_italic'}:settings.setdefault(key,CATALOG['defaults'][key])
    settings.setdefault('font_link', 'manual')
    settings.setdefault('gradient_to', CATALOG['defaults']['gradient_to'])
    settings.setdefault('opacity', CATALOG['defaults']['opacity'])
    settings.setdefault('font_scale', CATALOG['defaults']['font_scale'])
    settings.setdefault('shadow', CATALOG['defaults']['shadow'])
    if legacy:
        if not isinstance(settings.get('shape'), str) or settings['shape'] not in CATALOG['legacy_contours']:
            raise InvalidRecipe('Die alte Grundform ist ungültig.')
        settings['style'] = 'comic'
    for key, field in FIELDS.items():
        if key in ('font_bold','font_italic') and key not in settings:continue
        value = settings[key]
        valid = False
        if field['type'] == 'checkbox':
            valid = type(value) is bool
        elif field['type'] == 'range':
            valid = (type(value) is int and field['min'] <= value <= field['max']
                     and (value - field['min']) % field.get('step', 1) == 0)
        elif field['type'] == 'select':
            valid = isinstance(value, str) and value in {row[0] for row in field['options']}
        elif field['type'] == 'color':
            valid = isinstance(value, str) and re.fullmatch(r'#[0-9a-fA-F]{6}', value) is not None
        elif field['type'] == 'text':
            valid = isinstance(value, str) and 1 <= len(value.strip()) <= field['max']
        if not valid:
            raise InvalidRecipe('Ungültige Einstellung: ' + field['label'])
    review = payload.get('review', {})
    expected_review = REVIEW_KEYS - {'style'} if legacy else REVIEW_KEYS
    if not isinstance(review, dict) or set(review) != expected_review or any(not isinstance(value, str) or value not in REVIEW_VALUES for value in review.values()):
        raise InvalidRecipe('Die getrennten Bewertungen sind unvollständig oder ungültig.')
    review = dict(review)
    if legacy:
        review['style'] = 'open'
        contour = {'template': settings['shape'], 'points': [dict(x=x, y=y, round=r)
                   for x,y,r in CATALOG['legacy_contours'][settings['shape']]]}
        settings['shape'] = 'custom'
    else:
        contour = payload.get('contour')
    contour = validate_contour(contour)
    parent = payload.get('parent_id')
    if parent is not None and (not isinstance(parent, str) or not re.fullmatch(r'[a-f0-9]{32}', parent)):
        raise InvalidRecipe('Der Ausgangsentwurf ist ungültig.')
    kind = payload.get('kind', 'button')
    if kind not in ('button', 'shape'):
        raise InvalidRecipe('Unbekannte Entwurfsart.')
    result={'schema_version': 2, 'renderer_version': CATALOG['renderer_version'], 'contour': contour,
            'name': name.strip(), 'notes': notes, 'settings': dict(settings), 'kind': kind,
            'review': dict(review), 'parent_id': parent}
    if payload['schema_version']==4:
        source=payload.get('source_button')
        validate_source_recipe(dict(schema_version=3,kind='button',name=name,notes=notes,parent_id=parent,source_button=source,appearance={}),InvalidRecipe)
        result.update(schema_version=4,base=validate_base(payload.get('base'),InvalidRecipe),source_button=source)
    return result


class RecipeStore:
    def __init__(self, directory):
        self.directory = Path(directory).resolve()
        self.directory.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()

    def list(self):
        recipes, unreadable = [], 0
        with self.lock:
            for path in self.directory.glob('*.json'):
                try:
                    data = json.loads(path.read_text(encoding='utf-8'))
                    normalized = validate_recipe(data)
                    if data.get('id') != path.stem or not re.fullmatch(r'[a-f0-9]{32}', path.stem):
                        raise InvalidRecipe('Ungültige Kennung')
                    created = data['created_at']
                    if not isinstance(created, str) or datetime.fromisoformat(created).tzinfo is None:
                        raise InvalidRecipe('Ungültiger Zeitpunkt')
                    recipes.append(dict(normalized, id=data['id'], created_at=created))
                except (ValueError, OSError, KeyError):
                    unreadable += 1
        return sorted(recipes, key=lambda row: row['created_at'], reverse=True), unreadable

    def save(self, payload):
        data = validate_recipe(payload)
        data.update(id=uuid.uuid4().hex, created_at=datetime.now(timezone.utc).isoformat())
        raw = (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
        with self.lock:
            temporary = self.directory / (data['id'] + '.tmp')
            target = self.directory / (data['id'] + '.json')
            with temporary.open('xb') as stream:
                stream.write(raw)
                stream.flush()
                import os
                os.fsync(stream.fileno())
            temporary.rename(target)
        return data
