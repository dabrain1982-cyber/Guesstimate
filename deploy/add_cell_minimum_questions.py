"""Retired audit record of the rejected cell-quota question generator.

This file is deliberately kept so the origin of the removed questions remains
traceable. It must not be used to modify the active question library: forcing
every question type into every topic produced unsuitable questions, especially
for true/false. The active rollback is documented in
``deactivate_cell_minimum_questions.py``.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "fragen"
MANIFEST = json.loads((LIBRARY / "manifest.json").read_text(encoding="utf-8"))
ACTIVE_TYPES = tuple(MANIFEST["round_order"])
TYPE_DIRS = {key: value["directory"] for key, value in MANIFEST["question_types"].items()}
CATEGORY_DIRS = {key: value["directory"] for key, value in MANIFEST["categories"].items()}
PREFIXES = {
    "multiple_choice": "mc",
    "true_false": "tf",
    "match": "ma",
    "order": "or",
    "estimate": "es",
}

TARGET = 25


def ref(title: str, url: str) -> dict[str, str]:
    return {"title": title, "url": url}


SOURCES = {
    "gaming": [
        ref("PlayStation history: PlayStation", "https://www.playstation.com/en-us/playstation-history/1994-ps-one/"),
        ref("PlayStation history: PS2 and PSP", "https://www.playstation.com/en-us/playstation-history/2000-ps2-psp/"),
        ref("PlayStation history: PS3 and PS Vita", "https://www.playstation.com/en-us/playstation-history/2007-ps3-ps-vita/"),
        ref("PlayStation history: PS4 and PS VR", "https://www.playstation.com/en-us/playstation-history/2013-ps4-ps-vr/"),
    ],
    "faith_religion": [
        ref("Encyclopaedia Britannica: Christianity", "https://www.britannica.com/topic/Christianity"),
        ref("Encyclopaedia Britannica: Islam", "https://www.britannica.com/topic/Islam"),
        ref("Encyclopaedia Britannica: Buddhism", "https://www.britannica.com/topic/Buddhism"),
        ref("SQA: World Religions", "https://www.sqa.org.uk/sqa/files_ccc/N2USNRMEWorldReligions.pdf"),
    ],
    "music": [
        ref("Rock & Roll Hall of Fame: induction classes", "https://rockhall.com/inductees/classes/"),
        ref("Encyclopaedia Britannica: Western music", "https://www.britannica.com/art/Western-music"),
        ref("Goethe-Institut: Neue Deutsche Welle", "https://www.goethe.de/ins/sk/de/m/kul/sup/deu/ndw.html"),
    ],
    "sport": [
        ref("IOC Olympic Studies Centre: Olympic facts", "https://library.olympics.com/default/digitalCollection/DigitalCollectionAttachmentDownloadHandler.ashx?documentId=619389&parentDocumentId=619388&skipCopyright=true&skipWatermark=true"),
        ref("IFAB: Law 3 – The Players", "https://theifab.com/laws/latest/the-players/"),
        ref("FIBA: Official Basketball Rules", "https://refereeing.fiba.basketball/en/rules"),
        ref("IHF: Rules of the Game", "https://www.ihf.info/regulations-documents/361?selected=Rules%20of%20the%20Game"),
    ],
    "witnesses_of_time": [
        ref("Deutsches Historisches Museum: Lebendiges Museum Online", "https://www.dhm.de/lemo/"),
        ref("Encyclopaedia Britannica: World history", "https://www.britannica.com/topic/history"),
    ],
    "media_entertainment": [
        ref("Academy of Motion Picture Arts and Sciences: Oscars", "https://www.oscars.org/oscars"),
        ref("Encyclopaedia Britannica: history of film", "https://www.britannica.com/art/history-of-the-motion-picture"),
    ],
    "plants_animals": [
        ref("Smithsonian's National Zoo: Animals", "https://nationalzoo.si.edu/animals"),
        ref("Encyclopaedia Britannica: fastest animals", "https://www.britannica.com/list/the-fastest-animals-on-earth"),
        ref("Royal Botanic Gardens, Kew: Plants", "https://www.kew.org/plants"),
    ],
    "human_everyday": [
        ref("NCBI Bookshelf: Anatomy and Physiology", "https://www.ncbi.nlm.nih.gov/books/NBK547855/"),
        ref("USDA: Safe Minimum Internal Temperature Chart", "https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/safe-temperature-chart"),
        ref("NIST: SI Units – Temperature", "https://www.nist.gov/pml/owm/si-units-temperature"),
        ref("CDC: About Sleep", "https://www.cdc.gov/sleep/about/index.html"),
    ],
}


SUBTOPICS = {
    "gaming": ["Geschichte & Meilensteine", "Konsolen & Hardware", "Studios & Entwicklung", "Spielwelten & Figuren", "Spielmechanik & Begriffe"],
    "faith_religion": ["Christentum", "Judentum", "Islam", "Hinduismus", "Buddhismus", "Sikhismus", "Ostasiatische Religionen", "Heilige Schriften", "Feste & Rituale", "Heilige Orte & Religionsgeschichte"],
    "music": ["Rock", "Deutsche Musikgeschichte", "Internationale Musikgeschichte", "Klassische Musik", "Instrumente & Musiktheorie"],
    "sport": ["Sportvergleiche", "Leichtathletik & Ausdauer", "Mannschafts- & Ballsport", "Wasser-, Winter- & Motorsport", "Regeln & Ausrüstung", "Olympische Geschichte & Meilensteine"],
    "witnesses_of_time": ["Antike & Mittelalter", "Entdeckungen & Erfindungen", "Revolutionen & Staaten", "20. Jahrhundert", "Deutsche Geschichte"],
    "media_entertainment": ["Filmgeschichte", "Serien", "Literatur", "Bildende Kunst", "Mediengeschichte"],
    "plants_animals": ["Säugetiere", "Vögel", "Meeresleben", "Pflanzen", "Ökologie & Lebensräume"],
    "human_everyday": ["Anatomie", "Ernährung & Küche", "Zeit & Kalender", "Gesundheit & Schlaf", "Alltagsphysik"],
}


# label, relation, predicate, year/value, estimate prompt, estimate value, unit
DATA: dict[str, list[tuple[str, str, str, int, str, int | float, str]]] = {
    "gaming": [
        ("Ridge Racer", "Rennspiel", "ist ein Arcade-Rennspiel", 1994, "In welchem Jahr erschien Ridge Racer für die erste PlayStation?", 1994, "Jahr"),
        ("Tekken", "Kampfspiel", "setzt auf dreidimensionale Kämpfe", 1994, "In welchem Jahr erschien Tekken für die erste PlayStation?", 1994, "Jahr"),
        ("WipEout", "Antigravitations-Rennspiel", "verbindet futuristische Rennen mit Waffen", 1995, "In welchem Jahr erschien WipEout für die erste PlayStation?", 1995, "Jahr"),
        ("Tomb Raider", "Action-Adventure", "machte Lara Croft zur Hauptfigur", 1996, "In welchem Jahr erschien Tomb Raider für die erste PlayStation?", 1996, "Jahr"),
        ("PaRappa the Rapper", "Rhythmusspiel", "verlangt Eingaben passend zum Rhythmus", 1996, "In welchem Jahr erschien PaRappa the Rapper?", 1996, "Jahr"),
        ("Resident Evil", "Survival Horror", "verbindet Rätsel mit bedrohlichen Kreaturen", 1996, "In welchem Jahr erschien das erste Resident Evil für PlayStation?", 1996, "Jahr"),
        ("Crash Bandicoot", "Jump ’n’ Run", "hat Crash als springende und wirbelnde Hauptfigur", 1996, "In welchem Jahr erschien das erste Crash Bandicoot?", 1996, "Jahr"),
        ("Final Fantasy VII", "Rollenspiel", "führte Cloud und Sephiroth in die Reihe ein", 1997, "In welchem Jahr erschien Final Fantasy VII für PlayStation?", 1997, "Jahr"),
        ("Gran Turismo", "Rennsimulation", "warb mit besonders realistischer Fahrzeugdarstellung", 1997, "In welchem Jahr erschien das erste Gran Turismo?", 1997, "Jahr"),
        ("Metal Gear Solid", "Stealth-Action", "stellt heimliches Infiltrieren mit Solid Snake in den Mittelpunkt", 1998, "In welchem Jahr erschien Metal Gear Solid für PlayStation?", 1998, "Jahr"),
        ("Ape Escape", "Action-Plattformer", "benötigte als erstes PlayStation-Spiel zwingend den DualShock", 1999, "In welchem Jahr erschien Ape Escape?", 1999, "Jahr"),
        ("Jak and Daxter", "Action-Plattformer", "schickt Jak mit seinem Begleiter Daxter auf eine Reise", 2001, "In welchem Jahr erschien Jak and Daxter?", 2001, "Jahr"),
        ("Ico", "Action-Adventure", "verbindet behutsame Rätsel mit der Flucht vor Schatten", 2001, "In welchem Jahr erschien Ico?", 2001, "Jahr"),
        ("Ratchet & Clank", "3D-Plattformer", "stellt den Lombax Ratchet und den Roboter Clank ins Zentrum", 2002, "In welchem Jahr erschien das erste Ratchet & Clank?", 2002, "Jahr"),
        ("Sly Cooper", "Stealth-Plattformer", "hat einen diebischen Waschbären als Hauptfigur", 2002, "In welchem Jahr erschien das erste Sly Cooper?", 2002, "Jahr"),
        ("Killzone", "Ego-Shooter", "erzählt vom Kampf gegen die Helghast", 2004, "In welchem Jahr erschien das erste Killzone?", 2004, "Jahr"),
        ("God of War", "Action-Adventure", "führte Kratos als Hauptfigur ein", 2005, "In welchem Jahr erschien das erste God of War?", 2005, "Jahr"),
        ("Shadow of the Colossus", "Action-Adventure", "stellt Kämpfe gegen 16 Kolosse in den Mittelpunkt", 2005, "In welchem Jahr erschien Shadow of the Colossus?", 2005, "Jahr"),
        ("LocoRoco", "Puzzle-Plattformer", "lässt die Spielwelt statt der Figuren direkt kippen", 2006, "In welchem Jahr erschien LocoRoco?", 2006, "Jahr"),
        ("Patapon", "Rhythmus-Strategiespiel", "steuert eine Armee durch rhythmische Trommelfolgen", 2007, "In welchem Jahr erschien Patapon?", 2007, "Jahr"),
    ],
    "music": [
        ("Die vier Jahreszeiten", "Antonio Vivaldi", "besteht aus vier Violinkonzerten", 1725, "In welchem Jahr wurden Vivaldis Vier Jahreszeiten veröffentlicht?", 1725, "Jahr"),
        ("Brandenburgische Konzerte", "Johann Sebastian Bach", "sind eine Sammlung von sechs Konzerten", 1721, "In welchem Jahr widmete Bach die Brandenburgischen Konzerte dem Markgrafen?", 1721, "Jahr"),
        ("Messiah", "Georg Friedrich Händel", "ist ein englischsprachiges Oratorium", 1742, "In welchem Jahr wurde Händels Messiah uraufgeführt?", 1742, "Jahr"),
        ("Eine kleine Nachtmusik", "Wolfgang Amadeus Mozart", "ist eine Serenade für Streicher", 1787, "In welchem Jahr komponierte Mozart Eine kleine Nachtmusik?", 1787, "Jahr"),
        ("5. Sinfonie", "Ludwig van Beethoven", "beginnt mit einem berühmten Viertonmotiv", 1808, "In welchem Jahr wurde Beethovens 5. Sinfonie uraufgeführt?", 1808, "Jahr"),
        ("An der schönen blauen Donau", "Johann Strauss Sohn", "ist ein Konzertwalzer", 1867, "In welchem Jahr wurde An der schönen blauen Donau uraufgeführt?", 1867, "Jahr"),
        ("Carmen", "Georges Bizet", "ist eine Oper, die in Sevilla spielt", 1875, "In welchem Jahr wurde Bizets Carmen uraufgeführt?", 1875, "Jahr"),
        ("Die Planeten", "Gustav Holst", "ist eine siebensätzige Orchestersuite", 1920, "In welchem Jahr wurde Holsts vollständige Suite Die Planeten erstmals öffentlich aufgeführt?", 1920, "Jahr"),
        ("Rhapsody in Blue", "George Gershwin", "verbindet Konzertmusik mit Jazzelementen", 1924, "In welchem Jahr wurde Rhapsody in Blue uraufgeführt?", 1924, "Jahr"),
        ("Rock Around the Clock", "Bill Haley & His Comets", "gehört zum frühen Rock ’n’ Roll", 1954, "In welchem Jahr wurde Rock Around the Clock aufgenommen?", 1954, "Jahr"),
        ("Johnny B. Goode", "Chuck Berry", "erzählt von einem gitarrenspielenden Jungen", 1958, "In welchem Jahr erschien Johnny B. Goode?", 1958, "Jahr"),
        ("Respect", "Aretha Franklin", "wurde zu einem Soul-Klassiker", 1967, "In welchem Jahr erschien Aretha Franklins Version von Respect?", 1967, "Jahr"),
        ("Bohemian Rhapsody", "Queen", "verbindet Rock mit opernhaften Abschnitten", 1975, "In welchem Jahr erschien Bohemian Rhapsody?", 1975, "Jahr"),
        ("Trans Europa Express", "Kraftwerk", "ist ein Werk elektronischer Musik", 1977, "In welchem Jahr erschien Kraftwerks Album Trans Europa Express?", 1977, "Jahr"),
        ("Rapper’s Delight", "The Sugarhill Gang", "gehört zu den frühen international erfolgreichen Hip-Hop-Singles", 1979, "In welchem Jahr erschien Rapper’s Delight?", 1979, "Jahr"),
        ("99 Luftballons", "Nena", "wird der Neuen Deutschen Welle zugeordnet", 1983, "In welchem Jahr erschien 99 Luftballons?", 1983, "Jahr"),
        ("Smells Like Teen Spirit", "Nirvana", "gilt als prägender Grunge-Song", 1991, "In welchem Jahr erschien Smells Like Teen Spirit?", 1991, "Jahr"),
        ("Wonderwall", "Oasis", "erschien auf dem Album (What’s the Story) Morning Glory?", 1995, "In welchem Jahr erschien Wonderwall?", 1995, "Jahr"),
        ("Crazy in Love", "Beyoncé", "verbindet R&B und Pop mit einem markanten Bläsersample", 2003, "In welchem Jahr erschien Crazy in Love?", 2003, "Jahr"),
        ("Rolling in the Deep", "Adele", "verbindet Pop, Soul und Blues-Einflüsse", 2010, "In welchem Jahr erschien Rolling in the Deep?", 2010, "Jahr"),
    ],
    "faith_religion": [
        ("Tora", "Judentum", "bezeichnet die fünf Bücher Mose", -500, "Wie viele Bücher umfasst die Tora?", 5, "Bücher"),
        ("Tanach", "Judentum", "ist die hebräische Bibel", -300, "Wie viele Bücher zählt der Tanach in der jüdischen Zählung?", 24, "Bücher"),
        ("Zehn Gebote", "Judentum und Christentum", "formulieren grundlegende religiöse Gebote", -1200, "Wie viele Gebote nennt die traditionelle Bezeichnung Zehn Gebote?", 10, "Gebote"),
        ("Neues Testament", "Christentum", "bildet den jüngeren Hauptteil der christlichen Bibel", 100, "Wie viele Bücher umfasst das Neue Testament in der verbreiteten Zählung?", 27, "Bücher"),
        ("Evangelien", "Christentum", "erzählen im Neuen Testament vom Wirken Jesu", 80, "Wie viele kanonische Evangelien enthält das Neue Testament?", 4, "Evangelien"),
        ("Koran", "Islam", "ist in Suren gegliedert", 650, "Wie viele Suren umfasst der Koran?", 114, "Suren"),
        ("Fünf Säulen", "Islam", "fassen grundlegende religiöse Pflichten zusammen", 630, "Wie viele Säulen nennt die Bezeichnung Fünf Säulen des Islam?", 5, "Säulen"),
        ("islamischer Kalender", "Islam", "besteht aus zwölf Mondmonaten", 630, "Wie viele Monate umfasst der islamische Kalender?", 12, "Monate"),
        ("Veden", "Hinduismus", "gehören zu den ältesten heiligen Schriften Indiens", -1000, "Wie viele Veden werden traditionell unterschieden?", 4, "Veden"),
        ("Trimurti", "Hinduismus", "verbindet Brahma, Vishnu und Shiva in einer Dreiheit", 500, "Wie viele Gottheiten umfasst die hinduistische Trimurti?", 3, "Gottheiten"),
        ("Vier Edle Wahrheiten", "Buddhismus", "beschreiben Leiden, seine Ursache, sein Ende und den Weg dorthin", -500, "Wie viele Edle Wahrheiten lehrt der Buddhismus?", 4, "Wahrheiten"),
        ("Edler Achtfacher Pfad", "Buddhismus", "beschreibt acht Bereiche buddhistischer Übung", -500, "Wie viele Glieder hat der Edle Achtfache Pfad?", 8, "Glieder"),
        ("Tipitaka", "Buddhismus", "bedeutet wörtlich Drei Körbe", -100, "Aus wie vielen Körben besteht das Tipitaka dem Namen nach?", 3, "Körbe"),
        ("Sikh-Gurus", "Sikhismus", "bilden eine Folge von Guru Nanak bis Guru Gobind Singh", 1708, "Wie viele menschliche Gurus kennt die Sikh-Tradition?", 10, "Gurus"),
        ("Fünf K", "Sikhismus", "bezeichnen fünf sichtbare Glaubenszeichen", 1699, "Wie viele Glaubenszeichen gehören zu den Fünf K?", 5, "Glaubenszeichen"),
        ("Jom Kippur", "Judentum", "ist der Versöhnungstag", -500, "Wie viele Tage liegen zwischen Rosch ha-Schana und Jom Kippur einschließlich der beiden Festtage traditionell?", 10, "Tage"),
        ("Chanukka", "Judentum", "wird als achttägiges Lichterfest begangen", -164, "Wie viele Abende beziehungsweise Tage dauert Chanukka?", 8, "Tage"),
        ("Jainistische Tirthankaras", "Jainismus", "sind verehrte Wegbereiter der Lehre", -500, "Wie viele Tirthankaras kennt die jainistische Tradition?", 24, "Tirthankaras"),
        ("Bahá’í-Kalender", "Bahá’í-Religion", "gliedert das Jahr in Monate zu jeweils 19 Tagen", 1844, "Wie viele Monate besitzt der Bahá’í-Kalender?", 19, "Monate"),
        ("Shinto", "japanische Religion", "verehrt Kami und besitzt keinen einzelnen Gründer", 712, "In welchem Jahrhundert wurde das Kojiki niedergeschrieben?", 8, "Jahrhundert"),
    ],
    "sport": [
        ("Fußball", "IFAB", "wird mit höchstens elf Spielern je Mannschaft auf dem Feld gespielt", 1900, "Wie viele Spieler darf eine Fußballmannschaft höchstens gleichzeitig auf dem Feld haben?", 11, "Spieler"),
        ("Basketball", "FIBA", "wird mit fünf Spielern je Mannschaft auf dem Feld gespielt", 1936, "Wie viele Spieler einer Basketballmannschaft stehen gleichzeitig auf dem Feld?", 5, "Spieler"),
        ("Handball", "IHF", "wird mit sieben Spielern je Mannschaft auf dem Feld gespielt", 1936, "Wie viele Spieler einer Handballmannschaft stehen gleichzeitig auf dem Feld?", 7, "Spieler"),
        ("Volleyball", "FIVB", "wird mit sechs Spielern je Mannschaft auf dem Feld gespielt", 1964, "Wie viele Spieler einer Volleyballmannschaft stehen gleichzeitig auf dem Feld?", 6, "Spieler"),
        ("Rugby Union", "World Rugby", "wird mit 15 Spielern je Mannschaft begonnen", 1900, "Wie viele Spieler umfasst eine Rugby-Union-Mannschaft auf dem Feld?", 15, "Spieler"),
        ("Eishockey", "IIHF", "hat regulär sechs Spieler einschließlich Torhüter je Team auf dem Eis", 1920, "Wie viele Spieler eines Eishockeyteams stehen regulär einschließlich Torhüter auf dem Eis?", 6, "Spieler"),
        ("Baseball", "WBSC", "setzt neun Feldspieler je Mannschaft ein", 1912, "Wie viele Spieler einer Baseballmannschaft stehen gleichzeitig in der Verteidigung?", 9, "Spieler"),
        ("Wasserball", "World Aquatics", "wird mit sieben Spielern einschließlich Torhüter je Team gespielt", 1900, "Wie viele Spieler eines Wasserballteams befinden sich einschließlich Torhüter im Wasser?", 7, "Spieler"),
        ("Feldhockey", "FIH", "wird mit elf Spielern je Mannschaft gespielt", 1908, "Wie viele Spieler umfasst eine Feldhockeymannschaft auf dem Feld?", 11, "Spieler"),
        ("Cricket", "ICC", "wird von Mannschaften mit jeweils elf Spielern gespielt", 1900, "Wie viele Spieler umfasst eine Cricketmannschaft?", 11, "Spieler"),
        ("Futsal", "FIFA", "wird mit fünf Spielern einschließlich Torhüter je Mannschaft gespielt", 2018, "Wie viele Spieler eines Futsalteams stehen einschließlich Torhüter auf dem Feld?", 5, "Spieler"),
        ("Beachvolleyball", "FIVB", "wird mit zwei Spielern je Team gespielt", 1996, "Wie viele Spieler umfasst ein Beachvolleyballteam?", 2, "Spieler"),
        ("Curling", "World Curling", "wird regulär mit vier Spielern je Mannschaft gespielt", 1924, "Wie viele Spieler umfasst ein Curlingteam regulär?", 4, "Spieler"),
        ("Tischtennis", "ITTF", "spielt einen Satz normalerweise bis elf Punkte", 1988, "Bis zu wie vielen Punkten wird ein Tischtennissatz normalerweise gespielt?", 11, "Punkte"),
        ("Badminton", "BWF", "spielt einen Satz normalerweise bis 21 Punkte", 1992, "Bis zu wie vielen Punkten wird ein Badmintonsatz normalerweise gespielt?", 21, "Punkte"),
        ("Tennis", "ITF", "kennt vier Grand-Slam-Turniere pro Jahr", 1896, "Wie viele Grand-Slam-Turniere gibt es im Tennis pro Jahr?", 4, "Turniere"),
        ("400-Meter-Hürdenlauf", "World Athletics", "enthält zehn Hürden pro Bahn", 1900, "Wie viele Hürden stehen beim 400-Meter-Hürdenlauf pro Bahn?", 10, "Hürden"),
        ("Olympisches Schwimmen", "World Aquatics", "findet im 50-Meter-Becken statt", 1896, "Wie lang ist ein olympisches Schwimmbecken?", 50, "Meter"),
        ("Marathon", "World Athletics", "hat eine Distanz von 42,195 Kilometern", 1896, "Wie lang ist ein Marathon?", 42.195, "Kilometer"),
        ("Zehnkampf", "World Athletics", "umfasst zehn leichtathletische Disziplinen", 1912, "Wie viele Disziplinen umfasst ein Zehnkampf?", 10, "Disziplinen"),
    ],
    "witnesses_of_time": [
        ("Ende des Weströmischen Reiches", "Rom", "wird häufig mit der Absetzung des Romulus Augustulus verbunden", 476, "In welchem Jahr endete das Weströmische Reich traditionell?", 476, "Jahr"),
        ("Magna Carta", "England", "begrenzte 1215 die königliche Macht durch schriftlich festgehaltene Rechte", 1215, "In welchem Jahr wurde die Magna Carta besiegelt?", 1215, "Jahr"),
        ("Buchdruck mit beweglichen Metalllettern", "Mainz", "ist in Europa besonders mit Johannes Gutenberg verbunden", 1450, "Um welches Jahr entwickelte Gutenberg seinen Buchdruck in Mainz?", 1450, "Jahr"),
        ("Erste Atlantikfahrt des Kolumbus", "Spanien", "erreichte 1492 Inseln der Karibik", 1492, "In welchem Jahr erreichte Kolumbus auf seiner ersten Reise die Karibik?", 1492, "Jahr"),
        ("Luthers 95 Thesen", "Wittenberg", "wurden 1517 zum Symbol der Reformation", 1517, "In welchem Jahr veröffentlichte Luther seine 95 Thesen?", 1517, "Jahr"),
        ("Westfälischer Friede", "Münster und Osnabrück", "beendete 1648 den Dreißigjährigen Krieg", 1648, "In welchem Jahr wurde der Westfälische Friede geschlossen?", 1648, "Jahr"),
        ("Unabhängigkeitserklärung der USA", "Philadelphia", "wurde am 4. Juli 1776 angenommen", 1776, "In welchem Jahr wurde die US-Unabhängigkeitserklärung angenommen?", 1776, "Jahr"),
        ("Französische Revolution", "Frankreich", "begann 1789 mit einer tiefgreifenden politischen Umwälzung", 1789, "In welchem Jahr begann die Französische Revolution?", 1789, "Jahr"),
        ("Wiener Kongress", "Wien", "ordnete Europa nach den Napoleonischen Kriegen neu", 1815, "In welchem Jahr endete der Wiener Kongress?", 1815, "Jahr"),
        ("Gründung des Deutschen Kaiserreichs", "Versailles", "erfolgte 1871 während des Deutsch-Französischen Krieges", 1871, "In welchem Jahr wurde das Deutsche Kaiserreich gegründet?", 1871, "Jahr"),
        ("Beginn des Ersten Weltkriegs", "Europa", "folgte 1914 auf die Julikrise", 1914, "In welchem Jahr begann der Erste Weltkrieg?", 1914, "Jahr"),
        ("Frauenwahlrecht in Deutschland", "Deutschland", "wurde 1918 gesetzlich eingeführt", 1918, "In welchem Jahr wurde das Frauenwahlrecht in Deutschland eingeführt?", 1918, "Jahr"),
        ("Gründung der Vereinten Nationen", "San Francisco", "trat 1945 mit der UN-Charta in Kraft", 1945, "In welchem Jahr wurden die Vereinten Nationen gegründet?", 1945, "Jahr"),
        ("Bau der Berliner Mauer", "Berlin", "begann am 13. August 1961", 1961, "In welchem Jahr wurde die Berliner Mauer gebaut?", 1961, "Jahr"),
        ("Erste bemannte Mondlandung", "Mond", "gelang Apollo 11 im Jahr 1969", 1969, "In welchem Jahr landeten erstmals Menschen auf dem Mond?", 1969, "Jahr"),
        ("Fall der Berliner Mauer", "Berlin", "ereignete sich am 9. November 1989", 1989, "In welchem Jahr fiel die Berliner Mauer?", 1989, "Jahr"),
        ("Deutsche Wiedervereinigung", "Deutschland", "trat am 3. Oktober 1990 in Kraft", 1990, "In welchem Jahr wurde Deutschland wiedervereinigt?", 1990, "Jahr"),
        ("Vertrag von Maastricht", "Niederlande", "begründete die Europäische Union", 1992, "In welchem Jahr wurde der Vertrag von Maastricht unterzeichnet?", 1992, "Jahr"),
        ("Einführung des Euro-Bargelds", "Europäische Union", "erfolgte 2002 in zwölf Staaten", 2002, "In welchem Jahr wurde Euro-Bargeld eingeführt?", 2002, "Jahr"),
        ("Eröffnung des World Wide Web", "CERN", "machte 1991 die erste Website öffentlich zugänglich", 1991, "In welchem Jahr ging die erste Website am CERN online?", 1991, "Jahr"),
    ],
    "media_entertainment": [
        ("Schneewittchen und die sieben Zwerge", "Walt Disney", "war Disneys erster abendfüllender Zeichentrickfilm", 1937, "In welchem Jahr kam Disneys Schneewittchen in die Kinos?", 1937, "Jahr"),
        ("Citizen Kane", "Orson Welles", "erzählt über Rückblenden vom Leben Charles Foster Kanes", 1941, "In welchem Jahr erschien Citizen Kane?", 1941, "Jahr"),
        ("Casablanca", "Michael Curtiz", "spielt während des Zweiten Weltkriegs in Marokko", 1942, "In welchem Jahr erschien Casablanca?", 1942, "Jahr"),
        ("Die sieben Samurai", "Akira Kurosawa", "erzählt von Samurai, die ein Dorf verteidigen", 1954, "In welchem Jahr erschien Die sieben Samurai?", 1954, "Jahr"),
        ("Psycho", "Alfred Hitchcock", "ist besonders für die Duschszene bekannt", 1960, "In welchem Jahr erschien Psycho?", 1960, "Jahr"),
        ("2001: Odyssee im Weltraum", "Stanley Kubrick", "enthält den Bordcomputer HAL 9000", 1968, "In welchem Jahr erschien 2001: Odyssee im Weltraum?", 1968, "Jahr"),
        ("Der weiße Hai", "Steven Spielberg", "spielt in der fiktiven Küstenstadt Amity", 1975, "In welchem Jahr erschien Der weiße Hai?", 1975, "Jahr"),
        ("Star Wars", "George Lucas", "führte Luke Skywalker und Darth Vader ins Kino ein", 1977, "In welchem Jahr erschien der erste Star-Wars-Film?", 1977, "Jahr"),
        ("E.T.", "Steven Spielberg", "erzählt von der Freundschaft eines Jungen mit einem Außerirdischen", 1982, "In welchem Jahr erschien E.T.?", 1982, "Jahr"),
        ("Jurassic Park", "Steven Spielberg", "zeigt einen Freizeitpark mit geklonten Dinosauriern", 1993, "In welchem Jahr erschien Jurassic Park?", 1993, "Jahr"),
        ("Toy Story", "John Lasseter", "war der erste vollständig computeranimierte Langfilm", 1995, "In welchem Jahr erschien Toy Story?", 1995, "Jahr"),
        ("Matrix", "Lana und Lilly Wachowski", "stellt eine simulierte Wirklichkeit ins Zentrum", 1999, "In welchem Jahr erschien Matrix?", 1999, "Jahr"),
        ("Chihiros Reise ins Zauberland", "Hayao Miyazaki", "erzählt von Chihiro in einer Welt der Geister", 2001, "In welchem Jahr erschien Chihiros Reise ins Zauberland in Japan?", 2001, "Jahr"),
        ("Der Herr der Ringe: Die Gefährten", "Peter Jackson", "ist der erste Teil von Jacksons Filmtrilogie", 2001, "In welchem Jahr erschien Die Gefährten im Kino?", 2001, "Jahr"),
        ("Avatar", "James Cameron", "spielt größtenteils auf dem Mond Pandora", 2009, "In welchem Jahr erschien Avatar?", 2009, "Jahr"),
    ],
    "plants_animals": [
        ("Wanderfalke", "Vogel", "erreicht seine Höchstgeschwindigkeit im Sturzflug", 320, "Welche Spitzengeschwindigkeit erreicht ein Wanderfalke im Sturzflug ungefähr?", 320, "km/h"),
        ("Gepard", "Säugetier", "ist auf kurze Sprints an Land spezialisiert", 100, "Welche Spitzengeschwindigkeit erreicht ein Gepard ungefähr?", 100, "km/h"),
        ("Gabelbock", "Säugetier", "kann hohe Geschwindigkeit länger halten als ein Gepard", 88, "Welche Spitzengeschwindigkeit erreicht ein Gabelbock ungefähr?", 88, "km/h"),
        ("Strauß", "Vogel", "ist der schnellste laufende Vogel", 70, "Welche Laufgeschwindigkeit erreicht ein Strauß ungefähr?", 70, "km/h"),
        ("Löwe", "Säugetier", "beschleunigt schnell, hält das Tempo aber nur kurz", 80, "Welche Spitzengeschwindigkeit erreicht ein Löwe ungefähr?", 80, "km/h"),
        ("Gnu", "Säugetier", "lebt als Pflanzenfresser in afrikanischen Herden", 80, "Welche Spitzengeschwindigkeit erreicht ein Gnu ungefähr?", 80, "km/h"),
        ("Springbock", "Säugetier", "ist für hohe Sprünge und schnelle Flucht bekannt", 88, "Welche Spitzengeschwindigkeit erreicht ein Springbock ungefähr?", 88, "km/h"),
        ("Windhund", "Haushund", "wurde für schnelle Sichtjagden gezüchtet", 72, "Welche Spitzengeschwindigkeit erreicht ein Windhund ungefähr?", 72, "km/h"),
        ("Pferd", "Säugetier", "kann im Galopp etwa 70 km/h erreichen", 70, "Welche Spitzengeschwindigkeit erreicht ein Pferd ungefähr?", 70, "km/h"),
        ("Afrikanischer Elefant", "Säugetier", "ist das größte heute lebende Landtier", 40, "Welche Laufgeschwindigkeit erreicht ein Afrikanischer Elefant ungefähr?", 40, "km/h"),
        ("Flusspferd", "Säugetier", "kann an Land überraschend schnell laufen", 30, "Welche Laufgeschwindigkeit erreicht ein Flusspferd ungefähr?", 30, "km/h"),
        ("Eisbär", "Säugetier", "ist an das Leben in der Arktis angepasst", 40, "Welche Laufgeschwindigkeit erreicht ein Eisbär ungefähr?", 40, "km/h"),
        ("Leistenkrokodil", "Reptil", "ist das größte heute lebende Krokodil", 24, "Welche Laufgeschwindigkeit erreicht ein großes Krokodil an Land ungefähr?", 24, "km/h"),
        ("Riesenschildkröte", "Reptil", "bewegt sich an Land meist sehr langsam", 0.3, "Welche Geschwindigkeit erreicht eine Riesenschildkröte ungefähr?", 0.3, "km/h"),
        ("Faultier", "Säugetier", "bewegt sich energiesparend durch Baumkronen", 0.27, "Welche Geschwindigkeit erreicht ein Faultier am Boden ungefähr?", 0.27, "km/h"),
        ("Blauwal", "Säugetier", "ist das größte bekannte Tier der Erdgeschichte", 48, "Welche Schwimmgeschwindigkeit kann ein Blauwal ungefähr erreichen?", 48, "km/h"),
        ("Schwertfisch", "Knochenfisch", "besitzt einen langen, schwertartigen Oberkiefer", 97, "Welche Schwimmgeschwindigkeit wird für einen Schwertfisch ungefähr angegeben?", 97, "km/h"),
        ("Makohai", "Knorpelfisch", "gehört zu den schnellsten Haien", 74, "Welche Schwimmgeschwindigkeit erreicht ein Makohai ungefähr?", 74, "km/h"),
        ("Libelle", "Insekt", "jagt andere Insekten im Flug", 55, "Welche Fluggeschwindigkeit kann eine große Libelle ungefähr erreichen?", 55, "km/h"),
        ("Honigbiene", "Insekt", "sammelt Nektar und bestäubt Blüten", 24, "Welche Fluggeschwindigkeit erreicht eine Honigbiene ungefähr?", 24, "km/h"),
    ],
    "human_everyday": [
        ("Knochen im erwachsenen Skelett", "Anatomie", "werden üblicherweise mit 206 angegeben", 206, "Wie viele Knochen besitzt ein erwachsener Mensch gewöhnlich?", 206, "Knochen"),
        ("bleibende Zähne", "Anatomie", "umfassen mit Weisheitszähnen normalerweise 32 Zähne", 32, "Wie viele bleibende Zähne besitzt ein vollständiges Erwachsenengebiss einschließlich Weisheitszähnen?", 32, "Zähne"),
        ("Herzkammern", "Anatomie", "bestehen aus zwei Vorhöfen und zwei Hauptkammern", 4, "Wie viele Kammern besitzt das menschliche Herz?", 4, "Kammern"),
        ("Rippenpaare", "Anatomie", "schützen gemeinsam mit Brustbein und Wirbelsäule den Brustkorb", 12, "Wie viele Rippenpaare besitzt ein Mensch normalerweise?", 12, "Rippenpaare"),
        ("Halswirbel", "Anatomie", "bilden den obersten Abschnitt der Wirbelsäule", 7, "Wie viele Halswirbel besitzt der Mensch?", 7, "Wirbel"),
        ("Lungenlappen", "Anatomie", "verteilen sich auf drei rechts und zwei links", 5, "Wie viele Lungenlappen besitzt der Mensch insgesamt?", 5, "Lappen"),
        ("Hirnnervenpaare", "Anatomie", "verbinden vor allem Kopf und Hals direkt mit dem Gehirn", 12, "Wie viele Hirnnervenpaare werden unterschieden?", 12, "Paare"),
        ("Körpertemperatur", "Gesundheit", "liegt als grober Normalwert nahe 37 Grad Celsius", 37, "Bei wie viel Grad Celsius liegt die normale Körpertemperatur ungefähr?", 37, "°C"),
        ("Blutmenge eines Erwachsenen", "Anatomie", "liegt im Mittel ungefähr bei fünf Litern", 5, "Wie viele Liter Blut besitzt ein erwachsener Mensch ungefähr?", 5, "Liter"),
        ("Schwangerschaft", "Gesundheit", "dauert ab dem ersten Tag der letzten Periode ungefähr 40 Wochen", 40, "Wie viele Wochen dauert eine Schwangerschaft rechnerisch ungefähr?", 40, "Wochen"),
        ("Lebensdauer roter Blutkörperchen", "Anatomie", "beträgt ungefähr 120 Tage", 120, "Wie viele Tage lebt ein rotes Blutkörperchen ungefähr?", 120, "Tage"),
        ("empfohlene Schlafdauer für Erwachsene", "Gesundheit & Schlaf", "liegt für viele Erwachsene bei mindestens sieben Stunden", 7, "Wie viele Stunden Schlaf pro Nacht empfiehlt die CDC Erwachsenen mindestens?", 7, "Stunden"),
        ("Gefrierpunkt von Wasser", "Alltagsphysik", "liegt bei Normaldruck bei null Grad Celsius", 0, "Bei wie viel Grad Celsius gefriert reines Wasser bei Normaldruck?", 0, "°C"),
        ("Siedepunkt von Wasser", "Alltagsphysik", "liegt auf Meereshöhe ungefähr bei 100 Grad Celsius", 100, "Bei wie viel Grad Celsius siedet Wasser auf Meereshöhe ungefähr?", 100, "°C"),
        ("Kühlschranktemperatur", "Ernährung & Küche", "sollte höchstens etwa vier Grad Celsius betragen", 4, "Wie viel Grad Celsius sollte ein Kühlschrank laut USDA höchstens haben?", 4, "°C"),
        ("Gefrierschranktemperatur", "Ernährung & Küche", "sollte bei ungefähr minus 18 Grad Celsius liegen", -18, "Wie viele Grad unter null sollte ein Gefrierschrank ungefähr erreichen?", 18, "Grad unter 0 °C"),
        ("sichere Kerntemperatur für Geflügel", "Ernährung & Küche", "liegt laut USDA bei etwa 74 Grad Celsius", 74, "Welche Kerntemperatur sollte Geflügel mindestens erreichen?", 74, "°C"),
        ("sichere Kerntemperatur für Hackfleisch", "Ernährung & Küche", "liegt laut USDA bei etwa 71 Grad Celsius", 71, "Welche Kerntemperatur sollte Hackfleisch mindestens erreichen?", 71, "°C"),
        ("Ruhezeit ganzer Fleischstücke", "Ernährung & Küche", "beträgt nach Erreichen der Mindesttemperatur mindestens drei Minuten", 3, "Wie viele Minuten Ruhezeit empfiehlt das USDA für ganze Fleischstücke nach dem Garen mindestens?", 3, "Minuten"),
        ("Minuten eines Tages", "Zeit & Kalender", "ergeben sich aus 24 Stunden zu jeweils 60 Minuten", 1440, "Wie viele Minuten hat ein Tag?", 1440, "Minuten"),
        ("Sekunden einer Stunde", "Zeit & Kalender", "ergeben sich aus 60 Minuten zu jeweils 60 Sekunden", 3600, "Wie viele Sekunden hat eine Stunde?", 3600, "Sekunden"),
        ("Tage eines Schaltjahres", "Zeit & Kalender", "umfassen einen zusätzlichen 29. Februar", 366, "Wie viele Tage hat ein Schaltjahr?", 366, "Tage"),
        ("Monate eines Jahres", "Zeit & Kalender", "gliedern das Kalenderjahr in zwölf Abschnitte", 12, "Wie viele Monate hat ein Kalenderjahr?", 12, "Monate"),
        ("Stunden einer Woche", "Zeit & Kalender", "ergeben sich aus sieben Tagen zu je 24 Stunden", 168, "Wie viele Stunden hat eine Woche?", 168, "Stunden"),
    ],
}


ORDER_DATA = {
    "faith_religion": [
        ("Konzil von Nicäa", 325),
        ("Hidschra Mohammeds nach Medina", 622),
        ("Niederschrift des Kojiki", 712),
        ("Großes Schisma zwischen Ost- und Westkirche", 1054),
        ("Druck der Gutenberg-Bibel", 1455),
        ("Geburt Guru Nanaks", 1469),
        ("Beginn der Reformation", 1517),
        ("Einsetzung des Adi Granth im Goldenen Tempel", 1604),
        ("Gründung der Khalsa", 1699),
        ("Erklärung des Báb", 1844),
        ("Erstes Vatikanisches Konzil", 1869),
        ("erstes Weltparlament der Religionen", 1893),
        ("Beginn des Zweiten Vatikanischen Konzils", 1962),
    ],
    "human_everyday": [
        ("Gefrierschrank", -18),
        ("Gefrierpunkt von Wasser", 0),
        ("Kühlschrank", 4),
        ("kühler Wohnraum", 18),
        ("typische Raumtemperatur", 20),
        ("menschliche Körpertemperatur", 37),
        ("Mindest-Kerntemperatur ganzer Fleischstücke", 63),
        ("Mindest-Kerntemperatur von Hackfleisch", 71),
        ("Mindest-Kerntemperatur von Geflügel", 74),
        ("Siedepunkt von Wasser auf Meereshöhe", 100),
    ],
}


MC_TEMPLATES = {
    "gaming": "Welche Spielart passt am besten zu „{label}“?",
    "faith_religion": "Zu welcher Religion oder Tradition gehört „{label}“?",
    "music": "Wer schuf beziehungsweise veröffentlichte „{label}“?",
    "sport": "Welcher internationale Verband ist für „{label}“ maßgeblich?",
    "witnesses_of_time": "Mit welchem Ort oder Staat ist „{label}“ besonders verbunden?",
    "plants_animals": "Welcher Tiergruppe gehört „{label}“ an?",
}

MATCH_TEMPLATES = {
    "gaming": "Ordne das Spiel seiner Spielart zu.",
    "faith_religion": "Ordne den Begriff der zugehörigen Religion oder Tradition zu.",
    "music": "Ordne das Werk dem richtigen Act oder Komponisten zu.",
    "sport": "Ordne die Sportart ihrem internationalen Regelverband zu.",
    "witnesses_of_time": "Ordne das historische Ereignis dem passenden Ort oder Staat zu.",
    "plants_animals": "Ordne das Tier seiner Gruppe zu.",
    "human_everyday": "Ordne die Alltagsgröße ihrem Referenzwert zu.",
}

ORDER_TEMPLATES = {
    "gaming": "Ordne diese Spiele nach ihrem Erscheinen, vom frühesten zum spätesten.",
    "faith_religion": "Ordne diese religionsgeschichtlichen Ereignisse chronologisch.",
    "music": "Ordne diese Werke nach Veröffentlichung oder Uraufführung.",
    "sport": "Ordne diese Sportarten nach ihrem ersten Auftreten bei Olympischen Spielen.",
    "media_entertainment": "Ordne diese Filme nach ihrem Kinostart.",
    "plants_animals": "Ordne diese Tiere nach ungefährer Höchstgeschwindigkeit, vom langsamsten zum schnellsten.",
    "human_everyday": "Ordne diese Temperaturwerte von niedrig nach hoch.",
}

FALSE_TEMPLATES = {
    "gaming": "„{label}“ ist ein Spiel aus dem Bereich „{wrong}“.",
    "faith_religion": "Der Begriff „{label}“ gehört zur Religion oder Tradition „{wrong}“.",
    "music": "Das Werk „{label}“ stammt von „{wrong}“.",
    "sport": "Für die Sportart „{label}“ ist „{wrong}“ der maßgebliche internationale Verband.",
    "witnesses_of_time": "Das Ereignis „{label}“ ist besonders mit „{wrong}“ verbunden.",
    "plants_animals": "„{label}“ gehört zur Tiergruppe „{wrong}“.",
    "human_everyday": "Der Eintrag „{label}“ gehört zum Wissensbereich „{wrong}“.",
}


def slug(value: str) -> str:
    value = value.casefold()
    for old, new in {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "&": "und"}.items():
        value = value.replace(old, new)
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")


def file_path(question_type: str, category: str) -> Path:
    return LIBRARY / TYPE_DIRS[question_type] / CATEGORY_DIRS[category] / "fragen.json"


def numeric_id(question: dict[str, Any]) -> int:
    return int(re.search(r"\d+", question["id"]).group())


def format_number(value: int | float) -> str:
    if isinstance(value, float) and not value.is_integer():
        return str(value).replace(".", ",")
    return str(int(value))


def numeric_distractors(value: int | float) -> list[str]:
    if value == 0:
        candidates = [4, 10, 20]
    elif abs(value) < 10:
        candidates = [value + 1, value + 2, value * 2]
    elif abs(value) < 100:
        candidates = [value - 3, value + 3, round(value * 1.25)]
    elif 1400 <= value <= 2100:
        candidates = [value - 10, value + 10, value + 25]
    else:
        candidates = [round(value * 0.75), round(value * 1.25), round(value * 1.5)]
    result = []
    for candidate in candidates:
        rendered = format_number(candidate)
        if rendered != format_number(value) and rendered not in result:
            result.append(rendered)
    bump = 1
    while len(result) < 3:
        rendered = format_number(value + bump)
        if rendered != format_number(value) and rendered not in result:
            result.append(rendered)
        bump += 1
    return result[:3]


class Builder:
    def __init__(self) -> None:
        self.files: dict[tuple[str, str], list[dict[str, Any]]] = {}
        self.next_id: dict[str, int] = {}
        self.added: list[dict[str, Any]] = []
        self.topic_counts: dict[str, Counter[str]] = defaultdict(Counter)

        for question_type in ACTIVE_TYPES:
            highest = 0
            for category in CATEGORY_DIRS:
                path = file_path(question_type, category)
                questions = json.loads(path.read_text(encoding="utf-8"))
                self.files[(question_type, category)] = questions
                for question in questions:
                    highest = max(highest, numeric_id(question))
                    self.topic_counts[category][question["subtopic"]] += 1
            self.next_id[question_type] = highest + 1

    def choose_subtopic(self, category: str) -> str:
        candidates = SUBTOPICS[category]
        topic = min(candidates, key=lambda item: (self.topic_counts[category][item], candidates.index(item)))
        self.topic_counts[category][topic] += 1
        return topic

    def add(self, question_type: str, category: str, prompt: str, answer: Any, explanation: str, **fields: Any) -> None:
        number = self.next_id[question_type]
        self.next_id[question_type] += 1
        subtopic = self.choose_subtopic(category)
        question = {
            "id": f"{PREFIXES[question_type]}{number:03d}",
            "question_type": question_type,
            "primary_category": category,
            "subtopic": subtopic,
            "tags": {"topics": [subtopic], "entities": [], "genres": [], "regions": [], "eras": []},
            "source": {"status": "verified", "verified_on": "2026-10-04", "references": SOURCES[category]},
            "prompt": prompt,
            "answer": answer,
            "explanation": explanation,
            "subject_keys": [f"topic:{category}:{slug(subtopic)}"],
            **fields,
        }
        self.files[(question_type, category)].append(question)
        self.added.append(question)


def distinct_relations(records: list[tuple], start: int, correct: str) -> list[str]:
    values: list[str] = []
    for offset in range(1, len(records) + 1):
        candidate = records[(start + offset) % len(records)][1]
        if candidate != correct and candidate not in values:
            values.append(candidate)
        if len(values) == 3:
            return values
    raise RuntimeError("Nicht genügend unterschiedliche Ablenkungsantworten")


def groups(records: list[tuple], count: int, value_index: int) -> list[tuple]:
    candidates = []
    for combo in itertools.combinations(records, 3):
        if len({item[0] for item in combo}) < 3 or len({item[value_index] for item in combo}) < 3:
            continue
        candidates.append(combo)
    usage: Counter[str] = Counter()
    selected = []
    while candidates and len(selected) < count:
        combo = min(
            candidates,
            key=lambda items: (
                max(usage[item[0]] for item in items),
                sum(usage[item[0]] for item in items),
                tuple(item[0] for item in items),
            ),
        )
        candidates.remove(combo)
        selected.append(combo)
        usage.update(item[0] for item in combo)
    if len(selected) != count:
        raise RuntimeError(f"Nur {len(selected)} geeignete Dreiergruppen für {count} Fragen")
    return selected


def order_groups(records: list[tuple[str, int]], count: int) -> list[tuple[tuple[str, int], ...]]:
    candidates = []
    seen_answers: set[tuple[str, ...]] = set()
    for combo in itertools.combinations(records, 4):
        if len({value for _, value in combo}) < 4:
            continue
        answer = tuple(label for label, _ in sorted(combo, key=lambda item: item[1]))
        if answer in seen_answers:
            continue
        seen_answers.add(answer)
        candidates.append(combo)
    usage: Counter[str] = Counter()
    selected = []
    while candidates and len(selected) < count:
        combo = min(
            candidates,
            key=lambda items: (
                max(usage[label] for label, _ in items),
                sum(usage[label] for label, _ in items),
                tuple(label for label, _ in items),
            ),
        )
        candidates.remove(combo)
        selected.append(combo)
        usage.update(label for label, _ in combo)
    if len(selected) != count:
        raise RuntimeError(f"Nur {len(selected)} geeignete Vierergruppen für {count} Fragen")
    return selected


def add_multiple_choice(builder: Builder, category: str, count: int) -> None:
    records = DATA[category]
    for index, record in enumerate(records[:count]):
        label, relation, _predicate, _sort, estimate_prompt, estimate_value, unit = record
        if category == "human_everyday":
            correct = format_number(estimate_value)
            options_values = [correct, *numeric_distractors(estimate_value)]
            prompt = estimate_prompt
            explanation = f"Der Referenzwert beträgt {correct} {unit}."
        else:
            correct = relation
            options_values = [correct, *distinct_relations(records, index, correct)]
            prompt = MC_TEMPLATES[category].format(label=label)
            explanation = f"„{label}“ gehört hier zu: {relation}."
        shift = builder.next_id["multiple_choice"] % 4
        options_values = options_values[shift:] + options_values[:shift]
        options = dict(zip("ABCD", options_values))
        answer = next(key for key, value in options.items() if value == correct)
        builder.add("multiple_choice", category, prompt, answer, explanation, options=options)


def add_true_false(builder: Builder, category: str, count: int) -> None:
    records = DATA[category]
    for index, record in enumerate(records[:count]):
        label, relation, predicate, *_ = record
        answer = index % 2 == 0
        if answer:
            prompt = f"{label} {predicate}."
        else:
            wrong = distinct_relations(records, index, relation)[0]
            prompt = FALSE_TEMPLATES[category].format(label=label, wrong=wrong)
        explanation = f"Richtig ist: {label} {predicate}."
        builder.add("true_false", category, prompt, answer, explanation)


def add_match(builder: Builder, category: str, count: int) -> None:
    records = DATA[category]
    if category == "human_everyday":
        mapped = [(item[0], f"{format_number(item[5])} {item[6]}") for item in records]
    else:
        mapped = [(item[0], item[1]) for item in records]
    for combo in groups(mapped, count, 1):
        pairs = [(item[0], item[1]) for item in combo]
        answer = dict(pairs)
        builder.add(
            "match", category, MATCH_TEMPLATES[category], answer,
            "; ".join(f"{left} – {right}" for left, right in pairs) + ".",
            left=[left for left, _ in pairs], right=[right for _, right in pairs],
        )


def category_order_records(category: str) -> list[tuple[str, int | float]]:
    if category in ORDER_DATA:
        return ORDER_DATA[category]
    records = DATA[category]
    if category == "sport":
        records = [item for item in records if item[0] not in {"Futsal"}]
    return [(item[0], item[3]) for item in records]


def add_order(builder: Builder, category: str, count: int) -> None:
    records = category_order_records(category)
    for combo in order_groups(records, count):
        ordered = sorted(combo, key=lambda item: item[1])
        answer = [label for label, _ in ordered]
        values = " → ".join(f"{label} ({format_number(value)})" for label, value in ordered)
        items = answer[2:] + answer[:2]
        builder.add("order", category, ORDER_TEMPLATES[category], answer, values + ".", items=items)


def add_estimates(builder: Builder, category: str, count: int) -> None:
    for record in DATA[category][:count]:
        _label, _relation, _predicate, _sort, prompt, value, unit = record
        explanation = f"Der recherchierte Referenzwert beträgt {format_number(value)} {unit}."
        builder.add("estimate", category, prompt, value, explanation, unit=unit)


ADDERS = {
    "multiple_choice": add_multiple_choice,
    "true_false": add_true_false,
    "match": add_match,
    "order": add_order,
    "estimate": add_estimates,
}


def normalized_fingerprint(question: dict[str, Any]) -> str:
    answer = question["answer"]
    if question["question_type"] == "multiple_choice":
        answer = question["options"].get(answer, answer)
    canonical = {
        "type": question["question_type"],
        "prompt": " ".join(question["prompt"].casefold().split()),
        "answer": answer,
        "unit": question.get("unit", ""),
    }
    return hashlib.sha256(json.dumps(canonical, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def validate(builder: Builder) -> None:
    expected_added = 449
    if len(builder.added) != expected_added:
        raise RuntimeError(f"Erwartet: {expected_added} neue Fragen, erzeugt: {len(builder.added)}")

    all_questions = [question for questions in builder.files.values() for question in questions]
    ids = [question["id"] for question in all_questions]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Doppelte Fragen-ID")
    fingerprints = [normalized_fingerprint(question) for question in all_questions]
    if len(fingerprints) != len(set(fingerprints)):
        raise RuntimeError("Doppelter spielrelevanter Frageninhalt")

    counts: dict[tuple[str, str], int] = Counter(
        (question["question_type"], question["primary_category"]) for question in all_questions
    )
    deficient = {key: value for key, value in counts.items() if value < TARGET}
    if deficient:
        raise RuntimeError(f"Zellen unter {TARGET}: {deficient}")

    for question in builder.added:
        source = question["source"]
        if source.get("status") != "verified" or not source.get("references"):
            raise RuntimeError(f"Ungeprüfte Quelle: {question['id']}")
        if any(not item["url"].startswith("https://") for item in source["references"]):
            raise RuntimeError(f"Unsichere Quellenadresse: {question['id']}")

        question_type = question["question_type"]
        if question_type == "multiple_choice":
            if question["answer"] not in question["options"] or len(set(question["options"].values())) != 4:
                raise RuntimeError(f"Ungültige Auswahlfrage: {question['id']}")
        elif question_type == "match":
            if set(question["answer"]) != set(question["left"]) or Counter(question["answer"].values()) != Counter(question["right"]):
                raise RuntimeError(f"Ungültige Zuordnung: {question['id']}")
        elif question_type == "order":
            if Counter(question["answer"]) != Counter(question["items"]):
                raise RuntimeError(f"Ungültige Reihenfolge: {question['id']}")
        elif question_type == "estimate":
            if question["answer"] < 0:
                raise RuntimeError(f"Negative Schätzantwort: {question['id']}")


def _retired_main() -> None:
    builder = Builder()
    deficits = {}
    for category in CATEGORY_DIRS:
        if category not in DATA:
            continue
        for question_type in ACTIVE_TYPES:
            current = len(builder.files[(question_type, category)])
            need = max(0, TARGET - current)
            deficits[(question_type, category)] = need
            if need:
                ADDERS[question_type](builder, category, need)

    validate(builder)
    print(json.dumps({f"{qtype}/{category}": count for (qtype, category), count in deficits.items() if count}, ensure_ascii=False, indent=2))
    if "--apply" not in sys.argv:
        print("Trockenlauf: keine Dateien geändert.")
        return

    for key, questions in builder.files.items():
        questions.sort(key=numeric_id)
        file_path(*key).write_text(json.dumps(questions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("449 Fragen ergänzt; jede aktive Tabellenzelle enthält jetzt mindestens 25 Fragen.")


def main() -> None:
    raise SystemExit(
        "Stillgelegt: Kategorien sind keine Produktionsquoten. "
        "Dieses Skript darf den Fragenbestand nicht mehr verändern."
    )


if __name__ == "__main__":
    main()

