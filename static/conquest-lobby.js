(() => {
  const page = document.querySelector('[data-conquest-overview]');
  if (!page || page.dataset.active === '0') return;
  async function poll() {
    try {
      const response = await fetch(page.dataset.statusUrl, { cache: 'no-store', headers: { Accept: 'application/json' } });
      if (!response.ok) { window.location.assign(page.dataset.overviewUrl || window.location.href); return; }
      const state = await response.json();
      if (state.signature !== page.dataset.signature) { window.location.reload(); return; }
    } catch (_) { /* A temporary outage keeps the current room visible. */ }
    window.setTimeout(poll, 1500);
  }
  window.setTimeout(poll, 1500);
})();
