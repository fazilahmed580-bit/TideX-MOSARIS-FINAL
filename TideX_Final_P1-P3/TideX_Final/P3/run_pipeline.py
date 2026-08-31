import argparse
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
import json
import os

from src.main import find_candidates, generate_outputs

def main():
    parser = argparse.ArgumentParser(description="TideX P3 - AIS Vessel Analysis Pipeline")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    default_aoi = os.path.join(base_dir, "data", "spill_aoi.geojson")
    default_ais = os.path.join(base_dir, "data", "synthetic_ais.csv")
    
    parser.add_argument("--aoi", type=str, default=default_aoi,
                        help="Path to the spatial AOI (GeoJSON).")
    parser.add_argument("--ais", type=str, default=default_ais,
                        help="Path to the AIS data CSV.")
    parser.add_argument("--time-start", type=str, default=None,
                        help="Start of the analysis time window (ISO format).")
    parser.add_argument("--time-end", type=str, default=None,
                        help="End of the analysis time window (ISO format).")
    
    args = parser.parse_args()

    # Determine time window
    # If using the default synthetic data but time window is not provided, use the known regression window.
    # Otherwise, require a time window.
    if args.time_start and args.time_end:
        time_window = (args.time_start, args.time_end)
    else:
        # Fallback to regression test window if using synthetic_ais.csv
        if "synthetic_ais.csv" in args.ais:
            print("Notice: No time window provided. Using the synthetic regression time window.")
            time_window = ('2021-10-09T11:01:00+08:00', '2021-10-09T18:01:00+08:00')
        else:
            raise ValueError("Error: --time-start and --time-end must be provided for the analysis.")

    out_dir = os.path.join(base_dir, "outputs")
    os.makedirs(out_dir, exist_ok=True)
    
    geojson_path = os.path.join(out_dir, "candidates.geojson")
    json_path = os.path.join(out_dir, "candidate_features.json")
    
    print("Running P3 Pipeline...")
    print(f"AOI: {args.aoi}")
    print(f"AIS Data: {args.ais}")
    print(f"Time Window: {time_window[0]} to {time_window[1]}")
    
    candidates = find_candidates(args.aoi, time_window, args.ais)
    
    meaningful_candidates = candidates[candidates['spatial_compatible'] == True]
    
    if len(meaningful_candidates) == 0:
        print("\nNo meaningful candidates found within the specified spatial threshold.")
        print("Limitation: The available AIS data does not contain any vessels near the real P1 AOI (Gulf of Mexico).")
        print("Note: If using real P1 AOI with synthetic Taiwan AIS, 0 meaningful candidates are expected as they are in different regions.")
        # Proceed to output the ranking anyway for completeness or return
        
    if len(candidates) == 0:
        print("\nNo candidates found at all.")
        generate_outputs(candidates, geojson_path, json_path)
        return

    # Show final candidate table
    print("\n==================================================")
    print("FINAL CANDIDATE TABLE")
    print("==================================================")
    
    display_cols = ['mmsi', 'vessel_name', 'candidate_score', 'distance_km', 'time_difference_minutes']
    if 'mean_speed_knots' in candidates.columns:
        display_cols.append('mean_speed_knots')
        
    print(candidates[[c for c in display_cols if c in candidates.columns]].to_string(index=False))
    
    print("\n==================================================")
    print("IMPORTANT EVIDENCE")
    print("==================================================")
    for idx, row in candidates.iterrows():
        print(f"\nCandidate: {row['vessel_name']} (MMSI: {row['mmsi']}) - Score: {row['candidate_score']}")
        for ev in row['evidence']:
            print(f"  - {ev}")
            
    # Generate outputs
    generate_outputs(candidates, geojson_path, json_path)
    print("\n==================================================")
    print("OUTPUTS GENERATED")
    print("==================================================")
    print(f"1. GeoJSON output: {geojson_path}")
    print(f"2. JSON output: {json_path}")
    print("Done.")

if __name__ == "__main__":
    main()
