(() => {
  const nav = document.querySelector('.arena-main-nav');
  if (!nav) return;

  const homeLinks = nav.querySelectorAll('.arena-nav-home a');
  const gameLinks = nav.querySelectorAll('.arena-nav-games a');
  if (homeLinks[0]) homeLinks[0].textContent = 'guesstimate';
  if (homeLinks[1]) homeLinks[1].textContent = 'profil';
  if (homeLinks[2]) homeLinks[2].textContent = 'shop';
  if (gameLinks[0]) gameLinks[0].textContent = 'guesstimate party';
  if (gameLinks[1]) gameLinks[1].textContent = 'stormseed´s perfect';
  if (gameLinks[2]) gameLinks[2].textContent = 'cardboard';

  const rules = {
    daily: {
      label: 'guesstimate',
      title: 'Guesstimate',
      items: [
        'Beantworte täglich fünf Fragen und miss dich mit den anderen in der Quiz-Arena.',
        'Je schneller du richtig antwortest, desto mehr Punkte erhältst du.',
        'Verpasste Runden der laufenden Woche kannst du bis Sonntag nachholen.',
        'Deine Ergebnisse zählen für Tageswertung, Wochenliga und Hall of Fame.'
      ]
    },
    classic: {
      label: 'guesstimate party',
      title: 'Guesstimate Classic',
      items: [
        'Erstelle eine Lobby oder tritt einer offenen Lobby bei. Bis zu zehn Personen können gemeinsam spielen.',
        'Der Host gibt der Lobby einen Namen, wählt eine bis fünf Runden und startet, sobald alle da sind.',
        'Jede Runde besteht aus den fünf bekannten Guesstimate-Fragearten. Alle beantworten dieselben Fragen gleichzeitig.',
        'Richtige und schnelle Antworten bringen Punkte. Das Ergebnis verändert weder iKühe noch die regulären Ranglisten.'
      ]
    },
    perfect: {
      label: 'stormseed´s perfect',
      title: 'Stormseed´s Perfect',
      items: [
        'Erstelle eine Lobby oder tritt einer offenen Lobby bei. Der Host legt Zielpunktzahl oder Spielzeit fest.',
        'Zu jedem seltenen Begriff oder jeder Kuriosität erfinden alle eine möglichst glaubwürdige Antwort.',
        'Die echte Auflösung wird unter die erfundenen Antworten gemischt. Auch die eigene Antwort darf gewählt werden.',
        'Eine richtige Wahl und jede getäuschte Person bringen jeweils 100 Punkte. Der Host kann weitere sachlich richtige Antworten anerkennen.',
        'Beim Zeitspiel wird die laufende Frage noch beendet; danach gewinnt die höchste Punktzahl.'
      ]
    },
    cards: {
      label: 'cardboard',
      title: 'Card-Board',
      items: [
        'Der Card-Board ist ein freier Kartentisch für eure eigenen Regeln und bis zu sechs Personen.',
        'Der Host wählt vor dem Start den Kartensatz. Es wird nicht automatisch ausgeteilt.',
        'Karten können zwischen Ziehstapel, Ablage, freier Tischfläche und den Spielerpulten bewegt werden.',
        'Nur auf dem eigenen Pult siehst du deine Karten offen. Verdeckte Karten verraten den anderen weder Rang noch Farbe.',
        'Zum Tisch gehören außerdem Einsammeln, Mischen und ein gemeinsamer Notizzettel.'
      ]
    }
  };

  const existingButton = document.querySelector('[data-rules-open]');
  let dialog = document.querySelector('#rules-dialog');
  if (existingButton) existingButton.remove();
  if (dialog) dialog.remove();

  const openButton = document.createElement('button');
  openButton.type = 'button';
  openButton.className = 'arena-nav-rules';
  openButton.textContent = 'regeln';
  openButton.setAttribute('aria-haspopup', 'dialog');
  nav.append(openButton);

  dialog = document.createElement('dialog');
  dialog.className = 'rules-dialog rules-library-dialog';
  dialog.id = 'rules-dialog';
  dialog.setAttribute('aria-labelledby', 'rules-library-title');
  dialog.innerHTML = `
    <div class="rules-panel">
      <div class="rules-heading">
        <div><span class="eyebrow">SO WIRD GESPIELT</span><h2 id="rules-library-title">Spielregeln</h2></div>
        <button class="rules-close" type="button" aria-label="Spielregeln schließen">×</button>
      </div>
      <div class="rules-game-tabs" role="tablist" aria-label="Spiel auswählen"></div>
      <section class="rules-game-panel" aria-live="polite"><h3></h3><ul></ul></section>
    </div>`;
  document.body.append(dialog);

  const tabList = dialog.querySelector('.rules-game-tabs');
  const title = dialog.querySelector('.rules-game-panel h3');
  const list = dialog.querySelector('.rules-game-panel ul');
  const tabs = new Map();

  const initial = location.pathname.startsWith('/party') ? 'classic'
    : location.pathname.startsWith('/nerd') ? 'perfect'
    : location.pathname.startsWith('/karten') ? 'cards' : 'daily';

  function selectRules(key) {
    const selected = rules[key];
    tabs.forEach((button, tabKey) => button.setAttribute('aria-selected', String(tabKey === key)));
    title.textContent = selected.title;
    list.replaceChildren(...selected.items.map(item => {
      const li = document.createElement('li');
      li.textContent = item;
      return li;
    }));
  }

  Object.entries(rules).forEach(([key, entry]) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.role = 'tab';
    button.className = `rules-game-tab rules-game-${key}`;
    button.textContent = entry.label;
    button.addEventListener('click', () => selectRules(key));
    tabs.set(key, button);
    tabList.append(button);
  });
  selectRules(initial);

  openButton.addEventListener('click', () => dialog.showModal());
  dialog.querySelector('.rules-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
})();
