# Material und Ansicht als gemeinsame Projekteigenschaften

Stand: 27.10.2026, ausschließlich lokal. In der Werkstatt öffnet **Material &
Ansicht** eine gemeinsame Übersicht mit Originalbeispielen. Es bleiben 17
Elementbereiche; Materialien und Darstellung sind zwei Eigenschaftsbereiche,
keine zusätzlichen Einzelobjekte im Elementkatalog.

## Kleine Materialpalette

| Familie | Vorhandenes Beispiel / Abgrenzung |
|---|---|
| Holz | Ursprünglicher Buttonrenderer mit vorhandener Holztextur; Conquest-Tisch als weiterer Einsatz. |
| Stein & Tafel | Ursprünglicher Buttonrenderer mit Schiefer; Verweise auf die passenden festen Kreide-/Steinschriftstile. |
| Metall | Ursprünglicher Buttonrenderer mit Metalltextur; fester Stil „In Eisen gestanzt“ verknüpft. |
| Farbfläche | Farbe ohne Materialstruktur; kein neues Modell je Farbwert. |
| Farbverlauf | Bestehende Fläche mit zwei Farben. |
| Durchscheinend | Bestehende Fläche mit Deckkraft; keine Glassimulation behauptet. |
| Filz | Originale Playtable-Fläche. Bildgebundene Struktur, keine frei austauschbare 3D-Textur. |
| Papier | Originaler Perfect-Einstellungszettel; feste Handschrift-/Stempelstile verknüpft. |
| Bedruckter Karton | Freigegebener flacher Kartenbaustein. Aufdruck/Satz sind Eigenschaften; Fragen bleiben Daten. |

Die sechs Buttonbeispiele verwenden denselben vorhandenen Renderer, dieselbe
Kontur und die vorhandenen lokalen Materialien. Filz, Papier und Karten sind
direkte Vorschauen bereits erfasster Bausteine. Keine neuen Materialdateien,
Modelle, Bilder, Downloads oder parallelen Renderer erzeugt.

## Ansicht, Licht und Bewegung

Drei Beispiele ordnen die bestehenden Projektentscheidungen ein: 2D als feste
flache Oberfläche, 2,5D als fester schräger Blick auf räumliche Elemente und 3D
mit veränderbarer Kamera. Die Beispiele nutzen die originale Playtable-Fläche,
das vorhandene räumliche Conquest-Brett und den ursprünglichen Conquest-Raum.
2,5D erzeugt kein drittes Brett-/Würfelmodell.

Licht/Schatten und gewünschte Bewegung von Figuren, Würfeln und Karten bleiben
getrennte vorhandene Projektangaben. Die ursprünglichen beiden Würfelvarianten
und beiden Kartenbausteine bleiben bestehen. Eine Bewegungsauswahl implementiert
keine neue Physik für flache Anzeigen. Die konkrete Umsetzung klären die späteren
Baustein-Editoren bzw. die Spielintegration.

## Projektmappe und Bestandserhaltung

Unter **Materialwünsche für das Projekt** lässt sich eine Palette vormerken.
Die Wahl hält Gestaltungswünsche fest und verändert die Originalelemente nicht.
Speichern und Übergabe enthalten die Materialdefinitionen samt Herkunft als
zusätzliche Projekteigenschaft `surfaces`; sie werden nicht in `items` aufgenommen.
Damit verändern Materialwünsche weder Elementzahl noch Modellkennungen.

Das bestehende Projektformat 2 erhält einen optionalen Schlüssel. Alte Mappen
ohne Materialwahl bleiben ohne Migration lesbar. Ein Speichern ohne den neuen
Schlüssel erhält bereits gespeicherte Wünsche; eine ausdrücklich leere Auswahl
kann sie in einem neuen Stand entfernen. Frühere Dateien und Schnappschüsse
bleiben erhalten. Gespeicherte Materialdefinitionen ändern sich bei späteren
Katalogänderungen nicht nachträglich. Persönliche Dateien wurden nicht bearbeitet.

Eine gemeinsame Oberflächenkomponente zeigt die Materialfamilien in Übersicht
und Projektmappe; Vorschauen werden als Ganzes proportional skaliert. Beim
Schließen/Verlassen werden die Vorschau-Iframes entfernt. Dadurch laufen
ausgeblendete Szenen nicht weiter und erhalten keine ungültigen Größen.

18 gezielte Tests bestanden (93,489 Sekunden): Herkunft/Verknüpfungen,
Eigenschaften ohne Katalogwachstum, Original-Schnappschüsse, Wiederverwendung,
alte Mappen/Clients, unveränderliche Wünsche, unzulässige Auswahl, lokale Routen,
Fragenwachstum und Übergabe. JavaScript-Syntax geprüft. Browserprüfung mit
Materialbeispielen, fünf Schriftverweisen, drei Ansichten, Raum-Ansichtswechsel,
Speichern/Neuladen/Übergabe und schmaler Ansicht (390 px; Inhaltsbreite 375 px).

Prüfmappe ausschließlich unter `runtime/properties-20261027/qa-library/`;
Übergabe mit zwei Originalelementen und Holz-/Filzwunsch:
`handoff-88962de0a7fe48bb857cdb811ef1e7cc.json`.
Weitere Belege unter `runtime/properties-20261027/`.
Reproduzierbarer Katalog: [MATERIAL_DARSTELLUNG.json](MATERIAL_DARSTELLUNG.json),
erzeugt mit `python deploy/audit_workshop_properties.py`.

Die Editoroptionen sind weiterhin nicht abgenommen. Diese Auswahl ist keine
universelle Materialübertragung auf alle Komponenten und keine Spielumstellung.
