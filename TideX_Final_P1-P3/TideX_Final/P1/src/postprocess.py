"""
TideX P1 — Post-processing for oil-spill segmentation masks.

Pipeline:
    probability map
        → threshold
        → morphological opening (remove speckle)
        → morphological closing (fill holes)
        → connected components
        → remove small regions
        → final cleaned binary mask
"""

import numpy as np
from skimage import morphology, measure

from src.config import (
    THRESHOLD,
    MORPH_OPEN_KERNEL,
    MORPH_CLOSE_KERNEL,
    MIN_REGION_PIXELS,
)


def postprocess_mask(
    prob_map: np.ndarray,
    threshold: float = None,
    open_kernel: int = None,
    close_kernel: int = None,
    min_region_px: int = None,
) -> np.ndarray:
    """
    Post-process a probability map into a cleaned binary mask.

    Parameters
    ----------
    prob_map : (H, W) float32 array with values in [0, 1]
    threshold : probability threshold for binarization
    open_kernel : size of disk structuring element for opening
    close_kernel : size of disk structuring element for closing
    min_region_px : minimum connected component area in pixels

    Returns
    -------
    binary_mask : (H, W) uint8 array with {0, 1}
    """
    if threshold is None:
        threshold = THRESHOLD
    if open_kernel is None:
        open_kernel = MORPH_OPEN_KERNEL
    if close_kernel is None:
        close_kernel = MORPH_CLOSE_KERNEL
    if min_region_px is None:
        min_region_px = MIN_REGION_PIXELS

    # Step 1: Threshold
    binary = (prob_map >= threshold).astype(np.uint8)

    n_before = binary.sum()
    print(f"Post-processing:")
    print(f"  Threshold={threshold}: {n_before} positive pixels")

    if n_before == 0:
        print("  No oil detected — returning empty mask.")
        return binary

    # Step 2: Morphological opening (remove small noise/speckle)
    selem_open = morphology.disk(open_kernel)
    binary = morphology.binary_opening(binary, selem_open).astype(np.uint8)
    print(f"  After opening (disk={open_kernel}): {binary.sum()} px")

    # Step 3: Morphological closing (fill small holes)
    selem_close = morphology.disk(close_kernel)
    binary = morphology.binary_closing(binary, selem_close).astype(np.uint8)
    print(f"  After closing (disk={close_kernel}): {binary.sum()} px")

    # Step 4: Connected component filtering
    labels = measure.label(binary, connectivity=2)
    n_components = labels.max()

    kept = 0
    cleaned = np.zeros_like(binary)

    for region in measure.regionprops(labels):
        if region.area >= min_region_px:
            cleaned[labels == region.label] = 1
            kept += 1

    print(f"  Components: {n_components} found, "
          f"{kept} kept (min_area={min_region_px})")
    print(f"  Final positive pixels: {cleaned.sum()}")

    return cleaned


def get_region_stats(binary_mask: np.ndarray) -> list[dict]:
    """
    Get statistics for each connected region in the mask.

    Returns list of dicts with: label, area_px, centroid_row, centroid_col,
    bbox (minr, minc, maxr, maxc).
    """
    labels = measure.label(binary_mask, connectivity=2)
    stats = []

    for region in measure.regionprops(labels):
        stats.append({
            "label": region.label,
            "area_px": region.area,
            "centroid_row": region.centroid[0],
            "centroid_col": region.centroid[1],
            "bbox": region.bbox,  # (minr, minc, maxr, maxc)
        })

    return stats
