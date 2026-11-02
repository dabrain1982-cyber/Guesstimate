"""Activate only the reviewed Guesstimate 1.1 server revision."""
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shlex
import shutil
import sqlite3
import subprocess
import sys
import time
import urllib.request

ROOT = Path('/srv/guesstimate')
STORE = ROOT / '.version-store'
BASE = STORE / '1.0-20261102T024248Z'
RELEASE = STORE / '1.1-20261101T180035Z'
CANDIDATE = RELEASE / 'server-candidate'
DROPIN = Path('/etc/systemd/system/guesstimate.service.d/codex-version-1.1.conf')
CLOCK_UNIT = Path('/etc/systemd/system/guesstimate-blackjack-clock.service')
MANIFEST_PATH = CANDIDATE / 'releases/server-1.1-manifest.json'
PROOF_PATH = RELEASE / 'github-proof.json'

def digest(path):
    with path.open('rb') as src:
        return hashlib.file_digest(src, 'sha256').hexdigest()

def execute(*args, check=True, **kwargs):
    return subprocess.run(args, check=check, **kwargs)

def fetch_json(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'Guesstimate-version-verification'})
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)

def rows_digest(database, columns=None):
    result = {}
    with closing(sqlite3.connect(database)) as db:
        tables = [row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
        if columns is not None:
            assert set(columns) <= set(tables), 'An existing table was removed'
            tables = list(columns)
        for name in tables:
            quote = '"' + name.replace('"', '""') + '"'
            actual = [row[1] for row in db.execute('PRAGMA table_info('+quote+')')]
            chosen = columns[name]['columns'] if columns is not None else actual
            assert set(chosen) <= set(actual), 'Existing columns were removed: '+name
            fields = ','.join('"'+x.replace('"', '""')+'"' for x in chosen)
            rows = list(db.execute('SELECT '+fields+' FROM '+quote))
            stamp = hashlib.sha256(repr(sorted(rows, key=repr)).encode()).hexdigest()
            result[name] = {'columns': chosen, 'count': len(rows), 'sha256': stamp}
    return result

def copy_database(source, target):
    with closing(sqlite3.connect(source.resolve().as_uri()+'?mode=ro', uri=True)) as src:
        with closing(sqlite3.connect(target)) as out:
            src.backup(out)
            assert out.execute('PRAGMA quick_check').fetchall() == [('ok',)]
    target.chmod(0o600)

def create_parents(path, owner):
    missing = []
    current = path
    while not current.exists():
        missing.append(current)
        current = current.parent
    assert current == ROOT or ROOT in current.parents
    for item in reversed(missing):
        item.mkdir(mode=0o755)
        item.chmod(0o755)
        os.chown(item, owner.st_uid, owner.st_gid)

def main():
    if os.geteuid() != 0 or sys.argv[1:] != ['--activate']:
        raise SystemExit('Bitte ausfuehren: sudo python3 /srv/guesstimate/deploy/activate_version_1_1.py --activate')
    os.umask(0o077)
    assert ROOT.resolve() == ROOT
    manifest = json.loads(MANIFEST_PATH.read_text())
    proof = json.loads(PROOF_PATH.read_text())
    assert manifest['deployment'] == '1.1-server.1'
    assert not DROPIN.exists() and not CLOCK_UNIT.exists(), 'Service revision already exists; inspect before retry'
    assert digest(BASE/'program-and-assets.tar.gz') == 'e80c6c709f395d9387e7a05f9521f9b281123c8c93932260896cb9a99ee18443'
    receipt = json.loads((BASE/'private-backup-receipt.json').read_text())
    private = Path(receipt['private_directory'])
    assert receipt['private_backup_verified'] and digest(private/'manifest.json') == receipt['manifest_sha256']
    saved_private = json.loads((private/'manifest.json').read_text())
    assert digest(private/saved_private['database']['path']) == saved_private['database']['sha256']
    assert digest(private/saved_private['config_archive']['path']) == saved_private['config_archive']['sha256']
    print('1/6 GitHub und Sicherungen pruefen ...', flush=True)
    for tag, expected in proof['tags'].items():
        ref = fetch_json('https://api.github.com/repos/dabrain1982-cyber/Guesstimate/git/ref/tags/'+tag)
        obj = ref['object']
        if obj['type'] == 'tag':
            obj = fetch_json('https://api.github.com/repos/dabrain1982-cyber/Guesstimate/git/tags/'+obj['sha'])['object']
        assert obj['type'] == 'commit' and obj['sha'] == expected, 'GitHub version differs: '+tag
    content = fetch_json('https://api.github.com/repos/dabrain1982-cyber/Guesstimate/contents/releases/server-1.1-manifest.json?ref=v1.1-server.1')
    raw = MANIFEST_PATH.read_bytes()
    assert content['sha'] == hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    baseline = json.loads((BASE/'manifest.json').read_text())
    old = {entry['path']: entry for entry in baseline['source_files']}
    for entry in baseline['source_files']:
        if entry['path'] != 'PROJEKTLOG.md':
            assert digest(ROOT/entry['path']) == entry['sha256'], 'Server file changed since 1.0 backup: '+entry['path']
    for entry in manifest['files']:
        name = entry['path']
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert Path(name).parts[0] not in {'.git', 'runtime', 'config', 'instance', '.version-store', 'offline-versions'}
        assert name not in {'AGENTS.md', 'PROJEKTLOG.md', '.gitignore', '.codex-preview.py'}
        assert digest(CANDIDATE/name) == entry['sha256'], 'Candidate changed: '+name
        if (ROOT/name).exists() and name not in old:
            assert digest(ROOT/name) == entry['sha256'], 'Unrecorded server file conflict: '+name
    environment = os.environ.copy()
    settings = subprocess.check_output(['systemctl','show','guesstimate.service','-p','Environment','--value'], text=True)
    for token in shlex.split(settings):
        key, value = token.split('=', 1)
        environment[key] = value
    assert environment['QUIZ_DATABASE'] == str(ROOT/'runtime/quiz.sqlite3')
    assert environment['QUIZ_SECRET_KEY_FILE'] == str(ROOT/'config/session.secret')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    checks = RELEASE/('PRIVATE-preactivation-'+stamp)
    checks.mkdir(mode=0o700)
    isolated = checks/'isolated.sqlite3'
    copy_database(Path(environment['QUIZ_DATABASE']), isolated)
    before = rows_digest(isolated)
    candidate_env = environment.copy()
    candidate_env.update(PYTHONPATH=str(CANDIDATE)+':'+str(ROOT/'.deps'),
                         QUIZ_DATABASE=str(isolated), QUIZ_MAIL_USER='', QUIZ_MAIL_TO='',
                         QUIZ_MAIL_PASSWORD_FILE='', QUIZ_LOCAL_DEVELOPMENT='0')
    print('2/6 Migration an getrennter Datenkopie pruefen ...', flush=True)
    execute('/usr/bin/python3','-c','import production_runtime; assert production_runtime.app.config["PUBLIC_RELEASE"]=="1.1"',cwd=CANDIDATE,env=candidate_env)
    assert rows_digest(isolated, before) == before, 'Migration changed existing data'
    execute('/usr/bin/python3','deploy/validate_question_library.py',cwd=CANDIDATE,env=candidate_env)
    assert manifest['targeted_server_checks_passed']
    # Prepare exact originals, including permissions, for a code-only rollback.
    rollback = checks/'original-files'
    rollback.mkdir(mode=0o700)
    existing = []
    for entry in manifest['files']:
        name = entry['path']
        path = ROOT/name
        if path.exists():
            dest = rollback/name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)
            existing.append(name)
    unit = subprocess.check_output(['systemctl','cat','guesstimate.service'],text=True)
    env_lines = '\n'.join(line for line in unit.splitlines() if line.startswith('Environment='))
    clock = '[Unit]\nDescription=Guesstimate Blackjack table clock\nAfter=guesstimate.service\nPartOf=guesstimate.service\n\n[Service]\nType=simple\nUser=guesstimate\nGroup=guesstimate\nWorkingDirectory=/srv/guesstimate\n'+env_lines+'\nExecStart=/usr/bin/python3 /srv/guesstimate/production_runtime.py\nRestart=on-failure\nRestartSec=5\nNoNewPrivileges=true\nPrivateTmp=true\nProtectSystem=strict\nProtectHome=true\nReadWritePaths=/srv/guesstimate/runtime\n\n[Install]\nWantedBy=multi-user.target\n'
    dropin = '[Unit]\nWants=guesstimate-blackjack-clock.service\n\n[Service]\nExecStart=\nExecStart=/usr/bin/python3 -m gunicorn --workers 2 --timeout 60 --bind 127.0.0.1:8765 production_runtime:app\n'
    stopped = False
    started = False
    try:
        print('3/6 Guesstimate kurz anhalten und letzte Datensicherung erstellen ...', flush=True)
        execute('systemctl','stop','guesstimate.service')
        stopped = True
        live_backup = checks/'before-live.sqlite3'
        copy_database(Path(environment['QUIZ_DATABASE']), live_backup)
        live_before = rows_digest(live_backup)
        print('4/6 Gepruefte 1.1-Dateien uebernehmen ...', flush=True)
        owner = ROOT.stat()
        for entry in manifest['files']:
            path = ROOT/entry['path']
            create_parents(path.parent, owner)
            shutil.copyfile(CANDIDATE/entry['path'], path)
            path.chmod(old.get(entry['path'], {}).get('mode', 0o644))
            os.chown(path, owner.st_uid, owner.st_gid)
            assert digest(path) == entry['sha256']
        live_env = environment.copy()
        live_env.update(PYTHONPATH=str(ROOT)+':'+str(ROOT/'.deps'),QUIZ_LOCAL_DEVELOPMENT='0')
        execute('/usr/bin/python3','-c','import production_runtime',cwd=ROOT,env=live_env)
        assert rows_digest(Path(environment['QUIZ_DATABASE']), live_before) == live_before, 'Live migration changed existing data'
        DROPIN.parent.mkdir(mode=0o755,exist_ok=True)
        DROPIN.parent.chmod(0o755)
        DROPIN.write_text(dropin)
        DROPIN.chmod(0o644)
        CLOCK_UNIT.write_text(clock)
        CLOCK_UNIT.chmod(0o644)
        execute('systemd-analyze','verify',str(CLOCK_UNIT))
        execute('systemctl','daemon-reload')
        print('5/6 Nur Guesstimate und seine Tischuhr starten ...', flush=True)
        execute('systemctl','enable','guesstimate-blackjack-clock.service')
        execute('systemctl','start','guesstimate.service')
        started = True
        for attempt in range(45):
            try:
                health = fetch_json('http://127.0.0.1:8765/health')
                assert health['release']=='1.1' and health['deployment']=='1.1-server.1'
                break
            except Exception:
                if attempt==44:raise
                time.sleep(1)
        execute('systemctl','is-active','--quiet','guesstimate-blackjack-clock.service')
        public = fetch_json('https://igroup.it-sauther.de/guesstimate/health')
        assert public['release']=='1.1' and public['deployment']=='1.1-server.1'
        result = {'time_utc':datetime.now(timezone.utc).isoformat(),'version':'1.1','deployment':'1.1-server.1',
                  'activated':True,'local_health_verified':True,'public_health_verified':True,
                  'existing_player_data_preserved':True,'clock_service_active':True,
                  'browser_verification_pending':True,'preactivation_backup':str(checks)}
        output=RELEASE/'activation-result.json'
        with output.open('x') as out:json.dump(result,out,indent=2);out.write('\n')
        output.chmod(0o644)
        print('6/6 Version 1.1 aktiv; lokale und oeffentliche Kennung geprueft. Browserpruefung folgt.',flush=True)
    except BaseException:
        if stopped:
            print('Aktivierung fehlgeschlagen. Gesicherten Programmstand wiederherstellen ...',flush=True)
            execute('systemctl','stop','guesstimate-blackjack-clock.service',check=False)
            execute('systemctl','stop','guesstimate.service',check=False)
            for name in existing:
                shutil.copy2(rollback/name,ROOT/name)
                os.chown(ROOT/name,ROOT.stat().st_uid,ROOT.stat().st_gid)
            # Prior to accepting traffic, a failed migration can safely be undone.
            if not started and (checks/'before-live.sqlite3').exists():
                with closing(sqlite3.connect(checks/'before-live.sqlite3')) as source:
                    with closing(sqlite3.connect(environment['QUIZ_DATABASE'])) as target:
                        source.backup(target)
            if DROPIN.exists():DROPIN.unlink()
            if CLOCK_UNIT.exists():
                execute('systemctl','disable','guesstimate-blackjack-clock.service',check=False)
                CLOCK_UNIT.unlink()
            execute('systemctl','daemon-reload')
            execute('systemctl','start','guesstimate.service')
        raise

if __name__ == '__main__':
    main()
