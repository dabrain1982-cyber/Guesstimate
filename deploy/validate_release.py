"""Check version, bundled questions and patchnotes before publication."""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

def validate_release(*, for_publication=False):
    errors = []
    metadata = json.loads((ROOT / 'release.json').read_text(encoding='utf-8'))
    version = metadata['version']
    if not re.fullmatch(r'[1-9][0-9]*\.[0-9]{2}\.[0-9]{2,}', version):
        errors.append('Ungültige Versionsnummer.')
    def checked_path(relative):
        path = (ROOT / relative).resolve()
        if not path.is_relative_to(ROOT.resolve()):
            raise ValueError('Versionsdatei liegt außerhalb des Projekts.')
        return path
    refill = metadata['question_refill']
    manifest_path = checked_path(refill['manifest'])
    if hashlib.sha256(manifest_path.read_bytes()).hexdigest() != refill['sha256']:
        errors.append('Das gebundene Fragenmanifest stimmt nicht mit der Version überein.')
    report = json.loads(manifest_path.read_text(encoding='utf-8'))
    if report['release'] != version or report['total_added'] != refill['count'] or refill['reset_usage']:
        errors.append('Fragenpaket und Version widersprechen sich.')
    for item in report['files']:
        if hashlib.sha256(checked_path(item['path']).read_bytes()).hexdigest() != item['sha256']:
            errors.append('Fragenbestand weicht vom Versionsmanifest ab: ' + item['path'])
    notes = metadata['patchnotes']
    if notes.get('delivery') == 'chat_only':
        if notes.get('published') or notes.get('path') or notes.get('sha256'):
            errors.append('Patchnotes sollen nur im Chat vorbereitet werden.')
        if for_publication and notes.get('status') != 'prepared_for_owner':
            errors.append('Der Patchnote-Text für den Betreiber ist noch offen.')
    else:
        notes_path = checked_path(notes['path'])
        if notes_path.read_text(encoding='utf-8').splitlines()[0] != 'V ' + version:
            errors.append('Patchnotes gehören zu einer anderen Version.')
        if notes['sha256'] and hashlib.sha256(notes_path.read_bytes()).hexdigest() != notes['sha256']:
            errors.append('Patchnotes-Prüfsumme stimmt nicht.')
        if for_publication and (notes['status'] != 'ready' or not notes['sha256']):
            errors.append('Patchnotes sind noch in Vorbereitung.')
    if for_publication and metadata['status'] != 'ready':
        errors.append('Update ist noch in Vorbereitung; keine Veröffentlichung.')
    return errors

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--for-publication', action='store_true')
    args = parser.parse_args()
    errors = validate_release(for_publication=args.for_publication)
    print('\n'.join(errors) if errors else 'Versionsbindung geprüft.')
    raise SystemExit(bool(errors))
