(() => {
  const overview = document.querySelector('[data-lobby-overview][data-status-url]');
  if (!overview) return;
  const error = overview.querySelector('[data-overview-error]');
  let timer;
  let busy = false;
  let leaving = false;
  const poll = async () => {
    clearTimeout(timer);
    if (leaving || busy) return;
    if (document.hidden) { timer = setTimeout(poll, 3000); return; }
    busy = true;
    try {
      const response = await fetch(overview.dataset.statusUrl, {cache: 'no-store', headers: {Accept: 'application/json'}});
      if (leaving) return;
      if ([401, 403].includes(response.status) || response.redirected) { location.reload(); return; }
      if (!response.ok) throw new Error('overview');
      const state = await response.json();
      if (leaving) return;
      if (state.signature !== overview.dataset.signature) { location.reload(); return; }
      error.hidden = true;
    } catch (_) { if (!leaving) error.hidden = false; }
    finally { busy = false; }
    if (!leaving) timer = setTimeout(poll, 1500);
  };
  overview.querySelector('[data-overview-retry]').addEventListener('click', poll);
  overview.addEventListener('submit', () => { leaving = true; clearTimeout(timer); });
  overview.addEventListener('click', event => { if (event.target.closest('a[href]')) { leaving = true; clearTimeout(timer); } });
  addEventListener('pagehide', () => { leaving = true; clearTimeout(timer); });
  addEventListener('pageshow', event => {
    if (event.persisted) { leaving = false; busy = false; return poll(); }
  });
  document.addEventListener('visibilitychange', () => { if (!document.hidden) poll(); });
  timer = setTimeout(poll, 1500);
})();
