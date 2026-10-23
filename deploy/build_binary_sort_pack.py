"""Build the curated 60-round binary-sort question pack."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "fragen" / "zweigruppenzuordnen" / "fragen.json"
VERIFIED_ON = "2026-10-11"

SOURCES = {
    "banon": [("Gemeinde Banon: Dorf und Käse", "https://banon.fr/village-de-banon/"), ("Gemeinde Chaource: Ort und AOP-Käse", "https://www.chaource.fr/les-atouts-de-la-commune/")],
    "clothing": [("Clothing named after places", "https://en.wikipedia.org/wiki/List_of_clothing_named_after_places")],
    "iba": [("International Bartenders Association: Cocktails", "https://iba-world.com/cocktails/all-cocktails/")],
    "eu_food": [("EU-Register für geografische Angaben", "https://ec.europa.eu/agriculture/eambrosia/geographical-indications-register/")],
    "brands": [("WIPO Global Brand Database", "https://branddb.wipo.int/")],
    "names": [("US Social Security: Vornamendaten", "https://www.ssa.gov/oact/babynames/")],
    "hades": [("Supergiant Games: Hades", "https://www.supergiantgames.com/games/hades/")],
    "pokemon": [("The Pokémon Company: Pokédex", "https://www.pokemon.com/us/pokedex")],
    "minecraft": [("Minecraft: Block-Enzyklopädie", "https://www.minecraft.net/en-us/article/around-block"), ("IUPAC: Periodensystem", "https://iupac.org/what-we-do/periodic-table-of-elements/")],
    "mario": [("Nintendo: Super Mario Figuren", "https://mario.nintendo.com/characters/")],
    "igda": [("International Game Developers Association", "https://igda.org/")],
    "zelda": [("Nintendo: The Legend of Zelda", "https://www.nintendo.com/us/zelda/")],
    "bible": [("Deutsche Bibelgesellschaft: Bibel online", "https://www.die-bibel.de/bibel")],
    "popes": [("Encyclopaedia Britannica: List of popes", "https://www.britannica.com/topic/list-of-popes-2061267")],
    "nasa_asteroids": [("NASA: Asteroids", "https://science.nasa.gov/solar-system/asteroids/")],
    "nasa_moons": [("NASA: Moons", "https://science.nasa.gov/solar-system/moons/")],
    "un": [("Vereinte Nationen: Mitgliedstaaten", "https://www.un.org/en/about-us/member-states")],
    "marvel": [("Marvel: Characters", "https://www.marvel.com/characters")],
    "rockhall": [("Rock & Roll Hall of Fame: Inductees", "https://rockhall.com/inductees/")],
    "usgs": [("USGS: Gazetteer of Planetary Nomenclature", "https://planetarynames.wr.usgs.gov/")],
    "met": [("Metropolitan Opera: Archives", "https://www.metopera.org/discover/archives/")],
    "myth": [("Encyclopaedia Britannica: Greek mythology", "https://www.britannica.com/topic/Greek-mythology")],
    "swift": [("Taylor Swift: Albums", "https://www.taylorswift.com/")],
    "nfl": [("NFL: Teams", "https://www.nfl.com/teams/")],
    "f1": [("Formula 1: Teams", "https://www.formula1.com/en/teams")],
    "fa": [("The Football Association", "https://www.thefa.com/")],
    "olympics": [("Olympics: Sports", "https://www.olympics.com/en/sports/")],
    "nba": [("NBA: Teams", "https://www.nba.com/teams")],
    "golf": [("The R&A: Rules of Golf", "https://www.randa.org/rog/the-rules-of-golf")],
    "africa": [("Encyclopaedia Britannica: Western Africa", "https://www.britannica.com/place/western-Africa")],
    "presidents": [("White House: Presidents", "https://www.whitehouse.gov/about-the-white-house/presidents/")],
    "iwm": [("Imperial War Museums: Second World War", "https://www.iwm.org.uk/history/second-world-war")],
    "nasa_planets": [("NASA: Planets", "https://science.nasa.gov/solar-system/planets/")],
    "fide": [("FIDE: Laws of Chess", "https://handbook.fide.com/chapter/E012023")],
    "europe": [("Encyclopaedia Britannica: History of Europe", "https://www.britannica.com/topic/history-of-Europe")],
    "geo": [("Encyclopaedia Britannica: Geography", "https://www.britannica.com/science/geography")],
    "iho": [("International Hydrographic Organization", "https://iho.int/")],
    "nasa": [("NASA: Missions", "https://www.nasa.gov/missions/")],
    "acm": [("ACM Digital Library", "https://dl.acm.org/")],
    "bipm": [("BIPM: SI Brochure", "https://www.bipm.org/en/publications/si-brochure")],
    "iupac_nasa": [("IUPAC: Periodensystem", "https://iupac.org/what-we-do/periodic-table-of-elements/"), ("NASA: Solar System", "https://science.nasa.gov/solar-system/")],
    "gia": [("GIA: Gem Encyclopedia", "https://www.gia.edu/gem-encyclopedia")],
    "wmo": [("World Meteorological Organization: Cloud Atlas", "https://cloudatlas.wmo.int/")],
    "rhs": [("Royal Horticultural Society: Plants", "https://www.rhs.org.uk/plants")],
    "zoo": [("Smithsonian National Zoo: Animals", "https://nationalzoo.si.edu/animals")],
    "akc": [("American Kennel Club: Dog Breeds", "https://www.akc.org/dog-breeds/")],
    "iau": [("International Astronomical Union: Constellations", "https://www.iau.org/public/themes/constellations/")],
    "kew": [("Kew: Plants of the World Online", "https://powo.science.kew.org/")],
    "apple": [("Apple: macOS releases", "https://support.apple.com/en-us/109033")],
    "oscars": [("Academy Awards: Ceremonies", "https://www.oscars.org/oscars/ceremonies")],
    "xmen": [("Marvel: X-Men", "https://www.marvel.com/teams-and-groups/x-men")],
    "emmys": [("Television Academy: Shows", "https://www.televisionacademy.com/shows")],
    "bond": [("007: The Films", "https://www.007.com/the-films/"), ("Adele: Music", "https://www.adele.com/"), ("Billie Eilish: Music", "https://www.billieeilish.com/music")],
}

# id, category, subtopic, group A, group B, seven items, A/B/X answer codes, source
# X means that the item belongs to both groups.
ROUNDS = [
    (151,"human_everyday","Käse und Ortsnamen","Käsesorte","Ort in Frankreich",["Banon","Chaource","Mimolette","Reblochon","Sisteron","Époisses","Salers"],"XXAABXX","banon"),
    (152,"human_everyday","Kleidung mit Ortsnamen","Kleidung oder Accessoire","Geografischer Ort",["Jersey","Bikini","Cardigan","Balaclava","Parka","Calais","Ushuaia"],"XXXXABB","clothing"),
    (153,"human_everyday","Cocktails und US-Städte","Cocktail","Stadt in den USA",["Manhattan","Bronx","Chicago","Negroni","Daiquiri","Seattle","Philadelphia"],"XXXAABB","iba"),
    (154,"human_everyday","Italienische Käse und Orte","Italienischer Käse","Ort in Italien",["Asiago","Gorgonzola","Taleggio","Fontina","Burrata","Verona","Matera"],"XXXAABB","eu_food"),
    (155,"human_everyday","Marken und Geografie","Konsumgütermarke","Geografischer Name",["Amazon","Patagonia","Fiji","Apple","Dove","Nile","Sahara"],"XXXAABB","brands"),
    (156,"human_everyday","Monate und Vornamen","Englischer Monatsname","Vorname",["April","May","June","August","October","Maria","Kevin"],"XXXXABB","names"),
    (157,"gaming","Hades und griechische Mythologie","Figur aus dem Spiel Hades","Mythologische Gestalt",["Zagreus","Hades","Nyx","Thanatos","Skelly","Achilles","Odysseus"],"XXXXAXB","hades"),
    (158,"gaming","Pokémon und englische Wörter","Pokémon","Englisches Wort",["Ditto","Persian","Mew","Slowpoke","Electrode","Pikachu","Umbrella"],"XXXXXAB","pokemon"),
    (159,"gaming","Minecraft und Elemente","Material in Minecraft","Chemisches Element",["Gold","Iron","Copper","Coal","Redstone","Neon","Argon"],"XXXAABB","minecraft"),
    (160,"gaming","Mario und englische Wörter","Figur aus Super Mario","Englisches Wort",["Peach","Daisy","Toad","Bowser","Yoshi","Goomba","Lantern"],"XXXXAAB","mario"),
    (161,"gaming","Spielestudios und Wörter","Spielestudio","Englisches Wort",["Blizzard","Valve","Remedy","Gearbox","Ubisoft","Bungie","Thunder"],"XXXXAAB","igda"),
    (162,"gaming","Zelda und englische Wörter","Figur oder Rolle aus Zelda","Englisches Wort",["Link","Guardian","Champion","Sage","Midna","Impa","Lantern"],"XXXXAAB","zelda"),
    (163,"faith_religion","Bibelbücher und Personen","Bibelbuch","Person in der Bibel",["Ruth","Esther","Samuel","Joshua","Genesis","Exodus","Miriam"],"XXXXAAB","bible"),
    (164,"faith_religion","Päpste und römische Kaiser","Papstname","Römischer Kaisername",["Hadrian","Konstantin","Marcus","Leo","Gregor","Trajan","Augustus"],"XXXXABB","popes"),
    (165,"faith_religion","Antike Gottheiten und Asteroiden","Antike Gottheit","Asteroid",["Ceres","Vesta","Juno","Pallas","Eros","Zeus","Bennu"],"XXXXXAB","nasa_asteroids"),
    (166,"faith_religion","Engelnamen und Monde","Engelname","Mond",["Ariel","Gabriel","Michael","Metatron","Titan","Miranda","Europa"],"XAAABBB","nasa_moons"),
    (167,"faith_religion","Biblische Orte und Staaten","Biblischer Ortsname","Heutiger Staat",["Israel","Zypern","Libanon","Ägypten","Syrien","Kanaan","Frankreich"],"XXXXXAB","bible"),
    (168,"faith_religion","Nordische Mythologie und Marvel","Nordische Gottheit","MCU-Figur",["Thor","Loki","Odin","Frigg","Tyr","Groot","Thanos"],"XXXAABB","marvel"),
    (169,"music","Bands und US-Orte","Band","US-Ortsname",["Boston","Chicago","Kansas","Alabama","Nirvana","Metallica","Seattle"],"XXXXAAB","rockhall"),
    (170,"music","Bands und Lebensmittelwörter","Band","Englisches Lebensmittelwort",["Cream","Bread","Cake","Wings","Queen","Rice","Soup"],"XXXXABB","rockhall"),
    (171,"music","Komponisten und Merkurkrater","Komponist","Merkurkrater",["Beethoven","Bach","Chopin","Debussy","Mozart","Hans Zimmer","Kuiper"],"XXXXXAB","usgs"),
    (172,"music","Operntitel und Vornamen","Operntitel","Weiblicher Vorname",["Carmen","Aida","Norma","Tosca","Rigoletto","Maria","Sabine"],"XXXXABB","met"),
    (173,"music","Bands und Mythologie","Band","Mythologischer Begriff",["Phoenix","Muse","Styx","Nirvana","ABBA","Medusa","Minotaur"],"XXXAABB","myth"),
    (174,"music","Taylor-Swift-Alben und Farben","Taylor-Swift-Album","Englischer Farbname",["Red","1989","Midnights","Lover","Blue","Magenta","Turquoise"],"XAAABBB","swift"),
    (175,"sport","NFL und Vögel","NFL-Teamname","Englischer Vogelname",["Eagles","Falcons","Ravens","Cardinals","Jets","Packers","Kestrels"],"XXXXAAB","nfl"),
    (176,"sport","Formel 1 und Automarken","Formel-1-Konstrukteur","Straßenautomarke",["Ferrari","Mercedes","McLaren","Aston Martin","Haas","Williams","Volvo"],"XXXXAAB","f1"),
    (177,"sport","Fußballclubs und London","Englischer Fußballclub","Londoner Stadtteil",["Chelsea","Fulham","Tottenham","Brentford","Wimbledon","Liverpool","Croydon"],"XXXXXAB","fa"),
    (178,"sport","Olympia und Tanz","Olympische Sportart","Tanzstil",["Breaking","Boxing","Fencing","Skateboarding","Waltz","Tango","Salsa"],"XAAABBB","olympics"),
    (179,"sport","Teamnamen und Tiere","NBA- oder NFL-Teamname","Englischer Tiername",["Bulls","Bears","Dolphins","Panthers","Lakers","Packers","Badgers"],"XXXXAAB","nba"),
    (180,"sport","Golf und Vögel","Golfbegriff","Englischer Vogelname",["Eagle","Albatross","Condor","Birdie","Bogey","Sparrow","Kestrel"],"XXXAABB","golf"),
    (181,"witnesses_of_time","Reiche und heutige Staaten","Historisches afrikanisches Reich","Heutiger Staat",["Mali","Ghana","Benin","Äthiopien","Songhai","Togo","Kenia"],"XXXXABB","africa"),
    (182,"witnesses_of_time","US-Präsidenten und Städte","Nachname eines US-Präsidenten","US-Stadt",["Washington","Lincoln","Cleveland","Madison","Obama","Seattle","Dallas"],"XXXXABB","presidents"),
    (183,"witnesses_of_time","Operationen des Zweiten Weltkriegs","Militäroperation im Zweiten Weltkrieg","Englisches Alltagswort",["Torch","Mincemeat","Compass","Avalanche","Citadel","Bagration","Spoon"],"XXXXXAB","iwm"),
    (184,"witnesses_of_time","Römische Götter und Planeten","Römische Gottheit","Englischer Planetenname",["Mercury","Venus","Mars","Jupiter","Saturn","Vulcan","Earth"],"XXXXXAB","nasa_planets"),
    (185,"witnesses_of_time","Historische Titel und Schach","Historischer Titel","Englischer Schachbegriff",["King","Queen","Bishop","Knight","Emperor","Rook","Pawn"],"XXXXABB","fide"),
    (186,"witnesses_of_time","Herrscherhäuser und Orte","Europäisches Herrscherhaus","Geografischer Ort",["York","Lancaster","Windsor","Hannover","Bourbon","Plantagenet","Bremen"],"XXXXXAB","europe"),
    (187,"geography_world","Flüsse und Staaten","Fluss","Heutiger Staat",["Kongo","Niger","Senegal","Gambia","Uruguay","Amazonas","Laos"],"XXXXXAB","un"),
    (188,"geography_world","Inseln und Staaten","Insel","Heutiger Staat",["Zypern","Malta","Island","Bahrain","Madagaskar","Borneo","Nepal"],"XXXXXAB","un"),
    (189,"geography_world","Staaten und Vornamen","Englischer Staatsname","Vorname",["Georgia","Jordan","Chad","Dominica","India","Nepal","Kevin"],"XXXXXAB","names"),
    (190,"geography_world","Orte und Automodelle","Automodell","Geografischer Ort",["Tucson","Tacoma","Cayenne","Ibiza","Aspen","Golf","Lissabon"],"XXXXXAB","geo"),
    (191,"geography_world","Meere und Farben","Teil eines Meeresnamens","Englisches Farbwort",["Black","Red","White","Yellow","Coral","Baltic","Purple"],"XXXXXAB","iho"),
    (192,"geography_world","Seen und Staaten","Name eines Sees","Heutiger Staat",["Tschad","Malawi","Nicaragua","Victoria","Superior","Ruanda","Nepal"],"XXXAABB","geo"),
    (193,"science_technology","Raumfahrt und Mythologie","NASA-Mission","Mythologische Gestalt",["Apollo","Artemis","Juno","Psyche","Voyager","Lucy","Athena"],"XXXXAAB","nasa"),
    (194,"science_technology","Programmiersprachen und Schlangen","Programmiersprache","Englischer Schlangenname",["Python","Cobra","Boa","Julia","Rust","Mamba","Anaconda"],"XXXAABB","acm"),
    (195,"science_technology","Maßeinheiten und Forschende","Maßeinheit","Nachname eines Forschers",["Newton","Pascal","Watt","Joule","Kelvin","Meter","Einstein"],"XXXXXAB","bipm"),
    (196,"science_technology","Elemente und Himmelskörper","Englischer Elementname","Himmelskörper",["Mercury","Helium","Uranium","Neon","Mars","Ceres","Titan"],"XAAABBB","iupac_nasa"),
    (197,"science_technology","Edelsteine und Farben","Englischer Edelsteinname","Englischer Farbname",["Amber","Jade","Ruby","Emerald","Sapphire","Diamond","Magenta"],"XXXXXAB","gia"),
    (198,"science_technology","Wolken und Automodelle","Wolkengattung","Automodell",["Stratus","Cirrus","Cumulus","Altostratus","Mustang","Golf","Fiesta"],"XXAABBB","wmo"),
    (199,"plants_animals","Blumen und Vornamen","Blume oder Blütenpflanze","Vorname",["Rose","Iris","Lily","Daisy","Heather","Tulip","Kevin"],"XXXXXAB","rhs"),
    (200,"plants_animals","Tiere und Autos","Englischer Tiername","Automarke oder Automodell",["Beetle","Mustang","Puma","Jaguar","Panda","Platypus","Golf"],"XXXXXAB","zoo"),
    (201,"plants_animals","Hunderassen und Regionen","Englischer Hunderassenname","Geografische Region",["Labrador","Newfoundland","Chihuahua","Brittany","Beagle","Sahara","Patagonia"],"XXXXABB","akc"),
    (202,"plants_animals","Vögel und Sternbilder","Deutscher Vogelname","Deutscher Sternbildname",["Adler","Schwan","Pfau","Kranich","Rabe","Spatz","Dreieck"],"XXXXXAB","iau"),
    (203,"plants_animals","Pflanzen und griechische Mythologie","Botanische Gattung","Mythologische Gestalt",["Narcissus","Adonis","Iris","Daphne","Hyacinthus","Tulipa","Zeus"],"XXXXXAB","kew"),
    (204,"plants_animals","Raubtiere und macOS","Englischer Tiername","Apple-Betriebssystemversion",["Cheetah","Puma","Jaguar","Panther","Leopard","Ocelot","Ventura"],"XXXXXAB","apple"),
    (205,"media_entertainment","Filmtitel und Städte","Spielfilmtitel","Stadt",["Chicago","Casablanca","Philadelphia","Munich","Fargo","Titanic","Lissabon"],"XXXXXAB","oscars"),
    (206,"media_entertainment","X-Men und englische Wörter","X-Men-Figur","Englisches Wort",["Storm","Rogue","Beast","Angel","Cyclops","Magneto","Umbrella"],"XXXXXAB","xmen"),
    (207,"media_entertainment","Disney und Astronomie","Disney-Figur","Himmelskörper",["Pluto","Ariel","Triton","Elsa","Simba","Europa","Titan"],"XXXAABB","nasa_moons"),
    (208,"media_entertainment","Comicfiguren und Mythologie","Comicfigur","Mythologische Gestalt",["Thor","Hercules","Loki","Wonder Woman","Batman","Achilles","Athena"],"XXXAABB","marvel"),
    (209,"media_entertainment","Serientitel und Orte","Fernsehserie","Geografischer Ort",["Fargo","Dallas","Rome","Versailles","Berlin","Lost","Lissabon"],"XXXXXAB","emmys"),
    (210,"media_entertainment","James Bond und Popsongs","James-Bond-Film","Song von Adele oder Billie Eilish",["Skyfall","Goldfinger","Spectre","Casino Royale","Hello","Easy on Me","No Time to Die"],"XAAABBX","bond"),
]


def build() -> list[dict]:
    questions = []
    for number, category, subtopic, group_a, group_b, items, codes, source_key in ROUNDS:
        assert len(items) == 7 and len(set(items)) == 7
        assert len(codes) == 7 and {"A", "B", "X"} <= set(codes)
        answer = {item: ("both" if code == "X" else code) for item, code in zip(items, codes)}
        both = [item for item, code in zip(items, codes) if code == "X"]
        only_a = [item for item, code in zip(items, codes) if code == "A"]
        only_b = [item for item, code in zip(items, codes) if code == "B"]
        references = [{"title": title, "url": url} for title, url in SOURCES[source_key]]
        questions.append({
            "id": f"bs{number}", "question_type": "binary_sort",
            "primary_category": category, "subtopic": subtopic,
            "tags": {"topics": [subtopic], "entities": [], "genres": [], "regions": [], "eras": []},
            "source": {"status": "verified", "verified_on": VERIFIED_ON, "references": references},
            "subject_keys": [f"binary-sort:{number}"],
            "prompt": f"{group_a}, {group_b} oder beides?",
            "groups": {"A": group_a, "B": group_b}, "items": items, "answer": answer,
            "explanation": f"Beides: {', '.join(both)}. Nur {group_a}: {', '.join(only_a)}. Nur {group_b}: {', '.join(only_b)}.",
        })
    assert len(questions) == 60
    assert len({question["id"] for question in questions}) == 60
    return questions


if __name__ == "__main__":
    OUTPUT.write_text(json.dumps(build(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(ROUNDS)} Runden nach {OUTPUT} geschrieben.")
