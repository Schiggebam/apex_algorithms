import xarray as xr
import numpy as np
from openeo.udf.xarraydatacube import XarrayDataCube

from typing import Dict

def generate_composite(xarr: xr.DataArray, value) -> XarrayDataCube:
    """
    Lorem Ipsum
    :param xarr: abc
    :param value: abc
    :return: Datacube 
    """
    print(xarr)

    result = xarr.copy()                             # same as input
    result.values = np.zeros(xarr.values)            # exchange data
    return XarrayDataCube(result)

def apply_datacube(cube: XarrayDataCube, context: Dict) -> XarrayDataCube:
    value = context.get('value', None)

    return generate_composite(xarr=cube.get_array(), value=value)