"""Whole original room compositions, separate from boards, players and game state."""
from copy import deepcopy
from html import escape
import json
from urllib.parse import parse_qs,urlsplit
from library_store import ROOT,HERE,InvalidDesign
from source_windows import Fragments
from dice_library import digest,fragment

CONQUEST=ROOT/'offline-preview/conquest-2-5d-v1'


class RoomLibrary:
    def __init__(self,buttons):
        self.buttons=buttons;self.records={}
        self.files={'/room-components/stage.js':HERE/'room-stage.js','/room-components/stage.css':HERE/'room-stage.css'}
        self.common=[HERE/'room-stage.html',HERE/'room-stage.js',HERE/'room-stage.css',HERE/'room_library.py']
        for name in ('raum-wand-v2.png','moebel-v2.png','teppich.png'):
            self.files['/room-source/'+name]=CONQUEST/'assets'/name
        common=dict(body_class='has-player-background',body_style="--player-background-image:url('/shared/arena-stage-background-v1.png')")
        self.register('profile','Profilkulisse · Quiz und Party',['Guesstimate','Guesstimate Party','Perfect'],'2d',
            dict(renderer='css',markup='<div class="noise" aria-hidden="true"></div>',**common,
                 image_binding=dict(source='BACKGROUND_CATALOG',assets=['background-b'+str(i).zfill(2) for i in range(11)],css_property='--player-background-image')),
            'base.html',['static/arena-stage-background-v1.png'])
        for key,name,games,template,markup,asset in [
            ('collection','Games collection · gemeinsame Sammlungskulisse',['Perfect','Playtable','Würfeltisch','Kniffel','Mäxchen','Conquest'],'tabletop_connection.html','<main class="tabletop-connection"></main>','carousel-playtable-v1.png'),
            ('cards-lobby','Kartenraum · Lobby und Übersicht',['Playtable'],'card_table_index.html','<section class="lobby-browser" data-overview-game="cards"></section>','card-tables-background-v1.png'),
            ('dice-lobby','Würfelraum · Lobbys und Übersichten',['Würfeltisch','Kniffel','Mäxchen'],'dice_table_index.html','<section class="lobby-browser" data-overview-family="dice"></section>','dice-table-background-v2.png'),
            ('conquest-lobby','Conquest · Lobbykulisse',['Conquest'],'conquest_index.html','<section class="lobby-browser" data-overview-game="conquest"></section>','conquest-lobby-background-v1.png')]:
            self.register(key,name,games,'2d',dict(renderer='css',markup=markup,**common),template,['static/'+asset])
        self.register('cards-table','Playtable · vollständige Tischkulisse',['Playtable'],'2d',
            dict(renderer='css',markup='<main class="card-room"></main>',body_class='',body_style=''),
            'card_table_game.html',['static/card-table-felt-v1.png'],(1920,900))
        self.register('dice-table','Würfelspiele · vollständige Tischkulisse',['Würfeltisch','Kniffel','Mäxchen'],'2d',
            dict(renderer='css',markup='<main class="dice-game-room"></main>',body_class='',body_style=''),
            'dice_table_game.html',['static/dice-table-background-v2.png'],(1920,1080))
        source=buttons.read('templates/nerd_mode.html');decor=''
        for cls in ('perfect-curtain-left','perfect-curtain-right','perfect-lights','perfect-window','perfect-fireplace'):
            raw=Fragments(source).find({'class':cls})['markup']
            decor+=buttons.env.from_string(raw).render()
        self.register('perfect','Perfect · Clubraum mit ursprünglicher Raumgestaltung',['Perfect'],'2d',
            dict(renderer='css',markup='<main class="perfect-room">'+decor+'</main>',body_class='perfect-live phase-question',body_style=''),
            'nerd_mode.html',['static/stormseeds-perfect-clubroom-table-v2.png'])
        self.register('conquest','Conquest · räumlicher Spielraum',['Conquest'],'3d',
            dict(renderer='conquest',body_class='',body_style='',markup='',
                 layers=['raum-wand-v2.png','moebel-v2.png','teppich.png'],board_slot='Vorhandenes Brett separat zuordnen'),
            'conquest_table.html',[str((CONQUEST/p).relative_to(ROOT)) for p in ('scene.js','camera.js','territory-model.js','assets/raum-wand-v2.png','assets/moebel-v2.png','assets/teppich.png')])

    def register(self,key,name,games,representation,settings,template,paths,size=(1280,800)):
        settings=deepcopy(settings)
        settings['images']=['/shared/'+p.removeprefix('static/') for p in paths if p.startswith('static/') and p.endswith('.png')]
        identifier='rooms-'+key;styles=self.buttons.styles(template) if representation=='2d' else []
        dependencies=['templates/'+template,*styles,*paths]
        # CSS image/font dependencies are part of the source composition; the protected source stays unchanged.
        evidence=[dict(path=p.relative_to(ROOT).as_posix(),sha256=digest(p)) for p in sorted(set(self.common+[ROOT/p for p in dependencies]))]
        snapshot=dict(schema=1,kind='background',component='game-room-v1',settings=deepcopy(settings),styles=styles,
            source_template=template,evidence=evidence,parameters=dict(image='Vorhandenes Raum-/Profilmotiv',size='Proportionale Gesamtgröße',view='Ansicht der räumlichen Kulisse'),
            editor_review='deferred',game_integration=False)
        self.records[identifier]=dict(id=identifier,kind='background',name=name,game=games[0],games=games,source='game',representation=representation,
            component='game-room-v1',canonical=False,model_id='room-'+representation+'-v1',model_name='Raumkulisse · '+representation.upper(),
            family=representation,family_name='Flache Raumkulissen' if representation=='2d' else 'Räumliche Raumkulissen',
            usage='Vorhandene Raumkomposition ohne Spieloberfläche',editable=False,preview='/api/rooms/'+identifier+'/preview',
            preview_width=size[0],preview_height=size[1],snapshot=snapshot)

    def assets(self):return deepcopy(list(self.records.values()))

    def validate_sources(self,identifier):
        asset=self.records.get(identifier)
        if asset is None:raise InvalidDesign('Diese Raumkulisse ist nicht registriert.')
        for item in asset['snapshot']['evidence']:
            if digest(ROOT/item['path'])!=item['sha256']:raise InvalidDesign('Die Raumquelle wurde geändert. Bitte die Werkstatt neu laden.')
        return asset

    def conquest_factory(self):
        source=(CONQUEST/'scene.js').read_text(encoding='utf-8')
        room=fragment(source,'function buildRoom(wallTexture, furnitureTexture, rugTexture)', 'function frameView()')
        return "import * as THREE from '/vendor/three.module.js';\nexport function mountRoom(scene,wallTexture,furnitureTexture,rugTexture){\n"+room+"\nrugTexture.wrapS=rugTexture.wrapT=THREE.MirroredRepeatWrapping;\nbuildRoom(wallTexture,furnitureTexture,rugTexture);\n}\n"

    def preview(self,identifier,interactive=False):
        asset=self.validate_sources(identifier);snap=asset['snapshot'];cfg=dict(settings=snap['settings'],interactive=interactive)
        raw=json.dumps(cfg,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
        links=''.join('<link rel="stylesheet" href="/shared/'+escape(p.removeprefix('static/'),quote=True)+'">' for p in snap['styles'])
        page=(HERE/'room-stage.html').read_text(encoding='utf-8').replace('<!--source-css-->',links).replace('<!--config-->',raw)
        return page.replace('<!--body-class-->',escape(snap['settings']['body_class'],quote=True)).replace('<!--body-style-->',escape(snap['settings']['body_style'],quote=True))

    def file_path(self,path):return self.files.get(path)

    def http_get(self,handler,path):
        if path=='/room-source/conquest.js':
            self.validate_sources('rooms-conquest');page,mime=self.conquest_factory(),'text/javascript'
        elif path=='/room-source/territory-model.js':
            self.validate_sources('rooms-conquest');page,mime=(CONQUEST/'territory-model.js').read_text(encoding='utf-8'),'text/javascript'
        elif path.startswith('/api/rooms/'):
            if not path.endswith('/preview'):raise InvalidDesign('Unbekannte Raumvorschau.')
            query=parse_qs(urlsplit(handler.path).query);page,mime=self.preview(path.removeprefix('/api/rooms/').removesuffix('/preview'),query.get('interactive')==['1']),'text/html'
        else:return False
        raw=page.encode('utf-8');handler.send_response(200);handler.send_header('Content-Type',mime+'; charset=utf-8');handler.send_header('Content-Length',str(len(raw)))
        handler.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self'; frame-ancestors 'self'; object-src 'none'; base-uri 'none'; form-action 'none'")
        handler.end_headers();handler.wfile.write(raw);return True

    def report(self):return dict(configurations=[dict(id=a['id'],name=a['name'],games=a['games'],representation=a['representation']) for a in self.assets()],rule='Ganze Raumkompositionen; Wand, Möbel und Teppich gehören zusammen. Brett und Spieloberfläche bleiben eigene Bausteine.')
