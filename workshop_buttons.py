"""Opt-in local game integration of the canonical workshop button renderer."""
from pathlib import Path
import sys


def register_workshop_buttons(app):
    if not (app.config.get('LOCAL_DEVELOPMENT') or app.config.get('BUTTON_RUNTIME_ENABLED')):
        return
    from flask import abort, jsonify, request, send_file, url_for
    from jinja2 import BaseLoader
    root = Path(__file__).resolve().parent
    workshop = root/'offline-preview/game-workshop-v1'
    if str(workshop) not in sys.path: sys.path.append(str(workshop))
    from button_bridge import public_files, storage
    from source_buttons import SourceButtons
    from button_usage import ButtonUsage
    from media_selection import matched_css
    directory = Path(app.config.get('BUTTON_DESIGN_LIBRARY', root/'design-library'))
    recipes = storage.RecipeStore(Path(app.config.get('BUTTON_RECIPE_LIBRARY', directory/'recipes/button-workshop')))
    usage = ButtonUsage(directory, recipes, SourceButtons())
    app.extensions['workshop_buttons'] = usage
    files = public_files(root)
    files['/button-editor/game-runtime.js'] = root/'offline-preview/button-workshop-v1/game-runtime.js'
    files['/button-editor/game-runtime.css'] = root/'offline-preview/button-workshop-v1/game-runtime.css'
    files['/shared/comic-button.css'] = root/'static/comic-button.css'

    if not app.config.get('LOCAL_DEVELOPMENT'):
        # The public game gets the same component, without editor screens.
        hidden = {'index.html', 'workshop.js', 'contour-editor.js', 'profile-capture.html', 'source-check.html'}
        files = {name: path for name, path in files.items()
                 if name != '/button-editor/' and name.rsplit('/', 1)[-1] not in hidden}

    @app.after_request
    def public_asset_prefix(response):
        endpoint = request.endpoint or ''
        prefix = request.script_root.rstrip('/')
        if prefix and endpoint.startswith('workshop_buttons_') and response.mimetype in (
                'application/json', 'application/javascript', 'text/javascript', 'text/css'):
            response.direct_passthrough = False
            text = response.get_data(as_text=True)
            for folder in ('assets', 'media-assets', 'button-editor', 'shared'):
                text = text.replace('"/'+folder+'/', '"'+prefix+'/'+folder+'/')
                text = text.replace("'/"+folder+'/', "'"+prefix+'/'+folder+'/')
                text = text.replace('url(/'+folder+'/', 'url('+prefix+'/'+folder+'/')
            response.set_data(text)
        return response

    class DesignLoader(BaseLoader):
        def __init__(self, wrapped): self.wrapped = wrapped
        def get_source(self, environment, name):
            source, filename, current = self.wrapped.get_source(environment, name)
            return usage.instrument(name, source), filename, current
        def list_templates(self): return self.wrapped.list_templates()

    app.jinja_loader = DesignLoader(app.jinja_loader)

    @app.get('/_local/button-models', endpoint='workshop_buttons_state')
    def state():
        response = jsonify(usage.runtime())
        response.headers['Cache-Control'] = 'no-store'
        return response

    def asset(path):
        if path == '/button-editor/matched-media.css':
            return app.response_class(matched_css(), mimetype='text/css', headers={'Cache-Control':'no-store'})
        file = files.get(path)
        if file is None or not file.is_file(): abort(404)
        response = send_file(file)
        response.headers['Cache-Control'] = 'no-store'
        return response

    @app.get('/button-editor/<path:name>', endpoint='workshop_buttons_assets')
    def editor_asset(name): return asset('/button-editor/'+name)
    @app.get('/assets/<path:name>', endpoint='workshop_buttons_media')
    def media_asset(name): return asset('/assets/'+name)
    @app.get('/media-assets/<path:name>', endpoint='workshop_buttons_fonts')
    def font_asset(name): return asset('/media-assets/'+name)
    @app.get('/shared/<path:name>', endpoint='workshop_buttons_shared')
    def shared_asset(name): return asset('/shared/'+name)

    @app.after_request
    def install_runtime(response):
        if response.mimetype == 'text/html' and not response.direct_passthrough and not (request.endpoint or '').startswith('workshop_buttons_'):
            html = response.get_data(as_text=True)
            if '</body>' in html:
                script = '<script type="module" src="'+url_for('workshop_buttons_assets', name='game-runtime.js')+'"></script>'
                response.set_data(html.replace('</body>', script+'</body>', 1))
        return response

    def readonly_runtime_request():
        endpoint = request.endpoint or ''
        if endpoint.startswith('workshop_buttons_'):
            return app.view_functions[endpoint](**(request.view_args or {}))
    # Design assets/state do not record logins or touch a game database.
    app.before_request_funcs.setdefault(None, []).insert(0, readonly_runtime_request)
