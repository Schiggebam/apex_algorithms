import xarray as xr
import numpy as np
from openeo.udf.xarraydatacube import XarrayDataCube

from typing import Dict

def _nmad(xarr: xr.DataArray) -> xr.DataArray:
    b02 = xarr.sel(bands='B02')
    median = b02.median(dim=TIME, skipna=True)               
    dev = np.abs(b02 - median)                          
    mad = dev.median(dim=TIME, skipna=True)                  
    nmad = 1.4826 * mad
    upper = median + nmad_sigma * nmad

    cond = (b02 > upper) & (b02 > (median + 80.0))
    cond = cond.broadcast_like(xr_data)           

    return xr.where(cond, np.nan, xarr)


def _pvir2(xarr: xr.DataArray) -> xr.DataArray:
    b04 = xarr.sel(bands='B02')
    b08 = xarr.sel(bands='B08')
    b12 = xarr.sel(bands='B12')

    return ((b08 - b04) / (b08 + b04)) + ((b08 - b12) / (b08 + b12))


def generate_composite(xarr: xr.DataArray, value) -> XarrayDataCube:
    """
    Lorem Ipsum
    :param xarr: abc
    :param value: abc
    :return: Datacube 
    """

    b_bands = [b for b in xarr.bands.values if b.startswith("B") and len(b) == 3]
    th_img = xarr.sel(bands='S2_s2cr_pvir2_threshold_img')
    xarr_reflectance = xarr.sel(bands=b_bands)

    th = .2
    idx = _pvir2(xarr_reflectance)
    cond_idx = (idx > th_img).broadcast_like(xarr_reflectance)

    xarr_reflectance = xr.where(cond_idx, np.nan, xarr_reflectance)

    result_src      = xarr_reflectance.mean(dim="t", skipna=True)    # keepdims=False
    result_src_std  = xarr_reflectance.std(dim="t", skipna=True)

    result_src = result_src.assign_coords({
        "bands": [f"SRC_{b}" for b in result_src["bands"].values]
    })
    result_src_std = result_src_std.assign_coords({
        "bands": [f"SRC_STD_{b}" for b in result_src_std["bands"].values]
    })

    result = xr.concat([result_src, result_src_std], dim="bands")
    return XarrayDataCube(result)

def apply_datacube(cube: XarrayDataCube, context: Dict) -> XarrayDataCube:
    value = context.get('value', None)

    return generate_composite(xarr=cube.get_array(), value=value)