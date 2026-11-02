"""Append-only board authoring. Uses the existing board factory, never game state."""
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
from pathlib import Path
import re
from threading import Lock
from uuid import uuid4

from library_store import HERE, ROOT, InvalidDesign, text_value


FIELDS = [
    dict(key='representation',label='Ausführung',step=0,type='select',options={'3d':'3D · mit Brettdicke','2d':'2D · flach'}),
    dict(key='shape',label='Brettform',step=0,type='select',options={'rectangle':'Rechteckig','round':'Rund'}),
    dict(key='width',label='Breite der Spielfläche',step=0,type='number',min=20,max=160,increment=.5,unit='cm'),
    dict(key='height',label='Höhe der Spielfläche',step=0,type='number',min=20,max=160,increment=.5,unit='cm'),
    dict(key='border',label='Rahmenbreite',step=0,type='range',min=0,max=10,increment=.5,unit='cm'),
    dict(key='thickness',label='Brettdicke',step=0,type='range',min=.3,max=8,increment=.1,unit='cm'),
    dict(key='surface',label='Flächenfarbe',step=1,type='color'),
    dict(key='frame',label='Rahmen und Seitenwand',step=1,type='color'),
    dict(key='finish',label='Oberfläche',step=1,type='select',options={'matte':'Matt','satin':'Seidenmatt','gloss':'Glänzend'}),
    dict(key='image_id',label='Brettbild',step=1,type='image'),
    dict(key='image_fit',label='Bild einpassen',step=1,type='select',options={'contain':'Ganzes Bild erhalten','cover':'Fläche füllen · Ränder beschneiden'}),
    dict(key='pattern',label='Feldmuster',step=2,type='select',options={'checker':'Abwechselnd zwei Farben','grid':'Nur Gitterlinien','none':'Keine Felder'}),
    dict(key='columns',label='Spalten',step=2,type='number',min=2,max=24,increment=1,unit=''),
    dict(key='rows',label='Reihen',step=2,type='number',min=2,max=24,increment=1,unit=''),
    dict(key='secondary',label='Zweite Feldfarbe / Linienfarbe',step=2,type='color'),
    dict(key='pattern_opacity',label='Deckkraft der Felder',step=2,type='range',min=0,max=100,increment=5,unit='%'),
]
DEFAULTS = dict(representation='3d',shape='rectangle',width=60,height=60,border=2.5,thickness=1.8,
                surface='#e9d8b3',frame='#634530',finish='satin',image_id=None,image_fit='contain',
                pattern='checker',columns=8,rows=8,secondary='#527568',pattern_opacity=100)
BUILTIN_IMAGES = [
    ('conquest-map','Conquest · Weltkarte','offline-preview/conquest-2-5d-v1/assets/karte.png','/board-source/map.png'),
    ('wood','Holz','offline-preview/button-workshop-v1/assets/oak-v1.png','/assets/wood.png'),
    ('slate','Schiefer','offline-preview/button-workshop-v1/assets/slate-v1.png','/assets/slate.png'),
    ('felt','Playtable · Filz','static/card-table-felt-v1.png','/shared/card-table-felt-v1.png'),
]
IDENTIFIER = re.compile(r'board-[a-f0-9]{32}')


class BoardDesigns:
    def __init__(self,directory,images):
        self.directory=Path(directory)/'recipes/board-workshop'
        self.images=images
        self.lock=Lock()

    def image(self,identifier):
        if identifier is None:return None
        if not isinstance(identifier,str):raise InvalidDesign('Bitte ein vorhandenes Brettbild wählen.')
        for key,name,path,url in BUILTIN_IMAGES:
            if identifier==key:
                return dict(id=key,name=name,url=url,sha256=sha256((ROOT/path).read_bytes()).hexdigest())
        record=self.images.get(identifier)
        # Loading through ImageStore verifies the original bytes and normalizes orientation.
        self.images.view(identifier,True)
        return dict(id=identifier,name=record['name'],url='/library-images/'+identifier+'/view.png',sha256=record['sha256'])

    def config(self):
        images=[self.image(key) for key,_,_,_ in BUILTIN_IMAGES]
        images.extend(dict(id=a['id'],name=a['name'],url=a['image']) for a in self.images.assets())
        return dict(fields=deepcopy(FIELDS),defaults=deepcopy(DEFAULTS),images=images)

    def settings(self,value):
        if not isinstance(value,dict) or set(value)!=set(DEFAULTS):raise InvalidDesign('Die Bretteinstellungen sind unvollständig oder unbekannt.')
        for field in FIELDS:
            v=value[field['key']]
            if field['type']=='image':
                if v is not None:self.image(v)
                continue
            if field['type']=='select':valid=isinstance(v,str) and v in field['options']
            elif field['type']=='color':valid=isinstance(v,str) and re.fullmatch(r'#[a-fA-F0-9]{6}',v)
            else:
                valid=type(v) in (int,float) and math.isfinite(v) and field['min']<=v<=field['max']
                if valid:
                    step=(v-field['min'])/field['increment'];valid=abs(step-round(step))<1e-6
            if not valid:raise InvalidDesign('Ungültiger Wert: '+field['label'])
        if value['shape']=='round' and value['width']!=value['height']:raise InvalidDesign('Ein rundes Brett braucht denselben Durchmesser in beide Richtungen.')
        return deepcopy(value)

    def preview(self,value,interactive=True,view=None):
        settings=self.settings(value)
        if view is None:view=dict(fit=True,comparison=False,scale=100)
        if not isinstance(view,dict) or set(view)!={'fit','comparison','scale'} or type(view['fit']) is not bool or type(view['comparison']) is not bool or type(view['scale']) is not int or not 50<=view['scale']<=150 or view['scale']%5:
            raise InvalidDesign('Bitte eine passende Vorschau wählen.')
        config=dict(settings=dict(renderer='design',design=settings,image=self.image(settings['image_id'])),
                    representation=settings['representation'],interactive=interactive,view=deepcopy(view))
        raw=json.dumps(config,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
        return (HERE/'board-stage.html').read_text(encoding='utf-8').replace('<!--source-css-->','').replace('<!--config-->',raw)

    def validate_record(self,record):
        keys={'schema','id','name','settings','image_snapshot','parent_id','created_at'}
        if not isinstance(record,dict) or set(record)!=keys or type(record['schema']) is not int or record['schema']!=1:raise InvalidDesign('Unbekanntes Brettformat.')
        if not isinstance(record['id'],str) or not IDENTIFIER.fullmatch(record['id']):raise InvalidDesign('Ungültige Brettkennung.')
        text_value(record['name'],100,'Brettname',True)
        self.settings(record['settings'])
        if record['image_snapshot']!=self.image(record['settings']['image_id']):raise InvalidDesign('Das Brettbild wurde verändert. Der gespeicherte Entwurf bleibt erhalten.')
        if record['parent_id'] is not None and (not isinstance(record['parent_id'],str) or not IDENTIFIER.fullmatch(record['parent_id'])):raise InvalidDesign('Ungültiger Ausgangsentwurf.')
        if not isinstance(record['created_at'],str) or datetime.fromisoformat(record['created_at']).tzinfo is None:raise InvalidDesign('Ungültiger Speicherzeitpunkt.')
        return record

    def list(self):
        rows=[];bad=0
        with self.lock:
            for path in self.directory.glob('board-*.json'):
                try:
                    record=json.loads(path.read_text(encoding='utf-8'));self.validate_record(record)
                    if record['id']!=path.stem:raise InvalidDesign('Falscher Dateiname.')
                    rows.append(record)
                except (ValueError,OSError,TypeError):bad+=1
        return sorted(rows,key=lambda r:r['created_at'],reverse=True),bad

    def get(self,identifier):
        if not isinstance(identifier,str) or not IDENTIFIER.fullmatch(identifier):raise InvalidDesign('Unbekannter Brettentwurf.')
        try:
            with self.lock:record=json.loads((self.directory/(identifier+'.json')).read_text(encoding='utf-8'))
        except (ValueError,OSError):raise InvalidDesign('Der Brettentwurf konnte nicht gelesen werden.')
        if not isinstance(record,dict) or record.get('id')!=identifier:raise InvalidDesign('Die Brettkennung passt nicht zur Datei.')
        return self.validate_record(record)

    def save(self,payload):
        if not isinstance(payload,dict) or set(payload)!={'name','settings','parent_id'}:raise InvalidDesign('Bitte einen vollständigen Brettentwurf speichern.')
        settings=self.settings(payload['settings']);name=text_value(payload['name'],100,'Brettname',True).strip()
        parent=payload['parent_id']
        if parent is not None:self.get(parent)
        record=dict(schema=1,id='board-'+uuid4().hex,name=name,settings=settings,image_snapshot=self.image(settings['image_id']),
                    parent_id=parent,created_at=datetime.now(timezone.utc).isoformat())
        with self.lock:
            self.directory.mkdir(parents=True,exist_ok=True)
            with (self.directory/(record['id']+'.json')).open('x',encoding='utf-8') as out:json.dump(record,out,ensure_ascii=False,indent=2,allow_nan=False)
        return record

    def asset(self,record):
        representation=record['settings']['representation']
        return dict(kind='board',id=record['id'],name=record['name'],source='saved',variant='design',component='board-design-v1',
                    representation=representation,model_id='board-'+representation+'-v1',
                    model_name='Brett · '+representation.upper(),family=representation,family_name='Räumliche Bretter' if representation=='3d' else 'Flache Bretter und Spielflächen',editable=True,
                    created=record['created_at'],snapshot=deepcopy(record),preview='/api/board-designs/'+record['id']+'/preview',preview_width=720,preview_height=500)

    def assets(self):return [self.asset(record) for record in self.list()[0]]
