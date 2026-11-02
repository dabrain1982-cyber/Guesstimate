"""Document the two board variants and finite source configurations, local only."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'offline-preview/game-workshop-v1'))
from board_library import BoardLibrary

if __name__=='__main__':
    report=BoardLibrary().report()
    (ROOT/'docs/BRETTER_GRUNDLAGEN.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('2 Grundvarianten,',len(report['configurations']),'Konfigurationen,',len(report['coverage']),'Spiele geprüft. Editoroptionen offen.')
