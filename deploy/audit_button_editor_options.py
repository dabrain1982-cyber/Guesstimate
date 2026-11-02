"""Bounded editor review of Guesstimate core models; no game application or DB."""
from pathlib import Path
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'offline-preview/game-workshop-v1'))
from source_buttons import SourceButtons
from button_bridge import storage

if __name__=='__main__':
    source=SourceButtons();assets=source.assets()
    review=(ROOT/'offline-preview/game-workshop-v1/button-review.js').read_text(encoding='utf-8')
    cases=re.findall(r"number:'(\d+)',label:'([^']+)'",review)
    selected=[]
    for number,label in cases:
        asset=next(a for a in assets if a['game']=='Guesstimate' and a['label']==label)
        selected.append(dict(number=number,id=asset['id'],label=label,model=asset['model_id']))
    failures=[]
    for asset in assets:
        try:storage.validate_recipe(source.recipe(asset['id'],storage.CATALOG))
        except (ValueError,KeyError) as error:failures.append(dict(id=asset['id'],error=str(error)))
    paths=['offline-preview/button-workshop-v1/'+name for name in ('workshop.js','renderer.js','materials.css','catalog.json','font-matching.js','sound.js','geometry.js')]+['offline-preview/game-workshop-v1/button-review.js']
    report=dict(schema=1,checked_on='2026-10-27',scope='27 vorhandene Felder an einer Kernaktion sowie Größe/Schrift/Tiefe/Verfügbarkeit an neun Guesstimate-Kernmodellen. Keine vollständige Prüfung aller 85 Modelle.',
        fields=[dict(key=f['key'],label=f['label'],group=f['group']) for f in storage.CATALOG['fields']],
        reviewed_uses=selected,reviewed_models=len({a['model'] for a in selected}),
        catalog=dict(uses=len(assets),models=len({a['model_id'] for a in assets}),validated_recipes=len(assets)-len(failures),failed=failures),
        changes=[dict(field='finish',result='Bei bewahrter Originalfläche deaktiviert und erklärt; bei eigenem Material/Farbe/Stil verfügbar. Keine gespeicherten Werte verändert.'),
                 dict(field='wear',result='Im reduzierten Stil und bei reinen Farb-/durchscheinenden Flächen verborgen; sonst erhalten.'),
                 dict(field='volume',result='Nur bei gewähltem Klang sichtbar; bisheriger Wert bleibt erhalten.'),
                 dict(field='depth',result='Status benennt 0 als ohne Tiefe, 1–4 als dezent; keine Änderung der Bewegung.')],
        source_files={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},
        evidence='runtime/button-options-20261027/',
        media_integration=dict(added_on='2026-10-28',report='docs/BUTTON_MEDIEN_INTEGRATION.json',fonts=7,sounds=13),
        later=[
               'Persönliche gestalterische Abnahme; keine optische Angleichung oder Zusammenführung weiterer Modelle.',
               'Die übrigen Spiele/Modelle und anderen Baustein-Editoren bleiben gesondert zu prüfen.'])
    (ROOT/'docs/BUTTON_EDITOR_PRUEFUNG.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(fields=len(report['fields']),reviewed_models=report['reviewed_models'],reviewed_uses=len(selected),**report['catalog']),ensure_ascii=False))
    raise SystemExit(bool(failures))
