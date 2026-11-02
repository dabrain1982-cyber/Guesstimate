export function createFortifyControls({ turn, territories, onChange, onMove }) {
  const byId = new Map(territories.map(territory => [territory.id, territory]));
  let sourceId = null;
  let targetId = null;
  let message = '';
  return {
    get sourceId() { return sourceId; },
    get targetId() { return targetId; },
    get hint() { return turn.fortified ? 'Festigen abgeschlossen. Du kannst den Zug beenden.' : message || 'Wähle ein eigenes Ausgangsland oder beende den Zug ohne Verschiebung.'; },
    selected(territory) {
      targetId = null;
      if (!territory || turn.fortified) { sourceId = null; message = ''; onChange(); return; }
      if (sourceId && turn.fortifyTargets(sourceId).includes(territory.id)) {
        targetId = territory.id;
        message = `${byId.get(sourceId).name} → ${territory.name}: Wähle die Truppenzahl.`;
        onChange();
        onMove(territory, sourceId);
        return;
      }
      if (turn.fortifyTargets(territory.id).length) {
        sourceId = territory.id;
        message = `${territory.name}: Wähle ein grün markiertes eigenes Nachbarland.`;
      } else {
        message = turn.owner(territory.id) !== turn.ownerId
          ? 'Du kannst nur Truppen zwischen eigenen Nachbarländern verschieben.'
          : 'Wähle ein eigenes Land mit mindestens zwei Truppen und einem eigenen Nachbarland.';
      }
      onChange();
      document.querySelector('#turn-status').textContent = message;
    },
    amountClosed() { targetId = null; if (turn.fortified) sourceId = null; },
    clear() { sourceId = targetId = null; message = ''; },
  };
}
