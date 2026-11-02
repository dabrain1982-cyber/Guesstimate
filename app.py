from __future__ import annotations

from lobby_overview import render_overview
from leaderboard_views import currency_rankings, init_currency_peaks, record_currency_peak, winner_rows

import hashlib
import json
import math
import os
import secrets
import sqlite3
import smtplib
import ssl
from collections import Counter
from datetime import date, datetime, timedelta
from email.message import EmailMessage
from functools import wraps
from pathlib import Path
from typing import Any

from flask import (
    Flask,
    abort,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
from lobby_view import lobby_player_profiles

from questions import (
    CATEGORY_LABELS,
    CATEGORY_ORDER,
    KNOWLEDGE_CATEGORY_LABELS,
    QUESTION_BANK,
)
from nerd_mode import init_nerd_db, register_nerd_routes
from card_table import init_card_table_db, register_card_table_routes
from blackjack import init_blackjack_db, register_blackjack_routes
from conquest import init_conquest_db, register_conquest_routes
from dice_table import init_dice_table_db, register_dice_table_routes


GREETINGS = [
    "Heute Weltwissen oder wieder gepflegtes Halbwissen?",
    "Dein Bauchgefühl hat sich warmgelaufen. Hoffentlich.",
    "Fünf Fragen. Keine Ausreden. Los geht’s.",
    "Google ist heute leider nicht mit im Team.",
    "Zeit, gefährliches Halbwissen in Punkte zu verwandeln.",
    "Dein Platz in der Tabelle wirkt noch etwas provisorisch.",
    "Kurz überlegen, dann selbstbewusst danebenliegen.",
]
DEFAULT_PHRASE = "Noch kein Spruch gewählt."

MIN_ESTIMATE_POINTS = 10
MIN_QUESTION_POINTS = 10
MAX_QUESTION_POINTS = 100
MAX_PLAYERS = 100
DEFAULT_GAME_NAME = "stormseed´s guesstimate"
RELEASE_VERSION = "2026.10.24-pool-home-mail-v1"
QUESTION_FULL_TIME_SECONDS = (5.0, 5.0, 5.0, 8.0, 5.0)
FEEDBACK_SECONDS = 4
QUESTION_DECAY_SECONDS = (5.0, 7.0, 10.0, 12.0, 20.0)
QUESTION_TIME_LIMITS = tuple(
    hold + decay
    for hold, decay in zip(QUESTION_FULL_TIME_SECONDS, QUESTION_DECAY_SECONDS)
)
PARTY_START_COUNTDOWN_SECONDS = 6
PARTY_FEEDBACK_SECONDS = 4
PARTY_FINAL_FEEDBACK_SECONDS = 8
PARTY_NEXT_COUNTDOWN_SECONDS = 2
PARTY_PRESENCE_TIMEOUT_SECONDS = 30
PARTY_PRESENCE_WRITE_SECONDS = 3
CONTENT_START_DATE = date(2026, 9, 30)
CONTENT_DAY_OFFSET = 3
CATEGORY_OFFSETS = {
    "true_false": 0,
    "multiple_choice": 3,
    "match": 7,
    "order": 11,
    "estimate": 15,
}

AVATAR_CATALOG = [
    {"id": "a01", "name": "Kea", "trait": "Neugierig", "price": 2000, "asset": "stage/a01-kea.webp", "stage_asset": "stage/a01-kea.webp"},
    {"id": "a02", "name": "Wasserschwein", "trait": "Tiefenentspannt", "price": 2000, "asset": "a02-wasserschwein.webp", "stage_asset": "stage/a02-wasserschwein.webp"},
    {"id": "a03", "name": "Wanderfalke", "trait": "Übermotiviert", "price": 2000, "asset": "a03-wanderfalke.webp", "stage_asset": "stage/a03-wanderfalke.webp"},
    {"id": "a04", "name": "Faultier", "trait": "Effizient faul", "price": 2000, "asset": "a04-faultier.webp", "stage_asset": "stage/a04-faultier.webp"},
    {"id": "a05", "name": "Waschbär", "trait": "Improvisiert alles", "price": 2000, "asset": "a05-waschbaer.webp", "stage_asset": "stage/a05-waschbaer.webp"},
    {"id": "a06", "name": "Oktopus", "trait": "Multitasking", "price": 2000, "asset": "a06-oktopus.webp", "stage_asset": "stage/a06-oktopus.webp"},
    {"id": "a07", "name": "Ziege", "trait": "Unbeirrbar", "price": 2000, "asset": "a07-ziege.webp", "stage_asset": "stage/a07-ziege.webp"},
    {"id": "a08", "name": "Krähe", "trait": "Weiß es besser", "price": 2000, "asset": "a08-kraehe.webp", "stage_asset": "stage/a08-kraehe.webp"},
    {"id": "a09", "name": "Fennek", "trait": "Hört alles", "price": 2000, "asset": "a09-fennek.webp", "stage_asset": "stage/a09-fennek.webp"},
    {"id": "a10", "name": "Wombat", "trait": "Unerschütterlich", "price": 2000, "asset": "a10-wombat.webp", "stage_asset": "stage/a10-wombat.webp"},
    {"id": "a11", "name": "Gans", "trait": "Elegantes Chaos", "price": 2000, "asset": "a11-gans.webp", "stage_asset": "stage/a11-gans.webp"},
    {"id": "a12", "name": "Fangschreckenkrebs", "trait": "Sieht alles", "price": 2000, "asset": "a12-fangschreckenkrebs.webp", "stage_asset": "stage/a12-fangschreckenkrebs.webp"},
    {"id": "a13", "name": "Axolotl", "trait": "Unheilbar optimistisch", "price": 2000, "asset": "a13-axolotl.webp", "stage_asset": "stage/a13-axolotl.webp"},
    {"id": "a14", "name": "Somnus", "trait": "Döst strategisch", "price": 2000, "asset": "a14-somnus-cutout-v2.png", "stage_asset": "stage/a14-somnus-cutout-v2.png"},
    {"id": "a15", "name": "Ember", "trait": "Feuer und Flamme", "price": 2000, "asset": "a15-ember-cutout-v2.png", "stage_asset": "stage/a15-ember-cutout-v2.png"},
    {"id": "a16", "name": "Myrli", "trait": "Leuchtet ein", "price": 2000, "asset": "a16-myrli-cutout-v2.png", "stage_asset": "stage/a16-myrli-cutout-v2.png"},
    {"id": "a17", "name": "Luno", "trait": "Zielsicher verträumt", "price": 2000, "asset": "a17-luno-cutout-v2.png", "stage_asset": "stage/a17-luno-cutout-v2.png"},
    {"id": "a18", "name": "Nimbus", "trait": "Hat den Dreh raus", "price": 2000, "asset": "a18-nimbus-cutout-v2.png", "stage_asset": "stage/a18-nimbus-cutout-v2.png"},
]

PLAQUE_CATALOG = [
    {"id": "p01", "name": "Tavernenschild", "material": "Alte Eiche", "price": 3000, "asset": "p01.webp", "podium_asset": "p01-tavernenschild-v1.png", "perfect_podium_asset": "p01-tavernenschild-tall-v2.png", "desk_asset": "p01-tavernenschild-v1.png"},
    {"id": "p02", "name": "Schiefer", "material": "Stein & Quarz", "price": 3000, "asset": "p02.webp", "podium_asset": "p02-schiefer-v1.png", "perfect_podium_asset": "p02-schiefer-tall-v2.png", "desk_asset": "p02-schiefer-v1.png"},
    {"id": "p03", "name": "Gebürsteter Stahl", "material": "Kühler Stahl", "price": 3000, "asset": "p03.webp", "podium_asset": "p03-arena-console-v2.png", "perfect_podium_asset": "p03-arena-console-tall-v3.png", "desk_asset": "p03-arena-console-v2.png"},
    {"id": "p04", "name": "Gefalteter Stahl", "material": "Damaststruktur", "price": 3000, "asset": "p04.webp", "podium_asset": "p04-gefalteter-stahl-v1.png", "perfect_podium_asset": "p04-gefalteter-stahl-tall-v2.png", "desk_asset": "p04-gefalteter-stahl-v1.png"},
    {"id": "p05", "name": "Neonglas", "material": "Glas & Licht", "price": 3000, "asset": "p05.webp", "podium_asset": "p05-neonglas-v1.png", "perfect_podium_asset": "p05-neonglas-tall-v2.png", "desk_asset": "p05-neonglas-v1.png"},
    {"id": "p06", "name": "Theatersamt", "material": "Samt & Gold", "price": 3000, "asset": "p06.webp", "podium_asset": "p06-theatersamt-v1.png", "perfect_podium_asset": "p06-theatersamt-tall-v2.png", "desk_asset": "p06-theatersamt-v1.png"},
    {"id": "p07", "name": "Arcade-Acryl", "material": "Acryl & Konfetti", "price": 3000, "asset": "p07.webp", "podium_asset": "p07-arcade-acryl-v1.png", "perfect_podium_asset": "p07-arcade-acryl-tall-v2.png", "desk_asset": "p07-arcade-acryl-v1.png"},
    {"id": "p08", "name": "Emaille-Schild", "material": "Emaille & Metall", "price": 3000, "asset": "p08.webp", "podium_asset": "p08-emaille-v1.png", "perfect_podium_asset": "p08-emaille-tall-v2.png", "desk_asset": "p08-emaille-v1.png"},
    {"id": "p09", "name": "Kupferpatina", "material": "Kupfer & Grünspan", "price": 3000, "asset": "p09.webp", "podium_asset": "p09-kupferpatina-v1.png", "perfect_podium_asset": "p09-kupferpatina-tall-v2.png", "desk_asset": "p09-kupferpatina-v1.png"},
    {"id": "p10", "name": "Reiseleder", "material": "Leder & Messing", "price": 3000, "asset": "p10.webp", "podium_asset": "p10-reiseleder-v1.png", "perfect_podium_asset": "p10-reiseleder-tall-v2.png", "desk_asset": "p10-reiseleder-v1.png"},
    {"id": "p11", "name": "Kristalleis", "material": "Eis & Kristall", "price": 3000, "asset": "p11.webp", "podium_asset": "p11-kristalleis-v1.png", "perfect_podium_asset": "p11-kristalleis-tall-v2.png", "desk_asset": "p11-kristalleis-v1.png"},
    {"id": "p12", "name": "Wurzelholz", "material": "Holz, Moos & Pilze", "price": 3000, "asset": "p12.webp", "podium_asset": "p12-wurzelholz-v1.png", "perfect_podium_asset": "p12-wurzelholz-tall-v2.png", "desk_asset": "p12-wurzelholz-v1.png"},
    {"id": "p13", "name": "Spielhallen-Beton", "material": "Beton & Neon", "price": 3000, "asset": "p13.webp", "podium_asset": "p13-baustellenmeister-v1.png", "perfect_podium_asset": "p13-baustellenmeister-tall-v2.png", "desk_asset": "p13-baustellenmeister-v1.png"},
]

BACKGROUND_CATALOG = [
    {"id": "b01", "name": "Arena-Rundblick", "mood": "Neon & große Bühne", "price": 1000, "asset": "arena-stage-background-v2.png"},
    {"id": "b02", "name": "Clubzimmer", "mood": "Holz, Pflanzen & Abendlicht", "price": 1000, "asset": "stormseeds-perfect-clubroom-v1.png"},
    {"id": "b03", "name": "Wissensatelier", "mood": "Bücher, Sterne & warmes Licht", "price": 1000, "asset": "background-wissensatelier-v1.png"},
    {"id": "b04", "name": "Neon-Garten", "mood": "Botanik & Nachtlichter", "price": 1000, "asset": "background-neon-garten-v1.png"},
    {"id": "b05", "name": "Bergsee", "mood": "Weite, Wasser & Morgenlicht", "price": 1000, "asset": "background-bergsee-v1.png"},
    {"id": "b06", "name": "Quiz-Kosmos", "mood": "Galaxien & Leuchtpflanzen", "price": 1000, "asset": "background-quiz-kosmos-v1.png"},
    {"id": "b07", "name": "Gameshow-Arena", "mood": "Publikum & Scheinwerfer", "price": 1000, "asset": "background-gameshow-arena-v1.png"},
    {"id": "b08", "name": "Mediterraner Hof", "mood": "Sonne, Stein & Terrakotta", "price": 1000, "asset": "background-mediterraner-hof-v1.png"},
    {"id": "b09", "name": "Papierlandschaft", "mood": "Papier, Farbe & Fernblick", "price": 1000, "asset": "background-papierlandschaft-v1.png"},
    {"id": "b10", "name": "Wolkenpavillon", "mood": "Pastell, Wolken & Ruhe", "price": 1000, "asset": "background-wolkenpavillon-v1.png"},
]

PHRASE_CATALOG = [
    {"id": f"s{index:02d}", "text": text, "name": f"Spruch {index}", "price": 250}
    for index, text in enumerate((
        "Ich wusste es. Also fast.",
        "Wissen ist Macht. Halbwissen reicht hier aber völlig.",
        "Ich rate nicht. Ich interpretiere Fakten kreativ.",
        "Selbstbewusstsein ersetzt erstaunlich viel Wissen.",
        "Falsch geraten, überzeugend vorgetragen.",
        "Meine Bildung hat heute leider frei.",
        "Ich bin nicht ahnungslos. Ich bin ergebnisoffen.",
        "Google wäre jetzt stolz auf mich. Oder peinlich berührt.",
        "Kompetenz wird maßlos überschätzt.",
        "Ich kam, sah und lag daneben.",
        "Andere haben Wissen. Ich habe Ausstrahlung.",
        "Knapp daneben ist auch eine Form von Präzision.",
        "Wenn ich raten will, frage ich mich selbst.",
        "Fakten sind auch nur Meinungen mit Quellenangabe.",
        "Ich kenne die Antwort. Sie kennt mich nur noch nicht.",
        "Heute Genie, morgen wieder realistisch.",
        "Mein gefährliches Halbwissen ist vollständig geladen.",
        "Ich verliere nicht. Ich sammle dramatische Wendungen.",
        "Niveau ist keine Punktzahl.",
        "Erst antworten, dann denken – spart Zeit.",
        "Ich spiele nicht schlecht. Ihr versteht nur meine Strategie nicht.",
        "Bescheidenheit ist etwas für die unteren Ranglistenplätze.",
        "Für diese Antwort möchte ich einen Telefonjoker verklagen.",
        "Bildungslücke? Ich nenne das geistigen Freiraum.",
        "Ich bin der Grund, warum Multiple Choice vier Antworten braucht.",
        "Intelligenz sieht bei mir nur aus wie Glück.",
        "Wissen vergeht. Mein Punktestand bleibt peinlich.",
        "Wer richtig liegt, hat nur weniger mutig geraten.",
        "Ich habe keine Ahnung – aber davon erschreckend viel.",
        "Gegen mich zu verlieren ist immerhin eine gute Geschichte.",
        "Wenn Arroganz Punkte gäbe, wäre das hier vorbei.",
        "Ich benötige keine Fakten. Ich habe eine starke Meinung.",
        "Mein Gehirn lädt noch. Bitte nicht aktualisieren.",
        "Das war taktisch falsch.",
        "Ich lasse euch gewinnen. Aus sozialen Gründen.",
        "Irren ist menschlich. Ich bin heute besonders menschlich.",
        "Mein Wissen endet dort, wo die Frage beginnt.",
        "Die Antwort war richtig, bevor ich sie angeklickt habe.",
        "Ich bin nicht Letzter. Ich kontrolliere das Tabellenende.",
        "Diese Runde wird später aus meiner Biografie gestrichen.",
    ), 1)
]

DEFAULT_AVATAR = {
    "id": "a00",
    "name": "Start-Avatar",
    "trait": "Neutraler Klassiker",
    "asset": "starter-neutral.svg",
    "public_asset": "starter-neutral-public.svg",
    "stage_asset": "starter-neutral.svg",
    "price": 0,
}
DEFAULT_PLAQUE = {
    "id": "p00",
    "name": "Startpult",
    "material": "Neutral",
    "price": 0,
    "asset": None,
    "podium_asset": "p00-startpult-v1.png",
    "perfect_podium_asset": "p00-startpult-tall-v2.png",
    "desk_asset": "p00-startpult-v1.png",
}
DEFAULT_BACKGROUND = {
    "id": "b00",
    "name": "Neon-Arena",
    "mood": "Der Guesstimate-Klassiker",
    "price": 0,
    "asset": "arena-stage-background-v1.png",
}
DEFAULT_AVATAR_ID = "a00"
DEFAULT_PLAQUE_ID = "p00"
DEFAULT_BACKGROUND_ID = "b00"
DEFAULT_PHRASE_ID = ""


class ForwardedPrefixMiddleware:
    """Make generated URLs respect a prefix stripped by the reverse proxy."""

    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        prefix = environ.get("HTTP_X_FORWARDED_PREFIX", "").rstrip("/")
        if prefix:
            environ["SCRIPT_NAME"] = prefix
        return self.wsgi_app(environ, start_response)


class QuestionPoolExhausted(RuntimeError):
    pass


def configured_secret_key() -> str:
    secret_file = os.environ.get("QUIZ_SECRET_KEY_FILE")
    if secret_file:
        return Path(secret_file).read_text(encoding="utf-8").strip()
    return os.environ.get("QUIZ_SECRET_KEY", "dev-only-change-me")
def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=configured_secret_key(),
        # UI-Arbeit wird direkt aus dem einzigen Projektordner ausgeliefert.
        # Der Produktionsprozess darf deshalb Templates bei geändertem
        # Dateistempel neu laden, ohne dass für jede Layoutkorrektur ein
        # privilegierter Dienstneustart nötig ist.
        TEMPLATES_AUTO_RELOAD=True,
        SEND_FILE_MAX_AGE_DEFAULT=0,
        DATABASE=os.environ.get(
            "QUIZ_DATABASE", str(Path(app.instance_path) / "quiz.sqlite3")
        ),
        GAME_NAME=os.environ.get("QUIZ_GAME_NAME", DEFAULT_GAME_NAME),
        APPLICATION_ROOT=os.environ.get("QUIZ_URL_PREFIX", "/"),
        MAIL_USER=os.environ.get("QUIZ_MAIL_USER", ""),
        MAIL_TO=os.environ.get("QUIZ_MAIL_TO", ""),
        MAIL_PASSWORD_FILE=os.environ.get("QUIZ_MAIL_PASSWORD_FILE", ""),
        PUBLIC_URL=os.environ.get("QUIZ_PUBLIC_URL", "").rstrip("/"),
        PREVIEW_CURRENCY_BONUS=int(os.environ.get("QUIZ_PREVIEW_CURRENCY_BONUS", "0")),
        OWNER_USERNAME=normalize_username(os.environ.get("QUIZ_OWNER_USERNAME", "stormseed")),
        CARD_TABLE_ENABLED=os.environ.get("QUIZ_ENABLE_CARD_TABLE", "1") == "1",
        LOCAL_DEVELOPMENT=os.environ.get("QUIZ_LOCAL_DEVELOPMENT", "0") == "1",
        OFFLINE_VERSION=os.environ.get("QUIZ_OFFLINE_VERSION", ""),
        SESSION_COOKIE_NAME=os.environ.get("QUIZ_SESSION_COOKIE_NAME", "session"),
        DAILY_CATCHUP_EXCLUDED_WEEKS=("2026-10-26",),
        DICE_TABLE_AVAILABLE=True,
        KNIFFEL_AVAILABLE=True,
        MAEXCHEN_AVAILABLE=True,
        TABLETOP_FAMILY_HUBS_AVAILABLE=True,
    )
    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    register_database(app)
    register_routes(app)
    from inbox import init_inbox, register_inbox
    register_inbox(app, login_required, require_csrf, is_owner_user)
    from public_profiles import register_public_profiles
    register_public_profiles(app, login_required, player_cosmetics, player_total_points, player_trophy_counts, rank_rows)
    register_nerd_routes(app)
    if app.config["CARD_TABLE_ENABLED"]:
        register_card_table_routes(app, login_required, require_csrf)
        register_blackjack_routes(app, login_required, require_csrf)
        register_conquest_routes(app, login_required, require_csrf)
    register_dice_table_routes(app, login_required, require_csrf)
    register_template_helpers(app)
    app.wsgi_app = ForwardedPrefixMiddleware(app.wsgi_app)

    with app.app_context():
        init_db()
        init_inbox(get_db())
        init_nerd_db(get_db)
        if app.config["CARD_TABLE_ENABLED"]:
            init_card_table_db(get_db)
            init_blackjack_db(get_db)
            init_conquest_db(get_db)
        init_dice_table_db(get_db)
        init_currency_peaks(get_db(), app.config['PREVIEW_CURRENCY_BONUS'])

    return app


def register_database(app: Flask) -> None:
    def get_db() -> sqlite3.Connection:
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON")
        return g.db

    def close_db(_: BaseException | None = None) -> None:
        db = g.pop("db", None)
        if db is not None:
            db.close()

    app.teardown_appcontext(close_db)
    app.get_db = get_db  # type: ignore[attr-defined]


def get_db() -> sqlite3.Connection:
    from flask import current_app

    return current_app.get_db()  # type: ignore[attr-defined]


def init_db() -> None:
    get_db().executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            display_name TEXT NOT NULL,
            pin_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS daily_rounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            round_date TEXT NOT NULL UNIQUE,
            questions_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            round_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'playing',
            current_index INTEGER NOT NULL DEFAULT 0,
            multiplier REAL NOT NULL DEFAULT 1.0,
            estimate_raw INTEGER,
            score INTEGER,
            rank_before INTEGER,
            rank_after INTEGER,
            started_at TEXT NOT NULL,
            question_started_at TEXT,
            completed_at TEXT,
            UNIQUE(user_id, round_id),
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(round_id) REFERENCES daily_rounds(id)
        );

        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            attempt_id INTEGER NOT NULL,
            question_id TEXT NOT NULL,
            answer_json TEXT NOT NULL,
            correct INTEGER NOT NULL,
            credit REAL NOT NULL,
            multiplier_delta REAL NOT NULL,
            time_factor REAL NOT NULL DEFAULT 1.0,
            response_seconds REAL NOT NULL DEFAULT 0.0,
            accuracy_points INTEGER NOT NULL DEFAULT 0,
            points INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            UNIQUE(attempt_id, question_id),
            FOREIGN KEY(attempt_id) REFERENCES attempts(id)
        );

        CREATE TABLE IF NOT EXISTS login_days (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            login_date TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(user_id, login_date),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS vacation_uses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            missed_date TEXT NOT NULL,
            used_at TEXT NOT NULL,
            UNIQUE(user_id, missed_date),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS question_usage (
            question_id TEXT PRIMARY KEY,
            content_hash TEXT,
            category TEXT NOT NULL,
            source_type TEXT NOT NULL,
            source_id TEXT NOT NULL,
            used_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS party_lobbies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            host_user_id INTEGER NOT NULL,
            rounds INTEGER NOT NULL DEFAULT 1,
            status TEXT NOT NULL DEFAULT 'waiting',
            current_question_index INTEGER NOT NULL DEFAULT 0,
            questions_json TEXT,
            question_started_at TEXT,
            countdown_ends_at TEXT,
            created_at TEXT NOT NULL,
            started_at TEXT,
            completed_at TEXT,
            FOREIGN KEY(host_user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS party_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lobby_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            score INTEGER NOT NULL DEFAULT 0,
            joined_at TEXT NOT NULL,
            last_seen_at TEXT,
            UNIQUE(lobby_id, user_id),
            FOREIGN KEY(lobby_id) REFERENCES party_lobbies(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS party_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lobby_id INTEGER NOT NULL,
            member_id INTEGER NOT NULL,
            question_index INTEGER NOT NULL,
            question_id TEXT NOT NULL,
            answer_json TEXT NOT NULL,
            correct INTEGER NOT NULL,
            credit REAL NOT NULL,
            response_seconds REAL NOT NULL,
            accuracy_points INTEGER NOT NULL,
            points INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(member_id, question_index),
            FOREIGN KEY(lobby_id) REFERENCES party_lobbies(id),
            FOREIGN KEY(member_id) REFERENCES party_members(id)
        );

        CREATE TABLE IF NOT EXISTS system_notifications (
            kind TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            sent_at TEXT
        );

        CREATE TABLE IF NOT EXISTS user_cosmetics (
            user_id INTEGER PRIMARY KEY,
            avatar_id TEXT NOT NULL DEFAULT 'a00',
            plaque_id TEXT NOT NULL DEFAULT 'p00',
            background_id TEXT NOT NULL DEFAULT 'b00',
            phrase_id TEXT NOT NULL DEFAULT '',
            developer_enabled INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS shop_purchases (
            user_id INTEGER NOT NULL,
            item_type TEXT NOT NULL,
            item_id TEXT NOT NULL,
            price INTEGER NOT NULL,
            purchased_at TEXT NOT NULL,
            PRIMARY KEY(user_id, item_type, item_id),
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS data_migrations (
            id TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS party_members_lobby_idx ON party_members(lobby_id);
        CREATE INDEX IF NOT EXISTS party_answers_lobby_idx ON party_answers(lobby_id);

        CREATE INDEX IF NOT EXISTS attempts_user_idx ON attempts(user_id);
        CREATE INDEX IF NOT EXISTS attempts_round_idx ON attempts(round_id);
        CREATE INDEX IF NOT EXISTS login_days_user_idx ON login_days(user_id);
        CREATE INDEX IF NOT EXISTS vacation_uses_user_idx ON vacation_uses(user_id);

        CREATE TRIGGER IF NOT EXISTS users_limit_100
        BEFORE INSERT ON users
        WHEN (SELECT COUNT(*) FROM users) >= 100
        BEGIN
            SELECT RAISE(ABORT, 'player_limit_reached');
        END;

        INSERT OR IGNORE INTO login_days (user_id, login_date, created_at)
        SELECT id, substr(created_at, 1, 10), created_at
        FROM users
        WHERE date(substr(created_at, 1, 10)) IS NOT NULL;

        INSERT OR IGNORE INTO login_days (user_id, login_date, created_at)
        SELECT user_id, substr(started_at, 1, 10), started_at
        FROM attempts
        WHERE date(substr(started_at, 1, 10)) IS NOT NULL;
        """
    )
    attempt_columns = {
        row["name"] for row in get_db().execute("PRAGMA table_info(attempts)").fetchall()
    }
    if "question_started_at" not in attempt_columns:
        get_db().execute("ALTER TABLE attempts ADD COLUMN question_started_at TEXT")
    answer_columns = {
        row["name"] for row in get_db().execute("PRAGMA table_info(answers)").fetchall()
    }
    if "time_factor" not in answer_columns:
        get_db().execute(
            "ALTER TABLE answers ADD COLUMN time_factor REAL NOT NULL DEFAULT 1.0"
        )
    if "response_seconds" not in answer_columns:
        get_db().execute(
            "ALTER TABLE answers ADD COLUMN response_seconds REAL NOT NULL DEFAULT 0.0"
        )
    if "accuracy_points" not in answer_columns:
        get_db().execute(
            "ALTER TABLE answers ADD COLUMN accuracy_points INTEGER NOT NULL DEFAULT 0"
        )
    if "points" not in answer_columns:
        get_db().execute(
            "ALTER TABLE answers ADD COLUMN points INTEGER NOT NULL DEFAULT 0"
        )
    cosmetics_columns = {
        row["name"]
        for row in get_db().execute("PRAGMA table_info(user_cosmetics)").fetchall()
    }
    if "background_id" not in cosmetics_columns:
        get_db().execute(
            "ALTER TABLE user_cosmetics ADD COLUMN background_id TEXT NOT NULL DEFAULT 'b00'"
        )
    if "developer_enabled" not in cosmetics_columns:
        get_db().execute(
            "ALTER TABLE user_cosmetics ADD COLUMN developer_enabled INTEGER NOT NULL DEFAULT 0"
        )
    if "phrase_id" not in cosmetics_columns:
        get_db().execute(
            "ALTER TABLE user_cosmetics ADD COLUMN phrase_id TEXT NOT NULL DEFAULT ''"
        )
    usage_columns = {
        row["name"]
        for row in get_db().execute("PRAGMA table_info(question_usage)").fetchall()
    }
    if "content_hash" not in usage_columns:
        get_db().execute("ALTER TABLE question_usage ADD COLUMN content_hash TEXT")
    party_lobby_columns = {
        row["name"]
        for row in get_db().execute("PRAGMA table_info(party_lobbies)").fetchall()
    }
    if "countdown_ends_at" not in party_lobby_columns:
        get_db().execute("ALTER TABLE party_lobbies ADD COLUMN countdown_ends_at TEXT")
    party_member_columns = {
        row["name"]
        for row in get_db().execute("PRAGMA table_info(party_members)").fetchall()
    }
    if "last_seen_at" not in party_member_columns:
        get_db().execute("ALTER TABLE party_members ADD COLUMN last_seen_at TEXT")
    get_db().execute(
        "UPDATE party_members SET last_seen_at = joined_at WHERE last_seen_at IS NULL"
    )
    question_lookup = {
        item["id"]: (category, item)
        for category, bank in QUESTION_BANK.items()
        for item in bank
    }
    stored_question_sources = [
        ("daily_rounds", "round_date", row["round_date"], row["questions_json"])
        for row in get_db()
        .execute("SELECT round_date, questions_json FROM daily_rounds")
        .fetchall()
    ]
    stored_question_sources.extend(
        ("party_lobbies", "id", row["id"], row["questions_json"])
        for row in get_db()
        .execute(
            "SELECT id, questions_json FROM party_lobbies WHERE questions_json IS NOT NULL"
        )
        .fetchall()
    )
    for table, key_column, key_value, questions_json in stored_question_sources:
        questions = json.loads(questions_json)
        changed = False
        for question in questions:
            found = question_lookup.get(question["id"])
            if (
                found
                and not question.get("knowledge_category")
                and found[1].get("knowledge_category")
            ):
                question["knowledge_category"] = found[1]["knowledge_category"]
                changed = True
        if changed:
            get_db().execute(
                f"UPDATE {table} SET questions_json = ? WHERE {key_column} = ?",
                (json.dumps(questions, ensure_ascii=False), key_value),
            )
    for row in get_db().execute(
        "SELECT question_id FROM question_usage WHERE content_hash IS NULL"
    ).fetchall():
        found = question_lookup.get(row["question_id"])
        if found:
            category, question = found
            get_db().execute(
                "UPDATE OR IGNORE question_usage SET content_hash = ? WHERE question_id = ?",
                (question_fingerprint(question, category), row["question_id"]),
            )
    get_db().execute(
        """
        UPDATE question_usage
        SET content_hash = NULL
        WHERE content_hash IS NOT NULL
          AND rowid NOT IN (
              SELECT MIN(rowid) FROM question_usage
              WHERE content_hash IS NOT NULL
              GROUP BY content_hash
          )
        """
    )
    get_db().execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS question_usage_content_hash_idx
        ON question_usage(content_hash)
        WHERE content_hash IS NOT NULL
        """
    )

    existing_sources: list[tuple[str, str, str]] = []
    existing_sources.extend(
        ("daily", row["round_date"], row["questions_json"])
        for row in get_db().execute(
            "SELECT round_date, questions_json FROM daily_rounds"
        ).fetchall()
    )
    existing_sources.extend(
        ("party", str(row["id"]), row["questions_json"])
        for row in get_db().execute(
            "SELECT id, questions_json FROM party_lobbies WHERE questions_json IS NOT NULL"
        ).fetchall()
    )
    for source_type, source_id, questions_json in existing_sources:
        for question in json.loads(questions_json):
            get_db().execute(
                """
                INSERT OR IGNORE INTO question_usage
                    (question_id, content_hash, category, source_type, source_id, used_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    question["id"],
                    question_fingerprint(question),
                    question["category"],
                    source_type,
                    source_id,
                    datetime.now().isoformat(timespec="seconds"),
                ),
            )
    get_db().commit()


def normalize_username(value: str) -> str:
    return " ".join(value.strip().casefold().split())


def today_iso() -> str:
    return date.today().isoformat()


def active_round_date() -> str:
    today = today_iso()
    selected = session.get("active_round_date", today)
    if selected != today and catchup_week_excluded(date.fromisoformat(selected)):
        session.pop("active_round_date", None)
        session.pop("catchup_queue", None)
        return today
    return selected


def catchup_week_excluded(day: date) -> bool:
    monday = day - timedelta(days=day.weekday())
    return monday.isoformat() in current_app.config["DAILY_CATCHUP_EXCLUDED_WEEKS"]


def missed_current_week_dates(user_id: int, current_day: date | None = None) -> list[str]:
    today = current_day or date.today()
    monday = today - timedelta(days=today.weekday())
    if catchup_week_excluded(today):
        return []
    played = {
        row["round_date"]
        for row in get_db().execute(
            """
            SELECT r.round_date
            FROM attempts a
            JOIN daily_rounds r ON r.id = a.round_id
            WHERE a.user_id = ? AND a.status = 'completed'
              AND r.round_date BETWEEN ? AND ?
            """,
            (user_id, monday.isoformat(), today.isoformat()),
        ).fetchall()
    }
    return [
        (monday + timedelta(days=offset)).isoformat()
        for offset in range((today - monday).days)
        if (monday + timedelta(days=offset)).isoformat() not in played
    ]


def record_daily_login(user_id: int, login_day: date | None = None) -> bool:
    """Count at most one login per day and report whether it was the first."""

    database = get_db()
    cursor = database.execute(
        """
        INSERT OR IGNORE INTO login_days (user_id, login_date, created_at)
        VALUES (?, ?, ?)
        """,
        (
            user_id,
            (login_day or date.today()).isoformat(),
            datetime.now().isoformat(timespec="seconds"),
        ),
    )
    database.commit()
    return cursor.rowcount == 1


def content_day_number(day: str) -> int:
    return (date.fromisoformat(day) - CONTENT_START_DATE).days + CONTENT_DAY_OFFSET


def content_cycle_position(day: str) -> int:
    question_count = min(len(bank) for bank in QUESTION_BANK.values())
    return content_day_number(day) % question_count


def daily_questions(day: str) -> list[dict[str, Any]]:
    selected = []
    day_number = content_day_number(day)
    for category in CATEGORY_ORDER:
        bank = QUESTION_BANK[category]
        index = (day_number + CATEGORY_OFFSETS[category]) % len(bank)
        question = dict(bank[index])
        question["category"] = category
        selected.append(question)
    return selected


def question_fingerprint(
    question: dict[str, Any], question_type: str | None = None
) -> str:
    """Return a stable identity for a question even if its ID changes."""

    format_name = question_type or question.get("category", "")
    answer: Any = question.get("answer")
    if format_name == "multiple_choice":
        answer = question.get("options", {}).get(answer, answer)

    def normalize(value: Any) -> Any:
        if isinstance(value, str):
            return " ".join(value.casefold().split())
        if isinstance(value, dict):
            return {str(key): normalize(item) for key, item in sorted(value.items())}
        if isinstance(value, list):
            return [normalize(item) for item in value]
        return value

    canonical = {
        "format": format_name,
        "prompt": normalize(question.get("prompt", "")),
        "answer": normalize(answer),
        "unit": normalize(question.get("unit", "")),
    }
    encoded = json.dumps(
        canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(encoded.encode()).hexdigest()


def question_subject_keys(question: dict[str, Any]) -> set[str]:
    """Return stable topic keys used to keep related questions apart."""

    return {str(value) for value in question.get("subject_keys", []) if value}


def reserve_question_sets(
    source_type: str,
    source_id: str,
    set_count: int = 1,
    *,
    manage_transaction: bool = True,
) -> list[list[dict[str, Any]]]:
    """Atomically reserve globally unused questions for daily or party play."""

    database = get_db()
    if manage_transaction:
        database.execute("BEGIN IMMEDIATE")
    try:
        used_ids = {
            row["question_id"]
            for row in database.execute("SELECT question_id FROM question_usage").fetchall()
        }
        used_hashes = {
            row["content_hash"]
            for row in database.execute(
                "SELECT content_hash FROM question_usage WHERE content_hash IS NOT NULL"
            ).fetchall()
        }
        question_lookup = {
            item["id"]: item for bank in QUESTION_BANK.values() for item in bank
        }
        recent_subjects: set[str] = set()
        recent_knowledge_categories: Counter[str] = Counter()
        for row in database.execute(
            """
            SELECT question_id FROM question_usage
            ORDER BY used_at DESC, rowid DESC
            LIMIT 50
            """
        ).fetchall():
            previous = question_lookup.get(row["question_id"])
            if previous:
                recent_subjects.update(question_subject_keys(previous))
                if previous.get("knowledge_category"):
                    recent_knowledge_categories[previous["knowledge_category"]] += 1

        available_by_category: dict[str, list[dict[str, Any]]] = {}
        for category in CATEGORY_ORDER:
            available = []
            available_hashes: set[str] = set()
            for item in QUESTION_BANK[category]:
                content_hash = question_fingerprint(item, category)
                if (
                    item["id"] in used_ids
                    or content_hash in used_hashes
                    or content_hash in available_hashes
                ):
                    continue
                available.append(item)
                available_hashes.add(content_hash)
            if len(available) < set_count:
                raise QuestionPoolExhausted(
                    f"Für {CATEGORY_LABELS[category]} sind nicht mehr genug neue Fragen vorhanden."
                )
            available_by_category[category] = available

        sets: list[list[dict[str, Any]]] = [[] for _ in range(set_count)]
        reservation_subjects: set[str] = set()
        for set_index in range(set_count):
            set_knowledge_categories: set[str] = set()
            for category in CATEGORY_ORDER:
                candidates = available_by_category[category]

                def mixing_score(item: dict[str, Any]) -> tuple[int, int, int, int, str]:
                    subjects = question_subject_keys(item)
                    knowledge_category = item.get("knowledge_category")
                    return (
                        len(subjects & reservation_subjects),
                        len(subjects & recent_subjects),
                        int(
                            bool(knowledge_category)
                            and knowledge_category in set_knowledge_categories
                        ),
                        recent_knowledge_categories[knowledge_category],
                        hashlib.sha256(
                            f"{source_type}:{source_id}:{set_index}:{category}:{item['id']}".encode()
                        ).hexdigest(),
                    )

                original = min(candidates, key=mixing_score)
                candidates.remove(original)
                question = dict(original)
                question["category"] = category
                sets[set_index].append(question)
                reservation_subjects.update(question_subject_keys(question))
                if question.get("knowledge_category"):
                    set_knowledge_categories.add(question["knowledge_category"])

        now = datetime.now().isoformat(timespec="seconds")
        for question_set in sets:
            for question in question_set:
                database.execute(
                    """
                    INSERT INTO question_usage
                        (question_id, content_hash, category, source_type, source_id, used_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        question["id"],
                        question_fingerprint(question),
                        question["category"],
                        source_type,
                        source_id,
                        now,
                    ),
                )
        # A successful reservation proves that a new complete set was available.
        # Rearm the warning for this supply, including after an earlier refill.
        database.execute(
            """
            UPDATE system_notifications SET created_at = ?, sent_at = NULL
            WHERE kind = 'question_pool_exhausted'
            """,
            (now,),
        )
        if manage_transaction:
            database.commit()
        return sets
    except Exception:
        if manage_transaction:
            database.rollback()
        raise


def record_pool_exhausted() -> None:
    get_db().execute(
        """
        INSERT OR IGNORE INTO system_notifications (kind, created_at)
        VALUES ('question_pool_exhausted', ?)
        """,
        (datetime.now().isoformat(timespec="seconds"),),
    )
    get_db().commit()
    try:
        send_pool_exhausted_email()
    except (OSError, smtplib.SMTPException) as error:
        # The pending row remains unsent and can be retried after mail setup is fixed.
        current_app.logger.warning("Fragenvorrat-Mail nicht versendet: %s", error)


def pool_mail_ready() -> bool:
    from flask import current_app

    password_file = current_app.config.get("MAIL_PASSWORD_FILE", "")
    return bool(
        current_app.config.get("MAIL_USER", "")
        and current_app.config.get("MAIL_TO", "")
        and password_file
        and Path(password_file).is_file()
        and Path(password_file).stat().st_size > 0
    )


def send_pool_exhausted_email() -> bool:
    from flask import current_app

    row = get_db().execute(
        "SELECT * FROM system_notifications WHERE kind = 'question_pool_exhausted'"
    ).fetchone()
    if not row or row["sent_at"]:
        return bool(row and row["sent_at"])
    user = current_app.config.get("MAIL_USER", "")
    recipient = current_app.config.get("MAIL_TO", "")
    password_file = current_app.config.get("MAIL_PASSWORD_FILE", "")
    if not pool_mail_ready():
        current_app.logger.warning("Fragenvorrat-Mail: Mailkonfiguration unvollständig")
        return False
    password = Path(password_file).read_text(encoding="utf-8").strip()
    message = EmailMessage()
    message["From"] = user
    message["To"] = recipient
    message["Subject"] = "Stormseed´s Guesstimate: Neue Fragen werden benötigt"
    pool = question_pool_status()
    remaining = "\n".join(
        f"- {CATEGORY_LABELS[category]}: {pool['remaining'][category]}"
        for category in CATEGORY_ORDER
    )
    message.set_content(
        "Für Stormseed´s Guesstimate ist keine neue vollständige Fragerunde mehr verfügbar.\n\n"
        f"Unverbrauchte Fragen je Frageart:\n{remaining}\n\n"
        "Die normale Startseite bleibt sichtbar; nur nicht verfügbare Spielrunden sind gesperrt.\n"
        "Es werden keine alten Fragen automatisch wiederverwendet. Neuer Fragen-Nachschub wird benötigt."
    )
    context = ssl.create_default_context()
    with smtplib.SMTP("mail.gmx.net", 587, timeout=15) as smtp:
        smtp.starttls(context=context)
        smtp.login(user, password)
        smtp.send_message(message)
    get_db().execute(
        "UPDATE system_notifications SET sent_at = ? WHERE kind = 'question_pool_exhausted'",
        (datetime.now().isoformat(timespec="seconds"),),
    )
    get_db().commit()
    return True


def question_pool_status() -> dict[str, Any]:
    used_ids = {
        row["question_id"]
        for row in get_db().execute("SELECT question_id FROM question_usage").fetchall()
    }
    used_hashes = {
        row["content_hash"]
        for row in get_db()
        .execute(
            "SELECT content_hash FROM question_usage WHERE content_hash IS NOT NULL"
        )
        .fetchall()
    }
    remaining_questions: dict[str, list[dict[str, Any]]] = {}
    for category, bank in QUESTION_BANK.items():
        unique_fresh: dict[str, dict[str, Any]] = {}
        for question in bank:
            content_hash = question_fingerprint(question, category)
            if question["id"] in used_ids or content_hash in used_hashes:
                continue
            unique_fresh.setdefault(content_hash, question)
        remaining_questions[category] = list(unique_fresh.values())
    remaining = {
        category: len(questions)
        for category, questions in remaining_questions.items()
    }
    remaining_by_knowledge_category = Counter(
        question.get("knowledge_category")
        for questions in remaining_questions.values()
        for question in questions
        if question.get("knowledge_category")
    )
    return {
        "remaining": remaining,
        "remaining_by_knowledge_category": {
            category: remaining_by_knowledge_category[category]
            for category in KNOWLEDGE_CATEGORY_LABELS
        },
        "complete_rounds": min(remaining.values()),
        "exhausted": min(remaining.values()) == 0,
    }


def get_or_create_round(day: str | None = None) -> sqlite3.Row:
    day = day or today_iso()
    database = get_db()
    row = database.execute(
        "SELECT * FROM daily_rounds WHERE round_date = ?", (day,)
    ).fetchone()
    if row:
        return row
    try:
        database.execute("BEGIN IMMEDIATE")
        row = database.execute(
            "SELECT * FROM daily_rounds WHERE round_date = ?", (day,)
        ).fetchone()
        if row:
            database.commit()
            return row
        questions = reserve_question_sets(
            "daily", day, 1, manage_transaction=False
        )[0]
        now = datetime.now().isoformat(timespec="seconds")
        database.execute(
            "INSERT INTO daily_rounds (round_date, questions_json, created_at) VALUES (?, ?, ?)",
            (day, json.dumps(questions, ensure_ascii=False), now),
        )
        database.commit()
        if question_pool_status()["exhausted"]:
            record_pool_exhausted()
    except Exception:
        database.rollback()
        raise
    return database.execute(
        "SELECT * FROM daily_rounds WHERE round_date = ?", (day,)
    ).fetchone()


def rank_rows(scope: str = "all", reference_day: str | None = None) -> list[dict[str, Any]]:
    reference_day = reference_day or today_iso()
    if scope == "daily":
        score_expression = "CASE WHEN r.round_date = ? THEN a.score ELSE 0 END"
        round_expression = "CASE WHEN r.round_date = ? THEN 1 END"
        parameters: tuple[Any, ...] = (reference_day, reference_day)
    elif scope == "weekly":
        current_day = date.fromisoformat(reference_day)
        week_start = current_day - timedelta(days=current_day.weekday())
        week_end = week_start + timedelta(days=6)
        score_expression = "CASE WHEN r.round_date BETWEEN ? AND ? THEN a.score ELSE 0 END"
        round_expression = "CASE WHEN r.round_date BETWEEN ? AND ? THEN 1 END"
        parameters = (
            week_start.isoformat(),
            week_end.isoformat(),
            week_start.isoformat(),
            week_end.isoformat(),
        )
    elif scope == "all":
        score_expression = "a.score"
        round_expression = "a.id"
        parameters = ()
    else:
        raise ValueError(f"Unbekannte Bestenlisten-Ansicht: {scope}")

    rows = get_db().execute(
        f"""
        SELECT u.id, u.display_name,
               COALESCE(uc.avatar_id, ?) AS avatar_id,
               COALESCE(uc.plaque_id, ?) AS plaque_id,
               COALESCE(SUM({score_expression}), 0) AS points,
               COUNT({round_expression}) AS rounds
        FROM users u
        LEFT JOIN user_cosmetics uc ON uc.user_id = u.id
        LEFT JOIN attempts a ON a.user_id = u.id AND a.status = 'completed'
        LEFT JOIN daily_rounds r ON r.id = a.round_id
        GROUP BY u.id, u.display_name, uc.avatar_id, uc.plaque_id
        ORDER BY points DESC, u.display_name COLLATE NOCASE ASC
        """,
        (DEFAULT_AVATAR_ID, DEFAULT_PLAQUE_ID, *parameters),
    ).fetchall()
    if scope != "all":
        rows = [row for row in rows if int(row["rounds"]) > 0]
    leaderboard = []
    last_points = None
    last_rank = 0
    for index, row in enumerate(rows, 1):
        points = int(row["points"])
        if points != last_points:
            last_rank = index
            last_points = points
        leaderboard.append(
            {
                "id": row["id"],
                "display_name": row["display_name"],
                "avatar_id": row["avatar_id"],
                "plaque_id": row["plaque_id"],
                "points": points,
                "rounds": int(row["rounds"]),
                "rank": last_rank,
            }
        )
    return leaderboard


def current_rank(user_id: int) -> int:
    return next(item["rank"] for item in rank_rows() if item["id"] == user_id)


def leaderboard_slice(user_id: int, visible: int = 5) -> tuple[list[dict], dict | None]:
    leaderboard = rank_rows()
    return leaderboard, None


def leaderboard_sets(reference_day: str | None = None) -> dict[str, list[dict[str, Any]]]:
    current, peaks = currency_rankings(get_db(), current_app.config.get('PREVIEW_CURRENCY_BONUS', 0))
    return {
        "daily": rank_rows("daily", reference_day),
        "weekly": rank_rows("weekly", reference_day),
        "all": rank_rows("all"),
        "weekly_wins": weekly_winner_rows(),
        "daily_wins": winner_rows(get_db(), 'daily', today_iso()),
        "currency_current": current,
        "currency_high": peaks,
    }


def weekly_winner_rows(reference_day: str | None = None) -> list[dict[str, Any]]:
    return winner_rows(get_db(), "weekly", reference_day or today_iso())


def previous_daily_winner(reference_day: date | None = None) -> dict[str, Any] | None:
    yesterday = (reference_day or date.today()) - timedelta(days=1)
    winners = rank_rows("daily", yesterday.isoformat())
    return winners[0] if winners else None


def player_total_points(user_id: int) -> int:
    row = get_db().execute(
        """
        SELECT COALESCE(SUM(score), 0) AS points
        FROM attempts
        WHERE user_id = ? AND status = 'completed'
        """,
        (user_id,),
    ).fetchone()
    return int(row["points"])


def player_currency_balance(user_id: int) -> int:
    spent = get_db().execute(
        "SELECT COALESCE(SUM(price), 0) FROM shop_purchases WHERE user_id = ?",
        (user_id,),
    ).fetchone()[0]
    return max(
        0,
        player_total_points(user_id)
        - int(spent)
        + int(current_app.config.get("PREVIEW_CURRENCY_BONUS", 0)),
    )


def player_cosmetics(user_id: int) -> dict[str, Any]:
    row = get_db().execute(
        "SELECT avatar_id, plaque_id, background_id, phrase_id, developer_enabled FROM user_cosmetics WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    return {
        "avatar_id": row["avatar_id"] if row else DEFAULT_AVATAR_ID,
        "plaque_id": row["plaque_id"] if row else DEFAULT_PLAQUE_ID,
        "background_id": row["background_id"] if row else DEFAULT_BACKGROUND_ID,
        "phrase_id": row["phrase_id"] if row else DEFAULT_PHRASE_ID,
        "developer_enabled": bool(row["developer_enabled"]) if row else False,
    }


def is_owner_user(user_id: int) -> bool:
    row = get_db().execute("SELECT username FROM users WHERE id = ?", (user_id,)).fetchone()
    return bool(row and row["username"] == current_app.config["OWNER_USERNAME"])


def catalog_ids(item_type: str) -> set[str]:
    if item_type == "avatar":
        return {DEFAULT_AVATAR_ID, *(item["id"] for item in AVATAR_CATALOG)}
    if item_type == "plaque":
        return {DEFAULT_PLAQUE_ID, *(item["id"] for item in PLAQUE_CATALOG)}
    if item_type == "background":
        return {DEFAULT_BACKGROUND_ID, *(item["id"] for item in BACKGROUND_CATALOG)}
    if item_type == "phrase":
        return {item["id"] for item in PHRASE_CATALOG}
    return set()


def owned_catalog_ids(user_id: int, item_type: str) -> set[str]:
    defaults = (
        {DEFAULT_AVATAR_ID}
        if item_type == "avatar"
        else {DEFAULT_PLAQUE_ID}
        if item_type == "plaque"
        else {DEFAULT_BACKGROUND_ID}
        if item_type == "background"
        else set()
    )
    rows = get_db().execute(
        "SELECT item_id FROM shop_purchases WHERE user_id = ? AND item_type = ?",
        (user_id, item_type),
    ).fetchall()
    owned = defaults | {row["item_id"] for row in rows}
    cosmetics = player_cosmetics(user_id)
    if is_owner_user(user_id) and cosmetics["developer_enabled"]:
        return catalog_ids(item_type)
    return owned


def player_trophy_counts(user_id: int, reference_day: date | None = None) -> dict[str, int]:
    """Count finalized first-place finishes for the compact profile cabinet."""
    today = reference_day or date.today()
    rows = get_db().execute(
        """
        SELECT r.round_date, a.user_id, COALESCE(a.score, 0) AS score
        FROM attempts a
        JOIN daily_rounds r ON r.id = a.round_id
        WHERE a.status = 'completed' AND r.round_date < ?
        ORDER BY r.round_date
        """,
        (today.isoformat(),),
    ).fetchall()

    daily_scores: dict[str, dict[int, int]] = {}
    weekly_scores: dict[tuple[int, int], dict[int, int]] = {}
    monthly_scores: dict[tuple[int, int], dict[int, int]] = {}
    current_week = today.isocalendar()[:2]
    current_month = (today.year, today.month)
    for row in rows:
        round_day = date.fromisoformat(row["round_date"])
        score = int(row["score"])
        daily_scores.setdefault(row["round_date"], {})[row["user_id"]] = score

        week_key = round_day.isocalendar()[:2]
        if week_key < current_week:
            week = weekly_scores.setdefault(week_key, {})
            week[row["user_id"]] = week.get(row["user_id"], 0) + score

        month_key = (round_day.year, round_day.month)
        if month_key < current_month:
            month = monthly_scores.setdefault(month_key, {})
            month[row["user_id"]] = month.get(row["user_id"], 0) + score

    def wins(periods: dict[Any, dict[int, int]]) -> int:
        return sum(
            1
            for scores in periods.values()
            if user_id in scores and scores[user_id] == max(scores.values())
        )

    party_scores: dict[int, dict[int, int]] = {}
    for row in get_db().execute(
        """
        SELECT pl.id AS lobby_id, pm.user_id, pm.score
        FROM party_lobbies pl
        JOIN party_members pm ON pm.lobby_id = pl.id
        WHERE pl.status = 'completed' AND pm.status = 'active'
        """
    ).fetchall():
        party_scores.setdefault(row["lobby_id"], {})[row["user_id"]] = int(row["score"])

    return {
        "daily": wins(daily_scores),
        "weekly": wins(weekly_scores),
        "monthly": wins(monthly_scores),
        "party": wins(party_scores),
    }


def estimate_points(
    guess: float, answer: float, percentage_base: float | None = None
) -> tuple[int, float]:
    """Score an estimate by its percentage deviation from a meaningful base.

    Most quantities use the answer itself as their base. Calendar years are
    different: year zero is an arbitrary origin, so an 80-year miss must not
    look like a tiny error merely because the date is around 1900. Their
    caller therefore supplies a 100-year reference span.
    """

    base = abs(answer if percentage_base is None else percentage_base)
    if base == 0:
        relative_error = 0.0 if guess == answer else 1.0
    else:
        relative_error = abs(guess - answer) / base
    points = max(
        MIN_ESTIMATE_POINTS,
        round(100 * max(0.0, 1.0 - relative_error)),
    )
    return points, relative_error


def question_time_factor(elapsed_seconds: float, question_index: int) -> float:
    """Return the server-authoritative factor in one-second steps."""

    limit = QUESTION_TIME_LIMITS[question_index]
    decay = QUESTION_DECAY_SECONDS[question_index]
    hold = QUESTION_FULL_TIME_SECONDS[question_index]
    elapsed = max(0.0, elapsed_seconds)
    if elapsed <= hold:
        return 1.0
    if elapsed >= limit:
        return 0.0
    elapsed_decay_seconds = math.floor(elapsed - hold)
    return (decay - elapsed_decay_seconds) / decay


def timed_question_points(accuracy_points: int, time_factor: float) -> int:
    """Apply a 100–50% time multiplier; fully wrong stays at zero."""

    accuracy = min(MAX_QUESTION_POINTS, max(0, accuracy_points))
    if accuracy == 0:
        return 0
    factor = min(1.0, max(0.0, time_factor))
    time_multiplier = 0.5 + 0.5 * factor
    value = int(math.floor(accuracy * time_multiplier + 0.5))
    return max(MIN_QUESTION_POINTS, value)


def order_question_points(correct_count: int, time_factor: float) -> int:
    """Score exact-position hits for a four-item ordering question.

    One correct position is largely unavoidable in a four-item permutation, so
    ordering questions use their own deliberately flatter point table. The
    normal time factor interpolates between the late and no-deduction values.
    """

    if not 0 <= correct_count <= 4:
        raise ValueError("Ungültige Anzahl richtiger Positionen")
    late_points = (0, 10, 25, 50, 50)
    fast_points = (0, 15, 50, 100, 100)
    factor = min(1.0, max(0.0, time_factor))
    value = late_points[correct_count] + (
        fast_points[correct_count] - late_points[correct_count]
    ) * factor
    return int(math.floor(value + 0.5))


def awarded_question_points(evaluation: dict[str, Any], time_factor: float) -> int:
    """Apply the category-specific time scoring to an evaluated answer."""

    if "order_correct_count" in evaluation:
        return order_question_points(evaluation["order_correct_count"], time_factor)
    return timed_question_points(evaluation["accuracy_points"], time_factor)


def partial_credit(correct_count: int, total_count: int) -> float:
    if total_count <= 0 or not 0 <= correct_count <= total_count:
        raise ValueError("Ungültige Teilwertung")
    return correct_count / total_count


def match_option_order(question: dict[str, Any], seed_value: str) -> list[str]:
    """Return a deterministic derangement of the correct match order."""

    correct_order = [question["answer"][left] for left in question["left"]]
    if len(correct_order) < 2:
        return correct_order
    seed = int(hashlib.sha256(seed_value.encode()).hexdigest()[:8], 16)
    shift = 1 + seed % (len(correct_order) - 1)
    return correct_order[shift:] + correct_order[:shift]


def format_answer(question: dict[str, Any], value: Any) -> str:
    category = question["category"]
    if category == "true_false":
        return "Wahr" if value else "Falsch"
    if category == "multiple_choice":
        return f"{value}: {question['options'].get(value, value)}"
    if category == "estimate":
        number = f"{float(value):g}".replace(".", ",")
        return f"{number} {question['unit']}"
    if category == "order":
        return " → ".join(value)
    if category == "match":
        return " · ".join(f"{left} → {right}" for left, right in value.items())
    return str(value)


def answer_review(daily_round: sqlite3.Row, attempt: sqlite3.Row) -> list[dict[str, Any]]:
    questions = json.loads(daily_round["questions_json"])
    answer_rows = get_db().execute(
        "SELECT * FROM answers WHERE attempt_id = ? ORDER BY id", (attempt["id"],)
    ).fetchall()
    answers_by_id = {row["question_id"]: row for row in answer_rows}
    review = []
    for question in questions:
        row = answers_by_id.get(question["id"])
        if row is None:
            continue
        submitted = json.loads(row["answer_json"])
        order_correct_count = (
            order_correct_positions(submitted, question["answer"])
            if question["category"] == "order"
            else None
        )
        review.append(
            {
                "question": question,
                "category_label": CATEGORY_LABELS[question["category"]],
                "knowledge_category_label": KNOWLEDGE_CATEGORY_LABELS.get(
                    question.get("knowledge_category"), ""
                ),
                "submitted": format_answer(question, submitted),
                "correct_answer": format_answer(question, question["answer"]),
                "credit": float(row["credit"]),
                "time_factor": float(row["time_factor"]),
                "response_seconds": float(row["response_seconds"]),
                "accuracy_points": int(row["accuracy_points"]),
                "points": int(row["points"]),
                "order_correct_count": order_correct_count,
            }
        )
    return review


def order_correct_positions(submitted: list[str], correct: list[str]) -> int:
    if (
        not isinstance(submitted, list)
        or len(submitted) != len(correct)
        or not all(isinstance(item, str) for item in submitted)
        or set(submitted) != set(correct)
    ):
        raise ValueError("Ungültige Reihenfolge")
    return sum(
        submitted_item == correct_item
        for submitted_item, correct_item in zip(submitted, correct)
    )


def order_credit(submitted: list[str], correct: list[str]) -> float:
    if not correct:
        raise ValueError("Ungültige Reihenfolge")
    return partial_credit(order_correct_positions(submitted, correct), len(correct))


def evaluate(question: dict[str, Any], form: dict[str, str]) -> dict[str, Any]:
    category = question["category"]
    order_correct_count = None
    if category == "multiple_choice":
        value = form.get("answer", "")
        if value not in question["options"]:
            raise ValueError("Bitte wähle eine Antwort aus.")
        credit = float(value == question["answer"])
        submitted: Any = value
    elif category == "true_false":
        value = form.get("answer", "")
        if value not in {"true", "false"}:
            raise ValueError("Bitte entscheide dich für wahr oder falsch.")
        submitted = value == "true"
        credit = float(submitted == question["answer"])
    elif category == "estimate":
        value = form.get("answer", "").strip().replace(" ", "").replace(",", ".")
        try:
            submitted = float(value)
        except ValueError as error:
            raise ValueError("Bitte gib eine gültige Zahl ein.") from error
        if not math.isfinite(submitted) or submitted < 0:
            raise ValueError("Deine Schätzung muss eine positive Zahl sein.")
        percentage_base = 100.0 if question.get("unit") == "Jahr" else None
        raw, relative_error = estimate_points(
            submitted,
            float(question["answer"]),
            percentage_base=percentage_base,
        )
        credit = raw / 100
        return {
            "submitted": submitted,
            "credit": credit,
            "correct": submitted == float(question["answer"]),
            "delta": 0.0,
            "estimate_raw": raw,
            "accuracy_points": raw,
            "relative_error": relative_error,
        }
    elif category == "order":
        raw = form.get("answer", "")
        try:
            submitted = json.loads(raw)
        except json.JSONDecodeError as error:
            raise ValueError("Die Reihenfolge konnte nicht gelesen werden.") from error
        order_correct_count = order_correct_positions(submitted, question["answer"])
        credit = partial_credit(order_correct_count, len(question["answer"]))
    elif category == "match":
        submitted = {left: form.get(f"pair_{index}", "") for index, left in enumerate(question["left"])}
        values = list(submitted.values())
        if any(value not in question["right"] for value in values) or len(set(values)) != len(values):
            raise ValueError("Bitte ordne jedem Begriff genau ein Gegenstück zu.")
        correct_count = sum(submitted[left] == right for left, right in question["answer"].items())
        credit = partial_credit(correct_count, len(question["answer"]))
    else:  # pragma: no cover
        raise ValueError("Unbekannte Kategorie")

    accuracy_points = (
        order_question_points(order_correct_count, 1.0)
        if order_correct_count is not None
        else int(math.floor(MAX_QUESTION_POINTS * credit + 0.5))
    )
    evaluation = {
        "submitted": submitted,
        "credit": credit,
        "correct": credit == 1.0,
        "delta": 0.0,
        "estimate_raw": None,
        "accuracy_points": accuracy_points,
    }
    if order_correct_count is not None:
        evaluation["order_correct_count"] = order_correct_count
    return evaluation


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("login"))
        return view(**kwargs)

    return wrapped_view


def csrf_token() -> str:
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(24)
    return session["csrf_token"]


def require_csrf() -> None:
    token = request.form.get("csrf_token", "")
    if not token or not secrets.compare_digest(token, session.get("csrf_token", "")):
        abort(400)


def get_attempt(round_id: int) -> sqlite3.Row | None:
    return get_db().execute(
        "SELECT * FROM attempts WHERE user_id = ? AND round_id = ?",
        (g.user["id"], round_id),
    ).fetchone()


def get_party_lobby(lobby_id: int) -> sqlite3.Row | None:
    return get_db().execute(
        "SELECT * FROM party_lobbies WHERE id = ?", (lobby_id,)
    ).fetchone()


def refresh_party_lobby_state(lobby_id: int) -> sqlite3.Row | None:
    """Advance a finished start countdown without requiring a background worker."""

    lobby = get_party_lobby(lobby_id)
    if (
        lobby
        and lobby["status"] == "countdown"
        and lobby["countdown_ends_at"]
        and datetime.now() >= datetime.fromisoformat(lobby["countdown_ends_at"])
    ):
        get_db().execute(
            """
            UPDATE party_lobbies
            SET status = 'playing', question_started_at = countdown_ends_at,
                started_at = countdown_ends_at
            WHERE id = ? AND status = 'countdown'
            """,
            (lobby_id,),
        )
        get_db().commit()
        lobby = get_party_lobby(lobby_id)
    return lobby


def get_party_member(lobby_id: int, user_id: int) -> sqlite3.Row | None:
    return get_db().execute(
        "SELECT * FROM party_members WHERE lobby_id = ? AND user_id = ?",
        (lobby_id, user_id),
    ).fetchone()


def touch_party_member(lobby_id: int, user_id: int) -> None:
    """Record that a player still has this party open without writing every poll."""

    now_value = datetime.now()
    member = get_db().execute(
        """
        SELECT COALESCE(last_seen_at, joined_at) AS seen_at
        FROM party_members
        WHERE lobby_id = ? AND user_id = ? AND status = 'active'
        """,
        (lobby_id, user_id),
    ).fetchone()
    if member and now_value - datetime.fromisoformat(member["seen_at"]) >= timedelta(
        seconds=PARTY_PRESENCE_WRITE_SECONDS
    ):
        get_db().execute(
            """
            UPDATE party_members SET last_seen_at = ?
            WHERE lobby_id = ? AND user_id = ? AND status = 'active'
            """,
            (now_value.isoformat(timespec="microseconds"), lobby_id, user_id),
        )
        get_db().commit()


def refresh_party_presence(lobby_id: int | None = None) -> None:
    """Remove vanished players, transfer the host, and close empty parties."""

    database = get_db()
    now_value = datetime.now()
    now = now_value.isoformat(timespec="microseconds")
    cutoff = (
        now_value - timedelta(seconds=PARTY_PRESENCE_TIMEOUT_SECONDS)
    ).isoformat(timespec="microseconds")
    lobby_filter = " AND pl.id = ?" if lobby_id is not None else ""
    params = (lobby_id,) if lobby_id is not None else ()
    active_lobbies = database.execute(
        f"""
        SELECT pl.id, pl.host_user_id, pl.status
        FROM party_lobbies pl
        WHERE pl.status IN ('waiting', 'countdown', 'playing'){lobby_filter}
        """,
        params,
    ).fetchall()
    changed_playing: list[int] = []
    for lobby in active_lobbies:
        stale_members = database.execute(
            """
            UPDATE party_members
            SET status = 'away'
            WHERE lobby_id = ? AND status = 'active'
              AND COALESCE(last_seen_at, joined_at) < ?
            """,
            (lobby["id"], cutoff),
        ).rowcount
        members = database.execute(
            """
            SELECT * FROM party_members
            WHERE lobby_id = ? AND status = 'active'
            ORDER BY joined_at, id
            """,
            (lobby["id"],),
        ).fetchall()
        if not members:
            database.execute(
                """
                UPDATE party_lobbies
                SET status = 'abandoned', completed_at = ?
                WHERE id = ? AND status IN ('waiting', 'countdown', 'playing')
                """,
                (now, lobby["id"]),
            )
        elif not any(member["user_id"] == lobby["host_user_id"] for member in members):
            database.execute(
                "UPDATE party_lobbies SET host_user_id = ? WHERE id = ?",
                (members[0]["user_id"], lobby["id"]),
            )
        if stale_members and lobby["status"] == "playing":
            changed_playing.append(lobby["id"])
    database.commit()
    for changed_lobby_id in changed_playing:
        current = get_party_lobby(changed_lobby_id)
        if current:
            advance_party_if_ready(current)


def party_members(lobby_id: int) -> list[sqlite3.Row]:
    return get_db().execute(
        """
        SELECT pm.*, u.display_name,
               COALESCE(uc.avatar_id, ?) AS avatar_id,
               COALESCE(uc.plaque_id, ?) AS plaque_id
        FROM party_members pm JOIN users u ON u.id = pm.user_id
        LEFT JOIN user_cosmetics uc ON uc.user_id = u.id
        WHERE pm.lobby_id = ? AND pm.status = 'active'
        ORDER BY pm.joined_at, pm.id
        """,
        (DEFAULT_AVATAR_ID, DEFAULT_PLAQUE_ID, lobby_id),
    ).fetchall()


def active_party_lobbies(user_id: int) -> list[sqlite3.Row]:
    return get_db().execute(
        """
        SELECT pl.*, u.display_name AS host_name,
               COUNT(CASE WHEN pm.status = 'active' THEN 1 END) AS member_count,
               MAX(CASE WHEN pm.user_id = ? AND pm.status = 'active' THEN 1 ELSE 0 END)
                   AS is_member
        FROM party_lobbies pl
        JOIN users u ON u.id = pl.host_user_id
        LEFT JOIN party_members pm ON pm.lobby_id = pl.id
        WHERE pl.status IN ('waiting', 'countdown', 'playing')
        GROUP BY pl.id
        ORDER BY pl.created_at DESC
        """,
        (user_id,),
    ).fetchall()


def party_overview_signature(lobbies: list[sqlite3.Row]) -> str:
    return "|".join(
        f"{row['id']}:{row['status']}:{row['host_user_id']}:{row['rounds']}:"
        f"{row['member_count']}:{row['is_member']}:{row['name']}"
        for row in lobbies
    )


def advance_party_if_ready(lobby: sqlite3.Row) -> None:
    if lobby["status"] != "playing":
        return
    database = get_db()
    active_count = database.execute(
        "SELECT COUNT(*) FROM party_members WHERE lobby_id = ? AND status = 'active'",
        (lobby["id"],),
    ).fetchone()[0]
    answer_count = database.execute(
        """
        SELECT COUNT(*) FROM party_answers pa
        JOIN party_members pm ON pm.id = pa.member_id
        WHERE pa.lobby_id = ? AND pa.question_index = ? AND pm.status = 'active'
        """,
        (lobby["id"], lobby["current_question_index"]),
    ).fetchone()[0]
    if active_count == 0 or answer_count < active_count:
        return
    questions = json.loads(lobby["questions_json"])
    next_index = lobby["current_question_index"] + 1
    now_value = datetime.now()
    now = now_value.isoformat(timespec="microseconds")
    if next_index >= len(questions):
        database.execute(
            """
            UPDATE party_lobbies SET status = 'completed', current_question_index = ?,
                   question_started_at = NULL, completed_at = ? WHERE id = ?
            """,
            (next_index, now, lobby["id"]),
        )
    else:
        question_starts_at = (
            now_value
            + timedelta(
                seconds=PARTY_FEEDBACK_SECONDS + PARTY_NEXT_COUNTDOWN_SECONDS
            )
        ).isoformat(timespec="microseconds")
        database.execute(
            "UPDATE party_lobbies SET current_question_index = ?, question_started_at = ? WHERE id = ?",
            (next_index, question_starts_at, lobby["id"]),
        )
    database.commit()


def register_routes(app: Flask) -> None:
    @app.errorhandler(QuestionPoolExhausted)
    def unavailable_round(error):
        # Also handle old tabs and direct round URLs after the last reservation.
        record_pool_exhausted()
        return redirect(url_for("home"))

    @app.before_request
    def load_user() -> None:
        user_id = session.get("user_id")
        g.user = (
            get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            if user_id
            else None
        )
        if (
            g.user is not None
            and request.endpoint not in ("static", "players", "public_profile")
            and session.get("login_recorded_on") != today_iso()
        ):
            if record_daily_login(g.user["id"]):
                session["show_yesterday_winner"] = True
            session["login_recorded_on"] = today_iso()

    @app.route("/login", methods=("GET", "POST"))
    def login():
        if g.user:
            return redirect(url_for("home"))
        if request.method == "POST":
            require_csrf()
            username = normalize_username(request.form.get("username", ""))
            pin = request.form.get("pin", "")
            user = get_db().execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()
            if user is None or not check_password_hash(user["pin_hash"], pin):
                flash("Name oder PIN stimmen nicht. Noch mal mit Gefühl.", "error")
            else:
                session.clear()
                session["user_id"] = user["id"]
                session["csrf_token"] = secrets.token_urlsafe(24)
                session["show_yesterday_winner"] = record_daily_login(user["id"])
                session["login_recorded_on"] = today_iso()
                missed_days = missed_current_week_dates(user["id"])
                session["show_catchup_prompt"] = bool(missed_days)
                session["missed_week_days"] = missed_days
                return redirect(url_for("home"))
        return render_template("login.html")

    @app.route("/registrieren", methods=("GET", "POST"))
    def register():
        if g.user:
            return redirect(url_for("home"))
        if request.method == "POST":
            require_csrf()
            display_name = " ".join(request.form.get("username", "").strip().split())
            username = normalize_username(display_name)
            pin = request.form.get("pin", "")
            pin_confirm = request.form.get("pin_confirm", "")
            error = None
            if not 2 <= len(display_name) <= 24:
                error = "Dein Spielername muss 2 bis 24 Zeichen lang sein."
            elif any(ord(character) < 32 for character in display_name):
                error = "Dieser Spielername enthält ungültige Zeichen."
            elif not 4 <= len(pin) <= 32:
                error = "Deine PIN muss mindestens 4 Zeichen lang sein."
            elif pin != pin_confirm:
                error = "Die beiden PINs sind nicht identisch."
            elif get_db().execute("SELECT COUNT(*) FROM users").fetchone()[0] >= MAX_PLAYERS:
                error = f"{app.config['GAME_NAME']} ist mit 100 Spielern vollständig belegt."
            elif get_db().execute(
                "SELECT id FROM users WHERE username = ?", (username,)
            ).fetchone():
                error = "Dieser Spielername ist schon vergeben."
            if error:
                flash(error, "error")
            else:
                database = get_db()
                try:
                    cursor = database.execute(
                        """
                        INSERT INTO users (username, display_name, pin_hash, created_at)
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            username,
                            display_name,
                            generate_password_hash(pin),
                            datetime.now().isoformat(timespec="seconds"),
                        ),
                    )
                    database.commit()
                except sqlite3.IntegrityError:
                    database.rollback()
                    if database.execute("SELECT COUNT(*) FROM users").fetchone()[0] >= MAX_PLAYERS:
                        flash(
                            f"{app.config['GAME_NAME']} ist mit 100 Spielern vollständig belegt.",
                            "error",
                        )
                    else:
                        flash("Dieser Spielername ist schon vergeben.", "error")
                else:
                    session.clear()
                    session["user_id"] = cursor.lastrowid
                    session["csrf_token"] = secrets.token_urlsafe(24)
                    session["show_yesterday_winner"] = record_daily_login(
                        cursor.lastrowid
                    )
                    session["login_recorded_on"] = today_iso()
                    missed_days = missed_current_week_dates(cursor.lastrowid)
                    session["show_catchup_prompt"] = bool(missed_days)
                    session["missed_week_days"] = missed_days
                    return redirect(url_for("home"))
        return render_template("register.html")

    @app.post("/logout")
    @login_required
    def logout():
        require_csrf()
        session.clear()
        return redirect(url_for("login"))

    @app.get("/profil")
    @login_required
    def profile():
        cosmetics = player_cosmetics(g.user["id"])
        owned_avatar_ids = owned_catalog_ids(g.user["id"], "avatar")
        owned_plaque_ids = owned_catalog_ids(g.user["id"], "plaque")
        owned_background_ids = owned_catalog_ids(g.user["id"], "background")
        owned_phrase_ids = owned_catalog_ids(g.user["id"], "phrase")
        return render_template(
            "profile.html",
            cosmetics=cosmetics,
            owned_avatars=[
                item for item in [DEFAULT_AVATAR, *AVATAR_CATALOG]
                if item["id"] in owned_avatar_ids
            ],
            owned_plaques=[
                item for item in [DEFAULT_PLAQUE, *PLAQUE_CATALOG]
                if item["id"] in owned_plaque_ids
            ],
            owned_backgrounds=[
                item for item in [DEFAULT_BACKGROUND, *BACKGROUND_CATALOG]
                if item["id"] in owned_background_ids
            ],
            owned_phrases=[item for item in PHRASE_CATALOG if item["id"] in owned_phrase_ids],
            trophies=player_trophy_counts(g.user["id"]),
            total_points=player_total_points(g.user["id"]),
            is_owner=is_owner_user(g.user["id"]),
        )

    @app.post("/profil/entwickler")
    @login_required
    def profile_developer_mode():
        require_csrf()
        if not is_owner_user(g.user["id"]):
            abort(403)
        enabled = request.form.get("developer_enabled") == "1"
        cosmetics = player_cosmetics(g.user["id"])
        if not enabled:
            actually_owned = {
                item_type: (
                    ({DEFAULT_AVATAR_ID} if item_type == "avatar" else
                     {DEFAULT_PLAQUE_ID} if item_type == "plaque" else
                     {DEFAULT_BACKGROUND_ID} if item_type == "background" else
                     set())
                    | {
                        row["item_id"]
                        for row in get_db().execute(
                            "SELECT item_id FROM shop_purchases WHERE user_id = ? AND item_type = ?",
                            (g.user["id"], item_type),
                        ).fetchall()
                    }
                )
                for item_type in ("avatar", "plaque", "background", "phrase")
            }
            if cosmetics["avatar_id"] not in actually_owned["avatar"]:
                cosmetics["avatar_id"] = DEFAULT_AVATAR_ID
            if cosmetics["plaque_id"] not in actually_owned["plaque"]:
                cosmetics["plaque_id"] = DEFAULT_PLAQUE_ID
            if cosmetics["background_id"] not in actually_owned["background"]:
                cosmetics["background_id"] = DEFAULT_BACKGROUND_ID
            if cosmetics["phrase_id"] not in actually_owned["phrase"]:
                cosmetics["phrase_id"] = DEFAULT_PHRASE_ID
        get_db().execute(
            """
            INSERT INTO user_cosmetics
                (user_id, avatar_id, plaque_id, background_id, phrase_id, developer_enabled, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                avatar_id = excluded.avatar_id,
                plaque_id = excluded.plaque_id,
                background_id = excluded.background_id,
                phrase_id = excluded.phrase_id,
                developer_enabled = excluded.developer_enabled,
                updated_at = excluded.updated_at
            """,
            (
                g.user["id"], cosmetics["avatar_id"], cosmetics["plaque_id"],
                cosmetics["background_id"], cosmetics["phrase_id"], int(enabled),
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        get_db().commit()
        flash("Entwicklermodus aktiviert." if enabled else "Entwicklermodus deaktiviert.", "success")
        return redirect(url_for("profile"))

    @app.get("/shop")
    @login_required
    def shop():
        cosmetics = player_cosmetics(g.user["id"])
        return render_template(
            "shop.html",
            avatars=AVATAR_CATALOG,
            plaques=PLAQUE_CATALOG,
            backgrounds=[DEFAULT_BACKGROUND, *BACKGROUND_CATALOG],
            phrases=PHRASE_CATALOG,
            owned_avatars=owned_catalog_ids(g.user["id"], "avatar"),
            owned_plaques=owned_catalog_ids(g.user["id"], "plaque"),
            owned_backgrounds=owned_catalog_ids(g.user["id"], "background"),
            owned_phrases=owned_catalog_ids(g.user["id"], "phrase"),
            cosmetics=cosmetics,
        )

    @app.post("/shop/kaufen/<item_type>/<item_id>")
    @login_required
    def shop_buy(item_type: str, item_id: str):
        require_csrf()
        catalog = (
            AVATAR_CATALOG
            if item_type == "avatar"
            else PLAQUE_CATALOG
            if item_type == "plaque"
            else BACKGROUND_CATALOG
            if item_type == "background"
            else PHRASE_CATALOG
            if item_type == "phrase"
            else []
        )
        item = next((entry for entry in catalog if entry["id"] == item_id), None)
        if not item:
            abort(404)
        if item["price"] is None:
            flash(
                "Der Preis wird erst von Stormseed festgelegt. Dieser Artikel ist noch nicht kaufbar.",
                "error",
            )
            return redirect(
                url_for("shop", tab={"avatar": "avatars", "plaque": "plaques", "background": "backgrounds", "phrase": "phrases"}[item_type])
            )
        database = get_db()
        database.execute("BEGIN IMMEDIATE")
        if item_id in owned_catalog_ids(g.user["id"], item_type):
            database.rollback()
            flash("Dieses Stück gehört dir bereits.", "success")
            return redirect(url_for("shop"))
        if player_currency_balance(g.user["id"]) < item["price"]:
            database.rollback()
            flash("Dafür fehlen dir noch ein paar iKühe.", "error")
            return redirect(url_for("shop"))
        record_currency_peak(database, g.user['id'], player_currency_balance(g.user['id']))
        database.execute(
            """
            INSERT INTO shop_purchases (user_id, item_type, item_id, price, purchased_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                g.user["id"],
                item_type,
                item_id,
                item["price"],
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        database.commit()
        flash(f"{item['name']} gehört jetzt dir.", "success")
        return redirect(
            url_for("shop", tab={"avatar": "avatars", "plaque": "plaques", "background": "backgrounds", "phrase": "phrases"}[item_type])
        )

    @app.post("/shop/ausruesten/<item_type>/<item_id>")
    @app.post("/profil/ausruesten/<item_type>/<item_id>")
    @login_required
    def profile_equip(item_type: str, item_id: str):
        require_csrf()
        if (
            item_type not in ("avatar", "plaque", "background", "phrase")
            or item_id not in owned_catalog_ids(g.user["id"], item_type)
        ):
            abort(403)
        cosmetics = player_cosmetics(g.user["id"])
        if item_type == "avatar":
            cosmetics["avatar_id"] = item_id
        elif item_type == "plaque":
            cosmetics["plaque_id"] = item_id
        elif item_type == "background":
            cosmetics["background_id"] = item_id
        else:
            cosmetics["phrase_id"] = item_id
        get_db().execute(
            """
            INSERT INTO user_cosmetics (user_id, avatar_id, plaque_id, background_id, phrase_id, developer_enabled, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET avatar_id = excluded.avatar_id,
                plaque_id = excluded.plaque_id,
                background_id = excluded.background_id,
                phrase_id = excluded.phrase_id,
                developer_enabled = excluded.developer_enabled,
                updated_at = excluded.updated_at
            """,
            (
                g.user["id"],
                cosmetics["avatar_id"],
                cosmetics["plaque_id"],
                cosmetics["background_id"],
                cosmetics["phrase_id"],
                int(cosmetics["developer_enabled"]),
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        get_db().commit()
        return redirect(url_for("profile", section=item_type))

    @app.get("/")
    @login_required
    def home():
        should_greet_with_winner = session.pop("show_yesterday_winner", False)
        missed_days = missed_current_week_dates(g.user["id"])
        selected_round_date = session.get("active_round_date")
        if (
            selected_round_date
            and selected_round_date != today_iso()
            and selected_round_date not in missed_days
        ):
            session.pop("active_round_date", None)
            session.pop("catchup_queue", None)
        try:
            daily_round = get_or_create_round(active_round_date())
        except QuestionPoolExhausted:
            daily_round = None
        round_day = daily_round["round_date"] if daily_round else active_round_date()
        attempt = get_attempt(daily_round["id"]) if daily_round else None
        available_replays = missed_days
        if question_pool_status()["exhausted"]:
            record_pool_exhausted()
            reserved_days = {
                row["round_date"]
                for row in get_db().execute("SELECT round_date FROM daily_rounds")
            }
            available_replays = [day for day in missed_days if day in reserved_days]
        greeting_index = int(hashlib.sha256(f"{today_iso()}:{g.user['id']}".encode()).hexdigest()[:8], 16)
        return render_template(
            "home.html",
            daily_round=daily_round,
            round_available=daily_round is not None,
            attempt=attempt,
            leaderboards=leaderboard_sets(round_day),
            greeting=GREETINGS[greeting_index % len(GREETINGS)],
            default_phrase=DEFAULT_PHRASE,
            yesterday_winner=(
                previous_daily_winner() if should_greet_with_winner else None
            ),
            show_catchup_prompt=(
                session.pop("show_catchup_prompt", False) and bool(available_replays)
            ),
            missed_week_days=available_replays,
            active_round_date=round_day,
            trophies=player_trophy_counts(g.user["id"]),
        )

    @app.post("/woche/auswahl")
    @login_required
    def choose_week_replay():
        require_csrf()
        choice = request.form.get("choice")
        missed_days = missed_current_week_dates(g.user["id"])
        if question_pool_status()["exhausted"]:
            reserved_days = {
                row["round_date"]
                for row in get_db().execute("SELECT round_date FROM daily_rounds")
            }
            missed_days = [day for day in missed_days if day in reserved_days]
        queue = missed_days + [today_iso()] if choice == "all" else [today_iso()]
        session["catchup_queue"] = list(dict.fromkeys(queue))
        session["active_round_date"] = session["catchup_queue"][0]
        return redirect(url_for("home"))

    @app.post("/woche/weiter")
    @login_required
    def next_catchup_round():
        require_csrf()
        queue = session.get("catchup_queue", [])
        current = active_round_date()
        queue = [day for day in queue if day != current]
        if queue:
            session["catchup_queue"] = queue
            session["active_round_date"] = queue[0]
        else:
            session.pop("catchup_queue", None)
            session.pop("active_round_date", None)
        return redirect(url_for("home"))

    @app.post("/runde/starten")
    @login_required
    def start_round():
        require_csrf()
        daily_round = get_or_create_round(active_round_date())
        attempt = get_attempt(daily_round["id"])
        if not attempt:
            database = get_db()
            database.execute(
                """
                INSERT INTO attempts
                    (user_id, round_id, rank_before, started_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    g.user["id"],
                    daily_round["id"],
                    current_rank(g.user["id"]),
                    datetime.now().isoformat(timespec="seconds"),
                ),
            )
            database.commit()
            attempt = get_attempt(daily_round["id"])
        if attempt["status"] == "completed":
            return redirect(url_for("result"))
        return redirect(url_for("question"))

    @app.get("/runde")
    @login_required
    def question():
        daily_round = get_or_create_round(active_round_date())
        attempt = get_attempt(daily_round["id"])
        if not attempt:
            return redirect(url_for("home"))
        if attempt["status"] == "completed":
            return redirect(url_for("result"))
        questions = json.loads(daily_round["questions_json"])
        index = attempt["current_index"]
        if index >= len(questions):
            return redirect(url_for("result"))
        item = questions[index]
        previous = get_db().execute(
            "SELECT * FROM answers WHERE attempt_id = ? AND question_id = ?",
            (attempt["id"], item["id"]),
        ).fetchone()
        if item["category"] == "order" and not previous:
            seed = int(hashlib.sha256(f"{daily_round['round_date']}:{item['id']}:shuffle".encode()).hexdigest()[:8], 16)
            display_items = sorted(item["items"], key=lambda value: hashlib.sha256(f"{seed}:{value}".encode()).hexdigest())
        else:
            display_items = item.get("items", [])
        match_options = (
            match_option_order(
                item,
                f"{daily_round['round_date']}:{item['id']}:{g.user['id']}:match",
            )
            if item["category"] == "match" and not previous
            else item.get("right", [])
        )
        feedback = None
        elapsed_seconds = 0.0
        running_points = int(
            get_db()
            .execute(
                "SELECT COALESCE(SUM(points), 0) FROM answers WHERE attempt_id = ?",
                (attempt["id"],),
            )
            .fetchone()[0]
        )
        if previous:
            feedback = dict(previous)
            feedback["submitted"] = json.loads(previous["answer_json"])
            if item["category"] == "order":
                feedback["order_correct_count"] = order_correct_positions(
                    feedback["submitted"], item["answer"]
                )
            feedback_unlock_at = datetime.fromisoformat(previous["created_at"]) + timedelta(
                seconds=FEEDBACK_SECONDS
            )
            feedback_remaining_ms = max(
                0,
                math.ceil((feedback_unlock_at - datetime.now()).total_seconds() * 1000),
            )
        else:
            feedback_remaining_ms = 0
            started_at = attempt["question_started_at"]
            if not started_at:
                started_at = datetime.now().isoformat(timespec="microseconds")
                get_db().execute(
                    "UPDATE attempts SET question_started_at = ? WHERE id = ?",
                    (started_at, attempt["id"]),
                )
                get_db().commit()
            elapsed_seconds = max(
                0.0, (datetime.now() - datetime.fromisoformat(started_at)).total_seconds()
            )
        return render_template(
            "question.html",
            attempt=attempt,
            question=item,
            index=index,
            total=len(questions),
            display_items=display_items,
            match_options=match_options,
            feedback=feedback,
            category_label=CATEGORY_LABELS[item["category"]],
            knowledge_category_label=KNOWLEDGE_CATEGORY_LABELS.get(
                item.get("knowledge_category"), ""
            ),
            timer_limit=QUESTION_TIME_LIMITS[index],
            timer_decay=QUESTION_DECAY_SECONDS[index],
            timer_hold=QUESTION_FULL_TIME_SECONDS[index],
            elapsed_seconds=elapsed_seconds,
            running_points=running_points,
            feedback_remaining_ms=feedback_remaining_ms,
        )

    @app.post("/runde/antwort")
    @login_required
    def answer_question():
        require_csrf()
        daily_round = get_or_create_round(active_round_date())
        attempt = get_attempt(daily_round["id"])
        if not attempt or attempt["status"] != "playing":
            return redirect(url_for("home"))
        questions = json.loads(daily_round["questions_json"])
        index = attempt["current_index"]
        if index >= len(questions):
            return redirect(url_for("result"))
        item = questions[index]
        try:
            evaluation = evaluate(item, request.form.to_dict())
        except ValueError as error:
            flash(str(error), "error")
            return redirect(url_for("question"))
        started_at = attempt["question_started_at"]
        elapsed_seconds = (
            max(0.0, (datetime.now() - datetime.fromisoformat(started_at)).total_seconds())
            if started_at
            else 0.0
        )
        time_factor = question_time_factor(elapsed_seconds, index)
        earned_points = awarded_question_points(evaluation, time_factor)
        database = get_db()
        cursor = database.execute(
            """
            INSERT OR IGNORE INTO answers
                (attempt_id, question_id, answer_json, correct, credit,
                 multiplier_delta, time_factor, response_seconds,
                 accuracy_points, points, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                attempt["id"],
                item["id"],
                json.dumps(evaluation["submitted"], ensure_ascii=False),
                int(evaluation["correct"]),
                evaluation["credit"],
                0.0,
                time_factor,
                elapsed_seconds,
                evaluation["accuracy_points"],
                earned_points,
                datetime.now().isoformat(timespec="microseconds"),
            ),
        )
        database.commit()
        if not cursor.rowcount:
            return redirect(url_for("question"))
        return redirect(url_for("question"))

    @app.post("/runde/weiter")
    @login_required
    def next_question():
        require_csrf()
        daily_round = get_or_create_round(active_round_date())
        attempt = get_attempt(daily_round["id"])
        if not attempt or attempt["status"] != "playing":
            return redirect(url_for("home"))
        questions = json.loads(daily_round["questions_json"])
        index = attempt["current_index"]
        item = questions[index]
        answered = get_db().execute(
            "SELECT id, created_at FROM answers WHERE attempt_id = ? AND question_id = ?",
            (attempt["id"], item["id"]),
        ).fetchone()
        if not answered:
            flash("Erst antworten, dann abhauen.", "error")
            return redirect(url_for("question"))
        feedback_unlock_at = datetime.fromisoformat(answered["created_at"]) + timedelta(
            seconds=FEEDBACK_SECONDS
        )
        if datetime.now() < feedback_unlock_at:
            return redirect(url_for("question"))
        next_index = index + 1
        database = get_db()
        if next_index >= len(questions):
            score = int(
                database.execute(
                    "SELECT COALESCE(SUM(points), 0) FROM answers WHERE attempt_id = ?",
                    (attempt["id"],),
                ).fetchone()[0]
            )
            database.execute(
                """
                UPDATE attempts
                SET current_index = ?, status = 'completed', score = ?,
                    question_started_at = NULL, completed_at = ?
                WHERE id = ?
                """,
                (next_index, score, datetime.now().isoformat(timespec="seconds"), attempt["id"]),
            )
            record_currency_peak(database, g.user['id'], player_currency_balance(g.user['id']))
            database.commit()
            rank_after = current_rank(g.user["id"])
            database.execute(
                "UPDATE attempts SET rank_after = ? WHERE id = ?",
                (rank_after, attempt["id"]),
            )
            database.commit()
            return redirect(url_for("result"))
        database.execute(
            "UPDATE attempts SET current_index = ?, question_started_at = NULL WHERE id = ?",
            (next_index, attempt["id"]),
        )
        database.commit()
        return redirect(url_for("question"))

    @app.get("/ergebnis")
    @login_required
    def result():
        daily_round = get_or_create_round(active_round_date())
        attempt = get_attempt(daily_round["id"])
        if not attempt:
            return redirect(url_for("home"))
        if attempt["status"] != "completed":
            return redirect(url_for("question"))
        current_position = current_rank(g.user["id"])
        movement = int(attempt["rank_before"] or current_position) - current_position
        return render_template(
            "result.html",
            attempt=attempt,
            leaderboards=leaderboard_sets(daily_round["round_date"]),
            movement=movement,
            current_position=current_position,
            answer_review=answer_review(daily_round, attempt),
            round_date_display=date.fromisoformat(daily_round["round_date"]).strftime("%d.%m.%Y"),
            has_next_catchup=any(
                day != daily_round["round_date"]
                for day in session.get("catchup_queue", [])
            ),
        )

    @app.get("/health")
    def health():
        get_db().execute("SELECT 1").fetchone()
        return {
            "status": "ok",
            "release": app.config.get('OFFLINE_VERSION') or RELEASE_VERSION,
            "code_release": RELEASE_VERSION,
            "questions": question_pool_status(),
            "pool_mail_ready": pool_mail_ready(),
        }

    @app.get("/party")
    @login_required
    def party_index():
        refresh_party_presence()
        lobbies = active_party_lobbies(g.user["id"])
        return render_overview(
            "party_index.html",
            lobbies=lobbies,
        )

    @app.get("/party/status")
    @login_required
    def party_overview_status():
        refresh_party_presence()
        lobbies = active_party_lobbies(g.user["id"])
        return {"signature": party_overview_signature(lobbies)}

    @app.post("/party/erstellen")
    @login_required
    def party_create():
        require_csrf()
        refresh_party_presence()
        database = get_db()
        database.execute("BEGIN IMMEDIATE")
        active = database.execute(
            "SELECT COUNT(*) FROM party_lobbies WHERE status IN ('waiting', 'countdown', 'playing')"
        ).fetchone()[0]
        if active >= 2:
            database.rollback()
            flash("Es können höchstens zwei Partys gleichzeitig laufen.", "error")
            return redirect(url_for("party_index"))
        own = database.execute(
            """
            SELECT pl.id FROM party_lobbies pl JOIN party_members pm ON pm.lobby_id = pl.id
            WHERE pm.user_id = ? AND pm.status = 'active' AND pl.status IN ('waiting', 'countdown', 'playing')
            """,
            (g.user["id"],),
        ).fetchone()
        if own:
            database.rollback()
            return redirect(url_for("party_lobby", lobby_id=own["id"]))
        now = datetime.now().isoformat(timespec="seconds")
        lobby_id = database.execute(
            """
            INSERT INTO party_lobbies (name, host_user_id, created_at)
            VALUES (?, ?, ?)
            """,
            (f"{g.user['display_name']}s Party", g.user["id"], now),
        ).lastrowid
        database.execute(
            """
            INSERT INTO party_members (lobby_id, user_id, joined_at, last_seen_at)
            VALUES (?, ?, ?, ?)
            """,
            (lobby_id, g.user["id"], now, now),
        )
        database.commit()
        return redirect(url_for("party_lobby", lobby_id=lobby_id))

    @app.post("/party/<int:lobby_id>/beitreten")
    @login_required
    def party_join(lobby_id: int):
        require_csrf()
        refresh_party_presence(lobby_id)
        database = get_db()
        database.execute("BEGIN IMMEDIATE")
        lobby = get_party_lobby(lobby_id)
        own = database.execute(
            """
            SELECT pl.id FROM party_lobbies pl
            JOIN party_members pm ON pm.lobby_id = pl.id
            WHERE pm.user_id = ? AND pm.status = 'active'
              AND pl.status IN ('waiting', 'countdown', 'playing') AND pl.id != ?
            """,
            (g.user["id"], lobby_id),
        ).fetchone()
        count = database.execute(
            "SELECT COUNT(*) FROM party_members WHERE lobby_id = ? AND status = 'active'",
            (lobby_id,),
        ).fetchone()[0]
        if own:
            database.rollback()
            flash("Du bist bereits in einer anderen laufenden Party.", "error")
            return redirect(url_for("party_lobby", lobby_id=own["id"]))
        if not lobby or lobby["status"] != "waiting" or count >= 10:
            database.rollback()
            flash("Dieser Party kannst du gerade nicht beitreten.", "error")
            return redirect(url_for("party_index"))
        existing = get_party_member(lobby_id, g.user["id"])
        now = datetime.now().isoformat(timespec="microseconds")
        if existing:
            database.execute(
                "UPDATE party_members SET status = 'active', last_seen_at = ? WHERE id = ?",
                (now, existing["id"]),
            )
        else:
            database.execute(
                """
                INSERT INTO party_members (lobby_id, user_id, joined_at, last_seen_at)
                VALUES (?, ?, ?, ?)
                """,
                (lobby_id, g.user["id"], now, now),
            )
        database.commit()
        return redirect(url_for("party_lobby", lobby_id=lobby_id))

    @app.post("/party/<int:lobby_id>/einstellungen")
    @login_required
    def party_settings(lobby_id: int):
        require_csrf()
        touch_party_member(lobby_id, g.user["id"])
        refresh_party_presence(lobby_id)
        lobby = get_party_lobby(lobby_id)
        if not lobby or lobby["host_user_id"] != g.user["id"] or lobby["status"] != "waiting":
            abort(403)
        try:
            rounds = max(1, min(5, int(request.form.get("rounds", "1"))))
        except ValueError:
            rounds = 1
        name = " ".join(request.form.get("name", "").strip().split())[:36] or lobby["name"]
        get_db().execute(
            "UPDATE party_lobbies SET rounds = ?, name = ? WHERE id = ?",
            (rounds, name, lobby_id),
        )
        get_db().commit()
        return redirect(url_for("party_lobby", lobby_id=lobby_id))

    @app.post("/party/<int:lobby_id>/starten")
    @login_required
    def party_start(lobby_id: int):
        require_csrf()
        touch_party_member(lobby_id, g.user["id"])
        refresh_party_presence(lobby_id)
        database = get_db()
        database.execute("BEGIN IMMEDIATE")
        lobby = get_party_lobby(lobby_id)
        if not lobby or lobby["host_user_id"] != g.user["id"] or lobby["status"] != "waiting":
            database.rollback()
            abort(403)
        try:
            rounds = max(
                1, min(5, int(request.form.get("rounds", lobby["rounds"])))
            )
        except (TypeError, ValueError):
            rounds = lobby["rounds"]
        name = (
            " ".join(request.form.get("name", lobby["name"]).strip().split())[:36]
            or lobby["name"]
        )
        database.execute(
            "UPDATE party_lobbies SET rounds = ?, name = ? WHERE id = ?",
            (rounds, name, lobby_id),
        )
        try:
            question_sets = reserve_question_sets(
                "party", str(lobby_id), rounds, manage_transaction=False
            )
        except QuestionPoolExhausted as error:
            database.rollback()
            if question_pool_status()["exhausted"]:
                record_pool_exhausted()
            flash(str(error), "error")
            return redirect(url_for("party_lobby", lobby_id=lobby_id))
        questions = [question for question_set in question_sets for question in question_set]
        now_value = datetime.now()
        countdown_ends_at = (
            now_value + timedelta(seconds=PARTY_START_COUNTDOWN_SECONDS)
        ).isoformat(timespec="microseconds")
        database.execute(
            """
            UPDATE party_lobbies SET status = 'countdown', questions_json = ?,
                   current_question_index = 0, question_started_at = NULL,
                   countdown_ends_at = ?, started_at = NULL
            WHERE id = ?
            """,
            (json.dumps(questions, ensure_ascii=False), countdown_ends_at, lobby_id),
        )
        database.commit()
        if question_pool_status()["exhausted"]:
            record_pool_exhausted()
        return redirect(url_for("party_lobby", lobby_id=lobby_id))

    @app.get("/party/<int:lobby_id>")
    @login_required
    def party_lobby(lobby_id: int):
        member = get_party_member(lobby_id, g.user["id"])
        if member and member["status"] == "active":
            touch_party_member(lobby_id, g.user["id"])
        refresh_party_presence(lobby_id)
        lobby = refresh_party_lobby_state(lobby_id)
        member = get_party_member(lobby_id, g.user["id"])
        if not lobby or not member or member["status"] != "active":
            return redirect(url_for("party_index"))
        members = party_members(lobby_id)
        if lobby["status"] == "waiting":
            return render_template("party_lobby.html", lobby=lobby, members=members,
                                   lobby_players=lobby_player_profiles(members))
        if lobby["status"] == "countdown":
            remaining_ms = max(
                0,
                round(
                    (
                        datetime.fromisoformat(lobby["countdown_ends_at"])
                        - datetime.now()
                    ).total_seconds()
                    * 1000
                ),
            )
            return render_template(
                "party_countdown.html",
                lobby=lobby,
                remaining_ms=remaining_ms,
                visual_seconds=PARTY_START_COUNTDOWN_SECONDS,
                headline="Die Party startet",
                detail="Alle bereit? Gleich geht’s gleichzeitig los.",
            )
        requested_feedback = request.args.get("feedback", type=int)
        if lobby["status"] == "completed" and requested_feedback is None:
            return render_template("party_result.html", lobby=lobby, members=members)

        questions = json.loads(lobby["questions_json"])
        index = requested_feedback if requested_feedback is not None else lobby["current_question_index"]
        index = max(0, min(index, len(questions) - 1))
        question = questions[index]
        answer = get_db().execute(
            "SELECT * FROM party_answers WHERE member_id = ? AND question_index = ?",
            (member["id"], index),
        ).fetchone()
        feedback = None
        if answer:
            feedback = dict(answer)
            feedback["submitted"] = json.loads(answer["answer_json"])
            if question["category"] == "order":
                feedback["order_correct_count"] = order_correct_positions(
                    feedback["submitted"], question["answer"]
                )
            feedback["submitted_display"] = format_answer(
                question, feedback["submitted"]
            )
            feedback["correct_display"] = format_answer(question, question["answer"])
            if question["category"] == "estimate":
                feedback["difference_display"] = format_answer(
                    question,
                    abs(float(feedback["submitted"]) - float(question["answer"])),
                )
        if lobby["status"] == "completed" and feedback is None:
            return render_template("party_result.html", lobby=lobby, members=members)
        if (
            requested_feedback is None
            and index == lobby["current_question_index"]
            and lobby["question_started_at"]
            and datetime.now() < datetime.fromisoformat(lobby["question_started_at"])
        ):
            remaining_ms = max(
                0,
                round(
                    (
                        datetime.fromisoformat(lobby["question_started_at"])
                        - datetime.now()
                    ).total_seconds()
                    * 1000
                ),
            )
            return render_template(
                "party_countdown.html",
                lobby=lobby,
                remaining_ms=remaining_ms,
                visual_seconds=PARTY_NEXT_COUNTDOWN_SECONDS,
                headline="Nächste Frage",
                detail="Kurz Luft holen …",
            )
        seed = f"party:{lobby_id}:{index}:{question['id']}"
        display_items = sorted(
            question.get("items", []),
            key=lambda value: hashlib.sha256(f"{seed}:{value}".encode()).hexdigest(),
        )
        match_options = match_option_order(question, seed) if question["category"] == "match" else []
        elapsed = max(
            0.0,
            (datetime.now() - datetime.fromisoformat(lobby["question_started_at"])).total_seconds(),
        ) if lobby["question_started_at"] and index == lobby["current_question_index"] else 0.0
        return render_template(
            "party_question.html", lobby=lobby, member=member, members=members,
            question=question, index=index, total=len(questions), feedback=feedback,
            display_items=display_items, match_options=match_options,
            category_label=CATEGORY_LABELS[question["category"]],
            knowledge_category_label=KNOWLEDGE_CATEGORY_LABELS.get(
                question.get("knowledge_category"), ""
            ),
            timer_limit=QUESTION_TIME_LIMITS[index % 5], timer_decay=QUESTION_DECAY_SECONDS[index % 5],
            timer_hold=QUESTION_FULL_TIME_SECONDS[index % 5], elapsed_seconds=elapsed,
            waiting=bool(answer and index == lobby["current_question_index"]),
            historical_feedback=requested_feedback is not None and index < lobby["current_question_index"],
            party_status_url=url_for("party_status", lobby_id=lobby_id),
            feedback_seconds=(
                PARTY_FINAL_FEEDBACK_SECONDS
                if lobby["status"] == "completed"
                else PARTY_FEEDBACK_SECONDS
            ),
            next_countdown_seconds=PARTY_NEXT_COUNTDOWN_SECONDS,
            party_completed=lobby["status"] == "completed",
            final_feedback_seconds=PARTY_FINAL_FEEDBACK_SECONDS,
        )

    @app.get("/party/<int:lobby_id>/status")
    @login_required
    def party_status(lobby_id: int):
        member = get_party_member(lobby_id, g.user["id"])
        if member and member["status"] == "active":
            touch_party_member(lobby_id, g.user["id"])
        refresh_party_presence(lobby_id)
        lobby = refresh_party_lobby_state(lobby_id)
        member = get_party_member(lobby_id, g.user["id"])
        if not lobby or not member or member["status"] != "active":
            return {"status": "unavailable"}, 404
        members = party_members(lobby_id)
        question_starts_in_ms = (
            max(
                0,
                round(
                    (
                        datetime.fromisoformat(lobby["question_started_at"])
                        - datetime.now()
                    ).total_seconds()
                    * 1000
                ),
            )
            if lobby["question_started_at"]
            else None
        )
        completion_feedback_remaining_ms = (
            max(
                0,
                round(
                    (
                        PARTY_FINAL_FEEDBACK_SECONDS
                        - (
                            datetime.now()
                            - datetime.fromisoformat(lobby["completed_at"])
                        ).total_seconds()
                    )
                    * 1000
                ),
            )
            if lobby["completed_at"]
            else None
        )
        return {
            "status": lobby["status"],
            "name": lobby["name"],
            "rounds": lobby["rounds"],
            "host_user_id": lobby["host_user_id"],
            "current_question_index": lobby["current_question_index"],
            "question_started_at": lobby["question_started_at"],
            "question_starts_in_ms": question_starts_in_ms,
            "countdown_ends_at": lobby["countdown_ends_at"],
            "completion_feedback_remaining_ms": completion_feedback_remaining_ms,
            "members": [
                {"id": row["id"], "name": row["display_name"]} for row in members
            ],
        }

    @app.post("/party/<int:lobby_id>/antwort")
    @login_required
    def party_answer(lobby_id: int):
        require_csrf()
        touch_party_member(lobby_id, g.user["id"])
        refresh_party_presence(lobby_id)
        lobby = get_party_lobby(lobby_id)
        member = get_party_member(lobby_id, g.user["id"])
        if not lobby or lobby["status"] != "playing" or not member or member["status"] != "active":
            return redirect(url_for("party_index"))
        if (
            lobby["question_started_at"]
            and datetime.now() < datetime.fromisoformat(lobby["question_started_at"])
        ):
            return redirect(url_for("party_lobby", lobby_id=lobby_id))
        index = lobby["current_question_index"]
        question = json.loads(lobby["questions_json"])[index]
        try:
            evaluation = evaluate(question, request.form.to_dict())
        except ValueError as error:
            flash(str(error), "error")
            return redirect(url_for("party_lobby", lobby_id=lobby_id))
        elapsed = max(0.0, (datetime.now() - datetime.fromisoformat(lobby["question_started_at"])).total_seconds())
        time_factor = question_time_factor(elapsed, index % 5)
        points = awarded_question_points(evaluation, time_factor)
        database = get_db()
        cursor = database.execute(
            """
            INSERT OR IGNORE INTO party_answers
                (lobby_id, member_id, question_index, question_id, answer_json, correct,
                 credit, response_seconds, accuracy_points, points, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (lobby_id, member["id"], index, question["id"],
             json.dumps(evaluation["submitted"], ensure_ascii=False), int(evaluation["correct"]),
             evaluation["credit"], elapsed, evaluation["accuracy_points"], points,
             datetime.now().isoformat(timespec="seconds")),
        )
        if not cursor.rowcount:
            database.rollback()
            return redirect(url_for("party_lobby", lobby_id=lobby_id, feedback=index))
        database.execute(
            "UPDATE party_members SET score = score + ? WHERE id = ?", (points, member["id"])
        )
        database.commit()
        advance_party_if_ready(get_party_lobby(lobby_id))
        return redirect(url_for("party_lobby", lobby_id=lobby_id, feedback=index))

    @app.post("/party/<int:lobby_id>/verlassen")
    @login_required
    def party_leave(lobby_id: int):
        require_csrf()
        database = get_db()
        lobby = get_party_lobby(lobby_id)
        member = get_party_member(lobby_id, g.user["id"])
        if (
            not lobby
            or lobby["status"] not in ("waiting", "countdown", "playing")
            or not member
            or member["status"] != "active"
        ):
            return redirect(url_for("party_index"))
        database.execute(
            "UPDATE party_members SET status = 'left' WHERE id = ?", (member["id"],)
        )
        remaining = database.execute(
            """
            SELECT * FROM party_members
            WHERE lobby_id = ? AND status = 'active'
            ORDER BY joined_at, id
            """,
            (lobby_id,),
        ).fetchall()
        if not remaining:
            database.execute(
                """
                UPDATE party_lobbies SET status = 'abandoned', completed_at = ?
                WHERE id = ?
                """,
                (datetime.now().isoformat(timespec="microseconds"), lobby_id),
            )
        elif lobby["host_user_id"] == g.user["id"]:
            database.execute(
                "UPDATE party_lobbies SET host_user_id = ? WHERE id = ?",
                (remaining[0]["user_id"], lobby_id),
            )
        database.commit()
        current = get_party_lobby(lobby_id)
        if current:
            advance_party_if_ready(current)
        flash("Du hast die Party verlassen.", "success")
        return redirect(url_for("party_index"))

    @app.post("/party/<int:lobby_id>/mitglied/<int:member_id>/entfernen")
    @login_required
    def party_remove_member(lobby_id: int, member_id: int):
        require_csrf()
        touch_party_member(lobby_id, g.user["id"])
        refresh_party_presence(lobby_id)
        lobby = get_party_lobby(lobby_id)
        if not lobby or lobby["host_user_id"] != g.user["id"]:
            abort(403)
        member = get_db().execute(
            "SELECT * FROM party_members WHERE id = ? AND lobby_id = ?", (member_id, lobby_id)
        ).fetchone()
        if not member or member["user_id"] == lobby["host_user_id"]:
            abort(400)
        get_db().execute("UPDATE party_members SET status = 'removed' WHERE id = ?", (member_id,))
        get_db().commit()
        advance_party_if_ready(get_party_lobby(lobby_id))
        return redirect(url_for("party_lobby", lobby_id=lobby_id))


def register_template_helpers(app: Flask) -> None:
    from player_portrait import register_portraits
    register_portraits(app, [DEFAULT_AVATAR, *AVATAR_CATALOG])

    @app.context_processor
    def inject_globals():
        user = getattr(g, "user", None)
        public_url = app.config.get("PUBLIC_URL") or request.url_root.rstrip("/")
        cosmetics = player_cosmetics(user["id"]) if user else None
        phrase_lookup = {item["id"]: item for item in PHRASE_CATALOG}
        return {
            "csrf_token": csrf_token,
            "game_name": app.config["GAME_NAME"],
            "today_display": date.today().strftime("%d.%m.%Y"),
            "today_iso_value": today_iso(),
            "currency_balance": player_currency_balance(user["id"]) if user else 0,
            "default_phrase": DEFAULT_PHRASE,
            "equipped_phrase": phrase_lookup.get(cosmetics["phrase_id"], {}).get("text", DEFAULT_PHRASE) if cosmetics else DEFAULT_PHRASE,
            "player_cosmetics": cosmetics,
            "avatar_catalog": {
                DEFAULT_AVATAR_ID: DEFAULT_AVATAR,
                **{item["id"]: item for item in AVATAR_CATALOG},
            },
            "plaque_catalog": {
                DEFAULT_PLAQUE_ID: DEFAULT_PLAQUE,
                **{item["id"]: item for item in PLAQUE_CATALOG},
            },
            "background_catalog": {
                DEFAULT_BACKGROUND_ID: DEFAULT_BACKGROUND,
                **{item["id"]: item for item in BACKGROUND_CATALOG},
            },
            "phrase_catalog": phrase_lookup,
            "public_url": public_url,
            "share_image_url": f"{public_url}/static/guesstimate-share.jpg",
        }

    @app.template_filter("points")
    def points_filter(value: int | None) -> str:
        return f"{int(value or 0):,}".replace(",", ".")


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=True)
