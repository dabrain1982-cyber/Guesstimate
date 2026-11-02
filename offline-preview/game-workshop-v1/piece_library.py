"""Reusable existing pieces, isolated from game state and event handlers."""
from copy import deepcopy
import json
from urllib.parse import parse_qs, urlsplit
from library_store import HERE, ROOT, PRESETS, InvalidDesign
from dice_library import fragment, digest

CONQUEST=ROOT/'offline-preview/conquest-2-5d-v1'
MODELS={'chess':'Schachfiguren', 'checkers':'Damesteine', 'conquest':'Conquest · Truppenmarke'}
COVERAGE=[
    dict(game=game,source=source,model=model,finding=finding) for game,source,model,finding in [
        ('Guesstimate','templates/question.html',None,'Fragenfenster und Anzeigen; keine Spielsteine.'),
        ('Guesstimate Party','templates/party_question.html',None,'Spieleranzeigen und Pulte; keine Spielsteine.'),
        ('Perfect','templates/nerd_mode.html',None,'Fragenfenster, Pulte und Buzzer; keine Spielsteine.'),
        ('Playtable','templates/card_table_game.html',None,'Karten als eigener Bereich. Pokerchip-Motiv ist die bestehende Einsatzanzeige im Regler, kein beweglicher Spielstein.'),
        ('Würfeltisch','templates/dice_table_game.html',None,'Würfel und Anzeigen; keine zusätzlichen Spielsteine.'),
        ('Kniffel','templates/dice_table_game.html',None,'Würfel und Ergebnisblock; keine zusätzlichen Spielsteine.'),
        ('Mäxchen','templates/dice_table_game.html',None,'Würfel und Statusanzeigen; keine zusätzlichen Spielsteine.'),
        ('Conquest','offline-preview/conquest-2-5d-v1/territories.js','conquest','Ein gemeinsamer Sockel mit farbiger Zahlenfläche und Auswahlring; keine eigene Marke je Land oder Truppenzahl.')]]


class PieceLibrary:
    def __init__(self):
        self.records={}
        self.files={'/piece-components/stage.js':HERE/'piece-stage.js','/piece-components/stage.css':HERE/'piece-stage.css','/piece-components/authoring.js':HERE/'piece-authoring.js'}
        self.common=[HERE/'piece-stage.html',HERE/'piece-stage.js',HERE/'piece-stage.css',CONQUEST/'camera.js']
        for preset in (p for p in PRESETS if p['kind']=='pieces'):
            cfg=deepcopy(preset['settings']);key=cfg['set']
            for representation in ('2d','3d'):
                self.register(preset['id']+'-'+representation,preset['name']+' · '+representation.upper(),key,representation,[],
                    dict(renderer='generated',figure=cfg),[HERE/'models.js',HERE/'schema.json',HERE/'library_store.py'])
        # Palette is read directly from the pure source module by the preview.
        self.register('conquest','Conquest · vorhandene Truppenmarke','conquest','3d',['Conquest'],
            dict(renderer='conquest',count=8,palette_source='PREVIEW_ARMIES',selected=False),
            [CONQUEST/'territories.js',CONQUEST/'territory-model.js',CONQUEST/'style.css',ROOT/'templates/conquest_table.html'])
        self.conquest_factory()

    def register(self,key,name,model,representation,games,settings,paths):
        identifier='pieces-'+key
        parameters=dict(role='Figurenrolle innerhalb des Satzes' if model=='chess' else 'Steinform',
                        style='Formensprache und Proportionen',color='Farbe / Seite',count='Anzahl bzw. Zahlenwert',
                        size='Proportionale Gesamtgröße',state='Darstellungs- und Auswahlzustand')
        if model=='conquest':parameters['composition']='Räumlicher Sockel und projizierte Zahlenfläche gehören zusammen'
        snapshot=dict(schema=1,kind='pieces',component='game-pieces-v1',model=model,settings=deepcopy(settings),
            parameters=parameters,evidence=[dict(path=p.relative_to(ROOT).as_posix(),sha256=digest(p)) for p in sorted(set(self.common+paths))],
            editor_review='deferred',game_integration=False)
        self.records[identifier]=dict(id=identifier,kind='pieces',name=name,model_id='pieces-'+model+'-v1',model_name=MODELS[model],
            family=model,family_name=MODELS[model],source='game' if games else 'preset',game=games[0] if games else '',games=games,
            record_role='component_example',canonical=False,representation=representation,component='game-pieces-v1',
            usage='Vorhandener Spielbaustein' if games else 'Bisherige Werkstattvorlage',editable=False,
            preview='/api/pieces/'+identifier+'/preview',preview_width=640,preview_height=420,snapshot=snapshot)

    def assets(self):return deepcopy(list(self.records.values()))

    def validate_sources(self,identifier):
        asset=self.records.get(identifier)
        if asset is None:raise InvalidDesign('Diese Spielsteinkonfiguration ist nicht registriert.')
        for entry in asset['snapshot']['evidence']:
            if digest(ROOT/entry['path'])!=entry['sha256']:raise InvalidDesign('Die Spielsteinquelle wurde geändert. Bitte die Werkstatt neu laden.')
        return asset

    def conquest_factory(self):
        source=(CONQUEST/'territories.js').read_text(encoding='utf-8')
        geometry=fragment(source,'  const baseGeometry =','  function select(id)')
        body=fragment(source,'    const counter =',"    button.addEventListener('click'")
        entry=fragment(source,'    entries.set(id, { button, ring, anchor:', '\n  }\n  scene.add(group);')
        projection=fragment(source,'        projected.copy(anchor).project(camera);', '\n      }\n      arrowSvg.setAttribute')
        return ("import * as THREE from '/vendor/three.module.js';\nimport {PREVIEW_ARMIES} from '/piece-source/territory-model.js';\n"
            'export {PREVIEW_ARMIES};\nexport function makeCounter({owner,armies,name,layer}) {\n'
            "const BOARD_Y=0,point={x:0,z:0},id='preview',troopLabel=`${armies} Truppen`,group=new THREE.Group(),entries=new Map();\n"
            +geometry+body+'    layer.append(button);\n'+entry+'\nreturn {group,entries,button,ring};\n}\n'
            +'export function projectCounters(entries,camera,width,height) {\nconst projected=new THREE.Vector3();\nfor(const {button,anchor} of entries.values()){\n'+projection+'\n}\n}\n')

    def preview(self,identifier,interactive=False):
        asset=self.validate_sources(identifier)
        cfg=dict(settings=asset['snapshot']['settings'],model=asset['snapshot']['model'],representation=asset['representation'],interactive=interactive)
        raw=json.dumps(cfg,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
        css='<link rel="stylesheet" href="/piece-source/style.css">' if cfg['model']=='conquest' else ''
        return (HERE/'piece-stage.html').read_text(encoding='utf-8').replace('<!--source-css-->',css).replace('<!--config-->',raw)

    def file_path(self,path):return self.files.get(path)

    def http_get(self,handler,path):
        if path.startswith('/api/pieces/'):
            if not path.endswith('/preview'):raise InvalidDesign('Unbekannte Spielsteinvorschau.')
            query=parse_qs(urlsplit(handler.path).query)
            page,mime=self.preview(path.removeprefix('/api/pieces/').removesuffix('/preview'),query.get('interactive')==['1']),'text/html'
        elif path=='/piece-source/conquest.js':
            self.validate_sources('pieces-conquest');page,mime=self.conquest_factory(),'text/javascript'
        elif path in ('/piece-source/territory-model.js','/piece-source/style.css'):
            self.validate_sources('pieces-conquest')
            page,mime=(CONQUEST/path.rsplit('/',1)[1]).read_text(encoding='utf-8'),'text/css' if path.endswith('.css') else 'text/javascript'
        else:return False
        raw=page.encode('utf-8');handler.send_response(200);handler.send_header('Content-Type',mime+'; charset=utf-8');handler.send_header('Content-Length',str(len(raw)))
        handler.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self'; frame-ancestors 'self'; object-src 'none'; base-uri 'none'; form-action 'none'")
        handler.end_headers();handler.wfile.write(raw);return True

    def report(self):
        return dict(schema=1,models=MODELS,configurations=[dict(id=a['id'],name=a['name'],model=a['snapshot']['model'],representation=a['representation'],games=a['games']) for a in self.records.values()],
            coverage=deepcopy(COVERAGE),rule='Formfamilien als Bausteine. Rollen, Stil, Farben, Anzahl und Zustände als Eigenschaften; keine Bestände pro Land, Partie oder Spieler.',
            limits=['Schach und Dame sind vorhandene Werkstattvorlagen, keine zusätzlichen aktiven Spiele.','Conquest-Marke ist ein zusammengesetzter räumlicher Baustein mit flacher Zahlenfläche.','Karten, Würfel, Spielerporträts und reine Einsatzanzeigen bleiben in ihren Kategorien.','Editoroptionen und Spielintegration bleiben offen.'])
