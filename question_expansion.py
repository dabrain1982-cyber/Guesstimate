"""Additional curated questions, generated from compact verified fact tables."""

from __future__ import annotations

import hashlib


def _options(values, index):
    picks = [values[index], values[(index + 3) % len(values)], values[(index + 6) % len(values)], values[(index + 8) % len(values)]]
    ordered = sorted(dict.fromkeys(picks), key=lambda value: hashlib.sha256(f"{index}:{value}".encode()).hexdigest())
    while len(ordered) < 4:
        candidate = values[(index + len(ordered) + 1) % len(values)]
        if candidate not in ordered:
            ordered.append(candidate)
    return {key: value for key, value in zip("ABCD", ordered)}


MC_GROUPS = [
    ("Welche Hauptstadt gehört zu {left}?", "{left} hat {right} als Hauptstadt.", [("Neuseeland","Wellington"),("Marokko","Rabat"),("Finnland","Helsinki"),("Chile","Santiago"),("Vietnam","Hanoi"),("Irland","Dublin"),("Kenia","Nairobi"),("Portugal","Lissabon"),("Kanada","Ottawa"),("Mongolei","Ulaanbaatar")]),
    ("Welches chemische Symbol gehört zu {left}?", "Das Elementsymbol von {left} ist {right}.", [("Kalium","K"),("Silber","Ag"),("Blei","Pb"),("Zinn","Sn"),("Kupfer","Cu"),("Helium","He"),("Calcium","Ca"),("Wolfram","W"),("Quecksilber","Hg"),("Kobalt","Co")]),
    ("Wer schrieb „{left}“?", "„{left}“ stammt von {right}.", [("Der Prozess","Franz Kafka"),("Stolz und Vorurteil","Jane Austen"),("Der alte Mann und das Meer","Ernest Hemingway"),("Moby-Dick","Herman Melville"),("Der kleine Prinz","Antoine de Saint-Exupéry"),("Faust","Johann Wolfgang von Goethe"),("Frankenstein","Mary Shelley"),("Der Name der Rose","Umberto Eco"),("Die Schatzinsel","Robert Louis Stevenson"),("Madame Bovary","Gustave Flaubert")]),
    ("Wer schuf das Kunstwerk „{left}“?", "„{left}“ wurde von {right} geschaffen.", [("Guernica","Pablo Picasso"),("Das Mädchen mit dem Perlenohrring","Jan Vermeer"),("Die Beständigkeit der Erinnerung","Salvador Dalí"),("Der Kuss","Gustav Klimt"),("Die Nachtwache","Rembrandt"),("Seerosen","Claude Monet"),("American Gothic","Grant Wood"),("Die Geburt der Venus","Sandro Botticelli"),("Der Denker","Auguste Rodin"),("Nighthawks","Edward Hopper")]),
    ("In welcher Einheit wird {left} gemessen?", "{left} wird in {right} gemessen.", [("elektrischer Widerstand","Ohm"),("Frequenz","Hertz"),("Kraft","Newton"),("Energie","Joule"),("Druck","Pascal"),("Lichtstärke","Candela"),("Temperatur im SI-System","Kelvin"),("elektrische Ladung","Coulomb"),("magnetische Flussdichte","Tesla"),("Radioaktivität","Becquerel")]),
    ("In welcher Stadt steht {left}?", "{left} befindet sich in {right}.", [("die Christusstatue Cristo Redentor","Rio de Janeiro"),("der Schiefe Turm","Pisa"),("die Hagia Sophia","Istanbul"),("der CN Tower","Toronto"),("die Akropolis","Athen"),("der Fernsehturm Oriental Pearl","Shanghai"),("das Burj al Arab","Dubai"),("die Karlsbrücke","Prag"),("der Trevi-Brunnen","Rom"),("das Rijksmuseum","Amsterdam")]),
    ("Welches Land gilt als Ursprungsland von {left}?", "{left} wird mit {right} als Ursprungsland verbunden.", [("Sushi","Japan"),("Paella","Spanien"),("Gulasch","Ungarn"),("Kimchi","Korea"),("Tacos","Mexiko"),("Fondue","Schweiz"),("Moussaka","Griechenland"),("Feijoada","Brasilien"),("Tom Yum","Thailand"),("Hummus","Naher Osten")]),
    ("Wer wird mit der Entwicklung von {left} verbunden?", "{right} wird mit {left} verbunden.", [("dem World Wide Web","Tim Berners-Lee"),("der Brailleschrift","Louis Braille"),("dem Dieselmotor","Rudolf Diesel"),("der modernen Klimaanlage","Willis Carrier"),("dem Dynamit","Alfred Nobel"),("dem ersten praktikablen Telefon","Alexander Graham Bell"),("dem Klettverschluss","George de Mestral"),("dem Sicherheitsaufzug","Elisha Otis"),("der ersten mechanischen Rechenmaschine","Blaise Pascal"),("dem modernen Kugelschreiber","László Bíró")]),
    ("Wie heißt der Fachbegriff für {left}?", "Der Fachbegriff lautet {right}.", [("die Lehre von Pilzen","Mykologie"),("die Wissenschaft von Erdbeben","Seismologie"),("die Lehre von Vögeln","Ornithologie"),("die Erforschung von Insekten","Entomologie"),("die Lehre von Karten","Kartografie"),("die Wissenschaft vom Wetter","Meteorologie"),("die Lehre von Sternen und Weltall","Astronomie"),("die Erforschung alter Kulturen durch Funde","Archäologie"),("die Lehre von Vererbung","Genetik"),("die Lehre von Meeren","Ozeanografie")]),
    ("Welches Tier ist für {left} bekannt?", "{right} ist dafür bekannt.", [("den längsten Hals","die Giraffe"),("elektrische Entladungen zur Verteidigung","der Zitteraal"),("Werkzeuggebrauch mit Steinen","der Seeotter"),("Echoortung in völliger Dunkelheit","die Fledermaus"),("Farbwechsel zur Tarnung","das Chamäleon"),("die größte Spannweite unter lebenden Vögeln","der Wanderalbatros"),("extrem langsamen Stoffwechsel","das Faultier"),("Stacheln aus umgebildeten Haaren","das Stachelschwein"),("Bauten mit Dämmen","der Biber"),("eine sehr lange klebrige Zunge","der Ameisenbär")]),
]

MC_KNOWLEDGE_CATEGORIES = [
    "geography",
    "science_nature",
    "arts_literature",
    "arts_literature",
    "science_nature",
    "geography",
    "sports_leisure",
    "science_nature",
    "science_nature",
    "science_nature",
]


def build_multiple_choice():
    questions = []
    number = 41
    for group_index, (prompt, explanation, pairs) in enumerate(MC_GROUPS):
        values = [right for _, right in pairs]
        for index, (left, right) in enumerate(pairs):
            choices = _options(values, index)
            answer = next(key for key, value in choices.items() if value == right)
            subject_keys = [f"subject:{left.casefold()}"]
            subject_keys.extend(f"entity:{value.casefold()}" for value in choices.values())
            questions.append({"id": f"mc{number:03d}", "prompt": prompt.format(left=left), "options": choices, "answer": answer, "explanation": explanation.format(left=left, right=right), "subject_keys": subject_keys, "knowledge_category": MC_KNOWLEDGE_CATEGORIES[group_index]})
            number += 1
    return questions


def build_true_false():
    questions = []
    number = 41
    for group_index, (_, _, pairs) in enumerate(MC_GROUPS):
        for index, (left, right) in enumerate(pairs):
            truth = (group_index + index) % 2 == 0
            shown = right if truth else pairs[(index + 1) % len(pairs)][1]
            if group_index == 0:
                prompt = f"{shown} ist die Hauptstadt von {left}."
                explanation = f"Die Hauptstadt von {left} ist {right}."
            elif group_index == 1:
                prompt = f"Das chemische Symbol von {left} lautet {shown}."
                explanation = f"{left} trägt das Symbol {right}."
            elif group_index == 2:
                prompt = f"„{left}“ wurde von {shown} geschrieben."
                explanation = f"Das Werk stammt von {right}."
            elif group_index == 3:
                prompt = f"Das Kunstwerk „{left}“ stammt von {shown}."
                explanation = f"Geschaffen wurde es von {right}."
            elif group_index == 4:
                prompt = f"{left.capitalize()} wird in {shown} gemessen."
                explanation = f"Die passende Einheit ist {right}."
            elif group_index == 5:
                prompt = f"{left.capitalize()} befindet sich in {shown}."
                explanation = f"Der richtige Ort ist {right}."
            elif group_index == 6:
                prompt = f"{left} stammt ursprünglich aus {shown}."
                explanation = f"Als Ursprungsregion gilt {right}."
            elif group_index == 7:
                prompt = f"{shown} wird mit {left} verbunden."
                explanation = f"Damit verbunden wird {right}."
            elif group_index == 8:
                prompt = f"Der Fachbegriff für {left} lautet {shown}."
                explanation = f"Richtig ist {right}."
            else:
                prompt = f"Für {left} ist {shown} bekannt."
                explanation = f"Das gesuchte Tier ist {right}."
            subject_keys = {
                f"subject:{left.casefold()}",
                f"entity:{shown.casefold()}",
                f"entity:{right.casefold()}",
            }
            questions.append({"id": f"tf{number:03d}", "prompt": prompt, "answer": truth, "explanation": explanation, "subject_keys": sorted(subject_keys), "knowledge_category": MC_KNOWLEDGE_CATEGORIES[group_index]})
            number += 1
    return questions


MATCH_GROUPS = [
    ("Ordne das Land seiner Hauptstadt zu.", MC_GROUPS[0][2]),
    ("Ordne das Element seinem Symbol zu.", MC_GROUPS[1][2]),
    ("Ordne das Werk seinem Autor oder seiner Autorin zu.", MC_GROUPS[2][2]),
    ("Ordne das Kunstwerk der richtigen Person zu.", MC_GROUPS[3][2]),
    ("Ordne die Messgröße ihrer Einheit zu.", MC_GROUPS[4][2]),
    ("Ordne das Wahrzeichen seiner Stadt zu.", MC_GROUPS[5][2]),
    ("Ordne das Gericht seiner Herkunft zu.", MC_GROUPS[6][2]),
    ("Ordne die Entwicklung der verbundenen Person zu.", MC_GROUPS[7][2]),
    ("Ordne das Forschungsgebiet seinem Fachbegriff zu.", MC_GROUPS[8][2]),
    ("Ordne die Besonderheit dem Tier zu.", MC_GROUPS[9][2]),
]


def build_match():
    questions = []
    number = 41
    patterns = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9, 0, 4), (1, 5, 8), (2, 6, 9), (0, 3, 7), (1, 4, 9), (2, 5, 7), (3, 6, 8)]
    for group_index, (prompt, pairs) in enumerate(MATCH_GROUPS):
        for pattern in patterns:
            chosen = [pairs[index] for index in pattern]
            left = [item[0] for item in chosen]
            right = [item[1] for item in chosen]
            answer = dict(chosen)
            subject_keys = [f"subject:{item.casefold()}" for item in left]
            subject_keys.extend(f"entity:{item.casefold()}" for item in right)
            questions.append({"id": f"ma{number:03d}", "prompt": prompt, "left": left, "right": right, "answer": answer, "explanation": "; ".join(f"{a} – {b}" for a, b in chosen) + ".", "subject_keys": subject_keys, "knowledge_category": MC_KNOWLEDGE_CATEGORIES[group_index]})
            number += 1
    return questions


FACT_GROUPS = [
    ("Ordne die Ereignisse vom frühesten zum spätesten.", "In welchem Jahr geschah: {label}?", "Jahr", [("Kolumbus erreicht Amerika",1492),("Luthers Thesenanschlag",1517),("Unabhängigkeitserklärung der USA",1776),("Französische Revolution beginnt",1789),("erstes Telefonat Bells",1876),("erste moderne Olympische Spiele",1896),("Titanic sinkt",1912),("Ende des Zweiten Weltkriegs",1945),("erste Mondlandung",1969),("Fall der Berliner Mauer",1989)]),
    ("Ordne die Bauwerke vom niedrigsten zum höchsten.", "Wie hoch ist {label} ungefähr?", "Meter", [("Brandenburger Tor",26),("Freiheitsstatue mit Sockel",93),("Big Ben mit Turm",96),("Kölner Dom",157),("Washington Monument",169),("Eiffelturm",330),("Empire State Building mit Antenne",443),("CN Tower",553),("Shanghai Tower",632),("Burj Khalifa",828)]),
    ("Ordne die Flüsse vom kürzesten zum längsten.", "Wie lang ist {label} ungefähr?", "km", [("Themse",346),("Spree",400),("Elbe",1094),("Rhein",1233),("Donau",2850),("Wolga",3530),("Kongo",4700),("Mississippi-Missouri",6275),("Jangtsekiang",6300),("Nil",6650)]),
    ("Ordne die Länder nach Fläche – vom kleinsten zum größten.", "Wie groß ist die Fläche von {label} ungefähr?", "km²", [("Island",103000),("Griechenland",132000),("Nepal",147000),("Tunesien",164000),("Uruguay",176000),("Vereinigtes Königreich",244000),("Italien",301000),("Deutschland",358000),("Japan",378000),("Schweden",450000)]),
    ("Ordne die Tiere nach Spitzengeschwindigkeit – von langsamer zu schneller.", "Welche Spitzengeschwindigkeit erreicht {label} ungefähr?", "km/h", [("Faultier",0.3),("Riesenschildkröte",0.5),("Mensch im Sprint",45),("Elefant",40),("Hauskatze",48),("Giraffe",60),("Strauß",70),("Löwe",80),("Gepard",100),("Wanderfalke im Sturzflug",320)]),
    ("Ordne die Entfernungen von klein nach groß.", "Wie groß ist die mittlere Entfernung: {label}?", "km", [("Erde–ISS",400),("Berlin–München Luftlinie",505),("Berlin–Paris Luftlinie",880),("Erde–Mond",384400),("Sonne–Merkur",57900000),("Sonne–Venus",108200000),("Sonne–Erde",149600000),("Sonne–Mars",227900000),("Sonne–Jupiter",778500000),("Sonne–Saturn",1433000000)]),
    ("Ordne die Stoffe nach Schmelzpunkt – von niedrig zu hoch.", "Bei wie viel Grad Celsius schmilzt {label} ungefähr?", "°C", [("Quecksilber",-39),("Eis",0),("Schokolade",34),("Zinn",232),("Blei",327),("Aluminium",660),("Silber",962),("Gold",1064),("Kupfer",1085),("Eisen",1538)]),
    ("Ordne die technischen Meilensteine von früher nach später.", "In welchem Jahr fand dieser technische Meilenstein statt: {label}?", "Jahr", [("Gutenbergs Buchdruck mit beweglichen Lettern",1450),("Watts Patent für seine verbesserte Dampfmaschine",1769),("Daguerres öffentliche Vorstellung seines Fotografieverfahrens",1839),("Bells Telefonpatent",1876),("Edisons Vorstellung seiner praktischen Glühlampe",1879),("Benz' Patent für sein Automobil",1886),("erster Motorflug der Brüder Wright",1903),("Bairds öffentliche Vorführung seines Fernsehsystems",1926),("Tim Berners-Lees Plan für das World Wide Web",1989),("Vorstellung des ersten iPhones",2007)]),
    ("Ordne die Werke nach Erstveröffentlichung.", "In welchem Jahr erschien {label} erstmals?", "Jahr", [("Don Quijote Teil 1",1605),("Robinson Crusoe",1719),("Stolz und Vorurteil",1813),("Frankenstein",1818),("Moby-Dick",1851),("Die Verwandlung",1915),("Der große Gatsby",1925),("1984",1949),("Der Herr der Ringe Band 1",1954),("Harry Potter Band 1",1997)]),
    ("Ordne die sportlichen Distanzen von kurz nach lang.", "Wie lang ist {label} genau oder ungefähr?", "Meter", [("Basketballfeld",28),("Olympisches Schwimmbecken",50),("Fußballfeld Standardlänge",105),("Leichtathletik-Runde",400),("Ruderregatta olympisch",2000),("5-km-Lauf",5000),("10-km-Lauf",10000),("Halbmarathon",21097.5),("Marathon",42195),("100-km-Ultramarathon",100000)]),
]

FACT_KNOWLEDGE_CATEGORIES = [
    "history",
    "geography",
    "geography",
    "geography",
    "science_nature",
    "science_nature",
    "science_nature",
    "science_nature",
    "arts_literature",
    "sports_leisure",
]


def build_order():
    questions = []
    number = 41
    patterns = [(0,2,5,9),(1,3,6,8),(0,4,7,9),(2,3,5,8),(1,4,6,9),(0,3,7,8),(1,2,6,7),(2,4,5,9),(0,1,5,8),(3,4,7,9)]
    for group_index, (prompt, _, _, facts) in enumerate(FACT_GROUPS):
        for pattern in patterns:
            answer = [facts[index][0] for index in pattern]
            answer.sort(key=lambda label: next(value for item, value in facts if item == label))
            items = sorted(answer, key=lambda value: hashlib.sha256(f"{number}:{value}".encode()).hexdigest())
            questions.append({"id": f"or{number:03d}", "prompt": prompt, "items": items, "answer": answer, "explanation": "Richtig: " + " → ".join(answer) + ".", "subject_keys": [f"fact:{group_index}:{label.casefold()}" for label in answer], "knowledge_category": FACT_KNOWLEDGE_CATEGORIES[group_index]})
            number += 1
    return questions


def build_estimate():
    questions = []
    number = 41
    for group_index, (_, prompt, unit, facts) in enumerate(FACT_GROUPS):
        for label, value in facts:
            question_prompt = prompt.format(label=label)
            answer, answer_unit = value, unit
            if value < 0:
                question_prompt = f"Wie viele Grad Celsius unter null liegt der Schmelzpunkt von {label}?"
                answer, answer_unit = abs(value), "Grad unter null"
            elif value == 0:
                question_prompt = "Bei wie viel Kelvin gefriert reines Wasser ungefähr?"
                answer, answer_unit = 273.15, "Kelvin"
            questions.append({"id": f"es{number:03d}", "prompt": question_prompt, "answer": answer, "unit": answer_unit, "explanation": f"Der gesuchte Richtwert beträgt {answer:g} {answer_unit}.", "subject_keys": [f"fact:{group_index}:{label.casefold()}"], "knowledge_category": FACT_KNOWLEDGE_CATEGORIES[group_index]})
            number += 1
    return questions


EXTRA_QUESTION_BANK = {
    "multiple_choice": build_multiple_choice(),
    "true_false": build_true_false(),
    "estimate": build_estimate(),
    "order": build_order(),
    "match": build_match(),
}
