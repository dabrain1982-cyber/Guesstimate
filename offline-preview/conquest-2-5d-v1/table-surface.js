import {mountConquestButtons} from './game-buttons.js';
const markup = `
    <canvas id="scene" aria-label="Räumlicher Tisch mit unserer Conquest-Karte und der Raumkulisse"></canvas>
    <svg id="attack-arrows" class="attack-arrows" aria-hidden="true"><g id="attack-paths"></g></svg>
    <div id="territories" class="territory-layer" role="group" aria-label="42 Länder – Truppenmarke zum Auswählen anklicken"></div>
    <a id="table-back" class="table-back" href="/karten/welteroberung" hidden>← Lobby</a>
      <div class="camera-controls" role="group" aria-label="Kamera">
        <button type="button" data-pose="sit" aria-label="Sitzposition" title="Sitzposition" aria-pressed="true">Sitz</button>
        <label class="sr-only" for="angle">Blickwinkel einstellen</label><input id="angle" type="range" min="32" max="82" step="0.1" value="32" aria-label="Blickwinkel einstellen">
        <button type="button" data-pose="over" aria-pressed="false">Überblick</button>
        <output id="angle-value" for="angle">32°</output>
      </div>
    <aside id="player-roster" class="player-roster" aria-label="Armeen am Tisch" role="list"></aside>
    <div class="country-navigation" aria-label="Land mit Tastatur auswählen">
      <label class="sr-only" for="territory-picker">Land auswählen</label>
      <select id="territory-picker" disabled><option value="">Land auswählen …</option></select>
      <button id="clear-selection" type="button" aria-label="Auswahl aufheben" hidden>×</button>
    </div>
    <p id="selection-status" class="sr-only" role="status" aria-live="polite"></p>
    <section id="turn-bar" class="turn-bar" aria-label="Zugleiste" data-phase="reinforce">
      <span id="turn-actor-name" class="sr-only"></span>
      <div id="combat-intent" class="combat-intent" hidden>
        <div id="attack-dice-choice" class="attack-dice-choice" role="radiogroup" aria-label="Angriffswürfel wählen · Mausrad zurück verringert die Anzahl">
          <div class="dice-options"><button type="button" class="dice-choice" role="radio" data-dice-count="1" aria-label="Mit 1 Angriffswürfel" aria-checked="false"></button><button type="button" class="dice-choice" role="radio" data-dice-count="2" aria-label="Mit 2 Angriffswürfeln" aria-checked="false"></button><button type="button" class="dice-choice" role="radio" data-dice-count="3" aria-label="Mit 3 Angriffswürfeln" aria-checked="true"></button></div>
          <span id="attack-dice-caption">3 Angriffswürfel</span>
        </div>
        <div class="combat-route">
          <div class="combat-country" aria-label="Angreifendes Land"><span id="attack-source-name"></span><strong id="attack-source-strength"></strong></div>
          <span class="combat-direction" aria-hidden="true">➜</span>
          <div class="combat-country combat-target" aria-label="Angegriffenes Land"><span id="attack-target-name"></span><strong id="attack-target-strength"></strong></div>
          <button id="attack-clear" type="button" aria-label="Angriffsziel abwählen" title="Ziel abwählen · dann zum Festigen weitergehen">×</button>
        </div>
      </div>
      <section id="battle-result" class="battle-result" hidden aria-label="Kampfergebnis" role="status"><div id="attack-roll-row" class="dice-row"><span>Angriff</span><div id="attacker-rolls" class="dice-values"></div></div><div id="defense-roll-row" class="dice-row"><span>Verteidigung</span><div id="defender-rolls" class="dice-values defense-dice"></div></div><p id="battle-summary"></p><p id="battle-outcome"></p></section>
    <section id="deployment-controls" class="deployment-controls" hidden aria-labelledby="deployment-land">
      <form id="deployment-form">
        <span id="deployment-purpose" class="dialog-eyebrow sr-only">Eigenes Land verstärken</span><h2 id="deployment-land"></h2>
        <p id="deployment-available"></p>
        <div class="amount-control"><button id="deployment-less" type="button" aria-label="Eine Truppe weniger">−</button><label><span id="deployment-amount-label" class="sr-only">Truppen zum Platzieren</span><input id="deployment-amount" type="number" min="1" max="6" step="1" value="1" inputmode="numeric" required autofocus></label><button id="deployment-more" type="button" aria-label="Eine Truppe mehr">+</button></div>
        <label id="deployment-slider-label" class="sr-only" for="deployment-slider">Anzahl der Verstärkungen</label><input id="deployment-slider" type="range" min="1" max="6" step="1" value="1">
        <p id="deployment-preview"></p><p id="deployment-error" role="alert"></p>
        <div class="dialog-actions"><button id="cancel-deployment" type="button">Abbrechen</button><button id="confirm-deployment" type="submit" class="primary-action">1 Truppe setzen</button></div>
      </form>
    </section>
      <div class="phase-action"><div class="phase-heading"><strong id="turn-phase">Verstärken</strong></div><button id="next-phase" type="button" aria-describedby="turn-hint" disabled>Weiter zum Angriff</button><button id="roll-attack" type="button" aria-describedby="battle-outcome" hidden>Angreifen</button></div>
      <div class="reinforcement-reserve"><strong id="reinforcements-left">6</strong><span id="reserve-caption">zu verteilen</span></div>
      <button id="reset-turn" class="reset-turn" type="button" aria-label="Offline-Beispiel neu starten" title="Offline-Beispiel neu starten">↻</button>
      <p id="turn-hint" class="sr-only">Wähle eine goldene Marke und verteile deine Truppen.</p>
    </section>
    <p id="turn-status" class="sr-only" role="status" aria-live="polite"></p>
    <aside class="prototype-note">Offline-Vorschau <span>·</span> Beispielbelegung</aside>
    <aside id="turn-notice" class="turn-notice" aria-label="Dein Zug" role="status" aria-live="polite" hidden>
      <span class="turn-notice-eyebrow">Deine Armee ist bereit</span><h2>Dein Zug!</h2>
      <div class="turn-notice-count"><strong id="turn-notice-armies">3</strong><span>Armeen zum Verteilen</span></div>
      <p id="turn-notice-detail"></p><button id="notice-open-cards" type="button" hidden>Zu den Karten</button>
    </aside>
    <aside id="turn-receipt" class="turn-receipt" aria-label="Erhaltene Länderkarte" aria-live="polite" hidden>
      <div class="turn-receipt-heading"><span>Neue Länderkarte</span><button id="dismiss-turn-receipt" type="button" aria-label="Kartenhinweis ausblenden">×</button></div>
      <button id="awarded-card" class="awarded-card" type="button" aria-label="Erhaltene Karte und Kartenhand vergrößern"></button><p id="turn-receipt-detail"></p>
    </aside>
    <section id="victory-result" class="victory-result" aria-labelledby="victory-title" hidden>
      <button id="close-victory" class="result-close" type="button" aria-label="Endstand einklappen">×</button>
      <span id="victory-mode" class="result-eyebrow">Feldzug beendet</span>
      <div class="victory-crown" aria-hidden="true">♛</div>
      <div id="winner-portrait" class="winner-portrait"></div>
      <h2 id="victory-title"></h2><p id="victory-reason"></p>
      <p id="victory-mission" class="victory-mission" hidden></p>
      <p id="victory-stats"></p>
      <div class="result-actions"><button id="finish-game" type="button">Zur Übersicht</button><button id="play-again" class="primary-action" type="button">Nochmal spielen</button></div>
    </section>
    <section id="card-hand" class="card-hand" aria-label="Deine Länderkarten" data-expanded="false">
      <button id="cards-toggle" type="button" aria-label="Karten einklappen" aria-expanded="false" aria-controls="hand-cards" hidden>×</button>
      <div id="hand-cards" class="hand-cards"></div>
      <button id="review-mission" type="button" aria-label="Deine Auftragskarte ansehen" hidden>✦</button>
      <section id="trade-panel" class="trade-panel" aria-label="Kartensatz mit der Bank tauschen" hidden>
        <button id="trade-cards" type="button" class="primary-action" disabled>Drei Karten auswählen</button>
      </section>
      <p id="trade-feedback" role="status" aria-live="polite" hidden></p>
    </section>
    <dialog id="mission-reveal" class="mission-reveal" aria-labelledby="mission-title">
      <span class="mission-seal" aria-hidden="true">✦</span><p class="mission-eyebrow">Nur für dich · streng geheim</p>
      <h2 id="mission-title">Dein Auftrag</h2><p id="mission-text"></p>
      <span class="mission-rule" aria-hidden="true"></span><p class="mission-footnote">Dein Auftrag bleibt am Stern neben deinem Avatar erreichbar.</p>
      <button id="accept-mission" type="button">Auftrag merken</button>
    </dialog>
    <div class="loading" id="loading" role="status"><span></span><p>Dein Tisch wird vorbereitet …</p></div>
    <div class="error" id="error" role="alert" hidden><h1>Die Ansicht konnte nicht geöffnet werden.</h1><p id="error-detail"></p><button type="button" id="reload">Erneut laden</button></div>
`;

export function mountTableSurface() {
  document.querySelector(".prototype").innerHTML = markup;
  return mountConquestButtons();
}
