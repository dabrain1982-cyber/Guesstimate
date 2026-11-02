"""Append the researched October 2026 question expansion safely.

The data in this file is intentionally explicit so the researched batch remains
auditable. Existing question records are never rewritten or replaced.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VERIFIED_ON = "2026-10-17"


def source(
    title: str,
    url: str,
    *more: tuple[str, str],
    verified_on: str = VERIFIED_ON,
) -> dict[str, Any]:
    references = [{"title": title, "url": url}]
    references.extend({"title": item_title, "url": item_url} for item_title, item_url in more)
    return {
        "status": "verified",
        "verified_on": verified_on,
        "references": references,
    }


PHASE1: dict[str, list[dict[str, Any]]] = {
    "multiplechoice": [
        {
            "id": "mc606",
            "question_type": "multiple_choice",
            "primary_category": "human_everyday",
            "subtopic": "Snackkultur & Markensprache",
            "tags": {
                "topics": ["Snacks", "Popkultur", "Markensprache"],
                "entities": ["Cheetos", "Cheetle", "PepsiCo"],
                "genres": [],
                "regions": ["International"],
                "eras": ["Gegenwart"],
            },
            "prompt": "Wie nennt Cheetos offiziell den orangefarbenen Staub, der nach dem Snacken an den Fingern klebt?",
            "answer": "B",
            "explanation": "Cheetos nennt den orangefarbenen Gewürzstaub an den Fingern offiziell „Cheetle“.",
            "subject_keys": [
                "topic:human_everyday:snackkultur-und-markensprache",
                "entity:cheetos",
                "entity:cheetle",
            ],
            "source": source(
                "PepsiCo: Cheetos Pops Into The New Year",
                "https://www.pepsico.com/en/newsroom/press-releases/2020/cheetos-pops-into-the-new-year-with-launch-of-cheetos-popcorn-in-stores-nationwide",
                verified_on="2026-10-18",
            ),
            "options": {
                "A": "Cheddarprint",
                "B": "Cheetle",
                "C": "Chester Dust",
                "D": "Crunchmark",
            },
        }
    ],
    "paarebilden": [
        {
            "id": "ma227",
            "question_type": "match",
            "primary_category": "witnesses_of_time",
            "subtopic": "Nobelpreis & Institutionen",
            "tags": {
                "topics": ["Nobelpreis", "Preisvergabe", "Institutionen"],
                "entities": [
                    "Königlich Schwedische Akademie der Wissenschaften",
                    "Karolinska-Institut",
                    "Schwedische Akademie",
                ],
                "genres": [],
                "regions": ["Schweden"],
                "eras": ["seit 1901"],
            },
            "prompt": "Ordne den Nobelpreis der Institution zu, die seine Preisträger auswählt.",
            "left": [
                "Nobelpreis für Physik",
                "Nobelpreis für Physiologie oder Medizin",
                "Nobelpreis für Literatur",
            ],
            "right": [
                "Schwedische Akademie",
                "Nobelversammlung am Karolinska-Institut",
                "Königlich Schwedische Akademie der Wissenschaften",
            ],
            "answer": {
                "Nobelpreis für Physik": "Königlich Schwedische Akademie der Wissenschaften",
                "Nobelpreis für Physiologie oder Medizin": "Nobelversammlung am Karolinska-Institut",
                "Nobelpreis für Literatur": "Schwedische Akademie",
            },
            "explanation": "Die Wissenschaftsakademie entscheidet über Physik, die Nobelversammlung am Karolinska-Institut über Medizin und die Schwedische Akademie über Literatur.",
            "subject_keys": [
                "topic:witnesses_of_time:nobelpreis-vergabeinstitutionen",
                "entity:koeniglich-schwedische-akademie-der-wissenschaften",
                "entity:karolinska-institut",
                "entity:schwedische-akademie",
            ],
            "source": source(
                "Nobel Prize: The history of the Nobel Foundation",
                "https://www.nobelprize.org/were-in-this-forever-the-history-of-the-nobel-foundation/",
            ),
        }
    ],
    "reihenfolge": [
        {
            "id": "or401",
            "question_type": "order",
            "primary_category": "music",
            "subtopic": "Tonträger & Audioformate",
            "tags": {
                "topics": ["Audioformate", "Musikspeicherung", "Technikgeschichte"],
                "entities": ["Langspielplatte", "Compact Cassette", "Compact Disc", "MP3"],
                "genres": [],
                "regions": ["International"],
                "eras": ["20. Jahrhundert"],
            },
            "prompt": "Ordne diese Audioformate nach ihrer Einführung – vom ältesten zum jüngsten.",
            "items": ["Compact Disc (CD)", "MP3-Dateiendung", "Langspielplatte (LP)", "Compact Cassette"],
            "answer": ["Langspielplatte (LP)", "Compact Cassette", "Compact Disc (CD)", "MP3-Dateiendung"],
            "explanation": "Langspielplatte (1948) → Compact Cassette (1963) → Compact Disc (1982) → MP3-Dateiendung (1995).",
            "subject_keys": [
                "topic:music:geschichte-der-audioformate",
                "entity:langspielplatte",
                "entity:compact-cassette",
                "entity:compact-disc",
                "entity:mp3",
            ],
            "source": source(
                "Library of Congress: Recording Technology Timeline",
                "https://www.loc.gov/programs/national-recording-preservation-plan/tools-and-resources/historical-background/timeline/",
                (
                    "Fraunhofer IIS: 30 Years of .mp3",
                    "https://www.iis.fraunhofer.de/en/magazin/panorama/2025/30-years-of-mp3.html",
                ),
            ),
        },
        {
            "id": "or402",
            "question_type": "order",
            "primary_category": "sport",
            "subtopic": "Sportbälle & Regelmaße",
            "tags": {
                "topics": ["Sportgeräte", "Ballgewicht", "Regelwerke"],
                "entities": ["ITTF", "ITF", "IFAB", "FIBA"],
                "genres": [],
                "regions": ["International"],
                "eras": ["Regelstand 2024 bis 2026"],
            },
            "prompt": "Ordne diese regulären Sportbälle nach ihrem vorgeschriebenen Gewicht – von leicht nach schwer.",
            "items": ["Fußball", "Tischtennisball", "Basketball Größe 7", "Tennisball"],
            "answer": ["Tischtennisball", "Tennisball", "Fußball", "Basketball Größe 7"],
            "explanation": "Tischtennisball (2,7 g) → Tennisball (56,0–59,4 g) → Fußball (410–450 g) → Basketball Größe 7 (580–620 g). Die Gewichtsbereiche überschneiden sich nicht.",
            "subject_keys": [
                "topic:sport:regelgewichte-von-sportbaellen",
                "entity:tischtennisball",
                "entity:tennisball",
                "entity:fussball",
                "entity:basketball-groesse-7",
            ],
            "source": source(
                "ITTF: Technical Leaflet T3 – The Ball",
                "https://documents.ittf.sport/sites/default/files/public/2020-10/2020_BoD_documents_2.pdf",
                (
                    "ITF: 2025 Rules of Tennis",
                    "https://www.itftennis.com/media/7221/2025-rules-of-tennis-english.pdf",
                ),
                (
                    "IFAB: Law 2 – The Ball",
                    "https://www.theifab.com/laws/2025-26/the-ball/",
                ),
                (
                    "FIBA: Official Basketball Rules 2024 – Basketball Equipment",
                    "https://assets.fiba.basketball/image/upload/documents-corporate-fiba-official-rules-2024-official-basketball-rules-and-basketball-equipment.pdf",
                ),
            ),
        },
        {
            "id": "or403",
            "question_type": "order",
            "primary_category": "science_technology",
            "subtopic": "Monde im Sonnensystem",
            "tags": {
                "topics": ["Monde", "Durchmesser", "Sonnensystem"],
                "entities": ["Phobos", "Enceladus", "Europa", "Titan"],
                "genres": [],
                "regions": ["Sonnensystem"],
                "eras": [],
            },
            "prompt": "Ordne diese Monde nach ihrem mittleren Durchmesser – vom kleinsten zum größten.",
            "items": ["Europa", "Phobos", "Titan", "Enceladus"],
            "answer": ["Phobos", "Enceladus", "Europa", "Titan"],
            "explanation": "Phobos (22,2 km) → Enceladus (498,8 km) → Europa (3.121,6 km) → Titan (5.150 km). Die Durchmesser ergeben sich aus den von NASA angegebenen mittleren Radien.",
            "subject_keys": [
                "topic:science_technology:monddurchmesser",
                "entity:phobos",
                "entity:enceladus",
                "entity:europa-mond",
                "entity:titan-mond",
            ],
            "source": source(
                "NASA: Solar System Lithograph Set – Moons",
                "https://www.nasa.gov/wp-content/uploads/2011/05/solar_system_lithograph_set_h.pdf?emrc=c77ddc",
            ),
        },
        {
            "id": "or404",
            "question_type": "order",
            "primary_category": "human_everyday",
            "subtopic": "Bundestag & Gesetzgebung",
            "tags": {
                "topics": ["Gesetzgebung", "Bundestag", "Parlamentsarbeit"],
                "entities": ["Deutscher Bundestag", "Bundestagsausschüsse"],
                "genres": [],
                "regions": ["Deutschland"],
                "eras": ["Gegenwart"],
            },
            "prompt": "Ordne diese Stationen eines üblichen Gesetzentwurfs im Bundestag – von früh nach spät.",
            "items": [
                "Beratung im Fachausschuss",
                "Dritte Lesung und Schlussabstimmung",
                "Erste Lesung und Überweisung",
                "Zweite Lesung im Plenum",
            ],
            "answer": [
                "Erste Lesung und Überweisung",
                "Beratung im Fachausschuss",
                "Zweite Lesung im Plenum",
                "Dritte Lesung und Schlussabstimmung",
            ],
            "explanation": "Erste Lesung und Überweisung → Beratung im Fachausschuss → zweite Lesung im Plenum → dritte Lesung und Schlussabstimmung.",
            "subject_keys": [
                "topic:human_everyday:gesetzgebungsverfahren-im-bundestag",
                "entity:deutscher-bundestag",
                "subject:lesungen-eines-gesetzentwurfs",
            ],
            "source": source(
                "Deutscher Bundestag: Weg der Gesetzgebung",
                "https://www.bundestag.de/parlament/aufgaben/gesetzgebung_neu/gesetzgebung/weg-255468",
            ),
        },
    ],
    "schaetzung": [
        {
            "id": "es225",
            "question_type": "estimate",
            "primary_category": "music",
            "subtopic": "Musik im Weltraum",
            "tags": {
                "topics": ["Voyager Golden Record", "Musikauswahl", "Raumfahrt"],
                "entities": ["NASA", "Voyager Golden Record"],
                "genres": [],
                "regions": ["Weltraum"],
                "eras": ["1977"],
            },
            "prompt": "Wie viele Minuten Musik enthält die Voyager Golden Record laut NASA?",
            "answer": 90,
            "unit": "Minuten",
            "explanation": "Die vergoldete Schallplatte an Voyager 1 und 2 enthält eine 90-minütige Musikauswahl aus verschiedenen Kulturen und Epochen.",
            "subject_keys": ["topic:music:voyager-golden-record", "entity:nasa", "entity:voyager-golden-record"],
            "source": source(
                "NASA: Golden Record Contents",
                "https://science.nasa.gov/mission/voyager/golden-record-contents/",
            ),
        },
        {
            "id": "es226",
            "question_type": "estimate",
            "primary_category": "gaming",
            "subtopic": "Spielzeit & Tageszyklus",
            "tags": {
                "topics": ["Minecraft", "Tageszyklus", "Spielmechanik"],
                "entities": ["Minecraft", "Mojang"],
                "genres": ["Sandbox"],
                "regions": ["International"],
                "eras": ["Gegenwart"],
            },
            "prompt": "Wie viele reale Minuten dauert ein vollständiger Tag in Minecraft?",
            "answer": 20,
            "unit": "Minuten",
            "explanation": "Ein vollständiger Minecraft-Tag umfasst 24.000 Spielticks und dauert 20 Minuten realer Spielzeit.",
            "subject_keys": ["topic:gaming:minecraft-tageszyklus", "entity:minecraft", "subject:24000-spielticks"],
            "source": source(
                "Minecraft Education: Coding with Minecraft – Adjust Time",
                "https://education.minecraft.net/lessonsupportfiles/8325548264145603-Coding%20with%20Minecraft_Unit%206_Functions.pdf",
            ),
        },
        {
            "id": "es227",
            "question_type": "estimate",
            "primary_category": "sport",
            "subtopic": "Basketball & Spielfeldmaße",
            "tags": {
                "topics": ["Basketball", "Korbhöhe", "Sportregeln"],
                "entities": ["FIBA"],
                "genres": [],
                "regions": ["International"],
                "eras": ["Regelstand 2026"],
            },
            "prompt": "Wie hoch hängt ein Basketballkorb nach FIBA-Regeln über dem Spielfeld?",
            "answer": 3.05,
            "unit": "Meter",
            "explanation": "Die Oberkante des Rings liegt nach den internationalen Basketballregeln 3,05 Meter über dem Boden.",
            "subject_keys": ["topic:sport:basketball-korbhoehe", "entity:fiba", "subject:hoehe-des-basketballrings"],
            "source": source(
                "FIBA: Official Basketball Rules 2026",
                "https://about.fiba.basketball/en/services/resource-hub/downloads",
            ),
        },
        {
            "id": "es228",
            "question_type": "estimate",
            "primary_category": "sport",
            "subtopic": "Curling & Sportgerät",
            "tags": {
                "topics": ["Curling", "Curlingstein", "Wintersport"],
                "entities": ["Olympische Spiele"],
                "genres": [],
                "regions": ["International"],
                "eras": [],
            },
            "prompt": "Wie viele Kilogramm wiegt ein olympischer Curlingstein laut IOC-Unterlagen?",
            "answer": 19.96,
            "unit": "Kilogramm",
            "explanation": "Die Olympia-Unterlagen nennen für den beim Curling gespielten Stein ein Gewicht von 19,96 Kilogramm.",
            "subject_keys": ["topic:sport:gewicht-eines-curlingsteins", "entity:curlingstein", "entity:ioc"],
            "source": source(
                "IOC Olympic Library: Sochi 2014 Ticket Sales Guide – Curling",
                "https://library.olympics.com/digitalCollection/DigitalCollectionAttachmentDownloadHandler.ashx?documentId=161101&parentDocumentId=56870&skipCopyright=true&skipWatermark=true",
            ),
        },
        {
            "id": "es229",
            "question_type": "estimate",
            "primary_category": "gaming",
            "subtopic": "LEGO & Spielfiguren",
            "tags": {
                "topics": ["LEGO", "Minifigur", "Bausteinsystem"],
                "entities": ["LEGO Minifigur", "LEGO Group"],
                "genres": ["Konstruktionsspielzeug"],
                "regions": ["Dänemark", "International"],
                "eras": ["seit 1978"],
            },
            "prompt": "Wie viele aufeinandergesetzte normale LEGO-Steine ist eine Minifigur ohne Haare oder Kopfbedeckung hoch?",
            "answer": 4,
            "unit": "LEGO-Steine",
            "explanation": "Ohne Haare oder Kopfbedeckung ist eine klassische LEGO-Minifigur genau so hoch wie vier aufeinandergesetzte Standardsteine.",
            "subject_keys": ["topic:gaming:lego-minifigur-proportionen", "entity:lego-minifigur", "entity:lego-group"],
            "source": source(
                "LEGO: Little Figure, Big Story",
                "https://www.lego.com/en-us/aboutus/news/2019/october/minifigure-40",
            ),
        },
        {
            "id": "es230",
            "question_type": "estimate",
            "primary_category": "witnesses_of_time",
            "subtopic": "Nobelpreis & Auszeichnungen",
            "tags": {
                "topics": ["Nobelpreis", "Medaille", "Gold"],
                "entities": ["Nobelstiftung", "Nobelpreismedaille"],
                "genres": [],
                "regions": ["Schweden", "Norwegen"],
                "eras": ["Gegenwart"],
            },
            "prompt": "Wie viele Karat hat das recycelte Gold der heutigen Nobelpreismedaillen?",
            "answer": 18,
            "unit": "Karat",
            "explanation": "Die Nobelstiftung lässt die Medaillen heute in Handarbeit aus recyceltem Gold mit 18 Karat herstellen.",
            "subject_keys": ["topic:witnesses_of_time:nobelpreismedaillen", "entity:nobelstiftung", "subject:18-karat-gold"],
            "source": source(
                "Nobel Prize: Nobel Prize facts",
                "https://www.nobelprize.org/prizes/lists/nobel-prize-facts/",
            ),
        },
        {
            "id": "es231",
            "question_type": "estimate",
            "primary_category": "geography_world",
            "subtopic": "Berlin & Bauwerke",
            "tags": {
                "topics": ["Berliner Fernsehturm", "Treppen", "Bauwerke"],
                "entities": ["Berliner Fernsehturm"],
                "genres": [],
                "regions": ["Berlin", "Deutschland"],
                "eras": ["Gegenwart"],
            },
            "prompt": "Wie viele Stufen umfasst das Treppenhaus des Berliner Fernsehturms?",
            "answer": 986,
            "unit": "Stufen",
            "explanation": "Das Treppenhaus des Berliner Fernsehturms umfasst 986 Stufen. Es ist nur für Notfälle und Servicepersonal vorgesehen.",
            "subject_keys": ["topic:geography_world:berliner-fernsehturm", "entity:berliner-fernsehturm", "subject:treppenhaus"],
            "source": source(
                "Berliner Fernsehturm: FAQ",
                "https://tv-turm.de/faqs/",
            ),
        },
        {
            "id": "es232",
            "question_type": "estimate",
            "primary_category": "witnesses_of_time",
            "subtopic": "Bundestag & Reichstagsgebäude",
            "tags": {
                "topics": ["Bundestagsadler", "Reichstagsgebäude", "Parlamentskunst"],
                "entities": ["Bundestagsadler", "Norman Foster", "Ludwig Gies"],
                "genres": [],
                "regions": ["Berlin", "Deutschland"],
                "eras": ["1999"],
            },
            "prompt": "Wie viele Tonnen wiegt der große Bundesadler im Plenarsaal des Bundestages ungefähr?",
            "answer": 2.5,
            "unit": "Tonnen",
            "explanation": "Der aus vier Aluminiumschichten bestehende Adler hat 58 Quadratmeter Fläche und wiegt ungefähr 2,5 Tonnen.",
            "subject_keys": ["topic:witnesses_of_time:bundestagsadler", "entity:bundestagsadler", "entity:reichstagsgebaeude"],
            "source": source(
                "Deutscher Bundestag: Norman Foster",
                "https://www.bundestag.de/blueprint/servlet/en/visittheBundestag/art/artists/foster_inhalt-369938",
            ),
        },
        {
            "id": "es233",
            "question_type": "estimate",
            "primary_category": "science_technology",
            "subtopic": "Genetik & Zellbiologie",
            "tags": {
                "topics": ["DNA", "Genom", "Zellkern"],
                "entities": ["menschliche DNA", "NHGRI"],
                "genres": [],
                "regions": ["Menschlicher Körper"],
                "eras": [],
            },
            "prompt": "Wie viele Meter lang wäre die DNA aus dem Zellkern einer menschlichen Körperzelle ausgestreckt ungefähr?",
            "answer": 2,
            "unit": "Meter",
            "explanation": "Die DNA eines menschlichen Zellkerns wäre ausgestreckt ungefähr zwei Meter lang, obwohl der Zellkern nur mikroskopisch klein ist.",
            "subject_keys": ["topic:science_technology:dna-verpackung", "entity:menschliche-dna", "subject:dna-laenge-pro-zelle"],
            "source": source(
                "National Human Genome Research Institute: 10 Years of the Human Genome",
                "https://www.genome.gov/Pages/About/Planning/Symposium2011AgendaPowerpoints/Bernstein-10yearsHumanGenome.pdf",
            ),
        },
        {
            "id": "es605",
            "question_type": "estimate",
            "primary_category": "human_everyday",
            "subtopic": "Post-it-Entwicklung",
            "tags": {
                "topics": ["Post-it", "Erfindungen", "Büroalltag"],
                "entities": ["Spencer Silver", "Art Fry", "3M"],
                "genres": [],
                "regions": ["USA"],
                "eras": ["1968 bis 1980"],
            },
            "prompt": "Wie viele Jahre lagen ungefähr zwischen der Entdeckung des Post-it-Klebers 1968 und dem Marktstart 1980?",
            "answer": 12,
            "unit": "Jahre",
            "explanation": "Der schwach haftende Kleber entstand 1968; Post-it Notes kamen 1980 auf den Markt. Dazwischen lagen rund zwölf Jahre.",
            "subject_keys": ["topic:human_everyday:post-it-entwicklung", "entity:post-it", "entity:3m"],
            "source": source(
                "USPTO: Post-it Notes show real sticking power",
                "https://ttabvue.uspto.gov/ttabvue/ttabvue-91173411-OPP-44.pdf",
            ),
        },
        {
            "id": "es235",
            "question_type": "estimate",
            "primary_category": "geography_world",
            "subtopic": "Bahnhöfe & Infrastruktur",
            "tags": {
                "topics": ["Bahnhöfe", "Bahnsteige", "Rekorde"],
                "entities": ["Essen Hauptbahnhof", "Deutsche Bahn"],
                "genres": [],
                "regions": ["Essen", "Deutschland"],
                "eras": ["Gegenwart"],
            },
            "prompt": "Wie viele Meter lang ist Deutschlands längster Bahnsteig am Essener Hauptbahnhof laut Deutscher Bahn?",
            "answer": 667,
            "unit": "Meter",
            "explanation": "Der Bahnsteig an den Gleisen 4 und 6 in Essen ist 667 Meter lang und wird von der Deutschen Bahn als längster Bahnsteig Deutschlands bezeichnet.",
            "subject_keys": ["topic:geography_world:deutsche-bahnhoefe", "entity:essen-hauptbahnhof", "subject:laengster-bahnsteig-deutschlands"],
            "source": source(
                "Deutsche Bahn: Top 10 der NRW-Bahnhöfe",
                "https://www-ecm-pu.deutschebahn.com/de/presse/presse-regional/pr-duesseldorf-de/DB-in-NRW/Top-10-der-NRW-Bahnhoefe-11276958",
            ),
        },
    ],
}


DIRECTORIES = {
    "multiplechoice": "multiplechoice",
    "paarebilden": "paarebilden",
    "reihenfolge": "reihenfolge",
    "schaetzung": "schaetzung",
}


def normalized(text: str) -> str:
    return re.sub(r"\W+", " ", text.casefold()).strip()


def append_batch(batch: dict[str, list[dict[str, Any]]]) -> None:
    all_rows: list[dict[str, Any]] = []
    for path in (ROOT / "fragen").glob("*/fragen.json"):
        all_rows.extend(json.loads(path.read_text(encoding="utf-8")))
    existing_ids = {row["id"] for row in all_rows}
    existing_prompts = {normalized(row["prompt"]): row["id"] for row in all_rows}
    existing_subject_sets = {
        tuple(sorted(row.get("subject_keys", []))): row["id"]
        for row in all_rows
        if row.get("subject_keys")
    }

    additions = [row for rows in batch.values() for row in rows]
    addition_ids = [row["id"] for row in additions]
    if len(addition_ids) != len(set(addition_ids)):
        raise SystemExit("Der neue Fragenblock enthält doppelte IDs.")
    if set(addition_ids) & existing_ids:
        raise SystemExit(f"Neue IDs sind bereits belegt: {sorted(set(addition_ids) & existing_ids)}")
    for row in additions:
        prompt_key = normalized(row["prompt"])
        if prompt_key in existing_prompts:
            raise SystemExit(f"Doppelter Fragetext {row['id']} / {existing_prompts[prompt_key]}")
        subject_set = tuple(sorted(row.get("subject_keys", [])))
        if subject_set and subject_set in existing_subject_sets:
            raise SystemExit(f"Doppelter Themen-Steckbrief {row['id']} / {existing_subject_sets[subject_set]}")

    for key, rows in batch.items():
        path = ROOT / "fragen" / DIRECTORIES[key] / "fragen.json"
        stored = json.loads(path.read_text(encoding="utf-8"))
        stored.extend(rows)
        path.write_text(json.dumps(stored, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"{path.relative_to(ROOT)}: +{len(rows)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["phase1"])
    args = parser.parse_args()
    append_batch(PHASE1 if args.phase == "phase1" else {})


if __name__ == "__main__":
    main()

