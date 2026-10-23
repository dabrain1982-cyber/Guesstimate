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

document.querySelectorAll("[data-week-date]").forEach((tally) => {
  const date = new Date(`${tally.dataset.weekDate}T12:00:00`);
  const day = date.getDay() || 7;
  const addGroup = (count, crossed = false) => {
    const group = document.createElement("span");
    group.className = `tally-group${crossed ? " is-five" : ""}`;
    group.setAttribute("aria-hidden", "true");
    for (let mark = 0; mark < count; mark += 1) group.append(document.createElement("i"));
    tally.append(group);
  };
  addGroup(Math.min(day, 4), day >= 5);
  if (day > 5) addGroup(day - 5);
  tally.setAttribute("aria-label", `Wochentag ${day} von 7`);
});
