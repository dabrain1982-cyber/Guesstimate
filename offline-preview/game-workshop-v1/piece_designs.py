"""Append-only equipment designs using the existing chess/checker model factory."""
from copy import deepcopy
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re
from threading import Lock
from uuid import uuid4
from library_store import HERE, InvalidDesign, text_value

ROLES={'pawn':'Bauer','rook':'Turm','knight':'Springer','bishop':'Läufer','queen':'Dame','king':'König'}
FIELDS=[
    dict(key='set',label='Figurenfamilie',step=0,type='select',options={'chess':'Schachfiguren · gemeinsamer Satz','checkers':'Damesteine'}),
    dict(key='representation',label='Ausführung',step=0,type='select',options={'3d':'3D · räumliche Figuren','2d':'2D · flache Spielmarken'}),
    dict(key='style',label='Formensprache',step=0,type='select',options={'classic':'Gedrechselt','geometric':'Geometrisch'}),
    dict(key='size',label='Gesamtgröße',step=1,type='range',min=50,max=180,increment=5,unit='%'),
    dict(key='height',label='Körperhöhe',step=1,type='range',min=.6,max=1.5,increment=.05,percent=True),
    dict(key='base',label='Fußbreite',step=1,type='range',min=.65,max=1.2,increment=.05,percent=True),
    dict(key='stem',label='Körperbreite',step=1,type='range',min=.6,max=1.5,increment=.05,percent=True),
    dict(key='head',label='Kopfgröße',step=1,type='range',min=.7,max=1.3,increment=.05,percent=True),
    dict(key='light',label='Erste Seite',step=2,type='color'),
    dict(key='dark',label='Zweite Seite',step=2,type='color'),
    dict(key='roughness',label='Mattheit',step=2,type='range',min=.15,max=1,increment=.05,percent=True),
    dict(key='metallic',label='Metallwirkung',step=2,type='range',min=0,max=1,increment=.05,percent=True),
]
DEFAULTS=dict(set='chess',representation='3d',style='classic',size=100,height=1,base=1,stem=1,head=1,
              light='#fff0d2',dark='#253e3a',roughness=.4,metallic=.1)
IDENTIFIER=re.compile(r'piece-[a-f0-9]{32}')


class PieceDesigns:
    def __init__(self,directory):
        self.directory=Path(directory)/'recipes/piece-workshop';self.lock=Lock()

    def config(self):return dict(fields=deepcopy(FIELDS),defaults=deepcopy(DEFAULTS),roles=deepcopy(ROLES))

    def settings(self,value):
        if not isinstance(value,dict) or set(value)!=set(DEFAULTS):raise InvalidDesign('Die Figureneinstellungen sind unvollständig oder unbekannt.')
        for f in FIELDS:
            v=value[f['key']]
            if f['type']=='select':valid=isinstance(v,str) and v in f['options']
            elif f['type']=='color':valid=isinstance(v,str) and re.fullmatch(r'#[a-fA-F0-9]{6}',v)
            else:
                valid=type(v) in (int,float) and math.isfinite(v) and f['min']<=v<=f['max']
                if valid:
                    step=(v-f['min'])/f['increment'];valid=abs(step-round(step))<1e-6
            if not valid:raise InvalidDesign('Ungültiger Wert: '+f['label'])
        return deepcopy(value)

    def preview(self,value,interactive=True,view=None):
        s=self.settings(value)
        if view is None:view=dict(role='all',side='both',fit=True,comparison=False,scale=100)
        if not isinstance(view,dict) or set(view)!={'role','side','fit','comparison','scale'}:raise InvalidDesign('Bitte eine passende Figurenvorschau wählen.')
        if not isinstance(view['role'],str) or view['role'] not in ('all',*ROLES) or view['side'] not in ('both','light','dark') or type(view['fit']) is not bool or type(view['comparison']) is not bool or type(view['scale']) is not int or not 50<=view['scale']<=150 or view['scale']%5:
            raise InvalidDesign('Bitte eine passende Figurenvorschau wählen.')
        cfg=dict(settings=dict(renderer='design',figure=s),model=s['set'],representation=s['representation'],interactive=interactive,view=deepcopy(view))
        raw=json.dumps(cfg,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
        return (HERE/'piece-stage.html').read_text(encoding='utf-8').replace('<!--source-css-->','').replace('<!--config-->',raw)

    def validate_record(self,r):
        if not isinstance(r,dict) or set(r)!={'schema','id','name','settings','parent_id','created_at'} or type(r['schema']) is not int or r['schema']!=1:raise InvalidDesign('Unbekanntes Figurenformat.')
        if not isinstance(r['id'],str) or not IDENTIFIER.fullmatch(r['id']):raise InvalidDesign('Ungültige Figurenkennung.')
        text_value(r['name'],100,'Satzname',True);self.settings(r['settings'])
        if r['parent_id'] is not None and (not isinstance(r['parent_id'],str) or not IDENTIFIER.fullmatch(r['parent_id'])):raise InvalidDesign('Ungültiger Ausgangsentwurf.')
        if not isinstance(r['created_at'],str) or datetime.fromisoformat(r['created_at']).tzinfo is None:raise InvalidDesign('Ungültiger Speicherzeitpunkt.')
        return r

    def list(self):
        records=[];bad=0
        with self.lock:
            for path in self.directory.glob('piece-*.json'):
                try:
                    r=json.loads(path.read_text(encoding='utf-8'));self.validate_record(r)
                    if r['id']!=path.stem:raise InvalidDesign('Falscher Dateiname.')
                    records.append(r)
                except (ValueError,TypeError,OSError):bad+=1
        return sorted(records,key=lambda r:r['created_at'],reverse=True),bad

    def get(self,identifier):
        if not isinstance(identifier,str) or not IDENTIFIER.fullmatch(identifier):raise InvalidDesign('Unbekannter Figurensatz.')
        try:
            with self.lock:r=json.loads((self.directory/(identifier+'.json')).read_text(encoding='utf-8'))
        except (ValueError,OSError):raise InvalidDesign('Der Figurensatz konnte nicht gelesen werden.')
        if not isinstance(r,dict) or r.get('id')!=identifier:raise InvalidDesign('Die Figurenkennung passt nicht zur Datei.')
        return self.validate_record(r)

    def save(self,payload):
        if not isinstance(payload,dict) or set(payload)!={'name','settings','parent_id'}:raise InvalidDesign('Bitte einen vollständigen Figurensatz speichern.')
        s=self.settings(payload['settings']);name=text_value(payload['name'],100,'Satzname',True).strip();parent=payload['parent_id']
        if parent is not None:self.get(parent)
        record=dict(schema=1,id='piece-'+uuid4().hex,name=name,settings=s,parent_id=parent,created_at=datetime.now(timezone.utc).isoformat())
        with self.lock:
            self.directory.mkdir(parents=True,exist_ok=True)
            with (self.directory/(record['id']+'.json')).open('x',encoding='utf-8') as out:json.dump(record,out,ensure_ascii=False,indent=2,allow_nan=False)
        return record

    def asset(self,r):
        s=r['settings'];title='Schachfiguren' if s['set']=='chess' else 'Damesteine'
        return dict(kind='pieces',id=r['id'],name=r['name'],source='saved',variant='design',component='piece-design-v1',representation=s['representation'],
                    model_id='pieces-'+s['set']+'-v1',model_name=title,family=s['set'],family_name=title,editable=True,created=r['created_at'],
                    preview='/api/piece-designs/'+r['id']+'/preview',preview_width=720,preview_height=500,snapshot=deepcopy(r))

    def assets(self):return [self.asset(r) for r in self.list()[0]]
