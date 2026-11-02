"""Canonical approved ivory-card renderer, shared by samples and full deck."""
from pathlib import Path
from base64 import b64encode
from functools import lru_cache
import hashlib
import json
import shutil

ROOT=Path(__file__).resolve().parents[3]
ART=Path(__file__).resolve().parent.parent/'card-front-drafts'
RANKS=('A','2','3','4','5','6','7','8','9','10','J','Q','K')
SUITS=('S','H','D','C')

SHAPES = {
    'S': 'M0-48C-12-30-48-8-48 18C-48 45-18 52-6 29C-6 43-10 52-24 58H24C10 52 6 43 6 29C18 52 48 45 48 18C48-8 12-30 0-48Z',
    'H': 'M0 48C-11 35-48 10-48-15C-48-46-15-53 0-29C15-53 48-46 48-15C48 10 11 35 0 48Z',
    'D': 'M0-53L32 0 0 53-32 0Z',
    'C': 'M-8 28C-32 51-59 28-45 6C-39-4-27-7-16-2C-33-35-15-53 0-53C15-53 33-35 16-2C27-7 39-4 45 6C59 28 32 51 8 28C7 43 13 51 25 56H-25C-13 51-7 43-8 28Z',
}

def pip(suit, x, y, size, rotation=0, **attributes):
    attrs=' '.join(f'{key}="{value}"' for key,value in attributes.items())
    return f'<path d="{SHAPES[suit]}" transform="translate({x} {y}) rotate({rotation}) scale({size/106})" {attrs}/>'

def front(rank, suit, artwork):
    ink = '#96372b' if suit in ('D', 'H') else '#292b22'
    corner = f'<text x="16" y="92" font-size="96" font-family="Georgia,serif" font-weight="700">{rank}</text>' + pip(suit,43,126,36)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="280" height="380" viewBox="0 0 280 380" role="img" aria-label="{rank}{suit} Kartenmuster">
<defs>
 <linearGradient id="paper" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#e4d6b9"/><stop offset=".27" stop-color="#f6eed9"/><stop offset=".7" stop-color="#f1e7cd"/><stop offset="1" stop-color="#dfcda8"/></linearGradient>
 <radialGradient id="edge"><stop offset=".65" stop-color="#836940" stop-opacity="0"/><stop offset="1" stop-color="#80613b" stop-opacity=".12"/></radialGradient>
 <filter id="grain"><feTurbulence type="fractalNoise" baseFrequency=".7" numOctaves="3" seed="13" stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/></filter>
 <clipPath id="outline"><rect x="1" y="1" width="278" height="378" rx="14"/></clipPath>
 <clipPath id="court"><rect x="53" y="64" width="174" height="126"/></clipPath>
</defs>
<g clip-path="url(#outline)">
 <rect x="1" y="1" width="278" height="378" rx="14" fill="url(#paper)"/>
 <rect width="280" height="380" fill="url(#edge)"/>
 <rect width="280" height="380" filter="url(#grain)" opacity=".042"/>
 <path d="M17 92V23Q17 17 23 17H92M188 17H257Q263 17 263 23V92M263 288V357Q263 363 257 363H188M92 363H23Q17 363 17 357V288" fill="none" stroke="#987c4c" stroke-width=".8" opacity=".5"/>
 <path d="M6 47V21Q6 6 21 6H50M230 6H259Q274 6 274 21V48M274 332V359Q274 374 259 374H230M50 374H21Q6 374 6 359V332" fill="none" stroke="#fff7df" stroke-width="1" opacity=".65"/>
 <g fill="{ink}">{corner}<g transform="translate(280 380) rotate(180)">{corner}</g>{artwork}</g>
</g><rect x="1" y="1" width="278" height="378" rx="14" fill="none" stroke="#9b8257" stroke-width="1.2"/>
</svg>'''

POSITIONS={
 '2':[(140,125),(140,255)],
 '3':[(140,125),(140,190),(140,255)],
 '4':[(92,125),(188,125),(92,255),(188,255)],
 '5':[(92,125),(188,125),(92,255),(188,255),(140,190)],
 '6':[(92,125),(188,125),(92,190),(188,190),(92,255),(188,255)],
 '7':[(92,125),(188,125),(92,190),(188,190),(92,255),(188,255),(140,157)],
 '8':[(92,125),(188,125),(92,190),(188,190),(92,255),(188,255),(140,157),(140,223)],
 '9':[(x,y) for y in (125,168,212,255) for x in (92,188)]+[(140,190)],
 '10':[(x,y) for y in (125,168,212,255) for x in (92,188)]+[(140,146),(140,234)],
}

@lru_cache(maxsize=3)
def court_image(rank):
 name={'J':'jack','Q':'queen','K':'king'}[rank]
 return 'data:image/png;base64,'+b64encode((ART/(name+'-court-v1.png')).read_bytes()).decode()

def artwork(rank,suit):
 if rank=='A':
  return pip(suit,140,194,133)+'<path d="M89 284Q140 297 191 284M116 296L140 304 164 296" fill="none" stroke="#9a7c43" stroke-width="1.2" opacity=".65"/>'
 if rank in POSITIONS:
  return ''.join(pip(suit,x,y,36 if rank in ('9','10') else 39,180 if y>190 else 0,**{'data-main-pip':'true'}) for x,y in POSITIONS[rank])
 upper=f'<g id="court-half" clip-path="url(#court)"><image x="55" y="62" width="170" height="255" href="{court_image(rank)}"/></g>'
 return upper+'<g transform="rotate(180 140 190)"><use href="#court-half"/></g>'+'<path d="M63 190L88 182H192L217 190 192 198H88Z" fill="#294137" stroke="#a58c52" stroke-width="1.2"/><path d="M121 190L140 183 159 190 140 197Z" fill="#c1a268"/>'

def render_card(code):
 rank,suit=code[:-1],code[-1]
 if rank not in RANKS or suit not in SUITS:raise ValueError('Invalid card code')
 return front(rank,suit,artwork(rank,suit))

def build_deck():
 out=ROOT/'static/cards/blackjack/fronts-ivory-v1';out.mkdir(parents=True,exist_ok=True)
 cards=[]
 for suit in SUITS:
  for rank in RANKS:
   code=rank+suit;path=out/(code+'.svg');path.write_text(render_card(code),encoding='utf-8')
   cards.append(dict(code=code,file=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
 for name in ('king','queen','jack'):shutil.copy2(ART/(name+'-court-v1.png'),out/(name+'-court-v1.png'))
 manifest=dict(name='Black Jack – Elfenbein',date='2026-10-31',approved_style=True,card_count=52,dimensions=[280,380],delivery_format='SVG',readability_revision=3,corner_rank_size=96,corner_suit_size=36,ranks=list(RANKS),suits=list(SUITS),cards=cards,canonical_renderer='offline-preview/blackjack-v1/card-fronts/render_deck.py',approved_samples=['AS','7D','KC'],court_art='three unchanged generated RGBA originals; same court per rank across all suits; SVG reuses the same half without duplicating the portrait',back='samtgruen-gold-140.webp unchanged',previous_deck='offline-preview/card-comparison-v1/assets/kenney retained',prompts=['offline-preview/blackjack-v1/card-front-drafts/'+name+'-art-prompt.txt' for name in ('king','queen','jack')])
 manifest['generation']=dict(mode='built-in image_gen',originals_unmodified=True,prompts={name:(ART/(name+'-art-prompt.txt')).read_text(encoding='utf-8') for name in ('king','queen','jack')})
 (out/'deck.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 return manifest

if __name__=='__main__':
 manifest=build_deck();print(str(ROOT/'static/cards/blackjack/fronts-ivory-v1'),manifest['card_count'],'cards')
