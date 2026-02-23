"""
model.py - Certificate Classifier Model Definition
Uses EfficientNet-B0 as backbone with a custom classification head.
"""

import torch
import torch.nn as nn
from efficientnet_pytorch import EfficientNet
import logging

logger = logging.getLogger(__name__)


class CertificateClassifier(nn.Module):
    """
    Binary classifier for real vs fake certificate detection.
    Backbone: EfficientNet-B0 with fine-tuned last layers.
    """

    def __init__(self, num_classes: int = 2, pretrained: bool = True):
        super(CertificateClassifier, self).__init__()

        # Load EfficientNet-B0 pretrained on ImageNet
        if pretrained:
            self.backbone = EfficientNet.from_pretrained("efficientnet-b0")
            logger.info("Loaded pretrained EfficientNet-B0 weights")
        else:
            self.backbone = EfficientNet.from_name("efficientnet-b0")

        # Get the number of features in the final layer
        in_features = self.backbone._fc.in_features

        # Replace the classifier head
        self.backbone._fc = nn.Sequential(
            nn.Dropout(p=0.3),
            nn.Linear(in_features, 256),
            nn.ReLU(),
            nn.Dropout(p=0.2),
            nn.Linear(256, num_classes),
        )

        # Freeze early layers, only fine-tune last blocks + head
        self._freeze_early_layers()

    def _freeze_early_layers(self):
        """Freeze all layers except the last 3 MBConv blocks and the head."""
        total_blocks = len(self.backbone._blocks)
        # Freeze all feature extraction layers except last 3 blocks
        for i, block in enumerate(self.backbone._blocks):
            if i < total_blocks - 3:
                for param in block.parameters():
                    param.requires_grad = False

        # Always freeze stem conv and BN
        for param in self.backbone._conv_stem.parameters():
            param.requires_grad = False
        for param in self.backbone._bn0.parameters():
            param.requires_grad = False

        frozen = sum(1 for p in self.parameters() if not p.requires_grad)
        trainable = sum(1 for p in self.parameters() if p.requires_grad)
        logger.info(f"Frozen params: {frozen}, Trainable params: {trainable}")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.backbone(x)


def get_model(num_classes: int = 2, pretrained: bool = True) -> CertificateClassifier:
    """Factory function to create and return the model."""
    model = CertificateClassifier(num_classes=num_classes, pretrained=pretrained)
    return model


def load_model(model_path: str, device: torch.device) -> CertificateClassifier:
    """Load a saved model from disk."""
    model = get_model(pretrained=False)
    state_dict = torch.load(model_path, map_location=device)
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()
    logger.info(f"Loaded model from {model_path}")
    return model
