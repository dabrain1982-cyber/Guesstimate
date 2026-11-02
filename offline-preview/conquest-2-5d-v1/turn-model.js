// Local interaction prototype only. The live game will continue to validate
// moves on its server; this fixture never loads or saves a real match.
export function randomIndex(size) {
  if (!Number.isSafeInteger(size) || size < 1 || size > 4294967296) throw new Error('Ungültige Zufallsauswahl.');
  const word = new Uint32Array(1);
  const limit = Math.floor(4294967296 / size) * size;
  do { globalThis.crypto.getRandomValues(word); } while (word[0] >= limit);
  return word[0] % size;
}
export function rollD6() { return randomIndex(6) + 1; }

export function createPreviewTurn(territories, { ownerId = 'gold', total = 6, rollDie = rollD6, drawIndex = randomIndex } = {}) {
  if (!Number.isSafeInteger(total) || total < 0) throw new Error('Ungültige Verstärkungszahl.');
  const initial = new Map(territories.map(territory => [territory.id, {
    ownerId: territory.owner.id, armies: territory.armies,
  }]));
  if (!territories.some(territory => territory.owner.id === ownerId)) throw new Error('Die aktive Armee besitzt kein Land.');
  let armies = new Map([...initial].map(([id, territory]) => [id, territory.armies]));
  let owners = new Map([...initial].map(([id, territory]) => [id, territory.ownerId]));
  const byId = new Map(territories.map(territory => [territory.id, territory]));
  let remaining = total;
  let phase = 'reinforce';
  let pending = null;
  let conqueredCount = 0;
  let fortified = false;
  let turnNumber = 1;
  let endResult = null;
  const initialOwnerId = ownerId;
  const playerOrder = [...new Set(territories.map(territory => territory.owner.id))];
  const initialDeck = territories.map((territory, index) => ({ id: territory.id, name: territory.name, type: ['Infanterie', 'Reiter', 'Geschütz'][index % 3] }));
  let deck = [...initialDeck];
  let hands = new Map(playerOrder.map(id => [id, []]));

  function nextOwner() {
    const start = playerOrder.indexOf(ownerId);
    for (let offset = 1; offset <= playerOrder.length; offset++) {
      const candidate = playerOrder[(start + offset) % playerOrder.length];
      if ([...owners.values()].includes(candidate)) return candidate;
    }
    return ownerId;
  }

  function fortifyTargets(id) {
    if (phase !== 'fortify' || fortified || owners.get(id) !== ownerId || armies.get(id) < 2) return [];
    return (byId.get(id)?.neighbors || []).filter(neighbor => owners.get(neighbor) === ownerId);
  }

  function finishTurn() {
    if (phase !== 'fortify' || pending) throw new Error('Der Zug kann erst nach Angreifen und Besetzen beendet werden.');
    let card = null;
    if (conqueredCount > 0) {
      if (!deck.length) throw new Error('Der Länderkartenstapel ist leer. Der Zug wurde noch nicht beendet.');
      const index = drawIndex(deck.length);
      if (!Number.isInteger(index) || index < 0 || index >= deck.length) throw new Error('Ungültige Kartenziehung.');
      card = deck[index];
      deck.splice(index, 1);
      hands.get(ownerId).push(card);
    }
    phase = 'ended';
    endResult = Object.freeze({ ownerId, turnNumber, conqueredCount, fortified, card: card ? Object.freeze({ ...card }) : null });
    return endResult;
  }

  function attackTargets(id) {
    if (phase !== 'attack' || pending || owners.get(id) !== ownerId || armies.get(id) < 2) return [];
    return (byId.get(id)?.neighbors || []).filter(neighbor => owners.get(neighbor) !== ownerId);
  }

  function dice(count) {
    return Array.from({ length: count }, () => {
      const value = rollDie();
      if (!Number.isInteger(value) || value < 1 || value > 6) throw new Error('Ungültiges Würfelergebnis.');
      return value;
    }).sort((a, b) => b - a);
  }

  return Object.freeze({
    get ownerId() { return ownerId; },
    get total() { return total; },
    get remaining() { return remaining; },
    get phase() { return phase; },
    get canAdvance() { return (phase === 'reinforce' && remaining === 0) || (phase === 'attack' && !pending) || phase === 'fortify'; },
    get pendingConquest() { return pending ? { ...pending } : null; },
    get conqueredCount() { return conqueredCount; },
    get fortified() { return fortified; },
    get turnNumber() { return turnNumber; },
    get nextOwnerId() { return nextOwner(); },
    get endResult() { return endResult; },
    get deckCount() { return deck.length; },
    hand(id = ownerId) { return (hands.get(id) || []).map(card => ({ ...card })); },
    owner(id) { return owners.get(id); },
    attackTargets,
    fortifyTargets,
    finishTurn,
    troops(id) {
      if (!armies.has(id)) throw new Error('Unbekanntes Land.');
      return armies.get(id);
    },
    canReinforce(id) {
      return phase === 'reinforce' && remaining > 0 && owners.get(id) === ownerId;
    },
    place(id, count) {
      if (phase !== 'reinforce') throw new Error('Die Verstärkungsphase ist beendet.');
      if (owners.get(id) !== ownerId) throw new Error('Du kannst nur eigene Länder verstärken.');
      if (!Number.isSafeInteger(count) || count < 1 || count > remaining) {
        throw new Error(`Wähle eine ganze Zahl zwischen 1 und ${remaining}.`);
      }
      const next = armies.get(id) + count;
      if (!Number.isSafeInteger(next)) throw new Error('Zu viele Truppen auf diesem Land.');
      armies.set(id, next);
      remaining -= count;
      return next;
    },
    advance() {
      if (pending) throw new Error('Lass zuerst Truppen in das eroberte Land einrücken.');
      if (phase === 'attack') { phase = 'fortify'; return; }
      if (phase === 'fortify') return finishTurn();
      if (phase !== 'reinforce') throw new Error('Die Phase wurde bereits gewechselt.');
      if (remaining !== 0) throw new Error('Verteile zuerst alle Verstärkungen.');
      phase = 'attack';
    },
    attack(from, to, attackDice) {
      if (phase !== 'attack') throw new Error('Angriffe sind nur in der Angriffsphase möglich.');
      if (pending) throw new Error('Lass zuerst Truppen in das eroberte Land einrücken.');
      if (!attackTargets(from).includes(to)) throw new Error('Wähle ein eigenes Land mit mindestens zwei Truppen und ein benachbartes feindliches Ziel.');
      const maximum = Math.min(3, armies.get(from) - 1);
      if (!Number.isInteger(attackDice) || attackDice < 1 || attackDice > maximum) throw new Error(`Wähle 1 bis ${maximum} Angriffswürfel.`);
      const defenseDice = Math.min(2, armies.get(to));
      const attackRolls = dice(attackDice);
      const defenseRolls = dice(defenseDice);
      let attackerLoss = 0, defenderLoss = 0;
      for (let index = 0; index < Math.min(attackDice, defenseDice); index++) {
        if (attackRolls[index] > defenseRolls[index]) defenderLoss++;
        else attackerLoss++;
      }
      armies.set(from, armies.get(from) - attackerLoss);
      armies.set(to, armies.get(to) - defenderLoss);
      const conquered = armies.get(to) === 0;
      if (conquered) {
        owners.set(to, ownerId);
        pending = { from, to, min: attackDice, max: armies.get(from) - 1 };
      }
      return { from, to, attackRolls, defenseRolls, attackerLoss, defenderLoss, conquered };
    },
    occupy(count) {
      if (!pending) throw new Error('Es wartet kein erobertes Land auf Truppen.');
      if (!Number.isSafeInteger(count) || count < pending.min || count > pending.max) {
        throw new Error(`Lass ${pending.min} bis ${pending.max} Truppen einrücken.`);
      }
      armies.set(pending.from, armies.get(pending.from) - count);
      armies.set(pending.to, count);
      pending = null;
      conqueredCount++;
    },
    fortify(from, to, count) {
      if (!fortifyTargets(from).includes(to)) throw new Error('Festigen ist einmal pro Zug zwischen benachbarten eigenen Ländern möglich.');
      if (!Number.isSafeInteger(count) || count < 1 || count >= armies.get(from)) throw new Error('Mindestens eine Truppe muss im Ausgangsland bleiben.');
      const next = armies.get(to) + count;
      if (!Number.isSafeInteger(next)) throw new Error('Zu viele Truppen auf dem Zielland.');
      armies.set(from, armies.get(from) - count);
      armies.set(to, next);
      fortified = true;
    },
    passTurn() {
      if (phase !== 'ended') throw new Error('Beende zuerst den aktuellen Zug.');
      ownerId = nextOwner();
      turnNumber++;
      remaining = total;
      phase = 'reinforce';
      conqueredCount = 0;
      fortified = false;
      endResult = null;
      return ownerId;
    },
    endTurn() {
      if (phase === 'fortify') finishTurn();
      if (phase !== 'ended') throw new Error('Beende zuerst deine Angriffe und die notwendige Besetzung.');
      const result = endResult;
      this.passTurn();
      return result;
    },
    reset() {
      armies = new Map([...initial].map(([id, territory]) => [id, territory.armies]));
      owners = new Map([...initial].map(([id, territory]) => [id, territory.ownerId]));
      remaining = total;
      phase = 'reinforce';
      pending = null;
      conqueredCount = 0;
      fortified = false;
      turnNumber = 1;
      ownerId = initialOwnerId;
      endResult = null;
      deck = [...initialDeck];
      hands = new Map(playerOrder.map(id => [id, []]));
    },
  });
}
