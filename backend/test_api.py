"""
Quick test script to validate the API endpoints are working correctly.
Run this while the server is running:
  python test_api.py
"""
import urllib.request
import json
import sys

BASE_URL = "http://127.0.0.1:8000"


def get(path):
    req = urllib.request.Request(f"{BASE_URL}{path}", method="GET")
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())


def post(path, body):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())


def test_404():
    """Test that an unknown spill ID returns 404."""
    try:
        post("/investigate", {"spill_id": "unknown_999"})
        print("[FAIL] 404 test: expected HTTPError, got success")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"[PASS] 404 test: got expected 404 for unknown spill ID")
        else:
            print(f"[FAIL] 404 test: expected 404, got {e.code}")


print("=" * 60)
print("TideX MOSARIS API Test Suite")
print("=" * 60)

# Test 1: GET /
print("\n[TEST] GET /")
result = get("/")
assert result["status"] == "ok", f"Expected 'ok', got {result['status']}"
print(f"  [PASS] status={result['status']}")
print(f"  [PASS] service={result['service']}")

# Test 2: POST /spill
print("\n[TEST] POST /spill")
result = post("/spill", {"spill_id": "demo_001"})
assert "demo_001" in result["message"]
print(f"  [PASS] {result['message']}")

# Test 3: POST /spill/demo_001/detect
print("\n[TEST] POST /spill/demo_001/detect")
result = post("/spill/demo_001/detect", {})
assert result["spill_detected"] == True
assert result["confidence"] == 0.91
assert result["polygon"]["type"] == "Polygon"
assert len(result["polygon"]["coordinates"][0]) >= 4
print(f"  [PASS] spill_detected={result['spill_detected']}")
print(f"  [PASS] confidence={result['confidence']}")
print(f"  [PASS] polygon is valid GeoJSON Polygon")

# Test 4: POST /spill/demo_001/backtrack
print("\n[TEST] POST /spill/demo_001/backtrack")
result = post("/spill/demo_001/backtrack", {})
assert result["origin_region"]["type"] == "Polygon"
assert result["uncertainty_polygon"]["type"] == "Polygon"
assert len(result["backward_particles"]) > 0
print(f"  [PASS] origin_region is valid GeoJSON Polygon")
print(f"  [PASS] backward_particles={len(result['backward_particles'])} points")

# Test 5: GET /spill/demo_001/candidates
print("\n[TEST] GET /spill/demo_001/candidates")
result = get("/spill/demo_001/candidates")
candidates = result["candidates"]
assert len(candidates) == 4
for c in candidates:
    assert c["track"]["type"] == "LineString"
print(f"  [PASS] candidates found: {len(candidates)}")
for c in candidates:
    print(f"  [PASS] MMSI {c['mmsi']} track is valid LineString")

# Test 6: POST /spill/demo_001/simulate
print("\n[TEST] POST /spill/demo_001/simulate")
result = post("/spill/demo_001/simulate", {"mmsi": "123456789"})
assert result["mmsi"] == "123456789"
assert len(result["predicted_polygons"]) > 0
assert result["predicted_polygons"][0]["type"] == "Polygon"
print(f"  [PASS] mmsi={result['mmsi']}")
print(f"  [PASS] predicted_polygons={len(result['predicted_polygons'])}")

# Test 7: GET /spill/demo_001/ranking
print("\n[TEST] GET /spill/demo_001/ranking")
result = get("/spill/demo_001/ranking")
rankings = result["rankings"]
assert len(rankings) == 4
assert rankings[0]["score"] >= rankings[1]["score"]  # sorted by score descending
print(f"  [PASS] rankings returned: {len(rankings)}")
print(f"  [PASS] top MMSI={rankings[0]['mmsi']} score={rankings[0]['score']}")
assert "disclaimer" in result
print(f"  [PASS] disclaimer present")

# Test 8: POST /investigate (MAIN TEST)
print("\n[TEST] POST /investigate (MASTER PIPELINE)")
result = post("/investigate", {"spill_id": "demo_001"})

# Verify spill
assert result["spill"]["spill_id"] == "demo_001"
assert result["spill"]["spill_detected"] == True
assert result["spill"]["polygon"]["type"] == "Polygon"
print(f"  [PASS] P1 spill detected, confidence={result['spill']['confidence']}")

# Verify source
assert result["source"]["origin_region"]["type"] == "Polygon"
assert len(result["source"]["backward_particles"]) > 0
print(f"  [PASS] P2 source backtracked, backward_particles={len(result['source']['backward_particles'])}")

# Verify candidates
assert len(result["candidates"]) == 4
for c in result["candidates"]:
    assert c["track"]["type"] == "LineString"
print(f"  [PASS] P3 candidates={len(result['candidates'])}")

# Verify ranking
assert len(result["ranking"]) == 4
top = result["ranking"][0]
assert 0.0 <= top["score"] <= 1.0
assert len(top["supporting_evidence"]) > 0
print(f"  [PASS] P4 ranking complete, top={top['mmsi']} score={top['score']}")

# Verify forecast
assert len(result["forecast"]) > 0
assert len(result["forecast"][0]) == 2  # [lon, lat]
print(f"  [PASS] P2 forecast={len(result['forecast'])} future positions")

# Verify simulations
assert len(result["simulations"]) == 4
for sim in result["simulations"]:
    assert len(sim["predicted_polygons"]) > 0
print(f"  [PASS] P4 simulations={len(result['simulations'])}")

# Test 9: 404 on unknown spill ID
print("\n[TEST] 404 on unknown spill ID")
test_404()

print("\n" + "=" * 60)
print("ALL TESTS PASSED")
print("=" * 60)
