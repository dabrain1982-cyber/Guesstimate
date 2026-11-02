"""Prepare a separate local workspace from a verified version and its data snapshot."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base',default='1.1')
    parser.add_argument('--version',default='1.2')
    parser.add_argument('--port',type=int,default=8784)
    args=parser.parse_args()
    if not all(v.replace('.','').isdigit() for v in (args.base,args.version)):
        parser.error('Numeric versions required')
    if not 1024<=args.port<=65535:
        parser.error('Invalid local port')
    record_path=ROOT/'releases'/f'{args.version}.json'
    workspace=ROOT/'offline-versions'/args.version
    if workspace.exists() or record_path.exists():
        parser.error('Target already exists; no existing version overwritten')
    base=json.loads((ROOT/'releases'/f'{args.base}.json').read_text(encoding='utf-8'))
    manifest=json.loads((ROOT/base['manifest']).read_text(encoding='utf-8'))
    if manifest['status']!='verified':
        parser.error('Base snapshot is not verified')
    workspace.mkdir(parents=True)
    count=0
    with zipfile.ZipFile(ROOT/base['archives']['code-and-assets.zip']['path']) as archive:
        for entry in manifest['files']['code-and-assets.zip']:
            target=(workspace/entry['path']).resolve()
            if not target.is_relative_to(workspace):
                raise RuntimeError('Unsafe archive path')
            raw=archive.read(entry['path'])
            if hashlib.sha256(raw).hexdigest()!=entry['sha256']:
                raise RuntimeError('Base file checksum differs: '+entry['path'])
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(raw)
            count+=1
    copied=[]
    with zipfile.ZipFile(ROOT/base['archives']['PRIVATE-PC-DATA-DO-NOT-UPLOAD.zip']['path']) as archive:
        names=set(archive.namelist())
        for relative in ('runtime/pc-local/quiz.sqlite3',
                         'runtime/conquest-hud-20261025/walkthrough.sqlite3',
                         'runtime/conquest-hud-20261025/preview-cases.json'):
            if relative not in names:
                if relative=='runtime/pc-local/quiz.sqlite3':
                    raise RuntimeError('Personal local game snapshot is missing')
                continue
            target=workspace/relative
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(archive.read(relative))
            if target.suffix=='.sqlite3':
                with sqlite3.connect(target.as_uri()+'?mode=ro',uri=True) as db:
                    if db.execute('PRAGMA quick_check').fetchone()[0]!='ok':
                        raise RuntimeError('Copied game database failed verification')
            copied.append(relative)
    # The new version owns a fresh signing key and a distinct cookie name.
    # The original account PIN hashes and all game data are copied as-is, never printed.
    record=dict(version=args.version,status='offline_prepared',base_version=args.base,
        base_manifest=base['manifest'],workspace=workspace.relative_to(ROOT).as_posix(),port=args.port,
        prepared_utc=datetime.now(timezone.utc).isoformat(),verified_source_files=count,
        copied_local_data=copied,deployed=False,new_signing_key_on_first_start=True,
        cookie_name='guesstimate_offline_'+args.version.replace('.','_'))
    record_path.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    starter=ROOT/f'Version-{args.version}-starten.cmd'
    starter.write_text('@echo off\npy -3 "%~dp0deploy\\run_offline_version.py" --version '+args.version+' %*\n',encoding='utf-8')
    (workspace/'Guesstimate-starten.cmd').write_text('@echo off\npy -3 "'+str(ROOT/'deploy/run_offline_version.py')+'" --version '+args.version+' %*\n',encoding='utf-8')
    (workspace/'VERSION.txt').write_text('Offline '+args.version+'\nBasis: '+args.base+'\n'+base['manifest']+'\n',encoding='utf-8')
    with (workspace/'AGENTS.md').open('a',encoding='utf-8') as handle:
        handle.write('\n\n## Identitaet dieser lokalen Arbeitskopie\n\nVersion '+args.version+
            ', getrennt von der gesicherten Basis '+args.base+'. Eigene lokale Spieldaten und Anmeldung.\n'+
            'Aenderungen fuer diese Version nur in diesem Ordner ausfuehren; urspruengliche Basis und Archive erhalten.\n')
    with (ROOT/'releases/events.jsonl').open('a',encoding='utf-8') as handle:
        handle.write(json.dumps(dict(event='offline_workspace_prepared',version=args.version,
            base=args.base,workspace=record['workspace'],deployed=False))+'\n')
    print(json.dumps(record,ensure_ascii=False),flush=True)


if __name__=='__main__': main()
