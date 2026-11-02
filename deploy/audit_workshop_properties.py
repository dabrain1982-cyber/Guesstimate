"""Document bounded project properties, independently of games, DBs and personal maps."""
from pathlib import Path
import importlib.util,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'offline-preview/game-workshop-v1'))
spec=importlib.util.spec_from_file_location('properties_audit_server',ROOT/'offline-preview/game-workshop-v1/serve.py')
server=importlib.util.module_from_spec(spec);spec.loader.exec_module(server)
from workspace_store import ProjectLibrary
from workshop_catalog import ELEMENT_KINDS,PRESENTATION

if __name__=='__main__':
    base=ROOT/'runtime/properties-20261027'
    store=ProjectLibrary(base/'audit-library',base/'audit-buttons',server.EXISTING_ASSETS)
    assets=store.assets();catalog=store.properties.catalog(assets)
    report=dict(schema=1,checked_on='2026-10-27',scope='Nur lokale Projekteigenschaften; keine zusätzlichen Elementassets und keine Spiel-/Editorumstellung.',
        areas=len(ELEMENT_KINDS),catalog=catalog,project_decisions=PRESENTATION,
        source_files={entry['path']:entry['sha256'] for row in catalog['materials'] for entry in row['evidence']},
        rule='Materialwünsche werden an der Projektmappe gespeichert, Originalelemente und ihre Schnappschüsse bleiben exakt.',
        storage=dict(optional_field='surfaces',project_schema=2,old_maps='Ohne neuen Schlüssel unverändert lesbar; keine automatische Migration.',handoff='Materialdefinitionen und Herkunft eingefroren; bestehende Elementliste und Darstellung unverändert übernommen.'),
        limits=['Beispiele zeigen vorhandene Materialien, keine beliebige Beschichtung jedes Bausteins.',
                'Kreide, Stein und Metall verweisen auf die passenden festen Schriftstile; keine freie Effektmatrix.',
                '2,5D ist eine Ansicht räumlicher Elemente, kein drittes Brett- oder Würfelmodell.',
                'Anzahl, Aufdruck, Farbe, Licht und Bewegung bleiben Eigenschaften. Physik wird nur für die vorhandenen räumlichen Würfel belegt.',
                'Die Detailoptionen der einzelnen Editoren und eine spätere Spielintegration bleiben offen.'])
    (ROOT/'docs/MATERIAL_DARSTELLUNG.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(materials=len(catalog['materials']),views=len(catalog['views']),areas=len(ELEMENT_KINDS),new_element_assets=0),ensure_ascii=False))
