"""Document approved card foundations without opening the application or a DB."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'offline-preview/game-workshop-v1'))
from card_library import CardLibrary


if __name__ == '__main__':
    report = CardLibrary().report()
    (ROOT/'docs/KARTEN_GRUNDLAGEN.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(f'{report["models"]} Grundmodelle, {report["library_entries"]} Einträge, {report["finite_sets"]} endliche Sätze; keine Frageeinträge. Editorprüfung offen.')
