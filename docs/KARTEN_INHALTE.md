# Endliche Kartensätze und wachsende Fragenbestände

Stand: 27.10.2026. Korrigierte Aufnahme, nur lokal.

| Gegenstand | Werkstattlogik | Quelle |
|---|---|---|
| Französische Spielkarten | Ganzer Satz; 32/52/55/104/110 Mitglieder, in 3D oder flach | Reine Kartenfabrik aus `card_table.py` |
| Conquest-Länder | Ein Satz: 42 Länder, zwei Joker als Ergänzung | `static/conquest/world.json`, `conquest_cards.catalog` |
| Conquest-Aufträge | Ein Satz mit zwölf Mitgliedern | `world.json` → `missions` |
| Perfect-Begriffe und -Kuriositäten | Datenquellen am vorhandenen Fragenfenster | Bestehende zwei Fragenbanken, `nerd_mode.py` |
| Daily-/Party-Quiz | Datenquellen an Antwortfläche und Auflösung | Aktive Typen aus `fragen/manifest.json`, `questions.py` |

Die zuvor versuchte Registrierung jeder einzelnen Perfect-Frage wurde entfernt.
Ebenso werden endliche Conquest-Karten und französische Karten nicht mehr als
voneinander unabhängige Bibliotheksbausteine aufgelistet. Sie bleiben einzeln
visualisierbar, innerhalb ihres Satzes.

Ein Satz wird vollständig mit seinen Mitgliedern und Herkunftsprüfsummen in einer
Projektmappe gespeichert. Die Vorschauwahl eines Mitglieds ändert die gesammelte
Ausstattung nicht. Wiederverwendung legt keine zusätzlichen Entwurfsdateien an.
Eine Fragenfenster-Auswahl speichert dagegen ausschließlich die Datenquellen und
Felder, keine Kopie der Fragenbank und keine ausgewählte echte Frage.

`question_bindings.py` bindet neutrale Fensterbeispiele nach ihrer vorhandenen
Komponentenkennung. Die Felder folgen dem bestehenden Steckbrief bzw. dem
bestehenden Perfect-Format (Begriffe mit `term`, Kuriositäten mit Erläuterung).
Die Spielquellen selbst und ihre bisherigen Kennungen bleiben unverändert.
Die Vorschau zeigt weiterhin neutrale Beispiele. Diese Aufnahme ist keine neue
Fragenredaktion, Faktenprüfung oder Änderung an Spielabläufen.

Abgrenzung und Prüfung aller Bereiche:
[WERKSTATT_LOGIKPRUEFUNG.md](WERKSTATT_LOGIKPRUEFUNG.md).