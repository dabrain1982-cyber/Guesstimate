import { BOARD_POSITIONS } from './territory-model.js';

export const SYMBOL_LABELS = { infantry: 'Infanterie', cavalry: 'Reiter', artillery: 'Geschütz', wild: 'Joker' };
const TYPES = ['infantry', 'cavalry', 'artillery'];

export function cardCatalog(world) {
  const names = new Map(world.territories.map(row => [row.id, row.name]));
  names.set('joker-1', 'Joker I'); names.set('joker-2', 'Joker II');
  const symbols = world.cardSymbols || Object.fromEntries(world.territories.map((row, index) => [row.id, TYPES[index % 3]]));
  return Object.entries(symbols).map(([id, symbol]) => ({ id, name: names.get(id), symbol, type: SYMBOL_LABELS[symbol] }));
}

export function isCardSet(cards) {
  if (cards.length !== 3 || new Set(cards.map(card => card.id)).size !== 3) return false;
  if (cards.some(card => !SYMBOL_LABELS[card.symbol])) return false;
  const normal = cards.filter(card => card.symbol !== 'wild').map(card => card.symbol);
  return new Set(normal).size === 1 || new Set(normal).size === normal.length;
}

// Original vector marks, shared by every reward card and inventory card.
const ICONS = {
  infantry: '<path d="M32 24Q32 9 48 9T64 24Z" fill="currentColor"/><circle cx="48" cy="31" r="10" fill="currentColor"/><path d="M33 49Q48 40 63 49L66 70H30Z" fill="currentColor"/><path d="M36 68L31 94M58 68L63 94M33 52L20 68M62 52L72 64M76 15V92M71 20H81M24 95H38M56 95H70"/>',
  cavalry: '<circle cx="53" cy="20" r="9" fill="currentColor"/><path d="M48 32L46 52H63L59 35Z" fill="currentColor"/><path d="M48 36L68 44M55 52L61 72"/><path d="M20 58Q22 46 44 49L69 49L76 28L85 34L91 50L81 55L77 67H29Z" fill="currentColor"/><path d="M30 64L24 90M44 65L40 91M67 64L72 90M76 60L85 81M20 55L11 72M78 30L77 18L85 28"/>',
  artillery: '<path d="M20 57L14 39L78 17L85 35Z" fill="currentColor"/><path d="M80 19L88 16L94 31L86 35M46 53L34 72H73L88 88M15 90H90"/><circle cx="37" cy="76" r="18"/><circle cx="37" cy="76" r="4" fill="currentColor"/><path d="M37 58V94M19 76H55M24 63L50 89M24 89L50 63"/>',
};

function symbolImage(symbol) {
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('viewBox', '0 0 104 104');
  svg.setAttribute('role', 'img');
  svg.setAttribute('aria-label', `${SYMBOL_LABELS[symbol]}-Symbol`);
  svg.setAttribute('fill', 'none');
  svg.setAttribute('stroke', 'currentColor');
  svg.setAttribute('stroke-width', '5');
  svg.setAttribute('stroke-linecap', 'round');
  svg.setAttribute('stroke-linejoin', 'round');
  svg.innerHTML = ICONS[symbol];
  return svg;
}

export function createCountryCard(card, { owned = false, ownerName = null, ownerColor = null } = {}) {
  const symbol = card.symbol || Object.keys(SYMBOL_LABELS).find(key => SYMBOL_LABELS[key] === card.type);
  const article = document.createElement('article');
  article.className = 'country-card';
  article.dataset.cardId = card.id;
  article.dataset.symbol = symbol;
  article.dataset.owned = String(owned && symbol !== 'wild');
  if (ownerColor) article.style.setProperty('--card-owner', ownerColor);
  const title = document.createElement('h3');
  title.textContent = card.name;
  const face = document.createElement('div');
  face.className = 'country-card-symbol' + (symbol === 'wild' ? ' joker-symbols' : '');
  face.append(...(symbol === 'wild' ? TYPES : [symbol]).map(symbolImage));
  const type = document.createElement('p');
  type.className = 'country-card-type';
  type.textContent = card.type;
  const mapWindow = document.createElement('div');
  mapWindow.className = 'country-card-map';
  if (symbol === 'wild') {
    mapWindow.classList.add('joker-caption');
    mapWindow.textContent = 'Ersetzt jedes Symbol';
  } else {
    const map = document.createElement('img');
    map.src = new URL('./assets/karte.png', import.meta.url).href;
    map.alt = ''; map.draggable = false;
    const [x, y] = BOARD_POSITIONS[card.id];
    map.style.left = `calc(50% - ${x / 2}px)`;
    map.style.top = `calc(50% - ${y / 2}px)`;
    mapWindow.append(map);
  }
  const brand = document.createElement('small');
  brand.textContent = 'stormseed´s conquest';
  const ownership = document.createElement('div');
  ownership.className = 'country-card-ownership';
  const status = symbol === 'wild' ? 'Joker · kein eigenes Gebiet'
    : owned ? 'Dein Gebiet' : ownerName ? 'Gebiet von ' + ownerName : 'Kein eigenes Gebiet';
  const label = document.createElement('strong'); label.textContent = status;
  ownership.append(label);
  if (owned && symbol !== 'wild') {
    const bonus = document.createElement('span'); bonus.className = 'country-card-bonus';
    bonus.textContent = '+2 hier beim Eintausch';
    ownership.append(bonus);
  }
  article.setAttribute('aria-label', `${card.name} – ${card.type} – ${status}${owned && symbol !== 'wild' ? ' – automatisch +2 Einheiten hier beim Eintausch' : ''}`);
  article.append(title, ownership, face, type, mapWindow, brand);
  return article;
}
