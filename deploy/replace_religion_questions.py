"""Remove religion questions and replace every active one with a researched item."""

from __future__ import annotations

import json
from pathlib import Path

from deploy.add_question_expansion import PHASE1
from deploy.add_question_expansion_phase2 import build_batch, cited, match, tf


ROOT = Path(__file__).resolve().parents[1]


def binary(number: int, category: str, topic: str, prompt: str, groups: dict[str, str],
           answer: dict[str, str], explanation: str, sources: str | list[str]) -> dict:
    return {
        "id": f"bs{number}", "question_type": "binary_sort",
        "primary_category": category, "subtopic": topic,
        "tags": {"topics": [topic], "entities": [], "genres": [], "regions": [], "eras": []},
        "source": cited(sources), "subject_keys": [f"binary-sort:{number}"],
        "prompt": prompt, "groups": groups, "items": list(answer),
        "answer": answer, "explanation": explanation,
    }

REMOVE = {
    "wahroderunwahr": {*(f"tf{n}" for n in range(158, 168)), *(f"tf{n}" for n in range(505, 510))},
    "multiplechoice": {"mc226", *(f"mc{n}" for n in range(505, 510))},
    "paarebilden": {"ma203", *(f"ma{n}" for n in range(505, 510))},
    "reihenfolge": {*(f"or{n}" for n in range(505, 510))},
    "schaetzung": {"es234", *(f"es{n}" for n in range(505, 510))},
    "zweigruppenzuordnen": {*(f"bs{n}" for n in range(163, 169))},
}


LEGACY_REPLACEMENTS = {
    "wahroderunwahr": [
        tf(606, "CERN stellte die Web-Software 1993 kostenlos in die Public Domain.", True, "Am 30. April 1993 gab CERN die grundlegende Web-Software zur freien Nutzung, Veränderung und Weitergabe frei.", "Freies Web", "cern_web"),
        tf(607, "Der QR-Code kam erstmals auf Kontaktlinsen-Packungen als allgemeines Konsumprodukt zum Einsatz.", True, "DENSO nennt Kontaktlinsen-Packungen als ersten Einsatz auf allgemeinen Handelsprodukten.", "QR-Code im Handel", "qr"),
        tf(608, "Bluetooth war zunächst nur als vorläufiger Codename gedacht.", True, "RadioWire oder PAN sollten den Namen ersetzen; Bluetooth setzte sich vorher bereits durch.", "Bluetooth-Codename", "bluetooth"),
        tf(609, "Ab etwa 1.000 Metern Meerestiefe dringt nach Angaben der NOAA kein Sonnenlicht mehr vor.", True, "Kaum Licht reicht tiefer als 200 Meter; unter 1.000 Metern dringt kein Sonnenlicht mehr vor.", "Dunkle Tiefsee", "noaa_dark"),
        tf(610, "Celluloid wurde als Elfenbeinersatz für Billardkugeln entwickelt, erwies sich dafür aber als ungeeignet.", True, "Der frühe halbsynthetische Kunststoff sollte Elfenbein ersetzen, funktionierte als Billardkugelmaterial jedoch nicht gut genug.", "Celluloid-Ursprung", "plastics"),
        tf(611, "Armbanduhren galten vielen Männern vor dem Ersten Weltkrieg als weibischer Schmuck.", True, "Das Smithsonian beschreibt, dass Männer sie lange als feminine Spielerei betrachteten und erst im Ersten Weltkrieg breiter trugen.", "Armbanduhr-Kultur", "wristwatch"),
        tf(612, "Blauwale können unter passenden Meeresbedingungen Artgenossen noch in rund 1.600 Kilometern Entfernung erreichen.", True, "NOAA nennt Entfernungen bis zu 1.000 Meilen, also ungefähr 1.600 Kilometer.", "Blauwal-Rufe", "bluewhale"),
        tf(613, "Der Klettverschluss wurde durch Kletten inspiriert, die an Kleidung und Fell hängen blieben.", True, "George de Mestral übertrug die Hakenstruktur der Kletten auf einen textilen Verschluss.", "Klettverschluss-Idee", "velcro"),
        tf(614, "Der DART-Einschlag veränderte nicht nur die Umlaufzeit, sondern auch die Form von Dimorphos.", True, "NASA-Auswertungen zeigen eine verkürzte Bahn und eine veränderte, länglichere Form des Asteroiden.", "DART-Formänderung", "dart"),
        tf(615, "Der Begriff CAPTCHA wurde im Jahr 2000 von einem Team der Carnegie Mellon University geprägt.", True, "Das Team entwickelte die Tests gegen Bots und prägte zugleich die Abkürzung CAPTCHA.", "CAPTCHA-Ursprung", "captcha"),
    ],
    "paarebilden": [
        match(606, "science_technology", "Coole Tech-Geburtsorte", "Ordne den digitalen Meilenstein seinem Entstehungsumfeld zu.", [("QR-Code", "DENSO in Japan"), ("World Wide Web", "CERN in der Schweiz"), ("erste SMS", "Vodafone in Großbritannien")], ["qr", "cern_web", "sms"]),
    ],
    "zweigruppenzuordnen": [
        binary(600, "science_technology", "Code mit Tiernamen", "Programmiersprache, Tiername oder beides?", {"A": "Programmiersprache", "B": "Tiername"}, {"Python": "both", "Swift": "both", "Ruby": "A", "Rust": "A", "Go": "A", "Cobra": "B", "Lemur": "B"}, "Beides: Python und Swift. Nur Programmiersprache: Ruby, Rust, Go. Nur Tiername: Cobra, Lemur.", ["python", "swift", "rust", "zoo", "dictionary"]),
        binary(601, "science_technology", "NASA und Alltagsenglisch", "NASA-Mission, englisches Alltagswort oder beides?", {"A": "NASA-Mission", "B": "englisches Alltagswort"}, {"Voyager": "both", "Curiosity": "both", "Opportunity": "both", "Spirit": "both", "Dawn": "both", "Cassini": "A", "Umbrella": "B"}, "Beides: Voyager, Curiosity, Opportunity, Spirit, Dawn. Nur NASA-Mission: Cassini. Nur Alltagswort: Umbrella.", ["nasa_history", "dictionary"]),
        binary(602, "music", "Bandnamen als Wörter", "Bandname, englisches Alltagswort oder beides?", {"A": "Bandname", "B": "englisches Alltagswort"}, {"Queen": "both", "Rush": "both", "Kiss": "both", "Journey": "both", "Heart": "both", "ABBA": "A", "Table": "B"}, "Beides: Queen, Rush, Kiss, Journey, Heart. Nur Bandname: ABBA. Nur Alltagswort: Table.", ["rockhall_words", "dictionary"]),
        binary(603, "science_technology", "Einheiten und Namen", "SI-Einheit, Nachname eines Wissenschaftlers oder beides?", {"A": "SI-Einheit", "B": "Wissenschaftler-Nachname"}, {"Watt": "both", "Pascal": "both", "Kelvin": "both", "Ampere": "both", "Candela": "A", "Einstein": "B", "Curie": "B"}, "Beides: Watt, Pascal, Kelvin, Ampere. Nur SI-Einheit: Candela. Nur Nachname: Einstein, Curie.", "bipm"),
        binary(604, "human_everyday", "Essen in Farbe", "Lebensmittel, englischer Farbname oder beides?", {"A": "Lebensmittel", "B": "englischer Farbname"}, {"Orange": "both", "Lime": "both", "Olive": "both", "Salmon": "both", "Chocolate": "both", "Pasta": "A", "Turquoise": "B"}, "Beides: Orange, Lime, Olive, Salmon, Chocolate. Nur Lebensmittel: Pasta. Nur Farbname: Turquoise.", ["usda_food", "css_colors"]),
        binary(605, "science_technology", "Computerwörter im echten Leben", "Computerbegriff, Ding außerhalb der IT oder beides?", {"A": "Computerbegriff", "B": "Ding außerhalb der IT"}, {"Mouse": "both", "Cookie": "both", "Tablet": "both", "Window": "both", "Server": "both", "Router": "A", "Muffin": "B"}, "Beides: Mouse, Cookie, Tablet, Window, Server. Nur Computerbegriff: Router. Nur außerhalb der IT: Muffin.", ["nist_glossary", "dictionary"]),
    ],
}


def replacements() -> dict[str, list[dict]]:
    phase2 = build_batch()
    wanted_ids = {
        "wahroderunwahr": {"tf616", "tf601", "tf602", "tf603", "tf604"},
        "multiplechoice": {"mc600", "mc601", "mc602", "mc603", "mc604"},
        "paarebilden": {"ma600", "ma601", "ma602", "ma603", "ma604"},
        "reihenfolge": {"or600", "or601", "or602", "or603", "or604"},
        "schaetzung": {"es600", "es601", "es602", "es603", "es604"},
        "zweigruppenzuordnen": {"bs600", "bs601", "bs602", "bs603", "bs604"},
    }
    result = {
        directory: [row for row in rows if row["id"] in wanted_ids[directory]]
        for directory, rows in phase2.items()
    }
    result["multiplechoice"].extend(PHASE1["multiplechoice"])
    result["schaetzung"].extend(row for row in PHASE1["schaetzung"] if row["id"] == "es605")
    for directory, rows in LEGACY_REPLACEMENTS.items():
        result.setdefault(directory, []).extend(rows)
    return result


def main() -> None:
    additions = replacements()
    active_removed = 0
    active_added = sum(len(rows) for directory, rows in additions.items() if directory != "zweigruppenzuordnen")
    for directory, doomed in REMOVE.items():
        path = ROOT / "fragen" / directory / "fragen.json"
        rows = json.loads(path.read_text(encoding="utf-8"))
        before = len(rows)
        rows = [row for row in rows if row["id"] not in doomed]
        removed = before - len(rows)
        if removed != len(doomed):
            raise SystemExit(f"{directory}: erwartet {len(doomed)} Entfernungen, gefunden {removed}")
        if directory != "zweigruppenzuordnen":
            active_removed += removed
        rows.extend(additions.get(directory, []))
        path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"{directory}: -{removed}, +{len(additions.get(directory, []))}")
    if active_removed != active_added:
        raise SystemExit(f"Aktiver Bestand unausgeglichen: -{active_removed}, +{active_added}")


if __name__ == "__main__":
    main()
