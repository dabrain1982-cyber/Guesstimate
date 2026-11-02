import * as THREE from './vendor/three/three.module.js';
import { BOARD_Y, BOARD_WIDTH, boardPoint, buildPreviewTerritories, PREVIEW_ARMIES } from './territory-model.js';
import { createTurnControls } from './turn-controls.js';
import { comicArrowPath } from './attack.js';

export function createTerritoryLayer({ world, scene, camera, canvas, render, remote = null }) {
  const armies = remote?.armies || PREVIEW_ARMIES;
  const territories = buildPreviewTerritories(world).map(territory => remote ? {
    ...territory, owner: armies.find(army => army.id === remote.owner(territory.id)), armies: remote.troops(territory.id),
  } : territory);
  const byId = new Map(territories.map(territory => [territory.id, territory]));
  const layer = document.querySelector('#territories');
  const picker = document.querySelector('#territory-picker');
  const close = document.querySelector('#clear-selection');
  const status = document.querySelector('#selection-status');
  const group = new THREE.Group();
  group.name = '42 selectable territory counters';
  const entries = new Map();
  let selectedId = null;
  let turnControls;
  let lastActorId = null;
  const armyById = new Map(armies.map(army => [army.id, army]));
  const arrowSvg = document.querySelector('#attack-arrows');
  const arrowPaths = document.querySelector('#attack-paths');
  const arrowGroups = new Map();

  const baseGeometry = new THREE.CylinderGeometry(.145, .16, .055, 24);
  const ringGeometry = new THREE.RingGeometry(.20, .25, 40);
  ringGeometry.rotateX(-Math.PI / 2);
  const bronze = new THREE.MeshStandardMaterial({ color: '#b88d50', roughness: .42, metalness: .65 });

  function select(id) {
    const territory = byId.get(id);
    if (id && !territory) return;
    selectedId = territory?.id ?? null;
    picker.value = selectedId || '';
    close.hidden = !territory;
    status.textContent = territory
      ? territory.name + ': ' + turnControls.turn.troops(territory.id) + ' Truppen, Armee ' + armyById.get(turnControls.turn.owner(territory.id)).name + '.'
      : 'Auswahl aufgehoben.';
    turnControls.selected(territory);
    if (turnControls.turn.phase === 'attack') {
      selectedId = turnControls.attack.targetId || turnControls.attack.sourceId;
      picker.value = selectedId || '';
      close.hidden = !selectedId;
    }
    refreshAppearance();
  }

  for (const continent of world.continents) {
    const optgroup = document.createElement('optgroup');
    optgroup.label = continent.name;
    for (const territory of territories.filter(item => item.continent.id === continent.id)) {
      optgroup.append(new Option(territory.name, territory.id));
    }
    picker.append(optgroup);
  }

  for (const territory of territories) {
    const { id, point, owner, armies, name } = territory;
    const troopLabel = `${armies} ${armies === 1 ? 'Truppe' : 'Truppen'}`;
    const counter = new THREE.Mesh(baseGeometry, bronze);
    counter.position.set(point.x, BOARD_Y + .032, point.z);
    counter.castShadow = true;
    counter.name = `Counter base: ${name}`;
    group.add(counter);
    const ring = new THREE.Mesh(ringGeometry, new THREE.MeshBasicMaterial({ color: '#ffe499', transparent: true, opacity: 1, depthWrite: false }));
    ring.position.set(point.x, BOARD_Y + .009, point.z);
    ring.visible = false;
    group.add(ring);

    // One accessible number face per physical base. Projection uses the same
    // camera as the board, so counters stay attached throughout the lean.
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'army-marker';
    button.dataset.territory = id;
    button.dataset.owner = owner.id;
    button.setAttribute('aria-pressed', 'false');
    button.setAttribute('aria-label', `${name}, ${troopLabel}, Armee ${owner.name}`);
    button.title = `${name} · ${troopLabel} · ${owner.name}`;
    button.style.setProperty('--army-color', owner.color);
    button.style.setProperty('--army-ink', owner.ink);
    button.textContent = String(armies);
    button.addEventListener('click', () => select(id));
    layer.append(button);
    entries.set(id, { button, ring, anchor: new THREE.Vector3(point.x, BOARD_Y + .065, point.z) });
  }
  scene.add(group);

  function refreshAppearance() {
      if (remote) for (const army of remote.armies) Object.assign(armyById.get(army.id), army);
      const { turn, attack, fortify } = turnControls;
      if (lastActorId && lastActorId !== turn.ownerId) {
        selectedId = null;
        picker.value = '';
        close.hidden = true;
      }
      lastActorId = turn.ownerId;
      const attacking = turn.phase === 'attack';
      const fortifying = turn.phase === 'fortify';
      if (attacking) {
        selectedId = attack.targetId || attack.sourceId;
        picker.value = selectedId || '';
        close.hidden = !selectedId;
      }
      const movement = fortifying ? fortify : attack;
      const targets = new Set(fortifying ? turn.fortifyTargets(fortify.sourceId) : attack.targets);
      for (const territory of territories) {
        const { button, ring } = entries.get(territory.id);
        const count = turn.troops(territory.id);
        const owner = armyById.get(turn.owner(territory.id));
        const troopLabel = `${count} ${count === 1 ? 'Truppe' : 'Truppen'}`;
        button.textContent = String(count);
        button.setAttribute('aria-label', `${territory.name}, ${troopLabel}, Armee ${owner.name}`);
        button.title = `${territory.name} · ${troopLabel} · ${owner.name}`;
        button.dataset.owner = owner.id;
        button.style.setProperty('--army-color', owner.color);
        button.style.setProperty('--army-ink', owner.ink);
        const selected = territory.id === selectedId;
        const source = (attacking || fortifying) && territory.id === movement.sourceId;
        const attackTarget = attacking && (targets.has(territory.id) || (turn.battleRequest && territory.id === attack.targetId));
        const fortifyTarget = fortifying && targets.has(territory.id);
        button.setAttribute('aria-pressed', String(selected));
        button.classList.toggle('can-reinforce', turn.canReinforce(territory.id));
        button.classList.toggle('attack-source', attacking && source);
        button.classList.toggle('attack-target', attackTarget);
        button.classList.toggle('fortify-source', fortifying && source);
        button.classList.toggle('fortify-target', fortifyTarget);
        ring.visible = selected || source || attackTarget || fortifyTarget;
        ring.material.color.set(fortifyTarget ? '#b9e7b1' : attackTarget ? '#ff9c68' : selected || source ? '#ffe499' : '#e6f1d8');
        ring.material.opacity = selected || source ? 1 : .8;
      }
      render();
  }

  turnControls = createTurnControls({ territories, onChange: refreshAppearance, remote, armies });

  picker.disabled = false;
  picker.addEventListener('change', () => select(picker.value));
  close.addEventListener('click', () => {
    const last = selectedId;
    select(null);
    entries.get(last)?.button.focus({ preventScroll: true });
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && selectedId && !event.target.closest('dialog')) {
      const last = selectedId;
      select(null);
      entries.get(last)?.button.focus({ preventScroll: true });
    }
  });
  let pointerStart;
  canvas.addEventListener('pointerdown', event => { pointerStart = [event.clientX, event.clientY]; });
  canvas.addEventListener('pointerup', event => {
    if (pointerStart && Math.hypot(event.clientX - pointerStart[0], event.clientY - pointerStart[1]) < 5 && selectedId) select(null);
    pointerStart = null;
  });

  return {
    startTurn() { turnControls.start(); },
    update() {
      const width = canvas.clientWidth;
      const height = canvas.clientHeight;
      const projected = new THREE.Vector3();
      for (const { button, anchor } of entries.values()) {
        projected.copy(anchor).project(camera);
        button.style.left = `${(projected.x + 1) * width / 2}px`;
        button.style.top = `${(1 - projected.y) * height / 2}px`;
        button.hidden = projected.z <= -1 || projected.z >= 1;
      }
      arrowSvg.setAttribute('viewBox', `0 0 ${width} ${height}`);
      const phase = turnControls.turn.phase;
      const movement = phase === 'fortify' ? turnControls.fortify : turnControls.attack;
      const {sourceId, targetId} = movement;
      const routes = phase === 'attack' ? [...turnControls.attack.targets] : [];
      if (phase === 'attack' && turnControls.turn.battleRequest && targetId && !routes.includes(targetId)) routes.push(targetId);
      if (phase === 'fortify' && targetId) routes.push(targetId);
      arrowSvg.classList.toggle('is-fortify', phase === 'fortify');
      const activeKeys = new Set();
      if (sourceId && ['attack','fortify'].includes(phase)) for (const destination of routes) {
        const from = boardPoint(sourceId, BOARD_Y + .07), to = boardPoint(destination, BOARD_Y + .07);
        const wraps = new Set([sourceId, destination]);
        const segments = wraps.has('alaska') && wraps.has('kamtschatka')
          ? [[from, { ...from, x: sourceId === 'alaska' ? -BOARD_WIDTH / 2 + .1 : BOARD_WIDTH / 2 - .1 }],
             [{ ...to, x: destination === 'alaska' ? -BOARD_WIDTH / 2 + .1 : BOARD_WIDTH / 2 - .1 }, to]]
          : [[from, to]];
        segments.forEach(([start,end],index) => {
          const a = new THREE.Vector3(start.x,start.y,start.z).project(camera);
          const b = new THREE.Vector3(end.x,end.y,end.z).project(camera);
          const shape = comicArrowPath((a.x+1)*width/2,(1-a.y)*height/2,(b.x+1)*width/2,(1-b.y)*height/2,index%2?-1:1);
          if (!shape || a.z<=-1 || a.z>=1 || b.z<=-1 || b.z>=1) return;
          const key = phase + ':' + sourceId + ':' + destination + ':' + index;
          activeKeys.add(key);
          let view = arrowGroups.get(key);
          if (!view) {
            const group = document.createElementNS('http://www.w3.org/2000/svg','g');
            group.classList.add('combat-arrow'); group.dataset.source=sourceId; group.dataset.target=destination;
            const paths = ['arrow-shadow','arrow-face','arrow-shine'].map(name=>{
              const path=document.createElementNS('http://www.w3.org/2000/svg','path');path.setAttribute('class',name);group.append(path);return path;
            });
            view={group,paths};arrowGroups.set(key,view);arrowPaths.append(group);
          }
          view.group.dataset.selected=String(destination===targetId);
          view.paths[0].setAttribute('d',shape.body);view.paths[1].setAttribute('d',shape.body);view.paths[2].setAttribute('d',shape.shine);
        });
      }
      for (const [key,view] of arrowGroups) if (!activeKeys.has(key)) {view.group.remove();arrowGroups.delete(key);}

    },
  };
}
