"""Register existing game buttons from their actual templates and styles.

The preview reads the canonical markup and CSS. It never imports the app,
opens a game database, or installs game handlers in the preview.
"""
from __future__ import annotations

import ast
from copy import deepcopy
import hashlib
from html import escape, unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from jinja2 import ChainableUndefined, Environment, FileSystemLoader, meta, select_autoescape
from library_store import ROOT, InvalidDesign

VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
BUTTON_LINK = re.compile(r'button|btn|buzzer|(?:^|\s)(?:perfect-home-link|back-link|table-back|variant-a-edit)(?:\s|$)')
LOCATIONS = {
    'home.html': ('Guesstimate', 'Startseite'), 'question.html': ('Guesstimate', 'Frage und Auflösung'),
    'result.html': ('Guesstimate', 'Ergebnis'), 'base.html': ('Gemeinsam', 'Navigation und Regeln'),
    '_leaderboard.html': ('Gemeinsam', 'Rangliste'), '_lobby_room.html': ('Gemeinsam', 'Lobby'),
    '_lobby_overview.html': ('Gemeinsam', 'Lobbyübersicht'),
    '_profile_window.html': ('Gemeinsam', 'Profilfenster'),
    'profile.html': ('Profil', 'Inventar'), 'shop.html': ('Profil', 'Shop'),
    'login.html': ('Zugang', 'Anmeldung'), 'register.html': ('Zugang', 'Registrierung'),
}


class SampleUndefined(ChainableUndefined):
    """Neutral example values for template branches, never real player data."""
    def __call__(self, *args, **kwargs): return ''
    def __int__(self): return 0
    def __float__(self): return 0.0
    def __index__(self): return 0
    def __add__(self, other): return other
    def __radd__(self, other): return other
    def __sub__(self, other): return 0
    def __mul__(self, other): return 0
    def __lt__(self, other): return False
    def __le__(self, other): return False
    def __gt__(self, other): return False
    def __ge__(self, other): return False


class ButtonParser(HTMLParser):
    def __init__(self, text, extended_links=True):
        super().__init__(convert_charrefs=False)
        self.text=text;self.stack=[];self.buttons=[];self.current=None;self.extended_links=extended_links
        self.starts=[0]+[m.end() for m in re.finditer('\n',text)]
        self.feed(text)

    def absolute_offset(self):
        line,column=self.getpos();return self.starts[line-1]+column

    def handle_starttag(self,tag,attrs):
        attributes=dict(attrs)
        if tag in ('button','a','input') and self.current is None:
            link_pattern=BUTTON_LINK if self.extended_links else re.compile(r'button|btn|buzzer')
            nav_tab=self.extended_links and any('arena-main-nav' in classes for _,classes,_ in self.stack) and 'arena-nav-brand' not in (attributes.get('class') or '')
            is_button = tag=='button' or (tag=='a' and (link_pattern.search(attributes.get('class') or '') or self.extended_links and attributes.get('role')=='button' or nav_tab)) or (tag=='input' and attributes.get('type') in ('submit','button','reset'))
            if is_button:
                self.current={'tag':tag,'start':self.absolute_offset(),'line':self.getpos()[0],
                              'ancestors':deepcopy(self.stack),'attrs':attributes}
                if tag=='input':self.finish(self.absolute_offset()+len(self.get_starttag_text()))
        if tag not in VOID:
            self.stack.append((tag,attributes.get('class') or '',attributes.get('id') or ''))

    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag not in VOID:self.handle_endtag(tag)

    def handle_endtag(self,tag):
        if self.current is not None and self.current['tag']==tag:
            end=self.text.find('>',self.absolute_offset())
            self.finish(end+1)
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0]==tag:
                self.stack=self.stack[:i];break

    def finish(self,end):
        self.current['markup']=self.text[self.current['start']:end]
        self.buttons.append(self.current);self.current=None


class ContextParser(HTMLParser):
    """Read the original ancestry of a dynamic factory's mount point."""
    def __init__(self,text,token):
        super().__init__();self.stack=[];self.found=None;self.token=token;self.feed(text)
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag not in VOID:self.stack.append((tag,attrs.get('class',''),attrs.get('id','')))
        if self.token in attrs:self.found=deepcopy(self.stack)
    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0]==tag:self.stack=self.stack[:i];break


def location(name):
    if name in LOCATIONS:return LOCATIONS[name]
    if name.startswith('party_'):return 'Guesstimate Party',name.removesuffix('.html').removeprefix('party_').replace('_',' ')
    if name.startswith('nerd_'):return 'Perfect','Spielraum' if name=='nerd_mode.html' else 'Übersicht'
    if name.startswith('card_table_'):return 'Playtable',name.removesuffix('.html').removeprefix('card_table_').replace('game','Spieltisch').replace('lobby','Lobby').replace('index','Übersicht')
    if name.startswith('dice_table_'):return 'Würfelspiele',name.removesuffix('.html').removeprefix('dice_table_').replace('game','Spieltisch').replace('lobby','Lobby').replace('index','Übersicht')
    if name.startswith('conquest_'):return 'Conquest',name.removesuffix('.html').removeprefix('conquest_').replace('_',' ')
    return 'Gemeinsam',name.removesuffix('.html').replace('_',' ').strip()


def maexchen_branch(text,offset):
    scopes=[]
    for match in re.finditer(r'{%\s*(if|elif|else|endif)\b(.*?)%}',text[:offset],re.S):
        kind,expression=match[1],match[2].strip()
        if kind=='if':scopes.append(True if expression=='is_maexchen' else None)
        elif kind=='endif' and scopes:scopes.pop()
        elif kind=='else' and scopes and scopes[-1] is not None:scopes[-1]=not scopes[-1]
        elif kind=='elif' and scopes:scopes[-1]=None
    return next((value for value in reversed(scopes) if value is not None),None)


class SourceButtons:
    def public_file(self,path):
        path=unquote(urlsplit(path).path)
        if path.startswith(('/shared/','/static/')):base=self.root/'static';relative=path.split('/',2)[2]
        elif path.startswith('/conquest-source/'):base=self.root/'offline-preview/conquest-2-5d-v1';relative=path.removeprefix('/conquest-source/')
        elif path=='/button-editor/materials.css':return self.root/'offline-preview/button-workshop-v1/materials.css'
        else:return None
        candidate=(base/relative).resolve()
        return candidate if candidate.is_relative_to(base) and candidate.suffix in ('.css','.png','.webp','.svg','.jpg','.ttf') and candidate.is_file() else None

    def http_get(self,handler,catalog,path):
        if not path.startswith('/api/game-buttons/'):return False
        try:
            if handler.headers.get('Host') not in (f'127.0.0.1:{handler.server.server_port}',f'localhost:{handler.server.server_port}'):
                handler.json_response({'error':'Nur lokal erreichbar.'},403);return True
            if path.endswith('/recipe'):
                handler.json_response({'recipe':self.recipe(path.removeprefix('/api/game-buttons/').removesuffix('/recipe'),catalog)})
            elif path.endswith('/preview'):
                raw=self.preview(path.removeprefix('/api/game-buttons/').removesuffix('/preview')).encode('utf-8')
                handler.send_response(200);handler.send_header('Content-Type','text/html; charset=utf-8');handler.send_header('Content-Length',str(len(raw)))
                handler.send_header('Content-Security-Policy',"default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; script-src 'none'; form-action 'none'; frame-ancestors 'self'")
                handler.end_headers();handler.wfile.write(raw)
            else:handler.json_response({'error':'Unbekannte Originalansicht.'},404)
        except (ValueError,OSError) as error:handler.json_response({'error':str(error)},400)
        return True

    def __init__(self, root=ROOT):
        self.root=Path(root)
        self.env=Environment(loader=FileSystemLoader(self.root/'templates'),undefined=SampleUndefined,
                             autoescape=select_autoescape(['html'],default_for_string=True))
        self.env.filters['points']=lambda value:str(value)
        self.env.globals.update(url_for=lambda endpoint,**args:'/shared/'+str(args['filename']) if endpoint=='static' and 'filename' in args else '#',
                                csrf_token=lambda:'preview-no-action')
        self.env.globals['category_icon']=self.env.get_template('_icons.html').module.category_icon
        self.records={};self.generated_errors=[]
        try:
            model_data=json.loads(Path(__file__).with_name('button-models.json').read_text(encoding='utf-8'))
            self.models=model_data['models'];self.approved_models=model_data.get('approved_groups',{})
        except (OSError,ValueError,KeyError):self.models={};self.approved_models={}
        try:self.profiles=json.loads(Path(__file__).with_name('button-profiles.json').read_text(encoding='utf-8'))['profiles']
        except (OSError,ValueError,KeyError):self.profiles={}
        self.discover()

    def read(self,path):return (self.root/path).read_text(encoding='utf-8-sig')

    def styles(self,name):
        text=self.read('templates/'+name)
        parent=re.search(r'{%\s*extends\s+["\x27]([^"\x27]+)',text)
        tokens=re.findall(r'url_for\(\s*["\x27](static|conquest_table_asset)["\x27]\s*,\s*filename\s*=\s*["\x27]([^"\x27]+\.css)["\x27]',text)
        own=[]
        for endpoint,filename in tokens:
            path=('static/'+filename if endpoint=='static' else
                  'offline-preview/button-workshop-v1/materials.css' if filename=='button-materials.css' else
                  'offline-preview/conquest-2-5d-v1/'+filename)
            if (self.root/path).is_file() and path not in own:own.append(path)
        result=self.styles(parent[1]) if parent else []
        insertion=len(result)
        if parent:
            prefix=self.read('templates/'+parent[1]).split('{% block extra_head',1)[0]
            insertion=len(re.findall(r'filename\s*=\s*["\x27][^"\x27]+\.css["\x27]',prefix))
        result[insertion:insertion]=[p for p in own if p not in result]
        if name.startswith('_') and not result:result=self.styles('base.html')
        return result

    def sample(self,name):
        return dict(attempt=None,round_available=True,missed_week_days=[1,2,3],index=0,total=5,
                    feedback_remaining_ms=0,can_start=True,is_host=True,is_maexchen=False,
                    g={'user':{'id':1}},lobby={'id':1,'name':'Beispielrunde','dice_count':5,'host_user_id':1},
                    member={'id':1,'ready':False},guests=[{'id':2}],ready_guests=[{'id':2}],
                    choice='Beispielantwort',right='Beispielantwort',option={'key':'example','label':'Beispielantwort'},
                    request={'endpoint':'home'},config={'PERFECT_MAX_PLAYERS':7},capacity=7,back_label='Zurück zur Übersicht',leave_label='lobby verlassen')

    def rendered(self,record):
        values={**self.sample(record['template']),**record.get('sample_values',{})}
        return record.get('rendered_markup') or self.env.from_string(record['markup']).render(**values)

    def discover(self):
        entries=set()
        for file in self.root.glob('*.py'):
            tree=ast.parse(file.read_text(encoding='utf-8-sig'))
            for node in ast.walk(tree):
                if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in ('render_template','render_overview') and node.args:
                    for value in ast.walk(node.args[0]):
                        if isinstance(value,ast.Constant) and isinstance(value.value,str) and value.value.endswith('.html'):
                            entries.add(value.value)
        self.entry_templates=entries.copy()
        pending=list(entries);active=set();self.template_dependencies={}
        while pending:
            name=pending.pop()
            if name in active or not (self.root/'templates'/name).is_file():continue
            active.add(name)
            refs={v for v in meta.find_referenced_templates(self.env.parse(self.read('templates/'+name))) if v}
            self.template_dependencies[name]=refs;pending.extend(refs)
        self.active_templates=active
        self.template_games={name:set() for name in active}
        for entry in entries:
            game,_=location(entry);todo=[entry];seen=set()
            while todo:
                name=todo.pop()
                if name in seen or name not in active:continue
                seen.add(name);self.template_games[name].add(game);todo.extend(self.template_dependencies.get(name,()))
        for games in self.template_games.values():
            if 'Würfelspiele' in games:games.update(('Würfeltisch','Kniffel','Mäxchen'))
            # Login/registration use the logged-out shell; the authenticated
            # navigation/dialog controls are not their game uses.
            games.discard('Zugang')
        for name in sorted(active):
            text=self.read('templates/'+name);game,place=location(name)
            styles=[{'path':p,'sha256':hashlib.sha256((self.root/p).read_bytes()).hexdigest()} for p in self.styles(name)]
            shell=re.search(r'{%\s*block\s+shell_class\s*%}(.*?){%\s*endblock',text,re.S)
            legacy={b['start']:i for i,b in enumerate(ButtonParser(text,False).buttons)}
            for ordinal,button in enumerate(ButtonParser(text).buttons):
                record={**button,'template':name,'styles':styles,'shell':shell[1].strip() if shell else ''}
                body=re.search(r'<body\b[^>]*class="([^"]*)"',text)
                if body and not record['shell']:record['shell']=body[1]
                if name=='dice_table_game.html':
                    is_maexchen=maexchen_branch(text,button['start']) is True
                    record['sample_values']={'is_maexchen':is_maexchen,'is_kniffel':False}
                    record['games']=['Mäxchen'] if is_maexchen else ['Würfeltisch'] if maexchen_branch(text,button['start']) is False else ['Würfeltisch','Kniffel','Mäxchen']
                if name=='_profile_window.html' and 'variant-a-edit' in (button['attrs'].get('class') or ''):
                    record['games']=['Guesstimate']
                source=dict(path='templates/'+name,line=button['line'],ordinal=legacy.get(button['start'],'link-'+str(button['line'])))
                self.register(record,source,game,place,text)
                if name=='dice_table_game.html' and maexchen_branch(text,button['start']) is False:
                    variant=deepcopy(record);variant['sample_values']={'is_maexchen':False,'is_kniffel':True};variant['games']=['Kniffel']
                    self.register(variant,{**source,'context':'kniffel'},'Kniffel',place,text)
        # This module is the mounted surface of the current saved Conquest table.
        surface='offline-preview/conquest-2-5d-v1/table-surface.js'
        text=self.read(surface)
        mount=self.read('offline-preview/conquest-2-5d-v1/game-buttons.js')
        choices=re.search(r"for\(const id of (\[[^\]]+\])",mount)
        canonical=set(ast.literal_eval(choices[1])) if choices else set()
        profile=json.loads(self.read('offline-preview/conquest-2-5d-v1/button-profile.json'))
        styles=[{'path':p,'sha256':hashlib.sha256((self.root/p).read_bytes()).hexdigest()} for p in self.styles('conquest_table.html')]
        legacy={b['start']:i for i,b in enumerate(ButtonParser(text,False).buttons)}
        for ordinal,button in enumerate(ButtonParser(text).buttons):
            # A received card is a card component; reset-turn is deliberately hidden
            # by the saved-game scene. Neither is a reusable UI-button design.
            if button['attrs'].get('id') in ('awarded-card','reset-turn'):continue
            record={**button,'template':'table-surface.js','styles':styles,'shell':''}
            if button['attrs'].get('id') in canonical:record['recipe']=deepcopy(profile)
            if button['attrs'].get('class')=='dice-choice':
                icons=json.loads(Path(__file__).with_name('generated-buttons.json').read_text(encoding='utf-8'))['icons']
                if any(hashlib.sha256((self.root/p['path']).read_bytes()).hexdigest()!=p['sha256'] for p in icons['evidence']):
                    if 'conquest-dice-icon' not in self.generated_errors:self.generated_errors.append('conquest-dice-icon')
                    continue
                record['rendered_markup']=button['markup'].replace('</button>',icons['dice']+'</button>')
                record['evidence']=icons['evidence']
            self.register(record,dict(path=surface,line=button['line'],ordinal=legacy.get(button['start'],'link-'+str(button['line']))),'Conquest','Spieltisch',text)
        self.discover_generated()

    def discover_generated(self):
        manifest=Path(__file__).with_name('generated-buttons.json')
        if not manifest.is_file():return
        for item in json.loads(manifest.read_text(encoding='utf-8'))['buttons']:
            if any(hashlib.sha256((self.root/p['path']).read_bytes()).hexdigest()!=p['sha256'] for p in item['evidence']):
                self.generated_errors.append(item['key']);continue
            button=ButtonParser(item['markup']).buttons[0]
            ancestors=item['ancestors']
            if item.get('context_token'):
                context=ContextParser(self.read('templates/'+item['template']),item['context_token']).found
                if context is None:raise InvalidDesign('Der Einsatzort eines erzeugten Buttons fehlt: '+item['key'])
                ancestors=context+ancestors
            record={**button,'template':item['template'],'styles':[dict(path=p,sha256=hashlib.sha256((self.root/p).read_bytes()).hexdigest()) for p in self.styles(item['template'])],
                    'shell':item.get('shell',''),'evidence':item['evidence'],'rendered_markup':item['markup'],
                    'ancestors':ancestors,'context_state':item.get('context_state'),'games':item['games'],'cell_width':item.get('cell_width'),
                    'capture_key':item['key']}
            self.register(record,dict(path=item['path'],line=item['line'],ordinal=item['key']),item['game'],item['usage'],self.read(item['path']))

    def register(self,record,source,game,place,text):
        markup=self.rendered(record)
        aria=record['attrs'].get('aria-label')
        label=self.env.from_string(aria).render(**self.sample(record['template'])) if aria else re.sub('<[^>]+>',' ',markup)
        label=unescape(re.sub(r'\s+',' ',label)).strip()
        label=label or record['attrs'].get('title') or record['attrs'].get('id') or 'Auswahl'
        snapshot=dict(type='game-button',source=source,markup=record['markup'],styles=record['styles'],
                      source_sha256=hashlib.sha256((self.root/source['path']).read_bytes()).hexdigest(),example_values=True)
        if 'recipe' in record:snapshot['recipe']=deepcopy(record['recipe'])
        if record.get('evidence'):snapshot['evidence']=deepcopy(record['evidence'])
        if record.get('rendered_markup'):snapshot['rendered_markup']=record['rendered_markup']
        if record.get('cell_width'):snapshot['cell_width']=record['cell_width']
        stamp=hashlib.sha256(json.dumps(snapshot,sort_keys=True).encode()).hexdigest()[:22]
        identifier='gamebutton-'+stamp
        record.update(id=identifier,label=label,name=(game+' · '+place+' · '+label)[:100],game=game,place=place,snapshot=snapshot)
        self.records[identifier]=record

    def assets(self):
        return [dict(kind='buttons',id=r['id'],name=r['name'],representation='2d',source='game',variant='source',
                     model_id=self.model_id(r),
                     model_name=self.approved_model(r)[1],context_state=self.context_state(r),
                     game=r['game'],games=r.get('games') or sorted(self.template_games.get(r['template'],{r['game']})),usage=r['place'],preview='/api/game-buttons/'+r['id']+'/preview',editable=True,
                     label=r['label'],canonical='recipe' in r,disabled='disabled' in r['attrs'],
                     snapshot=deepcopy(r['snapshot'])) for r in self.records.values()]

    def model_id(self,record):
        approved,_=self.approved_model(record)
        if approved:return 'approved-'+approved
        if 'recipe' in record:
            defaults=json.loads(self.read('offline-preview/button-workshop-v1/catalog.json'))['defaults']
            settings={**defaults,**record['recipe']['settings']};settings.pop('label',None)
            value=dict(settings=settings,contour=record['recipe']['contour'])
            return 'recipe-'+hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()
        # Each source ID fingerprints all markup/CSS evidence. Changed sources cannot inherit old grouping.
        return 'original-'+self.models.get(record['id'],record['id'])

    def approved_model(self,record):
        for key,group in self.approved_models.items():
            if any(member['path']==record['snapshot']['source']['path'] and member['label']==record['label'] for member in group['members']):
                return key,group['name']
        return None,None

    def context_state(self,record):
        if self.approved_model(record)[0]=='guesstimate-start-action':
            return 'Runde abgeschlossen: Ergebnis öffnen' if record['label'].startswith('heutiges') else 'Runde offen: spielen oder fortsetzen'
        return record.get('context_state')

    def recipe(self,identifier,catalog):
        r=self.records.get(identifier)
        if r is None:raise InvalidDesign('Dieser Originalbutton ist nicht registriert.')
        if 'recipe' not in r:
            if identifier in self.profiles:
                from profile_recipe import from_profile
                return from_profile(self.profiles[identifier],dict(id=r['id'],name=r['name'],snapshot=deepcopy(r['snapshot'])),catalog)
            return dict(schema_version=3,kind='button',name=r['name'][:80],notes='Eigener Entwurf aus '+r['name'],parent_id=None,
                        source_button=dict(id=r['id'],name=r['name'],snapshot=deepcopy(r['snapshot'])),appearance={})
        value=deepcopy(r['recipe'])
        return dict(schema_version=2,kind='button',name=r['name'][:80],notes='Übernommen aus '+r['name'],parent_id=None,
                    settings={**catalog['defaults'],**value['settings'],'label':r['label']},contour=value['contour'],
                    review={key:'open' for key,_ in catalog['review_dimensions']})

    def preview(self,identifier):
        record=self.records.get(identifier)
        if record is None:raise InvalidDesign('Dieser Spielbutton ist nicht registriert.')
        snapshot=record['snapshot']
        if hashlib.sha256((self.root/snapshot['source']['path']).read_bytes()).hexdigest()!=snapshot['source_sha256']:
            raise InvalidDesign('Die Spielquelle wurde geändert. Bitte die Werkstatt neu laden.')
        for source in record['styles']:
            if hashlib.sha256((self.root/source['path']).read_bytes()).hexdigest()!=source['sha256']:
                raise InvalidDesign('Die Spielgestaltung wurde geändert. Bitte die Werkstatt neu laden.')
        for source in record.get('evidence',[]):
            if hashlib.sha256((self.root/source['path']).read_bytes()).hexdigest()!=source['sha256']:
                raise InvalidDesign('Die Buttonquelle wurde geändert. Bitte den Bestand erneut aufnehmen.')
        def url(path):
            if path.startswith('static/'):return '/shared/'+path.removeprefix('static/')
            if path=='offline-preview/button-workshop-v1/materials.css':return '/button-editor/materials.css'
            return '/conquest-source/'+path.removeprefix('offline-preview/conquest-2-5d-v1/')
        links=''.join('<link rel="stylesheet" href="'+escape(url(s['path']),quote=True)+'?source_sha='+s['sha256']+'">' for s in record['styles'])
        wrappers=[]
        for tag,classes,ancestor_id in record['ancestors']:
            if tag in ('html','body','head','script','style'):continue
            values={**self.sample(record['template']),**record.get('sample_values',{})}
            classes=self.env.from_string(classes).render(**values)
            wrappers.append('<'+tag+' class="source-ancestor '+escape(classes,quote=True)+'"'+(' id="'+escape(ancestor_id,quote=True)+'"' if ancestor_id else '')+'>')
        ends=''.join('</'+tag+'>' for tag,_,_ in reversed(record['ancestors']) if tag not in ('html','body','head','script','style'))
        shell=self.env.from_string(record['shell']).render(**self.sample(record['template']))
        context_style=''
        if record.get('cell_width'):
            context_style='#source-context table.source-ancestor{display:table!important;width:'+str(record['cell_width'])+'px!important}#source-context tbody.source-ancestor{display:table-row-group!important}#source-context tr.source-ancestor{display:table-row!important}#source-context td.source-ancestor{display:table-cell!important}'
        visible_markup=self.rendered(record)
        # Hidden controls are shown in their visible example state in this inert
        # preview only. The original markup and game visibility rules stay intact.
        end=visible_markup.find('>')
        visible_markup=re.sub(r'\s+hidden(?:\s*=\s*(?:"[^"]*"|\x27[^\x27]*\x27))?(?=[\s>])','',visible_markup[:end+1])+visible_markup[end+1:]
        return '<!doctype html><html lang="de"><meta charset="utf-8"><meta name="viewport" content="width=1000"><title>'+escape(record['name'])+'</title>'+links+'''<style>
html,body{margin:0!important;width:520px!important;height:180px!important;min-height:0!important;overflow:hidden!important;background:#142439!important}body{display:grid!important;place-items:center!important;padding:18px!important;box-sizing:border-box!important}#source-stage{width:430px;height:144px;display:grid;place-items:center}#source-context{width:100%;max-width:none!important;min-height:0!important;margin:0!important;padding:0!important;text-align:center;background:none!important;box-shadow:none!important;border:0!important}html::before,html::after,body::before,body::after,#source-context::before,#source-context::after{display:none!important}#source-context .source-ancestor{display:contents!important}#source-context .source-ancestor::before,#source-context .source-ancestor::after{display:none!important}#source-context :is(button,a,input[type=submit]){position:relative!important;inset:auto!important;margin:0!important}#source-context .perfect-buzzer{width:260px!important;height:140px!important}
</style><style>'''+context_style+'</style><body inert><div id="source-stage"><div id="source-context" class="app-shell '+escape(shell,quote=True)+'">'+''.join(wrappers)+visible_markup+ends+'</div></div></body></html>'
