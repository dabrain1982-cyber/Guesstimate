# Werkstatt: Button-Editor und Bibliotheken

Verbindliche Entscheidung vom **29.10.2026**: Nur der **Button-Editor** bleibt
als Editor erhalten. Der Navigationspunkt heißt **Editor**. Sämtliche anderen
Editorbereiche und die **Projektmappe** sind aus der Werkstatt entfernt.
Die 17 Bibliotheksbereiche und ihre gespeicherten Inhalte bleiben für spätere
Recherchen erhalten. Alte Editoradressen anderer Elementarten öffnen deren
Bibliothek; dort werden keine Bearbeitungs- oder Projektzuordnungswege angeboten.
Material & Ansicht bleibt eine lesende Referenzsammlung.

Die folgende frühere Planung ist historisch und **kein Fortsetzungsauftrag**.
Insbesondere sind Bretter, Figuren, Karten und Avatare nicht als fertige,
vom Nutzer akzeptierte Editoren anzusehen. Eine weitere Entwicklung ist nicht
beauftragt.

## Frühere Planung vom 28./29.10.2026 (ersetzt)

Stand: 29.10.2026. Grundlage sind die vorhandenen 17 Werkstattbereiche, die
aktuelle Umsetzung und der ausdrückliche Nutzerwunsch: Bretter, Figuren,
Karten und Avatare erhalten eigene Editoren. Fenster sind nach der Rückmeldung
vom 29.10.2026 unter „Überhaupt sinnvoll?“ vorerst zurückgestellt. Nur der
Nachholdialog ist bearbeitbar; die Fensteraufgabe wurde damit nicht erfüllt.
Erste Fassungen für Bretter, Figuren, Karten und
Bildavatare sind eingerichtet; die gemeinsame praktische Abnahme steht an.

Die folgende Einordnung ist keine vollständige Abnahme vorhandener Werkzeuge.
Für die nicht ausdrücklich entschiedenen Bereiche ist sie eine Empfehlung.

| Bereich | Sinnvoller Umfang | Begründung / Stand |
| --- | --- | --- |
| Buttons | Eigener Gestaltungseditor | Form, Fläche, Schrift und Verhalten unabhängig gestalten. Bereits vorhanden. |
| Fenster | Überhaupt sinnvoll? – vorerst zurückgestellt | Nutzen eines eigenen Editors erneut offen. Nur der Nachholdialog ist bearbeitbar; die allgemeine Fensteraufgabe ist nicht erledigt. Vorerst keine weitere Umsetzung. Vorhandener Stand bleibt erhalten. |
| Bretter | Eigener Gestaltungseditor, entschieden | Form und Maße, 2D/3D, Fläche/Bild, optionale Felder, Rahmen und Dicke. Erste nutzbare Fassung jetzt eingerichtet. |
| Figuren & Spielsteine | Eigener Gestaltungseditor, entschieden | Grundform/Rolle, Proportionen, Größe, Farben und Oberfläche; als Satz gestalten. Kein eigener Editor je Figur oder Land. Erste Fassung für Schach und Dame mit festem Größenvergleich umgesetzt; Conquest-Marke vorerst Original. |
| Karten | Eigener Gestaltungseditor, entschieden | Gemeinsame Vorder-/Rückseite, Format, Schrift-/Bildfelder und kompletter Kartensatz. Gestaltung und Satzinhalt getrennt halten. Erste Fassung für eigene Sätze mit gemeinsamer Gestaltung und einzelnen Titel-/Text-/Zeichenfeldern eingerichtet; ursprüngliche Spielkartensätze bleiben Originale. |
| Avatare | Eigener Gestaltungseditor, entschieden | Erste Fassung für Bildwahl/-import, quadratischen Ausschnitt, Rahmenform/-farbe/-stärke, Hintergrund und Größe mit festem Vergleich in der echten Spieleranzeige. Gemeinsames Bildwerkzeug und unveränderte Spielerfabrik wiederverwendet. Profilzuordnung, freie Figurenmodellierung und Ausstattung bleiben offen. Bedienweg: [AVATAR_EDITOR.md](AVATAR_EDITOR.md). |
| Würfel | Modellauswahl mit Eigenschaften | Vorhandene 2D-/3D-Bausteine, Anzahl, Farbe, Größe und Aufdrucke. In 3D die vorhandene Wurfprobe nutzen. Kein eigener Modellierbereich nötig, solange diese Eigenschaften genügen. |
| Hintergründe | Auswahl und Bildimport | Fertiges Motiv wählen. Zuschnitt bei Bedarf im gemeinsamen Bildwerkzeug; kein eigener Zeicheneditor. Raumkulissen bleiben ganze Komponenten. |
| Titelbilder | Auswahl, Import und gemeinsames Bildwerkzeug | Vorhandene Motive verwenden. Freien Textsatz erst ergänzen, wenn eigene Titelkompositionen tatsächlich benötigt werden. |
| Icons | Auswahl plus gemeinsamer Zuschnitt | Endliche Symbolsätze oder eigene Bilddateien; keine einzelnen Zeichenprogramme je Symbol. |
| Flyer | Vorlagenauswahl und wenige Inhaltsfelder | Bild und Beschriftung in der bestehenden gemeinsamen Komposition. Ein eigener Layouteditor lohnt sich erst bei konkretem Wunsch nach anderen Kompositionen. |
| Eingaben | Bausteinauswahl und Eigenschaften | Text-/Zahlenfeld, Auswahl, Schalter oder Regler; danach Beschriftung, Grenzen, Vorgabe und Zustand. Verhalten ist wichtiger als freie Form. |
| Anzeigen | Vorlagenauswahl und Eigenschaften | Wert, Einheit, Farbe, Format; Datenquelle im späteren Spiel verknüpfen. Keine einzelnen Timer-/Punkte-Zeichenprogramme. |
| Spieleranzeigen & Pulte | Vorlagen und Ausstattung | Avatar, Namenspult und sichtbare Werte in der vorhandenen gemeinsamen Komponente. Avatar-/Bildwerkzeug wiederverwenden. |
| Lobbys & Übersichten | Vorlage und Ausstattung | Raum, Plätze, Hintergrund und gemeinsame Elemente konfigurieren. Keine freie zweite Lobbykomposition pro Spiel. |
| Schriften | Auswahl und Formatierung am Baustein | Schriftart, Größe, Farbe, Fett/Kursiv; Effekt bei Bedarf durch geeignete Schriftdatei. Kein Schriftzeicheneditor. |
| Klänge | Auswahl/Import, Hörprobe und Lautstärke | Passenden Klang am Ereignis zuordnen. Schneiden/Mischen erst bei tatsächlichem Bedarf, kein Audioeditor für eine Klangwahl. |

## Recherche und daraus abgeleiteter Brettaufbau

- [Tabletop Simulator: Custom Board](https://kb.tabletopsimulator.com/custom-content/custom-board/)
  beschreibt ein Brett als Bildfläche, deren Proportionen vom Bild abhängen,
  mit optionalem Gitter. Daraus übernehmen wir die einfache Bildwahl und
  getrennte Felder. Unser Editor erlaubt zusätzlich eine frei gewählte Fläche;
  Bilder werden proportional eingepasst oder ausdrücklich beschnitten.
- [Tabletopia: Game Board](https://help.tabletopia.com/knowledge-base/game-board/)
  führt Größe, Dicke und Form getrennt und unterscheidet grafische Fläche von
  magnetischen Ausrichtungshilfen. Daraus folgt für uns: sichtbare Feldmuster
  sind noch keine Spielregeln oder Bewegungsziele. Diese erste Fassung bietet
  rechteckige und runde Formen; freie Konturen sind noch nicht umgesetzt.
- [Tabletop Simulator: Custom Deck](https://kb.tabletopsimulator.com/custom-content/custom-deck/)
  behandelt Vorderseiten, gemeinsame oder eigene Rückseiten und den ganzen
  Satz. Das stützt den späteren Karteneditor als Satzwerkzeug mit gemeinsamer
  Gestaltung statt voneinander isolierter Einzelkarten.

Die Reihenfolge **Form & Größe → Oberfläche & Bild → Felder → Speichern** ist
unsere aus diesen Quellen und den bisherigen Bedienversuchen abgeleitete
Gestaltungsentscheidung. Sie ist keine Empfehlung einer Fremdsoftware.

## Erste Bretterfassung

- Einstieg: Gestalten → Bretter → Neues Brett beginnen.
- Rechteckige oder runde Spielfläche; echte Maßangaben in cm. Rahmen kommt außen
  hinzu. Für die vorhandene Werkstattgeometrie entsprechen 10 cm einer
  Szeneneinheit. Dies definiert keine Größenänderung bestehender Spiele.
- Fläche, Rahmen/Seitenwand und zweite Feld-/Linienfarbe bleiben unabhängig.
  Optional Bild aus den vorhandenen Motiven oder PNG/JPEG/WebP vom PC.
  Import nutzt dieselbe Bildablage und Originalprüfung wie die Bildwerkstatt.
- Keine Felder, Zweifarbenmuster oder Gitterlinien. Reihen und Spalten getrennt,
  eigene Deckkraft. Hinweis, wenn ein deckendes Muster das Bild verdeckt.
- 2D und 3D bleiben genau zwei Grundvarianten; Form, Bild und Gestaltung sind
  Eigenschaften. Drehen und Draufsicht verändern ausschließlich die Vorschau.
- Die bestehende `buildBoard`-Fabrik ist um die neuen Eigenschaften erweitert.
  Vorschau, gespeicherte Ansicht und Bibliothek verwenden dieselbe Fabrik und
  dieselbe Vorschauseite. Alte Feldbrettrezepte behalten ihren bisherigen Pfad.
- Speichern erzeugt fortlaufende Entwürfe unter
  `design-library/recipes/board-workshop/`. Bibliothek, Weitergestalten und
  Projektübergabe verwenden die genaue Variante. Alte Dateien werden nicht
  umgeschrieben. Ungespeicherte Werte bleiben pro Browsertab erhalten.
- Originale von Conquest, Playtable und Würfeltisch bleiben unverändert in der
  Bibliothek. Die bisherigen Feldbrettvorlagen lassen sich als eigener Entwurf
  beginnen. Neue Bretter sind noch keinem vorhandenen Spiel zugeordnet.

Freie Konturen, Sechseckfelder, Beschriftungs-/Zonenwerkzeuge, Einrastpunkte und
die Einbindung eigener Bretter in vorhandene Spiele bleiben mögliche spätere
Schritte. Diese Liste ist keine automatische Umsetzungsliste.

## Größen verständlich einstellen

Nutzerrückmeldung vom 28.10.2026: Für Größen außer Schriftgrößen hilft eine
nackte Zahl wenig, wenn ihre sichtbare Wirkung nicht einschätzbar ist. Daraus
folgt als Gestaltungsprinzip für die weiteren Editoren: sichtbare Größenregler
und geeignete relative Vergleiche; genaue Zahlen als ergänzende Feineinstellung.
Die bisher vorhandenen Editoren sind damit noch nicht pauschal nachgerüstet.
Reihen, Spalten oder Anzahlen bleiben sinnvolle Zahlenfelder.

Im Brettereditor bereits umgesetzt: Breite/Durchmesser, Höhe, Rahmen und Dicke
haben Regler und aufklappbare genaue Werte. Die Vorschau verwendet zunächst
einen festen Maßstab, sodass ein vergrößertes Brett tatsächlich größer wird.
Eine zuschaltbare Beispielkarte (6 × 9 cm) und Beispiel-Figur (4 cm hoch) dienen
ausschließlich dem Vergleich. Sie werden mit den bestehenden Karten-/Figuren-
Fabriken dargestellt, gehören nicht zum Brettentwurf und werden nicht in
Projektmappen aufgenommen. Es wird keine Spielfeldaufstellung daraus erzeugt.
Das sind Beispielmaße in der virtuellen Szene, keine Zentimeterkalibrierung
des jeweiligen Monitors.

„Ganzes Brett einpassen“ schaltet die automatische Einpassung ausdrücklich
wieder an. „Ansicht näher / weiter“ verändert nur den Vorschauabstand. Ansicht
und Vergleichshilfen bleiben außerhalb des gespeicherten Brettdatensatzes.
