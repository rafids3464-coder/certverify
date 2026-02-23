"""
ocr.py - Tesseract OCR integration for certificate text extraction.

Extracts: university name, date, roll number.
Also validates text alignment and checks for spelling anomalies.
"""

import re
import logging
from typing import Optional

from PIL import Image
import pytesseract

logger = logging.getLogger(__name__)

# Common misspellings / anomaly patterns
SUSPICIOUS_PATTERNS = [
    r"\b0\s*(?=\d{3})\b",   # leading zero as letter O
    r"[|l]{3,}",             # runs of pipe / lowercase-l (OCR errors)
    r"\d{1,2}/\d{1,2}/\d{2}(?!\d)",  # 2-digit year that looks truncated
]

# Expected keywords that should appear in a valid certificate
EXPECTED_KEYWORDS = [
    "certif", "university", "college", "institute",
    "award", "complet", "degree", "diploma",
]

# Date patterns
DATE_PATTERNS = [
    r"\b\d{1,2}\s+(?:January|February|March|April|May|June|July|"
    r"August|September|October|November|December)[,\s]+\d{4}\b",
    r"\b\d{1,2}/\d{1,2}/\d{4}\b",
    r"\b\d{4}-\d{2}-\d{2}\b",
]

# Roll number patterns (alphanumeric IDs)
ROLL_PATTERNS = [
    r"\b[A-Z]{2,4}\d{2}\d{3,6}\b",
    r"\b\d{10,12}\b",
    r"\b[A-Z]{1,3}[-/]\d{4}[-/]\d{3,6}\b",
]


def extract_text(image_path: str) -> dict:
    """
    Run Tesseract OCR on the image and extract structured fields.

    Returns:
        {
            "raw_text":       full OCR text,
            "university":     extracted university name (str or ""),
            "date":           extracted date string (str or ""),
            "roll_number":    extracted roll number (str or ""),
            "is_valid_text":  bool — passes basic structural checks,
            "anomaly_flags":  list of detected anomaly strings,
        }
    """
    try:
        img = Image.open(image_path).convert("RGB")
    except Exception as e:
        logger.error(f"OCR: cannot open image {image_path}: {e}")
        return _empty_result(anomaly="image_load_error")

    # OCR with best-quality engine mode
    config = "--oem 3 --psm 6"
    try:
        raw = pytesseract.image_to_string(img, config=config)
    except Exception as e:
        logger.error(f"OCR failed: {e}")
        return _empty_result(anomaly="ocr_engine_error")

    result = {
        "raw_text":    raw.strip(),
        "university":  _extract_university(raw),
        "date":        _extract_date(raw),
        "roll_number": _extract_roll(raw),
        "is_valid_text": False,
        "anomaly_flags": [],
    }

    result["is_valid_text"], result["anomaly_flags"] = _validate_text(raw)
    logger.info(
        f"OCR | uni='{result['university']}' | "
        f"date='{result['date']}' | roll='{result['roll_number']}'"
    )
    return result


# ── Private helpers ───────────────────────────────────────────────────────────

def _empty_result(anomaly: str = "") -> dict:
    return {
        "raw_text": "",
        "university": "",
        "date": "",
        "roll_number": "",
        "is_valid_text": False,
        "anomaly_flags": [anomaly] if anomaly else [],
    }


def _extract_university(text: str) -> str:
    """Heuristically look for university/college name on first few lines."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for line in lines[:8]:  # usually in the header
        lower = line.lower()
        if any(kw in lower for kw in ["university", "college", "institute", "school", "iit", "nit"]):
            return line[:120]  # truncate for safety
    return ""


def _extract_date(text: str) -> str:
    """Extract a date string using regex patterns."""
    for pat in DATE_PATTERNS:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(0)
    return ""


def _extract_roll(text: str) -> str:
    """Extract a roll number / enrollment ID."""
    for pat in ROLL_PATTERNS:
        m = re.search(pat, text)
        if m:
            return m.group(0)
    return ""


def _validate_text(text: str) -> tuple:
    """
    Validate OCR text for structural integrity.

    Returns:
        (is_valid: bool, anomaly_flags: list[str])
    """
    flags = []
    lower = text.lower()

    # Check for expected keywords
    found_keywords = [kw for kw in EXPECTED_KEYWORDS if kw in lower]
    if len(found_keywords) < 2:
        flags.append("missing_certificate_keywords")

    # Check for suspicious patterns
    for pat in SUSPICIOUS_PATTERNS:
        if re.search(pat, text):
            flags.append(f"suspicious_pattern:{pat[:20]}")

    # Check text length (very short = suspicious)
    word_count = len(text.split())
    if word_count < 10:
        flags.append("too_short_text")

    # Check for excessive special characters (copy-paste artifacts)
    special_ratio = len(re.findall(r"[^a-zA-Z0-9\s.,:/\-]", text)) / max(len(text), 1)
    if special_ratio > 0.15:
        flags.append(f"high_special_char_ratio:{special_ratio:.2f}")

    is_valid = len(flags) == 0
    return is_valid, flags
