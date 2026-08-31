import xarray as open_nc
import os

filepath = r'data/da1eb91a39ce1cff2bb15e83f3d5bfa7.nc'
if not os.path.exists(filepath):
    for root, dirs, files in os.walk('.'):
        if 'da1eb91a39ce1cff2bb15e83f3d5bfa7.nc' in files:
            filepath = os.path.join(root, 'da1eb91a39ce1cff2bb15e83f3d5bfa7.nc')
            break

print(f"Dataset path: {filepath}")
ds = open_nc.open_dataset(filepath)

print("\n--- DATASET OVERVIEW ---")
print(ds)

print("\n--- DIMENSIONS ---")
print(ds.dims)

print("\n--- COORDINATES ---")
for coord_name in ds.coords:
    coord = ds[coord_name]
    print(f"Coordinate: {coord_name}")
    print(f"  Shape: {coord.shape}")
    print(f"  Min: {coord.values.min()}, Max: {coord.values.max()}")
    print(f"  Attributes: {dict(coord.attrs)}")

print("\n--- VARIABLES AND ATTRIBUTES ---")
for var_name in ds.data_vars:
    var = ds[var_name]
    print(f"Variable: {var_name}")
    print(f"  Dimensions: {var.dims}")
    print(f"  Shape: {var.shape}")
    print(f"  Attributes: {dict(var.attrs)}")

print("\n--- SPECIFIC FIELDS FOR USER REQUEST ---")
# Latitude range
lat_var = None
for k in ds.coords:
    if 'lat' in k.lower():
        lat_var = k
        break

if lat_var:
    lat_vals = ds[lat_var].values
    print(f"Latitude Range: min = {lat_vals.min()}, max = {lat_vals.max()}")

# Longitude range
lon_var = None
for k in ds.coords:
    if 'lon' in k.lower():
        lon_var = k
        break

if lon_var:
    lon_vals = ds[lon_var].values
    print(f"Longitude Range: min = {lon_vals.min()}, max = {lon_vals.max()}")

# Time range
time_var = None
for k in ds.coords:
    if 'time' in k.lower() or k.lower() == 't':
        time_var = k
        break

if time_var:
    time_vals = ds[time_var].values
    print(f"Time Range: start = {time_vals[0]}, end = {time_vals[-1]}, num_time_steps = {len(time_vals)}")

# 10m u-wind and 10m v-wind detection
u10_var = None
v10_var = None
for var_name in ds.variables:
    var = ds[var_name]
    long_name = str(var.attrs.get('long_name', '')).lower()
    standard_name = str(var.attrs.get('standard_name', '')).lower()
    if var_name.lower() in ['u10', '10u', 'u10m'] or '10m u' in long_name or '10m_u' in standard_name or 'u-component of wind' in long_name or 'eastward_wind' in standard_name:
        u10_var = (var_name, dict(var.attrs))
    if var_name.lower() in ['v10', '10v', 'v10m'] or '10m v' in long_name or '10m_v' in standard_name or 'v-component of wind' in long_name or 'northward_wind' in standard_name:
        v10_var = (var_name, dict(var.attrs))

print(f"\n10m U-Wind Variable: {u10_var}")
print(f"10m V-Wind Variable: {v10_var}")
