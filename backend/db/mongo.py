"""
db/mongo.py — Async MongoDB layer (v2).

Extended with: user CRUD, admin seed, history, upload user-tagging.
Retains original save_result / get_results / ping_db for backward compat.
"""

import os
import logging
from typing import Optional
from datetime import datetime

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import DESCENDING

from middleware.auth import hash_password

logger = logging.getLogger(__name__)

# ── Connection ─────────────────────────────────────────────────────────────────
MONGO_URI   = os.getenv("MONGO_URI",   "mongodb://mongodb:27017")
DB_NAME     = os.getenv("MONGO_DB_NAME", "certdb")
ADMIN_USER  = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASS  = os.getenv("ADMIN_PASSWORD", "Admin@1234")

_client: Optional[AsyncIOMotorClient] = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        logger.info(f"MongoDB client: {MONGO_URI}")
    return _client


def _col(name: str):
    return get_client()[DB_NAME][name]


# ── Results (backward-compatible) ─────────────────────────────────────────────

async def save_result(doc: dict) -> str:
    doc.setdefault("timestamp", datetime.utcnow())
    res = await _col("results").insert_one(doc)
    return str(res.inserted_id)


async def get_results(limit: int = 50) -> list:
    cursor = _col("results").find({}, {"_id": 0}).sort("timestamp", DESCENDING).limit(limit)
    return await cursor.to_list(length=limit)


async def get_all_results(limit: int = 100) -> list:
    cursor = _col("results").find({}).sort("timestamp", DESCENDING).limit(limit)
    raw = await cursor.to_list(length=limit)
    for doc in raw:
        doc["_id"] = str(doc["_id"])
    return raw


async def delete_result_by_id(record_id: str) -> bool:
    try:
        res = await _col("results").delete_one({"_id": ObjectId(record_id)})
        return res.deleted_count > 0
    except Exception:
        return False


async def ping_db() -> bool:
    try:
        await get_client().admin.command("ping")
        return True
    except Exception as e:
        logger.error(f"MongoDB ping failed: {e}")
        return False


# ── User CRUD ──────────────────────────────────────────────────────────────────

async def create_user(doc: dict) -> str:
    doc.setdefault("created_at", datetime.utcnow())
    res = await _col("users").insert_one(doc)
    return str(res.inserted_id)


async def get_user_by_email(email: str) -> Optional[dict]:
    return await _col("users").find_one({"email": email})


async def get_all_users() -> list:
    cursor = _col("users").find({}, {"password": 0, "_id": 0}).sort("created_at", DESCENDING)
    return await cursor.to_list(length=500)


async def disable_user(email: str) -> bool:
    res = await _col("users").update_one(
        {"email": email}, {"$set": {"disabled": True}}
    )
    return res.modified_count > 0


# ── User history ───────────────────────────────────────────────────────────────

async def get_user_history(user_email: str, limit: int = 50) -> list:
    """Return results linked to a specific user email."""
    cursor = (
        _col("results")
        .find({"user_email": user_email}, {"_id": 0})
        .sort("timestamp", DESCENDING)
        .limit(limit)
    )
    return await cursor.to_list(length=limit)


# ── Admin CRUD ─────────────────────────────────────────────────────────────────

async def create_admin(doc: dict) -> str:
    doc.setdefault("created_at", datetime.utcnow())
    res = await _col("admins").insert_one(doc)
    return str(res.inserted_id)


async def get_admin_by_username(username: str) -> Optional[dict]:
    return await _col("admins").find_one({"username": username})


async def ensure_default_admin() -> None:
    """Seed a default admin account from env vars on first startup."""
    existing = await get_admin_by_username(ADMIN_USER)
    if not existing:
        await create_admin({
            "username": ADMIN_USER,
            "password": hash_password(ADMIN_PASS),
            "role":     "admin",
        })
        logger.info(f"Default admin seeded: {ADMIN_USER}")
