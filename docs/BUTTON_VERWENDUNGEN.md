# Buttonmodelle im lokalen Hauptspiel verwenden

Stand: 28.10.2026. Diese Funktion ist lokal; sie veröffentlicht nichts auf dem Projektserver.

## Bedienweg

1. In der gemeinsamen Werkstatt **Bibliothek → Buttons** öffnen.
2. Einen eigenen gespeicherten Button über **Ansehen** öffnen und
   **Verwendungen verwalten** wählen. Im Buttoneditor befindet sich derselbe
   Zugang im Schritt **5 · Speichern**. Ungespeicherte Änderungen zuerst speichern.
3. Die Übersicht nennt den gewählten Entwurf mit Speicherdatum. Jede Einsatzgruppe
   zeigt ihre derzeitige Zuordnung: **Original** oder einen gespeicherten Stand.
   **Im Spiel ansehen** zeigt die originale Spielseite mit Beispieldaten und
   markiert den betreffenden Knopf orange. Bei gekoppelten Stellen kann der
   Spielzustand gewechselt werden. **Diese Gruppe auswählen** merkt die Wahl
   direkt dort vor; **Zur Übersicht** führt zur endgültigen Zuordnung zurück.
   **Einsatzstellen auflisten** zeigt zusätzlich die Orte und Zustände als Text.
4. Gewünschte Gruppen ankreuzen und **Zuordnung übernehmen** drücken. Das bloße
   Ankreuzen ändert nichts. Nicht ausgewählte Gruppen behalten ihre Zuordnung.
5. Zum Zurücksetzen die betreffenden Gruppen auswählen und
   **Original wiederherstellen** drücken.

Die Startseitenaktion verbindet ausdrücklich **spielen / fortsetzen** und
**heutiges ergebnis**. Beide Zustände wechseln gemeinsam. Ähnlich aussehende
Buttons an anderen Quellen bleiben unabhängig auswählbar, beispielsweise der
Nachholbutton. Die Standardansicht **Passende & zugeordnete** begrenzt die Liste
auf verwandte Gestaltungen; mit Suche, Spiel und **Alle Einsatzstellen** sind
weitere Ziele erreichbar. Beschriftung und Aktion stammen weiterhin vom Einsatzort.

Ein neuer gespeicherter Bearbeitungsstand wird nicht automatisch aktiv: Er wird
erneut den gewünschten Stellen zugeordnet. So bleibt sichtbar, welche Version gilt.

### Verwendeten Button wieder bearbeiten (29.10.2026)

In der Bibliothek beim Spielbutton **Aktuellen Spielbutton bearbeiten** wählen.
Der Editor lädt den genau dort zugeordneten gespeicherten Stand einschließlich
Schrift, Farben und Form. Eine neuere, noch nicht zugeordnete Version wird nicht
stattdessen geöffnet. Auch der ältere direkte Einstieg über `source_button`
verwendet diese Auflösung in beiden lokalen Werkstätten.

Ist keine Gestaltung zugeordnet, wird das Original als Ausgangspunkt geladen.
Die als Original bezeichnete Bibliotheksvorschau und der Originalvergleich
bleiben Referenzen der ursprünglichen Gestaltung. Ein unlesbarer zugeordneter
Entwurf wird als Fehler gemeldet, statt unbemerkt die alte Vorlage zu laden.

## Geltungsbereich und Start

Die Einbindung gehört zum normalen lokalen Hauptspiel auf
<http://127.0.0.1:8765/>. Bei geschlossenem Spiel startet
`Guesstimate-starten.cmd --main-game` diesen Bestand mit der Einbindung.
Bereits mit der Einbindung geöffnete Seiten lesen neue Zuordnungen automatisch.
Die aktuelle Conquest-Arbeitsvorschau auf 8767 ist ein separates Programm;
ihre räumlichen Spezialaktionen sind hier noch nicht angeschlossen.

Der Bestand bleibt bei 144 Buttonansichten und 85 Gestaltungsmodellen. Für die
Zuordnung gibt es 140 getrennte Einsatzgruppen: 112 sind angeschlossen, 28
Spezialkomponenten bzw. nicht eindeutig zuweisbare Quellen sind sichtbar gesperrt.
Das ist keine vollständige Funktionsabnahme aller 112 Ziele.

## Erhaltung und Umsetzung

- Entwurfsdateien und Originalvorlagen werden beim Zuordnen nicht überschrieben.
  Neue Zustände liegen als fortlaufende Dateien in `design-library/button-usage/`.
  Eine veraltete geöffnete Übersicht kann einen neueren Stand nicht überschreiben.
- Nur der lokale Starter registriert `workshop_buttons.py`. `app.py` und die
  Originaltemplates bleiben gegenüber dem Beginn dieser Arbeit unverändert.
  Die Zuordnungsmarkierungen entstehen im Speicher beim Laden der Templates.
- Die Darstellung verwendet den gemeinsamen Buttonrenderer aus der Werkstatt.
  Der ursprüngliche Spielknopf behält Formulardaten und Aktionen; seine sichtbare
  Darstellung wird proportional durch das gewählte Modell ersetzt. Beim
  Zurücksetzen erscheint wieder das ursprüngliche Element. Gestaltete Aktionen
  werden als Buttons bedient, auch wenn die ursprüngliche Aktion ein Link war.
- Entwurfsabrufe und Darstellungsdateien schreiben keine Anmeldungen oder
  Spielhistorie. Die Funktion ist außerhalb des lokalen Starters nicht aktiv.

## Nachgewiesene Prüfung am 28.10.2026

Mit getrennten Entwürfen, Zuordnungen und einer getrennten Spieldatenbank wurden
die tatsächlichen Hauptspielseiten auf 8778 geprüft: Starten/Fortsetzen öffnete
die Fragerunde, der zweite Startzustand das Ergebnis. Ein zusätzlich gewählter
Nachholbutton behielt seinen dynamischen Tageszähler und startete die richtige
Nachholrunde. Übernehmen und Zurücksetzen erschienen automatisch auf einer
bereits geöffneten Spielseite; danach waren die Originale wieder sichtbar.

In der persönlichen Bibliothek wurde der Zugang **Test 1 → Ansehen →
Verwendungen verwalten** mit der aufgeklappten Startgruppe geprüft. Es wurde keine
persönliche Zuordnung angewendet. Die persönliche gestalterische Abnahme bleibt
beim Nutzer.

Prüfnachweise: `runtime/button-usage-20261028/`, insbesondere
`tests-latest.txt`, `verification.json` und `verwendungen-persoenlich.png`.

### Ergänzung: Einsatzort sehen (28.10.2026)

Die Einsatzort-Vorschau verwendet die originalen Templates, Räume, Hintergründe
und Stile mit neutralen Beispieldaten. Ein orangefarbener Rahmen markiert den
betreffenden Knopf beziehungsweise wiederholte Knöpfe derselben Quelle. Versteckte
Shop-/Profilbereiche und Dialoge werden im passenden Zustand geöffnet. Die ganze
Spielansicht wird proportional eingepasst und lässt sich scrollen. Die Vorschau
zeigt das Original; der gespeicherte Entwurf wird erst beim Übernehmen eingesetzt.

Direkt bei der Ansicht kann die Gruppe zur Auswahl hinzugefügt oder entfernt
werden. Bei der Startseitenaktion lassen sich Spielen/Fortsetzen und Ergebnis
umschalten. Die endgültige Zuordnung erfolgt anschließend in der Übersicht.

Die Vorschau führt keine Spielaktionen aus und lädt keine persönlichen Daten.
Sie verwendet dieselben vorhandenen Vorlagen wie das Spiel und die bestehenden
neutralen Werkstattbeispiele, ohne eine zweite Seitenkomposition zu pflegen.
Alle 116 Ansichten der 112 anschließbaren Einsatzgruppen wurden auf erfolgreiche
Darstellung mit Zielmarkierung geprüft. Zusätzlich sichtbar im Browser geprüft:
beide Startzustände, Nachholdialog, Auswahl neben der Ansicht und Shop-Hintergründe.
Keine vollständige visuelle Abnahme sämtlicher Ansichten behauptet.
Nachweise: `runtime/button-context-20261028/`.

