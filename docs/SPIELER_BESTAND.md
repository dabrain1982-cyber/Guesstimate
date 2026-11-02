# Spieleranzeigen und Pulte in der lokalen Werkstatt

146 Einsatzvarianten in 13 Modellen. Stand: 27.10.2026.

Bibliothek → Spieleranzeigen & Pulte bietet Suche sowie Spiel- und Bausteinfilter. Gemeinsame Komponenten stehen als Modell zusammen; Rollen, Zustände und Pultmotive bleiben einzeln auswählbar und mehreren Projekten zuordenbar. Gespeicherte Projektstände und lokale Übergaben bewahren die konkrete Variante mit Originalfragment, Beispieldarstellung und Quellprüfsummen.

| Modell | Varianten | Spiele / Einsatz | Bausteine |
|---|---:|---|---|
| Gemeinsames Profilfenster | 16 | Guesstimate, Profil | Profilfenster |
| Gemeinsame Pultauswahl | 27 | Profil, Shop | Pultmotive |
| Gemeinsamer Lobbyplatz | 19 | Conquest, Guesstimate Party, Kniffel, Mäxchen, Playtable, Würfeltisch | Lobbyplätze |
| Perfect · Spielerfenster | 13 | Perfect | Profilfenster |
| Würfelspiele · Spielerfenster | 9 | Kniffel, Mäxchen, Würfeltisch | Profilfenster |
| Würfelspiele · Aktionspult | 3 | Kniffel, Mäxchen, Würfeltisch | Spielerpulte |
| Kniffel · Spielerwertung | 1 | Kniffel | Ranglisten und Ergebnisse |
| Playtable · Namenspult | 6 | Playtable | Spielerpulte |
| Gemeinsamer Ranglisteneintrag | 21 | Guesstimate | Ranglisten und Ergebnisse |
| Party · Ergebnisplatz (Altbestand) | 2 | Guesstimate Party | Ranglisten und Ergebnisse |
| Perfect · Ergebniseintrag | 2 | Perfect | Ranglisten und Ergebnisse |
| Conquest · Armeeporträt | 25 | Conquest | Kompakte Porträts |
| Conquest · Siegerporträt | 2 | Conquest | Kompakte Porträts |

## Gemeinsame Quellen und Zuordnung

source_players.py verwendet den gemeinsamen Quellen-, Vorschau- und Speicherweg von Fenstern, Eingaben und Anzeigen. Die vollständige Profilbühne kommt aus _profile_window.html; Lobbyplätze aus _lobby_room.html. Perfect- und Würfelrahmen bleiben ihre vorhandenen Spielvarianten. Die Ranglisten lesen _leaderboard.html und _player_identity.html. Pultauswahl bewahrt die 14 registrierten Familien im Profil und die 13 angebotenen Shopmotive; dieselben 14 Familien sind im vollständigen Profilfenster auswählbar. Das sind vorhandene Ausstattungsbeispiele, keine Änderungen persönlicher Ausrüstung.

Kompakte Conquest-Porträts werden durch die tatsächliche createPlayerPortrait-Fabrik erzeugt. Die vorhandenen public_portrait/register_portraits-Funktionen liefern Bildausschnitt und Sichtbarkeitsregeln für alle 19 registrierten Avatare. Die Aufnahme führt ausschließlich diese reinen Funktionen in einem neutralen Kontext aus; keine Flask-Anwendung oder Datenbank wird gestartet. Eigener Startavatar und öffentliche Darstellung bleiben getrennt. Test- und neutrale Armeen behalten ihre buchstabenbasierte Darstellung. Armee- und Siegerporträt sind zwei Verwendungen derselben Fabrik.

Die Quellenprüfung ordnet 14 verbundene Makroaufrufe sowie 7 Spieler-/Pultquellstellen zu. Dynamische Fabrikbeispiele: 27. Es fehlen keine Zuordnungen im geprüften Bestand. Gleiche Zahlen oder ähnliche Optik allein begründen keine Zusammenfassung.

## Grenzen und spätere Aufgaben

- Ausschließlich neutrale feste Beispiele; keine Konten, echten Spielernamen, Ergebnisse oder Partien gelesen.
- Profilfenster und Porträts behalten ihre gesamte ursprüngliche Innenkomposition. Äußere Vorschauplätze ersetzen den Spielrahmen; die Werkstatt skaliert die ganze Vorschau proportional.
- Playtable behält reine Namenspulte. Kein Porträteinbau am Kartentisch und keine zusätzlichen Avatare in laufenden Quizfragen oder Countdowns.
- Die Party-Ergebnispulte sind vorhandener Altbestand; ihre Aufnahme ist keine neue Gestaltungsfreigabe.
- Kartenflächen, Würfelpulte und Werte können zusätzlich in ihren eigenen Elementfamilien erscheinen. Die Vorschau liest jeweils dieselbe Originalquelle.
- Skripte, automatische Textanpassung, Ausrüstungswechsel und Spielaktionen laufen in diesen inerten Beispielen nicht.
- Spielereditor und gemeinsame Prüfung sinnvoller Editoroptionen bleiben spätere Aufgaben.

## Aufnahme erneuern

`node deploy/capture_generated_players.mjs`

`python deploy/audit_player_coverage.py`

Beide Werkzeuge arbeiten ausschließlich lokal. Veraltete Fabrikquellen werden abgewiesen; fehlende Zuordnungen lassen die Quellenprüfung fehlschlagen.
