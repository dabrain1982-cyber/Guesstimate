# Eingaben in der lokalen Werkstatt

58 Einsatzvarianten in 27 Modellen. Stand: 26.10.2026.

Bibliothek → Eingaben bietet Suche sowie Filter nach Spiel und Eingabeart. Gemeinsame Modelle halten Beschriftungen, Grenzen und Zustände als einzeln auswählbare Varianten fest. Eine konkrete Variante kann in mehreren Projektmappen gesammelt und mit vollständigem Original, gerendertem Beispiel und Quellen übergeben werden.

| Modell | Varianten | Spiele / Einsatz | Eingabearten |
|---|---:|---|---|
| Zugang · Eingabefeld | 5 | Zugang | Text und Zahlen |
| Gemeinsames Lobbytextfeld | 2 | Conquest, Guesstimate Party | Text und Zahlen |
| Gemeinsame Lobbyauswahl | 4 | Guesstimate Party, Playtable, Würfeltisch | Auswahlfelder |
| Lobby · Zahlenfeld | 1 | Playtable | Text und Zahlen |
| Conquest · Siegziel wählen | 1 | Conquest | Auswahlfelder |
| Conquest · Armeefarben wählen | 1 | Conquest | Auswahlfelder |
| Perfect · Lobbyname | 1 | Perfect | Text und Zahlen |
| Perfect · Spielende wählen | 1 | Perfect | Auswahlfelder |
| Perfect · Zielwert auswählen | 2 | Perfect | Auswahlfelder |
| Quiz · Antwortauswahl | 8 | Guesstimate, Guesstimate Party | Auswahlfelder |
| Quiz · Schätzwert | 2 | Guesstimate, Guesstimate Party | Text und Zahlen |
| Quiz · Reihenfolge | 2 | Guesstimate, Guesstimate Party | Zusammengesetzte Auswahl |
| Quiz · Zuordnung | 2 | Guesstimate, Guesstimate Party | Zusammengesetzte Auswahl |
| Perfect · Antwort verfassen | 1 | Perfect | Text und Zahlen |
| Perfect · Antwort wählen | 2 | Perfect | Auswahlfelder |
| Perfect · Weitere richtige Antworten anerkennen | 2 | Perfect | Auswahlfelder |
| Playtable · Punkte bieten | 1 | Playtable | Regler |
| Playtable · Karten pro Person | 1 | Playtable | Regler |
| Playtable · Gemeinsamer Notizzettel | 1 | Playtable | Text und Zahlen |
| Würfelspiele · Kameraschalter | 6 | Kniffel, Mäxchen, Würfeltisch | Schalter |
| Mäxchen · Ansage wählen | 1 | Mäxchen | Auswahlfelder |
| Profil · Schalter | 2 | Profil | Schalter |
| Conquest · Blickwinkel einstellen | 1 | Conquest | Regler |
| Conquest · Land mit Tastatur auswählen | 1 | Conquest | Auswahlfelder |
| Conquest · Truppenanzahl mit Minus und Plus | 3 | Conquest | Zusammengesetzte Auswahl |
| Conquest · Truppenregler | 3 | Conquest | Regler |
| Conquest · Angriffswürfel wählen | 1 | Conquest | Auswahlfelder |

## Herkunft und gemeinsame Vorschau

source_inputs.py verwendet denselben Originalquellen- und Vorschauweg wie source_windows.py. Originalvorlagen, umgebende Beschriftungen, Styles und Schranken wie min, max, maxlength, required oder disabled werden mit neutralen Beispieldaten aufgenommen. Eine gemeinsame Grundklasse begründet ein Modell; unterschiedliche Einsatzgestaltungen bleiben Varianten. Die Spiele und ihre Eingabekomponenten werden nicht umgebaut oder nachgezeichnet.

Der Bericht ordnet alle 45 nativen bzw. rollenbasierten Quellkontrollen in den verbundenen Vorlagen und der aktuellen Conquest-Oberfläche zu. Schleifen erzeugen im Spiel mehrere Instanzen; diese Zahl zählt Quellstellen. Zuordnen und Sortieren sind zusätzlich als zusammenhängende Auswahlen aufgenommen.

## Grenzen und spätere Aufgaben

- Die Vorschau ist inert. Eingaben, Sortieren, Validierung, automatisches Speichern und Spielaktionen werden nicht ausgeführt.
- PIN-Felder bleiben leer. Keine Zugangsdaten, Spielerantworten, Konten oder Spielstände werden gelesen.
- Versteckte Übertragungsfelder und CSRF-Werte sind keine gestaltbaren Bibliothekselemente.
- Native Auswahllisten und Regler behalten die Darstellung des jeweiligen Browsers.
- Zustandsabhängige Grenzen werden im Spiel berechnet; aufgenommen sind die kenntlich gemachten neutralen bzw. ursprünglichen Zustände.
- Ein Eingabeeditor und die gemeinsame Prüfung sinnvoller Editoroptionen bleiben spätere Arbeit.

## Aufnahme erneuern

`python deploy/audit_input_coverage.py`

Erneuert diesen Bericht und EINGABEN_BESTAND.json ausschließlich aus lokalen Quellen. Fehlende Zuordnungen führen zu einem fehlgeschlagenen Prüfergebnis.
