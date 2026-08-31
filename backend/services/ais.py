"""
services/ais.py  --  P3 MOCK
------------------------------
This file is the PLUG-IN POINT for the P3 teammate.

WHAT THIS FILE DOES:
  Simulates AIS vessel candidate filtering near the Gulf of Mexico source region.
"""


def find_candidates(source: dict) -> list:
    """
    Mock P3: returns AIS candidate vessels near the estimated source region in Gulf of Mexico.
    """

    candidates = [

        # --- CANDIDATE 1: Strongest match ---
        {
            "mmsi":               "123456789",
            "vessel_name":        "MV Gulf Star",
            "distance_km":        4.2,
            "time_difference_hr": 0.5,
            "speed":              11.4,
            "heading":            142,
            "track": {
                "type": "LineString",
                "coordinates": [
                    [-88.75, 28.25],
                    [-88.65, 28.35],
                    [-88.55, 28.45],
                    [-88.50, 28.52],
                    [-88.45, 28.60],
                    [-88.35, 28.70],
                    [-88.25, 28.78],
                ]
            }
        },

        # --- CANDIDATE 2: Moderate match ---
        {
            "mmsi":               "234567890",
            "vessel_name":        "MV Coastal Voyager",
            "distance_km":        11.8,
            "time_difference_hr": 1.2,
            "speed":              8.7,
            "heading":            78,
            "track": {
                "type": "LineString",
                "coordinates": [
                    [-88.85, 28.40],
                    [-88.70, 28.48],
                    [-88.55, 28.53],
                    [-88.40, 28.58],
                    [-88.25, 28.62],
                    [-88.10, 28.68],
                ]
            }
        },

        # --- CANDIDATE 3: Weak match ---
        {
            "mmsi":               "345678901",
            "vessel_name":        "MV Sea Wanderer",
            "distance_km":        28.5,
            "time_difference_hr": 3.8,
            "speed":              6.2,
            "heading":            215,
            "track": {
                "type": "LineString",
                "coordinates": [
                    [-87.90, 29.10],
                    [-88.00, 28.95],
                    [-88.10, 28.80],
                    [-88.20, 28.68],
                    [-88.30, 28.58],
                ]
            }
        },

        # --- CANDIDATE 4: Contradictory evidence ---
        {
            "mmsi":               "456789012",
            "vessel_name":        "MV Gulf Runner",
            "distance_km":        15.2,
            "time_difference_hr": 0.8,
            "speed":              14.1,
            "heading":            310,
            "track": {
                "type": "LineString",
                "coordinates": [
                    [-88.40, 28.75],
                    [-88.45, 28.88],
                    [-88.50, 29.00],
                    [-88.55, 29.12],
                    [-88.60, 29.25],
                ]
            }
        },
    ]

    return candidates
