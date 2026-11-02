(() => {
  const selector = "[data-fit-podium-text]";
  const observed = new Set();
  let scheduled = false;

  const fit = (element) => {
    if (!element.isConnected || !element.clientWidth || !element.clientHeight) return;
    element.style.removeProperty("font-size");
    const size = parseFloat(getComputedStyle(element).fontSize);
    if (!Number.isFinite(size)) return;
    const overflows = () => element.scrollWidth > element.clientWidth || element.scrollHeight > element.clientHeight;
    if (!overflows()) return;
    let low = 1;
    let high = size;
    for (let step = 0; step < 12; step += 1) {
      const middle = (low + high) / 2;
      element.style.fontSize = `${middle}px`;
      if (overflows()) high = middle;
      else low = middle;
    }
    element.style.fontSize = `${Math.floor(low * 100) / 100}px`;
  };

  const refresh = () => {
    scheduled = false;
    for (const element of observed) {
      if (!element.isConnected) {
        resizeObserver?.unobserve(element);
        observed.delete(element);
      }
    }
    document.querySelectorAll(selector).forEach((element) => {
      if (!observed.has(element)) {
        observed.add(element);
        resizeObserver?.observe(element);
      }
      fit(element);
    });
  };
  const queue = () => {
    if (!scheduled) {
      scheduled = true;
      requestAnimationFrame(refresh);
    }
  };
  const resizeObserver = "ResizeObserver" in window ? new ResizeObserver(queue) : null;
  if (!resizeObserver) window.addEventListener("resize", queue);

  const containsWindow = (node) => node.nodeType === 1 &&
    (node.matches("[data-profile-window]") || node.querySelector("[data-profile-window]"));
  if ("MutationObserver" in window) {
    new MutationObserver((records) => {
      if (records.some((record) => {
        const element = record.target.nodeType === 1 ? record.target : record.target.parentElement;
        return element?.closest("[data-profile-window]") ||
          [...record.addedNodes, ...record.removedNodes].some(containsWindow);
      })) queue();
    }).observe(document.documentElement, { childList: true, subtree: true, characterData: true });
  }
  document.addEventListener("profile:updated", queue);
  document.fonts?.ready.then(queue);
  // This also supports windows inserted later by a game, with no second renderer.
  window.ProfileWindow = Object.freeze({ refresh: queue });
  queue();
})();
