"""
routers/auth.py — Authentication endpoints.

POST /auth/signup       — create new user account
POST /auth/login        — user login → JWT
POST /auth/admin/login  — admin login → JWT
"""

import os
import logging
from fastapi import APIRouter, HTTPException, status

from models.user import UserCreate, UserLogin, AdminLogin, TokenResponse
from db.mongo import (
    create_user, get_user_by_email,
    create_admin, get_admin_by_username,
    ensure_default_admin,
)
from middleware.auth import hash_password, verify_password, create_token

logger  = logging.getLogger(__name__)
router  = APIRouter(prefix="/auth", tags=["authentication"])


# ── User signup ────────────────────────────────────────────────────────────────

@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserCreate):
    """Register a new user account. Returns a JWT on success."""
    existing = await get_user_by_email(body.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )
    hashed = hash_password(body.password)
    await create_user({
        "name":     body.name,
        "email":    body.email,
        "password": hashed,
        "role":     "user",
        "disabled": False,
    })
    token = create_token(sub=body.email, role="user", name=body.name)
    logger.info(f"New user registered: {body.email}")
    return TokenResponse(access_token=token, role="user", name=body.name)


# ── User login ─────────────────────────────────────────────────────────────────

@router.post("/login", response_model=TokenResponse)
async def login(body: UserLogin):
    """Authenticate a user and return a JWT."""
    user = await get_user_by_email(body.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid email or password.")
    if user.get("disabled"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Your account has been disabled.")
    if not verify_password(body.password, user["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid email or password.")

    token = create_token(sub=body.email, role="user", name=user["name"])
    logger.info(f"User logged in: {body.email}")
    return TokenResponse(access_token=token, role="user", name=user["name"])


# ── Admin login ────────────────────────────────────────────────────────────────

@router.post("/admin/login", response_model=TokenResponse)
async def admin_login(body: AdminLogin):
    """Authenticate an admin and return an admin JWT."""
    # Ensure default admin exists (seed on first call)
    await ensure_default_admin()

    admin = await get_admin_by_username(body.username)
    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid username or password.")
    if not verify_password(body.password, admin["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid username or password.")

    token = create_token(sub=body.username, role="admin", name=body.username)
    logger.info(f"Admin logged in: {body.username}")
    return TokenResponse(access_token=token, role="admin", name=body.username)
