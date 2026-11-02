"""Local button-model assignments. Originals and saved recipes are never rewritten."""
from copy import deepcopy
from pathlib import Path
import json
import hashlib
import os
import re
import threading
import time
from uuid import uuid4


class UsageConflict(ValueError):
    pass


class ButtonUsage:
    def __init__(self, directory, recipes, sources):
        self.directory = Path(directory) / 'button-usage'
        self.recipes = recipes
        self.sources = sources
        self.lock = threading.Lock()
        self.models = {}
        self.snippets = {}
        for asset in sources.assets():
            source = asset['snapshot']['source']
            path = source['path']
            markup = asset['snapshot'].get('markup', '')
            supported = path.startswith('templates/') and bool(re.match(r'<(?:button|a)\b', markup))
            position = None
            if supported:
                text = (sources.root/path).read_text(encoding='utf-8-sig')
                positions = [match.start() for match in re.finditer(re.escape(markup),text)]
                exact = [index for index in positions if text.count('\n',0,index)+1 == source.get('line')]
                candidates = exact if len(exact)==1 else positions
                supported = len(candidates)==1
                if supported:position=candidates[0]
            # Only explicitly approved links are atomic across separate sources.
            # Samples of one physical source stay together; equal-looking,
            # independent sources remain separate choices.
            stamp = path+'|'+str(position)+'|'+asset['snapshot'].get('source_sha256','')
            physical = 'use-'+hashlib.sha256(stamp.encode()).hexdigest()[:28] if supported else 'use-'+asset['id']
            key = asset['model_id'] if asset['model_id'].startswith('approved-') else physical
            row = self.models.setdefault(key, dict(id=key, model_id=asset['model_id'], name=asset.get('model_name') or asset['name'],
                games=[], classes=[], uses=[], supported=True))
            for token in sources.records[asset['id']].get('attrs',{}).get('class','').split():
                if token not in row['classes'] and not token.startswith(('is-','has-')):row['classes'].append(token)
            for game in asset.get('games') or [asset['game']]:
                if game not in row['games']: row['games'].append(game)
            if supported:
                self.snippets.setdefault(path.removeprefix('templates/'), {})[position] = (markup,key)
            row['supported'] &= supported
            row['uses'].append(dict(id=asset['id'], game=asset['game'], place=asset['usage'],
                label=asset['label'], state=asset.get('context_state') or '', path=path,
                context_preview='/api/button-usage/'+asset['id']+'/context' if supported else None))
        for row in self.models.values():
            row['coupled'] = len(row['uses']) > 1 or len(row['games']) > 1
            row['reason'] = '' if row['supported'] else 'Für diese Spielkomponente ist die lokale Zuordnung noch nicht freigegeben.'
        self.by_source = {use['id']: row['id'] for row in self.models.values() for use in row['uses']}

    def state(self):
        files = sorted(self.directory.glob('usage-*.json'), reverse=True)
        if not files: return dict(revision=None, bindings={})
        try:
            value = json.loads(files[0].read_text(encoding='utf-8'))
            if not isinstance(value['bindings'], dict): raise ValueError()
            return value
        except (OSError, ValueError, KeyError):
            raise ValueError('Die letzte Zuordnung konnte nicht gelesen werden. Sie wurde nicht verändert.')

    def catalog(self):
        state = self.state()
        recipes, bad = self.recipes.list()
        available = {r['id']: r for r in recipes if r['kind'] == 'button' and r['schema_version'] in (2, 4)}
        rows = deepcopy(list(self.models.values()))
        for row in rows:
            identifier = state['bindings'].get(row['id'])
            row['recipe_id'] = identifier
            row['active_name'] = available[identifier]['name'] if identifier in available else 'Entwurf nicht lesbar · Original wird verwendet' if identifier else 'Original'
            row['active_created'] = available[identifier]['created_at'] if identifier in available else None
        return dict(revision=state['revision'], models=rows,
            recipes=[dict(id=r['id'], name=r['name'], created=r['created_at'],
                source_model=self.by_source.get(r.get('source_button', {}).get('id'))) for r in available.values()],
            stale=[key for key in state['bindings'] if key not in self.models], unreadable=bad)

    def editor_recipe(self, identifier, catalog):
        if identifier not in self.by_source:
            raise ValueError('Dieser Spielbutton ist nicht registriert.')
        state = self.state()
        model = self.by_source[identifier]
        assigned = state['bindings'].get(model)
        if assigned:
            recipes, _ = self.recipes.list()
            recipe = next((r for r in recipes if r['id'] == assigned and r['kind'] == 'button'
                           and r['schema_version'] in (2, 4)), None)
            if recipe is None:
                raise ValueError('Der zugeordnete Buttonentwurf kann nicht gelesen werden. Bitte die Zuordnung prüfen.')
            return dict(recipe=deepcopy(recipe), persisted=True)
        return dict(recipe=self.sources.recipe(identifier, catalog), persisted=False)

    def http_get(self, handler, catalog, path):
        if not path.startswith('/api/button-usage/') or not path.endswith('/editor'):
            return False
        if handler.headers.get('Host') not in (f'127.0.0.1:{handler.server.server_port}', f'localhost:{handler.server.server_port}'):
            handler.json_response({'error':'Nur lokal erreichbar.'}, 403)
            return True
        identifier = path.removeprefix('/api/button-usage/').removesuffix('/editor')
        try:
            handler.json_response(self.editor_recipe(identifier, catalog))
        except (ValueError, OSError) as error:
            handler.json_response({'error':str(error)}, 400)
        return True

    def update(self, payload):
        if not isinstance(payload, dict) or set(payload) != {'revision', 'recipe_id', 'models'}:
            raise ValueError('Bitte einen Entwurf und seine Einsatzstellen wählen.')
        targets = payload['models']
        if not isinstance(targets, list) or not targets or any(not isinstance(key, str) for key in targets) or len(targets) != len(set(targets)):
            raise ValueError('Bitte mindestens eine eindeutige Einsatzgruppe wählen.')
        if any(not isinstance(key, str) or key not in self.models or not self.models[key]['supported'] for key in targets):
            raise ValueError('Eine ausgewählte Einsatzgruppe ist nicht verfügbar. Bitte die Übersicht neu laden.')
        identifier = payload['recipe_id']
        if identifier is not None:
            recipes, _ = self.recipes.list()
            recipe = next((r for r in recipes if r['id'] == identifier and r['kind'] == 'button' and r['schema_version'] in (2, 4)), None)
            if recipe is None: raise ValueError('Bitte zuerst einen vollständigen Buttonentwurf speichern.')
        with self.lock:
            self.directory.mkdir(parents=True, exist_ok=True)
            lock_path = self.directory/'writer.lock'
            try: descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except FileExistsError: raise UsageConflict('Eine Zuordnung wird gerade gespeichert. Bitte erneut versuchen.')
            try:
                state = self.state()
                if payload['revision'] != state['revision']:
                    raise UsageConflict('Die Zuordnungen wurden inzwischen geändert. Bitte die Übersicht neu öffnen.')
                bindings = dict(state['bindings'])
                for key in targets:
                    if identifier is None: bindings.pop(key, None)
                    else: bindings[key] = identifier
                revision = f'{time.time_ns():020d}-{uuid4().hex}'
                value = dict(revision=revision, bindings=bindings)
                temporary = self.directory/('pending-'+revision)
                with temporary.open('x', encoding='utf-8') as output:
                    json.dump(value, output, ensure_ascii=False, indent=2)
                temporary.replace(self.directory/('usage-'+revision+'.json'))
                return self.catalog()
            finally:
                os.close(descriptor)
                lock_path.unlink()

    def runtime(self):
        from button_bridge import storage
        state = self.state()
        recipes, _ = self.recipes.list()
        available = {r['id']: r for r in recipes if r['kind'] == 'button' and r['schema_version'] in (2, 4)}
        bindings = {key: value for key, value in state['bindings'].items()
                    if key in self.models and self.models[key]['supported'] and value in available}
        return dict(revision=state['revision'], bindings=bindings, sounds=storage.CATALOG['sounds'] if bindings else [],
                    recipes={identifier: {key: value for key, value in available[identifier].items()
                        if key in ('schema_version', 'renderer_version', 'settings', 'contour', 'base')}
                        for identifier in set(bindings.values())})

    def instrument(self, name, source):
        # Only in-memory template input changes. The original files/IDs remain exact.
        source = source.replace('\r\n','\n')
        for position, (markup,key) in sorted(self.snippets.get(name, {}).items(), reverse=True):
            if self.models[key]['supported'] and source[position:position+len(markup)]==markup:
                changed = re.sub(r'^<(button|a)\b', lambda m: m[0]+' data-workshop-model="'+key+'"', markup, count=1)
                source = source[:position]+changed+source[position+len(markup):]
        return source
