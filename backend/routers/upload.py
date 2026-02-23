"""
routers/upload.py - POST /upload endpoint for certificate authenticity analysis.
Public endpoint — JWT is optional (used to tag result for history tracking).
"""

import logging
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends
from fastapi.responses import JSONResponse

from models.result import PredictionResponse, OCRResult
from services.pipeline import run_prediction
from db.mongo import save_result

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["upload"])

MAX_FILE_SIZE      = 20 * 1024 * 1024
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}

# Optional bearer — won't reject unauthenticated requests
_optional_bearer = HTTPBearer(auto_error=False)


def _try_get_email(creds: Optional[HTTPAuthorizationCredentials]) -> Optional[str]:
    """Decode JWT if present; return user email or None."""
    if not creds:
        return None
    try:
        from middleware.auth import decode_token
        payload = decode_token(creds.credentials)
        if payload.get("role") == "user":
            return payload.get("sub")
    except Exception:
        pass
    return None


@router.post("/upload", response_model=PredictionResponse)
async def upload_certificate(
    file: UploadFile = File(...),
    creds: Optional[HTTPAuthorizationCredentials] = Depends(_optional_bearer),
):
    """
    Upload a certificate image or PDF for authenticity analysis.
    JWT is optional — if provided, result is stored under the user's history.
    """
    filename = file.filename or "unknown"
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{ext}'. Allowed: {ALLOWED_EXTENSIONS}"
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({len(content) / 1e6:.1f} MB). Max 20 MB."
        )
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    logger.info(f"Upload: {filename} ({len(content) / 1024:.1f} KB)")

    try:
        result = await run_prediction(
            image_bytes=content,
            filename=filename,
            content_type=file.content_type or "",
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.exception(f"Pipeline error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")

    # Persist — optionally link to user
    user_email = _try_get_email(creds)
    try:
        mongo_doc = {
            "filename":     result["filename"],
            "prediction":   result["prediction"],
            "confidence":   result["confidence"],
            "cnn_score":    result["cnn_score"],
            "clip_score":   result["clip_score"],
            "tamper_score": result["tamper_score"],
            "heatmap_b64":  result.get("heatmap_b64", ""),
        }
        if user_email:
            mongo_doc["user_email"] = user_email
        await save_result(mongo_doc)
    except Exception as e:
        logger.warning(f"MongoDB save failed (non-critical): {e}")

    ocr_data = result.get("ocr", {})
    response = PredictionResponse(
        prediction=result["prediction"],
        confidence=result["confidence"],
        cnn_score=result["cnn_score"],
        clip_score=result["clip_score"],
        tamper_score=result["tamper_score"],
        ocr=OCRResult(**ocr_data),
        heatmap_b64=result.get("heatmap_b64", ""),
        filename=filename,
    )

    logger.info(
        f"[PREDICTION] {response.prediction} ({response.confidence:.1f}%) | "
        f"user={user_email or 'anonymous'} | {filename}"
    )
    return response


@router.get("/health")
async def health_check():
    """Quick health check endpoint."""
    from db.mongo import ping_db
    db_ok = await ping_db()
    return {"status": "ok", "mongodb": "connected" if db_ok else "disconnected"}


@router.get("/results")
async def get_recent_results(limit: int = 20):
    """Retrieve recent analysis results from the database."""
    from db.mongo import get_results
    results = await get_results(limit=min(limit, 100))
    return {"count": len(results), "results": results}
