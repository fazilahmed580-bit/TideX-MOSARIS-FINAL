import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString
import numpy as np

def circular_mean(angles):
    """Calculate mean of circular angles in degrees."""
    angles = np.array(angles)
    valid_angles = angles[~np.isnan(angles)]
    if len(valid_angles) == 0:
        return np.nan
    rads = np.deg2rad(valid_angles)
    sin_mean = np.mean(np.sin(rads))
    cos_mean = np.mean(np.cos(rads))
    mean_angle = np.rad2deg(np.arctan2(sin_mean, cos_mean))
    return mean_angle % 360

def spatial_filter(trajectories_gdf, aoi_gdf, max_dist_km=20.0):
    """
    Determine if vessels came close to AOI.
    Returns GDF with spatial metrics.
    """
    # Reproject to dynamic UTM Zone for distance calculation in meters
    utm_crs = aoi_gdf.estimate_utm_crs()
    traj_utm = trajectories_gdf.to_crs(utm_crs)
    aoi_utm = aoi_gdf.to_crs(utm_crs)
    
    aoi_geom = aoi_utm.geometry.iloc[0]
    
    distances_km = []
    intersects = []
    closest_points = []
    
    for geom in traj_utm.geometry:
        # Distance calculation
        dist_m = geom.distance(aoi_geom)
        distances_km.append(dist_m / 1000.0)
        
        # Intersects / touches
        intersects.append(geom.intersects(aoi_geom) or geom.touches(aoi_geom))
        
        # Closest point from trajectory to AOI
        # nearest_points returns (pt1 on geom1, pt2 on geom2)
        from shapely.ops import nearest_points
        if not geom.is_empty and not aoi_geom.is_empty:
            p1, p2 = nearest_points(geom, aoi_geom)
            # p1 is the closest point on the trajectory (in UTM)
            closest_points.append(p1)
        else:
            closest_points.append(None)
        
    trajectories_gdf['distance_km'] = distances_km
    trajectories_gdf['intersects_aoi'] = intersects
    trajectories_gdf['spatial_compatible'] = trajectories_gdf['distance_km'] <= max_dist_km
    
    # Convert closest points back to WGS84 for reporting
    if any(p is not None for p in closest_points):
        closest_pts_gdf = gpd.GeoSeries(closest_points, crs=traj_utm.crs).to_crs(epsg=4326)
        trajectories_gdf['closest_point_to_aoi'] = closest_pts_gdf.values
    else:
        trajectories_gdf['closest_point_to_aoi'] = None
        
    return trajectories_gdf

def temporal_filter(trajectories_gdf, time_start, time_end, max_time_diff_minutes=120):
    """
    Determine if vessels are temporally compatible.
    """
    time_start = pd.to_datetime(time_start, utc=True)
    time_end = pd.to_datetime(time_end, utc=True)
    target_time = time_start + (time_end - time_start) / 2 # Midpoint of window for distance
    
    first_times = []
    last_times = []
    time_diffs = []
    time_to_targets = []
    temporal_compats = []
    
    for idx, row in trajectories_gdf.iterrows():
        pts_df = row['points_data']
        times = pts_df['timestamp']
        
        first_times.append(times.min())
        last_times.append(times.max())
        
        # Closest time to the window [time_start, time_end]
        # If any point is inside the window, diff is 0
        in_window = (times >= time_start) & (times <= time_end)
        if in_window.any():
            min_diff = 0.0
        else:
            diff_to_start = (time_start - times).dt.total_seconds() / 60.0
            diff_to_end = (times - time_end).dt.total_seconds() / 60.0
            # If all times are before start, min diff is to start
            if (times < time_start).all():
                min_diff = diff_to_start.min()
            else:
                min_diff = diff_to_end.min()
                
        # Time distance to the target midpoint (in minutes)
        target_diff = (times - target_time).abs().min().total_seconds() / 60.0
        
        time_diffs.append(abs(min_diff))
        time_to_targets.append(target_diff)
        temporal_compats.append(abs(min_diff) <= max_time_diff_minutes)
        
    trajectories_gdf['first_ais_time'] = first_times
    trajectories_gdf['last_ais_time'] = last_times
    trajectories_gdf['time_difference_minutes'] = time_diffs
    trajectories_gdf['time_to_target_minutes'] = time_to_targets
    trajectories_gdf['temporal_compatible'] = temporal_compats
    
    return trajectories_gdf

def kinematics_analysis(trajectories_gdf):
    """
    Calculate speed and heading statistics.
    """
    mean_speeds, median_speeds, min_speeds, max_speeds = [], [], [], []
    mean_headings = []
    speed_compats = []
    heading_compats = []
    
    for idx, row in trajectories_gdf.iterrows():
        pts_df = row['points_data']
        speeds = pts_df['sog_knots'].dropna()
        headings = pts_df['heading_deg'].dropna()
        if len(headings) == 0:
            headings = pts_df['cog_deg'].dropna() # fallback to COG
            
        if len(speeds) > 0:
            mean_s = speeds.mean()
            median_s = speeds.median()
            min_s = speeds.min()
            max_s = speeds.max()
        else:
            mean_s, median_s, min_s, max_s = 0, 0, 0, 0
            
        if len(headings) > 0:
            mean_h = circular_mean(headings)
        else:
            mean_h = np.nan
            
        mean_speeds.append(mean_s)
        median_speeds.append(median_s)
        min_speeds.append(min_s)
        max_speeds.append(max_s)
        mean_headings.append(mean_h)
        
        # Heuristic for speed: moving but not impossibly fast
        speed_compats.append(mean_s >= 1.0 and mean_s <= 30.0)
        
        # Heading compatibility - just checking if we have valid heading data for now.
        heading_compats.append(not np.isnan(mean_h))
        
    trajectories_gdf['mean_speed_knots'] = mean_speeds
    trajectories_gdf['median_speed_knots'] = median_speeds
    trajectories_gdf['min_speed_knots'] = min_speeds
    trajectories_gdf['max_speed_knots'] = max_speeds
    trajectories_gdf['mean_heading_deg'] = mean_headings
    trajectories_gdf['speed_compatible'] = speed_compats
    trajectories_gdf['heading_compatible'] = heading_compats
    
    return trajectories_gdf

def trajectory_consistency(trajectories_gdf, aoi_gdf):
    """
    Determine if trajectory approaches, passes near, intersects, or moves away.
    """
    utm_crs = aoi_gdf.estimate_utm_crs()
    aoi_utm = aoi_gdf.to_crs(utm_crs).geometry.iloc[0]
    traj_utm = trajectories_gdf.to_crs(utm_crs)
    
    consistencies = []
    evidence_list = []
    
    for idx, row in traj_utm.iterrows():
        pts = row['points_data'].sort_values(by='timestamp')
        if len(pts) < 2:
            consistencies.append(False)
            evidence_list.append(["Insufficient data points for trajectory consistency."])
            continue
            
        # Convert points to UTM to calculate distances over time
        pts_gdf = gpd.GeoDataFrame(pts, geometry=gpd.points_from_xy(pts.longitude, pts.latitude), crs="EPSG:4326")
        pts_utm = pts_gdf.to_crs(utm_crs)
        
        distances = pts_utm.geometry.apply(lambda p: p.distance(aoi_utm) / 1000.0).values
        
        evidence = []
        is_consistent = False
        
        if row['intersects_aoi']:
            evidence.append("Trajectory intersects the AOI.")
            is_consistent = True
        
        dist_change = distances[-1] - distances[0]
        min_dist_idx = np.argmin(distances)
        
        if min_dist_idx > 0 and min_dist_idx < len(distances) - 1:
            evidence.append("Trajectory approaches the AOI, passes near it, and then moves away.")
            is_consistent = True
        elif dist_change < -5.0: # moved at least 5km closer
            evidence.append("Trajectory approaches the AOI.")
            is_consistent = True
        elif dist_change > 5.0 and distances[0] < 10.0:
            evidence.append("Trajectory moves away from the AOI vicinity.")
            is_consistent = True
        elif distances.min() < 5.0:
            evidence.append("Trajectory remains in close proximity to the AOI.")
            is_consistent = True
        else:
            evidence.append("Trajectory remains unrelated or far from the AOI.")
            
        consistencies.append(is_consistent)
        evidence_list.append(evidence)
        
    trajectories_gdf['trajectory_consistent'] = consistencies
    trajectories_gdf['consistency_evidence'] = evidence_list
    
    return trajectories_gdf

def score_candidates(trajectories_gdf):
    """
    Generate an explainable, discriminative candidate-relevance score (0 to 100).
    """
    scores = []
    all_evidence = []
    
    for idx, row in trajectories_gdf.iterrows():
        score = 0.0
        evidence = []
        
        # Base evidence from consistency
        evidence.extend(row['consistency_evidence'])
        
        # Spatial score (0 to 40 points)
        if row['spatial_compatible']:
            dist = row['distance_km']
            if row['intersects_aoi']:
                num_pts = row.get('num_points', len(row['points_data']) if 'points_data' in row else 1)
                # Direct intersection: 35 to 40 points based on observation density
                spatial_score = round(35.0 + min(5.0, (num_pts / 300.0) * 5.0), 1)
            else:
                spatial_score = round(max(0.0, 35.0 - (dist * 1.4)), 1)
            score += spatial_score
            evidence.append(f"Spatially compatible: Distance {dist:.2f} km (Score: {spatial_score:.1f}/40)")
        else:
            evidence.append(f"Spatially incompatible: Distance {row['distance_km']:.2f} km")
            
        # Temporal score (0 to 30 points)
        if row['temporal_compatible']:
            time_diff = row['time_difference_minutes']
            if time_diff == 0.0:
                # Inside window: score 24 to 30 based on proximity to target/midpoint time
                target_diff_min = row.get('time_to_target_minutes', 0.0)
                temp_score = round(30.0 - min(6.0, (target_diff_min / 60.0) * 1.2), 1)
            else:
                temp_score = round(max(0.0, 24.0 - (time_diff / 5.0)), 1)
            score += temp_score
            evidence.append(f"Temporally compatible: Time diff {time_diff:.1f} min (Score: {temp_score:.1f}/30)")
        else:
            evidence.append(f"Temporally incompatible: Time diff {row['time_difference_minutes']:.1f} min")
            
        # Speed score (0 to 10 points) - Continuous operational plausibility
        if row['speed_compatible']:
            mean_s = row['mean_speed_knots']
            if 7.0 <= mean_s <= 15.0:
                speed_score = round(10.0 - abs(mean_s - 11.0) * 0.25, 1)
            elif 3.0 <= mean_s < 7.0:
                speed_score = round(6.5 + (mean_s - 3.0) * 0.5, 1)
            elif 15.0 < mean_s <= 22.0:
                speed_score = round(8.5 - (mean_s - 15.0) * 0.5, 1)
            else:
                speed_score = round(max(1.0, 5.0 - abs(mean_s - 2.0) * 0.5), 1)
            score += speed_score
            evidence.append(f"Speed compatible: Mean SOG {mean_s:.1f} knots (Score: {speed_score:.1f}/10)")
        else:
            mean_s = row.get('mean_speed_knots', 0.0)
            evidence.append(f"Speed incompatible: Mean SOG {mean_s:.1f} knots")
            
        # Trajectory consistency bonus (0 to 20 points)
        if row['trajectory_consistent']:
            if row['intersects_aoi']:
                has_approach_evidence = any("approaches" in ev for ev in row['consistency_evidence'])
                consistency_score = 20.0 if has_approach_evidence else 17.0
            elif row['distance_km'] <= 5.0:
                consistency_score = round(15.0 - (row['distance_km'] * 1.0), 1)
            else:
                consistency_score = round(max(5.0, 12.0 - (row['distance_km'] * 0.4)), 1)
            score += consistency_score
            evidence.append(f"Trajectory consistent with passing/approaching AOI (Score: {consistency_score:.1f}/20)")
            
        final_score = min(100.0, max(0.0, round(score, 1)))
        scores.append(final_score)
        all_evidence.append(evidence)
        
    trajectories_gdf['candidate_score'] = scores
    trajectories_gdf['evidence'] = all_evidence
    
    # Rank candidates by score
    trajectories_gdf = trajectories_gdf.sort_values(by='candidate_score', ascending=False).reset_index(drop=True)
    
    return trajectories_gdf

