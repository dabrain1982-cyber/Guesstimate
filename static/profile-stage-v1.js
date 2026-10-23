(() => {
  const fit = (element) => {
    element.style.removeProperty("font-size");
    let size = parseFloat(getComputedStyle(element).fontSize);
    const minimum = 8;
    while (
      size > minimum &&
      (element.scrollWidth > element.clientWidth || element.scrollHeight > element.clientHeight)
    ) {
      size -= 0.5;
      element.style.fontSize = `${size}px`;
    }
  };

  const fields = () => [...document.querySelectorAll("[data-fit-podium-text]")];
  if (!fields().length) return;

  const fitAll = () => fields().forEach(fit);
  fitAll();
  document.fonts?.ready.then(fitAll);
  document.addEventListener("profile:updated", fitAll);

  if ("ResizeObserver" in window) {
    const observer = new ResizeObserver(fitAll);
    fields().forEach((element) => observer.observe(element));
    document.addEventListener("profile:updated", () => {
      fields().forEach((element) => observer.observe(element));
    });
  } else {
    window.addEventListener("resize", fitAll);
  }
})();
