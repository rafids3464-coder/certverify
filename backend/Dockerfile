# ============================================================
# CertVerify v2 — FastAPI Backend Dockerfile
# ============================================================

FROM python:3.10-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# System dependencies
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

# Set working directory
WORKDIR /app

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install CPU PyTorch
RUN pip install --no-cache-dir \
    torch==2.1.2+cpu \
    torchvision==0.16.2+cpu \
    --index-url https://download.pytorch.org/whl/cpu

# Copy only requirements first
COPY backend/requirements.txt ./backend/requirements.txt

# Install Python dependencies
RUN grep -v "^torch" backend/requirements.txt | \
    grep -v "^torchvision" > /tmp/requirements.txt && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# Copy entire project
COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
