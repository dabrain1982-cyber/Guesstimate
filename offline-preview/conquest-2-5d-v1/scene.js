import * as THREE from './vendor/three/three.module.js';
import { frameCamera, framingAtAngle, tableViewBounds, MIN_ANGLE, MAX_ANGLE } from './camera.js';
import { createTerritoryLayer } from './territories.js';
import { BOARD_WIDTH, BOARD_DEPTH, BOARD_Y } from './territory-model.js';

import { mountTableSurface } from './table-surface.js';
import { createRemoteTurn } from './remote-turn.js';
const buttonsReady=mountTableSurface();
const config = JSON.parse(document.querySelector('#conquest-config')?.textContent || 'null');
const canvas = document.querySelector('#scene');
const angleInput = document.querySelector('#angle');
const angleOutput = document.querySelector('#angle-value');
const loading = document.querySelector('#loading');
const errorPanel = document.querySelector('#error');
const cameraControls = document.querySelector('.camera-controls');
const turnBar = document.querySelector('#turn-bar');
const boardWidth = BOARD_WIDTH;
const boardDepth = BOARD_DEPTH;
const tabletopY = 2.85;
const tableWidth = boardWidth + 1.1;
const tableDepth = boardDepth + 1.1;
const target = new THREE.Vector3(0, tabletopY, 0);
let angle = MIN_ANGLE;
let renderer;
let scene;
let camera;
let ready = false;
let territoryLayer;

function reportError(error) {
  console.error(error);
  loading.hidden = true;
  errorPanel.hidden = false;
  document.querySelector('#error-detail').textContent =
    'Bitte versuche es erneut. Falls die Ansicht weiter fehlt, kann dieser Browser die räumliche Vorschau gerade nicht darstellen.';
}

document.querySelector('#reload').addEventListener('click', () => location.reload());

// Procedural material textures are native parts of the 3D objects, not
// stretched copies of the room photo. The turn adapter supplies game state.
function seededRandom(seed) {
  let state = seed >>> 0;
  return () => {
    state = (1664525 * state + 1013904223) >>> 0;
    return state / 4294967296;
  };
}

function makeWoodTexture() {
  const surface = document.createElement('canvas');
  surface.width = 1024;
  surface.height = 512;
  const ctx = surface.getContext('2d');
  const random = seededRandom(317);
  ctx.fillStyle = '#764121';
  ctx.fillRect(0, 0, surface.width, surface.height);
  for (let row = 0; row < 1100; row++) {
    const y = random() * 512;
    const bend = random() * 12 + 2;
    ctx.beginPath();
    ctx.moveTo(0, y);
    for (let x = 0; x <= 1024; x += 16) {
      ctx.lineTo(x, y + Math.sin(x / (90 + random() * 8) + y * .02) * bend);
    }
    ctx.strokeStyle = row % 4 === 0 ? `rgba(226,157,80,${random() * .18})` : `rgba(28,11,4,${random() * .22})`;
    ctx.lineWidth = random() * 1.8 + .2;
    ctx.stroke();
  }
  for (let i = 0; i < 14000; i++) {
    const x = random() * 1024;
    const y = random() * 512;
    ctx.fillStyle = random() > .5 ? '#e1b57513' : '#18090518';
    ctx.fillRect(x, y, random() * 4 + 1, .6);
  }
  const texture = new THREE.CanvasTexture(surface);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
  texture.anisotropy = 8;
  return texture;
}

function octagon(width, depth, cut) {
  const x = width / 2;
  const z = depth / 2;
  return new THREE.Shape([
    new THREE.Vector2(-x + cut, -z), new THREE.Vector2(x - cut, -z),
    new THREE.Vector2(x, -z + cut), new THREE.Vector2(x, z - cut),
    new THREE.Vector2(x - cut, z), new THREE.Vector2(-x + cut, z),
    new THREE.Vector2(-x, z - cut), new THREE.Vector2(-x, -z + cut),
  ]);
}

function horizontalSolid(shape, depth, y, material, bevel = .04) {
  const geometry = new THREE.ExtrudeGeometry(shape, {
    depth, steps: 1, bevelEnabled: bevel > 0,
    bevelSize: bevel, bevelThickness: bevel, bevelSegments: 2,
  });
  geometry.rotateX(-Math.PI / 2);
  const mesh = new THREE.Mesh(geometry, material);
  mesh.position.y = y;
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  return mesh;
}

function makeTable(mapTexture, woodTexture) {
  const table = new THREE.Group();
  table.name = 'Conquest table';
  const wood = new THREE.MeshStandardMaterial({ map: woodTexture, roughness: .6, metalness: .04 });
  const darkWood = new THREE.MeshStandardMaterial({ color: '#382218', roughness: .68 });
  const brass = new THREE.MeshStandardMaterial({ color: '#b98246', metalness: .65, roughness: .37 });
  table.add(horizontalSolid(octagon(tableWidth - .2, tableDepth - .2, .3), .62, tabletopY - .86, darkWood));
  table.add(horizontalSolid(octagon(tableWidth, tableDepth, .34), .24, tabletopY - .24, wood, .055));

  const trim = new THREE.Shape([
    new THREE.Vector2(-boardWidth / 2 - .085, -boardDepth / 2 - .085),
    new THREE.Vector2(boardWidth / 2 + .085, -boardDepth / 2 - .085),
    new THREE.Vector2(boardWidth / 2 + .085, boardDepth / 2 + .085),
    new THREE.Vector2(-boardWidth / 2 - .085, boardDepth / 2 + .085),
  ]);
  trim.holes.push(new THREE.Path([
    new THREE.Vector2(-boardWidth / 2, -boardDepth / 2),
    new THREE.Vector2(-boardWidth / 2, boardDepth / 2),
    new THREE.Vector2(boardWidth / 2, boardDepth / 2),
    new THREE.Vector2(boardWidth / 2, -boardDepth / 2),
  ]));
  table.add(horizontalSolid(trim, .012, tabletopY + .062, brass, 0));

  const board = new THREE.Mesh(
    new THREE.PlaneGeometry(boardWidth, boardDepth),
    new THREE.MeshBasicMaterial({ map: mapTexture, toneMapped: false }),
  );
  board.name = 'Unchanged Conquest colour map';
  board.rotation.x = -Math.PI / 2;
  board.position.y = BOARD_Y;
  table.add(board);

  const legHeight = tabletopY - .6;
  for (const xSign of [-1, 1]) {
    for (const zSign of [-1, 1]) {
      const leg = new THREE.Mesh(new THREE.CylinderGeometry(.25, .36, legHeight, 4), wood);
      leg.rotation.y = Math.PI / 4;
      leg.position.set(xSign * (tableWidth / 2 - .85), legHeight / 2, zSign * (tableDepth / 2 - .85));
      leg.castShadow = true;
      table.add(leg);
      const foot = new THREE.Mesh(new THREE.CylinderGeometry(.365, .37, .16, 4), brass);
      foot.rotation.y = Math.PI / 4;
      foot.position.set(leg.position.x, .1, leg.position.z);
      table.add(foot);
      const bolt = new THREE.Mesh(new THREE.SphereGeometry(.055, 12, 8), brass);
      bolt.scale.y = .35;
      bolt.position.set(xSign * (tableWidth / 2 - .23), tabletopY + .065, zSign * (tableDepth / 2 - .23));
      table.add(bolt);
    }
  }
  return table;
}

// Each visible surface has one material. There is no projected carpet/photo
// blend and no timber fallback outside a photograph's rectangular boundary.
function buildRoom(wallTexture, furnitureTexture, rugTexture) {
  rugTexture.repeat.set(10, 10);
  const floorMaterial = new THREE.MeshBasicMaterial({ map: rugTexture, toneMapped: false });
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(100, 100), floorMaterial);
  floor.rotation.x = -Math.PI / 2;
  floor.position.z = 12;
  floor.name = 'Room floor';
  scene.add(floor);

  const wallSectionWidth = 32;
  const wallWidth = wallSectionWidth * 3;
  const wallHeight = wallSectionWidth * wallTexture.image.height / wallTexture.image.width;
  wallTexture.wrapS = THREE.MirroredRepeatWrapping;
  wallTexture.repeat.x = 3;
  const back = new THREE.Mesh(new THREE.PlaneGeometry(wallWidth, wallHeight),
    new THREE.MeshBasicMaterial({ map: wallTexture, toneMapped: false }));
  back.position.set(0, wallHeight / 2, -12);
  back.name = 'Complete panoramic room wall';
  scene.add(back);

  const furnitureRegions = [
    { box: [44, 55, 894, 704], x: -8.8, z: -8.5, yaw: .08 },
    { box: [1155, 55, 2007, 711], x: 8.8, z: -8.5, yaw: -.08 },
  ];
  for (const region of furnitureRegions) {
    const [left, top, right, bottom] = region.box;
    const texture = furnitureTexture.clone();
    texture.repeat.set((right - left) / texture.image.width, (bottom - top) / texture.image.height);
    texture.offset.set(left / texture.image.width, 1 - bottom / texture.image.height);
    texture.needsUpdate = true;
    const height = 4.8;
    const width = height * (right - left) / (bottom - top);
    const card = new THREE.Mesh(new THREE.PlaneGeometry(width, height),
      new THREE.MeshBasicMaterial({ map: texture, transparent: true, alphaTest: .08, depthWrite: false, toneMapped: false, side: THREE.DoubleSide }));
    card.position.set(region.x, height / 2 - .08, region.z);
    card.rotation.y = region.yaw;
    card.name = 'Separate leather chair and lamp card';
    scene.add(card);
  }
  const shadow = new THREE.Mesh(new THREE.PlaneGeometry(60, 60), new THREE.ShadowMaterial({ color: '#100904', opacity: .3 }));
  shadow.rotation.x = -Math.PI / 2;
  shadow.position.y = .008;
  shadow.receiveShadow = true;
  scene.add(shadow);
}

function frameView() {
  // Fill the view with the map at each angle. The map stays visible; the front
  // wooden rail may cross the lower edge as explicitly requested by the user.
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  // Browser captures and minimising can briefly report an unusable layout.
  // Keep the last frame until a later resize has room to draw it again.
  if (width < 1 || height <= 40) return false;
  const framing = { ...framingAtAngle(angle, height), ...tableViewBounds(width, height, {
    rosterBottom: document.querySelector('#player-roster').getBoundingClientRect().bottom,
    actionsTop: turnBar.getBoundingClientRect().top,
    controlsTop: cameraControls.getBoundingClientRect().top,
  }) };
  if (framing.bottomPixel <= framing.topPixel + 30) return false;
  const corners = [];
  for (const x of [-boardWidth / 2, boardWidth / 2]) {
    for (const z of [-boardDepth / 2, boardDepth / 2]) {
      corners.push(new THREE.Vector3(x, tabletopY + .078, z));
    }
  }
  frameCamera(camera, {
    target, points: corners, angle, width, height, ...framing,
  });
  return true;
}

function render() {
  if (!ready) return;
  if (!frameView()) return;
  renderer.render(scene, camera);
  territoryLayer?.update();
  angleInput.value = String(angle);
  angleOutput.value = `${Math.round(angle)}°`;
  angleInput.setAttribute('aria-valuetext', `${Math.round(angle)} Grad`);
  document.querySelector('[data-pose="sit"]').setAttribute('aria-pressed', String(angle <= MIN_ANGLE + .05));
  document.querySelector('[data-pose="over"]').setAttribute('aria-pressed', String(angle >= MAX_ANGLE - .05));
}

function setAngle(value) {
  angle = THREE.MathUtils.clamp(value, MIN_ANGLE, MAX_ANGLE);
  render();
}

function resize() {
  if (!ready || canvas.clientWidth < 1 || canvas.clientHeight <= 40) return;
  renderer.setSize(canvas.clientWidth, canvas.clientHeight, false);
  camera.aspect = canvas.clientWidth / canvas.clientHeight;
  camera.updateProjectionMatrix();
  render();
}

async function main() {
  await buttonsReady;
  renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(Math.min(Math.max(devicePixelRatio, 1), 1.5));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.25;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  scene = new THREE.Scene();
  scene.background = new THREE.Color('#21150e');
  camera = new THREE.PerspectiveCamera(40, 1, .15, 200);

  const loader = new THREE.TextureLoader();
  const [mapTexture, wallTexture, furnitureTexture, rug, world] = await Promise.all([
    loader.loadAsync(new URL('./assets/karte.png', import.meta.url).href), loader.loadAsync(new URL('./assets/raum-wand-v2.png', import.meta.url).href),
    loader.loadAsync(new URL('./assets/moebel-v2.png', import.meta.url).href),
    loader.loadAsync(new URL('./assets/teppich.png', import.meta.url).href),
    fetch(config?.worldUrl || new URL('./assets/world.json', import.meta.url).href).then(response => {
      if (!response.ok) throw new Error('Die Gebietsdaten konnten nicht geladen werden.');
      return response.json();
    }),
  ]);
  for (const texture of [mapTexture, wallTexture, furnitureTexture, rug]) {
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.anisotropy = Math.min(16, renderer.capabilities.getMaxAnisotropy());
  }
  const wood = makeWoodTexture();
  rug.wrapS = rug.wrapT = THREE.MirroredRepeatWrapping;
  buildRoom(wallTexture, furnitureTexture, rug);
  scene.add(makeTable(mapTexture, wood));
  const remote = config ? createRemoteTurn(config, world) : null;
  territoryLayer = createTerritoryLayer({ world, scene, camera, canvas, render, remote });
  if (config) {
    document.querySelector('#table-back').hidden = false;
    document.querySelector('#table-back').href = config.backUrl;
    document.querySelector('.prototype-note').textContent = 'Lokaler Entwickler-Test · Du steuerst alle Testarmeen';
    document.querySelector('.prototype-note').hidden = !config.game.developer;
    document.querySelector('#reset-turn').hidden = true;
  }

  scene.add(new THREE.HemisphereLight('#ffeac9', '#35251a', 2.1));
  const light = new THREE.DirectionalLight('#fff2dc', 3.0);
  light.position.set(-7, 18, 10);
  light.castShadow = true;
  light.shadow.mapSize.set(1024, 1024);
  Object.assign(light.shadow.camera, { left: -12, right: 12, top: 12, bottom: -12, near: 1, far: 50 });
  light.shadow.bias = -.0005;
  light.shadow.normalBias = .025;
  scene.add(light);
  const fire = new THREE.PointLight('#e39238', 80, 30, 2);
  fire.position.set(0, 3, -11.5);
  scene.add(fire);

  ready = true;
  loading.hidden = true;
  resize();
  renderer.shadowMap.autoUpdate = false;
  document.body.dataset.ready = 'true';
  territoryLayer.startTurn();
}

angleInput.addEventListener('input', () => setAngle(Number(angleInput.value)));
document.querySelector('[data-pose="sit"]').addEventListener('click', () => setAngle(MIN_ANGLE));
document.querySelector('[data-pose="over"]').addEventListener('click', () => setAngle(MAX_ANGLE));
document.querySelector('.prototype').addEventListener('wheel', (event) => {
  if (!ready || event.ctrlKey || !event.deltaY) return;
  if (event.target.closest('.camera-controls, .table-back, .country-navigation, .player-roster, .turn-bar, .card-hand, .victory-result, .turn-receipt, dialog')) return;
  event.preventDefault();
  const unit = event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? canvas.clientHeight : 1;
  setAngle(angle - event.deltaY * unit * (MAX_ANGLE - MIN_ANGLE) / 2400);
}, { passive: false });
canvas.addEventListener('webglcontextlost', (event) => {
  event.preventDefault();
  reportError(new Error('WebGL context lost'));
});
window.addEventListener('resize', resize);
// Names, phase labels and loaded fonts may change the HUD height without a
// window resize. Keep the map and the lower panels clear of the actual bar.
const hudResizeObserver = new ResizeObserver(() => {
  document.querySelector('.prototype').style.setProperty('--turn-bar-height', `${turnBar.getBoundingClientRect().height}px`);
  resize();
});
hudResizeObserver.observe(turnBar);
hudResizeObserver.observe(document.querySelector('#player-roster'));
hudResizeObserver.observe(cameraControls);
main().catch(reportError);
