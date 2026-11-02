# Ranglisten und Conquest-Flyer für Version1.1

Die sichtbare Rangliste hat genau drei Hauptregister mit jeweils zwei Ansichten:

| Register | Ansichten | Wertung |
|---|---|---|
| guesstimate | Tag, Woche | Punkte abgeschlossener Daily-Quizrunden |
| iKühe | Aktuell, All Time High | Kontostand und erfasster höchster Kontostand |
| Hall of Fame | Tagessiege, Wochensiege | Gewonnene abgeschlossene Daily-Quizzeiträume |

Bei gleichen Werten gibt es geteilte Ränge. Geteilte erste Plätze zählen für
alle betroffenen Spieler als Sieg. Der laufende Tag und die laufende Woche
werden noch nicht als endgültige Siege vergeben. Perfect-/Partysiege gehören
nicht in diese Hall-of-Fame-Wertung.
Die Hall of Fame bleibt auch beim Anzeigen einer älteren Nachholrunde auf dem
aktuellen Stand; nur die Tag-/Wochenpunkte beziehen sich auf den Rundentag.

Die bisherigen Gesamtpunkte bleiben für Profile und interne Rangberechnungen
erhalten. Sie sind kein zusätzlicher sichtbarer Ranglistenreiter mehr. Der
frühere Gesamtpunkte-Rang im öffentlichen Profil heißt entsprechend wieder
Gesamtpunkte-Rang; die monatlichen Pokale tragen die genaue Bezeichnung
Monatssiege.

## iKühe-Höchststand

Bestehende Höchststände werden aus gespeicherten Quizabschlüssen und
Shopkäufen rekonstruiert. Alte Zeitstempel sind sekundengenau. Wenn Guthaben
und Ausgaben dieselbe Sekunde tragen, wird deren gemeinsamer Endstand
ausgewertet; eine nicht belegbare frühere Spitze wird nicht erfunden.
Historische Spitzen sind deshalb nur soweit in der vorhandenen Historie
belegbar wiederherstellbar. Die Oberfläche nennt sie „Erfasster Höchststand“.

Die neue Tabelle `currency_peaks` hält belegte Spitzen dauerhaft fest.
Quizgutschrift und Erfassung erfolgen in derselben Transaktion; vor einem
Shopkauf wird der noch nicht verminderte Kontostand erfasst. Lesen der
Ranglisten verändert weder Konten noch die Historie. Vorhandene
Quizpunkte und Preise bleiben unverändert. Black-Jack-Testguthaben gehört
nicht zur regulären iKühe-Rangliste.

## Gemeinsame Anzeige und Flyer

`templates/_leaderboard.html` besitzt eine gemeinsame Komposition für
Startseite, Fragen und Ergebnis. Die Register sind per Maus und Tastatur
bedienbar. Alle sechs Ansichten benutzen dieselbe Spieleranzeige.

Der sechste Flyer der Startseiten-Diashow zeigt Stormseed’s Conquest
(Risiko). Vorhandene Kartenillustration, gemeinsame Titelkomposition
`conquest_flyer_copy` und `static/conquest-flyer.css` werden auch für die
Conquest-Kachel im Brettspielbereich benutzt. Skalierung erfolgt über den
gesamten Flyer; keine unabhängige zweite Innenkomposition.
