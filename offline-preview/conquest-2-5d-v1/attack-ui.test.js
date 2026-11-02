import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createAttackControls, comicArrowPath, enemyTargets} from './attack.js';
import {createPreviewTurn} from './turn-model.js';
import {buildPreviewTerritories} from './territory-model.js';

const world=JSON.parse(readFileSync(new URL('./assets/world.json',import.meta.url)));
function fixture({source=6,customTurn=null}={}){
  const nodes=new Map(),previous=globalThis.document;
  let opened=0;
  class Element{
    constructor(){this.dataset={};this.attributes=new Map();this.events=new Map();this.style={setProperty(){}};this.children=[];}
    addEventListener(key,value){this.events.set(key,value);}
    setAttribute(key,value){this.attributes.set(key,value);}
    replaceChildren(...values){this.children=values;}
    focus(){} showModal(){opened++;}
  }
  const node=key=>{if(!nodes.has(key))nodes.set(key,new Element());return nodes.get(key);};
  const buttons=[1,2,3].map(value=>{const el=new Element();el.dataset.diceCount=String(value);return el;});
  globalThis.document={querySelector:node,querySelectorAll:selector=>selector==='[data-dice-count]'?buttons:[],createElement:()=>new Element()};
  const territories=buildPreviewTerritories(world);
  territories.find(row=>row.id==='venezuela').armies=source;
  territories.find(row=>row.id==='brasilien').armies=3;
  const turn=customTurn||createPreviewTurn(territories,{total:0});
  if(!customTurn)turn.advance();
  let controls;
  controls=createAttackControls({turn,territories,onChange:()=>controls.sync(),onOccupy(){}});
  return {turn,controls,node,buttons,get opened(){return opened;},pick:id=>controls.selected(territories.find(row=>row.id===id)),dispose(){globalThis.document=previous;}};
}

test('Country selection stays on the board and starts each new choice at the maximum dice',()=>{
  const f=fixture();try{
    f.pick('venezuela');assert.equal(f.controls.maxDice,3);assert.equal(f.controls.diceCount,3);
    assert.equal(f.controls.targetId,null);assert.equal(f.node('#roll-attack').hidden,true);
    f.pick('brasilien');assert.equal(f.opened,0);assert.equal(f.node('#roll-attack').hidden,false);
    f.controls.chooseDice(1);f.controls.sync();assert.equal(f.controls.diceCount,1,'Polling must preserve a manual choice');
    f.pick('brasilien');assert.equal(f.controls.hasAction,false,'Clicking the target again deselects it');
    f.pick('brasilien');assert.equal(f.controls.diceCount,3);
    f.controls.clear();f.controls.sync();assert.equal(f.controls.sourceId,null);
  }finally{f.dispose();}
});
test('Wheel and keyboard choose bounded quantities without executing an attack',()=>{
  const f=fixture();try{
    f.pick('venezuela');f.pick('brasilien');
    const before=f.turn.troops('brasilien');let prevented=0,stopped=0;
    const wheel=deltaY=>f.node('#attack-dice-choice').events.get('wheel')({deltaY,preventDefault(){prevented++;},stopPropagation(){stopped++;}});
    wheel(100);assert.equal(f.controls.diceCount,2);wheel(100);wheel(100);assert.equal(f.controls.diceCount,1);
    wheel(-100);assert.equal(f.controls.diceCount,2);
    const key=value=>f.node('#attack-dice-choice').events.get('keydown')({key:value,preventDefault(){}});
    key('End');assert.equal(f.controls.diceCount,3);key('Home');assert.equal(f.controls.diceCount,1);
    assert.equal(prevented,4);assert.equal(stopped,4);assert.equal(f.turn.troops('brasilien'),before);
    assert.equal(f.buttons[0].attributes.get('aria-checked'),'true');
  }finally{f.dispose();}
});
test('The garrison determines the dice limit; a single troop never offers an attack',()=>{
  for(const [source,expected] of [[1,0],[2,1],[3,2],[4,3]]){
    const f=fixture({source});try{
      f.pick('venezuela');assert.equal(f.controls.diceCount,expected);
      f.controls.chooseDice(4);assert.equal(f.controls.diceCount,expected);
      if(source===1){assert.deepEqual(f.controls.targets,[]);assert.equal(f.node('#attack-dice-choice').hidden,true);}
    }finally{f.dispose();}
  }
});
test('Friendly neighbours are excluded even if an adapter includes one among its targets',()=>{
  const turn={phase:'attack',troops:()=>6,owner:id=>id==='enemy'?'red':'gold',attackTargets:()=>['friend','enemy']};
  assert.deepEqual(enemyTargets(turn,'source'),['enemy']);
  turn.phase='fortify';assert.deepEqual(enemyTargets(turn,'source'),[]);
});
test('A pending defense restores both countries and the submitted dice after reload',async()=>{
  let calls=0;
  const turn={isRemote:true,canAct:true,phase:'attack',ownerId:'gold',
    battleRequest:{from:'venezuela',to:'brasilien',defender:'red',dice:2},
    troops:id=>id==='venezuela'?6:3,owner:id=>id==='venezuela'?'gold':'red',
    attackTargets:()=>[],attack(){calls++;}};
  const f=fixture({customTurn:turn});try{
    f.controls.sync();assert.equal(f.controls.sourceId,'venezuela');assert.equal(f.controls.targetId,'brasilien');
    assert.equal(f.controls.diceCount,2);assert.equal(f.node('#roll-attack').disabled,true);
    f.controls.chooseDice(1);await f.controls.perform();assert.equal(calls,0);assert.equal(f.controls.diceCount,2);
    assert.match(f.node('#battle-outcome').textContent,/automatisch/);
  }finally{f.dispose();}
});
test('A press executes once, locks during the request and displays the result inline',async()=>{
  let resolve,calls=0,submitted;
  const turn={isRemote:true,canAct:true,phase:'attack',ownerId:'gold',
    troops:id=>id==='venezuela'?6:3,owner:id=>id==='venezuela'?'gold':'red',
    attackTargets:id=>id==='venezuela'?['brasilien']:[],
    attack(from,to,dice){calls++;submitted={from,to,dice};return new Promise(done=>{resolve=done;});}};
  const f=fixture({customTurn:turn});try{
    f.pick('venezuela');f.pick('brasilien');f.controls.chooseDice(2);
    const pending=f.controls.perform();await f.controls.perform();assert.equal(calls,1);assert.equal(f.node('#roll-attack').disabled,true);
    resolve({sequence:1,attackRolls:[6,2],defenseRolls:[5,3],attackerLoss:1,defenderLoss:1,conquered:false});await pending;
    assert.deepEqual(submitted,{from:'venezuela',to:'brasilien',dice:2});
    assert.equal(f.node('#battle-result').hidden,false);assert.equal(f.opened,0);
    assert.equal(f.controls.diceCount,3);assert.equal(f.node('#roll-attack').disabled,false);
    assert.equal(f.node('#attacker-rolls').children.length,2);
    assert.match(f.node('#battle-summary').textContent,/Angriff 1 · Verteidigung 1/);
  }finally{f.dispose();}
});
test('Projected comic arrows remain finite in every direction and omit collapsed segments',()=>{
  for(let angle=0;angle<360;angle+=15){
    const radians=angle*Math.PI/180,shape=comicArrowPath(200,200,200+Math.cos(radians)*90,200+Math.sin(radians)*90);
    assert(shape.body.endsWith(' Z'));assert(!/NaN|Infinity/.test(shape.body+shape.shine));
  }
  assert.equal(comicArrowPath(1,1,1,1),null);assert.equal(comicArrowPath(0,0,5,0),null);
});

test('Automatic defense has no controls and its result survives phase and turn changes',()=>{
  const turn={isRemote:true,canAct:false,phase:'attack',ownerId:'red',inventoryOwnerId:'gold',
    troops:id=>id==='venezuela'?4:2,owner:id=>id==='venezuela'?'red':'gold',attackTargets:()=>[]};
  const f=fixture({customTurn:turn});try{
    f.controls.sync();
    turn.lastBattle={sequence:1,from:'venezuela',to:'brasilien',attackerId:'red',defenderId:'gold',
      attackRolls:[5,3],defenseRolls:[6,4],attackerLoss:2,defenderLoss:0,conquered:false};
    f.controls.sync();
    assert.equal(f.opened,0);assert.equal(f.node('#roll-attack').hidden,true);
    assert.equal(f.node('#attack-dice-choice').hidden,true);
    assert.equal(f.node('#battle-result').hidden,false);
    assert.match(f.node('#battle-outcome').textContent,/Brasilien: Angriff abgewehrt/);
    assert.equal(f.node('#defender-rolls').children.length,2);
    turn.phase='fortify';f.controls.sync();
    assert.equal(f.node('#battle-result').hidden,false);
    turn.lastBattle=null;turn.phase='reinforce';f.controls.clear({keepDefense:true});f.controls.sync();
    assert.match(f.node('#battle-outcome').textContent,/abgewehrt/);
    assert.equal(f.node('#battle-result').hidden,false);
  }finally{f.dispose();}
});

test('A lost country is reported even if polling first observes the fortify phase',()=>{
  const turn={isRemote:true,canAct:false,phase:'attack',ownerId:'red',inventoryOwnerId:'gold',
    troops:()=>3,owner:()=> 'red',attackTargets:()=>[]};
  const f=fixture({customTurn:turn});try{
    f.controls.sync();turn.phase='fortify';
    turn.lastBattle={sequence:1,from:'venezuela',to:'brasilien',attackerId:'red',defenderId:'gold',
      attackRolls:[6,5],defenseRolls:[2],attackerLoss:0,defenderLoss:1,conquered:true};
    f.controls.sync();
    assert.match(f.node('#battle-outcome').textContent,/Brasilien verloren/);
    assert.equal(f.node('#battle-result').hidden,false);assert.equal(f.node('#roll-attack').hidden,true);
    assert.equal(f.opened,0);
  }finally{f.dispose();}
});
