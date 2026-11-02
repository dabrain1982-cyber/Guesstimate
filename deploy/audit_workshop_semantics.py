"""Audit catalog granularity, without importing the game or opening its database."""
from collections import Counter
from hashlib import sha256
import json
import importlib.util
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'offline-preview/game-workshop-v1'))
from workspace_store import ProjectLibrary
from workshop_catalog import ELEMENT_KINDS
spec=importlib.util.spec_from_file_location('semantic_workshop_server',ROOT/'offline-preview/game-workshop-v1/serve.py')
server_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(server_module)
EXISTING_ASSETS=server_module.EXISTING_ASSETS

SOURCE_KINDS=('buttons','windows','inputs','indicators','players','lobby')
NOTES={
 'fonts':'Sieben recherchierte freie Schrift-/Oberflächenkombinationen: Kreide, Stein, Metall, Stempel, Handschrift, Comic, Klar. Passende feste Stile statt beliebiger Effektmatrix; lokal, Editoroptionen später.',
 'sounds':'13 kurze Kenney-CC0-Klänge nach Bedienung, Tischaktionen und Spielereignissen; drei Zweckgruppen. Originale erhalten, lokale Pegelangleichung; keine Spielereignisse als Datenkopien.',
 'buttons':'Beschriftungen und feste Einsatzorte derselben Modelle; keine Klickereignisse als Elemente.',
 'windows':'35 gemeinsame Modelle, 114 feste Beispiele einschließlich vollständiger Quizfragen-/Ergebnisfenster, Antwortübersicht, Ranglistenrahmen und Leerzustand. Fragen nach Feldvertrag verknüpft, keine Fragenkopien.',
 'inputs':'Feldtypen, Grenzen und feste Auswahlzustände; keine Eingaben oder Antwortdatensätze.',
 'indicators':'Anzeigeformen mit eingefrorenen Beispielwerten; keine laufenden Zeiten oder Punktestände.',
 'players':'Profil-/Pultmodelle, feste Rollen und endliche Ausstattungsmotive; keine realen Konten.',
 'lobby':'Gemeinsame Raum-/Listenmodelle mit neutralen Rollen und Zuständen; keine echten Räume.',
 'board':'Zwei Grundvarianten 2D/3D; Größe, Form und Bild als Eigenschaften. Conquest, Playtable und gemeinsame Würfelfläche aufgenommen; acht Spiele auf vorhandene Bretter geprüft.',
 'pieces':'Drei wiederverwendbare Formfamilien mit sieben Konfigurationen: vorhandene Schach-/Damevorlagen und ursprüngliche Conquest-Truppenmarke. Rollen, Stil, Farben, Anzahl und Zustände als Eigenschaften; keine Bestände je Land oder Partie. Acht Spiele geprüft.',
 'dice':'Genau zwei vorhandene Umsetzungen: Würfeltisch mit Physik und flache Conquest-Anzeige. Anzahl, Aufdrucke und Farben sind Parameter; keine einzelnen Würfelergebnisse.',
 'cards':'Zwei Grundbausteine, zwölf ganze Sätze. Einzelkarten sind Satzmitglieder, Fragen sind Daten.',
 'background':'15 endliche Bildmotive und neun ganze Raumkonfigurationen in den beiden Grundvarianten 2D/3D. Conquests Wand, Möbel und Teppich als ein Raum; keine Zustands- oder Spielstandkopien.',
 'avatars':'Endlicher Motivkatalog; keine Aufnahme einzelner Personen.',
 'titles':'Acht vorhandene Spielmotive und Mäxchen-Logo, zwei gemeinsame Bildfamilien. Reine Texttitel bleiben Teil ihrer vorhandenen Kompositionen.',
 'icons':'Fünf endliche Symbolsätze (5/4/15/3/2 Motive) und App-Symbol. Satz als Ganzes, Motivwahl nur in der Vorschau.',
 'flyers':'13 feste Konfigurationen in drei gemeinsamen Kompositionen: Startseiten-Flyer, Spiel-/Gruppenkachel und Perfect-Kachel. Persönliche Grußfolie ausgeschlossen.'}

def report(directory,buttons_directory):
    store=ProjectLibrary(directory,buttons_directory,EXISTING_ASSETS)
    assets=store.assets();generated=[a for a in assets if a['source'] not in ('saved','legacy')]
    families=[]
    for kind,meta in ELEMENT_KINDS.items():
        rows=[a for a in generated if a['kind']==kind]
        source=[a for a in rows if a['source']=='game']
        families.append(dict(kind=kind,title=meta['title'],entries=len(rows),
                             source_examples=len(source),source_models=len({a['model_id'] for a in source}),
                             roles=dict(Counter(a.get('record_role') for a in rows)),finding=NOTES[kind]))
    bindings=[dict(id=a['id'],game=a['game'],binding=a['snapshot']['data_binding']) for a in generated if a['snapshot'].get('data_binding')]
    return dict(schema=1,scope='Nur lokaler Katalog; keine Spiele, Fragenbanken, Konten oder persönlichen Entwürfe geändert.',
                rule='Wiederverwendbarer Baustein / endlicher Satz / verknüpfter wachsender Datenbestand.',
                families=families,question_entries=0,question_windows=bindings,cards=store.cards.report(),
                catalog_ids={k:sorted(a['id'] for a in generated if a['kind']==k) for k in SOURCE_KINDS},
                further_families=[dict(kind=k,finding=v) for k,v in {
                    'materials':'Gemeinsame Palette mit neun Materialfamilien und Originalbeispielen. Wünsche als Projekteigenschaft; keine zusätzlichen Elementassets. Editoroptionen später.',
                    'presentation':'Drei Originalansichten erläutern die bestehenden Projektentscheidungen. Kamera, Licht und Bewegung als Eigenschaften; keine einzelnen Frames oder dritten Brett-/Würfelmodelle.'}.items()],
                limits=['Logikprüfung der Aufnahme; gesonderter Abschlussabgleich aller acht Spiele in WERKSTATT_ABSCHLUSSPRUEFUNG.json.',
                        'Feste Zustandsbeispiele bleiben als Einsatzvarianten der gemeinsamen Modelle erhalten.',
                        'Editoroptionen und Spielintegration bleiben offen.'])

if __name__=='__main__':
    base=ROOT/'runtime/workshop-audit-20261027'
    result=report(base/'read-only-library',base/'read-only-buttons')
    (ROOT/'docs/WERKSTATT_LOGIKPRUEFUNG.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(areas=len(result['families']),further=len(result['further_families']),question_entries=0,
                         source_models={f['kind']:f['source_models'] for f in result['families'] if f['source_models']},
                         bound_windows=len(result['question_windows'])),ensure_ascii=False))
