# Aktueller Umfang ab 29.10.2026

Nur der Button-Editor bleibt in der Werkstatt, unter **Editor**. Alle anderen
Editoroberflächen, ihre Bearbeitungszugänge und die Projektmappe sind entfernt.
Die 17 Bibliotheksbereiche einschließlich gespeicherter Entwürfe bleiben zum
Ansehen und Recherchieren erhalten. Alte Editoradressen öffnen die passende
Bibliothek. Material & Ansicht bleibt eine lesende Referenzsammlung.
Ältere Beschreibungen anderer Editoren oder der Projektmappe weiter unten
dokumentieren den früheren Stand und sind kein weiterer Entwicklungsauftrag.

## Frühere Dokumentation (ersetzt, kein Fortsetzungsauftrag)

# Deine Werkstatt (lokal)

## Button-Editor: eigener Neubeginn ab 28.10.2026

Der weiterhin gemeinsam eingebundene Button-Editor bietet **Neuen Button erstellen** und fünf direkt anwählbare Schritte: Form → Oberfläche & Farbe → Beschriftung → Bewegung & Ton → Speichern. Die sieben neuen Schriftwahlen verändern nur Schrift und Wirkung; Fläche und Farben bleiben separat. Vorhandene gekoppelte Rezepte bleiben lesbar und lassen sich ausdrücklich trennen. Eigene Oberflächen einer Spielvorlage werden erkennbar vom Original unterschieden. Details und Prüfumfang stehen in der Button-Werkstatt-README.

Speichern legt einen Entwurf an. Eine allgemeine Auswahl aktiver Entwürfe für bestehende Spiele ist noch offen; Projektzuordnung und Spieleinsatz sind verschiedene Schritte.

Start über die vorhandene Werkstattübersicht oder:
`python -X utf8 D:\Guesstimate\offline-preview\game-workshop-v1\serve.py --port 8776`
und <http://127.0.0.1:8776/#editor/buttons>.

## Drei unabhängige Bereiche

Der vorhandene Desktop-Starter öffnet direkt diese gemeinsame Werkstatt auf
8776. Die ältere Übersicht und der eigenständige Buttoneditor bleiben erhalten;
beide Buttonzugänge benutzen dieselben Quellen und denselben Entwurfsspeicher.
Es wird keine neue Werkstatt pro Erweiterung angelegt.

**Gestalten** ist die projektunabhängige Werkstatt. Oben steht Werkstatt;
links stehen die wachsenden Elementarten. Buttons sind der erste Eintrag.
In der Mitte wird das vorhandene Werkzeug für genau diese Elementart geladen.
Ein Besuch legt weder ein Spiel noch eine Projektmappe an.

**Bibliothek** verwendet dieselbe Elementliste. Hier lassen sich vorhandene
Bilder, eigene gespeicherte Entwürfe und Werkzeugvorlagen ansehen, weitergestalten
und frei benannten Projekten zuordnen. Ein Element kann in mehreren Projekten
liegen. Mehrere Buttons oder andere Varianten derselben Art sind zulässig.

**Projektmappe** ist die Sammlung der benannten Projekte. Ein neues Projekt
beginnt leer mit einem selbst gewählten Namen. Es sammelt beliebig kombinierte
Elemente, Wünsche und offene Entscheidungen. Die Übergabe enthält feste
Momentaufnahmen der Auswahl und bereitet ein Interview mit Codex vor. Das Spiel
entsteht anschließend aus dieser Auswahl und dem Gespräch.

Schach ist eine vorhandene Projektmappe und bestimmt weder Startseite noch
Werkzeugauswahl. Die frühere Mappe wird unverändert erhalten und beim Öffnen
lesend in die neue Sammlung übersetzt. Erst ausdrückliches Speichern erzeugt
einen neuen Stand mit derselben Projektkennung und bewahrtem vollständigem
Ursprungsdatensatz.

## Vorhandene Werkzeuge und Bestände

- **Buttons:** Die vorhandene Button-Werkstatt wird als dieselbe Oberfläche
  eingebunden. Sie nutzt ihren bisherigen Validator, Speicher und Renderer.
  Standalone-Werkstatt und eingebettete Ansicht schreiben dieselben Entwürfe;
  Form-, Material-, Schrift-, Klang- und Bewegungslogik sind nicht kopiert.
  Nach dem Speichern lässt sich der genaue Entwurf unmittelbar zuordnen.
- **Bretter:** Zwei Grundvarianten (2D/3D), mit Größe, Form und Bild als Eigenschaften. Conquest-Brett, Playtable-Kartenfläche und gemeinsame Würfelfläche aus vorhandenen Quellen; bisheriges Feldbrett als Konfiguration. Alle acht Spiele geprüft, Quiz/Perfect ohne eigenes Brett. Bestehende persönliche Entwürfe unverändert. Eigene Bretter im neuen Editor gestalten; bestehende Spieloberflächen bleiben in der Bibliothek. Siehe [BRETTER_GRUNDLAGEN.md](../../docs/BRETTER_GRUNDLAGEN.md).
- **Figuren:** Neuer Editor für Schachfiguren und Damesteine mit Größe, Proportionen und Farben sowie festem Größenvergleich. Die ursprüngliche Conquest-Marke bleibt in der Bibliothek. Aufnahme und Grenzen siehe [SPIELSTEINE_GRUNDLAGEN.md](../../docs/SPIELSTEINE_GRUNDLAGEN.md).
- **Würfel:** Genau zwei vorhandene Varianten: räumliche Würfeltisch-Würfel mit Physik und flache Conquest-Anzeige. Anzahl, Aufdrucke und Farben sind Eigenschaften, keine weiteren Bausteine. Vorschauen lesen die ursprünglichen Renderer direkt. Die bisherigen Musterwürfel sind aus der Standardauswahl genommen; gespeicherte alte Mappen und persönliche Entwürfe bleiben erhalten. Editoroptionen später. Siehe [WUERFEL_GRUNDLAGEN.md](../../docs/WUERFEL_GRUNDLAGEN.md).
  Die Vorschau zeigt ausschließlich den gerade bearbeiteten Baustein.
  2D-/3D-Ausführung wird am Element gespeichert. Die Vorschauansicht ist keine
  vorweggenommene Projektkamera. Neue Varianten bleiben in ihrer Bibliothek.
- **Karten:** Zwei gemeinsame Grundbausteine (beweglich in 3D / flach) und
  zwölf vollständige Satzvarianten: je fünf französische Spielkartensätze in
  beiden Ausführungen, dazu Conquest mit 42 Ländern (zwei Joker ergänzend) und
  zwölf Aufträgen als zwei flache Sätze. Einzelkarten sind nur Satzmitglieder.
  Perfect- und Quizfragen gehören zu Fenstern mit Datenquellen nach Steckbrief.
  Alte eigene Entwürfe und gespeicherte Kartenauswahlen bleiben erhalten.
  Eigene Sätze im neuen Karteneditor gestalten; Originale bleiben auswählbar. Siehe [KARTEN_GRUNDLAGEN.md](../../docs/KARTEN_GRUNDLAGEN.md)
  und [WERKSTATT_LOGIKPRUEFUNG.md](../../docs/WERKSTATT_LOGIKPRUEFUNG.md).
- **Lobbys & Übersichten:** 134 Quellvarianten in sieben Modellen aus allen
  sieben Mehrspielerspielen. Ganze Räume, Übersichten, Zeilen und Zustände
  ansehen und Projekten zuordnen; der bisherige allgemeine Lobbyentwurf bleibt erhalten.
- **Hintergründe, Titelbilder und Flyer:** Fertige Bilder importieren, ansehen,
  auswählen und Projekten zuordnen. Diese Arten werden nicht als editierbar
  angeboten. Vorhandene Originale und früher gespeicherte Ausschnitte bleiben
  unverändert verfügbar.
- **Icons und Avatarbilder:** Bildwerkstatt für Ausschnitt und proportionale
  Ausgabegröße. Original und Varianten bleiben getrennt erhalten. Das ist kein
  freier Zeichen-, Textsatz- oder 3D-Avatar-Editor.
- **Fenster:** 84 konkrete Verwendungen in 30 Modellen aus allen vorhandenen
  Spielen sowie Profil und Shop. Regeldialoge, Entscheidungen, Inventare und
  Aktionsflächen sind in der Bibliothek ansehbar und Projekten zuordenbar.
  Gemeinsame Modelle bewahren die jeweiligen Inhalte, Rollen und Zustände als
  einzelne Varianten. Ein Fenstereditor und dessen Optionsprüfung folgen später.
- **Eingaben:** 58 Einsatzvarianten in 27 Modellen. Text- und Zahlenfelder,
  Auswahlfelder, Schalter, Regler sowie Zuordnen und Sortieren verwenden dieselbe
  Originalquellen-Vorschau wie die Fenster. Beschriftungen, Grenzen und Zustände
  bleiben je Variante erhalten. Die Bibliothek lässt sich nach Spiel und
  Eingabeart filtern; konkrete Varianten sind Projektmappen zuordenbar.
- **Anzeigen:** 210 Einsatzvarianten in 63 Modellen aus allen acht Spielen sowie
  Profil und Shop. Punkte, Timer, Fortschritt, Status, Zähler und Ergebnisse
  lassen sich nach Spiel und Anzeigeart filtern und als konkrete Variante
  Projekten zuordnen. Zeitwerte bleiben feste Beispiele; Editoroptionen folgen später.

## Aktuelle Arbeitsreihenfolge (28.10.2026)

Die Elementaufnahme und gemeinsame Material-/Ansichtsübersicht sind auf dem
dokumentierten Stand abgeschlossen. Nach der zuvor zurückgestellten Button-
Optionsprüfung ist jetzt der erste technische Durchgang an neun Guesstimate-
Kernmodellen erfolgt: wirkungslose Optionen abhängig vom Kontext kenntlich
gemacht bzw. verborgen, Tiefenanzeige korrigiert. Keine Originalgestaltung oder
Zusammenführungsentscheidung geändert. Siehe `docs/BUTTON_EDITOR_PRUEFUNG.md`.

Die Prüfung sämtlicher 85 Modelle, weiterer Baustein-Editoren und die persönliche
gestalterische Abnahme bleiben offen. Sieben feste Schriftstile und 13 kurze
Klänge aus der neuen Werkstattauswahl sind jetzt im Button-Editor wählbar.
Alte Kennungen, gespeicherte Rezepte und Spielzuordnungen bleiben erhalten.
Siehe `docs/BUTTON_MEDIEN_INTEGRATION.md`.

Weitere optische Zusammenführungen, vollständiger Einsatzweg eines gespeicherten
Buttons und Projektvorschau sind weiterhin gesonderte Aufgaben.

Die nächsten Elementarten verwenden weiterhin ihre tatsächlichen gemeinsamen
Quellen. Eine Bestandsübersicht allein gilt nicht als eingerichtete Bibliothek
oder fertiger Editor. Fenster, Eingaben und Anzeigen aus den Spielen sind aufgenommen.

## Fensterbibliothek

Unter Bibliothek → Fenster nach Spiel, Fensterart oder Text suchen.
„Varianten ansehen“ öffnet ein gemeinsames Modell mit einzeln auswählbaren
Einsatzorten und Zuständen. „Zu einem Projekt hinzufügen“ übernimmt genau die
angezeigte Variante. Mehrere Varianten desselben Modells und Wiederverwendung
in mehreren Mappen sind möglich.

`source_windows.py` liest die tatsächlichen verbundenen Vorlagen, Makros und
Styles. Neutrale Beispieldaten ersetzen Konten, Spielstände und geheime Inhalte.
Die Vorschau lädt keine Spielhandler und führt keine Formularaktionen aus.
Dynamische Karten, Würfel und Kniffelblock stammen aus erfassten Originalfabriken
in `generated-windows.json`, mit geprüften Quellen. Die Originalkomposition wird
als Ganzes proportional skaliert; es entsteht keine zweite Fensterimplementierung.
Laufzeitabhängige Button-Mounts sind nicht Teil dieser inerten Komponentenbeispiele.

Projektstände und lokale Übergaben enthalten die vollständige konkrete Variante
mit Originalfragment, gerendertem Beispiel, Quellen und Prüfsummen. Die Aufnahme
erzeugt keine persönlichen Fensterkopien oder neue Mappen. Bestand und Zuordnung:
[FENSTER_BESTAND.md](../../docs/FENSTER_BESTAND.md). Erneuern mit
`node deploy/capture_generated_windows.mjs` und
`python deploy/audit_window_coverage.py`. Die Button-Optionsprüfung bleibt für
später vorgemerkt.

## Eingabebibliothek

Die Eingabebibliothek verwendet `source_inputs.py` auf demselben Vorschauweg
wie `source_windows.py`; es gibt keine kopierte Grundimplementierung der
Originalkomponenten. Vorschauen bleiben inert, PIN-Felder leer. Es werden
weder Konten noch Spielerantworten oder Spielstände gelesen. Eingabeeditor,
Validierungsprobe und gemeinsame Optionsprüfung bleiben spätere Aufgaben.
Quellen und Grenzen: [EINGABEN_BESTAND.md](../../docs/EINGABEN_BESTAND.md).
Erneuern: `python deploy/audit_input_coverage.py`.

## Anzeigenbibliothek

`source_indicators.py` verwendet denselben Quellen-, Varianten- und Vorschauweg
wie Fenster und Eingaben. Die Vorschau zeigt unveränderte Originalkomponenten
mit neutralen Werten und skaliert deren gesamte Komposition. Kniffelanzeigen,
Mäxchen-Leben, Conquest-Porträtwerte, Wurfergebnisse und Zeitpunkte stammen aus
den vorhandenen Darstellungsfunktionen bzw. Berechnungen. Die Erfassung prüft
ihre Quellen; sie lädt weder Konten noch Spielstände und startet keine Timer.
Gemeinsame Lobbyzustände bleiben einem Modell zugeordnet, während Spiele und
Zustände einzeln erhalten bleiben. Die konkrete Auswahl bleibt auch nach
erneutem Öffnen einer Projektmappe und in der lokalen Übergabe erhalten.

Bestand und Grenzen: [ANZEIGEN_BESTAND.md](../../docs/ANZEIGEN_BESTAND.md).
Erneuern: `node deploy/capture_generated_indicators.mjs` und
`python deploy/audit_indicator_coverage.py`. Anzeigeneditor und die gemeinsame
Prüfung der Editoroptionen bleiben spätere Aufgaben.

## Spieleranzeigen und Pulte

Bibliothek → Spieleranzeigen & Pulte ergänzt 146 Varianten in 13 Modellen aus
allen acht Spielen sowie Profil und Shop. Gemeinsame Profilfenster, Lobbyplätze,
kompakte Porträts, Ranglisteneinträge und Namenspulte bleiben ihren Originalquellen
zugeordnet. Die 14 Pultfamilien erscheinen im Profilfenster und in der Auswahl
des Profils; der Shop enthält seine 13 angebotenen Motive. Die bestehenden
öffentlichen Porträtausschnitte aller 19 Avatare bleiben erhalten.

`source_players.py` verwendet denselben Quellen-, Vorschau- und Speicherweg wie
Fenster, Eingaben und Anzeigen. Die gesamte Originalkomponente wird proportional
skaliert; es entsteht keine zweite Innenkomposition. Rollen, Zustände und Motive
sind einzeln zuordenbar. Konten, Ausrüstung und Partien werden für die neutralen
Beispiele nicht gelesen. Kartenflächen und Würfelpulte bleiben zusätzlich in
ihren jeweiligen Elementfamilien auffindbar. Editoroptionen folgen später.

Bestand: [SPIELER_BESTAND.md](../../docs/SPIELER_BESTAND.md). Erneuern mit
`node deploy/capture_generated_players.mjs` und `python deploy/audit_player_coverage.py`.

## Lobbys und Lobbyübersichten

Bibliothek → Lobbys & Übersichten ergänzt 134 Quellvarianten in sieben Modellen
aus allen sieben Mehrspielerspielen. Der bisherige allgemeine Lobbyentwurf bleibt
zusätzlich erhalten; ohne Filter stehen deshalb acht Modelle bzw. 135 Varianten
in der Bibliothek. „Im Spiel verwendet“ zeigt die aufgenommenen Originale.

Gemeinsame Übersicht, Lobbyzeile, Listenheader und Leer-/Fehlerzustände stammen
aus `_lobby_overview.html`. Die sechs Standardlobbys verwenden `_lobby_room.html`;
Perfect behält seinen eigenen Raum mit Zettel, Buzzer und Spielerwänden. Host,
lesende Mitspieler, Bereitschaft, Belegung sowie Beitritt, Rückkehr und Ergebnisse
bleiben konkrete Varianten. Ganze Räume zeigen die vorhandenen Spielhintergründe.
Das Daily Quiz besitzt keine Mehrspielerlobby und bleibt entsprechend abgegrenzt.

`source_lobbies.py` verwendet denselben Originalquellen- und Vorschauweg wie die
übrigen aufgenommenen Komponenten. Werte und Listen sind neutrale feste Beispiele;
Beitritt, Start, Aktualisierung und automatische Speicherung laufen dort nicht.
Die ausgewählte Variante bleibt in Projektmappen und lokalen Übergaben erhalten.
Neue Editoranbindungen und die gemeinsame Optionsprüfung bleiben spätere Arbeit.

Bestand: [LOBBYS_BESTAND.md](../../docs/LOBBYS_BESTAND.md). Erneuern mit
`python deploy/audit_lobby_coverage.py`.

## Bildwerkstatt

Unter einer Bildart ein PNG-, JPEG- oder WebP-Bild vom PC importieren oder ein
Motiv aus der Bibliothek öffnen. Hintergründe, Titelbilder und Flyer zeigen
ausschließlich Import und Auswahl. Ein Import liegt unmittelbar gespeichert in
der jeweiligen Bibliothek und lässt sich direkt einem Projekt zuordnen.
Beim Import werden die ursprünglichen Bytes
unverändert als eigenes Original gesichert. Das Öffnen vorhandener Bilder
schreibt keine Kopie und verändert die Quelle nicht.

Bei Icons und Avatarbildern den Ausschnitt am Rahmen und an den Ecken ziehen, mit Pfeiltasten verschieben
oder über Pixelwerte einstellen. Freies Format, Originalverhältnis, 16:9, 4:3,
1:1 und 2:3 stehen zur Wahl. Ausgabebreite oder -höhe ändern jeweils proportional
die andere Seite; es entsteht keine unabhängige Streckung. Transparenz und die
Ausrichtung hochkant gespeicherter Fotos werden berücksichtigt.

Die Vorschau und gespeicherte Datei verwenden denselben Renderer in
`image_store.py`. Ein eindeutiger Name und die gewünschte Bildart bestimmen,
unter welchem Eintrag die Variante in der Bibliothek erscheint. Ein Original
kann verschiedene Ausschnitte für mehrere Bildarten liefern. Gespeicherte
Varianten lassen sich direkt zuordnen und später mit ihrem ursprünglichen
Ausschnitt erneut öffnen. Projekte und Übergaben halten die Bildkennung,
Prüfsumme, Maße, Quelldatei und vollständigen Bearbeitungswerte fest.

Importgrenze: 20 MB und 40 Millionen Bildpunkte; Ausgabe bis 4096 Pixel je Seite
als PNG. Animierte Dateien und SVG-Import sind nicht Bestandteil dieses Editors.
Vorhandene SVG-Bilder bleiben in der Bibliothek ansehbar und zuordenbar.
Die bereits lokal installierte Bildbibliothek Pillow 12.3.0 ist nun auch in den
lokalen Anforderungen festgehalten; es wurde kein neues Paket heruntergeladen.

## Vorhandene Spielbuttons

Unter Bibliothek → Buttons sind die tatsächlich in den verbundenen Spielvorlagen
stehenden Buttons registriert. Sammlung „Im Spiel verwendet“ und „Spiel / Einsatz“
filtern beispielsweise auf Guesstimate. Namen nennen Spiel, Einsatzort und
Beschriftung. Der Startseitenbutton „spielen“, Ergebnis- und Nachholaktionen sind
enthalten. Beispielzahlen und Beispielantworten enthalten keine Spielerinformationen.

`source_buttons.py` liest die Originalfragmente und ihre tatsächlichen Stylesheets.
Die Vorschau verwendet diese Quellen in einem nicht bedienbaren Rahmen; Spiel-
skripte und Formaktionen werden dort nicht ausgeführt. Die Grundimplementierung
der Spielbuttons wird nicht als neue HTML-/CSS-Seite nachgezeichnet. Der Rahmen
skaliert den vollständigen Ausschnitt proportional. Zuordnung zur Projektmappe
speichert Originalfragment, Quellort und Prüfsummen; Spielquellen werden dadurch
nicht geändert. Eine geänderte Stylesheetquelle wird bei der Vorschau erkannt.

144 Verwendungen sind aufgenommen: 137 HTML/CSS-Quellansichten einschließlich
dynamisch erzeugter Würfel-/Kniffel-/Kartenbadge-Buttons und gesonderter Kniffel-
Darstellung sowie sieben bereits gemeinsam gerenderte Conquest-Aktionen.
Die Erkennung folgt auch den gemeinsamen Lobbyübersichten und den tatsächlich
eingebundenen eigenen Skripten. Klickflächen auf Karten und Truppenmarken sind
ihren Spielelementen zugeordnet. Die vollständige Zuordnung und abgegrenzte alte
Quellen stehen in `docs/BUTTON_BESTAND.md` und `docs/BUTTON_BESTAND.json`. Alle registrierten Originale öffnen
im gemeinsamen Buttoneditor mit denselben Material-, Schrift-, Tiefen- und
Konturwerkzeugen wie eigene Entwürfe. Die separate CSS-Regleroberfläche ist ersetzt.
`button-profiles.json` enthält die aus den registrierten Quellen gelesenen Maße
und Eigenschaften. `profile_recipe.py` / `unified-import.js` übersetzen diese in
Form, Fläche, Tiefe und Beschriftung. Rezeptformat 4 ergänzt das gemeinsame Rezept
um Ausgangsmaße, Bild-/Schriftdaten und einen unveränderlichen Quellbezug.

`renderer.js`, `geometry.js` und `contour-editor.js` sind dieselben Komponenten für
alte und übernommene Entwürfe. Variable Formhöhe, physisch runde Ecken und eigene
Seitenwand-/Schriftfarben ergänzen den vorhandenen Editor. Randpunkte und Kerben
wirken auf Fläche und Tiefe mit derselben Kontur. Bisherige Rezeptformate bleiben
lesbar; Format 3 wird beim Öffnen in den gemeinsamen Editor übersetzt, ohne die
bestehende Datei umzuschreiben. `source-renderer.js` bleibt nur für unveränderte
Originalvergleiche und alte Bibliotheksvorschauen erhalten, ohne eigenen Editor.

Speichern erzeugt einen eigenen Stand. Die laufenden Spiele, deren Quellen,
Ereignisse und eingesetzte Originalbuttons werden nicht ersetzt. Die gemeinsame
Geometrie erhält das bisherige Verhalten alter Rezepte ohne neue Eigenschaften.

Die Bibliothek zeigt die 144 Quellverwendungen als 85 Modelle mit getrennt auswählbaren
Varianten. `button-models.json` hält die nachgewiesenen Originalgruppen fest:
gleicher Aufbau und gleiche berechnete Gestaltung nach neutralisierter Beschriftung,
bei 1000/390 px und normal, Hover, Druck, Fokus sowie gesperrt. Vorhandene Bewegungs-
definitionen werden mitverglichen. Änderungen an Quellmarkup oder CSS erzeugen neue
Quellkennungen und übernehmen keine alte Gruppierung ungeprüft. Bereits registrierte
Quellkennungen bleiben bei einer Erweiterung der Erkennung erhalten. Im Spielfilter
werden gemeinsame Komponenten über ihre Verwendungszuordnung gefunden, ohne sie
pro Spiel zu kopieren. Gespeicherte Rezepte
mit gleicher Gestaltung und anderer Beschriftung teilen ebenfalls ein Modell.
Originale, Varianten, Einsatzorte und Projektbezüge bleiben einzeln erhalten.
Abweichende Gestaltungen werden nicht vereinheitlicht. Der Nutzer verlangt vor
einer solchen Angleichung ausdrücklich eine Rückfrage.

`/button-editor/source-check.html` prüft alle 99 HTML-/CSS-Originale gegen den
Adapter und erzeugt die Modellnachweise. Es verändert nur eigene Vorschauframes.
Die sieben bestehenden Conquest-Rezepte verwenden weiterhin denselben bisherigen
Rendererpfad; die Originalanbindung wird ausschließlich in der Werkstatt registriert.

15 Elementbereiche stehen im Menü. Die Bestandsaufnahme kennt 19 Familien; die
vier weiteren werden im aufklappbaren Bestandsbereich genannt und nicht als
bereits verfügbare Editoren ausgegeben.

Die Bestandsaufnahme der tatsächlichen Spiele steht in
`docs/BAUKASTEN_BESTAND.md`; die nachprüfbaren Quellstellen und Prüfsummen in
`docs/WERKSTATT_BESTAND.json`. `python deploy/inventory_workshop_elements.py`
erneuert ausschließlich diesen Quellbericht, ohne App-Import, Datenbankzugriff
oder Serverkontakt. Quellstellen sind weder gerenderte Instanzen noch automatisch
gespeicherte editierbare Bibliothekselemente.

`workshop_catalog.py` ist die erweiterbare Elementliste. Darstellung, Kamera,
Licht und Objektbewegungen sind Projektentscheidungen. Beispiele und Hinweise
aus den gesammelten 2D-/3D-Elementen helfen bei der Auswahl; alles darf bis zum
Interview offenbleiben. Es wird kein Spiel oder Kameraverhalten automatisch gebaut.

## Daten, Quellen und Abgrenzung

`design-library/recipes/button-workshop/` enthält weiterhin die bisherigen
Button- und Formdateien. Generische Varianten liegen unter `elements/`,
Projektstände unter `projects/`, vollständige JSON-Übergaben mit lesbarem
MD-Begleittext unter `handoffs/`. Diese Ordner enthalten persönliche Daten,
sind von Git ausgeschlossen und gehören in die Datensicherung.

`images/originals/`, `images/variants/` und `images/records/` ergänzen die
unveränderten Originaldateien, erzeugten PNG-Dateien und Metadaten der
Bildwerkstatt. Auch `images/` ist von Git ausgeschlossen und Teil der
persönlichen Datensicherung. Keine Bilddatei wird beim Speichern überschrieben.

Jedes Speichern erzeugt einen eigenen Stand. Die stabile Projektkennung hält
mehrere Stände unter einem Projekt zusammen. Die Projektdatei speichert genaue
Elementkennungen und vollständige Momentaufnahmen. Bereits gewählte Varianten
ändern sich dadurch nicht nachträglich. Entfernen aus einer Mappe löscht
keine Bibliotheksdatei und lässt frühere Projektstände bestehen.

Schema 1 bleibt für bisherige Mappen und Entwürfe lesbar. Neue Projektmappen
verwenden Schema 2 mit einer Liste frei kombinierter Elemente statt acht
fest belegter Spielplätze. Alte Browser-Zwischenstände werden nicht automatisch
als neue Mappe oder Werkstattausstattung geladen.

`models.js` ist die gemeinsame Fabrik der allgemeinen Vorlagen; `scene.js`
zeigt diese einzeln. Aufgenommene Spielkomponenten nutzen ihre ursprünglichen
Vorlagen bzw. Fabriken über lokale Vorschauadapter. Three.js wird erst beim Öffnen eines räumlichen Werkzeugs geladen.
Die Bibliothek nutzt für Buttons unmittelbar den ursprünglichen Renderer.
Vorhandene Bildassets werden anhand registrierter Pfade und Prüfsummen zugeordnet.
Die lokale Three.js-Ausgabe stammt weiter aus dem vorhandenen Vendor-Bestand
mit MIT-Lizenz. Es werden keine fremden Theme-Modelle oder neuen Pakete bezogen.

Die Wurfprobe umfasst nur begrenzte Fallbewegung und Tischkontakt. Freies
Modellieren, allgemeine Objektphysik, weitere Editoren, konkrete Spielregeln und
Online-Integration bleiben eigene Arbeiten. Diese Werkstatt verändert keine
laufenden Spiele und verschickt keine Nachrichten.

## Gemeinsame Material- und Ansichtsauswahl

Unter `#properties` stehen zehn Materialfamilien mit Originalbeispielen sowie
drei Ansichtsbeispiele (2D, fester räumlicher Blick / 2,5D, 3D). Sechs Beispiele
verwenden den ursprünglichen Buttonrenderer, die übrigen die vorhandene
Playtable-Fläche, den Perfect-Zettel und die freigegebene flache Karte.
Verweise auf passende feste Schriftstile; keine beliebige Effektmatrix.

Materialwünsche können in der Projektmappe gesammelt werden. Sie sind keine
Elemente in `items` und verändern deren Schnappschüsse nicht. Format 2 erhält
den optionalen Schlüssel `surfaces` mit eingefrorenen Definitionen/Quellen.
Alte Mappen und ältere Clients erhalten vorhandene Wünsche; keine automatische
Migration. Ansicht, Licht und Bewegung nutzen die bisherigen Projektfelder.
Dies ist keine automatische Materialumstellung oder Abnahme von Editoroptionen.

`property_catalog.py` beschreibt die Quellen; `properties.js`/`.css` sind eine
gemeinsame Oberfläche für Übersicht und Projektwahl. Verlassen/Schließen entfernt
Vorschau-Iframes; neue Beispiele nutzen dieselbe proportionale Vorschaufunktion.
Siehe `docs/MATERIAL_DARSTELLUNG.md/.json`, `tests.test_workshop_properties`.

## Raumkulissen und Abschlussabgleich

`room_library.py` registriert neun ganze Original-Raumkonfigurationen in zwei
Grundmodellen 2D/3D. Conquests Wand, Möbel und Teppich bleiben zusammen, Brett
und Spieloberfläche separat. Die ursprüngliche `buildRoom`-Fabrik bleibt die
verbindliche Quelle. Die 15 bisherigen Bildmotive/privaten Entwürfe bleiben erhalten.

`completion_library.py` ergänzt fünf bisher fehlende ganze Quizfenstermodelle:
Fragenfenster, Rundenergebnis, Antwortübersicht, Ranglistenrahmen und Leerzustand.
30 begrenzte Beispiele, keine einzelnen Fragen. Ursprüngliche Fensterkennungen
bleiben erhalten. Insgesamt 35 Modelle / 114 Beispiele, davon 40 mit Verweisen
auf Fragenbanken und Steckbrief. Editoroptionen später.

Abgleich aller acht aktuellen Spiele, Quelle/Katalog und Prüfgrenzen:
`docs/WERKSTATT_ABSCHLUSSPRUEFUNG.md/.json`.
`python deploy/audit_workshop_completeness.py`
`python -m unittest tests.test_room_completeness tests.test_card_contents tests.test_workshop_collections`

## Prüfen

Schriften und Klänge: `media_library.py` bietet sieben passende Schrift-/
Oberflächenkombinationen und 13 kurze, neu recherchierte Kenney-CC0-Klänge.
Neue Bibliotheksbereiche, lokale Muster/Hörproben und Projektzuordnung; die
alten Buttonrezepte und Spielzuordnungen bleiben unverändert. Keine beliebige
Schrift-/Effektmatrix, keine automatische Spielumstellung. Im Button-Editor jetzt
ausdrücklich wählbar; weitere Baustein-Editoroptionen bleiben später.
Siehe `docs/KLAENGE_SCHRIFTEN_AUSWAHL.md` und `tests.test_media_library`.

Titelbilder, Flyer und Icons: `graphic_library.py` registriert unveränderte
Spielmotive, ursprüngliche Flyer-/Kachelvorlagen und endliche Symbolsätze.
Elf Modelle mit 28 festen Konfigurationen; einzelne Symbole nur innerhalb des
Satzes ansehen, als Ganzes sammeln. Persönliche Grußfolie bleibt ausgeschlossen.
Eigene Bildimporte/Entwürfe erhalten; Editoroptionen später.
Siehe `docs/BILDBAUSTEINE_BESTAND.md` und `tests.test_graphic_library`.

Figuren und Spielsteine: drei wiederverwendbare Formfamilien (Schach, Dame,
ursprüngliche Conquest-Truppenmarke), sieben feste Satz-/Ansichtskonfigurationen.
Rollen, Stil, Farben, Anzahl und Zustände sind Eigenschaften. Alle acht Spielbereiche
geprüft; persönliche Entwürfe und Spiele bleiben unverändert. Die Zahlenfläche
und der räumliche Sockel der Conquest-Marke gehören zu einem Baustein. Reine
Einsatzanzeigen bleiben im Anzeigenbereich. Editoroptionen später.
Siehe `docs/SPIELSTEINE_GRUNDLAGEN.md` und `tests.test_piece_library`.

`python -m unittest tests.test_image_workshop tests.test_workshop_collections tests.test_game_workshop tests.test_local_launcher`

Zusätzlich bestehen die Prüfungen der ursprünglichen Button-Werkstatt.
Für eine getrennte Bibliothek:
`--library-dir D:\Guesstimate\runtime\…\library --buttons-dir D:\Guesstimate\runtime\…\buttons`.

### Modelle gemeinsam prüfen

In der Buttonbibliothek öffnet „Guesstimate-Modelle vergleichen“ eine Vergleichsansicht
innerhalb derselben Werkstatt. Direkte Ansicht:
`/?review=buttons&source=game&game=Guesstimate#library/buttons`.
Sie zeigt Originalvorschauen, die vier Bausteine und die tatsächlichen Einsatzorte.
Die Antwortauswahl besitzt eine rein lokale Vorschau ihres vorhandenen Auswahlzustands.
Es gibt keinen Speichern-/Übernehmenweg für Designentscheidungen in dieser Ansicht.

Nutzerentscheidung vom 26.10.2026: Spielen/Fortsetzen und Ergebnis sind Umstände
derselben Startseitenaktion. Die explizite Gruppe steht unter `approved_groups` in
`button-models.json`; bei einer Neuerfassung automatischer Gruppen ist sie zu erhalten.
Quellkennungen und beide Funktionen bleiben getrennt erhalten. Aktuell 53 Quellmodelle,
neun davon bei Guesstimate; zehn Einsatzansichten zeigen die bisherigen Unterschiede.
Der Startseiten-Nachholbutton soll zum selben Stil passen. Seine Tiefe und Gestaltung
werden für den persönlichen Editortest des Nutzers ausdrücklich nicht automatisch
angeglichen. Alle weiteren Zusammenführungen bleiben Vorschläge.

### Gespeicherte Buttonmodelle zuordnen (28.10.2026)

Eigene Buttons besitzen unter **Ansehen → Verwendungen verwalten** eine gemeinsame
Zuordnungsübersicht; derselbe Dialog öffnet sich aus dem eingebetteten Editor im
Speicherschritt. Gekoppelte Startzustände ändern sich zusammen, unabhängige Quellen
werden einzeln gewählt. Aktuelle Zuordnung, Speicherdatum, zusätzliche Einsatzorte
und Rückkehr zum Original sind sichtbar. Die Einbindung gilt für das lokale
Hauptspiel über `deploy/run_local.py`, nicht für den Projektserver oder die
separate räumliche Conquest-Vorschau. Bedienweg, Umfang und Prüfgrenzen:
[`docs/BUTTON_VERWENDUNGEN.md`](../../docs/BUTTON_VERWENDUNGEN.md).

### Erster Fenstereditor (28.10.2026)

Unter **Gestalten → Fenster** lässt sich zunächst der originale
Guesstimate-Nachholdialog bearbeiten: **Form → Farben → Speichern**.
Fenstergröße skaliert das ganze Fenster, Eckenrundung und Rahmenstärke ändern
seine Hülle. Fläche, Überschrift, Erklärungstext und Rahmenfarbe sind separat
wählbar. Jeder Wert kann auf **Original** zurückgesetzt werden. Der Vergleich
zeigt das unveränderte Fenster und erhält die eigenen Einstellungen.

Die Arbeitsfläche ist unabhängig vom Entwurf hell, dunkel oder gerastert.
Originaltemplates und ihre Innenkomposition bleiben die Grundlage; Texte und
Buttons werden nicht neu aufgebaut. Der erste Editor ist bewusst auf dieses
Fenstermodell beschränkt. Andere Fenster bleiben in der Bibliothek auswählbar.

Eigene Stände liegen fortlaufend in `design-library/recipes/window-workshop/`.
Sie erscheinen unter **Bibliothek → Fenster → Meine Entwürfe**, können wieder
bearbeitet und in Projektmappen aufgenommen werden. Die Entwurfsadresse erhält
die genaue Kennung. Ungespeicherte Einstellungen werden pro Browsertab zur
Wiederaufnahme erhalten. Speichern ersetzt kein Fenster im laufenden Spiel;
eine Spieleinbindung für Fenster ist noch nicht eingerichtet.

Prüfung mit getrennten Daten: Form/Farben, proportionaler Aufbau mit erhaltenen
Kindbuttons, Originalvergleich und Rücksetzen, ungespeicherte Wiederaufnahme,
Speichern, Neuladen, Bibliotheksvorschau und Weitergestalten. 24 Tests für
Fensterentwürfe, Originalfenster und gemeinsame Werkstatt bestanden; Nachweise
unter `runtime/window-editor-20261028/`.

### Welche weiteren Werkzeuge sinnvoll sind

Der Nutzer hat am 28.10.2026 eigene Editoren für **Bretter, Figuren, Karten und
Avatare** festgelegt. Die frühere vorläufige Einordnung ist damit präzisiert.
Die Bewertung aller 17 Bereiche sowie recherchierte Grundlagen stehen in
[EDITOR_BEREICHE_2026-10-28.md](../../docs/EDITOR_BEREICHE_2026-10-28.md).
Andere Bereiche erhalten je nach Bedarf Auswahl, gemeinsame Bildwerkzeuge oder
Eigenschaften an bestehenden Vorlagen. Bestehende Werkzeuge bleiben erhalten.

### Brettereditor: erste Fassung

**Gestalten → Bretter → Neues Brett beginnen**. Form & Größe → Oberfläche & Bild
→ Felder → Speichern. Rechteckig oder rund, 2D oder 3D; Maße und Rahmen in cm,
Brettdicke in 3D. Farbe, Rahmen/Seitenwand und Feldfarbe sind unabhängig.
Ein Bild aus der Auswahl oder vom PC ergänzen, proportional einpassen oder
bewusst beschneiden. Optional Gitter, Zweifarbenmuster oder keine Felder;
Reihen, Spalten und Deckkraft getrennt. Die Vorschau lässt sich drehen und
von oben ansehen, ohne den gespeicherten Baustein zu ändern.

Eigene Bretter liegen fortlaufend in `design-library/recipes/board-workshop/`.
**Bibliothek → Bretter → Meine Entwürfe → Ansehen → Weitergestalten** öffnet den
gespeicherten Stand. Ungespeicherte Werte bleiben pro Browsertab erhalten.
Neue Bretter nutzen dieselbe bestehende `buildBoard`-Fabrik und Vorschauseite.
Originale und ältere Entwürfe bleiben erhalten. Speichern ersetzt kein Brett
in einem vorhandenen Spiel; Zonen, Einrastpunkte und Spielregeln folgen später.

Prüfungen: `python -X utf8 -m unittest tests.test_board_designs tests.test_board_library tests.test_game_workshop -v`.
Prüfdaten getrennt unter `runtime/board-editor-20261028/`.

Größenbedienung nach Nutzerrückmeldung: Größenregler statt alleiniger Zahlen;
genaue Werte unter **Genau einstellen**. Zunächst fester Vorschau-Maßstab mit
zuschaltbarer Vergleichskarte und Figur. **Ganzes Brett einpassen** aktiviert
die automatische Einpassung ausdrücklich. Hilfen und Ansichtszoom sind reine
Vorschau und werden nicht mitgespeichert.


### Figureneditor mit Größenvergleich

**Gestalten → Figuren & Spielsteine → Neuen Figurensatz beginnen**.
Form → Größe & Proportionen → Material & Farben → Speichern. Schachfiguren
und Damesteine, 2D/3D, unabhängige Proportionen und Farben für beide Seiten.
Die bestehende Modellfabrik wird wiederverwendet. Eine feste graue Figur und
eine Beispielkarte machen Größenänderungen direkt sichtbar; „Alles einpassen“
ist ausdrücklich wählbar. Genaue Prozentwerte liegen unter „Genau einstellen“.

Eigene Sätze erscheinen unter Bibliothek → Figuren & Spielsteine → Meine
Entwürfe und lassen sich weitergestalten. Speicherung fortlaufend unter
`design-library/recipes/piece-workshop/`. Vergleichsobjekte und Vorschaurolle
werden nicht mitgespeichert. Die Conquest-Marke bleibt zunächst als Original
verfügbar; kein Figurensatz wird durch Speichern in einem Spiel aktiviert.
Details: [SPIELSTEINE_GRUNDLAGEN.md](../../docs/SPIELSTEINE_GRUNDLAGEN.md).


### Eigene Kartensätze

**Gestalten → Karten → Neuen Kartensatz beginnen**. Format & Größe → Vorderseite
→ Rückseite → Karteninhalt → Speichern. Gemeinsame Gestaltung, getrennte Farben
für beide Seiten, eigene Titel/Texte/Zeichen je Karte, Hinzufügen/Duplizieren/
Entfernen innerhalb des Satzes. Die feste Vergleichskarte macht Größe sichtbar.
2D/3D verwenden dieselben Flächentexturen und die bestehenden gemeinsamen Körper.

Der ganze Satz wird fortlaufend unter `design-library/recipes/card-workshop/`
gespeichert und lässt sich in der Bibliothek weitergestalten. Alte Kartensätze
und persönliche Dateien bleiben erhalten. Eigene Karten ersetzen durch Speichern
keine Karten in bestehenden Spielen. Grenzen und Bedienweg:
[KARTEN_GRUNDLAGEN.md](../../docs/KARTEN_GRUNDLAGEN.md).

### Eigene Bildavatare

**Gestalten → Avatare**. Bild wählen → Ausschnitt → Rahmen → Größe → Speichern.
Vorhandene Motive oder eigene PNG-/JPEG-/WebP-Dateien; quadratischer Zuschnitt,
unabhängige Rahmen-/Hintergrundfarbe, vier Rahmenformen und sichtbare Stärke.
Ein fester Vergleich neben der eigenen Spieleranzeige macht Größenänderungen
sichtbar. Derselbe unveränderte Spielerbaustein zeigt auch den Conquest-Kontext
mit neutralen Beispielwerten. Genaue Prozentwerte unter „Genau einstellen“.

Vollständige Entwürfe liegen fortlaufend in `recipes/avatar-workshop/` und
lassen sich ansehen, weitergestalten sowie Projektmappen zuordnen. Originale
und frühere Stände bleiben erhalten. Speichern ersetzt keinen Profilavatar.
Bedienweg und Grenzen: [AVATAR_EDITOR.md](../../docs/AVATAR_EDITOR.md).
