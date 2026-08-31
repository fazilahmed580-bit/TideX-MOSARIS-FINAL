"""
pipeline.py
-----------
Central pipeline orchestration for MOSARIS.

Ties together P1 -> P2 -> P3 -> P4 into one unified investigation pipeline.

KNOWN DEMO CASES:
  "demo_001" -- Gulf of Mexico demo spill
"""

import logging
from services.pipeline_adapter import execute_integrated_pipeline

logger = logging.getLogger("mosaris.pipeline")

# Spill IDs that the system knows about.
KNOWN_SPILL_IDS = {"demo_001"}


def run_investigation(spill_id: str) -> dict:
    """
    Execute the full MOSARIS investigation pipeline for a given spill ID.

    Pipeline sequence:
      P1: detect_spill      -- find the spill from SAR satellite data (Gulf of Mexico)
      P2: backtrack         -- trace spill back to origin & generate forecast
      P3: find_candidates   -- find AIS candidate vessels near source
      P4: attribution       -- what-if forward drift simulation & candidate ranking

    Returns a dict matching the InvestigationResult schema.
    Raises ValueError if the spill_id is unknown.
    """
    if spill_id not in KNOWN_SPILL_IDS:
        raise ValueError(f"Unknown spill ID: '{spill_id}'. Known IDs: {KNOWN_SPILL_IDS}")

    # Execute integrated P1 -> P2 -> P3 -> P4 pipeline via adapter
    result = execute_integrated_pipeline(spill_id)
    return result
