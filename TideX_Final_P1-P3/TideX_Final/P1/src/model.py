"""
TideX P1 — MiniUNet segmentation model.

A lightweight 3-level U-Net with filters [16, 32, 64, 128].
~120K parameters — designed for CPU-feasible training on 256×256
single-band SAR patches.
"""

import torch
import torch.nn as nn


class DoubleConv(nn.Module):
    """Two consecutive Conv2d-BN-ReLU blocks."""

    def __init__(self, in_ch: int, out_ch: int):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1, bias=False),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, 3, padding=1, bias=False),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        return self.block(x)


class MiniUNet(nn.Module):
    """
    Lightweight U-Net for binary segmentation.

    Architecture (default filters=[16, 32, 64, 128]):

        Input  1×256×256
          ↓
        Enc1  16×256×256  ──────────────┐
          ↓ pool                        │
        Enc2  32×128×128  ──────────┐   │
          ↓ pool                    │   │
        Enc3  64×64×64   ───────┐   │   │
          ↓ pool                │   │   │
        Bottleneck 128×32×32    │   │   │
          ↑ up                  │   │   │
        Dec3  64×64×64   ──────┘   │   │
          ↑ up                     │   │
        Dec2  32×128×128 ─────────┘   │
          ↑ up                        │
        Dec1  16×256×256 ────────────┘
          ↓
        Output 1×256×256
    """

    def __init__(self, in_channels: int = 1, out_channels: int = 1,
                 filters: list[int] | None = None):
        super().__init__()

        if filters is None:
            filters = [16, 32, 64, 128]

        assert len(filters) == 4, "Need exactly 4 filter sizes"
        f1, f2, f3, f4 = filters

        # Encoder
        self.enc1 = DoubleConv(in_channels, f1)
        self.enc2 = DoubleConv(f1, f2)
        self.enc3 = DoubleConv(f2, f3)
        self.pool = nn.MaxPool2d(2)

        # Bottleneck
        self.bottleneck = DoubleConv(f3, f4)

        # Decoder
        self.up3 = nn.ConvTranspose2d(f4, f3, kernel_size=2, stride=2)
        self.dec3 = DoubleConv(f3 * 2, f3)  # concat with enc3

        self.up2 = nn.ConvTranspose2d(f3, f2, kernel_size=2, stride=2)
        self.dec2 = DoubleConv(f2 * 2, f2)  # concat with enc2

        self.up1 = nn.ConvTranspose2d(f2, f1, kernel_size=2, stride=2)
        self.dec1 = DoubleConv(f1 * 2, f1)  # concat with enc1

        # Output head
        self.out_conv = nn.Conv2d(f1, out_channels, kernel_size=1)

    def forward(self, x):
        # Encoder
        e1 = self.enc1(x)                  # f1 × H × W
        e2 = self.enc2(self.pool(e1))      # f2 × H/2 × W/2
        e3 = self.enc3(self.pool(e2))      # f3 × H/4 × W/4

        # Bottleneck
        b = self.bottleneck(self.pool(e3))  # f4 × H/8 × W/8

        # Decoder with skip connections
        d3 = self.up3(b)                   # f3 × H/4 × W/4
        d3 = torch.cat([d3, e3], dim=1)    # 2*f3 × H/4 × W/4
        d3 = self.dec3(d3)                 # f3 × H/4 × W/4

        d2 = self.up2(d3)                  # f2 × H/2 × W/2
        d2 = torch.cat([d2, e2], dim=1)    # 2*f2 × H/2 × W/2
        d2 = self.dec2(d2)                 # f2 × H/2 × W/2

        d1 = self.up1(d2)                  # f1 × H × W
        d1 = torch.cat([d1, e1], dim=1)    # 2*f1 × H × W
        d1 = self.dec1(d1)                 # f1 × H × W

        return self.out_conv(d1)           # out × H × W


class DiceLoss(nn.Module):
    """Soft Dice loss for binary segmentation (operates on logits)."""

    def __init__(self, smooth: float = 1.0):
        super().__init__()
        self.smooth = smooth

    def forward(self, logits, targets):
        probs = torch.sigmoid(logits)
        probs_flat = probs.view(probs.size(0), -1)
        targets_flat = targets.view(targets.size(0), -1)

        intersection = (probs_flat * targets_flat).sum(dim=1)
        dice = (2.0 * intersection + self.smooth) / (
            probs_flat.sum(dim=1) + targets_flat.sum(dim=1) + self.smooth
        )
        return 1.0 - dice.mean()


def dice_score(logits, targets, threshold=0.5):
    """Compute hard Dice score (for evaluation)."""
    preds = (torch.sigmoid(logits) > threshold).float()
    preds = preds.view(preds.size(0), -1)
    targets = targets.view(targets.size(0), -1)

    intersection = (preds * targets).sum(dim=1)
    dice = (2.0 * intersection + 1e-7) / (
        preds.sum(dim=1) + targets.sum(dim=1) + 1e-7
    )
    return dice.mean().item()


def iou_score(logits, targets, threshold=0.5):
    """Compute IoU (Jaccard) score."""
    preds = (torch.sigmoid(logits) > threshold).float()
    preds = preds.view(preds.size(0), -1)
    targets = targets.view(targets.size(0), -1)

    intersection = (preds * targets).sum(dim=1)
    union = (preds + targets - preds * targets).sum(dim=1)
    iou = (intersection + 1e-7) / (union + 1e-7)
    return iou.mean().item()


def count_parameters(model: nn.Module) -> int:
    """Count total trainable parameters."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)
