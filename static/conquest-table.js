(() => {
  const app = document.querySelector("[data-conquest-app]");
  if (!app) return;

  const stage = app.querySelector("[data-stage]");
  const scene = app.querySelector("[data-scene]");
  const board = app.querySelector("[data-board]");
  const territoryLayer = app.querySelector("[data-territories]");
  const floatingLayer = app.querySelector("[data-floating-cards]");
  const info = app.querySelector("[data-info]");
  const assetRoot = app.dataset.assetsRoot;
  const continentColors = {
    nordamerika: "#d9bd3f", suedamerika: "#d96b3f", europa: "#506bb7",
    afrika: "#bd4961", asien: "#5b9f62", australien: "#71518f",
  };
  const camera = { x: 0, y: 28, zoom: 0.88, tilt: 52, turn: 0 };
  let activeStyle = app.dataset.boardStyle || "klassisch";
  let activeCardStyle = app.dataset.cardStyle || activeStyle;
  let world = null;
  let gameState = null;
  let stageDrag = null;
  let territoryPile = [];
  let missionPile = [];
  let cardSerial = 0;
  let diceEngine = null;

  const asset = (path) => `${assetRoot}${path}`;
  const clamp = (value, minimum, maximum) => Math.max(minimum, Math.min(maximum, value));
  const shuffledRange = (length) => {
    const values = Array.from({ length }, (_, index) => index);
    for (let index = values.length - 1; index > 0; index -= 1) {
      const swap = Math.floor(Math.random() * (index + 1));
      [values[index], values[swap]] = [values[swap], values[index]];
    }
    return values;
  };

  const applyCamera = (animate = true) => {
    stage.classList.toggle("is-dragging", !animate);
    app.style.setProperty("--scene-x", `${camera.x}px`);
    app.style.setProperty("--scene-y", `${camera.y}px`);
    app.style.setProperty("--scene-zoom", camera.zoom.toFixed(3));
    app.style.setProperty("--scene-tilt", `${camera.tilt}deg`);
    app.style.setProperty("--scene-turn", `${camera.turn}deg`);
    if (animate) window.setTimeout(() => stage.classList.remove("is-dragging"), 300);
  };

  const resetCamera = (view = "center") => {
    camera.x = 0;
    camera.y = view === "top" ? 30 : 28;
    camera.zoom = view === "top" ? 0.82 : 0.88;
    camera.tilt = view === "top" ? 0 : 52;
    camera.turn = 0;
    applyCamera(true);
  };

  const stylePaths = (boardStyle, cardStyle = boardStyle) => ({
    board: asset(`boards/welt-${boardStyle}.webp`),
    territorySheet: asset(`decks/laender-${cardStyle}/sheet-1.webp`),
    territoryBack: asset(`decks/laender-${cardStyle}/back.webp`),
    missionSheet: asset(`decks/missionen-${cardStyle}/sheet-1.webp`),
    missionBack: asset(`decks/missionen-${cardStyle}/back.webp`),
  });

  const applyStyle = (style, cardStyle = style) => {
    activeStyle = style;
    activeCardStyle = cardStyle;
    const paths = stylePaths(style, cardStyle);
    board.src = paths.board;
    app.style.setProperty("--territory-back", `url("${paths.territoryBack}")`);
    app.style.setProperty("--mission-back", `url("${paths.missionBack}")`);
    app.querySelector("[data-deck='territory'] .conquest-card-back").style.setProperty("--deck-back", `url("${paths.territoryBack}")`);
    app.querySelector("[data-deck='mission'] .conquest-card-back").style.setProperty("--deck-back", `url("${paths.missionBack}")`);
    app.querySelectorAll("[data-style]").forEach((button) => button.classList.toggle("is-active", button.dataset.style === style));
    app.querySelectorAll(".conquest-drawn-card").forEach((card) => {
      const mission = card.dataset.kind === "mission";
      card.dataset.sheet = mission ? paths.missionSheet : paths.territorySheet;
      card.style.backgroundImage = `url("${card.dataset.sheet}")`;
      card.style.setProperty("--card-back", `url("${mission ? paths.missionBack : paths.territoryBack}")`);
    });
  };

  const projectedPosition = ([longitude, latitude]) => ({
    x: (70 + (longitude + 180) / 360 * (2048 - 140)) / 2048 * 100,
    y: (105 + (85 - latitude) / 145 * (1280 - 220)) / 1280 * 100,
  });

  const selectTerritory = (territory) => {
    const neighbors = new Set(territory.neighbors);
    territoryLayer.querySelectorAll("button").forEach((button) => {
      button.classList.toggle("is-selected", button.dataset.territory === territory.id);
      button.classList.toggle("is-neighbor", neighbors.has(button.dataset.territory));
    });
    const names = territory.neighbors.map((id) => world.territories.find((item) => item.id === id)?.name).filter(Boolean);
    const continent = world.continents.find((item) => item.id === territory.continent);
    info.innerHTML = `<small>${continent.name.toUpperCase()} · BONUS ${continent.bonus}</small><strong>${territory.name}</strong><span>Nachbarn: ${names.join(", ")}</span>`;
  };

  const renderTerritories = () => {
    territoryLayer.replaceChildren(...world.territories.map((territory) => {
      const point = projectedPosition(territory.label);
      const button = document.createElement("button");
      button.type = "button";
      button.className = "conquest-territory";
      button.dataset.territory = territory.id;
      button.title = territory.name;
      button.setAttribute("aria-label", territory.name);
      button.style.left = `${point.x}%`;
      button.style.top = `${point.y}%`;
      button.style.setProperty("--territory-color", continentColors[territory.continent]);
      button.addEventListener("click", (event) => { event.stopPropagation(); selectTerritory(territory); });
      return button;
    }));
    renderArmies();
  };

  const armyColors = ["#f0c548", "#dd5e50", "#4e8bd8", "#55ad70", "#b668c7", "#ef8e3f"];
  const renderArmies = () => {
    if (!gameState) return;
    const colorByMember = new Map(gameState.members.map((member, index) => [String(member.id), armyColors[index % armyColors.length]]));
    territoryLayer.querySelectorAll("[data-territory]").forEach((button) => {
      const territory = gameState.game.territories[button.dataset.territory];
      if (!territory) return;
      const owner = String(territory.owner);
      button.textContent = String(territory.armies);
      button.style.setProperty("--army-color", owner === "neutral" ? "#a7aca9" : colorByMember.get(owner) || "#ddd");
      button.dataset.owner = owner;
    });
  };

  const placeCard = (card, x, y) => {
    card.style.left = `${x}px`;
    card.style.top = `${y}px`;
    card.dataset.x = String(x);
    card.dataset.y = String(y);
  };

  const makeCardDraggable = (card) => {
    let drag = null;
    card.addEventListener("pointerdown", (event) => {
      if (event.button !== 0) return;
      event.stopPropagation();
      drag = { pointer: event.pointerId, x: event.clientX, y: event.clientY, cardX: Number(card.dataset.x), cardY: Number(card.dataset.y) };
      card.classList.add("is-dragging");
      card.setPointerCapture(event.pointerId);
    });
    card.addEventListener("pointermove", (event) => {
      if (!drag || drag.pointer !== event.pointerId) return;
      const scale = Math.max(camera.zoom, 0.45);
      placeCard(card, clamp(drag.cardX + (event.clientX - drag.x) / scale, 55, 1195), clamp(drag.cardY + (event.clientY - drag.y) / scale, 70, 650));
    });
    card.addEventListener("pointerup", (event) => {
      if (!drag || drag.pointer !== event.pointerId) return;
      drag = null;
      card.classList.remove("is-dragging");
    });
    card.addEventListener("dblclick", (event) => { event.stopPropagation(); card.classList.toggle("is-face-down"); });
    card.addEventListener("contextmenu", (event) => { event.preventDefault(); event.stopPropagation(); card.classList.toggle("is-face-down"); });
  };

  const drawCard = (kind) => {
    const mission = kind === "mission";
    const pile = mission ? missionPile : territoryPile;
    const count = mission ? 12 : 42;
    if (!pile.length) pile.push(...shuffledRange(count));
    const index = pile.pop();
    const columns = mission ? 4 : 7;
    const rows = mission ? 3 : 6;
    const column = index % columns;
    const row = Math.floor(index / columns);
    const paths = stylePaths(activeStyle, activeCardStyle);
    const card = document.createElement("button");
    card.type = "button";
    card.className = "conquest-drawn-card";
    card.dataset.kind = kind;
    card.dataset.index = String(index);
    card.dataset.sheet = mission ? paths.missionSheet : paths.territorySheet;
    card.title = "Doppelklick oder Rechtsklick: umdrehen";
    card.style.backgroundImage = `url("${card.dataset.sheet}")`;
    card.style.backgroundSize = `${columns * 100}% ${rows * 100}%`;
    card.style.backgroundPosition = `${columns === 1 ? 0 : column / (columns - 1) * 100}% ${rows === 1 ? 0 : row / (rows - 1) * 100}%`;
    card.style.setProperty("--card-back", `url("${mission ? paths.missionBack : paths.territoryBack}")`);
    card.style.setProperty("--card-turn", `${(cardSerial % 7 - 3) * 1.7}deg`);
    cardSerial += 1;
    placeCard(card, mission ? 1005 : 900, mission ? 530 : 225);
    makeCardDraggable(card);
    floatingLayer.append(card);
  };

  stage.addEventListener("pointerdown", (event) => {
    if (event.button !== 0 || event.target.closest("button, canvas")) return;
    stageDrag = { pointer: event.pointerId, x: event.clientX, y: event.clientY, cameraX: camera.x, cameraY: camera.y, turn: camera.turn, rotate: event.shiftKey };
    stage.classList.add("is-dragging");
    stage.setPointerCapture(event.pointerId);
  });
  stage.addEventListener("pointermove", (event) => {
    if (!stageDrag || stageDrag.pointer !== event.pointerId) return;
    if (stageDrag.rotate || event.shiftKey) {
      camera.turn = clamp(stageDrag.turn + (event.clientX - stageDrag.x) * 0.18, -32, 32);
    } else {
      camera.x = clamp(stageDrag.cameraX + event.clientX - stageDrag.x, -420, 420);
      camera.y = clamp(stageDrag.cameraY + event.clientY - stageDrag.y, -260, 300);
    }
    applyCamera(false);
  });
  const endStageDrag = (event) => {
    if (!stageDrag || stageDrag.pointer !== event.pointerId) return;
    stageDrag = null;
    stage.classList.remove("is-dragging");
  };
  stage.addEventListener("pointerup", endStageDrag);
  stage.addEventListener("pointercancel", endStageDrag);
  stage.addEventListener("wheel", (event) => {
    event.preventDefault();
    camera.zoom = clamp(camera.zoom * Math.exp(-event.deltaY * 0.0011), 0.46, 1.55);
    applyCamera(false);
  }, { passive: false });
  stage.addEventListener("contextmenu", (event) => event.preventDefault());

  app.querySelectorAll("[data-style]").forEach((button) => button.addEventListener("click", () => applyStyle(button.dataset.style)));
  app.querySelectorAll("[data-view]").forEach((button) => button.addEventListener("click", () => resetCamera(button.dataset.view)));
  app.querySelectorAll("[data-deck]").forEach((button) => button.addEventListener("click", (event) => { event.stopPropagation(); drawCard(button.dataset.deck); }));

  const localizeThemeAssets = (value) => {
    if (Array.isArray(value)) return value.map(localizeThemeAssets);
    if (value && typeof value === "object") return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, localizeThemeAssets(item)]));
    if (typeof value === "string" && value.startsWith("https://cdn.dddice.com/")) return `${app.dataset.themeAssetsUrl}${new URL(value).pathname.split("/").pop()}`;
    return value;
  };

  const initDice = async () => {
    const canvas = app.querySelector("[data-conquest-dice]");
    const status = app.querySelector("[data-dice-status]");
    if (!window.ThreeDDice) { status.textContent = "Würfeltechnik konnte nicht geladen werden."; return; }
    try {
      diceEngine = new window.ThreeDDice(canvas, undefined, {
        bgColor: 0x000000, bgOpacity: 0, persistRolls: true,
        camera: { fov: 26, distance: 20, position: { x: 4, y: 15, z: 20 }, rotation: null, quaternion: null },
        dice: { size: .78, allowPlayerMoveDice: false, defaultClickBehavior: "nothing" },
        light: { castShadows: true },
      });
      diceEngine.start();
      const response = await fetch(app.dataset.themeUrl, { cache: "force-cache" });
      if (!response.ok) throw new Error("theme");
      const payload = await response.json();
      diceEngine.loadTheme(localizeThemeAssets(payload.data || payload));
      diceEngine.loadThemeResources("outgunned-reimagined-ma8o1nit");
      diceEngine.resize(canvas.clientWidth, canvas.clientHeight);
      status.textContent = "3D-Würfel bereit.";
    } catch (_) {
      status.textContent = "Würfeltechnik konnte nicht geladen werden.";
      diceEngine = null;
    }
  };

  app.querySelector("[data-roll]").addEventListener("click", async () => {
    if (!diceEngine) return;
    const status = app.querySelector("[data-dice-status]");
    diceEngine.clear();
    status.textContent = "Würfel rollen …";
    try {
      await diceEngine.rollLocal(Array.from({ length: 5 }, () => ({ type: app.dataset.dieType, theme: "outgunned-reimagined-ma8o1nit" })));
      status.textContent = "Rot: Angriff · Dunkel: Verteidigung (Farbvarianten folgen).";
    } catch (_) { status.textContent = "Der Wurf konnte nicht gestartet werden."; }
  });

  fetch(app.dataset.worldUrl, { cache: "no-store" })
    .then((response) => { if (!response.ok) throw new Error("world"); return response.json(); })
    .then((payload) => {
      world = payload;
      territoryPile = shuffledRange(world.territories.length);
      missionPile = shuffledRange(world.missions.length);
      renderTerritories();
      applyStyle(activeStyle, activeCardStyle);
      resetCamera("center");
    })
    .catch(() => { info.innerHTML = "<small>FEHLER</small><strong>Spieldaten fehlen</strong><span>Die 42 Gebiete konnten nicht geladen werden.</span>"; });

  window.addEventListener("resize", () => {
    const canvas = app.querySelector("[data-conquest-dice]");
    if (diceEngine) diceEngine.resize(canvas.clientWidth, canvas.clientHeight);
  });
  initDice();
  fetch(app.dataset.statusUrl, { cache: "no-store", headers: { Accept: "application/json" } })
    .then((response) => { if (!response.ok) throw new Error("state"); return response.json(); })
    .then((payload) => { gameState = payload; renderArmies(); })
    .catch(() => {});
})();
