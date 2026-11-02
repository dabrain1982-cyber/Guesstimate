(() => {
  const button = document.querySelector('[data-mail-button]');
  if (!button) return;
  const form = button.closest('form');
  const count = button.querySelector('[data-mail-count]');
  let busy = false;
  let leaving = false;
  form.addEventListener('submit', () => {
    leaving = true;
    button.classList.remove('is-waiting');
  });
  const refresh = async () => {
    if (busy || leaving || document.hidden) return;
    busy = true;
    try {
      const response = await fetch(button.dataset.statusUrl, { credentials: 'same-origin', cache: 'no-store', headers: { Accept: 'application/json' } });
      if (!response.ok || response.redirected) return;
      const status = await response.json();
      if (leaving) return;
      button.classList.toggle('is-waiting', status.attention);
      count.hidden = !status.unread;
      count.textContent = String(status.unread);
      form.elements.through.value = String(status.latest);
      button.setAttribute('aria-label', status.unread ? `Mail · ${status.unread} ungelesen` : 'Mail');
    } catch (_) { /* Keep the last known state while the connection is unavailable. */ }
    finally { busy = false; }
  };
  window.setInterval(refresh, 30000);
  document.addEventListener('visibilitychange', refresh);
  window.addEventListener('pageshow', () => { leaving = false; refresh(); });
})();
