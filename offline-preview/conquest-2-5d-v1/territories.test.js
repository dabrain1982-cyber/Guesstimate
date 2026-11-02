import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { PerspectiveCamera, Vector3, Plane, Raycaster, Vector2 } from './vendor/three/three.module.js';
import { frameCamera, framingAtAngle } from './camera.js';
import { buildPreviewTerritories, boardPoint, BOARD_WIDTH, BOARD_DEPTH, BOARD_Y, MAP_WIDTH, MAP_HEIGHT } from './territory-model.js';

const world = JSON.parse(readFileSync(new URL('./assets/world.json', import.meta.url)));

test('All 42 counters use the current world IDs, names and reciprocal neighbor graph', () => {
  const sourceWorld = JSON.parse(readFileSync(new URL('../../static/conquest/world.json', import.meta.url)));
  assert.deepEqual(world, sourceWorld, 'The offline snapshot must not invent a second set of rules.');
  const territories = buildPreviewTerritories(world);
  assert.equal(territories.length, 42);
  assert.equal(territories.find(item => item.id === 'russland').name, 'Ukraine');
  assert.ok(territories.find(item => item.id === 'alaska').neighbors.includes('kamtschatka'));
  assert.ok(territories.find(item => item.id === 'ostafrika').neighbors.includes('naher-osten'));
  assert.ok(territories.find(item => item.id === 'ostafrika').neighbors.includes('madagaskar'));
  assert.deepEqual([MAP_WIDTH, MAP_HEIGHT], [1284, 1225]);
});

test('Marker coordinates match the image orientation, including opposite map edges', () => {
  assert.ok(boardPoint('alaska').x < -4 && boardPoint('alaska').z < 0);
  assert.ok(boardPoint('kamtschatka').x > 4 && boardPoint('kamtschatka').z < 0);
  assert.ok(boardPoint('argentinien').x < 0 && boardPoint('argentinien').z > 3);
  assert.ok(boardPoint('ostaustralien').x > 4 && boardPoint('ostaustralien').z > 2);
  assert.throws(() => boardPoint('unknown'), /Brettposition fehlt/);
});

test('The labelled fixture stays deterministic and separate from actual game state', () => {
  const before = JSON.stringify(world);
  const first = buildPreviewTerritories(world);
  assert.deepEqual(first, buildPreviewTerritories(world));
  assert.equal(JSON.stringify(world), before);
  for (const owner of ['gold', 'rot', 'blau']) {
    assert.equal(first.filter(item => item.owner.id === owner).length, 14);
    assert.ok(new Set(first.filter(item => item.owner.id === owner).map(item => item.armies)).size >= 4, 'Each army needs varied counts to inspect readability.');
  }
  assert.ok(first.every(item => Number.isInteger(item.armies) && item.armies >= 1 && item.armies <= 8));
});

for (const [width, height, headerBottom] of [[1920, 900, 69], [1366, 768, 69], [390, 844, 125]]) {
  test(`Each projected marker ray returns to its own fixed anchor throughout the ${width}x${height} lean`, () => {
    const camera = new PerspectiveCamera(40, width / height, .15, 200);
    const target = new Vector3(0, 2.85, 0);
    const corners = [-1, 1].flatMap(x => [-1, 1].map(z => new Vector3(x * BOARD_WIDTH / 2, BOARD_Y, z * BOARD_DEPTH / 2)));
    const markerPlane = new Plane(new Vector3(0, 1, 0), -(BOARD_Y + .065));
    const raycaster = new Raycaster();
    for (let angle = 32; angle <= 82; angle += 2) {
      frameCamera(camera, { target, points: corners, angle, width, height, ...framingAtAngle(angle, height, headerBottom) });
      for (const territory of world.territories) {
        const point = boardPoint(territory.id, BOARD_Y + .065);
        const anchor = new Vector3(point.x, point.y, point.z);
        const projected = anchor.clone().project(camera);
        assert.ok(Math.abs(projected.x) < 1 && Math.abs(projected.y) < 1, `${territory.id} at ${angle} must remain on screen`);
        raycaster.setFromCamera(new Vector2(projected.x, projected.y), camera);
        const hit = raycaster.ray.intersectPlane(markerPlane, new Vector3());
        assert.ok(hit && hit.distanceTo(anchor) < 1e-7, `${territory.id} must stay on its board anchor at ${angle}`);
      }
    }
  });
}
