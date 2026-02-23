# CertVerify — Fake Certificate Detection

An AI-powered web application for detecting forged and tampered certificates using a multi-modal pipeline combining deep learning, semantic analysis, and forensic tampering detection.

---

## Architecture Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌───────────────┐
│   Next.js       │────▶│   FastAPI        │────▶│   ML Pipeline │
│   Frontend      │◀────│   Backend        │◀────│   (GPU)       │
│   :3000         │     │   :8000          │     │               │
└─────────────────┘     └──────────────────┘     └───────────────┘
                                  │
                         ┌────────▼────────┐
                         │    MongoDB      │
                         │    :27017       │
                         └─────────────────┘
```

### ML Pipeline (scored & fused)
| Component | Role | Weight |
|-----------|------|--------|
| EfficientNet-B0 CNN | Real vs Fake classifier | 60% |
| CLIP (ViT-B/32) | Image-text semantic match | 20% |
| Error Level Analysis | Tampering heatmap | 20% |
| Tesseract OCR | Field extraction + validation | — |

---

## Prerequisites

### Required
- [Docker Desktop](https://docs.docker.com/desktop/windows/) with WSL2 backend
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) for GPU support

### Verify GPU access
```bash
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

---

## Quick Start

```bash
# 1. Clone / navigate to the project directory
cd "Fake certificate"

# 2. Copy environment file
cp .env.example .env

# 3. Launch all services
docker-compose up --build
```

The first run will **automatically**:
1. Generate ~2000 synthetic certificate images (train + val split)
2. Generate ~2000 tampered fake variants
3. Train EfficientNet-B0 for up to 15 epochs (~20–40 min on RTX 4060)
4. Cache the trained model in the `model_weights` volume

Subsequent runs skip training and boot in seconds.

### Access the app
| URL | Service |
|-----|---------|
| http://localhost:3000 | Web interface |
| http://localhost:8000/docs | FastAPI Swagger UI |
| http://localhost:8000/api/health | Health check |
| http://localhost:27017 | MongoDB (internal) |

---

## Project Structure

```
Fake certificate/
├── ml/                        # ML pipeline
│   ├── dataset/
│   │   ├── generate_synthetic.py   # creates REAL certs
│   │   └── create_tampered.py      # creates FAKE certs
│   ├── model.py               # EfficientNet-B0 classifier
│   ├── train.py               # training loop (15 epochs, early stop)
│   ├── predict.py             # full prediction pipeline
│   ├── ocr.py                 # Tesseract OCR + validation
│   ├── ela.py                 # Error Level Analysis
│   ├── clip_check.py          # CLIP semantic similarity
│   ├── utils.py               # shared utilities
│   ├── entrypoint.sh          # auto-train on cold start
│   ├── requirements.txt
│   └── Dockerfile
├── backend/                   # FastAPI REST API
│   ├── routers/upload.py      # POST /api/upload
│   ├── models/result.py       # Pydantic schemas
│   ├── db/mongo.py            # Motor async MongoDB
│   ├── services/pipeline.py   # pipeline orchestration
│   ├── main.py                # FastAPI app
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                  # Next.js 14 UI
│   ├── pages/
│   │   ├── index.js           # landing page
│   │   ├── upload.js          # drag & drop upload
│   │   └── result.js          # result + heatmap display
│   ├── components/
│   │   ├── DropZone.js        # file upload widget
│   │   ├── ResultCard.js      # prediction display
│   │   └── HeatmapDisplay.js  # ELA heatmap viewer
│   ├── styles/globals.css     # dark theme design system
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml         # orchestration
├── .env.example               # environment template
└── README.md
```

---

## API Reference

### `POST /api/upload`

Upload a certificate for analysis.

**Request:** `multipart/form-data` with field `file` (JPG/PNG/PDF, max 20 MB)

**Response:**
```json
{
  "prediction":   "REAL",
  "confidence":   87.45,
  "cnn_score":    0.912,
  "clip_score":   0.831,
  "tamper_score": 0.784,
  "ocr": {
    "university":  "IIT Delhi",
    "date":        "15 June, 2024",
    "roll_number": "CS24001",
    "is_valid_text": true,
    "anomaly_flags": []
  },
  "heatmap_b64": "<base64 PNG>",
  "filename":    "certificate.jpg",
  "timestamp":   "2026-02-20T16:00:00"
}
```

---

## Training Details

| Parameter | Value |
|-----------|-------|
| Base model | EfficientNet-B0 (pretrained ImageNet) |
| Frozen layers | First N-3 MBConv blocks |
| Epochs | 15 (early stopping, patience=3) |
| Batch size | 32 |
| Optimizer | AdamW (lr=1e-4, wd=1e-4) |
| Scheduler | CosineAnnealingLR |
| Loss | CrossEntropyLoss + label smoothing (0.1) |
| Augmentations | Rotation, brightness, Gaussian noise, JPEG artifacts |
| GPU | RTX 4060 8GB (CUDA 11.8) |

---

## Running Without Docker (Development)

### ML + Backend
```bash
cd ml
pip install -r requirements.txt
python dataset/generate_synthetic.py
python dataset/create_tampered.py
python train.py
```

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## Troubleshooting

**GPU not detected in Docker:**
- Ensure NVIDIA Container Toolkit is installed: `nvidia-ctk --version`
- Restart Docker Desktop after toolkit installation

**Training logs:**
```bash
docker logs certify-ml -f
```

**Model not found (backend 503 error):**
- Training is still in progress. Check `docker logs certify-ml -f`
- Model will be ready once training completes

**Poppler not found (PDF upload fails):**
- Poppler is installed inside the Docker container
- For local dev on Windows: download from https://github.com/oschwartz10612/poppler-windows/releases
