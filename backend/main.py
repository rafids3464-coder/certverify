"""
main.py — FastAPI application entrypoint (v2).

Adds: auth, history, admin routers.
Preserves: /api/upload, /api/health unchanged.
"""

import os
import sys
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── ML path setup ──────────────────────────────────────────────────────────────
ML_DIR = Path(__file__).parent.parent / "ml"
if ML_DIR.exists():
    sys.path.insert(0, str(ML_DIR))

BACKEND_DIR = Path(__file__).parent
sys.path.insert(0, str(BACKEND_DIR))


# ── Lifespan ───────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 60)
    logger.info("  CertVerify v2 — Starting Up")
    logger.info("=" * 60)

    # MongoDB check
    try:
        from db.mongo import ping_db, ensure_default_admin
        ok = await ping_db()
        logger.info(f"MongoDB: {'✔ connected' if ok else '⚠ not reachable'}")
        if ok:
            await ensure_default_admin()
    except Exception as e:
        logger.warning(f"DB startup check failed: {e}")

    # Model warm-up
    model_path = Path("/app/models/model.pth")
    if model_path.exists():
        try:
            from predict import _get_cnn
            import torch
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            _get_cnn(device)
            logger.info("✔ CNN model pre-loaded")
        except Exception as e:
            logger.warning(f"Model pre-load skipped: {e}")
    else:
        logger.warning("⚠ model.pth not found — training may still be running")

    logger.info("API ready.")
    yield
    logger.info("Shutting down.")


# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="CertVerify API v2",
    description="Fake Certificate Detection — CNN + CLIP + ELA + OCR + Auth",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ───────────────────────────────────────────────────────────────────────
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://frontend:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────
from routers.upload  import router as upload_router
from routers.auth    import router as auth_router
from routers.history import router as history_router
from routers.admin   import router as admin_router

app.include_router(upload_router)    # /api/upload  (unchanged, public)
app.include_router(auth_router)      # /auth/...
app.include_router(history_router)   # /api/history (protected)
app.include_router(admin_router)     # /admin/...   (admin JWT)


# ── Root ───────────────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {"service": "CertVerify API", "version": "2.0.0", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)),
                reload=False, log_level="info")
