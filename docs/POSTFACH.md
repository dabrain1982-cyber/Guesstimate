# Postfach – lokale Ergänzung vom 01.11.2026

Der Briefumschlag „mail“ in der gemeinsamen Leiste öffnet eine eigene Seite
unter `/mail`. Nachrichten erscheinen als helle Papierzettel mit lokal
eingebundener Handschrift (Caveat, Quelle und SIL-Lizenz unter `static/fonts/`).
Empfangene und gesendete Nachrichten bleiben im jeweiligen Postfach erhalten.

## Umfang und Versandrechte

- Angemeldete Spieler können ausschließlich dem Betreiber schreiben.
- Der Betreiber kann einen einzelnen Mitspieler oder alle anderen zum
  Sendezeitpunkt vorhandenen Konten anschreiben. Maßgeblich ist die bestehende
  Einstellung `OWNER_USERNAME`, normalerweise `stormseed`.
- Texte sind Klartext mit Zeilenumbrüchen; HTML wird nicht ausgeführt.
- Es gibt nur Gelesen/Ungelesen. Keine Ticketstufen, Anhänge oder weiteren
  Verwaltungsfunktionen. Der vorhandene externe Fragenvorrat-Mailversand ist
  davon unabhängig.

## Briefumschlag und Lesen

Neue eingehende Post lässt den Briefumschlag wackeln, bis er angeklickt wird.
Dieser Klick bestätigt die angekündigten Nachrichten dauerhaft für das Konto,
markiert aber keinen Zettel als gelesen. Erst das Öffnen eines einzelnen
eingegangenen Zettels setzt dessen Lesestatus. Eine später eingehende Nachricht
aktiviert die Bewegung erneut. Die Zähler werden auf sichtbaren Seiten alle
30 Sekunden und bei Rückkehr zur Seite aktualisiert. Bei bevorzugter
reduzierter Bewegung bleibt die Bewegung aus; der Zähler ist weiter sichtbar.

Rundnachrichten besitzen für jeden Empfänger einen eigenen Lesestatus.
Empfängerrechte und Schreibaktionen werden auf dem Server geprüft. Alle
Schreibaktionen einschließlich Öffnen/Gelesen erfordern das bestehende
CSRF-Token. Private Post wird ohne Browsercache ausgeliefert.

## Dateien, Daten und Stand

`inbox.py` besitzt die einzige Implementierung für Versand, Zustellung,
Lesestatus und Briefumschlagbestätigung. `templates/mail.html`, `static/mail.css`
und `static/mail.js` sind die gemeinsamen Ansichten. Der Leistenknopf verwendet
die bestehende Navigationskomponente in `base.html`/`quiz-arena.css`.

Die Anwendung legt ausschließlich zusätzliche Tabellen `inbox_messages`,
`inbox_deliveries` und `inbox_attention` in ihrer jeweiligen Datenbank an.
Die bestehenden Spieldaten werden nicht umgeschrieben. Eine Rücknahme des
Programmcodes darf diese Datenbank nicht durch einen alten Stand ersetzen.

Die Ergänzung ist im normalen Offline-Spiel auf Port8765 sichtbar geprüft.
Versandprüfungen fanden ausschließlich mit erfundenen Konten und eigener
Datenbank auf Port8779 statt. Im persönlichen Offline-Spiel wurden keine
Nachrichten verschickt. Sicherung und Belege: `runtime/mail-20261101/`.

Der eingefrorene Sicherungsstand1.1 unter `releases/1.1.json` bleibt unverändert.
Dieses Postfach ist eine nachfolgende lokale Ergänzung, noch ohne neue
Releasezuordnung oder öffentliche Veröffentlichung. Endgültige Patchnotes
und deren Rundversand stehen nach Abgleich mit dem tatsächlichen Serverstand
noch aus.

## Prüfungen

- 11 Postfachprüfungen einschließlich Rechtegrenzen, privaten Inhalten,
  Gelesenständen, dauerhafter Bestätigung, gleichzeitig neuer Nachricht,
  Texteingaben, URL-Präfix und bestehender Werkstatt-Button-Einbindung bestanden.
- Browser: Spieler→Betreiber und Betreiber→alle Testspieler, Papier/Handschrift,
  Zettel öffnen, Bewegung stoppen und durch spätere Post neu aktivieren geprüft.
- Persönliches Offline-Spiel: tatsächlicher Leistenknopf und Betreiberseite
  geöffnet.31 bestehende Tabellen vor/nach der Aktivierung inhaltlich identisch;
  SQLite-Prüfung `ok`, keine persönlichen Nachrichten angelegt.
