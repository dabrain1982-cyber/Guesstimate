# Conquest – gemeinsamer 2,5D-Spieltisch

Normaler Einstieg auf diesem PC: [Conquest-Lobby](http://127.0.0.1:8765/karten/welteroberung).
Der Spielstart öffnet dieselbe Tischdarstellung in der normalen Anwendung.
`table-surface.js` enthält genau eine gemeinsame Oberfläche, `remote-turn.js`
verbindet sie mit den serverseitig geprüften und gespeicherten Zugaktionen.
Ein gesonderter Tischserver ist dafür nicht erforderlich.

Seit 25.10.2026: Jede Armee zeigt Truppen und Länder am Avatar; die kleine
Plakette enthält die Kartenanzahl. Die eigene Plakette vergrößert die
Kartenhand am Avatar; ein Klick auf eine große Karte wählt sie aus. Kartenidentitäten und Missionen bleiben privat. Unten steht
die nächste Spielaktion ohne umschließende Box und ohne weiteren Avatar. Im
Angriff stehen Quelle/Ziel und Würfel direkt darüber. Der Verstärkungsvorrat erscheint
nur beim eigenen Verteilen. In schmalen Fenstern stehen die Spieleranzeigen in
zwei Spalten oberhalb der Karte, mit derselben gemeinsamen Porträtkomponente.

Die untere Hauptaktion und „Truppen verteilen“ erproben den gespeicherten
Eintrag **Stormseed´s conquest**: grüne Steinoberfläche, acht Konturpunkte,
Fredoka/geritzt, dezent, 300 ms, leichter Holzanschlag bei 20 %. Der gespeicherte
Stand liegt fest in `button-profile.json`; spätere Werkstattänderungen ändern
ihn nicht automatisch. Der Button wird als Ganzes für den Spieltisch skaliert.
Darstellung und Druckbewegung stammen aus demselben Renderer wie in der
Werkstatt, die Grundgestaltung aus `static/comic-button.css`. Kein Nachbau
seiner Innenkomposition. Auch Kartentausch, Revanche und Missionsbestätigung verwenden diesen Renderer.
Weitere bisherige Spielbuttons sind noch offen.

In gespeicherten App-Partien enthält die Kartenhand die Satzwahl für den
Kartentausch: gemeinsame steigende Werte, zwei Joker, Tauschpflicht und der
automatische Bonus von +2 auf jedes eigene Kartengebiet nach der Projektregel. Die großen drei
Truppensymbole werden von derselben Kartenkomponente in Gewinnanzeige und
Kartenhand dargestellt. Die vollständigen Regeln stehen in `CONQUEST_RULESET.md`
im Projektstamm. Die isolierte Beispielzug-Logik simuliert diesen Bankbetrieb
weiterhin nicht; der geprüfte Kartentausch läuft in der normalen Anwendung.

Die weiterhin mögliche isolierte Vorschau auf Port 54508 nutzt dieselben
Darstellungs- und Bedienkomponenten mit einem ungespeicherten Beispielzug.
Die folgenden Angaben zu Beispielarmeen, sechs festen Verstärkungen und dem
Zurücksetzen beim Neuladen betreffen ausschließlich diesen isolierten Aufruf.

Dieser getrennte Prototyp dient dazu, das Vorbeugen, die Länderbedienung und
den vollständigen Beispielzug mit Verstärken, Angreifen, Festigen und Zugende
am Tisch zu beurteilen.
Er verwendet keine Spielerdatenbank und verändert keine gespeicherte Partie. Im normalen App-Aufruf wird stattdessen die gespeicherte Partie aus der Lobby geladen.

## Karten, Mission und Abschluss

Es gibt keinen Inventar- oder Siegerdialog mehr. Karten kommen als freie kleine Hand direkt aus dem eigenen
Avatar, ohne Inventarfläche oder Textblöcke: erster Klick vergrößert, zweiter Klick
wählt für einen Satz aus. Nach erfolgreicher Abgabe klappt die Hand
automatisch wieder ein; bei einem Fehler bleiben Hand und Auswahl geöffnet.
Besitzkennzeichnung und Pflichttausch bleiben erhalten; jedes eigene Land
im eingetauschten Satz erhält automatisch +2. Nur die Auftragskarte erscheint
zu Spielbeginn bewusst als eigener moderner Dialog. Nach dem Bestätigen bleibt
die Mission am kleinen Stern neben dem eigenen Avatar erneut aufrufbar; ihr
Satz steht im Hinweis des Symbols. Es gibt keinen Text unter der Hand.
Erst ein gültig ausgewählter Kartensatz blendet eine kleine Tauschaktion ein.
Eine Bonusgebietsauswahl gibt es nicht. Auch weitere Kartensätze im selben
Zug erhalten automatisch +2 je eigenem Gebiet.
Die Hand folgt ihrem tatsächlichen Besitzer, auch beim Scrollen und bei
Größenänderungen; schmale Fenster fächern zur freien Bildschirmseite auf.

Das Merken der Anzeige wird je Partie und Spieler lokal gespeichert, ohne
Missionstext. Eine Revanche zeigt den neu gezogenen Auftrag erneut.

Der Endstand ist eine einklappbare Anzeige am Brett mit dem gemeinsamen
Spielerporträt, Sieggrund und Endwerten. Revanche und Verlassen verwenden die
vorhandenen gespeicherten Lobbyaktionen. Neue Sieger-/Verlierergrafiken sind
weiterhin offen. Kartenhand, Ergebnis und Kartenhinweis reagieren beim
Scrollen nicht auf die Kamera.

## Bedienung

Der obere Namens-/Werkzeugstreifen ist entfernt; der Spielname steht auf dem
Brett. Sitzposition, Blickwinkelregler, Überblick und Gradzahl stehen als
kleine gemeinsame Bediengruppe unten rechts. „← Lobby“ bleibt unten links
erreichbar. Auf schmalen Fenstern stehen Spielaktionen über dieser unteren
Bedienzeile. Die bisherige Kamerabewegung (32–82 Grad) bleibt erhalten; die
Bretteinpassung nutzt den freien oberen Rand und hält die untere Bedienung frei.


- Mausrad nach vorn: über den Tisch beugen.
- Mausrad zurück: zurücklehnen.
- Der Schieberegler erlaubt dieselbe Bewegung mit Maus, Touch und Tastatur.
- `Sitzposition` wählt 32 Grad, `Überblick` 82 Grad.
- Es gibt kein freies Verschieben und keinen manuellen Zoom. Die Kamera bewegt
  sich um die unveränderte Tischplatte. Ihr Abstand und die Bildausrichtung
  werden für jeden Winkel passend bestimmt, bei unveränderter Kameralinse.
- Die Sitzposition zeigt die Karte deutlich näher als der erste 2,5D-Entwurf.
  Der Überblick nutzt die Höhe unterhalb der Bedienleiste fast vollständig.
  Die Karte bleibt im Bild; der vordere Holzrahmen darf unten aus dem Bild laufen.
  Damit ersetzt die aktuelle Nutzerentscheidung ausdrücklich die frühere
  Vorgabe, den ganzen Tisch bei jedem Winkel mit einem festen Abstand einzupassen.
- Eine Truppenmarke wählt das Land direkt auf dem Brett, ohne eine zusätzliche
  Länder-Infobox. Namen, Truppen und Armee bleiben als zugängliche Beschriftung
  an den Marken vorhanden. Angriffsziele werden durch Comic-Pfeile angezeigt;
  eigene Nachbarn erhalten im Angriff keine Markierung.
- Das ergänzende Ländermenü mit denselben 42 Ländern erscheint bei Tastaturfokus.
  `Escape`, der Schließen-Knopf oder ein Klick auf die freie Szene
  heben die Auswahl auf. Ziehen verschiebt die Ansicht weiterhin nicht.
- Die drei Armeen und ihre Zahlen sind ausdrücklich eine **Beispielbelegung**
  für die Bedienungsprüfung, keine regelgerechte Startaufstellung. Sie sind
  deterministisch und werden nicht gespeichert. Bestätigte Verstärkungen
  verändern ausschließlich den aktuellen Beispielzug im Arbeitsspeicher.
  Länder werden über ihre Marken oder das Menü ausgewählt; die Landflächen
  besitzen noch keine eigenen flächigen Treffermasken.

## Verstärkungsphase

- Der Beispielzug beginnt als goldene Armee mit **sechs Verstärkungen**. Die
  kurze Meldung `Verstärkung erhalten` führt über `Truppen verteilen` zum Brett.
  Die sechs Truppen sind eine feste Vorgabe für diesen Bedienungsversuch;
  Ländergrundwert, Kontinentbonus und Kartentausch werden hier noch nicht
  als regelgerechter Nachschub berechnet.
- Unten stehen der verfügbare Vorrat und `Weiter zum Angriff`, ohne die frühere
  Holz-/Messingbox und ohne doppelten Avatar. Das Brett wird oberhalb der
  tatsächlich benötigten Bedienfläche eingepasst.
- Eine eigene goldene Marke öffnet die Mengenwahl. Zahleneingabe, Plus/Minus
  und Schieberegler wählen dieselbe Anzahl. Die Vorschau zeigt die bisherige
  Truppenzahl und das Ergebnis der Platzierung. Erst der grüne Setzen-Knopf
  erhöht die Marke und verringert den Vorrat um genau diese Anzahl.
- `Abbrechen` oder `Escape` verwerfen die Mengenwahl vollständig. Fremde
  Länder bleiben zur Information auswählbar, erlauben aber keine Verstärkung.
  Ungültige Zahlen, Teilzahlen und Mengen über dem Vorrat werden abgewiesen.
- Solange auch nur eine Truppe übrig ist, bleibt `Weiter zum Angriff` nativ
  deaktiviert und grau. Erst bei null wird er grün. Sein Klick erreicht die
  Angriffsphase und sperrt weitere Verstärkungen.
- Der kleine Kreis-Pfeil `Offline-Beispiel neu starten` setzt nur diese lokale
  Vorführung einschließlich aller Kartenhände auf ihre ursprüngliche Belegung
  mit sechs Verstärkungen zurück.
  Neu laden beginnt ebenfalls mit dem Ausgangszustand.

## Angriffsphase

- Nach der vollständigen Verstärkung `Weiter zum Angriff` wählen. Ein eigenes
  Land mit mindestens zwei Truppen anklicken: Comic-Pfeile leuchten zu allen
  erreichbaren Feindländern auf. Ein anderes eigenes Land wechselt die Quelle.
  Eigene Nachbarländer bleiben dabei unmarkiert.
- Ein markiertes feindliches Land wählt das Ziel ohne Angriffsdialog. Quelle
  und Ziel erscheinen unten, die Würfelwahl darüber. Alle Pfeile folgen der
  Brettkamera; Alaska–Kamtschatka bleibt in zwei Abschnitte an den Rändern geteilt.
- Ein bis drei Angriffswürfel wählen, soweit die Truppenzahl reicht. Neue
  Quellen/Ziele starten beim zulässigen Maximum. Mausrad zurück über der
  Würfelwahl reduziert, vorwärts erhöht; Klick und Pfeiltasten sowie Pos1/Ende
  sind ebenfalls möglich. Polling erhält die Wahl. Mindestens
  eine Truppe muss im Ausgangsland bleiben. `Angreifen` löst genau
  einen Vergleich aus. Die Vorschau würfelt unverändert zufällig mit der
  Browser-Kryptozufallsquelle, zeigt die absteigend sortierten Werte und zieht
  die angezeigten Verluste unmittelbar von den Marken ab. Das Ergebnis steht
  direkt am Brett. Gleichstand gewinnt
  die Verteidigung. Erneutes Würfeln bleibt eine eigene bewusste Aktion.
- Die Gegner dieser Einzelspieler-Vorführung verteidigen automatisch mit der
  größtmöglichen zulässigen Zahl (ein bis zwei Würfel). Das ist eine lokale
  Bedienungserleichterung; eine menschliche Verteidigungswahl für das spätere
  Mehrspielerspiel wird hier nicht ersetzt oder vorweggenommen.
- Nach der letzten verlorenen Verteidigungstruppe wechselt das Land zu Gold.
  Bis zum verpflichtenden Einrücken ist es vorübergehend unbesetzt; weitere
  Angriffe und der Phasenwechsel sind gesperrt. `Truppen einrücken` öffnet
  denselben Mengenwahldialog wie bei der Verstärkung, als ganze Komponente.
  Mindestens die Zahl der zuletzt benutzten Angriffswürfel muss einrücken;
  mindestens eine Truppe bleibt im Ausgangsland. Diese notwendige Besetzung
  lässt sich nicht mit Escape oder Abbrechen überspringen.
- Nach der Besetzung aktualisieren sich Farbe, Besitzer, Länderzahlen,
  Truppenzahl und gültige Angriffsziele. Auch das neu eroberte Land kann als
  Ausgangsland dienen, sofern es mindestens zwei Truppen und feindliche
  Nachbarn besitzt. Ein erneuter Klick auf das Ziel oder das kleine × hebt die
  Zielwahl auf. Die einzelne Hauptaktion wird dann `Weiter zum Festigen`.
  Dieser bisherige Ablauf wurde ausdrücklich bestätigt; Festigen wird nicht
  automatisch übersprungen. Ausstehende Verteidigung wird bei Neuladen mit
  Ländern und gewählter Würfelzahl wieder aufgenommen; weitere Würfe sind gesperrt.
- Der lokale Neustart stellt auch die ursprünglichen Besitzer wieder her.

## Festigen, Zugende und Kartenhand

- In `Festigen` ein eigenes Land mit mindestens zwei Truppen und anschließend
  ein grün markiertes eigenes Nachbarland auswählen. Nur eine direkte
  Nachbarschaft zählt; es gibt keinen freien Weg über mehrere eigene Länder.
  Der gleiche Mengenwahldialog wie bei Verstärkung und Einrücken wird verwendet.
- Die bestätigte Verschiebung ist einmal pro Zug möglich. Mindestens eine
  Truppe bleibt im Ausgangsland, die Gesamtzahl bleibt unverändert. Abbrechen
  verbraucht die Verschiebung nicht. Über `Zug beenden` darf Festigen auch
  vollständig übersprungen werden.
- Erst `Zug beenden` vergibt bei mindestens einer vollständig besetzten
  Eroberung genau **eine** zufällige Länderkarte. Mehrere Eroberungen erzeugen
  keine zusätzliche Karte; ohne Eroberung gibt es keine. Wiederholte Abschluss-
  aufrufe sind gesperrt. Die gezogene Karte muss keines der eroberten Länder
  darstellen. Der Stapel umfasst die 42 Länder und wird ohne Zurücklegen gezogen.
- Die tatsächlich zugeteilte Karte erscheint zwei Sekunden mittig, fliegt
  danach in 480 ms zum Avatar ihres Empfängers und verschwindet. Die Hand
  enthält sie bereits nach der bestätigten Vergabe. Aktualisierungen und
  Neuladen spielen einen alten Kartenempfang nicht erneut ab. Bei reduzierter
  Bewegung bleibt die zweisekündige Anzeige, der Flug entfällt. Ein Klick
  auf die Karte öffnet die eigene Hand am Avatar. Anzeige und Hand verwenden
  dieselbe vollständige Kartenkomponente mit Ausschnitt der Brettgrafik.
- „Dein Zug!“ zeigt die verteilbaren Armeen zwei Sekunden. Bei Tauschpflicht
  bleibt der Hinweis mit dem Kartenbutton bis zum Öffnen der Hand bestehen.
- `An … übergeben` startet den nächsten Beispielzug in der Reihenfolge
  Gold → Rot → Blau. Armeen ohne Länder werden übersprungen. Brett und
  Kartenhände bleiben erhalten; Eroberungszähler und einmaliges Festigen
  beginnen neu. Jede Armee erhält weiterhin sechs fest vorgegebene
  Beispiel-Verstärkungen, keine neu eingeführte Nachschubregel.
- Alle drei Armeen werden für diesen lokalen Bedienungsversuch manuell auf
  demselben PC gesteuert. Es gibt keine KI oder angemeldeten Mitspieler und
  keine gespeicherte Partie. Karten und Truppen bleiben nur bis zum Neuladen
  beziehungsweise vollständigen lokalen Neustart erhalten.
- Kartentausch, Nachschubberechnung, Sieg-/Missionsprüfung und die Anbindung
  an echte Mehrspielerpartien bleiben offen. Bei leerem Kartenstapel wird ein
  berechtigter Zugabschluss ohne Veränderung abgewiesen, statt den Kartengewinn
  still auszulassen; ein Kartentausch-/Ablagestapel ist noch nicht enthalten.

Kampfregeln anhand des offiziellen klassischen Regelhefts geprüft:
[Hasbro, Seiten 8–10](https://www.hasbro.com/common/instruct/risk.pdf).

## Aufbau und bewusster Umfang

- Räumlicher Tisch mit Holzplatte, Rand, Metallleiste, Unterbau und Beinen.
- Die vorhandene farbige Karte liegt als unveränderte Bildtextur auf dem Tisch.
- Der gesamte Boden verwendet genau eine Teppichtextur auf einer einzigen
  Fläche. Die frühere Mischung aus fotografiertem und ergänztem Teppich entfällt.
- Eine vollständige Panorama-Rückwand und zwei freigestellte Möbelgruppen bilden
  getrennte Kulissenebenen. Die Rückwand wird seitlich gespiegelt fortgesetzt;
  ihre Abschnitte behalten die Proportionen des Bilds. Es gibt keine seitlichen
  Ersatzflächen mit generischer Holzmaserung und keine Projektion des Raumfotos
  über Wand und Boden hinweg.
- Der Raum bleibt eingeblendet. Beim Blick nach unten sieht man entsprechend
  mehr Boden und weniger von der hinteren Wand.
- Die Kulisse ist eine vereinfachte Tiefenbühne, kein vollständig modellierter
  Raum. Die Möbelkarten besitzen weiterhin keine echte räumliche Tiefe und
  können bei starken Winkeln als Bildkulisse erkennbar sein. Der Prototyp enthält
  42 dynamische Truppenmarken: räumliche Metallsockel mit einer gut lesbaren,
  zur Kamera ausgerichteten Zahlenfläche. Beide verwenden dieselben festen
  Brettkoordinaten und dieselbe Kamera wie die Karte. Eigene Figurenmodelle,
  echte Partiedaten, regelgerechte Nachschubberechnung, Kartentausch und
  Spielendprüfung gehören in einen späteren Integrationsschritt. Der vollständige
  Zugablauf ist ausschließlich Teil dieser lokalen Bedienungsvorschau.

## Dateien und Bildbearbeitung

- `table-surface.js`, `style.css`, `scene.js`: gemeinsame Oberfläche und Darstellung.
- `index.html`: Einstieg für den isolierten Beispielzug.
- `remote-turn.js`: Verbindung zur normalen App, Revisionen, Statusabgleich und Zugaktionen.
- `camera.js`: gemeinsame Kamera- und Einpassungsberechnung.
- `camera.test.js`: acht lokale Geometrieprüfungen.
- `territory-model.js`: Bildkoordinaten, Umrechnung auf die unveränderte
  Brettfläche und getrennte Beispielbelegung.
- `territories.js`: eine gemeinsame Markenkomponente, Auswahl und Nachbaranzeige.
- `territories.test.js`: sechs Daten- und Projektionsprüfungen.
- `turn-model.js`: isolierte Beispielzüge mit Verstärkung, Besitzprüfung,
  Würfelvergleich, Eroberung, Einrücken, einmaligem Festigen, einmaliger
  Kartenzuteilung, getrennten Händen und Übergabe an die nächste aktive Armee.
- `turn-controls.js`: gemeinsame Zugleiste, Meldungen, Kartenhand und dieselbe
  Mengenwahl für Verstärkung, Einrücken und Festigen.
- `attack.js`: Auswahl von Ausgangsland/Ziel und Angriffsdialog.
- `fortify.js`: Auswahl eigener Nachbarn für die einmalige Verschiebung.
- `cards.js`: dieselbe Länderkarte für Gewinnanzeige und Kartenhand.
- `turn-end.test.js`: zehn zusätzliche Prüfungen von Festigen, Kartenvergabe,
  wiederholten Abschlussaktionen, Kartenstapel und Zugübergabe.
- `attack.test.js`: neun Prüfungen der Angriffe einschließlich aller 36
  Einer-Würfelvergleiche, Gleichstand, Besitzwechsel und Besetzungsgrenzen.
- `reinforcement.test.js`: sieben Prüfungen der Platzierungsgrenzen,
  Truppenerhaltung, Phasensperre und freien Sicht oberhalb der Zugleiste.
- `assets/world.json`: unveränderte lokale Kopie von
  `static/conquest/world.json` mit 42 Gebieten, Namen, Kontinenten und
  Nachbarschaften. Der Test vergleicht den Snapshot mit der Projektdatei.
  Die bestehenden Bildpositionen stammen aus `static/conquest-table.js`.
  Bei späterer App-Integration diese Daten aus der gemeinsamen Quelle laden;
  dieser Prototyp führt keine zweite Spielregelimplementierung ein.
- `assets/karte.png`: bytegleiche Kopie von
  `static/conquest/boards/welt-conquest-farbkarte-v2.png`.
  SHA256: `7d239294d81561a8d66f6a703995f48704fdfe73340989520fd53bfb181cea23`.
- `assets/raum-ohne-tisch.png`: erhaltene erste Bearbeitung des ursprünglichen
  `static/card-tables-background-v1.png` bearbeitete Kulisse; der dort fest
  gemalte Spieltisch wurde entfernt und der Boden ergänzt. Dieses Gesamtbild
  wird im korrigierten Entwurf nicht mehr auf die Kulisse projiziert.
- `assets/teppich.png`: orthografische Teppichtextur für den gesamten Boden.
- `assets/raum-wand-v2.png`: vollständige Panorama-Rückwand, ohne Boden und Möbel.
- `assets/moebel-v2.png`: zwei Möbelgruppen auf echtem transparentem Hintergrund;
  ihre beiden Bildhälften werden als getrennte Karten dargestellt.
- Die Kulissenbilder wurden mit dem **eingebauten image_gen-Werkzeug** erstellt
  beziehungsweise anhand der vorhandenen Kulisse bearbeitet. Die vollständigen
  ursprünglichen Aufträge stehen in [bearbeitungsauftrag.txt](bearbeitungsauftrag.txt),
  die beiden Korrekturaufträge mit Eingabebildern, Ausgabeorten und Transparenzmodus
  in [bearbeitungsauftrag-v2.txt](bearbeitungsauftrag-v2.txt). Originalbilder und
  ursprüngliche Generatorausgaben bleiben erhalten.
- `assets/manifest.json` dokumentiert Bildmaße und Prüfsummen.

Die Holztextur des räumlichen Tischs wird reproduzierbar direkt im Browser
erzeugt. Sie ist keine Verformung des Raumfotos.

## Lokaler Betrieb und Abhängigkeiten

Die Tischdateien liegen in diesem Ordner. Der gemeinsame Porträtbaustein und
die lokalen Schriften kommen aus `static/`. Der kleine Vorschaustarter liefert
neben dem Tisch ausschließlich diese freigegebenen gemeinsamen Dateien aus;
er öffnet keine Datenbank. Es gibt keine CDN-, Konten- oder externen Verbindungen.

Die Vorschau wird ausschließlich an `127.0.0.1` gebunden, beispielsweise mit:

```powershell
python deploy/preview_conquest.py --port 54508
```

Die Grafikbibliothek ist unverändert lokal beigelegt:
[Three.js 0.180.0, Tag r180](https://github.com/mrdoob/three.js/tree/r180).
Die MIT-Lizenz liegt unter `vendor/three/LICENSE`. Verwendet werden ausschließlich
`three.module.js` und `three.core.js`, ohne zusätzliche Pakete oder Installation.

## Prüfungen

```powershell
node --test offline-preview/conquest-2-5d-v1/*.test.js
node --check offline-preview/conquest-2-5d-v1/scene.js
node --check offline-preview/conquest-2-5d-v1/territories.js
node --check offline-preview/conquest-2-5d-v1/turn-controls.js
node --check offline-preview/conquest-2-5d-v1/attack.js
```

Die Geometrieprüfungen prüfen alle Viertelgrad-Schritte von 32 bis 82 Grad bei
sechs Fensterformaten: Die Karte muss im sichtbaren Bereich liegen und die
verfügbare Größe ausnutzen. Kameralinse und Zielpunkt bleiben unverändert,
die Kamerabewegung muss kontinuierlich sein. Zwei zusätzliche Prüfungen sichern
den nahen Sitzabstand mit seitlich sichtbarem Holzrahmen sowie den unten
angeschnittenen vorderen Rahmen im Überblick ab.

Die zusätzlichen Prüfungen sichern die 42 Kennungen und den unveränderten
Nachbarschaftsgraphen, die Bildausrichtung, die getrennte Beispielbelegung
und die Rückprojektion aller Marken bei 26 Winkeln in drei Fensterformaten.

Die Browserprüfung und die tatsächlichen Prüfbilder werden im Projektlog
dokumentiert. Ein bestandener Geometrietest allein ist keine visuelle Abnahme.
