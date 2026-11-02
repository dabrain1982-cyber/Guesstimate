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

## Sicherung vor lokaler Weiterarbeit (23.10.2026)

- Den vollständigen nicht ignorierten Projektstand einschließlich Quellcode,
  Fragen, Dokumentation und Bildassets im separaten Git-Zweig
  `codex/server-snapshot-2026-10-23` gesichert. Laufzeitdaten, Konfigurationen,
  Datenbanken und Umgebungsdateien bleiben durch `.gitignore` ausgeschlossen.
- Nach dem Serverneustart zehn beschädigte beziehungsweise unreferenzierte
  Git-Objektdateien festgestellt. Die defekten Dateien wurden in einen
  temporären Sicherungsordner verschoben; sieben referenzierte Objekte wurden
  bytegenau aus den unveränderten Projektdateien neu erzeugt. Anschließend lief
  `git fsck --full --no-dangling` ohne Befund durch.
- Der Snapshot-Commit `b475dae` wurde erfolgreich zu GitHub übertragen. Der
  nächste vorgesehene Schritt ist ein lokales Codex-Projekt auf dem PC, das
  diesen Zweig auscheckt. Rechenintensive Grafikarbeiten sollen dort und nicht
  mehr im Live-Serverordner ausgeführt werden.

## Lokale Fortsetzung des Conquest-HD-Renders (23.10.2026)

- Den Zweig `codex/server-snapshot-2026-10-23` im lokalen Windows-Arbeitsordner
  `D:\Guesstimate` ausgecheckt. Der Checkout folgt dem gleichnamigen
  GitHub-Zweig; der Arbeitsbaum war vor Beginn unverändert und `git fsck
  --full --no-dangling` lief ohne Befund.
- Das HD-Renderwerkzeug so umgestellt, dass pro Prozess zwingend genau ein
  Brettstil erzeugt wird. Die 42 Gebietszuweisungen bleiben nur noch in der
  verkleinerten Arbeitsauflösung im Speicher und werden einzeln für Farbe und
  Grenzlinie hochskaliert. Der frühere automatische Dreifachrender sowie 42
  gleichzeitig gehaltene Vollauflösungsmasken entfallen.
- Die Schriftauswahl funktioniert nun sowohl mit lokalen Linux- als auch mit
  Windows-Schriften. Der gemeinfreie Natural-Earth-Datensatz liegt nur als von
  Git ausgeschlossene lokale Renderquelle unter `runtime/natural-earth/`.
- Einen einzelnen klassischen 4096-x-2560-Proberender ausschließlich lokal
  nach `offline-preview/conquest-hd-local-test/welt-klassisch-hd.webp`
  ausgeführt. Er endete erfolgreich nach 200,1 Sekunden bei gemessenen 389,4
  MiB Spitzenspeicher; die WebP-Datei ist 993.078 Byte groß und wurde visuell
  als vollständiges Brett geprüft. Keine aktive Brettdatei und kein
  Live-Serverbestand wurden verändert; die beiden weiteren Stile sind noch
  nicht gerendert.
- Die lokale Fragenbibliotheksprüfung, die drei gezielten Conquest-Tests und
  anschließend alle 128 Projekttests bestanden. Unter Windows benötigen die
  Tests einen beschreibbaren projektlokalen Temporärordner sowie UTF-8-Modus;
  die zunächst beobachteten Fehler waren ausschließlich gesperrte
  System-Temp-Pfade beziehungsweise die Windows-Standardcodierung und ließen
  sich unter diesen lokalen Testbedingungen nicht reproduzieren.

## Stormseed’s Conquest – ein verbindliches handgemaltes Brett (23.10.2026)

- Der Nutzer hat die bisherige Pixel-/Vektorgrafik ausdrücklich verworfen und
  die frühere Mehrfachstilplanung vereinfacht: Zunächst wird genau ein schönes
  Weltbrett verwendet. Maßgeblich sind die bekannte Aufteilung in 42 Gebiete
  und die warme, hochwertige Materialwirkung der vorhandenen Tabletop-,
  Karten- und Würfeltischkulissen. Das Spiel ist für den privaten Freundeskreis
  bestimmt; die aktuelle Anweisung ersetzt für dieses Brett die frühere
  allgemein formulierte Zurückhaltung gegenüber der gezeigten Aufteilung.
- Ein neues, eigenständiges handgemaltes Brett mit detaillierter
  Aquarellkartografie, Holz-/Messingrahmen, sechs farbigen Kontinenten,
  Landschaftstexturen, Schiffen und Kompass als
  `static/conquest/boards/welt-conquest-v1.png` eingebunden. Die Bilddatei
  enthält bewusst keine fest eingebrannten Beschriftungen, Spielsteine,
  Karten oder Bedienoberfläche.
- Die drei bisherigen Brettstilknöpfe aus der laufenden Spielansicht entfernt;
  auch in der Lobby ist das Brett nicht mehr auswählbar. Historische
  Brettdateien bleiben unangetastet, werden aber von der Spielansicht nicht
  mehr geladen. Karten-, Figuren- und Würfelstile bleiben weiterhin getrennt
  wählbar.
- Titel, alle 42 korrekten deutschen Gebietsnamen und die Truppenzähler liegen
  als dynamische Ebene über dem Brett. Für die stilisierte neue Geometrie sind
  eigene, stabile Brettpositionen hinterlegt; Karten und spätere
  Figuren-/Steingrafiken können dadurch unabhängig vom Hintergrund ausgetauscht
  und bewegt werden.

## Gezielte Karten- und Lesbarkeitskorrekturen (23.10.2026)

- Das handgemalte Brett lokal als `welt-conquest-v3.png` fortgeschrieben. Peru
  besitzt nun eine klar geschlossene Landesgrenze zu Brasilien und Argentinien.
  Die falsche lange Angriffsverbindung von Ostafrika Richtung Indien wurde
  durch die kurze Verbindung zum Nahen Osten ersetzt; die sachfremde Linie von
  Indonesien Richtung Südpol wurde vollständig entfernt.
- Eine falsche Linie zum dekorativen Schiff links wurde entfernt. Die gültige
  Übersee-Verbindung Brasilien–Nordafrika beginnt und endet jetzt eindeutig an
  den beiden Ländern und berührt kein Schiff.
- Die dynamischen Beschriftungen für Großbritannien, Naher Osten und Indonesien
  erhalten feste Sonderpositionen und liegen bewusst über den übrigen
  Brettmarkierungen, damit sie auch in der geneigten Spielansicht lesbar
  bleiben.
- Die sechs zuvor fehlenden Kontinent-Bonusfenster werden wieder dynamisch auf
  dem Brett angezeigt: Nordamerika +5, Südamerika +2, Europa +5, Afrika +3,
  Asien +7 und Australien +2. Bildbearbeitung und Einbindung erfolgten nur im
  lokalen Arbeitsordner; der Live-Server wurde nicht verwendet.

## Regelgebundene Wasser-Angriffsverbindungen (23.10.2026)

- Die gestrichelten Linien sind keine Dekoration, sondern verbindliche
  Angriffswege. Deshalb enthält `welt-conquest-v4.png` keine festgemalten
  gestrichelten Linien mehr; alle soliden Landesgrenzen und die Peru-Korrektur
  bleiben unverändert erhalten.
- Die Wasserverbindungen werden nun ausschließlich aus `seaConnections` in
  `static/conquest/world.json` gezeichnet. Jede Verbindung wird vor dem Rendern
  gegen die beidseitige Nachbarschaft der beiden Gebiete geprüft. Dadurch sind
  Schiffe und der Südpol keine möglichen Endpunkte und Bildbearbeitung kann
  weder zusätzliche Angriffswege erfinden noch gültige Regeln verändern.
- Die Alaska–Kamtschatka-Verbindung wird korrekt an beiden Kartenrändern
  fortgesetzt. Alle übrigen Linien enden unter den zugehörigen dynamischen
  Gebietsmarken; die Darstellung bleibt damit von der Hintergrundgrafik
  getrennt und überprüfbar.

## Neue Kartenillustration unmittelbar aus der Spielskizze (23.10.2026)

- Auf ausdrückliche Anweisung eine neue Kartenillustration ausschließlich aus
  der bereitgestellten schwarz-weißen Spielskizze erzeugt; frühere generierte
  Karten wurden dabei nicht als Bildreferenz verwendet.
- Die neue, noch nicht in den Spieltisch eingebaute Fassung liegt unter
  `static/conquest/boards/welt-conquest-skizze-v1.png`. Der frühere RISK-Block
  wurde durch den Titel „Stormseed’s Conquest“ ersetzt. Vor einer Einbindung
  ist weiterhin eine sichtbare Abnahme durch den Nutzer erforderlich.

## Conquest – ausschließlich lokale Kupferfläche und Inventar (23.10.2026)

- Der Nutzer hat ausdrücklich festgelegt, dass ausschließlich offline im
  Windows-Arbeitsordner `D:\Guesstimate` gearbeitet wird. Keine Übertragung
  zum Live-Server, keine dortige Dateiänderung und kein Produktionsneustart
  wurden in diesem Arbeitsschritt ausgeführt.
- Zwei neue farbige Bildgenerierungen wichen erneut von der gelieferten Skizze
  ab, insbesondere bei Ukraine/Skandinavien und den afrikanischen Grenzen.
  Beide Fassungen wurden nicht eingebunden. Weitere komplette generative
  Neuzeichnungen der Karte wurden gestoppt.
- Stattdessen die Originalskizze unverändert unter
  `static/conquest/boards/welt-konturen-original-v1.png` übernommen. Ihre
  SHA-256-Prüfsumme ist identisch mit der Nutzerdatei:
  `9d10783b0366f9dcabc7ec07a062053dc9faf6ffc7769c53e40946462f6d3a42`.
  Damit werden keine neu erfundenen Kamtschatka-Linien oder veränderten
  Ländergrenzen der Farbgenerierungen übernommen. Der Bestand bleibt eine
  papierfarbene Originalkonturen-Fassung, keine fertige neue Farbillustration.
- Titel `stormseed´s conquest` und die sechs Kontinentboni werden von genau
  einer gemeinsamen Komponente `_conquest_board_surface.html` dargestellt.
  Spielansicht und lokale flache Bildvorschau verwenden dieselbe Komponente.
  Die sichtbare Gebietsbezeichnung lautet wie in der Vorlage Ukraine; die
  bestehende interne ID `russland` bleibt unverändert.
- Die Kartenoberfläche ist perspektivisch direkt in die Kupfereinfassung der
  vorhandenen Tischkulisse eingepasst. Der zusätzliche Holzunterbau, seine
  Schatten/Volumen, die frei ziehbaren Karten und der separate Würfelbereich
  wurden aus der Conquest-Ansicht entfernt. Draufsicht, Tischansicht,
  Verschieben und Zoom verwenden dieselbe Oberfläche und Gebietsmarken.
- Das persönliche Inventar liest ausschließlich die eigenen gespeicherten
  Länderkarten und die eigene zugeteilte Mission. Die Startverteilung hinterlässt
  keine Länderkarten. Missionen gegen nicht mitspielende Armeefarben werden
  vor der neuen Vergabe herausgefiltert; vorhandene echte Spielstände wurden
  nicht umgeschrieben. Die Statusanzeige wird regelmäßig lesend aktualisiert.
- Die offizielle Kartenregel recherchiert und im Regelunterbau festgehalten:
  genau eine zufällige Länderkarte am Ende eines Zuges mit mindestens einer
  Eroberung, keine zusätzliche Karte pro weiterem eroberten Land. Die
  Startaufstellungskarten werden wieder eingesammelt; geheime Missionen
  gehören nur im entsprechenden Modus in das eigene Inventar.
- Wichtige offene Grenze: Die eigentlichen Zugaktionen, Eroberung, Zugende,
  automatischer Kartengewinn und Kartentausch fehlen weiterhin. Die
  Inventaranzeige allein ist kein Nachweis eines spielbaren Eroberungsablaufs.
- Fragenbibliotheksprüfung erfolgreich, 131 Projekttests bestanden. Nach der
  zusätzlichen Missionsfilterung die sechs Conquest-Tests erneut erfolgreich
  ausgeführt; JavaScript-Syntax und `git diff --check` ebenfalls erfolgreich.
- Die getrennte PC-Vorschau auf `127.0.0.1:54506` im verbundenen Chrome
  tatsächlich geöffnet. Originalgrenzen in Draufsicht, direkte Kupferpassung,
  42 Truppenmarken sowie Öffnen und Schließen des privaten Inventars mit
  echter zugeteilter Mission geprüft. Prüfbilder und flache Brettansicht
  liegen unter `offline-preview/conquest-kupfer-v1/`. Kein öffentlicher
  Live-Status wird aus dieser lokalen Abnahme abgeleitet.

## Farbige Conquest-Vorlage – gezielte Bildkorrektur (23.10.2026)

- Nach Nutzerbeanstandung der ersatzweise eingebauten beigefarbenen
  Skizzenfassung die vom Nutzer erneut gezeigte farbige Karte gezielt
  weiterbearbeitet. Die beige Fassung ersetzt nicht die gewünschte farbige
  Gestaltung.
- Ostkanada ergänzt; Skandinavien auf der Halbinsel und Ukraine auf dem
  östlichen blauen Festland beschriftet; die zusätzliche obere Verbindung am
  rechten Asienrand entfernt; Nordafrika und Zentralafrika durch eine
  durchgehende Grenze getrennt; die lange gestrichelte Linie im Roten Meer
  entfernt und durch eine kurze Ostafrika–Naher-Osten-Verbindung ersetzt.
- Die fertige Bilddatei nach Sichtprüfung ausschließlich unter
  `offline-preview/conquest-farbkorrektur-v1/stormseeds-conquest-korrigiert-v1.png`
  gespeichert. Der zugehörige Bearbeitungsauftrag liegt daneben als Textdatei.
  Es handelt sich um eine lokale Prüffassung; eine Nutzerabnahme wird nicht
  vorweggenommen.
- In diesem Schritt keine Anwendungsdateien oder aktive Bildverweise
  verändert, keine Serververbindung aufgebaut und keine Veröffentlichung
  ausgeführt. Die lokale Spielansicht verwendet bis zu einer späteren
  gezielten Einbindung weiterhin ihren zuvor gespeicherten Stand.

## Conquest – sichtbare Filzkeile lokal beseitigt (23.10.2026)

- Der vom Nutzer gezeigte rechte Filzstreifen widerlegte die frühere
  Behauptung einer vollständigen Kupferpassung. Die bisherige Projektion
  endete seitlich zu weit innen; die Tischöffnung besitzt außerdem acht
  Eckpunkte einschließlich der abgeschrägten Ecken.
- Die Kartenebene in `static/conquest-table.js` bis hinter die Innenkanten
  erweitert und über eine gemeinsame achteckige Öffnung beschnitten.
  `templates/conquest_table.html` enthält die zugehörige Hülle;
  `static/conquest-table.css` deren Positionierung. In der Draufsicht
  wird die Beschneidung aufgehoben. CSS-/JS-Verweise auf Version 5 erhöht.
- Rechnerische Gegenprüfung am unveränderten Hintergrund: 553.336 als
  grüner Filz erkannte Bildpunkte innerhalb der Tischöffnung untersucht,
  keiner davon außerhalb der neuen Abdeckung. Zusätzlich die tatsächliche
  lokale Browseransicht bei 1920 × 1080 geprüft: kein sichtbarer Filzkeil
  an der beanstandeten rechten Kante oder den übrigen Tischkanten;
  Draufsicht weiterhin vollständig. Temporäre Browsergrößenvorgabe danach
  zurückgesetzt. Prüfbilder:
  `offline-preview/conquest-kupfer-passung-v2/tischansicht.jpg` und
  `offline-preview/conquest-kupfer-passung-v2/rechte-kante.jpg`.
- Nur die lokale Passung geändert. Die farbige Kartenfassung bleibt eine
  nicht abgenommene Prüffassung; insbesondere sind die vom Nutzer genannten
  Verbindungen Ostafrika–Madagaskar und Ostafrika–Naher Osten nicht als
  korrekt erledigt nachgewiesen. Keine Serververbindung, Veröffentlichung
  oder Änderung am laufenden Dienst.

## Daily Quiz – Startseite bei Fragenmangel und Mailwarnung (24.10.2026)

- Öffentlich beobachteter Ausgangsstand: Der laufende Dienst liefert Release
  `2026.10.23-daily-catchup-access-v1`; die angemeldete Hauptseite wird bei
  fehlender neuer Tagesrunde durch `pool_exhausted.html` und HTTP 503 ersetzt.
  Der Nutzer hat ausdrücklich festgelegt, dass die normale Hauptseite erhalten
  bleibt und ausschließlich der nicht verfügbare Spielknopf ausgegraut wird.
- Aktueller Live-Pool vor Aktivierung der Korrektur: 11 Wahr/Falsch,
  1 Auswahl, 0 Paare, 0 Reihenfolgen, 1 Schätzung; keine neue vollständige
  Runde. `pool_mail_ready: true` belegt lediglich vorhandene Konfiguration,
  keinen erfolgreichen SMTP-Versand. Die geschützte Live-Datenbank und
  Maildatei sind für das Arbeitskonto `igroup` nicht lesbar; die Anzahl
  tatsächlich abgeschlossener Runden und der aktuelle Benachrichtigungseintrag
  sind deshalb zu diesem Zeitpunkt nicht verifiziert.
- Die Hauptseitenroute rendert nun in allen Fällen dieselbe `home.html` mit
  Profilfenster, Karussell und Rangliste. Ohne reservierten Fragensatz ist nur
  `spielen` deaktiviert und grau. Bereits reservierte Tagesrunden bleiben
  start-/fortsetzbar und fertige Ergebnisse erreichbar. Nachholzugänge lassen
  bei leerem Vorrat nur bereits reservierte Tage zu. Alte direkte Rundenaufrufe
  kehren bei Fragenmangel zur Hauptseite zurück, statt einen Serverfehler
  auszulösen. Die neue CSS-Regel steht an der zuständigen Aktionskomponente.
- Die bisherige Mailwarnung besitzt nur einen dauerhaften `sent_at`-Wert und
  wurde nach Nachschub nicht erneut scharfgeschaltet. Erfolgreiche neue
  Reservierungen setzen nun ausschließlich diese Benachrichtigungsmetadaten
  zurück. Versandfehler bleiben ungesendet und werden protokolliert; weitere
  Hauptseitenaufrufe bei leerem Pool versuchen eine noch offene Warnung erneut.
  Die Mail nennt die verbliebenen Fragen je Frageart. Ein für fünf Partyrunden
  zu kleiner, aber nicht leerer Vorrat löst keine falsche Leerstandsmail aus.
- Neues Wartungswerkzeug `deploy/report_question_pool.py`: Standardbetrieb
  liest ausschließlich über eine SQLite-Verbindung mit `mode=ro` aggregierte
  Rundenzähler, Reservierungen, Perfect-Zyklusbestände und den Versandvermerk.
  Nur `--notify` verwendet den normalen SMTP-Absender; `--resend` erlaubt
  ausdrücklich einen erneuten Versand. Zugangsdaten werden nicht ausgegeben.
  Der Anwendungsimport wird dabei zunächst mit einer isolierten temporären
  Datenbank ausgeführt, damit keine Startmigration an der Live-Datenbank läuft.
- `deploy/activate_pool_fix.sh` ist für den einmaligen administrativen
  Aktivierungsschritt vorbereitet: Fragenprüfung, kontrollierter Neustart,
  Healthcheck, aggregierter Bericht und erneuter Versandversuch als
  Dienstkonto `guesstimate`. Der Bericht wird ohne Geheimnisse unter
  `deploy/pool-fix-result.log` abgelegt. Spielergebnisse, Konten, Antworten und
  Fragen-Nutzungshistorie werden durch das Werkzeug nicht verändert.
- Prüfung: Fragenbibliothek erfolgreich; alle 135 lokalen Projekttests
  bestanden. Nach Übertragung der sieben gezielt betroffenen Dateien außerdem
  alle 65 Quiztests in einer isolierten Server-Prüfdatenbank bestanden;
  Shellsyntax und `git diff --check` ohne Fehler. Nur die sieben geprüften
  Dateien wurden übertragen; lokale Conquest-Arbeiten bleiben auf dem PC.
- Die isolierte PC-Vorschau unter `127.0.0.1:54507` wurde tatsächlich im
  Browser geöffnet: vollständige normale Startseite, grauer gesperrter
  Spielknopf, bedienbares Karussell und funktionierender Ranglistenwechsel.
  Prüfbild lokal: `runtime/pool-fix/startseite-leerer-pool.png`.
- Offener Aktivierungsschritt: `sudo` verlangt das dem Arbeitskonto nicht
  verfügbare Administratorkennwort. Der Nutzer wurde um Ausführung von
  `sudo bash /srv/guesstimate/deploy/activate_pool_fix.sh` gebeten.
  Produktionsneustart, tatsächliche Mailannahme und authentifizierte sichtbare
  Live-Funktionsprüfung stehen noch aus. Live-Status: **nicht getan**.

## 50 Wahr/Falsch-Fragen lokal vorgemerkt; Live-Update zurückgestellt (24.10.2026)

- Auf ausdrücklichen Nutzerwunsch das gemeinsame Live-Update zurückgestellt,
  bis die weiteren Fragenpakete vorbereitet sind. Zunächst ausschließlich
  50 spannende Wahr-oder-falsch-Fragen recherchiert und lokal unter
  `D:\Guesstimate\fragen\vormerkungen\2026-10-24-wahr-falsch-50\`
  vorgemerkt. Das Fragenpaket wurde nicht zum Live-Server übertragen und
  gehört nicht zum aktiven Manifest.
- `kandidaten.json` enthält genau 50 steckbriefkonforme Einträge mit
  27 wahren und 23 falschen Aussagen, kurzen Auflösungen und insgesamt
  58 Quellenreferenzen. `LESELISTE.md` zeigt alle Karten lesbar mit Quellen;
  `RECHERCHE.json` dokumentiert Belegprüfung und Prüfsummen;
  `PRUEFBERICHT.md` hält Dublettenentscheidungen und offene Grenzen fest.
- Die Fakten tatsächlich in institutionellen Veröffentlichungen, Fachquellen
  beziehungsweise Originalstudien recherchiert und für das Quiz eigenständig
  formuliert. Keine Religionsfrage und keine Frage über eine einzelne Person
  in den neuen Kandidaten. Einzelne technisch gesperrte Direktaufrufe wurden
  anhand tatsächlich ausgelesener Originalseiteninhalte im Suchindex geprüft;
  zusätzliche zugängliche Belege sind, wo erforderlich, mitgeführt.
- Gegen alle 1.403 Daily-Bestandseinträge einschließlich der 60 vorbereiteten
  Zwei-Gruppen-Fragen geprüft. Die bereits vorhandenen Kerne Dosenöffner/
  Konservendose (`tf186`) und Fax vor Telefon (`tf187`) wurden als Dubletten
  ausgeschlossen und ersetzt. Auch Kandidaten zur Pinguinverbreitung und zur
  Voyager-Schallplatte wegen zu starker Bestandsnähe nicht übernommen.
- Die IDs `tf700` bis `tf749` sind vorläufige Vorschläge und in den aktuellen
  Fragendateien frei. Vor einer späteren Aktivierung ist die historische
  Live-Nutzung in `question_usage` zusätzlich zu prüfen. Kein vorhandener
  Eintrag, keine bestehende ID und keine Nutzungshistorie wurden verändert.
- Aktueller Altbestandsbefund: `tf18` verneint korrekt wildlebende Pinguine am
  Nordpol, behauptet in der Erklärung aber unzutreffend eine ausschließlich
  südliche Verbreitung. Galápagos Conservancy belegt Vorkommen knapp nördlich
  des Äquators. Der Eintrag wurde in diesem Auftrag nicht verändert;
  eine spätere redaktionelle Korrektur ist offen.
- Prüfungen: Bibliotheksprüfung für den unveränderten aktiven Bestand
  erfolgreich; dieselbe verbindliche Prüfung außerdem für eine isolierte
  Bibliothekskopie mit den 50 Kandidaten erfolgreich. Alle aktiven
  Fragendateien bytegenau unverändert und kein Kandidat vom aktuellen
  Fragenlader eingelesen. Keine Aktivierung und kein Neustart ausgeführt.
- Die Zahl tatsächlich gespielter Runden bleibt offen. Für `igroup` ist die
  Live-Datenbank weiterhin nicht lesbar. Der Nutzer erhielt einen gesonderten
  rein lesenden Administrationsbefehl für `deploy/report_question_pool.py`,
  der weder neu startet noch eine Mail sendet. Der öffentliche Dienst meldet
  unverändert Release `2026.10.23-daily-catchup-access-v1` und 0 neue
  vollständige Runden. Startseiten-/Mailkorrektur weiterhin vorbereitet;
  vollständige Live-Aktivierung und SMTP-Nachweis stehen aus.

### 24.10.2026 – 50 Multiple-Choice-Fragen lokal vorgemerkt

- Auf Nutzerwunsch weitere 50 recherchierte Auswahlfragen mit jeweils vier
  Antworten, eindeutiger Lösung, Erklärung und insgesamt 60 Quellenverweisen
  vorbereitet. Ablage ausschließlich lokal:
  `fragen/vormerkungen/2026-10-24-multiple-choice-50/` mit
  `kandidaten.json`, `LESELISTE.md`, `RECHERCHE.json` und
  `PRUEFBERICHT.md`.
- Wortlaut selbst formuliert und Sachverhalte tatsächlich recherchiert.
  Belege überwiegend von Institutionen, Museen, Hochschulen,
  Forschungsstellen und zuständigen Sportverbänden. Technische Sperren
  einzelner Direktabrufe und die Prüfung über Originalseiteninhalte im
  Suchindex sind pro Karte dokumentiert.
- Abgleich gegen sämtliche 1.403 Daily-Einträge einschließlich der
  vorbereiteten Zwei-Gruppen-Fragen und zusätzlich gegen die 50 bereits
  vorgemerkten Wahr/Falsch-Fragen: 1.453 Vergleichseinträge. Optionen,
  Zuordnungen, Erklärungen und Metadaten einbezogen; Ähnlichkeitshinweise
  nach Wissenskern redaktionell geprüft. Keine Dublette festgestellt.
- Religion ausgeschlossen. Kein weiterer Schwerpunkt auf bereits häufig
  vertretenen Personen. Warren Robinett und Delia Derbyshire kommen im
  Vergleichsbestand nicht vor und werden jeweils einmal erwähnt.
- Bei der Biberfrage die verbreitete Erklärung der Zahnfarbe durch Eisen
  anhand neuerer Max-Planck-/ACS-Forschung verworfen. Der Kandidat fragt
  stattdessen die belegte Schutzfunktion eisenreichen Zahnschmelzes ab.
- IDs `mc700` bis `mc749` sind vorläufig und in aktuellen Dateien frei.
  Historische Verwendung in `question_usage` vor Aktivierung noch lesend
  abzugleichen; geschützte Nutzungshistorie und Rundenzähler nicht geändert.
- Prüfungen erfolgreich: bestehende Bibliotheksprüfung des aktiven Bestands,
  dieselbe Prüfung in einer isolierten Kopie mit beiden neuen Paketen
  zusammen (1.503 Einträge einschließlich inaktiver Zwei-Gruppen-Fragen),
  vier unterschiedliche Optionen je Frage, Fragetexte höchstens 160 Zeichen,
  ID-Prüfung und unveränderte Prüfsummen sämtlicher aktiver Fragendateien.
  Aktueller Fragenlader weiterhin 266 Auswahl- und 268 Wahr/Falsch-Fragen;
  keine Vormerkung wird eingelesen.
- Keine Fragen übertragen, keine Aktivierung und kein Neustart. Beide
  Vormerkungspakete bleiben lokal. Gemeinsames Live-Update einschließlich
  vorbereiteter Startseiten-/Mailkorrektur auf Nutzerwunsch bis zur
  Vorbereitung der übrigen Fragearten zurückgestellt.

### 24.10.2026 – 50 Aufgaben „Paare bilden“ lokal vorgemerkt

- Auf Nutzerwunsch weitere 50 recherchierte Paaraufgaben vorbereitet, jede
  mit genau drei eindeutigen Zuordnungen, Erklärung und Quellen. Insgesamt
  150 einzeln geprüfte Paare und 129 Quellenverweise. Ablage ausschließlich
  lokal unter `fragen/vormerkungen/2026-10-24-paare-bilden-50/` mit
  `kandidaten.json`, `LESELISTE.md`, `RECHERCHE.json` und
  `PRUEFBERICHT.md`.
- Aus tatsächlich recherchierten Sachverhalten selbst formuliert. Überwiegend
  Belege von Institutionen, Museen, Hochschulen, Herstellern und zuständigen
  Sportverbänden. Inhaltliche Prüfung umfasst alle drei Paare jeder Aufgabe.
  Technische Direktabrufsperren, Weiterleitungen und verwendete Original-
  Suchindexinhalte sind bei den betroffenen Aufgaben dokumentiert.
- Abgleich gegen alle 1.403 Daily-Bestandseinträge einschließlich der 60
  inaktiven Zwei-Gruppen-Fragen sowie beide bisherigen Vormerkungspakete
  mit zusammen 100 Fragen: 1.503 Vergleichseinträge. Optionen, einzelne
  Zuordnungen, Lösungen, Erklärungen und Metadaten einbezogen; auffällige
  Begriffe und Ähnlichkeitshinweise nach Wissenskern redaktionell bewertet.
  Keine Dublette festgestellt. Kimchi wegen mehrfachen Vorkommens durch
  Kombucha ersetzt; Chewbaccas Geräuschquelle wegen des vorgemerkten
  `mc704` nicht erneut verwendet.
- Religion ausgeschlossen. Keine neue Wissensfrage über eine reale Person.
  Namen von Instrumenten, Verfahren und physikalischen Effekten erfordern
  kein biografisches Wissen. Beim Rollstuhlrugby ausdrücklich erlaubten
  Kontakt zwischen Rollstühlen von verbotenem Körperkontakt unterschieden.
- IDs `ma700` bis `ma749` sind vorläufig und im aktuellen Dateibestand frei.
  Historische Verwendung in `question_usage` vor Aktivierung noch lesend
  abzugleichen. Spielergebnisse, Konten und Nutzungshistorie unverändert.
- Prüfungen erfolgreich: verbindliche Bibliotheksprüfung des aktiven
  Bestands sowie dieselbe Prüfung in einer isolierten Kopie mit allen drei
  Vormerkungspaketen zusammen (1.553 Einträge einschließlich inaktiver
  Zwei-Gruppen-Fragen). Genau 50 vollständige Aufgaben, 150 unterschiedliche
  Paare, eindeutige vollständige Lösungen, gemischte rechte Reihenfolge und
  Fragetexte höchstens 160 Zeichen geprüft. Prüfsummen aller aktiven
  Fragendateien und beider früheren Pakete unverändert. Der Fragenlader liest
  weiter 265 Paaraufgaben und keine der neuen Vormerkungen ein.
- Insgesamt lokal 150 neue Aufgaben vorgemerkt: 50 Wahr/Falsch, 50 Multiple
  Choice und 50 Paare bilden. Keine Fragen übertragen, keine Aktivierung und
  kein Neustart. Das gemeinsame Live-Update einschließlich vorbereiteter
  Startseiten-/Mailkorrektur bleibt bis zur Vorbereitung der übrigen Fragen
  zurückgestellt.
- Abschlussprüfung der Serververbindung scheiterte zweimal mit SSH-
  Verbindungstimeout; auch der öffentliche Health-Endpunkt war über das
  Recherchewerkzeug nicht abrufbar. Daraus wird kein Serverausfall abgeleitet.
  Aktuelle erneute Live-Prüfung und Übertragung dieser Lognotiz auf den Server
  stehen aus. Diese Notiz ist bisher nur lokal gespeichert. Die Anzahl
  tatsächlich gespielter Runden bleibt mangels lesbaren Zugriffs auf die
  geschützte Live-Datenbank weiterhin offen.

### 24.10.2026 – 50 Schätzfragen lokal vorgemerkt; Reihenfolge zuletzt

- Auf ausdrücklichen Nutzerwunsch die vierte Frageart „Reihenfolge“ in der
  Redaktion zunächst übersprungen und stattdessen 50 Schätzfragen recherchiert.
  „Reihenfolge“ kommt bei der weiteren Vorbereitung zuletzt. Die tatsächliche
  Spielreihenfolge im Manifest wurde nicht geändert.
- Neues Paket ausschließlich lokal unter
  `fragen/vormerkungen/2026-10-24-schaetzfragen-50/` mit
  `kandidaten.json`, `LESELISTE.md`, `RECHERCHE.json` und
  `PRUEFBERICHT.md`. Genau 50 Fragen, jede mit positivem numerischem
  Vergleichswert, eindeutiger Einheit, Erklärung und Quellen; insgesamt 55
  Quellenverweise. Wortlaut anhand tatsächlich recherchierter Fakten selbst
  formuliert. Keine Religionsfrage und keine neue Wissensfrage über eine
  reale Person.
- Abgleich gegen alle 1.403 lokalen Daily-Einträge einschließlich der 60
  vorbereiteten Zwei-Gruppen-Fragen sowie die 150 vorher vorgemerkten Fragen:
  1.553 Vergleichseinträge. Aufgaben, Optionen, Zuordnungen, Lösungen,
  Erklärungen und Metadaten einbezogen; Volltext- und Begriffssuche sowie
  gewichteten Wortabgleich nach Wissenskern redaktionell bewertet. Auch die
  neuen Fragen untereinander geprüft. Keine Dublette festgestellt.
- Vorhandene Kerne vor Aufnahme ausgeschlossen: Elefantentragzeit
  (`ma533`, `or186`), Fläche des Salar de Uyuni (`mc217`), Temperatur des
  Blitzkanals (`tf23`), ISS-Tagesumlauftakt (`tf40`) und das Alter der
  Grönlandhaie (vorgemerktes `tf712`). Concorde-Wärmeausdehnung wegen der
  Nähe zur bestehenden Eiffelturm-Ausdehnung (`tf10`) nicht übernommen.
- Zahlen mit schwankendem oder zeitlichem Bezug im Fragetext eingegrenzt:
  unter anderem konkrete Rekordversuche, Modelljahr des Golfballs,
  Regelfassung des Ruderboots, Betreiberstand beim Miniatur Wunderland,
  Studienmittel einer Vogelwanderung und obere Enden genannter Richtbereiche.
  Englische „quintillion“ korrekt als deutsche Trillionen übersetzt.
  Stunden/Minuten, Meter/Kilometer, Startmasse, Zoll/Zentimeter,
  Meilen/Kilometer und Apollo-Speicher einschließlich Parität nachgerechnet.
  Einzelheiten und Quellenzugriff pro Frage in `RECHERCHE.json` dokumentiert.
- Kennungen `es700` bis `es749` sind vorläufig und in den aktuellen lokalen
  Dateien frei. Vor dem späteren Live-Update müssen der aktuelle Serverbestand
  und die historische Verwendung in `question_usage` erneut lesend abgeglichen
  werden. Spielergebnisse, Konten und Nutzungsverlauf blieben unverändert.
- Prüfungen erfolgreich: verbindliche Bibliotheksprüfung des aktiven
  Bestands; dieselbe Prüfung zusätzlich in einer isolierten Kopie mit allen
  vier Vormerkungspaketen (1.603 Einträge einschließlich der 60 inaktiven
  Zwei-Gruppen-Fragen). Genau 50 unterschiedliche Fragen, numerische endliche
  Antworten, korrekte Einheitenumrechnungen, vorgegebenes JSON-Schema und
  Fragetexte höchstens 160 Zeichen geprüft.
- Alle sechs bestehenden Daily-Dateien und sämtliche Dateien der drei
  früheren Vormerkungspakete per Prüfsumme unverändert. Der Fragenlader liest
  weiterhin 275 Schätzfragen und keine der 50 neuen Kandidaten ein. Insgesamt
  jetzt 200 neue Aufgaben lokal vorgemerkt: jeweils 50 Wahr/Falsch, Auswahl,
  Paare bilden und Schätzung. Keine Frage übertragen, keine Aktivierung und
  kein Neustart; gemeinsames Live-Update weiterhin zurückgestellt.
- SSH-Verbindung sowohl am Beginn als auch am Abschluss erneut mit Timeout
  gescheitert. Das lokale Projektlog wurde vollständig gelesen; das
  maßgebliche Serverlog konnte in diesem Schritt nicht neu vollständig gelesen
  und diese Fortschrittsnotiz nicht dorthin übertragen werden. Beide lokalen
  Nachträge zu Paar- und Schätzfragen müssen bei wieder erreichbarem Server
  nachgeführt werden. Kein Serverausfall und kein aktueller öffentlicher
  Live-Status daraus abgeleitet. Zahl gespielter Runden weiterhin nicht
  verifiziert.


### 24.10.2026 – 50 Reihenfolgeaufgaben der Variante 1 lokal vorgemerkt

- Nutzerentscheidung umgesetzt: Variante 1 erweitert die Ordnungsmerkmale bei
  unverändert vier Karten und bestehender Wertung. Variante 2 bleibt für später.
  Ausdrücklich noch kein Live-Update.
- Neues Paket nur lokal unter
  `fragen/vormerkungen/2026-10-24-reihenfolge-50/` mit `kandidaten.json`,
  `LESELISTE.md`, `RECHERCHE.json` und `PRUEFBERICHT.md`: genau 50 Aufgaben,
  200 Karten und 73 Quellenverweise. Neun Themenfelder; unter anderem Rang,
  Seltenheit, Lautstärke, Wettkampf-/Produktionsablauf, Nahrungskette, Route,
  Materialeigenschaft und Wahrscheinlichkeit. Keine Religionsfrage und keine
  neue biografische Wissensfrage über eine reale Person.
- 1.403 lokale Daily-Einträge einschließlich 60 inaktiver Zwei-Gruppen-Aufgaben
  und alle 200 früheren Vormerkungen als Vergleich: 1.603 Einträge. Volltext,
  Optionen, Vergleichsbegriffe, Lösungen, Erklärungen und Metadaten einbezogen;
  ähnliche Treffer nach Wissenskern bewertet, neue Aufgaben auch untereinander
  geprüft. Keine Dublette festgestellt. Bereits vorhandene Singstimmen,
  Tempobegriffe, Luftzusammensetzung, Mensch/Hund-Zahnzahlen, menschlichen
  Chromosomensatz, Tennisnetzhöhe und Zitronensaft/reines Wasser ausgeschlossen.
- Originalquellen tatsächlich inhaltlich recherchiert. Einzelne durch direkte
  Abrufbeschränkungen nur im ausgelesenen Original-Suchindex zugänglich;
  Einschränkungen pro Aufgabe dokumentiert. Defekte Altlinks ersetzt oder
  entfernt. Regel-/Tabellenfassungen und abweichende Abläufe eingegrenzt.
- Vorläufige IDs `or700` bis `or749` im aktuellen lokalen Vergleich frei.
  Historische Verwendung und Fingerabdrücke in `question_usage` noch nicht
  verifiziert; vor einer späteren Aktivierung erneut mit Serverbestand und
  Nutzungshistorie abgleichen. Keine Änderung an Spielergebnissen/Konten.
- Prüfungen erfolgreich: verbindliche aktive Bibliotheksprüfung und dieselbe
  Prüfung in isolierter Gesamtkopie mit allen 250 Vormerkungen (1.653 Einträge
  einschließlich der 60 inaktiven Zwei-Gruppen-Aufgaben); Schema, Kennungen,
  vier eindeutige Karten, vollständige Lösung, Quellen, Textlängen und numerische
  Sortierungen geprüft. Würfelsummen über alle 36 Paare unabhängig ausgezählt.
- 40 geschützte Dateien einschließlich aller sechs Daily-Dateien, Manifest,
  Fragenlader, vorhandener anderer Änderungen und aller vier früheren
  Vormerkungspakete per Prüfsumme unverändert. Vorhandenen Loginhalt bytegetreu
  erhalten. Aktiver Lader weiterhin 269 Reihenfolge-/1.343 aktive Fragen;
  keine Vormerkung eingelesen. Insgesamt 250 neue Aufgaben, je Frageart 50.
- Server-SSH in diesem Schritt mit Timeout gescheitert. Maßgebliches Serverlog
  nicht frisch vollständig lesbar; kein aktueller Server-/Historienabgleich.
  Diese Notiz bisher nur lokal, zusammen mit offenen Paar-/Schätzfragen-Notizen
  später nachzuführen. Kein Serverausfall oder öffentlicher Live-Status daraus
  abgeleitet. Keine Übertragung, Aktivierung oder Neustart; Rundenzahl weiterhin
  nicht verifiziert. Live-Update bleibt ausdrücklich zurückgestellt.

## Conquest – farbige Nutzerfassung mit drei Bildkorrekturen (24.10.2026)

- Die vom Nutzer heute bereitgestellte farbige Gesamtkarte als eigene Vorlage
  übernommen; keine ältere beige oder anders erzeugte Fassung ersetzt.
  Ausgangsbild lokal unter
  `offline-preview/conquest-farbkarte-2026-10-24/vorlage.png` gesichert.
- Mit dem eingebauten Bildwerkzeug drei gezielte Änderungen erzeugt:
  punktiertes Gegenstück der Kamtschatka-Verbindung am linken Rand bis Alaska;
  Grönland einschließlich des westlichen gelben Bereichs einheitlich goldgelb
  ohne hart abgetrennte weiße Innenfläche; verkleinerter Titel und vollständige
  Kontinentlegende in der vorhandenen Goldkartusche.
- Die gespeicherte Gesamtkarte tatsächlich geöffnet und die drei Stellen
  visuell geprüft. Legende lesbar mit allen sechs Farbmarken und Werten:
  Nordamerika +5, Südamerika +2, Europa +5, Afrika +3, Asien +7, Australien +2.
  Die bestehende rechte Kamtschatka-Verbindung ist weiterhin sichtbar.
- Ergebnis ausschließlich lokal:
  `offline-preview/conquest-farbkarte-2026-10-24/stormseeds-conquest-farbkarte-v1.png`.
  Der vollständige Bearbeitungsauftrag liegt daneben in
  `bearbeitungsauftrag.txt`. Die Projektkopie stimmt per SHA256 mit dem
  erzeugten Bild überein:
  `a527f349a346a34688b829e581f2e5938f9760833e925f54be174066605f59a8`.
- In diesem Schritt keine Programmdateien, aktiven Bildverweise oder Fragen
  verändert. Keine Verbindung zum Server, Übertragung, Aktivierung oder
  Neustart. Die Bildkorrektur ist keine Prüfung des vollständigen Spielablaufs;
  ein Einbau dieser neuen Fassung in die lokale Spielansicht steht noch aus.

## Conquest – Beschriftungen, Inselpalette und Rand bereinigt (24.10.2026)

- Auf Nutzerwunsch die lokale farbige Fassung mit dem eingebauten Bildwerkzeug
  weiterbearbeitet. Beschriftungen jetzt vollständig `Madagaskar`, `Indonesia`
  und `Japan`. Alle zur Indonesia-Gruppe gehörenden Inseln einschließlich
  der nördlichen kleinen Inselgruppe lila; Siam auf dem Festland weiterhin
  grün. Middle East einschließlich Arabischer Halbinsel jetzt Asien-grün.
- Die dick gestrichelte rechteckige Randumrahmung entfernt; der durchgezogene
  schwarze/goldene Rahmen bleibt. Die tatsächlichen punktierten
  Angriffsverbindungen bleiben sichtbar, einschließlich der beiden
  Randsegmente Alaska und Kamtschatka. Japan nach gezielter Farbkorrektur
  grün, die weiter südlich gelegene Indonesia-Inselgruppe weiterhin lila.
- Ergebnis gespeichert und tatsächlich in Originalauflösung geöffnet:
  `offline-preview/conquest-farbkarte-2026-10-24/stormseeds-conquest-farbkarte-v2.png`.
  Die genannten Beschriftungen, Farben, beide Kartenränder sowie die sechs
  unveränderten Kontinentboni visuell kontrolliert. SHA256:
  `7d239294d81561a8d66f6a703995f48704fdfe73340989520fd53bfb181cea23`.
  Vorgängerversion v1 per Prüfsumme unverändert.
- Vollständige Aufträge liegen daneben in `bearbeitungsauftrag-v2.txt` und
  `bearbeitungsauftrag-v2-nachkorrektur.txt`. Keine Programmdateien, aktiven
  Bildverweise oder Fragen verändert; kein Serverzugriff und keine Aktivierung.
  Die neue Bilddatei ist weiterhin noch nicht in die lokale Spielansicht
  eingebaut.

## Conquest – Offline-Vorschau wieder geöffnet (24.10.2026)

- Die vorhandene lokale Vorschauanwendung unter `127.0.0.1:54506` erneut
  gestartet und die Testlobby `/karten/welteroberung/4` in Chrome geöffnet.
  Sie verwendet ausschließlich `runtime/codex-preview.sqlite3`; vor dem
  Start eine zusätzliche Sicherung dieser lokalen Testdatenbank angelegt.
- Die tatsächlich gerenderte Tischansicht mit 42 Truppenmarken sowie das
  Öffnen und Schließen des privaten Inventars geprüft. Die zugeteilte Mission
  und der leere Länderkartenbestand wurden angezeigt. Prüfbild:
  `runtime/conquest-offline-2026-10-24/tischansicht.png`.
- Die Ansicht verwendet weiterhin die Konturenkarte. Die neue Farbkarte v2
  bleibt separat vorbereitet und noch nicht eingebaut. Keine Programm- oder
  Fragendatei geändert; kein Serverzugriff, keine Übertragung und keine
  Live-Aktivierung. Der eigentliche Zugablauf bleibt weiterhin offen.

## Conquest – neue Farbkarte in die Offline-Vorschau eingebaut (24.10.2026)

- Auf ausdrücklichen Nutzerauftrag die vorbereitete Farbkarte v2 ausschließlich
  im lokalen Arbeitsordner eingebunden. Die neue aktive lokale Bilddatei heißt
  `static/conquest/boards/welt-conquest-farbkarte-v2.png` und stimmt bytegenau
  mit der vorbereiteten Vorlage überein; SHA256:
  `7d239294d81561a8d66f6a703995f48704fdfe73340989520fd53bfb181cea23`.
  Die Vorlage und die frühere Konturenkarte bleiben erhalten.
- Spielansicht und flache Brettvorschau verwenden weiterhin dieselbe zentrale
  Komponente `_conquest_board_surface.html`. Den früheren zusätzlichen Titel-
  und Legendenkasten einschließlich seiner unbenutzten CSS-Regeln entfernt,
  weil beides bereits in der Farbkarte enthalten ist. Die Farben werden ohne
  den bisherigen Papier-Mischmodus angezeigt; das Seitenverhältnis entspricht
  der Originaldatei mit 1284 × 1225 Pixeln.
- Alle 42 Truppenmarken an der neuen Grafik ausgerichtet. Tisch- und Draufsicht
  projizieren dieselben Bildkoordinaten; die bestehende Kupferpassung und die
  Spielregeln bleiben erhalten. CSS-/JS-Verweise auf Version 6 erhöht und die
  vorhandene Bildreferenz im Conquest-Test aktualisiert.
- Tatsächliche Chrome-Prüfung unter `/karten/welteroberung/4`: Farbkarte geladen,
  42 dynamische Marken vorhanden, keine zusätzliche alte Kartusche, Tischpassung
  und vollständige Draufsicht visuell kontrolliert. Alaska, Grönland, Ukraine,
  Irkutsk und Indonesien angeklickt; die jeweiligen Gebiets- und Nachbaranzeigen
  funktionieren. Inventar mit unveränderter Mission geöffnet und geschlossen.
  Prüfbilder: `runtime/conquest-farbkarte-integration-2026-10-24/tischansicht.png`
  und `runtime/conquest-farbkarte-integration-2026-10-24/draufsicht.png`.
- Alle sechs vorhandenen Conquest-Tests in isolierter lokaler Prüfdatenbank
  bestanden; abschließende JavaScript-Syntaxprüfung erfolgreich. Keine
  Serververbindung, Übertragung, Live-Aktivierung oder Änderung am Fragenbestand.
  Der vollständige Zugablauf ist weiterhin nicht implementiert.

## Conquest – Mausrad zum Vorbeugen statt Zoom (24.10.2026)

- Auf Nutzerwunsch die bisherige Kombination aus freiem Verschieben und
  Mausrad-Zoom in der lokalen Vorschau ersetzt. Das Rad verändert jetzt
  ausschließlich den Blickwinkel innerhalb fester Grenzen zwischen Tisch-
  und Draufsicht. Vorwärts beugt über den Tisch, rückwärts lehnt zurück.
  Die Darstellung bleibt zentriert; ihre Grundskalierung hängt ausschließlich
  von der Fenstergröße ab. Den überflüssigen Knopf `Zentrieren` entfernt.
- Karte, Kupferöffnung und Tischkulisse werden mit zusammengehörigen
  Projektionen geneigt; die 42 Truppenmarken folgen denselben Kartenpunkten.
  Die beiden Ansichtsknöpfe wählen weiterhin die Endlagen. Die vollständige
  Draufsicht wird zwischen oberer Bedienleiste und unterem Hinweis eingepasst.
- Die Raumkulisse ist weiterhin ein Foto, kein räumlich begehbares Modell.
  Ihre Randbereiche laufen weich aus; zur Draufsicht wird die Kulisse
  ausgeblendet. Dadurch entstehen beim Winkelwechsel keine harten Ränder der
  endlichen Fotofläche. Ersetzte Zoom-, Zieh- und Cursorregeln entfernt statt
  überschrieben; CSS-/JS-Verweise jetzt Version 8.
- Tatsächliche Chrome-Prüfung der lokalen Lobby: Radbewegung in beide
  Richtungen, Zwischenwinkel und beide Endlagen funktionieren. Zusätzliches
  Scrollen an den Grenzen verlässt den zulässigen Bereich nicht. Ein Ziehversuch
  verändert weder Kartenprojektion noch Szenenposition; die Grundskalierung
  blieb bei allen Winkeln gleich. Grönland im Zwischenwinkel angeklickt und
  korrekte Gebiets-/Nachbaranzeige beobachtet.
- Alle sechs Conquest-Tests in isolierter lokaler Prüfdatenbank bestanden;
  abschließende JavaScript-Syntaxprüfung und `git diff --check` erfolgreich.
  Prüfbilder unter `runtime/conquest-blickwinkel-2026-10-24/`, insbesondere
  `vorgebeugt.png` und `draufsicht.png`. Chrome mit einer vorgebeugten Ansicht
  offengelassen. Ausschließlich lokal gearbeitet; kein Serverzugriff und keine
  Änderung an Fragen, Konten oder gespeichertem Spielzustand.

## Conquest – Raumkulisse beim Vorbeugen dauerhaft sichtbar (24.10.2026)

- Die ausdrückliche Nutzerkorrektur ersetzt die zuvor eingeführte Ausblendung:
  Die Raumkulisse bleibt vom normalen Tischwinkel bis zur Draufsicht vollständig
  eingeblendet. Die winkelabhängige Deckkraft und die damit gekoppelte Öffnung
  der Kartenbeschneidung entfernt. Die Karte bleibt bei jedem Winkel innerhalb
  derselben mitbewegten Kupferöffnung.
- Die vorhandene Fotoergänzung an den Rändern verwendet jetzt den oberen
  Raumanteil, damit die frühere vergrößerte grüne Filzfläche dort nicht dominiert.
  Die Raumgrafik bleibt eine perspektivisch mitbewegte Fotokulisse. Mausrad-
  Winkelsteuerung, feste Zentrierung und ausgeschaltetes Verschieben bleiben
  erhalten. CSS-/JS-Verweise auf Version 9 erhöht.
- Tatsächlich in Chrome geprüft: Tischansicht, Vorbeugen, Draufsicht per Mausrad
  und Zurücklehnen. In allen vier Zuständen `opacity: 1`, `visibility: visible`
  und 42 Truppenmarken beobachtet; Tisch und Karte visuell in Zwischenwinkel
  und Draufsicht geprüft. Nachweise unter
  `runtime/conquest-raum-sichtbar-2026-10-24/`: `pruefung.json`,
  `vorgebeugt.png` und `draufsicht.png`. Die lokale Vorschau bleibt geöffnet.
- JavaScript-Syntaxprüfung und `git diff --check` erfolgreich. Ausschließlich
  lokale Darstellungs- und Dokumentationsdateien geändert; kein Serverzugriff,
  keine Veröffentlichung und keine Änderung an Fragen oder Spielständen.

## Conquest – Grenze der Fotokulisse und offene Darstellungsentscheidung (24.10.2026)

- Nutzerprüfung widerlegt eine natürlich wirkende Raumbewegung: Die seitliche
  unscharfe Fotoergänzung erscheint als großer Holzbalken, während sich der
  Raum beim Vorbeugen verzieht. Die bisherigen Sichtbarkeitswerte und
  Prüfbilder belegen keine räumlich korrekte Kamerabewegung. Dieser gewünschte
  Effekt ist mit dem aktuellen Stand nicht erreicht.
- Aktueller Codebefund: `.conquest-room` verwendet ein flaches Foto mit
  vergrößerter unscharfer Ergänzung und derselben ebenen Projektion wie die
  Karte. Im geprüften Assetbestand unter `static/` und `offline-preview/`
  liegt kein 3D-Raummodell vor; vorhandene FBX-Modelle gehören zu den Würfeln.
- Zwei mögliche Richtungen dem Nutzer zur Entscheidung vorgelegt: ein
  getrennter lokaler Prototyp mit echter Raum-/Tischgeometrie und beweglicher
  Kamera oder eine feste Raumkulisse mit separat kippbarer Tischplatte.
  Eine Richtungsentscheidung steht noch aus. In diesem Schritt keine weitere
  Darstellungsänderung, kein Serverzugriff und keine Veröffentlichung.

## Conquest – Aufwand für eine begrenzte 2,5D-Ansicht geklärt (24.10.2026)

- Nutzerentscheidung: Ein vollständiger 3D-Raum geht zu weit. Aktueller Auftrag
  ist ausschließlich die Aufwandsklärung für die einzelne Tischansicht und ihre
  Eignung für spätere 3D-Figuren, keine Umsetzung.
- Nach Prüfung des aktuellen Codes und des Originalhintergrunds als passende
  Richtung eingegrenzt: räumlicher Tisch mit Brett und späteren Figuren sowie
  eine aus wenigen getrennten Bildflächen bestehende Raumkulisse. Die Kamera
  erhält ausschließlich einen begrenzten Vorbeugeweg. Ein vollständiges
  Raummodell ist weder dafür noch für Figuren auf dem Brett erforderlich.
- Größter offener Gestaltungsaufwand: Im Originalbild sind Tisch, Raum und
  gegenseitige Verdeckungen fest verbunden. Für den vorgesehenen Kamerabereich
  müssen diese Ebenen getrennt und neu sichtbar werdende Bildbereiche ergänzt
  werden. Eine bloße Verzerrung des Gesamtfotos ist dafür nicht geeignet.
- Vorläufige Arbeitsabschätzung: etwa 2–4 konzentrierte Arbeitsstunden für
  einen ersten Sichtprototyp, insgesamt ungefähr 1–2 Arbeitstage für Einbindung,
  Kamerapassung, Gebietsbedienung und Prüfung. Keine gemessene Dauer oder
  Terminzusage; Grafikrekonstruktion ist die größte Unsicherheit. Eigene
  Figurenmodelle und deren vollständige spätere Integration sind nicht enthalten.
- Technische Grundlage anhand der offiziellen Three.js-Dokumentation zu
  Bildhintergründen und dem Laden von 3D-Modellen geprüft. Keine Anwendungs-
  oder Bilddateien geändert, keine Installation, kein Serverzugriff und keine
  Veröffentlichung.

## Conquest – erster getrennter lokaler 2,5D-Prototyp (24.10.2026)

- Auf ausdrücklichen Nutzerauftrag den Ansichtsprototyp unter
  `offline-preview/conquest-2-5d-v1/` gebaut und in Chrome tatsächlich geöffnet:
  `http://127.0.0.1:54508/`. Der getrennte statische Vorschauprozess ist nur
  an `127.0.0.1` gebunden. Bestehende Anwendungsdateien, die Flask-Vorschau,
  Fragen, Konten und gespeicherte Partien wurden in diesem Schritt nicht verändert.
- Der Tisch besitzt echte räumliche Geometrie für Platte, Rand, Unterbau und
  Beine. Die Kamera bewegt sich per Mausrad oder Schieberegler auf einem festen
  Bogen von 32 bis 82 Grad. Tisch und Karte bleiben stehen; manuelles Zoomen und
  Verschieben sind nicht vorhanden. Der feste Kameraabstand wird nur passend
  zur Fenstergröße bestimmt und gilt dann für den gesamten Bewegungsbereich.
- Die Karte ist eine bytegleiche Kopie der bisherigen Farbkarte v2; SHA256
  unverändert `7d239294d81561a8d66f6a703995f48704fdfe73340989520fd53bfb181cea23`.
  Der Prototyp lädt keine Spielerdatenbank und enthält bewusst noch keine
  Truppenmarken, Figuren oder Spielzüge. Er dient zunächst der Bewegungsprobe.
- Für die Tiefenkulisse mit dem eingebauten Bildwerkzeug den in das Foto
  gemalten Tisch entfernt und den Boden ergänzt; eine passende Teppichtextur
  ergänzt neu sichtbare Bodenbereiche. Beide Bilder, vollständige Aufträge
  und Prüfsummen liegen im Prototypordner. Originalbilder bleiben erhalten.
  Die Raumkulisse wird auf eine Bodenfläche, eine hintere und zwei seitliche
  Bildflächen projiziert und bleibt eingeblendet. Sie ist weiterhin eine
  vereinfachte Bildbühne; Möbel und einzelne Materialübergänge sind noch keine
  räumlich ausgearbeiteten Objekte und benötigen gegebenenfalls Feinschliff.
- Three.js 0.180.0, Tag r180, samt MIT-Lizenz lokal beigelegt. Alle benötigten
  Laufzeitdateien liegen im Prototypordner; keine CDN- oder Kontoverbindung.
  Die Darstellung rendert bei Eingaben und Größenänderungen, ohne dauernden
  Animationslauf im Leerlauf.
- Sechs neue lokale Kameratests bestanden: Einpassung bei fünf Fensterformaten
  für alle Viertelgrad-Schritte des Bewegungsbereichs, unveränderter Abstand
  und Blickwinkel der Kameralinse sowie Anheben/Vorbewegen der Kamera bei
  unverändertem Zielpunkt. JavaScript-Syntaxprüfung erfolgreich.
- Tatsächliche Chrome-Prüfung: sichtbare Karte auf dem Tisch, Sitzposition
  32 Grad, Zwischenwinkel 54 Grad und Überblick 82 Grad visuell kontrolliert;
  Radbewegung in beide Richtungen und zusätzliche Bewegung an beiden Grenzen
  korrekt begrenzt. Ziehen verändert die Ansicht nicht. Schieberegler per
  Tastatur mit Home/End geprüft; keine Warnungen oder Fehler in der Seitenkonsole.
  Nachweise: `runtime/conquest-2-5d-pruefung/browser-pruefung.json` und drei
  Prüfbilder im selben Ordner. Prototyp in Chrome in Sitzposition offengelassen.
- Dokumentation unter `offline-preview/conquest-2-5d-v1/README.md`. Keine
  Serververbindung, Übertragung, Live-Aktivierung oder Veröffentlichung.
  Der Nutzer soll zunächst das Vorbeugen beurteilen; weitere Integration offen.

## Conquest – Kulissenübergänge und naher Blick korrigiert, weiterhin lokal (24.10.2026)

- Nutzerbefund am ersten 2,5D-Prototyp: sichtbare Übergänge zwischen zwei
  Teppichdarstellungen, falsche Holzstruktur oben seitlich und zu großer
  Betrachtungsabstand. Neue ausdrückliche Vorgabe: näherer Sitzabstand; im
  Überblick darf der vordere Holzrahmen unten über den Bildrand laufen.
  Diese Vorgabe ersetzt die bisherige Einpassung des gesamten Tischs bei
  unverändertem Kameraabstand über alle Winkel.
- Ausschließlich den getrennten lokalen Prototyp unter
  `offline-preview/conquest-2-5d-v1/` weiterbearbeitet. Vorherige Fassungen der
  geänderten Dateien und die beiden Nutzerbilder unter
  `runtime/conquest-2-5d-korrektur-2026-10-24/` gesichert. Vorhandene andere
  Arbeitsänderungen erhalten; keine Fragen, Konten oder Spielstände angefasst.
- Projektion des Gesamtfotos über Wand, Boden und Seitenflächen entfernt.
  Eine einzige durchgehende Bodenfläche verwendet jetzt überall denselben
  Teppich. Die Kulisse besteht aus einer vollständigen Panorama-Rückwand mit
  gespiegelter seitlicher Fortsetzung sowie zwei freigestellten Möbelkarten.
  Mit dem eingebauten Bildwerkzeug zwei getrennte Kulissenbilder anhand der
  bisherigen Kulisse erstellt; Aufträge, Ausgaben, Bildmaße und Prüfsummen im
  Prototypordner dokumentiert. Frühere Bilder bleiben erhalten.
- Kamera weiterhin von 32 bis 82 Grad, ohne freies Verschieben oder manuelles
  Zoomen. Abstand und Bildausrichtung werden je Winkel für eine nahe Ansicht
  bestimmt; Kameralinse und Tischposition bleiben unverändert. Im Überblick
  füllt die Karte nahezu die nutzbare Höhe, ihr vorderer Holzrahmen reicht
  unten aus dem Bild. Die Sitzansicht zeigt die größere Karte, Kamin und Sessel.
  Sehr kurze vorübergehende Fenstermaße werden beim Neuzeichnen abgefangen.
- Acht Kameratests bestanden: alle Viertelgrad-Schritte bei sechs Formaten,
  vollständige Sichtbarkeit und Größenausnutzung der Karte, kontinuierliche
  Kamerabewegung sowie die gesonderten Vorgaben für Sitzposition und Überblick.
  JavaScript-Syntaxprüfung und `git diff --check` erfolgreich. Kartenbild
  weiterhin bytegleich zur Farbkarte v2, SHA256 unverändert
  `7d239294d81561a8d66f6a703995f48704fdfe73340989520fd53bfb181cea23`.
- Tatsächliche Chrome-Prüfung unter `http://127.0.0.1:54508/`: Sitzposition
  32 Grad, Vorbeugen 54 Grad und Überblick 82 Grad visuell kontrolliert.
  Die bemängelten Teppich-Materialwechsel und generischen Holz-Ersatzflächen
  sind in diesen Ansichten entfernt. Mausrad in beide Richtungen samt Grenzen,
  beide Ansichtstasten, Schieberegler Home/End und fehlende Verschiebung beim
  Ziehen geprüft. Nach der letzten Korrektur und erneutem Laden keine neuen
  Konsolenfehler oder Warnungen. Prüfprotokoll und drei Bilder mit Endung
  `-v2` im oben genannten Laufzeitordner; frühere Zwischenfehler im Protokoll
  ausdrücklich erhalten. Vorschau in Sitzposition geöffnet gelassen.
- Die Möbel bleiben flache Kulissenkarten ohne eigene räumliche Tiefe;
  kein vollständiger 3D-Raum und noch keine Figuren oder Spielzüge. Kein
  Zugriff auf den Live-Server, keine Live-Aktivierung oder Veröffentlichung.

## Live-Auftrag – Fragen zuerst, Tisch erst nach erneuter Erreichbarkeitsprüfung (24.10.2026)

- Nutzer hat die bisher lokal vorbereiteten Fragen und Conquest-Änderungen
  ausdrücklich zur Veröffentlichung freigegeben. Nach einem erneuten vom
  Nutzer gemeldeten Serverausfall gilt verbindlich: Beim nächsten erfolgreichen
  Zugriff zuerst die 250 neuen Daily-Fragen aktivieren; danach erneut prüfen,
  ob der Server noch erreichbar ist, und erst anschließend Tisch/Lobby ändern.
- Drei aktuelle SSH-Versuche mit dem bestehenden Zugang scheiterten am
  Verbindungsaufbau mit Timeout, darunter zwei ausdrücklich über IPv4.
  Der öffentliche Spiel-Healthcheck antwortete von diesem Rechner ebenfalls
  nicht; eine unabhängige HTTPS-Kontrollseite lieferte HTTP 200. Keine Ursache
  daraus abgeleitet. Aktuelles Serverlog, Dateistand, Rechte und geschützte
  Nutzungshistorie konnten in diesem Schritt nicht frisch gelesen werden.
  Es wurden keine Dateien zum Server übertragen und kein Dienst neu gestartet.
- Lokal ein getrenntes Fragen-Importpaket erstellt:
  `runtime/live-aktivierung-2026-10-24/fragen-250-vorbereitet.tar.gz`.
  Enthalten sind ausschließlich die fünf Pakete mit jeweils 50 neuen Fragen
  und ein Importplan, keine Datenbank, Zugangsdaten oder Tischdateien.
  Vorhandene aktive Fragendateien, Manifest, Steckbrief und Fragenlader blieben
  per SHA-256 unverändert. IDs und Inhaltsfingerabdrücke gegen den aktuellen
  lokalen Gesamtbestand sowie untereinander ohne Kollision geprüft.
- Dieselbe verbindliche Bibliotheksprüfung in einer getrennten Gesamtkopie
  einschließlich aller 250 Kandidaten erfolgreich. Alle 135 bestehenden
  Projekttests lokal bestanden. Windows-Prüflauf mit `.deps`, UTF-8,
  temporärem Ordner im Arbeitsbereich und isolierter Import-Datenbank;
  Ergebnisse unter `runtime/live-aktivierung-2026-10-24/`.
- Wiederaufnahme in diesem bestehenden Chat eingerichtet, Kennung
  `guesstimate-fragen-zuerst-aktivieren`, Status ACTIVE, alle fünf Minuten.
  Bei unverändertem Verbindungs-Timeout ohne neue Erkenntnis keine wiederholte
  Statusmeldung. Nach Rückkehr Import mit aktuellem Serverbestand und
  `question_usage` rein lesend abgleichen, Bibliotheksprüfung vor Aktivierung,
  tatsächliches Nachladen und sichtbare Live-Prüfung nachweisen. Keine
  Conquest-Dateien vor dem Fragenimport veröffentlichen und keine unnötige
  Leerstandsmail durch ein Wartungswerkzeug versenden.
- Live-Status weiterhin **nicht getan**. Dieser Lognachtrag ist vorerst nur
  lokal. Der zuletzt korrigierte 2,5D-Prototyp bleibt getrennt von der
  bestehenden Spielansicht; vor Tischveröffentlichung integrieren und prüfen.

## Fragenimport – Server kurz erreichbar, Aktivierung weiterhin offen (24.10.2026)

- Beim Wiederaufnahmetest SSH erfolgreich. Aktuelles Server-AGENTS und das
  vollständige Serverlog mit 2.684 Zeilen gelesen. App, Fragenlader, Manifest,
  Steckbrief, Validator und alle sechs Daily-Dateien entsprechen inhaltlich
  dem lokalen Ausgangsbestand. Dienst `active/running`, Release
  `2026.10.24-pool-home-mail-v1`; Health meldete weiterhin null neue Runden.
- Nutzungshistorie für `igroup` nicht lesbar; `sudo -n -l` verlangt ein
  Administratorkennwort. Keine Umgehung und keine Änderung der Nutzungshistorie.
- Ausschließlich Fragenpaket und begrenzten Aktivierungsbefehl auf dem Server
  bereitgestellt: `deploy/fragen-250-vorbereitet.tar.gz`,
  `deploy/question-refill-20261024/` und
  `deploy/activate_question_refill_20261024.py`. SHA-256 nach Übertragung
  abgeglichen. Aktive Fragendateien weiterhin unverändert; keine Conquest-Datei
  übertragen und kein Signal an den Spieldienst gesendet.
- Neue lokale Importprüfungen erfolgreich: Sperre historischer IDs und
  Fingerabdrücke, Erhalt zwischenzeitlicher Ergänzungen, wiederholbarer Import,
  Schutz bestehender geänderter IDs und echte Auswahl aus allen fünf neuen
  Paketen bei vollständig verbrauchtem Altbestand in isolierter Prüfdatenbank.
- Der anschließende Server-Validator in einer getrennten temporären
  Bibliothekskopie wurde mit SIGSEGV (Signal 11) beendet. Noch keine aktive
  Dateiübernahme und kein administrativer Aktivierungsversuch ausgeführt.
  Die folgende reine Dienstprüfung blieb ohne Antwort; SSH-Client beendet,
  ein neuer kurzer SSH-Test lief wieder in Timeout. Keine Ursache abgeleitet.
- Für die Aktivierung ist auf dem erreichbaren Server noch erforderlich:
  `sudo python3 /srv/guesstimate/deploy/activate_question_refill_20261024.py --activate`.
  Das Werkzeug prüft vor der Übernahme erneut, bricht bei Prüfungsfehlern ab,
  liest die Historie ausschließlich mit SQLite `mode=ro`, sichert die fünf
  Originaldateien und lädt nur bei erfolgreicher Prüfung die Gunicorn-Worker
  per SIGHUP nach. Kein Hostneustart und keine Wartungs-Mail.
- Wiederaufnahme aktualisiert: vorhandenes Paket nicht erneut bereitstellen,
  unveränderten Adminblock nicht wiederholt melden, nach erfolgreichem
  administrativem Import das Ergebnis und Health prüfen; Tisch erst danach.
  Live-Status **nicht getan**. Dieser Nachtrag ist vorerst ausschließlich lokal.

## Anschlussauftrag – beide Serverprojekte auf GitHub sichern (24.10.2026)

- Nutzer beauftragt ausdrücklich die anschließende Sicherung des tatsächlichen
  Server-Projektstands: Guesstimate samt allen Spielen nach
  `https://github.com/dabrain1982-cyber/Guesstimate`, persönliches Dashboard mit
  Finanzen, Essen und Co nach `https://github.com/dabrain1982-cyber/iGroup`.
- Bestehende Wiederaufnahme um beide Sicherungen erweitert. Priorität bleibt:
  Fragen zuerst, Server erneut prüfen, mögliche Conquest-Aktualisierung, danach
  die tatsächlichen Projektstände sichern. Beide Repositories vor Übertragung
  anhand aktueller Ordner, Remotes und Arbeitsstände zuordnen; private Daten
  und Geheimnisse gemäß bisherigem Sicherungsumfang erhalten, nicht in Git
  veröffentlichen. Keine Force-Pushes und keine Rücksetzung vorhandener Arbeit.
- Sicherungen noch nicht ausgeführt; Abschluss erst mit nachgewiesenen
  Commit-IDs und erfolgreichem entferntem Stand. Dieser Nachtrag nur lokal.

## Automatische Wiederaufnahme beendet – Upload erst auf erneuten Anstoß (24.10.2026)

- Nutzer teilt mit, dass der Server vorerst offline bleibt und die weitere
  Offline-Arbeit in einem anderen Chat fortgesetzt wird. Den Upload stößt
  der Nutzer später ausdrücklich in diesem Chat erneut an.
- Automatische Wiederaufnahme `guesstimate-fragen-zuerst-aktivieren` gelöscht.
  Keine weiteren automatischen Verbindungsprüfungen, Aktivierungen, Uploads
  oder GitHub-Sicherungen aus diesem Auftrag. Vorbereitete Dateien erhalten.
- Beim erneuten Anstoß den dann aktuellen Offline- und Serverstand vergleichen;
  diesen Zwischenstand nicht ungeprüft veröffentlichen. Reihenfolge bleibt
  Fragen, erneute Serverprüfung, mögliche Conquest-Aktualisierung und danach
  die beauftragten Sicherungen beider Serverprojekte.
- Aktivierung und Sicherungen weiterhin nicht nachgewiesen. Keine neuen
  Serverzugriffe in diesem Schritt; Nachtrag ausschließlich lokal.

## Conquest – Länderbedienung und Truppenmarken am Offline-Tisch (24.10.2026)

- Nutzer setzt die Arbeit ausdrücklich offline fort und wählt als nächsten
  Schritt Länderbedienung und Truppenmarken. Ausschließlich den getrennten
  2,5D-Prototyp unter `offline-preview/conquest-2-5d-v1/` erweitert. Vorherige
  Fassung vollständig unter `runtime/conquest-laender-marken-2026-10-24/vorher/`
  gesichert; bestehende andere Arbeiten erhalten. Kein Serverzugriff,
  Upload, Dienstneustart oder Veröffentlichung.
- Alle 42 Länder verwenden dieselben Bildpositionen wie die vorhandene
  Farbkarte. Dynamische Marken mit räumlichem Metallsockel und lesbarer
  Zahlenfläche folgen der unveränderten Brettkamera. Eine Auswahl zeigt
  Land, Kontinentbonus, Truppenzahl und Armee sowie ausschließlich die im
  bestehenden Weltmodell hinterlegten direkten Nachbarn. Goldener Ring für
  die Auswahl, helle Ringe für Nachbarn; Nachbarknöpfe wechseln die Auswahl.
  Bilddateien, Tischgeometrie und Kamerapassung unverändert.
- Die Gebietsdaten liegen als unveränderter, vom lokalen Test gegen die
  Projektquelle geprüfter Snapshot `assets/world.json` im Prototyp. Drei
  Beispielarmeen mit je 14 Ländern und wechselnden Truppenzahlen dienen
  ausschließlich der sichtbaren Bedienungsprüfung. Keine echten Partien,
  Konten oder gespeicherten Truppen gelesen oder geändert. Die Oberfläche
  kennzeichnet die Beispielbelegung; keine behauptete Regel-Startaufstellung.
- Länder über ihre Marken oder das nach Kontinenten gruppierte Menü
  auswählbar; noch keine flächigen Treffermasken der Landumrisse. Escape,
  Schließen und Klick auf die freie Szene heben die Auswahl auf. Das Mausrad
  funktioniert auch über Marken, während die Länderanzeige unabhängig
  scrollbar bleibt. Auswählen führt keinen Spielzug aus; echte Züge,
  Truppenänderungen und die Anbindung an den Partiezustand bleiben offen.
- 14 lokale Tests bestanden: acht bestehende Kameraprüfungen und sechs neue
  Prüfungen von Daten, Koordinaten, Beispielbelegung und Rückprojektion aller
  Marken über den Vorbeugeweg. JavaScript-Syntax und `git diff --check`
  erfolgreich. Keine vollständige App-Testsuite erforderlich, da nur der
  getrennte statische Prototyp und Dokumentation geändert wurden.
- Tatsächliche Chrome-Prüfung: alle 42 Marken bei der normalen Fenstergröße
  angeklickt; zusätzlich bei 1365 × 767 Pixeln alle 42 jeweils in Sitzposition
  (32 Grad) und Überblick (82 Grad). Ländernamen, Auswahl und Nachbaranzeige
  beobachtet. Wechsel Alaska–Kamtschatka per Nachbarknopf, Vorbeugen per
  Mausrad über einer Marke und Auswahl im Zwischenwinkel geprüft. Escape
  hebt die Auswahl auf. Alle 42 Länder außerdem bei 390 × 844 Pixeln per
  Menü auswählbar. Keine Browserfehler oder Warnungen beobachtet.
- Prüfbilder und Protokoll unter
  `runtime/conquest-laender-marken-2026-10-24/`. Die Vorschau läuft nur an
  `http://127.0.0.1:54508/` und bleibt für die Nutzerprüfung geöffnet.
  Diese Änderung ist ausschließlich offline geprüft, nicht live aktiviert.
- Abschließender SHA-256-Vergleich: 625 geschützte Dateien einschließlich
  bestehender Projektänderungen und vorbereitetem Fragen-Uploadarchiv
  unverändert. Kartenbild weiterhin mit SHA-256
  `7d239294d81561a8d66f6a703995f48704fdfe73340989520fd53bfb181cea23`.
  Temporäre Browsergrößenvorgabe zurückgesetzt; die normale Fenstergröße
  und der zur Nutzerprüfung geöffnete Tisch bleiben erhalten.

## Conquest – Verstärkungsphase mit kleiner Zugleiste offline eingebaut (24.10.2026)

- Auf ausdrücklichen Nutzerauftrag die Verstärkungsphase im getrennten
  Prototyp `offline-preview/conquest-2-5d-v1/` umgesetzt. Die zuvor erläuterte
  Bildreferenz dient als Ablaufvorlage: Verstärkungsmeldung, Auswahl eines
  eigenen Landes, Mengenwahl, Bestätigen/Abbrechen und gesperrter Weiter-Knopf
  bis zur vollständigen Verteilung. Gestaltung im vorhandenen Holz-/Messingstil.
- Beispielzug: aktive goldene Armee mit sechs fest vorgegebenen Truppen.
  Diese Zahl ist ausdrücklich ein Bedienungsbeispiel, keine Berechnung aus
  Ländergrundwert, Kontinentbonus oder Kartentausch. Keine gespeicherte Partie
  angebunden; nur der Arbeitsspeicher dieses Vorschau-Tabs wird verändert.
- Kompakte untere Zugleiste zeigt Armee, Phase, Restbestand und
  `Weiter zum Angriff`. Mengenwahl per Zahl, Plus/Minus und Schieberegler;
  erst Bestätigen verändert Marke, Länderanzeige und Restbestand gemeinsam.
  Abbrechen/Escape ändern keine Truppen. Nur eigene Länder verstärkbar;
  ungültige Zahlen und Überschreitungen des Vorrats werden ohne Teiländerung
  abgewiesen. Das Beispiel lässt sich über den Kreis-Pfeil erneut starten.
- `Weiter zum Angriff` ist bei jedem positiven Restbestand nativ deaktiviert
  und grau. Bei null wird er grün; sein Klick erreicht die Angriffsphase und
  sperrt weitere Platzierungen. Angriffe selbst bleiben noch nicht enthalten
  und werden als offen gekennzeichnet. Keine vorgetäuschte fertige Kampfphase.
- Einpassung der bestehenden unveränderten Karte berücksichtigt nun die
  tatsächliche Oberkante der Zugleiste. Der gesamte Karteninhalt bleibt in
  Sitz-/Draufsicht oberhalb der Bedienung sichtbar. Frühere untere Mausrad-
  Hinweispille durch die Zugleiste ersetzt und ihre CSS-Regeln entfernt;
  vorhandene Komponentenregeln direkt angepasst. Verweise auf CSS/JS Version 5.
- Ausgangsprototyp vollständig unter
  `runtime/conquest-verstaerkung-2026-10-24/vorher/` gesichert. Nur den
  getrennten Prototyp und Dokumentation erweitert; keine Serververbindung,
  Veröffentlichung oder Änderung von Konten, Ergebnissen oder Nutzungshistorie.
- 21 lokale Tests bestanden: bisherige 14 plus sieben Prüfungen für die
  letzte noch offene Truppe, Eigentum, Mengenbegrenzung, unveränderte fremde
  Armeen, Erhaltung der Gesamttruppenzahl, Phasenwechsel, lokalen Neustart und
  Kartenfreiraum über der Zugleiste. JavaScript-Syntaxprüfungen erfolgreich.
- Tatsächliche Browserprüfung: Verstärkungsmeldung und Mengenwahl sichtbar;
  fremdes Land, Abbrechen und zu große Menge ohne Platzierung geprüft.
  Verteilung 2 nach Alaska, 3 nach Alberta, 1 nach Venezuela beobachtet:
  Restbestand 6 → 4 → 1 → 0, Weiter-Knopf bei 1 weiterhin gesperrt und erst
  bei 0 aktiv. Danach Angriffsphase und Sperre weiterer Verstärkung geprüft;
  Neustart stellt die ursprünglichen Marken und sechs Verstärkungen wieder her.
- Zusätzlicher tatsächlicher Ablauf bei 390 × 844 Pixeln: Auswahl per
  Ländermenü, Abbruch mit Escape, Plus/Minus, Schieberegler bis zur Gesamtmenge,
  Platzierung aller sechs Truppen und Phasenwechsel per Eingabetaste.
  Kein horizontaler Überlauf und keine Browserfehler oder Warnungen beobachtet.
  Sitz- und Draufsicht kontrolliert; temporäre Browsergrößenvorgabe zurückgesetzt.
- Die geöffnete Chrome-Vorschau wurde bereits während der Arbeit vom Nutzer
  bedient; die vollständigen Ablaufprüfungen deshalb in einem getrennten
  lokalen Browser-Tab ausgeführt. Prüfbilder und Protokoll unter
  `runtime/conquest-verstaerkung-2026-10-24/`. Öffentliche Live-Aktivierung
  bleibt außerhalb dieses ausdrücklich offline erteilten Auftrags.
- Abschließender Prüfsummenvergleich: 625 geschützte Projektdateien und
  vorbereitete Uploaddateien unverändert. `git diff --check` erfolgreich.
  Bestehende Chrome-Vorschau geöffnet gelassen; beim letzten lesenden Blick
  befand sich auch der dort vom Nutzer bediente Beispielzug bei null offenen
  Verstärkungen in der Angriffsphase. Kein Zurücksetzen dieses Nutzer-Teststands.

## Conquest – Angriffsphase mit Würfeln und Eroberung offline eingebaut (24.10.2026)

- Auf ausdrücklichen Nutzerauftrag die Angriffsphase ausschließlich im
  getrennten 2,5D-Prototyp erweitert. Der vollständige vorherige Stand liegt
  unter `runtime/conquest-angriff-2026-10-24/vorher/`. Bestehende andere
  Projektänderungen erhalten; keine Serververbindung oder Veröffentlichung.
- Nach vollständig verteilter Verstärkung eigenes Land mit mindestens zwei
  Truppen auswählen. Nur feindliche Nachbarn aus dem bestehenden Weltmodell
  werden als mögliche Ziele orange markiert. Auswahl über Marke, Nachbarknopf
  und Ländermenü gemeinsam; ein anderes eigenes Land wechselt das Ausgangsland.
  Gewählter Angriff erhält einen mit der Brettkamera projizierten Pfeil.
  Alaska–Kamtschatka besitzt zwei gerichtete Kartenrandabschnitte.
- Ein bis drei zulässige Angriffswürfel auswählbar. Jede bewusste Würfelaktion
  löst genau einen Kampfvergleich aus; zufällige Werte stammen unverändert aus
  der lokalen Browser-Kryptozufallsquelle. Sortierte Würfel, Verluste und
  verbleibende Truppen werden sichtbar angezeigt und auf den Marken angewandt.
  Mindestens eine eigene Truppe bleibt zurück; bei Gleichstand gewinnt die
  Verteidigung. Kampfregeln am offiziellen Hasbro-Regelheft, Seiten 8–10,
  geprüft: `https://www.hasbro.com/common/instruct/risk.pdf`.
- Gegner würfeln nur in dieser Einzelspieler-Vorschau automatisch mit der
  größtmöglichen Verteidigungszahl (ein bis zwei). Dies ist keine neue
  verbindliche Mehrspielerregel und ersetzt keine spätere Verteidigerwahl.
- Nach Eroberung wechselt der Besitzer zu Gold. Das vorübergehend noch leere
  eroberte Land muss unmittelbar besetzt werden; bis dahin sind weitere
  Angriffe und Phasenwechsel gesperrt. Mengenwahl verwendet vollständig
  denselben Dialog wie die Verstärkung. Mindestmenge entspricht den zuletzt
  eingesetzten Angriffswürfeln, Höchstmenge lässt eine Truppe zurück. Escape
  oder Abbrechen können diesen Pflichtschritt nicht umgehen.
- Nach Besetzung Besitzer, Farbe, Truppen, Länderzahlen und Angriffsziele
  aktualisiert. Das eroberte Land kann selbst als Ausgangsland dienen.
  `Angriffe beenden` erreicht `Festigen`; Festigen, Zugende, Kartengewinn,
  Kartentausch, Sieg-/Missionsprüfung und gegnerische Züge bleiben offen.
  Die Zugleiste zählt besetzte Eroberungen, keine gezogenen Karten.
- Gemeinsamer Zustandsautomat jetzt `turn-model.js`, gemeinsame Zug-/Mengen-
  Bedienung `turn-controls.js`; die bisherigen Verstärkungsdateien entsprechend
  umbenannt und alle Verweise aktualisiert. Angriffsdialog in `attack.js`.
  Keine zweite Karten- oder Mengenkomposition. Ersetzte Texte und CSS an den
  zuständigen Komponenten konsolidiert; CSS-/JS-Verweise Version 6.
- 30 lokale Tests bestanden, darunter neun neue Angriffsprüfungen: Besitz,
  Nachbarschaft, Würfelgrenzen, alle 36 Einervergleiche, Gleichstände,
  Truppenerhaltung, Eroberung, Pflichtbesetzung und deren Grenzen, Kartenrand,
  wiederholte Aktionen, Rücksetzen und Sperre nach Phasenende. JavaScript-
  Syntax und `git diff --check` erfolgreich. 625 geschützte Projekt-/Upload-
  Dateien per Prüfsumme unverändert; aktive Spiel- und Fragendateien erhalten.
- Tatsächlicher Browserlauf in getrennter lokaler Testansicht: sechs
  Verstärkungen nach Venezuela, danach Angriffsauswahl mit ausschließlich
  Mittelamerika, Peru und Brasilien. Ein-Truppen-Ausgangsland und entferntes
  Ziel blockiert; Abbrechen ohne Truppenänderung. Zufällige angezeigte Würfe
  gegen Brasilien mit den sichtbaren Verlusten unabhängig gegengeprüft.
  Eroberung tatsächlich beobachtet, Pflichtbesetzung und gesperrter Weiter-
  Knopf vor dem Einrücken geprüft. Einrücken von zehn Truppen ließ genau eine
  in Venezuela; Brasilien danach Gold mit zehn Truppen, Länderzahl Gold 15,
  Blau 13 und neuer Angriff von Brasilien möglich.
- Zusätzlich Angriffe beenden und Wiederherstellung der ursprünglichen
  Besitzer im Beispiel-Neustart geprüft. Randverbindung bei 82 Grad mit zwei
  SVG-Pfeilen beobachtet. Bei 390 × 844 Pixeln Landwahl per Menü und ein
  tatsächlicher Einerangriff gegen zwei Verteidigungswürfel, dessen Verluste
  mit den Marken übereinstimmten. Kein horizontaler Überlauf und keine
  Browserfehler oder Warnungen; temporäre Größenänderung zurückgesetzt.
- Nachweise: `runtime/conquest-angriff-2026-10-24/browser-pruefung.json` und
  dortige Prüfbilder. Neue Chrome-Vorschau unter `http://127.0.0.1:54508/`
  geöffnet und zur Nutzerprüfung unmittelbar in der Angriffsphase mit
  Venezuela als Ausgangsland bereitgestellt. Dafür nur die sechs Beispiel-
  Verstärkungen verteilt, noch keinen Kampf in dieser Nutzeransicht gewürfelt.
  Vorherige Nutzer-Vorschau unverändert geöffnet gelassen. Ergebnis ist
  ausschließlich offline geprüft und nicht live aktiviert.

## Conquest – Festigen, Zugende und einmaliger Kartengewinn offline eingebaut (24.10.2026)

- Auf ausdrücklichen Nutzerauftrag den getrennten Prototyp unter
  `offline-preview/conquest-2-5d-v1/` um Festigen, Zugende und Kartengewinn
  erweitert. Vollständige vorherige Fassung unter
  `runtime/conquest-zugende-2026-10-24/vorher/` gesichert. Keine Serververbindung,
  Übertragung oder Veränderung echter Konten, Spielstände und Nutzungshistorie.
- Festigen ist optional und erlaubt genau eine bestätigte Verschiebung pro
  Zug zwischen direkt benachbarten eigenen Ländern. Mindestens eine Truppe
  bleibt zurück, die Gesamtsumme bleibt erhalten. Eigene Ziele sind grün
  markiert; dieselbe Kartenprojektion und derselbe vollständige Mengenwahldialog
  wie bei Verstärkung/Einrücken werden verwendet. Abbrechen verbraucht die
  Aktion nicht; zweite Verschiebung, fremde/entfernte Ziele und ungültige Mengen
  werden ohne Teiländerung abgewiesen.
- `Zug beenden` schließt die Festigungsphase auch ohne Verschiebung ab.
  Bei mindestens einer vollständig besetzten Eroberung genau eine zufällige
  Länderkarte, unabhängig von der Zahl der Eroberungen; ohne Eroberung keine.
  Abschluss und Kartenzuteilung sind atomar im lokalen Zustandsautomaten;
  wiederholte Abschlussaktionen können keine weitere Karte erzeugen.
  Die 42 Länderkarten werden ohne Zurücklegen gezogen. Ein leerer Stapel oder
  ungültiger Ziehwert bricht einen berechtigten Abschluss unverändert ab.
- Gewinnanzeige zeigt die tatsächlich zugeteilte Karte und `+1`. Der kleine
  Kartenknopf öffnet die getrennte Hand der aktuellen Armee. Beide Ansichten
  verwenden dieselbe Kartenkomponente `cards.js`, mit Landname, Kartentyp und
  Ausschnitt der unveränderten aktuellen Brettgrafik. Keine neue Rastergrafik
  generiert und keine alten Karten-/Brettgrafiken wieder als Vorlage eingebaut.
- Nach der Abschlussanzeige bewusste Übergabe an die nächste Armee in der
  Beispielreihenfolge Gold → Rot → Blau; Armeen ohne Gebiete werden übersprungen.
  Besitzer, Truppen und Kartenhände bleiben erhalten, Eroberungszähler und
  einmaliges Festigen beginnen neu. Armeeanzeige, Verstärkungsmeldung,
  Angriffsdialog und Besitzprüfungen folgen der jeweils aktiven Armee.
  Jede erhält weiterhin sechs feste Beispiel-Verstärkungen, keine neue
  Nachschubregel. Manuelle Bedienung auf demselben PC, keine KI oder echten
  Mehrspielersitzungen. Vollständiger lokaler Neustart löscht auch Beispielkarten.
- Bestehende Komponenten konsolidiert: `turn-model.js` mit Phasen-/Kartenlogik,
  `fortify.js` für die Auswahl, `cards.js` als gemeinsame Kartenansicht und
  `turn-controls.js` für dieselbe Zugleiste und Mengenwahl in allen drei
  Situationen. CSS-/JS-Verweise Version 7. Kartentausch, regelgerechte
  Nachschubberechnung, Sieg-/Missionsprüfung und Backend-Anbindung bleiben offen.
- 40 lokale Tests bestanden, darunter zehn neue Prüfungen von Nachbarschaft,
  einmaliger Verschiebung, Truppenerhaltung, übersprungenem Festigen,
  null/einer/mehreren Eroberungen, genau einer Karte, mehrfachen Abschluss-
  versuchen, blockiertem Abschluss vor dem Einrücken, Zugübergabe, Erhalt
  getrennter Hände, Kartenstapel und Neustart. JavaScript-Syntaxprüfungen und
  `git diff --check` erfolgreich. 625 geschützte Projekt-/Uploaddateien per
  SHA-256 unverändert; aktive Spiel- und Fragendateien erhalten.
- Tatsächlicher Browserlauf: Alberta → Alaska als eigene Nachbarn ausgewählt,
  fremdes und entferntes Ziel blockiert, Mengenwahl abgebrochen und anschließend
  sieben Truppen verschoben. Alberta blieb bei einer, Alaska stieg von eins auf
  acht, Gesamtzahl unverändert und zweite Verschiebung gesperrt. Abschluss
  ohne Eroberung gab keine Karte, Übergabe an Rot erhielt den Brettstand.
- Weiterer tatsächlicher Browserlauf mit unveränderten zufälligen Würfen:
  Mittelamerika und Brasilien erobert und besetzt; auch nach beiden Eroberungen
  und zusätzlichem Festigen beim Zugende nur eine Karte. Beobachtete gezogene
  Karte `sibirien`, Hand Gold eins, Anzeige `+1`; keine Karte vor dem Zugende.
  Getrennte Hände und Übergabe über Rot und Blau zurück zu Gold geprüft:
  Rot/Blau sahen jeweils keine Gold-Karte, Gold behielt dieselbe Karte.
- Bei 390 × 844 Pixeln Kartenhand, Ländermenü, Mengenbegrenzung, Festigen per
  Schieberegler und Eingabetaste sowie Zugende geprüft. Ein späterer Gold-Zug
  ohne neue Eroberung erhöhte die bereits vorhandene Hand nicht erneut.
  Keine Browserfehler/Warnungen und kein horizontaler Überlauf beobachtet;
  temporäre Browsergrößenvorgabe zurückgesetzt.
- Nachweise unter `runtime/conquest-zugende-2026-10-24/`, einschließlich
  `browser-pruefung.json`, `laenderkarte-erhalten.png`, `kartenhand-erhalten.png`
  und mobiler Prüfbilder. Neue Chrome-Vorschau unter `http://127.0.0.1:54508/`
  geöffnet und geöffnet gelassen; letzter lesender Blick zeigte `Festigen` und
  eine noch leere Kartenhand. Vorhandene Vorschau-Tabs nicht zurückgesetzt.
  Ergebnis ausschließlich offline geprüft, keine Live-Aktivierung.

## Normale PC-Anwendung für die Server-Ausfallzeit vorbereitet (24.10.2026)

- Aktuellen lokalen Arbeitsbaum und Git-Zuordnung geprüft. Der GitHub-Zweig
  `codex/server-snapshot-2026-10-23` ist über die verbundene GitHub-Abfrage
  weiterhin vorhanden. Der lokale Checkout steht auf `3819398`; zahlreiche
  jüngere lokale Änderungen sind noch nicht eingecheckt. Keine vorhandene
  Änderung zurückgesetzt, kein Commit, Upload oder Serverzugriff ausgeführt.
- Lokale Projekt-Datenbanken ausschließlich lesend geprüft: bisherige
  Vorschaukonten, isolierte Prüfdatenbanken und leere Importdatenbanken sind
  keine aktuelle Sicherung der echten Server-Spielstände. Unter
  `C:\Users\DaBra\Documents\Codex\2026-10-10\ic\work\server-altbestand-2026-10-10\guesstimate-consistent.sqlite3`
  eine echte ältere Sicherung gefunden. SQLite `mode=ro` und `quick_check`
  erfolgreich; 11 Konten, 99 Versuche, letzter reservierter Tag 10.10.2026.
  Nutzer stellt ausdrücklich klar: Dieser Datenstand ist für den Ersatzbetrieb
  zu alt. Datei weder eingespielt noch verändert; aktuelle Spielstände bleiben
  ohne neuere Sicherung beziehungsweise Zugriff auf die Serverdatenbank offen.
- `deploy/run_local.py`, `requirements-local.txt` und
  `Guesstimate-starten.cmd` für die normale Windows-Anwendung hinzugefügt;
  Bedienung und Trennung der Daten in `README.md` dokumentiert. Waitress 3.0.2
  ausschließlich in der ignorierten lokalen `.deps` installiert. Der Launcher
  bindet fest an `127.0.0.1`, deaktiviert Debugmodus und Mailversand und setzt
  vor dem App-Import eine eigene dauerhafte Datenbank unter
  `runtime/pc-local/quiz.sqlite3` sowie einen eigenen Sitzungsschlüssel.
  Keine Vorschaukonten, Ergebnisse oder Bonuspunkte angelegt.
- Anwendung im Hintergrund auf `http://127.0.0.1:8765/` gestartet. Anmeldung
  HTTP 200; `/health` meldete `status: ok`, Release
  `2026.10.24-pool-home-mail-v1`, Mailversand nicht konfiguriert und 265
  vollständige Runden im frischen lokalen Vorrat. Dies ist kein Beleg für
  unverbrauchte Serverfragen: Die lokale Datenbank beginnt ohne Serverhistorie.
  Neue PC-Datenbank und Sitzungsschlüssel nachweislich von Git ausgeschlossen.
- Verbindliche Fragenbibliotheksprüfung und alle 135 vorhandenen Projekttests
  in isolierten lokalen Prüfdatenbanken erfolgreich. Chrome tatsächlich auf
  der lokalen Loginseite geöffnet; Gestaltung, Name, Anmeldefelder und Zugang
  zur Registrierung sichtbar geprüft und Tab für den Nutzer offen gelassen.
  Kein echter Nutzerlogin und keine vollständige Browser-Spielrunde ausgeführt.
- Öffentlicher Ersatzbetrieb noch nicht eingerichtet. Für aktuelle Konten,
  Punkte und Fragenverbräuche fehlt weiterhin eine aktuelle Datenbankkopie.
  Eine neue Übergangsinstanz würde später einen ausdrücklichen Datenabgleich
  benötigen und darf nicht ungeprüft die Serverdatenbank ersetzen. Entwicklung
  lokal fortsetzbar; neueste Conquest-Zugaktionen bleiben vorerst im getrennten
  Prototyp `offline-preview/conquest-2-5d-v1/`. Keine Wiederaufnahme des
  ausdrücklich beendeten automatischen Server-Uploads eingerichtet.

## Lokaler Stormseed-Zugang auf Nutzerwunsch angelegt (24.10.2026)

- Nutzer bittet ausdrücklich um Anmeldung als Stormseed in der neuen
  PC-Anwendung. Vorher lesend bestätigt, dass `runtime/pc-local/quiz.sqlite3`
  noch kein Konto enthält. Konsistente Sicherung vor der Registrierung unter
  `runtime/pc-local-check/before-stormseed-registration.sqlite3` angelegt.
- Über den unveränderten regulären Registrierungsablauf ein neues lokales
  Konto `Stormseed` mit eigener zufälliger PIN angelegt. Kein Serverkonto,
  alter Spielstand oder Vorschauergebnis übernommen; keine bestehende PIN
  geändert. Zugangsdaten bleiben außerhalb des Projektlogs und Git.
- Im bereits vom Nutzer geöffneten In-App-Browser über die normale Anmeldung
  eingeloggt. Die Startseite zeigt tatsächlich Stormseed, Startausrüstung und
  null iKühe. Nachholhinweis geschlossen; keine Quizrunde gespielt.
  Tab für den Nutzer geöffnet gelassen. Sichtnachweis ausschließlich lokal:
  `runtime/pc-local-check/stormseed-angemeldet.png`.

## Entwicklermodus für den lokalen Stormseed aktiviert (24.10.2026)

- Auf ausdrücklichen Nutzerwunsch im angemeldeten lokalen Profil unter
  `http://127.0.0.1:8765/profil` das vorhandene Entwickler-Häkchen aktiviert.
  Bestätigung „Entwicklermodus aktiviert.“ und gesetztes Häkchen tatsächlich
  im In-App-Browser beobachtet. Keine Programmänderung oder Serververbindung.
- Alle vier Sammlungsreiter sichtbar geprüft: 19 Avatare einschließlich
  Startfigur, 14 Pulte einschließlich Startpult, 11 Hintergründe einschließlich
  Standard und 40 Sprüche auswählbar. Keine Ausrüstung gewechselt und keine
  Käufe oder zusätzlichen Punkte angelegt. Profil zur Auswahl geöffnet gelassen.
- Sichtnachweis ausschließlich lokal unter
  `runtime/pc-local-check/stormseed-entwicklermodus.png`. Keine neue Testsuite
  erforderlich; vorhandene Profilfunktion über ihre reguläre Oberfläche bedient.

## Conquest – räumlicher Tisch hinter der normalen lokalen Lobby (24.10.2026)

- Auf ausdrücklichen Nutzerauftrag die neue Tischdarstellung mit der normalen
  Conquest-Lobby unter `http://127.0.0.1:8765/karten/welteroberung/1`
  verbunden. Spielstart und laufender Tisch verwenden dieselbe Lobbyadresse
  und dieselbe lokale Anwendung. Ein zusätzlicher Tischserver ist nicht nötig.
  Keine Serververbindung oder Veröffentlichung; kein Commit und kein Push.
  Vorherige betroffene Dateien, vollständigen Prototyp und eine
  konsistente lokale Datenbankkopie unter
  `runtime/conquest-lobby-integration-2026-10-24/vorher/` gesichert.
- Sichtbare Oberfläche und 2,5D-Szene besitzen eine gemeinsame Implementierung
  unter `offline-preview/conquest-2-5d-v1/`. `table-surface.js` enthält die eine
  Oberfläche; sowohl der isolierte Beispielaufruf als auch die normale App
  verwenden dieselben Kamera-, Marken-, Dialog- und Kartenkomponenten.
  `conquest_table.html` bindet diese ein. Die App liefert nur ausdrücklich
  freigegebene Laufzeitdateien über ihre eigene Adresse aus und lädt die
  Weltdaten aus der gemeinsamen Projektquelle. Keine neue Kartengrafik erzeugt.
- Neue gespeicherte Zugregeln in `conquest_turns.py`: Grundverstärkung und
  vollständige Kontinentboni, Platzieren, Angreifen, Pflichtbesetzung,
  einmaliges direkt benachbartes Festigen, Zugende mit genau einer Karte bei
  Eroberung und Wechsel zur nächsten noch vertretenen Armee. Aktionen laufen
  atomar mit SQLite-Sperre, CSRF-Schutz, Mitgliedschaft, Zugrechten und
  erwarteter Revision. Doppelübermittlung und veraltete Ansichten werden
  abgewiesen. Der Browser würfelt und entscheidet in gespeicherten Partien
  nicht selbst; `remote-turn.js` lädt den bestätigten Zustand nach.
- In normalen Mehrspielerpartien entscheidet die verteidigende Person über
  ein oder zwei zulässige Würfel. Erst anschließend werden beide Würfelreihen
  auf dem Server erzeugt und ausgewertet. Neutrale Armee und lokale Testarmeen
  verwenden die maximal zulässige Verteidigungszahl. Private Hände, gezogene
  Karten und Missionen werden nicht an fremde Spieler übertragen. Regelbasis
  einschließlich Verstärkung, Verteidigerwahl und einmaligem Kartengewinn am
  offiziellen Hasbro-Regelheft erneut geprüft.
- Da aktuell nur Stormseed in Lobby 1 anwesend ist, einen ausdrücklich
  bezeichneten `Entwickler-Test starten`-Knopf ergänzt. Voraussetzung:
  lokale Launcher-Konfiguration, Besitzerkonto, aktives Entwickler-Häkchen,
  Host und genau ein echtes Mitglied. Zwei virtuelle Testarmeen gehören nur
  zu diesem gespeicherten Feldzug; keine weiteren Benutzerkonten entstehen.
  Der Besitzer beginnt und steuert alle Testarmeen abwechselnd. Normale
  Starts benötigen unverändert mindestens zwei echte Mitglieder. Auf einem
  normalen Server ist die zusätzliche lokale Freigabe standardmäßig aus.
- Prüfungen: verbindliche Fragenbibliotheksprüfung erfolgreich; alle 141
  Python-Projekttests einschließlich zwölf Conquest-Tests bestanden. Alle
  40 vorhandenen Tisch-/Kamera-/Zugtests mit Node bestanden. Syntaxprüfungen
  aller eigenen Tischmodule und `git diff --check` erfolgreich. Neue Prüfungen
  decken lokale Entwicklerrechte, virtuelle Plätze ohne neue Konten,
  Persistenz, Revisionen, ungültige Aktionen, fremde Züge, Verteidigerwahl,
  Pflichtbesetzung, Kartengewinn und private Karten ab.
- Ausschließlich die eindeutig zugeordnete lokale Anwendung kontrolliert
  neu gestartet; bestehende Sitzung, Profil und Entwicklermodus erhalten.
  In der tatsächlich geöffneten Lobby 1 den neuen Teststart betätigt:
  42 Länder, drei Armeen mit je 14 Ländern und je 35 Starttruppen,
  Stormseed beginnt mit vier Grundverstärkungen. Verstärkungsmeldung und
  räumlicher Tisch im In-App-Browser tatsächlich gesehen. Die gestartete
  Nutzerpartie bei vier noch zu verteilenden Verstärkungen geöffnet gelassen.
- Für weitergehende Browseraktionen eine konsistente getrennte Kopie dieser
  Partie unter `runtime/conquest-lobby-integration-2026-10-24/ui-test.sqlite3`
  verwendet. Darin vier Verstärkungen nach Mittelamerika: drei auf sieben,
  Rest null und Wechsel erst danach freigegeben. Nach Neuladen weiterhin
  sieben Truppen und null offene Verstärkungen. Zwei echte zufällige Kämpfe
  gegen Venezuela: zuerst Angriff 5/3/2 gegen 6/1 mit je einem Verlust, danach
  6/6/3 gegen 4 mit Eroberung. Pflichtbesetzung mit drei Truppen und einmaliges
  Festigen einer weiteren Truppe tatsächlich ausgeführt. Zugende vergab genau
  die Karte Neuguinea; nach Neuladen dieselbe Karte und derselbe Zugabschluss,
  anschließend Übergabe an Testarmee Rot mit leerer eigener Hand und vier
  Verstärkungen. Keine Browserwarnungen oder Fehler in dieser Prüfkopie.
  Prüf-Tab geschlossen und eindeutig zugeordneten vorübergehenden Prüfprozess
  wieder beendet. Die echte Nutzerpartie durch diese Zugprüfung nicht verändert.
- Sichtnachweise unter `runtime/conquest-lobby-integration-2026-10-24/`:
  `spielstart.png`, `tisch-in-der-app.png` und `test-zugende.png`.
  Abschließender lokaler Healthcheck `status: ok`; öffentlich nichts aktiviert.
  Klassische Gebietswahl, Kartentausch, Kartenübernahme bei Ausscheiden und
  automatische Sieg-/Missionsprüfung bleiben offen. Die ganze Partie ist damit
  noch nicht vollständig fertig; der beauftragte lokale Einstieg von der
  Lobby in den neuen Tisch ist sichtbar und funktionsfähig geprüft.

## Conquest – offizielle Kartentauschwerte recherchiert, feste Auswahl verworfen (24.10.2026)

- Nutzer nimmt seine zwischenzeitliche Auswahl fester Werte nach Symbol
  ausdrücklich zurück und verlangt die Originalwerte aus einer tatsächlich
  recherchierten Risiko-Spielanleitung. Keine Karten-, Zugregel- oder
  Spielstandsänderung aufgrund dieser zurückgenommenen Auswahl ausgeführt.
- Offizielle deutsche Hasbro-Anleitungsseite für Risiko B7404 aufgerufen und
  den dortigen Download geprüft:
  `https://instructions.hasbro.com/api/download/B7404_de-de_risiko.pdf`.
  Gedruckte Seiten 10–11: Drei gleiche oder drei unterschiedliche Symbole
  bilden einen Satz. Der Wert steigt gemeinsam für alle Spieler nach der
  Zahl der eingetauschten Sätze: 4, 6, 8, 10, 12, 15, danach jeweils fünf
  weitere Einheiten (20, 25 usw.). Die Symbolart bestimmt in dieser Fassung
  nicht die Truppenzahl. Die feste Auswahl ist damit keine Vorgabe mehr.
- Gegen die bereits im Projekt referenzierte offizielle klassische
  Sechs-Personen-Anleitung `https://www.hasbro.com/common/instruct/risk.pdf`
  abgeglichen: Dieselbe gemeinsame steigende Tauschfolge auf Seiten 7–8.
  Die recherchierten Fassungen enthalten außerdem Joker, Tausch am Anfang
  des eigenen Zugs und Tauschpflicht bei fünf oder sechs Karten.
- Relevanter Unterschied zur vorausgehenden Nutzerbeschreibung: Diese
  offiziellen Regeln geben zusätzlich zwei Einheiten für ein eigenes Gebiet
  auf einer eingetauschten Karte. Das Land ist darin auch nach dem Aufbau
  relevant. Dieser Befund ist vor einer Umsetzung ausdrücklich zu benennen;
  keine abweichende Hausregel oder Bonusauslegung stillschweigend einbauen.
- In diesem Schritt ausschließlich recherchiert und die Regelbasis
  dokumentiert. Kartentausch, Darstellung und gespeicherte Partie unverändert;
  keine Aktivierung, kein Neustart und kein Serverzugriff.

## Conquest – Original-Kartentausch und sichtbare Symbole lokal eingebaut (24.10.2026)

- Nutzer beauftragt ausdrücklich den lokalen Einbau der recherchierten
  Originalregeln mit steigenden Werten, Jokern und +2-Gebietsbonus sowie klar
  erkennbaren drei Symbolen. Der bisherige gespeicherte Feldzug bleibt erhalten.
  Betroffene Dateien und konsistente Datenbank vor der Änderung unter
  `runtime/conquest-kartentausch-2026-10-24/vorher/` gesichert. Kein Serverzugriff,
  keine Veröffentlichung, kein Commit und kein Push.
- `conquest_cards.py` ergänzt den serverseitigen Bankbetrieb. Die gemeinsame
  Tauschfolge lautet 4, 6, 8, 10, 12, 15, danach jeweils +5. Drei gleiche oder
  drei unterschiedliche Symbole bilden einen Satz; Joker ersetzen jedes
  Symbol. Es werden ausschließlich drei unterschiedliche tatsächlich eigene
  Karten angenommen. Die Bank erhält sie in einem Ablagestapel; ein leerer
  Zugstapel verwendet die gemischten abgegebenen Karten erneut.
- `world.json` enthält nun ausdrücklich die unveränderte bisherige
  Symbolzuordnung aller 42 Gebietskarten und zusätzlich `joker-1`/`joker-2`.
  Vorhandene IDs und Symbole bleiben stabil, insbesondere Japan als Geschütz.
  Das bisherige Weltmodell wurde semantisch unverändert nachgewiesen; nur
  `cardSymbols` ergänzt. Der isolierte Welt-Snapshot entsprechend aktualisiert.
  Alte gespeicherte Partien erhalten die zwei Joker einmalig im regulär
  gespeicherten Folgezustand; vorhandene Hände, Truppen und Phasen werden
  nicht zurückgesetzt.
- Tausch grundsätzlich vor dem ersten Platzieren des eigenen Zugs. Bei fünf
  oder mehr Karten blockieren Pflichttausch und Serverprüfung Platzieren und
  Phasenwechsel bis zur Abgabe eines Satzes. Andere Personen, falsche Phasen,
  ungültige Sätze und doppelte/veraltete Anfragen werden abgewiesen. Zusätzliche
  freie Einheiten erhöhen nur den noch zu platzierenden Vorrat.
- Der +2-Bonus kommt direkt auf ein eigenes Gebiet einer abgegebenen Karte;
  bei mehreren passenden Gebieten wird eines gewählt. Nach dem offiziellen
  klassischen Sechs-Personen-Regelheft insgesamt höchstens zwei solcher
  Bonuseinheiten pro Zug, auch bei mehreren Tauschaktionen. Die frühere
  Beschreibung „Land nur beim Aufbau relevant“ ist damit auf ausdrücklichen
  Nutzerauftrag ersetzt. Klassisches Hasbro-Regelheft, Seiten 7–10, vor
  Umsetzung erneut gelesen und Regeln einschließlich Sonderfall abgeglichen.
- Nach der Pflichtbesetzung des letzten gegnerischen Gebiets werden dessen
  Handkarten übernommen. Bei anschließend mindestens sechs Karten wird der
  Angriff für Pflichttausch unterbrochen, bis höchstens vier übrig sind.
  Danach erhaltene Einheiten platzieren und den Angriff fortsetzen. Bei
  weniger als sechs übernommenen Gesamt-Handkarten bleibt der Tausch bis zum
  nächsten eigenen Zug gesperrt. Andere Hände und Missionskarten bleiben privat.
- Dieselbe Kartenkomponente zeigt jetzt große eigene Vektorsymbole für
  Infanterie, Reiter und Geschütz in Gewinnanzeige und Inventar. Joker zeigen
  alle drei Symbole. Landname und kleiner Kartenausschnitt bleiben vorhanden.
  Keine neue Rastergrafik und keine fremden Symbolassets verwendet. Bestehende
  Komponentenregeln direkt konsolidiert, keine nachträglichen CSS-Gegenblöcke.
- Inventar um Satzwahl, Anzeige des nächsten gemeinsamen Tauschwerts,
  verständliche Tauschpflicht, Jokerprüfung und Gebietsbonus-Auswahl ergänzt.
  Ungültige Kombinationen deaktivieren den Tauschknopf. Jede Übermittlung
  verwendet die bestehende atomare Aktionsroute mit CSRF und Revision; kein
  optimistisches Gutschreiben im Browser. Cachekennung des Tischs jetzt 9.
- Verbindliche Fragenbibliotheksprüfung erfolgreich; alle 157 Projekttests
  bestanden, darunter 28 Conquest-/Kartentests. Alle 43 Node-Tischtests,
  Syntaxprüfungen und `git diff --check` erfolgreich. Prüfungen umfassen
  Wertestaffel, gemeinsame Zählung, alle Satzformen mit Jokern, fremde und
  doppelte Karten, Tauschzeitpunkt, Pflichttausch, Bonusgrenze, Neu-Mischen,
  Vererbung, mehrfachen Soforttausch und Erhalt alter Spielstände.
- In einer ausschließlich lokalen getrennten Datenbankkopie tatsächlicher
  Browserlauf: ungültiger Satz gesperrt; zwei Infanteriekarten plus Joker
  gegen vier Einheiten getauscht; Alberta gezielt als Bonusgebiet gewählt,
  dort fünf auf sieben Truppen. Nach Neuladen acht freie Verstärkungen und
  drei verbleibende Karten nachgewiesen. Reiter, Geschütz und zweiter Joker
  gegen sechs Einheiten getauscht, ohne erneuten +2-Bonus. Insgesamt 14 freie
  Verstärkungen platziert; danach normaler Zugabschluss und Wechsel zu Rot.
  Rot tauschte drei Reiterkarten gegen acht Einheiten; nach Neuladen zwölf
  Verstärkungen und gemeinsamer nächster Tauschwert zehn. Insgesamt weiterhin
  exakt 44 Karten, davon neun abgegeben. Keine Browserwarnungen oder Fehler
  in der getrennten Prüfung.
- Die drei unterschiedlichen großen Symbole, Auswahl, Scrollbedienung und
  Bonuswahl zusätzlich in der normalen Fenstergröße tatsächlich angesehen.
  Keine künstliche Browsergrößenvorgabe gesetzt. Eine eigene Mobilprüfung wird
  nicht behauptet. Prüfbilder und Zusammenfassung liegen unter
  `runtime/conquest-kartentausch-2026-10-24/`, insbesondere
  `drei-symbole-und-kartentausch.png`, `joker-und-gebietsbonus.png` und
  `pruefung.json`. Test-Tab geschlossen und zugeordneten Prüfprozess beendet.
- Die zugeordnete normale lokale Anwendung kontrolliert neu gestartet und
  den echten Feldzug im In-App-Browser neu geladen. Tatsächlich weiterhin
  Stormseed, Zug 1 beendet, zwei Eroberungen und genau die vorhandene Karte
  Japan; nun mit großem Geschützsymbol. Spielzustands-JSON vor und nach
  Aktivierung SHA-256-identisch. Keine Prüfkarten in die Nutzerpartie gelegt.
  Sichtnachweis `echte-partie-neues-symbol.png`; Nutzerpartie geöffnet gelassen.
  Abschließender lokaler Healthcheck `ok`. Kartentausch ist lokal aktiviert
  und sichtbar funktionsfähig geprüft; öffentlich wurde nichts aktiviert.
- Weiter offen: klassische Gebietswahl und automatische Sieg-/Missionsprüfung.

## Conquest – Sieg, Missionen und verständliches Rundenende lokal aktiviert (24.10.2026)

- Nutzer beauftragt die lokale Sieg-/Missionsprüfung ausdrücklich mit Erhalt
  der laufenden Partie. Seine anschließende Klarstellung ersetzt die bisherige
  beschriftete Übergabe: Der Knopf im Abschlussfenster heißt „Runde beenden“.
  Er wechselt in der festen Reihenfolge der Lobbybeitritte zur nächsten Armee;
  ausgeschiedene Armeen werden übersprungen. Keine KI beauftragt oder eingebaut.
- Vorhandene Änderungen erhalten. Betroffene Dateien und konsistente
  Datenbank vor Beginn unter `runtime/conquest-sieg-missionen-2026-10-24/vorher/`
  gesichert. Zusätzlich den inzwischen vom Nutzer weitergespielten aktuellen
  Stand unmittelbar beim kontrollierten lokalen Neustart erneut gesichert.
  Keine Serververbindung, Veröffentlichung, Änderungen an Spielergebnissen,
  Commit oder Push im Rahmen dieses Auftrags.
- Originalregeln erneut tatsächlich in den offiziellen Hasbro-Heften gelesen:
  `https://www.hasbro.com/common/instruct/risk.pdf`, Seiten 10, 12 und 13–14,
  und deutsche B7404-Fassung unter
  `https://www.hasbro.com/common/documents/dad2886d1c4311ddbd0b0800200c9a66/00D3C6D450569047F52AD646F2A6EC69.pdf`,
  Seiten 10–13. Beide erlauben den sofortigen Missionssieg auch durch Hilfe
  eines anderen Spielers beim Vernichten einer Farbe. Keine abweichende
  Wartepflicht bis zum nächsten eigenen Zug und keine 24-Länder-Ersatzregel
  für das Vernichten durch einen Dritten eingeführt.
- Neue gemeinsame serverseitige Prüfung `conquest_victory.py`: alle 42 Länder
  bei Welteroberung, im Zweierspiel nur den Gegner besiegen, neutrale Gebiete
  dürfen bleiben. Alle zwölf vorhandenen Missions-IDs ausdrücklich abgedeckt:
  vollständige genannte Kontinente, mindestens 24 Länder, mindestens 18 Länder
  mit jeweils mindestens zwei Einheiten und Farbmissionen mit eigener Farbe
  als 24-Länder-Ersatzziel. Vorhandene Missionstexte und ausgeloste Aufgaben
  bleiben erhalten. Nicht mitspielende Farben erzeugen keinen Sieg.
- Nach jeder gültigen Aktion prüfen, einschließlich Verstärkung,
  Kartengebietsbonus und Festigen. Eine Eroberung zählt für den Sieg erst
  nach dem vorgeschriebenen Einrücken; kein Ende mit einem unbesetzten Land.
  Lebende Missionsinhaber werden auch außerhalb ihres Zugs geprüft;
  ausgeschiedene Spieler können nicht gewinnen. Bei mehreren durch dieselbe
  Aktion erfüllten Aufgaben gilt aktive Person, dann feste Sitzreihenfolge.
- Sieg, Gewinnername, Grund, aufgedeckte Gewinnmission, Endzeit und letzte
  Zustandsänderung werden in derselben bestehenden Datenbanktransaktion
  gespeichert. Weitere Aktionen werden serverseitig abgewiesen. Andere
  Missionen und Kartenhände bleiben privat. Alte Zustände erhalten notwendige
  Zusatzfelder ohne Neuverteilung, Karten- oder Truppenänderung.
- Gemeinsame Tischkomponente um Gewinnerfenster ergänzt. Alle Beteiligten
  erhalten den Abschluss über die bestehende Aktualisierung. Gewinner und
  Endbrett bleiben nach Neuladen und über „Ergebnis ansehen“ erreichbar;
  abgeschlossene eigene Feldzüge stehen in der Übersicht und blockieren
  keinen neuen Feldzug. Reine Beispielvorschau ohne Lobby bleibt Übungsablauf.
- Abschlussfenster mit Karte heißt nun „Neue Länderkarte“ und erklärt, dass
  die Karte im eigenen Inventar bleibt. Es ist die Belohnung nach Eroberung,
  kein Tausch an einen Mitspieler. Der vorhandene Kartentausch entfernt nur
  ausgewählte Sätze und legt sie auf den Ablagestapel. „Runde beenden“ gibt
  keine Handkarten weiter. CSS an der zuständigen Komponente ergänzt, keine
  überschreibenden Korrekturblöcke; Tisch-Cachekennung jetzt 10.
- Verbindliche Fragenbibliotheksprüfung erfolgreich. Alle 174 Python-
  Projekttests und 43 Node-Tischtests bestanden. Nach abschließender
  Zusammenführung der gemeinsamen Farbzuordnung alle 45 Conquest-Tests
  erneut erfolgreich. Darunter Grenzen 23/24 und 17/18, alle Kontinent-
  und Farbaufgaben, Selbstfarbe, Drittspielerhilfe, ausgeschiedener Inhaber,
  Kartenbonus/Festigen als Auslöser, Pflichtbesetzung, neutrale Zweierarmee,
  Datenschutz, atomare Speicherung, wiederholte Anfragen und feste Zugfolge.
- Tatsächlicher Browserlauf ausschließlich mit getrennter Datenbankkopie:
  neue Länderkarte mit „Runde beenden“, danach Rot → Blau in der vorhandenen
  Reihenfolge; Karte nicht an Blau abgegeben. Welteroberung mit echten
  Zufallswürfen für das letzte Gebiet, noch kein Sieger vor dem Einrücken,
  danach „Stormseed gewinnt!“ und alle 42 Länder. Neuladen, Tisch ansehen und
  erneutes Ergebnisöffnen funktionieren. Mission mit 17 doppelt besetzten
  Ländern plus einer letzten Verstärkung unmittelbar gewonnen; Aufgabe im
  Gewinnerfenster aufgedeckt. Zweite Ansicht zeigte denselben Sieg ohne
  Neuladen über die normale Aktualisierung. Keine Konsolenfehler/Warnungen
  in beiden Prüf-Tabs. Eigene Prüf-Tabs und zugeordneter Prüfprozess geschlossen.
- Prüfbilder, Testausgaben und Datenbankkopie unter
  `runtime/conquest-sieg-missionen-2026-10-24/`, insbesondere
  `runde-beenden-pruefkopie.png`, `welteroberung-sieg-pruefkopie.png` und
  `mission-erfuellt-pruefkopie.png`. Es sind vorbereitete Prüfstände, keine
  Siege in der echten Nutzerpartie.
- Normale lokale Anwendung kontrolliert aktiviert und echte Partie neu
  geladen: weiterhin laufend, Rot in der Angriffsphase, zwei Eroberungen.
  Beim Neustart Revision 53 und vollständiges gespeichertes Zustands-JSON
  vorher/nachher identisch, SHA256
  `7cb6127ad2d909c9e04ada1d6d1b3b7204446fa7630841ecd7bd71dd62c314ed`.
  Neuer Abschlussknopf und Gewinnerkomponente in der tatsächlich geladenen
  Tischseite nachgewiesen. Keine eigene Aktion in der Nutzerpartie ausgeführt.
  Lokaler Healthcheck abschließend `ok`, echte Partie geöffnet gelassen.
- Sieg-/Missionsprüfung lokal aktiviert und sichtbar funktionsfähig geprüft.
  Klassische Gebietswahl bleibt offen; öffentliche Aktivierung nicht erfolgt.

## Conquest – manuelle Startaufstellung nach Länderzuteilung lokal aktiviert (24.10.2026)

- Nutzer möchte nach Zuteilung der Länder selbst über die Besetzung seiner
  Länder entscheiden und wählt ausdrücklich „Reihum jeweils eine Einheit
  setzen“. Dies ersetzt für neue Partien die bisherige zufällige Verteilung
  der gesamten Starttruppen. Die Länder werden weiterhin automatisch
  zugeteilt; eine freie reihum durchgeführte Länderwahl ist ein anderer,
  weiterhin offener Schritt. Laufende Partien bleiben erhalten.
- Aktuellen Arbeitsbaum, Regelunterbau, Start-/Zuglogik und gemeinsame
  Tischbedienung geprüft. Betroffene Dateien und konsistente Datenbank unter
  `runtime/conquest-startaufstellung-2026-10-24/vorher/` gesichert. Vorhandene
  andere Änderungen erhalten; kein Serverzugriff, keine Veröffentlichung,
  keine Konten-, Ergebnis- oder Nutzungshistorienänderung.
- Offizielle klassische Hasbro-Anleitung erneut gelesen:
  `https://www.hasbro.com/common/instruct/risk.pdf`, Seite 5 (Startaufstellung)
  und Seiten 11–12 (Zweier-Sonderregel). Auf jedem zugeteilten Land steht
  zunächst genau eine Einheit. Die übrigen Starttruppen setzen die Spieler
  jeweils einzeln in der festen Sitzreihenfolge auf beliebige eigene Länder.
  Wiederholtes Verstärken desselben Lands ist möglich. Startgesamtzahlen
  bleiben 40/35/30/25/20 bei zwei bis sechs Personen.
- `conquest_setup.py` verwaltet die zusätzliche Phase `setup`, getrennte
  Startvorräte, ursprünglichen Startspieler und automatische Weitergabe nach
  einer Platzierung. Erschöpfte Vorräte werden übersprungen. Im Zweierspiel
  zwei aufeinanderfolgende einzelne eigene Platzierungen, anschließend eine
  einzelne neutrale Platzierung, dann Gegnerwechsel; alle drei Armeen starten
  mit insgesamt 40 Einheiten.
- Eine eigene Einheit darf nur vom aktuellen Spieler beziehungsweise dem
  autorisierten lokalen Entwickler gesetzt werden. Mehrfachmengen, fremde
  oder unbekannte Länder, Angriffe, Kartentausch, Festigen und Phasenwechsel
  werden vor Abschluss der Aufstellung abgewiesen. Bestehende Revision und
  Transaktion verhindern Doppelplatzierungen. Siegprüfung während der noch
  laufenden Startaufstellung gesperrt.
- Erst nach dem letzten nötigen Setzen regulären ersten Zug starten: der
  zuvor ermittelte Startspieler erhält Grundverstärkung und gegebenenfalls
  Kontinentboni. Aufstellung verbraucht keine regulären Züge, zieht keine
  Handkarten und ändert keine Länderbesitzer. Ältere laufende Zustände ohne
  Aufstellungsdaten werden nicht neu verteilt oder in die Startphase versetzt.
- Gemeinsame Zugleiste zeigt „Startaufstellung“, aktiven Spieler und offenen
  Startvorrat. Dieselbe bestehende Mengenkomponente bestätigt genau eine
  Starteinheit; keine zweite Komposition. Zulässige Länder werden über die
  vorhandenen Marken hervorgehoben. Einstieg erklärt Gesamtvorrat und bereits
  besetzte Länder, danach zügiger Wechsel ohne zusätzliche Übergabefenster
  zwischen den einzelnen Platzierungen. Tisch-Cachekennung jetzt 11.
- Lobbytext unterscheidet jetzt „Länderzuteilung“ und die anschließende
  manuelle Truppenaufstellung. Regelunterbau entsprechend aktualisiert.
- Fragenbibliotheksprüfung erfolgreich, alle 182 Python-Projekttests und
  43 Node-Tischtests bestanden; davon 53 Conquest-Tests. Neue Prüfungen decken
  sämtliche Spielerzahlen, vollständige Startvorräte, Platzierungsgrenzen,
  Berechtigungen, Wiederaufnahme, Reihenfolge, unterschiedlich große
  Restvorräte, die neutrale Sonderregel, Doppelanfragen und Übergang zum ersten
  regulären Zug ab. Syntaxprüfungen und `git diff --check` erfolgreich.
- Tatsächlicher Browserlauf in getrennter Datenbankkopie: neue Lobby über
  die Oberfläche erstellt und Entwicklertest gestartet, exakt eine Einheit
  auf jedem der 42 Länder. Abbrechen lässt das Land unverändert. Alle
  63 restlichen Starteinheiten tatsächlich einzeln mit der Oberfläche
  platziert, immer Stormseed → Rot → Blau. Je Armee danach exakt 35 Einheiten,
  weiterhin dieselben Länderbesitzer und leere Hände. Anschließend normaler
  erster Zug von Stormseed mit vier Grundverstärkungen. Neuladen erhält
  Aufstellung und Übergang; keine Browserfehler oder Warnungen beobachtet.
- Belege unter `runtime/conquest-startaufstellung-2026-10-24/`, insbesondere
  `startaufstellung-pruefkopie.png`, `browser-platzierungen.json`,
  `startaufstellung-abgeschlossen.png` und `pruefung.json`. Eigener Prüf-Tab
  und zugeordneter Prüfprozess geschlossen.
- Normale lokale Anwendung kontrolliert neu gestartet und echte Nutzerpartie
  erneut geöffnet: weiterhin Blau in der Angriffsphase. Gespeicherter Zustand
  vor/nach Aktivierung bei Revision 58 exakt identisch, SHA256
  `41105efae060e9205817327c0034b3670a3950ee043cb19583c6f4533379b336`.
  Aktuelle Tischdateien mit Cachekennung 11 im Browser nachgewiesen; keine
  Spielaktion in der echten Partie ausgeführt. Abschließender lokaler
  Healthcheck `ok`. Startaufstellung für neue lokale Partien aktiviert und
  sichtbar funktionsfähig geprüft; laufende Partie geöffnet gelassen.

## Conquest – auf Nutzerwunsch neue lokale Partie gestartet (24.10.2026)

- Nutzer erlaubt ausdrücklich das Beenden der bisherigen Partie und verlangt
  eine neue. Den einzelnen lokalen Entwicklertest Nr. 1 nach Prüfung von
  Besitzer, Entwicklertest-Kennung und genau einer echten Mitgliedschaft
  ohne Sieger als abgebrochen geschlossen; Mitgliedschaft beendet.
  Vollständige Datenbank vorher unter
  `runtime/conquest-neue-partie-2026-10-24/vor-neuer-partie.sqlite3` gesichert.
  Alter Spielzustands-JSON bleibt per SHA256 unverändert erhalten.
- Über die laufende Browseroberfläche neue Lobby Nr. 2 erstellt und
  „Entwickler-Test starten“ betätigt. Geheime Missionen und automatische
  Länderzuteilung beibehalten. Neue Partie tatsächlich in der Startaufstellung
  geöffnet: Stormseed beginnt, 42 Länder mit je einer Einheit, je 14 Länder
  pro Armee und je 21 noch zu setzende Starttruppen. Keine Startplatzierung
  für den Nutzer vorgenommen. Rot und Blau weiterhin virtuelle Testarmeen.
- Sichtprüfung im In-App-Browser und anschließende Datenbankprüfung stimmen
  überein. Screenshot `neue-partie-startbereit.png` und Nachweis
  `neue-partie.json` im selben Laufzeitordner. Neue Partie unter
  `http://127.0.0.1:8765/karten/welteroberung/2` geöffnet gelassen.
  Keine Programmänderung, kein Dienstneustart und kein Serverzugriff.

## Conquest – Starttruppen direkt pro Klick setzen (24.10.2026)

- Auf ausdrücklichen Nutzerwunsch entfällt das einzelne Bestätigungsfenster
  während der Startaufstellung. Ein Klick auf ein zulässiges eigenes Land
  setzt sofort genau eine Einheit über die bestehende gespeicherte Aktion.
  Danach folgt die nächste Armee beziehungsweise der nächste Schritt der
  Zweier-Sonderregel. Alte Bestätigungspfade für die Startphase entfernt;
  normale Verstärkung, Besetzung und Festigen verwenden weiterhin ihre
  gemeinsame Mengenwahl. Startvorräte und Regeln bleiben unverändert.
- Gemeinsame `turn-controls.js` angepasst, keine zweite Oberflächenkomponente
  und kein CSS-Korrekturblock. Während des Speicherns sind weitere
  Startplatzierungen gesperrt. Fehler werden sichtbar zurückgemeldet;
  Truppen werden erst nach Serverantwort aktualisiert. Einstieg und Hinweis
  erklären die unmittelbare Wirkung des Klicks. Regelunterbau aktualisiert.
- Vorherige Dateien und konsistente Datenbank unter
  `runtime/conquest-direkt-setzen-2026-10-24/vorher/` gesichert. Vorhandene
  andere Arbeiten erhalten. Fragenprüfung, sieben Startaufstellungstests,
  alle 43 Node-Tischtests, JavaScript-Syntax und `git diff --check` erfolgreich.
- Tatsächlicher Browserlauf in getrennter Kopie der aktuellen Aufstellung:
  fremdes Land ändert nichts und öffnet kein Fenster; ein Klick auf Grönland
  erhöht Rot von eins auf zwei und wechselt direkt zu Blau. Alle 62 dort
  noch übrigen Startplatzierungen ohne Bestätigung abgeschlossen. Danach
  insgesamt 105 Einheiten und normaler erster Zug mit vier Verstärkungen.
  Normales Verstärken öffnet weiterhin die Mengenwahl. Keine Browserfehler
  oder Warnungen. Prüftab und zugeordneter Prüfprozess geschlossen.
- Änderung ohne Dienstneustart durch die vorhandenen nicht zwischengespeicherten
  Tischdateien aktiviert. Echte Partie Nr. 2 im In-App-Browser neu geladen
  und ausschließlich das einmalige Einstiegsfenster geschlossen. Aktuell Rot
  in der Startaufstellung; kein Bestätigungsfenster mehr geöffnet. Keine
  Starteinheit für den Nutzer gesetzt. Gespeicherter Zustand bei Revision 2
  vor/nach Neuladen exakt identisch, SHA256
  `479c2ccbf5c5b79534b772bf9bca1f8dfcc9b3339a8096ecb8efc8520a755f3b`.
- Sichtnachweise `ein-klick-ohne-dialog.png` (Prüfkopie) und
  `aktuelle-partie-direkt-setzen.png` (echte Partie) sowie `pruefung.json` im
  oben genannten Laufzeitordner. Lokaler Healthcheck abschließend `ok`.
  Direkte Startplatzierung lokal aktiviert und tatsächlich funktionsfähig
  geprüft. Keine Serververbindung oder öffentliche Veröffentlichung.

## Conquest – vollständige Probeläufe und Wiederaufnahmefehler behoben (24.10.2026)

- Nutzer beauftragt ausdrücklich den vollständigen Probelauf vom Start bis
  zum Sieg in einer Kopie sowie das Beheben gefundener Fehler. Echte
  Datenbank konsistent und betroffene Dateien vorher unter
  `runtime/conquest-volltest-2026-10-24/vorher/` gesichert. Zwei getrennte
  Prüfdatenbanken für lange Partien und gezielte Browser-Wiederaufnahme.
  Keine Konten, Ergebnisse oder Spielzustände der normalen Nutzeranwendung
  durch Prüfaktionen verändert; keine Serververbindung oder Veröffentlichung.
- Drei frische normale Partien tatsächlich vom Erstellen/Beitreten der Lobby
  über vollständige Startaufstellung bis zum gespeicherten Sieg durchgespielt.
  Reguläre Flask-Anwendungsrouten und getrennte angemeldete Spielersitzungen,
  keine Entwicklerfreigabe für fremde Züge. Echte zufällige Serverwürfe;
  nach dem Start keine vorbereiteten Bretter, Kartenhände, Missionen oder
  Gewinner eingesetzt. Prüfstrategie wählt ausschließlich erlaubte Aktionen.
- Welteroberung mit drei Personen: 91 Züge, 4.436 gespeicherte Aktionen,
  Stormseed gewinnt alle 42 Länder. Geheime Missionen mit drei Personen:
  103 Züge, 5.092 Aktionen, Stormseed gewinnt mit Asien und Afrika; sämtliche
  betroffenen Länder des Missionssiegs zusätzlich unabhängig nachgeprüft.
  Zweierspiel mit neutraler Armee: 143 Züge, 9.123 Aktionen, Prüfarmee 1 gewinnt.
- Zusammen 18.651 Aktionen, 7.249 Kämpfe, 1.979 Eroberungen und 104 getauschte
  Kartensätze, darunter 15 mit Joker. Gebietsboni, Kartengewinn, Festigen,
  Ausscheiden und Kartenübernahme tatsächlich aufgetreten. Nach jeder Aktion
  Truppenbilanz, gültige Besetzung, Revision und stets 44 eindeutige Karten
  geprüft. Regelmäßig Seiten und private Statuskanäle sämtlicher Spieler
  aufgerufen; keine fremden Hände/Missionszuordnungen übertragen. Fremde und
  doppelte Aktionen abgewiesen, nach Abschluss weitere Spielaktionen gesperrt.
- Ein erster vorsichtiger Strategielauf wurde angehalten, weil die beiden
  verbliebenen Testarmeen einander auswichen und kleine Gebiete wiederholt
  tauschten. Keine verletzte Regelinvariante; er zählt nicht als vollständig
  abgeschlossene Partie. Seine Aktionen und Zustände bleiben unter `world/`
  erhalten. Drei danach frisch gestartete Durchläufe mit entschlossenerer
  legaler Zugauswahl abgeschlossen, Belege unter `world2/`, `missions2/`, `duel2/`.
- Gefundener echter Bedienfehler mit zwei unabhängigen Browser-Sitzungen
  nachgestellt: Angreifer lädt während einer offenen Verteidigungswahl neu;
  nach Eroberung bleibt ein Land mit null Truppen und ausstehender Besetzung,
  aber ohne Einrückfenster stehen. Weitere Aktionen sind zu Recht gesperrt,
  die Bedienung führte jedoch nicht zum notwendigen Pflichtschritt zurück.
- In der gemeinsamen `turn-controls.js` behoben: wartenden Verteidiger klar
  anzeigen und ausstehende eigene Besetzung zentral bei jeder Aktualisierung
  öffnen, sofern weder Kampfergebnis noch Einrückfenster offen sind.
  Bestehendes Kampfergebnis behält seinen Einrückknopf. Keine zweite
  Dialogkomponente, kein CSS-Gegenblock und keine Änderung der Spielregeln.
- Wiederholung im Browser mit einer weiteren tatsächlich ausgespielten
  Eroberung nach Neuladen: Verteidiger wählt seine Würfel, Einrückfenster
  erscheint danach ohne weiteres Neuladen automatisch. Pflichtbesetzung,
  Zugabschluss mit genau einer Karte nach zwei Eroberungen und Übergabe
  an die zweite Sitzung erfolgreich. Keine Browserfehler oder Warnungen.
- Drei gezielte Controller-Regressionstests ergänzt: Wiederaufnahme samt
  Warteanzeige, geöffnetes/geschlossenes Kampfergebnis und Schutz des fremden
  Betrachters. Vorher-Fassung scheitert an zwei dieser Prüfungen, korrigierte
  Fassung besteht alle drei. Alle 182 Python-Projekttests und 46 Node-Tests
  erfolgreich, Fragenbibliotheksprüfung, Syntax und `git diff --check` ebenso.
- Alle drei tatsächlichen Endstände aus der durchgespielten Datenbank im
  Browser geöffnet und Gewinner/Mission kontrolliert. Neuladen erhält den
  Welteroberungssieg. Belege und verständlicher Bericht unter
  `runtime/conquest-volltest-2026-10-24/PROBELAUF.md`, zusätzlich Aktionsprotokolle,
  Zugzustände, `pruefung.json` und die Bilder
  `welteroberung-vollstaendig-gewonnen.png`,
  `missionspartie-vollstaendig-gewonnen.png`,
  `zweierspiel-vollstaendig-gewonnen.png`,
  `wiederaufnahme-fehler-vorher.png` und `wiederaufnahme-behoben.png`.
- Korrektur über die vorhandenen nicht zwischengespeicherten Tischdateien
  lokal aktiviert und echte Partie Nr. 2 neu geladen. Weiterhin Rot beim
  Verstärken, sechs Einheiten offen. Vollständiger gespeicherter Zustand
  vor/nach Aktivierung bei Revision 102 exakt identisch, SHA256
  `520951e8877d3d9b034f3af712b542d1f6b363a0dd6786606eb390a8b6d9f05f`.
  Keine eigene Spielaktion in der Nutzerpartie ausgeführt. Prüftabs und
  zugeordnete Prüfprozesse geschlossen, Nutzerpartie geöffnet gelassen.
  Abschließender lokaler Healthcheck `ok`. Kein Dienstneustart erforderlich.


### 2026-10-24 – Lokal: Conquest-Lobby, Rückkehr und gemeinsamer Abschluss

- Nutzerentscheidung: Auch beim ausdrücklichen Verlassen einer laufenden
  Partie bleiben Platz und Armee für eine spätere Rückkehr erhalten. Keine
  Neutralisierung oder Entfernung der Armee. Beim Verlassen des Hosts übernimmt
  der nächste anwesende Spieler in ursprünglicher Sitzreihenfolge. Verlässt die
  letzte Person die Lobby, wird sie geschlossen; zusätzlich kann der Host die
  Lobby ausdrücklich für alle beenden.
- Den vorhandenen Weg Guesstimate → Tabletop Connection → Conquest ausgebaut.
  Gemeinsame Conquest-Kachel für beide bestehenden Tabletop-Ansichten; keine
  zusätzliche Spielauswahl unter dem Startseiten-Karussell. Feldzugübersicht und
  Lobby im warmen Spielzimmer mit bestehender Hintergrundgrafik gestaltet.
  Vorhandene gemeinsame `player_identity`-Komponente für die echten Mitglieder
  und deren ausgerüstete Avatare/Schilder wiederverwendet. Keine kopierte
  Innenkomposition. Zuständige `conquest-lobby.css` konsolidiert ersetzt.
- Lobby zeigt Namen, tatsächliche Teilnehmer, Sitzfarben, Reihenfolge, Host und
  reservierte Plätze. Host kann Namen und Siegziel automatisch speichern und
  gemeinsam starten. Gastsicht aktualisiert sich. Die unabhängigen Wünsche für
  Karten, Figuren und Würfel bleiben erhalten; das Gestaltungsmenü erklärt
  ausdrücklich, dass der aktuelle Tisch die klassische Ausstattung verwendet.
  Conquest-Regeln über den bestehenden Regeln-Knopf der Hauptnavigation verfügbar.
- Laufender Tisch führt über „← Lobby“ in seine eigene Lobby. Rückkehr aktiviert
  dieselbe Mitgliedsnummer und dasselbe Beitrittsdatum; Länder, Truppen, Karten,
  Missionen und laufender Zug bleiben vollständig unverändert. Fehlt gerade der
  aktive Spieler oder der Verteidiger eines offenen Angriffs, werden Aktionen
  bis zu dessen Rückkehr gesperrt und der Grund angezeigt. Fremde können einer
  gestarteten Partie nicht neu beitreten. Ein ehemaliger Host erhält bei
  Rückkehr nicht automatisch wieder die Hostrolle.
- Nach Sieg: „Tisch ansehen“, „Nochmal spielen“ und „Beenden“. Nur der Host
  eröffnet über „Nochmal spielen“ die Vorbereitung in derselben Lobby, ohne
  anwesende Teilnehmer zu verlieren oder abwesende automatisch anzumelden.
  Abgeschlossener Zustand wird einmalig in `conquest_game_history` aufbewahrt.
  Erst der folgende normale Spielstart erzeugt eine neue Startaufstellung.
  Laufende Partien lassen sich nicht über den Wiederholungsknopf zurücksetzen.
  „Beenden“ verlässt individuell; Hostwechsel und Schließen beim letzten
  Teilnehmer gelten auch hier. Alle Tische beobachten den Lobbyzustand nach
  Spielende weiter, damit Wiederholung und Schließen gemeinsam sichtbar werden.
- Getrennte SQLite-Testkopie unter
  `runtime/conquest-lobby-umfeld-2026-10-24/` verwendet. Zwei unabhängige
  Browser-Sitzungen: Einstieg von Guesstimate, Name/Siegziel speichern,
  Mehrspielerstart, Tisch/Lobby-Wechsel, Host verlassen, reservierten Platz und
  Warteanzeige in der anderen Sitzung, Rückkehr und unveränderter gesamter
  Spielzustand geprüft. Der neue Host bleibt nach Rückkehr im Amt.
- Ausschließlich in dieser Kopie einen vorbereiteten abgeschlossenen Endstand
  für die Abschlussbedienung verwendet; dies ist kein weiterer vollständig
  ausgespielter Probelauf. Gewinneranzeige in beiden Sitzungen, Wiederholung
  durch neuen Host, automatische gemeinsame Rückkehr, Erhalt aller drei
  Teilnehmer und genau ein archiviertes Ergebnis geprüft. Neue Partie mit
  geänderten Einstellungen gestartet; Schließen durch Host führt auch den
  anderen laufenden Tisch automatisch zur Übersicht. Keine Browserfehler oder
  Warnungen. Prüfansichten und zugeordneter Prüfprozess danach geschlossen.
- Acht neue Python-Prüfungen für Hostwechsel, Rückkehr, wartenden Verteidiger,
  Hostrechte, Schließen, Wiederholung, Archivierung, Schutz laufender Partien,
  CSRF und gemeinsame Einstellungen. Drei neue Node-Prüfungen für Beobachtung
  nach dem Sieg, Weiterleitung beim Schließen und Wiederholung/Verlassen mit
  aktueller Revision. Alle 190 Python-Projekttests und 49 Node-Tests erfolgreich.
  Bestehende Navigationstest-Erwartung für den neuen Erstellen-Knopf auf dessen
  Formularziel umgestellt. Fragenbibliotheksprüfung, Syntax und Diffprüfung
  ebenfalls erfolgreich. Letzte acht Lobbyprüfungen nach Optimierung der
  Übersichtssignatur erneut bestanden; reine Spielzüge laden die Übersicht
  nicht mehr ohne sichtbare Änderung neu.
- Lokal auf 127.0.0.1:8765 aktiviert. Vor Neustart den zugehörigen Prozess und
  Port geprüft, unmittelbar nach Anhalten konsistente Sicherung
  `vor-aktivierung.sqlite3` und Zustandsmanifest erstellt. Alle Lobby- und
  Mitgliedschaftszeilen nach Neustart und Browserkontrolle exakt identisch.
  Echte Partie Nr. 2 weiterhin `playing`, Revision 102, Rot beim Verstärken,
  sechs offene Einheiten. Unveränderte Zustands-SHA256
  `520951e8877d3d9b034f3af712b542d1f6b363a0dd6786606eb390a8b6d9f05f`.
  Auch Partie Nr. 1 und sämtliche Mitgliedschaften unverändert. Keine eigene
  Spielaktion in der Nutzerpartie ausgeführt.
- Aktive Lobby im Browser sichtbar geprüft, von dort den echten gespeicherten
  Tisch mit sechs Verstärkungen geöffnet und wieder in die Lobby navigiert.
  Lobby zum direkten Weiterspielen geöffnet gelassen; Screenshot
  `runtime/conquest-lobby-umfeld-2026-10-24/lobby-lokal-aktiv.png`.
  Abschlussbericht `LOBBYPRUEFUNG.md` im selben Verzeichnis. Abschließender
  lokaler Healthcheck `ok`. Kein Serverzugriff, keine Veröffentlichung oder
  Änderung von Konten, Ergebnissen oder Zugangsdaten auf dem Live-Server.


### 2026-10-24 – Gewünschte PIN für den lokalen Stormseed-Zugang

- Auf ausdrücklichen Nutzerwunsch ausschließlich die PIN des vorhandenen
  lokalen Kontos `Stormseed` (Benutzer-ID 1) in
  `runtime/pc-local/quiz.sqlite3` geändert. Als regulären Werkzeug-Passworthash
  gespeichert; keine Klartext-Zugangsdaten im Projektlog oder Git abgelegt.
- Unmittelbar davor konsistente SQLite-Sicherung im ignorierten Verzeichnis
  `runtime/pc-local-check/local-login-20261024/` angelegt. Alle Tabellen direkt
  vor/nach PIN-Änderung logisch identisch, nur `users.pin_hash` ausgenommen.
  Auch nach Anmeldeprüfung sämtliche fachlichen Datensätze identisch; die
  normale Anmeldung schreibt lediglich interne SQLite-Sequenzzähler fort.
  Entwicklermodus, Ausrüstung, Punkte, Verlauf und Conquest-Partien erhalten.
- Normale Anmeldung mit Spielername und gewünschter PIN über `/login` am
  tatsächlich laufenden lokalen Dienst erfolgreich; authentifizierte
  Startseite bestätigt. Keine Programmänderung und kein Neustart erforderlich.
- Nutzer-Browser anschließend regulär abgemeldet und auf der sichtbaren
  Loginseite belassen, damit der Nutzer sich selbst anmelden kann. Dies
  verändert keine Lobby-Mitgliedschaft. Kein Serverzugriff oder Datenimport.
  Frühere Serverkonten und -Scores bleiben ohne aktuelle Sicherung weiterhin
  nicht in diese lokale PC-Datenbank übernommen.


### 2026-10-24 – Offline: games collection, Spielgruppen und gemeinsame Oberflächenvorgaben

- Nutzer beauftragt ausschließlich die Punkte 1 bis 3 des Konsistenzplans: Navigation/Farben/Hintergründe, Regeln ohne Seitenwechsel und Brettspiel-Untergruppe. Zusätzlich ersetzt der sichtbare Name `games collection` den früheren Namen `tabletop connection`. Alle Buttons und Spielnamen erscheinen kleingeschrieben; normale Texte, Sätze und vom Nutzer vergebene Namen bleiben davon getrennt. Diese ausdrückliche neue Benennung ersetzt die früheren Namensvorgaben. Interne Endpunkte und bisherige Spieladressen bleiben erhalten.
- Frühere Rückfragen sind entschieden: Guesstimate Party behält seinen eigenen Regeltext. Perfect behält seine Anordnung mit Einstellungszettel und Startbuzzer. Die Punkte 4 bis 6 des Plans, insbesondere neue Spielerfenster, Zusatzflächen und ein gemeinsamer Lobby-Aufbau, sind in diesem Schritt nicht umgesetzt.
- Vorhandene lokale Änderungen vor Beginn erfasst: Prüfsummen für 720 Projektdateien; betroffene bestehende Dateien und eine konsistente lokale Datenbankkopie unter `runtime/consistency-20261024/` gesichert. Bestehende andere Änderungen nicht zurückgesetzt. Keine Serververbindung, Übertragung, Veröffentlichung, Commits oder Pushes ausgeführt.
- Das aktive Navigationsgrün an die gemeinsame Farbe `#d8ff42` gebunden; die beiden widersprüchlichen früheren Aktiv-Farbregeln ersetzt beziehungsweise entfernt. `--variant-a-acid` verwendet denselben Grundwert. Die gemeinsame Kleinschreibung steht einmalig in `static/ui-conventions.css` und wird auch von den eigenständigen Perfect- und Conquest-Ansichten geladen. Statische Buttontexte und Spielnamen entsprechend angepasst; die Profilfenster-Innenkomposition und Spielmechaniken bleiben erhalten.
- `games collection` unter der bestehenden Adresse `/karten` zeigt drei Zugänge: `zu den kartentischen`, `zu den würfeltischen`, `zu den brettspielen`. Die neue, angemeldeten Spielern vorbehaltene Adresse `/karten/brettspiele` verwendet die vorhandene gemeinsame Gruppenvorlage, denselben Hintergrund wie die Sammlung und die Überschrift `brettspiele`. Darin stehen die vorhandenen Perfect- und Conquest-Kacheln. Perfect-Rücklink und Conquest-Spielweg berücksichtigen diese Zwischenebene.
- Gemeinsame Hintergrundregeln in `card-table.css` konsolidiert. Kartenübersicht und Kartentisch-Lobby verwenden `card-tables-background-v1.png`; Sammlung und Brettspiele verwenden `carousel-playtable-v1.png`; die Würfeltischgruppe behält ihre Würfeltischkulisse. Persönliche Guesstimate-Hintergründe sowie die Hintergründe innerhalb der Spielerfenster bleiben erhalten. Die Sammlungsnavigation bleibt auf allen zugehörigen Gruppen- und Spielübersichten aktiv.
- Profil und Shop besitzen nun denselben direkt öffnenden Guesstimate-Regeldialog wie die Hauptseite. Der frühere Link zur Startseite mit `?regeln=1` entfällt. Party und Spiele behalten ihre vorhandenen Regeltexte. Die gemeinsame Regelsteuerung bedient alle vorhandenen Auslöser, einschließlich des zusätzlichen Knopfs in der Mäxchen-Spielansicht; wiederholtes Öffnen ist abgesichert.
- Ausschließlich die eindeutig über Port, Prozess und Startbefehl zugeordnete lokale Anwendung auf `127.0.0.1:8765` neu gestartet. Unmittelbar nach dem Anhalten vor der Aktivierung zusätzliche konsistente Sicherung und Tabellenmanifest angelegt. Nach Aktivierung und abschließender Kontrolle sind alle fachlichen Tabellen, einschließlich Konten, Fragenverlauf und gespeicherter Conquest-Partien, logisch identisch. Nur der interne SQLite-Sequenzzähler änderte sich durch reguläre Anwendungsaufrufe. Keine eigene Spielaktion in einer Nutzerpartie ausgeführt.
- Prüfungen: alle 192 Python-Projekttests erfolgreich; verbindliche Fragenbibliotheksprüfung, JavaScript-Syntaxprüfung und `git diff --check` erfolgreich. Die Regelauslöser zusätzlich mit zwei unabhängigen Knöpfen, erneutem Öffnen und Schließen geprüft. 18 reguläre lokale HTTP-Seitenaufrufe mit Registrierung und Kartentisch-Lobbyerstellung ausschließlich in getrennter Datenbankkopie erfolgreich. Gruppen, Spieleinstiege, Rückwege, Regeltexte und die Zugriffssperre der Brettspielgruppe geprüft. Frühere Beschriftungserwartungen in bestehenden Tests an die ausdrücklich gewünschte Schreibweise angepasst.
- Tatsächlich laufende lokale Anwendung: Health `ok`; ausgelieferte `ui-conventions.css`, `rules.js`, `card-table.css` und `quiz-arena.css` per SHA-256 identisch mit den neuen lokalen Dateien; neue Brettspieladresse ohne Sitzung erwartungsgemäß Login-Weiterleitung. Im authentifizierten Browser die Sammlungsseite mit drei Gruppen, Titel `games collection`, Hintergrund `carousel-playtable-v1.png`, aktivem Grün `rgb(216, 255, 66)`, kleingeschriebenen Bedienelementen und ohne horizontalen Überlauf nachgewiesen.
- Offene Grenze der Sichtprüfung: Browser-Screenshots liefen in Timeout. Beim anschließenden Versuch der sichtbaren Fensterprüfung stoppte Computer Use, weil die aktuelle Windows-Browseradresse nicht sicher genug zugeordnet werden konnte. Danach keine weiteren Computer-Eingaben und kein Wechsel zu einer anderen Fernsteuerung. Vollständige visuelle Prüfung der Brettspiel-Unterseite, der Profil-/Shop-Regelfenster, des Kartentisch-Lobbyhintergrunds und kleiner Fenster bleibt offen. Die HTTP- und automatisierten Prüfungen ersetzen diese Sichtprüfung nicht. Status: lokal eingebaut und aktiviert, vollständige visuelle Offline-Abnahme noch nicht getan; öffentlich nichts aktiviert.
- Nachweise ausschließlich lokal unter `runtime/consistency-20261024/`: `tests-final.log`, `http-check.json`, `active-app-check.json`, `browser-check.json`, `before-activation-data.json`, `final-data.json` und gesicherte Ausgangsdateien/Datenbank. Diese Laufzeitdateien sind von Git ausgeschlossen.


### 2026-10-24 – Offline: gemeinsames Profilfenster mit Pultanzeigen und Zusatzfläche

- Nutzer beauftragt Punkt 4 des Konsistenzplans ausdrücklich lokal: gemeinsamer Spielerbaustein mit einheitlichen Pultanzeigen und anpassbarer Fläche darunter. Keine Serververbindung, Übertragung, Veröffentlichung oder Änderung an Spielregeln und gespeicherten Partien. Vorhandene Änderungen erhalten; 721 Projektdateien vor Beginn per Prüfsumme erfasst, betroffene Dateien und konsistente lokale Datenbank unter `runtime/profile-window-20261024/` gesichert.
- `templates/_profile_window.html` erweitert: zwei gemeinsame Pultfelder für Name und Wert mit Beschriftung/Einheit und optionalem Symbol, gemeinsame Statusanzeige mit fünf Darstellungen sowie Zusatzfläche für standardisierte Werte oder einen Jinja-Inhaltsblock. Avatar, Pult, Hintergrund und Spruch kommen weiterhin aus der Profilausrüstung. Bestehende iKuh-/Shop-Aufrufe, Pokale und Perfects bisheriger `game_points`-Aufruf bleiben kompatibel; ausdrücklich übergebene Spielewerte führen nicht zum Shop.
- Die Zusatzfläche ist unabhängig von der 43:57-Szene: `auto` wächst mit dem Inhalt, `compact`, `standard` und `expanded` bieten drei proportionale Höhen mit eigenem Scrollbereich. Optional kann eine feste Pixelhöhe vorgegeben werden; null blendet die Fläche aus. Inhalte werden automatisch maskiert, unbekannte Größen-/Statusangaben fallen auf die gemeinsame Standarddarstellung zurück. Eigene Karten und Aktionen können später denselben Inhaltsblock verwenden; die Datenfreigabe bleibt Aufgabe des Spiels.
- Sichtbare Grundimplementierung konsolidiert: `static/profile-window.css` enthält genau eine Szenenkomposition und die unveränderten Feldkoordinaten aller 14 Pulte. Vollständig ersetzte Grund-, Gegen- und Mobilregeln aus `quiz-arena.css`, `profile-stage-v1.css`, `typography-v1.css` und dem Perfect-Szenenoverride entfernt. Seitenbezogene Regeln betreffen weiterhin nur den äußeren Rahmen. Basisvorlage und Perfect laden dieselbe neue Komponentendatei.
- `profile-stage-v1.js` passt beide Beschriftungsfelder automatisch an, auch bei langen Namen/Zahlen, nach Textänderungen und bei nachträglich eingefügten Fenstern. Ein zunächst leeres Dokument bleibt funktionsfähig. Größen- und Inhaltsänderungen werden zusammengefasst verarbeitet; entfernte Felder werden nicht weiter beobachtet. Keine zweite HTML-Implementierung im Skript angelegt.
- Verwendung und Übergabeformat unter `docs/PROFILE_WINDOW.md` dokumentiert, einschließlich Status, Werten, variabler Zusatzfläche, eigenen Inhaltsblöcken und Aktualisierung. Der gemeinsame Baustein ist bereit; ein neuer Lobby-Aufbau und die weitere spielweise Anbindung aus den Punkten 5 und 6 wurden nicht vorgezogen. Perfect behält seine vorhandene Zettel-/Buzzer-Anordnung.
- Die normale lokale Anwendung über automatisch neu geladene Vorlagen und statische Dateien aktualisiert; kein Neustart und keine eigene Spielaktion erforderlich. Im authentifizierten lokalen Profil vor/nach der Änderung dieselben Szenenmaße und relativen Positionen von Hängeplakette, Avatar, Pult, Name und Wertefeld gemessen: maximale Abweichung exakt null. Avatar-/Pultgrafiken und Profilausrüstung unverändert.
- Separate interaktive Vorschau auf `http://127.0.0.1:8766/` erstellt. Sie verwendet eine eigene Datenbankkopie, ausschließlich Beispiel-Spielwerte und Beispielkarten sowie das unveränderte gemeinsame Makro. Nur an 127.0.0.1 gebunden; sie liefert die Vorschau und öffentliche statische Assets aus. Normale Anwendung bleibt auf Port 8765. Vorschau für den Nutzer geöffnet gelassen.
- Tatsächliche Browserprüfung: alle 14 Pulte mit einem 24 Zeichen langen breiten Namen und neunstelliger Zahl ohne Textüberlauf; alle Bilder geladen. Zusatzflächen kompakt, normal, groß und automatisch per Oberfläche gewechselt; Szenenhöhe dabei konstant 368,2118 Pixel, Beginn der Zusatzfläche jeweils exakt an der Szenenunterkante. Fensterbreiten 160, 280 und 430 geprüft; nach automatischer Textanpassung kein Feld- oder Seitenüberlauf. Nachträgliches Fenster sowie auf einer eigenen Prüfansicht das erste Fenster eines anfangs leeren Dokuments erfolgreich eingefügt. Temporäre Breitenänderung auf 280 zurückgestellt; keine Browser-Viewportvorgabe verwendet.
- Eine Browseraufnahme der echten Komponenten tatsächlich angezeigt und visuell kontrolliert. Nachfolgende Versuche, eine weitere Aufnahme als Datei zu sichern, liefen in Screenshot-Timeouts; deshalb keine gespeicherte Bilddatei behauptet. Bedientest, DOM-Messungen und funktionsfähige lokale Vorschau liegen unabhängig davon vor. Zusätzliche Prüftabs geschlossen, Vorschautab erhalten.
- Prüfungen erfolgreich: alle 197 Python-Projekttests einschließlich fünf neuer Verhaltenstests für Legacy-/Perfect-Werte, freie Pultfelder/Status, Inhaltsblöcke, Größen/Nullhöhe und sichere Textdarstellung. Nach der letzten Nullhöhen-Präzisierung zusätzlich die sieben gezielten Komponenten-/Bestandstests erneut bestanden. Fragenbibliotheksprüfung, JavaScript-Syntax und `git diff --check` erfolgreich. Lokaler Healthcheck `ok`; ausgelieferte Komponenten-/Profil-/Arena-/Typografiedateien per SHA-256 identisch zu den lokalen Dateien.
- Abschließender rein lesender Tabellenvergleich: sämtliche 29 Tabellen der normalen lokalen Datenbank gegenüber der konsistenten Sicherung logisch identisch, einschließlich Konten, Profilausrüstung, Spielstände und Nutzungshistorie. Keine aktuelle oder frühere Nutzerpartie verändert. Nachweise in `runtime/profile-window-20261024/`: `tests-final.log`, `tests-targeted.log`, `verification.json`, `active-app.json`, `before-data.json`, `after-data.json` und gesicherte Ausgangsdateien. Keine öffentliche Aktivierung.


### 2026-10-25 – Offline: gemeinsamer Lobby-Aufbau

- Nutzer beauftragt Punkt 5 ausdrücklich offline. Perfect behält Einstellungszettel und Startbuzzer an den bisherigen Stellen. Vorhandenen Arbeitsstand vor Änderungen erfasst: 724 Projektdateien per Prüfsumme, betroffene Dateien und konsistente Sicherung der normalen lokalen Datenbank unter `runtime/lobby-layout-20261025/`. Keine Verbindung zum Projektserver, keine Übertragung, Veröffentlichung oder Änderung an Spielregeln.
- Genau eine Standard-Lobbyvorlage `templates/_lobby_room.html` mit `static/lobby.css`: Name und Belegung oben, gemeinsame Profilfenster links, Einstellungen und Spielstart rechts, Austritt darunter. guesstimate party, playtable, würfeltisch, kniffel, mäxchen und stormseed´s conquest verwenden diese Vorlage. Unter 900 px stehen die Einstellungen unter den Spielern. Vollständig ersetzte Lobbyregeln aus den bisherigen Karten-, Würfel-, Party-, Conquest- und Profil-Styles entfernt; Übersichten und laufende Spieltische behalten ihre Gestaltung.
- `lobby_view.py` ergänzt nur die Anzeige durch einen gemeinsamen lesenden Abruf der aktuellen Profilausrüstung. Avatar, Pult, Hintergrund und Spruch stammen aus dem Profil; keine neue Ausstattungskopie oder Kontowährung gespeichert. Im gemeinsamen Pultfeld stehen Host/Mitspieler/Testarmee, in der Zusatzfläche Anwesenheit oder reservierter Platz. Spielreihenfolge und Mitgliedsdaten bleiben unverändert.
- Host-Einstellungen und Gast-Zusammenfassungen stehen an derselben Stelle. Ein gemeinsamer Startknopf lautet `spiel starten`; keine neue Bereit-Pflicht. Bisherige Startbedingungen erhalten, insbesondere mindestens zwei Personen für mäxchen und conquest. Party behält Host-Entfernen, conquest Reihenfolge, Armeefarben, virtuelle Testarmeen, Rückkehrplätze, Wiederholung, Ergebnis- und Schließaktionen.
- Ein gemeinsamer Browserablauf `static/lobby.js` übernimmt Statusaktualisierung, nacheinander gespeicherte vollständige Formularstände und Start erst nach abgeschlossenen Speicherungen. Eigene Speicherungen laden die nächste Eingabe nicht mehr weg. Zahlen- und Namenseingaben werden auch ohne vorherigen Fokuswechsel übernommen. Bei Speicherfehler bleiben Formular und Eingaben für einen erneuten Versuch erhalten; weggefallene Mitgliedschaft bzw. geschlossene Lobbys führen zur passenden Übersicht. Alte Lobby-Steuerungen aus den Spielskripten entfernt; deren übrige Spiel-/Übersichtsabläufe erhalten und Dateiversionen angepasst. Conquests Entwicklertest-Startknopf bleibt als ursprünglicher Formularauslöser erhalten.
- Wiederverwendung und Schnittstellen für neue Spiele in `docs/LOBBY_LAYOUT.md` dokumentiert. Perfects `nerd_mode.html`, `stormseeds-perfect.css` und `stormseeds-perfect.js` sind gegenüber der Sicherung bytegleich. Zettel, Buzzer und bisherige Bereitschaftsanzeige in Host- und Gastansicht zusätzlich tatsächlich im Browser gesehen. Die weitere Avatar-/Informationsanbindung innerhalb laufender Spiele aus Punkt 6 bleibt offen.
- Vollständige Python-Prüfung: alle 201 Tests bestanden, einschließlich vier neuer Prüfungen für den gemeinsamen Aufbau, aktuelle Profile, Beitritt/Austritt, Mindestbesetzung, Gast-/Hostbereiche und Perfect-Ausnahme. Nach den letzten Status-/Übersichtsattributen weitere 13 gezielte Prüfungen bestanden. Drei zusätzliche JavaScript-Verhaltensprüfungen für schnelle Folgeeingaben/Startreihenfolge einschließlich Entwicklertest-Auslöser, Fehler mit erneutem Versuch sowie geschlossene Gastlobby bestanden. Fragenbibliotheksprüfung, JavaScript-Syntaxprüfungen und `git diff --check` erfolgreich.
- Eigene lokale Prüfanwendung mit ausschließlich Testspielern und eigener Datenbank auf 127.0.0.1:8767 verwendet; keine echte Nutzerpartie bedient. Alle sechs Standardlobbys im Browser geprüft. Host-/Gastoptionen bei Party, Karten, Würfeln und Conquest abgeglichen. Kartentisch sichtbar mit 104 Karten und 789 Startpunkten gestartet, Würfeltisch mit fünf verdeckten Würfeln, mäxchen mit drei Leben, conquest mit gewählter Welteroberung. Alle sechs Starts zusätzlich in der Testdatenbank bestätigt. Separate schmale Einbettungen mit 390/800 px Rahmenbreite (373/783 px Dokumentbreite wegen Scrollbalken) geprüft: eine Spalte, Einstellungen unter den Spielern, kein seitlicher Überlauf; Profilfenster proportional skaliert. Die Browser-Größenvorgabe hatte keine messbare Wirkung und wurde zurückgesetzt; Größenbeleg stammt ausschließlich aus den tatsächlichen Einbettungen. Desktopaufnahme unter `runtime/lobby-layout-20261025/lobby-desktop.png` gespeichert und visuell geprüft.
- Normale PC-Anwendung mit unverändertem lokalen Datenbankpfad und Sitzungsschlüssel neu gestartet. Neuer Prozess 20232 über `deploy/run_local.py --port 8765`; Healthcheck und neue Lobby-Dateien liefern lokal HTTP 200. Abschließender lesender Datenvergleich: alle 28 Inhaltstabellen einschließlich Konten, Profilausrüstung, Login-Einträgen, Ergebnissen, Spielständen und Nutzungshistorie unverändert. Einzige Abweichung der insgesamt 29 Tabellen: `sqlite_sequence.login_days` von 11 auf 12 durch das bereits bestehende `INSERT OR IGNORE` in der Startinitialisierung; keine Loginzeile hinzugefügt oder verändert. Diesen internen Zähler ausdrücklich dokumentiert und nicht nachträglich zurückgeschrieben. Nachweise in `state-verification.json`, `active-app.json`, `verification.json`, `preview-results.json` und den Prüfprotokollen. Keine öffentliche Aktivierung.
- Nach Abschluss die ausschließlich für Punkt 5 gestartete Testvorschau auf Port 8767 und ihre Prüftabs geschlossen. Testdaten und Aufnahme bleiben als lokale Nachweise erhalten. Die normale Anwendung auf Port 8765 bleibt aktiv. Die vorhandene Profilfenster-Vorschau auf Port 8766 wurde nicht verändert.


### 2026-10-25 – Offline: Baukasten erfasst und Varianten zugeordnet, nur Dokumentation

- Nutzer beauftragt nach der Präzisierung von Punkt 6 ausschließlich die lokale Dokumentation des vorhandenen Baukastens und seiner Einsatzvarianten. Keine weitere Spielumsetzung, kein Serverkontakt, keine Übertragung und kein Neustart. Vorhandenen Arbeitsstand mit Prüfsummen von 733 bestehenden Dateien einschließlich der lokalen Datenbank und des Sitzungsschlüssels erfasst; Log-Ausgangsstand unter `runtime/baukasten-doku-20261025/` gesichert.
- Gestalterische Entscheidung präzisiert: eine wiedererkennbare Spielefamilie aus denselben Materialien und zentralen Bausteinen mit benannten passenden Varianten. Keine allgemeine Pflicht zu vollständigen Profilfenstern oder zusätzlichen Avataren in jeder Spielansicht. Pro benannter Variante bleibt genau eine Grundimplementierung maßgeblich; keine unabhängigen Seitenkopien und keine spielweise veränderte Innenkomposition der 43:57-Profilbühne.
- `docs/BAUKASTEN.md` legt Spieler-, Inhalts- und Zugangsvarianten mit Status und Einsatzmatrix fest. Vollständiges Profilfenster für bestehende Profil-/Lobby-/perfect-/Würfelansichten; zentraler Porträtausschnitt aus demselben Avatarbestand für kompakte Listen und die geplante conquest-Zuganzeige; reine Namensanzeige als Standard des laufenden Kartentischs. Ein Kartentischporträt bleibt bis zur eigenen Platzprüfung mit zwei/vier/sechs Personen ausdrücklich ohne Einbauentscheidung. Laufende Fragen und Countdowns von guesstimate/party erhalten keine zusätzlichen Avatare. Bereits vorhandene Party-Lobby-/Ergebnisbilder und Ranglisten werden davon getrennt behandelt. perfect behält Zettel und Buzzer an den bisherigen Stellen.
- Gemeinsame Lobbyübersicht als spätere eigene Komponente festgelegt: Spielkopf, Listenheader mit Erstellen-Aktion, einheitliche Lobbyzeilen, Zustände, Beitritts-/Rückkehraktionen und Rückwege über die jeweilige Spielgruppe. Die vorhandene geöffnete Standardlobby aus Punkt 5 bleibt eigenständig beschrieben. Zentrale Porträtvariante, gemeinsame Listenkomponente und weitere Spielwerte-Anbindungen sind dokumentierte nächste Arbeiten; sie wurden nicht erstellt, angeschlossen oder neu visuell abgenommen.
- `docs/BAUKASTEN_BESTAND.md` erfasst aktuelle Komponenten, Katalogfelder, Bildvarianten, Räume, Spielmaterial und lokale Bibliotheken/Modelle. Aktuelle Kataloge ohne App-Import aus `app.py` gelesen: 19 Avatare inklusive Standard, 14 Pultfamilien inklusive Standard, 11 Profilhintergründe inklusive Standard sowie 40 auswählbare Sprüche plus Standardtext. Hohe Profilpulte, ältere Artikel-/Ergebnispulte und Hängeplaketten je Familie zugeordnet. Weitere nicht in diesen Katalogfeldern registrierte Dateien bleiben als Bestand erhalten; daraus keine vollständige Nichtverwendung abgeleitet.
- Ergänzend `docs/BAUKASTEN_DATEIEN.json` als ausdrücklich nicht vom Spiel geladener Dokumentationsstand angelegt: 263 verlinkte Quell-/Assetdateien mit Pfad, Größe, SHA-256, Katalogbindungen und bei Bildern gelesenen Maßen bzw. SVG-Angaben. Lokales Würfelpaket mit 24 Dateien, FBX-Modelle, Texturen, Klänge, Schriftdateien und Three.js erfasst. Vorhandene Lizenzdateien zugeordnet; keine pauschale Lizenzübertragung auf Theme-Assets und keine erfundenen Quellenbelege. Kein Download, keine Grafikerzeugung, kein Modellimport, keine Assetverschiebung oder Löschung.
- Vorhandene `docs/PROFILE_WINDOW.md` und `docs/LOBBY_LAYOUT.md` auf den Baukasten verwiesen. Die irreführende Aussage „Alle Spiele verwenden das Makro“ auf die tatsächlichen vollständigen Profilfenster begrenzt und den bereits erledigten Lobby-Anschluss von offenen Spielanbindungen getrennt. README um den Dokumentationseinstieg ergänzt; übrige Inhalte erhalten.
- Prüfungen: 277 lokale Dokumentverweise aufgelöst, keine defekten Verweise; Tabellenstruktur und Codeblock-Abschlüsse geprüft; alle 263 Dateigrößen/Prüfsummen erneut mit dem Bestand abgeglichen und Katalogzahlen bestätigt. Aktuelles Kartenmotiv in der statischen Ablage und im räumlichen Tisch per SHA-256 identisch. Abschließender Vergleich erlaubt ausschließlich Dokumentationsänderungen: keine Änderung an Spielcode, Vorlagen, Styles, Bildern, Modellen, Tests, Spielständen oder Sitzungsschlüssel. Projektlog ausschließlich ergänzt, bisheriger Inhalt als unveränderter Byte-Präfix erhalten. `git diff --check` erfolgreich. Keine Spieltests oder Browser-/Live-Abnahme für diese reine Dokumentationsarbeit behauptet. Nachweise lokal in `runtime/baukasten-doku-20261025/verification.json` und `inventory-check.json`.


### 2026-10-25 – Offline: gemeinsame Lobbyübersichten nach dem Baukasten

- Nutzer beauftragt die Umsetzung von `zugang.liste` ausdrücklich offline mit Erhalt vorhandener Änderungen und Spielstände. Vor Beginn 736 bestehende Dateien einschließlich PC-Datenbank/Sitzungsschlüssel per Prüfsumme erfasst, bestehende Quelltexte gesichert und konsistente lokale Datenbankkopie unter `runtime/lobby-overviews-20261025/before.sqlite3` angelegt. Keine Serververbindung, Übertragung, Veröffentlichung oder Änderung von Spielregeln.
- Gemeinsame Übersicht für guesstimate party, playtable, würfeltisch, kniffel, mäxchen, perfect und conquest: `templates/_lobby_overview.html`, `static/lobby-overview.css`, `static/lobby-overview.js` und `lobby_overview.py`. Genau ein Aufbau für Spielkopf, Erstellen-Aktion, Lobbyname/Host/Belegung/Zustand/Einstellung, Aktion, leere Liste, Aktualisierungsfehler und Rückweg. Spielseiten übergeben nur Inhalt, Kapazität und vorhandene Endpunkte; keine neue Porträtvariante eingebaut.
- `lobby erstellen` steht im gemeinsamen Listenheader; unter 680 px folgen Erstellen und Zeilenaktion ihren Texten. Vorhandene persönliche Party-, Karten-, Würfel-, perfect- und conquest-Hintergründe erhalten. Karten kehren zur Kartengruppe, Würfelspiele zur Würfelgruppe, perfect/conquest zu brettspiele und Party zu guesstimate zurück. Gewählte Raum-/Spielmaterialien und laufende Spieltische bleiben eigenständig.
- Gemeinsame Aktionen: `beitreten`, `zur lobby`, `zurück ins spiel`, bei reserviertem conquest-Platz `zurückkehren`, bei eigenem abgeschlossenen Feldzug `ergebnis ansehen`. Volle bzw. gestartete fremde Lobbys bieten keinen unzulässigen Beitritt. Bestehende Abfragen, Teilnehmergrenzen, CSRF-/Mitgliedschaftsprüfung und Backend-Beitrittsregeln erhalten. perfect zeigt entsprechend dem beschlossenen Baukasten nun auch mit eigener aktiver Mitgliedschaft seine Übersicht und bietet die Rückkehraktion; nur der frühere automatische Sprung vom Index in die eigene Lobby entfällt.
- Ein gemeinsamer Ablauf prüft sichtbare Übersichtsangaben per JSON über dieselbe Übersichtsadresse. Private Spielzustände und reine Spielzugrevisionen gehen nicht in die Signatur ein. Verdeckte Tabs reduzieren Abfragen; Rückkehr über Browserverlauf setzt sie fort. Navigation/Beitritt unterbrechen die alte Ansicht. Bei Unterbrechung bleiben Zeilen erhalten und `erneut prüfen` wird angeboten. Ältere Party-/Conquest-Statusadressen bleiben verfügbar, ihre separaten bisherigen Übersichtsskripte sind in der neuen Übersicht nicht aktiv.
- Ersetzte Übersichtsgestaltungen aus Party-, Karten-, Würfel-, perfect- und conquest-Styles an ihren ursprünglichen Stellen konsolidiert. Der bisherige `static/conquest-lobby.js`-Bestand bleibt erhalten, ist aber nicht mehr eingebunden. Die geöffnete perfect-Raumvorlage ist bis auf Dateiversionen identisch, sein Spielskript bytegleich; alle 56 Zettel-/Startformular-/Buzzer-Regelblöcke stimmen mit der Sicherung überein. Keine Position oder Bereitschafts-/Startregel des geöffneten Raums geändert.
- Prüfungen: vollständige Suite mit allen 206 Python-Tests erfolgreich, darunter fünf neue gemeinsame Übersichtstests für leere Ansichten, Beitritt/Rückkehr aller Spiele, volle/gestartete/eigene/reservierte/abgeschlossene Runden, maskierte Spielernamen, datensparsame Signaturen und Präfix-/Routenparameter. Nach der letzten Parameterpräzisierung diese fünf Tests erneut bestanden. Sieben JavaScript-Verhaltenstests bestanden, davon vier für Übersichtsaktualisierung, Fehler/Wiederholung, Navigation/verdeckte Tabs und Browserverlauf sowie drei bestehende Lobby-Speicherprüfungen. Fragenbibliotheksprüfung, JavaScript-Syntax und `git diff --check` erfolgreich. Alte Oberflächenerwartungen gezielt auf die beschlossenen Beschriftungen und Rückwege angepasst; keine Spielregelerwartungen gelockert.
- Eigene Prüfanwendung auf 127.0.0.1:8767 mit eigener Datenbank, getrennten Host-/Gastcookies und ausschließlich Testspielern verwendet. Alle sieben Übersichten tatsächlich im Browser geprüft: gleicher Aufbau, Erstellen oberhalb der Zeilen, passende Hintergründe und kein horizontaler Überlauf. Alle sieben leeren Listen und je 390/800 px breite Einbettungen geprüft (373/783 px Dokumentbreite wegen Scrollbalken): kein seitliches Überlaufen, bei der schmalen Ansicht Erstellen und Zeilenaktion unter den Texten. Keine Browser-Größenvorgabe geändert.
- Sichtbare Abläufe: Kartentisch-Beitritt und automatische Belegungsänderung in der anderen Ansicht; neue perfect-Lobby über den gemeinsamen Erstellen-Knopf mit ursprünglichem Zettel/Buzzer; conquest über die Übersicht betreten, gestartet, verlassen, reservierten Platz mit `zurückkehren` wieder aufgenommen und anschließend als eigene laufende Partie mit 2/6 Personen angezeigt. Normale Nutzerpartien nicht bedient. Aufnahme der fertigen Übersicht unter `runtime/lobby-overviews-20261025/uebersicht-desktop.png`; DOM-/Ablaufnachweise in `browser-verification.json`.
- Baukasten, Bestand und `docs/LOBBY_LAYOUT.md` auf den tatsächlich eingebauten Stand fortgeschrieben; Schnittstelle in `docs/LOBBY_OVERVIEW.md` dokumentiert. Dateiliste umfasst nun 267 vorhandene Quellen; Größen/Prüfsummen sowie 286 lokale Dokumentverweise erfolgreich geprüft. Zentrale Porträtvariante und weitere Spielwerte-Anbindungen bleiben offen.
- Ausschließlich die verifizierte normale PC-Anwendung mit derselben lokalen Datenbank und demselben Sitzungsschlüssel neu gestartet. Neuer Prozess 7692 über `deploy/run_local.py --port 8765`; Healthcheck und neue Übersichtsdateien lokal HTTP 200. Abschließender lesender Vergleich der 29 Datenbanktabellen: keine Änderung der 28 Inhaltstabellen einschließlich Konten, Profilausrüstung, Ergebnissen, Spielständen und Nutzungshistorie. Nur `sqlite_sequence.login_days` steigt durch den bestehenden Startablauf von 12 auf 13; keine Loginzeile hinzugefügt oder verändert und kein Zähler nachträglich zurückgeschrieben. Sitzungsschlüssel unverändert. Nachweise in `active-app.json`, `state-verification.json`, `preservation-review.json` und den Prüfprotokollen. Keine öffentliche Aktivierung.
- Nach Abschluss die nur für diesen Auftrag gestartete Prüfanwendung auf Port 8767 beendet und den noch vorhandenen eigenen Prüftab geschlossen; weitere Prüftabs waren bereits nicht mehr zugeordnet. Normale Anwendung auf Port 8765 bleibt aktiv, bestehende Profilvorschau nicht verändert. Lokale Testdaten, Sicherungen und Aufnahme als Nachweise erhalten.


### 2026-10-25 – Offline: kompakte Conquest-Spieleranzeige und offene Comicgestaltung

- Nutzer beauftragt die kompakte Anzeige ausdrücklich offline. Vor Beginn 743
  vorhandene Projekt-/Datendateien per Prüfsumme erfasst, bestehende Quelltexte
  und konsistente normale PC-Datenbank unter `runtime/conquest-portraits-20261025/`
  gesichert. Keine Serververbindung, Übertragung, Veröffentlichung, Commits oder
  Pushes. Vorhandene fremde Änderungen erhalten.
- `spieler.portraet` besitzt nun eine gemeinsame Implementierung in
  `static/player-portrait.js` und `static/player-portrait.css`, mit zentraler
  Profil-/Ausschnittzuordnung `player_portrait.py`. Conquest zeigt in der
  bestehenden unteren Zugleiste den aktuellen Spieler, den ausgerüsteten Avatar,
  Armeefarbe, Phase, Länder und bereits platzierte Truppen. Noch zu verteilende
  Truppen stehen getrennt daneben. Keine zusätzliche Profilbühne um die Karte.
  Alle 19 vorhandenen Avatarmotive unverändert; keine neue Zeichnung erzeugt.
- Aktuelle Profilausrüstung wird auch für reservierte Plätze lesend abgerufen.
  Die öffentliche Standardavatarvariante bleibt für andere Spieler erhalten.
  Virtuelle Testarmeen und Neutral erhalten keine erfundenen Benutzeravatare.
  Profilwechsel werden auch ohne Änderung der Spielrevision angezeigt; ältere
  Statusantworten können keinen neueren Stand ersetzen. Namen werden als Text
  eingesetzt, lange Namen gekürzt angezeigt und vollständig zugänglich gehalten.
  Eigene Karten und Missionen bleiben in der bisherigen privaten Freigabe.
- Alte Initialen-Komposition und zugehörige Desktop-/Mobilregeln an der
  zuständigen Zugleiste ersetzt. Die neue Porträtkomponente skaliert als Ganzes;
  keine Spielkopie ihrer Innenkomposition. Die tatsächliche Zugleistenhöhe wird
  bei Kartenkamera, unterer Informationsfläche und Mengenfenster berücksichtigt.
  Bestehende Kamera-/Kartenmechanik beibehalten; Tisch-Dateiversion jetzt 13.
- Isoliertes Beispiel und gespeicherter Tisch verwenden denselben Porträtcode.
  `deploy/preview_conquest.py` liefert dafür nur den bisherigen Beispielordner
  und die benötigten gemeinsamen UI-/Schriftdateien über 127.0.0.1 aus, ohne
  Datenbankzugriff. Startanweisung angepasst, damit die isolierte Vorschau
  trotz gemeinsamer Quellen weiter funktioniert. Im Browser 42 Marken,
  Beispielanzeige und fehlerfreier Start tatsächlich geprüft.
- Neue Gestaltungspräzisierung in `docs/GESTALTUNGSPLAN.md` festgehalten:
  funktionaler Bestand ist keine fertige Comicgestaltung. Nach dem kompakten
  Porträt zunächst die gemeinsame Comicform von Buttons und spielbegleitenden
  Anzeigen entwerfen und prüfen, vor weiterer gestalterischer Verbreitung.
  Die Nutzerreferenz verlangt ausgeprägte dunkle Tiefe, beim Drücken kleiner
  werdende Unterkante und lebendigere Formen. Die generelle Button-/Dialog-
  Überarbeitung wurde hier nicht umgesetzt. Für Party ein eigenständiges
  modernes Siegertreppchen planen; alte `podium`-Darstellung nicht als fertigen
  Standard übernehmen. Gewinner- und eventuell Verliererposen je Avatar bleiben
  eine unentschiedene Idee, keine beauftragte Grafikerzeugung.
- Baukasten, Bestand und Schnittstellendokumentation auf den lokalen Anschluss
  aktualisiert; `docs/PLAYER_PORTRAIT.md` beschreibt Quelle, Datenschutz,
  Darstellung und Wiederverwendung. Weitere Ranglisten-/Spielwerte-Anbindungen,
  vollständige Comicgestaltung und Party-Treppchen bleiben offen. Quizfragen
  weiterhin ohne zusätzliche Avatare; Kartentisch erst nach Platzprüfung;
  Perfects Zettel/Buzzer bleiben an ihren bisherigen Stellen.
- Prüfungen: alle 210 Python-Projekttests und 57 JavaScript-Verhaltenstests
  erfolgreich. Neue Abdeckung für aktuelle Ausrüstung ohne Spielzustandsänderung,
  eigene/öffentliche Standardvariante, reservierte Spieler, unbekannte Avatar-ID,
  Präfixe, gemeinsame Auslieferung und Profilaktualisierung ohne neue Spielrevision.
  Fragenbibliotheksprüfung, JavaScript-Syntax und `git diff --check` erfolgreich.
- Tatsächliche Browserprüfung ausschließlich mit eigener Testdatenbank: zwei,
  drei und sechs Personen, virtuelle Entwicklerarmeen, Wechsel von Spieler,
  Avatar und Armeefarbe nach Platzierung sowie Übernahme eines neuen Avatars
  bei unverändertem Spielzustand. Zweierspiel: nach erster eigener Platzierung
  15 Truppen, nach zweiter 16; neutrale Platzierung getrennt, anschließend
  nächster Spieler mit seinen 14 Truppen. Alle 19 Avatare geladen und visuell
  geprüft. Lange Namen und siebenstellige Truppenzahl in eigener Galerie geprüft.
- Schmale echte Einbettungen mit 320, 390 und 800 Pixel Dokumentbreite geprüft:
  kein horizontaler Überlauf, keine Überschneidung von Informationsfläche und
  Zugleiste; bei 320/390 Pixel genau 16 Pixel Abstand. Im Überblick bei allen
  drei Breiten sämtliche 42 Marken oberhalb der Zugleiste. Keine Browser-
  Viewportvorgabe geändert. Aufnahmen `all-avatars.png`, `narrow-frames.png`,
  `test-army.png` und `conquest-player-preview.png` tatsächlich angesehen;
  letztere zeigt ausschließlich die vorbereitete Testpartie, keine Nutzerpartie.
- Eindeutig zugeordnete normale PC-Anwendung kontrolliert mit unverändertem
  Datenbankpfad/Sitzungsschlüssel neu gestartet, neuer Prozess 24836. Lokaler
  Healthcheck HTTP 200/ok. Lesender Vergleich aller 29 Tabellen: 28 Inhaltstabellen
  einschließlich Konten, Ergebnissen, Profilausrüstung, gespeicherten Feldzügen und
  Fragenverbrauch unverändert. Einzige Abweichung: `sqlite_sequence.login_days`
  steigt durch den bestehenden Startablauf von 15 auf 16; keine Loginzeile
  hinzugefügt oder geändert, Zähler nicht zurückgeschrieben. Sitzungsschlüssel
  unverändert. Normale Lobby Nr. 4 bleibt wartend mit Stormseed allein und wurde
  nicht gestartet oder als Testpartie benutzt. Neue Anzeige ist lokal für
  laufende Partien aktiviert; sämtliche Browser-Spielaktionen erfolgten in
  getrennten Testdaten. Öffentliche Aktivierung nicht erfolgt.

- Abschluss: eigene Browser-Prueftabs geschlossen und die zugeordneten
  Pruefprozesse auf Port 8767/8768 beendet. Normale lokale Anwendung bleibt
  aktiv; Health weiterhin ok. Ausgelieferte gemeinsame Portraet-JS/CSS-Dateien
  stimmen exakt mit den lokalen Dateien ueberein. 272 erfasste Quelldateien und
  303 lokale Dokumentverweise geprueft, keine unerwartete Aenderung am zuvor
  vorhandenen Bestand. Nachweise in `verification.json`, `active-app.json`,
  `preservation-review.json` und den Browser-/Pruefprotokollen im Laufzeitordner.


### 2026-10-25 – Offline: interaktive Comic-Buttons und Spielanzeigen, Entwurf 01

- Nutzer beauftragt ausschließlich einen lokalen Entwurf zum Anschauen nach
  seiner Buttonreferenz. Vor Beginn 751 bestehende Projekt-/Datendateien erfasst
  und konsistente lokale Sicherung unter `runtime/comic-ui-v1-20261025/` angelegt.
  Keine Serververbindung, Übertragung, Veröffentlichung oder Einbindung in die
  normalen Spiele. Normale Anwendung nicht neu gestartet; vorhandener Code,
  Assets und andere lokale Änderungen bleiben erhalten.
- Eigenständige Vorschau `offline-preview/comic-ui-v1/` unter
  `http://127.0.0.1:8770/`: feste dunkle Buttonbasis, beim Drücken absinkende
  Vorderseite, kantige asymmetrische Comicform, Lichtkante und plastische Flächen.
  Genau eine Button-Komposition mit gemeinsamen Parametern für Größe und Tiefe;
  Haupt-/Nebenaktion, Blau, Gefahr, Auswahl, Fokus und deaktiviert verwenden sie.
  Bestehendes Aktionsgrün und lokale Inter-/Fredoka-Schriften beibehalten.
- Conquest-Beispiel mit bestehender Karte und unverändertem gemeinsamem Porträt,
  Wertetafeln, Phasenemblem, wechselnden Phasenhinweisen, Zugübergabe und
  Inventardialog. Dazu Würfelstand mit verbrauchtem Wurf und Uhr mit Pause,
  Warnung, Ende und Rücksetzung. Alle Werte/Wechsel nur im Browser; keine
  Anbindung an Konten, Spielregeln, gespeicherte Partien oder Nutzungsverbrauch.
  Referenzbild nur lokal angezeigt; kein fremdes Spielasset nachgebaut und
  keine Rastergrafik generiert. Party-Siegertreppchen bleibt getrennt offen.
- Vorschau im tatsächlichen Browser gesehen und bedient. Buttonfläche bei
  normaler Tiefe von 0 auf 5,04 Pixel abgesenkt, bei maximaler Tiefe auf 8,04
  Pixel; Außenhöhe beim bloßen Drücken identisch. Dauerhafter Druckvergleich
  per Umschalter und gemeinsame Tiefenverstellung vorhanden. Phasenwechsel,
  Wechsel zu Robin/Fennek, deaktivierter dritter Würfelwurf, Inventar öffnen
  per Leertaste und schließen per Escape, echte Tastaturfokusanzeige sowie
  Pfeiltastenbedienung der Phasen geprüft. Timer erreicht 00:00 mit Warnfarbe,
  Ende und gesperrtem Start; Pause und Rücksetzung geprüft.
- Echte Einbettungen mit 320/390/800 Pixel Rahmenbreite geprüft (305/375/785
  Pixel Inhaltsbreite wegen eigener Scrollbalken): alle Bilder geladen,
  keine seitlichen Seiten- oder Buttonüberläufe. Desktop, schmale Ansichten
  und Inventardialog tatsächlich visuell kontrolliert. Keine Browser-
  Viewportvorgabe verändert. Aufnahmen `comic-preview.png`, `widths.png` und
  `inventory-dialog.png`, Messungen in `browser-checks.json`. JavaScript- und
  Python-Syntax sowie `git diff --check` erfolgreich; keine neue Vollprüfung
  der unveränderten normalen Spielanwendung behauptet.
- Lesender Erhaltungsabgleich: bestehender Spielcode, Styles, Vorlagen, Bilder
  und Sitzungsschlüssel unverändert. Parallel änderten sich in der normalen
  Datenbank bei bestehender Party-Lobby Nr. 6 nur `status`/`completed_at` und
  beim vorhandenen Mitglied Nr. 6 `status`; keine Zeilen hinzugefügt/entfernt.
  Der genaue Auslöser wurde nicht untersucht. Die Vorschau hat keinen
  Datenbankzugriff. Vorhandene parallele Zustandsänderungen nicht zurückgesetzt;
  weitere Tabellen einschließlich Conquest, Konten, Ergebnissen und Verbrauch
  im Vergleich unverändert. Keine pauschale Unverändertheit aller Tabellen
  behauptet. Prüfnachweise bleiben im ignorierten lokalen Laufzeitordner.
- `docs/GESTALTUNGSPLAN.md` unterscheidet jetzt vorhandene und geprüfte Vorschau
  von ausstehender gestalterischer Abnahme und späterem Spieleinbau. Der Entwurf
  ist kein bereits freigegebener Standard. Eigene Breiten-Prüfansicht geschlossen,
  eigentliche Vorschau für den Nutzer geöffnet gelassen; lokaler Prozess 21772
  bleibt dafür aktiv und lauscht ausschließlich an 127.0.0.1:8770.


### 2026-10-25 – Offline: sichtbarer Klickweg bei normalen Comic-Aktionen

- Nutzer meldet, dass normale Aktionsbuttons bei kurzem Klick nicht erkennbar
  hinunter und zurück gehen. Der bisherige `:active`-Effekt galt nur während
  des Gedrückthaltens; die frühere Messung des festgehaltenen Zustands war kein
  Nachweis eines vollständigen kurzen Aktionsklicks.
- Gemeinsame Button-Funktion in `offline-preview/comic-ui-v1/components.js`
  korrigiert: normale Aktionen zeigen einen 300-ms-Druckweg mit Absenken,
  kurzem Halten und Rückkehr. Start aus der tatsächlichen aktuellen Position,
  wiederholte Klicks ersetzen die vorherige Bewegung. Aktion wird sofort
  genau einmal ausgeführt, auch wenn sie danach ihren Button deaktiviert.
  Ausgewählte Phasen und Umschalter behalten ihre bisherige Einraststellung;
  reduzierte Bewegung verwendet nur einen kurzen diskreten Druckzustand.
- Nach Neuladen in der laufenden lokalen Vorschau tatsächliche Zeitreihen
  aufgenommen: normaler Mausklick auf „spiel starten“ von −1 auf 5,04 Pixel
  und zurück auf −1 bei weiterhin darüberstehendem Zeiger. Tastatur-Leertaste
  bei „truppen verteilen“ von 0 auf 5,88 Pixel und wieder 0; Beschriftung bereits
  während der Bewegung zu „angriff beenden“ gewechselt, Phase genau einmal
  weitergeschaltet. Spätere Kontrolle: Aktionsfläche wieder bei 0, ausgewählte
  Phase weiterhin abgesenkt. Keine Browserfehler/Warnungen beobachtet.
- Nachweise unter `runtime/comic-button-tap-20261025/`: vorherige Dateien,
  Sicherung, `animation-traces.json` und `button-feedback.png`. README
  präzisiert. Syntax und `git diff --check` erfolgreich. Nur die separate
  Vorschau angepasst; keine Einbindung in normale Spiele, kein Dienstneustart,
  kein Serverkontakt oder Transfer. Vorhandene andere Änderungen erhalten.


### 2026-10-25 – Offline: Comic-Tafel für Sammlung erhalten und dezente Auswahl gesichert

- Nutzer möchte die bestehende Gestaltungs-/Einstellseite ausdrücklich erhalten
  und für eine spätere Sammlung wiederfinden. `offline-preview/SAMMLUNG.md`
  führt sie als Tafel UI-001, verlinkt Quelle und Startanweisung. Die Seite und
  ihre bisherigen Beispielabläufe bleiben bestehen; keine neue Generator-
  Oberfläche gebaut und nichts in normale Spiele eingebunden.
- Nutzerbewertung getrennt festgehalten: Druckweg „dezent“ gefällt; Form und
  Oberfläche noch offen. Schriftwirkung und Sound sind weitere zu untersuchende
  Dimensionen. `offline-preview/comic-ui-v1/entwurf.json` dokumentiert Auswahl,
  300-ms-Klickbewegung und Bewertungsstand. Es ist noch kein vom Spiel geladener
  Generator-Import. Gesamtentwurf nicht als allgemein freigegeben markiert.
- Tatsächliche Nutzerauswahl vor Änderung im Browser gelesen: Regler 4, Label
  dezent, Drucktiefe 0,25 em. Diese Werte nun als Voreinstellung der bestehenden
  Vorschau hinterlegt, damit späteres Öffnen wieder dort beginnt. In einer
  frischen Vorschau bestätigt: Regler 4/dezent, gemeinsame Buttonbasis 3 Pixel
  bei 12-Pixel-Schrift. Nur eigenen Kontrolltab geschlossen; bestehende
  Nutzervorschau einschließlich ihrer aktuellen Sitzung geöffnet erhalten.
- README, Baukasten und Gestaltungsplan verweisen auf die Sammlung. Denkmodell
  für einen späteren Generator: getrennte Form/Kontur, Material/Oberfläche,
  Schriftform/Beschriftungswirkung, Körper/Tiefe/Bewegung und Sound; gemeinsam
  benannte Einstellungen statt unabhängiger Spielkopien. Dies ist eine
  Überlegung, keine Umsetzung oder Freigabe zum weiteren Einbau.
- Vorherige betroffene Dateien und Prüfsummen von 755 bestehenden Quelldateien
  unter `runtime/ui-collection-20261025/` gesichert. Vorhandene Änderungen anderer
  Arbeiten erhalten; keine Datenbankänderung, kein App-Neustart, kein Server-
  kontakt oder Transfer. Neue Voreinstellung und JSON auf Übereinstimmung,
  lokale Dokumentverweise und `git diff --check` geprüft. Die Änderung betrifft
  ausschließlich die Sammlung, Dokumentation und Vorschau-Voreinstellung;
  bestehende Form, Oberfläche und Klickbewegung selbst unverändert.


### 2026-10-25 – Offline: Button-Werkstatt UI-002 mit dauerhaften Entwurfsständen

- Auf ausdrücklichen Folgeauftrag eine eigene lokale Werkstatt unter
  `offline-preview/button-workshop-v1/` gebaut, in `offline-preview/SAMMLUNG.md`
  als UI-002 registriert. UI-001 bleibt daneben erhalten. Baukasten und
  Gestaltungsplan beschreiben jetzt das vorhandene Werkzeug, weiterhin keine
  gestalterische Gesamtfreigabe und keinen Einbau in normale Spiele.
- Drei Startvorlagen (Holz, Stein/Schiefer, gebrauchtes Metall); Material,
  Glanz/Struktur/Farbe, Kontur/Form, Schriftform und fünf Beschriftungswirkungen,
  Druckweg/Dauer/Bewegungsgefühl sowie optionale lokale Materialklänge.
  Ausgangswert dezent, 300 ms, ohne Ton. CSS-Material- und Schriftwirkungen
  bleiben Entwürfe; keine neuen Bild- oder fremden Audioassets erzeugt.
- Eine gemeinsame Buttonkomposition für große Vorschau, sechs Zustände,
  A/B-Vergleich, Bibliothekskacheln und Beispieltafel. Wiederverwendung der
  bestehenden Funktion und des Grund-CSS aus UI-001. Bestehende Funktion nur um
  optionalen Bewegungsparameter erweitert; bisherige Aufrufer behalten 300 ms
  und ease-out. Alle übrigen Dateien der ersten Tafel im Prüfsummenvergleich
  unverändert. Kein separater Innenaufbau je Muster oder Spiel.
- Entwürfe werden mit Name, vollständigen Einstellungen, Notiz und getrennten
  Bewertungen dauerhaft als neue JSON-Dateien unter
  `design-library/recipes/button-workshop/` gespeichert. Keine Überschreibung
  oder Löschung alter Stände; Ausgangsstand wird referenziert. Persönliche
  Dateien von Git ausgeschlossen und als Benutzerdaten dokumentiert. Export
  und validiertes Einlesen vorhanden. Ungespeicherte Änderungen und gemerkter
  A-Vergleich gelten nur für die aktuelle Seite; die Oberfläche benennt dies.
  Katalog ist gemeinsame Quelle für Bedienfelder und Datenvalidierung.
- Fünf Prüfungen erfolgreich: erhaltende Speicherung und Neustart,
  ungültige Daten ohne Speicherung, beschädigte Dateien ohne Löschen,
  Importvalidierung sowie tatsächliche HTTP-Speicher-/Lesewege einschließlich
  fremdem Ursprung und abgewiesenem Dateizugriff. JS-Syntax, Dokumentverweise
  und git diff --check erfolgreich. Prüfungen mit temporären Verzeichnissen
  im lokalen runtime-Ordner, ohne Spielimport oder Datenbankzugriff.
- Tatsächlich im Browser geprüft: Materialwechsel, festgehaltenes A gegen
  geändertes B, Leertaste, deaktivierter Zustand, Speichern, Neuladen und
  Wiederöffnen mit Einstellungen/Bewertungen/Notiz, Export und erneutes
  Einlesen derselben Datei sowie zwei erhaltene Stände. Nach Neustart des
  Prüfservers beide Stände wieder geladen. Materialabhängige Klangbewertung
  wird bei Materialwechsel wieder offen, Bewegungsbewertung bleibt getrennt.
  Sound-Auslösung zeigt „Ton bereit · Holz · 20 %“, keine Browserwarnungen
  während dieser Funktionsprüfung; Klangqualität nicht nach Gehör abgenommen.
- Reale Klick-Zeitreihe UI-002 bei dezent: Absenkung bis 3,91 Pixel und Rückkehr
  auf −1 bei darüberstehendem Zeiger. Erste Tafel separat nochmals geprüft:
  Regler 4/dezent, Klick bis 2,04 Pixel und Rückkehr auf −1. Kleinere Wege dort
  folgen aus der proportional kleineren Schriftgröße. Spätere Funktionen oder
  CSS-Zustände wurden nicht als Ersatz für den tatsächlichen Klicknachweis
  verwendet. Unter `runtime/button-workshop-v1-20261025/` liegen Zeitreihen,
  Screenshot, Ausgangssicherung und Prüfsummen.
- 320/390/800-px-Prüfansicht geöffnet und visuell kontrolliert; bei 320 px
  tatsächlicher Klick, Zustandsraster, umbrochener A/B-Vergleich, Wertetafel,
  Einstellfelder und Einzelbewertungen sichtbar geprüft. Nach Abschalten nur
  des eigenen Prüfservers versuchtes Speichern: verständliche Fehlermeldung,
  Name/Notiz/Entwurf erhalten, Sammlung weiter zwei Stände, erneutes Speichern
  möglich. Keine falsche Erfolgsmeldung. Prüfdaten getrennt unter runtime,
  persönliche Sammlung nicht mit Testentwürfen befüllt.
- Vorher 759 bestehende Dateien und konsistente lokale Spieldatenbank gesichert.
  Abschlussvergleich: keine geänderten Spieltabellen. An vorhandenen Quellen
  nur Bausteinoption, Sammlungsindex, Baukasten, Gestaltungsplan und dieser
  Logeintrag geändert. Alle vorhandenen anderen Arbeiten erhalten. Kein
  Serverkontakt, kein Transfer und kein Neustart des normalen Spiels.
- Werkstatt geöffnet gelassen: ausschließlich 127.0.0.1:8771, Prozess 23252.
  UI-001 bleibt auf 8770 (21772), normales lokales Spiel auf 8765 (24836).
  Eigene Prüftabs und Prüfserver 8772 anschließend geschlossen/beendet.


### 2026-10-25 – Rückmeldung zu UI-002: Materialien und freie Kontur

- Nutzer gefallen die aktuellen Materialfamilien nicht; sie wirken ihm zu
  unrealistisch. Die bestehenden Materialmuster sind damit ausdrücklich kein
  freigegebener Gestaltungsstand. Die bevorzugte dezente Bewegung bleibt eine
  getrennte Bewertung.
- Nutzer empfindet „Unregelmäßig & comicartig“ und „Abgeschlagene Kanten“ als
  dieselbe Form und fragt nach direkter Formanpassung im Editor. Aktuellen
  Renderer geprüft: beide sind achtpunktige, nur geringfügig unterschiedliche
  Polygonkonturen. Frei bearbeitbare Konturen gibt es bisher nicht; vorhanden
  sind lediglich die Formauswahl und die Konturstärke.
- Als mögliche Weiterentwicklung einen Kontureditor mit verschiebbaren
  Randpunkten und Speicherung der eigenen Kontur beschrieben. In diesem
  Klärungsschritt keine neue Materialgestaltung oder Konturbearbeitung gebaut,
  keine gespeicherten Entwürfe und keine Spiel-/Serverdateien verändert.


### 2026-10-25 – Offline: frei bearbeitbare Konturen und unabhängige Stilwahl

- Nutzer bestätigt die Konturbearbeitung und Materialüberarbeitung. Präzisierung:
  Comic ist aktuell gewünscht, der Generator muss jedoch verschiedene Stile
  ermöglichen. Stilwahl deshalb unabhängig von Material, Kontur, Schrift und
  Bewegung angelegt: Comic (Voreinstellung), Natürlich und Klar. Kein Stilwechsel
  überschreibt die anderen Einstellungen. Separate Stilbewertung ergänzt.
- UI-002 um einen Kontureditor mit 3–32 Randpunkten erweitert: tatsächliches
  Ziehen, Punktwahl und X/Y-Eingabe, Rundung je Punkt, Hinzufügen/Entfernen,
  Doppelklick auf eine Kante, Pfeiltasten sowie Rückgängig/Wiederholen und
  Rückkehr zur Vorlage. Deutlich getrennte Vorlagen für asymmetrisch/weich,
  ruhig gerundet und Scharten/Abplatzungen. Kontur und Rundungen aus derselben
  normierten Geometrie für Editor, Buttonbasis, Oberfläche und alle Vorschauen;
  weiterhin dieselbe gemeinsame Buttonkomposition aus UI-001.
- Datenformat 2 speichert Stil und vollständige Kontur. Format 1 bleibt lesbar:
  vorhandene Konturpunkte als eigene bearbeitbare Kontur übernehmen, Comic und
  offene Stilbewertung ergänzen. Originaldateien unverändert; neues Speichern
  erzeugt weiterhin neue Stände. Validierung auf beiden Seiten schützt vor
  Kreuzungen, ungültigen Zahlen, zu kleinen Flächen und unzulässigen Punktzahlen.
  Die Vorschau älterer Einstellungen kann durch neue Materialbilder anders
  aussehen; keine unveränderte Pixelwiedergabe alter Renderstände behauptet.
- Die regelmäßigen CSS-Materialmuster durch drei originale, mit dem eingebauten
  image_gen-Werkzeug erzeugte lokale Texturen ersetzt: `assets/oak-v1.png`,
  `slate-v1.png` und `steel-v1.png` unter der Werkstatt. Bilder einzeln angesehen,
  als Rohoberflächen ohne Rahmen/Text vorhanden. Vollständige Prompts und
  Herkunft in `assets/PROVENANCE.json`. Keine Projektbilder hochgeladen und
  keine fremden Bilder übernommen. Stil regelt Materialpräsenz, Konturwirkung
  und Lichtkanten; Glanz/Farbe/Struktur bleiben separat bedienbar. Neue Wirkung
  ist noch keine Nutzerabnahme der Materialien.
- Acht Speicher-/HTTP-Prüfungen erfolgreich, einschließlich Format-1-Lesen mit
  unveränderter Originaldatei, eigener gerundeter Kontur und Stil nach Neustart
  sowie abgewiesener Kreuzungen/ungültiger Geometrie. Zusätzliche JS-Prüfungen
  für gültige verschiedene Vorlagen, Rundungsgrenzen und degenerierte Konturen.
  Syntax, lokale Dokumentverweise und git diff --check geprüft.
- Im Browser tatsächlich geprüft: Mauszug (X 12,5 auf 16,1, Y 7 auf 0), ein
  Rückgängig-Schritt stellt den gesamten Zug wieder her, Wiederholen und
  Pfeiltasten; Rundung bis 45 %, Punkt hinzufügen/entfernen, Doppelklick mit
  zehn resultierenden Punkten. Kreuzende Eingabe 99 abgewiesen, vorherige
  Kontur und gültiger Feldwert erhalten. Bei drei Punkten Entfernen deaktiviert.
  Stilwechsel erhalten dieselbe Kontur; gemerktes A und aktuelles B behalten
  getrennte Stile. Dieselbe Kontur in allen aktuellen Buttonvorschauen bestätigt.
- Eigene Zehn-Punkte-Kontur mit Stil, Notiz und Bewertungen gespeichert, eigenen
  Prüfserver neu gestartet, Browser neu geladen und Entwurf unverändert wieder
  geöffnet. Export/Einlesen desselben Format-2-Entwurfs erfolgreich, ohne
  automatisches Speichern. Browserprüfung ausschließlich mit separaten Dateien
  unter `runtime/button-contours-20261025/fixture-recipes`. 320-px-Ansicht von
  Kontur, Punktwahl und Zahlenfeldern gesehen und X-Wert dort tatsächlich
  geändert; kein horizontaler Überstand der sichtbaren Bedienfelder.
- Während der Arbeit geänderte Nutzerauswahl unmittelbar vor Aktualisierung
  nochmals aus der geöffneten alten Tafel gelesen und gesichert. Nach Laden
  der neuen Oberfläche über reguläres Dateieinlesen wiederhergestellt: Metall,
  Farbe #31879c, glänzend, Struktur 0, Konturstärke 2, gemeißelte Beschriftung,
  Druckweg 12, 180 ms und federnd. Nicht stillschweigend auf dezent zurückgesetzt.
  Bisherige acht Konturpunkte jetzt frei bearbeitbar. Kein Entwurf automatisch
  gespeichert. Reale Klick-Zeitreihe in dieser Auswahl: Absenkung beobachtet
  und Rückkehr auf −1 bei darüberstehendem Zeiger; keine Browserfehler/Warnungen.
  Screenshot und Zeitreihe unter `runtime/button-contours-20261025/`.
- Vorher 773 vorhandene Dateien und konsistente Spieldatenbank gesichert;
  Abschlussvergleich ohne geänderte Spieltabellen. Normales Spiel, erste Tafel
  und deren Dateien unverändert. Nur Werkstatt und zugehörige Dokumentation
  erweitert. Kein Kontakt oder Transfer zum Spielserver, kein Neustart des
  normalen Spiels. Werkstatt läuft auf 127.0.0.1:8771 (Prozess 22388), eigene
  Prüfversion und eigener Prüftab zum Abschluss beendet/geschlossen.


### 2026-10-25 – Offline: wiederfindbare Formvorlagen, Schriftzuordnung und Klangrecherche

- Nutzer verwechselt „zur Vorlage“ mit einer Ablage seiner geänderten Form.
  Aktuellen Code und geöffnete Seite geprüft: der Knopf setzte ausschließlich
  zurück, keine gespeicherten Entwürfe vorhanden und Rückgängig bereits leer.
  Die frühere Änderung konnte aus dieser Sitzung nicht zuverlässig rekonstruiert
  werden; keine Wiederherstellung behauptet. Aktion jetzt eindeutig
  „Grundform zurücksetzen“, mit Hinweis auf Rückgängig und fehlende Speicherung.
- Separates „Form als Vorlage speichern“ mit Name ergänzt. Eigene Konturen
  erscheinen dauerhaft unter „Deine Formen“, inklusive direkter Sprunglinks
  auch für die schmale/zweispaltige Anordnung. Dieselbe erhaltende Ablage mit
  `kind: shape`; vollständige Buttonentwürfe bleiben `button`. „Form verwenden“
  übernimmt die Kontur und erhält andere Einstellungen; Rückgängig möglich.
  Speichern erzeugt neue Stände, keine Änderung alter Dateien.
- Vorhandene Inter/Fredoka im Editor unter echten Namen sichtbar. Vier lokal
  abgelegte Schriften aus dem offiziellen google/fonts-Bestand ergänzt:
  Cinzel, Rock Salt, Kalam und Share Tech Mono; Lizenzen/Herkunft unter
  `assets/fonts/`. Keine globale Änderung der Spieltypografie und keine
  Installation im Betriebssystem. Cmap-Prüfung für deutsche Umlaute/ß und
  sichtbare Rock-Salt-Probe im Browser durchgeführt.
- Schriftzuordnung wählbar: passend zur Beschriftungswirkung oder manuell.
  Gemeißelt verwendet Cinzel, Geritzt auf Holz/Stein Rock Salt, Kreide Kalam,
  Anzeige Share Tech Mono. Eigene Schriftwahl schaltet auf manuell. Ältere
  Dateien ohne Zuordnung werden mit ihrer bisherigen Schrift/manuell geladen;
  keine stille Änderung ihrer Datei. Die Zuordnung ist eine Entwurfsentscheidung.
- Öffentlich nach Material- und weiteren markanten Klängen recherchiert.
  Zehn lokale Hörbeispiele aus AntumDeluge/Scrapes (CC0), Kenney/Impact Sounds
  und Interface Sounds (CC0) sowie Lee Barkovich/Robotic mechanic step sounds
  (CC-BY 3.0) vorbereitet. Quellen, Originalnamen, Prüfsummen, Dauern und
  Lizenzen unter `assets/audio/`; Urheber/Lizenz zusätzlich sichtbar an den
  Hörbeispielen. Originaldateien unverändert. Kein Bezug aus kostenpflichtigen
  Paketen, kein Kontakt zum Spielserver.
- Kandidaten: raues Reiben, Planken-/leichter Holzanschlag, Robotertritt und
  schwerer Stampfer, Metallplatte, Klick, Einrasten, Drop, digitale Bestätigung.
  Quellenbeschreibung des Stein-Kandidaten: Objekt über Betonblock, keine
  belegte Aufnahme zweier natürlicher Felsen. Auswahl nach Quellenbeschreibung,
  nicht nach Gehör abgenommen. Nicht als fertiger Materialsound bezeichnet.
  Alte synthetische Töne sind als Platzhalter benannt und bleiben für alte
  Einstellungen lesbar. Neue Voreinstellung weiterhin ohne Ton.
- Klanggalerie spielt vollständige Dateien. Button verwendet kurze Ausschnitte
  mit Ein-/Ausblendung, einmal beim Drücken, kein zweiter Aufnahme-Anschlag beim
  Loslassen. Neue Drücke ersetzen vorherige Wiedergabe; Stoppen verhindert auch
  den nachträglichen Start noch ladender Aufnahmen. Gesamte Wiedergabe stoppbar.
- Zehn Speicher-/HTTP-Prüfungen bestanden, einschließlich getrennter, erhaltender
  Formstände und alter Format-2-Dateien ohne Schriftzuordnung. Geometrie- und
  Schriftzuordnungsprüfungen bestanden. Zusätzliche Audio-Verhaltensprüfung für
  Einzelanschlag, kein Loslass-Duplikat, Zwischenspeicherung, Abbruch noch ladender
  Aufnahme und Dateifehler erfolgreich. Syntax, Dokumentverweise und
  git diff --check erfolgreich.
- Browserprüfung mit eigenen Dateien unter
  `runtime/button-library-audio-20261025/fixture-recipes`: eigene Form gespeichert,
  Grundform zurückgesetzt, Rückgängig stellt geänderten X-Wert wieder her;
  nach Neuladen Vorlage in Sammlung und bei anderem Material übernommen.
  Automatische Cinzel-/Rock-Salt-Zuordnung und erhaltene manuelle Inter-Auswahl
  geprüft. Reibung, Planke, Robotertritt und Klick tatsächlich geladen/decodiert
  und über den Button gestartet; vollständige Plankenaufnahme über native
  Audiosteuerung wiedergegeben und gestoppt. Keine Browserfehler/Warnungen;
  diese technische Wiedergabeprüfung ist keine klangliche Abnahme.
- Aktuelle Nutzerauswahl vor Aktualisierung über reguläres „Entwurf speichern“
  gesichert und wieder geöffnet: gleiche Einstellungen und identischer Konturpfad
  bestätigt. Die inzwischen offene Zehn-Punkte-Form separat als
  „Werkstatt-Holz · Form“ gesichert. Passende Schriftzuordnung aktiviert und
  bisherigen Holz-Platzhalter durch Planken-Kandidaten ersetzt; aktualisierten
  Buttonstand ebenfalls gespeichert. Zwei Buttonstände und eine Formvorlage
  in persönlicher Sammlung; keine Prüfform dort angelegt. Dies ist die aktuell
  offene Form, keine behauptete Wiederherstellung der früheren verlorenen Fassung.
- Vorher 781 vorhandene Dateien und konsistente lokale Spieldatenbank gesichert.
  Abschlussvergleich ohne geänderte Spieltabellen. Erste Tafel und normales
  Spiel unverändert. Nur lokale Werkstatt und Dokumentation erweitert; kein
  Transfer auf den Spielserver. Werkstatt bleibt auf 127.0.0.1:8771 (24664),
  erste Tafel auf 8770 (21772), normales Spiel auf 8765 (24836). Eigener
  Prüfserver 8772 und eigener Prüftab zum Abschluss beendet/geschlossen.

### 2026-10-25 – Offline: zusammenhängende Conquest-Zugtafel UI-003

- Neue lokale Tafel unter `offline-preview/conquest-console-v1/`, erreichbar
  auf 127.0.0.1:8773 (7228). Auf Nutzerauftrag die gespeicherte Buttonform
  mit Spielerwerten und Zuganzeigen verbunden. Ausschließlich Beispielwerte
  im Browser, keine Anbindung an normale Partien und kein Servertransfer.
- `profile.json` enthält einen festen Stand aus „Werkstatt-Holz“ und
  „Werkstatt-Holz · Form“: identische Zehn-Punkte-Kontur, Holz, Fredoka,
  aufgemalte Beschriftung, dezent/4, 300 ms, Planken-Kandidat. Einstellungen
  und Kontur gegen die persönlichen Quelldateien abgeglichen. Auf der Tafel
  eigene grüne Aktionsfarbe mit stärkerem Farbauftrag; Start ohne Ton.
  Dies ist ein Arbeitsentwurf, keine Abnahme von Form, Oberfläche oder Klang.
- Dieselben Button-/Materialbausteine wie UI-001/UI-002 und unveränderter
  gemeinsamer Spielerporträtbaustein. Materialrenderer um optionale Symbol-
  und Farbauftragsparameter ergänzt; bisherige Aufrufe behalten ihre Werte.
  Aktionsknöpfe bleiben beim Aktualisieren bestehen und bewegen sich beim
  Drücken abwärts/aufwärts. Aktuelle Phase bleibt abgesenkt. Keine zweite
  Innenkomposition für schmale Ansichten. Gemeinsame Würfel unverändert genutzt.
- Beispielablauf: sechs Verstärkungen vollständig verteilen, fester Angriff
  mit zwei Verteidigungsverlusten, einmaliges Festigen zwischen direkten
  Nachbarländern mit mindestens einer verbleibenden Truppe, Zugabschluss mit
  Zusammenfassung und getrennte ausdrückliche Übergabe. Anschließend Robin
  am Zug, eigene Aktionen gesperrt und fremde Reserve verborgen. Drei als
  Platzhalter gekennzeichnete Inventarkarten; keine echten Kartendaten.
- Vorhandene farbige Karte vollständig und im Originalseitenverhältnis;
  sechs Beispielmarkierungen, keine vollständige spielbare Kartensteuerung.
  Sammlung und Gestaltungsplan führen UI-003 jetzt als eigene lokale Tafel.
  UI-001/UI-002 bleiben erhalten. Normaler Spieleinbau und gestalterische
  Bewertung weiterhin offen; Party-Siegertreppchen unverändert offen.
- Sieben neue Ablaufprüfungen und zwei HTTP-Prüfungen erfolgreich. Alle
  freigegebenen Dateien erreichbar, private Dateien und POST gesperrt. Zehn
  bestehende Werkstattprüfungen sowie deren Geometrie-/Schrift-/Audio-Prüfungen
  bestanden; JavaScript-Syntax und git diff --check erfolgreich.
- Sichtbar im Browser geprüft: vollständiger Zug, Auswahl eines anderen
  Verstärkungslands, Phasensperre, Abbrechen/Escape ohne Truppenänderung,
  ungültige Verlegung, nur einmaliges Festigen, Zusammenfassung erneut öffnen,
  Übergabe/Warten und Inventar. Druckbewegung per tatsächlichem Klick und
  sichtbaren Transformationswerten erfasst. Plankenaufnahme gestartet/decodiert,
  danach Ton wieder ausgeschaltet; keine klangliche Abnahme. Schmale Rahmen
  320/390/800 px geprüft, keine horizontale Überbreite, Kartenverhältnis 1.0482
  wie Original. Hauptvorschau ohne erfasste Browserwarnungen/-fehler.
- Vorher 810 vorhandene Dateien und konsistente lokale Datenbanksicherung
  erfasst. Keine vorhandene Datei entfernt, alle drei persönlichen Rezept-
  dateien per Prüfsumme unverändert, keine veränderte Spieltabelle. Außer den
  neuen Tafeldaten nur Materialrenderer und Dokumentation/Log verändert.
  Nachweisdateien und Bildschirmbilder unter
  `runtime/conquest-console-20261025/`. Normales Spiel 8765 (24836), UI-001
  8770 (21772) und Werkstatt 8771 (24664) laufen weiter; nicht neu gestartet.


### 2026-10-25 – Lokal: Conquest-Avatarwerte und gespeicherten Button im Spiel erprobt

- Nutzer kann mit der großen UI-003-Konsole aktuell wenig anfangen. Sie bleibt
  als Arbeitsstand erhalten und wird nicht als Vorlage für das Spiel verwendet.
  Neue ausdrückliche Vorgabe ersetzt die frühere Beschränkung auf das aktive
  Spielerporträt: alle Armeen mit Truppen/Ländern am Avatar und Kartenanzahl
  als Plakette; Spielaktionen getrennt am unteren Rand nach den Referenzen.
- Gemeinsamer Porträtbaustein um genau diese Werteansicht und eine Avataransicht
  für die untere Aktion erweitert. Ganze Anzeigen skalieren proportional, keine
  Spielkopien ihrer Innenkomposition. Aktive Armee, eigener Platz, Testarmeen
  und ausgeschiedene Armeen gekennzeichnet. Eigene Kartenplakette öffnet das
  eigene Inventar. Fremde Kartenanzahl öffentlich, Identitäten/Missionen privat.
  Neue Anzahl wird ausschließlich aus dem gelesenen Zustand abgeleitet; keine
  Änderung gespeicherter Partien und keine zusätzliche Datenbankmigration.
- Große kombinierte Anzeige und doppelte Länderlegende ersetzt. Unten jetzt
  aktiver Avatar, Phase/kleine Fortschrittsmarken und nächste Hauptaktion.
  Vorrat nur während eigener Verteilung. Karte, Raum, normale Lobby/Rückkehr
  und Spielregeln erhalten. Schmale Fenster ordnen dieselben Porträts in zwei
  Spalten oberhalb der Karte an; gemessene Höhe fließt in die Kameraeinpassung
  ein, damit die Spieleranzeigen keine Länder verdecken.
- Gespeicherter Eintrag „Stormseed´s conquest“ gefunden. Er liegt als Formstand
  vor, enthält aber auch vollständige Einstellungen: grüne Steinoberfläche,
  acht Konturpunkte, Fredoka/manuell/geritzt, dezent/4, 300 ms und leichter
  Holzanschlag bei 20 %. Vollständigen Stand für zwei Spielaktionen übernommen:
  untere Hauptaktion sowie „Truppen verteilen“. Feste Kopie im Buttonprofil,
  keine automatische Bindung an spätere Werkstattänderungen; Quelldatei erhalten.
- Dieselbe Buttonfunktion und derselbe Materialrenderer wie in der Werkstatt.
  Button-Grund-CSS aus UI-001 nach static/comic-button.css zentralisiert; Tafeln
  laden dieselbe Datei. Relative Modulzuordnung und optionale Textur-/Audiobasis
  ermöglichen den gemeinsamen Einsatz hinter dem App-Präfix. Keine zweite
  Button-Komposition. Deaktivierte Beschriftung zentral besser lesbar. Normale
  Aktionslabels erhalten die bewegte Fläche; Truppenmeldung schließt erst nach
  dem Druckimpuls. Andere alte Spielbuttons und Generatorfeinschliff bleiben offen.
- 36 gezielte Python-Prüfungen erfolgreich, einschließlich öffentlicher Anzahl
  bei privatem Karteninhalt, unverändertem Spielzustand und gemeinsamer Asset-
  Auslieferung. 50 JavaScript-Verhaltenstests sowie Geometrie-/Schrift-/Audio-
  Prüfungen bestanden. Zehn bestehende Werkstatt-HTTP-Prüfungen und zwei
  Tafeldienst-Prüfungen erfolgreich; Syntax und git diff --check erfolgreich.
- Vier Personen im echten lokalen Conquest-Tisch sichtbar geprüft, ausschließlich
  mit eigener Datenbank runtime/conquest-hud-20261025/walkthrough.sqlite3 auf
  8767 (23568), eigener Sitzungscookie. Kein großer UI-003-Nachbau. Hauptaktion,
  Zugende, Übergabe, aktiver Avatarwechsel, gesperrte eigene Aktion beim Warten
  und eigene Karten am Avatar geprüft. Tatsächlicher Druckimpuls bis 2,72 Pixel
  und zurück, auch vor Schließen der Truppenmeldung; sechs Personen zusätzlich
  angesehen. 320/390/800-px-Einbettungen sichtbar kontrolliert. Nachweise und
  Bildschirmbilder im genannten Laufzeitordner; Vier-Spieler-Testpartie bleibt
  zum Ansehen geöffnet. Testdaten im Anschluss wieder auf Angriffsansicht gestellt.
- Vorher 821 bestehende Dateien und konsistente lokale Spieldatenbank gesichert.
  Keine vorhandene Datei entfernt, vier persönliche Entwurfsdateien per Prüfsumme
  unverändert. Normale lokale Anwendung kontrolliert mit derselben Datenbank und
  demselben Sitzungsschlüssel neu geladen, jetzt 8765 (24256). Health HTTP 200/ok,
  gemeinsame Dateien stimmen mit der Auslieferung überein. Alle 28 Inhaltstabellen
  unverändert; nur sqlite_sequence.login_days steigt durch den bestehenden
  Startablauf von 16 auf 17, ohne Loginzeile zu ändern. Nicht zurückgeschrieben.
  Echte Lobby Nr. 4 bleibt wartend; keine echte Partie für Prüfungen gestartet.
- Tafeldienste für neue gemeinsame Dateizuordnung neu geladen, ohne Browser-
  Entwürfe oder Ablagen zu ersetzen: 8770 (18204), 8771 (6652), 8773 (23540).
  Kein Kontakt zum Spielserver, keine Übertragung/Veröffentlichung. Gestaltungs-
  plan, Porträt-Dokumentation und Sammlung aktualisiert; kein allgemeiner
  Abschluss der Materialgestaltung oder des Generators behauptet.


### 2026-10-25 – Lokal: Angriffspfeile und direkte Angriffsbedienung am Brett

- Neue Nutzerpräzisierung ersetzt die zuletzt eingeführte untere Avatar-/Kasten-
  anordnung: unten nur die Spielaktion, im Angriff Quelle links, Ziel rechts
  und die Würfelwahl darüber. Der gesamte untere Bereich hat keinen Rahmen,
  Hintergrundkasten oder Avatar mehr. Die Armeeanzeigen am Brett bleiben.
  Verfügbarer Truppenvorrat während eigener Verteilung separat sichtbar.
- Gewöhnliche Länderauswahl öffnet keine Länder-Infobox mehr; die vollständig
  ersetzte Komposition und ihre CSS-Regeln entfernt. Angriffsvorbereitung und
  Ergebnis stehen direkt am Brett, ohne den früheren Angriffsdialog. Marken
  bleiben beschriftete Tastaturknöpfe; ergänzende 42-Länder-Auswahl wird nur bei
  Tastaturfokus eingeblendet. Notwendige Mengenwahl/Einrücken, Verteidigungswahl,
  Inventar und Zugzusammenfassung bleiben als bestehende Aktionsdialoge erhalten.
- Eigene Angriffsquelle zeigt Comic-Pfeile zu sämtlichen angreifbaren Feindländern.
  Eigene Nachbarn werden im Angriff nicht hervorgehoben. Gemeinsame geschlossene
  Pfeilform mit dunkler Kontur, Lichtkante, Schatten und Leuchten, für kurze
  Verbindungen seitlich an den Marken vorbeigeführt. Projektion folgt unverändert
  der Brettkamera; Alaska–Kamtschatka weiterhin als zwei Randabschnitte. SVG-
  Elemente bleiben bei Kamerabewegung bestehen. Armeefarben ausgewählter Marken
  bleiben erhalten; allgemeine Hover-Regel an der zuständigen Stelle korrigiert.
- Würfelzahl bei neuer Quellen-/Zielwahl und neuem Wurf am zulässigen Maximum,
  höchstens drei und stets eine Truppe zurück. Mausrad zurück verringert,
  vorwärts erhöht innerhalb der Grenzen; Klick/Pfeiltasten/Pos1/Ende ebenfalls
  nutzbar. Mausrad über dem Wähler bewegt nicht die Brettkamera. Polling erhält
  die manuelle Wahl. Ausstehende Verteidigung stellt Länder und die bereits
  abgegebene Würfelzahl nach Neuladen wieder her und sperrt doppelte Würfe.
- Genau eine Hauptaktion sichtbar: gewähltes Angriffspaar bietet „Angreifen“;
  Ziel erneut anklicken oder × hebt es auf und zeigt „Weiter zum Festigen“.
  Auf Nachfrage ausdrücklich bestätigt: zuerst Festigen, dann Zugende, kein
  automatisches Überspringen. Gespeicherter Buttonrenderer auch für Angreifen
  verwendet; keine zweite Button-Komposition. Überholte untere Avataransicht
  und Fortschrittspunkte vollständig entfernt.
- 57 JavaScript-Prüfungen erfolgreich, darunter sieben neue Prüfungen für
  Auswahl ohne Modal, Maximalwahl, Polling, Mausrad/Tastatur, Truppengrenze,
  Ausschluss eigener Nachbarn, Wiederaufnahme, Einfachausführung und Pfeilform.
  Bestehende Wiederaufnahmeprüfung auf Inline-Ergebnis angepasst: verpflichtendes
  Einrücken bleibt weiterhin gesichert. Syntax und git diff --check erfolgreich.
- Sichtbar mit eigenen neuen Testdaten geprüft: Venezuela → Brasilien, zwei
  Feindpfeile und unmarkiertes eigenes Peru; echtes Mausrad 3→2→3 bei unveränderten
  32 Grad. Angriff mit zwei Würfeln, echte Verteidigungsantwort, Ergebnis direkt
  am Brett und Rückkehr zur Maximalwahl. Ziel abgewählt, korrekter Übergang zu
  Festigen, Zugende und nächste eigene Verstärkung mit sichtbarem Vorrat vier.
  Transparenter Bereich: 0 Pixel Rahmen, kein Schatten und kein Avatar.
  320/390/800-Pixel-Einbettungen geprüft. Randverbindung besitzt zwei kurze
  Pfeile statt einer Verbindung durch die ganze Karte.
- Vorher 824 bestehende Dateien, normale PC-Datenbank und bestehende geöffnete
  Testpartie konsistent gesichert. Keine bestehende Datei entfernt, gespeicherte
  Buttonentwürfe unverändert. Abschlussvergleich: keine geänderte Tabelle in
  normaler PC-Datenbank oder bestehender Testdatenbank. Offener Angriff Ägypten
  → Südeuropa wartet unverändert auf Robin; nur die Oberfläche neu geladen.
- Prüfung ausschließlich mit neuer Datenbank unter
  runtime/conquest-attack-ui-20261025/ auf 127.0.0.1:8768 (23764), eigener
  Sitzungscookie, getrennt von der bestehenden Partie auf 8767. Keine normale
  Partie gestartet und keine Spielregel/Backend-Datenhaltung geändert. Vorhandene
  Dienste nicht neu gestartet, gemeinsame Tischdateien werden neu ausgeliefert.
  Eigene schmale Prüfansicht geschlossen; Angriffsbeispiel und bestehende Partie
  bleiben offen. Dokumentation und Prüfnachweise im genannten Laufzeitordner.
  Kein Spielserverkontakt, keine Übertragung oder Veröffentlichung.

## 2026-10-25 – Doppelklick-Starter für PC-Spiel und Werkstätten (nur lokal)

- Vorhandenen Starter Guesstimate-starten.cmd erweitert und
  Werkstaetten-starten.cmd ergänzt. Gemeinsamer Startweg über
  deploy/launch_local.cmd und deploy/start_local.py; nutzt vorhandenes Python,
  installiert nichts und öffnet nach erfolgreichem Start den Standardbrowser.
- Normales Spiel weiter ausschließlich auf 127.0.0.1:8765 mit bestehenden
  PC-Daten. Werkstatt-Starter verwaltet Comic-Tafel 8770, Button-Werkstatt 8771
  und archivierte Conquest-Zugtafel 8773. Die separaten Spieltests auf 8767/8768
  gehören ausdrücklich nicht zu diesen Startern.
- Laufende Dienste aus genau diesem Projektordner werden anhand von Prozess
  und HTTP-Antwort erkannt und weiterverwendet. Fremdbelegung bricht vor dem
  Start der Gruppe ab. Gemeinsame Windows-Dateisperre verhindert doppelte
  Starts bei gleichzeitigem Öffnen. Beenden und Fehlerbereinigung betreffen
  ausschließlich die im jeweiligen Startfenster neu gestarteten Prozesse.
- Neue gemeinsame Werkstattübersicht auf http://127.0.0.1:8771/sammlung;
  bestehende Werkzeuge verlinkt, alte Conquest-Tafel als früherer Entwurf
  eingeordnet. Keine zweite Implementierung der Werkstatt-Komponenten.
  Anleitung in LOKAL_STARTEN.md, README und Sammlung verknüpft.
- Sieben gezielte Prüfungen erfolgreich: bestehender Dienst ohne Neustart,
  fremder Port ohne Teilstart, falsche HTTP-Antwort, Startfehler und Zeitablauf
  mit begrenzter Bereinigung, Pfade mit Leerzeichen und reine Statusprüfung.
  Echter Kaltstart einer getrennten Werkstatt auf Testport 52268 mit eigenem
  Entwurfsordner: zwei gleichzeitig gestartete Prozesse erzeugten genau einen
  Dienst, der zweite verwendete ihn weiter; danach nur eigenen Testdienst
  beendet und freien Anschluss nachgewiesen. Syntax und git diff --check geprüft.
- Beide tatsächlichen CMD-Dateien mit unterdrücktem Browser erfolgreich
  ausgeführt; alle bestehenden Dienste weiterverwendet. Nur Button-Werkstatt
  für die neue Übersichtsroute neu gestartet (13604). Normaler PC-Spielserver
  unverändert 24256, Comic-Tafel 18204 und Archiv 23540 weiterverwendet.
  Übersicht, Links zur Button-Werkstatt und Comic-Tafel sowie Archivaufklappen
  im Browser sichtbar geprüft. Übersicht bleibt als eigener Tab geöffnet.
- Bestehenden Arbeitsstand vorab gesichert. Abschlussvergleich: keine geänderte
  Tabelle der normalen PC-Datenbank, unveränderter Sitzungsschlüssel und alle
  vier vorhandenen Buttonentwurfsdateien unverändert; keine bestehende Datei
  entfernt. Nachweise unter runtime/local-launcher-20261025/.
- Kein externer Spielserverkontakt, keine Übertragung, keine Veröffentlichung
  und keine Firewall-/Routeränderung. Zugriff von anderen Geräten oder aus
  dem Internet bleibt eine separate, noch nicht eingerichtete Erweiterung.

## 2026-10-25 – Lokale Conquest-Testrunde neu gestartet, Mitspieler simuliert

- Nutzer verschiebt Internetbetrieb und beauftragt ausdrücklich den Neustart
  der geöffneten Testrunde sowie regelkonforme Beispielzüge der Mitspieler.
  Ausschließlich Tisch 3 der bestehenden Vorschau auf 127.0.0.1:8767 neu
  aufgestellt. Gleiche vier Testkonten, Mitgliedschaften, Gastgeber und
  Einstellungen einschließlich geheimer Missionen erhalten. Normale zufällige
  Länderzuteilung und Startaufstellung verwendet; keine erfundenen Würfel oder
  frei veränderten Truppenzahlen. Laufenden Vorschauprozess nicht neu gestartet.
- Lokaler Simulator unter offline-preview/conquest-opponents/: Robin, Bela und
  Alex setzen auf, verstärken, greifen höchstens zweimal pro Zug an, verteidigen,
  besetzen eroberte Länder, tauschen Pflichtkartensätze, festigen einmal und
  geben weiter. Alle Spielzüge laufen mit getrennten Testsitzungen über die
  bestehende normale Spielaktionsroute mit Mitgliedschaft, CSRF, Revision und
  unveränderter zentraler Regelprüfung. Keine zweite Spielregelimplementierung.
- Stormseed bleibt vollständig manuell, einschließlich Startaufstellung,
  Verteidigungswürfeln und Einrücken. Simulator wartet auf diese Entscheidungen
  und läuft danach weiter. Prozess 7268 bleibt im Hintergrund aktiv, bis
  Spielende, Stopdatei oder manuellem Beenden. Doppelstart wird durch eine
  Windows-Dateisperre abgewiesen; zweiten Start tatsächlich geprüft.
- Datenbank- und Testkontenzuordnung im Simulator strikt auf diese vorhandene
  Vier-Personen-Vorschau begrenzt. Die anderen Testpartien, die normale
  PC-Datenbank und die Werkstätten werden nicht bedient. Vorhandene Daten einmal
  vor der anschließenden Nutzerpräzisierung geprüft/gesichert; nach „keine
  laufenden Spiele sichern“ keine weiteren Sicherungen angelegt.
- Sieben gezielte Prüfungen erfolgreich: keine menschliche Platzierung oder
  Verteidigungswahl, einzelne legale Starttruppe, Pflichtkartentausch,
  Mindestbesetzung, mehrere vollständige Runden durch die echte Regelfunktion,
  Spielende und reservierter abwesender Spieler. Syntax und git diff --check
  erfolgreich. Keine Änderungen an den normalen Spielmodulen oder Tischdateien.
- Browserprüfung: neue Aufstellung sichtbar, alle drei Mitspieler setzen
  automatisch je eine Einheit, anschließend wartet das Spiel auf Stormseed.
  Während der weiteren Prüfung spielt der Nutzer bereits selbst: bis zur
  Datenprüfung 30 automatisch ausgeführte Mitspieleraktionen, keine vom
  Simulator eingereichte Stormseed-Aktion, keine Fehlermeldung. Keine geänderte
  Tabelle in der normalen PC-Datenbank; in der Vorschau außerhalb von Tisch 3
  ebenfalls keine geänderten Datensätze. Nachweise und Simulatorausgabe unter
  runtime/conquest-opponents-20261025/. Kein externer Serverkontakt oder Upload.
- Anschließend auch im laufenden Browser sichtbar: Startaufstellung vom Nutzer
  abgeschlossen, Robin verstärkt mit drei Einheiten und greift Weststaaten →
  Oststaaten mit zwei Würfeln an (Revision 93). Menschliche Verteidigungsauswahl
  erscheint und wird vom Simulator bewusst abgewartet. Aufnahme testrunde.png.

## 2026-10-25 – Automatische Verteidigung ohne Fenster oder Würfelknopf (lokal)

- Neue ausdrückliche Nutzervorgabe ersetzt die bisherige freie
  Verteidigerwahl: bei genau einer Einheit ein Würfel, ab zwei Einheiten stets
  zwei. Abweichung vom bisher herangezogenen offiziellen Hasbro-Regelheft
  benannt und in CONQUEST_RULESET.md als gewünschte Projektregel festgehalten.
- Anschließende Präzisierung: Solange keine manuell zu bedienenden Würfel
  implementiert sind, braucht die Verteidigung weder Fenster noch eigenen
  Würfelknopf. Server löst neue Angriffe einschließlich maximaler Verteidigung
  direkt in derselben geprüften Transaktion auf. Zufallswürfe und alle
  übrigen Kampf-/Besetzungsregeln bleiben erhalten. Ein späterer manueller
  Würfelmodus ist hierdurch weder implementiert noch vorgetäuscht.
- Alten Verteidigungsdialog samt Auswahl und Ereignisbehandlung vollständig
  aus der gemeinsamen Tischkomponente entfernt. Kampfergebnis über denselben
  bestehenden Anzeigenbaustein direkt am Brett: abgewehrt, verteidigt mit
  Verlust oder konkretes Land verloren. Während der Verteidigung keine
  Angriffswürfelauswahl und keine untätigen Aktionsknöpfe. Eigene
  Verteidigungsergebnisse bleiben auch bei schnellen gegnerischen Phasen-
  und Zugwechseln lesbar, bis eine neue Auswahl oder Aktion sie ablöst.
- Kompatibilität für bereits gespeicherte offene Angriffe: ursprünglicher
  Verteidiger löst den alten Auftrag beim Laden automatisch genau einmal auf;
  feste Würfelzahl wird aus der tatsächlichen Garnison bestimmt. Übergebene
  alte Clientzahlen können sie nicht reduzieren. Angreifer-/Verteidiger-ID im
  Kampfergebnis erlaubt eindeutige Ergebniszuordnung auch nach Gebietsverlust.
- 76 Python-Prüfungen und sämtliche 60 JavaScript-Prüfungen bestanden.
  Darunter automatische Auflösung bei 1/2/5 verteidigenden Einheiten,
  Wiederaufnahme alter Anfragen, ignorierte übergebene Würfelzahlen, gesperrte
  Doppelabgabe, Pflichtbesetzung und sichtbare Ergebnisinfo ohne Fenster oder
  Bedienknöpfe, auch nach schnellen Phasen- und Zugwechseln. git diff --check
  erfolgreich. Keine CSS-Korrekturblöcke oder zweite Anzeigeimplementierung.
- Aktive Testrunde auf 8767 ohne Neuaufstellung wieder aufgenommen. Dafür
  vorhandenes Laufzeitskript um --resume ergänzt: liest dieselben Testfälle
  und startet keine erneute Datenerzeugung. Testserver 16356, gleiche Sitzung,
  Startzeit und Mitgliedschaften. Simulator 7268 läuft weiter. Browserprüfung:
  bisher blockierter Angriff Weststaaten → Oststaaten automatisch aufgelöst;
  gegnerische Züge laufen weiter. Später direkt am Brett sichtbar „Indien:
  Angriff abgewehrt.“ mit einem Verteidigungswürfel bei einer Einheit. Nutzer
  hat anschließend selbst regulär weitergespielt und Länder besetzt; keine
  eigenen Spielentscheidungen für ihn ausgeführt.
- Normalen lokalen Prozess auf 8765 ebenfalls mit derselben PC-Datenbank
  neu gestartet (24760, Health ok), damit ausgelieferte Oberfläche und
  Regelprozess zusammenpassen. Keine geänderten normalen Dateninhalte,
  Konten oder Spielstände. Einzige Metadatenänderung der PC-Datenbank:
  sqlite_sequence.login_days 18→19 durch bestehende Startinitialisierung;
  Tabelle login_days selbst unverändert. Keine neuen Spielstandssicherungen.
- Prüfnachweise unter runtime/conquest-auto-defense-20261025/. Andere
  Werkstätten unverändert. Keine Übertragung, kein Kontakt zum externen
  Spielserver und keine Veröffentlichung.

## 2026-10-25 – Mengenwahl am Brett, automatischer Phasenwechsel und Kartenbesitz

- Verstärkung und Pflicht-Einrücken auf ausdrücklichen Nutzerwunsch ohne
  zusätzliche Fenster. Ein gemeinsamer Mengenwähler im bestehenden unteren
  Brettbereich für Verstärken, Einrücken und das bisher bereits gemeinsam
  implementierte Festigen: Zahlenfeld, ±, Schieber, zulässiger Vorrat bzw.
  Mindest-/Höchstzahl und Bestätigung über denselben gespeicherten Comic-
  Buttonrenderer. Kein neuer Rahmen oder Avatarbereich. Alten Begrüßungs-
  und Mengendialog samt Ereignissen und ersetzten CSS-Regeln entfernt.
- Mengenwahl verändert noch keine Truppe. Speichern ist ausdrücklich zu
  bestätigen, währenddessen gegen Doppelabgabe gesperrt. Pflichtbesetzung
  kann weder abgebrochen noch durch Auswahl eines anderen Landes umgangen
  werden. Polling erhält eine gewählte Menge. Fehler bleiben sichtbar und
  können mit derselben Menge erneut bestätigt werden.
- Nach letzter Verstärkung beantragt die Oberfläche automatisch genau einen
  regulären, servergeprüften Phasenwechsel. Eine noch mögliche oder
  verpflichtende Tauschentscheidung verhindert die Automatik. Bisherige
  Tauschregel ausdrücklich erläutert und beibehalten: nur vor der ersten
  Platzierung. Kartenangebote prüfen nun tatsächliche gültige Sätze statt
  bloß mindestens drei Handkarten. Pflicht ab fünf Karten unverändert.
- Anschließenden Wunsch nach Besitzkennzeichnung auf Karten mit umgesetzt.
  Gemeinsame Kartenkomponente für Inventar und Gewinnkarte: klarerer Comic-
  Titel, eigener Besitz grün mit „Dein Gebiet“, sonst aktueller Besitzer;
  möglicher +2-Gebietsbonus oder bereits verbrauchter Bonus sichtbar. Joker
  ohne Besitzbonus. Regelhinweis und Gebietsauswahl erklären: +2 nur auf eines
  der eigenen Gebiete im eingetauschten Satz, höchstens einmal pro Zug. Die
  bisherige Grundillustration bleibt ein Arbeitsstand, keine finale Freigabe.
- 77 Python-Prüfungen und 65 JavaScript-Prüfungen erfolgreich. Neue Prüfungen
  für tatsächliche Kartensätze, Besitz-/Bonus-/Jokermarkierung, Bestätigung
  ohne vorherige Platzierung, erhaltene Menge bei Polling, Teilverstärkung,
  automatische letzte Platzierung, Schutz offener Kartentausche, verpflichtende
  Inline-Besetzung, Doppelabgabe und erneute Bestätigung nach Speicherfehler.
- Sichtbare Prüfung mit ausschließlich neuen getrennten Daten auf 8769:
  Grönland 2→4 mit zwei gesetzten Einheiten, Vorrat danach eins; letzte Einheit
  auf Alberta, direkter Übergang zum Angriff ohne Weiter-Knopf. Pflicht-
  Einrücken Ostaustralien → Westaustralien mit Bereich 3–5, ausdrücklich vier
  gewählt und bestätigt, danach Quelle zwei/Ziel vier. Keine Modalöffnung.
  Fünf Testkarten: eigene Island/Ural, fremde Indonesien/Ägypten und Joker
  korrekt unterschieden. Gültigen Satz gewählt, Ural als Bonusgebiet
  bestätigt: +4 Vorrat (3→7), +2 direkt auf Ural, nur zwei Handkarten übrig.
- Laufende Nutzerpartie auf 8767 über --resume fortgesetzt (10896), gleicher
  Tisch, gleiche Startzeit und Mitgliedschaften; Simulator 7268 bleibt aktiv.
  Nutzeransicht aktualisiert, bisherigen Überblick von 82 Grad wieder
  eingestellt. Mengen-/Verstärkungsdialog in der tatsächlichen Seite nicht
  mehr vorhanden, keine eigenen Platzierungen oder Kartentausche für den
  Nutzer ausgeführt. Normalen lokalen Prozess passend neu geladen (25436).
- Keine neuen Spielstandssicherungen, kein externer Kontakt, kein Upload.
  Nachweise und eigene QA-Daten unter runtime/conquest-inline-20261025/.
  git diff --check erfolgreich. Größenprüfung über den damaligen Frame-
  Zugriff lieferte keine verwertbaren Maße; daraus keine mobile Sichtprüfung
  abgeleitet.
- Eigenen QA-Dienst 23808 und seine Prüftabs nach Abschluss beendet. Nutzer-
  runde und Simulator bleiben aktiv. Normale PC-Inhaltstabellen unverändert;
  bestehende Startinitialisierung erhöht ausschließlich die Metadatenfolge
  sqlite_sequence.login_days durch den Neustart von 19 auf 20, ohne einen
  Login-Datensatz anzulegen.

## 2026-10-25 – Zugende am Brett, Zughinweis und nähere Kamera (lokal)

- Auf Nutzerwunsch kein separates Zugende-Fenster mehr: ein Klick auf den
  vorhandenen Comic-Knopf „Zug beenden“ führt Kartenvergabe und Übergabe in
  einer regulären, atomaren Aktion `finish` aus. Wiederverwendet unverändert
  die bestehenden Regeln für Abschluss und Zugwechsel; genau eine Revision,
  keine zweite Vergabe durch Doppel-Klick oder Wiederholung. Alte gespeicherte
  Endzustände können ohne erneute Kartenziehung weitergegeben werden.
- Erhaltene Karte als nicht blockierender Hinweis rechts am Brett. Nutzt die
  gemeinsame Kartenkomponente als Ganzes proportional skaliert. Übergabe
  erfolgt sofort, Anzeige bleibt lesbar, ist ausblendbar und nach Neuladen
  wiederherstellbar. Private letzte Zugbelege werden je Armee gespeichert,
  öffentlich jeweils nur an deren eigenen Betrachter geliefert. Zugende-
  Dialog, zweiter Bestätigungsknopf und vollständig ersetzte CSS entfernt.
- Nachfolgend beauftragten modernen „Dein Zug!“-Hinweis ergänzt: verfügbare
  Armeen, ohne Pflicht nach 1000 ms ausgeblendet; Polling startet die Zeit
  nicht ständig neu. Bei Tauschpflicht dauerhaft mit „Zu den Karten“ über
  denselben Buttonrenderer. Nach erfülltem Tausch aktualisierte Armeezahl
  und anschließendes Ausblenden. Kein Modal und keine eigene Spielentscheidung.
- Kameraausrichtung konsolidiert: Sitzposition von 84 auf 98 Prozent der
  verfügbaren Kartenbreite, an der unteren Bediengrenze ausgerichtet statt
  fest oben verankert; der freie Boden vor dem Tisch entfällt weitgehend.
  Überblick bis 99,5 Prozent Breite, übrige vertikale Fläche zentriert und
  knappere Sicherheitsabstände. Gleiche Linse, 32–82 Grad und stetiger Verlauf;
  vollständige unveränderte Karte inklusive Titel/Legende und 42 Marken
  erhalten. Kein Bild gestreckt oder neues Brett aufgelegt.
- Während der Arbeit nachgefragten Kartenbonus erläutert: insgesamt +2 auf
  genau eines der eigenen Länder im Satz, höchstens einmal pro Zug. Karte
  nennt jetzt „Für den +2-Bonus wählbar“. Bei mehreren passenden Ländern
  explizite Auswahl mit leerer Vorauswahl nötig; vorher kein Eintausch.
  Keine Änderung am Auszahlungsbetrag oder an der Fünf-Karten-Tauschpflicht.
- 79 Python-Prüfungen und 73 JavaScript-Prüfungen bestanden. Neu geprüft:
  atomare Übergabe mit genau einer Karte/Revision, veraltete Wiederholung,
  private Wiederaufnahme, alte bereits abgegebene Endzustände, direkter
  Wechsel auch im reinen Beispielmodell, Ein-Klick-Controller, bleibende/
  ausblendbare Karte ohne Dialog, einmalige alte Wiederaufnahme, beide
  Zughinweiszustände mit 1000-ms-Zeitgeber und eindeutige Bonusgebietswahl.
  Kamera über alle Zwischenwinkel und sechs Bildschirmverhältnisse geprüft,
  ebenso Projektion, Marker und Abstand zur Bedienung. git diff --check ok.
- Sichtbar mit ausschließlich neu erzeugten separaten Daten auf 8769 geprüft:
  Pflicht-Hinweis mit drei Armeen, Kartenknopf öffnet Inventar; nach Tausch
  sieben Armeen und Hinweis ausgeblendet. Andere Prüfrunde: Besetzung bestätigt,
  zu Festigen gewechselt, einmal „Zug beenden“ → Robin ist am Zug, Länderkarte
  Alaska am Rand, kein offener Dialog. Beide Kameraposen aufgenommen, ganze
  Karte und alle 42 Marken sichtbar. Nachweise unter
  runtime/conquest-endview-20261025/.
- Nutzer hat währenddessen die separate Prüfrunde auf 8769 mitbedient; diese
  Vorschau bleibt deshalb erreichbar (2076). Ursprüngliche Runde auf 8767
  nach zwischenzeitlich geschlossenem Browser-Tab erneut geöffnet und direkt
  als fortgesetzte Nutzeransicht markiert. Gleiche Partie, Startzeit und
  Mitgliedschaften, kein Neustart der Runde. Eigener Zug mit 35 verfügbaren
  Armeen sichtbar; regulärer Hinweis verschwindet, alter Zugende-Dialog fehlt.
  Testprozess 24924 und normaler PC-Prozess 19320 verwenden die aktualisierten
  Regeln, Simulator 7268 weiterhin vorgesehen; kein neuer Spielstand angelegt.
- Keine neuen Spielstandssicherungen, kein externer Spielserverkontakt oder
  Upload. Grundgrafik und angekündigte manuelle Würfel bleiben Arbeitsstände.
- Abschluss: Simulator 7268 aktiv und lokale Health-Prüfung ok. Normale
  PC-Inhaltstabellen unverändert; Startinitialisierung erhöht lediglich
  sqlite_sequence.login_days von 20 auf 21. Keine neue Anmeldung oder
  Änderung in der Tabelle login_days. Ursprüngliche Runde und separate
  Prüfansicht bleiben zum Anschauen geöffnet.


## 2026-10-25 – Kartenhand, Siegeranzeige, Missionsstart und bereinigte Lobby (lokal)

- Auf Nutzerwunsch Inventar- und Siegerdialog entfernt. Länderkarten als
  kompakte Hand am Brettrand: erster Klick vergrößert, nächster Klick auf eine
  Karte wählt sie aus/ab (höchstens drei). Avatarplakette und erhaltene Karte
  öffnen dieselbe Hand. Keine zweite Kartenkomposition; ein Kartenrenderer,
  jeweils als Ganzes skaliert. Auswahl bleibt bei Aktualisierungen erhalten.
  Gültiger Satz, Tauschpflicht, Besitzmarkierung und genau ein ausgewähltes
  Bonusland unverändert. Der Zughinweis verdeckt keine vergrößerten Karten.
- Siegeranzeige am Brett mit gemeinsamem Spielerporträt, Sieggrund und
  Endwerten; einklappbar und über Ergebnis ansehen erneut aufrufbar. Normale
  Revanche und Verlassen weiter über die vorhandenen gespeicherten Aktionen.
  Neue Gewinner-/Verlierer-Avatargrafiken weiterhin offen. Kein Party-Podium
  als fertig ausgegeben. Kartentausch, Revanche und Missionsbestätigung nutzen
  denselben gespeicherten Comic-Buttonrenderer wie die bisherigen Hauptaktionen.
- Geheime Auftragskarte erscheint beim Spielbeginn als bewusst beauftragter
  eigener Dialog. Privater Missionssatz bleibt bei den Länderkarten, Karte
  erneut aufrufbar. Gesehene Anzeige je Partie/Spieler lokal gemerkt; Revanche
  mit neuer Startzeit zeigt den neuen Auftrag wieder. Keine fremde Mission
  freigegeben und kein Missionstext in Browserpräferenzen gespeichert.
- Nutzer hat bestätigt: Länder weiter zufällig zuteilen, übrige Starttruppen
  selbst reihum setzen; lediglich überflüssige Zuteilungsoption entfernen.
  Überholte Material-/Figuren-/Würfelstil-Auswahl aus der Lobby genommen.
  Aktuell ein Weltbrett, Truppenpunkte und automatische Auswertung sichtbar;
  echte Würfel, weitere Bretter und Armeefiguren noch nicht auswählbar.
  Gespeicherte alte Stilwerte bleiben erhalten.
- Spielergrenze 2–6 speicherbar, nie unter der vorhandenen Belegung; Beitritt
  und gemeinsame Übersicht beachten sie. Host kann unterschiedliche Farben
  vor dem Start wählen. Neue Partien speichern die Farbe unabhängig vom
  Sitzplatz; Farbmissionen richten sich danach. Alte Partien bleiben bei
  ihrer bisherigen Zuordnung. Additive lokale Datenbankfelder player_limit
  (Standard 6) und color_index; keine alten Zustände umgeschrieben.
- 82 Conquest- und neun gemeinsame Lobby-Pythonprüfungen erfolgreich,
  83 JavaScriptprüfungen erfolgreich. Neu: Spielergrenze/Beitritt, doppelte
  Farben abweisen, Farberhalt im Spiel und richtige Farbmission, zweistufiger
  Kartenklick, Auswahl bei Polling, Mission einmalig/erneut aufrufen sowie
  einklappbarer Endstand. Bestehende Regeln und Privatheit weiter geprüft.
- Sichtbare Prüfung mit getrennten neuen Daten auf 8774: fünf Karten,
  drei per Kartenklick gewählt, Venezuela ausdrücklich als Bonusland gewählt;
  Tausch +4 Vorrat und genau +2 dort, zwei Karten verbleiben. Endstand
  eingeklappt/erneut geöffnet, Revanche, 3/3 Plätze und Orange/Grün gespeichert;
  neue Runde mit diesen Farben und neuem Missionspopup gestartet. Große und
  kleine Kartenansicht sowie tatsächliche 390-Pixel-Einbettung angesehen.
  Bilder und Prüfprotokolle unter runtime/conquest-cards-20261025/.
- Nutzerlobby 6 sichtbar mit bereinigter Ausstattung aktualisiert. Lokale
  Testanwendung mit --resume fortgesetzt (24048), normale PC-Anwendung neu
  geladen (21532). Lesender Vergleich aller 28 ursprünglichen Inhaltstabellen
  beider Datenbanken: unverändert. Sieg von Stormseed in Partie 3 bleibt bei
  Revision 642, Zug 45, Nordamerika/Australien und derselben Startzeit;
  wartende Lobby 6 bleibt Revision 0. Keine Nutzer-Spielaktion ausgeführt.
  Keine neuen Spielstandssicherungen, kein externer Serverkontakt/Upload.
- Abschluss: eigene Zusatzvorschau 17952 und ihre Prüftabs geschlossen.
  Nutzerlobby bleibt offen. Beide verbleibenden lokalen Spieldienste liefern
  HTTP 200 am Health-Endpunkt. Mausrad über der vergrößerten Kartenhand
  verändert den Kamerawinkel nicht; sichtbar bei 32 Grad geprüft.
  git diff --check und JavaScript-Syntaxprüfung erfolgreich.


## 2026-10-25 – Nutzerkorrektur: freie Kartenhand direkt am Avatar (lokal)

- Die zuvor gebaute breite grüne Kartenablage wurde vom Nutzer als zu groß
  und zu verdeckend zurückgewiesen. Ersetzt durch eine kleine freie Hand,
  die direkt vom eigenen Avatar aus aufgefächert wird. Kein Hintergrund,
  Rahmen, Inventartitel, Leertext, Regelblock oder historische Tauschangabe.
  Auch den zusätzlichen Kartentauschblock in der unteren Zugleiste entfernt.
- Kleine Hand anklicken zum Aufklappen, Karten anklicken zum Aus-/Abwählen.
  Avatarplakette klappt ebenfalls auf/zu; X/Escape klappt ein. Auswahl bleibt
  bei Polling erhalten. Die kanonische Kartenkomponente wird weiterhin nur
  proportional skaliert. Die gemeinsame Porträtkomponente stellt ihren
  Avataranker bereit; keine nachgebaute Porträtkomponente.
- Hand folgt dem eigenen gespeicherten Spieler, unabhängig vom aktuellen
  Zugführer. Position folgt Fenstergröße und Roster-Scrollen. Je nach freiem
  Platz nach rechts/links, bei tiefem Sitz nach oben aufgefächert; keine Hand
  für einen aus der Spieleranzeige herausgescrollten Avatar. Enger Fächer auf
  kleinen Bildschirmen, statt einer separaten mobilen Inventargestaltung.
- Unter der Hand erscheint nur bei gültigem Satz die kleine Tauschaktion.
  Bei mehreren Bonusländern bleibt eine ausdrückliche Wahl nötig, vorher
  keine Abgabe. Erfolg über Kartenanzahl/Truppenwerte sichtbar und barrierefrei
  angekündigt; Speicherfehler bleiben kurz sichtbar und erlauben Wiederholung.
- Die neue Anforderung ohne Text unter der Hand ersetzt die dort zuvor
  dauernd angezeigte Missionszeile: Mission über einen kleinen Stern am
  eigenen Avatar (Satz im Tooltip), Auftragskarte weiterhin erneut aufrufbar.
  Das beauftragte Missionspopup beim Spielbeginn bleibt erhalten.
- 77 JavaScriptprüfungen, Syntaxprüfung und git diff --check erfolgreich.
  Gezielt geprüft: Karte zuerst aufklappen/dann wählen, Auswahl bleibt bei
  Polling, Tauschaktion nur für gültige drei Karten, ausdrückliche Bonuswahl,
  Auftrag einmalig am Start und über Avatar-Stern erneut aufrufbar.
- Sichtbar mit getrennten Daten auf 8774 geprüft: transparente Hand mit fünf
  Karten, aufgeklappt ca. 487 × 226 px statt der vorherigen 1100 × 600 px.
  Kein Textblock oder Paneelhintergrund. Tausch durch Testspieler Robin:
  fünf → zwei Karten, +4 Vorrat, genau +2 auf das gewählte Ostkanada. Echte
  390-Pixel-Einbettungen für eigenen linken/rechten Avatar geprüft; Fächer
  passt seine Überlappung an. Aufnahmen unter
  runtime/conquest-avatar-hand-20261025/.
- Conquest-Daten beider lokalen Anwendungen lesend gegen den vorherigen
  Prüfpunkt verglichen: unverändert. In der Nutzer-Testdatenbank sogar alle
  28 ursprünglichen Inhaltstabellen unverändert. Im normalen PC-Bestand
  unterscheiden sich seit dem älteren Prüfpunkt andere Party-/Playtable-/
  Würfeltabellen; diese weder angefasst noch zurückgeschrieben. Kein
  Neustart ihrer Dienste nötig, nur lokale Oberflächendateien geladen.
  Keine neuen Spielstandssicherungen oder externen Übertragungen.
  Zusätzliche Prüfvorschau 22596 bleibt auf 8774 samt Prüftab bewusst zum
  Anschauen offen; bisherige Nutzerlobby 6 ebenfalls erhalten.


## 2026-10-25 – Gleichgerichtete Kartenüberlappung (lokal)

- Nutzer bestätigt die überlappende aufgeklappte Hand, verlangt aber eine
  einheitliche Richtung statt doppelter Verdeckung der Mongolei. Jede Karte
  liegt jetzt genau vor der vorherigen, auch bei Hover/Fokus und Auswahl.
  Nur leichtes Anheben, kein Springen vor beide Nachbarn mehr.
- Breiten und Avataranker erhalten. Fächerdrehung von -5 bis +5 Grad durch
  kleine feste Unregelmäßigkeiten von -1,4 bis +1,1 Grad und 0–2 Pixel Versatz
  ersetzt. Keine zufällige Neuordnung bei Aktualisierungen. Hand bildet ihren
  eigenen Stapelkontext, damit X und Missionssymbol weiterhin erreichbar sind.
- 77 JavaScriptprüfungen und git diff --check erfolgreich. Browserprüfung auf
  der bestehenden getrennten Prüfrunde: feste Stapelfolge 1–5, Mongolei
  angewählt/abgewählt ohne Änderung der Reihenfolge. Auswahl anschließend leer
  wie zuvor, Spielaktion nicht ausgeführt. Bildnachweis unter
  runtime/conquest-avatar-hand-20261025/einheitliche-ueberlappung.png.
  Vorschau und bisherige Nutzerlobby bleiben geöffnet. Keine Datenbankänderung,
  kein Dienstneustart und keine externe Übertragung für diese Korrektur.


## 2026-10-26 – Spielerzahl aus Beitritten, drei Testmitspieler in Lobby 6

- Nutzer hat die feste Spielerzahl-Vorgabe korrigiert: Teilnehmerzahl ergibt
  sich ausschließlich aus den Beitritten. Auswahl aus Host-/Gastlobby entfernt.
  Allgemeine Grenze von sechs Spielern bleibt; alte gespeicherte player_limit-
  Werte beeinflussen weder Beitritt, Übersicht noch Start. Bestehende Spalte
  nicht gelöscht oder rückgeschrieben, bei neuen Datenbanken nicht mehr erzeugt.
- Robin, Bela und Alex über die vorhandenen lokalen Testkonten und normalen
  Beitrittsrouten zur wartenden Nutzerlobby 6 hinzugefügt. Keine Konten erstellt,
  kein direkter Datenbankeingriff, kein automatischer Spielstart. Vier aktive
  Spieler sichtbar, Startknopf für den Host freigegeben, kein Spielerzahlfeld.
- Neuer begrenzter lobby_runner.py wartet auf manuellen Start und bedient nur
  die überprüften Konten 7/8/9 auf Port 8767 in dieser Testlobby. Eigener Platz
  17 bleibt durch Policy und beim Senden ausgeschlossen; Mitspieler 18/19/20.
  Separate Sitzungen je Bot, normale Aktionsrouten/Revisionen, gleiche geprüfte
  Regelstrategie wie zuvor. Nach Spielende stoppt die Simulation. Kein Neustart
  oder Zurücksetzen der abgeschlossenen Partie 3.
- Nutzer hat während der Prüfung selbst gestartet und die Startaufstellung
  begonnen. Simulator hat darauf reagiert; wiederholte reguläre Platzierungen
  von 18, 19 und 20 beobachtet, keine Aktion für 17. Laufender Spieltisch mit
  vier Armeen sichtbar geprüft, Kamera und eigene Spielentscheidungen beim
  Nutzer belassen. Nachweis unter runtime/conquest-lobby6-20261025/.
- 83 Conquest-Pythonprüfungen und neun gemeinsame Lobbyprüfungen erfolgreich.
  Neu geprüft: alte gespeicherte Grenze 2 hält den dritten Beitritt nicht auf,
  Übersicht weiterhin 3/6, alte Formulare können keine Zielzahl erzwingen;
  neue Mitgliedsnummern 17–20 halten menschliche Züge manuell und Botzüge legal.
  git diff --check erfolgreich.
- Lokale Dienste mit erhaltenem Bestand neu geladen: Testanwendung 16120 mit
  --resume, normaler PC-Dienst 20108. Simulator 19940 bleibt im Hintergrund
  aktiv. Alter Endstand von Partie 3 bleibt completed/Revision 642 und mit
  derselben Startzeit erhalten. Keine neuen Spielstandssicherungen und keine
  externen Übertragungen. Zusätzliche Karten-Prüfvorschau bleibt getrennt.


## 2026-10-26 – Automatisch +2 auf jedes eigene Gebiet eines Kartensatzes

- Nutzer korrigiert die bisherige Projektregel ausdrücklich: keine Wahl eines
  einzelnen Bonuslands. Jeder eingetauschte eigene Gebietsbesitz erhält direkt
  zwei Einheiten, zwei passende Karten ergeben insgesamt vier, drei insgesamt
  sechs. Gilt bei jedem gültigen Satz im Zug; kein einmaliger Zwei-Einheiten-
  Deckel mehr. Fremde Gebiete und Joker bekommen keinen direkten Gebietsbonus.
  Regulärer globaler Tauschwert und Pflichttausch bleiben unverändert.
- exchange berechnet den Bonus ausschließlich aus den drei tatsächlich
  eingetauschten Karten und dem aktuellen Brettbesitz. Alle Ziele in derselben
  regulären Aktion gespeichert. Alte bonus_territory-Eingaben können nichts
  umleiten oder unterdrücken; veraltete territory_bonus_received-Metadaten
  begrenzen neue Tausche nicht. Keine nachträgliche Auszahlung alter Tausche.
- Gebietsauswahl, Selektor-Logik und ersetzte CSS entfernt. Client und Bots
  senden nur die gewählten Karten. Eigene Karte nennt „+2 hier beim Eintausch“;
  alle ausgezahlten Länder im barrierefreien Tauschbeleg aufgeführt. Regeln
  und aktuelle Dokumentation auf diese ausdrückliche Projektregel angepasst.
- 85 Python- und 77 JavaScriptprüfungen erfolgreich. Gezielt: null/ein/zwei/
  drei eigene Kartengebiete, weitere Sätze im selben Zug trotz altem Flag,
  keine Auszahlung auf fremdes oder nicht eingetauschtes Gebiet, Joker,
  ungültige Auswahl ohne Teilzahlung und unveränderte Revisionssicherung.
- Während der Umsetzung meldete der Nutzer noch die alte Fehlermeldung aus
  dem laufenden Python-Prozess. Nach bestandenen Prüfungen lokale Prozesse
  aktualisiert: Nutzerpartie 24016 mit --resume, PC-Dienst 7076, Kartenprüfung
  23812 und alte idempotente Zugende-Prüfung 23188. Simulator 23692 übernimmt
  dieselbe laufende Runde mit der neuen Policy; keine neue Partie erzeugt.
- Browser-Tab der Partie war zwischenzeitlich geschlossen; denselben Tisch 6
  erneut geöffnet und als Nutzeransicht markiert. Nutzer hat danach selbst
  seinen zuvor gewählten Satz abgegeben: Südafrika und Neuguinea jeweils
  1→3, Afghanistan als fremdes Gebiet ohne Bonus; acht reguläre Tauscheinheiten
  zusätzlich im Vorrat, fünf→zwei Karten. Keine eigene Abgabe für den Nutzer
  ausgeführt. Selektor nicht mehr vorhanden, alte Fehlermeldung verschwunden.
- Getrennte sichtbare Dreierprüfung auf 8775: Alaska 3→5, Alberta 2→4,
  Weststaaten 3→5, regulärer Vorrat 5→9. Ohne Zusatzentscheidung getauscht.
  Neue Prüfvorschau 15036 und Prüftab danach beendet. Bilder/Ergebnisse unter
  runtime/conquest-bonus-20261026/. Nutzerpartie und Simulator bleiben aktiv;
  beide lokalen Health-Endpunkte liefern HTTP 200. Keine neuen Sicherungen,
  kein externer Upload. git diff --check erfolgreich.


## 2026-10-26 – Einzelschritt: Karten nach Tausch einklappen, weitere Arbeit geplant

- Nutzer verlangt ausdrücklich schrittweise Arbeit. Nur den ersten kleinen
  Ablauf umgesetzt: Nach bestätigtem Kartentausch eigene Hand einklappen und
  Tastaturfokus zur Kartenplakette am Avatar zurückgeben. Während des Speicherns
  oder bei Fehler bleibt die Hand mit ihrer Auswahl geöffnet. Keine Änderung
  an den Auszahlungsmengen oder der Tauschpflicht.
- 78 JavaScriptprüfungen erfolgreich; neue Prüfung für laufende, erfolgreiche
  und fehlgeschlagene Abgabe einschließlich erhaltenem Satz und Wiederholung.
  Sichtbar in getrennter vorhandener Prüfrunde auf 8775: drei Karten abgegeben,
  zwei übrig, Hand automatisch geschlossen, keine ausgewählten Karten mehr,
  Fokus am eigenen Avatar, Tauschaktion verborgen. Bild/Ergebnis unter
  runtime/conquest-autocollapse-20261026/. Zusätzlicher Prüftab geschlossen.
- Nutzer hat die Folgepartie selbst gestartet (Tisch 6, Start 00:48:00.956196).
  Vorheriger Simulator hatte nach dem letzten Sieg regulär gestoppt; dieselben
  drei autorisierten Testspieler mit 17140 wieder aufgenommen. Keine Runde
  neu erzeugt oder zurückgesetzt. Bestehende Nutzeransicht aktualisiert und
  ihren Überblick bei 82 Grad wiederhergestellt; keine Starteinheit gesetzt.
- Weitere Reihenfolge in docs/GESTALTUNGSPLAN.md festgehalten: zuerst oberen
  Streifen entfernen und Kamerabedienung unten rechts; dann neue Karte mittig
  für zwei Sekunden und zum Avatar, „Dein Zug“ zwei Sekunden; danach echter
  Nahblick, gemeinsame Karten-/Angriffsklänge auch in der Button-Werkstatt,
  später weitere Elementarten im Editor. Diese Punkte noch nicht umgesetzt.
- Nutzer hat für den späteren Nahblick ausdrücklich erlaubt, dass Kartenränder
  und äußere Länder aus dem Bild geraten. Das ersetzt dort die bisherige
  vollständige Einpassung. Aktuelle Kameraursache geprüft: Entfernung wird bei
  jedem Winkel neu an die vollständige Karte angepasst, daher kein stetiges
  Näherkommen. Kein Kameraverhalten im aktuellen ersten Schritt geändert.
- Nutzer hat zusätzlich den oberen Streifen als unnötig bezeichnet; Name steht
  auf dem Brett, Position/Bedienung soll nach unten. Dies als direkt nächsten
  Schritt priorisiert. Vorhandene Werkstatt und Sammlung bleiben erhalten;
  keine neuen Geräusche oder weiteren Elementtypen als fertig ausgegeben.
  git diff --check erfolgreich, keine neuen Spielstandssicherungen/Uploads.


## 2026-10-26 – Oberen Streifen entfernt, kleine Kamera unten rechts (lokal)

- Auf ausdrücklichen Auftrag den gesamten oberen Namens-/Werkzeugstreifen
  entfernt. Kein zweiter Spielname mehr neben dem Namen auf dem Brett.
  Ein gemeinsamer kompakter Kamerabaustein unten rechts: Sitz, Winkelregler,
  Überblick und Gradzahl; Sitzposition weiter als vollständiger zugänglicher
  Name. Rückweg zur bestehenden Lobby als kleiner Link unten links erhalten.
  Normale Spielansicht zeigt auch keinen zusätzlichen Namenshinweis im Fuß.
- Zuständige CSS-Regeln konsolidiert, alte toolbar-/brand-/controls-Regeln
  einschließlich ihrer mobilen Abwandlungen entfernt. Kamera ca. 214 × 40 px
  mit zwölf Pixeln Abstand zu rechtem/unterem Rand. Auf schmalen Fenstern
  Spielaktionen darüber, statt Überlappung mit Kamerabedienung. Gleiche
  Bedienkomposition in allen Größen; Spieleranzeige nach oben nachgerückt.
- Bretteinpassung reserviert keinen früheren Headerplatz mehr. Obere Grenze
  vier Pixel; auf schmalen Fenstern unter der tatsächlichen Spieleranzeige.
  Unten zählen Zugleiste und Kamerabedienung. Resize- und Scrollbehandlung
  angepasst, ohne Winkelbereich, Linse oder den bisherigen Bewegungsverlauf
  zu ändern. Ein späterer echter Nahblick bleibt eigener geplanter Schritt.
- 79 JavaScriptprüfungen erfolgreich, einschließlich aller Zwischenwinkel
  auf sechs Verhältnissen und neuer Grenzen bei tiefer Zugleiste/unteren
  Kamerasteuerungen. Syntaxprüfung und git diff --check erfolgreich.
- Sichtbar in getrennter bestehender Prüfrunde: beide Kameraposen und Regler
  per Tastatur, keine Grafikfehlermeldung, 42 Länder. 390 × 660 px: Rückweg,
  Spielaktion und Kamera erreichbar, untere Gruppen getrennt. Desktopkamera
  ca. 214 × 40 px. Zusatz-Prüftab anschließend geschlossen.
- Nutzerpartie aktualisiert, vorherige 82-Grad-Ansicht wiederhergestellt.
  Tatsächlicher Tisch 6 sichtbar ohne oberen Streifen, 42 Marken und kleine
  Kamera unten rechts. Gleiche Startzeit und alle vier Mitgliedschaften;
  kein eigener Spielzug, kein Backend-/Simulatorneustart oder Zurücksetzen.
  Metadaten/Bilder unter runtime/conquest-controls-20261026/. Keine neuen
  Spielstandssicherungen und keine externe Übertragung.

## 2026-10-26 – Kartenempfang mittig und Hinweiszeiten (nur lokal)

- Neue Länderkarte nach bestätigtem Zugende zwei Sekunden in der Mitte,
  danach 480 ms schrumpfender Flug zum tatsächlichen Avatar des Empfängers.
  Ziel erst beim Abflug gemessen; der inzwischen nächste Spieler ist nicht
  das Flugziel. Danach verschwindet die Anzeige. Gemeinsame vollständige
  Länderkarte für Hand und Empfang erhalten, kein neuer Kartenbestand.
- Wiederholte Zustandsaktualisierungen starten weder Anzeige noch Timer neu.
  Bereits gespeicherte alte Empfangsergebnisse werden beim Laden übersprungen;
  spätere neue Ergebnisse werden einmal angezeigt. Öffnen der Hand, Schließen,
  Auswahl, Zurücksetzen und Seitenwechsel räumen den Empfangstimer auf.
  Bei reduzierter Bewegung bleibt die zweisekündige Anzeige ohne Flug.
- „Dein Zug!“ auf zwei Sekunden verlängert; Pflichttauschhinweis mit Karten-
  button bleibt wie bisher bestehen. Keine Regel-, Vergabe- oder Serveränderung.
  Vorhandene automatische Einklappfunktion nach Kartentausch erhalten.
- 81 JavaScriptprüfungen erfolgreich, darunter Zwei-Sekunden-Dauer ohne
  Neustart bei Aktualisierung, Flug zum früheren Akteur statt Folgeakteur,
  Aufräumen, kein Wiederholen alter Ergebnisse und reduzierte Bewegung.
  JavaScript-Syntax und git diff --check erfolgreich.
- Sichtbar in unabhängiger eigener Prüfdatenbank: echte Kartenvergabe nach
  regelkonformer Eroberung und einem Abschlussklick, mittige Karte, Flugstart
  mit Ziel am eigenen Avatar, anschließendes Verschwinden und Erhalt in der
  Hand. Neuladen wiederholt den Empfang nicht. Auch 390 × 660 px mittig
  geprüft; „Dein Zug!“ sichtbar und danach verschwunden. Keine Browserfehler.
- Nutzerpartie Tisch 6 aktualisiert; 59,1 Grad und Auswahl Argentinien in
  Festigen wiederhergestellt. Gleiche Startzeit, alle vier Mitgliedschaften,
  Revision 723 und vollständiger Spielzustand vor/nach Aktualisierung gleich.
  Kein eigener Spielzug, kein Neustart des Spielservers oder Gegnersimulators.
  Prüfmetadaten und Bilder: runtime/conquest-card-flight-20261026/. Temporäre
  separate Prüfvorschau anschließend beendet. Keine neue Spielstandssicherung
  und nichts auf einen externen Server übertragen.

## 2026-10-26 – Vorhandener Desktop-Starter öffnet die aktuelle lokale Vorschau

- Auf Nutzerauftrag denselben Starter auf das aktuelle lokale Arbeitsziel
  umgestellt. Desktop-Verknüpfung ausgelesen: Ziel unverändert
  D:\Guesstimate\Guesstimate-starten.cmd, ohne weitere Argumente.
  deploy/local-preview.json legt derzeit Conquest fest. Der Starter verwendet
  die aktuellen Dateien dieses Projektordners, keine separat gebaute Exe.
- Dauerhafter Fortsetzen-Einstieg deploy/run_current_conquest.py auf 8767
  verwendet ausschließlich die vorhandene walkthrough.sqlite3 und gespeicherte
  Spielerzuordnung. Bei fehlenden Dateien Abbruch statt neuer Beispielpartie.
  /local/current öffnet als bisheriger lokaler Testspieler die neueste aktive
  eigene Lobby bzw. laufende/beendete Partie. Kein Zurückspringen zum alten
  Tisch 3; aktuell Tisch 6. Bestehende getrennte Sitzung und Mitspieler-
  Einstieg erhalten. Der Starter löst keine Spielzüge oder Botstarts aus.
- Normales Hauptspiel auf 8765 weiterhin über --main-game erreichbar;
  Werkstattstarter unverändert. Vorhandene Dienste werden wiederverwendet,
  fremde Portbelegung weiterhin nicht übernommen oder beendet.
- 15 gezielte Pythonprüfungen erfolgreich: gespeichertes Ziel, fehlende Daten,
  unbekanntes Profil, Hauptspielaufruf, kein Doppelstart, Prozessbereinigung,
  frischer Browserzugang, neueste eigene Lobby und ignorierte fremde/ausgetretene
  Mitgliedschaften. git diff --check erfolgreich.
- Tatsächlichen bisherigen lokalen Vorschauprozess eindeutig identifiziert
  und einmal durch Start über Guesstimate-starten.cmd --no-browser ersetzt.
  Ohne laufenden Vorschauprozess vorhandene Partie erfolgreich geladen.
  Zweiter Starteraufruf erkennt denselben Prozess 1796, kein Doppelstart.
  Hauptspiel und Gegnersimulation nicht neu gestartet. /local/current im
  Browser sichtbar bei Tisch 6, Festigen, Stormseed und allen vier Spielern.
- Spielzustand, Revision 723 und Mitgliedschaften vor/nach Neustart gleich.
  Desktop-Verknüpfung nicht ersetzt; keine Spielstandssicherung oder externe
  Übertragung. Nachweise: runtime/conquest-launcher-20261026/.


## 2026-10-26 – Zielbild der persönlichen Spielewerkstatt bestätigt

- Nutzer bestätigt eine unter seinem Zugang in Guesstimate integrierte
  Spielewerkstatt mit durchsuchbaren Bibliotheken, passenden Editoren und
  dauerhaft gespeicherten Projektmappen. Ablauf: zu einer Spielidee stöbern,
  einzelne Elemente im Projekt sammeln, bei Bedarf bearbeiten und anschließend
  das Projekt mit weiteren Angaben an Codex zum Bauen des Spiels übergeben.
- Projektmappen sollen ausgewählte Elemente in ihren konkreten gespeicherten
  Varianten, deren vorgesehene Rollen, eigene Anmerkungen und offene Wünsche
  zusammenhalten. Ergänzende Regeln und Spielabläufe können bei der Übergabe
  im Gespräch präzisiert werden; ein vollständiger Bauplan ist keine
  Voraussetzung für das Sammeln oder Übergeben.
- Bibliotheksbereiche: Titelbilder, Schriften, Icons und Flyer; Hintergründe,
  Räume, Lobbys und Kameraeinstellungen; Avatare und Spieleranzeigen; Buttons
  und weitere Anzeigeelemente; Bretter, Figuren, Karten und Würfel; Klänge und
  Musik sowie Regeltexte und wiederverwendbare systemische Regelbausteine.
  Neue Arbeiten sollen nach und nach als wiederverwendbare Bausteine verfügbar
  werden, mit erkennbaren Entwurfs- und Freigabeständen.
- Geplante Bearbeitung: Elemente aus der Bibliothek bzw. einer vorhandenen
  Spieloberfläche im passenden Editor öffnen und als eigene Variante speichern.
  Vor Anwendung muss der Geltungsbereich erkennbar sein: aktuelle Verwendung
  oder mehrere Verwendungen eines gemeinsamen Bausteins. Die verbindlichen
  gemeinsamen Grundkomponenten bleiben maßgeblich; keine unabhängigen
  Seitenkopien ihrer Innenkomposition.
- Erster vorgesehener Ausbau: gemeinsame Bibliotheksoberfläche, Projektmappen
  und nachvollziehbare Übergabe; vorhandene lokale Button-Werkstatt als erstes
  Werkzeug anschließen. Weitere Elementeditoren nach tatsächlichem Bedarf.
  Bisherige Formen, Entwürfe, Materialien und Sammlung bleiben erhalten.
- Nutzer stellt klar: Es gibt keinen integrierten Live-Editor, der externe
  Server bleibt ausgefallen. Das aktuelle Zielbild betrifft eine künftige
  Erweiterung auf Grundlage des lokalen Bestands. In diesem Schritt nur diese
  Entscheidung dokumentiert; keine neue Editorfunktion, Serververbindung,
  Aktivierung, Änderung von Konten oder Spielständen.


## 2026-10-26 – Button-Werkstatt verständlicher gegliedert (nur lokal)

- Nutzer beanstandet zu viele gleichzeitig sichtbare Knöpfe und Fenster,
  schwer auffindbare Vorlagen/Entwürfe und unverständliche Zusatzanzeigen.
  Vorhandene Eigenschaftenwahl und freie Formbearbeitung bleiben erhalten.
- Zwei dauerhaft erkennbare Zugänge: „button bearbeiten“ und „vorlagen &
  entwürfe“. Bearbeitung mit Eigenschaften links, einzelnem Testbutton rechts,
  vollständigem Speichern direkt darunter und anschließendem Formeditor.
  Werkstattaktionen sind von den gestalteten Buttonmustern unterscheidbar.
- Eigene Bibliotheksansicht mit gespeicherten vollständigen Entwürfen,
  gespeicherten Formen und Startvorlagen; Suche nach Namen über alle Bereiche.
  Pro Karte eine ausdrücklich beschriftete Öffnen-/Verwenden-Aktion. Nach
  Speicherung direkter Link zur Entwurfsbibliothek. Formübernahme erhält
  Material, Schrift und Klang und führt zur Bearbeitung zurück.
- Bewertungen/Notizen, weitere Buttonzustände, Vorher-/Nachher-Vergleich,
  Beispieltafel und Klanggalerie gezielt aufklappbar und erklärt. Separates
  Form-Speichern unter „Nur die Form als Vorlage speichern“. Export/Einlesen
  in der Bibliothek; Einlesen führt zur Bearbeitung. Das Umschalten der
  Hauptbereiche ersetzt den aktuellen Entwurf nicht.
- Zuständige Werkstattvorlage, Steuerung und ihre beiden Oberflächenstyles
  konsolidiert; keine neuen CSS-Gegenblöcke für die alte dritte Spalte.
  Gemeinsamer Button-/Materialrenderer, Geometrie, Klangdateien, Katalog,
  Speicherformat und Spielkomponenten unverändert. README aktualisiert.
- Alle zehn vorhandenen Speicher-/Validierungs-/HTTP-Prüfungen erfolgreich,
  ebenso JavaScript-Syntaxprüfung. Der erste lokale HTTP-Prüfversuch war durch
  Socket-Zugriffsrechte blockiert; mit freigegebener lokaler Testverbindung
  bestanden alle Prüfungen. Keine doppelte HTML-ID in der neuen Vorlage.
- Browserabläufe ausschließlich mit getrennten Kopien der vier Entwürfe auf
  127.0.0.1:8772 geprüft: Suche nach conquest, gespeicherte Acht-Punkte-Form
  übernehmen bei unverändertem Steinmaterial, neuen vollständigen Entwurf
  speichern, per Link wiederfinden, nach Neuladen erneut öffnen mit acht
  Punkten und gespeichertem Stand. Zusätzliche Tests standardmäßig geschlossen.
- Bearbeitung und Bibliothek bei tatsächlich gemessener CSS-Breite 433 ohne
  horizontalen Überlauf sichtbar geprüft. Angeforderte Breite 390 wurde vom
  Browser abweichend dargestellt; kein exakter 390-Pixel-Nachweis behauptet.
  Temporäre Größenvorgabe zurückgesetzt. Keine Browserwarnungen/-fehler beim
  Abschluss. Datei-Export und Dateiauswahl im Browser nicht erneut nachgewiesen;
  ein anfänglicher Exportaufruf hing ohne Ergebnis. Weitere Browseraufrufe
  wurden zeitlich begrenzt ausgeführt.
- Vorherige Werkstattquellen unter runtime/button-workshop-clarity-20261026/
  gesichert. 360 geschützte vorhandene Dateien einschließlich der vier
  persönlichen Entwurfs-/Formdateien abschließend SHA-256-identisch. Keine
  Testeinträge in die persönliche Sammlung geschrieben, keine Spieldatenbank
  bedient und kein externer Serverkontakt. Prüfmetadaten in verification.json.
- Persönlicher Werkstattdienst war beim erneuten Öffnen nicht erreichbar.
  Nur diesen lokalen Dienst auf 127.0.0.1:8771 mit dem unveränderten bisherigen
  Entwurfsordner gestartet. Beide neuen Ansichten tatsächlich mit der normalen
  Sammlung gesehen: zwei vollständige Entwürfe und zwei Formen. Bibliothek im
  Browser geöffnet gelassen; Bilder bearbeiten.png und bibliothek.png im
  genannten Prüfverzeichnis. Kein Neustart eines Spielprozesses und keine
  öffentliche Aktivierung. Gestalterische Bewertung bleibt beim Nutzer.


## 2026-10-26 – Buttonkontur proportional und drei unterscheidbare Stile (lokal)

- Nutzer meldet, dass die bearbeitete Form unten rund wirkt, der Entwurfsbutton
  oben aber spitz. Am gespeicherten Werkstatt-Holz tatsächlich gemessen:
  Buttonfläche 504,671875 × 66,6875, Verhältnis 7,5677; die bearbeitete Ebene
  verwendet 560:180, Verhältnis 3,1111. Gleiche Prozentpunkte wurden damit
  unabhängig in Breite und Höhe verzerrt. Keine andere gespeicherte Form als
  vermeintlichen Ersatz verwendet.
- Gemeinsame Zeichenebene und Buttonmaße in geometry.js festgelegt.
  Materialrenderer hält die Buttonfläche in denselben Proportionen;
  Schrift, Konturrand und Druckweg folgen der tatsächlich verfügbaren Breite.
  Erzwungene breite Vorschau-Mindestbreiten entfernt und die Vorschaufläche
  für echtes gemeinsames Verkleinern konsolidiert. Lange Beschriftungen
  passen sich innerhalb der unveränderten Form an. Bewegungsfunktion erhalten.
- Ein Materialrenderer für Werkstatt, Bibliotheksmuster, Vergleiche und die
  bereits angeschlossenen lokalen Spielbuttons. Keine zweite Konturkopie und
  keine Stilveränderung der gespeicherten Eckpunkte. Unbenutzte Größenbeobachter
  werden beim Ersetzen der Vorschauen freigegeben.
- Auf Nutzerpräzisierung Stile deutlicher getrennt: Comic mit gemalten Flächen,
  vereinfachten Materialspuren und kräftiger Kontur; Natürlich mit echter
  vorhandener Materialtextur und weicheren Lichtkanten; Grafisch mit flächigen
  Farben und einfachen Holzlinien, Steinflächen oder Metallstreifen ohne
  fotografische Textur. Alle drei mit allen drei Materialien kombinierbar.
  Interne Stilkennung minimal bleibt für Grafisch erhalten; renderer_version
  auf button-workshop-v4. Auswahl beschreibt jeweils die gewählte Richtung.
- Vorhandene Materialbilder, Schriftwahl, Klangdateien und gespeicherte
  Rezeptdateien erhalten. Neue CSS-Wirkungen an den zuständigen Stil- und
  Materialregeln konsolidiert. README und Gestaltungsplan aktualisiert.
- Zehn vorhandene Speicher-/Validierungs-/HTTP-Prüfungen bestanden. Bestehende
  Geometrie-, Schriftzuordnungs- und Klangprüfungen erfolgreich; zusätzliche
  Regression prüft gemeinsame Zeichenebene, Rundungskoordinaten und proportionale
  Höhe, Schrift, Rand und Druckweg über Größen und alle Stile. Syntax erfolgreich.
- Getrennte Browserprüfung auf 8772 mit Kopien der vier gespeicherten Einträge:
  Holzform oben/unten verglichen, Punkt verändert, Tastaturschritt rückgängig,
  Kontur über alle Stile unverändert, geänderte grafische Form als eigenen
  Prüfentwurf gespeichert und nach Neuladen mit Stil minimal und Punkt X=12
  wieder geöffnet. Alle neun Stil-/Materialkombinationen tatsächlich angesehen.
- Echte 320-/390-/800-Pixel-Einbettungen gemessen, ohne horizontalen Überlauf.
  Button bei 320 px auf 227 × 72,953125 verkleinert; Schrift und Druckweg relativ
  zur Breite unverändert. Lange Beschriftung bei 320 px passt in dieselbe Form.
  Ein Fehler im Frame-Prüfkontext ist in verification.json ausdrücklich
  protokolliert; persönliche Abschlussansicht ohne Browserwarnungen/-fehler.
- Nur persönlichen Werkstattdienst auf 8771 für den neuen Katalog neu geladen,
  mit unverändertem Entwurfsordner. Gespeichertes Werkstatt-Holz in neuer
  persönlicher Browseransicht geöffnet: 276 × 88,703125, Verhältnis 3,1115
  einschließlich Browser-Pixelrundung. Gerenderte CSS-Kontur und Editorpfad
  besitzen dieselbe Punktzahl; maximale normierte Abweichung unter 0,000005.
  Die ursprüngliche Nutzeransicht nicht neu geladen oder überschrieben.
- Alle vier persönlichen Dateien abschließend SHA-256-identisch, keine neuen
  Einträge in der persönlichen Sammlung. Keine Spieldatenbank bedient, keine
  Spielregel geändert, kein Spielprozess neu gestartet und kein Serverkontakt.
  Vollständige Spielansicht nicht neu abgenommen; gemeinsamer Materialrenderer
  wirkt auch in dessen vorhandenen Verwendungen. Visuelle Stilbewertung bleibt
  beim Nutzer. Eigene Prüftabs und Prüfdienst beendet; persönliche Werkstatt offen.
- Nachweise und Ausgangsquellen: runtime/button-shape-style-20261026/,
  insbesondere verification.json, form-pruefung.json, responsive-pruefung.json,
  stilwechsel-pruefung.json, holz-entwurf.png und stile-materialien.png.

## 2026-10-26 – Persönliche Spielewerkstatt: Bibliothek, Projektmappe und Übergabe (lokal)

- Nutzerziel präzisiert: Schach ist das erste Beispiel für wiederverwendbare
  Figuren, Brett, Hintergrund, Darstellung/Kamera, Licht/Objektverhalten, Lobby,
  Würfel und Karten. Raum bedeutet bedarfsabhängig 2D/2,5D/3D, Licht/Schatten,
  Kamera oder flache Oberfläche sowie gezielt benötigte Objektbewegungen.
  Reihenfolge liegt beim Umsetzer; entscheidend ist der durchgehende Ablauf
  statt einzelner unverbundener Zwischenstände.
- Neue lokale Werkstatt unter offline-preview/game-workshop-v1/ auf 8776:
  Gestalten, Bibliothek und Projektmappe. Alle acht Arten besitzen einen
  grundlegenden parametrischen Editor. Gemeinsame räumliche Vorschau und
  Großansicht verwenden dieselben Modellfabriken in models.js. Neue eigene
  Schachfiguren mit sechs Rollen, Dame-Steine, Brett, D6 und Musterkarte entstehen
  aus Projektcode. Lokale vorhandene Three.js-Dateien samt MIT-Lizenz und
  bestehende Material-/Raumbilder werden referenziert, nicht ersetzt.
- Zentrale schema.json für sichtbare Eigenschaften und serverseitige Prüfung.
  2D nutzt stabile Draufsicht und flache Figurensymbole, 2,5D eine parallele
  Kamera, 3D Perspektive. Grundlicht, gerichtetes Licht, Schatten sowie
  Sofort-/Gleitbewegung für Figuren, Kartenwenden und Würfelfall einstellbar.
  Fallprobe besitzt Schwerkraft, Tischkontakt, Rückprall und begrenzte Laufzeit;
  anschließend Ausrichtung auf das angezeigte Würfelergebnis. Keine vollständige
  Starrkörperphysik oder Kollision aller Objekte. Bildkulissen bleiben flach.
- Lobbyvorschau rendert direkt die vorhandenen Makros _lobby_room.html und
  _profile_window.html einschließlich der gemeinsamen Schriftanpassung aus
  profile-stage-v1.js. Nur Musterspieler; keine Konten oder Spielstände gelesen
  oder verändert. Lobbytitel, Plätze, Raum, Akzent und Beispielausstattung sind
  gestaltbar; keine zweite unabhängige Lobby-Innenkomposition angelegt.
- Varianten werden append-only in design-library/elements/ gespeichert,
  Projektmappen in projects/. Jede Mappe hält vollständige Werte und genaue
  Bibliotheksreferenzen fest. Nach Änderungen wird eine Referenz gelöst;
  widersprüchliche Referenz-/Wertepaare werden abgewiesen. Vor dem Öffnen eines
  alten Standes oder Anlegen einer neuen Mappe werden aktuelle Änderungen als
  eigener Stand erhalten. Browser-Zwischenablage zusätzlich, kein Ersatz für
  das ausdrückliche dauerhafte Speichern.
- Vorhandene vollständige Buttonentwürfe werden nur gelesen und wahlweise als
  unveränderte Momentaufnahme in die Mappe aufgenommen. Gleichnamige Buttons
  werden mit Speicherzeit unterschieden. Übergabe erzeugt lokale vollständige
  JSON-Datei und lesbaren MD-Begleittext unter handoffs/ samt kopierbarem Pfad;
  keine Nachricht oder Datei extern versendet. Persönliche neue Ablageordner
  vor dem Schreiben von Git ausgeschlossen und als Benutzerdaten dokumentiert.
- Durchgehender Browserablauf auf 8777 mit getrennter Prüfbibliothek: Brett mit
  zehn Spalten gestalten, speichern, suchen und übernehmen; Figuren ändern;
  alle Darstellungsarten ansehen; Lobby mit drei Plätzen; Würfel und Karte
  aufnehmen; einen bisherigen Button und Wünsche ergänzen; Mappe/Übergabe
  speichern. Übergabedatei unabhängig gelesen und Werte einschließlich
  vollständiger ursprünglicher Buttondatei verglichen. Nach Neuladen echten
  gespeicherten Stand geöffnet und neueren Textentwurf als eigenen Stand
  erhalten. Dasselbe Brett in neuer Dame-Mappe wiederverwendet.
- Figuren tatsächlich angeklickt und auf freies Feld bewegt; Würfelprobe 5/6
  stimmte mit den sichtbaren oberen Augen überein. Kartenwenden und Großansicht
  geprüft. Kartentext passt seine Schrift an längeren Inhalt an. Anfangs noch
  schwarze, erst verspätet geladene Tischtextur durch Zeichnen beim Laden
  behoben. 390-Pixel-Einbettung zeigte zunächst zu breite Mindestmaße; zuständige
  Grid-Kinder konsolidiert und anschließend vollständig schmal sichtbar. Bei
  abschließender 2D-Kartenprüfung umgekehrte Kamerarichtung erkannt, feste
  Hochrichtung gesetzt und aufrechte Vorder-/Rückansicht erneut angesehen.
- 21 Speicher-/Referenz-/HTTP-/Starterprüfungen bestanden, außerdem JS-Syntax
  und Fallprobe mit Grenzwerten. Erster unprivilegierter Prüflauf war durch
  lokale Socket-/Tempordnerrechte blockiert; getrennte Prüfordner im Projekt
  und freigegebene lokale Testverbindung verwendet. Keine externen Quellen oder
  Server kontaktiert. Abschlussbrowser ohne Warnungen/Fehler.
- Werkstattübersicht und bestehender Starter um 8776 ergänzt. Persönlichen
  Dienst mit absolutem Skriptpfad gestartet; echte Besitz-/Antwortprüfung des
  Starters bestätigt Wiederverwendung dieses Dienstes. Eine persönliche Mappe
  Schach mit vorläufiger Ausstattung und der beschriebenen Arbeitsweise
  angelegt, gespeichert und im Browser nach Neuladen bestätigt. Würfel/Karten
  sind dort verfügbar, zunächst optional. Prüftabs und eigener Prüfdienst
  geschlossen; persönliche Werkstatt offen. Bestehende Spiel-/Buttonprozesse
  nicht neu gestartet. Alle 95 vorab erfassten geschützten Quelldateien und
  bisherigen persönlichen Entwürfe SHA-256-identisch.
- Noch offen: freies Modellieren/Zeichnen jenseits der angebotenen Parameter,
  vollständige Physik, weitere Assetarten und Editorfunktionen, konkrete
  Spielregeln sowie Integration in den persönlichen Online-Zugang. Keine
  spielbare Schachpartie oder öffentliche Aktivierung behauptet.
- Nachweise: runtime/game-workshop-20261026/verification.json,
  spielewerkstatt.png, uebergabe-pruefung.png, dame-wiederverwendung.png,
  bewegungsprobe.png, karte-gross.png und 390px.png. Ausgangsdateien der
  Anschlussstellen unter source-before/ erhalten.

## 2026-10-26 – Werkstatt von Spielen entkoppelt; Projektmappen als freie Sammlungen (lokal)

- Nutzer korrigiert den bisherigen spielbezogenen Aufbau ausdrücklich:
  Werkstatt ist die allgemeine Startseite mit Gestalten, Bibliothek und
  Projektmappe. Schach ist ausschließlich ein Projekt. Gestalten und Bibliothek
  besitzen dieselbe wachsende Elementliste. Links bleibt die Auswahl erhalten,
  daneben wird jeweils der vorhandene Generator bzw. der Bibliotheksbestand
  geladen. Neues Projekt beginnt leer mit eigenem Namen; eine Mappe sammelt
  beliebige und auch mehrere Elemente derselben Art. Nach der Übergabe soll
  das Spiel im Interview entstehen. Diese Präzisierung ersetzt die vorherige
  automatische Schachausstattung als Ziel der Werkstattoberfläche.
- index.html, workshop.js und workshop.css der lokalen Werkstatt entsprechend
  umgebaut. Hauptüberschrift immer Werkstatt; Einstieg Buttons ohne aktive
  Projektmappe oder Brettszene. Gestalten und Bibliothek teilen dieselbe
  Navigation; gewählte Elementart bleibt beim Bereichswechsel erhalten.
  Such-/Sammlungsfilter werden bei Wechsel der Elementart zurückgesetzt.
- Vorhandene Button-Werkstatt unter /button-editor/ unmittelbar aus denselben
  Quelldateien eingebunden. Ursprünglichen Validator, Dateispeicher, Renderer,
  Geometrie, Schriften, Material- und Klanglogik wiederverwendet. Kleine bedingte
  Einbettungsbrücke meldet gespeicherte Kennung und benötigte Höhe und führt
  Bibliothekslinks in die gemeinsame Ansicht. Eigene embedded.css ändert nur
  die umgebende Werkstattnavigation, nicht die Buttonkomposition. Bisheriger
  eigenständiger Einstieg und Speicher bleiben bestehen.
- Neue erweiterbare Elementregistrierung workshop_catalog.py: Buttons zuerst,
  danach Bretter, Figuren, Hintergründe, Lobbys, Würfel, Karten und Avatare.
  Generische Generatoren zeigen ausschließlich den gewählten einzelnen
  Baustein mit neutraler Vorschau; Three.js wird erst dafür geladen. Bestehende
  Bilder sind sichtbar wählbar: 15 Hintergründe und 19 registrierte Avatare.
  Für diese Bildbestände ist ausdrücklich kein freier Editor eingerichtet.
- In der Bibliothek Buttons mit dem ursprünglichen Renderer und Formen mit
  dessen Konturpfad dargestellt. Alle übrigen Elemente einzeln ansehbar und
  einer frei gewählten Mappe zuordenbar. Eigene Entwürfe lassen sich auch direkt
  nach dem Speichern in der Werkstatt zuordnen. Keine globale aktive Mappe
  erzwingt beim Gestalten eine Spielausstattung. Oberflächenregeln für normale
  Werkstattknöpfe schließen die gemeinsame .comic-button-Komponente aus.
- workspace_store.py ergänzt Projektformat 2: frei kombinierbare Elementliste
  mit vollständigen gespeicherten Momentaufnahmen und stabiler Projektkennung.
  Jeder Schreibvorgang erzeugt einen neuen Stand unter derselben Mappe. Mehrere
  Buttons und Wiederverwendung in mehreren Mappen nachgewiesen. Entfernen aus
  einer Mappe löscht weder Bibliothek noch frühere Projektstände. Übernahme aus
  früheren Ständen unterstützt auch bisherige, nicht separat gespeicherte
  Legacy-Elemente. Auswahl und Kennungen werden serverseitig geprüft.
- Bisherige Format-1-Mappen bleiben unverändert. Beim Lesen werden sie nur für
  die Anzeige angepasst; Kamera und Raumverhalten werden Projektentscheidungen.
  Erst ausdrücklich ausgelöstes Speichern erzeugt einen neuen Format-2-Stand,
  der den vollständigen Ursprungsdatensatz zusätzlich bewahrt. Öffnen der
  Werkstatt migriert keine Dateien und erzeugt keine neue persönliche Mappe.
- Darstellung/Kamera, Licht/Schatten und Bewegungsbedarf stehen als offene
  Entscheidungen in der jeweiligen Mappe, erläutert mit drei Beispielen.
  Hinweise berücksichtigen die tatsächlich gesammelten 2D-/3D-Ausführungen;
  die Darstellung wird dadurch nicht automatisch vorgegeben. Die Übergabe
  bündelt Auswahl und Wünsche mit einer generischen Interview-Checkliste.
  Keine Spielregeln oder Spiellogik aus dem Projektnamen abgeleitet.
- Browserprüfung ausschließlich mit kopierter Bibliothek auf 8777: frei
  benannte leere Mappe angelegt, neuen Button in eingebundener ursprünglicher
  Werkstatt gespeichert und direkt zugeordnet, unter Buttons wiedergefunden,
  denselben Button aus der Bibliothek einer zweiten neu benannten Mappe
  zugeordnet. Zweiten bisherigen Button und vorhandenes Clubzimmer ergänzt.
  Eigenständigen Brettgenerator geöffnet, 6×6-Raster gestaltet, gespeichert und
  ergänzt. Projektübersicht zeigte drei Mappen statt Einzelkarten für jeden
  Speicherstand; ursprüngliches Schach blieb eine eigene Mappe.
- Erneut geladene Prüfmappe hielt zwei Buttons, Hintergrund und eigenes Raster.
  Offene Kamerawahl und Hinweis auf das räumliche Brett tatsächlich gesehen.
  Wünsche ergänzt, Interview-Übergabe geschrieben und deren JSON unabhängig
  auf vollständige Auswahl, zwei Buttons, 6×6-Raster und offene Darstellung
  geprüft. Die ursprünglichen Buttondateien liegen als exakte Momentaufnahme
  in der Mappe. Keine Prüfeinträge in die persönliche Sammlung geschrieben.
- 29 Sammlungs-/Speicher-/Referenz-/HTTP-/Starterprüfungen bestanden, dazu alle
  zehn ursprünglichen Button-Werkstattprüfungen und JavaScript-Syntax.
  Browseransicht bei tatsächlich 390 px Rahmenbreite sichtbar kontrolliert;
  Kategorien dort horizontal erreichbar, Inhalt in der Breite passend.
  Bibliotheks-Buttonflächen gemessen: 204 × 65,5625, Verhältnis 3,11153 mit
  Pixelrundung. Gemeinsame Renderer, Geometrie, models.js und scene.js gegenüber
  dem Ausgangsstand SHA-256-identisch.
- Nur persönlichen Werkstattdienst auf 8776 mit unveränderter Datenablage neu
  gestartet; vorhandener Starter bestätigt Besitz und aktuelle Antwort.
  Persönliche Ansicht zeigt Werkstatt, Buttons und null räumliche Szenencanvases.
  Projektübersicht zeigt ausschließlich die vorhandene Schach-Mappe. Normale
  Startansicht geöffnet gelassen; Abschluss ohne Browserwarnungen/-fehler.
  Prüftabs und eigener Prüfdienst geschlossen. Kein Kontakt zum externen
  Server, keine öffentliche Aktivierung und keine Spiel-/Kontenänderung.
- Alle fünf bisherigen persönlichen JSON-Dateien einschließlich vier Button-/
  Formdateien und der Schach-Mappe abschließend SHA-256-identisch. Dokumentation,
  Werkstattübersicht und Sammlungseintrag an die korrigierte Struktur angepasst.
  Nachweise und Ausgangsquellen unter runtime/workshop-generic-20261026/:
  verification.json, werkstatt.png, bibliothek.png, projekt-uebergabe.png,
  390px.png und source-before/.

## 2026-10-26 – Gemeinsame Bildwerkstatt mit Import, Ausschnitt und Varianten (lokal)

- Nach Zustimmung zum nächsten Schritt einen gemeinsamen Bildeditor für
  Hintergründe, Titelbilder, Icons, Flyer und Avatare eingerichtet. Keine
  spielbezogene Vorauswahl. Gestalten und Bibliothek verwenden weiterhin
  dieselbe Elementregistrierung und Projektzuordnung.
- PNG, JPEG und WebP lassen sich vom PC importieren. Die Originaldatei bleibt
  bytegenau erhalten. Ausschnitte mit Maus, Tastatur und Pixelwerten bearbeitbar;
  feste Seitenverhältnisse und proportionale Ausgabegröße verfügbar. Gespeicherte
  Varianten sind eigenständige PNG-Dateien mit Quellbezug und erneut ladbarem
  Bearbeitungsstand. Transparenz und EXIF-Ausrichtung berücksichtigt.
- Vorschau und gespeicherte Variante verwenden dieselbe Bildverarbeitung.
  Vorhandene registrierte Rasterbilder sind ebenfalls als Quelle verwendbar;
  ihre Dateien werden nicht verändert. SVG bleibt ansehbar und zuordenbar.
  Grenzen: 20 MiB und 40 Megapixel beim Import, maximal 4096 Pixel je Ausgabeseite;
  kein freies Malen, Textsatz, Freistellen oder Import animierter Bilder.
- image_store.py, image-editor.js und image-editor.css ergänzen den bestehenden
  Speicher und die Oberfläche. Persönliche Bilddateien unter design-library/images
  werden ignoriert. Bereits installiertes Pillow 12.3.0 in requirements-local.txt
  festgehalten; keine Installation oder externen Downloads ausgeführt.
- 40 Speicher-, Bild-, Sammlungs-, HTTP- und Startertests bestanden; JavaScript-
  Syntax geprüft. Browserprüfung in getrennter Ablage auf 8777: nativer Dateiimport,
  Ausschnitt 100/50/400/300, Titelbild 640×480, exaktes Wiederöffnen, Verschieben per
  Tastatur und Maus, quadratisches Icon 128×128 aus demselben Original. Beide
  Varianten einer frei benannten Mappe zugeordnet und Interview-Übergabe geprüft.
  Dateigrößen, Pixelmaße, Quellbezug und SHA-256 unabhängig kontrolliert.
- Schmale Ansicht bei tatsächlichen 390 px Rahmenbreite sichtbar kontrolliert.
  Keine Browserwarnungen/-fehler beobachtet. Der erfolgreiche native Dateidialog
  benötigte trotz begrenzter Aufrufzeiten 72,5 Sekunden; ein Ganzseitenfoto schlug
  fehl, nachfolgende Ansichts- und Mobilaufnahmen gelangen. Keine Wiederholschleife.
- Nur den persönlichen Werkstattdienst auf 8776 mit derselben Ablage neu gestartet.
  Aktueller Gesundheitsstatus ok; vorhandener Starter erkennt und verwendet den
  Dienst. Persönliche Bildwerkstatt geöffnet; spätere Abschlussansicht Würfel
  unverändert belassen. Prüfseiten und eigener Prüfdienst auf 8777 geschlossen.
- Alle fünf vorab erfassten persönlichen JSON-Dateien SHA-256-identisch. Zusätzlich
  vorgefundenen persönlichen Brettentwurf bewahrt. Keine Prüfbilder in die
  persönliche Bibliothek importiert. Buttonrenderer und bisherige Modellgeneratoren
  nicht ersetzt. Kein externer Serverkontakt, keine Veröffentlichung oder Änderung
  an Spielen, Konten oder Nutzungshistorie.
- Dokumentation unter offline-preview/game-workshop-v1/README.md,
  design-library/README.md und docs/BAUKASTEN.md aktualisiert. Nachweise unter
  runtime/image-workshop-20261026/: verification.json, projekt-uebergabe.png,
  390px.png und source-before/. bildwerkstatt.png zeigt die spätere lokale
  Abschlussansicht mit Würfeln, nicht die Bildbearbeitungsprobe.

## 2026-10-26 – Nutzerpräzisierung: Basis, bestehende Spielelemente und gemeinsame Editorprüfung

- Eine gemeinsame Projektvorschau wird vom Nutzer als verfrüht zurückgestellt.
  Vorrang haben die Elementarten, verständliche und sinnvolle Editoroptionen
  sowie die Verbindung der Werkstatt mit dem tatsächlichen Spielebestand.
- Hintergründe, Titelbilder und Flyer werden importiert, extern bearbeitet oder
  von Codex gestaltet und anschließend aufgenommen. Sie sollen ausdrücklich
  nicht als editierbare Elemente angezeigt werden. Diese Vorgabe ersetzt die
  vorherige Einordnung dieser drei Arten als Bildeditoren; vorhandene Originale
  und Varianten bleiben erhalten. Die Oberflächenkorrektur ist noch umzusetzen.
- Fenster als weitere Elementfamilie aufnehmen; genannt wurden Dialogboxen und
  Inventare. Die übrigen Elementarten sollen entsprechend ihrer tatsächlichen
  Gestaltungsmöglichkeiten editierbar werden. Der konkrete Optionsumfang ist
  je Editor gemeinsam zu klären, nicht aus der bloßen Kategorie abzuleiten.
- Bestehende Spiele auf noch fehlende Elemente und gemeinsame Muster prüfen.
  Bereits eingesetzte Buttons und andere Bausteine sind Ausgangsbestand für
  Bibliothek und Verwendungszuordnung. Vorhandensein im Spiel allein ist noch
  kein Nachweis eines eigenständig gespeicherten Werkstattentwurfs.
- Ziel: gespeicherte, möglichst zuordenbare und gegebenenfalls editierbare
  Elemente mit gemeinsamer Grundimplementierung auch an ihren Einsatzorten.
  Die notwendige Anpassung bestehender Einbindungen ist Teil dieses Aufbaus.
  Keine unabhängigen Gestaltungskopien pro Spiel anlegen.
- Nutzer wünscht die Prüfung einzelner Editoroptionen im Gespräch: erklären,
  gezielt befragen, Optionen entfernen, verändern oder ergänzen. Auswahlbestände
  einschließlich recherchierter, kategorisierter Geräusche dürfen bedarfsbezogen
  hinzukommen. Eine Reihenfolge und konkrete Editoränderungen sind noch gemeinsam
  festzulegen. In diesem Schritt nur Festlegungen dokumentiert; keine Oberfläche
  oder bestehende Spieleinbindung umgebaut und keinen externen Server kontaktiert.

## 2026-10-26 – Bestandsaufnahme begonnen, Bildarten eingeordnet und Buttonflächen erweitert

- Nutzer bestätigt die Reihenfolge: tatsächlichen Bestand und Elementarten
  vervollständigen, Werkstatt korrekt einordnen, Buttonoptionen gemeinsam prüfen,
  anschließend einen vollständigen Einsatzweg an der lokalen Startseite herstellen
  und das Vorgehen auf weitere Editoren übertragen. Projektvorschau zurückgestellt.
- deploy/inventory_workshop_elements.py liest lokale Spielquellen ohne App-Import,
  Datenbankzugriff oder Serverkontakt. WERKSTATT_BESTAND.json erfasst 19 Familien
  mit Zeilennachweisen und Prüfsummen: 85 UI-Quelldateien, insgesamt 97 belegte
  Quelldateien; 126 Button-, 44 Eingabe- und drei explizite Dialogquellstellen,
  fünf dynamische Erzeugungsstellen und 254 einschlägige CSS-Definitionen.
  Dies sind Quellvorkommen, keine Zahl gerenderter Instanzen oder automatisch
  gespeicherter Bibliothekselemente. Alle Familienbelege nochmals überprüft.
- Daily Quiz, Party, Perfect, Playtable, Würfeltisch, Kniffel, Mäxchen, Conquest,
  Profil und Sammlung berücksichtigt. Bestehende Startseitenbuttons besitzen
  eigene CSS-Grundlagen; Conquest lädt einen gespeicherten Entwurf über den
  kanonischen Werkstatt-Renderer. Alte static/conquest-table.js nicht als Beleg
  für die aktuelle, über scene.js/table-surface.js geladene Oberfläche ausgegeben.
- Fenster in derselben Elementliste bei Gestalten und Bibliothek aufgenommen:
  Regeln, Startseitenentscheidung, Aufträge, Inventar/Kartenhand und Aktionsflächen.
  Anzeige nennt ausdrücklich fünf erfasste Arten; keine gespeicherten Vorlagen
  oder vorhandenen Fenstereditor behauptet. Eingaben, Anzeigen, Spieler/Pulte,
  Klänge, Schriften und Materialbestände als weitere Zuordnungsbedarfe dokumentiert.
- Hintergründe, Titelbilder und Flyer verwenden nun eine gemeinsame Import- und
  Auswahlansicht statt des Bildeditors. Fertige Bilder hinzufügen, ansehen und
  direkt zuordnen; Weitergestalten in ihrer Bibliotheksansicht ausgeblendet.
  Alte Originale und Varianten unverändert erhalten. Icons/Avatarbilder behalten
  den gemeinsamen Ausschnitteditor, dessen Ausgabekategorien auf diese beiden
  Arten begrenzt sind. API und Originalspeicherung unverändert weiterverwendet.
- Beim ersten Optionsdurchgang entscheidet der Nutzer: Materialauswahl um das
  ergänzen, was die tatsächlich bestehenden Spielbuttons benötigt. Daraus im
  gemeinsamen Buttonrenderer Farbfläche, zweifarbiger Verlauf und durchscheinende
  Fläche ergänzt; Holz, Stein und Metall bleiben bestehen. Zwei Farben beim Verlauf,
  Flächendeckkraft bei durchscheinenden Flächen, entsprechende Startvorlagen und
  kurze Erläuterungen verfügbar. Unwirksame Spuren-/Strukturregler für diese drei
  Arten ausgeblendet, Glanz bei durchscheinenden Flächen ebenfalls ausgeblendet.
- Neue Werte gradient_to und opacity werden beim Lesen alter Rezepte mit Defaults
  ergänzt; bestehende Dateien werden nicht umgeschrieben. Ursprüngliche Kontur-
  geometrie unverändert. Durchscheinende Flächen verwenden denselben Konturpfad
  auch für ihren sichtbaren Rand; Deckkraft verändert nicht die Beschriftung.
  Bei automatischem Materialklang für diese Flächen klare fehlende Zuordnung statt
  erfundenem Materialklang. Rendererstand button-workshop-v5.
- Oberflächenbedarf mit Belegen unter button_surface_coverage erfasst: Lobbyfarbe,
  Karten-/Würfelverlauf, durchscheinende Nebenaktionen. Perfect-Buzzer als eigener
  vorhandener Bildbutton erfasst, noch nicht als Werkstattrezept übernommen.
  Die neuen Startvorlagen sind Beispiele auf der gemeinsamen Werkstattform.
  Vollständige Originalübernahme, Kontur/Rahmen, Schrift, Bewegung und tatsächliche
  Spieleinbindung bleiben weitere Arbeiten; keine pauschale Umgestaltung ausgeführt.
- 40 bestehende gemeinsame Werkstatt-/Bild-/Speicher-/HTTP-/Startertests bestanden;
  zwölf Buttontests einschließlich neuer Oberfläche und Altdateikompatibilität
  bestanden. Geometrie-, Proportions-, Schrift- und Audio-Prüfdateien sowie JS-Syntax
  bestanden. Browserprüfung nur mit kopierter Bibliothek auf 8777: Clubzimmer aus
  Importansicht einer neuen Prüfmappe zugeordnet, Bildansicht ohne Bearbeiten,
  Titelbild/Flyer ohne Ausschnitteditor, Iconeditor weiterhin verwendbar. Drei neue
  Buttonflächen gespeichert, Verlauf mit beiden Farben wieder geöffnet und die
  Deckkraftgrenzen 0/100 ausprobiert. Gespeicherte Werte unabhängig kontrolliert.
- Beide persönlichen Werkstattdienste gezielt neu geladen: 8771 erst nach Prüfung
  von Prozesskennung, Kommandozeile und Listener; 8776 über eigenen Dienst.
  Gleiche unveränderte persönliche Ablagen. Beide API-Kataloge identisch mit sechs
  Materialfamilien; Starter erkennt und verwendet beide Dienste. Neue Bildansicht
  und Materialauswahl mit persönlichem Bestand im Browser beobachtet, keine
  Konsolenwarnungen/-fehler. Prüfseiten und eigener Prüfdienst 8777 geschlossen.
- Alle sechs vorab erfassten persönlichen JSON-Dateien SHA-256-identisch. Keine
  neuen Prüfeinträge im persönlichen Bestand. Generatoren, Bildspeicher, Bibliotheks-
  und Projektspeicher, Konturgeometrie und bestehende Spielquellen unverändert.
  Dokumentation und Quellbericht aktualisiert. Nachweise unter
  runtime/workshop-basis-20261026/: before.json, source-before/, verification.json,
  fensterbestand.png, bildauswahl.png, farbverlauf.png, durchscheinend.png,
  deckkraft-null.png, farbflaeche.png und persoenliche-buttonauswahl.png.
  Nativen Dateidialog für die reine Importansicht nicht erneut ausgeführt;
  Import-Endpunkt durch bestehende HTTP-Tests abgedeckt. Kein externer Serverkontakt,
  keine Veröffentlichung und keine Änderung an Konten, Partien oder Nutzungshistorie.

## 2026-10-26 – Originalbuttons zugeordnet, Werkstatteinstieg berichtigt und Schrifttiefe getrennt

- Frühere Erledigungsaussage präzisiert: 19 erfasste Elementfamilien waren eine
  Quellbestandsaufnahme, keine 19 eingerichteten Werkstattbereiche. Die Oberfläche
  nennt nun ausdrücklich zwölf Elementbereiche und 19 erfasste Familien. Die
  sieben weiteren Familien stehen als Bestandsbedarf, ohne angebotenen Editor.
  Die zuvor ergänzten Materialarten waren keine Übernahme der Originalbuttons.
- Desktopverknüpfung Werkstaetten-starten.cmd - Verknüpfung.lnk gelesen und
  unverändert erhalten: Ziel D:\Guesstimate\Werkstaetten-starten.cmd, Arbeitsordner
  D:\Guesstimate. Derselbe Starter führt jetzt zur gemeinsamen Werkstatt auf
  http://127.0.0.1:8776/#editor/buttons. Alte Übersicht und einzelner Buttoneditor
  verweisen auf dieselbe Werkstatt/Bibliothek; keine Entwürfe oder Seiten gelöscht.
  Ausführung des tatsächlichen Starterziels mit --no-browser erfolgreich:
  alle vier vorhandenen Dienste wiederverwendet, kanonische Einstiegsadresse gemeldet.
- source_buttons.py erfasst ohne App-Import und ohne Datenbankzugriff 106 aktuell
  verwendete Quellbuttons: 99 aus tatsächlich verbundenen Jinja-Vorlagen und sieben
  Conquest-Aktionen mit bestehender Anbindung an den gemeinsamen Buttonrenderer.
  Darunter Guesstimate-Startseite einschließlich spielen, heutiges Ergebnis und
  verpasste Runden. Bibliothek nach Im Spiel verwendet sowie Spiel/Einsatz filterbar.
  Direkter Einstieg: http://127.0.0.1:8776/?source=game&game=Guesstimate#library/buttons.
- Originalvorschauen verwenden vorhandene HTML-Fragmente und Stylesheets mit
  Quellenpfad, Quellposition und Prüfsummen; keine separat nachgebaute Spieloberfläche.
  Vorschau in inaktivem, abgeschirmtem Frame ohne Skript- oder Formularausführung;
  gemeinsame Vorschauhülle skaliert proportional. Dynamische Werte sind kenntliche
  Beispieldaten, keine echten Spieler-/Kontodaten. Stylesheet-Prüfsummen werden
  vor der Vorschau geprüft. Quellbezüge sind keine vollständige historische Medienkopie.
- Originale über vorhandene Projektzuordnung als genaue Quellsnapshots nutzbar.
  Reine HTML/CSS-Originale einschließlich Guesstimate sind zunächst ansehbar und
  zuordenbar; ihre Editoranbindung bleibt ausdrücklich offen. Die sieben bereits
  angebundenen Conquest-Aktionen lassen sich als eigene Entwürfe im selben Editor
  öffnen und speichern. Dadurch wird keine bestehende Spielaktion automatisch ersetzt.
- Nutzer meldet fehlende Schriftgröße und schwarze, vom Schatten nicht getrennte
  Seitenflächen. Schriftgröße nun unabhängig von der Buttongröße regelbar, 50–160 %.
  Buttongröße steht bei Form und Kontur. Seitenwände verwenden einen materialfarbigen
  Verlauf; separater weicher Schlagschatten ist von 0–60 % einstellbar. Einheitlicher
  Rendererstand button-workshop-v6. Alte Rezepte erhalten nur beim Lesen kompatible
  Defaults für font_scale und shadow; vorhandene Dateien nicht umgeschrieben.
- 46 gemeinsame Python-Tests und zwölf Buttontests bestanden, insgesamt 58.
  Node-Prüfungen für Geometrie, Proportionen, Schriften und Audio sowie JS-Syntax
  bestanden. Neue Prüfungen decken Quellvorschau/CSP, Original-CSS, Quellsnapshots,
  Projektzuordnung/Übergabe und die Übernahme kanonischer Rezepte ab.
- Browserprüfung mit kopierter Bibliothek: Original spielen sichtbar, einer eigenen
  Prüfmappe zugeordnet; Conquest-Aktion als Entwurf geöffnet, verändert, gespeichert
  und erneut geöffnet. Schrift von 32 auf 51,2 Pixel vergrößert, Button dabei
  unverändert 384 Pixel breit und 131,421875 Pixel hoch. Materialfarbige Seitenwände
  sowie äußerer Schatten sichtbar getrennt; Schatten auf null gestellt und Rezept
  mit Schriftgröße 160 %, Tiefe 12 und Schatten 20 % wieder geöffnet.
- Persönliche Dienste 8771/8776 verwenden identische Kataloge und denselben
  gemeinsamen Renderer. Persönliche Guesstimate-Bibliothek auf 8776 im Browser
  mit beiden Filtern geprüft und geöffnet gelassen; keine ungespeicherte Nutzerseite
  zwangsweise neu geladen. Prüfseiten geschlossen und eigener Prüfdienst 8777 beendet.
  Alle sechs ursprünglichen persönlichen JSON-Dateien weiterhin SHA-256-identisch;
  zusätzlich vom Nutzer angelegter Entwurf erhalten, insgesamt sieben persönliche
  JSON-Dateien. Keine Prüfeinträge im persönlichen Bestand.
- Diagnostik: Editor ohne Konsolenfehler; bei Originalvorschau-Frames meldet der
  Browser MutationObserver.observe mit ungültigem Node-Parameter. Ursache nicht
  belegt; ausgelieferte Werkstattmodule enthalten keinen MutationObserver, Skripte
  der Originalvorschau sind per CSP gesperrt. Sicht-/Zuordnungsprüfungen bestanden.
  Diese Meldung bleibt offen; keine pauschal fehlerfreie Bibliothekskonsole behauptet.
- Nachweise unter runtime/workshop-gamebuttons-20261026/: before.json, source-before/,
  verification.json, guesstimate-original.png, schrift-seitenwaende.png und
  persoenliche-bibliothek.png. Dokumentation und Bestandsbericht aktualisiert.
  Keine Spielvorlagen oder Spielzustände ersetzt, keine Konten-/Nutzungsdaten verändert,
  kein externer Serverkontakt und keine Veröffentlichung. Die gemeinsame lokale
  Buttondarstellung verwendet überall dieselbe aktualisierte Grundimplementierung.

## 2026-10-26 – Originale im Editor und Buttonmodelle mit einzeln erhaltenen Varianten

- Verbindliche Nutzerpräzisierung: Die Editorfunktionen richten sich nach den
  vorhandenen Buttons. Aussehen und Spielfunktion der Originale dürfen bei dieser
  Anbindung nicht verändert werden. Zusätzlich gleiche Gestaltung mit anderer
  Beschriftung/Einsatzstelle in der Bibliothek zu einem Modell zusammenfassen.
  Unterschiedliche Gestaltungen bleiben getrennt. Vor einer optischen Angleichung
  zum Zweck weiterer Vereinheitlichung muss der Nutzer entscheiden; nicht automatisch
  umgestalten, ersetzen oder beide Vorgaben vermischen.
- Alle 106 registrierten Quellbuttons im bestehenden Editor öffnbar. Die sieben
  bereits angebundenen Conquest-Aktionen behalten ihren bisherigen Rezept-/Rendererpfad.
  Für 99 HTML/CSS-Originale liest source-renderer.js dieselben registrierten Quellen
  und Stylesheets in einem skriptfreien, inaktiven Frame. Keine Annäherung an eine
  andere Werkstattkontur. Original- und Entwurfsansicht nutzen dieselbe Grunddarstellung.
- source-editor.js erkennt den Button und seine vorhandenen Unterteile einschließlich
  Bild, Symbol, Beschriftung und Zusatzflächen. Regler für Schrift, Text, Maße,
  Innenabstände, einzelne Ecken, Rahmen, Fläche/Verlauf, Flächen-/Gesamtdeckkraft,
  einzelne äußere/innere Schatten, Textschatten und vorhandene Bildfilter. Original-
  zustand, Hover, Druck, Fokus und Sperre sind reine Ansichtsproben ohne Spielaktion.
  Eigene Änderungen, Rückgängig, Wiederholen sowie Teil-/Originalzurücksetzen verfügbar.
  Bestehende prozedurale Werkstattentwürfe und Kontureditor bleiben erhalten.
- Rezeptformat 3 speichert geprüften Quellnachweis und erlaubte Gestaltungsänderungen
  getrennt vom Original. Änderungen an Quelle, Ereignissen oder Spielfunktionen werden
  nicht angeboten. CSS- und HTML-/Skriptinjektionen werden abgewiesen; gerendert wird
  nur eine serverseitig registrierte Quelle, kein importiertes ausführbares Markup.
  Neue Speicherung erzeugt eine eigene Version; alte Entwürfe werden nicht überschrieben.
  Dieselbe Anbindung in gemeinsamer Werkstatt und einzelnem Buttoneditor verfügbar.
  Der Renderer erhält die Originalanbindung ausschließlich durch Registrierung in der
  Werkstatt; bestehende Spiele benötigen dadurch keine zusätzlichen Modulimporte.
- Bibliothek zeigt 106 Spielquellen als 54 Modelle: 53 HTML/CSS-Modelle und ein
  gemeinsames Conquest-Rezeptmodell. Eigene Entwürfe und Formen kommen zusätzlich
  hinzu. Varianten/Einsatzorte im Modelldialog auswählbar; Bearbeiten und Zuordnen
  beziehen sich auf die konkrete Variante, nicht auf alle Spieleinsätze. Suche und
  Filter finden Modelle über ihre Varianten. Gespeicherte Varianten gleicher
  Gestaltung mit anderem Text teilen ebenfalls ein Modell. Projektkennungen und
  vorhandene Zuordnungen unverändert; keine Quellbuttons entfernt oder umgestaltet.
- button-models.json enthält die mit Quellenkennungen verbundenen Gestaltungsnachweise.
  Browservergleich neutralisiert nur Text in eigenen Vorschaukopien und vergleicht
  den vollständigen berechneten Aufbau einschließlich Zusatzflächen bei 1000/390 px
  sowie Normal-, Hover-, Druck-, Fokus- und Sperrzustand; ursprüngliche Bewegungs-
  definitionen mitberücksichtigt. Geänderte Markup-/CSS-Quellen erhalten neue Kennungen
  und erben keine Gruppierung ungeprüft. Keine automatische Konzept-/Designangleichung.
- source-check.html: alle 99 HTML/CSS-Originale gegen die unveränderte Adapteransicht
  geprüft, keine Abweichung der berechneten Komponentengestaltung. Das ist eine lokale
  Quellen-/Vorschauprüfung, keine neue Prüfung sämtlicher laufender Spielfunktionen.
  Speichern und Wiederöffnen in getrennter Prüfbibliothek: Schrift 28 px, linke obere
  Ecke 4 px und eigener Text erhalten; Originalvergleich weiterhin 15,3 px, 17 px und
  spielen. Rückgängig auf gespeicherten Stand sowie vollständiges Zurücksetzen geprüft.
- 51 gemeinsame Python-Tests und zwölf Tests des einzelnen Buttoneditors bestanden,
  insgesamt 63; Node-Prüfungen für Geometrie/Proportionen/Schriften und Audio sowie
  JS-Syntax bestanden. Neue Tests decken alle Originalrezepte, unveränderte Quellen,
  getrennte Speicherung, Übergabe, abgewiesene Eingriffe und Modell-/Variantengruppen ab.
- Persönliche Dienste 8776 und 8771 anhand vollständiger Prozesspfade identifiziert,
  gezielt mit denselben Bibliotheken neu geladen. Beide liefern identisches Original-
  rezept. Persönliche Bibliothek sichtbar mit zehn Guesstimate-Modellen geprüft,
  Siebenergruppe geöffnet, konkrete Variante antwort einloggen im Editor beobachtet.
  Persönliche Navigation zählt 59 Modelle/Formen einschließlich fünf eigener Einträge.
  Kein Prüfrezept in der persönlichen Bibliothek; alle sieben persönlichen JSON-Dateien
  und insgesamt 353 geschützte Dateien aus templates/, static/, Conquest und Bibliothek
  SHA-256-identisch zum Beginn dieses Schritts. Keine Spiele, Konten oder Nutzungshistorie
  verändert, keine Originalfunktion ersetzt, kein externer Serverkontakt.
- Nachweise: runtime/source-button-editor-20261026/before.json, verification.json,
  original-comparison.json, edited-original.png und getrennte qa/-Bibliothek.
  Frühere MutationObserver-Meldungen der Browser-Frame-Diagnostik weiterhin im
  Sitzungsprotokoll sichtbar; Ursache ungeklärt, nicht als behoben ausgegeben.
- Eigener Prüfdienst 8777 anschließend beendet. Persönliche Modellgruppe mit sieben
  auswählbaren Einsatzvarianten geöffnet gelassen; keine Nutzereingaben gespeichert.
  Weitere Bildnachweise: personal-models.png und model-variants.png. Das Schließen
  einer älteren Prüfseite wurde vom Browser wegen geänderter Sitzungszuordnung
  abgewiesen; keine Wiederholung oder Zugriff auf andere Nutzerseiten vorgenommen.

## 2026-10-26 – Nutzerkorrektur umgesetzt: Originale im gemeinsamen Kontureditor

- Nutzer verwirft die separate CSS-Regleroberfläche für Originalbuttons ausdrücklich:
  vorhandene Buttons sollen in denselben Editor wie Werkstatt-Holz geladen werden,
  mit Form/Kontur, Fläche, Tiefe und Beschriftung. Kerben müssen mit demselben
  Punktwerkzeug möglich sein. Diese Entscheidung ersetzt den vorherigen Bearbeitungs-
  weg über source-editor.js; dessen separate Oberfläche und CSS entfernt. Originale
  in den Spielen bleiben unverändert; weitere Designangleichungen weiterhin nur
  nach Nutzerentscheidung. Modell-/Variantenübersicht bleibt bestehen.
- 99 HTML/CSS-Quellen in Ausgangsmaße, Oberfläche, Tiefe, Beschriftung und vorhandene
  Bild-/SVG-Daten zerlegt, mit Quellkennungen unter button-profiles.json verbunden.
  profile_recipe.py und unified-import.js übertragen diese in das gemeinsame Rezept-
  format 4. Gemeinsamer renderer.js erzeugt dieselbe Buttonkomposition wie bei eigenen
  Entwürfen; kein bearbeitbarer Originalbutton-Frame und keine zweite Reglerliste.
  Die sieben bereits angebundenen Conquest-Aktionen behalten ihren gemeinsamen Weg.
- Bestehende Geometrie um variable Formhöhe, Ausgangsproportionen und physisch runde
  Ecken ergänzt. Gemeinsamer ContourEditor verwendet dieselbe Zeichenebene wie Fläche
  und Seitenwand. Source-Beispiel weiter zu frage 2: 430 × 50 Pixel, Schrift 15 Pixel,
  vier Punkte mit 17-Pixel-Ecken, Fläche #d8ff42, unabhängige Tiefe #8e80ff mit fünf
  Pixeln Versatz. Ein Randpunkt wird direkt zur Kerbe; dieselbe Kontur gilt für die
  Fläche und die Tiefe. Größenänderung skaliert die Komposition proportional.
- Vorhandene Gruppen Material, Form/Kontur, Schrift und Tiefe/Bewegung beibehalten.
  Formhöhe, eigene Schrift-/Seitenwandfarbe und seitlicher Tiefenversatz ergänzt;
  Tiefe einschließlich null wählbar. Klare Beschriftung und Schrift der Vorlage
  verfügbar. Kein Innenabstands-/Einzelecken-/Bauteil-CSS-Editor mehr. Wechsel zu Holz
  mit natürlicher Darstellung im selben Editor geprüft, Kerbe bleibt erhalten.
- Rezeptformate 1/2/3 weiter lesbar. Format 3 wird beim Öffnen in das gemeinsame
  Rezept übersetzt; persönliche Dateien nicht umgeschrieben. Speichern bleibt
  versioniert und getrennt von der Spielquelle. source-renderer.js nur noch für
  unveränderte Originalvergleiche und alte Bibliotheksvorschauen. Grundform-Zurücksetzen
  stellt bei übernommenen Buttons deren ursprüngliche Kontur wieder her; bei alten
  Vorlagen weiterhin die Kataloggrundform. Rückgängig stellt die Kerbe wieder her.
- 53 gemeinsame Python-Tests und zwölf Buttontests bestanden, insgesamt 65.
  Node-Geometrie-/Schrift-/Audio-Prüfungen und Syntax bestanden. Neue Prüfungen für
  430:50-Proportionen, kreisrunde Ecken, gleiche Zeichen-/Buttonkontur, proportionale
  Tiefe/Schrift, gespeicherte Kerbe und abgewiesene fremde Bilder/ausführbare Grafiken.
  Frühere ungültige Testwerte 5 für Tiefe und 46 für Rundung liegen durch die bewusste
  Erweiterung nun im gültigen Bereich; Grenztests auf 100 beziehungsweise 51 umgestellt.
- Getrennte Prüfbibliothek: Kerbe über das vorhandene Punktwerkzeug eingefügt,
  gespeichert und wieder geöffnet; fünf und später sieben Punkte erhalten. Fläche
  und Tiefe besitzen denselben Konturpfad. Original-Grundform vier Punkte, Rückgängig
  zurück zu fünf Punkten geprüft. Der Browser-Hittest trifft im ausgesparten Bereich
  die transparente Buttonhülle statt der Fläche. Persönliche Werkstatt: Original über
  Bibliothek geöffnet, gemeinsamer Kontureditor mit vier Punkten sichtbar; keine
  Teständerung dort gespeichert. Originaldarstellung des genannten Beispiels geprüft;
  keine pixelgenaue Prüfung sämtlicher komplexer Bild-/Pseudoelementdekorationen behauptet.
- Persönliche Dienste 8776/8771 gezielt mit denselben Ablagen neu geladen. Beide
  liefern dasselbe gemeinsame Originalrezept; 106 Quellen / 54 Modelle weiterhin
  vorhanden. Alle sieben persönlichen JSON-Dateien und insgesamt 353 geschützte
  Quellen/Assets/Entwürfe SHA-256-identisch. Keine Spiele, Konten, Spielaktionen oder
  Nutzungshistorie geändert; kein externer Serverkontakt und keine Veröffentlichung.
- Nachweise unter runtime/unified-button-editor-20261026/: before.json,
  source-before/, verification.json, kerbe.png, common-editor.png und getrennte qa/.
- Eigene Prüfseiten geschlossen und Prüfdienst 8777 beendet. Persönlichen
  Guesstimate-Button im gemeinsamen Kontureditor geöffnet gelassen.

## 2026-10-26 – Buttonmodelle vergleichen und Startseitenzustände zuordnen

- Vergleichsansicht innerhalb der bestehenden Bibliothek ergänzt, erreichbar über
  „Guesstimate-Modelle vergleichen“. Zehn Einsatzsituationen mit Originalvorschauen,
  Aufgabe, Form/Fläche/Tiefe/Schrift und vorhandenen Beschriftungen nebeneinander.
  Dieselben inerten Originalvorschauen wie in der Bibliothek verwendet; kein neuer
  Buttoneditor und keine nachgebauten Vergleichsgrafiken. Auswahlzustand der
  Antwortoption nur in der Vorschau umschaltbar, ohne Spielaktion.
- Nutzer präzisiert: Spielen/Fortsetzen und heutiges Ergebnis sind Umstände derselben
  Startseitenaktion. Als freigegebene Gruppe guesstimate-start-action in
  button-models.json aufgenommen. Bibliothek zeigt ein Modell mit getrennt benannten
  Zuständen und Einsatzvarianten. Quellkennungen und tatsächliche Spielfunktionen
  unverändert. Damit 106 Quellen / 53 Modelle insgesamt, neun Guesstimate-Modelle
  bei zehn Vergleichssituationen. Automatische Modellzuordnung bleibt bestehen;
  freigegebene Gruppen müssen bei ihrer Neuerzeugung erhalten bleiben.
- „Alle verpassten Runden nachholen“ soll nach Nutzerentscheidung denselben
  Startseitenstil verwenden. Aktuelle Form, Fläche und Tiefe ausdrücklich nicht
  angeglichen: Nutzer möchte den gemeinsamen Editor daran selbst prüfen. Karte 03
  öffnet über „Im Editor testen“ den vorhandenen gemeinsamen Editor mit eigenem
  Quellrezept; Titel, Tiefe 5 und vier Konturpunkte dort sichtbar geprüft.
  Weitere Modell-/Stilangleichungen sind nur gekennzeichnete Vorschläge.
- Vergleichskarten vor den jeweils folgenden Vorschauen in den sichtbaren DOM
  eingefügt, damit die vorhandene Größenbeobachtung erhalten bleibt. Proportionale
  Vorschaugrößen geprüft. Original-Framehöhe 600 wie bei der Profilaufnahme;
  Schrift-/Ladebereitschaft abgewartet. Spielen und Ergebnis zeigen beide native
  430 × 58 Pixel und dieselbe Normaldarstellung, mit unterschiedlicher Beschriftung.
- Zwölf gezielte Python-Quellbuttontests bestanden. JS-Syntax und Zuordnung der zehn
  Vergleichssituationen zu tatsächlichen Quellen geprüft. Persönliche Bibliothek:
  ein Startseitenmodell und beide Zustandsbeschreibungen sichtbar. Vergleich und
  Auswahlvorschau sowie Übergabe des Nachholbuttons an den gemeinsamen Editor geprüft.
- SHA-256-Vergleich: alle 353 geschützten Spiel-/Asset-/Bibliotheksdateien unverändert;
  einzige Änderung unter 354 erfassten Dateien ist die freigegebene Modellmetadatei.
  Sieben persönliche JSON-Dateien erhalten, keine Prüfentwürfe dort gespeichert.
  Vorhandene andere Arbeitsänderungen bewahrt. Keine Spiele, Konten, Ergebnisse,
  Zugangsdaten oder Nutzungshistorie verändert; kein externer Serverkontakt und
  keine Veröffentlichung.
- Lokale Werkstatt 8776 gezielt mit derselben persönlichen Ablage neu geladen.
  Nutzerseiten mit möglichen Entwürfen nicht neu geladen; Vergleich in eigener
  Seite geöffnet gelassen. Getrennte Prüfseite und eigener Prüfdienst 8777 beendet.
  Nachweise: runtime/button-model-review-20261026/before.json, verification.json,
  review-data.json und vergleich.png. Frühere Browser-Frame-Diagnosemeldungen
  weiterhin nicht als behoben oder als Ursache eines Spielfehlers ausgegeben.

## 2026-10-26 – Buttonaufnahme je Spiel vervollständigt; persönliche Aktivierung offen

- Auftrag: vorhandene Buttons Spiel für Spiel aufnehmen, Originalaussehen und
  Spielfunktionen erhalten. Kandidaten für gemeinsame Modelle/Optionen erfassen;
  falls dafür optische Änderungen erforderlich sind, zuvor Nutzerentscheidung.
  Besprochener Startseitenstil/Nachholbutton bleibt für den persönlichen Editortest
  unverändert. Keine weitere optische Angleichung ausgeführt.
- Erkennung folgt jetzt auch render_overview und den daraus referenzierten gemeinsamen
  Lobbyvorlagen. Navigations- und Zurückknöpfe, Profil-Bearbeitung und die weiteren
  aktuellen Conquest-Tischaktionen ergänzt. Vorherige Parser-Ordnungen bleiben für
  bestehende Quellen stabil: alle 106 bisherigen Quellkennungen/Snapshots erhalten.
- 38 Verwendungen ergänzt, insgesamt 144 Verwendungen als 85 Modelle. Darunter 137
  HTML/CSS-Quellansichten und sieben bereits über den gemeinsamen Renderer angebundene
  Conquest-Aktionen. Gemeinsame Komponenten über ihre Verwendungszuordnung im jeweiligen
  Spielfilter auffindbar, ohne Spielkopien. Würfeltisch, Kniffel und Mäxchen separat
  wählbar. Abweichende Kniffel-Konsolengestaltung als vorhandene Kontextvariante erhalten.
- deploy/capture_generated_buttons.mjs liest die tatsächlichen DOM-Erzeugungsfunktionen
  für gehaltene/abgelegte Würfel, Kniffel-Ergebniseinträge und Kartenanzahl am Avatar.
  Inaktive Beispieldaten mit Quellprüfsummen unter generated-buttons.json; keine
  Spielhandler, App-/Datenbankimporte oder Netzwerkaufrufe ausgeführt. Würfelsymbol
  aus derselben vorhandenen Symbolfunktion übernommen. Geänderte Erzeugungsnachweise
  werden erkannt und nicht ungeprüft weiterverwendet.
- deploy/audit_button_coverage.py ordnet verbundene Vorlagen und eigene Skripte je
  Quelle zu; aktuell keine ungeklärte native Buttonstelle oder Erzeugungsfunktion.
  Bericht docs/BUTTON_BESTAND.md/.json nennt Spiele, Quellen und Grenzen. Klickflächen
  auf Länder-/Belohnungskarten gehören zu Karten, Truppenmarken zu Figuren/Spielsteinen.
  Nur im Offline-Beispiel verwendeter Neustartknopf sowie nicht eingebundene alte
  static/conquest-table.js ausdrücklich abgegrenzt. Normale Textlinks, Logos, Flyer,
  Aufklappüberschriften und Eingaben nicht als zusätzliche Buttonmodelle ausgegeben.
- Gemeinsame Vorschauhülle erhält relevante Vorfahren-IDs. Versteckte Aktionen nur
  in der inerten Vorschau sichtbar gemacht; Spielsichtbarkeit unverändert. Makro-
  Beispiel „lobby verlassen“ mit tatsächlichem Standardtext statt leerer Beschriftung.
  Generierte Würfeloberfläche aus ihrem vorhandenen Unterelement gelesen. Bei reinen
  SVG-Symbolbuttons bleibt der Zugänglichkeitsname erhalten und wird nicht zusätzlich
  als sichtbare Beschriftung auf den Entwurf gedruckt. Dieselbe gemeinsame Renderer-
  Implementierung; bestehende Rezepte ohne dieses neue Profilmerkmal unverändert.
- Vorhandene Profile/Modellnachweise ergänzt und freigegebene Startseiten-Zustandsgruppe
  bewahrt. Alle 144 Rezepte validiert. 137 isolierte Original-/Adapteransichten ohne
  berechnete Gestaltungsabweichung geprüft; Lobby-Standardtext danach gezielt erneut
  geprüft. Laufende Einblendanimationen für die Quellenmessung in beiden isolierten
  Frames an denselben Zeitpunkt gesetzt, Definitionen erhalten. Kein solcher Eingriff
  in eine tatsächliche Spielseite. Keine pixelgenaue Prüfung sämtlicher Spielzustände
  oder Ausführung sämtlicher Spielaktionen behauptet.
- 36 gezielte Python-Tests für Quellbuttons, Werkstatt und Projektzuordnung bestanden.
  Zusätzlich Node-Geometrie-/Schrift-/Proportionsprüfungen und geänderte JS-Syntax
  bestanden. Neue Tests decken Lobby-Hilfsfunktion, gemeinsame Verwendungen, erzeugte
  Quellen/Prüfsummen, Kniffel-Kontext, reine Vorschau-Sichtbarkeit und Symbolbeschriftung ab.
  Getrennte Browserprüfung: Kniffel einschließlich gemeinsamer Quellen auffindbar,
  Ergebniseintrag im gemeinsamen Kontureditor mit vier Punkten geöffnet; Symbolbutton
  mit SVG, verborgenem sichtbaren Hilfstext und erhaltenem Zugänglichkeitsnamen geprüft.
- Alle 353 geschützten Spiel-/Asset-/Bibliotheksdateien SHA-256-identisch zum Beginn;
  alle sieben persönlichen JSON-Dateien erhalten. Keine Prüfentwürfe in der persönlichen
  Ablage, keine Spiel-/Konto-/Ergebnis-/Nutzungsdaten geändert. Kein externer Serverkontakt,
  keine Veröffentlichung und keine Spieloriginale ersetzt.
- Persönliche Aktivierung auf 8776/8771 noch offen: automatische Freigabe wies das
  Neuladen dieser beiden Dienste wegen möglicher ungespeicherter Entwürfe in offenen
  Nutzertabs zurück. Aktion nicht ausgeführt und nicht umgangen. Freigabe beim Nutzer
  angefragt, nachdem die getrennte Prüfung konkret vorlag. Persönliche Prozesse 6840
  (8776) und 16500 (8771) sowie Nutzertabs unangetastet. Nicht als persönlich aktiviert
  oder dort neu sichtbar geprüft ausgeben, solange Zustimmung und Prüfung fehlen.
- Getrennter Prüfdienst auf 8777 (Prozess 14120) und eigene Prüfseite für die Freigabe
  bereitgehalten. Nachweise unter runtime/button-complete-20261026/: before.json,
  verification.json, assets-before/after.json, source-check.json, tests.log,
  ergaenzte-bibliothek.png, kniffel-editor.png und symbol-editor.png. Bekannte frühere
  MutationObserver-Meldungen der Browser-Frame-Diagnostik weiterhin ungeklärt.

## 2026-10-26 – Buttonaufnahme nach ausdrücklicher Freigabe persönlich aktiviert

- Nutzer antwortet ausdrücklich „Ja, beide Werkstätten neu laden“. Damit ist die
  zuvor wegen möglicher ungespeicherter Entwürfe zurückgewiesene Aktivierung freigegeben.
  Beide Prozesse anhand vollständiger Programm- und Portzuordnung erneut identifiziert
  und mit denselben persönlichen Ablagen neu geladen: gemeinsame Werkstatt 8776
  (neuer Prozess 3972), eigenständige Buttonwerkstatt 8771 (19088).
- Laufende persönliche Werkstatt meldet gesund, 144 Quellverwendungen / 85 Modelle,
  keine unlesbaren Bibliothekseinträge. Neuer Kniffel-Ergebniseintrag liefert auf beiden
  Diensten identisches Rezeptformat 4 mit vier Konturpunkten. Keine Prüfbibliothek
  anstelle der persönlichen Ablage eingebunden.
- Persönliche Bibliothek im Browser mit Kniffel-Filter sichtbar geprüft, einschließlich
  gemeinsamer und neu aufgenommener Einträge. Neuen Kniffel-Ergebniseintrag von dort im
  gemeinsamen Editor geöffnet und Quellname/vier Konturpunkte beobachtet. Dasselbe neue
  Element auch auf 8771 sichtbar im Kontureditor geöffnet. Keine Änderung gespeichert.
  Vorhandene Nutzertabs nicht zwangsweise neu geladen; eigene Prüfseite in die
  persönliche Bibliothek auf 8776 überführt und geöffnet gelassen.
- Alle 353 geschützten Spiel-/Asset-/Bibliotheksdateien weiterhin SHA-256-identisch;
  alle sieben persönlichen JSON-Dateien erhalten. Originalaussehen und Spielfunktionen
  nicht geändert, keine Spiel-/Konto-/Ergebnis-/Nutzungsdaten verändert. Kein externer
  Serverkontakt, keine Veröffentlichung. Getrennten eigenen Prüfdienst 8777 beendet.
- Frühere Aktivierungssperre dieses Arbeitsschritts damit aufgelöst. Nachweise unter
  runtime/button-complete-20261026/: aktualisierte verification.json, activation-http.json,
  personal-activation-library.png, personal-activation-editor.png und
  standalone-activation-editor.png. Weiter offen: persönlicher Bedienbarkeitstest und
  Entscheidungen über optisch abweichende Zusammenführungskandidaten.

## 2026-10-26 – Werkstatt: weitere Elemente vor Button-Optionsprüfung priorisiert

- Nutzer setzt die Werkstattarbeit im neuen Chat fort. Aufnahme und Anpassung
  der übrigen Elemente haben zunächst Vorrang, damit zusammenhängende Aufgaben
  mit längeren Prompts bearbeitet werden können. Eine konkrete nächste
  Elementart ist damit noch nicht festgelegt.
- Gemeinsame Prüfung und Anpassung sinnvoller Button-Editoroptionen ausdrücklich
  als spätere Aufgabe vorgemerkt. Diese Entscheidung ersetzt die frühere
  Reihenfolge, in der die Buttonprüfung vor weiteren Elementeditoren stand.
  Technische Aufnahme und Öffnung sind keine inhaltliche Abnahme der Optionen.
  Entscheidungen über optisch abweichende Zusammenführungskandidaten bleiben
  offen; Projektvorschau und vollständiger Button-Einsatzweg bleiben zurückgestellt.
- Aktuellen lokalen Buttonbericht gelesen: 144 registrierte Quellverwendungen,
  85 Modelle, keine fehlenden Verwendungen oder veralteten Aufnahmen gemeldet.
  Elementregistrierung, Werkstatt-README und maßgebliche Baukastendokumentation
  abgeglichen. Reihenfolge und spätere Aufgabe in diesen Dokumenten nachgeführt.
- Ausschließlich Dokumentation geändert. Keine Editoroptionen, Spielquellen,
  persönlichen Entwürfe oder Spieldaten verändert; keine Dienste neu geladen.
  Keine neue Sichtprüfung oder Funktionsabnahme behauptet. Das vorgeschriebene
  Server-Projektlog konnte wegen SSH-Verbindungszeitüberschreitung nicht gelesen
  werden; die Entscheidung ist nur im lokalen Arbeitsstand dokumentiert.

## 2026-10-26 – Fenster aus allen Spielen in die lokale Werkstatt aufgenommen

- Nutzer beauftragt ausdrücklich ausschließlich lokale Aufnahme von Regeldialogen,
  Entscheidungsfenstern, Inventaren und Aktionsflächen aus allen Spielen sowie die
  Zuordnung gemeinsamer Varianten. Button-Optionsprüfung bleibt für später
  vorgemerkt; ein Fenstereditor ist mit dieser Aufnahme nicht als fertig erklärt.
- source_windows.py ergänzt dieselbe Werkstatt und Projektbibliothek um 84 konkrete
  Verwendungen in 30 Modellen. Daily Quiz, Party, Perfect, Playtable, Würfeltisch,
  Kniffel, Mäxchen und Conquest sowie Profil und Shop sind zugeordnet. Alle drei
  tatsächlichen HTML-Dialogquellen im verbundenen Bestand sind erfasst. Regeln
  für Perfect und Conquest stammen aus Übersicht/Lobby, nicht deren eigenständigen
  laufenden Spielseiten. Bestehende allgemeine Regeltexte unverändert aufgenommen.
- Gemeinsame Varianten umfassen unter anderem Regeldialog, zwölf Lobbyeinstellungen,
  je vier Profil-/Shopinventare, Quizantworten und Auflösungen, Perfect-Karten,
  Einstellungszettel und Gastgeber-Aktionen, Würfelpulte sowie Conquest-Kartenhand,
  Truppenverschiebung und kompakte Zugleiste. Gruppierung verweist auf vorhandene
  Komponenten bzw. gemeinsame Grundklassen; Gestaltung, Inhalt und Zustände der
  einzelnen Verwendungen bleiben erhalten. Keine Spielkomponente nachgezeichnet.
- Vorschauen lesen Originalvorlagen/Makros und Styles mit neutralen Beispielen.
  Karten, Würfel und Kniffelblock aus tatsächlichen DOM-Fabriken als sieben
  nachprüfbare Beispielinhalte erfasst. Neues Werkzeug
  deploy/capture_generated_windows.mjs führt nur reine lokale Fabriken ohne Netz,
  Spielhandler oder Datenbank aus; Quellenprüfsummen schützen vor veralteten
  Aufnahmen. Vorschauframes sind inert, ohne Skripte/Formularaktionen. Nur die
  Gesamtplatzierung und proportionale Skalierung werden an die Werkstatt angepasst.
  Laufzeitabhängige Button-Mounts sind keine behauptete Funktion dieser Vorschau.
- Bibliothek → Fenster bietet Suche, Spielfilter, vier Fensterarten und gemeinsame
  Modellkarten mit einzeln auswählbaren Varianten. Konkrete Varianten lassen sich
  mehreren Mappen zuordnen. Projektstände und lokale Übergaben bewahren Original,
  gerendertes Beispiel, Zustand und Quellprüfsummen. Aufnahme legt keine persönlichen
  Fensterkopien oder neuen Mappen an. Native Browserbestätigungen, Alt-Conquest-
  Inventar und eigenständige andere Elementfamilien ausdrücklich abgegrenzt.
- Neue Berichte docs/FENSTER_BESTAND.md und .json über
  deploy/audit_window_coverage.py reproduzierbar; keine fehlende Dialogzuordnung.
  Allgemeinen Werkstattbestand, Baukastendokumentation und README fortgeschrieben.
  Dabei veralteten Material-Quellbeleg des Bestandswerkzeugs auf die tatsächlich
  vorhandene JSON-Schreibweise berichtigt; Bericht danach erfolgreich erneuert.
- 56 relevante Python-Prüfungen bestanden; nach Ergänzung der Aktionsleisten neun
  gezielte Fensterprüfungen erneut bestanden. JavaScript-Syntax geprüft. Erster
  unprivilegierter Testversuch durch lokale Socketrechte begrenzt; vollständige
  Prüfung mit erlaubten lokalen Testverbindungen und getrennter Ablage bestanden.
- Im getrennten Browser auf 8777 Conquest-Inventar filtern, konkrete vergrößerte
  Kartenhand auswählen, in eigene Testmappe speichern, nach Neuladen wieder öffnen
  und lokale Übergabe erzeugen tatsächlich geprüft. Übergabedatei anschließend
  unabhängig gelesen: richtige Variante samt Originalinhalt und Quellen enthalten.
  Kniffelblock sichtbar geprüft. Bei gesetztem 390-Pixel-Viewport tatsächliche
  Inhaltsbreite und Scrollbreite jeweils 375 Pixel einschließlich Scrollleiste;
  vier Filter und Bibliothek ohne horizontalen Seitenüberlauf gesehen.
- Persönlichen Werkstattdienst 8776 anhand vollständiger Programm-/Portzuordnung
  gezielt mit derselben bisherigen Ablage geladen; letzter Prozess 25164. Health
  ok, 84 Verwendungen/30 Modelle, keine unlesbaren Einträge. Alle 84 Vorschauadressen
  dort HTTP 200 mit gesperrten Skripten/Formularaktionen. Persönliche Bibliothek,
  Profilinventar und Perfect-Zettel einschließlich lesender Mitspieler-Variante
  tatsächlich im Browser gesehen. Abschlussansicht Bibliothek → Fenster geöffnet.
- Alle 353 vorab erfassten Spiel-/Asset-/Bibliotheksdateien SHA-256-identisch;
  alle sieben persönlichen JSON-Dateien erhalten. Testmappe ausschließlich unter
  runtime/window-workshop-20261026/qa-library. Keine Spiel-, Konto-, Ergebnis- oder
  Nutzungsdatenbank geöffnet, keine Spiel-/Buttondienste neu geladen, kein externer
  Serverkontakt und keine Veröffentlichung. Den getrennten Prüfdienst beendet;
  persönliche Werkstatt danach weiterhin mit Health ok erreichbar.
- Nachweise unter runtime/window-workshop-20261026/: source-before/,
  protected-before.json, verification.json, tests.log, window-tests-final.log,
  fensterbibliothek.png, perfect-varianten.png, kniffelblock.png, schmal.png und
  qa-library/handoffs/. Noch offen: Fenstereditor/Optionsprüfung; Button-Editor-
  Prüfung und optische Zusammenführungskandidaten bleiben zurückgestellt.

## 2026-10-26 – Eingaben und Auswahlfelder als nächster lokaler Werkstattbaustein

- Nutzer bittet um Fortsetzung nach Vorschlag. Als nächsten Baustein Aufnahme
  der Eingaben und Auswahlfelder angekündigt und umgesetzt. Lokaler Umfang und
  spätere gemeinsame Editor-Optionsprüfung bleiben maßgeblich; keine neue
  Gestaltungsangleichung an den tatsächlichen Spielen vorgenommen.
- Neuer Bereich Bibliothek → Eingaben: 58 Einsatzvarianten in 27 Modellen.
  Text/Zahlen, Auswahlfelder, Schalter, Regler und zusammengesetzte Auswahlen
  aus Daily Quiz, Party, Perfect, Playtable, Würfeltisch, Kniffel, Mäxchen,
  Conquest sowie Profil und Zugang aufgenommen. Alle 45 nativen bzw.
  rollenbasierten Quellkontrollen zugeordnet; Sortieren und Zuordnen zusätzlich
  als zusammenhängende Auswahlen. Versteckte Übertragungswerte ausgeschlossen.
- source_inputs.py verwendet denselben Originalquellen-/Vorschauweg wie Fenster.
  SourceWindows um konfigurierbare Elementart, Quelle, Vorschaugröße und
  Variantenregistrierung erweitert; keine zweite Grundimplementierung. Alle
  vorhandenen 84 Fensterkennungen unverändert. Originalfragmente und Styles,
  Beschriftungen, min/max/maxlength/required sowie Ein-/Aus-/Auswahlzustände je
  Variante erhalten. Neutrale Beispieldaten; PIN-Felder bleiben leer.
- Vorschauen inert und ohne Skript-/Formularaktionen. Sortieren, Validierung,
  automatisches Speichern, Authentifizierung und Spieleingaben laufen dort nicht.
  Grenzen und gesperrte Initialzustände werden als vorhanden gekennzeichnet;
  zustandsabhängige Spielgrenzen werden nicht als geprüftes Live-Verhalten ausgegeben.
- Vorhandene Bibliotheksfilter, Modellkarten, Variantenauswahl, Projektmappen und
  Übergaben erweitert. Eingabeart und Fensterart verwenden dieselbe dynamische
  Filterkomponente. Ein Modell bewahrt seine konkreten Quellen und Zustände;
  reine ähnliche Optik begründet keine Vereinheitlichung der Spiele. Die Werkstatt
  hat nun 13 Bereiche und 19 erfasste Familien; sechs weitere Familien bleiben
  als Bestandsbedarf sichtbar. Buttonvergleich zählt weiterhin ausschließlich Buttons.
- docs/EINGABEN_BESTAND.md und .json mit deploy/audit_input_coverage.py aus lokalen
  Quellen reproduzierbar; keine fehlende Zuordnung. Werkstatt-README,
  Baukastendokumentation und allgemeiner Bestandsbericht entsprechend fortgeschrieben.
- 65 relevante Python-Prüfungen einschließlich bisheriger Fenster-, Button-,
  Bild-, Speicher- und HTTP-Grenzen bestanden. JavaScript-Syntax ebenfalls geprüft.
  Keine zusätzliche Prüfung von Spielaktionen oder Spielregeln behauptet.
- Getrennter Browser auf 8777: Spielfilter Kniffel und Eingabeart Schalter,
  konkrete Variante „Kamera fixieren · Aus“, dauerhafte Zuordnung zu eigener
  Testmappe, Wiederöffnen nach Neuladen und lokale Übergabe tatsächlich geprüft.
  Übergabedatei unabhängig gelesen: genau die ausgeschaltete Variante samt
  Originalfragment und Quellprüfsummen enthalten. Bei gesetztem 390-Pixel-Viewport
  Inhaltsbreite/Scrollbreite jeweils 375 Pixel; kein horizontaler Seitenüberlauf.
- Ausschließlich persönlichen Werkstattdienst 8776 anhand vollständigem Startpfad
  und Portbesitz mit derselben bisherigen Ablage neu geladen; letzter Prozess 1996.
  Health ok, 58 Eingabevarianten/27 Modelle und 84 Fenster/30 Modelle; keine
  unlesbaren Einträge. Alle 142 Eingabe-/Fenster-Vorschauadressen dort HTTP 200
  mit gesperrten Skripten/Formularaktionen. Persönliche Eingabebibliothek,
  getrennte Quiz-/Party-Sortiervarianten und erhaltener Fensterbestand im Browser
  gesehen; Eingabebibliothek als Abschlussansicht geöffnet.
- Alle 353 vorab erfassten Spiel-/Asset-/Bibliotheksdateien SHA-256-identisch;
  alle sieben persönlichen JSON-Dateien erhalten. Testmappe ausschließlich unter
  runtime/input-workshop-20261026/qa-library. Keine Spiel-/Konto-/Ergebnis-/
  Nutzungsdatenbank geöffnet, keine Spiel- oder Buttondienste neu geladen und
  kein externer Serverkontakt bzw. keine Veröffentlichung. Getrennten Prüfdienst
  beendet; persönliche Werkstatt danach weiterhin mit Health ok erreichbar.
- Nachweise: runtime/input-workshop-20261026/source-before/,
  protected-before.json, verification.json, tests.log, schmal.png,
  reihenfolge.png, eingabebibliothek.png und qa-library/handoffs/.
  Eingabeeditor und Optionsprüfung bleiben spätere Aufgaben; dasselbe gilt für
  die zurückgestellte gemeinsame Fenster-/Button-Editorprüfung.

## 2026-10-27 – Punkte, Timer und Statusanzeigen in der lokalen Werkstatt

- Bibliothek → Anzeigen ergänzt: 210 Einsatzvarianten in 63 Modellen aus allen
  acht Spielen sowie Profil und Shop. Sechs Anzeigearten: Punkte/Werte, Timer,
  Fortschritt, Status, Zähler/Reserven und Ergebnisse. Gemeinsame Komponenten
  stehen als Modell zusammen; Spiele, Werte, Rollen und Zustände bleiben als
  konkrete Varianten erhalten. Spiel- und Anzeigeartfilter sowie Textsuche
  verwenden die vorhandenen Bibliothekskomponenten. Nun 14 Elementbereiche bei
  19 erfassten Familien; fünf weitere Familien bleiben im Bestandsbereich.
- source_indicators.py verwendet denselben Quellen-, Vorschau-, Modell- und
  Speicherweg wie Fenster/Eingaben. Originalvorlagen, Makros und Styles bleiben
  maßgeblich. Der gemeinsame Vorschauweg unterstützt eine äußere Breitenvorgabe
  für Containerkomponenten und sichtbare überstehende Porträtteile. Ganze
  Profilfenster und Conquest-Porträts behalten ihre Innenkomposition. Alle 84
  vorhandenen Fensterkennungen und alle 58 Eingabekennungen unverändert.
- Neutrale feste Beispiele auch für dynamische Anzeigen: Kniffelblock und
  Wurflichter, Wurfnotizen/-ergebnisse, Mäxchen-Leben einschließlich Schwimmen
  mit einem Leben, öffentliche Conquest-Armeewerte und Kampfwürfel aus den
  vorhandenen Darstellungsfunktionen. Quiz-Zeitpunkte aus der bestehenden
  Berechnung. deploy/capture_generated_indicators.mjs erfasst 18 Beispiele bzw.
  Berechnungsergebnisse mit Quellprüfsummen; veraltete Quellen werden abgewiesen.
  Vorschauen bleiben inert und führen keine Timer, Punktevergabe oder Spielaktionen aus.
- docs/ANZEIGEN_BESTAND.md/.json dokumentieren Quellen, Modelle, Zustände und
  Grenzen; mit deploy/audit_indicator_coverage.py reproduzierbar. Alle 34
  semantisch markierten Anzeigequellen zugeordnet oder begründet abgegrenzt;
  keine fehlende Zuordnung. Weitere sichtbare Punkte-/Status-/Zählerklassen und
  dynamische Werte zusätzlich erfasst. Dies ist keine Prüfung aller möglichen
  laufenden Spielzustände. Vorhandene Party-Ergebnisliste ausdrücklich als
  Altbestand aufgenommen; keine neue Podiumgestaltung umgesetzt oder freigegeben.
  Werkstatt-README, Baukastendokumentation und allgemeiner Bestandsbericht aktualisiert.
- 76 relevante Python-Prüfungen bestanden. Nach der abschließenden Größenkorrektur
  11 Anzeigenprüfungen und anschließend die gemeinsame Vorschauprüfung erneut
  bestanden. JavaScript-Syntax geprüft. Ein anfänglicher lokaler Verbindungsabbruch
  im Herkunftsprüfungstest trat bei gezielter Wiederholung und im Gesamtlauf
  nicht mehr auf; die Fremdherkunft wurde jeweils mit HTTP 403 abgewiesen.
- Getrennter Browserprüfbestand auf 8777: Spiel-/Anzeigeartfilter, normaler und
  dringender Perfect-Timer, exakte Zuordnung „Antwort verfassen · Dringend“ zur
  eigenen Testmappe, Neuladen und lokale Übergabe tatsächlich geprüft. Übergabe
  unabhängig gelesen: genau diese Variante mit 0:12, Dringlichkeitsklasse,
  Originalfragment und gültigen Quellprüfsummen enthalten. Vollständige Profil-
  und Conquest-Komposition sichtbar geprüft. Bei 390-Pixel-Viewport Inhalts-
  und Scrollbreite jeweils 375 Pixel; kein horizontaler Seitenüberlauf.
- Ausschließlich persönlichen Werkstattdienst 8776 anhand vollständigem Startpfad
  und Portbesitz mit bisheriger Ablage neu geladen; letzter Prozess 19616.
  Health ok, 210 Anzeigen/63 Modelle, 84 Fenster/30 Modelle, 58 Eingaben/27 Modelle;
  keine unlesbaren Einträge. Alle 352 Vorschauadressen dort HTTP 200 mit
  gesperrten Skripten/Formularaktionen und inertem Inhalt. Persönliche
  Anzeigenbibliothek mit tatsächlichen Vorschauen im Browser gesehen und als
  Abschlussansicht geöffnet. Abschließende Vorschauplatzkorrektur ebenfalls geladen.
- Alle 353 vorab erfassten Spiel-/Asset-/Bibliotheksdateien SHA-256-identisch;
  alle sieben persönlichen JSON-Dateien erhalten. Testmappe ausschließlich unter
  runtime/indicator-workshop-20261027/qa-library. Keine Spiel-/Konto-/Ergebnis-/
  Nutzungsdatenbank geöffnet, keine Spiel- oder Buttondienste neu geladen und
  kein externer Serverkontakt bzw. keine Veröffentlichung. Getrennten Prüfdienst
  beendet; persönliche Werkstatt danach weiterhin mit Health ok erreichbar.
- Nachweise: runtime/indicator-workshop-20261027/source-before/,
  protected-before.json, verification.json, personal-http.json, tests-final.log,
  tests-indicators-final.log, schmal.png, conquest-werte.png,
  anzeigenbibliothek.png und qa-library/handoffs/.
  Anzeigeneditor und Optionsprüfung bleiben spätere Aufgaben; ebenso die
  zurückgestellte gemeinsame Fenster-/Eingabe-/Button-Editorprüfung.

## 2026-10-27 – Spieleranzeigen und Pulte in der lokalen Werkstatt

- Neuer Bereich Bibliothek → Spieleranzeigen & Pulte: 146 Varianten in 13 Modellen
  aus allen acht Spielen sowie Profil und Shop. Profilfenster, Lobbyplätze,
  kompakte Porträts, Ranglisten/Ergebnisse, Namenspulte und Pultmotive nach Spiel
  und Baustein filterbar. Rollen und Zustände bleiben konkrete Varianten;
  mehrere Projektmappen können dieselbe Variante ohne Elementkopien verwenden.
  Nun 15 Elementbereiche bei 19 erfassten Familien; vier weitere im Bestandsbereich.
- source_players.py verwendet den gemeinsamen Quellen-, Vorschau- und Speicherweg
  von Fenstern/Eingaben/Anzeigen. Originale aus _profile_window.html,
  _lobby_room.html, _player_identity.html und den vorhandenen Spielrahmen;
  keine neue Innenkomposition. Alle 14 Pultfamilien als vollständiges Profilfenster
  und als vorhandene Profilauswahl erfasst; Shop mit seinen 13 angebotenen Motiven.
  Reine Namenspulte am laufenden Kartentisch beibehalten. Keine zusätzlichen
  Avatare in Quizfragen oder Countdowns eingebaut. Party-Ergebnispulte ausdrücklich
  als Altbestand aufgenommen; damit keine neue Podiumgestaltung freigegeben.
- Conquest-Armee- und Siegerporträts stammen aus derselben Originalfabrik
  createPlayerPortrait. deploy/capture_generated_players.mjs erfasst 27 neutrale
  Fabrikbeispiele. Die bestehenden register_portraits/public_portrait-Funktionen
  liefern die Ausschnitte aller 19 registrierten Avatare in einem neutralen
  Funktionskontext ohne Anwendungs-/Datenbankstart. Eigener Startavatar und
  öffentliche Variante getrennt; Test- und neutrale Armeen mit vorhandener
  Buchstabendarstellung. Öffentliche Werte, Kartenanzahl, eigener Kartenknopf,
  aktiver Platz, ausgeschiedene Armee und Siegerdarstellung einzeln zugeordnet.
- Vorhandene Profilfenster-, Perfect-, Würfel- und Lobbyrollen erhalten.
  Bereit/Antwort steht/Gewählt sowie Wartende getrennt; Mäxchen-Leben/Zugzustände
  aus der bereits erfassten Originaldarstellung. Würfelaktionspulte und
  Kniffel-Spielerwertung verwenden dieselben Quellen wie ihre bisherigen Familien.
  Bilddateien der konkreten Spielerbeispiele zusätzlich per Prüfsumme gebunden.
  Vorschauen inert; keine Ausrüstungswechsel, automatische Textanpassung oder
  Spielaktionen ausgeführt. Kleine Beispielrahmen sind keine Optionsabnahme.
- Gemeinsame Fragmentauswahl um einen gezielten Quellvorkommensindex erweitert,
  damit Startseiten- und Ergebnisrangliste ihre tatsächlichen Quellzweige erhalten.
  Alle 84 bisherigen Fenster-, 58 Eingabe- und 210 Anzeigenkennungen unverändert.
  Spielerbibliothek nutzt dieselben Modellkarten, Variantenfilter und Projektwege.
  docs/SPIELER_BESTAND.md/.json über deploy/audit_player_coverage.py reproduzierbar:
  alle 14 verbundenen Makroaufrufe und sieben Spieler-/Pultquellstellen zugeordnet,
  keine fehlende Zuordnung. README, Baukastendokumentation und allgemeiner
  Bestandsbericht fortgeschrieben.
- 85 relevante Python-Prüfungen bestanden. Sichtprüfung deckte einen zu weit
  gefassten Perfect-Selektor auf: einzelnes Spielerfenster und Spielrahmen teilen
  dieselbe Mitgliedskennung. Selektor auf die Spielerkomponente begrenzt; danach
  alle neun Spielerprüfungen erneut bestanden, einschließlich genau eines
  Profilfensters pro Perfect-Beispiel. JavaScript-Syntax ebenfalls bestanden.
- Getrennte Browserprüfung auf 8777: Spiel-/Bausteinfilter, Kea-Porträt mit dem
  bestehenden Ausschnitt, Neonglas-Pultmotiv, fremdes Namenspult bei sechs Plätzen,
  vollständiges Profilfenster und korrigierter Perfect-Spielerplatz sichtbar
  geprüft. Eigene Testmappe mit genau der Kea-Variante gespeichert, nach Neuladen
  wieder geöffnet und lokal übergeben. Übergabedatei unabhängig gelesen:
  gewählte Variante mit Skalierung 1,7/oberem Ausschnitt -48 und gültigen Quellen.
  Bei 390-Pixel-Viewport Inhalts-/Scrollbreite jeweils 375 Pixel; kein seitlicher
  Seitenüberlauf. Testmappe ausschließlich unter runtime/player-workshop-20261027/qa-library.
- Nur persönlichen Werkstattdienst 8776 nach exakter Programm-/Portprüfung mit
  bisheriger Ablage neu geladen; letzter Prozess 22540. Health ok, 146 Spieler-
  varianten/13 Modelle und 352 vorhandene Fenster-/Eingabe-/Anzeigenvarianten;
  alle 498 Vorschauadressen HTTP 200 mit gesperrten Skripten/Formularaktionen und
  inertem Inhalt. Keine unlesbaren Einträge, bestehende persönliche Projektmappe
  erhalten. Persönliche Spielerbibliothek im Browser gesehen und geöffnet gelassen.
- Alle 353 vorab erfassten Spiel-/Asset-/Bibliotheksdateien SHA-256-identisch;
  alle sieben persönlichen JSON-Dateien erhalten. Keine Spiel-/Konto-/Ergebnis-/
  Nutzungsdatenbank geöffnet, keine Spiel- oder Buttondienste neu geladen,
  kein externer Serverkontakt und keine Veröffentlichung. Getrennten Prüfdienst
  beendet; persönliche Werkstatt danach weiterhin mit Health ok erreichbar.
- Nachweise unter runtime/player-workshop-20261027/: source-before/,
  protected-before.json, verification.json, tests-final.log, tests-players-final.log,
  portraet.png, pultmotiv.png, namenspult.png, perfect-spielerfenster.png,
  schmal.png, spielerbibliothek.png und qa-library/handoffs/.
  Spielereditor und gemeinsame Optionsprüfung bleiben wie beauftragt spätere Arbeit.

## 2026-10-27 – Lobbys und Lobbyübersichten in der lokalen Werkstatt

- Bibliothek → Lobbys & Übersichten um 134 Quellvarianten in sieben Modellen
  ergänzt. Alle sieben Mehrspielerspiele enthalten: Party, Playtable, Würfeltisch,
  Kniffel, Mäxchen, Perfect und Conquest. Ganze Übersichten, Zeilen, Listenheader,
  Leer-/Fehlerzustände, Standardräume und Perfect-Raum getrennt gruppiert. Das
  Daily Quiz hat keine Mehrspielerlobby; Startseite und Spielerbausteine bleiben
  ihren bisherigen Elementarten zugeordnet.
- source_lobbies.py verwendet denselben Originalquellen-, Vorschau-, Modell- und
  Speicherweg wie die bisherigen Aufnahmen. Gemeinsame Übersicht aus
  _lobby_overview.html und sechs Standardräume aus _lobby_room.html. Perfect
  behält seinen vorhandenen Raum mit Zettel, Buzzer, Spielerwänden und Hintergrund;
  keine Spielkomponente oder Innenkomposition nachgezeichnet oder vereinheitlicht.
  Host-/Mitspielerrollen, allein/volle Besetzung, Punkte-/Zeitspiel, Bereitschaft
  und fester Start-Countdown bleiben konkrete Varianten. Conquest zusätzlich mit
  reserviertem Platz, Rückkehr, laufender/beendeter Partie und geschlossenem Raum.
- Lobbyzeilen bewahren Beitritt, volle fremde Lobby ohne Beitrittsaktion, eigene
  wartende/laufende Runde und Ergebniszugang. Conquest-Rückkehr separat; Fehler-
  beispiele behalten die zuletzt geladene neutrale Liste sichtbar. Keine Prüfung
  tatsächlicher Spielübergänge oder aller möglichen Live-Zustände behauptet.
  Erstellen/Beitreten/Start/Bereitschaft/Autospeichern/Polling laufen nicht in
  den inerten Vorschauen. Keine echten Konten, Mitgliedschaften oder Partien gelesen.
- Gemeinsamer Vorschauweg um optionalen Erhalt des Quellhintergrunds und der
  ursprünglichen Überlaufbegrenzung erweitert. Ganze Räume übernehmen den
  ursprünglichen neutral gerenderten Hintergrundkontext. Äußerer Vorschauplatz
  für vollständige Listen/Conquest-Räume vergrößert; kein Abschneiden durch eine
  zusätzliche innere Werkstatt-Scrollfläche. Die gesamte Komposition skaliert
  proportional. Bestehende Profilgrafiken und automatische Textanpassung bleiben
  unverändert; die Textanpassung läuft in diesen inerten Beispielen nicht.
- Bisheriger allgemeiner Lobbyentwurf und sein Editor erhalten. Daher insgesamt
  acht Modelle/135 Varianten unter „Alle“; „Im Spiel verwendet“ zeigt die sieben
  Quellmodelle/134 Varianten. Vorlagen und Spielquellen verwenden weiterhin ihre
  jeweiligen vorhandenen Vorschauwege. Es bleiben 15 Elementbereiche und 19
  Bestandsfamilien. Neue Spielquellen nicht als editierbar ausgegeben; gemeinsame
  Prüfung und Anpassung sinnvoller Editoroptionen weiter ausdrücklich offen.
- docs/LOBBYS_BESTAND.md/.json über deploy/audit_lobby_coverage.py reproduzierbar:
  alle zehn verbundenen Makro-/Raumquellen zugeordnet, keine fehlende Zuordnung.
  Werkstatt-README, Baukastendokumentation und allgemeiner Bestandsbericht
  fortgeschrieben. Alle bisherigen 84 Fenster-, 58 Eingabe-, 210 Anzeigen- und
  146 Spielerkennungen unverändert.
- 94 relevante Python-Werkstattprüfungen bestanden; nach der letzten Anpassung
  des Vorschauplatzes und Erhalt der ursprünglichen Überlaufbegrenzung alle neun
  Lobbyprüfungen erneut bestanden. JavaScript-Syntax geprüft. Der erste gezielte
  Lauf zeigte nur einen zu eng formulierten Testvergleich der Wurzelklasse;
  Prüfung auf die tatsächliche gemeinsame Quellklasse samt Vorschaukennung korrigiert.
- Getrennter Browser auf 8777: Spiel-/Lobbyartfilter, Conquest-Rückkehrzeile,
  Speicherung in eigener Testmappe, Wiederöffnen nach Neuladen und lokale Übergabe
  tatsächlich geprüft. Übergabe unabhängig gelesen: genau „Reservierter Platz ·
  zurückkehren“ samt Originalfragment und gültigen Quellprüfsummen enthalten.
  Vollständige Conquest-Übersicht und voller Raum sichtbar geprüft; nach Erweiterung
  Wurzel-Inhalts-/Scrollhöhe jeweils gleich (Übersicht 1661, voller Raum 1664 Pixel).
  Perfect-Raum mit sieben Profilfenstern, geladenen Originalbildern, Zettel und
  Buzzer gesehen. Vorhandenen allgemeinen Lobbyentwurf sichtbar geöffnet.
  Bei 390-Pixel-Viewport tatsächliche Inhalts-/Scrollbreite jeweils 375 Pixel;
  kein seitlicher Überlauf der Bibliothek.
- Ausschließlich persönliche Werkstatt 8776 nach exakter Programm-/Portprüfung
  mit bisheriger Ablage neu geladen; letzter Prozess 13968. Health ok, 134 neue
  Lobbyquellvarianten und 498 bisherige Quellvarianten, keine unlesbaren Einträge.
  Alle 632 Quellvorschauadressen HTTP 200 mit inertem Inhalt und gesperrten
  Skripten/Formularaktionen. Persönliche Bibliothek im Browser gesehen und als
  Abschlussansicht geöffnet. Bestehende persönliche Projektmappe erhalten.
- Alle 353 vorab erfassten Spiel-/Asset-/Bibliotheksdateien SHA-256-identisch;
  alle sieben persönlichen JSON-Dateien erhalten. Testmappe ausschließlich unter
  runtime/lobby-workshop-20261027/qa-library. Keine Spiel-/Konto-/Ergebnis-/
  Nutzungsdatenbank geöffnet, keine Spiel- oder Buttondienste neu geladen,
  kein externer Serverkontakt und keine Veröffentlichung. Eigenen Prüfdienst
  beendet; persönliche Werkstatt danach weiterhin mit Health ok erreichbar.
- Nachweise unter runtime/lobby-workshop-20261027/: source-before/,
  protected-before.json, verification.json, tests-final.log, tests-lobbies-final.log,
  rueckkehr.png, uebersicht.png, standardraum.png, perfect-raum.png,
  bisherige-vorlage.png, schmal.png, lobbybibliothek.png und qa-library/handoffs/.

## 2026-10-27 – Karten, Würfel und Bretter vor weiterer Aufnahme abstimmen

- Nutzer verlangt insbesondere vor der Karten-/Würfelaufnahme eine gemeinsame
  Abstimmung. Als Grundrichtung nennt er bewegliche bzw. anfassbare Spielobjekte
  und reine Anzeigebausteine; Conquest-Karten als Beispiel der zweiten Verwendung.
  Das bereits heruntergeladene Kartenmodell soll als Grundlage dienen und in den
  Editor aufgenommen werden. Kein neues Modell oder fremder Ersatz ausgewählt.
- Konkreter Kartenmodellimport im geprüften lokalen Guesstimate-Bestand noch
  nicht eindeutig identifiziert. Aktiver Kartentisch verwendet die vorhandene
  DOM-/CSS-Kartenkomponente; models.js erzeugt die bisherige parametrische
  Werkstattkarte aus Projektcode. Suche einschließlich ignorierter Projektdateien
  fand die vorhandenen dddice-Modelle d6.fbx/d2.fbx, aber kein separates Karten-
  GLB/GLTF/OBJ/FBX/Blend-Modell. Im geprüften DiceyTable-Export im Downloadordner
  sind beide Assetlisten leer. Das schließt einen Download an anderer Stelle
  nicht aus. Nutzer nach Name, Dateiname oder Speicherort gefragt.
- Nutzer möchte Bretter ebenfalls mit gemeinsamem Grundaufbau und Varianten für
  Größe, Form und Bild behandeln; 2D/3D sowie Einordnung von 2,5D werden besprochen.
  Figuren sollen wegen ihrer unterschiedlichen Formen gesondert abgestimmt werden.
  Noch keine Modell-, Editor-, Kamera- oder Spiellogikänderung vorgenommen.
- Klänge und Schriften sollen ausdrücklich neu recherchiert und die Auswahl
  verbessert werden. Bisherige Auswahl gilt damit als vorläufig; neue Recherche
  und Auswahl in diesem Gesprächsschritt noch nicht ausgeführt. Bestehende
  Schrift-/Klangdateien und Nutzungen bleiben erhalten.
- Ausschließlich lokale Quellen gelesen und diese Präzisierung protokolliert;
  keine Dienste neu geladen, keine Entwürfe/Spieldaten verändert, kein Upload
  oder externer Serverkontakt.

## 2026-10-27 – Getrennter kostenloser Kartenvergleich und Werkzeugquellen

- Nutzer beauftragt einen lokalen Vergleich von bisherigen Karten, grafisch
  verbesserter Variante und einem passenden kostenlosen 3D-Modell sowie die
  Recherche weiterer Quellen und Hilfsmittel. Bestehende Spiele bleiben
  unverändert; weder Editorintegration noch endgültige Modell-/Stilauswahl.
- Eigene Vorschau offline-preview/card-comparison-v1/ auf 127.0.0.1:8778.
  Die erste Spalte liest die Original-CSS und die cardElement-Fabrik unmittelbar
  aus static/card-table.css/.js. Nur neutraler Eingabeadapter für Bewegung und
  Wenden; keine Originaldatei verändert, kein Spiel-/Datenbankstart.
- Zweite Spalte verwendet kostenlose CC0-Kartengrafiken von Kenney,
  https://kenney.nl/assets/boardgame-pack. Original-Lizenz lokal beigelegt.
  PNG-Karten 140 × 190 Pixel: für übliche Vergleichsgröße geeignet, noch keine
  endgültige hochauflösende Grafikaufbereitung. Optionale Vektoren im Archiv.
- Dritte Spalte verwendet tatsächlich importierte Kartengeometrie aus dem
  kostenlosen CC0-Poker-Pack von mehrasaur:
  https://opengameart.org/content/poker-pack. Autorenseite mit CC0-Angabe geprüft;
  Originale card.obj/card.mtl/card.blend erhalten, keine darin enthaltene Software
  ausgeführt. Achsen ausgerichtet, zentriert, einheitlich skaliert, konvexe
  Flächen trianguliert und planare Vorder-/Rückseiten-UVs ergänzt. Ursprünglicher
  abgerundeter Umriss und Dicke erhalten: 24 Quellpunkte, 44 Dreiecke, bei Höhe
  192 Breite 137,454 und Dicke 1,094. Dieselben Kenney-Grafiken wie Spalte zwei.
  Keine eigene Ersatz-Box als fremden Import ausgegeben. Quellen, Anpassungen
  und Archivprüfsummen in assets/import-manifest.json/provenance.txt dokumentiert.
- Gemeinsame Beispiele, Blickwinkel und Vergrößerung; Einzelkarte, Fünferhand,
  Zwölferstapel und vollständiges 52er-Deck. Bewegung mit Maus/Touch-Eingabeweg
  oder Pfeiltasten, Wenden per Doppelklick/Rechtsklick/Leertaste. Positionen beim
  Kippen/Zoomen erhalten, Zurücksetzen stellt Beispiele wieder her. Alle Zustände
  ausschließlich im Arbeitsspeicher. Keine Biegeverformung, Kartenphysik oder
  Anbindung vorhandener Mehrspieler-/Misch-/Austeilfunktionen behauptet.
- Bestehendes lokales Three.js r180 samt MIT-Lizenz wiederverwendet. Separater
  Vergleichsserver nur lesend, an Loopback gebunden, Dateien begrenzt und externe
  Laufzeitaufrufe per CSP ausgeschlossen. Persönliche Werkstatt 8776 und andere
  Spiel-/Buttondienste nicht neu geladen. Kein Kauf, kein Login und kein Upload.
  Öffentliche Recherche und zwei kostenlose Assetdownloads ausdrücklich Teil
  dieses Auftrags; kein Kontakt zum Projektserver.
- Weitere Primärquellen geprüft und unter dem Vergleich sowie in dessen README
  gesammelt: Kenney, OpenGameArt, Quaternius, Poly Haven, ambientCG, Blender,
  Inkscape, GIMP, Material Maker, glTF Transform, Khronos glTF Validator,
  Kenney Casino Audio, Freesound, Audacity und Google Fonts. KayKit-Karten als
  kostenpflichtiger Extra-Inhalt erkannt und ausgeschlossen. Keine zusätzlichen
  Programme installiert. Neue Klang-/Schriftauswahl und Hör-/Lesbarkeitsabnahme
  bleiben offen; bloße Quellenrecherche ist keine fertige Auswahl.
- Sichtbar geprüft: alle drei Ansichten vollständig geladen, Vorder-/Rückseiten,
  gekippter Stapel, vollständige 52er-Decks; Tastaturbewegung und Wenden in allen
  drei Varianten, Mausbewegung in allen drei, Rechtsklick im 3D-Fenster und
  Doppelklick in der Grafikansicht. Nach Blickwinkeländerung verschobene Position
  erhalten. Bei 390 Pixeln tatsächliche Inhalts-/Scrollbreite jeweils 375 Pixel;
  alle drei Vorschaurahmen 341 × 330 Pixel. Normale Ansicht wiederhergestellt.
- HTTP-Prüfung von 90 Vergleichsressourcen erfolgreich; unzulässige
  Dateipfade und Schreibanfragen abgewiesen. JavaScript-Syntax und Python-Dateien
  geprüft. Alle 353 vorab erfassten bestehenden Spiel-/Asset-/Bibliotheksdateien
  einschließlich sieben persönlicher JSON-Dateien SHA-256-identisch.
- Nachweise: runtime/card-comparison-20261027/ mit Originalarchiven,
  protected-before.json, http-verification.json, interactions.json, narrow.json,
  stapel.png, ganzes-deck.png, schmal.png und vergleich.png. Separater Dienst
  bleibt für die Nutzerprüfung geöffnet; Modellentscheidung und Editoroptionen
  weiterhin offen.
- Vergleich und persönliche Werkstatt zum Abschluss jeweils mit Health ok
  erreichbar. Browserkonsole meldete beim Neuladen zusätzlich MutationObserver-
  Fehler ohne Quelladresse; im Vergleichscode und den beiden eingebundenen
  Three.js-Dateien keine entsprechende Quellstelle. Ursache nicht zugeordnet;
  die beschriebenen sichtbaren Bedienprüfungen waren erfolgreich. Keine pauschal
  fehlerfreie Browserkonsole behauptet.

## 2026-10-27 – Freigegebene 3D- und Anzeigekarten in der lokalen Werkstatt

- Nutzer wählt den importierten 3D-Kartenkörper für bewegliche Karten und die
  grafisch verbesserte flache Variante für Anzeige-/Auswahlkarten. Beide als
  gemeinsame Grundmodelle in Bibliothek → Karten aufgenommen. Je 68 Varianten:
  52 Spielkarten, ein Joker und 15 Rückseiten in Blau/Grün/Rot. Zusammen 136 neue
  Varianten; die beiden bisherigen allgemeinen Vorlagen „Eigene Spielkarte“ und
  „Ereigniskarte“ bleiben erhalten. Persönlich nun vier Modelle/138 Varianten.
- card_library.py registriert die Grundlagen als freigegebene Vorlagen, nicht
  als bereits im Spiel eingesetzt. Kartentypfilter, Suche, Modellgruppen,
  Variantenwahl, Projektzuordnung und Übergabe über die vorhandenen gemeinsamen
  Bibliothekswege. Keine persönlichen Kartenkopien oder Mappen bei der Aufnahme
  angelegt. Derselbe Baustein kann in mehreren Projekten verwendet werden.
- Vorschau und Assets unmittelbar aus dem vorhandenen lokalen Kartenvergleich
  wiederverwendet; keine Kopie der Grafik, Geometrie oder Innenkomposition.
  Gemeinsamer Renderer unterstützt feste Anfangsvarianten und ein getrenntes
  Vorschauverhalten: 3D verschiebbar/wendbar, flach auswählbar ohne Verschieben,
  kleine Bibliotheksvorschauen ohne Eingabe. Joker und alle 15 Rückseitenmotive
  unterstützt. Große Vorschau proportional an verfügbare Höhe/Breite angepasst.
  Vergleich bleibt mit seinen bisherigen drei Spalten nutzbar.
- Gespeicherte Varianten enthalten Modell-/2D-/3D-Zuordnung, Kartenwert,
  Rückseitenmotiv, ursprüngliche Geometrieangaben, CC0-Herkunft und Quellen-
  prüfsummen. Veränderte Quellen werden in Vorschauen abgewiesen. Eingaben in
  diesen Vorschauen ändern nur flüchtige Beispielzustände und keine Spiele.
  Neue Modelle erhalten keinen irreführenden Zugang zum alten generischen
  Karteneditor. Bisheriger Editor und alte Entwürfe bleiben weiterhin verfügbar;
  Editoroptionen der neuen Grundlagen wie beauftragt später gemeinsam prüfen.
- docs/KARTEN_GRUNDLAGEN.md/.json mit deploy/audit_card_library.py reproduzierbar;
  Werkstatt-README, BAUKASTEN.md und allgemeine Bestandsberichte aktualisiert.
  Dies ist ausdrücklich keine vollständige Inhaltsaufnahme aller Spielkarten.
  Conquest-Länder-/Belohnungskarten und Perfect-Begriffs-/Kuriositätenkarten
  benötigen später ihre eigenen Inhalte und die passende Anbindung. Sie werden
  nicht zu Pokerkarten umgedeutet; bestehende Spiele behalten ihre Darstellung.
- 22 relevante Python-Prüfungen bestanden, einschließlich Quellenänderung,
  lokaler HTTP-Grenze, exakter Auswahl, Wiederverwendung und Übergabe; JavaScript-
  Syntax und Python-Dateien geprüft. Sichtprüfung fand einen Zeichensatzfehler
  in der bearbeiteten Werkstattdatei und eine zu weit gefasste Vorschauauswahl
  für alte Kartenvorlagen. UTF-8 wiederhergestellt und Legacy-Vorschau gezielt
  zurück an den bisherigen Renderer gebunden; Ereigniskarte danach mit Vorder-
  und Rückseite sichtbar geprüft. Neue Editoroptionen damit nicht abgenommen.
- Getrennte Browserprüfung auf 8777: Modell-/Kartentypfilter und Jokersuche,
  3D-Rückseite Grün 4 mit Mausbewegung und Tastaturwenden, flacher Joker mit
  Tastaturauswahl und unveränderter Position bei Pfeiltaste. Beide Varianten in
  „Kartenprüfung · getrennte Testmappe“ gespeichert, Seite neu geladen und beide
  Varianten aus der Mappe erneut sichtbar geöffnet. Lokale Übergabe unabhängig
  gelesen: genau cards-movable-green4 (3D, Grün 4, Rückseite) und
  cards-display-joker (2D, Joker). Testdaten nur unter runtime/card-library-20261027/qa-library.
  Bei 390 Pixeln tatsächliche Inhalts-/Scrollbreite jeweils 375 Pixel.
- Nur persönliche Werkstatt 8776 nach vollständiger Programm-/Portprüfung mit
  ihren bisherigen Startparametern und derselben persönlichen Ablage neu geladen;
  neuer Prozess 25808. Health ok, 136 neue Kartenvorschauen HTTP 200, keine
  unlesbaren Datensätze. Alle bisherigen 144 Buttons, 84 Fenster, 58 Eingaben,
  210 Anzeigen, 146 Spieler- und 134 Lobbyvarianten weiter registriert.
  Persönliche Kartenbibliothek mit geladenen neuen Vorschaubildern sichtbar
  geöffnet gelassen. Getrennten Prüfdienst beendet; persönliche Health danach ok.
- Alle 428 geschützten Bestandsdateien SHA-256-identisch: vorherige 353 Spiel-/
  Asset-/Bibliotheksdateien einschließlich sieben persönlicher JSON-Dateien sowie
  die 75 Kartenvergleichs-Assetdateien. Bestehende persönliche Mappe erhalten.
  Keine Spiel-/Konto-/Ergebnis-/Nutzungsdatenbank geöffnet, keine Spiel- oder
  Buttondienste neu geladen, keine neuen Downloads, kein externer Serverkontakt
  und keine Veröffentlichung.
- Nachweise unter runtime/card-library-20261027/: source-before/,
  protected-before.json, tests.log, verification.json, 3d-rueckseite.png,
  flache-auswahl.png, bisherige-ereigniskarte.png, narrow.json, schmal.png,
  kartenbibliothek.png sowie qa-library/handoffs/handoff-b3504fc2d27045298e19bffe72f4efc1.json.

## 27.10.2026 – Lokale Korrektur der Werkstattlogik: Bausteine, Sätze und Fragendaten

- Nutzerpräzisierung umgesetzt: Fragen nach Steckbrief sind wachsende Datenbestände an Fenstern. Die versuchte Registrierung von 513 einzelnen Perfect-Fragen als Karten ist aus dem aktiven Katalog und dem Kartenrenderer entfernt. Keine Fragenbank wurde dafür geändert.
- Die frühere Aufnahme einzelner Spielkarten wird durch zwei Grundbausteine und zwölf ganze Satzvarianten ersetzt: fünf französische Deckkonfigurationen (32/52/55/104/110) jeweils in 3D und flach, dazu zwei flache Conquest-Sätze. Conquest enthält 42 Länder, zwei vorhandene Joker als Ergänzung und zwölf Aufträge. Mitglieder werden innerhalb des Satzes durchgeblättert; gespeichert wird der ganze Satz. Alte persönliche Einzelkartenauswahlen bleiben lesbar; persönliche JSON-Dateien werden nicht migriert.
- Perfect-Fragen-/Abstimmungs-/Auflösungsfenster sowie Quiz-Antwortflächen und Auflösungen erhalten Datenquellen- und Feldverträge. 21 bestehende Fensterbeispiele sind verknüpft; keine Einzel-Frage-IDs oder vollständigen Fragenbanken werden in die Bibliothek übernommen. Quellen- und Modellkennungen der bestehenden UI-Bausteine bleiben stabil.
- Alle 15 bisherigen Elementbereiche und vier zusätzlich inventarisierten Familien auf dieselbe Inhaltsverwechslung geprüft. Kein weiterer entsprechender Fehler gefunden: die sechs Quellbibliotheken verwenden begrenzte Einsatz-/Zustandsbeispiele, keine realen Konten, Lobbys, Punktestandhistorien oder wachsenden Inhaltsdatensätze. Die Aufnahme sämtlicher Spielelemente ist damit ausdrücklich noch nicht abgeschlossen. Bretter, Figuren, Würfel, Titel/Icons/Flyer und gemeinsame Materialaufbereitung bleiben teilweise offen; Klänge/Schriften brauchen weiterhin die gewünschte neue Recherche.
- Prüfübersicht: docs/WERKSTATT_LOGIKPRUEFUNG.md und .json. Aktuelle Kartendokumentation sowie Bestandsübersicht korrigiert. Automatische Katalogprüfung weist erzeugte Einzelfragen zurück; eigene Entwürfe sind von dieser Anreicherung und Sperre ausgenommen.
- Prüfungen: 16 gezielte Tests (Karten, Inhalte/Datenbindung, Projektmappen) bestanden, 86,458 Sekunden. Einschließlich simulierter Erweiterung um 2.000 Fragen ohne Katalogwachstum, stabiler Quellkennungen, vollständiger Sätze, Wiederverwendung/Laden/Übergabe und lokaler HTTP-Grenzen. JavaScript-Syntax geprüft. Beleg: runtime/workshop-audit-20261027/tests.txt.
- Browserprüfung: Conquest-Länder im Satz gewechselt, 12 Aufträge und französischer 55er-Satz mit Joker visualisiert; Perfect-Fragenfenster mit neutraler Beispielfrage und Datenquellen geprüft. Getrennte Prüfmappe mit genau zwei Elementen (ganzer Ländersatz + Fragenfenster) gespeichert, neu geöffnet und lokal übergeben; Übergabe enthält 42 Länder + zwei Joker sowie Quellenverweise statt Perfect-Fragenkopien. Langer Auftrag vollständig sichtbar (Inhaltshöhe 215/215 px).
- Persönliche Werkstatt auf 127.0.0.1:8776 mit unveränderten Startoptionen neu geladen und korrigierten Satz im Browser geprüft. Kein Speichern von Testentwürfen in design-library. Prüfsummenvergleich: 448 geschützte Dateien unverändert, darunter sämtliche erfassten Fragen-JSONs und alle sieben persönlichen JSON-Dateien. Prüfungen liefen in separaten runtime-Verzeichnissen. Kein Serverkontakt, keine Veröffentlichung oder Umstellung bestehender Spiele. Editoroptionen bleiben offen.
## 27.10.2026 – Genau zwei Würfelvarianten in der lokalen Werkstatt

- Nutzer legt genau zwei vorhandene Varianten fest: räumliche Würfel mit Physik vom Würfeltisch und flache Würfelanzeigen aus Conquest. Anzahl, Seitenaufdrucke und Farben sind Eigenschaften dieser Varianten; keine zusätzlichen Bausteine je Wurf, Augenzahl oder Gruppengröße. Weitere Würfelmodelle werden nicht ergänzt.
- Bibliothek → Würfel enthält zwei neue gemeinsame Quellbausteine. Die bisherigen zwei generischen Musterwürfel werden nicht mehr als neue Standardauswahl angeboten. Vorhandene persönliche Entwürfe und gespeicherte ältere Mappen bleiben unverändert lesbar; der alte Renderer bleibt dafür verfügbar. Die vollständigen Editoroptionen werden weiterhin später geprüft.
- Räumliche Vorschau verwendet die bestehenden Funktionen localizeThemeAssets/createEngine/ensureEngine/animateRoll aus static/dice-table.js sowie das vorhandene lokale dddice-SDK, d6-Modell und Theme. Flache Vorschau verwendet unverändert Conquests showRolls aus attack.js und die ursprünglichen battle-die-Regeln. Keine Spielquelle umgeschrieben, kein neuer Würfelkörper und keine neue Physikimplementierung erzeugt. Adapter betreiben ausschließlich neutrale Vorschauwerte, keine Spielhandler, Konten, Statusabfragen oder Datenbanken. Themeressourcen bleiben lokal; Vorschauverbindungen auf eigenen Ursprung begrenzt.
- Bausteinschnappschüsse enthalten Eigenschaften und Herkunftsprüfsummen. Die Aufnahme wächst nicht mit gewürfelten Ergebnissen. Dokumentiert in docs/WUERFEL_GRUNDLAGEN.md; Bestands- und Logikprüfung auf die zwei vorhandenen Varianten aktualisiert.
- Zwölf gezielte Tests (vier Würfelprüfungen und acht Projektmappenprüfungen) bestanden, 76,034 Sekunden. Direkte Verwendung der Originalfabriken, Quelländerungserkennung, lokale Routen, unveränderte alte Mappenschnappschüsse, Wiederverwendung/Laden/Übergabe und genau zwei neue Würfeleinträge geprüft. JavaScript-Syntax beider Vorschau-/Werkstattdateien geprüft.
- Beide Varianten in einer getrennten Browser-Prüfmappe gesammelt, nach Neuladen mit genau zwei Elementen wieder geöffnet und lokal übergeben. Persönliche Werkstatt 127.0.0.1:8776 mit denselben Startoptionen neu geladen. Dort beide Varianten sichtbar geprüft; Wurfprobe mit geänderten Werten ausgeführt, flache Originalanzeige mit 2/5 kontrolliert. Screenshots: runtime/dice-library-20261027/dice-library.png, physics.png und flat.png. Prüfdaten ausschließlich im getrennten runtime-Verzeichnis.
- Abschließender Schutzvergleich: 478 Dateien SHA-256-identisch, einschließlich Spiel-Pythondateien, Fragenbeständen, ursprünglichen Würfel-/Theme-/Modell-/Rendererdateien und sieben persönlichen JSON-Dateien. Keine zusätzlichen persönlichen Dateien. Kein Projektserverkontakt, keine Veröffentlichung und keine Umstellung bestehender Spiele.
- Für die weitere Aufnahme bleiben insbesondere tatsächliche Bretter, Figuren und weitere Bild-/Symbolbestände sowie die gewünschte neue Klang-/Schriftrecherche offen. Material-/Darstellungsoptionen und sämtliche abschließenden Editortests bleiben späteren Schritten vorbehalten.
## 27.10.2026 – Bretter und Spielflächen als 2D-/3D-Grundvarianten (nur lokal)

- Nutzerauftrag umgesetzt: zwei Brettgrundvarianten 2D und 3D. Größe, Form und Bild sind Eigenschaften, keine zusätzlichen Grundmodelle. 2,5D wird als schräge Ansicht der räumlichen Variante behandelt; keine neuen Einträge pro Land, Feld, Spielzug oder Partie.
- Acht vorhandene Spiele geprüft. Conquest: dasselbe unveränderte Weltbrett flach sowie auf dem vorhandenen räumlichen Tisch. Playtable: ursprüngliche gemeinsame Karten-/Filzfläche. Würfeltisch, Kniffel und Mäxchen: eine gemeinsame Würfelfläche aus dem tatsächlichen Renderbereich im bestehenden Tischbild. Daily-/Party-Quiz und Perfect haben kein eigenes Brett; ihre Fenster und Raumkulissen bleiben in den bisherigen Bereichen. Kniffelblock bleibt Fenster-/Anzeigebaustein. Keine alten unbenutzten Conquest-Bildentwürfe oder neuen 3D-Tische für reine 2D-Flächen als aktuelle Spielbretter ausgegeben.
- Insgesamt sechs feste Quellkonfigurationen unter zwei Grundvarianten, einschließlich des bisherigen Schach-/Dame-Feldbretts in beiden Ansichten. Persönliche Brettentwürfe werden über ergänzende Katalogmetadaten ihrer gespeicherten Ausführung zugeordnet, ohne Dateien oder Schnappschüsse umzuschreiben. Die alten allgemeinen Brettvorlagen werden nicht als zusätzliche Grundmodelle angeboten. Persönlicher Entwurf „Schachbrett Simpel“ weiterhin sichtbar geöffnet und mit ursprünglichem Renderer dargestellt.
- board_library.py liest die ursprünglichen Conquest-Tisch-/Geometrie-/Holzfunktionen und verwendet die vorhandene Kameraeinpassung; nur Modulpfade werden für die lokale Vorschau umgebogen. Gleiches Bild wie im lokalen Spiel. Feldbrett nutzt weiterhin models.js/buildBoard. Playtable und Würfelfläche verwenden ursprüngliche CSS-Regeln und Bilder mit proportionaler Gesamtskalierung; Würfelbereich exakt aus den vorhandenen Quellmaßen abgeleitet (1290 × 685). Keine Spielhandler, Länderbesitzdaten, Konten, Datenbanken oder aktiven Spiele geladen. Rendererquellen durch Prüfsummen gebunden.
- Dokumentiert in docs/BRETTER_GRUNDLAGEN.md/.json; reproduzierbar mit deploy/audit_board_library.py. Allgemeine Bestands- und Logikübersicht sowie Werkstatt-README aktualisiert. Editoroptionen bleiben ausdrücklich offen.
- Zwölf gezielte Tests (vier Brettprüfungen, acht Projektmappenprüfungen) bestanden, 73,441 Sekunden. Zwei Modelle, Abdeckung aller acht Spiele, Eigenschaftenvertrag, unveränderte Quellfabrik, Quelländerungserkennung, lokale Routen, Wiederverwendung/Laden/Übergabe und Erhaltung älterer Brettschnappschüsse geprüft. Python- und JavaScript-Syntax geprüft.
- Browserprüfung auf getrennter Prüfbibliothek: flaches Conquest-Brett, Playtable-Fläche, gemeinsame Würfelfläche und flaches Feldbrett dargestellt; Conquest-3D-Tisch sichtbar gedreht. Zwei Brettkonfigurationen (Conquest 3D und Playtable 2D) gesammelt, nach Neuladen als zwei Elemente wieder geöffnet und lokal übergeben; Übergabe enthält Größe/Form/Bild und die jeweilige Darstellung.
- Persönliche Werkstatt auf 127.0.0.1:8776 mit denselben Startoptionen und derselben Ablage neu geladen; Browser vollständig aktualisiert. Dort räumliches Feldbrett, eigener alter Brettentwurf und beide Conquest-Ansichten geprüft. Bibliothek zeigt zwei Grundvarianten, eigene Konfiguration bleibt darunter erhalten. Screenshot: runtime/board-library-20261027/board-library.png. Prüfdaten ausschließlich im getrennten runtime-Verzeichnis.
- Schutzvergleich: 480 erfasste Bestandsdateien SHA-256-identisch, darunter Spielquellen, tatsächliche Brettbilder/-modelle, Fragenbestände und sämtliche sieben persönlichen JSON-Dateien; keine zusätzlichen persönlichen JSON-Dateien. Kein Projektserverkontakt, keine Veröffentlichung und keine Umstellung bestehender Spiele. Figuren und weitere Bild-/Symbolbestände sowie neue Klang-/Schriftrecherche bleiben weitere Aufgaben; Editoroptionen später.
## 27.10.2026 – Figuren, Spielsteine und Conquest-Marken in der lokalen Werkstatt

- Drei wiederverwendbare Formfamilien mit sieben festen Konfigurationen aufgenommen: ursprüngliche Schachfiguren (gedrechselt/geometrisch, jeweils 2D/3D), Damesteine (2D/3D) und Conquests vorhandene räumliche Truppenmarke mit projizierter Zahlenfläche. Rollen, Stil, Proportionen, Farbe/Seite, Anzahl/Zahlenwert und Zustand sind Eigenschaften. Keine Einträge je Figur, Land, Truppenbestand, Spieler oder Partie. Schach/Dame bleiben allgemeine vorhandene Werkstattvorlagen und werden nicht als zusätzliche aktive Spiele ausgegeben.
- Alle acht Spielbereiche geprüft. Die übrigen Spiele besitzen keine zusätzlichen Spielsteinmodelle. Pokerchip-Motiv des Playtable-Einsatzreglers bleibt bestehende Einsatzanzeige; Karten, Würfel, Spielerporträts/Pulte und Routenpfeile bleiben ihren Kategorien zugeordnet. Keine neuen Figurenmodelle erfunden oder geladen.
- piece_library.py bindet ursprüngliche Quellen mit Prüfsummen. Schach/Dame importieren buildPiece direkt. Conquest verwendet unveränderte Geometrie-, Material-, DOM- und Projektionsfragmente aus territories.js sowie originale CSS-Regeln; Sockel und Zahlenfläche bleiben ein Baustein. Neutraler Beispielpunkt und Zahlenwert 8, originale Vorschaufarbe. Keine Spielhandler, Statusabfragen, realen Länderbestände oder Datenbanken eingebunden. Gesamte Komposition proportional skaliert.
- Alte allgemeine Figuren-Vorlagen nicht doppelt angeboten. Persönliche Entwürfe und alte Mappenschnappschüsse bleiben unverändert lesbar; zusätzliche Familienmetadaten nur an Katalogkopien. Editoroptionen bleiben später; Bibliothek ansehen, Konfiguration wählen und Projekten zuordnen ist jetzt verfügbar.
- Dokumentiert in docs/SPIELSTEINE_GRUNDLAGEN.md/.json, reproduzierbar mit deploy/audit_piece_library.py. Allgemeine Bestands-/Logikübersicht, BAUKASTEN und Werkstatt-README aktualisiert.
- Zwölf gezielte Tests (vier Spielsteinprüfungen und acht Projektmappenprüfungen) bestanden, 72,566 Sekunden. Begrenzte Familien statt Einzelbeständen, exakte Originalfragmente ohne Spielhandler, Quelländerungserkennung, lokale Routen, Wiederverwendung, alte/persönliche Schnappschüsse und Übergabe geprüft. Python-/JavaScript-Syntax geprüft.
- Browserprüfung: alle sieben Konfigurationen geladen, räumliche Schachansicht gedreht, Conquest-Marke sowie flache/räumliche Dameansichten geprüft. Getrennte Prüfmappe mit genau drei Formfamilien gespeichert, nach Neuladen wieder geöffnet und lokal übergeben (runtime/pieces-library-20261027/qa-library/handoffs/handoff-62e353941a03438b94c50bab1a5f2c3a.json). Eigener Prüfprozess auf Port 8777 anschließend anhand genauer Programm-/Ablagezuordnung beendet.
- Persönliche Werkstatt auf 127.0.0.1:8776 mit unveränderter persönlicher Ablage gestartet (beide Werkstattports waren zu Beginn ohne laufenden Dienst). Drei Formfamilien sichtbar geprüft. Screenshot: runtime/pieces-library-20261027/piece-library.png. Persönlicher Bestand weiterhin eine Projektmappe; alle sieben persönlichen JSON-Dateien unverändert. Keine Testentwürfe dort gespeichert.
- Schutzvergleich: 480 erfasste Dateien SHA-256-identisch, keine zusätzlichen persönlichen JSON-Dateien. Bestehende Spielquellen, Fragenbanken und Entwürfe unverändert. Kein Projektserverkontakt, keine Veröffentlichung oder Umstellung bestehender Spiele. Weitere Bild-/Symbolbestände und gewünschte neue Klang-/Schriftrecherche bleiben offen; Editoroptionen später.
## 27.10.2026 – Titelmotive, Flyer und Symbolsätze lokal aufgenommen

- Nächsten offenen Bild-/Symbolbestand erfasst: neun Bildmotive/Logos in zwei Bildfamilien, 13 Flyer-/Kachelkonfigurationen in drei ursprünglichen Kompositionen und sechs Symbolbausteine. Insgesamt 28 Konfigurationen in elf Modellen. Alle acht Spielbereiche zugeordnet. Gemeinsam verwendete Motive, etwa Würfeltisch/Mäxchen, einmal erfasst; Spielbeschriftungen bleiben Varianten der gemeinsamen Kachel.
- Icons als fünf endliche Sätze (Quiz 5, Navigation 4, Comic 15, Conquest-Ausstattung 3, Spielerstatistik 2) plus vorhandenes App-Symbol aufgenommen. Motivauswahl wechselt nur die Vorschau; Zuordnung und Übergabe enthalten den ganzen Satz. Keine Einzelregistrierungen pro Verwendung, Frage, Spieler oder Partie. Comic-Satz enthält die verfügbaren Motive der bestehenden Fabrik, nicht die Behauptung, jedes Motiv sei derzeit an einer aktiven Aktion verwendet.
- Bilddateien und Flyerkompositionen getrennt verwendbar. Originalartikel aus home.html, gemeinsame Makros aus _game_flyers.html sowie Spiel-/Gruppenkacheln aus tabletop_family.html/tabletop_connection.html unverändert gelesen. Originalbilder, Beschriftungen, Schriften, Überlagerungen und Kompositionen bleiben erhalten. Persönliche Geburtstagsfolie und angekündigte Schweinchen-Kachel nicht in den allgemeinen aktiven Spielbestand aufgenommen. Reine Texttitel bleiben Bestandteil ihrer bestehenden Kompositionen; keine neuen Bitmapkopien erzeugt.
- graphic_library.py bindet Herkunft und Prüfsummen. Quizzeichen aus Originalmakro/Sprite, Navigation aus bestehenden SVGs, Comiczeichen aus originaler icon-Fabrik, Conquest-Ausstattung aus originaler symbolImage-Fabrik, Statistikzeichen aus createPlayerPortrait; keine neu gezeichneten Symbole. Vorschau skaliert die ganze Komposition proportional und übernimmt keine Spielhandler, aktiven Links, Statusabfragen, Datenbanken oder echten Spielerdaten. Bestehender eigener Bildimport und persönliche Bildentwürfe erhalten; neue Editoroptionen später.
- Dokumentiert in docs/BILDBAUSTEINE_BESTAND.md/.json; reproduzierbar mit deploy/audit_graphic_library.py. Bestands-/Logikübersicht, BAUKASTEN und Werkstatt-README aktualisiert.
- Zwölf gezielte Tests (vier Grafikprüfungen und acht Projektmappenprüfungen) bestanden, 74,532 Sekunden. Nach im Browser gefundenem und korrigiertem fehlendem lokalen Modulpfad der Statistikzeichen alle vier Grafikprüfungen einschließlich beider originaler JS-Symbolquellen erneut bestanden, 20,802 Sekunden. Syntax geprüft. Quellenbindung, endliche Sätze, persönliche Ausschlüsse, unveränderte Originalfabrik, lokale Routen, Wiederverwendung und vollständige Übergabe abgedeckt.
- Browserprüfung: alle 28 Konfigurationen geladen, Quiz- und Conquest-Symbol innerhalb des Satzes gewechselt. Getrennte Prüfmappe mit genau drei Elementen (Perfect-Flyer, kompletter Quiz-Symbolsatz, Conquest-Bildmotiv) gespeichert, nach Neuladen wieder geöffnet und lokal übergeben. Übergabe enthält alle fünf Quizmotive trotz vorher gewählter Einzelvorschau (runtime/graphics-library-20261027/qa-library/handoffs/handoff-d5cf3776a79e4770b7362f2eb3fd2bcb.json). Prüfprozess auf Port 8777 nach genauer Programm-/Ablagezuordnung beendet.
- Nur persönliche Werkstatt auf 127.0.0.1:8776 mit denselben Startoptionen und derselben Ablage neu geladen. Titelmotive, Flyer und Symbole dort sichtbar geprüft; weiterhin eine persönliche Projektmappe und sieben persönliche JSON-Dateien. Screenshot: runtime/graphics-library-20261027/flyer-library.png. Alle Prüfdaten ausschließlich in getrennten runtime-Verzeichnissen gespeichert.
- Schutzvergleich: 480 erfasste Bestandsdateien SHA-256-identisch; sämtliche sieben persönlichen JSON-Dateien unverändert und keine zusätzlichen persönlichen JSON-Dateien. Spiele, Fragenbanken und Entwürfe erhalten. Kein Projektserverkontakt, keine Veröffentlichung oder Spielumstellung. Gewünschte neue Klang-/Schriftrecherche, Materialaufbereitung und Prüfung der Editoroptionen bleiben offen.
## 27.10.2026 – Kleine freie Auswahl für passende Schriftwirkungen und Spielklänge

- Nutzerpräzisierung umgesetzt: passende Schrift-/Oberflächenkombinationen statt freier Effektmatrix für jede Schrift. Sieben feste Stile aufgenommen: Kreide/Cabin Sketch Bold, Stein/Cinzel, Metall/Stardos Stencil Bold, Stempel/Schreibmaschine/Special Elite, Handschrift/Kalam, Comic/Fredoka und Klar/Inter. Raue Kreideglyphen stammen aus der gewählten Schrift; Stein und Metall kombinieren geeignete Formen mit begrenzten 2D-Licht-/Schattenkanten und lokaler Oberfläche. Keine 3D-Schriftmodelle oder allgemeine neue Materialmatrix erzeugt.
- Neu recherchierte Originaldateien aus dem offiziellen Google-Fonts-Repository lokal gespeichert: sechs OFL-1.1-Familien und Special Elite unter Apache 2.0. Originale Beschreibungen, Lizenztexte, Downloadadressen, Git-Blob-Kennungen und Prüfsummen erhalten. Alle sieben konkreten Fontdateien auf ÄÖÜäöüß und 0–9 geprüft. Browser lädt Fonts nur vom eigenen lokalen Werkstattdienst. Alte Fontdateien und bestehende Schriftzuordnungen nicht verändert.
- 13 kurze Kenney-CC0-Klänge aus den offiziellen Paketen Interface Sounds, Casino Audio und Music Jingles ausgewählt: fünf Bedienklänge, fünf Tischaktionen und drei Spielereignisse. Rundenbeginn, Sieg und Niederlage verwenden dieselbe Pizzicato-Klangfarbe; passende auf-/absteigende Folgen für Sieg/Niederlage. Dauern 0,023–3,064 Sekunden. Kleine funktionale Ausgangsauswahl, keine vollständige Musik-/Effektsammlung.
- Original-OGGs und mitgelieferte CC0-Texte unverändert erhalten. Lokale Mono-WAV-Hördateien mit angeglichenem Pegel, maximaler Spitze 0,65 und 5-ms-Randblenden erstellt; keine Tonhöhenänderung oder Kürzung. Dauer/Pegel/Wellenform und Herkunft in sounds.json dokumentiert. Freier Decoder ausschließlich im isolierten runtime-Prüfordner verwendet; keine neue Abhängigkeit der Spiele oder des Werkstattdienstes. Klangliche persönliche Abnahme bleibt möglich; technische Prüfung ersetzt diese nicht.
- Zwei neue Bibliotheksbereiche Schriften und Klänge in derselben Werkstatt. Sieben Schriftstile und drei Klangzweckgruppen mit 13 einzeln wählbaren Proben. Probehören, Stopp und Lautstärke funktionieren nur in der Vorschau; kein automatisches Abspielen oder Umstellen von Spielereignissen. Schließen entfernt eine laufende Medienvorschau. Schriftstile und Klänge lassen sich als unveränderte Schnappschüsse in Projektmappen sammeln und übergeben. Keine Editoroptionen geprüft oder bestehende Buttonauswahl ersetzt.
- Dokumentiert in docs/KLAENGE_SCHRIFTEN_AUSWAHL.md/.json; reproduzierbarer Bericht mit deploy/audit_media_library.py. Allgemeine Bestands-/Logikübersicht, BAUKASTEN und Werkstatt-README fortgeschrieben. Nun 17 Elementbereiche und zwei zusätzlich inventarisierte Familien (Material/Darstellung); deren Aufbereitung und die späteren Editorprüfungen bleiben offen.
- Zwölf gezielte Tests (vier Medienprüfungen, acht Projektmappenprüfungen) bestanden, 76,176 Sekunden. Freie Lizenz-/Quellbindung, passende feste Stile, deutsche Glyphen, WAV-Dekodierbarkeit und Dauern, lokale Routen, Wiederverwendung, erneutes Laden und unveränderte Übergabeschnappschüsse geprüft. Python-/JavaScript-Syntax bestanden.
- Browser: alle sieben Schriftstile sichtbar geladen; alle 13 Klangdateien bis zum Wiedergabeende geprüft. Stopp, Lautstärkeänderung und Entfernen der laufenden Vorschau beim Schließen kontrolliert. Getrennte Prüfmappe mit Kreide-, Metallstil und Siegklang nach Neuladen wieder geöffnet und lokal übergeben (runtime/media-library-20261027/qa-library/handoffs/handoff-d6fab0c4b4fd4eb59056a69c8df3e302.json). Prüfprozess auf Port 8777 anschließend nach genauer Programm-/Ablagezuordnung beendet.
- Persönliche Werkstatt auf 127.0.0.1:8776 mit identischen Startoptionen und derselben Ablage neu geladen. Neue Schriftbereiche sichtbar und Siegklang erneut bis zum Ende geprüft. Screenshot: runtime/media-library-20261027/chalk-personal.png. Persönlicher Bestand weiterhin eine Projektmappe und sieben JSON-Dateien; keine Prüfentwürfe dort gespeichert.
- Abschließender Schutzvergleich: 536 erfasste Bestandsdateien unverändert, einschließlich aller alten Buttonressourcen, Spielquellen, Fragenbestände und sämtlicher persönlicher JSON-Dateien. Keine zusätzlichen persönlichen JSON-Dateien. Recherche nur an öffentlichen kostenlosen Quellen; keine Konten, Käufe, Veröffentlichung oder Projektserver-/Spielumstellung.
## 27.10.2026 – Vollständigkeitsstand geprüft: Raumkulisse als konkrete Restlücke

- Auf Nachfrage aktuellen laufenden Katalog auf 127.0.0.1:8776 mit Quellen verglichen: 17 befüllte Elementbereiche, 15 Hintergrundmotive und 19 Avatare. Gefüllte Bereiche belegen noch keine vollständige Aufnahme aller vorhandenen Darstellungen; die bisherigen Berichte weisen diese Grenze ausdrücklich aus.
- Konkrete Restlücke bestätigt: Conquests aktuelle scene.js lädt raum-wand-v2.png, moebel-v2.png und teppich.png, während im Hintergrundbereich für Conquest nur conquest-lobby-background-v1.png registriert ist. Die zusammengehörige räumliche Spielkulisse fehlt als wiederverwendbare Raumkonfiguration. Keine drei unabhängigen neuen Grundbausteine daraus ableiten.
- Offener nächster Aufnahmeschritt: Raumkulissen ergänzen und abschließenden Quellen-/Katalogabgleich aller acht Spiele ausführen. Gemeinsame Material-/Darstellungsaufbereitung betrifft Eigenschaften bestehender Bausteine; Editoroptionen bleiben gesondert später. Dokumentationshinweis in WERKSTATT_LOGIKPRUEFUNG.md ergänzt. Keine Spiel-, Katalog-, Entwurfs- oder Dienständerung vorgenommen.
## 27.10.2026 – Raumkulissen ergänzt und acht Spiele abschließend auf Werkstattelemente abgeglichen

- Neun ganze ursprüngliche Raumkonfigurationen unter Hintergründe aufgenommen: acht flache Kulissen und Conquests räumlicher Spielraum. Zwei gemeinsame Grundmodelle 2D/3D; Wand, Möbel und Teppich bilden bei Conquest ein zusammengehöriges Element. Tisch/Brett und Spieloberfläche bleiben separat. Ursprüngliche buildRoom-Fabrik aus scene.js unverändert über Vorschauadapter verwendet; keine zweite Raumgeometrie entworfen. Perfect mit ursprünglichen Vorhängen, Lichtern, Fenster und Kamin. Gemeinsame Würfel-/Lobby-/Profilkulissen nach ihren vorhandenen Quellen zugeordnet.
- Die 15 bisherigen Hintergrundmotive behalten ihre Kennungen und Schnappschüsse. Bildhintergründe, flache Räume und räumliche Räume als drei Bibliotheksgruppen sichtbar; Bild-/Ansichtsauswahl bleibt Eigenschaft. Neue RoomLibrary bietet lokale Vorschau und Projektzuordnung, keine geprüften Editoroptionen oder Spielintegration.
- Beim Quellen-/Katalogabgleich noch fehlende ganze Quizkompositionen ergänzt: vollständiges Fragenfenster, Rundenergebnis, Antwortübersicht, Ranglistenrahmen und leerer Fragenvorrat. Fünf Modelle mit 30 festen neutralen Beispielen (16/3/3/7/1); Start-/Ergebnisrangliste Varianten derselben Originalvorlage. Insgesamt nun 35 Fenstermodelle und 114 Beispiele, bestehende 84 Fensterkennungen unverändert. Keine Fragen kopiert oder als Karten registriert. 40 Fensterbeispiele mit Verweis auf Fragenbanken und Steckbrief; wachsende Fragenbestände ändern keine Katalogkennungen.
- Aktuellen Bestand von Guesstimate, Party, Perfect, Playtable, Würfeltisch, Kniffel, Mäxchen und Conquest einschließlich eingebundener Makros und Spielesammlung geprüft. Abschlussbericht hält 60 Vorlagen-/Stil-/Fabrikquellen mit Prüfsummen, 65 semantische Container (53 zugeordnet, zehn belegte Anordnungen, zwei Ausschlüsse) und 13 zentrale DOM-/3D-Fabriken fest. Sechs erneuerte Quellprüfungen für Buttons, Fenster, Eingaben, Anzeigen, Spieler und Lobbys ohne offene Zuordnungen. Im dokumentierten aktuellen Bestand keine weiteren fehlenden Elementzuordnungen festgestellt; kein behaupteter Durchlauf aller möglichen Spielzustände. Persönliche Grußfolie, technischer Vorschau-/Entwicklerhinweis, inaktive Prototypen, native Browserdialoge und technische Bibliotheksinternas ausdrücklich abgegrenzt.
- Dokumentation: docs/WERKSTATT_ABSCHLUSSPRUEFUNG.md/.json; reproduzierbar mit deploy/audit_workshop_completeness.py. Bestands-/Logikübersicht, BAUKASTEN und Werkstatt-README aktualisiert. Material-/Darstellungsaufbereitung betrifft Eigenschaften bestehender Bausteine; Editoroptionen und persönliche Gestaltungsabnahme bleiben später.
- 19 gezielte Tests bestanden (Raum-/Quellen-/Fensterprüfung, Fragenwachstum und Projektmappen), 93,707 Sekunden. Lokale Vorschauabrufe nach vollständigem Einlesen der Antworten zusätzlich einzeln erneut bestanden, 14,603 Sekunden. Originalfabrik, Quelländerungserkennung, stabile bisherige Schnappschüsse/Kennungen, neutrale Ergebniswerte, zwei Raumgrundmodelle, acht Spiele, Erkennung neuer unregistrierter Container, lokale Routen, Wiederverwendung/Neuladen/Übergabe geprüft. JavaScript-Syntax von workshop.js und room-stage.js bestanden.
- Browser: alle neun Räume und 30 neuen Fensterbeispiele geladen, Ansichtswechsel des Conquest-Raums geprüft. Vollständige Fragenfenster mit fünf Fragetypen/Auflösungen für Quiz und Party, Ergebnisstufen 100/320/500, Antwortübersichten und sieben Ranglistenvarianten sichtbar mit neutralen Werten geprüft. Keine Browserfehler gemeldet. Getrennte Prüfmappe mit genau zwei Elementen (ganzer Raum und verknüpftes Fragenfenster) nach Neuladen wieder geöffnet und lokal übergeben: runtime/completeness-20261027/qa-library/handoffs/handoff-565e9b3c31984a16a114003e25406867.json. Übergabe enthält alle drei Raumtexturen und den question_bank_reference-Vertrag. Eigener Prüfprozess auf Port 8777 nach genauer Pfad-/Ablagezuordnung beendet.
- Persönliche Werkstatt auf 127.0.0.1:8776 mit identischen Optionen und derselben Ablage neu geladen. Drei Hintergrundgruppen, 35 Fenstermodelle und ursprünglicher Conquest-Raum dort sichtbar geprüft. Screenshot: runtime/completeness-20261027/rooms-personal.png. Persönlicher Bestand weiterhin eine Projektmappe und sieben persönliche JSON-Dateien; keine Prüfentwürfe darin gespeichert.
- Abschließender Schutzvergleich: 590 erfasste Dateien SHA-256-identisch; sämtliche sieben persönlichen JSON-Dateien unverändert und keine zusätzlichen persönlichen JSON-Dateien. Spiele, Fragenbanken und Entwürfe unverändert. Keine Veröffentlichung, Projektserverabfrage, Spiel-/Datenbankumstellung oder Änderung anderer lokaler Dienste.

## 27.10.2026 – Gemeinsame Material-/Ansichtsübersicht und Projektwünsche (nur lokal)

- Nutzerfreigabe zur Fortsetzung auf die verbleibende gemeinsame Material-/Darstellungsaufbereitung angewandt; bausteinspezifische Editoroptionen bleiben später. Neuer Bereich „Material & Ansicht“ in der Werkstatt, keine zusätzlichen Elementarten. 17 Elementbereiche und zwei gemeinsame Eigenschaftsbereiche klar getrennt.
- Kleine gemeinsame Palette: Holz, Stein/Tafel, Metall, Farbfläche, Farbverlauf, Durchscheinend, Filz, Papier und bedruckter Karton. Die sechs vorhandenen Buttonmaterialien mit demselben ursprünglichen Renderer und derselben Kontur gezeigt; Filz/Papier/Karten als direkte Vorschauen der vorhandenen Bausteine. Quellen und Prüfsummen an Definitionen gebunden. Keine Materialdateien, Modelle, Bilder oder Renderer kopiert bzw. neu heruntergeladen. Passende feste Kreide-/Stein-/Metall-/Handschrift-/Stempelstile verlinkt; keine beliebige Schrift-/Effektmatrix.
- Drei Originalbeispiele erläutern die bestehenden Projektentscheidungen: 2D mit flacher Playtable-Fläche, fester räumlicher Blick / 2,5D mit demselben räumlichen Conquest-Brett und 3D mit ursprünglichem Conquest-Raum. Licht/Schatten und Bewegungswünsche für Figuren, Würfel, Karten separat. Beide vorhandenen Würfelvarianten und beide Kartenbausteine bleiben erhalten; keine neue Physik für flache Anzeigen behauptet.
- Materialwünsche können ausdrücklich in einer Projektmappe gewählt werden. Optionaler Schlüssel surfaces im bestehenden Format 2 mit eingefrorenen Definitionen und Herkunft. Kein Material als zusätzliches item, keine automatische Beschichtung/Änderung des Originals. Alte Mappen ohne Schlüssel unverändert lesbar; Speichern durch einen alten Client erhält vorhandene Wünsche. Leere explizite Auswahl entfernt Wünsche erst in einem neuen Stand. Alte Dateien und Element-Schnappschüsse bleiben erhalten.
- Gemeinsame PropertyPanels-Oberfläche für Übersicht und Projektwahl; vorhandene Vorschaumethode proportional verwendet. Beim Quellen-/Browservergleich zunächst unskalierte Vorschauteile durch zu späte DOM-Anbindung erkannt und im neuen Panel behoben. Ausgeblendete/geschlossene Vorschau-Iframes werden entfernt, damit vorhandene räumliche Vorschauen keine ungültige Größe erhalten und nicht weiterlaufen. Ursprüngliche Spiel-/Brett-/Raumrenderer unverändert. Nach Korrektur bei erneutem Ansicht-/Projektwechsel keine neuen Vorschaufehler beobachtet.
- 18 gezielte Tests bestanden, 93,489 Sekunden: Quellen/Verknüpfungen, neun Familien und drei Ansichten ohne Katalogwachstum, exakte Originalelemente, Speichern/Laden/Übergabe, alte Mappen und Clients, stabile eingefrorene Wünsche, ungültige Auswahl, Quelländerungserkennung, lokale Routen und Fragenwachstum. Python-/JavaScript-Syntax bestanden. Abschließender acht-Spiele-Quellenabgleich weiterhin ohne offene Elementzuordnungen; 40 Fragenfensterverweise, keine Einzelfragen als Assets.
- Browser: neun Materialfamilien, fünf verknüpfte feste Schriftstile und drei Originalansichten geladen. Raumansicht gewechselt; Entfernen geschlossener Vorschauen und Verlassen der Übersicht geprüft. Schmal bei 390 Pixeln ohne horizontalen Überlauf (375 Pixel Inhalt); temporäre Viewportvorgabe wieder zurückgesetzt. Getrennte Prüfmappe mit Holz-/Filzwunsch, fester räumlicher Ansicht, Licht/Kartenbewegung und zwei Originalelementen (Conquest-Brett, flache Karte) gespeichert, nach Neuladen wieder geöffnet und übergeben. Übergabe: runtime/properties-20261027/qa-library/handoffs/handoff-88962de0a7fe48bb857cdb811ef1e7cc.json. Exakte Wünsche und zwei unveränderte Element-Schnappschüsse unabhängig gelesen. Prüfprozess auf 8777 anschließend nach genauer Pfad-/Ablageprüfung beendet.
- Persönliche Werkstatt auf 127.0.0.1:8776 mit denselben Optionen und derselben persönlichen Ablage neu geladen. Neuer Bereich dort mit geladenen ursprünglichen Brett-/Raumvorschauen sichtbar geprüft und geöffnet gelassen. Screenshots: runtime/properties-20261027/materials-personal.png und materials-personal-full.png. Weiterhin eine persönliche Projektmappe und sieben persönliche JSON-Dateien, kein neuer surfaces-Schlüssel an der bestehenden persönlichen Mappe und keine Prüfentwürfe dort gespeichert.
- Schutzvergleich über 650 Ausgangsdateien: 649 unverändert; ausschließlich die in diesem Auftrag ergänzte Werkstatt-README als erwartete Dokumentationsänderung ausgenommen. Keine unerwarteten Änderungen und keine zusätzlichen persönlichen JSON-Dateien. Spiele, Fragenbanken, sämtliche persönlichen Entwürfe und ursprüngliche Vorschau-/Assetquellen unverändert. Kein Projektserverkontakt, keine Veröffentlichung und keine Umstellung anderer lokaler Dienste.
- Dokumentiert in docs/MATERIAL_DARSTELLUNG.md/.json; Bericht mit deploy/audit_workshop_properties.py reproduzierbar. Allgemeine Bestands-/Logikübersicht, Abschlussbericht, BAUKASTEN und Werkstatt-README aktualisiert. Inhaltliche Material-/Darstellungswünsche jetzt gemeinsam verfügbar; konkrete Umsetzung einzelner Editoroptionen, Spieleinbau und persönliche gestalterische Abnahme bleiben offen.

## 27.10.2026 – Erster technischer Button-Optionscheck an Guesstimate-Kernmodellen

- Erneute Nutzerfreigabe zur Fortsetzung als nächsten vorgemerkten Arbeitsschritt auf die zurückgestellte Editorprüfung angewandt; Beginn beim Button-Editor ausdrücklich angekündigt. Neun Guesstimate-Kernmodelle mit zehn Einsatzbeispielen aus der vorhandenen Vergleichsansicht geprüft. Die freigegebene Startseitenaktion Spielen/Ergebnis bleibt ein Modell. Keine weiteren optischen Zusammenführungen vorgenommen; Nachholbutton und andere Originalgestaltungen unverändert.
- Alle 27 vorhandenen Felder an der Startseitenaktion mit konkreten Werten berührt, einschließlich Voraussetzungen für Deckkraft, Seitenwandfarben und Klang. Zusätzlich Größen-/Schrift-/Tiefenänderungen sowie Verfügbarkeit an neun Kernmodellen geprüft. Keine Behauptung, sämtliche 85 Modelle oder alle möglichen Kombinationen seien abgenommen.
- Tatsächliche Probleme gefunden und ausschließlich in der Bedienoberfläche offline-preview/button-workshop-v1/workshop.js korrigiert: Matt/Glanz bei bewahrter Originalfläche deaktiviert und erklärt, bei eigenem Material/Farbe/Stil freigegeben; wirkungslosen Strukturregler im reduzierten Stil verborgen; Lautstärke nur bei gewähltem Klang sichtbar; Tiefe 0 jetzt „ohne Tiefe“, 1–4 „dezent“. Werte werden durch Ausblenden/Deaktivieren nicht geändert. Der Zustand der Originalfläche wird direkt aus dem verbindlichen Renderer gelesen; keine zweite Oberflächenlogik oder neue Materialimplementierung.
- Vorher/nachher an allen neun Kernmodellen exakt gleiche Ausgangswerte und erfasste Darstellungsmerkmale bestätigt. Größe, Formhöhe, Schriftgröße und Tiefe reagieren. An eigener Holzfläche im natürlichen Stil wirken Glanz und Struktur; bei Klangwahl wird die Lautstärke verfügbar. Konturwechsel, Klickprobe mit 650-ms-Einstellung und lokaler Holzaufnahme bei 40 % ausgeführt. Animationskurve/Dauer im Browser nicht messtechnisch abgenommen; Parameterzuordnung im unveränderten Quellcode geprüft.
- Eigene Variante „Optionsprüfung · Holztest“ nur in getrennter Prüfbibliothek gespeichert. Über gemeinsame Bibliothek im eingebetteten Editor erneut geöffnet; Material wood, Stil natural, Glanz gloss, Struktur 55, Tiefe 4, Schriftgröße 130, Holzklang und Lautstärke 40 erhalten. In einer getrennten Mappe nach Neuladen wieder geöffnet und lokal übergeben. Übergabe: runtime/button-options-20261027/qa-library/handoffs/handoff-cb77db32f0c44792bdd0453a330e0129.json. Exakte Gleichheit zwischen gespeichertem Rezept und übergebenem Schnappschuss unabhängig bestätigt; genau ein Mappelement.
- Zwölf bestehende Button-Werkstattprüfungen bestanden (1,155 Sekunden), zwei gezielte Quell-/Übergabetests bestanden (9,025 Sekunden). Bestehende Node-Prüfungen für Geometrie, Schriftzuordnung, Proportionen und Klangablauf bestanden; JavaScript-Syntax geprüft. Frischer Katalogcheck: 144 Verwendungen, 85 Modelle, alle 144 Rezepte validierbar, keine Fehler. Browser-Prüflog ohne Fehler.
- Persönliche Werkstatt unter 127.0.0.1:8776 im neuen Editorfenster nur lesend geöffnet und Korrektur sichtbar bestätigt: Originalfläche erhalten, Oberfläche deaktiviert mit Erklärung, „ohne Tiefe · 300 ms“. Screenshot: runtime/button-options-20261027/editor-personal.png. Keine Testdatei in persönlicher Bibliothek gespeichert. Persönlicher Dienst 19712 läuft unverändert weiter; kein Dienstneustart erforderlich. Eigener QA-Prozess auf 8777 nach genauer Port-/Pfad-/Ablageprüfung beendet.
- Schutzvergleich: alle 654 erfassten Dateien unverändert, darunter Spielquellen, Fragenbestände, Renderer/Materialien/Geometrie/Klänge, übrige Werkstattbausteine und sämtliche sieben persönlichen JSON-Dateien. Keine zusätzlichen persönlichen JSON-Dateien. Keine Datenbank, Veröffentlichung, Projektserverabfrage oder Spielumstellung. Nur Editor-Bedienoberfläche und ausdrücklich fortgeschriebene Dokumentation verändert.
- Dokumentiert in docs/BUTTON_EDITOR_PRUEFUNG.md/.json; reproduzierbarer Bericht mit deploy/audit_button_editor_options.py. Beide Werkstatt-READMEs und Abschlussbericht fortgeschrieben. Nächster sinnvoller Schritt: neue sieben passende feste Schriftstile und 13 kurze Werkstattklänge auch im älteren Button-Editor anbieten, ohne Änderung alter Kennungen/Rezepte/Spielzuordnungen. Weitere Modelle/Editoren, persönliche Gestaltungsabnahme und Spieleinbau bleiben offen.

## 28.10.2026 – Sieben feste Schriftstile und 13 kurze Klänge im Button-Editor (nur lokal)

- Ausdrücklicher Nutzerauftrag umgesetzt: sieben bestehende passende Schrift-/Oberflächenstile in „Schrift & Wirkung“, 13 kurze Werkstattklänge in „Klang“ und der Hörgalerie. Kreide/Tafel, Stein, Eisen, Stempel/Schreibmaschine, Handschrift, Comic und Klar nutzen ihre bisherigen konkreten Schriftdateien und Flächen. Keine beliebige Effektmatrix. Nicht wirksame freie Material-/Schriftoptionen beim festen Stil verborgen; Werte bleiben erhalten und beim Wechsel zur bisherigen Schrift wieder verfügbar. Bild-/Symbolbuttons werden nicht mit Textstilen überdeckt; am ursprünglichen Perfect-Bildbuzzer im Browser bestätigt.
- Neue Kennungen mit media-Präfix ausschließlich zusätzlich zu alten Kennungen. Keine neuen Pflichtfelder oder Standardwerte, keine Migration oder automatische Zuordnung. Neuer kleiner Medienadapter erweitert den Werkstattkatalog; lokale Aliase verwenden die vorhandenen Font- und WAV-Dateien. Neue kurze Clips werden vollständig gespielt. Alte Klangausschnitte, Klangengine, ursprünglicher Buttonrenderer, Materialien, Geometrie und Medienbibliotheksdateien unverändert.
- Eine opt-in-Erweiterung verwendet dieselbe kanonische Buttonkomposition in Editor, Bibliotheksminiaturen und Detailansichten. Passende Flächen werden proportional aus der bestehenden media-stage.css abgeleitet. Spiele importieren weiterhin ihren ursprünglichen Renderer. Alle 144 ursprünglichen Rezepte wurden zusätzlich mit dem vor dem Auftrag gespeicherten Ausgangsstand exakt verglichen; keine Werteabweichung. Frischer Katalogabgleich ebenfalls 144 validierbare Rezepte, 85 Modelle und keine Unterschiede zwischen altem und erweitertem Katalog.
- Zwölf bestehende Buttonprüfungen und vier neue Medienprüfungen bestanden; zusätzlich zwei gezielte Quell-/Übergabetests. Neue Prüfungen decken additive Auswahl, alte Kennungen/Standardwerte, lokale Font-/WAV-Routen beider Werkstattdienste, Speichern/Neuladen und unveränderte Übergabe von sieben Stilvarianten ab. Node prüft alle 13 tatsächlichen kurzen WAV-Dateien an der unveränderten Klangengine: volle Dauer, kein zweiter Anschlag beim Loslassen, Zwischenspeicherung und Lautstärke 0. Vorhandene Geometrie-/Klangprüfungen und Python-/JavaScript-Syntax bestanden. Keine vollständige Prüfung aller 85 Modelle behauptet.
- Browser: alle sieben Fonts tatsächlich geladen und auf derselben unveränderten 430×58-Buttonform gezeigt. Schrift und ursprüngliches Pfeilsymbol haben passende Schriftfarbe. Alle 13 Klänge am Button ausgelöst; Galerieauswahl, Stopp, Lautstärke 0 und eine vollständige native WAV-Hörprobe geprüft. Wechsel zur ursprünglichen Schrift stellt Originalfläche und ursprünglichen Font wieder her. Neue Kreide-/Klickvariante nur in getrennter runtime-Testablage gespeichert, über Bibliothek und eingebetteten Editor wieder geöffnet; Font, Klang und Lautstärke 30 erhalten. Prüfmappe nach Neuladen lokal übergeben: runtime/button-media-20261028/qa-library/handoffs/handoff-c3fc359be07045fc8bfd67a4b27cd7e4.json. Übergebener Schnappschuss exakt gleich dem gespeicherten Rezept.
- Frühe Iframewechsel zeigten MutationObserver-Meldungen ohne Quelldatei im Browserprotokoll; Herkunft nicht geklärt. Kein Scheitern von Speichern, Wiederöffnen oder Übergabe beobachtet. In der später neu geladenen persönlichen Editoransicht keine neuen Warnungen/Fehler. Persönliche gestalterische/klangliche Abnahme bleibt offen.
- Persönliche Werkstatt 8776 ausschließlich mit denselben Startoptionen und Ablagen neu geladen (PID 29268). Dort ursprünglichen Ausgangsbutton und neue Kreide-/Klickauswahl sichtbar geprüft; Vorschau geöffnet gelassen, nichts persönlich gespeichert. Screenshot: runtime/button-media-20261028/editor-personal.png. Eigenen getrennten QA-Prozess auf 8777 nach genauer Pfad-/Ablageprüfung beendet. Keine anderen lokalen Dienste oder Spiele verändert.
- Schutzvergleich: alle 647 erfassten geschützten Dateien unverändert; sämtliche sieben persönlichen JSON-Dateien unverändert und keine zusätzlichen persönlichen JSONs. Spiele, Fragenbanken, Entwürfe und bestehende Zuordnungen erhalten. Kein Projektserverkontakt, keine Veröffentlichung, keine neue Assetrecherche/Downloads oder Spiel-/Datenbankumstellung.
- Dokumentiert in docs/BUTTON_MEDIEN_INTEGRATION.md/.json; Bestandsbericht mit deploy/audit_button_media.py reproduzierbar. Button-Optionsbericht, Medienauswahl, Werkstatt-READMEs und Abschlussbericht fortgeschrieben. Weitere Modelle und Baustein-Editoren sowie Spieleinbau bleiben gesonderte Aufgaben.

## 28.10.2026 – Übergabe für die gemeinsame Editorprüfung heute Mittag

- Auf ausdrücklichen Nutzerwunsch die Chatübergabe lokal als [UEBERGABE_WERKSTATT_EDITOR_2026-10-28.md](UEBERGABE_WERKSTATT_EDITOR_2026-10-28.md) gespeichert. Nutzerkorrektur: Fortsetzung heute Mittag am 28.10.2026, nicht am Folgetag.
- Einstieg für den neuen Chat: gemeinsame praktische Benutzung und gezielte Verbesserung des Button-Editors anhand der Rückmeldungen des Nutzers. Abgeschlossene Elementaufnahme und noch offene vollständige Editor-/Gestaltungsprüfung klar getrennt; Bausteinlogik, lokale Grenzen, Dokumente und zuletzt geöffnete Ansicht enthalten.
- Ausschließlich Übergabedatei ergänzt und diesen Logeintrag angehängt. Vorherigen Loginhalt beim Rücklesen bytegenau erhalten; Übergabe als UTF-8 zurückgelesen. Keine Spiele, Fragenbanken, persönlichen Entwürfe, Zuordnungen oder Dienste geändert.

## 28.10.2026 – Wiedereinstieg in die gemeinsame lokale Button-Editorprüfung

- Übergabe UEBERGABE_WERKSTATT_EDITOR_2026-10-28.md und die dort genannten Prüfberichte gelesen. Praktische Bedienversuche des Nutzers sind der nächste Schritt; keine erneute allgemeine Elementaufnahme und keine Gestaltungsänderung vorgenommen.
- Persönliche Werkstatt auf Port 8776 war beim Einstieg im Browser nicht erreichbar. Nur diesen lokalen Dienst mit der vorhandenen Ablage D:\Guesstimate\design-library und dem bisherigen Buttonentwurfsordner gestartet (PID 6216). Die ursprüngliche Startseitenvorlage spielen im Browser tatsächlich sichtbar geöffnet; Schrift-/Stilauswahl und Speicherbereich vorhanden. Browseransicht für die gemeinsame Fortsetzung offen gelassen. Keine neue vollständige Editorprüfung behauptet.
- Alle sieben persönlichen JSON-Dateien vor/nach dem Wiedereinstieg SHA-256-identisch, keine zusätzlichen persönlichen JSON-Dateien. Kein Projektserverkontakt, keine Änderung von Spielen, Fragenbanken oder Zuordnungen. Startprotokolle und Ausgangsprüfsummen: runtime/workshop-resume-20261028-144950/.

## 28.10.2026 – Praktischer Buttonaufbau: Neubeginn, getrennte Farben und Schrift

- Nutzerentscheidung nach benannten Widerspruch zur bisherigen festen Schrift-/Flächenkopplung bestätigt: zuerst Form, dann Oberfläche/Farbe, danach Beschriftung, Bewegung/Ton und Speichern. Neuer Einstieg „Neuen Button erstellen“ mit neutralem flachem Button und fünf direkt anwählbaren Schritten. Derselbe Editor für Neubeginn, Vorlagen und vorhandene Spielbuttons; keine zweite Buttonkomposition.
- Sieben neue letter-Schriftwahlen verwenden die vorhandenen Schriftdateien und passenden Wirkungen ausschließlich für die Beschriftung. Fläche, Schriftfarbe und Seitenwandfarbe bleiben separat. Alte media-Rezepte behalten unverändert ihre bisherige Darstellung und Kennungen; sichtbare Aktion trennt sie und übernimmt ihre Grundfarbe als eigene Farbfläche. Originaler Renderer, Geometrie, Medienbibliothek, Klangengine, Standardkatalog und Spielquellen unverändert. Erweiterung ausschließlich im gemeinsamen Werkstattadapter.
- Tiefe und Schatten bei Form eingeordnet; Seitenwandfarbe bei Oberfläche/Farbe stets sichtbar, mit Erklärung bei flacher Form. Farbwahl stellt auf Eigene Farbe um. Vorlagen erklären ihre bewahrte Originalfläche; Material, Farbe oder Glanz bearbeiten die eigene Oberfläche, ohne zuerst andere Werte ändern zu müssen. Speichern aktualisiert die genaue Entwurfsadresse für erneutes Laden. Ein Neubeginn bewahrt den vorherigen Entwurf pro Browsertab zur Wiederaufnahme.
- Zwölf bestehende Editorprüfungen und fünf Medien-/Speicherprüfungen bestanden, außerdem bestehende Node-Geometrie-/Schrift-/Proportionsprüfungen sowie Python-/JavaScript-Syntax. Der erste HTTP-Testlauf war durch lokale Socket-Zugriffsrechte blockiert; nach Freigabe bestanden alle fünf Prüfungen. Keine vollständige Prüfung aller 85 Modelle behauptet.
- Getrennte Browserprüfung auf 8777: neuen grünen Button mit Tiefe 8, eigener Seitenwand, cremefarbener Kreideschrift und Klickklang erstellt, ausprobiert, gespeichert und nach Neuladen mit identischen Werten wieder geöffnet. Neubeginn und Rückkehr zum vorherigen Entwurf geprüft. Shop-Vorlage violett/glänzend bearbeitet, als eigene Variante gespeichert und nach Neuladen bestätigt. Älteren gekoppelten Kreidestil erhalten, anschließend ausdrücklich getrennt und eigene Schriftfarbe sichtbar geändert. Alle Prüfdaten unter runtime/button-flow-20261028/.
- Persönliche Werkstatt 8776 nach eindeutiger Prozess-/Port-/Ablageprüfung mit denselben persönlichen Verzeichnissen neu geladen (PID 20220). Zusätzliche Ansicht mit neuem Button im In-App-Browser sichtbar geöffnet; persönliche Editoransicht ohne protokollierte Warnungen/Fehler. Screenshot runtime/button-flow-20261028/editor-personal.png. Keinen persönlichen Prüfentwurf gespeichert. Elf geschützte Ausgangsdateien einschließlich sämtlicher sieben persönlichen JSON-Dateien SHA-256-identisch; keine zusätzlichen persönlichen JSON-Dateien. Keine Veröffentlichung oder Projektserverabfrage.
- Nächster Benutzerschritt: selbst einen neuen Button gestalten und speichern, danach vorhandene Shop-Vorlage bearbeiten. Eine allgemeine Aktiv-/Inaktiv-Auswahl für Entwürfe in bestehenden Spielen ist weiterhin nicht implementiert und wird in der Oberfläche als noch nicht verfügbar benannt. Es wurde kein Entwurf im Spiel aktiviert. Dokumentation in beiden Werkstatt-READMEs sowie BUTTON_EDITOR_PRUEFUNG und BUTTON_MEDIEN_INTEGRATION fortgeschrieben.

## 28.10.2026 – Einstellbarer Vorschauhintergrund und klare Herkunftsbezeichnung

- Nutzerrückmeldung: dunkle feste Vorschau erschwert die Trennung von Seitenwand und Schlagschatten. Im gemeinsamen Button-Editor Hell als Anfangswert, Prüfraster, Dunkel und eigene Farbe ergänzt. Separate Browserpräferenz, unverändert über Neuladen; kein Bestandteil des Rezepts. Zuständige Vorschau-CSS konsolidiert und zusätzlichen dekorativen Bodenschatten vollständig entfernt. Buttonrenderer, Buttonschatten und Seitenwand unverändert.
- Persönlichen neuen Entwurf „Mein neuer Button“ und abgeleiteten Startseitenentwurf „Guesstimate · Startseite · spielen → Test 1“ festgestellt. Letzterer trägt die Herkunft des Spielen-Buttons aus templates/home.html. Er ist gespeichert, aber es wurde keine Spieleinbindung/Aktivierung vorgenommen. Bestätigt: Die Werkstatt bietet weiterhin nur Entwurfs-/Projektzuordnung; eine allgemeine Aktiv-/Inaktiv-Auswahl fehlt. Nutzer über den derzeit notwendigen ausdrücklichen Auftrag zur lokalen Einbindung informiert.
- Missverständliche Herkunftsbezeichnung „Im Spiel verwendet“ durch „Original aus dem Spiel“ bzw. „Originale aus den Spielen“ im gemeinsamen Bibliotheksfilter ersetzt. Dies bezeichnet die Herkunft der Vorlage, nicht den Aktivzustand eines gespeicherten Entwurfs. Beide Bezeichnungen im persönlichen Bibliotheksbrowser geprüft.
- Persönliche gespeicherte Test-1-Variante nur lesend in zusätzlicher Ansicht geöffnet. Hell, Prüfraster, Dunkel, eigene Farbe und deren Erhaltung nach Neuladen geprüft; Entwurfsstatus blieb gespeicherter Stand. Kein zusätzlicher Vorschau-Bodenschatten mehr vorhanden. JavaScript-Syntax beider geänderten Steuerungen bestanden. Alle neun persönlichen JSON-Dateien nach dem Prüflauf SHA-256-identisch und keine zusätzlichen persönlichen Dateien. Kein Dienstneustart, Projektserverkontakt, keine Veröffentlichung und kein Spielbutton ersetzt. Belege: runtime/button-preview-background-20261028/; Screenshot editor-light.png.

## 28.10.2026 – Leere Editor-Zwischenansicht abgefangen und Test-1-Entwurf wieder geöffnet

- Nutzerbild zeigt uninitialisierte Oberfläche: fehlende Vorschau, Formwerkzeug und Speicherknopf, noch statische Standardbeschriftungen. Beim Weg Bibliothek → Meine Entwürfe → Test 1 → Ansehen → Weitergestalten denselben leeren Zwischenzustand nachgestellt; die Vorschau lud im Prüflauf anschließend vollständig nach. Ein dauerhafter Ladeabbruch auf dem ursprünglichen Nutzerbild ist damit nicht als Ursache belegt.
- Gemeinsamen Editorstart abgesichert: eigene Ladeanzeige, Bearbeitungsfläche erst nach erfolgreicher Initialisierung sichtbar; Import-/Startfehler und Zeitüberschreitung mit Meldung und explizitem erneutem Laden. Fehlender angeforderter gespeicherter Entwurf wird nicht still durch einen neuen Button ersetzt. Keine automatische Wiederholung und keine zweite Editorimplementierung.
- Getrennte lokale Prüfumgebung 8777 mit bewusst erzeugtem Modulfehler: nur Fehlermeldung/Neuladen sichtbar, unfertige Bearbeitung verborgen. Fehler aufgehoben, Neuladen über die angebotene Aktion geprüft, danach neuen Prüfentwurf gespeichert und bestätigten gespeicherten Stand gesehen. Zwölf bestehende Editorprüfungen und JavaScript-Syntax bestanden.
- Persönlichen Test-1-Entwurf auf 8776 über die gemeinsame Bibliothek erneut geöffnet; geladene Vorschau, vier Konturpunkte und sichtbaren Speicherknopf geprüft. Zusätzlich eine vollständige eigenständige Ansicht des gespeicherten Test-1-Entwurfs im In-App-Browser geöffnet und auf dem Speicherschritt offen gelassen; dort keine Browserwarnungen/-fehler. Screenshot runtime/button-editor-startup-20261028/editor-restored.png. Keine persönliche Speicherung ausgelöst; alle neun persönlichen JSON-Dateien SHA-256-identisch, keine zusätzlichen persönlichen Dateien.
- Beim früheren Iframewechsel erneut MutationObserver-Meldungen ohne Quelldatei beobachtet; Herkunft weiterhin ungeklärt, kein Ursachennachweis für den gemeldeten Zustand. Die Steuerung bestehender In-App-Tabs war über die Browseranbindung teilweise nicht verfügbar; neue eigene Prüfseiten funktionierten. Kein Neustart der persönlichen Werkstatt, kein Projektserverkontakt, keine Veröffentlichung und keine Spieleinbindung vorgenommen.


## 28.10.2026 – Buttonmodelle: Verwendungen verwalten und lokale Spieleinbindung

- Nutzer hat die sichtbare Zuordnungsübersicht und die lokale Umsetzung beauftragt. Eigene vollständige Buttonentwürfe bieten jetzt „Verwendungen verwalten“ in der Bibliotheksvorschau und im Speicherschritt des gemeinsamen Editors. Derselbe Dialog wird eigenständig und eingebettet verwendet; im Iframe öffnet ihn die Hauptseite. Entwurf und aktueller zugeordneter Stand mit Datum, Spiel-/Suchfilter, aufklappbare Einsatzstellen und explizite Übernehmen-/Original-Aktionen sind sichtbar.
- Die bereits freigegebene Startseitenaktion bleibt eine atomare Gruppe aus Spielen/Fortsetzen und Ergebnis. Ansichten derselben physischen Quelle bleiben zusammen. Gleich aussehende unabhängige Quellen werden nicht still zusammengelegt: beispielsweise Nachholen kann zusätzlich gewählt werden. Bestand weiterhin 144 Ansichten/85 Gestaltungsmodelle; für die Zuordnung 140 Einsatzgruppen, davon 112 angeschlossen und 28 Spezialkomponenten bzw. uneindeutige Quellen gesperrt. Keine vollständige Abnahme aller Ziele behauptet.
- Neue lokale Zuordnungsstände liegen fortlaufend unter design-library/button-usage/. Ein Revisionsabgleich verhindert das Überschreiben neuerer Zuordnungen durch alte Dialoge. Originalvorlagen und gespeicherte Entwürfe werden nicht überschrieben; nicht ausgewählte Gruppen bleiben erhalten. Neue Entwurfsstände werden bewusst erneut zugeordnet.
- Das normale lokale Hauptspiel registriert die Einbindung über deploy/run_local.py und workshop_buttons.py. Templates werden nur beim Laden im Speicher markiert. Der ursprüngliche Knopf behält Formularwerte, Aktionen und dynamische Beschriftung; sichtbare Modelle verwenden denselben Werkstattrenderer und skalieren als Ganzes. Zurücksetzen entfernt die Darstellung und zeigt das Original wieder. Die räumliche Conquest-Arbeitsvorschau auf 8767 ist separat und noch nicht angeschlossen; Hauptspielstart über Guesstimate-starten.cmd --main-game auf 8765. app.py, Originaltemplates, der gemeinsame Grundrenderer und die erzeugten Buttonaufnahmen wurden gegenüber dem Arbeitsbeginn nicht verändert. Darstellungs-/Zuordnungsabrufe schreiben keine Anmeldungen oder Spielhistorie.
- Sichtbar mit eigener Prüfbibliothek auf 8777 und echtem Hauptspiel auf 8778 mit getrennter Datenbank/Testkonto geprüft: Startaktion öffnete die Fragerunde; abgeschlossener Zustand öffnete das Ergebnis. Zusätzlich gewählter Nachholbutton behielt den aktuellen Tageszähler und startete die korrekte Nachholrunde. Übernehmen und Wiederherstellen erschienen automatisch auf einer bereits geöffneten Spielseite; abschließend 0 Ersatzdarstellungen/0 versteckte Originale und ursprünglicher Ergebnislink wieder vorhanden. Testzuordnungen anschließend leer. Bibliothekszugang und Zugang aus dem eingebetteten Editor ebenfalls sichtbar geprüft.
- Persönliche Bibliothek auf 8776 mit Test-1-Entwurf geöffnet und gekoppelte Startgruppe ausgeklappt. Keine persönliche Zuordnung angewendet; aktueller persönlicher Zuordnungsstand leer. Alle neun vorhandenen persönlichen JSON-Dateien SHA-256-identisch, keine neuen persönlichen JSON-Dateien; app.py exakt identisch mit Arbeitsbeginn. Persönliche Spiel-/Kontendaten wurden nicht geöffnet oder verändert. Persönliches Hauptspiel nicht gestartet. Nur die lokale Werkstatt neu geladen, kein Projektserverkontakt und keine Veröffentlichung.
- Prüfungen: 21 Tests für Zuordnungen, Medien und gemeinsame Werkstatt; zwölf lokale Startertests; zwölf bestehende Editorprüfungen im Verlauf dieser Arbeit sowie JavaScript-Syntax und gemeinsame Geometrie erfolgreich. Nachweise: runtime/button-usage-20261028/tests-latest.txt, verification.json und verwendungen-persoenlich.png. Bedienweg und Prüfgrenzen: docs/BUTTON_VERWENDUNGEN.md. Nächster persönlicher Versuch: Test 1 in der geöffneten Übersicht zuordnen, normales lokales Hauptspiel starten und die gewünschte Gestaltung selbst prüfen.


## 28.10.2026 – Buttonverwendungen mit sichtbarem Einsatzort

- Nutzerrückmeldung: Namen allein reichen zur Wahl der Einsatzorte nicht aus. Jede anschließbare Einsatzgruppe bietet jetzt „Im Spiel ansehen“. Die originale Spielseite mit neutralen Beispieldaten zeigt den betreffenden Knopf orange markiert, einschließlich wiederholter Knöpfe derselben Quelle. Verknüpfte Spielzustände sind in der Vorschau umschaltbar. Die Gruppe kann direkt neben der Ansicht ausgewählt oder entfernt werden; gespeichert wird weiterhin erst mit „Zuordnung übernehmen“ in der Übersicht. Die Textliste heißt „Einsatzstellen auflisten“.
- Vorschau aus tatsächlichen Templates/Stilen und den bestehenden neutralen Werkstattkontexten erzeugt. Kein zweiter Nachbau der Spielseiten. Ganze Seite proportional eingepasst, Ziel in den sichtbaren Ausschnitt gerückt; passende Shop-/Profilbereiche und Dialoge geöffnet. Originale Spielskripte, Formularaktionen und Sitzungstoken entfernt. Nur ein eigener Vorschauhelfer für Zustandsöffnung, Scrollposition und Markierung läuft. Keine persönlichen Spieldaten geladen, keine Spiele gestartet oder persönlichen Zuordnungen angewendet.
- Alle 116 Ansichten der 112 verfügbaren Einsatzgruppen auf erfolgreiche Wiedergabe mit Zielmarkierung und ursprünglichen Stilen geprüft. Zehn Tests für Kontext und Zuordnung bestanden; nach ergänzter Fehlerbehandlung vier Kontexttests inklusive beider Werkstattdienste und Fehlerantwort bestanden; alle verfügbaren Ansichten nach abschließender Zustandskorrektur nochmals erfolgreich gerendert. JavaScript-/Python-Syntax bestanden. Keine vollständige visuelle Abnahme aller Ansichten behauptet.
- In getrennter Bibliothek sichtbar geprüft: Startseite mit Spielen und Ergebnis, Nachholknopf im ursprünglichen Dialog, Gruppe direkt an der Vorschau auswählen und mit unveränderter Auswahl zur Übersicht zurückkehren; Shop-Hintergrundbereich mit beiden wiederholten Kaufknöpfen markiert. Persönliche Werkstatt neu geladen und Test 1 mit markiertem Spielen-Knopf im Kontext geöffnet/offen gelassen. Alle neun persönlichen JSON-Dateien gegenüber Arbeitsbeginn identisch, keine zusätzlichen persönlichen Dateien oder gespeicherten Zuordnungen. Originaltemplates und Buttonrenderer unverändert. Getrennter Prüfserver anschließend beendet, persönliche Werkstatt auf 8776 erreichbar.
- Die schon zuvor beobachteten MutationObserver-Meldungen ohne Quelldatei traten in der Browseranbindung erneut auf. Ursache weiterhin ungeprüft; sichtbare Kontextdarstellung und Auswahl funktionierten. Nachweise unter runtime/button-context-20261028/ einschließlich einsatzort-persoenlich.png und verification.json. Bedienweg in docs/BUTTON_VERWENDUNGEN.md aktualisiert. Kein Projektserverkontakt und keine Veröffentlichung.


## 28.10.2026 – Schriftwahl mit Fett/Kursiv und persönliche Spielzuordnung geprüft

- Nutzerrückmeldung zur wirkungsarmen Beschriftungswirkung umgesetzt: separate Wirkungs-/Schriftkopplung im Editor ausgeblendet und durch die gängigen unabhängigen Schalter Fett und Kursiv ergänzt. Neue Schriftwahl setzt die frühere Beschriftungswirkung ausdrücklich auf Klar/manuelle Wahl zurück. Alte gespeicherte Werte bleiben erhalten; eine vorhandene alte Wirkung wird erklärt, ohne beim Laden einen neuen Entwurfsstand zu erzeugen.
- Kreide über die direkte Schriftwahl „Kreideschrift · Cabin Sketch“. Offiziellen Google-Fonts-Bestand und OFL-Lizenz recherchiert. Die bereits vorhandenen fetten Cabin-Sketch-/Stardos-Stencil-Dateien bleiben erhalten; deren reguläre Schnitte samt Lizenz lokal unter assets/fonts ergänzt und in PROVENANCE.json mit URL/Prüfsumme dokumentiert. Streifenmaske der neuen Kreidewahl entfernt; gezeichneter Strich stammt aus der Schriftdatei. Keine Systemschriften installiert. Fehlende echte Kursivschnitte werden bei ausdrücklicher Formatierung vom Browser geneigt.
- Optional boolesche Rezeptfelder font_bold/font_italic: fehlen sie, bleibt die bisherige Darstellung erhalten. Validierung lehnt Zahlen/Zeichenketten statt Bool ab. Gemeinsamer Medienadapter für Editor, Bibliothek und lokale Spieleinbindung verwendet; grundlegender Buttonrenderer, Spieltemplates, source IDs und gekoppelte Alt-Medienstile erhalten. 144 Originalrezepte weiterhin wertgleich validiert. Neue Formatierung speichert und übergibt sich mit dem Entwurf, ohne ältere Dateien umzuschreiben.
- Drei neue Typografieprüfungen, elf Medien-/Zuordnungsprüfungen und zwölf bisherige Editorprüfungen erfolgreich; außerdem JavaScript-Syntax und bestehende Geometrie-/Proportionsprüfungen. Sichtbar in getrennter Werkstatt: Cabin Sketch normal 400/fett 700, Kursiv ein/aus, gemeinsame Formatierung speichern und nach Neuladen erhalten; regulärer Stardos-Stencil-Schnitt geladen und Schriftstil normal bestätigt. Prüfdaten ausschließlich runtime/button-type-20261028/qa-*. Persönliche Werkstatt und lokales Hauptspiel anschließend mit neuem Validator/Adapter geladen; getrennter Prüfserver wieder beendet.
- Persönliche gespeicherte Zuordnung tatsächlich vorhanden: Entwurf 96ba2a2cf7334b7e94309cc57f41040b („Guesstimate · Startseite · spielen →“) in vier Gruppen: Startseitenaktion Spielen/Ergebnis, innerer Nachholdialog, Weiter-zur-Frage, nächsten Tag nachholen. Normales lokales Hauptspiel war zunächst geschlossen; auf ausdrücklichen Prüfauftrag gestartet. Im angemeldeten persönlichen Hauptspiel auf 8765 den Spielen-Button sichtbar mit genau diesem Rezept, Schriftfarbe #485714 und Seitenwand #3b4710 nachgewiesen, auch nach Aktualisierung des Adapters. Weitere drei Gruppen vom Spiel ausgeliefert; deren jeweilige Spielzustände in dieser Prüfung nicht durchgespielt. Keine Runde gestartet, weiterhin null Versuche.
- Der normale Spielstart/das Öffnen hat automatisch die heutige Tagesrunde mit fünf Fragenreservierungen vorbereitet und den heutigen Login vermerkt: daily_rounds +1, question_usage +5, login_days +1. Keine bestehenden Datensätze entfernt oder geändert; übrige 25 Anwendungstabellen einschließlich Konten/Versuche unverändert. Vorab lokale Sicherung und Tabellenprüfsummen unter runtime/button-type-20261028/game-before.*. Diese normale Initialisierung wurde nicht durch manuelle Datenbankänderungen zurückgesetzt. Keine Behauptung eines vollständig unveränderten Datenbankinhalts.
- Alle elf persönlichen JSON-Dateien einschließlich Entwürfen und Zuordnung gegenüber Beginn dieser Arbeit identisch, keine neuen persönlichen JSON-Dateien und keine weitere Zuordnung angewendet. Eine zusätzliche ungespeicherte Kreide-Vorschau mit Fett/Kursiv in der persönlichen Werkstatt geöffnet; tatsächliches Hauptspiel offen gelassen. Screenshots kreide-fett-kursiv.png und zuordnung-im-spiel.png, Prüfzusammenfassung verification.json. Kein Projektserverkontakt, keine Veröffentlichung.
- Nächster persönlicher Bedienversuch: neue Schriftwahl und Fett/Kursiv abnehmen. Danach praktische Prüfung des Fenster-/Dialogeditors mit vergleichbarem Ablauf aus Gestalten, Speichern und Einsatzort ansehen; noch keine neue Fensterarbeit begonnen.


## 28.10.2026 – Erster Fenstereditor und Nutzen weiterer Editoren

- Nutzer hat nach Abschluss des Buttondurchgangs die praktische Fensterarbeit begonnen. Aktueller Ausgangszustand geprüft: Fenster waren bis dahin nur Bibliothek/Vorschau. Als erster bearbeitbarer Fall jetzt der vorhandene Guesstimate-Nachholdialog; andere Fenstermodelle bleiben weiterhin zur Ansicht und Projektauswahl verfügbar, ihre Editoren sind nicht als fertig erklärt.
- Neue Fensterwerkstatt im gemeinsamen Editor: Form → Farben → Speichern. Ganze Komponente proportional skalieren (60–140 %), Ecken und Rahmenstärke gestalten; Fläche, Überschrift, Erklärungstext und Rahmenfarbe unabhängig wählen. Originalwerte einzeln zurücksetzen, Originalvergleich ohne Verlust der eigenen Einstellungen, separate helle/dunkle/gerasterte Arbeitsfläche. Originalmarkup und Stile werden vom bestehenden SourceWindows-Renderer wiederverwendet, keine zweite Innenkomposition und keine neuen Childbuttons. Texte und Aktionen bleiben aus der Vorlage; Vorschau ist inert und ohne Spiel-/Kontenzugriff.
- Eigene Entwürfe werden fortlaufend unter design-library/recipes/window-workshop/ gespeichert, mit Quelle, Originalsnapshot, Einstellungen und Vorgänger. Bibliothek → Fenster → Meine Entwürfe zeigt dieselbe Gestaltung; Weitergestalten und genaue Entwurfsadresse unterstützen Wiederöffnen. Ungespeicherte Werte bleiben pro Browsertab zur Wiederaufnahme erhalten. Projektmappen und Übergabe übernehmen die genaue eingefrorene Variante. Speichern ersetzt noch kein Fenster im Spiel; für Fenster wurde keine Spielaktivierung eingerichtet oder ausgeführt.
- 24 Tests für Fensterentwürfe, vorhandene Fenster und gemeinsame Werkstatt bestanden; JavaScript-/Python-Syntax bestanden. Sichtbar in getrennter Prüfbibliothek 110 %, Rundung 8 px, Rahmen 2 px sowie vier eigene Farben geprüft. Originalvergleich zeigte wieder 24 px und ursprüngliches Blau; Einzelrücksetzen der Überschrift ließ die übrigen Farben erhalten. Ungespeicherte Wiederaufnahme, Speichern, Neuladen, Bibliotheksvorschau, Weitergestalten und Neubeginn aus der Originalvorlage einschließlich bereinigter Entwurfsadresse geprüft. Gespeicherte Prüfvariante window-79de9923b55d45c1b5c31f1a37095118 bleibt ausschließlich im getrennten Prüfbestand.
- Persönliche Werkstatt auf 8776 mit denselben Ablagen neu geladen und Fenstereditor mit unveränderter Originalvorlage auf Form geöffnet/offen gelassen. Keine persönliche Fensterdatei gespeichert. Alle elf vorhandenen persönlichen JSON-Dateien SHA-256-identisch, keine zusätzlichen persönlichen JSON-Dateien. Originaltemplates und laufendes persönliches Spiel nicht verändert; keine Fenster-/Buttonzuordnung angewendet. Getrennter Prüfserver beendet. Nachweise: runtime/window-editor-20261028/tests.txt, verification.json, fenster-editor-persoenlich.png.
- Nutzerkorrektur für das weitere Vorgehen: Nach dem Fensterdurchgang zuerst bewerten, wo ein eigener Editor überhaupt sinnvoll ist. Vorläufige Empfehlung in der gemeinsamen README dokumentiert: Gestaltungseditoren für Buttons/Fenster und bei Bedarf eigene Kartendesigns; gemeinsames Bildwerkzeug für Bildmaterial; vorhandene Modelle mit Eigenschaften bei Würfeln/Brettern/Figuren; Vorlagen und ausgewählte Eigenschaften bei Eingaben/Anzeigen/Pulten/Lobbys; Auswahl und Formatierung/Lautstärke für Schriften/Klänge. Dies ist ein Vorschlag, keine Freigabe für weitere automatische Editorentwicklung. Bestehende Werkzeuge erhalten. Keine neue Bestandsaufnahme, kein Projektserverkontakt und keine Veröffentlichung.


## 28.10.2026 – Brettereditor, Einordnung der Bereiche und sichtbare Größen

- Nutzer hat eigene Editoren für Bretter, Figuren, Karten und Avatare ausdrücklich festgelegt und den Beginn am Brettereditor beauftragt. Die vorherige Einordnung war ein Vorschlag; sie ist entsprechend präzisiert. Alle 17 Bereiche im aktuellen Werkstattbestand durchgesehen und den sinnvollen Umfang in docs/EDITOR_BEREICHE_2026-10-28.md festgehalten. Buttons/Fenster und die vier genannten Bereiche als Gestaltungswerkzeuge; bei den übrigen Bereichen Auswahl, gemeinsames Bildwerkzeug oder Eigenschaften an gemeinsamen Vorlagen empfohlen. Keine Umsetzung der Figuren-/Karten-/Avatar-Erweiterungen behauptet. Persönliche Fensterprüfung vom Nutzer auf später verschoben.
- Offizielle Dokumentation von Tabletop Simulator (Custom Board, Custom Deck) und Tabletopia (Game Board) tatsächlich recherchiert. Brettbild, getrennte Maße/Form/Dicke und optionale Gitter als Grundlage; Reihenfolge Form & Größe → Oberfläche & Bild → Felder → Speichern aus diesen Quellen und den eigenen Bedienversuchen abgeleitet. Quellen und Grenzen im Bereichsdokument verlinkt.
- Erster eigener Brettereditor in derselben Werkstatt: neues rechteckiges oder rundes Brett, 2D/3D, Maße, Rahmen und Dicke, unabhängige Fläche-/Seitenwand-/Feldfarben, Oberfläche, vorhandenes oder lokal importiertes Bild. Bild proportional vollständig einpassen oder ausdrücklich beschneiden; optional Zweifarbenmuster, Gitter oder keine Felder, Reihen/Spalten und Deckkraft getrennt. Ein verdecktes Brettbild durch deckende Felder wird erklärt. Alte Feldbrettkonfigurationen lassen sich als eigener Stand beginnen; die vorhandenen Conquest-, Playtable- und Würfeltisch-Originale bleiben daneben in der Bibliothek. Keine freien Konturen, Einrastpunkte oder Spielregelbearbeitung eingerichtet.
- Bestehende buildBoard-Fabrik um Authoring-Eigenschaften erweitert; alte Rezepte behalten ihre bisherige Geometrie. Vorschau, gespeicherte Bibliotheksansicht und Weitergestalten verwenden dieselbe Fabrik und board-stage-Seite. Weiterhin genau zwei Grundvarianten 2D/3D, Gestaltung und Bilder bleiben Eigenschaften bzw. Varianten. Eigene Entwürfe append-only unter design-library/recipes/board-workshop/, mit Vorgänger und überprüftem Bildsnapshot. Projektmappe/Übergabe halten die genaue Auswahl fest; ungespeicherte Werte pro Browsertab wiederaufnehmbar. Kein Spielbrett ersetzt oder einem bestehenden Spiel zugeordnet.
- Rückmeldung während des Durchgangs: Zahlen allein sind für Größen außer Schriftgrößen wenig hilfreich. Im Brettereditor daraufhin Größenregler für Breite/Durchmesser, Höhe, Rahmen und Dicke ergänzt; genaue Zahlen unter Genau einstellen. Standardvorschau jetzt mit festem Maßstab und zuschaltbaren Vergleichshilfen: Beispielkarte 6 × 9 cm und Figur 4 cm hoch, aus denselben vorhandenen Karten-/Figurenfabriken. Nur Vorschauhilfen, keine zusätzliche Spielaufstellung und nicht Bestandteil gespeicherter Bretter oder Projektmappen. Ganzes Brett einpassen aktiviert die automatische Einpassung ausdrücklich; Ansicht näher/weiter bleibt ebenfalls außerhalb des Entwurfs. Zahlen sind virtuelle Beispielmaße, keine Monitor-Zentimeterkalibrierung. Das Prinzip gilt für weitere Editoren; bestehende andere Editoren wurden nicht pauschal umgebaut.
- 21 Tests für neue Brettentwürfe, bisherige Bretter und gemeinsame Werkstatt erfolgreich; JavaScript-/Python-Syntax bestanden. Sichtbar mit getrennten Daten geprüft: Maße/Farben, Weltbild mit eigenem Gitter und 40 Prozent Deckkraft, Draufsicht, Speichern, genaue Adresse neu laden, Bibliotheksansicht/Weitergestalten, rundes Brett ohne Felder, lokaler PNG-Import und gespeicherter 2D-Folgestand. Größenvergleich anschließend bei Breite 40 und 100 mit unverändertem Karten-/Figurenmaß sichtbar geprüft. Nach letzter Vorschauänderung Dienste mit aktuellen Quellprüfsummen vollständig neu geladen. Kein vollständiger visueller Durchgang aller Originalflächen behauptet.
- Persönliche Werkstatt 8776 mit frischem ungespeichertem Brett auf Form geöffnet. Alle elf vorhandenen persönlichen JSON-Dateien gegenüber Beginn SHA-256-identisch, keine Ergänzungen. Keine persönliche Brettdatei gespeichert. Prüfstände board-14d02d6812844b5b99fd577c59e09db1 und board-e8ada86ae175441680056b741cc03112 samt Bild ausschließlich im getrennten Bestand runtime/board-editor-20261028/qa-library. Nutzer hat diese Prüfwerkstatt während der Arbeit geöffnet; deshalb 8777 und die beiden Prüfstände bewusst erhalten, alle vier dortigen Dateien nach der Größenrückmeldung identisch. Geöffnete Entwürfe nicht gelöscht. Persönliches Hauptspiel nicht angefasst, keine Konten-/Partie-/Fragenabfrage, kein Projektserverkontakt und keine Veröffentlichung.
- Nachweise: runtime/board-editor-20261028/tests-final.txt, verification.json, brettereditor-persoenlich.png sowie groessenvergleich-40.png und groessenvergleich-100.png. Bedienweg und Einordnung in der gemeinsamen README und docs/EDITOR_BEREICHE_2026-10-28.md. Nächster persönlicher Versuch: im Brettereditor Größe/Form verändern, Fläche oder Bild und Felder wählen, eigenen Stand in der persönlichen Bibliothek speichern. Weitere Editoren danach nach Bedarf gestalten; keine automatische Entwicklung aller 17 Bereiche.


## 28.10.2026 – Figureneditor mit direktem Größenvergleich

- Nutzer hat die Fortsetzung am Figureneditor beauftragt und einen direkt sichtbaren Größenvergleich ausdrücklich verlangt. Erster Gestaltungsumfang für die vorhandenen Schachfiguren und Damesteine: Form → Größe & Proportionen → Material & Farben → Speichern. Zusammengesetzte Conquest-Marke bleibt zunächst unverändertes Bibliotheksoriginal; kein allgemeiner freier 3D-Modellierer und keine Integration neuer Figurensätze in bestehende Spiele behauptet.
- Figurenfabrik models.js/buildPiece unverändert wiederverwendet. Gesamtgröße skaliert den vollständigen Baustein proportional; Körperhöhe, Fuß, Körper und Kopf werden über die vorhandenen Modellparameter gestaltet. Bei Damesteinen keine wirkungslosen Kopf-/Körperbreitenregler; bei 2D nur Größe und Markenbreite, räumliche Material-/Proportionsregler verborgen. Beide Seitenfarben unabhängig wählbar. Änderungen gelten für die ganze Satzfamilie, Vorschaurolle und Seite sind eigene Ansichtswahlen.
- Standardvorschau mit festem Maßstab: bearbeitete Figuren gegenüber grauer Referenzfigur (4 cm hoch) und Beispielkarte (6 × 9 cm). Für 2D eine 3 cm breite Vergleichsmarke. Alle Vergleichsobjekte verwenden dieselben bisherigen Fabriken. Vergleich, Rolle, Seitenansicht, Zoom, Drehung und Draufsicht bleiben reine Vorschau und außerhalb gespeicherter Datensätze/Projektmappen. Alles einpassen aktiviert automatische Einpassung ausdrücklich; genaue Prozentwerte unter Genau einstellen. Virtuelle Beispielmaße, keine Monitor-Zentimeterkalibrierung.
- Neue Figurenrezepte append-only in design-library/recipes/piece-workshop/, mit Vorgänger und geprüften Einstellungen. Eigene Sätze in der gemeinsamen Bibliothek, als exakte Variante weitergestaltbar und Projektmappen/Übergaben zuordenbar. Alte eigene Rezepte und die sieben Quellkonfigurationen erhalten. Originale von Schach und Dame können als eigener Satz begonnen werden. Ungespeicherte Werte bleiben pro Browsertab erhalten. Keine persönliche Speicherung oder Spieleinbindung ausgelöst.
- 27 Tests für Figurenentwürfe, vorhandene Spielsteine, Bretterentwürfe und gemeinsame Werkstatt bestanden; Python-/JavaScript-Syntax bestanden. Sichtbar mit separater Prüfbibliothek 8779: Gesamtgröße 60/150 bei unveränderter Vergleichsfigur, Körperhöhe 125 %, Fuß 80 %, Kopf 85 %, eigene grün-/messingfarbene Seiten und Material geprüft. Gespeicherten Schachsatz nach Neuladen genau wieder geöffnet, Bibliotheksansicht und Weitergestalten geprüft. Danach flache Damesteine mit passenden Reglern und Referenzmarke angesehen und als Folgestand gespeichert. Projektübergabe und unveränderte frühere Versionen zusätzlich in Tests nachgewiesen. Keine vollständige visuelle Abnahme aller Rollen-/Materialkombinationen behauptet.
- Prüfsätze piece-53a03be2df59429c81aee103b3dfdc54 und piece-1a66c1263fe34e529aba8891188afdf4 liegen ausschließlich unter runtime/piece-editor-20261028/qa-library. Eigene zusätzliche Figuren-Prüfansicht geschlossen und zugehöriger Dienst beendet. Die zuvor vom Nutzer geöffnete Brett-Prüfwerkstatt 8777 samt ihrem Bestand blieb erhalten und erhielt dieselben neuen Werkzeugfunktionen. Persönliche Werkstatt 8776 neu geladen und in eigener zusätzlicher Ansicht bei Größe & Proportionen geöffnet/offen gelassen. Frühere Browserbindung war nicht steuerbar; bestehende Nutzeransichten deshalb nicht navigiert oder geschlossen.
- Alle 17 zu Beginn gesicherten Dateien aus persönlicher Bibliothek und geöffneter Brett-Prüfbibliothek SHA-256-identisch, keine Ergänzungen. Keine persönliche Figurenrezeptdatei gespeichert. Hauptspiel, Konten, Spielstände und Fragenbanken nicht geöffnet oder verändert; kein Projektserverkontakt, keine Veröffentlichung. Nachweise: runtime/piece-editor-20261028/tests.txt, verification.json, groessenvergleich-60.png, groessenvergleich-150.png und figureneditor-persoenlich.png. Bedienweg und Grenzen in SPIELSTEINE_GRUNDLAGEN.md, gemeinsamer README und Editorbereichsübersicht fortgeschrieben.


## 28.10.2026 – Eigene Kartensätze mit gemeinsamem Design und Größenvergleich

- Fortsetzung nach dem Figureneditor: erster Karteneditor für eigene endliche Sätze, entsprechend dem bereits festgelegten Editorbereich Karten. Ablauf Format & Größe → Vorderseite → Rückseite → Karteninhalt → Speichern. Zwei Ausführungen (flach/räumlich), Formatauswahl und Größenregler mit fester Vergleichskarte 6 × 9 cm. Vergleich, Zoom, Auswahl der Kartenseite und schräge Ansicht bleiben reine Vorschau. Alles einpassen aktiviert automatische Einpassung ausdrücklich.
- Gemeinsame Vorder-/Rückseitengestaltung: Fläche, Schrift, Vorderseitenrahmen und Zeichenfarbe unabhängig; eigene Rückseitenfläche und Rahmen-/Musterfarbe, Rauten oder nur Rahmen. Kartenkante in 3D. Titel, Text und Zeichen je Satzmitglied bearbeiten; neue Karten, Duplikate und Entfernen innerhalb des ungespeicherten Satzes, letzter Bestandteil geschützt. 1–100 eigene Karten pro Satz. Beim Inhaltsschritt wird die Vorderseite gezeigt, beim Speichern beide Seiten. Ungespeicherter Satz einschließlich zuletzt bearbeiteter Karte pro Browsertab wiederaufnehmbar.
- Bestehende kanonische Grundlagen wiederverwendet: flache Karte aus originalCard, ursprünglicher importierter 3D-Körper und seine Materialien als gemeinsame Funktionen in card-comparison-v1/body.js ausgelagert. Der bisherige Vergleich und der neue Editor benutzen dieselben Funktionen. Beide eigenen Darstellungsarten benutzen dieselben erzeugten Flächen aus der vorhandenen cardTexture-Funktion; neue Farben und formatabhängige Textabstände ergänzend, frühere Rezeptwerte behalten ihre bisherigen Vorgaben. Keine neue Kopie des Kartenkörpers. Ursprüngliche Modelldatei unverändert; Positionen, UVs, 44 Dreiecke, Maße und Materialseiten mit Node-Prüfung nachgewiesen.
- Eigene Sätze fortlaufend unter design-library/recipes/card-workshop/, vollständige Mitglieder plus Gestaltung, Vorgänger und Speicherzeitpunkt. Bibliothek zeigt die konkrete Variante mit Mitgliedsauswahl; Weitergestalten, Projektmappe und Übergabe halten den ganzen Satz fest. Originale Standardsätze, Conquest-Karten und ältere allgemeine Kartenvorlagen bleiben erhalten. Alte allgemeine Vorlagen bleiben mit bisherigem Renderer ansehbar und können als eigener Satz begonnen werden. Eigene Bilder, freie Layouts, Tabellenimport und Bearbeitung bestehender Standardsätze bleiben offen. Keine Fragenbanken kopiert und keinen Kartensatz im Spiel aktiviert.
- Prüfungen: erster breiter Lauf 29 von 30 Pythonprüfungen erfolgreich; ein bestehender Fremdursprung-HTTP-Test brach mit WinError 10053 ab. Dieser Test danach zusammen mit den sechs abschließend angepassten Kartentests erfolgreich ausgeführt (7/7, erwartete Ablehnung mit HTTP 403). Damit alle 30 unterschiedlichen geprüften Fälle erfolgreich abgedeckt; kein vollständig erfolgreicher einzelner 30er-Lauf behauptet. Separater Node-Test für gemeinsamen Körper, Positionen, UVs und Materialseiten bestanden. JavaScript-/Python-Syntax bestanden. Prüfungen erfassen eigene und ursprüngliche Karten, Karteninhalte, Figurenentwürfe und gemeinsame Werkstatt.
- Sichtbar in getrennter Bibliothek 8779 geprüft: Kartenhöhe 6/12 bei gleichbleibender Referenz, unabhängige Farben, Rückseite ohne Rauten, individuelle Inhalte bei drei Karten, Hinzufügen/Duplizieren/Entfernen, ungespeicherte Wiederaufnahme mit aktiver Karte, vollständiges Speichern und genaue Adresse erneut laden. Bibliotheksvorschau des dritten Satzmitglieds und Weitergestalten geprüft. Flaches Querformat angesehen, Titelabstand vom Rahmen korrigiert und erneut sichtbar geprüft. Bestehende räumliche Herz-7-Karte nach der gemeinsamen Auslagerung sichtbar mit ursprünglichem Motiv und fertiger Vorschau geprüft. Keine vollständige Abnahme aller 100 Karten oder aller alten Satzvarianten behauptet.
- Prüfsätze deck-d4f0a3007db541d198b9a72764c83665 (3D) und deck-c3c5f7f60c964b128811f768ebcfbc77 (2D-Querformat, mit Vorgänger) enthalten jeweils dieselben drei Karten und liegen ausschließlich im getrennten Prüfbestand runtime/card-editor-20261028/qa-library. Eigene Prüfansichten geschlossen und zusätzlicher Dienst 8779 beendet. Nutzer-Prüfwerkstatt 8777 mit ihrem bestehenden Brettbestand erhalten, persönliche Werkstatt 8776 mit denselben Ablagen und aktuellen Quellen neu geladen. Persönlichen Karteneditor mit ungespeicherter Ausgangsgestaltung geöffnet/offen gelassen. Bestehende Nutzeransichten nicht navigiert oder geschlossen.
- Alle 20 geschützten Ausgangsdateien aus persönlicher Bibliothek, geöffneter Brett-Prüfbibliothek, ursprünglichem Karten-JavaScript/-CSS und Modelldatei SHA-256-identisch; keine zusätzlichen Dateien in den geschützten Bibliotheken. Keine persönliche Kartensatzdatei gespeichert. Hauptspiel, Konten, Spielstände und Fragenbanken nicht geöffnet oder verändert; kein Projektserverkontakt, keine Veröffentlichung. Nachweise unter runtime/card-editor-20261028/: tests.txt, tests-final-targeted.txt, verification.json, groessenvergleich-6.png, groessenvergleich-12.png, querformat-geprueft.png und karteneditor-persoenlich.png. Bedienweg und Grenzen in KARTEN_GRUNDLAGEN.md, gemeinsamer README und Editorbereichsübersicht fortgeschrieben.


## 28.10.2026 – Eigener Bildavatar mit Ausschnitt, Rahmen und sichtbarem Größenvergleich

- Fortsetzung nach dem Karteneditor: Avatare besitzen den Ablauf Bild wählen → Ausschnitt → Rahmen → Größe → Speichern. Vorhandene Rasterbilder oder eigener PNG-/JPEG-/WebP-Import, quadratischer Ausschnitt mit direkter Rückmeldung in der Spieleranzeige. Ursprüngliche Rahmenform, Kreis, abgerundetes Quadrat und Quadrat; unabhängige Rahmenfarbe, Hintergrund und Stärkeregler. Größe als sichtbarer Regler, Prozentwerte ergänzend unter Genau einstellen.
- Das gemeinsame ImageEditor-Werkzeug um einbettbaren Zuschnitt mit festem Verhältnis und getrennten Kennungen/Zwischenspeichern erweitert; keine zweite Zuschnittsteuerung. Dieselbe Bildverarbeitung für Vorschau und gespeicherten Ausschnitt. Avatarvorschau und Bibliotheksansicht benutzen dieselbe neue Vorschauseite sowie die unveränderte createPlayerPortrait-Fabrik und deren CSS. Ganze Spieleranzeige proportional über ihr Schriftmaß skaliert; feste Vergleichsanzeige daneben und kanonische Conquest-Anzeige mit neutralen Truppen-/Länder-/Kartenwerten darunter. Öffentliche Ausgangsausschnitte aus der bestehenden register_portraits-Funktion übernommen, ohne app.py auszuführen oder eine Datenbank zu öffnen. Keine kopierte Spielerkomposition.
- Vollständige Entwürfe append-only unter design-library/recipes/avatar-workshop/: Originalquelle und SHA-256, quadratischer Ausschnitt, Rahmen und Größe, Name, Vorgänger und Zeitpunkt. Originalbilder und frühere Bildvarianten bleiben unverändert. Bibliothek zeigt Entwurfsnamen; Weitergestalten, genaue Adresse, Projektmappe und Übergabe erhalten die konkrete Variante. Ungespeicherter Entwurf pro Browsertab wiederaufnehmbar. Importierte oder in anderen Werkzeugen hinzugefügte Bilder werden in der Bildauswahl nachgeladen. SVG-Zuschnitt, freie Figurenmodellierung/Ausstattung und Profilzuordnung bleiben offen. Speichern ändert keinen Profilavatar.
- Abschließender vollständiger Lauf: 37 Pythonprüfungen für Avatarentwürfe, gemeinsame Bildwerkstatt, Werkstattablage und bestehende Spieleranzeigen erfolgreich. Zuvor gefundene veraltete Erwartung von 15 Werkstattbereichen auf den vorhandenen Stand von 17 korrigiert; keine Produktionsfunktion dafür verändert. JavaScript-/Python-Syntax bestanden. Geschützte Originaldateien der Spielerfabrik, CSS und Python-Porträtzuordnung unverändert.
- Sichtbar auf 8779 in getrennter Prüfbibliothek: Ausschnitt per Pfeiltasten von 288/395 auf 298/405 verschoben, runder messingfarbener Rahmen mit blaugrauem Hintergrund und Stärke 5, Größe 60/150 bei unverändertem Vergleich geprüft. Ganze Spieleranzeige 13,2/33 px gegenüber fester Referenz 22 px; Kontextanzeige entsprechend 8,4/21 px. Ungespeicherte Wiederaufnahme, Speichern, genaue Adresse neu laden, Bibliotheksvorschau und Weitergestalten geprüft. Zweiten kleinen Entwurf mit abgerundetem Quadrat als Folgestand gespeichert; erster Stand und Ausschnitt erhalten. Wechsel zur allgemeinen Bildwerkstatt mit anderer Bildquelle geprüft, keine doppelten Elementkennungen, Avatar bleibt unabhängig. Keine vollständige visuelle Abnahme aller Motive/Rahmen behauptet; eigener Dateiimport zusätzlich in API-/Bildprüfungen, nicht im Dateiauswahldialog getestet.
- Prüfavatare avatar-a729d0702c244f1dad888e65ee438ecf und avatar-57cb10b1363a41c7a244d8292379551a ausschließlich unter runtime/avatar-editor-20261028/qa-library. Eigene Prüfansicht geschlossen und eigener Dienst 8779 beendet. Persönliche Werkstatt 8776 (PID 23204) und weiterhin vom Nutzer verwendete Brett-Prüfwerkstatt 8777 (PID 8760) mit unveränderten Ablagen neu geladen. Persönlichen Avatarbereich in eigener zusätzlicher Ansicht bei Größe geöffnet/offen gelassen; keine Browserwarnungen/-fehler protokolliert. Bestehende Nutzeransichten nicht navigiert oder geschlossen.
- Alle 20 geschützten Ausgangsdateien aus persönlicher Bibliothek, geöffneter Brett-Prüfbibliothek und ursprünglicher Spielerkomponente SHA-256-identisch; keine zusätzlichen Dateien in den geschützten Bibliotheken. Keine persönliche Avatarrezeptdatei gespeichert. Hauptspiel, Konten, Spielstände und Fragenbanken nicht geöffnet oder verändert; kein Projektserverkontakt, keine Veröffentlichung. Nachweise: runtime/avatar-editor-20261028/tests-final.txt, verification.json, groessenvergleich-60.png, groessenvergleich-150.png und avatareditor-persoenlich.png. Bedienweg und Grenzen in docs/AVATAR_EDITOR.md, gemeinsamer README und Editorbereichsübersicht fortgeschrieben. Nächster sinnvoller Schritt: persönliche praktische Prüfung der vier neu begonnenen Bereiche.


## 29.10.2026 – Profile für angemeldete Mitspieler sichtbar (lokal)

- Nutzerwunsch nach der Avatarwerkstatt: auch Profile anderer Spieler ansehen. Neue Übersicht /spieler mit Namenssuche und Außenansicht /spieler/<id>, nur für angemeldete Spieler. Bestehendes Profil bleibt Ausrüstung/Einstellungen; neue Links Mein öffentliches Profil und Spieler entdecken. Namen der Daily-Ranglisten öffnen das Profil; gemeinsame Lobbys bieten Profil ansehen für echte Spieler, keine Profilverknüpfung für virtuelle Armeen.
- Außenansicht zeigt ausgerüsteten Avatar, Pult, Hintergrund und Spruch, Gesamtpunkte/Rang, abgeschlossene Daily-Quizrunden, Tagesbestwert/Durchschnitt sowie Titel. Keine Käufe, Inventar, iKuh-Kontostände, Anmeldeinformationen oder Entwicklereinstellungen. Laufende Ergebnisse ausgeschlossen, neutraler Startavatar mit bestehendem öffentlichen Bild. Persönliche PINs nicht gelesen/geändert. Seiten privat/nicht zwischengespeichert und nicht indexierbar; Präfixe erhalten. Profilbesuche/Suche lösen auch bei neuem Sitzungstag keine Datenbankänderung aus, durch Vergleich aller Tabellen geprüft.
- Eine kanonische Komposition: profile_window unverändert wiederverwendet, Pokalschrank aus eigener Profilvorlage in gemeinsames _profile_trophies.html ausgelagert, Spielerübersicht verwendet player_identity. Namenslink als optionaler Parameter an derselben Identitätskomponente. Neue Profile in SourcePlayers erfasst, Pokalschrankquelle in SourceIndicators angepasst. Alle 27 dynamischen Spielerbeispiele mit aktuellen app.py-Prüfsummen neu erzeugt. Keine CSS-Korrekturblöcke an bestehenden Komponenten; neue Seitengestaltung in public-profiles.css.
- Prüfungen: 16 Profil-/Fenster-/Lobbytests erfolgreich (darunter sieben neue Fälle für Anmeldung, Feldgrenze, neutrale Darstellung, aktuelle Ausstattung, Suche/Präfix, Ranglisten-/Lobbyzugänge und ausschließlich lesende Besuche). Weiterer Lauf mit 28 Fällen für Spieler-/Anzeigequellen, bestehende Buttonzuordnungen und eigene Ausrüstung: 26 bestanden; zwei Bestandsannahmen auf 16 statt 14 Komponentenverwendungen und vorhandene 17 statt 15 Werkstattbereiche korrigiert, beide anschließend erfolgreich nachgeprüft. Damit 44 unterschiedliche Fälle erfolgreich abgedeckt, kein einzelner vollständig erfolgreicher 44er-Lauf behauptet. Python-Syntax bestanden. Bestehende ResourceWarnings für nicht geschlossene Testdatei/-socket beobachtet; kein neuer Funktionsfehler daraus abgeleitet.
- Sichtbar auf getrennter Testanwendung 8778 mit erfundenen Profilen geprüft: eigene Profilseite → Spieler entdecken, Suche nach mira mit genau einem Treffer, fremdes Profil mit eigenem Bergsee-Hintergrund/Kupferpult/Waschbär/Spruch, 755 Punkten, zwei abgeschlossenen Runden, Bestwert 395, Durchschnitt 378 und zwei Tagessiegen. Suchfeldbreite nach sichtbarer Prüfung korrigiert und erneut geprüft. Keine Browserwarnungen/-fehler in abschließender Testansicht. Screenshot runtime/public-profiles-20261029/profil-mitspielerin.png.
- Lokales Hauptspiel 8765 (PID 23632), persönliche Werkstatt 8776 (abschließend PID 17064) und vom Nutzer verwendete Brett-Prüfwerkstatt 8777 (abschließend PID 13840) nach eindeutiger Prozess-/Ablageprüfung neu geladen. Hauptspiel-Health ok, beide Werkstätten ohne unlesbare Dateien und mit zwei neuen Profilverwendungen. Nach letzter Textkorrektur Werkstattaufnahmen neu geladen; beide neuen Profilvorschauen auf beiden Ports mit HTTP 200 geprüft. Alle 18 geschützten Nicht-Datenbankdateien einschließlich persönlicher Entwürfe unverändert; keine zusätzlichen Dateien in den geschützten Bibliotheken. Alle 28 Anwendungstabellen des persönlichen Spiels nach dem Neustart unverändert. Nur der automatische sqlite_sequence-Zähler für login_days stieg von 28 auf 29; kein Login-Datensatz hinzugekommen und keine manuelle Rücksetzung. Sicherung vor Neustart unter runtime/public-profiles-20261029/game-before.sqlite3.
- Fehler bei erster Testanmeldung: Standardcookie auf 127.0.0.1 verwendet, wodurch eine vorhandene lokale Anmeldung abgelöst worden sein kann. Korrigiert: Vorschau eigener Cookie guesstimate-profile-preview und Browseransicht auf localhost:8778. Persönliches Spiel /spieler öffnete anschließend die Anmeldeseite. Nutzer ausdrücklich informiert und zur eigenen erneuten Anmeldung eingeladen; Prüfung mit seinem bestehenden Konto steht noch aus. Keine automatische Anmeldung, keine Zugangsdaten angefordert. Persönliche Anmeldeseite und erfundenes Beispielprofil offen gelassen; bestehende Nutzeransichten nicht navigiert/geschlossen. Prüfserver 8778 (PID 23064) für die sichtbare Testansicht weiter aktiv, mit getrennter Datenbank.
- Kein Projektserverkontakt und keine Veröffentlichung. Öffentliche Serverfassung nicht aktualisiert. Bedienweg, Umfang und Prüfgrenzen in docs/SPIELERPROFILE.md; Prüfberichte und verification.json unter runtime/public-profiles-20261029/.

## 29.10.2026 – Fenster zurückgestellt; praktische Prüfung bei Brettern fortsetzen

- Nutzer stellt den Nutzen eines eigenen Fenstereditors erneut infrage und die Fenster unter „Überhaupt sinnvoll?“ vorerst zurück. Bisher ist nur der Nachholdialog bearbeitbar; dies erfüllt die allgemeine Fensteraufgabe nicht. Keine weitere Fensterentwicklung beauftragt, vorhandener Stand bleibt erhalten. Einordnung in docs/EDITOR_BEREICHE_2026-10-28.md entsprechend geändert.
- Nächster Editor in der vereinbarten Reihenfolge: Bretter, danach Figuren/Spielsteine, Karten und Avatare. Erste Fassungen sind vorhanden; die persönliche praktische Prüfung ist der nächste Schritt. In diesem Durchgang nur die Entscheidung dokumentiert, keine Programm- oder Spieldaten geändert.


## 29.10.2026 – Werkstatt auf Button-Editor und Bibliotheken begrenzt

- Ausdrückliche neue Nutzerentscheidung ersetzt die bisherige Editorplanung und Reihenfolge: Nur der Button-Editor bleibt; der Navigationspunkt heißt Editor statt Gestalten. Sämtliche anderen Editoroberflächen sowie die Projektmappe aus der Werkstatt entfernt. Keine weitere Editorentwicklung beauftragt. Bibliotheken für spätere Recherchen erhalten. Alte Planung in docs/EDITOR_BEREICHE_2026-10-28.md und Werkstatt-README ausdrücklich als ersetzt markiert.
- Nicht nur Navigationslinks verborgen: Einbindung der anderen Editorprogramme und ihre Oberflächen aus index.html/workshop.js entfernt, Projektmappenansichten/-dialoge/-Zuordnungen entfernt, Bearbeitungsaktionen auf Buttons begrenzt. Alle 16 anderen Editoradressen öffnen ihre jeweilige Bibliothek; alte Projektadressen öffnen die Buttonbibliothek. Katalog meldet ausschließlich Buttons als Editor; sämtliche anderen Bibliothekselemente sind als nicht bearbeitbar ausgewiesen. Material & Ansicht bleibt eine lesende Referenz ohne Projektmappenweg. Bibliotheksvorschauen und gespeicherte Inhalte bleiben verfügbar; alte Quelldateien und Ablagedaten nicht gelöscht.
- Persönliche Werkstatt 8776 mit denselben Ablagen neu geladen, abschließend PID 4036. Aktuelle API: 17 Bibliotheksbereiche, 941 Einträge, keine unlesbaren Dateien. Alle 941 Elementkennungen vor/nach identisch. Alle 13 Dateien der persönlichen design-library SHA-256-identisch; keine zusätzlichen Dateien. Keine persönlichen Entwürfe oder Projektmappen geschrieben/gelöscht. Hauptspiel, Konten, Spielstände und Fragenbanken nicht geändert; ausschließlich lokal, kein Projektserverkontakt.
- Browserprüfung: sämtliche 16 entfernten Editoradressen zeigen ihre Bibliothek, keinen Editor und keinen Bearbeitungslink. Projektmappenadresse führt zur Bibliothek, keine Projektlinks mehr. Conquest-Truppenmarke weiterhin in der Bibliothek geöffnet und sichtbar geprüft. Material-/Ansichtsreferenz ohne Projektmappenverweis. Verbleibender Button-Editor in frischer persönlicher Ansicht vollständig mit fünf Schritten sichtbar; keine Warnungen/Fehler in dieser abschließenden Ansicht. Screenshot runtime/workshop-reduction-20261029/werkstatt-bereinigt.png. Zwischenzeitlich einmal dynamischer Modul-Ladefehler nach Neuladen einer älteren Prüfansicht; Ursache nicht bestimmt, Fehleransicht geschlossen. Frische geprüfte Ansicht offen gelassen.
- JavaScript- und Python-Syntax geprüft. 13 Ablageprüfungen erfolgreich; fünf HTTPprüfungen zunächst durch lokale Socket-Zugriffsrechte blockiert. Mit lokalem Netzwerkzugriff vier erfolgreich, dabei vorhandenen Fehler in alter Lobbyvorschau gefunden: neutrales Spielerprofil wurde fälschlich als statische Datei aufgelöst. Vorschau-Link neutralisiert und der betroffene fünfte HTTPfall anschließend erfolgreich geprüft. Damit 18 verschiedene vorhandene Prüffälle abgedeckt, kein einzelner erfolgreicher Gesamtlauf behauptet. Prüfdaten ausschließlich in getrennten Laufzeitablagen. Nachweise: verification.json, retired-routes.json, http-tests.txt, lobby-preview-test.txt unter runtime/workshop-reduction-20261029/.

## 29.10.2026 – Spielen zurückgesetzt und falsches Wiederöffnen im Buttoneditor behoben

- Nutzerfehler nachvollzogen: Startseitenaktion war dem gespeicherten Entwurf 96ba2a2cf7334b7e94309cc57f41040b zugeordnet (Inter, Schriftgröße 160 %, Schriftfarbe #485714). Der Einstieg über den Spielbutton lud dennoch die ursprüngliche Quellvorlage mit font=source, ohne die aktive Zuordnung zu lesen. Frühere Speicher-/Zuordnungsprüfungen hatten diesen konkreten Wiederöffnungsweg nicht abgesichert.
- Auf Nutzerwunsch ausschließlich die gekoppelte Startseitenaktion Spielen/Fortsetzen/Ergebnis über die vorhandene Zuordnungsfunktion auf Original zurückgesetzt. Im angemeldeten persönlichen Hauptspiel auf 8765 sichtbar geprüft; keine Runde gestartet. Die drei weiteren Zuordnungen desselben Entwurfs blieben erhalten, ebenso alle gespeicherten Entwürfe. Zurücksetzung als neuer Zuordnungsstand, keine Historie überschrieben oder gelöscht.
- Gemeinsame Auflösung in ButtonUsage ergänzt: Der Editor lädt den exakt an der Einsatzstelle zugeordneten gespeicherten Stand, auch bei neuerer unzugeordneter Version. Beide lokalen Werkstätten verwenden denselben Ladeweg. Ohne Zuordnung wird das Original geladen; unlesbare zugeordnete Entwürfe verursachen eine ausdrückliche Fehlermeldung. Originalreferenzen und Originalvergleich bleiben unverändert. Bibliotheksaktion heißt nun Aktuellen Spielbutton bearbeiten.
- Vollständiger Lauf aller neun gezielten Tests in tests.test_button_usage erfolgreich, einschließlich neuer Fälle für gekoppelte Zustände, exakten aktiven statt neueren Stand, Rücksetzung, unlesbaren Entwurf sowie echte HTTPaufrufe beider Werkstätten. JavaScript-/Python-Syntax und git diff --check geprüft. Browserprüfung in getrennter Werkstatt 8779 über Bibliothek → Startseitenaktion → Bearbeiten: tatsächlich aktiver Entwurf mit Inter, 160 % und #485714 sichtbar, obwohl neuerer anderer Entwurf gespeichert war. Anschließend derselbe Ladeweg in persönlicher Werkstatt 8776 an einer erhaltenen Zuordnung geprüft: genaue gespeicherte Kennung in der Editoradresse, Schriftwerte und gespeicherter Stand sichtbar. Keine persönliche Bearbeitung gespeichert.
- Persönliche Werkstätten 8771 und 8776 mit denselben Ablagen neu geladen. Der bisherige gemeinsame Starter musste zuvor beendet werden, damit dessen Überwachung die übrigen Werkstätten nicht mitbeendet; neuer Starter 22892. Comic-Tafel 8770 und Conquest-Archiv 8773 weiterverwendet. Hauptspielprozess 5728 nicht neu gestartet; Health ok. Getrennte Prüfansichten geschlossen und eigener Prüfprozess nach Abschluss beendet.
- Alle 14 zu Beginn erfassten persönlichen Bibliotheksdateien SHA-256-identisch. Zusätzlich zum Rücksetzungsstand erschien während der Arbeit ein weiterer persönlicher Entwurf 9dbf91d83ac34588a82ac9e9f54443ae (Gemeinsam · Rangliste · tag); dieser wurde erhalten. Keine Konten, Spielergebnisse, Fragen oder Nutzungshistorie bearbeitet. Kein Projektserverkontakt, keine Veröffentlichung. Nachweise unter runtime/button-editor-reopen-20261029/: mismatch-before.json, usage-before.json, usage-after-reset.json, tests.txt, verification.json und Screenshots. Diese Prüfung betrifft den gemeldeten Ladefehler; keine Gesamtabnahme sämtlicher Editorfunktionen behauptet.

## 29.10.2026 – Bibliotheksabsturz nach gültiger Buttonspeicherung korrigiert

- Nutzer meldet leere Werkstatt mit Failed to fetch. Aktuell nachgewiesen: Dienst und /api/recipes erreichbar, /api/library bricht jedoch mit KeyError: settings in ProjectLibrary.button_model ab. Gültiger eigener Entwurf 9dbf91d83ac34588a82ac9e9f54443ae ist ein vollständig bearbeitbarer Browserimport, dessen ursprüngliche Spielquelle nur Markup und kein vorab aufgenommenes Messprofil liefert. Der Modellvergleich setzte fälschlich bei jeder ursprünglichen Quelle settings voraus. Dies ist ein weiterer, durch den vorherigen Wiederöffnungsfix nicht behobener Fehler.
- Vergleich in workspace_store.py auf tatsächlich vorhandene Ausgangseinstellungen begrenzt. Importierte Entwürfe ohne vorab vermessene Quellvorlage erhalten weiterhin eine aus ihren eigenen Gestaltungswerten abgeleitete Modellkennung. Kein Entwurf entfernt, umgeschrieben oder übersprungen, kein Fehler durch leere Bibliothek verdeckt.
- Elf gezielte Tests in einem vollständigen Lauf erfolgreich (32,895 s): neuer Fall mit Markupquelle → vollständigem Browserimport → Speichern zweier Stände → /api/library und /api/recipes mit exakten Schnappschüssen; bestehender Modellvergleich sowie alle neun Zuordnungs-/Editorprüfungen. Python-Syntax und git diff --check erfolgreich.
- Persönliche Werkstatt 8776 mit derselben Ablage neu geladen; übrige lokale Dienste weiterverwendet. Neuer gemeinsamer Starter 12856. /api/library anschließend HTTP 200, 943 Elemente, zehn gespeicherte Buttoneinträge, null unlesbare Dateien. Alle 16 zu Beginn erfassten persönlichen Bibliotheksdateien SHA-256-identisch, einschließlich der beiden am 29.10. gespeicherten Entwürfe. Keine persönlichen Daten gespeichert oder zugeordnet, keine Spiel-/Konto-/Fragen-/Nutzungsdaten bearbeitet und kein Projektserverkontakt.
- Persönliche Bibliothek im Browser mit Meine Entwürfe vollständig sichtbar geprüft, danach gespeicherten Spielen-Entwurf e5f98f6ff59c4162b2b71c4b47862e75 mit gespeichertem Stand wieder geöffnet. Nutzer bediente währenddessen die Ansichten weiter; abschließend persönliche Werkstatt mit Entwurf 9dbf91d83ac34588a82ac9e9f54443ae sowie Hauptspiel offen. Zusätzliche Browser-Speicherprüfung in getrennter Kopie nicht als abgeschlossen gewertet: während der Bedienung wechselte der geladene Stand, deshalb keine weiteren Eingaben gegen diese Ansicht. Prüfkopie auf 8779 als solche erläutert, nach Schließen ihrer Browseransicht beendet. Keine vollständige visuelle Abnahme aller Editorabläufe behauptet.
- Nachweise unter runtime/button-library-load-20261029/: traceback-before.txt, workspace_store-before.py, personal-before.json, tests.txt, verification.json, persoenliche-bibliothek.png. Der aktuelle persönliche Bearbeitungsstand bleibt beim Nutzer.


## 29.10.2026 – Black Jack: lokale Spielfeldvorschau, freigegebener Flyer und Klangabgleich

- Blackjack-Regelwerk aus dem Downloadordner gelesen und Tischansicht aus Spielerperspektive anhand offizieller Spielbank-/Anbieterquellen recherchiert. Vorschau mit Bank gegenüber, Kartenschlitten rechts, Ablage links, offenen Spielerhänden und eigener Bedienleiste. S17, sechs Decks, Hole Card, 3:2 sowie die Split-/Aufgeben-Details sind vorläufige Tischvorschläge, keine abgeschlossene Regelfreigabe.
- Nutzerentscheidung: einfache Anzeigekarten verwenden. Keine weitere Kartenphysik-Suche oder Physikumsetzung. Vorschau verwendet vorhandene Kenney-Kartengrafiken; bestehende Kartenmodelle und andere Spiele nicht geändert. Waschbär als künftig beweglicher/sprechender Geber besprochen, noch nicht umgesetzt.
- Freigegebener Flyer: static/carousel-blackjack-v2.png, Waschbär am grünen Tisch, auf Nutzerkorrektur Geldscheine links und Chip-Vorrat rechts ergänzt. In der fünften Hauptseitenanzeige statt der Jenny-Glückwünsche und als neue Kartentischkachel eingetragen. Bilddatei und Titel bleiben getrennt. Eine gemeinsame blackjack_flyer_copy-Komposition mit lokalem Cinzel und goldener Titelwirkung für beide Verwendungen. Kachel heißt Spielfeldvorschau und führt zur separaten Oberfläche; kein fertiges Mehrspielerspiel behauptet.
- Persönliches Buttonrezept Black Jack, Kennung 132b54b7b45b42ef9c4b9d6ad3375355, über den unveränderten Werkstatt-Renderer in der Vorschau eingesetzt. Beschriftungen Karte ziehen/Hit, Halten/Stand, Teilen/Split, Verdoppeln/Double Down, Versicherung/Insurance und Aufgeben/Surrender. Rezeptdatei SHA-256-identisch zum gelesenen Stand bb4abe42ec4e894e3f449e406e5f082eaa96dba5aed06bbfdc220a6d635bd394.
- Auf Lautstärkerückmeldung acht vorhandene Klangdateien einzeln gemessen und nur ihre Wiedergabe in der Blackjack-Vorschau angeglichen. Kurzer Klick angehoben, Bestätigung sowie Sieg/Niederlage um rund 13,5–13,8 dB abgesenkt; begrenzte Signalspitzen und gemeinsame Begrenzung bei überlappenden Klängen. Originale Klangdateien unverändert. Bericht runtime/blackjack-20261029/sound-balance.json.
- Zusätzlich tatsächlich beobachtete Mehrfachauslösung korrigiert: zurückgemeldeter eigener widgetState startete den Bankzug und Kartengeräusch erneut. Revisions-/Signaturvergleich verhindert dieses Echo; Wiederaufnahme eines Bankzugs erfolgt ohne erneute Klangauslösung und mit genau einem Timer. Separater Node-Regressionsnachweis audio-echo-check.mjs bestanden. Im laufenden lokalen Browser Verlust-, Gewinn- und Aufgebenablauf mit laufender Audiowiedergabe, einmaligen Kartengeräuschen und passenden Signalen geprüft. Seit dem korrigierten Quellenstand keine neuen Browserwarnungen/-fehler beobachtet. Nachweis sound-browser-check.json.
- Flyer mit tatsächlich geladener Cinzel-Schrift sichtbar in eigener Ansicht geprüft und für den Nutzer offen gelassen; Nachweis runtime/blackjack-20261029/flyer-mit-schrift.png. Zwei gezielte bestehende Vorlagentests für Hauptseite und Kartentische bestanden; Fragenbibliotheksprüfung erfolgreich. Angemeldete Hauptseite und Kachel noch nicht abschließend visuell abgenommen. Keine öffentliche Serveraktivierung.
- Bearbeitbare Vorschau dauerhaft im Projekt unter offline-preview/blackjack-v1/blackjack-tisch.html, Herkunft/Verwendungen in source.json; ausgelieferte Ansicht static/blackjack-vorschau.html und Antwortkopie im Visualisierungsordner daraus abgeleitet. Beispiele laufen ausschließlich im Browser. Keine Konten, realen Spielstände oder Fragen-/Nutzungsdaten bearbeitet. Grafiküberarbeitung mit dem Nutzer ist der nächste Schritt.

## 29.10.2026 – Black-Jack-Flyer freigegeben und neuer Button mit Cinzel

- Nutzer bestätigt den Flyer einschließlich der gezeigten Cinzel-Titelschrift ausdrücklich mit „Der Flyer ist ok“. Keine weitere Flyeränderung in diesem Schritt.
- Neuesten persönlichen Black-Jack-Button 72beaf357d3742c1bb5a0633ac4e2603 aus der aktuellen Bibliothek gelesen: eigene Kontur mit neun Punkten, Seidenmatt, 80 % Formhöhe, 150 % Schriftgröße und geänderte Farben/Tiefe. Auf Nutzerauftrag ausschließlich die Schrift auf cinzel geändert und über den kanonischen RecipeStore als Folgestand af65d52a1fbd4deba1bf41b612704b52 gespeichert. Alle 13 vorher vorhandenen persönlichen Buttondateien SHA-256-identisch; keine frühere Fassung überschrieben.
- Cinzel war bereits lokal enthalten und im gemeinsamen Renderer unterstützt; vorhandene Kennung und Fontdatei wiederverwendet. Im Editor jetzt als „Cinzel · Black Jack“ in der Gruppe „Spielschriften“ sichtbar. Keine doppelte Fontkennung, keine neue Darstellungskopie und keine Veränderung anderer Schriftwerte oder Standardbuttons. Die Fontdatei ist bytegleich mit der Flyer-Schrift.
- Vorschauquelle offline-preview/blackjack-v1/blackjack-tisch.html verwendet den neuen Entwurf für sämtliche sechs Aktionen. Antwortkopie und ausgelieferte static/blackjack-vorschau.html aktualisiert; source.json verweist auf den Folgestand. Schriftfarbe/Fläche/Kontur bleiben vom Nutzerstand übernommen. Lokale Editoransicht und Spielfeld tatsächlich im Browser geprüft: Cinzel geladen, alle sechs Beschriftungen passen, keine Warnungen/Fehler. Gespeicherter Entwurf lässt sich mit exakter Schriftwahl erneut öffnen. Nachweise runtime/blackjack-20261029/button-cinzel-editor.png, button-cinzel-spielfeld.png und button-cinzel-browser.json.
- Gezielter isolierter Speichern-/Wiederöffnenvergleich des konkreten Cinzel-Entwurfs bestanden, ebenso Fontidentität, Erhalt aller älteren Rezepte, JavaScript-Syntax und State-Echo-Regressionsprüfung. Breiterer Lauf bestehender Module test_button_typography/test_button_media nicht erfolgreich: acht Fälle, davon zwei bestanden, fünf Fehler und eine fehlgeschlagene Erwartung. Veraltete Quellvorlagen ohne settings/Annahme von 144 statt aktuell 145 Quellen sowie gesperrter lokaler HTTPzugriff; keine Tests oder Quellbuttonmodelle dafür umgeschrieben. Kein erfolgreicher Gesamttestlauf behauptet. Prüfbericht button-cinzel.json.
- Ausschließlich lokale Werkstatt und Spielfeldvorschau aktualisiert, keine öffentliche Veröffentlichung, keine Konten/Spielstände/Fragen-/Nutzungsdaten bearbeitet.

## 29.10.2026 – Abweichende Black-Jack-Buttons vollständig korrigiert

- Nutzerrückmeldung und zwei Vergleichsbilder widerlegen die vorherige Behauptung einer vollständig gleichen Darstellung. Tatsächliche Ursachen: Vorschau überschreibt Buttongröße und streckt auf Spaltenbreite; nur die kopierten Grundregeln wurden mit einer ID verstärkt und verdrängen dadurch eigene Rendererregeln für Beschriftung/Seitenwand; unmittelbares Ersetzen der Aktionsleiste bricht die Klickbewegung ab.
- Neueste persönliche Stände berücksichtigt: zunächst 3346060459a648f7835797efbaedb439 mit Courier New, Beschriftung Neue Runde und 110 % Schriftgröße; während der Prüfung Folgestand 4482a87651ca4edfa1e42bad0e872adf mit geänderter Seitenwandfarbe #323b12. Maßgeblich ist abschließend dieser vollständige Nutzerstand, ohne erneutes Erzwingen der vorherigen Cinzel-Wahl. Flyer bleibt unverändert freigegeben. In diesem Schritt keinen Entwurf gespeichert oder überschrieben.
- Größenüberschreibung und Breitenstreckung entfernt. Gemeinsame CSS-Selektoren behalten ihre ursprüngliche Rangfolge, gemeinsame Werkstattquellen für Geometrie, Renderer, Medienerweiterung, Komponente und Bewegung direkt übernommen. Ausgewählter Klang verwendet jetzt die originale Werkstatt-Klangengine samt identischer WAV-Datei, Ausschnitt/Dauer und Lautstärke 40 %. Nur der Dateitransport wird für die selbständige Vorschau durch eingebettete Bytes ersetzt. Normalisierte Spiel-/Kartensignale bleiben erhalten.
- Spielaktion wartet auf das Ende der tatsächlich laufenden Buttonanimation, bevor Aktionsknöpfe ersetzt werden; doppelte Klicks währenddessen lösen keine zweite Aktion aus. Zusätzlich im Browser gefundenen Fehler nach Split korrigiert: Neue Runde setzt den aktiven Handindex auf null zurück. Vorher führte Index 1 bei nur einer neuen Hand zu einem Lesefehler.
- Direkter Browservergleich Neue Runde in Editor/Vorschau beim Stand 334606... ohne Unterschied in allen erhobenen Werten. Abschließend aktuellen Stand 4482... im Editor gegen einen aktiven Spielbutton geprüft: außer dem vorgesehenen Aktionstext keine Unterschiede in Maßen, Kontur, Schriftfamilie/-größe/-gewicht/-stil, Großschreibung, Farbe, Schatten, Oberfläche, Seitenwand, Versatz und Übergängen. Beide 240 × 66,703125 px, Beschriftung 22 px. Alle sechs Spielaktionen mit exakter Rezeptkennung und gleicher Grundgröße geprüft. Neue Runde nach zwei geteilten Händen tatsächlich im Browser erfolgreich; Klangmeldung bestätigt Spielstein setzen bei 40 %. Seit abschließendem Quellenstand keine Browserwarnungen/-fehler beobachtet.
- Nachweise runtime/blackjack-20261029/button-exakt-browser.json, button-exakt-browserfehler.json und button-exakt-spielfeld.png. Gezielte Node-Regressionsprüfung test_preview.mjs erfolgreich: eigenes Zustandsecho ohne Wiederholung, genau ein Bankzug, vollständige Bewegung vor Aktionswechsel, Doppelklickschutz und neue Runde nach Split. Python-Syntax und Quellen-/Rezeptprüfsummen erfolgreich. Gemeinsame Quelldateien nicht verändert; frühere persönliche Entwürfe erhalten. Keine erneute Behauptung eines erfolgreichen breiten Werkstatttestlaufs.
- Reproduzierbare Ableitung in offline-preview/blackjack-v1/build_preview.py, Quellen und gewählter Entwurf in source.json. Bearbeitbare Vorschau, Antwortkopie und lokal ausgelieferte Ansicht aktualisiert. Zusätzliche kurzzeitige Editor-Prüfansicht geschlossen; Nutzereingaben in bestehender Werkstatt nicht verändert. Weiterhin ausschließlich lokales Browserbeispiel, keine Serververöffentlichung oder Bearbeitung echter Konto-/Spiel-/Fragen-/Nutzungsdaten.

## 29.10.2026 – Black Jack: neue Grafikrichtung und schrittweiser offener Tisch

- Neue ausdrückliche Nutzervorgabe: ungefähr 45 Grad Blickwinkel von vorn auf den Tisch, als stünde man davor; Perspektivprinzip aus Risiko/Conquest übernehmen. Alter glaubwürdiger Tisch, materialbetonte Darstellung und warme, gemütliche dunkle Szene, angelehnt an das genannte Gemälde mit kartenspielenden Hunden. Geber hinter dem Tisch, bestehende Spieleravatare an den Plätzen. Freigegebener Flyer bleibt ein eigener bereits abgenommener Stand.
- Blackjack soll ausdrücklich keine Lobby besitzen: ein gemeinsamer Tisch, ein Geber und drei Spielerplätze. Spielbetrieb ab mindestens einem Spieler. Neue Teilnehmer steigen im Rundenrhythmus ein. Diese ausdrückliche Ausnahme gilt für Blackjack; bestehende Lobbyabläufe anderer Spiele bleiben erhalten.
- Aktuelle Quellen geprüft: offline-preview/conquest-2-5d-v1/camera.js ermöglicht den gewünschten Winkel über die vorhandene perspektivische Kamera und passende Bildeinpassung; scene.js enthält den räumlichen Tisch mit Material-/Lichtaufbau. Die vorhandene gemeinsame Spieleranzeige liegt in static/player-portrait.js/.css mit öffentlicher Profildatenquelle in player_portrait.py; Avatarbilder werden nicht neu erfunden oder in Spielstände kopiert.
- Nutzer verlangt ausdrücklich schrittweises Vorgehen. Vorgesehene Reihenfolge: 1) einzelner Bild-/Kompositionsentwurf mit Tisch, Raum, Geber und Platz für drei Teilnehmer; 2) nach gestalterischer Festlegung spielbare Perspektive, Karten/Chips und Bedienung in dieser Szene; 3) vorhandene Avatare und Namen an die Plätze anschließen; 4) gemeinsamen offenen Tischbetrieb und Einstieg zwischen Runden umsetzen, anschließend gezielt mit ein bis drei Spielern prüfen.
- Vorschlag für den späteren Ablauf: freier Platz → Platz nehmen → nächste Einsatzphase abwarten; eine laufende Hand wird durch einen neuen Teilnehmer nicht verändert. Genaue Zeitfenster, Verhalten bei Verbindungsabbruch/Verlassen während einer Hand und Platzreservierung sind vor Umsetzung dieses Schritts noch festzulegen. Bisherige reine Browserbeispiele sind kein gemeinsamer Mehrspielertisch.
- In diesem Planungsschritt ausschließlich Quellen gelesen und Entscheidungen/Reihenfolge dokumentiert. Noch keine neue Raumgrafik erzeugt, keine Perspektive umgestellt und keinen Tischbetrieb implementiert; keine Veröffentlichung oder Änderung echter Konten/Spielstände.

## 29.10.2026 – Black Jack Schritt 1: erster Raum-/Tisch-Bildentwurf

- Auf ausdrücklichen Auftrag ausschließlich den ersten Bildentwurf erstellt: erhöhter schräger Blick vom Spieler auf einen alten massiven Holz-/Ledertisch, dunkler grüner Filz, warm beleuchtetes dunkles Spielzimmer und Waschbär als Geber in dunkler Weste, weißem Hemd und Fliege. Drei freie Einsatzbereiche für spätere Avatareinbindung; Geldscheine, Chipreserve, Kartenschlitten und Ablage als zurückhaltende Details. Bildlich auf ungefähr 45 Grad angelegt, noch keine programmierte Kameraprojektion.
- Mit integrierter Bildgenerierung erstellt und unmittelbar visuell geprüft. Entwurf dauerhaft im Projekt gesichert: offline-preview/blackjack-v1/concepts/blackjack-tisch-45grad-v1.png. Originalausgabe unverändert erhalten; Projektkopie bytegleich. Vollständiger Prompt, Erzeugungsart, Herkunft, Bildmaße und SHA-256 im gleichnamigen JSON. SHA-256: db12feee38e159f796879e4f69c8600a1773aae54baf72638c48aa324ce77cda.
- Entwurf zur gestalterischen Beurteilung gezeigt; noch keine Nutzerfreigabe. Bestehender Flyer, Werkstattbuttons und laufende Spielfeldvorschau nicht ersetzt. Keine Avatareinbindung, Spielmechanik oder gemeinsamer Tischbetrieb in diesem Schritt umgesetzt; keine Veröffentlichung oder Änderung von Konten/Spielständen.

## 29.10.2026 – Black Jack Schritt 2: nahe Sitzansicht spielbar, Original und Flyermotiv gesichert

- Nutzer gibt den Raum-/Tischentwurf ausdrücklich frei und beauftragt die Übertragung ins spielbare Feld, mit näherer Ansicht aus dem zentralen Stuhl. „Spiellobby“ in diesem Zusammenhang als direkte Tischansicht umgesetzt; die vorherige ausdrückliche Vorgabe ohne separate Lobby bleibt bestehen. Schritt 3 (echte Avatare) und Schritt 4 (gemeinsamer Tischbetrieb) weiterhin nicht vorgezogen.
- Freigegebenes Original concepts/blackjack-tisch-45grad-v1.png unverändert erhalten, SHA-256 weiterhin db12feee38e159f796879e4f69c8600a1773aae54baf72638c48aa324ce77cda. Über den vorhandenen ImageStore zusätzlich in der persönlichen Werkstatt gesichert: Hintergrund image-074e7c3530364c7a82a2c51735c5b5cf, daraus vollständige Flyervorlage image-90e77aa2660d4a48b54bc3a2bab3cafb. Sichtbar unter Hintergründe/Flyer mit Suche Black Jack geprüft. Aktiver Hauptseitenflyer nicht ersetzt.
- Nähere Sitzansicht als separate Version mit integrierter Bildgenerierung aus dem freigegebenen Bild abgeleitet: größerer Geber gegenüber, vorderer Tischrand direkt vor dem Spieler, keine verdeckenden Stuhllehnen, freie Filzfläche für Spielkarten. Vollständiges PNG unter static/blackjack-tisch-sitzansicht-v1.png, komprimierte WebP-Darstellung separat. Auch als Hintergrund image-21df0fd0c7a54453a65c66a839392b9f in der Werkstatt. Herkunft, Rollen, Kennungen und vollständiger Bildprompt im Projekt hinterlegt.
- Alten CSS-Tisch samt Symbolgeber vollständig durch zuständige scene.html/scene.css ersetzt. Die feste gemalte Szene trägt eine separate bedienbare Kartenebene mit 45 Grad Neigung, Kontaktschatten und Einsatzmarken. Alle vorhandenen Kenney-Kartengrafiken bytegleich im Vorschaucode erhalten. Keine Physik und kein frei drehbarer 3D-Raum implementiert oder behauptet. Nähere Bildkomposition ist eine eigene Spielansicht, keine Änderung des freigegebenen Originals.
- Persönliches Buttonrezept 4482a87651ca4edfa1e42bad0e872adf, gemeinsamer Renderer, Bewegung und Sound unverändert. Im Browser Neue Runde direkt gegen denselben Werkstattstand verglichen: keine Abweichung in sämtlichen erhobenen Gestaltungs-/Maßwerten, weiterhin 240 × 66,703125 px. Alle sechs Aktionen mit identischer Rezeptkennung. Kartenzug → Bankzug → gewonnene Hand tatsächlich durchgeklickt, anschließend Ausgangsbeispiel wiederhergestellt. Alle Kartenbilder und Hintergrund geladen, Kartenebene zeigt Matrix für exakt 45 Grad, Buttonklang Spielstein setzen bei 40 %, normalisierter Spielklang weiterhin balanced-v1. Keine Browserwarnungen/-fehler in geprüfter Spielansicht.
- Node-Regressionsprüfung für Bank-/Zustandsecho, vollständige Buttonbewegung, Doppelaktionen und neue Runde nach Split bestanden. Erhaltung aller 24 vorher vorhandenen Bibliotheksdateien, Originalbild, Kartengrafiken und Buttonquellen durch Prüfsummen/Inhaltsvergleich bestätigt. Antwortkopie und dauerhaft gespeicherte Quelle identisch, Antwortfragment 765949 Bytes. Browserlayout bei tatsächlich 1218 px Feldbreite geprüft; Versuch einer schmalen Viewportvorgabe änderte die beobachtete Tabgröße nicht und wird ausdrücklich nicht als bestandene schmale Browserprüfung gezählt. Vorgabe zurückgesetzt.
- Nachweise runtime/blackjack-step2-20261029/: sitzansicht-spielbar.png, buttonvergleich.json, browserpruefung.json, dateipruefung.json, werkstatt-hintergruende.png und werkstatt-flyermotiv.png. Bearbeitbare Szenenquellen, Ableitung, Bildprompt und Bibliothekszuordnung dauerhaft im Projekt; lokale Vorschau aktualisiert. Weiterhin Browserbeispiel mit markierten Beispieldaten, keine Mehrspieleraktivierung, kein Projektserverkontakt und keine Bearbeitung realer Konten/Spielstände.

## 29.10.2026 – Black Jack Schritt 3: Avatarplätze, eigener Buttonvorschlag und drei Kartenrücken

- Nutzer beauftragt vorhandene Avatare und Spielernamen an drei Plätzen, bei unveränderter Tischgrafik. Zusätzlich ausdrücklich eigener passender Buttonentwurf unter dem genauen Namen vorschlag black Jack button; dies ersetzt für diese Vorschau die vorherige Vorgabe, ausschließlich den persönlichen grünen Button einzusetzen. Persönliche Vorlagen und Zuordnungen anderer Spiele nicht überschrieben. Während der Arbeit zusätzlich drei passende Kartenrücken und Aufnahme in die Bibliothek beauftragt.
- Ausschließlich lesende Prüfung der lokalen Profildaten: im tatsächlichen Hauptspielbestand runtime/pc-local/quiz.sqlite3 existiert derzeit Stormseed mit Waschbär a05. Über die vorhandene public_portrait-Zuordnung eingebunden. Zwei weitere Plätze zeigen klar als Beispiel gekennzeichnete Mira/Kea und Jan/Fennek mit vorhandenen Kataloggrafiken, keine erfundenen Konten oder realen Teilnehmer behauptet. Gemeinsame createPlayerPortrait-Komponente und deren CSS unverändert übernommen; das Spiel positioniert die ganzen Anzeigen am Holzrand. Die aktuelle Profilzuordnung wird beim Vorschau-Build gelesen, nicht in den Browser-Spielstand kopiert. Echte gemeinsame Sitzvergabe bleibt Schritt 4.
- Separater vollständiger Buttonvorschlag mit Holzoberfläche, goldfarbener Cinzel-Schrift, ruhiger gerundeter Form, 180 ms direkter Druckbewegung und Spielstein-Klang bei 25 %. Erster Stand 763e945ed29b4b65a65a32197843775f, weitergestalteter Stand ce5b017b432b478893fd4b52a2163dac; beide append-only gespeichert. Letzter Stand in der Vorschau sichtbar und im tatsächlichen Buttoneditor mit exaktem Namen und gespeichertem Status geprüft. Direkter Browservergleich: identische Geometrie, Schrift-, Farb- und Bewegungswerte; allein die Transportadresse der gemeinsamen Holztextur unterscheidet sich wegen eingebetteter komprimierter Darstellung. Schrift nur verlustfrei im WOFF-Container verpackt, vollständige TTF-Quelle erhalten.
- Drei Kartenrücken mit integrierter Bildgenerierung entworfen: Samtgrün & Gold (Waschbärmedaillon), Nachtblau & Messing (Kompassornament), Burgunder & Kupfer (Blatt-/Rosettenornamente). Unveränderte Original-PNGs unter static/cards/blackjack/, vollständige Prompts/Herkunft/Prüfsummen in card-back-prompts.json. Aufnahme über vorhandenen ImageStore, dessen unterstützte Bildarten gezielt um Kartenrücken unter cards erweitert wurden. Ein gemeinsamer Bibliotheksbaustein Kartenrücken mit drei Varianten; keine 52 Einzelkarten und keine neuen Spielinhalte erzeugt. Bibliothekskennungen image-86e2940ff66e4d328f0a2401ef30faff, image-a214df2705cd407ab48812ae913c4305, image-c6db34ea93f34ec1bec4bc4bce0ecb22. Im laufenden Werkstattbrowser unter Karten → Kartenrücken einschließlich aller drei Auswahlwerte sichtbar geprüft.
- Rückseiten in der Spielvorschau über Kartenrücken auswählbar. Alle drei tatsächlich ausgewählt, jeweils andere geladene Grafik bei unveränderter Hand; Auswahl wird gespeichert. Alle drei Avatarbilder geladen, Cinzel geladen, genau drei Porträtinstanzen auch nach wiederholtem Rendern. Karte ziehen → Bankzug → Gewinn mit neuem Vorschlagsbutton durchgeklickt, Klangmeldung bestätigt 25 %, Beispiel anschließend wiederhergestellt. Kein neuer Browserfehler in den abschließenden Prüfansichten beobachtet.
- Bestehender Builder-Abschluss nach Einbindung der Porträtkomponente auf eindeutige Tischwurzel begrenzt; vorher konnte deren interne root-Zeile beim erneuten Bauen als falsche Grenze dienen. Wiederholter identischer Build anschließend SHA-256-identisch. Antwortfragment 973761 Bytes, dauerhaft gespeicherte Quelle und Antwortkopie identisch. Elf Bildspeicherprüfungen einschließlich neuem Kartenrücken-Rundlauf erfolgreich; abschließender vollständiger Lauf des Bildmoduls einschließlich lokaler HTTP-Prüfung: zwölf Fälle erfolgreich. Node-Regressionsprüfung für Zustandsecho, Bankzug, Buttonbewegung/Doppelklick, Split-Rundenwechsel und Rückseitenwahl ohne Spielzustandsänderung erfolgreich.
- Lokale Werkstatt wegen neuer Bildart neu geladen: zuvor Werkstatt PID 4212 unter gemeinsamem Starter 12856; vor gezieltem Neustart beide als passende Projektprozesse verifiziert. Alten Starter hart beendet, damit seine Überwachung die übrigen Dienste nicht mitbeendet; anschließend Werkstatt neu gestartet über bisherigen gemeinsamen Startweg. Neuer Starter PID 24288, neue Werkstatt PID 19616. Hauptspiel und übrige Werkstattdienste mit unveränderten Prozesskennungen weiter aktiv. Alle 35 erfassten bisherigen Bibliotheks-/Originaldateien einschließlich Tischbildern und gemeinsamer Porträtkomponente unverändert.
- Nachweise runtime/blackjack-step3-20261029/: button-vergleich.json, dateipruefung.json, ports-before.json/ports-after.json und Browserbilder. Tischgrafik in PNG und WebP bytegleich erhalten. Keine neuen Avatarbilder generiert, keine Konten/Ergebnisse/Nutzungshistorien bearbeitet, keine neue Lobby oder gemeinsame Spielsteuerung umgesetzt und keine Veröffentlichung auf dem Projektserver.

## 29.10.2026 – Black Jack: grüner Kartenrücken gewählt, Alternativen erhalten

- Nutzer wählt Samtgrün & Gold verbindlich als Kartenrücken für Black Jack. Diese Variante ist bereits die Standardwahl der aktuellen Vorschau und wurde nun zusätzlich mit Bibliothekskennung und Prüfsumme in source.json sowie im Motivindex als gewählte Standardvariante dokumentiert.
- Nachtblau & Messing und Burgunder & Kupfer bleiben als gesicherte Alternativen in der Kartenbibliothek. Für alle drei Originaldateien Prüfsummen und vorhandene Bibliotheksdatensätze samt Bilddateien erneut geprüft; keine Bilddateien oder gespeicherten Vorlagen verändert/entfernt.
- Auf Nachfrage zum nächsten Punkt: Schritt 4 ist der gemeinsame Tischbetrieb ohne Lobby, mit einem Geber und drei Plätzen, Runden ab mindestens einem Spieler und Einstieg in der nächsten Einsatzphase. In diesem Durchgang nur die Gestaltungsentscheidung gesichert; keine gemeinsame Spielsteuerung begonnen.

## 30.10.2026 – Black Jack: Buttonvorschlag mit altem dunklem Holz überarbeitet

- Nutzer hat den bisherigen Vorschlagsbutton gefunden, lehnt dessen helle moderne Holzoberfläche aber ausdrücklich als unpassend zum alten dunklen Tisch ab. Diese Rückmeldung betrifft den eigenen Vorschlag, nicht die persönlichen grünen Black-Jack-Buttons. Tischgrafik und zuvor gewählter grüner Kartenrücken bleiben erhalten.
- Mit integrierter Bildgenerierung eine gesonderte dunkle gealterte Nussbaumoberfläche anhand der bestehenden Sitzansicht erzeugt. Unveränderte Originalausgabe dauerhaft unter offline-preview/blackjack-v1/concepts/blackjack-button-walnut-aged-v1.png, vollständiger Prompt, Referenzen und Prüfsummen in button-material.json. Darstellungskopie walnut-aged-v1.webp als eigene Materialwahl wood-aged / Altes dunkles Nussbaumholz in der gemeinsamen Buttonwerkstatt ergänzt. Helles Holz nicht ersetzt; gemeinsamer Renderer, Form und Beschriftungsaufbau bleiben maßgeblich. Neue Materialwahl auch im Materialkatalog samt Holzklang und WebP-Auslieferung berücksichtigt.
- Neuer append-only Folgestand 656dbd73ec9c45a1b86791b2e3a0fcb0 unter dem exakten Namen vorschlag black Jack button; Vorgänger ce5b017b432b478893fd4b52a2163dac bleibt erhalten. Matte dunkle Oberfläche, gedämpfte Messingschrift in Cinzel, dunkle Seitenwand und zurückhaltende warme Kanten. Größe, Kontur, direkte Druckbewegung von 180 ms und Spielstein-Klang bei 25 Prozent unverändert übernommen. Gesperrte Beschriftung auf diesem dunklen Material lesbar gehalten. Kein übertragener Button gestreckt oder separat nachgebaut.
- Vorschau und Antwortkopie aus dem vollständigen Rezept neu abgeleitet. Tatsächlicher Browservergleich von Neue Runde im Spiel und gespeicherten Editor: identische Maße 240 × 73,171875 px, Material, matte Oberfläche, Cinzel 20 px, Schriftfarbe, Kontur, Seitenwand und Flächenkanten. Sechs Aktionsbuttons und neue auswählbare Materialoption im Editor sichtbar geprüft; keine neuen Warnungen/Fehler in beiden Prüftabs. Nachweise runtime/blackjack-dark-button-20261030/spielfeld.png, buttonvergleich.json und dateipruefung.json. Gestaltungsfreigabe durch Nutzer für diese neue Fassung steht aus.
- Alle 44 vorab erfassten persönlichen Bibliotheks-/Originaldateien einschließlich Tischbildern, früheren Rezepten und bisheriger Holztextur SHA-256-identisch. Fragment, Antwortkopie und Quellenmanifest identisch; Buttontextur zusätzlich mit Herkunftspfad und Prüfsumme im Quellenmanifest dokumentiert.
- Gezielte Prüfungen bestanden: sechs Werkstatt-Material-/Projektprüfungen, vorhandene Klangprüfung mit 13 lokalen Klängen sowie Blackjack-Regressionsprüfung für Zustandsecho, Bankzug, vollständige Druckbewegung, doppelte Klicks, neue Runde nach Split und Kartenrückenwahl. Zunächst blockierter lokaler HTTP-Test nach erlaubtem lokalem Zugriff wiederholt; zwei erwartete Materialzahlen von neun auf zehn aktualisiert. Kein breiter Gesamttest behauptet.
- Spiel und Werkstätten waren beim Öffnen nicht gestartet. Regulären lokalen Startweg verborgen gestartet; erster Start durch WinError 10013 blockiert. Nach erlaubtem lokalen Zugriff gestartet; beim Werkstattstart fehlende neue Materialbeschreibung im gemeinsamen Katalog ergänzt, anschließend Dienste bereit. Ausschließlich lokale Vorschau/Werkstatt geändert, keine Serververöffentlichung und kein gemeinsamer Blackjack-Tischbetrieb umgesetzt. Schritt 4 bleibt offen.

## 30.10.2026 – Black Jack Schritt 4, Teil 1: echte gespeicherte Sitzbelegung direkt am Tisch

- Nutzer beauftragt ausdrücklich Platznehmen und echte Sitzbelegung mit vorhandenen Namen/Avataren, ohne Lobby und bei unveränderter Tischgrafik. Direktseite /karten/blackjack im lokalen Hauptspiel ergänzt. Die Black-Jack-Kachel unter Kartentische führt jetzt direkt dorthin. Die ältere /static/blackjack-vorschau.html bleibt das gekennzeichnete Browserbeispiel; echte Tischbelegung wird dort nicht behauptet.
- Neue blackjack_seats-Tabelle in der bestehenden Spieldatenbank mit genau drei zulässigen Platznummern und höchstens einem Platz je Benutzer. Öffnen/Ansehen nimmt keinen Platz ein. Platznehmen und Tisch verlassen verwenden ausschließlich das angemeldete Konto und den vorhandenen CSRF-Schutz. Gleichzeitige Platzansprüche werden per BEGIN IMMEDIATE und Eindeutigkeitsbedingungen entschieden; ein belegter Platz wird nicht überschrieben. Wiederholtes Platznehmen auf demselben Platz ist ohne Zusatzwirkung möglich. Wechsel setzt vorheriges Freigeben voraus; fremde Plätze lassen sich nicht freigeben.
- Profile werden bei jeder Statusabfrage aus users/user_cosmetics gelesen und über public_portrait sowie die unveränderte gemeinsame createPlayerPortrait-Komponente angezeigt. Keine Namen oder Avatarzuordnungen aus Beispielhänden übernommen, keine neuen Konten im persönlichen Bestand angelegt. Genau drei physische Plätze links/Mitte/rechts; eigener Platz sichtbar markiert. Zuschauer sehen die aktuelle Belegung. Neue Abfrage alle 1,5 Sekunden, Verbindungs-/Sitzungsfehler sperren unbelegte Aktionsbestätigung, statt einen Erfolg vorzutäuschen. Neuladen/Schließen gibt einen Platz nicht frei; ausdrückliches Tisch verlassen tut dies. Ablauf bei laufenden Spielrunden bleibt dem nächsten Teil vorbehalten.
- Eine gemeinsame Szenenimplementierung: bisherige scene.html nach templates/_blackjack_table.html und scene.css nach static/blackjack-table.css verlagert. Hauptspiel und Browserbeispiel nutzen dieselbe Komposition mit Moduskonfiguration. Der Builder erzeugt die Werkstattdateien aus unveränderten gemeinsamen Renderer-/Geometrie-/Klangquellen und dem vollständigen Rezept 656dbd73ec9c45a1b86791b2e3a0fcb0. Kein eigener nachgebauter Button und keine zusätzliche Materialvariante. Größe, 180-ms-Druckbewegung, Cinzel und gewählter Spielstein-Klang bei 25 Prozent erhalten. Kartenrunden werden am echten Tisch noch nicht angeboten; dort erscheinen keine Beispielspieler oder Beispielhände. Tischregeln bleiben aufrufbar.
- Zehn gezielte Python-Prüfungen bestanden: sieben neue Sitzbelegungsfälle (Anmeldung/CSRF, drei gültige Plätze, öffentliche aktuelle Profile, Konflikte/Idempotenz, nur eigene Freigabe, Wiederöffnen und zwei gleichzeitige Ansprüche mit genau einem Gewinner) sowie drei betroffene bisherige Kartentisch-Einstiege. Erwartung der Black-Jack-Kachel auf die neue direkte Tischroute aktualisiert. Vorhandene Node-Prüfung für das Browserbeispiel einschließlich Bewegung, Zustandsabgleich, Split-Wechsel und Kartenrückenwahl bestanden. Erste Läufe scheiterten an fehlendem lokalen Bibliothekspfad, gesperrtem System-Temp und einem unvollständigen Prüfprofil; diese Prüfvorbereitung korrigiert. Kein erfolgreicher Gesamttest aller Spiele behauptet.
- Lokales Hauptspiel gezielt neu geladen, vorher Datenbank und 44 persönliche Bibliotheks-/Originaldateien gesichert. Alle vier bestehenden Werkstattprozesse behielten ihre Kennungen. Nach Nutzeranmeldung tatsächliche Browserprüfung mit Stormseed/Waschbär a05: Platz 2 belegt; Neuladen erhält Platz; zweites Fenster zeigt dieselbe Belegung. Freigeben im ersten Fenster erscheint automatisch im zweiten, erneutes Platznehmen im zweiten automatisch im ersten. Kachel → direkter Tisch ebenfalls tatsächlich geprüft. Abschließend Stormseed auf Platz 2, zwei Plätze frei. Keine Browserwarnungen/-fehler in der abschließenden Tischansicht. Mehrere unterschiedliche Spieler und konkurrierende Ansprüche mit getrennten Testclients geprüft; kein abgeschlossener Browserlauf mit drei verschiedenen echten Personen behauptet. Eigener isolierter Testdienst beendet.
- Alle 44 erfassten Bibliotheks-/Originaldateien einschließlich Sitzansicht PNG/WebP, freigegebenem Ursprungsbild, Avatar-Komponente und früheren Buttonentwürfen SHA-256-identisch. Bestehende Datenbankzeilen unverändert. Datenvergleich zeigt zusätzlich zur neuen Sitzbelegung einen regulär neu angelegten Daily-Rundensatz und fünf neue question_usage-Reservierungen beim normalen Hauptseitenaufruf; vorhandene Runden/Reservierungen unverändert. Kein Bearbeiten von Konten, PINs, vorhandenen Spielergebnissen oder altem Nutzungsverlauf für Sitzbelegung/Prüfung. Prüfkonten ausschließlich in getrennten Testdatenbanken.
- Nachweise runtime/blackjack-seating-20261030/: before.sqlite3/after.sqlite3, protected-before.json, dateipruefung.json, ports-before.json/ports-after.json und tisch-echte-sitzbelegung.png. Quellen und Betriebsgrenze in offline-preview/blackjack-v1/README.md dokumentiert. Ausschließlich lokal aktiviert und sichtbar geprüft, keine Veröffentlichung auf /srv/guesstimate. Offen bleiben Teil 2 mit echten Kartenrunden und anschließend Rundenrhythmus/Einstieg zwischen Runden.

## 30.10.2026 – Black Jack Schritt 4, Teil 2: gespeicherte echte Kartenrunden

- Auf „dann mach weiter“ den vereinbarten nächsten Teil mit Einsätzen, Karten und regelgerechten Runden angeschlossen. Vorhandenes Nutzerregelwerk erneut gelesen und die bereits gezeigten Hausvarianten beibehalten. Der direkte gemeinsame Tisch bleibt ohne Lobby. Dieser Teil startet durch Austeilen mit den bis dahin gesetzten Einsätzen; automatische Zeitfenster und Inaktivitätsaktionen bleiben der folgende Schritt.
- blackjack_game.py verwaltet den serverseitigen Stapel aus sechs 52er-Decks, gemischt mit SystemRandom. Zwischen Runden wird bei weniger als 156 verbleibenden Karten neu gemischt. Kein vorgegebener Beispielzug und keine Ersatzkarte bei leerem Stapel. Zustand und Revision liegen in blackjack_game, eigene Tischpunktvorräte in blackjack_balances. Startvorrat 1.000; Einsätze 10–500 in Zehnerschritten, vor Austeilen änderbar/rücknehmbar. Bei unter 10 verfügbaren Tischpunkten ohne gebundenen Einsatz lässt sich ein neuer Vorrat von 1.000 nehmen. Kontowährung, Ranglisten und bisherige Ergebnisse werden dafür nicht verwendet.
- Unterstützt sind Karte ziehen, Halten, Verdoppeln mit genau einer Zusatzkarte, einmaliges Teilen bis zu zwei Händen, Verdoppeln nach Teilen, je eine Zusatzkarte für geteilte Asse, spätes Aufgeben sowie Versicherung zum halben Grundeinsatz bei offenem Bank-Ass. S17, natürliche Blackjacks 3:2, normale Gewinne 1:1, Gleichstand mit Einsatzrückgabe und geteilte 21 als normale Hand umgesetzt. Die Bank prüft Blackjack vor den Spielerzügen, bei Ass nach den Versicherungsentscheidungen aller Beteiligten. Spieler spielen in Platz-/Handreihenfolge; Abrechnung erfolgt genau einmal. Die Bank zieht bei noch auszuspielenden stehenden Händen bis mindestens 17, sonst werden bereits entschiedene Hände ohne unnötige zusätzliche Bankkarten abgerechnet.
- Jede Spielaktion verlangt Anmeldung, CSRF und die aktuelle Tischrevision; Schreibtransaktionen verhindern gleichzeitige doppelte Spielzüge und Auszahlungen. Statusabfragen bleiben lesend und konsistent. Verdeckte Bankkarte und Reststapel werden nicht übertragen. Neu Sitzende warten während einer Hand auf die nächste Einsatzphase. Aufstehen in einer laufenden Runde hält die eigenen Hände, lehnt gegebenenfalls noch nicht gewählte Versicherung ab und reserviert den Platz bis zur regulären Abrechnung; danach wird er frei. Gespeicherte Hände, Vorräte und Ergebnis bleiben beim Neuladen erhalten.
- Vorhandene Kenney-Karten über eine auf genau 52 Kartencodes begrenzte Assetroute eingebunden; grüner Samtgrün-&-Gold-Rücken unverändert. Alle Karten liegen in der gemeinsamen bestehenden 45-Grad-Ebene. Avatare, Szenenkomponente und vollständiges Buttonrezept 656dbd73ec9c45a1b86791b2e3a0fcb0 einschließlich Größe/180-ms-Bewegung/25-Prozent-Klang erhalten. Keine neue Buttongestaltung. Aktionswechsel wartet weiter auf die Druckbewegung. Normale technische Klangdiagnose aus der Spieloberfläche ausgeblendet, Fehler bleiben sichtbar. Acht vorhandene Spielklänge samt ihren angeglichenen Verstärkungen byte-/datenidentisch übernommen; bisherige Hüllkurve und Summenkompressor erhalten. Klang in einem Fenster erst nach dessen eigener Eingabe freigegeben.
- 23 gezielte Python-Prüfungen bestanden: sieben bisherige Sitzfälle und 16 Rundenfälle mit Asswerten, vollständigem 312-Karten-Stapel, S17, Blackjack-/Versicherungs-/Aufgabeauszahlungen, geteilten Assen, Teilen plus Verdoppeln, drei Spielern in Reihenfolge, Neueinstieg, Aufstehen, verdeckten Daten, Guthabenschutz und konkurrierenden identischen Ziehversuchen. Die vorhandene Node-Regressionsprüfung des älteren Browserbeispiels sowie Python-/JavaScript-Syntaxprüfungen bestanden. Kein erfolgreicher Gesamttest aller Spiele oder Browserlauf mit drei verschiedenen echten Personen behauptet.
- Lokales Hauptspiel gezielt neu geladen; alle Werkstattprozesse mit unveränderten Kennungen erhalten. Tatsächliche Browserrunde mit Stormseed auf Platz 2: Einsatz 10, eigene Karten 8 Herz + 2 Kreuz, danach 5 Pik, Halten bei 15; Bank 8 Kreuz + 7 Karo + Ass Herz + 4 Pik = 20. Verlust 10 korrekt abgerechnet, neuer Tischvorrat 990. Zweites Fenster übernahm Einsatz, Austeilen, gezogene Karte und Ergebnis automatisch. Nach Neuladen derselbe gespeicherte Stand, alle Kartenbilder und Avatar geladen, keine abschließenden Browserwarnungen/-fehler. Tisch zeigt Ergebnis der ersten Runde und Neue Runde für die nächste Einsatzphase.
- Vorherige Datenbank gesichert und anschließend vollständig verglichen: keine bestehende Tabelle/Zeile verändert, einschließlich der bisherigen Sitzbelegung, Konten, Ergebnisse und Nutzungsverläufe. Nur die neuen Rundenzustands-/Tischpunktetabellen kamen hinzu. Alle 43 diesmal erfassten Bibliotheks-/Originaldateien einschließlich Tischbildern, Avatar-Komponente und persönlichen Buttonvorlagen SHA-256-identisch. Datenidentität der acht übernommenen Klangaufnahmen und Verstärkungen ebenfalls bestätigt.
- Quellen, Hausregeln und offene Betriebsgrenze in offline-preview/blackjack-v1/README.md beschrieben; source.json unterscheidet nun ausdrücklich das ältere Beispiel und den echten Tisch mit manuell gestarteten Runden. Nachweise runtime/blackjack-rounds-20261030/: before.sqlite3/after.sqlite3, protected-before.json, dateipruefung.json, ports-before.json/ports-after.json, runde-karten-verdeckt.png und runde-abgerechnet.png. Ausschließlich lokal aktiviert und sichtbar geprüft, keine Serververöffentlichung. Weiter offen: automatischer Rundenrhythmus, Einsatz-/Zugzeitfenster und Verhalten bei Inaktivität.

## 30.10.2026 – Black Jack: automatischer Einsatz-/Rundenrhythmus

- Nach Statusabgleich nennt der Nutzer den nächsten Schritt (automatischer Rundenrhythmus) mit „ok“ frei. Diesen Punkt umgesetzt; Zug-/Versicherungszeitlimits und Inaktivitätsregeln nicht vorgezogen. Die bisherigen manuellen Start-/Weiterknöpfe waren ausdrücklich der vorläufige vorherige Ausbaustand und werden im regulären automatischen Offline-Modus jetzt ersetzt.
- Gemeinsame Einsatzphase von 20 Sekunden und Ergebnispause von 10 Sekunden. Nach dem Einsatzfenster teilt der Geber an alle Personen mit gesetztem Einsatz automatisch aus; nach der Abrechnung öffnet sich die nächste Einsatzphase. Neue Teilnehmer werden weiterhin erst bei der nächsten Runde mit eigenem Einsatz aufgenommen. Jede Runde verlangt einen ausdrücklich neu gesetzten Einsatz. Ohne Einsatz endet ein leeres Fenster im Warten; ein neuer Einsatz oder ein neu sitzender Teilnehmer öffnet wieder ein Fenster. Ohne belegten Platz steht die Uhr. Keine selbstständige Wiederholung oder Erhöhung von Einsätzen.
- Servermodul blackjack_clock.py gestartet über den vorhandenen deploy/run_local.py. Die Uhr arbeitet unabhängig von Browserfenstern im lokalen Spielprozess. Fristen liegen mit dem Rundenzustand in SQLite; Neuladen und Dienstneustart setzen sie nicht zurück. Nach langer Unterbrechung erfolgt höchstens der nächste anstehende Wechsel, kein nachträgliches Durchspielen verpasster Runden. Alle Schreibvorgänge bleiben serialisiert; zwei Uhrinstanzen können dieselbe Runde nicht doppelt starten. Statusabfragen bleiben lesend. Direkte manuelle Start-/Weiteranfragen sind im automatischen Modus gesperrt; nach Ende des Einsatzfensters werden neue Einsatzänderungen abgewiesen.
- Countdown im vorhandenen Statusbereich angezeigt, ohne neue Buttongestaltung oder zweite Komposition. Die Browser zählen nur herunter; die Rundenwechsel erfolgen auf dem Server. Die reine Serverzeit ist vom Vergleich für vollständige Oberflächenupdates ausgenommen, damit Statusabfragen nicht alle 1,5 Sekunden Eingabefokus, Karten oder Buttons neu erzeugen. Fristablauf sperrt abgelaufene Einsatzknöpfe. Form, Größe, Cinzel, Material, Bewegung und Klang des vollständigen Werkstattrezepts unverändert. Tischregeln um die aktuellen Zeitfenster ergänzt.
- 31 gezielte Python-Prüfungen bestanden: bisherige 23 Sitz-/Rundenfälle sowie acht Uhrfälle zu exakten Fristen, Änderungen ohne Fristverlängerung, leerem Fenster und bewusst neuem Einsatz, automatischem Ergebniswechsel ohne Wiederholungswette, leerem Tisch, parallelen Uhren, späten/manuellen Anfragen, lesendem Status, Dienstneustart und späterem Einstieg. In Testanwendungen startet kein Hintergrundthread. Python-/JavaScript-Syntaxprüfungen bestanden. Kein erfolgreicher Gesamttest aller Spiele behauptet.
- Lokales Hauptspiel gezielt neu geladen (PID 7360 → 20104). Die Werkstattports 8770/8771/8773/8776 waren vorher nicht belegt und blieben es; keine Werkstatt gestartet oder beendet. Erste Prozessvergleichsprüfung nahm fälschlich laufende Werkstätten an und wurde anhand der gespeicherten Vorher-/Nachherlisten korrigiert. Kein unerwarteter Prozesswechsel festgestellt.
- Nutzer spielte während der sichtbaren Prüfung selbst weiter; danach nur lesend beobachtet, keine weiteren fremden Spielzüge ausgelöst. Einsatzphase Runde 19 und danach Runde 20 mit Countdown gesehen. Runde 22 auf Platz 3 nach Countdown ohne Starttaste tatsächlich ausgeteilt (3 Pik + 10 Herz, Bank 8 Herz + grüne Rückseite). Danach Einsatzphase Runde 23 mit null Einsatz gesehen; nach Ende des leeren Fensters blieb der Tisch wartend bei null Einsatz. Zwei Fenster zeigten gleichen Platz, Vorrat und Countdown. Keine abschließenden Browserwarnungen/-fehler. Keine abgeschlossene Browserprüfung mit drei verschiedenen echten Personen behauptet.
- Alle 45 vorher erfassten Bibliotheks-/Originaldateien einschließlich Tischbildern, Avatar-Komponente, Buttonvorlagen und erzeugtem gemeinsamen Werkstattprogramm/-CSS SHA-256-identisch. Datenbankvergleich zeigt Änderungen ausschließlich in blackjack_game, blackjack_balances und blackjack_seats durch Tischuhr und gleichzeitiges reguläres Spielen/Sitzwechsel des Nutzers. Alle anderen bestehenden Tabellen unverändert. Keine Rücksetzung von dessen Runden, Tischpunkten oder gewähltem Platz.
- Quellen, Grenzen und Zeitfenster in README.md und source.json unter offline-preview/blackjack-v1/ dokumentiert. Nachweise runtime/blackjack-clock-20261030/: Datenbanksicherungen, protected-before.json, dateipruefung.json, ports-before.json/ports-after.json, process-verification.json, automatischer-tisch.png und automatisch-ausgeteilt.png. Ausschließlich lokal geladen und sichtbar geprüft, keine Serververöffentlichung. Noch offen: Zeitlimits für Spielerzüge/Versicherung, Inaktivität/Verbindungsabbruch sowie sichtbarer Praxistest mit mehreren unterschiedlichen Konten.


## 30.10.2026 – Black Jack: sofortige Einsatzvormerkung und Beitrittstest mit Hugo

- Auf ausdrücklichen Nutzerauftrag die frühere Pflicht zum Warten auf die Einsatzphase geändert: Nach dem Platznehmen ist jederzeit ein Einsatz für die nächste Runde möglich, auch während fremder oder eigener laufender Hände. Vormerkungen reservieren Tischpunkte, lassen sich bis zum Austeilen ändern/zurücknehmen und werden genau einmal übernommen. Aufstehen gibt die zusätzliche Vormerkung frei; der bereits ausgeteilte Einsatz bleibt bis zur regulären Abrechnung gebunden. Gespeicherte Vormerkungen überstehen Rundenende, Neuladen und Dienstneustart. Keine automatische Wiederholungswette.
- Ein einziger Sitzender erhält keinen Einsatzcountdown: Sein Einsatz teilt innerhalb derselben Schreibtransaktion sofort aus. Ein neuer ausdrücklicher Einsatz allein in der Ergebnisphase startet ebenfalls sofort. Bei mehreren Sitzenden endet das bisherige höchstens 20-sekündige Einsatzfenster früher, sobald alle gesetzt haben. Laufende Hände bleiben unberührt; die normale 10-sekündige Ergebnispause für bereits vorgemerkte Einsätze bleibt bestehen. Statusabfragen bleiben lesend, Revisionen und Transaktionen verhindern Doppelstart/Doppelabbuchung. Die Frontend-Fähigkeitskennung prebet_supported verhindert neue Einsatzangebote gegenüber einem noch nicht neu geladenen älteren Server.
- Anzeige ergänzt um Vormerkung für Runde N, nächsten reservierten Einsatz und passende Sitzkennzahlen. Tischregeln und Quellenbeschreibung aktualisiert. Die kanonische Szenenkomposition, ursprüngliche Karten/Avatare und das vollständige dunkle Werkstattbutton-Rezept bleiben erhalten. Alle 45 vorab erfassten Bibliotheks-/Originaldateien SHA-256-identisch.
- 39 gezielte Python-Prüfungen bestanden: bisherige Sitz-/Runden-/Uhrfälle und acht Fälle für Sofortstart allein bzw. bei vollständiger Bereitschaft, Vormerkung während einer Hand und Übernahme nach Neustart, Ändern/Rücknahme/Aufstehen, bereits gebundene Punkte, Aufstehstatus und konkurrierende Einsatzanfragen. Python- und JavaScript-Syntaxprüfungen bestanden. Kein Gesamttest anderer Spiele behauptet.
- Getrennter ausdrücklich gekennzeichneter Beitrittstest über deploy/preview_blackjack_join.py auf http://127.0.0.1:8780/ gestartet. Eigene Datenbank runtime/blackjack-join-simulation/quiz.sqlite3 und eigener Sitzungscookie. Ausschließlich dort existieren Stormseed · Test und Hugo · simuliert; nur öffentliche Anzeigename-/Ausrüstungskennungen des vorhandenen Profils werden lesend übernommen. Keine PIN, persönlicher Sitzungsschlüssel oder reale Kontoanmeldung verwendet/verändert. Hugo wartet zunächst mit vorbereiteter 16 gegen offene Bank-6 auf den Besucher und dessen Vormerkung, hält vier Sekunden später und spielt danach mit normalen Regeln weiter. Er bewegt ausschließlich seine eigene Testhand.
- Tatsächlicher Browserweg geprüft: Test-Hauptseite → games collection → Kartentische → Black Jack → Platz 2 nehmen während Hugos Hand → 50 Punkte vormerken. Vormerkung im Ergebnis erhalten; in Runde 2 automatisch genau als 50-Punkte-Hand übernommen, Bestand dabei weiterhin 950. Keine Browserwarnungen/-fehler in der Spielprüfung. Anschließend ausschließlich den eigenen Teststand auf den zuvor gesicherten Anfang zurückgestellt, Hugo auf Platz 1 und zwei freie Plätze sichtbar erneut geprüft. Test-Hauptseite für den Nutzer offen gehalten; der Nutzertest selbst steht noch aus.
- Reguläres lokales Hauptspiel gezielt neu geladen (PID 20104 → 7704). Dort nur lesend Runde 31/Ergebnis und Runde 32 ohne Einsatzcountdown sowie Hinweis auf Sofortstart beobachtet; keine eigene Aktion in der persönlichen Partie ausgeführt. Werkstattports 8770/8771/8773/8776 vorher/nachher nicht belegt. Testdienst zusätzlich auf Loopback 8780, keine Veröffentlichung oder Änderung unter /srv/guesstimate.
- Persönlicher Vorher-/Nachher-Datenvergleich: Unterschiede in den drei Blackjack-Tabellen durch den fortgesetzten Tischbetrieb sowie sqlite_sequence für login_days (40 → 42); alle übrigen Tabelleninhalte einschließlich Nutzerkonten, Ergebnisse, Nutzungshistorie und Profilzuordnungen identisch. SQLite quick_check ok und keine Fremdschlüsselverletzung. Nachweise einschließlich Sicherungen, Dateivergleich, Prozesslisten, 39-Prüfungs-Ergebnis und tatsächlichen Browserbildern unter runtime/blackjack-prebet-20261030/. Noch offen bleiben Zug-/Versicherungszeitlimits und Inaktivitätsregeln.


## 30.10.2026 – Black Jack: Fensterpassung, transparente Bedienung und Werte am Avatar

- Auf Nutzerfeedback zu abgeschnittenem Geberkopf, Seiten-Scrollbar und festen braunen Leisten die zuständige gemeinsame Tischkomposition überarbeitet. Ursache: Bild mit object-fit cover und maximal 720 Pixel Szenenhöhe trotz größerer Breite. Auf Desktop wird das unveränderte 1672×941-Bild nun vollständig und im richtigen Seitenverhältnis in Breite und Höhe eingepasst; freie Ränder bleiben dunkel. Zwei obere Leisten und der separate Fußstreifen entfernt. Kleiner Rückweg/Titel links und Ton/Tischregeln rechts schweben direkt im Bild. Unter 900 Pixel Breite bleibt dieselbe Komposition im Seitenfluss zugänglich; kein Versprechen völliger Scrollfreiheit in beliebig kleinen Fenstern.
- Untere Bedienfläche vollständig transparent, ohne zusätzlichen Kasten oder Hintergrundstreifen. Bestehende Aktionsbuttons bleiben das vollständige gespeicherte Werkstattrezept; begrenzter Platz wird ausschließlich über die proportionale Größenoption des gemeinsamen Renderers ausgeglichen. Keine Streckung, keine neue Schrift-/Material-/Bewegungs-/Klanggestaltung. Zusatzhinweise stehen am Button als Hilfetext bereit; der Sitzhinweis bleibt als zugängliche Beschreibung erhalten. Eingabebeschriftung gekürzt, ausführlicher zugänglicher Feldname erhalten. Zuständige CSS-Regeln ersetzt/konsolidiert, keine neue Korrektursammlung angehängt.
- Bestand, laufender Einsatz und nächste Vormerkung werden bei jedem belegten Platz über die unveränderte kanonische Avatar-Komponente angezeigt. Statusantwort um ausschließlich öffentliche Tischpunkte/Einsätze des jeweiligen Sitzes ergänzt. Getrennte Geldanzeige aus dem echten unteren Bedienbereich und zusätzliche Einsatzmarken unter den Karten entfernt. Höhen von Aktionen und Avataren werden beobachtet; Karten bleiben darüber. Bankwert neben die Bankkarten versetzt, damit er sich nicht mit dem Spielernamen überlagert. Tischbild, Kartenassets und gespeicherte Vorlagen unverändert.
- Regulären lokalen Spielserver und getrennten vorhandenen Hugo-Testprozess neu geladen, ohne den Teststand oder eine persönliche Partie zurückzustellen. Neue Ansicht im tatsächlichen Hauptspiel mit Stormseed/Platz 2/515 Tischpunkten/Runde 32 sowie im bestehenden Hugo-Test mit zwei Avataren, Karten, Einsatz und Vormerkung sichtbar geprüft. Keine Spielzüge, Einsätze oder Versicherungsentscheidungen für den Nutzer ausgeführt. Nur Tischregeln im Hauptspiel geöffnet und geschlossen; funktioniert auch als überlagerte Bedienung.
- Desktop-Größen 1280×720 und 1911×910 sowie das normale Vorschaufenster 1140×884 geprüft. Dokumentbreite/-höhe stimmen mit dem jeweiligen Fenster überein; kein Seitenüberlauf. Transparenter Bedienhintergrund tatsächlich als rgba(0,0,0,0) gemessen. Vollständiger Geberkopf sichtbar. Sieben Sitz-/Profil-/Statusprüfungen und Python-/JavaScript-Syntaxprüfungen bestanden; keine abschließenden Browserwarnungen/-fehler in den geprüften Tischansichten. Keine neuen Rundenspielregeln und keine Serververöffentlichung.
- Alle 45 erfassten persönlichen Bibliotheks-/Originaldateien einschließlich Bild, Buttonrezept, gemeinsamem Buttonprogramm/-CSS und Avatar-Komponente SHA-256-identisch. Persönlicher Vorher-/Nachher-Datenvergleich: ausschließlich sqlite_sequence geändert; sämtliche eigentlichen Tabelleninhalte einschließlich Blackjack-Hand, Punkten, Sitzen, Konten und Ergebnissen identisch. SQLite quick_check ok, keine Fremdschlüsselverletzungen. Nachweise und Sicherungen unter runtime/blackjack-layout-20261030/, insbesondere tisch-transparent-1911.png, tisch-transparent-standard.png, mit-karten-und-avataren.png und layout-standard.json. Aktueller Offline-Tisch geöffnet; bestehende Nutzertabs erhalten. Der alte selbständige Browserbeispielstand wurde nicht neu gebaut; seine weiter zuständige Szenenvorlage und die Quellenbeschreibung wurden aktualisiert.


## 30.10.2026 – Black Jack: Tisch verlassen dauerhaft am äußeren Bildschirmrand

- Auf Nutzerauftrag Tisch verlassen aus der wechselnden Reihe der Spielaktionen entfernt. Der vorhandene Werkstattbutton sitzt nun fest unten rechts am Browserfenster, jeweils 16 Pixel vom Rand. Er behält diese Position auch neben einem schmaler eingepassten Tischbild. Seine proportionale Größe hängt nur von der Fenster-/Szenengröße ab, nicht von Rundenzustand oder der Zahl der übrigen Aktionen. Ein gemeinsamer Renderdurchlauf verwendet unverändert dasselbe Rezept und dieselbe Austrittsaktion; keine zweite Buttonimplementierung und keine neue Bestätigung eingeführt.
- Für belegten eigenen Platz einen getrennten zugänglich benannten Verlassen-Bereich in der zuständigen Tischvorlage ergänzt. Spielaktionen halten rechts Platz frei, auf schmalen Fenstern unten. Zuschauer und bereits zum Aufstehen vorgemerkte Spieler erhalten wie bisher keinen weiteren Austrittsbutton. Keine Änderungen an Spielregeln, Punkten oder gespeichertem Tischzustand; kein Dienstneustart nötig.
- Sichtbar im laufenden regulären Offline-Spiel während der Einsatzphase (Runde 32, Stormseed) und im bestehenden Hugo-Test während der Versicherung (Runde 8) geprüft. In beiden Ansichten bei 1280×720 genau 16 Pixel rechts/unten und außerhalb der Spielaktionsgruppe gemessen. Zusätzlich bei 1911×910 geprüft: tatsächlicher Bildschirmrand, nicht nur Tischbildkante; der außerhalb des Bildes liegende Buttonteil ist sichtbar und per Trefferprüfung erreichbar. Keine Browserwarnungen/-fehler; JavaScript-Syntaxprüfung bestanden. Keine fremden Spielzüge oder Austrittsaktionen ausgeführt.
- Alle 45 geschützten Original-/Bibliotheksdateien einschließlich Werkstattrezept, gemeinsamem Buttonprogramm und Bild SHA-256-identisch. Sicherung der drei bearbeiteten Dateien, Dateivergleich und tatsächliche Browserbilder unter runtime/blackjack-exit-20261030/. Quelle und README aktualisiert. Ausschließlich lokal sichtbar, keine Serververöffentlichung.


## 30.10.2026 – Black Jack: Karten nacheinander sichtbar ausgeben

- Nutzerwunsch nach Austeilen wie am echten Tisch umgesetzt. Die bisherige echte Ziehfolge bleibt unverändert: je eine Karte an die gesetzten belegten Plätze in Sitzreihenfolge, danach Bank; dann zweiter Umlauf. Neu ist ausschließlich die zeitliche Darstellung im Browser. Modul static/blackjack-card-motion.js verwendet die bestehenden Kartenbilder, 270-ms-Flug von der Kartenschuhseite, 85-ms-Pause und den bestehenden angeglichenen Kartenklang je Ankunft. Tischgrafik, Avatare, Werkstattbuttons und Spielregeln bleiben erhalten.
- Nachziehen animiert ausschließlich neue Karten. Teilen zählt die schon liegenden Karten über beide Hände mit; gleiche Bilder aus sechs Decks werden als mehrere Karten behandelt. Die Bankkarte bleibt verdeckt, bis sie im öffentlichen Spielstatus aufgedeckt ist; dann 240-ms-Drehbewegung, anschließend gegebenenfalls einzeln gezogene Bankkarten. Betroffene Summen und neue Ergebnisbeschriftungen erscheinen erst nach der Bewegung; vorliegende Karten anderer Hände bleiben bestehen. Kartenaktionen sind während der laufenden Darstellung deaktiviert, Vormerkung und das fest am Rand stehende Tisch verlassen bleiben erreichbar.
- Keine Änderung an serverseitigem Stapel, Transaktionen, Phasenwechseln, Einsatzverwaltung oder Abrechnung. Statusabfragen und Avatar-/Einsatzänderungen starten keine erneute Animation. Während der Bewegung eintreffende Kartenänderungen werden nach deren Abschluss dargestellt. Neue Öffnung einer laufenden Partie zeigt den gespeicherten Stand sofort. Abbruch bei Seitenwechsel räumt bewegte Kopien/Animationen auf. Systemeinstellung für reduzierte Bewegung wird berücksichtigt. Noch keine Zug-/Versicherungstimeouts ergänzt.
- Neun Node-Prüfungen der Austeilplanung bestanden: drei Plätze in zwei Umläufen, Erstöffnung ohne Wiederholung, unveränderte Statusantwort, einzelne Zusatzkarte, Aufdecken vor Bankziehen, sofortiges Ergebnis mit zunächst verdeckt gegebener Bankkarte, Teilen ohne Wiederholung der alten Karten, identische Kartenbilder und Leeren des Tisches. JavaScript-/Prüfserver-Syntaxprüfungen bestanden.
- Getrennte reine Darstellungsvorführung auf 127.0.0.1:8782 verwendet, ausdrücklich als Vorführung markiert, ohne Datenbank, Konto oder Kopie einer persönlichen Partie. Tatsächlich per Browser Einsatz setzen → acht Ankünfte in Reihenfolge Platz 1/2/3/Bank/1/2/3/Bank geprüft. Kartenaktionen währenddessen gesperrt, danach freigegeben; Statusabfragen erzeugten keine Wiederholung. Karte ziehen ergänzt genau eine Ankunft auf Platz 2; Halten zeigt Bank aufdecken vor zusätzlicher Bankkarte. Danach genau elf Ankünfte insgesamt. Vorführung während der zweiten Karte zurückgesetzt: keine zurückbleibenden Flugkarten; erneuter vollständiger Lauf erfolgreich. Vorhandener balanced-v1-Klangpfad aktiv, keine Browserwarnungen/-fehler.
- Bestehenden gemeinsamen Hugo-Testtisch auf 8780 nur geöffnet: Runde 8/Versicherung, liegende Karten sofort vorhanden, Bank-Ass plus unveränderte verdeckte Karte, keine wiederholte Austeilung. Keine Spielzüge oder Einsatzänderungen für den Nutzer ausgelöst. Alle 45 geschützten Original-/Bibliotheksdateien SHA-256-identisch. Keine Serververöffentlichung oder Dienstneuladung des Hauptspiels. Reproduzierbare Prüfvorführung, Sicherungen, Dateivergleich und Bilder unter runtime/blackjack-deal-20261030/, insbesondere nacheinander-zwischenstand.png und bestehender-tisch-ohne-wiederholung.png. README und Quellenmanifest aktualisiert; archiviertes Browserbeispiel nicht neu gebaut.


## 30.10.2026 – Black Jack: Einsatzbedienung zur Klärung geöffnet

- Nutzer beanstandet den dauerhaft zwischen Spielaktionen stehenden Vormerkungsbutton, besonders nach der Versicherung. Gewünscht sind unmittelbares Setzen beim Dazukommen und ein stimmiger Einsatzablauf im Tischrhythmus. Anschließend klärt der Nutzer, dass die gewünschte Einsatzlogik noch nicht eindeutig ist, und bittet zunächst um einen Bedienvorschlag. Daher in diesem Auftrag noch keine Spielregel, Einsatzwiederholung, automatische Abbuchung oder Oberfläche verändert.
- Aktuelle tatsächliche Ansicht nur lesend geprüft: Hugo-Test, Runde 19, eigener Zug mit Karte ziehen/Halten/Verdoppeln/Aufgeben und daneben Vormerkung ändern/zurück. Die Vermischung betrifft die gemeinsame Aktionsleiste. Vorschlag zur Entscheidung: dauerhaft erreichbarer kleiner Einsatzbereich am Avatar, laufenden Hand-Einsatz getrennt von der Auswahl für die nächste Hand anzeigen; in der Hauptleiste nur aktuelle Spielzüge. Offen ist, ob ein frei gewählter persönlicher Betrag bis zum Ändern/Aussetzen automatisch wiederholt wird oder jede Runde neu bestätigt werden soll. Rückfrage dazu gestellt; keine Variante bereits als verbindlich umgesetzt. Bestehende Hände und Einsätze unangetastet.


## 30.10.2026 – Black Jack: ausdrücklich gelegter Einsatz, danach fest

- Neueste Nutzerentscheidung ersetzt die zwischenzeitlich gewählte automatische Wiederholung: Teilnahme ausschließlich mit einem ausdrücklich gelegten Einsatz für genau eine Runde. Button heißt in allen Einsatzphasen schlicht Einsatz. Die noch unvollständige automatische Umstellung in blackjack_game.py/blackjack_clock.py/blackjack.py aus der unmittelbar zuvor eigenen Sicherung zurückgenommen; sie war weder gestartet noch in eine persönliche Datenbank übernommen worden. Vorprüfung beider bestehender Zustände bestätigte kein stake_policy-Feld. Keine automatische Abbuchung eingerichtet.
- Auf ergänzenden Nutzerauftrag ist der Einsatz nach dem Legen fest. Betrag ändern oder cancel-bet werden serverseitig mit 409 abgewiesen, ohne Punkte/Revision zu verändern. Betragseingabe und sämtliche Einsatzbuttons verschwinden, solange ein Betrag auf dem Tisch liegt. Aktuelle Hand bleibt unberührt. Nach einmaliger Übernahme in die Runde ist für eine weitere Runde ein neuer ausdrücklicher Einsatz nötig. Bestehender Austrittsablauf bleibt erhalten: Wer vor dem Austeilen wirklich aufsteht, bekommt einen zusätzlichen noch nicht ausgespielten Einsatz wie bisher zurück; kein geänderter Verfall oder Kontoeingriff.
- 43 gezielte Python-Prüfungen bestanden: 39 Sitz-/Runden-/Uhr-/Einstiegsfälle mit angepassten Erwartungen für feste Einsätze sowie vier zusätzliche Natural-Fälle. Abgedeckt sind gesperrtes Ändern/Zurückziehen in Einsatzphase und laufender Hand, gebundene Punkte ohne Double-Doppelnutzung, gleichzeitige Doppelklicks, genau einmalige Verwendung, keine automatische Wiederholung und Aufsteh-/Neustartverhalten. Python-/JavaScript-Syntaxprüfungen bestanden.
- Eigener isolierter Prüftisch auf 8782 mit eigener Datenbank, synthetischen Prüfkonten und getrenntem Cookie verwendet. Tatsächlich per Browser geprüft: Während Versicherung 50 Punkte für Runde 2 legen → Eingabefeld und Einsatzbutton verschwinden → ohne Versicherung weiter → ausschließlich Ziehen/Halten/Verdoppeln/Teilen/Aufgeben in der Spielleiste; 50 Punkte für Runde 2 weiter beim Avatar sichtbar. Keine Editier-/Zurückziehknöpfe nach der Versicherungsentscheidung. Keine Browserwarnungen/-fehler. Keine Aktion in der persönlichen Partie oder im bestehenden Hugo-Test ausgelöst. Eigener Prüftisch anschließend beendet.
- Hauptspiel und bestehenden Hugo-Test gezielt neu geladen, gespeicherte Partien nicht zurückgesetzt. Neue Beschriftung im tatsächlichen Hugo-Tisch während Runde 47 sowie nach Aktivierung die Einsatzphase für Runde 59 beobachtet; eigener Spieler ohne Einsatz erhält nur den Button Einsatz. Vergleich des persönlichen Hauptbestands zeigt ausschließlich sqlite_sequence verändert, sämtliche eigentlichen Tabelleninhalte identisch. quick_check ok, keine Fremdschlüsselverletzung. Alle 45 geschützten Bibliotheks-/Originaldateien SHA-256-identisch. Belege und Sicherungen: runtime/blackjack-explicit-stake-20261030/, insbesondere tests-locked.txt, einsatz-liegt-nach-versicherung.png, protected-check.json, data-comparison.json und Prozesslisten. Ausschließlich lokal, keine Veröffentlichung auf /srv/guesstimate.
- Offene Dealer-Recherche ebenfalls erledigt: Nutzerregelwerk gelesen, aktuelles MGC-Regelwerk https://massgaming.com/wp-content/uploads/RULES-Blackjack-4-9-26.pdf verglichen. Natural gewinnt 3:2, zwei Naturals ergeben Gleichstand; Bank-21 aus drei Karten schlägt den Spieler-Natural nicht. Kein weiteres Bankziehen nötig, wenn es kein Ergebnis mehr beeinflusst. Vier konkrete Engine-Fälle dafür bestanden. Verbleibende Abweichung zur dortigen §7(a)-Abwicklung: Bei mehreren Spielern wird sicherer Natural gegen offene Bank-2–9 hier erst am Rundenende ausgezahlt. Frühe Auszahlung noch nicht geändert; keine pauschale Behauptung vollständig identischen Dealer-Ablaufs.


## 30.10.2026 – Black Jack: Einsatzbutton auch während der eigenen Hand ausblenden

- Nutzer meldet trotz voriger Ausblendung weiterhin einen Einsatzbutton. Fehler direkt am tatsächlichen Hugo-Tisch reproduziert: Runde 70, eigener Spieler mit 11 Kartenpunkten und bereits ausgespielten 50 Tischpunkten sah Eingabefeld/Ein­satzbutton für Runde 71. Ursache war die alleinige Prüfung von own_bet: Dieser zukünftige Einsatz wird beim Austeilen geleert, obwohl der aktuelle Hand-Einsatz weiterhin gebunden ist.
- Gemeinsame Berechtigungsfunktion can_place_bet ergänzt. Neue öffentliche Freigabe can_bet berücksichtigt den bereits gelegten zukünftigen Einsatz und die eigene laufende Hand einschließlich Versicherung. Frontend verwendet diese Freigabe; bei älterer Statusantwort gleiche sichtbare Fallunterscheidung als Übergang. Während eigener Hand und Bankanimation kein Einsatzbutton/-feld; nach sichtbarem Rundenabschluss wieder verfügbar, solange kein neuer Einsatz liegt. Server weist auch direkte zweite Initialeinsätze während eigener Hand zurück. Verdoppeln/Teilen bleiben eigenständige zulässige Spielzüge.
- Neue Teilnehmer ohne laufende eigene Hand dürfen weiterhin jederzeit für die nächste Runde setzen. Bereits früher gelegte zukünftige Einsätze bleiben erhalten und werden nicht zurückgesetzt. Der simulierte Hugo legt neue Einsätze nun ebenfalls erst nach seiner laufenden Runde; Vorbereitung seines ersten Prüftisches angepasst, damit keine unzulässigen Folgeeinsätze versucht werden. Keine automatische Einsatzwiederholung und keine Änderungen an Zieh-/Auszahlungsregeln.
- 45 Python-Prüfungen bestanden: bisherige 43 Fälle mit angepasster Teilnehmer-/Neueinsteigerabgrenzung sowie zwei zusätzliche Freigabefälle für ungelegt, gelegt, ausgeteilt, beendet und Versicherung. Syntaxprüfungen bestanden. Eigener getrennter Prüftisch mit neuer Datenbank zeigte tatsächlich: Versicherung ohne Einsatzbutton → ohne Versicherung → eigener Zug weiterhin ohne Einsatzbutton → Bankanimation ohne Einsatzbutton → Rundenende mit Einsatzbutton → Einsatz gelegt, Button und Feld wieder verschwunden. Keine Browserwarnungen/-fehler. Eigene Prüfpartie anschließend beendet.
- Beide lokalen Spielprozesse gezielt neu geladen und den ursprünglich beanstandeten bestehenden Tisch erneut nur lesend geöffnet. Exakt dieselbe Runde 70 mit denselben Karten, 925 Tischpunkten und eigener Hand 11: jetzt null Einsatzbuttons und null Betragsfelder, reguläre Spielzüge vorhanden. Keine fremden Spielaktionen ausgeführt. Vorher-/Nachhervergleich beider bestehenden Datenbanken: ausschließlich sqlite_sequence geändert; sämtliche eigentlichen Tabelleninhalte einschließlich Händen, Einsätzen, Punkten, Konten und Profilen identisch. quick_check jeweils ok, keine Fremdschlüsselverletzungen. Alle 45 geschützten Original-/Bibliotheksdateien SHA-256-identisch.
- Nachweise unter runtime/blackjack-bet-visibility-20261030/: tests.txt, bestehender-tisch-korrigiert.png, kein-einsatzbutton-waehrend-hand.png, Datenbanksicherungen, Daten-/Dateivergleich und Prozesslisten. README und Quellenmanifest aktualisiert. Ausschließlich lokal sichtbar geprüft, keine Serververöffentlichung.


## 30.10.2026 – Black Jack: feste Test-iKühe, bewusster Austritt und unverzerrte Monitoransicht

- Nutzerklärung verbindlich: Beim Verlassen verfällt der noch liegende Einsatz. Umsetzung für „Tisch verlassen“ und „Kartentische“ über dieselbe CSRF-geschützte POST-Aktion. Ein Folgerundeneinsatz wird genau einmal ohne Rückzahlung entfernt; laufende Hände einschließlich bereits gelegter Versicherung verfallen ebenfalls. Bereits abgerechnete Gewinne bleiben erhalten. Nach laufender Runde wird der reservierte Sitz frei. Neuladen und Tab-Schließen sind kein Austritt.
- Die beiden lokalen Starter konfigurieren einen festen Grundeinsatz von 500 Test-iKühen. Neue Tischbesucher erhalten 10.000 getrenntes Testguthaben; bestehende Guthaben und bereits liegende Alteinsätze werden nicht zurückgesetzt/umgerechnet. Ein erschöpfter Testvorrat unter 500 kann zwischen eigenen Händen ausdrücklich aufgefüllt werden. Kein automatisches Wiederholen des Einsatzes, keine echten iKühe-Abbuchungen und keine Änderung von Kontowährungstabellen.
- Eigene Avatar-Anzeige nutzt unmittelbar die kanonische player-portrait.js/.css, ergänzt um eine optionale strukturierte Guthabenanzeige mit großen Werten für Bestand, Einsatz und Rundengewinn. Andere Varianten bleiben erhalten. Spiel- und Austrittsbuttons verwenden unverändert das gespeicherte dunkle Werkstattrezept mit Schrift, Bewegung und Buttonklang.
- Unveränderte CC0-Chipaufnahmen aus dem bereits lokal gesicherten Kenney-Casino-Paket nach static/audio/blackjack/ übernommen, Herkunft/Lizenz gesichert. Chipablage bei Einsatz, Teilen, Verdoppeln und Versicherung; Chipbewegung bei Auszahlung. RMS-Anpassung und Spitzenbegrenzung vor dem vorhandenen Kompressor; keine Wiederholung durch Polling oder Wiederöffnen. Im eigenen Browsertest chips-place und chips-payout tatsächlich beobachtet, +500 Rundengewinn am Avatar sichtbar.
- Die zunächst versuchte Raumerweiterung v1 hatte sichtbare Übergänge und bleibt ein unbenutzter Entwurf. Anschließend wurde fälschlich object-fit:fill zur Monitorfüllung verwendet; der Nutzer erkannte die Verzerrung. Diese Streckung ist vollständig entfernt. Maßgeblicher Stand: ursprüngliche 1672×941-Szene proportional und vollständig, seitliche Raumerweiterung v2 als separater Hintergrund mit schmaler 1,5-Prozent-Kantenüberblendung. Originaldatei SHA-256 weiterhin 1585284abc0f54dce3f833904a66e2607407add4d58ace46aa0dae36a23ddf02. Bei 1911×910 im bestehenden Hugo-Tisch gemessen: Bildfläche 1616,90625×910, Skalierung X 0,9670492 / Y 0,9670563 (Pixelrundung), Seite exakt 1911×910 ohne Scrollleisten. Keine Verzerrung des Gebers. Breite Seiten gefüllt; sehr schmale/hohe Fenster behalten proportionale Darstellung. Bildgenerierung über eingebautes image_gen; v2-Prompt und PNG lokal gesichert.
- Nutzer meldete fehlendes Split bei zwei Vieren: direkt im laufenden Tisch zwei 4 Karo, Einsatz 500, verfügbares Guthaben 250 beobachtet. Der gleiche Zusatzeinsatz von 500 war deshalb nicht gedeckt; Regel korrekt, fehlende Begründung unklar. Server liefert nun bei sonst teilbarer Zweikartenhand eine Geldmangel-Begründung; „Teilen“ bleibt dann gesperrt sichtbar und der Status nennt Bedarf und Bestand. Keine Guthabenänderung zum Freigeben im Benutzerbestand vorgenommen. Eigener getrennter Prüftisch: Sperre bei 250, Freigabe bei genügend Guthaben, danach zwei Hände mit korrekt zusätzlicher Abbuchung sichtbar geprüft. Bestehender Hugo-Tisch zeigte anschließend Teilen bei zwei Assen und ausreichendem Guthaben; keine fremden Spielzüge ausgelöst.
- Prüfungen: 52 Regel-/Sitz-/Takt-/Einsatztests bestanden; neun Kartenpräsentationsprüfungen bestanden; JS-Syntax geprüft. Sichtbarer Browserweg Einsatz500 → Kartentische → freier Sitz → erneut Platz nehmen bewies Verfall und keinen zweiten Abzug. Zusätzliche Tests sichern das Verfallen einer sonst gewinnenden Hand und einer sonst gewinnenden Versicherung. Beide lokalen Dienste auf 8765 und 8780 gezielt mit bestehenden Datenbanken neu geladen. Hauptbestand unveränderte Guthaben/Sitze, nur blackjack_game verändert. Während aktiver Nutzung ändern sich Simulation/Hugo-Runden weiter; dort keine Behauptung unveränderter Runden/Guthaben. Kontotabellen beider Bestände unverändert, quick_check jeweils ok, keine Fremdschlüsselverletzungen. 43 von 45 geschützten Dateien identisch; ausschließlich kanonische Avatar-js/css gezielt erweitert, persönliche Bibliothek, Rezept, Originalklänge und Originalbilder erhalten.
- Nachweise: runtime/blackjack-table-polish-20261030/ (tests.txt, fixed-tests.txt, final-data-and-assets.json, Sicherungen, gewinn-und-avatar.png, split-mit-fehlendem-guthaben.png, teilen-mit-zwei-haenden.png). Gültiger abschließender Bildnachweis: monitor-proportionen-korrigiert.png. Der frühere gestreckte Nachweis ist ausdrücklich als monitor-1911x910-verworfen-gestreckt.png markiert. README und Quellenmanifest aktualisiert. Ausschließlich lokale Offline-Arbeit; keine Veröffentlichung oder Änderung auf /srv/guesstimate.
- Offen bleiben: Geberbewegungen/Worte, Zug- und Versicherungszeitlimits/Verbindungsabbrüche, frühzeitige Auszahlung eines sicheren Naturals gegen offene Bank2–9 bei mehreren Spielern, Praxistest mit drei echten Spielern und spätere echte iKühe-Anbindung.


## 30.10.2026 – Black Jack: geteilte Asse, Bank-Blackjack und Kartenklang

- Nutzerscreenshot mit A–6 und A–Bube nach Teilen gegen Bank7–7–8 mit denselben Kartenwerten im eigenen Prüftisch nachgespielt. Nach geltender Tischregel erhalten geteilte Asse je nur eine Zusatzkarte, beide Hände stehen automatisch; 21 nach Teilen ist kein Natural. Beide Hände gewinnen bei Bank22. Gegen Bank20 verliert die17 und die21 gewinnt1:1. Ungeteilte eigene Soft17 lässt weiterhin Halten/Ziehen zu. Diese konkreten Fälle sowie Bank-Blackjack bei Zehner offen und bei Ass offen mit vorheriger Versicherung sind durch fünf zusätzliche bestandene Tests abgesichert. MGC-Regelwerk vom09.04.2026, §§1,6(i),9,11(c),12 erneut verglichen; Nutzer-Regeldatei gelesen. Keine Änderung der bereits korrekten Spiellogik an diesen Stellen, sondern verständliche Hinweise im Spiel für automatisch abgeschlossene geteilte Asse und Bank-Blackjack ergänzt.
- Runde136 nicht exakt rekonstruierbar: Bei der aktuellen Prüfung war Runde140 gespeichert; Sicherungen dieses Arbeitsabschnitts enthielten113,119,121,134. Der Singleton speichert keine Rundengeschichte. Daher keine Behauptung, die konkrete offene Bankkarte/Versicherungsphase aus136 nachträglich beobachtet zu haben. Bei bestätigtem Bank-Natural gibt es regulär keine weiteren Spielerzüge; eine Versicherungsentscheidung ist zuvor nur bei offenem Ass vorgesehen.
- Das als „Plop“ beanstandete bisherige Kartenablagegeräusch stammte aus Kenney card-place-1. Für die Ausspielbewegung durch die unveränderte reale Kartenaufnahme card-slide-4 (0,459s) aus dem bereits gesicherten CC0-Casino-Paket ersetzt; liegt unter static/audio/blackjack/card-deal-slide.ogg. Der Klang startet jetzt mit der Kartenbewegung. Bisherige Originalclips/Buttons bleiben erhalten; Normalisierung/Spitzenbegrenzung weiter gemeinsam. Eigener Browserzug5→7 bewies tatsächliche Wiedergabe sound=card-deal / mix=balanced-v1 ohne Soundfehler. Ob der Klang geschmacklich passt, bleibt Nutzerbewertung.
- Jetzt57 Regel-/Ablauftests und neun Kartenpräsentationsprüfungen bestanden, JavaScript-Syntax geprüft. Eigener Prüftisch zeigte dieselben Kartenwerte wie im Screenshot, beide Gewinne je500, Gesamtgewinn1000 und den erklärenden Hinweis. Belege: tests-rules-and-sound.txt, geteilte-asse-erklaert.png und neuer-kartenklang.json unter runtime/blackjack-table-polish-20261030/. Vor letzter Übernahme beide bestehenden Datenbanken zusätzlich gesichert; die beiden lokalen Dienste mit denselben gespeicherten Partien neu geladen. Keine Serververöffentlichung oder Änderung echter Kontowährung.

- Abschließende Übernahmeprüfung: Hauptbestand gegenüber Sicherung vor letztem Neustart in allen Tabellen identisch. Im weiter aktiv gespielten Hugo-Test ausschließlich blackjack_game/blackjack_balances verändert; Kontotabellen unverändert. quick_check beide ok, null Fremdschlüsselverletzungen. Eigenen Prüfdienst8782 beendet, normale Offline-Dienste8765/8780 laufen weiter. Beleg delivery-data-check.json. Letzter sichtbarer Prüfaufruf im bestehenden Hugo-Bestand zeigte Runde155, festen500er-Einsatz und neue Split-Asse-Metadaten; Originalbild weiterhin proportional.


## 30.10.2026 – Black Jack: Karten liegen von Anfang an auf der richtigen Höhe

- Nutzer präzisiert: Karten liegen zunächst zu tief und rücken während der Hand nach oben; Summen sind nicht beanstandet. Fehler mit denselben angezeigten Kartenwerten Hugo A–4–9=14 → A–4–9–9=23 in einer getrennten reinen Darstellungsprüfung reproduziert, ohne Konto/Datenbank oder Eingriff in die laufende Partie. Ursache: Die leere Aktionszeile war 0px hoch, beim eigenen Zug 58,53125px; die gemessene Konsolenhöhe stieg von43 auf101,53125px und verschob Karten/Avatare. Zusätzlich verschob die neu angehängte Ergebniszeile die Karten um rund19px.
- Kanonische Aktionszeile reserviert nun auch während fremder Züge die volle Buttonhöhe. Der Wert wird aus dem echten unveränderten Werkstattbutton gemessen und proportional auf dessen volle Tischgröße bezogen; keine eigene Buttongeometrie eingeführt. Tabellenabstände synchron im Renderdurchlauf vor dem ersten sichtbaren Bild gemessen; bisheriger ResizeObserver bleibt für Größenänderungen. Ergebnisinformationen verwenden die vorhandene Handbeschriftung statt einer zusätzlichen Zeile. Während der Kartenbewegung bleiben die Ergebnisbeschriftungen verborgen. Zuständige CSS-Regeln konsolidiert, keine angehängten Korrekturblöcke.
- Tatsächlich per Browser und Einzelbild-Messung geprüft: Hugo-Zug ohne Aktionen → eigene vier Aktionen → Versicherung → Ergebnis. Bei1280×720 bleibt Kartenoberkante451,743103px, Avataroberkante553,3125px und Konsole102px in allen acht erfassten Zustandsbildern identisch. Bei1911×910 bleibt Kartenoberkante605,028137px und Avataroberkante728,3125px in allen neun Bildern identisch. Nachziehen/Aufdecken weiterhin nacheinander; neun Kartenpräsentationsprüfungen und JS-Syntax bestanden.
- Bestehenden Hugo-Tisch auf8780 nur lesend geöffnet: Runde190, eigene12 gegen Hugo23, reservierte Aktionshöhe59px, keine zusätzliche Ergebniszeile und keine Browserwarnungen/-fehler. Originaltischbild weiterhin unverändert und proportional. Alle45 geschützten Original-/Bibliotheksdateien einschließlich Rezept, Schrift, Klängen und kanonischer Avatar-Komponente SHA-256-identisch zum Stand vor dieser Korrektur. Kein Spielzug im Benutzerbestand, keine Datenbankänderung durch Prüfskripte und kein Neustart der normalen Offline-Dienste erforderlich; nur gemeinsame Darstellungsdateien geändert. Eine bereits geöffnete Seite muss neu geladen werden.
- Sicherungen und Nachweise: runtime/blackjack-layout-stability-20261030/ (before-fix.json, after-fix.json, frame-measurements-1280.json, frame-measurements-1911.json, bestehender-tisch-korrigiert.png, protected-check.json). README und Quellenmanifest aktualisiert. Eigene Prüfung ausschließlich lokal; keine Veröffentlichung.


## 30.10.2026 – Black Jack: Karten und Einsätze am jeweiligen gemalten Kreis

- Nutzer beanstandet die ungleiche Lage der Karten relativ zu den Kreisen, ausdrücklich auch im zuvor als korrigiert gezeigten Bild. Die vorige Korrektur beseitigte den HUD-bedingten Höhensprung, ließ aber alle Spielerhände auf derselben Höhe statt am gemalten Tischbogen. Nutzer erlaubt ausdrücklich, Avatare zu verschieben, um die Spielfläche freizuhalten. Diese neue Vorgabe ersetzt die bisherige untere Avatarreihe.
- Gemeinsame Positionsdaten für linken/mittleren/rechten Einsatzkreis eingeführt. Karten werden an ihrem tatsächlichen perspektivisch projizierten unteren Rand am oberen Kreisrand ausgerichtet, gleicher Versatz von2 Prozent der Szenenhöhe. Das entspricht14,4px bei720px Szene und18,2px bei910px Szene; Unterschiede unter0,2px. Die mittlere Hand folgt dem tiefer gemalten mittleren Kreis. Höhen von Aktionsleiste, Avataren und Ergebnistext beeinflussen die Karten nicht mehr. Geteilte Hände verwenden dieselbe gemeinsame Komponente und dieselbe Unterkante. Positionsmessung synchron vor sichtbarem Bild; vorhandene Austeilanimation bleibt erhalten.
- Eigener vollständiger kanonischer Avatar mit Guthaben fest unten links am Bildschirm, eigene Aktionen mit gemessenem Abstand daneben, Tisch verlassen weiterhin ganz außen rechts. Mitspieler oben an den Seiten, bei drei Zuschauereinträgen dritter darunter. Freie Plätze in ihrem Einsatzkreis. Dadurch verdeckt der eigene Avatar keinen Kreis mehr. Ein gemeinsamer Chipmarker je Platz zeigt den bestehenden Einsatzwert im Kreis; Werte aus vorhandenen öffentlichen Einsatz-/Folgeeinsatzdaten, keine neue Spielregel oder Abbuchung. Originaltischbild, Schrift, Buttongeometrie/-bewegung/-klang und Avatarinnenkomposition unverändert. Alte widersprechende HUD-basierte Karten-/Sitzhöhenregeln entfernt; responsive Anordnung an derselben Komponente angepasst.
- Eigene reine Darstellungsvorführung ohne Konten/Datenbank: drei belegte Plätze,1280×720 sowie1911×910, Hugo-Zug→eigener Zug→Versicherung→Ergebnis→zwei geteilte Hände tatsächlich geprüft. Bei1911×910: äußere Kartenunterkanten637,929px, mittlere beide681,614px; jeweils18,2px zum jeweiligen oberen Kreisrand. Alle Einsätze in den Kreisen, keine Avatarüberschneidung mit Einsatzfeldern, Aktionsbuttons neben eigenem Avatar erreichbar. Neun Kartenpräsentationsprüfungen und JS-Syntax bestanden.
- Beide vorhandenen Offline-Dienste auf8765/8780 gezielt mit denselben Datenbanken neu geladen, damit das gemeinsame Template übernommen wird. Bestehenden Hugo-Tisch Runde200, eigener14 gegen Hugo19, nur lesend mit neuem Layout geöffnet: Chips500 in beiden Kreisen, eigener Avatar unten links, Mitspieler seitlich, keine Browserwarnungen/-fehler. Keine Spielzüge für den Nutzer ausgelöst. Kontotabellen unverändert; im aktiv genutzten Hugo-Test können sich blackjack_game/blackjack_balances weiter ändern. quick_check beide ok, keine Fremdschlüsselverletzungen. Alle45 geschützten Original-/Bibliotheksdateien SHA-256-identisch zum Zustand vor diesem Auftrag.
- Belege/Sicherungen: runtime/blackjack-circle-alignment-20261030/ (alignment-wide.json, drei-plaetze-und-split.png, bestehender-tisch-neu.png, data-check.json, protected-check.json, before/ und Datenbanksicherungen). Quellenmanifest und README auf die neue Kreisausrichtung aktualisiert. Ausschließlich lokal, keine Veröffentlichung.


## 30.10.2026 – Black Jack: vereinbarter Schritt1, überflüssige Anzeigen entfernen

- Nutzer beauftragt ausschließlich Schritt1 der zuletzt besprochenen Reihenfolge. Freie Plätze auf der Spielfläche jetzt vollständig verborgen, auch bei Erstöffnung; die vorhandenen Platznehmen-Aktionen bleiben erhalten. Avataranzeigen enthalten Namen und Geldwerte, ohne „Du“, Platznummer oder Belegt-/Am-Zug-Zusatz. In der Simulation Namenssuffixe „· Test“/„· simuliert“ über eine gemeinsame Anzeigefunktion für Avatar und Handcaption entfernt. Keine Kontonamen umgeschrieben. Währungsanzeige im Avatar verkürzt auf iKühe; obere Tischangabe kennzeichnet weiterhin ausdrücklich Test-iKühe. Zusätzlichen schwebenden Testbanner ausschließlich auf Tischseite ausgeblendet, da er bei1280×720 den Mitspieler verdeckte; auf anderen Testseiten erhalten.
- Rundenzähler, Sitzbelegung und explizite Phase aus der Aktionszeile in den Bereich direkt oberhalb „Tisch verlassen“ verschoben. Genau ein Zähler; getrennt vom bei Rendern ersetzten Buttoncontainer, Countdown aktualisiert weiter. Kanonische Avatar-Komponente kann leeren optionalen Status jetzt tatsächlich verbergen; Aufrufer mit angegebenem Status unverändert. Sichtbare Avatarform, Kopfgröße und Werkstattentwurf nicht neu gestaltet. Bestehende Kartenverankerung, Jetons, Bild und Spielregeln erhalten.
- Eigener UI-Prüftisch ohne Konto/Datenbank:1280×720 sowie1911×910, zwei/belegte drei Plätze und wieder freier Platz, reine Namen Hugo/Stormseed, Statuszeilen verborgen, Belegung2/3 bzw.3/3 korrekt. Phase Einsatzphase mit59s Countdown sichtbar. Zähler jeweils8px oberhalb Verlassen: kompakt Unterkante637,469/Buttonoberkante645,469; groß812,828/820,828. Neun Kartenpräsentationsprüfungen und Syntax der drei JS-Module bestanden. Bestehender Hugo-Tisch Runde251, eigene13 gegen Hugo22, nur lesend mit neuer Anzeige geprüft; keine Browserwarnungen/-fehler. Beide lokalen Dienste mit vorhandenen Datenbanken neu geladen, um das gemeinsame Template zu übernehmen.
- Kontotabellen unverändert, quick_check beide ok und null Fremdschlüsselverletzungen. Im weiter genutzten Testspiel können blackjack_game/blackjack_balances fortschreiten.44 von45 geschützten Dateien identisch; ausschließlich kanonische player-portrait.js für optionalen leeren Status erweitert. Persönliche Bilder, Avatarbilder, Karten, Schrift, Sounds, Werkstattrezept und Buttonrenderer unverändert. Belege/Sicherungen: runtime/blackjack-cleanup-step1-20261030/ (verification.json, live-verification.json, punkt1-im-spiel.png, protected-check.json, data-check.json, before/). README/Quellenmanifest aktualisiert. Ausschließlich lokal.
- Klärung für Schritt2: Bisherigen Werkstattbutton nicht am Einsatzort frei verändern. Nutzer erlaubt, eine kleinere Version in der Werkstatt abzuspeichern; die Schrift muss zur Fläche passen. Nutzerbeobachtung ungefähr2,5-facher Platz für die aktuelle Beschriftung. Noch keine Buttonverkleinerung oder Rezeptänderung vorgenommen. Danach geplant: größere Avatarköpfe/kompaktere Flächen nahe den Händen, Geberkartenverhältnis prüfen, passende Jetons samt Anzeigeablauf, eigene Kartenvorderseiten.


## 30.10.2026 – Black Jack: Schritt 2, kompakter Button als eigener Werkstattentwurf

- Nutzer beauftragt kleinere Buttonversion in der Werkstatt und Verwendung im Spiel, mit gut lesbarer, flächennutzender Beschriftung. Neuer gespeicherter Entwurf „vorschlag black Jack button – kompakt“, ID17476727364949609038305dee84e91f, Elternentwurf656dbd73ec9c45a1b86791b2e3a0fcb0 unverändert erhalten. Ausschließlich Einstellungen Größe20→17, Formhöhe90→104 und Schriftgröße100→120 Prozent geändert. Native Breite240→204px (15Prozent schmaler), Höhe73,172→71,375px, Cinzel20→20,4px. Zweizeilige lange Texte passen ohne zusätzliche Schriftverkleinerung in die Endfassung. Dunkles altes Nussbaumholz, Farben, Kontur,180ms Druckbewegung und Spielstein-Klang25Prozent übernommen.
- Vorhandenen build_preview.py mit neuer Rezeptkennung ausgeführt. Laufendes Spiel, archivierte Vorschau und Antwortkopie verwenden denselben unveränderten gespeicherten Entwurf und den kanonischen Werkstattrenderer; keine neue Seitenvariante oder Größen-/Schrift-CSS-Korrektur. Tischgrafik, Avatarpositionen, Karten und Spielregeln nicht verändert. Alle vor dieser Arbeit erfassten bestehenden Bibliotheksdateien sowie Originaltischbild, Raumerweiterung und kanonische Avatarkomponente SHA-256-identisch. Genau ein neuer Rezeptdatensatz.
- Werkstattstart zunächst blockiert: veraltete neutrale Quellennachweise für Spieler/Anzeigen nach den früheren Änderungen. Bestehende capture_generated_indicators.mjs und capture_generated_players.mjs erneut ausgeführt (reine VM-Darstellung, keine Browser-/DB-/Spielaktion);18 Anzeigen- und27 Spielerbeispiele aktualisiert. Danach Bibliothek → neuen Entwurf ansehen → im Button-Editor öffnen sowie erneutes direktes Öffnen nach Neuladen tatsächlich geprüft: Größe17, Höhe104, Cinzel120Prozent, gespeicherter Stand; Vorschau204×71,375px bei20,4px Schrift. Testbutton gedrückt, Druck-/Klangstatus für180ms/25Prozent angezeigt. Keine vorhandenen Entwürfe überschrieben.
- Endfassung im UI-Prüftisch für Versicherung/Ohne Versicherung/Verlassen sichtbar geprüft: bei1911×910 alle204×71,375px und20,4px Schrift; bei1280×720 alle163,188×57,094px und16,319px Schrift. Bestehender Hugo-Tisch Runde252 nur lesend geöffnet: fünf Aktionen Ziehen/Halten/Verdoppeln/Teilen/Aufgeben und äußerer Verlassenbutton haben neue Rezeptkennung; bei1911×910 alle204×71,375px mit20,4px Schrift. Bei1280×720 fünf Aktionen proportional137,063px/13,706px Schrift, Verlassen163,188px/16,319px. Keine Browserwarnungen/-fehler und keine Spielaktion für den Nutzer ausgelöst. Kein Neustart der beiden vorhandenen Spielserver erforderlich; eine geöffnete Seite muss neu geladen werden.
- Neun Kartenpräsentationsprüfungen, JS-Syntax und neun Werkstatt-Spielerquellenprüfungen bestanden. Von elf Anzeigenquellenprüfungen zehn bestanden; breitere Inventurprüfung meldet weiterhin zwei nicht erfasste bestehende Blackjack-Anzeigen (bj-sound-status und bj-status im unveränderten _blackjack_table.html). Diesen Inventurrest nicht als bestanden ausgegeben und keine zusätzliche Anzeige-Gestaltung begonnen. Die anfänglichen Socket-Beschränkungen der HTTP-Prüfungen durch erlaubten lokalen Testzugriff aufgelöst.
- Belege/Sicherungen: runtime/blackjack-compact-button-20261030/ mit before/, recipe.json, verification.json, live-verification.json, preservation.json, tests-players.txt, tests-indicators.txt, werkstatt-kompakt.png und punkt2-im-spiel.png. Quellenmanifest/README aktualisiert. Eigener UI-Prüfdienst beendet, Werkstatt8776 und beide bisherigen Offline-Spiele bleiben erreichbar. Ausschließlich lokal, keine Veröffentlichung oder Änderung echter Kontowährung. Nächster Gestaltungsschritt3: größere Avatarköpfe, kompaktere Anzeigen nahe den jeweiligen Händen.


## 30.10.2026 – Black Jack: Meldung Runde260 und Schutz beim Buttonwechsel

- Nutzer meldet in Runde260 zwei erhaltene Karten und sofortiges Aufdecken der Bank, danach Vermutung eines verzögerten zusätzlichen Klicks auf den an derselben Stelle erscheinenden Haltenbutton. Keine sichere nachträgliche Diagnose: erste nur lesende Abfrage fand bereits Einsatzphase nach Runde260, spätere Sicherung nach262. Singleton speichert keine Rundengeschichte; auch lokale Rohkopie enthielt nur262, nicht260. Sofortiges Aufdecken bei Bank-Natural wäre nach vorhandener Engine zulässig, ist für260 nicht belegt. Weder Kartenwerte noch angenommene Fehlaktion als Tatsache ausgegeben. Keine Ergebnisse/Guthaben berichtigt.
- Konkrete Schwachstelle der Eingabesicherung behoben: Während laufender Anfrage wurden die vorhandenen Buttons optisch nicht gesperrt und durch Animations-/Layout-Rendern konnten erneut aktive Buttons erscheinen; pending verhinderte zwar gleichzeitige weitere Anfragen, schützte jedoch nicht den anschließenden Funktionswechsel vor verspäteten Eingaben. Buttons jetzt während pending gesperrt. Gemeinsamer game-spezifischer Eingabeschutz verlangt für Maus-/Touchaktionen einen frischen Druck auf genau diesen aktiv verfügbaren Button. Druckbeginn auf deaktiviertem/ersetztem Button, vor seiner Erzeugung aufgezeichnete Eingaben und Doppelklicknachlauf verworfen. Schneller Zweitklick unter600ms an derselben Position (unter16px) wird bei gewechseltem Kommando nicht zur neuen Aktion. Tastatur-/Assistenzaktivierung erhalten. Kanonischer Werkstattbutton einschließlich Form, Schrift, Bewegung und Klang unverändert.
- Neun gezielte Eingabesicherungsprüfungen und neun Kartenpräsentationsprüfungen bestanden; JS-Syntax bestanden. Eigener reiner UI-Prüftisch ohne Konten/Datenbank, künstliche0,4s Antwortverzögerung: echter Browser-Doppelklick auf Einsatz → trace genau[bet], Bankkarte bleibt verdeckt, eigener17er-Spielzug mit Ziehen/Halten verfügbar → später bewusst Halten → trace genau[bet,stand] und erst dann Bank aufgedeckt/Ergebnis. Keine Browserwarnungen/-fehler. Bestehenden Hugo-Tisch nur lesend mit neuer Datei geöffnet, inzwischen Einsatzphase269, keine Browserwarnungen/-fehler. Kein Spielzug für den Nutzer ausgelöst und kein Neustart der normalen Dienste nötig. Geöffnete Spielseite für den neuen Schutz neu laden.
- Dateien: static/blackjack-action-intent.js, static/blackjack-seating.js, tests/test_blackjack_action_intent.mjs; Quellenmanifest und README aktualisiert. Belege/Sicherung unter runtime/blackjack-round260-20261030/: observed-state.json, observed.sqlite3/raw.sqlite3 (nur Sicherung), blackjack-seating-before.js, browser-verification.json, nach-doppelklick.png. Eigener UI-Prüfdienst nach Prüfung beendet. Ausschließlich lokal, keine Veröffentlichung und keine Änderung echter Kontowährung. Ursache der konkreten Runde260 bleibt ausdrücklich unbestätigt.


## 30.10.2026 – Black Jack: Klickschutz ohne Ausgrauen oder verlorenes Buttonfeedback

- Nutzerkorrektur ersetzt die native visuelle Sperre des letzten Schritts: Buttons sollen Druckbewegung/Klang behalten. Vorige Umsetzung setzte disabled unmittelbar im Klickhandler; diese Sperre entfernte die Rückmeldung und ist entfernt. Dynamische Tischbuttons rendern jetzt mit normalem gespeicherten Werkstattzustand. Logische Verfügbarkeit (Anfrage, Austeilen, Verbindung, fehlendes Guthaben) wird im bestehenden Eingabeschutz separat geprüft und semantisch per aria-disabled angegeben. Kein neues Erscheinungsbild und keine CSS-Ausnahme. Während einer Anfrage wird der gedrückte Button nicht durch Rendern ersetzt; laufende Druckanimation kann zu Ende laufen. Physische Rückmeldung ist keine zweite Serveraktion.
- Eingabesicherung zusätzlich um unabhängige Verfügbarkeitsfunktion erweitert: frischer Druck während nicht ausführbarer Aktion darf später nicht zum Zug werden. Bestehender Schutz gegen verzögerte/Doppelklickeingaben erhalten; Tastatur-/Assistenzwege erhalten. 13 gezielte Eingabeprüfungen und neun Kartenpräsentationsprüfungen sowie JS-Syntax bestanden.
- Getrennter reiner UI-Prüftisch ohne Konten/DB mit künstlicher2s Antwortverzögerung: Doppelklick auf Einsatz → genau[bet], 244 DOM-Einzelbilder während Anfrage, kein natives disabled,25 Bilder mit laufender Druckanimation und gemessener Bewegung von−0,935px bis+1,462px, Klangstatus Spielstein setzen/25Prozent. Screenshot während laufender Anfrage zeigt normalen dunklen Holzbutton. Danach bewusster Doppelklick Halten → genau[bet,stand]. Keine Browserwarnungen/-fehler. Bestehenden Hugo-Tisch Runde273 nur lesend mit neuer Datei geladen; eigene13 gegen Hugo17, normale Buttons, keine Browserwarnungen/-fehler. Keine eigene Aktion im Nutzerbestand, keine Spiel-/Kontodaten verändert und kein Neustart der laufenden Dienste erforderlich. Nutzer muss die bereits geöffnete Spielseite neu laden.
- Nur blackjack-seating.js, blackjack-action-intent.js und die vorhandene Eingabeprüfung angepasst; Werkstattrezept, Buttonrenderer, Schrift, Klang, Tischbild und Avatarpositionen unverändert. Manifest/README aktualisiert. Belege und Vorstände: runtime/blackjack-button-feedback-20261030/ (feedback-verification.json, live-check.json, button-ohne-ausgrauen.png, *.before). Eigener Prüfdienst nach Abschluss beendet; normale Spielserver laufen weiter. Ausschließlich lokal.

## 31.10.2026 – Black Jack: Schritt 3, größere Köpfe und kompakte Spieleranzeigen

- Vom Nutzer beauftragten Schritt3 nach ausdrücklicher Fortsetzung umgesetzt und sichtbar geprüft. Kanonische player-portrait-Komponente um die gemeinsame Variante layout=table ergänzt: runder Kopf75×75px bei voller Größe (zuvor etwa50,7px), separates kompaktes Namens-/Geldfeld204×66,813px. Alle belegten Plätze verwenden dieselbe Innenkomposition mit Bestand, Einsatz und Rundengewinn; volle Komponente proportional skaliert. Goldakzent folgt der tatsächlich aktiven Hand. Default-/Armeevarianten unverändert. Keine Konto-/Spielernamen umgeschrieben.
- Bisherige Rand-Docks und eigener fester Platz unten links entfernt. Äußere Köpfe über ihren jeweiligen Händen, mittlere Anzeige nahe der eigenen Hand neben der Bankreihe. Bei einer langen Geberhand begrenzte seitliche Verschiebung und Ausweichen nach oben. Neun Geberkarten zeigten zunächst eine Berührung des linken Geldfelds und zu große Rechtsverschiebung der Mitte; im zuständigen Layout korrigiert und erneut sichtbar geprüft. Kartenanker am jeweiligen Kreis, Tischgrafik und Werkstattbutton erhalten. Zuständige CSS-Regeln ersetzt/konsolidiert; keine nachträglichen Korrekturblöcke.
- Getrennte reine Darstellungsprüfung ohne Konten/Datenbank: drei belegte Plätze und zwei eigene Split-Hände sowie neun Geberkarten mit Rundengewinn+1.000 bzw. Verlust−500 bei1024×768,1280×720 und1911×910. Keine Überschneidungen mit Karten, Bankzahl oder Einsatzmarkern. Bei390px dieselbe vollständige Komponente unter dem Bild ohne horizontales Überlaufen; Geldwerte sichtbar. Keine Browserwarnungen/-fehler. 13 Eingabe- und neun Kartenpräsentationsprüfungen sowie JS-Syntax bestanden. Alle46 vorab erfassten Bibliotheks-/Originaldateien SHA-256-identisch, einschließlich Originaltisch, Buttonrezept/-renderer, Porträt-JS und Kartenbewegung.
- Nach der Pause waren keine lokalen Dienste mehr aktiv. Normalen Offline-Starter8765 mit vorhandenem Bestand gestartet. Nutzer meldete sich selbst erneut an. Bestehenden normalen Tisch mit echtem Profil Stormseed nur lesend geöffnet: Runde32, mittlerer Platz, Einsatzphase, Kopf75px/Textfeld204px, Rezept17476727364949609038305dee84e91f, Originalbild1672×941 mit object-fit:contain und keine Browserwarnungen/-fehler. Kein Spielzug für den Nutzer ausgelöst, keine Spiel-/Kontodaten durch Prüfskripte geändert. Mehrspieler-/Geber-Grenzfälle ausschließlich im getrennten UI-Prüftisch geprüft. Der bisherige Hugo-Dienst8780 wurde nach der Pause nicht gestartet.
- Änderungen: static/player-portrait.css, static/blackjack-table.css, static/blackjack-seating.js sowie README/Quellenmanifest. Belege/Sicherungen unter runtime/blackjack-avatar-step3-20261030/: before/, verification.json, live-verification.json, protected-check.json, drei-plaetze-split-1280.png, drei-plaetze-split-1911.png, lange-geberhand-1280.png, lange-geberhand-1911.png, mobile-390.png und punkt3-im-spiel.png. Ausschließlich lokal, keine Veröffentlichung. Nächster Gestaltungspunkt4 bleibt Prüfung des Größenverhältnisses der Geberkarten; Jetons und Kartenvorderseiten folgen später.

- Anschließend übermittelter Bildausschnitt auf Rückfrage geklärt: Nutzer meint die wegen Geldmangel fehlende Versicherung, nicht die Avatarposition. Keine weitere Positionsänderung daraus abgeleitet.


## 31.10.2026 – Black Jack: nicht leistbare Versicherung erklärt den Geldmangel

- Nutzer zeigt Versicherung bei15 iKühen Restguthaben und wünscht den Button weiterhin sichtbar; Klick soll erklären, dass Geld fehlt. Aktuelle Engine liefert bei zu wenig Guthaben nur no-insurance, deshalb fehlte der Button. Darstellung ergänzt Versicherung ausschließlich bei offener eigener Versicherungsentscheidung und zu wenig Guthaben. Kein Ändern der legalen Serveraktionen oder Versicherungsregel.
- Klick auf diesen normalen Werkstattbutton lässt Druckbewegung/Klang auslaufen und zeigt danach im vorhandenen Statusbereich die benötigten250 und verfügbaren15 Test-iKühe. Keine Wette/Anfrage wird gesendet, Entscheidung und Guthaben unverändert. Der bisherige Eingabeschutz bleibt aktiv; keine native Deaktivierung/Ausgrauung. Ohne Versicherung und leistbare Versicherung bleiben reguläre Serveraktionen. Nur blackjack-round-view.js und eine lokale Erklärung im bestehenden act-Ablauf von blackjack-seating.js angepasst.
- Separater UI-Prüftisch ohne Konten/DB: beide Buttons sichtbar, Fehlklick ergibt genaue Geldmeldung, Guthaben15 und verdeckte Bankkarte bleiben bestehen, kein insurance-POST. Danach bewusste reguläre Klicks liefern trace exakt[no-insurance bei15, insurance bei9500]. Normaler Buttonklang25Prozent sichtbar bestätigt. Keine Browserwarnungen/-fehler;13 Eingabe- und neun Kartenpräsentationsprüfungen sowie JS-Syntax bestanden. Bestehenden normalen Spieltisch8765 neu geladen, inzwischen Runde38/eigene15, neue Module und unveränderte Werkstattbuttons sichtbar; die gemeldete Versicherungssituation dort nicht erzwungen und kein Spielzug für den Nutzer ausgelöst.
- Belege: runtime/blackjack-avatar-step3-20261030/insurance-verification.json, insurance-action-trace.json, versicherung-guthaben-hinweis.png und vor Änderung gesicherte JS-Dateien. README/Quellenmanifest aktualisiert. Originaltisch/Bibliothek/Buttons unverändert, ausschließlich lokale Darstellung. Nächster Gestaltungspunkt4 bleibt Größenverhältnis der Geberkarten.

- Abschluss: Eigenen UI-Prüfdienst8782 beendet und eigene Prüftabs geschlossen. Normaler Offline-Dienst8765 und der vom Nutzer angemeldete Chrome-Tisch bleiben offen; keine temporäre Fenstergrößenvorgabe mehr aktiv.


## 31.10.2026 – Black Jack: eigener Avatar am Einsatz und Schritt4 Geberkartengröße

- Nutzer verwirft ausdrücklich die bisherige eigene Avatarposition neben der Bank und wünscht ihn links neben seinen Jetons. Diese neue Anweisung ersetzt die mittlere eigene Position aus Schritt3. Unveränderte kanonische Porträtkomponente an den eigenen Einsatz gebunden. Für den linken Sitz reicht die Breite zum Rand nicht; auf Rückfrage Nutzerwahl „teste option1“ umgesetzt: dort Anzeige unter den Jetons. Rechter Sitz kann neben geteilten mittleren Karten nach unten ausweichen. Statusmeldungen bei tatsächlicher Textberührung begrenzt/eingerückt; keine neue Randposition und keine zusätzliche Avatar-Innenkomposition.
- Geberkartengröße tatsächlich gemessen: bei1911×910 zuvor sichtbare Breite72,721px gegen96,741px Spielerkarte (etwa75Prozent). Native Geberbreite70→80px, neue responsive Regelclamp(30px,5.2cqw,80px); sichtbar83,238px gegen weiterhin96,741px, etwa86Prozent. Rund14Prozent größer, unverändertes Seitenverhältnis und45Grad. Bankanker50Prozent/52Prozent, Kartenanker der Spieler und Originaltischbild unverändert. Ein höherer Bankanker wurde nur im getrennten Prüftisch betrachtet und verworfen, weil Karten dann zu weit auf der gemalten Chipablage liegen.
- Größere Bankkarten berührten einzelne Handbeschriftungen. Konkreten Konflikt vor endgültiger Änderung benannt; Nutzer erlaubt bei Bedarf seitliche Handtexte und verweist auf Platz zwischen Karten und Jetons. Nur betroffene Handtexte bevorzugt zwischen Karten und Einsatz gesetzt; wenn dort Karten, Jetons oder Avatar liegen, seitlicher freier Platz. Reine Positionsverschiebung bei unverändertem Text-/Kartenaufbau, Karten bleiben stabil an ihren Kreisen. Geber-, Spieler-, Karten- und Werkstattkomponenten weiter gemeinsam.
- Getrennter UI-Prüftisch ohne Konten/DB: drei Spieler und zwei geteilte mittlere Hände bei1280×720 und1911×910, neun Geberkarten/Ergebnis mit Gewinn und Verlust auf beiden Größen, linker/rechter eigener Sitz bei1024×768. Keine Überschneidungen von Avataren mit Karten, Geldmarkern, Bankzahl, Handtext oder Aktionsbuttons; keine Banküberschneidung mit Handtext. Schmale390px-Ansicht ohne horizontales Überlaufen der Avatare; die bestehende enge Karten-/Beschriftungsdarstellung unter900px wurde ausdrücklich nicht als korrigiert ausgegeben. Keine Browserwarnungen/-fehler in den geprüften Browserprotokollen.13 Eingabe- und neun Kartenpräsentationsprüfungen sowie JS-Syntax bestanden.
- Normalen laufenden Offline-Tisch8765 mit neuer Darstellung nur lesend geladen: Runde72, echtes ProfilStormseed, Avatar links neben Einsatz, größere Geberkarten und Handtext unter den Karten sichtbar; keine Browserwarnungen/-fehler in live-verification.json. Nutzer spielt weiter, Screenshots können daher andere Karten als die vorausgegangene Messung zeigen. Kein Spielzug durch Codex ausgelöst, keine Spiel-/Kontodaten durch Prüfskripte geändert und kein Neustart des normalen Spiels.
- Dateien: static/blackjack-table.css, static/blackjack-seating.js, static/blackjack-round-view.js; README/Quellenmanifest aktualisiert.48 von49 gesicherten geschützten Dateien SHA-256-identisch; einzig round-view.js für freigegebene Beschriftungspositionen verändert. Originalbild, Raumerweiterung, Porträtkomponente, Buttonrezept/-renderer, Schrift, Klang und Kartenbewegung identisch. Belege/Sicherungen: runtime/blackjack-avatar-and-dealer-step4-20261031/ mit before/, verification.json, live-verification.json, protected-check.json, nachher-mitte-split-1280.png, nachher-mitte-split-1911.png, lange-geberhand-1280.png, lange-geberhand-1911.png, eigener-platz-links-1024.png und punkt4-im-spiel.png. Ausschließlich lokal, keine Veröffentlichung. Nächster Gestaltungsschritt5: passende Jetons entwerfen.

- Abschluss: Eigenen UI-Prüfdienst8782 und Prüftab beendet, temporäre Fenstergröße zurückgesetzt. Normaler Dienst8765 und bestehender Chrome-Tisch laufen weiter.


## 31.10.2026 – Black Jack: Schritt5, passende Jeton-Grafiken

- Nutzer bestätigt als nächsten Schritt passende Jetons. Drei transparente Originalgrafiken mit eingebauter Bildgenerierung erstellt, Referenz ausschließlich die Jetons vor dem Geber im vorhandenen Tischbild: Waldgrün, Burgunder und Anthrazit, matte abgenutzte Flächen, elfenbeinfarbene Einlagen, warme Beleuchtung und schräge Sitzansicht. Tischbild nicht bearbeitet. PNG-Originale mit Alpha unverändert in static/jetons/blackjack/ kopiert und zusätzlich über vorhandenen ImageStore als lesende Rastergrafiken unter Icons gesichert. Kein weiterer Werkstatteditor aktiviert.
- Bibliothekskennungen: grünimage-1f9cb8f0c2d14026aa6fd703b62c5ca1, rotimage-951f5c820ce64c9a8fb735ca79f68cf5, anthrazitimage-99cae58293974d888fd3e959cfec7d1b. Unveränderte Quelldateien, Prüfsummen und Generierungsquellen in offline-preview/blackjack-v1/jeton-assets.json. Grün aktiv, andere Farben gesicherte Alternativen; keine Zuordnung zu neuen Nennwerten. Bibliothekseinträge und Originaldateien direkt eingelesen und per Prüfsumme validiert; keine zusätzliche Behauptung einer sichtbaren Werkstattprüfung.
- Alte kleine CSS-Scheibe22×15px und umgebenden Rahmen durch eine gemeinsame realistische Jeton-Einsatzanzeige ersetzt. Bildbereich bei1911×910 etwa67,906×49,688px, proportional überclamp(40px,4.2cqw,70px). Live-Gesamteinsatz in der hellen Mitte, längere Zahlen passend innerhalb derselben Komponente. Nur bestehende öffentliche Einsatzwerte; keine neue Abbuchung, Stückelung oder Auszahlungslogik. Am linken eigenen Sitz folgt der Avatar der tatsächlichen Jeton-Unterkante mit8px Abstand. Sonstige Avatarpositionen/-Innenkomposition, Tischbild, Karten, Buttons und Klang unverändert. Zuständige CSS-Regeln ersetzt, keine Korrekturblöcke angehängt.
- Getrennter UI-Prüftisch ohne Konten/DB: drei Plätze mit500/1.000/500 bei1911×910 und1280×720, linker eigener Sitz1024×768, keine Berührung mit Karten, Avataren oder Buttons; ohne Einsatz keine Jetons. Keine Browserwarnungen/-fehler.13 Eingabe- und neun Kartenpräsentationsprüfungen sowie JS-Syntax bestanden. Alle49 bestehenden geschützten Original-/Bibliotheks-/Komponentendateien SHA-256-identisch. Genau drei additive Bilddatensätze mit unveränderten Originalkopien.
- Laufenden normalen Offline-Tisch8765 nur lesend neu geladen: Runde80, Stormseed, eigene11,500 Einsatz, neuer grüner Jeton63,797×46,688px und keine Browserwarnungen/-fehler. Keine Spielaktion für den Nutzer und kein Eingriff in Spiel-/Kontodaten durch Prüfskripte, kein Neustart des normalen Dienstes. Belege/Sicherung: runtime/blackjack-jetons-step5-20261031/ (before/, generated-assets.json, protected-check.json, verification.json, live-verification.json, jetons-drei-plaetze-1911.png, jetons-drei-plaetze-1280.png, jetons-linker-platz-1024.png, jetons-im-spiel.png). Quellenmanifest/README aktualisiert. Ausschließlich lokal, keine Veröffentlichung.
- Nächster Schritt6 bleibt Gewinn-/Verlustdarstellung der Jetons: Gewinn sichtbar ergänzen, Übernahme zum Guthaben und Abräumen. Bewegungen weiterhin optional. Dafür in diesem Schritt keine neue Animation oder Ablaufänderung eingeführt.

- Abschluss: Eigenen Prüfdienst8782 und Prüftab beendet; normale Fenstergröße wiederhergestellt. Offline-Spiel8765 und bestehender Chrome-Tisch bleiben geöffnet.


## 31.10.2026 – Jetons: Werkstattübernahme erst nach Nutzerfreigabe

- Nutzer korrigiert den Freigabeweg: Jetons erst in die Werkstatt aufnehmen, wenn er sie freigibt. Die zuvor ohne separate Gestaltungsfreigabe angelegten drei Bildbibliothekseinträge waren zu früh. Genau diese drei Einträge und ihre Originalkopien nach Prüfung von Kennung, Prüfsumme und Zielpfad aus design-library/ in runtime/blackjack-jetons-step5-20261031/pending-library-import/ verschoben. Reversibel gesichert, keine fremden Einträge oder Bilder verändert.
- Statische Jeton-Entwürfe und sichtbare grüne Spielvorschau bleiben erhalten. Manifest kennzeichnet alle drei Varianten ausdrücklich als Freigabe ausstehend; keine aktive library_id mehr. Wiederaufnahme der gesicherten Importdateien erst nach ausdrücklicher Nutzerfreigabe. README/Quellenmanifest aktualisiert. Prüfung: drei Kennungen nicht mehr im ImageStore-Bestand; alle sechs verschobenen Dateien unverändert gesichert und statische Bilddateien weiterhin SHA-256-identisch. Kein Neustart oder Spiel-/Konteneingriff.


## 31.10.2026 – Blackjack-Regelrecherche, unbeschriftete Stapel, offene Verlustregel

- Nutzer bezweifelt frühe Aufdeckung bei Bank-Blackjack und beauftragt Recherche. Aktuelle Primärquelle MGC RULES-Blackjack-4-9-26.pdf bestätigt Hole Card ohne frühe Prüfung sowie Peek als Alternative (Abschnitt6(i)); bei Peek endet Bank-Blackjack vor normalen Spielerzügen, bei offenem Ass vorher Versicherungswahl. Bisheriger Code entspricht Peek. Beigefügtes Blackjack Regelwerk.markdown beschreibt den allgemeinen Ablauf, legt diese Variante nicht fest. Casinos-Austria-Spielerklärung bestätigt den abweichenden Ablauf ohne zweite Bankkarte vor den Spielerzügen; nicht stillschweigend mit unserer verdeckten Anfangskarte gleichgesetzt.
- Konkrete Variantenentscheidung abgefragt: Nutzer wählt Aufdeckung erst nach Spielerzügen. Weitere notwendige Folgeentscheidung offen: MGC10(b)/11(d) gibt zusätzliche Split-/Double-Einsätze bei Bank-Blackjack zurück; MGC8 erstattet bei Aufgeben die Hälfte nur ohne Bank-Blackjack. Nutzer gefragt, ob diese Abrechnung oder Verlust aller Zusatzbeträge gelten soll. Noch keine Antwort; keine Aktivierung/Änderung des laufenden Dienstes. Engine-Core mit beim Geben festgehaltener dealer_peek-Regel vorbereitet; bestehende unmarkierte Runden bleiben Peek. Fünf neue NoPeek-Abfolgeprüfungen (Ten-Up, Versicherungsentscheidung, mehrere Spieler, Natural neben normalem Spieler, Rundenbindung) und neun bestehende Naturalprüfungen bestanden. Noch keine fertige neue Abrechnung oder Live-Regelprüfung behauptet.
- Jetonvorgabe geändert: ohne Beschriftung, grün500 stapeln; Nutzer ergänzt vorläufig schwarz250 für Restanteile, oben auflegen. Sichtbare Zahlen entfernt; die zugängliche Einsatzbezeichnung und Geldwerte am Avatar bleiben. Eine gelegte Versicherung wird beim sichtbaren Gesamteinsatz berücksichtigt. Bestehender Stapel bleibt bei identischem Betrag beim Poll erhalten. Neue verbindliche Farbwerte ersetzen die frühere Live-Summenbeschriftung.
- Rot und Schwarz sind jetzt ausdrücklich zur Bibliotheksübernahme freigegeben. Genau die vier zuvor gesicherten Original-/Metadateien nach Pfad-/Prüfsummenprüfung zurückkopiert; beide Einträge validiert. Grün weiterhin außerhalb Werkstatt gesichert, im Spiel gewählt. Keine Bilder neu erzeugt oder pixelweise verändert.
- UI-Prüftisch ohne Konten/DB: sieben Beträge250/500/750/1000/1250/1500/2000 tatsächlich geprüft, jeweilige Chipwerte korrekt, kein Rest und keine sichtbare Zahl; schwarze250 zuletzt/oben.1280×720 und linker Sitz1024×768 ohne Avatar-/Karten-/Buttonüberlagerung, keine Browserwarnungen/-fehler. Prüfung am normalen Tisch aktuell nicht erfolgt: Chrome inzwischen geschlossen/nicht verfügbar. Keine Spielaktion für Nutzer und kein Neustart des normalen Spiels.
- Bewegung auf Nutzerauftrag recherchiert, nicht implementiert. Vorschlag mit vorhandener Web Animations API:40–60px aus Richtung Avatar,220–300ms mit kleinem Bogen/softem Aufsetzen; Verlust kurz Richtung Bank und ausblenden; Gewinn erst ergänzen, dann zum Spieler. Nur neue bestätigte Vorgänge animieren, kein Poll-/Reload-Wiederholen; bestehender Klang beim Aufsetzen, reduzierte Bewegung berücksichtigen. Quellen Element.animate, Animation.finished und prefers-reduced-motion von MDN. Kein Physiksystem oder zusätzliche Bibliothek nötig.
- Belege/Quellen/Sicherungen unter runtime/blackjack-stacks-research-20261031/: before/, research.json, verification.json, protected-check.json, vier-gruene-jetons-1280.png, gruen500-schwarz250-1280.png. Quellenmanifest/Jetonmanifest/README aktualisiert. Offen bleiben Abrechnungsentscheidung, vollständige NoPeek-Implementierung/Aktivierung/Spielprüfung sowie die tatsächliche Jetonbewegung.

- Abschluss der unabhängigen Arbeiten: Eigener UI-Prüfdienst8782 und Prüftab beendet, temporäre Fenstergröße zurückgesetzt. Offline-Dienst8765 läuft weiter, Chrome war vom Nutzer geschlossen. Offene Abrechnungsfrage bleibt ausstehend; NoPeek nicht aktiviert.


## 31.10.2026 – Black Jack: späte Bankaufdeckung nach veröffentlichter Regel aktiviert

- Nutzer bestätigt auf die konkrete Abrechnungsfrage die offiziellen veröffentlichten Regeln ohne eigene Sonderregelung. Zusammen mit seiner vorigen Wahl „Erst nach Spielerzügen aufdecken“ umgesetzt: Hole Card bleibt bis zum Ende der Spielerhände verdeckt, auch bei einer Zehn/Ass und tatsächlichem Bank-Blackjack. Primärquelle MGC RULES-Blackjack-4-9-26.pdf, Abschnitte6(i),8,10(b),11(d), https://massgaming.com/wp-content/uploads/RULES-Blackjack-4-9-26.pdf. Keine Behauptung einer einzigen weltweit verbindlichen Blackjackvariante; die konkret recherchierte Variante mit später Prüfung gilt an diesem Tisch.
- Bei Bank-Blackjack wird der ursprüngliche Einsatz genau einmal pro Spieler verloren; zusätzliche Split-/Double-Beträge kommen zurück. Natürlicher eigener Blackjack bleibt Gleichstand. Bei Aufgeben gibt es die Hälfte nur ohne Bank-Blackjack; andernfalls Verlust des ganzen Grundeinsatzes. Versicherung separat und erst bei endgültiger Bankaufdeckung abrechnen. Der bereits ausdrücklich gewünschte Verlust aller noch liegenden Einsätze beim Verlassen bleibt erhalten. Spieler mit21 bzw. geteilten Assen ohne weitere zulässige Entscheidung werden wie bisher automatisch abgeschlossen.
- Beim Geben gespeicherte round_rules halten die gewählte Regel für die ganze Hand fest. Unmarkierte bereits laufende Hände bleiben Peek. BLACKJACK_DEALER_PEEK=False im normalen Offline-Starter8765 sowie im derzeit nicht gestarteten optionalen Hugo-Dienst8780 gesetzt; Clock übernimmt dies nur als Tischregel für kommende Hände. Öffentliches dealer_peek/next_dealer_peek erklärt aktuellen Ablauf und Übergang in den Tischregeln. Keine private Bankkarte vorzeitig an den Browser geliefert. Keine neue Regelaktivierung im entfernten Serverbestand.
- Prüfungen:219 Blackjack-Pythonprüfungen erfolgreich, darin15 gezielte NoPeek-Enginefälle und zwei zusätzliche Fixed-Stake/Clock-Integrationsfälle;13 Eingabe- und neun Kartenpräsentationsprüfungen sowie JS-Syntax bestanden. Neue Fälle umfassen mehrere Spieler, Natural neben normaler Hand, Versicherung, Aufgeben, geteilte/verdoppelte und überkaufte Hände, einmalige Rückzahlung und Übergang aus laufender alter Runde.
- Separater In-Memory-Prüftisch8782 mit derselben echten Engine und kanonischer Spieloberfläche, ohne Datenbank/Spielerkonten: sichtbare Zehn mit verdecktem Ass lässt Verdoppeln zu, danach nur500 Verlust; offenes Ass lässt nach „Ohne Versicherung“ normale Spielerentscheidung zu; Paar Achten lässt beide Hände teilen und verdoppeln, Bank bis zum letzten Spielerzug verdeckt, am Ende2.000 gelegt/1.500 zurück/500 Verlust. Exakte UI-Aktionsfolge und öffentliche Zustände in engine-ui-trace.json, Screenshots vor/nach sowie beide geteilten Hände dokumentiert. Keine Browserwarnungen/-fehler im Prüftisch.
- Vor Neustart SQLite-Backup des vorhandenen normalen Spiels erstellt und31 Tabellen fingerprinted. Exakt zugeordneten Offline-Prozess neu geladen, über den regulären start_local.py-Starter. Vor/nach Neustart nur blackjack_game verändert, darin nur table_rules; Runde84, Handkarten, Guthaben und Sitz unverändert. Keine Hand des Nutzers gespielt, keine Konto-/Ergebnis-/Historienänderung durch Prüfskripte.
- Nutzer hat sich selbst angemeldet. Anschließend tatsächlichen Weg Startseite → games collection → Kartentische → Black Jack geöffnet. Echtes Stormseed-Profil, Runde84, eigene7Herz/4Karo gegen5Kreuz mit verdeckter Karte,12.750 Test-iKühe/500 Einsatz erhalten. Tischregeln zeigen laufende Peek-Hand und späte Aufdeckung ab nächster Runde. Unbeschrifteter grüner500er jetzt auch im normalen Spiel sichtbar geprüft. Keine Browserwarnungen/-fehler. Den Bank-Blackjack-Grenzfall im persönlichen Tisch nicht erzwungen; sichtbar mit echter Engine ausschließlich getrennt geprüft.
-55 geschützte Dateien unverändert, einschließlich Tischbild, Raumerweiterung, Werkstattbuttons/Renderer, Porträtkomponente, Kartenbewegung, Bildbibliothek und Jetonoriginalen. Änderungen auf Engine, Clock, Offline-Konfiguration und Regel-/Ergebnisbeschreibung begrenzt; README/Quellenmanifest aktualisiert. Belege und Vorstände: runtime/blackjack-no-peek-activation-20261031/ mit quiz-before-reload.sqlite3, db-before.json, db-after-reload.json, tests.txt, verification.json, live-verification.json und Screenshots.
- Jetonbewegung bleibt recherchierter Vorschlag, noch nicht implementiert. Nächster Gestaltungsschritt6 bleibt Gewinn-/Verlustdarstellung mit Ergänzen und Abräumen; Kartenvorderseiten und lebendiger Geber bleiben nachfolgende Punkte. Bestehende gestapelte grüne500er und vorläufige schwarze250er ohne Beschriftung erhalten. Eigener Prüfdienst/Prüftab werden beendet, normaler Offline-Tisch bleibt offen.

## 31.10.2026 – Jetonbewegung: Zwischenstand auf Nutzerwunsch pausiert

- Nutzer beauftragt dezente Bewegung beim Setzen zum Einsatzfeld, Gewinn erst ergänzen/dann Avatar, Verlust Richtung Geber; Tischgrafik und Buttons unverändert. Anschließend ausdrücklich „Wir machen später weiter“: Arbeit hier beendet, keine weitere Prüfung/Umsetzung nach der Pause.
- Unfertiger lokaler Stand gespeichert: neues static/blackjack-jeton-motion.js mit gemeinsamer Stapeldarstellung/Bewegung aus öffentlichen Einsätzen, Warteschlangen je Sitz, Abrechnung erst nach Kartenbewegung, Richtungswegen bis48px,260ms hinein/290ms hinaus und140ms sichtbarer Gewinn-Ergänzung. Neu-/Bestandsanzeige ohne Wiederholung bei Poll, Initialladen oder verstecktem Tab; reduced-motion-Zweig vorhanden. Keine Konto-/Abrechnungsänderung. Anbindung in blackjack-seating.js, Klangzuständigkeit in blackjack-round-view.js, zwei zuständige CSS-Regeln in blackjack-table.css; unbenutzte points-Konstante in seating.js noch aufzuräumen.
-22 neue reine Jetonplanungs-/Stückelungsprüfungen sowie13 bestehende Eingabe- und neun Kartenpräsentationsprüfungen bestanden; JS-Syntax geprüft. Keine vollständige Abschlussprüfung und kein fertiger Live-Status behauptet. Tisch-/Buttonoriginale zuvor gesichert, abschließender Hashvergleich noch offen.
- Eigener In-Memory-Prüfdienst läuft auf8782, gestartete PID7664, Skript runtime/blackjack-jeton-motion-20261031/serve_motion_check.py; keine Konten/DB. Browser-IAB-Tab8 ist vom Nutzer inzwischen sichtbar benutzt worden, zuletzt Runde3/Verlust im Prüftisch. Daher jüngere zusätzliche Spielaktionen in der Trace nicht als automatisch ausgelöste Fehler interpretieren. Nicht eigenmächtig diesen vom Nutzer geöffneten Tisch schließen. Beim späteren Beenden zuerst tatsächlichen Prozessbefehl prüfen.
- Sichtbar getrennt geprüft: Platzieren, normaler Gewinn mit ergänztem Stapel/Avatar-Richtung, Verlust zum Geber und anschließendes Abräumen. RAF-Spuren unter runtime/blackjack-jeton-motion-20261031/gewinn-evidence.json und verlust-evidence.json. Browserprotokoll bis zur Pause ohne Warnungen/Fehler. Blackjack-Test zeigte Gewinn-Ergänzungsereignis, aber die anschließende Prüfung wurde durch zwischenzeitliches Spielen im Prüftisch uneindeutig; gezielt erneut prüfen, nicht als abgeschlossen ausgeben.
- Offen: Browserprüfung von Blackjack/250-Anteil, gemischten Split-Händen, sofortigem Folgeeinsatz während Auszahlung, Neuladen/Poll ohne Wiederholung, reduzierter Bewegung und äußeren Sitzen. Bewegungsrichtung/-größe anhand gespeicherter DOM-Frames noch abschließend auswerten. Dokumentation/Manifest für fertigen Stand noch nicht aktualisiert.
- Normaler Offline-Dienst8765 bleibt bestehen. Bestehender Chrome-Tab30644766 war vor Änderungen nur lesend geprüft: Runde88/Einsatzphase, Stormseed rechts,13.250 Test-iKühe. Neue Fassung dort noch nicht geladen/abschließend geprüft. Kein eigener Spielzug im Nutzerbestand, kein Neustart des normalen Dienstes. Sicherungen/geschützte Dateiliste unter runtime/blackjack-jeton-motion-20261031/before/ und protected-before.json.

## 31.10.2026 – Jetonbewegung vom Nutzer gestalterisch freigegeben

- Nutzer bestätigt „Das passt so mit der Jetonbewegung“ und fragt nach dem nächsten Punkt. Gestalterische Freigabe festgehalten; keine neue Ausarbeitung oder Bibliotheksübernahme daraus abgeleitet.
- Die vor der Pause offenen technischen Abschlussprüfungen und Prüfung am normalen Offline-Tisch bleiben offen. Danach folgt als nächster Gestaltungspunkt die Kartenvorderseite passend zum alten Tisch: zunächst wenige Muster zur Freigabe, anschließend gemeinsamer Kartensatz. Lebendiger Geber bleibt nachfolgender eigener Punkt.


## 31.10.2026 – Jetonbewegung technisch abgeschlossen, Kartenmuster beauftragt

- Nach Nutzerfreigabe der Gestaltung und ausdrücklichem Weiter-Auftrag die offenen Prüfungen abgeschlossen.22 neue Jetonplanungs-/Stückelungsprüfungen,13 Eingabe- und neun Kartenpräsentationsprüfungen sowie JS-Syntax bestanden. Bewegung basiert nur auf öffentlichen Einsätzen/Rückzahlungen; keine Buchungs-/Regeländerung. Unbenutzte seating.js-Konstante entfernt.60 geschützte Original-/Bibliotheks-/Regel-/Button-/Porträt-/Kartendateien SHA-256-identisch.
- Eigenen getrennten In-Memory-Prüftisch mit echter Engine auf8783 gestartet, damit der vom Nutzer benutzte Prüftisch8782 nicht verändert wird. Sichtbar geprüft: Blackjack-Auszahlung1.250 mit grün/grün/schwarz, gemischte geteilte/verdoppelte Hände mit gleichzeitigem Verlust/Gewinn trotz Netto0, sofortiger nächster Einsatz während laufender Auszahlung, linker/rechter Sitz, Aufgeben mit250 Verlust/250 Rückgabe, Neuladen und gleichbleibende Polls ohne Wiederholung. Reduzierte Bewegung im Prüftisch emuliert, keine Systemeinstellung geändert: keine Flugobjekte, vollständiges Aufräumen. Browser ohne Warnungen/Fehler. Aktuelle Canonical-Sprites behalten ihre Größe während des Flugs. Keine persönliche Hand gespielt.
- Normalen Offline-Tisch8765 nur neu geladen: echtes Stormseed-Profil, Runde88/Einsatzphase,13.250 Test-iKühe, neue Jetonkomponente vorhanden, normaler unveränderter Rezeptbutton17476727364949609038305dee84e91f und Originaltischbild. Kein Testeinsatz am persönlichen Tisch und kein Neustart des normalen Dienstes. Aktuelle Darstellung/Komponentenprüfung dort, Bewegungs-Grenzfälle getrennt mit echter Engine. Belege: runtime/blackjack-jeton-motion-20261031/verification.json, live-verification.json, protected-check.json, final-*.json und jetons-normaler-tisch.png. README/Manifest aktualisiert.
- Nutzer hat anschließend Kartenmuster als nächsten Gestaltungsschritt autorisiert: Ass, Zahlenkarte, König passend zum Ambiente, zunächst zur Ansicht/Freigabe. Bisherige Spielkarten bis zur Freigabe erhalten; keine automatische Bibliotheksübernahme. Lebendiger Geber weiterhin nachfolgender eigener Punkt.


## 31.10.2026 – Drei Kartenvorderseiten als Freigabemuster gezeigt

- Beauftragte Muster Pik-Ass, Karo-Sieben und Kreuz-König erstellt. Gemeinsamer SVG-Aufbau280×380 mit warmem Elfenbeinpapier, zurückhaltender Papierstruktur/Randabnutzung, dunklen bzw. burgunderroten klaren Druckwerten und korrekten Kartensymbolen. Eigenes Königsmotiv per integrierter Bildgenerierung als transparente PNG erstellt, Original unverändert gesichert. Klassisches Doppelbild durch dieselbe Originalgrafik im gemeinsamen Kartenrenderer, keine graue Bildfläche.
- Lokal unter /static/blackjack-kartenmuster-v1.html geöffnet und sichtbar geprüft: drei große Muster plus dieselben Karten klein/schräg zur Beurteilung am Tisch. Alle sechs Bildvorkommen laden, sieben Haupt-Karos exakt geprüft, keine Browserwarnungen/-fehler. Vorschauseite bleibt geöffnet. Screenshot/Prompt/Quellen/Renderer unter offline-preview/blackjack-v1/card-front-drafts/, Karten-SVGs/Originalkopie unter static/cards/blackjack/front-drafts-v1/.
- Gestalterische Freigabe für Kartenmuster ausstehend. Keine bisherigen Spielkarten ersetzt, kein vollständiger Satz ausgerollt und kein Import in Bibliothek/Werkstatt. Nächster Schritt nach Zustimmung: den gemeinsamen Stil auf den Kartensatz übertragen. Lebendiger Geber weiterhin danach. Eigener zusätzlicher Prüfdienst8783 und Prüftab9 beendet/geschlossen; bisheriger Nutzertisch8782 und normales Spiel8765 erhalten.


## 31.10.2026 – Freigegebener Kartensatz vollständig, Eckwerte am Tisch vergrößert

- Nutzer nimmt die drei Muster an („Sind ok, wir nehmen die“). Vollständigen Satz52 Karten in vier Farben/13 Werten mit einem kanonischen SVG-Renderer erstellt. Bube und Dame per integrierter Bildgenerierung im Stil des Königs ergänzt; alle drei transparenten Originalgrafiken unverändert im Projekt gesichert. Einheitlicher Aufbau für Papier/Rahmen/Rang/Pips/Doppelbild, ursprüngliche Kenney-Dateien und ursprüngliche Muster unverändert erhalten. Keine neue Werkstatt-Editorfläche oder entfernte Veröffentlichung.
- Nutzer meldet während der Umsetzung am Prüftisch zu kleine Kartenwerte. Diese konkrete Korrektur umgesetzt: Eckwerte42→96, Gewicht700, Farbsymbole25→36; Zentralpips für die größeren Ecken eingerückt. Auch10 passt in die freigehaltene Ecke. Karte bleibt280×380, sichtbare Kartengröße und45Grad unverändert. Figuren, Papier/Tisch, grüner Rücken, Jetonbewegung und Werkstattbuttons erhalten. Ursprüngliche drei Musterdateien bleiben als historische Freigabeversion erhalten, die Vorschauseite verwendet jetzt den aktiven gemeinsamen Satz.
- Ein anfänglich versuchter Canvas-PNG-Export lieferte abgeschnittene Unterseiten. In der Gesamtansicht erkannt und benannt. Genau52 selbst erzeugte PNG-Dateien nach Prüfsummen-/Pfadprüfung reversibel nach runtime/blackjack-full-deck-20261031/discarded-canvas-export/ verschoben. Temporäre Exportwerkzeuge nach obsolete-export-tools/ gesichert. Aktive Spielauswahl ausschließlich vollständige SVGs; doppelte Einbettung derselben Bildhälfte durch SVG-Wiederverwendung ersetzt, Originalbildinhalt unverändert. Kein defekter PNG-Kartensatz aktiv.
- Sichtbarer Kartenrenderer verwendet die zentrale Quelle static/blackjack-card-art.js: fronts-ivory-v1/__CARD__.svg?v=3, Kennungivory-v1-large-index. Flugkarten übernehmen dieselbe Bildquelle, grüner Rücken unverändert. Keine Python-/Regel-/Kontenänderung und kein Neustart des normalen Spiels nötig.52 eindeutige Dateien, exakte Pip-Anzahl aller Zahlenkarten, zwei korrekte große Eckwerte, vollständige Abmessungen und Bildhälften geprüft. Alle65 vorab geschützten Bibliotheks-/Original-/Regel-/Button-/Jetondateien SHA-256-identisch;13 Eingabe-, neun Kartenpräsentations- und22 Jetonplanungsprüfungen sowie JS-Syntax erfolgreich.
- Getrennter echter Engine-Prüftisch auf8783 gestartet und neue Bildkarten mit Ausgeben/Aufdecken betrachtet. Nutzer hat diesen Tisch inzwischen selbst übernommen/weitergespielt. Nach seinem Lesbarkeitshinweis nur neu geladen, keine weitere Aktion für ihn ausgelöst: aktuelle Runde2 mit2Kreuz/2Kreuz gegen offene2Kreuz in seinem tatsächlichen Chrome-Fenster; große Werte auf Spieler- und Geberkarten sichtbar geprüft. Die neue SVG-Galerie lädt alle52 Karten vollständig ohne Beschnitt. Keine Browserwarnungen/-fehler in der Abschlussprüfung.
- Normaler Chrome-Tisch war zwischenzeitlich geschlossen. Neuen normalen Offline-Tab8765 mit bestehender Anmeldung geöffnet: Stormseed, Runde88/Einsatzphase,13.250 Test-iKühe und kein Einsatz, aktive Kennungivory-v1-large-index, unverändertes Rezept17476727364949609038305dee84e91f und Originaltisch. Keine persönliche Hand gespielt oder Gelder verändert. Aktuelle Kartenhand sichtbar im vom Nutzer verwendeten getrennten Prüftisch, aktive Auswahl zusätzlich am normalen Konto geprüft.
- Dateien: offline-preview/blackjack-v1/card-fronts/render_deck.py; static/cards/blackjack/fronts-ivory-v1/ mit52 SVGs, drei Original-PNGs und deck.json; static/blackjack-card-art.js und gemeinsame round-view-Anbindung. Übersicht /static/blackjack-kartensatz-v1.html bleibt geöffnet. Belege/Sicherungen unter runtime/blackjack-full-deck-20261031/: verification.json, live-verification.json, grosse-kartenwerte-am-tisch.png, grosse-kartenwerte-gesamt.png und vollständige Galerie. Prompts/Erzeugungsmodus stehen auch im Deckmanifest. Quellenmanifest/README aktualisiert.
- Vom Nutzer inzwischen verwendete Prüftische8782 und8783 (aktueller eigener Prüfdienst5772, serve_check.py) bleiben bestehen, ebenso normales Spiel8765. Keine Geberanimation in diesem Schritt begonnen. Nächster Gestaltungspunkt bleibt der lebendigere Geber.

## 31.10.2026 – Nutzer bestätigt den Spielstand nach eigener Runde

- Nutzer spielt am normalen Offline-Tisch selbst und bestätigt anschließend „alles gut“. Aktuelle Grafik einschließlich größerer Kartenwerte damit persönlich akzeptiert. Keine weiteren Spielzüge oder Änderungen aus der anschließenden Statusfrage abgeleitet.
- Nächster Gestaltungspunkt bleibt der lebendige Geber: zunächst dezente Bewegungsvorschau, danach spielbezogene Reaktionen und Worte; Stimme als gesonderte Option. Echte iKühe-Anbindung bleibt ein späterer separater Auftrag, aktuell weiterhin getrenntes Testguthaben. Ein gemeinsamer Praxistest zu dritt vor späterer Veröffentlichung ist eine Empfehlung, keine neu behauptete erledigte Prüfung.


## 01.11.2026 – Offline-Version1.1 gesichert, Server-Versionierung ab07Uhr geplant

- Nutzer akzeptiert den gegenwärtigen Spielstand bis zum richtigen Mehrspielertest und wünscht unterscheidbare Versionsnummern mit Prüf-/Abnahmelog und Rückweg: bisherigen Serverstand prüfen und, falls noch keine passende Nummer existiert, als1.0 sichern; Offline-Arbeit als nächste Version1.1 ablegen. Vorhandene technische Kennungen behalten, bei widersprechender Nummerierung fragen. Keine öffentliche Umschaltung aus dem Auftrag abgeleitet.
- Verifizierte lokale Sicherung1.1 erstellt: runtime/version-backups/1.1-20261101T034203Z/.1372 Code-/Grafik-/Quellendateien einschließlich unversionierter/ignorierter Projektassets in code-and-assets.zip;8419 lokale Daten-/Belegdateien getrennt in PRIVATE-PC-DATA-DO-NOT-UPLOAD.zip.145 SQLite-Dateien über die Online-Backup-API kopiert und mit quick_check geprüft. Beide Archive vollständig erneut eingelesen und Einträge SHA-256-geprüft. Alle bestehenden Git-Refs zusätzlich in repository.bundle gesichert und per git bundle verify geprüft. Installierte Abhängigkeiten/Cache ausgeschlossen, Anforderungsdateien enthalten. Rund1,1GB Archive/Git plus getrennte SQLite-Kopien; private Sicherung bleibt lokal.
- Neuer reproduzierbarer Helfer deploy/snapshot_offline.py; unveränderlicher Code-/Grafiksnapshot, Manifest, Prüfsummen, Git-Status, getrennte Version-Metadaten und Lesemich im Sicherungsordner. Zuordnung in releases/1.1.json, appendierendes Ereignislog releases/events.jsonl, Bedien-/Rückwegshinweise releases/README.md. Status1.1: lokal gesichert/offline akzeptiert, realer Mehrspielertest ausstehend, nicht veröffentlicht. App-Code und bisherige technische Health-Kennung nicht verändert. Serverstand heute noch nicht geprüft oder als1.0 behauptet. Sicherung derzeit auf demselben PC; zusätzliche serverseitige Kopie folgt erst bei Erreichbarkeit.
- Architektur lesend geprüft:500er-Einsatz/10.000 Teststart/NoPeek und Uhrstart sind nur im lokalen Starter/Simulator gesetzt; app.create_app richtet diese gemeinsame Betriebspolitik bzw. Uhr nicht ein. Serverdienst startet Gunicorn mit2 Workern. Vor Live-Übernahme nötig: gemeinsame Konfiguration, eindeutig betriebene Tischuhr unter Produktionsbedingungen, verknüpfte Laufzeit-/Versionskennung und geprüfter Rückweg mit getrennten Daten. Weitere kleine Refactors möglich: Regeln/Datenzugriff, gemeinsame Einsatz-/Sichtdaten, Controller-Aufgaben und Material-Build. Keine dieser Spiel-Refactorings in den akzeptierten Stand eingebaut. Befunde in releases/structure-review.json.
- Nutzer beantwortet Datumsfrage ausdrücklich: erste automatische Prüfung heute Sonntag01.11.2026 ab07:00Uhr Berlin. Geplante Fortsetzung im aktuellen Chat erfolgreich erstellt und lokalen Eintrag gelesen: guesstimate-versionen-1-0-und-1-1-sichern, ACTIVE, stündlich07–23Uhr bis Abschluss. Auftrag prüft echte Erreichbarkeit und vorhandene Version, sichert Serverbasis vor Kennzeichnung, legt ausschließlich eingefrorene Code-/Grafikversion separat ab und protokolliert verifizierte Herkunft/Status. Keine PC-Daten/Secrets/Git-Bundle hochladen, keine aktiven Dateien ersetzen, kein Dienstneustart. Bei Konflikten melden statt Nummern überschreiben. Nach erfolgreicher Ablage Fortsetzung beenden; unverändert offline keine Routinemeldungen.
- Offizielle OpenAI-Dokumentation zu geplanten Aufgaben geprüft: Für lokale Aufgaben muss der Rechner eingeschaltet und die Desktop-App geöffnet bleiben. Nutzer darüber informiert. Keine SSH-Verbindung, kein Upload und keine Aktivierung in dieser Sitzung ausgeführt. Bestehende Spiele, Konten, Ergebnisse und Dienste erhalten.

## 01.11.2026 – Lokales Papierpostfach und einmalige Nachhol-Ausnahme

- Nutzer legt eigene Mail-Seite mit handschriftlichen Papierzetteln fest. Spieler dürfen ausschließlich dem Betreiber schreiben; dieser darf einzelne Spieler oder alle anderen vorhandenen Konten anschreiben. Nur Gelesen/Ungelesen, keine Ticketstufen oder sonstigen Zusatzfunktionen. Leistenumschlag wackelt bei neuer Post bis zum ersten Klick; Lesen einzelner Zettel ist getrennt. Spätere neue Post aktiviert die Bewegung erneut, die Bestätigung bleibt pro Konto erhalten.
- Lokale Umsetzung in inbox.py, templates/mail.html, static/mail.css/js und gemeinsamer Leiste. Bestehende Betreiberkennung verwendet, alle Empfänger-/Zugriffsrechte serverseitig geprüft, Schreibaktionen mit CSRF, Klartext/HTML-Escaping, private Antworten ohne Cache. Drei zusätzliche Postfachtabellen; lokal eingebundene Caveat-Handschrift samt Originalquelle/SIL-Lizenz. Rundnachrichten werden an zum Sendezeitpunkt vorhandene andere Konten zugestellt und haben einzelne Lesestände. Schmalere gemeinsame Leiste ohne Überlagerung von Datum/Spielsammlung angeordnet; vollständige Komponenten beibehalten.
- Erste getrennte Prüfungen erkannten eine nicht eigenständig auswertbare Jinja-Verzweigung in der Nachrichtenliste für die bestehende Button-Werkstatt. In der zuständigen Mail-Komponente auf einen gemeinsamen vollständigen Formular-/Buttonaufbau konsolidiert; keine Bibliotheks-/Rezept-/Parserdatei verändert. Normaler Offline-Starter mit Werkstattintegration startet anschließend erfolgreich.31 ursprüngliche Datenbanktabellen nach Aktivierung inhaltlich identisch zur SQLite-Online-Sicherung, quick_check ok;0 persönliche Nachrichten verschickt.
- Frühere Nutzeranforderung zur Wiedereröffnung ebenfalls lokal umgesetzt: Woche ab26.10.2026 ist vom Nachholen ausgenommen. Am heutigen Sonntag01.11. ist nur die heutige Daily-Runde spielbar; ab Montag02.11. gelten wieder die normalen Nachholtage der neuen Woche. Zentrale Datumsprüfung verwirft auch alte aktive Nachholrunden bei direkten Spielaufrufen. Keine Ergebnisse oder Nutzungseinträge gelöscht. Die bisherige dauerhafte Nachholregel bleibt außerhalb dieser ausdrücklich gewünschten Einmal-Ausnahme erhalten.
- Prüfungen:11 Postfachtests und3 Ausnahmefälle vollständig bestanden;65 bestehende Kernprüfungen vor Ergänzung der Ausnahme bestanden und die4 betroffenen bisherigen Nachholfälle danach erneut erfolgreich geprüft. Kalenderabhängiger Normalbetriebstest erhält dafür ausdrücklich keine Ausnahme; Ausnahmewoche gesondert geprüft. JavaScript-Syntax und git diff --check bestanden. Normales Offline-Spiel8765 mit vorhandenem Stormseed-Login sichtbar geprüft: heutige Startseite ohne Nachholzugang, neuer Mail-Knopf, eigene Betreiberseite mit Papierformular. Keine Hand/Quizrunde gespielt. Vorhandene Anmeldung/Sitzungsschlüssel erhalten.
- Getrennte Browserprüfung auf8779 mit erfundenen Konten: Spieler an Betreiber, Betreiber an alle, eigene Lesestände, Wackeln bis Klick und erneutes Wackeln bei neuer Nachricht sichtbar; abschließende Vorschau ohne Browserwarnungen/-fehler. Während Dienstneustarts im normalen Tab zeitweise bestehende Button-Runtime-Verbindungswarnungen beobachtet; daraus keine fehlerfreie Gesamt-Browserhistorie behauptet. Screenshot Papierzettel und Gelesen/Ungelesen: runtime/mail-20261101/papierzettel-vorschau.jpg. Weitere Sicherungen/Prüfberichte dort, Bedienung in docs/POSTFACH.md. Eigener Vorschauprüfdienst/-tab wird nach Belegsicherung geschlossen, normaler Offline-Dienst und Nutzerpostfach bleiben offen.
- Alles lokal: keine Serververbindung, öffentliche Veröffentlichung oder echte Rundmail. Unveränderliche1.1-Sicherung und deren Versionszuordnung bleiben erhalten; Postfach/Ausnahme sind spätere lokale Ergänzungen. Exakter Abgleich der endgültigen1.1-Patchnotes mit dem tatsächlichen Serverstand, Veröffentlichung und eine neue Releasezuordnung bleiben offen.

- Abschluss bestätigt: Offline-Health ok, bestehende Buttonzuordnung HTTP200; eigener Prüfdienst8779 und Prüftab beendet. Normaler Nutzertab war zuletzt auf dem Shop und wurde dort belassen. Bildnachweis der zuvor geprüften eigenen Postfachseite sowie der getrennten Papierzettelvorschau ist gesichert.

## 01.11.2026 – Regeln im Shop/Profil ausgeblendet, Games-Collection-Auswahl

- Nutzer fordert den Regelknopf wie bei Mail auch für Shop und Profil auszublenden. Gemeinsame Bereichsentscheidung rules_hidden in templates/base.html eingeführt: dort weder Regelknopf noch unpassender Daily-Regeldialog; gilt auch für Spielerübersicht und öffentliche Profile. Spielseiten behalten ihre bestehenden Spielregeln. Sichtbar im normalen Offline-Spiel an Shop, eigenem und öffentlichem Profil geprüft.
- Anschließend gewünschte Häkchenauswahl oberhalb der Games-Collection-Kacheln eingebaut: casino und singleplayer, höchstens ein Haken. Nutzer bestätigt ausdrücklich Singleplayer nur mit Black Jack und Kniffel; freie Karten-/Würfeltische ausgeschlossen. Casino zeigt derzeit Black Jack. Ohne Haken erscheinen weiterhin die drei bisherigen Spielgruppen. Auswahl wird in der Seitenadresse ansicht geführt und beim Neuladen bzw. Zurückkehren wiederhergestellt.
- Bestehende Black-Jack-Kachel direkt aus blackjack_flyer wiederverwendet. Kniffel-Kachel unverändert aus dem bisherigen Unterbereich in kniffel_flyer übernommen, beide Orte verwenden diese eine Quelle. Keine zweite Innenkomposition; vorhandene Gestaltung und Spielziele erhalten. Neue Auswahlzuständigkeit static/game-collection.js, CSS an bestehender Games-Collection-Komponente und deren Responsive-Regel konsolidiert. Keine Spielregeln, Einsätze, Guthaben oder Datenbanken geändert. Black Jack verwendet weiterhin sein ausdrücklich getrenntes Testguthaben; Casino-Ansicht nennt dies sichtbar. Keine echte iKühe-Anbindung aus dem Filterauftrag abgeleitet.
- Prüfungen: bestehende Regelbereichs-/Navigationstests (2), Collection-/Gruppenfälle (4, darunter bestehender Pot-Fall) und Werkstatt-Button-Integration (1) erfolgreich. Alten Collection-Test auf drei Standardkacheln plus zwei anfangs verborgene direkte Spielkacheln präzisiert. JavaScript-Syntax und git diff --check bestanden. Im tatsächlichen Offline-Browser beide Ansichten, gegenseitiges Abwählen, Abwählen zurück zu den drei Gruppen und Neuladen mit erhaltenem Singleplayer-Haken geprüft; keine game-collection-Warnungen/-Fehler. Keine Partie gestartet oder persönliche Ausstattung geändert.
- Belege: runtime/collection-filter-20261101/casino.jpg und singleplayer.jpg. Normales Offline-Spiel läuft ohne Dienstneustart weiter; Collection mit Singleplayer-Auswahl geöffnet. Keine Serververbindung oder öffentliche Veröffentlichung; unveränderliche1.1-Sicherung erhalten.

## 01.11.2026 – Rundmail mit Patchnotes1.1 als ungesendeter Entwurf vorbereitet

- Nutzer wünscht Patchnotes für Version1.1 und Vorbereitung als Mail an alle Spieler. Rückfrage zur Abgrenzung des bereits eingefrorenen Stands ausdrücklich beantwortet: alle bisherigen Änderungen einschließlich Postfach, Regelknopfpflege und Games-Collection-Filtern gehören in den geplanten Umfang dieser Rundmail. Ursprüngliche1.1-Sicherung/Manifest nicht geändert oder als neu geprüft ausgegeben; genaue öffentliche Gegenprüfung und Veröffentlichung weiterhin offen.
- Spielertext umfasst Black Jack mit getrennten Test-iKühen, Conquest-Ausbau, Mitspielerprofile/gemeinsame Lobbys, Casino-/Singleplayer-Auswahl, Papierpostfach, ausgeblendete Regeln und Startseite bei Fragenmangel. Einmalige Nachhol-Ausnahme ausdrücklich mit01./02.11.2026 und26.–31.10. benannt; bei späterem Versand auf tatsächliches Datum prüfen. Keine unbestätigte Fragenaktivierung, echte iKühe-Anbindung oder bereits erfolgte Veröffentlichung behauptet.
- Reproduzierbarer Entwurf unter releases/drafts/1.1-rundmail.txt und .json gespeichert: Empfängerall, Betreff „Version1.1 – Black Jack, neue Post und mehr Überblick“, vollständiger Mailtext, Statusprepared_unsent, sent_atnull, bestätigt erweiterter Umfang und Bezug zum alten Sicherungsmanifest. Betreff-/Textlängen geprüft;2135 Zeichen im Nachrichtentext. Vorbereitung als eigenes Ereignis in releases/events.jsonl angehängt; keine vorhandene Versionshistorie ersetzt.
- Im normalen Offline-Postfach8765 mit bestehender Betreiberanmeldung eigener Tab3 geöffnet und EmpfängerAlleSpieler, Betreff und Text eingetragen; Feldwerte exakt gegen den gespeicherten Entwurf verglichen. Versandknopf nicht betätigt. inbox_messages und inbox_deliveries vor/nach jeweils0. Entwurfstab zur Prüfung offen gehalten; zusätzlicher Text ist unabhängig vom Browser gesichert. Beleg/Formprüfung unter runtime/patchnotes-1.1-20261101/ einschließlich rundmail-vorbereitet.jpg. Kein Programmumbau, Serverzugriff oder Mailversand.

## 01.11.2026 – Erweiterter Abschlussstand1.1: Conquest-Flyer und drei Ranglisten

- Nutzer ergänzt ausdrücklich noch Version1.1 und beauftragt danach die Vorbereitung einer getrennten Offline-Version1.2. Bestätigte Entscheidungen: All Time High meint höchsten Kontostand (nicht insgesamt verdiente iKühe); für1.2 lokale Spielstände getrennt kopieren. Frühere1.1-Archive bleiben unverändert, die erweiterte1.1 erhält eine neue Sicherungsrevision mit erhaltenem Vorgänger.
- Conquest/Risiko als sechsten Diashow-Flyer angeschlossen: vorhandene Kartenillustration mit einer kanonischen Conquest-Titelkomposition für Diashow und Brettspielkachel. Containerbezogene proportionale Darstellung über conquest-flyer.css; kein zweiter Innenaufbau und keine Bildbibliothek ersetzt. Voriger/nächster Flyer im echten Offline-Spiel geprüft.
- Genau drei sichtbare Ranglisten: guesstimate(Tag/Woche), iKühe(Aktuell/All Time High), Hall of Fame(Tagessiege/Wochensiege aus dem Daily Quiz). Eine gemeinsame Vorlage für Startseite/Frage/Ergebnis und eine gemeinsame Spieleranzeige; frühere zwei unabhängig aufgebaute Ranglistenvorlagen konsolidiert. Haupt-/Unterregister per Maus und Pfeiltasten bedienbar, genau eine Unterliste sichtbar. Gesamtpunkte intern/profilseitig erhalten, bisher irreführenden Gesamtpunkte-Rang bzw. Monats-Pokallabel präzisiert.
- iKühe aus bisherigen Quizabschlüssen und Käufen berechnet; Black-Jack-Testguthaben ausgeschlossen. Neue currency_peaks-Tabelle hält belegte Spitzen. Abschlussgutschrift und Erfassung innerhalb derselben Transaktion, vor Shopabbuchung Ausgangsbestand erfasst. Historische sekundengleiche Bewegungen ohne beweisbare Reihenfolge werden netto ausgewertet; keine unbewiesene Spitze erfunden. Deshalb All Time High in der Oberfläche als erfasster Höchststand bezeichnet; ältere nicht mehr belegbare Zwischenstände bleiben eine tatsächliche Rekonstruktionsgrenze. Lesen der Listen bleibt ohne Historienänderung. Abgeschlossene Tage/Wochen gewertet, geteilte Siege für alle Erstplatzierten.
- Sieben neue Ranglistenfälle einschließlich tatsächlichem Shopkauf, gleicher Sekunde, gleichhohen Rängen, Jahreswechsel und unverändernder Abfrage bestanden.65 Kernprüfungen einschließlich tatsächlicher500-Punkte-Gutschrift/Spitzenerfassung sowie7 öffentliche Profilprüfungen bestanden. Bestehende Werkstatt-Button-Integration erfolgreich. Vorhandener Kern-Testtext an neue Registerbezeichnungen angepasst. Bekannte ResourceWarning und Meldungen über unkonfigurierten externen Mailversand in Tests, keine fehlgeschlagene Prüfung im Abschlusslauf.
- Normales Offline-Spiel nach SQLite-Online-Sicherung neu geladen, Health/Browsertitel kennzeichnen nun1.1.34 bisherige Tabellen vor/nach inhaltlich identisch, zusätzliche Spitzentabelle hat einen belegten0-Stand. Kein persönlicher Quiz-/Kartenzug oder Kauf ausgelöst. Sichtbar geprüft: Conquest-Flyer, beide iKühe-Ansichten, Hall of Fame und Unterregister per Tastatur. Entdeckte Verengung der Liste durch neuen Hinweis im bestehenden Flex-Panel an dessen zuständiger Regel konsolidiert und erneut sichtbar geprüft. Belege/Tests/Sicherung in runtime/release-closeout-20261101/.
- Patchnotes-/Rundmailentwurf um Ranglisten und Flyer erweitert; weiter ungesendet. Snapshot-Helfer unterstützt auf ausdrücklichen Auftrag angehängte Revisionen mit Vorgängerhistorie; alte Registrierung wird bei fehlender Revisionsoption vor dem Archivieren abgewiesen. Neue Helfer bereiten1.2 aus dem verifizierten Code-/Grafikarchiv und den getrennten lokalen Datensicherungen vor. Eigene Startdatei, Port8784, Sitzungsschlüssel/Cookie und Arbeitsordner offline-versions/1.2; bestehende Bibliotheken nur lesend gemeinsam. Erst nach Abschluss der Sicherung wird diese Kopie erzeugt und gestartet geprüft. Öffentliche Veröffentlichung, wirklicher Mehrspielertest und Versand bleiben offen.

- Zusätzlichen Nachhol-Grenzfall abschließend abgesichert: Hall of Fame zählt unabhängig vom Datum einer älteren angezeigten Runde stets die bis heute abgeschlossenen Zeiträume. Tag/Woche beziehen sich weiterhin auf deren Rundentag. Jetzt8 Ranglistenprüfungen bestanden. Vorherige Zwischenrevision bleibt nachvollziehbar erhalten; endgültige1.1-Sicherung wird nach dieser Korrektur erneut angehängt, damit1.2 exakt von der letzten geprüften Quelle ausgeht.
