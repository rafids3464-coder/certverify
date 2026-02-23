"""
generate_synthetic.py - Generate synthetic "REAL" certificate images.

Creates ~2000 synthetic certificates across 5 templates with:
- Random university names, student names, dates, roll numbers
- Random seal/stamp placement
- Random signature placement
Outputs to dataset/train/real/ and dataset/val/real/
"""

import os
import random
import string
import math
from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

# ── Configuration ─────────────────────────────────────────────────────────────

TRAIN_COUNT = 1600   # number of training real certs
VAL_COUNT   = 400    # number of validation real certs
OUTPUT_ROOT = Path(__file__).parent.parent / "dataset"

# ── Data pools ────────────────────────────────────────────────────────────────

UNIVERSITIES = [
    "Harvard University", "Stanford University", "MIT", "Oxford University",
    "Cambridge University", "IIT Delhi", "IIT Bombay", "NIT Trichy",
    "University of Toronto", "ETH Zurich", "National University of Singapore",
    "Caltech", "Princeton University", "Yale University", "Columbia University",
    "University of Michigan", "Cornell University", "Duke University",
    "Johns Hopkins University", "UC Berkeley",
]

COURSES = [
    "Bachelor of Technology in Computer Science",
    "Master of Science in Data Science",
    "Bachelor of Engineering",
    "Diploma in Machine Learning",
    "Certificate in Cybersecurity",
    "Master of Business Administration",
    "Bachelor of Science in Physics",
    "Doctor of Philosophy in Mathematics",
]

FIRST_NAMES = [
    "Aarav", "Priya", "John", "Sarah", "Mohammed", "Fatima", "Li", "Wei",
    "Carlos", "Maria", "Ahmed", "Aisha", "Raj", "Ananya", "David", "Emily",
    "Chen", "Yuki", "Luca", "Sofia",
]

LAST_NAMES = [
    "Sharma", "Smith", "Johnson", "Patel", "Khan", "Wang", "Garcia",
    "Martinez", "Singh", "Kumar", "Ali", "Chen", "Williams", "Brown",
    "Tanaka", "Rossi", "Müller", "Dubois", "Ivanov", "Santos",
]

COLORS_BG = [
    (250, 248, 240),  # warm white
    (240, 248, 255),  # alice blue
    (255, 250, 240),  # floral white
    (245, 245, 220),  # beige
    (255, 255, 240),  # ivory
]

BORDER_COLORS = [
    (139, 90, 43),   # brown gold
    (0, 80, 140),    # navy blue
    (128, 0, 0),     # maroon
    (0, 100, 0),     # dark green
    (70, 70, 70),    # charcoal
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def random_roll() -> str:
    prefix = random.choice(["CS", "EC", "ME", "CE", "AI"])
    year   = random.randint(18, 24)
    num    = random.randint(1000, 9999)
    return f"{prefix}{year:02d}{num}"


def random_date() -> str:
    day   = random.randint(1, 28)
    month = random.choice([
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ])
    year  = random.randint(2018, 2025)
    return f"{day} {month}, {year}"


def draw_border(draw: ImageDraw.ImageDraw, W: int, H: int, color: Tuple) -> None:
    """Draw a double-line decorative border."""
    m1, m2 = 20, 28
    draw.rectangle([m1, m1, W - m1, H - m1], outline=color, width=3)
    draw.rectangle([m2, m2, W - m2, H - m2], outline=color, width=1)


def draw_seal(img: Image.Image, x: int, y: int, r: int = 55) -> None:
    """Draw a circular seal / stamp."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    color = random.choice([(0, 0, 180), (180, 0, 0), (0, 120, 0)])
    for i in range(3):
        draw.ellipse(
            [x - r + i * 4, y - r + i * 4, x + r - i * 4, y + r - i * 4],
            outline=(*color, 160), width=2
        )
    # inner text
    draw.text((x - 20, y - 8), "SEAL", fill=(*color, 180))
    img.paste(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"),
              (0, 0))


def draw_signature(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    """Simulate a handwritten signature using random curves."""
    sig_color = (20, 20, 120)
    start_x = x
    for i in range(40):
        dx = random.randint(-15, 20)
        dy = random.randint(-8, 8)
        draw.line([(start_x, y), (start_x + dx, y + dy)], fill=sig_color, width=2)
        start_x += dx
        y += dy // 2


# ── Template functions ────────────────────────────────────────────────────────

def _get_font(size: int):
    """Try to get a system font, fall back to default."""
    try:
        paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
            "C:/Windows/Fonts/times.ttf",
            "C:/Windows/Fonts/georgia.ttf",
            "C:/Windows/Fonts/arial.ttf",
        ]
        for p in paths:
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    except Exception:
        pass
    return ImageFont.load_default()


def template_classic(data: dict, W: int = 800, H: int = 600) -> Image.Image:
    """Classic parchment-style certificate."""
    bg_color = random.choice(COLORS_BG)
    border_color = random.choice(BORDER_COLORS)
    img = Image.new("RGB", (W, H), bg_color)
    draw = ImageDraw.Draw(img)
    draw_border(draw, W, H, border_color)

    font_title = _get_font(36)
    font_uni   = _get_font(22)
    font_body  = _get_font(16)
    font_small = _get_font(13)

    # Title
    draw.text((W // 2, 80), "CERTIFICATE OF COMPLETION",
              fill=border_color, font=font_title, anchor="mm")
    # University
    draw.text((W // 2, 130), data["university"],
              fill=(40, 40, 40), font=font_uni, anchor="mm")
    # Separator line
    draw.line([(100, 155), (W - 100, 155)], fill=border_color, width=1)
    # Body text
    draw.text((W // 2, 200), "This is to certify that",
              fill=(60, 60, 60), font=font_body, anchor="mm")
    draw.text((W // 2, 240), data["name"],
              fill=border_color, font=_get_font(28), anchor="mm")
    draw.text((W // 2, 285), "has successfully completed the course of",
              fill=(60, 60, 60), font=font_body, anchor="mm")
    draw.text((W // 2, 315), data["course"],
              fill=(40, 40, 40), font=font_body, anchor="mm")
    draw.text((W // 2, 355), f"Roll No: {data['roll']}",
              fill=(80, 80, 80), font=font_small, anchor="mm")
    draw.text((W // 2, 380), f"Date of Issue: {data['date']}",
              fill=(80, 80, 80), font=font_small, anchor="mm")
    # Signature
    draw.text((200, 470), "Authorized Signatory", fill=(80, 80, 80), font=font_small)
    draw_signature(draw, 200, 460)
    draw.line([(160, 465), (340, 465)], fill=(80, 80, 80), width=1)
    # Seal
    seal_x = random.randint(W - 160, W - 100)
    seal_y = random.randint(H - 140, H - 80)
    draw_seal(img, seal_x, seal_y)
    return img


def template_modern(data: dict, W: int = 800, H: int = 600) -> Image.Image:
    """Modern flat-design certificate with colored header band."""
    img = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    # Header band
    band_color = random.choice([(0, 80, 160), (160, 0, 0), (0, 110, 50)])
    draw.rectangle([0, 0, W, 120], fill=band_color)
    draw.text((W // 2, 60), data["university"],
              fill=(255, 255, 255), font=_get_font(24), anchor="mm")
    draw.text((W // 2, 160), "CERTIFICATE OF ACHIEVEMENT",
              fill=(50, 50, 50), font=_get_font(30), anchor="mm")
    draw.text((W // 2, 230), f"Awarded to: {data['name']}",
              fill=(30, 30, 30), font=_get_font(20), anchor="mm")
    draw.text((W // 2, 280), data["course"],
              fill=(60, 60, 60), font=_get_font(16), anchor="mm")
    draw.text((W // 2, 330), f"Enrollment: {data['roll']}  |  Date: {data['date']}",
              fill=(100, 100, 100), font=_get_font(13), anchor="mm")
    draw.rectangle([40, 400, W - 40, 402], fill=band_color)
    draw.text((200, 450), "Director", fill=(60, 60, 60), font=_get_font(13))
    draw_signature(draw, 160, 445)
    draw_seal(img, W - 120, H - 100)
    return img


def template_elegant(data: dict, W: int = 800, H: int = 600) -> Image.Image:
    """Elegant certificate with corner ornaments."""
    img = Image.new("RGB", (W, H), (255, 253, 245))
    draw = ImageDraw.Draw(img)
    gold = (184, 134, 11)
    # Corner ornaments (simple arcs)
    for x, y in [(30, 30), (W - 80, 30), (30, H - 80), (W - 80, H - 80)]:
        draw.arc([x, y, x + 50, y + 50], 0, 360, fill=gold, width=3)
    draw.rectangle([40, 40, W - 40, H - 40], outline=gold, width=2)
    draw.text((W // 2, 90), "CERTIFICATE OF EXCELLENCE",
              fill=gold, font=_get_font(32), anchor="mm")
    draw.text((W // 2, 135), data["university"],
              fill=(50, 50, 50), font=_get_font(18), anchor="mm")
    draw.line([(150, 158), (W - 150, 158)], fill=gold, width=1)
    draw.text((W // 2, 210), "Proudly presented to",
              fill=(80, 80, 80), font=_get_font(16), anchor="mm")
    draw.text((W // 2, 255), data["name"],
              fill=(30, 30, 90), font=_get_font(30), anchor="mm")
    draw.text((W // 2, 305), data["course"],
              fill=(60, 60, 60), font=_get_font(15), anchor="mm")
    draw.text((W // 2, 345), f"Roll No: {data['roll']}",
              fill=(100, 100, 100), font=_get_font(13), anchor="mm")
    draw.text((W // 2, 370), f"Issued on: {data['date']}",
              fill=(100, 100, 100), font=_get_font(13), anchor="mm")
    draw_signature(draw, 180, 460)
    draw.line([(150, 470), (310, 470)], fill=(80, 80, 80), width=1)
    draw_seal(img, W - 140, H - 110)
    return img


def template_academic(data: dict, W: int = 800, H: int = 600) -> Image.Image:
    """Traditional academic certificate with watermark text."""
    img = Image.new("RGB", (W, H), (250, 245, 235))
    draw = ImageDraw.Draw(img)
    # Watermark
    watermark = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wdraw = ImageDraw.Draw(watermark)
    wdraw.text((W // 2, H // 2), "OFFICIAL", fill=(0, 0, 0, 15),
               font=_get_font(90), anchor="mm")
    img = Image.alpha_composite(img.convert("RGBA"), watermark).convert("RGB")
    draw = ImageDraw.Draw(img)
    maroon = (128, 0, 0)
    draw.rectangle([15, 15, W - 15, H - 15], outline=maroon, width=4)
    draw.rectangle([22, 22, W - 22, H - 22], outline=maroon, width=1)
    draw.text((W // 2, 75), data["university"].upper(),
              fill=maroon, font=_get_font(20), anchor="mm")
    draw.text((W // 2, 130), "OFFICIAL ACADEMIC CERTIFICATE",
              fill=(30, 30, 30), font=_get_font(26), anchor="mm")
    draw.text((W // 2, 190), "This certifies that",
              fill=(70, 70, 70), font=_get_font(14), anchor="mm")
    draw.text((W // 2, 230), data["name"],
              fill=maroon, font=_get_font(28), anchor="mm")
    draw.text((W // 2, 275), "has fulfilled all requirements for the degree of",
              fill=(70, 70, 70), font=_get_font(14), anchor="mm")
    draw.text((W // 2, 308), data["course"],
              fill=(30, 30, 30), font=_get_font(16), anchor="mm")
    draw.text((100, 360), f"Roll No: {data['roll']}",
              fill=(80, 80, 80), font=_get_font(13))
    draw.text((W - 250, 360), f"Date: {data['date']}",
              fill=(80, 80, 80), font=_get_font(13))
    draw_signature(draw, 150, 460)
    draw.line([(100, 470), (300, 470)], fill=(80, 80, 80), width=1)
    draw.text((120, 480), "Registrar", fill=(80, 80, 80), font=_get_font(12))
    draw_seal(img, W - 130, H - 120)
    return img


def template_minimalist(data: dict, W: int = 800, H: int = 600) -> Image.Image:
    """Clean minimalist certificate."""
    img = Image.new("RGB", (W, H), (252, 252, 252))
    draw = ImageDraw.Draw(img)
    accent = random.choice([(41, 128, 185), (39, 174, 96), (142, 68, 173)])
    draw.rectangle([0, 0, 8, H], fill=accent)
    draw.text((W // 2, 100), data["university"],
              fill=(50, 50, 50), font=_get_font(22), anchor="mm")
    draw.rectangle([80, 120, W - 80, 122], fill=accent)
    draw.text((W // 2, 170), "CERTIFICATE",
              fill=accent, font=_get_font(40), anchor="mm")
    draw.text((W // 2, 230), "This certificate is presented to",
              fill=(120, 120, 120), font=_get_font(15), anchor="mm")
    draw.text((W // 2, 280), data["name"],
              fill=(30, 30, 30), font=_get_font(32), anchor="mm")
    draw.text((W // 2, 330), f"For: {data['course']}",
              fill=(80, 80, 80), font=_get_font(16), anchor="mm")
    draw.text((W // 2, 370), f"ID: {data['roll']}   •   {data['date']}",
              fill=(150, 150, 150), font=_get_font(13), anchor="mm")
    draw_signature(draw, W - 280, 470)
    draw.line([(W - 320, 480), (W - 80, 480)], fill=(150, 150, 150), width=1)
    draw_seal(img, 130, H - 100)
    return img


TEMPLATES = [
    template_classic,
    template_modern,
    template_elegant,
    template_academic,
    template_minimalist,
]


# ── Main generator ────────────────────────────────────────────────────────────

def generate_certificate(idx: int) -> Image.Image:
    data = {
        "university": random.choice(UNIVERSITIES),
        "name": f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
        "course": random.choice(COURSES),
        "roll": random_roll(),
        "date": random_date(),
    }
    template_fn = TEMPLATES[idx % len(TEMPLATES)]
    return template_fn(data)


def generate_dataset(train_count: int = TRAIN_COUNT, val_count: int = VAL_COUNT) -> None:
    print(f"[DATASET] Generating {train_count} train + {val_count} val REAL certificates...")

    for split, count in [("train", train_count), ("val", val_count)]:
        out_dir = OUTPUT_ROOT / split / "real"
        out_dir.mkdir(parents=True, exist_ok=True)
        for i in range(count):
            img = generate_certificate(i)
            img.save(out_dir / f"real_{split}_{i:04d}.jpg", "JPEG", quality=95)
            if (i + 1) % 200 == 0:
                print(f"  [{split}] Generated {i + 1}/{count}")

    print("[DATASET] Real certificate generation complete.")


if __name__ == "__main__":
    generate_dataset()
