import { PREVIEW_ARMIES } from './territory-model.js';
import { setActionLabel } from './game-buttons.js';

export function enemyTargets(turn, sourceId) {
  if (!sourceId || turn.phase !== 'attack' || turn.troops(sourceId) < 2) return [];
  return turn.attackTargets(sourceId).filter(id => turn.owner(id) !== turn.owner(sourceId));
}

// One closed comic shape for all projected routes, including wrapped borders.
export function comicArrowPath(x1, y1, x2, y2, bend = 1) {
  const length = Math.hypot(x2 - x1, y2 - y1);
  if (!Number.isFinite(length) || length < 12) return null;
  const dx = (x2 - x1) / length, dy = (y2 - y1) / length, nx = -dy, ny = dx;
  const trim = Math.min(20, length * .24), span = length - 2 * trim;
  // Close counters need an arc beside their rims rather than a hidden arrow under both faces.
  const offset = Math.max(0, Math.min(14, (70 - length) * .4)) * bend;
  const sx = x1 + dx * trim + nx * offset, sy = y1 + dy * trim + ny * offset;
  const ex = x2 - dx * trim + nx * offset, ey = y2 - dy * trim + ny * offset;
  const head = Math.min(15, span * .44), half = Math.min(3.8, span * .15), wing = half * 2.5;
  const bx = ex - dx * head, by = ey - dy * head;
  const curve = Math.min(7, span * .08) * bend;
  const mx = (sx + bx) / 2 + nx * curve, my = (sy + by) / 2 + ny * curve;
  const p = (x, y) => x.toFixed(2) + ' ' + y.toFixed(2);
  return {
    body: 'M ' + p(sx + nx * half, sy + ny * half) + ' Q ' + p(mx + nx * half, my + ny * half) + ' ' + p(bx + nx * half, by + ny * half) + ' L ' + p(bx + nx * wing, by + ny * wing) + ' L ' + p(ex, ey) + ' L ' + p(bx - nx * wing, by - ny * wing) + ' L ' + p(bx - nx * half, by - ny * half) + ' Q ' + p(mx - nx * half, my - ny * half) + ' ' + p(sx - nx * half, sy - ny * half) + ' Z',
    shine: 'M ' + p(sx + nx * half * .3, sy + ny * half * .3) + ' Q ' + p(mx + nx * half * .3, my + ny * half * .3) + ' ' + p(bx, by),
  };
}

export function createAttackControls({ turn, territories, onChange, onOccupy, armies = PREVIEW_ARMIES }) {
  const byId = new Map(territories.map(territory => [territory.id, territory]));
  const node = selector => document.querySelector(selector);
  const roll = node('#roll-attack'), status = node('#turn-status');
  const diceButtons = [...document.querySelectorAll('[data-dice-count]')];
  let sourceId = null, targetId = null, count = 0, lastMaximum = 0, busy = false, restoring = true;
  let hint = '', feedback = '', result = null, seenBattle = 0;
  const canAct = () => !turn.isRemote || turn.canAct;
  const maximum = () => sourceId ? Math.max(0, Math.min(3, turn.troops(sourceId) - 1)) : 0;
  const targets = () => enemyTargets(turn, sourceId);
  const resetDice = () => { count = lastMaximum = maximum(); };
  const hasPair = () => turn.phase === 'attack' && Boolean(sourceId && targetId);
  const ownDefense = () => Boolean(result?.defenderId && String(result.defenderId) === String(turn.inventoryOwnerId));

  function paint() {
    const active = turn.phase === 'attack', max = maximum();
    node('#combat-intent').hidden = !active || !sourceId || (!canAct() && !turn.battleRequest && !turn.pendingConquest && !ownDefense());
    node('#attack-source-name').textContent = byId.get(sourceId)?.name || 'Eigenes Land wählen';
    node('#attack-source-strength').textContent = sourceId ? String(turn.troops(sourceId)) : '';
    node('#attack-target-name').textContent = byId.get(targetId)?.name || 'Feindland wählen';
    node('#attack-target-strength').textContent = targetId ? String(turn.troops(targetId)) : '';
    for (const [side,id] of [['source',sourceId],['target',targetId]]) {
      const army = id && (turn.armies || armies).find(row => row.id === turn.owner(id));
      node('#attack-' + side + '-strength').style.setProperty('--country-color', army?.color || '#b75c42');
    }
    node('#attack-clear').disabled = busy || !canAct() || Boolean(turn.battleRequest || turn.pendingConquest);
    node('#attack-clear').hidden = !canAct();
    node('#attack-dice-choice').hidden = !active || !sourceId || !max || !canAct() || Boolean(turn.pendingConquest);
    node('#attack-dice-caption').textContent = count + ' Angriffswürfel';
    for (const button of diceButtons) {
      const value = Number(button.dataset.diceCount);
      button.hidden = value > max;
      button.disabled = busy || !canAct() || Boolean(turn.battleRequest || turn.pendingConquest);
      button.setAttribute('aria-checked', String(value === count));
      button.dataset.active = String(value <= count);
      button.tabIndex = value === count ? 0 : -1;
    }
    roll.hidden = !hasPair() || !canAct();
    roll.disabled = busy || !canAct() || Boolean(turn.battleRequest) || (!turn.pendingConquest && !targets().includes(targetId));
    setActionLabel(roll, busy ? 'Wird gewürfelt …' : turn.battleRequest ? 'Verteidigung abwarten' : turn.pendingConquest ? 'Truppen einrücken' : 'Angreifen');
    node('#battle-result').hidden = (!active && !ownDefense()) || !(result || feedback);
    node('#attack-roll-row').hidden = node('#defense-roll-row').hidden = !result;
    node('#battle-summary').textContent = result ? 'Verluste: Angriff ' + result.attackerLoss + ' · Verteidigung ' + result.defenderLoss : '';
    node('#battle-outcome').textContent = feedback;
  }
  function notify() { paint(); onChange(); }
  function showRolls(selector, values) {
    node(selector).replaceChildren(...values.map(value => {
      const die = document.createElement('span'); die.className = 'battle-die'; die.textContent = String(value); return die;
    }));
  }
  function record(battle) {
    result = battle; seenBattle = battle.sequence || seenBattle;
    showRolls('#attacker-rolls', battle.attackRolls);
    showRolls('#defender-rolls', battle.defenseRolls);
    const land = byId.get(battle.to)?.name || 'Dein Land';
    feedback = ownDefense()
      ? battle.conquered ? land + ' verloren.' : battle.defenderLoss ? land + ' verteidigt · ' + battle.defenderLoss + (battle.defenderLoss === 1 ? ' Truppe verloren.' : ' Truppen verloren.') : land + ': Angriff abgewehrt.'
      : battle.conquered ? canAct() ? turn.pendingConquest ? 'Land erobert. Jetzt Truppen einrücken.' : 'Land besetzt. Du kannst weiter angreifen oder zum Festigen weitergehen.' : land + ' wurde erobert.' : turn.troops(sourceId) < 2 ? 'Eine Truppe bleibt zurück. Hier ist kein weiterer Angriff möglich.' : canAct() ? 'Du kannst erneut angreifen oder ein anderes Ziel wählen.' : 'Angriff abgeschlossen.';
    resetDice();
    status.textContent = 'Angriff ' + battle.attackRolls.join(', ') + ' · Verteidigung ' + battle.defenseRolls.join(', ') + '. ' + feedback;
  }
  function sync() {
    const battle = turn.lastBattle;
    if (battle && battle.sequence !== seenBattle && byId.has(battle.from) && byId.has(battle.to)
        && (String(battle.defenderId) === String(turn.inventoryOwnerId)
          || (turn.phase === 'attack' && (!canAct() || restoring)))) {
      sourceId = battle.from; targetId = battle.to; record(battle);
    }
    if (turn.phase !== 'attack') { sourceId = targetId = null; if (!ownDefense()) { result = null; feedback = ''; } restoring = false; paint(); return; }
    const request = turn.battleRequest || turn.pendingConquest;
    if (request && byId.has(request.from) && byId.has(request.to)) {
      sourceId = request.from; targetId = request.to; resetDice();
      if (turn.battleRequest) {
        count = turn.battleRequest.dice || count;
        const defender = (turn.armies || armies).find(army => army.id === String(turn.battleRequest.defender));
        feedback = 'Die Verteidigung von ' + (defender?.name || 'der Gegenseite') + ' wird automatisch aufgelöst.';
      }
    }
    restoring = false;
    if (battle && battle.sequence !== seenBattle && battle.from === sourceId && battle.to === targetId) record(battle);
    if (sourceId && !request && !busy) {
      if (turn.owner(sourceId) !== turn.ownerId) sourceId = targetId = null;
      else if (canAct() && targetId && !targets().includes(targetId)) targetId = null;
    }
    if (maximum() !== lastMaximum) resetDice();
    paint();
  }
  function chooseDice(value) {
    if (busy || !canAct() || turn.phase !== 'attack' || turn.battleRequest || turn.pendingConquest) return;
    if (!Number.isInteger(value) || value < 1 || value > maximum()) return;
    count = value; paint();
  }
  function clear({ keepDefense = false } = {}) {
    sourceId = targetId = null; count = lastMaximum = 0; hint = '';
    if (!keepDefense || !ownDefense()) { feedback = ''; result = null; }
    seenBattle = turn.lastBattle?.sequence || result?.sequence || 0; restoring = false; paint();
  }
  for (const button of diceButtons) button.addEventListener('click', () => chooseDice(Number(button.dataset.diceCount)));
  node('#attack-dice-choice').addEventListener('wheel', event => {
    event.preventDefault(); event.stopPropagation();
    if (event.deltaY) chooseDice(count + (event.deltaY > 0 ? -1 : 1));
  }, { passive: false });
  node('#attack-dice-choice').addEventListener('keydown', event => {
    const directions = {ArrowLeft:-1,ArrowDown:-1,ArrowRight:1,ArrowUp:1};
    if (event.key in directions) { event.preventDefault(); chooseDice(count + directions[event.key]); }
    else if (event.key === 'Home' || event.key === 'End') { event.preventDefault(); chooseDice(event.key === 'Home' ? 1 : maximum()); }
    else return;
    diceButtons.find(button => Number(button.dataset.diceCount) === count)?.focus();
  });
  node('#attack-clear').addEventListener('click', () => {
    if (busy || turn.battleRequest || turn.pendingConquest) return;
    targetId = null; result = null; feedback = ''; hint = ''; resetDice(); notify();
  });
  async function perform() {
    if (busy || !canAct() || !hasPair() || turn.battleRequest) return;
    if (turn.pendingConquest) { onOccupy(); return; }
    if (!targets().includes(targetId) || count < 1 || count > maximum()) return;
    busy = true; result = null; feedback = ''; notify();
    try {
      const battle = await turn.attack(sourceId, targetId, count);
      if (battle.pendingDefense) sync(); else record(battle);
    } catch (error) { feedback = error.message; }
    finally { busy = false; sync(); notify(); }
  }
  roll.addEventListener('click', perform);
  return {
    sync, clear, perform, chooseDice,
    get sourceId() { return sourceId; }, get targetId() { return targetId; },
    get diceCount() { return count; }, get maxDice() { return maximum(); },
    get targets() { return targets(); }, get hasAction() { return hasPair(); },
    get hint() { return hint || 'Wähle ein eigenes Land mit mindestens zwei Truppen.'; },
    selected(territory) {
      if (busy || !canAct() || turn.battleRequest || turn.pendingConquest) return;
      result = null; feedback = ''; restoring = false;
      if (!territory) { clear(); notify(); return; }
      if (turn.owner(territory.id) === turn.ownerId) {
        sourceId = territory.id; targetId = null; resetDice();
        hint = targets().length ? territory.name + ': Wähle ein Land am Ende eines Angriffspfeils.' : 'Von hier ist gerade kein Angriff möglich.';
      } else if (sourceId && targets().includes(territory.id)) {
        targetId = targetId === territory.id ? null : territory.id; resetDice();
        hint = targetId ? byId.get(sourceId).name + ' → ' + territory.name + ': Angriff bereit.' : 'Zielwahl aufgehoben. Du kannst zum Festigen weitergehen.';
      } else { targetId = null; hint = sourceId ? 'Dieses Land ist kein angreifbarer feindlicher Nachbar.' : 'Wähle zuerst ein eigenes Ausgangsland.'; }
      notify(); status.textContent = hint;
    },
    occupied() { targetId = null; result = null; feedback = ''; resetDice(); hint = 'Land besetzt. Du kannst weiter angreifen oder zum Festigen weitergehen.'; },
  };
}
