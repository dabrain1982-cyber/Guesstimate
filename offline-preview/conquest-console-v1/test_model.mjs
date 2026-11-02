import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createExample,act,maxMove,ownTurn} from './model.js';

test('Verstärkungen müssen vollständig verteilt werden; Auswahl ist auf eigene Länder beschränkt',()=>{
  let state=createExample();const initial=structuredClone(state);
  assert.throws(()=>act(state,'advance'),/alle/);
  assert.throws(()=>act(state,'select',{country:'nordafrika'}),/eigenes/);
  state=act(state,'select',{country:'peru'});
  for(let i=0;i<6;i++)state=act(state,'place');
  assert.equal(state.board.peru.armies,10);assert.equal(state.board.westeuropa.armies,8);
  assert.equal(state.remaining,0);assert.equal(state.totals[0],48);assert.equal(state.placed,6);
  assert.throws(()=>act(state,'place'));
  assert.equal(act(state,'advance').phase,'attack');
  assert.deepEqual(initial,createExample(),'Ausgangsstand darf nicht verändert werden');
});
test('Angriffsbeispiel passt zu den gezeigten Würfeln und kann nur einmal laufen',()=>{
  const state=createExample('attack'),next=act(state,'attack-demo');
  assert.equal(next.board.nordafrika.armies,1);assert.equal(next.totals[1],35);
  assert.equal(next.board.westeuropa.armies,14);assert.equal(state.board.nordafrika.armies,3);
  assert.throws(()=>act(next,'attack-demo'),/bereits/);
  assert.equal(act(next,'advance').phase,'fortify');
});
test('Festigen lässt eine Truppe zurück, erhält die Gesamtzahl und ist einmal pro Zug erlaubt',()=>{
  const state=createExample('fortify');
  for(const count of [0,-1,1.5,14,NaN])assert.throws(()=>act(state,'fortify',{count}));
  const next=act(state,'fortify',{count:maxMove(state)});
  assert.equal(next.board.westeuropa.armies,1);assert.equal(next.board.suedeuropa.armies,19);
  assert.deepEqual(next.totals,state.totals);assert.throws(()=>act(next,'fortify',{count:1}),/einmal/);
});
test('Abschluss und explizite Übergabe sind getrennte Schritte',()=>{
  let state=createExample('fortify');assert.throws(()=>act(state,'pass'),/zuerst/);
  state=act(state,'end');assert.equal(state.phase,'ended');assert.equal(state.actor,0);
  assert.throws(()=>act(state,'place'));state=act(state,'pass');
  assert.equal(state.actor,1);assert.equal(state.turn,8);assert.equal(state.phase,'reinforce');assert.equal(ownTurn(state),false);
  for(const action of ['place','advance','attack-demo','fortify','end','pass'])assert.throws(()=>act(state,action,{count:1}),/wartest/);
});
test('Vollständiger Beispielzug erhält konsistente Zähler',()=>{
  let state=createExample();for(let i=0;i<6;i++)state=act(state,'place');
  state=act(state,'advance');state=act(state,'attack-demo');state=act(state,'advance');
  state=act(state,'fortify',{count:3});state=act(state,'end');state=act(state,'pass');
  assert.equal(state.board.westeuropa.armies,11);assert.equal(state.board.suedeuropa.armies,9);
  assert.equal(state.board.nordafrika.armies,1);assert.deepEqual(state.totals,[48,35]);assert.equal(state.moved,3);
});
test('Beispielsituationen sind getrennt und nicht in beliebige Phasen umschaltbar',()=>{
  for(const scenario of ['reinforce','attack','fortify','ended','waiting']){
    const first=createExample(scenario),second=createExample(scenario);first.board.peru.armies++;
    assert.equal(second.board.peru.armies,4);
  }
  assert.throws(()=>createExample('invalid'));assert.throws(()=>act(createExample(),'end'));
});
test('Angriffs- und Verlegungsstrecke stimmen mit den Nachbarn der vorhandenen Weltkarte überein',()=>{
  const world=JSON.parse(readFileSync(new URL('../../static/conquest/world.json',import.meta.url)));
  const west=world.territories.find(country=>country.id==='westeuropa');
  assert(west.neighbors.includes('nordafrika'));assert(west.neighbors.includes('suedeuropa'));
});
