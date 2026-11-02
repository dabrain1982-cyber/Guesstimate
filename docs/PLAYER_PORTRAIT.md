# Kompakte Spieleranzeige

`spieler.portraet` verwendet genau eine Grundimplementierung:
[player-portrait.js](../static/player-portrait.js) baut die Anzeige,
[player-portrait.css](../static/player-portrait.css) legt ihre gesamte
Innenkomposition fest. Conquest ist der erste angeschlossene Einsatzort.
Die ältere Ranglisten-/Pultdarstellung wird dafür nicht kopiert.

## Profilquelle und Sichtbarkeit

[player_portrait.py](../player_portrait.py) registriert die bestehenden
Avatar-Kataloge aus `app.py`. Die Daten kommen aus der aktuellen Profilausrüstung,
auch für einen reservierten Platz. Keine Avatar-ID oder Grafik wird in einen
Spielzustand kopiert. Fremde Startavatare verwenden weiterhin
`starter-neutral-public.svg`; der eigene Startavatar bleibt die eigene Variante.
Unbekannte IDs fallen mit denselben Sichtbarkeitsregeln auf den Standard zurück.

Die vorhandenen 1400×1400-Bühnenbilder sind einheitlich ausgerichtet und beginnen
bei y=400. Der gemeinsame Ausschnitt verwendet Maßstab 1,7 und Oberkante −48 %;
der Standardavatar verwendet das vollständige SVG. Alle 19 vorhandenen Motive
bleiben unverändert. Ausschnittsdaten gehören zentral zur Avatarzuordnung.

Virtuelle Testarmeen und neutrale Armeen haben kein Benutzerprofil. Sie erhalten
keinen erfundenen Avatar; die gemeinsame Komponente zeigt eine farbige
Buchstabenmarke und die Anzeige kennzeichnet eine Testarmee ausdrücklich.

## Verwendung und Aktualisierung

```js
const view = createPlayerPortrait(container);
view.update({
  name: 'Spielername',
  portrait: publicPortrait, // avatar_id, url, alt, crop
  color: armyColor,
  kind: 'player',
  status: 'Am Zug · Gold · Verstärken',
  metrics: '14 Länder · 40 Truppen',
  metricsDescription: 'Länder in Besitz und bereits platzierte Truppen.',
});
```

Namen werden als Text eingefügt; lange Namen erhalten eine Ellipse und bleiben
vollständig als Text und im Titel verfügbar. Bilder haben Alternativtexte;
Ladefehler fallen auf die Buchstabenmarke zurück. Die Anzeige selbst ist kein Knopf;
eine eigene Kartenplakette kann das private Inventar öffnen.
Die Gesamtgröße kann über `--player-portrait-size` proportional geändert werden.
Spiele dürfen die innere Anordnung und die Bildausschnitte nicht überschreiben.

Bei Conquest kommen nur freigegebene Profildaten in `game.armies`. Länderzahl
und Truppensumme beziehen sich auf die besetzten Länder des angezeigten Spielers.
Auf Nutzerpräzisierung vom 25.10.2026 verwendet Conquest `layout: 'army'` für
jede Armee: `stats: {troops, countries}` neben dem Avatar und `cardCount` als
kleine Plakette. `current` hebt die aktive Armee hervor; `onCards` öffnet nur
das eigene Inventar. Der Status kennzeichnet eigene, aktive und virtuelle Armeen.
Die Gesamtzahlen stammen aus der Partie. Die Anzahl fremder Karten ist jetzt
öffentlich; Kartenidentitäten und Missionen bleiben privat. Die Komponente
erzeugt genau eine gemeinsame Innenkomposition. Das Spiel ordnet nur die ganzen
Anzeigen an: links untereinander, auf schmalen Fenstern in zwei Spalten.

Diese neue Nutzerentscheidung ersetzt die frühere Beschränkung auf das aktive
Porträt in der Zugleiste. Nach der weiteren Präzisierung stehen unten nur die
Spielaktionen und im Angriff die gewählten Länder/Würfel; dort gibt es keinen
zusätzlichen Avatar und keine umschließende Box. Verfügbare Verstärkungen
erscheinen ausschließlich während der eigenen Verteilung. Die veraltete
Avataransicht der unteren Leiste wurde entfernt. Die Armeeanzeigen verwenden
weiterhin denselben gemeinsamen Porträtcode.

Profiländerungen lösen auch bei unveränderter Spielrevision eine Aktualisierung
aus. Eine ältere Statusantwort ersetzt keinen neueren Zustand. Die tatsächliche
Höhe der Zugleiste wird für Kamera und untere Informationsflächen berücksichtigt.
In schmalen Fenstern beginnt die Karte unter dem gemessenen Spielerbereich.

Die isolierte Conquest-Vorschau exportiert dieselbe Komponente über einen
einzeiligen Verweis. Die authentifizierte App liefert dieselbe Quelldatei aus
`static/`; es gibt keine zweite innere Darstellung.

## Gestaltungsstatus

Der Porträtbaustein ist eine lokale Umsetzung mit vorhandenen Avatarbildern.
Er erklärt die übrigen Conquest-Dialoge und Buttons nicht zu fertigen
Comic-Elementen. Für deren Überarbeitung und das eigenständige Party-Treppchen
gilt der [Gestaltungsplan](GESTALTUNGSPLAN.md).
