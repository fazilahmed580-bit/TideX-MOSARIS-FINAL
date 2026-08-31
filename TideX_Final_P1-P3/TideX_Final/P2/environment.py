import os
import glob
import numpy as np
import pandas as pd
import xarray as xr
from scipy.interpolate import RegularGridInterpolator


class Environment:
    """
    Environmental data handler for TideX P2.
    Loads ERA5 wind (u10, v10) and CMEMS surface currents (uo, vo),
    subsets CMEMS to the region of interest, and provides interpolated
    environmental vectors (u_wind, v_wind, u_curr, v_curr) for particle simulations.
    """

    def __init__(self, era5_path=None, cmems_path=None):
        if era5_path is None:
            # Standard Default Resolution Priority for ERA5
            candidates = [
                os.path.join('data', 'era5_p1_2018.nc'),
                os.path.join('data', 'era5_region.nc'),
            ]
            for cand in candidates:
                if os.path.exists(cand):
                    era5_path = cand
                    break

            if era5_path is None:
                # Dynamic search for ERA5 NetCDF file in data/
                all_nc = glob.glob(os.path.join('data', '*.nc'))
                for f in all_nc:
                    if 'era5' in os.path.basename(f).lower():
                        era5_path = f
                        break
                if era5_path is None and all_nc:
                    non_cmems = [f for f in all_nc if 'cmems' not in os.path.basename(f).lower()]
                    if non_cmems:
                        era5_path = non_cmems[0]

        if cmems_path is None:
            # Standard Default Resolution Priority for CMEMS
            candidates = [
                os.path.join('data', 'cmems_p1_2018.nc'),
                os.path.join('data', 'cmems_region.nc'),
            ]
            for cand in candidates:
                if os.path.exists(cand):
                    cmems_path = cand
                    break

            if cmems_path is None:
                # Dynamic search for CMEMS NetCDF file in data/
                all_nc = glob.glob(os.path.join('data', '*.nc'))
                for f in all_nc:
                    if 'cmems' in os.path.basename(f).lower():
                        cmems_path = f
                        break

        if era5_path is None or not os.path.exists(era5_path):
            raise FileNotFoundError(
                f"ERA5 environmental forcing file not found (searched: {era5_path}). "
                "Please ensure forcing files are in data/ or run 'python setup_data.py'."
            )
        if cmems_path is None or not os.path.exists(cmems_path):
            raise FileNotFoundError(
                f"CMEMS environmental forcing file not found (searched: {cmems_path}). "
                "Please ensure forcing files are in data/ or run 'python setup_data.py'."
            )

        print(f"[Environment] Loading ERA5 wind data from {era5_path}")
        self.ds_era5 = xr.open_dataset(era5_path)

        print(f"[Environment] Loading CMEMS current data from {cmems_path}")
        self.ds_cmems = xr.open_dataset(cmems_path)

        # Process ERA5 coordinates & variables
        self.era5_lat_name = self._find_coord(self.ds_era5, ['latitude', 'lat'])
        self.era5_lon_name = self._find_coord(self.ds_era5, ['longitude', 'lon'])
        self.era5_time_name = self._find_coord(self.ds_era5, ['time', 'valid_time', 't'])

        self.u10_name = self._find_var(self.ds_era5, ['u10', '10u', 'u10m', 'u'])
        self.v10_name = self._find_var(self.ds_era5, ['v10', '10v', 'v10m', 'v'])

        # Process CMEMS coordinates & variables
        self.cmems_lat_name = self._find_coord(self.ds_cmems, ['latitude', 'lat'])
        self.cmems_lon_name = self._find_coord(self.ds_cmems, ['longitude', 'lon'])
        self.cmems_time_name = self._find_coord(self.ds_cmems, ['time', 'valid_time', 't'])

        self.uo_name = self._find_var(self.ds_cmems, ['uo', 'u_curr', 'u'])
        self.vo_name = self._find_var(self.ds_cmems, ['vo', 'v_curr', 'v'])

        # Drop depth dimension if present in CMEMS
        if 'depth' in self.ds_cmems.dims or 'depth' in self.ds_cmems.coords:
            self.ds_cmems = self.ds_cmems.isel(depth=0)

        # Subset CMEMS dynamically around ERA5 spatial region
        era5_lats = self.ds_era5[self.era5_lat_name].values
        era5_lons = self.ds_era5[self.era5_lon_name].values

        min_lat, max_lat = float(np.min(era5_lats)) - 0.5, float(np.max(era5_lats)) + 0.5
        min_lon, max_lon = float(np.min(era5_lons)) - 0.5, float(np.max(era5_lons)) + 0.5

        cmems_lats = self.ds_cmems[self.cmems_lat_name].values
        cmems_lons = self.ds_cmems[self.cmems_lon_name].values

        lat_mask = (cmems_lats >= min_lat) & (cmems_lats <= max_lat)
        lon_mask = (cmems_lons >= min_lon) & (cmems_lons <= max_lon)

        if np.any(lat_mask) and np.any(lon_mask):
            self.ds_cmems_sub = self.ds_cmems.sel({
                self.cmems_lat_name: cmems_lats[lat_mask],
                self.cmems_lon_name: cmems_lons[lon_mask]
            })
        else:
            self.ds_cmems_sub = self.ds_cmems

        # Set reference epoch for timestamp conversion (seconds since 2000-01-01)
        self.ref_epoch = pd.Timestamp("2000-01-01T00:00:00")

        # Build fast RegularGridInterpolators for ERA5 and CMEMS
        self._build_interpolators()

    def _find_coord(self, ds, candidates):
        candidate_list = [k for k in ds.coords]
        for c in candidate_list:
            if any(cand == c.lower() or cand in c.lower() for cand in candidates):
                return c
        return candidates[0]

    def _find_var(self, ds, candidates):
        var_list = [k for k in ds.data_vars]
        for v in var_list:
            v_lower = v.lower()
            long_name = str(ds[v].attrs.get('long_name', '')).lower()
            if any(cand == v_lower or cand in v_lower or cand in long_name for cand in candidates):
                return v
        return list(ds.data_vars.keys())[0]

    def _to_timestamp_sec(self, times_array):
        # Convert numpy datetime64 or pd.DatetimeIndex to float seconds relative to ref_epoch
        dt_index = pd.to_datetime(times_array)
        if getattr(dt_index, 'tz', None) is not None:
            dt_index = dt_index.tz_localize(None)
        return (dt_index - self.ref_epoch).total_seconds().values

    def _build_interpolators(self):
        # ERA5 Grid Setup
        e_time_sec = self._to_timestamp_sec(self.ds_era5[self.era5_time_name].values)
        e_lats = self.ds_era5[self.era5_lat_name].values.astype(float)
        e_lons = self.ds_era5[self.era5_lon_name].values.astype(float)

        # Sort latitude / longitude if descending (RegularGridInterpolator requires ascending coordinates)
        e_lat_order = np.argsort(e_lats)
        e_lon_order = np.argsort(e_lons)

        e_lats_sorted = e_lats[e_lat_order]
        e_lons_sorted = e_lons[e_lon_order]

        u10_vals = self.ds_era5[self.u10_name].values[:, e_lat_order, :][:, :, e_lon_order]
        v10_vals = self.ds_era5[self.v10_name].values[:, e_lat_order, :][:, :, e_lon_order]

        self.e_time_min, self.e_time_max = float(e_time_sec.min()), float(e_time_sec.max())
        self.e_lat_min, self.e_lat_max = float(e_lats_sorted.min()), float(e_lats_sorted.max())
        self.e_lon_min, self.e_lon_max = float(e_lons_sorted.min()), float(e_lons_sorted.max())

        self.interp_u10 = RegularGridInterpolator(
            (e_time_sec, e_lats_sorted, e_lons_sorted), u10_vals,
            bounds_error=False, fill_value=None
        )
        self.interp_v10 = RegularGridInterpolator(
            (e_time_sec, e_lats_sorted, e_lons_sorted), v10_vals,
            bounds_error=False, fill_value=None
        )

        # CMEMS Grid Setup
        c_time_sec = self._to_timestamp_sec(self.ds_cmems_sub[self.cmems_time_name].values)
        c_lats = self.ds_cmems_sub[self.cmems_lat_name].values.astype(float)
        c_lons = self.ds_cmems_sub[self.cmems_lon_name].values.astype(float)

        c_lat_order = np.argsort(c_lats)
        c_lon_order = np.argsort(c_lons)

        c_lats_sorted = c_lats[c_lat_order]
        c_lons_sorted = c_lons[c_lon_order]

        uo_vals = self.ds_cmems_sub[self.uo_name].values[:, c_lat_order, :][:, :, c_lon_order]
        vo_vals = self.ds_cmems_sub[self.vo_name].values[:, c_lat_order, :][:, :, c_lon_order]

        self.c_time_min, self.c_time_max = float(c_time_sec.min()), float(c_time_sec.max())
        self.c_lat_min, self.c_lat_max = float(c_lats_sorted.min()), float(c_lats_sorted.max())
        self.c_lon_min, self.c_lon_max = float(c_lons_sorted.min()), float(c_lons_sorted.max())

        self.interp_uo = RegularGridInterpolator(
            (c_time_sec, c_lats_sorted, c_lons_sorted), uo_vals,
            bounds_error=False, fill_value=None
        )
        self.interp_vo = RegularGridInterpolator(
            (c_time_sec, c_lats_sorted, c_lons_sorted), vo_vals,
            bounds_error=False, fill_value=None
        )

        print("[Environment] Spatiotemporal interpolators built successfully.")

    def get_vectors(self, lats, lons, timestamp):
        """
        Interpolate (u_wind, v_wind, u_curr, v_curr) at positions (lats, lons) and given timestamp.
        Safely clamps query coordinates and timestamps to valid grid boundaries.

        Parameters:
        -----------
        lats : np.ndarray
            1D array of particle latitudes.
        lons : np.ndarray
            1D array of particle longitudes.
        timestamp : pd.Timestamp, np.datetime64, or string
            Current simulation timestamp.

        Returns:
        --------
        tuple of (u_wind, v_wind, u_curr, v_curr) as 1D numpy arrays (in m/s).
        """
        if isinstance(timestamp, (str, pd.Timestamp, np.datetime64)):
            ts = pd.Timestamp(timestamp)
            if ts.tzinfo is not None:
                ts = ts.tz_localize(None)
            ts_sec = (ts - self.ref_epoch).total_seconds()
        else:
            ts_sec = float(timestamp)

        # Physically transparent boundary clamping to grid domain bounds
        e_t = np.clip(np.full_like(lats, ts_sec), self.e_time_min, self.e_time_max)
        e_lat = np.clip(lats, self.e_lat_min, self.e_lat_max)
        e_lon = np.clip(lons, self.e_lon_min, self.e_lon_max)
        pts_era5 = np.column_stack([e_t, e_lat, e_lon])

        c_t = np.clip(np.full_like(lats, ts_sec), self.c_time_min, self.c_time_max)
        c_lat = np.clip(lats, self.c_lat_min, self.c_lat_max)
        c_lon = np.clip(lons, self.c_lon_min, self.c_lon_max)
        pts_cmems = np.column_stack([c_t, c_lat, c_lon])

        u_wind = self.interp_u10(pts_era5)
        v_wind = self.interp_v10(pts_era5)
        u_curr = self.interp_uo(pts_cmems)
        v_curr = self.interp_vo(pts_cmems)

        # Replace any residual NaN extrapolations with 0.0
        u_wind = np.nan_to_num(u_wind, nan=0.0)
        v_wind = np.nan_to_num(v_wind, nan=0.0)
        u_curr = np.nan_to_num(u_curr, nan=0.0)
        v_curr = np.nan_to_num(v_curr, nan=0.0)

        return u_wind, v_wind, u_curr, v_curr
