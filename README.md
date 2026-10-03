# Stormseed´s Guesstimate – tägliches Quiz

Ein mobil optimiertes Quiz für bis zu 100 Personen: Login, eine tägliche Runde mit fünf Kategorien, normiertes Scoring und eine fortlaufende Gesamtrangliste.

## Was bereits funktioniert

- freie Registrierung: Jeder Link-Empfänger wählt Spielername und PIN selbst
- genau eine Runde pro Person und Kalendertag
- alle verpassten Runden der laufenden Woche können bis Sonntag nachgeholt werden
- 750 kuratierte Fragen (150 je Kategorie) in einem global unverbrauchten Vorrat für Tagesquiz und Partys
- ansteigende Schwierigkeit: Wahr/Falsch, Multiple Choice, Paare, Reihenfolge und die Schätzung als Finale
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

Wahr/Falsch und Auswahl erhalten fachlich 100 Punkte bei einer richtigen und 0 Punkte bei einer falschen Antwort. Bei der waagerechten Reihenfolge zählt jede der vier korrekt platzierten Positionen 25 Punkte; die Zuordnung wird pro richtigem Paar anteilig bewertet. Die Schätzung liefert abhängig von der relativen Abweichung 10 bis 100 Genauigkeitspunkte.

Die ersten fünf Sekunden bleiben immer bei voller Zeitwertung. Danach sinkt der Zeitfaktor in Sekundenschritten von 100 auf höchstens 50 Prozent. Dadurch bleiben Teilwertungen proportional: Ein fachlicher Ausgangswert von 25/50/75/100 Punkten kann durch die Zeit höchstens auf 13/25/38/50 Punkte sinken. Positive Wertungen und die Schätzung behalten mindestens 10 Punkte.

| Frage | Dauer des Punkteabzugs | 50-Prozent-Faktor erreicht nach |
| --- | ---: | ---: |
| 1 | 5 Sekunden | 10 Sekunden gesamt |
| 2 | 7 Sekunden | 12 Sekunden gesamt |
| 3 | 10 Sekunden | 15 Sekunden gesamt |
| 4 | 12 Sekunden | 17 Sekunden gesamt |
| 5 | 20 Sekunden | 25 Sekunden gesamt |

Die Zeit wird auf dem Server gemessen, damit ein Neuladen der Seite die Uhr nicht zurücksetzt.

## Lokal starten

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/flask --app app run
```

Danach ist die App unter `http://127.0.0.1:5000` erreichbar. Über **Eigenen Login anlegen** wählt jeder Spieler seinen sichtbaren Namen und eine persönliche PIN. Vor dem Livegang muss `QUIZ_SECRET_KEY` auf ein langes zufälliges Geheimnis gesetzt werden.

## Tests

```bash
.venv/bin/python -m unittest discover -s tests -v
```

Die Tests prüfen unter anderem die größenunabhängige Schätzformel, Teilpunkte der Reihenfolge, den kompletten perfekten Spielablauf, den Maximalscore und die Einmalteilnahme.

## Debian-Server

Die Dateien in `deploy/` richten einen abgeschotteten systemd-Dienst hinter dem bestehenden Caddy-HTTPS-Proxy ein. Gunicorn bindet nur intern an `127.0.0.1:8765`; die bestehende iGroup-Anwendung bleibt auf ihrem eigenen internen Port.

Ein erneutes Einspielen mit vollständigem Reset von Runden, Antworten und Highscore – bei unveränderten Logins – erfolgt mit:

```bash
sudo "/home/igroup/minime-deploy/guesstimate/deploy/install-live.sh" --reset-game
```

Vor dem Reset wird automatisch eine Datenbanksicherung angelegt.

Bis die eigene Subdomain eingerichtet ist, veröffentlicht Caddy das Quiz unter `/guesstimate/` und leitet alle übrigen Aufrufe weiter an die bestehende iGroup-Anwendung.

Der Healthcheck liegt unter `/health`.

### Benachrichtigung bei leerem Fragenpool

Die Anwendung verschickt genau eine Nachricht an die in /etc/guesstimate.env konfigurierte Adresse, sobald keine vollständige unverbrauchte Runde mehr vorhanden ist. Alte Fragen werden nicht selbstständig wieder freigegeben. Adresse und Kontaktadresse stehen nur in dieser lokalen Konfigurationsdatei; das Mail-Passwort gehört ausschließlich in die nur für den Dienst lesbare Datei /etc/guesstimate-mail.secret. Beides wird niemals in Git gespeichert. Fehlt die Einrichtung oder schlägt der Versand fehl, bleibt die Nachricht als ungesendet vorgemerkt.

Die sichere Einrichtung erfolgt auf dem Server mit:

```bash
sudo install -o root -g guesstimate -m 0640 deploy/guesstimate.env.example /etc/guesstimate.env
sudoedit /etc/guesstimate.env
sudo install -o root -g guesstimate -m 0640 /dev/null /etc/guesstimate-mail.secret
sudoedit /etc/guesstimate-mail.secret
sudo chown root:guesstimate /etc/guesstimate-mail.secret
sudo chmod 0640 /etc/guesstimate-mail.secret
sudo systemctl restart guesstimate.service
```

In der Datei steht ausschließlich das GMX-Passwort beziehungsweise App-Passwort. Der GMX-Zugriff für Mailprogramme muss im Konto freigeschaltet sein.

### Für später vorgemerkt: eigene Adresse

Der Serverbesitzer muss im DNS `guesstimate.it-sauther.de` auf diesen Server zeigen lassen. Danach wird Caddy von `igroup.it-sauther.de/guesstimate/` auf die eigenständige Adresse `https://guesstimate.it-sauther.de` umgestellt. Diese DNS-Änderung kann nicht innerhalb der Quiz-Anwendung vorgenommen werden.
