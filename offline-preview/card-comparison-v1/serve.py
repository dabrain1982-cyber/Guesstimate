"""Read-only local comparison. No app imports, game requests or database access."""
from argparse import ArgumentParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
THREE = ROOT / 'offline-preview/conquest-2-5d-v1/vendor/three'


def original_factory():
    source = (ROOT / 'static/card-table.js').read_text(encoding='utf-8')
    start = source.index('  const cardElement = (card) => {')
    stop = source.index('\n  const renderCards = ', start)
    factory = source[start:stop]
    return ('// Original factory read directly from static/card-table.js at request time.\n'
            'export function originalCard(card, onFlip) {\n'
            'const room={dataset:{memberId:"sample"}};let dragging=false;\n'
            'const postAction=async()=>onFlip();const poll=async()=>{};\n'
            + factory + '\nreturn cardElement(card);\n}\n')


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.headers.get('Host') not in (f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'):
            return self.send_error(403)
        path = unquote(urlsplit(self.path).path)
        if path in ('/original/card.js', '/health'):
            raw = (original_factory() if path.endswith('.js') else json.dumps({'status': 'ok', 'service': 'card-comparison-v1', 'read_only': True})).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/javascript; charset=utf-8' if path.endswith('.js') else 'application/json')
            self.send_header('Content-Length', str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
            return
        super().do_GET()

    def file_path(self):
        path = unquote(urlsplit(self.path).path)
        original = {'/original/card.css': ROOT/'static/card-table.css',
                    '/original/guesstimate-card-back-v1.png': ROOT/'static/guesstimate-card-back-v1.png',
                    '/fonts/Inter.ttf': ROOT/'static/fonts/Inter-Variable.ttf',
                    '/fonts/Fredoka.ttf': ROOT/'static/fonts/Fredoka-Variable.ttf'}
        if path in original:
            return original[path]
        if path.startswith('/vendor/'):
            file = THREE / path.removeprefix('/vendor/')
            return file if file.name in ('three.module.js', 'three.core.js', 'LICENSE') and file.parent == THREE else None
        file = (HERE / ('index.html' if path == '/' else path.lstrip('/'))).resolve()
        if file.is_relative_to(HERE) and file.is_file() and file.suffix in ('.html', '.js', '.css', '.json', '.png', '.md', '.txt', '.obj', '.mtl', '.blend'):
            return file
        return None

    def send_head(self):
        if self.file_path() is None:
            self.send_error(404)
            return None
        return super().send_head()

    def translate_path(self, path):
        return str(self.file_path() or HERE/'missing')

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; font-src 'self'; frame-src 'self'; frame-ancestors 'self'; object-src 'none'; base-uri 'none'; form-action 'none'")
        super().end_headers()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--port', type=int, default=8778)
    port = parser.parse_args().port
    if not 1024 <= port <= 65535:
        parser.error('Ungültiger Port')
    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    print(f'Kartenvergleich: http://127.0.0.1:{port}/', flush=True)
    server.serve_forever()
