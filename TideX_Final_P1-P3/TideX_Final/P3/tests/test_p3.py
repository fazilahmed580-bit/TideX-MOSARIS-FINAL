import unittest
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
import json
import os
import shutil

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ais_loader import clean_ais
from src.trajectory import build_trajectories
from src.filter import spatial_filter, temporal_filter, kinematics_analysis, trajectory_consistency, score_candidates
from src.main import find_candidates, generate_outputs

class TestP3Module(unittest.TestCase):
    def setUp(self):
        # A simple synthetic dataset for testing
        self.test_data = pd.DataFrame({
            'mmsi': [111, 111, 222, 222],
            'vessel_name': ['V1', 'V1', 'V2', 'V2'],
            'timestamp': ['2021-10-09T12:00:00Z', '2021-10-09T13:00:00Z', '2021-10-09T12:00:00Z', '2021-10-09T13:00:00Z'],
            'latitude': [24.0, 24.1, 24.5, 24.6],
            'longitude': [120.0, 120.1, 120.5, 120.6],
            'sog_knots': [10.0, 10.5, 12.0, 12.5],
            'cog_deg': [45.0, 46.0, 90.0, 91.0],
            'heading_deg': [45.0, 46.0, 90.0, 91.0]
        })
        
        self.aoi_polygon = Polygon([
            (120.05, 24.05), (120.15, 24.05), (120.15, 24.15), (120.05, 24.15), (120.05, 24.05)
        ])
        
        self.time_window = ('2021-10-09T11:00:00Z', '2021-10-09T14:00:00Z')

    def test_ais_cleaning(self):
        # Test invalid MMSI, coordinate removal
        dirty_data = self.test_data.copy()
        dirty_data.loc[4] = [None, 'V3', '2021-10-09T14:00:00Z', 24.0, 120.0, 10, 0, 0] # missing mmsi
        dirty_data.loc[5] = [333, 'V3', '2021-10-09T14:00:00Z', 95.0, 120.0, 10, 0, 0]  # invalid lat
        
        cleaned = clean_ais(dirty_data)
        self.assertEqual(len(cleaned), 4) # Should only keep the original 4 valid points
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(cleaned['timestamp']))

    def test_trajectory_reconstruction(self):
        cleaned = clean_ais(self.test_data)
        traj_gdf = build_trajectories(cleaned)
        
        self.assertEqual(len(traj_gdf), 2)
        self.assertIn('geometry', traj_gdf.columns)
        self.assertEqual(traj_gdf[traj_gdf['mmsi'] == 111]['num_points'].iloc[0], 2)

    def test_filtering_and_scoring(self):
        candidates = find_candidates(self.aoi_polygon, self.time_window, self.test_data)
        
        self.assertEqual(len(candidates), 2)
        
        # V1 should be closer to AOI than V2
        v1_score = candidates[candidates['mmsi'] == 111]['candidate_score'].iloc[0]
        v2_score = candidates[candidates['mmsi'] == 222]['candidate_score'].iloc[0]
        
        self.assertGreater(v1_score, v2_score)

    def test_different_aoi_format(self):
        # Test if string GeoJSON is accepted
        geojson_str = json.dumps({
            "type": "Polygon",
            "coordinates": [[[120.05, 24.05], [120.15, 24.05], [120.15, 24.15], [120.05, 24.15], [120.05, 24.05]]]
        })
        candidates = find_candidates(geojson_str, self.time_window, self.test_data)
        self.assertEqual(len(candidates), 2)
        
    def test_no_taihang118(self):
        # Even without TAIHANG118, pipeline should run smoothly on other data
        # Ensure our test_data (which doesn't have TAIHANG118) runs correctly
        candidates = find_candidates(self.aoi_polygon, self.time_window, self.test_data)
        mmsis = candidates['mmsi'].tolist()
        self.assertNotIn(412065000, mmsis)
        self.assertGreater(len(candidates), 0)
        
    def test_alternative_aoi_gdf(self):
        # Provide GeoDataFrame as AOI
        aoi_gdf = gpd.GeoDataFrame(geometry=[self.aoi_polygon], crs="EPSG:4326")
        candidates = find_candidates(aoi_gdf, self.time_window, self.test_data)
        self.assertEqual(len(candidates), 2)

if __name__ == '__main__':
    unittest.main()
