"""
train.py — EfficientNet-B0 Training Pipeline (Stable Docker Version)
"""

import os
import sys
import logging
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets
import torchvision.transforms as T
import numpy as np
from tqdm import tqdm
from PIL import Image, ImageDraw

# ── Paths ────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent
DATASET_DIR = BASE_DIR / "dataset"
MODEL_PATH  = BASE_DIR.parent / "models" / "model.pth"
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(BASE_DIR))

from model import get_model
from utils import setup_logging, get_device, IMAGENET_MEAN, IMAGENET_STD

setup_logging()
logger = logging.getLogger(__name__)

# ── Hyperparameters ──────────────────────────────────────────
BATCH_SIZE  = 32
NUM_EPOCHS  = 12
LEARNING_RATE = 5e-5
NUM_WORKERS = 0   # 🔥 VERY IMPORTANT FOR DOCKER STABILITY

# ── Custom Transforms ────────────────────────────────────────

class ShadowOverlay:
    def __call__(self, img: Image.Image) -> Image.Image:
        import random
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        W, H = img.size
        pts = [
            (random.randint(0, W//2), 0),
            (0, random.randint(0, H//2)),
            (0, 0),
        ]

        alpha = random.randint(30, 90)
        draw.polygon(pts, fill=(0, 0, 0, alpha))

        return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


class MotionBlur:
    def __init__(self, max_kernel: int = 5):
        self.max_k = max_kernel

    def __call__(self, img: Image.Image) -> Image.Image:
        import cv2
        k = np.random.choice([3, 5])
        kernel = np.zeros((k, k))

        if np.random.rand() > 0.5:
            kernel[k // 2, :] = 1 / k
        else:
            kernel[:, k // 2] = 1 / k

        arr = np.array(img)
        blurred = cv2.filter2D(arr, -1, kernel)
        return Image.fromarray(blurred.astype(np.uint8))


def get_transforms():
    train_tf = T.Compose([
        ShadowOverlay(),
        MotionBlur(),
        T.Resize((224, 224)),
        T.ToTensor(),
        T.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])

    val_tf = T.Compose([
        T.Resize((224, 224)),
        T.ToTensor(),
        T.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])

    return train_tf, val_tf


# ── Dataset ──────────────────────────────────────────────────

def load_datasets(train_tf, val_tf):
    train_dir = DATASET_DIR / "train"
    val_dir   = DATASET_DIR / "val"

    train_ds = datasets.ImageFolder(str(train_dir), transform=train_tf)
    val_ds   = datasets.ImageFolder(str(val_dir),   transform=val_tf)

    logger.info(f"Train: {len(train_ds)} | Val: {len(val_ds)}")

    return train_ds, val_ds


# ── Training ─────────────────────────────────────────────────

def train_one_epoch(model, loader, criterion, optimizer, device, ep):
    model.train()
    running_loss = 0.0

    bar = tqdm(loader, desc=f"Epoch {ep}", ncols=90)

    for imgs, labels in bar:
        imgs = imgs.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()
        outputs = model(imgs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        bar.set_postfix(loss=f"{loss.item():.4f}")

    return running_loss / len(loader)


# ── Main ─────────────────────────────────────────────────────

def main():
    device = get_device()
    logger.info(f"Device: {device}")

    train_tf, val_tf = get_transforms()
    train_ds, val_ds = load_datasets(train_tf, val_tf)

    pin = device.type == "cuda"

    train_loader = DataLoader(
        train_ds,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=NUM_WORKERS,
        pin_memory=pin,
    )

    model = get_model(num_classes=2, pretrained=True)
    model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=LEARNING_RATE)

    print("\n==============================")
    print("Training Started")
    print("==============================\n")

    for epoch in range(1, NUM_EPOCHS + 1):
        loss = train_one_epoch(model, train_loader, criterion, optimizer, device, epoch)
        print(f"Epoch {epoch}/{NUM_EPOCHS} - Loss: {loss:.4f}")

    torch.save(model.state_dict(), MODEL_PATH)

    print("\n==============================")
    print("Training Complete")
    print(f"Model saved at {MODEL_PATH}")
    print("==============================\n")


if __name__ == "__main__":
    main()