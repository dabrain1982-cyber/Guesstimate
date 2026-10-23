"""Load the physical, question-type-first question library."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


# The JSON library is loaded at process start; changing this module also gives
# the live Gunicorn reloader a deterministic signal after question rollouts.
QUESTION_LIBRARY_ROOT = Path(__file__).resolve().parent / "fragen"
MANIFEST_PATH = QUESTION_LIBRARY_ROOT / "manifest.json"


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"Fragen-Datei fehlt: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Ungültiges JSON in {path}: {exc}") from exc


QUESTION_LIBRARY_MANIFEST = _read_json(MANIFEST_PATH)
if QUESTION_LIBRARY_MANIFEST.get("schema_version") != 2:
    raise RuntimeError("Die Version der Fragenablage wird nicht unterstützt")

QUESTION_TYPE_DEFINITIONS = QUESTION_LIBRARY_MANIFEST["question_types"]
KNOWLEDGE_CATEGORY_DEFINITIONS = QUESTION_LIBRARY_MANIFEST["categories"]

KNOWLEDGE_CATEGORY_LABELS = {
    key: definition["label"]
    for key, definition in KNOWLEDGE_CATEGORY_DEFINITIONS.items()
}

CATEGORY_LABELS = {
    key: definition["label"]
    for key, definition in QUESTION_TYPE_DEFINITIONS.items()
    if definition["active"]
}

CATEGORY_ORDER = QUESTION_LIBRARY_MANIFEST["round_order"]
if set(CATEGORY_ORDER) != set(CATEGORY_LABELS):
    raise RuntimeError("Aktive Fragearten und Rundenreihenfolge widersprechen sich")


def _id_sort_key(question: dict[str, Any]) -> tuple[str, int]:
    question_id = str(question.get("id", ""))
    match = re.search(r"\d+", question_id)
    return (
        question_id[: match.start()] if match else question_id,
        int(match.group()) if match else 0,
    )


def _load_question_bank() -> dict[str, list[dict[str, Any]]]:
    bank: dict[str, list[dict[str, Any]]] = {
        question_type: [] for question_type in CATEGORY_ORDER
    }
    seen_ids: set[str] = set()

    for question_type in CATEGORY_ORDER:
        type_definition = QUESTION_TYPE_DEFINITIONS[question_type]
        path = QUESTION_LIBRARY_ROOT / type_definition["directory"] / "fragen.json"
        questions = _read_json(path)
        if not isinstance(questions, list):
            raise RuntimeError(f"{path} muss eine Liste von Fragen enthalten")

        for stored in questions:
            if not isinstance(stored, dict):
                raise RuntimeError(f"Ungültiger Eintrag in {path}")
            question = dict(stored)
            question_id = question.get("id")
            if not question_id or question_id in seen_ids:
                raise RuntimeError(f"Fehlende oder doppelte Fragen-ID: {question_id}")
            if question.get("question_type") != question_type:
                raise RuntimeError(f"Falsche Frageart bei {question_id} in {path}")
            for required in ("prompt", "answer", "explanation", "source"):
                if required not in question:
                    raise RuntimeError(f"{question_id} fehlt das Feld {required}")
            if question_type == "true_false":
                if any(
                    field in question
                    for field in ("primary_category", "category", "subtopic", "topics", "tags")
                ):
                    raise RuntimeError(
                        f"Wahr-oder-unwahr-Frage {question_id} enthält Kategorienfelder"
                    )
            else:
                for required in ("primary_category", "subtopic", "tags"):
                    if required not in question:
                        raise RuntimeError(
                            f"{question_id} fehlt das Steckbrief-Feld {required}"
                        )
                if question["primary_category"] not in KNOWLEDGE_CATEGORY_DEFINITIONS:
                    raise RuntimeError(
                        f"Unbekannte Themenkategorie bei {question_id}"
                    )

            # Runtime compatibility: the game calls the question type "category".
            question["category"] = question_type
            knowledge_category = question.get("primary_category")
            if knowledge_category:
                question["knowledge_category"] = knowledge_category
            bank[question_type].append(question)
            seen_ids.add(question_id)

        bank[question_type].sort(key=_id_sort_key)

    return bank


QUESTION_BANK = _load_question_bank()
