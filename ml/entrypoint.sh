#!/usr/bin/env bash
# entrypoint.sh - ML container startup script
# Automatically triggers training if model.pth is not found.
# Then keeps the container alive (pipeline called by FastAPI via subprocess/import).

set -e

MODEL_PATH="/app/models/model.pth"
DATASET_TRAIN="/app/ml/dataset/train/real"

echo "============================================================"
echo "  Fake Certificate Detection — ML Container"
echo "============================================================"

# ── Step 1: Check if model already exists ────────────────────────────────────
if [ -f "$MODEL_PATH" ]; then
    echo "[STARTUP] Found existing model at $MODEL_PATH. Skipping training."
else
    echo "[STARTUP] No model found. Starting full training pipeline..."

    # ── Step 2: Generate synthetic REAL certificates ──────────────────────────
    echo "[DATASET] Generating synthetic REAL certificates..."
    python /app/ml/dataset/generate_synthetic.py

    # ── Step 3: Generate tampered FAKE certificates ───────────────────────────
    echo "[DATASET] Generating tampered FAKE certificates..."
    python /app/ml/dataset/create_tampered.py

    # ── Step 4: Train the model ───────────────────────────────────────────────
    echo "[TRAIN] Starting EfficientNet-B0 training (15 epochs)..."
    python /app/ml/train.py

    echo "[STARTUP] Training complete. Model saved to $MODEL_PATH"
fi

# ── Step 5: Keep container running (backend imports from /app/ml) ─────────────
echo "[STARTUP] ML pipeline ready. Container will remain active."
echo "[STARTUP] FastAPI backend will import from /app/ml/predict.py"
tail -f /dev/null
