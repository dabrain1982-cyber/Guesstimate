"""Serve the isolated Conquest example and its shared UI, without any database."""
from argparse import ArgumentParser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SHARED = {'/static/' + name: ROOT / 'static' / name for name in (
    'comic-button.css', 'player-portrait.js', 'player-portrait.css', 'typography-v1.css',
    'fonts/Inter-Variable.ttf', 'fonts/Fredoka-Variable.ttf',
)}
for public, folder, name in (
    ('button-renderer.js', 'button-workshop-v1', 'renderer.js'),
    ('geometry.js', 'button-workshop-v1', 'geometry.js'),
    ('components.js', 'comic-ui-v1', 'components.js'),
    ('button-materials.css', 'button-workshop-v1', 'materials.css'),
    ('button-sound.js', 'button-workshop-v1', 'sound.js'),
    ('button-assets/slate-v1.png', 'button-workshop-v1', 'assets/slate-v1.png'),
    ('button-assets/audio/catalog.json', 'button-workshop-v1', 'assets/audio/catalog.json'),
    ('button-assets/audio/wood-light.ogg', 'button-workshop-v1', 'assets/audio/wood-light.ogg'),
): SHARED['/' + public] = ROOT / 'offline-preview' / folder / name


class PreviewHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        path = unquote(urlsplit(self.path).path)
        if path.startswith('/static/') and path not in SHARED:
            self.send_error(404)
            return
        super().do_GET()

    def translate_path(self, path):
        public_path = unquote(urlsplit(path).path)
        return str(SHARED[public_path]) if public_path in SHARED else super().translate_path(path)


if __name__ == '__main__':
    parser = ArgumentParser(description='Isoliertes Conquest-Beispiel auf diesem PC')
    parser.add_argument('--port', type=int, default=54508)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error('Port muss zwischen 1024 und 65535 liegen.')
    handler = partial(PreviewHandler, directory=str(ROOT / 'offline-preview/conquest-2-5d-v1'))
    print(f'Isoliertes Beispiel ohne Spielstaende: http://127.0.0.1:{args.port}/', flush=True)
    ThreadingHTTPServer(('127.0.0.1', args.port), handler).serve_forever()
