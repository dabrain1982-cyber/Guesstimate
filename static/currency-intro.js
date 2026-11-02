(() => {
  const intro = document.querySelector('[data-currency-intro]');
  const catchup = document.querySelector('[data-catchup-dialog]');
  const next = () => { if (catchup && !catchup.open) catchup.showModal(); };
  if (!intro) { next(); return; }
  intro.querySelectorAll('[data-intro-close]').forEach(button =>
    button.addEventListener('click', () => intro.close()));
  intro.addEventListener('close', next, {once:true});
  fetch(intro.dataset.claimUrl, {
    method:'POST', credentials:'same-origin', cache:'no-store',
    headers:{'Content-Type':'application/x-www-form-urlencoded',Accept:'application/json'},
    body:new URLSearchParams({csrf_token:intro.dataset.csrf}),
  }).then(async response => {
    if (!response.ok) throw new Error('announcement claim failed');
    const result = await response.json();
    if (result.show) intro.showModal();
    else next();
  }).catch(() => next());
})();
