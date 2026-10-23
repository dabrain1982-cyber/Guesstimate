"""Build the selected Perfect screen from a deterministic Setzkasten geometry."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps

from render_perfect_setzkasten_preview import PLAYERS, draw_game_ui, render_profile


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "offline-preview/perfect-setzkasten-test/setzkasten-modern-background-rebuilt-v1.png"
OUT = ROOT / "offline-preview/perfect-setzkasten-precise-v1"
WIDTH, HEIGHT = 1672, 941
PROFILE_W, PROFILE_H = 258, 342  # exact 43:57

PLAYER_WINDOWS = (
    (155, 78, PROFILE_W, PROFILE_H),
    (230, 442, PROFILE_W, PROFILE_H),
    (1259, 78, PROFILE_W, PROFILE_H),
    (1184, 442, PROFILE_W, PROFILE_H),
)


def texture(source: Image.Image, box, tint=((7, 24, 27), (61, 127, 123))):
    x1, y1, x2, y2 = box
    crop = source.crop((420, 43, 1240, 88)).convert("L")
    colored = ImageOps.colorize(crop, black=tint[0], white=tint[1]).convert("RGBA")
    return colored.resize((x2-x1, y2-y1), Image.Resampling.LANCZOS)


def beam(canvas: Image.Image, source: Image.Image, box, vertical=False):
    x1, y1, x2, y2 = box
    strip = source.crop((410, 43, 1240, 88)).convert("L")
    strip = ImageOps.colorize(strip, black=(6, 22, 24), white=(62, 126, 121)).convert("RGBA")
    if vertical:
        strip = strip.rotate(90, expand=True)
    strip = strip.resize((x2-x1, y2-y1), Image.Resampling.LANCZOS)
    canvas.alpha_composite(strip, (x1, y1))
    d = ImageDraw.Draw(canvas)
    d.line((x1, y1, x2-1, y1), fill=(83, 145, 137), width=2)
    d.line((x1, y1, x1, y2-1), fill=(65, 119, 116), width=2)
    d.line((x1, y2-2, x2-1, y2-2), fill=(19, 8, 5), width=3)
    d.line((x2-2, y1, x2-2, y2-1), fill=(17, 8, 5), width=3)


def cubby(canvas: Image.Image, source: Image.Image, box, tone=0):
    x1, y1, x2, y2 = box
    d = ImageDraw.Draw(canvas)
    palette = ((10, 34, 37), (13, 43, 45), (19, 48, 46))
    d.rectangle(box, fill=palette[tone % len(palette)])
    for offset in range(6, max(7, y2-y1), 19):
        d.line((x1+5, y1+offset, x2-5, y1+offset), fill=(21, 58, 57), width=1)
    d.rectangle((x1, y1, x2, y2), outline=(3, 15, 17), width=5)
    d.line((x1+4, y1+4, x2-4, y1+4), fill=(0, 0, 0, 110), width=5)
    d.line((x1+4, y1+4, x1+4, y2-4), fill=(0, 0, 0, 100), width=5)


def paste_prop(canvas: Image.Image, source: Image.Image, crop, target):
    prop = source.crop(crop).convert("RGBA")
    prop.thumbnail((target[2], target[3]), Image.Resampling.LANCZOS)
    canvas.alpha_composite(prop, (target[0] + (target[2]-prop.width)//2, target[1] + (target[3]-prop.height)//2))


def install_player_window(canvas: Image.Image, source: Image.Image, profile: Image.Image, box):
    x, y, w, h = box
    assert (w, h) == (PROFILE_W, PROFILE_H)
    assert w * 57 == h * 43
    canvas.alpha_composite(profile.resize((w, h), Image.Resampling.LANCZOS), (x, y))

    # These four strips are cabinet walls. They sit outside the opening and
    # connect directly to the neighboring cubbies; there is no card wrapper.
    rail = 13
    beam(canvas, source, (x-rail, y-rail, x+w+rail, y), False)
    beam(canvas, source, (x-rail, y+h, x+w+rail, y+h+rail), False)
    beam(canvas, source, (x-rail, y, x, y+h), True)
    beam(canvas, source, (x+w, y, x+w+rail, y+h), True)

    inner = Image.new("RGBA", canvas.size)
    di = ImageDraw.Draw(inner)
    di.rectangle((x, y, x+9, y+h), fill=(0, 0, 0, 120))
    di.rectangle((x, y, x+w, y+10), fill=(0, 0, 0, 135))
    inner = inner.filter(ImageFilter.GaussianBlur(5))
    canvas.alpha_composite(inner)


def build():
    source = Image.open(SOURCE).convert("RGBA")
    # Timber wall is retained as material context, but the complete cabinet is
    # newly drawn over it from explicit coordinates.
    wall = source.filter(ImageFilter.GaussianBlur(2))
    canvas = wall.copy()
    canvas.alpha_composite(Image.new("RGBA", canvas.size, (12, 7, 4, 42)))

    d = ImageDraw.Draw(canvas)
    d.rectangle((42, 34, 1630, 899), fill=(13, 42, 43, 255), outline=(28, 12, 7), width=7)

    # Every small compartment is explicitly outside the four player windows.
    cubbies = [
        # Irregular left outer tower.
        (63, 60, 142, 181), (63, 194, 142, 318), (63, 331, 142, 431),
        (63, 444, 142, 602), (63, 615, 142, 732), (63, 745, 142, 870),
        # Narrow but usable compartments beside the shifted lower portrait.
        (155, 442, 217, 556), (155, 569, 217, 691), (155, 704, 217, 784),
        # Proper compartments under the lower-left portrait; no slit remains.
        (155, 797, 270, 870), (283, 797, 386, 870), (399, 797, 488, 870),

        # Irregular upper composition: tall compartments alternate with split stacks.
        (426, 60, 545, 228),
        (558, 60, 690, 132), (558, 145, 620, 228), (633, 145, 690, 228),
        (703, 60, 850, 178), (703, 191, 772, 228), (785, 191, 850, 228),
        (863, 60, 1000, 132), (863, 145, 932, 228), (945, 145, 1000, 228),
        (1013, 60, 1140, 181), (1013, 194, 1077, 228), (1090, 194, 1140, 228),
        (1153, 60, 1246, 228),
        # Side pockets end cleanly at the large openings and parchment.
        (426, 244, 492, 326), (426, 339, 492, 420),
        (1180, 244, 1246, 326), (1180, 339, 1246, 420),

        # Organic lower middle: every vertical group breaks at another height.
        (505, 703, 620, 870),
        (633, 703, 760, 770), (633, 783, 700, 870), (713, 783, 760, 870),
        (773, 703, 910, 815), (773, 828, 835, 870), (848, 828, 910, 870),
        (923, 703, 1040, 760), (923, 773, 1040, 870),
        (1053, 703, 1167, 825), (1053, 838, 1105, 870), (1118, 838, 1167, 870),

        # Right side uses a different rhythm instead of mirroring the left.
        (1530, 60, 1609, 205), (1530, 218, 1609, 350),
        (1530, 363, 1609, 486), (1530, 499, 1609, 645),
        (1530, 658, 1609, 770), (1530, 783, 1609, 870),
        (1455, 442, 1517, 548), (1455, 561, 1517, 673), (1455, 686, 1517, 784),
        # Proper compartments under the lower-right portrait.
        (1184, 797, 1283, 870), (1296, 797, 1401, 870), (1414, 797, 1517, 870),
    ]
    for idx, box in enumerate(cubbies):
        cubby(canvas, source, box, idx)

    # Central parchment is also bounded by real cabinet walls.
    parchment_box = (505, 244, 1167, 690)
    parchment_crop = source.crop((522, 244, 1151, 679)).resize((662, 446), Image.Resampling.LANCZOS)
    canvas.alpha_composite(parchment_crop, (505, 244))
    beam(canvas, source, (492, 231, 1180, 244), False)
    beam(canvas, source, (492, 690, 1180, 703), False)
    beam(canvas, source, (492, 244, 505, 690), True)
    beam(canvas, source, (1167, 244, 1180, 690), True)

    profiles = [render_profile(player) for player in PLAYERS]
    for profile, box in zip(profiles, PLAYER_WINDOWS):
        install_player_window(canvas, source, profile, box)

    # A restrained handful of existing Guesstimate props occupies only small cubbies.
    paste_prop(canvas, source, (78, 86, 184, 222), (65, 74, 66, 110))
    paste_prop(canvas, source, (72, 253, 190, 371), (62, 237, 72, 102))
    paste_prop(canvas, source, (72, 395, 176, 474), (62, 390, 70, 80))
    paste_prop(canvas, source, (611, 128, 722, 240), (570, 145, 105, 76))
    paste_prop(canvas, source, (724, 145, 858, 239), (720, 145, 105, 75))
    paste_prop(canvas, source, (960, 120, 1072, 239), (934, 144, 100, 78))
    paste_prop(canvas, source, (1080, 165, 1184, 239), (1053, 155, 82, 68))
    paste_prop(canvas, source, (1510, 155, 1607, 261), (1540, 82, 68, 106))
    paste_prop(canvas, source, (1515, 700, 1606, 844), (1540, 724, 66, 122))

    draw_game_ui(canvas, parchment_box, True)
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle((682, 77, 990, 109), 14, fill=(15, 46, 48, 238), outline=(222, 168, 72), width=2)
    from render_perfect_setzkasten_preview import centered, font
    centered(d, (682, 77, 990, 109), "Jans Runde  ·  Runde 4  ·  4 Spieler", font(12, True), (255, 238, 188))

    # One continuous outer cabinet frame, drawn last.
    beam(canvas, source, (42, 34, 1630, 55), False)
    beam(canvas, source, (42, 878, 1630, 899), False)
    beam(canvas, source, (42, 55, 63, 878), True)
    beam(canvas, source, (1609, 55, 1630, 878), True)

    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / "stormseeds-perfect-setzkasten-4-spieler-v2.png"
    canvas.convert("RGB").save(target, quality=96)
    print(target)


if __name__ == "__main__":
    build()
