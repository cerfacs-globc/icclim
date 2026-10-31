.. _output_storage:

############################
Configure NetCDF output size
############################

icclim keeps its historical NetCDF output encoding by default. Compression and
data-variable chunk encoding are opt-in so existing workflows keep the same
write characteristics.

Set ``ICCLIM_OUTPUT_COMPRESSION_LEVEL`` to an integer from 1 to 9 to enable
zlib compression for data variables. Compression requires ``NETCDF4`` or
``NETCDF4_CLASSIC`` output. Level 4 is a common balance between output size and
write speed:

.. code-block:: console

   export ICCLIM_OUTPUT_COMPRESSION_LEVEL=4

Set ``ICCLIM_OUTPUT_CHUNKS`` to a JSON object to select stored chunk lengths by
dimension. Dimensions that are not listed retain the first Dask chunk length,
or their full length for eager output:

.. code-block:: console

   export ICCLIM_OUTPUT_CHUNKS='{"time": 12, "lat": 64, "lon": 64}'

These settings affect file storage only. They do not change calculated values.
Compression can reduce files substantially for repetitive or smoothly varying
fields, but it can make writing slower. Benchmark representative output before
enabling it in a production workflow.

For example, a local repeated-value 100 by 64 by 64 ``float32`` output was
1,648,416 bytes with default encoding and 26,016 bytes with compression level 4
and 20 by 16 by 16 stored chunks. Median write time over three runs increased
from 0.0167 to 0.0195 seconds. Real climate fields generally compress less, so
measure both size and write throughput on representative data.
