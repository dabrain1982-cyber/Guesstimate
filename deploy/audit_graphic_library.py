"""Reproduce the local artwork/flyer/icon inventory without application imports."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'offline-preview/game-workshop-v1'))
from source_buttons import SourceButtons
from graphic_library import GraphicLibrary

if __name__=='__main__':
    report=GraphicLibrary(SourceButtons()).report()
    (ROOT/'docs/BILDBAUSTEINE_BESTAND.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report['areas'],ensure_ascii=False))
