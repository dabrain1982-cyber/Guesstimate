(() => {
  const collection = document.querySelector('[data-game-collection]');
  if (!collection) return;
  const choices = [...collection.querySelectorAll('[data-collection-filter]')];
  const groups = collection.querySelector('[data-collection-groups]');
  const results = collection.querySelector('[data-collection-results]');
  const casinoNote = collection.querySelector('[data-casino-note]');
  const games = [...collection.querySelectorAll('[data-collection-modes]')];
  const render = (requestedMode) => {
    const mode = choices.some(choice => choice.value === requestedMode) ? requestedMode : '';
    choices.forEach(choice => { choice.checked = choice.value === mode; });
    groups.hidden = Boolean(mode);
    results.hidden = !mode;
    results.dataset.mode = mode;
    casinoNote.hidden = mode !== 'casino';
    games.forEach(game => { game.hidden = !game.dataset.collectionModes.split(' ').includes(mode); });
  };
  choices.forEach(choice => choice.addEventListener('change', () => {
    const mode = choice.checked ? choice.value : '';
    render(mode);
    const url = new URL(window.location.href);
    if (mode) url.searchParams.set('ansicht', mode);
    else url.searchParams.delete('ansicht');
    window.history.replaceState(window.history.state, '', url);
  }));
  const restore = () => render(new URL(window.location.href).searchParams.get('ansicht'));
  window.addEventListener('pageshow', restore);
  window.addEventListener('popstate', restore);
  restore();
})();
