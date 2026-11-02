"""Inert, neutral game screens built from the original templates and styles."""
from datetime import date
from hashlib import sha256
from html import escape
import re

from jinja2 import BaseLoader, UndefinedError
from source_windows import InertMarkup, SourceWindows, definitions


class ButtonContext:
    def __init__(self, usage):
        self.usage = usage
        self.sources = usage.sources
        self.examples = SourceWindows(self.sources, self.sources.root, definitions_list=[])

    def render(self, identifier):
        record = self.sources.records.get(identifier)
        if record is None or not self.usage.models[self.usage.by_source[identifier]]['supported']:
            raise ValueError('Für diese Einsatzstelle ist noch keine vollständige Spielansicht verfügbar.')
        source = record['snapshot']['source']
        path = source['path']
        if sha256((self.sources.root/path).read_bytes()).hexdigest() != record['snapshot']['source_sha256']:
            raise ValueError('Diese Spielseite wurde geändert. Bitte die Werkstatt neu starten.')
        markup = record['markup']
        template = record['template']
        if template.startswith('_') or template == 'base.html':
            template = {'_lobby_room.html':'party_lobby.html', '_lobby_overview.html':'party_index.html'}.get(template, 'home.html')
            if record['template'] == '_leaderboard.html' and not any('variant-a-leaderboard' in a[1] for a in record['ancestors']): template = 'result.html'
        wrapped = self.examples.env.loader

        class TargetLoader(BaseLoader):
            def get_source(self, environment, name):
                text, filename, current = wrapped.get_source(environment, name)
                if 'templates/'+name == path:
                    positions = [m.start() for m in re.finditer(re.escape(markup), text)]
                    exact = [p for p in positions if text.count('\n', 0, p)+1 == source['line']]
                    candidates = exact if len(exact) == 1 else positions
                    if len(candidates) != 1:
                        raise ValueError('Die Einsatzstelle ist in dieser Spielseite nicht eindeutig.')
                    position = candidates[0]
                    marked = re.sub(r'^<(button|a)\b', lambda m: m[0]+' data-usage-target="true"', markup, count=1)
                    text = text[:position]+marked+text[position+len(markup):]
                return text, filename, current

        environment = self.examples.env.overlay(loader=TargetLoader())
        def url_for(endpoint, **args):
            if endpoint == 'static': return '/shared/'+args['filename']
            if endpoint == 'conquest_table_asset':
                return '/button-editor/materials.css' if args['filename'] == 'button-materials.css' else '/conquest-source/'+args['filename']
            return '#'
        environment.globals = {**self.examples.env.globals, 'url_for':url_for}
        contexts = [self.examples.context(dict(template=template, values=patch))
                    for patch in [{}]+[d.get('values', {}) for d in definitions() if d['template'] == template]]
        if record['template'] in ('_lobby_overview.html','_lobby_room.html','conquest_lobby.html'):
            from source_lobbies import SourceLobbies, definitions as lobby_definitions
            if not hasattr(self, 'lobbies'): self.lobbies = SourceLobbies(self.sources, self.sources.root)
            contexts += [self.lobbies.context(d) for d in lobby_definitions() if d['template'] == template]
        today = date.today().isoformat()
        fixed = dict(round_available=True, show_catchup_prompt=False, active_round_date=today, today_iso_value=today,
                     attempt=dict(status='completed', score=250), answer_review=[], has_next_catchup='nächsten tag' in record['label'])
        if template == 'home.html':
            fixed.update(attempt=dict(status='completed', score=250) if record['label'].startswith('heutiges') else None,
                         show_catchup_prompt=any(a[0] == 'dialog' for a in record['ancestors']))
        if template in ('question.html', 'party_question.html'):
            if 'data-feedback' not in markup and 'Endergebnis' not in record['label'] and not any('feedback-panel' in a[1] for a in record['ancestors']): fixed['feedback'] = None
            fixed['party_completed'] = 'Endergebnis' in record['label']
        if path == 'templates/base.html' and record['label'].startswith('spielregeln'): fixed['g'] = dict(user=None)
        if template == 'conquest_lobby.html':
            fixed['can_develop'] = True
            contexts += [{**values, 'is_active':False} for values in contexts]
        page = None
        for values in contexts:
            values.update(record.get('sample_values', {}))
            values.update(fixed)
            if template == 'profile.html' and record['label'] == 'ausgerüstet': values['cosmetics']['phrase_id'] = 'example'
            if template == 'shop.html':
                for key in ('avatars','plaques','backgrounds','phrases'):
                    if record['label'].startswith('gehört dir'): values['owned_'+key] = [item['id'] for item in values[key]]
                    if record['label'] == 'preis folgt': values[key] = [{**item,'price':None} for item in values[key]]
            try: candidate = environment.get_template(template).render(**values)
            except (TypeError, ValueError, KeyError, UndefinedError): continue
            if 'data-usage-target="true"' in candidate:
                page = candidate
                break
        if page is None:
            raise ValueError('Dieser Spielzustand lässt sich noch nicht als vollständige Vorschau zeigen.')
        parser = InertMarkup(page)
        page = ''.join(parser.parts)
        head = '<link rel="stylesheet" href="/button-context.css">'
        script = '<script src="/button-context.js" defer></script>'
        return '<!doctype html>'+page.replace('</head>', head+'</head>', 1).replace('</body>', script+'</body>', 1)


def http_context(handler, usage, path):
    if not path.startswith('/api/button-usage/') or not path.endswith('/context'):
        return False
    identifier = path.removeprefix('/api/button-usage/').removesuffix('/context')
    try:
        if not hasattr(usage, 'context_view'): usage.context_view = ButtonContext(usage)
        page = usage.context_view.render(identifier)
        status = 200
    except (ValueError, OSError) as error:
        page = '<!doctype html><html lang="de"><meta charset="utf-8"><body><p>'+escape(str(error))+'</p><script src="/button-context.js" defer></script></body></html>'
        status = 400
    raw = page.encode('utf-8')
    handler.send_response(status)
    handler.send_header('Content-Type', 'text/html; charset=utf-8')
    handler.send_header('Content-Length', str(len(raw)))
    handler.send_header('Content-Security-Policy', "default-src 'none'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; script-src 'self'; connect-src 'none'; form-action 'none'; frame-ancestors 'self'")
    handler.end_headers()
    handler.wfile.write(raw)
    return True
