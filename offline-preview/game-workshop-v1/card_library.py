"""Reusable card bodies and finite equipment sets, never individual questions."""
from copy import deepcopy
from hashlib import sha256
from html import escape
import importlib.util
import json
from pathlib import Path
import re
from urllib.parse import parse_qs,urlsplit
from library_store import ROOT,InvalidDesign
from card_contents import standard_sets,conquest_sets
HERE=ROOT/'offline-preview/card-comparison-v1'
MODELS={'movable':dict(name='Bewegliche Karten · 3D',representation='3d',mode='model',interaction='move'),'display':dict(name='Anzeige- und Auswahlkarten · flach',representation='2d',mode='graphic',interaction='select')}
FAMILIES={'movable':'Bewegliche Karte','display':'Flache Karte','standard-set':'Spielkartensätze','conquest-set':'Conquest-Kartensätze'}
def digest(path):return sha256(path.read_bytes()).hexdigest()
class CardLibrary:
    def __init__(self):
        self.records={}
        spec=importlib.util.spec_from_file_location('card_comparison_server',HERE/'serve.py')
        self.comparison=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.comparison)
        self.model_metadata=json.loads((HERE/'assets/import-manifest.json').read_text(encoding='utf-8'))['model']
        base=['offline-preview/card-comparison-v1/'+n for n in ('stage.js','stage.css','stage.html','serve.py','body.js')]+['static/card-table.js','static/card-table.css','offline-preview/game-workshop-v1/content-card.js']
        self.base_evidence=[dict(path=p,sha256=digest(ROOT/p)) for p in base]
        standards=standard_sets()
        for model in MODELS:
            self.register(model)
            for pack in standards:self.register(model,pack)
        for pack in conquest_sets():self.register('display',pack)
    def register(self,model,pack=None):
        meta=MODELS[model];identifier='cards-'+('set-'+model+'-'+pack['key'] if pack else 'component-'+model)
        paths=['assets/kenney/license.txt','assets/import-manifest.json','assets/kenney/cardBack_blue2.png']
        members=pack['members']+pack['supplements'] if pack else [dict(key='Hearts7')]
        paths+=['assets/kenney/card'+m['key']+'.png' for m in members if m.get('key')]
        if model=='movable':paths+=['assets/mehrasaur/'+n for n in ('card-mesh.json','card.obj','card.mtl','card.blend','provenance.txt')]
        evidence=deepcopy(self.base_evidence)+[dict(path=(HERE/p).relative_to(ROOT).as_posix(),sha256=digest(HERE/p)) for p in sorted(set(paths))]
        if pack:evidence += [dict(path=p,sha256=digest(ROOT/p)) for p in pack['evidence']]
        snapshot=dict(schema=2,kind='cards',component='approved-card-v1',model_id='cards-'+model+'-v1',settings=dict(mode=meta['mode'],card='Hearts7',back=False,back_art='cardBack_blue2.png',layout='single',angle=32 if model=='movable' else 0,zoom=100 if pack and pack['game']=='Conquest' else 125,interaction=meta['interaction']),geometry=deepcopy(self.model_metadata) if model=='movable' else None,licenses=[dict(author='Kenney Vleugels',license='CC0-1.0',scope='Graphic assets only',url='https://kenney.nl/assets/boardgame-pack')],evidence=evidence,game_integration=False,editor_review='deferred')
        if model=='movable':snapshot['licenses'].append(dict(author='mehrasaur',license='CC0-1.0',url='https://opengameart.org/content/poker-pack'))
        if pack:
            snapshot['set']=deepcopy(pack);snapshot['set'].update(member_count=len(pack['members']),supplement_count=len(pack['supplements']))
        family=pack['family'] if pack else model
        self.records[identifier]=dict(kind='cards',id=identifier,name=pack['name'] if pack else meta['name']+' · Grundbaustein',source='set' if pack else 'preset',record_role='finite_set' if pack else 'component',component='approved-card-v1',representation=meta['representation'],model_id='cards-'+model+'-v1',model_name=meta['name'],family=family,family_name=FAMILIES[family],game=pack['game'] if pack else '',editable=False,usage='Endlicher Kartensatz' if pack else 'Wiederverwendbarer Kartenbaustein',preview='/api/cards/'+identifier+'/preview',preview_width=520,preview_height=440,snapshot=snapshot)
    def assets(self):return deepcopy(list(self.records.values()))
    def legacy(self,identifier):
        # Read old saved card choices without advertising individual cards.
        match=re.fullmatch(r'cards-(movable|display)-(hearts|spades|clubs|diamonds)(a|k|q|j|10|[2-9])',identifier)
        back=re.fullmatch(r'cards-(movable|display)-(blue|green|red)([1-5])',identifier)
        joker=re.fullmatch(r'cards-(movable|display)-joker',identifier)
        if not (match or back or joker):return None
        model=(match or back or joker)[1];a=deepcopy(self.records['cards-component-'+model]);a['id']=identifier
        if match:a['snapshot']['settings']['card']=match[2].capitalize()+match[3].upper()
        if joker:a['snapshot']['settings']['card']='Joker'
        if back:a['snapshot']['settings'].update(back=True,back_art='cardBack_'+back[2]+back[3]+'.png')
        return a
    def preview(self,identifier,interactive=False,member=None):
        asset=self.records.get(identifier) or self.legacy(identifier)
        if asset is None:raise InvalidDesign('Dieser Kartenbaustein oder Kartensatz ist nicht registriert.')
        for entry in asset['snapshot']['evidence']:
            if digest(ROOT/entry['path'])!=entry['sha256']:raise InvalidDesign('Die Kartenquelle wurde geändert. Bitte die Werkstatt neu laden.')
        cfg=deepcopy(asset['snapshot']['settings']);payload=None;pack=asset['snapshot'].get('set')
        if pack:
            choices=pack['members']+pack['supplements'];selected=next((v for v in choices if v['id']==member),None) if member else choices[0]
            if selected is None:raise InvalidDesign('Diese Karte gehört nicht zu diesem Satz.')
            cfg['card']=selected.get('key','Hearts7');payload=selected.get('content')
            if payload:cfg['interaction']='select' if payload['kind']=='country' else 'read'
        attrs=dict(card_mode=cfg['mode'],card_key=cfg['card'],card_back=cfg['back_art'],card_face_down=str(cfg['back']).lower(),card_angle=str(cfg['angle']),card_zoom=str(cfg['zoom']),card_layout=cfg['layout'],card_interaction=cfg['interaction'] if interactive else 'none')
        body='<body '+' '.join('data-'+k.replace('_','-')+'="'+escape(v,quote=True)+'"' for k,v in attrs.items())+'>'
        if payload:
            raw=json.dumps(payload,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026');body+='<script type="application/json" id="card-content">'+raw+'</script>'
        return (HERE/'stage.html').read_text(encoding='utf-8').replace('<body>',body).replace('href="stage.css"','href="/card-components/stage.css"').replace('src="stage.js"','src="/card-components/stage.js"').replace('<title>Kartenvorschau</title>','<title>'+escape(asset['name'])+'</title>')
    def file_path(self,path):
        routes={'/card-components/stage.js':HERE/'stage.js','/card-components/stage.css':HERE/'stage.css','/card-components/body.js':HERE/'body.js','/card-components/content-card.js':Path(__file__).parent/'content-card.js','/original/card.css':ROOT/'static/card-table.css','/original/guesstimate-card-back-v1.png':ROOT/'static/guesstimate-card-back-v1.png'}
        for name in ('cards.js','territory-model.js','assets/karte.png'):routes['/card-content/conquest/'+name]=ROOT/'offline-preview/conquest-2-5d-v1'/name
        if path in routes:return routes[path]
        if path.startswith(('/assets/kenney/','/assets/mehrasaur/')):
            file=(HERE/path.lstrip('/')).resolve()
            if file.is_relative_to(HERE/'assets') and file.is_file() and file.suffix in ('.png','.json','.obj','.mtl','.blend','.txt'):return file
        return None
    def http_get(self,handler,path):
        if path!='/original/card.js' and not path.startswith('/api/cards/'):return False
        try:
            if path=='/original/card.js':page,mime=self.comparison.original_factory(),'text/javascript'
            else:
                if not path.endswith('/preview'):raise InvalidDesign('Unbekannte Kartenvorschau.')
                query=parse_qs(urlsplit(handler.path).query);page=self.preview(path.removeprefix('/api/cards/').removesuffix('/preview'),query.get('interactive')==['1'],query.get('member',[None])[0]);mime='text/html'
            raw=page.encode('utf-8');handler.send_response(200);handler.send_header('Content-Type',mime+'; charset=utf-8');handler.send_header('Content-Length',str(len(raw)))
            handler.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'self'; object-src 'none'; base-uri 'none'; form-action 'none'");handler.end_headers();handler.wfile.write(raw)
        except (OSError,ValueError) as error:handler.json_response({'error':str(error)},400)
        return True
    def report(self):
        packs=[a for a in self.records.values() if a['record_role']=='finite_set']
        return dict(schema=2,models=2,library_entries=len(self.records),finite_sets=len(packs),question_entries=0,sets=[dict(id=a['id'],name=a['name'],representation=a['representation'],members=a['snapshot']['set']['member_count'],supplements=a['snapshot']['set']['supplement_count']) for a in packs],distinction='Reusable component -> finite equipment set -> members inside the set. Questions bind to windows by schema reference.',limits=['No game changes.','Question banks and private drafts are not rewritten.','Editor options remain deferred.'])
