# Lokale Entwurfsbibliothek

Hier liegen dauerhaft gespeicherte persönliche Varianten aus der Button-Werkstatt.
`recipes/button-workshop/` enthält JSON-Dateien, keine Spielstände. Der Ordner
ist von Git ausgeschlossen, bleibt aber beim Beenden und Neustarten erhalten.
Diese Dateien sind Benutzerdaten und dürfen nicht als temporäre Prüfdaten
bereinigt werden. Eine normale Datensicherung sollte diesen Ordner einschließen.

Jedes Speichern erzeugt einen neuen Stand. Vorhandene Stände werden nicht
überschrieben oder gelöscht. Export und erneutes Einlesen sind in der Werkstatt
möglich. Werkzeuge und Materialdefinitionen liegen unter
`offline-preview/button-workshop-v1/`.

Die Spielewerkstatt unter `offline-preview/game-workshop-v1/` ergänzt:

- `elements/`: eigene Brett-, Figuren-, Raum-, Kamera-, Licht-/Verhaltens-,
  Lobby-, Würfel- und Kartenvarianten.
- `projects/`: Projektmappen mit vollständigen Einstellungswerten und festen
  Referenzen auf die gewählten Bibliotheksstände; ausgewählte Buttons werden
  zusätzlich als unveränderte Momentaufnahme aufgenommen.
- `handoffs/`: vollständige Übergabedateien (JSON) und lesbare Begleittexte (MD).
- `images/originals/`: unveränderte importierte Rasterbilder.
- `images/variants/`: daraus erzeugte eigene PNG-Varianten.
- `images/records/`: Bildkennungen, Maße, Prüfsummen, Herkunft und genaue
  Ausschnitt-/Ausgabewerte. Diese gehören zusammen mit den Bilddateien in
  die Datensicherung. Neue Bildvarianten überschreiben keine Originaldatei.

Auch diese Ordner sind persönliche, von Git ausgeschlossene Daten und gehören
in die normale Datensicherung. Alle Speichervorgänge erzeugen neue Stände.
Das bloße Öffnen der Werkstatt legt keine persönlichen Bibliotheksdateien an.
Browser-Zwischenstände sind nur eine zusätzliche Hilfe; dauerhaft auf dem PC
gespeichert ist eine Mappe erst nach „Projektmappe speichern“.

Die Werkstatt und Bibliothek sind unabhängig von einem Projekt. Neue Mappen
beginnen leer und sammeln frei ausgewählte Elemente, auch mehrere Varianten
derselben Art. Neue Mappen verwenden Schema 2 mit stabiler Projektkennung;
mehrere gespeicherte Stände bleiben unter derselben Mappe. Bisherige Dateien
bleiben unverändert lesbar. Beim ausdrücklichen Speichern einer bisherigen
Mappe entsteht ein neuer Stand mit vollständig bewahrtem Ursprungsdatensatz.
Beim bloßen Öffnen findet keine automatische Datenmigration statt.
