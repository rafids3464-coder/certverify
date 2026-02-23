"""
generate_synthetic.py — Multi-Template REAL Certificate Generator (v2)

- Scans /app/ml/templates/ for background images (JPG/PNG)
- Falls back to 5 programmatic templates if folder is empty
- Overlays randomised Indian student fields with ±5-10px jitter
- Generates ≥1000 REAL samples per template → train/real + val/real
"""

import os
import random
import math
from pathlib import Path
from typing import Tuple, List, Optional

from PIL import Image, ImageDraw, ImageFont
import numpy as np

# ── Configuration ─────────────────────────────────────────────────────────────
OUTPUT_ROOT   = Path(__file__).parent.parent / "dataset"
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
IMG_SIZE      = (512, 512)
SAMPLES_PER_TEMPLATE_TRAIN = 1000
SAMPLES_PER_TEMPLATE_VAL   = 200
VAL_SPLIT     = 0.15    # fraction reserved for val

# ── Indian Names Pool ─────────────────────────────────────────────────────────
FIRST_NAMES = [
    "Aarav","Aditya","Akash","Alok","Amit","Ananya","Anish","Anjali","Ankit",
    "Ankita","Anushka","Arjun","Aryan","Ayesha","Bhavya","Chirag","Deepa",
    "Deepak","Disha","Divya","Fatima","Gaurav","Harsha","Ishaan","Ishita",
    "Jayesh","Jyoti","Kabir","Kajal","Karan","Kavya","Keerthi","Krish",
    "Lakshmi","Lavanya","Mahesh","Manisha","Meera","Mohit","Nalini","Neha",
    "Nikhil","Nisha","Pallavi","Pooja","Pradeep","Pranav","Priya","Rahul",
    "Raj","Rajesh","Ravi","Ritika","Rohan","Rohini","Sachin","Sagar","Sakshi",
    "Salma","Sandeep","Sanjana","Sanjay","Sara","Shivani","Shreya","Siddharth",
    "Simran","Sneha","Sonam","Srishti","Suresh","Swati","Tanvi","Tarun",
    "Uday","Uma","Varun","Vedant","Vikram","Virat","Vishal","Yasmin","Yash",
]

LAST_NAMES = [
    "Agarwal","Ahuja","Bhat","Chandra","Chatterjee","Chopra","Desai","Dey",
    "Dubey","Ghosh","Gupta","Iyer","Jain","Joshi","Kapoor","Kaur","Khan",
    "Kumar","Malhotra","Mehta","Mishra","Mukherjee","Nair","Nayak","Pande",
    "Patel","Pillai","Raj","Rao","Reddy","Saha","Sharma","Shukla","Singh",
    "Sinha","Srivastava","Tiwari","Trivedi","Varma","Yadav",
]

COURSES = [
    "B.Tech in Computer Science & Engineering",
    "B.Tech in Electronics & Communication Engineering",
    "B.Tech in Mechanical Engineering",
    "B.Tech in Civil Engineering",
    "B.Tech in Information Technology",
    "M.Tech in Data Science & AI",
    "M.Tech in VLSI Design",
    "MBA in Business Analytics",
    "BCA in Computer Applications",
    "MCA in Computer Applications",
    "B.Sc in Physics (Hons.)",
    "B.Sc in Mathematics (Hons.)",
]

CLASSES = ["First Class with Distinction", "First Class", "Second Class", "Third Class"]
CLASS_WEIGHTS = [0.25, 0.45, 0.20, 0.10]

UNIVERSITIES = [
    "Anna University", "VTU Karnataka", "Mumbai University",
    "Delhi University", "Pune University", "Osmania University",
    "Jadavpur University", "Calcutta University", "Madras University",
    "Rajasthan Technical University",
]

MONTHS = [
    "January","February","March","April","May","June",
    "July","August","September","October","November","December",
]


# ── Font helper ───────────────────────────────────────────────────────────────
def _get_font(size: int, bold: bool = False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "C:/Windows/Fonts/georgiab.ttf" if bold else "C:/Windows/Fonts/georgia.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def _jitter(base: int, amount: int = 8) -> int:
    return base + random.randint(-amount, amount)


def _random_data() -> dict:
    cgpa = round(random.uniform(5.0, 10.0), 2)
    cls  = random.choices(CLASSES, weights=CLASS_WEIGHTS, k=1)[0]
    yr   = random.randint(2010, 2025)
    mo   = random.choice(MONTHS)
    return {
        "name":      f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
        "reg_no":    f"{random.choice(['CS','EC','ME','CE','IT'])}{str(yr)[-2:]}{random.randint(1000,9999):04d}",
        "course":    random.choice(COURSES),
        "university":random.choice(UNIVERSITIES),
        "class":     cls,
        "cgpa":      f"{cgpa:.2f}",
        "month_year":f"{mo} {yr}",
        "cert_id":   f"CERT{random.randint(100000, 999999)}",
        "date":      f"{random.randint(1,28):02d}/{random.randint(1,12):02d}/{yr}",
    }


# ── Overlay engine ────────────────────────────────────────────────────────────
def overlay_fields(img: Image.Image, data: dict) -> Image.Image:
    """Overlay all certificate text fields with jitter onto the image."""
    img = img.copy().convert("RGB")
    draw = ImageDraw.Draw(img)
    W, H = img.size

    # Derive text colour from image brightness
    arr = np.array(img)
    mean_bright = arr.mean()
    txt_color   = (10, 10, 10) if mean_bright > 160 else (240, 235, 220)
    accent      = (90, 30, 10) if mean_bright > 160  else (220, 180, 80)

    # University name (top band)
    draw.text((_jitter(W//2), _jitter(55, 6)), data["university"],
              fill=accent, font=_get_font(18, bold=True), anchor="mm")

    # Certificate title
    draw.text((_jitter(W//2), _jitter(110, 6)), "CERTIFICATE OF COMPLETION",
              fill=txt_color, font=_get_font(22, bold=True), anchor="mm")

    # Presented to
    draw.text((_jitter(W//2), _jitter(170, 5)), "This is to certify that",
              fill=txt_color, font=_get_font(13), anchor="mm")

    # Student Name  ← biggest, most prominent
    draw.text((_jitter(W//2), _jitter(215, 8)), data["name"],
              fill=accent, font=_get_font(26, bold=True), anchor="mm")

    # Reg No
    draw.text((_jitter(W//2), _jitter(255, 6)),
              f"Registration No: {data['reg_no']}",
              fill=txt_color, font=_get_font(13), anchor="mm")

    # Course
    draw.text((_jitter(W//2), _jitter(290, 6)),
              f"has successfully completed  {data['course']}",
              fill=txt_color, font=_get_font(12), anchor="mm")

    # Class + CGPA
    draw.text((_jitter(W//2), _jitter(328, 6)),
              f"Class: {data['class']}     CGPA: {data['cgpa']} / 10.0",
              fill=txt_color, font=_get_font(13), anchor="mm")

    # Month-Year
    draw.text((_jitter(W//2), _jitter(364, 5)),
              f"Awarded in {data['month_year']}",
              fill=txt_color, font=_get_font(12), anchor="mm")

    # Cert ID
    draw.text((_jitter(60, 5), _jitter(H - 60, 5)),
              f"Cert ID: {data['cert_id']}", fill=txt_color, font=_get_font(10))

    # Date
    draw.text((_jitter(W - 130, 5), _jitter(H - 60, 5)),
              f"Date: {data['date']}", fill=txt_color, font=_get_font(10))

    return img


# ── Programmatic fallback templates ───────────────────────────────────────────
COLORS_BG = [
    (252, 248, 238), (240, 248, 255), (255, 252, 240),
    (245, 245, 222), (250, 250, 255),
]
BORDER_COLORS = [
    (130, 80, 20), (0, 70, 130), (110, 0, 0),
    (0, 90, 0),    (60, 60, 80),
]

def _make_programmatic_template(idx: int) -> Image.Image:
    bg  = COLORS_BG[idx % len(COLORS_BG)]
    bc  = BORDER_COLORS[idx % len(BORDER_COLORS)]
    img = Image.new("RGB", IMG_SIZE, bg)
    draw = ImageDraw.Draw(img)
    W, H = IMG_SIZE
    m = 18
    draw.rectangle([m, m, W-m, H-m], outline=bc, width=3)
    draw.rectangle([m+7, m+7, W-m-7, H-m-7], outline=bc, width=1)
    # Decorative corners
    for (cx, cy) in [(m+25, m+25), (W-m-25, m+25), (m+25, H-m-25), (W-m-25, H-m-25)]:
        draw.ellipse([cx-12, cy-12, cx+12, cy+12], outline=bc, width=2)
    return img


def load_templates() -> List[Image.Image]:
    """Load from templates/ dir; fall back to programmatic if empty."""
    tmpl_paths = (
        list(TEMPLATES_DIR.glob("*.jpg")) +
        list(TEMPLATES_DIR.glob("*.jpeg")) +
        list(TEMPLATES_DIR.glob("*.png"))
    )
    templates = []
    for p in tmpl_paths:
        try:
            img = Image.open(p).convert("RGB").resize(IMG_SIZE, Image.LANCZOS)
            templates.append(img)
        except Exception as e:
            print(f"  [WARN] Could not load template {p}: {e}")

    if not templates:
        print("  [INFO] No template images found — using 5 programmatic templates")
        templates = [_make_programmatic_template(i) for i in range(5)]

    print(f"  [TEMPLATES] Loaded {len(templates)} template(s)")
    return templates


# ── Main ──────────────────────────────────────────────────────────────────────
def generate_dataset(
    samples_per_train: int = SAMPLES_PER_TEMPLATE_TRAIN,
    samples_per_val:   int = SAMPLES_PER_TEMPLATE_VAL,
) -> None:
    templates = load_templates()

    for split, count in [("train", samples_per_train), ("val", samples_per_val)]:
        out_dir = OUTPUT_ROOT / split / "real"
        out_dir.mkdir(parents=True, exist_ok=True)

        total = 0
        for t_idx, tmpl in enumerate(templates):
            print(f"  [REAL/{split}] Template {t_idx+1}/{len(templates)} — {count} samples")
            for i in range(count):
                data = _random_data()
                img  = overlay_fields(tmpl, data)
                fname = f"real_{split}_t{t_idx:02d}_{i:04d}.jpg"
                img.save(out_dir / fname, "JPEG", quality=95)
                total += 1
            print(f"    Saved {count} → {out_dir}")

        print(f"[REAL] {split}: {total} images total")

    print("[DATASET] REAL generation complete.")


if __name__ == "__main__":
    generate_dataset()
