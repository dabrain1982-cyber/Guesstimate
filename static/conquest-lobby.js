(() => {
  const lobby = document.querySelector("[data-conquest-lobby]");
  if (!lobby) return;
  const settings = lobby.querySelector("[data-conquest-settings]");
  let saving = false;
  let reloadAfterSave = false;
  const saveSettings = async () => {
    if (!settings || saving) { reloadAfterSave = true; return; }
    saving = true;
    const note = settings.querySelector("[data-conquest-autosave]");
    note.textContent = "Speichert …";
    try {
      const response = await fetch(settings.dataset.settingsUrl, { method: "POST", body: new FormData(settings) });
      if (!response.ok) throw new Error("save");
      note.textContent = "Gespeichert.";
    } catch (_) { note.textContent = "Konnte nicht gespeichert werden."; }
    saving = false;
    if (reloadAfterSave) { reloadAfterSave = false; saveSettings(); }
  };
  settings?.querySelectorAll("select").forEach((select) => select.addEventListener("change", saveSettings));
  const poll = async () => {
    try {
      const response = await fetch(lobby.dataset.statusUrl, { cache: "no-store", headers: { Accept: "application/json" } });
      if (!response.ok) return window.location.reload();
      const state = await response.json();
      if (state.status !== "waiting" || String(state.members.length) !== lobby.dataset.memberCount) return window.location.reload();
      if (String(state.revision) !== lobby.dataset.revision) {
        if (!settings) return window.location.reload();
        lobby.dataset.revision = String(state.revision);
      }
    } catch (_) {}
    window.setTimeout(poll, 1000);
  };
  window.setTimeout(poll, 1000);
})();
