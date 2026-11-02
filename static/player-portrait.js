// One compact player component. Games supply public data, never their own markup.
export function createPlayerPortrait(host) {
  const make = (tag, className) => {
    const node = document.createElement(tag);
    node.className = className;
    return node;
  };
  const root = make('div', 'player-portrait');
  const stats = make('div', 'player-portrait-stats');
  stats.hidden = true;
  const statViews = ['troops', 'countries'].map((key, index) => {
    const row = make('span', 'player-portrait-stat');
    const symbol = make('span', 'player-portrait-stat-icon');
    symbol.setAttribute('aria-hidden', 'true');
    symbol.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' + (index === 0
      ? '<circle cx="12" cy="4" r="2"/><path d="m8 9 4-2 4 2m-4-2v8m-4 6 4-6 4 6M8 9l-2 5m10-5 2 5"/>'
      : '<path d="m3 8 6-4 6 3 6-3v15l-6 3-6-3-6 3zm6-4v15m6-12v15"/>') + '</svg>';
    const value = make('strong', 'player-portrait-stat-value');
    row.append(symbol, value); stats.append(row);
    return {key, row, value};
  });
  const frame = make('span', 'player-portrait-frame');
  const image = make('img', 'player-portrait-image');
  const fallback = make('span', 'player-portrait-fallback');
  fallback.setAttribute('aria-hidden', 'true');
  frame.append(image, fallback);
  const copy = make('div', 'player-portrait-copy');
  const status = make('span', 'player-portrait-status');
  const name = make('strong', 'player-portrait-name');
  const metrics = make('span', 'player-portrait-metrics');
  const wallet = make('div', 'player-portrait-wallet');
  const walletValues = ['balance', 'wager', 'gain'].map((key, index) => {
    const item = make('span', 'player-portrait-wallet-item');
    const label = make('small', 'player-portrait-wallet-label');
    label.textContent = ['Bestand', 'Einsatz', 'Gewinn'][index];
    const amount = make('strong', 'player-portrait-wallet-value');
    item.append(label, amount); wallet.append(item);
    return {key, amount, label};
  });
  wallet.hidden = true;
  copy.append(status, name, metrics, wallet);
  const badge = make('button', 'player-portrait-badge');
  badge.type = 'button'; badge.hidden = true;
  let openCards = null;
  badge.addEventListener('click', () => openCards?.());
  root.append(stats, frame, copy, badge);
  host.replaceChildren(root);
  image.addEventListener('error', () => { image.hidden = true; fallback.hidden = false; });
  return {
    get anchor() { return frame; },
    focusCards() { badge.focus(); },
    update(player) {
      name.textContent = player.name;
      name.title = player.name;
      status.textContent = player.status || '';
      status.hidden = !player.status;
      metrics.textContent = player.metrics || '';
      metrics.hidden = !player.metrics;
      metrics.title = player.metricsDescription || '';
      wallet.hidden = !player.wallet;
      root.dataset.wallet = String(Boolean(player.wallet));
      metrics.hidden = Boolean(player.wallet) || !player.metrics;
      if (player.wallet) {
        for (const {key, amount, label} of walletValues) {
          if (key === 'balance') label.textContent = 'Bestand' + (player.wallet.unit ? ' · ' + player.wallet.unit : '');
          const value = player.wallet[key];
          amount.textContent = value == null ? '—' : (key === 'gain' && value > 0 ? '+' : '') + Number(value).toLocaleString('de-DE');
          amount.dataset.sign = key === 'gain' && value != null ? (value > 0 ? 'positive' : value < 0 ? 'negative' : 'neutral') : 'neutral';
        }
      }
      root.dataset.kind = player.kind || 'player';
      root.dataset.layout = player.layout || 'default';
      root.dataset.current = String(Boolean(player.current));
      stats.hidden = !player.stats;
      for (const item of statViews) {
        const value = player.stats?.[item.key] ?? 0;
        const label = item.key === 'troops' ? 'Truppen' : 'Länder';
        item.value.textContent = Number(value).toLocaleString('de-DE');
        item.row.title = value + ' ' + label;
        item.row.setAttribute('aria-label', value + ' ' + label);
      }
      badge.hidden = player.cardCount == null;
      badge.textContent = String(player.cardCount ?? '');
      openCards = player.onCards || null;
      badge.disabled = !openCards;
      badge.title = player.name + ': ' + player.cardCount + (player.cardCount === 1 ? ' Länderkarte' : ' Länderkarten');
      badge.setAttribute('aria-label', badge.title + (openCards ? ' · eigene Karten ansehen' : ''));
      root.style.setProperty('--player-color', player.color || '#d8ff42');
      fallback.textContent = Array.from(player.name || '?')[0];
      const portrait = player.portrait;
      if (portrait?.url) {
        if (image.getAttribute('src') !== portrait.url) {
          image.hidden = false;
          fallback.hidden = true;
          image.src = portrait.url;
        }
        image.alt = `${portrait.alt} von ${player.name}`;
        root.style.setProperty('--portrait-scale', String(portrait.crop?.scale || 1));
        root.style.setProperty('--portrait-top', `${portrait.crop?.top || 0}%`);
      } else {
        image.removeAttribute('src');
        image.hidden = true;
        fallback.hidden = false;
        image.alt = '';
      }
    },
  };
}
