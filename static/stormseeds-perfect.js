(() => {
  const room = document.querySelector("[data-perfect-room]");
  if (!room) return;

  const phase = room.dataset.phase || "";
  const statusUrl = room.dataset.statusUrl;
  const indexUrl = room.dataset.indexUrl || "/nerd";
  const initialRound = room.dataset.roundId || "";
  const initialSignature = room.dataset.lobbySignature || "";
  const deadlineValue = room.dataset.deadline;
  const isPaused = room.dataset.paused === "true";
  const pausedAtValue = room.dataset.pausedAt;
  const timer = document.querySelector("[data-timer]");
  const countdown = document.querySelector("[data-countdown]");
  const gameTimer = document.querySelector("[data-game-timer]");
  let reloading = false;
  let pausedSeconds = null;
  let pausedGameSeconds = null;
  let warningShown = false;

  if (isPaused && deadlineValue) {
    const parsedDeadline = new Date(deadlineValue);
    if (!Number.isNaN(parsedDeadline.getTime())) {
      const pauseMoment = new Date(pausedAtValue || "");
      const frozenAt = Number.isNaN(pauseMoment.getTime()) ? Date.now() : pauseMoment.getTime();
      pausedSeconds = Math.max(0, Math.ceil((parsedDeadline.getTime() - frozenAt) / 1000));
    }
  }
  if (isPaused && gameTimer?.dataset.gameDeadline) {
    const parsedGameDeadline = new Date(gameTimer.dataset.gameDeadline);
    if (!Number.isNaN(parsedGameDeadline.getTime())) {
      const pauseMoment = new Date(pausedAtValue || "");
      const frozenAt = Number.isNaN(pauseMoment.getTime()) ? Date.now() : pauseMoment.getTime();
      pausedGameSeconds = Math.max(0, Math.ceil((parsedGameDeadline.getTime() - frozenAt) / 1000));
    }
  }

  const remainingSeconds = () => {
    if (!deadlineValue) return null;
    const deadline = new Date(deadlineValue);
    if (Number.isNaN(deadline.getTime())) return null;
    return pausedSeconds ?? Math.max(0, Math.ceil((deadline.getTime() - Date.now()) / 1000));
  };

  const paintClock = () => {
    const seconds = remainingSeconds();
    if (seconds === null) return;
    if (timer) {
      const minutes = Math.floor(seconds / 60);
      timer.textContent = `${minutes}:${String(seconds % 60).padStart(2, "0")}`;
      timer.classList.toggle("is-urgent", seconds <= 15);
    }
    if (countdown) countdown.textContent = String(Math.max(1, seconds));
    const warning = document.querySelector("[data-time-warning]");
    if (warning && seconds <= 30 && !warningShown) {
      warningShown = true;
      warning.classList.add("is-visible");
    }
    if (gameTimer && gameTimer.dataset.gameDeadline) {
      const gameEnd = new Date(gameTimer.dataset.gameDeadline);
      const gameSeconds = pausedGameSeconds ?? Math.max(
        0,
        Math.ceil((gameEnd.getTime() - Date.now()) / 1000),
      );
      if (!Number.isNaN(gameEnd.getTime())) {
        const hours = Math.floor(gameSeconds / 3600);
        const minutes = Math.floor((gameSeconds % 3600) / 60);
        const secondsPart = String(gameSeconds % 60).padStart(2, "0");
        gameTimer.textContent = gameSeconds
          ? `Noch ${hours ? `${hours}:` : ""}${String(minutes).padStart(hours ? 2 : 1, "0")}:${secondsPart}`
          : "Zeit abgelaufen";
      }
    }
  };

  const settings = document.querySelector("[data-perfect-settings]");
  if (settings) {
    const autosave = settings.querySelector("[data-perfect-autosave]");
    let saveTimer = null;
    let saving = false;
    const syncGoalFields = () => {
      const selected = settings.querySelector("input[name='goal_mode']:checked")?.value;
      settings.querySelectorAll("[data-goal-value]").forEach((field) => {
        field.disabled = field.dataset.goalValue !== selected;
      });
      settings.querySelectorAll("[data-goal-value-panel]").forEach((panel) => {
        panel.hidden = panel.dataset.goalValuePanel !== selected;
      });
    };
    const saveSettings = async () => {
      if (saving) return;
      saving = true;
      if (autosave) autosave.textContent = "Wird übernommen …";
      try {
        const response = await fetch(settings.action, {
          method: "POST",
          body: new FormData(settings),
          headers: { Accept: "application/json" },
        });
        if (!response.ok) throw new Error("settings");
        if (autosave) autosave.textContent = "Übernommen ✓";
      } catch (_) {
        if (autosave) autosave.textContent = "Konnte nicht übernommen werden.";
      } finally {
        saving = false;
      }
    };
    const queueSave = () => {
      window.clearTimeout(saveTimer);
      saveTimer = window.setTimeout(saveSettings, 180);
    };
    settings.querySelectorAll("input[name='goal_mode']").forEach((radio) => {
      radio.addEventListener("change", () => {
        syncGoalFields();
        queueSave();
      });
    });
    settings.querySelectorAll("select").forEach((select) => {
      select.addEventListener("change", queueSave);
    });
    settings.querySelector("input[name='name']")?.addEventListener("change", queueSave);
    settings.addEventListener("submit", (event) => {
      event.preventDefault();
      event.stopImmediatePropagation();
      queueSave();
    });
    syncGoalFields();
  }

  const reload = () => {
    if (reloading) return;
    reloading = true;
    window.location.reload();
  };

  const poll = async () => {
    if (!statusUrl || document.hidden || reloading) return;
    try {
      const response = await fetch(statusUrl, {
        headers: { Accept: "application/json" },
        cache: "no-store",
      });
      if (response.status === 404) {
        window.location.assign(indexUrl);
        return;
      }
      if (!response.ok) return;
      const state = await response.json();
      const stateRound = state.round_id ? String(state.round_id) : "";
      if (
        state.phase !== phase ||
        stateRound !== initialRound ||
        state.lobby_signature !== initialSignature
      ) reload();
    } catch (_) {
      // A short connection loss should not interrupt the current screen.
    }
  };

  const answerInput = document.querySelector("[data-answer-input]");
  const charCount = document.querySelector("[data-char-count]");
  const answerForm = answerInput?.closest("form[data-draft-url]");
  let answerSaveTimer = null;
  const saveDraft = async (form) => {
    if (!form?.dataset.draftUrl || isPaused) return;
    try {
      await fetch(form.dataset.draftUrl, {
        method: "POST",
        body: new FormData(form),
        headers: { Accept: "application/json" },
        cache: "no-store",
      });
    } catch (_) {
      // The normal submit button remains available if a draft request fails.
    }
  };
  if (answerInput && charCount) {
    const updateCount = () => {
      charCount.textContent = `${answerInput.value.length} / 220`;
      window.clearTimeout(answerSaveTimer);
      answerSaveTimer = window.setTimeout(() => saveDraft(answerForm), 120);
    };
    answerInput.addEventListener("input", updateCount);
    updateCount();
    answerInput.focus();
  }

  const voteForm = document.querySelector("[data-vote-form][data-draft-url]");
  voteForm?.querySelectorAll("input[name='vote_key']").forEach((choice) => {
    choice.addEventListener("change", () => saveDraft(voteForm));
  });

  if (isPaused) {
    room.querySelectorAll("form:not(.perfect-pause-form):not(.perfect-next-question-form):not([data-leave-form]) input, form:not(.perfect-pause-form):not(.perfect-next-question-form):not([data-leave-form]) textarea, form:not(.perfect-pause-form):not(.perfect-next-question-form):not([data-leave-form]) button").forEach((control) => {
      control.disabled = true;
    });
  }

  document.querySelectorAll("form").forEach((form) => {
    if (form.matches("[data-leave-form]")) return;
    form.addEventListener("submit", () => {
      form.querySelectorAll("button[type='submit']").forEach((button) => {
        button.disabled = true;
      });
    });
  });

  const leaveForm = document.querySelector("[data-leave-form]");
  if (leaveForm) {
    leaveForm.addEventListener("submit", (event) => {
      const memberCount = Number(leaveForm.dataset.memberCount || "0");
      if (memberCount > 1 && !window.confirm("Möchtest du diese Runde wirklich verlassen?")) {
        event.preventDefault();
      }
    });
  }

  paintClock();
  window.setInterval(paintClock, 250);
  window.setInterval(poll, 900);
  document.addEventListener("visibilitychange", () => {
    if (!document.hidden) poll();
  });
})();
