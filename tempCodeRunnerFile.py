import nctoolkit as nc
import xarray as xr
ds = nc.open_url("https://www.ncei.noaa.gov/data/sea-surface-temperature-whoi/access/1988/")
ds_xr = ds.to_xarray()