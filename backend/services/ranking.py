"""
services/ranking.py  --  P4 MOCK
----------------------------------
This file is the PLUG-IN POINT for the P4 teammate.

WHAT THIS FILE DOES:
  Simulates evidence ranking and what-if simulation for Gulf of Mexico scenario.
"""


def rank_candidates(candidates: list, source: dict, spill: dict) -> list:
    """
    Mock P4: ranks candidate vessels by evidence strength.
    """

    rankings = [
        # Candidate 1 -- MV Gulf Star -- strongest evidence
        {
            "mmsi": "123456789",
            "rank": 1,
            "score": 0.92,
            "supporting_evidence": [
                "Vessel passed through estimated source region at release time",
                "Track trajectory closely matches backward drift path",
                "Time of passage is within the estimated release window (0.5 hr)",
                "Speed and heading consistent with source location approach",
                "Simulated spill polygon significantly overlaps detected spill",
            ],
            "contradictory_evidence": [
                "AIS transmission gap is relatively short (may indicate normal passage)",
            ]
        },

        # Candidate 2 -- MV Coastal Voyager -- moderate evidence
        {
            "mmsi": "234567890",
            "rank": 2,
            "score": 0.61,
            "supporting_evidence": [
                "Vessel was near source region boundary",
                "Time of passage partially compatible with release window",
                "Heading broadly consistent with source approach",
            ],
            "contradictory_evidence": [
                "Distance from exact source centroid is above 10 km",
                "Time difference (1.2 hr) falls near edge of release window",
            ]
        },

        # Candidate 3 -- MV Sea Wanderer -- weak evidence
        {
            "mmsi": "345678901",
            "rank": 3,
            "score": 0.28,
            "supporting_evidence": [
                "Vessel was in the broader search area",
            ],
            "contradictory_evidence": [
                "Distance from source (28.5 km) is significantly above threshold",
                "Time difference (3.8 hr) falls outside the estimated release window",
                "Track does not intersect backward drift path",
            ]
        },

        # Candidate 4 -- MV Gulf Runner -- contradictory evidence
        {
            "mmsi": "456789012",
            "rank": 4,
            "score": 0.18,
            "supporting_evidence": [
                "Vessel was relatively close in time (0.8 hr)",
            ],
            "contradictory_evidence": [
                "Vessel heading (310 deg NW) moves AWAY from source region",
                "Track trajectory does not match any simulated backward particle path",
                "Vessel speed is unusually high suggesting transit, not loitering",
                "Simulated spill polygon has minimal overlap with detected spill",
            ]
        },
    ]

    return rankings


def simulate(mmsi: str, source: dict, spill: dict) -> dict:
    """
    Mock P4 what-if simulation:
    'If vessel MMSI was the source, what would the spill look like in Gulf of Mexico?'
    """

    simulations = {
        "123456789": {
            "type": "Polygon",
            "coordinates": [[
                [-88.42, 28.82],
                [-88.28, 28.82],
                [-88.23, 28.73],
                [-88.33, 28.63],
                [-88.48, 28.66],
                [-88.51, 28.76],
                [-88.42, 28.82]
            ]]
        },
        "234567890": {
            "type": "Polygon",
            "coordinates": [[
                [-88.50, 28.68],
                [-88.32, 28.70],
                [-88.25, 28.60],
                [-88.38, 28.50],
                [-88.55, 28.52],
                [-88.58, 28.63],
                [-88.50, 28.68]
            ]]
        },
        "345678901": {
            "type": "Polygon",
            "coordinates": [[
                [-88.25, 28.85],
                [-88.10, 28.88],
                [-88.05, 28.78],
                [-88.18, 28.68],
                [-88.32, 28.70],
                [-88.32, 28.80],
                [-88.25, 28.85]
            ]]
        },
        "456789012": {
            "type": "Polygon",
            "coordinates": [[
                [-88.62, 28.65],
                [-88.45, 28.68],
                [-88.40, 28.58],
                [-88.52, 28.48],
                [-88.68, 28.50],
                [-88.70, 28.60],
                [-88.62, 28.65]
            ]]
        },
    }

    polygon = simulations.get(mmsi, {
        "type": "Polygon",
        "coordinates": [[
            [-88.40, 28.85],
            [-88.25, 28.85],
            [-88.20, 28.75],
            [-88.30, 28.65],
            [-88.45, 28.68],
            [-88.48, 28.78],
            [-88.40, 28.85]
        ]]
    })

    return {
        "mmsi": mmsi,
        "predicted_polygons": [polygon]
    }
