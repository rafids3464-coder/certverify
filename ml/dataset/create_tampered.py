"""
create_tampered.py — Multi-Fake Generator (v2)

For EACH REAL image generates 3–5 FAKE variants using 5 distinct forgery types:
  Type 1: Data Modification   — changed CGPA/class via text overlay
  Type 2: Font Inconsistency  — mismatched font + misalignment on one field
  Type 3: Copy-Paste Artifact — opaque patch + local Gaussian blur
  Type 4: Seal Manipulation   — HSV colour shift + partial occlusion
  Type 5: Perspective Tamper  — cv2 slight skew + local warp

Target: REAL:FAKE ≈ 1:3–4 (≥10,000 total images)
"""

import os
import io
import random
from pathlib import Path
from typing import Callable

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cv2

# ── Paths ──────────────────────────────────────────────────────────────────────
DATASET_ROOT = Path(__file__).parent.parent / "dataset"

REAL_DIRS = {
    "train": DATASET_ROOT / "train" / "real",
    "val":   DATASET_ROOT / "val"   / "real",
}
FAKE_DIRS = {
    "train": DATASET_ROOT / "train" / "fake",
    "val":   DATASET_ROOT / "val"   / "fake",
}

FAKES_PER_REAL_MIN = 3
FAKES_PER_REAL_MAX = 5


# ── Helpers ────────────────────────────────────────────────────────────────────
def _get_font(size: int, monospace: bool = False):
    candidates = [
        "C:/Windows/Fonts/cour.ttf" if monospace else "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf" if monospace else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeMono.ttf" if monospace else
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def _white_block(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int):
    """Paint a white rectangle to erase existing text."""
    draw.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))


# ── Forgery type implementations ───────────────────────────────────────────────

def fake_data_modification(img: Image.Image) -> Image.Image:
    """
    Type 1 — Data Modification
    Over-paint the CGPA field area with a falsified value,
    and change the declared class from higher to lower (or vice versa).
    """
    img  = img.copy()
    draw = ImageDraw.Draw(img)
    W, H = img.size
    font = _get_font(13)

    # Erase CGPA region (approximate position from overlay engine)
    y_cgpa = int(H * 0.64)
    _white_block(draw, W//2 - 200, y_cgpa - 14, 400, 28)

    # Write fake data
    fake_cgpa  = round(random.uniform(5.0, 10.0), 2)
    fake_class = random.choice(["First Class with Distinction", "Third Class",
                                 "Second Class", "Pass Class"])
    draw.text((W//2, y_cgpa), f"Class: {fake_class}     CGPA: {fake_cgpa:.2f} / 10.0",
              fill=(0, 0, 0), font=font, anchor="mm")
    return img


def fake_font_inconsistency(img: Image.Image) -> Image.Image:
    """
    Type 2 — Font Inconsistency
    Replace the course title with a monospace font + slight positional misalignment.
    """
    img  = img.copy()
    draw = ImageDraw.Draw(img)
    W, H = img.size
    mono_font = _get_font(12, monospace=True)

    y_course = int(H * 0.57)
    misalign = random.randint(-12, 12)    # horizontal misalignment
    _white_block(draw, 20, y_course - 14, W - 40, 28)

    courses = [
        "B.Tech Computer Science (TAMPERED)",
        "M.Tech Data Engineering",
        "MBA Finance [MODIFIED]",
    ]
    draw.text((W//2 + misalign, y_course + random.randint(-4, 4)),
              f"has successfully completed  {random.choice(courses)}",
              fill=(30, 30, 30), font=mono_font, anchor="mm")
    return img


def fake_copy_paste_artifact(img: Image.Image) -> Image.Image:
    """
    Type 3 — Copy-Paste Artifact
    Paste a slightly colour-shifted patch from elsewhere in the image,
    then blur the signature-area region.
    """
    img   = img.copy()
    W, H  = img.size
    arr   = np.array(img)

    # Random source region (top-left quadrant)
    sx = random.randint(0, W//3)
    sy = random.randint(0, H//3)
    pw = random.randint(60, 140)
    ph = random.randint(40, 100)
    patch = arr[sy:sy+ph, sx:sx+pw].copy()

    # Colour-shift (subtle hue drift)
    patch[:, :, 0] = np.clip(patch[:, :, 0].astype(int) + random.randint(-30, 30), 0, 255)

    # Destination: mid or lower region
    dx = random.randint(W//3, W - pw - 10)
    dy = random.randint(H//2, H - ph - 40)
    arr[dy:dy+ph, dx:dx+pw] = patch

    result  = Image.fromarray(arr)
    # Blur the signature area (bottom strip)
    sig_box = (40, H - 130, W - 40, H - 40)
    sig_region = result.crop(sig_box).filter(ImageFilter.GaussianBlur(radius=4))
    result.paste(sig_region, sig_box)
    return result


def fake_seal_manipulation(img: Image.Image) -> Image.Image:
    """
    Type 4 — Seal Manipulation
    Shift the hue of the lower-right corner (where seal typically lives)
    and partially occlude it with a semi-transparent rectangle.
    """
    img  = img.copy()
    W, H = img.size

    # HSV colour shift on the seal region
    arr = np.array(img)
    # Seal area: bottom-right quadrant
    ry1, ry2 = int(H * 0.65), H
    rx1, rx2 = int(W * 0.65), W
    seal_region_bgr = cv2.cvtColor(arr[ry1:ry2, rx1:rx2], cv2.COLOR_RGB2HSV)
    seal_region_bgr[:, :, 0] = (seal_region_bgr[:, :, 0].astype(int) +
                                  random.randint(20, 60)) % 180
    arr[ry1:ry2, rx1:rx2] = cv2.cvtColor(seal_region_bgr, cv2.COLOR_HSV2RGB)
    result = Image.fromarray(arr)

    # Partial occlusion: semi-transparent white rectangle
    overlay = Image.new("RGBA", result.size, (0, 0, 0, 0))
    odraw   = ImageDraw.Draw(overlay)
    ox = random.randint(rx1, rx1 + 60)
    oy = random.randint(ry1, ry1 + 60)
    odraw.rectangle([ox, oy, ox + random.randint(40, 80), oy + random.randint(30, 60)],
                    fill=(255, 255, 255, 140))
    result = Image.alpha_composite(result.convert("RGBA"), overlay).convert("RGB")
    return result


def fake_perspective_tamper(img: Image.Image) -> Image.Image:
    """
    Type 5 — Perspective Tamper
    Apply a mild perspective warp (simulating a re-scanned cropped forgery).
    """
    arr  = np.array(img)
    H, W = arr.shape[:2]

    jit = random.randint(8, 22)
    src = np.float32([[0, 0], [W, 0], [W, H], [0, H]])
    # Shift corners slightly
    dst = np.float32([
        [random.randint(-jit, jit),  random.randint(-jit, jit)],
        [W + random.randint(-jit, jit), random.randint(-jit, jit)],
        [W + random.randint(-jit, jit), H + random.randint(-jit, jit)],
        [random.randint(-jit, jit),  H + random.randint(-jit, jit)],
    ])
    M   = cv2.getPerspectiveTransform(src, dst)
    out = cv2.warpPerspective(arr, M, (W, H), borderMode=cv2.BORDER_REPLICATE)
    return Image.fromarray(out)


FAKE_TYPES: list = [
    fake_data_modification,
    fake_font_inconsistency,
    fake_copy_paste_artifact,
    fake_seal_manipulation,
    fake_perspective_tamper,
]


def generate_fakes_for_image(src: Image.Image, count: int) -> list:
    """Apply `count` distinct fake types to the source image."""
    selected = random.sample(FAKE_TYPES, min(count, len(FAKE_TYPES)))
    results  = []
    for fn in selected:
        try:
            results.append(fn(src))
        except Exception as e:
            print(f"    [WARN] {fn.__name__} failed: {e}")
    return results


# ── Main ──────────────────────────────────────────────────────────────────────

def generate_tampered_dataset() -> None:
    for split in ["train", "val"]:
        real_dir = REAL_DIRS[split]
        fake_dir = FAKE_DIRS[split]
        fake_dir.mkdir(parents=True, exist_ok=True)

        real_files = (
            list(real_dir.glob("*.jpg")) +
            list(real_dir.glob("*.jpeg")) +
            list(real_dir.glob("*.png"))
        )
        if not real_files:
            print(f"  [WARN] No real images found in {real_dir}")
            continue

        print(f"\n[FAKE/{split}] Generating fakes from {len(real_files)} real images…")
        total_fakes = 0

        for idx, src_path in enumerate(real_files):
            try:
                src = Image.open(src_path).convert("RGB")
            except Exception as e:
                print(f"  [ERROR] {src_path.name}: {e}")
                continue

            n_fakes = random.randint(FAKES_PER_REAL_MIN, FAKES_PER_REAL_MAX)
            fakes   = generate_fakes_for_image(src, n_fakes)

            for f_idx, fake_img in enumerate(fakes):
                stem  = src_path.stem
                fname = f"fake_{split}_{stem}_f{f_idx}.jpg"
                fake_img.save(fake_dir / fname, "JPEG", quality=90)
                total_fakes += 1

            if (idx + 1) % 200 == 0:
                print(f"    Processed {idx + 1}/{len(real_files)} real → {total_fakes} fakes so far")

        print(f"  [FAKE/{split}] Done: {total_fakes} fake images created")

    print("\n[DATASET] FAKE generation complete.")


if __name__ == "__main__":
    generate_tampered_dataset()
