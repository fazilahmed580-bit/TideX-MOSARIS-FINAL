"""
demo_pipeline.py
----------------
Run the complete MOSARIS investigation without starting the web server.
Useful for testing the pipeline quickly from the command line.

HOW TO RUN:
  Open a terminal in the backend/ folder and run:
    python demo_pipeline.py

OUTPUT:
  A readable summary of the investigation result.
"""

import sys
import json
import os

# Make sure Python can find the backend modules
sys.path.insert(0, os.path.dirname(__file__))

from pipeline import run_investigation


def print_separator(char="-", width=60):
    print(char * width)


def print_section(title):
    print_separator("=")
    print(f"  {title}")
    print_separator("=")


def run_demo():
    spill_id = "demo_001"

    print()
    print_separator("*")
    print("  TideX MOSARIS -- Demo Investigation Pipeline")
    print("  Maritime Oil-Spill Attribution & Response Intelligence System")
    print_separator("*")
    print(f"  Running investigation for spill ID: {spill_id}")
    print()

    # Run the full pipeline
    result = run_investigation(spill_id)

    # -----------------------------------------------------------------------
    # P1 -- Spill Detection
    # -----------------------------------------------------------------------
    print_section("P1 -- SPILL DETECTION")
    spill = result["spill"]
    print(f"  Spill detected:   {'YES' if spill['spill_detected'] else 'NO'}")
    print(f"  Spill ID:         {spill['spill_id']}")
    print(f"  Timestamp:        {spill['timestamp']}")
    print(f"  Centroid:         lat={spill['centroid'][0]}, lon={spill['centroid'][1]}")
    print(f"  Area:             {spill['area_km2']} km2")
    print(f"  Confidence:       {spill['confidence'] * 100:.0f}%")
    print()

    # -----------------------------------------------------------------------
    # P2 -- Source Backtracking
    # -----------------------------------------------------------------------
    print_section("P2 -- SOURCE BACKTRACKING")
    source = result["source"]
    print(f"  Origin window:    {source['origin_time_start']} to {source['origin_time_end']}")
    print(f"  Backward particles: {len(source['backward_particles'])} points")
    print(f"  Forward particles:  {len(source['forward_particles'])} points")
    print()

    # -----------------------------------------------------------------------
    # P3 -- AIS Candidates
    # -----------------------------------------------------------------------
    print_section("P3 -- AIS CANDIDATE VESSELS")
    candidates = result["candidates"]
    print(f"  Total candidates found: {len(candidates)}")
    for c in candidates:
        print(f"    MMSI {c['mmsi']}  |  {c.get('vessel_name', 'Unknown')}  "
              f"|  dist={c['distance_km']} km  |  time_diff={c['time_difference_hr']} hr")
    print()

    # -----------------------------------------------------------------------
    # P4 -- Ranking
    # -----------------------------------------------------------------------
    print_section("P4 -- CANDIDATE RANKING")
    print("  DISCLAIMER: Scores are investigation-priority scores.")
    print("  They are NOT guilt probabilities or legal findings.")
    print()
    rankings = result["ranking"]
    for r in rankings:
        name = next(
            (c.get("vessel_name", "Unknown") for c in candidates if c["mmsi"] == r["mmsi"]),
            "Unknown"
        )
        print(f"  Rank #{r['rank']}  MMSI: {r['mmsi']}  ({name})")
        print(f"    Score:          {r['score']:.2f}")
        print(f"    Supporting:     {len(r['supporting_evidence'])} items")
        for ev in r["supporting_evidence"]:
            print(f"      [+] {ev}")
        print(f"    Contradictory:  {len(r['contradictory_evidence'])} items")
        for ev in r["contradictory_evidence"]:
            print(f"      [-] {ev}")
        print()

    # -----------------------------------------------------------------------
    # P4 -- Simulations
    # -----------------------------------------------------------------------
    print_section("P4 -- WHAT-IF SIMULATIONS")
    simulations = result["simulations"]
    print(f"  Simulations generated: {len(simulations)}")
    for s in simulations:
        print(f"    MMSI {s['mmsi']}:  {len(s['predicted_polygons'])} predicted polygon(s)")
    print()

    # -----------------------------------------------------------------------
    # P2 -- Forecast
    # -----------------------------------------------------------------------
    print_section("P2 -- FORWARD FORECAST")
    forecast = result["forecast"]
    print(f"  Forecast generated:   YES")
    print(f"  Future positions:     {len(forecast)} points")
    if forecast:
        last = forecast[-1]
        print(f"  Final position:       lon={last[0]}, lat={last[1]}")
    print()

    # -----------------------------------------------------------------------
    # Top candidate summary
    # -----------------------------------------------------------------------
    print_section("INVESTIGATION SUMMARY")
    top = rankings[0]
    top_name = next(
        (c.get("vessel_name", "Unknown") for c in candidates if c["mmsi"] == top["mmsi"]),
        "Unknown"
    )
    print(f"  Top priority vessel:  {top_name}  (MMSI: {top['mmsi']})")
    print(f"  Priority score:       {top['score']:.2f}")
    print(f"  Forecast generated:   YES  ({len(forecast)} future positions)")
    print()
    print_separator("*")
    print("  Demo investigation complete.")
    print("  Start the server with:  uvicorn main:app --reload")
    print("  Then POST to:           http://127.0.0.1:8000/investigate")
    print_separator("*")
    print()


if __name__ == "__main__":
    run_demo()
