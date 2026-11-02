"""Inventory the opt-in local button media bridge; no game app or database."""
from pathlib import Path
from hashlib import sha256
import json,sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'offline-preview/game-workshop-v1'))
from source_buttons import SourceButtons
from button_bridge import storage
from media_selection import SELECTION,FILES,matched_css


if __name__=='__main__':
    legacy=json.loads((ROOT/'offline-preview/button-workshop-v1/catalog.json').read_text(encoding='utf-8'))
    source=SourceButtons();assets=source.assets()
    mismatches=[]
    for asset in assets:
        old=storage.validate_recipe(source.recipe(asset['id'],legacy))
        new=storage.validate_recipe(source.recipe(asset['id'],storage.CATALOG))
        if old!=new:mismatches.append(asset['id'])
    paths=['offline-preview/button-workshop-v1/'+p for p in ('media_selection.py','media-renderer.js','renderer.js','sound.js','catalog.json')]
    paths+=['offline-preview/game-workshop-v1/'+p for p in ('media_library.py','media-stage.css')]
    report=dict(schema=1,checked_on='2026-10-28',scope='Lokale opt-in-Auswahl im Button-Editor; keine Umstellung von Spielen oder gespeicherten Entwürfen.',
        fonts=SELECTION['fonts'],sounds=SELECTION['sounds'],
        existing_choices={key:next(f['options'] for f in legacy['fields'] if f['key']==key) for key in ('font','sound')},
        original_recipes=dict(checked=len(assets),different=mismatches),
        aliases={url:dict(file=path.relative_to(ROOT).as_posix(),sha256=sha256(path.read_bytes()).hexdigest()) for url,path in FILES.items()},
        source_files={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},
        matched_css_sha256=sha256(matched_css().encode('utf-8')).hexdigest(),
        evidence='runtime/button-media-20261028/',
        later=['Persönliche gestalterische und klangliche Abnahme.','Weitere Modelle, andere Baustein-Editoren und Spieleinbau gesondert prüfen.'])
    (ROOT/'docs/BUTTON_MEDIEN_INTEGRATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(fonts=len(SELECTION['fonts']),sounds=len(SELECTION['sounds']),**report['original_recipes'])))
    raise SystemExit(bool(mismatches))
