# Guesstimate auf diesem PC

Im Ordner `D:\Guesstimate` liegen zwei Dateien zum Doppelklicken:

- **Guesstimate-starten.cmd** öffnet die aktuelle lokale Arbeitsvorschau.
  Auch deine vorhandene Desktop-Verknüpfung nutzt diesen Starter. Aktuell ist
  das Conquest mit dem vorhandenen Spielstand; nach einem PC-Neustart startet
  der Starter den benötigten Dienst wieder und setzt diesen Stand fort.
- **Werkstaetten-starten.cmd** öffnet direkt die gemeinsame Werkstatt mit
  Gestalten, Bibliothek und Projektmappe. Der eingebundene Buttoneditor und
  die erhaltenen älteren Werkzeuge benutzen weiterhin ihre vorhandenen Dateien.

Läuft der passende Dienst aus diesem Projektordner bereits, wird er
weiterverwendet. Mehrfaches Öffnen erzeugt keine weiteren Server. Ein fremdes
Programm auf demselben Anschluss wird nicht beendet; der Starter meldet den
Konflikt.

Wenn ein Startfenster offenbleibt, braucht der neu gestartete Dienst dieses
Fenster. **Strg+C oder Schließen beendet die damit gestarteten Dienste.** Bereits
vorher laufende Dienste bleiben bestehen. Wenn alles schon läuft, schließt sich
das neue Fenster nach dem Öffnen des Browsers wieder.

## Daten und Adressen

- Aktuelle Arbeitsvorschau: <http://127.0.0.1:8767/local/current>
  Öffnet automatisch die neueste eigene Conquest-Partie bzw. deren Lobby.
- Normales Hauptspiel: <http://127.0.0.1:8765/>. Bei Bedarf gezielt über
  `Guesstimate-starten.cmd --main-game` starten.
- Gemeinsame Werkstatt: <http://127.0.0.1:8776/#editor/buttons>
- Spielbuttons und eigene Entwürfe: <http://127.0.0.1:8776/#library/buttons>
- Übersicht der erhaltenen älteren Werkzeuge: <http://127.0.0.1:8771/sammlung>
- Die vorhandenen PC-Spielstände bleiben in `runtime/pc-local/quiz.sqlite3`.
  Der Sitzungsschlüssel bleibt in `runtime/pc-local/session.secret`.
- Gespeicherte Buttonentwürfe bleiben in
  `design-library/recipes/button-workshop/`. Eigene Formen und noch nicht
  exportierte Browser-Einstellungen immer mit demselben Browser öffnen, in dem
  sie erstellt wurden. Die Doppelklick-Dateien öffnen den Standardbrowser;
  bei einem anderen bisherigen Browser dort die obige Adresse öffnen.
- Startmeldungen stehen bei Bedarf in `runtime/local-launcher/`.
- Die aktuelle Conquest-Vorschau verwendet weiterhin die vorhandenen Daten
  in `runtime/conquest-hud-20261025/walkthrough.sqlite3` und die vorhandene
  Spielerzuordnung. Keine neue Testrunde wird erzeugt. Fehlen diese Dateien,
  bricht der Starter mit einer Meldung ab. Das Angriffsbeispiel auf 8768 bleibt
  separat. Die Mitspielersimulation wird durch Doppelklicken nicht gestartet.
- `deploy/local-preview.json` legt das aktuelle Arbeitsziel für denselben
  Starter fest. Änderungen am lokalen Programm werden direkt von den Dateien
  im Projektordner geladen; keine neue Verknüpfung nötig.

Die Starter installieren nichts und nutzen das vorhandene Python. Vorrang hat
eine `.venv`, danach der Windows-Python-Starter `py`, danach `python`.
Für das normale Spiel werden die bereits eingerichteten Abhängigkeiten aus
`.deps` genutzt. Die Werkstätten benötigen nur Python.

## Eigene Buttonmodelle im Hauptspiel

Ab 28.10.2026: In der Werkstatt **Bibliothek → Buttons → eigener Entwurf →
Ansehen → Verwendungen verwalten** öffnen. Gewünschte Einsatzgruppen wählen und
**Zuordnung übernehmen** drücken; **Original wiederherstellen** setzt sie zurück.
Dies gilt für das normale Hauptspiel auf 8765, gestartet mit
`Guesstimate-starten.cmd --main-game`. Die aktuelle räumliche Conquest-Vorschau
auf 8767 bleibt separat. Umfang und Bedienweg: [Buttonverwendungen](docs/BUTTON_VERWENDUNGEN.md).

## Was „auf dem PC hosten“ hier bedeutet

Die Dienste sind ausschließlich auf diesem PC erreichbar. Sie laufen, solange
der PC und der jeweilige Dienst laufen. Zum Spielen von weiteren Geräten im
Heimnetz oder über das Internet braucht es eine separate Einrichtung des
Zugriffs. Die Starter ändern dafür weder Firewall noch Router und übertragen
nichts auf den bisherigen Spielserver.
