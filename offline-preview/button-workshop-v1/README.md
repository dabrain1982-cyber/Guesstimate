# UI-002 · Lokale Button-Werkstatt

## Neuer geführter Ablauf ab 28.10.2026

Auf Nutzerentscheidung ersetzt die neue Schriftwahl die bisherige Kopplung von Schriftwirkung und Fläche. **Neuen Button erstellen** beginnt mit einer neutralen flachen Form. Schritte: Form; Oberfläche & Farbe; Beschriftung; Bewegung & Ton; Speichern. Die Vorschau bleibt erreichbar, alle Schritte sind direkt anwählbar. Formtiefe und Schlagschatten stehen bei Form, die stets sichtbare Seitenwandfarbe bei Oberfläche & Farbe. Eine Farbwahl schaltet die jeweilige Farbautomatik ausdrücklich auf Eigene Farbe.

Die sieben neuen `letter-*`-Schriftwahlen verwenden die vorhandenen Schriftdateien und passende Wirkungen, ohne die Fläche zu überschreiben. Alte `media-*`-Rezepte behalten ihre bisherige Darstellung; eine sichtbare Aktion trennt sie und übernimmt die Grundfarbe als eigene Farbfläche. Bei übernommenen Spielbuttons ist die Originalfläche erklärt. Farbe, Material oder Glanz bearbeiten die eigene Fläche unmittelbar; eine ausdrückliche Aktion ist ebenfalls vorhanden. Originalquellen werden dadurch nicht verändert.

Speichern erzeugt weiterhin einen eigenen Stand. Die genaue Entwurfsadresse wird aktualisiert, sodass Neuladen denselben gespeicherten Button öffnet. Beim Beginn eines weiteren Buttons lässt sich der vorherige Entwurf in diesem Tab wiederherstellen (auch ungespeicherte Werte). Eine allgemeine Aktiv-/Inaktiv-Auswahl für den Einsatz in bestehenden Spielen ist noch nicht implementiert. Der nächste Benutzerschritt ist das eigene Gestalten und Speichern; Spieleinbau folgt getrennt.

Prüfung: zwölf bisherige Editortests und fünf Medien-/Speicherprüfungen bestanden; Geometrie-/Schrift-/Proportionsprüfung bestanden. Getrennte Browserprüfung: neuer grüner Button mit cremefarbener Kreideschrift und eigener Seitenwand, Klickprobe, Speichern und Neuladen; Vorigen Entwurf fortsetzen; Shop-Vorlage violett/glänzend bearbeiten, speichern und neu laden. Prüfdaten ausschließlich unter `runtime/button-flow-20261028/`.

## Erste Optionsprüfung am 27.10.2026

Neun Guesstimate-Kernmodelle mit zehn Einsatzbeispielen geprüft, alle 27 Felder
an der Startseitenaktion berührt. Keine optische Angleichung ausgeführt.
Matt/Glanz ist bei bewahrter Originalfläche deaktiviert und erklärt; eine
eigene Fläche gibt die Option frei. Struktur ist im reduzierten Stil verborgen,
Lautstärke erst bei Klangwahl sichtbar. Werte bleiben erhalten. Die Tiefenanzeige
nennt 0 jetzt korrekt „ohne Tiefe“. Originale, Renderer und persönliche Rezepte
unverändert; kein bestandener Gesamttest sämtlicher 85 Modelle behauptet.

Belege: `docs/BUTTON_EDITOR_PRUEFUNG.md/.json`. Als Nächstes die bereits neuen
sieben festen Schriftstile und 13 kurzen Werkstattklänge mit dieser älteren
Buttonauswahl verbinden; keine automatische Umgestaltung bestehender Rezepte.

## Bedienung ab 26.10.2026

- **button bearbeiten:** links die Eigenschaften wählen, rechts einen einzelnen
  Testbutton ausprobieren und darunter den vollständigen Entwurf benennen und
  speichern. Die freie Formbearbeitung bleibt direkt erreichbar.
- **vorlagen & entwürfe:** eigene Bibliotheksansicht mit gespeicherten
  vollständigen Buttons, gespeicherten Formen und Startvorlagen. Eine Suche
  nach Namen durchsucht alle drei Bereiche. Die Zahl am Zugang zählt die
  persönlich gespeicherten Entwürfe und Formen.
- **Nur die Form als Vorlage speichern** unter der Formbearbeitung aufklappen,
  wenn ausschließlich ein wiederverwendbarer Umriss gewünscht ist. Beim
  Übernehmen einer Form bleiben Material, Schrift und Klang erhalten.
- Bewertungen und Notizen sind optional aufklappbar. Weitere Zustandsproben,
  Vorher-/Nachher-Vergleich und die Beispieltafel stehen unter **Button testen
  & vergleichen**, Hörbeispiele unter **Klänge anhören & auswählen**.
- Export und Einlesen stehen in der Bibliothek unter **Entwurfsdateien
  mitnehmen oder einlesen**. Eine eingelesene Datei öffnet die Bearbeitung;
  dauerhaftes Speichern bleibt ein eigener ausdrücklicher Schritt.

Die Bedienknöpfe der Werkstatt sind von den gestalteten Buttonmustern
unterscheidbar. Bibliotheksvorschauen sind reine Muster; je Karte gibt es
eine ausdrücklich beschriftete Öffnen-/Verwenden-Aktion. Das Umschalten der
beiden Hauptbereiche erhält den aktuellen ungespeicherten Entwurf. Erst das
Öffnen eines anderen Entwurfs bzw. einer Startvorlage ersetzt ihn.

Die folgende Funktionsübersicht beschreibt auch die weiterhin vorhandenen,
jetzt gezielt aufklappbaren Werkzeuge.

Der physische Button wird inzwischen auch im lokalen Conquest erprobt.
Grundgestaltung in `static/comic-button.css`, dieselbe Buttonfunktion und
derselbe Materialrenderer für Werkstatt und Spiel. Die bisherigen Tafeln bleiben
erhalten. Dies erklärt den Generator oder seine Materialwirkung nicht für fertig.

Start aus `D:\Guesstimate`:

```powershell
python -X utf8 offline-preview/button-workshop-v1/serve.py --port 8771
```

Vorschau: <http://127.0.0.1:8771/>. Der Dienst bindet ausschließlich an diesen
PC. Keine Verbindung zum Spielserver, kein Zugriff auf die Spieldatenbank.
Die erste Tafel UI-001 unter <http://127.0.0.1:8770/> bleibt eigenständig erhalten.

## Ausprobieren

- Unabhängig wählbarer Gestaltungsstil: **Comic** mit gemalten Farbflächen,
  vereinfachten Materialspuren und kräftigen Konturen; **Natürlich** mit
  ausgeprägter echter Materialstruktur; **Grafisch** mit flächigen Farben und
  abstrakten Holzlinien, Steinflächen oder Metallstreifen ohne Fototextur.
  Alle drei sind mit allen drei Materialien kombinierbar. Die bisherige
  gespeicherte Stilkennung `minimal` bleibt für Grafisch gültig.
  Comic ist die Voreinstellung; Stilwechsel erhalten Kontur, Material,
  Beschriftung und Bewegung. Der Generator ist nicht auf Comic festgelegt.
- Drei Startvorlagen: bemaltes Holz, Kreide auf Schiefer und gebrauchtes Metall.
- Material, matte/seidenmatte/glänzende Oberfläche, Struktur und Grundfarbe.
- Deutlich getrennte Formvorlagen: asymmetrisch/weich, ruhig gerundet und
  Scharten/Abplatzungen. Jede lässt sich frei weiterbearbeiten.
- Formeditor und Buttonfläche verwenden dieselbe Zeichenebene im Verhältnis
  560:180. Die Vorschau wird nicht mehr unabhängig in die Breite gezogen.
  Bei Platzmangel skalieren Kontur, Schrift, Rand und Druckweg gemeinsam.
  Das gilt für große Vorschau, Bibliotheksmuster und die über denselben
  Materialrenderer angebundenen Spielbuttons. Lange Beschriftungen werden
  innerhalb der unveränderten Form eingepasst.
- **Kontureditor:** 3–32 Randpunkte ziehen, per Doppelklick auf eine Kante
  oder Schaltfläche hinzufügen, auswählen und entfernen. X/Y-Werte eingeben,
  Rundung je Punkt einstellen, Änderungen rückgängig machen/wiederholen oder
  zur Vorlage zurückkehren. Pfeiltasten bewegen Punkte um 0,5 Prozentpunkte,
  mit Umschalt um 5. Überkreuzte, zu kleine oder ungültige Konturen werden
  abgefangen. Numerische Felder und Punktwahl ergänzen die Mausbedienung.
- Schriftform und aufgemalte, kreidige, gemeißelte, geritzte oder leuchtende
  Beschriftung. Diese Wirkungen sind CSS-Entwürfe, keine fertigen Bildmaterialien.
- Inter und Fredoka sind unter ihren echten Namen auswählbar. Hinzu kommen
  Cinzel (gemeißelt/graviert), Rock Salt (rau geritzt), Kalam (handschriftlich)
  und Share Tech Mono (Anzeige), zusätzlich die Systemschrift Courier New.
  „Passend zur Beschriftungswirkung“ verknüpft die Schriftwahl mit der Wirkung:
  etwa Cinzel für Gemeißelt und Rock Salt für Geritzt auf Holz/Stein. Eigene
  Schriftwahl schaltet auf manuell; alte Dateien behalten ihre gewählte Schrift.
  Neue Schriftdateien liegen ausschließlich lokal unter `assets/fonts/`, mit
  Lizenztexten und [Herkunftsangaben](assets/fonts/PROVENANCE.json).
- Druckweg, Klickdauer und Bewegungsgefühl. Ausgangswert ist **dezent**, 300 ms;
  die vorhandene Nutzerpräferenz für die Bewegung bleibt getrennt von den
  offenen Bewertungen der Form, Oberfläche, Schrift und Klänge.
- Optionale recherchierte Klangkandidaten aus lokalen Dateien: Reibung auf
  rauem Block, Holz/Planke, Robotertritt/Stampfer, Metallplatte, trockener Klick,
  Einrasten, Drop und digitale Bestätigung. Die Galerie spielt die ganze
  Aufnahme; am Button erklingt ein kurzer Ausschnitt beim Drücken. Loslassen
  erzeugt keinen zweiten Aufnahme-Anschlag. Standard bleibt ohne Ton.
  Bisherige Syntheseklänge sind ausdrücklich als alte Platzhalter bezeichnet.
- Dieselbe Komponente als großer Testbutton, sechs Zustände, A/B-Vergleich,
  Sammlungsvorschau und Beispiel einer Wertetafel. „Als A merken“ hält eine
  Vergleichsvariante bis zum nächsten Neuladen fest.

## Entwürfe aufheben

**Formvorlagen separat speichern:** unter dem Kontureditor einen Namen vergeben
und „Form als Vorlage speichern“ verwenden. Die Form erscheint unter
„Deine Formen“ und bleibt nach Neustart erhalten. „Form verwenden“ übernimmt
nur die Kontur, ohne Material, Schrift oder Bewegung zu ersetzen. Ältere Stände
bleiben beim erneuten Speichern erhalten. Diese Ablage verwendet denselben
erhaltenden Datenspeicher, mit `kind: shape`; Buttonentwürfe verwenden `button`.

**Grundform zurücksetzen** ersetzt die Kontur durch die Ausgangsvorlage. Es
speichert keine Form. Rückgängig stellt die Änderung innerhalb derselben
Bearbeitung wieder her; nach Laden eines anderen Entwurfs/Neuladen ist diese
temporäre Liste leer. Die frühere Beschriftung „zur Vorlage“ war missverständlich
und ist ersetzt.

„Entwurf speichern“ legt einen neuen Stand mit Name, allen Einstellungen,
Notiz und getrennten Bewertungen in
`D:\Guesstimate\design-library\recipes\button-workshop\` ab. Der Ordner
bleibt beim Schließen des Browsers oder Neustarten des Dienstes bestehen.
Vorhandene Stände werden weder überschrieben noch gelöscht. Geänderte Stände
erhalten einen Verweis auf ihren Ausgangsentwurf. Die persönlichen Dateien
sind von Git ausgeschlossen und sollten in die normale Datensicherung.

Erst gespeicherte Stände sind dauerhaft aufgehoben. Ungespeicherte Eingaben
und der gemerkte A-Vergleich gelten nur für die aktuelle Seite. Export erzeugt
eine einzelne JSON-Datei; „Datei einlesen“ prüft und lädt sie, speichert sie
aber erst nach einem ausdrücklichen Klick auf „Entwurf speichern“.

Kontur und Stil gehören zu jedem gespeicherten/exportierten Entwurf. Format 2
liest auch alte Dateien aus Format 1. Alte Konturpunkte werden als bearbeitbare
eigene Kontur übernommen, Comic ergänzt und die neue Stilbewertung offen
gelassen. Die ursprüngliche Datei wird dabei nicht verändert. Neue Materialbilder
können die Vorschau älterer Entwürfe anders aussehen lassen; deren alte
Einstellungen und Dateien bleiben erhalten.

Der Validator und die Bedienfelder verwenden denselben `catalog.json`.
Fehlerhafte Dateien werden abgewiesen; beschädigte Sammlungsdateien werden
gemeldet und unverändert liegen gelassen. Es gibt keine Löschfunktion.

## Gemeinsame Bausteine und Grenzen

`renderer.js` verwendet die bestehende Button-Funktion und das bestehende
Grund-CSS aus `../comic-ui-v1/`. Material und Schrift verändern deren
Parameter; sie erzeugen keine unabhängigen Innenaufbauten je Beispiel.
Die bestehende Funktion erhielt nur eine optionale Bewegungseinstellung;
ohne diese bleiben die ursprünglichen 300 ms und `ease-out` bestehen.
`geometry.js` erzeugt aus denselben Prozentpunkten und Rundungen die Kontur
für Editor und alle Buttongrößen. Es gibt keine zweite gezeichnete Buttonkopie.

Die ursprünglichen regelmäßigen Materialmuster wurden durch drei neu erzeugte
lokale Oberflächentexturen ersetzt: [Eiche](assets/oak-v1.png),
[Schiefer](assets/slate-v1.png) und [Stahl](assets/steel-v1.png).
Die Stilwahl steuert Konturwirkung, Lichtkante und Materialpräsenz getrennt.
Herkunft und vollständige Prompts: [PROVENANCE.json](assets/PROVENANCE.json).
Erzeugt mit dem eingebauten `image_gen`-Werkzeug; keine fremden Bilder importiert.
Die Materialwirkung bleibt bis zur Nutzerbewertung ein Entwurf.

Das Werkzeug ist eine lokale Gestaltungswerkstatt, keine Abnahme des Designs
und kein Einbau in die normalen Spiele. Das neue Party-Treppchen und die
weitere Überarbeitung der Spielanzeigen bleiben gesonderte offene Aufgaben.

## Prüfung

```powershell
python -m unittest discover -s offline-preview/button-workshop-v1 -p test_workshop.py -v
node offline-preview/button-workshop-v1/test_geometry.mjs
node offline-preview/button-workshop-v1/test_sound.mjs
```

Die zehn Speicherprüfungen behandeln zusätzlich Format-1-Kompatibilität,
erhaltene Originaldateien, eigene gerundete Konturen/Stile und abgewiesene
überkreuzte/ungültige Konturen. Geometrieprüfungen decken die Vorlagen,
Rundungsgrenzen und deutlich getrennten Konturen ab.
Audio-Verhalten prüft zusätzlich: genau ein Aufnahme-Anschlag pro Druck,
kein zweiter beim Loslassen, Wiederverwendung, Abbruch noch ladender Klänge
und verständliche Fehler. Reale Browserwiedergabe wurde zusätzlich geprüft.
Breitenübersicht: `/layout-check.html` (320, 390 und 800 px).
Für Browserprüfungen eine getrennte Ablage verwenden:

```powershell
python -X utf8 offline-preview/button-workshop-v1/serve.py --port 8772 --recipes-dir D:\Guesstimate\runtime\button-workshop-v1-20261025\fixture-recipes
```

Browserprüfung am 25.10.2026: Materialwechsel, A/B-Trennung, tatsächliche
Klick-Zeitreihe mit Rückkehr, Leertaste, deaktivierter Zustand, Speichern und
Wiederladen, Export/Import, zweiter erhaltener Stand, Sound-Auslösung ohne
Browserwarnungen sowie die schmalen Ansichten geprüft. Klangstatus technisch
bestätigt, die klangliche Qualität nicht nach Gehör abgenommen. Prüfdaten
bleiben getrennt von der persönlichen Sammlung.

Erweiterung ebenfalls im Browser geprüft: tatsächlicher Mauszug mit Rückgängig/
Wiederholen, numerische Änderung, Rundung, Hinzufügen/Entfernen und Doppelklick
auf eine Kante; Kreuzung abgewiesen. Stilwechsel erhalten die Kontur, A/B bleibt
getrennt. Eigene Kontur mit zehn Punkten und Stil nach echtem Dienstneustart
wieder geladen und per Datei exportiert/eingelesen. Bei drei Punkten ist
Entfernen deaktiviert. 320-px-Ansicht einschließlich tatsächlicher numerischer
Punktbearbeitung kontrolliert.

## Gemeinsame Schriftstile und kurze Klänge (28.10.2026)

Unter „Schrift & Wirkung“ stehen zusätzlich die sieben passenden festen
Schrift-/Oberflächenstile der gemeinsamen Medienbibliothek bereit. Ein Stil
verbindet seine geeignete Schrift, Wirkung und Fläche; nicht wirksame freie
Material-/Schrifteinstellungen werden verborgen und behalten ihre Werte.
Eine bisherige Schrift stellt die freie Auswahl wieder her. Bild-/Symbolbuttons
werden nicht automatisch mit Textstilen überdeckt.

Unter „Klang“ und in den Hörbeispielen stehen 13 kurze Werkstattklänge bereit,
nach Bedienung, Tischaktionen und Spielereignissen gruppiert. Neue kurze Proben
werden vollständig gespielt. Bisherige Klangkandidaten, Rezeptkennungen und
Standardwerte bleiben erhalten. Keine automatische Umgestaltung oder
Spielzuordnung. Font-/WAV-Dateien aus der gemeinsamen Medienbibliothek werden
direkt wiederverwendet; der ursprüngliche Spielrenderer und die Klangengine
bleiben unverändert. Dieselbe Werkstatt-Erweiterung zeigt die neuen Stile im
Editor, in gespeicherten Bibliotheksvorschauen und in Detailansichten.

Siehe `docs/BUTTON_MEDIEN_INTEGRATION.md` und die Prüfungen
`tests.test_button_media` sowie `tests/test_button_media_sound.mjs`.

## Bisherige Klangrecherche und Hörbeispiele

Die zehn Kandidaten sind nach den Angaben der Urheber ausgewählt, nicht nach
Gehör abgenommen. Ob ihre Wirkung dem gewünschten Button entspricht, bleibt
bei der Hörprobe zu entscheiden. Insbesondere ist der Stein-Kandidat die
Aufnahme eines über einen Betonblock gezogenen Objekts, keine belegte Aufnahme
zweier natürlicher Felsen. Ein kurzer Plankenanschlag und ein leichterer
Holzanschlag stehen zum direkten Vergleich bereit. Robotertritt und Stampfer
sind gestaltete mechanische Effekte aus demselben Quellenpaket.

| Richtung | Quelle | Dateien/Lizenz |
|---|---|---|
| Raues Reiben als Stein-Kandidat | AntumDeluge, [Scrapes](https://opengameart.org/content/scrapes) | CC0 |
| Holz, Planke, Metallplatte | Kenney, [Impact Sounds](https://kenney.nl/assets/impact-sounds) | CC0 |
| Robotertritt und schwererer Stampfer | Lee Barkovich, [Robotic mechanic step sounds](https://opengameart.org/content/robotic-mechanic-step-sounds) | CC-BY 3.0; sichtbare Attribution an den Hörbeispielen |
| Klick, Einrasten, Drop, Bestätigung | Kenney, [Interface Sounds](https://kenney.nl/assets/interface-sounds) | CC0 |

Originaldateien, Lizenztexte, vollständige Quellen, Dauern und Prüfsummen sind
unter `assets/audio/` abgelegt: [Credits](assets/audio/CREDITS.md) und
[Klangkatalog](assets/audio/catalog.json). Die Dateien sind unverändert;
Button-Ausschnitte und Ein-/Ausblendung entstehen erst bei der Wiedergabe.

## Oberflächen aus dem Spielebestand

Die Materialauswahl umfasst zusätzlich zu Holz, Stein und Metall eine Farbfläche,
einen zweifarbigen Verlauf und eine durchscheinende Fläche. Grundlage sind die
vorhandenen Lobbyaktionen, Karten-/Würfelaktionen und Nebenaktionen; die Belege
stehen in `docs/WERKSTATT_BESTAND.json`. Dazu gibt es drei neue Startvorlagen.
Diese zeigen Oberflächen in der gemeinsamen Werkstattform und sind keine bereits
übernommenen Originalbuttons mit ihrer vollständigen Funktion und Anordnung.

Die zweite Farbe erscheint beim Verlauf, die Deckkraft bei durchscheinenden
Flächen. Spuren und Struktur werden für diese drei Flächen nicht angeboten;
Glanz ist bei durchscheinenden Flächen ebenfalls ausgeblendet. Beschriftung und
Kontur bleiben bei veränderter Flächendeckkraft sichtbar. Eine automatische
Materialklang-Zuordnung wird nur für Holz, Stein und Metall angeboten; bei anderen
Flächen kann ein Klang gezielt gewählt werden.

Neue Verlaufs- und Deckkraftwerte sind beim Lesen älterer Entwürfe optional.
Bestehende Einstellungen und Dateien bleiben erhalten. Die drei bisherigen
Materialdefinitionen und die gemeinsame Konturgeometrie werden weiterverwendet.
Bildknöpfe wie der Perfect-Buzzer sind als eigener Übernahmebedarf erfasst und
werden nicht durch eine erfundene Materialfläche ersetzt. Form, Schrift und
Bewegung sowie konkrete Spieleinbindungen bleiben Gegenstand der weiteren Prüfung.

## Schriftgröße und Tiefe

Unter Schrift & Wirkung verändert „Schriftgröße“ die Beschriftung unabhängig von
der Buttonfläche. „Buttongröße“ steht unter Form & Kontur und skaliert den gesamten
Entwurf. Beim Anzeigen in anderen Größen werden weiterhin alle Teile proportional
skaliert; lange Beschriftungen werden bei Platzmangel eingepasst.

Die Seitenwände verwenden eine abgedunkelte Materialfarbe. „Schlagschatten“ ist
ein eigener weicher Schatten außerhalb des Buttons und lässt sich auf null stellen.
Neue Werte font_scale und shadow sind beim Lesen bisheriger Rezepte optional.
Der gemeinsame Renderer verwendet diese Einstellungen in Werkstatt, Bibliothek
und bestehenden angebundenen Spielbuttons; bisherige Entwurfsdateien bleiben erhalten.

## Vorschauhintergrund ab 28.10.2026

Über dem Testbutton sind Hell (neuer Anfangswert), Prüfraster, Dunkel und Eigene Farbe wählbar. Die Wahl wird als separate Browserpräferenz aufbewahrt; sie gehört nicht zum Rezept und macht einen gespeicherten Entwurf nicht ungespeichert. Der zusätzliche dekorative Bodenschatten der Vorschau wurde entfernt. Die Schatten und Seitenwand des eigentlichen Buttons bleiben unverändert. Hell, Raster und freie Farbe einschließlich Neuladen mit dem persönlichen Entwurf „Guesstimate · Startseite · spielen → Test 1“ im Browser geprüft; keine persönliche Datei gespeichert oder geändert.

## Vollständiger Start statt leerer Zwischenansicht

Der gemeinsame Editor hält die Bearbeitungsfläche verborgen, bis Einstellungen, Vorschau, Formwerkzeug und der angeforderte Entwurf geladen sind. Davor erscheint eine Ladeanzeige. Import- und Startfehler sowie ein länger ausstehender Start zeigen eine Meldung mit „Editor erneut laden“; ein unbekannter Entwurfsverweis fällt nicht mehr still auf einen neuen Button zurück. Der Bootstrap gilt für eigenständige und eingebettete Ansicht. Mit einer getrennten Prüfumgebung ein absichtlich fehlschlagendes Modul, die Auffangmeldung, erneutes Laden und anschließendes Speichern geprüft. Persönlichen Test-1-Entwurf aus der Bibliothek über Weitergestalten einschließlich Form- und Speicheransicht geprüft. Keine persönliche Datei geändert.

## Gespeicherte Modelle im Spiel verwenden (28.10.2026)

Im Schritt **5 · Speichern** öffnet **Verwendungen verwalten** die gemeinsame
Übersicht für gespeicherte vollständige Buttons. Bei ungespeicherten Änderungen
zuerst speichern. Einsatzgruppen wählen, ihre aktuelle Zuordnung prüfen und
**Zuordnung übernehmen** drücken. **Original wiederherstellen** setzt ausgewählte
Gruppen zurück. Die Zuordnung gilt für das lokale Hauptspiel; weitere neue
Entwurfsstände werden bewusst erneut zugeordnet. Einzelheiten und Prüfgrenzen
stehen in [`docs/BUTTON_VERWENDUNGEN.md`](../../docs/BUTTON_VERWENDUNGEN.md).

## Beschriftung: Schriftart, Fett und Kursiv (28.10.2026)

Im Schritt **3 · Beschriftung** gibt es eine direkte Schriftwahl sowie die
unabhängigen Schalter **Fett** und **Kursiv**. Die frühere Wirkungsauswahl und
ihre Schriftkopplung werden nicht mehr angeboten. Eine neue Schriftwahl setzt
die alte Beschriftungswirkung ausdrücklich auf Klar zurück. Ältere gespeicherte
Entwürfe behalten ihre Werte; eine enthaltene alte Wirkung wird erklärt.

**Kreideschrift · Cabin Sketch** verwendet die Struktur der echten Schriftdatei
anstelle des früheren Streifenfilters. Regulär und Fett werden als lokale
Schriftschnitte geladen; dasselbe gilt für Stardos Stencil. Beide stammen aus
dem offiziellen Google-Fonts-Bestand und liegen mit OFL-Lizenz und Herkunft
unter `assets/fonts/`. Schräge Schrift wird bei fehlendem eigenen kursiven
Schnitt vom Browser geneigt.

Die optionalen booleschen Rezeptwerte `font_bold` und `font_italic` werden nur
bei bewusster Betätigung gespeichert. Bei ihrem Fehlen bleibt die bisherige
Darstellung erhalten. Der gemeinsame Medienadapter setzt die Formatierung in
Editor, Bibliothek und lokaler Spieleinbindung um. Unveränderte alte Entwürfe
werden nicht automatisch neu geschrieben.
