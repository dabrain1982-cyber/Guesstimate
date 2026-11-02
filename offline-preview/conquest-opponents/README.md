# Simulierte lokale Conquest-Mitspieler

Nur für die bestehende Vier-Personen-Testrunde auf
<http://127.0.0.1:8767/karten/welteroberung/3>. Stormseed bleibt manuell;
Robin, Bela und Alex führen regelkonforme Beispielzüge aus. Dies ist keine
strategische KI und keine Änderung am normalen Mehrspielermodus.

Start im Projektordner:

```powershell
python -X utf8 offline-preview/conquest-opponents/runner.py
```

Mit `--restart` wird ausschließlich diese Testrunde neu aufgestellt. Derselbe
Tisch, dieselben Testkonten und Einstellungen bleiben erhalten. Die anderen
Testpartien und die normale PC-Datenbank werden nicht verändert. Das bisherige
Startskript der Vorschau nicht erneut ausführen: Es würde weitere Testdaten
anlegen.

Startaufstellung jeweils eine Truppe, Verstärkung, höchstens zwei Angriffswürfe
je gegnerischem Zug, automatische Verteidigung, Pflichtbesetzung, Pflichtkartentausch und
einmaliges Festigen laufen über die normale Spielaktionsroute. Echte
Zufallswürfe bleiben erhalten. Verteidigung erfolgt mit einem Würfel bei einer
Einheit, sonst mit zwei Würfeln, ohne Wahl oder Fenster. Eigene Aufstellung,
Züge und Einrücken bleiben beim Nutzer. Bei menschlicher Entscheidung wartet die
Simulation; sie läuft nach dem Chat weiter, solange ihr Prozess und die
lokale Vorschau laufen. Nach Spielende stoppt sie.

Strg+C im Prozess oder Datei `runtime/conquest-opponents-20261025/stop`
anlegen hält die Simulation an. Für erneuten Start diese eigene Stopdatei
vorher entfernen. Pro Testrunde wird genau ein Simulator zugelassen.


## Neue Lobby 6: Spieler beitreten lassen, Host startet selbst

Für die vom Nutzer neu angelegte Lobby auf
<http://127.0.0.1:8767/karten/welteroberung/6>:

```powershell
python -X utf8 offline-preview/conquest-opponents/lobby_runner.py --prepare
python -u -X utf8 offline-preview/conquest-opponents/lobby_runner.py
```

Vorbereiten lässt die vorhandenen Testkonten Robin, Bela und Alex über die
normalen Beitrittsrouten beitreten. Es erstellt keine Konten und startet kein
Spiel. Ohne `--prepare` wartet der Prozess auf den manuellen Start durch
Stormseed und spielt anschließend ausschließlich diese drei Konten. Die
neuen Mitgliedsnummern werden aus der überprüften lokalen Testlobby gelesen;
der menschliche Platz wird beim Senden nochmals ausgeschlossen. Eigene
Startaufstellung und Züge bleiben manuell, Sieg stoppt den Simulator.

Es gelten fest nur Port 8767, die bestehende Testdatenbank und die geprüften
vier Testkonten in Lobby 6. Die normale PC-Datenbank wird nicht geöffnet.
Stopdatei: `runtime/conquest-lobby6-20261025/stop`. Status, Sperre und Protokolle
liegen ebenfalls in diesem Ordner. Die ursprüngliche abgeschlossene Partie 3
wird nicht zurückgesetzt. Der alte Runner für Partie 3 bleibt getrennt.
