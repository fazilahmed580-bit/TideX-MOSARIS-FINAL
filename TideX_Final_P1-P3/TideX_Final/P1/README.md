# TideX P1: Sentinel-1 SAR Oil-Spill Detection

Pixel-level oil-spill segmentation from Sentinel-1 SAR GeoTIFF imagery.
Produces georeferenced spill polygons (GeoJSON) for downstream AIS vessel
attribution (P3) and drift modelling (P2/P4).

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run detection on a SAR scene
python detect.py --input X:\TideX\train\images\2018_08_21_.tif --output outputs/
```

## Output Files

```
outputs/
  geojson/spill_aoi.geojson     <-- GeoJSON polygons in EPSG:4326 (P3/P5 handoff)
  predictions/probability_map.tif
  predictions/binary_mask.tif
  visualizations/overlay.png
  metadata.json
```

### metadata.json
```json
{
  "spill_detected": true,
  "confidence": 0.87,
  "area_km2": 3.72,
  "centroid": {"lat": 24.123, "lon": -88.456},
  "n_polygons": 5,
  "polygon_file": "spill_aoi.geojson",
  "crs": "EPSG:4326",
  "source_image": "2018_08_21_.tif"
}
```

## P3/P5 Integration

P3 only needs:
- `spill_aoi.geojson` -- actual polygon geometry
- `metadata.json` -- summary statistics

No knowledge of the model internals is required.

## Architecture

**MiniUNet** -- lightweight 3-level U-Net with filters [8, 16, 32, 64].

| Property | Value |
|---|---|
| Input | 1 x 256 x 256 (single-band SAR) |
| Output | 1 x 256 x 256 (oil probability) |
| Parameters | ~121K |
| Loss | 0.5*BCE + 0.5*Dice |
| Optimizer | AdamW (lr=1e-3, wd=1e-4) |

## Pipeline

```
Sentinel-1 GeoTIFF
    |
    v
Sliding-window tiling (256x256, stride 128)
    |
    v
Per-tile normalization (p2/p98 percentile)
    |
    v
MiniUNet inference
    |
    v
Average overlapping predictions
    |
    v
Threshold (0.5)
    |
    v
Morphological cleanup (open + close)
    |
    v
Connected component filtering (min 500 px)
    |
    v
Vectorize to polygons
    |
    v
Reproject to EPSG:4326
    |
    v
GeoJSON + metadata JSON
```

## Training

```bash
# Full training (5000 samples, 8 epochs)
python -m src.train

# Quick benchmark (300 samples, 2 epochs)
python -m src.train --benchmark

# Custom config
python -m src.train --max-train 3000 --epochs 5 --batch-size 8
```

## Dataset

- 14 training + 7 test Sentinel-1 SAR GeoTIFF scenes
- All EPSG:32616 (UTM zone 16N)
- Binary masks: 0=background, 1=oil-spill
- CSV patches: 256x256 with bottom-right (x,y) coordinate convention
- SAR values: dB-scale (approx. -40 to +27)

## Project Structure

```
p1/
  src/
    config.py       -- All hyperparameters and paths
    dataset.py      -- PyTorch Dataset with CSV parsing
    model.py        -- MiniUNet architecture
    train.py        -- Training loop
    inference.py    -- Sliding-window full-scene inference
    postprocess.py  -- Morphological cleanup
    geospatial.py   -- Mask to GeoJSON conversion
    visualize.py    -- Overlay generation
  detect.py         -- CLI entry point
  models/           -- Saved checkpoints
  outputs/          -- Inference results
  requirements.txt
  README.md
```

## Reference

Chang et al. (2024), "Marine Oil Pollution Monitoring Based on
Morphological Attention U-Net Using SAR Images," Sensors.

Note: This MVP uses a lightweight MiniUNet, not the exact architecture
from the reference paper.

## Hardware

Designed for CPU-only training and inference.
Benchmark: ~1.2s/batch on Intel CPU, ~50 min total training.
