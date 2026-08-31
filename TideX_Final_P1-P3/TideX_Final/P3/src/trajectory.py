import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString
import json

def build_trajectories(clean_df):
    """
    Reconstruct vessel trajectories from clean AIS data.
    """
    trajectories = []
    
    grouped = clean_df.groupby('mmsi')
    
    for mmsi, group in grouped:
        # group is already sorted by timestamp if clean_df is sorted, but let's be sure
        group = group.sort_values(by='timestamp')
        
        vessel_name = group['vessel_name'].iloc[0]
        start_time = group['timestamp'].iloc[0]
        end_time = group['timestamp'].iloc[-1]
        num_points = len(group)
        
        start_pos = Point(group['longitude'].iloc[0], group['latitude'].iloc[0])
        end_pos = Point(group['longitude'].iloc[-1], group['latitude'].iloc[-1])
        
        points = [Point(lon, lat) for lon, lat in zip(group['longitude'], group['latitude'])]
        
        if num_points > 1:
            geometry = LineString(points)
            # approximate track length in degrees (will calculate real distance in filtering)
            track_length_deg = geometry.length
        else:
            geometry = start_pos # Just a point if only 1 observation
            track_length_deg = 0.0
            
        trajectories.append({
            'mmsi': mmsi,
            'vessel_name': vessel_name,
            'start_time': start_time,
            'end_time': end_time,
            'num_points': num_points,
            'start_pos': start_pos,
            'end_pos': end_pos,
            'track_length_deg': track_length_deg,
            'geometry': geometry,
            'points_data': group # Keep raw data for speed/heading analysis
        })
        
    return gpd.GeoDataFrame(trajectories, geometry='geometry', crs='EPSG:4326')

def trajectories_to_geojson(candidates_df, filepath=None):
    """
    Convert trajectories to GeoJSON format.
    """
    # Assuming candidates_df is a GeoDataFrame with candidate scores and evidence
    # Convert timestamps and other non-serializable fields to string
    out_df = candidates_df.copy()
    
    # Select columns to include as properties
    cols_to_keep = [
        'mmsi', 'vessel_name', 'distance_km', 'time_difference_minutes',
        'mean_speed_knots', 'median_speed_knots', 'mean_heading_deg',
        'spatial_compatible', 'temporal_compatible', 'speed_compatible',
        'heading_compatible', 'trajectory_consistent', 'candidate_score',
        'evidence', 'geometry'
    ]
    
    # filter cols that exist
    cols_to_keep = [c for c in cols_to_keep if c in out_df.columns]
    out_df = out_df[cols_to_keep]
    
    # Serialize evidence list to JSON string for GeoJSON properties if needed, or just let GeoPandas handle it
    # GeoPandas might struggle with lists in to_json
    if 'evidence' in out_df.columns:
        out_df['evidence'] = out_df['evidence'].apply(json.dumps)
        
    if filepath:
        out_df.to_file(filepath, driver="GeoJSON")
    else:
        return out_df.to_json()
