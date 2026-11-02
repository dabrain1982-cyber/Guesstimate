(() => {
  const form = document.querySelector("[data-feedback-delay]");
  if (!form) return;

  const button = form.querySelector("button[type='submit']");
  const label = form.querySelector("[data-feedback-button-label]");
  const countdown = form.querySelector("[data-feedback-countdown]");
  const initialRemaining = Math.max(0, Number(form.dataset.remainingMs || 0));
  const startedAt = performance.now();

  const draw = () => {
    const remaining = Math.max(0, initialRemaining - (performance.now() - startedAt));
    if (remaining <= 0) {
      button.disabled = false;
      label.hidden = false;
      countdown.hidden = true;
      return;
    }

    button.disabled = true;
    label.hidden = true;
    countdown.hidden = false;
    countdown.textContent = `Auflösung lesen · ${Math.ceil(remaining / 1000)} s`;
    window.requestAnimationFrame(draw);
  };

  draw();
})();
