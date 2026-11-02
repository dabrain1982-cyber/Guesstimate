(() => {
  const app = document.querySelector("[data-conquest-app]");
  if (!app) return;
  const stage = app.querySelector("[data-stage]");
  const scene = app.querySelector("[data-scene]");
  const room = app.querySelector(".conquest-room");
  const toolbar = app.querySelector(".conquest-toolbar");
  const opening = app.querySelector("[data-board-opening]");
  const surface = app.querySelector("[data-board-surface]");
  const territoryLayer = app.querySelector("[data-territories]");
  const info = app.querySelector("[data-info]");
  const inventory = app.querySelector("[data-inventory]");
  const boardImageWidth = 1284;
  const boardImageHeight = 1225;
  const boardWidth = 1000;
  const boardHeight = boardWidth * boardImageHeight / boardImageWidth;
  const sceneWidth = 1672;
  const sceneHeight = 941;
  // The photographed opening has bevelled corners. Its side rails continue
  // beyond the front corners of the felt, so a four-point inset leaves wedges.
  const tableOpening = [[332, 267], [1342, 267], [1369, 277], [1665, 634], [1611, 677], [61, 677], [8, 634], [305, 277]];
  const tablePlane = [[313, 267], [1361, 267], [1708, 678], [-30, 678]];
  // Pixel positions on welt-conquest-farbkarte-v2.png. Both views project
  // these same points together with the single shared board surface.
  const boardPositions = {
    alaska: [99, 180], "nordwest-territorium": [219, 207], groenland: [566, 152],
    alberta: [196, 321], ontario: [311, 336], ostkanada: [439, 373],
    weststaaten: [164, 478], oststaaten: [333, 459], mittelamerika: [197, 573],
    venezuela: [220, 674], peru: [210, 872], brasilien: [333, 781], argentinien: [190, 1033],
    island: [592, 350], grossbritannien: [559, 494], skandinavien: [657, 388],
    nordeuropa: [626, 531], westeuropa: [548, 620], suedeuropa: [648, 599], russland: [744, 431],
    nordafrika: [529, 694], aegypten: [652, 665], ostafrika: [719, 780],
    zentralafrika: [647, 846], suedafrika: [666, 937], madagaskar: [765, 949],
    ural: [885, 348], sibirien: [958, 308], jakutien: [1103, 246], kamtschatka: [1157, 363],
    irkutsk: [1040, 384], mongolei: [1020, 467], japan: [1134, 546], afghanistan: [855, 512],
    china: [974, 600], "naher-osten": [762, 683], indien: [884, 682], suedostasien: [997, 677],
    indonesien: [1049, 754], neuguinea: [1195, 785], westaustralien: [1114, 917], ostaustralien: [1204, 918],
  };
  const armyColors = ["#e0b43c", "#c44b40", "#3e78b8", "#43875b", "#925eaf", "#d17c36"];
  const initialLean = innerWidth < 720 ? 1 : 0;
  const camera = { lean: initialLean };
  let boardTransform = null;
  let world = null;
  let gameState = null;
  let selectedId = null;
  let pollTimer = null;
  let stopped = false;
  let inventorySignature = null;
  const clamp = (value, low, high) => Math.max(low, Math.min(high, value));

  // One planar projective transform fits the surface inside the photographed
  // copper rail. There is no second tabletop, extrusion or independent frame.
  const boardCorners = [[0, 0], [boardWidth, 0], [boardWidth, boardHeight], [0, boardHeight]];
  const transformForCorners = (source, corners) => {
    const rows = source.flatMap(([x, y], index) => {
      const [u, v] = corners[index];
      return [[x, y, 1, 0, 0, 0, -u * x, -u * y, u], [0, 0, 0, x, y, 1, -v * x, -v * y, v]];
    });
    for (let column = 0; column < 8; column += 1) {
      let pivot = column;
      for (let row = column + 1; row < 8; row += 1) if (Math.abs(rows[row][column]) > Math.abs(rows[pivot][column])) pivot = row;
      [rows[column], rows[pivot]] = [rows[pivot], rows[column]];
      const divisor = rows[column][column];
      for (let entry = column; entry < 9; entry += 1) rows[column][entry] /= divisor;
      for (let row = 0; row < 8; row += 1) {
        if (row === column) continue;
        const factor = rows[row][column];
        for (let entry = column; entry < 9; entry += 1) rows[row][entry] -= factor * rows[column][entry];
      }
    }
    return rows.map((row) => row[8]);
  };

  const project = (transform, x, y) => {
    const [a, b, c, d, e, f, g, h] = transform;
    const divisor = g * x + h * y + 1;
    return [(a * x + b * y + c) / divisor, (d * x + e * y + f) / divisor];
  };

  const cssMatrix = ([a, b, c, d, e, f, g, h]) =>
    "matrix3d(" + [a, d, 0, g, b, e, 0, h, 0, 0, 1, 0, c, f, 0, 1].join(",") + ")";

  const applyView = () => {
    // Automatic framing depends only on the window, never on wheel zoom or
    // dragging. Keep the whole board between the toolbar and the lower hint.
    const fit = stage.clientWidth / sceneWidth;
    const visibleTop = (sceneHeight - stage.clientHeight / fit) / 2;
    const safeTop = visibleTop + (toolbar.offsetTop + toolbar.offsetHeight + 16) / fit;
    const safeBottom = visibleTop + (stage.clientHeight - 48) / fit;
    const availableHeight = Math.max(80, safeBottom - safeTop);
    const topWidth = Math.min(sceneWidth - 48 / fit, availableHeight * boardWidth / boardHeight);
    const topHeight = topWidth * boardHeight / boardWidth;
    const topLeft = (sceneWidth - topWidth) / 2;
    const topY = (safeTop + safeBottom - topHeight) / 2;
    const topPlane = [[topLeft, topY], [topLeft + topWidth, topY],
      [topLeft + topWidth, topY + topHeight], [topLeft, topY + topHeight]];
    const lean = camera.lean;
    const corners = tablePlane.map(([x, y], index) => [
      x + (topPlane[index][0] - x) * lean,
      y + (topPlane[index][1] - y) * lean,
    ]);
    const roomTransform = transformForCorners(tablePlane, corners);
    // The photographed table and its copper opening follow the same plane
    // as the map. Keep the room visible throughout the entire movement.
    room.style.transform = cssMatrix(roomTransform);
    opening.style.clipPath = "polygon(" + tableOpening.map(([x, y]) => {
      const point = project(roomTransform, x, y);
      return point[0] + "px " + point[1] + "px";
    }).join(",") + ")";
    boardTransform = transformForCorners(boardCorners, corners);
    surface.style.transform = cssMatrix(boardTransform);
    territoryLayer.querySelectorAll("[data-territory]").forEach((button) => {
      const point = boardPositions[button.dataset.territory];
      const [x, y] = project(boardTransform, point[0] / boardImageWidth * boardWidth, point[1] / boardImageHeight * boardHeight);
      button.style.left = x + "px";
      button.style.top = y + "px";
    });
    app.querySelectorAll("[data-view]").forEach((button) => {
      const active = button.dataset.view === "top" ? lean > .999 : lean < .001;
      button.setAttribute("aria-pressed", String(active));
    });
    scene.style.transform = "translate(-50%, -50%) scale(" + fit + ")";
  };

  const setLean = (value) => {
    camera.lean = clamp(value, 0, 1);
    applyView();
  };

  const showInfo = (heading, title, detail) => {
    const small = document.createElement("small");
    const strong = document.createElement("strong");
    const span = document.createElement("span");
    small.textContent = heading;
    strong.textContent = title;
    span.textContent = detail;
    info.replaceChildren(small, strong, span);
  };

  const selectTerritory = (territory) => {
    selectedId = territory.id;
    const neighbors = new Set(territory.neighbors);
    territoryLayer.querySelectorAll("button").forEach((button) => {
      button.classList.toggle("is-selected", button.dataset.territory === selectedId);
      button.classList.toggle("is-neighbor", neighbors.has(button.dataset.territory));
    });
    const names = territory.neighbors.map((id) => world.territories.find((item) => item.id === id)?.name).filter(Boolean);
    const continent = world.continents.find((item) => item.id === territory.continent);
    const armies = gameState?.game?.territories[territory.id]?.armies;
    showInfo(continent.name + " · BONUS +" + continent.bonus, territory.name + (armies ? " · " + armies + " Truppen" : ""), "Nachbarn: " + names.join(", "));
  };

  const renderArmies = () => {
    if (!gameState?.game) return;
    const colors = new Map(gameState.members.map((member, index) => [String(member.id), armyColors[index % armyColors.length]]));
    territoryLayer.querySelectorAll("[data-territory]").forEach((button) => {
      const territory = gameState.game.territories[button.dataset.territory];
      if (!territory) return;
      const owner = String(territory.owner);
      const name = world.territories.find((item) => item.id === button.dataset.territory).name;
      button.textContent = String(territory.armies);
      button.style.setProperty("--army-color", owner === "neutral" ? "#87918a" : colors.get(owner) || "#87918a");
      button.dataset.owner = owner;
      button.setAttribute("aria-label", name + ", " + territory.armies + " Truppen");
    });
  };

  const renderInventory = () => {
    const own = gameState?.game?.inventory;
    if (!own) return;
    app.querySelector("[data-inventory-count]").textContent = String(own.territory_cards.length);
    const signature = JSON.stringify(own);
    if (signature === inventorySignature) return;
    inventorySignature = signature;
    app.querySelector("[data-own-mission]").textContent = own.mission?.text || "Welteroberung – du hast keine geheime Missionskarte.";
    app.querySelector("[data-inventory-cards]").replaceChildren(...own.territory_cards.map((entry) => {
      const card = document.createElement("article");
      card.className = "conquest-inventory-card";
      card.dataset.cardId = entry.id;
      card.textContent = entry.name;
      return card;
    }));
    app.querySelector("[data-inventory-empty]").hidden = own.territory_cards.length > 0;
  };

  const renderTerritories = () => {
    territoryLayer.replaceChildren(...world.territories.map((territory) => {
      if (!boardPositions[territory.id]) throw new Error("Brettposition fehlt: " + territory.id);
      const button = document.createElement("button");
      button.type = "button";
      button.className = "conquest-territory";
      button.dataset.territory = territory.id;
      button.title = territory.name;
      button.setAttribute("aria-label", territory.name);
      button.addEventListener("click", (event) => { event.stopPropagation(); selectTerritory(territory); });
      return button;
    }));
    renderArmies();
    applyView();
  };

  const loadState = async () => {
    try {
      const response = await fetch(app.dataset.statusUrl, { cache: "no-store", headers: { Accept: "application/json" } });
      if (!response.ok || !response.headers.get("content-type")?.includes("application/json")) throw new Error("state");
      const next = await response.json();
      if (!gameState || next.revision >= gameState.revision) {
        gameState = next;
        if (world) renderArmies();
        renderInventory();
        const current = next.members.find((member) => member.id === next.game?.current_member_id);
        if (next.game && current) app.querySelector("[data-turn-summary]").textContent = "RUNDE " + next.game.round + " · " + current.name + " IST DRAN";
      }
    } catch (_) {
      app.querySelector("[data-turn-summary]").textContent = "Verbindung unterbrochen · erneuter Versuch …";
      if (!gameState) app.querySelector("[data-own-mission]").textContent = "Dein Inventar konnte noch nicht geladen werden.";
    } finally {
      if (!stopped) pollTimer = window.setTimeout(loadState, 2000);
    }
  };

  stage.addEventListener("wheel", (event) => {
    if (event.ctrlKey || !event.deltaY) return;
    event.preventDefault();
    const unit = event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? stage.clientHeight : 1;
    setLean(camera.lean - event.deltaY * unit / 2400);
  }, { passive: false });
  app.querySelectorAll("[data-view]").forEach((button) => button.addEventListener("click", () => {
    setLean(button.dataset.view === "top" ? 1 : 0);
  }));
  app.querySelector("[data-inventory-open]").addEventListener("click", () => inventory.showModal());
  app.querySelector("[data-inventory-close]").addEventListener("click", () => inventory.close());
  inventory.addEventListener("click", (event) => {
    const bounds = inventory.getBoundingClientRect();
    if (event.target === inventory && (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom)) inventory.close();
  });
  window.addEventListener("resize", applyView);
  window.addEventListener("pagehide", () => {
    stopped = true;
    clearTimeout(pollTimer);
  });
  fetch(app.dataset.worldUrl, { cache: "no-store" })
    .then((response) => { if (!response.ok) throw new Error("world"); return response.json(); })
    .then((payload) => { world = payload; renderTerritories(); })
    .catch(() => showInfo("FEHLER", "Spieldaten fehlen", "Die 42 Gebiete konnten nicht geladen werden."));
  applyView();
  loadState();
})();
