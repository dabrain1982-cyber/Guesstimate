document.querySelectorAll("[data-leaderboards]").forEach((leaderboard) => {
  const tabs = [...leaderboard.querySelectorAll("[data-leaderboard-tab]")];
  const panels = [...leaderboard.querySelectorAll("[data-leaderboard-panel]")];

  const select = (selectedTab) => {
    const selectedKey = selectedTab.dataset.leaderboardTab;
    tabs.forEach((tab) => tab.setAttribute("aria-selected", String(tab === selectedTab)));
    panels.forEach((panel) => {
      panel.hidden = panel.dataset.leaderboardPanel !== selectedKey;
    });
  };

  tabs.forEach((tab, index) => {
    tab.addEventListener("click", () => select(tab));
    tab.addEventListener("keydown", (event) => {
      if (!["ArrowLeft", "ArrowRight"].includes(event.key)) return;
      event.preventDefault();
      const step = event.key === "ArrowRight" ? 1 : -1;
      const next = tabs[(index + step + tabs.length) % tabs.length];
      next.focus();
      select(next);
    });
  });
});
