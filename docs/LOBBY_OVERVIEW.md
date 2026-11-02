# Gemeinsame Lobbyübersichten

Die Baukastenvariante `zugang.liste` ist lokal umgesetzt. Sie verwendet genau
eine Vorlage für Kopf, Erstellen-Aktion, Lobbyzeile, Zustände, leere Liste,
Aktualisierungsfehler und Rückweg:

- `templates/_lobby_overview.html`
- `static/lobby-overview.css`
- `static/lobby-overview.js`
- `lobby_overview.py`

Die sieben Übersichten sind guesstimate party, playtable, würfeltisch, kniffel,
mäxchen, perfect und conquest. Die einzelnen Vorlagen übergeben Spielnamen,
Beschreibung, Kapazität, vorhandene Endpunkte und eine kurze Zusammenfassung der
jeweiligen Einstellung. Sie besitzen keinen zweiten inneren Listenaufbau.

## Aufbau

Der Spielkopf steht auf dem bisherigen Spielhintergrund. Im Listenheader folgt
rechts `lobby erstellen`. Eine Zeile zeigt in derselben Reihenfolge Lobbyname,
Host, Belegung, Zustand, Einstellung und die passende Aktion. Unter 680 px stehen
Erstellen und Zeilenaktion unter ihren Texten. Lange Namen und Texte dürfen
umbrechen. Eine leere Liste und ein vorübergehender Aktualisierungsfehler
verwenden dieselben Meldungen in allen Spielen.

Die Liste benötigt keine Hostporträts. Die zentrale Porträtvariante ist bei
Conquest umgesetzt, siehe [PLAYER_PORTRAIT.md](PLAYER_PORTRAIT.md). Ihre Anbindung
in Listen und die weiteren Spielwerte-Anbindungen bleiben spätere Arbeiten.

## Verwendung für weitere Spiele

Der Endpunkt ruft `render_overview(template, lobbies, **context)` auf. Die bisherigen
Spielabfragen und deren Anwesenheits-/Mitgliedschaftsregeln bleiben beim Spiel.
Der gemeinsame Helfer erzeugt aus den sichtbaren Zeilenangaben eine Signatur.
Er führt selbst keine Datenbankabfrage, keinen Beitritt und keine Zustandsänderung
aus. Bei `Accept: application/json` liefert dieselbe Adresse nur `signature`.

Die Zeilen enthalten `id`, `name`, `host_name`, `member_count`, `status` und
`is_member`, optional `is_reserved`, `player_limit` sowie die tatsächlich angezeigten Einstellungen.
Wenn vorhanden, ersetzt `player_limit` die allgemeine Spielkapazität für diese
Zeile; Belegung, Voll-Anzeige und Beitrittsaktion verwenden denselben Wert.
Die Signatur berücksichtigt ausschließlich die in `DISPLAY_FIELDS` aufgeführten
sichtbaren Angaben. Private Hände, Missionen, Antworten und einzelne Spielzüge
werden weder ausgeliefert noch als Anlass für ein Neuladen verwendet.

Die Seitenvorlage importiert das Makro `lobby_overview` mit Kontext. Parameter:
`lobbies`, `game`, `title`, `description`, `capacity`, `create_endpoint`,
`join_endpoint`, `lobby_endpoint`, `back_endpoint`, `back_label`; optional
`family`, `completed_endpoint`, `signature`, `status_url`. Über einen Jinja-
`call(lobby)` wird ausschließlich der Einstellungstext geliefert. Die gemeinsame
Vorlage rendert sämtliche Aktionen inklusive CSRF-Feld.

Der äußere Rahmen verwendet `lobby-overview-shell`. Ein Spiel darf seinen
Hintergrund über `data-overview-game` bzw. `data-overview-family` auswählen;
es überschreibt keine inneren Zeilen-, Schaltflächen- oder Mobilregeln.

## Aktionen und Rückwege

| Situation | Aktion |
|---|---|
| Fremde offene Lobby mit Platz | `beitreten`, POST zum vorhandenen Beitrittsendpunkt |
| Eigene wartende Lobby, auch bei voller Belegung | `zur lobby` |
| Eigener Countdown oder laufende Partie | `zurück ins spiel` |
| Reservierter conquest-Platz | `zurückkehren`, POST zum bisherigen Wiederbeitritt |
| Eigener abgeschlossener conquest-Feldzug | `ergebnis ansehen`, bestehende Abschlusslobby |
| Volle oder gestartete fremde Runde | Zustandsanzeige ohne Beitrittsaktion |

Karten kehren zu `kartentische`, Würfelspiele zu `würfeltische`, perfect und
conquest zu `brettspiele` zurück. Party kehrt zu guesstimate zurück.

perfect zeigt nun auch mit einer eigenen aktiven Mitgliedschaft seine Übersicht;
der bisherige automatische Sprung in die eigene Lobby entfällt zugunsten der
gemeinsamen Rückkehraktion. Das folgt der beschlossenen Baukasten-Zuordnung.
Der geöffnete perfect-Raum behält seinen Zettel, Buzzer und seine Bereitschafts-
und Startregeln.

## Aktualisierung

Ein gemeinsamer Browserablauf prüft die Signatur etwa alle 1,5 Sekunden. Verdeckte
Tabs reduzieren die Abfragen; die Rückkehr über den Browserverlauf setzt die
Aktualisierung fort. Nach einer Abgabe von Beitritt/Erstellen bzw. einem Linkwechsel
unterbricht die alte Ansicht ihre Aktualisierung, damit kein verspätetes Neuladen
die Navigation stört.

Bei einer Unterbrechung bleiben die zuletzt geladenen Zeilen sichtbar und eine
gemeinsame Meldung bietet `erneut prüfen`. Eine erfolgreiche Aktualisierung
entfernt die Meldung. Die Liste ändert keine Spielberechtigungen: die vorhandenen
Spielendpunkte prüfen Beitritt, Kapazität und CSRF weiterhin selbst.

Die älteren Party-/Conquest-Übersichtsstatusadressen bleiben verfügbar. Die neue
Oberfläche verwendet die gemeinsame Prüfung über ihre eigene Übersichtsadresse.
Der ältere `static/conquest-lobby.js`-Bestand ist nicht mehr eingebunden; laufende
Lobbys verwenden weiterhin `lobby.js` und Spiele ihre bisherigen Spielskripte.

Weitere Zuordnungen: [BAUKASTEN.md](BAUKASTEN.md),
[LOBBY_LAYOUT.md](LOBBY_LAYOUT.md), [BAUKASTEN_BESTAND.md](BAUKASTEN_BESTAND.md).
