import { cardCatalog } from './cards.js';

// Requests carry a revision. The server validates and commits every move.
export function createRemoteTurn(config, world) {
  let game = config.game;
  let revision = config.revision;
  let busy = false;
  let leaving = false;
  const listeners = new Set();
  const byId = new Map(cardCatalog(world).map(card => [card.id, {
    ...card, neighbors: world.territories.find(row => row.id === card.id)?.neighbors || [],
  }]));
  function accept(payload) {
    if (payload.game && payload.revision >= revision) {
      game = payload.game;
      revision = payload.revision;
    }
  }
  async function read() {
    const response = await fetch(config.statusUrl, { cache: 'no-store' });
    if (!response.ok) throw new Error('Die Verbindung zum gespeicherten Spielstand fehlt. Bitte neu laden.');
    const payload = await response.json();
    if (['waiting', 'closed'].includes(payload.status)) {
      leaving = true;
      window.location.assign(payload.status === 'waiting' ? config.backUrl : config.overviewUrl);
      return false;
    }
    if (!['playing', 'completed'].includes(payload.status)) throw new Error('Dieser Feldzug ist nicht mehr geöffnet.');
    // Profile equipment can change without a move; it must not touch game revision.
    const changed = payload.revision >= revision && (payload.revision > revision || (payload.game &&
      JSON.stringify(payload.game.armies) !== JSON.stringify(game.armies)));
    accept(payload);
    return changed;
  }
  async function send(action, values = {}) {
    if (busy) throw new Error('Die vorige Aktion wird noch gespeichert.');
    busy = true;
    try {
      const body = new URLSearchParams({ csrf_token: config.csrfToken, revision: String(revision), action, ...values });
      const response = await fetch(config.actionUrl, { method: 'POST', body });
      const payload = await response.json();
      if (!response.ok) {
        await read();
        throw new Error(payload.error || 'Die Aktion konnte nicht gespeichert werden.');
      }
      accept(payload);
      return payload.result;
    } finally { busy = false; }
  }
  async function lifecycle(url) {
    if (busy) throw new Error('Die vorige Aktion wird noch gespeichert.');
    busy = true;
    try {
      const body = new URLSearchParams({ csrf_token: config.csrfToken, revision: String(revision) });
      const response = await fetch(url, { method: 'POST', body, headers: { Accept: 'application/json' } });
      const payload = await response.json();
      if (!response.ok) {
        await read();
        throw new Error(payload.error || 'Die Lobby konnte nicht aktualisiert werden. Bitte erneut versuchen.');
      }
      leaving = true;
      window.location.assign(payload.redirect);
    } finally { busy = false; }
  }
  function targets(id, phase, ownTarget) {
    if (!game.can_act || busy || game.phase !== phase || game.pending_conquest || game.battle_request
        || String(game.territories[id]?.owner) !== String(game.current_member_id)
        || game.territories[id]?.armies < 2 || (phase === 'fortify' && game.fortified)) return [];
    return (byId.get(id)?.neighbors || []).filter(key => (String(game.territories[key].owner) === String(game.current_member_id)) === ownTarget);
  }
  async function poll() {
    try { if (!busy && await read()) for (const listener of listeners) listener(); }
    catch (error) {
      const hint = document.querySelector('#turn-hint');
      if (hint) hint.textContent = error.message;
    }
    if (!leaving) timer = setTimeout(poll, 1200);
  }
  let timer = setTimeout(poll, 1200);
  window.addEventListener('pagehide', () => clearTimeout(timer), { once: true });
  return {
    isRemote: true,
    get missionKey() { return `conquest:mission:${config.gameKey || config.statusUrl}:${game.inventory_owner_id}`; },
    get armies() { return game.armies; },
    get ownerId() { return String(game.current_member_id); },
    get inventoryOwnerId() { return game.inventory_owner_id; },
    get canAct() { return game.can_act; },
    get canDefend() { return game.can_defend; },
    get battleRequest() { return game.battle_request; },
    get lastBattle() { return game.last_battle; },
    get developer() { return game.developer; },
    get winner() { return game.winner; },
    get lobbyInfo() { return game.lobby; },
    get waitingForMember() { return game.waiting_for_member; },
    leaveLobby() { return lifecycle(game.lobby.leave_url); },
    rematch() { return lifecycle(game.lobby.rematch_url); },
    get setupInfo() { return game.setup; },
    get reinforcementDetail() {
      return `${game.reinforcement.base} Grundverstärkungen` + game.reinforcement.continents.map(row => ` + ${row.bonus} ${row.name}`).join('') + (game.reinforcement.cards ? ` + ${game.reinforcement.cards} aus Kartentausch` : '') + '. Verteile sie auf deine eigenen Länder.';
    },
    get tradeInfo() { return game.trade || { can_trade: false, mandatory: false, next_value: 4, count: 0 }; },
    trade(cards) { return send('trade', { cards: JSON.stringify(cards) }); },
    get ownMission() { return game.inventory.mission; },
    get total() { return game.phase === 'setup' ? game.remaining : game.reinforcement.total; },
    get remaining() { return game.remaining; },
    get phase() { return game.phase; },
    get canAdvance() { return game.can_act && !busy && !game.trade?.mandatory && !game.pending_conquest && !game.battle_request &&
      ((game.phase === 'reinforce' && game.remaining === 0) || ['attack', 'fortify'].includes(game.phase)); },
    get pendingConquest() { return game.pending_conquest; },
    get conqueredCount() { return game.conquered_count; },
    get fortified() { return game.fortified; },
    get turnNumber() { return game.turn_number; },
    get nextOwnerId() { return game.next_owner_id; },
    get endResult() { return game.end_result ? { ...game.end_result, card: byId.get(game.end_result.card) || null } : null; },
    get lastTurnResult() { return game.last_turn_result ? { ...game.last_turn_result, card: byId.get(game.last_turn_result.card) || null } : null; },
    hand() { return game.inventory.territory_cards.map(card => byId.get(card.id)); },
    owner(id) { return String(game.territories[id]?.owner); },
    troops(id) { return game.territories[id]?.armies || 0; },
    canReinforce(id) { return game.can_act && !busy && !game.trade?.mandatory && ['setup', 'reinforce'].includes(game.phase) && game.remaining > 0
      && String(game.territories[id]?.owner) === String(game.phase === 'setup' ? game.setup.target_owner : game.current_member_id); },
    attackTargets(id) { return targets(id, 'attack', false); },
    fortifyTargets(id) { return targets(id, 'fortify', true); },
    place(to, count) { return send('place', { to, count }); },
    advance() { return send('advance'); },
    attack(from, to, dice) { return send('attack', { from, to, dice }); },
    occupy(count) { return send('occupy', { count }); },
    fortify(from, to, count) { return send('fortify', { from, to, count }); },
    passTurn() { return send('pass'); },
    async endTurn() {
      const result = (await send('finish')).endResult;
      return {...result, card: byId.get(result.card) || null};
    },
    defend() { return send('defend'); },
    subscribe(listener) { listeners.add(listener); },
  };
}
