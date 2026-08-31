import os
import xarray as xr

# Input and output paths
input_path = os.path.join('data', 'da1eb91a39ce1cff2bb15e83f3d5bfa7.nc')
output_path = os.path.join('data', 'era5_region.nc')

if not os.path.exists(input_path):
    for root, dirs, files in os.walk('data'):
        for f in files:
            if f.endswith('.nc') and f != 'era5_region.nc':
                input_path = os.path.join(root, f)
                break

print(f"Opening original ERA5 dataset: {input_path}")
ds = xr.open_dataset(input_path)

# Identify coordinate names
lat_name = next((c for c in ds.coords if 'lat' in c.lower()), 'latitude')
lon_name = next((c for c in ds.coords if 'lon' in c.lower()), 'longitude')
time_name = next((c for c in ds.coords if 'time' in c.lower() or c.lower() == 't'), 'time')

# Identify 10m u and v wind variables
u10_name = None
v10_name = None
for v in ds.data_vars:
    v_lower = v.lower()
    long_name = str(ds[v].attrs.get('long_name', '')).lower()
    if v_lower in ['u10', '10u', 'u10m'] or '10m u' in long_name or 'u-component' in long_name:
        u10_name = v
    elif v_lower in ['v10', '10v', 'v10m'] or '10m v' in long_name or 'v-component' in long_name:
        v10_name = v

if not u10_name or not v10_name:
    var_list = list(ds.data_vars.keys())
    u10_name = u10_name or var_list[0]
    v10_name = v10_name or (var_list[1] if len(var_list) > 1 else var_list[0])

# Select variables u10 and v10
ds_wind = ds[[u10_name, v10_name]]

# Subset spatial region: Latitude [14.0, 16.0] N, Longitude [71.0, 73.0] E
lat_vals = ds_wind[lat_name].values
lon_vals = ds_wind[lon_name].values

lat_mask = (lat_vals >= 14.0) & (lat_vals <= 16.0)
lon_mask = (lon_vals >= 71.0) & (lon_vals <= 73.0)

ds_subset = ds_wind.sel({
    lat_name: ds_wind[lat_name].values[lat_mask],
    lon_name: ds_wind[lon_name].values[lon_mask]
})

# Save subset to data/era5_region.nc
ds_subset.to_netcdf(output_path)

# Verify and print requested summary items
ds_out = xr.open_dataset(output_path)

out_lat = ds_out[lat_name].values
out_lon = ds_out[lon_name].values
out_time = ds_out[time_name].values

print("\n--- EXTRACTION REPORT ---")
print(f"Output Filename     : {output_path}")
print(f"Dimensions          : {dict(ds_out.dims)}")
print(f"Variables           : {list(ds_out.data_vars.keys())}")
print(f"Latitude Range      : {out_lat.min():.2f} N to {out_lat.max():.2f} N")
print(f"Longitude Range     : {out_lon.min():.2f} E to {out_lon.max():.2f} E")
print(f"Time Range          : {str(out_time[0])[:19]} to {str(out_time[-1])[:19]}")
print(f"Number of Time Steps : {len(out_time)}")
