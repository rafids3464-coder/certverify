# ============================================================
# ML Container Dockerfile
# CUDA 11.8 + Python 3.10 on Ubuntu 22.04
# ============================================================

FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

LABEL maintainer="Fake Certificate Detection"
LABEL description="ML training & inference container"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# ── System dependencies ───────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 \
    python3-pip \
    python3.10-dev \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1-mesa-glx \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set python3.10 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1 \
    && update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

# ── Working directory ─────────────────────────────────────────────────────────
WORKDIR /app

# ── Python dependencies ───────────────────────────────────────────────────────
# Install torch with CUDA 11.8 first (separate index)
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

RUN pip install --no-cache-dir \
    torch==2.1.2+cu118 \
    torchvision==0.16.2+cu118 \
    torchaudio==2.1.2+cu118 \
    --index-url https://download.pytorch.org/whl/cu118

COPY requirements.txt /app/ml/requirements.txt
RUN pip install --no-cache-dir -r /app/ml/requirements.txt

# ── Copy ML source ────────────────────────────────────────────────────────────
COPY . /app/ml/

# ── Entrypoint ────────────────────────────────────────────────────────────────
RUN chmod +x /app/ml/entrypoint.sh

ENTRYPOINT ["/bin/bash", "/app/ml/entrypoint.sh"]
