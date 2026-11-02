# Gemeinsamer Baukasten für die Spielefamilie

Stand: 25.10.2026 · Arbeitsordner: `D:\Guesstimate` · ausschließlich lokal.

Dieses Dokument legt fest, welche vorhandenen Bausteine und welche benannten
Varianten wir an welchen Stellen verwenden. Das Dokument selbst ändert keine
Spielregel, Ausrüstung oder gespeicherte Partie. Noch nicht vorhandene gemeinsame
Varianten bleiben ausdrücklich als geplante Umsetzung gekennzeichnet. Funktionaler
Bestand ist keine fertige Comicgestaltung. Die offene Überarbeitung und ihre
Reihenfolge stehen in [GESTALTUNGSPLAN.md](GESTALTUNGSPLAN.md).

Der geprüfte Dateibestand mit Avatar-, Pult-, Hintergrund-, Material- und
Werkzeugzuordnungen steht in [BAUKASTEN_BESTAND.md](BAUKASTEN_BESTAND.md).
Die vorhandenen Schnittstellen sind in [PROFILE_WINDOW.md](PROFILE_WINDOW.md)
und [LOBBY_LAYOUT.md](LOBBY_LAYOUT.md) beschrieben.

## 1. Gestalterische Leitentscheidung

Die Spiele sollen als eine zusammengehörige Familie erkennbar sein. Dazu gehören
derselbe Materialbestand, dieselben verständlichen Bedienelemente und vertraute
Wege vom Auswählen über den Beitritt bis zum Spielstart. Der Platzbedarf und die
Bedienung des jeweiligen Spiels bestimmen die passende Darstellung.

Die Nutzerpräzisierung vom 25.10.2026 ersetzt die frühere pauschale Vorstellung,
in jeder Spielansicht dasselbe vollständige Profilfenster einzusetzen:

- In den laufenden Fragen von guesstimate und guesstimate party kommen keine
  zusätzlichen Avatare hinzu.
- Am Kartentisch bleibt die vorhandene Karten- und Bedienfläche vorrangig.
- Wo ein Spielerbild erscheint, stammt es aus dem vorhandenen, im Profil
  ausgerüsteten Avatarbestand. Es wird kein eigener Charakter für ein Spiel gebaut.
- Eine kompakte Darstellung ist eine zentral festgelegte Variante aus denselben
  Assets. Ein Spiel erhält keine eigene Kopie ihrer inneren Gestaltung.
- Das vollständige Profilfenster bleibt eine einzige Komponente mit unveränderter
  43:57-Szene. Seine Bestandteile werden nicht pro Spiel verschoben oder gestaucht.
- Hintergründe und Spielmaterial dürfen zum jeweiligen Spiel passen. Persönlicher
  Profilhintergrund und gemeinsamer Spielraum sind getrennte Dinge.
- perfect behält seine vorhandene Anordnung von Einstellungszettel und Buzzer.

Damit bleibt die Grundregel aus `AGENTS.md` erhalten: pro benannter sichtbarer
Variante genau eine Grundimplementierung. Die jetzt festgelegten Varianten
begründen keine Erlaubnis für unabhängige Seitenkopien.

## 2. Was bereits vorhanden ist

| Bereich | Verbindliche Quelle im aktuellen Bestand | Einordnung |
|---|---|---|
| Profilausrüstung | Kataloge in `app.py`; Zuordnung über `user_cosmetics` | Eine gemeinsame Quelle für Avatar, Pult, Hintergrund und Spruch |
| Vollständiges Profilfenster | `templates/_profile_window.html`, `static/profile-window.css`, `static/profile-stage-v1.js` | Gemeinsamer Baustein vorhanden |
| Pultwerte und Zusatzfläche | Parameter des Profilfensters für Name, Wert, Einheit, Status und Inhalte | Vorhanden; weitere Spielanbindungen offen |
| Standardlobby | `templates/_lobby_room.html`, `static/lobby.css`, `static/lobby.js`, `lobby_view.py` | Für die sechs Standardlobbys vorhanden |
| Kompakte Spielerdarstellungen | `player_portrait.py`, `static/player-portrait.js`, `static/player-portrait.css` | Gemeinsamer Porträtbaustein bei Conquest; ältere Ranglisten bleiben gesonderter Bestand |
| Spielauswahl und Kacheln | `templates/tabletop_connection.html`, `templates/tabletop_family.html`, `templates/_game_flyers.html` | Gemeinsame Kachelfamilie vorhanden; Bilder und Texte stammen noch aus mehreren Vorlagen |
| Lobbyübersichten | `templates/_lobby_overview.html`, `static/lobby-overview.css`, `static/lobby-overview.js`, `lobby_overview.py` | Gemeinsame Listenkomponente für sieben Übersichten lokal umgesetzt |
| Grundgestaltung | `static/ui-conventions.css`, `static/typography-v1.css`, `templates/_icons.html`, `templates/base.html` | Gemeinsame Grundlagen vorhanden; einzelne Spiele besitzen zusätzlich eigene Materialien und Schriften |
| Regeln und Dialoge | `static/rules.js`, Basisvorlage sowie bestehende Spielvorlagen | Gemeinsame Regelbedienung vorhanden; Texte und manche Spieldialoge bleiben spielbezogen |
| Spielmaterial und räumlicher Tisch | Karten-/Würfelskripte, lokale Würfeldateien, conquest-Tischmodule | Vorhanden, teilweise noch an das jeweilige Spiel gebunden |

Diese Einordnung beschreibt den aktuellen Code. Sie behauptet weder eine neue
visuelle Abnahme noch einen aktuellen Stand auf dem Server.

### Gemeinsame Grundgestaltung

| Element | Festlegung für die Varianten |
|---|---|
| Bedien- und Lesetext | Vorhandene lokale Inter-Schrift aus `typography-v1.css` |
| Markante Oberflächenüberschriften | Vorhandene lokale Fredoka-Schrift; Beschriftungen auf Papier, Karten oder Spielobjekten dürfen ihre vorhandene, zum Material gehörende Typografie behalten |
| Aktiver Navigationspunkt / gewöhnliche Hauptaktion | Gemeinsames Grün `#d8ff42` aus `--acid`; keine beinahe gleichen neuen Grüntöne als Seitenkopien |
| Nebenaktion / nicht verfügbare Aktion | Gemeinsame zurückhaltende bzw. deaktivierte Darstellung; Verfügbarkeit zusätzlich durch das tatsächliche Bedienelement festlegen |
| Gefahr oder Ende für alle | Klar beschriftete eigene Aktion; von einem bloßen Austritt unterscheidbar |
| Bedienelement als Spielobjekt | Vorhandenes Materialobjekt darf seine eigene Farbe behalten, insbesondere der rote perfect-Buzzer. Seine Bedeutung und Bedienbarkeit bleiben eindeutig. |
| Armeefarben, Kartenfarben und Spielsymbole | Fachliche Spielkennzeichnungen behalten ihre Bedeutung; sie werden nicht pauschal in Aktionsgrün umgefärbt |
| Schreibweise | Spielnamen und Schaltflächen kleingeschrieben. Normale Sätze, Personen-/Lobbynamen und tatsächliche Dateipfade werden dadurch nicht umbenannt. |

Die vorhandenen Aktionsbedeutungen und Farben bleiben erhalten. Die bisherigen
Buttonformen und viele Spielanzeigen sind noch kein fertiger Comicstandard.
Vor ihrer weiteren gestalterischen Verbreitung wird die gemeinsame Formensprache
nach [GESTALTUNGSPLAN.md](GESTALTUNGSPLAN.md) erprobt. Es entstehen keine
unabhängigen Schaltflächenfamilien je Spielseite.

## 3. Festgelegte Spieler- und Inhaltsvarianten

Die Kennungen dienen der Dokumentation. Sie sind noch keine neuen Programmdateien
oder Aufrufe.

| Kennung | Aufbau und zulässige Anpassung | Vorhanden / nächster Einsatz |
|---|---|---|
| `spieler.profil` | Vorhandene vollständige Szene aus ausgerüstetem Avatar, Pult, Hintergrund und Spruch. Das gesamte Fenster skaliert proportional. | Vorhanden: Startseite, Profil, Standardlobbys, perfect und Würfelspiele |
| `spieler.portraet` | Kleiner Ausschnitt aus dem vorhandenen `stage_asset`, daneben Name, Status und freigegebene Werte. Keine neue Zeichnung, kein Minipult und keine gestauchte Profilbühne. | Gemeinsame Variante bei Conquest lokal umgesetzt; Schnittstelle in `PLAYER_PORTRAIT.md`. Weitere Listenanbindungen offen. |
| `spieler.name` | Vorhandener Name und gegebenenfalls Spielwert ohne Avatarbild. Verwendet gemeinsame Schrift, Zahlen- und Statusregeln. | Am Kartentisch und in engen Wertungstabellen; kein zusätzlicher Spielerblock in den Quizfragen |
| `inhalt.pokale` | Bestehende Pokale und persönliche Kontowährung am Profilfenster. | Startseite; keine Übernahme als allgemeine Spielwertung |
| `inhalt.lobby` | Host/Mitspieler/Testarmee im Pultfeld, Anwesenheit oder reservierter Platz darunter. | In Standardlobbys vorhanden; nur tatsächlich beigetretene bzw. ausdrücklich reservierte Spieler anzeigen |
| `inhalt.spiel` | Spielbezogener Wert und Status; darunter bei Bedarf standardisierte Werte oder ein freigegebener Inhaltsblock. | Schnittstelle vorhanden; Spielzuordnungen in Abschnitt 5 |

Die Porträtvariante verwendet die zentral registrierten Ausschnitte des
Avatarbestands aus [PLAYER_PORTRAIT.md](PLAYER_PORTRAIT.md). Diese Zuordnung
gehört zum Avatarbestand, nicht in die einzelnen Spiele.
Für den neutralen Startavatar wird die vorhandene öffentliche Darstellung nach
den bestehenden Sichtbarkeitsregeln berücksichtigt. Es entstehen keine neuen
Spieleridentitäten oder erfundenen Profilbilder für virtuelle Armeen.

Die Zusatzfläche des vollständigen Profilfensters kann `auto`, `compact`,
`standard` oder `expanded` verwenden; eine feste Höhe bzw. null ist ebenfalls
bereits vorgesehen. Die Auswahl ändert die Fläche unter der Szene, nicht deren
Innenkomposition. Häufige Inhalte wie Name, Wert und Status werden aus den
gemeinsamen Feldern bezogen, statt daneben nochmals neu gebaut zu werden.

### Gemeinsame Bedeutung der Zustände

| Vorhandene Statuskennung | Bedeutung | Textbeispiele |
|---|---|---|
| `neutral` | Anwesend, ohne aktive Aufgabe | Am Tisch, Host, Mitspieler |
| `ready` | Eigene Vorbereitung/Eingabe abgeschlossen | Bereit, Antwort steht, Gewählt |
| `active` | Aktive Aufgabe oder Zug | Am Zug, Entscheidet |
| `waiting` | Wartet auf eine Aktion oder Rückkehr | Wartet, Platz reserviert |
| `out` | Für diese Runde ausgeschieden oder beendet | Ausgeschieden, Partie beendet |

Farbe allein genügt nicht: der Zustand wird zusätzlich als Text angezeigt.
Die vorhandene Zusatzkennung für eine reagierende Person bei mäxchen kann
spielbezogen erhalten bleiben. Aus dieser Tabelle folgt keine neue
Bereitschaftspflicht oder Änderung daran, wer wann handeln darf.

## 4. Gemeinsame Wege durch die Sammlung und die Lobbys

| Kennung | Festgelegte Verwendung | Umsetzung im aktuellen Bestand |
|---|---|---|
| `zugang.kachel` | Sammlung und Untergruppen; gemeinsamer Rahmen, Bild, Spiel-/Gruppenname und Status. Spielmotive bleiben erhalten. | Kachelfamilie vorhanden; vollständige zentrale Datenzuordnung noch offen |
| `zugang.karussell` | Bestehende Startseiten-Präsentation mit demselben Spielnamen, Motivbestand und Spielziel wie die zugehörige Kachel. | Vorhanden; keine Pflicht, die Startseite zu einer Kachelwand umzubauen |
| `zugang.liste` | Alle Lobbyübersichten: Spielkopf, gemeinsamer Listenheader, Erstellen-Aktion, wiederverwendbare Lobbyzeilen und Rückweg. | Gemeinsame Komponente lokal umgesetzt |
| `lobby.standard` | Geöffnete Lobbys von party, playtable, würfeltisch, kniffel, mäxchen und conquest. | Gemeinsamer Baustein aus Punkt 5 vorhanden |
| `lobby.perfect` | Bestehender perfect-Raum mit denselben Profilassets und eigenen Zettel-/Buzzer-Positionen. | Vorhandene ausdrücklich beibehaltene Ausnahme |
| `dialog.regeln` | Öffnet im jeweiligen Bereich ohne ungewollten Seitenwechsel. Inhalte bleiben zum Spiel passend. | Gemeinsame Bedienung vorhanden; kein universeller Regeltext |

Für die gemeinsame Lobbyliste gilt:

1. Der Spielkopf zeigt Namen und kurze Beschreibung auf dem jeweiligen
   Hintergrund. Darunter steht der Listenheader mit `lobby erstellen` rechts;
   bei schmaler Ansicht steht die Aktion darunter.
2. Eine Lobbyzeile verwendet dieselbe Reihenfolge für Lobbyname, Host, Belegung,
   Zustand und wichtigste Einstellung. Ein Hostporträt ist keine Pflicht; wenn
   vorhanden, verwendet es `spieler.portraet`.
3. Die Aktion heißt bei offenen Runden `beitreten`, bei einer eigenen wartenden
   Runde `zur lobby`, bei einer eigenen laufenden Runde `zurück ins spiel`.
   Reservierte Plätze erhalten `zurückkehren`, abgeschlossene eigene Partien
   `ergebnis ansehen`, sofern das Spiel diesen Zustand unterstützt.
4. Volle bzw. bereits gestartete fremde Runden zeigen ihren Zustand und erlauben
   keinen Beitritt, soweit das bestehende Spiel diesen nicht zulässt.
5. Zustände, leere Listen und Fehler erhalten dieselbe Darstellung und Bedeutung.
   Die Aktion erzeugt keine zusätzlichen Konten und keine automatische Teilnahme.
6. Der Rückweg führt in die passende Spielgruppe: Karten zu `kartentische`,
   Würfelspiele zu `würfeltische`, perfect und conquest zu `brettspiele`.
   Die Sammlung ist von dort erreichbar. party kehrt in seinen guesstimate-Bereich
   zurück. Diese Rückwege sind in den Übersichten umgesetzt.

Die geöffnete Standardlobby behält ihren bereits umgesetzten Aufbau: Kopf und
Belegung oben, Mitspieler links, Einstellungen und Start rechts, Austritt darunter.
Unter 900 px stehen die Einstellungen unter den Spielern. Hostrechte,
Startbedingungen, Profilquellen und gespeicherte Rückkehrplätze bleiben Aufgabe
des jeweiligen Spiels.

## 5. Einsatzmatrix der Spieleranzeigen

| Ort | Festgelegte Variante | Inhalte und Grenzen | Aktueller Stand |
|---|---|---|---|
| Startseite | `spieler.profil` + `inhalt.pokale` | Persönliche Ausrüstung, iKühe und Pokale | Vorhanden |
| Profil | `spieler.profil` | Ausrüstungsansicht und Bearbeitung; vollständige Szene proportional | Vorhanden |
| Shop und Pultauswahl | Bestehende Artikelvorschau | Ungekaufter Artikel ist eine Produktvorschau, keine Änderung der ausgerüsteten Identität. Derselbe registrierte Materialbestand wird gezeigt. | Ältere gemeinsame Vorschau über `_player_identity.html`; nicht blind durch ein Spielerfenster ersetzen |
| Ranglisten | `spieler.portraet` mit Name, Rang und Wert | Kompakt; kein vollständiges Profilfenster je Zeile | Bestehende `ranking`-Darstellung später an die benannte kompakte Variante anbinden |
| Sammlung / Spielgruppen | `zugang.kachel`; keine zusätzlichen Spielerbilder | Spielmotive und verständliche Auswahl | Kacheln vorhanden |
| Lobbyübersichten | `zugang.liste`, optional `spieler.portraet` für den Host | Gemeinsame Aktionen und Zustände; keine Avatarpflicht | Gemeinsam lokal umgesetzt; ohne verpflichtendes Hostporträt |
| Geöffnete Standardlobbys | `lobby.standard` + `spieler.profil` + `inhalt.lobby` | Name, Rolle und Anwesenheit; keine leeren Platzhalterpulte | Vorhanden, einschließlich party-Lobby |
| perfect-Lobby | `lobby.perfect` + `spieler.profil` | Spielpunkte und bestehende Bereitschaft; Zettel/Buzzer an ihren Stellen | Vorhanden; Status bisher noch als äußerer Spielbaustein |
| guesstimate, laufende Fragen und Auflösung | Keine zusätzliche Avataranzeige | Frage, Eingabe, Zeit und Punkte haben Vorrang | Beibehalten |
| guesstimate party, Countdown und laufende Fragen/Auflösung | Keine zusätzliche Avataranzeige | Gemeinsamer Quizablauf ohne neue Spielerbühne | Beibehalten |
| guesstimate party, Endergebnis | Eigenständiges modernes Siegertreppchen, erst entwerfen | Gemeinsame Avatarfamilie; Gewinner- und eventuell Verliererposen sind eine noch offene Idee | Ältere `podium`-Darstellung ist Altbestand, kein fertiger Ergebnisbaustein. Neue Entscheidung im `GESTALTUNGSPLAN.md`. |
| playtable, laufender Kartentisch | `spieler.name` | Namen, Kartenablagen, Bestand und Gebote behalten ihren Platz; keine vollständigen Profilfenster | Beibehalten. Porträt ist nur eine gesonderte Platzprüfung, kein festgelegter Einbau. |
| würfeltisch | `spieler.profil` + `inhalt.spiel` | Anwesenheit und eigene Bedienbarkeit; keine erfundene Punktzahl und keine globale Kontowährung als Spielwertung | Profilfenster vorhanden; aktuelle Währungsanzeige künftig passend belegen oder weglassen |
| kniffel | `spieler.profil` + `inhalt.spiel` | Zugstatus, Würfe im eigenen Zug und gegebenenfalls Gesamtpunkte; der gemeinsame Kniffelblock bleibt maßgeblich | Fenster und Block vorhanden; spielbezogene Feldanbindung offen |
| mäxchen | `spieler.profil` + `inhalt.spiel` | Leben, Schwimmen/Ausgeschieden, aktive oder reagierende Person; keine fremden verdeckten Würfelwerte | Fenster, Leben und Markierungen vorhanden; Anzeigen später über die gemeinsame Schnittstelle zusammenführen |
| perfect, laufendes Spiel | `spieler.profil` + `inhalt.spiel` | Punkte sowie Denkt nach/Antwort steht/Wählt/Gewählt/Entscheidet; geheime Antworten und Wahlen bleiben geschützt | Profilfenster vorhanden; Status noch außen statt in der gemeinsamen Statusfläche |
| conquest, laufendes Spiel | `spieler.portraet` in der Zugleiste; Spielwerte in vorhandenen Informationsflächen | Aktive Person, Armeefarbe, Phase, Länder und platzierte Truppen; verfügbare Truppen daneben. Eigene Karten/Mission bleiben privat. | Gemeinsame Porträtanbindung lokal umgesetzt; allgemeine Comicüberarbeitung von Spielanzeigen/Buttons bleibt offen. |
| conquest, Rückkehr-/Abschlusslobby | `lobby.standard` + `spieler.profil` | Reservierte Plätze, Ergebnis, Wiederholung und Rückkehraktionen | Vorhanden |

Die Aussage „Quiz ohne Avatare“ betrifft die laufenden Quizansichten. Sie entfernt
nicht nachträglich die bereits vorhandenen Bilder in party-Lobby, Rangliste,
Startseite oder party-Endergebnis.

### Platzentscheidung am Kartentisch

Für die aktuelle Spielansicht ist `spieler.name` festgelegt. Der gemeinsame
Baukasten kann dort durch Schrift, Zustände und Bedienelemente erkennbar sein,
ohne zusätzliche Profilfenster zu benötigen.

Ein späterer Porträtversuch darf nur den bestehenden Namensbereich verwenden.
Vor einer Entscheidung sind zwei, vier und sechs Personen, gedrehte Gegenplätze,
ausgelegte Karten, lange Namen sowie Bestand/Gebote zu prüfen. Karten dürfen nicht
verdeckt, Ablageflächen nicht verkleinert und fremde Handkarten nicht offengelegt
werden. Bis zu einer solchen Platzprüfung bleibt die Variante ohne Bild bestehen.

### Platzentscheidung bei conquest

Die kompakte Zugleiste ist der erste Einsatzort für das vorhandene Avatarbild.
Es werden keine vollständigen Profilbühnen um die Karte verteilt und keine
zusätzlichen 3D-Spielerfiguren benötigt. Die Karte, Kamera, Länderbedienung und
Armeefarben bleiben maßgeblich. Die vollständige Profilvariante bleibt in der Lobby.
Diese Zuordnung ist lokal umgesetzt. Verwendet wird ausschließlich die gemeinsame
Komponente aus [PLAYER_PORTRAIT.md](PLAYER_PORTRAIT.md).

## 6. Material-, Hintergrund- und Werkzeugfamilien

| Familie | Verwendung | Festgelegte Abgrenzung |
|---|---|---|
| Persönliche Profilausstattung | Alle Spielerbilder nach der gewählten Variante | Ausrüstung nach Avatar-/Pult-/Hintergrund-/Spruch-ID lesen; keine neue spielbezogene Ausstattung speichern |
| Persönlicher Hintergrund | guesstimate-Bereich und Innenraum der vollständigen Profilfenster | Kein automatischer Hintergrund für fremde Kartentische, Würfelräume oder Brettspiele |
| Sammlungshintergrund | games collection und brettspiele | Gemeinsamer vorhandener Sammlungsraum |
| Kartentischfamilie | Kartenübersicht/-lobby und laufender Filztisch | Vorhandene Raum-, Filz-, Ablage- und Kartenassets; Tischablagen sind keine persönlichen Profilpulte |
| Würfeltischfamilie | würfeltisch, kniffel und mäxchen | Vorhandener Würfelraum, dieselbe Würfeltechnik und passende Bedienkonsolen |
| perfect-Familie | Clubraum, Einstellungszettel, Buzzer | Vorhandene freigestellte Objekte und gemeinsame Profilfenster; kein Nachzeichnen pro Spielseite |
| conquest-Familie | Gemeinsame Tischszene, Brett, Karten und Zugdialoge | Vorhandene aktive Tischmodule; frühere Werkbank-/Brettstile sind kein automatisch aktiver Standard |
| Bibliotheken und Modelle | Lokale Würfeltechnik, Texturen, Modelle, Klänge und Three.js | Paketdateien zusammen mit ihren Herkunfts-/Lizenznachweisen erfassen; Paketlizenz nicht pauschal auf alle Theme-Assets übertragen |

Der aktuelle Bestand enthält lokale Würfelmodelle und einen im conquest-Code
erzeugten räumlichen Tisch. Ein zentral registrierter Bestand an 3D-Avatarfiguren
ist damit nicht belegt. Für die festgelegten Porträts werden die vorhandenen
2D-Avatarbilder verwendet. Neue Modellimporte oder Grafikerzeugung gehören nicht
zu dieser Dokumentation.

## 7. Regeln für die spätere Umsetzung und Erweiterung

1. Zuerst eine vorhandene Kennung aus diesem Baukasten wählen. Neue Spiele erhalten
   Varianten und Inhalte über diese Bausteine, keine kopierten HTML-/CSS-Innenaufbauten.
2. Wenn eine neue Variante gebraucht wird, sie zentral mit Zweck, Quelle,
   Größenverhalten und Einsatzorten ergänzen. Eine andere Breite allein erzeugt
   keine neue Variante.
3. Assets anhand des registrierten Familien-/Variantenpfads verwenden. Eine Datei
   mit höherer Versionsnummer ersetzt nicht automatisch die ausgerüstete oder
   aktuell eingebundene Grafik. Alte Dateien bleiben bis zu einer gesonderten
   Verwendungsprüfung erhalten.
4. Pro Asset Quelle, Variante, Dateipfad, Maße/Format, Einsatz und Status erfassen.
   Bei fremden Bibliotheken/Modellen die vorhandenen Lizenz-/Herkunftsbelege
   zuordnen; offene Belege ausdrücklich offen lassen.
5. Komponenten erhalten nur Werte, die der Betrachter sehen darf. Eigene Karten,
   geheime Missionen und verdeckte Würfel werden nicht aus einer gemeinsamen
   Spielerübersicht erschlossen oder an fremde Browser übertragen.
6. Spielwerte und Kontowährung trennen. Länderzahl, Gesamttruppen und aktuelle
   Verstärkungen haben unterschiedliche Bedeutungen und Beschriftungen.
7. Erst nach einem gesonderten Umsetzungsauftrag Komponenten anbinden. Vor einer
   Abnahme reale Spielerzahlen, lange Namen, verschiedene Pulte, Statuswechsel,
   schmale Ansichten und die Lesbarkeit des eigentlichen Spiels prüfen.

Die gemeinsame Lobbyliste ist lokal umgesetzt; ihre Schnittstelle steht in
[LOBBY_OVERVIEW.md](LOBBY_OVERVIEW.md). Die zentrale Porträtvariante ist bei
Conquest lokal angeschlossen. Vor weiteren gestalterischen Spielanbindungen
folgt der gemeinsame Comicentwurf für Buttons und Spielanzeigen; siehe
[GESTALTUNGSPLAN.md](GESTALTUNGSPLAN.md).
Für den Kartentisch bleibt eine Porträteinbindung eine eigene Platzentscheidung.
Die lokalen Gestaltungs- und Einstelltafeln werden in der
[Entwurfssammlung](../offline-preview/SAMMLUNG.md) wiederauffindbar aufbewahrt.
Die ergänzende lokale [Button-Werkstatt](../offline-preview/button-workshop-v1/README.md)
kombiniert Material, Form, Schriftwirkung, Bewegung und optionale Klänge an
derselben Buttonkomponente. Sie bietet A/B-Vergleich und dauerhaft gespeicherte
Entwurfsstände mit Einzelbewertungen. Die erste Comic-Tafel bleibt erhalten.
Beide sind separate lokale Werkzeuge; ein Spieleinbau oder eine allgemeine
Galerie für alle Bausteine ist damit nicht erfolgt.
Comic bleibt die aktuell gewünschte Spielgestaltung. Die Werkstatt ist darüber
hinaus für unterschiedliche Stile ausgelegt: Comic, Natürlich und Klar sind
getrennt von Material, freier Kontur, Schrift und Bewegung wählbar. Eigene
Randpunkte und Rundungen gehören zu den gespeicherten Entwurfsdaten.
Weitere Spielwerte-Anbindungen bleiben offen. Der
ursprüngliche Erfassungsschritt änderte ausschließlich Dokumentation; der
anschließende lokale Einbau der Lobbyübersichten ist im Projektlog getrennt
verzeichnet.

Die lokale [Spielewerkstatt](../offline-preview/game-workshop-v1/README.md)
verbindet acht grundlegende Bausteinarten mit einer Variantenbibliothek und
gespeicherten Projektmappen. Bretter verwenden zwei Grundvarianten (2D/3D), mit Größe, Form und Bild als Eigenschaften. Vorhandene Conquest-, Playtable- und Würfelflächen sind als Konfigurationen aufgenommen; das Feldbrett und ältere Entwürfe verwenden weiterhin `models.js`.
Figuren/Spielsteine verwenden drei Formfamilien: die vorhandenen Schachfiguren und
Damesteine aus demselben parametrischen Generator sowie die ursprüngliche
Conquest-Truppenmarke mit Sockel und projizierter Zahlenfläche. Rollen, Stil,
Farbe, Anzahl und Zustand sind Eigenschaften; keine einzelnen Bestände je Partie.
Sieben feste Konfigurationen sind zuordenbar. Editoroptionen später; siehe
[SPIELSTEINE_GRUNDLAGEN.md](SPIELSTEINE_GRUNDLAGEN.md).
Titelbilder/Bildmotive, Flyer und Icons verwenden vorhandene Quellen: neun Motive/
Logos in zwei Bildfamilien, 13 Flyer-/Kachelkonfigurationen in drei Kompositionen
und sechs Symbolbausteine (fünf ganze Symbolsätze plus App-Symbol). Symbolauswahl
wechselt nur die Vorschau; gesammelt wird der Satz. Persönliche Grußfolie bleibt
außerhalb des allgemeinen Katalogs. Siehe [BILDBAUSTEINE_BESTAND.md](BILDBAUSTEINE_BESTAND.md).
Schriften und Klänge haben eigene Bibliotheksbereiche: sieben passende freie
Schrift-/Oberflächenkombinationen (unter anderem Kreide, Stein und Metall) und
13 kurze CC0-Klänge für Bedienung, Tischaktionen und Spielereignisse. Alles lokal
ansehen/probehören und zuordnen; vorhandene Spiele/Entwürfe unverändert.
Siehe [KLAENGE_SCHRIFTEN_AUSWAHL.md](KLAENGE_SCHRIFTEN_AUSWAHL.md).
Würfel nutzen genau zwei vorhandene Varianten: Würfeltisch mit Physik und flache
Conquest-Anzeige. Anzahl, Aufdrucke und Farben sind Eigenschaften dieser Varianten.
Die alten generischen Würfel bleiben nur für vorhandene Entwürfe lesbar. Lobbyvorschauen verwenden
unverändert `_lobby_room.html` und `_profile_window.html` mit Musterdaten.
Vorhandene Buttonentwürfe lassen sich als feste Momentaufnahme aufnehmen.
Die Mappe ist eine Ausstattung für die anschließende gemeinsame Spielumsetzung;
Schachregeln, vollständige Starrkörperphysik und Online-Anbindung sind dadurch
nicht implementiert. Bestehende Spiele werden nicht automatisch umgestaltet.

Für Karten sind seit 27.10.2026 die beiden gemeinsam freigegebenen Grundlagen
in der Bibliothek aufgenommen: importierter 3D-Körper für bewegliche Karten und
grafisch verbesserte flache Anzeige-/Auswahlkarten. Zwei Grundbausteine und zwölf vollständige Kartensätze;
Vorschau und Assets direkt mit dem lokalen Kartenvergleich geteilt. Vorhandene
allgemeine Kartenentwürfe bleiben erhalten. Conquest: zwei endliche Sätze mit 42 Ländern und zwölf Aufträgen. Fragen werden über Datenquellen an Fenster gebunden, nicht als Elemente registriert.
Editoroptionen und tatsächliche Spielumstellung folgen separat. Siehe
[KARTEN_GRUNDLAGEN.md](KARTEN_GRUNDLAGEN.md).

Die Werkstatt ist nach Präzisierung vom 26.10.2026 projektunabhängig aufgebaut:
Gestalten und Bibliothek verwenden dieselbe wachsende Elementliste, beginnend
mit Buttons. Die vorhandene Button-Werkstatt und ihr Renderer werden direkt
eingebunden. Andere Generatoren zeigen einzelne Bausteine; Hintergründe und
Avatare bieten zunächst vorhandene Bilder ohne freien Editor. Projektmappe ist
die Sammlung benannter, zunächst leerer Projekte mit frei kombinierbaren
Elementen. Mehrere Varianten derselben Art und Wiederverwendung in mehreren
Projekten sind vorgesehen. Darstellung, Kamera und Objektverhalten gehören
als offene Entscheidungen in die jeweilige Mappe. Übergabe und anschließendes
Interview bilden die Grundlage für den späteren Spielebau. Der frühere
spielbezogene Werkstattaufbau gilt damit nicht mehr als Zieloberfläche.

Nach Nutzerpräzisierung vom 26.10.2026 werden Hintergründe, Titelbilder und Flyer
als fertige Bilder importiert, angesehen, ausgewählt und Projekten zugeordnet.
Sie werden nicht als editierbar angezeigt. Bereits gespeicherte Originale und
Ausschnitte bleiben erhalten. Icons und Avatarbilder verwenden weiterhin den
gemeinsamen Bildeditor für Ausschnitt und proportionale Ausgabegröße.
Fenster bieten nun eine zuordenbare Bibliothek mit 84 konkreten Verwendungen
in 30 Modellen: Regeldialoge, Entscheidungen, Inventare und Aktionsflächen
aller Spiele sowie Profil und Shop. Gemeinsame Modelle verwenden die
ursprünglichen Komponenten; Inhalte, Rollen und Zustände bleiben als einzelne
Varianten erhalten. Beispiele laden weder Konten noch Spielstände und führen
keine Spielaktionen aus. Projektmappen und Übergaben bewahren die konkrete
Variante samt Quellnachweisen. Der Fenstereditor und dessen Optionsprüfung
bleiben offen. Quellen und Grenzen stehen in [FENSTER_BESTAND.md](FENSTER_BESTAND.md).

Eingaben ergänzen dieselbe Bibliothek mit 58 Einsatzvarianten in 27 Modellen.
Text- und Zahlenfelder, Auswahl, Schalter, Regler sowie Zuordnen und Sortieren
verwenden denselben Originalquellen- und Vorschauweg wie Fenster. Beschriftung,
Grenzen und Zustände werden je Variante mitgeführt. Alle 45 nativen bzw.
rollenbasierten Quellkontrollen sind zugeordnet; versteckte Übertragungswerte
sind keine Gestaltungselemente. Eingabeeditor und Optionsprüfung bleiben späterer
Arbeit vorbehalten. Bestand: [EINGABEN_BESTAND.md](EINGABEN_BESTAND.md).

Anzeigen ergänzen 210 Einsatzvarianten in 63 Modellen aus allen acht Spielen
sowie Profil und Shop: Punkte, Timer, Fortschritt, Status, Zähler und Ergebnisse.
Gemeinsame Komponenten verwenden dieselben Quellen und denselben Vorschauweg.
Werte, Rollen und Zustände bleiben einzeln zuordenbar. Dynamische Inhalte werden
mit den vorhandenen Darstellungsfunktionen als neutrale Beispiele eingefroren;
hier läuft kein Spieltimer. Die Prüfung erfasst außerdem alle 34 semantisch
markierten Anzeigequellen und dokumentiert Ausnahmen. Anzeigeneditor und dessen
Optionsprüfung bleiben offen. Bestand: [ANZEIGEN_BESTAND.md](ANZEIGEN_BESTAND.md).

Spieleranzeigen und Pulte ergänzen 146 Varianten in 13 Modellen aus allen acht
Spielen sowie Profil und Shop. Ganze Profilfenster, Lobbyplätze, kompakte Porträts,
Ranglisteneinträge und Namenspulte verwenden die vorhandenen gemeinsamen Quellen.
Alle 14 Pultfamilien und die bestehenden Ausschnitte aller 19 Avatare sind
zugeordnet. Rollen, Zustände und Motive bleiben konkrete Projektvarianten;
Konten und Ausrüstung werden für diese Beispiele nicht gelesen. Der Kartentisch
behält seine Namenspulte und laufende Quizfragen erhalten keine zusätzlichen
Avatare. Editor und Optionsprüfung bleiben offen. Bestand:
[SPIELER_BESTAND.md](SPIELER_BESTAND.md).

Lobbys und Lobbyübersichten ergänzen 134 Quellvarianten in sieben Modellen aus
allen sieben Mehrspielerspielen. Standardraum, ganze Übersicht, einzelne Zeilen,
Listenheader und Leer-/Fehlerzustände verwenden ihre vorhandenen gemeinsamen
Quellen. Perfect behält seinen eigenen Raum mit Zettel und Buzzer. Rollen,
Bereitschaft, Belegung, Beitritt, Rückkehr und Ergebnisse sind einzelne Varianten.
Der bisherige allgemeine Lobbyentwurf bleibt zusätzlich erhalten. Das Daily Quiz
besitzt keine Mehrspielerlobby; seine Startseitenkomponenten bleiben getrennt.
Die neuen Aufnahmen sind inert; Editoroptionen bleiben spätere Arbeit. Bestand:
[LOBBYS_BESTAND.md](LOBBYS_BESTAND.md).

Die aktuellen Spielequellen sind nach Elementfamilien und konkreten Vorkommen
in [BAUKASTEN_BESTAND.md](BAUKASTEN_BESTAND.md) und WERKSTATT_BESTAND.json erfasst.
Eine Quellstelle ist noch kein gespeicherter Werkstattentwurf. Nach der
vervollständigten Buttonaufnahme haben gemäß Nutzerentscheidung vom 26.10.2026
Aufnahme und Anpassung der übrigen Elemente Vorrang. Die gemeinsame Prüfung
und Anpassung sinnvoller Button-Editoroptionen bleibt als spätere Aufgabe
offen; sie ist keine Voraussetzung für die nächsten Elementarten. Der
vollständige Weg vom gespeicherten Button zu einem tatsächlichen Einsatzort
und die gemeinsame Projektvorschau bleiben zurückgestellt. Die aktuelle
Reihenfolge steht in [BAUKASTEN_BESTAND.md](BAUKASTEN_BESTAND.md).
