(() => {
  const tabs = [...document.querySelectorAll("[data-shop-tab]")];
  const panels = [...document.querySelectorAll("[data-shop-panel]")];
  if (!tabs.length) return;

  const select = (name) => {
    tabs.forEach((tab) => tab.setAttribute("aria-selected", String(tab.dataset.shopTab === name)));
    panels.forEach((panel) => { panel.hidden = panel.dataset.shopPanel !== name; });
    const url = new URL(window.location.href);
    url.searchParams.set("tab", name);
    window.history.replaceState({}, "", url);
  };

  tabs.forEach((tab) => tab.addEventListener("click", () => select(tab.dataset.shopTab)));
  const requested = new URLSearchParams(window.location.search).get("tab");
  if (["avatars", "plaques", "backgrounds", "phrases"].includes(requested)) select(requested);
})();
