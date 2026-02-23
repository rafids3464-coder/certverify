"""
ela.py - Error Level Analysis (ELA) for tampering detection.

ELA reveals areas of an image that have been edited by comparing
the image with a JPEG-recompressed version of itself.
High error levels in unexpected areas indicate potential tampering.

Returns:
    - Tampering score (0.0 = clean, 1.0 = highly tampered)
    - Base64-encoded heatmap PNG
"""

import io
import base64
import logging
from typing import Tuple

import numpy as np
from PIL import Image, ImageEnhance
import cv2

logger = logging.getLogger(__name__)

# ELA compression quality — lower quality = larger diff for tampered regions
ELA_QUALITY   = 90
AMPLIFY_SCALE = 15   # amplification factor for visualizing differences
HEATMAP_SIZE  = (800, 600)


def compute_ela(image_path: str) -> Tuple[float, str]:
    """
    Run Error Level Analysis on the given image.

    Args:
        image_path: path to the input image (JPG or PNG)

    Returns:
        (score: float 0–1, heatmap_base64: str)
    """
    try:
        original = Image.open(image_path).convert("RGB")
    except Exception as e:
        logger.error(f"ELA: cannot open image {image_path}: {e}")
        return 0.5, _blank_heatmap()

    # Re-save at reduced quality to introduce JPEG quantisation
    buf = io.BytesIO()
    original.save(buf, format="JPEG", quality=ELA_QUALITY)
    buf.seek(0)
    recompressed = Image.open(buf).copy()

    # Compute absolute difference
    orig_arr  = np.asarray(original, dtype=np.float32)
    recomp_arr = np.asarray(recompressed, dtype=np.float32)
    diff_arr  = np.abs(orig_arr - recomp_arr)

    # Amplify for visualisation
    amplified = np.clip(diff_arr * AMPLIFY_SCALE, 0, 255).astype(np.uint8)

    # Compute tampering score: high-diff regions as fraction of image area
    # Use top 5% brightest pixels as "suspicious" regions
    gray_diff = amplified.mean(axis=2)            # (H, W)
    threshold = np.percentile(gray_diff, 95)
    suspicious_pixels = np.sum(gray_diff > threshold)
    total_pixels = gray_diff.size
    raw_score = suspicious_pixels / total_pixels  # 0–1

    # Normalise: a clean JPEG might have ~5% high-diff naturally,
    # so we scale relative to 20% = max expected tampering fraction
    score = float(np.clip(raw_score / 0.20, 0.0, 1.0))
    logger.info(f"ELA score: {score:.4f} (raw: {raw_score:.4f})")

    # Build a coloured heatmap using OpenCV's COLORMAP_JET
    heatmap_cv = cv2.applyColorMap(gray_diff.astype(np.uint8), cv2.COLORMAP_JET)
    heatmap_rgb = cv2.cvtColor(heatmap_cv, cv2.COLOR_BGR2RGB)
    heatmap_pil = Image.fromarray(heatmap_rgb).resize(HEATMAP_SIZE, Image.LANCZOS)

    # Blend heatmap with original for interpretability
    original_resized = original.resize(HEATMAP_SIZE, Image.LANCZOS)
    blended = Image.blend(original_resized, heatmap_pil, alpha=0.55)

    # Encode to base64 PNG
    out_buf = io.BytesIO()
    blended.save(out_buf, format="PNG")
    out_buf.seek(0)
    heatmap_b64 = base64.b64encode(out_buf.read()).decode("utf-8")

    return score, heatmap_b64


def _blank_heatmap() -> str:
    """Return a 1×1 transparent PNG as a safe fallback."""
    img = Image.new("RGB", (1, 1), (0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")
