"""Loopback-only editor and personal library, without loading the live app."""
from argparse import ArgumentParser
import ast
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import unquote, urlsplit, parse_qs
from jinja2 import Environment, FileSystemLoader, select_autoescape
from library_store import Library, SCHEMA, PRESETS, ROOT, HERE, settings, InvalidDesign
from workspace_store import ProjectLibrary
from workshop_catalog import ELEMENT_KINDS, PRESENTATION, existing_assets
from button_bridge import storage as button_storage, public_files
from image_store import MAX_BYTES, IMAGE_KINDS
from button_usage import ButtonUsage, UsageConflict

FILES = {'/': HERE/'index.html', '/sammlung': ROOT/'offline-preview/SAMMLUNG.html'}
FILES['/shared/profile-stage-v1.js'] = ROOT/'static/profile-stage-v1.js'
FILES['/shared/player-portrait.js'] = ROOT/'static/player-portrait.js'
for name in ('avatar-editor.js','avatar-editor.css','avatar-renderer.js','avatar-stage.css'):FILES['/'+name]=HERE/name
for name in ('index.html', 'workshop.css', 'workshop.js', 'properties.js', 'properties.css', 'image-editor.js', 'image-import.js', 'image-editor.css', 'scene.js', 'models.js', 'motion.js', 'lobby-preview.css', 'layout-check.html', 'image-layout-check.html', 'button-review.js', 'button-review.css', 'button-context.js', 'button-context.css'):
    FILES['/' + name] = HERE/name
for name in ('three.module.js', 'three.core.js', 'LICENSE'):
    FILES['/vendor/' + name] = ROOT/'offline-preview/conquest-2-5d-v1/vendor/three'/name
for key, path in {
    'room.png':'offline-preview/conquest-2-5d-v1/assets/raum-ohne-tisch.png',
    'wood.png':'offline-preview/button-workshop-v1/assets/oak-v1.png',
    'slate.png':'offline-preview/button-workshop-v1/assets/slate-v1.png',
}.items():
    FILES['/assets/'+key] = ROOT/path
FILES.update(public_files(ROOT))
for name in ('window-editor.js','window-editor.css'):FILES['/'+name]=HERE/name
for name in ('board-editor.js','board-editor.css'):FILES['/'+name]=HERE/name
for name in ('piece-editor.js','piece-editor.css'):FILES['/'+name]=HERE/name
for name in ('card-editor.js','card-editor.css','card-authoring.js','card-authoring.css'):FILES['/'+name]=HERE/name

# Read declarative cosmetic catalogs without importing app.py or opening its DB.
NAMES = ('AVATAR_CATALOG', 'PLAQUE_CATALOG', 'BACKGROUND_CATALOG', 'DEFAULT_AVATAR', 'DEFAULT_PLAQUE', 'DEFAULT_BACKGROUND')
CATALOGS = {}
for statement in ast.parse((ROOT/'app.py').read_text(encoding='utf-8')).body:
    if isinstance(statement, ast.Assign):
        for target in statement.targets:
            if isinstance(target, ast.Name) and target.id in NAMES:
                CATALOGS[target.id] = ast.literal_eval(statement.value)
ENV = Environment(loader=FileSystemLoader([str(HERE), str(ROOT/'templates')]), autoescape=select_autoescape(['html']))
ENV.filters['points'] = lambda v: str(v)
EXISTING_ASSETS = existing_assets(CATALOGS)


def inventory_families():
    report=ROOT/'docs/WERKSTATT_BESTAND.json'
    try:return [dict(id=f['id'],name=f['name']) for f in json.loads(report.read_text(encoding='utf-8'))['families']]
    except (OSError,ValueError,KeyError):return []


def lobby_preview(value):
    cfg = settings('lobby', value)
    catalog = lambda name, default: {v['id']:v for v in [CATALOGS[default], *CATALOGS[name]]}
    players = [dict(id=i, user_id=i, seat=i, display_name='Dein Platz' if i == 1 else f'Musterplatz {i}',
                    cosmetics=dict(avatar_id=cfg['avatar'], plaque_id=cfg['plaque'], background_id='b02', phrase_id=''))
               for i in range(1, cfg['seats'] + 1)]
    images = {'club':'stormseeds-perfect-clubroom-table-v2.png', 'cards':'card-tables-background-v1.png', 'conquest':'conquest-lobby-background-v1.png'}
    return ENV.get_template('lobby-preview.html').render(
        cfg=cfg, background=images[cfg['background']], players=players,
        lobby=dict(id='workshop', name=cfg['title'], status='waiting', host_user_id=1),
        g=SimpleNamespace(user=SimpleNamespace(id=1)), currency_balance=0,
        avatar_catalog=catalog('AVATAR_CATALOG', 'DEFAULT_AVATAR'),
        plaque_catalog=catalog('PLAQUE_CATALOG', 'DEFAULT_PLAQUE'),
        background_catalog=catalog('BACKGROUND_CATALOG', 'DEFAULT_BACKGROUND'),
        phrase_catalog={}, default_phrase='Ein guter Zug beginnt hier.',
        # Library previews use neutral players; profile links stay in the preview.
        url_for=lambda endpoint, **args: '/shared/' + args['filename'] if endpoint == 'static' else '#',
    )


class Handler(SimpleHTTPRequestHandler):
    def image_response(self,raw):
        self.send_response(200)
        self.send_header('Content-Type','image/png')
        self.send_header('Content-Length',str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def json_response(self, value, status=200):
        raw = json.dumps(value, ensure_ascii=False, allow_nan=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def local_host(self):
        return self.headers.get('Host') in (f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}')

    def do_GET(self):
        if not self.local_host():
            return self.json_response({'error':'Nur lokal erreichbar.'}, 403)
        path = unquote(urlsplit(self.path).path)
        if self.server.library.button_usage.http_get(self,button_storage.CATALOG,path):return
        from button_context import http_context
        if http_context(self,self.server.library.button_usage,path):return
        if path == '/api/window-designs':return self.json_response(self.server.library.window_designs.config())
        if path == '/api/board-designs':return self.json_response(self.server.library.board_designs.config())
        if path == '/api/piece-designs':return self.json_response(self.server.library.piece_designs.config())
        if path == '/api/card-designs':return self.json_response(self.server.library.card_designs.config())
        if path == '/api/avatar-designs':return self.json_response(self.server.library.avatar_designs.config())
        if path.startswith('/api/avatar-designs/') and path.endswith('/preview'):
            try:
                store=self.server.library.avatar_designs;record=store.get(path.removeprefix('/api/avatar-designs/').removesuffix('/preview'))
                raw=store.preview(record['source_id'],record['recipe'],record['settings'],parse_qs(urlsplit(self.path).query).get('interactive')==['1']).encode('utf-8')
                self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(raw)))
                self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'self'; object-src 'none'; base-uri 'none'; form-action 'none'")
                self.end_headers();self.wfile.write(raw);return
            except (ValueError,OSError) as error:return self.json_response({'error':str(error)},400)
        if path.startswith('/api/card-designs/') and path.endswith('/preview'):
            try:
                store=self.server.library.card_designs;query=parse_qs(urlsplit(self.path).query)
                record=store.get(path.removeprefix('/api/card-designs/').removesuffix('/preview'))
                raw=store.preview(record['settings'],record['members'],query.get('interactive')==['1'],member_id=query.get('member',[None])[0]).encode('utf-8')
                self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(raw)))
                self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'self'; object-src 'none'; base-uri 'none'; form-action 'none'")
                self.end_headers();self.wfile.write(raw);return
            except (ValueError,OSError) as error:return self.json_response({'error':str(error)},400)
        if path.startswith('/api/piece-designs/') and path.endswith('/preview'):
            try:
                store=self.server.library.piece_designs
                record=store.get(path.removeprefix('/api/piece-designs/').removesuffix('/preview'))
                raw=store.preview(record['settings'],parse_qs(urlsplit(self.path).query).get('interactive')==['1']).encode('utf-8')
                self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(raw)))
                self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'self'; object-src 'none'; base-uri 'none'; form-action 'none'")
                self.end_headers();self.wfile.write(raw);return
            except (ValueError,OSError) as error:return self.json_response({'error':str(error)},400)
        if path.startswith('/api/board-designs/') and path.endswith('/preview'):
            try:
                store=self.server.library.board_designs
                record=store.get(path.removeprefix('/api/board-designs/').removesuffix('/preview'))
                raw=store.preview(record['settings'],parse_qs(urlsplit(self.path).query).get('interactive')==['1']).encode('utf-8')
                self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(raw)))
                self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'self'; object-src 'none'; base-uri 'none'; form-action 'none'")
                self.end_headers();self.wfile.write(raw);return
            except (ValueError,OSError) as error:return self.json_response({'error':str(error)},400)
        if path.startswith('/api/window-designs/') and path.endswith('/preview'):
            try:
                store=self.server.library.window_designs
                record=store.get(path.removeprefix('/api/window-designs/').removesuffix('/preview'))
                raw=store.preview(record['source_id'],record['settings']).encode('utf-8')
                self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(raw)))
                self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'none'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; form-action 'none'; frame-ancestors 'self'")
                self.end_headers();self.wfile.write(raw);return
            except (ValueError,OSError) as error:return self.json_response({'error':str(error)},400)
        if path == '/api/button-usage':
            try:return self.json_response(self.server.library.button_usage.catalog())
            except ValueError as error:return self.json_response({'error':str(error)},400)
        if path=='/button-editor/matched-media.css':
            from media_selection import matched_css
            raw=matched_css().encode('utf-8');self.send_response(200);self.send_header('Content-Type','text/css; charset=utf-8');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw);return
        if path == '/api/library':
            elements, bad_e = self.server.library.list('elements')
            projects, bad_p = self.server.library.list('projects')
            assets=self.server.library.assets()
            return self.json_response(dict(schema=SCHEMA, presets=PRESETS, elements=elements, projects=projects,
                                           buttons=self.server.library.buttons(), unreadable=bad_e+bad_p+self.server.library.images.records()[1]+self.server.library.window_designs.list()[1]+self.server.library.board_designs.list()[1]+self.server.library.piece_designs.list()[1]+self.server.library.card_designs.list()[1]+self.server.library.avatar_designs.list()[1],
                                           kinds=ELEMENT_KINDS, presentation=PRESENTATION, assets=assets,
                                           properties=self.server.library.properties.catalog(assets),
                                           project_groups=self.server.library.project_groups(),
                                           project_views=[self.server.library.project_view(p) for p in projects],
                                           image_kinds=IMAGE_KINDS,inventory_families=inventory_families()))
        try:
            if self.server.library.rooms.http_get(self,path):return
            if self.server.library.completion.http_get(self,path):return
            if self.server.library.media.http_get(self,path):return
            if self.server.library.graphics.http_get(self,path):return
            if self.server.library.pieces.http_get(self,path):return
            if self.server.library.boards.http_get(self,path):return
            if self.server.library.dice.http_get(self,path):return
            if self.server.library.cards.http_get(self,path):return
            if self.server.library.source_lobbies.http_get(self,path):return
            if self.server.library.source_players.http_get(self,path):return
            if self.server.library.source_indicators.http_get(self,path):return
            if self.server.library.source_inputs.http_get(self,path):return
            if self.server.library.source_windows.http_get(self,path):return
            if self.server.library.source_buttons.http_get(self,button_storage.CATALOG,path):return
            if path == '/api/images/source':
                identifier=parse_qs(urlsplit(self.path).query).get('id',[''])[0]
                return self.json_response(self.server.library.images.info(identifier))
            if path.startswith('/image-sources/') and path.endswith('.png'):
                return self.image_response(self.server.library.images.source_preview(path[len('/image-sources/'):-4]))
            if path.startswith('/library-images/'):
                parts=path.split('/')
                if len(parts)!=4 or parts[3] not in ('view.png','thumb.png'):raise InvalidDesign('Unbekannte Bildansicht.')
                return self.image_response(self.server.library.images.view(parts[2],parts[3]=='thumb.png'))
        except (ValueError,OSError) as error:
            return self.json_response({'error':str(error) if isinstance(error,InvalidDesign) else 'Das Bild konnte nicht gelesen werden.'},400)
        if path == '/api/catalog':
            return self.json_response(button_storage.CATALOG)
        if path == '/api/recipes':
            recipes, unreadable = self.server.library.button_store.list()
            return self.json_response(dict(recipes=recipes,unreadable=unreadable))
        if path == '/health':
            return self.json_response({'status':'ok', 'service':'game-workshop-v1'})
        return super().do_GET()

    def do_POST(self):
        host = self.headers.get('Host', '')
        if not self.local_host() or self.headers.get('Origin', 'http://' + host) != 'http://' + host:
            return self.json_response({'error':'Speichern ist nur aus dieser lokalen Werkstatt möglich.'}, 403)
        path = urlsplit(self.path).path
        if path == '/api/images/import':
            try:
                length=int(self.headers.get('Content-Length',0))
                if not 0<length<=MAX_BYTES:raise InvalidDesign('Bitte ein Bild mit höchstens 20 MB wählen.')
                record=self.server.library.images.import_image(self.rfile.read(length),unquote(self.headers.get('X-Filename','Mein Bild')),
                                                              self.headers.get('X-Image-Kind','background'))
                return self.json_response({'asset':self.server.library.images.as_asset(record)},201)
            except (ValueError,OSError) as error:
                return self.json_response({'error':str(error) if isinstance(error,InvalidDesign) else 'Das Bild konnte nicht importiert werden.'},400)
        if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
            return self.json_response({'error':'Bitte eine Projektdatei verwenden.'}, 415)
        try:
            length = int(self.headers.get('Content-Length', 0))
            if not 0 < length <= 131072:
                raise InvalidDesign('Die Projektdatei ist leer oder zu groß.')
            value = json.loads(self.rfile.read(length))
            path = urlsplit(self.path).path
            if path == '/api/button-usage':
                try:return self.json_response(self.server.library.button_usage.update(value),201)
                except UsageConflict as error:return self.json_response({'error':str(error)},409)
                except ValueError as error:return self.json_response({'error':str(error)},400)
            if path == '/api/window-designs/preview':
                return self.json_response(self.server.library.window_designs.preview_request(value))
            if path == '/api/window-designs':
                record=self.server.library.window_designs.save(value)
                return self.json_response({'asset':self.server.library.window_designs.asset(record)},201)
            if path == '/api/board-designs/preview':
                if not isinstance(value,dict) or set(value) not in ({'settings'},{'settings','view'}):raise InvalidDesign('Bitte die Bretteinstellungen wählen.')
                return self.json_response({'html':self.server.library.board_designs.preview(value['settings'],view=value.get('view'))})
            if path == '/api/board-designs':
                record=self.server.library.board_designs.save(value)
                return self.json_response({'asset':self.server.library.board_designs.asset(record)},201)
            if path == '/api/piece-designs/preview':
                if not isinstance(value,dict) or set(value) not in ({'settings'},{'settings','view'}):raise InvalidDesign('Bitte die Figureneinstellungen wählen.')
                return self.json_response({'html':self.server.library.piece_designs.preview(value['settings'],view=value.get('view'))})
            if path == '/api/piece-designs':
                record=self.server.library.piece_designs.save(value)
                return self.json_response({'asset':self.server.library.piece_designs.asset(record)},201)
            if path == '/api/card-designs/preview':
                if not isinstance(value,dict) or set(value) not in ({'settings','members'},{'settings','members','view'}):raise InvalidDesign('Bitte Gestaltung und Karten des Satzes wählen.')
                return self.json_response({'html':self.server.library.card_designs.preview(value['settings'],value['members'],view=value.get('view'))})
            if path == '/api/card-designs':
                record=self.server.library.card_designs.save(value)
                return self.json_response({'asset':self.server.library.card_designs.asset(record)},201)
            if path == '/api/avatar-designs/preview':
                if not isinstance(value,dict) or set(value)!={'source_id','recipe','settings'}:raise InvalidDesign('Bitte Bildausschnitt und Avatargestaltung wählen.')
                return self.json_response({'html':self.server.library.avatar_designs.preview(value['source_id'],value['recipe'],value['settings'])})
            if path == '/api/avatar-designs':
                record=self.server.library.avatar_designs.save(value)
                return self.json_response({'asset':self.server.library.avatar_designs.asset(record)},201)
            if path == '/api/elements':
                result = {'element':self.server.library.save_element(value)}
            elif path == '/api/images/preview':
                if not isinstance(value,dict) or set(value)!={'source_id','recipe'}:raise InvalidDesign('Ungültige Bildvorschau.')
                raw,_,_=self.server.library.images.render(value['source_id'],value['recipe'],preview=True)
                return self.image_response(raw)
            elif path == '/api/images/variants':
                record=self.server.library.images.save_variant(value)
                result = {'asset':self.server.library.images.as_asset(record)}
            elif path == '/api/recipes':
                if length > 32768:raise InvalidDesign('Die Entwurfsdatei ist zu groß.')
                result = {'recipe':self.server.library.button_store.save(value)}
            elif path == '/api/validate':
                return self.json_response({'recipe':button_storage.validate_recipe(value)})
            elif path == '/api/projects':
                result = {'project':self.server.library.save_project(value)}
            elif path == '/api/handoff':
                if not isinstance(value, dict) or set(value) != {'project_id'}:
                    raise InvalidDesign('Bitte zuerst die Projektmappe speichern.')
                record = self.server.library.handoff(value['project_id'])
                result = {'handoff':record, 'path':str(self.server.library.directory/'handoffs'/(record['id']+'.json'))}
            elif path == '/api/lobby':
                return self.json_response({'html':lobby_preview(value)})
            else:
                return self.json_response({'error':'Unbekannte Aktion.'}, 404)
            return self.json_response(result, 201)
        except (ValueError, UnicodeError) as error:
            return self.json_response({'error':str(error) if isinstance(error, (InvalidDesign,button_storage.InvalidRecipe)) else 'Die Datei enthält keinen gültigen Entwurf.'}, 400)
        except OSError:
            return self.json_response({'error':'Speichern hat nicht geklappt. Deine Eingaben bleiben erhalten.'}, 500)

    def file_path(self):
        path = unquote(urlsplit(self.path).path)
        room_file = self.server.library.rooms.file_path(path)
        if room_file:return room_file
        media_file = self.server.library.media.file_path(path)
        if media_file:return media_file
        graphic_file = self.server.library.graphics.file_path(path)
        if graphic_file:return graphic_file
        piece_file = self.server.library.pieces.file_path(path)
        if piece_file:return piece_file
        board_file = self.server.library.boards.file_path(path)
        if board_file is not None:return board_file
        dice_file = self.server.library.dice.file_path(path)
        if dice_file is not None:return dice_file
        card_file = self.server.library.cards.file_path(path)
        if card_file is not None:return card_file
        if path in FILES:
            return FILES[path]
        if path.startswith(('/shared/','/static/')):
            candidate = (ROOT/'static'/path.split('/',2)[2]).resolve()
            if candidate.is_relative_to(ROOT/'static') and candidate.suffix in ('.png', '.webp', '.svg', '.jpg', '.css', '.ttf') and candidate.is_file():
                return candidate
        if path.startswith('/conquest-source/'):
            root=ROOT/'offline-preview/conquest-2-5d-v1'
            candidate=(root/path.removeprefix('/conquest-source/')).resolve()
            if candidate.is_relative_to(root) and candidate.suffix in ('.css','.png','.webp','.svg','.jpg','.ttf') and candidate.is_file():return candidate
        return None

    def send_head(self):
        if self.file_path() is None:
            self.send_error(404)
            return None
        return super().send_head()

    def translate_path(self, path):
        return str(self.file_path() or HERE/'missing')

    def end_headers(self):
        digest=parse_qs(urlsplit(self.path).query).get('source_sha',[''])[0]
        file=self.file_path() if digest else None
        immutable=file and file.suffix=='.css' and hashlib.sha256(file.read_bytes()).hexdigest()==digest
        self.send_header('Cache-Control', 'private, max-age=31536000, immutable' if immutable else 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        super().end_headers()


def make_server(port=8776, directory=None, buttons_directory=None):
    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    server.library = ProjectLibrary(directory, buttons_directory, EXISTING_ASSETS)
    server.library.button_usage = ButtonUsage(server.library.directory,server.library.button_store,server.library.source_buttons)
    return server


if __name__ == '__main__':
    parser = ArgumentParser(description='Lokale Spielewerkstatt')
    parser.add_argument('--port', type=int, default=8776)
    parser.add_argument('--library-dir', type=Path)
    parser.add_argument('--buttons-dir', type=Path)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error('Ungültiger Port.')
    server = make_server(args.port, args.library_dir, args.buttons_dir)
    print(f'Spielewerkstatt: http://127.0.0.1:{args.port}/', flush=True)
    print(f'Persönliche Bibliothek: {server.library.directory}', flush=True)
    server.serve_forever()
