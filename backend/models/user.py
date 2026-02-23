"""
models/user.py — User and Admin Pydantic schemas for auth system.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal
from datetime import datetime


class UserCreate(BaseModel):
    name:     str = Field(..., min_length=2, max_length=80)
    email:    str = Field(..., description="User email")
    password: str = Field(..., min_length=6, max_length=128)


class UserLogin(BaseModel):
    email:    str
    password: str


class AdminLogin(BaseModel):
    username: str
    password: str


class UserInDB(BaseModel):
    id:         Optional[str] = None
    name:       str
    email:      str
    role:       Literal["user"] = "user"
    disabled:   bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AdminInDB(BaseModel):
    id:         Optional[str] = None
    username:   str
    role:       Literal["admin"] = "admin"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    role:         str
    name:         str


class TokenPayload(BaseModel):
    sub:  str          # user email or admin username
    role: str          # "user" or "admin"
    name: str
    exp:  Optional[int] = None
