import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { buildPreviewTerritories } from './territory-model.js';
import { createPreviewTurn } from './turn-model.js';

const world = JSON.parse(readFileSync(new URL('./assets/world.json', import.meta.url)));
function fixture({ source = 6, target = 2, from = 'venezuela', to = 'brasilien', rolls = [6, 5, 1, 4, 3] } = {}) {
  const territories = buildPreviewTerritories(world);
  territories.find(territory => territory.id === from).armies = source;
  territories.find(territory => territory.id === to).armies = target;
  let rolled = 0;
  const turn = createPreviewTurn(territories, { total: 0, rollDie: () => {
    assert.ok(rolled < rolls.length, 'An unexpected die was requested.');
    return rolls[rolled++];
  } });
  turn.advance();
  return { turn, territories, diceUsed: () => rolled };
}

test('An attack needs the attack phase, an owned source, an enemy neighbor and a garrison', () => {
  const initial = createPreviewTurn(buildPreviewTerritories(world));
  assert.throws(() => initial.attack('venezuela', 'brasilien', 3), /Angriffsphase/);
  const { turn, diceUsed } = fixture();
  const before = turn.troops('venezuela');
  for (const [from, to] of [['brasilien', 'venezuela'], ['venezuela', 'japan'], ['venezuela', 'argentinien'], ['alaska', 'kamtschatka'], ['unknown', 'brasilien']]) {
    assert.throws(() => turn.attack(from, to, 1));
    assert.equal(diceUsed(), 0);
    assert.equal(turn.troops('venezuela'), before);
  }
  assert.ok(turn.attackTargets('venezuela').includes('brasilien'));
  assert.ok(!turn.attackTargets('venezuela').includes('argentinien'));
});

test('Invalid or excessive attack dice do not consume randomness or alter either army', () => {
  const { turn, diceUsed } = fixture({ source: 3 });
  for (const count of [0, -1, 3, 4, 1.5, NaN, '2']) {
    assert.throws(() => turn.attack('venezuela', 'brasilien', count), /Angriffswürfel/);
    assert.equal(turn.troops('venezuela'), 3);
    assert.equal(turn.troops('brasilien'), 2);
    assert.equal(diceUsed(), 0);
  }
});

test('Sorted dice comparisons can split the losses without conquering the target', () => {
  const { turn } = fixture({ rolls: [1, 6, 1, 2, 5] });
  const result = turn.attack('venezuela', 'brasilien', 3);
  assert.deepEqual(result.attackRolls, [6, 1, 1]);
  assert.deepEqual(result.defenseRolls, [5, 2]);
  assert.equal(result.attackerLoss, 1);
  assert.equal(result.defenderLoss, 1);
  assert.equal(result.conquered, false);
  assert.equal(turn.troops('venezuela'), 5);
  assert.equal(turn.troops('brasilien'), 1);
  assert.equal(turn.owner('brasilien'), 'blau');
});

test('Conquest requires occupation using at least the final attack dice and leaving one behind', () => {
  const { turn } = fixture({ rolls: [1, 6, 5, 4, 5] });
  const result = turn.attack('venezuela', 'brasilien', 3);
  assert.equal(result.conquered, true);
  assert.equal(turn.owner('brasilien'), 'gold');
  assert.deepEqual(turn.pendingConquest, { from: 'venezuela', to: 'brasilien', min: 3, max: 5 });
  const externalCopy = turn.pendingConquest;
  externalCopy.min = 0;
  assert.equal(turn.pendingConquest.min, 3);
  assert.equal(turn.canAdvance, false);
  assert.throws(() => turn.advance(), /einrücken/);
  assert.throws(() => turn.attack('alberta', 'ontario', 1), /einrücken/);
  for (const count of [0, 2, 6, 3.5]) assert.throws(() => turn.occupy(count));
  turn.occupy(5);
  assert.equal(turn.troops('venezuela'), 1);
  assert.equal(turn.troops('brasilien'), 5);
  assert.equal(turn.pendingConquest, null);
  assert.equal(turn.conqueredCount, 1);
  assert.ok(turn.attackTargets('brasilien').includes('nordafrika'), 'A captured country uses its new owner for further attacks.');
  assert.throws(() => turn.occupy(3), /kein erobertes/);
});

test('All 36 one-versus-one results give ties to defense and preserve the last attacking troop', () => {
  let attackWins = 0, defenseWins = 0;
  for (let attack = 1; attack <= 6; attack++) for (let defense = 1; defense <= 6; defense++) {
    const { turn } = fixture({ source: 2, target: 1, rolls: [attack, defense] });
    const result = turn.attack('venezuela', 'brasilien', 1);
    if (attack > defense) {
      attackWins++;
      assert.equal(result.defenderLoss, 1);
      turn.occupy(1);
      assert.equal(turn.troops('venezuela'), 1);
      assert.equal(turn.troops('brasilien'), 1);
    } else {
      defenseWins++;
      assert.equal(result.attackerLoss, 1);
      assert.equal(turn.troops('venezuela'), 1);
      assert.deepEqual(turn.attackTargets('venezuela'), []);
      assert.throws(() => turn.attack('venezuela', 'brasilien', 1));
    }
  }
  assert.equal(attackWins, 15);
  assert.equal(defenseWins, 21);
});

test('The Alaska-Kamchatka border connection is a legal attack without inventing other neighbors', () => {
  const { turn } = fixture({ from: 'alaska', to: 'kamtschatka', source: 3, target: 1, rolls: [6, 1] });
  const result = turn.attack('alaska', 'kamtschatka', 1);
  assert.equal(result.conquered, true);
  turn.occupy(2);
  assert.equal(turn.owner('kamtschatka'), 'gold');
  assert.equal(turn.troops('alaska'), 1);
  assert.equal(turn.troops('kamtschatka'), 2);
});

test('A failed die source cannot partially apply a battle', () => {
  const { turn } = fixture({ rolls: [6, 0] });
  assert.throws(() => turn.attack('venezuela', 'brasilien', 1), /Ungültiges Würfelergebnis/);
  assert.equal(turn.troops('venezuela'), 6);
  assert.equal(turn.troops('brasilien'), 2);
  assert.equal(turn.owner('brasilien'), 'blau');
  assert.equal(turn.pendingConquest, null);
});

test('Ending attacks is optional and locks combat after reaching fortification', () => {
  const { turn } = fixture();
  assert.equal(turn.canAdvance, true);
  turn.advance();
  assert.equal(turn.phase, 'fortify');
  assert.equal(turn.canAdvance, true, 'The turn can finish without fortifying.');
  assert.deepEqual(turn.attackTargets('venezuela'), []);
  assert.throws(() => turn.attack('venezuela', 'brasilien', 1), /Angriffsphase/);
});

test('Reset restores owners, armies and the fixture even during pending occupation', () => {
  const { turn, territories } = fixture({ rolls: [6, 5, 1, 4, 3] });
  const before = JSON.stringify(territories);
  turn.attack('venezuela', 'brasilien', 3);
  turn.reset();
  assert.equal(turn.phase, 'reinforce');
  assert.equal(turn.pendingConquest, null);
  assert.equal(turn.conqueredCount, 0);
  for (const territory of territories) {
    assert.equal(turn.owner(territory.id), territory.owner.id);
    assert.equal(turn.troops(territory.id), territory.armies);
  }
  assert.equal(JSON.stringify(territories), before);
});
