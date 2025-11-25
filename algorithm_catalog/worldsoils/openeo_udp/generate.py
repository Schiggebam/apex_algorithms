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

def scl_to_masks(scl_layer):
        to_mask = openeo.processes.any(
            array_create(
                [
                    scl_layer == SCL_LEGEND["cloud_shadows"],
                    scl_layer == SCL_LEGEND["cloud_medium_probability"],
                    scl_layer == SCL_LEGEND["cloud_high_probability"],
                    scl_layer == SCL_LEGEND["thin_cirrus"],
                    scl_layer == SCL_LEGEND["saturated_or_defective"],
                    scl_layer == SCL_LEGEND["snow"],
                    scl_layer == SCL_LEGEND["no_data"],
                    scl_layer == SCL_LEGEND["dark_area_pixels"],
                    scl_layer == SCL_LEGEND["unclassified"],
                ]
            ),
        )

        return to_mask

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
        bands=S2_BANDS,
        spatial_extent=spatial_extent,
        temporal_extent=temporal_extent,
        max_cloud_cover=max_cloud_cover,
    )

    scl = con.load_collection(
        collection_id="SENTINEL2_L2A",
        temporal_extent=temporal_extent,
        spatial_extent=spatial_extent,
        bands=["SCL"],
        max_cloud_cover=max_cloud_cover,
    )

    worldcover = con.load_collection(
        "ESA_WORLDCOVER_10M_2021_V2",
        spatial_extent=spatial_extent,
        # temporal_extent=["2021-01-01", "2021-12-31"],
        bands=["MAP"]
    )
    worldcover = worldcover.reduce_dimension(dimension="t", reducer="first")
    

    cloud_mask = scl.apply(process=scl_to_masks)

    s2_cube = s2_cube.mask(cloud_mask)

    ### Threshold image ###
    # stac_url_th_img = "https://raw.githubusercontent.com/Schiggebam/dlr_scmap_resources/refs/heads/main/scmap-pvir2%2Bnbr-sen2cor-thresholds-eu-v1.json"
    # stac_url_th_img = "https://github.com/Schiggebam/dlr_scmap_resources/raw/main/th_S2_s2cr_buffered_stac_yflip_timerange.json"
    # stac_url_th_img = "https://raw.githubusercontent.com/EmileSonneveld/dlr_scmap_resources/refs/heads/main/th_S2_s2cr_buffered_stac_yflip.json"
    stac_url_th_img = "https://raw.githubusercontent.com/Schiggebam/dlr_scmap_resources/refs/heads/main/th_S2_s2cr_buffered_stac_yflip_no_t.json"
    th_item = con.load_stac(stac_url_th_img, bands=["S2_s2cr_pvir2_threshold_img"], spatial_extent=spatial_extent)
    thresholds = th_item.resample_cube_spatial(s2_cube, method="bilinear").reduce_dimension(dimension="bands", reducer="first")
    worldcover = worldcover.resample_cube_spatial(s2_cube, method="near")

    # s2_cube = s2_cube.merge_cubes(thresholds)

    # b_scl = s2_cube.band("SCL")
    # cond_scl = ~((b_scl == SCL_LEGEND['vegetation']) | (b_scl == SCL_LEGEND['not_vegetated']) | (b_scl == SCL_LEGEND['water']))
    # s2_cube = s2_cube.mask(cond_scl)

    
    s2_merged = s2_cube

    b_04 = s2_merged.band("B04")
    b_08 = s2_merged.band("B08")
    b_12 = s2_merged.band("B12")

    ndvi  = (b_08 - b_04) / (b_08 + b_04)
    nbr   = (b_08 - b_12) / (b_08 + b_12)
    pvir2 = ndvi + nbr
    
    pvir2_named = pvir2.add_dimension(name="bands", label="pvir2", type="bands")
    th_named = thresholds.add_dimension(name="bands", label="th_img", type="bands")
    th_named = th_named.reduce_dimension(dimension="t", reducer="mean")

    s2_merged = s2_merged.merge_cubes(pvir2_named)
    s2_merged = s2_merged.merge_cubes(th_named)
    
    
    # th = 0.2
    th = s2_merged.band("th_img") 

    mask = s2_merged.band("pvir2") > th
    s2_masked = s2_merged.mask(mask)

    # value = 3.1415
# 
    # udf_process = openeo.UDF.from_file(
    #     Path(__file__).parent / "scmap_composite_udf.py",
    #     runtime="Python", 
    #     version="3.8",
    #     context={
    #         'value': value
    #     }
    # )
    # udf = openeo.UDF.from_file(
    #     Path(__file__).parent / "dynamic_masking_udf.py",
    #     runtime="Python",
    #     version="3.8"
    # )

    # pvir2 = s2_merged.band("pvir2")
    # s2_masked = s2_merged.apply_dimension(dimension="bands", process=mask_x)
    
    cond_wc = (worldcover == 50) | (worldcover == 80)
    s2_masked = s2_masked.mask(cond_wc)

    src = s2_masked.reduce_dimension(dimension="t", reducer="mean")

    # s2_cube = s2_cube.apply(process=udf_process)
    # scm_composite = s2_cube.reduce_dimension(dimension='t', reducer=udf_process)

    return src


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
    bbox = { "west": 11, "south": 48, "east": 11.2, "north": 48.2, "crs": "EPSG:4326"}
    temporal_extent = ["2025-04-15", "2025-05-07"]
    # composite = con.datacube_from_process(
    #     "scmap_composite",
    #     namespace="https://raw.githubusercontent.com/Schiggebam/apex_algorithms/refs/heads/scmap/algorithm_catalog/worldsoils/openeo_udp/scmap_composite.json",
    #     temporal_extent=temporal_extent,
    #     spatial_extent=bbox,
    #     max_cloud_cover=80
    # )
    # composite.execute_batch()
    scmap_composite = composite(
        con=con,
        temporal_extent=temporal_extent,
        spatial_extent=bbox,
        max_cloud_cover=80,
    )
    job = scmap_composite.create_job(title="scmap_composite")
    job.start_and_wait()
    job.get_results().download_files()


if __name__ == "__main__":
    if False:
        test_run()
        exit()
    # save process to json
    with open(Path(__file__).parent / "scmap_composite.json", "w") as fp:
        json.dump(generate(), fp, indent=2)

