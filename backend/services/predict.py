"""
predict.py - Full certificate authenticity prediction pipeline.

Combines:
  - CNN (EfficientNet-B0):  60% weight
  - CLIP similarity:        20% weight
  - ELA tampering score:    20% weight

Final score: 0.6 * CNN + 0.2 * CLIP + 0.2 * ELA
Returns a structured JSON-compatible dict.
"""

import sys
import logging
from pathlib import Path
from typing import Optional

import torch

# ── Path setup ────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent
MODEL_PATH = BASE_DIR.parent / "models" / "model.pth"
sys.path.insert(0, str(BASE_DIR))

from utils import get_device, load_image, get_inference_transform
from model import load_model
from ocr import extract_text
from ela import compute_ela
from clip_check import compute_clip_similarity

logger = logging.getLogger(__name__)

# ── Model cache (avoid reloading on every request) ────────────────────────────
_cnn_model = None
_device: Optional[torch.device] = None

CNN_WEIGHT   = 0.6
CLIP_WEIGHT  = 0.2
TAMPER_WEIGHT = 0.2
THRESHOLD    = 0.5   # scores >= 0.5 → REAL


def _get_cnn(device: torch.device):
    """Lazy-load the CNN model (thread-unsafe but adequate for single-worker)."""
    global _cnn_model
    if _cnn_model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"model.pth not found at {MODEL_PATH}. "
                "Run train.py to train the model first."
            )
        _cnn_model = load_model(str(MODEL_PATH), device)
        logger.info("CNN model loaded and cached")
    return _cnn_model


def _cnn_predict(image_path: str, device: torch.device) -> float:
    """
    Run the CNN and return a probability that the image is REAL (0–1).
    class_to_idx is usually {'fake': 0, 'real': 1} with ImageFolder.
    """
    model  = _get_cnn(device)
    tf     = get_inference_transform()
    img    = load_image(image_path)
    tensor = tf(img).unsqueeze(0).to(device)

    with torch.no_grad():
        logits = model(tensor)
        probs  = torch.softmax(logits, dim=1)
        # Index 1 corresponds to "real" (alphabetical ImageFolder ordering: fake=0, real=1)
        real_prob = probs[0, 1].item()

    logger.info(f"CNN | real_prob={real_prob:.4f}")
    return real_prob


def run_pipeline(image_path: str) -> dict:
    """
    Run the full multi-modal prediction pipeline.

    Args:
        image_path: absolute path to the image (JPG/PNG) — PDF must be pre-converted.

    Returns:
        {
            "prediction":  "REAL" | "FAKE",
            "confidence":  float (0–100 percentage),
            "cnn_score":   float (0–1),
            "clip_score":  float (0–1),
            "tamper_score": float (0–1),
            "ocr":         dict from extract_text(),
            "heatmap_b64": str (base64 PNG),
        }
    """
    global _device
    if _device is None:
        _device = get_device()
    device = _device

    logger.info(f"Pipeline started: {image_path}")

    # ── Step 1: CNN ───────────────────────────────────────────────────────────
    try:
        cnn_score = _cnn_predict(image_path, device)
    except FileNotFoundError as e:
        logger.error(str(e))
        raise
    except Exception as e:
        logger.error(f"CNN inference error: {e}")
        cnn_score = 0.5

    # ── Step 2: OCR ───────────────────────────────────────────────────────────
    try:
        ocr_result = extract_text(image_path)
    except Exception as e:
        logger.error(f"OCR error: {e}")
        ocr_result = {"raw_text": "", "university": "", "date": "",
                      "roll_number": "", "is_valid_text": False, "anomaly_flags": []}

    # ── Step 3: CLIP ──────────────────────────────────────────────────────────
    try:
        clip_score = compute_clip_similarity(
            image_path, ocr_result["raw_text"], device=device
        )
    except Exception as e:
        logger.error(f"CLIP error: {e}")
        clip_score = 0.5

    # ── Step 4: ELA ───────────────────────────────────────────────────────────
    try:
        ela_raw, heatmap_b64 = compute_ela(image_path)
        # Invert ELA: high tampering score → lower authenticity
        tamper_score = 1.0 - ela_raw
    except Exception as e:
        logger.error(f"ELA error: {e}")
        tamper_score = 0.5
        heatmap_b64  = ""

    # ── Step 5: Combined score ────────────────────────────────────────────────
    final_score = (
        CNN_WEIGHT    * cnn_score    +
        CLIP_WEIGHT   * clip_score   +
        TAMPER_WEIGHT * tamper_score
    )
    final_score = float(max(0.0, min(1.0, final_score)))

    prediction = "REAL" if final_score >= THRESHOLD else "FAKE"
    confidence = round(final_score * 100, 2)

    result = {
        "prediction":   prediction,
        "confidence":   confidence,
        "cnn_score":    round(cnn_score,    4),
        "clip_score":   round(clip_score,   4),
        "tamper_score": round(tamper_score, 4),
        "ocr":          ocr_result,
        "heatmap_b64":  heatmap_b64,
    }

    logger.info(
        f"Pipeline result: {prediction} | confidence={confidence:.2f}% | "
        f"CNN={cnn_score:.3f} | CLIP={clip_score:.3f} | Tamper={tamper_score:.3f}"
    )
    print(
        f"[PREDICTION] {prediction} | confidence={confidence:.2f}% | "
        f"CNN={cnn_score:.3f} | CLIP={clip_score:.3f} | Tamper={tamper_score:.3f}"
    )

    return result
