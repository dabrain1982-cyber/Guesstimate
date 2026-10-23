#!/usr/bin/env python3
"""Render the three Stormseed's Conquest boards from Natural Earth vectors."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont


WIDTH, HEIGHT = 4096, 2560
MAP_BOX = (130, 245, WIDTH - 130, HEIGHT - 245)
MASK_SCALE = 4
FONT_ROOT = Path("/usr/share/fonts/truetype/dejavu")
ROOT = Path(__file__).resolve().parents[1]

STYLES = {
    "klassisch": {
        "paper": (229, 218, 190), "ocean": (220, 213, 194), "ink": (52, 43, 33),
        "border": (74, 57, 40), "fine": (113, 96, 73), "font": "DejaVuSerif.ttf",
    },
    "taktisch": {
        "paper": (5, 20, 36), "ocean": (5, 37, 58), "ink": (223, 246, 251),
        "border": (76, 217, 235), "fine": (55, 129, 151), "font": "DejaVuSans.ttf",
    },
    "farbenfroh": {
        "paper": (235, 243, 246), "ocean": (104, 199, 222), "ink": (25, 38, 53),
        "border": (255, 255, 255), "fine": (70, 128, 144), "font": "DejaVuSans.ttf",
    },
}


def rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[index:index + 2], 16) for index in (0, 2, 4))


def mix(a, b, amount):
    return tuple(round(a[i] * (1 - amount) + b[i] * amount) for i in range(3))


def font(style, size, bold=False):
    name = style["font"]
    if bold:
        name = name.replace(".ttf", "-Bold.ttf")
    return ImageFont.truetype(str(FONT_ROOT / name), size)


def project(lon: float, lat: float, scale: int = 1) -> tuple[int, int]:
    left, top, right, bottom = MAP_BOX
    x = left + (lon + 180) / 360 * (right - left)
    y = top + (85 - lat) / 145 * (bottom - top)
    return round(x / scale), round(y / scale)


def polygons(geometry):
    if geometry["type"] == "Polygon":
        yield geometry["coordinates"]
    elif geometry["type"] == "MultiPolygon":
        yield from geometry["coordinates"]


def ring_points(ring, scale=1):
    points = [project(float(lon), float(lat), scale) for lon, lat in ring]
    maximum = WIDTH / scale * .7
    if any(abs(points[index][0] - points[index - 1][0]) > maximum for index in range(1, len(points))):
        return []
    return points


def draw_geometry_mask(features, continents, size, scale):
    image = Image.new("L", size, 0)
    draw = ImageDraw.Draw(image)
    for feature in features:
        if feature["properties"].get("CONTINENT") not in continents:
            continue
        for polygon in polygons(feature["geometry"]):
            outer = ring_points(polygon[0], scale)
            if len(outer) >= 3:
                draw.polygon(outer, fill=255)
            for hole in polygon[1:]:
                inner = ring_points(hole, scale)
                if len(inner) >= 3:
                    draw.polygon(inner, fill=0)
    return image


def territory_masks(world, geojson):
    small = (WIDTH // MASK_SCALE, HEIGHT // MASK_SCALE)
    group_continents = {
        "nordamerika": {"North America"}, "suedamerika": {"South America"},
        "afrika": {"Africa"}, "australien": {"Oceania"}, "eurasien": {"Europe", "Asia"},
    }
    territory_group = {
        row["id"]: ("eurasien" if row["continent"] in {"europa", "asien"} else row["continent"])
        for row in world["territories"]
    }
    small_masks = [Image.new("L", small, 0) for _ in world["territories"]]
    for group, continent_names in group_continents.items():
        land = draw_geometry_mask(geojson["features"], continent_names, small, MASK_SCALE)
        candidate_indices = [index for index, row in enumerate(world["territories"]) if territory_group[row["id"]] == group]
        centers = [(index, *project(*world["territories"][index]["label"], MASK_SCALE)) for index in candidate_indices]
        output = [bytearray(small[0] * small[1]) for _ in candidate_indices]
        pixels = land.load()
        for y in range(small[1]):
            offset = y * small[0]
            for x in range(small[0]):
                if not pixels[x, y]:
                    continue
                winner = min(range(len(centers)), key=lambda item: ((x - centers[item][1]) * .78) ** 2 + ((y - centers[item][2]) * 1.12) ** 2)
                output[winner][offset + x] = 255
        for local_index, global_index in enumerate(candidate_indices):
            small_masks[global_index] = Image.frombytes("L", small, bytes(output[local_index]))
    masks = [mask.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS) for mask in small_masks]
    land = Image.new("L", (WIDTH, HEIGHT), 0)
    for mask in masks:
        land = ImageChops.lighter(land, mask)
    return masks, land


def dotted_line(draw, start, end, color, width=5, dash=18):
    length = math.dist(start, end)
    if not length:
        return
    for distance in range(0, math.ceil(length), dash * 2):
        finish = min(distance + dash, length)
        a, b = distance / length, finish / length
        draw.line((start[0] + (end[0] - start[0]) * a, start[1] + (end[1] - start[1]) * a,
                   start[0] + (end[0] - start[0]) * b, start[1] + (end[1] - start[1]) * b), fill=color, width=width)


def compass(draw, center, style):
    cx, cy = center
    draw.ellipse((cx - 72, cy - 72, cx + 72, cy + 72), outline=style["fine"], width=4)
    draw.ellipse((cx - 48, cy - 48, cx + 48, cy + 48), outline=style["fine"], width=2)
    for angle in range(0, 360, 45):
        radians = math.radians(angle - 90)
        outer = (cx + math.cos(radians) * 67, cy + math.sin(radians) * 67)
        side_a = (cx + math.cos(radians + .22) * 16, cy + math.sin(radians + .22) * 16)
        side_b = (cx + math.cos(radians - .22) * 16, cy + math.sin(radians - .22) * 16)
        draw.polygon((outer, side_a, (cx, cy), side_b), fill=style["border"] if angle % 90 == 0 else style["fine"])
    draw.text((cx, cy - 94), "N", font=font(style, 24, True), fill=style["ink"], anchor="mm")


def background(style_name, style):
    image = Image.new("RGB", (WIDTH, HEIGHT), style["ocean"])
    if style_name == "klassisch":
        noise = Image.effect_noise((WIDTH // 2, HEIGHT // 2), 22).resize((WIDTH, HEIGHT), Image.Resampling.BICUBIC)
        texture = Image.merge("RGB", (noise, noise, noise))
        image = Image.blend(image, texture, .065)
        vignette = Image.new("L", (WIDTH, HEIGHT), 0)
        vignette_draw = ImageDraw.Draw(vignette)
        vignette_draw.ellipse((-500, -400, WIDTH + 500, HEIGHT + 500), fill=215)
        vignette = vignette.filter(ImageFilter.GaussianBlur(250))
        dark = Image.new("RGB", image.size, mix(style["ocean"], (40, 25, 15), .35))
        image.paste(dark, mask=ImageChops.invert(vignette))
    elif style_name == "taktisch":
        draw = ImageDraw.Draw(image)
        for x in range(MAP_BOX[0], MAP_BOX[2] + 1, 120):
            draw.line((x, MAP_BOX[1], x, MAP_BOX[3]), fill=(12, 64, 87), width=2)
        for y in range(MAP_BOX[1], MAP_BOX[3] + 1, 120):
            draw.line((MAP_BOX[0], y, MAP_BOX[2], y), fill=(12, 64, 87), width=2)
    else:
        top = Image.new("RGB", image.size, (154, 225, 238))
        image = Image.blend(image, top, .2)
    return image


def render(style_name, world, geojson, masks, land, output):
    style = STYLES[style_name]
    image = background(style_name, style)
    continent_colors = {row["id"]: rgb(row["color"]) for row in world["continents"]}

    coast_shadow = land.filter(ImageFilter.GaussianBlur(13))
    coast_shadow = ImageChops.subtract(coast_shadow, land)
    image.paste(Image.new("RGB", image.size, (0, 0, 0)), mask=coast_shadow.point(lambda value: min(130, value * 2)))
    for index, territory in enumerate(world["territories"]):
        color = continent_colors[territory["continent"]]
        if style_name == "klassisch":
            color = mix(color, (226, 210, 172), .17)
        elif style_name == "taktisch":
            color = mix(color, (18, 111, 135), .26)
        else:
            color = mix(color, (255, 255, 255), .06)
        if index % 2:
            color = mix(color, (255, 255, 255), .055)
        image.paste(Image.new("RGB", image.size, color), mask=masks[index])

    draw = ImageDraw.Draw(image)
    country_color = mix(style["fine"], style["ocean"], .42)
    for feature in geojson["features"]:
        for polygon in polygons(feature["geometry"]):
            points = ring_points(polygon[0])
            if len(points) >= 3:
                draw.line(points + [points[0]], fill=country_color, width=2)

    boundary = Image.new("L", (WIDTH, HEIGHT), 0)
    boundary_draw = ImageDraw.Draw(boundary)
    for mask in masks:
        edge = ImageChops.difference(mask.filter(ImageFilter.MaxFilter(13)), mask.filter(ImageFilter.MinFilter(13)))
        boundary = ImageChops.lighter(boundary, edge)
    boundary = boundary.filter(ImageFilter.GaussianBlur(.65))
    image.paste(Image.new("RGB", image.size, style["border"]), mask=boundary)
    draw = ImageDraw.Draw(image)

    territories = {row["id"]: row for row in world["territories"]}
    seen = set()
    for territory in world["territories"]:
        start = project(*territory["label"])
        for neighbor_id in territory["neighbors"]:
            edge = tuple(sorted((territory["id"], neighbor_id)))
            if edge in seen:
                continue
            seen.add(edge)
            end = project(*territories[neighbor_id]["label"])
            if math.dist(start, end) > 480:
                if edge == ("alaska", "kamtschatka"):
                    dotted_line(draw, start, (MAP_BOX[0], start[1]), style["fine"])
                    dotted_line(draw, (MAP_BOX[2], end[1]), end, style["fine"])
                else:
                    dotted_line(draw, start, end, style["fine"])

    draw.rounded_rectangle((44, 38, WIDTH - 44, HEIGHT - 38), radius=34, outline=style["fine"], width=4)
    draw.rounded_rectangle((62, 56, WIDTH - 62, HEIGHT - 56), radius=28, outline=mix(style["fine"], style["ocean"], .35), width=2)
    draw.text((WIDTH // 2, 64), "STORMSEED’S CONQUEST", font=font(style, 82, True), fill=style["ink"], anchor="ma",
              stroke_width=2, stroke_fill=style["ocean"])
    draw.text((WIDTH // 2, 154), "42 GEBIETE · 6 KONTINENTE", font=font(style, 28, True), fill=style["ink"], anchor="ma")

    label_adjust = {
        "grossbritannien": (-18, 5), "nordeuropa": (22, -8), "westeuropa": (-10, 18),
        "suedosteuropa": (26, 20), "naher-osten": (18, 10), "japan": (20, 12),
        "indonesien": (-18, 12), "neuguinea": (22, -10), "island": (0, -10),
    }
    for territory in world["territories"]:
        x, y = project(*territory["label"])
        dx, dy = label_adjust.get(territory["id"], (0, 0))
        name = territory["name"]
        size = 31 if len(name) < 12 else 25
        draw.text((x + dx, y + dy), name, font=font(style, size, style_name != "klassisch"), fill=style["ink"], anchor="mm",
                  stroke_width=3, stroke_fill=style["ocean"])

    compass(draw, (WIDTH // 2 - 290, HEIGHT // 2 + 260), style)
    legend_x, legend_y = 140, HEIGHT - 170
    for continent in world["continents"]:
        color = continent_colors[continent["id"]]
        draw.rounded_rectangle((legend_x, legend_y, legend_x + 50, legend_y + 50), radius=10, fill=color, outline=style["ink"], width=2)
        label = f'{continent["name"]}  +{continent["bonus"]}'
        text_font = font(style, 26, True)
        draw.text((legend_x + 66, legend_y + 26), label, font=text_font, fill=style["ink"], anchor="lm")
        legend_x += round(70 + draw.textlength(label, font=text_font) + 42)

    if style_name == "klassisch":
        image = ImageEnhance.Color(image).enhance(.88)
        paper_noise = Image.effect_noise((WIDTH // 2, HEIGHT // 2), 12).resize((WIDTH, HEIGHT), Image.Resampling.BICUBIC)
        paper_rgb = Image.merge("RGB", (paper_noise, paper_noise, paper_noise))
        image = Image.blend(image, paper_rgb, .022)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, "WEBP", quality=96, method=6)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--geojson", required=True, type=Path)
    args = parser.parse_args()
    world = json.loads((ROOT / "static/conquest/world.json").read_text(encoding="utf-8"))
    geojson = json.loads(args.geojson.read_text(encoding="utf-8"))
    masks, land = territory_masks(world, geojson)
    for style_name in STYLES:
        render(style_name, world, geojson, masks, land, ROOT / f"static/conquest/boards/welt-{style_name}-hd.webp")


if __name__ == "__main__":
    main()
