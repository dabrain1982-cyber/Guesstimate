"""One-time, source-backed expansion of four undersupplied categories.

The physical JSON files remain the canonical question library.  This migration
is idempotent: it refuses to add an ID that is already present.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "fragen"
MANIFEST = json.loads((LIBRARY / "manifest.json").read_text(encoding="utf-8"))

TYPE_DIRS = {
    key: value["directory"] for key, value in MANIFEST["question_types"].items()
}
CATEGORY_DIRS = {
    key: value["directory"] for key, value in MANIFEST["categories"].items()
}

PREFIXES = {
    "multiple_choice": "mc",
    "true_false": "tf",
    "match": "ma",
    "order": "or",
    "estimate": "es",
}

next_number = {
    "multiple_choice": 151,
    "true_false": 151,
    "match": 151,
    "order": 151,
    "estimate": 151,
}

new_questions: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)


def reference(title: str, url: str) -> dict[str, str]:
    return {"title": title, "url": url}


def source(*references: dict[str, str]) -> dict[str, Any]:
    return {
        "status": "verified",
        "verified_on": "2026-10-04",
        "references": list(references),
    }


def slug(value: str) -> str:
    value = value.casefold()
    replacements = {
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "ß": "ss",
        "&": "und",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")


def add(
    question_type: str,
    category: str,
    subtopic: str,
    prompt: str,
    answer: Any,
    explanation: str,
    fact_source: dict[str, Any],
    *,
    entities: list[str] | None = None,
    genres: list[str] | None = None,
    regions: list[str] | None = None,
    eras: list[str] | None = None,
    **fields: Any,
) -> None:
    number = next_number[question_type]
    next_number[question_type] += 1
    question_id = f"{PREFIXES[question_type]}{number:03d}"
    entities = entities or []
    question = {
        "id": question_id,
        "question_type": question_type,
        "primary_category": category,
        "subtopic": subtopic,
        "tags": {
            "topics": [subtopic],
            "entities": entities,
            "genres": genres or [],
            "regions": regions or [],
            "eras": eras or [],
        },
        "source": fact_source,
        "prompt": prompt,
        "answer": answer,
        "explanation": explanation,
        "subject_keys": [
            f"topic:{category}:{slug(subtopic)}",
            *(f"entity:{entity.casefold()}" for entity in entities),
        ],
        **fields,
    }
    new_questions[(question_type, category)].append(question)


def add_mc(
    category: str,
    subtopic: str,
    prompt: str,
    correct: str,
    distractors: list[str],
    explanation: str,
    fact_source: dict[str, Any],
    **metadata: Any,
) -> None:
    number = next_number["multiple_choice"]
    values = [correct, *distractors]
    shift = number % 4
    values = values[shift:] + values[:shift]
    options = dict(zip("ABCD", values))
    answer = next(key for key, value in options.items() if value == correct)
    add(
        "multiple_choice",
        category,
        subtopic,
        prompt,
        answer,
        explanation,
        fact_source,
        options=options,
        **metadata,
    )


def add_tf(
    category: str,
    subtopic: str,
    prompt: str,
    answer: bool,
    explanation: str,
    fact_source: dict[str, Any],
    **metadata: Any,
) -> None:
    add(
        "true_false",
        category,
        subtopic,
        prompt,
        answer,
        explanation,
        fact_source,
        **metadata,
    )


def add_match(
    category: str,
    subtopic: str,
    prompt: str,
    pairs: list[tuple[str, str]],
    fact_source: dict[str, Any],
    **metadata: Any,
) -> None:
    left = [item[0] for item in pairs]
    right = [item[1] for item in pairs]
    add(
        "match",
        category,
        subtopic,
        prompt,
        dict(pairs),
        "; ".join(f"{left_item} – {right_item}" for left_item, right_item in pairs)
        + ".",
        fact_source,
        left=left,
        right=right,
        **metadata,
    )


def add_order(
    category: str,
    subtopic: str,
    prompt: str,
    answer: list[str],
    explanation: str,
    fact_source: dict[str, Any],
    **metadata: Any,
) -> None:
    items = answer[2:] + answer[:2]
    add(
        "order",
        category,
        subtopic,
        prompt,
        answer,
        explanation,
        fact_source,
        items=items,
        **metadata,
    )


def add_estimate(
    category: str,
    subtopic: str,
    prompt: str,
    answer: int | float,
    unit: str,
    explanation: str,
    fact_source: dict[str, Any],
    **metadata: Any,
) -> None:
    add(
        "estimate",
        category,
        subtopic,
        prompt,
        answer,
        explanation,
        fact_source,
        unit=unit,
        **metadata,
    )


PLAYSTATION = source(
    reference(
        "PlayStation history: 1994",
        "https://www.playstation.com/en-us/playstation-history/1994-ps-one/",
    )
)
GAME_BOY = source(
    reference(
        "Nintendo: Game Boy hardware history",
        "https://www.nintendo.com/en-gb/Hardware/Nintendo-History/Game-Boy/Game-Boy-627031.html",
    )
)
MARIO = source(
    reference(
        "Nintendo: The history of Super Mario",
        "https://www.nintendo.com/en-ca/explore/characters/mario/history/",
    )
)
NINTENDO_HISTORY = source(
    reference("Nintendo history", "https://careers.nintendo.com/our-history/")
)
ZELDA = source(
    reference(
        "Nintendo: The Triforce",
        "https://www.nintendo.com/us/explore/characters/zelda/triforce/",
    )
)
XBOX = source(
    reference(
        "Xbox 25th anniversary timeline",
        "https://www.xbox.com/en-us/xbox-25th-anniversary",
    )
)
MINECRAFT = source(
    reference(
        "Minecraft: About Minecraft",
        "https://www.minecraft.net/en-us/about-minecraft",
    )
)
MINECRAFT_MOBS = source(
    reference(
        "Minecraft: Everything you need to know about mobs",
        "https://www.minecraft.net/en-us/article/minecraft-mobs",
    )
)
MINECRAFT_COMMANDS = source(
    reference(
        "Minecraft: How to use commands",
        "https://www.minecraft.net/en-us/article/minecraft-commands",
    )
)
SWITCH = source(
    reference(
        "Nintendo: Switch launch",
        "https://www.nintendo.com/en-gb/News/2017/January/Nintendo-Switch-launches-on-3rd-March--1173122.html",
    )
)


def add_gaming_questions() -> None:
    category = "gaming"
    history = "Geschichte & Meilensteine"
    hardware = "Konsolen & Hardware"
    studios = "Studios & Entwicklung"
    worlds = "Spielwelten & Figuren"
    mechanics = "Spielmechanik & Begriffe"

    add_mc(category, history, "Wann erschien die erste PlayStation in Japan?", "1994", ["1989", "2001", "2005"], "Die erste PlayStation startete am 3. Dezember 1994 in Japan.", PLAYSTATION, entities=["PlayStation"], eras=["1990er"])
    add_mc(category, history, "In welchem Jahr kam der Game Boy in Japan auf den Markt?", "1989", ["1983", "1994", "2001"], "Nintendo brachte den Game Boy 1989 in Japan heraus.", GAME_BOY, entities=["Game Boy"], eras=["1980er"])
    add_mc(category, hardware, "Welches Speichermedium nutzte die erste PlayStation für ihre Spiele?", "CD-ROM", ["Diskette", "MiniDisc", "DVD"], "Die erste PlayStation setzte auf CD-ROMs statt auf Module.", PLAYSTATION, entities=["PlayStation"])
    add_mc(category, hardware, "Wie viele AA-Batterien benötigte der ursprüngliche Game Boy?", "Vier", ["Zwei", "Sechs", "Acht"], "Der ursprüngliche Game Boy wurde mit vier AA-Batterien betrieben.", GAME_BOY, entities=["Game Boy"])
    add_mc(category, studios, "Zu welchem Unternehmen gehört die Spielemarke Xbox?", "Microsoft", ["Sony", "Nintendo", "Sega"], "Xbox ist die Spielemarke von Microsoft.", XBOX, entities=["Xbox", "Microsoft"])
    add_mc(category, studios, "Welches Studio entwickelt Minecraft?", "Mojang Studios", ["Naughty Dog", "Valve", "CD Projekt Red"], "Minecraft wird von Mojang Studios entwickelt.", MINECRAFT, entities=["Minecraft", "Mojang Studios"])
    add_mc(category, worlds, "Wie heißt der meist grün gekleidete Held der Reihe „The Legend of Zelda“?", "Link", ["Zelda", "Ganondorf", "Tingle"], "Link ist der wiederkehrende Held der Zelda-Reihe; Zelda ist die Prinzessin.", ZELDA, entities=["Link", "The Legend of Zelda"])
    add_mc(category, worlds, "In welchem Land spielen viele Geschichten der Zelda-Reihe?", "Hyrule", ["Tamriel", "Midgar", "San Andreas"], "Viele Zelda-Geschichten sind im Land Hyrule angesiedelt.", ZELDA, entities=["Hyrule", "The Legend of Zelda"])
    add_mc(category, mechanics, "Welchem grundlegenden Spieltyp ordnet Minecraft sich selbst zu?", "Open-World-Sandbox", ["Rennsimulation", "Rundenstrategie", "Rhythmusspiel"], "Minecraft beschreibt sich als Open-World-Sandboxspiel.", MINECRAFT, entities=["Minecraft"])

    add_tf(category, history, "Xbox Series X und Series S erschienen im Jahr 2020.", True, "Microsoft nennt den 10. November 2020 als Start der Series-X|S-Generation.", XBOX, entities=["Xbox Series X", "Xbox Series S"], eras=["2020er"])
    add_tf(category, hardware, "Der ursprüngliche Game Boy zeigte Spiele auf einem vollfarbigen Bildschirm.", False, "Sein LCD stellte vier Graustufen dar, keine Vollfarben.", GAME_BOY, entities=["Game Boy"])
    add_tf(category, studios, "Die PlayStation-Marke wurde von Nintendo eingeführt.", False, "PlayStation ist eine Marke von Sony; Nintendo entwickelte eigene Konsolenreihen.", PLAYSTATION, entities=["PlayStation", "Sony"])
    add_tf(category, worlds, "Link trägt in der Zelda-Triforce-Zuordnung den Teil des Mutes.", True, "Nintendo ordnet Link die Triforce des Mutes zu.", ZELDA, entities=["Link", "Triforce"])
    add_tf(category, worlds, "Ein Creeper gilt in Minecraft als friedliche Kreatur.", False, "Minecraft führt den Creeper als feindlichen Mob.", MINECRAFT_MOBS, entities=["Minecraft", "Creeper"])
    add_tf(category, mechanics, "Minecraft besitzt laut offizieller Beschreibung kein fest vorgeschriebenes Spielende.", True, "Als Sandboxspiel hat Minecraft kein offizielles Ende, auch wenn viele den Enderdrachen als persönliches Ziel betrachten.", MINECRAFT, entities=["Minecraft"])
    add_tf(category, mechanics, "Minecraft unterscheidet Mobs grundsätzlich in passive, neutrale und feindliche Gruppen.", True, "Die offizielle Übersicht beschreibt genau diese drei Verhaltenskategorien.", MINECRAFT_MOBS, entities=["Minecraft", "Mobs"])

    add_match(category, history, "Ordne die Xbox-Generation ihrem Startjahr zu.", [("Xbox", "2001"), ("Xbox 360", "2005"), ("Xbox One", "2013")], XBOX, entities=["Xbox"], eras=["2000er", "2010er"])
    add_match(category, hardware, "Ordne die Konsole ihrem Hersteller zu.", [("PlayStation", "Sony"), ("Xbox", "Microsoft"), ("Game Boy", "Nintendo")], source(*PLAYSTATION["references"], *XBOX["references"], *GAME_BOY["references"]), entities=["PlayStation", "Xbox", "Game Boy"])
    add_match(category, hardware, "Ordne die Game-Boy-Angabe ihrem Wert zu.", [("Bildbreite", "160 Pixel"), ("Bildhöhe", "144 Pixel"), ("Graustufen", "4")], GAME_BOY, entities=["Game Boy"])
    add_match(category, studios, "Ordne die Spielemarke ihrem Unternehmen zu.", [("Super Mario", "Nintendo"), ("PlayStation", "Sony"), ("Xbox", "Microsoft")], source(*MARIO["references"], *PLAYSTATION["references"], *XBOX["references"]), entities=["Super Mario", "PlayStation", "Xbox"])
    add_match(category, studios, "Ordne die Spielemarke ihrem verantwortlichen Unternehmen zu.", [("Minecraft", "Mojang Studios"), ("Super Mario", "Nintendo"), ("Halo", "Xbox/Microsoft")], source(*MINECRAFT["references"], *MARIO["references"], *XBOX["references"]), entities=["Minecraft", "Super Mario", "Halo"])
    add_match(category, worlds, "Ordne die Zelda-Figur ihrem Triforce-Teil zu.", [("Link", "Mut"), ("Zelda", "Weisheit"), ("Ganondorf", "Kraft")], ZELDA, entities=["Link", "Zelda", "Ganondorf", "Triforce"])
    add_match(category, worlds, "Ordne den Begriff seiner Spielwelt zu.", [("Hyrule", "The Legend of Zelda"), ("Creeper", "Minecraft"), ("Pilzkönigreich", "Super Mario")], source(*ZELDA["references"], *MINECRAFT_MOBS["references"], *MARIO["references"]), entities=["Hyrule", "Creeper", "Pilzkönigreich"])
    add_match(category, worlds, "Ordne die Figur ihrer Rolle zu.", [("Link", "Held"), ("Zelda", "Prinzessin"), ("Ganondorf", "Gegenspieler")], ZELDA, entities=["Link", "Zelda", "Ganondorf"])
    add_match(category, mechanics, "Ordne den Minecraft-Mob seinem Grundverhalten zu.", [("Kuh", "passiv"), ("Wolf", "neutral"), ("Creeper", "feindlich")], MINECRAFT_MOBS, entities=["Minecraft", "Kuh", "Wolf", "Creeper"])

    add_order(category, history, "Ordne die Xbox-Konsolen nach ihrem Erscheinen.", ["Xbox", "Xbox 360", "Xbox One", "Xbox Series X|S"], "Xbox (2001) → Xbox 360 (2005) → Xbox One (2013) → Xbox Series X|S (2020).", XBOX, entities=["Xbox"])
    add_order(category, history, "Ordne diese Mario-Spiele nach ihrem Erscheinen.", ["Super Mario Bros.", "Super Mario Land", "Super Mario World", "Super Mario 64"], "Super Mario Bros. (1985) → Super Mario Land (1989) → Super Mario World (1991) → Super Mario 64 (1996).", MARIO, entities=["Super Mario"])
    add_order(category, history, "Ordne diese PlayStation-Eingabegeräte nach ihrer Einführung.", ["ursprünglicher PlayStation-Controller", "PlayStation Analog Joystick", "Dual Analog Controller", "DualShock"], "Controller (1994) → Analog Joystick (1996) → Dual Analog (April 1997) → DualShock (November 1997).", PLAYSTATION, entities=["PlayStation"])
    add_order(category, history, "Ordne diese Nintendo-Systeme chronologisch.", ["Game Boy", "Nintendo 64", "Nintendo DS", "Nintendo Switch"], "Game Boy (1989) → Nintendo 64 (1996) → Nintendo DS (2004) → Nintendo Switch (2017).", source(*GAME_BOY["references"], *NINTENDO_HISTORY["references"], *SWITCH["references"]), entities=["Nintendo"])
    add_order(category, studios, "Ordne diese Markenstarts chronologisch.", ["Game Boy", "PlayStation", "Xbox", "Nintendo Switch"], "Game Boy (1989) → PlayStation (1994) → Xbox (2001) → Nintendo Switch (2017).", source(*GAME_BOY["references"], *PLAYSTATION["references"], *XBOX["references"], *SWITCH["references"]), entities=["Nintendo", "Sony", "Microsoft"])
    add_order(category, worlds, "Ordne diese Mario-Abenteuer nach Veröffentlichung.", ["Super Mario Bros.", "Super Mario Bros. 2", "Super Mario Land", "Super Mario World"], "1985 → 1988 → 1989 → 1991.", MARIO, entities=["Super Mario"])
    add_order(category, mechanics, "Ordne die Minecraft-Schwierigkeitsgrade von friedlich bis schwer.", ["Friedlich", "Einfach", "Normal", "Schwer"], "Die offizielle Reihenfolge lautet Friedlich → Einfach → Normal → Schwer.", MINECRAFT_COMMANDS, entities=["Minecraft"])

    add_estimate(category, history, "In welchem Jahr erschien die erste spielbare PC-Version von Minecraft?", 2009, "Jahr", "Die erste PC-Version erschien 2009; die Vollversion folgte 2011.", MINECRAFT, entities=["Minecraft"], eras=["2000er"])
    add_estimate(category, hardware, "Wie viele Pixel breit ist der Bildschirm des ursprünglichen Game Boy?", 160, "Pixel", "Der Game-Boy-Bildschirm besitzt 160 Pixel in der Breite.", GAME_BOY, entities=["Game Boy"])
    add_estimate(category, hardware, "Wie viele Pixel hoch ist der Bildschirm des ursprünglichen Game Boy?", 144, "Pixel", "Der Bildschirm ist 144 Pixel hoch.", GAME_BOY, entities=["Game Boy"])
    add_estimate(category, hardware, "Wie viele Stunden Batterielaufzeit nennt Nintendo ungefähr für den ursprünglichen Game Boy?", 15, "Stunden", "Nintendo nennt ungefähr 15 Stunden mit vier AA-Batterien.", GAME_BOY, entities=["Game Boy"])
    add_estimate(category, worlds, "Aus wie vielen Teilen besteht die Triforce in der Zelda-Reihe?", 3, "Teile", "Die Triforce besteht aus Kraft, Weisheit und Mut.", ZELDA, entities=["Triforce"])
    add_estimate(category, worlds, "Wie viele zentrale Figuren erhalten in Nintendos Triforce-Erklärung je einen Teil?", 3, "Figuren", "Link, Zelda und Ganondorf erhalten jeweils einen Teil.", ZELDA, entities=["Link", "Zelda", "Ganondorf"])
    add_estimate(category, mechanics, "Wie viele grundlegende Verhaltenskategorien unterscheidet Minecraft bei Mobs?", 3, "Kategorien", "Die Kategorien sind passiv, neutral und feindlich.", MINECRAFT_MOBS, entities=["Minecraft", "Mobs"])
    add_estimate(category, mechanics, "Wie viele Graustufen konnte der ursprüngliche Game Boy darstellen?", 4, "Graustufen", "Das Display stellte vier Graustufen dar.", GAME_BOY, entities=["Game Boy"])
    add_estimate(category, mechanics, "Wie viele Spielmodi nennt Nintendo für die Switch: TV-, Tisch- und Handheld-Modus?", 3, "Spielmodi", "Nintendo beschreibt TV-, Tisch- und Handheld-Modus.", SWITCH, entities=["Nintendo Switch"])
    add_estimate(category, mechanics, "Wie viele heilige Eigenschaften verkörpern die drei Zelda-Triforce-Teile zusammen?", 3, "Eigenschaften", "Kraft, Weisheit und Mut bilden die drei Eigenschaften.", ZELDA, entities=["Triforce"])


CHRISTIANITY = source(
    reference("Encyclopaedia Britannica: Christianity", "https://www.britannica.com/topic/Christianity")
)
JUDAISM = source(
    reference(
        "United States Holocaust Memorial Museum: Introduction to Judaism",
        "https://encyclopedia.ushmm.org/content/en/article/introduction-to-judaism",
    )
)
ISLAM = source(
    reference("Encyclopaedia Britannica: Islam", "https://www.britannica.com/topic/Islam")
)
ISLAM_TEXTS = source(
    reference("ReligionFacts: Islamic sacred texts", "https://religionfacts.com/islam/texts")
)
HINDUISM = source(
    reference("Encyclopaedia Britannica: Hinduism", "https://www.britannica.com/topic/Hinduism")
)
ASHRAMA = source(
    reference(
        "New World Encyclopedia: Ashrama",
        "https://www.newworldencyclopedia.org/entry/Ashram",
    )
)
HINDU_TEXTS = source(
    reference("ReligionFacts: The Vedas", "https://religionfacts.com/hinduism/texts/vedas")
)
BUDDHISM = source(
    reference("Encyclopaedia Britannica: Buddhism", "https://www.britannica.com/topic/Buddhism")
)
SIKHISM = source(
    reference("Encyclopaedia Britannica: Sikhism", "https://www.britannica.com/topic/Sikhism")
)
WORLD_RELIGIONS = source(
    reference(
        "Scottish Qualifications Authority: World Religions",
        "https://www.sqa.org.uk/sqa/files_ccc/N2USNRMEWorldReligions.pdf",
    )
)
SHINTO_TEXTS = source(
    reference("ReligionFacts: Shinto texts", "https://religionfacts.com/shinto/texts")
)
TAO_TEXTS = source(
    reference("ReligionFacts: Taoist texts", "https://religionfacts.com/taoism/texts")
)
ZOROASTRIAN_TEXTS = source(
    reference("ReligionFacts: Zoroastrian texts", "https://religionfacts.com/zoroastrianism/texts")
)
VATICAN = source(
    reference("UNESCO: Vatican City", "https://whc.unesco.org/en/list/286")
)
BODH_GAYA = source(
    reference("UNESCO: Mahabodhi Temple Complex at Bodh Gaya", "https://whc.unesco.org/en/list/1056")
)
JERUSALEM = source(
    reference("UNESCO: Old City of Jerusalem and its Walls", "https://whc.unesco.org/en/list/148")
)


ROCK_HALL = source(
    reference("Rock & Roll Hall of Fame: Inductee classes", "https://rockhall.com/inductees/classes/")
)
OASIS = source(
    reference("Rock & Roll Hall of Fame: Oasis", "https://rockhall.com/inductees/oasis/")
)
GERMAN_MUSIC = source(
    reference(
        "Goethe-Institut: Neue Deutsche Welle",
        "https://www.goethe.de/ins/sk/de/m/kul/sup/deu/ndw.html",
    )
)
KRAFTWERK = source(
    reference(
        "Deutsche Welle: Four decades of German electronic music",
        "https://www.dw.com/en/machine-music-four-decades-of-german-electronic-and-dance-music/a-6151880",
    )
)
GERMAN_HISTORY_MUSIC = source(
    reference(
        "Haus der Geschichte: Hits & Hymnen",
        "https://www.hdg.de/presse/pressemitteilung-2021-03-11-hits-hymnen",
    )
)
BEETHOVEN = source(
    reference(
        "Encyclopaedia Britannica: Ludwig van Beethoven",
        "https://www.britannica.com/biography/Ludwig-van-Beethoven",
    )
)
VIVALDI = source(
    reference(
        "Encyclopaedia Britannica: The Four Seasons",
        "https://www.britannica.com/topic/The-Four-Seasons-by-Vivaldi",
    )
)
MOZART = source(
    reference(
        "Encyclopaedia Britannica: Wolfgang Amadeus Mozart",
        "https://www.britannica.com/biography/Wolfgang-Amadeus-Mozart",
    )
)
PREPARED_PIANO = source(
    reference(
        "Berliner Philharmoniker: What is a prepared piano?",
        "https://www.berliner-philharmoniker.de/en/stories/a-short-piano-lexicon/what-is-a-prepared-piano/",
    )
)
VIOLIN = source(
    reference("Encyclopaedia Britannica: Violin", "https://www.britannica.com/art/violin")
)
MUSIC_THEORY = source(
    reference("Encyclopaedia Britannica: Octave", "https://www.britannica.com/art/octave-music")
)


def add_music_questions() -> None:
    category = "music"
    rock = "Rock"
    german = "Deutsche Musikgeschichte"
    international = "Internationale Musikgeschichte"
    classical = "Klassische Musik"
    instruments = "Instrumente & Musiktheorie"

    add_mc(category, rock, "Wie heißt das 1994 erschienene Debütalbum von Oasis?", "Definitely Maybe", ["The Bends", "Parklife", "Urban Hymns"], "Oasis veröffentlichte 1994 das Debütalbum „Definitely Maybe“.", OASIS, entities=["Oasis", "Definitely Maybe"], genres=["Rock"], regions=["Großbritannien"], eras=["1990er"])
    add_mc(category, rock, "In welchem Jahr wurde Nirvana in die Rock & Roll Hall of Fame aufgenommen?", "2014", ["2001", "2009", "2019"], "Nirvana gehörte zur Hall-of-Fame-Klasse von 2014.", ROCK_HALL, entities=["Nirvana"], genres=["Rock", "Grunge"], regions=["USA"], eras=["2010er"])
    add_mc(category, german, "In welcher deutschen Stadt wurde Kraftwerk gegründet?", "Düsseldorf", ["Hamburg", "Leipzig", "München"], "Ralf Hütter und Florian Schneider gründeten Kraftwerk 1970 in Düsseldorf.", KRAFTWERK, entities=["Kraftwerk"], genres=["Elektronische Musik"], regions=["Deutschland", "Düsseldorf"], eras=["1970er"])
    add_mc(category, german, "Welcher Bewegung wird Nenas „99 Luftballons“ zugeordnet?", "Neue Deutsche Welle", ["Hamburger Schule", "Krautrock", "Neue Deutsche Härte"], "Nena wurde zu einem der international bekanntesten Acts der Neuen Deutschen Welle.", GERMAN_MUSIC, entities=["Nena", "99 Luftballons"], genres=["Neue Deutsche Welle"], regions=["Deutschland"], eras=["1980er"])
    add_mc(category, international, "In welcher Hall-of-Fame-Klasse wurde Bob Marley aufgenommen?", "1994", ["1986", "2002", "2010"], "Bob Marley steht in der Rock-&-Roll-Hall-of-Fame-Klasse von 1994.", ROCK_HALL, entities=["Bob Marley"], genres=["Reggae"], regions=["Jamaika"], eras=["1990er"])
    add_mc(category, classical, "Welcher Komponist schrieb den Zyklus „Die vier Jahreszeiten“?", "Antonio Vivaldi", ["Johann Sebastian Bach", "Joseph Haydn", "Franz Schubert"], "„Die vier Jahreszeiten“ stammen von Antonio Vivaldi.", VIVALDI, entities=["Antonio Vivaldi", "Die vier Jahreszeiten"], genres=["Barock"], regions=["Italien"])
    add_mc(category, instruments, "Wer gilt als Vater des präparierten Klaviers?", "John Cage", ["Claude Debussy", "Gustav Mahler", "Niccolò Paganini"], "John Cage entwickelte die Technik mit Gegenständen zwischen den Klaviersaiten entscheidend weiter.", PREPARED_PIANO, entities=["John Cage", "präpariertes Klavier"], genres=["Neue Musik"], regions=["USA"], eras=["20. Jahrhundert"])

    add_tf(category, rock, "Led Zeppelin wurde 1995 in die Rock & Roll Hall of Fame aufgenommen.", True, "Led Zeppelin gehört zur Klasse von 1995.", ROCK_HALL, entities=["Led Zeppelin"], genres=["Rock"], regions=["Großbritannien"], eras=["1990er"])
    add_tf(category, rock, "Radiohead wurde bereits in der ersten Hall-of-Fame-Klasse von 1986 aufgenommen.", False, "Radiohead wurde 2019 aufgenommen; die erste Klasse stammt von 1986.", ROCK_HALL, entities=["Radiohead"], genres=["Rock"], regions=["Großbritannien"])
    add_tf(category, german, "Kraftwerk wurde 1970 in Düsseldorf gegründet.", True, "Die Gründung durch Ralf Hütter und Florian Schneider erfolgte 1970 in Düsseldorf.", KRAFTWERK, entities=["Kraftwerk"], genres=["Elektronische Musik"], regions=["Deutschland", "Düsseldorf"], eras=["1970er"])
    add_tf(category, german, "„99 Luftballons“ wurde in den 1960er-Jahren veröffentlicht.", False, "Der Song stammt aus dem Jahr 1983 und gehört zur Ära der Neuen Deutschen Welle.", GERMAN_MUSIC, entities=["Nena", "99 Luftballons"], genres=["Neue Deutsche Welle"], regions=["Deutschland"], eras=["1980er"])
    add_tf(category, international, "ABBA gehört zur Rock-&-Roll-Hall-of-Fame-Klasse von 2010.", True, "ABBA wurde 2010 aufgenommen.", ROCK_HALL, entities=["ABBA"], genres=["Pop"], regions=["Schweden"], eras=["2010er"])
    add_tf(category, classical, "Beethoven vollendete neun Sinfonien.", True, "Beethovens nummerierter Sinfoniezyklus umfasst neun Werke.", BEETHOVEN, entities=["Ludwig van Beethoven"], genres=["Klassik", "Romantik"], regions=["Deutschland", "Österreich"])
    add_tf(category, classical, "Vivaldis „Vier Jahreszeiten“ bestehen aus vier Violinkonzerten.", True, "Jede Jahreszeit wird durch ein eigenes Violinkonzert dargestellt.", VIVALDI, entities=["Antonio Vivaldi", "Die vier Jahreszeiten"], genres=["Barock"], regions=["Italien"])
    add_tf(category, instruments, "Bei einem „präparierten Klavier“ verändern Schrauben, Filz oder andere Gegenstände an den Saiten den Klang.", True, "Schrauben, Filz, Holz oder andere Materialien verändern das Schwingungsverhalten der Saiten.", PREPARED_PIANO, entities=["präpariertes Klavier"], genres=["Neue Musik"])
    add_tf(category, instruments, "Eine moderne Standardvioline besitzt normalerweise sechs Saiten.", False, "Die Standardvioline besitzt vier Saiten.", VIOLIN, entities=["Violine"])

    add_match(category, rock, "Ordne die Rockband ihrem Hall-of-Fame-Aufnahmejahr zu.", [("Nirvana", "2014"), ("Pearl Jam", "2017"), ("Radiohead", "2019")], ROCK_HALL, entities=["Nirvana", "Pearl Jam", "Radiohead"], genres=["Rock"], eras=["2010er"])
    add_match(category, german, "Ordne den deutschen Act dem bekannten Titel zu.", [("Nena", "99 Luftballons"), ("Scorpions", "Wind of Change"), ("Kraftwerk", "Das Model")], source(*GERMAN_MUSIC["references"], *GERMAN_HISTORY_MUSIC["references"], *KRAFTWERK["references"]), entities=["Nena", "Scorpions", "Kraftwerk"], regions=["Deutschland"])
    add_match(category, german, "Ordne den Act seinem Schwerpunkt in der deutschen Popgeschichte zu.", [("Kraftwerk", "elektronische Pionierarbeit"), ("Nena", "Neue Deutsche Welle"), ("Scorpions", "internationaler Hard Rock")], source(*KRAFTWERK["references"], *GERMAN_MUSIC["references"], *GERMAN_HISTORY_MUSIC["references"]), entities=["Kraftwerk", "Nena", "Scorpions"], regions=["Deutschland"])
    add_match(category, international, "Ordne den Act seinem Hall-of-Fame-Aufnahmejahr zu.", [("Bob Marley", "1994"), ("ABBA", "2010"), ("Tina Turner", "2021 als Solokünstlerin")], ROCK_HALL, entities=["Bob Marley", "ABBA", "Tina Turner"], regions=["international"])
    add_match(category, classical, "Ordne den Komponisten dem Werk zu.", [("Beethoven", "9. Sinfonie"), ("Mozart", "Die Zauberflöte"), ("Vivaldi", "Die vier Jahreszeiten")], source(*BEETHOVEN["references"], *MOZART["references"], *VIVALDI["references"]), entities=["Beethoven", "Mozart", "Vivaldi"], genres=["Klassische Musik"])
    add_match(category, instruments, "Ordne das Instrument seiner Instrumentenfamilie zu.", [("Violine", "Streichinstrument"), ("Trompete", "Blechblasinstrument"), ("Klavier", "Tasteninstrument")], source(*VIOLIN["references"], *PREPARED_PIANO["references"]), entities=["Violine", "Trompete", "Klavier"])

    add_order(category, rock, "Ordne diese Rock-Acts nach ihrer Aufnahme in die Hall of Fame.", ["Led Zeppelin", "Nirvana", "Pearl Jam", "Radiohead"], "Led Zeppelin (1995) → Nirvana (2014) → Pearl Jam (2017) → Radiohead (2019).", ROCK_HALL, entities=["Led Zeppelin", "Nirvana", "Pearl Jam", "Radiohead"], genres=["Rock"])
    add_order(category, rock, "Ordne diese Oasis-Ereignisse chronologisch.", ["Bandgründung in Manchester", "Debütalbum Definitely Maybe", "Album Morning Glory", "Hall-of-Fame-Aufnahme"], "Gründung (1991) → Definitely Maybe (1994) → Morning Glory (1995) → Aufnahme (2026).", OASIS, entities=["Oasis"], genres=["Rock"], regions=["Großbritannien"])
    add_order(category, german, "Ordne diese Stationen deutscher Popgeschichte.", ["Gründung von Kraftwerk", "Joachim Witt: Der Goldene Reiter", "Nena: 99 Luftballons", "Scorpions: Wind of Change"], "Kraftwerk (1970) → Der Goldene Reiter (1980) → 99 Luftballons (1983) → Wind of Change (1990).", source(*KRAFTWERK["references"], *GERMAN_MUSIC["references"], *GERMAN_HISTORY_MUSIC["references"]), entities=["Kraftwerk", "Joachim Witt", "Nena", "Scorpions"], regions=["Deutschland"])
    add_order(category, german, "Ordne diese deutschen beziehungsweise deutschsprachigen Popphänomene grob chronologisch.", ["Krautrock und frühe Elektronik", "Neue Deutsche Welle", "Neue Deutsche Härte", "deutscher Popboom der 2010er"], "Frühe Elektronik/Krautrock → NDW → Neue Deutsche Härte → Popboom der 2010er.", GERMAN_MUSIC, entities=["Krautrock", "Neue Deutsche Welle", "Neue Deutsche Härte"], regions=["Deutschland"])
    add_order(category, international, "Ordne diese Acts nach ihrem Hall-of-Fame-Aufnahmejahr.", ["Bob Marley", "Michael Jackson", "ABBA", "Tina Turner als Solokünstlerin"], "Bob Marley (1994) → Michael Jackson (2001) → ABBA (2010) → Tina Turner (2021).", ROCK_HALL, entities=["Bob Marley", "Michael Jackson", "ABBA", "Tina Turner"])
    add_order(category, classical, "Ordne diese Komponisten nach ihrem Geburtsjahr.", ["Antonio Vivaldi", "Johann Sebastian Bach", "Wolfgang Amadeus Mozart", "Ludwig van Beethoven"], "Vivaldi (1678) → Bach (1685) → Mozart (1756) → Beethoven (1770).", source(*VIVALDI["references"], *MOZART["references"], *BEETHOVEN["references"]), entities=["Vivaldi", "Bach", "Mozart", "Beethoven"], genres=["Klassische Musik"])
    add_order(category, classical, "Ordne diese musikalischen Epochen chronologisch.", ["Barock", "Klassik", "Romantik", "Moderne"], "Barock → Klassik → Romantik → Moderne.", BEETHOVEN, genres=["Klassische Musik"])
    add_order(category, instruments, "Ordne diese Tonabstände von klein nach groß.", ["Halbton", "Ganzton", "Quarte", "Oktave"], "Halbton → Ganzton → Quarte → Oktave.", MUSIC_THEORY, entities=["Intervall", "Oktave"])

    add_estimate(category, rock, "In welchem Jahr erschien Oasis' Debütalbum „Definitely Maybe“?", 1994, "Jahr", "Das Album erschien 1994.", OASIS, entities=["Oasis", "Definitely Maybe"], genres=["Rock"], regions=["Großbritannien"])
    add_estimate(category, rock, "Wie viele Jahre lagen zwischen der ersten Hall-of-Fame-Klasse von 1986 und Nirvanas Aufnahme 2014?", 28, "Jahre", "Von 1986 bis 2014 sind es 28 Jahre.", ROCK_HALL, entities=["Nirvana", "Rock & Roll Hall of Fame"], genres=["Rock", "Grunge"], regions=["USA"])
    add_estimate(category, german, "In welchem Jahr wurde Kraftwerk gegründet?", 1970, "Jahr", "Kraftwerk wurde 1970 in Düsseldorf gegründet.", KRAFTWERK, entities=["Kraftwerk"], regions=["Deutschland"], eras=["1970er"])
    add_estimate(category, german, "In welchem Jahr erschien Nenas „99 Luftballons“?", 1983, "Jahr", "Der Song erschien 1983.", GERMAN_MUSIC, entities=["Nena", "99 Luftballons"], regions=["Deutschland"], eras=["1980er"])
    add_estimate(category, classical, "Wie viele nummerierte Sinfonien vollendete Beethoven?", 9, "Sinfonien", "Beethoven vollendete neun nummerierte Sinfonien.", BEETHOVEN, entities=["Ludwig van Beethoven"], genres=["Klassische Musik"])
    add_estimate(category, classical, "Aus wie vielen Violinkonzerten besteht Vivaldis Zyklus „Die vier Jahreszeiten“?", 4, "Konzerte", "Jede der vier Jahreszeiten besitzt ein eigenes Konzert.", VIVALDI, entities=["Antonio Vivaldi", "Die vier Jahreszeiten"], genres=["Barock"])
    add_estimate(category, instruments, "Wie viele Saiten besitzt eine Standardvioline?", 4, "Saiten", "Eine Standardvioline hat vier Saiten.", VIOLIN, entities=["Violine"])
    add_estimate(category, instruments, "Wie viele gleich große Halbtonschritte umfasst eine Oktave im westlichen chromatischen Tonsystem?", 12, "Halbtonschritte", "Die Oktave wird chromatisch in zwölf Halbtonschritte geteilt.", MUSIC_THEORY, entities=["Oktave"])


OLYMPIC_FACTS = source(
    reference(
        "IOC Olympic Studies Centre: Olympic Games facts and figures",
        "https://library.olympics.com/digitalCollection/DigitalCollectionAttachmentDownloadHandler.ashx?documentId=3703315&parentDocumentId=172552&skipCopyright=true&skipWatermark=true",
    )
)
OLYMPIC_WINTER = source(
    reference(
        "IOC: 100 years of the Olympic Winter Games",
        "https://newsroom.olympics.com/record/1298",
    )
)
OLYMPIC_POOLS = source(
    reference(
        "IOC Olympic Studies Centre: Olympic swimming pools",
        "https://library.olympics.com/default/digitalCollection/DigitalCollectionAttachmentDownloadHandler.ashx?documentId=619389&parentDocumentId=619388&skipCopyright=true&skipWatermark=true",
    )
)
HURDLES = source(
    reference(
        "World Athletics: 400 metres hurdles",
        "https://worldathletics.org/disciplines/sprints/400-metres-hurdles",
    )
)
FOOTBALL_PLAYERS = source(
    reference("IFAB Law 3: The Players", "https://theifab.com/laws/latest/the-players/")
)
FOOTBALL_TIME = source(
    reference(
        "IFAB Law 7: The Duration of the Match",
        "https://www.theifab.com/laws/latest/the-duration-of-the-match/",
    )
)
BASKETBALL = source(
    reference("FIBA: Official Basketball Rules", "https://refereeing.fiba.basketball/en/rules")
)
HANDBALL = source(
    reference(
        "IHF: The evolution of indoor handball",
        "https://www.ihf.info/media-center/news/how-did-we-get-here-evolution-indoor-handball",
    )
)
TENNIS = source(
    reference(
        "International Tennis Federation: Rules and regulations",
        "https://www.itftennis.com/en/about-us/governance/rules-and-regulations/",
    )
)
MOTORSPORT = source(
    reference(
        "FIA: Formula One regulations and race flags",
        "https://www.fia.com/sites/default/files/final_din_a4_media_kit_english_26.07.2016.pdf",
    )
)


def add_sport_questions() -> None:
    category = "sport"
    athletics = "Leichtathletik & Ausdauer"
    team = "Mannschafts- & Ballsport"
    water_winter_motor = "Wasser-, Winter- & Motorsport"
    rules = "Regeln & Ausrüstung"
    history = "Olympische Geschichte & Meilensteine"

    add_mc(category, athletics, "Wie viele Hürden stehen in einem 400-Meter-Hürdenlauf pro Bahn?", "10", ["8", "12", "14"], "Beim 400-Meter-Hürdenlauf werden zehn gleichmäßig verteilte Hürden überquert.", HURDLES, entities=["400-Meter-Hürdenlauf"], genres=["Leichtathletik"])
    add_mc(category, team, "Wie viele Spieler darf eine Fußballmannschaft höchstens gleichzeitig auf dem Feld haben?", "11", ["9", "10", "12"], "Nach IFAB-Regel 3 spielen höchstens elf Personen je Mannschaft, darunter ein Torwart.", FOOTBALL_PLAYERS, entities=["Fußball"], genres=["Mannschaftssport"])
    add_mc(category, team, "Wie viele Spieler einer Basketballmannschaft stehen regulär gleichzeitig auf dem Feld?", "5", ["4", "6", "7"], "Im Basketball stehen fünf Spieler je Mannschaft gleichzeitig auf dem Feld.", BASKETBALL, entities=["Basketball"], genres=["Mannschaftssport"])
    add_mc(category, water_winter_motor, "Wie lang ist ein olympisches Wettkampfbecken normalerweise?", "50 Meter", ["25 Meter", "40 Meter", "75 Meter"], "Olympische Wettkampfbecken besitzen eine Länge von 50 Metern.", OLYMPIC_POOLS, entities=["Schwimmen"], genres=["Wassersport"])
    add_mc(category, rules, "Welche Organisation verwaltet die internationalen Tennisregeln?", "International Tennis Federation", ["FIFA", "FIBA", "World Rugby"], "Die ITF ist Hüterin der Tennisregeln.", TENNIS, entities=["Tennis", "ITF"])
    add_mc(category, rules, "Wie viele Schritte darf ein Feldspieler im Handball mit dem Ball höchstens machen, ohne zu dribbeln?", "3", ["2", "4", "5"], "Im Handball sind ohne Dribbling höchstens drei Schritte erlaubt.", HANDBALL, entities=["Handball"])
    add_mc(category, history, "Wer gewann 1896 den Dreisprung und wurde damit erster Olympiasieger der Neuzeit?", "James Connolly", ["Spyridon Louis", "Paavo Nurmi", "Carl Lewis"], "James Connolly gewann am 6. April 1896 den Dreisprung.", OLYMPIC_FACTS, entities=["James Connolly"], eras=["1896"])
    add_mc(category, history, "Wo fanden 1924 die später als erste Olympische Winterspiele anerkannten Wettbewerbe statt?", "Chamonix", ["St. Moritz", "Oslo", "Innsbruck"], "Die Wintersportwoche von Chamonix 1924 wurde später als erste Olympische Winterspiele anerkannt.", OLYMPIC_WINTER, entities=["Chamonix 1924"], eras=["1924"])

    add_tf(category, team, "Ein Fußballspiel darf nicht beginnen, wenn eine Mannschaft weniger als sieben Spieler hat.", True, "IFAB verlangt zum Beginn mindestens sieben Spieler pro Mannschaft.", FOOTBALL_PLAYERS, entities=["Fußball"])
    add_tf(category, water_winter_motor, "Ein olympisches Schwimmbecken ist normalerweise 50 Meter lang.", True, "Die dokumentierten olympischen Wettkampfbecken sind 50 Meter lang.", OLYMPIC_POOLS, entities=["Schwimmen"], genres=["Wassersport"])
    add_tf(category, water_winter_motor, "Die schwarz-weiß karierte Flagge kennzeichnet im Motorsport das Rennende.", True, "Die FIA weist der karierten Flagge das Ende des Rennens zu.", MOTORSPORT, entities=["Motorsport", "karierte Flagge"], genres=["Motorsport"])
    add_tf(category, rules, "Ein Basketballspiel nach FIBA-Regeln ist in vier Viertel gegliedert.", True, "FIBA-Basketball wird in vier Vierteln gespielt.", BASKETBALL, entities=["Basketball"])
    add_tf(category, rules, "Ein Handball-Feldspieler darf den Ball ohne Dribbling beliebig viele Schritte tragen.", False, "Ohne Dribbling sind höchstens drei Schritte erlaubt.", HANDBALL, entities=["Handball"])
    add_tf(category, history, "Bei den ersten Olympischen Spielen der Neuzeit 1896 nahmen ausschließlich Männer teil.", True, "Für Athen 1896 nennt das IOC 241 Athleten und keine Athletinnen.", OLYMPIC_FACTS, entities=["Athen 1896"])
    add_tf(category, history, "Bei den Olympischen Spielen 1900 in Paris nahmen bereits Frauen teil.", True, "Das IOC verzeichnet für Paris 1900 insgesamt 22 Athletinnen.", OLYMPIC_FACTS, entities=["Paris 1900"])
    add_tf(category, history, "An den Winterspielen von Chamonix 1924 nahmen mehr als 100 Nationen teil.", False, "Es waren 16 nationale Mannschaften beziehungsweise NOKs vertreten.", OLYMPIC_WINTER, entities=["Chamonix 1924"])

    add_match(category, team, "Ordne die Sportart der regulären Zahl gleichzeitig eingesetzter Spieler je Mannschaft zu.", [("Fußball", "11"), ("Basketball", "5"), ("Handball", "7")], source(*FOOTBALL_PLAYERS["references"], *BASKETBALL["references"], *HANDBALL["references"]), entities=["Fußball", "Basketball", "Handball"])
    add_match(category, water_winter_motor, "Ordne dem Sport die passende Wettkampfumgebung beziehungsweise Anzeige zu.", [("Schwimmen", "50-Meter-Wettkampfbecken"), ("Formel-Rennsport", "karierte Zielflagge"), ("Skispringen", "Schanze")], source(*OLYMPIC_POOLS["references"], *MOTORSPORT["references"], *OLYMPIC_WINTER["references"]), entities=["Schwimmen", "Motorsport", "Skispringen"])
    add_match(category, rules, "Ordne die Regelorganisation der Sportart zu.", [("IFAB", "Fußball"), ("ITF", "Tennis"), ("FIBA", "Basketball")], source(*FOOTBALL_PLAYERS["references"], *TENNIS["references"], *BASKETBALL["references"]), entities=["IFAB", "ITF", "FIBA"])
    add_match(category, rules, "Ordne die Regel der Sportart zu.", [("zwei Halbzeiten zu 45 Minuten", "Fußball"), ("vier Viertel", "Basketball"), ("höchstens drei Schritte ohne Dribbling", "Handball")], source(*FOOTBALL_TIME["references"], *BASKETBALL["references"], *HANDBALL["references"]), entities=["Fußball", "Basketball", "Handball"])
    add_match(category, history, "Ordne den Austragungsort dem Jahr zu.", [("Athen", "1896"), ("Paris", "1900"), ("Chamonix", "1924")], source(*OLYMPIC_FACTS["references"], *OLYMPIC_WINTER["references"]), entities=["Athen 1896", "Paris 1900", "Chamonix 1924"])
    add_match(category, history, "Ordne die olympische Persönlichkeit ihrer Leistung zu.", [("James Connolly", "erster Olympiasieger der Neuzeit"), ("Spyridon Louis", "Marathonsieger 1896"), ("König Georg I.", "Eröffnung der Spiele 1896")], OLYMPIC_FACTS, entities=["James Connolly", "Spyridon Louis", "Georg I."])
    add_match(category, history, "Ordne den frühen Olympischen Spielen die dokumentierte Teilnehmerzahl zu.", [("Athen 1896", "241"), ("Paris 1900", "997"), ("Chamonix 1924", "258")], source(*OLYMPIC_FACTS["references"], *OLYMPIC_WINTER["references"]), entities=["Athen 1896", "Paris 1900", "Chamonix 1924"])


RETAG_EXISTING = {
    # Gaming: 1 history, 2 hardware, 4 studios, 0 worlds, 1 mechanics.
    "or143": "Geschichte & Meilensteine",
    "or16": "Konsolen & Hardware",
    "or148": "Konsolen & Hardware",
    "mc146": "Studios & Entwicklung",
    "tf145": "Studios & Entwicklung",
    "tf148": "Studios & Entwicklung",
    "ma143": "Studios & Entwicklung",
    "tf17": "Spielmechanik & Begriffe",
    # Music: 1 rock, 0 German, 6 international, 2 classical, 3 theory/instruments.
    "mc08": "Rock",
    "tf143": "Internationale Musikgeschichte",
    "mc147": "Internationale Musikgeschichte",
    "ma36": "Internationale Musikgeschichte",
    "ma144": "Internationale Musikgeschichte",
    "ma148": "Internationale Musikgeschichte",
    "or145": "Internationale Musikgeschichte",
    "ma24": "Klassische Musik",
    "or23": "Klassische Musik",
    "mc33": "Instrumente & Musiktheorie",
    "es03": "Instrumente & Musiktheorie",
    "es30": "Instrumente & Musiktheorie",
    # Sport: ten comparisons, seven athletics, four team, four water/winter/motor, two rules.
    **{f"or{number}": "Sportvergleiche" for number in range(131, 141)},
    "es134": "Leichtathletik & Ausdauer",
    "es136": "Leichtathletik & Ausdauer",
    "es137": "Leichtathletik & Ausdauer",
    "es138": "Leichtathletik & Ausdauer",
    "es139": "Leichtathletik & Ausdauer",
    "es140": "Leichtathletik & Ausdauer",
    "es13": "Leichtathletik & Ausdauer",
    "es131": "Mannschafts- & Ballsport",
    "es133": "Mannschafts- & Ballsport",
    "es32": "Mannschafts- & Ballsport",
    "es36": "Mannschafts- & Ballsport",
    "es132": "Wasser-, Winter- & Motorsport",
    "es135": "Wasser-, Winter- & Motorsport",
    "es05": "Wasser-, Winter- & Motorsport",
    "es40": "Wasser-, Winter- & Motorsport",
    "ma15": "Regeln & Ausrüstung",
    "ma27": "Regeln & Ausrüstung",
}

EXPECTED_ADDITIONS = {
    "gaming": {
        "multiple_choice": 9,
        "true_false": 7,
        "match": 9,
        "order": 7,
        "estimate": 10,
    },
    "music": {
        "multiple_choice": 7,
        "true_false": 9,
        "match": 6,
        "order": 8,
        "estimate": 8,
    },
    "sport": {
        "multiple_choice": 8,
        "true_false": 8,
        "match": 7,
        "order": 0,
        "estimate": 0,
    },
}

EXPECTED_SUBTOPICS = {
    "gaming": {
        "Geschichte & Meilensteine": 10,
        "Konsolen & Hardware": 10,
        "Studios & Entwicklung": 10,
        "Spielwelten & Figuren": 10,
        "Spielmechanik & Begriffe": 10,
    },
    "music": {
        "Rock": 10,
        "Deutsche Musikgeschichte": 10,
        "Internationale Musikgeschichte": 10,
        "Klassische Musik": 10,
        "Instrumente & Musiktheorie": 10,
    },
    "sport": {
        "Sportvergleiche": 10,
        "Leichtathletik & Ausdauer": 8,
        "Mannschafts- & Ballsport": 8,
        "Wasser-, Winter- & Motorsport": 8,
        "Regeln & Ausrüstung": 8,
        "Olympische Geschichte & Meilensteine": 8,
    },
}


def file_path(question_type: str, category: str) -> Path:
    return (
        LIBRARY
        / TYPE_DIRS[question_type]
        / CATEGORY_DIRS[category]
        / "fragen.json"
    )


def numeric_id(question: dict[str, Any]) -> int:
    return int(re.search(r"\d+", question["id"]).group())


def build() -> None:
    add_gaming_questions()
    add_music_questions()
    add_sport_questions()


def validate_new_questions() -> None:
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    ids: set[str] = set()
    prompts: set[str] = set()
    for (question_type, category), questions in new_questions.items():
        counts[category][question_type] += len(questions)
        for question in questions:
            if question["id"] in ids:
                raise RuntimeError(f"Doppelte neue ID: {question['id']}")
            ids.add(question["id"])
            normalized_prompt = " ".join(question["prompt"].casefold().split())
            if normalized_prompt in prompts:
                raise RuntimeError(f"Doppelte neue Frage: {question['prompt']}")
            prompts.add(normalized_prompt)
            if question["source"].get("status") != "verified":
                raise RuntimeError(f"Neue Frage ohne geprüften Quellenstatus: {question['id']}")
            references = question["source"].get("references", [])
            if not references or any(
                not item.get("url", "").startswith("https://") for item in references
            ):
                raise RuntimeError(f"Neue Frage ohne HTTPS-Quelle: {question['id']}")

    actual = {
        category: {question_type: counts[category][question_type] for question_type in PREFIXES}
        for category in EXPECTED_ADDITIONS
    }
    if actual != EXPECTED_ADDITIONS:
        raise RuntimeError(f"Unerwartete Verteilung der neuen Fragen: {actual}")
    if len(ids) != 103:
        raise RuntimeError(f"Erwartet: 103 neue Fragen, erhalten: {len(ids)}")


def apply() -> None:
    existing_ids: set[str] = set()
    existing_by_id: dict[str, dict[str, Any]] = {}
    all_files: dict[tuple[str, str], list[dict[str, Any]]] = {}

    for question_type in PREFIXES:
        for category in CATEGORY_DIRS:
            path = file_path(question_type, category)
            questions = json.loads(path.read_text(encoding="utf-8"))
            all_files[(question_type, category)] = questions
            for question in questions:
                question_id = question["id"]
                if question_id in existing_ids:
                    raise RuntimeError(f"Doppelte vorhandene ID: {question_id}")
                existing_ids.add(question_id)
                existing_by_id[question_id] = question

    collisions = existing_ids & {
        question["id"] for questions in new_questions.values() for question in questions
    }
    if collisions:
        raise RuntimeError(f"Neue IDs sind bereits vorhanden: {sorted(collisions)}")

    missing_retags = set(RETAG_EXISTING) - set(existing_by_id)
    if missing_retags:
        raise RuntimeError(f"Fragen zum Neuverschlagworten fehlen: {sorted(missing_retags)}")

    for question_id, topic in RETAG_EXISTING.items():
        question = existing_by_id[question_id]
        category = question["primary_category"]
        question["subtopic"] = topic
        question.setdefault("tags", {})["topics"] = [topic]
        question["subject_keys"] = [
            key
            for key in question.get("subject_keys", [])
            if not key.startswith(f"topic:{category}:")
        ]
        question["subject_keys"].append(f"topic:{category}:{slug(topic)}")

    for key, questions in new_questions.items():
        all_files[key].extend(questions)

    target_questions: list[dict[str, Any]] = []
    for key, questions in all_files.items():
        questions.sort(key=numeric_id)
        target_questions.extend(questions)

    category_counts = Counter(
        question["primary_category"] for question in target_questions
    )
    for category in EXPECTED_ADDITIONS:
        if category_counts[category] != 50:
            raise RuntimeError(
                f"{category} hat {category_counts[category]} statt 50 Fragen"
            )

    subtopic_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for question in target_questions:
        category = question["primary_category"]
        if category in EXPECTED_SUBTOPICS:
            subtopic_counts[category][question["subtopic"]] += 1
    actual_subtopics = {
        category: dict(subtopic_counts[category]) for category in EXPECTED_SUBTOPICS
    }
    if actual_subtopics != EXPECTED_SUBTOPICS:
        raise RuntimeError(
            "Unterthemen sind nicht wie geplant verteilt: "
            + json.dumps(actual_subtopics, ensure_ascii=False, sort_keys=True)
        )

    for key, questions in all_files.items():
        file_path(*key).write_text(
            json.dumps(questions, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    print("103 Fragen ergänzt; Gaming, Musik und Sport wurden gezielt erweitert.")


def _retired_main() -> None:
    build()
    validate_new_questions()
    print(
        json.dumps(
            {
                category: {
                    question_type: len(new_questions[(question_type, category)])
                    for question_type in PREFIXES
                }
                for category in EXPECTED_ADDITIONS
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    if "--apply" in sys.argv:
        apply()
    else:
        print("Trockenlauf erfolgreich. Mit --apply werden die JSON-Dateien ergänzt.")


def main() -> None:
    raise SystemExit(
        "Stillgelegt: Kategorien sind keine Mindestquoten und keine Speicherordner mehr."
    )


if __name__ == "__main__":
    main()

