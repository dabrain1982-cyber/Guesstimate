"""Render a reproducible four-player preview from the current Perfect assets."""

from __future__ import annotations

from pathlib import Path
import sys
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "offline-preview/perfect-next-question-v1/perfect-group-4-avatars.png"
PROPOSAL_OUTPUT = ROOT / "offline-preview/perfect-next-question-v1/perfect-group-4-avatars-proposal-v2.png"
WIDTH, HEIGHT, TOPBAR = 1920, 1080, 72


def font(size: int, bold: bool = False, serif: bool = False) -> ImageFont.FreeTypeFont:
    family = "dejavu/DejaVuSerif-Bold.ttf" if serif else (
        "dejavu/DejaVuSans-Bold.ttf" if bold else "dejavu/DejaVuSans.ttf"
    )
    return ImageFont.truetype(f"/usr/share/fonts/truetype/{family}", size)


def cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    scale = max(size[0] / image.width, size[1] / image.height)
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)),
        Image.Resampling.LANCZOS,
    )
    left = (resized.width - size[0]) // 2
    top = (resized.height - size[1]) // 2
    return resized.crop((left, top, left + size[0], top + size[1]))


def contain(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    copy = image.copy()
    copy.thumbnail(size, Image.Resampling.LANCZOS)
    layer = Image.new("RGBA", size)
    layer.alpha_composite(copy, ((size[0] - copy.width) // 2, size[1] - copy.height))
    return layer


def centered(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str, used_font, fill):
    left, top, right, bottom = box
    bounds = draw.textbbox((0, 0), text, font=used_font)
    x = left + (right - left - (bounds[2] - bounds[0])) / 2
    y = top + (bottom - top - (bounds[3] - bounds[1])) / 2 - bounds[1]
    draw.text((x, y), text, font=used_font, fill=fill)


def rounded_gradient(size, top, bottom, radius):
    image = Image.new("RGBA", size)
    pixels = image.load()
    for y in range(size[1]):
        ratio = y / max(1, size[1] - 1)
        color = tuple(round(top[i] * (1 - ratio) + bottom[i] * ratio) for i in range(4))
        for x in range(size[0]):
            pixels[x, y] = color
    mask = Image.new("L", size)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    image.putalpha(mask)
    return image


def draw_player(canvas, x, y, name, score, avatar_asset, plaque_asset, status, host=False, you=False):
    width, height = 290, 270
    glow = Image.new("RGBA", (width, 70))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((20, 16, width - 20, 58), fill=(255, 181, 67, 92))
    glow = glow.filter(ImageFilter.GaussianBlur(10))
    canvas.alpha_composite(glow, (x, y + height - 62))

    avatar = Image.open(ROOT / "static/avatars" / avatar_asset).convert("RGBA")
    avatar = contain(avatar, (220, 212))
    shadow = Image.new("RGBA", avatar.size)
    shadow.putalpha(avatar.getchannel("A").filter(ImageFilter.GaussianBlur(5)))
    canvas.alpha_composite(shadow, (x + 35 + 4, y + 4))
    canvas.alpha_composite(avatar, (x + 35, y))

    plaque = Image.open(ROOT / "static/plaques" / plaque_asset).convert("RGBA")
    plaque = plaque.resize((width, 78), Image.Resampling.LANCZOS)
    plaque_shadow = Image.new("RGBA", plaque.size, (20, 4, 2, 0))
    plaque_shadow.putalpha(plaque.getchannel("A").filter(ImageFilter.GaussianBlur(5)))
    canvas.alpha_composite(plaque_shadow, (x, y + height - 72))
    canvas.alpha_composite(plaque, (x, y + height - 78))
    draw = ImageDraw.Draw(canvas)
    if you:
        draw.rounded_rectangle((x + 3, y + height - 75, x + width - 3, y + height - 3), 18, outline=(255, 219, 100), width=3)
    centered(draw, (x + 30, y + height - 69, x + width - 30, y + height - 40), name, font(20, True, True), (255, 247, 220))
    centered(draw, (x + 30, y + height - 42, x + width - 30, y + height - 16), f"{score} Punkte", font(14, True), (255, 216, 115))

    pill_text = "HOST" if host else status.upper()
    pill_font = font(10, True)
    bounds = draw.textbbox((0, 0), pill_text, font=pill_font)
    pill_width = max(72, bounds[2] - bounds[0] + 22)
    pill_box = (x + width - pill_width - 14, y + height - 105, x + width - 14, y + height - 72)
    fill = (83, 38, 18, 246) if host else (27, 18, 15, 241)
    outline = (216, 163, 64) if host else (142, 117, 90)
    draw.rounded_rectangle(pill_box, 17, fill=fill, outline=outline, width=2)
    centered(draw, pill_box, pill_text, pill_font, (255, 240, 187) if host else (238, 226, 207))


def main() -> None:
    proposal = "--proposal" in sys.argv
    canvas = Image.new("RGBA", (WIDTH, HEIGHT), (24, 11, 9, 255))
    background = Image.open(ROOT / "static/stormseeds-perfect-clubroom-table-v2.png").convert("RGBA")
    canvas.alpha_composite(cover(background, (WIDTH, HEIGHT - TOPBAR)), (0, TOPBAR))
    shade = Image.new("RGBA", (WIDTH, HEIGHT - TOPBAR))
    shade_draw = ImageDraw.Draw(shade)
    for y in range(HEIGHT - TOPBAR):
        alpha = round(12 + 38 * y / (HEIGHT - TOPBAR))
        shade_draw.line((0, y, WIDTH, y), fill=(29, 9, 4, alpha))
    canvas.alpha_composite(shade, (0, TOPBAR))

    topbar = rounded_gradient((WIDTH, TOPBAR), (56, 27, 21, 255), (33, 16, 13, 255), 0)
    canvas.alpha_composite(topbar, (0, 0))
    draw = ImageDraw.Draw(canvas)
    draw.line((0, TOPBAR - 2, WIDTH, TOPBAR - 2), fill=(185, 108, 41), width=2)
    draw.text((42, 27), "← Lobbys", font=font(13, True), fill=(248, 216, 141))
    centered(draw, (760, 4, 1160, 66), "Stormseed´s  Perfect", font(31, True, True), (255, 211, 63))

    # Current host controls, including the newly requested action.
    controls = [((1342, 12, 1437, 43), "Ⅱ  Pause"), ((1445, 12, 1583, 43), "»  Nächste Frage")]
    for box, label in controls:
        draw.rounded_rectangle(box, 16, fill=(67, 31, 22, 242), outline=(223, 180, 106), width=1)
        centered(draw, box, label, font(11, True), (255, 243, 207))
    draw.text((1610, 11), "Jans Runde · Runde 4", font=font(11), fill=(207, 174, 140))
    draw.text((1691, 33), "Ziel: 1.500 Punkte", font=font(13, True), fill=(255, 218, 115))

    player_positions = (
        ((78, 130), (1552, 130), (190, 742), (1440, 742))
        if proposal else
        ((48, 132), (1582, 132), (77, 455), (1553, 455))
    )
    player_data = [
        ("Jan", "300", "stage/a01-kea.webp", "p01.webp", "Denkt nach", True, True),
        ("Mira", "500", "stage/a06-oktopus.webp", "p06.webp", "Denkt nach", False, False),
        ("Tom", "200", "stage/a14-somnus-cutout-v2.png", "p09.webp", "Denkt nach", False, False),
        ("Lea", "400", "stage/a17-luno-cutout-v2.png", "p12.webp", "Denkt nach", False, False),
    ]
    players = [(*position, *data) for position, data in zip(player_positions, player_data)]
    for player in players:
        draw_player(canvas, *player)

    card_x, card_y, card_w, card_h = 530, 119, 860, 592
    shadow = Image.new("RGBA", (card_w + 70, card_h + 70))
    ImageDraw.Draw(shadow).rounded_rectangle((35, 30, card_w + 35, card_h + 30), 30, fill=(10, 2, 1, 190))
    shadow = shadow.filter(ImageFilter.GaussianBlur(22))
    canvas.alpha_composite(shadow, (card_x - 35, card_y - 20))
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((card_x - 9, card_y - 9, card_x + card_w + 9, card_y + card_h + 9), 31, fill=(50, 19, 8), outline=(224, 174, 89), width=3)
    draw.rounded_rectangle((card_x, card_y, card_x + card_w, card_y + card_h), 23, fill=(247, 229, 181), outline=(169, 103, 41), width=8)
    draw.rounded_rectangle((card_x + 35, card_y + 30, card_x + 165, card_y + 62), 16, fill=(148, 39, 24))
    centered(draw, (card_x + 35, card_y + 30, card_x + 165, card_y + 62), "KURIOSITÄT", font(11, True), (255, 241, 186))
    draw.rounded_rectangle((card_x + card_w - 112, card_y + 29, card_x + card_w - 35, card_y + 65), 18, fill=(255, 243, 202), outline=(179, 104, 37), width=2)
    centered(draw, (card_x + card_w - 112, card_y + 29, card_x + card_w - 35, card_y + 65), "2:41", font(16, True), (122, 36, 21))

    question = "Wie maßregeln manche Oktopusse ihre Fischpartner bei einer gemeinsamen Jagd?"
    lines = wrap(question, width=43)
    y = card_y + 98
    for line in lines:
        centered(draw, (card_x + 50, y, card_x + card_w - 50, y + 48), line, font(35, True, True), (56, 25, 15))
        y += 46
    instruction = "Erfinde eine kurze, glaubwürdige Auflösung. Die echte Antwort wird später unauffällig untergemischt."
    centered(draw, (card_x + 80, y + 10, card_x + card_w - 80, y + 45), instruction, font(14), (105, 67, 49))
    draw.text((card_x + 94, y + 76), "DEINE ANTWORT", font=font(11, True), fill=(118, 68, 42))
    input_box = (card_x + 92, y + 100, card_x + card_w - 92, y + 238)
    draw.rounded_rectangle(input_box, 12, fill=(255, 248, 223), outline=(184, 121, 57), width=2)
    draw.text((input_box[0] + 16, input_box[1] + 15), "Klingt das glaubwürdig genug?", font=font(16), fill=(153, 125, 100))
    draw.text((input_box[0], input_box[3] + 18), "0 / 220", font=font(12), fill=(118, 82, 59))
    button = (card_x + card_w - 300, input_box[3] + 8, card_x + card_w - 92, input_box[3] + 53)
    draw.rounded_rectangle(button, 11, fill=(123, 43, 26), outline=(247, 189, 77), width=2)
    centered(draw, button, "Antwort abgeben", font(14, True), (255, 240, 193))

    output = PROPOSAL_OUTPUT if proposal else OUTPUT
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output, quality=94)
    print(output)


if __name__ == "__main__":
    main()
