"""Controlled 1.01.01 activation; private data stay on the project server."""
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
import sqlite3
import subprocess
import tarfile
import time
import urllib.request

ROOT=Path('/srv/guesstimate')
VERSION='1.01.01'
SERVICES=('guesstimate-blackjack-clock.service','guesstimate.service')

def digest(path):
    with Path(path).open('rb') as source:
        return hashlib.file_digest(source,'sha256').hexdigest()

def run(*args,**kwargs):
    return subprocess.run(args,check=True,**kwargs)

def health(url):
    with urllib.request.urlopen(url,timeout=10) as response:
        return json.load(response)

def copy_db(source,target):
    with closing(sqlite3.connect(Path(source).resolve().as_uri()+'?mode=ro',uri=True)) as src:
        with closing(sqlite3.connect(target)) as dst:
            src.backup(dst)
            assert dst.execute('PRAGMA quick_check').fetchall()==[('ok',)]
    target.chmod(0o600)

def row_hashes(path,existing=None):
    with closing(sqlite3.connect(path)) as db:
        tables=[r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
        result={}
        if existing:assert set(existing)<=set(tables),'Existing table removed'
        for table in existing or tables:
            quoted='"'+table.replace('"','""')+'"'
            columns=[r[1] for r in db.execute('PRAGMA table_info('+quoted+')')]
            fields=existing[table]['columns'] if existing else columns
            assert set(fields)<=set(columns),'Existing column removed'
            query=','.join('"'+x.replace('"','""')+'"' for x in fields)
            rows=list(db.execute('SELECT '+query+' FROM '+quoted))
            result[table]=dict(columns=fields,count=len(rows),
                sha256=hashlib.sha256(repr(sorted(rows,key=repr)).encode()).hexdigest())
        return result

def require_empty_table(database):
    with closing(sqlite3.connect(Path(database).resolve().as_uri()+'?mode=ro',uri=True)) as db:
        seats=db.execute('SELECT COUNT(*) FROM blackjack_seats').fetchone()[0]
        state=json.loads(db.execute('SELECT state_json FROM blackjack_game WHERE id=1').fetchone()[0])
        assert seats==0 and not state['bets'] and state['phase'] in ('betting','result'), \
            'Der Blackjacktisch ist belegt oder eine Hand laeuft. Niemanden automatisch entfernen.'

def replace_file(source,target):
    assert target.is_relative_to(ROOT) and not target.is_symlink()
    assert target.parent.resolve().is_relative_to(ROOT)
    owner=ROOT.stat()
    missing=[]
    parent=target.parent
    while not parent.exists():
        missing.append(parent);parent=parent.parent
    for parent in reversed(missing):
        parent.mkdir(mode=0o755)
        os.chown(parent,owner.st_uid,owner.st_gid)
    temp=target.with_name('.'+target.name+'.update-tmp')
    assert not temp.exists()
    shutil.copyfile(source,temp)
    os.chmod(temp,target.stat().st_mode&0o777 if target.exists() else 0o644)
    os.chown(temp,owner.st_uid,owner.st_gid)
    os.replace(temp,target)

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def check_questions(candidate,database):
    module=load_module('refill_check',candidate/'deploy/activate_question_refill_20261024.py')
    with closing(sqlite3.connect(Path(database).resolve().as_uri()+'?mode=ro',uri=True)) as db:
        usage=db.execute('SELECT question_id,content_hash FROM question_usage').fetchall()
    prepared=module.prepare(ROOT,candidate/'deploy/question-refill-20261024',usage)
    assert sum(prepared['added'].values())==250 and not prepared['already_present'], \
        'Questions differ from the reviewed unused refill.'
    for name,data in prepared['replacements'].items():
        assert json.loads(data)==json.loads((candidate/name).read_bytes()),name
    return dict(added=prepared['added'],usage_count=len(usage),history_reset=False)

def runtime_env(original,database,candidate):
    env=original.copy()
    env.update(QUIZ_DATABASE=str(database),PYTHONPATH=str(candidate)+':'+str(ROOT/'.deps'),
        QUIZ_MAIL_USER='',QUIZ_MAIL_TO='',QUIZ_MAIL_PASSWORD_FILE='',
        QUIZ_LOCAL_DEVELOPMENT='0',QUIZ_OFFLINE_VERSION='',PYTHONDONTWRITEBYTECODE='1')
    return env

def wait_health(version,deployment):
    for attempt in range(40):
        try:
            result=health('http://127.0.0.1:8765/health')
            assert result['release']==version and result['deployment']==deployment
            return result
        except Exception:
            if attempt==39:raise
            time.sleep(.5)

def recover(candidate,backup):
    run('systemctl','stop',*SERVICES)
    saved=json.loads((backup/'code-manifest.json').read_text())
    for entry in saved:
        if entry['path'] in {'AGENTS.md','PROJEKTLOG.md'}:continue
        assert digest(backup/'code'/entry['path'])==entry['sha256'],'Damaged rollback source: '+entry['path']
        replace_file(backup/'code'/entry['path'],ROOT/entry['path'])
    # Retain the canonical reader and every live ledger entry. Blackjack is
    # paused in this recovery build; other account views/shop remain accurate.
    for name in ['account_wallet.py','leaderboard_views.py','nerd_mode.py','dice_table.py']:
        replace_file(candidate/name,ROOT/name)
    for entry in json.loads((candidate/'release-assets/1.01.01-question-import.json').read_text())['files']:
        replace_file(candidate/entry['path'],ROOT/entry['path'])
    replace_file(candidate/'deploy/wallet_recovery_runtime.py',ROOT/'production_runtime.py')
    run('systemctl','start','guesstimate.service')
    local=wait_health('1.1','1.1-wallet-recovery.1')
    public=health('https://igroup.it-sauther.de/guesstimate/health')
    assert public['release']=='1.1' and public['deployment']=='1.1-wallet-recovery.1'
    state_path=ROOT/'.version-store/server-state.json'
    state=json.loads(state_path.read_text())
    state.update(last_observed_release='1.1',current_active=dict(version='1.1',
        deployment='1.1-wallet-recovery.1',blackjack_paused=True,visible_production_verification=False))
    state_path.write_text(json.dumps(state,indent=2)+'\n')
    with (ROOT/'PROJEKTLOG.md').open('a') as output:
        output.write('\n## '+datetime.now(timezone.utc).isoformat()+' Kontovertraegliche Rueckkehr\n')
        output.write('-1.1-wallet-recovery.1 aktiv, Blackjack pausiert. Aktuelle Kontobuchungen und Fragen erhalten; keine Datenbank zurueckgespielt.\n')
    return dict(status='recovered_with_wallet_reader',local_health=local,public_health=public,
        database_restored=False,blackjack_paused=True,private_backup=str(backup))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--activate',action='store_true')
    parser.add_argument('--recover',type=Path)
    args=parser.parse_args()
    assert os.geteuid()==0,'Administratorrechte benoetigt.'
    os.umask(0o077)
    release=args.release.resolve()
    assert release.parent==ROOT/'.version-store' and release.name.startswith(VERSION+'-')
    candidate=release/'candidate'
    manifest=json.loads((release/'deployment-manifest.json').read_text())
    assert manifest['version']==VERSION and manifest['base_tag']=='v1.1-server.1'
    for entry in manifest['files']:
        name=entry['path'];parts=Path(name).parts
        assert not Path(name).is_absolute() and '..' not in parts
        assert parts[0] not in {'.git','runtime','config','instance','.version-store','offline-versions'}
        assert name not in {'AGENTS.md','PROJEKTLOG.md'}
        assert digest(candidate/name)==entry['sha256'],name
    if args.recover:
        backup=args.recover.resolve()
        assert backup.parent==release and backup.name.startswith('PRIVATE-')
        result=recover(candidate,backup)
        (release/'recovery-result.json').write_text(json.dumps(result,indent=2)+'\n')
        print('Kontovertraegliche Rueckkehr geprueft; Blackjack pausiert. Keine Datenbank zurueckgespielt.')
        return
    result_path=release/'activation-result.json'
    assert not result_path.exists(),'Aktivierungsbeleg existiert; vor Wiederholung Zustand pruefen.'
    assert args.activate,'--activate benoetigt.'
    baseline=json.loads((release/'baseline-manifest.json').read_text())
    assert digest(release/'baseline-manifest.json')==manifest['base_manifest_sha256']
    baseline_names={entry['path'] for entry in baseline['files']}
    changed_names={entry['path'] for entry in manifest['files']}
    for entry in baseline['files']:
        if entry['path']!='PROJEKTLOG.md':
            assert digest(ROOT/entry['path'])==entry['sha256'],'Live file changed: '+entry['path']
            if entry['path'] not in changed_names:
                assert digest(candidate/entry['path'])==entry['sha256'],'Candidate baseline changed: '+entry['path']
    for entry in manifest['files']:
        target=ROOT/entry['path']
        if target.exists() and entry['path'] not in baseline_names:
            assert digest(target)==entry['sha256'],'New-file collision: '+entry['path']
    github=json.loads((release/'github-proof.json').read_text())
    commit=health('https://api.github.com/repos/dabrain1982-cyber/Guesstimate/git/ref/tags/v1.01.01')
    assert commit['object']['sha']==github['commit'] and commit['object']['type']=='commit'
    assert digest(release/'deployment-manifest.json')==github['manifest_sha256']
    content=health('https://api.github.com/repos/dabrain1982-cyber/Guesstimate/contents/release-assets/1.01.01-deployment.json?ref=v1.01.01')
    raw=(release/'deployment-manifest.json').read_bytes()
    assert content['sha']==hashlib.sha1(b'blob '+str(len(raw)).encode()+bytes([0])+raw).hexdigest()
    print('1/6 Quellen, GitHub und Ausgangsstand geprueft.',flush=True)
    env=os.environ.copy()
    settings=subprocess.check_output(['systemctl','show','guesstimate.service','-p','Environment','--value'],text=True)
    env.update(dict(token.split('=',1) for token in shlex.split(settings)))
    assert env['QUIZ_DATABASE']==str(ROOT/'runtime/quiz.sqlite3')
    database=Path(env['QUIZ_DATABASE'])
    require_empty_table(database)
    assert health('http://127.0.0.1:8765/health')['release']=='1.1'
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    backup=release/('PRIVATE-'+stamp)
    backup.mkdir(mode=0o700)
    (backup/'environment.json').write_text(json.dumps(env,indent=2))
    with tarfile.open(backup/'configuration.tar.gz','x:gz') as archive:
        for path in [ROOT/'config',Path('/etc/systemd/system/guesstimate.service'),
            Path('/etc/systemd/system/guesstimate.service.d'),Path('/etc/systemd/system/guesstimate-blackjack-clock.service')]:
            archive.add(path,arcname=str(path).lstrip('/'))
    with tarfile.open(backup/'configuration.tar.gz','r:gz') as archive:
        config_files=[]
        for member in archive.getmembers():
            if member.isfile():
                data=archive.extractfile(member).read()
                original=Path('/')/member.name
                assert hashlib.sha256(data).hexdigest()==digest(original),'Config backup mismatch'
                config_files.append(dict(path=member.name,sha256=hashlib.sha256(data).hexdigest()))
    code=[]
    for name in sorted(baseline_names|{'AGENTS.md','PROJEKTLOG.md'}):
        path=ROOT/name
        target=backup/'code'/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(path,target)
        assert digest(target)==digest(path)
        code.append(dict(path=name,sha256=digest(target)))
    (backup/'code-manifest.json').write_text(json.dumps(code,indent=2))
    copy_db(database,backup/'isolated.sqlite3')
    receipt=dict(code_manifest_sha256=digest(backup/'code-manifest.json'),
        configuration_sha256=digest(backup/'configuration.tar.gz'),configuration_files=config_files,
        isolated_database_sha256=digest(backup/'isolated.sqlite3'),sqlite_quick_check='ok',
        source_files_verified=len(code),private_data_stay_on_server=True)
    (backup/'backup-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    before=row_hashes(backup/'isolated.sqlite3')
    questions=check_questions(candidate,backup/'isolated.sqlite3')
    isolated_env=runtime_env(env,backup/'isolated.sqlite3',candidate)
    run('/usr/bin/python3','-B','-c',
        'import production_runtime as p; assert p.app.config["PUBLIC_RELEASE"]=="1.01.01";'
        'assert p.app.config["BLACKJACK_CURRENCY"]=="account-ikuehe";'
        'assert p.app.config["BLACKJACK_FIXED_STAKE"]==500',cwd=candidate,env=isolated_env)
    assert row_hashes(backup/'isolated.sqlite3',before)==before,'Migration changed existing records.'
    run('/usr/bin/python3','-B','deploy/validate_question_library.py',cwd=candidate,env=isolated_env)
    run('/usr/bin/python3','-B','deploy/validate_release.py','--for-publication',cwd=candidate,env=isolated_env)
    print('2/6 Private Sicherung und unveraenderte vorhandene Daten an Kopie geprueft.',flush=True)
    stopped=False
    files_changed=False
    try:
        stopped=True
        run('systemctl','stop',*SERVICES)
        require_empty_table(database)
        copy_db(database,backup/'before-live.sqlite3')
        receipt['before_live_database_sha256']=digest(backup/'before-live.sqlite3')
        (backup/'backup-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
        live_before=row_hashes(backup/'before-live.sqlite3')
        questions=check_questions(candidate,backup/'before-live.sqlite3')
        files_changed=True
        for entry in manifest['files']:
            replace_file(candidate/entry['path'],ROOT/entry['path'])
            assert digest(ROOT/entry['path'])==entry['sha256']
        live_env=runtime_env(env,database,ROOT)
        run('/usr/bin/python3','-B','-c','import production_runtime',cwd=ROOT,env=live_env)
        assert row_hashes(database,live_before)==live_before,'Existing live records changed during migration.'
        print('3/6 Version uebernommen, vorhandene Daten erhalten.',flush=True)
        run('systemctl','start','guesstimate.service')
        run('systemctl','start','guesstimate-blackjack-clock.service')
        local=wait_health(VERSION,VERSION+'-server.1')
        run('systemctl','is-active','--quiet',*SERVICES)
        public=health('https://igroup.it-sauther.de/guesstimate/health')
        assert public['release']==VERSION and public['deployment']==VERSION+'-server.1'
        for entry in manifest['files']:
            assert digest(ROOT/entry['path'])==entry['sha256']
        result=dict(time_utc=datetime.now(timezone.utc).isoformat(),version=VERSION,
            deployment=VERSION+'-server.1',activated=True,local_health=local,public_health=public,
            existing_data_preserved=True,private_backup=str(backup),private_backup_verified=True,questions=questions,
            database_restored=False,browser_verification_pending=True,human_multiplayer_test=False,
            patchnotes_published=False,mail_sent=False)
        with result_path.open('x') as output:json.dump(result,output,indent=2);output.write('\n')
        result_path.chmod(0o644)
        state_path=ROOT/'.version-store/server-state.json'
        state=json.loads(state_path.read_text())
        state.update(last_observed_release=VERSION,current_active=dict(version=VERSION,
            deployment=VERSION+'-server.1',activated=True,visible_production_verification=False),
            time_utc=result['time_utc'])
        state_path.write_text(json.dumps(state,indent=2)+'\n')
        with (ROOT/'.version-store/events.jsonl').open('a') as output:
            output.write(json.dumps(dict(time_utc=result['time_utc'],version=VERSION,
                event='activated_browser_pending',private_backup=str(backup),patchnotes_published=False))+'\n')
        with (ROOT/'PROJEKTLOG.md').open('a') as output:
            output.write('\n## '+result['time_utc']+' V1.01.01 aktiviert, Browserpruefung noch offen\n')
            output.write('- Private Server-Sicherung: '+str(backup)+'. Daten/Migration und Quellenhashes geprueft.250 Fragen ergaenzt; keine Nutzung zurueckgesetzt. Kein Mailversand; Patchnotes nur im Chat fuer Betreiber.\n')
        print('6/6 V1.01.01 aktiv. Oeffentliche Browserpruefung noch offen; keine Patchnotes gesendet.',flush=True)
    except BaseException as error:
        if stopped and not files_changed:
            run('systemctl','start','guesstimate.service')
            run('systemctl','start','guesstimate-blackjack-clock.service')
            print('Vor Dateiumschaltung abgebrochen; bisheriger Betrieb unveraendert gestartet.',flush=True)
        if stopped and files_changed:
            print('Aktivierung fehlgeschlagen; Kontobuchungen bleiben erhalten.',flush=True)
            try:
                result=recover(candidate,backup)
                result['activation_error']=str(error)
                (release/'recovery-result.json').write_text(json.dumps(result,indent=2)+'\n')
                print('Sichere1.1-Rueckkehr mit Kontoleser aktiv; Blackjack pausiert.',flush=True)
            except BaseException:
                run('systemctl','stop',*SERVICES)
                print('Dienste geschlossen gehalten. Keine alte Datenbank zurueckgespielt.',flush=True)
                raise
        raise

if __name__=='__main__':main()
