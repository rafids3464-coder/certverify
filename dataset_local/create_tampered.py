"""
create_tampered.py - Generate FAKE (tampered) versions of real certificates.

Applies one or more of the following forgeries:
1. Replace seal with a mismatched seal
2. Move logo / seal to wrong position
3. Change text via overlay
4. Change font style (text replacement)
5. Add JPEG compression artifacts
"""

import os
import random
import copy
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

# ── Configuration ─────────────────────────────────────────────────────────────

INPUT_REAL_TRAIN = Path(__file__).parent.parent / "dataset/train/real"
INPUT_REAL_VAL   = Path(__file__).parent.parent / "dataset/val/real"
OUTPUT_FAKE_TRAIN = Path(__file__).parent.parent / "dataset/train/fake"
OUTPUT_FAKE_VAL   = Path(__file__).parent.parent / "dataset/val/fake"

# Ratio of tampered to real (we'll match 1:1)
TRAIN_TAMPER_COUNT = 1600
VAL_TAMPER_COUNT   = 400


# ── Tampering functions ───────────────────────────────────────────────────────

def tamper_replace_seal(img: Image.Image) -> Image.Image:
    """Replace the seal area with a visually wrong seal."""
    img = img.copy()
    draw = ImageDraw.Draw(img)
    W, H = img.size
    # Place a mismatched colored seal in corner
    cx = random.randint(W - 200, W - 60)
    cy = random.randint(H - 200, H - 60)
    r  = random.randint(35, 60)
    wrong_color = random.choice([(255, 0, 0), (0, 200, 0), (200, 100, 0)])
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=wrong_color, width=4)
    draw.ellipse([cx - r + 8, cy - r + 8, cx + r - 8, cy + r - 8],
                 outline=wrong_color, width=2)
    draw.text((cx - 15, cy - 8), "FAKE", fill=wrong_color)
    return img


def tamper_move_logo(img: Image.Image) -> Image.Image:
    """Cut a region from one corner and paste it offset to simulate logo move."""
    img = img.copy()
    W, H = img.size
    # Crop a region
    x1, y1 = random.randint(0, W // 4), random.randint(0, H // 4)
    x2, y2 = x1 + random.randint(60, 120), y1 + random.randint(60, 120)
    region = img.crop((x1, y1, x2, y2))
    # Paste it at a wrong location
    new_x = random.randint(W // 2, W - (x2 - x1) - 10)
    new_y = random.randint(H // 4, H // 2)
    img.paste(region, (new_x, new_y))
    return img


def tamper_text_overlay(img: Image.Image) -> Image.Image:
    """Overlay fake text that doesn't match the certificate's font/style."""
    img = img.copy()
    draw = ImageDraw.Draw(img)
    W, H = img.size
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 18)
    except Exception:
        font = ImageFont.load_default()
    # Place wrong overlay text
    fake_name = random.choice(["Alex Turner", "John Doe", "Maria Lopez", "Test User"])
    x = random.randint(100, W // 2)
    y = random.randint(180, 280)
    # White block to cover original text
    draw.rectangle([x - 5, y - 5, x + 240, y + 25], fill=(255, 255, 255))
    draw.text((x, y), fake_name, fill=(0, 0, 180), font=font)
    return img


def tamper_font_change(img: Image.Image) -> Image.Image:
    """Add a text block with a different font over the name area."""
    img = img.copy()
    draw = ImageDraw.Draw(img)
    W, H = img.size
    # Cover existing name area with white rectangle + different font text
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/cour.ttf", 22)  # Courier (monospace)
    except Exception:
        font = ImageFont.load_default()
    fake_name = random.choice(["AdminUser99", "TAMPERED", "Test Certificate", "000000"])
    cx = W // 2
    y  = random.randint(220, 280)
    draw.rectangle([cx - 200, y - 5, cx + 200, y + 30], fill=(255, 255, 255))
    draw.text((cx - 100, y), fake_name, fill=(0, 0, 0), font=font)
    return img


def tamper_compression_artifacts(img: Image.Image) -> Image.Image:
    """Simulate copy-paste artifacts via aggressive JPEG recompression."""
    import io
    buf = io.BytesIO()
    # Save at very low quality to introduce block artifacts
    quality = random.randint(5, 25)
    img.save(buf, format="JPEG", quality=quality)
    buf.seek(0)
    degraded = Image.open(buf).copy()
    buf.close()
    # Re-save at normal quality
    buf2 = io.BytesIO()
    degraded.save(buf2, format="JPEG", quality=90)
    buf2.seek(0)
    return Image.open(buf2).copy()


TAMPERING_FNS = [
    tamper_replace_seal,
    tamper_move_logo,
    tamper_text_overlay,
    tamper_font_change,
    tamper_compression_artifacts,
]


def apply_tampering(img: Image.Image) -> Image.Image:
    """
    Apply 1–3 random tampering operations to the image.
    Multiple tampers increase realistic forgery diversity.
    """
    n_tampers = random.randint(1, 3)
    chosen = random.sample(TAMPERING_FNS, min(n_tampers, len(TAMPERING_FNS)))
    for fn in chosen:
        try:
            img = fn(img)
        except Exception as e:
            print(f"  Warning: {fn.__name__} failed: {e}")
    return img


# ── Main ──────────────────────────────────────────────────────────────────────

def generate_tampered(
    real_dir: Path,
    out_dir: Path,
    count: int,
    split: str,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    real_files = list(real_dir.glob("*.jpg")) + list(real_dir.glob("*.png"))

    if not real_files:
        print(f"  [WARN] No real images found in {real_dir}")
        return

    print(f"[DATASET] Generating {count} FAKE certificates for '{split}'...")
    for i in range(count):
        src = random.choice(real_files)
        try:
            img = Image.open(src).convert("RGB")
            fake = apply_tampering(img)
            fake.save(out_dir / f"fake_{split}_{i:04d}.jpg", "JPEG", quality=90)
        except Exception as e:
            print(f"  [ERROR] index {i}: {e}")
        if (i + 1) % 200 == 0:
            print(f"  [{split}] Created {i + 1}/{count} fake certs")

    print(f"[DATASET] Fake certificate generation complete for '{split}'.")


def main():
    generate_tampered(INPUT_REAL_TRAIN, OUTPUT_FAKE_TRAIN, TRAIN_TAMPER_COUNT, "train")
    generate_tampered(INPUT_REAL_VAL,   OUTPUT_FAKE_VAL,   VAL_TAMPER_COUNT,   "val")


if __name__ == "__main__":
    main()
