"""2D and 3D boards; finite source appearances are configurations, never game states."""
from copy import deepcopy
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import re
from urllib.parse import parse_qs, urlsplit
from library_store import ROOT, HERE, PRESETS, InvalidDesign
from source_windows import Fragments
from dice_library import fragment

CONQUEST=ROOT/'offline-preview/conquest-2-5d-v1'
MODELS={'2d':'Brett · 2D','3d':'Brett · 3D'}
COVERAGE=[
    dict(game='Guesstimate',status='Kein eigenes Brett; Fragenfenster',source='templates/question.html'),
    dict(game='Guesstimate Party',status='Kein eigenes Brett; Fragenfenster',source='templates/party_question.html'),
    dict(game='Perfect',status='Kein eigenes Brett; Fragenfenster und Raumkulisse',source='templates/nerd_mode.html'),
    dict(game='Playtable',status='Gemeinsame Kartenfläche · 2D',source='templates/card_table_game.html'),
    *[dict(game=g,status='Eine gemeinsame Würfelfläche · 2D',source='templates/dice_table_game.html') for g in ('Würfeltisch','Kniffel','Mäxchen')],
    dict(game='Conquest',status='Ein Brettbild · 2D und vorhandener 3D-Tisch',source='templates/conquest_table.html')]


def digest(path):return sha256(path.read_bytes()).hexdigest()


def css_properties(path,selector):
    text=path.read_text(encoding='utf-8')
    match=re.search(r'^'+re.escape(selector)+r'\s*\{([^}]+)\}',text,re.M)
    if not match:raise InvalidDesign('Die Spielflächenquelle hat sich geändert: '+selector)
    return dict((k.strip(),v.strip()) for k,v in (part.split(':',1) for part in match[1].split(';') if ':' in part))


def pixels(value):
    if not re.fullmatch(r'\d+(?:\.\d+)?px',value):raise InvalidDesign('Die Spielflächenmaße brauchen eine erneute Prüfung.')
    return float(value[:-2])


class BoardLibrary:
    def __init__(self):
        self.records={}
        self.files={'/board-components/stage.js':HERE/'board-stage.js','/board-components/stage.css':HERE/'board-stage.css',
                    '/board-source/map.png':CONQUEST/'assets/karte.png','/board-source/territory-model.js':CONQUEST/'territory-model.js',
                    }
        for name in ('three.module.js','three.core.js'):
            self.files['/board-source/vendor/three/'+name]=CONQUEST/'vendor/three'/name
        generic=deepcopy(next(p['settings'] for p in PRESETS if p['kind']=='board'))
        side=generic['square']*generic['columns']+2*generic['border']
        common=[HERE/'board-stage.html',HERE/'board-stage.js',HERE/'board-stage.css',CONQUEST/'camera.js']
        self.common=common
        for representation in MODELS:
            self.register('base',representation,'Schach-/Damebrett · Grundkonfiguration',[],
                dict(renderer='grid',size=dict(width=side,depth=side,unit='Szeneneinheit'),shape=dict(type='rectangle'),
                     image=dict(type='generated',pattern=generic['pattern']),grid=generic),[HERE/'models.js'])
        meta=(CONQUEST/'territory-model.js').read_text(encoding='utf-8')
        numbers={key:float(re.search(r'export const '+key+r' = ([\d.]+);',meta)[1]) for key in ('MAP_WIDTH','MAP_HEIGHT','BOARD_WIDTH','BOARD_Y')}
        width=numbers['BOARD_WIDTH'];depth=width*numbers['MAP_HEIGHT']/numbers['MAP_WIDTH']
        for representation in MODELS:
            self.register('conquest',representation,'Conquest · Weltbrett', ['Conquest'],
                dict(renderer='image' if representation=='2d' else 'conquest',size=dict(width=width,depth=depth,unit='Szeneneinheit'),
                     shape=dict(type='rectangle',support='Tisch mit abgeschrägten Ecken' if representation=='3d' else None),
                     image=dict(type='file',path=(CONQUEST/'assets/karte.png').relative_to(ROOT).as_posix(),url='/board-source/map.png',width=numbers['MAP_WIDTH'],height=numbers['MAP_HEIGHT'])),
                [CONQUEST/'assets/karte.png',CONQUEST/'scene.js',CONQUEST/'territory-model.js',CONQUEST/'camera.js',ROOT/'templates/conquest_table.html'])
        card_css=ROOT/'static/card-table.css';card=css_properties(card_css,'.card-room')
        self.register('playtable','2d','Playtable · gemeinsame Kartenfläche',['Playtable'],
            dict(renderer='playtable',size=dict(width=pixels(card['width']),depth=pixels(card['height']),unit='Quellpixel'),
                 shape=dict(type='rectangle'),image=dict(type='file',path='static/card-table-felt-v1.png')),
            [card_css,ROOT/'static/card-table-felt-v1.png',ROOT/'templates/card_table_game.html'])
        dice_css=ROOT/'static/dice-table.css';room=css_properties(dice_css,'.dice-game-room');area=css_properties(dice_css,'.dice-render-area')
        w,h=pixels(room['width']),pixels(room['height']);x,y=pixels(area['left']),pixels(area['top'])
        self.register('dice-table','2d','Würfeltisch · gemeinsame Würfelfläche',['Würfeltisch','Kniffel','Mäxchen'],
            dict(renderer='dice-table',size=dict(width=w-x-pixels(area['right']),depth=h-y-pixels(area['bottom']),unit='Quellpixel'),
                 shape=dict(type='rectangle'),image=dict(type='file',path='static/dice-table-background-v2.png',
                     crop=dict(x=x,y=y,room_width=w,room_height=h))),
            [dice_css,ROOT/'static/dice-table-background-v2.png',ROOT/'templates/dice_table_game.html'])
        self.conquest_factory()

    def register(self,key,representation,name,games,settings,paths):
        identifier='boards-'+representation+'-'+key
        snapshot=dict(schema=1,kind='board',component='game-board-v1',settings=deepcopy(settings),
                      parameters=dict(size='Größe und Seitenverhältnis',shape='Form der Fläche',image='Bild bzw. Feldmuster'),
                      source_key=key,evidence=[dict(path=p.relative_to(ROOT).as_posix(),sha256=digest(p)) for p in sorted(set(self.common+paths))],
                      editor_review='deferred',game_integration=False)
        self.records[identifier]=dict(kind='board',id=identifier,name=name,source='game' if games else 'preset',
            component='game-board-v1',record_role='component_example' if games else 'component',canonical=False,
            representation=representation,model_id='board-'+representation+'-v1',model_name=MODELS[representation],
            family=representation,family_name='Flache Bretter und Spielflächen' if representation=='2d' else 'Räumliche Bretter',
            game=games[0] if games else '',games=games,usage='Vorhandene Brettkonfiguration' if games else 'Wiederverwendbare Grundvariante',
            editable=False,preview='/api/boards/'+identifier+'/preview',preview_width=640,preview_height=420,snapshot=snapshot)

    def assets(self):return deepcopy(list(self.records.values()))

    def validate_sources(self,identifier):
        asset=self.records.get(identifier)
        if asset is None:raise InvalidDesign('Diese Brettkonfiguration ist nicht registriert.')
        for entry in asset['snapshot']['evidence']:
            if digest(ROOT/entry['path'])!=entry['sha256']:raise InvalidDesign('Die Brettquelle wurde geändert. Bitte die Werkstatt neu laden.')
        return asset

    def conquest_factory(self):
        source=(CONQUEST/'scene.js').read_text(encoding='utf-8')
        declarations=fragment(source,'const boardWidth = BOARD_WIDTH;','const target =')
        factory=fragment(source,'function seededRandom(seed)', '// Each visible surface has one material.')
        return "import * as THREE from '/vendor/three.module.js';\nimport {BOARD_WIDTH,BOARD_DEPTH,BOARD_Y} from '/board-source/territory-model.js';\n"+declarations+'\n'+factory+'\nexport {makeTable,makeWoodTexture};'

    def preview(self,identifier,interactive=False):
        asset=self.validate_sources(identifier);cfg=deepcopy(asset['snapshot']['settings'])
        page=(HERE/'board-stage.html').read_text(encoding='utf-8')
        css=''
        if cfg['renderer']=='playtable':
            css='<link rel="stylesheet" href="/static/card-table.css">'
            markup=Fragments((ROOT/'templates/card_table_game.html').read_text(encoding='utf-8')).find({'class':'card-free-area'})['markup']
            if '{{' in markup or '{%' in markup:raise InvalidDesign('Die Kartenfläche braucht eine neue neutrale Erfassung.')
            cfg['markup']='<main class="card-room">'+markup+'</main>'
        if cfg['renderer']=='dice-table':
            css='<link rel="stylesheet" href="/static/dice-table.css">'
            cfg['markup']='<main class="dice-game-room" aria-label="Gemeinsame Würfelfläche"></main>'
        raw=json.dumps(dict(settings=cfg,representation=asset['representation'],interactive=interactive),ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
        return page.replace('<!--source-css-->',css).replace('<!--config-->',raw).replace('<title>Brettvorschau</title>','<title>'+escape(asset['name'])+'</title>')

    def file_path(self,path):return self.files.get(path)

    def http_get(self,handler,path):
        if path=='/board-source/camera.js':
            self.validate_sources('boards-3d-base')
            page,mime=(CONQUEST/'camera.js').read_text(encoding='utf-8').replace("'./vendor/three/three.module.js'","'/vendor/three.module.js'"),'text/javascript'
        elif path=='/board-source/conquest.js':
            self.validate_sources('boards-3d-conquest');page,mime=self.conquest_factory(),'text/javascript'
        elif path.startswith('/api/boards/'):
            if not path.endswith('/preview'):raise InvalidDesign('Unbekannte Brettvorschau.')
            query=parse_qs(urlsplit(handler.path).query)
            page,mime=self.preview(path.removeprefix('/api/boards/').removesuffix('/preview'),query.get('interactive')==['1']),'text/html'
        else:return False
        raw=page.encode('utf-8');handler.send_response(200);handler.send_header('Content-Type',mime+'; charset=utf-8');handler.send_header('Content-Length',str(len(raw)))
        handler.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self'; frame-ancestors 'self'; object-src 'none'; base-uri 'none'; form-action 'none'")
        handler.end_headers();handler.wfile.write(raw);return True

    def report(self):
        return dict(schema=1,models=MODELS,configurations=[dict(id=a['id'],name=a['name'],representation=a['representation'],games=a['games'],settings=deepcopy(a['snapshot']['settings'])) for a in self.records.values()],coverage=deepcopy(COVERAGE),
                    rule='Zwei Grundvarianten. Größe, Form und Bild sind Eigenschaften. Keine Partien, Länder oder Felder als eigene Brettbausteine.',
                    limits=['2,5D ist eine Ansicht der räumlichen Grundvariante.','Keine neuen 3D-Tische für reine 2D-Spielflächen erfunden.','Fragenfenster und vollständige Raumkulissen sind keine zusätzlichen Bretter.','Ältere Entwurfsbilder bleiben außerhalb der aktuellen Spielkonfigurationen.','Editoroptionen und Spielumstellung bleiben offen.'])
