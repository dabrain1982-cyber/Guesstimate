# Lokaler Kartenvergleich · 27.10.2026

Drei Ansichten derselben Beispiele: bestehender Kartentisch, neue Kartengrafik,
importierter 3D-Körper. Ausschließlich kostenlos; keine Änderung an Spielen oder
persönlichen Werkstattdaten. Nicht in den Editor integriert.

Start: `python -X utf8 offline-preview/card-comparison-v1/serve.py --port 8778`

Adresse: http://127.0.0.1:8778/

Nach der Auswahl vom 27.10.2026 sind der 3D-Körper für bewegliche Karten und
die neue flache Grafik für Anzeige-/Auswahlkarten als zwei gemeinsame Modelle
in der lokalen Werkstatt auf 8776 aufgenommen. Vergleich und Bibliothek teilen
denselben Renderer und dieselben Assetdateien. Bestandsumfang und weitere
offene Schritte stehen in `docs/KARTEN_GRUNDLAGEN.md` im Projektordner.

## Verwendete Quellen

1. **Guesstimate-Bestand:** Darstellung wird unmittelbar aus
   `static/card-table.css` und der originalen `cardElement`-Fabrik in
   `static/card-table.js` gelesen. Nur der umgebende Eingabeadapter arbeitet mit
   neutralen Beispielen. Kein Spielstart, keine Serveraktion, keine Datenbank.
   Die bisherige Rückseite bleibt in der ersten Spalte erhalten.
2. **Kenney – Board Game Pack v2:**
   https://kenney.nl/assets/boardgame-pack · Autor Kenney Vleugels.
   CC0, lokale Original-Lizenz unter `assets/kenney/license.txt`.
   Verwendet werden die Karten-PNGs (140 × 190 Pixel). Keine eigene Neuzeichnung.
   Diese Auflösung reicht für den Vergleich in üblicher Spielgröße; für eine
   große Endfassung sollten die ebenfalls angebotenen Vektoren aufbereitet
   werden. Hier keine unbegrenzte Druck-/Zoomqualität behauptet.
3. **mehrasaur – Poker Pack:**
   https://opengameart.org/content/poker-pack · CC0 laut konkreter Autorenseite.
   Enthält `card.obj`, `card.mtl`, `card.blend`. Nur die Karten-Dateien verwendet.
   Originalquellen unter `assets/mehrasaur/`. In `card-mesh.json` wurden Achsen
   ausgerichtet, Mittelpunkt und einheitliche Größe gesetzt, konvexe Flächen
   trianguliert und Vorder-/Rückseiten-UVs ergänzt. Der ursprüngliche abgerundete
   Umriss und die echte Dicke sind erhalten. Kein selbst erzeugter Ersatzkörper.
   Das Quellmodell enthält keine Kartengrafik und keine Biege-/Physikanimation.
   Es wird mit denselben Kenney-Grafiken wie Spalte 2 versehen.
4. **Three.js r180:** Bereits lokal vorhandene Bibliothek aus der Conquest-
   Vorschau, MIT-Lizenz unter `/vendor/LICENSE`. Keine neue Laufzeitinstallation.

Downloadadressen, Prüfsummen und Modellmaße: `assets/import-manifest.json`.
Originalarchive unter `runtime/card-comparison-20261027/downloads/`.
`prepare.py` extrahiert nur bekannte Datendateien aus geprüften Archiven und
erzeugt die lokale Geometrieansicht. Keine heruntergeladene Software ausgeführt.

## Vergleich und Grenzen

- Gemeinsame Beispielkarten, Anordnung, Zoom und Blickwinkel.
- Einzelkarte, Hand mit fünf Karten, Stapel mit zwölf und ganzes Deck mit 52.
- Ziehen, Wenden, Tastaturbedienung. Alle Zustände nur im Arbeitsspeicher der
  Vergleichsseite; Neuladen setzt sie zurück.
- Erste und zweite Spalte verwenden denselben flachen Darstellungsaufbau.
  Zweite und dritte Spalte dieselbe neue Grafik. Der Modellkörper der dritten
  Spalte behält sein ursprüngliches Seitenverhältnis; die Höhe ist gleich.
- Keine Mehrspieler-, Misch-, Austeil-, Kartenphysik- oder Regelprüfung. Die
  vorhandene Spiellogik müsste bei einer späteren Übernahme angebunden werden.
- WebGL erforderlich für die dritte Spalte; Ladefehler werden sichtbar gemeldet.
- Die laufende Werkstatt und der Spiele-Dienst werden nicht neu gestartet.
- Der Vergleichsserver bindet nur 127.0.0.1, erlaubt keine Schreibanfragen und
  liefert ausschließlich Vergleichsdateien und ausdrücklich freigegebene
  Originalgrafik-/Schrift-/Bibliotheksdateien aus. Keine externen Laufzeitaufrufe.

## Weitere geprüfte Quellen und Hilfsmittel

Stand 27.10.2026. Recherche und Empfehlungen, keine zusätzlichen Installationen:

| Quelle / Werkzeug | Nutzen | Kosten / Lizenzhinweis |
|---|---|---|
| https://kenney.nl/assets | Zusammenpassende Bediengrafiken, Spielelemente, Klänge | Einzelne Assetpakete kostenlos, CC0; All-in-1-Bundle optional kostenpflichtig |
| https://opengameart.org/ | Spezialmodelle und Grafik | Kostenlos; Lizenz pro Werk |
| https://quaternius.com/packs/3dcardkitfantasy.html | Figuren und modellierte Fantasy-Karten als Stilreferenz | Kostenlose CC0-Grundpakete, bezahlte Erweiterungen; Fantasy-Karten sind keine normalen Pokerkarten |
| https://kaylousberg.itch.io/board-game-bits | Einheitliche Spielfiguren, Marker und Würfel | CC0-Grundpaket kostenlos; Spielkarten laut Autor in kostenpflichtiger Extra-Version, daher hier ausgeschlossen |
| https://polyhaven.com/license | Modelle, realistische Oberflächen, Umgebungslicht | Assets CC0; hier nichts heruntergeladen |
| https://ambientcg.com/ | Papier, Stoff, Filz, Holz | Assets CC0; hier nichts heruntergeladen |
| https://www.blender.org/about/ | Geometrie, UVs, Animation, Export | Kostenlos und offen, GPL |
| https://inkscape.org/en/about/license/ | Vektorgrafiken und Kartenmotive | Kostenlos und offen, GPL |
| https://www.gimp.org/ | Bilder, Texturen, Zuschnitt | Kostenlos und offen |
| https://www.materialmaker.org/ | Eigene prozedurale Oberflächen | Kostenloses offenes Werkzeug; Community-Materialien gesondert prüfen |
| https://gltf-transform.dev/cli | Modelle prüfen und optimieren | Offenes Werkzeug, MIT laut Projekt |
| https://github.com/KhronosGroup/glTF-Validator | Standardkonformität künftiger glTF-/GLB-Importe | Offenes Prüfwerkzeug; keine Aussage über künstlerische Qualität |
| https://kenney.nl/assets/casino-audio | Karten, Chips, Würfelgeräusche | Kostenlos, CC0; noch keine Klangauswahl/Integration |
| https://freesound.org/help/faq/ | Individuelle Tisch-/Spielgeräusche | Lizenz je Datei: CC0, CC BY oder CC BY-NC; keine pauschale Freigabe |
| https://www.audacityteam.org/faq/ | Klänge schneiden und Lautstärke bearbeiten | Kostenlos und offen; nicht neu installiert |
| https://developers.google.com/fonts/ | Lesbare offene Schriftfamilien | Kostenlos; Einzellizenz beilegen, lokal hosten; Auswahl noch offen |

Empfehlung: Inhalt und Grafik einer Karte gemeinsam verwalten, dazu flache
Anzeige-/Auswahlansicht und räumliche Tischansicht. Die endgültige Stilwahl und
Editoroptionen sind weiterhin offen. Neue Schrift- und Klangquellen sind damit
recherchiert; die eigentliche Hör-/Schriftauswahl steht noch aus.
