# Blackjack: normales iKühe-Konto (V 1.01.01, noch nicht veröffentlicht)

account_wallet.py ist die gemeinsame Kontoberechnung: abgeschlossene Quizpunkte
minus Shopkäufe plus unveränderlich angehängte currency_entries. Hauptseite,
Profil, Shop, Ranglisten und die Guthabenanzeigen anderer Lobbys nutzen sie.
Quizpunkte und Käufe werden weder umgeschrieben noch als Anfangsguthaben kopiert.

blackjack_store.py verbindet die bestehende Regel-Engine mit diesem Konto.
Jede einzelne Abbuchung/Gutschrift der Engine wird in Reihenfolge aufgezeichnet.
Tischzustand, Kontobuchungen und erfasste Höchststände werden gemeinsam unter
BEGIN IMMEDIATE gespeichert. Spielrevision und eindeutiger Buchungsschlüssel
verhindern doppelte Buchungen. Bei Fehlern rollt dieselbe Transaktion alles zurück.
Shopkäufe verwenden ebenfalls die Schreibsperre und die gemeinsame Kontoprüfung.
Test-iKühe bleiben in blackjack_balances und zählen nie zum normalen Konto.

## Übergang und Warnung

Die Produktionskonfiguration verlangt account-ikuehe,500 Grundeinsatz und NoPeek.
Die separate Tischuhr bleibt der einzige automatische Taktgeber.
Ein alter Testtisch wird nur ohne Sitze, Einsätze oder laufende Hand umgestellt.
Bis dahin bleiben bisherige Hände im Testmodus; neue Einsätze/Beitritte werden
zurückgewiesen. Alte Testbeträge werden nicht belastet oder in normale iKühe
umgewandelt. Die spätere Aktivierung muss den leeren Testtisch vorab prüfen.

Vor jedem neuen Platznehmen erscheint die Warnung. Der Server verlangt dafür
accept_risk=1 zusammen mit der bestehenden Anmeldung/CSRF-Prüfung.
Abbrechen und Escape belegen keinen Sitz und buchen nichts. Die Bestätigung
allein setzt keinen Einsatz. Kostenloses Auffüllen wird im Kontomodus sowohl
in der Oberfläche als auch auf dem Server ausgeschlossen.

## Prüfung und verbleibende Veröffentlichungsschritte

15 neue Kontofälle und8 Ranglistenfälle bestanden, darunter Gewinn/Verlust,
Blackjack, Gleichstand, Aufgeben, Teilen, Verdoppeln, Versicherung, NoPeek,
doppelte Anforderungen, parallele Shop-/Tischaktionen, zwei Taktgeber,
Rollback bei Speicherfehler und Erhalt bestehender Daten bei Schemaergänzung.
90 bestehende Quiz-/Blackjack-/Versionsfälle sowie44 Bewegungs-/Eingabechecks
ebenfalls bestanden. Sichtbare Konto-/Warnprüfung erfolgte mit einem isolierten
fiktiven Vorschaukonto; keine persönliche oder öffentliche Hand gespielt.

Vor Veröffentlichung bleiben die gemeinsame Gesamtprüfung mit Serverdatenkopie,
die aktuellen Fragenhistorien-Prüfungen, Sicherung, Rückweg und Umschaltung offen.
Wichtig für den Rückweg: Unveränderte alte1.0/1.1-Programme berücksichtigen
currency_entries nicht. Nach echten Kontobuchungen darf deshalb nicht blind
nur alter Code gestartet werden. Ein Rückweg muss den kompatiblen Kontoleser
beibehalten oder den Spielbetrieb geschlossen lassen, bis die Daten korrekt
gelesen werden. Niemals aktuelle Buchungen durch eine alte DB ersetzen.
Dieser betriebliche Rückweg gehört noch zu Punkt6.


## Vorbereiteter betrieblicher Rückweg (02.11.2026)

deploy/activate_update_1_01_01.py erstellt vor der Umschaltung private,
serverseitige SQLite-/Konfigurations- und vollständige Quellensicherungen mit
Prüfsummen. Vorhandene Datensätze werden vor und nach der Schemaergänzung
verglichen. Die aktuelle Nutzungshistorie wird vor dem Fragenimport erneut
gelesen. Ein belegter Blackjacktisch führt zum Abbruch; kein Spieler wird
automatisch entfernt.

Bei einem Fehler vor dem Dateitausch startet der bisherige Betrieb wieder.
Nach dem Dateitausch erfolgt eine gesonderte1.1-wallet-recovery.1:
alter1.1-Code, kanonischer neuer Kontoleser und neue Fragen bleiben verfügbar;
Blackjack ist vorübergehend pausiert. Keine alte Datenbank wird zurückgespielt.
Projektlog und Anweisungen werden nicht durch ältere Kopien ersetzt.
Die Rückkehr ist an isoliertem fiktivem Serverguthaben geprüft:
1500 Quiz minus100 Kauf minus500 Blackjack =900 im Konto und in der Rangliste;
Blackjack-GET und -POST liefern503, Buchungszeilen bleiben unverändert.
Dies ist eine ausdrücklich gekennzeichnete Wiederherstellung, kein
unveränderter Start des Tags v1.1.

42 betroffene Prüfungen lokal bestanden;9 gezielte Linux-Serverfälle und
gesonderter Wiederherstellungstest bestanden. Ein breiter Serverlauf verlor
nach SSH-Zeitlimit den Abschlussbeleg und gilt daher nicht als bestanden.
Private echte Serverdatenkopie und Aktivierung erfordern weiterhin die
Administratorausführung. Menschlicher Mehrspielertest bleibt offen.

Die iKühe-Einführung verwendet für Popup und Seite dieselbe Inhaltskomponente.
user_notice_views merkt sie einmal je Konto, unabhängig von Sitzungs-Cookies;
kein Bezug zur Warnung vor jedem Platznehmen. Patchnotes werden auf aktuelle
ausdrückliche Anweisung nur im Chat für den Betreiber vorbereitet und nicht
als Nachricht oder vollständiger Text öffentlich ausgeliefert.
