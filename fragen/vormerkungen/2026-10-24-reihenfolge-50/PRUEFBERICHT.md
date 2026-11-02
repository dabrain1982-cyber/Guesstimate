# Prüfbericht: 50 Reihenfolgeaufgaben, Variante 1

Stand: 24.10.2026. Status: **ausschließlich lokal vorgemerkt, nicht live aktiviert**.

## Umfang und Format

- Genau 50 Aufgaben, vorläufig `or700` bis `or749`, jeweils vier eindeutige Karten und eine vollständige eindeutige Lösung.
- 200 Karten und 73 Quellenverweise auf 73 unterschiedliche Originalseiten oder Original-PDFs.
- Bestehendes JSON-Schema, Kategorien und ID-Form eingehalten. Kein Umbau von Oberfläche, Spielmechanik oder Wertung; Variante 2 nicht umgesetzt.
- Keine Religionsfragen und keine neue biografische Wissensfrage über reale Personen. Fragen für Erwachsene aus neun Themenfeldern.

## Recherche und Eindeutigkeit

Jeder neue Wissenskern wurde tatsächlich recherchiert. Angaben wurden mit den zuständigen Verbänden, Herstellern, Museen, Fachinstitutionen oder wissenschaftlichen Lehrquellen abgeglichen. Die Aufgaben sind anhand dieser Fakten selbst formuliert. `verified` kennzeichnet die inhaltliche Quellenprüfung und verspricht keine ständige technische Erreichbarkeit jeder Webseite.

Einige Original-PDFs oder Seiten waren als ausgelesener Originalinhalt im Suchindex erreichbar, während ein direkter Neuabruf an Zugriffsschutz, Zeitlimit oder Dateigröße scheiterte. Diese Fälle stehen pro Aufgabe in `RECHERCHE.json`. Defekte Altlinks wurden ersetzt oder als redundante Belege entfernt. Es wird keine erfolgreiche visuelle Prüfung der Donaukarte behauptet.

Regelfassungen, Wettkampfart, Startpunkt, Edition und Vergleichsrichtung stehen dort in der Frage, wo sie die Lösung bestimmen. Schwankende Tabellenwerte werden als Richtwerte behandelt; die IUCN-Artenzahlen ausdrücklich auf 2024-1 datiert. Prozesskarten sind ausgewählte Schritte mit eindeutiger relativer Abfolge. Beispiele: Einzellagen statt Lagenstaffel, reguläre Kinofassung, Standard-Gitarrenstimmung und vier näher bezeichnete Herstellungsschritte.

## Dublettenabgleich

Vergleich mit 1.403 lokalen Daily-Aufgaben einschließlich der 60 inaktiven Zwei-Gruppen-Aufgaben sowie 200 früheren Vormerkungen: **1.603 Einträge**. Aufgaben, Vergleichsbegriffe, Optionen, Zuordnungen, Antworten, Erklärungen und Metadaten berücksichtigt. Volltext- und Begriffssuche mit gewichtetem Wortabgleich als Suchhilfe; ähnliche Treffer und die 50 neuen Aufgaben untereinander redaktionell nach Wissenskern bewertet. **Keine Dublette festgestellt.**

Bereits vorhandene Fakten wurden verworfen oder ersetzt: Singstimmenordnung, Tempozuordnungen Largo/Andante/Presto, Luftzusammensetzung, Mensch/Hund-Zahnzahl, menschlicher Chromosomensatz, Tennisnetzhöhe sowie Zitronensaft/reines Wasser auf der pH-Skala. Verbleibende ähnliche Themen wurden auf verschiedene Wissenskerne abgegrenzt, etwa Dichte gegenüber Schmelztemperatur oder Oberflächendruck gegenüber Sonnenabstand. Details und die nächsten Vergleichstreffer stehen pro Aufgabe in `RECHERCHE.json`.

## Ausgeführte Prüfungen

- Verbindliche Prüfung mit `python -X utf8 deploy/validate_question_library.py`: erfolgreich.
- Dieselbe Bibliotheksprüfung in einer getrennten lokalen Gesamtkopie mit allen fünf Vormerkungspaketen: erfolgreich, **1.653 Einträge**.
- 50 verschiedene Kennungen und Fragetexte; alle Kennungen im geprüften aktuellen lokalen Vergleichsbestand frei.
- Je vier unterschiedliche Karten, Antwort mit exakt denselben vier Karten, Ausgangsanordnung nicht bereits gelöst und kein Startplatz mit seiner Zielposition identisch.
- Alle Fragetexte höchstens 160 Zeichen; Quellen mit HTTPS, nicht leerem Titel und Prüfdatum; erforderliche Themenfelder vorhanden.
- Zahlenreihen separat auf strikte Ordnung geprüft; Würfelsummen durch vollständiges Auszählen aller 36 geordneten Paare nachgerechnet.
- Alle 40 geschützten Bestandsdateien einschließlich aller sechs Daily-Dateien, Manifest, Fragenlader und aller Dateien der vier früheren Vormerkungspakete per SHA-256 unverändert.
- Bestehender Projektlog-Inhalt beim Ergänzen bytegetreu erhalten.
- Aktiver Fragenlader unverändert: **269 Reihenfolgeaufgaben, 1.343 aktive Aufgaben insgesamt, keine neue Vormerkungs-ID geladen**.

## Offener Abgleich vor einer späteren Aktivierung

Die SSH-Verbindung zum maßgeblichen Server scheiterte bei diesem Arbeitsschritt mit Timeout. Das Serverlog, dortige zwischenzeitliche Änderungen und die geschützte Nutzungshistorie konnten daher nicht frisch abgeglichen werden. Vor Aktivierung müssen der aktuelle Serverbestand und `question_usage` einschließlich Inhaltsfingerabdrücken geprüft werden; Kennungen bleiben bis dahin vorläufig. Daraus wird weder ein Serverausfall noch ein aktueller öffentlicher Live-Status abgeleitet.

Es wurden keine Dateien auf den Server übertragen, keine aktiven Fragen verändert, kein Dienst neu gestartet und keine Spielergebnisse, Konten oder Nutzungsdaten geändert. Insgesamt liegen jetzt **250 neue Aufgaben lokal vorgemerkt** vor: jeweils 50 Wahr/Falsch, Auswahl, Paare bilden, Schätzung und Reihenfolge. Die lokale Lognotiz muss später zusammen mit den offenen Paar-/Schätzfragen-Notizen auf den wieder erreichbaren Server nachgeführt werden.
