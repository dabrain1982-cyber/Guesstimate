/* Shared waiting-room behavior. Game rules and membership stay on the server. */
(() => {
  const room = document.querySelector('.game-lobby');
  if (!room || room.dataset.active === '0' || !room.dataset.statusUrl) return;
  const settings = room.querySelector('[data-lobby-settings]');
  const hint = settings?.querySelector('[data-lobby-autosave]');
  let pending = Promise.resolve();
  let saving = 0;
  let dirty = false;
  let failed = false;
  let submitting = false;
  let starting = false;
  let failureMessage = '';
  let timer;

  const readStatus = async () => {
    const response = await fetch(room.dataset.statusUrl, {cache: 'no-store', headers: {Accept: 'application/json'}});
    if (!response.ok) {
      const error = new Error('status');
      error.status = response.status;
      throw error;
    }
    return response.json();
  };
  const adoptSettings = state => {
    if (state.revision != null) room.dataset.revision = String(state.revision);
    if (state.rounds != null) room.dataset.rounds = String(state.rounds);
    if (state.player_limit != null) room.querySelector('[data-lobby-occupancy]').textContent = `${state.members.length}/${state.player_limit} Plätze belegt`;
    for (const member of state.members || []) {
      if (!member.color) continue;
      const seat = room.querySelector(`[data-lobby-member="${member.id}"] .game-lobby-seat`);
      if (seat) { seat.style.setProperty('--lobby-seat-color', member.color); seat.querySelector('[data-lobby-seat-label]').textContent = `${member.seat} · ${member.army_name}`; }
    }
    if (state.name != null) {
      room.dataset.lobbyName = state.name;
      room.querySelector('[data-lobby-title]').textContent = state.name;
      document.title = `${state.name} · ${room.querySelector('.game-name').textContent}`;
    }
  };
  const save = () => {
    clearTimeout(timer);
    const body = new FormData(settings);
    dirty = false;
    saving += 1;
    if (hint) hint.textContent = 'Speichert …';
    pending = pending.then(async () => {
      try {
        const response = await fetch(settings.dataset.settingsUrl, {method: 'POST', body, headers: {Accept: 'application/json'}});
        if (!response.ok) {
          const details = typeof response.json === 'function' ? await response.json().catch(() => ({})) : {};
          throw new Error(details.error || 'Speichern fehlgeschlagen. Bitte erneut versuchen.');
        }
        adoptSettings(await readStatus());
        failed = false;
      } catch (error) {
        failed = true;
        failureMessage = error.message;
      } finally {
        saving -= 1;
        if (!saving && hint) hint.textContent = failed ? failureMessage : 'Gespeichert.';
      }
    });
    return pending;
  };
  settings?.addEventListener('input', event => {
    dirty = true;
    if (hint) hint.textContent = 'Wird übernommen …';
    if (event.target.matches('input[name="name"], input[type="number"]')) {
      clearTimeout(timer);
      timer = setTimeout(save, 500);
    }
  });
  settings?.addEventListener('change', save);
  settings?.addEventListener('submit', async event => {
    if (submitting) return;
    event.preventDefault();
    if (starting) return;
    starting = true;
    const submitter = event.submitter;
    // Include the last edit even if blur/change has not fired, then drain all saves.
    await save();
    if (failed) { starting = false; return; }
    submitting = true;
    settings.requestSubmit(submitter);
  });

  const poll = async () => {
    if (submitting) return;
    try {
      const state = await readStatus();
      // An own save must never reload the form and discard the next edit.
      if (!saving && !dirty && !failed) {
        const changed = state.status !== room.dataset.lobbyState ||
          String(state.members.length) !== room.dataset.memberCount ||
          (room.dataset.memberSignature != null && state.members.map(member => member.id).join(',') !== room.dataset.memberSignature) ||
          (state.host_user_id != null && String(state.host_user_id) !== room.dataset.lobbyHost) ||
          (state.revision != null && String(state.revision) !== room.dataset.revision) ||
          (state.rounds != null && String(state.rounds) !== room.dataset.rounds) ||
          (state.name != null && state.name !== room.dataset.lobbyName);
        if (changed) {
          if (state.status === 'closed' && room.dataset.overviewUrl) window.location.assign(room.dataset.overviewUrl);
          else window.location.reload();
          return;
        }
      }
    } catch (error) {
      if ([401, 403, 404, 410].includes(error.status)) {
        if (room.dataset.overviewUrl) window.location.assign(room.dataset.overviewUrl);
        else window.location.reload();
        return;
      }
      // Keep the room and unsaved inputs during a temporary interruption.
    }
    setTimeout(poll, 1000);
  };
  setTimeout(poll, 1000);
})();
