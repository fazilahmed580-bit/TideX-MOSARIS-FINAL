"""
services/drift.py  --  P2 MOCK
--------------------------------
This file is the PLUG-IN POINT for the P2 teammate.

WHAT THIS FILE DOES:
  Simulates drift modelling, source backtracking, and forward forecast.

HOW P2 TEAMMATE REPLACES THIS:
  1. Keep function names:
       backtrack(spill: dict) -> dict
       forecast(source: dict) -> list
  2. Keep return structures (see RETURN FORMAT below).
  3. Replace function bodies with your real ocean drift algorithm.
  4. Do NOT change api/routes.py or main.py.

GEOGRAPHIC CONTEXT (demo):
  Spill is ~80 km south of Mississippi Delta, Gulf of Mexico.
  Prevailing current moves NNE towards the coastline.
  Source is estimated ~30 km further southwest.
"""


def backtrack(spill: dict) -> dict:
    """
    Mock P2 backtracking: given the detected spill, estimate where it came from in Gulf of Mexico.
    """

    # Estimated source region -- ~30 km SW of the detected spill [28.75N, -88.35W]
    origin_polygon = {
        "type": "Polygon",
        "coordinates": [[
            [-88.65, 28.45],
            [-88.45, 28.45],
            [-88.45, 28.58],
            [-88.65, 28.58],
            [-88.65, 28.45]   # closed
        ]]
    }

    # Uncertainty polygon (larger area around the origin estimate)
    uncertainty_polygon = {
        "type": "Polygon",
        "coordinates": [[
            [-88.80, 28.32],
            [-88.30, 28.32],
            [-88.30, 28.70],
            [-88.80, 28.70],
            [-88.80, 28.32]   # closed
        ]]
    }

    # Backward particles: simulated drift paths from spill back to source
    backward_particles = [
        [-88.35, 28.75],
        [-88.42, 28.70],
        [-88.48, 28.65],
        [-88.52, 28.60],
        [-88.55, 28.55],
        [-88.57, 28.52],
        [-88.60, 28.50],
    ]

    # Forward particles: current predicted drift from spill position onward
    forward_particles = [
        [-88.35, 28.75],
        [-88.30, 28.82],
        [-88.25, 28.90],
        [-88.20, 28.98],
        [-88.15, 29.05],
        [-88.10, 29.12],
    ]

    return {
        "origin_region":       origin_polygon,
        "origin_time_start":   "2026-08-30T07:00:00",
        "origin_time_end":     "2026-08-30T10:00:00",
        "uncertainty_polygon": uncertainty_polygon,
        "backward_particles":  backward_particles,
        "forward_particles":   forward_particles,
    }


def forecast(source: dict) -> list:
    """
    Mock P2 forecast: given the estimated source, predict where the spill will go next in Gulf of Mexico.
    """

    # Extend the forward particles further into the future towards Mississippi coastline
    future_particles = [
        [-88.10, 29.12],
        [-88.08, 29.18],
        [-88.05, 29.24],
        [-88.02, 29.30],
        [-88.00, 29.36],
        [-87.98, 29.42],
        [-87.95, 29.48],
        [-87.92, 29.55],
    ]

    return future_particles
