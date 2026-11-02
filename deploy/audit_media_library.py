"""Reproduce the local free lettering and sound selection report."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'offline-preview/game-workshop-v1'))
from media_library import MediaLibrary
if __name__=='__main__':
    report=MediaLibrary().report();(ROOT/'docs/KLAENGE_SCHRIFTEN_AUSWAHL.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(len(report['fonts']),'Schriftstile,',len(report['sounds']),'Klänge, nur lokale freie Quellen.')
