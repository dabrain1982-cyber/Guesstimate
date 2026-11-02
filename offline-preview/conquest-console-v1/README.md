# UI-003 · Conquest-Zugtafel

Lokale Vorschau: <http://127.0.0.1:8773/>.

```powershell
python -X utf8 offline-preview/conquest-console-v1/serve.py --port 8773
```

Die Tafel bindet ausschließlich an diesen PC. Sie importiert weder die
Spielanwendung noch eine Datenbank und bietet keine Schreibschnittstelle.
Alle Aktionen betreffen Beispielwerte im geöffneten Browser. Neuladen bzw.
„Beispiel zurücksetzen“ beginnt das gewählte Beispiel erneut.

## Ausprobieren

- Unter **Beispielsituation** direkt zu Verstärken, Angriff, Festigen,
  Zugende oder Warten wechseln.
- Sechs Verstärkungen auf eigene markierte Länder verteilen; die nächste
  Phase wird erst danach freigegeben. Auswahl über Karte oder Liste.
- Einen Angriff vorbereiten, abbrechen oder einen ausdrücklich festen
  Beispielwurf ansehen: 5/3/2 gegen 4/1, zwei Verluste bei der Verteidigung.
- Einmal nach Südeuropa festigen, mit Vorher-/Nachher-Anzeige und mindestens
  einer verbleibenden Truppe in Westeuropa. Beide Länder sind direkte Nachbarn.
- Zug abschließen und die Zusammenfassung ansehen. Erst **An Robin übergeben**
  wechselt zur nächsten Person. Schließen der Zusammenfassung lässt den
  bereits abgeschlossenen Zug unverändert. Im Wartestatus sind die eigenen
  Spielaktionen gesperrt und Robins Reserve wird nicht offengelegt.
- Inventar mit drei ausdrücklich benannten Platzhalterkarten öffnen.
- Materialklang bei Bedarf einschalten; Start immer ohne Ton. Holzplanken-
  Kandidat von Kenney, CC0, Quelle/Lizenz auf der Tafel. Technische Wiedergabe
  geprüft; keine klangliche Abnahme.

## Gemeinsame Gestaltung

`profile.json` ist eine feste Kopie der am 25.10.2026 vorhandenen Auswahl
„Werkstatt-Holz“ und „Werkstatt-Holz · Form“: Zehn-Punkte-Kontur, Holz,
Fredoka, aufgemalte Beschriftung, dezent/4, 300 ms. Persönliche Entwurfsdateien
bleiben erhalten. Künftige Werkstattänderungen verändern diese Tafel nicht
automatisch. Das ist noch keine allgemeine Übernahme beliebiger Entwürfe.

Buttons verwenden dieselbe Grundkomponente wie UI-001 und denselben
Materialrenderer wie UI-002. Die Tafel ergänzt keine zweite Button-Komposition.
Hauptaktionen sind grün bemalt (stärkerer Farbauftrag), andere Knöpfe erhalten
den Holzton. Kontur und Bewegung bleiben gleich. Aktionsknöpfe behalten beim
Aktualisieren ihre Elemente und ihre Abwärts-/Aufwärtsbewegung; die aktuelle
Phase bleibt abgesenkt. Bestätigungen bleiben bis zum Ende des Druckimpulses
sichtbar. Der Materialrenderer bietet optionale Symbol-/Farbauftragsparameter;
vorhandene Werkstattaufrufe behalten ihr bisheriges Verhalten.

Die Spieleranzeige verwendet unverändert `static/player-portrait.js` und dessen
gemeinsame Gestaltung. Größenanpassung erfolgt proportional über die Größe des
ganzen Bausteins. Karte und vorhandene Avatarbilder werden unverändert geladen.
Die farbige Karte wird vollständig im ursprünglichen Seitenverhältnis gezeigt.
Nur sechs Beispielpositionen sind markiert; dies ist kein vollständiger
Karteneditor und keine spielbare Conquest-Implementierung.

## Geprüfter Stand vom 25.10.2026

- Sieben Ablaufprüfungen einschließlich vollständigem Zug, ungültigen Aktionen,
  getrenntem Abschluss/Übergabe und Nachbarschaftsabgleich mit der Weltkarte.
- Zwei HTTP-Prüfungen: alle freigegebenen Dateien erreichbar, private Pfade
  und Schreibzugriffe gesperrt. Zehn bestehende Werkstattprüfungen und deren
  Geometrie-/Schrift-/Audio-Prüfungen weiterhin erfolgreich.
- Sichtbare Browserprüfung des gesamten Ablaufs, Abbrechen/Escape,
  Materialklang, Druckbewegung und schmalen Ansichten.

Die Tafel ist ein **Arbeitsentwurf zur Ansicht**, keine gestalterische Freigabe.
Form, Materialwirkung, Schrift und Klang bleiben bewertbar. UI-001 und UI-002
bleiben erhalten. Kein Einbau in das normale Spiel und kein Servertransfer.
