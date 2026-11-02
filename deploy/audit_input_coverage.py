"""Rebuild source-backed local input inventory; no app/DB or game actions."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'offline-preview/game-workshop-v1'))
from source_inputs import SourceInputs


def main():
    report = SourceInputs().report()
    (ROOT / 'docs/EINGABEN_BESTAND.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    groups = {}
    for asset in report['assets']:
        groups.setdefault(asset['model_id'], []).append(asset)
    lines = ['# Eingaben in der lokalen Werkstatt', '',
             f'{report["uses"]} Einsatzvarianten in {report["models"]} Modellen. Stand: 26.10.2026.', '',
             'Bibliothek → Eingaben bietet Suche sowie Filter nach Spiel und Eingabeart. Gemeinsame Modelle '
             'halten Beschriftungen, Grenzen und Zustände als einzeln auswählbare Varianten fest. '
             'Eine konkrete Variante kann in mehreren Projektmappen gesammelt und mit vollständigem Original, '
             'gerendertem Beispiel und Quellen übergeben werden.', '',
             '| Modell | Varianten | Spiele / Einsatz | Eingabearten |', '|---|---:|---|---|']
    for entries in groups.values():
        lines.append('| ' + entries[0]['model_name'] + ' | ' + str(len(entries)) + ' | ' +
                     ', '.join(sorted({a['game'] for a in entries})) + ' | ' +
                     ', '.join(sorted({a['family_name'] for a in entries})) + ' |')
    lines += ['', '## Herkunft und gemeinsame Vorschau', '',
              'source_inputs.py verwendet denselben Originalquellen- und Vorschauweg wie source_windows.py. '
              'Originalvorlagen, umgebende Beschriftungen, Styles und Schranken wie min, max, maxlength, '
              'required oder disabled werden mit neutralen Beispieldaten aufgenommen. Eine gemeinsame '
              'Grundklasse begründet ein Modell; unterschiedliche Einsatzgestaltungen bleiben Varianten. '
              'Die Spiele und ihre Eingabekomponenten werden nicht umgebaut oder nachgezeichnet.', '',
              f'Der Bericht ordnet alle {len(report["source_controls"])} nativen bzw. rollenbasierten '
              'Quellkontrollen in den verbundenen Vorlagen und der aktuellen Conquest-Oberfläche zu. '
              'Schleifen erzeugen im Spiel mehrere Instanzen; diese Zahl zählt Quellstellen. '
              'Zuordnen und Sortieren sind zusätzlich als zusammenhängende Auswahlen aufgenommen.', '',
              '## Grenzen und spätere Aufgaben', '',
              '- Die Vorschau ist inert. Eingaben, Sortieren, Validierung, automatisches Speichern und Spielaktionen werden nicht ausgeführt.',
              '- PIN-Felder bleiben leer. Keine Zugangsdaten, Spielerantworten, Konten oder Spielstände werden gelesen.',
              '- Versteckte Übertragungsfelder und CSRF-Werte sind keine gestaltbaren Bibliothekselemente.',
              '- Native Auswahllisten und Regler behalten die Darstellung des jeweiligen Browsers.',
              '- Zustandsabhängige Grenzen werden im Spiel berechnet; aufgenommen sind die kenntlich gemachten neutralen bzw. ursprünglichen Zustände.',
              '- Ein Eingabeeditor und die gemeinsame Prüfung sinnvoller Editoroptionen bleiben spätere Arbeit.', '',
              '## Aufnahme erneuern', '', '`python deploy/audit_input_coverage.py`', '',
              'Erneuert diesen Bericht und EINGABEN_BESTAND.json ausschließlich aus lokalen Quellen. '
              'Fehlende Zuordnungen führen zu einem fehlgeschlagenen Prüfergebnis.', '']
    (ROOT / 'docs/EINGABEN_BESTAND.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps(dict(uses=report['uses'], models=report['models'], controls=len(report['source_controls']),
                         uncovered=report['uncovered']), ensure_ascii=False))
    return bool(report['uncovered'])


if __name__ == '__main__':
    raise SystemExit(main())
