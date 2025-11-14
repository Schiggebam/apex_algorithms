import numpy as np
import xarray as xr
from typing import Dict
from openeo.udf.xarraydatacube import XarrayDataCube


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


def apply_datacube(cube: XarrayDataCube, context: dict) -> XarrayDataCube:
    """
    cube dims: (bands, t, y, x)
    """
    xarr: xr.DataArray = cube.get_array()

    # Extract required bands
    pvir2  = xarr.sel(bands="pvir2")
    th_img = xarr.sel(bands="th_img")

    # Mask condition
    mask = pvir2 > th_img

    # Apply mask only to reflectance bands
    refl_bands = [b for b in xarr.bands.values if b.startswith("B")]

    result = xarr.copy()

    for b in refl_bands:
        result.loc[dict(bands=b)] = xr.where(
            mask, 
            result.sel(bands=b), 
            float(np.nan)
        )

    # Do not mask pvir2 or threshold band → keep unchanged
    return XarrayDataCube(result)