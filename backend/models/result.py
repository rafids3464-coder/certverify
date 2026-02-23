"""
models/result.py - Pydantic models for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class OCRResult(BaseModel):
    """Structured OCR extraction output."""
    raw_text:      str = ""
    university:    str = ""
    date:          str = ""
    roll_number:   str = ""
    is_valid_text: bool = False
    anomaly_flags: List[str] = []


class PredictionResponse(BaseModel):
    """Full pipeline prediction response."""
    prediction:   str   = Field(..., description="REAL or FAKE")
    confidence:   float = Field(..., ge=0.0, le=100.0, description="Confidence percentage")
    cnn_score:    float = Field(..., ge=0.0, le=1.0)
    clip_score:   float = Field(..., ge=0.0, le=1.0)
    tamper_score: float = Field(..., ge=0.0, le=1.0)
    ocr:          OCRResult
    heatmap_b64:  str   = Field("", description="Base64-encoded ELA heatmap PNG")
    filename:     str   = ""
    timestamp:    datetime = Field(default_factory=datetime.utcnow)


class UploadResult(BaseModel):
    """MongoDB-stored result document."""
    filename:     str
    prediction:   str
    confidence:   float
    cnn_score:    float
    clip_score:   float
    tamper_score: float
    timestamp:    datetime = Field(default_factory=datetime.utcnow)
