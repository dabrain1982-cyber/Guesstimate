import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { buildPreviewTerritories } from './territory-model.js';
import { createPreviewTurn } from './turn-model.js';

const world = JSON.parse(readFileSync(new URL('./assets/world.json', import.meta.url)));
function fixture() {
  const territories = buildPreviewTerritories(world);
  territories.find(item => item.id === 'venezuela').armies = 9;
  let rolls = [];
  const turn = createPreviewTurn(territories, { total: 0, drawIndex: () => 0, rollDie: () => {
    assert.ok(rolls.length, 'Unexpected die.');
    return rolls.shift();
  } });
  function win(from, to, count = 3) {
    rolls = [...Array(count).fill(6), ...Array(Math.min(2, turn.troops(to))).fill(1)];
    const result = turn.attack(from, to, count);
    if (result.conquered) turn.occupy(turn.pendingConquest.min);
    return result;
  }
  return { turn, territories, win };
}
const totalTroops = (turn, territories) => territories.reduce((sum, territory) => sum + turn.troops(territory.id), 0);

test('Fortification transfers once between owned neighbors, conserves troops and leaves one behind', () => {
  const { turn, territories } = fixture();
  turn.advance(); turn.advance();
  const before = totalTroops(turn, territories);
  assert.ok(turn.fortifyTargets('alberta').includes('alaska'));
  turn.fortify('alberta', 'alaska', 7);
  assert.equal(turn.troops('alberta'), 1);
  assert.equal(turn.troops('alaska'), 8);
  assert.equal(totalTroops(turn, territories), before);
  assert.equal(turn.fortified, true);
  assert.deepEqual(turn.fortifyTargets('alaska'), []);
  assert.throws(() => turn.fortify('alaska', 'alberta', 1), /einmal/);
  assert.equal(turn.troops('alaska'), 8);
});

test('Invalid fortifications and invalid phases cannot consume the one allowed move', () => {
  const { turn, territories } = fixture();
  assert.throws(() => turn.fortify('alberta', 'alaska', 1));
  turn.advance();
  assert.throws(() => turn.fortify('alberta', 'alaska', 1));
  turn.advance();
  const before = territories.map(item => turn.troops(item.id));
  for (const [from, to, count] of [['alberta', 'ontario', 1], ['alberta', 'venezuela', 1], ['alberta', 'alberta', 1], ['unknown', 'alaska', 1], ['alberta', 'alaska', 8], ['alberta', 'alaska', 0], ['alberta', 'alaska', -1], ['alberta', 'alaska', 1.5], ['alberta', 'alaska', '2']]) {
    assert.throws(() => turn.fortify(from, to, count));
    assert.equal(turn.fortified, false);
    assert.deepEqual(territories.map(item => turn.troops(item.id)), before);
  }
});

test('A turn with no conquest can skip fortification and awards no card', () => {
  const { turn } = fixture();
  assert.throws(() => turn.passTurn(), /Beende zuerst/);
  turn.advance(); turn.advance();
  const result = turn.finishTurn();
  assert.equal(result.card, null);
  assert.equal(result.fortified, false);
  assert.equal(turn.phase, 'ended');
  assert.equal(turn.canAdvance, false);
  assert.deepEqual(turn.hand(), []);
  assert.equal(turn.deckCount, 42);
});

test('The one-click end action awards once and immediately hands off',()=>{
  const {turn,win}=fixture();
  turn.advance();
  while(!win('venezuela','brasilien').conquered){}
  turn.advance();
  const actor=turn.ownerId,next=turn.nextOwnerId,before=turn.deckCount;
  const receipt=turn.endTurn();
  assert.ok(receipt.card);assert.equal(receipt.ownerId,actor);
  assert.equal(turn.ownerId,next);assert.equal(turn.phase,'reinforce');
  assert.equal(turn.deckCount,before-1);assert.equal(turn.hand(actor).length,1);
  assert.throws(()=>turn.endTurn());assert.equal(turn.deckCount,before-1);
});

test('A single occupied conquest earns exactly one random country card at turn end', () => {
  const { turn, win } = fixture();
  turn.advance();
  win('venezuela', 'brasilien');
  assert.equal(turn.hand().length, 0, 'No card during the attack phase.');
  turn.advance();
  assert.equal(turn.hand().length, 0, 'No card just for entering fortification.');
  const result = turn.finishTurn();
  assert.equal(result.conqueredCount, 1);
  assert.equal(result.card.id, 'alaska', 'The draw is independent of the captured country.');
  assert.equal(turn.hand().length, 1);
  assert.equal(turn.deckCount, 41);
});

test('Two conquests plus fortification still earn only one card, with duplicate finish blocked', () => {
  const { turn, win } = fixture();
  turn.advance();
  win('venezuela', 'mittelamerika');
  win('venezuela', 'brasilien');
  assert.equal(turn.conqueredCount, 2);
  turn.advance();
  turn.fortify('venezuela', 'brasilien', 2);
  const result = turn.finishTurn();
  assert.equal(result.conqueredCount, 2);
  assert.equal(result.fortified, true);
  assert.equal(turn.hand().length, 1);
  for (let repeat = 0; repeat < 3; repeat++) {
    assert.throws(() => turn.finishTurn());
    assert.throws(() => turn.advance());
    assert.equal(turn.hand().length, 1);
    assert.equal(turn.deckCount, 41);
  }
  assert.throws(() => turn.attack('brasilien', 'peru', 1), /Angriffsphase/);
  assert.throws(() => turn.fortify('alberta', 'alaska', 1));
});

test('Pending occupation blocks turn end and handoff without generating a card', () => {
  const territories = buildPreviewTerritories(world);
  const dice = [6, 6, 6, 1];
  const turn = createPreviewTurn(territories, { total: 0, rollDie: () => dice.shift(), drawIndex: () => 0 });
  turn.advance();
  turn.attack('venezuela', 'brasilien', 3);
  assert.ok(turn.pendingConquest);
  assert.throws(() => turn.advance());
  assert.throws(() => turn.finishTurn());
  assert.throws(() => turn.passTurn());
  assert.equal(turn.hand().length, 0);
  assert.equal(turn.deckCount, 42);
});

test('Handoff preserves the board and separate hands while resetting per-turn allowances', () => {
  const { turn, territories, win } = fixture();
  turn.advance(); win('venezuela', 'brasilien'); turn.advance();
  turn.fortify('alberta', 'alaska', 1);
  turn.finishTurn();
  const board = territories.map(item => [turn.owner(item.id), turn.troops(item.id)]);
  assert.equal(turn.nextOwnerId, 'rot');
  turn.passTurn();
  assert.equal(turn.ownerId, 'rot');
  assert.equal(turn.turnNumber, 2);
  assert.equal(turn.phase, 'reinforce');
  assert.equal(turn.fortified, false);
  assert.equal(turn.conqueredCount, 0);
  assert.equal(turn.hand().length, 0);
  assert.equal(turn.hand('gold').length, 1);
  assert.deepEqual(territories.map(item => [turn.owner(item.id), turn.troops(item.id)]), board);
  assert.throws(() => turn.passTurn());
  for (let skipped = 0; skipped < 2; skipped++) {
    turn.advance(); turn.advance(); turn.finishTurn(); turn.passTurn();
  }
  assert.equal(turn.ownerId, 'gold');
  assert.equal(turn.hand().length, 1);
  assert.equal(turn.deckCount, 41);
});

test('Later qualifying turns draw a different card from the remaining deck', () => {
  const { turn, win } = fixture();
  turn.advance(); win('venezuela', 'brasilien'); turn.advance(); turn.finishTurn(); turn.passTurn();
  for (let skipped = 0; skipped < 2; skipped++) {
    turn.advance(); turn.advance(); turn.finishTurn(); turn.passTurn();
  }
  turn.advance();
  win('venezuela', 'mittelamerika');
  turn.advance(); turn.finishTurn();
  const hand = turn.hand();
  assert.equal(hand.length, 2);
  assert.equal(new Set(hand.map(card => card.id)).size, 2);
  assert.equal(turn.deckCount, 40);
  hand[0].name = 'changed externally';
  assert.equal(turn.hand()[0].name, 'Alaska');
});

test('An invalid draw cannot partially end a qualifying turn or consume a card', () => {
  const territories = buildPreviewTerritories(world);
  const dice = [6, 6, 6, 1];
  const turn = createPreviewTurn(territories, { total: 0, rollDie: () => dice.shift(), drawIndex: () => 42 });
  turn.advance(); turn.attack('venezuela', 'brasilien', 3); turn.occupy(3); turn.advance();
  assert.throws(() => turn.finishTurn(), /Kartenziehung/);
  assert.equal(turn.phase, 'fortify');
  assert.equal(turn.hand().length, 0);
  assert.equal(turn.deckCount, 42);
});

test('Restart restores the original army, all cards and the initial example state', () => {
  const { turn, territories, win } = fixture();
  turn.advance(); win('venezuela', 'brasilien'); turn.advance(); turn.finishTurn(); turn.passTurn();
  turn.reset();
  assert.equal(turn.ownerId, 'gold');
  assert.equal(turn.phase, 'reinforce');
  assert.equal(turn.turnNumber, 1);
  assert.equal(turn.deckCount, 42);
  assert.equal(turn.hand('gold').length + turn.hand('rot').length + turn.hand('blau').length, 0);
  assert.equal(turn.endResult, null);
  assert.ok(territories.every(item => turn.owner(item.id) === item.owner.id && turn.troops(item.id) === item.armies));
});
