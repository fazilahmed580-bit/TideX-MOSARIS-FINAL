import pandas as pd
import geopandas as gpd
from shapely.geometry import shape, Polygon, MultiPolygon
from shapely.geometry.base import BaseGeometry
import json

from .ais_loader import clean_ais
from .trajectory import build_trajectories, trajectories_to_geojson
from .filter import (
    spatial_filter, 
    temporal_filter, 
    kinematics_analysis, 
    trajectory_consistency, 
    score_candidates
)

def normalize_source_region(source_region):
    """
    Ensure the source region is a GeoDataFrame with EPSG:4326.
    Computes unary_union to handle MultiPolygon or multiple features properly.
    """
    import os
    if isinstance(source_region, gpd.GeoDataFrame):
        gdf = source_region
    elif isinstance(source_region, gpd.GeoSeries):
        gdf = gpd.GeoDataFrame(geometry=source_region)
    elif isinstance(source_region, BaseGeometry): # Shapely geometry
        gdf = gpd.GeoDataFrame(geometry=[source_region], crs="EPSG:4326")
    elif isinstance(source_region, str): # GeoJSON string or file path
        if os.path.exists(source_region):
            gdf = gpd.read_file(source_region)
        else:
            # Try to parse as JSON string
            import json
            try:
                geom = shape(json.loads(source_region))
                gdf = gpd.GeoDataFrame(geometry=[geom], crs="EPSG:4326")
            except json.JSONDecodeError:
                raise ValueError("source_region string must be a valid file path or valid GeoJSON string.")
    elif isinstance(source_region, dict): # GeoJSON dict
        if 'features' in source_region:
            # FeatureCollection
            geoms = [shape(f['geometry']) for f in source_region['features'] if f.get('geometry')]
            gdf = gpd.GeoDataFrame(geometry=geoms, crs="EPSG:4326")
        elif 'geometry' in source_region:
            geom = shape(source_region['geometry'])
            gdf = gpd.GeoDataFrame(geometry=[geom], crs="EPSG:4326")
        else:
            geom = shape(source_region)
            gdf = gpd.GeoDataFrame(geometry=[geom], crs="EPSG:4326")
    else:
        raise ValueError("Unsupported source_region format. Provide a Shapely geometry, GeoJSON string/dict, GeoDataFrame, or a file path.")
        
    if gdf.crs is None:
        gdf.set_crs("EPSG:4326", inplace=True)
    elif gdf.crs != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")
        
    # Combine all geometries into a single geometry using union_all()
    combined_geom = gdf.geometry.union_all()
    # Return as a single-row GeoDataFrame
    return gpd.GeoDataFrame(geometry=[combined_geom], crs="EPSG:4326")

def find_candidates(source_region, time_window, ais_data):
    """
    Find candidate vessels based on AIS data and a source region/time window.
    
    Args:
        source_region: Spatial AOI (Polygon, GeoJSON, GeoDataFrame)
        time_window: Tuple of (start_time, end_time) e.g. ('2021-10-09T11:01:00Z', '2021-10-09T18:01:00Z')
        ais_data: Path to CSV or pandas DataFrame
        
    Returns:
        candidates_df: GeoDataFrame containing ranked candidates.
    """
    # 1. Normalize AOI
    aoi_gdf = normalize_source_region(source_region)
    
    # 2. Parse time window
    time_start, time_end = time_window
    time_start = pd.to_datetime(time_start, utc=True)
    time_end = pd.to_datetime(time_end, utc=True)
    
    # 3. Load and clean AIS
    clean_df = clean_ais(ais_data)
    
    if len(clean_df) == 0:
        return gpd.GeoDataFrame()
        
    # 4. Reconstruct trajectories
    trajectories_gdf = build_trajectories(clean_df)
    
    # 5. Spatial Filtering
    trajectories_gdf = spatial_filter(trajectories_gdf, aoi_gdf, max_dist_km=25.0)
    
    # 6. Temporal Filtering
    trajectories_gdf = temporal_filter(trajectories_gdf, time_start, time_end, max_time_diff_minutes=180)
    
    # 7. Speed / Heading Analysis
    trajectories_gdf = kinematics_analysis(trajectories_gdf)
    
    # 8. Trajectory Consistency
    trajectories_gdf = trajectory_consistency(trajectories_gdf, aoi_gdf)
    
    # 9. Candidate Ranking
    ranked_candidates = score_candidates(trajectories_gdf)
    
    return ranked_candidates

def generate_outputs(ranked_candidates, geojson_path, json_path):
    """
    Generate GeoJSON and JSON outputs.
    """
    # Exclude complex pandas dataframes from outputs
    out_gdf = ranked_candidates.drop(columns=['points_data'])
    
    # Write GeoJSON
    trajectories_to_geojson(out_gdf, geojson_path)
    
    # Write JSON features
    # Drop geometry for standard JSON
    json_df = pd.DataFrame(out_gdf.drop(columns=['geometry']))
    
    # Convert timestamps and geometries
    for col in ['start_time', 'end_time', 'first_ais_time', 'last_ais_time', 'start_pos', 'end_pos', 'closest_point_to_aoi']:
        if col in json_df.columns:
            json_df[col] = json_df[col].astype(str)
            
    json_df.to_json(json_path, orient='records', indent=4)
