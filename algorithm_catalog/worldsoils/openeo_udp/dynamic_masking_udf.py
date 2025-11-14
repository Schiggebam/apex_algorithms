import numpy as np
import xarray as xr
from typing import Dict
from openeo.udf.xarraydatacube import XarrayDataCube


def apply_datacube(cube: XarrayDataCube, context: dict) -> XarrayDataCube:
    """
    This function is executed by apply_dimension(dimension="t").
    Therefore the input cube has shape:

        dims = ('t', 'bands', 'y', 'x')

    We compute pvir2 for all time slices, compare it with the threshold
    (which is a separate band), mask the reflectance bands, and then
    reduce the time dimension by mean.
    """
    arr: xr.DataArray = cube.get_array()

    # --- Identify bands ---
    all_bands = list(arr.coords["bands"].values)

    # Reflectance bands B02..B12 (three characters and starting with B)
    refl_bands = [b for b in all_bands if b.startswith("B") and len(b) == 3]

    # Threshold band
    th_band = "th_img"

    # --- Select subsets ---
    refl = arr.sel(bands=refl_bands)
    b04  = arr.sel(bands="B04")
    b08  = arr.sel(bands="B08")
    b12  = arr.sel(bands="B12")
    th   = arr.sel(bands=th_band)          # dims: ('t', 'y', 'x')

    # Expand threshold to match reflectance bands
    th = th.broadcast_like(b04)             # now dims match ('t','y','x')

    # --- Compute indices ---
    ndvi = (b08 - b04) / (b08 + b04)
    nbr  = (b08 - b12) / (b08 + b12)
    pvir2 = ndvi + nbr                       # dims: ('t','y','x')

    # --- Create mask for each time slice ---
    mask = pvir2 > th                        # dims: ('t','y','x')

    # Apply mask to all reflectance bands
    refl_masked = xr.where(mask, np.nan, refl)

    # --- Reduce time dimension ---
    # refl_mean = refl_masked.mean(dim="t", skipna=True)

    return XarrayDataCube(refl_masked)


# def apply_datacube(cube: XarrayDataCube, context: dict) -> XarrayDataCube:
#     xarr: xr.DataArray = cube.get_array()
#     # dims: typically ('t',) for apply(), or scalar for reduce_dimension
# 
#     # reflectance bands (filter by names)
#     refl_bands = [b for b in xarr.coords["bands"].values if b.startswith("B")]
#     refl = xarr.sel(bands=refl_bands)
# 
#     # pvir2 and threshold image
#     pvir2 = xarr.sel(bands="pvir2")
#     th    = xarr.sel(bands="th_img")
# 
#     # mask per pixel, per timestep
#     mask = pvir2 > th
# 
#     # apply mask
#     refl_masked = xr.where(mask, np.nan, refl)
# 
#     return XarrayDataCube(refl_masked)


# def apply_datacube(cube: XarrayDataCube, context: dict) -> XarrayDataCube:
#     """
#     cube dims: (bands, t, y, x)
#     """
#     xarr: xr.DataArray = cube.get_array()
# 
#     # Extract required bands
#     pvir2  = xarr.sel(bands="pvir2")
#     th_img = xarr.sel(bands="th_img")
# 
#     print("DEBUG pvir2:", float(pvir2.min()), float(pvir2.max()))
#     print("DEBUG th_img:", float(th_img.min()), float(th_img.max()))
#     print("DEBUG ratio:", float((pvir2 - th_img).min()), float((pvir2 - th_img).max()))
# 
#     # Mask condition
#     mask = pvir2 > th_img
# 
#     # Apply mask only to reflectance bands
#     refl_bands = [b for b in xarr.bands.values if b.startswith("B")]
# 
#     result = xarr.copy()
# 
#     for b in refl_bands:
#         result.loc[dict(bands=b)] = xr.where(
#             mask, 
#             result.sel(bands=b), 
#             float(np.nan)
#         )
# 
#     # Do not mask pvir2 or threshold band → keep unchanged
#     return XarrayDataCube(result)