# Gemeinsame Lobbys

Die Standardlobbys von guesstimate party, playtable, würfeltisch, kniffel,
mäxchen und stormseed´s conquest verwenden `_lobby_room.html`, `lobby.css`
und `lobby.js`. stormseed´s perfect behält seinen Raum mit Einstellungszettel
und Startbuzzer.

Die Zuordnung der Spieler- und Zugangsvarianten steht in
[BAUKASTEN.md](BAUKASTEN.md), der geprüfte Dateibestand in
[BAUKASTEN_BESTAND.md](BAUKASTEN_BESTAND.md). Diese gemeinsame Lobbyvorlage gilt
für die geöffneten Standardlobbys. Sie schreibt keinen einheitlichen Aufbau der
laufenden Spieltische und keine zusätzlichen Avatare in den Quizfragen vor.
Die gemeinsame Lobbyübersicht ist als eigene Komponente umgesetzt und in
[LOBBY_OVERVIEW.md](LOBBY_OVERVIEW.md) beschrieben; die vorhandene Lobbyvorlage
ersetzt sie nicht.

## Aufbau und neue Spiele

1. Im Lobby-Endpunkt die unveränderte Mitgliederliste mit
   `lobby_player_profiles(members)` für die Anzeige ergänzen. Die Funktion liest
   die aktuelle Profil-Ausstattung gesammelt und schreibt keine Spielerdaten.
2. `_lobby_room.html` mit Kontext importieren. `lobby_room` erhält Lobby,
   ergänzte Spieler, Kapazität, Spielkennung, Spielname in Kleinschreibung,
   Zahl aktiver Spieler, Austrittsadresse und Statusattribute.
3. Über einen Jinja-`call(slot, player=None)` nur die spielbezogenen Inhalte
   bereitstellen: `settings`, optional `player_actions`, `roster_note`, `footer`
   und `closed`. Keine eigene Spieler-, Spalten- oder Startknopf-Anordnung
   nachbauen. `lobby_start_button` und `lobby_summary` verwenden.
4. Den äußeren Seitenrahmen mit `game-lobby-shell` versehen. Ein eigener
   Spielhintergrund darf die Seite gestalten; die Profilfenster bleiben
   unveränderte Instanzen der gemeinsamen Profilkomponente.

Der Aufbau ist immer Überschrift/Belegung, Mitspieler links, Einstellungen
und Start rechts, Austritt darunter. Unter 900 px stehen die Einstellungen
unter den Spielern. Gäste sehen die gewählten Einstellungen an derselben
Stelle und erhalten keinen Startknopf. Die Mindestbesetzung bestimmt weiterhin
das jeweilige Spiel. Es gibt keine zusätzliche gemeinsame Bereit-Pflicht.

## Status und Speichern

`attributes` enthält `data-status-url`, `data-member-count`,
`data-member-signature` (aktive Mitglieds-IDs, kommasepariert) und, falls das
Spiel diese verwendet, `data-revision` bzw. `data-rounds`.
`data-overview-url` bestimmt das Ziel nach einer geschlossenen Lobby.
`data-active="0"` erhält die reine Rückkehransicht eines abwesenden Spielers.
Die gemeinsamen Attribute für Namen, Zustand und Host setzt die Vorlage.

Der Status-Endpunkt liefert `status`, `members` mit `id` und optional
`host_user_id`, `revision`, `rounds` und `name`. Der Browser lädt bei einer
Änderung die Lobby neu. Eigene, noch nicht gespeicherte Eingaben unterbrechen
diese Aktualisierung, damit sie erhalten bleiben.

Bearbeitbare Einstellungen erhalten `data-lobby-settings` und
`data-settings-url`; die zugehörige Meldung trägt `data-lobby-autosave`.
Speichern läuft nacheinander mit vollständigen Formularständen. Eigene
Änderungen übernehmen die neue Statusversion, ohne die nächste Eingabe durch
Neuladen zu verlieren. Der Start wartet auf alle Speicherungen und übergibt
auch den ursprünglichen Startknopf (einschließlich Conquest-Entwicklertest).
Bei einem Speicherfehler bleibt die Lobby mit Eingaben stehen und erlaubt
einen erneuten Versuch.

Formulare behalten ihre bisherigen Spiel-Endpunkte, CSRF-Prüfung und
Hostrechte. Der gemeinsame Browsercode erzeugt keine Mitglieder, ändert
keine Bereitschafts- oder Spielregeln und startet keine Partie von selbst.

## Profile und Sonderfälle

Jedes Profil zeigt die aktuelle Ausrüstung aus dem Profil. Das untere Pultfeld
zeigt Host/Mitspieler bzw. Testarmee. Der Bereich darunter zeigt Anwesenheit
oder einen reservierten Platz; weitere Spielinformationen können über die
gemeinsame Profilfenster-API ergänzt werden, siehe `PROFILE_WINDOW.md`.

Conquest behält Reihenfolge, Armeefarben, Rückkehrplätze, Ergebnis-,
Wiederholungs- und Schließaktionen. Virtuelle Armeen benötigen kein Konto.
Perfects Zettel-, Buzzer-, Bereitschafts- und Startabläufe bleiben eigenständig.
