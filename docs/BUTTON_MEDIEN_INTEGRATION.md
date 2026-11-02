# Schriftstile und kurze Klänge im Button-Editor

## Cinzel für Black Jack · 29.10.2026

Unter **Text & Schrift → Schriftart → Spielschriften** ist **Cinzel · Black Jack**
wählbar. Dieselbe bereits lokal vorhandene variable Schrift wird für den
freigegebenen Blackjack-Flyer verwendet. Die vorhandene Kennung `cinzel`,
Fontdatei und gemeinsame Darstellung bleiben erhalten. Die Schriftwahl lässt
sich unabhängig von Fläche und Schriftfarbe auf jeden eigenen Button anwenden.
Für Black Jack wird der neueste persönliche Buttonstand als neuer Folgestand
mit Cinzel gespeichert; frühere Entwürfe bleiben erhalten.

## Ergänzung: getrennte Schriftwahl vom 28.10.2026

Der Nutzer hat die bisherige Kopplung von Schriftwirkung und Fläche für die neue Bearbeitung ausdrücklich ersetzt: zuerst Form und Fläche/Farbe, danach Schrift und Schriftfarbe. Die sieben neuen `letter-*`-Wahlen nutzen dieselben lokalen Schriften und passenden Wirkungen ausschließlich für die Beschriftung. Die bisherigen `media-*`-Kennungen bleiben unverändert lesbar und sehen ohne Bearbeitung weiterhin gleich aus. Ein übernommener gekoppelter Stil wird erklärt und lässt sich ausdrücklich trennen; seine Grundfarbe wird dann als eigene Farbfläche übernommen. Klangwahl und Klangengine unverändert. Der folgende ursprüngliche Bericht beschreibt die vorherige Integration der gekoppelten Stile.

Stand: 28.10.2026, ausschließlich lokal.

Die sieben recherchierten Schriftstile sind unter **Schrift & Wirkung → Schrift
oder Schriftstil** wählbar: Kreide auf Tafel, in Stein gemeißelt, in Eisen
gestanzt, Stempel/Schreibmaschine, Handschrift auf Papier, Comic und Klar.
Jeder Stil verwendet seine passende Schrift, Wirkung und Fläche aus der
bestehenden Medienbibliothek. Form, Beschriftung, Größe und Bewegung bleiben
eigene Einstellungen. Bild- und reine Symbolbuttons erhalten keine
unpassende Textbeschichtung.

Bei einem festen Stil werden die dort nicht wirksamen freien Material- und
Schriftwirkungen verborgen. Ihre bisherigen Werte bleiben erhalten. Die Wahl
einer bisherigen Schrift gibt sie wieder frei und stellt auch die bisherige
Originalfläche wieder her, sofern sie zuvor erhalten war.

Unter **Klang → Buttonklang** stehen die 13 kurzen Werkstattklänge sowie
**Ohne Ton** bereit. Die Hörbeispiele lassen sich direkt auswählen, stoppen und
in der Lautstärke ändern. Neue Proben werden vollständig gespielt;
Loslassen löst keinen zweiten Anschlag aus. Die bisherigen Klangkandidaten
bleiben mit ihren unveränderten Kennungen und Ausschnitten verfügbar.

## Wiederverwendung und Erhaltung

Keine neue Schrift-/Effektmatrix und keine neue Klangerzeugung. Die
Schriftoberflächen werden aus `media-stage.css` proportional abgeleitet;
Font- und WAV-Verweise nutzen die vorhandenen lokalen Dateien. Herkunft und
freie Lizenzen bleiben in der Medienbibliothek dokumentiert. Der gemeinsame
Buttonrenderer und die bisherige Klangengine bleiben unverändert. Eine
Werkstatt-Erweiterung ergänzt ausschließlich ausdrücklich gewählte neue Werte.
Editor, gespeicherte Bibliotheksvorschauen und Detailansichten verwenden
dieselbe Erweiterung. Spiele verwenden weiter ihren bisherigen Renderer.

Bestehende Font-/Klangkennungen, Standardwerte und alle 144 ursprünglichen
Buttonrezepte bleiben gleich. Kein neues Pflichtfeld, keine Migration und
keine automatische Zuordnung. Persönliche Entwürfe, Projektmappen, Fragenbanken
und Spiele werden nicht geändert. Neue Einstellungen lassen sich als eigener
Entwurf speichern und unverändert in einer Projektmappe sammeln/übergeben.

## Prüfungen

- Alle sieben konkreten Fonts im Browser geladen und an derselben ursprünglichen
  Buttonform gezeigt; Beschriftung und Maße bleiben erhalten.
- Alle 13 Klänge am Testbutton ausgelöst; Stopp, Lautstärke 0 und Auswahl aus
  der Hörgalerie geprüft. Lokale WAVs laden ohne Dekodierfehler. Die vollständigen
  Clipdauern und nur ein Anschlag werden zusätzlich an der unveränderten
  Klangengine geprüft. Das ist keine persönliche klangliche Abnahme.
- Speichern und erneutes Öffnen eines Kreide-/Klickentwurfs über die gemeinsame
  Bibliothek und den eingebetteten Editor in einer getrennten Testablage.
  Nach Neuladen der Prüfmappe lokal übergeben; Schnappschuss ist exakt gleich
  dem gespeicherten Rezept (`media-chalk`, `media-click`, Lautstärke 30).
  Übergabe: `runtime/button-media-20261028/qa-library/handoffs/handoff-c3fc359be07045fc8bfd67a4b27cd7e4.json`.
- Sieben Stile und alle 13 Klangkennungen validiert; sieben gespeicherte
  Varianten einschließlich unveränderter Herkunft und Einstellungen übergeben.
- Zwölf bestehende Buttonprüfungen und vier neue Medienprüfungen bestanden;
  zusätzlich gezielte Quell-/Übergabeprüfungen und Node-Klang-/Geometrieprüfungen.
  Keine vollständige Abnahme aller 85 Modelle oder anderer Baustein-Editoren.

Persönliche Werkstatt auf Port 8776 mit gleicher Ablage neu geladen und die neue
Auswahl dort sichtbar geprüft. Screenshot: `runtime/button-media-20261028/editor-personal.png`.
Keine Prüfung dort gespeichert. Alle 647 geschützten Ausgangsdateien und die
sieben persönlichen JSON-Dateien sind unverändert; keine zusätzlichen
persönlichen JSONs. Der eigene getrennte Prüfprozess auf Port 8777 wurde beendet.

Beim frühen Wechsel zu Iframe-Vorschauen enthielt das Browserprotokoll
MutationObserver-Meldungen ohne Quelldatei; ihre Herkunft ist nicht geklärt.
Speichern, Wiederöffnen und Übergabe funktionierten. In der abschließend neu
geladenen persönlichen Editoransicht kamen keine neuen Warnungen/Fehler hinzu.

Bestand und Quellenprüfsummen: [BUTTON_MEDIEN_INTEGRATION.json](BUTTON_MEDIEN_INTEGRATION.json),
erzeugt mit `python deploy/audit_button_media.py`. Browsernachweise und
Vorher-/Nachher-Schutzvergleich: `runtime/button-media-20261028/`.
