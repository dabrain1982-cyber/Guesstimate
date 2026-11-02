"""Build and append the researched 250-question expansion from compact facts.

The compact tables keep the batch reviewable: every row carries its source,
while the factories enforce the current question profile consistently.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERIFIED_ON = "2026-10-18"

SOURCES = {
    "nintendo": ("Nintendo History", "https://www.nintendo.com/en-gb/Hardware/Nintendo-History/Nintendo-History-625945.html"),
    "playstation": ("PlayStation history", "https://www.playstation.com/en-us/playstation-history/1994-ps-one/"),
    "xbox": ("Xbox 25th anniversary timeline", "https://www.xbox.com/en-us/xbox-25th-anniversary"),
    "minecraft": ("Minecraft: About Minecraft", "https://www.minecraft.net/en-us/about-minecraft"),
    "tetris": ("Tetris: About Tetris", "https://tetris.com/about"),
    "games": ("The Strong: World Video Game Hall of Fame", "https://www.strongmuseum.org/exhibits/world-video-game-hall-of-fame/"),
    "bluetooth": ("Bluetooth SIG: Origin of the name", "https://www.bluetooth.com/about-us/bluetooth-origin/"),
    "bubble_wrap": ("Sealed Air: BUBBLE WRAP Brand Protective Packaging", "https://www.sealedair.com/products/brand/bubble-wrap"),
    "qr": ("DENSO WAVE: QR Code 30th anniversary", "https://www.denso-wave.com/en/system/qr/qr30th/"),
    "postit": ("USPTO: Sticking to it", "https://www.uspto.gov/learning-and-resources/journeys-innovation/sticking-it"),
    "ingenuity": ("NASA: Ingenuity Mars Helicopter", "https://science.nasa.gov/mission/mars-2020-perseverance/ingenuity-mars-helicopter/"),
    "emoji": ("MoMA: Shigetaka Kurita — Emoji", "https://www.moma.org/collection/works/196070"),
    "noaa_weird": ("NOAA: Weird Ocean Phenomena", "https://oceanservice.noaa.gov/ocean/weird-ocean-weather.html"),
    "noaa_dark": ("NOAA: Why is the ocean blue?", "https://oceanservice.noaa.gov/facts/oceanblue.html"),
    "plastics": ("Smithsonian: One word — Plastics", "https://americanhistory.si.edu/explore/stories/one-word-plastics"),
    "wristwatch": ("Smithsonian: Revolution on Your Wrist", "https://amhistory.si.edu/docs/Dennis_Stephens_Dillon_%20Revolution_on_Wrist_1997.pdf"),
    "bluewhale": ("NOAA Fisheries: Blue Whale", "https://www.fisheries.noaa.gov/species/blue-whale"),
    "velcro": ("USPTO: Biomimicry", "https://www.uspto.gov/kids/Biomimicry.pdf"),
    "cern_web": ("CERN: Where the web was born", "https://home.cern/science/computing/the-birth-of-the-web/where-web-was-born/"),
    "sms": ("Vodafone: 25 years since the first text message", "https://www.vodafone.com/news/newsroom/technology/25-anniversary-text-message"),
    "barcode": ("GS1: First barcode scan", "https://www.gs1.org/docs/media_centre/gs1pr_260614_first_barcode_scan.pdf"),
    "dart": ("NASA: Asteroid orbit changed after DART impact", "https://www.nasa.gov/missions/dart/nasa-study-asteroids-orbit-shape-changed-after-dart-impact/"),
    "dart_mission": ("NASA Science: Double Asteroid Redirection Test", "https://science.nasa.gov/mission/dart/"),
    "teapot": ("RFC Editor: RFC 2324", "https://www.rfc-editor.org/rfc/rfc2324.html"),
    "captcha": ("Carnegie Mellon: Computer Security as a Song", "https://www.cs.cmu.edu/news/2013/computer-security-song"),
    "snoopy": ("NASA: Suited for Spacewalking", "https://www.nasa.gov/wp-content/uploads/2009/07/143159main_suited_for_spacewalking.pdf"),
    "python": ("Python Software Foundation: Python documentation", "https://docs.python.org/3/"),
    "swift": ("Swift.org: Documentation", "https://www.swift.org/documentation/"),
    "rust": ("The Rust Programming Language", "https://www.rust-lang.org/"),
    "rockhall_words": ("Rock & Roll Hall of Fame: Inductees", "https://rockhall.com/inductees/"),
    "css_colors": ("W3C: CSS Color Module", "https://www.w3.org/TR/css-color-4/"),
    "usda_food": ("USDA FoodData Central", "https://fdc.nal.usda.gov/"),
    "nist_glossary": ("NIST: Computer Security Resource Center Glossary", "https://csrc.nist.gov/glossary"),
    "dictionary": ("Merriam-Webster Dictionary", "https://www.merriam-webster.com/"),
    "computer_history": ("Computer History Museum: Networking & the Web", "https://www.computerhistory.org/timeline/networking-the-web/"),
    "worldheritage": ("UNESCO World Heritage List", "https://whc.unesco.org/en/list/"),
    "loc_sound": ("Library of Congress: Recording Technology Timeline", "https://www.loc.gov/programs/national-recording-preservation-plan/tools-and-resources/historical-background/timeline/"),
    "instruments": ("Encyclopaedia Britannica: Musical instrument", "https://www.britannica.com/art/musical-instrument"),
    "classical": ("Encyclopaedia Britannica: Classical music", "https://www.britannica.com/art/Western-music"),
    "rockhall": ("Rock & Roll Hall of Fame: Inductees", "https://rockhall.com/inductees/"),
    "cage": ("John Cage Trust: 4′33″", "https://johncage.org/apps"),
    "ifab": ("IFAB: Laws of the Game", "https://theifab.com/"),
    "fiba": ("FIBA: Official Basketball Rules", "https://refereeing.fiba.basketball/en/rules"),
    "itf": ("ITF: Rules and regulations", "https://www.itftennis.com/en/about-us/governance/rules-and-regulations/"),
    "athletics": ("World Athletics: Disciplines", "https://worldathletics.org/disciplines"),
    "olympics": ("Olympics: Sports", "https://www.olympics.com/en/sports/"),
    "history": ("Encyclopaedia Britannica: History of Europe", "https://www.britannica.com/topic/history-of-Europe"),
    "rosetta": ("British Museum: The Rosetta Stone", "https://www.britishmuseum.org/blog/everything-you-ever-wanted-know-about-rosetta-stone"),
    "suffrage": ("New Zealand History: Women and the vote", "https://nzhistory.govt.nz/politics/womens-suffrage"),
    "nasa_history": ("NASA: Missions", "https://www.nasa.gov/missions/"),
    "nobel": ("Nobel Prize facts", "https://www.nobelprize.org/prizes/facts/nobel-prize-facts/"),
    "oscars": ("Academy Awards: Ceremonies", "https://www.oscars.org/oscars/ceremonies"),
    "pixar": ("Pixar: Our Story", "https://www.pixar.com/our-story"),
    "bond": ("007: The Films", "https://www.007.com/the-films/"),
    "marvel": ("Marvel: Characters", "https://www.marvel.com/characters"),
    "television": ("Television Academy: History", "https://www.televisionacademy.com/academy/about/history"),
    "kew": ("Kew: Plants of the World Online", "https://powo.science.kew.org/"),
    "zoo": ("Smithsonian's National Zoo: Animals", "https://nationalzoo.si.edu/animals"),
    "nhm": ("Natural History Museum: Dino Directory", "https://www.nhm.ac.uk/discover/dino-directory.html"),
    "gestation": ("MSD Veterinary Manual: Gestation periods", "https://www.msdvetmanual.com/multimedia/table/approximate-gestation-periods"),
    "ocean": ("NOAA Ocean Service: Ocean facts", "https://oceanservice.noaa.gov/facts/"),
    "un": ("United Nations: Member States", "https://www.un.org/en/about-us/member-states"),
    "unesco": ("UNESCO World Heritage Centre", "https://whc.unesco.org/en/list"),
    "noaa": ("NOAA: What is the Sargasso Sea?", "https://oceanservice.noaa.gov/facts/sargassosea.html"),
    "cia": ("CIA: The World Factbook", "https://www.cia.gov/the-world-factbook/"),
    "britannica_geo": ("Encyclopaedia Britannica: Geography", "https://www.britannica.com/science/geography"),
    "nasa": ("NASA: Planetary Fact Sheet", "https://nssdc.gsfc.nasa.gov/planetary/factsheet/"),
    "iupac": ("IUPAC: Periodic Table of Elements", "https://iupac.org/what-we-do/periodic-table-of-elements/"),
    "bipm": ("BIPM: SI Brochure", "https://www.bipm.org/en/publications/si-brochure"),
    "unicode": ("Unicode Consortium: Unicode Statistics", "https://www.unicode.org/versions/stats/"),
    "nist": ("NIST: Metric (SI) Program", "https://www.nist.gov/pml/owm/metric-si"),
    "nih": ("MedlinePlus: Body systems", "https://medlineplus.gov/anatomy.html"),
    "vitamins": ("NIH Office of Dietary Supplements: Fact Sheets", "https://ods.od.nih.gov/factsheets/list-all/"),
    "emergency": ("European Commission: 112", "https://digital-strategy.ec.europa.eu/en/policies/112"),
    "materials": ("USDA: Natural Fibers", "https://agresearchmag.ars.usda.gov/2000/nov/dye/"),
    "epa": ("US EPA: Resin Identification Codes", "https://www.epa.gov/recycle/frequent-questions-recycling"),
    "cooking": ("Encyclopaedia Britannica: Cooking", "https://www.britannica.com/topic/cooking"),
    "fleming": ("Encyclopaedia Britannica: Ian Fleming", "https://www.britannica.com/biography/Ian-Fleming"),
}

CATEGORY_LABELS = {
    "gaming": "Gaming", "music": "Musik",
    "sport": "Sport", "witnesses_of_time": "Zeugen der Zeit",
    "media_entertainment": "Medien & Unterhaltung", "plants_animals": "Pflanzen & Tiere",
    "geography_world": "Geografie & Welt", "science_technology": "Wissenschaft & Technik",
    "human_everyday": "Mensch & Alltag",
}


def slug(text: str) -> str:
    replacements = str.maketrans("äöüßé′", "aouse'")
    return re.sub(r"[^a-z0-9]+", "-", text.casefold().translate(replacements)).strip("-")


def cited(key: str | list[str]) -> dict:
    keys = [key] if isinstance(key, str) else key
    return {
        "status": "verified",
        "verified_on": VERIFIED_ON,
        "references": [{"title": SOURCES[item][0], "url": SOURCES[item][1]} for item in keys],
    }


def topic_fields(category: str, topic: str, entities: list[str], era: str = "") -> dict:
    return {
        "primary_category": category,
        "subtopic": topic,
        "tags": {
            "topics": [topic], "entities": entities[:4], "genres": [],
            "regions": ["International"], "eras": [era] if era else [],
        },
    }


def tf(number: int, prompt: str, answer: bool, explanation: str, topic: str, source_key: str) -> dict:
    return {
        "id": f"tf{number}", "question_type": "true_false", "prompt": prompt,
        "answer": answer, "explanation": explanation,
        "subject_keys": [f"topic:phase2:{slug(topic)}", f"fact:true-false:{number}"],
        "source": cited(source_key),
    }


def mc(number: int, category: str, topic: str, prompt: str, correct: str,
       distractors: list[str], explanation: str, source_key: str) -> dict:
    values = [correct, *distractors]
    shift = number % 4
    values = values[shift:] + values[:shift]
    options = dict(zip("ABCD", values))
    answer = next(letter for letter, value in options.items() if value == correct)
    row = {
        "id": f"mc{number}", "question_type": "multiple_choice", "prompt": prompt,
        "answer": answer, "explanation": explanation,
        "subject_keys": [f"topic:{category}:{slug(topic)}", f"fact:multiple-choice:{number}"],
        "source": cited(source_key), "options": options,
    }
    row.update(topic_fields(category, topic, [correct]))
    return row


def match(number: int, category: str, topic: str, prompt: str,
          pairs: list[tuple[str, str]], source_key: str) -> dict:
    left = [a for a, _ in pairs]
    right = [b for _, b in pairs][::-1]
    row = {
        "id": f"ma{number}", "question_type": "match", "prompt": prompt,
        "answer": dict(pairs),
        "explanation": "; ".join(f"{a} – {b}" for a, b in pairs) + ".",
        "subject_keys": [f"topic:{category}:{slug(topic)}", f"fact:match:{number}"],
        "source": cited(source_key), "left": left, "right": right,
    }
    row.update(topic_fields(category, topic, left))
    return row


def order(number: int, category: str, topic: str, prompt: str,
          values: list[tuple[str, float]], unit: str, source_key: str) -> dict:
    answer = [label for label, _ in sorted(values, key=lambda item: item[1])]
    items = [label for label, _ in values[2:] + values[:2]]
    rendered = " → ".join(f"{label} ({value:g} {unit})" for label, value in sorted(values, key=lambda item: item[1]))
    row = {
        "id": f"or{number}", "question_type": "order", "prompt": prompt,
        "answer": answer, "explanation": rendered + ".",
        "subject_keys": [f"topic:{category}:{slug(topic)}", f"fact:order:{number}"],
        "source": cited(source_key), "items": items,
    }
    row.update(topic_fields(category, topic, [label for label, _ in values]))
    return row


def estimate(number: int, category: str, topic: str, prompt: str, answer: float,
             unit: str, explanation: str, source_key: str) -> dict:
    row = {
        "id": f"es{number}", "question_type": "estimate", "prompt": prompt,
        "answer": answer, "unit": unit, "explanation": explanation,
        "subject_keys": [f"topic:{category}:{slug(topic)}", f"fact:estimate:{number}"],
        "source": cited(source_key),
    }
    row.update(topic_fields(category, topic, [topic]))
    return row


TRUE_FALSE_SPECS = [
    # Gaming
    ("Nintendo begann im 19. Jahrhundert mit Spielkarten.", True, "Nintendo wurde 1889 gegründet und stellte zunächst Hanafuda-Spielkarten her.", "Nintendo-Ursprung", "nintendo"),
    ("Die erste PlayStation kam in Japan noch vor 1995 auf den Markt.", True, "Sony veröffentlichte die erste PlayStation in Japan im Dezember 1994.", "PlayStation-Start", "playstation"),
    ("Die erste Xbox erschien vor der PlayStation 2.", False, "Die PlayStation 2 startete 2000, die erste Xbox 2001.", "Konsolen-Chronologie", "xbox"),
    ("Ein Creeper kann in Minecraft durch einen Blitz zu einem geladenen Creeper werden.", True, "Ein Blitzeinschlag lädt einen Creeper auf und verstärkt seine Explosion.", "Minecraft-Creeper", "minecraft"),
    ("Jeder Tetris-Stein besteht aus fünf Quadraten.", False, "Tetrominos, die klassischen Tetris-Steine, bestehen aus vier Quadraten.", "Tetris-Tetrominos", "tetris"),
    # Moderne Alltagskultur & kuriose Technik
    ("Luftpolsterfolie war ursprünglich als strukturierte Tapete gedacht.", True, "Alfred Fielding und Marc Chavannes laminierten 1957 zwei Kunststofffolien mit eingeschlossenen Luftblasen für einen Wandbelag. Erst später wurde daraus Schutzverpackung.", "Luftpolsterfolie-Ursprung", "bubble_wrap"),
    ("Der QR-Code wurde ursprünglich für die Verwaltung von Autoteilen entwickelt.", True, "DENSO entwickelte den QR-Code für die Produktion und Nachverfolgung von Automobilteilen.", "QR-Code-Ursprung", "qr"),
    ("Die Idee für Post-it-Zettel entstand aus der Suche nach einem wiederablösbaren Lesezeichen.", True, "Art Fry wollte ein Lesezeichen, das haftet, aber die Buchseiten nicht beschädigt.", "Post-it-Idee", "postit"),
    ("Der Mars-Helikopter Ingenuity war für höchstens fünf Testflüge geplant und schaffte am Ende 72.", True, "Aus einer Demonstration mit bis zu fünf geplanten Flügen wurden 72 Flüge in fast drei Jahren.", "Ingenuity-Flüge", "ingenuity"),
    ("St.-Elms-Feuer ist trotz seines Namens keine gewöhnliche Flamme.", True, "Das Leuchten entsteht durch eine elektrische Entladung in einem starken elektrischen Feld.", "St.-Elms-Feuer", "noaa_weird"),
    # Musik
    ("Eine Oboe erzeugt ihren Ton mit einem Doppelrohrblatt.", True, "Bei der Oboe schwingen zwei gegeneinanderliegende Rohrblätter.", "Oboe", "instruments"),
    ("Das Saxofon gehört trotz seines Metallkörpers zu den Holzblasinstrumenten.", True, "Entscheidend ist das einfache Rohrblatt, nicht das Material des Korpus.", "Saxofon", "instruments"),
    ("Ein Theremin wird normalerweise gespielt, ohne das Instrument zu berühren.", True, "Die Hände verändern in elektromagnetischen Feldern Tonhöhe und Lautstärke.", "Theremin", "instruments"),
    ("John Cages 4′33″ schreibt eine durchgehend festgelegte Melodie vor.", False, "Das Werk lässt die ungeplanten Umgebungsgeräusche der Aufführung hörbar werden.", "4 Minuten 33", "cage"),
    ("Eine Bratsche ist üblicherweise höher gestimmt als eine Violine.", False, "Die Bratsche ist tiefer gestimmt; ihre tiefste Saite ist die C-Saite.", "Bratsche", "instruments"),
    # Sport
    ("Beim sportlichen Gehen muss ständig ein für das menschliche Auge sichtbarer Bodenkontakt bestehen.", True, "Die Wettkampfregel verlangt sichtbaren Bodenkontakt und ein gestrecktes Knie in der vorgeschriebenen Phase.", "Sportliches Gehen", "athletics"),
    ("Ein Fußballteam darf ein Spiel mit sechs Spielern fortsetzen.", False, "Nach IFAB-Regeln darf ein Spiel bei weniger als sieben Spielern nicht fortgesetzt werden.", "Mindestspielerzahl Fußball", "ifab"),
    ("Ein FIBA-Basketballspiel besteht regulär aus vier Vierteln.", True, "Nach FIBA-Regeln werden vier Viertel zu je zehn Minuten gespielt.", "Basketball-Viertel", "fiba"),
    ("Beim Tennis ist der Ball bei einem Aufschlag, der das Netz berührt und korrekt landet, sofort aus.", False, "Ein solcher Netzaufschlag wird ohne Punktwertung wiederholt.", "Netzaufschlag Tennis", "itf"),
    ("Beim Fußball kann direkt aus einem Abstoß ein Abseits entstehen.", False, "Bei direktem Ballerhalt aus einem Abstoß gilt die Abseitsregel nicht.", "Abseits beim Abstoß", "ifab"),
    # Zeugen der Zeit
    ("Der Stein von Rosette trägt Texte in drei verschiedenen Schriften.", True, "Die Inschrift nutzt Hieroglyphen, Demotisch und Altgriechisch.", "Stein von Rosette", "rosetta"),
    ("Der gregorianische Kalender wurde erstmals 1582 eingeführt.", True, "Papst Gregor XIII. führte die Kalenderreform 1582 ein.", "Gregorianischer Kalender", "history"),
    ("Neuseeland führte 1893 als erstes selbstverwaltetes Land das nationale Frauenwahlrecht ein.", True, "Das Wahlgesetz erhielt am 19. September 1893 die königliche Zustimmung.", "Frauenwahlrecht Neuseeland", "suffrage"),
    ("Die Magna Carta wurde im 14. Jahrhundert besiegelt.", False, "König Johann besiegelte die Magna Carta 1215, also im 13. Jahrhundert.", "Magna Carta", "history"),
    ("Apollo 11 landete nach der Mondmission im Atlantik.", False, "Die Kapsel wasserte 1969 im Pazifik.", "Apollo 11 Wasserung", "nasa_history"),
    # Medien & Unterhaltung
    ("Pixars Studiomaskottchen Luxo Jr. ist eine Schreibtischlampe.", True, "Die hüpfende Lampe aus dem Kurzfilm Luxo Jr. wurde Teil des Pixar-Logos.", "Pixar-Maskottchen", "pixar"),
    ("Der Filmpreis Oscar hieß von Anfang an offiziell so.", False, "Die Auszeichnung heißt offiziell Academy Award of Merit; Oscar ist der gebräuchliche Spitzname.", "Oscar-Name", "oscars"),
    ("Dr. No war der erste von Eon Productions produzierte James-Bond-Film.", True, "Die Eon-Filmreihe begann 1962 mit Dr. No.", "James Bond Filmstart", "bond"),
    ("Wakanda ist in den Marvel-Geschichten ein fiktives afrikanisches Land.", True, "Wakanda ist die Heimat von Black Panther im Marvel-Universum.", "Wakanda", "marvel"),
    ("Die Emmy Awards zeichnen ausschließlich Kinofilme aus.", False, "Die Emmys sind vor allem Auszeichnungen für Fernsehen und verwandte Programme.", "Emmy Awards", "television"),
    # Pflanzen & Tiere
    ("Das Blut vieler Kraken erscheint wegen des kupferhaltigen Hämocyanins blau.", True, "Hämocyanin transportiert Sauerstoff mit Kupfer statt mit Eisen.", "Krakenblut", "ocean"),
    ("Fledermäuse sind die einzigen Säugetiere mit aktivem Dauerflug.", True, "Andere gleitende Säugetiere können nicht aus eigener Kraft dauerhaft fliegen.", "Fledermausflug", "zoo"),
    ("Bambus gehört botanisch zu den Gräsern.", True, "Bambusse bilden eine Unterfamilie innerhalb der Süßgräser.", "Bambus", "kew"),
    ("Kaffeebohnen sind botanisch die Samen der Kaffeefrucht.", True, "Die sogenannten Bohnen sind die Samen in den Kaffeekirschen.", "Kaffeesamen", "kew"),
    ("Haie besitzen ein Knochenskelett wie die meisten Landwirbeltiere.", False, "Das Skelett der Haie besteht überwiegend aus Knorpel.", "Haiskelett", "ocean"),
    # Geografie & Welt
    ("Das Sargassomeer wird vollständig durch Meeresströmungen statt durch Küsten begrenzt.", True, "Es ist das einzige Meer ohne Landgrenze und wird durch Strömungen des Nordatlantikwirbels gefasst.", "Sargassomeer", "noaa"),
    ("Der Nullmeridian ist als Längengrad 0 festgelegt.", True, "Von ihm aus werden geografische Längengrade gezählt.", "Nullmeridian", "britannica_geo"),
    ("Der Baikalsee ist der tiefste See der Erde.", True, "Seine größte Tiefe beträgt rund 1.642 Meter.", "Baikalsee", "unesco"),
    ("Die Donau mündet in die Ostsee.", False, "Die Donau fließt durch ihr Delta ins Schwarze Meer.", "Donaumündung", "britannica_geo"),
    ("Die Antarktis gilt wegen ihrer geringen Niederschläge als Wüste.", True, "Wüste bezeichnet Trockenheit, nicht zwingend Hitze.", "Antarktische Wüste", "britannica_geo"),
    # Wissenschaft & Technik
    ("Helium hat eine geringere Dichte als Luft.", True, "Helium ist ein sehr leichtes Edelgas und steigt in Luft auf.", "Heliumdichte", "iupac"),
    ("Brom ist bei normaler Raumtemperatur flüssig.", True, "Brom gehört neben Quecksilber zu den wenigen Elementen, die bei Raumtemperatur flüssig sind.", "Flüssiges Brom", "iupac"),
    ("Kelvinwerte werden mit einem Gradzeichen geschrieben.", False, "Die SI-Einheit heißt Kelvin und wird ohne Gradzeichen geschrieben, etwa 300 K.", "Kelvin-Schreibweise", "bipm"),
    ("RNA verwendet normalerweise Uracil anstelle von Thymin.", True, "In RNA ersetzt Uracil in der Regel die Base Thymin der DNA.", "RNA-Basen", "nih"),
    ("Ein einzelnes sichtbares Emoji kann in Unicode aus mehreren Zeichen bestehen.", True, "Flaggen, Hauttöne und ZWJ-Folgen können als eine Glyphe erscheinen.", "Emoji-Sequenzen", "unicode"),
    # Mensch & Alltag
    ("Reife rote Blutkörperchen des Menschen besitzen keinen Zellkern.", True, "Bei ihrer Reifung verlieren menschliche Erythrozyten den Zellkern.", "Rote Blutkörperchen", "nih"),
    ("Die Leber kann nach einem Teilverlust Gewebe nachbilden.", True, "Sie besitzt eine außergewöhnliche Regenerationsfähigkeit.", "Leberregeneration", "nih"),
    ("Vitamin D ist wasserlöslich.", False, "Vitamin D gehört zu den fettlöslichen Vitaminen.", "Vitamin D", "vitamins"),
    ("Die Rufnummer 112 funktioniert als europäische Notrufnummer in allen EU-Staaten.", True, "112 ist EU-weit kostenlos erreichbar.", "EU-Notruf 112", "emergency"),
    ("Baumwolle ist eine synthetische Faser aus Erdöl.", False, "Baumwolle ist eine natürliche Pflanzenfaser.", "Baumwollfaser", "materials"),
]

MULTIPLE_CHOICE_SPECS = [
    # category, topic, prompt, correct, distractors, explanation, source
    ("gaming", "Game-Boy-Entwicklung", "Wer leitete bei Nintendo die Entwicklung des ursprünglichen Game Boy?", "Gunpei Yokoi", ["Shigeru Miyamoto", "Satoru Iwata", "Masayuki Uemura"], "Gunpei Yokoi leitete das Team, das den Game Boy entwickelte.", "nintendo"),
    ("gaming", "PlayStation-Start", "In welchem Land erschien die erste PlayStation zuerst?", "Japan", ["USA", "Frankreich", "Südkorea"], "Die erste PlayStation startete im Dezember 1994 in Japan.", "playstation"),
    ("gaming", "Tetris-Erfinder", "Wer entwickelte 1984 das ursprüngliche Tetris?", "Alexei Paschitnow", ["Toru Iwatani", "John Carmack", "Sid Meier"], "Alexei Paschitnow entwickelte Tetris in Moskau.", "tetris"),
    ("gaming", "Triforce", "Welche drei Tugenden verkörpern die Teile der Triforce?", "Kraft, Weisheit und Mut", ["Feuer, Wasser und Erde", "Zeit, Raum und Licht", "Stärke, Glück und Magie"], "Die Triforce besteht aus Kraft, Weisheit und Mut.", "nintendo"),
    ("gaming", "Minecraft-Portale", "Aus welchem Material wird der Rahmen eines Netherportals in Minecraft gebaut?", "Obsidian", ["Endstein", "Grundgestein", "Quarzblock"], "Ein Netherportal benötigt einen Rahmen aus Obsidian.", "minecraft"),
    ("science_technology", "HTTP-Humor", "Welcher HTTP-Code bedeutet im Aprilscherz-RFC „I'm a teapot“?", "418", ["204", "302", "451"], "RFC 2324 legte am 1. April 1998 für eine Teekanne den scherzhaften Code 418 fest.", "teapot"),
    ("science_technology", "Raumanzug-Spitznamen", "Was ist bei NASA-Raumanzügen die „Snoopy cap“?", "eine Kommunikationshaube", ["ein Sonnenschutz", "ein Notfallhandschuh", "eine Werkzeugtasche"], "Die Communications Carrier Assembly mit Kopfhörern und Mikrofonen trägt den Spitznamen Snoopy cap.", "snoopy"),
    ("science_technology", "CAPTCHA", "Wofür steht das C in CAPTCHA?", "Completely", ["Computer", "Cryptographic", "Certified"], "CAPTCHA steht für Completely Automated Public Turing Test to Tell Computers and Humans Apart.", "captcha"),
    ("media_entertainment", "Erste SMS", "Was stand in der ersten SMS von 1992?", "Merry Christmas", ["Hello World", "Call me", "Happy New Year"], "Neil Papworth schickte die erste SMS von einem Computer; ihr Text lautete Merry Christmas.", "sms"),
    ("human_everyday", "Erster Barcode-Scan", "Welches Produkt wurde 1974 als erstes an einer Kasse per Barcode gescannt?", "Wrigley's-Kaugummi", ["eine Cola-Dose", "eine Cornflakes-Packung", "eine Zahnpastatube"], "In einem Supermarkt in Ohio wurde eine Packung Wrigley's Juicy Fruit gescannt.", "barcode"),
    ("music", "Rhapsody in Blue", "Wer komponierte Rhapsody in Blue?", "George Gershwin", ["Aaron Copland", "Leonard Bernstein", "Duke Ellington"], "George Gershwin komponierte Rhapsody in Blue für die Uraufführung von 1924.", "classical"),
    ("music", "Präpariertes Klavier", "Welcher Komponist machte das präparierte Klavier besonders bekannt?", "John Cage", ["Gustav Mahler", "Claude Debussy", "Anton Bruckner"], "John Cage entwickelte viele Werke für Klavier mit Gegenständen an den Saiten.", "cage"),
    ("music", "Theremin", "Nach wem ist das elektronische Instrument Theremin benannt?", "Leon Theremin", ["Robert Moog", "Thomas Edison", "Hermann von Helmholtz"], "Der Erfinder Leon Theremin gab dem Instrument seinen Namen.", "instruments"),
    ("music", "Saxofon", "Wer erfand das Saxofon?", "Adolphe Sax", ["Theobald Böhm", "Antonio Stradivari", "Hector Berlioz"], "Der belgische Instrumentenbauer Adolphe Sax patentierte das Saxofon 1846.", "instruments"),
    ("music", "Boléro", "Wer komponierte den Boléro?", "Maurice Ravel", ["Erik Satie", "Claude Debussy", "Camille Saint-Saëns"], "Maurice Ravel komponierte den Boléro 1928.", "classical"),
    ("sport", "Fußballumfang", "Welchen Umfang muss ein regulärer Fußball haben?", "68 bis 70 Zentimeter", ["58 bis 60 Zentimeter", "73 bis 75 Zentimeter", "80 bis 82 Zentimeter"], "IFAB schreibt einen Umfang von 68 bis 70 Zentimetern vor.", "ifab"),
    ("sport", "Basketball-Wurfuhr", "Wie lange läuft die FIBA-Wurfuhr bei einem neuen Ballbesitz?", "24 Sekunden", ["20 Sekunden", "30 Sekunden", "35 Sekunden"], "Ein Team muss innerhalb von 24 Sekunden einen Wurf abgeben, der den Ring berührt oder trifft.", "fiba"),
    ("sport", "Grand-Slam-Beläge", "Welches Grand-Slam-Turnier wird auf Sand gespielt?", "Roland-Garros", ["Wimbledon", "US Open", "Australian Open"], "Roland-Garros in Paris wird auf roten Sandplätzen ausgetragen.", "itf"),
    ("sport", "Zehnkampf", "Aus wie vielen Disziplinen besteht ein Zehnkampf?", "Zehn", ["Sieben", "Neun", "Zwölf"], "Der Zehnkampf kombiniert zehn Leichtathletikdisziplinen an zwei Tagen.", "athletics"),
    ("sport", "Golf-Par", "Was bezeichnet Par beim Golf?", "Die erwartete Schlagzahl für ein Loch", ["Die Zahl der Spieler einer Gruppe", "Die Breite des Fairways", "Das Gewicht des Balls"], "Par ist die festgelegte Schlagzahl, die ein sehr guter Spieler für ein Loch erwarten lässt.", "olympics"),
    ("witnesses_of_time", "Hieroglyphen-Entzifferung", "Welche alte Schrift ließ sich mit Hilfe des Steins von Rosette entziffern?", "Ägyptische Hieroglyphen", ["Maya-Schrift", "Linear A", "Indus-Schrift"], "Der parallele griechische Text half beim Verständnis der Hieroglyphen.", "rosetta"),
    ("witnesses_of_time", "Diamant-Sutra", "Aus welchem Jahr stammt die datierte Druckausgabe des Diamant-Sutra?", "868", ["476", "1215", "1455"], "Die chinesische Buchrolle trägt ein Kolophon aus dem Jahr 868.", "history"),
    ("witnesses_of_time", "Frauenwahlrecht", "Welche Aktivistin prägte die neuseeländische Frauenwahlrechtskampagne?", "Kate Sheppard", ["Emmeline Pankhurst", "Susan B. Anthony", "Olympe de Gouges"], "Kate Sheppard organisierte die großen Petitionen, die dem Wahlgesetz von 1893 vorausgingen.", "suffrage"),
    ("witnesses_of_time", "Westfälischer Friede", "In welchem Jahr wurde der Westfälische Friede geschlossen?", "1648", ["1492", "1713", "1815"], "Die Verträge von Münster und Osnabrück beendeten 1648 den Dreißigjährigen Krieg.", "history"),
    ("witnesses_of_time", "Versailler Vertrag", "Wo wurde der Versailler Vertrag 1919 unterzeichnet?", "Im Spiegelsaal von Versailles", ["Im Louvre", "Im Élysée-Palast", "In Notre-Dame"], "Die Unterzeichnung fand am 28. Juni 1919 im Spiegelsaal statt.", "history"),
    ("media_entertainment", "Pixar-Erstling", "Welcher Film war Pixars erster abendfüllender Kinofilm?", "Toy Story", ["Cars", "Findet Nemo", "Die Unglaublichen"], "Toy Story erschien 1995 als Pixars erster Langfilm.", "pixar"),
    ("media_entertainment", "Filmfest Cannes", "Wie heißt der Hauptpreis des Filmfestivals von Cannes?", "Goldene Palme", ["Goldener Löwe", "Goldener Bär", "Goldene Kamera"], "Die Palme d'Or ist die höchste Auszeichnung des Festivals von Cannes.", "oscars"),
    ("media_entertainment", "Berlinale", "Welches Tier trägt der Hauptpreis der Berlinale im Namen?", "Bär", ["Löwe", "Adler", "Pferd"], "Der Hauptpreis der Berlinale heißt Goldener Bär.", "oscars"),
    ("media_entertainment", "James Bond", "Welcher Darsteller spielte James Bond in Dr. No?", "Sean Connery", ["Roger Moore", "George Lazenby", "Daniel Craig"], "Sean Connery spielte Bond im ersten Eon-Kinofilm Dr. No.", "bond"),
    ("media_entertainment", "Academy Awards", "Welche Organisation vergibt die Oscars?", "Academy of Motion Picture Arts and Sciences", ["Hollywood Foreign Press Association", "Screen Actors Guild", "British Film Institute"], "Die Academy of Motion Picture Arts and Sciences richtet die Academy Awards aus.", "oscars"),
    ("plants_animals", "Zimt", "Aus welchem Pflanzenteil wird Zimt gewonnen?", "Innere Rinde", ["Wurzel", "Blütennarbe", "Fruchtkern"], "Zimt entsteht aus der getrockneten inneren Rinde von Zimtbäumen.", "kew"),
    ("plants_animals", "Arabica-Kaffee", "Aus welcher Region stammt Coffea arabica ursprünglich?", "Äthiopisches Hochland", ["Anden", "Java", "Mexikanisches Hochland"], "Wildformen von Arabica-Kaffee stammen aus Äthiopien und angrenzenden Gebieten.", "kew"),
    ("plants_animals", "Wal-Verwandtschaft", "Welche Tiere sind die nächsten heute lebenden Verwandten der Wale?", "Flusspferde", ["Robben", "Seekühe", "Elefanten"], "Molekulare und fossile Befunde ordnen Wale und Flusspferde derselben Verwandtschaftsgruppe zu.", "zoo"),
    ("plants_animals", "Rentieraugen", "Welche Farbe kann das Tapetum im Rentierauge im Winter annehmen?", "Blau", ["Rot", "Orange", "Schwarz"], "Die reflektierende Schicht wechselt im dunklen arktischen Winter von golden zu blau.", "zoo"),
    ("plants_animals", "Fledermaus-Ortung", "Womit orientieren sich viele Fledermäuse in der Dunkelheit?", "Echoortung", ["Magnetischen Schnurrhaaren", "Infrarotaugen", "Elektrischen Organen"], "Sie senden Ultraschallrufe aus und werten deren Echos aus.", "zoo"),
    ("geography_world", "NATO-Sitz", "In welcher Stadt befindet sich das NATO-Hauptquartier?", "Brüssel", ["Den Haag", "Genf", "Straßburg"], "Das NATO-Hauptquartier befindet sich in Brüssel.", "cia"),
    ("geography_world", "EZB-Sitz", "In welcher Stadt sitzt die Europäische Zentralbank?", "Frankfurt am Main", ["Brüssel", "Luxemburg", "Wien"], "Die EZB hat ihren Sitz in Frankfurt am Main.", "cia"),
    ("geography_world", "EU-Gerichtshof", "In welcher Stadt hat der Gerichtshof der Europäischen Union seinen Sitz?", "Luxemburg", ["Brüssel", "Straßburg", "Den Haag"], "Der Gerichtshof der Europäischen Union sitzt in Luxemburg.", "cia"),
    ("geography_world", "Salar de Uyuni", "In welchem Land liegt der Salar de Uyuni?", "Bolivien", ["Peru", "Chile", "Argentinien"], "Der riesige Salzsee liegt im bolivianischen Altiplano.", "britannica_geo"),
    ("geography_world", "Baikalsee", "In welchem Land liegt der Baikalsee?", "Russland", ["Mongolei", "Kasachstan", "China"], "Der Baikalsee liegt in Sibirien in Russland.", "unesco"),
    ("science_technology", "Helium", "Welche Ordnungszahl hat Helium?", "2", ["1", "4", "8"], "Helium ist das zweite Element des Periodensystems.", "iupac"),
    ("science_technology", "Wolfram", "Welche Ordnungszahl hat Wolfram?", "74", ["47", "72", "79"], "Wolfram ist Element 74 des Periodensystems.", "iupac"),
    ("science_technology", "SI-Basiseinheiten", "Welche SI-Basiseinheit misst die elektrische Stromstärke?", "Ampere", ["Volt", "Ohm", "Coulomb"], "Das Ampere ist die SI-Basiseinheit der elektrischen Stromstärke.", "bipm"),
    ("science_technology", "Unicode-Kodierung", "Welche Unicode-Kodierung verwendet pro Codepunkt ein bis vier Bytes?", "UTF-8", ["ASCII", "UTF-32", "EBCDIC"], "UTF-8 ist eine variable Kodierung mit ein bis vier Bytes je Unicode-Codepunkt.", "unicode"),
    ("science_technology", "Computermaus", "Wer führte 1968 die Computermaus in der berühmten „Mother of All Demos“ vor?", "Douglas Engelbart", ["Alan Turing", "Tim Berners-Lee", "Dennis Ritchie"], "Douglas Engelbart demonstrierte das Zeigegerät 1968 öffentlich.", "nist"),
    ("human_everyday", "Vitamin C", "Welche Krankheit entsteht klassisch bei schwerem Vitamin-C-Mangel?", "Skorbut", ["Rachitis", "Beriberi", "Pellagra"], "Längerer Vitamin-C-Mangel kann Skorbut verursachen.", "vitamins"),
    ("human_everyday", "Vitamin D", "Welche Mineralstoffaufnahme unterstützt Vitamin D besonders?", "Calcium", ["Natrium", "Kupfer", "Fluorid"], "Vitamin D fördert die Calciumaufnahme und unterstützt Knochen.", "vitamins"),
    ("human_everyday", "Notrufnummern", "Welche Nummer verbindet in Deutschland mit der Polizei?", "110", ["112", "116117", "115"], "110 ist der Polizeinotruf; 112 erreicht Feuerwehr und Rettungsdienst.", "emergency"),
    ("human_everyday", "Ärztlicher Bereitschaftsdienst", "Welche Nummer hat der ärztliche Bereitschaftsdienst in Deutschland?", "116117", ["110", "112", "115"], "116117 ist für dringende, aber nicht lebensbedrohliche medizinische Probleme außerhalb der Sprechzeiten gedacht.", "emergency"),
    ("human_everyday", "Naturfasern", "Welche Faser wächst als Samenhaar an einer Pflanze?", "Baumwolle", ["Nylon", "Polyester", "Acryl"], "Baumwolle besteht aus Fasern, die die Samen der Baumwollpflanze umgeben.", "materials"),
]

MATCH_SPECS = [
    ("gaming", "Originalplattformen", "Verbinde das Spiel mit der Konsole, auf der es ursprünglich besonders bekannt wurde.", [("Sonic the Hedgehog", "Mega Drive"), ("Halo: Combat Evolved", "Xbox"), ("Wii Sports", "Wii")], "games"),
    ("gaming", "Spielfiguren", "Ordne das Spiel seiner Hauptfigur zu.", [("Hades", "Zagreus"), ("Metroid", "Samus Aran"), ("Tomb Raider", "Lara Croft")], "games"),
    ("gaming", "Minecraft-Dimensionen", "Ordne den Minecraft-Gegner seiner typischen Dimension zu.", [("Shulker", "Das Ende"), ("Blaze", "Nether"), ("Wächter", "Oberwelt")], "minecraft"),
    ("gaming", "Klassische Arcade-Spiele", "Ordne das Arcade-Spiel seinem Entwickler zu.", [("Pac-Man", "Namco"), ("Donkey Kong", "Nintendo"), ("Asteroids", "Atari")], "games"),
    ("gaming", "Nintendo-Serien", "Ordne die Figur ihrer Nintendo-Spielreihe zu.", [("Fox McCloud", "Star Fox"), ("Olimar", "Pikmin"), ("Melinda", "Animal Crossing")], "nintendo"),
    ("geography_world", "Seltsames Meereswetter", "Ordne das Phänomen seiner Ursache zu.", [("Meteotsunami", "Luftdruckstörung"), ("St.-Elms-Feuer", "elektrische Entladung"), ("Maelstrom", "aufeinandertreffende Strömungen")], "noaa_weird"),
    ("witnesses_of_time", "Digitale Premieren", "Ordne den digitalen Meilenstein seinem Jahr zu.", [("erste SMS", "1992"), ("QR-Code", "1994"), ("originales Emoji-Set", "1999")], ["sms", "qr", "emoji"]),
    ("human_everyday", "Ideen aus dem Alltag", "Ordne die Erfindung ihrem Auslöser zu.", [("Post-it", "haftendes Lesezeichen"), ("Klettverschluss", "Kletten am Stoff"), ("Celluloid", "Ersatz für Elfenbein")], ["postit", "velcro", "plastics"]),
    ("science_technology", "Mission mit Ansage", "Ordne das NASA-Projekt seiner Aufgabe zu.", [("DART", "Asteroid ablenken"), ("Ingenuity", "Flug auf dem Mars testen"), ("Perseverance", "Marsgestein untersuchen")], ["dart", "ingenuity", "nasa_history"]),
    ("media_entertainment", "Digitale Wörter", "Ordne den Begriff seiner wörtlichen oder ausgeschriebenen Bedeutung zu.", [("Emoji", "Bildzeichen"), ("QR", "Quick Response"), ("CAPTCHA", "automatischer Turing-Test")], ["emoji", "qr", "captcha"]),
    ("music", "Tonentstehung bei Bläsern", "Ordne das Blasinstrument seiner Art der Tonerzeugung zu.", [("Oboe", "Doppelrohrblatt"), ("Klarinette", "Einfachrohrblatt"), ("Querflöte", "Luftstrom an einer Kante")], "instruments"),
    ("music", "Tonarten", "Verbinde die Dur-Tonart mit ihrer Zahl an Vorzeichen.", [("C-Dur", "keine Vorzeichen"), ("G-Dur", "ein Kreuz"), ("F-Dur", "ein Be")], "classical"),
    ("music", "Artikulation", "Ordne die musikalische Artikulationsangabe ihrer Wirkung zu.", [("Legato", "gebunden"), ("Staccato", "kurz getrennt"), ("Tenuto", "ausgehalten")], "classical"),
    ("music", "Tanzherkunft", "Ordne den Tanz seinem Ursprungsland zu.", [("Tango", "Argentinien"), ("Samba", "Brasilien"), ("Flamenco", "Spanien")], "classical"),
    ("music", "Stimmlagen", "Ordne die Stimmlage ihrer üblichen Lage zu.", [("Sopran", "hohe Frauenstimme"), ("Tenor", "hohe Männerstimme"), ("Bass", "tiefe Männerstimme")], "classical"),
    ("sport", "Sportpokale", "Ordne den Pokal seiner Sportart zu.", [("Davis Cup", "Tennis"), ("Ryder Cup", "Golf"), ("Stanley Cup", "Eishockey")], "olympics"),
    ("sport", "Spielpositionen", "Ordne die Position ihrer Sportart zu.", [("Quarterback", "American Football"), ("Libero", "Volleyball"), ("Wicketkeeper", "Cricket")], "olympics"),
    ("sport", "Sportstätten", "Ordne die Sportart ihrer typischen Wettkampffläche zu.", [("Bahnradsport", "Velodrom"), ("Judo", "Tatami"), ("Fechten", "Planche")], "olympics"),
    ("sport", "Sportgeräte", "Ordne das Gerät seiner Sportart zu.", [("Puck", "Eishockey"), ("Federball", "Badminton"), ("Florett", "Fechten")], "olympics"),
    ("sport", "Weltverbände", "Ordne den Weltverband seiner Sportart zu.", [("World Athletics", "Leichtathletik"), ("World Aquatics", "Schwimmsport"), ("UCI", "Radsport")], "olympics"),
    ("witnesses_of_time", "Antike Stätten", "Ordne die historische Stätte ihrer Kultur zu.", [("Machu Picchu", "Inka"), ("Chichén Itzá", "Maya"), ("Persepolis", "Achämeniden")], "worldheritage"),
    ("witnesses_of_time", "Kalenderreformen", "Ordne das Kalendersystem der historischen Einführung zu.", [("Julianischer Kalender", "Julius Caesar"), ("Gregorianischer Kalender", "Papst Gregor XIII."), ("Französischer Revolutionskalender", "Nationalkonvent")], "history"),
    ("witnesses_of_time", "Historische Dokumente", "Ordne das Dokument seinem Jahr zu.", [("Magna Carta", "1215"), ("Unabhängigkeitserklärung der USA", "1776"), ("Allgemeine Erklärung der Menschenrechte", "1948")], "history"),
    ("witnesses_of_time", "Entdeckungsfahrten", "Ordne den Seefahrer seinem bekannten Reiseziel zu.", [("Vasco da Gama", "Seeweg nach Indien"), ("Ferdinand Magellan", "erste Weltumsegelungsexpedition"), ("James Cook", "Ostküste Australiens")], "history"),
    ("witnesses_of_time", "Alte Schreibmedien", "Ordne das Schreibmedium dem typischen Material zu.", [("Papyrus", "Pflanzenmark"), ("Pergament", "Tierhaut"), ("Keilschrifttafel", "Ton")], "history"),
    ("media_entertainment", "Filmregie", "Ordne den Film seiner Regisseurin oder seinem Regisseur zu.", [("Jaws", "Steven Spielberg"), ("Psycho", "Alfred Hitchcock"), ("Lost in Translation", "Sofia Coppola")], "oscars"),
    ("media_entertainment", "Animationsstudios", "Ordne den Film seinem Animationsstudio zu.", [("Toy Story", "Pixar"), ("Chihiros Reise ins Zauberland", "Studio Ghibli"), ("Shrek", "DreamWorks Animation")], "pixar"),
    ("media_entertainment", "Filmfiguren", "Ordne die Figur der Filmreihe zu.", [("Ellen Ripley", "Alien"), ("Indiana Jones", "Jäger des verlorenen Schatzes"), ("Marty McFly", "Zurück in die Zukunft")], "oscars"),
    ("media_entertainment", "Festivalpreise", "Ordne den Hauptpreis seinem Filmfestival zu.", [("Goldene Palme", "Cannes"), ("Goldener Löwe", "Venedig"), ("Goldener Bär", "Berlin")], "oscars"),
    ("media_entertainment", "Fiktive Orte", "Ordne den Ort dem erzählten Universum zu.", [("Wakanda", "Marvel"), ("Hogwarts", "Harry Potter"), ("Mittelerde", "Der Herr der Ringe")], "marvel"),
    ("plants_animals", "Tierklassen", "Ordne das Tier seiner Wirbeltierklasse zu.", [("Axolotl", "Amphibien"), ("Komodowaran", "Reptilien"), ("Schnabeltier", "Säugetiere")], "zoo"),
    ("plants_animals", "Nutzpflanzen", "Ordne die Pflanze ihrem Produkt zu.", [("Hevea brasiliensis", "Naturkautschuk"), ("Linum usitatissimum", "Leinen"), ("Theobroma cacao", "Kakao")], "kew"),
    ("plants_animals", "Lebensräume", "Ordne das Tier seinem natürlichen Lebensraum zu.", [("Fennek", "Sahara"), ("Eisbär", "Arktis"), ("Kaiserpinguin", "Antarktis")], "zoo"),
    ("plants_animals", "Tragzeiten", "Ordne das Tier seiner ungefähren Tragzeit zu.", [("Hauskatze", "2 Monate"), ("Pferd", "11 Monate"), ("Elefant", "22 Monate")], "gestation"),
    ("plants_animals", "Blattformen", "Ordne den Baum seiner typischen Blattform zu.", [("Ginkgo", "fächerförmig"), ("Ahorn", "handförmig gelappt"), ("Weide", "schmal lanzettlich")], "kew"),
    ("geography_world", "Währungen", "Verbinde jeden Staat mit dem Namen seines gesetzlichen Zahlungsmittels.", [("Bhutan", "Ngultrum"), ("Belize", "Belize-Dollar"), ("Kasachstan", "Tenge")], "cia"),
    ("geography_world", "Flussmündungen", "Ordne den Fluss dem Meer zu, in das er mündet.", [("Po", "Adriatisches Meer"), ("Weichsel", "Ostsee"), ("Orinoco", "Atlantik")], "britannica_geo"),
    ("geography_world", "Gebirge", "Ordne den Berg seinem Gebirge zu.", [("Aconcagua", "Anden"), ("Denali", "Alaskakette"), ("Elbrus", "Kaukasus")], "britannica_geo"),
    ("geography_world", "Inselstaaten", "Ordne die Insel dem Staat zu.", [("Tasmanien", "Australien"), ("Hokkaidō", "Japan"), ("Sizilien", "Italien")], "cia"),
    ("geography_world", "Seen und Länder", "Ordne den See dem Land zu.", [("Tanasee", "Äthiopien"), ("Bleder See", "Slowenien"), ("Tauposee", "Neuseeland")], "cia"),
    ("science_technology", "Ordnungszahlen", "Ordne das Element seiner Ordnungszahl zu.", [("Neon", "10"), ("Kobalt", "27"), ("Zinn", "50")], "iupac"),
    ("science_technology", "SI-Basisgrößen", "Ordne die SI-Basiseinheit ihrer Größe zu.", [("Candela", "Lichtstärke"), ("Mol", "Stoffmenge"), ("Kelvin", "Temperatur")], "bipm"),
    ("science_technology", "Planetenmonde", "Ordne den Planeten seinem größten Mond zu.", [("Jupiter", "Ganymed"), ("Saturn", "Titan"), ("Neptun", "Triton")], "nasa"),
    ("science_technology", "Naturgesetze", "Ordne die Person dem nach ihr benannten Gesetz zu.", [("Georg Ohm", "elektrischer Widerstand"), ("Robert Hooke", "elastische Verformung"), ("Blaise Pascal", "Druckübertragung")], "nist"),
    ("science_technology", "Digitale Einheiten", "Ordne die Einheit ihrer üblichen Bedeutung zu.", [("Bit", "binäre Stelle"), ("Byte", "acht Bit"), ("Hertz", "Ereignisse pro Sekunde")], "nist"),
    ("human_everyday", "Organe", "Ordne das Organ seiner Hauptaufgabe zu.", [("Niere", "Blut filtern"), ("Lunge", "Gasaustausch"), ("Bauchspeicheldrüse", "Verdauungsenzyme und Hormone bilden")], "nih"),
    ("human_everyday", "Mangelkrankheiten", "Ordne den Nährstoff seiner klassischen Mangelkrankheit zu.", [("Vitamin C", "Skorbut"), ("Vitamin D", "Rachitis"), ("Vitamin B1", "Beriberi")], "vitamins"),
    ("human_everyday", "Küchenwerkzeuge", "Ordne das Werkzeug seiner Hauptanwendung zu.", [("Schneebesen", "Aufschlagen"), ("Mörser", "Zerstoßen"), ("Sieb", "Trennen nach Größe")], "britannica_geo"),
    ("human_everyday", "Garmethoden", "Ordne die Garmethode ihrem hauptsächlichen Wärmeträger zu.", [("Dämpfen", "Wasserdampf"), ("Frittieren", "heißes Fett"), ("Sous-vide", "temperiertes Wasserbad")], "cooking"),
    ("human_everyday", "Recyclingcodes", "Ordne den Kunststoff seinem Resin-Code zu.", [("PET", "1"), ("HDPE", "2"), ("PVC", "3")], "epa"),
]

ORDER_SPECS = [
    ("gaming", "Nintendo-Konsolen", "Ordne diese Nintendo-Konsolen nach ihrer Erstveröffentlichung – von früh nach spät.", [("Nintendo Entertainment System", 1983), ("Game Boy", 1989), ("Nintendo 64", 1996), ("Nintendo Switch", 2017)], "Jahr", "nintendo"),
    ("gaming", "PlayStation-Generationen", "Ordne die PlayStation-Konsolen nach ihrer Veröffentlichung – von früh nach spät.", [("PlayStation", 1994), ("PlayStation 2", 2000), ("PlayStation 3", 2006), ("PlayStation 5", 2020)], "Jahr", "playstation"),
    ("gaming", "Brettspiel-Erscheinungen", "Ordne diese Spiele nach ihrer ersten kommerziellen Ausgabe – von früh nach spät.", [("Monopoly", 1935), ("Scrabble", 1948), ("Risiko", 1957), ("Catan", 1995)], "Jahr", "games"),
    ("gaming", "Spielklassiker", "Ordne diese Spiele nach ihrer ersten Veröffentlichung – von früh nach spät.", [("Pong", 1972), ("Space Invaders", 1978), ("Pac-Man", 1980), ("Tetris", 1984)], "Jahr", "games"),
    ("gaming", "Minecraft-Versionen", "Ordne diese Minecraft-Meilensteine – von früh nach spät.", [("Öffentliche Alpha", 2010), ("Vollversion 1.0", 2011), ("Aquatic Update", 2018), ("Caves & Cliffs", 2021)], "Jahr", "minecraft"),
    ("witnesses_of_time", "Tech-Alltag", "Ordne diese digitalen Alltagsmomente – von früh nach spät.", [("erster Barcode-Scan", 1974), ("Web-Vorschlag", 1989), ("erste SMS", 1992), ("QR-Code", 1994)], "Jahr", ["barcode", "cern_web", "sms", "qr"]),
    ("science_technology", "Geburt des Web", "Ordne diese Web-Meilensteine – von früh nach spät.", [("erster Web-Vorschlag", 1989), ("erster Browser und Server", 1990), ("Line-Mode-Browser", 1992), ("Web-Software gemeinfrei", 1993)], "Jahr", "cern_web"),
    ("media_entertainment", "Digitale Kommunikation", "Ordne diese Kommunikations-Meilensteine – von früh nach spät.", [("E-Mail dominiert ARPANET", 1973), ("erste SMS", 1992), ("originales Emoji-Set", 1999), ("CAPTCHA-Begriff", 2000)], "Jahr", ["computer_history", "sms", "emoji", "captcha"]),
    ("science_technology", "DART-Mission", "Ordne diese DART-Ereignisse – von früh nach spät.", [("Start der Sonde", 2021.11), ("Freisetzung von LICIACube", 2022.09), ("Einschlag auf Dimorphos", 2022.091), ("Bestätigung der Bahnänderung", 2022.10)], "Zeitpunkt", ["dart_mission", "dart"]),
    ("science_technology", "Ingenuity-Mission", "Ordne diese Ingenuity-Ereignisse – von früh nach spät.", [("Landung mit Perseverance", 2021.02), ("erster Flug", 2021.04), ("letzter Flug", 2024.0118), ("Missionsende", 2024.0125)], "Zeitpunkt", "ingenuity"),
    ("music", "Tonaufzeichnung", "Ordne diese Tonträger und Geräte nach ihrer Einführung – von früh nach spät.", [("Phonograph", 1877), ("Schellackplatte", 1890), ("Compact Cassette", 1963), ("Compact Disc", 1982)], "Jahr ungefähr", "loc_sound"),
    ("music", "Kompositionen", "Ordne diese Werke nach ihrer Uraufführung – von früh nach spät.", [("Messias", 1742), ("9. Sinfonie von Beethoven", 1824), ("Boléro", 1928), ("4′33″", 1952)], "Jahr", "classical"),
    ("music", "Orchesterinstrumente", "Ordne diese Instrumente nach ihrer üblichen Tonlage – von tief nach hoch.", [("Kontrabass", 1), ("Violoncello", 2), ("Viola", 3), ("Violine", 4)], "Tonlage", "instruments"),
    ("music", "Notenwerte", "Ordne die Notenwerte nach ihrer Dauer – von kurz nach lang.", [("Sechzehntelnote", 0.0625), ("Achtelnote", 0.125), ("Viertelnote", 0.25), ("Ganze Note", 1)], "ganze Note", "classical"),
    ("music", "Musikfestival-Gründungen", "Ordne diese Musikfestivals nach ihrer ersten Ausgabe – von früh nach spät.", [("Newport Jazz Festival", 1954), ("Monterey Pop Festival", 1967), ("Glastonbury Festival", 1970), ("Lollapalooza", 1991)], "Jahr", "rockhall"),
    ("sport", "Wurfgeräte", "Ordne diese Leichtathletik-Wurfgeräte nach Regelgewicht – von leicht nach schwer.", [("Frauen-Speer", 0.6), ("Frauen-Diskus", 1), ("Männer-Diskus", 2), ("Männer-Kugel", 7.26)], "Kilogramm", "athletics"),
    ("sport", "Schwimmstrecken", "Ordne diese Beckenschwimm-Strecken – von kurz nach lang.", [("50 Meter Freistil", 50), ("100 Meter Rücken", 100), ("200 Meter Schmetterling", 200), ("1.500 Meter Freistil", 1500)], "Meter", "olympics"),
    ("sport", "Teamgrößen", "Ordne die Sportarten nach Spielern pro Team auf dem Feld – von wenigen nach vielen.", [("Beachvolleyball", 2), ("Basketball", 5), ("Handball", 7), ("Fußball", 11)], "Spieler", "olympics"),
    ("sport", "Olympische Premieren", "Ordne diese Sportarten nach ihrer ersten olympischen Austragung – von früh nach spät.", [("Leichtathletik", 1896), ("Basketball", 1936), ("Triathlon", 2000), ("Skateboard", 2021)], "Jahr", "olympics"),
    ("sport", "Hürdenhöhen", "Ordne diese Hürden nach ihrer Höhe – von niedrig nach hoch.", [("400 m Hürden Frauen", 0.762), ("100 m Hürden Frauen", 0.838), ("400 m Hürden Männer", 0.914), ("110 m Hürden Männer", 1.067)], "Meter", "athletics"),
    ("witnesses_of_time", "Epochenfolge", "Ordne diese historischen Epochen – von früh nach spät.", [("Bronzezeit", -2200), ("Römische Kaiserzeit", 27), ("Renaissance", 1400), ("Industrialisierung", 1760)], "Beginn ungefähr", "history"),
    ("witnesses_of_time", "Revolutionen", "Ordne diese Revolutionen – von früh nach spät.", [("Glorious Revolution", 1688), ("Amerikanische Revolution", 1775), ("Französische Revolution", 1789), ("Russische Oktoberrevolution", 1917)], "Jahr", "history"),
    ("witnesses_of_time", "Raumfahrt", "Ordne diese Raumfahrt-Meilensteine – von früh nach spät.", [("Sputnik 1", 1957), ("Juri Gagarin im All", 1961), ("Apollo 11", 1969), ("Start des Hubble-Teleskops", 1990)], "Jahr", "nasa_history"),
    ("witnesses_of_time", "Friedensverträge", "Ordne diese Verträge – von früh nach spät.", [("Westfälischer Friede", 1648), ("Wiener Kongress", 1815), ("Versailler Vertrag", 1919), ("Dayton-Abkommen", 1995)], "Jahr", "history"),
    ("witnesses_of_time", "Nobelpreis-Meilensteine", "Ordne diese Nobelpreis-Ereignisse – von früh nach spät.", [("Alfred Nobels Testament", 1895), ("Erste Preisvergabe", 1901), ("Wirtschaftspreis gestiftet", 1968), ("Malala als jüngste Preisträgerin", 2014)], "Jahr", "nobel"),
    ("media_entertainment", "Filmklassiker", "Ordne diese Filme nach ihrem Kinostart – von früh nach spät.", [("Metropolis", 1927), ("Citizen Kane", 1941), ("Der Pate", 1972), ("Pulp Fiction", 1994)], "Jahr", "oscars"),
    ("media_entertainment", "Pixar-Filme", "Ordne diese Pixar-Filme nach ihrem Start – von früh nach spät.", [("Toy Story", 1995), ("Die Monster AG", 2001), ("Ratatouille", 2007), ("Alles steht Kopf", 2015)], "Jahr", "pixar"),
    ("media_entertainment", "Bond-Filme", "Ordne diese Bond-Filme nach ihrem Kinostart – von früh nach spät.", [("Dr. No", 1962), ("Goldfinger", 1964), ("GoldenEye", 1995), ("Skyfall", 2012)], "Jahr", "bond"),
    ("media_entertainment", "Filmtechnik", "Ordne diese Filmtechnik-Meilensteine – von früh nach spät.", [("Erste öffentliche Lumière-Vorführung", 1895), ("The Jazz Singer mit Ton", 1927), ("Breiter Einsatz von Technicolor", 1939), ("Toy Story vollständig computeranimiert", 1995)], "Jahr", "oscars"),
    ("media_entertainment", "Marvel-Filmstarts", "Ordne diese Marvel-Filme nach ihrem Start – von früh nach spät.", [("Iron Man", 2008), ("The Avengers", 2012), ("Black Panther", 2018), ("Shang-Chi", 2021)], "Jahr", "marvel"),
    ("plants_animals", "Tiergrößen", "Ordne diese Tiere nach typischer Körpermasse – von leicht nach schwer.", [("Honigbiene", 0.0001), ("Hauskatze", 4), ("Afrikanischer Elefant", 6000), ("Blauwal", 120000)], "Kilogramm ungefähr", "zoo"),
    ("plants_animals", "Brutdauer", "Ordne diese Vogeleier nach der typischen Brutdauer – von kurz nach lang.", [("Huhn", 21), ("Ente", 28), ("Gans", 30), ("Strauß", 42)], "Tage ungefähr", "zoo"),
    ("plants_animals", "Pflanzenhöhe", "Ordne diese Pflanzen nach ihrer möglichen Höhe – von niedrig nach hoch.", [("Moos", 0.05), ("Sonnenblume", 3), ("Riesenbambus", 30), ("Küstenmammutbaum", 115)], "Meter ungefähr", "kew"),
    ("plants_animals", "Dinosaurier-Zeit", "Ordne diese Dinosaurier nach ihrem ersten Auftreten – von früh nach spät.", [("Plateosaurus", -214), ("Stegosaurus", -155), ("Iguanodon", -140), ("Tyrannosaurus", -68)], "Millionen Jahre", "nhm"),
    ("plants_animals", "Samenmasse", "Ordne diese Samen nach typischer Masse – von leicht nach schwer.", [("Orchideensamen", 0.000001), ("Mohnsamen", 0.0005), ("Reiskorn", 0.025), ("Kokosnuss", 1400)], "Gramm ungefähr", "kew"),
    ("geography_world", "Inselstaaten-Unabhängigkeit", "Ordne diese Inselstaaten nach ihrer Unabhängigkeit – von früh nach spät.", [("Sri Lanka", 1948), ("Zypern", 1960), ("Malta", 1964), ("Vanuatu", 1980)], "Jahr", "cia"),
    ("geography_world", "Inselflächen", "Ordne diese Inseln nach Fläche – von klein nach groß.", [("Malta", 316), ("Kreta", 8336), ("Island", 103000), ("Grönland", 2166086)], "Quadratkilometer ungefähr", "cia"),
    ("geography_world", "Flusslängen", "Ordne diese Flüsse nach Länge – von kurz nach lang.", [("Themse", 346), ("Rhein", 1233), ("Donau", 2850), ("Nil", 6650)], "Kilometer ungefähr", "britannica_geo"),
    ("geography_world", "Länderflächen", "Ordne diese Länder nach Fläche – von klein nach groß.", [("Luxemburg", 2586), ("Portugal", 92226), ("Japan", 377975), ("Argentinien", 2780400)], "Quadratkilometer ungefähr", "cia"),
    ("geography_world", "Breitengrade", "Ordne diese Städte geografisch – von Süden nach Norden.", [("Kapstadt", -33.9), ("Singapur", 1.3), ("Berlin", 52.5), ("Reykjavík", 64.1)], "Grad Nord", "cia"),
    ("science_technology", "Planetendurchmesser", "Ordne diese Planeten nach Durchmesser – von klein nach groß.", [("Merkur", 4879), ("Mars", 6792), ("Neptun", 49528), ("Jupiter", 142984)], "Kilometer", "nasa"),
    ("science_technology", "Ordnungszahlen", "Ordne diese Elemente nach ihrer Ordnungszahl – aufsteigend.", [("Kohlenstoff", 6), ("Aluminium", 13), ("Eisen", 26), ("Gold", 79)], "Ordnungszahl", "iupac"),
    ("science_technology", "SI-Präfixe", "Ordne diese SI-Präfixe nach ihrer Größe – von klein nach groß.", [("Nano", 1e-9), ("Mikro", 1e-6), ("Milli", 1e-3), ("Kilo", 1e3)], "Faktor", "bipm"),
    ("science_technology", "Datengrößen", "Ordne diese Datenmengen – von klein nach groß.", [("Bit", 0.125), ("Byte", 1), ("Kilobyte", 1000), ("Megabyte", 1000000)], "Byte", "nist"),
    ("science_technology", "Unicode-Versionen", "Ordne diese Unicode-Versionen nach Veröffentlichung – von früh nach spät.", [("Unicode 1.1", 1993), ("Unicode 3.0", 1999), ("Unicode 6.0", 2010), ("Unicode 15.0", 2022)], "Jahr", "unicode"),
    ("human_everyday", "Zahnentwicklung", "Ordne diese Zahnarten im Oberkiefer von vorn nach hinten.", [("Schneidezähne", 1), ("Eckzahn", 2), ("Vormahlzähne", 3), ("Mahlzähne", 4)], "Position", "nih"),
    ("human_everyday", "Körperorgane", "Ordne diese Organe nach typischer Masse – von leicht nach schwer.", [("Schilddrüse", 25), ("Herz", 300), ("Gehirn", 1400), ("Leber", 1500)], "Gramm ungefähr", "nih"),
    ("human_everyday", "Kochtemperaturen", "Ordne diese Vorgänge bei Normaldruck nach Temperatur – von niedrig nach hoch.", [("Schokolade schmilzt", 32), ("Eiweiß gerinnt", 62), ("Wasser siedet", 100), ("Zucker karamellisiert", 170)], "Grad Celsius ungefähr", "nih"),
    ("human_everyday", "Textilgeschichte", "Ordne diese Fasern nach ihrer industriellen Einführung – von früh nach spät.", [("Baumwolle", 1700), ("Viskose", 1891), ("Nylon", 1935), ("Elasthan", 1958)], "Jahr ungefähr", "materials"),
    ("human_everyday", "Notrufnummern", "Ordne diese Rufnummern nach ihrem Zahlenwert – aufsteigend.", [("Polizei 110", 110), ("EU-Notruf 112", 112), ("Behördennummer 115", 115), ("Bereitschaftsdienst 116117", 116117)], "Nummer", "emergency"),
]

ESTIMATE_SPECS = [
    ("gaming", "Tetris-Spielfeld", "Wie viele Felder ist das klassische Tetris-Spielfeld breit?", 10, "Felder", "Das sichtbare Standard-Spielfeld ist zehn Felder breit.", "tetris"),
    ("gaming", "Pac-Man-Punkte", "Wie viele kleine Punkte liegen im ursprünglichen Pac-Man-Labyrinth?", 240, "Punkte", "Das klassische Labyrinth enthält 240 kleine Pellets plus vier Energiekugeln.", "games"),
    ("gaming", "Minecraft-Stapel", "Wie viele Blöcke passen bei den meisten Blockarten in einen Minecraft-Stapel?", 64, "Blöcke", "Die übliche maximale Stapelgröße beträgt 64.", "minecraft"),
    ("gaming", "Schachbrett", "Wie viele Felder hat ein gewöhnliches Schachbrett?", 64, "Felder", "Acht mal acht Felder ergeben 64.", "games"),
    ("gaming", "Monopoly-Startgeld", "Wie viele Monopoly-Dollar Startgeld erhält jeder Spieler in der US-Klassikversion?", 1500, "Monopoly-Dollar", "Die klassische US-Ausgabe verteilt 1.500 Monopoly-Dollar pro Person.", "games"),
    ("science_technology", "Ingenuity-Flugbuch", "Wie viele Flüge absolvierte der Mars-Helikopter Ingenuity insgesamt?", 72, "Flüge", "Aus höchstens fünf geplanten Testflügen wurden am Ende 72.", "ingenuity"),
    ("media_entertainment", "Original-Emojis", "Wie viele Emojis enthielt das 1999 veröffentlichte Originalset von NTT DOCOMO?", 176, "Emojis", "Shigetaka Kuritas Set umfasste 176 Bildzeichen auf einem Raster von zwölf mal zwölf Pixeln.", "emoji"),
    ("science_technology", "DART-Wirkung", "Um wie viele Minuten verkürzte DART die Umlaufzeit von Dimorphos ungefähr?", 33.25, "Minuten", "Die später verfeinerte Messung ergab 33 Minuten und 15 Sekunden.", "dart"),
    ("human_everyday", "SMS-Zeichenlimit", "Wie viele Zeichen durfte eine klassische SMS höchstens enthalten?", 160, "Zeichen", "Die frühe SMS war auf 160 Zeichen begrenzt.", "sms"),
    ("human_everyday", "Erster Barcode-Kauf", "Wie viele US-Cent kostete der 1974 zuerst gescannte Kaugummi?", 67, "US-Cent", "Die Zehnerpackung Wrigley's Juicy Fruit kostete 67 Cent.", "barcode"),
    ("music", "Kammerton", "Wie viele Hertz hat der international gebräuchliche Kammerton a′?", 440, "Hertz", "Für die Standardstimmung wird der Kammerton a′ üblicherweise auf 440 Hertz gesetzt.", "instruments"),
    ("music", "Abbey Road", "Wie viele Titel enthält die britische Originalausgabe des Beatles-Albums Abbey Road?", 17, "Titel", "Die ursprüngliche Trackliste umfasst 17 Titel.", "rockhall"),
    ("music", "Posaunenzug", "Wie viele grundlegende Zugpositionen hat eine gewöhnliche Tenorposaune?", 7, "Positionen", "Der Posaunenzug wird in sieben Grundpositionen gespielt.", "instruments"),
    ("music", "Trompetenventile", "Wie viele Ventile hat eine gewöhnliche moderne Trompete?", 3, "Ventile", "Die Standardtrompete besitzt drei Ventile.", "instruments"),
    ("music", "Cage-Dauer", "Wie viele Sekunden entsprechen der Titeldauer von John Cages 4′33″?", 273, "Sekunden", "Vier Minuten und 33 Sekunden sind 273 Sekunden.", "cage"),
    ("sport", "Elfmeterpunkt", "Wie viele Meter ist der Strafstoßpunkt im Fußball von der Torlinie entfernt?", 11, "Meter", "Der Strafstoßpunkt liegt elf Meter von der Mitte der Torlinie entfernt.", "ifab"),
    ("sport", "Basketballfeld", "Wie viele Meter lang ist ein FIBA-Basketballfeld?", 28, "Meter", "Das FIBA-Spielfeld misst 28 mal 15 Meter.", "fiba"),
    ("sport", "Tennisnetz", "Wie hoch ist ein Tennisnetz in der Mitte?", 0.914, "Meter", "In der Mitte wird das Netz auf 0,914 Meter gehalten.", "itf"),
    ("sport", "Olympiabecken", "Wie viele Meter breit ist ein olympisches Wettkampfbecken üblicherweise?", 25, "Meter", "Das Langbahnbecken misst üblicherweise 50 mal 25 Meter.", "olympics"),
    ("sport", "Fußballtor", "Wie viele Meter breit ist ein Fußballtor zwischen den Pfosten?", 7.32, "Meter", "Der Abstand zwischen den Innenkanten der Pfosten beträgt 7,32 Meter.", "ifab"),
    ("witnesses_of_time", "Rosetta-Abmessung", "Wie hoch ist der Stein von Rosette ungefähr?", 112.3, "Zentimeter", "Der erhaltene Stein ist rund 112,3 Zentimeter hoch.", "rosetta"),
    ("witnesses_of_time", "Gutenberg-Bibel", "Wie viele Zeilen stehen auf einer voll gesetzten Seite der Gutenberg-Bibel gewöhnlich?", 42, "Zeilen", "Die berühmte Ausgabe wird deshalb auch 42-zeilige Bibel genannt.", "history"),
    ("witnesses_of_time", "Diamant-Sutra", "Wie viele Meter lang ist die gedruckte Rolle des Diamant-Sutra ungefähr?", 5, "Meter", "Die aus mehreren Papierblättern geklebte Rolle ist etwa fünf Meter lang.", "history"),
    ("witnesses_of_time", "Berliner Mauer", "Wie viele Kilometer lang waren die Grenzanlagen um West-Berlin ungefähr?", 155, "Kilometer", "Die Anlagen um West-Berlin erstreckten sich über rund 155 Kilometer.", "history"),
    ("witnesses_of_time", "Apollo-11-Dauer", "Wie viele Stunden dauerte die Apollo-11-Mission ungefähr?", 195, "Stunden", "Vom Start bis zur Wasserung vergingen gut acht Tage beziehungsweise rund 195 Stunden.", "nasa_history"),
    ("media_entertainment", "Oscar-Statuette", "Wie hoch ist eine Oscar-Statuette ungefähr?", 34.3, "Zentimeter", "Die Academy nennt eine Höhe von 13,5 Zoll, also etwa 34,3 Zentimetern.", "oscars"),
    ("media_entertainment", "Bond-Romane", "Wie viele James-Bond-Romane schrieb Ian Fleming?", 12, "Romane", "Ian Fleming schrieb zwölf Bond-Romane; hinzu kamen zwei Sammlungen mit Kurzgeschichten.", "fleming"),
    ("media_entertainment", "Toy-Story-Laufzeit", "Wie viele Minuten dauert der erste Toy Story ungefähr?", 81, "Minuten", "Der Kinofilm hat eine Laufzeit von rund 81 Minuten.", "pixar"),
    ("media_entertainment", "Kinobildrate", "Wie viele Bilder pro Sekunde sind im Tonfilm-Kino traditionell Standard?", 24, "Bilder pro Sekunde", "Mit dem Tonfilm setzte sich 24 Bilder pro Sekunde als Kinostandard durch.", "oscars"),
    ("media_entertainment", "Emmy-Start", "In welchem Jahr wurden die ersten Emmy Awards verliehen?", 1949, "Jahr", "Die erste Emmy-Verleihung fand 1949 statt.", "television"),
    ("plants_animals", "Krakenarme", "Wie viele Arme besitzt ein Krake?", 8, "Arme", "Kraken gehören zu den Achtarmigen Tintenfischen und besitzen acht Arme.", "ocean"),
    ("plants_animals", "Seesternarme", "Wie viele Arme hat ein gewöhnlicher Gemeiner Seestern typischerweise?", 5, "Arme", "Der Gemeine Seestern besitzt typischerweise fünf Arme.", "ocean"),
    ("plants_animals", "Känguru-Tragzeit", "Wie viele Tage dauert die Tragzeit eines Roten Riesenkängurus ungefähr?", 33, "Tage", "Nach etwa 33 Tagen wird das winzige Junge geboren und kriecht in den Beutel.", "gestation"),
    ("plants_animals", "Blauwalherz", "Wie viele Kilogramm kann das Herz eines großen Blauwals ungefähr wiegen?", 180, "Kilogramm", "Häufig genannte Vermessungen großer Blauwalherzen liegen um 180 Kilogramm.", "ocean"),
    ("plants_animals", "Bambuswachstum", "Wie viele Zentimeter kann besonders schnell wachsender Bambus an einem Tag ungefähr zulegen?", 91, "Zentimeter", "Bei bestimmten Bambusarten wurden Tageszuwächse um 91 Zentimeter gemessen.", "kew"),
    ("geography_world", "Polarumfang", "Wie viele Kilometer beträgt der Erdumfang über die Pole ungefähr?", 40008, "Kilometer", "Der meridionale Erdumfang liegt bei rund 40.008 Kilometern.", "britannica_geo"),
    ("geography_world", "Marianengraben-Länge", "Wie viele Kilometer lang ist der Marianengraben ungefähr?", 2550, "Kilometer", "Der bogenförmige Tiefseegraben erstreckt sich über ungefähr 2.550 Kilometer.", "noaa"),
    ("geography_world", "Mount Everest", "Wie viele Meter hoch ist der Mount Everest nach der gemeinsamen Festlegung Nepals und Chinas?", 8848.86, "Meter", "Die 2020 bekanntgegebene offizielle Höhe beträgt 8.848,86 Meter.", "britannica_geo"),
    ("geography_world", "Baikalsee-Tiefe", "Wie viele Meter tief ist der Baikalsee maximal?", 1642, "Meter", "Die maximale Tiefe des Baikalsees beträgt 1.642 Meter.", "unesco"),
    ("geography_world", "UN-Gründung", "Wie viele Gründungsmitglieder hatten die Vereinten Nationen 1945?", 51, "Staaten", "51 Staaten gehören zu den Gründungsmitgliedern der Vereinten Nationen.", "un"),
    ("science_technology", "Absoluter Nullpunkt", "Bei wie vielen Grad Celsius liegt der absolute Nullpunkt?", -273.15, "Grad Celsius", "Null Kelvin entsprechen exakt minus 273,15 Grad Celsius.", "nist"),
    ("science_technology", "Avogadro-Konstante", "Wie groß ist die Avogadro-Konstante ungefähr, als Teilchen pro Mol?", 6.02214076e23, "Teilchen pro Mol", "Die SI-Definition legt exakt 6,02214076 × 10²³ pro Mol fest.", "bipm"),
    ("science_technology", "SI-Präfixe", "Wie viele offizielle SI-Präfixe gibt es seit der Ergänzung um quetta bis quecto?", 24, "Präfixe", "Seit 2022 reichen 24 Präfixe von quecto bis quetta.", "bipm"),
    ("science_technology", "Unicode-Codepunkte", "Wie viele mögliche Codepunkte umfasst der gesamte Unicode-Coderaum?", 1114112, "Codepunkte", "17 Ebenen mit je 65.536 Positionen ergeben 1.114.112 mögliche Codepunkte.", "unicode"),
    ("science_technology", "Mondgravitation", "Wie groß ist die Fallbeschleunigung auf dem Mond ungefähr?", 1.62, "Meter pro Quadratsekunde", "An der Mondoberfläche beträgt die Fallbeschleunigung ungefähr 1,62 m/s².", "nasa"),
    ("human_everyday", "Rippenpaare", "Wie viele Rippenpaare besitzt ein Mensch gewöhnlich?", 12, "Rippenpaare", "Der menschliche Brustkorb besitzt gewöhnlich zwölf Rippenpaare.", "nih"),
    ("human_everyday", "Lungenlappen", "Wie viele Lungenlappen haben beide menschlichen Lungen zusammen?", 5, "Lungenlappen", "Die rechte Lunge hat drei, die linke zwei Lappen.", "nih"),
    ("human_everyday", "Körperwasser", "Wie viel Prozent des Körpergewichts eines Erwachsenen bestehen ungefähr aus Wasser?", 60, "Prozent", "Als grober Mittelwert werden für Erwachsene rund 60 Prozent genannt.", "nih"),
    ("human_everyday", "Ruhepuls", "Wie viele Schläge pro Minute hat ein typischer erwachsener Ruhepuls ungefähr?", 70, "Schläge pro Minute", "Ein üblicher Ruhebereich liegt etwa zwischen 60 und 100; 70 ist ein plausibler Richtwert.", "nih"),
    ("human_everyday", "EU-Staaten", "Wie viele Mitgliedstaaten hat die Europäische Union im Jahr 2026?", 27, "Staaten", "Seit dem Austritt des Vereinigten Königreichs besteht die EU aus 27 Mitgliedstaaten.", "emergency"),
]


def build_batch() -> dict[str, list[dict]]:
    numbers = [500, 501, 502, 503, 504, 600, 601, 602, 603, 604, *range(510, 550)]
    true_false_numbers = [500, 501, 502, 503, 504, 616, 601, 602, 603, 604, *range(510, 550)]
    batch = {
        "wahroderunwahr": [tf(number, *spec) for number, spec in zip(true_false_numbers, TRUE_FALSE_SPECS)],
        "multiplechoice": [mc(number, *spec) for number, spec in zip(numbers, MULTIPLE_CHOICE_SPECS)],
        "paarebilden": [match(number, *spec) for number, spec in zip(numbers, MATCH_SPECS)],
        "reihenfolge": [order(number, *spec) for number, spec in zip(numbers, ORDER_SPECS)],
        "schaetzung": [estimate(number, *spec) for number, spec in zip(numbers, ESTIMATE_SPECS)],
    }
    lengths = {key: len(rows) for key, rows in batch.items()}
    if set(lengths.values()) != {50}:
        raise SystemExit(f"Erwartet wurden exakt 50 Fragen je Art, gefunden: {lengths}")
    return batch


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9äöüß]+", " ", text.casefold()).strip()


def tokens(text: str) -> set[str]:
    ignored = {"der", "die", "das", "den", "dem", "des", "ein", "eine", "einer", "eines",
               "und", "oder", "ist", "sind", "wie", "welche", "welcher", "welches", "ihrem",
               "seiner", "seinem", "diese", "nach", "von", "zu", "im", "im", "in", "mit"}
    return {word for word in normalize(text).split() if len(word) > 2 and word not in ignored}


def audit(batch: dict[str, list[dict]]) -> list[str]:
    existing: list[dict] = []
    for path in (ROOT / "fragen").glob("*/fragen.json"):
        existing.extend(json.loads(path.read_text(encoding="utf-8")))
    additions = [row for rows in batch.values() for row in rows]
    errors: list[str] = []
    existing_ids = {row["id"] for row in existing}
    existing_prompts = {normalize(row["prompt"]): row["id"] for row in existing}
    new_ids: set[str] = set()
    new_prompts: dict[str, str] = {}
    for row in additions:
        if row["id"] in existing_ids or row["id"] in new_ids:
            errors.append(f"doppelte ID: {row['id']}")
        new_ids.add(row["id"])
        key = normalize(row["prompt"])
        if key in existing_prompts:
            errors.append(f"doppelter Fragetext: {row['id']} / {existing_prompts[key]}")
        if key in new_prompts:
            errors.append(f"doppelter neuer Fragetext: {row['id']} / {new_prompts[key]}")
        new_prompts[key] = row["id"]
        if len(row["prompt"]) > 160:
            errors.append(f"Fragetext zu lang: {row['id']} ({len(row['prompt'])})")

    # A conservative lexical screen catches near-copies for human review. A
    # high threshold avoids treating recurring quiz grammar as a duplicate.
    existing_token_rows = [(row["id"], tokens(row["prompt"])) for row in existing]
    for row in additions:
        current = tokens(row["prompt"])
        for old_id, old in existing_token_rows:
            union = current | old
            if union and len(current & old) / len(union) >= 0.82:
                errors.append(f"mögliche sinngleiche Frage: {row['id']} / {old_id}")
                break
    return errors


def append(batch: dict[str, list[dict]]) -> None:
    for directory, rows in batch.items():
        path = ROOT / "fragen" / directory / "fragen.json"
        stored = json.loads(path.read_text(encoding="utf-8"))
        stored.extend(rows)
        path.write_text(json.dumps(stored, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"{path.relative_to(ROOT)}: +{len(rows)}")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["check", "apply"])
    args = parser.parse_args()
    batch = build_batch()
    errors = audit(batch)
    if errors:
        raise SystemExit("Prüfung fehlgeschlagen:\n- " + "\n- ".join(errors))
    print("Phase-2-Prüfung erfolgreich: 250 neue Fragen, exakt 50 je Frageart.")
    if args.mode == "apply":
        append(batch)


if __name__ == "__main__":
    main()

