# Lobbys und Lobbyübersichten in der lokalen Werkstatt

134 Quellvarianten in 7 gemeinsamen Modellen. Stand: 27.10.2026.

Bibliothek → Lobbys & Übersichten enthält nun die Originale aus allen sieben Mehrspielerspielen. Der vorhandene allgemeine Lobbyentwurf bleibt zusätzlich erhalten. Mit der Sammlung „Im Spiel verwendet“ werden nur die aufgenommenen Quellvarianten angezeigt. Spiel, Lobbyart und Text filtern die Ansicht. Konkrete Rollen und Zustände können mehreren Projektmappen zugeordnet und samt Original, Beispieldarstellung und Quellen lokal übergeben werden.

| Modell | Varianten | Spiele / Einsatz | Lobbyarten |
|---|---:|---|---|
| Gemeinsame Lobbyübersicht | 21 | Conquest, Guesstimate Party, Kniffel, Mäxchen, Perfect, Playtable, Würfeltisch | Lobbyübersichten |
| Gemeinsame Lobbyzeile | 53 | Conquest, Guesstimate Party, Kniffel, Mäxchen, Perfect, Playtable, Würfeltisch | Lobbyzeilen |
| Gemeinsamer Listenheader | 7 | Conquest, Guesstimate Party, Kniffel, Mäxchen, Perfect, Playtable, Würfeltisch | Erstellen und Rückwege |
| Gemeinsame leere Liste | 7 | Conquest, Guesstimate Party, Kniffel, Mäxchen, Perfect, Playtable, Würfeltisch | Leer- und Fehlerzustände |
| Gemeinsamer Aktualisierungshinweis | 7 | Conquest, Guesstimate Party, Kniffel, Mäxchen, Perfect, Playtable, Würfeltisch | Leer- und Fehlerzustände |
| Gemeinsamer Standardraum | 30 | Conquest, Guesstimate Party, Kniffel, Mäxchen, Playtable, Würfeltisch | Standardlobbys |
| Perfect · Raum mit Zettel und Buzzer | 9 | Perfect | Perfect-Raum |

## Gemeinsame Quellen und Varianten

Die Übersicht verwendet ausschließlich _lobby_overview.html mit ihren ursprünglichen Spielparametern. Spielkopf, Erstellen-Aktion, Liste, Rückweg, Zeilen und Leer-/Fehlerzustand stammen aus derselben Komponente. Eigene wartende oder laufende Lobbys, Beitritt, volle fremde Lobbys und Ergebnisse bleiben getrennte Zustände. Conquest ergänzt reservierte Plätze und Rückkehr sowie geschlossene Räume. Die Aktualisierungsfehler-Variante zeigt weiterhin die zuletzt geladene neutrale Beispielliste.

Die sechs Standardlobbys verwenden _lobby_room.html samt gemeinsamer Profilfenster. Hosteinstellungen, lesende Mitspieler, Einzelbelegung und volle Besetzung bleiben konkrete Varianten. Perfect verwendet unverändert den eigenen Raum aus nerd_mode.html mit Zettel, Buzzer und Spielerwänden: Punkte-/Zeitspiel, Host/Mitspieler, Bereitschaft, volle Besetzung und Start-Countdown. Es wird kein Standardraum in Perfect eingebaut.

Alle 10 verbundenen Makro-/Raumquellen sind zugeordnet. source_lobbies.py nutzt denselben Quellen-, Vorschau- und Speicherweg wie die anderen aufgenommenen Komponenten. Ganze Räume verwenden die vorhandenen Spielhintergründe; die Werkstatt passt nur den äußeren Vorschauplatz an und skaliert die ganze Komposition.

## Abgrenzung und spätere Aufgaben

- Das Daily Quiz hat keine Mehrspielerlobby oder Lobbyübersicht. Seine Startseiten- und Spielerkomponenten bleiben ihren bisherigen Elementarten zugeordnet.
- Ausschließlich neutrale feste Beispiele; keine echten Lobbys, Konten, Mitgliedschaften, Partien oder Ausrüstungsdaten gelesen.
- Vorschauen bleiben inert. Erstellen, Beitreten, Bereitschaft, Starten, Rückkehr, Autospeichern, Aktualisieren und Countdowns werden nicht ausgeführt.
- Aufgenommene Darstellungszustände sind keine Prüfung der Spielübergänge oder aller möglichen laufenden Situationen.
- Bisherige eigene Lobbyentwürfe und der vorhandene allgemeine Lobbyeditor bleiben verfügbar. Die aufgenommenen Spielquellen werden dadurch nicht editierbar.
- Gemeinsame Prüfung und Anpassung sinnvoller Editoroptionen bleiben spätere Arbeit.

## Aufnahme erneuern

`python deploy/audit_lobby_coverage.py`

Das Werkzeug liest ausschließlich lokale Quellen ohne App-/Datenbankimport oder Netzverbindung. Fehlende Zuordnungen führen zu einem fehlgeschlagenen Prüfergebnis.
