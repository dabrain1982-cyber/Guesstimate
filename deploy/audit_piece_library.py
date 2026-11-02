"""Write the local piece inventory without application or database imports."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'offline-preview/game-workshop-v1'))
from piece_library import PieceLibrary

if __name__=='__main__':
    report=PieceLibrary().report()
    (ROOT/'docs/SPIELSTEINE_GRUNDLAGEN.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(len(report['models']),'Formfamilien,',len(report['configurations']),'Konfigurationen,',len(report['coverage']),'Spiele geprüft. Editoroptionen offen.')
