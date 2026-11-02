# Vorhandene Bildmotive, Flyer und Symbolsätze

Stand: 27.10.2026, ausschließlich lokale Werkstatt. Acht Spielbereiche geprüft:
Guesstimate, Guesstimate Party, Perfect, Playtable, Würfeltisch, Kniffel, Mäxchen
und Conquest. Vorhandene Spiele und persönliche Entwürfe bleiben unverändert;
Editoroptionen folgen später.

## Zuordnung

| Bereich | Gemeinsame Bausteine | Feste Konfigurationen |
|---|---|---|
| Titelbilder / Bildmotive | Spielmotiv und vorhandenes Mäxchen-Logo | Acht ursprüngliche Spiel-/Gruppenmotive und ein SVG-Logo |
| Flyer | Startseiten-Flyer, allgemeine Spielkachel, Perfect-Kachel | Vier Startseiten-Flyer, sechs Spielkacheln und drei Gruppenkacheln |
| Icons | Quiz-Fragetypen, Navigation, Comic-Aktionen, Conquest-Ausstattung, Spielerstatistik und App-Symbol | Fünf vollständige Symbolsätze (5/4/15/3/2 Motive) und das bestehende App-Symbol |

Das sind **28 feste Konfigurationen in elf gemeinsamen Modellen**. Bilder,
Beschriftung, Größe und Symbolauswahl sind Eigenschaften. Ein wiederholter Einsatz
desselben Bildes erzeugt kein neues Bildmotiv: Würfeltisch und Mäxchen teilen etwa
dasselbe Würfelmotiv. Ihre vorhandenen Kachelbeschriftungen bleiben auswählbare
Varianten der gemeinsamen Komposition.

Ein Symbolsatz wird als Ganzes gesammelt. Die Auswahl „Symbol im Satz“ wechselt
ausschließlich die Vorschau. Es gibt keine zusätzlichen Einträge je Symbolnutzung,
Frage, Spieler oder Partie. Die 15 Comic-Zeichen sind die endlichen verfügbaren
Motive der bestehenden gemeinsamen Fabrik; damit wird nicht behauptet, dass jedes
davon aktuell an einer aktiven Aktion vorkommt.

## Originalquellen

Die Bildmotive liegen unverändert unter `static/carousel-*.png`,
`static/tabletop-*-tile-v1.png` und `static/maexchen-logo-v1.svg`.
Die vier allgemeinen Startseiten-Flyer werden unmittelbar aus ihren ursprünglichen
Artikeln in `templates/home.html` gelesen. Spiel- und Gruppenkacheln nutzen
`templates/tabletop_family.html`, `templates/tabletop_connection.html` und die
gemeinsamen Makros in `templates/_game_flyers.html`. Originalbilder, Schriftregeln,
Beschriftungen, Überlagerungen und Komposition bleiben erhalten. Bilddatei und
zusammengesetzter Flyer sind getrennt verwendbar.

Die Quizzeichen verwenden das ursprüngliche `_icons.html`-Makro und denselben
Fünfer-Sprite. Navigationszeichen kommen aus den bestehenden SVGs in `base.html`.
Comic-Zeichen importieren `comic-ui-v1/components.js/icon` unmittelbar.
Conquests Ausstattungszeichen verwenden die originale `symbolImage`-Fabrik aus
`cards.js`; keine neuen Infanterie-, Reiter- oder Geschützmodelle. Die beiden
Statistikzeichen werden von `static/player-portrait.js/createPlayerPortrait`
erzeugt. Das App-Symbol bleibt die ursprüngliche `favicon.svg`.

`graphic_library.py` registriert Quellen und Prüfsummen; `graphic-stage.js`
passt ausschließlich die ganze Vorschau proportional an den verfügbaren Platz an.
Keine Bildbearbeitung oder Bildkopie ist zur Aufnahme nötig. Vorschauen haben keine
Spielhandler, aktive Links, Statusabfragen, Datenbanken oder echten Spielerdaten.
Der bestehende eigene Bildimport und persönliche Bildentwürfe bleiben verfügbar.

## Abgrenzung

- Die persönliche Geburtstagsfolie bleibt außerhalb des allgemeinen Katalogs.
- Die angekündigte Schweinchen-Kachel ist kein vorhandenes aktives Spiel.
- Reine Texttitel bleiben Teil ihrer bestehenden Fenster-/Titel-/Flyerkomposition;
  daraus werden keine zusätzlichen Bitmapdateien erzeugt.
- Kartenbilder, Würfelseiten, Spielerporträts und dynamische Routen bleiben bei
  ihren vorhandenen Bausteinen. Nicht verwendete ältere Entwurfsbilder werden
  nicht automatisch als aktuelle Spielmotive aufgenommen.
- Neue Klang-/Schriftrecherche, Materialaufbereitung und Editorprüfung bleiben offen.

Reproduzierbarer Bericht: `python deploy/audit_graphic_library.py`,
[BILDBAUSTEINE_BESTAND.json](BILDBAUSTEINE_BESTAND.json).
Prüfungen und Schutzvergleich: `runtime/graphics-library-20261027/`.

Abschlussprüfung: zwölf gezielte Grafik-/Projektmappenprüfungen bestanden
(74,532 Sekunden); nach Korrektur eines lokalen Modulpfades alle vier Grafiktests
erneut bestanden (20,802 Sekunden). Alle 28 Konfigurationen im Browser geladen,
Symbolauswahl innerhalb des Satzes gewechselt. Prüfmappe mit drei Elementen
(Bildmotiv, Flyer, vollständiger Fünfer-Symbolsatz) gespeichert, nach Neuladen
wieder geöffnet und lokal übergeben. Persönliche Werkstatt auf Port 8776 mit
derselben Ablage sichtbar geprüft. 480 geschützte Dateien und sämtliche sieben
persönlichen JSON-Dateien unverändert; keine zusätzlichen persönlichen JSON-Dateien.
