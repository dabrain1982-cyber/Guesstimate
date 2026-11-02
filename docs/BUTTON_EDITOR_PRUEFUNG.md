# Erste Prüfung sinnvoller Button-Editoroptionen

## Ergänzung: praktischer Aufbau vom 28.10.2026

Nach Nutzerbestätigung jetzt **Neuen Button erstellen** und ein geführter Ablauf in fünf frei anwählbaren Schritten: Form; Oberfläche & Farbe; Beschriftung; Bewegung & Ton; Speichern. Die neue Schriftwahl überschreibt Fläche und Farben nicht mehr. Schrift- und Seitenwandfarbe bleiben auffindbar; ihre Benutzung wählt automatisch die eigene Farbe. Bei Vorlagen erklärt der Editor die bewahrte Originalfläche. Das Verändern von Glanz, Material oder Farbe schaltet auf die eigene Oberfläche um. Gespeicherte Originale und persönliche Dateien werden nicht migriert.

Im getrennten Browserbestand einen neuen grünen Button mit eigener Seitenwand und cremefarbener Kreideschrift erstellt, ausprobiert, gespeichert und nach Neuladen mit denselben Werten geöffnet. Ein weiterer Neubeginn und Rückkehr zum vorherigen Entwurf geprüft. Zusätzlich vorhandenen Shop-Button violett/glänzend bearbeitet, als eigene Variante gespeichert und nach Neuladen bestätigt. Zwölf vorhandene Editortests und fünf Medien-/Speicherprüfungen bestanden, einschließlich additiver Schriftkennungen, alter Rezepte, getrennten Farben und unveränderter Übergabeschnappschüsse. Geometrie-/Schrift-/Proportionsprüfung und Syntax bestanden. Keine vollständige Abnahme aller 85 Modelle. Allgemeine Spiele-Aktivierung bleibt offen. Belege: `runtime/button-flow-20261028/`.

Stand: 27.10.2026, ausschließlich lokal. Geprüft sind die **neun Guesstimate-
Kernmodelle** aus der vorhandenen Vergleichsansicht mit zehn Einsatzbeispielen.
Spielen und heutiges Ergebnis gehören zum bereits freigegebenen gemeinsamen
Startseitenmodell. Keine weiteren Modelle optisch zusammengeführt.

## Geprüfter Umfang

An der Startseitenaktion wurden alle 27 vorhandenen Editorfelder mit konkreten
Werten berührt: Stil/Material, Oberfläche/Struktur/Farben/Deckkraft, Grundform/
Kontur/Größe/Formhöhe, Beschriftung/Schriftzuordnung/Schriftart/Wirkung/Schriftgröße,
Tiefe/Schatten/Bewegungsdauer/-gefühl, Klang/Lautstärke und die manuellen
Schrift-/Seitenwandfarben sowie seitlicher Versatz. Abhängigkeiten wurden mit
passenden Voraussetzungen getestet, etwa Deckkraft an einer durchscheinenden
Fläche und Seitenwandfarbe mit sichtbarer Tiefe.

Zusätzlich wurden die neun Kernmodelle auf Größen-/Schrift-/Tiefenänderung,
unveränderten Ausgangszustand und sinnvolle Verfügbarkeit der Optionen geprüft.
Das umfasst Startseitenaktion, Nachholaktion, Weiter, Abschlusszustand, zwei
Nebenaktionen, Navigation, Antwortauswahl und Textaktion. Das ist keine Prüfung
sämtlicher 85 Modelle und keine persönliche gestalterische Abnahme.

## Befunde und Korrekturen

| Option | Festgestellt | Lokale Bedienkorrektur |
|---|---|---|
| Matt / Glänzend | Bei fünf Kernmodellen sichtbar, jedoch wirkungslos, solange die exakt übernommene Originalfläche erhalten blieb. Vier weitere hatten die Option bei durchscheinender Fläche bereits verborgen. | Bei bewahrter Originalfläche deaktiviert, mit Erklärung. Eigenes Material, Farbe oder Stil gibt die Option frei. |
| Spuren & Struktur | Im reduzierten Stil ohne sichtbare Wirkung. | Nur in passenden Stilen/Materialien sichtbar. |
| Lautstärke | Auch bei „Ohne Ton“ angeboten. | Erst bei gewähltem Klang sichtbar. Wert bleibt erhalten. |
| Tiefenbeschreibung | Tiefe 0 wurde als „spürbar“ bezeichnet. | Jetzt „ohne Tiefe“; 1–4 „dezent“, danach wie bisher abgestuft. |

Diese Änderungen betreffen ausschließlich die Bedienoberfläche in
`offline-preview/button-workshop-v1/workshop.js`. Renderer, Konturen, Materialien,
Klangdateien, Spielquellen, Quellenrezepte und gespeicherte persönliche Entwürfe
sind unverändert. Die Verfügbarkeit der Oberfläche liest den Zustand aus dem
verbindlichen Renderer; es gibt keine zweite Materialimplementierung.

An allen neun Kernmodellen sind vor/nach der Korrektur dieselben Ausgangswerte
und erfassten Darstellungsmerkmale bestätigt. Die Tiefenabweichung des
Nachholbuttons und weitere Zusammenführungsvorschläge bleiben bewusst bestehen.

## Nachweise

Material-/Stilwechsel, Kontur, Maße, Beschriftung und Farben bewirken die
erwarteten Änderungen. Matt/Glanz und Struktur wirken bei einer eigenen
Holzfläche im natürlichen Stil. Lautstärke wird bei Klangwahl verfügbar. Echte
Klickprobe mit 650-ms-Einstellung und lokaler Holz-Klangprobe bei 40 % ausgeführt.
Die genaue Kurve/Dauer der Animation wurde im Browser nicht messtechnisch
abgenommen; Parameterzuordnung zusätzlich im unveränderten Quellcode geprüft.

Eigene Variante „Optionsprüfung · Holztest“ ausschließlich in getrennter
Prüfbibliothek gespeichert, über die gemeinsame Bibliothek im eingebetteten
Editor erneut geöffnet und mit denselben Einstellungen bestätigt. Danach in
einer Prüfmappe gesammelt, nach Neuladen wieder geöffnet und lokal übergeben:
`runtime/button-options-20261027/qa-library/handoffs/handoff-cb77db32f0c44792bdd0453a330e0129.json`.

Zwölf bestehende Button-Werkstattprüfungen und zwei gezielte Quell-/Übergabetests
bestanden; außerdem vorhandene Node-Prüfungen für Geometrie, Schriftzuordnung,
Proportionen und Klangablauf. Alle 144 registrierten Rezepte bleiben validierbar.
Prüfdateien unter `runtime/button-options-20261027/`, reproduzierbare Übersicht:
[BUTTON_EDITOR_PRUEFUNG.json](BUTTON_EDITOR_PRUEFUNG.json), erzeugt mit
`python deploy/audit_button_editor_options.py`.

## Ergänzung vom 28.10.2026

Die **sieben passenden festen Schriftstile und 13 kurzen Klänge** der neu
recherchierten Werkstattauswahl sind jetzt im Button-Editor angebunden. Alte
Rezeptkennungen und Auswahlwerte bleiben erhalten; keine automatische
Umgestaltung bestehender Buttons. Umfang und Nachweise stehen in
[BUTTON_MEDIEN_INTEGRATION.md](BUTTON_MEDIEN_INTEGRATION.md).
Weitere Modell-/Editorprüfungen sowie persönliche Gestaltungsentscheidungen
bleiben getrennte Aufgaben.
