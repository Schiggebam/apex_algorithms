# SCMaP OpenEO User defined process
This algorithm is used to build bare surface mean composites, by averaging all bare surface observations over a specfic range in time.

For a detailed description about the algorithm, please refer to the [Documentation](https://download.geoservice.dlr.de/SOILSUITE/files/EUROPE_5Y/000_Data_Overview/SoilSuite_Data_Description_Europe_V1.pdf) of SoilSuite, or to any of the papers linked below.


## Usage
Plese refer to the APEx Documentation [Documentation](https://esa-apex.github.io/apex_documentation/guides/udp_writer_guide.html) and the [GitHub](https://github.com/ESA-APEx/apex_algorithms)

## Literature references
[SoilSuite Europe](https://geoservice.dlr.de/web/datasets/soilsuite_eur_5y)
- Rogge, D., Bauer, A, Zeidler, J., Müller, A., Esch, T. and Heiden, U. (2018). Building an exposed soil composite processor (SCMaP) for mapping spatial and temporal characteristics of soils with Landsat imagery (1984-2014). Remote Sensing of Environment, 205, 1-17. ISSN 0034-4257 DOI: 10.3390/rs14184526
- Heiden, U., d’Angelo, P., Schwind, P., Karlshöfer, P., Müller, R., Zepp, S., Wiesmeier, M., & Reinartz, P. (2022). Soil Reflectance Composites—Improved Thresholding and Performance Evaluation. Remote Sensing, 14(18), 4526. DOI: 10.1016/j.rse.2017.11.004
- Karlshoefer, P., d’Angelo, P., Eberle, J., & Heiden, U. (2025). Evaluation framework for the generation of continental bare surface reflectance composites. Geoderma, 459. DOI: 10.1016/j.geoderma.2025.117340


## License
[CC-BY-4.0](https://spdx.org/licenses/CC-BY-4.0)

## Authors / Contact
- Uta Heiden (Producer, Processor) DLR/EOC Imaging Spectroscopy
- - uta.heiden@dlr.de
- Pablo d'Angelo (Producer, Processor) DLR/EOC Photogrammetry and Image Analysis
- - pablo.angelo.dlr.de
- Paul Karlshöfer (Producer, Processor, OpenEO UDP) DLR/EOC Imaging Spectroscopy
- - paul.karlshoefer@dlr.de
EOC Geoservice (Host) DLR/EOC


## Acknowledgments / Funding
- European Space Agency





Author: paul.karlshoefer@dlr.de (German Aerospace Center)

# Description

This algorithm generates a Sentinel-2 based composite for a selected area and temporal extent. By default, the resolution of the output is 10 meters.

The used compositing method is the "max-NDVI" method, which selects the pixel with the highest NDVI value for each pixel location and within the time window.
The method falls under the 'rank composite' category, and ensures that selected spectral band values for any individual pixel all come from the same observation.

The method generates good results for timeseries analytics, but spatially neighbouring pixels may be selected from different observations,
which leads to visual discontinuities in the result.

# Performance characteristics

The method is computationally efficient, as it only requires the B04, B08 and SCL bands to determine the rank score. Loading
of other bands can be minimized to read only selected observations.


# Examples

The image below shows a typical result over an agricultural area.

![max_ndvi_example.png](max_ndvi_example.png)

The examples below show typical resource usage figures. They illustrate that the cost varies as a function of the parameters,
and most importantly that it is not possible to linearly extrapolate the cost from one example to another.


## 3-month composite over Denmark

A complete example including STAC metadata is shown here:

https://radiantearth.github.io/stac-browser/#/external/s3.waw3-1.cloudferro.com/swift/v1/APEx-examples/max_ndvi_denmark/collection.json

The processing platform reported these usage statistics for the example:

```
Credits: 63
CPU usage: 47.743,722 cpu-seconds
Wall time: 1.948 seconds
Input Pixel 10.997,635 mega-pixel
Max Executor Memory: 3,239 gb
Memory usage: 154.767.121,977 mb-seconds
Network Received: 1.677.537.930.040 b
```

The relative cost is 1 CDSE platform credits per km² for a 3 month input window.
The cost per input pixel is 0.0057 credits per megapixel.

## 15-month composite over Denmark

In a second example, a longer compositing window was tested, generating a 3-band result. Here we see a lower cost per km², but a similar cost per input
pixel.

```
Credits: 189
CPU usage: 77.621,979 cpu-seconds
Wall time: 5.499 seconds
Input Pixel: 31.494,448 mega-pixel
Max Executor Memory: 4,332 gb
Memory usage: 564.094.942,143 mb-seconds
Network Received: 872.636.866.126 b
```

The relative cost is 0.03 CDSE platform credits per km² for a 15 month input window.
The cost per input pixel is 0.006 credits per megapixel.

# Literature references

The max-ndvi compositing method has been applied to multiple sensors, as described in literature:

This publication describes characteristics of the method when applied to AVHRR data:
https://www.tandfonline.com/doi/abs/10.1080/01431168608948945

This publication applied it to Landsat data, for cropland estimation:
https://www.nature.com/articles/s43016-021-00429-z

# Known limitations

The method uses a vegetation index as scoring metric to determine the best pixel, making it only suitable for land applications.
Bare or urban areas may not be well represented in the composite.

It favours the observation which is least contaminated by atmospheric effects, but does not guarantee a fully uncontaminated composite.

For individual time windows of up to 3 months, the method was efficient up to 100x100km areas. For larger areas of interest, we recommend splitting the area into smaller tiles.


# Known artifacts

Artifacts are expected over water and urban areas.

![max_ndvi_water_artifacts.png](max_ndvi_water_artifacts.png)

Residual cloud artifacts may be present in the composite, especially for smaller time windows or during cloudy seasons.
The cloud artifacts are caused by the limited capabilities of the default Sentinel-2 cloud detection mechanism to correctly identify all clouds.

![max_ndvi_cloud_artifacts.png](max_ndvi_cloud_artifacts.png)
