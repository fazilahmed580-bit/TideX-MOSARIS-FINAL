"""
schemas/models.py
-----------------
All Pydantic data models for the MOSARIS backend.

These models define:
  - What data each API endpoint accepts (request bodies)
  - What data each API endpoint returns (responses)

Pydantic automatically validates types, so if you send wrong data
the API will return a clear error message.

COORDINATE CONVENTION (IMPORTANT):
  GeoJSON always uses [longitude, latitude] order.
  The "centroid" field in SpillResult uses [latitude, longitude]
  because that is the documented API contract for this project.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


# ---------------------------------------------------------------------------
# GeoJSON geometry helpers
# A "dict" is used here so any GeoJSON geometry type is accepted.
# Example: {"type": "Polygon", "coordinates": [...]}
# ---------------------------------------------------------------------------

GeoJSONGeometry = Dict[str, Any]


# ---------------------------------------------------------------------------
# Request models (what the frontend sends to the API)
# ---------------------------------------------------------------------------

class InvestigateRequest(BaseModel):
    """
    Body for POST /investigate.
    If no spill_id is given, the backend uses the built-in demo case.
    """
    spill_id: str = Field(
        default="demo_001",
        description="ID of the spill case to investigate. Use 'demo_001' for the demo."
    )


class SimulateRequest(BaseModel):
    """
    Body for POST /spill/{id}/simulate.
    Asks the backend: 'What if THIS vessel was the source?'
    """
    mmsi: str = Field(description="MMSI identifier of the candidate vessel to simulate.")


class SpillRequest(BaseModel):
    """
    Body for POST /spill.
    Registers a new spill case by ID.
    """
    spill_id: str = Field(description="Unique identifier for the spill case.")


# ---------------------------------------------------------------------------
# Result models (what the API returns)
# ---------------------------------------------------------------------------

class SpillResult(BaseModel):
    """
    Output from P1 spill detection.

    NOTE on centroid: [latitude, longitude] -- this is the API contract.
    NOTE on polygon: GeoJSON uses [longitude, latitude] in coordinates.
    """
    spill_id: str
    timestamp: str
    spill_detected: bool
    polygon: GeoJSONGeometry          # GeoJSON Polygon [lon, lat]
    centroid: List[float]             # [latitude, longitude] -- API contract
    area_km2: float
    confidence: float


class SourceEstimate(BaseModel):
    """
    Output from P2 backtracking.
    Tells us where and when the spill most likely originated.
    """
    origin_region: GeoJSONGeometry          # GeoJSON Polygon [lon, lat]
    origin_time_start: str
    origin_time_end: str
    uncertainty_polygon: GeoJSONGeometry    # GeoJSON Polygon [lon, lat]
    backward_particles: List[List[float]]   # List of [lon, lat] points
    forward_particles: List[List[float]]    # List of [lon, lat] points


class VesselCandidate(BaseModel):
    """
    A single candidate vessel from P3 AIS filtering.
    """
    mmsi: str
    vessel_name: Optional[str] = None
    distance_km: float
    time_difference_hr: float
    speed: float
    heading: int
    track: GeoJSONGeometry    # GeoJSON LineString [lon, lat]


class CandidateRanking(BaseModel):
    """
    P4 ranking result for one candidate vessel.

    IMPORTANT DISCLAIMER:
    The 'score' is an investigation-priority / attribution-confidence score.
    It is NOT a probability of guilt, legal responsibility, or culpability.
    It reflects how well the available evidence aligns with this vessel
    being the source, for the purpose of prioritising investigation.
    """
    mmsi: str
    rank: int
    score: float = Field(description=(
        "Investigation-priority score (0.0-1.0). "
        "NOT a guilt probability. See API documentation."
    ))
    supporting_evidence: List[str]
    contradictory_evidence: List[str]


class SimulationResult(BaseModel):
    """
    Output from P4 what-if simulation.
    Shows predicted spill polygon if the given vessel was the source.
    """
    mmsi: str
    predicted_polygons: List[GeoJSONGeometry]   # List of GeoJSON Polygons


class InvestigationResult(BaseModel):
    """
    Complete result returned by POST /investigate.
    This is everything the React/Leaflet frontend needs to display the full map.

    Fields:
      spill      - detected oil spill (P1 output)
      source     - estimated origin (P2 backtrack output)
      candidates - AIS vessel candidates (P3 output)
      ranking    - candidate rankings (P4 output)
      forecast   - forward particle forecast (P2 forecast output)
      simulations - what-if simulation polygons per candidate (P4 simulate)
    """
    spill: SpillResult
    source: SourceEstimate
    candidates: List[VesselCandidate]
    ranking: List[CandidateRanking]
    forecast: List[List[float]]         # List of [lon, lat] forward particles
    simulations: List[SimulationResult]


class StatusResponse(BaseModel):
    """Simple health-check response for GET /."""
    status: str
    service: str
    message: str
