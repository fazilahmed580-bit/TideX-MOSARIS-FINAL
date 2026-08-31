# TideX MOSARIS Backend

**Maritime Oil-Spill Attribution & Response Intelligence System**

SIH 2026 MVP Backend — Built with Python + FastAPI

---

## Table of Contents

1. [What MOSARIS does](#1-what-mosaris-does)
2. [What FastAPI is](#2-what-fastapi-is)
3. [Project structure](#3-project-structure)
4. [Installing Python](#4-installing-python)
5. [Opening a terminal in the backend folder](#5-opening-a-terminal-in-the-backend-folder)
6. [Creating a virtual environment](#6-creating-a-virtual-environment)
7. [Activating the virtual environment](#7-activating-the-virtual-environment)
8. [Installing requirements](#8-installing-requirements)
9. [Starting the server](#9-starting-the-server)
10. [Opening /docs](#10-opening-docs)
11. [Testing GET /](#11-testing-get-)
12. [Testing POST /investigate](#12-testing-post-investigate)
13. [Running demo_pipeline.py](#13-running-demo_pipelinepy)
14. [Understanding the response](#14-understanding-the-response)
15. [How P1 replaces the mock service](#15-how-p1-replaces-the-mock-service)
16. [How P2 replaces the mock service](#16-how-p2-replaces-the-mock-service)
17. [How P3 replaces the mock service](#17-how-p3-replaces-the-mock-service)
18. [How P4 replaces the mock service](#18-how-p4-replaces-the-mock-service)
19. [How P6 React/Leaflet connects](#19-how-p6-reactleaflet-connects)
20. [MVP limitations](#20-mvp-limitations)

---

## 1. What MOSARIS does

When a marine oil spill is detected, investigators need to answer:
- **Where exactly is the spill?**
- **Where did it come from?** (which location, what time)
- **Which vessel might be responsible?**
- **Where will the spill go next?**

MOSARIS runs a complete automated investigation pipeline:

```
P1: SAR Spill Detection
       ↓
P2: Drift Backtracking  →  Source Region Estimate
       ↓
P3: AIS Vessel Filtering  →  Candidate Vessels
       ↓
P4: Evidence Ranking + What-If Simulation
       ↓
P2: Forward Forecast
       ↓
Combined Investigation Result  →  React/Leaflet Map
```

The backend (P5) ties all of these steps together and exposes one API that the React frontend (P6) can call.

> **⚠️ IMPORTANT**: Attribution-confidence scores produced by MOSARIS are **investigation-priority scores only**. They are NOT guilt probabilities, NOT legal findings, and NOT culpability assessments. All final decisions must be made by qualified human investigators.

---

## 2. What FastAPI is

FastAPI is a Python library that makes it easy to create a web API (a backend that can receive requests from a frontend or other programs).

- You write Python functions.
- FastAPI turns them into HTTP endpoints that any frontend can call.
- It automatically creates interactive documentation at `/docs`.
- It automatically validates data using Pydantic models.

Think of it as: **"Python functions accessible over the internet."**

---

## 3. Project structure

```
TideX/
│
├── backend/
│   ├── main.py              ← Start here. Creates the FastAPI app.
│   ├── requirements.txt     ← List of packages to install.
│   ├── README.md            ← This file.
│   ├── pipeline.py          ← Connects P1→P2→P3→P4 in order.
│   ├── demo_pipeline.py     ← Test the pipeline without a browser.
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py        ← All HTTP endpoints (GET, POST, etc.)
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── models.py        ← Data shapes (what the API sends/receives)
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── spill_detection.py  ← P1 mock (teammate replaces this)
│   │   ├── drift.py            ← P2 mock (teammate replaces this)
│   │   ├── ais.py              ← P3 mock (teammate replaces this)
│   │   └── ranking.py          ← P4 mock (teammate replaces this)
│   │
│   └── data/
│       └── demo_case.json   ← Demo spill data (Arabian Sea)
│
└── .gitignore
```

---

## 4. Installing Python

1. Go to: https://www.python.org/downloads/
2. Download **Python 3.11** or newer (3.12 recommended).
3. **During install**: check the box that says **"Add Python to PATH"**.
4. Click Install Now.
5. Open a new terminal and type: `python --version`
   You should see something like: `Python 3.12.x`

> **Note**: On this machine, Python 3.14 is installed at:
> `C:\Users\fazil\AppData\Local\Programs\Python\Python314\python.exe`

---

## 5. Opening a terminal in the backend folder

**Method 1 (easiest):**
1. Open File Explorer.
2. Navigate to the `TideX\backend` folder.
3. Click the address bar at the top.
4. Type `powershell` and press Enter.

**Method 2:**
1. Press `Win + R`, type `powershell`, press Enter.
2. Type: `cd C:\Users\fazil\.gemini\antigravity\scratch\TideX\backend`

---

## 6. Creating a virtual environment

A virtual environment keeps your project's packages separate from other Python projects.

Open a terminal **inside the `backend/` folder** and run:

```powershell
python -m venv venv
```

> If `python` doesn't work, try the full path:
> ```powershell
> C:\Users\fazil\AppData\Local\Programs\Python\Python314\python.exe -m venv venv
> ```

This creates a `venv/` folder inside `backend/`.

---

## 7. Activating the virtual environment

Every time you open a new terminal, you need to activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

You should see `(venv)` at the start of your terminal prompt. That means it's active.

> **If you get an error about "execution policy"**, run this first:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Then try activating again.

---

## 8. Installing requirements

With the virtual environment **active**, run:

```powershell
pip install -r requirements.txt
```

This installs FastAPI, Uvicorn, and Pydantic.

---

## 9. Starting the server

With the virtual environment **active**, run:

```powershell
uvicorn main:app --reload
```

You should see output like:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

The `--reload` flag means the server restarts automatically when you change code.

**To stop the server**: press `Ctrl + C`.

---

## 10. Opening /docs

While the server is running, open your browser and go to:

```
http://127.0.0.1:8000/docs
```

You will see the **interactive API documentation** — a complete list of all endpoints. You can test them directly from the browser by clicking "Try it out".

---

## 11. Testing GET /

**In your browser**, go to:
```
http://127.0.0.1:8000/
```

You should see:
```json
{
  "status": "ok",
  "service": "TideX MOSARIS Backend",
  "message": "Backend is running. Visit /docs for API documentation."
}
```

---

## 12. Testing POST /investigate

This is the **main endpoint** that runs the complete pipeline.

**Using curl (in PowerShell):**
```powershell
Invoke-WebRequest -Method POST `
  -Uri "http://127.0.0.1:8000/investigate" `
  -ContentType "application/json" `
  -Body '{"spill_id": "demo_001"}' | Select-Object -ExpandProperty Content
```

**Using the /docs UI:**
1. Go to `http://127.0.0.1:8000/docs`
2. Click on `POST /investigate`
3. Click "Try it out"
4. In the body, enter: `{"spill_id": "demo_001"}`
5. Click "Execute"

---

## 13. Running demo_pipeline.py

This lets you test the pipeline **without starting the server**.

With the virtual environment active, in the `backend/` folder:

```powershell
python demo_pipeline.py
```

You should see a full readable summary of the investigation.

---

## 14. Understanding the response

The `/investigate` endpoint returns:

```json
{
  "spill": {
    "spill_id": "demo_001",
    "timestamp": "...",
    "spill_detected": true,
    "polygon": { "type": "Polygon", "coordinates": [[...]] },
    "centroid": [18.95, 71.86],
    "area_km2": 12.4,
    "confidence": 0.91
  },
  "source": {
    "origin_region": { "type": "Polygon", "coordinates": [[...]] },
    "origin_time_start": "...",
    "origin_time_end": "...",
    "uncertainty_polygon": { "type": "Polygon", "coordinates": [[...]] },
    "backward_particles": [[lon, lat], ...],
    "forward_particles": [[lon, lat], ...]
  },
  "candidates": [
    {
      "mmsi": "123456789",
      "vessel_name": "MV Arabian Star",
      "distance_km": 4.2,
      "time_difference_hr": 0.5,
      "speed": 11.4,
      "heading": 142,
      "track": { "type": "LineString", "coordinates": [[lon, lat], ...] }
    }
  ],
  "ranking": [
    {
      "mmsi": "123456789",
      "rank": 1,
      "score": 0.92,
      "supporting_evidence": ["..."],
      "contradictory_evidence": ["..."]
    }
  ],
  "forecast": [[lon, lat], ...],
  "simulations": [
    {
      "mmsi": "123456789",
      "predicted_polygons": [{ "type": "Polygon", "coordinates": [[...]] }]
    }
  ]
}
```

**Important notes:**
- `centroid` is `[latitude, longitude]` — API contract.
- All GeoJSON coordinates are `[longitude, latitude]` — GeoJSON standard.
- `score` is an **investigation-priority score**, NOT a guilt probability.

---

## 15. How P1 replaces the mock service

**File to modify:** `backend/services/spill_detection.py`

**Function to replace:**
```python
def detect_spill(spill_id: str) -> dict:
    ...
```

**Required return format:**
```python
{
    "spill_id":       str,     # same as input
    "timestamp":      str,     # ISO 8601, e.g. "2026-08-30T10:00:00"
    "spill_detected": bool,
    "polygon": {               # GeoJSON Polygon [longitude, latitude]
        "type": "Polygon",
        "coordinates": [[[lon, lat], ...]]
    },
    "centroid": [lat, lon],    # [latitude, longitude] -- API contract
    "area_km2": float,
    "confidence": float        # 0.0 to 1.0
}
```

**Do NOT change:** `api/routes.py`, `main.py`, `pipeline.py`.

---

## 16. How P2 replaces the mock service

**File to modify:** `backend/services/drift.py`

**Functions to replace:**

```python
def backtrack(spill: dict) -> dict:
    ...
```
Returns: source estimate dict (see format in drift.py).

```python
def forecast(source: dict) -> list:
    ...
```
Returns: `[[lon, lat], [lon, lat], ...]` — future particle positions.

**Do NOT change:** `api/routes.py`, `main.py`, `pipeline.py`.

---

## 17. How P3 replaces the mock service

**File to modify:** `backend/services/ais.py`

**Function to replace:**
```python
def find_candidates(source: dict) -> list:
    ...
```
Returns: list of candidate vessel dicts (see format in ais.py).

**Do NOT change:** `api/routes.py`, `main.py`, `pipeline.py`.

---

## 18. How P4 replaces the mock service

**File to modify:** `backend/services/ranking.py`

**Functions to replace:**

```python
def rank_candidates(candidates: list, source: dict, spill: dict) -> list:
    ...
```
Returns: list of ranking dicts sorted by rank.

```python
def simulate(mmsi: str, source: dict, spill: dict) -> dict:
    ...
```
Returns: `{"mmsi": str, "predicted_polygons": [GeoJSON Polygon, ...]}`.

**⚠️ SCORES MUST REMAIN**: investigation-priority scores in range [0.0, 1.0]. Never describe them as guilt probabilities.

**Do NOT change:** `api/routes.py`, `main.py`, `pipeline.py`.

---

## 19. How P6 React/Leaflet connects

The React frontend should call **one endpoint**:

```
POST http://localhost:8000/investigate
Content-Type: application/json

{ "spill_id": "demo_001" }
```

**Using Axios (JavaScript):**
```javascript
import axios from 'axios';

const response = await axios.post('http://localhost:8000/investigate', {
  spill_id: 'demo_001'
});

const data = response.data;

// Spill polygon (GeoJSON [lon, lat]):
const spillPolygon = data.spill.polygon;

// Source region:
const sourceRegion = data.source.origin_region;

// Vessel tracks:
data.candidates.forEach(c => {
  const track = c.track;  // GeoJSON LineString
});

// Rankings:
data.ranking.forEach(r => {
  console.log(`Rank ${r.rank}: MMSI ${r.mmsi}, score ${r.score}`);
});

// Forward forecast:
const forecastPoints = data.forecast;  // [[lon, lat], ...]

// Simulated polygons:
data.simulations.forEach(s => {
  const polygon = s.predicted_polygons[0];
});
```

**CORS is already enabled** for `http://localhost:3000` and `http://localhost:5173`.

**Leaflet note:** Leaflet uses `[latitude, longitude]` for `L.latLng()` and `L.polygon()`, but GeoJSON layers use `[longitude, latitude]`. Use `L.geoJSON()` to automatically handle GeoJSON data without manual coordinate flipping.

---

## 20. MVP limitations

| Limitation | Description |
|---|---|
| Mock data only | P1/P2/P3/P4 use hard-coded demo data. Real algorithms not yet integrated. |
| Single demo case | Only `demo_001` (Arabian Sea) is supported. |
| No database | Data is in memory / JSON files. PostgreSQL/PostGIS can be added later. |
| No authentication | No login or API key. Add this before any public deployment. |
| Simplified simulation | P4 simulation is geometric only, not a validated oil-spill transport model. |
| No real SAR data | Spill polygon is fictional for demonstration. |
| No real AIS data | Vessel tracks are fictional for demonstration. |
| No real ocean currents | Drift paths are straight-line approximations, not real circulation models. |
| Local only | Not deployed to any cloud. Runs on `localhost` only. |

---

*TideX MOSARIS — Smart India Hackathon 2026*
