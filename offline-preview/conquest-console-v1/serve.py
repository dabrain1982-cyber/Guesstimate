"""Read-only local UI board. No game import, recipe writes or DB access."""
from argparse import ArgumentParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
WORKSHOP=HERE.parent/'button-workshop-v1'
FILES={'/':HERE/'index.html'}
for name in ('index.html','console.css','console.js','turn-console.js','model.js','profile.json','layout-check.html'):
    FILES['/'+name]=HERE/name
for name in ('renderer.js','geometry.js','materials.css','fonts.css','sound.js'):
    FILES['/workshop/'+name]=WORKSHOP/name
for name in ('components.js','comic-ui.css'):
    FILES['/shared/'+name]=HERE.parent/'comic-ui-v1'/name
FILES['/workshop/components.js']=HERE.parent/'comic-ui-v1/components.js'
for name in ('comic-button.css','typography-v1.css','player-portrait.js','player-portrait.css','favicon.svg','fonts/Inter-Variable.ttf','fonts/Fredoka-Variable.ttf'):
    FILES['/shared/'+name]=ROOT/'static'/name
FILES.update({'/shared/waschbaer.webp':ROOT/'static/avatars/stage/a05-waschbaer.webp',
              '/shared/fennek.webp':ROOT/'static/avatars/stage/a09-fennek.webp',
              '/shared/conquest-map.png':HERE.parent/'conquest-farbkarte-2026-10-24/stormseeds-conquest-farbkarte-v2.png'})
for name in ('oak-v1.png','slate-v1.png','steel-v1.png'):
    FILES['/assets/'+name]=WORKSHOP/'assets'/name
for path in (WORKSHOP/'assets/fonts').iterdir():
    if path.suffix in ('.ttf','.txt','.json'):FILES['/assets/fonts/'+path.name]=path
SOUNDS=json.loads((WORKSHOP/'assets/audio/catalog.json').read_text(encoding='utf-8'))['sounds']
for record in SOUNDS:FILES['/assets/audio/'+record['file']]=WORKSHOP/'assets/audio'/record['file']
FILES['/sound-catalog.json']=WORKSHOP/'assets/audio/catalog.json'
FILES['/sound-credits']=WORKSHOP/'assets/audio/CREDITS.md'

class Handler(SimpleHTTPRequestHandler):
    def send_head(self):
        if unquote(urlsplit(self.path).path) not in FILES:
            self.send_error(404);return None
        return super().send_head()
    def translate_path(self,path):return str(FILES.get(unquote(urlsplit(path).path),HERE/'missing'))
    def do_POST(self):self.send_error(405,'Diese Tafel speichert keine Daten.')
    def end_headers(self):self.send_header('Cache-Control','no-store');super().end_headers()

def make_server(port=8773):return ThreadingHTTPServer(('127.0.0.1',port),Handler)

if __name__=='__main__':
    parser=ArgumentParser(description='Conquest-Zugtafel lokal ansehen')
    parser.add_argument('--port',type=int,default=8773);args=parser.parse_args()
    if not 1024<=args.port<=65535:parser.error('Ungültiger Port.')
    print(f'Conquest-Tafel: http://127.0.0.1:{args.port}/',flush=True)
    make_server(args.port).serve_forever()
