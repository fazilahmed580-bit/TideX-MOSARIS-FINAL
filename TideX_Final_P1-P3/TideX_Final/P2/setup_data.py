import os
import sys
import json
import pandas as pd
import numpy as np
from p1_loader import load_p1_data


def prepare_p1_data():
    """
    Reproducible environmental data downloader & validator for real P1 spill case.
    Dynamically ingests P1 metadata & AOI bounds, verifies existing forcing datasets,
    or fetches missing forcing via CDS API (ERA5) and Copernicus Marine Client (CMEMS).
    """
    print("=" * 60)
    print("TideX P2 Environmental Data Setup & Reproducibility Check")
    print("=" * 60)

    # 1. Dynamically load P1 satellite observation metadata & AOI bounds
    p1_info = load_p1_data(
        geojson_path=os.path.join('data', 'spill_aoi.geojson'),
        metadata_path=os.path.join('data', 'metadata.json')
    )

    centroid = p1_info["centroid"]
    bounds = p1_info["aoi_bounds"]
    obs_date = p1_info["observation_date"]

    print("\n[P1 Observation Parameters]")
    print(f"Observation Date : {obs_date}")
    print(f"Spill Centroid   : Lat {centroid['lat']}°N, Lon {centroid['lon']}°E")
    print(f"AOI Bounds       : Lon [{bounds[0]:.4f}, {bounds[2]:.4f}], Lat [{bounds[1]:.4f}, {bounds[3]:.4f}]")

    target_era5_path = os.path.join('data', 'era5_p1_2018.nc')
    target_cmems_path = os.path.join('data', 'cmems_p1_2018.nc')

    era5_ready = os.path.exists(target_era5_path)
    cmems_ready = os.path.exists(target_cmems_path)

    print("\n[Environmental File Status]")
    print(f"ERA5 P1 Forcing  ({target_era5_path}) : {'PRESENT' if era5_ready else 'MISSING'}")
    print(f"CMEMS P1 Forcing ({target_cmems_path}): {'PRESENT' if cmems_ready else 'MISSING'}")

    if era5_ready and cmems_ready:
        print("\nAll required real P1 2018 environmental forcing datasets are present in data/!")
        print("Fresh clone reproducibility check passed. You can run: python test_p2.py")
        return True

    # Compute requested temporal & spatial downloading window with 1.0 deg margin
    buffer_deg = 1.0
    min_lon = max(-180.0, bounds[0] - buffer_deg)
    max_lon = min(180.0, bounds[2] + buffer_deg)
    min_lat = max(-90.0, bounds[1] - buffer_deg)
    max_lat = min(90.0, bounds[3] + buffer_deg)

    start_date = (pd.to_datetime(obs_date) - pd.Timedelta(days=2)).strftime("%Y-%m-%d")
    end_date = (pd.to_datetime(obs_date) + pd.Timedelta(days=2)).strftime("%Y-%m-%d")

    print(f"\n[Download Request Specifications]")
    print(f"Dataset ERA5  : reanalysis-era5-single-levels (10m_u_component_of_wind, 10m_v_component_of_wind)")
    print(f"Dataset CMEMS : cmems_mod_glo_phy_my_0.083deg_P1D-m (uo, vo at ~0.494m depth)")
    print(f"Date Range    : {start_date} to {end_date}")
    print(f"Bounding Box  : Lat [{min_lat:.2f}, {max_lat:.2f}] N, Lon [{min_lon:.2f}, {max_lon:.2f}] E")

    # 2. Download missing ERA5 forcing via cdsapi
    if not era5_ready:
        print("\nAttempting ERA5 download via CDS API...")
        try:
            import cdsapi
            client = cdsapi.Client()
            print(f"Requesting ERA5 wind data for {start_date} to {end_date}...")
            client.retrieve(
                'reanalysis-era5-single-levels',
                {
                    'product_type': 'reanalysis',
                    'format': 'netcdf',
                    'variable': [
                        '10m_u_component_of_wind',
                        '10m_v_component_of_wind',
                    ],
                    'date': f"{start_date}/{end_date}",
                    'time': [f"{h:02d}:00" for h in range(24)],
                    'area': [max_lat, min_lon, min_lat, max_lon],
                },
                target_era5_path
            )
            print(f"Successfully downloaded ERA5 forcing to {target_era5_path}")
            era5_ready = True
        except Exception as e:
            print(f"\n[ERA5 Download Failed] {e}")
            print("\n--- CDS API Setup Instructions ---")
            print("1. Register for a free account at https://cds.climate.copernicus.eu/")
            print("2. Obtain your API Key from your CDS user profile.")
            print("3. Set environment variable in PowerShell:")
            print('   $env:CDSAPI_KEY="YOUR_API_KEY"')

    # 3. Download missing CMEMS forcing via copernicusmarine
    if not cmems_ready:
        print("\nAttempting CMEMS download via Copernicus Marine API...")
        cm_user = os.environ.get("COPERNICUSMARINE_USER") or os.environ.get("COPERNICUS_USER")
        cm_pass = os.environ.get("COPERNICUSMARINE_PASSWORD") or os.environ.get("COPERNICUS_PASSWORD")
        try:
            import copernicusmarine
            print(f"Requesting CMEMS surface current data for {start_date} to {end_date}...")
            copernicusmarine.subset(
                dataset_id="cmems_mod_glo_phy_my_0.083deg_P1D-m",
                variables=["uo", "vo"],
                minimum_longitude=min_lon,
                maximum_longitude=max_lon,
                minimum_latitude=min_lat,
                maximum_latitude=max_lat,
                start_datetime=f"{start_date} 00:00:00",
                end_datetime=f"{end_date} 23:59:59",
                minimum_depth=0.4,
                maximum_depth=0.6,
                output_filename=target_cmems_path,
                username=cm_user,
                password=cm_pass
            )
            print(f"Successfully downloaded CMEMS forcing to {target_cmems_path}")
            cmems_ready = True
        except Exception as e:
            print(f"\n[CMEMS Download Failed] {e}")
            print("\n--- CMEMS API Setup Instructions ---")
            print("1. Register for a free account at https://marine.copernicus.eu/")
            print("2. Set environment variables in PowerShell:")
            print('   $env:COPERNICUSMARINE_USER="YOUR_USERNAME"')
            print('   $env:COPERNICUSMARINE_PASSWORD="YOUR_PASSWORD"')

    if era5_ready and cmems_ready:
        print("\nData setup completed successfully.")
        return True
    else:
        print("\n" + "!" * 60)
        print("DATA SETUP WARNING: Environmental forcing files could not be fetched automatically.")
        print("Please set your API credentials or verify datasets in data/.")
        print("!" * 60)
        return False


if __name__ == '__main__':
    prepare_p1_data()
