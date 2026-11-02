"""Versioned avatar crops and frames; reuse image rendering and the real portrait."""
import ast
import base64
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from threading import Lock
from types import SimpleNamespace
from uuid import uuid4
from library_store import HERE, ROOT, InvalidDesign, text_value

DEFAULTS=dict(shape='original',frame='#17140f',background='#d8ff42',frame_width=3,size=100)
SHAPES={'original':'Wie im Spiel','round':'Rund','rounded':'Abgerundetes Quadrat','square':'Quadratisch'}
IDENTIFIER=re.compile(r'avatar-[a-f0-9]{32}')

class AvatarDesigns:
    def __init__(self,directory,images):
        self.directory=Path(directory)/'recipes/avatar-workshop';self.images=images;self.lock=Lock()
        # Execute only the public, pure catalog registration, never the Flask app.
        tree=ast.parse((ROOT/'player_portrait.py').read_text(encoding='utf-8'))
        function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='register_portraits')
        scope={};exec(compile(ast.Module(body=[function],type_ignores=[]),'player_portrait.py','exec'),scope)
        app=SimpleNamespace(extensions={})
        scope['register_portraits'](app,[dict(id=k.removeprefix('avatar-')) for k in images.existing if k.startswith('avatar-')])
        self.crops={'avatar-'+k:v['crop'] for k,v in app.extensions['player_portraits'].items()}
    def config(self):return dict(defaults=deepcopy(DEFAULTS),shapes=deepcopy(SHAPES),crops=deepcopy(self.crops),default_source='avatar-a01')
    def settings(self,value):
        if not isinstance(value,dict) or set(value)!=set(DEFAULTS):raise InvalidDesign('Die Avatargestaltung ist unvollständig.')
        if not isinstance(value['shape'],str) or value['shape'] not in SHAPES:raise InvalidDesign('Bitte eine Rahmenform wählen.')
        for key in ('frame','background'):
            if not isinstance(value[key],str) or not re.fullmatch(r'#[a-fA-F0-9]{6}',value[key]):raise InvalidDesign('Bitte eine gültige Farbe wählen.')
        if type(value['frame_width']) is not int or not 0<=value['frame_width']<=8:raise InvalidDesign('Bitte eine Rahmenstärke wählen.')
        if type(value['size']) is not int or not 50<=value['size']<=180 or value['size']%5:raise InvalidDesign('Bitte eine passende Anzeigegröße wählen.')
        return deepcopy(value)
    def render(self,source_id,recipe):
        if not isinstance(recipe,dict) or recipe.get('width')!=recipe.get('height') or recipe.get('output_width')!=512:raise InvalidDesign('Ein Avatar braucht einen quadratischen Ausschnitt.')
        raw,_,source=self.images.render(source_id,recipe)
        return raw,source
    def preview(self,source_id,recipe,settings,interactive=True):
        s=self.settings(settings);raw,_=self.render(source_id,recipe)
        cfg=dict(settings=s,image='data:image/png;base64,'+base64.b64encode(raw).decode(),interactive=interactive,reference_crop=self.crops.get('avatar-a02',dict(scale=1,top=0)))
        data=json.dumps(cfg,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
        return (HERE/'avatar-stage.html').read_text(encoding='utf-8').replace('<!--config-->',data)
    def validate_record(self,r):
        if not isinstance(r,dict) or set(r)!={'schema','id','name','source_id','source_snapshot','recipe','settings','parent_id','created_at'} or type(r['schema']) is not int or r['schema']!=1:raise InvalidDesign('Unbekanntes Avatarformat.')
        if not isinstance(r['id'],str) or not IDENTIFIER.fullmatch(r['id']):raise InvalidDesign('Ungültige Avatarkennung.')
        text_value(r['name'],100,'Avatarname',True);self.settings(r['settings'])
        # The source descriptor is pinned to the original image, including its checksum.
        info=self.images.info(r['source_id']);snapshot={k:info[k] for k in ('source_id','sha256','width','height')}
        if r['source_snapshot']!=snapshot:raise InvalidDesign('Die Bildquelle des Avatars wurde inzwischen verändert.')
        from image_store import validate_recipe
        validate_recipe(r['recipe'],info['width'],info['height'])
        if r['recipe']['width']!=r['recipe']['height'] or r['recipe']['output_width']!=512:raise InvalidDesign('Ungültiger Avatarausschnitt.')
        if r['parent_id'] is not None and (not isinstance(r['parent_id'],str) or not IDENTIFIER.fullmatch(r['parent_id'])):raise InvalidDesign('Ungültiger Ausgangsentwurf.')
        if not isinstance(r['created_at'],str) or datetime.fromisoformat(r['created_at']).tzinfo is None:raise InvalidDesign('Ungültiger Speicherzeitpunkt.')
        return r
    def list(self):
        records=[];bad=0
        with self.lock:
            for path in self.directory.glob('avatar-*.json'):
                try:
                    r=json.loads(path.read_text(encoding='utf-8'));self.validate_record(r)
                    if r['id']!=path.stem:raise InvalidDesign('Falscher Dateiname.')
                    records.append(r)
                except (ValueError,TypeError,OSError,KeyError):bad+=1
        return sorted(records,key=lambda r:r['created_at'],reverse=True),bad
    def get(self,key):
        if not isinstance(key,str) or not IDENTIFIER.fullmatch(key):raise InvalidDesign('Unbekannter Avatarentwurf.')
        try:
            with self.lock:r=json.loads((self.directory/(key+'.json')).read_text(encoding='utf-8'))
        except (ValueError,OSError):raise InvalidDesign('Der Avatarentwurf konnte nicht gelesen werden.')
        if not isinstance(r,dict) or r.get('id')!=key:raise InvalidDesign('Die Avatarkennung passt nicht zur Datei.')
        return self.validate_record(r)
    def save(self,value):
        if not isinstance(value,dict) or set(value)!={'name','source_id','recipe','settings','parent_id'}:raise InvalidDesign('Bitte den vollständigen Avatar speichern.')
        s=self.settings(value['settings']);name=text_value(value['name'],100,'Avatarname',True).strip()
        _,source=self.render(value['source_id'],value['recipe']);info=self.images.info(source['source_id'])
        parent=value['parent_id']
        if parent is not None:self.get(parent)
        r=dict(schema=1,id='avatar-'+uuid4().hex,name=name,source_id=source['source_id'],source_snapshot={k:info[k] for k in ('source_id','sha256','width','height')},recipe=deepcopy(value['recipe']),settings=s,parent_id=parent,created_at=datetime.now(timezone.utc).isoformat())
        with self.lock:
            self.directory.mkdir(parents=True,exist_ok=True)
            with (self.directory/(r['id']+'.json')).open('x',encoding='utf-8') as out:json.dump(r,out,ensure_ascii=False,indent=2,allow_nan=False)
        return r
    def asset(self,r):
        return dict(kind='avatars',id=r['id'],name=r['name'],source='saved',variant='design',component='avatar-design-v1',representation='2d',editable=True,
                    model_name=r['name'],created=r['created_at'],preview='/api/avatar-designs/'+r['id']+'/preview',preview_width=720,preview_height=520,snapshot=deepcopy(r))
    def assets(self):return [self.asset(r) for r in self.list()[0]]
