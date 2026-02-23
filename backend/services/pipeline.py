"""
services/pipeline.py - Pipeline orchestration service for the FastAPI backend.
"""

import os
import logging
import tempfile

logger = logging.getLogger(__name__)


async def run_prediction(image_bytes: bytes, filename: str, content_type: str) -> dict:
    suffix = _get_suffix(filename, content_type)

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(image_bytes)
        tmp_path = tmp.name

    try:
        if suffix == ".pdf":
            tmp_path = _pdf_to_jpeg(tmp_path)

        # ✅ Local import from same folder
        from .predict import run_pipeline

        result = run_pipeline(tmp_path)
        result["filename"] = filename
        return result

    except FileNotFoundError:
        logger.error("model.pth not found")
        raise RuntimeError("ML model not ready.")

    except Exception as e:
        logger.exception(f"Pipeline error for {filename}: {e}")
        raise RuntimeError(f"Prediction pipeline failed: {e}")

    finally:
        _safe_remove(tmp_path)


def _get_suffix(filename: str, content_type: str) -> str:
    name_lower = filename.lower()
    if name_lower.endswith(".pdf") or "pdf" in content_type:
        return ".pdf"
    if name_lower.endswith(".png") or "png" in content_type:
        return ".png"
    return ".jpg"


def _pdf_to_jpeg(pdf_path: str) -> str:
    from pdf2image import convert_from_path

    pages = convert_from_path(pdf_path, dpi=200, first_page=1, last_page=1)
    if not pages:
        raise ValueError("Empty PDF")

    out_path = pdf_path.replace(".pdf", "_p1.jpg")
    pages[0].convert("RGB").save(out_path, "JPEG", quality=95)
    return out_path


def _safe_remove(path: str) -> None:
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass