"""
main.py
-------
Entry point for the MOSARIS FastAPI backend.

HOW TO START THE SERVER:
  Local Development:
    uvicorn main:app --reload --host 127.0.0.1 --port 8000

  Production (Render / Container):
    uvicorn main:app --host 0.0.0.0 --port $PORT
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

# ---------------------------------------------------------------------------
# Create the FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="TideX MOSARIS Backend",
    description=(
        "Maritime Oil-Spill Attribution & Response Intelligence System (MOSARIS). "
        "Provides a complete investigation pipeline: "
        "SAR spill detection (P1) -> drift backtracking (P2) -> "
        "AIS candidate filtering (P3) -> evidence ranking (P4).\n\n"
        "**IMPORTANT**: Attribution-confidence scores are investigation-priority scores. "
        "They are NOT guilt probabilities, legal findings, or culpability assessments."
    ),
    version="1.0.0-MVP",
    contact={
        "name": "TideX Team -- SIH 2026",
    }
)

# ---------------------------------------------------------------------------
# CORS Configuration -- configurable via ALLOWED_ORIGINS env var
# ---------------------------------------------------------------------------

allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
if allowed_origins_env:
    origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]
else:
    origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "*"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Attach all API routes
# ---------------------------------------------------------------------------

app.include_router(router)
