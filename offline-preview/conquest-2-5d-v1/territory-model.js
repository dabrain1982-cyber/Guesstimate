// Pixel anchors from the existing colour-map implementation. This isolated
// preview supplies its fixture; the application supplies its shared world data.
export const MAP_WIDTH = 1284;
export const MAP_HEIGHT = 1225;
export const BOARD_WIDTH = 12;
export const BOARD_DEPTH = BOARD_WIDTH * MAP_HEIGHT / MAP_WIDTH;
export const BOARD_Y = 2.928;

export const BOARD_POSITIONS = {
  alaska: [99, 180], 'nordwest-territorium': [219, 207], groenland: [566, 152],
  alberta: [196, 321], ontario: [311, 336], ostkanada: [439, 373],
  weststaaten: [164, 478], oststaaten: [333, 459], mittelamerika: [197, 573],
  venezuela: [220, 674], peru: [210, 872], brasilien: [333, 781], argentinien: [190, 1033],
  island: [592, 350], grossbritannien: [559, 494], skandinavien: [657, 388],
  nordeuropa: [626, 531], westeuropa: [548, 620], suedeuropa: [648, 599], russland: [744, 431],
  nordafrika: [529, 694], aegypten: [652, 665], ostafrika: [719, 780],
  zentralafrika: [647, 846], suedafrika: [666, 937], madagaskar: [765, 949],
  ural: [885, 348], sibirien: [958, 308], jakutien: [1103, 246], kamtschatka: [1157, 363],
  irkutsk: [1040, 384], mongolei: [1020, 467], japan: [1134, 546], afghanistan: [855, 512],
  china: [974, 600], 'naher-osten': [762, 683], indien: [884, 682], suedostasien: [997, 677],
  indonesien: [1049, 754], neuguinea: [1195, 785], westaustralien: [1114, 917], ostaustralien: [1204, 918],
};

export const PREVIEW_ARMIES = [
  { id: 'gold', name: 'Gold', color: '#dab249', ink: '#24190b' },
  { id: 'rot', name: 'Rot', color: '#ad3935', ink: '#fff8e1' },
  { id: 'blau', name: 'Blau', color: '#326fa5', ink: '#fff8e1' },
];

export function boardPoint(id, y = BOARD_Y) {
  const anchor = BOARD_POSITIONS[id];
  if (!anchor) throw new Error(`Brettposition fehlt: ${id}`);
  return {
    x: (anchor[0] / MAP_WIDTH - .5) * BOARD_WIDTH,
    y,
    z: (anchor[1] / MAP_HEIGHT - .5) * BOARD_DEPTH,
  };
}

export function buildPreviewTerritories(world) {
  const ids = new Set(world.territories.map(territory => territory.id));
  if (ids.size !== 42 || world.territories.length !== 42) throw new Error('Die Welt muss 42 eindeutige Gebiete enthalten.');
  const byId = new Map(world.territories.map(territory => [territory.id, territory]));
  return world.territories.map((territory, index) => {
    const continent = world.continents.find(item => item.id === territory.continent);
    if (!continent) throw new Error(`Kontinent fehlt: ${territory.id}`);
    const point = boardPoint(territory.id);
    if (Math.abs(point.x) >= BOARD_WIDTH / 2 || Math.abs(point.z) >= BOARD_DEPTH / 2) {
      throw new Error(`Brettposition außerhalb der Karte: ${territory.id}`);
    }
    for (const neighbor of territory.neighbors) {
      if (!byId.get(neighbor)?.neighbors.includes(territory.id)) throw new Error(`Ungültige Nachbarschaft: ${territory.id}/${neighbor}`);
    }
    return {
      ...territory,
      continent,
      point,
      // A repeatable display fixture, not a legal starting setup or saved game.
      owner: PREVIEW_ARMIES[index % PREVIEW_ARMIES.length],
      armies: 1 + (index * 5 + Math.floor(index / 7)) % 8,
    };
  });
}
