# Abschlussabgleich der Werkstattelemente

Stand: 27.10.2026. Ausschließlich lokal. Im unten abgegrenzten aktuellen
Spielbestand sind keine offenen Elementzuordnungen mehr festgestellt worden.
Die gemeinsame Material-/Ansichtsübersicht und Projektwünsche sind inzwischen
unter [MATERIAL_DARSTELLUNG.md](MATERIAL_DARSTELLUNG.md) umgesetzt. Editoroptionen,
bausteinspezifische Material-/Darstellungsumsetzung und persönliche Abnahme
bleiben spätere Aufgaben.

## Geprüfte Spiele

| Spiel | Einbezogene vorhandene Oberflächen und Ausstattung |
|---|---|
| Guesstimate | Startseite, Fragen und Auflösungen, Ergebnis, Antwortübersicht, Ranglisten, leerer Fragenvorrat; Profilkulisse. |
| Guesstimate Party | Einstieg, Lobby, Countdown, Fragen/Auflösungen und Ergebnis; gemeinsame Profilkulisse. |
| Perfect | Einstieg, eigener Lobby-/Clubraum und sämtliche vorhandenen Phasenfenster; Fragen nur über Datenquellen. |
| Playtable | Übersicht, Lobby, Kartentisch, Hände/Stapel, Spielerpulte, Aktionsflächen, Gebote und Notiz; ganze endliche Kartensätze. |
| Würfeltisch | Übersicht, Lobby, Tisch, physikalische Würfel, Spieler, Aktionspult und Anzeigen. |
| Kniffel | Gemeinsame Würfelräume und -komponenten, Haltefelder und Kniffelblock als bestehende Bausteine. |
| Mäxchen | Gemeinsame Würfelräume, eigener Aktionspult-/Ansagezustand; verdeckter Wurf als Zustand derselben Würfel/Anzeige. |
| Conquest | Aktuelle räumliche Tischoberfläche, Brett, Raum, Truppenmarke, Karten-/Auftragssätze, Zugleiste, Kämpfen und Verschieben, Hinweise und Endstand. |

Die gemeinsame Spielesammlung sowie eingebundene Makros für Regeln, Profil,
Porträts, Lobbys, Flyer und Symbole sind einbezogen. Die ältere, aktuell nicht
geladene Conquest-Tischdarstellung wird nicht als aktuelle Oberfläche gezählt.

## Geschlossene Lücken

Neun ganze Raumkonfigurationen sind als zwei Grundmodelle **2D und 3D** im
Hintergrundbereich ergänzt. Conquests Wand, Möbel und Teppich sind ein Element;
der Tisch/das Brett bleibt ein eigener Baustein. Acht flache Raumkonfigurationen
verwenden die ursprünglichen CSS-Kompositionen und Motive. Perfect behält seine
ursprünglichen Vorhänge, Lichter und Raumdekoration. Die 15 zuvor registrierten
Bildmotive bleiben mit denselben Kennungen und Schnappschüssen erhalten.

Beim Abschlussabgleich fehlten außerdem vollständige Quizkompositionen oberhalb
der bereits aufgenommenen Antwortfelder und Einzelanzeigen. Ergänzt sind fünf
gemeinsame Fenstermodelle mit 30 festen Beispielen: vollständiges Fragenfenster
(16: zwei Spiele, fünf Fragearten und drei Auflösungszustände), Rundenergebnis
(3), Antwortübersicht (3), Ranglistenrahmen (7: Start-/Ergebnisseite mit ihren
vorhandenen Reitern) und leerer Fragenvorrat (1). Insgesamt nun **35 Modelle und
114 Quellbeispiele**. Die ursprünglichen 84 Fensterkennungen sind unverändert.

Diese Vorschauen verwenden neutrale Platzhalter. Kein Frageninhalt ist als
Karte oder anderes eigenes Element registriert. 40 vorhandene/neue
Fragenfensterbeispiele tragen einen Feldvertrag und Verweise auf die
Fragenbanken; ein wachsender Fragenbestand verändert den Katalog nicht.

## Nachweise und Grenzen

Der reproduzierbare [Quellenbericht](WERKSTATT_ABSCHLUSSPRUEFUNG.json) hält
60 aktuelle Vorlagen-/Stil-/Fabrikquellen mit Prüfsummen fest. 65 semantische
Container sind geprüft: 53 innerhalb registrierter Komponenten, zehn belegte
Anordnungen bereits registrierter Bausteine und zwei begründete Ausschlüsse
(persönliche Grußfolie und technischer Entwicklerhinweis). 13 zentrale
DOM-/3D-Fabriken sind den bestehenden Elementfamilien zugeordnet. Die sechs
erneuerten Quellprüfungen für Buttons, Fenster, Eingaben, Anzeigen, Spieler und
Lobbys melden keine fehlenden Zuordnungen. Die bisherige Fensterprüfung belegt
84 Beispiele; die zusätzlichen 30 sind separat im Abschlussbericht aufgeführt.

Die Prüfung kombiniert Quellenabgleich und lokale Bibliotheksvorschauen. Sie
behauptet keinen Durchlauf jeder möglichen Partie oder sämtlicher Spielzustände.
Native Browserdialoge, technische Bibliotheksinternas und inaktive Prototypen
sind kein zusätzlicher Werkstattausstattungsbestand. Zahlen, Antworten, Personen,
Spielstände, Routen, Kamerapositionen und Materialparameter sind Daten bzw.
Eigenschaften bestehender Bausteine.

19 gezielte Tests bestanden: Raum-/Quellenbindung, ursprüngliche Raumfabrik,
stabile bisherige Kennungen, neutrale Fensterwerte, Fragenwachstum ohne neue
Elemente, lokale Vorschauwege sowie Speichern/Wiederverwenden/Neuladen/Übergabe.
Zusätzliche JavaScript-Syntaxprüfung bestanden. Alle neun Räume und 30 neuen
Fensterbeispiele im Browser geladen; Ansichtswechsel des Conquest-Raums und eine
getrennte Prüfmappe mit Raum und verknüpftem Fragenfenster nach Neuladen und
lokaler Übergabe geprüft. Belege: `runtime/completeness-20261027/`.

Schutzvergleich: 590 zuvor erfasste Dateien und sämtliche sieben persönlichen
JSON-Dateien unverändert; keine neuen persönlichen JSON-Dateien. Keine
Spielintegration, Fragenbearbeitung, Veröffentlichung oder Projektserverabfrage.

Erzeugen: `python deploy/audit_workshop_completeness.py`.

## Erster anschließender Editorcheck

Neun Guesstimate-Kernmodelle des Button-Editors sind inzwischen technisch auf
sinnvolle Verfügbarkeit ihrer Optionen geprüft. Kontextabhängige Bedienkorrekturen
ohne Änderung von Originalen oder Renderer; keine vollständige Abnahme aller
85 Modelle. Siehe [BUTTON_EDITOR_PRUEFUNG.md](BUTTON_EDITOR_PRUEFUNG.md).

Seit 28.10.2026 sind die sieben passenden festen Schriftstile und 13 kurzen
Werkstattklänge auch im Button-Editor ausdrücklich wählbar. Bestehende Auswahl,
Rezepte und Spielzuordnungen bleiben erhalten. Siehe
[BUTTON_MEDIEN_INTEGRATION.md](BUTTON_MEDIEN_INTEGRATION.md).
