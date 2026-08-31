import numpy as np
import pandas as pd
from drift import ParticleDriftSimulation


def _coords_to_geojson_polygon(lons, lats, use_convex_hull=True):
    """
    Generate a valid GeoJSON Polygon geometry from particle (lons, lats).
    Uses ConvexHull if available, fallback to Bounding Box.
    """
    if len(lons) < 3:
        use_convex_hull = False

    if use_convex_hull:
        try:
            from scipy.spatial import ConvexHull
            points = np.column_stack([lons, lats])
            hull = ConvexHull(points)
            hull_points = points[hull.vertices]
            # Close polygon ring
            hull_coords = [[float(pt[0]), float(pt[1])] for pt in hull_points]
            hull_coords.append(hull_coords[0])
            return {
                "type": "Polygon",
                "coordinates": [hull_coords]
            }
        except Exception:
            pass

    # Bounding box fallback
    min_lon, max_lon = float(np.min(lons)), float(np.max(lons))
    min_lat, max_lat = float(np.min(lats)), float(np.max(lats))
    bbox_coords = [
        [min_lon, min_lat],
        [max_lon, min_lat],
        [max_lon, max_lat],
        [min_lon, max_lat],
        [min_lon, min_lat]
    ]
    return {
        "type": "Polygon",
        "coordinates": [bbox_coords]
    }


def _sample_points_in_polygon(spill_polygon, num_particles=500):
    """
    Sample particles within or around input GeoJSON spill_polygon, Feature, FeatureCollection, or point.
    """
    min_lon, max_lon, min_lat, max_lat = None, None, None, None

    if isinstance(spill_polygon, dict):
        all_lons = []
        all_lats = []

        features = spill_polygon.get("features", [spill_polygon] if spill_polygon.get("type") == "Feature" else [])
        if not features and "coordinates" in spill_polygon:
            features = [{"geometry": spill_polygon}]

        for feat in features:
            geom = feat.get("geometry", feat)
            coords = geom.get("coordinates", [])
            g_type = geom.get("type", "")

            if g_type == "Polygon":
                for ring in coords:
                    for pt in ring:
                        all_lons.append(pt[0])
                        all_lats.append(pt[1])
            elif g_type == "MultiPolygon":
                for poly in coords:
                    for ring in poly:
                        for pt in ring:
                            all_lons.append(pt[0])
                            all_lats.append(pt[1])

        if all_lons and all_lats:
            min_lon, max_lon = float(np.min(all_lons)), float(np.max(all_lons))
            min_lat, max_lat = float(np.min(all_lats)), float(np.max(all_lats))

    elif isinstance(spill_polygon, (list, tuple)) and len(spill_polygon) == 2:
        center_lat, center_lon = spill_polygon
        min_lat, max_lat = center_lat - 0.05, center_lat + 0.05
        min_lon, max_lon = center_lon - 0.05, center_lon + 0.05

    if min_lon is None:
        min_lat, max_lat = 14.95, 15.05
        min_lon, max_lon = 71.95, 72.05

    lats = np.random.uniform(min_lat, max_lat, size=num_particles)
    lons = np.random.uniform(min_lon, max_lon, size=num_particles)

    return lats, lons


def backtrack(spill_polygon, observation_time, duration_hours=24, num_particles=500, env=None):
    """
    Perform backward Lagrangian oil-spill trajectory tracking.

    Parameters:
    -----------
    spill_polygon : dict or tuple
        GeoJSON Polygon dict of observed spill, or (center_lat, center_lon).
    observation_time : str or pd.Timestamp
        Timestamp of spill observation.
    duration_hours : float
        Hours to backtrack into the past.
    num_particles : int
        Number of Lagrangian particles (default: 500).
    env : Environment instance (optional)

    Returns:
    --------
    dict containing GeoJSON structures:
        - probable_source_region (GeoJSON Feature / Polygon)
        - backward_trajectories (GeoJSON FeatureCollection)
        - uncertainty_polygon (GeoJSON Feature / Polygon)
    """
    print(f"[Backtrack] Initializing {num_particles} particles at observation time {observation_time}...")
    init_lats, init_lons = _sample_points_in_polygon(spill_polygon, num_particles=num_particles)

    sim = ParticleDriftSimulation(env=env)
    res = sim.run_simulation(
        initial_lats=init_lats,
        initial_lons=init_lons,
        start_time=observation_time,
        duration_hours=duration_hours,
        dt_seconds=3600,
        mode='backward'
    )

    final_lats = res["final_lats"]
    final_lons = res["final_lons"]
    trajectories = res["trajectories"]

    # 1. Probable Source Region Polygon
    source_geom = _coords_to_geojson_polygon(final_lons, final_lats, use_convex_hull=True)
    probable_source_region = {
        "type": "Feature",
        "properties": {
            "description": "Probable oil-spill origin area",
            "observation_time": str(observation_time),
            "estimated_origin_time": res["timestamps"][-1].strftime("%Y-%m-%dT%H:%M:%SZ"),
            "particle_count": num_particles
        },
        "geometry": source_geom
    }

    # 2. Backward Trajectories FeatureCollection
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

    backward_trajectories = {
        "type": "FeatureCollection",
        "features": trajectory_features
    }

    # 3. Uncertainty Polygon at origin
    uncertainty_geom = _coords_to_geojson_polygon(final_lons, final_lats, use_convex_hull=False)
    uncertainty_polygon = {
        "type": "Feature",
        "properties": {
            "description": "Origin spatial uncertainty envelope (bounding box)",
            "area_type": "uncertainty_envelope"
        },
        "geometry": uncertainty_geom
    }

    print("[Backtrack] Completed successfully.")
    return {
        "probable_source_region": probable_source_region,
        "backward_trajectories": backward_trajectories,
        "uncertainty_polygon": uncertainty_polygon
    }
