# Verbindlicher Fragen-Steckbrief

Alle Fragen besitzen `id`, `question_type`, `prompt`, `answer`, `explanation`,
`source` und `subject_keys`. Die Quelle besitzt immer `status`, `verified_on`
und eine nicht leere Liste `references` mit `title` und einer HTTPS-`url`.

Auswahlfragen ergänzen `options`, Paarfragen `left` und `right`,
Reihenfolgefragen `items` und Schätzfragen `unit`. Diese vier Fragearten
besitzen außerdem immer `primary_category`, `subtopic` und `tags`. Die
Tags enthalten exakt `topics`, `entities`, `genres`, `regions` und `eras`.

Die vorbereitete Zwei-Gruppen-Zuordnung ergänzt `groups` mit den Bezeichnungen
`A` und `B` sowie genau sieben eindeutige `items`. `answer` ordnet jeden Begriff
`A`, `B` oder `both` zu; jede Runde verwendet alle drei Antwortarten mindestens
einmal. Auch diese Frageart besitzt die Themenfelder und den vollständigen
Quellen-Steckbrief.

Wahr-oder-falsch-Fragen enthalten bewusst keine Kategorien-, Unterthemen- oder
Tag-Felder. Das ist ihr einheitlicher Steckbrief und keine Ausnahme einzelner
Fragen.

## Ausgeschlossene Themen

Religionsfragen sind nicht Bestandteil von Guesstimate. Glaubenslehren,
heilige Schriften, religiöse Ämter, Riten, Feste und Bekenntnisse dürfen nicht
der Wissenskern einer Frage sein. Eine beiläufige Erwähnung in einer echten
Geografie-, Kunst- oder Geschichtsfrage ist nur zulässig, wenn die Auflösung
kein Religionswissen verlangt.

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
