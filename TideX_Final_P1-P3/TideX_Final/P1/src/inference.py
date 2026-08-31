"""
TideX P1 — Full-scene sliding-window inference.

Takes a Sentinel-1 GeoTIFF and produces a full probability map
using overlapping 256×256 tiles with averaging.
"""

import numpy as np
import rasterio
import torch
from tqdm import tqdm

from src.config import (
    PATCH_SIZE,
    INFERENCE_STRIDE,
    INFERENCE_BATCH_SIZE,
    MODEL_PATH,
    FILTERS,
)
from src.dataset import normalize_sar
from src.model import MiniUNet


def load_model(model_path=None, device=None):
    """Load trained MiniUNet from checkpoint."""
    if model_path is None:
        model_path = MODEL_PATH
    if device is None:
        device = torch.device("cpu")

    checkpoint = torch.load(model_path, map_location=device, weights_only=False)
    filters = checkpoint.get("filters", FILTERS)

    model = MiniUNet(in_channels=1, out_channels=1, filters=filters)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()

    print(f"Model loaded: {model_path}")
    print(f"  Checkpoint Dice : {checkpoint.get('dice', 'N/A'):.4f}")
    print(f"  Checkpoint IoU  : {checkpoint.get('iou', 'N/A'):.4f}")
    print(f"  Epoch           : {checkpoint.get('epoch', 'N/A')}")

    return model


def sliding_window_inference(
    image_path: str,
    model: torch.nn.Module,
    device: torch.device = None,
    stride: int = None,
    batch_size: int = None,
) -> tuple[np.ndarray, dict]:
    """
    Run sliding-window inference on a full SAR GeoTIFF.

    Returns:
        prob_map: (H, W) float32 array of oil-spill probabilities [0, 1]
        meta: dict with rasterio profile and transform for geo-referencing
    """
    if device is None:
        device = torch.device("cpu")
    if stride is None:
        stride = INFERENCE_STRIDE
    if batch_size is None:
        batch_size = INFERENCE_BATCH_SIZE

    # Read full image
    with rasterio.open(image_path) as src:
        full_image = src.read(1).astype(np.float32)
        profile = src.profile.copy()
        transform = src.transform
        crs = src.crs

    H, W = full_image.shape
    print(f"Input image: {image_path}")
    print(f"  Size: {W}×{H}, CRS: {crs}")

    # Accumulator arrays for averaging overlapping predictions
    prob_sum = np.zeros((H, W), dtype=np.float64)
    count_map = np.zeros((H, W), dtype=np.float64)

    # Generate tile coordinates
    tiles = []
    for row_start in range(0, H - PATCH_SIZE + 1, stride):
        for col_start in range(0, W - PATCH_SIZE + 1, stride):
            tiles.append((row_start, col_start))

    # Handle right/bottom edges — add edge-aligned tiles
    # Right edge column
    if (W - PATCH_SIZE) % stride != 0:
        col_start = W - PATCH_SIZE
        for row_start in range(0, H - PATCH_SIZE + 1, stride):
            tiles.append((row_start, col_start))

    # Bottom edge row
    if (H - PATCH_SIZE) % stride != 0:
        row_start = H - PATCH_SIZE
        for col_start in range(0, W - PATCH_SIZE + 1, stride):
            tiles.append((row_start, col_start))

    # Bottom-right corner
    if (W - PATCH_SIZE) % stride != 0 and (H - PATCH_SIZE) % stride != 0:
        tiles.append((H - PATCH_SIZE, W - PATCH_SIZE))

    print(f"  Total tiles: {len(tiles)} (stride={stride})")

    # Process tiles in batches
    model.eval()
    with torch.no_grad():
        for i in tqdm(range(0, len(tiles), batch_size), desc="  Inference"):
            batch_tiles = tiles[i : i + batch_size]

            # Extract and normalize patches
            patches = []
            for (r, c) in batch_tiles:
                patch = full_image[r : r + PATCH_SIZE, c : c + PATCH_SIZE]
                patch = normalize_sar(patch)
                patches.append(patch)

            # Stack into batch tensor: [B, 1, H, W]
            batch_tensor = torch.from_numpy(
                np.array(patches)
            ).float().unsqueeze(1).to(device)

            # Predict
            logits = model(batch_tensor)
            probs = torch.sigmoid(logits).squeeze(1).cpu().numpy()

            # Accumulate
            for j, (r, c) in enumerate(batch_tiles):
                prob_sum[r : r + PATCH_SIZE, c : c + PATCH_SIZE] += probs[j]
                count_map[r : r + PATCH_SIZE, c : c + PATCH_SIZE] += 1.0

    # Average where we have predictions
    # Pixels not covered by any tile stay at 0
    valid = count_map > 0
    prob_map = np.zeros_like(prob_sum, dtype=np.float32)
    prob_map[valid] = (prob_sum[valid] / count_map[valid]).astype(np.float32)

    coverage = valid.sum() / (H * W) * 100
    print(f"  Coverage: {coverage:.1f}% of pixels predicted")

    meta = {
        "profile": profile,
        "transform": transform,
        "crs": crs,
        "height": H,
        "width": W,
    }

    return prob_map, meta


def save_probability_map(prob_map: np.ndarray, meta: dict, output_path: str):
    """Save probability map as a GeoTIFF preserving source georeferencing."""
    profile = meta["profile"].copy()
    profile.update(
        dtype="float32",
        count=1,
        compress="deflate",
    )

    with rasterio.open(output_path, "w", **profile) as dst:
        dst.write(prob_map, 1)

    print(f"Probability map saved: {output_path}")


def save_binary_mask(binary_mask: np.ndarray, meta: dict, output_path: str):
    """Save binary mask as a GeoTIFF preserving source georeferencing."""
    profile = meta["profile"].copy()
    profile.update(
        dtype="uint8",
        count=1,
        compress="deflate",
    )

    with rasterio.open(output_path, "w", **profile) as dst:
        dst.write(binary_mask.astype(np.uint8), 1)

    print(f"Binary mask saved: {output_path}")
