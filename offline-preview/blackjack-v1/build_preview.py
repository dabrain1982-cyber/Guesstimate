"""Rebuild the local Blackjack preview from its saved button and shared renderer."""
from argparse import ArgumentParser
import base64
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import struct
import zlib
from jinja2 import Environment, FileSystemLoader


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BUTTON = ROOT / 'offline-preview/button-workshop-v1'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def woff_bytes(raw):
    """Lossless font-container packaging, https://www.w3.org/TR/WOFF/."""
    count = struct.unpack_from('>H', raw, 4)[0]
    tables = [struct.unpack_from('>4sIII', raw, 12 + 16*i) for i in range(count)]
    offset = 44 + 20*count
    entries, chunks = {}, []
    for tag, checksum, start, length in sorted(tables, key=lambda row:row[2]):
        original = raw[start:start+length]
        packed = zlib.compress(original)
        if len(packed) >= length:
            packed = original
        assert (zlib.decompress(packed) if len(packed) < length else packed) == original
        entries[tag] = struct.pack('>4sIIII', tag, offset, len(packed), length, checksum)
        block = packed + b'\0' * (-len(packed) % 4)
        chunks.append(block); offset += len(block)
    sfnt_size = 12 + 16*count + sum((row[3]+3)&~3 for row in tables)
    header = struct.pack('>4sIIHHIHHIIIII', b'wOFF', struct.unpack_from('>I',raw)[0], offset, count, 0, sfnt_size, 1, 0, 0, 0, 0, 0, 0)
    return header + b''.join(entries[row[0]] for row in tables) + b''.join(chunks)


def module(path, imports, exports):
    text = path.read_text(encoding='utf-8')
    text = re.sub(r'^import .*?;\s*$', '', text, flags=re.M)
    text = re.sub(r'^export \{[^}]*\};\s*$', '', text, flags=re.M)
    text = re.sub(r'\bexport (?=(?:const|function|class)\b)', '', text)
    return imports + '\n' + text + '\nreturn {' + ','.join(exports) + '};\n})();\n'


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--recipe', required=True)
    parser.add_argument('--render-script', type=Path, required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[a-f0-9]{32}', args.recipe):
        parser.error('Ungültige Rezeptkennung')
    sys.path.insert(0, str(ROOT / 'offline-preview/game-workshop-v1'))
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / '.deps'))
    from button_bridge import storage
    from media_selection import FILES
    from players import build_players

    recipe_path = ROOT / 'design-library/recipes/button-workshop' / (args.recipe + '.json')
    recipe = json.loads(recipe_path.read_text(encoding='utf-8'))
    storage.validate_recipe(recipe)
    if recipe['schema_version'] != 2 or recipe.get('base'):
        parser.error('Diese Vorschau erwartet einen eigenen Button ohne importierte Spielquelle.')
    source_path = HERE / 'blackjack-tisch.html'
    manifest_path = HERE / 'source.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    source = source_path.read_text(encoding='utf-8')

    # The approved scene has its own versioned source; shared workshop styles
    # remain outside this scene stylesheet and keep their original selectors.
    scene_image = ROOT / 'static/blackjack-tisch-sitzansicht-v1.webp'
    image_url = 'data:image/webp;base64,' + base64.b64encode(scene_image.read_bytes()).decode('ascii')
    templates = Environment(loader=FileSystemLoader(ROOT / 'templates'), autoescape=True)
    markup = templates.get_template('_blackjack_table.html').render(live_table=False, scene_image=image_url)
    scene_css = (ROOT / 'static/blackjack-table.css').read_text(encoding='utf-8')
    script_start = source.index('<script>')
    source = markup + '\n<style>\n' + scene_css + '\n/* blackjack-workshop-canonical */\n</style>\n' + source[script_start:]

    # Keep the shared CSS selectors intact. Prefixing only these rules used to
    # outrank the renderer's own settings for lettering, ink and sidewall.
    base_css = (ROOT / 'static/comic-button.css').read_text(encoding='utf-8')
    material_css = (BUTTON / 'materials.css').read_text(encoding='utf-8')
    textures = {
        'wood': ('/assets/oak-v1.png', ROOT / 'static/blackjack-button-oak-v1.webp'),
        'wood-aged': ('/assets/walnut-aged-v1.webp', BUTTON / 'assets/walnut-aged-v1.webp'),
    }
    texture_file = None
    if recipe['settings']['material'] in textures:
        texture_url, texture_file = textures[recipe['settings']['material']]
        texture = base64.b64encode(texture_file.read_bytes()).decode('ascii')
        material_css = material_css.replace("url('" + texture_url + "')", "url('data:image/webp;base64," + texture + "')")
    start = source.index('/* blackjack-workshop-canonical */')
    end = source.index('</style>', start)
    portrait_css = (ROOT / 'static/player-portrait.css').read_text(encoding='utf-8')
    source = source[:start] + '/* blackjack-workshop-canonical */\n@layer button-base {\n' + base_css + '\n}\n' + material_css + '\n' + portrait_css + '\n' + source[end:]

    geometry_exports = ['cloneContour','makeContour','CONTOUR_PLANE','CONTOUR_ASPECT','BUTTON_WIDTH_UNITS','contourPlane','buttonMetrics','contourError','roundedPoints','toPolygon','outlinePath']
    bundle = 'const __bjGeometry=(()=>{\n' + module(BUTTON / 'geometry.js', '', geometry_exports)
    bundle += 'const __bjComponents=(()=>{\n' + module(ROOT / 'offline-preview/comic-ui-v1/components.js', '', ['icon','button','die'])
    bundle += 'const __bjRenderer=(()=>{\n' + module(BUTTON / 'renderer.js', 'const {button}=__bjComponents; const {toPolygon,outlinePath,contourPlane,CONTOUR_PLANE,CONTOUR_ASPECT,buttonMetrics,BUTTON_WIDTH_UNITS}=__bjGeometry;', ['registerSourceRenderer','materialize','renderButton'])
    bundle += 'const __bjMedia=(()=>{\n' + module(BUTTON / 'media-renderer.js', 'const {renderButton:originalRender,materialize:originalMaterialize,registerSourceRenderer}=__bjRenderer;', ['matchedFont','materialize','renderButton'])

    selected = recipe['settings']['sound']
    if selected == 'material':
        selected = {'wood':'wood-plank','wood-aged':'wood-plank','stone':'stone-scrape','metal':'robot-step'}.get(recipe['settings']['material'])
    records = [row for row in storage.CATALOG['sounds'] if row['id'] == selected]
    assets, audio_hashes = {}, {}
    for record in records:
        asset = FILES.get('/assets/audio/' + record['file'], BUTTON / 'assets/audio' / record['file'])
        assets[record['file']] = base64.b64encode(asset.read_bytes()).decode('ascii')
        audio_hashes[record['file']] = digest(asset)
    bundle += 'const __bjAudioRecords=' + json.dumps(records, ensure_ascii=False) + ';\n'
    bundle += 'const __bjAudioAssets=' + json.dumps(assets) + ';\n'
    bundle += "async function __bjAudioAsset(file){const data=__bjAudioAssets[file];return {ok:typeof data==='string',async arrayBuffer(){return Uint8Array.from(atob(data),c=>c.charCodeAt(0)).buffer;}};}\n"
    # Only the file transport is adapted for the self-contained conversation
    # preview. The shared sound engine, offsets, durations and volume stay exact.
    sound = module(BUTTON / 'sound.js', '', ['createSound'])
    assert sound.count('fetch(assetBase+record.file)') == 1
    sound = sound.replace('fetch(assetBase+record.file)', '__bjAudioAsset(record.file)')
    bundle += 'const __bjSoundEngine=(()=>{\n' + sound
    bundle += 'const __bjPlayers=(()=>{\n' + module(ROOT / 'static/player-portrait.js', '', ['createPlayerPortrait'])
    runtime_bundle = bundle + 'const recipe=' + json.dumps(recipe, ensure_ascii=False) + ';\n'
    runtime_bundle += 'const renderButton=__bjMedia.renderButton, createSound=__bjSoundEngine.createSound, createPlayerPortrait=__bjPlayers.createPlayerPortrait, audioRecords=__bjAudioRecords;\nexport {recipe,renderButton,createSound,createPlayerPortrait,audioRecords};\n'
    (ROOT / 'static/blackjack-workshop.js').write_text(runtime_bundle, encoding='utf-8')
    players, player_sources = build_players(ROOT)
    bundle += 'const __bjSeatData=' + json.dumps(players, ensure_ascii=False) + ';\n'
    backs = json.loads((HERE / 'card-back-prompts.json').read_text(encoding='utf-8'))['variants']
    card_backs = {row['name']:'data:image/webp;base64,' + base64.b64encode((ROOT / row['thumbnail']).read_bytes()).decode('ascii') for row in backs}
    bundle += 'const __bjCardBacks=' + json.dumps(card_backs, ensure_ascii=False) + ';\n'
    bundle += 'const __bjRecipe=' + json.dumps(recipe, ensure_ascii=False) + ';\n'
    start = source.index('const __bjGeometry=')
    end = source.index("\n  const root = document.getElementById('stormseed-blackjack');", start)
    source = source[:start] + bundle + source[end:]

    # Mono uses the same installed Courier New as the workshop. Cinzel stays
    # available for an explicitly selected Cinzel recipe, without forcing it.
    source = re.sub(r"@font-face\{font-family:'Workshop Cinzel';[^}]+\}\n?", '', source)
    face = ''
    if recipe['settings']['font'] == 'cinzel':
        data = base64.b64encode(woff_bytes((BUTTON / 'assets/fonts/Cinzel-Variable.ttf').read_bytes())).decode('ascii')
        face = "@font-face{font-family:'Workshop Cinzel';src:url('data:font/woff;base64," + data + "') format('woff');font-style:normal;font-weight:400 900;font-display:swap}\n"
        source = source.replace('<style>', '<style>\n' + face, 1)
    (ROOT / 'static/blackjack-workshop.css').write_text('/* Generated from the canonical workshop sources by build_preview.py. */\n' + face + '@layer button-base {\n' + base_css + '\n}\n' + material_css, encoding='utf-8')
    assert len(source.encode('utf-8')) < 1_000_000, f"Vorschau zu groß: {len(source.encode('utf-8'))} Bytes; Avatare {len(json.dumps(players))}, Kartenrücken {len(json.dumps(card_backs))}, Materialien {len(material_css)}"
    source_path.write_text(source, encoding='utf-8')
    Path(manifest['response_copy']).write_text(source, encoding='utf-8')
    subprocess.run([sys.executable, str(args.render_script), str(source_path), str(ROOT / manifest['served_preview']), '--title', 'Black Jack · Spielfeldvorschau', '--force'], check=True)
    shared = ['static/comic-button.css','offline-preview/comic-ui-v1/components.js'] + ['offline-preview/button-workshop-v1/' + name for name in ['materials.css','geometry.js','renderer.js','media-renderer.js','sound.js']]
    manifest.update(button_recipe=recipe_path.relative_to(ROOT).as_posix(), button_parent=recipe.get('parent_id'), button_font=recipe['settings']['font'], source_sha256=digest(source_path), button_recipe_sha256=digest(recipe_path), shared_sources={name:digest(ROOT / name) for name in shared}, button_audio_sources=audio_hashes, build_script='offline-preview/blackjack-v1/build_preview.py', button_overrides=['action label and disabled state only'])
    manifest['button_texture'] = dict(path=texture_file.relative_to(ROOT).as_posix(), sha256=digest(texture_file)) if texture_file else None
    manifest.update(scene_image=scene_image.relative_to(ROOT).as_posix(), scene_image_sha256=digest(scene_image), approved_scene_original='offline-preview/blackjack-v1/concepts/blackjack-tisch-45grad-v1.png', scene_sources={name:digest(ROOT / name) for name in ['templates/_blackjack_table.html','static/blackjack-table.css']}, card_perspective_degrees=45, view='close seated view; fixed painted environment with interactive card layer')
    manifest['seating_table'] = dict(route='/karten/blackjack', component='templates/_blackjack_table.html', styles='static/blackjack-table.css', script='static/blackjack-seating.js', runtime={name:digest(ROOT / name) for name in ['static/blackjack-workshop.js','static/blackjack-workshop.css']})
    manifest.update(portrait_component={name:digest(ROOT / name) for name in ['static/player-portrait.js','static/player-portrait.css','player_portrait.py']},portrait_assets={name:digest(ROOT / name) for name in player_sources}, seat_roles=['marked example','existing local profile','marked example'], card_back_library=[row['library_id'] for row in backs])
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Button vollständig übernommen:', recipe['id'])


if __name__ == '__main__':
    main()
