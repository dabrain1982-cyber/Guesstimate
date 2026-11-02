import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { cardCatalog, isCardSet, createCountryCard } from './cards.js';

const world = JSON.parse(readFileSync(new URL('./assets/world.json', import.meta.url), 'utf8'));
const cards = cardCatalog(world);
test('All 42 countries keep a stable symbol, with two distinct wildcard cards', () => {
  assert.equal(cards.length, 44);
  assert.equal(new Set(cards.map(card => card.id)).size, 44);
  assert.deepEqual(['infantry', 'cavalry', 'artillery', 'wild'].map(symbol => cards.filter(card => card.symbol === symbol).length), [14, 14, 14, 2]);
  assert.equal(cards.find(card => card.id === 'japan').symbol, 'artillery');
});
test('Selection accepts three equal, three distinct and matching wildcard sets', () => {
  const group = symbol => cards.filter(card => card.symbol === symbol);
  for (const symbol of ['infantry', 'cavalry', 'artillery']) {
    assert.ok(isCardSet(group(symbol).slice(0, 3)));
    assert.ok(isCardSet([...group(symbol).slice(0, 2), group('wild')[0]]));
    assert.ok(isCardSet([group(symbol)[0], ...group('wild')]));
  }
  assert.ok(isCardSet(['infantry', 'cavalry', 'artillery'].map(symbol => group(symbol)[0])));
  assert.ok(isCardSet(['infantry', 'cavalry', 'wild'].map(symbol => group(symbol)[0])));
});
test('Duplicate cards and a non-matching mixed set cannot be selected as a set', () => {
  const infantry = cards.filter(card => card.symbol === 'infantry');
  const cavalry = cards.find(card => card.symbol === 'cavalry');
  assert.equal(isCardSet([infantry[0], infantry[0], infantry[0]]), false);
  assert.equal(isCardSet([infantry[0], infantry[1], cavalry]), false);
  assert.equal(isCardSet(infantry.slice(0, 2)), false);
});

test('Cards distinguish owned countries, opponents and jokers with an explicit bonus',()=>{
  const saved=globalThis.document;
  class Element {
    constructor(){this.children=[];this.dataset={};this.attributes=new Map();this.style={setProperty(){}};this.classList={add(){}};this.textContent='';}
    append(...children){this.children.push(...children);}
    setAttribute(key,value){this.attributes.set(key,value);}
  }
  globalThis.document={createElement:()=>new Element(),createElementNS:()=>new Element()};
  const text=element=>element.textContent+' '+element.children.map(text).join(' ');
  try{
    const card=cards.find(row=>row.id==='alaska');
    const own=createCountryCard(card,{owned:true,ownerName:'Stormseed',bonusAvailable:true});
    assert.equal(own.dataset.owned,'true');assert.match(text(own),/Dein Gebiet/);assert.match(text(own),/\+2 hier beim Eintausch/);
    const other=createCountryCard(card,{ownerName:'Robin'});
    assert.equal(other.dataset.owned,'false');assert.match(text(other),/Gebiet von Robin/);assert.doesNotMatch(text(other),/\+2/);
    const spent=createCountryCard(card,{owned:true,bonusAvailable:false});
    assert.match(text(spent),/\+2 hier beim Eintausch/);assert.doesNotMatch(text(spent),/genutzt|wählbar/);
    const joker=createCountryCard(cards.find(row=>row.id==='joker-1'),{owned:true,bonusAvailable:true});
    assert.equal(joker.dataset.owned,'false');assert.doesNotMatch(text(joker),/\+2/);
  }finally{globalThis.document=saved;}
});
