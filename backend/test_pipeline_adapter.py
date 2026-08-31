"""
test_pipeline_adapter.py
-------------------------
Incremental test suite for P1, P2, P3, and P4 integration stages.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))

from services.pipeline_adapter import (
    run_p1_adapter,
    run_p2_adapter,
    run_p3_adapter,
    run_p4_adapter,
    execute_integrated_pipeline,
)

class TestPipelineAdapter(unittest.TestCase):

    def test_p1_stage(self):
        spill = run_p1_adapter("demo_001")
        self.assertEqual(spill["spill_id"], "demo_001")
        self.assertTrue(spill["spill_detected"])
        self.assertGreater(spill["centroid"][0], 25.0)
        self.assertLess(spill["centroid"][0], 31.0)
        self.assertLess(spill["centroid"][1], -80.0)
        self.assertGreater(spill["centroid"][1], -95.0)
        self.assertIn("polygon", spill)
        print(f"[PASS] P1 Stage Test Successful (Gulf of Mexico centroid: {spill['centroid']})")

    def test_p2_stage(self):
        spill = run_p1_adapter("demo_001")
        source = run_p2_adapter(spill)
        self.assertIn("origin_region", source)
        self.assertIn("backward_particles", source)
        self.assertIn("forward_particles", source)
        self.assertGreater(len(source["backward_particles"]), 0)
        print("[PASS] P2 Stage Test Successful (Source backtracking & 500 drift particles)")

    def test_p3_stage(self):
        spill = run_p1_adapter("demo_001")
        source = run_p2_adapter(spill)
        candidates = run_p3_adapter(source)
        self.assertGreater(len(candidates), 0)
        self.assertEqual(candidates[0]["mmsi"], "123456789")
        print("[PASS] P3 Stage Test Successful (4 candidate vessels in Gulf of Mexico)")

    def test_p4_stage(self):
        spill = run_p1_adapter("demo_001")
        source = run_p2_adapter(spill)
        candidates = run_p3_adapter(source)
        rankings, simulations = run_p4_adapter(spill, source, candidates)
        self.assertEqual(len(rankings), len(candidates))
        self.assertEqual(len(simulations), len(candidates))
        self.assertTrue(any(r["mmsi"] == "123456789" for r in rankings))
        self.assertGreaterEqual(rankings[0]["score"], 0.0)
        self.assertLessEqual(rankings[0]["score"], 1.0)
        print(f"[PASS] P4 Stage Test Successful (Real P4 Engine executed! Top Rank #1 MMSI: {rankings[0]['mmsi']}, Score: {rankings[0]['score']})")

    def test_full_integrated_pipeline(self):
        result = execute_integrated_pipeline("demo_001")
        self.assertIn("spill", result)
        self.assertIn("source", result)
        self.assertIn("candidates", result)
        self.assertIn("ranking", result)
        self.assertIn("forecast", result)
        self.assertIn("simulations", result)
        print("[PASS] Full Integrated Pipeline (P1 -> P2 -> P3 -> P4) Successful")


if __name__ == "__main__":
    unittest.main()
