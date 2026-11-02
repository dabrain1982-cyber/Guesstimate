"""Two existing dice renderers; counts, faces and colors are parameters, not records."""
import ast
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from urllib.parse import urlsplit
from library_store import ROOT, InvalidDesign

HERE=Path(__file__).resolve().parent
TABLE=ROOT/'static/dice-table.js'
CONQUEST=ROOT/'offline-preview/conquest-2-5d-v1'
THEME=ROOT/'static/vendor/dddice-outgunned'


def digest(path):return sha256(path.read_bytes()).hexdigest()


def fragment(source,start,end):
    if source.count(start)!=1 or source.count(end)!=1:
        raise InvalidDesign('Die Würfelquelle hat sich geändert; der Vorschauadapter muss geprüft werden.')
    return source[source.index(start):source.index(end)].strip()


class DiceLibrary:
    def __init__(self):
        self.constants={}
        for node in ast.parse((ROOT/'dice_table.py').read_text(encoding='utf-8')).body:
            if isinstance(node,ast.Assign):
                for target in node.targets:
                    if isinstance(target,ast.Name) and target.id in ('DICE_TABLE_THEME_ID','DICE_TABLE_D6_TYPE'):
                        self.constants[target.id]=ast.literal_eval(node.value)
        self.files={'/dice-components/stage.js':HERE/'dice-stage.js','/dice-components/stage.css':HERE/'dice-stage.css',
                    '/dice-source/dddice.js':ROOT/'static/vendor/dddice-0.21.8.js',
                    '/dice-source/conquest.css':CONQUEST/'style.css'}
        for file in THEME.iterdir():
            if file.is_file():self.files['/dice-source/assets/'+file.name]=file
        common=[HERE/'dice-stage.html',HERE/'dice-stage.js',HERE/'dice-stage.css',CONQUEST/'style.css',ROOT/'static/typography-v1.css']
        self.records={}
        for key,name,games,representation,paths in [
            ('physics','Räumliche Würfel · mit Physik',['Würfeltisch','Kniffel','Mäxchen'],'3d',
             [TABLE,ROOT/'dice_table.py',ROOT/'static/vendor/dddice-0.21.8.js',
              ROOT/'static/vendor/dddice-0.21.8.LICENSE.txt',ROOT/'static/vendor/dddice-0.21.8.THIRD-PARTY-NOTICES.txt',*THEME.iterdir()]),
            ('display','Flache Würfelanzeige · Conquest',['Conquest'],'2d',
             [CONQUEST/'attack.js',CONQUEST/'style.css',ROOT/'static/typography-v1.css'])]:
            evidence=[dict(path=p.relative_to(ROOT).as_posix(),sha256=digest(p)) for p in sorted(set(paths+common)) if p.is_file()]
            snapshot=dict(schema=1,kind='dice',component='game-dice-v1',renderer=key,
                          settings=dict(count=2,imprints=['1','2','3','4','5','6'],palette='original',
                                        die_type=self.constants['DICE_TABLE_D6_TYPE'] if key=='physics' else 'd6'),
                          parameters=dict(count='Anzahl innerhalb dieser Variante',imprints='Aufdrucke der sechs Seiten',
                                          palette='Körper-/Aufdruckfarben; keine zusätzlichen Grundmodelle'),
                          source=dict(path='static/dice-table.js' if key=='physics' else 'offline-preview/conquest-2-5d-v1/attack.js',
                                      functions=['localizeThemeAssets','createEngine','ensureEngine','animateRoll'] if key=='physics' else ['showRolls']),
                          evidence=evidence,editor_review='deferred',game_integration=False)
            identifier='dice-'+key+'-v1'
            self.records[identifier]=dict(kind='dice',id=identifier,name=name,source='preset',record_role='component',
                component='game-dice-v1',representation=representation,model_id=identifier,model_name=name,
                family=key,family_name='Räumlich mit Physik' if key=='physics' else 'Flache Anzeige',
                game=games[0],games=games,editable=False,usage='Wiederverwendbare Würfelvariante',
                preview='/api/dice/'+identifier+'/preview',preview_width=640,preview_height=400,snapshot=snapshot)
        self.physics_factory();self.flat_factory()

    def assets(self):return deepcopy(list(self.records.values()))

    def validate_sources(self,identifier):
        asset=self.records.get(identifier)
        if asset is None:raise InvalidDesign('Diese Würfelvariante ist nicht registriert.')
        for entry in asset['snapshot']['evidence']:
            if digest(ROOT/entry['path'])!=entry['sha256']:
                raise InvalidDesign('Die Würfelquelle wurde geändert. Bitte die Werkstatt neu laden.')
        return asset

    def physics_factory(self):
        source=TABLE.read_text(encoding='utf-8')
        blocks=[fragment(source,'const localizeThemeAssets =','const makeMiniDie ='),
                fragment(source,'const animateRoll =','const renderConcealed =')]
        return 'export function tableDice(scope){\nconst {room,canvas,engineStatus,fitRoom}=scope;\nconst savedCamera=null,cameraLocked=true,memberId=0;\nlet engine=null,enginePromise=null,lastRollId=0;\nconst visualDice=new Map();\nconst fallback=scope.fallback;\nconst showFallback=scope.showFallback;\n'+ '\n'.join(blocks)+'\nreturn {roll:async entries=>{lastRollId++;await animateRoll(entries);return engine;}};\n}'

    def flat_factory(self):
        source=(CONQUEST/'attack.js').read_text(encoding='utf-8')
        body=fragment(source,'function showRolls(','function record(')
        return 'const node=selector=>document.querySelector(selector);\nexport '+body

    def preview(self,identifier,interactive=False):
        asset=self.validate_sources(identifier)
        page=(HERE/'dice-stage.html').read_text(encoding='utf-8')
        if asset['representation']=='2d':page=page.replace('<script src="/dice-source/dddice.js" defer></script>','')
        return page.replace('data-renderer=""','data-renderer="'+asset['snapshot']['renderer']+'"').replace('data-interactive="false"','data-interactive="'+str(interactive).lower()+'"').replace('data-theme=""','data-theme="'+self.constants['DICE_TABLE_THEME_ID']+'"').replace('data-die-type=""','data-die-type="'+self.constants['DICE_TABLE_D6_TYPE']+'"')

    def file_path(self,path):return self.files.get(path)

    def http_get(self,handler,path):
        if not path.startswith('/api/dice/') and path not in ('/dice-source/physics.js','/dice-source/flat.js'):return False
        if path=='/dice-source/physics.js':
            self.validate_sources('dice-physics-v1');page,mime=self.physics_factory(),'text/javascript'
        elif path=='/dice-source/flat.js':
            self.validate_sources('dice-display-v1');page,mime=self.flat_factory(),'text/javascript'
        else:
            if not path.endswith('/preview'):raise InvalidDesign('Unbekannte Würfelvorschau.')
            identifier=path.removeprefix('/api/dice/').removesuffix('/preview')
            page,mime=self.preview(identifier,'interactive=1' in urlsplit(handler.path).query.split('&')),'text/html'
        raw=page.encode('utf-8');handler.send_response(200)
        handler.send_header('Content-Type',mime+'; charset=utf-8');handler.send_header('Content-Length',str(len(raw)))
        handler.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self'; connect-src 'self'; worker-src 'self' blob:; frame-ancestors 'self'; object-src 'none'; base-uri 'none'; form-action 'none'")
        handler.end_headers();handler.wfile.write(raw);return True
