"""Render two four-player Setzkasten concepts with the canonical profile assets."""

from __future__ import annotations

from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "offline-preview/perfect-setzkasten-test"

BACKGROUNDS = {
    "oma": Path("/home/igroup/.codex/generated_images/01a16010-225d-72c3-8188-2974874fcd34/exec-b2c7521b-c8d1-4fb6-afb0-7602d1eb0062.png"),
    "modern": Path("/home/igroup/.codex/generated_images/01a16010-225d-72c3-8188-2974874fcd34/exec-2e4b1357-19b5-4684-8c35-a137d0aa0db5.png"),
    "modern_rebuilt": ROOT / "offline-preview/perfect-setzkasten-test/setzkasten-modern-background-rebuilt-v1.png",
}

PLAYERS = (
    {
        "name": "Jan", "score": "300 Punkte", "phrase": "Ich weiß kreativ.",
        "background": "background-bergsee-v1.png", "plaque": "p01.webp",
        "avatar": "a01-kea.webp", "podium": "p01-tavernenschild-tall-v2.png", "pult": "p01",
    },
    {
        "name": "Mira", "score": "500 Punkte", "phrase": "Fast schon wahr.",
        "background": "background-neon-garten-v1.png", "plaque": "p06.webp",
        "avatar": "a06-oktopus.webp", "podium": "p06-theatersamt-tall-v2.png", "pult": "p06",
    },
    {
        "name": "Tom", "score": "200 Punkte", "phrase": "Details? Überschätzt.",
        "background": "background-wissensatelier-v1.png", "plaque": "p09.webp",
        "avatar": "a14-somnus-cutout-v2.png", "podium": "p09-kupferpatina-tall-v2.png", "pult": "p09",
    },
    {
        "name": "Lea", "score": "400 Punkte", "phrase": "Klingt verdächtig.",
        "background": "background-wolkenpavillon-v1.png", "plaque": "p12.webp",
        "avatar": "a17-luno-cutout-v2.png", "podium": "p12-wurzelholz-tall-v2.png", "pult": "p12",
    },
)

PULT_FIELDS = {
    "p01": ((.2892, .5192, .7252, .6738), (.2892, .7768, .7252, .9314)),
    "p06": ((.2923, .4264, .7093, .5499), (.3077, .6823, .6938, .8058)),
    "p09": ((.3029, .4686, .7176, .5886), (.3177, .7257, .7028, .8457)),
    "p12": ((.3147, .4343, .7047, .5543), (.3222, .6914, .6972, .8114)),
}


def font(size: int, bold: bool = False, serif: bool = False) -> ImageFont.FreeTypeFont:
    if serif:
        family = "dejavu/DejaVuSerif-Bold.ttf" if bold else "dejavu/DejaVuSerif.ttf"
    else:
        family = "dejavu/DejaVuSans-Bold.ttf" if bold else "dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(f"/usr/share/fonts/truetype/{family}", size)


def cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    scale = max(size[0] / image.width, size[1] / image.height)
    resized = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    x = (resized.width - size[0]) // 2
    y = (resized.height - size[1]) // 2
    return resized.crop((x, y, x + size[0], y + size[1]))


def contain(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    image = image.copy()
    image.thumbnail(size, Image.Resampling.LANCZOS)
    layer = Image.new("RGBA", size)
    layer.alpha_composite(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return layer


def centered(draw: ImageDraw.ImageDraw, box, text: str, used_font, fill, stroke=0, stroke_fill=None):
    l, t, r, b = box
    bounds = draw.textbbox((0, 0), text, font=used_font, stroke_width=stroke)
    x = l + (r - l - (bounds[2] - bounds[0])) / 2
    y = t + (b - t - (bounds[3] - bounds[1])) / 2 - bounds[1]
    draw.text((x, y), text, font=used_font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)


def fit_font(draw, text, max_width, start, *, bold=False, serif=False, minimum=10):
    size = start
    while size > minimum and draw.textbbox((0, 0), text, font=font(size, bold, serif))[2] > max_width:
        size -= 1
    return font(size, bold, serif)


def render_profile(player: dict) -> Image.Image:
    w, h = 430, 570
    scene = cover(Image.open(ROOT / "static" / player["background"]).convert("RGBA"), (w, h))
    shade = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for y in range(h):
        a = int(8 + 75 * (y / h) ** 2)
        sd.line((0, y, w, y), fill=(4, 2, 9, a))
    scene.alpha_composite(shade)

    plaque_w, plaque_h = round(w * .84), round((w * .84) / 3.1)
    plaque = Image.open(ROOT / "static/plaques" / player["plaque"]).convert("RGBA").resize((plaque_w, plaque_h), Image.Resampling.LANCZOS)
    plaque_x, plaque_y = (w - plaque_w) // 2, round(h * .005)
    scene.alpha_composite(plaque, (plaque_x, plaque_y))
    draw = ImageDraw.Draw(scene)
    phrase_font = fit_font(draw, player["phrase"], plaque_w * .66, 21, bold=True, serif=True, minimum=12)
    centered(draw, (plaque_x + plaque_w*.17, plaque_y + plaque_h*.22, plaque_x + plaque_w*.83, plaque_y + plaque_h*.64), player["phrase"], phrase_font, (255, 242, 190), 1, (44, 19, 10))

    avatar_w, avatar_h = round(w * .58), round(h * .49)
    avatar = contain(Image.open(ROOT / "static/avatars/stage" / player["avatar"]).convert("RGBA"), (avatar_w, avatar_h))
    scene.alpha_composite(avatar, ((w - avatar_w) // 2, round(h * .20)))

    podium_w, podium_h = round(w * .79), round((w * .79) * 7 / 8)
    podium = contain(Image.open(ROOT / "static/podiums" / player["podium"]).convert("RGBA"), (podium_w, podium_h))
    podium_x, podium_y = (w - podium_w) // 2, h - podium_h
    scene.alpha_composite(podium, (podium_x, podium_y))

    draw = ImageDraw.Draw(scene)
    name_box, score_box = PULT_FIELDS[player["pult"]]
    def absolute(box):
        return tuple((podium_x + box[i] * podium_w) if i % 2 == 0 else (podium_y + box[i] * podium_h) for i in range(4))
    name_abs, score_abs = absolute(name_box), absolute(score_box)
    centered(draw, name_abs, player["name"], fit_font(draw, player["name"], name_abs[2]-name_abs[0]-6, 26, bold=True, serif=True), (255, 244, 211), 1, (42, 16, 7))
    centered(draw, score_abs, player["score"], fit_font(draw, player["score"], score_abs[2]-score_abs[0]-5, 20, bold=True), (255, 222, 100), 1, (42, 16, 7))
    return scene


def framed_profile(profile: Image.Image, width: int, modern: bool) -> Image.Image:
    height = round(width * 57 / 43)
    profile = profile.resize((width, height), Image.Resampling.LANCZOS)
    pad = max(5, width // 35)
    shadow_pad = max(12, width // 12)
    frame = Image.new("RGBA", (width + 2*pad + shadow_pad, height + 2*pad + shadow_pad))
    sh = Image.new("RGBA", frame.size)
    ImageDraw.Draw(sh).rounded_rectangle((shadow_pad//2, shadow_pad//2, width+2*pad+shadow_pad//2, height+2*pad+shadow_pad//2), pad, fill=(0, 0, 0, 210))
    sh = sh.filter(ImageFilter.GaussianBlur(max(5, width//24)))
    frame.alpha_composite(sh)
    color = (31, 72, 78, 255) if modern else (70, 32, 13, 255)
    line = (217, 159, 64, 255) if modern else (145, 79, 30, 255)
    d = ImageDraw.Draw(frame)
    d.rounded_rectangle((0, 0, width+2*pad, height+2*pad), pad, fill=color, outline=line, width=max(2, pad//2))
    frame.alpha_composite(profile, (pad, pad))
    return frame


def inset_compartment(profile: Image.Image, width: int, background: Image.Image) -> Image.Image:
    """Build one true Setzkasten recess: profile as back wall, wood rails in front."""
    height = round(width * 57 / 43)
    rail = 20
    brass = 3
    outer_w, outer_h = width + rail * 2, height + rail * 2
    recess = Image.new("RGBA", (outer_w, outer_h))

    # The canonical scene is the complete back wall of the compartment.
    scene = profile.resize((width, height), Image.Resampling.LANCZOS)
    recess.alpha_composite(scene, (rail, rail))

    # Reuse actual painted timber from the selected cabinet for all four
    # compartments, so the rails belong to the Setzkasten instead of looking
    # like a separate card border.
    source = background.crop((410, 45, 1230, 88)).convert("L")
    source = ImageOps.colorize(source, black=(7, 24, 27), white=(53, 117, 118)).convert("RGBA")
    top = cover(source, (outer_w, rail))
    bottom = cover(source.transpose(Image.Transpose.FLIP_TOP_BOTTOM), (outer_w, rail))
    vertical_source = source.rotate(90, expand=True)
    left = cover(vertical_source, (rail, outer_h))
    right = cover(vertical_source.transpose(Image.Transpose.FLIP_LEFT_RIGHT), (rail, outer_h))
    recess.alpha_composite(top, (0, 0))
    recess.alpha_composite(bottom, (0, outer_h - rail))
    recess.alpha_composite(left, (0, 0))
    recess.alpha_composite(right, (outer_w - rail, 0))

    draw = ImageDraw.Draw(recess)
    draw.rectangle((1, 1, outer_w-2, outer_h-2), outline=(33, 15, 8), width=3)
    draw.line((4, 4, outer_w-5, 4), fill=(77, 139, 135), width=2)
    draw.line((4, 4, 4, outer_h-5), fill=(67, 126, 124), width=2)
    draw.line((rail-2, rail-2, outer_w-rail+1, rail-2), fill=(5, 19, 22), width=4)
    draw.line((rail-2, rail-2, rail-2, outer_h-rail+1), fill=(5, 18, 21), width=4)
    draw.line((rail, outer_h-rail+1, outer_w-rail, outer_h-rail+1), fill=(69, 125, 119), width=2)
    draw.line((outer_w-rail+1, rail, outer_w-rail+1, outer_h-rail), fill=(65, 120, 116), width=2)
    # Brass pins and a narrow inner shadow make the scene read as recessed.
    for cx, cy in ((7, 7), (outer_w-8, 7), (7, outer_h-8), (outer_w-8, outer_h-8)):
        draw.ellipse((cx-brass, cy-brass, cx+brass, cy+brass), fill=(210, 151, 53), outline=(73, 39, 17), width=1)
    shadow = Image.new("RGBA", (outer_w, outer_h))
    sd = ImageDraw.Draw(shadow)
    sd.rectangle((rail, rail, rail+10, outer_h-rail), fill=(0, 0, 0, 175))
    sd.rectangle((rail, rail, outer_w-rail, rail+11), fill=(0, 0, 0, 185))
    sd.rectangle((outer_w-rail-5, rail, outer_w-rail, outer_h-rail), fill=(0, 0, 0, 70))
    sd.rectangle((rail, outer_h-rail-5, outer_w-rail, outer_h-rail), fill=(0, 0, 0, 60))
    shadow = shadow.filter(ImageFilter.GaussianBlur(5))
    recess.alpha_composite(shadow)
    return recess


def install_profile_as_recess_back(canvas: Image.Image, profile: Image.Image, box: tuple[int, int, int, int]):
    """Replace the cabinet back wall itself; draw only the cabinet's boundary rails."""
    x, y, width, height = box
    if width * 57 != height * 43:
        raise ValueError("player recess must be exactly 43:57")
    scene = profile.resize((width, height), Image.Resampling.LANCZOS)
    canvas.alpha_composite(scene, (x, y))

    # Thin structural dividers sit outside the opening. There is intentionally
    # no surrounding card, picture frame, pad, or drop shadow.
    rail = 9
    timber = canvas.crop((520, 46, 1170, 72)).convert("L")
    timber = ImageOps.colorize(timber, black=(7, 25, 28), white=(58, 126, 124)).convert("RGBA")
    top = cover(timber, (width + rail * 2, rail))
    bottom = cover(timber.transpose(Image.Transpose.FLIP_TOP_BOTTOM), (width + rail * 2, rail))
    vertical = timber.rotate(90, expand=True)
    left = cover(vertical, (rail, height))
    right = cover(vertical.transpose(Image.Transpose.FLIP_LEFT_RIGHT), (rail, height))
    canvas.alpha_composite(top, (x - rail, y - rail))
    canvas.alpha_composite(bottom, (x - rail, y + height))
    canvas.alpha_composite(left, (x - rail, y))
    canvas.alpha_composite(right, (x + width, y))

    # The shadow falls into the recess, never outside as on a floating card.
    shade = Image.new("RGBA", canvas.size)
    sd = ImageDraw.Draw(shade)
    sd.rectangle((x, y, x + 8, y + height), fill=(0, 0, 0, 115))
    sd.rectangle((x, y, x + width, y + 9), fill=(0, 0, 0, 130))
    shade = shade.filter(ImageFilter.GaussianBlur(4))
    canvas.alpha_composite(shade)


def draw_game_ui(canvas: Image.Image, parchment, modern: bool):
    l, t, r, b = parchment
    draw = ImageDraw.Draw(canvas)
    accent = (12, 93, 105) if modern else (137, 45, 25)
    ink = (43, 26, 18)
    tag = (l+42, t+22, l+158, t+50)
    draw.rounded_rectangle(tag, 14, fill=accent)
    centered(draw, tag, "KURIOSITÄT", font(10, True), (255, 242, 199))
    timer = (r-100, t+20, r-42, t+50)
    draw.rounded_rectangle(timer, 15, fill=(255, 244, 211), outline=accent, width=2)
    centered(draw, timer, "2:41", font(13, True), accent)

    question = "Wie maßregeln manche Oktopusse ihre Fischpartner bei einer gemeinsamen Jagd?"
    lines = wrap(question, width=39)
    y = t + 70
    for line in lines:
        centered(draw, (l+42, y, r-42, y+35), line, font(22, True, True), ink)
        y += 31
    centered(draw, (l+40, y+5, r-40, y+32), "Erfinde eine kurze, glaubwürdige Auflösung.", font(12), (103, 71, 49))
    input_box = (l+62, y+49, r-62, b-58)
    draw.rounded_rectangle(input_box, 10, fill=(255, 249, 226, 235), outline=(160, 111, 60), width=2)
    draw.text((input_box[0]+14, input_box[1]+12), "Deine Antwort …", font=font(13), fill=(145, 120, 94))
    button = (r-214, b-48, r-62, b-15)
    draw.rounded_rectangle(button, 10, fill=accent, outline=(229, 177, 73), width=2)
    centered(draw, button, "Antwort abgeben", font(11, True), (255, 244, 207))

    controls = (l+180, t+19, r-116, t+51)
    draw.rounded_rectangle(controls, 14, fill=(56, 32, 22, 225), outline=(211, 155, 69), width=1)
    centered(draw, controls, "Ⅱ  Pause       »  Nächste Frage", font(11, True), (255, 233, 177))


def build(kind: str):
    canvas = Image.open(BACKGROUNDS[kind]).convert("RGBA")
    modern = kind == "modern"
    if modern:
        placements = ((198, 108, 180), (266, 465, 205), (1300, 107, 180), (1218, 492, 205))
        parchment = (523, 252, 1135, 665)
    else:
        placements = ((168, 98, 210), (279, 474, 205), (1292, 98, 210), (1193, 492, 205))
        parchment = (535, 247, 1132, 625)

    profiles = [render_profile(player) for player in PLAYERS]
    for profile, (x, y, width) in zip(profiles, placements):
        canvas.alpha_composite(framed_profile(profile, width, modern), (x, y))
    draw_game_ui(canvas, parchment, modern)

    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / f"setzkasten-{kind}-4-spieler-v1.png"
    canvas.convert("RGB").save(target, quality=95)
    print(target)


def build_selected_modern_lobby():
    """Selected direction: four equally sized canonical profiles, as large as the recesses allow."""
    canvas = Image.open(BACKGROUNDS["modern"]).convert("RGBA")
    profile_width = 225
    placements = (
        (179, 92),   # upper left, near the outer edge
        (250, 451),  # lower left, deliberately shifted inward
        (1278, 91),  # upper right, near the outer edge
        (1204, 472), # lower right, deliberately shifted inward
    )

    profiles = [render_profile(player) for player in PLAYERS]
    for profile, (x, y) in zip(profiles, placements):
        canvas.alpha_composite(framed_profile(profile, profile_width, True), (x, y))

    draw_game_ui(canvas, (523, 252, 1135, 665), True)

    # A restrained running-lobby label uses an existing empty compartment
    # without changing the central question card or any player component.
    draw = ImageDraw.Draw(canvas)
    lobby = (681, 73, 990, 105)
    draw.rounded_rectangle(lobby, 14, fill=(17, 46, 48, 232), outline=(218, 164, 68), width=2)
    centered(draw, lobby, "Jans Runde  ·  Runde 4  ·  4 Spieler", font(12, True), (255, 237, 185))

    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / "setzkasten-modern-laufende-lobby-4-spieler-v2.png"
    canvas.convert("RGB").save(target, quality=96)
    print(target)


def build_selected_modern_inset_lobby():
    """Corrected concept: exact profile recesses, never cards placed on top."""
    canvas = Image.open(BACKGROUNDS["modern"]).convert("RGBA")
    profile_width = 235
    placements = (
        (164, 81),
        (241, 433),
        (1262, 81),
        (1177, 456),
    )
    profiles = [render_profile(player) for player in PLAYERS]
    for profile, (x, y) in zip(profiles, placements):
        canvas.alpha_composite(inset_compartment(profile, profile_width, canvas), (x, y))

    draw_game_ui(canvas, (523, 252, 1135, 665), True)
    draw = ImageDraw.Draw(canvas)
    lobby = (681, 73, 990, 105)
    draw.rounded_rectangle(lobby, 14, fill=(17, 46, 48, 232), outline=(218, 164, 68), width=2)
    centered(draw, lobby, "Jans Runde  ·  Runde 4  ·  4 Spieler", font(12, True), (255, 237, 185))

    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / "setzkasten-modern-laufende-lobby-4-spieler-v3.png"
    canvas.convert("RGB").save(target, quality=96)
    print(target)


def build_rebuilt_cabinet_lobby():
    """Final structural correction based on the annotated shelf-line diagnosis."""
    canvas = Image.open(BACKGROUNDS["modern_rebuilt"]).convert("RGBA")
    # All four openings have exactly the same dimensions and 43:57 ratio.
    # Their larger rectangles cover the old dividers completely, so no former
    # shelf edge can continue behind a player scene.
    recesses = (
        (157, 77, 258, 342),
        (235, 440, 258, 342),
        (1268, 77, 258, 342),
        (1183, 475, 258, 342),
    )
    profiles = [render_profile(player) for player in PLAYERS]
    for profile, box in zip(profiles, recesses):
        install_profile_as_recess_back(canvas, profile, box)

    draw_game_ui(canvas, (523, 252, 1135, 665), True)
    draw = ImageDraw.Draw(canvas)
    lobby = (681, 73, 990, 105)
    draw.rounded_rectangle(lobby, 14, fill=(17, 46, 48, 232), outline=(218, 164, 68), width=2)
    centered(draw, lobby, "Jans Runde  ·  Runde 4  ·  4 Spieler", font(12, True), (255, 237, 185))

    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / "setzkasten-modern-laufende-lobby-4-spieler-v4.png"
    canvas.convert("RGB").save(target, quality=96)
    print(target)


if __name__ == "__main__":
    build("oma")
    build("modern")
    build_selected_modern_lobby()
    build_selected_modern_inset_lobby()
    build_rebuilt_cabinet_lobby()
