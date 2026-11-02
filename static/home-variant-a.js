(() => {
  const carousel = document.querySelector("[data-game-carousel]");
  if (!carousel) return;

  const slides = [...carousel.querySelectorAll("[data-game-slide]")];
  let activeIndex = 0;
  let rotation;

  function select(index) {
    activeIndex = (index + slides.length) % slides.length;
    slides.forEach((slide, slideIndex) => {
      const selected = slideIndex === activeIndex;
      slide.hidden = !selected;
      slide.classList.toggle("is-active", selected);
    });
  }

  function startRotation() {
    window.clearInterval(rotation);
    rotation = window.setInterval(() => select(activeIndex + 1), 10000);
  }

  carousel.querySelector("[data-carousel-prev]")?.addEventListener("click", () => {
    select(activeIndex - 1);
    startRotation();
  });
  carousel.querySelector("[data-carousel-next]")?.addEventListener("click", () => {
    select(activeIndex + 1);
    startRotation();
  });
  carousel.addEventListener("mouseenter", () => window.clearInterval(rotation));
  carousel.addEventListener("mouseleave", startRotation);
  carousel.addEventListener("focusin", () => window.clearInterval(rotation));
  carousel.addEventListener("focusout", startRotation);
  startRotation();

  if (new URLSearchParams(window.location.search).has("regeln")) {
    document.querySelector("[data-rules-open]")?.click();
  }
})();
