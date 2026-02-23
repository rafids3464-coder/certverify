"""
routers/admin.py — Admin-only endpoints (require admin JWT).

GET    /admin/uploads          — all uploaded certificates
GET    /admin/metrics          — model + dataset stats
DELETE /admin/upload/{id}      — delete a result record
POST   /admin/disable-user     — disable a user account
POST   /admin/retrain          — trigger ML retraining subprocess
GET    /admin/logs             — last N system log lines
GET    /admin/users            — list all users
"""

import os
import subprocess
import logging
import asyncio
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from middleware.auth import require_admin
from db.mongo import (
    get_all_results, delete_result_by_id,
    disable_user, get_all_users,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])

DATASET_ROOT = Path("/app/ml/dataset")
MODEL_PATH   = Path("/app/models/model.pth")
LOG_FILE     = Path("/tmp/certverify.log")

# Retrain lock — prevent concurrent retraining
_retrain_running = False


# ── Models ─────────────────────────────────────────────────────────────────────
class DisableUserRequest(BaseModel):
    email: str


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.get("/uploads")
async def get_all_uploads(
    limit: int = 100,
    _admin = Depends(require_admin),
):
    """Return all certificate analysis records (newest first)."""
    results = await get_all_results(limit=min(limit, 500))
    return {"count": len(results), "results": results}


@router.get("/users")
async def list_users(_admin = Depends(require_admin)):
    """Return all registered user accounts."""
    users = await get_all_users()
    return {"count": len(users), "users": users}


@router.get("/metrics")
async def get_metrics(_admin = Depends(require_admin)):
    """Return model file stats and dataset image counts."""
    # Dataset counts
    def count_dir(path: Path) -> int:
        if not path.exists():
            return 0
        return sum(1 for f in path.rglob("*") if f.suffix.lower() in {".jpg", ".jpeg", ".png"})

    train_real = count_dir(DATASET_ROOT / "train" / "real")
    train_fake = count_dir(DATASET_ROOT / "train" / "fake")
    val_real   = count_dir(DATASET_ROOT / "val"   / "real")
    val_fake   = count_dir(DATASET_ROOT / "val"   / "fake")

    model_info = {}
    if MODEL_PATH.exists():
        stat = MODEL_PATH.stat()
        model_info = {
            "exists":       True,
            "size_mb":      round(stat.st_size / 1e6, 2),
            "last_modified": stat.st_mtime,
        }
    else:
        model_info = {"exists": False}

    return {
        "dataset": {
            "train_real": train_real,
            "train_fake": train_fake,
            "val_real":   val_real,
            "val_fake":   val_fake,
            "total":      train_real + train_fake + val_real + val_fake,
        },
        "model": model_info,
    }


@router.delete("/upload/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_upload(record_id: str, _admin = Depends(require_admin)):
    """Delete an analysis record by its MongoDB ObjectId string."""
    deleted = await delete_result_by_id(record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Record not found.")


@router.post("/disable-user")
async def disable_user_account(
    body: DisableUserRequest,
    _admin = Depends(require_admin),
):
    """Disable a user account by email."""
    updated = await disable_user(body.email)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"message": f"User {body.email} has been disabled."}


@router.post("/retrain")
async def trigger_retrain(_admin = Depends(require_admin)):
    """Spawn a background retraining subprocess."""
    global _retrain_running
    if _retrain_running:
        raise HTTPException(status_code=409, detail="Retraining is already in progress.")
    _retrain_running = True

    async def _run():
        global _retrain_running
        try:
            logger.info("Admin triggered retraining…")
            proc = await asyncio.create_subprocess_exec(
                "python", "/app/ml/train.py",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            stdout, _ = await proc.communicate()
            logger.info(f"Retrain exit code: {proc.returncode}")
            LOG_FILE.write_text(stdout.decode(errors="replace") if stdout else "")
        except Exception as e:
            logger.error(f"Retrain error: {e}")
        finally:
            _retrain_running = False

    asyncio.create_task(_run())
    return {"message": "Retraining started in background. Check /admin/logs for progress."}


@router.get("/retrain/status")
async def retrain_status(_admin = Depends(require_admin)):
    return {"running": _retrain_running}


@router.get("/logs")
async def get_logs(lines: int = 100, _admin = Depends(require_admin)):
    """Return the last N lines of the most recent retrain log."""
    if LOG_FILE.exists():
        all_lines = LOG_FILE.read_text(errors="replace").splitlines()
        return {"lines": all_lines[-min(lines, 500):]}
    return {"lines": ["No log file found. Trigger retraining first."]}
