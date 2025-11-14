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
        Path(__file__).parent / "scmap_composite_udf.py",
        runtime="Python", 
        version="3.8",
        context={
            'value': value
        }
    )

    # scm_composite = (s2_cube.apply(process=udf_process))
    scm_composite = s2_cube.reduce_dimension(dimension='t', reducer=udf_process)

    return scm_composite


def auth(url: str="openeo.dataspace.copernicus.eu") -> Connection:
    connection = openeo.connect(url=url)
    connection.authenticate_oidc()
    return connection


def generate() -> dict:
    # TODO (paul) : Possibily replace with openeo.connect("openeofed.dataspace.copernicus.eu")
    con: Connection = auth()

    temporal_extent = Parameter.temporal_interval(
        name="temporal_extent",
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

    schema = {
        "description": "Bare surface composite with statistical producs",
        "schema": {
            "type": "object",
            "subtype": "datacube"
        }
    }

    return build_process_dict(
        process_graph=scmap_composite,
        process_id="scmap_composite",
        summary="Bare surface composite with statistical producs",
        description=(
            Path(__file__).parent / "Readme.md"
        ).read_text(),
        parameters=[
            temporal_extent,
            spatial_extent,
            max_scene_cloud_cover,
        ],
        returns=schema,
        categories=["sentinel-2", "composites", "bare surface"]
    )


def test_run():
    con = auth()
    bbox = { "west": 11.15, "south": 48.05, "east": 11.3, "north": 48.2, "crs": "EPSG:4326"}
    temporal_extent = ["2025-03-15", "2025-05-07"]
    composite = con.datacube_from_process(
        "scmap_composite", 
        namespace="https://raw.githubusercontent.com/Schiggebam/apex_algorithms/refs/heads/scmap/algorithm_catalog/worldsoils/openeo_udp/scmap_composite.json",
        temporal_extent=temporal_extent,
        spatial_extent=bbox,
        max_cloud_cover=80
    )
    composite.execute_batch()


if __name__ == "__main__":
    if False:
        test_run()
        exit()
    # save process to json
    with open(Path(__file__).parent / "scmap_composite.json", "w") as fp:
        json.dump(generate(), fp, indent=2)

