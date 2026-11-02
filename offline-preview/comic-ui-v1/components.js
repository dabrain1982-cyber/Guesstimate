// A single preview button composition, used at every size and in every demo.
const paths = {
  arrow: '<path d="m5 12 13 0m-5-5 5 5-5 5"/>',
  cards: '<path d="M7 4h12v16H7z"/><path d="m5 6-3 1 3 14 3-1M11 8h4m-4 4h4m-4 4h2"/>',
  flag: '<path d="M5 21V3m0 1c5-4 8 4 14 0v10c-6 4-9-4-14 0"/>',
  army: '<path d="m7 8 1-5 4 2 4-2 1 5-2 3v4l3 4H6l3-4v-4zM7 8h10M9 12h6M5 21h14"/>',
  plus: '<path d="M12 4v16M4 12h16"/>',
  sword: '<path d="m4 3 7 2 10 15-3 2L8 9zM9 15l8-5M7 17l3 4M5 20l4-3"/>',
  shield: '<path d="M12 2 3 6v7c1 5 5 8 9 10 4-2 8-5 9-10V6zM7 12l4 4 6-8"/>',
  reset: '<path d="M5 6a8 8 0 1 1-1 11M5 2v6h6"/>',
  play: '<path d="m8 4 12 8-12 8z"/>',
  pause: '<path d="M7 4v16M17 4v16"/>',
  bolt: '<path d="m14 2-10 12h7l-1 9L21 9h-8z"/>',
  keyboard: '<rect x="2" y="5" width="20" height="14" rx="3"/><path d="M6 9h1m4 0h1m4 0h1M6 12h1m4 0h1m4 0h1M7 16h10"/>',
  hand: '<path d="M7 12V5a2 2 0 0 1 4 0v5-6a2 2 0 0 1 4 0v6-3a2 2 0 0 1 4 0v7c0 6-3 8-7 8-3 0-5-2-6-4l-3-4a2 2 0 0 1 3-2l2 2"/>',
  check: '<path d="m4 12 5 5L20 5"/>',
  dice: '<rect x="3" y="3" width="18" height="18" rx="4"/><path d="M8 8h.01M16 8h.01M12 12h.01M8 16h.01M16 16h.01"/>',
};

export function icon(name) {
  const holder = document.createElement('span');
  holder.className = 'comic-icon';
  holder.setAttribute('aria-hidden', 'true');
  holder.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">${paths[name] || paths.arrow}</svg>`;
  return holder;
}

export function button({label, variant='primary', symbol, small=false, action, disabled=false, ariaLabel, motion}) {
  const element = document.createElement('button');
  element.type = 'button';
  element.className = `comic-button tone-${variant}${small ? ' size-small' : ''}`;
  element.disabled = disabled;
  if (ariaLabel) element.setAttribute('aria-label', ariaLabel);
  const face = document.createElement('span');
  face.className = 'comic-button-face';
  if (symbol) face.append(icon(symbol));
  const text = document.createElement('span');
  text.className = 'comic-button-label';
  text.textContent = label;
  face.append(text);
  element.append(face);
  let tapAnimation;
  element.addEventListener('click', event => {
    if (element.disabled) return;
    // A quick click can end before :active has visibly travelled. Complete a
    // short down-and-up stroke for actions; selection/toggle buttons stay sunk.
    if (!element.hasAttribute('aria-pressed') && element.getAttribute('role') !== 'tab') {
      const start = getComputedStyle(face).transform;
      const resting = element.matches(':hover') ? 'translateY(-1px)' : 'translateY(0)';
      const pressed = 'translateY(calc(var(--button-depth) - .08em))';
      const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
      const feeling = motion?.() || {};
      tapAnimation?.cancel();
      tapAnimation = face.animate(reduced ? [
        { transform: pressed }, { transform: pressed, offset: .75 }, { transform: resting },
      ] : [
        { transform: start }, { transform: pressed, offset: .28 },
        { transform: pressed, offset: .53 }, { transform: resting },
      ], { duration: reduced ? 120 : (feeling.duration || 300), easing: reduced ? 'steps(1, end)' : (feeling.easing || 'ease-out') });
    }
    action?.(event);
  });
  return { element, label(value) { text.textContent = value; } };
}

export function die(value) {
  const element = document.createElement('div');
  element.className = 'comic-die';
  element.setAttribute('aria-hidden', 'true');
  const positions = {1:[5],2:[1,9],3:[1,5,9],4:[1,3,7,9],5:[1,3,5,7,9],6:[1,3,4,6,7,9]}[value];
  for(let index=1;index<=9;index++) {
    const pip = document.createElement('i');
    if (positions.includes(index)) pip.className='is-dot';
    element.append(pip);
  }
  return element;
}
