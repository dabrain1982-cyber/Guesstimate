# Sammlung der Gestaltungs- und Einstelltafeln

Diese lokalen Tafeln bleiben als wiederauffindbare Arbeitsmittel erhalten.
Sie dienen dem Ausprobieren und Vorbereiten künftiger Einstellungen. Ein
vorhandener Entwurf ist keine Freigabe für den Einbau in die Spiele.

Im Projektordner öffnet **Werkstaetten-starten.cmd** alle benötigten Dienste
und die [gemeinsame Übersicht](http://127.0.0.1:8771/sammlung). Ausführliche
Hinweise stehen in [LOKAL_STARTEN.md](../LOKAL_STARTEN.md).

| Kennung | Tafel | Zweck | Festgehaltener Stand |
|---|---|---|---|
| UI-001 | [Comic-Buttons und Spielanzeigen](comic-ui-v1/README.md) | Buttons, Druckweg, Zustände, Conquest-Zugleiste, Inventar, Würfel und Uhr gemeinsam ansehen und bedienen | Bewegung mit Druckweg **dezent** gefällt. Form und Oberfläche bleiben offen. Schriftwirkung und Sound sind weitere zu untersuchende Dimensionen. |
| UI-002 | [Button-Werkstatt](button-workshop-v1/README.md) | Unabhängige Stilwahl Comic/Natürlich/Klar; freie Konturen mit Rundungen, Holz/Stein/Metall, Beschriftung, Bewegung und Klang; A/B-Vergleich; gespeicherte/exportierte Entwürfe | Comic ist aktueller Wunsch und Voreinstellung. Freier Kontureditor und neue lokale Materialtexturen ergänzt; Materialwirkung weiter zur Bewertung. Alte Entwurfsdateien erhalten und lesbar. Start bei **dezent**, 300 ms, ohne Ton. Kein Spieleinbau. |
| UI-003 | [Conquest-Zugtafel](conquest-console-v1/README.md) | Gespeicherte Holz-/Zehn-Punkte-Form zusammen mit Spielerwerten, drei Zugphasen, Bestätigungen, Zugende und Warten ausprobieren | Lokale Beispielrunde auf **8773**. Gemeinsame Buttons und Spielerporträt; dezent, 300 ms, ohne Ton gestartet. Form und Material bleiben Arbeitsentwürfe. Kein Einbau in normale Partien. |
| GAME-001 | [Deine Werkstatt](game-workshop-v1/README.md) | Projektunabhängige Werkzeuge und Bibliothek mit gemeinsamer Elementliste; freie Projektmappen sammeln mehrere Varianten und bereiten das Interview vor | Lokal auf **8776**, Einstieg Buttons. Vorhandene Button-Werkstatt direkt eingebunden. Schach bleibt eine Projektmappe. Kamera und Verhalten sind offene Projektentscheidungen. |

UI-003 ist nach aktueller Rückmeldung keine geeignete Vorlage für die
Spieloberfläche und bleibt nur als Arbeitsstand erhalten. Der aktuelle Test
findet direkt im lokalen Conquest-Tisch statt: kompakte Avatarwerte und
untere Aktionen mit dem gespeicherten „Stormseed´s conquest“-Entwurf.

Die erste Tafel liegt dauerhaft unter `offline-preview/comic-ui-v1/`.
UI-002 führt eigene Konturen jetzt unter **Deine Formen** und bietet eine
**Klanggalerie** mit zehn recherchierten Hörbeispielen. „Grundform zurücksetzen“
und „Form als Vorlage speichern“ sind getrennte Aktionen. Zusätzliche Schriften
und passende oder manuelle Schriftzuordnung gehören ebenfalls zur Werkstatt.
Startanweisung und Vorschauadresse stehen im verlinkten README. Die Dateien
bleiben auch erhalten, wenn Browser oder lokaler Vorschaudienst beendet werden.
Das aktuelle Einstellungs-/Bewertungsblatt steht in
[entwurf.json](comic-ui-v1/entwurf.json). Es dokumentiert die Auswahl; es ist
noch kein allgemeines Import-/Exportformat eines Generators.

## Wie die Sammlung wachsen soll

- Bestehende Tafeln nicht bei der nächsten Aufgabe verwerfen oder unbemerkt
  durch eine andere Stilrichtung ersetzen. Weiterentwicklungen und Bewertungen
  mit Datum nachvollziehbar halten.
- Einstellungen, Materialideen und Bewertungen getrennt festhalten. Eine
  gefallende Bewegung macht Form, Oberfläche oder den gesamten Entwurf nicht
  automatisch fertig.
- Bei weiteren Tafeln dieselben gemeinsamen Bausteine verwenden. Varianten
  künftig als benannte Einstellungen speichern, ohne unabhängige Kopien ihrer
  Innenkomposition in einzelne Spiele einzubauen.
- Die erste Button-Werkstatt UI-002 ist lokal umgesetzt. Ihre persönlichen
  Entwurfsdateien liegen dauerhaft unter `design-library/recipes/button-workshop/`,
  getrennt von den Spielständen. Speichern erzeugt neue Stände. Die erste Tafel
  bleibt daneben erhalten; weitere Elemente können später eigene Tafeln bekommen.
