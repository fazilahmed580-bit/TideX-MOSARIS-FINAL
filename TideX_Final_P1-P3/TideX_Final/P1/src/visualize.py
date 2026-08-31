"""
TideX P1 — Visualization utilities.

Generates SAR + mask overlays and prediction visualizations.
"""

from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import rasterio

from src.dataset import normalize_sar


def create_overlay(
    image_path: str | Path,
    binary_mask: np.ndarray,
    prob_map: np.ndarray,
    output_path: str | Path,
    title: str = "Oil-Spill Detection",
):
    """
    Create a 3-panel visualization:
        [SAR image | Probability map | SAR + mask overlay]

    Saves to output_path as PNG.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Read and normalize SAR for display
    with rasterio.open(image_path) as src:
        sar = src.read(1)

    sar_norm = normalize_sar(sar)

    fig, axes = plt.subplots(1, 3, figsize=(20, 7))

    # Panel 1: SAR image
    axes[0].imshow(sar_norm, cmap="gray", vmin=0, vmax=1)
    axes[0].set_title("SAR Image (normalized)", fontsize=12)
    axes[0].axis("off")

    # Panel 2: Probability map
    im = axes[1].imshow(prob_map, cmap="hot", vmin=0, vmax=1)
    axes[1].set_title("Oil Probability Map", fontsize=12)
    axes[1].axis("off")
    plt.colorbar(im, ax=axes[1], fraction=0.046, pad=0.04)

    # Panel 3: Overlay — SAR + red mask
    overlay = np.stack([sar_norm] * 3, axis=-1)  # Grayscale → RGB
    # Paint oil regions red
    oil_pixels = binary_mask == 1
    overlay[oil_pixels, 0] = 1.0   # Red
    overlay[oil_pixels, 1] = 0.2   # Dim green
    overlay[oil_pixels, 2] = 0.2   # Dim blue

    axes[2].imshow(overlay)
    axes[2].set_title("SAR + Detected Oil Spill", fontsize=12)
    axes[2].axis("off")

    fig.suptitle(title, fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    print(f"Overlay saved: {output_path}")


def create_training_samples_viz(
    image_dir: Path,
    mask_dir: Path,
    df,
    output_path: str | Path,
    n_samples: int = 8,
):
    """
    Visualize random training patches (SAR + mask side by side).
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    from src.config import PATCH_SIZE

    # Sample positive patches
    pos = df[df["class"] == 1.0].sample(n=min(n_samples, len(df)))

    fig, axes = plt.subplots(n_samples, 2, figsize=(8, 3 * n_samples))

    for i, (_, row) in enumerate(pos.iterrows()):
        fname = row["filename"]
        x, y = int(row["x"]), int(row["y"])

        window = rasterio.windows.Window(
            x - PATCH_SIZE, y - PATCH_SIZE, PATCH_SIZE, PATCH_SIZE
        )

        with rasterio.open(image_dir / fname) as src:
            patch_img = src.read(1, window=window)

        with rasterio.open(mask_dir / fname) as src:
            patch_mask = src.read(1, window=window)

        patch_img = normalize_sar(patch_img)

        axes[i, 0].imshow(patch_img, cmap="gray")
        axes[i, 0].set_title(f"SAR: {fname}", fontsize=8)
        axes[i, 0].axis("off")

        axes[i, 1].imshow(patch_mask, cmap="Reds", vmin=0, vmax=1)
        axes[i, 1].set_title(f"Mask (oil fraction: {patch_mask.mean():.2%})", fontsize=8)
        axes[i, 1].axis("off")

    plt.suptitle("Training Sample Sanity Check", fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_path, dpi=120, bbox_inches="tight")
    plt.close(fig)

    print(f"Training samples visualization saved: {output_path}")
