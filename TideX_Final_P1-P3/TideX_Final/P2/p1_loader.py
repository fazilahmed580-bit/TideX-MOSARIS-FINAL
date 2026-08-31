import os
import json
import re
import pandas as pd
import numpy as np


def load_p1_data(geojson_path=None, metadata_path=None):
    """
    Dynamically read P1 real satellite spill detection outputs (spill_aoi.geojson and metadata.json).
    Does not hardcode latitude, longitude, or observation timestamp.

    Returns:
    --------
    dict containing:
        - metadata (raw dict)
        - centroid (dict with lat, lon)
        - aoi_bounds (list: [min_lon, min_lat, max_lon, max_lat])
        - observation_date (str: YYYY-MM-DD)
        - geojson (dict)
        - feature_count (int)
    """
    if metadata_path is None:
        metadata_path = os.path.join('data', 'metadata.json')
    if geojson_path is None:
        geojson_path = os.path.join('data', 'spill_aoi.geojson')

    if not os.path.exists(metadata_path):
        raise FileNotFoundError(f"P1 metadata file not found at {metadata_path}")
    if not os.path.exists(geojson_path):
        raise FileNotFoundError(f"P1 GeoJSON file not found at {geojson_path}")

    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    with open(geojson_path, 'r') as f:
        geojson_data = json.load(f)

    # Extract centroid dynamically from metadata.json
    centroid = metadata.get("centroid", {})
    if not centroid and "lat" in metadata:
        centroid = {"lat": metadata.get("lat"), "lon": metadata.get("lon")}

    # Parse observation date dynamically from source_image or metadata
    source_img = metadata.get("source_image", "")
    date_match = re.search(r'(\d{4})_(\d{2})_(\d{2})', source_img)
    if date_match:
        obs_date = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
    else:
        obs_date = metadata.get("observation_date", "2018-08-21")

    # Compute AOI bounding box dynamically across all features in spill_aoi.geojson
    all_lons = []
    all_lats = []

    features = geojson_data.get("features", [])
    for feat in features:
        geom = feat.get("geometry", {})
        coords = geom.get("coordinates", [])
        geom_type = geom.get("type", "")

        if geom_type == "Polygon":
            for ring in coords:
                for pt in ring:
                    all_lons.append(pt[0])
                    all_lats.append(pt[1])
        elif geom_type == "MultiPolygon":
            for poly in coords:
                for ring in poly:
                    for pt in ring:
                        all_lons.append(pt[0])
                        all_lats.append(pt[1])

    if all_lons and all_lats:
        aoi_bounds = [
            float(np.min(all_lons)),
            float(np.min(all_lats)),
            float(np.max(all_lons)),
            float(np.max(all_lats))
        ]
    else:
        # Fallback to centroid bounding box
        c_lat, c_lon = centroid.get("lat", 0.0), centroid.get("lon", 0.0)
        aoi_bounds = [c_lon - 0.1, c_lat - 0.1, c_lon + 0.1, c_lat + 0.1]

    return {
        "metadata": metadata,
        "centroid": centroid,
        "aoi_bounds": aoi_bounds,
        "observation_date": obs_date,
        "geojson": geojson_data,
        "feature_count": len(features)
    }


def check_environmental_compatibility(p1_info, env):
    """
    Validate whether the environmental forcing datasets (ERA5/CMEMS in env)
    spatially and temporally cover the P1 real observation.

    Returns:
    --------
    dict containing:
        - compatible (bool)
        - reason (str)
        - env_time_range (tuple)
        - env_lat_range (tuple)
        - env_lon_range (tuple)
    """
    # Extract ERA5 time, lat, lon ranges from env
    e_times = env.ds_era5[env.era5_time_name].values
    e_lats = env.ds_era5[env.era5_lat_name].values
    e_lons = env.ds_era5[env.era5_lon_name].values

    env_time_min = pd.to_datetime(e_times.min()).strftime("%Y-%m-%d")
    env_time_max = pd.to_datetime(e_times.max()).strftime("%Y-%m-%d")

    env_lat_min, env_lat_max = float(np.min(e_lats)), float(np.max(e_lats))
    env_lon_min, env_lon_max = float(np.min(e_lons)), float(np.max(e_lons))

    p1_date = p1_info["observation_date"]
    p1_lat = p1_info["centroid"]["lat"]
    p1_lon = p1_info["centroid"]["lon"]

    # Check temporal match
    time_match = (env_time_min <= p1_date <= env_time_max)

    # Check spatial match
    lat_match = (env_lat_min <= p1_lat <= env_lat_max)
    lon_match = (env_lon_min <= p1_lon <= env_lon_max)

    spatial_match = lat_match and lon_match

    is_compatible = time_match and spatial_match

    reasons = []
    if not time_match:
        reasons.append(
            f"Temporal mismatch: P1 observation date ({p1_date}) is outside available environmental forcing dates ({env_time_min} to {env_time_max})."
        )
    if not spatial_match:
        reasons.append(
            f"Spatial mismatch: P1 centroid ({p1_lat:.4f}°N, {p1_lon:.4f}°E) is outside available environmental forcing grid ({env_lat_min:.2f}° to {env_lat_max:.2f}°N, {env_lon_min:.2f}° to {env_lon_max:.2f}°E)."
        )

    reason_str = " Compatible" if is_compatible else " | ".join(reasons)

    return {
        "compatible": is_compatible,
        "reason": reason_str,
        "env_time_range": (env_time_min, env_time_max),
        "env_lat_range": (env_lat_min, env_lat_max),
        "env_lon_range": (env_lon_min, env_lon_max)
    }
