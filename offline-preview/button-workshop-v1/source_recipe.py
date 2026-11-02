"""Appearance-only edits of a registered source button; no executable game data."""
from copy import deepcopy
import json
import re

PROPERTIES = set('width height min-width min-height max-width max-height padding-top padding-right padding-bottom padding-left border-top-left-radius border-top-right-radius border-bottom-right-radius border-bottom-left-radius border-width border-style border-color color background-color background-image opacity font-size font-family font-weight line-height letter-spacing text-align text-transform box-shadow text-shadow transform transition-duration fill stroke stroke-width object-fit'.split())
TARGET = re.compile(r'root(?:\.[0-9]{1,3}){0,12}(?:::(?:before|after))?')
PROPERTIES.add('filter')


def validate_source_recipe(payload, error):
    def require(condition, message):
        if not condition:raise error(message)
    require(payload.get('kind')=='button', 'Ein Originalbutton wird als Buttonentwurf gespeichert.')
    source=payload.get('source_button')
    require(isinstance(source,dict) and set(source)=={'id','name','snapshot'}, 'Der Originalbezug fehlt.')
    require(isinstance(source['id'],str) and re.fullmatch(r'gamebutton-[a-f0-9]{22}',source['id']), 'Ungültiger Originalbezug.')
    require(isinstance(source['name'],str) and 1<=len(source['name'])<=100, 'Ungültiger Originalname.')
    snapshot=source['snapshot']
    require(isinstance(snapshot,dict) and snapshot.get('type')=='game-button', 'Der Quellnachweis fehlt.')
    # The snapshot is evidence only. Rendering uses the registered source, never supplied HTML.
    import hashlib
    digest=hashlib.sha256(json.dumps(snapshot,sort_keys=True).encode()).hexdigest()[:22]
    require(source['id']=='gamebutton-'+digest, 'Der Quellnachweis wurde verändert.')
    changes=payload.get('appearance')
    require(isinstance(changes,dict) and len(changes)<=64, 'Zu viele bearbeitete Buttonteile.')
    for target,part in changes.items():
        require(isinstance(target,str) and TARGET.fullmatch(target), 'Ungültiger Buttonteil.')
        require(isinstance(part,dict) and set(part)<={'style','text'} and 'style' in part, 'Ungültige Gestaltung.')
        require(isinstance(part['style'],dict) and len(part['style'])<=len(PROPERTIES), 'Ungültige Gestaltung.')
        if 'text' in part:
            require('::' not in target and isinstance(part['text'],str) and len(part['text'])<=200, 'Ungültige Beschriftung.')
        for key,value in part['style'].items():
            require(key in PROPERTIES and isinstance(value,str) and 0<len(value)<=1200, 'Unbekannte Gestaltungseinstellung.')
            require(not re.search(r'[;{}<>@\\\x00-\x1f]|url\s*\(|expression\s*\(|var\s*\(',value,re.I), 'Nur feste Gestaltungswerte sind erlaubt.')
            require(bool(re.fullmatch(r'[\w\s#.,%()\-+\'"/]+',value,re.UNICODE)), 'Ungültiger Gestaltungswert.')
    name=payload.get('name');notes=payload.get('notes','');parent=payload.get('parent_id')
    require(isinstance(name,str) and 1<=len(name.strip())<=80, 'Bitte einen Namen mit höchstens 80 Zeichen eingeben.')
    require(isinstance(notes,str) and len(notes)<=1500, 'Die Notiz ist zu lang.')
    require(parent is None or isinstance(parent,str) and re.fullmatch('[a-f0-9]{32}',parent), 'Ungültiger Ausgangsentwurf.')
    return dict(schema_version=3,renderer_version='source-button-v1',kind='button',name=name.strip(),notes=notes,
                parent_id=parent,source_button=deepcopy(source),appearance=deepcopy(changes))
