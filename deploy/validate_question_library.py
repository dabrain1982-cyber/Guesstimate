"""Validate the complete question library before tests or deployment."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "fragen"
MANIFEST = json.loads((LIBRARY / "manifest.json").read_text(encoding="utf-8"))

TYPE_FIELDS = {
    "multiple_choice": {"options"},
    "true_false": set(),
    "match": {"left", "right"},
    "order": {"items"},
    "estimate": {"unit"},
    "binary_sort": {"groups", "items"},
}
PREFIXES = {
    "multiple_choice": "mc",
    "true_false": "tf",
    "match": "ma",
    "order": "or",
    "estimate": "es",
    "binary_sort": "bs",
}
COMMON_FIELDS = {"id", "question_type", "prompt", "answer", "explanation", "source"}
TOPIC_FIELDS = {"primary_category", "subtopic", "tags"}
CURRENT_FIELDS = COMMON_FIELDS | TOPIC_FIELDS | {"subject_keys"}
CURRENT_TRUE_FALSE_FIELDS = COMMON_FIELDS | {"subject_keys"}
TAG_FIELDS = {"topics", "entities", "genres", "regions", "eras"}
SOURCE_FIELDS = {"status", "verified_on", "references"}
FORBIDDEN_TRUE_FALSE_FIELDS = TOPIC_FIELDS | {"knowledge_category", "category", "topics"}
FORBIDDEN_RELIGION_CATEGORY = "faith_religion"


def _number(question_id: str) -> int:
    match = re.search(r"\d+", question_id)
    if not match:
        raise ValueError("enthält keine Nummer")
    return int(match.group())


def validate_library() -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    categories = set(MANIFEST["categories"])

    # Aktive Fragearten sind verpflichtend. Vorbereitete inaktive Fragearten
    # werden geprüft, sobald ihr Fragenpaket nicht mehr leer ist.
    for question_type in TYPE_FIELDS:
        definition = MANIFEST["question_types"][question_type]
        path = LIBRARY / definition["directory"] / "fragen.json"
        questions = json.loads(path.read_text(encoding="utf-8"))

        if not isinstance(questions, list):
            errors.append(f"{path}: keine Fragenliste")
            continue
        if not questions:
            if definition["active"]:
                errors.append(f"{path}: keine Fragenliste")
            continue

        for question in questions:
            question_id = str(question.get("id", "<ohne ID>"))
            prefix = f"{question_id}:"
            try:
                number = _number(question_id)
            except ValueError as exc:
                errors.append(f"{prefix} {exc}")
                continue

            if question_id in seen_ids:
                errors.append(f"{prefix} doppelte ID")
            seen_ids.add(question_id)
            if not question_id.startswith(PREFIXES[question_type]):
                errors.append(f"{prefix} falsches ID-Präfix")
            if question.get("question_type") != question_type:
                errors.append(f"{prefix} falsche oder fehlende Frageart")

            missing = (COMMON_FIELDS | TYPE_FIELDS[question_type]) - set(question)
            if missing:
                errors.append(f"{prefix} fehlende Pflichtfelder: {sorted(missing)}")

            prompt = question.get("prompt")
            if not isinstance(prompt, str) or not prompt.strip():
                errors.append(f"{prefix} leerer Fragetext")
            elif len(prompt) > 160:
                errors.append(f"{prefix} Fragetext ist mit {len(prompt)} Zeichen zu lang")
            if "erstmals vorgestellt oder patentiert" in str(prompt):
                errors.append(f"{prefix} unklare Sammelformulierung im Fragetext")

            if question_type == "true_false":
                forbidden = FORBIDDEN_TRUE_FALSE_FIELDS & set(question)
                if forbidden:
                    errors.append(f"{prefix} unzulässige Themenfelder: {sorted(forbidden)}")
                if not isinstance(question.get("answer"), bool):
                    errors.append(f"{prefix} Antwort muss true oder false sein")
            else:
                missing_topics = TOPIC_FIELDS - set(question)
                if missing_topics:
                    errors.append(f"{prefix} fehlende Themenfelder: {sorted(missing_topics)}")
                if question.get("primary_category") not in categories:
                    errors.append(f"{prefix} ungültige Themenkategorie")
                if question.get("primary_category") == FORBIDDEN_RELIGION_CATEGORY:
                    errors.append(f"{prefix} Religionsfragen sind ausgeschlossen")
                if not isinstance(question.get("subtopic"), str) or not question.get("subtopic"):
                    errors.append(f"{prefix} Unterthema fehlt")
                tags = question.get("tags")
                if not isinstance(tags, dict) or set(tags) != TAG_FIELDS:
                    errors.append(f"{prefix} Tags entsprechen nicht dem Steckbrief")

            # IDs ab 151 stammen aus dem aktuellen, quellengeprüften Bestand und
            # müssen exakt dem heutigen Steckbrief entsprechen.
            if number >= 151:
                expected = (
                    CURRENT_TRUE_FALSE_FIELDS
                    if question_type == "true_false"
                    else CURRENT_FIELDS
                ) | TYPE_FIELDS[question_type]
                if set(question) != expected:
                    errors.append(
                        f"{prefix} Steckbrief weicht ab; erwartet {sorted(expected)}, "
                        f"gefunden {sorted(question)}"
                    )
                subject_keys = question.get("subject_keys")
                if not isinstance(subject_keys, list) or not subject_keys:
                    errors.append(f"{prefix} subject_keys fehlen")
                elif any("faith_religion" in str(key) for key in subject_keys):
                    errors.append(f"{prefix} Religionsfragen sind ausgeschlossen")
                source = question.get("source")
                if not isinstance(source, dict) or set(source) != SOURCE_FIELDS:
                    errors.append(f"{prefix} Quellen-Steckbrief weicht ab")
                else:
                    if source.get("status") != "verified":
                        errors.append(f"{prefix} Quelle ist nicht als geprüft markiert")
                    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(source.get("verified_on", ""))):
                        errors.append(f"{prefix} Prüfdatum fehlt oder ist ungültig")
                    references = source.get("references")
                    if not isinstance(references, list) or not references:
                        errors.append(f"{prefix} Quellenreferenz fehlt")
                    else:
                        for reference in references:
                            if set(reference) != {"title", "url"}:
                                errors.append(f"{prefix} Quellenreferenz weicht ab")
                            if not str(reference.get("url", "")).startswith("https://"):
                                errors.append(f"{prefix} Quelle verwendet kein HTTPS")

            if question_type == "multiple_choice":
                options = question.get("options")
                if not isinstance(options, dict) or set(options) != {"A", "B", "C", "D"}:
                    errors.append(f"{prefix} Auswahloptionen müssen A bis D sein")
                elif question.get("answer") not in options:
                    errors.append(f"{prefix} Antwort verweist auf keine Auswahloption")
            elif question_type == "match":
                left = question.get("left")
                right = question.get("right")
                answer = question.get("answer")
                if not isinstance(left, list) or len(left) != 3 or len(set(left)) != 3:
                    errors.append(f"{prefix} linke Paarseite muss drei eindeutige Werte haben")
                if not isinstance(right, list) or len(right) != 3 or len(set(right)) != 3:
                    errors.append(f"{prefix} rechte Paarseite muss drei eindeutige Werte haben")
                if isinstance(left, list) and isinstance(right, list) and isinstance(answer, dict):
                    if set(answer) != set(left) or set(answer.values()) != set(right):
                        errors.append(f"{prefix} Paarlösung passt nicht zu den Auswahlwerten")
            elif question_type == "order":
                items = question.get("items")
                answer = question.get("answer")
                if not isinstance(items, list) or not isinstance(answer, list):
                    errors.append(f"{prefix} Reihenfolgewerte müssen Listen sein")
                elif len(items) < 3 or len(set(items)) != len(items) or set(items) != set(answer):
                    errors.append(f"{prefix} Reihenfolgelösung ist ungültig")
            elif question_type == "estimate":
                if not isinstance(question.get("answer"), (int, float)):
                    errors.append(f"{prefix} Schätzantwort muss numerisch sein")
                if not isinstance(question.get("unit"), str) or not question.get("unit"):
                    errors.append(f"{prefix} Einheit fehlt")
            elif question_type == "binary_sort":
                groups = question.get("groups")
                items = question.get("items")
                answer = question.get("answer")
                if (
                    not isinstance(groups, dict)
                    or set(groups) != {"A", "B"}
                    or not all(isinstance(value, str) and value for value in groups.values())
                ):
                    errors.append(f"{prefix} Gruppen müssen A und B benennen")
                if (
                    not isinstance(items, list)
                    or len(items) != 7
                    or len(set(items)) != 7
                    or not all(isinstance(item, str) and item for item in items)
                ):
                    errors.append(f"{prefix} Zuordnung benötigt sieben eindeutige Begriffe")
                if not isinstance(answer, dict) or not isinstance(items, list) or set(answer) != set(items):
                    errors.append(f"{prefix} Zuordnungslösung passt nicht zu den Begriffen")
                elif not set(answer.values()) <= {"A", "B", "both"}:
                    errors.append(f"{prefix} Zuordnung enthält einen ungültigen Gruppenwert")
                elif not {"A", "B", "both"} <= set(answer.values()):
                    errors.append(f"{prefix} Zuordnung muss A, B und Beides enthalten")

    return errors


def main() -> None:
    errors = validate_library()
    if errors:
        raise SystemExit("Fragenprüfung fehlgeschlagen:\n- " + "\n- ".join(errors))
    print("Fragenprüfung erfolgreich.")


if __name__ == "__main__":
    main()
