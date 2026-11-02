# Bildavatare gestalten

Stand: 28.10.2026. Lokale Werkstatt, Gestalten → Avatare.

1. **Bild wählen:** vorhandenes Rastermotiv öffnen oder PNG, JPEG oder WebP
   vom PC importieren. Das Original bleibt unverändert in der Bildbibliothek.
2. **Ausschnitt:** quadratischen Rahmen verschieben oder an den Ecken ändern.
   Pfeiltasten verschieben fein, Umschalt plus Pfeiltaste in größeren Schritten.
   Die vorhandenen Bühnenavatare beginnen mit dem Ausschnitt aus der gemeinsamen
   Spieleranzeige. „Größter quadratischer Ausschnitt“ setzt mittig zurück.
3. **Rahmen:** ursprüngliche Form, Kreis, abgerundetes Quadrat oder Quadrat;
   unabhängige Rahmenfarbe, Hintergrund und sichtbarer Stärkeregler.
4. **Größe:** ganze Spieleranzeige proportional skalieren. Die linke Anzeige
   behält ihre Größe; rechts ändern sich Avatar, Name und Anzeige gemeinsam.
   Darunter dient die originale Conquest-Anzeige mit neutralen Beispielwerten
   als Kontext. Prozentwerte stehen ergänzend unter „Genau einstellen“.
5. **Speichern:** Namen vergeben und vollständigen Entwurf sichern. In der
   Bibliothek unter „Meine Entwürfe“ ansehen und weitergestalten. Der genaue
   gespeicherte Stand hat eine eigene Adresse und lässt sich Projektmappen
   und Übergaben zuordnen. Ungespeicherte Werte bleiben pro Browsertab erhalten.

Ein Avatarentwurf besteht aus Originalquelle mit Prüfsumme, Ausschnitt,
Rahmen und Anzeigegröße. Neue Stände liegen fortlaufend unter
`design-library/recipes/avatar-workshop/`; frühere Stände bleiben erhalten.
Rahmen und Anzeigegröße werden nicht in das Bild eingebrannt. Zuschnitt und
PNG-Ausgabe verwenden dieselbe Bildverarbeitung wie die übrige Bildwerkstatt.
Beide Werkzeuge können auf derselben Seite bestehen und bearbeiten getrennte
Entwürfe. Die Ausgabe des Avatarzuschnitts ist einheitlich 512 × 512 Pixel;
die Darstellung wird visuell eingestellt.

Vorschau, Bibliotheksansicht und gespeicherter Entwurf verwenden dieselbe
Avatarvorschau und die unveränderte gemeinsame `createPlayerPortrait`-Fabrik.
Die Größe wird über deren Schriftmaß für die ganze Komponente eingestellt.
Die vorhandene Rahmengeometrie ist eine Editoroption an dieser Komponente;
es gibt keine kopierte Spielerkomposition. Vergleich und Beispielwerte sind
Vorschauhilfen und gehören nicht zum Entwurf.

Diese Fassung bearbeitet Bildavatare. SVG-Zuschnitt, freie Figurenmodellierung,
Kleidung/Ausstattung und automatische Verwendung in einem Spielerprofil sind
nicht umgesetzt. Speichern verändert keine Konten oder aktuellen Spielavatare.
Die persönliche Abnahme aller Motive und Rahmenkombinationen bleibt offen.
