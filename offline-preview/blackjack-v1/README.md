# Lokale Black-Jack-Spielfeldvorschau

Die Vorschau ist ein Browserbeispiel ohne Mehrspieler-Backend. `source.json`
nennt den tatsächlich eingebauten, gespeicherten Buttonstand und die
Prüfsummen seiner gemeinsamen Darstellungsquellen.

## Freigegebene Szene und Sitzansicht

Das unveränderte freigegebene Bild liegt unter
`concepts/blackjack-tisch-45grad-v1.png`. Es ist zusätzlich in der persönlichen
Werkstatt als Hintergrund und als Flyervorlage gesichert. `scene-assets.json`
enthält die konkreten Bibliothekskennungen und den Herkunftsnachweis.

Die nähere Sitzansicht liegt als vollständiges PNG unter
`static/blackjack-tisch-sitzansicht-v1.png`; die WebP-Datei ist nur eine
komprimierte Darstellungskopie. Diese gemalte feste Szene wird mit einer
separaten bedienbaren Kartenebene kombiniert. Die vorhandenen Kenney-Karten
werden mit 45 Grad Neigung und Kontaktschatten auf dem Filz angezeigt.
Dies ist kein frei drehbarer 3D-Raum. Die vorhandenen Werkstattbuttons
stehen außerhalb dieser Kartenprojektion. Am echten Tisch wird das vollständige
Rezept bei begrenztem Platz über die Größenoption des gemeinsamen Renderers
proportional angepasst; Material, Kontur, Schriftverhältnis, Bewegung und Klang
bleiben erhalten.

`templates/_blackjack_table.html` und `static/blackjack-table.css` bilden die
einzige zuständige Szenenkomposition für Vorschau und echten Tisch. Der
Builder übernimmt sie zusammen mit den unveränderten gemeinsamen
Werkstattquellen. Der vorherige reine CSS-Tisch ist vollständig ersetzt.
Die Sitzanzeigen verwenden unverändert `static/player-portrait.js` und dessen
CSS. `players.py` liest ausschließlich Namen und Avatar des vorhandenen lokalen
Profils über eine SQLite-Verbindung im Lesemodus. Dieser aktuelle Profilstand
wird beim Bauen der Vorschau übernommen; es gibt noch keine laufende Sitzvergabe.
Stormseed ist das vorhandene Profil, Mira/Kea und Jan/Fennek sind ausdrücklich
markierte Ansichtsbeispiele. Keine Konten werden für diese Beispiele angelegt.
Spielstände enthalten keine Kopie der Profilausrüstung. Der gemeinsame
Tischbetrieb mit Kartenrunden ist im Hauptspiel unter `/karten/blackjack`
gesondert angeschlossen. Die Beispielansicht bleibt davon unabhängig.

## Echte Sitzbelegung ohne Lobby

`/karten/blackjack` öffnet unmittelbar denselben Tisch im Hauptspiel. Dieser
Einstieg ist jetzt auch mit der Black-Jack-Kachel unter Kartentische verknüpft.
Die ältere `/static/blackjack-vorschau.html` bleibt das getrennt gekennzeichnete
Browserbeispiel; dessen Beispielhände sind keine gemeinsamen Spielrunden.

`blackjack.py` verwaltet genau drei Plätze in `blackjack_seats` innerhalb der
vorhandenen Spieldatenbank. Namen und Avatare werden bei jeder Abfrage aus den
vorhandenen Profilen gelesen. Zuschauer benötigen eine Anmeldung, nehmen beim
Öffnen aber keinen Platz ein. Platznehmen/Freigeben erfordern die bestehende
Sitzung und deren CSRF-Token. Eine Person belegt höchstens einen Platz;
gleichzeitiges Platznehmen wird in einer SQLite-Schreibtransaktion entschieden.
Andere Spieler können fremde Plätze nicht freigeben.

`static/blackjack-seating.js` zeigt die gemeinsame Belegung alle 1,5 Sekunden
neu an, benutzt die kanonische Spieleranzeige und den vollständigen gewählten
Werkstattbutton. Die Druckbewegung endet vor dem Austausch der Aktionsleiste.
Neuladen oder Schließen gibt einen Platz nicht automatisch frei. Zum Aufstehen
dienen „Tisch verlassen“ und der Rückweg „Kartentische“. Ein noch liegender
Einsatz einschließlich Zusatzwetten verfällt. Während einer laufenden Runde
bleibt der Platz bis zu deren Ende reserviert und wird dann freigegeben. Am echten Tisch werden keine
Beispielkarten oder Beispielspieler angezeigt.

`build_preview.py` erzeugt `static/blackjack-workshop.js/.css` ausschließlich
aus denselben Werkstattquellen und demselben Rezept wie die Vorschau. Diese
Dateien sind Ableitungen, keine unabhängig gestalteten Komponenten. Der echte
Tisch lädt das unveränderte Tischbild direkt aus dem statischen Bestand.

`tests/test_blackjack_seating.py` prüft Anmeldung/CSRF, drei Plätze, öffentliche
Profildaten, Wiederöffnen, idempotente und konkurrierende Platzvergabe sowie
Freigabe ausschließlich des eigenen Platzes.

Die aktuelle echte Tischansicht stellt das unveränderte 1672×941-Bild stets
proportional und vollständig dar. Breite Monitorfenster erhalten seitlich eine
separat generierte Raumerweiterung (`static/blackjack-room-wide-v2.png`), mit
schmaler Kantenüberblendung. Die zentrale Originaldatei bleibt unverändert;
kein Strecken auf das Seitenverhältnis des Fensters. Geprüft bei 1911×910:
Skalierung Breite/Höhe jeweils 0,96705, keine Seitenlücken oder Scrollleisten.
Der erste Raumentwurf v1 bleibt separat als unbenutzter Entwurf gesichert.
Rückweg, Titel, Ton und Regeln liegen im Bild; die Bedienfläche ist transparent.
Die kanonische Avatar-Komponente zeigt beim eigenen Platz große Werte für
Bestand, Einsatz und Rundengewinn. Die Beträge sind ausschließlich getrennte
Test-iKühe, keine echte Kontowährung. Die Karten folgen den festen Kreispositionen im Originalbild; die Avataranzeigen
stehen an den Seiten und unten links.
Unter 900 Pixel Breite geht dieselbe Komposition in den normalen Seitenfluss;
bei sehr kleinen Fenstern bleibt Scrollen möglich, um alle Aktionen zu erreichen.

**Tisch verlassen** liegt getrennt von den Spielaktionen fest unten rechts am
Browserfenster, jeweils 16 Pixel vom Rand. Seine Position und proportionale
Größe hängen nicht von Handphase oder Zahl der Spielaktionen ab. Der übrige
Bedienbereich hält dafür Platz frei. Der Button verwendet dasselbe vollständige
Werkstattrezept und dieselbe bisherige Aktion; beim Aufstehen oder als Zuschauer
wird er ausgeblendet.

## Echte Kartenrunden

`blackjack_game.py` verwaltet Kartenstapel, Einsätze, Hände, Versicherung und
Abrechnung im gespeicherten Singleton `blackjack_game`. Die getrennte Tabelle
`blackjack_balances` hält ausschließlich getrenntes Testguthaben. Die lokalen
Starter konfigurieren einen festen Grundeinsatz von 500 Test-iKühen und 10.000
Startguthaben für neue Tischbesucher. Bestehende Guthaben und bereits liegende
Alteinsätze bleiben erhalten. Unter 500 kann der Testvorrat zwischen eigenen
Händen ausdrücklich auf 10.000 aufgefüllt werden. Keine automatische Auffüllung
und keine Abbuchung echter iKühe. Ohne lokale Konfiguration behalten ältere
Regeltests und das archivierte Browserbeispiel ihre ursprünglichen Punktwerte.
Neu Hinzukommende können über **Einsatz** jederzeit einen Betrag für die
nächste Runde legen, auch während einer fremden laufenden Hand. Wer bereits
an der laufenden Runde teilnimmt, erhält den Einsatzbutton erst nach dem
Rundenende und dem Abschluss der Bankanimation wieder. Einmal
gelegt ist er fest: Betragsfeld und Einsatzbuttons verschwinden; Ändern und
Zurückziehen werden auch serverseitig abgewiesen. Die Tischpunkte werden sofort
reserviert und beim Austeilen genau einmal übernommen. Für jede weitere Runde
ist ein neuer ausdrücklicher Einsatz nötig. Die laufende Hand bleibt unberührt.
Die serverseitige Freigabe `can_bet` berücksichtigt sowohl noch auf dem Tisch
liegende Einsätze als auch den bereits in der eigenen Hand ausgespielten Einsatz.
Dadurch erscheint beim Austeilen kein zweiter Einsatzbutton für die Folgerunde.
Beim Aufstehen verfällt der noch liegende Einsatz. Reservierte Folgerundeneinsätze
werden entfernt, ohne erneut abzubuchen oder zurückzuzahlen. Laufende Hände und
Versicherungen werden als verfallen abgerechnet. Bereits ausgezahlte Ergebnisse
bleiben erhalten. Der Rückweg „Kartentische“ ruft dieselbe geschützte POST-Aktion
auf und navigiert erst nach deren Abschluss. Ein erneuter Austritt kostet nichts
zusätzlich. Teilen (Split) erfordert einen gleichwertigen Zweikartenstart und
den gleichen Zusatzeinsatz. Bei zu wenig Guthaben bleibt der Button gesperrt
sichtbar, mit Angabe von erforderlichem und verfügbarem Testguthaben.

Der Tisch mischt sechs 52er-Decks mit `SystemRandom` und mischt zwischen Runden
bei weniger als 156 verbliebenen Karten neu. Kein Ersatzkarten-Fallback.
Die Bank hält bei Soft 17; natürliche Blackjacks zahlen 3:2. Unterstützt sind
Ziehen, Halten, Verdoppeln (auch nach Teilen), einmaliges Teilen in zwei Hände,
genau eine Zusatzkarte für geteilte Asse, spätes Aufgeben und Versicherung zur
Hälfte des Grundeinsatzes. Geteilte 21 zählt als normaler Gewinn. Die Bank prüft
ihren Blackjack vor den Spielerzügen, bei offenem Ass nach den Entscheidungen
aller Teilnehmer. Ziehfolge und Ergebnisberechnung finden nur auf dem Server
innerhalb derselben Schreibtransaktion statt. Revisionen verhindern doppelte
Aktionen und Auszahlungen. Statusabfragen verändern den Spielzustand nicht.

Die verdeckte Bankkarte und der Reststapel werden nicht an Browser übertragen.
`blackjack-card-motion.js` zeigt neu ausgegebene Karten nacheinander: je eine
Karte an die belegten Plätze in Sitzreihenfolge und danach an die Bank, dann die
zweite Runde. Kartenflug 270 ms, kurze Pause 85 ms, vorhandener angeglichener
Kartenklang pro Ankunft. Die verdeckte Bankkarte bleibt verdeckt; erst ein
öffentlich aufgedeckter Status erlaubt die Drehbewegung. Nachziehen ergänzt
nur neue Karten, Teilen gibt vorhandene Karten nicht erneut aus. Gleiche
Kartenbilder aus den sechs Decks werden einzeln gezählt.

Die Ziehfolge und die gespeicherte Abrechnung bleiben atomar auf dem Server.
Der Browser staffelt ausschließlich die Darstellung. Während der Bewegung
bleiben betroffene Summen und neue Ergebnisse zurückgehalten; Kartenaktionen
sind bis zum Ende gesperrt. Vormerkung und festes Tisch verlassen bleiben
erreichbar. Zwischenzeitliche Statusantworten werden nach der laufenden
Bewegung übernommen; Statusabfragen starten keine zweite Austeilung. Beim
ersten Öffnen einer laufenden Partie wird der gespeicherte Stand sofort gezeigt.
Seitenwechsel bricht die Bewegungen sauber ab. Die Systemeinstellung für
reduzierte Bewegung wird beachtet. `tests/test_blackjack_card_motion.mjs` prüft
neun Fälle zu Reihenfolge, verdeckter Karte, Nachziehen, Aufdecken, Teilen,
identischen Kartenbildern, Wiederholungen, Erstöffnung und Leeren des Tisches.

Alle Spieler sehen die offenen Hände; nur die aktuell berechtigte Person kann
ihre Hand spielen. Neu Sitzende können sofort für die nächste Runde vormerken,
nehmen aber nicht nachträglich an der laufenden Hand teil. Im regulären
Offline-Start läuft die gemeinsame Tischuhr: Bei mehreren Sitzenden dauert die
Einsatzphase höchstens 20 Sekunden. Haben alle gesetzt, wird sofort ausgeteilt.
Ein alleiniger Spieler startet mit seinem Einsatz sofort, ohne Einsatzcountdown.
Ein neuer ausdrücklicher Einsatz des alleinigen Spielers überspringt auch die
Ergebnispause. Ansonsten bleiben 10 Sekunden zum Ansehen der Ergebnisse; eine
bereits während der Hand gesetzte Vormerkung bleibt dabei erhalten. Die
manuellen Start-/Weiterknöpfe werden im automatischen Modus nicht angeboten.

Ohne Spieler steht die Uhr. Ohne Einsatz endet ein leeres Einsatzfenster im
Warten; ein ausdrücklich neuer Einsatz oder ein neu sitzender Teilnehmer
öffnet wieder ein Fenster. Einsätze werden niemals automatisch wiederholt.
Während Spielerzug und Versicherung läuft in diesem Schritt noch keine
Abkürzung bei Inaktivität; Zugzeitlimits sind der nächste Arbeitsschritt.

`blackjack_clock.py` führt die Phasenwechsel im Offline-Server aus und wird
von `deploy/run_local.py` einmal pro Prozess gestartet. Status-GETs bleiben
lesend; Browser zählen nur die gemeinsame verbleibende Zeit herunter. Die
gespeicherte Frist bleibt beim Neuladen und Dienstneustart erhalten. Nach
längerer Unterbrechung wird höchstens der nächste anstehende Wechsel
ausgeführt; es entstehen keine nachträglich gespielten Runden. Transaktionen
und Revisionen schützen auch zwei gleichzeitig ausführende Uhrinstanzen.
In Testanwendungen startet kein Hintergrundthread; kontrollierte Uhrtests
prüfen diese Wechsel ohne Wartezeiten. Andere Startwege/Serveraktivierung
werden durch diese lokale Änderung nicht eingerichtet.

Die vorhandenen Kenney-Kartengrafiken werden über eine auf 52 Karten begrenzte
Assetroute ausgeliefert. Der gewählte grüne Kartenrücken bleibt unverändert.
`blackjack-round-view.js` verwendet die gemeinsame Szenenkomposition, Karten-
und Chipklassen. `blackjack-round-clips.js` enthält exakt die acht vorhandenen
Klangdaten und deren bereits angeglichene Verstärkungen aus dem Browserbeispiel;
die Wiedergabe behält Lautstärke, Hüllkurve und Summenkompressor bei. In einem
Fenster beginnt sie erst nach einer eigenen Eingabe. Normaler Klangdiagnosetext
bleibt aus der Spielansicht ausgeblendet; Fehler werden weiterhin angezeigt.

`tests/test_blackjack_rounds.py` ergänzt die Sitzprüfung um Auszahlungen,
Soft-17-/Assregeln, natürliche und geteilte Blackjacks, Versicherung, Aufgeben,
Teilen/Verdoppeln, drei Spieler in Zugfolge, gleichzeitige doppelte Ziehversuche,
verdeckte Daten, Wiederöffnen sowie feste Einsätze/Auffüllen von Tischpunkten.
`tests/test_blackjack_clock.py` ergänzt Fristen, leere Fenster, bewusst neue
Einsätze, automatische Ergebnis-/Rundenwechsel, Neustart und konkurrierende
Uhrinstanzen. `tests/test_blackjack_prebet.py` ergänzt Sofortstart allein und
bei vollständiger Bereitschaft, Vormerkung während einer Hand, Übernahme nach
Neustart, gesperrtes Ändern/Zurückziehen und Aufstehen ohne Erstattung der laufenden Hand,
reserviertes Guthaben und konkurrierende Einsatzanfragen. Die vollständige
abgeleitete Prüfklasse umfasst 39 Fälle. Der sichtbare Countdown verändert
keine Buttoninnenkomposition.

Vier ergänzende Fälle in `tests/test_blackjack_naturals.py` prüfen natürlichen
Blackjack gegen Bank-16 ohne unnötiges Ziehen, andere weiterhin spielende Hände,
Bank-21 aus drei Karten sowie Bank-Ass mit/ohne eigenen Blackjack. Ergebnis und
Auszahlung stimmen. Offener Unterschied zum Ablauf in §7(a) der
[MGC-Regeln](https://massgaming.com/wp-content/uploads/RULES-Blackjack-4-9-26.pdf):
Ein sicherer Spieler-Blackjack bei offener Bank-2–9 wird hier noch gemeinsam am
Rundenende ausgezahlt statt sofort vor den weiteren Spielerzügen.

## Getrennter Beitrittstest mit Hugo

`python deploy/preview_blackjack_join.py --port 8780` startet ausschließlich
auf `127.0.0.1` einen gesondert gekennzeichneten Teststand. Eigene Datenbank:
`runtime/blackjack-join-simulation/quiz.sqlite3`; eigener Sitzungscookie.
Die Anwendung meldet ausschließlich ihre eigene Testidentität an. Aus dem
persönlichen Spiel werden nur der öffentliche Anzeigename und die drei
Ausrüstungskennungen gelesen; Konten, PINs, Sitzungsschlüssel und Spielstände
des persönlichen Bestands werden nicht verändert oder übernommen.

Die normale Navigation bleibt erhalten: Hauptseite → games collection →
Kartentische → Black Jack. Auf Platz 1 sitzt **Hugo · simuliert**, mit echter
Spielregelverarbeitung und ausdrücklich vorbereiteter erster Hand (16 gegen
offene Bank-6). Er wartet auf Beitritt und Einsatzvormerkung der Testidentität.
Vier Sekunden danach hält er und gibt den normalen Rundenrhythmus frei. In
weiteren Runden zieht er unter 17 bzw. hält ab 17 und reserviert eigene
500 Test-iKühe für die nächste Runde. Er spielt niemals die Besucherhand.
Der restliche Stapel wird zufällig aus den verbleibenden sechs Decks gemischt.
Der gespeicherte Testzustand bleibt bei einem Neustart erhalten.

## Buttonvorschlag und Kartenrücken

Auf Nutzerauftrag liegt ein eigener, vollständiger Werkstattentwurf unter
**vorschlag black Jack button** vor; `button-proposal.json` nennt den neuesten
Folgestand und den bisherigen persönlichen Black-Jack-Button. Der Vorschlag
wird in dieser Vorschau verwendet. Frühere persönliche Entwürfe und Zuordnungen
anderer Spiele bleiben erhalten. Der aktuelle Folgestand nutzt das gesonderte
Werkstattmaterial **Altes dunkles Nussbaumholz** (`wood-aged`), passend zum alten
Tisch. Das helle Holz bleibt als bisherige Materialwahl erhalten. Die
unveränderte erzeugte Materialquelle und ihr vollständiger Prompt liegen unter
`concepts/blackjack-button-walnut-aged-v1.png` und `button-material.json`.
Geometrie, Schriftdarstellung, Druckbewegung und
Klang stammen weiterhin vom gemeinsamen Renderer. Die eingebettete Cinzel wird
verlustfrei im WOFF-Container verpackt; Schrifttabellen werden nicht verändert.

Die drei mit Bildgenerierung entworfenen Kartenrücken **Samtgrün & Gold**,
**Nachtblau & Messing** und **Burgunder & Kupfer** liegen als unveränderte PNGs
unter `static/cards/blackjack/`. `card-back-prompts.json` dokumentiert alle
Prompts, Herkunftsdateien, Prüfsummen, Darstellungskopien und Bibliothekskennungen.
In der Werkstatt sind sie unter **Karten → Kartenrücken** als drei Varianten
eines gemeinsamen Bildbausteins gespeichert. Es sind Rückseitenmotive, keine
neuen Kartensätze oder Spielinhalte. Die Vorschau bietet dieselbe Auswahl im
Feld **Kartenrücken**; Vorderseiten und aktuelle Hand bleiben bei der Wahl erhalten.

`build_preview.py` übernimmt das vollständige Rezept unverändert. Nur der
Aktionstext und der vom Spiel bestimmte deaktivierte Zustand wechseln.
Keine Breitenstreckung oder abweichende Buttongröße am Einsatzort. Die
gemeinsamen Regeln für Fläche, Beschriftung und Seitenwand behalten ihre
ursprüngliche Rangfolge; das gemeinsame Button-, Bewegungs- und Klangprogramm
wird aus den Werkstattquellen abgeleitet. Für die eingebettete Klangdatei wird
ausschließlich der Dateitransport angepasst, nicht Wiedergabedauer oder Pegel.

Neu bauen: `python offline-preview/blackjack-v1/build_preview.py --recipe ID
--render-script PFAD_ZU_visualize/scripts/render.py` (als eine Befehlszeile).
Der gewählte Stand wird in `blackjack-tisch.html`, die Antwortkopie und
`static/blackjack-vorschau.html` übernommen. Gespeicherte Entwürfe werden dabei
nicht verändert. Eine geöffnete lokale Vorschau anschließend neu laden.

`node offline-preview/blackjack-v1/test_preview.mjs` prüft die wiederholungsfreie
Bankaktion, das Ende der Druckbewegung vor dem Aktionswechsel, doppelte Klicks
und den Wechsel von zwei geteilten Händen zur nächsten Runde.


## Chipklang und aktuelle Nachweise (30.10.2026)

`static/audio/blackjack/` enthält unveränderte CC0-Chipaufnahmen aus dem bereits
gesicherten Kenney-Casino-Paket (Quelle https://kenney.nl/assets/casino-audio).
Die Wiedergabe normalisiert RMS und begrenzt Spitzen vor dem bestehenden
Kompressor; Einsatz, Teilen, Verdoppeln und Versicherung spielen Chipablage,
die Auszahlung spielt Chipbewegung. Abfragen/Neuladen wiederholen keinen Klang.
Werkstattrezept, Druckbewegung und bisherige Originalklänge bleiben erhalten.

57 Ablauf-/Regeltests und neun Kartenpräsentationsprüfungen bestanden. Sichtbar
geprüft: 500er-Einsatz, Weg über Kartentische mit Verfall und freiem Sitz,
Wiederbetreten ohne zweiten Abzug, +500 Rundengewinn mit Chipklang, gesperrtes
Teilen bei zwei Vieren und 250 Restguthaben sowie freigegebenes Teilen mit
zwei getrennten Händen. Der bestehende Hugo-Test zeigte ebenfalls ein legales
Teilen-Angebot bei zwei Assen und ausreichendem Guthaben. Belege/Sicherungen:
`runtime/blackjack-table-polish-20261030/`. Die zwischenzeitliche fehlerhafte
Bildstreckung ist entfernt; maßgeblicher Bildnachweis ist ausschließlich
`monitor-proportionen-korrigiert.png`.

Offen: Geberanimation/Worte, Zug-/Versicherungszeitlimits samt Verbindungsabbrüchen,
frühe Auszahlung sicherer Naturals gegen Bank 2–9 bei mehreren Spielern,
Praxistest mit drei echten Spielern und spätere echte iKühe-Anbindung.


### Regelfragen und Kartenklang (30.10.2026, Ergänzung)

Die gezeigte Situation mit geteilten Assen wurde mit derselben Kartenfolge
nachgespielt: A–6=17, A–Bube=21, Bank7–7–8=22. Geteilte Asse erhalten je nur
eine Zusatzkarte, damit sind beide Hände beendet. Beide gewinnen bei Bank-Bust.
Gegen Bank20 verliert die17, die geteilte21 gewinnt1:1 (kein Natural).
Die Oberfläche erklärt abgeschlossene geteilte Asse sowie den sofortigen
Rundenabschluss bei Blackjack der Bank. Bei offenem Bank-Ass bleibt vorher
die Versicherungsentscheidung; mit Zehner/Bild und verdecktem Ass endet die
Runde ohne Spielerzüge. Eine ungeteilte eigene Soft17 bleibt dagegen spielbar.
Regelbeleg: MGC Blackjack Rules, 09.04.2026, §§1,6(i),9,11(c),12.
Runde136 war bei der Prüfung bereits überschrieben (aktueller Stand Runde140);
keine Behauptung einer exakten Rekonstruktion dieser Runde. Vorhandene Sicherungen
enthielten113/119/121/134, nicht136. Es gibt noch keine Rundengeschichte.

Der beanstandete Auftreffklang war Kenney card-place-1. Für Kartenbewegungen
wird nun card-slide-4 aus demselben gesicherten CC0-Paket benutzt, als
`static/audio/blackjack/card-deal-slide.ogg`. Unveränderte Aufnahme, 0,459s;
Wiedergabe beginnt mit der Ausspielbewegung statt erst nach dem Auftreffen.
Die bestehenden Originalclips bleiben erhalten. Browsernachweis:
`runtime/blackjack-table-polish-20261030/neuer-kartenklang.json`.


### Ausrichtung an den gemalten Einsatzkreisen (30.10.2026)

Alle drei Plätze verwenden dieselbe Anordnung am jeweiligen Kreis: Karten am
geberseitigen oberen Rand, Chipmarkierung in der Mitte. Die gemalten Kreise
liegen entlang des Tischbogens auf unterschiedlichen Höhen; die mittlere Hand
muss deshalb tiefer liegen als die äußeren. Die sichtbaren Kartenunterkanten
werden direkt an den Bildkoordinaten ausgerichtet, mit derselben gemeinsamen
45-Grad-Perspektive. Der Abstand zum oberen Kreisrand beträgt an allen Plätzen
2 Prozent der Szenenhöhe. Eine Messung vor dem ersten sichtbaren Bild gleicht
die perspektivische Projektion aus. Aktionsanzahl, Avatargröße, Handergebnis und
Statuszeile bestimmen die Kartenposition nicht mehr.

Die Avataranordnung wurde in Schritt3 überarbeitet: größere Köpfe und kompakte
Geldanzeigen stehen nahe an den jeweiligen Händen. Unbesetzte Plätze bleiben
verborgen. Die Aktionsleiste nutzt die dadurch freigegebene untere Fläche. Die Kartenbeschriftung enthält den
Spielernamen bzw. das Handergebnis. Chipwerte stammen ausschließlich aus den
bereits vorhandenen öffentlichen Einsatzwerten; keine neue Abbuchungslogik.
Tischgrafik und Werkstattrezept bleiben erhalten. Die Aktionszeile reserviert
weiterhin die volle Höhe des proportional dargestellten Werkstattbuttons.

Prüfung mit drei belegten Plätzen bei 1280×720 und 1911×910, einschließlich
Zugwechsel, Versicherung, Ergebnis und zwei geteilten Händen. Bei 720px Höhe
beträgt der Kartenabstand zum oberen Kreisrand jeweils ca.14,4px, bei910px Höhe
ca.18,2px. Bei zwei mittleren Händen liegen beide Unterkanten auf derselben Höhe.
Neun Kartenpräsentationsprüfungen und JS-Syntax bestanden. Bestehender Hugo-Tisch
Runde200 nur lesend geprüft, keine Browserwarnungen/-fehler. Belege/Sicherungen:
`runtime/blackjack-circle-alignment-20261030/`. Beide Offline-Dienste wurden mit
den gespeicherten Partien neu geladen, um das gemeinsame Template zu übernehmen.


### Aufräumen, Schritt1 (30.10.2026)

Unbesetzte Spieleranzeigen bleiben vollständig verborgen; Platznehmen ist
weiterhin über die vorhandenen Aktionen möglich. Die Avataranzeigen enthalten
Name, Bestand, Einsatz und beim eigenen Spieler Rundengewinn. Optionale Statuszeile
entfällt. Nur in der Simulation werden die Namenszusätze „· Test“/„· simuliert“
für Avatar und Handbeschriftung gemeinsam ausgeblendet; Konten bleiben unverändert.
Die Währung ist weiter getrenntes Testguthaben, oben ausdrücklich als Test-iKühe
gekennzeichnet. Der zusätzliche schwebende Testbanner wird nur auf der Tischseite
verborgen, damit er keinen Avatar überdeckt; auf den übrigen Testseiten bleibt er.

Runde, Belegung und aktuelle Phase stehen einmalig direkt über dem äußeren
Verlassen-Button. Der Zähler bleibt beim Ersetzen der Buttons bestehen und
aktualisiert die Zeit weiter. Eine leere Statuszeile wird durch die kanonische
Avatar-Komponente optional verborgen; andere Aufrufer mit Status behalten ihn.
Kopfgröße, Avatarpositionen und Werkstattbutton wurden für Schritt1 nicht gestaltet.

Geprüft bei1280×720 und1911×910: freier Platz verborgen, Spieler bei Belegung
sichtbar, vereinfachte Namen, keine Statuszusätze, Countdown mit Einsatzphase,
Zähler8px oberhalb Verlassen. Bestehender Hugo-Tisch Runde251 nur lesend geprüft,
keine Browserwarnungen/-fehler. Neun Kartenpräsentationsprüfungen und JS-Syntax
bestanden. Belege: `runtime/blackjack-cleanup-step1-20261030/`.

Nächster Schritt2: Auf Nutzerklärung kleinere Buttonversion in der Werkstatt
speichern; Beschriftung soll die Fläche sinnvoll nutzen. Nutzerbeobachtung:
aktuell passt die Beschriftung ungefähr2,5-mal auf die Fläche. Diese Anpassung
ist noch nicht umgesetzt. Weitere Avatar-Neugestaltung folgt erst in Schritt3.


### Kompakter Werkstattbutton, Schritt 2 (30.10.2026)

Gespeichert als **vorschlag black Jack button – kompakt**, Kennung
`17476727364949609038305dee84e91f`; bisheriger Entwurf
`656dbd73ec9c45a1b86791b2e3a0fcb0` bleibt unverändert.
Native Größe 204 × 71,375 px statt 240 × 73,172 px, 15 Prozent schmaler.
Cinzel 20,4 px statt 20 px; lange Texte werden zweizeilig dargestellt.
Gespeicherte Einstellungen: Größe 17, Formhöhe 104 Prozent, Schriftgröße
120 Prozent. Farbe, gealtertes Nussbaumholz, Kontur, Druckbewegung (180 ms)
und Klang (Spielstein setzen, 25 Prozent) vom Elternentwurf erhalten.
Der bestehende Builder übernimmt diesen Entwurf unverändert in den
Spielrenderer und in die archivierte Vorschau. Keine Größen-/Schriftkorrektur
am Einsatzort und keine neue Grundkomponente.

Werkstattweg Bibliothek → kompakten Entwurf ansehen → im Button-Editor öffnen
sowie erneutes Öffnen nach Neuladen sichtbar geprüft. Testbutton meldet
Druckbewegung und gewählten Spielsteinklang. Laufender Hugo-Tisch Runde 252
nur lesend bei 1280 × 720 und 1911 × 910 geprüft: alle fünf Aktionen
(einschließlich Teilen) und Verlassen verwenden dieselbe gespeicherte Kennung.
Bei großem Fenster alle 20,4 px, bei engem Fenster proportional skaliert.
Versicherung/Ohne Versicherung in separater reiner Darstellungsprüfung ebenfalls
20,4 px bei großer Ansicht bzw. 16,319 px bei kompakter Ansicht, vollständig
lesbar. Tischbild, Avatarpositionen und Spielzustand nicht bearbeitet.
Belege: `runtime/blackjack-compact-button-20261030/`.

Werkstattstart blockierte zuvor wegen veralteter neutraler Anzeigen-/Spieler-
Quellenaufnahmen. Beide vorhandenen Capture-Skripte ohne Browser, DB oder
Spielaktion erneut ausgeführt; 18 Anzeigen und 27 Spielerbeispiele mit aktuellen
Quellen erzeugt. Bibliothek und gespeicherter Button danach sichtbar geöffnet.
Nächster Gestaltungsschritt: größere Avatarköpfe und kompaktere Anzeigen nahe
an ihren Händen.


### Eingaben beim Buttonwechsel (30.10.2026)

Ein frischer Druck gehört genau zu dem dabei sichtbaren und freigegebenen
Button. Verspätete, auf deaktivierten Buttons begonnene oder doppelte Klicks
werden beim Funktionswechsel nicht übernommen. Während einer Anfrage bleibt die weitere Spielaktion gesperrt;
Buttonfarbe, Druckbewegung und Klang bleiben erhalten. Ein schneller Zweitklick an derselben Stelle wird bei
geändertem Kommando verworfen; bewusste spätere Spielzüge bleiben möglich.
Neun gezielte Eingabeprüfungen und neun Kartenpräsentationsprüfungen bestanden.
Prüftisch mit verzögerter Antwort: doppelter Einsatzklick sendet nur bet; erst
ein bewusster späterer Haltenklick sendet stand. Belege unter
`runtime/blackjack-round260-20261030/`. Die genaue Ursache der gemeldeten
Runde260 bleibt mangels gespeicherter Rundengeschichte unbestätigt.


### Buttonrückmeldung trotz Klickschutz (30.10.2026)

Nutzerkorrektur: keine ausgegrauten Buttons und kein Abschalten der gespeicherten
Druck-/Klangrückmeldung. Der Spielhandler prüft die Verfügbarkeit unabhängig
vom Werkstattrenderer. Buttons behalten den normalen Entwurf, auch während
Anfragen und Austeilen. Semantische Nichtverfügbarkeit per aria-disabled; kein
natives disabled. Begonnene Druckanimationen bleiben bis zur Antwort eingehängt.
Mehrfache/verspätete Eingaben führen weiterhin nicht zu zusätzlichen Spielzügen.
Prüfung mit 2s Verzögerung und Doppelklick: genau ein bet, 244 erfasste Bilder
ohne native Deaktivierung, 25 Animationsbilder, normaler Buttonklang25Prozent;
später bewusst Halten ergibt genau ein stand. 13 Eingabe- und neun Karten-
präsentationsprüfungen bestanden. Belege: runtime/blackjack-button-feedback-20261030/.


### Größere Avatarköpfe und kompakte Anzeigen, Schritt 3 (31.10.2026)

Die kanonische Porträtkomponente besitzt die gemeinsame Variante `layout=table`.
Der runde Kopf steht neben dem kleineren Namens-/Geldfeld. Bei voller Größe
ist der Kopf75px groß; das Textfeld misst204×66,813px. Alle belegten Plätze
zeigen denselben Aufbau mit Bestand, Einsatz und Rundengewinn. Die Anzeige des
aktiven Spielers erhält den vorhandenen Goldakzent. Andere Porträtvarianten
bleiben unverändert. Die gesamte Komponente wird proportional skaliert.

Die äußeren Köpfe liegen über ihren jeweiligen Karten; der mittlere steht
seitlich der Bankreihe nahe der eigenen Hand. Bei vielen Bankkarten ist die
seitliche Ausweichbewegung begrenzt, stattdessen weichen betroffene Anzeigen
nach oben aus. Karten bleiben am Kreis verankert. Die bisherigen Rand-Docks
und der feste eigene Avatar unten links sind entfernt. Auf schmalen Ansichten
stehen dieselben vollständigen Komponenten unter der Tischgrafik.

Reine Darstellungsprüfung ohne Konten/DB: drei Spieler und geteilte Hände sowie
neun Geberkarten mit positivem/negativem Rundengewinn bei1024×768,1280×720 und
1911×910; keine Überschneidung der Spieleranzeigen mit Karten, Bankzahl oder
Einsatzmarkern. Schmale390px-Ansicht ohne horizontales Überlaufen; Name und Geld
sichtbar. Keine Browserwarnungen/-fehler. 13 Eingabe- und neun Karten-
präsentationsprüfungen bestanden. Alle46 geschützten Bibliotheks-/Originaldateien
SHA-256-identisch. Originaltisch, Werkstattbutton und Kartenbewegung unverändert.

Nach erneuter Anmeldung durch den Nutzer am normalen Offline-Spiel8765
sichtbar geprüft: gespeicherter mittlerer Platz Stormseed, Runde32, Einsatzphase,
neue75px-Kopf-/204px-Geldanzeige, gleiche kompakte Buttonrezeptkennung.
Kein Spielzug für den Nutzer ausgelöst und keine Spiel-/Kontodaten per Skript
geändert. Drei Spieler und lange Bankhand ausschließlich im getrennten
Darstellungstest geprüft. Belege/Sicherungen: runtime/blackjack-avatar-step3-20261030/.
Nächster Gestaltungspunkt4: Größenverhältnis der Geberkarten prüfen.


### Versicherung bei zu wenig Guthaben (31.10.2026)

Solange die eigene Versicherungsentscheidung offen ist, bleibt Versicherung
auch bei zu wenig Guthaben sichtbar. Der normale Werkstattbutton bestätigt
den Klick weiterhin mit Druckbewegung und Klang; nach dessen Rückmeldung
erscheint die Erklärung mit benötigtem und verfügbarem Guthaben. Die erfolglose
Wahl sendet keine Spielaktion und verändert weder Guthaben noch Entscheidung.
Ohne Versicherung bleibt eine reguläre Aktion. Andere nicht ausführbare
Spielaktionen wurden damit nicht geändert.

Im getrennten UI-Prüftisch geprüft:15 Test-iKühe verfügbar,250 benötigt,
Meldung sichtbar und kein insurance-Aufruf; Ablehnen sendet genau no-insurance,
leistbare Versicherung sendet normal insurance. Keine Browserwarnungen/-fehler.
13 Eingabe- und neun Kartenpräsentationsprüfungen bestanden. Laufendes Spiel8765
mit aktuellem Modul neu geladen; dort inzwischen eigener Zug in Runde38,
keine Versicherungssituation erzwungen und keine Aktion für den Nutzer.
Belege: insurance-verification.json, insurance-action-trace.json und
versicherung-guthaben-hinweis.png unter runtime/blackjack-avatar-step3-20261030/.


### Eigener Avatar am Einsatz und Geberkarten, Schritt 4 (31.10.2026)

Neue Nutzerkorrektur ersetzt die Position des eigenen Avatars neben der Bank:
Die unveränderte gemeinsame Porträtkomponente steht links neben den eigenen
Jetons. Am linken Sitz ist links davon nicht genug Platz; auf ausdrücklichen
Nutzertest Option1 steht die vollständige Anzeige dort unter dem Einsatz.
Im rechten Sitz weicht sie bei Berührung geteilter mittlerer Karten etwas
nach unten aus. Statusmeldungen werden nur bei tatsächlicher Textberührung
seitlich begrenzt, ohne Buttons oder Karten zu verschieben.

Geberkarten waren sichtbar etwa75Prozent so breit wie die mittleren
Spielerkarten. Native CSS-Breite70→80px, gleiches Seitenverhältnis und45Grad;
bei1911×910 sichtbar72,72→83,24px gegenüber96,74px Spielerkarte, also etwa86Prozent.
Kleinere Fenster skalieren weiter proportional (neue Regel30px/5,2cqw/80px).
Bankposition50Prozent/52Prozent und Originaltischbild unverändert.

Größere Bankkarten berührten einzelne Handbeschriftungen. Nutzer erlaubt
seitliche Ausweichpositionen, bevorzugt den Filz zwischen Karten und Jetons.
Auf Desktop werden nur betroffene Beschriftungen dorthin gesetzt, ansonsten
seitlich neben ihre Karten. Die Karten selbst bleiben an den bisherigen
Kreisankern. Avatargröße/-aufbau, Werkstattbutton und Spielregeln unverändert.
Die schmale Ansicht behält ihren bisherigen Porträtfluss; die generell enge
Karten-/Beschriftungsdarstellung unter900px wurde hier nicht neu aufgebaut.

Prüfung:1280×720/1911×910 mit drei Spielern, geteilten Händen und neun
Bankkarten; linker und rechter eigener Sitz bei1024×768 ohne Berührung
mit Karten, Geldmarkern, Bankzahl, Handtext oder Aktionen. Keine Browserwarnungen
/-fehler. 13 Eingabe- und neun Kartenpräsentationsprüfungen bestanden.
Normalen Offline-Tisch8765 nur lesend mit neuem Stand geöffnet, Runde72
mit echtem Stormseed-Profil, größerer Bankkarte und Avatar links vom Einsatz
sichtbar. Kein Spielzug für den Nutzer, keine DB-/Kontenänderung durch Prüfskripte.
48 von49 geschützten Dateien identisch; ausschließlich round-view.js für die
autorisierte Handbeschriftung verändert. Originalbild und Bibliothek identisch.
Belege/Sicherungen: runtime/blackjack-avatar-and-dealer-step4-20261031/.
Nächster Gestaltungsschritt5: passende Jetons entwerfen.


### Jeton-Grafiken, Schritt5 (31.10.2026)

Drei neue transparente Rasteroriginale in Waldgrün, Burgunder und Anthrazit,
mit den Jetons auf der unveränderten Geberablage als Material-/Lichtreferenz.
Matte, leicht abgenutzte Oberflächen, elfenbeinfarbene Einlagen und schräge
Sitzperspektive. Originaldateien einschließlich Alpha unverändert gesichert
unter static/jetons/blackjack/. Die zunächst angelegten Bibliothekseinträge
wurden auf Nutzerkorrektur wieder herausgenommen und außerhalb der Werkstatt
gesichert. Übernahme in die Werkstatt erst nach ausdrücklicher Nutzerfreigabe.
Kennungen, Prüfsummen und Erzeugungsquellen stehen in jeton-assets.json.

Aktiv ist der grüne Jeton als gemeinsame Einsatzkomponente für alle Plätze.
Die alte22×15px-CSS-Scheibe samt Rahmen ist ersetzt. Der gesamte Bildbereich
misst bei1911×910 etwa67,91×49,69px und passt proportional zur Tischperspektive.
Der tatsächliche Gesamteinsatz wird in der hellen Mitte dargestellt; kein
neuer Nennwert/keine Zuordnung von Farben zu Geldbeträgen. Längere Gesamtbeträge
werden innerhalb derselben Komponente passend gesetzt. Der linke eigene
Avatar folgt bei gesetztem Einsatz dessen tatsächlicher Unterkante.

Drei Plätze, Split-Gesamteinsatz1.000 und normaler500er-Einsatz bei1911×910
und1280×720, linker Sitz bei1024×768 sichtbar geprüft: keine Überlagerung
mit Karten, Avataren oder Aktionen. Ohne Einsatz sind keine Jetons sichtbar.
Normaler laufender Tisch8765, Runde80 mit echtem Stormseed-Profil,500 Einsatz
und neuer grüner Grafik63,80×46,69px sichtbar geprüft, keine Browserwarnungen
/-fehler, kein Spielzug für den Nutzer. 13 Eingabe- und neun Kartenpräsentations-
prüfungen bestanden. Alle49 geschützten bestehenden Dateien identisch. Die drei Entwürfe und
ihre vorläufigen Importdateien sind bis zur Freigabe außerhalb der Werkstatt
gesichert.

Belege: runtime/blackjack-jetons-step5-20261031/. Tischbild, Karten,
Avatar-Innenkomposition, Buttons, Klang und Spielregeln unverändert.
Schritt6 (Gewinn ergänzen, zum Guthaben übernehmen und Verluste abräumen)
wurde noch nicht begonnen; bisheriges Erscheinen/Verschwinden bleibt bestehen.


### Unbeschriftete Stapel und Regelrecherche (31.10.2026)

Nutzerwahl: grün500, vorläufig schwarz250 oben auf dem Stapel. Rot und Schwarz
auf ausdrückliche Freigabe wieder in die Bildbibliothek aufgenommen; Grün
bleibt als Werkstattimport ausstehend, im Spiel ausdrücklich gewählt. Keine
Zahlen auf Jetons. Gesamteinsatz bleibt am Avatar und als zugänglicher Titel
der Einsatzanzeige erhalten. Eine gesetzte Versicherung zählt zum auf dem
Tisch dargestellten Betrag. Polls bauen identische Stapel nicht erneut auf.

Reine Darstellungsprüfung:250=schwarz;500=grün;750=grün+schwarz;1000=zwei grüne;
1250=zwei grüne+schwarz;1500=drei grüne;2000=vier grüne. Keine sichtbaren
Zahlen, Restbetrag0, schwarzer Chip jeweils zuletzt/oben. Bei1280×720 geprüft,
linker Sitz1024×768 ohne Avatar-/Karten-/Buttonüberlagerung. Browser ohne
Warnungen/Fehler. Anschließend am normalen Offline-Tisch8765 mit echtem
Stormseed-Profil in Runde84 sichtbar geprüft: grüner500er ohne Beschriftung.
Kein Spielzug für den Nutzer ausgelöst.

Regelrecherche bestätigt beide Abläufe: Peek mit frühem Bank-Blackjack-Ende
(bei Ass erst nach Versicherungswahl) und Hole Card ohne frühe Prüfung. Nutzer
wählt späte Aufdeckung und bestätigt die veröffentlichte Regel ohne eigene
Sonderregelung. Am31.10.2026 für neue Offline-Runden aktiviert: Bei Bank-
Blackjack geht der ursprüngliche Einsatz genau einmal verloren; zusätzliche
Beträge aus Teilen/Verdoppeln kommen zurück. Aufgeben gibt die Hälfte nur
ohne Bank-Blackjack zurück. Versicherung wird getrennt abgerechnet.
Die beim Geben festgehaltene Rundenregel erhält bereits laufende Peek-Hände.
219 Blackjack-Pythonprüfungen,13 Eingabe- und neun Kartenpräsentationsprüfungen
bestanden. Sichtbar am getrennten In-Memory-Prüftisch mit echter Engine:
Zehn offen und Verdoppeln, Ass offen und nach Versicherungswahl weiter
spielen, beide geteilten Hände verdoppeln. Letzter Fall:2.000 gelegt,500
Verlust,1.500 zurück. Keine Datenbank/Konten im Prüftisch.
Normalen Offline-Dienst mit SQLite-Sicherung neu geladen und echten
Stormseed-Tisch über das normale Menü geöffnet: Runde84 mit unveränderter
Hand/Guthaben/Sitz und Hinweis auf die neue Regel ab nächster Runde.
31 Datenbanktabellen vor/nach Neustart verglichen: nur blackjack_game
verändert, dort nur table_rules.55 geschützte Dateien unverändert.
Belege: runtime/blackjack-no-peek-activation-20261031/. Kein Serverupload.

Primärquelle: https://massgaming.com/wp-content/uploads/RULES-Blackjack-4-9-26.pdf
Abschnitt6(i),8,10(b),11(d). Dein beigefügtes Regelwerk beschreibt den
allgemeinen Ablauf, legt Peek/NoPeek aber nicht ausdrücklich fest.

### Jetonbewegung abgeschlossen (31.10.2026)

Die gestalterisch freigegebene Bewegung verwendet dieselbe kanonische
Stapelkomponente wie ruhende Einsätze: maximal48px,260ms hinein,290ms hinaus.
Neue bestätigte Beträge fliegen aus Richtung Avatar zum Einsatzfeld.
Nach Abschluss der Kartenbewegung gehen verlorene Anteile zum Geber;
Gewinnbeträge kommen hinzu, bleiben140ms sichtbar, dann geht die gesamte
Auszahlung Richtung Avatar. Auch Gleichstand, Aufgeben, Versicherung,
gemischte Split-Hände und zurückgegebene NoPeek-Zusatzeinsätze verwenden
die tatsächlich öffentlich abgerechneten Werte. Keine neue Geldbuchung.

Identische Polls, Neuladen und Rückkehr aus verstecktem Tab starten keine
alte Bewegung. Reduzierte Bewegung wird beachtet. Ein sofortiger nächster
Einsatz wartet in derselben Sitz-Warteschlange hinter der Auszahlung;
die Schaltfläche wird dafür nicht blockiert. Jetonklang beim Ankommen,
keine doppelte Auszahlungs-Klangquelle. Tischbild/Buttons/Regeln unverändert.

22 neue reine Jetonprüfungen,13 Eingabe- und neun Kartenpräsentationsprüfungen
bestanden. Getrennte echte Engine im Browser: Blackjack inklusive250er,
gemischte Split-Hände, sofortiger Folgeeinsatz während Auszahlung, äußere
Sitze, Teilrückzahlung, Neuladen/Polls und emulierte reduzierte Bewegung.
60 geschützte Dateien SHA-256-identisch. Normalen Offline-Tisch8765 mit
Stormseed-Profil in Runde88 neu geladen, Komponente und normale Buttons
sichtbar; kein persönlicher Spielzug ausgelöst. Grenzfälle getrennt auf8783
geprüft, vom Nutzer verwendeter Prüftisch8782 erhalten.
Belege: runtime/blackjack-jeton-motion-20261031/. Kein Serverupload.
Nächster Gestaltungspunkt: drei Kartenvorderseiten als Freigabemuster.


### Kartenvorderseiten: drei Freigabemuster (31.10.2026)

Pik-Ass, Karo-Sieben und Kreuz-König unter /static/blackjack-kartenmuster-v1.html.
Gemeinsamer Kartenaufbau280×380: warmes Elfenbeinpapier, dezente Papierstruktur,
feine Randabnutzung, lesbare dunkle/burgunderrote Werte und korrekte Symbole.
Doppelbild-König mit eigens erzeugter transparenter Illustration. Die Raster-
Originaldatei bleibt unverändert, Rahmen/Werte/Pips verwenden denselben
SVG-Aufbau. Vorschau zeigt große Muster und dieselben Karten klein/schräg.
Keine Spielkarten ersetzt, keine Bibliotheksübernahme vor Nutzerfreigabe.
Alle sechs Vorschaubilder im Browser geladen, sieben Haupt-Karos geprüft,
keine Browserwarnungen/-fehler. Quellen, Original, Bildprompt und Screenshot:
offline-preview/blackjack-v1/card-front-drafts/. Bildgenerierung eingebautes
image_gen; keine API-Schlüssel/CLI verwendet. Königoriginal zusätzlich
static/cards/blackjack/front-drafts-v1/king-court-v1.png gesichert.


### Vollständiges freigegebenes Blatt, größere Eckwerte (31.10.2026)

Nutzer nimmt den Stil an.52 SVG-Karten für alle vier Farben und13 Werte,
mit zusätzlich erzeugter Dame/Bube im selben Material-/Farbstil. Ein gemeinsamer
Renderer erzeugt Papier, Rahmen, Rang, Farbe, Pips und gespiegelte Bildkarten.
Eine einzige aktive URL-Auswahl in blackjack-card-art.js wird von der gemeinsamen
Tischdarstellung genutzt; Flugkarten übernehmen dieselben Bildquellen. Grüner
Kartenrücken, Tischbild, Größen/Perspektive, Jetons, Buttons und Regeln bleiben.
Kenney-Originale und ursprüngliche freigegebene Muster sind gesichert erhalten.

Nutzer meldet am Tisch zu kleine Werte. Im gemeinsamen Renderer auf96 statt42
und Gewicht700 vergrößert; Farbsymbol36 statt25. Zentralpips leicht eingerückt,
damit auch10 Platz hat. Native Kartengröße280×380 und sichtbare Spielgeometrie
unverändert. Derselbe große Index gilt für Spieler- und Geberkarten.

Ein versuchter Canvas-PNG-Export zeigte in der Gesamtansicht abgeschnittene
untere Flächen. Diese52 Dateien sind außerhalb der aktiven Assets unter
runtime/blackjack-full-deck-20261031/discarded-canvas-export/ gesichert;
verwendet werden ausschließlich vollständige SVGs. Kein fehlerhafter PNG-Pfad
bleibt als aktiver Kartensatz. Bildkarten referenzieren ihre eine Originalgrafik
innerhalb des SVGs zweimal, ohne die Bilddaten doppelt einzubetten.

Validiert:52 eindeutige Karten, alle Zahlenkarten mit richtiger Pip-Anzahl,
zwei korrekte Eckwerte je Karte, unveränderte280×380,65 geschützte Dateien
identisch. Neue Karten samt Austeilen/Bankaufdeckung im getrennten echten
Engine-Tisch geprüft. Nach Nutzerhinweis aktuelle Zweier-Hand nur neu geladen,
große Eckwerte auf Geber-/Spielerkarten sichtbar geprüft; kein weiterer Spielzug
für den Nutzer. Vollständige Galerie mit52 geladenen Bildern ohne Beschnitt.
Normalen Offline-Tisch8765 mit neuer Auswahl geladen, persönlicher Bestand
bleibt erhalten. Kein Serverupload, kein Werkstatteditor neu eröffnet.

Reproduktion: python offline-preview/blackjack-v1/card-fronts/render_deck.py.
Übersicht: /static/blackjack-kartensatz-v1.html. Belege/Sicherungen unter
runtime/blackjack-full-deck-20261031/. Die vom Nutzer inzwischen benutzten
Prüftische8782 und8783 bleiben bestehen. Nächster Gestaltungspunkt bleibt der
lebendigere Geber; hierzu noch keine Umsetzung.
