"""One-time migration to a flat, question-type-first library (schema v2).

The v1 library nested every question type below a mandatory knowledge category.
Schema v2 stores one JSON list per question type. True/false questions carry no
category taxonomy at all; other formats retain their existing descriptive
metadata until their own format is reviewed separately.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "fragen"
TEMP_LIBRARY = ROOT / "fragen.__schema_v2_tmp__"

NEW_DIRECTORIES = {
    "true_false": "wahroderunwahr",
    "multiple_choice": "multiplechoice",
    "match": "paarebilden",
    "order": "reihenfolge",
    "estimate": "schaetzung",
    "word_scramble": "buchstabensalat",
    "binary_sort": "zweigruppenzuordnen",
}

EXPECTED_COUNTS = {
    "true_false": 184,
    "multiple_choice": 184,
    "match": 182,
    "order": 175,
    "estimate": 178,
    "word_scramble": 0,
    "binary_sort": 0,
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    manifest_path = LIBRARY / "manifest.json"
    manifest = read_json(manifest_path)
    if manifest.get("schema_version") != 1:
        raise SystemExit("Die Ausgangsbibliothek ist nicht im erwarteten Schema 1.")

    flattened: dict[str, list[dict]] = {}
    seen_ids: set[str] = set()
    for question_type, definition in manifest["question_types"].items():
        questions: list[dict] = []
        for category in manifest["categories"].values():
            path = (
                LIBRARY
                / definition["directory"]
                / category["directory"]
                / "fragen.json"
            )
            stored = read_json(path)
            if not isinstance(stored, list):
                raise RuntimeError(f"Keine Fragenliste: {path}")
            for original in stored:
                question = dict(original)
                question_id = question.get("id")
                if not question_id or question_id in seen_ids:
                    raise RuntimeError(f"Fehlende oder doppelte ID: {question_id}")
                if question.get("question_type") != question_type:
                    raise RuntimeError(f"Falsche Frageart bei {question_id}")
                if question_type == "true_false":
                    question.pop("primary_category", None)
                    question.pop("subtopic", None)
                    question.pop("tags", None)
                questions.append(question)
                seen_ids.add(question_id)
        questions.sort(key=lambda item: int("".join(filter(str.isdigit, item["id"]))))
        flattened[question_type] = questions

    counts = {key: len(value) for key, value in flattened.items()}
    if counts != EXPECTED_COUNTS:
        raise RuntimeError(f"Unerwartete Fragenzahlen: {counts}")
    if any(
        forbidden in question
        for question in flattened["true_false"]
        for forbidden in ("primary_category", "category", "subtopic", "topics", "tags")
    ):
        raise RuntimeError("Eine Wahr-oder-unwahr-Frage enthält noch Kategorienfelder.")

    updated_manifest = dict(manifest)
    updated_manifest["schema_version"] = 2
    updated_manifest["storage_order"] = ["question_type"]
    updated_manifest["taxonomy"] = {
        "mode": "optional_metadata",
        "forbidden_for_question_types": ["true_false"],
        "production_quotas": False,
    }
    updated_manifest["question_types"] = {
        key: {**definition, "directory": NEW_DIRECTORIES[key]}
        for key, definition in manifest["question_types"].items()
    }

    if "--apply" not in sys.argv:
        print(json.dumps(counts, ensure_ascii=False, indent=2))
        print("Trockenlauf: keine Dateien geändert.")
        return

    if TEMP_LIBRARY.exists():
        shutil.rmtree(TEMP_LIBRARY)
    TEMP_LIBRARY.mkdir()
    (TEMP_LIBRARY / "manifest.json").write_text(
        json.dumps(updated_manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    for question_type, questions in flattened.items():
        target = TEMP_LIBRARY / NEW_DIRECTORIES[question_type]
        target.mkdir()
        (target / "fragen.json").write_text(
            json.dumps(questions, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    shutil.rmtree(LIBRARY)
    TEMP_LIBRARY.rename(LIBRARY)
    print("Fragenbibliothek auf Schema 2 und flache Frageart-Ordner umgestellt.")
    print(json.dumps(counts, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
