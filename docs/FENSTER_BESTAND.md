# Fenster in der lokalen Werkstatt

84 Verwendungen in 30 gemeinsamen Modellen. Stand: 26.10.2026.

Unter Bibliothek → Fenster nach Spiel, Fensterart oder Text suchen. Ansehen öffnet die konkrete Variante; bei gemeinsamen Modellen bleiben Spiel, Inhalt und Zustand einzeln auswählbar. Jede Variante lässt sich mehreren Projektmappen zuordnen. Projektstände und Übergaben enthalten vollständige Momentaufnahmen mit Originalfragment, gerendertem Beispiel, Quellen und Prüfsummen.

| Modell | Varianten | Spiele / Einsatz | Fensterarten |
|---|---:|---|---|
| Gemeinsamer Regeldialog | 8 | Conquest, Guesstimate, Guesstimate Party, Kniffel, Mäxchen, Perfect, Playtable, Würfeltisch | Regeldialoge |
| Guesstimate · Verpasste Runden wählen | 1 | Guesstimate | Entscheidungsfenster |
| Profilinventar | 4 | Profil | Inventare |
| Shopauswahl | 4 | Shop | Inventare |
| Gemeinsame Lobbyeinstellungen | 12 | Conquest, Guesstimate Party, Kniffel, Mäxchen, Playtable, Würfeltisch | Aktionsflächen |
| Perfect · Einstellungszettel | 3 | Perfect | Aktionsflächen |
| Perfect · Spielkarte | 7 | Perfect | Aktionsflächen, Entscheidungsfenster |
| Perfect · Gastgeber-Aktionen | 3 | Perfect | Aktionsflächen |
| Quiz · Antwortfläche | 10 | Guesstimate, Guesstimate Party | Aktionsflächen |
| Quiz · Antwortauflösung | 6 | Guesstimate, Guesstimate Party | Aktionsflächen |
| Playtable · Eigener Kartenbereich | 1 | Playtable | Inventare |
| Playtable · Karten austeilen und verwalten | 1 | Playtable | Aktionsflächen |
| Playtable · Punkte bieten | 1 | Playtable | Aktionsflächen |
| Playtable · Potübernahme bestätigen | 1 | Playtable | Entscheidungsfenster |
| Playtable · Gemeinsamer Notizzettel | 1 | Playtable | Aktionsflächen |
| Playtable · Tisch verlassen oder beenden | 1 | Playtable | Aktionsflächen |
| Würfelspiele · Aktionspult | 3 | Kniffel, Mäxchen, Würfeltisch | Aktionsflächen |
| Würfelspiele · Behaltene Würfel | 2 | Kniffel, Würfeltisch | Inventare |
| Kniffel · Kniffelblock | 1 | Kniffel | Aktionsflächen |
| Conquest · Geheimer Auftrag | 1 | Conquest | Entscheidungsfenster |
| Conquest · Kompakte Zugleiste | 1 | Conquest | Aktionsflächen |
| Conquest · Angriff vorbereiten | 1 | Conquest | Aktionsflächen |
| Conquest · Kampfergebnis | 1 | Conquest | Aktionsflächen |
| Conquest · Zugbeginn | 1 | Conquest | Aktionsflächen |
| Conquest · Neue Länderkarte | 1 | Conquest | Inventare |
| Conquest · Länderkarten tauschen | 1 | Conquest | Aktionsflächen |
| Conquest · Endstand und nächste Partie | 1 | Conquest | Aktionsflächen |
| Conquest · Ansicht erneut laden | 1 | Conquest | Aktionsflächen |
| Conquest · Truppen verschieben | 3 | Conquest | Aktionsflächen |
| Conquest · Eigene Länderkarten | 2 | Conquest | Inventare |

## Quellen und Gruppierung

Gemeinsame Modelle verweisen auf vorhandene Komponenten bzw. ihre gemeinsame CSS-Grundklasse. Unterschiedliche Inhalte und Gestaltungen bleiben getrennte Varianten; ähnliche Optik allein führt nicht zur Zusammenführung. Die Spiele werden dadurch nicht umgebaut.

Die Aufnahme folgt den aktuell verbundenen Seitenvorlagen und der aktuellen Conquest-Tischoberfläche. Alle dort gefundenen HTML-Dialoge sind zugeordnet. Regelvarianten für Perfect und Conquest stammen aus Übersicht bzw. Lobby; deren eigenständige laufende Spielseiten enthalten diesen Dialog nicht. Playtable, Würfeltisch und Kniffel verwenden im vorhandenen allgemeinen Regeldialog den bisherigen allgemeinen Text. Die Aufnahme ergänzt keine neuen Regeln.

Die Vorschau verwendet die ursprünglichen Vorlagen, Makros und Styles mit neutralen Beispieldaten. Dynamische Karten, Würfel und Kniffelblock werden aus den tatsächlichen DOM-Fabriken erfasst. Nur Platzierung und die proportionale Skalierung der gesamten Vorschau werden an die Werkstatt angepasst. Interne responsive Kompositionen werden nicht kopiert.

## Grenzen und spätere Aufgaben

- Noch kein Fenstereditor; dessen sinnvolle Optionen klären wir später gemeinsam.
- Vorschauen sind nicht bedienbare Komponentenbeispiele. Spielaktionen, Kontenanbindung und laufzeitabhängige Button-Mounts werden dort nicht ausgeführt.
- Native Bestätigungsfenster des Browsers in Perfect und Playtable sind Verhalten des Browsers und keine frei gestaltbare HTML-Fenstervorlage.
- Das alte Conquest-Inventar aus static/conquest-table.js ist nicht eingebunden und bleibt als Altbestand abgegrenzt.
- Porträts, vollständige Lobbys und Spielflächen, einzelne Karten, Eingabefelder, Timer und Ladeanzeigen behalten ihre eigenen Elementfamilien.

## Aufnahme erneuern

`node deploy/capture_generated_windows.mjs`

`python deploy/audit_window_coverage.py`

Die erste Anweisung erfasst ausschließlich reine lokale DOM-Fabriken in einer Umgebung ohne Netzwerk oder Spielhandler. Die zweite erneuert diesen Bericht und FENSTER_BESTAND.json. Anwendung und Spieldatenbanken werden nicht importiert oder geöffnet.
