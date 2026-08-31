"""
services/spill_detection.py  --  P1 MOCK
-----------------------------------------
This file is the PLUG-IN POINT for the P1 teammate.

WHAT THIS FILE DOES:
  Simulates SAR (Synthetic Aperture Radar) oil-spill detection.
  In the mock, it returns a realistic spill result in the Gulf of Mexico.

HOW P1 TEAMMATE REPLACES THIS:
  1. Keep the function name:    detect_spill(spill_id: str) -> dict
  2. Keep the return structure  (see RETURN FORMAT below)
  3. Replace the body with your real Sentinel-1 / U-Net algorithm.
  4. Do NOT change anything in api/routes.py or main.py.

RETURN FORMAT:
  {
    "spill_id":        str,          # same as input
    "timestamp":       str,          # ISO 8601, UTC
    "spill_detected":  bool,
    "polygon":         dict,         # GeoJSON Polygon  [lon, lat]
    "centroid":        [lat, lon],   # NOTE: [lat, lon] -- API contract
    "area_km2":        float,
    "confidence":      float         # 0.0 to 1.0
  }

COORDINATE NOTE:
  GeoJSON uses [longitude, latitude].
  centroid uses [latitude, longitude] -- this is intentional per API contract.
"""


def detect_spill(spill_id: str) -> dict:
    """
    Mock P1: Returns a simulated oil-spill detection result.

    The demo spill is located in the northern Gulf of Mexico,
    approximately 80 km south of the Mississippi River Delta.
    """

    # Demo spill polygon in the Gulf of Mexico
    # GeoJSON coordinates are [longitude, latitude]
    spill_polygon = {
        "type": "Polygon",
        "coordinates": [[
            [-88.40, 28.85],
            [-88.25, 28.85],
            [-88.20, 28.75],
            [-88.30, 28.65],
            [-88.45, 28.68],
            [-88.48, 28.78],
            [-88.40, 28.85]   # closed -- first == last
        ]]
    }

    return {
        "spill_id":       spill_id,
        "timestamp":      "2026-08-30T10:00:00",
        "spill_detected": True,
        "polygon":        spill_polygon,
        "centroid":       [28.75, -88.35],   # [latitude, longitude] -- API contract
        "area_km2":       12.4,
        "confidence":     0.91
    }
