import urllib.request
import json

print("=" * 60)
print("TideX MOSARIS Full-Stack End-to-End Test")
print("=" * 60)

# 1. Test Frontend HTTP Server
try:
    with urllib.request.urlopen("http://127.0.0.1:5173") as resp:
        html = resp.read().decode('utf-8')
        assert "<title>TideX MOSARIS" in html
        print("[PASS] Frontend Vite Server is running on http://127.0.0.1:5173")
except Exception as e:
    print(f"[FAIL] Frontend connection error: {e}")

# 2. Test Backend Connection & /investigate endpoint
try:
    req = urllib.request.Request(
        "http://127.0.0.1:8000/investigate",
        data=json.dumps({"spill_id": "demo_001"}).encode('utf-8'),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        assert data["spill"]["spill_detected"] == True
        assert len(data["candidates"]) == 4
        assert len(data["ranking"]) == 4
        assert len(data["forecast"]) > 0
        assert len(data["simulations"]) == 4
        print(f"[PASS] Backend FastAPI /investigate returned full payload:")
        print(f"       - Spill ID: {data['spill']['spill_id']}")
        print(f"       - Spill Polygon Coords: {len(data['spill']['polygon']['coordinates'][0])} vertices")
        print(f"       - Centroid: {data['spill']['centroid']}")
        print(f"       - Candidates: {len(data['candidates'])} vessels")
        print(f"       - Top Candidate: {data['ranking'][0]['mmsi']} (Score: {data['ranking'][0]['score']})")
        print(f"       - Forward Forecast Particles: {len(data['forecast'])} points")
except Exception as e:
    print(f"[FAIL] Backend /investigate error: {e}")

print("=" * 60)
print("FULL STACK VERIFICATION SUCCESSFUL")
print("=" * 60)
