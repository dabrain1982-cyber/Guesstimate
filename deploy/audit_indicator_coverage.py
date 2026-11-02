"""Rebuild the local display inventory without importing games or their DBs."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'offline-preview/game-workshop-v1'))
from source_indicators import SourceIndicators


def main():
    report = SourceIndicators().report()
    (ROOT / 'docs/ANZEIGEN_BESTAND.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    groups = {}
    for a in report['assets']:
        groups.setdefault(a['model_id'], []).append(a)
    lines = ['# Anzeigen in der lokalen Werkstatt', '',
             f'{report["uses"]} Einsatzvarianten in {report["models"]} Modellen. Stand: 27.10.2026.', '',
             'Unter Bibliothek → Anzeigen nach Spiel, Anzeigeart oder Text filtern. Gemeinsame Modelle '
             'halten die konkreten Inhalte, Werte, Einheiten und Zustände als einzelne Varianten fest. '
             'Jede Variante kann in mehreren Projektmappen gesammelt und mit vollständigem Original, '
             'Beispieldarstellung und Quellen übergeben werden.', '',
             '| Modell | Varianten | Spiele / Einsatz | Anzeigearten |', '|---|---:|---|---|']
    for entries in groups.values():
        lines.append('| ' + entries[0]['model_name'] + ' | ' + str(len(entries)) + ' | ' +
                     ', '.join(sorted({a['game'] for a in entries})) + ' | ' +
                     ', '.join(sorted({a['family_name'] for a in entries})) + ' |')
    lines += ['', '## Gemeinsame Quellen und Varianten', '',
              'source_indicators.py verwendet denselben Quellen-, Vorschau- und Speicherweg wie Fenster und Eingaben. '
              'Vorhandene Vorlagen, Makros, Styles und DOM-Fabriken bleiben maßgeblich. Ganze Spielerfenster und '
              'kompakte Armeebausteine behalten ihre ursprüngliche Innenkomposition. Gemeinsame Komponenten '
              'begründen die Modellzuordnung; bloß gleiche Zahlen oder Einheiten führen nicht zu einer Angleichung.', '',
              'Die Quellenprüfung erfasst explizite Status-/Alarm-/Fortschrittsrollen, Live-Bereiche, Ausgaben '
              'und Timerkennungen im verbundenen Bestand. Alle sind einer Anzeige oder einer begründeten '
              'Abgrenzung zugeordnet. Zusätzlich sind sichtbare Punkte-, Status- und Zählerklassen sowie '
              'dynamisch erzeugte Werte anhand ihrer tatsächlichen Spielquellen aufgenommen. Quellstellen '
              'zählen keine während des Spiels vervielfachten Bildschirmexemplare.', '',
              'Dynamische Beispiele werden mit deploy/capture_generated_indicators.mjs aus den Originalfabriken '
              'erfasst: Kniffelblock/Wurfanzeigen, Wurfnotizen, Mäxchen-Leben, Würfelergebnisse, öffentliche '
              'Armeewerte und Kampfwürfel. Die Zeitpunkte verwenden die vorhandene Berechnungsfunktion. '
              'Prüfsummen binden die Beispiele an diese Quellen; veraltete Erfassungen werden abgewiesen.', '',
              '## Grenzen und spätere Aufgaben', '',
              '- Werte und Zeitstände sind neutrale, feste Beispiele. Es läuft kein Spieltimer, keine Punktevergabe und keine Spielaktion.',
              '- Es werden keine Konten, Ergebnisse, gespeicherten Partien, privaten Aufträge oder aktuellen Spielerwerte gelesen.',
              '- Die Party-Ergebnisliste ist als vorhandener Altbestand aufgenommen; eine neue Podiumgestaltung ist damit weder umgesetzt noch freigegeben.',
              '- Reine assistive Statuskanäle erhalten einen Quellnachweis. Es wird daraus keine erfundene sichtbare Gestaltung gebaut.',
              '- Native/browserabhängige Darstellung und vorhandene spielabhängige Unterschiede bleiben erhalten.',
              '- Anzeigeeditor, Animationen, Klangentscheidungen und die gemeinsame Prüfung sinnvoller Editoroptionen bleiben spätere Arbeit.', '',
              '## Aufnahme erneuern', '', '`node deploy/capture_generated_indicators.mjs`', '',
              '`python deploy/audit_indicator_coverage.py`', '',
              'Beide Werkzeuge arbeiten ausschließlich lokal ohne Anwendungs-/Datenbankimport oder Netzverbindung. '
              'Fehlende Zuordnungen führen zu einem fehlgeschlagenen Prüfergebnis.', '']
    (ROOT / 'docs/ANZEIGEN_BESTAND.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps(dict(uses=report['uses'], models=report['models'], semantic_sources=len(report['semantic_sources']),
                         uncovered=report['uncovered']), ensure_ascii=False))
    return bool(report['uncovered'])


if __name__ == '__main__':
    raise SystemExit(main())
