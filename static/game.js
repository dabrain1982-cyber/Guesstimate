(() => {
  const list = document.querySelector('#order-list');
  const answer = document.querySelector('#order-answer');
  if (!list || !answer) return;

  const rows = () => [...list.querySelectorAll('li[data-value]')];
  const sync = () => {
    const currentRows = rows();
    currentRows.forEach((row, index) => {
      row.querySelector('.order-position').textContent = index + 1;
    });
    answer.value = JSON.stringify(currentRows.map((row) => row.dataset.value));
  };

  let active = null;
  let placeholder = null;
  let pointerId = null;
  let grabOffsetX = 0;

  const finishDrag = () => {
    if (!active || !placeholder) return;
    placeholder.replaceWith(active);
    active.classList.remove('is-dragging');
    active.removeAttribute('style');
    document.body.classList.remove('sorting-active');
    active = null;
    placeholder = null;
    pointerId = null;
    sync();
  };

  list.addEventListener('pointerdown', (event) => {
    if (active || (event.button !== undefined && event.button !== 0)) return;
    const row = event.target.closest('li[data-value]');
    if (!row) return;
    event.preventDefault();

    const rect = row.getBoundingClientRect();
    active = row;
    pointerId = event.pointerId;
    grabOffsetX = event.clientX - rect.left;
    placeholder = document.createElement('li');
    placeholder.className = 'order-placeholder';
    placeholder.style.height = `${rect.height}px`;
    placeholder.setAttribute('aria-hidden', 'true');
    list.insertBefore(placeholder, row.nextSibling);

    row.classList.add('is-dragging');
    row.style.width = `${rect.width}px`;
    row.style.height = `${rect.height}px`;
    row.style.left = `${rect.left}px`;
    row.style.top = `${rect.top}px`;
    document.body.classList.add('sorting-active');
    row.setPointerCapture(pointerId);
  });

  list.addEventListener('pointermove', (event) => {
    if (!active || event.pointerId !== pointerId) return;
    event.preventDefault();
    active.style.left = `${event.clientX - grabOffsetX}px`;

    const candidates = rows().filter((row) => row !== active);
    const next = candidates.find((row) => {
      const rect = row.getBoundingClientRect();
      return event.clientX < rect.left + rect.width / 2;
    });
    list.insertBefore(placeholder, next || null);
  });

  list.addEventListener('pointerup', (event) => {
    if (!active || event.pointerId !== pointerId) return;
    finishDrag();
  });

  list.addEventListener('pointercancel', finishDrag);

  list.addEventListener('keydown', (event) => {
    const row = event.target.closest('li[data-value]');
    if (!row || !['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
    event.preventDefault();
    if (event.key === 'ArrowLeft' && row.previousElementSibling) {
      list.insertBefore(row, row.previousElementSibling);
    } else if (event.key === 'ArrowRight' && row.nextElementSibling) {
      list.insertBefore(row.nextElementSibling, row);
    }
    sync();
    row.focus();
  });

  document.querySelector('#answer-form')?.addEventListener('submit', sync);
  sync();
})();

