import json
import sys
from pathlib import Path

import openeo
from openeo.api.process import Parameter
from openeo.processes import array_create
from openeo.rest.udp import build_process_dict
from openeo.rest.connection import Connection

from typing import List, Union

d_description = {
    "te": "Lorem Ipsum", 
    "bb": "Lorem Ipsum",
}

def composite(con: Connection,
              temporal_extent: List[str]|Parameter,
              spatial_extent: dict|Parameter,
              max_cloud_cover: int|Parameter):
    """
    ...
    """


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
    spatial_extend = Parameter.bounding_box(
        name = "bounding_box",
        description=d_description["bb"],
        default={"west": 11.1, "south": 48.0, "east": 11.3, "north": 48.2, "crs": "EPSG:4326"} 
    )

    scmap_composite = composite(
        
    )


def test_run():
    pass

if __name__ == "__main__":
    # save process to json
    with open(Path(__file__).parent / "scmap_composite.json", "w") as fp:
        json.dump(generate(), fp, indent=2)

