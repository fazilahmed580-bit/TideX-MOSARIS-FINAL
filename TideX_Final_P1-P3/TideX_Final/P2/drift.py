import numpy as np
import pandas as pd
from environment import Environment


class ParticleDriftSimulation:
    """
    Lightweight 2D Lagrangian particle drift simulation for TideX P2.

    Assumptions & Formulas:
    -----------------------
    1. Total advection velocity: U_total = U_current + windage * U_wind
       - Surface ocean current (U_current) direct advection (100% coupling).
       - Windage factor (alpha = 0.03 / 3%) models wind drag on floating surface oil slicks.
    2. Random Walk Turbulent Diffusion:
       - Diffusion velocity offset = N(0, 1) * sqrt(2 * D / dt)
       - Default turbulent diffusivity coefficient D = 1.0 m^2/s.
    3. Coordinate Transformation (m/s to deg/s):
       - 1 degree latitude ~ 111,320 meters.
       - 1 degree longitude ~ 111,320 * cos(lat_radians) meters.
    4. Time Stepping:
       - Forward mode (mode='forward'): dt > 0, advection moves along U_total vector.
       - Backward mode (mode='backward'): dt > 0 step size, time steps backward,
         advection moves along -U_total vector to trace origin locations.
    """

    def __init__(self, env=None, windage=0.03, diffusion_coef=1.0):
        self.env = env if env is not None else Environment()
        self.windage = windage
        self.diffusion_coef = diffusion_coef
        self.meters_per_lat_deg = 111320.0

    def run_simulation(self, initial_lats, initial_lons, start_time, duration_hours=24,
                       dt_seconds=3600, mode='forward'):
        """
        Run Lagrangian particle tracking simulation.

        Parameters:
        -----------
        initial_lats : np.ndarray or list
            Initial latitude coordinates of particles.
        initial_lons : np.ndarray or list
            Initial longitude coordinates of particles.
        start_time : str, pd.Timestamp, or np.datetime64
            Simulation start timestamp.
        duration_hours : float
            Total simulation time in hours.
        dt_seconds : float
            Euler integration step size in seconds (default: 3600 s / 1 hr).
        mode : str
            'forward' for forecast, 'backward' for hindcast/backtracking.

        Returns:
        --------
        trajectories : dict
            Dictionary mapping particle index to list of (timestamp_str, lat, lon) tuples.
        final_lats : np.ndarray
        final_lons : np.ndarray
        """
        lats = np.array(initial_lats, dtype=float).copy()
        lons = np.array(initial_lons, dtype=float).copy()
        num_particles = len(lats)

        start_ts = pd.Timestamp(start_time)
        num_steps = int(np.ceil((duration_hours * 3600) / dt_seconds))

        # Record particle trajectory history
        # History structure: list of arrays of shape (num_particles, 2) at each time step
        history_lats = [lats.copy()]
        history_lons = [lons.copy()]
        history_timestamps = [start_ts]

        current_ts = start_ts
        direction = 1.0 if mode == 'forward' else -1.0

        for step in range(num_steps):
            # Query environmental vectors (u_wind, v_wind, u_curr, v_curr) in m/s
            u_wind, v_wind, u_curr, v_curr = self.env.get_vectors(lats, lons, current_ts)

            # Net advection velocity (m/s)
            u_adv = u_curr + self.windage * u_wind
            v_adv = v_curr + self.windage * v_wind

            # Apply motion direction: forward moves along advection, backward moves opposite to advection
            u_effective = direction * u_adv
            v_effective = direction * v_adv

            # Random walk diffusion step (m/s)
            # Standard deviation = sqrt(2 * D / dt)
            if self.diffusion_coef > 0:
                sigma_diff = np.sqrt(2.0 * self.diffusion_coef / dt_seconds)
                u_diff = np.random.normal(0.0, sigma_diff, size=num_particles)
                v_diff = np.random.normal(0.0, sigma_diff, size=num_particles)
            else:
                u_diff = 0.0
                v_diff = 0.0

            u_total = u_effective + u_diff
            v_total = v_effective + v_diff

            # Convert velocity (m/s) to displacement in degrees
            # dlat = (v_total * dt) / meters_per_lat_deg
            # dlon = (u_total * dt) / (meters_per_lat_deg * cos(lat_rad))
            lat_rad = np.radians(lats)
            dlat = (v_total * dt_seconds) / self.meters_per_lat_deg
            dlon = (u_total * dt_seconds) / (self.meters_per_lat_deg * np.cos(lat_rad))

            # Euler integration step
            lats += dlat
            lons += dlon

            # Advance simulation timestamp
            time_delta = pd.Timedelta(seconds=dt_seconds)
            current_ts = current_ts + time_delta if mode == 'forward' else current_ts - time_delta

            history_lats.append(lats.copy())
            history_lons.append(lons.copy())
            history_timestamps.append(current_ts)

        # Format output trajectories
        trajectories = []
        for i in range(num_particles):
            path = [
                {
                    "timestamp": history_timestamps[t].strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "lat": float(history_lats[t][i]),
                    "lon": float(history_lons[t][i])
                }
                for t in range(len(history_timestamps))
            ]
            trajectories.append(path)

        return {
            "trajectories": trajectories,
            "final_lats": lats,
            "final_lons": lons,
            "history_lats": history_lats,
            "history_lons": history_lons,
            "timestamps": history_timestamps
        }
