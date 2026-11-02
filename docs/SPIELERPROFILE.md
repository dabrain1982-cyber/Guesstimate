# Spielerprofile

Stand: 29.10.2026. Im lokalen Hauptspiel umgesetzt; keine Aktivierung auf dem
Projektserver vorgenommen.

Unter **Profil → Spieler entdecken** steht eine durchsuchbare Übersicht aller
registrierten Spieler. Ein Klick auf einen Spielernamen in den Daily-Quiz-
Ranglisten oder auf „Profil ansehen“ in einer gemeinsamen Lobby öffnet ebenfalls
das jeweilige Profil. „Mein öffentliches Profil“ zeigt die eigene Außenansicht;
„Eigenes Profil bearbeiten“ führt zurück zur bisherigen Ausrüstung.

Die Ansicht ist nur für angemeldete Mitspieler erreichbar. Sichtbar sind Name,
ausgerüsteter Avatar, Hintergrund, Pult und Spruch sowie Gesamtpunkte, Rang der
Hall of Fame, abgeschlossene Daily-Quizrunden, bester Tageswert, Durchschnitt
und Titel. Noch laufende Runden zählen nicht in die Ergebnisübersicht. Bei
gleicher Punktzahl gilt dieselbe Rangfolge wie in der bisherigen Rangliste.

Käufe, Inventar, iKuh-Kontostand, Anmeldeinformationen und Entwicklereinstellungen
gehören nicht zur Außenansicht. Der neutrale Startavatar verwendet dort auch
beim eigenen öffentlichen Profil seine vorhandene öffentliche Bildfassung.
Ein Profilbesuch oder eine Suche verändert keine Spiel-/Kontodaten und trägt
auch nach einem Datumswechsel keinen Login ein. Normales Anmelden und Öffnen
der Startseite behalten ihr bisheriges Verhalten.

Routen: `/spieler`, `/spieler?q=Name`, `/spieler/<id>`. Präfixe des vorhandenen
Webservers werden übernommen. Ungültige Spielerkennungen ergeben 404, Änderungen
über diese Ansichten sind nicht vorgesehen. Antworten sind privat und nicht
zwischenspeicherbar; die Seiten werden nicht zur Suchmaschinenindexierung
angeboten.

Die Profilansicht verwendet unverändert das gemeinsame `profile_window`-Makro.
Der Pokalschrank ist in `_profile_trophies.html` zusammengeführt und wird in der
eigenen und fremden Ansicht verwendet. Die Spielerübersicht benutzt die vorhandene
`player_identity`-Komponente. Die beiden neuen Verwendungen und die verschobene
Pokalschrankquelle sind in der lokalen Werkstatt erfasst; 27 dynamische Beispiele
mit aktuellen Quellenprüfsummen neu aufgenommen. Kein zweiter Profilnachbau.

Die lokale Testansicht auf `localhost:8778` enthält nur die erfundenen Spieler
Profiltest, Mira und Neuling. Sie verwendet einen eigenen Anmeldecookie. Die erste
Testanmeldung auf 127.0.0.1 verwendete zuvor versehentlich den Standardcookie;
im persönlichen lokalen Spiel wurde anschließend eine Anmeldeseite beobachtet.
Erneute persönliche Anmeldung und deren Prüfung stehen bis zur Rückmeldung des
Nutzers aus. Persönliche PINs wurden nicht gelesen oder verändert.

Nachweise liegen unter `runtime/public-profiles-20261029/`: eigene sieben
Profiltests sowie bestehende Profilfenster-/Lobbytests (16/16), weitere 28
unterschiedliche Prüfungen für Spieler-/Anzeigequellen, Buttonzuordnungen und
bisherige Profile. Zwei dabei veraltete Bestandserwartungen nach Anpassung
erfolgreich nachgeprüft. Insgesamt 44 unterschiedliche Fälle erfolgreich
abgedeckt; kein vollständig erfolgreicher einzelner 44er-Lauf behauptet.
Browserprüfung von eigener Profilnavigation, Suche und fremdem Profil sowie
Screenshot `profil-mitspielerin.png`. Persönliche Anwendungstabellen nach dem
Neuladen unverändert, interner SQLite-Zähler `login_days` von 28 auf 29 erhöht.
