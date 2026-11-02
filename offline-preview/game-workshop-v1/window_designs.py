"""Append-only designs for the original catch-up window; no game data access."""
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
from threading import Lock
from uuid import uuid4

from library_store import InvalidDesign, text_value


FIELDS = [
    dict(key='scale', label='Fenstergröße', step=0, type='range', min=60, max=140, increment=5, unit='%'),
    dict(key='radius', label='Eckenrundung', step=0, type='range', min=0, max=40, increment=1, unit='px'),
    dict(key='border_width', label='Rahmenstärke', step=0, type='range', min=0, max=6, increment=1, unit='px'),
    dict(key='surface', label='Fläche', step=1, type='color'),
    dict(key='heading', label='Überschrift', step=1, type='color'),
    dict(key='text', label='Erklärungstext', step=1, type='color'),
    dict(key='border', label='Rahmenfarbe', step=1, type='color'),
]
DEFAULTS = {f['key']:100 if f['key']=='scale' else None for f in FIELDS}


class WindowDesigns:
    def __init__(self, directory, sources):
        self.directory = Path(directory)/'recipes/window-workshop'
        self.sources = sources
        self.lock = Lock()

    def can_edit(self, identifier):
        return identifier in self.sources.records and self.sources.records[identifier]['snapshot']['model']=='catchup-dialog'

    def source(self, identifier):
        if not isinstance(identifier,str) or not self.can_edit(identifier):
            raise InvalidDesign('Als erstes Fenster lässt sich der Guesstimate-Nachholdialog bearbeiten.')
        return self.sources.records[identifier]

    def config(self):
        return dict(fields=FIELDS, defaults=DEFAULTS,
                    sources=[a for a in self.sources.assets() if self.can_edit(a['id'])])

    def settings(self, value):
        if not isinstance(value,dict) or set(value)!=set(DEFAULTS):
            raise InvalidDesign('Die Fenstereinstellungen sind unvollständig oder unbekannt.')
        for field in FIELDS:
            v=value[field['key']]
            if v is None and field['key']!='scale':continue
            if field['type']=='color':valid=isinstance(v,str) and re.fullmatch(r'#[a-fA-F0-9]{6}',v)
            else:valid=type(v) is int and field['min']<=v<=field['max'] and (v-field['min'])%field['increment']==0
            if not valid:raise InvalidDesign('Ungültiger Wert: '+field['label'])
        return deepcopy(value)

    def style(self, value):
        s=self.settings(value)
        root=[];rules=[]
        if s['scale']!=100:root += ['transform:scale('+str(s['scale']/100)+')!important','transform-origin:center']
        for key,property in [('radius','border-radius'),('border_width','border-width')]:
            if s[key] is not None:root.append(property+':'+str(s[key])+'px!important')
        for key,property in [('surface','background'),('border','border-color')]:
            if s[key] is not None:root.append(property+':'+s[key]+'!important')
        if root:rules.append('.workshop-window-root{'+ ';'.join(root)+'}')
        if s['heading'] is not None:rules.append('.workshop-window-root .catchup-panel h2{color:'+s['heading']+'!important}')
        if s['text'] is not None:rules.append('.workshop-window-root .catchup-panel>p:not(.eyebrow){color:'+s['text']+'!important}')
        return '\n'.join(rules)

    def preview(self, source_id, value):
        self.source(source_id)
        page=self.sources.preview(source_id)
        marker='<style id="window-design-overrides">'+self.style(value)+'</style>'
        # Source previews omit an explicit head; insert before their body.
        return page.replace('<body ',marker+'<body ',1)

    def preview_request(self, payload):
        if not isinstance(payload,dict) or set(payload)!={'source_id','settings'}:
            raise InvalidDesign('Bitte ein Fenster und seine Einstellungen wählen.')
        source=self.source(payload['source_id'])
        width,height=self.sources.preview_size_for(source['definition'])
        return dict(html=self.preview(payload['source_id'],payload['settings']),width=width,height=height)

    def validate_record(self, record):
        if not isinstance(record,dict) or set(record)!={'schema','id','name','source_id','source_snapshot','settings','parent_id','created_at'} or type(record.get('schema')) is not int or record['schema']!=1:
            raise InvalidDesign('Unbekanntes Fensterformat.')
        if not isinstance(record['id'],str) or not re.fullmatch(r'window-[a-f0-9]{32}',record['id']):raise InvalidDesign('Ungültige Fensterkennung.')
        text_value(record['name'],100,'Fenstername',True)
        source=self.source(record['source_id'])
        if record['source_snapshot']!=source['snapshot']:raise InvalidDesign('Die Fenstervorlage hat sich geändert. Der gespeicherte Stand bleibt erhalten.')
        self.settings(record['settings'])
        if record['parent_id'] is not None and (not isinstance(record['parent_id'],str) or not re.fullmatch(r'window-[a-f0-9]{32}',record['parent_id'])):
            raise InvalidDesign('Ungültiger Ausgangsentwurf.')
        if not isinstance(record['created_at'],str) or datetime.fromisoformat(record['created_at']).tzinfo is None:raise InvalidDesign('Ungültiger Speicherzeitpunkt.')
        return record

    def list(self):
        rows=[];bad=0
        for path in self.directory.glob('window-*.json'):
            try:
                value=json.loads(path.read_text(encoding='utf-8'));self.validate_record(value)
                if value['id']!=path.stem:raise InvalidDesign('Falscher Dateiname.')
                rows.append(value)
            except (ValueError,OSError,TypeError):bad+=1
        return sorted(rows,key=lambda r:r['created_at'],reverse=True),bad

    def get(self, identifier):
        if not isinstance(identifier,str) or not re.fullmatch(r'window-[a-f0-9]{32}',identifier):raise InvalidDesign('Unbekannter Fensterentwurf.')
        try:record=json.loads((self.directory/(identifier+'.json')).read_text(encoding='utf-8'))
        except (OSError,ValueError):raise InvalidDesign('Der Fensterentwurf konnte nicht gelesen werden.')
        if not isinstance(record,dict) or record.get('id')!=identifier:raise InvalidDesign('Die Fensterkennung passt nicht zur Datei.')
        return self.validate_record(record)

    def save(self, payload):
        if not isinstance(payload,dict) or set(payload)!={'source_id','name','settings','parent_id'}:
            raise InvalidDesign('Bitte einen vollständigen Fensterentwurf speichern.')
        source=self.source(payload['source_id']);settings=self.settings(payload['settings'])
        name=text_value(payload['name'],100,'Fenstername',True).strip()
        parent=payload['parent_id']
        if parent is not None and self.get(parent)['source_id']!=payload['source_id']:raise InvalidDesign('Der Ausgangsentwurf gehört zu einem anderen Fenster.')
        record=dict(schema=1,id='window-'+uuid4().hex,name=name,source_id=payload['source_id'],source_snapshot=deepcopy(source['snapshot']),
                    settings=settings,parent_id=parent,created_at=datetime.now(timezone.utc).isoformat())
        self.validate_record(record)
        with self.lock:
            self.directory.mkdir(parents=True,exist_ok=True)
            with (self.directory/(record['id']+'.json')).open('x',encoding='utf-8') as output:json.dump(record,output,ensure_ascii=False,indent=2)
        return record

    def asset(self, record):
        source=next(a for a in self.sources.assets() if a['id']==record['source_id'])
        styling=dict(source=source['model_id'],settings=record['settings'])
        return dict(kind='windows',id=record['id'],name=record['name'],source='saved',variant='design',component='window-design-v1',representation='2d',
                    model_id='window-design-'+sha256(json.dumps(styling,sort_keys=True).encode()).hexdigest(),model_name=record['name'],
                    game=source['game'],games=source['games'],family=source['family'],family_name=source['family_name'],usage=source['usage'],
                    editable=True,created=record['created_at'],snapshot=deepcopy(record),preview='/api/window-designs/'+record['id']+'/preview',
                    preview_width=source['preview_width'],preview_height=source['preview_height'])

    def assets(self):return [self.asset(record) for record in self.list()[0]]
