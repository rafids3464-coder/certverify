"""
utils.py - Shared utilities for the ML pipeline.
Handles PDF → image conversion, normalization, and logging setup.
"""

import os
import io
import logging
import base64
from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image
import torch
import torchvision.transforms as T

# ── Logging ──────────────────────────────────────────────────────────────────

def setup_logging(level: str = "INFO") -> None:
    """Configure root logger with a clean format."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


# ── Image transforms ──────────────────────────────────────────────────────────

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]

def get_inference_transform() -> T.Compose:
    """Standard EfficientNet inference transform."""
    return T.Compose([
        T.Resize((224, 224)),
        T.ToTensor(),
        T.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


def get_train_transform() -> T.Compose:
    """Augmented training transform."""
    return T.Compose([
        T.Resize((256, 256)),
        T.RandomCrop(224),
        T.RandomHorizontalFlip(p=0.3),
        T.RandomVerticalFlip(p=0.1),
        T.RandomRotation(degrees=10),
        T.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2),
        T.ToTensor(),
        T.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


# ── PDF → Image ───────────────────────────────────────────────────────────────

def pdf_to_image(pdf_path: str, dpi: int = 200) -> Image.Image:
    """
    Convert the first page of a PDF to a PIL Image.
    Requires poppler to be installed.
    """
    try:
        from pdf2image import convert_from_path
        pages = convert_from_path(pdf_path, dpi=dpi, first_page=1, last_page=1)
        if not pages:
            raise ValueError(f"No pages found in PDF: {pdf_path}")
        return pages[0].convert("RGB")
    except ImportError:
        raise RuntimeError("pdf2image not installed. Run: pip install pdf2image")
    except Exception as e:
        raise RuntimeError(f"PDF conversion failed: {e}")


# ── File helpers ──────────────────────────────────────────────────────────────

def load_image(path: str) -> Image.Image:
    """Load image from path, auto-converting PDF if needed."""
    ext = Path(path).suffix.lower()
    if ext == ".pdf":
        return pdf_to_image(path)
    img = Image.open(path).convert("RGB")
    return img


def image_to_base64(img: Image.Image, fmt: str = "PNG") -> str:
    """Encode a PIL Image to a base64 string."""
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def base64_to_image(b64: str) -> Image.Image:
    """Decode a base64 string to a PIL Image."""
    data = base64.b64decode(b64)
    return Image.open(io.BytesIO(data)).convert("RGB")


# ── Device ────────────────────────────────────────────────────────────────────

def get_device() -> torch.device:
    """Return the best available compute device."""
    if torch.cuda.is_available():
        device = torch.device("cuda")
        gpu_name = torch.cuda.get_device_name(0)
        vram = torch.cuda.get_device_properties(0).total_memory / 1e9
        logging.getLogger(__name__).info(
            f"Using GPU: {gpu_name} ({vram:.1f} GB VRAM)"
        )
    else:
        device = torch.device("cpu")
        logging.getLogger(__name__).warning("CUDA not available — using CPU")
    return device
