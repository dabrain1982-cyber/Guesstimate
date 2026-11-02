# Logikprüfung der bisherigen Werkstattaufnahme

Stand: 27.10.2026. Geprüft wurden alle 17 bisherigen Elementbereiche sowie die
zwei zusätzlich inventarisierten Familien auf die Verwechslung von Bausteinen
und einzelnen Inhalten. Der anschließende Quellen-/Katalogabgleich aller acht
Spiele ist in [WERKSTATT_ABSCHLUSSPRUEFUNG.md](WERKSTATT_ABSCHLUSSPRUEFUNG.md)
belegt; im dort abgegrenzten aktuellen Bestand bestehen keine offenen
Elementzuordnungen. Editoroptionen und persönliche Gestaltungsabnahme sind offen.

Die verbindliche Trennung lautet:

1. **Baustein:** gemeinsame Darstellung und Verhalten, etwa Fragenfenster, Timer oder Kartenkörper.
2. **Endlicher Satz:** bekannte Ausstattung als Ganzes, etwa 32 Spielkarten oder 42 Conquest-Länder.
3. **Wachsender Datenbestand:** Fragen nach Steckbrief, verbunden mit einem Fenster; keine eigenen visuellen Bausteine je Frage.

## Ergebnis nach Bereich

| Bereich | Bisherige Aufnahme und Ergebnis |
|---|---|
| Buttons | 85 Modelle, 144 feste Quellbeispiele. Beschriftungen/Einsatzorte, keine Klickereignisse oder Nutzereingaben. |
| Fenster | 35 Modelle, 114 feste Quellbeispiele. Regeln, Inventare, Entscheidungen, Phasen sowie vollständige Quizfenster/Antwortübersicht/Ranglisten. Fragenfenster erhalten Datenquellen statt Fragenkopien. |
| Eingaben | 27 Modelle, 58 Beispiele. Feldtypen, Grenzen, Optionen und Zustände; keine eingegebenen Antworten als Elemente. |
| Anzeigen | 63 Modelle, 210 Beispiele. Neutrale Punkte, eingefrorene Zeiten und begrenzte Zustände; keine Historie pro Wert oder Sekunde. |
| Spieleranzeigen/Pulte | 13 Modelle, 146 Beispiele. Feste Rollen, Zustände und endliche Pultmotive; keine realen Personen oder Konten. |
| Lobbys/Übersichten | 7 Quellmodelle, 134 Beispiele, plus allgemeine Lobbyvorlage. Gemeinsame Räume, Listen und begrenzte Rollen; keine echten Lobbys als Datensätze. |
| Karten | Fehler korrigiert: zwei Grundbausteine, zwölf vollständige Sätze. Einzelkarten nur innerhalb eines Satzes. Keine registrierten Einzelfragen. Zwei ältere allgemeine Vorlagen bleiben. |
| Bretter | 2D und 3D als zwei Grundvarianten. Größe, Form und Bild sind Eigenschaften. Conquest-Brett, Playtable-Fläche und gemeinsame Fläche von Würfeltisch/Kniffel/Mäxchen aufgenommen; Quiz/Perfect ohne eigenes Brett. Keine Partien oder einzelnen Felder als Bausteine. |
| Figuren / Spielsteine | Drei Formfamilien mit sieben Konfigurationen: ursprüngliche Schach-/Damevorlagen und Conquest-Truppenmarke. Rollen, Stil, Farbe, Anzahl und Zustand als Eigenschaften; keine einzelnen Bestände je Land oder Partie. Acht Spiele geprüft. |
| Würfel | Genau zwei vorhandene Varianten aufgenommen: Würfeltisch mit Physik und flache Conquest-Anzeige. Anzahl, Aufdrucke und Farben sind Parameter; keine Einzelwürfe als Elemente. Editoroptionen später. |
| Hintergründe | 15 endliche Bildmotive plus neun ganze Raumkonfigurationen in zwei Grundvarianten 2D/3D. Conquests Wand, Möbel und Teppich bilden einen zusammengehörigen Raum. Ursprüngliche Kulissen aus allen acht Spielen zugeordnet; keine Spielstände. |
| Avatare | 19 endliche Motive, keine personenbezogenen Profileinträge. |
| Titelbilder | Acht bestehende Spielmotive und Mäxchen-Logo in zwei Bildfamilien. Wiederverwendete Motive einmal erfasst; reine Texttitel bleiben Teil ihrer Komposition. |
| Icons | Fünf endliche Symbolsätze (5/4/15/3/2 Motive) und App-Symbol. Ganze Sätze sammeln; einzelne Symbole nur in der Vorschau wählen. |
| Flyer | 13 feste Varianten in drei gemeinsamen Kompositionen aus Originalvorlagen. Persönliche Geburtstagsfolie ausgeschlossen; Bilder getrennt verwendbar. |
| Klänge | 13 neu recherchierte kurze CC0-Klänge in drei Zweckgruppen; lokal probehören und zuordnen. Keine Kopien pro Wiedergabeereignis. Alte Buttonzuordnungen erhalten. |
| Schriften | Sieben freie passende Schrift-/Oberflächenkombinationen, einschließlich Kreide, Stein und Metall. Feste Stile statt beliebiger Effektmatrix; lokale Fontdateien, alte Entwürfe erhalten. |
| Materialien | Gemeinsame Palette aus neun Materialfamilien mit Originalbeispielen. Als Projektwünsche speichern/übergeben; keine zusätzlichen Elemente und keine automatische Materialübertragung. Detailoptionen später. |
| Darstellung | Drei Originalbeispiele für 2D, festen räumlichen Blick (2,5D) und 3D. Vorhandene Projektentscheidungen für Ansicht, Licht und Bewegung; keine Registrierung einzelner Frames/Positionen oder zusätzlicher Grundmodelle. |

## Warum feste Beispiele bleiben

Der Abschlussabgleich hat die zuvor fehlende Conquest-Raumkulisse als ganze
Raumkonfiguration aufgenommen, außerdem die übrigen ursprünglichen Raumvarianten
und vollständige Quizkompositionen ergänzt. Keine weiteren offenen Zuordnungen
in den geprüften aktuellen Spielquellen. Umfang, Belege und Ausschlüsse stehen
im gesonderten Abschlussbericht. Material-/Darstellungswünsche sind jetzt gemeinsam als Projekteigenschaften
aufbereitet; siehe [MATERIAL_DARSTELLUNG.md](MATERIAL_DARSTELLUNG.md).
Die Umsetzung der Detailoptionen in Baustein-Editoren bleibt später.

Ein Timer mit neutralem Normal-/Dringlichkeitsbeispiel oder ein Lobbyplatz als
Gastgeber/Mitspieler ist ein überschaubares Zustandsbeispiel desselben Modells.
Solche Beispiele wachsen nicht mit den Spieldaten. Gleiches gilt für feste
Quellstellen, Spielphasen und endliche Ausstattungskataloge. Es wird dafür keine
zweite unabhängige Grundimplementierung geschaffen. Ihre Kennungen und vorhandene
Projektverweise bleiben erhalten. Weitere gestalterische Zusammenführungen werden
nicht ohne Sichtprüfung vorgenommen.

Die Quellfabriken `source_buttons.py`, `source_windows.py`, `source_inputs.py`,
`source_indicators.py`, `source_players.py` und `source_lobbies.py` erzeugen feste
Definitionen bzw. begrenzte Zustandskombinationen. `library_store.py` enthält die
generischen Vorlagen; `workshop_catalog.py` die Bildkatalog-Zuordnung.
`card_contents.py` liest ausschließlich endliche Spielausstattung.
`question_bindings.py` ergänzt nur Datenquellen und Feldverträge an Katalogkopien.
Persönliche Entwürfe und alte gespeicherte Ausschnitte werden nicht umgeschrieben.

Eine Katalogsperre lehnt automatisch erzeugte Einzelfragen ab. Die Regression
prüft zusätzlich, dass selbst ein simulierter Ausbau um 2.000 Fragen die
Katalogeinträge nicht verändert und der Katalog Fragenbanken gar nicht einliest.
Gemeinsame Komponenten- und Quellenkennungen bleiben bei der Ergänzung der
Verknüpfungen stabil. Ganze Sätze und Fensterverknüpfungen werden auf Speichern,
Wiederverwendung, erneutes Laden und Übergabe geprüft.

Maschinenlesbare Übersicht: [WERKSTATT_LOGIKPRUEFUNG.json](WERKSTATT_LOGIKPRUEFUNG.json).
Erzeugung: `python deploy/audit_workshop_semantics.py` mit getrennter leerer
Prüfbibliothek. Prüfbelege und Vorher-Prüfsummen liegen unter
`runtime/workshop-audit-20261027/`. Editoroptionen und Spielintegration bleiben offen.
