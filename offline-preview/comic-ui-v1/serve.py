"""Local design preview: allowlisted files only, no app import or database access."""
from argparse import ArgumentParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
FILES={'/':HERE/'index.html',**{'/'+name:HERE/name for name in ('index.html','comic-ui.css','components.js','preview.js')},
       '/reference.png':ROOT/'runtime/comic-ui-v1-20261025/reference.png',
       '/check-widths':ROOT/'runtime/comic-ui-v1-20261025/qa-widths.html'}
for name in ('comic-button.css','typography-v1.css','player-portrait.js','player-portrait.css','favicon.svg','fonts/Inter-Variable.ttf','fonts/Fredoka-Variable.ttf'):
    FILES['/shared/'+name]=ROOT/'static'/name
FILES.update({'/shared/waschbaer.webp':ROOT/'static/avatars/stage/a05-waschbaer.webp',
              '/shared/fennek.webp':ROOT/'static/avatars/stage/a09-fennek.webp',
              '/shared/conquest-map.png':ROOT/'offline-preview/conquest-2-5d-v1/assets/karte.png'})


class Handler(SimpleHTTPRequestHandler):
    def send_head(self):
        if unquote(urlsplit(self.path).path) not in FILES:
            self.send_error(404)
            return None
        return super().send_head()

    def translate_path(self,path):
        return str(FILES.get(unquote(urlsplit(path).path),HERE/'missing'))

    def end_headers(self):
        self.send_header('Cache-Control','no-store')
        super().end_headers()


if __name__=='__main__':
    parser=ArgumentParser(description='Comic-Gestaltungsentwurf lokal ansehen')
    parser.add_argument('--port',type=int,default=8770)
    args=parser.parse_args()
    if not 1024<=args.port<=65535:parser.error('Ungültiger Port.')
    print(f'Comic-Vorschau: http://127.0.0.1:{args.port}/',flush=True)
    ThreadingHTTPServer(('127.0.0.1',args.port),Handler).serve_forever()
