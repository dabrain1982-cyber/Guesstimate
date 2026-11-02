(() => {
  const initGame = () => {
    const room = document.querySelector("[data-dice-room]");
    if (!room) return;
    const canvas = room.querySelector("[data-dddice-canvas]");
    const fallback = room.querySelector("[data-dice-fallback]");
    const concealed = room.querySelector("[data-dice-concealed]");
    const engineStatus = room.querySelector("[data-dice-engine-status]");
    const message = room.querySelector("[data-dice-message]");
    const history = room.querySelector("[data-dice-history]");
    const kniffelSheet = room.querySelector("[data-kniffel-sheet]");
    const kniffelLights = room.querySelector("[data-kniffel-lights]");
    const held = room.querySelector("[data-dice-held]");
    const tray = room.querySelector("[data-dice-tray]");
    const cameraLock = room.querySelector("[data-camera-lock]");
    const maexchenAnnouncement = room.querySelector("[data-maexchen-announcement]");
    const maexchenOrder = room.querySelector("[data-maexchen-order]");
    const maexchenClaimControl = room.querySelector("[data-maexchen-claim-control]");
    const maexchenClaim = room.querySelector("[data-maexchen-claim]");
    const csrf = room.querySelector("[data-csrf]").value;
    const memberId = Number(room.dataset.memberId);
    const diceCount = Number(room.dataset.diceCount);
    const hiddenRoll = room.dataset.hiddenRoll === "1";
    const gameMode = room.dataset.gameMode || "sandbox";
    const buttons = Object.fromEntries([...room.querySelectorAll("[data-dice-action]")].map((button) => [button.dataset.diceAction, button]));
    let cameraLocked = room.dataset.cameraLocked === "1";
    let savedCamera = null;
    try { savedCamera = JSON.parse(room.dataset.cameraConfig); } catch (_) {}
    let engine = null;
    let enginePromise = null;
    let latestState = null;
    let lastRollId = null;
    let actionBusy = false;
    let latestRevision = -1;
    let pointerDown = null;
    let zoneSignature = "";
    let concealedSignature = "";
    let kniffelSignature = "";
    const visualDice = new Map();

    const fitRoom = () => {
      const scale = Math.min(window.innerWidth / 1920, window.innerHeight / 1080);
      room.style.transform = `translate(${(window.innerWidth - 1920 * scale) / 2}px, ${(window.innerHeight - 1080 * scale) / 2}px) scale(${scale})`;
      room.style.transformOrigin = "top left";
      if (engine) engine.resize(canvas.clientWidth, canvas.clientHeight);
    };
    window.addEventListener("resize", fitRoom);
    fitRoom();

    const localizeThemeAssets = (value) => {
      if (Array.isArray(value)) return value.map(localizeThemeAssets);
      if (value && typeof value === "object") return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, localizeThemeAssets(item)]));
      if (typeof value === "string" && value.startsWith("https://cdn.dddice.com/")) return `${room.dataset.themeAssetsUrl}${new URL(value).pathname.split("/").pop()}`;
      return value;
    };

    const createEngine = async () => {
      if (!window.ThreeDDice) throw new Error("sdk-missing");
      const position = savedCamera?.position || { x: 5, y: 18, z: 26 };
      const candidate = new window.ThreeDDice(canvas, undefined, {
        bgColor: 0x000000, bgOpacity: 0, autoClear: null, persistRolls: true,
        camera: { fov: 28, distance: 28, position, rotation: null, quaternion: null },
        dice: { size: 1.15, allowPlayerMoveDice: false, defaultClickBehavior: "nothing" },
        light: { castShadows: true },
      });
      candidate.start();
      const response = await fetch(room.dataset.themeUrl, { cache: "force-cache" });
      if (!response.ok) throw new Error("theme-missing");
      const payload = await response.json();
      candidate.loadTheme(localizeThemeAssets(payload.data || payload));
      candidate.loadThemeResources(room.dataset.theme);
      if (savedCamera?.target && candidate.controls) {
        candidate.controls.target.set(savedCamera.target.x, savedCamera.target.y, savedCamera.target.z);
        candidate.controls.update();
      }
      candidate.controlsEnabled = !cameraLocked;
      engine = candidate;
      fitRoom();
      engineStatus.textContent = cameraLocked ? "3D-Würfel bereit · Kamera fixiert" : "3D-Würfel bereit · Kamera einstellbar";
      return engine;
    };

    const ensureEngine = () => {
      if (!enginePromise) enginePromise = createEngine().catch((error) => {
        engineStatus.textContent = `3D-Würfel konnten nicht geladen werden: ${error.message || "unbekannter Fehler"}`;
        return null;
      });
      return enginePromise;
    };

    const makeMiniDie = (die, zone) => {
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.dieId = die.id;
      button.title = zone === "held" ? "Zum erneuten Würfeln einsammeln" : "Auswahl zurücknehmen";
      const face = document.createElement("span");
      face.className = "dice-mini";
      face.dataset.value = die.value ?? "?";
      button.append(face);
      return button;
    };

    const renderZones = (dice, canControl) => {
      const nextSignature = JSON.stringify(dice.filter((die) => die.zone !== "active").map((die) => [die.id, die.value, die.zone]));
      if (nextSignature !== zoneSignature) {
        zoneSignature = nextSignature;
        held.replaceChildren(...dice.filter((die) => die.zone === "held").map((die) => makeMiniDie(die, "held")));
        tray.replaceChildren(...dice.filter((die) => die.zone === "tray").map((die) => makeMiniDie(die, "tray")));
        [...held.querySelectorAll("button"), ...tray.querySelectorAll("button")].forEach((button) => {
          button.addEventListener("click", () => performAction("toggle", { die_id: button.dataset.dieId }));
        });
      }
      [...held.querySelectorAll("button"), ...tray.querySelectorAll("button")].forEach((button) => { button.disabled = !canControl; });
      for (const die of dice) {
        const visualId = visualDice.get(die.id);
        const visual = visualId && engine?.dice?.get(visualId);
        if (visual) visual.getObject().visible = die.zone === "active";
      }
    };

    const showFallback = (entries) => {
      fallback.replaceChildren(...entries.map((entry) => {
        const die = document.createElement("span");
        die.textContent = entry.value ?? "?";
        return die;
      }));
    };

    const animateRoll = async (entries) => {
      fallback.replaceChildren();
      const renderer = await ensureEngine();
      if (!renderer || entries.some((entry) => entry.value == null)) return showFallback(entries);
      renderer.clear();
      visualDice.clear();
      const values = entries.map((entry) => entry.value);
      const nativeRandom = Math.random;
      let localRandomCall = 0;
      let animation;
      try {
        Math.random = () => {
          const call = localRandomCall++;
          const dieIndex = Math.floor(call / 5);
          if (dieIndex < values.length && call % 5 === 0) return (values[dieIndex] - 0.5) / 6;
          return nativeRandom();
        };
        animation = renderer.rollLocal(entries.map(() => ({ type: room.dataset.dieType, theme: room.dataset.theme })), { external_id: lastRollId }, {
          uuid: `guesstimate-player-${memberId}`, username: "Guesstimate-Spieler",
        });
      } catch (error) {
        engineStatus.textContent = `3D-Wurf fehlgeschlagen: ${error.message || "unbekannter Fehler"}`;
        showFallback(entries);
        return;
      } finally { Math.random = nativeRandom; }
      try {
        const response = await animation;
        response.data.values.forEach((value, index) => visualDice.set(entries[index].id, value.uuid));
      } catch (error) {
        engineStatus.textContent = `3D-Wurf fehlgeschlagen: ${error.message || "unbekannter Fehler"}`;
        showFallback(entries);
      }
    };

    const renderConcealed = (count, visible) => {
      const nextSignature = `${visible}:${count}`;
      if (nextSignature === concealedSignature) return;
      concealedSignature = nextSignature;
      concealed.classList.toggle("is-visible", visible);
      if (!visible) return concealed.replaceChildren();
      concealed.replaceChildren(...Array.from({ length: count }, () => {
        const die = document.createElement("span");
        if (gameMode === "maexchen") {
          die.className = "maexchen-logo-die";
          const cube = document.createElement("span");
          cube.className = "maexchen-logo-cube";
          ["front", "back", "right", "left", "top", "bottom"].forEach((side) => {
            const face = document.createElement("i");
            face.className = `face-${side}`;
            cube.append(face);
          });
          die.append(cube);
        } else die.className = "dice-brand-die";
        return die;
      }));
    };

    const renderHistory = (rows = []) => {
      if (!history) return;
      history.replaceChildren(...rows.map((row) => {
        const line = document.createElement("div");
        line.className = "dice-history-row";
        const name = document.createElement("b");
        name.textContent = row.name;
        const rolls = document.createElement("span");
        rolls.textContent = row.rolls.length ? row.rolls.map((entry) => entry.values ? entry.values.join(" · ") : "verdeckt").join("  |  ") : "–";
        line.append(name, rolls);
        return line;
      }));
    };

    const renderKniffel = (kniffel) => {
      if (!kniffelSheet || !kniffel) return;
      const nextSignature = JSON.stringify(kniffel);
      if (nextSignature === kniffelSignature) return;
      kniffelSignature = nextSignature;
      const currentId = Number(kniffel.current_member_id);
      const table = document.createElement("table");
      table.style.width = `${196 + kniffel.scorecards.length * 52}px`;
      const columns = document.createElement("colgroup");
      const categoryColumn = document.createElement("col");
      categoryColumn.className = "kniffel-category-column";
      const ruleColumn = document.createElement("col");
      ruleColumn.className = "kniffel-rule-column";
      columns.append(categoryColumn, ruleColumn);
      kniffel.scorecards.forEach(() => {
        const playerColumn = document.createElement("col");
        playerColumn.className = "kniffel-player-column";
        columns.append(playerColumn);
      });
      table.append(columns);
      const head = document.createElement("thead");
      const headRow = document.createElement("tr");
      const corner = document.createElement("th");
      corner.colSpan = 2;
      corner.textContent = "Erster Teil";
      headRow.append(corner);
      kniffel.scorecards.forEach((card) => {
        const cell = document.createElement("th");
        cell.textContent = card.name;
        cell.title = card.name;
        if (Number(card.id) === currentId) cell.classList.add("is-current");
        headRow.append(cell);
      });
      head.append(headRow);
      table.append(head);
      const body = document.createElement("tbody");
      const categories = Object.fromEntries(kniffel.categories.map((category) => [category.key, category]));
      const rules = {
        ones: ["1er", "Nur Einser zählen"], twos: ["2er", "Nur Zweier zählen"],
        threes: ["3er", "Nur Dreier zählen"], fours: ["4er", "Nur Vierer zählen"],
        fives: ["5er", "Nur Fünfer zählen"], sixes: ["6er", "Nur Sechser zählen"],
        three_kind: ["Dreierpasch", "Alle Augen zählen"], four_kind: ["Viererpasch", "Alle Augen zählen"],
        full_house: ["Full House", "25 Punkte"], small_straight: ["Kleine Straße", "30 Punkte"],
        large_straight: ["Große Straße", "40 Punkte"], five_kind: ["Kniffel", "50 Punkte"],
        chance: ["Chance", "Alle Augen zählen"],
      };
      const appendScoreCells = (row, category) => {
        kniffel.scorecards.forEach((card) => {
          const cell = document.createElement("td");
          const score = card.scores[category.key];
          if (score !== undefined) {
            cell.textContent = score;
            cell.classList.add("is-filled");
          } else if (Number(card.id) === memberId && kniffel.available_scores[category.key] !== undefined) {
            const scoreButton = document.createElement("button");
            scoreButton.type = "button";
            scoreButton.textContent = kniffel.available_scores[category.key];
            scoreButton.title = `${category.label} mit ${kniffel.available_scores[category.key]} Punkten eintragen`;
            scoreButton.addEventListener("click", () => performAction("score", { category: category.key }));
            cell.append(scoreButton);
          }
          if (Number(card.id) === currentId) cell.classList.add("is-current");
          row.append(cell);
        });
      };
      const appendCategory = (key) => {
        const category = categories[key];
        const row = document.createElement("tr");
        const label = document.createElement("th");
        label.textContent = rules[key][0];
        const rule = document.createElement("td");
        rule.className = "kniffel-rule";
        rule.textContent = rules[key][1];
        row.append(label, rule);
        appendScoreCells(row, category);
        body.append(row);
      };
      const appendTotal = (labelText, ruleText, key, className = "") => {
        const row = document.createElement("tr");
        row.className = `kniffel-total-row ${className}`;
        const label = document.createElement("th");
        label.textContent = labelText;
        const rule = document.createElement("td");
        rule.className = "kniffel-rule";
        rule.textContent = ruleText;
        row.append(label, rule);
        kniffel.scorecards.forEach((card) => {
          const cell = document.createElement("td");
          cell.textContent = card.totals[key];
          row.append(cell);
        });
        body.append(row);
      };
      const appendSection = (labelText) => {
        const row = document.createElement("tr");
        row.className = "kniffel-section-row";
        const label = document.createElement("th");
        label.colSpan = 2 + kniffel.scorecards.length;
        label.textContent = labelText;
        row.append(label);
        body.append(row);
      };
      ["ones", "twos", "threes", "fours", "fives", "sixes"].forEach(appendCategory);
      appendTotal("Zwischensumme", "", "upper");
      appendTotal("Bonus bei 63 und mehr", "+ 35 Punkte", "bonus");
      appendTotal("Summe Erster Teil", "", "upper_total", "is-part-total");
      appendSection("Zweiter Teil");
      ["three_kind", "four_kind", "full_house", "small_straight", "large_straight", "five_kind", "chance"].forEach(appendCategory);
      appendTotal("Summe Zweiter Teil", "", "lower");
      appendTotal("Summe Erster Teil", "", "upper_total");
      appendTotal("Endsumme", "", "total", "is-grand-total");
      table.append(body);
      kniffelSheet.replaceChildren(table);
      if (kniffelLights) [...kniffelLights.children].forEach((light, index) => light.classList.toggle("is-lit", index < kniffel.rolls_left));
    };

    const maexchenLabel = (value) => {
      if (value === "21") return "Mäxchen · 21";
      if (value?.[0] === value?.[1]) return `${value[0]}er-Pasch`;
      return value || "–";
    };

    const renderMaexchen = async (state) => {
      const game = state.maexchen;
      const roll = state.roll;
      const dice = state.dice || [];
      const phase = game.phase;
      const currentId = Number(game.current_member_id);
      const responderId = Number(game.responder_id);
      const isCurrent = currentId === memberId;
      const isResponder = responderId === memberId;
      const isRoller = roll && Number(roll.roller_id) === memberId;
      const playerMap = new Map(game.players.map((player) => [Number(player.id), player]));

      room.querySelectorAll("[data-dice-player]").forEach((element) => {
        const playerId = Number(element.dataset.dicePlayer);
        const player = playerMap.get(playerId);
        element.classList.toggle("is-current-turn", playerId === currentId && phase !== "finished");
        element.classList.toggle("is-responder", playerId === responderId && phase === "awaiting_response");
        element.classList.toggle("is-eliminated", Boolean(player?.eliminated));
        const life = element.querySelector("[data-maexchen-life]");
        if (life && player) {
          life.textContent = player.eliminated
            ? "Ausgeschieden"
            : `${"♥ ".repeat(player.lives)}${"♡ ".repeat(3 - player.lives)}${player.swimming ? "· schwimmt" : ""}`.trim();
        }
      });
      const orderedNames = game.turn_order
        .map((id) => playerMap.get(Number(id)))
        .filter(Boolean)
        .map((player) => player.eliminated ? `${player.name} (raus)` : player.name);
      maexchenOrder.textContent = orderedNames.join("  →  ");
      maexchenAnnouncement.textContent = game.claim ? `Ansage: ${maexchenLabel(game.claim)}` : `Runde ${game.round_number}`;

      Object.values(buttons).forEach((button) => { button.hidden = true; button.disabled = actionBusy; });
      maexchenClaimControl.hidden = true;
      const showButton = (name) => { if (buttons[name]) buttons[name].hidden = false; };

      if (!roll) {
        lastRollId = null;
        renderConcealed(0, false);
        canvas.classList.remove("is-concealed");
        fallback.classList.remove("is-concealed");
        engine?.clear();
      } else {
        const publicRoll = roll.phase === "public";
        const canSeeValues = publicRoll || isRoller;
        const rolled = roll.rolled_ids.map((id) => dice.find((die) => die.id === id)).filter(Boolean);
        canvas.classList.toggle("is-concealed", !canSeeValues);
        fallback.classList.toggle("is-concealed", !canSeeValues);
        renderConcealed(roll.rolled_ids.length, !canSeeValues);
        if (canSeeValues && rolled.every((die) => die.value != null) && roll.id !== lastRollId) {
          lastRollId = roll.id;
          await animateRoll(rolled);
        }
      }

      if (phase === "awaiting_roll") {
        if (isCurrent) {
          showButton("roll");
          message.textContent = game.claim
            ? `Du glaubst ${maexchenLabel(game.claim)} und musst jetzt strikt höher ansagen.`
            : "Du legst vor. Würfle, schau hin und mach deine Ansage.";
        } else {
          const current = playerMap.get(currentId);
          message.textContent = `${current?.name || "Ein Mitspieler"} ist mit Würfeln an der Reihe.`;
        }
      } else if (phase === "awaiting_claim") {
        if (isCurrent) {
          maexchenClaimControl.hidden = false;
          const minimum = game.claim ? game.values.indexOf(game.claim) : -1;
          [...maexchenClaim.options].forEach((option, index) => { option.disabled = index <= minimum; });
          const firstAllowed = [...maexchenClaim.options].find((option) => !option.disabled);
          if (firstAllowed && maexchenClaim.selectedOptions[0]?.disabled) maexchenClaim.value = firstAllowed.value;
          showButton("claim");
          message.textContent = "Nur du siehst die Augen. Sage einen strikt höheren Wert an – oder bluffe.";
        } else message.textContent = `${roll?.roller_name || "Der Würfler"} kennt den Wurf und überlegt die Ansage.`;
      } else if (phase === "awaiting_response") {
        if (isResponder) {
          if (game.claim === "21") showButton("believe_maexchen");
          else showButton("believe");
          showButton("reveal");
          message.textContent = game.claim === "21"
            ? "Glaubst du das Mäxchen, gibst du ein Leben ab und legst neu vor. Aufdecken kann zwei Leben kosten."
            : "Glauben und selbst strikt höher weitermachen – oder für alle aufdecken.";
        } else {
          const responder = playerMap.get(responderId);
          message.textContent = `${responder?.name || "Der Nächste"} entscheidet über ${maexchenLabel(game.claim)}.`;
        }
      } else if (phase === "round_result") {
        const result = game.round_result;
        maexchenAnnouncement.textContent = result.actual
          ? `${maexchenLabel(result.claim)} angesagt · ${maexchenLabel(result.actual)} gewürfelt`
          : maexchenLabel(result.claim);
        if (isCurrent) showButton("next_round");
        const status = result.eliminated ? " und scheidet aus" : (result.swimming ? " und schwimmt jetzt" : "");
        message.textContent = `${result.loser_name} verliert ${result.loss === 2 ? "zwei Leben" : "ein Leben"}${status}. ${result.reason}`;
      } else if (phase === "finished") {
        const winner = playerMap.get(Number(game.winner_id));
        maexchenAnnouncement.textContent = `${winner?.name || "Gewonnen"} gewinnt`;
        message.textContent = "Die Mäxchenrunde ist beendet.";
      }
    };

    const renderState = async (state) => {
      latestState = state;
      if (gameMode === "maexchen") return renderMaexchen(state);
      renderHistory(state.history);
      renderKniffel(state.kniffel);
      const roll = state.roll;
      const dice = state.dice || [];
      const isRoller = roll && Number(roll.roller_id) === memberId;
      const ownKniffelTurn = gameMode !== "kniffel" || Number(state.kniffel?.current_member_id) === memberId;
      const canControl = Boolean(isRoller && roll.phase === "revealed" && ownKniffelTurn && !actionBusy);
      const trayCount = dice.filter((die) => die.zone === "tray").length;
      renderZones(dice, canControl);
      buttons.roll.disabled = actionBusy || !ownKniffelTurn || Boolean(isRoller && roll?.phase === "covered") || Boolean(state.kniffel?.completed) || Number(state.kniffel?.rolls_left) === 0;
      buttons.roll.textContent = roll ? (trayCount ? `${trayCount} Würfel würfeln` : `Alle ${diceCount} neu würfeln`) : `${diceCount} Würfel würfeln`;
      buttons.collect.disabled = actionBusy || !canControl || dice.every((die) => die.zone === "tray");
      if (buttons.reveal) buttons.reveal.disabled = actionBusy || !isRoller || roll?.phase !== "covered";
      if (!roll) {
        lastRollId = null;
        renderConcealed(0, false);
        if (gameMode === "kniffel") {
          const current = state.members.find((item) => Number(item.id) === Number(state.kniffel?.current_member_id));
          message.textContent = state.kniffel?.completed ? "Die Kniffelrunde ist beendet." : (ownKniffelTurn ? "Du bist am Zug – erster Wurf." : `${current?.name || "Ein Mitspieler"} ist am Zug.`);
        } else message.textContent = "Der Tisch ist bereit.";
        return;
      }
      const covered = hiddenRoll && roll.phase === "covered";
      canvas.classList.toggle("is-concealed", covered);
      fallback.classList.toggle("is-concealed", covered);
      renderConcealed(roll.rolled_ids.length, covered);
      if (roll.id !== lastRollId) {
        lastRollId = roll.id;
        const rolled = roll.rolled_ids.map((id) => dice.find((die) => die.id === id)).filter(Boolean);
        if (rolled.every((die) => die.value != null)) animateRoll(rolled);
      }
      if (covered && isRoller) message.textContent = "Verdeckter Wurf – zum Ansehen aufdecken.";
      else if (covered) message.textContent = `${roll.roller_name} würfelt verdeckt.`;
      else if (gameMode === "kniffel" && ownKniffelTurn && state.kniffel.rolls_left === 0) message.textContent = "Dritter Wurf: Wähle jetzt ein freies Feld im Kniffelblock.";
      else if (gameMode === "kniffel" && !ownKniffelTurn) message.textContent = `${roll.roller_name} ist am Zug.`;
      else message.textContent = `${roll.roller_name}: Würfel anklicken, die erneut geworfen werden sollen.`;
    };

    const fetchState = async () => {
      const response = await fetch(room.dataset.statusUrl, { cache: "no-store", headers: { Accept: "application/json" } });
      if (!response.ok) throw new Error("status");
      const state = await response.json();
      if (state.status !== "playing") return window.location.reload();
      if (Number(state.revision) < latestRevision) return;
      latestRevision = Number(state.revision);
      await renderState(state);
    };

    const performAction = async (action, extra = {}) => {
      if (actionBusy) return;
      actionBusy = true;
      const body = new FormData();
      body.set("csrf_token", csrf);
      body.set("action", action);
      Object.entries(extra).forEach(([key, value]) => body.set(key, value));
      try {
        const response = await fetch(room.dataset.actionUrl, { method: "POST", body, headers: { Accept: "application/json" } });
        if (!response.ok) throw new Error("action");
        await fetchState();
      } catch (_) {
        message.textContent = "Die Aktion konnte gerade nicht ausgeführt werden.";
      } finally {
        actionBusy = false;
        await fetchState().catch(() => {});
      }
    };

    const selectDieAt = (event) => {
      if (!engine || !latestState?.roll || Number(latestState.roll.roller_id) !== memberId || latestState.roll.phase !== "revealed") return;
      if (pointerDown && Math.hypot(event.clientX - pointerDown.x, event.clientY - pointerDown.y) > 6) return;
      const rect = canvas.getBoundingClientRect();
      engine.pointer.set(((event.clientX - rect.left) / rect.width) * 2 - 1, -((event.clientY - rect.top) / rect.height) * 2 + 1);
      engine.raycaster.setFromCamera(engine.pointer, engine.camera);
      let hit = null;
      for (const [serverId, visualId] of visualDice) {
        const die = engine.dice.get(visualId);
        if (!die || !die.getObject().visible) continue;
        const intersections = engine.raycaster.intersectObject(die.getObject(), true);
        if (intersections.length && (!hit || intersections[0].distance < hit.distance)) hit = { id: serverId, distance: intersections[0].distance };
      }
      if (hit) performAction("toggle", { die_id: hit.id });
    };
    canvas.addEventListener("pointerdown", (event) => { pointerDown = { x: event.clientX, y: event.clientY }; });
    canvas.addEventListener("click", selectDieAt);
    Object.entries(buttons).forEach(([action, button]) => button.addEventListener("click", () => {
      performAction(action, action === "claim" ? { claim: maexchenClaim.value } : {});
    }));

    cameraLock.addEventListener("change", async () => {
      const renderer = await ensureEngine();
      if (!renderer) return;
      const locked = cameraLock.checked;
      const camera = locked ? {
        position: { x: renderer.camera.position.x, y: renderer.camera.position.y, z: renderer.camera.position.z },
        target: { x: renderer.controls.target.x, y: renderer.controls.target.y, z: renderer.controls.target.z },
      } : null;
      const body = new FormData();
      body.set("csrf_token", csrf);
      body.set("locked", locked ? "1" : "0");
      if (camera) body.set("camera", JSON.stringify(camera));
      try {
        const response = await fetch(room.dataset.cameraUrl, { method: "POST", body, headers: { Accept: "application/json" } });
        if (!response.ok) throw new Error("camera");
        cameraLocked = locked;
        renderer.controlsEnabled = !locked;
        engineStatus.textContent = locked ? "3D-Würfel bereit · Kamera fixiert" : "3D-Würfel bereit · Kamera einstellbar";
      } catch (_) {
        cameraLock.checked = !locked;
        message.textContent = "Die Kameraposition konnte nicht gespeichert werden.";
      }
    });

    ensureEngine();
    const poll = async () => {
      await fetchState().catch(() => {});
      window.setTimeout(poll, 850);
    };
    poll();
  };
  initGame();
})();
