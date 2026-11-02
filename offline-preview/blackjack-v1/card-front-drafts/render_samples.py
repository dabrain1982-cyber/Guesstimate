"""Compatibility entry point: rebuild the shared current card set, keep old samples."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'card-fronts'))
from render_deck import build_deck
if __name__=='__main__':
 build_deck()
 print('/static/blackjack-kartenmuster-v1.html')
