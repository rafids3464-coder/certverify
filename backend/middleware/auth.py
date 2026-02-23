"""
middleware/auth.py — JWT creation, decoding, password hashing, and FastAPI dependencies.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

JWT_SECRET = os.getenv("JWT_SECRET", "certverify-super-secret-change-in-prod")
ALGORITHM = "HS256"
ACCESS_EXPIRE = timedelta(hours=24)

# 🔥 FIX: use bcrypt_sha256 (no 72 byte limit issue)
pwd_ctx = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")
bearer_ = HTTPBearer(auto_error=False)


# ─────────────────────────────────────────────
# PASSWORD HELPERS
# ─────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return pwd_ctx.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain, hashed)


# ─────────────────────────────────────────────
# JWT HELPERS
# ─────────────────────────────────────────────

def create_token(sub: str, role: str, name: str) -> str:
    expire = datetime.utcnow() + ACCESS_EXPIRE
    payload = {
        "sub": sub,
        "role": role,
        "name": name,
        "exp": expire,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ─────────────────────────────────────────────
# FASTAPI DEPENDENCIES
# ─────────────────────────────────────────────

def _extract_token(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer_)
) -> str:
    if creds is None or not creds.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Provide a Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return creds.credentials


def get_current_user(token: str = Depends(_extract_token)) -> dict:
    return decode_token(token)


def require_admin(token: str = Depends(_extract_token)) -> dict:
    payload = decode_token(token)
    if payload.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )
    return payload