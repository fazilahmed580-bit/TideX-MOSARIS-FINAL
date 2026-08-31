# TideX P2: Lagrangian Oil-Spill Drift Modeling & Hindcasting/Forecasting Engine

TideX P2 is an advanced 2D Lagrangian particle tracking engine designed for ocean oil-spill drift simulation, backward origin hindcasting, and forward trajectory forecasting.

---

## 1. Project Purpose & P1 → P2 Workflow

TideX operates in a two-stage modular architecture:

1. **P1 Module (Satellite Detection):** Detects oil slicks from satellite Synthetic Aperture Radar (SAR) imagery, generating bounding AOI polygons (`data/spill_aoi.geojson`) and detection metadata (`data/metadata.json`).
2. **P2 Module (Lagrangian Simulation):** Ingests P1 satellite spill detections, initializes 500 Lagrangian particles across the detected spill boundary, and runs spatiotemporal advection-diffusion particle tracking using environmental wind and ocean current forcing datasets.

---

## 2. Environmental Forcing Datasets

TideX P2 requires two environmental forcing datasets:

- **ERA5 Atmospheric Wind (ECMWF):**
  - Variables: `u10` (10m eastward wind component) and `v10` (10m northward wind component).
- **CMEMS Surface Ocean Currents (Copernicus Marine):**
  - Variables: `uo` (eastward velocity) and `vo` (northward velocity).
  - Surface Depth: Approximately `0.494 m` (near-surface layer).

For the real P1 satellite case (August 21, 2018 in the Gulf of Mexico), the required forcing files are saved under `data/`:
- `data/era5_p1_2018.nc`
- `data/cmems_p1_2018.nc`

For synthetic P2 demonstration mode:
- `data/era5_region.nc`
- `data/cmems_region.nc` (or available CMEMS `.nc` files in `data/`)

---

## 3. Installation & Setup (Windows PowerShell)

Open **Windows PowerShell** in the project repository directory:

```powershell
# 1. Create a Python virtual environment
python -m venv venv

# 2. Activate the virtual environment
.\venv\Scripts\Activate.ps1

# 3. Upgrade pip and install all required dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 4. Preparing / Downloading Environmental Data (`setup_data.py`)

If setting up a fresh clone or downloading fresh ERA5 / CMEMS environmental forcing data for a new satellite spill observation:

1. **Set Environment Credentials (Optional / As Needed):**
   > [!IMPORTANT]
   > Never commit your API keys, passwords, or personal credentials into git. Always use environment variables or local non-committed config files.

   ```powershell
   # Copernicus Climate Data Store (CDS) API Key
   $env:CDSAPI_KEY="your-cds-api-key-here"

   # Copernicus Marine Service (CMEMS) Credentials
   $env:COPERNICUSMARINE_USER="your-cmems-username"
   $env:COPERNICUSMARINE_PASSWORD="your-cmems-password"
   ```

2. **Run the Data Setup Script:**

   ```powershell
   python setup_data.py
   ```

   `setup_data.py` dynamically reads `data/metadata.json` and `data/spill_aoi.geojson`, calculates the required spatial bounding box and observation timeframe, checks existing dataset files in `data/`, and downloads missing forcing data using `cdsapi` and `copernicusmarine`.

---

## 5. Running the Simulation & Testing

### Running the End-to-End Simulation Engine (`test_p2.py`)

To run the complete TideX P2 simulation test suite (Synthetic P2 Demonstration + Real P1 24h Hindcast & 24h Forecast):

```powershell
python test_p2.py
```

### Running Unit Tests (`pytest`)

To run the automated `pytest` test suite covering environment ingestion, boundary clamping, Lagrangian drift step physics, backtrack hindcasting, forward forecasting, and GeoJSON validity:

```powershell
python -m pytest -v
```

---

## 6. Expected Output Files

Upon successful execution of `test_p2.py`, output artifacts are generated under the `outputs/` directory:

- **`outputs/p1_probable_source.geojson`**: GeoJSON Polygon feature representing the estimated origin area of the P1 oil spill 24 hours prior to satellite observation.
- **`outputs/p1_backward_trajectories.geojson`**: GeoJSON FeatureCollection containing 500 particle LineString backward trajectories tracing the oil drift into the past.
- **`outputs/p1_forecast_uncertainty.geojson`**: GeoJSON Polygon feature representing the forecasted spill dispersion envelope 24 hours into the future.
- **`outputs/p1_forward_trajectories.geojson`**: GeoJSON FeatureCollection containing 500 particle LineString forward trajectories.

---

## 7. Credential & Security Policy

- **No Secrets in Code:** Never commit passwords, CDS API keys, tokens, or personal user paths into the repository.
- **Environment Overrides:** `setup_data.py` and `environment.py` check process environment variables (`CDSAPI_KEY`, `COPERNICUSMARINE_USER`, `COPERNICUSMARINE_PASSWORD`) or standard user config locations (`~/.cdsapirc`, `~/.copernicusmarine/`).
