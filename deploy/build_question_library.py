"""Retired schema-v1 migration, kept only as an audit record."""

from __future__ import annotations

import json
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIBRARY_ROOT = ROOT / "fragen"
sys.path.insert(0, str(ROOT))

from legacy_questions import QUESTION_BANK

CATEGORIES = {
    "gaming": ("Gaming", "gaming"),
    "faith_religion": ("Glaube & Religion", "glaube-religion"),
    "music": ("Musik", "musik"),
    "sport": ("Sport", "sport"),
    "witnesses_of_time": ("Zeugen der Zeit", "zeugen-der-zeit"),
    "media_entertainment": ("Medien & Unterhaltung", "medien-unterhaltung"),
    "plants_animals": ("Pflanzen & Tiere", "pflanzen-tiere"),
    "geography_world": ("Geografie & Welt", "geografie-welt"),
    "science_technology": ("Wissenschaft & Technik", "wissenschaft-technik"),
    "human_everyday": ("Mensch & Alltag", "mensch-alltag"),
}

QUESTION_TYPES = {
    "multiple_choice": ("Auswahl", "auswahl", True),
    "true_false": ("Wahr oder falsch", "wahr-falsch", True),
    "match": ("Paare bilden", "paare-bilden", True),
    "order": ("Reihenfolge", "reihenfolge", True),
    "estimate": ("Schätzung", "schaetzung", True),
    "word_scramble": ("Buchstabensalat", "buchstabensalat", False),
    "binary_sort": ("Zwei Gruppen zuordnen", "zwei-gruppen-zuordnen", False),
}

# The original 40 hand-authored questions per type require an explicit primary topic.
BASE = {
    "multiple_choice": {
        "witnesses_of_time": [1],
        "geography_world": [2, 6, 10, 15, 18, 20, 21, 31, 34, 36, 39],
        "human_everyday": [3, 7, 19, 22, 27, 32],
        "plants_animals": [4, 14, 23, 29, 35, 40],
        "science_technology": [5, 9, 11, 12, 13, 16, 17, 25, 26, 30, 37, 38],
        "music": [8, 33],
        "media_entertainment": [24, 28],
    },
    "true_false": {
        "plants_animals": [1, 3, 6, 8, 11, 13, 15, 18, 19, 21, 24, 29, 32, 35, 38],
        "science_technology": [2, 7, 9, 10, 20, 23, 28, 31, 37, 39, 40],
        "witnesses_of_time": [4, 16, 27, 33],
        "human_everyday": [5, 25, 30, 34],
        "media_entertainment": [12],
        "geography_world": [14, 22, 26, 36],
        "gaming": [17],
    },
    "estimate": {
        "human_everyday": [1, 7, 12, 14, 17, 19, 22, 26, 28, 38],
        "geography_world": [2, 6, 11, 18, 21, 27, 31, 34, 37, 39],
        "music": [3, 30],
        "science_technology": [4, 8, 9, 10, 15, 20, 25, 29],
        "sport": [5, 13, 32, 36, 40],
        "media_entertainment": [16],
        "plants_animals": [23, 33, 35],
        "witnesses_of_time": [24],
    },
    "order": {
        "science_technology": [1, 4, 5, 13, 24, 26, 29, 32, 39],
        "geography_world": [2, 6, 7, 11, 15, 18, 21, 27, 31, 33, 35, 40],
        "media_entertainment": [3, 12, 19],
        "witnesses_of_time": [8, 10, 25, 30, 36],
        "plants_animals": [9, 22, 28, 34],
        "human_everyday": [14, 17, 20, 37, 38],
        "gaming": [16],
        "music": [23],
    },
    "match": {
        "witnesses_of_time": [1, 34],
        "human_everyday": [2, 4, 13, 19, 29, 35, 39],
        "media_entertainment": [3, 7, 9, 14, 32],
        "geography_world": [6, 17, 22, 25, 28, 31],
        "plants_animals": [5, 23, 38],
        "science_technology": [8, 10, 11, 12, 16, 18, 20, 21, 26, 30, 33, 37, 40],
        "sport": [15, 27],
        "music": [24, 36],
    },
}

BASE_LOOKUP = {
    (question_type, number): category
    for question_type, groups in BASE.items()
    for category, numbers in groups.items()
    for number in numbers
}

GENERATED_PAIR_SUBTOPICS = [
    "Hauptstädte",
    "Chemie",
    "Literatur",
    "Bildende Kunst",
    "Physik und Maßeinheiten",
    "Wahrzeichen",
    "Essen und Herkunft",
    "Erfindungen und Entwicklungen",
    "Forschungsgebiete",
    "Tierwelt",
]

GENERATED_FACT_SUBTOPICS = [
    "Historische Ereignisse",
    "Bauwerke",
    "Flüsse",
    "Länderflächen",
    "Tiergeschwindigkeiten",
    "Entfernungen",
    "Schmelzpunkte",
    "Erfindungsgeschichte",
    "Literaturgeschichte",
    "Sportdistanzen",
]

DEFAULT_SUBTOPICS = {
    "gaming": "Gaming allgemein",
    "faith_religion": "Glaube und Religion allgemein",
    "music": "Musik allgemein",
    "sport": "Sport allgemein",
    "witnesses_of_time": "Geschichte allgemein",
    "media_entertainment": "Medien und Unterhaltung allgemein",
    "plants_animals": "Pflanzen und Tiere allgemein",
    "geography_world": "Geografie und Welt allgemein",
    "science_technology": "Wissenschaft und Technik allgemein",
    "human_everyday": "Mensch und Alltag allgemein",
}


def number_of(question: dict) -> int:
    return int(re.search(r"\d+", question["id"]).group())


def primary_category(question_type: str, question: dict) -> str:
    number = number_of(question)
    if number <= 40:
        return BASE_LOOKUP[(question_type, number)]

    if number >= 141:
        overrides = {
            "multiple_choice": {146: "gaming", 147: "music"},
            "true_false": {143: "music", 145: "gaming", 148: "gaming"},
            "match": {143: "gaming", 144: "music", 148: "music"},
            "order": {143: "gaming", 145: "music", 148: "gaming"},
        }
        return overrides.get(question_type, {}).get(number, "media_entertainment")

    group = (number - 41) // 10
    if question_type in {"multiple_choice", "true_false", "match"}:
        fixed = {
            0: "geography_world",
            1: "science_technology",
            2: "media_entertainment",
            3: "media_entertainment",
            4: "science_technology",
            5: "geography_world",
            6: "human_everyday",
            7: "witnesses_of_time",
            9: "plants_animals",
        }
        if group in fixed:
            return fixed[group]
        return {
            121: "plants_animals",
            122: "science_technology",
            123: "plants_animals",
            124: "plants_animals",
            125: "geography_world",
            126: "science_technology",
            127: "science_technology",
            128: "witnesses_of_time",
            129: "science_technology",
            130: "science_technology",
        }[number]

    fixed = {
        0: "witnesses_of_time",
        1: "geography_world",
        2: "geography_world",
        3: "geography_world",
        4: "plants_animals",
        6: "science_technology",
        7: "witnesses_of_time",
        8: "media_entertainment",
        9: "sport",
    }
    if group in fixed:
        return fixed[group]
    return "geography_world" if number in {92, 93} else "science_technology"


def subtopic(question_type: str, question: dict, category: str) -> str:
    number = number_of(question)
    if 41 <= number <= 140:
        group = (number - 41) // 10
        if question_type in {"multiple_choice", "true_false", "match"}:
            return GENERATED_PAIR_SUBTOPICS[group]
        return GENERATED_FACT_SUBTOPICS[group]

    subject_keys = question.get("subject_keys", [])
    if any(":game:" in key or ":tech:xbox" in key or ":tech:ps" in key or ":tech:switch" in key for key in subject_keys):
        return "Videospiele und Konsolen"
    if any(":music:" in key for key in subject_keys):
        return "Popmusik"
    if any(":film:" in key for key in subject_keys):
        return "Film"
    if any(":series:" in key for key in subject_keys):
        return "Serien"
    return DEFAULT_SUBTOPICS[category]


def tags(question: dict, category: str, topic: str) -> dict:
    subject_keys = question.get("subject_keys", [])
    entities = [key.split(":", 1)[1] for key in subject_keys if key.startswith("entity:")]
    topics = [topic]
    topics.extend(key.split(":", 1)[1] for key in subject_keys if key.startswith("subject:"))
    return {
        "topics": list(dict.fromkeys(topics)),
        "entities": list(dict.fromkeys(entities)),
        "genres": [],
        "regions": [],
        "eras": [],
    }


def migrate_question(question_type: str, question: dict) -> tuple[str, dict]:
    category = primary_category(question_type, question)
    topic = subtopic(question_type, question, category)
    payload = {
        "id": question["id"],
        "question_type": question_type,
        "primary_category": category,
        "subtopic": topic,
        "tags": tags(question, category, topic),
        "source": {"status": "legacy_bank", "references": []},
    }
    for key, value in question.items():
        if key not in {"id", "category", "knowledge_category", "subject_keys"}:
            payload[key] = value
    if question.get("subject_keys"):
        payload["subject_keys"] = question["subject_keys"]
    return category, payload


def _retired_main() -> None:
    if "--replace" not in sys.argv:
        raise SystemExit(
            "Nur für die Erstübernahme: mit --replace bestätigen. "
            "Dabei wird die bestehende Fragenablage neu erzeugt."
        )
    if LIBRARY_ROOT.exists():
        shutil.rmtree(LIBRARY_ROOT)
    LIBRARY_ROOT.mkdir()

    manifest = {
        "schema_version": 1,
        "storage_order": ["question_type", "primary_category"],
        "round_order": [
            "true_false",
            "multiple_choice",
            "match",
            "order",
            "estimate",
        ],
        "usage_tracking": {
            "location": "database.question_usage",
            "repeat_before_exhaustion": False,
        },
        "question_types": {
            key: {"label": label, "directory": directory, "active": active}
            for key, (label, directory, active) in QUESTION_TYPES.items()
        },
        "categories": {
            key: {"label": label, "directory": directory}
            for key, (label, directory) in CATEGORIES.items()
        },
    }
    (LIBRARY_ROOT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for question_type, questions in QUESTION_BANK.items():
        for question in questions:
            category, payload = migrate_question(question_type, question)
            grouped[(question_type, category)].append(payload)

    for question_type, (_, type_directory, _) in QUESTION_TYPES.items():
        for category, (_, category_directory) in CATEGORIES.items():
            target = LIBRARY_ROOT / type_directory / category_directory
            target.mkdir(parents=True, exist_ok=True)
            questions = grouped.get((question_type, category), [])
            (target / "fragen.json").write_text(
                json.dumps(questions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )

    print(f"{sum(len(items) for items in grouped.values())} Fragen nach {LIBRARY_ROOT} migriert")


def main() -> None:
    raise SystemExit(
        "Stillgelegt: Dieses Skript würde die flache Fragenstruktur wieder durch "
        "Kategorien-Unterordner ersetzen."
    )


if __name__ == "__main__":
    main()
