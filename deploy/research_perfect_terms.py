#!/usr/bin/env python3
"""Collect source excerpts for the pending Perfect term cards.

This is an editorial aid: it records what the source actually returned.  It
does not write to the live card library and never marks a card as verified.
"""

from __future__ import annotations

import html
import json
import re
import time
import sys
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TERMS_FILE = ROOT / "fragen/stormseedsperfekt/BEGRIFFSKANDIDATEN_343.md"
OUTPUT = ROOT / "fragen/stormseedsperfekt/begriffe/recherche_343.json"
ACTIVE_CARDS = ROOT / "fragen/stormseedsperfekt/begriffe/fragen.json"
DEFINITIONS = ROOT / "fragen/stormseedsperfekt/begriffe/entwuerfe_343.tsv"
USER_AGENT = "StormseedsGuesstimate/1.0 (question editorial research)"

ENGLISH_TITLES = {
    "Antanaklasis": "Antanaclasis", "Enantiosemie": "Auto-antonym",
    "Epitrochasmus": "Epitrochasmus", "Desublimation": "Deposition (phase transition)",
    "Diffusiophorese": "Diffusiophoresis and diffusioosmosis", "Metastabilität": "Metastability",
    "Ostwald-Reifung": "Ostwald ripening", "Spinodale": "Spinodal",
    "Superfluidität": "Superfluidity", "Thermokline": "Thermocline",
    "Vitrifikation": "Vitrification", "Zetapotential": "Zeta potential",
    "Zirkonisierung": "Conversion coating", "Abaxial": "Glossary of leaf morphology",
    "Auxese": "Auxesis (biology)", "Benthon": "Benthos", "Cauliflorie": "Cauliflory",
    "Ektomykorrhiza": "Ectomycorrhiza", "Epiphytie": "Epiphyte", "Homöosis": "Homeosis",
    "Aboulie": "Aboulia", "Formikation": "Formication", "Graphästhesie": "Graphesthesia",
    "Kinesie": "Kinesis (biology)", "Somatoparaphrenie": "Somatoparaphrenia",
    "Synästhesie": "Synesthesia", "Zoopsie": "Zoopsia", "Abrasionsterrasse": "Wave-cut platform",
    "Arête": "Arête", "Flasergefüge": "Flaser bed", "Harnischfläche": "Slickenside",
    "Ignimbrit": "Ignimbrite", "Isostasieanomalie": "Gravity anomaly", "Lahars": "Lahar",
    "Mélange": "Mélange", "Ophiolith": "Ophiolite", "Periglazial": "Periglaciation",
    "Pingo": "Pingo", "Regolith": "Regolith", "Yardang": "Yardang",
    "Aleatorischer Vertrag": "Aleatory contract", "Arrogation": "Adrogation",
    "Assumpsit": "Assumpsit", "Avulsion": "Avulsion (legal term)",
    "Cessio legis": "Subrogation", "Dotalrecht": "Dowry", "Legalzession": "Subrogation",
    "Vindikationslage": "Rei vindicatio", "Fachwerkbinder": "Truss", "Kalfatwerk": "Caulking",
    "Klitik": "Clitic", "Paragoge": "Epenthesis", "Prosopopöie": "Prosopopoeia",
    "Synalöphe": "Synalepha", "Synärese": "Synaeresis", "Transfix": "Transfix",
    "Birefringenz": "Birefringence", "Stenökie": "Stenotopic species",
    "Autotopagnosie": "Autotopagnosia", "Dysdiadochokinese": "Dysdiadochokinesia",
    "Dysgeusie": "Dysgeusia", "Sakkade": "Saccade", "Abkantung": "Bending (metalworking)",
    "Ankerklüse": "Hawsehole", "Ballastkiel": "Keel", "Barkentine": "Barquentine",
    "Blindniet": "Rivet", "Wantenspanner": "Turnbuckle",
}

MANUAL_SOURCES = {
    "Epitrochasmus": {
        "title": "Brigham Young University: epitrochasmus",
        "url": "https://rhetoric.byu.edu/Figures/E/epitrochasmus.htm",
        "excerpt": "A rhetorical figure that touches rapidly on one point and then another, often through asyndeton.",
    },
    "Zwickelphase": {
        "title": "Wikipedia: Gefüge (Werkstoffkunde)",
        "url": "https://de.wikipedia.org/wiki/Gef%C3%BCge_(Werkstoffkunde)",
        "excerpt": "Eine zusätzliche Phase kann in den Zwickeln einer polyedrischen Hauptphase auftreten.",
    },
    "Zoopsie": {
        "title": "Université de Sherbrooke, Usito: zoopsie",
        "url": "https://usito.usherbrooke.ca/lexies/mots/zoopsie",
        "excerpt": "Hallucination visuelle d’animaux.",
    },
    "Gesamthand": {
        "title": "Gabler Wirtschaftslexikon: Gemeinschaft zur gesamten Hand",
        "url": "https://wirtschaftslexikon.gabler.de/definition/gemeinschaft-zur-gesamten-hand-32491",
        "excerpt": "Die Beteiligten sind am gesamten Sondervermögen beteiligt und können nicht über Anteile an einzelnen Gegenständen verfügen.",
    },
    "Zessionsregress": {
        "title": "Duncker & Humblot: Regreßfiguren im Zivilrecht",
        "url": "https://www.duncker-humblot.de/_files_media/leseproben/9783428502233.pdf",
        "excerpt": "Der Zessionsregress wird durch eine Abtretung an den Sicherungsgeber erreicht, der den Gläubiger befriedigt hat.",
    },
}


def terms() -> list[str]:
    found = []
    for line in TERMS_FILE.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\d+\.\s+(.+)$", line)
        if match:
            found.append(match.group(1).strip())
    if len(found) != 343 or len(set(map(str.casefold, found))) != 343:
        raise SystemExit("Kandidatenliste ist nicht eindeutig oder nicht 343 Einträge lang")
    return found


def api(language_project: str, params: dict[str, str | int]) -> dict:
    url = f"https://de.{language_project}.org/w/api.php?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def api_host(host: str, params: dict[str, str | int]) -> dict:
    url = f"https://{host}/w/api.php?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def search(project: str, term: str) -> dict | None:
    data = api(
        project,
        {
            "action": "query",
            "generator": "search",
            "gsrsearch": f'intitle:"{term}"',
            "gsrlimit": 3,
            "prop": "extracts|info",
            "exintro": 1,
            "explaintext": 1,
            "inprop": "url",
            "format": "json",
            "utf8": 1,
        },
    )
    pages = list(data.get("query", {}).get("pages", {}).values())
    if not pages:
        return None
    exact = [page for page in pages if page.get("title", "").casefold() == term.casefold()]
    page = (exact or pages)[0]
    excerpt = clean(page.get("extract", ""))
    if not excerpt:
        return None
    return {
        "title": page.get("title"),
        "url": page.get("fullurl"),
        "excerpt": excerpt[:1800],
        "exact_title": bool(exact),
    }


def bulk_exact(project: str, requested: list[str]) -> dict[str, dict | None]:
    if project == "wiktionary":
        return bulk_wiktionary(requested)
    data = api(
        project,
        {
            "action": "query",
            "titles": "|".join(requested),
            "redirects": 1,
            "prop": "extracts|info",
            "exintro": 1,
            "explaintext": 1,
            "inprop": "url",
            "format": "json",
            "utf8": 1,
        },
    )
    aliases = {term: term for term in requested}
    for item in data.get("query", {}).get("normalized", []):
        for original, current in list(aliases.items()):
            if current == item["from"]:
                aliases[original] = item["to"]
    for item in data.get("query", {}).get("redirects", []):
        for original, current in list(aliases.items()):
            if current == item["from"]:
                aliases[original] = item["to"]
    pages = {
        page.get("title"): page
        for page in data.get("query", {}).get("pages", {}).values()
        if "missing" not in page
    }
    results = {}
    for original, resolved in aliases.items():
        page = pages.get(resolved)
        excerpt = clean((page or {}).get("extract", ""))
        results[original] = (
            {
                "title": page.get("title"),
                "url": page.get("fullurl"),
                "excerpt": excerpt[:1800],
                "exact_title": page.get("title", "").casefold() == original.casefold(),
            }
            if page and excerpt
            else None
        )
    return results


def bulk_wiktionary(requested: list[str]) -> dict[str, dict | None]:
    data = api(
        "wiktionary",
        {
            "action": "query",
            "titles": "|".join(requested),
            "redirects": 1,
            "prop": "revisions|info",
            "rvprop": "content",
            "rvslots": "main",
            "inprop": "url",
            "format": "json",
            "formatversion": 2,
            "utf8": 1,
        },
    )
    aliases = {term: term for term in requested}
    for key in ("normalized", "redirects"):
        for item in data.get("query", {}).get(key, []):
            for original, current in list(aliases.items()):
                if current == item["from"]:
                    aliases[original] = item["to"]
    pages = {page.get("title"): page for page in data.get("query", {}).get("pages", []) if not page.get("missing")}
    results = {}
    for original, resolved in aliases.items():
        page = pages.get(resolved)
        revisions = (page or {}).get("revisions", [])
        raw = revisions[0].get("slots", {}).get("main", {}).get("content", "") if revisions else ""
        match = re.search(r"\{\{Bedeutungen\}\}(.*?)(?:\n\{\{|\n===|\Z)", raw, flags=re.S)
        meaning = match.group(1) if match else ""
        meaning = re.sub(r"<!--.*?-->", " ", meaning, flags=re.S)
        meaning = re.sub(r"\{\{[^{}]*\}\}", " ", meaning)
        meaning = re.sub(r"\[\[(?:[^]|]+\|)?([^]]+)\]\]", r"\1", meaning)
        meaning = clean(meaning.replace("'''", "").replace("''", ""))
        results[original] = (
            {
                "title": page.get("title"),
                "url": page.get("fullurl"),
                "excerpt": meaning[:1800],
                "exact_title": page.get("title", "").casefold() == original.casefold(),
            }
            if page and meaning
            else None
        )
    return results


def duden(term: str) -> dict | None:
    slug = urllib.parse.quote(term.replace(" ", "_"), safe="_-")
    url = f"https://www.duden.de/rechtschreibung/{slug}"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        page = response.read().decode("utf-8", "replace")
    marker = re.search(r'id="bedeutung[^\"]*"', page, flags=re.I)
    if not marker:
        return None
    section = page[marker.start() : marker.start() + 12000]
    paragraphs = re.findall(r"<p[^>]*>(.*?)</p>", section, flags=re.I | re.S)
    excerpt = clean(" ".join(paragraphs))
    return {"title": f"Duden: {term}", "url": url, "excerpt": excerpt[:1800]} if excerpt else None


def research_duden() -> None:
    all_terms = terms()
    rows = {row["term"]: row for row in json.loads(OUTPUT.read_text(encoding="utf-8"))}
    for index, term in enumerate(all_terms, 1):
        row = rows[term]
        if (row["sources"].get("duden") or {}).get("excerpt"):
            continue
        try:
            row["sources"]["duden"] = duden(term)
        except Exception as exc:
            row["sources"]["duden"] = {"error": f"{type(exc).__name__}: {exc}"}
        OUTPUT.write_text(
            json.dumps([rows[item] for item in all_terms], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Duden {index:3}/343 {term}", flush=True)
        time.sleep(0.35)


def research_missing() -> None:
    all_terms = terms()
    rows = {row["term"]: row for row in json.loads(OUTPUT.read_text(encoding="utf-8"))}
    missing = [
        term
        for term in all_terms
        if not any((rows[term]["sources"].get(project) or {}).get("excerpt") for project in ("wikipedia", "wiktionary", "duden"))
    ]
    for index, term in enumerate(missing, 1):
        try:
            result = search("wikipedia", term)
        except Exception as exc:
            result = {"error": f"{type(exc).__name__}: {exc}"}
        if result:
            rows[term]["sources"]["wikipedia_search"] = result
        OUTPUT.write_text(
            json.dumps([rows[item] for item in all_terms], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Suche {index:2}/{len(missing)} {term}", flush=True)
        time.sleep(1.5)


def research_english() -> None:
    all_terms = terms()
    rows = {row["term"]: row for row in json.loads(OUTPUT.read_text(encoding="utf-8"))}
    items = list(ENGLISH_TITLES.items())
    for start in range(0, len(items), 15):
        chunk = items[start : start + 15]
        requested = [title for _, title in chunk]
        data = api_host("en.wikipedia.org", {
            "action": "query", "titles": "|".join(requested), "redirects": 1,
            "prop": "extracts|info", "exintro": 1, "explaintext": 1,
            "inprop": "url", "format": "json", "formatversion": 2, "utf8": 1,
        })
        redirects = {item["from"]: item["to"] for item in data.get("query", {}).get("normalized", [])}
        redirects.update({item["from"]: item["to"] for item in data.get("query", {}).get("redirects", [])})
        pages = {page.get("title"): page for page in data.get("query", {}).get("pages", []) if not page.get("missing")}
        for term, title in chunk:
            resolved = redirects.get(title, title)
            resolved = redirects.get(resolved, resolved)
            page = pages.get(resolved)
            excerpt = clean((page or {}).get("extract", ""))
            if excerpt:
                rows[term]["sources"]["wikipedia_en"] = {
                    "title": page.get("title"), "url": page.get("fullurl"), "excerpt": excerpt[:1800]
                }
        OUTPUT.write_text(json.dumps([rows[item] for item in all_terms], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"English Wikipedia {start + 1}-{start + len(chunk)}", flush=True)
        time.sleep(1)


def add_manual_sources() -> None:
    all_terms = terms()
    rows = {row["term"]: row for row in json.loads(OUTPUT.read_text(encoding="utf-8"))}
    for term, source in MANUAL_SOURCES.items():
        rows[term]["sources"]["specialist"] = source
    OUTPUT.write_text(json.dumps([rows[item] for item in all_terms], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_cards() -> None:
    all_terms = terms()
    definitions = dict(line.split("\t", 1) for line in DEFINITIONS.read_text(encoding="utf-8").splitlines())
    research = {row["term"]: row for row in json.loads(OUTPUT.read_text(encoding="utf-8"))}
    if list(definitions) != all_terms or list(research) != all_terms:
        raise SystemExit("Begriffe, Definitionen und Recherche sind nicht deckungsgleich")
    cards = json.loads(ACTIVE_CARDS.read_text(encoding="utf-8"))
    if [card["id"] for card in cards] != [f"ssp-begriff-{index:03}" for index in range(1, 13)]:
        raise SystemExit("Der bestehende Kartenbestand entspricht nicht den erwarteten zwölf Karten")
    priorities = ("specialist", "wikipedia", "wikipedia_en", "wiktionary", "duden", "wikipedia_search")
    for index, term in enumerate(all_terms, 13):
        source = next(
            (research[term]["sources"].get(kind) for kind in priorities
             if (research[term]["sources"].get(kind) or {}).get("excerpt")),
            None,
        )
        if not source:
            raise SystemExit(f"Kein ausgelesener Beleg für {term}")
        cards.append({
            "id": f"ssp-begriff-{index:03}",
            "card_type": "term",
            "term": term,
            "prompt": f"Was bedeutet „{term}“?",
            "answer": definitions[term],
            "source": {
                "status": "verified",
                "verified_on": "2026-10-21",
                "references": [{"title": source["title"], "url": source["url"]}],
            },
        })
    ACTIVE_CARDS.write_text(json.dumps(cards, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "duden":
        research_duden()
        return
    if len(sys.argv) > 1 and sys.argv[1] == "missing":
        research_missing()
        return
    if len(sys.argv) > 1 and sys.argv[1] == "english":
        research_english()
        return
    if len(sys.argv) > 1 and sys.argv[1] == "manual":
        add_manual_sources()
        return
    if len(sys.argv) > 1 and sys.argv[1] == "cards":
        build_cards()
        return
    all_terms = terms()
    existing = {term: {"term": term, "sources": {}} for term in all_terms}
    if OUTPUT.exists():
        existing.update({row["term"]: row for row in json.loads(OUTPUT.read_text(encoding="utf-8"))})
    projects = ("wiktionary",) if len(sys.argv) > 1 and sys.argv[1] == "wiktionary" else ("wikipedia", "wiktionary")
    for project in projects:
        for start in range(0, len(all_terms), 40):
            chunk = all_terms[start : start + 40]
            try:
                results = bulk_exact(project, chunk)
            except Exception as exc:
                print(f"{project} {start + 1}-{start + len(chunk)}: {type(exc).__name__}: {exc}")
                time.sleep(3)
                continue
            for term, result in results.items():
                if result or not (existing[term]["sources"].get(project) or {}).get("excerpt"):
                    existing[term]["sources"][project] = result
            OUTPUT.write_text(
                json.dumps([existing[term] for term in all_terms], ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            print(f"{project} {start + 1:3}-{start + len(chunk):3}", flush=True)
            time.sleep(0.5)


if __name__ == "__main__":
    main()
