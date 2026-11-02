"""Independent element libraries and named collections; v1 maps remain readable."""
from copy import deepcopy
import json
import hashlib
from library_store import Library, PRESETS, KINDS, ID, InvalidDesign, text_value, settings
from button_bridge import storage as button_storage
from workshop_catalog import ELEMENT_KINDS, PRESENTATION
from image_store import ImageStore
from source_buttons import SourceButtons
from source_windows import SourceWindows
from source_inputs import SourceInputs
from source_indicators import SourceIndicators
from source_players import SourcePlayers
from source_lobbies import SourceLobbies
from card_library import CardLibrary
from question_bindings import annotate_assets
from dice_library import DiceLibrary
from board_library import BoardLibrary
from piece_library import PieceLibrary, MODELS as PIECE_MODELS
from graphic_library import GraphicLibrary
from media_library import MediaLibrary
from room_library import RoomLibrary
from completion_library import CompletionLibrary
from property_catalog import PropertyCatalog, validate_surfaces
from window_designs import WindowDesigns
from board_designs import BoardDesigns
from piece_designs import PieceDesigns
from card_designs import CardDesigns
from avatar_designs import AvatarDesigns


def presentation(value):
    if not isinstance(value,dict) or set(value)!=set(PRESENTATION):
        raise InvalidDesign('Die Projektentscheidungen sind unvollständig.')
    for key,meta in PRESENTATION.items():
        if not isinstance(value[key],str) or value[key] not in meta['options']:
            raise InvalidDesign('Ungültige Projektentscheidung: '+meta['label'])
    return deepcopy(value)


class ProjectLibrary(Library):
    def __init__(self,directory=None,buttons_directory=None,existing=()):
        super().__init__(directory,buttons_directory)
        self.button_store=button_storage.RecipeStore(self.buttons_directory)
        self.properties=PropertyCatalog(button_storage.CATALOG)
        self.existing=deepcopy(list(existing))
        self.images=ImageStore(self.directory,self.existing)
        self.avatar_designs=AvatarDesigns(self.directory,self.images)
        self.source_buttons=SourceButtons()
        self.source_windows=SourceWindows(self.source_buttons)
        self.window_designs=WindowDesigns(self.directory,self.source_windows)
        self.source_inputs=SourceInputs(self.source_buttons)
        self.source_indicators=SourceIndicators(self.source_buttons)
        self.source_players=SourcePlayers(self.source_buttons)
        self.source_lobbies=SourceLobbies(self.source_buttons)
        self.cards=CardLibrary()
        self.card_designs=CardDesigns(self.directory)
        self.dice=DiceLibrary()
        self.boards=BoardLibrary()
        self.board_designs=BoardDesigns(self.directory,self.images)
        self.pieces=PieceLibrary()
        self.piece_designs=PieceDesigns(self.directory)
        self.graphics=GraphicLibrary(self.source_buttons)
        self.media=MediaLibrary()
        self.rooms=RoomLibrary(self.source_buttons)
        self.completion=CompletionLibrary(self.source_buttons)

    def assets(self):
        assets=[*deepcopy(self.existing),*self.images.assets(),*self.source_buttons.assets(),*self.source_windows.assets(),*self.source_inputs.assets(),*self.source_indicators.assets(),*self.source_players.assets(),*self.source_lobbies.assets(),*self.cards.assets(),*self.dice.assets(),*self.boards.assets(),*self.pieces.assets(),*self.graphics.assets(),*self.media.assets(),*self.rooms.assets(),*self.completion.assets()]
        assets.extend(self.window_designs.assets())
        assets.extend(self.board_designs.assets())
        assets.extend(self.piece_designs.assets())
        assets.extend(self.card_designs.assets())
        assets.extend(self.avatar_designs.assets())
        for asset in assets:
            if asset['kind']=='background' and asset.get('source')=='existing':
                asset.update(model_id='background-image-v1',model_name='Bildhintergründe',family='image',family_name='Vorhandene Bildmotive')
        recipes,_=self.button_store.list()
        for recipe in recipes:
            # Keep the exact original file in a project, including old renderer metadata.
            try:raw=json.loads((self.buttons_directory/(recipe['id']+'.json')).read_text(encoding='utf-8'))
            except (ValueError,OSError):continue
            assets.append(dict(kind='buttons',id=recipe['id'],name=recipe['name'],representation='2d',source='saved',
                               model_id=self.button_model(recipe),
                               variant=recipe['kind'],created=recipe['created_at'],snapshot=raw))
        for record in [*self.list('elements')[0],*PRESETS]:
            kind=record['kind']
            if kind in ('dice','board','pieces') and record.get('builtin'):continue
            if kind not in ELEMENT_KINDS or kind in ('background','avatars','buttons'):continue
            asset=dict(kind=kind,id=record['id'],name=record['name'],representation=record.get('representation','3d' if kind!='lobby' else '2d'),
                       source='preset' if record.get('builtin') else 'saved',created=record.get('created'),snapshot=deepcopy(record))
            if kind=='board':
                asset.update(model_id='board-'+asset['representation']+'-v1',model_name='Brett · '+asset['representation'].upper())
            if kind=='pieces':
                model=record['settings']['set']
                asset.update(model_id='pieces-'+model+'-v1',model_name=PIECE_MODELS[model])
            assets.append(asset)
        for asset in assets:
            if asset['kind']!='buttons':asset['editable']=False
        return annotate_assets(assets)

    def button_model(self,recipe):
        if recipe['schema_version']==4:
            identifier=recipe['source_button']['id'];record=self.source_buttons.records.get(identifier)
            base=self.source_buttons.model_id(record) if record else 'original-'+identifier
            if record:
                original=self.source_buttons.recipe(identifier,button_storage.CATALOG)
                # A browser capture can originate from a markup-only source
                # without a prebuilt measurement profile or editor settings.
                if 'settings' in original:
                    left={k:v for k,v in recipe['settings'].items() if k!='label'}
                    right={k:v for k,v in original['settings'].items() if k!='label'}
                    if left==right and recipe['contour']==original['contour']:return base
            styling=dict(settings={k:v for k,v in recipe['settings'].items() if k!='label'},contour=recipe['contour'])
            return base+'-'+hashlib.sha256(json.dumps(styling,sort_keys=True).encode()).hexdigest()
        if recipe['schema_version']==3:
            identifier=recipe['source_button']['id'];record=self.source_buttons.records.get(identifier)
            base=self.source_buttons.model_id(record) if record else 'original-'+identifier
            styles={key:part['style'] for key,part in recipe['appearance'].items() if part['style']}
            return base if not styles else base+'-'+hashlib.sha256(json.dumps(styles,sort_keys=True).encode()).hexdigest()
        settings=dict(recipe['settings']);settings.pop('label',None)
        value=dict(settings=settings,contour=recipe['contour'])
        return 'recipe-'+hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()

    def save_element(self,value):
        if not isinstance(value,dict) or set(value) not in ({'kind','name','settings'},{'kind','name','settings','representation'}):
            raise InvalidDesign('Kein vollständiger Baustein.')
        if value['kind'] not in ('board','pieces','lobby','dice','cards'):
            raise InvalidDesign('Für diese Elementart ist hier kein Generator eingerichtet.')
        representation=value.get('representation','2d' if value['kind']=='lobby' else '3d')
        if representation not in ('2d','3d'):raise InvalidDesign('Ungültige Ausführung.')
        return self.write('elements',dict(schema=1,name=text_value(value['name'],100,'Name',True),kind=value['kind'],
                                          settings=settings(value['kind'],value['settings']),representation=representation))

    def validate_saved_project(self,value):
        text_value(value.get('name'),100,'Projektname',True)
        text_value(value.get('notes'),10000,'Projektwünsche')
        key=value.get('project_key')
        if not isinstance(key,str) or not ID.fullmatch(key) or not key.startswith('project-'):
            raise InvalidDesign('Ungültige Projektkennung.')
        presentation(value.get('presentation'))
        if 'surfaces' in value:validate_surfaces(value['surfaces'])
        items=value.get('items')
        if not isinstance(items,list) or len(items)>200:raise InvalidDesign('Ungültige Elementsammlung.')
        seen=set()
        for item in items:
            if not isinstance(item,dict) or not isinstance(item.get('kind'),str) or item['kind'] not in ELEMENT_KINDS:
                raise InvalidDesign('Unbekannte Elementart in der Mappe.')
            text_value(item.get('id'),160,'Elementkennung',True)
            text_value(item.get('name'),100,'Elementname',True)
            if not isinstance(item.get('snapshot'),dict) or item.get('representation') not in ('2d','3d'):
                raise InvalidDesign('Die gespeicherte Elementvariante ist unvollständig.')
            ref=(item['kind'],item['id'])
            if ref in seen:raise InvalidDesign('Ein Element ist doppelt in der Mappe.')
            seen.add(ref)
        return value

    def project_view(self,record):
        if record['schema']==2:return deepcopy(record)
        items=[]
        for kind in ELEMENT_KINDS:
            if kind in ('buttons','avatars') or not record['included'].get(kind):continue
            snap=dict(kind=kind,name=KINDS[kind]['title'],settings=deepcopy(record['elements'][kind]))
            items.append(dict(kind=kind,id=record['sources'].get(kind) or f'legacy-{record["id"]}-{kind}',name=snap['name'],
                              representation='3d' if kind in ('board','pieces','dice','cards') else '2d',source='legacy',snapshot=snap))
        for raw in record.get('button_snapshots',[]):
            items.append(dict(kind='buttons',id=raw['id'],name=raw['name'],representation='2d',source='saved',snapshot=deepcopy(raw)))
        p={k:'undecided' for k in PRESENTATION}
        if record['included'].get('camera'):p['mode']={'2d':'flat','2.5d':'depth','3d':'spatial'}[record['elements']['camera']['mode']]
        if record['included'].get('room'):
            room=record['elements']['room'];p.update(shadows='yes' if room['shadows'] else 'no',pieces='no' if room['pieces']=='off' else 'yes',
                                                   dice='yes' if room['dice'] else 'no',cards='no' if room['cards']=='off' else 'yes')
        return dict(schema=2,id=record['id'],created=record['created'],project_key=record['id'],name=record['name'],notes=record['notes'],
                    items=items,presentation=p,legacy_source=deepcopy(record))

    def project_groups(self):
        groups={}
        for record in self.list('projects')[0]:
            view=self.project_view(record);key=view['project_key']
            if key not in groups:groups[key]=dict(project=view,versions=[])
            groups[key]['versions'].append(dict(id=record['id'],created=record['created']))
        return list(groups.values())

    def save_project(self,value):
        if isinstance(value,dict) and value.get('schema')==1:return super().save_project(value)
        expected={'schema','project_key','name','notes','items','presentation'}
        if not isinstance(value,dict) or set(value) not in (expected,expected|{'surfaces'}) or type(value.get('schema')) is not int or value['schema']!=2:
            raise InvalidDesign('Keine vollständige Projektmappe.')
        name=text_value(value['name'],100,'Projektname',True).strip()
        notes=text_value(value['notes'],10000,'Projektwünsche')
        p=presentation(value['presentation']);key=value['project_key']
        groups=self.project_groups();known={g['project']['project_key']:g['project'] for g in groups}
        if key is not None and (not isinstance(key,str) or key not in known):raise InvalidDesign('Diese Projektmappe wurde nicht gefunden.')
        previous=known.get(key,{})
        choices={(v['kind'],v['id']):v for v in self.assets()}
        if key is not None:
            for record in reversed(self.list('projects')[0]):
                old=self.project_view(record)
                if old['project_key']==key:
                    choices.update({(v['kind'],v['id']):v for v in old['items']})
        # Existing snapshots win over later changes in the library.
        choices.update({(v['kind'],v['id']):v for v in previous.get('items',[])})
        refs=value['items']
        if not isinstance(refs,list) or len(refs)>200:raise InvalidDesign('Eine Mappe kann höchstens 200 Elemente enthalten.')
        items=[];seen=set()
        for ref in refs:
            if not isinstance(ref,dict) or set(ref)!={'kind','id'} or not isinstance(ref['kind'],str) or not isinstance(ref['id'],str):
                raise InvalidDesign('Ungültige Elementauswahl.')
            pair=(ref['kind'],ref['id'])
            if pair not in choices:raise InvalidDesign('Ein gewähltes Element wurde in der Bibliothek nicht gefunden.')
            if pair in seen:raise InvalidDesign('Ein Element ist doppelt ausgewählt.')
            seen.add(pair);items.append(deepcopy(choices[pair]))
        payload=dict(schema=2,project_key=key,name=name,notes=notes,items=items,presentation=p)
        if 'surfaces' in value:
            payload['surfaces']=self.properties.select(value['surfaces'],previous.get('surfaces',[]))
        elif 'surfaces' in previous:
            payload['surfaces']=deepcopy(previous['surfaces'])
        if previous.get('legacy_source'):payload['legacy_source']=deepcopy(previous['legacy_source'])
        return self.write('projects',payload)

    def handoff(self,project_id):
        records=self.list('projects')[0]
        record=next((p for p in records if p['id']==project_id),None)
        if record is None:raise InvalidDesign('Diese gespeicherte Projektmappe wurde nicht gefunden.')
        if record['schema']==1:return super().handoff(project_id)
        self.validate_saved_project(record)
        lines=[f'# Projektübergabe: {record["name"]}','','Gespeicherter Stand: '+project_id,'',
               'Bitte entwickle das Spiel aus diesen gesammelten Elementen und führe dazu ein Interview mit mir.',
               'Die Auswahl ist eine Grundlage; die vollständigen Regeln und Abläufe entstehen im Gespräch.','','## Gesammelte Elemente']
        for item in record['items']:
            lines.append(f'- {ELEMENT_KINDS[item["kind"]]["title"]}: {item["name"]} · {item["id"]} · {item["representation"].upper()}')
        if not record['items']:lines.append('Noch keine Elemente ausgewählt.')
        lines+=['','## Darstellung und Verhalten']
        for key,meta in PRESENTATION.items():lines.append(f'- {meta["label"]}: {meta["options"][record["presentation"][key]]}')
        if 'surfaces' in record:
            lines+=['','## Materialwünsche für das Projekt','Wünsche für die spätere Gestaltung; die Originalelemente sind unverändert.']
            lines.extend('- '+entry['name']+': '+entry.get('description','')+' '+entry.get('note','') for entry in record['surfaces'])
            if not record['surfaces']:lines.append('Keine Materialwünsche festgelegt.')
        lines+=['','## Meine Idee und Wünsche',record['notes'] or 'Im Interview ergänzen.','','## Im Interview klären',
                '- Für wen ist das Spiel und was ist sein Ziel?',
                '- Welche Regeln, Spielzüge und Abläufe sind gewünscht?',
                '- Welche Elemente fehlen noch und welche Varianten gefallen?',
                '- Welche Darstellung, Kamera, Bewegung und Klänge passen dazu?',
                '- Wie sollen Lobby, Spielerzahl, Speichern und gemeinsames Spielen funktionieren?',
                '','Die vollständigen Elementvarianten stehen in der zugehörigen JSON-Übergabe.']
        handoff=self.write('handoffs',dict(schema=1,name=record['name'],project_id=project_id,project=deepcopy(record),brief='\n'.join(lines)))
        with (self.directory/'handoffs'/(handoff['id']+'.md')).open('x',encoding='utf-8') as out:out.write(handoff['brief'])
        return handoff
