"""Scoped final cross-check of active eight-game UI sources against workshop components."""
from collections import Counter
from pathlib import Path
import hashlib,importlib.util,json,re,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'offline-preview/game-workshop-v1'))
from workspace_store import ProjectLibrary
from source_windows import Fragments

PAGES={
 'Guesstimate':['home.html','question.html','result.html','pool_exhausted.html'],
 'Guesstimate Party':['party_index.html','party_lobby.html','party_countdown.html','party_question.html','party_result.html'],
 'Perfect':['nerd_index.html','nerd_mode.html'],
 'Playtable':['card_table_index.html','card_table_lobby.html','card_table_game.html'],
 **{g:['dice_table_index.html','dice_table_lobby.html','dice_table_game.html'] for g in ('Würfeltisch','Kniffel','Mäxchen')},
 'Conquest':['conquest_index.html','conquest_lobby.html','conquest_table.html']}
COLLECTION=['tabletop_connection.html','tabletop_family.html']
AGGREGATES={
 'variant-a-showcase':('Anordnung vorhandener Flyer, Titel und Startaktionen',['graphics-flyer-daily']),
 'variant-a-ranking':('Seitengerüst um den aufgenommenen Ranglistenrahmen',['window-quiz-ranking-window']),
 'action-dock':('Anordnung bereits erfasster Weiter-/Ergebnisaktionen',['buttons']),
 'result-dock':('Anordnung bereits erfasster Ergebnisaktionen',['buttons']),
 'card-player-desks':('Liste wiederverwendeter Spielerpulte',['players']),
 'dice-game-players':('Liste wiederverwendeter Spieleranzeigen',['players']),
 'card-free-area':('Gemeinsame Kartenfläche, bereits als Brett erfasst',['boards-2d-playtable']),
 'dice-render-area':('Renderplatz der vorhandenen Physikwürfel und Würfelfläche',['dice-physics-v1','boards-2d-dice-table']),
 'tabletop-game-grid':('Raster wiederverwendeter Spielkacheln',['graphics-tile-conquest','graphics-tile-cards']),
 'tabletop-family-grid':('Raster wiederverwendeter Spielkacheln',['flyers']),
 'camera-controls':('Ansichtseinstellungen vorhandener Räume und Bretter',['inputs']),
 'player-roster':('Liste wiederverwendeter Spielerporträts',['players'])}
FACTORIES={
 'static/card-table.js':('createElement', ['cards','windows','indicators','inputs'], 'Karten, Stapel, Gebote, Notiz und Pot; keine Einträge je einzelner Karte oder Aktion.'),
 'static/dice-table.js':('createElement', ['dice','windows','indicators','players'], 'Physikwürfel, Haltefelder, Wurfhistorie, Kniffelblock und verdeckter Wurf als Zustand derselben Würfel/Anzeige.'),
 'static/stormseeds-perfect.js':('querySelector', ['windows','inputs','indicators'], 'Bestehende Phasenfenster; Werte und Zustandsklassen. Browserbestätigungen sind Browserfunktionen.'),
 'static/party.js':('querySelector', ['windows','indicators','lobby'], 'Countdown und Phasenwechsel bestehender Vorlagen; keine neuen Datenobjekte je Zeitwert.'),
 'static/leaderboards.js':('querySelector', ['windows','players','indicators'], 'Vorhandener Ranglistenrahmen und wiederholte Zeilen.'),
 'static/player-portrait.js':('createPlayerPortrait', ['players','icons'], 'Eine gemeinsame Porträtfabrik, endliche Statistikzeichen.'),
 'offline-preview/conquest-2-5d-v1/scene.js':('buildRoom', ['background','board'], 'Originaler Raum und Tisch als getrennte wiederverwendbare Kompositionen.'),
 'offline-preview/conquest-2-5d-v1/territories.js':('createTerritoryLayer', ['pieces','indicators'], 'Eine Truppenmarke für alle Länder; Zahlen/Farben und Auswahl sind Eigenschaften. Routen sind Darstellungskonfiguration.'),
 'offline-preview/conquest-2-5d-v1/turn-controls.js':('createTurnControls', ['windows','players','cards'], 'Zugleiste, Hände, Aufträge, Bestätigungen und Porträts aus vorhandenen Fabriken.'),
 'offline-preview/conquest-2-5d-v1/attack.js':('showRolls', ['dice','windows','inputs','indicators'], 'Originale flache Würfelanzeige und Kampffenster; Routenpfeile als Darstellung.'),
 'offline-preview/conquest-2-5d-v1/fortify.js':('createFortifyControls', ['windows','inputs'], 'Vorhandene Truppenverschiebung; Betrag und Ziel als Daten.'),
 'offline-preview/conquest-2-5d-v1/cards.js':('createCountryCard', ['cards','icons'], 'Endliche Länder-/Auftragssätze und gemeinsame Kartensymbole.'),
 'offline-preview/conquest-2-5d-v1/table-surface.js':('mountTableSurface', ['windows','buttons','inputs','indicators','players'], 'Aktuelle Tischoberfläche, keine alte static/conquest-table.js-Variante.')}


def clean_template(text):return re.sub(r'{[{%].*?[%}]}',lambda m:re.sub(r'[^\n]',' ',m[0]),text,flags=re.S)


def classify(text,index,assets):
    rows=[]
    for row in Fragments(clean_template(text)).elements:
        if row['tag'] not in ('section','article','aside','dialog'):continue
        classes=(row['attrs'].get('class') or '').split()
        if not classes:continue
        first=classes[0];refs=index.get(first,[])
        if row['attrs'].get('data-game-slide')=='4':
            status,reason,refs='excluded','Persönliche Grußfolie; Form bereits als allgemeiner Flyerbaustein erfasst.',[]
        elif first=='prototype-note':
            status,reason,refs='excluded','Technischer Vorschau-/Entwicklerhinweis; scene.js blendet ihn im normalen Spiel aus.',[]
        elif refs:status,reason='covered','Originalklasse innerhalb eines registrierten Bausteins oder einer Raumkomposition.'
        elif first in AGGREGATES:
            reason,requirements=AGGREGATES[first];refs=[a['id'] for a in assets if any(r in (a['id'],a.get('model_id'),a['kind']) for r in requirements)]
            status='composition' if refs else 'unreviewed'
        else:status,reason,refs='unreviewed','Noch keiner Komponente oder belegten Anordnung zugeordnet.',[]
        rows.append(dict(line=row['line'],tag=row['tag'],root_class=first,status=status,reason=reason,refs=sorted(set(refs))[:10]))
    return rows


def collect(store):
    assets=store.assets();index={}
    for a in assets:
        snapshot=a['snapshot'];markup=snapshot.get('rendered_markup','')+snapshot.get('settings',{}).get('markup','')
        for element in Fragments(markup).elements:
            for cls in (element['attrs'].get('class') or '').split():index.setdefault(cls,[]).append(a['id'])
    checked={};games=[];gaps=[];paths=set()
    for game,pages in PAGES.items():
        entries=list(pages)+(COLLECTION if game in ('Perfect','Playtable','Würfeltisch','Kniffel','Mäxchen','Conquest') else [])
        dependencies=set(entries);todo=list(entries)
        while todo:
            current=todo.pop()
            for child in store.source_buttons.template_dependencies.get(current,[]):
                if child not in dependencies:dependencies.add(child);todo.append(child)
        sources=[]
        for page in sorted(dependencies):
            path='templates/'+page;paths.add(path)
            if path not in checked:checked[path]=classify((ROOT/path).read_text(encoding='utf-8'),index,assets)
            rows=checked[path];sources.append(dict(path=path,semantic_containers=len(rows)))
            gaps.extend(dict(game=game,path=path,**row) for row in rows if row['status']=='unreviewed')
            paths.update(store.source_buttons.styles(page))
        matching=[a for a in assets if game in [a.get('game'),*(a.get('games') or [])]]
        games.append(dict(game=game,sources=sources,categories=sorted({a['kind'] for a in matching}),refs=sorted(a['id'] for a in matching)))
    surface='offline-preview/conquest-2-5d-v1/table-surface.js';paths.add(surface)
    checked[surface]=classify((ROOT/surface).read_text(encoding='utf-8'),index,assets)
    gaps.extend(dict(game='Conquest',path=surface,**row) for row in checked[surface] if row['status']=='unreviewed')
    factories=[]
    for path,(anchor,kinds,reason) in FACTORIES.items():
        paths.add(path);text=(ROOT/path).read_text(encoding='utf-8');present=anchor in text
        if not present:gaps.append(dict(path=path,status='unreviewed',reason='Erwartete Originalfabrik fehlt.'))
        factories.append(dict(path=path,anchor=anchor,status='reviewed' if present else 'unreviewed',categories=kinds,reason=reason,
                              refs=sorted(a['id'] for a in assets if a['kind'] in kinds)[:12]))
    scans={}
    for name,file,key in [('buttons','BUTTON_BESTAND.json','missing'),('windows','FENSTER_BESTAND.json','missing_dialogs'),('inputs','EINGABEN_BESTAND.json','uncovered'),('indicators','ANZEIGEN_BESTAND.json','uncovered'),('players','SPIELER_BESTAND.json','uncovered'),('lobby','LOBBYS_BESTAND.json','uncovered')]:
        data=json.loads((ROOT/'docs'/file).read_text(encoding='utf-8'));scans[name]=data.get(key,[])
        if scans[name]:gaps.append(dict(path=file,status='unreviewed',reason='Quellprüfung enthält offene Zuordnungen.'))
    return dict(schema=1,scope='Acht bestehende Spiele, aktuelle Seitenvorlagen, gemeinsame Makros und geprüfte DOM-/3D-Fabriken. Keine Behauptung vollständiger Editor- oder Spiellogiktests.',
        games=games,containers=checked,factories=factories,source_audits=scans,remaining_unreviewed=gaps,
        rooms=store.rooms.report(),added_windows=[dict(id=a['id'],name=a['name'],model=a['model_id']) for a in store.completion.assets()],
        source_files={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(paths)},
        classifications=dict(Counter(r['status'] for rows in checked.values() for r in rows)),
        excluded=['Persönliche Entwürfe und Grußfolie','Wachsende Fragen-/Spieler-/Partiedaten','Nicht geladene alte Conquest-Tischdarstellung und sonstige inaktive Prototypen','Native Browserdialoge und technische Bibliotheksinternas','Kamera, Licht, Schatten, Bewegung und Materialparameter als Eigenschaften, keine zusätzlichen Einzelobjekte'],
        later=['Editoroptionen','Bausteinspezifische Umsetzung von Material- und Darstellungseigenschaften','Persönliche gestalterische Abnahme'])


if __name__=='__main__':
    spec=importlib.util.spec_from_file_location('completeness_server',ROOT/'offline-preview/game-workshop-v1/serve.py');server=importlib.util.module_from_spec(spec);spec.loader.exec_module(server)
    base=ROOT/'runtime/completeness-20261027';result=collect(ProjectLibrary(base/'audit-library',base/'audit-buttons',server.EXISTING_ASSETS))
    (ROOT/'docs/WERKSTATT_ABSCHLUSSPRUEFUNG.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(games=len(result['games']),sources=len(result['source_files']),containers=result['classifications'],remaining=result['remaining_unreviewed']),ensure_ascii=False))
    raise SystemExit(bool(result['remaining_unreviewed']))
