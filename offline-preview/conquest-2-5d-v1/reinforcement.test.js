import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { buildPreviewTerritories } from './territory-model.js';
import { createPreviewTurn } from './turn-model.js';
import { PerspectiveCamera, Vector3 } from './vendor/three/three.module.js';
import { frameCamera, framingAtAngle } from './camera.js';
import { BOARD_WIDTH, BOARD_DEPTH, BOARD_Y } from './territory-model.js';

const world = JSON.parse(readFileSync(new URL('./assets/world.json', import.meta.url)));
const freshTerritories = () => buildPreviewTerritories(world);

test('The turn stays locked after partial placement and unlocks only on the final troop', () => {
  const territories = freshTerritories();
  const turn = createPreviewTurn(territories);
  const before = turn.troops('alaska');
  assert.equal(turn.remaining, 6);
  assert.equal(turn.canAdvance, false);
  assert.throws(() => turn.advance(), /Verteile zuerst/);
  turn.place('alaska', 5);
  assert.equal(turn.troops('alaska'), before + 5);
  assert.equal(turn.remaining, 1);
  assert.equal(turn.canAdvance, false);
  assert.throws(() => turn.advance(), /Verteile zuerst/);
  turn.place('alberta', 1);
  assert.equal(turn.remaining, 0);
  assert.equal(turn.canAdvance, true);
  turn.advance();
  assert.equal(turn.phase, 'attack');
  assert.equal(turn.canAdvance, true, 'Attacking is optional.');
  assert.throws(() => turn.place('alaska', 1), /beendet/);
  turn.advance();
  assert.equal(turn.phase, 'fortify');
  assert.equal(turn.canAdvance, true, 'Fortification may be skipped.');
  turn.advance();
  assert.equal(turn.phase, 'ended');
  assert.equal(turn.canAdvance, false);
  assert.throws(() => turn.advance(), /bereits gewechselt/);
});

test('Invalid targets and quantities cannot change any troop count or the reserve', () => {
  const territories = freshTerritories();
  const turn = createPreviewTurn(territories);
  const before = territories.map(territory => turn.troops(territory.id));
  for (const [id, count] of [['groenland', 1], ['unknown', 1], ['alaska', 0], ['alaska', -1], ['alaska', 1.5], ['alaska', 7], ['alaska', NaN], ['alaska', '2']]) {
    assert.throws(() => turn.place(id, count));
    assert.equal(turn.remaining, 6);
    assert.deepEqual(territories.map(territory => turn.troops(territory.id)), before);
  }
});

test('Reinforcements are conserved and do not change foreign armies or the source fixture', () => {
  const territories = freshTerritories();
  const fixture = JSON.stringify(territories);
  const turn = createPreviewTurn(territories);
  const originalTotal = territories.reduce((sum, territory) => sum + territory.armies, 0);
  for (const id of ['alaska', 'alberta', 'weststaaten', 'venezuela', 'argentinien', 'skandinavien']) {
    turn.place(id, 1);
    const boardTotal = territories.reduce((sum, territory) => sum + turn.troops(territory.id), 0);
    assert.equal(boardTotal + turn.remaining, originalTotal + 6);
  }
  assert.ok(territories.filter(territory => territory.owner.id !== 'gold').every(territory => turn.troops(territory.id) === territory.armies));
  assert.equal(JSON.stringify(territories), fixture);
});

test('Restart restores only the local example and cannot duplicate an exhausted reserve', () => {
  const territories = freshTerritories();
  const turn = createPreviewTurn(territories);
  turn.place('alaska', 6);
  assert.throws(() => turn.place('alaska', 1));
  turn.advance();
  turn.reset();
  assert.equal(turn.phase, 'reinforce');
  assert.equal(turn.remaining, 6);
  assert.equal(turn.canAdvance, false);
  assert.ok(territories.every(territory => turn.troops(territory.id) === territory.armies));
});

for (const [width, height, toolbarBottom, barTop] of [[1920, 900, 69, 792], [1366, 768, 69, 660], [390, 844, 105, 736]]) {
  test(`The board stays above the turn bar at every lean in ${width}x${height}`, () => {
    const camera = new PerspectiveCamera(40, width / height, .15, 200);
    const target = new Vector3(0, 2.85, 0);
    const corners = [-1, 1].flatMap(x => [-1, 1].map(z => new Vector3(x * BOARD_WIDTH / 2, BOARD_Y, z * BOARD_DEPTH / 2)));
    for (let angle = 32; angle <= 82; angle += .25) {
      frameCamera(camera, { target, points: corners, angle, width, height, ...framingAtAngle(angle, height, toolbarBottom), bottomPixel: barTop - 10 });
      for (const corner of corners) {
        const projected = corner.clone().project(camera);
        const screenY = (1 - projected.y) * height / 2;
        assert.ok(screenY <= barTop - 10 + 1e-5, `Board covered by turn bar at ${angle}`);
        assert.ok(screenY >= toolbarBottom, `Board covered by toolbar at ${angle}`);
      }
    }
  });
}
