(() => {
  document.querySelectorAll("[data-match-buttons]").forEach((board) => {
    const form = board.closest("form");
    const rows = [...board.querySelectorAll("[data-match-row]")];
    const submit = form?.querySelector("[data-match-submit]");
    if (!form || !rows.length) return;

    let locked = false;

    const refresh = () => {
      const selected = new Set(
        rows.map((row) => row.querySelector('input[type="hidden"]').value).filter(Boolean),
      );

      rows.forEach((row) => {
        const input = row.querySelector('input[type="hidden"]');
        row.querySelectorAll("[data-match-value]").forEach((button) => {
          const isSelected = input.value === button.dataset.matchValue;
          const isUsedElsewhere = selected.has(button.dataset.matchValue) && !isSelected;
          button.classList.toggle("is-selected", isSelected);
          button.setAttribute("aria-pressed", String(isSelected));
          button.disabled = locked || isUsedElsewhere;
        });
      });

      const complete = rows.every(
        (row) => row.querySelector('input[type="hidden"]').value,
      );
      if (!complete || locked) return;

      locked = true;
      board.classList.add("is-locked");
      board.querySelectorAll("[data-match-value]").forEach((button) => {
        button.disabled = true;
      });
      if (submit) submit.textContent = "Antwort wird eingeloggt …";
      window.setTimeout(() => form.requestSubmit(), 180);
    };

    board.addEventListener("click", (event) => {
      const button = event.target.closest("[data-match-value]");
      if (!button || button.disabled || locked) return;
      const row = button.closest("[data-match-row]");
      const input = row.querySelector('input[type="hidden"]');
      input.value = input.value === button.dataset.matchValue ? "" : button.dataset.matchValue;
      refresh();
    });

    form.addEventListener("submit", (event) => {
      const complete = rows.every(
        (row) => row.querySelector('input[type="hidden"]').value,
      );
      if (!complete) event.preventDefault();
    });

    refresh();
  });
})();
