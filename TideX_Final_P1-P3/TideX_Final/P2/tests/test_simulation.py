import os
import pytest
import numpy as np
import pandas as pd
from environment import Environment
from drift import ParticleDriftSimulation
from backtrack import backtrack, _coords_to_geojson_polygon
from forecast import forecast
from p1_loader import load_p1_data, check_environmental_compatibility


@pytest.fixture(scope="module")
def p1_env():
    """Fixture providing initialized Environment for real P1 2018 forcing files."""
    era5_p1 = os.path.join("data", "era5_p1_2018.nc")
    cmems_p1 = os.path.join("data", "cmems_p1_2018.nc")
    if os.path.exists(era5_p1) and os.path.exists(cmems_p1):
        return Environment(era5_path=era5_p1, cmems_path=cmems_p1)
    return Environment()


def test_p1_loader_dynamic():
    """Test dynamic loading of real P1 metadata and AOI GeoJSON."""
    p1_data = load_p1_data()
    assert "centroid" in p1_data
    assert "lat" in p1_data["centroid"]
    assert "lon" in p1_data["centroid"]
    assert p1_data["centroid"]["lat"] == pytest.approx(29.11045, rel=1e-3)
    assert p1_data["centroid"]["lon"] == pytest.approx(-88.730939, rel=1e-3)
    assert p1_data["observation_date"] == "2018-08-21"
    assert len(p1_data["aoi_bounds"]) == 4
    assert p1_data["feature_count"] > 0


def test_real_p1_forcing_validity(p1_env):
    """
    Test proving that p1_env environmental forcing files are real and appropriate
    for the P1 Gulf of Mexico case (August 21, 2018; 29.11 N, -88.73 W) rather than
    falling back to synthetic 2026 data.
    """
    p1_data = load_p1_data()
    compat = check_environmental_compatibility(p1_data, p1_env)

    assert compat["compatible"] is True, f"P1 forcing mismatch: {compat['reason']}"

    # Verify ERA5 spatial coverage covers Gulf of Mexico P1 centroid (29.11 N, -88.73 W)
    e_lats = p1_env.ds_era5[p1_env.era5_lat_name].values
    e_lons = p1_env.ds_era5[p1_env.era5_lon_name].values

    assert np.min(e_lats) <= 29.11 <= np.max(e_lats)
    assert np.min(e_lons) <= -88.73 <= np.max(e_lons)

    # Verify ERA5 temporal coverage covers 2018-08-21
    e_times = pd.to_datetime(p1_env.ds_era5[p1_env.era5_time_name].values)
    t_min_str = e_times.min().strftime("%Y-%m-%d")
    t_max_str = e_times.max().strftime("%Y-%m-%d")

    assert t_min_str <= "2018-08-21" <= t_max_str


def test_environment_clamping(p1_env):
    """Test environment vector interpolation and boundary clamping."""
    lats = np.array([29.11, 35.0, 10.0])  # Includes out-of-bounds positions
    lons = np.array([-88.73, -100.0, -70.0])
    u_w, v_w, u_c, v_c = p1_env.get_vectors(lats, lons, "2018-08-21T12:00:00Z")

    assert len(u_w) == 3
    assert len(v_w) == 3
    assert len(u_c) == 3
    assert len(v_c) == 3
    assert not np.isnan(u_w).any()
    assert not np.isnan(v_w).any()
    assert not np.isnan(u_c).any()
    assert not np.isnan(v_c).any()


def test_drift_simulation_forward(p1_env):
    """Test forward particle drift simulation execution."""
    sim = ParticleDriftSimulation(env=p1_env, windage=0.03, diffusion_coef=1.0)
    init_lats = np.full(100, 29.11)
    init_lons = np.full(100, -88.73)

    res = sim.run_simulation(
        initial_lats=init_lats,
        initial_lons=init_lons,
        start_time="2018-08-21T12:00:00Z",
        duration_hours=6,
        dt_seconds=3600,
        mode="forward"
    )

    assert len(res["final_lats"]) == 100
    assert len(res["final_lons"]) == 100
    assert len(res["trajectories"]) == 100
    assert len(res["timestamps"]) == 7  # t0 + 6 hourly steps


def test_drift_simulation_backward(p1_env):
    """Test backward particle drift simulation execution."""
    sim = ParticleDriftSimulation(env=p1_env, windage=0.03, diffusion_coef=1.0)
    init_lats = np.full(100, 29.11)
    init_lons = np.full(100, -88.73)

    res = sim.run_simulation(
        initial_lats=init_lats,
        initial_lons=init_lons,
        start_time="2018-08-21T12:00:00Z",
        duration_hours=6,
        dt_seconds=3600,
        mode="backward"
    )

    assert len(res["final_lats"]) == 100
    assert len(res["final_lons"]) == 100
    assert len(res["trajectories"]) == 100


def test_backtrack_and_forecast_geojson(p1_env):
    """Test backtrack hindcast and forecast GeoJSON structure validity."""
    p1_data = load_p1_data()

    # Run 12h backtrack
    bt_res = backtrack(
        spill_polygon=p1_data["geojson"],
        observation_time="2018-08-21T12:00:00Z",
        duration_hours=12,
        num_particles=50,
        env=p1_env
    )

    assert "probable_source_region" in bt_res
    assert "backward_trajectories" in bt_res
    assert bt_res["probable_source_region"]["geometry"]["type"] == "Polygon"
    assert bt_res["backward_trajectories"]["type"] == "FeatureCollection"
    assert len(bt_res["backward_trajectories"]["features"]) == 50

    # Run 12h forecast from estimated origin
    origin = bt_res["probable_source_region"]
    origin_time = origin["properties"]["estimated_origin_time"]

    fc_res = forecast(
        source_region=origin,
        start_time=origin_time,
        duration_hours=12,
        num_particles=50,
        env=p1_env
    )

    assert "future_trajectories" in fc_res
    assert "forecast_uncertainty_polygon" in fc_res
    assert fc_res["forecast_uncertainty_polygon"]["geometry"]["type"] == "Polygon"
    assert fc_res["future_trajectories"]["type"] == "FeatureCollection"
    assert len(fc_res["future_trajectories"]["features"]) == 50


def test_geojson_polygon_helper():
    """Test convex hull and bounding box polygon generator."""
    lons = np.array([-88.75, -88.70, -88.72, -88.71])
    lats = np.array([29.10, 29.12, 29.15, 29.11])

    geom = _coords_to_geojson_polygon(lons, lats, use_convex_hull=True)
    assert geom["type"] == "Polygon"
    assert len(geom["coordinates"][0]) >= 4
    # Closed ring check
    assert geom["coordinates"][0][0] == geom["coordinates"][0][-1]
