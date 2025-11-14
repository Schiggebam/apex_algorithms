import numpy as np
import xarray as xr
from typing import Dict
from openeo.udf.xarraydatacube import XarrayDataCube


def apply_datacube(cube: XarrayDataCube, context: Dict) -> XarrayDataCube:
    # Convert to xarray
    xarr: xr.DataArray = cube.get_array()  
    # dims: (t, bands, y, x)

    # --- Extract bands ---
    # reflectance = all S2 bands B02 .. B12
    refl_bands = [b for b in xarr.bands.values if b.startswith("B")]
    refl = xarr.sel(bands=refl_bands)

    # threshold image (2D or 3D)
    th = xarr.sel(bands="th_img")

    # pvir2 band
    pvir2 = xarr.sel(bands="pvir2")

    # --- Ensure threshold image broadcasts properly ---
    # If threshold is 2D (x,y) but pvir2 is 3D (t,x,y), broadcast:
    if "t" not in th.dims:
        th = th.expand_dims({"t": pvir2.coords["t"].values})  # broadcast temporally

    # --- Build mask ---
    # True where pixel should be masked
    mask = pvir2 > th

    # Broadcast mask to all reflectance bands
    mask = mask.broadcast_like(refl)

    # Apply mask (set bad pixels to NaN)
    refl_masked = xr.where(mask, np.nan, refl)

    # Return only masked reflectance bands
    return XarrayDataCube(refl_masked)
