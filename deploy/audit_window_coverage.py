"""Rebuild the local window inventory without opening the app or game data."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'offline-preview/game-workshop-v1'))
from source_windows import SourceWindows


def main():
    report = SourceWindows().report()
    (ROOT / 'docs/FENSTER_BESTAND.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    groups = {}
    for asset in report['assets']:
        groups.setdefault(asset['model_id'], []).append(asset)
    lines = ['# Fenster in der lokalen Werkstatt', '',
             f'{report["uses"]} Verwendungen in {report["models"]} gemeinsamen Modellen. Stand: 26.10.2026.', '',
             'Unter Bibliothek → Fenster nach Spiel, Fensterart oder Text suchen. Ansehen öffnet die konkrete Variante; '
             'bei gemeinsamen Modellen bleiben Spiel, Inhalt und Zustand einzeln auswählbar. Jede Variante lässt sich '
             'mehreren Projektmappen zuordnen. Projektstände und Übergaben enthalten vollständige Momentaufnahmen '
             'mit Originalfragment, gerendertem Beispiel, Quellen und Prüfsummen.', '',
             '| Modell | Varianten | Spiele / Einsatz | Fensterarten |', '|---|---:|---|---|']
    for assets in groups.values():
        lines.append('| ' + assets[0]['model_name'] + ' | ' + str(len(assets)) + ' | ' +
                     ', '.join(sorted({a['game'] for a in assets})) + ' | ' +
                     ', '.join(sorted({a['family_name'] for a in assets})) + ' |')
    lines += ['', '## Quellen und Gruppierung', '',
              'Gemeinsame Modelle verweisen auf vorhandene Komponenten bzw. ihre gemeinsame CSS-Grundklasse. '
              'Unterschiedliche Inhalte und Gestaltungen bleiben getrennte Varianten; ähnliche Optik allein führt '
              'nicht zur Zusammenführung. Die Spiele werden dadurch nicht umgebaut.', '',
              'Die Aufnahme folgt den aktuell verbundenen Seitenvorlagen und der aktuellen Conquest-Tischoberfläche. '
              'Alle dort gefundenen HTML-Dialoge sind zugeordnet. Regelvarianten für Perfect und Conquest stammen '
              'aus Übersicht bzw. Lobby; deren eigenständige laufende Spielseiten enthalten diesen Dialog nicht. '
              'Playtable, Würfeltisch und Kniffel verwenden im vorhandenen allgemeinen Regeldialog den bisherigen '
              'allgemeinen Text. Die Aufnahme ergänzt keine neuen Regeln.', '',
              'Die Vorschau verwendet die ursprünglichen Vorlagen, Makros und Styles mit neutralen Beispieldaten. '
              'Dynamische Karten, Würfel und Kniffelblock werden aus den tatsächlichen DOM-Fabriken erfasst. '
              'Nur Platzierung und die proportionale Skalierung der gesamten Vorschau werden an die Werkstatt '
              'angepasst. Interne responsive Kompositionen werden nicht kopiert.', '',
              '## Grenzen und spätere Aufgaben', '',
              '- Noch kein Fenstereditor; dessen sinnvolle Optionen klären wir später gemeinsam.',
              '- Vorschauen sind nicht bedienbare Komponentenbeispiele. Spielaktionen, Kontenanbindung und '
              'laufzeitabhängige Button-Mounts werden dort nicht ausgeführt.',
              '- Native Bestätigungsfenster des Browsers in Perfect und Playtable sind Verhalten des Browsers '
              'und keine frei gestaltbare HTML-Fenstervorlage.',
              '- Das alte Conquest-Inventar aus static/conquest-table.js ist nicht eingebunden und bleibt als Altbestand abgegrenzt.',
              '- Porträts, vollständige Lobbys und Spielflächen, einzelne Karten, Eingabefelder, Timer und '
              'Ladeanzeigen behalten ihre eigenen Elementfamilien.', '',
              '## Aufnahme erneuern', '',
              '`node deploy/capture_generated_windows.mjs`', '',
              '`python deploy/audit_window_coverage.py`', '',
              'Die erste Anweisung erfasst ausschließlich reine lokale DOM-Fabriken in einer Umgebung ohne Netzwerk '
              'oder Spielhandler. Die zweite erneuert diesen Bericht und FENSTER_BESTAND.json. '
              'Anwendung und Spieldatenbanken werden nicht importiert oder geöffnet.', '']
    (ROOT / 'docs/FENSTER_BESTAND.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('uses', 'models', 'games', 'missing_dialogs')}, ensure_ascii=False))
    return 1 if report['missing_dialogs'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
