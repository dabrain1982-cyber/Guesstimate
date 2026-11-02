"""Finite equipment sets only. Question banks never create card records."""
import ast
from copy import deepcopy
import importlib.util
import json
from types import SimpleNamespace
from library_store import ROOT
WORLD='static/conquest/world.json'
CONQUEST_JS='offline-preview/conquest-2-5d-v1/'
SUITS={'clubs':('Clubs','Kreuz'),'spades':('Spades','Pik'),'hearts':('Hearts','Herz'),'diamonds':('Diamonds','Karo')}
RANKS={'A':'Ass','K':'König','Q':'Dame','J':'Bube'}
def read(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def standard_sets():
    tree=ast.parse((ROOT/'card_table.py').read_text(encoding='utf-8'));scope={}
    for node in tree.body:
        if isinstance(node,ast.Assign):
            for target in node.targets:
                if isinstance(target,ast.Name) and target.id in ('CARD_TABLE_DECKS','SUITS','RANKS'):scope[target.id]=ast.literal_eval(node.value)
    factory=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_build_deck')
    module=ast.Module(body=[ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0),factory],type_ignores=[])
    scope['secrets']=SimpleNamespace(SystemRandom=lambda:SimpleNamespace(shuffle=lambda rows:None))
    exec(compile(ast.fix_missing_locations(module),'card_table.py::_build_deck','exec'),scope)
    result=[]
    for size in scope['CARD_TABLE_DECKS']:
        members=[]
        for row in scope['_build_deck'](size):
            if row['joker']:key,name='Joker','Joker '+row['id'].split('-')[-1]
            else:
                suit,label=SUITS[row['suit']];key=suit+row['rank'];name=label+' '+RANKS.get(row['rank'],row['rank'])
            if size>55:name+=' · Satz '+row['id'][1]
            members.append(dict(id=row['id'],name=name,key=key,original={k:row[k] for k in ('id','rank','suit','symbol','color','joker')}))
        jokers=sum(m['original']['joker'] for m in members)
        label=f'{size-jokers} Karten'+(f' + {jokers} Joker' if jokers else '')
        result.append(dict(key='standard-'+str(size),name=label,game='Playtable',family='standard-set',members=members,supplements=[],evidence=['card_table.py']))
    return result

def conquest_sets():
    world=read(WORLD)
    spec=importlib.util.spec_from_file_location('workshop_conquest_metadata',ROOT/'conquest_cards.py')
    metadata=importlib.util.module_from_spec(spec);spec.loader.exec_module(metadata)
    lands,jokers=[],[]
    for row in metadata.catalog(world).values():
        content=dict(kind='country',category='Länderkarte',game='Conquest',title=row['name'],prompt=row['type'],country=deepcopy(row),description='Ersetzt jedes Symbol' if row['symbol']=='wild' else 'Besitz und Eintauschbonus werden erst im Spiel bestimmt.')
        entry=dict(id=row['id'],name=row['name']+' · '+row['type'],content=content,original=deepcopy(row))
        (jokers if row['symbol']=='wild' else lands).append(entry)
    missions=[dict(id=r['id'],name=r['text'],original=deepcopy(r),content=dict(kind='mission',category='Geheimer Auftrag',game='Conquest',title='Dein Auftrag',prompt=r['text'])) for r in world['missions']]
    return [dict(key='conquest-countries',name='Conquest · 42 Länderkarten',game='Conquest',family='conquest-set',members=lands,supplements=jokers,evidence=[WORLD,'conquest_cards.py',CONQUEST_JS+'cards.js',CONQUEST_JS+'territory-model.js',CONQUEST_JS+'assets/karte.png']),dict(key='conquest-missions',name='Conquest · 12 Aufträge',game='Conquest',family='conquest-set',members=missions,supplements=[],evidence=[WORLD,'conquest.py',CONQUEST_JS+'turn-controls.js'])]