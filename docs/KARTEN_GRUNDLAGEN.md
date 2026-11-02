# Karten: Grundbausteine und endliche Sätze

Stand: 27.10.2026, ausschließlich lokal.

Die Werkstatt führt wiederverwendbare Bausteine. Eine einzelne Frage ist ein
Datensatz nach dem vorhandenen Steckbrief und kein Kartenobjekt.

| Grundbaustein | Ausstattung als ganzer Satz |
|---|---|
| Bewegliche Karte · 3D | 32, 52, 52 + 3 Joker, 104 und 104 + 6 Joker |
| Flache Anzeige-/Auswahlkarte | Dieselben fünf Spielkartensätze; Conquest-Länder und Conquest-Aufträge |

Das ergibt zwei Grundbausteine und zwölf Satzvarianten, insgesamt 14 neue
Bibliothekseinträge. Die zwei bisherigen generischen Kartenvorlagen bleiben
zusätzlich verfügbar. Unter jedem der beiden gemeinsamen Modelle lassen sich
Grundbaustein und Sätze auswählen. Die Auswahl „Karte im Satz“ blättert nur die
Vorschau; „Zu einem Projekt hinzufügen“ sammelt den vollständigen Satz.

Conquest umfasst **42 Länderkarten** und **12 Aufträge** in zwei Sätzen. Die
zwei im bestehenden Spiel vorhandenen Joker sind ergänzende Mitglieder des
Ländersatzes; sie werden nicht als zwei weitere Länder gezählt. Die Inhalte und
Kennungen werden unverändert aus den endlichen Spieldefinitionen übernommen.
Es werden keine persönlichen Kartenhände, Auftragszuweisungen oder Spielstände gelesen.

Perfect und Guesstimate verwenden ihre vorhandenen Fragenfenster. Die neuen
Metadaten verknüpfen diese mit ihren Datenquellen und dem Feldvertrag. Es werden
keine Fragenbanken in den Bausteinkatalog kopiert. Neue Fragen lassen Anzahl und
Kennungen der Bausteine unverändert. Siehe [KARTEN_INHALTE.md](KARTEN_INHALTE.md).

## Darstellung und Erhaltung

Werkstatt und lokaler Kartenvergleich nutzen denselben Renderer und dieselben
Bild-/Modelldateien. Der 3D-Körper stammt aus mehrasaurs Poker Pack (44 Dreiecke),
die französischen Kartengrafiken aus Kenneys Boardgame Pack, jeweils CC0 laut
vorhandenen Herkunfts- und Lizenzdateien. Diese Grafiklizenz erklärt nicht die
Conquest-Inhalte zu CC0. Conquest-Symbole und Kartenausschnitte benutzen die
ursprüngliche reine Kartenfabrik als Inhalt der flachen Grundlage.

Die bewegliche Vorschau kann gezogen und gewendet werden. Flache Länderkarten
lassen sich markieren; Aufträge dienen der Anzeige. Es wird keine Partie ausgeführt.
Editoroptionen bleiben offen. Bestehende Spiele und persönliche Entwürfe werden
nicht umgestellt. Alte gespeicherte Einzelkartenauswahlen bleiben lesbar, erscheinen
aber nicht mehr als neue Einzelbausteine im Katalog.

Reproduzierbare Berichte: `python deploy/audit_card_library.py` und
`python deploy/audit_workshop_semantics.py`.

## Eigene Kartensätze gestalten (28.10.2026)

Gestalten → Karten → Neuen Kartensatz beginnen. Die erste Fassung gestaltet
eigene endliche Sätze mit 1 bis 100 Karten. Bestehende französische Sätze und
Conquest-Sätze bleiben als Originale in der Bibliothek. Sie werden durch das
Öffnen des Editors nicht umgeschrieben oder durch eigene Karten ersetzt.

Ablauf: **Format & Größe → Vorderseite → Rückseite → Karteninhalt → Speichern**.
2D und 3D sind wählbar. Kartenhöhe und Seitenverhältnis mit Reglern ändern,
Hochkant/Quadrat/Querformat als schnelle Formatwahl. Rechts steht eine feste
Vergleichskarte von 6 × 9 cm; die bearbeiteten Karten werden bei Größenänderungen
tatsächlich größer oder kleiner. „Alles einpassen“ schaltet die automatische
Einpassung ausdrücklich ein. Die Maße sind virtuelle Beispielmaße, kein
Zentimetermaßstab des jeweiligen Monitors.

Fläche, Schrift, Vorderseitenrahmen und Zeichenfarbe sind getrennt. Die
Rückseite besitzt ihre eigene Fläche und Rahmen-/Musterfarbe. Rauten oder nur
Rahmen wählen; Kartenkante bei 3D. Diese Gestaltung gilt für den ganzen Satz.
Unter Karteninhalt einzelne Karten wählen, hinzufügen, duplizieren oder aus dem
ungespeicherten Satz entfernen. Jede Karte enthält Titel, Text und ein Zeichen.
Der letzte Satzbestandteil lässt sich nicht entfernen. Eine Einzelkarte wird
nicht als weiterer Baustein in die Bibliothek aufgenommen.

Vorderseite, Rückseite oder beide gemeinsam ansehen; in 3D auch schräg. Ansicht,
Vergleich und Zoom gehören ausschließlich zur Vorschau. Beide Darstellungen
verwenden dieselben erzeugten Kartenflächen. Die flache Grundlage stammt aus
der bisherigen originalCard-Fabrik. Der räumliche Körper und seine Materialien
sind als gemeinsame Funktionen aus dem vorhandenen Vergleichsrenderer gelöst;
Vergleich, vorhandene Bibliothek und neuer Editor verwenden diese Funktionen.
Ursprüngliche Modelldatei, 44 Dreiecke, Positionen und UVs bleiben erhalten.
Frühere allgemeine Einzelkartenvorlagen bleiben lesbar und können als eigener
Satz begonnen werden. Ihr bisheriger Bibliotheksrenderer bleibt erhalten.

Speichern hält die gemeinsame Gestaltung und sämtliche Karten als einen Satz
fest, fortlaufend in `design-library/recipes/card-workshop/`. Frühere Versionen
bleiben erhalten. Bibliothek → Karten → Meine Entwürfe → Ansehen/Varianten ansehen
→ Weitergestalten. In der Bibliotheksvorschau einzelne Satzmitglieder wählen;
Projektzuordnung und Übergabe übernehmen immer den vollständigen Satz.
Ungespeicherte Werte bleiben pro Browsertab erhalten. Speichern aktiviert keinen
Kartensatz in einem bestehenden Spiel.

Freies Layout, eigene Bilder auf Karten, Import von CSV-Karteninhalten und
Bearbeitung der vorhandenen Standardsätze sind noch nicht Teil dieser Fassung.
Fragenbanken bleiben unabhängig an ihren bisherigen Fragenfenstern.
