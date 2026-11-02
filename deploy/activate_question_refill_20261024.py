#!/usr/bin/env python3
"""Append the reviewed 250-question refill and gracefully reload only Gunicorn.

Requires an administrator for read-only question_usage access and SIGHUP.
No account, result, answer or usage-history records are written by this tool.
"""
from __future__ import annotations

import argparse
import ast
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import sqlite3
import subprocess
import tempfile
import time
from typing import Any
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / 'deploy/question-refill-20261024'
RESULT = ROOT / 'deploy/question-refill-20261024-result.json'


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fingerprint_function(root: Path):
    tree = ast.parse((root / 'app.py').read_text(encoding='utf-8'))
    node = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'question_fingerprint')
    scope = {'Any': Any, 'hashlib': hashlib, 'json': json}
    exec(compile(ast.Module(body=[node], type_ignores=[]), 'question_fingerprint', 'exec'), scope)
    return scope['question_fingerprint']


def read_usage(root: Path) -> list[tuple[str, str | None]]:
    uri = (root / 'runtime/quiz.sqlite3').resolve().as_uri() + '?mode=ro'
    with closing(sqlite3.connect(uri, uri=True)) as database:
        database.execute('PRAGMA query_only=ON')
        return database.execute('SELECT question_id, content_hash FROM question_usage').fetchall()


def prepare(root: Path, payload: Path, usage: list[tuple[str, str | None]]) -> dict:
    plan = json.loads((payload / 'import-plan.json').read_text(encoding='utf-8'))
    manifest = json.loads((root / 'fragen/manifest.json').read_text(encoding='utf-8'))
    fingerprint = fingerprint_function(root)
    ids = {row[0] for row in usage}
    hashes = {row[1] for row in usage if row[1]}
    existing_ids = {}
    existing_hashes = set()
    for kind, definition in manifest['question_types'].items():
        for question in json.loads((root / 'fragen' / definition['directory'] / 'fragen.json').read_text(encoding='utf-8')):
            existing_ids[question['id']] = question
            existing_hashes.add(fingerprint(question, kind))
    replacements, before, additions = {}, {}, {}
    already_present = 0
    entries = plan['files']
    if len(entries) != 5 or {entry['question_type'] for entry in entries} != set(manifest['round_order']):
        raise RuntimeError('Das Paket enthält nicht genau die fünf aktiven Fragearten.')
    for entry in entries:
        kind = entry['question_type']
        relative = 'fragen/' + manifest['question_types'][kind]['directory'] + '/fragen.json'
        if entry['target'] != relative or entry['payload'] != kind + '.json':
            raise RuntimeError('Unerwarteter Paketpfad.')
        data = (payload / entry['payload']).read_bytes()
        if digest(data) != entry['sha256']:
            raise RuntimeError('Paket-Prüfsumme stimmt nicht: ' + kind)
        questions = json.loads(data)
        if len(questions) != 50 or entry['count'] != 50:
            raise RuntimeError('Es müssen je Frageart genau 50 neue Aufgaben vorliegen.')
        path = root / relative
        original = path.read_bytes()
        rows = json.loads(original)
        added = []
        for question in questions:
            qid = question['id']
            if question['question_type'] != kind:
                raise RuntimeError('Falsche Frageart bei ' + qid)
            if qid in existing_ids:
                if question != existing_ids[qid]:
                    raise RuntimeError('Bestehende ID mit anderem Inhalt: ' + qid)
                already_present += 1
                continue
            content_hash = fingerprint(question, kind)
            if qid in ids or content_hash in hashes:
                raise RuntimeError('Historisch bereits verwendete Frage: ' + qid)
            if content_hash in existing_hashes:
                raise RuntimeError('Inhaltsdublette: ' + qid)
            if question['source']['status'] != 'verified':
                raise RuntimeError('Nicht quellengeprüfte Frage: ' + qid)
            added.append(question)
            existing_ids[qid] = question
            existing_hashes.add(content_hash)
        additions[kind] = len(added)
        if added:
            before[relative] = original
            replacements[relative] = (json.dumps(rows + added, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    return {'before': before, 'replacements': replacements, 'added': additions, 'already_present': already_present}


def validate(root: Path, replacements: dict[str, bytes]) -> None:
    with tempfile.TemporaryDirectory(prefix='question-refill-check-') as directory:
        stage = Path(directory)
        shutil.copytree(root / 'fragen', stage / 'fragen', ignore=shutil.ignore_patterns('vormerkungen'))
        (stage / 'deploy').mkdir()
        shutil.copy2(root / 'deploy/validate_question_library.py', stage / 'deploy/validate_question_library.py')
        for name, data in replacements.items():
            (stage / name).write_bytes(data)
        subprocess.run([os.sys.executable, '-X', 'utf8', str(stage / 'deploy/validate_question_library.py')], check=True)


def replace_preserving_owner(path: Path, data: bytes) -> None:
    stat = path.stat()
    descriptor, name = tempfile.mkstemp(prefix='.' + path.name + '.refill-', dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chown(temporary, stat.st_uid, stat.st_gid)
        os.chmod(temporary, stat.st_mode & 0o777)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def service_pid() -> int:
    command = ['systemctl', 'show', 'guesstimate.service', '--value', '-p']
    state = subprocess.check_output(command + ['ActiveState'], text=True).strip()
    execution = subprocess.check_output(command + ['ExecStart'], text=True)
    working = subprocess.check_output(command + ['WorkingDirectory'], text=True).strip()
    if state != 'active' or 'gunicorn' not in execution or working != str(ROOT):
        raise RuntimeError('Der erwartete laufende Guesstimate-Dienst wurde nicht bestätigt.')
    pid = int(subprocess.check_output(command + ['MainPID'], text=True).strip())
    if pid <= 1:
        raise RuntimeError('Ungültiger Dienstprozess.')
    return pid


def health() -> dict:
    with urlopen('http://127.0.0.1:8765/health', timeout=5) as response:
        return json.load(response)


def activate() -> dict:
    if ROOT != Path('/srv/guesstimate') or os.geteuid() != 0:
        raise RuntimeError('Bitte als Administrator im Projekt /srv/guesstimate ausführen.')
    before_health = health()
    pid = service_pid()
    prepared = prepare(ROOT, PAYLOAD, read_usage(ROOT))
    validate(ROOT, prepared['replacements'])
    if not prepared['replacements']:
        return {'status': 'already_imported', 'added': prepared['added'], 'already_present': prepared['already_present'], 'health': before_health}
    # Re-read history and files after validation to detect intervening changes.
    fresh = prepare(ROOT, PAYLOAD, read_usage(ROOT))
    if prepared != fresh:
        raise RuntimeError('Fragenbestand oder Importplan inzwischen geändert; keine Aktivierung.')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = ROOT / 'runtime' / ('question-refill-backup-' + stamp)
    backup.mkdir(mode=0o700)
    for name, data in prepared['before'].items():
        destination = backup / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    (backup / 'before-health.json').write_text(json.dumps(before_health, indent=2), encoding='utf-8')
    written = []
    try:
        for name, data in prepared['replacements'].items():
            if (ROOT / name).read_bytes() != prepared['before'][name]:
                raise RuntimeError('Datei während Aktivierung geändert: ' + name)
            replace_preserving_owner(ROOT / name, data)
            written.append(name)
        subprocess.run([os.sys.executable, '-X', 'utf8', str(ROOT / 'deploy/validate_question_library.py')], check=True)
        # Gunicorn handles HUP by replacing its workers; no host/service reboot.
        if service_pid() != pid:
            raise RuntimeError('Dienstprozess inzwischen geändert.')
        os.kill(pid, signal.SIGHUP)
        samples = []
        for _ in range(40):
            time.sleep(1)
            try:
                current = health()
                if current.get('status') == 'ok' and not current['questions']['exhausted']:
                    samples.append(current)
                    if len(samples) >= 4:
                        break
                else:
                    samples.clear()
            except (OSError, ValueError):
                samples.clear()
        if len(samples) < 4:
            raise RuntimeError('Der laufende Dienst bestätigt den neuen Fragenvorrat nicht.')
    except Exception:
        for name in written:
            if (ROOT / name).read_bytes() == prepared['replacements'][name]:
                replace_preserving_owner(ROOT / name, prepared['before'][name])
            else:
                print('Zwischenzeitliche Änderung erhalten; Original liegt in ' + str(backup / name), file=os.sys.stderr)
        if written:
            os.kill(service_pid(), signal.SIGHUP)
        raise
    result = {'status': 'active', 'added': prepared['added'], 'already_present': prepared['already_present'], 'backup': str(backup), 'health_before': before_health, 'health_after': samples[-1], 'master_pid': pid, 'activation': 'Gunicorn SIGHUP; keine Dienst-/Serverneustarts', 'usage_access': 'SQLite mode=ro; keine Schreibabfragen'}
    with (ROOT / 'PROJEKTLOG.md').open('a', encoding='utf-8') as log:
        log.write('\n## Daily Quiz – 250er-Fragennachschub aktiviert (' + stamp + ')\n\n')
        log.write('- Nur die fünf vorbereiteten Fragepakete ergänzt: ' + json.dumps(prepared['added'], ensure_ascii=False) + '.\n')
        log.write('- Bestehende Einträge erhalten; IDs und Fingerabdrücke gegen question_usage rein lesend geprüft.\n')
        log.write('- Vollständige Bibliotheksprüfung vor und nach Übernahme bestanden; Originaldateien gesichert unter `' + str(backup) + '`.\n')
        log.write('- Gunicorn-Worker per SIGHUP neu geladen; vier aufeinanderfolgende Health-Antworten bestätigen neuen Vorrat. Kein Hostneustart, keine Leerstandsmail.\n')
        log.write('- Erreichbarkeit erneut prüfen, dann erst Conquest fortsetzen. Authentifizierte sichtbare Live-Abnahme steht noch aus.\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--activate', action='store_true', help='Geprüften Nachschub übernehmen und Gunicorn-Worker nachladen.')
    args = parser.parse_args()
    try:
        if args.activate:
            report = activate()
        else:
            prepared = prepare(ROOT, PAYLOAD, read_usage(ROOT))
            validate(ROOT, prepared['replacements'])
            report = {'status': 'checked_not_activated', 'added': prepared['added'], 'already_present': prepared['already_present']}
    except Exception as error:
        print('Nicht aktiviert: ' + str(error), file=os.sys.stderr)
        raise SystemExit(1)
    RESULT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
