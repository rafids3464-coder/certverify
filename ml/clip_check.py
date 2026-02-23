"""
clip_check.py - CLIP-based image-text semantic similarity scoring.

Uses openai/clip-vit-base-patch32 (via HuggingFace transformers) to compute
cosine similarity between an image embedding and OCR-extracted text embedding.

A low similarity score suggests the image content doesn't semantically match
what a legitimate certificate should contain.
"""

import logging
from typing import Optional

import torch
import numpy as np
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

logger = logging.getLogger(__name__)

# ── Model singleton (loaded once) ─────────────────────────────────────────────

_clip_model: Optional[CLIPModel] = None
_clip_processor: Optional[CLIPProcessor] = None
_clip_device: Optional[torch.device] = None

MODEL_NAME = "openai/clip-vit-base-patch32"

# Reference text prompts that describe a genuine certificate
REAL_PROMPTS = [
    "a official university certificate or diploma document",
    "an academic award certificate with student name and university seal",
    "a formal certification document with official stamp",
]

FAKE_PROMPTS = [
    "a tampered or forged certificate document",
    "a fake diploma with suspicious marks and alterations",
]


def _load_clip(device: torch.device) -> None:
    """Load CLIP model and processor (cached after first call)."""
    global _clip_model, _clip_processor, _clip_device
    if _clip_model is None:
        logger.info(f"Loading CLIP model: {MODEL_NAME}")
        _clip_processor = CLIPProcessor.from_pretrained(MODEL_NAME)
        _clip_model = CLIPModel.from_pretrained(MODEL_NAME).to(device)
        _clip_model.eval()
        _clip_device = device
        logger.info("CLIP model loaded successfully")


def compute_clip_similarity(image_path: str, text: str, device: Optional[torch.device] = None) -> float:
    """
    Compute semantic similarity between the image and OCR text.

    Strategy:
    1. Encode the image.
    2. Encode the OCR text alongside reference real/fake prompts.
    3. Return cosine similarity of image embedding with the real-certificate
       text cluster, normalised as a 0–1 score.

    Args:
        image_path: path to the certificate image
        text:       OCR-extracted text from the certificate
        device:     torch device (auto-detected if None)

    Returns:
        float — similarity score where 1.0 = highly similar to a real cert
    """
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    try:
        _load_clip(device)
    except Exception as e:
        logger.error(f"CLIP load error: {e}")
        return 0.5  # neutral fallback

    try:
        img = Image.open(image_path).convert("RGB")
    except Exception as e:
        logger.error(f"CLIP: cannot open image {image_path}: {e}")
        return 0.5

    # Build text candidates
    # Combine OCR text with reference real/fake prompts for contrastive scoring
    ocr_text = text.strip() if text and len(text.strip()) > 5 else "certificate document"
    # Truncate OCR text to avoid CLIP token limit (77 tokens)
    ocr_text = " ".join(ocr_text.split()[:50])

    all_texts = [ocr_text] + REAL_PROMPTS + FAKE_PROMPTS

    try:
        with torch.no_grad():
            inputs = _clip_processor(
                text=all_texts,
                images=img,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=77,
            )
            inputs = {k: v.to(device) for k, v in inputs.items()}
            outputs = _clip_model(**inputs)

            # Normalised image embedding: (1, D)
            img_emb  = outputs.image_embeds / outputs.image_embeds.norm(dim=-1, keepdim=True)
            # Normalised text embeddings: (N, D)
            txt_emb  = outputs.text_embeds / outputs.text_embeds.norm(dim=-1, keepdim=True)

            # Cosine similarities: (1, N)
            sims = (img_emb @ txt_emb.T).squeeze(0).cpu().numpy()

            # sims[0]   = similarity with OCR text
            # sims[1:4] = similarity with real prompts
            # sims[4:]  = similarity with fake prompts

            real_score = float(np.mean(sims[1 : 1 + len(REAL_PROMPTS)]))
            fake_score = float(np.mean(sims[1 + len(REAL_PROMPTS) :]))
            ocr_score  = float(sims[0])

            # Combine: weight OCR similarity + real vs fake prompt gap
            gap = real_score - fake_score              # positive = looks real
            combined = 0.5 * ocr_score + 0.5 * (gap + 1.0) / 2.0  # map to 0–1
            similarity = float(np.clip(combined, 0.0, 1.0))

        logger.info(
            f"CLIP | ocr_sim={ocr_score:.3f} | real={real_score:.3f} "
            f"| fake={fake_score:.3f} | final={similarity:.3f}"
        )
        return similarity

    except Exception as e:
        logger.error(f"CLIP inference failed: {e}")
        return 0.5
