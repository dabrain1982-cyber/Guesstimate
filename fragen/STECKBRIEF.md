# Verbindlicher Fragen-Steckbrief

Alle Fragen besitzen `id`, `question_type`, `prompt`, `answer`, `explanation`,
`source` und `subject_keys`. Die Quelle besitzt immer `status`, `verified_on`
und eine nicht leere Liste `references` mit `title` und einer HTTPS-`url`.

Auswahlfragen ergänzen `options`, Paarfragen `left` und `right`,
Reihenfolgefragen `items` und Schätzfragen `unit`. Diese vier Fragearten
besitzen außerdem immer `primary_category`, `subtopic` und `tags`. Die
Tags enthalten exakt `topics`, `entities`, `genres`, `regions` und `eras`.

Wahr-oder-falsch-Fragen enthalten bewusst keine Kategorien-, Unterthemen- oder
Tag-Felder. Das ist ihr einheitlicher Steckbrief und keine Ausnahme einzelner
Fragen.

## Sprache

- Der Fragetext muss beim ersten Vorlesen verständlich sein.
- Ein Satz prüft nur einen Gedanken.
- Geläufige Wörter sind Fachsprache und Verwaltungssprache vorzuziehen.
- Notwendige Fachbegriffe werden im Satz kurz verständlich gemacht.
- Nebensätze, Passivketten, doppelte Verneinungen und austauschbare
  Sammelformulierungen werden vermieden.
- Der Fragetext bleibt in der Regel unter 160 Zeichen. Eine längere Erklärung
  gehört in `explanation`, nicht in die Frage.

Schwerfällig: Bei einem präparierten Klavier verändern Gegenstände zwischen
oder auf den Saiten den Klang.

Klar: Bei einem „präparierten Klavier“ verändern Schrauben, Filz oder andere
Gegenstände an den Saiten den Klang.

Vor dem Speichern und vor jeder Veröffentlichung ist auszuführen:

```bash
python3 deploy/validate_question_library.py
```
