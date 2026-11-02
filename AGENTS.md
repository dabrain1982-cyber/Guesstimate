# Verbindliche Projektanweisung für Codex

Dieses Repository ist ausschließlich das Projekt **Stormseed´s Guesstimate**.
Der maßgebliche Arbeits- und Live-Ordner ist `/srv/guesstimate`. Leite die
Projektzugehörigkeit niemals nur aus dem Chat-Titel oder der Seitenleiste ab.

## Vor jeder Arbeit

1. Lies `/srv/guesstimate/PROJEKTLOG.md` vollständig.
2. Lies die für den Auftrag maßgeblichen Projektdateien. Für Fragenarbeit sind
   dies mindestens `fragen/STECKBRIEF.md`, `fragen/manifest.json`, `questions.py`
   und die betroffenen `fragen/*/fragen.json`.
3. Prüfe den aktuellen Arbeitsstand und bewahre vorhandene Änderungen anderer
   Arbeiten. Überschreibe oder entferne sie nicht eigenmächtig.
4. Verwende den aktuellen Datei- und Live-Zustand als Beleg. Frühere Chats und
   das Projektlog liefern Kontext, ersetzen aber keine aktuelle Prüfung.

## Fragenredaktion

- **Keine Religionsfragen.** Religion, Glaubenslehren, heilige Schriften,
  religiöse Ämter, Riten, Feste und Bekenntnisse sind als Fragethema dauerhaft
  ausgeschlossen. Eine beiläufige Erwähnung in einer echten Geografie-, Kunst-
  oder Geschichtsfrage macht diese nicht automatisch zur Religionsfrage; der
  geprüfte Wissenskern darf aber nicht religiös sein.
- Prüfe neue Fragen des Daily Quiz gegen den gesamten Bestand aller dortigen
  Fragearten auf denselben Sachverhalt, bloße Umformulierungen und starke
  inhaltliche Überschneidungen. Bei Stormseed´s Perfect gilt die
  Dublettenprüfung getrennt je Kategorie: Eine Begriffskarte schließt nur eine
  weitere Begriffskarte aus, eine Kuriosität nur eine weitere Kuriosität.
  Überschneidungen mit dem Daily Quiz oder der jeweils anderen Perfect-Kategorie
  sind zulässig, sofern die neue Karte für ihr eigenes Spielformat geeignet ist.
- Recherchiere jeden neuen Sachverhalt tatsächlich. Setze eine Quelle nur dann
  auf `verified`, wenn sie den Inhalt und die Auflösung belegt.
- Bevorzuge Primärquellen, zuständige Institutionen, Universitäten, Museen und
  anerkannte Fachquellen. Erfinde keine Fakten, Titel oder URLs.
- Halte den verbindlichen Steckbrief, das aktuelle JSON-Schema und die
  vorhandene ID-Systematik ein. Bestehende Fragen und IDs bleiben unverändert.
- Formuliere für neugierige Erwachsene verständlich, fair und mit erkennbarem
  Erkenntnis- oder Gesprächswert. Vermeide Kinderfragen, belanglose Details,
  Fangfragen und unnötiges Spezialwissen.
- Kategorien sind Metadaten. Gute Themenmischung ist erwünscht, aber Qualität,
  Eindeutigkeit und Dublettenfreiheit gehen vor rechnerischen Quoten.
- Vor jeder Live-Aktivierung muss
  `python3 deploy/validate_question_library.py` erfolgreich laufen. Danach sind
  die relevanten Tests und der öffentliche Live-Status zu prüfen.
- Neue Fragen im Live-Ordner gelten automatisch als unverbraucht, solange ihre
  ID bzw. ihr Inhaltsfingerabdruck nicht in `question_usage` steht.

## Projektlog

Aktualisiere `PROJEKTLOG.md`, wenn eine Änderung den späteren Arbeitsstand,
offene Aufgaben, wichtige Entscheidungen oder die nachgewiesene Live-Situation
verändert. Das Log ist keine Abschrift des Chats und kein Platz für interne
Gedankengänge. Notiere nur überprüfbare Ergebnisse, relevante Entscheidungen,
offene Punkte und ausgeführte Prüfungen.

## Widersprüche und Oberflächenpflege

- Vergleiche jede neue Gestaltungsanforderung vor der Umsetzung mit den
  verbindlichen Entscheidungen im Projektlog und dem aktuellen Programmcode.
  Widerspricht sie einer früheren Entscheidung, benenne den konkreten
  Widerspruch sofort und lasse den Nutzer entscheiden, welche Vorgabe künftig
  gelten soll. Setze nicht beide Varianten gleichzeitig um und entscheide
  nicht stillschweigend.
- Sichtbare Komponenten besitzen genau eine verbindliche Grundimplementierung.
  Wiederverwendungen müssen dieselbe Komponente nutzen und dürfen sie nur als
  Ganzes proportional skalieren. Seitenabhängige Kopien der Innenkomposition
  sind unzulässig, sofern der Nutzer sie nicht ausdrücklich verlangt.
- Behebe CSS-Probleme nicht durch immer neue Korrekturblöcke am Dateiende.
  Ermittle die tatsächlich wirksamen Regeln, konsolidiere sie an der
  zuständigen Komponente und entferne vollständig ersetzte oder
  widersprüchliche Altregeln. Responsive Regeln dürfen eine Komponente an den
  verfügbaren Platz anpassen, aber keine zweite unabhängige Gestaltung bilden.
- Bei einem Live-Auftrag bedeutet **getan**, dass das verlangte Ergebnis im
  laufenden Spiel tatsächlich sichtbar und funktionsfähig geprüft wurde.
  Gespeicherter Code, bestandene Tests oder öffentlich erreichbare Dateien
  allein gelten nicht als Erledigung. Solange die Live-Prüfung fehlt oder das
  Ergebnis abweicht, lautet der Status **nicht getan**.

## Sicherheit und Veröffentlichung

- `/srv/guesstimate` ist zugleich der vom laufenden Dienst verwendete Bestand.
  Änderungen an aktiven Fragen-Dateien können damit unmittelbar live wirken.
- Verändere keine Spielergebnisse, Konten, Nutzungshistorie oder Zugangsdaten,
  sofern der Nutzer dies nicht ausdrücklich verlangt.
- Behaupte keine erfolgreiche Aktivierung oder Prüfung, bevor sie tatsächlich
  beobachtet wurde.

