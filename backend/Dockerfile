# ============================================================
# CertVerify v2 — FastAPI Backend Dockerfile
# Python 3.10 + Tesseract + Poppler + CPU Torch
# ============================================================

FROM python:3.10-slim-bullseye

LABEL maintainer="CertVerify"
LABEL description="FastAPI backend with ML + OCR support"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# ────────────────────────────────────────────────────────────
# System Dependencies
# ────────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ────────────────────────────────────────────────────────────
# Working Directory
# ────────────────────────────────────────────────────────────
WORKDIR /app

# ────────────────────────────────────────────────────────────
# Upgrade pip
# ────────────────────────────────────────────────────────────
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# ────────────────────────────────────────────────────────────
# Install CPU PyTorch (backend inference only)
# ────────────────────────────────────────────────────────────
RUN pip install --no-cache-dir \
    torch==2.1.2+cpu \
    torchvision==0.16.2+cpu \
    --index-url https://download.pytorch.org/whl/cpu

# ────────────────────────────────────────────────────────────
# Install Remaining Python Dependencies
# ────────────────────────────────────────────────────────────
COPY requirements.txt /tmp/requirements.txt

# Remove torch + torchvision from requirements (already installed)
RUN grep -v "^torch" /tmp/requirements.txt | \
    grep -v "^torchvision" > /tmp/requirements_filtered.txt && \
    pip install --no-cache-dir -r /tmp/requirements_filtered.txt

# ────────────────────────────────────────────────────────────
# Copy Backend Source
# ────────────────────────────────────────────────────────────
COPY . /app

# ────────────────────────────────────────────────────────────
# Expose Port
# ────────────────────────────────────────────────────────────
EXPOSE 8000

# ────────────────────────────────────────────────────────────
# Start FastAPI
# ────────────────────────────────────────────────────────────
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]