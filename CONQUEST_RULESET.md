# Stormseed’s Conquest – verbindlicher Regelunterbau

Der Spielablauf wird als eigener serverseitiger Zustandsautomat umgesetzt. Die
Grafik- und Physikwerkzeuge stellen Brett, Karten, Figuren und Würfel dar; sie
entscheiden niemals selbst über einen gültigen Spielzug.

## Start

- 2–6 Personen; bei zwei Personen kommt eine neutrale Armee hinzu.
- Alle 42 Gebiete sind zu Beginn besetzt.
- Starttruppen: 2 Personen 40, 3 Personen 35, 4 Personen 30, 5 Personen 25,
  6 Personen 20.
- Ein Würfelentscheid bestimmt die erste Person.
- Bei „Geheime Missionen“ erhält jede Person genau eine private Mission.

## Zugphasen und notwendige Anzeige

1. **Verstärken**: verfügbare Truppen, Gebietsgrundwert, Kontinentbonus,
   mögliche Kartensätze und auswählbare eigene Zielgebiete.
2. **Angreifen**: eigenes Startgebiet, benachbartes feindliches Ziel,
   1–3 Angriffswürfel, 1–2 Verteidigungswürfel, Verluste und bei Eroberung die
   Anzahl der einrückenden Truppen. Angriff kann übersprungen oder wiederholt
   werden.
3. **Festigen**: einmalig Truppen von einem eigenen Gebiet in ein benachbartes
   eigenes Gebiet verschieben; mindestens eine Truppe bleibt zurück. Die Phase
   darf übersprungen werden.
4. **Zugende**: genau eine Länderkarte, falls in diesem Zug mindestens ein
   Gebiet erobert wurde; dann Wechsel zur nächsten noch aktiven Person.

## Technikentscheidung

`boardgame.io` ist ein MIT-lizenziertes Gerüst für Lobby, Mehrspielerzustand,
Züge und Phasen, enthält aber kein fertiges Regelwerk für dieses Spiel. Das
Projekt besitzt bereits dieselben Grundbausteine in Flask und SQLite. Deshalb
wird kein zweiter Node-/Socket-Server eingeführt; die Regeln werden hier
klein, nachvollziehbar und testbar in Python umgesetzt.

## Quellen

- Hasbro, offizielles klassisches Regelheft: https://www.hasbro.com/common/instruct/risk.pdf
- Hasbro, neuere Regelfassung: https://www.hasbro.com/common/documents/DAD2886D1C4311DDBD0B0800200C9A66/F56A63AE8FA145D9B82A5FA3919CA3A5.pdf
- boardgame.io, offizielle Dokumentation: https://boardgame.io/
