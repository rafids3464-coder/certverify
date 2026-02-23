"""
routers/history.py — User upload history (JWT-protected).

GET /api/history  — returns authenticated user's past certificate uploads
"""

import logging
from fastapi import APIRouter, Depends
from middleware.auth import get_current_user
from db.mongo import get_user_history

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["history"])


@router.get("/history")
async def get_history(
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
):
    """Return the current user's upload history, newest first."""
    user_email = current_user["sub"]
    results    = await get_user_history(user_email, limit=min(limit, 200))
    logger.info(f"History requested by {user_email}: {len(results)} records")
    return {"count": len(results), "results": results}
