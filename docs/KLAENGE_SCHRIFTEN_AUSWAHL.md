# Kleine Auswahl: Schriftwirkung und Spielklänge

Stand: 27.10.2026. Kostenlos recherchiert, heruntergeladen und ausschließlich in
der lokalen Werkstatt aufgenommen. Eigene Bibliotheksbereiche **Schriften** und
**Klänge**; Varianten ansehen/probehören und Projekten zuordnen. Editoroptionen
und die Umstellung bestehender Spiele bleiben später.

## Passende Schrift und Oberfläche als Stil

| Stil | Schrift | Wirkung und Einsatz |
|---|---|---|
| Kreide auf Tafel | Cabin Sketch Bold | Raue gezeichnete Buchstaben auf dunkler Tafel; kurze Fragen und Überschriften |
| In Stein gemeißelt | Cinzel | An römische Inschriften angelehnte Formen mit passender vertiefter Darstellung auf Stein |
| In Eisen gestanzt | Stardos Stencil Bold | Kräftige Industrieschrift mit eingeprägter Wirkung auf Metall; kurze Pult-/Markenbeschriftung |
| Stempel & Schreibmaschine | Special Elite | Unregelmäßiger alter Farbauftrag auf Papier; Aufträge und Hinweise |
| Handschrift auf Papier | Kalam | Handschriftliche Notizen und kurze Kartentexte |
| Comic | Fredoka | Kräftige freundliche Titel und Spielaktionen |
| Klar & gut lesbar | Inter | Gemeinsame ruhige Grundschrift für Regeln, Fragen und Menüs |

Das sind sieben feste, bewusst passende Kombinationen. Eine freie Kombination
aller Schriften mit sämtlichen Effekten wird nicht erzeugt. Der Kreidecharakter
steckt in den rauen Glyphen der gewählten Schrift. Stein und Metall kombinieren
geeignete Schriftformen mit begrenzten Licht-/Schattenkanten und einer passenden
Oberfläche. Es sind visuelle 2D-Stile, keine gefrästen 3D-Schriftmodelle.
Die Oberflächen der Muster sind einfache lokale CSS-Darstellungen.

Die Schriftdateien kommen aus dem offiziellen [Google-Fonts-Repository](https://github.com/google/fonts).
Sechs Familien stehen unter SIL OFL 1.1; Special Elite unter Apache 2.0.
Unveränderte Fontdateien, Urheber-/Lizenztexte und Originalbeschreibungen liegen
unter `offline-preview/game-workshop-v1/assets/media/fonts/`. Downloadadressen,
Originalnamen, Git-Blob-Kennungen und SHA-256 stehen in `font-provenance.json`.
Alle sieben Schriften besitzen in der geprüften Datei ÄÖÜäöüß und die Ziffern 0–9.
Die Browser laden die Fonts ausschließlich vom lokalen Werkstattdienst.

Primärbeschreibungen: [Cabin Sketch](https://raw.githubusercontent.com/google/fonts/main/ofl/cabinsketch/DESCRIPTION.en_us.html),
[Cinzel](https://raw.githubusercontent.com/google/fonts/main/ofl/cinzel/DESCRIPTION.en_us.html),
[Stardos Stencil](https://raw.githubusercontent.com/google/fonts/main/ofl/stardosstencil/DESCRIPTION.en_us.html),
[Special Elite](https://raw.githubusercontent.com/google/fonts/main/apache/specialelite/DESCRIPTION.en_us.html).
Die Auswahl und Materialzuordnung sind unsere Gestaltungsentscheidung; die Quellen
belegen Herkunft, Schriftbeschreibung und Lizenz.

## Klänge nach Spielzweck

| Zweckgruppe | Aufgenommene Klangproben |
|---|---|
| Klicks & Bedienung | Klick, Bestätigen, Zurück, Nicht möglich, Timer-Tick |
| Tischaktionen | Karte bewegen, Karte ablegen, Karten mischen, Würfeln, Spielstein setzen |
| Spielereignisse | Rundenbeginn, Sieg, Niederlage |

13 kurze Klänge, von 0,023 bis 3,064 Sekunden. Rundenbeginn, Sieg und Niederlage
nutzen dieselbe Pizzicato-Klangfarbe; Sieg und Niederlage sind passende auf- bzw.
absteigende Folgen. Die Auswahl ist ein kleiner funktionaler Ausgangsbestand,
keine vollständige Musik-/Effektsammlung.

Alle Aufnahmen stammen unmittelbar aus Kenneys CC0-Paketen:
[Interface Sounds](https://kenney.nl/assets/interface-sounds),
[Casino Audio](https://kenney.nl/assets/casino-audio) und
[Music Jingles](https://kenney.nl/assets/music-jingles).
Originale OGG-Dateien und mitgelieferte CC0-Texte bleiben lokal erhalten.
Für die Werkstatt liegen zusätzlich Mono-WAVs mit angeglichenem Pegel und 5-ms-
Randblenden vor. Keine Tonhöhenänderung, Kürzung oder Neukomposition.
Die Hörprobe startet mit 45 % Wiedergabelautstärke. Probehören, Stopp und
Lautstärkeregler betreffen nur die Vorschau. Kein automatisches Abspielen oder
Zuordnen zu einem laufenden Spiel.

`sounds.json` nennt Originaldatei, Paket, Quelle, Lizenz, Prüfsummen, Dauer,
Pegeländerung und Wellenform. Die Qualitätsprüfung dekodiert die Dateien, prüft
Dauer/Pegel und begrenzt die abgeleiteten Spitzen auf maximal 0,65. Das ersetzt
keine persönliche klangliche Abnahme. Sämtliche 13 Proben wurden im Browser bis
zum Wiedergabeende geprüft; die Auswahl kann später nach Gehör weiter verfeinert
werden. Eine isolierte Prüfwerkzeugkopie des freien Miniaudio-Decoders liegt nur
unter `runtime/media-library-20261027/tools`, keine neue Spieleabhängigkeit.

## Erhaltung und Ausbau

Alte Buttonrezepte, bisherige Schrift-/Klangauswahl und persönliche Entwürfe
bleiben unverändert. Bestehende Spiele erhalten durch die neue Auswahl keine
neuen Fonts, Klänge oder Zuordnungen. Die beiden Zusatzfamilien Material und
Darstellung sowie bestehende Buttonparameter werden dadurch nicht neu gestaltet.
Die sieben Schriftstile und einzelne Klangproben können als unveränderte
Schnappschüsse in mehreren Projektmappen verwendet und lokal übergeben werden.

Maschinenlesbarer Bestand: [KLAENGE_SCHRIFTEN_AUSWAHL.json](KLAENGE_SCHRIFTEN_AUSWAHL.json),
erzeugt durch `python deploy/audit_media_library.py`.
Recherche-/Prüfbelege und Vorher-/Nachher-Vergleich:
`runtime/media-library-20261027/`. Seit 28.10.2026 ist die Auswahl auch im
Button-Editor ausdrücklich wählbar; weitere Baustein-Editoroptionen bleiben
offen. Siehe [BUTTON_MEDIEN_INTEGRATION.md](BUTTON_MEDIEN_INTEGRATION.md).

Abschlussprüfung: zwölf gezielte Medien-/Projektmappentests bestanden,
76,176 Sekunden. Sieben Schriftstile mit Umlauten/ß sowie alle 13 Klangproben im
Browser geprüft; Stopp, Lautstärke und Entfernen der laufenden Vorschau beim
Schließen kontrolliert. Getrennte Mappe mit Kreide, Metall und Siegklang nach
Neuladen wieder geöffnet und lokal übergeben. Persönliche Werkstatt auf Port 8776
mit derselben Ablage sichtbar geprüft. 536 geschützte Dateien unverändert,
einschließlich alter Buttonressourcen und sämtlicher sieben persönlicher JSONs.
