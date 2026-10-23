(() => {
  const tabs = [...document.querySelectorAll("[data-profile-tab]")];
  const panels = [...document.querySelectorAll("[data-profile-panel]")];
  if (!tabs.length) return;

  const select = (name) => {
    tabs.forEach((tab) => tab.setAttribute("aria-selected", String(tab.dataset.profileTab === name)));
    panels.forEach((panel) => { panel.hidden = panel.dataset.profilePanel !== name; });
  };

  tabs.forEach((tab) => tab.addEventListener("click", () => select(tab.dataset.profileTab)));
  const requested = new URLSearchParams(window.location.search).get("section");
  if (["avatar", "plaque", "background", "phrase"].includes(requested)) select(requested);

  document.addEventListener("submit", async (event) => {
    const form = event.target.closest('form[action*="/profil/ausruesten/"]');
    if (!form || form.dataset.submitting === "true") return;

    event.preventDefault();
    form.dataset.submitting = "true";
    const button = form.querySelector('button[type="submit"]');
    if (button) button.disabled = true;

    const currentPanel = form.closest("[data-profile-panel]");
    const panelScrollTop = currentPanel?.scrollTop ?? 0;
    const pageScrollY = window.scrollY;

    try {
      const response = await fetch(form.action, {
        method: "POST",
        body: new FormData(form),
        credentials: "same-origin",
      });
      if (!response.ok) throw new Error(`Ausrüsten fehlgeschlagen (${response.status})`);

      const nextDocument = new DOMParser().parseFromString(await response.text(), "text/html");
      const nextPreview = nextDocument.querySelector(".profile-window-copy");
      const nextPanel = nextDocument.querySelector(
        `[data-profile-panel="${currentPanel?.dataset.profilePanel}"]`,
      );
      const preview = document.querySelector(".profile-window-copy");
      if (!preview || !currentPanel || !nextPreview || !nextPanel) {
        window.location.assign(response.url);
        return;
      }

      preview.replaceChildren(...nextPreview.childNodes);
      currentPanel.replaceChildren(...nextPanel.childNodes);
      currentPanel.scrollTop = panelScrollTop;
      window.scrollTo(0, pageScrollY);
      window.history.replaceState(null, "", response.url);
      document.dispatchEvent(new CustomEvent("profile:updated"));
    } catch (_error) {
      form.dataset.submitting = "true";
      form.submit();
    }
  });
})();
