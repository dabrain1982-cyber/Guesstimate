"""Render the user's red/green 160x90 blueprint as a real wood Setzkasten."""

from __future__ import annotations

from math import floor
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps

import render_perfect_setzkasten_preview as profile_renderer


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "offline-preview/perfect-setzkasten-test/setzkasten-modern-background-rebuilt-v1.png"
OUT = ROOT / "offline-preview/perfect-setzkasten-blueprint-v1"
W, H = 1920, 1080

# The blueprint is 160x90 units. These scales deliberately distort the whole
# cabinet before styling it: 20*x-scale by 30*y-scale becomes exactly 215x285,
# and 215:285 equals the canonical profile ratio 43:57.
OX, OY = 100, 112
SX, SY = 10.75, 9.5
PROFILE_SIZE = (215, 285)

WHITE_SLOTS = ((10, 60, 30, 90), (0, 10, 20, 40), (140, 60, 160, 90), (130, 0, 150, 30))
GREEN_SLOTS = ((20, 20, 40, 50), (120, 40, 140, 70))
PARCHMENT = (40, 10, 120, 80)


def px(x: float) -> int:
    return floor(OX + x * SX)


def py(y: float) -> int:
    return floor(OY + (90 - y) * SY)


def unit_rect(rect):
    x1, y1, x2, y2 = rect
    return px(x1), py(y2), px(x2), py(y1)


def wood_strip(source: Image.Image, size, vertical=False):
    raw = source.crop((410, 43, 1240, 88)).convert("L")
    raw = ImageOps.colorize(raw, black=(7, 24, 26), white=(61, 126, 120)).convert("RGBA")
    if vertical:
        raw = raw.rotate(90, expand=True)
    return raw.resize(size, Image.Resampling.LANCZOS)


def hbeam(canvas, source, x1, x2, y, thickness=14):
    left, right, center = px(x1), px(x2), py(y)
    top = center - thickness // 2
    canvas.alpha_composite(wood_strip(source, (right-left, thickness)), (left, top))
    d = ImageDraw.Draw(canvas)
    d.line((left, top, right, top), fill=(76, 142, 133), width=2)
    d.line((left, top+thickness-2, right, top+thickness-2), fill=(21, 8, 5), width=3)


def vbeam(canvas, source, x, y1, y2, thickness=14):
    center, top, bottom = px(x), py(y2), py(y1)
    left = center - thickness // 2
    canvas.alpha_composite(wood_strip(source, (thickness, bottom-top), True), (left, top))
    d = ImageDraw.Draw(canvas)
    d.line((left, top, left, bottom), fill=(70, 132, 126), width=2)
    d.line((left+thickness-2, top, left+thickness-2, bottom), fill=(20, 8, 5), width=3)


def opening_shadow(canvas, rect):
    x1, y1, x2, y2 = rect
    shade = Image.new("RGBA", canvas.size)
    d = ImageDraw.Draw(shade)
    d.rectangle((x1, y1, x1+9, y2), fill=(0, 0, 0, 125))
    d.rectangle((x1, y1, x2, y1+10), fill=(0, 0, 0, 140))
    canvas.alpha_composite(shade.filter(ImageFilter.GaussianBlur(4)))


def draw_slot_boundary(canvas, source, rect):
    x1, y1, x2, y2 = rect
    hbeam(canvas, source, x1, x2, y1)
    hbeam(canvas, source, x1, x2, y2)
    vbeam(canvas, source, x1, y1, y2)
    vbeam(canvas, source, x2, y1, y2)


def base_profiles():
    return list(profile_renderer.PLAYERS)


def extra_profiles():
    profile_renderer.PULT_FIELDS.update({
        "p03": ((.3166, .3829, .6916, .5029), (.3241, .6829, .6841, .8029)),
        "p08": ((.2875, .4573, .7297, .5836), (.3033, .7371, .7139, .8634)),
    })
    return [
        {
            "name": "Nika", "score": "350 Punkte", "phrase": "Ich bluffe beruflich.",
            "background": "background-gameshow-arena-v1.png", "plaque": "p03.webp",
            "avatar": "a05-waschbaer.webp", "podium": "p03-arena-console-tall-v3.png", "pult": "p03",
        },
        {
            "name": "Ben", "score": "250 Punkte", "phrase": "Das klingt völlig echt.",
            "background": "background-papierlandschaft-v1.png", "plaque": "p08.webp",
            "avatar": "a13-axolotl.webp", "podium": "p08-emaille-tall-v2.png", "pult": "p08",
        },
    ]


def paste_prop(canvas, source, crop, target_units):
    x1, y1, x2, y2 = unit_rect(target_units)
    prop = source.crop(crop).convert("RGBA")
    prop.thumbnail((x2-x1-10, y2-y1-10), Image.Resampling.LANCZOS)
    canvas.alpha_composite(prop, (x1+(x2-x1-prop.width)//2, y1+(y2-y1-prop.height)//2))


def build(player_count: int):
    source = Image.open(SOURCE).convert("RGBA")
    wall = source.resize((W, H), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(2))
    canvas = wall.copy()
    canvas.alpha_composite(Image.new("RGBA", canvas.size, (10, 6, 4, 45)))

    outer = unit_rect((0, 0, 160, 90))
    ImageDraw.Draw(canvas).rectangle(outer, fill=(12, 42, 43, 255), outline=(25, 10, 6), width=8)

    # Red blueprint lines, now real wood. Segments deliberately vary like the supplied drawing.
    horizontal = [
        (0, 160, 0), (0, 160, 90),
        (0, 10, 70), (0, 40, 60), (20, 40, 50), (20, 40, 45),
        (0, 20, 40), (20, 40, 30), (20, 40, 20), (0, 40, 10),
        (40, 120, 80), (40, 120, 10),
        (120, 140, 70), (120, 160, 60), (140, 160, 50),
        (120, 140, 40), (130, 160, 30), (150, 160, 20), (120, 160, 10),
    ]
    vertical = [
        (0, 0, 90), (160, 0, 90),
        (10, 60, 90), (20, 0, 60), (30, 60, 90), (30, 40, 60), (40, 0, 90),
        (50, 0, 10), (60, 0, 10), (60, 80, 90), (80, 0, 10), (90, 80, 90), (110, 0, 10),
        (120, 0, 90), (130, 0, 30), (130, 30, 40), (140, 60, 90),
        (140, 40, 60), (150, 0, 30), (150, 30, 60),
    ]
    for x1, x2, y in horizontal:
        hbeam(canvas, source, x1, x2, y)
    for x, y1, y2 in vertical:
        vbeam(canvas, source, x, y1, y2)

    # In four-player mode the two green areas remain ordinary varied compartments.
    if player_count == 4:
        hbeam(canvas, source, 20, 40, 35)
        vbeam(canvas, source, 31, 20, 50)
        hbeam(canvas, source, 120, 140, 55)
        vbeam(canvas, source, 130, 40, 70)

    # Parchment replaces the full central back wall; it is never laid over internal shelves.
    parchment_px = unit_rect(PARCHMENT)
    parchment = source.crop((522, 244, 1151, 679)).resize(
        (parchment_px[2]-parchment_px[0], parchment_px[3]-parchment_px[1]), Image.Resampling.LANCZOS
    )
    canvas.alpha_composite(parchment, (parchment_px[0], parchment_px[1]))
    draw_slot_boundary(canvas, source, PARCHMENT)
    opening_shadow(canvas, parchment_px)

    player_specs = base_profiles() + (extra_profiles() if player_count == 6 else [])
    player_slots = list(WHITE_SLOTS) + (list(GREEN_SLOTS) if player_count == 6 else [])
    for spec, slot in zip(player_specs, player_slots):
        box = unit_rect(slot)
        assert (box[2]-box[0], box[3]-box[1]) == PROFILE_SIZE
        profile = profile_renderer.render_profile(spec).resize(PROFILE_SIZE, Image.Resampling.LANCZOS)
        canvas.alpha_composite(profile, (box[0], box[1]))
        draw_slot_boundary(canvas, source, slot)
        opening_shadow(canvas, box)

    # A minority of ordinary cubbies receive the modern game props.
    paste_prop(canvas, source, (78, 86, 184, 222), (0, 70, 10, 90))
    paste_prop(canvas, source, (72, 253, 190, 371), (0, 50, 10, 70))
    paste_prop(canvas, source, (72, 395, 176, 474), (0, 40, 10, 50))
    paste_prop(canvas, source, (611, 128, 722, 240), (50, 80, 60, 90))
    paste_prop(canvas, source, (724, 145, 858, 239), (60, 80, 90, 90))
    paste_prop(canvas, source, (960, 120, 1072, 239), (90, 80, 110, 90))
    paste_prop(canvas, source, (1080, 165, 1184, 239), (110, 80, 120, 90))
    paste_prop(canvas, source, (1510, 155, 1607, 261), (150, 50, 160, 60))

    profile_renderer.draw_game_ui(canvas, parchment_px, True)
    d = ImageDraw.Draw(canvas)
    header = (px(63), py(89), px(97), py(85))
    d.rounded_rectangle(header, 16, fill=(15, 46, 48, 238), outline=(222, 168, 72), width=2)
    profile_renderer.centered(d, header, f"Jans Runde  ·  Runde 4  ·  {player_count} Spieler", profile_renderer.font(13, True), (255, 238, 188))

    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / f"stormseeds-perfect-setzkasten-{player_count}-spieler.png"
    canvas.convert("RGB").save(target, quality=96)
    print(target)


if __name__ == "__main__":
    build(4)
    build(6)
