# Figuren und Spielsteine

Stand: 27.10.2026. Ausschließlich lokale Werkstatt; Editoroptionen folgen später.

## Wiederverwendbare Formfamilien

| Formfamilie | Vorhandene Grundlage | Konfigurationen |
|---|---|---|
| Schachfiguren | `models.js/buildPiece`, alle sechs Rollen in beiden Farben | Bisherige gedrechselte und geometrische Vorlage, jeweils 2D/3D |
| Damesteine | Derselbe ursprüngliche Modellgenerator, Rolle `checker` | Bisherige Damevorlage in 2D/3D |
| Conquest-Truppenmarke | Sockel, Zahlenfläche und Auswahlring aus `territories.js`, ursprüngliche CSS-Gestaltung | Eine gemeinsame räumliche Konfiguration mit projizierter Zahlenfläche |

Damit stehen **drei Formfamilien mit sieben festen Konfigurationen** zur Verfügung.
Schach und Dame sind bestehende allgemeine Werkstattvorlagen; sie werden nicht als
zusätzliche aktive Spiele ausgegeben. Die beiden Stile der Schachvorlage bleiben
Eigenschaften derselben Familie. Die flachen Ansichten verwenden die bisherige
Symbol-/Draufsicht desselben Generators.

Figurenrolle, Stil, Proportionen, Farbe bzw. Seite, Anzahl/Zahlenwert und Zustand
sind Eigenschaften. Es gibt keine Bibliothekseinträge pro Bauer, Land, Truppenzahl,
Spieler oder Partie. Gesammelt wird eine Satz-/Bausteinkonfiguration, keine laufende
Aufstellung. Die Vorschau zeigt neutrale Musterwerte und die Rollen eines Satzes.

## Abdeckung der vorhandenen Spiele

Alle acht Spielbereiche geprüft: Guesstimate, Guesstimate Party, Perfect,
Playtable, Würfeltisch, Kniffel, Mäxchen und Conquest. Nur Conquest besitzt derzeit
zusätzliche Spielsteine: ein gemeinsames Markensystem für alle Länder. Die Marke
besteht aus einem räumlichen Bronzesockel, einem Auswahlring und einer über dieselbe
Kamera projizierten farbigen Zahlenfläche. Diese Teile bleiben ein Baustein;
die Zahlenfläche wird nicht nochmals als eigener Button registriert.

Die übrigen Spiele verwenden bereits zugeordnete Karten, Würfel, Fenster,
Spieleranzeigen und Pulte. Das Pokerchip-Motiv am Playtable-Einsatzregler ist die
bereits vorhandene **Einsatzanzeige** (`output.poker-chip-display`), kein zusätzlicher
beweglicher Chip. Angriffs-/Bewegungspfeile bleiben Darstellungs-/Routenanzeigen.
Bildlich in Raumkulissen oder Flyern dargestellte Figuren sind keine eigenen Modelle.
Die ältere, vom aktuellen Conquest-Tisch nicht geladene `static/conquest-table.js`
wird nicht als zusätzliches Spielsteinsystem aufgenommen.

## Originalquellen und Bestandsschutz

`piece_library.py` registriert die Familien und bindet ihre Herkunft mit Prüfsummen.
Schach und Dame importieren den bestehenden `buildPiece` unmittelbar. Für Conquest
werden Geometrie, Material, DOM-Zahlenfläche, Anker und Kameraprojektion aus der
ursprünglichen Fabrik unverändert gelesen. Der Adapter setzt ausschließlich einen
neutralen Beispielpunkt, eine originale Vorschaufarbe und den Beispielwert 8 ein.
Er übernimmt keine Spielhandler, Statusabfragen, Länderbestände oder Datenbanken.
Die bestehende CSS-Datei wird unverändert eingebunden. Die Vorschau skaliert die
gesamte Komposition proportional.

Die drei alten allgemeinen Figuren-Vorlagen werden nicht zusätzlich neben ihren
zugeordneten Konfigurationen angezeigt. Vorhandene persönliche Entwürfe und ältere
Mappenschnappschüsse bleiben unverändert lesbar; nur Katalogkopien erhalten bei
Bedarf die Familienzuordnung. Der bisherige Renderer bleibt dafür verfügbar.

Quellinventar: [SPIELSTEINE_GRUNDLAGEN.json](SPIELSTEINE_GRUNDLAGEN.json),
reproduzierbar mit `python deploy/audit_piece_library.py`.
Prüfungen und Vorher-/Nachher-Nachweise liegen unter
`runtime/pieces-library-20261027/`. Editoroptionen, neue Figurenmodelle und die
Umstellung bestehender Spiele sind nicht Teil dieses Aufnahmeschritts.

Abschlussprüfung: zwölf gezielte Tests (Spielsteine und Projektmappen) bestanden,
72,566 Sekunden. Alle sieben Vorschaukonfigurationen im Browser geöffnet;
räumliche Ansicht gedreht. Getrennte Prüfmappe mit drei Formfamilien nach Neuladen
wieder geöffnet und lokal übergeben. Persönliche Werkstatt auf Port 8776 sichtbar
geprüft. 480 geschützte Dateien unverändert, einschließlich aller sieben
persönlichen JSON-Dateien; keine zusätzlichen persönlichen JSON-Dateien.


## Figureneditor ab 28.10.2026

Gestalten → Figuren & Spielsteine → Neuen Figurensatz beginnen. Die erste
Fassung gestaltet Schachfiguren und Damesteine aus derselben vorhandenen
`buildPiece`-Fabrik. Die zusammengesetzte Conquest-Marke bleibt zunächst als
Original in der Bibliothek; sie wird durch diesen Editor nicht ersetzt.

Ablauf: **Form → Größe & Proportionen → Material & Farben → Speichern**.
3D-Figuren und flache 2D-Marken sind wählbar. Bei Schach die gedrechselte oder
geometrische Formensprache wählen. Gesamtgröße, Körperhöhe, Fußbreite,
Körperbreite und Kopfgröße sind unabhängige Regler. Räumliche Proportionen
werden bei 2D verborgen; beim Damestein entfallen Kopf und Körperbreite.
Die Farben der beiden Seiten sind getrennt, Mattheit und Metallwirkung gelten
für den ganzen Satz und werden in 3D angeboten.

Standardmäßig bleibt der Maßstab der Vorschau fest. Die bearbeitete Figur
ändert ihre Größe sichtbar gegenüber einer grauen Referenzfigur (4 cm hoch)
und einer Beispielkarte (6 × 9 cm). Bei flachen Marken wird stattdessen eine
3 cm breite Referenzmarke gezeigt. Die cm sind virtuelle Beispielmaße, keine
Kalibrierung des Monitors. Die Karte und die Referenzfigur verwenden ebenfalls
die vorhandenen kanonischen Fabriken; sie gehören ausschließlich zur Vorschau.

Vorschaurolle einzeln oder alle sechs Rollen wählen, eine oder beide Seiten
zeigen, die räumlichen Figuren drehen und von oben ansehen. Diese Ansicht,
Vergleichshilfen und Ansichtszoom werden nicht als neue Spielteile gespeichert.
„Alles einpassen“ aktiviert die automatische Einpassung ausdrücklich. Zahlen
bleiben als Prozent-Feineinstellung unter „Genau einstellen“ verfügbar.

Gespeichert wird der vollständige gemeinsame Satz, keine einzelne Vorschaurolle.
Eigene Stände liegen append-only unter `design-library/recipes/piece-workshop/`
mit Vorgängerkennung. Bibliothek → Figuren & Spielsteine → Meine Entwürfe →
Ansehen/Varianten ansehen → Weitergestalten. Alte Werkstattvorlagen können als
eigener Satz begonnen werden; bestehende Dateien werden nicht umgeschrieben.
Projektmappe und Übergabe übernehmen die genaue ausgewählte Variante.
Ungespeicherte Werte bleiben pro Browsertab zur Wiederaufnahme erhalten.
Speichern aktiviert keinen Figurensatz in einem bestehenden Spiel.
