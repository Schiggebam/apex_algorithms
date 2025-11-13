import json
import sys
from pathlib import Path

# 9anmsR9Uefg6aAk

import openeo
from openeo.api.process import Parameter
from openeo.processes import array_create
from openeo.rest.udp import build_process_dict
from openeo.rest.connection import Connection

from typing import List, Union

d_description = {
    "te": "Lorem Ipsum", 
    "bb": "Lorem Ipsum",
    "cc": "Maximum allowed scene-wide cloud cover for the scene to be considered in the composite"
}

S2_BANDS = "B02 B03 B04 B05 B06 B07 B08 B8A B11 B12".split()

SCL_LEGEND = {
        "no_data": 0,
        "saturated_or_defective": 1,
        "dark_area_pixels": 2,
        "cloud_shadows": 3,
        "vegetation": 4,
        "not_vegetated": 5,
        "water": 6,
        "unclassified": 7,
        "cloud_medium_probability": 8,
        "cloud_high_probability": 9,
        "thin_cirrus": 10,
        "snow": 11}

def composite(con: Connection,
              temporal_extent: List[str]|Parameter,
              spatial_extent: dict|Parameter,
              max_cloud_cover: int|Parameter) -> openeo.DataCube:
    """
    ...
    """

    ### Input Data ###
    s2_cube = con.load_collection(
        collection_id="SENTINEL2_L2A",
        bands=S2_BANDS + ['SCL', 'sunZenithAngles'],
        spatial_extent=spatial_extent,
        temporal_extent=temporal_extent
    )

    b_scl = s2_cube.band("SCL")
    cond_scl = ~((b_scl == SCL_LEGEND['vegetation']) | (b_scl == SCL_LEGEND['not_vegetated']) | (b_scl == SCL_LEGEND['water']))

    s2_cube = s2_cube.mask(cond_scl)

    value = 3.1415

    udf_process = openeo.UDF.from_file(
        "scmap_composite_udf.py",
        runtime="Python", 
        context={
            'value': value
        }
    )


def auth(url: str="openeo.dataspace.copernicus.eu") -> Connection:
    connection = openeo.connect(url=url)
    connection.authenticate_oidc()
    return connection


def generate() -> dict:
    # TODO (paul) : Possibily replace with openeo.connect("openeofed.dataspace.copernicus.eu")
    con: Connection = auth()

    temporal_extent = Parameter.temporal_interval(
        name="temporal_extend",
        description=d_description["te"]
    )
    spatial_extent = Parameter.bounding_box(
        name = "bounding_box",
        description=d_description["bb"],
        default={"west": 11.1, "south": 48.0, "east": 11.3, "north": 48.2, "crs": "EPSG:4326"} 
    )
    max_scene_cloud_cover = Parameter.number(
        name = "max_cloud_cover",
        description=d_description["cc"], 
        default=80
    )

    scmap_composite = composite(
        con=con, 
        temporal_extent=temporal_extent,
        spatial_extent=spatial_extent,
        max_cloud_cover=max_scene_cloud_cover
    )


def test_run():
    pass

if __name__ == "__main__":
    # save process to json
    with open(Path(__file__).parent / "scmap_composite.json", "w") as fp:
        json.dump(generate(), fp, indent=2)

