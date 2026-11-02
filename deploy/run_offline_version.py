"""Run a prepared version with its own files, database, cookies and port."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import runpy
import socket
import subprocess
import sys
import time
from urllib.request import ProxyHandler, build_opener
import webbrowser

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', default='1.2')
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--serve', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()
    if not args.version.replace('.', '').isdigit():
        parser.error('Invalid version')
    metadata = json.loads((ROOT/'releases'/f'{args.version}.json').read_text(encoding='utf-8'))
    workspace = (ROOT/metadata['workspace']).resolve()
    if not workspace.is_relative_to(ROOT/'offline-versions') or not (workspace/'deploy/run_local.py').is_file():
        parser.error('Prepared local workspace is missing')
    port = int(metadata['port'])
    url = f'http://127.0.0.1:{port}'
    if args.serve:
        sys.path[:0] = [str(workspace), str(ROOT/'.deps')]
        os.environ.update(QUIZ_OFFLINE_VERSION=args.version,
                          QUIZ_SESSION_COOKIE_NAME='guesstimate_offline_'+args.version.replace('.', '_'))
        sys.argv = [str(workspace/'deploy/run_local.py'), '--port', str(port)]
        runpy.run_path(sys.argv[0], run_name='__main__')
        return 0
    opener = build_opener(ProxyHandler({}))
    def ready():
        try:
            with opener.open(url+'/health', timeout=2) as response:
                health = json.load(response)
            with opener.open(url+'/static/favicon.svg', timeout=2) as response:
                icon = response.read()
            return health.get('status') == 'ok' and health.get('release') == args.version and \
                hashlib.sha256(icon).digest() == hashlib.sha256((workspace/'static/favicon.svg').read_bytes()).digest()
        except (OSError, ValueError):
            return False
    if args.check:
        print(f'Offline {args.version}: '+('bereit' if ready() else 'nicht gestartet'))
        return 0 if ready() else 1
    with socket.socket() as probe:
        occupied = probe.connect_ex(('127.0.0.1', port)) == 0
    process = None
    try:
        if occupied and not ready():
            parser.error(f'Port {port} is already occupied; nothing was stopped')
        if not occupied:
            log = workspace/'runtime/version-start.log'
            with log.open('ab') as output:
                process = subprocess.Popen([sys.executable, '-u', '-X', 'utf8', str(Path(__file__).resolve()),
                    '--version', args.version, '--serve'], cwd=workspace, stdout=output, stderr=subprocess.STDOUT,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            deadline = time.monotonic()+35
            while not ready():
                if process.poll() is not None or time.monotonic()>deadline:
                    raise RuntimeError('Start fehlgeschlagen. Hinweise: '+str(log))
                time.sleep(.2)
        if not args.no_browser:
            webbrowser.open(url+'/')
        print(f'Offline {args.version} bereit: {url}/', flush=True)
        while process and process.poll() is None:
            time.sleep(.3)
        return 0
    except KeyboardInterrupt:
        return 0
    finally:
        if process and process.poll() is None:
            process.terminate()
            process.wait(timeout=8)


if __name__ == '__main__':
    raise SystemExit(main())
