# Buttonbestand der lokalen Spiele

Aktuell lokal verbundene Seitenvorlagen, eigene Skripte und gespeicherte Conquest-Oberfläche; keine Live-Server-Prüfung.

144 registrierte Verwendungen, 85 Modelle. Gemeinsame Verwendungen werden je Spiel mitgezählt; die Spielzeilen sind daher nicht addierbar.

| Spiel / Bereich | Verwendungen einschließlich gemeinsamer Buttons | Modelle |
|---|---:|---:|
| Conquest | 48 | 34 |
| Gemeinsam | 24 | 20 |
| Guesstimate | 29 | 22 |
| Guesstimate Party | 20 | 17 |
| Kniffel | 22 | 20 |
| Mäxchen | 23 | 19 |
| Perfect | 25 | 21 |
| Playtable | 26 | 22 |
| Profil | 35 | 17 |
| Würfelspiele | 28 | 21 |
| Würfeltisch | 21 | 19 |
| Zugang | 2 | 1 |

Alle verbundenen nativen Buttonstellen und eigenen Erzeugungsfunktionen sind im JSON-Bericht einzeln zugeordnet. Ungeklärte Stellen: 0. Veraltete Erzeugungsnachweise: 0.

Klickflächen auf Länderkarten und Truppenmarken sind als Verbindungen zu Karten beziehungsweise Figuren/Spielsteinen erfasst. Sie werden nicht als zusätzliche, leere Buttonmodelle ausgegeben. Der nur in der Offline-Demo verwendete Neustartknopf und die alte, nicht eingebundene Conquest-Oberfläche sind ausdrücklich abgegrenzt. Normale Textlinks, Logos, Flyer, Aufklappüberschriften und Eingabefelder bleiben ihren Elementarten zugeordnet.

Originalmarkup, Styles und Spielaktionen bleiben unverändert. Die Vorschau zeigt versteckte Aktionen in einem sichtbaren Beispielzustand, ohne sie im Spiel freizuschalten. Registrierte Buttons öffnen im gemeinsamen Editor als eigene Entwürfe. Die Aufnahme ersetzt keine tatsächliche Spielkomponente und ist keine Prüfung sämtlicher Spielaktionen.

## Kandidaten für spätere Modelloptionen

- **Startseitenaktion und Nachholen:** Zielstil besprochen; Nachholbutton bleibt für den persönlichen Editortest unverändert.
- **Würfelauswahl: behalten / Ablage:** Eine Quellfunktion, kontextabhängig unterschiedliche Maße und Bewegung. Kandidat für Modelloptionen, keine Angleichung ausgeführt.
- **Conquest: Schließen / Auswahl aufheben:** Gleiche Aufgabe mit unterschiedlichen Größen und Kontexten. Kandidat zur gemeinsamen Optionsprüfung, keine Angleichung ausgeführt.

## Erneuern

`node deploy/capture_generated_buttons.mjs` liest die Originalfunktionen für dynamische Buttons und erzeugt inaktive Beispieldaten. `python deploy/audit_button_coverage.py` erneuert diesen Bericht. Beide arbeiten ohne App-Import, Datenbankzugriff oder Serverkontakt. Geänderte Erzeugungsquellen werden anhand ihrer Prüfsummen als veraltet erkannt. Profile und Modellnachweise werden anschließend über die bestehenden lokalen Prüfseiten erneuert; freigegebene Gruppen bleiben erhalten.
