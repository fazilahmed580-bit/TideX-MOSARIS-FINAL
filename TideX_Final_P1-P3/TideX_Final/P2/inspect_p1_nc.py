import os
import pandas as pd
import xarray as xr

e_path = os.path.join('data', 'era5_p1_2018.nc')
c_path = os.path.join('data', 'cmems_p1_2018.nc')

ds_e = xr.open_dataset(e_path)
ds_c = xr.open_dataset(c_path)

print("=== ERA5 P1 2018 ===")
print("Time:", ds_e.coords['time'].values.min(), "to", ds_e.coords['time'].values.max())
print("Lat:", ds_e.coords['latitude'].values.min(), "to", ds_e.coords['latitude'].values.max())
print("Lon:", ds_e.coords['longitude'].values.min(), "to", ds_e.coords['longitude'].values.max())

print("\n=== CMEMS P1 2018 ===")
print("Time:", ds_c.coords['time'].values.min(), "to", ds_c.coords['time'].values.max())
print("Lat:", ds_c.coords['latitude'].values.min(), "to", ds_c.coords['latitude'].values.max())
print("Lon:", ds_c.coords['longitude'].values.min(), "to", ds_c.coords['longitude'].values.max())
