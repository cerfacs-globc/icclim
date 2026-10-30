.. _station_workflows:

########################################
 Scale calculations over many stations
########################################

Station observations are often stored as independent time series.  Calling
icclim once for every station works, but it repeatedly pays the cost of input
preparation, unit handling, resampling and dask graph construction.  For a
large station archive, that fixed cost can dominate the index calculation.

Represent stations as a dimension
=================================

icclim and xarray can calculate every station in an array at the same time.
Build one dataset with ``station`` and ``time`` dimensions instead of looping
over individual station identifiers:

.. code:: python

   import icclim
   import pandas as pd

   observations = pd.read_parquet("daily_observations.parquet")
   observations["time"] = pd.to_datetime(observations["time"])

   # The remaining columns are climate variables such as tg, tn, tx and rr.
   ds = observations.set_index(["station", "time"]).to_xarray()

   # Insert omitted calendar dates as explicit missing observations.  A regular
   # daily coordinate lets icclim apply missing-data rules correctly.
   full_time = pd.date_range(
       start=ds.time.values[0],
       end=ds.time.values[-1],
       freq="D",
   )
   ds = ds.reindex(time=full_time)

Set the units and other CF metadata required by the selected indices on the
variables in ``ds``.  A variable that is unavailable for a station can remain
``NaN`` for that station.

Avoid this per-station pattern:

.. code:: python

   for station_id in ds.station.values:
       one_station = ds.sel(station=station_id)
       icclim.index(
           in_files=one_station,
           index_name="TG",
           slice_mode="year",
       )

Pass the station dimension to icclim instead:

.. code:: python

   result = icclim.index(
       in_files=ds,
       index_name="TG",
       slice_mode="year",
   )

The result retains the ``station`` dimension.  The speedup can be large because
the setup and resampling work is shared, but the exact improvement depends on
the index, record lengths, missing data, chunking and available memory.

Batch stations when the full archive does not fit in memory
===========================================================

Use batches of stations, not individual stations, when the complete dataset or
its intermediate results are too large.  Start with a conservative batch size
and increase it while monitoring peak memory use.  For example:

.. code:: python

   from pathlib import Path

   import icclim

   output_dir = Path("indices")
   output_dir.mkdir(exist_ok=True)

   index_names = ["TG", "TN", "TX", "DTR", "SU", "TR"]
   slice_modes = ["year", "month", "DJF", "MAM", "JJA", "SON"]
   station_batch_size = 250

   for start in range(0, ds.sizes["station"], station_batch_size):
       stop = min(start + station_batch_size, ds.sizes["station"])
       batch = ds.isel(station=slice(start, stop))

       for slice_mode in slice_modes:
           icclim.indices(
               index_group=index_names,
               in_files=batch,
               slice_mode=slice_mode,
               out_file=str(
                   output_dir / f"batch_{start}_{stop}_{slice_mode}.nc"
               ),
           )

``icclim.indices`` still evaluates the definition of every requested index, but
it collects compatible results in one dataset and writes one output file.  This
avoids managing a separate file and a separate top-level workflow for every
index.  Keep indices requiring different options in separate calls.  For
example, SPI indices may need station-specific calibration periods.

The best batch size is workload-specific.  Values between 100 and 500 stations
are useful starting points for long daily station records, but they are not
universal defaults.  Benchmark several sizes with representative data before
processing the full archive.  Independent batches can also be submitted as
separate jobs, provided that each job has enough memory for its dask workers.

Measure lazy calculations correctly
===================================

An icclim result may contain lazy dask arrays.  Timing the function call alone
can therefore measure graph construction without measuring the numerical
calculation.  Use ``load`` or ``compute`` before stopping the calculation timer:

.. code:: python

   from time import perf_counter

   graph_start = perf_counter()
   result = icclim.indices(
       index_group=index_names,
       in_files=batch,
       slice_mode="month",
   )
   graph_end = perf_counter()

   result.load()
   compute_end = perf_counter()

   result.to_netcdf("monthly_indices.nc")
   write_end = perf_counter()

   print("Graph construction:", graph_end - graph_start)
   print("Calculation:", compute_end - graph_end)
   print("NetCDF writing:", write_end - compute_end)

Run a small warm-up calculation before collecting timings, then repeat each
measurement and compare medians.  Use the same stations, periods, completeness
settings and output products when comparing icclim with another implementation.

For lower-level control of chunk sizes, worker counts and memory limits, see
:ref:`dask`.
