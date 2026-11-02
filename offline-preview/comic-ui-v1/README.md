# Comic-Buttons und Spielanzeigen · Entwurf 01

Die verbindliche Button-Grundgestaltung liegt jetzt in
`static/comic-button.css`; diese Tafel lädt dieselbe Datei wie der lokale
Conquest-Test. Ihre übrigen Muster und Einstellungen bleiben erhalten.

Dauerhaft aufbewahrte Tafel **UI-001** in der
[Sammlung der Gestaltungs- und Einstelltafeln](../SAMMLUNG.md).
Bevorzugter Stand vom 25.10.2026: Druckweg **dezent**. Diese Voreinstellung
bleibt beim erneuten Öffnen erhalten. Form und Oberfläche sind weiterhin offen;
Schriftwirkung und Sound sind zusätzliche Gestaltungsdimensionen. Die Auswahl
und ihre getrennten Bewertungen sind in [entwurf.json](entwurf.json) festgehalten.

Eine eigenständige lokale Designvorschau nach der Nutzerreferenz
„Screenshot 2026-10-24 175332.png“. Keine Anbindung an Spielzüge, Konten,
Fragenverbräuche oder eine Datenbank. Der normale Spielbetrieb lädt diese Dateien
nicht; ein Neustart der Anwendung ist nicht erforderlich.

Start im Projektordner:

```powershell
python offline-preview/comic-ui-v1/serve.py --port 8770
```

Danach `http://127.0.0.1:8770/` öffnen. Der Server bindet ausschließlich an diesen
PC und liefert nur die aufgeführten Vorschau-/gemeinsamen Assetdateien.
Die lokale Referenzaufnahme liegt unverändert im ignorierten Laufzeitordner
`runtime/comic-ui-v1-20261025/reference.png`.

## Enthalten

- Genau eine Button-Komposition in `components.js`/`comic-ui.css`: feste dunkle
  Unterkante, bewegliche Vorderseite, eigene Lichtkante, unregelmäßig gerundete
  Kontur. Hauptaktion, Nebenaktion und blaue Materialvariante verwenden dieselbe
  Komposition. Größe und Tiefe sind gemeinsame Parameter.
- Normal, Hover, gedrückt, ausgewählt, Tastaturfokus und tatsächlich deaktiviert.
  „Druck festhalten“ ermöglicht einen dauerhaften Sichtvergleich. Echte
  Maus-/Tastatureingaben verwenden dieselben Druckregeln. Normale Aktionsbuttons
  führen auch bei kurzem Klick einen vollständigen Druckweg aus: hinunter,
  kurz gedrückt, wieder hinauf (300 ms). Ausgewählte Phasen und Umschalter
  bleiben unten. Die Aktion selbst wird sofort genau einmal ausgeführt; sie
  wartet nicht auf die Animation. Bei reduzierter Bewegung nur kurzer
  diskreter Druckzustand, ohne fließende Bewegung.
- Veränderbare Drucktiefe, Conquest-Phasenwechsel mit gemeinsamem unverändertem
  Porträtbaustein, Inventardialog, Würfelstand und Uhr mit Warn-/Endzustand.
- Nur Beispielwerte. Die Würfe zeigen einen festgelegten Beispielablauf, keine
  echte Zufalls- oder Spielregelberechnung. Phase/Spieler wechseln nur im Browser.
- Bestehende Avatar-/Kartenbilder und lokale Schriften. Keine neue Rastergrafik,
  kein fremdes Asset aus dem Referenzspiel kopiert.

## Status

Lokaler, zu besprechender Gestaltungsentwurf. Nicht in die normalen Spiele
eingebaut und keine Freigabe der alten oder neuen Anzeigen als endgültiges Design.
Weitere Umsetzung folgt erst nach dem Anschauen und einem eigenen Auftrag.
Der Party-Ergebnisentwurf bleibt eine eigenständige spätere Arbeit.
