# Stormseed’s Conquest – verbindlicher Regelunterbau

Der Spielablauf wird als eigener serverseitiger Zustandsautomat umgesetzt. Die
Grafik- und Physikwerkzeuge stellen Brett, Karten, Figuren und Würfel dar; sie
entscheiden niemals selbst über einen gültigen Spielzug.

## Start

- 2–6 Personen; bei zwei Personen kommt eine neutrale Armee hinzu.
- Alle 42 Gebiete sind zu Beginn besetzt.
- Starttruppen: 2 Personen 40, 3 Personen 35, 4 Personen 30, 5 Personen 25,
  6 Personen 20.
- Bei neuen Partien werden zunächst nur die Länder automatisch zugeteilt,
  mit genau einer Einheit auf jedem Land. Die restlichen Starttruppen setzen
  die Spieler selbst reihum, jeweils eine Einheit auf ein eigenes Land.
  Kein eigener Vorrat darf überschritten und keine fremde Armee verstärkt
  werden. Wer keine Starttruppen mehr hat, wird bei der Aufstellung übersprungen.
- Während der Startaufstellung setzt ein Klick auf ein zulässiges Land
  unmittelbar eine Einheit, ohne Bestätigungsfenster. Bis zum Speichern ist
  keine weitere Platzierung möglich. Danach folgt automatisch die nächste
  Armee beziehungsweise der nächste Schritt der Zweieraufstellung.
- Die Zweier-Sonderregel der klassischen Anleitung gilt: nacheinander zwei
  einzelne eigene Einheiten setzen, danach eine neutrale Einheit auf ein
  beliebiges neutrales Land. Anschließend folgt der Gegner. Auch die neutrale
  Armee hat insgesamt 40 Starttruppen.
- Ein Würfelentscheid bestimmt die erste Person.
- Die Sitzreihenfolge entspricht den Lobbybeitritten. Nach vollständiger
  Aufstellung beginnt die ermittelte erste Person ihren regulären ersten Zug
  mit Grundverstärkung und möglichen Kontinentboni. Während der Aufstellung
  sind Angriffe, Kartentausch, Festigen und Zugwechselknöpfe gesperrt.
- Bereits laufende ältere Partien behalten ihre fertige Aufstellung und
  aktuelle Zugphase. Sie werden durch diese Änderung nicht neu aufgebaut.
- Bei „Geheime Missionen“ erhält jede Person genau eine private Mission.
- Missionen gegen eine nicht mitspielende Armeefarbe werden vor der Vergabe
  entfernt. Die im Projekt verfügbare Zweier-Missionsvariante ist eine
  Projektvariante; das klassische Hasbro-Regelheft sieht geheime Missionen
  für drei bis sechs Personen vor.

## Zugphasen und notwendige Anzeige

1. **Verstärken**: verfügbare Truppen, Gebietsgrundwert, Kontinentbonus,
   mögliche Kartensätze und auswählbare eigene Zielgebiete. Menge direkt am
   Brett wählen und bestätigen; kein separates Verstärkungsfenster. Nach der
   letzten Platzierung geht es ohne zusätzlichen Knopf zum Angriff weiter,
   sofern keine zulässige oder verpflichtende Tauschentscheidung offen ist.
2. **Angreifen**: eigenes Startgebiet, benachbartes feindliches Ziel,
   1–3 Angriffswürfel, automatische Verteidigung mit einem Würfel bei genau
   einer Einheit und zwingend zwei Würfeln ab zwei Einheiten, Verluste und bei Eroberung die
   Anzahl der einrückenden Truppen. Angriff kann übersprungen oder wiederholt
   werden. Auch das verpflichtende Einrücken wird direkt am Brett innerhalb
   der zulässigen Grenzen gewählt und bestätigt, ohne separates Fenster.
3. **Festigen**: einmalig Truppen von einem eigenen Gebiet in ein benachbartes
   eigenes Gebiet verschieben; mindestens eine Truppe bleibt zurück. Die Phase
   darf übersprungen werden.
4. **Zugende**: genau eine Länderkarte, falls in diesem Zug mindestens ein
   Gebiet erobert wurde. Einmal „Zug beenden“ vergibt gegebenenfalls die Karte
   und wechselt direkt zur nächsten noch aktiven Person in der festen
   Reihenfolge der Lobbybeitritte. Keine zusätzliche Bestätigung oder Fenster.
   Die erhaltene Karte erscheint zwei Sekunden in der Bildschirmmitte und
   fliegt dann zum Avatar ihres Empfängers. Danach ist das Brett wieder frei;
   Aktualisierungen und Neuladen wiederholen den alten Kartenempfang nicht.
   Bei reduzierter Bewegung entfällt der Flug. Die Vergabe ist bereits vor
   dieser reinen Anzeige gespeichert und bleibt nach Neuladen erhalten.
   Die erhaltene Karte bleibt in der eigenen Kartenhand; dies ist kein Kartentausch.

Die feste maximale Verteidigungszahl ist die ausdrücklich gewünschte
Conquest-Projektregel vom 25.10.2026. Die als Quelle genannte klassische
Hasbro-Anleitung erlaubt dem Verteidiger dagegen die Wahl zwischen einem und
zwei Würfeln, sofern ausreichend Einheiten vorhanden sind. Solange keine
manuellen Würfel implementiert sind, berechnet der Server beide Seiten mit
einem einzigen Angriff. Es gibt weder ein Verteidigungsfenster noch einen
Verteidigungs- oder Würfelknopf. Das Ergebnis erscheint direkt am Brett.

Zu Beginn der eigenen Verstärkungsphase zeigt „Dein Zug!“ die verfügbaren
Armeen und verschwindet nach zwei Sekunden. Bei Tauschpflicht bleibt der
Hinweis mit „Zu den Karten“ stehen, bis diese erfüllt ist. Er ist kein
blockierender Dialog und verändert keine Truppenzahl.

## Tisch, Länderkarten und Missionen

- Die lokale Vorschau verwendet die vom Nutzer freigegebene farbige Fassung
  `welt-conquest-farbkarte-v2.png` mit ihrem eingebauten Titel und ihrer
  Kontinentlegende. Die Truppenmarken sind an dieser Grafik ausgerichtet;
  die bestehende interne Gebiets-ID `russland` für Ukraine bleibt erhalten.
- Die Karte liegt als unveränderte flache Oberfläche in der Kupfereinfassung
  eines räumlichen Tischs. Die vom Nutzer beauftragte 2,5D-Ansicht ersetzt die
  ältere Verformung der vollständigen Fotokulisse. Es gibt kein zweites
  aufgelegtes Brett und keine frei ziehbaren Karten- oder Würfelstapel.
- Das Mausrad verändert ausschließlich den Blickwinkel stufenlos zwischen
  Sitzposition und Überblick (32 bis 82 Grad). Die Kamera bewegt sich um den
  unveränderten Tisch; Karte und Marken verwenden dieselbe Kamera. Die Karte
  bleibt automatisch eingepasst. Die nähere Sitzposition nutzt nahezu die
  gesamte Breite und richtet die vordere Kartenkante am unteren Bedienrand
  aus. Der Überblick verteilt übrigen Freiraum gleichmäßig oben und unten.
  Äußerer Holzrand darf dabei aus dem Bild laufen; die vollständige Karte
  bleibt sichtbar. Freies Verschieben und manueller Zoom
  entfallen. Die Raumkulisse bleibt vollständig eingeblendet.
- Der Titel lautet `stormseed´s conquest`. Die Kontinentboni sind Nordamerika
  +5, Südamerika +2, Europa +5, Afrika +3, Asien +7 und Australien +2.
- Die Startverteilung der Gebiete erzeugt keine bleibenden Länderkarten in der
  Kartenhand. Karten zur Startverteilung werden nach dem Platzieren wieder
  eingesammelt; die digitale automatische Verteilung benötigt sie nicht.
- Pro abgeschlossenem Eroberungszug gibt es genau eine Länderkarte, auch nach
  mehreren Eroberungen. Die Karte muss nicht das gerade eroberte Land zeigen.
- Eigene Länderkarten und gegebenenfalls die eigene geheime Mission erscheinen
  ausschließlich als freie Kartenhand am Avatar ihres Besitzers. Ein Klick auf die kleinen
  Karten vergrößert die Hand; ein Klick auf eine große Karte wählt sie aus
  (höchstens drei). Es gibt kein separates Inventarfenster. Die gezogene
  Mission wird zu Spielbeginn als Auftragskarte vorgestellt; der Satz bleibt
  im Hinweis des kleinen Sterns am Avatar; die Karte ist dort erneut aufrufbar.
  Unter den Karten gibt es keine Regeltexte oder Inventarfläche. Nur ein
  gültiger Satz blendet die kleine Tauschaktion ein. Der Tisch bietet keine freie
  Karten-Ziehfunktion. Im Modus Welteroberung gibt es keine Missionskarte.
- Die Kampfauflösung benötigt weiterhin die regelgemäßen Zufallsergebnisse;
  aus dem Wegfall des sichtbaren Würfelbereichs folgt keine neue Kampfregel.

## Kartentausch

- Verbindliche Grundlage ist das offizielle klassische Regelheft für zwei bis
  sechs Personen, Seiten 7–10. Die steigenden Tauschwerte stimmen mit der
  deutschen Hasbro-Fassung B7404, Seiten 10–11, überein.
- Der Stapel enthält 42 Gebietskarten mit dauerhaft zugeordnetem Infanterie-,
  Reiter- oder Geschützsymbol sowie zwei unterschiedliche Joker. Die
  Zuordnung steht ausdrücklich in `static/conquest/world.json` unter
  `cardSymbols`; bestehende Karten behalten ihr bisheriges Symbol.
- Ein Satz umfasst drei gleiche oder drei unterschiedliche Symbole; Joker
  ersetzen beliebige Symbole. Nur drei unterschiedliche eigene Karten dürfen
  abgegeben werden. Die Bank nimmt sie auf den Ablagestapel.
- Der Tauschwert steigt gemeinsam für alle Spieler: 4, 6, 8, 10, 12, 15,
  danach jeweils fünf mehr (20, 25 usw.). Die Symbolart verändert den Wert
  nicht. Die Einheiten ergänzen den noch zu platzierenden Vorrat.
- Normal getauscht wird am Anfang des eigenen Zugs vor dem ersten Platzieren.
  Bei mindestens fünf Karten ist ein Satz verpflichtend, bevor Truppen
  platziert oder die Phase gewechselt werden dürfen. Ein weiterer gültiger
  Satz darf vor dem Platzieren freiwillig abgegeben werden.
- Ein Tausch wird nur angeboten, wenn die Hand tatsächlich einen gültigen
  Satz enthält. Nach dem ersten Platzieren ist das normale Tauschfenster
  geschlossen, auch wenn noch ein Satz in der Hand liegt. Der automatische
  Phasenwechsel nach dem letzten Setzen öffnet keine zusätzliche Tauschzeit.
- Jede Karte zeigt den aktuellen Gebietsbesitzer. Eigene Gebiete sind mit
  „Dein Gebiet“ und dem möglichen +2-Gebietsbonus gekennzeichnet; Joker haben
  keinen eigenen Gebietsbonus. Die Markierung wird aus dem aktuellen Brett
  und dem tatsächlich betrachtenden Spieler abgeleitet, auch nach Eroberungen.
- Projektregel auf ausdrücklichen Nutzerwunsch vom 26.10.2026: Jedes eigene
  besetzte Gebiet, das auf einer der drei eingetauschten Karten steht, erhält
  automatisch zwei Einheiten direkt auf dem Brett. Zwei passende eigene Karten
  ergeben +2 auf beide Länder, drei passende +2 auf alle drei Länder. Keine
  Gebietsauswahl und keine einmalige Begrenzung pro Zug; weitere gültige Sätze
  erhalten den Bonus ebenso. Fremde Länder und Joker erhalten keinen Bonus.
  Die regulären Tauscheinheiten kommen zusätzlich unverändert in den Vorrat.
  Dies ersetzt die frühere Regel mit insgesamt +2 auf nur einem gewählten Land.
- Nach der Pflichtbesetzung des letzten Gebiets eines Gegners gehen dessen
  Handkarten an den Angreifer. Entstehen dadurch mindestens sechs Karten,
  wird der Angriff unterbrochen: Sätze tauschen, bis höchstens vier Karten
  übrig sind, die zusätzlichen Einheiten platzieren, dann weiter angreifen.
  Bei weniger als sechs Karten muss der Tausch bis zum nächsten eigenen Zug
  warten. Der gemeinsame Tauschzähler und die automatischen +2 je eigenem Gebiet gelten
  auch in diesem Sonderfall unverändert.
- Ist der Zugstapel leer, werden die abgegebenen Karten neu gemischt und
  wieder als Zugstapel verwendet. Hände und private Missionskarten bleiben
  ausschließlich für ihre Besitzer sichtbar.

## Sieg und geheime Missionen

- Grundlage: klassisches Hasbro-Regelheft, Seiten 10, 12 und 13–14, sowie
  deutsche Fassung B7404, Seiten 10–13. Keine Wartepflicht bis zum nächsten
  eigenen Zug: Auch wenn ein anderer Spieler die letzte Einheit einer
  gesuchten Farbe entfernt, erfüllt dies die entsprechende Mission sofort.
- Welteroberung mit drei bis sechs Personen endet mit der Besetzung aller
  42 Länder. Im Zweierspiel genügt das Besiegen des Gegners; neutrale Gebiete
  müssen nicht vollständig erobert werden.
- Die vorhandenen Missionskarten und bereits ausgelosten Aufgaben bleiben
  unverändert. Kontinentaufgaben verlangen jedes Gebiet der genannten
  Kontinente, die 24-Länder-Aufgabe mindestens 24 eigene Gebiete. Bei der
  18-Länder-Aufgabe müssen mindestens 18 eigene Gebiete gleichzeitig jeweils
  mindestens zwei Einheiten besitzen; weitere eigene Gebiete dürfen einfacher
  besetzt bleiben.
- Farbmissionen beziehen sich dauerhaft auf die ursprüngliche Sitzfarbe.
  Ist die gesuchte Farbe die eigene, gilt stattdessen das auf der Karte
  angegebene Ziel von 24 Ländern. Eine nicht vertretene Farbe löst keinen
  automatischen Sieg aus. Ausgeschiedene Spieler können nicht mehr gewinnen.
- Nach jeder gültigen Aktion wird geprüft, auch nach Verstärkung,
  Kartenbonus und Festigen. Bei einer Eroberung muss zunächst die notwendige
  Besetzung abgeschlossen sein. Werden durch dieselbe Aktion mehrere
  Missionen erfüllt, wird zuerst der aktive Spieler geprüft, dann die
  weiteren Spieler in der festen Sitzreihenfolge.
- Gewinner, Sieggrund, aufgedeckte Gewinnmission und Endzeit werden zusammen
  mit der letzten Aktion gespeichert. Danach sind weitere Spielaktionen
  gesperrt. Alle Beteiligten sehen dieselbe Gewinneranzeige; andere private
  Missionen und Hände bleiben geschützt. Der Tisch und das Ergebnis lassen
  sich nach Neuladen und aus der Feldzugübersicht erneut ansehen.

## Implementierungsstand dieses Schritts

Die normale Lobby öffnet bei Spielstart die räumliche Tischoberfläche.
Automatische Länderzuteilung, manuelle Startaufstellung, Grundverstärkung (mindestens drei, sonst
Gebiete geteilt durch drei abgerundet) und vollständige Kontinentboni,
Verstärken, Angreifen, Pflichtbesetzung, einmaliges benachbartes Festigen,
Zugende, genau eine Karte bei Eroberung und Zugübergabe werden serverseitig
geprüft und gespeichert. Revisionen verhindern doppelte oder veraltete Aktionen.
Im normalen Mehrspielerspiel würfelt der Server beim Angriff sofort für beide
Seiten. Jede Armee einschließlich Neutral verteidigt mit der festgelegten
maximal zulässigen Zahl. Der Client kann diese Zahl nicht reduzieren.
Private Hände und Missionen werden ausschließlich an ihren Besitzer übertragen.
Ein noch gespeicherter offener Angriff aus der früheren Verteidigerwahl wird
beim Wiederöffnen durch den Verteidiger automatisch ohne Fenster mit der
festen maximalen Zahl aufgelöst. Entsteht danach eine Pflichtbesetzung, öffnet
sie sich auch ohne ein noch geöffnetes Angriffsfenster automatisch; ein
offenes Kampfergebnis behält weiterhin seinen Einrückknopf.

Nur der lokale Besitzer mit aktivem Entwicklermodus kann aus einer
Einpersonen-Lobby einen gekennzeichneten Entwicklertest mit zwei virtuellen
Testarmeen starten. Er steuert die Armeen abwechselnd; die Verteidigung
verwendet in diesem Test die maximal mögliche Würfelzahl. Keine zusätzlichen
Benutzerkonten oder Ranglistenpunkte entstehen. Dieser Test beginnt bewusst
mit dem Besitzer und ist kein regulärer Mehrspieler-Würfelentscheid.

Automatische Sieg-/Missionsprüfung und gespeicherte Gewinneranzeige sind
vorhanden. Die klassische Gebietswahl ist weiterhin offen. Die normale
PC-Anwendung verwendet diese Regeln; die getrennte reine Beispielvorschau
ohne Lobby bleibt ein Übungsablauf ohne geheime Missionen.

## Lobby, Rückkehr und nächste Partie

- Guesstimate → Tabletop Connection → Conquest öffnet die Feldzugübersicht.
  Offene Lobbys lassen sich betreten; eine gestartete Partie nimmt ausschließlich
  ihre ursprünglichen Teilnehmer wieder auf. Die Lobby bleibt auch während der
  Partie über „← Lobby“ erreichbar.
- Ausdrückliches Verlassen verändert weder gespeicherte Länder und Einheiten
  noch Karten, Missionen, ursprüngliche Sitzfarbe oder Zugreihenfolge. Die
  Mitgliedschaft wird als abwesend markiert. Bei Rückkehr wird dieselbe
  Mitgliedsnummer wieder aktiviert; der laufende Spielzustand bleibt erhalten.
- Fehlt der aktive Spieler, wartet das Spiel auf seine Rückkehr. Neue Angriffe
  benötigen keine Antwort des automatisch verteidigenden Spielers. Bei noch
  gespeicherten offenen Angriffen aus der früheren Verteidigerwahl bleibt die
  Wiederaufnahme durch den ursprünglichen Verteidiger möglich. Es gibt keine automatische Neutralisierung,
  Zugüberspringung oder Stellvertretung durch den Host.
- Verlässt der Host die Lobby, übernimmt der nächste noch anwesende Spieler in
  Sitzreihenfolge. Ein zurückkehrender ehemaliger Host erhält seine Armee,
  übernimmt aber nicht automatisch wieder die Hostrolle.
- Der Host kann die gesamte Lobby schließen. Auch wenn die letzte Person
  ausdrücklich verlässt, wird die Lobby geschlossen; danach ist keine
  Wiederaufnahme dieser Lobby möglich. Der letzte Zustand wird nicht gelöscht.
- Nach einem Sieg kann ausschließlich der Host „Nochmal spielen“ wählen.
  Der abgeschlossene Zustand wird einmalig in `conquest_game_history`
  aufbewahrt, dieselbe Lobby mit denselben anwesenden Mitgliedern öffnet sich
  zur Vorbereitung der nächsten Partie. Der anschließende Start erzeugt eine
  neue Startaufstellung. Abwesende Spieler werden nicht automatisch angemeldet.
  „Zur Übersicht“ verlässt die Lobby für die jeweilige Person.
- Spieltische beobachten auch nach dem Sieg weiter den Lobbyzustand, damit
  alle die gemeinsame Rückkehr in die Lobby oder deren Schließen sehen.

## Technikentscheidung

`boardgame.io` ist ein MIT-lizenziertes Gerüst für Lobby, Mehrspielerzustand,
Züge und Phasen, enthält aber kein fertiges Regelwerk für dieses Spiel. Das
Projekt besitzt bereits dieselben Grundbausteine in Flask und SQLite. Deshalb
wird kein zweiter Node-/Socket-Server eingeführt; die Regeln werden hier
klein, nachvollziehbar und testbar in Python umgesetzt.

## Quellen

- Hasbro, offizielles klassisches Regelheft: https://www.hasbro.com/common/instruct/risk.pdf
- Hasbro, deutsche Anleitung B7404: https://instructions.hasbro.com/api/download/B7404_de-de_risiko.pdf
- Hasbro, neuere Regelfassung: https://www.hasbro.com/common/documents/DAD2886D1C4311DDBD0B0800200C9A66/F56A63AE8FA145D9B82A5FA3919CA3A5.pdf
- boardgame.io, offizielle Dokumentation: https://boardgame.io/


## Aktuelle lokale Lobbyausstattung (25.10.2026)

- Die Spielerzahl ergibt sich ausschließlich durch die tatsächlichen Beitritte
  (zwei bis sechs Personen). Es gibt keine einstellbare Spielerzahl und keine
  vorgewählte Zielbesetzung. Alte gespeicherte Spielergrenzen sind wirkungslos.
- Länder zufällig zuteilen, übrige Starttruppen selbst reihum setzen. Kein
  Auswahlfeld für die Länderzuteilung. Ein Brett (Welt), automatische
  Kampfauswertung und Truppenpunkte; weitere Bretter, echte Würfel und
  Armeefiguren sind noch nicht auswählbar. Frühere Stilwerte bleiben erhalten.
- Der Host wählt vor dem Start die unterschiedlichen Armeefarben. Die Farbe
  wird mit der neuen Partie gespeichert, unabhängig von der Zugreihenfolge.
  Farbmissionen beziehen sich auf diese tatsächliche Farbe. Alte Partien
  behalten ihre bisherige Farbzuordnung nach Sitzplatz.
- Der Endstand erscheint als einklappbare Siegeranzeige direkt am Brett.
  Ergebnis erneut ansehen, Übersicht verlassen und reguläre Revanche bleiben
  möglich. Keine neuen Gewinner- oder Verlierer-Avatarbilder erstellt.
