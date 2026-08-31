import numpy as np
import pandas as pd
from drift import ParticleDriftSimulation
from backtrack import _coords_to_geojson_polygon, _sample_points_in_polygon


def forecast(source_region, start_time, duration_hours=24, num_particles=500, env=None):
    """
    Perform forward Lagrangian oil-spill trajectory forecast.

    Parameters:
    -----------
    source_region : dict or tuple
        GeoJSON Feature / Polygon dict of estimated spill source, or (center_lat, center_lon).
    start_time : str or pd.Timestamp
        Timestamp of release / forecast start.
    duration_hours : float
        Hours to forecast into the future.
    num_particles : int
        Number of Lagrangian particles (default: 500).
    env : Environment instance (optional)

    Returns:
    --------
    dict containing GeoJSON structures:
        - future_trajectories (GeoJSON FeatureCollection)
        - forecast_uncertainty_polygon (GeoJSON Feature / Polygon)
    """
    print(f"[Forecast] Initializing {num_particles} particles at start time {start_time}...")
    if isinstance(source_region, dict) and "geometry" in source_region:
        geom_polygon = source_region["geometry"]
    else:
        geom_polygon = source_region

    init_lats, init_lons = _sample_points_in_polygon(geom_polygon, num_particles=num_particles)

    sim = ParticleDriftSimulation(env=env)
    res = sim.run_simulation(
        initial_lats=init_lats,
        initial_lons=init_lons,
        start_time=start_time,
        duration_hours=duration_hours,
        dt_seconds=3600,
        mode='forward'
    )

    final_lats = res["final_lats"]
    final_lons = res["final_lons"]
    trajectories = res["trajectories"]

    # 1. Future Trajectories FeatureCollection
    trajectory_features = []
    for i, path in enumerate(trajectories):
        coords = [[pt["lon"], pt["lat"]] for pt in path]
        feature = {
            "type": "Feature",
            "properties": {
                "particle_id": i,
                "start_time": path[0]["timestamp"],
                "end_time": path[-1]["timestamp"]
            },
            "geometry": {
                "type": "LineString",
                "coordinates": coords
            }
        }
        trajectory_features.append(feature)

    future_trajectories = {
        "type": "FeatureCollection",
        "features": trajectory_features
    }

    # 2. Forecast Uncertainty Polygon at final forecast time
    uncertainty_geom = _coords_to_geojson_polygon(final_lons, final_lats, use_convex_hull=True)
    forecast_uncertainty_polygon = {
        "type": "Feature",
        "properties": {
            "description": "Forecasted spill spread envelope at end of simulation",
            "forecast_start_time": str(start_time),
            "forecast_end_time": res["timestamps"][-1].strftime("%Y-%m-%dT%H:%M:%SZ"),
            "duration_hours": duration_hours
        },
        "geometry": uncertainty_geom
    }

    print("[Forecast] Completed successfully.")
    return {
        "future_trajectories": future_trajectories,
        "forecast_uncertainty_polygon": forecast_uncertainty_polygon
    }
