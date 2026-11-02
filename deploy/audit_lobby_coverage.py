"""Inventory original lobby rooms and lists without importing games or their DB."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'offline-preview/game-workshop-v1'))
from source_lobbies import SourceLobbies


def main():
    report = SourceLobbies().report()
    (ROOT / 'docs/LOBBYS_BESTAND.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    groups = {}
    for a in report['assets']:groups.setdefault(a['model_id'], []).append(a)
    lines = ['# Lobbys und Lobbyübersichten in der lokalen Werkstatt', '',
             f'{report["uses"]} Quellvarianten in {report["models"]} gemeinsamen Modellen. Stand: 27.10.2026.', '',
             'Bibliothek → Lobbys & Übersichten enthält nun die Originale aus allen sieben '
             'Mehrspielerspielen. Der vorhandene allgemeine Lobbyentwurf bleibt zusätzlich erhalten. '
             'Mit der Sammlung „Im Spiel verwendet“ werden nur die aufgenommenen Quellvarianten angezeigt. '
             'Spiel, Lobbyart und Text filtern die Ansicht. Konkrete Rollen und Zustände können mehreren '
             'Projektmappen zugeordnet und samt Original, Beispieldarstellung und Quellen lokal übergeben werden.', '',
             '| Modell | Varianten | Spiele / Einsatz | Lobbyarten |', '|---|---:|---|---|']
    for rows in groups.values():
        lines.append('| ' + rows[0]['model_name'] + ' | ' + str(len(rows)) + ' | ' +
                     ', '.join(sorted({a['game'] for a in rows})) + ' | ' + ', '.join(sorted({a['family_name'] for a in rows})) + ' |')
    lines += ['', '## Gemeinsame Quellen und Varianten', '',
              'Die Übersicht verwendet ausschließlich _lobby_overview.html mit ihren ursprünglichen '
              'Spielparametern. Spielkopf, Erstellen-Aktion, Liste, Rückweg, Zeilen und Leer-/Fehlerzustand '
              'stammen aus derselben Komponente. Eigene wartende oder laufende Lobbys, Beitritt, volle '
              'fremde Lobbys und Ergebnisse bleiben getrennte Zustände. Conquest ergänzt reservierte '
              'Plätze und Rückkehr sowie geschlossene Räume. Die Aktualisierungsfehler-Variante zeigt '
              'weiterhin die zuletzt geladene neutrale Beispielliste.', '',
              'Die sechs Standardlobbys verwenden _lobby_room.html samt gemeinsamer Profilfenster. '
              'Hosteinstellungen, lesende Mitspieler, Einzelbelegung und volle Besetzung bleiben '
              'konkrete Varianten. Perfect verwendet unverändert den eigenen Raum aus nerd_mode.html '
              'mit Zettel, Buzzer und Spielerwänden: Punkte-/Zeitspiel, Host/Mitspieler, Bereitschaft, '
              'volle Besetzung und Start-Countdown. Es wird kein Standardraum in Perfect eingebaut.', '',
              f'Alle {len(report["component_calls"])} verbundenen Makro-/Raumquellen sind zugeordnet. '
              'source_lobbies.py nutzt denselben Quellen-, Vorschau- und Speicherweg wie die anderen '
              'aufgenommenen Komponenten. Ganze Räume verwenden die vorhandenen Spielhintergründe; '
              'die Werkstatt passt nur den äußeren Vorschauplatz an und skaliert die ganze Komposition.', '',
              '## Abgrenzung und spätere Aufgaben', '',
              '- Das Daily Quiz hat keine Mehrspielerlobby oder Lobbyübersicht. Seine Startseiten- und Spielerkomponenten bleiben ihren bisherigen Elementarten zugeordnet.',
              '- Ausschließlich neutrale feste Beispiele; keine echten Lobbys, Konten, Mitgliedschaften, Partien oder Ausrüstungsdaten gelesen.',
              '- Vorschauen bleiben inert. Erstellen, Beitreten, Bereitschaft, Starten, Rückkehr, Autospeichern, Aktualisieren und Countdowns werden nicht ausgeführt.',
              '- Aufgenommene Darstellungszustände sind keine Prüfung der Spielübergänge oder aller möglichen laufenden Situationen.',
              '- Bisherige eigene Lobbyentwürfe und der vorhandene allgemeine Lobbyeditor bleiben verfügbar. Die aufgenommenen Spielquellen werden dadurch nicht editierbar.',
              '- Gemeinsame Prüfung und Anpassung sinnvoller Editoroptionen bleiben spätere Arbeit.', '',
              '## Aufnahme erneuern', '', '`python deploy/audit_lobby_coverage.py`', '',
              'Das Werkzeug liest ausschließlich lokale Quellen ohne App-/Datenbankimport oder Netzverbindung. '
              'Fehlende Zuordnungen führen zu einem fehlgeschlagenen Prüfergebnis.', '']
    (ROOT / 'docs/LOBBYS_BESTAND.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps(dict(uses=report['uses'], models=report['models'], component_calls=len(report['component_calls']), uncovered=report['uncovered'])))
    return bool(report['uncovered'])


if __name__ == '__main__':raise SystemExit(main())
