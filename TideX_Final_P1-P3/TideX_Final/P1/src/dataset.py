"""
TideX P1 — PyTorch Dataset for oil-spill segmentation.

Reads the supplied CSV, pairs image/mask by filename,
extracts 256×256 patches using bottom-right (x,y) convention,
filters out invalid boundary samples, normalizes SAR,
and supports optional geometric augmentation.
"""

import random
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
import rasterio.windows
import torch
from torch.utils.data import Dataset

from src.config import (
    PATCH_SIZE,
    SAR_CLIP_LOW,
    SAR_CLIP_HIGH,
    SAR_NAN_FILL,
    SAR_INF_CLAMP,
)


def normalize_sar(patch: np.ndarray) -> np.ndarray:
    """
    Per-patch percentile normalization for SAR dB values.

    1. Replace NaN / Inf with safe defaults.
    2. Clip to [p2, p98] percentile range.
    3. Scale to [0, 1].

    This is intentionally per-patch so the same function works
    identically during training and sliding-window inference.
    """
    patch = patch.astype(np.float32)
    patch = np.nan_to_num(
        patch,
        nan=SAR_NAN_FILL,
        posinf=SAR_INF_CLAMP,
        neginf=SAR_NAN_FILL,
    )

    p_lo = np.percentile(patch, SAR_CLIP_LOW)
    p_hi = np.percentile(patch, SAR_CLIP_HIGH)

    if p_hi > p_lo:
        patch = (patch - p_lo) / (p_hi - p_lo)
    else:
        patch = np.zeros_like(patch)

    return np.clip(patch, 0.0, 1.0)


class OilSpillDataset(Dataset):
    """
    PyTorch Dataset for the Sentinel-1 oil-spill segmentation task.

    CSV convention
    --------------
    coordinates = "x,y" = bottom-right corner of the 256×256 patch.
    So:  patch = raster[y-256 : y,  x-256 : x]

    Invalid samples (coordinates outside image bounds) are filtered
    out during __init__ and logged.
    """

    def __init__(
        self,
        csv_path: str | Path,
        image_dir: str | Path,
        mask_dir: str | Path,
        augment: bool = False,
        max_samples: int | None = None,
        seed: int = 42,
    ):
        self.image_dir = Path(image_dir)
        self.mask_dir = Path(mask_dir)
        self.augment = augment

        # ----------------------------------------------------------
        # Parse CSV
        # ----------------------------------------------------------
        df = pd.read_csv(csv_path)
        coords = df["coordinates"].str.split(",", expand=True).astype(int)
        df["x"] = coords[0]
        df["y"] = coords[1]
        df["filename"] = df["paths"].apply(lambda p: Path(str(p)).name)

        # ----------------------------------------------------------
        # Cache image dimensions (avoid repeated rasterio opens)
        # ----------------------------------------------------------
        self._dims: dict[str, tuple[int, int]] = {}
        for fname in df["filename"].unique():
            img_path = self.image_dir / fname
            if img_path.exists():
                with rasterio.open(img_path) as src:
                    self._dims[fname] = (src.width, src.height)

        # ----------------------------------------------------------
        # Filter invalid boundary samples
        # ----------------------------------------------------------
        valid_mask = df.apply(self._is_valid, axis=1)
        n_invalid = (~valid_mask).sum()
        df = df[valid_mask].reset_index(drop=True)

        print(
            f"Dataset: {csv_path.name if isinstance(csv_path, Path) else Path(csv_path).name}"
        )
        print(f"  Total rows in CSV : {len(valid_mask)}")
        print(f"  Invalid (excluded): {n_invalid}")
        print(f"  Valid samples     : {len(df)}")

        # ----------------------------------------------------------
        # Optional: subsample for speed
        # ----------------------------------------------------------
        if max_samples is not None and len(df) > max_samples:
            # Stratified sampling: maintain class ratio
            rng = np.random.RandomState(seed)

            pos = df[df["class"] == 1.0]
            neg = df[df["class"] == 0.0]

            pos_ratio = len(pos) / len(df)
            n_pos = int(max_samples * pos_ratio)
            n_neg = max_samples - n_pos

            n_pos = min(n_pos, len(pos))
            n_neg = min(n_neg, len(neg))

            sampled_pos = pos.sample(n=n_pos, random_state=rng)
            sampled_neg = neg.sample(n=n_neg, random_state=rng)

            df = pd.concat([sampled_pos, sampled_neg]).sample(
                frac=1.0, random_state=rng
            ).reset_index(drop=True)

            print(f"  Subsampled to     : {len(df)} "
                  f"(pos={n_pos}, neg={n_neg})")

        self.df = df

        # Class distribution
        cls_counts = df["class"].value_counts()
        print(f"  Class 1 (oil)     : {cls_counts.get(1.0, 0)}")
        print(f"  Class 0 (bg)      : {cls_counts.get(0.0, 0)}")

    def _is_valid(self, row) -> bool:
        """Check if the patch fits within the image."""
        fname = row["filename"]
        if fname not in self._dims:
            return False

        W, H = self._dims[fname]
        x, y = int(row["x"]), int(row["y"])

        return (
            x >= PATCH_SIZE
            and y >= PATCH_SIZE
            and x <= W
            and y <= H
        )

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int):
        row = self.df.iloc[idx]

        filename = row["filename"]
        x = int(row["x"])
        y = int(row["y"])

        # Bottom-right convention:
        #   window col_off = x - 256
        #   window row_off = y - 256
        window = rasterio.windows.Window(
            col_off=x - PATCH_SIZE,
            row_off=y - PATCH_SIZE,
            width=PATCH_SIZE,
            height=PATCH_SIZE,
        )

        # Read image patch
        with rasterio.open(self.image_dir / filename) as src:
            image = src.read(1, window=window)

        # Read mask patch
        with rasterio.open(self.mask_dir / filename) as src:
            mask = src.read(1, window=window)

        # Safety: ensure correct shape
        assert image.shape == (PATCH_SIZE, PATCH_SIZE), (
            f"Bad image shape {image.shape} for {filename} at ({x},{y})"
        )
        assert mask.shape == (PATCH_SIZE, PATCH_SIZE), (
            f"Bad mask shape {mask.shape} for {filename} at ({x},{y})"
        )

        # Normalize SAR
        image = normalize_sar(image)

        # Binary mask
        mask = (mask > 0.5).astype(np.float32)

        # Augmentation (geometric only — fast, no extra deps)
        if self.augment:
            if random.random() < 0.5:
                image = np.fliplr(image).copy()
                mask = np.fliplr(mask).copy()
            if random.random() < 0.5:
                image = np.flipud(image).copy()
                mask = np.flipud(mask).copy()
            if random.random() < 0.5:
                k = random.randint(1, 3)
                image = np.rot90(image, k).copy()
                mask = np.rot90(mask, k).copy()

        # To tensors  [H,W] → [1,H,W]
        image = torch.from_numpy(image).float().unsqueeze(0)
        mask = torch.from_numpy(mask).float().unsqueeze(0)

        return image, mask
