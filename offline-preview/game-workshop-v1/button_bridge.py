"""Use the existing button editor and its original validator/store in this shell."""
import importlib.util
import sys
from pathlib import Path

BUTTON_DIR = Path(__file__).resolve().parents[1]/'button-workshop-v1'
if str(BUTTON_DIR) not in sys.path:sys.path.insert(0,str(BUTTON_DIR))
spec = importlib.util.spec_from_file_location('canonical_button_storage', BUTTON_DIR/'storage.py')
storage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(storage)


def public_files(root):
    files = {}
    for name in ('index.html','workshop.css','embedded.css','materials.css','workshop.js','renderer.js','sound.js',
                 'geometry.js','contour-editor.js','contour-editor.css','font-matching.js','fonts.css','library.css',
                 'source-renderer.js','source-check.html','unified-import.js','profile-capture.html','button-usage.js','button-usage.css'):
        files['/button-editor/'+name] = BUTTON_DIR/name
    files['/button-editor/'] = BUTTON_DIR/'index.html'
    files['/button-editor/media-renderer.js']=BUTTON_DIR/'media-renderer.js'
    from media_selection import FILES as MEDIA_FILES
    files.update(MEDIA_FILES)
    files['/button-editor/components.js'] = root/'offline-preview/comic-ui-v1/components.js'
    for path in (BUTTON_DIR/'assets').rglob('*'):
        if path.is_file() and path.suffix in ('.png','.webp','.ttf','.txt','.json','.wav','.mp3','.ogg','.md'):
            relative = path.relative_to(BUTTON_DIR).as_posix()
            files['/'+relative] = path
            files['/button-editor/'+relative] = path
    for name in ('components.js','comic-ui.css'):
        files['/shared/'+name] = root/'offline-preview/comic-ui-v1'/name
    return files
