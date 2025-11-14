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


def generate_composite(xarr: xr.DataArray, value) -> XarrayDataCube:
    """
    Lorem Ipsum
    :param xarr: abc
    :param value: abc
    :return: Datacube 
    """
    print(xarr)
     
    result = xarr.mean(dim="t", skipna=True)    # keepdims=False
    return XarrayDataCube(result)

def apply_datacube(cube: XarrayDataCube, context: Dict) -> XarrayDataCube:
    value = context.get('value', None)

    return generate_composite(xarr=cube.get_array(), value=value)