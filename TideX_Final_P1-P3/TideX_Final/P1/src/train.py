"""
TideX P1 — Training script.

Trains MiniUNet on the oil-spill segmentation dataset.
Supports configurable sample limits, epochs, batch size.
Saves the best model by validation Dice.

Usage:
    python -m src.train                       # Full training
    python -m src.train --benchmark           # Quick benchmark (~300 samples)
"""

import argparse
import random
import time

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm

from src.config import (
    TRAIN_CSV,
    VAL_CSV,
    TRAIN_IMAGE_DIR,
    TRAIN_MASK_DIR,
    MODEL_PATH,
    PATCH_SIZE,
    MAX_TRAIN_SAMPLES,
    MAX_VAL_SAMPLES,
    BATCH_SIZE,
    EPOCHS,
    LEARNING_RATE,
    NUM_WORKERS,
    SEED,
    BCE_WEIGHT,
    DICE_WEIGHT,
    FILTERS,
)
from src.dataset import OilSpillDataset
from src.model import MiniUNet, DiceLoss, dice_score, iou_score, count_parameters


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def train_one_epoch(model, loader, bce_fn, dice_fn, optimizer, device):
    model.train()
    running_loss = 0.0
    n_batches = 0

    pbar = tqdm(loader, desc="  Train", leave=False)
    for images, masks in pbar:
        images = images.to(device)
        masks = masks.to(device)

        optimizer.zero_grad(set_to_none=True)

        logits = model(images)
        loss = BCE_WEIGHT * bce_fn(logits, masks) + DICE_WEIGHT * dice_fn(logits, masks)

        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        n_batches += 1
        pbar.set_postfix(loss=f"{loss.item():.4f}")

    return running_loss / max(n_batches, 1)


@torch.no_grad()
def validate(model, loader, bce_fn, dice_fn, device):
    model.eval()
    running_loss = 0.0
    running_dice = 0.0
    running_iou = 0.0
    n_batches = 0

    pbar = tqdm(loader, desc="  Val  ", leave=False)
    for images, masks in pbar:
        images = images.to(device)
        masks = masks.to(device)

        logits = model(images)
        loss = BCE_WEIGHT * bce_fn(logits, masks) + DICE_WEIGHT * dice_fn(logits, masks)

        running_loss += loss.item()
        running_dice += dice_score(logits, masks)
        running_iou += iou_score(logits, masks)
        n_batches += 1

    n = max(n_batches, 1)
    return running_loss / n, running_dice / n, running_iou / n


def main():
    parser = argparse.ArgumentParser(description="TideX P1 Training")
    parser.add_argument("--benchmark", action="store_true",
                        help="Quick benchmark with ~300 samples")
    parser.add_argument("--max-train", type=int, default=None,
                        help="Override MAX_TRAIN_SAMPLES")
    parser.add_argument("--max-val", type=int, default=None,
                        help="Override MAX_VAL_SAMPLES")
    parser.add_argument("--epochs", type=int, default=None,
                        help="Override EPOCHS")
    parser.add_argument("--batch-size", type=int, default=None,
                        help="Override BATCH_SIZE")
    parser.add_argument("--lr", type=float, default=None,
                        help="Override LEARNING_RATE")
    args = parser.parse_args()

    # Resolve config overrides
    max_train = args.max_train or (300 if args.benchmark else MAX_TRAIN_SAMPLES)
    max_val = args.max_val or (100 if args.benchmark else MAX_VAL_SAMPLES)
    epochs = args.epochs or (2 if args.benchmark else EPOCHS)
    batch_size = args.batch_size or BATCH_SIZE
    lr = args.lr or LEARNING_RATE

    set_seed(SEED)
    device = torch.device("cpu")

    print("=" * 70)
    print("TideX P1 - Oil-Spill Segmentation Training")
    print("=" * 70)
    if args.benchmark:
        print(">>> BENCHMARK MODE <<<")
    print(f"Device          : {device}")
    print(f"Train samples   : {max_train}")
    print(f"Val samples     : {max_val}")
    print(f"Batch size      : {batch_size}")
    print(f"Epochs          : {epochs}")
    print(f"Learning rate   : {lr}")
    print(f"Filters         : {FILTERS}")
    print()

    # ----------------------------------------------------------
    # Datasets
    # ----------------------------------------------------------
    print("Loading training data...")
    train_ds = OilSpillDataset(
        TRAIN_CSV, TRAIN_IMAGE_DIR, TRAIN_MASK_DIR,
        augment=True, max_samples=max_train, seed=SEED,
    )
    print()
    print("Loading validation data...")
    val_ds = OilSpillDataset(
        VAL_CSV, TRAIN_IMAGE_DIR, TRAIN_MASK_DIR,
        augment=False, max_samples=max_val, seed=SEED,
    )
    print()

    train_loader = DataLoader(
        train_ds, batch_size=batch_size, shuffle=True,
        num_workers=NUM_WORKERS, drop_last=False,
    )
    val_loader = DataLoader(
        val_ds, batch_size=batch_size, shuffle=False,
        num_workers=NUM_WORKERS, drop_last=False,
    )

    # ----------------------------------------------------------
    # Model
    # ----------------------------------------------------------
    model = MiniUNet(in_channels=1, out_channels=1, filters=FILTERS).to(device)
    n_params = count_parameters(model)
    print(f"Model parameters: {n_params:,}")
    print()

    bce_fn = nn.BCEWithLogitsLoss()
    dice_fn = DiceLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)

    # ----------------------------------------------------------
    # Training loop
    # ----------------------------------------------------------
    best_dice = 0.0
    total_start = time.time()

    for epoch in range(epochs):
        epoch_start = time.time()
        print(f"Epoch {epoch + 1}/{epochs}")

        train_loss = train_one_epoch(
            model, train_loader, bce_fn, dice_fn, optimizer, device
        )

        val_loss, val_dice, val_iou = validate(
            model, val_loader, bce_fn, dice_fn, device
        )

        epoch_time = time.time() - epoch_start
        batches_per_epoch = len(train_loader)
        time_per_batch = epoch_time / batches_per_epoch if batches_per_epoch > 0 else 0

        print(f"  Train Loss : {train_loss:.4f}")
        print(f"  Val Loss   : {val_loss:.4f}")
        print(f"  Val Dice   : {val_dice:.4f}")
        print(f"  Val IoU    : {val_iou:.4f}")
        print(f"  Epoch time : {epoch_time:.1f}s "
              f"({time_per_batch:.2f}s/batch, {batches_per_epoch} batches)")

        if val_dice > best_dice:
            best_dice = val_dice
            torch.save({
                "model_state_dict": model.state_dict(),
                "filters": FILTERS,
                "dice": best_dice,
                "iou": val_iou,
                "epoch": epoch + 1,
                "n_params": n_params,
            }, MODEL_PATH)
            print(f"  [OK] Best model saved (Dice={best_dice:.4f})")

        print()

    total_time = time.time() - total_start
    print("=" * 70)
    print("TRAINING COMPLETE")
    print("=" * 70)
    print(f"Total time       : {total_time:.1f}s ({total_time/60:.1f} min)")
    print(f"Best val Dice    : {best_dice:.4f}")
    print(f"Model saved to   : {MODEL_PATH}")


if __name__ == "__main__":
    main()
