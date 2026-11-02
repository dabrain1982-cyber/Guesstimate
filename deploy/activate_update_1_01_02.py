"""Activate only the broadcast-sender copy fix; never resend a broadcast."""
from contextlib import closing
from datetime import datetime, timezone
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shlex
import shutil
import signal
import sqlite3
import subprocess
import tarfile
import time
import urllib.request

ROOT=Path('/srv/guesstimate')
VERSION='1.01.02'

def digest(path):
    with path.open('rb') as source:return hashlib.file_digest(source,'sha256').hexdigest()

def fetch(url):
    with urllib.request.urlopen(url,timeout=10) as response:return json.load(response)

def run(*args,**kw):return subprocess.run(args,check=True,**kw)

def backup_database(source,target):
    with closing(sqlite3.connect(source.resolve().as_uri()+'?mode=ro',uri=True)) as src:
        with closing(sqlite3.connect(target)) as out:
            src.backup(out)
            assert out.execute('PRAGMA quick_check').fetchall()==[('ok',)]
    target.chmod(0o600)

def hashes(db,owner_id):
    result={}
    for (name,) in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
        quoted='"'+name.replace('"','""')+'"'
        where=' WHERE user_id != ?' if name in ('inbox_deliveries','inbox_attention') else ''
        rows=list(db.execute('SELECT * FROM '+quoted+where,(owner_id,) if where else ()))
        result[name]=hashlib.sha256(repr(sorted([tuple(r) for r in rows],key=repr)).encode()).hexdigest()
    return result

def own_copy(database,module,username):
    with closing(sqlite3.connect(database)) as db:
        db.row_factory=sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        with db:
            db.execute('BEGIN IMMEDIATE')
            owner=db.execute('SELECT id FROM users WHERE username=?',(username,)).fetchone()
            assert owner,'Configured owner not found'
            before=hashes(db,owner['id'])
            result=module.add_latest_broadcast_sender_copy(db,owner['id'])
            assert hashes(db,owner['id'])==before,'Existing messages, other recipients or game data changed'
            result['status']=module.inbox_summary(db,owner['id'])
        return result

def atomic_copy(source,target):
    assert target.parent.resolve().is_relative_to(ROOT) and not target.is_symlink()
    target.parent.mkdir(parents=True,exist_ok=True)
    temp=target.with_name('.'+target.name+'.mail-update-tmp')
    assert not temp.exists()
    shutil.copyfile(source,temp)
    owner=target.stat() if target.exists() else ROOT.stat()
    temp.chmod(target.stat().st_mode&0o777 if target.exists() else 0o644)
    os.chown(temp,owner.st_uid,owner.st_gid)
    os.replace(temp,target)

def wait_version(version):
    for attempt in range(80):
        try:
            value=fetch('http://127.0.0.1:8765/health')
            assert value['release']==version
            return value
        except Exception:
            if attempt==79:raise
            time.sleep(.5)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--activate',action='store_true')
    args=parser.parse_args()
    assert os.geteuid()==0 and args.activate,'Bitte mit sudo und --activate ausfuehren.'
    os.umask(0o077)
    release=Path(__file__).resolve().parent
    assert release.parent==ROOT/'.version-store' and release.name.startswith(VERSION+'-')
    candidate=release/'candidate'
    manifest=json.loads((release/'deployment-manifest.json').read_text())
    github=json.loads((release/'github-proof.json').read_text())
    assert manifest['version']==VERSION
    assert not (release/'activation-result.json').exists(),'Existing activation receipt: inspect before retry.'
    assert digest(release/'deployment-manifest.json')==github['manifest_sha256']
    ref=fetch('https://api.github.com/repos/dabrain1982-cyber/Guesstimate/git/ref/tags/v1.01.02')
    assert ref['object']['type']=='commit' and ref['object']['sha']==github['commit']
    content=fetch('https://api.github.com/repos/dabrain1982-cyber/Guesstimate/contents/release-assets/1.01.02-deployment.json?ref=v1.01.02')
    raw=(release/'deployment-manifest.json').read_bytes()
    assert content['sha']==hashlib.sha1(b'blob '+str(len(raw)).encode()+bytes([0])+raw).hexdigest()
    for entry in manifest['files']:
        name=entry['path'];parts=Path(name).parts
        assert not Path(name).is_absolute() and '..' not in parts
        assert parts[0] not in {'runtime','config','.version-store','.git','instance'}
        assert name not in {'AGENTS.md','PROJEKTLOG.md'}
        assert digest(candidate/name)==entry['sha256'],name
        target=ROOT/name
        if entry['before_sha256'] is None:assert not target.exists(),name
        else:assert digest(target)==entry['before_sha256'],'Live source changed: '+name
    assert fetch('http://127.0.0.1:8765/health')['release']=='1.01.01'
    settings=subprocess.check_output(['systemctl','show','guesstimate.service','-p','Environment','--value'],text=True)
    env=os.environ.copy()
    env.update(dict(x.split('=',1) for x in shlex.split(settings)))
    database=Path(env['QUIZ_DATABASE'])
    assert database==ROOT/'runtime/quiz.sqlite3'
    username=env.get('QUIZ_OWNER_USERNAME','stormseed').strip().casefold()
    master=int(subprocess.check_output(['systemctl','show','guesstimate.service','-p','MainPID','--value'],text=True))
    command=subprocess.check_output(['systemctl','show','guesstimate.service','-p','ExecStart','--value'],text=True)
    assert master>1 and 'gunicorn' in command
    backup=release/('PRIVATE-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    backup.mkdir(mode=0o700)
    backup_database(database,backup/'before.sqlite3')
    with tarfile.open(backup/'configuration.tar.gz','x:gz') as archive:
        archive.add(ROOT/'config',arcname='config')
    with tarfile.open(backup/'configuration.tar.gz','r:gz') as archive:
        for member in archive.getmembers():
            if member.isfile():
                assert hashlib.sha256(archive.extractfile(member).read()).hexdigest()==digest(ROOT/member.name)
    saved=[]
    for entry in manifest['files']:
        original=ROOT/entry['path']
        if original.exists():
            target=backup/'code'/entry['path'];target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(original,target)
            assert digest(target)==entry['before_sha256']
            saved.append(entry['path'])
    (backup/'manifest.json').write_text(json.dumps(dict(files=manifest['files'],
        database_sha256=digest(backup/'before.sqlite3'),
        config_sha256=digest(backup/'configuration.tar.gz')),indent=2))
    backup_database(database,backup/'isolated.sqlite3')
    spec=importlib.util.spec_from_file_location('mail_sender_update',candidate/'inbox.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    simulated=own_copy(backup/'isolated.sqlite3',module,username)
    print('1/3 Sicherung und eigene Kontrollkopie an privater Datenkopie geprueft.',flush=True)
    changed=False
    try:
        changed=True
        for entry in manifest['files']:atomic_copy(candidate/entry['path'],ROOT/entry['path'])
        run('/usr/bin/python3','-B','deploy/validate_question_library.py',cwd=ROOT,env=env)
        run('/usr/bin/python3','-B','deploy/validate_release.py','--for-publication',cwd=ROOT,env=env)
        old_workers=set(subprocess.check_output(['ps','-o','pid=','--ppid',str(master)],text=True).split())
        os.kill(master,signal.SIGHUP)
        for attempt in range(120):
            current=set(subprocess.check_output(['ps','-o','pid=','--ppid',str(master)],text=True).split())
            if not old_workers&current:break
            time.sleep(.5)
        else:raise RuntimeError('Vorherige Webworker noch aktiv; keine Kontrollkopie live ergaenzt.')
        local=wait_version(VERSION)
        public=fetch('https://igroup.it-sauther.de/guesstimate/health')
        assert public['release']==VERSION
        print('2/3 Webdienst kontrolliert neu geladen, keine Serverneustart.',flush=True)
        result_copy=own_copy(database,module,username)
        for entry in manifest['files']:assert digest(ROOT/entry['path'])==entry['sha256']
        result=dict(time_utc=datetime.now(timezone.utc).isoformat(),version=VERSION,activated=True,
            public_health=public,private_backup=str(backup),private_backup_verified=True,
            sender_copy=result_copy,other_recipients_resent=False,new_messages_created=False,
            browser_verification_pending=True,copy_simulated=simulated)
        with (release/'activation-result.json').open('x') as output:json.dump(result,output,indent=2)
        (release/'activation-result.json').chmod(0o644)
        with (ROOT/'PROJEKTLOG.md').open('a') as output:
            output.write('\n## '+result['time_utc']+' V1.01.02 aktiviert, sichtbare Kontrolle noch offen\n')
            output.write('- Alle Spieler umfasst Absender; letzte eigene Kontrollkopie geprueft. Keine anderen Empfaenger erneut beliefert. Keine Spiel-/Kontodaten geaendert.\n')
        state_path=ROOT/'.version-store/server-state.json';state=json.loads(state_path.read_text())
        state.update(last_observed_release=VERSION,current_active=dict(version=VERSION,
            deployment=VERSION+'-server.1',activated=True,visible_production_verification=False))
        state_path.write_text(json.dumps(state,indent=2)+'\n')
        print('3/3 V1.01.02 aktiv. Eigene Kopie:',json.dumps(result_copy),flush=True)
    except BaseException:
        if changed:
            for name in saved:atomic_copy(backup/'code'/name,ROOT/name)
            os.kill(master,signal.SIGHUP)
            wait_version('1.01.01')
            print('Programmstand wiederhergestellt. Keine Datenbank zurueckgespielt.',flush=True)
        raise

if __name__=='__main__':main()
