(() => {
  const timer = document.querySelector('#time-factor');
  const bar = document.querySelector('#time-factor-bar');
  const value = document.querySelector('#time-factor-value');
  if (!timer || !bar || !value) return;

  const initialElapsed = Number(timer.dataset.elapsed || 0);
  const limit = Number(timer.dataset.limit || 10);
  const hold = Number(timer.dataset.hold || 2);
  const maxPenalty = Number(timer.dataset.maxPenalty || 50);
  const started = performance.now();

  const factorAt = (elapsed) => {
    if (elapsed <= hold) return 1;
    if (elapsed >= limit) return 0;
    const decay = limit - hold;
    const elapsedDecaySeconds = Math.floor(elapsed - hold);
    return (decay - elapsedDecaySeconds) / decay;
  };

  const update = () => {
    const elapsed = initialElapsed + (performance.now() - started) / 1000;
    const factor = factorAt(elapsed);
    const points = 100 - Math.round(maxPenalty * (1 - factor));
    const percent = points;
    bar.style.width = `${percent}%`;
    bar.style.backgroundColor = `hsl(${Math.round(8 + factor * 66)} 92% 61%)`;
    value.textContent = `${points} PKT`;
    timer.querySelector('[role="progressbar"]').setAttribute('aria-valuenow', String(percent));
    if (elapsed < limit) requestAnimationFrame(update);
  };

  update();
})();
