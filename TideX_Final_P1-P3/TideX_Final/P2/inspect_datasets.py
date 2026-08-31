import os
import xarray as xr

era5_path = os.path.join('data', 'era5_region.nc')
cmems_path = os.path.join('data', 'cmems_mod_glo_phy-cur_anfc_0.083deg_PT6H-i_1788086797234.nc')

out = []
out.append("=== ERA5 REGION ===")
ds_era5 = xr.open_dataset(era5_path)
out.append(str(ds_era5))
out.append("--- ERA5 DIMS ---")
out.append(str(dict(ds_era5.dims)))
out.append("--- ERA5 COORDS ---")
for c in ds_era5.coords:
    v = ds_era5[c].values
    out.append(f"{c}: shape={v.shape}, min={v.min()}, max={v.max()}, dtype={v.dtype}")
out.append("--- ERA5 VARS ---")
for var in ds_era5.data_vars:
    out.append(f"{var}: dims={ds_era5[var].dims}, shape={ds_era5[var].shape}, attrs={dict(ds_era5[var].attrs)}")

out.append("\n=== CMEMS CURRENTS ===")
ds_cmems = xr.open_dataset(cmems_path)
out.append(str(ds_cmems))
out.append("--- CMEMS DIMS ---")
out.append(str(dict(ds_cmems.dims)))
out.append("--- CMEMS COORDS ---")
for c in ds_cmems.coords:
    v = ds_cmems[c].values
    out.append(f"{c}: shape={v.shape}, min={v.min()}, max={v.max()}, dtype={v.dtype}")
out.append("--- CMEMS VARS ---")
for var in ds_cmems.data_vars:
    out.append(f"{var}: dims={ds_cmems[var].dims}, shape={ds_cmems[var].shape}, attrs={dict(ds_cmems[var].attrs)}")

summary_text = "\n".join(out)
with open("data_summary.txt", "w") as f:
    f.write(summary_text)

print("Inspection completed.")
