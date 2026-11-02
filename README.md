# Stormseed´s Guesstimate – tägliches Quiz

Ein mobil optimiertes Quiz für bis zu 100 Personen: Login, eine tägliche Runde mit fünf Kategorien, normiertes Scoring und eine fortlaufende Gesamtrangliste.

## Auf diesem PC starten

**Guesstimate-starten.cmd** öffnet das lokale Spiel, **Werkstaetten-starten.cmd**
die Sammlung der Gestaltungswerkzeuge. Beide Dateien per Doppelklick öffnen.
Laufende passende Dienste werden weiterverwendet. Anleitung und Datenablage:
[LOKAL_STARTEN.md](LOKAL_STARTEN.md). Der Zugriff bleibt auf diesen PC begrenzt.

## Gestaltung und wiederverwendbare Bausteine

Der [gemeinsame Baukasten](docs/BAUKASTEN.md) legt die vorgesehenen Varianten und
ihre Einsatzorte fest. Der [geprüfte Bestand](docs/BAUKASTEN_BESTAND.md) erfasst
Komponenten, Avatare, Pulte, Hintergründe, Spielmaterial und Werkzeuge.
Festgelegte nächste Varianten sind dort von bereits eingebauten Bausteinen
getrennt. Dieser Dokumentationsstand wurde ausschließlich offline erstellt.

## Was bereits funktioniert

- freie Registrierung: Jeder Link-Empfänger wählt Spielername und PIN selbst
- genau eine Runde pro Person und Kalendertag
- alle verpassten Runden der laufenden Woche können bis Sonntag nachgeholt werden
- 903 kuratierte Fragen in einem global unverbrauchten Vorrat für Tagesquiz und Partys
- die Unterthemen der gezielt erweiterten Kategorien sind gleichmäßig verteilt
- fünf aktive Fragearten: Wahr/Falsch, Auswahl, Paare bilden, Reihenfolge und die Schätzung als Finale
- zwei vorbereitete, noch inaktive Fragearten: Buchstabensalat und Zwei-Gruppen-Zuordnung
- zehn davon unabhängige Themenkategorien: Gaming, Glaube & Religion, Musik, Sport, Zeugen der Zeit, Medien & Unterhaltung, Pflanzen & Tiere, Geografie & Welt, Wissenschaft & Technik sowie Mensch & Alltag
- direkte Auflösung nach jeder Antwort
- anteilige Wertung bei Reihenfolge und Paaren
- normierte Schätzpunkte unabhängig von Einheit und Größenordnung
- Tagessieger, Wochenliga und die Hall of Fame als Gesamtwertung
- Hall-of-Fame-Punkte dienen zugleich als persönliche Währung „Ikühe“
- isolierter Partymodus mit höchstens zwei Lobbys, zehn Personen und fünf Runden
- ein gemeinsamer Fragenverbrauch für Tagesquiz und Partys verhindert Wiederholungen
- aktueller Rang wird bei jedem Aufruf neu aus der Live-Bestenliste berechnet
- Ergebnisrückblick mit allen eigenen und richtigen Antworten
- serverseitiger Zeitfaktor mit sichtbarem Balken pro Frage
- mobil optimierte sieben Screens vom Start bis zum Ergebnis
- SQLite-Persistenz, CSRF-Schutz und Healthcheck

## Punkte und Zeitwertung

Jede der fünf Fragen bringt 0 bis 100 Punkte. Eine fachlich vollständig falsche Antwort bringt immer 0 Punkte; eine perfekte Runde erreicht 500.

Wahr/Falsch und Auswahl erhalten fachlich 100 Punkte bei einer richtigen und 0 Punkte bei einer falschen Antwort. Bei der waagerechten Reihenfolge zählt ausschließlich jeder Begriff, der exakt auf seiner richtigen Position liegt. Ohne Zeitabzug ergeben ein Treffer 15 Punkte, zwei Treffer 50 Punkte und drei oder vier Treffer 100 Punkte. Mit vollständig abgelaufener Zeit sind es 10, 25 beziehungsweise 50 Punkte. Dazwischen sinkt die Wertung mit dem normalen Zeitfaktor stufenweise. Die Zuordnung wird pro richtigem Paar anteilig bewertet. Die Schätzung liefert abhängig von der relativen Abweichung 10 bis 100 Genauigkeitspunkte. Mengen und Größen werden relativ zum richtigen Wert bewertet. Bei Kalenderjahren dient eine Spanne von 100 Jahren als Prozentbasis, damit beispielsweise 80 Jahre Abweichung als 80 Prozent Fehler zählen und nicht durch die große Jahreszahl verharmlost werden.

Nach jeder Auflösung bleiben Antwort, richtige Lösung und Erklärung mindestens vier Sekunden sichtbar, bevor die nächste Frage oder das Ergebnis geöffnet werden kann.

Die ersten fünf Sekunden bleiben immer bei voller Zeitwertung. Danach sinkt der Zeitfaktor in Sekundenschritten von 100 auf höchstens 50 Prozent. Dadurch bleiben Teilwertungen proportional: Ein fachlicher Ausgangswert von 25/50/75/100 Punkten kann durch die Zeit höchstens auf 13/25/38/50 Punkte sinken. Positive Wertungen und die Schätzung behalten mindestens 10 Punkte.

| Frage | Dauer des Punkteabzugs | 50-Prozent-Faktor erreicht nach |
| --- | ---: | ---: |
| 1 | 5 Sekunden | 10 Sekunden gesamt |
| 2 | 7 Sekunden | 12 Sekunden gesamt |
| 3 | 10 Sekunden | 15 Sekunden gesamt |
| 4 | 12 Sekunden | 17 Sekunden gesamt |
| 5 | 20 Sekunden | 25 Sekunden gesamt |

Die Zeit wird auf dem Server gemessen, damit ein Neuladen der Seite die Uhr nicht zurücksetzt.

## Physische Fragenablage

Die Fragen liegen unter `fragen/` ausschließlich nach Frageart sortiert. Jede
Frageart besitzt direkt eine eigene `fragen.json`; Kategorien-Unterordner gibt
es nicht. Auf dem Live-Server entspricht das `/srv/guesstimate/fragen/`.
`fragen/manifest.json` legt Bezeichnungen, Ordnernamen, Aktivierungsstatus und
Rundenreihenfolge fest.

```text
fragen/
├── wahroderunwahr/fragen.json
├── multiplechoice/fragen.json
├── paarebilden/fragen.json
├── reihenfolge/fragen.json
├── schaetzung/fragen.json
└── zweigruppenzuordnen/fragen.json
```

Die unabhängige Ablage `fragen/stormseedsperfekt/` ist für ein separates,
noch nicht eingebundenes Spiel vorgemerkt. Sie gehört nicht zum Fragenmanifest
und enthält derzeit 12 neu recherchierte Begriffskarten sowie 12 neu
recherchierte Kuriositätenkarten in getrennten Listen. Der frühere ungeprüfte
Bestand wurde vollständig ersetzt.

Wahr-oder-unwahr-Fragen enthalten keinerlei Kategorien- oder Unterthemenfelder.
Alle anderen Fragearten besitzen einen einheitlichen Steckbrief mit
`primary_category`, `subtopic` und `tags`. Diese Angaben steuern keine feste
Produktionsquote, sind aber für Themenausgleich, Statusanzeige und konsistente
Weiterverarbeitung verpflichtend. Die vollständigen Regeln stehen in
`fragen/STECKBRIEF.md`.

Der dynamische Status „benutzt/unbenutzt“ steht absichtlich nicht in den
JSON-Dateien. Er wird dauerhaft in der Datenbanktabelle `question_usage`
geführt, damit beim Spielen keine Quelldatei umgeschrieben werden muss.

Die vorbereiteten künftigen Spielarten erhalten ihren jeweils eigenen Vorrat.

## Projekt und Betrieb

Der einzige Projektordner auf dem Server ist `/srv/guesstimate`.

- `app.py`, `questions.py`, `templates/`, `static/`, `fragen/`: laufende Anwendung.
- `tests/`: isolierte Prüfungen; `deploy/`: Dienst, Prüf- und Wartungswerkzeuge.
- `.deps/`: installierte Python-Abhängigkeiten.
- `runtime/quiz.sqlite3`: aktuelle Spielstände, Konten und verbrauchte Fragen.
- `config/session.secret`, `config/mail.secret`: geschützte Zugangsdaten.

Daten, Zugangsdaten und Abhängigkeiten sind vom Git-Repository ausgeschlossen.
Sicherungen und alte Versionen liegen ausschließlich auf dem lokalen PC.
Der Dienst `guesstimate.service` lauscht intern auf `127.0.0.1:8765`.
Die Systemregistrierung zeigt auf `deploy/guesstimate.service` in diesem Projekt.

Öffentliche Adresse: https://igroup.it-sauther.de/guesstimate/
Gesundheitsprüfung: https://igroup.it-sauther.de/guesstimate/health

Die Dienstregistrierung wird einmalig mit
`sudo /srv/guesstimate/deploy/install-live.sh` aktualisiert. Danach lädt Gunicorn
Änderungen am Python-Code automatisch; Templates und statische Dateien werden
ohnehin direkt aus dem Projekt gelesen. Der Installer bleibt für Änderungen an
Abhängigkeiten oder der Dienstdefinition zuständig. Er prüft den vorhandenen
Projektstand, überschreibt aber weder Spielstände noch die Konfiguration des
gemeinsamen HTTPS-Proxys.

## Tests

### Lokale Windows-Version

Im Windows-Arbeitsordner kann `Guesstimate-starten.cmd` per Doppelklick
gestartet werden. Danach im Browser `http://127.0.0.1:8765/` aufrufen.
Das Fenster muss beim Spielen offen bleiben; Strg+C beendet die Anwendung.
Bei der ersten Einrichtung werden die lokalen Abhängigkeiten mit
`python -m pip install --target .deps -r requirements-local.txt` installiert.

Dies ist die normale Anwendung mit Registrierung, Daily Quiz und den bereits
implementierten Mehrspielermodi. Der eigene dauerhafte PC-Spielstand liegt
unter `runtime/pc-local/quiz.sqlite3`, der Sitzungsschlüssel daneben.
Beide bleiben von Git ausgeschlossen. Es werden keine Vorschaukonten,
Bonuspunkte oder Beispielergebnisse angelegt und keine Mails verschickt.
Vorhandene Testdatenbanken und Server-Sicherungen werden nicht eingelesen.
Die Anwendung lauscht ausschließlich auf diesem PC; ein öffentlicher Zugang
ist damit noch nicht eingerichtet.

Die weiterentwickelte Conquest-Tischfassung ist hinter der normalen Lobby
eingebunden. `Feldzug starten` öffnet am selben Ort den räumlichen Tisch mit
gespeicherter Aufstellung und Zugaktionen. Ein zusätzlicher Tischserver ist
nicht erforderlich. Der lokale Besitzer mit aktivem Entwicklermodus kann eine
Einpersonen-Lobby über `Entwickler-Test starten` mit zwei virtuellen Testarmeen
starten und alle drei Armeen abwechselnd steuern. Dafür entstehen keine weiteren
Benutzerkonten. Normale Partien benötigen weiterhin mindestens zwei Personen.

Darstellung und Bedienung liegen gemeinsam unter
`offline-preview/conquest-2-5d-v1/`; die App liefert ausschließlich die benötigten
Dateien über ihre eigene Adresse aus. Die frühere isolierte Vorschau nutzt
dieselben Komponenten, behält aber ihren ausdrücklich ungespeicherten Beispielzug.
Gespeicherte Partien verwenden die Python-Zugregeln und bleiben beim Neuladen
erhalten. Der Kartentausch folgt der gemeinsamen steigenden Folge
4, 6, 8, 10, 12, 15, danach jeweils +5. Zwei Joker ergänzen die 42
Gebietskarten. Ein passendes eigenes Gebiet erhält beim Tausch direkt +2,
höchstens einmal je Zug. Im Inventar drei Karten auswählen und den Satz
mit der Bank tauschen; bei fünf oder mehr Karten ist dies vor dem Platzieren
Pflicht. Große Symbole zeigen Infanterie, Reiter und Geschütz.
Automatische Sieg-/Missionsprüfung und klassische Gebietswahl fehlen noch.

Für Freunde braucht es einen getrennten stabilen Spielbetrieb und einen
öffentlichen HTTPS-Zugang. Für die Fortsetzung vorhandener Konten, Punkte und
Fragenverbräuche ist zusätzlich eine aktuelle konsistente Server-Datenbank
erforderlich. Git allein enthält diese Daten nicht. Ein neuer PC-Spielstand
wird später nicht automatisch mit dem Server zusammengeführt.

### Prüfungen

```bash
cd /srv/guesstimate
PYTHONPATH=.deps:. python3 -m unittest discover -s tests -v
python3 deploy/validate_question_library.py
```

`deploy/reset_game.py` und `deploy/merge_player.py` sind getrennte Wartungswerkzeuge.
Sie werden bei einem normalen Neustart nicht ausgeführt. Vor einer Änderung an
echten Spielständen wird eine konsistente Sicherung auf den lokalen PC übertragen.

## Benachrichtigung bei leerem Fragenpool

Das Spiel meldet einen vollständig verbrauchten Fragenpool über das konfigurierte
Mailkonto. Zugangsdaten bleiben ausschließlich in `config/mail.secret`.
Fehlgeschlagener Versand bleibt als ungesendet vorgemerkt. Alte Fragen werden
nicht automatisch wieder freigegeben.
