"""Audit record of the completed 449-question cell-quota rollback.

The stored daily rounds and party rounds contain complete question snapshots,
so historical result views remain intact. Usage fingerprints stay in SQLite and
continue preventing already played content from returning under another ID.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "fragen"
MANIFEST = json.loads((LIBRARY / "manifest.json").read_text(encoding="utf-8"))

# Highest IDs in the reviewed 903-question library before the quota expansion.
KEEP_THROUGH = {
    "true_false": 184,
    "multiple_choice": 184,
    "match": 182,
    "order": 175,
    "estimate": 178,
}
EXPECTED_REMOVED = {
    "true_false": 83,
    "multiple_choice": 90,
    "match": 90,
    "order": 96,
    "estimate": 90,
}


def number(question_id: str) -> int:
    match = re.search(r"\d+", question_id)
    if not match:
        raise RuntimeError(f"Ungültige Fragen-ID: {question_id}")
    return int(match.group())


def _retired_main() -> None:
    files: dict[Path, list[dict]] = {}
    removed = {question_type: 0 for question_type in KEEP_THROUGH}
    kept_total = 0

    for question_type, limit in KEEP_THROUGH.items():
        type_dir = MANIFEST["question_types"][question_type]["directory"]
        for category in MANIFEST["categories"].values():
            path = LIBRARY / type_dir / category["directory"] / "fragen.json"
            questions = json.loads(path.read_text(encoding="utf-8"))
            kept = []
            for question in questions:
                if number(question["id"]) <= limit:
                    kept.append(question)
                else:
                    removed[question_type] += 1
            files[path] = kept
            kept_total += len(kept)

    if removed != EXPECTED_REMOVED:
        raise RuntimeError(f"Unerwartete Entfernungsverteilung: {removed}")
    if kept_total != 903:
        raise RuntimeError(f"Erwartet: 903 verbleibende Fragen, erhalten: {kept_total}")

    print(json.dumps({"removed": removed, "remaining": kept_total}, indent=2))
    if "--apply" not in sys.argv:
        print("Trockenlauf: keine Dateien geändert.")
        return

    for path, questions in files.items():
        path.write_text(
            json.dumps(questions, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print("449 Quotenfragen deaktiviert; 903 geprüfte Fragen bleiben aktiv.")


def main() -> None:
    raise SystemExit(
        "Bereits abgeschlossen: Die Bibliothek verwendet inzwischen das flache Schema 2."
    )


if __name__ == "__main__":
    main()
