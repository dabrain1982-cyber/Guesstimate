#!/usr/bin/env python3
"""Normalize profile avatars and tall podiums without changing aspect ratios.

Every complete visible avatar shares one height and touches the bottom of its
transparent canvas.  Every complete visible podium, including all decorations,
shares one height and touches the bottom of its transparent canvas.  Existing
public filenames are kept so the running service receives the corrected assets
without a Python reload.
"""

from pathlib import Path
import shutil

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
AVATAR_DIR = ROOT / "static" / "avatars" / "stage"
PODIUM_DIR = ROOT / "static" / "podiums"

AVATAR_CANVAS = (1400, 1400)
AVATAR_VISIBLE_HEIGHT = 1000
PODIUM_CANVAS = (1600, 1400)
PODIUM_VISIBLE_HEIGHT = 1200


def backup(path: Path) -> Path:
    backup_path = path.with_name(f"{path.stem}-pre-normalization-v1{path.suffix}")
    if not backup_path.exists():
        shutil.copy2(path, backup_path)
    return backup_path


def save(image: Image.Image, path: Path) -> None:
    if path.suffix.lower() == ".webp":
        image.save(path, "WEBP", lossless=True, method=6)
    else:
        image.save(path, "PNG", optimize=True)


def normalize_avatar(path: Path) -> None:
    source = Image.open(backup(path)).convert("RGBA")
    bounds = source.getchannel("A").getbbox()
    if not bounds:
        raise ValueError(f"Avatar has no visible pixels: {path}")

    visible = source.crop(bounds)
    scale = AVATAR_VISIBLE_HEIGHT / visible.height
    target_size = (round(visible.width * scale), AVATAR_VISIBLE_HEIGHT)
    if target_size[0] > AVATAR_CANVAS[0]:
        raise ValueError(f"Avatar would exceed normalized canvas: {path}")
    visible = visible.resize(target_size, Image.Resampling.LANCZOS)

    normalized = Image.new("RGBA", AVATAR_CANVAS, (0, 0, 0, 0))
    left = (AVATAR_CANVAS[0] - visible.width) // 2
    top = AVATAR_CANVAS[1] - visible.height
    normalized.alpha_composite(visible, (left, top))
    save(normalized, path)


def normalize_podium(path: Path) -> None:
    source = Image.open(backup(path)).convert("RGBA")
    bounds = source.getchannel("A").getbbox()
    if not bounds:
        raise ValueError(f"Podium has no visible pixels: {path}")

    visible = source.crop(bounds)
    scale = PODIUM_VISIBLE_HEIGHT / visible.height
    target_size = (round(visible.width * scale), PODIUM_VISIBLE_HEIGHT)
    if target_size[0] > PODIUM_CANVAS[0]:
        raise ValueError(f"Podium would exceed normalized canvas: {path}")
    visible = visible.resize(target_size, Image.Resampling.LANCZOS)

    normalized = Image.new("RGBA", PODIUM_CANVAS, (0, 0, 0, 0))
    left = (PODIUM_CANVAS[0] - visible.width) // 2
    top = PODIUM_CANVAS[1] - visible.height
    normalized.alpha_composite(visible, (left, top))
    save(normalized, path)


def active_avatars() -> list[Path]:
    result = []
    for number in range(1, 19):
        matches = [
            path
            for path in AVATAR_DIR.glob(f"a{number:02d}-*")
            if "pre-normalization" not in path.name
            and ((number >= 14 and "cutout-v2" in path.name) or (number < 14 and path.suffix == ".webp"))
        ]
        if len(matches) != 1:
            raise ValueError(f"Expected one active avatar a{number:02d}, found {matches}")
        result.append(matches[0])
    return result


def active_podiums() -> list[Path]:
    result = [path for path in PODIUM_DIR.glob("p*-tall-v*.png") if "pre-normalization" not in path.name]
    if len(result) != 14:
        raise ValueError(f"Expected 14 active tall podiums, found {len(result)}")
    return sorted(result)


if __name__ == "__main__":
    for avatar_path in active_avatars():
        normalize_avatar(avatar_path)
    for podium_path in active_podiums():
        normalize_podium(podium_path)
    print("Normalized 18 avatars and 14 podiums without changing aspect ratios.")
