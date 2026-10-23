(() => {
  const lobby = document.querySelector("[data-card-lobby]");
  const settings = document.querySelector("[data-card-settings]");
  if (lobby) {
    const pollLobby = async () => {
      try {
        const response = await fetch(lobby.dataset.statusUrl, { cache: "no-store", headers: { Accept: "application/json" } });
        if (!response.ok) return window.location.reload();
        const state = await response.json();
        if (state.status !== "waiting" || String(state.revision) !== lobby.dataset.revision || String(state.members.length) !== lobby.dataset.memberCount) return window.location.reload();
      } catch (_) {}
      window.setTimeout(pollLobby, 900);
    };
    window.setTimeout(pollLobby, 900);
  }
  if (settings) {
    const select = settings.querySelector("select[name='deck_size']");
    const points = settings.querySelector("input[name='starting_points']");
    const label = settings.querySelector("[data-card-autosave]");
    const saveSettings = async () => {
      label.textContent = "Speichert …";
      try {
        const response = await fetch(settings.dataset.settingsUrl, { method: "POST", body: new FormData(settings) });
        if (!response.ok) throw new Error("save");
        label.textContent = "Gespeichert.";
      } catch (_) { label.textContent = "Konnte nicht gespeichert werden."; }
    };
    select?.addEventListener("change", saveSettings);
    points?.addEventListener("change", saveSettings);
  }

  const room = document.querySelector("[data-card-room]");
  if (!room) return;
  const csrf = room.querySelector("[data-csrf]").value;
  const layers = new Map(Array.from(room.querySelectorAll("[data-card-layer]")).map((layer) => [layer.dataset.cardLayer, layer]));
  const note = room.querySelector("[data-card-note]");
  const banner = room.querySelector("[data-action-banner]");
  const dealCount = room.querySelector("[data-deal-count]");
  const dealCountOutput = room.querySelector("[data-deal-count-output]");
  const dealButton = room.querySelector("[data-table-action='deal']");
  const betControl = room.querySelector("[data-bet-control]");
  const betAmount = room.querySelector("[data-bet-amount]");
  const betOutput = room.querySelector("[data-bet-output]");
  const bidButton = room.querySelector("[data-bid-button]");
  const callButton = room.querySelector("[data-call-button]");
  let latestBankroll = null;
  let revision = -1;
  let dragging = false;
  let noteTimer = null;
  let currentActionKey = "";
  let latestCards = [];
  let latestMembers = [];

  const fitRoom = () => {
    const scale = Math.min(window.innerWidth / 1920, window.innerHeight / 900);
    const left = Math.max(0, (window.innerWidth - 1920 * scale) / 2);
    const top = Math.max(0, (window.innerHeight - 900 * scale) / 2);
    room.style.transformOrigin = "0 0";
    room.style.transform = `translate(${left}px, ${top}px) scale(${scale})`;
  };
  fitRoom();
  window.addEventListener("resize", fitRoom);

  const updateDealControl = () => {
    const deckSize = latestCards.filter((card) => card.zone === "deck").length;
    const maximum = latestMembers.length ? Math.floor(deckSize / latestMembers.length) : 0;
    const safeMaximum = Math.max(1, maximum);
    dealCount.max = String(safeMaximum);
    dealCount.value = String(Math.min(Number(dealCount.value), safeMaximum));
    dealCount.disabled = maximum < 1;
    dealButton.disabled = maximum < 1;
    dealCountOutput.textContent = maximum < 1 ? "0" : dealCount.value;
  };
  dealCount.addEventListener("input", () => { dealCountOutput.textContent = dealCount.value; });

  const postAction = async (values) => {
    const data = new FormData();
    data.set("csrf_token", csrf);
    Object.entries(values).forEach(([key, value]) => data.set(key, String(value)));
    const response = await fetch(room.dataset.actionUrl, { method: "POST", body: data, headers: { Accept: "application/json" } });
    if (!response.ok) throw new Error("action failed");
    return response.json();
  };

  const cardElement = (card) => {
    const element = document.createElement("div");
    element.className = `playing-card${card.face_up ? " face-up" : ""}`;
    const ownZone = `player:${room.dataset.memberId}`;
    element.draggable = !card.zone.startsWith("player:") || card.zone === ownZone;
    element.dataset.cardId = card.id;
    element.dataset.zone = card.zone;
    if (card.zone === "table") element.title = "Rechtsklick: Karte umdrehen";
    element.style.left = `${card.x}%`;
    element.style.top = `${card.y}%`;
    element.style.setProperty("--card-z", String(card.z));
    element.style.setProperty("--card-r", `${card.rotation || 0}deg`);
    const face = card.rank === null
      ? `<div class="playing-card-front"></div>`
      : card.joker
      ? `<div class="playing-card-front ${card.color}"><span class="playing-card-joker">★ JOKER ★</span></div>`
      : `<div class="playing-card-front ${card.color}"><span class="playing-card-corner">${card.rank}<i>${card.symbol}</i></span><span class="playing-card-suit">${card.symbol}</span><span class="playing-card-corner bottom">${card.rank}<i>${card.symbol}</i></span></div>`;
    element.innerHTML = `<div class="playing-card-inner"><div class="playing-card-back"></div>${face}</div>`;
    element.addEventListener("dragstart", (event) => {
      if (!element.draggable) { event.preventDefault(); return; }
      dragging = true;
      element.classList.add("is-dragging");
      event.dataTransfer.effectAllowed = "move";
      event.dataTransfer.setData("text/plain", card.id);
    });
    element.addEventListener("dragend", () => { dragging = false; element.classList.remove("is-dragging"); });
    element.addEventListener("contextmenu", async (event) => {
      if (card.zone !== "table") return;
      event.preventDefault();
      try { await postAction({ action: "flip", card_id: card.id }); await poll(true); } catch (_) {}
    });
    return element;
  };

  const renderCards = (cards) => {
    latestCards = cards;
    layers.forEach((layer) => layer.replaceChildren());
    const tops = new Map();
    const handPositions = new Map();
    const ownZone = `player:${room.dataset.memberId}`;
    const handZones = [...new Set(cards.filter((card) => card.zone.startsWith("player:")).map((card) => card.zone))];
    handZones.forEach((zone) => {
      const hand = cards.filter((card) => card.zone === zone).sort((a, b) => a.z - b.z);
      if (zone !== ownZone) {
        hand.forEach((card, index) => handPositions.set(card.id, { x: Math.min(94, 10 + index * 5), y: 58 }));
        return;
      }
      const rows = hand.length > 18 ? [hand.slice(0, Math.ceil(hand.length / 2)), hand.slice(Math.ceil(hand.length / 2))] : [hand];
      rows.forEach((row, rowIndex) => {
        const step = row.length > 1 ? Math.min(5, 88 / (row.length - 1)) : 0;
        const start = 50 - ((row.length - 1) * step) / 2;
        row.forEach((card, index) => handPositions.set(card.id, { x: start + index * step, y: rows.length === 1 ? 58 : (rowIndex ? 70 : 37) }));
      });
    });
    cards.forEach((card) => {
      if ((card.zone === "deck" || card.zone === "discard") && (!tops.has(card.zone) || tops.get(card.zone).z < card.z)) tops.set(card.zone, card);
    });
    cards.forEach((card) => {
      if ((card.zone === "deck" || card.zone === "discard") && tops.get(card.zone)?.id !== card.id) return;
      const position = handPositions.get(card.id);
      const displayCard = position ? { ...card, x: position.x, y: position.y } : card;
      layers.get(card.zone)?.append(cardElement(displayCard));
    });
    room.querySelector("[data-deck-count]").textContent = String(cards.filter((card) => card.zone === "deck").length);
    room.querySelector("[data-discard-count]").textContent = String(cards.filter((card) => card.zone === "discard").length);
    updateDealControl();
  };

  const renderBankroll = (bankroll) => {
    latestBankroll = bankroll;
    const enabled = Boolean(bankroll);
    room.querySelectorAll("[data-bankroll-for]").forEach((element) => {
      const key = element.dataset.bankrollFor;
      element.hidden = !enabled;
      if (enabled) element.querySelector("output").textContent = String(bankroll.balances[key] ?? 0);
    });
    room.querySelectorAll("[data-bid-for]").forEach((element) => {
      const key = element.dataset.bidFor;
      element.hidden = !enabled;
      if (enabled) element.querySelector("output").textContent = String(bankroll.bids[key] ?? 0);
    });
    room.querySelectorAll("[data-collect-pot]").forEach((button) => {
      button.hidden = !enabled;
      button.disabled = !enabled || button.dataset.collectPot !== room.dataset.memberId || Number(bankroll?.pot || 0) < 1 || Boolean(bankroll?.claim);
    });
    const pot = room.querySelector("[data-card-pot]");
    pot.hidden = !enabled;
    betControl.hidden = !enabled;
    if (!enabled) return;
    pot.querySelector("output").textContent = String(bankroll.pot || 0);
    const balance = Number(bankroll.balances[room.dataset.memberId] || 0);
    const ownBid = Number(bankroll.bids[room.dataset.memberId] || 0);
    const highestBid = Math.max(0, ...Object.values(bankroll.bids).map(Number));
    const callAmount = Math.max(0, highestBid - ownBid);
    betAmount.max = String(Math.max(1, balance));
    betAmount.value = String(Math.min(Number(betAmount.value), Math.max(1, balance)));
    betAmount.disabled = balance < 1;
    bidButton.disabled = balance < 1;
    callButton.disabled = callAmount < 1 || balance < 1;
    callButton.title = callAmount < 1 ? "Du bist bereits gleichauf." : `${Math.min(callAmount, balance)} zum Mitgehen einstellen`;
    betOutput.textContent = balance < 1 ? "0" : betAmount.value;
    const request = room.querySelector("[data-pot-request]");
    const claim = bankroll.claim;
    request.hidden = !claim;
    if (claim) {
      const requester = latestMembers.find((member) => String(member.id) === String(claim.requester));
      const isRequester = String(claim.requester) === room.dataset.memberId;
      const alreadyApproved = (claim.approvals || []).map(String).includes(room.dataset.memberId);
      request.querySelector("[data-pot-request-text]").textContent = isRequester
        ? `Warte auf die einstimmige Freigabe für ${bankroll.pot} Punkte.`
        : `${requester?.name || "Ein Spieler"} möchte ${bankroll.pot} Punkte aus dem Pot einsammeln.`;
      request.querySelectorAll("[data-pot-vote]").forEach((button) => { button.hidden = isRequester || alreadyApproved; });
    }
  };

  const animateAction = (action) => {
    if (!action) {
      room.classList.remove("is-collecting", "is-shuffling");
      banner.hidden = true;
      currentActionKey = "";
      return;
    }
    const key = `${action.type}:${action.started_at}`;
    if (key === currentActionKey) return;
    currentActionKey = key;
    banner.hidden = false;
    banner.textContent = action.type === "collect" ? "Karten werden eingesammelt …" : "Ablagestapel wird gemischt …";
    room.classList.toggle("is-collecting", action.type === "collect");
    room.classList.toggle("is-shuffling", action.type === "shuffle");
    if (action.type === "collect") {
      const target = room.querySelector("[data-drop-zone='discard']").getBoundingClientRect();
      room.querySelectorAll(".playing-card").forEach((card) => {
        const rect = card.getBoundingClientRect();
        card.style.setProperty("--gather-x", `${target.left + target.width / 2 - (rect.left + rect.width / 2)}px`);
        card.style.setProperty("--gather-y", `${target.top + target.height / 2 - (rect.top + rect.height / 2)}px`);
      });
    }
  };

  const poll = async (force = false) => {
    if (dragging || document.hidden) return;
    try {
      const response = await fetch(room.dataset.statusUrl, { cache: "no-store", headers: { Accept: "application/json" } });
      if (response.status === 404 || response.status === 410) return window.location.assign(room.dataset.indexUrl);
      if (!response.ok) return;
      const state = await response.json();
      latestMembers = state.members || [];
      updateDealControl();
      if (state.status !== "playing") return window.location.reload();
      if (force || state.revision !== revision) {
        revision = state.revision;
        renderCards(state.cards || []);
        if (document.activeElement !== note) note.value = state.note || "";
      }
      renderBankroll(state.bankroll);
      animateAction(state.action);
    } catch (_) {}
  };

  room.querySelectorAll("[data-drop-zone]").forEach((zone) => {
    zone.addEventListener("dragover", (event) => { event.preventDefault(); event.dataTransfer.dropEffect = "move"; zone.classList.add("is-drop-target"); });
    zone.addEventListener("dragleave", () => zone.classList.remove("is-drop-target"));
    zone.addEventListener("drop", async (event) => {
      event.preventDefault();
      zone.classList.remove("is-drop-target");
      const cardId = event.dataTransfer.getData("text/plain");
      if (!cardId) return;
      const rect = zone.getBoundingClientRect();
      const x = ((event.clientX - rect.left) / rect.width) * 100;
      const y = ((event.clientY - rect.top) / rect.height) * 100;
      try { await postAction({ action: "move", card_id: cardId, zone: zone.dataset.dropZone, x, y }); await poll(true); } catch (_) { await poll(true); }
    });
  });

  const dealWithCompatibleActions = async (count) => {
    try {
      await postAction({ action: "deal", count });
      return;
    } catch (_) {
      const deck = latestCards.filter((card) => card.zone === "deck").sort((a, b) => b.z - a.z);
      if (deck.length < latestMembers.length * count) throw new Error("not enough cards");
      let deckIndex = 0;
      for (let round = 0; round < count; round += 1) {
        for (const member of latestMembers) {
          const zone = `player:${member.id}`;
          const handSize = latestCards.filter((card) => card.zone === zone).length + round;
          await postAction({ action: "move", card_id: deck[deckIndex].id, zone, x: Math.min(94, 10 + handSize * 5), y: 58 });
          deckIndex += 1;
        }
      }
    }
  };

  const clearTableCompatible = async () => {
    try {
      await postAction({ action: "clear_table" });
    } catch (_) {
      const tableCards = latestCards.filter((card) => card.zone === "table").sort((a, b) => a.z - b.z);
      if (!tableCards.length) throw new Error("table empty");
      for (const card of tableCards) await postAction({ action: "move", card_id: card.id, zone: "discard", x: 50, y: 50 });
    }
  };

  room.querySelectorAll("[data-table-action]").forEach((button) => button.addEventListener("click", async () => {
    button.disabled = true;
    try {
      if (button.dataset.tableAction === "deal") await dealWithCompatibleActions(Number(dealCount.value));
      else if (button.dataset.tableAction === "clear_table") await clearTableCompatible();
      else await postAction({ action: button.dataset.tableAction });
      await poll(true);
    } catch (_) { await poll(true); }
    window.setTimeout(() => {
      if (button.dataset.tableAction === "deal") updateDealControl();
      else button.disabled = false;
    }, 1100);
  }));

  betAmount.addEventListener("input", () => { betOutput.textContent = betAmount.value; });
  callButton.addEventListener("click", () => {
    if (!latestBankroll) return;
    const ownKey = room.dataset.memberId;
    const ownBid = Number(latestBankroll.bids[ownKey] || 0);
    const highestBid = Math.max(0, ...Object.values(latestBankroll.bids).map(Number));
    const balance = Number(latestBankroll.balances[ownKey] || 0);
    const missing = Math.min(Math.max(0, highestBid - ownBid), balance);
    if (missing < 1) return;
    betAmount.value = String(missing);
    betOutput.textContent = String(missing);
  });
  bidButton.addEventListener("click", async () => {
    bidButton.disabled = true;
    try { await postAction({ action: "bid", amount: betAmount.value }); await poll(true); } catch (_) { await poll(true); }
  });
  room.querySelectorAll("[data-collect-pot]").forEach((button) => button.addEventListener("click", async () => {
    if (button.dataset.collectPot !== room.dataset.memberId) return;
    button.disabled = true;
    try { await postAction({ action: "claim_pot" }); await poll(true); }
    catch (_) {
      banner.textContent = "Collect konnte nicht gestartet werden.";
      banner.hidden = false;
      window.setTimeout(() => { banner.hidden = true; }, 2400);
      await poll(true);
    }
  }));
  room.querySelectorAll("[data-pot-vote]").forEach((button) => button.addEventListener("click", async () => {
    try { await postAction({ action: "vote_pot", vote: button.dataset.potVote }); await poll(true); } catch (_) { await poll(true); }
  }));

  const clampNote = (value) => value.replace(/\r/g, "").split("\n").slice(0, 8).map((line) => line.slice(0, 40)).join("\n");
  note.addEventListener("input", () => {
    const clean = clampNote(note.value);
    if (clean !== note.value) note.value = clean;
    window.clearTimeout(noteTimer);
    noteTimer = window.setTimeout(() => postAction({ action: "note", note: note.value }).catch(() => {}), 250);
  });
  note.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && note.value.split("\n").length >= 8) event.preventDefault();
  });

  room.querySelector("[data-leave-form]")?.addEventListener("submit", (event) => {
    if (!window.confirm("Möchtest du die Playtable wirklich verlassen?")) event.preventDefault();
  });
  room.querySelector("[data-end-form]")?.addEventListener("submit", (event) => {
    if (!window.confirm("Möchtest du die Lobby wirklich für alle beenden?")) event.preventDefault();
  });

  poll(true);
  window.setInterval(poll, 450);
  document.addEventListener("visibilitychange", () => { if (!document.hidden) poll(true); });
})();
