"""
TideX P1 — End-to-end oil-spill detection CLI.

Usage:
    python detect.py --input <SAR.tif> --output outputs/

Produces:
    outputs/
    ├── geojson/spill_aoi.geojson     ← GeoJSON polygons in EPSG:4326
    ├── predictions/probability_map.tif
    ├── predictions/binary_mask.tif
    ├── visualizations/overlay.png
    └── metadata.json

The GeoJSON is the critical handoff to P3/P5.
"""

import argparse
import sys
import time
from pathlib import Path

# Add parent to path so we can import src
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.config import (
    MODEL_PATH,
    INFERENCE_STRIDE,
    INFERENCE_BATCH_SIZE,
    THRESHOLD,
)
from src.inference import (
    load_model,
    sliding_window_inference,
    save_probability_map,
    save_binary_mask,
)
from src.postprocess import postprocess_mask
from src.geospatial import create_geospatial_output
from src.visualize import create_overlay


def main():
    parser = argparse.ArgumentParser(
        description="TideX P1: Sentinel-1 SAR Oil-Spill Detection"
    )
    parser.add_argument(
        "--input", "-i", required=True,
        help="Path to input Sentinel-1 GeoTIFF"
    )
    parser.add_argument(
        "--output", "-o", default="outputs",
        help="Output directory (default: outputs/)"
    )
    parser.add_argument(
        "--model", "-m", default=None,
        help=f"Path to model checkpoint (default: {MODEL_PATH})"
    )
    parser.add_argument(
        "--stride", type=int, default=INFERENCE_STRIDE,
        help=f"Inference stride (default: {INFERENCE_STRIDE})"
    )
    parser.add_argument(
        "--threshold", type=float, default=THRESHOLD,
        help=f"Probability threshold (default: {THRESHOLD})"
    )
    parser.add_argument(
        "--batch-size", type=int, default=INFERENCE_BATCH_SIZE,
        help=f"Tiles per batch (default: {INFERENCE_BATCH_SIZE})"
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}")
        sys.exit(1)

    output_dir = Path(args.output)
    pred_dir = output_dir / "predictions"
    vis_dir = output_dir / "visualizations"
    geo_dir = output_dir / "geojson"

    for d in [pred_dir, vis_dir, geo_dir]:
        d.mkdir(parents=True, exist_ok=True)

    model_path = args.model or MODEL_PATH

    print("=" * 70)
    print("TideX P1 — Oil-Spill Detection")
    print("=" * 70)
    print(f"Input     : {input_path}")
    print(f"Output    : {output_dir}")
    print(f"Model     : {model_path}")
    print(f"Stride    : {args.stride}")
    print(f"Threshold : {args.threshold}")
    print()

    total_start = time.time()

    # Step 1: Load model
    import torch
    device = torch.device("cpu")
    model = load_model(model_path, device)
    print()

    # Step 2: Sliding-window inference
    print("Running inference...")
    prob_map, meta = sliding_window_inference(
        str(input_path), model, device,
        stride=args.stride,
        batch_size=args.batch_size,
    )

    # Save probability map
    prob_path = pred_dir / "probability_map.tif"
    save_probability_map(prob_map, meta, str(prob_path))

    # Step 3: Post-processing
    print()
    binary_mask = postprocess_mask(prob_map, threshold=args.threshold)

    # Save binary mask
    mask_path = pred_dir / "binary_mask.tif"
    save_binary_mask(binary_mask, meta, str(mask_path))

    # Step 4: Visualization
    print()
    overlay_path = vis_dir / "overlay.png"
    create_overlay(
        str(input_path), binary_mask, prob_map, str(overlay_path),
        title=f"Oil-Spill Detection: {input_path.name}",
    )

    # Step 5: Geospatial output
    geojson_path = geo_dir / "spill_aoi.geojson"
    metadata_path = output_dir / "metadata.json"

    metadata = create_geospatial_output(
        binary_mask=binary_mask,
        prob_map=prob_map,
        meta=meta,
        source_image=str(input_path),
        geojson_path=str(geojson_path),
        metadata_path=str(metadata_path),
    )

    total_time = time.time() - total_start

    print()
    print("=" * 70)
    print("P1 COMPLETE")
    print("=" * 70)
    print(f"Total time: {total_time:.1f}s ({total_time/60:.1f} min)")
    print()
    print("Output files:")
    print(f"  GeoJSON     : {geojson_path}")
    print(f"  Metadata    : {metadata_path}")
    print(f"  Prob. map   : {prob_path}")
    print(f"  Binary mask : {mask_path}")
    print(f"  Overlay     : {overlay_path}")
    print()
    print("P3/P5 interface: use spill_aoi.geojson + metadata.json")


if __name__ == "__main__":
    main()
