"""Local material workshop; separate source/recipe files, no game DB access."""
from argparse import ArgumentParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit, unquote
from storage import CATALOG, InvalidRecipe, RecipeStore, validate_recipe
from media_selection import FILES as MEDIA_FILES, matched_css

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0,str(ROOT/'offline-preview/game-workshop-v1'))
from source_buttons import SourceButtons
from button_usage import ButtonUsage, UsageConflict
FILES = {'/': HERE / 'index.html'}
FILES['/sammlung'] = ROOT / 'offline-preview/SAMMLUNG.html'
FILES['/source-check.html']=HERE/'source-check.html'
for name in ('index.html', 'workshop.css', 'embedded.css', 'materials.css', 'workshop.js', 'renderer.js', 'sound.js', 'layout-check.html', 'geometry.js', 'contour-editor.js', 'contour-editor.css', 'font-matching.js', 'fonts.css', 'library.css', 'source-renderer.js', 'unified-import.js', 'profile-capture.html'):
    FILES['/' + name] = HERE / name
for name in ('oak-v1.png', 'slate-v1.png', 'steel-v1.png', 'walnut-aged-v1.webp'):
    FILES['/assets/' + name] = HERE / 'assets' / name
for path in (HERE/'assets/fonts').iterdir():
    if path.suffix in ('.ttf', '.txt', '.json'):
        FILES['/assets/fonts/'+path.name] = path
for sound in CATALOG['sounds']:
    FILES['/assets/audio/'+sound['file']] = HERE/'assets/audio'/sound['file']
for name in ('catalog.json', 'CREDITS.md', 'Kenney-Impact-License.txt', 'Kenney-Interface-License.txt', 'Scrapes-CC0.txt', 'Robot-Attribution.txt'):
    FILES['/assets/audio/'+name] = HERE/'assets/audio'/name
FILES['/components.js'] = ROOT / 'offline-preview/comic-ui-v1/components.js'
for name in ('comic-button.css', 'typography-v1.css', 'favicon.svg', 'fonts/Inter-Variable.ttf', 'fonts/Fredoka-Variable.ttf'):
    FILES['/shared/' + name] = ROOT / 'static' / name
for name in ('components.js', 'comic-ui.css'):
    FILES['/shared/' + name] = ROOT / 'offline-preview/comic-ui-v1' / name
FILES['/media-renderer.js']=HERE/'media-renderer.js'
for name in ('button-usage.js','button-usage.css'):FILES['/'+name]=HERE/name
for name in ('button-context.js','button-context.css'):FILES['/'+name]=ROOT/'offline-preview/game-workshop-v1'/name
FILES.update(MEDIA_FILES)


class Handler(SimpleHTTPRequestHandler):
    def json_response(self, value, status=200):
        raw = json.dumps(value, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        path = unquote(urlsplit(self.path).path)
        if path.startswith('/api/button-usage/'):
            if self.headers.get('Host') not in (f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}'):
                return self.json_response({'error':'Nur lokal erreichbar.'},403)
            if self.server.button_usage.http_get(self,CATALOG,path):return
            from button_context import http_context
            if http_context(self,self.server.button_usage,path):return
        if path == '/api/button-usage':
            try:return self.json_response(self.server.button_usage.catalog())
            except ValueError as error:return self.json_response({'error':str(error)},400)
        if path=='/matched-media.css':
            raw=matched_css().encode('utf-8');self.send_response(200);self.send_header('Content-Type','text/css; charset=utf-8');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw);return
        if self.server.source_buttons.http_get(self,CATALOG,path):return
        if path == '/api/catalog':
            return self.json_response(CATALOG)
        if path == '/api/recipes':
            recipes, unreadable = self.server.store.list()
            return self.json_response({'recipes': recipes, 'unreadable': unreadable})
        return super().do_GET()

    def do_POST(self):
        path = urlsplit(self.path).path
        if path not in ('/api/recipes', '/api/validate','/api/button-usage'):
            return self.json_response({'error': 'Unbekannte Aktion.'}, 404)
        origin = self.headers.get('Origin')
        host = self.headers.get('Host', '')
        if host not in (f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}') or (origin and origin != 'http://' + host):
            return self.json_response({'error': 'Speichern ist nur aus dieser lokalen Werkstatt möglich.'}, 403)
        if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
            return self.json_response({'error': 'Bitte eine Entwurfsdatei verwenden.'}, 415)
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 32768:
                raise InvalidRecipe('Die Entwurfsdatei ist leer oder zu groß.')
            payload = json.loads(self.rfile.read(length))
            if path == '/api/button-usage':
                try:return self.json_response(self.server.button_usage.update(payload),201)
                except UsageConflict as error:return self.json_response({'error':str(error)},409)
                except ValueError as error:return self.json_response({'error':str(error)},400)
            result = self.server.store.save(payload) if path == '/api/recipes' else validate_recipe(payload)
            self.json_response({'recipe': result}, 201 if path == '/api/recipes' else 200)
        except (ValueError, UnicodeError) as error:
            message = str(error) if isinstance(error, InvalidRecipe) else 'Die Datei enthält keinen gültigen Entwurf.'
            self.json_response({'error': message}, 400)
        except OSError:
            self.json_response({'error': 'Speichern auf diesem PC hat nicht geklappt. Deine Eingaben bleiben erhalten.'}, 500)

    def send_head(self):
        if unquote(urlsplit(self.path).path) not in FILES and self.server.source_buttons.public_file(self.path) is None:
            self.send_error(404)
            return None
        return super().send_head()

    def translate_path(self, path):
        return str(FILES.get(unquote(urlsplit(path).path)) or self.server.source_buttons.public_file(path) or HERE / 'missing')

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()


def make_server(port=8771, directory=None):
    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    server.store = RecipeStore(directory or ROOT / 'design-library/recipes/button-workshop')
    server.source_buttons=SourceButtons()
    server.button_usage=ButtonUsage(Path(directory).parent/'usage-library' if directory else ROOT/'design-library',server.store,server.source_buttons)
    return server


if __name__ == '__main__':
    parser = ArgumentParser(description='Lokale Button-Werkstatt')
    parser.add_argument('--port', type=int, default=8771)
    parser.add_argument('--recipes-dir', type=Path, help='Getrennter Ablageordner für Prüfungen')
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error('Ungültiger Port.')
    server = make_server(args.port, args.recipes_dir)
    print(f'Button-Werkstatt: http://127.0.0.1:{args.port}/', flush=True)
    print(f'Entwürfe bleiben auf diesem PC: {server.store.directory}', flush=True)
    server.serve_forever()
