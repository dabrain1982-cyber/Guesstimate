# Stormseed´s perfekt – eigenständige Kartenablage

Dieser Ordner ist für ein künftiges, eigenständiges Spiel vorbereitet. Er ist
absichtlich nicht in `fragen/manifest.json` eingetragen und wird vom laufenden
Guesstimate-Spiel nicht geladen.

## Bestände

- `begriffe/fragen.json`: 355 recherchierte Begriffskarten
- `kuriositaeten/fragen.json`: 12 neu recherchierte Kuriositätenkarten

Beide Dateien enthalten ein JSON-Array. Jedes Objekt in diesem Array ist genau
eine einzeln ziehbare Karte mit einer dauerhaften, eindeutigen `id`.

## Kartenfelder

Begriffskarten enthalten `id`, `card_type`, `term`, `prompt`, `answer` und
`source`. Jede Definition wurde einzeln anhand der jeweils verlinkten
Lexikon-, Wörterbuch- oder Fachquelle geprüft. Offensichtliche Alltags- und
gewöhnliche Fachbegriffe sind ausgeschlossen.

Kuriositätenkarten enthalten `id`, `card_type`, `prompt`, `answer`,
`explanation` und `source`. Sie wurden eigens als offene, blufftaugliche
Warum-, Wozu- oder Was-geschah-Fragen recherchiert. Sie sind keine Kopien aus
dem normalen Quizbestand und enthalten keine Schätzfragen.

Der spätere Spielmodus kann eine Karte ziehen, indem er ein einzelnes Objekt
aus dem jeweiligen Array auswählt. Eine Gruppierung mehrerer Aufgaben zu einer
physischen Vorder- oder Rückseite gibt es bewusst nicht.
