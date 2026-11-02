"""Whole custom decks, immutable versions; card contents are finite local equipment."""
from copy import deepcopy
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re
from threading import Lock
from uuid import uuid4
from library_store import HERE, InvalidDesign, text_value

FIELDS=[
    dict(key='representation',label='Ausführung',step=0,type='select',options={'3d':'3D · räumliche Karte','2d':'2D · flache Karte'}),
    dict(key='height',label='Kartenhöhe',step=0,type='range',min=5,max=30,increment=.05,unit='cm'),
    dict(key='ratio',label='Breite im Verhältnis zur Höhe',step=0,type='range',min=.55,max=1.4,increment=.05,percent=True),
    dict(key='front',label='Fläche der Vorderseite',step=1,type='color'),
    dict(key='ink',label='Schriftfarbe',step=1,type='color'),
    dict(key='front_accent',label='Rahmen der Vorderseite',step=1,type='color'),
    dict(key='symbol_color',label='Zeichenfarbe',step=1,type='color'),
    dict(key='back',label='Fläche der Rückseite',step=2,type='color'),
    dict(key='back_accent',label='Rahmen und Muster der Rückseite',step=2,type='color'),
    dict(key='back_pattern',label='Rückseitenmuster',step=2,type='select',options={'diamond':'Rauten','none':'Nur Rahmen'}),
    dict(key='edge',label='Kartenkante',step=2,type='color'),
]
DEFAULTS=dict(representation='3d',height=9,ratio=.7,front='#fff2d5',ink='#263d35',front_accent='#c59b4e',symbol_color='#c59b4e',
              back='#315c50',back_accent='#c59b4e',back_pattern='diamond',edge='#eee8d5')
SYMBOLS={'crown':'Krone','diamond':'Raute','star':'Stern','leaf':'Blatt','none':'Ohne Zeichen'}
MEMBERS=[dict(id='card-1',title='Dein nächster Zug',text='Hier beginnt eine neue Spielidee.',symbol='crown'),
         dict(id='card-2',title='Unerwarteter Besuch',text='Diese Karte gehört zu demselben Satz.',symbol='star')]
IDENTIFIER=re.compile(r'deck-[a-f0-9]{32}')

class CardDesigns:
    def __init__(self,directory):self.directory=Path(directory)/'recipes/card-workshop';self.lock=Lock()
    def config(self):return dict(fields=deepcopy(FIELDS),defaults=deepcopy(DEFAULTS),members=deepcopy(MEMBERS),symbols=deepcopy(SYMBOLS),max_cards=100)
    def settings(self,value):
        if not isinstance(value,dict) or set(value)!=set(DEFAULTS):raise InvalidDesign('Die Kartengestaltung ist unvollständig oder unbekannt.')
        for f in FIELDS:
            v=value[f['key']]
            if f['type']=='select':valid=isinstance(v,str) and v in f['options']
            elif f['type']=='color':valid=isinstance(v,str) and re.fullmatch(r'#[a-fA-F0-9]{6}',v)
            else:
                valid=type(v) in (int,float) and math.isfinite(v) and f['min']<=v<=f['max']
                if valid:
                    steps=(v-f['min'])/f['increment'];valid=abs(steps-round(steps))<1e-6
            if not valid:raise InvalidDesign('Ungültiger Wert: '+f['label'])
        return deepcopy(value)
    def members(self,value):
        if not isinstance(value,list) or not 1<=len(value)<=100:raise InvalidDesign('Ein eigener Satz braucht 1 bis 100 Karten.')
        seen=set()
        for member in value:
            if not isinstance(member,dict) or set(member)!={'id','title','text','symbol'}:raise InvalidDesign('Eine Karte ist unvollständig.')
            key=member['id']
            if not isinstance(key,str) or not re.fullmatch(r'card-[a-z0-9]{1,32}',key) or key in seen:raise InvalidDesign('Die Kartenkennungen müssen eindeutig sein.')
            seen.add(key);text_value(member['title'],55,'Kartentitel');text_value(member['text'],500,'Kartentext')
            if not isinstance(member['symbol'],str) or member['symbol'] not in SYMBOLS:raise InvalidDesign('Unbekanntes Kartenzeichen.')
        return deepcopy(value)
    def preview(self,settings,members,interactive=True,view=None,member_id=None):
        s=self.settings(settings);cards=self.members(members)
        if view is None:view=dict(member_id=member_id or cards[0]['id'],face='front',comparison=False,fit=True,scale=100,tilt=False)
        if not isinstance(view,dict):raise InvalidDesign('Bitte eine Kartenvorschau wählen.')
        view={'tilt':False,**view}
        if set(view)!={'member_id','face','comparison','fit','scale','tilt'}:raise InvalidDesign('Bitte eine Kartenvorschau wählen.')
        if view['member_id'] not in [m['id'] for m in cards] or view['face'] not in ('front','back','both') or type(view['comparison']) is not bool or type(view['fit']) is not bool or type(view['tilt']) is not bool or type(view['scale']) is not int or not 50<=view['scale']<=150 or view['scale']%5:raise InvalidDesign('Bitte eine passende Kartenvorschau wählen.')
        cfg=dict(settings=s,members=cards,interactive=interactive,view=deepcopy(view))
        raw=json.dumps(cfg,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
        return (HERE/'card-design-stage.html').read_text(encoding='utf-8').replace('<!--config-->',raw)
    def validate_record(self,r):
        if not isinstance(r,dict) or set(r)!={'schema','id','name','settings','members','parent_id','created_at'} or type(r['schema']) is not int or r['schema']!=1:raise InvalidDesign('Unbekanntes Kartensatzformat.')
        if not isinstance(r['id'],str) or not IDENTIFIER.fullmatch(r['id']):raise InvalidDesign('Ungültige Kartensatzkennung.')
        text_value(r['name'],100,'Satzname',True);self.settings(r['settings']);self.members(r['members'])
        if r['parent_id'] is not None and (not isinstance(r['parent_id'],str) or not IDENTIFIER.fullmatch(r['parent_id'])):raise InvalidDesign('Ungültiger Ausgangsentwurf.')
        if not isinstance(r['created_at'],str) or datetime.fromisoformat(r['created_at']).tzinfo is None:raise InvalidDesign('Ungültiger Speicherzeitpunkt.')
        return r
    def list(self):
        records=[];bad=0
        with self.lock:
            for path in self.directory.glob('deck-*.json'):
                try:
                    r=json.loads(path.read_text(encoding='utf-8'));self.validate_record(r)
                    if r['id']!=path.stem:raise InvalidDesign('Falscher Dateiname.')
                    records.append(r)
                except (ValueError,TypeError,OSError):bad+=1
        return sorted(records,key=lambda r:r['created_at'],reverse=True),bad
    def get(self,key):
        if not isinstance(key,str) or not IDENTIFIER.fullmatch(key):raise InvalidDesign('Unbekannter Kartensatz.')
        try:
            with self.lock:r=json.loads((self.directory/(key+'.json')).read_text(encoding='utf-8'))
        except (ValueError,OSError):raise InvalidDesign('Der Kartensatz konnte nicht gelesen werden.')
        if not isinstance(r,dict) or r.get('id')!=key:raise InvalidDesign('Die Kartenkennung passt nicht zur Datei.')
        return self.validate_record(r)
    def save(self,value):
        if not isinstance(value,dict) or set(value)!={'name','settings','members','parent_id'}:raise InvalidDesign('Bitte den ganzen Kartensatz speichern.')
        s=self.settings(value['settings']);cards=self.members(value['members']);name=text_value(value['name'],100,'Satzname',True).strip();parent=value['parent_id']
        if parent is not None:self.get(parent)
        r=dict(schema=1,id='deck-'+uuid4().hex,name=name,settings=s,members=cards,parent_id=parent,created_at=datetime.now(timezone.utc).isoformat())
        with self.lock:
            self.directory.mkdir(parents=True,exist_ok=True)
            with (self.directory/(r['id']+'.json')).open('x',encoding='utf-8') as out:json.dump(r,out,ensure_ascii=False,indent=2,allow_nan=False)
        return r
    def asset(self,r):
        model='movable' if r['settings']['representation']=='3d' else 'display'
        return dict(kind='cards',id=r['id'],name=r['name'],source='saved',variant='design',component='card-design-v1',representation=r['settings']['representation'],
                    model_id='cards-'+model+'-v1',model_name='Bewegliche Karten · 3D' if model=='movable' else 'Anzeige- und Auswahlkarten · flach',
                    family='custom-set',family_name='Eigene Kartensätze',editable=True,record_role='finite_set',created=r['created_at'],
                    preview='/api/card-designs/'+r['id']+'/preview',preview_width=720,preview_height=520,snapshot=deepcopy(r))
    def assets(self):return [self.asset(r) for r in self.list()[0]]
