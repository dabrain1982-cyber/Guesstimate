"""Rebuild local player-component inventory without game or database imports."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'offline-preview/game-workshop-v1'))
from source_players import SourcePlayers


def main():
    report = SourcePlayers().report()
    (ROOT / 'docs/SPIELER_BESTAND.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    groups = {}
    for a in report['assets']:groups.setdefault(a['model_id'], []).append(a)
    lines = ['# Spieleranzeigen und Pulte in der lokalen Werkstatt', '',
             f'{report["uses"]} Einsatzvarianten in {report["models"]} Modellen. Stand: 27.10.2026.', '',
             'Bibliothek → Spieleranzeigen & Pulte bietet Suche sowie Spiel- und Bausteinfilter. '
             'Gemeinsame Komponenten stehen als Modell zusammen; Rollen, Zustände und Pultmotive bleiben '
             'einzeln auswählbar und mehreren Projekten zuordenbar. Gespeicherte Projektstände und lokale '
             'Übergaben bewahren die konkrete Variante mit Originalfragment, Beispieldarstellung und Quellprüfsummen.', '',
             '| Modell | Varianten | Spiele / Einsatz | Bausteine |', '|---|---:|---|---|']
    for rows in groups.values():
        lines.append('| ' + rows[0]['model_name'] + ' | ' + str(len(rows)) + ' | ' +
                     ', '.join(sorted({a['game'] for a in rows})) + ' | ' + ', '.join(sorted({a['family_name'] for a in rows})) + ' |')
    lines += ['', '## Gemeinsame Quellen und Zuordnung', '',
              'source_players.py verwendet den gemeinsamen Quellen-, Vorschau- und Speicherweg von Fenstern, '
              'Eingaben und Anzeigen. Die vollständige Profilbühne kommt aus _profile_window.html; '
              'Lobbyplätze aus _lobby_room.html. Perfect- und Würfelrahmen bleiben ihre vorhandenen '
              'Spielvarianten. Die Ranglisten lesen _leaderboard.html und _player_identity.html. '
              'Pultauswahl bewahrt die 14 registrierten Familien im Profil und die 13 angebotenen Shopmotive; dieselben 14 '
              'Familien sind im vollständigen Profilfenster auswählbar. Das sind vorhandene '
              'Ausstattungsbeispiele, keine Änderungen persönlicher Ausrüstung.', '',
              'Kompakte Conquest-Porträts werden durch die tatsächliche createPlayerPortrait-Fabrik erzeugt. '
              'Die vorhandenen public_portrait/register_portraits-Funktionen liefern Bildausschnitt und '
              'Sichtbarkeitsregeln für alle 19 registrierten Avatare. Die Aufnahme führt ausschließlich '
              'diese reinen Funktionen in einem neutralen Kontext aus; keine Flask-Anwendung oder '
              'Datenbank wird gestartet. Eigener Startavatar und öffentliche Darstellung bleiben getrennt. '
              'Test- und neutrale Armeen behalten ihre buchstabenbasierte Darstellung. '
              'Armee- und Siegerporträt sind zwei Verwendungen derselben Fabrik.', '',
              f'Die Quellenprüfung ordnet {len(report["component_uses"])} verbundene Makroaufrufe sowie '
              f'{len(report["source_hooks"])} Spieler-/Pultquellstellen zu. Dynamische Fabrikbeispiele: '
              f'{report["factory_examples"]}. Es fehlen keine Zuordnungen im geprüften Bestand. '
              'Gleiche Zahlen oder ähnliche Optik allein begründen keine Zusammenfassung.', '',
              '## Grenzen und spätere Aufgaben', '',
              '- Ausschließlich neutrale feste Beispiele; keine Konten, echten Spielernamen, Ergebnisse oder Partien gelesen.',
              '- Profilfenster und Porträts behalten ihre gesamte ursprüngliche Innenkomposition. Äußere Vorschauplätze ersetzen den Spielrahmen; die Werkstatt skaliert die ganze Vorschau proportional.',
              '- Playtable behält reine Namenspulte. Kein Porträteinbau am Kartentisch und keine zusätzlichen Avatare in laufenden Quizfragen oder Countdowns.',
              '- Die Party-Ergebnispulte sind vorhandener Altbestand; ihre Aufnahme ist keine neue Gestaltungsfreigabe.',
              '- Kartenflächen, Würfelpulte und Werte können zusätzlich in ihren eigenen Elementfamilien erscheinen. Die Vorschau liest jeweils dieselbe Originalquelle.',
              '- Skripte, automatische Textanpassung, Ausrüstungswechsel und Spielaktionen laufen in diesen inerten Beispielen nicht.',
              '- Spielereditor und gemeinsame Prüfung sinnvoller Editoroptionen bleiben spätere Aufgaben.', '',
              '## Aufnahme erneuern', '', '`node deploy/capture_generated_players.mjs`', '',
              '`python deploy/audit_player_coverage.py`', '',
              'Beide Werkzeuge arbeiten ausschließlich lokal. Veraltete Fabrikquellen werden abgewiesen; '
              'fehlende Zuordnungen lassen die Quellenprüfung fehlschlagen.', '']
    (ROOT / 'docs/SPIELER_BESTAND.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps(dict(uses=report['uses'], models=report['models'], component_uses=len(report['component_uses']),
                         source_hooks=len(report['source_hooks']), uncovered=report['uncovered'])))
    return bool(report['uncovered'])


if __name__ == '__main__':raise SystemExit(main())
