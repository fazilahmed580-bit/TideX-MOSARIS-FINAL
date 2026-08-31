"""
Comprehensive dataset investigation for P1 oil-spill detection.
Answers:
  1. Coordinate convention verification
  2. Invalid sample analysis (the 811 samples)
  3. Image dimensions and SAR value statistics
  4. Class distribution
  5. Per-image breakdown of invalid samples
"""

import rasterio
import numpy as np
import pandas as pd
from pathlib import Path
import json

ROOT = Path("X:/TideX")
TRAIN_IMG_DIR = ROOT / "train" / "images"
TRAIN_MASK_DIR = ROOT / "train" / "masks"
TRAIN_CSV = ROOT / "train" / "dataframe_train_dataset_256_90.csv"
VAL_CSV = ROOT / "train" / "dataframe_val_dataset_256_90.csv"
PATCH_SIZE = 256

# ============================================================
# 1. Image metadata: dimensions, CRS, data type, value ranges
# ============================================================
print("=" * 70)
print("SECTION 1: IMAGE METADATA")
print("=" * 70)

image_meta = {}
for img_path in sorted(TRAIN_IMG_DIR.glob("*.tif")):
    with rasterio.open(img_path) as src:
        data = src.read(1)
        meta = {
            "width": src.width,
            "height": src.height,
            "bands": src.count,
            "crs": str(src.crs),
            "dtype": str(src.dtypes[0]),
            "transform": str(src.transform),
            "min": float(np.nanmin(data)),
            "max": float(np.nanmax(data)),
            "mean": float(np.nanmean(data)),
            "std": float(np.nanstd(data)),
            "p1": float(np.nanpercentile(data, 1)),
            "p5": float(np.nanpercentile(data, 5)),
            "p95": float(np.nanpercentile(data, 95)),
            "p99": float(np.nanpercentile(data, 99)),
            "nan_count": int(np.isnan(data).sum()),
            "inf_count": int(np.isinf(data).sum()),
        }
        image_meta[img_path.name] = meta
        print(f"\n{img_path.name}:")
        print(f"  Size: {meta['width']}x{meta['height']}, CRS: {meta['crs']}")
        print(f"  Range: [{meta['min']:.2f}, {meta['max']:.2f}], "
              f"Mean: {meta['mean']:.2f}, Std: {meta['std']:.2f}")
        print(f"  Percentiles: p1={meta['p1']:.2f}, p5={meta['p5']:.2f}, "
              f"p95={meta['p95']:.2f}, p99={meta['p99']:.2f}")
        print(f"  NaN: {meta['nan_count']}, Inf: {meta['inf_count']}")

# Check masks too
print("\n" + "=" * 70)
print("SECTION 1b: MASK METADATA")
print("=" * 70)

for mask_path in sorted(TRAIN_MASK_DIR.glob("*.tif")):
    with rasterio.open(mask_path) as src:
        mask_data = src.read(1)
        unique_vals = np.unique(mask_data)
        oil_fraction = np.mean(mask_data == 1) * 100
        print(f"\n{mask_path.name}:")
        print(f"  Size: {src.width}x{src.height}, dtype: {src.dtypes[0]}")
        print(f"  Unique values: {unique_vals}")
        print(f"  Oil fraction: {oil_fraction:.2f}%")

# ============================================================
# 2. CSV analysis
# ============================================================
print("\n" + "=" * 70)
print("SECTION 2: CSV ANALYSIS")
print("=" * 70)

train_df = pd.read_csv(TRAIN_CSV)
val_df = pd.read_csv(VAL_CSV)

print(f"\nTraining CSV: {len(train_df)} rows")
print(f"Validation CSV: {len(val_df)} rows")

# Parse coordinates
def parse_coords(df):
    coords = df["coordinates"].str.split(",", expand=True).astype(int)
    df = df.copy()
    df["coord_a"] = coords[0]
    df["coord_b"] = coords[1]
    df["filename"] = df["paths"].apply(lambda p: Path(str(p)).name)
    return df

train_df = parse_coords(train_df)
val_df = parse_coords(val_df)

# Class distribution
print(f"\nTraining class distribution:")
print(train_df["class"].value_counts().to_string())
print(f"\nValidation class distribution:")
print(val_df["class"].value_counts().to_string())

# Per-image sample counts
print(f"\nTraining samples per image:")
print(train_df["filename"].value_counts().to_string())

# ============================================================
# 3. Coordinate convention verification
# ============================================================
print("\n" + "=" * 70)
print("SECTION 3: COORDINATE CONVENTION VERIFICATION")
print("=" * 70)

# Test across MULTIPLE images, not just one
test_images = ["2018_08_21_.tif", "20200307.tif", "2018_12_07.tif", "20200224.tif"]

for test_img in test_images:
    print(f"\n--- Testing {test_img} ---")
    
    with rasterio.open(TRAIN_MASK_DIR / test_img) as src:
        mask = src.read(1)
    H, W = mask.shape
    
    positive_rows = train_df[
        (train_df["filename"] == test_img) &
        (train_df["class"] == 1.0)
    ].head(50)
    
    if len(positive_rows) == 0:
        print("  No positive samples found.")
        continue
    
    modes = {
        "xy_top_left":     lambda a, b: (a, b),
        "xy_bottom_right": lambda a, b: (a - PATCH_SIZE, b - PATCH_SIZE),
        "xy_center":       lambda a, b: (a - PATCH_SIZE//2, b - PATCH_SIZE//2),
        "yx_top_left":     lambda a, b: (b, a),
        "yx_bottom_right": lambda a, b: (b - PATCH_SIZE, a - PATCH_SIZE),
        "yx_center":       lambda a, b: (b - PATCH_SIZE//2, a - PATCH_SIZE//2),
    }
    
    for mode_name, coord_fn in modes.items():
        valid = 0
        oil_present = 0
        total_oil_pixels = 0
        
        for _, row in positive_rows.iterrows():
            a, b = row["coord_a"], row["coord_b"]
            x, y = coord_fn(a, b)
            
            if x < 0 or y < 0 or x + PATCH_SIZE > W or y + PATCH_SIZE > H:
                continue
            
            valid += 1
            patch = mask[y:y+PATCH_SIZE, x:x+PATCH_SIZE]
            oil_px = np.sum(patch == 1)
            if oil_px > 0:
                oil_present += 1
                total_oil_pixels += oil_px
        
        if valid > 0:
            avg_oil = total_oil_pixels / valid
            print(f"  {mode_name:20s}: {oil_present}/{valid} have oil, "
                  f"avg oil px = {avg_oil:.1f}")

# ============================================================
# 4. Invalid sample analysis
# ============================================================
print("\n" + "=" * 70)
print("SECTION 4: INVALID SAMPLE ANALYSIS (TRAIN)")
print("=" * 70)

def analyze_invalid(df, label):
    invalid_rows = []
    for _, row in df.iterrows():
        fname = row["filename"]
        a, b = row["coord_a"], row["coord_b"]
        meta = image_meta.get(fname)
        if meta is None:
            invalid_rows.append({
                "filename": fname, "a": a, "b": b,
                "class": row["class"], "reason": "file_not_found"
            })
            continue
        
        W, H = meta["width"], meta["height"]
        
        # Check as bottom-right (x,y)
        x_start = a - PATCH_SIZE
        y_start = b - PATCH_SIZE
        
        reasons = []
        if x_start < 0:
            reasons.append(f"x_start={x_start}<0")
        if y_start < 0:
            reasons.append(f"y_start={y_start}<0")
        if a > W:
            reasons.append(f"x={a}>W={W}")
        if b > H:
            reasons.append(f"y={b}>H={H}")
        
        if reasons:
            invalid_rows.append({
                "filename": fname, "a": a, "b": b,
                "width": W, "height": H,
                "class": row["class"],
                "reasons": "; ".join(reasons)
            })
    
    print(f"\n{label}: {len(invalid_rows)} invalid samples out of {len(df)}")
    
    if invalid_rows:
        inv_df = pd.DataFrame(invalid_rows)
        
        # Per-image breakdown
        print(f"\nPer-image breakdown:")
        print(inv_df.groupby("filename").size().to_string())
        
        # Class breakdown
        print(f"\nClass breakdown of invalid samples:")
        print(inv_df.groupby("class").size().to_string())
        
        # Reason breakdown
        if "reasons" in inv_df.columns:
            print(f"\nReason breakdown:")
            # Check which dimension is exceeded
            y_exceeds = inv_df[inv_df["reasons"].str.contains("y=.*>H", na=False)]
            x_exceeds = inv_df[inv_df["reasons"].str.contains("x=.*>W", na=False)]
            x_too_small = inv_df[inv_df["reasons"].str.contains("x_start.*<0", na=False)]
            y_too_small = inv_df[inv_df["reasons"].str.contains("y_start.*<0", na=False)]
            
            print(f"  y exceeds height: {len(y_exceeds)}")
            print(f"  x exceeds width:  {len(x_exceeds)}")
            print(f"  x_start < 0:      {len(x_too_small)}")
            print(f"  y_start < 0:      {len(y_too_small)}")
        
        # Show some examples
        print(f"\nFirst 10 invalid samples:")
        for i, r in enumerate(invalid_rows[:10]):
            print(f"  {r}")
    
    return invalid_rows

train_invalid = analyze_invalid(train_df, "TRAIN")
val_invalid = analyze_invalid(val_df, "VALIDATION")

# ============================================================
# 5. Check: are invalid samples coordinates > image dim?
#    Could the CSV have been generated for PADDED images?
# ============================================================
print("\n" + "=" * 70)
print("SECTION 5: PADDING HYPOTHESIS")
print("=" * 70)

# Check if invalid coords suggest a consistent padding pattern
for inv in train_invalid[:20]:
    fname = inv["filename"]
    a, b = inv["a"], inv["b"]
    meta = image_meta.get(fname, {})
    W = meta.get("width", "?")
    H = meta.get("height", "?")
    overshoot_x = a - W if isinstance(W, int) and a > W else 0
    overshoot_y = b - H if isinstance(H, int) and b > H else 0
    print(f"  {fname}: coord=({a},{b}), img=({W}x{H}), "
          f"overshoot_x={overshoot_x}, overshoot_y={overshoot_y}")

# ============================================================
# 6. Quick SAR value distribution summary across all images
# ============================================================
print("\n" + "=" * 70)
print("SECTION 6: SAR VALUE DISTRIBUTION SUMMARY")
print("=" * 70)

all_p1 = [m["p1"] for m in image_meta.values()]
all_p99 = [m["p99"] for m in image_meta.values()]
all_min = [m["min"] for m in image_meta.values()]
all_max = [m["max"] for m in image_meta.values()]

print(f"Across all {len(image_meta)} images:")
print(f"  Global min: {min(all_min):.2f}")
print(f"  Global max: {max(all_max):.2f}")
print(f"  p1 range:  [{min(all_p1):.2f}, {max(all_p1):.2f}]")
print(f"  p99 range: [{min(all_p99):.2f}, {max(all_p99):.2f}]")

print("\nDone.")
