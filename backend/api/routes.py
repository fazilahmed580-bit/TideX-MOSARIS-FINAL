"""
api/routes.py
-------------
All FastAPI route definitions for MOSARIS.

IMPORTANT:
  This file handles HTTP only -- routing, request parsing, and error responses.
  All business logic lives in pipeline.py and the services/ folder.
  Do NOT put algorithm logic in this file.

ENDPOINTS:
  GET  /                         -- health check
  POST /spill                    -- register a spill case
  POST /spill/{id}/detect        -- run P1 detection for a spill
  POST /spill/{id}/backtrack     -- run P2 backtracking for a spill
  GET  /spill/{id}/candidates    -- run P3 AIS candidate search
  POST /spill/{id}/simulate      -- run P4 what-if simulation
  GET  /spill/{id}/ranking       -- run P4 candidate ranking
  POST /investigate              -- run the COMPLETE pipeline (MAIN ENDPOINT)
"""

from fastapi import APIRouter, HTTPException
from schemas.models import (
    StatusResponse,
    SpillRequest,
    SpillResult,
    SourceEstimate,
    VesselCandidate,
    CandidateRanking,
    SimulateRequest,
    SimulationResult,
    InvestigateRequest,
    InvestigationResult,
)
from pipeline import run_investigation, KNOWN_SPILL_IDS
from services.spill_detection import detect_spill
from services.drift import backtrack, forecast
from services.ais import find_candidates
from services.ranking import rank_candidates, simulate

# Create the router -- main.py will attach this to the FastAPI app
router = APIRouter()


# ---------------------------------------------------------------------------
# GET /  --  Health Check
# ---------------------------------------------------------------------------

@router.get("/", response_model=StatusResponse, summary="Health check")
def root():
    """Returns a simple status message to confirm the backend is running."""
    return {
        "status": "ok",
        "service": "TideX MOSARIS Backend",
        "message": "Backend is running. Visit /docs for API documentation."
    }


# ---------------------------------------------------------------------------
# POST /spill  --  Register a spill case
# ---------------------------------------------------------------------------

@router.post("/spill", summary="Register a spill case")
def register_spill(body: SpillRequest):
    """
    Register a spill case by ID.
    Returns confirmation if the spill ID is known.
    """
    if body.spill_id not in KNOWN_SPILL_IDS:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown spill ID: '{body.spill_id}'. Available: {list(KNOWN_SPILL_IDS)}"
        )
    return {
        "message": f"Spill case '{body.spill_id}' is registered and ready.",
        "spill_id": body.spill_id
    }


# ---------------------------------------------------------------------------
# POST /spill/{id}/detect  --  Run P1 detection
# ---------------------------------------------------------------------------

@router.post("/spill/{spill_id}/detect", response_model=SpillResult,
             summary="P1: Detect oil spill from SAR data")
def detect(spill_id: str):
    """
    Runs the P1 spill detection service for the given spill ID.
    Returns the detected spill polygon, centroid, area, and confidence.
    """
    if spill_id not in KNOWN_SPILL_IDS:
        raise HTTPException(status_code=404, detail=f"Unknown spill ID: '{spill_id}'")
    try:
        result = detect_spill(spill_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"P1 detection failed: {str(e)}")


# ---------------------------------------------------------------------------
# POST /spill/{id}/backtrack  --  Run P2 backtracking
# ---------------------------------------------------------------------------

@router.post("/spill/{spill_id}/backtrack", response_model=SourceEstimate,
             summary="P2: Backtrack drift to estimate source region")
def backtrack_spill(spill_id: str):
    """
    Runs P1 detection first, then P2 backtracking.
    Returns the estimated source region, time window, drift particles.
    """
    if spill_id not in KNOWN_SPILL_IDS:
        raise HTTPException(status_code=404, detail=f"Unknown spill ID: '{spill_id}'")
    try:
        spill = detect_spill(spill_id)
        source = backtrack(spill)
        return source
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"P2 backtracking failed: {str(e)}")


# ---------------------------------------------------------------------------
# GET /spill/{id}/candidates  --  Run P3 AIS filtering
# ---------------------------------------------------------------------------

@router.get("/spill/{spill_id}/candidates", summary="P3: Find AIS candidate vessels")
def candidates(spill_id: str):
    """
    Runs P1 -> P2 -> P3 to find candidate vessels near the source.
    Returns a list of candidate vessels with their AIS tracks.
    """
    if spill_id not in KNOWN_SPILL_IDS:
        raise HTTPException(status_code=404, detail=f"Unknown spill ID: '{spill_id}'")
    try:
        spill = detect_spill(spill_id)
        source = backtrack(spill)
        candidate_list = find_candidates(source)
        return {"candidates": candidate_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"P3 candidate search failed: {str(e)}")


# ---------------------------------------------------------------------------
# POST /spill/{id}/simulate  --  Run P4 what-if simulation
# ---------------------------------------------------------------------------

@router.post("/spill/{spill_id}/simulate", response_model=SimulationResult,
             summary="P4: What-if simulation for a candidate vessel")
def simulate_vessel(spill_id: str, body: SimulateRequest):
    """
    Runs what-if simulation for a specific candidate vessel.
    Shows what the spill would look like if that vessel was the source.

    NOTE: This is a simplified MVP simulation, not a validated oil-spill model.
    """
    if spill_id not in KNOWN_SPILL_IDS:
        raise HTTPException(status_code=404, detail=f"Unknown spill ID: '{spill_id}'")
    try:
        spill = detect_spill(spill_id)
        source = backtrack(spill)
        result = simulate(body.mmsi, source, spill)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"P4 simulation failed: {str(e)}")


# ---------------------------------------------------------------------------
# GET /spill/{id}/ranking  --  Run P4 ranking
# ---------------------------------------------------------------------------

@router.get("/spill/{spill_id}/ranking", summary="P4: Rank candidate vessels by evidence")
def ranking(spill_id: str):
    """
    Runs the full pipeline up to ranking and returns ranked candidates.

    DISCLAIMER: Scores are investigation-priority scores, NOT guilt probabilities.
    """
    if spill_id not in KNOWN_SPILL_IDS:
        raise HTTPException(status_code=404, detail=f"Unknown spill ID: '{spill_id}'")
    try:
        spill = detect_spill(spill_id)
        source = backtrack(spill)
        candidate_list = find_candidates(source)
        rankings = rank_candidates(candidate_list, source, spill)
        return {
            "spill_id": spill_id,
            "disclaimer": (
                "Scores are investigation-priority / attribution-confidence scores. "
                "They are NOT guilt probabilities or legal findings."
            ),
            "rankings": rankings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"P4 ranking failed: {str(e)}")


# ---------------------------------------------------------------------------
# POST /investigate  --  MASTER ENDPOINT
# ---------------------------------------------------------------------------

@router.post("/investigate", response_model=InvestigationResult,
             summary="Run the complete MOSARIS investigation pipeline")
def investigate(body: InvestigateRequest):
    """
    **MAIN ENDPOINT** -- runs the complete investigation pipeline:

    P1 detect -> P2 backtrack -> P3 find_candidates ->
    P4 rank + simulate -> P2 forecast

    Returns everything the React/Leaflet frontend needs to display the full map:
    - Detected spill polygon
    - Source region estimate
    - Backward drift particles
    - AIS candidate vessels
    - Ranked candidates with evidence
    - What-if simulation polygons
    - Forward forecast particles

    **IMPORTANT**: Ranking scores are investigation-priority scores.
    They are NOT guilt probabilities or legal findings.
    """
    try:
        result = run_investigation(body.spill_id)
        return result
    except ValueError as e:
        # Unknown spill ID
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Investigation pipeline failed: {str(e)}")
