# Würfel: genau zwei vorhandene Varianten

Stand: 27.10.2026, ausschließlich lokale Werkstatt.

| Variante | Vorhandene Grundlage | Zweck |
|---|---|---|
| Räumliche Würfel mit Physik | `static/dice-table.js`, lokales dddice-SDK und vorhandenes Theme | Bewegte Würfel vom Würfeltisch, Kniffel und Mäxchen |
| Flache Würfelanzeige | `showRolls` aus Conquest und dessen ursprüngliche `.battle-die`-Regeln | Anzeige vorliegender Werte ohne physikalischen Wurf |

**Anzahl, Aufdrucke und Farben sind Eigenschaften dieser beiden Varianten.**
Es gibt keine zusätzlichen Bausteine je Würfelseite, Würfelgruppe, Aufdruck oder
Wurfergebnis. In der Standardbibliothek stehen genau zwei Würfeleinträge.
Die generischen Musterwürfel gehören nicht mehr zur neuen Standardauswahl.
Vorhandene persönliche Entwürfe und ältere Projektmappen bleiben unverändert lesbar.

## Verwendung in der Werkstatt

Bibliothek → Würfel → Ansehen. Die große räumliche Vorschau besitzt eine lokale
Wurfprobe mit zwei Beispielwürfeln. Die flache Vorschau zeigt neutrale Werte.
Ein Projekt sammelt die gewählte Darstellungsvariante einschließlich ihrer
Eigenschaften und Herkunft. Dieselbe Variante kann in mehreren Projekten verwendet
werden. Die vollständigen Editoroptionen für Anzahl, Seitenaufdrucke und Gestaltung
werden später gemeinsam geprüft; die alten generischen Einstellungen werden dafür
nicht als drittes Würfelsystem angeboten.

## Gemeinsame Quellen

`dice_library.py` liest die betreffenden Rendererfunktionen direkt aus den
unveränderten Spielquellen. Der 3D-Adapter nutzt die ursprünglichen Funktionen
`localizeThemeAssets`, `createEngine`, `ensureEngine` und `animateRoll`, mit neutralen
Werten und ohne Spielaktionen oder Statusabfragen. Modell, Texturen, Physik und
SDK stammen aus den bereits lokal vorhandenen Dateien. Der flache Adapter nutzt
unverändert Conquests `showRolls`; die Form- und Schriftregeln bleiben in der
ursprünglichen CSS-Quelle. Die Vorschau skaliert die flache Gruppe als Ganzes.

Es werden keine Renderer oder Modelle aus einer weiteren Quelle ergänzt.
Themeressourcen werden auf die vorhandenen lokalen Dateien umgebogen; die
Vorschau erlaubt Verbindungen ausschließlich zum eigenen lokalen Ursprung.
Die bestehende Theme-Ausstattung erhält keine neue pauschale Lizenzbehauptung.
Quellprüfsummen verhindern unbemerkte Übernahme geänderter Renderer.

Die Bibliothek und Speicherung benötigen keinen App-/Datenbankimport. Spiele,
Fragenbanken, Konten und persönliche Entwürfe werden nicht geändert. Prüfprojekte
liegen getrennt unter `runtime/dice-library-20261027/qa-library`.