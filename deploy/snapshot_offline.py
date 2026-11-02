"""Verified local backup, with private PC data kept out of the source archive."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[1]
SKIP={'.git','.deps','.venv','node_modules','__pycache__','.pytest_cache'}
PRIVATE={'runtime','config','instance','.ssh','.codex','.agents'}
CONTROL={'releases','offline-versions'}

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def private(path):
    return (path.parts[0] in PRIVATE or
            path.name.startswith('.env') and not path.name.endswith('.example') or
            path.suffix.lower() in {'.sqlite','.sqlite3','.db','.secret','.key','.pem','.pfx','.p12'})

def files(root):
    for base,dirs,names in os.walk(root,followlinks=False):
        dirs[:]=sorted(n for n in dirs if n not in SKIP and not (Path(base)/n).is_symlink()
                       and (Path(base)/n).relative_to(root).parts[0] not in CONTROL
                       and (Path(base)/n).relative_to(root).as_posix()!='runtime/version-backups')
        for name in sorted(names):
            p=Path(base)/name
            if p.is_symlink() or p.suffix in {'.pyc','.pyo'}:continue
            if name.endswith(('-wal','-shm','-journal')):continue
            yield p

def snapshot_db(source,target):
    target.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(source.resolve().as_uri()+'?mode=ro',uri=True,timeout=30) as original:
        original.execute('PRAGMA query_only=ON')
        with sqlite3.connect(target) as copy:
            original.backup(copy,pages=1024,sleep=.02)
            result=copy.execute('PRAGMA quick_check').fetchall()
            if result!=[('ok',)]:raise RuntimeError('SQLite check failed: '+str(source.relative_to(ROOT)))

def archive(paths,target,db_staging):
    entries=[]
    with zipfile.ZipFile(target,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=3,allowZip64=True) as z:
        for index,source in enumerate(paths,1):
            rel=source.relative_to(ROOT);stored=source;db=False
            if source.suffix.lower() in {'.sqlite','.sqlite3','.db'}:
                with source.open('rb') as f:db=f.read(16)==b'SQLite format 3\x00'
                if db:
                    stored=db_staging/rel;snapshot_db(source,stored)
            before=stored.stat();raw=stored.read_bytes();after=stored.stat()
            if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):
                raise RuntimeError('File changed during capture: '+str(rel))
            z.writestr(rel.as_posix(),raw)
            entries.append(dict(path=rel.as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),sqlite_snapshot=db,
                                source_size=source.stat().st_size,source_mtime_ns=source.stat().st_mtime_ns))
            if index%500==0:print(target.name,index,'files captured',flush=True)
    with zipfile.ZipFile(target) as z:
        if len(z.infolist())!=len(entries):raise RuntimeError('Archive entry count differs')
        for entry in entries:
            if hashlib.sha256(z.read(entry['path'])).hexdigest()!=entry['sha256']:
                raise RuntimeError('Archive checksum differs: '+entry['path'])
    return entries

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version',required=True)
    parser.add_argument('--append-revision',action='store_true',help='Add a new verified snapshot without replacing old archives')
    parser.add_argument('--acceptance',default='local checks passed; user acceptance and real multiplayer test pending')
    args=parser.parse_args()
    if not args.version.replace('.','').isdigit():parser.error('Use a numeric version, such as1.1')
    records=ROOT/'releases';records.mkdir(exist_ok=True)
    record_path=records/(args.version+'.json')
    previous=json.loads(record_path.read_text(encoding='utf-8')) if record_path.exists() else None
    if previous and not args.append_revision:
        parser.error('Version already registered; use --append-revision to retain and extend it')
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out=ROOT/'runtime/version-backups'/f'{args.version}-{stamp}';out.mkdir(parents=True,exist_ok=False)
    git_base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    git_status=subprocess.check_output(['git','status','--porcelain=v1','-uall'],cwd=ROOT,text=True)
    selected=list(files(ROOT));source=[p for p in selected if not private(p.relative_to(ROOT))];personal=[p for p in selected if private(p.relative_to(ROOT))]
    print('Snapshot',args.version,'source files',len(source),'private files',len(personal),flush=True)
    manifest=dict(schema=1,version=args.version,created_utc=stamp,status='capturing',git_base=git_base,
                  acceptance=args.acceptance,server_activation=False,
                  backup_scope='local workspace, including untracked and ignored project assets; installed dependencies/caches excluded',
                  dependency_exclusions=sorted(SKIP),control_metadata='releases/ stored alongside version records',archives={},files={})
    for name,paths in [('code-and-assets.zip',source),('PRIVATE-PC-DATA-DO-NOT-UPLOAD.zip',personal)]:
        target=out/name;entries=archive(paths,target,out/'PRIVATE-sqlite-snapshots')
        manifest['files'][name]=entries
        manifest['archives'][name]=dict(path=target.relative_to(ROOT).as_posix(),bytes=target.stat().st_size,sha256=digest(target),file_count=len(entries),verified=True,
                                       sqlite_count=sum(e['sqlite_snapshot'] for e in entries),local_only=True)
        print(name,'verified',len(entries),'files',target.stat().st_size,'bytes',flush=True)
    # Already-existing commits plus the complete dirty source tree above are both retained.
    bundle=out/'repository.bundle'
    subprocess.run(['git','bundle','create',str(bundle),'--all'],cwd=ROOT,check=True,capture_output=True)
    subprocess.run(['git','bundle','verify',str(bundle)],cwd=ROOT,check=True,capture_output=True)
    manifest['git_bundle']=dict(path=bundle.relative_to(ROOT).as_posix(),bytes=bundle.stat().st_size,sha256=digest(bundle),verified=True)
    changed=[]
    for entry in manifest['files']['code-and-assets.zip']:
        current=(ROOT/entry['path']).stat()
        if (current.st_size,current.st_mtime_ns)!=(entry['source_size'],entry['source_mtime_ns']):changed.append(entry['path'])
    if changed:raise RuntimeError('Source changed while backing up: '+', '.join(changed))
    manifest['status']='verified'
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (out/'git-status.txt').write_text(git_status,encoding='utf-8')
    (out/'README.txt').write_text('LOCAL BACKUP '+args.version+'\n\nAll ZIP entries were read back and SHA-256 checked. SQLite files were captured through the online backup API and quick_check.\nPRIVATE-PC-DATA-DO-NOT-UPLOAD.zip and PRIVATE-sqlite-snapshots are private local data, never a server deployment payload.\ncode-and-assets.zip is a complete offline source snapshot, not a reviewed activation package.\nSource + assets can be restored separately from data. Do not overwrite server runtime/config/accounts when rolling back application code.\nInstalled dependencies are excluded; requirement files are included. Git history is in repository.bundle; dirty and untracked work is in code-and-assets.zip.\n',encoding='utf-8')
    record=dict(version=args.version,status='local_snapshot_verified',acceptance=args.acceptance,
                server='not inspected or numbered yet',deployed=False,manifest=(out/'manifest.json').relative_to(ROOT).as_posix(),archives=manifest['archives'],git_bundle=manifest['git_bundle'])
    if previous:
        history=records/'history';history.mkdir(exist_ok=True)
        retained=history/f'{args.version}-before-{stamp}.json'
        with retained.open('x',encoding='utf-8') as handle:
            json.dump(previous,handle,ensure_ascii=False,indent=2);handle.write('\n')
        record['previous_manifests']=list(dict.fromkeys([*previous.get('previous_manifests',[]),previous['manifest']]))
        record['previous_record']=retained.relative_to(ROOT).as_posix()
    record_path.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with (records/'events.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(dict(time_utc=stamp,event='local_snapshot_revision_verified' if previous else 'local_snapshot_verified',version=args.version,manifest=record['manifest'],deployed=False))+'\n')
    print(json.dumps(dict(version=args.version,status='verified',directory=str(out),source_files=len(source),private_files=len(personal),sqlite_snapshots=sum(e['sqlite_snapshot'] for entries in manifest['files'].values() for e in entries)),ensure_ascii=False),flush=True)

if __name__=='__main__':main()
