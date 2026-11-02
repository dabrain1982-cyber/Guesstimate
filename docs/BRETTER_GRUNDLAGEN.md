# Bretter und Spielflächen: 2D und 3D

Stand: 27.10.2026, ausschließlich lokale Werkstatt.

Es gibt genau zwei Grundvarianten: **2D** und **3D**. Größe, Form und Bild sind
Eigenschaften einer Brettkonfiguration. 2,5D ist eine schräge Ansicht der räumlichen
Grundvariante und kein drittes Brettmodell. Einzelne Länder, Felder, Spielzüge und
Partien erzeugen keine neuen Bibliothekseinträge.

## Aufgenommene Konfigurationen

| Vorhandene Quelle | 2D | 3D | Eigenschaften / Zuordnung |
|---|---|---|---|
| Conquest-Weltbrett | Unverändertes Brettbild | Vorhandener räumlicher Tisch mit demselben Bild | Rechteckige Weltkarte, Bild 1284 × 1225; räumlicher Träger mit abgeschrägten Ecken |
| Playtable-Kartenfläche | Ursprüngliche Filzfläche und gemeinsame Ablagefläche | – | Ursprüngliches Layout 1920 × 900; Größe, Form und Filzbild als Eigenschaften |
| Würfeltisch / Kniffel / Mäxchen | Eine gemeinsame Würfelfläche | – | Tatsächlicher Anzeigebereich 1290 × 685 im vorhandenen Tischbild, keine dreifache Kopie je Spiel |
| Bisheriges Schach-/Damebrett | Draufsicht | Vorhandene Brettgeometrie | Feldmuster, Maße, Rahmen und Dicke aus derselben bisherigen Modellfabrik |

Das sind sechs feste Quellkonfigurationen unter zwei Grundvarianten. Persönliche
Brettentwürfe werden ihrer bereits gespeicherten 2D-/3D-Ausführung zugeordnet,
ohne ihre Dateien oder Schnappschüsse umzuschreiben. Die zwei bisherigen allgemeinen
Standard-Brettvorlagen werden nicht zusätzlich als eigenständige Grundmodelle
angeboten. Alte gespeicherte Auswahlen und eigene Entwürfe bleiben lesbar.

## Abdeckung der Spiele

Geprüft wurden Guesstimate, Guesstimate Party, Perfect, Playtable, Würfeltisch,
Kniffel, Mäxchen und Conquest. Daily-/Party-Quiz und Perfect besitzen kein eigenes
Spielbrett. Ihre Fragenfenster, Pulte und Raumkulissen bleiben in den bisherigen
Elementbereichen. Der Kniffelblock bleibt ein vorhandener Fenster-/Anzeigebaustein.

Bei Playtable und den Würfelspielen wird die bereits vorhandene 2D-Spielfläche
aufgenommen. Es wird kein neuer räumlicher Tisch für diese Spiele erfunden. Der
Würfelbereich ist ein exakt aus den bestehenden Layoutmaßen abgeleiteter Ausschnitt
des Tischbildes; die Bildperspektive ist Teil dieser vorhandenen 2D-Darstellung,
kein neu importiertes 3D-Modell. Ältere Conquest-Bildentwürfe und unbenutzte
Kartenversionen werden durch diesen Auftrag nicht zu aktuellen Spielvarianten.

## Gemeinsame Umsetzung und Speicherung

`board_library.py` liest vorhandene Quellmaße, Bildreferenzen und die reine
Conquest-Tischfabrik aus den aktuellen Dateien. Conquests `makeTable` samt
Geometrie-/Holzhelfern und Kameraeinpassung werden unverändert wiederverwendet.
Die Bilddatei ist dieselbe wie im laufenden lokalen Spiel. Weder das vollständige
Raumprogramm noch Spielhandler oder Länder-/Truppenstände werden gestartet.
Das Feldbrett nutzt die bestehende `buildBoard`-Funktion aus `models.js`.
Playtable und Würfelfläche benutzen die ursprünglichen CSS-Regeln und Bilder;
Vorschau und Innenkomposition werden nur als Ganzes proportional skaliert.

Eine Projektmappe speichert die konkrete Konfiguration mit Größe, Form, Bild,
Grundvariante und Herkunftsprüfsummen. Wiederverwendung und lokale Übergabe
behalten diese Auswahl exakt. Die Drehprobe verändert nur die flüchtige Ansicht.
Editoroptionen werden weiterhin später gemeinsam geprüft.

Es gibt keine Änderung an Spielen, Fragenbanken oder persönlichen Entwurfsdateien.
Kein App-/Datenbankimport, kein Serverkontakt, keine Veröffentlichung. Reproduzierbarer
Quellenbericht: `python deploy/audit_board_library.py` →
[BRETTER_GRUNDLAGEN.json](BRETTER_GRUNDLAGEN.json). Prüfdaten:
`runtime/board-library-20261027/`, getrennt von `design-library`.