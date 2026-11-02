"""Canonical public release metadata; operational activation state is logged separately."""
import json
from pathlib import Path
import re

RELEASE = json.loads((Path(__file__).parent / 'release.json').read_text(encoding='utf-8'))
PUBLIC_VERSION = RELEASE['version']
if not re.fullmatch(r'[1-9][0-9]*\.[0-9]{2}\.[0-9]{2,}', PUBLIC_VERSION):
    raise RuntimeError('Ungültige öffentliche Versionsnummer.')

def register_release_display(app):
    @app.after_request
    def display_release(response):
        version = app.config.get('PUBLIC_RELEASE')
        if version and response.mimetype == 'text/html' and not response.direct_passthrough:
            text = response.get_data(as_text=True)
            suffix = f' · V {version}'
            if '</title>' in text and suffix + '</title>' not in text:
                response.set_data(text.replace('</title>', suffix + '</title>', 1))
        return response
