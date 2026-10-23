# Projektlog – Stormseed´s Guesstimate

Diese Datei ist die dauerhafte, chatübergreifende Übergabe für Arbeiten im
Projekt `/srv/guesstimate`. Der aktuelle Datei- und Live-Zustand bleibt immer
die maßgebliche Wahrheit.

## Projektidentität

- Projekt: Stormseed´s Guesstimate
- Arbeits- und Live-Ordner: `/srv/guesstimate`
- Öffentliche Adresse: `https://igroup.it-sauther.de/guesstimate/`
- Lokaler Dienst: `guesstimate.service`, Gunicorn auf `127.0.0.1:8765`
- Fragenbestand: `fragen/<frageart>/fragen.json`
- Nutzung bereits ausgespielter Fragen: `runtime/quiz.sqlite3`, Tabelle
  `question_usage`
- Verbindliche Fragenregeln: `fragen/STECKBRIEF.md`
- Technische Bestandsdefinition: `fragen/manifest.json` und `questions.py`
- Bibliotheksprüfung: `python3 deploy/validate_question_library.py`

## Dauerhafte Arbeitsregeln

- Neue Chats lesen zuerst `AGENTS.md` und diese Datei vollständig.
- Fragen werden vor dem Speichern gegen alle Fragearten auf denselben Fakt,
  sinngleiche Wiederholungen und starke Überschneidungen geprüft.
- Fakten und Quellen werden tatsächlich recherchiert; `verified` bedeutet, dass
  die angegebene Quelle den Sachverhalt belegt.
- Vorhandene Fragen, IDs, Spielergebnisse und Nutzungseinträge bleiben erhalten.
- Neue Fragen müssen dem aktuellen Steckbrief entsprechen und vor der
  Live-Meldung die Bibliotheksprüfung bestehen.
- Fortschritt wird hier nur mit beobachtbaren Ergebnissen dokumentiert.

## Fragenbestand vor der Erweiterung

Live-Prüfung am 17.10.2026 vor Beginn dieses Auftrags:

| Frageart | Gesamtbestand | Unverbraucht |
|---|---:|---:|
| Wahr oder falsch | 218 | 11 |
| Auswahl | 215 | 10 |
| Paare bilden | 214 | 10 |
| Reihenfolge | 215 | 7 |
| Schätzung | 214 | 0 |

Ergebnis: Der Pool war blockiert, weil keine unverbrauchte Schätzfrage mehr
vorhanden war. Vollständige neue Runden waren dadurch nicht mehr möglich.

## Aktueller Auftrag vom 17.10.2026

### Phase 1 – Ausgleich

Erstellt und live geprüft:

- 11 Schätzfragen
- 1 Auswahlfrage
- 1 Paare-bilden-Frage
- 4 Reihenfolgefragen

Beobachteter Live-Stand nach dem Ausgleich: 11 unverbrauchte Fragen je aktiver
Frageart, 11 vollständige Runden, Pool nicht erschöpft.

### Phase 2 – Erweiterung

Nach erfolgreicher Phase 1 erstellt und live geschaltet:

- 50 neue Wahr-oder-falsch-Fragen
- 50 neue Auswahlfragen
- 50 neue Paare-bilden-Fragen
- 50 neue Reihenfolgefragen
- 50 neue Schätzfragen

Die 250 Fragen müssen recherchiert, dublettenfrei, thematisch abwechslungsreich,
steckbriefkonform und live validiert sein.

### Abschluss

- Gesamtprüfung der Fragenbibliothek und relevanter Tests
- Live-Status dokumentieren
- Aus den neu erstellten Fragen jeder aktiven Frageart genau eine Frage mit
  einem technischen Zufallsverfahren auswählen und dem Nutzer kurz vorlesen.
  Die Auswahl darf nicht redaktionell oder nach Präsentationswirkung erfolgen.

## Fortschritt und Prüfnachweise

- 17.10.2026: Ausgangsbestand und Live-Pool über `/health` geprüft.
- 17.10.2026: Bestehende Bibliothek vor der Erweiterung mit
  `deploy/validate_question_library.py` erfolgreich validiert.
- 17.10.2026: `AGENTS.md`, `PROJEKTLOG.md` und `PROMPTS.md` als dauerhafte
  Orientierung für neue Chats angelegt.
- 17.10.2026: Phase 1 mit 17 neuen Fragen abgeschlossen. Bibliotheksprüfung
  und 60 Tests bestanden; Live-Dienst anschließend mit exakt 11
  unverbrauchten Fragen je aktiver Frageart geprüft. Die vier neuen
  Reihenfolgefragen liegen wegen historisch bereits verbrauchter IDs bewusst
  im unbenutzten ID-Bereich `or401` bis `or404`.
- Phase 1: abgeschlossen.
- 17.10.2026: Phase 2 mit 250 neuen Fragen abgeschlossen, exakt 50 je aktiver
  Frageart. Neue IDs liegen je Typ im Bereich `500` bis `549`.
- 17.10.2026: Exakte Fragetexte, Themen-Steckbriefe und starke lexikalische
  Überschneidungen gegen den Gesamtbestand geprüft; gefundene Altbestands-
  Wiederholungen vor dem Anhängen ersetzt. Quellenlinks auf Erreichbarkeit
  geprüft und tote Links korrigiert.
- 17.10.2026: Gesamtbibliothek erfolgreich mit
  `deploy/validate_question_library.py` geprüft; anschließend 60 Tests mit
  `PYTHONPATH=.deps python3 -m unittest discover -s tests -p 'test_*.py'`
  bestanden.
- 17.10.2026: Öffentlichen Live-Endpunkt
  `https://igroup.it-sauther.de/guesstimate/health` geprüft. Beobachteter
  Stand: exakt 61 unverbrauchte Fragen je aktiver Frageart, 61 vollständige
  Runden, Pool nicht erschöpft.
- Phase 2: abgeschlossen und öffentlich live.
- 17.10.2026: Abschlussziehung einmalig mit `secrets.SystemRandom().choice()`
  aus allen 267 in diesem Auftrag neu erstellten Fragen ausgeführt. Gezogene
  IDs: `tf529`, `mc543`, `ma544`, `or537`, `es519`.

## Neuausrichtung des Mehrspielermodus

- 17.10.2026: Der bisherige Arbeitstitel und die bestehende grafische Richtung
  „Nerdiger Modus“ wurden verworfen. Der Modus wird als eigenständiges Spiel
  **Stormseed´s Perfect** neu gestaltet.
- Stormseed´s Perfect enthält keine Kategorienauswahl. Weitere Spielmodi werden
  später als eigene Reiter mit jeweils eigenem Ablauf ergänzt und gehören nicht
  in die Lobby von Stormseed´s Perfect.
- Für Stormseed´s Perfect werden getrennte Desktop-Zustände benötigt: Lobby aus
  Host-Sicht, Lobby aus Beitretenden-Sicht, Frage mit eigener Antworteingabe,
  Auswahl aus allen eingereichten Antworten, Host-Entscheidung über ebenfalls
  richtige Antworten, Punkteauflösung und Endergebnis.
- Die vorhandene technische Nerd-Modus-Implementierung bleibt bis zur gezielten
  Überarbeitung unangetastet; aus der bisherigen Oberfläche oder Bezeichnung
  folgt keine gestalterische Vorgabe für Stormseed´s Perfect.
- Auch die Mechaniken des bisherigen Nerd-Modus sind keine Vorgabe und dürfen
  nicht stillschweigend übernommen werden. Risikoregel, Hold’em und
  Kategorienwahl gehören nicht zu Stormseed´s Perfect. Das Spielende legt der
  Host ausdrücklich entweder über eine Zielpunktzahl oder eine Spielzeit fest.
- 17.10.2026: Für die neue Oberfläche wurde die warme, humorvolle Clubraum-
  Darstellung mit den vorhandenen Avataren, Pulten und Plaketten gegenüber der
  blauen Kontaktbogen-Variante bevorzugt. Benötigte Zustände sind als einzelne,
  vollständig sichtbare 16:9-Ansichten zu entwerfen, nicht als verkleinerter
  Kontaktbogen.
- Stormseed´s Perfect verwendet keine Lobbycodes. Vor dem Beitritt erscheint
  wie im Classic-Partymodus eine Übersicht der bestehenden Lobbys mit Status,
  Belegung und Beitreten-Schaltfläche; dort kann außerdem eine neue Lobby
  erstellt werden. Erst nach Auswahl beziehungsweise Erstellung öffnet sich die
  eigentliche Lobby mit den sichtbaren Mitspielern.
- 18.10.2026: Innerhalb einer geöffneten Lobby werden ausschließlich tatsächlich
  anwesende Personen dargestellt. Es gibt keine leeren Spielerplätze,
  Platzhalter oder „Freier Platz“-Pulte; beim Beitritt wird das Pult mit Avatar
  der neu hinzugekommenen Person dynamisch ergänzt.
- Die sieben festgelegten Desktopansichten wurden als einzelne visuelle
  Vollbildkonzepte ausgearbeitet: Lobbyübersicht zum Beitreten, Host-Lobby,
  Frage mit eigener Antworteingabe, anonyme Antwortauswahl, Host-Entscheidung,
  Punkteauflösung und Endergebnis. Diese Bilder sind Konzeptentwürfe; eine
  Umsetzung im Live-Spiel ist noch nicht erfolgt.
- 18.10.2026: Den Kartenbestand für Stormseed´s Perfect vor einer Live-
  Umsetzung vollständig strukturell geprüft. `begriffe/fragen.json` enthält
  390 Wikidata-Lexemdefinitionen; der Bestand ist quellenbelegt, aber nicht auf
  Blufftauglichkeit kuratiert und enthält viele unmittelbar verständliche
  Alltags- und Fachbegriffe wie Wachsmalstift, Einkaufsliste, Dosenöffner,
  Mikroskop oder Amtsgericht. `kuriositaeten/fragen.json` enthält 366 aus dem
  normalen Quizbestand kopierte Karten: 214 Schätzfragen und 152
  Multiple-Choice-Fragen. Davon tragen 258 weiterhin nur den Quellenstatus
  `legacy_bank`. Es handelt sich damit nicht um einen nachgewiesen geeigneten
  Nobody’s-Perfect-Kuriositätenbestand.
- Die aktuelle Nerd-Modus-Logik verwendet von den 366 Kuriositäten nur die 152
  ehemaligen Multiple-Choice-Fragen und schließt alle 214 Schätzfragen aus;
  auch diese 152 Karten wurden lediglich nach Herkunft gefiltert, nicht für
  das Bluffspiel redaktionell freigegeben.
- Konsequenz: Der Live-Ersatz durch Stormseed´s Perfect wurde bewusst noch
  nicht vorgenommen. Vor der Aktivierung müssen beide Bestände vollständig
  auf Eindeutigkeit, unbekannte aber fair erratbare Inhalte, glaubwürdige
  Bluffmöglichkeiten und belastbare Quellen kuratiert beziehungsweise neu
  aufgebaut werden.
- 18.10.2026: Eine anschließend vorgenommene automatische Reduktion auf 109
  Begriffe und 45 Kuriositäten erwies sich inhaltlich als falsch: Unter den
  angeblich geeigneten Karten befanden sich weiterhin offensichtliche Begriffe
  und gewöhnliche Zahlen- beziehungsweise Wissensfragen. Die vollständigen
  Ausgangsdateien mit 390 beziehungsweise 366 Karten wurden daraufhin exakt
  aus der lokalen Sitzungsaufzeichnung wiederhergestellt. Beide Dateien sind
  ausdrücklich ungeprüfter Altbestand und nicht zur Verwendung in
  Stormseed´s Perfect freigegeben.
- Für den neuen Modus ist stattdessen ein eigenständig recherchierter Bestand
  erforderlich: seltene reale Begriffe mit überraschender Definition sowie
  ungewöhnliche offene Warum-, Wozu- oder Was-geschah-Fragen. Reine Zahlen-,
  Jahres-, Autoren- und gewöhnliche Allgemeinwissensfragen sind ausgeschlossen.
- 18.10.2026: Den wiederhergestellten ungeprüften Altbestand anschließend auf
  ausdrücklichen Nutzerauftrag vollständig aus den beiden Serverdateien
  entfernt. `begriffe/fragen.json` enthält nun ausschließlich 8 einzeln anhand
  von Duden geprüfte seltene Begriffe. `kuriositaeten/fragen.json` enthält
  ausschließlich 8 neu recherchierte offene Kuriositäten aus institutionellen
  Quellen von NASA, Smithsonian, University of Oxford, Zoological Society of
  London und U.S. Naval History and Heritage Command. Keine dieser 16 Karten
  stammt aus dem normalen Guesstimate-Fragenbestand; Schätzfragen und
  `legacy_bank`-Einträge sind nicht enthalten.
- 18.10.2026: Den Neubestand nach weiterer Einzelrecherche auf 12 Begriffe und
  12 Kuriositäten erweitert. Ergänzt wurden vier seltene Duden-Begriffe sowie
  vier offene Geschichten zur ersten Webcam, Skinners taubengelenktem
  Flugkörper, einem per Paketpost beförderten Kind und Edisons sprechenden
  Puppen. Auch diese Karten besitzen einzeln geprüfte institutionelle Quellen.
- 18.10.2026: Den bisherigen Nerd-Modus vollständig durch **Stormseed´s
  Perfect** ersetzt. Der Ablauf besteht aus abwechselnden Begriffs- und
  Kuriositätenrunden: eigene Bluffantwort, anonyme Auswahl ohne Wahl der
  eigenen Antwort, Entscheidung des Hosts über weitere sachlich richtige
  Antworten, Punkteauflösung und Endergebnis. Eine richtige Wahl und jede
  erfolgreich getäuschte Person ergeben jeweils 100 Punkte.
- Die Lobbyübersicht übernimmt den Beitritt ohne Code aus dem Classic-
  Partymodus. In der geöffneten Lobby erscheinen ausschließlich tatsächlich
  anwesende Spieler mit ihren aktuellen Namen, Avataren und Pult-Skins. Der
  Host startet ausdrücklich, sobald mindestens ein Gast anwesend und jeder
  Gast bereit ist.
- Die alte Kategorienwahl und Risiko-/Hold’em-Regel werden vom Live-Modus nicht
  mehr verwendet. Der Host wählt vor dem Start zwischen 500 bis 5.000
  Zielpunkten und 5 bis 120 Minuten Spielzeit. Beim Zeitspiel wird die laufende
  Frage noch vollständig aufgelöst.
- Vor der Aktivierung `deploy/validate_question_library.py` erfolgreich
  ausgeführt. Anschließend 62 Tests einschließlich acht neuer vollständiger
  Stormseed´s-Perfect-Ablaufprüfungen bestanden. Der laufende Dienst war aktiv;
  der lokale Live-Endpunkt `/health` meldete `status: ok` und die Release-
  Kennung `2026.10.18-stormseeds-perfect-v1`; die neuen CSS- sowie JavaScript-
  Dateien wurden vom Dienst jeweils mit HTTP 200 ausgeliefert.

## Bereichsspezifische Spielregeln

- 18.10.2026: In Profil und Shop wird kein Regelknopf angeboten. Daily Quiz,
  Partymodus-Classic und Stormseed´s Perfect besitzen jeweils einen eigenen
  Regeltext unter dem einheitlichen Knopf „Spielregeln – So wird gespielt“.
- Der Partymodus-Classic zeigt einen eigenen Regeltext zu Lobbybeitritt,
  Host-Auswahl von 1 bis 5 Runden, fünf Fragearten pro Runde, gemeinsamem
  zeitabhängigem Punktespiel und der Trennung von iKühen und regulären
  Ranglisten. Die Daily-Regeln bleiben dem Daily Quiz vorbehalten.
- Die Bereichstrennung und Regeltexte wurden durch einen neuen Seitentest
  abgesichert; anschließend bestanden alle 63 Tests. Der laufende Gunicorn-
  Dienst übernahm die Änderungen per Auto-Reload; auf der öffentlichen
  Loginseite wurden die neue Knopfbeschriftung und der Daily-Regeltext
  beobachtet, der öffentliche `/health`-Endpunkt meldete `status: ok`.
- 18.10.2026: Die erste Stormseed´s-Perfect-Fassung nach Nutzerprüfung
  korrigiert: keine feste Zahl von acht Runden, keine Überschrift „Welche Runde
  darf es sein?“, kein Regeltext im Bühnenpanel. Die Lobbyübersicht verwendet
  stattdessen den Spruch „Oder weißt du etwa nicht, was ein Apotropaion ist?“
  und einen schlichten Lobby-erstellen-Ablauf.
- Die eigentliche Lobby verwendet einen neu aus der gewählten warmen Referenz
  abgeleiteten, leeren 16:9-Clubraum-Hintergrund. Avatare und Pulte bleiben
  dynamische Elemente und werden deutlich größer auf der Bühne angeordnet; das
  Host-Panel liegt kompakt oben rechts statt als große helle Karte in der
  Raummitte.
- Fragenprüfung und anschließend 66 Tests bestanden, darunter Prüfungen für
  beide Spielendbedingungen, eine neunte Runde ohne erreichtes Ziel und den
  bereichsspezifischen Perfect-Regeldialog.
- Der laufende Dienst meldete danach `status: ok` mit der Release-Kennung
  `2026.10.18-stormseeds-perfect-v2`. Stylesheet, Live-Skript und der neue
  Clubraum-Hintergrund wurden jeweils mit HTTP 200 ausgeliefert.
- 18.10.2026: Die geöffnete Stormseed´s-Perfect-Lobby nach erneuter
  Nutzerprüfung vollständig als interaktiven Clubraum aufgebaut. Das braune
  Einstellungsfenster und der sichtbare Speichern-Knopf wurden entfernt. Der
  Lobbyname ist links oben direkt änderbar; Punkte- oder Zeitende werden
  automatisch von einem Papierzettel auf dem Vordergrundtisch übernommen. Ein
  roter beschrifteter Tischbuzzer ist der eigentliche Startknopf.
- Der Lobbychat sitzt links unten; unmittelbar darüber stehen die drei
  Schnellreaktionen Daumen, Herz und Lachen. Chatnachrichten und Reaktionen
  werden serverseitig gespeichert und über die bestehende Lobbyaktualisierung
  an alle anwesenden Spieler verteilt.
- Die vorhandenen Pult-Skins werden nicht länger als flache Namensplakette
  dargestellt. Jeder Skin besitzt im Lobbybild nun einen vollständigen hohen
  Pultkörper mit seinem eigenen Material- und Farbschema; der vorhandene
  Pult-Asset bildet weiterhin die unveränderte individuelle Zierfront. Avatar,
  Name, Punktestand, Bereitschaft und Gastgeberstatus sind darin angeordnet.
- Der Clubraum-Hintergrund wurde um den gewünschten runden Holztisch mit freier
  Bedienfläche, Popcorn, Tasse und Büchern erweitert. Es sind weiterhin keine
  Spieler oder Bedienelemente in das Hintergrundbild eingebrannt.
- Vor der Live-Übernahme die Fragenprüfung und anschließend alle 67 Tests
  erfolgreich ausgeführt. Der aktive Dienst meldete danach `status: ok` mit
  Release `2026.10.18-stormseeds-perfect-v3`; Stylesheet, Live-Skript und der
  neue Tischhintergrund wurden vom laufenden Dienst jeweils mit HTTP 200
  ausgeliefert.
- 18.10.2026: Die Pultdarstellung nach Sichtprüfung korrigiert. Eine alte
  Lobby-CSS-Regel hatte die Namensfläche gleichzeitig von oben und unten
  positioniert und dadurch als große dunkle Fläche über Pultfront und
  Pultkörper gezogen. Die Namensfläche besitzt nun eine feste kleine Höhe in
  der originalen Skin-Front; der Pultkörper beginnt darunter, verjüngt sich
  nach unten und erhält einen Bodenschatten. Die künstlichen Neonleisten und
  Füße wurden entfernt.
- Den kleinen separaten Bereitschaftspunkt vollständig aus der
  Perfect-Vorlage entfernt. Gastgeberstatus erscheint goldbraun; die
  Bereitschaft von Gästen wird ausschließlich über die große Statusfläche am
  Pult gezeigt.
- Einstellungszettel und Startbuzzer perspektivisch an die Tischfläche
  angepasst, mit Kontakt- beziehungsweise Fallschatten versehen und die
  schmale Ansicht so geändert, dass Tischbedienung und Spieler im sichtbaren
  Bereich bleiben.
- Neu erstellte Perfect-Lobbys heißen automatisch `<Hostname>´s Runde`.
  Wartende Lobbys mit einem früher automatisch erzeugten Namen werden auf
  dieses Schema aktualisiert; selbst gewählte Lobbynamen bleiben unverändert.
- Fragenprüfung und alle 67 Tests bestanden. Der aktive Dienst meldete danach
  `status: ok` mit Release `2026.10.18-stormseeds-perfect-v4`; das neue
  Stylesheet wurde live mit HTTP 200 ausgeliefert.
- 18.10.2026: Die aus flacher Skin-Front und künstlich verlängerter CSS-Box
  zusammengesetzten Perfect-Pulte nach erneuter Nutzerprüfung vollständig
  verworfen. Startpult und alle 13 vorhandenen Pult-Skins besitzen nun je ein
  eigenständiges, hohes, transparent freigestelltes Pultobjekt mit sichtbarer
  Oberseite, tragfähigem Korpus und gemeinsam ausgerichtetem Fuß. Der Avatar
  steht direkt dahinter; Pultfuß und Bodenschatten liegen auf einer festen
  Standlinie hinter dem Tisch. Es gibt weiterhin keinen separaten
  Bereitschaftspunkt.
- Den gezeichneten CSS-Zettel und CSS-Buzzer ebenfalls ersetzt. Der
  Einstellungszettel ist jetzt ein perspektivisch flach aufliegendes
  Papierobjekt mit Materialkante und Kontakt-/Fallschatten. Der Startknopf ist
  ein freigestellter, plastischer roter Tischbuzzer mit Holz-/Messingsockel;
  seine Front trägt die Beschriftung „Spiel starten“.
- Die bisherigen Pult-Assets bleiben für Classic, Profil und Shop unverändert;
  die neuen hohen Varianten werden ausschließlich von Stormseed´s Perfect
  verwendet. Die Fragenprüfung und alle 67 Tests bestanden. Der lokale und
  öffentliche Live-Endpunkt meldeten `status: ok` mit Release
  `2026.10.18-stormseeds-perfect-v5`; Startpult, Pult 13, Papier und Buzzer
  wurden lokal und öffentlich jeweils mit HTTP 200 ausgeliefert.
- 18.10.2026: Größenverhältnis und Bodenwirkung der Perfect-Spieler nach
  Nutzerprüfung nachjustiert. Die Avatare sind kleiner und tiefer hinter den
  nun breiteren Pulten angeordnet; beide überlappen bewusst, sodass kein
  Hintergrundspalt mehr sichtbar ist. Die gemeinsame Standlinie liegt weiter
  unten. Ein weicherer Kontaktschatten sowie leicht an die Tiefenschärfe des
  Clubraums angepasste Pultgrafiken verbinden die freigestellten Objekte mit
  dem unscharfen Boden. Auch außerhalb der Lobby bleiben die vollständigen
  Pulte deutlich größer als zuvor.
- Die Wahlphase ist nicht länger anonym hinsichtlich der abstimmenden Person:
  Auf jeder Antwort erscheinen die Avatar-Köpfe der Personen, die sie gerade
  erwägen. Eine offene Wahl trägt eine gelbe Markierung; nach „Antwort
  einloggen“ wechselt derselbe Kopf für alle Beteiligten auf einen grünen
  Haken. Die Anzeige wird während der Wahl über die vorhandene
  Statusaktualisierung live nachgeführt.
- Die eigene erfundene Antwort darf nun gewählt werden. Eine Selbstwahl zählt
  weiterhin nicht als erfolgreiche Täuschung und erzeugt damit keinen eigenen
  Bluffpunkt. Spielregeltext und Ablaufprüfung wurden entsprechend geändert.
  Fragenprüfung und alle 67 Tests bestanden. Lokaler und öffentlicher
  Live-Endpunkt meldeten `status: ok` mit Release
  `2026.10.18-stormseeds-perfect-v6`; Stylesheet und Live-Skript wurden lokal
  und öffentlich mit HTTP 200 ausgeliefert.

## Religionsfreie Fragenbibliothek

- 18.10.2026: Religion als Fragethema dauerhaft ausgeschlossen. Die Regel ist
  in `AGENTS.md`, `PROMPTS.md` und `fragen/STECKBRIEF.md` festgehalten; die
  Kategorie `faith_religion` wurde aus dem Manifest entfernt. Zulässig bleibt
  nur eine beiläufige Erwähnung in echten Geografie-, Kunst- oder
  Geschichtsfragen, deren Auflösung kein Religionswissen verlangt.
- Sämtliche 38 aktiven Religionsfragen entfernt und eins zu eins durch neu
  recherchierte Fragen mit frischen IDs ersetzt: 15 Wahr/Falsch, 6 Auswahl,
  6 Paare, 5 Reihenfolgen und 6 Schätzungen. Die 250er-Erweiterung enthält
  damit weiterhin exakt 50 Fragen je aktiver Frageart. Die Gesamtzahlen der
  aktiven Dateien bleiben unverändert: 268 Wahr/Falsch, 266 Auswahl, 265
  Paare, 269 Reihenfolgen und 275 Schätzungen.
- Auch die sechs Religionsfragen der noch inaktiven Zwei-Gruppen-Frageart
  wurden durch sechs moderne Wortspiel- und Technikfragen ersetzt; der
  vorbereitete Bestand bleibt damit bei 60 Fragen.
- Die Korrektur ist mit `deploy/replace_religion_questions.py` reproduzierbar;
  beide früheren Erweiterungsskripte erzeugen keine Religionsfragen mehr.
  Die vollständige Fragenprüfung sowie alle 67 Tests bestanden.
- Der Gunicorn-Dienst übernahm den Fragenbestand per Auto-Reload. Lokaler und
  öffentlicher `/health`-Endpunkt meldeten anschließend `status: ok`, keine
  Erschöpfung und 53 vollständig spielbare Runden. Die geringere Zahl gegenüber
  dem früheren Stand von 61 ergibt sich aus der fortgeschriebenen
  Nutzungshistorie; Spielstände und `question_usage` wurden nicht verändert.
- 18.10.2026: Die bei der Zufallsstichprobe gezogene Auswahlfrage `mc605` zum
  Bluetooth-Logo auf Nutzerwunsch verworfen. Sie war zu leicht und verriet
  durch „Runen“ im Fragetext bereits die Struktur der Buchstabenantwort. Sie
  wurde vollständig aus Live-Datei und Generator entfernt und durch die neu
  recherchierte Frage `mc606` zur offiziellen Cheetos-Bezeichnung „Cheetle“
  ersetzt. Die Anzahl der Auswahlfragen und die 50er-Erweiterung bleiben
  unverändert. Fragenprüfung und alle 67 Tests bestanden; lokaler und
  öffentlicher `/health`-Endpunkt meldeten danach `status: ok` und weiterhin
  53 vollständig spielbare Runden.
- 18.10.2026: Auch die bei der nächsten Zufallsstichprobe gezogene
  Wahr/Falsch-Frage `tf600` zur Namensherkunft von Bluetooth auf Nutzerwunsch
  vollständig aus Live-Datei und Generator entfernt. Ersatz ist die neu
  recherchierte Frage `tf616` zur ursprünglichen Tapetenidee hinter
  Luftpolsterfolie; die neue ID verhindert eine Verwechslung mit der
  verworfenen Frage. Bestandszahlen und 50er-Erweiterung bleiben unverändert.
  Fragenprüfung und alle 67 Tests bestanden; lokaler und öffentlicher
  `/health`-Endpunkt meldeten danach `status: ok`, keine Erschöpfung und
  weiterhin 53 vollständig spielbare Runden.

## Kartentisch – lokale PC-Fassung

- 18.10.2026: Einen dritten Partymodus als zunächst deaktivierte lokale
  PC-Fassung angelegt. Der Modus heißt vorläufig „Kartentisch“ und wird nur bei
  gesetztem Schalter `QUIZ_ENABLE_CARD_TABLE=1` registriert und in der
  Navigation angezeigt. Er ist damit noch nicht öffentlich aktiviert.
- Die Lobby folgt dem vorhandenen Party-Aufbau, ist auf sechs Personen
  begrenzt und bietet ausschließlich die Kartensatzwahl 32, 52, 52 plus drei
  Joker, 104 oder 110 plus sechs Joker sowie den Startknopf.
- Das Spielfeld besitzt die getrennten Flächen A bis I: verdeckter Ziehstapel,
  offener Ablagestapel, Einsammeln, Mischen, gemeinsam gespeicherter Notizzettel
  mit acht Zeilen zu je 20 Zeichen, freie Kartenfläche, bis zu sechs
  Spielerpulte, Verlassen und Beenden mit Sicherheitsabfrage. Kartenbewegungen,
  Umdrehen und Notizen werden serverseitig synchronisiert; aus Stapeln kann nur
  die oberste Karte gezogen werden.
- 18.10.2026: Die Spielerpulte nach Nutzerklärung perspektivisch und privat
  umgesetzt. Das eigene Pult steht auf jedem Bildschirm stets unten und zeigt
  die dort abgelegten Karten ausschließlich dem Besitzer offen. Karten auf
  fremden Pulten bleiben verdeckt; Rang, Farbe und Symbol werden an fremde
  Browser gar nicht übertragen. Es findet weiterhin kein automatisches
  Austeilen oder Auffächern statt.
- Verdeckte Karten auf Ziehstapel und freier Tischfläche übertragen ebenfalls
  weder Rang, Farbe noch Symbol. Damit sieht auch die austeilende Person beim
  Ziehen und Bewegen nicht, welche Karte sie hält. Sichtbar wird eine Karte nur
  durch ausdrückliches Umdrehen auf der freien Fläche oder für den jeweiligen
  Besitzer nach dem Ablegen auf dessen eigenem Pult.
- 18.10.2026: PC-Tisch nach Sichtprüfung vergrößert. Spielerpulte besitzen nun
  das 2,5-Fache ihrer ursprünglichen Fläche, Karten die doppelte Breite und
  Höhe. F reicht weiter nach links; A und B schließen ohne Zwischenraum rechts
  daran an und ergeben zusammen exakt die Höhe von F. Der Verbund aus F, A und
  B bildet ein zentriertes Rechteck. Beim Ziehen vom Stapel bleibt ausdrücklich
  der Kartenrücken sichtbar; nur das eigene Pult deckt die dort abgelegte Karte
  für den Besitzer auf.
- 18.10.2026: Die abgenommene PC-Fassung anschließend auf ausdrücklichen
  Nutzerauftrag öffentlich aktiviert. `QUIZ_ENABLE_CARD_TABLE=1` ist in der
  Dienstdefinition hinterlegt; die Anwendung aktiviert den Modus auch beim
  laufenden Auto-Reload. Die erneute Fragenprüfung und alle 76 Tests bestanden.
  Lokaler und öffentlicher `/health`-Endpunkt meldeten `status: ok` mit Release
  `2026.10.18-card-table-v1`. Der öffentliche Kartentisch leitete ohne Sitzung
  erwartungsgemäß zur Anmeldung weiter; Stylesheet, Skript, Filzhintergrund und
  Kartenrückseite wurden über HTTPS jeweils mit HTTP 200 ausgeliefert.
- 18.10.2026: Den gemeinsamen Notizzettel auf Nutzerwunsch deutlich
  vergrößert. Er besitzt weiterhin acht dauerhaft sichtbare, direkt
  anklickbare Schreibzeilen, erlaubt nun aber 40 statt 20 Zeichen je Zeile.
  Browser- und Serverbegrenzung wurden gemeinsam angepasst.
- Einen dunkelgrünen Filzhintergrund und einen eigenständigen
  Guesstimate-Kartenrücken als neue lokale Bildassets erstellt. Standardwerte
  und Farben der Vorderseiten werden im Browser dargestellt.
- Fragenprüfung erfolgreich. Insgesamt 76 Tests bestanden, darunter neun
  neue Kartentisch-Ablaufprüfungen für alle fünf Kartensätze, Flächen A bis I,
  Stapelregeln, Sichtbarkeit, Notizzettel, Einsammeln, Mischen und Host-Rechte.
  Der laufende Dienst auf Port 8765 war bei der abschließenden lokalen Prüfung
  nicht erreichbar; eine öffentliche Live-Aktivierung wurde nicht behauptet
  und nicht vorgenommen.

## Oberflächenangleichung und technische Bestandsaufnahme

- 18.10.2026: Den Projektumfang für die Bestandsaufnahme ausdrücklich auf
  `/guesstimate/`, Profil, Shop, Partymodus-Classic, Stormseed´s Perfect und
  Kartentisch begrenzt. Das unabhängige `/login.html` gehört nicht dazu.
- Die gemeinsame Hauptnavigation in den Kernbereich Guesstimate/Profil/Shop
  und die Spielauswahl Classic/Perfect/Kartentisch gegliedert. Die Navigation
  bleibt eine gemeinsame Leiste; aktive Spiele besitzen lediglich eigene,
  zurückhaltende Farbakzente. Den Kopf der Perfect-Lobbyübersicht im Aufbau
  und Seitenrhythmus an Classic und Kartentisch angeglichen, ohne Spiellogik
  zu ändern.
- Danach Fragenprüfung und alle 76 Tests erfolgreich ausgeführt. Der lokale
  und öffentliche `/health`-Endpunkt meldeten `status: ok`, Release
  `2026.10.18-card-table-v1` und 53 vollständige unverbrauchte Runden. Beide
  geänderten Stylesheets wurden öffentlich mit HTTP 200 und identischer
  SHA-256-Prüfsumme zur lokalen Datei ausgeliefert.
- Anschließend eine ausschließlich lesende technische Bestandsaufnahme
  durchgeführt. Keine Altdatei wurde dabei gelöscht und keine Spiel- oder
  Nutzungsdaten wurden verändert. Als vorrangige offene Punkte bestätigt:
  fehlende Abwesenheitsbereinigung in Perfect und Kartentisch, sehr häufige
  schreibende Kartentisch-Statusabfragen, mögliche Doppelübermittlungsrennen
  bei Daily-, Classic- und Perfect-Antworten, dauerhaft im Startpfad liegende
  historische Datenkorrekturen, alte Nerd-Modus-Spalten und -Bezeichnungen,
  stark angewachsene überschreibende Stylesheets sowie fehlende produktive
  Härtung für Sitzungscookies, Geheimniskonfiguration und Loginversuche.
- Für spätere Bereinigung vorgemerkt, aber noch nicht entfernt: ausschließlich
  im Stylesheet verbliebene Regeln des ersetzten Perfect-Startkopfs sowie die
  im aktuellen Quellbestand nicht referenzierten Assets
  `arena-stage-background-v2.png`, `effects/anvil-comic-v1.png`,
  `guesstimate-share.png`, `instagram-guesstimate-2026-10-03.png` und
  `podiums/p03-brushed-steel.png`. Vor einer Löschung müssen öffentliche
  Direktverwendungen beziehungsweise externe Einbindungen gesondert
  ausgeschlossen werden.
- 18.10.2026: Die vorrangigen Mehrspielerprobleme anschließend behoben.
  Classic, Perfect und Kartentisch schreiben Anwesenheit nur noch nach einer
  vorherigen Leseprüfung und höchstens alle drei Sekunden. Perfect und
  Kartentisch markieren Personen nach 30 Sekunden ohne Statusabfrage als
  abwesend, übertragen bei Bedarf die Gastgeberrolle und schließen leere
  Lobbys. Abwesende Personen können einer noch wartenden Lobby wieder
  beitreten.
- Daily-, Classic- und Perfect-Antworten werden nun mit atomarem
  `INSERT OR IGNORE` gespeichert. Nahezu gleichzeitige Doppelübermittlungen
  erzeugen dadurch weder einen Fehler noch doppelte Punkte.
- Die beiden historischen, auf konkrete Spielernamen zugeschnittenen
  Shopkorrekturen vollständig aus `init_db()` entfernt. Ein neuer Test sichert
  nun das Gegenteil des früheren Verhaltens ab: Ein normaler Anwendungsstart
  verändert keinerlei Käufe oder Ausrüstung bestehender Nutzer.
- Aus der Perfect-Sollstruktur und der bestehenden Live-Datenbank die
  unbenutzten Altspalten `categories_json`, `holdem_enabled`, `chat_text`,
  `chat_at`, `stake` und `risk_points` entfernt. Aktuelle Lobby-, Runden-,
  Antwort- und Chatdaten blieben erhalten.
- Sämtliche CSS-Regeln des nicht mehr vorhandenen Perfect-Startkopfs und des
  nicht mehr verwendeten Regelbands entfernt; beide Perfect-Vorlagen verwenden
  nun dieselbe Stylesheet-Version. Eine vollständige mechanische Entfernung
  aller mehrfach definierten Regeln in `style.css` und `quiz-arena.css` wurde
  bewusst nicht vorgenommen, weil viele ältere Grundregeln von späteren
  Regeln nur teilweise überschrieben werden und blindes Löschen sichtbare
  Seiten beschädigen würde. Diese Konsolidierung benötigt seitenweise
  Sichtprüfung.
- Die fünf nicht referenzierten Bilddateien geprüft. Es sind keine identischen
  Dateiduplikate. Sie bleiben vorerst erhalten, weil drei davon eigenständige
  Veröffentlichungs- beziehungsweise Entwurfsbilder sein können und eine
  Löschung keinen Laufzeitfehler behebt; sie sind weiterhin keine aktiven
  Spielassets.
- Nach den Bereinigungen Fragenprüfung und alle nun 78 Tests erfolgreich.
  Lokaler und öffentlicher `/health`-Endpunkt meldeten `status: ok`, Release
  `2026.10.18-card-table-v1` und 53 vollständige Runden. Das bereinigte
  Perfect-Stylesheet wurde öffentlich mit HTTP 200 und identischer
  SHA-256-Prüfsumme ausgeliefert.

## Startseite „Variante A“ – 20.10.2026

- Die bisherige Arena-Startseite durch die vom Nutzer als **Variante A**
  bezeichnete dreiteilige Lobby ersetzt. Links steht eine persönliche
  Skin-Vitrine mit dem ausgerüsteten Avatar ohne eigenen Bildhintergrund, dem
  ausgerüsteten hohen Pult (Name im oberen Feld, unteres Feld frei), einer von
  der Decke hängenden Begrüßungsplakette, iKühen, ausgewähltem Spruch und den
  Pokalständen. Als Szenenhintergrund dient das vorhandene
  `stormseeds-perfect-clubroom-v1.png`.
- In der Mitte eine bedienbare Diashow für `guesstimate`, `guesstimate party`,
  `stormseed´s perfect` und `cardboard` mit echten vorhandenen Spielbildern,
  Kurzbeschreibung, Pfeilen, direkter Spielauswahl und passendem Aktionsknopf
  eingebaut. Für Guesstimate zeigt dieser abhängig vom Tagesstand `spielen`,
  `runde fortsetzen` oder `heutiges ergebnis`.
- Rechts die direkt sichtbare Rangliste mit den vier Umschaltern `tag`,
  `woche`, `hall of fame` und `wochensiege` eingebaut. `wochensiege` zählt
  abgeschlossene Wochenwertungen vor der laufenden Woche; geteilte erste
  Plätze werden jeweils als Sieg gewertet. Der frühere Live-Hinweis und der
  Verweis auf eine separate Gesamtrangliste entfallen auf der Startseite.

## Stormseed´s-Perfect-Spieltest – 20.10.2026

- Nach dem ersten Mehrspieler-Spieltest die Anwesenheitsbereinigung auf
  wartende Lobbys begrenzt. Ein gesperrtes Telefon oder verdeckter Browser-Tab
  kann damit während Countdown und laufendem Spiel keine Person mehr nach 30
  Sekunden entfernen. Ein neuer Ablauf testet ausdrücklich, dass bei 1.500
  Zielpunkten nach der ersten 100-Punkte-Runde die zweite Runde beginnt.
- Die Wahl ist bis zur Punkteauflösung vollständig geheim. Vorschauwahlen,
  Avatar-Markierungen auf Antwortkarten und Wahlwerte im Statuskanal wurden
  entfernt; andere Personen sehen nur noch den allgemeinen Abschlussstatus.
- Die wiederholt abgespielte Einzugsanimation der Pulte in der Lobby wurde
  deaktiviert. Dynamische Teilnehmer- und Bereitschaftsänderungen bleiben
  erhalten, ohne dass die Pulte bei jeder Aktualisierung neu ins Bild fahren.
- Fragenprüfung und alle 86 Tests erfolgreich ausgeführt.
- Die serverseitigen Korrekturen sind gespeichert, aber noch nicht vom
  laufenden Gunicorn-Prozess übernommen: `systemctl restart` wurde ohne
  Administratorrecht verweigert, `sudo` verlangt ein Passwort. Der zuletzt
  beobachtete lokale und öffentliche Health-Stand meldet deshalb weiterhin
  Release `2026.10.20-home-flyers-v1`. Erforderlicher offener Schritt ist ein
  administrativer Neustart von `guesstimate.service` mit anschließender
  lokaler und öffentlicher Live-Prüfung.

## Tabletop Connection – 20.10.2026

- Den bisherigen Navigationspunkt und Startseitenauftritt `playtable` in
  **Tabletop Connection** umbenannt. Das vorhandene Karussellmotiv
  `carousel-playtable-v1.png` dient zugleich als Hintergrund einer neuen
  Tabletop-Auswahlseite unter `/karten`.
- Die bisher direkt unter `/karten` gezeigte Kartentisch-Lobbyübersicht nach
  `/karten/kartentisch` verschoben und ausschließlich mit der ersten Kachel
  „Kartentisch – Spiel mit den Standard-Karten“ verknüpft. Lobby-, Beitritts-
  und Spielablauf blieben unverändert.
- Vier quadratische Kacheln für eine gemeinsame Reihe angelegt. Der Kartentisch
  ist anklickbar; Würfeltisch, Kniffel und Risiko sind mit eigenen, stilistisch
  zusammengehörigen Filztischmotiven sichtbar, aber ausdrücklich deaktiviert.
  Die vier Motive wurden mit der integrierten Bildgenerierung text- und
  logofrei erstellt und als versionierte Projektassets gespeichert.
- Fragenprüfung und alle 88 Tests erfolgreich ausgeführt. Zwei neue Tests
  sichern Anzahl, Beschriftung und Verlinkungszustand der Kacheln sowie den
  unverändert erreichbaren Kartentisch-Lobbybrowser ab.
- Der administrative Dienstneustart wurde in der Arbeitsumgebung erneut mit
  `Access denied` verweigert. Der öffentliche Health-Endpunkt meldete danach
  `status: ok`, aber noch Release `2026.10.20-perfect-playtest-fix-v1`; das
  neue Kartentisch-Kachelbild wurde bereits mit HTTP 200 ausgeliefert. Für die
  serverseitige Route und Vorlage bleibt ein administrativer Neustart mit
  anschließender Live-Prüfung offen.

### Quellen für wiederverwendbare Tabletop-Bausteine

- 23.10.2026: Für künftige Tabletop-Arbeiten dauerhaft vorgemerkt: itch.io als
  Fundstelle für kostenlos angebotene 3D-Modelle und Spielassets, dddice als
  Quelle der im Projekt bereits verwendeten 3D-Würfeltechnik sowie DiceyTable
  als Referenz für Bedienung, Kartenstapel, Tischaufbau und Physikverhalten.
- Vor jeder Übernahme ist die konkrete Lizenz des jeweiligen Modells oder
  Werkzeugs zu prüfen. „Kostenlos“ bedeutet nicht automatisch, dass eine
  Weitergabe, Bearbeitung oder öffentliche Nutzung erlaubt ist.
- DiceyTable bleibt Prototyp- und Referenzumgebung. Die dortige Laufzeitengine,
  Kamera, Physik und eingebauten Presets werden nicht als Bestandteil von
  Guesstimate übernommen. In das eigene Projekt gelangen nur selbst erstellte
  beziehungsweise nachweislich passend lizenzierte Dateien und eigenständige
  Web-Bausteine.

### Stormseed’s Conquest – Übernahme in das eigene Projekt

- 23.10.2026: Den selbst erstellten Bestand aus
  `dabrain1982-cyber/stormseed-s-diceytable` in die eigene Tabletop Connection
  übernommen: drei Brettstile, je drei Länder- und Missionskartenbögen samt
  Rückseiten sowie das verbindliche Modell mit 42 Gebieten, 12 Missionen,
  sechs Kontinenten und vollständigen Nachbarschaften. Laut mitübernommener
  Projektdokumentation wurden die Geodaten aus dem gemeinfreien Natural-Earth-
  Bestand abgeleitet und Grafik, Kartenaufbau und Name eigenständig erstellt.
- Unter `/karten/welteroberung` eine erste eigenständige Spielwerkbank
  angelegt. Sie besitzt Stilwechsel, anklickbare Gebiete mit Nachbaranzeige,
  zieh- und umdrehbare Länder- und Missionskarten, eine auf die Brettmitte
  ausgerichtete Kamera mit zusätzlichem Verschieben/Drehen sowie die bereits im
  Projekt verwendete dddice-Würfeltechnik. Der bisher deaktivierte Eintrag in
  Tabletop Connection verweist nun auf diese Werkbank und heißt
  `Stormseed’s Conquest`.
- Dies ist noch kein vollständiger synchronisierter Mehrspielermodus und keine
  fertige Regelautomatik. Die technische Grundlage ist lokal gespeichert;
  Fragenprüfung und alle 125 Tests bestanden. Die echte Sicht- und
  Interaktionsprüfung im laufenden Browser sowie die kontrollierte Übernahme
  durch den Produktionsprozess sind zu diesem Zeitpunkt noch offen.
- Die neue Route wurde über die getrennte lokale Vorschauanwendung mit HTTP
  200 ausgeliefert. Der kontrollierte Neustart von `guesstimate.service` wurde
  jedoch sowohl direkt mit `Access denied` als auch über `sudo -n` wegen des
  erforderlichen Administratorpassworts abgelehnt. Der öffentliche Aufruf von
  `/guesstimate/karten/welteroberung` lieferte deshalb weiterhin HTTP 404; die
  neue Werkbank ist ausdrücklich noch nicht öffentlich aktiv oder visuell im
  Produktionsbrowser abgenommen.
- Nach Nutzerkorrektur die Tabletop-Auswahl auf dieselbe maximale Arbeitsbreite
  von 1.540 Pixeln wie den Desktop-Shop gesetzt. Dadurch besitzen vier
  quadratische Kacheln dieselbe Größenordnung wie die Pultkacheln. Den
  irrtümlich hinzugefügten großen dunklen Seitenrahmen vollständig entfernt
  und den Originalnamen `carousel-playtable-v1.png` beibehalten.
- Anschließend die tatsächliche Ursache des weiterhin falschen Hintergrunds
  behoben: Die globale persönliche Profilkulisse überschrieb mit
  `!important` die Tabletop-Regel. Tabletop Connection erzwingt nun gezielt
  und ohne Farbfilter `carousel-playtable-v1.png`; die globale Noise-Schicht
  ist auf dieser Seite deaktiviert. Stylesheet-Cachekennung auf `v=6` erhöht.
- Dieselbe gezielte Hintergrundbehandlung anschließend auf die beiden anderen
  Multiplayer-Übersichten übertragen: Classic verwendet
  `carousel-party-classic-v1.png`, Stormseed´s Perfect verwendet
  `carousel-stormseeds-perfect-v1.png`. Beide Regeln überschreiben dort die
  persönliche Profilkulisse und blenden die Noise-Schicht aus; geöffnete
  Lobbys und Spielansichten bleiben unverändert.
- Die gemeinsame obere Leiste lautet nun in dieser Reihenfolge `guesstimate`,
  `profil`, `shop`, `regeln`, gefolgt von der separat eingefassten Gruppe
  `multiplayer` mit `guesstimate party`, `stormseed´s perfect` und `cardboard`;
  das Datum steht rechts. Nur Profil, Shop, Regeln und Datum tragen Symbole.
  Der separate iKuh-Shop-Knopf und der separate Regelknopf wurden für
  angemeldete Nutzer entfernt; beide Funktionen liegen in der Hauptleiste.
- Die Umsetzung ist dynamisch und verwendet die tatsächlichen Kontodaten,
  Skins, Pulte, Plaketten, Punktestände und Links; es handelt sich nicht um ein
  aufgelegtes Entwurfsbild. Kennung des Live-Stands:
  `2026.10.20-home-variant-a-v1`.
- Rücknahmehinweis: Die spätere Anweisung **„Variante A rückgängig machen“**
  bezeichnet genau die in diesem Abschnitt dokumentierte Startseiten-,
  Navigations-, Diashow- und Wochensiege-Änderung. Andere, bereits vorher im
  Arbeitsbaum vorhandene Änderungen dürfen dabei nicht zurückgesetzt werden.
- Prüfung: `deploy/validate_question_library.py` erfolgreich; alle 78 Tests
  erfolgreich. `guesstimate.service` aktiv. Lokaler und öffentlicher
  `/health`-Endpunkt meldeten `status: ok`, Release
  `2026.10.20-home-variant-a-v1`. Das öffentlich ausgelieferte
  `quiz-arena.css?v=50` und `home-variant-a.js?v=1` stimmte jeweils per
  SHA-256 exakt mit dem lokalen Live-Bestand überein.

## Persönliche Hintergrundmotive – 20.10.2026

- Sieben frühere Oberflächenentwürfe erneut als Bildreferenzen gesichtet. Die
  bereits vorhandene blaue Arena `arena-stage-background-v1.png` und der warme
  Clubraum `stormseeds-perfect-clubroom-v1.png` bleiben unverändert erhalten.
- Aus den übrigen eigenständigen Bildrichtungen fünf saubere, elementfreie
  Spielszenen ohne Menüs, Beschriftungen, Figuren oder Wasserzeichen erzeugt
  und im Live-Arbeitsordner gespeichert: `background-wissensatelier-v1.png`,
  `background-neon-garten-v1.png`, `background-bergsee-v1.png`,
  `background-quiz-kosmos-v1.png` und `background-gameshow-arena-v1.png`.
- Die neuen Dateien sind zunächst nur Bildassets. Shopkatalog, Kauf,
  Profilauswahl und persönliche Anwendung als Seitenhintergrund sind noch
  nicht implementiert oder öffentlich aktiviert.
- Den überwiegend dunklen, blau-violetten beziehungsweise warm-bernsteinfarbenen
  Bestand um drei bewusst andersartige 16:9-Motive ergänzt: den hellen
  mediterranen Tagesraum `background-mediterraner-hof-v1.png`, die taktile
  Papiercollage `background-papierlandschaft-v1.png` und die pastellfarbene
  Traumlandschaft `background-wolkenpavillon-v1.png`. Alle drei sind
  elementfreie Hintergrundassets ohne Text, Figuren, Bedienoberfläche oder
  Wasserzeichen und haben 1672 × 941 Pixel.
- 20.10.2026: Persönliche Hintergründe vollständig in Shop, Profil und
  Hauptseite eingebunden. Der zuvor live verwendete
  `arena-stage-background-v1.png` ist als kostenlose `Neon-Arena` (`b00`)
  Standardbesitz und durch den Datenbankstandard bei allen bestehenden und
  neuen Spielern ausgerüstet, solange sie keinen anderen Hintergrund wählen.
- Zehn weitere Kulissen sind als kaufbare Shopartikel zu je 2.500 iKühen
  verfügbar. Der Shop zeigt kompakte 16:9-Vorschauen; gekaufte Kulissen werden
  im Profil ausgerüstet. Dieselbe Auswahl steuert sowohl das persönliche
  Avatar-/Pult-Fenster auf der Hauptseite als auch den gesamten sichtbaren
  Guesstimate-Seitenhintergrund. Die eigenständigen Bühnen von Perfect und
  Cardboard wurden nicht umgestaltet.
- Die Kosmetikdaten wurden abwärtskompatibel um `background_id` erweitert;
  Avatar- und Pultausrüstung sowie bestehende Käufe bleiben erhalten. Ein neuer
  Ablaufprüftest deckt Standardbesitz, Shopkauf, Ausrüstung und beide
  Darstellungen ab.
- Fragenprüfung erfolgreich und alle 79 Tests bestanden. Der aktive lokale und
  öffentliche Dienst meldete `status: ok` und Release
  `2026.10.20-personal-backgrounds-v1`; `quiz-arena.css?v=51` und der geprüfte
  neue Hintergrund wurden lokal sowie öffentlich mit HTTP 200 ausgeliefert.
- 20.10.2026: Ausschließlich für den konfigurierten Besitzer-Account
  `stormseed` ein Entwickler-Häkchen im Profil ergänzt. Ist es aktiviert,
  gelten alle aktuellen Avatare, Pulte und Hintergründe virtuell als im Besitz
  und können ausgerüstet werden, ohne Käufe anzulegen oder iKühe abzuziehen.
  Andere Accounts sehen die Einstellung nicht; ein direkter Aufruf der Route
  wird serverseitig mit HTTP 403 abgewiesen.
- Beim Abschalten bleiben echte Käufe erhalten. Ausschließlich durch den
  Entwicklermodus verfügbare, noch ausgerüstete Artikel werden auf den
  jeweiligen kostenlosen Standard zurückgesetzt. Der Zustand liegt im neuen
  Feld `user_cosmetics.developer_enabled` und ist standardmäßig deaktiviert.
- Die Profilvorschau „So sehen dich die anderen“ verwendet nun dieselbe
  vollständige Szenendarstellung wie das persönliche Fenster auf der
  Hauptseite: gewählter Hintergrund, Hängeplakette, Avatar, hohes Pult,
  Spielername und Spruch.
- Fragenprüfung erfolgreich und alle nun 80 Tests bestanden. Der aktive lokale
  und öffentliche Dienst meldete `status: ok` mit Release
  `2026.10.20-owner-developer-mode-v1`; `quiz-arena.css?v=52` wurde lokal mit
  HTTP 200 ausgeliefert.
- 20.10.2026: Die erste Profilkopie war im Browser bis auf einen schmalen
  Bildstreifen zusammengefallen. Ursache war eine später geladene ältere
  `.variant-a-profile-scene`-Regel mit `min-height: 0`, welche die zuvor
  definierte Fensterhöhe überstimmte. Die Profilkopie besitzt nun in der
  finalen CSS-Priorität eine eigene feste responsive Szenenhöhe; Hintergrund,
  Hängeplakette, Avatar und Pult bleiben dadurch vollständig sichtbar.
- Eine neue Strukturprüfung sichert ab, dass die sichtbare Profilfensterregel
  nach der zusammenklappenden Grundregel steht. Fragenprüfung und alle nun 81
  Tests bestanden. Live-Kennung nach der Korrektur:
  `2026.10.20-owner-developer-mode-v2`, Stylesheet-Version `v=53`.

## Persönliche Sprüche und neue Hintergrundpreise – 20.10.2026

- Alle 40 vom Nutzer freigegebenen humorvollen, provokanten Spielersprüche als
  kaufbare Shopartikel angelegt. Jeder Spruch kostet 250 iKühe. Besitz und
  Ausrüstung werden getrennt gespeichert; noch nicht gekaufte Sprüche können
  nicht ausgerüstet werden.
- Im Profil einen eigenen Sprüche-Reiter ergänzt. Der dort ausgerüstete Spruch
  erscheint im persönlichen Fenster auf Hauptseite und Profil sowie während
  der Daily-Quizrunde und auf der Ergebnisseite. Ohne ausgerüsteten Spruch wird
  der neutrale Hinweis „Noch kein Spruch gewählt.“ angezeigt.
- Den Preis aller zehn kaufbaren persönlichen Hintergründe von 2.500 auf 1.000
  iKühe geändert. Bereits gespeicherte Käufe und deren historische Kaufpreise
  bleiben unverändert; der neue Preis gilt für künftige Käufe.
- Der Besitzer-Entwicklermodus schaltet nun auch alle Sprüche virtuell frei und
  setzt einen nur virtuell ausgerüsteten Spruch beim Abschalten sicher zurück.
- Fragenprüfung erfolgreich und alle nun 82 Tests bestanden. Der lokale und
  öffentliche `/health`-Endpunkt meldeten `status: ok`, 51 vollständige
  unverbrauchte Runden und Release `2026.10.20-phrases-v1`; das öffentliche
  `quiz-arena.css?v=55` wurde mit HTTP 200 ausgeliefert.

## Abgegrenztes Typografiepaket – 20.10.2026

- Die variablen Schriften Inter und Fredoka aus dem offiziellen Google-Fonts-
  Bestand samt OFL-Lizenz lokal unter `static/fonts/` hinterlegt. Es gibt keine
  Abhängigkeit von einem externen Schriftserver. Inter wird für Bedienung,
  Fließtext, Rangliste und Zahlen verwendet; Fredoka ausschließlich für
  Markenname, große Spieltitel und wichtige Überschriften.
- Für die Hauptseite die kleinsten Navigations-, Reiter-, Beschreibungs-,
  Spruch- und Pokaltexte moderat vergrößert. Sichtbare Extremgewichte wurden
  dort auf echte variable Schriftschnitte reduziert; der persönliche Spruch
  ist zugunsten der Lesbarkeit nicht mehr kursiv.
- Die gesamte gestalterische Änderung liegt gekapselt in
  `static/typography-v1.css`. Die spätere Anweisung **„diese Schriftänderung
  rückgängig machen“** bedeutet: ausschließlich die Einbindung dieser Datei in
  `templates/base.html` entfernen, die drei Dateien in `static/fonts/` sowie
  `typography-v1.css` entfernen und die Release-Kennung auf den vorherigen
  Stand `2026.10.20-phrases-v1` zurücksetzen. Andere Änderungen bleiben
  unangetastet.
- Fragenprüfung erfolgreich und alle nun 83 Tests bestanden. Lokaler und
  öffentlicher `/health`-Endpunkt meldeten `status: ok`, Release
  `2026.10.20-typography-v1`. Stylesheet, Inter und Fredoka wurden lokal und
  öffentlich jeweils mit HTTP 200 ausgeliefert.

## Profilbühne und Größenverhältnisse – 20.10.2026

- Das Profil als breite Desktop-Garderobe umgesetzt: links steht die große
  ausgerüstete Originalbühne, rechts die Sammlung mit vier Reitern; der
  vollständige Pokalschrank bildet eine kompakte gemeinsame Leiste darunter.
  Die Hauptseitenfassung derselben Komponente bleibt in diesem Schritt in
  ihrer bisherigen kompakten Anordnung erhalten.
- Auf der Profilbühne ersetzt der gewählte persönliche Spruch die frühere
  Begrüßung in der Hängeplakette. Der iKuh-Stand steht im unteren Feld des
  hohen Pults, der Spielername im oberen. Ein separates Spruchfeld unter dem
  Pult entfällt; das Pult bildet den unteren Abschluss der Bühne.
- Avatar und Pult werden als getrennte Ebenen skaliert. Die gemeinsame
  Grundproportion gilt für alle 19 Avatarzustände einschließlich Startfigur;
  breite beziehungsweise besonders schmale Motive besitzen zusätzliche
  Korrekturen. Für Startpult und alle 13 kaufbaren Pulte sind die abweichenden
  Positionen von Namens- und iKuh-Feld einzeln hinterlegt.
- Markenblock und Hauptnavigation vergrößert. `stormseed´s` sitzt als enge
  obere Zeile direkt auf dem größeren `guesstimate`; die drei
  Multiplayer-Schaltflächen besitzen kompaktere feste Breiten.
- Fragenprüfung erfolgreich und alle nun 84 Tests bestanden. Der aktive Dienst
  sowie lokaler und öffentlicher `/health`-Endpunkt meldeten `status: ok` mit
  Release `2026.10.20-profile-stage-v1`. Das öffentliche
  `quiz-arena.css?v=56` war per SHA-256 identisch mit dem lokalen Live-Bestand.
- Die erste Live-Sichtprüfung der Navigation zeigte, dass das später geladene
  Typografiepaket die vergrößerten Schriftwerte wieder überschrieb und eine
  ältere Rasterregel den Multiplayer-Rahmen über freie Breite streckte. Die
  abschließenden Navigationswerte liegen deshalb nun im separat zuletzt
  geladenen `profile-stage-v1.css`: größerer eng gestapelter Markenblock,
  lesbarere Hauptnavigation sowie ein auf den Inhalt begrenzter
  Multiplayer-Rahmen. Fragenprüfung und 84 Tests erneut erfolgreich; neue
  Release-Kennung `2026.10.20-profile-stage-v2`.
- Nach Sichtprüfung der Hauptseite den dort noch aktiven alten Profilzweig
  entfernt: persönlicher Spruch und iKuh-Stand stehen nun auf Profil und
  Hauptseite identisch in Hängeplakette beziehungsweise unterem Pultfeld; die
  frühere Begrüßung sowie die separaten Spruch- und Guthabenblöcke entfallen.
  Die Erfolgszeile unter der Hauptseitenbühne und das Ranglistenpanel besitzen
  einen transparenten statt dunkelblauen Flächenhintergrund.
- Den horizontalen Ranglistenüberlauf behoben. Ursache war die Kombination aus
  einer auf 86 Prozent verkleinerten Liste und festen Mindestbreiten der
  Skin-Zeilen. Die Liste nutzt nun exakt die verfügbare Breite, alle inneren
  Raster dürfen schrumpfen und horizontaler Überlauf ist ausgeschlossen;
  vertikales Blättern bei längeren Ranglisten bleibt erhalten.
- Fragenprüfung und alle 84 Tests erneut erfolgreich. Release-Kennung nach
  diesen Korrekturen: `2026.10.20-profile-stage-v3`.
- Namens- und iKuh-Texte werden nicht mehr mit einer festen Schriftgröße in
  alle Pulte gezwungen. Beide Texte besitzen pultspezifische, horizontal und
  vertikal zentrierte Feldgrenzen und werden nach dem Laden der lokalen
  Schriften sowie bei Größenänderungen tatsächlich gegen die verfügbare
  Fläche gemessen. Nur wenn ein Text übersteht, wird dessen Schrift schrittweise
  verkleinert. Das höhere Namensfeld des Tavernenschilds ist separat
  berücksichtigt. Fragenprüfung und 84 Tests bestanden; Release
  `2026.10.20-profile-stage-v5`.
- Die tatsächliche P01-Grafik anschließend gegen die Live-Aufnahme geprüft:
  Beim Tavernenschild lag das untere Feld deutlich tiefer als die zuvor
  geschätzte allgemeine Feldlage. iKühe stehen dort nun bei 74 Prozent der
  Pult-Höhe mittig im grünen unteren Rahmen; der Name wurde innerhalb des
  großen oberen Holzrahmens ebenfalls nach unten vermittelt. Release
  `2026.10.20-profile-stage-v6`.

## Hauptseiten-Titelfläche – 20.10.2026

- Die permanente Markeninszenierung in die mittlere Hauptseitenspalte
  zurückgebracht: `stormseed´s` steht über dem großen `guesstimate`, darunter
  bleiben Tagesquiz-Untertitel und Kurzbeschreibung unabhängig vom sichtbaren
  Karussellbild erhalten.
- Die vier Modusreiter unter dem Karussell vollständig entfernt. Bilder
  wechseln weiterhin automatisch oder über die beiden Pfeile; sie sind kein
  zweiter Navigationsweg. Party, Perfect und Cardboard werden ausschließlich
  über die obere Hauptnavigation geöffnet.
- Unter dem Karussell steht nur noch die Tagesquiz-Aktion. Sie bleibt je nach
  Tagesstand `spielen`, `runde fortsetzen` oder `heutiges ergebnis` und ändert
  sich beim Bildwechsel nicht mehr in eine Multiplayer-Aktion.
- Profilplakette, Avatar und Pult auf der Hauptseite gemeinsam tiefer gesetzt
  und den zu großen Abstand zwischen Plakette und Figur reduziert. Die
  Ranglisteninhalte beginnen ebenfalls tiefer; fünf Einträge passen sichtbar,
  weitere Einträge werden ausschließlich vertikal gescrollt.
- Fragenprüfung und alle 84 Tests bestanden. Release-Kennung:
  `2026.10.20-home-title-screen-v1`.

## Profil- und Shopbreite – 20.10.2026

- Die widersprüchliche Normalmonitor-Begrenzung aufgehoben, durch die die
  breite Profil-Arbeitsfläche über ihren Container hinausragte und optisch
  nicht zentriert erschien. Profil und Shop verwenden auf Desktop nun beide
  dieselbe ausdrücklich zentrierte Arbeitsbreite bis 1.540 Pixel.
- Die zusätzliche Shopbreite wird für vier Artikel je Reihe genutzt. Das gilt
  einheitlich für Avatare, Pulte, Hintergründe und Sprüche; unterhalb der
  Desktopbreite bleiben die bisherigen responsiven Umbrüche bestehen.
- Fragenprüfung und alle 84 Tests bestanden. Der aktive lokale und öffentliche
  `/health`-Endpunkt meldeten `status: ok` mit Release
  `2026.10.20-profile-shop-alignment-v1`. Das öffentliche
  `profile-stage-v1.css?v=5` wurde mit HTTP 200 und identischer SHA-256-Prüfsumme
  zur lokalen Datei ausgeliefert.

## Ranglistenfläche der Hauptseite – 20.10.2026

- Die feste maximale Listenhöhe von 405 Pixeln auf Desktop entfernt. Die
  Rangliste nutzt nun die gesamte verbleibende Höhe ihres rechten Panels;
  vorhandene Einträge bleiben oben kompakt angeordnet.
- Eine vertikale Scrollleiste erscheint erst, wenn die Ranglisteneinträge die
  tatsächlich verfügbare Fläche überschreiten. Die kleineren responsiven
  Ansichten behalten ihre gesonderten Höhenbegrenzungen.
- Fragenprüfung und alle 84 Tests bestanden. Lokaler und öffentlicher
  `/health`-Endpunkt meldeten `status: ok` mit Release
  `2026.10.20-leaderboard-scroll-v1`; das öffentliche
  `profile-stage-v1.css?v=6` war per SHA-256 identisch mit der lokalen Datei.
- Die erste Korrektur war unvollständig: Ohne feste Desktop-Bühnenhöhe konnte
  ein achter Rang die gesamte dreispaltige Hauptseite weiterhin nach unten
  vergrößern. Die Bühne ist nun auf die tatsächlich verfügbare Viewporthöhe
  begrenzt; sieben passende Einträge bleiben vollständig sichtbar, weiterer
  Inhalt scrollt innerhalb der Ranglistenfläche und verändert weder Panel noch
  Hintergrundkomposition.
- Fragenprüfung und alle 84 Tests erneut bestanden. Lokaler und öffentlicher
  `/health`-Endpunkt meldeten `status: ok` mit der korrigierten Release-Kennung
  `2026.10.20-leaderboard-scroll-v2`; `profile-stage-v1.css?v=7` war öffentlich
  per SHA-256 identisch mit der lokalen Datei.
- Auch diese zweite Fassung scrollte im Browser noch nicht: Das aktive
  Reiter-Panel zwischen Ranglistenrahmen und Liste hatte weiterhin eine
  inhaltsgetriebene Mindesthöhe. Es ist nun selbst die begrenzte, flexible
  Restfläche; die Liste erhält dadurch echten Überlauf und kann innerhalb des
  unveränderten Panels scrollen.
- Fragenprüfung und alle 84 Tests bestanden. Die bestehende semantische
  Scroll-Kennzeichnung ab mehr als fünf realen Spielern bleibt kompatibel;
  sichtbar wird die automatische Scrollleiste weiterhin erst bei tatsächlichem
  Platzmangel. Lokaler und öffentlicher `/health`-Endpunkt meldeten `status: ok`
  mit Release `2026.10.20-leaderboard-scroll-v3`; das öffentliche
  `profile-stage-v1.css?v=8` war per SHA-256 identisch mit der lokalen Datei.
- Die dritte Fassung scrollte zwar, ließ das CSS-Raster seine automatischen
  Rangzeilen aber bis unter die Höhe der darin liegenden Pulte stauchen. Dadurch
  überlappten bis zu elf Einträge, während oberhalb der Rangliste ein unnötiger
  Abstand von 68 Pixeln blieb. Diesen Abstand auf die normale Panelpolsterung
  von 18 Pixeln reduziert und jede Desktop-Rangzeile verbindlich auf 72 Pixel
  mit 10 Pixel Abstand festgelegt. Damit bleiben sieben vollständige Einträge
  lesbar; der achte liegt im echten Scrollbereich, ohne Pulte zu stauchen.
- Fragenprüfung und alle 84 Tests bestanden. Lokaler und öffentlicher
  `/health`-Endpunkt meldeten `status: ok` mit Release
  `2026.10.20-leaderboard-scroll-v4`; das öffentliche
  `profile-stage-v1.css?v=9` war per SHA-256 identisch mit der lokalen Datei.

## Fünfteiliges Hauptseiten-Karussell und Playtable – 20.10.2026

- Vier neue, textfreie 16:9-Karussellbilder mit der integrierten Bildgenerierung
  erstellt und als eigene Projektassets eingebunden: tägliches Quiz mit fünf
  Fragearten, Guesstimate Party Classic als gemeinsame Tier-Spielshow,
  Stormseed´s Perfect als warmes Bluff-Clubzimmer sowie Playtable als kreativ
  vermischter Tisch aus Schach, Dame, Karten, Würfeln und Welteroberungsspiel.
- Das vom Nutzer bereitgestellte Hochformat-Geburtstagsmotiv unverändert als
  fünfte Folie eingebunden. Es wird vollständig und ohne Beschnitt innerhalb
  des mittleren Fensters dargestellt.
- Das Karussell wechselt nun automatisch exakt alle zehn Sekunden; Pfeile sowie
  Pausieren bei Maus- und Tastaturinteraktion bleiben erhalten.
- Die sichtbare Bezeichnung `cardboard` beziehungsweise `Kartentisch` in
  Navigation, Hauptseite, Lobby, Spieltitel, Hinweisen und Standard-Lobbynamen
  durch `Playtable` ersetzt. Interne Routen und technische Bezeichner bleiben
  zur Wahrung der Kompatibilität unverändert.
- Fragenprüfung und alle 84 Tests bestanden. Alle fünf Bildassets wurden
  öffentlich mit HTTP 200 und jeweils identischer SHA-256-Prüfsumme zur lokalen
  Datei ausgeliefert. Lokaler und öffentlicher `/health`-Endpunkt meldeten
  `status: ok` mit Release `2026.10.20-home-carousel-v1`; das öffentliche
  Karussellskript enthält den geprüften 10.000-Millisekunden-Takt.
- Die fünf Karussellmotive anschließend als austauschbare Flyer aufgebaut.
  Bilddatei und dekorative Textebene bleiben getrennt, sodass einzelne Motive
  ohne Neugenerierung des Textes ersetzt oder vollständig entfernt werden
  können. Jeder Flyer zeigt den jeweiligen Spielnamen und den vom Nutzer
  vorgegebenen Erklärungssatz; das Geburtstagsmotiv besitzt eine entsprechende
  Grußplakette.
- Nach einem vom Nutzer gemeldeten größeren Serverausfall keine weiteren
  parallelen Bildgenerierungen oder speicherintensiven Sammeloperationen
  ausgeführt. Die sichtbaren Dienstinformationen enthielten keinen Beleg für
  die Ursache. Der Dienst lief bei der anschließenden Prüfung seit 21:29 Uhr
  aktiv, mit `NRestarts=0` und rund 71–73 MB Speicher. Bibliotheksprüfung und
  alle 84 Tests wurden danach einzeln mit niedriger Prozesspriorität
  ausgeführt und bestanden; der Dienst blieb ohne Neustart aktiv. Lokaler und
  öffentlicher `/health`-Endpunkt meldeten `status: ok` mit Release
  `2026.10.20-home-flyers-v1`.
- Nach Bestätigung der aktivierten Produktionsstabilisierung die Flyer-Arbeit
  ohne Bildgenerierung und ohne Dienstneustart fortgesetzt. Eine gezielte
  Seitenprüfung sichert nun fünf Folien, fünf getrennte Flyer-Textebenen und
  alle fünf vorgegebenen Erklärungssätze; der einzelne Test bestand. Die
  öffentlichen Styles und das Karussellskript wurden lesend geprüft, der
  10.000-Millisekunden-Takt war aktiv. Der Dienst blieb mit `NRestarts=0` und
  rund 72 MB Speicher stabil.
- Die erste öffentliche Sichtprüfung zeigte anschließend nur die Flyertexte
  auf leerer dunkelblauer Fläche. Ursache waren absolute Bildadressen mit
  `/static/...`, die am produktiven URL-Präfix `/guesstimate/` vorbeigingen und
  eine HTTP-Weiterleitung statt der PNG-Datei erhielten. Alle fünf Verweise im
  Stylesheet auf relative Static-Adressen umgestellt und die Stylesheet-Version
  auf `quiz-arena.css?v=57` erhöht. Die ausgelieferte CSS-Datei enthielt danach
  alle fünf korrigierten Pfade; jedes Bild wurde öffentlich mit HTTP 200
  geladen. Der gezielte Hauptseitentest bestand, der Dienst blieb aktiv mit
  `NRestarts=0`; kein Dienstneustart wurde ausgeführt.

## Produktionsstabilisierung – 20.10.2026

- Als Ursache dafür ermittelt, dass laufende Dateiänderungen den Dienst
  unmittelbar unterbrechen konnten: Gunicorn war in der produktiven
  systemd-Dienstdefinition mit dem Entwicklungsschalter `--reload` gestartet.
  Dadurch wurden auch unfertige Python-Zwischenstände vor Validierung und Tests
  automatisch live geladen; ein Importfehler konnte anschließend über
  `Restart=on-failure` wiederholte Neustarts auslösen.
- Den automatischen Quellcode-Reload aus der im Projekt hinterlegten
  Dienstdefinition entfernt. Die Korrektur ist inzwischen auch in der aktiven
  Datei `/etc/systemd/system/guesstimate.service` installiert. Der am
  20.10.2026 seit 21:29 Uhr laufende Prozess wurde nachweislich mit
  `gunicorn --workers 2 --timeout 60 --bind 127.0.0.1:8765 app:app` und ohne
  `--reload` gestartet; `ActiveState=active`, `Result=success` und
  `NRestarts=0` wurden beobachtet. Python-Änderungen werden damit erst nach
  einem ausdrücklichen, kontrollierten Dienstneustart übernommen; reine CSS-,
  JavaScript- und Bilddateien benötigen weiterhin keinen Prozessneustart.

## Login-Begrüßung und Classic-Lobbyplaketten – 20.10.2026

- Den bisherigen Tagessieger-Glückwunschdialog vollständig aus der
  Startseitenvorlage entfernt. Der Geburtstagsgruß bleibt ausschließlich als
  fünfter Flyer im Zehn-Sekunden-Karussell. Eine gegebenenfalls erforderliche
  Nachholabfrage öffnet sich weiterhin unabhängig.
- Die verzerrte Plakettendarstellung in der Classic-Lobby korrigiert. Die
  Lobbykarte verwendet für gekaufte Plaketten nun eine Neun-Segment-Skalierung:
  linkes und rechtes Zierstück behalten ihre Proportionen, nur das dafür
  vorgesehene Mittelstück wird horizontal verlängert.
- Fragenprüfung, zwei gezielte Startseiten-/Lobbytests und anschließend alle
  84 Tests bestanden. Ein kontrollierter Dienstneustart wurde vom System mit
  `Access denied` abgelehnt und nicht umgangen. Er ist für diese Änderung nicht
  erforderlich, weil `TEMPLATES_AUTO_RELOAD=True` aktiv ist und Stylesheets
  direkt ausgeliefert werden. Der Dienst blieb `active/running` mit
  `NRestarts=0`; `profile-stage-v1.css?v=11` wurde öffentlich geprüft.

## Stirnleiste – 20.10.2026

- Die Desktop-Navigation flacher ausgerichtet und alle sieben eigentlichen
  Schaltflächen auf dieselbe Höhe gesetzt. Die Beschriftung ist größer; die
  drei langen Spielnamen `guesstimate party`, `stormseed´s perfect` und
  `Tabletop Connection` stehen als kontrollierte Zweizeiler.
- Starre Breiten der Navigationsknöpfe entfernt. Knopfbreiten ergeben sich nun
  aus der jeweiligen Beschriftung und einheitlichem horizontalem Innenabstand.
- Im Markenblock `stormseed´s` strukturell mit dem Wortteil `guess` gekoppelt
  und exakt darüber zentriert; die Position hängt nicht mehr von einer
  geschätzten Verschiebung über dem Gesamtwort `guesstimate` ab.
- Stylesheet-Kennung auf `profile-stage-v1.css?v=12` erhöht. Fragenprüfung und
  alle 88 Tests bestanden; der Dienststatus wurde als `active` beobachtet.
  Lokaler und öffentlicher `/health`-Endpunkt meldeten `status: ok`; die neue
  Stylesheet-Version wurde öffentlich ausgeliefert.
- Korrektur nach echter Browseraufnahme: Die erste Markenlösung war visuell
  fehlerhaft, weil sie `guesstimate` in zwei getrennte Layoutteile zerlegte;
  `guess` und `timate` erschienen klein und mit großem Abstand. Die vorherige
  Aussage einer erfolgreichen Sichtprüfung war damit falsch: Geprüft waren
  lediglich Tests, Health-Endpunkte und Dateiauslieferung, nicht das
  Browserbild. `guesstimate` ist nun wieder ein einziges ungetrenntes Wort.
  `stormseed´s` liegt als separate Ebene zentriert über den linken 44 Prozent
  des Wortes und damit über `guess`; Stylesheet-Kennung `v=13`.
- Nach weiterer Browseraufnahme beide Wortmarken getrennt nachjustiert. In der
  Stirnleiste wurde `stormseed´s` um 5 Pixel nach unten an `guesstimate`
  herangeführt. In der mittleren Hauptseitenmarke ist die kleine Zeile nun
  absolut über den linken 44 Prozent des ungetrennten Wortes positioniert,
  statt als eigene zentrierte Blockzeile über dem Gesamtwort. Dadurch steht sie
  über `guess` und der große vorherige Zeilenabstand entfällt; Stylesheet-
  Kennung `v=14`.
- Nach direkter Nutzersichtprüfung ausschließlich die kleine Zeile der
  mittleren Hauptseitenmarke weitere 10 Pixel nach unten verschoben. Die
  Positionen der großen mittleren Marke und der bereits annähernd richtigen
  Wortmarke oben links blieben unverändert; Stylesheet-Kennung `v=15`.

## Classic-Party-Hintergrund – 20.10.2026

- Auf Nutzerwunsch die nachträglich eingeführte feste Karussellkulisse
  `carousel-party-classic-v1.png` ausschließlich von der Classic-
  Lobbyübersicht entfernt. Die Übersicht erbt nun wieder denselben persönlichen
  Seitenhintergrund wie die anschließend geöffnete Classic-Lobby; auch die
  gemeinsame Noise-Ebene wird dort nicht mehr eigens ausgeblendet.
- Perfect und Tabletop bleiben unverändert. Stylesheet-Kennung
  `quiz-arena.css?v=59`.

## Stormseed´s Perfect – kompakte Clubrunde (21.10.2026)

- Der bisher wirkungslose Link `← Lobbys` verlässt eine aktive Perfect-Lobby
  nun serverseitig und führt danach zur Lobbyübersicht. Verlässt die letzte
  Person den Raum, wird die Lobby wie vorgesehen auf `abandoned` gesetzt; bei
  genau einer anwesenden Person erscheint dafür keine Browserwarnung. Bei
  mehreren Anwesenden bleibt die Sicherheitsabfrage erhalten.
- Die Host-Krone sowohl aus der Lobbyübersicht als auch aus dem geöffneten Raum
  entfernt. Der Gastgeberstatus wird nur noch textlich als `Host` gezeigt.
- Host und Gäste verwenden in der Lobby dieselbe Tischkomposition: Zettel und
  plastischer Buzzer stehen jeweils an denselben Stellen. Beim Host startet der
  Buzzer das Spiel; bei Gästen schaltet er den Bereitschaftsstatus.
- Große Avatare und hohe Pulte aus der Spieleranzeige im Raum entfernt. Bis zu
  sieben gleichberechtigte kurze, skinabhängige Clubplaketten bilden nun eine
  feste Leiste innerhalb des sichtbaren Fensters. Sie zeigen Name, deutlich
  lesbaren Gesamtpunktestand und aktuellen Status ohne Rangnummern oder
  Ranglistenaufbau. Im laufenden Spiel scrollt nur noch die eigentliche
  Spielkarte innerhalb der verbleibenden Fläche.
- Luno anhand des vorhandenen Charakters als neue echte PNG-Freistellung mit
  Alphakanal erstellt (`a17-luno-cutout-v2.png`) und für normale sowie
  Bühnenansicht eingebunden. Die früheren blauen Hintergrundbilder bleiben als
  historische Dateien erhalten, werden vom Katalog aber nicht mehr verwendet.
- Release-Kennung auf `2026.10.21-perfect-club-rail-v1`, Perfect-Stylesheet auf
  `v=8` und Perfect-Skript auf `v=7` erhöht. Ein neuer Ablaufprüftest sichert
  die automatische Schließung beim Verlassen durch die letzte Person.
- Fragenprüfung und alle nun 89 Tests bestanden. Der erforderliche
  kontrollierte Neustart wurde von systemd mit `Access denied` verweigert. Der
  Dienst blieb `active` und meldet deshalb weiterhin die alte Release-Kennung
  `2026.10.20-tabletop-connection-v1`. Stylesheet und neue Luno-Datei werden
  bereits direkt mit HTTP 200 ausgeliefert; die serverseitige Luno-Zuordnung
  und neue Release-Kennung werden erst nach einem administrativen Neustart
  aktiv. Eine vollständige Live-Aktivierung wird bis dahin nicht behauptet.

### Korrektur nach Nutzertest

- Die im ersten Entwurf eingeführte untere Spielerleiste wieder entfernt. Sie
  überdeckte Lobbychat und Tischdekoration und stellte Namen sowie Punkte zu
  klein dar.
- Spieler werden nun links untereinander als kompakte Karten mit freigestelltem
  Avatar, kurzem persönlichem Pult, gut lesbarem Namen, Punktestand und Status
  angeordnet. Die Darstellung bleibt bewusst von einer Rangliste verschieden.
- Für den Lobbychat ist links unterhalb der Spielerkarten ein eigener Bereich
  reserviert. Zettel und Buzzer wurden als getrennte Tischobjekte neu innerhalb
  der Tischfläche positioniert; der Spielbereich erhält neben der Spielerreihe
  einen eigenen freien Inhaltsraum.
- Die lokale, vom Live-Bestand getrennte Zwei-Personen-Testlobby setzt den
  menschlichen Tester beim Einstieg erneut als Host und hält den GPT-Testbot
  als bereits bereiten Gast. Damit kann der Mensch die Runde selbst starten.
- Release-Kennung auf `2026.10.21-perfect-side-roster-v1` und Perfect-Stylesheet
  auf `v=9` erhöht. Die gezielte Perfect-Testsuite bestand mit 16 Tests;
  anschließend bestanden auch die Fragenprüfung und alle 89 Tests. Die lokale
  HTML-Prüfung belegte den Menschen als Host mit `Spiel starten` sowie den GPT-
  Testbot als Gast mit Status `Bereit`.

## Kartentisch – viewportfüllende Spielfläche (21.10.2026)

- Die feste, seitenweit scrollbar erzwungene 1920-×-1080-Fläche in einen
  viewportfüllenden Rahmen umgebaut. Der Tisch wird proportional vollständig
  in den verfügbaren Browserbereich eingepasst; die Seite selbst hat keinen
  horizontalen oder vertikalen Wanderbereich mehr. Die seitlichen Pulte nutzen
  weiterhin dieselbe Grundkomponente und werden als Ganzes größer skaliert und
  weiter ins sichtbare Bild gesetzt.
- Über Zieh- und Ablagestapel stehen nun gut lesbare, spielbrettartige
  Zahlenplaketten. Der neue Knopf `Austeilen` legt in Beitrittsreihenfolge für
  jede aktive Person genau eine oberste Stapelkarte auf deren privates Pult.
  Die Kartenwerte bleiben ausschließlich für den jeweiligen Besitzer sichtbar.
- Die Austeilaktion ist serverseitig atomar umgesetzt. Bis zu einem
  kontrollierten Dienstneustart verwendet das neue Live-Skript automatisch die
  bereits aktive Einzelbewegungs-Schnittstelle als kompatiblen Fallback.
- Fragenprüfung und alle nun 90 Tests bestanden; der gezielte Kartentischlauf
  bestand mit 13 Tests. Öffentliche CSS- und JavaScript-Datei wurden über HTTPS
  mit jeweils identischer SHA-256-Prüfsumme zum lokalen Bestand ausgeliefert.
- Der notwendige kontrollierte Neustart von `guesstimate.service` wurde mit
  `Access denied` abgewiesen. Der öffentliche Health-Endpunkt meldete weiterhin
  `status: ok`, aber noch Release `2026.10.21-perfect-club-stage-v1`. Eine
  authentifizierte visuelle Live-Prüfung der Spielansicht war in dieser
  Arbeitsumgebung nicht möglich; der Auftrag gilt deshalb nach der verbindlichen
  Live-Definition noch nicht als vollständig getan.
- Nach Nutzerkorrektur das eigene Kartentischpult ausschließlich horizontal
  auf 170 Prozent verbreitert. Seine linke Kante wurde so gesetzt, dass der
  darüberliegende Notizzettel das Pult leicht überlappt und der größere Teil
  der zusätzlichen Ablagefläche rechts entsteht. Lobby-verlassen und
  Lobby-beenden stehen nun links oben untereinander.
- Automatisch ausgeteilte Karten beginnen bei 10 statt 24 Prozent der
  Pultbreite und folgen in Schritten von 7 statt 12 Prozentpunkten. Dadurch
  passen deutlich mehr Karten in eine Reihe. Der Kartentischtest prüft nun
  ausdrücklich die Positionen der ersten beiden Austeilrunden.
- Fragenprüfung, 13 gezielte Kartentischtests und alle 90 Projekttests
  bestanden. `card-table.css?v=5` und `card-table.js?v=5` wurden öffentlich
  mit jeweils identischer SHA-256-Prüfsumme ausgeliefert; `/health` meldete
  `status: ok`. Eine authentifizierte visuelle Live-Abnahme steht weiterhin
  aus, daher nach der verbindlichen Definition noch Status nicht getan.
- Korrektur nach echter Nutzeraufnahme: Die gemeldete Verdichtung von 12 auf
  7 Prozentpunkte war optisch nicht erreicht. Bereits auf dem Pult liegende
  Karten behielten ihre alten gespeicherten Positionen; zudem entsprechen
  7 Prozent auf dem auf 170 Prozent verbreiterten Pult weiterhin rund 74
  Pixeln. Alle Karten eines Spielerpults werden nun bei jeder Darstellung nach
  ihrer Stapelreihenfolge sichtbar neu ausgerichtet, beginnend bei 10 Prozent
  und mit 5 Prozentpunkten Abstand. Damit werden auch bestehende Hände sofort
  korrigiert, ohne Spiel- oder Kartendaten zu löschen.
- Der gezielte Kartentischtest, die Fragenprüfung und alle 90 Tests bestanden.
  `card-table.js?v=6` und `card-table.css?v=6` wurden öffentlich bytegenau
  identisch ausgeliefert; `/health` meldete `status: ok`. Eine neue
  Nutzeraufnahme der korrigierten Reihe steht noch aus.
- Über den drei Stapelaktionen einen stilistisch passenden Schieberegler
  `Karten pro Person` ergänzt. Er reicht von 1 bis zur Zahl vollständiger
  Austeilrunden, die mit dem aktuell verbliebenen Ziehstapel für alle
  anwesenden Personen möglich ist, und passt sich bei jeder Statusänderung
  automatisch an. Ist keine vollständige Runde mehr möglich, werden Regler und
  Austeilknopf deaktiviert.
- `Austeilen` verteilt nun die eingestellte Kartenzahl rundengerecht und
  gleichmäßig an alle Personen. Die serverseitige Aktion arbeitet atomar; das
  bereits öffentlich aktive Kompatibilitätsverfahren unterstützt dieselbe
  Mehrfachausteilung bis zum noch ausstehenden Dienstneustart.
- Fragenprüfung, 14 Kartentischtests und alle nun 91 Projekttests bestanden.
  `card-table.js?v=7` und `card-table.css?v=7` wurden öffentlich mit jeweils
  identischer SHA-256-Prüfsumme ausgeliefert; `/health` meldete `status: ok`.
  Eine authentifizierte visuelle Live-Abnahme des Reglers steht noch aus.
- Kartentischplätze anschließend dauerhaft gemacht: Es gibt dort künftig in
  weder wartenden noch laufenden Lobbys eine automatische Abwesenheitsfrist.
  Historisch durch den früheren 30-Sekunden-Mechanismus auf `away` gesetzte
  Mitglieder werden beim ersten Statuszugriff wieder als aktiv geführt;
  ausschließlich ausdrückliches Verlassen entfernt eine Person.
- Die neue Aktion `Tisch abräumen` verschiebt ausschließlich Karten aus F auf
  die offene Ablage B; Karten auf Spielerpulten und im Ziehstapel bleiben
  unberührt. Bis zum Dienstneustart führt das bereits live ausgelieferte Skript
  dieselbe Aktion kompatibel über einzelne Kartenbewegungen aus.
- Die eigene Hand wird abhängig von ihrer Größe in einer oder zwei Reihen
  angeordnet. Jede Reihe wird innerhalb des 170-Prozent-Pults zentriert; bei
  sehr vielen Karten verkleinert sich der Abstand dynamisch, damit beide
  Reihen innerhalb der Fläche bleiben.
- Optionales Punktekonto vorbereitet: Der Host kann in der Lobby leer lassen
  oder 1 bis 1.000.000.000 Startpunkte pro Person setzen. Nur im zweiten Fall
  erscheinen Bestand, persönlicher Einsatzregler im Pokerchip, `Bieten`, die
  Einsätze an den Spielerflächen und der gemeinsame Pot. Einsätze werden
  serverseitig atomar vom eigenen Bestand abgezogen und zum persönlichen
  Einsatz sowie zum Pot addiert. Eine dekorative, platzsparende Chipstaffel
  sitzt am Rand des eigenen Pults.
- Fragenprüfung, 17 gezielte Kartentischtests und alle nun 94 Projekttests
  bestanden. `card-table.js?v=8` und `card-table.css?v=8` wurden öffentlich
  bytegenau identisch ausgeliefert; `/health` meldete `status: ok`, aber noch
  Release `2026.10.21-perfect-club-stage-v1`. Der kontrollierte Dienstneustart
  wurde erneut mit `Access denied` verweigert. Zweireihen-Anordnung und
  kompatibles Tischabräumen sind dadurch bereits öffentlich; dauerhafte Plätze
  und das Punktekonto werden erst nach administrativem Neustart aktiv und sind
  noch nicht live abgenommen. Gesamtstatus deshalb nicht getan.
- Korrektur nach Nutzeraufnahme: Die zuvor aus CSS-Kreisen gebildete
  Chipdekoration vollständig verworfen. Eine neue, eigens generierte breite
  Spielertafel `card-player-board-poker-v1.png` verwendet warmes rustikales
  Eichenholz und realistische rote, blaue, grüne, schwarze und helle
  Pokerchipstapel ausschließlich am rechten Rand; die Mitte bleibt für zwei
  Kartenreihen frei. Die Grafik wurde mit der integrierten Bildgenerierung als
  neues Original ohne Fremdlogos oder Texte erstellt.
- Einsatzdarstellung nach der Nutzerskizze neu geordnet: eigener bisheriger
  Einsatz und verbleibender Bestand stehen als getrennte Anzeigen rechts oben
  auf der Holztafel, der Einsatzregler steht vertikal an deren äußerem Rand,
  sein Wert erscheint in einem Pokerchip-Display, und der gemeinsame Pot liegt
  als deutliches Holz-/Messingobjekt auf dem Tisch. Die abstrakte Kreisstaffel
  wurde vollständig aus Vorlage und Stylesheet entfernt.
- Der Dienst wurde außerhalb dieser Sitzung nachweislich am 21.10.2026 um
  16:45:09 Uhr neu gestartet. Dieser Zeitpunkt liegt nach der serverseitigen
  Kartentischänderung; der öffentliche Health-Endpunkt meldete anschließend
  `status: ok` und Release `2026.10.21-perfect-timing-controls-v1`. Damit sind
  Lobby-Startpunkte, dauerhafte Lobbyplätze, Einsatzkonten und Pot inzwischen
  serverseitig aktiv. Ein späterer eigener Neustartversuch scheiterte zwar an
  fehlendem sudo-Passwort, war zu diesem Zeitpunkt aber nicht mehr erforderlich.
- Fragenprüfung und alle nun 95 Tests bestanden. `card-table.css?v=9`,
  `card-table.js?v=9` und die neue Holz-/Chiptafel wurden öffentlich jeweils
  bytegenau identisch ausgeliefert. Eine authentifizierte Nutzeraufnahme nach
  Neuladen steht noch aus; sichtbar live abgenommen ist die Neugestaltung daher
  noch nicht.
- Nach echter Nutzeraufnahme die Kartentischgeometrie weiter korrigiert. Die
  virtuelle Bühne verwendet nun 1.920 × 900 statt 1.920 × 1.080 Pixel und
  füllt damit das beobachtete breite Browserfenster ohne die großen seitlichen
  Leerflächen. F beginnt weiter links, ist deutlich breiter und höher; A/B
  stehen rechts anschließend außerhalb des eigenen Pults. Der Pot steht oben
  rechts innerhalb von F statt in der Kartenmitte. Das eigene Pult wurde etwas
  weiter nach links gesetzt.
- Die Poker-Holztafel als `card-player-board-poker-v2.png` neu erzeugt. Alle
  realistischen Chipstapel und losen Chips besitzen nun sichtbaren Holzabstand
  zum Bildrand und werden nicht mehr angeschnitten; die große mittlere Fläche
  bleibt für zwei Kartenreihen frei. Die integrierte Bildgenerierung diente nur
  der neuen originalen Projektgrafik ohne Logos oder Texte.
- Kartenrechte serverseitig verschärft: Eine Karte auf einem Spielerpult darf
  ausschließlich dessen Besitzer bewegen. Manuelle Zielbereiche sind nur noch
  F oder das eigene Pult; Deck und Ablage werden ausschließlich über die
  vorgesehenen Tischaktionen bedient. Fremde Pultkarten sind zusätzlich schon
  im Browser nicht mehr ziehbar.
- Jedes Spielerpult besitzt bei aktivem Punktekonto einen `Collect`-Knopf. Ein
  Antrag zählt als Zustimmung des Antragstellers; alle anderen aktiven Personen
  erhalten eine Bestätigen-/Ablehnen-Abfrage. Erst bei Einstimmigkeit wird der
  vollständige Pot dem Antragsteller gutgeschrieben und werden Pot sowie
  angezeigte Einsätze auf null gesetzt. Eine Ablehnung verwirft den Antrag.
- Fragenprüfung, 19 Kartentischtests und alle nun 99 Projekttests bestanden.
  `card-table.css?v=10`, `card-table.js?v=10` und die neue Holztafel wurden
  öffentlich mit identischen SHA-256-Prüfsummen ausgeliefert. Der öffentliche
  Dienst läuft jedoch seit 17:49:08 Uhr und damit vor den serverseitigen
  Änderungen von 19:21 Uhr; ein kontrollierter Neustart wurde erneut mit
  `Access denied` verweigert. Layout und Browser-Sperre sind öffentlich,
  serverseitige Kartenrechte und Pot-Abstimmung werden erst nach
  administrativem Neustart aktiv. Sichtbare Live-Abnahme weiterhin offen.

## Kartentisch – Lobbyaktualisierung und freie Pultbedienung (21.10.2026)

- Den gemeinsamen Notizzettel von 470 auf 235 Pixel und damit exakt auf die
  halbe bisherige Breite verkleinert.
- Auf dem eigenen Pult `Geboten`, `Bestand` und `Collect` aus Name und
  Chipmotiv herausgenommen und als eigene horizontale Leiste oberhalb des
  Pults angeordnet. Ihre Bedienebene liegt jetzt sicher über den Spielkarten;
  auch der Einsatzregler liegt über den Karten. Ein fehlgeschlagener
  Collect-Aufruf zeigt nun eine sichtbare Fehlermeldung.
- Beitritt und ausdrückliches Verlassen erhöhen nun immer die Lobbyrevision.
  Die wartende Lobby vergleicht zusätzlich die tatsächliche Mitgliederzahl
  und lädt dadurch auch bei einer unerwartet unveränderten Revision neu.
- JavaScript-Syntaxprüfung, Fragenprüfung, 20 Kartentischtests und alle nun
  100 Projekttests bestanden. CSS und JavaScript werden öffentlich bereits
  bytegenau identisch ausgeliefert. Der angeforderte Dienstneustart wurde mit
  `Access denied` verweigert; die neuen Python-Abläufe für Lobbyrevision und
  Collect werden deshalb erst nach administrativem Neustart aktiv. Eine
  authentifizierte sichtbare Live-Abnahme steht noch aus; Gesamtstatus: nicht
  getan.

## Kartentisch – Mitgehen und einheitliche Holzpulte (21.10.2026)

- Neben `Bieten` einen Knopf `Mitgehen` ergänzt. Er ermittelt den höchsten
  bisherigen persönlichen Gesamteinsatz, berücksichtigt den eigenen bereits
  gesetzten Betrag und übernimmt nur die noch fehlende, durch den eigenen
  Bestand gedeckte Differenz in den Einsatzregler. Die Zahlung erfolgt danach
  weiterhin bewusst über `Bieten`.
- Alle Gegnerpulte verwenden nun dieselbe Holz-/Pokerchip-Komponente wie das
  eigene Pult, als Ganzes proportional verkleinert. Gebot und Bestand stehen
  an ihrer jeweils zum zentralen Spieltisch gerichteten Unterkante. Collect
  wird ausschließlich am eigenen Pult ausgegeben.
- JavaScript-Syntaxprüfung, Fragenprüfung, 20 Kartentischtests und alle 100
  Projekttests bestanden. CSS und JavaScript werden öffentlich bytegenau
  identisch ausgeliefert. Der kontrollierte Dienstneustart wurde erneut mit
  `Access denied` verweigert; eine möglicherweise bereits vom Prozess
  zwischengespeicherte Spielvorlage sowie die sichtbare Mehrspieleransicht
  konnten daher nicht abschließend live abgenommen werden. Gesamtstatus: nicht
  getan.

### Einheitliche Spielerfiguren und Tischpositionen

- Die seitliche Plakettenanmutung verworfen. Jede anwesende Person erscheint
  nun in allen Spielphasen als dieselbe kompakte Figur: Der Avatar steht mittig
  hinter dem eigenen kurzen Pult; Name und Punkte stehen im Pult, der aktuelle
  Status direkt daneben. Die Figuren bleiben links untereinander und halten
  die Mitte für Frage- und Antwortfenster frei.
- Einstellungsblatt und Buzzer vom unteren Fensterrand nach oben auf die
  sichtbare Fläche des runden Holztischs versetzt. Die neue Position nutzt den
  unterhalb der hoch angeordneten Lobbyfiguren freien Raum.
- Perfect-Stylesheet auf `v=10` und Release-Kennung auf
  `2026.10.21-perfect-podium-roster-v1` erhöht. Die laufende isolierte
  Testlobby lieferte die neue Stylesheet-Version aus und zeigte den Menschen
  weiterhin als Host sowie den GPT-Testbot als Gast. Die gezielten 16 Perfect-
  Tests bestanden; anschließend bestanden auch die Fragenprüfung und alle 89
  Tests.

### Party-Anordnung um das Spielfenster

- Nach Sichtprüfung der laufenden Fragerunde die kleine linke Spielerleiste im
  Spiel verworfen. Auf breiten Ansichten stehen die anwesenden Personen nun als
  größere Partygäste paarweise links und rechts um das zentrale Frage- und
  Antwortfenster; weitere Personen füllen darunter liegende Positionen, eine
  siebte Person steht mittig am Tisch. Die Wohnzimmerkulisse bleibt dadurch
  sichtbar Teil der Spielansicht. Auf schmaleren Fenstern wechselt die Gruppe
  in eine horizontale Reihe oberhalb des Spielfensters.
- Ein erster Ansatz mit einer neu erzeugten einheitlichen Holzplakette wurde
  nach unmittelbarer Nutzerkorrektur vollständig verworfen und das unbenutzte
  Projektasset wieder entfernt. Jede Person zeigt stattdessen ihre tatsächlich
  ausgerüstete Shop-Plakette; nur das kostenlose Startobjekt ohne eigene
  Shop-Plakettendatei verwendet das vorhandene Startmotiv. Avatare, Namen,
  Punkte und Phasenstatus bleiben dynamisch.
- Perfect-Stylesheet auf `v=11` und Release-Kennung auf
  `2026.10.21-perfect-party-guests-v1` erhöht. Die laufende isolierte Lobby
  lieferte für den menschlichen Testspieler nachweislich dessen ausgerüstete
  Plakette `p03.webp` und keine neue allgemeine Plakette. Die 16 gezielten
  Perfect-Tests bestanden; anschließend bestanden auch die Fragenprüfung und
  alle 89 Tests.

### Referenzgestützte Clubbühne

- Nach Nutzerkritik tatsächlich aktuelle Partyspiel-Referenzen untersucht,
  darunter offizielle Jackbox-Darstellungen und Aussagen zur organischen,
  mechanikbezogenen Bildschirmstruktur sowie Kahoot-Hinweise zum gezielten
  Einsatz der Spielerfiguren in Lobby, Reaktionen und Ergebnis. Daraus als
  verbindliche Richtung abgeleitet: zentrale Aufgabe klar halten, Personen als
  sichtbare Besetzung der Szene statt als Statusliste behandeln und Kulisse
  zur räumlichen Gliederung nutzen.
- Lobby und laufendes Spiel verwenden jetzt dieselbe dynamische
  Personenkomponente aus vorhandenem freigestelltem Avatar, tatsächlich
  ausgerüsteter Shop-Plakette, Name, Punkten und Phasenstatus. Es wurden keine
  neuen Avatare, Pulte oder Plaketten erstellt. In der Lobby bildet sie eine
  gemeinsame Gästereihe; im Spiel verteilt sie sich um das zentrale Fenster.
- Das Frage- und Antwortfenster ohne neues Bildasset als Clubbühnen-Objekt
  überarbeitet: mehrschichtiger Holz-/Messingrahmen, stärkere Tiefenwirkung und
  ruhigere helle Innenfläche. Dadurch bleibt die Bedienung klar, während das
  Fenster gestalterisch zum Wohnzimmer gehört.
- Perfect-Stylesheet auf `v=12` und Release-Kennung auf
  `2026.10.21-perfect-club-stage-v1` erhöht. Fragenprüfung, 16 gezielte
  Perfect-Tests und anschließend alle 89 Tests bestanden.

## Transparente Avatarfassungen – 21.10.2026

- Die fünf zuletzt ergänzten Avatare `a14` bis `a18` vollständig geprüft.
  Luno lag bereits als echte Freistellung vor; Somnus, Ember, Myrli und Nimbus
  enthielten dagegen in normaler und Bühnenansicht denselben blauen
  Bildhintergrund.
- Für diese vier Figuren neue, quadratische RGBA-Freistellungen mit echtem
  Alphakanal als `*-cutout-v2.png` erstellt. Figur, Pose, Kleidung, Requisiten
  und charaktergebundene Leuchteffekte blieben erhalten. Der zentrale Katalog
  verweist nun bei allen fünf Avataren in normaler und Bühnenansicht auf die
  transparenten Fassungen.
- Damit die Korrektur trotz des erneut mit `Access denied` abgelehnten
  Dienstneustarts unmittelbar im laufenden Prozess sichtbar ist, enthalten
  auch die vier noch im Arbeitsspeicher referenzierten Altpfade jetzt exakt
  dieselben transparenten Dateien. Die früheren Kulissenbilder bleiben unter
  eindeutig benannten `*-background-v1.png`-Dateien historisch erhalten und
  sind nicht mehr im Katalog eingetragen.
- Alphakanal aller fünf aktiven Freistellungen technisch geprüft. Die
  Fragenprüfung und alle 89 Tests bestanden. Lokaler und öffentlicher
  `/health`-Endpunkt meldeten `status: ok` und Release
  `2026.10.20-tabletop-connection-v1`. Alle fünf normalen, alle fünf
  Bühnenpfade sowie die vier neuen versionierten Pfade wurden öffentlich mit
  HTTP 200 und jeweils identischer SHA-256-Prüfsumme zur lokalen Datei
  ausgeliefert.
- Korrektur nach echtem Nutzerbild: Die vorstehende Aussage zur sofortigen
  Live-Konsistenz war unvollständig. Der noch laufende alte Prozess verwies für
  Luno weiterhin auf `a17-luno.png` beziehungsweise
  `stage/a17-luno.png`; nur die neuen `cutout-v2`-Adressen waren zuvor geprüft
  worden. Deshalb erschien im Spiel weiterhin das blaue Quadrat. Beide alten
  Live-Pfade enthalten nun ebenfalls exakt die transparente Luno-Datei; die
  vorherigen Fassungen wurden als `a17-luno-background-v1.png` gesichert.
  Beide öffentlich ausgelieferten Altpfade und die versionierte Freistellung
  besitzen jetzt dieselbe SHA-256-Prüfsumme
  `cfac3e5cc2feaf6ee4fe0cd1ef2c4ae11ec5777359fb0c9ea18e1a806290f735`.
  Der öffentliche Health-Endpunkt meldete danach weiterhin `status: ok`.

## Ruhiger Ausrüstungswechsel im Profil – 21.10.2026

- Den vollständigen Seitenwechsel beim Ausrüsten von Avataren, Pulten,
  Hintergründen und Sprüchen entfernt. Die Profilseite sendet die bestehende
  Ausrüstungsanfrage nun im Hintergrund und ersetzt anschließend nur die
  persönliche Vorschau sowie den betroffenen Inventarbereich.
- Die Scrollposition der rechten Auswahlleiste und die Position der gesamten
  Seite bleiben dabei unverändert. Nachgeladene Pultbeschriftungen werden
  erneut an ihren verfügbaren Platz angepasst. Bei einem technischen Fehler
  bleibt die bisherige normale Formularübermittlung als Rückfall erhalten.
- Skriptkennungen auf `profile.js?v=4` und
  `profile-stage-v1.js?v=3` erhöht. JavaScript-Syntaxprüfung,
  Fragenbibliotheksprüfung und alle 89 Tests bestanden. Beide Skripte wurden
  öffentlich mit HTTP 200 und identischer SHA-256-Prüfsumme zur lokalen Datei
  ausgeliefert; der öffentliche Health-Endpunkt meldete `status: ok`.

## Profilfenster als kanonisches Original – 21.10.2026

- Die zuvor vom aufgerufenen Seitenendpunkt abhängige Sonderkomposition
  `variant-a-profile-editor` vollständig entfernt. Profil und Hauptseite
  rendern nun dieselbe zentrale Makrokomponente
  `templates/_profile_window.html` mit derselben kanonischen Szenenklasse
  `variant-a-profile-canonical`.
- Alle notwendigen Passformregeln für Avatar, Pult, Namensfeld und Guthaben
  hängen ausschließlich an dieser gemeinsamen Komponente sowie den
  `avatar-*`- und `plaque-*`-Kennungen. Damit werden dieselben Regeln im
  Profil-Original und in der Hauptseitenkopie angewendet. Unterschiedliche
  Außenmaße dürfen die gemeinsame Szene nur als Ganzes skalieren.
- Bearbeiten-Knopf und zusätzliche Hauptseitendetails liegen außerhalb der
  eigentlichen gemeinsamen Szene und verändern deren Innenkomposition nicht.
  Ein Test verbietet künftig sowohl `request.endpoint` als Umschalter in der
  Komponente als auch die frühere Klasse `variant-a-profile-editor` und prüft
  alle 14 Pult-Passformregeln an der kanonischen Klasse.
- Stylesheet-Kennung auf `quiz-arena.css?v=60` erhöht. Fragenprüfung und alle
  89 Tests bestanden. Das Stylesheet wurde öffentlich mit HTTP 200 und
  identischer SHA-256-Prüfsumme ausgeliefert; der öffentliche Health-Endpunkt
  meldete `status: ok`.
- Korrektur nach zwei echten Nutzeraufnahmen: Die gemeinsame Makro- und
  Klassenverwendung allein ergab noch keine visuell identische Kopie. Wegen
  unterschiedlicher Szenenhöhen wurde die Innenkomposition auf der Hauptseite
  gestreckt; Luno verschwand dort fast vollständig hinter dem Pult, während er
  im Profil richtig sichtbar war. Die vorherige Erfolgsmeldung war deshalb zu
  früh.
- Profil und Hauptseite verwenden nun zusätzlich dieselbe kanonische
  Zeichenfläche mit festem Seitenverhältnis `43 / 57`. Größenabhängige
  Beschriftungen und Aufhängung skalieren relativ zu dieser Fläche. Der
  verbindliche CSS-Block steht bewusst am Dateiende und überschreibt alle
  historischen profilspezifischen Mindesthöhen; eine maschinelle
  Prioritätsprüfung bestätigte seine letzte Position.
- Stylesheet-Kennung auf `quiz-arena.css?v=61` erhöht. Die beiden gezielten
  Original/Kopie- und Passformtests bestanden. Das Stylesheet wurde öffentlich
  mit HTTP 200 und identischer SHA-256-Prüfsumme ausgeliefert; `/health`
  meldete `status: ok`. Eine neue authentifizierte Browseraufnahme lag bei
  Abschluss noch nicht vor und wurde daher nicht als bestanden behauptet.
- Weitere echte Nutzeraufnahme mit Wanderfalke bestätigte, dass die gemeinsame
  Zeichenfläche allein noch nicht genügte: Die Avatarbox endete weiterhin zu
  tief, sodass bei Luno und Wanderfalke nur ein kleiner Teil des Kopfes über
  dem Pult sichtbar blieb. Die gemeinsame kanonische Avatarposition deshalb
  von 29 auf 15 Prozent der Szenenhöhe angehoben; ihre Unterkante liegt nun
  bei 64 statt 78 Prozent. Auch die höher spezifische Start-Avatar-Regel wurde
  auf eine entsprechend angehobene Position gesetzt.
- Stylesheet-Kennung auf `quiz-arena.css?v=62` erhöht. Fragenprüfung und alle
  89 Tests bestanden; die finale CSS-Priorität und beide neuen Positionswerte
  wurden zusätzlich maschinell geprüft. Das Stylesheet wird öffentlich mit
  identischer SHA-256-Prüfsumme ausgeliefert und `/health` meldet `status: ok`.
  Die visuelle Live-Abnahme steht weiterhin aus.

## CSS-Konsolidierung und verbindliche Widerspruchsregel – 21.10.2026

- `AGENTS.md` dauerhaft ergänzt: Neue Anforderungen müssen vor Umsetzung mit
  Projektlog und aktuellem Code abgeglichen werden. Bei einem konkreten
  Widerspruch ist der Nutzer sofort entscheiden zu lassen. Sichtbare
  Komponenten dürfen nur eine Grundimplementierung besitzen; ersetzte
  CSS-Regeln sind zu entfernen statt durch neue Endblöcke zu überdecken. Ein
  Live-Auftrag gilt nur nach tatsächlicher sichtbarer Funktionsprüfung als
  getan.
- Vollständige Selektorbestandsaufnahme der fünf aktiven Fachstylesheets
  durchgeführt. Dabei 202 Selektoren bestätigt, die in mehr als einem
  Stylesheet vorkamen; besonders stark überlagert sind historisch gewachsene
  Grund-, Arena-, Ranglisten-, Shop- und Perfect-Komponenten. Diese
  anderslautenden Regeln dürfen nicht blind entfernt werden und werden
  komponentenweise konsolidiert.
- Den akuten Profilfensterkonflikt an seiner tatsächlichen Ursache bereinigt:
  Das nach `quiz-arena.css` geladene `profile-stage-v1.css` enthielt weiterhin
  eine ausschließlich für die Hauptseite geltende zweite Innenkomposition für
  Plakette, Avatar und Pult. Diese Regeln wurden verworfen. Die kanonische
  Innenkomposition einschließlich Seitenverhältnis, Avatarposition,
  Pultposition, Beschriftung und allen 14 Pultfeldlagen steht nun genau einmal
  in `profile-stage-v1.css`; die doppelten und mobilen Gegenregeln wurden aus
  `quiz-arena.css` entfernt. Zusätzlich wurden 18 vollständig unbenutzte
  Regeln für die nicht mehr vorhandene Klasse `profile-current-window`
  entfernt.
- Stylesheetübergreifend 143 exakt identische frühere Regelblöcke entfernt,
  deren identische spätere wirksame Fassung erhalten blieb: 86 aus
  `style.css`, 55 aus `quiz-arena.css` und 2 aus
  `stormseeds-perfect.css`. Der aktive CSS-Bestand sank dadurch um rund 460
  Zeilen. Versionskennungen: `style.css?v=26`, `quiz-arena.css?v=65`,
  `profile-stage-v1.css?v=16`, `stormseeds-perfect.css?v=13`.
- Fragenprüfung und alle 89 Tests bestanden. Alle vier geänderten Stylesheets
  wurden öffentlich mit HTTP 200 und jeweils identischer SHA-256-Prüfsumme
  ausgeliefert; `/health` meldete `status: ok`. Die komponentenweise
  Konsolidierung der verbleibenden anderslautenden Überlagerungen und die
  tatsächliche Browserabnahme sind noch offen; der Gesamtauftrag ist deshalb
  nicht getan.
- Nach Nutzerprüfung die gemeinsame Profilkomposition weiter ausgerichtet:
  Hängeplakette von 7,75 auf 2,5 Prozent nach oben, Avatar von 15 auf 9 Prozent
  nach oben und Pult von -3 auf -6 Prozent nach unten verschoben. Die
  Startfigur besitzt entsprechend 12 statt 18 Prozent obere Position. Diese
  Werte gelten unverändert für Profil und Hauptseitenkopie.
- Bei der vorausgehenden Duplikatbereinigung war die absolute Positionierung
  des iKühe-Felds nicht vollständig in die kanonische Regel übernommen worden;
  dadurch stand das Guthaben außerhalb des unteren Pultfensters. Position,
  Feldgrenzen, Transformation und Textdarstellung sind nun vollständig in
  `profile-stage-v1.css` verankert. Version auf `v=17` erhöht; Fragenprüfung
  und alle 89 Tests bestanden. Die Datei wird öffentlich mit identischer
  SHA-256-Prüfsumme ausgeliefert, `/health` meldet `status: ok`. Sichtprüfung
  durch den Nutzer steht noch aus, daher weiterhin Status nicht getan.
- Nächste Feinjustierung nach Nutzerprüfung: Hängeplakette von 2,5 auf 0,5
  Prozent und Pult von -6 auf -4 Prozent nach oben verschoben. Den Avatar
  gleichzeitig von 9 auf 12 Prozent, die Startfigur von 12 auf 15 Prozent
  nach unten gesetzt, damit Avatar und Pult sichtbar überlappen und kein
  Hintergrundspalt zwischen beiden bleibt. Gemeinsames Stylesheet auf `v=18`
  erhöht; Fragenprüfung und alle 89 Tests bestanden. Die öffentliche Datei
  besitzt dieselbe SHA-256-Prüfsumme, `/health` meldet `status: ok`; sichtbare
  Nutzerabnahme steht aus, daher Status nicht getan.

## Einheitliches Avatar-/Pult-Raster – 21.10.2026

- Die 18 aktiven Bild-Avatare der Profilbühne proportional und ohne
  Seitenverzerrung auf einen gemeinsamen transparenten Rahmen normiert. Jeder
  sichtbare Avatar besitzt exakt 1.000 Pixel Höhe und endet ohne transparenten
  Leerraum an derselben Unterkante. Der kostenlose SVG-Startavatar verwendet
  denselben 1.400 × 1.400 Pixel großen Rahmen und dieselbe sichtbare Höhe.
- Alle 14 hohen Pultgrafiken einschließlich ihrer Lampen, Pflanzen, Kristalle
  und sonstigen Aufbauten vollständig und proportional auf einen gemeinsamen
  1.600 × 1.400 Pixel großen Rahmen normiert. Jedes vollständige Pult besitzt
  exakt 1.200 Pixel sichtbare Höhe und endet ohne transparenten Leerraum an
  derselben Unterkante. Kein Bestandteil wurde abgeschnitten oder gestreckt.
- Die kanonische Profilkomponente besitzt keine einzelnen Avatargrößen mehr.
  Alle Avatare verwenden dieselbe Position und überlappen das davorliegende
  Pult gemeinsam so weit, dass bei der vollständigen Sichtübersicht aller
  Avatare sowie aller Pulte kein Hintergrundspalt zwischen beiden Ebenen blieb.
  Profil und Hauptseite verwenden weiterhin dieselbe Komponente.
- Die pultspezifischen Koordinaten betreffen ausschließlich die tatsächlich an
  unterschiedlichen Stellen gezeichneten Namens- und iKühe-Fenster; sie wurden
  auf das neue gemeinsame Bildraster umgerechnet. Die fünf neuen Avatare sind
  zusätzlich unter den vom noch laufenden alten Prozess verwendbaren
  Altdateinamen identisch hinterlegt.
- Die unveränderten Ausgangsgrafiken bleiben als eindeutig benannte
  `*-pre-normalization-v1`-Sicherungen erhalten. Das reproduzierbare Werkzeug
  liegt unter `deploy/normalize_profile_assets.py`.
- Fragenprüfung und alle 89 Tests bestanden. Anschließend sämtliche 18 vom
  laufenden beziehungsweise aktuellen Katalog verwendbaren Avatarpfade und
  alle 14 Pultdateien einzeln mit der öffentlichen Auslieferung verglichen;
  jede Datei war bytegenau identisch. Die öffentliche Seite bindet
  `profile-stage-v1.css?v=19` ein. Der Dienst meldete danach `active/running`,
  `NRestarts=0`, Release `2026.10.21-perfect-club-stage-v1` und `status: ok`.
  Eine authentifizierte Browseraufnahme von Profil und Hauptseite liegt noch
  nicht vor und darf deshalb nicht als sichtbar live abgenommen gelten.

## Öffentlicher Haupteinstieg und verborgener Dashboard-Eingang – 21.10.2026

- Die Serverweiterleitung so vorbereitet, dass die Domainwurzel und alle nicht
  freigegebenen direkten Dashboard-Pfade zu `/guesstimate/` führen. Die
  bestehende persönliche Seite bleibt hinter ihrer unveränderten Anmeldung und
  ist zusätzlich nur über einen nicht verlinkten, zufällig erzeugten Eingang
  erreichbar.
- Der verborgene Eingang setzt ein sicheres, nicht von Seitenskripten lesbares
  Browsermerkmal. Es erlaubt anschließend die bisherigen Dashboard-Pfade,
  ersetzt aber ausdrücklich weder Passwort noch Sitzungsschutz. Die Caddy-
  Konfiguration liegt reproduzierbar unter `deploy/Caddyfile`.
- Die Konfiguration erfolgreich validiert und in den laufenden Caddy-Prozess
  geladen. Die öffentliche Domainwurzel und `/login.html` antworteten danach
  jeweils mit einer Weiterleitung zu `/guesstimate/`; der neue private Eingang
  lieferte die bestehende Loginseite und setzte das vorgesehene sichere
  Browsermerkmal. Mit diesem Merkmal blieb die Loginseite erreichbar und
  `/guesstimate/health` antwortete weiterhin erfolgreich.
- Die aktive Regel ist noch nicht neustartfest: Das Ersetzen der nur von root
  beschreibbaren Datei `/etc/caddy/Caddyfile` wurde ohne Administratorkennwort
  abgelehnt. Bei einem Caddy- oder Serverneustart würde deshalb vorerst die
  alte Konfiguration geladen. Die vollständige dauerhafte Fassung liegt unter
  `deploy/Caddyfile` und muss noch administrativ nach `/etc/caddy/Caddyfile`
  installiert werden.
- Auf Nutzerwunsch den zunächst zufällig benannten privaten URL-Pfad durch
  den merkbaren Eingang `/JansPortal/` ersetzt. Das sichere Browsermerkmal und
  der eigentliche Passwortschutz bleiben davon unverändert.
- Bei der Inkognitoprüfung erschien die Loginseite zunächst ohne Gestaltung,
  weil ihre relativen Verweise unter `/JansPortal/login.css` und
  `/JansPortal/login.js` lagen und noch zur öffentlichen Seite umgeleitet
  wurden. Beide ausschließlich für die Anmeldung benötigten Dateien werden nun
  unter dem Portalpfad an die bestehende private Anwendung weitergereicht.

## Stormseed´s Perfect – Zeitsteuerung und dauerhafte Plätze (21.10.2026)

- Die frühere Abwesenheitsfrist vollständig aus Perfect entfernt. Personen
  behalten ihren Platz in wartenden und laufenden Lobbys, bis sie ausdrücklich
  auf „Lobbys“ gehen und das Verlassen bestätigen. Durch die frühere Frist als
  `away` markierte Mitglieder werden in offenen Lobbys wieder aktiviert.
- Die Erfindungsphase von 120 auf 180 Sekunden und die Auswahlphase von 75 auf
  105 Sekunden verlängert. Beide Phasen zeigen bei 30 verbleibenden Sekunden
  einmal eine feste, nicht schließbare, aber kompakte Warnung außerhalb des
  eigentlichen Karteninhalts.
- Der Host besitzt während Countdown, Erfindungs- und Auswahlphase einen
  Play/Pause-Schalter. Pause friert Phasenfrist und bei Zeitspielen auch die
  gesamte Spielzeit ein; Antwort- und Wahlabgaben werden währenddessen auch
  serverseitig abgewiesen.
- Die am 18.10. erlaubte Selbstwahl auf neue ausdrückliche Nutzeranweisung
  wieder abgeschafft. Die eigene Bluffantwort ist sichtbar als nicht wählbar
  markiert und wird zusätzlich serverseitig aus den zulässigen Wahlwerten
  ausgeschlossen.
- In der Punkteauflösung wird nun auch die offizielle richtige Antwort als
  eigene grün markierte Karte gezeigt. Auf ihr und auf gewählten
  Spielerantworten erscheinen die tatsächlichen Avatare der Wählenden als
  kleine Münzen statt gleichlautender Namensinitialen.
- Perfect-Regeltext, Stylesheet- und Skriptkennungen aktualisiert. Syntaxprüfung,
  Fragenprüfung, 17 gezielte Perfect-Tests und alle nun 95 Projekttests
  bestanden. Der Nutzer führte anschließend den administrativen Neustart aus.
  Der Dienst wurde seit 16:45:09 Uhr als `active/running` mit zwei Workern
  beobachtet. Lokaler und öffentlicher Health-Endpunkt melden `status: ok` und
  Release `2026.10.21-perfect-timing-controls-v1`. Öffentlich ausgeliefertes
  JavaScript und CSS stimmen per SHA-256 exakt mit dem lokalen Bestand überein.
  Eine authentifizierte sichtbare Mehrspieler-Live-Abnahme steht noch aus;
  Gesamtstatus nach der verbindlichen Live-Definition daher weiterhin: nicht
  getan.

## Stormseed´s Perfect – Entwürfe, Kartenverbrauch und gemeinsame Prüfung (21.10.2026)

- Textantworten werden während des Schreibens als serverseitiger Entwurf
  gespeichert; eine in der Auswahl markierte Antwort ebenso. Läuft die
  jeweilige Zeit ab, schreibt der Server einen vorhandenen Text beziehungsweise
  die markierte Wahl automatisch als endgültige Eingabe fest. Leere Texte und
  nicht vorgenommene Wahlen bleiben weiterhin ohne Eingabe.
- Für Begriffe und Kuriositäten eine eigene globale Perfect-Verbrauchsliste
  eingeführt. Bereits in früheren Perfect-Runden verwendete Karten wurden aus
  `nerd_rounds` übernommen. Jede Kategorie verwendet zunächst sämtliche zwölf
  unverbrauchten Karten über alle Lobbys hinweg; erst danach wird ausschließlich
  diese vollständig verbrauchte Kategorie geleert und neu gemischt.
- Während der Host über weitere richtige Antworten entscheidet, sehen nun alle
  Personen dieselbe offizielle Auflösung sowie sämtliche eingereichten
  Spielerantworten mit Urheber. Nur die Kontrollkästchen und die Bestätigung
  bleiben dem Host vorbehalten.
- Release-Kennung auf `2026.10.21-perfect-draft-cycle-v1`, Perfect-Skript auf
  `v=9` und Stylesheet auf `v=15` erhöht. JavaScript- und Python-Syntaxprüfung,
  Fragenprüfung, 19 gezielte Perfect-Tests und alle nun 97 Projekttests
  bestanden. Ein kontrollierter Dienstneustart und die authentifizierte
  Mehrspieler-Live-Abnahme stehen noch aus; Gesamtstatus: nicht getan.

## Stormseed´s Perfect – Pausekorrektur und größere Clubgäste (21.10.2026)

- Nach Nutzeraufnahme den Unterschied zwischen gespeichertem Entwurf und
  eingeloggter Antwort in der Vorlage korrigiert. Ein Entwurf bleibt beim
  Pausieren editierbar, wird nach dem Neuladen wieder ins Eingabefeld gesetzt
  und erscheint nicht als „Eingeloggt“. Auch eine markierte Auswahl bleibt
  beim Pausieren ausschließlich Entwurf. Nur ausdrückliche Abgabe oder echter
  Ablauf der jeweiligen Phasenzeit sperren die Eingabe.
- Die laufende Desktop-Spielbühne anhand der 1920-Pixel-Nutzeraufnahme neu
  proportioniert. Die zentrale helle Karte wurde von maximal 960 auf 860 Pixel
  verschmälert; die seitlichen Clubgäste wachsen von höchstens 220 × 170 auf
  bis zu 290 × 270 Pixel. Ihre Avatare wachsen auf bis zu 220 Pixel Breite,
  die ausgerüsteten Plaketten sowie Namen und Punkte entsprechend mit.
- Die sechs seitlichen Positionen bilden drei räumlich gestaffelte Paare; eine
  siebte Person steht weiterhin mittig unten. Jede Figur erhält einen warmen
  Bodenschein. Die redundante zusätzliche Sprechblase wurde im laufenden Spiel
  entfernt; der eine Statuschip an der Figur bleibt maßgeblich. Unterhalb von
  1.450 Pixeln wechselt die bestehende responsive Spielerreihe einheitlich in
  eine kompakte horizontale Fassung.
- Release-Kennung auf `2026.10.21-perfect-club-guests-v1` und Perfect-CSS auf
  `v=16` erhöht. Fragenprüfung, JavaScript-Syntaxprüfung und alle 97 Tests
  bestanden, darunter ausdrückliche Prüfungen, dass weder Text- noch
  Auswahlentwürfe durch Pause eingeloggt werden. Dienstneustart und sichtbare
  Live-Abnahme stehen noch aus; Gesamtstatus: nicht getan.

## Begriffskarten-Erweiterung – Kandidatenbereinigung (21.10.2026)

- Die zunächst erstellte Liste mit 350 Begriffskandidaten nach ausdrücklicher
  Nutzerkorrektur auf 345 bereinigt. `Chamotte` wurde als bloße Schreibvariante
  von `Schamotte` entfernt; außerdem entfielen die als zu geläufig bewerteten
  Begriffe `Düne`, `Regress`, `Gesims` und `Ausleger`. `Kalfatwerk` bleibt als
  eigenständiger, für normale Spieler nicht ohne Weiteres zuordenbarer Begriff
  enthalten.
- Fünf zuvor irrtümlich als Ersatz eingeführte Begriffe wieder entfernt und
  den nicht beanstandeten ursprünglichen Kandidaten `Zwickelphase`
  wiederhergestellt. Die fortlaufend neu nummerierte Liste liegt nun unter
  `fragen/stormseedsperfekt/BEGRIFFSKANDIDATEN_345.md`.
- Die 345 Kandidaten sind weiterhin noch keine aktiven Karten. Definition,
  Quelle, Eindeutigkeit und Spieltauglichkeit müssen vor Aufnahme in
  `begriffe/fragen.json` einzeln geprüft werden.

## Begriffskarten-Erweiterung – Einzelredaktion und Aktivierung (21.10.2026)

- Für alle 343 gültigen Kandidaten liegt in
  `fragen/stormseedsperfekt/begriffe/entwuerfe_343.tsv` eine eigene kurze
  Kartenauflösung in unveränderter Reihenfolge vor. `Beihol` und
  `Bugsierspill` wurden ohne Ersatz entfernt, nachdem weder die
  Fachwörterbuchsuche noch die Volltextrecherche die exakten Begriffe belastbar
  belegen konnte; belegt war stattdessen nur `Beiholer`.
- `fragen/stormseedsperfekt/begriffe/recherche_343.json` hält für jeden der 343
  Begriffe den tatsächlich abgerufenen Quelleninhalt fest. Neben deutschen
  Wörterbuch- und Lexikoneinträgen wurden für internationale Fachbegriffe auch
  englische Fachseiten und einzelne spezialisierte Quellen verwendet.
- Eine bestandsweite Suche fand keinen der 343 Begriffe als exakten Begriff in
  einer anderen aktiven Fragendatei. Die vom Nutzer ausdrücklich akzeptierte
  Nähe von `Kalfatwerk` zu `kalfatern` bleibt davon unberührt.
- Alle 343 Karten wurden mit den IDs `ssp-begriff-013` bis
  `ssp-begriff-355` in `begriffe/fragen.json` aufgenommen. Zusammen mit den
  zwölf bisherigen Karten enthält die Kategorie nun 355 Karten.
- Verbindliche Fragenprüfung, zusätzliche Kartenprüfung und alle 100
  Projekttests bestanden. Die Wiederholungsprüfung verwendet nun dynamisch die
  vollständige Kategoriegröße. Der Neustartversuch ohne Administratorrechte
  wurde vom System verweigert; der seit 19:50:02 Uhr laufende Dienst verwendet
  daher noch seinen zuvor geladenen Kartenbestand. Administrativer Neustart
  und sichtbare Live-Abnahme sind noch ausstehend; Live-Status: nicht getan.

## Kuriositäten-Erweiterung und bereichsweise Dublettenregel (21.10.2026)

- Auf Nutzerentscheidung gilt die Dublettenprüfung fortan innerhalb des
  jeweiligen Spielbestands: Daily-Fragen werden untereinander geprüft;
  Stormseed´s-Perfect-Begriffe und -Kuriositäten jeweils nur innerhalb ihrer
  eigenen Kategorie. Ein bereits im Daily Quiz behandelter Sachverhalt schließt
  eine für das Bluffspiel geeignete Kuriosität nicht aus.
- Aus der eingereichten 50er-Sammlung wurden 27 belastbar recherchierte
  Kuriositäten übernommen. Tatsachenbehauptungen wurden, wo nötig, in offene
  Fragen umgebaut; belegbar verbreitete Mythen erscheinen ausdrücklich als
  Wanderlegenden. Das echte kommunale Sterbeverbot von Sarpourenx bleibt
  enthalten. Die angeblichen Sterbeverbote im britischen Parlament und auf
  Spitzbergen wurden wieder entfernt.
- Die Kuriositätenkategorie enthält nun 39 Karten. Nicht ausreichend belegbare
  Behauptungen aus Listen angeblich verrückter Gesetze wurden nicht als Fakten
  aktiviert. Innerhalb der 39 Karten wurden keine Sachverhaltsdubletten
  festgestellt.
- `deploy/validate_question_library.py`, 19 gezielte Perfect-Tests und alle 100
  Projekttests bestanden. Der Dienst ist seit 22:05:04 Uhr aktiv und `/health`
  meldet `status: ok`, konnte mangels Administratorrecht aber nicht neu
  gestartet werden. Der geschützte Live-Datenbestand war für das Arbeitskonto
  nicht lesbar; exakte unverbrauchte Perfect-Zahlen sowie die Übernahme des neu
  geladenen Bestands sind deshalb noch nicht nachgewiesen. Live-Status: nicht
  getan.

## Kuriositäten – Produktionsrecherche (21.10.2026)

- Unter `fragen/stormseedsperfekt/KURIOSITAETEN_RECHERCHE_2026-10-21.md` einen
  noch nicht aktivierten Kandidatenkatalog aus Gesetzestexten, Archiven,
  Museen, Universitäten, Fachaufsätzen und zuständigen Institutionen angelegt.
- Der Katalog dokumentiert 55 voneinander unterscheidbare Kartenkerne mit
  offener Frageform, Auflösung, Quelle und Redaktionsstatus: 47 werden von der
  vorhandenen Quelle bereits inhaltlich getragen, 8 bleiben wegen nötiger
  Zweitquelle, historischer Statusprüfung, anekdotischer Überlieferung oder
  möglicher Themenüberschneidung ausdrücklich Reserve.
- Als dauerhafte Quellenfelder wurden Tierverhalten, Erfindungsumwege,
  historische Alltags- und Behördenfälle, Naturphänomene, quellennahe
  Angewohnheiten bekannter Personen, echte Gesetze sowie belegte Wanderlegenden
  abgegrenzt. Kuriose Gesetzeslisten gelten nicht als Quelle.
- Der aktive Bestand blieb unverändert bei 39 Kuriositäten. Die verbindliche
  Fragenprüfung bestand nach Anlage des Recherchekatalogs weiterhin.

## Kuriositäten – zweiter 100er-Recherchekorb (21.10.2026)

- Unter
  `fragen/stormseedsperfekt/KURIOSITAETEN_RECHERCHE_100_2026-10-21.md` einen
  zweiten, noch nicht aktivierten Katalog mit genau 100 neuen Rohkandidaten
  angelegt. Die Verteilung folgt der ersten Ertragsanalyse: 25 Tierverhalten,
  18 Erfindungen/Technik, 17 historische Sonderfälle, 15 Naturphänomene, 12
  dokumentierte Gewohnheiten, 8 Regeln/Gesetze und 5 belegte Wanderlegenden.
- Die maschinell gezählte erste Siebung ergibt 72 quellengetragene A-Kerne, 25
  Reservefälle mit zusätzlichem Beleg- oder Präzisierungsbedarf und 3
  verworfene Behauptungen. Ausgesiebt wurden die Rache-Erfindung der
  Kartoffelchips als Tatsache, Dalís nicht ausreichend belegte persönliche
  Schlüssel-Nickerchenmethode und die im Turiner Regelbestand nicht belegte
  Pflicht zu drei Hundespaziergängen täglich.
- Die 100 Zeilen enthalten 100 Quellenverweise auf 89 unterschiedliche URLs.
  Ein zusätzlicher Textähnlichkeitsvergleich mit den 39 aktiven Kuriositäten
  und den 55 Ansätzen des ersten Korbs ergab keinen Verdachtsfall; die
  semantische Endprüfung bleibt Teil der Kartenredaktion.
- Beide Recherchekörbe enthalten zusammen 119 A-Kerne. Mit den 39 aktiven
  Karten besteht damit ein maximaler redaktioneller Horizont von 158
  Kuriositäten; das ist keine Aktivierungszusage. Der aktive Bestand blieb bei
  39 Karten. `deploy/validate_question_library.py` bestand erneut.


## Kuriositäten – 119 freigegebene Recherchefunde aktiviert (21.10.2026)

- Sämtliche mit `A` bewerteten Funde aus
  `KURIOSITAETEN_RECHERCHE_2026-10-21.md` und
  `KURIOSITAETEN_RECHERCHE_100_2026-10-21.md` als spielbare
  Stormseed´s-Perfect-Kuriositäten aufgearbeitet. Die 47 Funde der ersten und
  72 Funde der zweiten Recherche erhielten die fortlaufenden IDs
  `ssp-kuriositaet-042` bis `ssp-kuriositaet-160`; Reserve- und Ausschussfunde
  wurden nicht aktiviert. Zusammen mit dem bisherigen Bestand enthält die
  Kategorie nun 158 Karten.
- Jede neue Karte besitzt eine offene Frage, eine belastbare Auflösung und die
  im Recherchekatalog geprüfte Quelle mit Status `verified`. Die beiden früher
  entfernten Sterbeverbots-IDs `019` und `020` bleiben unbesetzt. Eine Prüfung
  innerhalb der Kategorie fand weder doppelte IDs noch identische Fragen oder
  Antworten noch auffällige starke Inhaltsüberschneidungen.
- `python3 deploy/validate_question_library.py` war erfolgreich. In der vom
  Dienst verwendeten Python-Umgebung bestanden alle 19 Perfect-Tests und alle
  59 allgemeinen Quiztests. Ein frischer Prozess lud 158 Kuriositäten; nachdem
  die bisherigen 39 Karten in einer isolierten Prüfdatenbank als verwendet
  markiert waren, zog die echte Auswahlfunktion mit `ssp-kuriositaet-078`
  nachweislich eine der neuen Karten.
- Der notwendige kontrollierte Neustart des laufenden Dienstes wurde zunächst
  von systemd mit `Access denied` und über `sudo` anschließend wegen des nicht
  verfügbaren Administratorpassworts abgewiesen. Der Dateibestand im
  Live-Ordner ist vollständig, aber administrativer Neustart und sichtbare
  öffentliche Live-Abnahme stehen deshalb noch aus; Live-Status nach der
  verbindlichen Definition: nicht getan.

## Stormseed´s Perfect – Host kann eine Frage überspringen (21.10.2026)

- Während der Erfindungsphase besitzt ausschließlich der Host neben
  Play/Pause den neuen Knopf „Nächste Frage“. Er ersetzt eine als bekannt oder
  ungeeignet empfundene Karte innerhalb derselben Runde und derselben
  Kategorie. Die Rundennummer, Kategorie und bisherigen Punktestände bleiben
  unverändert; begonnene und eingeloggte Antworten der verworfenen Karte
  werden vollständig entfernt und die neue Frage erhält wieder die volle
  Antwortzeit.
- Die verworfene Karte bleibt in `perfect_question_usage` verbraucht. Die
  Ersatzkarte wird ebenfalls sofort eingetragen. Erst wenn keine weitere
  unverbrauchte Karte derselben Kategorie existiert, wird der vorhandene
  Kategorienzyklus zurückgesetzt; dabei ist die gerade verworfene Karte von
  der unmittelbaren Neuauswahl ausgeschlossen. Eine erweiterte Lobby-Signatur
  sorgt dafür, dass auch die Bildschirme der Gäste bei einem Kartenwechsel in
  derselben Phase zuverlässig neu laden.
- Python- und JavaScript-Syntaxprüfung, verbindliche Fragenprüfung, 21 gezielte
  Perfect-Tests sowie alle 102 Projekttests bestanden. Eine reproduzierbare
  Desktopansicht mit vier tatsächlich vorhandenen Bühnen-Avataren und
  Plaketten liegt unter
  `offline-preview/perfect-next-question-v1/perfect-group-4-avatars.png`.
- Release-Kennung auf `2026.10.21-perfect-next-question-v1`, Perfect-CSS auf
  `v=17` und Perfect-JavaScript auf `v=10` erhöht. Der kontrollierte Neustart
  wurde von systemd erneut mit `Access denied` verweigert. Administrativer
  Neustart und sichtbare öffentliche Funktionsprüfung stehen deshalb noch aus;
  Live-Status: nicht getan.

## Stormseed´s Perfect – Setzkasten-Entwürfe (22.10.2026)

- Zwei vollständige 16:9-Konzeptansichten für vier Spieler erstellt: eine
  antike Oma-/Holzhausfassung und eine deutlich modernere blau-petrolfarbene
  Guesstimate-/Comicfassung. Beide verwenden eine große mittige Pergamentfläche
  und vier bewusst versetzt angeordnete Spielerfächer statt eines symmetrischen
  Vierer- oder Spaltenrasters.
- In beiden Ansichten werden dieselben vier vorhandenen Profilkomponenten mit
  ihren realen Hintergründen, Plaketten, Avataren und hohen Pulten im festen
  Seitenverhältnis 43:57 als Ganzes skaliert. Das bisherige iKuh-Feld zeigt im
  Entwurf jeweils die Punktzahl.
- Die Vorschauen liegen unter
  `offline-preview/perfect-setzkasten-test/setzkasten-oma-4-spieler-v1.png`
  und `offline-preview/perfect-setzkasten-test/setzkasten-modern-4-spieler-v1.png`.
  Es handelt sich ausschließlich um offline erzeugte Gestaltungsentwürfe; die
  laufende Spieloberfläche wurde dadurch nicht verändert.
- Die moderne Richtung anschließend als gewählten Vier-Spieler-Entwurf
  konkretisiert. Alle vier Spielerfenster besitzen darin exakt dieselbe Größe
  und dasselbe feste Seitenverhältnis 43:57; jede vorhandene Profilkomponente
  wird ausschließlich als Ganzes größer skaliert und sitzt vollständig in
  einem eigenen Setzkastenfach. Die versetzte Anordnung bleibt erhalten.
- Die laufende Offline-Lobby zeigt eine echte aktive Kuriositätenfrage samt
  Antwortfeld, Zeit, Pause und „Nächste Frage“. Der ausgewählte Entwurf liegt
  unter
  `offline-preview/perfect-setzkasten-test/setzkasten-modern-laufende-lobby-4-spieler-v2.png`.
  Eine Acht-Spieler-Fassung und Änderungen an der Live-Oberfläche wurden
  ausdrücklich noch nicht vorgenommen.
- Die zunächst weiterhin wie aufgelegte Karten wirkende Fassung verworfen und
  als `setzkasten-modern-laufende-lobby-4-spieler-v3.png` korrigiert: Jedes
  große Fach besitzt nun selbst exakt 43:57. Der persönliche Szenenhintergrund
  bildet die Rückwand des Fachs; Plakette, Avatar und Pult stehen darin. Dicke
  petrolfarbene Setzkastenleisten liegen räumlich vor den Bildkanten und fassen
  sie mit einer inneren Schattenkante ein. Es gibt keinen separaten Kartenrand
  und keinen Kartenschatten mehr. Die vier Fächer besitzen identische Maße;
  die Live-Oberfläche blieb unverändert.
- Nach der markierten Nutzeraufnahme auch diese Fassung verworfen: Dort waren
  die alten Fachgrenzen außerhalb der aufgelegten Profile weiterhin ablesbar.
  Für die neue Fassung `setzkasten-modern-laufende-lobby-4-spieler-v4.png`
  wurde deshalb zuerst der Setzkasten-Hintergrund selbst neu aufgebaut. Alle
  alten Wände und Zwischenböden, die durch die vier Spielerbereiche liefen,
  enden nun an den neuen Öffnungen. Erst danach ersetzen die vier kanonischen
  Profilbilder jeweils vollständig die Rückwand eines Fachs.
- Sämtliche vier Öffnungen besitzen exakt 258 × 342 Pixel und damit ohne
  Rundungsabweichung das vereinbarte Verhältnis 43:57. Es gibt weder einen
  Kartenrahmen noch eine zweite Box: Nur neun Pixel breite Setzkastenstege
  liegen außerhalb der Bildflächen. Der bereinigte Hintergrund ist als
  `setzkasten-modern-background-rebuilt-v1.png` gemeinsam mit der Vorschau im
  Offline-Ordner gespeichert. Live wurde nichts verändert.
- Nach erneuter Nutzerkorrektur auch die bildbasierte Setzkastenfassung nicht
  weiterverwendet. Unter `offline-preview/perfect-setzkasten-precise-v1/` liegt
  nun ein vollständig koordinatengenau neu aufgebauter Setzkasten. Außenrahmen,
  kleine Fächer, Zwischenböden, mittige Pergamentöffnung und vier Spielerfächer
  werden vom reproduzierbaren Werkzeug
  `deploy/render_perfect_setzkasten_precise.py` aus festen Geometrien erzeugt;
  das frühere Setzkastenbild ist keine fertige Unterlage mehr.
- Die vier Spieleröffnungen besitzen jeweils exakt 258 × 342 Pixel (43:57).
  Jede kanonische Profilkopie ersetzt die komplette Rückwand ihrer Öffnung;
  die angrenzenden Regalböden enden außerhalb des Bildes. Es existiert weder
  unter dem Profil noch hinter ihm ein altes Fachraster. Das geprüfte Ergebnis
  heißt `stormseeds-perfect-setzkasten-4-spieler.png`. Keine Live-Datei wurde
  eingebunden oder verändert.
- Die erste präzise Fassung nach Sichtkritik weiter überarbeitet. Die unteren
  Spielerfächer beginnen nun unmittelbar nach einem normalen tragenden Steg;
  die zu flachen Restfächer zwischen und unter den Porträts wurden entfernt.
  Ober- und Unterbereich verwenden keine gleichmäßigen Rasterreihen mehr,
  sondern unterschiedlich breite, unterschiedlich hohe sowie teilweise über
  zwei frühere Reihen reichende Fächer nach dem Prinzip historischer
  Setzkästen. Ergebnis:
  `offline-preview/perfect-setzkasten-precise-v1/stormseeds-perfect-setzkasten-4-spieler-v2.png`.
  Die vier 43:57-Spieleröffnungen und die Offline-Abgrenzung blieben erhalten.
- Das anschließend vom Nutzer vorgegebene rote 160×90-Raster als neue
  maßgebliche Geometrie umgesetzt. Vor jeder Gestaltung wurden die beiden
  Rasterachsen unterschiedlich skaliert, sodass jede 20×30-Rasteröffnung auf
  der 1920×1080-Zeichenfläche exakt 215×285 Pixel und damit 43:57 misst. Erst
  danach wurden die roten Linien als petrolfarbenes Setzkastenholz, die große
  Mittelöffnung als Pergament und die Spieleröffnungen als vollständige
  unverzerrte Profilrückwände ausgeführt.
- Zwei getrennte Offline-Ansichten liegen unter
  `offline-preview/perfect-setzkasten-blueprint-v1/`: Die Vier-Spieler-Fassung
  verwendet ausschließlich die vier weiß markierten Positionen; die
  Sechs-Spieler-Fassung ergänzt exakt die beiden grün markierten Positionen.
  Eine Acht-Spieler-Fassung wurde nicht erstellt. Das reproduzierbare Werkzeug
  ist `deploy/render_perfect_setzkasten_blueprint.py`; Live-Dateien blieben
  unverändert.

## Hauptnavigation und Perfect in Tabletop Connection (22.10.2026)

- Die frühere eingerahmte Navigationsgruppe `multiplayer` vollständig
  entfernt. Die obere Reihenfolge lautet nun `guesstimate`, `guesstimate
  party`, `profil`, `shop`, `regeln`; mit eigenem Abstand folgt der
  kleingeschriebene Knopf `tabletop connection`. Stormseed´s Perfect besitzt
  keinen eigenen Navigationsknopf mehr.
- Alle inaktiven Navigationsknöpfe verwenden eine zurückhaltende dunkelblaue
  Fläche auf der dunkelblauen Leiste. Der jeweils aktive Bereich verwendet
  einheitlich dieselbe grüne Hervorhebung; Party und Tabletop besitzen keine
  abweichenden Sonderfarbe mehr.
- Stormseed´s Perfect als erste Kachel in Tabletop Connection ergänzt. Die
  Kachel verlinkt auf den bestehenden Perfect-Lobbybrowser und verwendet die
  unveränderte vorhandene Originalgrafik
  `carousel-stormseeds-perfect-v1.png`. Die Flyer-Textebene liegt nun als
  gemeinsame Vorlagenkomponente vor und wird von Hauptseitenflyer und
  Tabletop-Kachel identisch verwendet; es wurde keine Ersatzgrafik erzeugt.
- Die Fragenprüfung und alle nun 103 Projekttests bestanden. Eine isoliert
  gerenderte angemeldete Vorschau bestätigte Reihenfolge, Kleinschreibung,
  fehlenden Multiplayer-Rahmen, fünf Tabletop-Kacheln und Perfect an erster
  Stelle. Die vier geänderten Stylesheets wurden öffentlich bytegenau identisch
  zum lokalen Bestand ausgeliefert; ebenso war die öffentliche Perfect-Grafik
  bytegenau mit dem unveränderten lokalen Original identisch. Der öffentliche
  Health-Endpunkt meldete `status: ok`, der Dienst war `active`.
- Eine authentifizierte sichtbare Abnahme der öffentlichen Haupt- und
  Tabletop-Seite konnte in der Arbeitsumgebung nicht selbst beobachtet werden.
  Nach der verbindlichen Live-Definition bleibt diese letzte Browserabnahme
  daher offen; vollständiger Live-Status: noch nicht getan.

## Korrektur der doppelten Seitenköpfe und der Perfect-Kachel (22.10.2026)

- Den alten, zusätzlich unter der Hauptnavigation ausgegebenen Seitenkopf mit
  Wortmarke und Datumsplakette in Tabletop Connection, sämtlichen
  Guesstimate-Party-Ansichten, Profil und Shop entfernt. Die Hauptnavigation
  mit ihrer Wortmarke und dem einen Datum bleibt unverändert erhalten. Die
  verwendeten Hintergrund- und Kachelbilder wurden nicht verändert.
- Die kleine Zeile über `Tabletop Connection` durch helle Schrift, höheres
  Gewicht und einen kräftigen dunklen Textschatten auf dem detailreichen
  Hintergrund lesbar gemacht.
- Auf der Perfect-Kachel den dunklen, umrandeten Textkasten entfernt. Der
  gemeinsame Flyertext erhält nur innerhalb dieser Kachel eine kompakte,
  linksbündige Anordnung am unteren Bildrand mit einem unteren Verlauf; die
  drei Tiere bleiben vollständig sichtbar.
- Die Fragenprüfung und alle 103 Projekttests bestanden. Eine frische,
  authentifizierte lokale Laufzeitvorschau wurde bei 1406 × 700 Pixeln
  tatsächlich gerendert: Tabletop zeigt weder den alten Seitenkopf noch das
  zweite Datum; die Zeile über der Überschrift ist lesbar und die
  Perfect-Kachel besitzt keinen Textrahmen. Party, Profil und Shop wurden im
  Browser zusätzlich jeweils mit genau einer Hauptnavigation und ohne
  `.game-header` geprüft.
- Der öffentliche Health-Endpunkt meldete `status: ok`; der Dienst war
  `active` mit `NRestarts=0`. Das öffentlich ausgelieferte
  `card-table.css?v=12` enthielt die aktuellen Korrekturen. Ein Dienstneustart
  war für diese Vorlagen- und CSS-Änderungen nicht erforderlich, da die App
  `TEMPLATES_AUTO_RELOAD=True` verwendet und statische Dateien direkt
  ausgeliefert werden. Eine authentifizierte öffentliche Browseraufnahme
  steht dennoch noch aus; nach der verbindlichen Live-Definition bleibt diese
  letzte Produktionsabnahme offen.

## Seitenkopfkorrektur für Perfect und Standard-Kartentisch (22.10.2026)

- Den geerbten alten Seitenkopf mit zusätzlicher Guesstimate-Wortmarke und
  Datumsplakette auch aus der Stormseed´s-Perfect-Lobbyübersicht, der
  Standard-Kartentisch-Lobbyübersicht und bereits erstellten
  Standard-Kartentisch-Lobbys entfernt. Die verbindliche Hauptnavigation mit
  genau einer Wortmarke und einem Datum bleibt erhalten. Die eigenständige
  Perfect-Spiellobby verwendete diesen geerbten Kopf nicht und blieb in ihrem
  Aufbau unverändert.
- In der Perfect-Lobbyübersicht `BLUFFEN, WISSEN, ÜBERZEUGEN` sowie den Satz
  `Oder weißt du etwa nicht, was ein Apotropaion ist?` vergrößert, deutlich
  fetter gesetzt, aufgehellt und durch einen dunklen, weichen Textschatten vom
  detailreichen Originalhintergrund abgehoben. Kein Bildasset wurde verändert.
- Fragenprüfung und alle 103 Projekttests bestanden. Eine frische
  authentifizierte Laufzeitvorschau wurde für alle drei betroffenen Ansichten
  bei 1406 Pixel Breite im Browser gerendert. In jeder Ansicht war
  `.game-header` genau nullmal vorhanden; die beiden Perfect-Zeilen waren auf
  dem Hintergrund sichtbar und lesbar.
- Der öffentliche Health-Endpunkt meldete `status: ok`; der Dienst war
  `active/running` mit `NRestarts=0`. Das öffentlich ausgelieferte
  `stormseeds-perfect.css?v=18` war per SHA-256 bytegenau identisch mit dem
  lokalen Bestand. Eine authentifizierte öffentliche Browseraufnahme steht
  weiterhin aus; die letzte Produktionsabnahme erfolgt nach dem Neuladen durch
  den Nutzer.

## Würfeltisch – Kacheln und Offline-Lobbygrundlage (22.10.2026)

- Tabletop Connection von fünf auf sieben Kacheln erweitert. Die bestehende
  Fünferbreite bleibt unverändert; `Mäxchen` ist die sechste Kachel und beginnt
  damit die zweite Reihe, gefolgt von `Schweinchen`. Beide verwenden vorläufig
  das vorhandene Würfeltischmotiv und bleiben als `Demnächst` unanklickbar.
- Einen gemeinsamen Würfeltisch-Unterbau bis einschließlich Lobbyerstellung
  und Lobbybeitritt vorbereitet. Er besitzt einen eigenen Lobbybrowser, bis zu
  sechs dauerhafte Lobbyplätze, Gastgeberübertragung beim Verlassen und eine
  wartende Lobbyansicht. Ein Spielstart, Würfe, Becher- oder Würfelanzahl sind
  ausdrücklich noch nicht implementiert; der sichtbare Startknopf ist deshalb
  deaktiviert und eine Startroute existiert nicht.
- Die Lobby verwendet die bestehende kanonische Profilfenster-Komponente für
  jede anwesende Person. Das Makro unterstützt dafür nun fremden Namen,
  Guthaben und eindeutige Elementkennungen, ohne die Innenkomposition zu
  duplizieren. Der vorhandene Würfeltisch verlinkt direkt auf den neuen
  Lobbybrowser; ausschließlich Mäxchen und Schweinchen bleiben gesperrt.
- Aus dem quadratischen Würfeltischmotiv per integrierter Bildgenerierung die
  breite, elementfreie Kulisse `static/dice-table-lobby-background-v1.png`
  erstellt. Sie enthält keine Spieler oder Bedienoberfläche und hält die
  Tischmitte für dynamische Inhalte frei.
- `deploy/validate_question_library.py` erfolgreich; anschließend alle 106
  Projekttests bestanden, darunter drei neue Würfeltischprüfungen für Kacheln,
  Erstellen/Beitreten, kanonische Profilfenster und den absichtlich fehlenden
  Startpfad. Keine Live-Aktivierung oder sichtbare öffentliche Abnahme
  vorgenommen; der lokale Dienst war aus der Arbeitsumgebung nicht erreichbar.
- Korrektur nach Nutzerhinweis: Den irrtümlich eingeführten konfigurierbaren
  Würfeltisch-Schalter wieder entfernt. In jedem frisch gestarteten
  Anwendungsprozess ist die Würfeltisch-Kachel automatisch aktiv und verlinkt
  direkt auf den Lobbybrowser; eine optionale Aktivierungsentscheidung gibt es
  nicht. Lediglich eine nicht konfigurierbare Verfügbarkeitsmarke schützt den
  noch laufenden alten Prozess davor, vor dem Neustart eine unbekannte Route in
  der automatisch neu geladenen Vorlage zu verlinken.
- Fragenprüfung, 23 gezielte Tabletop-/Würfeltischtests und erneut alle 106
  Projekttests bestanden. Der erforderliche Neustart von
  `guesstimate.service` wurde durch systemd mit `Access denied` verweigert.
  Deshalb zeigt der laufende alte Prozess weiterhin die bisherige gesperrte
  Würfeltisch-Kachel; nach einem administrativen Dienstneustart wird sie ohne
  weiteren Schalter automatisch anklickbar. Live-Status: nicht getan.

## Würfeltisch – Spielgrundlage mit dddice-Physik (22.10.2026)

- Die wartende Würfeltisch-Lobby um die Gastgeberoptionen `1–5 Würfel` und
  `Becher Ja/Nein` sowie einen tatsächlichen Spielstart erweitert. Nach dem
  Start schließt die Bild-im-Bild-Lobby; die kanonischen Profilfenster werden
  an den äußeren Tischplätzen angeordnet und unten erscheint ein Spielerpult
  mit Notizzettel sowie `Einsammeln`, `Würfeln` und bei Bechern `Aufdecken`.
- dddice-js 0.21.8 samt MIT-Lizenz und Drittanbieterhinweisen lokal eingebunden.
  Verwendet wird das öffentliche Theme `Outgunned Reimagined` mit seinem
  nummerierten W6. Der Browser erzeugt dafür einen anonymen dddice-Gastzugang;
  ein persönlicher Kontoschlüssel oder eine Verbindung zum Nutzerkonto wird
  nicht benötigt und nicht gespeichert.
- Das Zufallsergebnis entsteht ausschließlich auf dem eigenen Server. dddice
  stellt die vorgegebenen Werte mit seiner 3D-Physik dar. Würfel bleiben bis
  zum bewussten Einsammeln liegen. Ohne Becher sehen alle Mitglieder denselben
  Wurf; mit Becher werden die Werte nur an die würfelnde Person ausgeliefert.
  Der Becher bleibt aufrecht über dem verdeckten Wurf und wird beim Aufdecken
  angehoben. Andere Mitglieder erhalten auch danach keine verdeckten Zahlen.
- Der Notizzettel führt alle Spielernamen und bis zu sechs Würfe je Person.
  Private Becherwürfe erscheinen für andere lediglich als `verdeckt`.
- Die tatsächlich würfel- und becherfreie Tischkulisse
  `static/dice-table-background-v2.png` ersetzt im Würfeltisch die frühere
  Kulisse, die entgegen der vorherigen Logbeschreibung noch feste Würfel und
  einen Becher enthielt.
- Python- und JavaScript-Syntaxprüfung, Fragenprüfung, fünf gezielte
  Würfeltischtests und alle 108 Projekttests bestanden. Der öffentliche
  dddice-Gastzugang und das angegebene Theme wurden vor der Integration
  erfolgreich abgefragt. Ein administrativer Neustart von
  `guesstimate.service` wurde erneut mit `Access denied` verweigert; die neue
  serverseitige Spiellogik läuft deshalb im alten Dienstprozess noch nicht.
  Eine sichtbare Browserabnahme der 3D-Bewegung steht aus. Live-Status: nicht
  getan.

## Würfeltisch – fehlende 3D-Würfel behoben (22.10.2026)

- Nach der Nutzerbeobachtung, dass das Ergebnis berechnet und angezeigt wurde,
  aber keine Würfel sichtbar waren, die Laufzeitabhängigkeit vom direkten
  dddice-API- und CDN-Zugriff des Spielerbrowsers entfernt. Diese Trennung
  erklärt das Fehlerbild: Die eigene Spiellogik arbeitete, während das externe
  3D-Modell beziehungsweise seine Texturen nicht geladen wurden.
- Die vollständige öffentliche Setbeschreibung von `Outgunned Reimagined`
  sowie alle 23 unterschiedlichen referenzierten Modelle, Texturen,
  Vorschauen und Sounds liegen nun lokal unter
  `static/vendor/dddice-outgunned/`. Die Setbeschreibung wird beim Laden auf
  diese lokalen Dateien umgebogen. Der zuvor verwendete anonyme Gastzugang im
  Browser entfällt vollständig; während des Spiels ist keine Verbindung zu
  dddice erforderlich.
- Die öffentliche Auslieferung der neuen Setbeschreibung, des W6-Modells und
  von `dice-table.js?v=3` mit HTTP 200 geprüft; die öffentlich abgerufenen
  Dateien waren jeweils per SHA-256 bytegleich mit dem lokalen Bestand. Alle
  24 Asset-Verweise der Setbeschreibung wurden geprüft, keine lokale Datei
  fehlt.
- JavaScript- und Python-Syntaxprüfung, Fragenprüfung, fünf gezielte
  Würfeltischtests sowie alle 108 Projekttests bestanden. Eine erneute
  sichtbare Abnahme des 3D-Wurfs im authentifizierten Spiel durch den Nutzer
  ist noch erforderlich; bis dahin Live-Status nach Projektdefinition: nicht
  vollständig getan.

## Würfeltisch – dddice-Aufruf korrigiert (22.10.2026)

- Nachdem trotz vollständig lokaler Assets weiterhin nur das berechnete
  Ergebnis erschien, die konkrete dddice-0.21.8-Ausführung geprüft. Ursache:
  `rollLocal` erwartet intern trotz optionaler Schnittstellendeklaration ein
  Spielerobjekt; ohne dessen UUID brach die 3D-Ausführung vor dem Erzeugen der
  Würfel ab. Jeder lokale Wurf erhält nun eine rein lokale, tischbezogene
  Spielerkennung.
- Zusätzlich berücksichtigt dddice 0.21.8 den übergebenen Wert eines lokalen
  Würfels nicht, sondern wählt zunächst selbst einen Wert. Der Adapter führt
  ausschließlich diese Wertauswahl deterministisch auf das bereits vom
  eigenen Server bestimmte Ergebnis; UUIDs, Flugbahn, Drehung, Zusammenstöße
  und Endbewegung bleiben physikalisch zufällig. Das Aufrufmuster wurde für
  alle fünf möglichen Würfel mit `5, 1, 6, 3, 2` geprüft und lieferte exakt
  dieselbe Folge.
- Fehler der 3D-Engine werden nicht länger verschluckt, sondern im Spiel mit
  ihrer konkreten Meldung angezeigt; die numerische Ersatzdarstellung bleibt
  erhalten. `dice-table.js?v=4` wurde öffentlich mit HTTP 200 und bytegleichem
  SHA-256 ausgeliefert. JavaScript-Syntaxprüfung, fünf gezielte
  Würfeltischtests, Fragenprüfung und alle 108 Projekttests bestanden. Die
  sichtbare Abnahme nach Neuladen durch den Nutzer steht weiterhin aus.

## Würfeltisch – Spielerperspektive der 3D-Kamera (22.10.2026)

- Die dddice-Standardkamera als weiterer Darstellungsfehler identifiziert: Sie
  stand bei `x=0, y=50, z=0` senkrecht über dem Spielfeld und überschrieb die
  zuvor berechnete Blickrichtung zusätzlich durch Standardrotation und
  Nullquaternion. Damit entsprach sie weder der Person am unteren Bildschirmrand
  noch der Perspektive der Tischgrafik.
- Die Kamera für `dice-table.js?v=5` unten vor den Tisch versetzt
  (`x=5, y=18, z=26`), leicht seitlich ausgerichtet und ohne überschreibende
  Rotation/Quaternion auf die Tischmitte blicken lassen. Ziel ist eine
  erkennbare Ober-, Vorder- und Seitenfläche der Würfel.
- Die bestehende dddice-Physik besitzt Boden und vier unsichtbare rechteckige
  Seitenwände. Bei der jetzigen Kamera-/Flächenkonfiguration begrenzen sie eine
  Fläche von ungefähr 26 × 14 internen Einheiten; sie folgen derzeit nicht dem
  sichtbaren ovalen Holzrand. Diese Banden wurden bewusst noch nicht verändert,
  damit zunächst die Kameraperspektive separat abgenommen werden kann.
- Fragenprüfung, fünf gezielte Würfeltischtests und alle 108 Projekttests
  bestanden. Das öffentliche `dice-table.js?v=5` wurde mit HTTP 200 und
  bytegleichem SHA-256 geprüft. Die sichtbare Abnahme im authentifizierten
  Spiel bleibt offen.

## Würfeltisch – Teilwürfe, Ablage und persönliche Kamerasperre (22.10.2026)

- Die Lobbyoption `Becher Ja/Nein` ohne Bechergrafik in `Verdecktes Würfeln
  Ja/Nein` umbenannt. Bei aktivierter Option bleibt der eigentliche
  Zahlenwurf vollständig unsichtbar, bis die würfelnde Person `Aufdecken`
  betätigt; andere Personen erhalten die privaten Augenzahlen weiterhin
  nicht. Als vorläufige Verdecktdarstellung erscheinen neutrale animierte
  Guesstimate-G-Würfel. Eine endgültige sechsseitige Markentextur benötigt
  noch die festzulegende quadratische Logo-Fläche.
- Jeden sichtbaren Ergebniswürfel für die würfelnde Person einzeln anwählbar
  gemacht. Angewählte Würfel verschwinden aus dem 3D-Bereich und erscheinen
  im Spielerpult; ein erneuter Klick nimmt die Auswahl zurück. Der Wurfknopf
  nennt dynamisch die ausgewählte Anzahl. Ist nichts ausgewählt, werden ohne
  vorheriges Einsammeln alle konfigurierten Würfel neu geworfen.
- Bei einem Teilwurf werden alle nicht ausgewählten Würfel aus der
  Physikfläche entfernt und als geschützte Reihe links auf dem Tisch abgelegt.
  Nur die im Pult ausgewählten Würfel werden neu animiert. Dadurch können alte
  Würfel den neuen Wurf nicht physikalisch behindern. Abgelegte Würfel lassen
  sich wieder ins Pult holen; `Alle einsammeln` nimmt aktive und abgelegte
  Würfel gemeinsam auf.
- Den serverseitigen Tischzustand von einer bloßen Ergebnisliste auf einzelne
  Würfel mit stabiler Kennung und den Zonen `active`, `tray` und `held`
  erweitert. Der Notizzettel führt weiterhin Namen und Wurffolgen; bei einem
  Teilwurf wird nur die tatsächlich neu geworfene Folge ergänzt.
- Eine kontobezogene Option `Kamera fixieren – nur für mich` ergänzt. Beim
  Aktivieren werden Kameraposition und Blickziel des aktuellen Accounts
  gespeichert und die 3D-Steuerung gesperrt. Deaktivieren gibt die Kamera zum
  erneuten Einstellen frei; die Einstellung anderer Accounts bleibt
  unberührt.
- Fragenprüfung, Python- und JavaScript-Syntaxprüfung sowie alle 110
  Projekttests bestanden. Ein neuer Ablaufstest bildet den vereinbarten
  Kniffel-Fall `5 → 3 neu/2 behalten → 1 neu/4 behalten` vollständig ab.
  Der notwendige administrative Neustart von `guesstimate.service` wurde aus
  dieser Arbeitsumgebung sowohl direkt als auch mit angeforderten Rechten
  verweigert; `sudo` verlangt ein nicht verfügbares Passwort. Die sichtbare
  Live-Abnahme ist daher noch offen. Live-Status: nicht getan.

## Kniffeltisch – gemeinsamer Unterbau, drei Würfe und Wertungsblock (22.10.2026)

- Das vom regelmäßigen Statusabruf ausgelöste erneute Einfliegen der Würfel in
  die linke Behalten-Ablage und in das Spielerpult behoben. Beide Bereiche
  gleichen nun stabile Würfelkennungen ab und bauen ihre Elemente nur bei
  einer tatsächlichen Auswahl- oder Zonenänderung neu auf. Unveränderte Würfel
  bleiben zwischen den Statusabrufen fest stehen. Dasselbe gilt für die
  vorläufige Verdecktdarstellung.
- Die bisher gesperrte Kniffel-Kachel in Tabletop Connection geöffnet und eine
  eigene Kniffel-Lobby ergänzt. Standardwürfeltisch und Kniffel verwenden
  weiterhin dieselbe verbindliche Lobby-, Profilfenster-, Würfelphysik- und
  Spielerpult-Implementierung; Kniffel ist ein eigener Spielmodus statt einer
  abweichenden Kopie. Seine Lobby ist vom offenen Standardwürfeltisch getrennt
  und verwendet fest fünf Würfel sowie drei Würfe je Zug.
- Für Kniffel eine serverseitige Zugreihenfolge eingeführt. Nur die jeweils
  aktive Person darf würfeln; nach jedem Wurf erlischt eines von drei
  Wurflichtern. Nach dem dritten Wurf ist kein weiterer Wurf möglich. Ein Zug
  endet mit dem Eintragen einer Wertung, danach werden Tisch und Auswahl
  geleert, drei Wurflichter aktiviert und die nächste Person freigeschaltet.
- Den bisherigen Wurfnotizzettel im Kniffelmodus durch einen gemeinsamen
  Kniffelblock ersetzt. Er erzeugt für jedes beim Start anwesende Mitglied eine
  eigene Spalte. Freie Felder der aktiven Person zeigen nach einem Wurf direkt
  den berechneten Wert und tragen ihn per Klick verbindlich ein; belegte Felder
  können nicht erneut verwendet werden. Einser bis Sechser, Dreierpasch,
  Viererpasch, Full House, kleine und große Straße, Fünferpasch und Chance
  sowie oberer Zwischenstand, 63-Punkte-Bonus und Gesamtsumme sind enthalten.
  Eine Nullwertung kann regelgerecht zum Streichen eingetragen werden.
- Zuschauer erhalten Würfelstand, aktiven Spieler, Wurflichter und neue
  Einträge über denselben Statusabruf und können den laufenden Zug verfolgen,
  ohne selbst würfeln oder in eine fremde Spalte eintragen zu können.
- Datenbestand um den Spielmodus und einen eigenen Kniffelzustand erweitert;
  bestehende Würfeltische werden bei der Migration als Standardwürfeltisch
  eingeordnet. Lobbylisten und die Beschränkung auf eine eigene aktive Lobby
  gelten getrennt pro Spielmodus.
- Fragenprüfung, Python- und JavaScript-Syntaxprüfung, elf gezielte
  Würfeltisch-/Kniffeltests und alle 114 Projekttests bestanden. Die Tests
  decken zwei dynamische Spielerspalten, drei erlaubte Würfe, einen abgewiesenen
  vierten Wurf, fremde Würfelversuche, Chance-Eintrag, Spielerwechsel, die
  Standardwertungen und die nicht erneut gestartete Ablageanimation ab.
- Der erforderliche Neustart von `guesstimate.service` wurde erneut durch
  systemd mit `Access denied` verweigert. Damit sind Python-Routen und
  Datenmigration im laufenden alten Prozess noch nicht geladen; eine sichtbare
  öffentliche Browserabnahme war nicht möglich. Live-Status: nicht getan.
- Unmittelbare Laufzeitkorrektur nach einem 500-Fehler in Tabletop Connection:
  Die automatisch neu geladene Vorlage hatte im alten Prozess bereits
  `url_for('kniffel_index')` ausgewertet, obwohl dieser Prozess die neue
  Python-Route noch nicht registriert hatte. Die Kniffel-Kachel ist nun wie
  zuvor der Würfeltisch durch eine prozessgebundene Verfügbarkeitsmarke
  geschützt. Im alten Prozess erscheint sie bis zum Neustart wieder als
  unanklickbares `Demnächst`; ein frisch gestarteter Prozess aktiviert sie
  automatisch. Ein Regressionstest simuliert den alten Prozess ohne Marke und
  bestätigt HTTP 200 für `/karten`. Alle 32 gezielten Tabletop- und
  Würfeltischtests bestanden; der öffentliche nicht angemeldete Aufruf von
  `/guesstimate/karten` antwortete wieder regulär mit der erwarteten
  Login-Weiterleitung statt einem Serverfehler.
- Zweite Laufzeitkorrektur nach dem anschließenden Ausfall des vorhandenen
  Würfeltisch-Lobbybrowsers: Auch `dice_table_index.html` hatte bereits die
  neuen, vom alten Prozess noch nicht übergebenen Endpunktnamen erwartet. Alle
  gemeinsam genutzten Würfeltischvorlagen besitzen nun ausdrückliche
  Standardwerte für den bisherigen Standardmodus und seine vorhandenen
  Endpunkte. Damit bleiben Tabletop Connection, Würfeltisch-Lobbybrowser,
  bestehende Lobby und Spielansicht während des alten Prozesses kompatibel.
  Ein eigener Regressionstest rendert den Lobbybrowser absichtlich ohne den
  neuen Vorlagenkontext und bestätigt weiterhin die vorhandene
  `/karten/wuerfeltisch/erstellen`-Aktion. Alle 33 gezielten Tabletop- und
  Würfeltischtests bestanden. Kniffel bleibt bis zum administrativen
  Dienstneustart bewusst `Demnächst`, weil seine Python-Routen im alten
  Prozess technisch noch nicht existieren.

## Kniffeltisch – stabiler Sammelzustand und kompaktes Wertungsblatt (22.10.2026)

- Nach Nutzerbeobachtung zwei Ursachen für zurückspringende Behalten-Würfel
  abgesichert. Der Browser verwirft verspätet eintreffende Statusantworten mit
  älterer Revisionsnummer, sodass ein bereits eingesammelter Würfel nicht mehr
  durch einen überholten Poll erneut im Behalten-Feld gezeichnet wird. Die
  Aktion `Alle einsammeln` setzt außerdem die Rückkehrzone aller Würfel
  ausdrücklich auf die aktive Tischfläche; eine spätere Abwahl im Pult führt
  damit nicht zurück in die Behalten-Ablage. Einzelnes Hin- und Herschalten
  eines bewusst behaltenen Würfels bleibt unverändert möglich.
- Den bereitgestellten klassischen Kniffelblock als Gestaltungsreferenz
  ausgewertet und den interaktiven Block entsprechend neu aufgebaut: zwei
  Abschnitte `Erster Teil` und `Zweiter Teil`, eigene schmale Regelspalte,
  obere Kategorien `1er` bis `6er`, Bonuszeile, getrennte Zwischensummen,
  Dreier-/Viererpasch, Full House, beide Straßen, Kniffel, Chance und
  Endsumme. Das Referenzbild wird nicht als starres Hintergrundbild verwendet;
  alle Felder bleiben echte dynamische und anklickbare Spielelemente.
- Jede Spielerspalte besitzt nun unabhängig von der Spielerzahl eine feste
  Breite von 52 Pixeln; der Block wächst nur um genau eine solche Spalte pro
  Person und fasst sechs Spieler auf dem Pult. Der Spielername steht gekürzt im
  Spaltenkopf und vollständig im Hinweistext. Kategorie und Rechenregel
  beanspruchen zusammen 196 Pixel.
- Die serverseitigen Summen um `Summe Erster Teil` und `Summe Zweiter Teil`
  ergänzt, damit der Aufbau des klassischen Blatts vollständig dargestellt
  werden kann. Fragenprüfung, Syntaxprüfungen, 33 gezielte Würfeltischtests und
  alle 116 Projekttests bestanden.
- `dice-table.js?v=8` und `dice-table.css?v=5` werden öffentlich bereits mit
  HTTP 200 und bytegleichem SHA-256 ausgeliefert; damit sind Poll-Schutz und
  Blockgestaltung nach Neuladen wirksam. Der laufende Gunicorn-Prozess stammt
  von 21:14 Uhr und benötigt für die zusätzliche serverseitige Rückkehrzone
  noch einen Neustart. `sudo -n systemctl restart guesstimate.service` wurde
  mangels Passwort verweigert; die sichtbare authentifizierte Endabnahme bleibt
  offen. Live-Status: nicht vollständig getan.

## Kniffeltisch – separates Wertungsblatt und kompaktes Holzpult (22.10.2026)

- Nach visueller Nutzerabnahme den Kniffelblock vollständig aus dem bisherigen
  überbreiten Spielerpult gelöst. Das interaktive Blatt liegt nun als eigenes,
  leicht gedrehtes Papier rechts auf dem Tisch (`top: 238px`, `right: 250px`),
  also außerhalb des unteren Bedienpults. Seine dynamische Breite für bis zu
  sechs Spieler, Kategorien, Regeln und anklickbaren Wertungsfelder bleiben
  unverändert erhalten.
- Das Kniffel-Spielerpult auf 720 Pixel Breite und ungefähr 146 Pixel
  Mindesthöhe verkleinert und mittig am unteren Tischrand platziert. Der
  Standardwürfeltisch verwendet weiterhin seine bisherige Pultkomposition.
- Dem Kniffelpult ausschließlich mit konsolidierten Komponentenregeln eine
  mehrschichtige Holzmaserung, helle obere und dunkle untere Kante,
  Vertiefungsschatten und eine eingelassene Würfelablage gegeben. Die
  Aktionsknöpfe besitzen nun Verlauf, Glanzkante, Sockelschatten sowie eigene
  Hover- und gedrückte Zustände; der primäre Würfelknopf bleibt farblich klar
  hervorgehoben.
- Alle 33 gezielten Tabletop-/Würfeltischtests und alle 116 Projekttests
  bestanden. `dice-table.css?v=6` wird öffentlich mit HTTP 200 und bytegleichem
  SHA-256 ausgeliefert. Da diese Änderung nur automatisch neu geladene Vorlage
  und Stylesheet betrifft, ist kein weiterer Dienstneustart nötig; eine
  authentifizierte sichtbare Endabnahme erfolgt nach dem Neuladen durch den
  Nutzer.
- Position nach Bildkorrektur angepasst: Das separate Kniffelblatt liegt nicht
  mehr rechts oben, sondern entsprechend der markierten zweiten Darstellung
  unten links (`left: 92px`, `bottom: 22px`). Größe, Spaltenbreiten und
  Holzpult bleiben unverändert. 33 gezielte Tests bestanden;
  `dice-table.css?v=7` wird öffentlich bytegleich ausgeliefert.

## Mäxchen-Tisch und einheitliche Sitzreihenfolge (22.10.2026)

- Den vorhandenen Mäxchen-Einstieg als eigenen Spielmodus mit getrennten
  Lobbys, zwei bis sechs Personen, zwei Würfeln und serverseitiger
  Zugreihenfolge umgesetzt. Die Reihenfolge bleibt für alle Ansichten gleich;
  zusätzlich wurde der Kartentisch auf dieselbe kanonische, nur um den eigenen
  Sitz gedrehte Reihenfolge umgestellt.
- Die vereinbarten Hausregeln sind verbindlich im Spielzustand und im
  Regel-Dialog abgebildet: Ansagen müssen strikt steigen; jede Person beginnt
  mit drei Leben, schwimmt nach dem zweiten verlorenen Leben und scheidet nach
  dem dritten aus; der Rundenverlierer eröffnet die nächste Runde. Wer ein
  angesagtes Mäxchen glaubt, verliert ein Leben und darf vorlegen. Wird ein
  tatsächlich gewürfeltes Mäxchen erfolglos angezweifelt, kostet dies zwei
  Leben.
- Nach dem serverseitigen Wurf sieht ausschließlich die würfelnde Person die
  Augen. Alle anderen sehen zwei animierte dreidimensionale Logowürfel; sechs
  Seiten verwenden dasselbe neue dunkelblaue Mäxchen-21-Logo. `Aufdecken`
  veröffentlicht die echten Würfel für alle. Die Darstellung ist als eigene
  Würfelhaut vorbereitet, damit spätere Shop-Skins an derselben Stelle
  eingesetzt werden können.
- Die klassische Rangfolge 31 bis 65, anschließend Pasche 11 bis 66 und
  Mäxchen 21 wurde anhand der Spielanleitungen von SOL-EXPERT und des
  Landesbildungsservers Baden-Württemberg sowie der Spielübersicht bei
  Wikipedia geprüft. Abweichende Hausregeln wurden ausschließlich gemäß der
  Nutzerentscheidung umgesetzt.
- Python- und JavaScript-Syntaxprüfung, Fragenbibliotheksprüfung, 37 gezielte
  Tabletop-Tests und alle 120 Projekttests bestanden. Die automatisierten
  Mehrspielertests belegen verdeckte Würfel, gemeinsames Aufdecken,
  Doppelschaden beim echten Mäxchen, Leben/Schwimmen/Ausscheiden, den
  Führungswechsel nach Glauben und die identische Sitzreihenfolge.
- Der lokale zweipersönliche Vorschaustand wurde erzeugt und im Codex-Browser
  zur Ansicht bereitgestellt. Der erforderliche Neustart von
  `guesstimate.service` wurde durch systemd mit `Access denied` verweigert. Der
  laufende Prozess liefert deshalb weiterhin Release
  `2026.10.21-perfect-next-question-v1` und für `/karten/maexchen` HTTP 404;
  öffentlich ist der neue Modus noch nicht aktiv. Live-Status: nicht getan.

## Stormseed´s Perfect – acht Profilfensterplätze (22.10.2026)

- Die serverseitige Perfect-Kapazität von sieben auf acht anwesende Personen
  erhöht. Ein neuer Ablaufstest belegt, dass die achte Person beitreten kann,
  die neunte Person aber weiterhin abgewiesen wird. Lobbyübersicht,
  Raumzähler und Perfect-Regeltext beziehen ihre Zahl aus derselben
  Kapazitätskonfiguration; während des noch laufenden alten Prozesses bleibt
  die bisherige Siebenerangabe deshalb wahrheitsgemäß erhalten.
- Die separate Perfect-Komposition aus Avatar und kurzer Shop-Plakette in
  Lobby und Spiel vollständig aus der Vorlage entfernt. Jede anwesende Person
  verwendet nun die unveränderte kanonische Profilfenster-Komponente mit
  persönlichem Hintergrund, Spruch, Avatar, hohem Pult, Namen und iKuh-Stand.
  Nur das gesamte Fenster wird für Perfect proportional skaliert. Bis zu vier
  tatsächlich anwesende Personen stehen an der linken, bis zu vier an der
  rechten Wand; leere Platzhalter werden weiterhin nicht ausgegeben.
- Python- und JavaScript-Syntaxprüfung, verbindliche Fragenprüfung, 22 gezielte
  Perfect-Tests sowie alle nun 121 Projekttests bestanden. Das neue
  `stormseeds-perfect.css?v=19` wird öffentlich bereits mit HTTP 200 und
  bytegleicher SHA-256-Prüfsumme ausgeliefert.
- Der für die neue Python-Kapazität erforderliche kontrollierte Neustart von
  `guesstimate.service` wurde mit `Access denied` verweigert. Der öffentliche
  Health-Endpunkt meldet deshalb weiterhin Release
  `2026.10.22-maexchen-table-v1`; die Acht-Spieler-Logik ist im laufenden
  Prozess noch nicht aktiv. Eine authentifizierte sichtbare Abnahme der beiden
  Viererwände steht ebenfalls aus. Gesamtstatus nach der verbindlichen
  Live-Definition: nicht getan.

## Stormseed´s Perfect – Punkte im Profilfenster und Lobby ohne Chat (23.10.2026)

- Den Lobbychat einschließlich Schnellreaktionen vollständig aus der
  Perfect-Oberfläche entfernt. Der zugehörige Schreib-Endpunkt und die
  Chat-/Reaktionsdaten im Lobby-Polling sind ebenfalls entfernt; vorhandene
  historische Datenbankfelder und -einträge wurden bewusst nicht gelöscht.
- Die kanonische Profilfenster-Komponente um einen optionalen Spielewert
  erweitert. Ausschließlich Stormseed´s Perfect übergibt den aktuellen
  Punktestand und zeigt dadurch `Punkte` ohne Kuhsymbol an. Alle regulären
  Profilfenster verwenden unverändert den bisherigen iKuh-Stand und dieselbe
  Innenkomposition.
- Python- und JavaScript-Syntaxprüfung, verbindliche Fragenprüfung, 22 gezielte
  Perfect-Tests sowie alle 121 Projekttests bestanden. Die Tests belegen auch,
  dass Perfect keinen Chat und keine iKühe mehr ausgibt und der frühere
  Chat-Endpunkt HTTP 404 liefert.
- `stormseeds-perfect.css?v=20` wird öffentlich mit HTTP 200 und bytegleichem
  SHA-256 ausgeliefert. Der öffentliche Health-Endpunkt meldete bei der Prüfung
  weiterhin Release `2026.10.22-perfect-eight-player-v1`. Der erforderliche
  kontrollierte Neustart auf
  `2026.10.23-perfect-points-no-chat-v1` scheiterte, weil `sudo` ein Passwort
  verlangt. Die authentifizierte sichtbare Abnahme der Perfect-Lobby steht
  daher ebenfalls aus. Live-Status nach der verbindlichen Definition: nicht
  getan.

## Einheitlicher Rückweg zu tabletop connection (23.10.2026)

- Die Lobbyübersichten von Stormseed´s Perfect und dem Standard-Kartentisch
  besitzen unten nun denselben Rücklink auf die gemeinsame Auswahl `/karten`.
  Der Kartentisch führt damit nicht mehr fälschlich zur Guesstimate-Hauptseite.
- Die bereits gemeinsam verwendete Würfelspiel-Lobby für Würfeltisch, Kniffel
  und Mäxchen wurde auf dieselbe verbindliche Beschriftung vereinheitlicht.
  Der sichtbare Text lautet in allen Fällen exakt kleingeschrieben
  `zurück zu tabletop connection`.
- 59 gezielte Mehrspielertests, die verbindliche Fragenprüfung und alle 121
  Projekttests bestanden. Es handelt sich ausschließlich um automatisch neu
  geladene Vorlagen; ein Dienstneustart ist dafür nicht erforderlich. Eine
  authentifizierte öffentliche Sichtprüfung nach dem Neuladen steht noch aus.

## Sammelseiten für Würfel- und Kartentische (23.10.2026)

- Die Tabletop-Connection-Auswahl auf vier Kacheln verdichtet: Stormseed´s
  Perfect, `Zu den Kartentischen`, `Zu den Würfeltischen` und das weiterhin
  angekündigte Risiko. Die bisherigen einzelnen Kacheln für Würfeltisch,
  Kniffel, Mäxchen und Schweinchen stehen dort nicht mehr direkt.
- Eine gemeinsame, nicht duplizierte Sammelseiten-Komponente ergänzt. Die
  Würfeltischseite verwendet den vorhandenen großen Würfeltisch-Hintergrund
  und zeigt Würfeltisch, Kniffel, Mäxchen sowie das angekündigte Schweinchen.
  Die Kartentischseite enthält zunächst `Freies Spiel mit allen
  Standardkarten` und führt in die vorhandene Kartentisch-Lobby. Beide Seiten
  besitzen unten den kleingeschriebenen Rücklink `zurück zu tabletop
  connection`.
- Für die Kartentischseite einen neuen leeren, rechteckigen Kartentisch im
  warmen Clubzimmer als `static/card-tables-background-v1.png` erzeugt. Die
  Oberfläche enthält bewusst keine fest eingebrannten Karten, Würfel, Texte
  oder Bedienelemente, damit die dynamischen Spielkacheln darauf liegen.
- Python-Syntaxprüfung, verbindliche Fragenprüfung, 39 gezielte
  Tabletop-Tests und alle nun 123 Projekttests bestanden. Hintergrund und
  `card-table.css?v=13` werden öffentlich mit HTTP 200 und bytegleichen
  SHA-256-Prüfsummen ausgeliefert.
- Der notwendige Neustart von `guesstimate.service` wurde von systemd mit
  `Access denied` verweigert; der zusätzliche Versuch über `sudo` verlangt
  ein nicht verfügbares Passwort. Der öffentliche Health-Endpunkt meldet daher
  weiterhin Release `2026.10.23-perfect-points-no-chat-v1`; beide neuen
  Sammelseiten antworten öffentlich noch mit HTTP 404. Eine authentifizierte
  sichtbare Live-Abnahme ist dadurch nicht möglich. Live-Status nach der
  verbindlichen Definition: nicht getan.

## DiceyTable-Prototyp Stormseed´s Conquest (23.10.2026)

- Für den geplanten Risiko-artigen 3D-Spieltisch wurde das öffentliche
  Repository `dabrain1982-cyber/stormseed-s-diceytable` mit DiceyTable
  verbunden. Das Spielprojekt trägt vorläufig den Namen
  `Stormseed’s Conquest` und bleibt technisch vom laufenden
  Guesstimate-Dienst getrennt.
- Den vom Nutzer aus DiceyTable exportierten, dort als gültig ausgewiesenen
  Entwurf ausgewertet. Er enthält das Manifest, die Szene mit zehn privaten
  Spielerzonen, den eingebauten Raum und Tisch sowie ein minimales Skript.
- Im Repository den Arbeitszweig `wip` angelegt und die drei
  DiceyTable-Einstiegsdateien `diceytable.mod.json`, `setup.json` und
  `scripts/main.js` eingecheckt. Der lediglich zur Initialisierung verwendete
  Testwürfel samt nicht mitexportierter Preset-Assets wurde entfernt. Der
  Arbeitszweig ist noch nicht nach `main` veröffentlicht und noch nicht in
  DiceyTable spielgetestet.
- Die zunächst besprochenen Varianten sind keine getrennten Spiele und keine
  abweichenden Weltkarten. Ein gemeinsamer Satz realer geografischer Gebiete,
  Namen, Nachbarschaften und Regeln bildet den Spielinhalt. Brettdarstellung,
  Figuren, Karten und Würfel werden als vier voneinander unabhängige
  Skin-Kategorien umgesetzt und sollen frei kombinierbar sein.
- Vorgesehene Figurenrichtungen sind mindestens klassisch-alt, modern-bunt mit
  abgerundeter Formensprache und Fantasy. Fantasy-Figuren bleiben ein frei
  wählbarer Figurenskin auf dem normalen Weltbrett; eine eigene Fantasy-Karte
  oder abweichende Fantasy-Regeln sind derzeit nicht beschlossen. Eine
  eigenständige Guesstimate-Variante ist als spätere Idee vorgemerkt.
- Der Nutzer hat ausdrücklich festgelegt, dass marken- oder designrechtlich
  problematische Bestandteile entfallen. Insbesondere werden keine fremden
  Logos, Markennamen, Originalkartengrafiken, lizenzierten Figurenwelten oder
  exakt nachgebildeten Originalspielfiguren verwendet. Geografie und
  Spielinhalte erhalten eine eigenständige Gestaltung und Benennung.
- Auf `wip` mit Commit `97327b4` einen reproduzierbaren Grafikstand
  veröffentlicht: drei eigenständige Weltbretter (`klassisch`, `taktisch`,
  `farbenfroh`), pro Stil ein vollständiges Deck aus 42 Länderkarten und ein
  vollständiges Deck aus 12 Missionskarten samt Rückseiten und DiceyTable-
  Kartenbögen. Das gemeinsame Datenmodell enthält genau 42 eindeutige Länder,
  die Kontinentverteilung 9/4/7/6/12/4 und 83 gegenseitig bestätigte
  Nachbarschaften.
- Die Brettgeometrie wird aus gemeinfreien Natural-Earth-Daten und eigenen
  Zuordnungen erzeugt; Gestaltung, Kartenaufbau und Symbole sind neu erstellt.
  Das Manifest enthält nun Kurzbeschreibung, quadratisches Cover und ein
  16:9-Vorschaubild, wodurch die zuvor gemeldeten drei Publishing-Warnungen
  inhaltlich abgedeckt sind. Alle JSON-Dateien, Assetverweise, Bildmaße und
  Deckgrößen wurden lokal geprüft.
- Mit Commit `b2c44cb` außerdem eine physische Startszene vorbereitet: ein
  gesperrtes klassisches Brett als natives `board`, die 42 Länder- und 12
  Missionskarten als native physikalische `deck`-Objekte sowie drei rote
  Angriffs- und zwei dunkle Verteidigungswürfel auf Basis von DiceyTables
  vorhandenem D6-Preset. Ein Werkzeug kann dieselbe Startszene auch mit dem
  taktischen oder farbenfrohen Brett-/Kartenstil zusammensetzen.
- Die neue Szene ist noch nicht im DiceyTable-Browser geladen und sichtbar
  spielgetestet. Die freie, voneinander unabhängige Skin-Auswahl und die
  Figurenmodelle fehlen ebenfalls noch. Live-/Spielstatus daher weiterhin:
  nicht getan.
- Nach der DiceyTable-Synchronisationsansicht festgestellt, dass der dortige
  Entwurf ausschließlich `main` einliest. Den unveränderten und zuvor
  geprüften Stand `b2c44cb` deshalb per Fast-Forward von `wip` nach `main`
  übernommen; beide entfernten Zweige zeigen nachweislich auf denselben
  Commit. Dies veröffentlicht die Repository-Dateien, registriert das Spiel
  aber noch nicht als spielbaren DiceyTable-Mod. Die anschließende
  Browser-Synchronisation und sichtbare Szenenprüfung stehen weiterhin aus.

## Dauerhafter Zugang zu Daily-Nachholrunden (23.10.2026)

- Die Nachholabfrage nach der Anmeldung bleibt erhalten, ist aber nicht mehr
  der einzige Zugang. Solange frühere Tage der laufenden Woche ungespielt
  sind, zeigt die Guesstimate-Startseite nun dauerhaft einen zweiten Knopf mit
  der tatsächlichen Zahl der verpassten Runden. Das gilt auch nach Schließen
  des Begrüßungsdialogs und nach der Wahl `Lieber nur heute spielen`.
- Die fehlenden Wochentage werden bei jedem Startseitenaufruf neu aus den
  abgeschlossenen Daily-Runden ermittelt. Ein veralteter Sitzungswert ist
  damit nicht mehr maßgeblich. Eine erledigte oder aus einer früheren Woche
  stammende aktive Nachholrunde wird beim Rückweg zur Startseite verworfen;
  noch offene Runden werden weiterhin nacheinander gespielt.
- Der Login-Dialog benennt statt des unklaren `Ja` jetzt ausdrücklich Anzahl
  und Aktion. Ein neuer Ablaufstest deckt den einmaligen Dialog, den
  dauerhaften Knopf, die spätere Rückkehr nach `nur heute` und die vollständige
  Warteschlange Montag bis Mittwoch ab.
- `deploy/validate_question_library.py` war erfolgreich; alle nun 124
  Projekttests bestanden. `quiz-arena.css?v=67` wurde öffentlich mit HTTP 200
  und bytegleicher SHA-256-Prüfsumme ausgeliefert. Der Dienst blieb stabil mit
  `NRestarts=0`.
- Der erforderliche kontrollierte Neustart von `guesstimate.service` wurde
  sowohl normal als auch mit angeforderten Rechten durch systemd mit
  `Access denied` abgewiesen. Der öffentliche Health-Endpunkt meldet deshalb
  weiterhin Release `2026.10.23-tabletop-family-hubs-v1`; die neue
  serverseitige Ermittlung und Release-Kennung sind noch nicht aktiv. Eine
  authentifizierte sichtbare Produktionsabnahme ist damit ebenfalls offen.
  Live-Status nach der verbindlichen Definition: nicht getan.

## Conquest-HD-Render – Serverneustart und Sicherheitskorrektur (23.10.2026)

- Beim Versuch, drei neue 4096×2560-Brettgrafiken aus 1:10m-Natural-Earth-
  Vektordaten zu erzeugen, wurden gleichzeitig 42 vollständige Graustufenmasken
  sowie weitere Vollbild-Zwischenebenen im Arbeitsspeicher gehalten. Dieser
  Auftrag wurde entgegen der vereinbarten Vorgehensweise direkt auf dem
  Live-Server und ohne vorherigen kleinen Speicher-/Einzelbildtest gestartet.
- Während dieses Renderlaufs startete der gesamte Server neu. Nach dem Boot war
  die Systemlaufzeit erst sechs Minuten; `guesstimate.service` war seit
  19:19:54 Uhr wieder aktiv. Ein Kernel-OOM-Eintrag konnte mangels Leserechten
  auf das vorherige Bootjournal nicht eingesehen werden. Der zeitliche
  Zusammenhang und das speicherintensive Renderverfahren belegen die
  wahrscheinlichste Ursache, werden aber nicht fälschlich als direkt gelesene
  OOM-Meldung bezeichnet.
- Der Renderprozess ist beendet und keine der vorgesehenen `*-hd.webp`-Dateien
  wurde geschrieben. Die drei bisherigen Bretter blieben unverändert. Lokal
  und öffentlich antwortete `/guesstimate/health` nach dem Neustart wieder mit
  HTTP 200 und `status: ok`.
- Verbindliche Folgerung: Auf dem Live-Server keine weiteren hochauflösenden
  Mehrfachrender oder speicherintensiven Bildoperationen. Künftige
  Brettverbesserungen werden einzeln, in begrenzter Auflösung und mit
  beobachteter Speichernutzung außerhalb des laufenden Dienstes vorbereitet;
  erst die geprüfte fertige Datei wird in einem kleinen Schritt eingebunden.
