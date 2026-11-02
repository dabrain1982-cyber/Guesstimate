document.querySelectorAll("[data-leaderboards]").forEach((leaderboard) => {
  const bindTabs = (container, tabSelector, panelSelector, tabKey, panelKey) => {
    const tabs = [...container.querySelectorAll(tabSelector)];
    const panels = [...container.querySelectorAll(panelSelector)];
    const select = (selected) => {
      tabs.forEach(tab => {
        tab.setAttribute('aria-selected', String(tab === selected));
        tab.tabIndex = tab === selected ? 0 : -1;
      });
      panels.forEach(panel => { panel.hidden = panel.dataset[panelKey] !== selected.dataset[tabKey]; });
    };
    tabs.forEach((tab, index) => {
      tab.addEventListener('click', () => select(tab));
      tab.addEventListener('keydown', event => {
        if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
        event.preventDefault();
        const nextIndex = event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1 :
          (index + (event.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length;
        tabs[nextIndex].focus();
        select(tabs[nextIndex]);
      });
    });
  };
  bindTabs(leaderboard, '[data-leaderboard-group]', '[data-leaderboard-group-panel]', 'leaderboardGroup', 'leaderboardGroupPanel');
  leaderboard.querySelectorAll('[data-leaderboard-group-panel]').forEach(group =>
    bindTabs(group, '[data-leaderboard-tab]', '[data-leaderboard-panel]', 'leaderboardTab', 'leaderboardPanel'));
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
