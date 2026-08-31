import os
import json
from environment import Environment
from backtrack import backtrack
from forecast import forecast
from p1_loader import load_p1_data, check_environmental_compatibility


def run_p2_demo():
    print("=" * 60)
    print("TideX P2 MVP Lagrangian Oil-Spill Drift Demonstration (Synthetic Mode)")
    print("=" * 60)

    # 1. Initialize Environmental Handler
    print("\n[Step 1] Initializing Environmental Data (ERA5 & CMEMS)...")
    env = Environment()

    # 2. Define Synthetic Observed Spill Polygon near 15.0 N, 72.0 E
    observation_time = "2026-08-02T12:00:00Z"
    synthetic_spill_polygon = {
        "type": "Polygon",
        "coordinates": [[
            [71.98, 14.98],
            [72.02, 14.98],
            [72.02, 15.02],
            [71.98, 15.02],
            [71.98, 14.98]
        ]]
    }

    print(f"\n[Step 2] Synthetic Spill Observed at Lat 15.0, Lon 72.0")
    print(f"Observation Time: {observation_time}")

    # 3. Run Backtrack Simulation (24-hour hindcast)
    print("\n[Step 3] Running Backtrack (Hindcast) 24 hours into the past...")
    backtrack_results = backtrack(
        spill_polygon=synthetic_spill_polygon,
        observation_time=observation_time,
        duration_hours=24,
        num_particles=500,
        env=env
    )

    probable_source = backtrack_results["probable_source_region"]
    back_trajectories = backtrack_results["backward_trajectories"]
    back_uncertainty = backtrack_results["uncertainty_polygon"]

    print("\n--- BACKTRACK RESULTS SUMMARY ---")
    print(f"Probable Source Region Geometry Type: {probable_source['geometry']['type']}")
    print(f"Estimated Origin Time             : {probable_source['properties']['estimated_origin_time']}")
    print(f"Backward Trajectories Count       : {len(back_trajectories['features'])} particle paths")
    print(f"Uncertainty Polygon Geometry Type : {back_uncertainty['geometry']['type']}")

    # 4. Run Forecast Simulation (24-hour forecast from estimated origin)
    origin_start_time = probable_source['properties']['estimated_origin_time']
    print(f"\n[Step 4] Running Forecast 24 hours into the future starting from estimated origin ({origin_start_time})...")
    forecast_results = forecast(
        source_region=probable_source,
        start_time=origin_start_time,
        duration_hours=24,
        num_particles=500,
        env=env
    )

    fwd_trajectories = forecast_results["future_trajectories"]
    fwd_uncertainty = forecast_results["forecast_uncertainty_polygon"]

    print("\n--- FORECAST RESULTS SUMMARY ---")
    print(f"Forward Trajectories Count        : {len(fwd_trajectories['features'])} particle paths")
    print(f"Forecast Uncertainty Geometry Type: {fwd_uncertainty['geometry']['type']}")
    print(f"Forecast End Time                 : {fwd_uncertainty['properties']['forecast_end_time']}")

    # 5. Print GeoJSON Samples
    print("\n" + "=" * 60)
    print("GEOJSON OUTPUT DEMONSTRATION SAMPLES")
    print("=" * 60)

    print("\n1. Probable Source Region GeoJSON:")
    print(json.dumps(probable_source, indent=2))

    print("\n2. Sample Backward Trajectory Feature (Particle 0):")
    print(json.dumps(back_trajectories['features'][0], indent=2))

    print("\n3. Forecast Uncertainty Envelope GeoJSON:")
    print(json.dumps(fwd_uncertainty, indent=2))

    print("\n4. Sample Forward Trajectory Feature (Particle 0):")
    print(json.dumps(fwd_trajectories['features'][0], indent=2))

    print("\n" + "=" * 60)
    print("SUCCESS: Synthetic P2 MVP Lagrangian simulation completed cleanly!")
    print("=" * 60)
    return {
        "status": "COMPLETED",
        "env": env,
        "backtrack_results": backtrack_results,
        "forecast_results": forecast_results,
        "probable_source_region": probable_source,
        "backward_trajectories": back_trajectories,
        "forecast_uncertainty_polygon": fwd_uncertainty,
        "future_trajectories": fwd_trajectories
    }


def run_p1_demo(env=None):
    print("\n" + "=" * 60)
    print("TideX Real P1 Spill Integration Mode")
    print("=" * 60)

    # 1. Load P1 outputs dynamically
    print("\n[Step 1] Loading P1 Satellite Spill Detection Outputs dynamically...")
    p1_info = load_p1_data(
        geojson_path='data/spill_aoi.geojson',
        metadata_path='data/metadata.json'
    )

    centroid = p1_info["centroid"]
    bounds = p1_info["aoi_bounds"]
    metadata = p1_info["metadata"]
    obs_date = p1_info["observation_date"]

    print("\n--- REAL P1 SPILL DETECTION REPORT ---")
    print(f"Spill Detected          : {metadata.get('spill_detected')}")
    print(f"Detection Confidence    : {metadata.get('confidence')}")
    print(f"Area (km²)              : {metadata.get('area_km2')}")
    print(f"Total Polygons (AOI)    : {p1_info['feature_count']}")
    print(f"CRS                     : {metadata.get('crs')}")
    print(f"Source Image            : {metadata.get('source_image')}")
    print(f"Parsed Observation Date : {obs_date}")
    print(f"Observed Spill Centroid : Lat {centroid.get('lat'):.5f}°N, Lon {centroid.get('lon'):.5f}°E")
    print(f"AOI Bounding Box        : Lon [{bounds[0]:.5f}, {bounds[2]:.5f}], Lat [{bounds[1]:.5f}, {bounds[3]:.5f}]")

    # 2. Initialize Environmental Handler if not provided
    if env is None:
        print("\n[Step 2] Initializing Environmental Forcing Handler...")
        env = Environment()

    # 3. Check Environmental Forcing Compatibility
    print("\n[Step 3] Validating Environmental Forcing Match...")
    compat = check_environmental_compatibility(p1_info, env)

    print("\n--- ENVIRONMENTAL MATCH CHECK ---")
    print(f"Available ERA5/CMEMS Dates : {compat['env_time_range'][0]} to {compat['env_time_range'][1]}")
    print(f"Available ERA5/CMEMS Grid  : Lat {compat['env_lat_range'][0]}° to {compat['env_lat_range'][1]}°N, Lon {compat['env_lon_range'][0]}° to {compat['env_lon_range'][1]}°E")
    print(f"P1 Observation Requirement : Date {obs_date}, Centroid Lat {centroid.get('lat')}°N, Lon {centroid.get('lon')}°E")

    if not compat["compatible"]:
        print("\n" + "!" * 60)
        print("REAL P1 HINDCAST STATUS: CANNOT EXECUTE (FORCING MISMATCH)")
        print("!" * 60)
        print(f"Reason: {compat['reason']}")
        print("Note: The real P1 satellite observation (2018-08-21 in Gulf of Mexico) requires matching 2018 ERA5 wind and CMEMS current forcing datasets.")
        print("As required, the simulation was not executed with invalid forcing data and no results were fabricated.")
        print("=" * 60)
        return {
            "p1_info": p1_info,
            "status": "FORCING_MISMATCH",
            "reason": compat["reason"]
        }
    else:
        # Run backtrack simulation for real P1 spill
        obs_timestamp = f"{obs_date}T12:00:00Z"
        print(f"\n[Step 4] Running Backtrack Hindcast for Real P1 Spill at {obs_timestamp}...")
        backtrack_results = backtrack(
            spill_polygon=p1_info["geojson"],
            observation_time=obs_timestamp,
            duration_hours=24,
            num_particles=500,
            env=env
        )

        # Save GeoJSON hindcast outputs to outputs/ folder
        os.makedirs("outputs", exist_ok=True)
        source_out_path = os.path.join("outputs", "p1_probable_source.geojson")
        back_trajs_out_path = os.path.join("outputs", "p1_backward_trajectories.geojson")

        probable_source = backtrack_results["probable_source_region"]
        backward_trajs = backtrack_results["backward_trajectories"]

        with open(source_out_path, "w") as f:
            json.dump(probable_source, f, indent=2)

        with open(back_trajs_out_path, "w") as f:
            json.dump(backward_trajs, f, indent=2)

        # Calculate estimated source centroid dynamically from geometry coordinates
        source_coords = probable_source["geometry"]["coordinates"][0]
        lons_pts = [pt[0] for pt in source_coords]
        lats_pts = [pt[1] for pt in source_coords]
        est_source_centroid = {
            "lat": float(sum(lats_pts) / len(lats_pts)),
            "lon": float(sum(lons_pts) / len(lons_pts))
        }
        origin_time = probable_source["properties"]["estimated_origin_time"]

        # Run 24-hour Forward Forecast from estimated origin region
        print(f"\n[Step 5] Running Forward Forecast for Real P1 Spill starting at {origin_time}...")
        forecast_results = forecast(
            source_region=probable_source,
            start_time=origin_time,
            duration_hours=24,
            num_particles=500,
            env=env
        )

        fwd_trajs_out_path = os.path.join("outputs", "p1_forward_trajectories.geojson")
        fwd_uncert_out_path = os.path.join("outputs", "p1_forecast_uncertainty.geojson")

        fwd_trajs = forecast_results["future_trajectories"]
        fwd_uncert = forecast_results["forecast_uncertainty_polygon"]

        with open(fwd_trajs_out_path, "w") as f:
            json.dump(fwd_trajs, f, indent=2)

        with open(fwd_uncert_out_path, "w") as f:
            json.dump(fwd_uncert, f, indent=2)

        print("\n" + "=" * 60)
        print("REAL P1 SIMULATION RESULTS SAVED")
        print("=" * 60)
        print(f"Probable Source File     : {source_out_path}")
        print(f"Backward Trajectories    : {back_trajs_out_path}")
        print(f"Forecast Envelope File   : {fwd_uncert_out_path}")
        print(f"Forward Trajectories     : {fwd_trajs_out_path}")
        print(f"Estimated Origin Time    : {origin_time}")
        print(f"Estimated Source Center  : Lat {est_source_centroid['lat']:.5f}°N, Lon {est_source_centroid['lon']:.5f}°E")
        print("=" * 60)

        return {
            "p1_info": p1_info,
            "status": "COMPLETED",
            "backtrack_results": backtrack_results,
            "forecast_results": forecast_results,
            "source_file": source_out_path,
            "back_trajectories_file": back_trajs_out_path,
            "forecast_uncertainty_file": fwd_uncert_out_path,
            "fwd_trajectories_file": fwd_trajs_out_path,
            "origin_time": origin_time,
            "estimated_source_centroid": est_source_centroid
        }


def test_p2_synthetic_demo():
    """Pytest test case for synthetic P2 demonstration."""
    res = run_p2_demo()
    assert res is not None
    assert "probable_source_region" in res


def test_p1_real_demo():
    """Pytest test case for real P1 Gulf of Mexico 2018 integration."""
    p1_era5 = os.path.join('data', 'era5_p1_2018.nc')
    p1_cmems = os.path.join('data', 'cmems_p1_2018.nc')
    if os.path.exists(p1_era5) and os.path.exists(p1_cmems):
        p1_env = Environment(era5_path=p1_era5, cmems_path=p1_cmems)
    else:
        p1_env = None
    res = run_p1_demo(env=p1_env)
    assert res["status"] == "COMPLETED"
    assert os.path.exists(res["source_file"])
    assert os.path.exists(res["back_trajectories_file"])
    assert os.path.exists(res["forecast_uncertainty_file"])
    assert os.path.exists(res["fwd_trajectories_file"])


if __name__ == '__main__':
    run_p2_demo()
    p1_era5 = 'data/era5_p1_2018.nc'
    p1_cmems = 'data/cmems_p1_2018.nc'
    if os.path.exists(p1_era5) and os.path.exists(p1_cmems):
        p1_env = Environment(era5_path=p1_era5, cmems_path=p1_cmems)
    else:
        p1_env = None
    run_p1_demo(env=p1_env)
