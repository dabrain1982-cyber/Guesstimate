# Offene Gestaltung und Reihenfolge

Stand: 25.10.2026. Grundlage sind die ausdrücklichen Nutzerwünsche zur
Comicgestaltung und die lokale Buttonreferenz „Screenshot 2026-10-24 175332.png“.
Dieses Dokument beauftragt keine Veröffentlichung oder zusätzliche Grafikerzeugung.

## Was als fertig gelten darf

Ein vorhandener oder funktionierender Baustein ist keine abgeschlossene
Comicgestaltung. Die bisherigen Buttons, Phasen-/Zuganweisungen und viele Dialoge
sind funktionaler Bestand mit offener gestalterischer Überarbeitung. Ihre alten
Formen dürfen nicht als fertiger Standard in weitere Spieloberflächen übernommen
werden. Gemeinsame Spielregeln, Schriftgrundlagen, Aktionsfarben und vorhandene
Profilausrüstung bleiben maßgeblich; die neue Formgestaltung wird zentral erarbeitet.

Die kompakte Conquest-Spieleranzeige kann unabhängig davon mit dem vorhandenen
Avatarbestand umgesetzt werden. Sie benötigt weder neue Gewinnerbilder noch eine
Übernahme der älteren Party-Ergebnisdarstellung.

## Nächste Reihenfolge

1. **Kompakte Conquest-Spieleranzeige:** vorhandenes Avatarbild, Name, Armeefarbe,
   Truppen, Länder und Kartenanzahl bei jeder Armee; ein gemeinsamer
   Porträtbaustein. Neue Nutzerpräzisierung: Spielaktionen als kleine Leiste
   unten ohne Kasten und zusätzlichen Avatar, keine große kombinierte Spieler-/Aktionskonsole. Lokal im normalen
   Conquest-Tisch verbunden; Test mit vier Personen sichtbar geprüft.
2. **Gemeinsame Comic-Bedienelemente als eigener Entwurf:** zuerst Buttons und
   spielbegleitende Anzeigen zusammen erproben. Ausgeprägte dunkle Unterkante,
   sichtbare räumliche Tiefe, beim Drücken kleinere Unterkante und abgesenkte
   Oberfläche. Die Form soll lebendiger und comicartiger als ein sauberer
   moderner Standardknopf wirken. Dazu passend detailliertere Spielanweisungen,
   Phasenanzeigen und Dialoge. Normal, gedrückt, Fokus und deaktiviert gemeinsam
   prüfen; kleine Bildschirmgrößen und Lesbarkeit berücksichtigen. Keine
   unkontrollierten Einzelvarianten je Spiel. Ein separater lokaler Entwurf ist
   jetzt unter [Comic-Vorschau 01](../offline-preview/comic-ui-v1/README.md)
   vorhanden: Drucktiefe, Maus-/Tastaturzustände, Conquest-Zugleiste, Inventar,
   Würfelstand und Zeitanzeige mit Beispielwerten. Im Browser geprüft, noch
   nicht als Gestaltung abgenommen oder in die normalen Spiele eingebaut.
   Die Tafel wird auf ausdrücklichen Nutzerwunsch dauerhaft in der
   [Entwurfssammlung](../offline-preview/SAMMLUNG.md) aufbewahrt. Druckweg
   „dezent“ ist die bevorzugte Bewegung und Voreinstellung. Form und Oberfläche
   bleiben offen. Die ergänzende [Button-Werkstatt UI-002](../offline-preview/button-workshop-v1/README.md)
   ist jetzt lokal umgesetzt: Form, Material, Schriftwirkung, Bewegung und
   optionale Klänge kombinieren, A/B vergleichen und benannte Stände mit Notizen
   sowie Einzelbewertungen dauerhaft auf diesem PC speichern. Ausgangswert
   bleibt „dezent“, 300 ms, ohne Ton. Die Werkstatt ist keine gestalterische
   Gesamtfreigabe und ändert keine normalen Spiele.
   Auf Nutzerpräzisierung ist Comic nur die aktuell gewünschte Stilrichtung:
   Der Generator bietet zusätzlich Natürlich und Grafisch, unabhängig von Form
   und Material. Freie Randpunkte/Rundungen und gespeicherte eigene Konturen
   sind ergänzt. Die zunächst abgelehnten Materialmuster wurden durch neue
   lokale Oberflächentexturen ersetzt; deren Wirkung bleibt zu bewerten.
   Als nächster zusammenhängender Versuch ist die
   [Conquest-Zugtafel UI-003](../offline-preview/conquest-console-v1/README.md)
   lokal vorhanden: gespeicherte Holz-/Zehn-Punkte-Form mit Spielerwerten,
   Verstärken, Angriff, Festigen, Bestätigungen, Zugzusammenfassung und
   Wartestatus. Die Tafel verwendet dieselben Button- und Porträtbausteine,
   ausschließlich mit Beispielwerten. Sichtbar geprüft, weiterhin vor der
   gestalterischen Bewertung und vor einem Einbau in normale Partien.
   Der Nutzer kann mit dieser großen Konsole aktuell wenig anfangen. UI-003
   bleibt als Arbeitsstand erhalten, ist jedoch keine Vorlage für den Spieleinbau.
   Stattdessen wird jetzt der gespeicherte Eintrag „Stormseed´s conquest“ direkt
   in Conquest bei der unteren Hauptaktion und „Truppen verteilen“ erprobt.
   Dieselbe Buttonkomponente und derselbe Materialrenderer wie in der Werkstatt;
   fester Einstellungsstand, keine automatische Livebindung an spätere Entwürfe.
   Truppen/Länder/Kartenanzahl kommen kompakt zum jeweiligen Avatar. Der
   Generator und die übrigen älteren Spielbuttons bleiben gestalterisch offen.
   Weitere lokale Präzisierung: gewöhnliche Länderauswahl ohne Infobox und
   Angriffsvorbereitung ohne Dialog. Die eigene Quelle zeigt Comic-Pfeile nur
   zu angreifbaren Feindländern; eigene Nachbarn bleiben im Angriff unmarkiert.
   Quelle/Ziel und Würfelwahl stehen direkt über der einzelnen Hauptaktion.
   Würfel starten bei jeder neuen Wahl am Maximum, Mausrad zurück reduziert;
   Klick und Tastatur ergänzen die Bedienung. Der Nutzer hat ausdrücklich den
   bisherigen Ablauf bestätigt: Angriff beenden führt zuerst zum Festigen,
   danach folgt das Zugende. Der verfügbare Truppenvorrat bleibt sichtbar.
3. **Weitere Spielanzeigen anschließen:** nach der gemeinsamen Gestaltungsbasis
   die passenden Werte/Status bei Würfelspielen, Perfect und kompakten Listen
   anbinden. Funktionale Arbeiten können getrennt geprüft werden, dürfen aber
   keine alten Oberflächen als endgültiges Design festschreiben.
4. **Party-Endergebnis eigenständig gestalten:** ein modernes, spannenderes
   Siegertreppchen entwerfen und vor dem Umbau ansehen. Die bisherige
   `podium`-Darstellung bleibt bis dahin Altbestand; keine bloße Zwischenmigration
   als vermeintlich fertiger gemeinsamer Ergebnisbaustein. Gewinneransichten und
   eventuell Verliereransichten je vorhandenem Avatar sind eine zu prüfende Idee.
   Umfang, Posen und tatsächliche Grafikerzeugung sind noch nicht entschieden.

Weiterhin gelten: keine zusätzlichen Avatare während der Quizfragen; am
Kartentisch erst eine gesonderte Platzprüfung mit zwei, vier und sechs Personen;
Perfect behält Zettel und Buzzer. Die Bildreferenz dient als Gestaltungshinweis,
nicht als zu kopierendes fremdes Spielasset.


## Conquest: nächste Einzelschritte ab 26.10.2026

Auf Nutzerwunsch einzeln umsetzen und jeweils lokal ansehen, nicht das ganze
Paket zusammen einbauen. Aktueller Auftakt: Nach bestätigtem Kartentausch
klappt die eigene Hand automatisch ein. Solange die Abgabe läuft oder bei
Ablehnung bleibt sie mitsamt Auswahl geöffnet; kein Verlust bei Speicherfehler.

1. **Oberen Streifen entfernen – lokal umgesetzt (26.10.2026):** Der Name steht bereits auf dem Brett.
   Kamerabedienung klein unten rechts, Rückweg zur Lobby weiter erreichbar.
   Den frei werdenden oberen Platz wirklich für das Brett nutzen; die
   bisherige Kameraeinpassung darf keine obere Werkzeugleiste mehr reservieren.
   Noch keine Änderung der eigentlichen Kamerabewegung in diesem Schritt.
2. **Kartenempfang und Hinweiszeiten – lokal umgesetzt (26.10.2026):** Neue Länderkarte einmal in der
   Bildschirmmitte anzeigen, nach zwei Sekunden zum eigenen Avatar bewegen
   und dort verschwinden lassen. Dieselbe Kartenkomponente verwenden.
   Aktualisierungen dürfen die Bewegung nicht ständig wiederholen.
   „Dein Zug!“ ebenfalls zwei Sekunden; Pflichttausch bleibt bis zur Erfüllung.
3. **Nahblick der Kamera:** Vorrollen soll weiter zum Brett führen und nicht
   erst vergrößern, dann in einer höheren Ansicht wieder verkleinern.
   Separat erproben. Nutzer hat ausdrücklich bestätigt, dass äußere Länder
   beim starken Nahblick aus dem Ausschnitt geraten dürfen. Das ersetzt für
   diesen Nahblick die bisherige Vorgabe „immer alle Länder vollständig“;
   der Überblick bleibt als Rückkehrpunkt erhalten.
4. **Gemeinsame Klangauswahl:** Passende Kartenklänge für Erhalten, Aufklappen
   und Einklappen hörbar vergleichen. Dieselben Klänge sollen in der lokalen
   Button-Werkstatt auswählbar sein, kein zweiter separater Soundbestand.
   Danach Angriffsklänge mit mehreren Varianten; Säbelkampf als gewünschter
   Standardkandidat. Aufnahmeherkunft und Nutzbarkeit prüfen, bevor neue
   Klänge fest eingebaut werden. Vorhandene Synthese-Platzhalter nicht als
   fertige Materialien oder Kartengeräusche behandeln.
5. **Werkstatt später auf Elemente erweitern:** Über Buttons hinaus etwa
   Karten, Spielanzeigen und Tafeln gestalten. Bisherige gespeicherte Formen,
   Buttonentwürfe und Sammlung erhalten; gemeinsame Form-, Material-, Schrift-,
   Bewegungs- und Klangbausteine weiterverwenden. Noch kein allgemeiner
   Editorumbau im aktuellen ersten Schritt.

Der bisherige Kameracode erklärt den gemeldeten Größensprung: bei jedem
Blickwinkel wird die Entfernung neu so gewählt, dass die vollständige Karte
ins Bild passt. Ein echter Nahblick braucht deshalb eine bewusst andere
Einpassung, nicht nur einen weiter reichenden Winkelregler.
