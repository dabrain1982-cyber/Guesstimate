"""Audit currently connected local button sources without importing the game/DB."""
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'offline-preview/game-workshop-v1'))
from source_buttons import SourceButtons,ButtonParser


def audit():
    source=SourceButtons();assets=source.assets();records=list(source.records.values())
    def relative(path):return path.relative_to(ROOT).as_posix()
    scripts=set()
    for template in source.active_templates:
        text=source.read('templates/'+template)
        for endpoint,name in re.findall(r"url_for\(\s*['\"](static|conquest_table_asset)['\"]\s*,\s*filename\s*=\s*['\"]([^'\"]+\.js)['\"]",text):
            scripts.add(('static/' if endpoint=='static' else 'offline-preview/conquest-2-5d-v1/')+name)
    tree=ast.parse(source.read('conquest.py'))
    aliases={}
    for node in ast.walk(tree):
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='shared_buttons' for t in node.targets):
            aliases={name:'offline-preview/'+folder+'/'+file for name,(folder,file) in ast.literal_eval(node.value).items()}
    aliases['components.js']='offline-preview/comic-ui-v1/components.js'
    pending=list(scripts);active=set();vendor=[]
    while pending:
        name=pending.pop()
        if name in active:continue
        if '/vendor/' in name:vendor.append(name);continue
        if not (ROOT/name).is_file():
            name=aliases.get(Path(name).name,name)
            if not (ROOT/name).is_file():continue
        if name in active:continue
        active.add(name)
        for ref in re.findall(r"(?:\bfrom\s*|\bimport\s*\()\s*['\"]([^'\"]+\.js)['\"]",source.read(name)):
            target=(ROOT/name).parent/ref
            pending.append(relative(target.resolve()) if target.resolve().is_relative_to(ROOT) else '')
    captured=json.loads((ROOT/'offline-preview/game-workshop-v1/generated-buttons.json').read_text(encoding='utf-8'))['buttons']
    coverage=[];missing=[]
    for template in sorted(source.active_templates):
        name='templates/'+template
        for button in ButtonParser(source.read(name)).buttons:
            hits=[r['id'] for r in records if r['snapshot']['source']['path']==name and r['snapshot']['source']['line']==button['line']]
            item=dict(path=name,line=button['line'],registered=hits)
            coverage.append(item)
            if not hits:missing.append(item)
    surface='offline-preview/conquest-2-5d-v1/table-surface.js'
    other_elements=[]
    for button in ButtonParser(source.read(surface)).buttons:
        identifier=button['attrs'].get('id')
        hits=[r['id'] for r in records if r['snapshot']['source']['path']==surface and r['start']==button['start']]
        item=dict(path=surface,line=button['line'],element_id=identifier,registered=hits)
        if identifier=='reset-turn':item['disposition']='Nur Offline-Demo; gespeichertes Spiel blendet diesen Testknopf ausdrücklich aus.'
        elif identifier=='awarded-card':
            item['disposition']='Kartenkomponente mit Klickfläche; gehört zur Elementart Karten.';other_elements.append(item)
        elif not hits:missing.append(item)
        coverage.append(item)
    factories=[]
    for name in sorted(active):
        for match in re.finditer(r"(?:document\.createElement|\bmake)\(\s*['\"]button['\"]",source.read(name)):
            line=source.read(name)[:match.start()].count('\n')+1
            context=source.read(name)[max(0,match.start()-60):match.end()]
            item=dict(path=name,line=line)
            captures=[row['key'] for row in captured if row['path']==name and row.get('factory_line',row['line'])==line]
            if captures:item['disposition']='registered';item['capture_keys']=captures
            elif name=='offline-preview/comic-ui-v1/components.js':item['disposition']='Gemeinsamer Renderer; sieben registrierte Conquest-Aktionen.'
            elif name.endswith('/territories.js'):
                item['disposition']='Truppenmarke mit Klickfläche; gehört zu Figuren/Spielsteinen.';other_elements.append(item)
            elif name.endswith('/turn-controls.js'):
                item['disposition']='Auswählbare Länderkarte; gehört zu Karten.';other_elements.append(item)
            else:item['disposition']='UNGEKLÄRT';missing.append(item)
            factories.append(item)
    for item in factories:
        for key in item.get('capture_keys',[]):
            if not any(r.get('capture_key')==key for r in records):missing.append(dict(path=item['path'],capture_key=key))
    evidence={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in sorted({*active,*('templates/'+t for t in source.active_templates),surface})}
    games={}
    for game in sorted({g for a in assets for g in [a['game'],*a.get('games',[])]}):
        matches=[a for a in assets if a['game']==game or game in a.get('games',[])]
        games[game]=dict(uses=len(matches),models=len({a['model_id'] for a in matches}),includes_shared=True)
    return dict(schema=1,scope='Aktuell lokal verbundene Seitenvorlagen, eigene Skripte und gespeicherte Conquest-Oberfläche; keine Live-Server-Prüfung.',
                registered_uses=len(assets),models=len({a['model_id'] for a in assets}),games=games,
                native_coverage=coverage,dynamic_factories=factories,other_element_bindings=other_elements,
                active_templates=sorted(source.active_templates),active_scripts=sorted(active),vendor_scripts=sorted(set(vendor)),
                unmounted_legacy=['static/conquest-table.js'],missing=missing,stale_captures=source.generated_errors,evidence=evidence,
                design_candidates=[
                    dict(name='Startseitenaktion und Nachholen',status='Zielstil besprochen; Nachholbutton bleibt für den persönlichen Editortest unverändert.'),
                    dict(name='Würfelauswahl: behalten / Ablage',status='Eine Quellfunktion, kontextabhängig unterschiedliche Maße und Bewegung. Kandidat für Modelloptionen, keine Angleichung ausgeführt.'),
                    dict(name='Conquest: Schließen / Auswahl aufheben',status='Gleiche Aufgabe mit unterschiedlichen Größen und Kontexten. Kandidat zur gemeinsamen Optionsprüfung, keine Angleichung ausgeführt.')])


def write_report(report):
    (ROOT/'docs/BUTTON_BESTAND.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# Buttonbestand der lokalen Spiele','',report['scope'],'',
           f"{report['registered_uses']} registrierte Verwendungen, {report['models']} Modelle. Gemeinsame Verwendungen werden je Spiel mitgezählt; die Spielzeilen sind daher nicht addierbar.",'',
           '| Spiel / Bereich | Verwendungen einschließlich gemeinsamer Buttons | Modelle |','|---|---:|---:|']
    lines.extend(f"| {game} | {row['uses']} | {row['models']} |" for game,row in report['games'].items())
    lines+=['','Alle verbundenen nativen Buttonstellen und eigenen Erzeugungsfunktionen sind im JSON-Bericht einzeln zugeordnet. Ungeklärte Stellen: '+str(len(report['missing']))+'. Veraltete Erzeugungsnachweise: '+str(len(report['stale_captures']))+'.','',
            'Klickflächen auf Länderkarten und Truppenmarken sind als Verbindungen zu Karten beziehungsweise Figuren/Spielsteinen erfasst. Sie werden nicht als zusätzliche, leere Buttonmodelle ausgegeben. Der nur in der Offline-Demo verwendete Neustartknopf und die alte, nicht eingebundene Conquest-Oberfläche sind ausdrücklich abgegrenzt. Normale Textlinks, Logos, Flyer, Aufklappüberschriften und Eingabefelder bleiben ihren Elementarten zugeordnet.','',
            'Originalmarkup, Styles und Spielaktionen bleiben unverändert. Die Vorschau zeigt versteckte Aktionen in einem sichtbaren Beispielzustand, ohne sie im Spiel freizuschalten. Registrierte Buttons öffnen im gemeinsamen Editor als eigene Entwürfe. Die Aufnahme ersetzt keine tatsächliche Spielkomponente und ist keine Prüfung sämtlicher Spielaktionen.','',
            '## Kandidaten für spätere Modelloptionen','']
    lines.extend('- **'+item['name']+':** '+item['status'] for item in report['design_candidates'])
    lines+=['','## Erneuern','',
            '`node deploy/capture_generated_buttons.mjs` liest die Originalfunktionen für dynamische Buttons und erzeugt inaktive Beispieldaten. `python deploy/audit_button_coverage.py` erneuert diesen Bericht. Beide arbeiten ohne App-Import, Datenbankzugriff oder Serverkontakt. Geänderte Erzeugungsquellen werden anhand ihrer Prüfsummen als veraltet erkannt. Profile und Modellnachweise werden anschließend über die bestehenden lokalen Prüfseiten erneuert; freigegebene Gruppen bleiben erhalten.','']
    (ROOT/'docs/BUTTON_BESTAND.md').write_text('\n'.join(lines),encoding='utf-8')


if __name__=='__main__':
    report=audit();write_report(report)
    print(json.dumps({key:report[key] for key in ('registered_uses','models','games','missing','stale_captures')},ensure_ascii=False))
    raise SystemExit(bool(report['missing'] or report['stale_captures']))
