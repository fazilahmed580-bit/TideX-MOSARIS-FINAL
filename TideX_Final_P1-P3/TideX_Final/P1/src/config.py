"""
TideX P1 — Configuration
All hyperparameters, paths, and thresholds in one place.
"""

from pathlib import Path

# ============================================================
# PATHS
# ============================================================

ROOT = Path("X:/TideX")
P1_DIR = ROOT / "p1"

TRAIN_IMAGE_DIR = ROOT / "train" / "images"
TRAIN_MASK_DIR = ROOT / "train" / "masks"
TEST_IMAGE_DIR = ROOT / "test" / "images"
TEST_MASK_DIR = ROOT / "test" / "masks"

TRAIN_CSV = ROOT / "train" / "dataframe_train_dataset_256_90.csv"
VAL_CSV = ROOT / "train" / "dataframe_val_dataset_256_90.csv"

MODEL_DIR = P1_DIR / "models"
OUTPUT_DIR = P1_DIR / "outputs"
PRED_DIR = OUTPUT_DIR / "predictions"
VIS_DIR = OUTPUT_DIR / "visualizations"
GEO_DIR = OUTPUT_DIR / "geojson"

# Create directories
for d in [MODEL_DIR, PRED_DIR, VIS_DIR, GEO_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ============================================================
# DATA
# ============================================================

PATCH_SIZE = 256

# ============================================================
# TRAINING
# ============================================================

MAX_TRAIN_SAMPLES = 5000
MAX_VAL_SAMPLES = 1500
BATCH_SIZE = 16
EPOCHS = 8
LEARNING_RATE = 1e-3
NUM_WORKERS = 0          # Keep 0 on Windows
SEED = 42

# Loss weights
BCE_WEIGHT = 0.5
DICE_WEIGHT = 0.5

# ============================================================
# MODEL
# ============================================================

# MiniUNet encoder filter sizes
# 3-level encoder: [8, 16, 32] + bottleneck 64
# ~121K params - ~4x smaller than [16,32,64,128]
FILTERS = [8, 16, 32, 64]

MODEL_PATH = MODEL_DIR / "best_miniunet.pth"

# ============================================================
# INFERENCE
# ============================================================

INFERENCE_STRIDE = 128       # 50% overlap
INFERENCE_BATCH_SIZE = 32    # Tiles per batch during inference
THRESHOLD = 0.5              # Probability threshold

# ============================================================
# POST-PROCESSING
# ============================================================

MORPH_OPEN_KERNEL = 3        # Morphological opening kernel size
MORPH_CLOSE_KERNEL = 5       # Morphological closing kernel size
MIN_REGION_PIXELS = 500      # Minimum connected component size

# ============================================================
# GEOSPATIAL
# ============================================================

OUTPUT_CRS = "EPSG:4326"     # WGS84 for GeoJSON output

# ============================================================
# SAR NORMALIZATION
# ============================================================

SAR_CLIP_LOW = 2             # Lower percentile for normalization
SAR_CLIP_HIGH = 98           # Upper percentile for normalization
SAR_NAN_FILL = -40.0         # Fill value for NaN pixels
SAR_INF_CLAMP = 30.0         # Clamp value for Inf pixels
