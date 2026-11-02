"""Finite original game artwork, flyer compositions and reusable symbol sets."""
from copy import deepcopy
from html import escape
import json
import re
from urllib.parse import parse_qs, urlsplit
from PIL import Image
from library_store import HERE, ROOT, InvalidDesign
from source_windows import Fragments, InertMarkup
from dice_library import fragment, digest

CONQUEST=ROOT/'offline-preview/conquest-2-5d-v1'
GAMES=['Guesstimate','Guesstimate Party','Perfect','Playtable','Würfeltisch','Kniffel','Mäxchen','Conquest']
MODEL_NAMES={'artwork':'Spielmotive','logo':'Mäxchen · Logo','carousel':'Startseiten-Flyer','tile':'Gemeinsame Spielkachel',
             'perfect-tile':'Perfect · Spielkachel','quiz':'Quiz · Fragetypen','navigation':'Navigation',
             'comic':'Comic · Aktionssymbole','equipment':'Conquest · Kartensymbole','stats':'Spieler · Statistikzeichen','favicon':'App-Symbol'}


class GraphicLibrary:
    def __init__(self,buttons):
        self.buttons=buttons;self.records={}
        self.files={'/graphic-components/stage.js':HERE/'graphic-stage.js','/graphic-components/stage.css':HERE/'graphic-stage.css',
                    '/graphic-source/comic.js':ROOT/'offline-preview/comic-ui-v1/components.js',
                    '/graphic-source/player-portrait.js':ROOT/'static/player-portrait.js'}
        self.common=[HERE/'graphic-stage.html',HERE/'graphic-stage.css',HERE/'graphic-stage.js',HERE/'graphic_library.py']
        self.capture_artwork();self.capture_flyers();self.capture_icons()

    def rendered(self,name,values=None):
        source=self.buttons.read('templates/'+name)
        content=source.split('{% block content %}',1)[1].split('{% endblock %}',1)[0]
        prefix='{% from "_game_flyers.html" import perfect_flyer, conquest_flyer, perfect_flyer_copy %}{% set is_dice = family == "dice" %}'
        return self.buttons.env.from_string(prefix+content).render(**(values or {}))

    def register(self,key,kind,model,name,games,settings,paths,styles=(),members=()):
        identifier='graphics-'+key;styles=list(styles)
        paths=set(self.common+[str(p) for p in paths]+styles)
        paths={ROOT/p if isinstance(p,str) else p for p in paths}
        snapshot=dict(schema=1,kind=kind,component='game-graphics-v1',model=model,settings=deepcopy(settings),
            parameters=dict(motif='Bild oder Symbol innerhalb des endlichen Bestands',size='Proportionale Gesamtgröße',
                            text='Vorhandene Beschriftung der gemeinsamen Komposition'),
            styles=styles,evidence=[dict(path=p.relative_to(ROOT).as_posix(),sha256=digest(p)) for p in sorted(paths)],
            editor_review='deferred',game_integration=False)
        if members:snapshot['symbol_set']=dict(members=deepcopy(list(members)),member_count=len(members))
        self.records[identifier]=dict(id=identifier,kind=kind,name=name,source='game',game=games[0] if games else '',games=games,
            representation='2d',component='game-graphics-v1',canonical=False,record_role='finite_symbol_set' if members else 'component_example',
            model_id='graphics-'+model+'-v1',model_name=MODEL_NAMES[model],family=model,family_name=MODEL_NAMES[model],
            usage='Vorhandener Symbolsatz' if members else 'Originales Spielmotiv' if kind=='titles' else 'Vorhandene Spielpräsentation',editable=False,
            preview='/api/graphics/'+identifier+'/preview',preview_width=640,preview_height=460,snapshot=snapshot)

    def capture_artwork(self):
        entries=[
            ('daily','Guesstimate','carousel-daily-quiz-v1.png',[GAMES[0]]),
            ('party','Guesstimate Party','carousel-party-classic-v1.png',[GAMES[1]]),
            ('perfect','Perfect','carousel-stormseeds-perfect-v1.png',['Perfect']),
            ('collection','Games collection','carousel-playtable-v1.png',['Playtable','Würfeltisch','Kniffel','Mäxchen','Perfect','Conquest']),
            ('cards','Playtable','tabletop-card-table-tile-v1.png',['Playtable']),
            ('dice','Gemeinsames Würfelmotiv','tabletop-dice-table-tile-v1.png',['Würfeltisch','Mäxchen']),
            ('kniffel','Kniffel','tabletop-kniffel-tile-v1.png',['Kniffel']),
            ('conquest','Conquest','tabletop-risk-tile-v1.png',['Conquest'])]
        for key,name,file,games in entries:
            path=ROOT/'static'/file
            with Image.open(path) as image:size=dict(width=image.width,height=image.height)
            self.register('artwork-'+key,'titles','artwork',name+' · Bildmotiv',games,
                dict(renderer='image',url='/shared/'+file,asset='static/'+file,**size),
                ['static/'+file,'templates/home.html','templates/_game_flyers.html','templates/tabletop_family.html','templates/tabletop_connection.html','static/quiz-arena.css'])
        self.register('maexchen-logo','titles','logo','Mäxchen · vorhandenes Logo',['Mäxchen'],
            dict(renderer='image',url='/shared/maexchen-logo-v1.svg',asset='static/maexchen-logo-v1.svg'),
            ['static/maexchen-logo-v1.svg','static/dice-table.css','templates/dice_table_game.html'])

    def capture_flyers(self):
        styles=self.buttons.styles('home.html');page=self.buttons.read('templates/home.html')
        for index,(key,name,games) in enumerate([('daily','Guesstimate',[GAMES[0]]),('party','Guesstimate Party',[GAMES[1]]),
                ('perfect','Perfect',['Perfect']),('collection','Games collection',GAMES[2:])]):
            row=Fragments(page).find({'data-game-slide':str(index)})
            # Only the chosen general game slide is captured. Personal greetings stay outside the catalog.
            original=self.buttons.env.from_string('{% from "_game_flyers.html" import perfect_flyer_copy %}'+row['markup']).render()
            markup=''.join(InertMarkup(original,root=True).parts)
            asset=self.records['graphics-artwork-'+key]['snapshot']['settings']['asset']
            self.register('flyer-'+key,'flyers','carousel',name+' · Startseiten-Flyer',games,
                dict(renderer='markup',markup='<div class="home-variant-a"><div class="variant-a-slides">'+markup+'</div></div>',width=640,height=580),
                ['templates/home.html','templates/_game_flyers.html',asset],styles)
        for family in ('boards','dice','cards'):
            page=self.rendered('tabletop_family.html',dict(family=family))
            rows=sorted((r for r in Fragments(page).elements if 'tabletop-game-tile' in (r['attrs'].get('class') or '').split() and 'is-coming' not in (r['attrs'].get('class') or '')),key=lambda r:r['start'])
            specs={'boards':[('perfect',['Perfect']),('conquest',['Conquest'])],
                   'dice':[('dice',['Würfeltisch']),('kniffel',['Kniffel']),('maexchen',['Mäxchen'])],
                   'cards':[('cards',['Playtable'])]}[family]
            if len(rows)!=len(specs):raise InvalidDesign('Die Spielkacheln brauchen eine erneute Zuordnung.')
            for row,(key,games) in zip(rows,specs):
                markup=''.join(InertMarkup(row['markup'],root=True).parts)
                self.register('tile-'+key,'flyers','perfect-tile' if key=='perfect' else 'tile',games[0]+' · Spielkachel',games,
                    dict(renderer='markup',markup=markup,width=330,height=330),
                    ['templates/tabletop_family.html','templates/_game_flyers.html',*self.image_refs(markup)],self.buttons.styles('tabletop_family.html'))
        page=self.rendered('tabletop_connection.html')
        rows=sorted((r for r in Fragments(page).elements if 'tabletop-game-tile' in (r['attrs'].get('class') or '').split()),key=lambda r:r['start'])
        for row,(key,name,games) in zip(rows,[('cards','Kartentische',['Playtable']),('dice','Würfeltische',['Würfeltisch','Kniffel','Mäxchen']),('boards','Brettspiele',['Perfect','Conquest'])]):
            markup=''.join(InertMarkup(row['markup'],root=True).parts)
            self.register('family-'+key,'flyers','tile',name+' · Gruppenkachel',games,dict(renderer='markup',markup=markup,width=330,height=330),
                ['templates/tabletop_connection.html',*self.image_refs(markup)],self.buttons.styles('tabletop_connection.html'))

    @staticmethod
    def image_refs(markup):return ['static/'+p.split('?',1)[0] for p in re.findall(r'/shared/([^\"<> ]+)',markup)]

    def capture_icons(self):
        members=[dict(id=key,name=name) for key,name in [('multiple_choice','Antwortauswahl'),('true_false','Wahr / Falsch'),('estimate','Schätzen'),('order','Sortieren'),('match','Zuordnen')]]
        for member in members:member['markup']=str(self.buttons.env.globals['category_icon'](member['id']))
        self.register('icons-quiz','icons','quiz','Quiz · fünf Fragetypen',[GAMES[0],GAMES[1]],dict(renderer='symbols',factory='markup'),
            ['templates/_icons.html','static/category-sprite.png'],self.buttons.styles('base.html'),members)
        rows=sorted((r for r in Fragments(self.buttons.read('templates/base.html')).elements if r['tag']=='svg' and 'nav-icon' in (r['attrs'].get('class') or '').split()),key=lambda r:r['start'])
        if len(rows)!=4:raise InvalidDesign('Die Navigationssymbole brauchen eine neue Erfassung.')
        members=[dict(id=key,name=name,markup='<span class="arena-main-nav graphic-ancestor">'+row['markup']+'</span>') for row,(key,name) in zip(rows,[('profile','Profil'),('shop','Shop'),('rules','Regeln'),('date','Kalender')])]
        self.register('icons-navigation','icons','navigation','Gemeinsame Navigation',GAMES,dict(renderer='symbols',factory='markup'),['templates/base.html'],self.buttons.styles('base.html'),members)
        path=ROOT/'offline-preview/comic-ui-v1/components.js';source=path.read_text(encoding='utf-8')
        keys=re.findall(r'^  (\w+):',fragment(source,'const paths = {','export function icon'),re.M)
        names=dict(arrow='Pfeil',cards='Karten',flag='Flagge',army='Armee',plus='Plus',sword='Schwert',shield='Schild',reset='Zurücksetzen',play='Start',pause='Pause',bolt='Blitz',keyboard='Tastatur',hand='Hand',check='Haken',dice='Würfel')
        self.register('icons-comic','icons','comic','Gemeinsame Comic-Symbole',['Conquest'],dict(renderer='symbols',factory='comic'),
            ['offline-preview/comic-ui-v1/components.js','offline-preview/conquest-2-5d-v1/game-buttons.js'],['static/comic-button.css'],[dict(id=k,name=names.get(k,k)) for k in keys])
        self.register('icons-equipment','icons','equipment','Conquest · Ausstattungszeichen',['Conquest'],dict(renderer='symbols',factory='equipment'),
            ['offline-preview/conquest-2-5d-v1/cards.js'],[],[dict(id=k,name=n) for k,n in [('infantry','Infanterie'),('cavalry','Reiter'),('artillery','Geschütz')]])
        self.register('icons-stats','icons','stats','Spieler · Truppen und Länder',['Conquest'],dict(renderer='symbols',factory='stats'),
            ['static/player-portrait.js'],['static/player-portrait.css'],[dict(id=k,name=n) for k,n in [('troops','Truppen'),('countries','Länder')]])
        self.register('icons-favicon','icons','favicon','Vorhandenes App-Symbol',GAMES,dict(renderer='image',url='/shared/favicon.svg',asset='static/favicon.svg'),['static/favicon.svg','templates/base.html'])

    def assets(self):return deepcopy(list(self.records.values()))

    def validate_sources(self,identifier):
        asset=self.records.get(identifier)
        if asset is None:raise InvalidDesign('Dieser Bildbaustein ist nicht registriert.')
        for entry in asset['snapshot']['evidence']:
            if digest(ROOT/entry['path'])!=entry['sha256']:raise InvalidDesign('Die Bildquelle wurde geändert. Bitte die Werkstatt neu laden.')
        return asset

    def equipment_factory(self):
        source=(CONQUEST/'cards.js').read_text(encoding='utf-8')
        labels=next(line for line in source.splitlines() if line.startswith('export const SYMBOL_LABELS ='))
        return labels+'\n'+fragment(source,'const ICONS = {','export function createCountryCard')+'\nexport {symbolImage};\n'

    def preview(self,identifier,member=None):
        asset=self.validate_sources(identifier);snapshot=asset['snapshot'];cfg=deepcopy(snapshot['settings'])
        members=snapshot.get('symbol_set',{}).get('members',[])
        if member and not any(m['id']==member for m in members):raise InvalidDesign('Dieses Motiv gehört nicht zum Symbolsatz.')
        cfg['members']=[m for m in members if not member or m['id']==member]
        links=''.join('<link rel="stylesheet" href="/shared/'+escape(p.removeprefix('static/'),quote=True)+'">' for p in snapshot['styles'])
        raw=json.dumps(cfg,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
        return (HERE/'graphic-stage.html').read_text(encoding='utf-8').replace('<!--source-css-->',links).replace('<!--config-->',raw)

    def file_path(self,path):return self.files.get(path)

    def http_get(self,handler,path):
        if path=='/graphic-source/equipment.js':
            self.validate_sources('graphics-icons-equipment');page,mime=self.equipment_factory(),'text/javascript'
        elif path.startswith('/api/graphics/'):
            if not path.endswith('/preview'):raise InvalidDesign('Unbekannte Bildvorschau.')
            query=parse_qs(urlsplit(handler.path).query)
            page,mime=self.preview(path.removeprefix('/api/graphics/').removesuffix('/preview'),query.get('member',[None])[0]),'text/html'
        else:return False
        raw=page.encode('utf-8');handler.send_response(200);handler.send_header('Content-Type',mime+'; charset=utf-8');handler.send_header('Content-Length',str(len(raw)))
        handler.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self'; frame-ancestors 'self'; object-src 'none'; base-uri 'none'; form-action 'none'")
        handler.end_headers();handler.wfile.write(raw);return True

    def report(self):
        assets=self.assets()
        return dict(schema=1,models=MODEL_NAMES,areas={k:dict(configurations=sum(a['kind']==k for a in assets),models=len({a['model_id'] for a in assets if a['kind']==k})) for k in ('titles','flyers','icons')},
            assets=[dict(id=a['id'],kind=a['kind'],model=a['model_id'],name=a['name'],games=a['games'],members=a['snapshot'].get('symbol_set',{}).get('member_count',0),evidence=a['snapshot']['evidence']) for a in assets],
            coverage=[dict(game=g,assets=[a['id'] for a in assets if g in a['games']]) for g in GAMES],
            rule='Bildmotive, gemeinsame Kompositionen und endliche Symbolsätze. Kein Eintrag pro Spielstand, Inhalt oder Symbolverwendung.',
            exclusions=['Persönliche Geburtstagsfolie bleibt außerhalb des allgemeinen Katalogs.','Unveröffentlichte Schweinchen-Kachel bleibt außerhalb des Bestands aktiver Spiele.','Texttitel bleiben Bestandteil der ursprünglichen Titel-/Fenster-/Flyerkomposition, keine neuen Bitmapkopien.','Kartenbilder, Würfelseiten und dynamische Routen bleiben ihren vorhandenen Kategorien zugeordnet.','Editoroptionen und Spielintegration bleiben offen.'])
