import { createPreviewTurn } from './turn-model.js';
import { createAttackControls } from './attack.js';
import { createFortifyControls } from './fortify.js';
import { createCountryCard, isCardSet } from './cards.js';
import { PREVIEW_ARMIES } from './territory-model.js';
import { createPlayerPortrait } from './player-portrait.js';
import { setActionLabel } from './game-buttons.js';

export function createTurnControls({ territories, onChange, remote = null, armies = PREVIEW_ARMIES }) {
  const turn = remote || createPreviewTurn(territories);
  const byId = new Map(territories.map(territory => [territory.id, territory]));
  const bar = document.querySelector('#turn-bar');
  const next = document.querySelector('#next-phase');
  const hint = document.querySelector('#turn-hint');
  const status = document.querySelector('#turn-status');
  const deployment = document.querySelector('#deployment-controls');
  deployment.hidden = true;
  const amount = document.querySelector('#deployment-amount');
  const slider = document.querySelector('#deployment-slider');
  const confirm = document.querySelector('#confirm-deployment');
  const error = document.querySelector('#deployment-error');
  let targetId = null;
  let amountMode = 'reinforce';
  let transferSourceId = null;
  let attack;
  let fortify;
  let resolvingDefense = false;
  let editingAmount = false, submittingAmount = false;
  let autoAdvancing = false, autoAttempted = false, autoFailure = '';
  const turnReceipt = document.querySelector('#turn-receipt');
  turnReceipt.hidden = true;
  let endingTurn = false, legacyEndAttempted = false;
  let receiptKey = '', receiptTimer = null;
  const turnNotice = document.querySelector('#turn-notice');
  turnNotice.hidden = true;
  let noticeKey = '', noticeTimer = null, noticeMandatory = false;
  const victoryResult = document.querySelector('#victory-result');
  const winnerPortrait = createPlayerPortrait(document.querySelector('#winner-portrait'));
  let victoryShown = false;
  const cardHand = document.querySelector('#card-hand');
  const missionReveal = document.querySelector('#mission-reveal');
  let cardsExpanded = false, handSignature = '', missionPresented = false;
  const army = id => (remote?.armies || armies).find(item => item.id === String(id));
  const roster = new Map();
  for (const player of armies) {
    const host = document.createElement('div'); host.className = 'roster-seat';
    host.setAttribute('role', 'listitem'); host.dataset.player = player.id;
    document.querySelector('#player-roster').append(host);
    roster.set(player.id, createPlayerPortrait(host));
  }
  const selectedCards = new Set();
  const tradeButton = document.querySelector('#trade-cards');
  const tradeFeedback = document.querySelector('#trade-feedback');
  let trading = false;
  let placingInitial = false;

  function renderHand(focusId = null) {
    const cards = turn.hand();
    const info = remote?.tradeInfo;
    cardHand.style.setProperty('--hand-gaps', String(Math.max(1,cards.length-1)));
    const owned = new Set(cards.map(card => card.id));
    for (const key of selectedCards) if (!owned.has(key)) selectedCards.delete(key);
    const content = cards.map((card,index) => {
      const wrapper = document.createElement('button');
      wrapper.type = 'button'; wrapper.dataset.selectCard = card.id;
      // Hover and selection lift a card without changing the stack order.
      wrapper.style.setProperty('--card-order', String(index + 1));
      wrapper.style.setProperty('--card-angle', `${[-1.4,.7,-.8,1.1,-.3][index % 5]}deg`);
      wrapper.style.setProperty('--card-nudge', `${[1,-1,2,0,-1][index % 5]}px`);
      wrapper.className = 'hand-card' + (selectedCards.has(card.id) ? ' is-selected' : '');
      wrapper.append(countryCard(card));
      wrapper.setAttribute('aria-label', cardsExpanded ? `${card.name} ${selectedCards.has(card.id) ? 'abwählen' : 'auswählen'}` : `Länderkarten vergrößern · ${card.name}`);
      wrapper.setAttribute('aria-pressed', String(selectedCards.has(card.id)));
      wrapper.disabled = trading || (cardsExpanded && selectedCards.size === 3 && !selectedCards.has(card.id));
      wrapper.addEventListener('click', () => {
        if (!cardsExpanded) { showHand(); return; }
        if (selectedCards.has(card.id)) selectedCards.delete(card.id); else selectedCards.add(card.id);
        renderHand(card.id);
      });
      return wrapper;
    });
    document.querySelector('#hand-cards').replaceChildren(...content);
    document.querySelector('#cards-toggle').hidden = !cardsExpanded || !cards.length;
    document.querySelector('#trade-panel').hidden = true;
    if (remote) {
      const chosen = cards.filter(card => selectedCards.has(card.id));
      const valid = isCardSet(chosen);
      document.querySelector('#trade-panel').hidden = !cardsExpanded || !info.can_trade || !valid;
      tradeButton.disabled = trading || !info.can_trade || !valid;
      setActionLabel(tradeButton, trading ? 'Tausche …' : `Tauschen · +${info.next_value}`);
    }
    anchorCards();
    if (focusId) document.querySelector(`[data-select-card="${focusId}"]`)?.focus({ preventScroll: true });
  }

  function showHand() {
    hideTurnReceipt();
    setCardsExpanded(true);
  }
  function setCardsExpanded(expanded) {
    cardsExpanded = expanded;
    cardHand.dataset.expanded = String(expanded);
    document.querySelector('#cards-toggle').setAttribute('aria-expanded', String(expanded));
    renderHand();
    updateTurnNotice();
  }
  function updateCards() {
    const mission = remote?.ownMission;
    document.querySelector('#review-mission').hidden = !mission;
    document.querySelector('#review-mission').title = mission?.text || '';
    document.querySelector('#review-mission').setAttribute('aria-label', mission ? `Dein Auftrag: ${mission.text}` : 'Deine Auftragskarte ansehen');
    const signature = JSON.stringify([turn.hand(), turn.ownerId, turn.phase, turn.canAct, remote?.tradeInfo,
      turn.hand().map(card => turn.owner(card.id))]);
    if (signature !== handSignature) { handSignature = signature; renderHand(); }
    anchorCards();
    if (!missionPresented && mission && !remote.winner && (turn.phase === 'setup' || turn.turnNumber === 1)) {
      missionPresented = true;
      let seen = false;
      try { seen = localStorage.getItem(remote.missionKey) === 'seen'; } catch (_) { /* Session-only when storage is unavailable. */ }
      if (!seen) showMission();
    }
  }
  function anchorCards() {
    const owner = String(turn.inventoryOwnerId || turn.ownerId);
    cardHand.dataset.owner = owner;
    const source = roster.get(owner)?.anchor;
    const avatar = source?.getBoundingClientRect?.();
    const bounds = document.querySelector('.prototype').getBoundingClientRect?.();
    if (!avatar || !bounds) return;
    const rosterBounds = document.querySelector('#player-roster').getBoundingClientRect();
    const leftSide = (avatar.left + avatar.right) / 2 > bounds.left + bounds.width / 2;
    const x = (leftSide ? avatar.left - 8 : avatar.right + 8) - bounds.left;
    const space = Math.max(90, leftSide ? x - 8 : bounds.width - x - 8);
    cardHand.dataset.side = leftSide ? 'left' : 'right';
    cardHand.style.setProperty('--hand-x', `${x}px`);
    cardHand.style.setProperty('--hand-y', `${avatar.top - bounds.top}px`);
    cardHand.style.setProperty('--hand-space', `${space}px`);
    cardHand.style.setProperty('--avatar-height', `${avatar.height}px`);
    cardHand.dataset.up = String(avatar.top - bounds.top > Math.max(260, bounds.height - 300));
    cardHand.hidden = (!turn.hand().length && !remote?.ownMission)
      || avatar.bottom <= rosterBounds.top || avatar.top >= rosterBounds.bottom;
  }
  globalThis.window?.addEventListener?.('resize', anchorCards);
  document.querySelector('#player-roster').addEventListener('scroll', anchorCards);
  const anchorObserver = globalThis.ResizeObserver ? new ResizeObserver(anchorCards) : null;
  anchorObserver?.observe(document.querySelector('#player-roster'));
  globalThis.window?.addEventListener?.('pagehide', () => anchorObserver?.disconnect(), { once: true });
  function showMission() {
    if (!remote?.ownMission) return;
    document.querySelector('#mission-text').textContent = remote.ownMission.text;
    if (!missionReveal.open) missionReveal.showModal();
  }
  const rememberMission = () => {
    if (remote?.missionKey) try { localStorage.setItem(remote.missionKey, 'seen'); } catch (_) { /* Optional presentation preference. */ }
  };
  document.querySelector('#accept-mission').addEventListener('click', () => missionReveal.close());
  missionReveal.addEventListener('close', rememberMission);
  document.querySelector('#review-mission').addEventListener('click', showMission);
  const collapseCards = () => { setCardsExpanded(false); roster.get(String(turn.inventoryOwnerId || turn.ownerId))?.focusCards(); };
  document.querySelector('#cards-toggle').addEventListener('click', collapseCards);
  cardHand.addEventListener('keydown', event => { if (event.key === 'Escape' && cardsExpanded) collapseCards(); });

  tradeButton.addEventListener('click', async () => {
    if (trading || !remote || tradeButton.disabled) return;
    trading = true; tradeFeedback.hidden = true; renderHand();
    try {
      const result = await turn.trade([...selectedCards]);
      selectedCards.clear();
      collapseCards();
      document.querySelector('#hand-cards').scrollTop = 0;
      status.textContent = `Satz ${result.trade_number} getauscht: ${result.units} zusätzliche Truppen zum Verteilen.`
        + (result.bonus ? ` Je +2 direkt auf ${(result.bonus_territories || [result.bonus_territory]).map(id => byId.get(id)?.name || id).join(', ')}.` : '');
    } catch (failure) { tradeFeedback.textContent = failure.message; tradeFeedback.hidden = false; }
    finally { trading = false; renderHand(); if (editingAmount) updateAmount(); refresh(); }
  });

  const troopLabel = count => `${count} ${count === 1 ? 'Truppe' : 'Truppen'}`;

  function countryCard(card) {
    const owner = turn.owner(card.id);
    const viewer = String(turn.inventoryOwnerId || turn.ownerId);
    const owned = owner === viewer;
    return createCountryCard(card, { owned, ownerName: owner ? army(owner)?.name : null,
      ownerColor: owner ? army(owner)?.color : null });
  }

  function mayAutoAdvance() {
    return turn.phase === 'reinforce' && turn.remaining === 0 && turn.canAdvance
      && !remote?.tradeInfo.can_trade && !remote?.tradeInfo.mandatory;
  }

  async function autoAdvance() {
    autoAttempted = autoAdvancing = true; autoFailure = '';
    try {
      await turn.advance();
      closeDeployment(); attack.clear(); fortify.clear();
      status.textContent = 'Alle Verstärkungen sind gesetzt. Du kannst jetzt angreifen.';
    } catch (failure) { autoFailure = failure.message; }
    finally { autoAdvancing = false; refresh(); }
  }

  function updateTurnNotice() {
    if (cardsExpanded) { turnNotice.hidden = true; return; }
    const eligible = turn.phase === 'reinforce' && (!remote || turn.canAct) && !remote?.winner;
    if (!eligible) {
      turnNotice.hidden = true; clearTimeout(noticeTimer); noticeTimer = null; noticeMandatory = false;
      return;
    }
    const mandatory = Boolean(remote?.tradeInfo.mandatory);
    const key = `${turn.ownerId}/${turn.turnNumber}`;
    if (key !== noticeKey || (mandatory !== noticeMandatory)) {
      noticeKey = key; turnNotice.hidden = false;
      clearTimeout(noticeTimer); noticeTimer = null;
    }
    document.querySelector('#turn-notice-armies').textContent = String(turn.remaining);
    document.querySelector('#turn-notice-detail').textContent = mandatory
      ? 'Tauschpflicht: Gib zuerst einen gültigen Kartensatz ab.'
      : 'Wähle ein eigenes Land und verteile deine Armeen.';
    document.querySelector('#notice-open-cards').hidden = !mandatory;
    if (mandatory) {
      turnNotice.hidden = false; clearTimeout(noticeTimer); noticeTimer = null;
    } else if (!turnNotice.hidden && noticeTimer === null) {
      noticeTimer = setTimeout(() => { turnNotice.hidden = true; noticeTimer = null; }, 2000);
    }
    noticeMandatory = mandatory;
  }
  globalThis.window?.addEventListener?.('pagehide', () => {
    clearTimeout(noticeTimer); hideTurnReceipt();
  }, { once: true });

  function refresh() {
    attack.sync();
    if (editingAmount && !submittingAmount && ((remote && !turn.canAct)
        || (amountMode === 'occupy' && !turn.pendingConquest)
        || (amountMode === 'reinforce' && (turn.phase !== 'reinforce' || turn.remaining === 0))
        || (amountMode === 'fortify' && (turn.phase !== 'fortify' || turn.fortified)))) closeDeployment();
    const settingUp = turn.phase === 'setup';
    const reinforcing = settingUp || turn.phase === 'reinforce';
    bar.dataset.phase = turn.phase;
    const actor = army(remote?.winner?.member_id || turn.ownerId);
    document.querySelector('#turn-phase').textContent = { setup: 'Startaufstellung', reinforce: 'Verstärken', attack: 'Angreifen', fortify: 'Festigen', ended: 'Zug beendet', completed: 'Spiel beendet' }[turn.phase];
    document.querySelector('#turn-actor-name').textContent = remote?.winner ? `${actor.name} hat gewonnen` : remote ? `${actor.name} ist am Zug` : `Beispielzug · Du bist ${actor.name}`;
    const inventoryOwner = String(turn.inventoryOwnerId || turn.ownerId);
    for (const player of remote?.armies || armies) {
      const lands = territories.filter(territory => turn.owner(territory.id) === player.id);
      const self = player.id === inventoryOwner;
      roster.get(player.id)?.update({...player, layout: 'army', current: player.id === actor.id,
        status: [player.kind === 'test' ? 'Testarmee' : '', self ? 'du' : '', player.id === actor.id ? remote?.winner ? 'Sieger' : 'am Zug' : '', player.eliminated ? 'ausgeschieden' : ''].filter(Boolean).join(' · '),
        stats: {countries: lands.length, troops: lands.reduce((sum, territory) => sum + turn.troops(territory.id), 0)},
        cardCount: player.id === 'neutral' ? null : remote ? player.card_count : turn.hand(player.id).length,
        onCards: self ? () => setCardsExpanded(!cardsExpanded) : null,
      });
    }
    bar.style.setProperty('--active-army', actor.color);
    bar.style.setProperty('--active-ink', actor.ink);
    document.querySelector('.reinforcement-reserve').hidden = !reinforcing || editingAmount || Boolean(remote && !turn.canAct);
    document.querySelector('#reinforcements-left').textContent = String(turn.remaining);
    document.querySelector('#reserve-caption').textContent = settingUp ? (remote.setupInfo.target_owner === 'neutral' ? 'neutral übrig' : 'Starttruppen') : reinforcing ? (turn.remaining ? 'zu verteilen' : 'noch offen') : 'erobert';
    next.hidden = Boolean(remote && !turn.canAct && !remote.winner) || (turn.phase === 'attack' && attack.hasAction)
      || autoAdvancing || (reinforcing && (turn.remaining > 0 || remote?.tradeInfo.mandatory || (mayAutoAdvance() && !autoFailure)));
    next.disabled = endingTurn || (!turn.canAdvance && !(turn.phase === 'ended' && (!remote || turn.canAct)) && !remote?.winner);
    bar.dataset.hasCombat = String(turn.phase === 'attack' && Boolean(attack.sourceId));
    setActionLabel(next, endingTurn ? 'Zug wird beendet …' : remote?.winner ? 'Ergebnis ansehen' : remote && !turn.canAct ? army(turn.ownerId).name + ' ist am Zug' : settingUp ? 'Starttruppen setzen' : reinforcing ? 'Weiter zum Angriff' : turn.phase === 'attack' ? 'Weiter zum Festigen' : 'Zug beenden');
    hint.textContent = remote?.winner ? `${remote.winner.name} gewinnt. ${remote.winner.reason}` : remote?.waitingForMember
      ? `Warten auf ${remote.waitingForMember}. Platz und Armee bleiben für die Rückkehr erhalten.` : remote?.battleRequest
      ? `Die Verteidigung von ${army(String(remote.battleRequest.defender)).name} wird automatisch aufgelöst.`
      : remote?.tradeInfo.mandatory ? 'Tauschpflicht: Öffne deine Karten und tausche zuerst einen gültigen Satz.' : remote && !turn.canAct ? `Warte auf ${actor.name}. Du kannst die Länder und deine Karten ansehen.` : settingUp
      ? remote.setupInfo.target_owner === 'neutral' ? 'Ein Klick auf ein neutrales Land setzt dort sofort eine Einheit.'
        : remote.setupInfo.duel ? `Klicke auf ein eigenes Land: eine Einheit (${remote.setupInfo.own_in_turn + 1}/2), danach eine neutrale Einheit.`
        : 'Ein Klick auf ein eigenes Land setzt sofort eine Einheit. Danach ist die nächste Armee dran.' : !reinforcing
      ? turn.phase === 'attack' ? attack.hint : turn.phase === 'fortify' ? fortify.hint : 'Der Zug wird abgeschlossen und an den nächsten Spieler übergeben.'
      : turn.remaining
        ? 'Wähle eine eigene Marke und verteile deine Truppen.'
        : 'Alle Truppen verteilt. Du kannst jetzt zum Angriff weitergehen.';
    if (editingAmount) {
      document.querySelector('#combat-intent').hidden = true;
      document.querySelector('#battle-result').hidden = true;
      document.querySelector('#roll-attack').hidden = true;
    }
    document.querySelector('.phase-action').hidden = editingAmount;
    updateCards();
    updateTurnNotice();
    if (remote?.lastTurnResult) showTurnReceipt(remote.lastTurnResult);
    onChange();
    if (remote?.winner) setActionLabel(document.querySelector('#play-again'), remote.lobbyInfo?.is_host ? 'Nochmal spielen' : 'Zur Lobby · nochmal spielen');
    if (remote?.winner && !victoryShown) showVictory();
    else if (turn.pendingConquest && (!remote || turn.canAct) && !editingAmount) {
      if (cardsExpanded) setCardsExpanded(false);
      openAmountControls(byId.get(turn.pendingConquest.to), 'occupy');
    }
    if (!mayAutoAdvance() && !autoAdvancing) { autoAttempted = false; autoFailure = ''; }
    if (mayAutoAdvance() && !autoAttempted && !autoAdvancing) void autoAdvance();
    if (autoFailure) hint.textContent = status.textContent = autoFailure;
    if (turn.phase !== 'ended') legacyEndAttempted = false;
    if (remote && turn.canAct && turn.phase === 'ended' && !legacyEndAttempted && !endingTurn) {
      legacyEndAttempted = true;
      void endCurrentTurn();
    }
  }

  function showVictory() {
    const result = remote?.winner;
    if (!result) return;
    victoryShown = true;
    if (missionReveal.open) missionReveal.close();
    if (cardsExpanded) setCardsExpanded(false);
    const player = army(result.member_id);
    if (player) winnerPortrait.update({...player, status: 'Sieger des Feldzugs', metrics: '', current: true});
    document.querySelector('#victory-mode').textContent = `${result.mission ? 'Mission erfüllt' : 'Welteroberung'} · Feldzug beendet`;
    document.querySelector('#victory-title').textContent = `${result.name} gewinnt!`;
    document.querySelector('#victory-reason').textContent = result.reason;
    document.querySelector('#victory-mission').textContent = result.mission ? 'Die siegreiche geheime Mission ist jetzt aufgedeckt.' : '';
    document.querySelector('#victory-mission').hidden = !result.mission;
    const lands = territories.filter(territory => turn.owner(territory.id) === String(result.member_id));
    document.querySelector('#victory-stats').textContent = `${lands.length} Länder · ${lands.reduce((sum, territory) => sum + turn.troops(territory.id), 0)} Truppen · Zug ${result.turn_number || turn.turnNumber}`;
    victoryResult.style.setProperty('--winner-color', player?.color || '#d8ed67');
    status.textContent = `${result.name} hat den Feldzug gewonnen. ${result.reason}`;
    victoryResult.hidden = false;
  }
  document.querySelector('#close-victory').addEventListener('click', () => { victoryResult.hidden = true; });
  document.querySelector('#play-again').addEventListener('click', async () => {
    if (!remote) return;
    try {
      if (remote.lobbyInfo.is_host) await remote.rematch();
      else window.location.assign(remote.lobbyInfo.room_url);
    } catch (failure) { status.textContent = document.querySelector('#victory-reason').textContent = failure.message; }
  });
  document.querySelector('#finish-game').addEventListener('click', async () => {
    if (!remote) return;
    try { await remote.leaveLobby(); }
    catch (failure) { status.textContent = document.querySelector('#victory-reason').textContent = failure.message; }
  });

  function updateAmount(value) {
    if (value !== undefined) amount.value = String(value);
    const count = amount.valueAsNumber;
    const minimum = Number(amount.min);
    const maximum = Number(amount.max);
    const valid = Number.isSafeInteger(count) && count >= minimum && count <= maximum;
    if (valid) slider.value = String(count);
    const allowed = amountMode === 'occupy' ? turn.pendingConquest?.to === targetId
      : amountMode === 'fortify' ? turn.fortifyTargets(transferSourceId).includes(targetId)
      : turn.canReinforce(targetId);
    confirm.disabled = submittingAmount || autoAdvancing || !valid || !allowed;
    document.querySelector('#deployment-less').disabled = valid && count <= minimum;
    document.querySelector('#deployment-more').disabled = valid && count >= maximum;
    error.textContent = valid ? '' : `Wähle eine ganze Zahl von ${minimum} bis ${maximum}.`;
    setActionLabel(confirm, submittingAmount ? 'Wird gespeichert …' : valid ? `${troopLabel(count)} ${{ occupy: 'einrücken', fortify: 'verschieben', reinforce: 'setzen' }[amountMode]}` : 'Truppen wählen');
    if (targetId) {
      const current = turn.troops(targetId);
      document.querySelector('#deployment-preview').textContent = amountMode === 'fortify' && valid
        ? `${turn.troops(transferSourceId) - count} bleiben zurück · ${current + count} im Zielland.`
        : amountMode === 'occupy' && valid && turn.pendingConquest
        ? `${turn.troops(turn.pendingConquest.from) - count} bleiben im Ausgangsland zurück.`
        : valid
        ? `${current} + ${count} = ${current + count} Truppen auf diesem Land`
        : `${current} Truppen auf diesem Land`;
    }
  }

  function closeDeployment() {
    deployment.hidden = true;
    editingAmount = false;
    targetId = null;
    if (amountMode === 'fortify') fortify?.amountClosed();
  }

  async function placeInitial(territory) {
    if (placingInitial || turn.phase !== 'setup' || !turn.canReinforce(territory.id)) return;
    placingInitial = true;
    try {
      const saved = turn.place(territory.id, 1);
      refresh();
      hint.textContent = status.textContent = `Eine Starteinheit auf ${territory.name} wird gesetzt …`;
      await saved;
    } catch (failure) {
      refresh();
      hint.textContent = status.textContent = failure.message;
      return;
    } finally { placingInitial = false; }
    refresh();
    if (remote?.winner) return;
    status.textContent = `Eine Starteinheit auf ${territory.name} gesetzt. ${army(turn.ownerId).name} ist am Zug.`;
  }

  function openAmountControls(territory, mode = 'reinforce', fromId = null) {
    amountMode = mode;
    transferSourceId = fromId;
    const occupy = mode === 'occupy';
    const moving = mode === 'fortify';
    targetId = territory.id;
    const pending = turn.pendingConquest;
    const minimum = occupy ? pending.min : 1;
    const maximum = occupy ? pending.max : moving ? turn.troops(fromId) - 1 : turn.remaining;
    document.querySelector('#deployment-purpose').textContent = occupy ? 'Erobertes Land besetzen' : moving ? 'Eigene Truppen verlegen' : 'Eigenes Land verstärken';
    document.querySelector('#deployment-land').textContent = moving || occupy ? `${byId.get(occupy ? pending.from : fromId).name} → ${territory.name}` : territory.name;
    document.querySelector('#deployment-available').textContent = occupy
      ? `${minimum} bis ${maximum} Truppen aus ${byId.get(pending.from).name}`
      : moving ? `Einmalig ${minimum} bis ${maximum} Truppen verschieben` : `${troopLabel(turn.remaining)} verfügbar`;
    document.querySelector('#cancel-deployment').hidden = occupy;
    document.querySelector('#deployment-amount-label').textContent = occupy ? 'Einrückende Truppen' : moving ? 'Truppen zum Verschieben' : 'Truppen zum Platzieren';
    document.querySelector('#deployment-slider-label').textContent = occupy ? 'Einrückende Truppen per Schieberegler' : moving ? 'Verschiebung per Schieberegler' : 'Anzahl der Verstärkungen';
    amount.min = slider.min = String(minimum);
    amount.max = slider.max = String(maximum);
    updateAmount(minimum);
    editingAmount = true;
    deployment.hidden = false;
    refresh();
  }

  const resultKey = result => result ? `${result.ownerId}/${result.turnNumber}/${result.card?.id || ''}` : '';
  function hideTurnReceipt() {
    clearTimeout(receiptTimer); receiptTimer = null;
    turnReceipt.hidden = true;
    turnReceipt.dataset.stage = 'hidden';
  }
  function showTurnReceipt(result) {
    const key = resultKey(result);
    if (key === receiptKey) return; // Polling must not restart an award or its timers.
    receiptKey = key;
    hideTurnReceipt();
    if (!result.card || (remote && String(result.ownerId) !== String(turn.inventoryOwnerId || result.ownerId))) return;
    document.querySelector('#awarded-card').replaceChildren(countryCard(result.card));
    document.querySelector('#turn-receipt-detail').textContent = `Zug ${result.turnNumber} · ${result.conqueredCount} ${result.conqueredCount === 1 ? 'Land erobert' : 'Länder erobert'}`;
    turnReceipt.dataset.stage = 'center';
    turnReceipt.hidden = false;
    receiptTimer = setTimeout(() => {
      // Measure at departure, so resizing or scrolling during the two seconds
      // still sends the card to its actual owner's portrait, never the next actor.
      const avatar = roster.get(String(result.ownerId))?.anchor?.getBoundingClientRect?.();
      const card = turnReceipt.getBoundingClientRect?.();
      const reduced = globalThis.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
      if (avatar && card && !reduced) {
        turnReceipt.style.setProperty('--receipt-x', `${avatar.left + avatar.width / 2 - card.left - card.width / 2}px`);
        turnReceipt.style.setProperty('--receipt-y', `${avatar.top + avatar.height / 2 - card.top - card.height / 2}px`);
        turnReceipt.dataset.stage = 'flying';
        receiptTimer = setTimeout(hideTurnReceipt, 480);
      } else hideTurnReceipt();
    }, 2000);
  }

  async function endCurrentTurn() {
    if (endingTurn || !['fortify', 'ended'].includes(turn.phase) || (remote && !turn.canAct)) return;
    endingTurn = true; refresh();
    try {
      const result = await turn.endTurn();
      attack.clear(); fortify.clear(); closeDeployment();
      showTurnReceipt(result);
      status.textContent = `Zug beendet${result.card ? ' · Länderkarte erhalten' : ''}. ${army(turn.ownerId).name} ist jetzt am Zug.`;
    } catch (failure) { hint.textContent = status.textContent = failure.message; }
    finally { endingTurn = false; refresh(); }
  }

  amount.addEventListener('input', () => updateAmount());
  slider.addEventListener('input', () => updateAmount(Number(slider.value)));
  document.querySelector('#deployment-less').addEventListener('click', () => updateAmount(Math.max(Number(amount.min), (amount.valueAsNumber || Number(amount.min)) - 1)));
  document.querySelector('#deployment-more').addEventListener('click', () => updateAmount(Math.min(Number(amount.max), (amount.valueAsNumber || 0) + 1)));
  document.querySelector('#cancel-deployment').addEventListener('click', () => { closeDeployment(); refresh(); });
  document.querySelector('#deployment-form').addEventListener('submit', async event => {
    event.preventDefault();
    if (!targetId || submittingAmount || confirm.disabled) return;
    const id = targetId;
    const count = amount.valueAsNumber;
    const mode = amountMode;
    submittingAmount = true; updateAmount();
    try {
      if (mode === 'occupy') await turn.occupy(count);
      else if (mode === 'fortify') await turn.fortify(transferSourceId, id, count);
      else await turn.place(id, count);
    } catch (failure) {
      submittingAmount = false;
      updateAmount();
      error.textContent = failure.message;
      return;
    } finally { submittingAmount = false; }
    closeDeployment();
    if (mode === 'occupy') attack.occupied();
    if (mode === 'fortify') fortify.clear();
    refresh();
    if (remote?.winner) return;
    status.textContent = mode === 'fortify' ? `${troopLabel(count)} nach ${byId.get(id).name} verschoben. Festigen ist für diesen Zug abgeschlossen.`
      : mode === 'occupy'
      ? `${byId.get(id).name} mit ${troopLabel(count)} besetzt. Du kannst weitere Angriffe wählen.`
      : `${troopLabel(count)} auf ${byId.get(id).name} gesetzt. ${troopLabel(turn.remaining)} noch zu verteilen.`;
    document.querySelector(`[data-territory="${id}"]`).focus({ preventScroll: true });
  });
  next.addEventListener('click', async () => {
    if (remote?.winner) { showVictory(); return; }
    if (endingTurn) return;
    if (['fortify', 'ended'].includes(turn.phase)) { await endCurrentTurn(); return; }
    if (!turn.canAdvance) return;
    try { next.disabled = true; await turn.advance(); }
    catch (failure) { refresh(); hint.textContent = status.textContent = failure.message; return; }
    attack.clear();
    fortify.clear();
    closeDeployment();
    refresh();
    if (remote?.winner) return;
    status.textContent = turn.phase === 'attack' ? 'Alle Verstärkungen sind verteilt. Die Angriffsphase wurde erreicht.' : turn.phase === 'fortify' ? 'Die Angriffe wurden beendet. Festigen wurde erreicht.' : 'Der Zug wurde beendet.';
  });
  document.querySelector('#dismiss-turn-receipt').addEventListener('click', () => {
    hideTurnReceipt();
  });
  document.querySelector('#awarded-card').addEventListener('click', showHand);
  document.querySelector('#notice-open-cards').addEventListener('click', showHand);
  document.querySelector('#reset-turn').addEventListener('click', () => {
    turn.reset();
    attack.clear();
    fortify.clear();
    closeDeployment();
    receiptKey = ''; hideTurnReceipt();
    noticeKey = ''; clearTimeout(noticeTimer); noticeTimer = null;
    if (cardsExpanded) setCardsExpanded(false);
    refresh();
    status.textContent = 'Das Offline-Beispiel beginnt erneut. Alle Beispielkarten und Truppen sind zurückgesetzt.';
  });

  attack = createAttackControls({ turn, territories, armies, onChange: refresh, onOccupy: () => openAmountControls(byId.get(turn.pendingConquest.to), 'occupy') });
  fortify = createFortifyControls({ turn, territories, onChange: refresh, onMove: (territory, fromId) => openAmountControls(territory, 'fortify', fromId) });

  return {
    turn,
    attack,
    fortify,
    start() {
      // A saved result is already in the hand. Reloading must not award it again
      // visually; only results received after this page opens are presented.
      receiptKey = resultKey(remote?.lastTurnResult);
      refresh();
      if (remote) {
        let previousActor = turn.ownerId;
        let previousPhase = turn.phase;
        const sync = () => {
          if (turn.winner) { refresh(); return; }
          const setupFinished = previousPhase === 'setup' && turn.phase === 'reinforce';
          previousPhase = turn.phase;
          if (previousActor !== turn.ownerId || setupFinished) {
            previousActor = turn.ownerId;
            attack.clear({ keepDefense: true }); fortify.clear(); closeDeployment();
            if (cardsExpanded) setCardsExpanded(false);
          }
          refresh();
          // Resume an old saved attack once, without restoring its retired dialog.
          if (turn.canDefend && !resolvingDefense) {
            resolvingDefense = true;
            turn.defend().then(refresh).catch(failure => {
              hint.textContent = status.textContent = failure.message;
            }).finally(() => { resolvingDefense = false; });
          }
        };
        turn.subscribe(sync);
        sync();
      }
    },
    selected(territory) {
      if (placingInitial || submittingAmount || autoAdvancing) return;
      if (remote && !turn.canAct) return;
      hideTurnReceipt();
      if (remote?.tradeInfo.mandatory) { showHand(); return; }
      if (turn.pendingConquest) return;
      if (editingAmount) closeDeployment();
      if (turn.phase === 'attack') { attack.selected(territory); return; }
      if (turn.phase === 'fortify') { fortify.selected(territory); return; }
      if (!territory) { refresh(); return; }
      if (!turn.canReinforce(territory.id)) {
        if (['setup', 'reinforce'].includes(turn.phase) && turn.remaining > 0) {
          hint.textContent = remote?.setupInfo?.target_owner === 'neutral' ? 'Wähle eine neutrale Marke für die neutrale Starteinheit.' : 'Dieses Land gehört einer anderen Armee. Wähle eine eigene Marke.';
          status.textContent = hint.textContent;
        }
        return;
      }
      if (turn.phase === 'setup') { void placeInitial(territory); return; }
      hint.textContent = `Wähle die Verstärkung für ${territory.name} und bestätige sie.`;
      openAmountControls(territory);
    },
  };
}
