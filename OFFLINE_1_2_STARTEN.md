# Version1.2 offline vorbereiten und starten

Die erweiterte Version1.1 wird als neuer überprüfter Snapshot gesichert.
Ältere1.1-Archive bleiben erhalten; `releases/1.1.json` nennt die neueste
Sicherung und die Vorgänger. Private PC-Spielstände bleiben getrennt vom
Codearchiv und werden nicht auf einen öffentlichen Server übertragen.

Die neue Arbeitskopie entsteht unter `D:\Guesstimate\offline-versions\1.2`.
Sie enthält eine überprüfte Kopie des1.1-Programms und eine eigene Kopie des
normalen lokalen Spielstands aus dessen Sicherung. Eine vorhandene getrennte
Conquest-Vorschau wird ebenfalls kopiert. Konten und Spielstände der Basis
werden dabei nicht verändert. Installierte Bibliotheken werden vom selben PC
mitbenutzt; neue Programm- und Designänderungen bleiben in der eigenen Kopie.

Starten: `D:\Guesstimate\Version-1.2-starten.cmd` doppelklicken.
Adresse: <http://127.0.0.1:8784/>. Die Browsertitel zeigen „offline1.2“.
Die Anmeldung ist durch einen eigenen Sitzungsschlüssel und Cookienamen von
Version1.1 auf Port8765 getrennt. Mit dem kopierten vorhandenen Konto selbst
anmelden; die PIN bleibt die bisherige. Sie wird bei der Vorbereitung nicht
ausgelesen oder neu gesetzt.

Das Startfenster offenlassen. Schließen bzw. Strg+C beendet den damit
gestarteten1.2-Dienst; eine bereits laufende passende Instanz wird wiederverwendet.
Andere Programme und Version1.1 werden nicht beendet.

`releases/1.2.json` nennt Basis, Arbeitsordner, Datenkopien und Port.
Version1.2 ist ein neuer lokaler Arbeitsstand, keine veröffentlichte Version.
Neue Entwicklungsarbeit dafür gehört in `offline-versions/1.2`.
Die neue Ranglisten-/Flyer-Ergänzung gehört noch zur gesicherten1.1.
