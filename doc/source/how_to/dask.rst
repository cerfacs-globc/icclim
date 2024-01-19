.. _dask:

########################################
 Chunk data and parallelize computation
########################################

*******
 TL;DR
*******

icclim make use of dask to chunk and parallelize computations. You can
configure dask to limit its memory footprint and CPU usage by
instantiating a distributed Cluster and by tuning dask.config options. A
configuration working well for small to medium dataset and simple
climate indices could be:

.. code:: python

   import dask
   from distributed import Client

   client = Client(memory_limit="10GB", n_workers=1, threads_per_worker=8)
   dask.config.set({"array.slicing.split_large_chunks": False})
   dask.config.set({"array.chunk-size": "100 MB"})
   icclim.index(in_files="data.nc", indice_name="SU", out_file="output.nc")

----

|  icclim uses xarray to manipulate data and xarray provides multiple
   backends to handle in-memory data.
|  By default, xarray uses numpy, this is overwritten in icclim to use
   dask whenever a path to a file is provided as input.
|  Numpy is fast and reliable for small dataset but may exhaust the
   memory on large dataset.
|  The other backend possibility of xarray is dask. dask can divide data
   into small chunk to minimize the memory footprint of computations.
   This chunking also enable parallel computation by running the
   calculation on each chunk concurrently.
|  This parallelization can speed up the computation but because each
   parallel thread will need multiple chunks to be in-memory at once, it
   can bring memory issues that chunking was meant to avoid.

|  In this document we first explain some concepts around dask,
   parallelization and performances, then we propose multiple dask
   configurations to be used with icclim.
|  You will also find a few dask pitfall dodging instructions which
   might help understanding why your computation doesn't run.
|  Each configuration aims to answer a specific scenario. For you own
   data, you will likely need to customize these configurations to your
   needs.

*********************
 The art of chunking
*********************

|  Dask proposes a way to divide large dataset into multiple smaller
   chunks that fit in memory.
|  This process is known as chunking and, with icclim there are 2 ways
   to control it.
|  First, you can open your dataset with xarray and do your own
   chunking:

.. code:: python

   import xarray
   import icclim

   ds = xarray.open_dataset("data.nc")
   ds = ds.chunk({"time": 10, "lat": 20, "lon": 20})

And then use ``ds`` dataset object as input for icclim.

.. code:: python

   icclim.index(in_files=ds, indice_name="SU", out_file="output.nc")

In that case, icclim will not re-chunk ``ds`` data. It is left to you to
find the proper chunking. For more information on how to properly chunk
see:

-  xarray guide:
   https://xarray.pydata.org/en/stable/user-guide/dask.html#chunking-and-performance
-  dask best practices:
   https://docs.dask.org/en/stable/array-best-practices.html

Another option is to leave dask find the best chunking for each
dimension. This is the recommended way and the default behavior of
icclim when using file a path in `in_files` parameter. In this case,
chunking can still be controlled by limiting the size of each individual
chunk:

.. code:: python

   import dask

   dask.config.set({"array.chunk-size": "50 MB"})
   icclim.su(in_files="data.nc")

By default, the dask chunk-size is around 100MB. You can also use
``with`` python keyword if you don't want this configuration to spread
globally. Internally, icclim will ask xarray and dask to chunk using
``"auto"`` configuration. This usually results in a pretty good
chunking. It chunks by respecting as much as possible how the data is
stored and will make chunks as large as approximately the configured
chunk-size. Moreover, some operations in icclim/xclim need to re-chunk
intermediary results. We usually try to keep the chunk sizes to their
initial value but re-chunking is costly and we sometimes prefer to
generate larger chunks to try improving performances. If you wish to
avoid this large chunking behavior, you can try the following dask
configuration:

.. code:: python

   dask.config.set({"array.slicing.split_large_chunks": True})

Create an optimized chunking on disk
====================================

Sometimes, you have to work with data that were originally chunked and
stored in a way that is suboptimal. Often climate data are stored in a
one year per file format thus the natural chunking of the dataset will
be one year per chunk. The most efficient way to read data on disk would
be to chunk data in memory the same way it is distributed on disk. Here
it means having one chunk per file, as long as a file size does not
exceed the `array.chunk-size` configuration.

This scattering of the time axis in many chunks can limit the
computation performances of some indices. Indeed, indices such as
percentile based indices require a specific chunking schema to be
computed. This means we must either rechunk in memory to have an
optimized chunking. However, this generates many dask tasks and can
overload dask scheduler.

To tackle this issue, icclim 5.1.0 comes with a new feature to first
rewrite the data on disk before starting any computation. We rely on the
`rechunker library
<https://rechunker.readthedocs.io/en/latest/index.html>`_ to make this
possible. The feature is ``icclim.create_optimized_zarr_store``. It is a
context manager which allow you to rewrite an input data into a zarr
store. Zarr stores are a modern way to store files on disk with
optimized reading and writing in mind. In our case, it allows to
rewrite files with a specific chunking schema, optimized for climate
indices computation.

Now, depending on the climate index you want to compute, the optimal
chunking schema might differ.

For most indices, if you consider chunking on time dimension, you should
never chunk below the target resampling period. For example, with
``slice_mode="month"``, ideally each chunk should include whole month
and never chunk in the middle of a month. But month being of variable
lengths, it might actually be much easier to have one chunk per year.
Leap years would add another difficulty to this.

However, on indices where a bootstrapping of percentile is necessary (e.g
Tg90p), it is actually optimal to have no chunk at all on time
dimension. This is true only because the bootstrapping algorithm rely on
`map_block
<https://xarray.pydata.org/en/stable/generated/xarray.map_blocks.html>`_.
In that case, you can use ``icclim.create_optimized_zarr_store`` to
first create a zarr store not chunked at all on time dimension:

.. code:: python

   import icclim

   ref_period = [datetime.datetime(1980, 1, 1), datetime.datetime(2009, 12, 31)]
   with icclim.create_optimized_zarr_store(
       in_files="netcdf_files/tas.nc",
       var_names="tas",
       target_zarr_store_name="opti.zarr",
       keep_target_store=False,
       chunking={"time": -1, "lat": "auto", "lon": "auto"},
   ) as opti_tas:
       icclim.index(
           index_name="TG90p",
           in_files=opti_tas,
           slice_mode="YS",
           base_period_time_range=ref_period,
           out_file="netcdf_files/output/tg90p.nc",
       )

Actually `chunking={"time": -1, "lat":"auto", "lon":"auto" }`,
which avoid chunking on time, is the default behavior of the function.
`chunking` parameter could thus be omitted in the above example.

You can also control if you want to keep the optimized zarr store on
disk by turning ``keep_target_store`` to True. This can be useful if you
wish to compute other indices using the same chunking.

*****************
 On performances
*****************

Computation of ECA&D indices can largely be done in parallel on spatial
dimensions. Indeed, the ECA&D indices available in icclim are all
computed on each individual pixel independently. In a ideal world it
means we could compute each pixel concurrently. In reality this would
result in considerable efforts necessary to chunk data that much, this
would be sub-optimal because the smaller chunk are, the greater dask
overhead is.

.. note::

   By overhead, we mean here the necessary python code running to move
   around and handle each independent chunk.

|  Another important aspect of dask to consider for performances is the
   generated task graph.
|  Dask creates a graph of all the actions (tasks) it must accomplish to
   compute the calculation.
|  This graph, created before the computation, shows for each chunk the
   route to follow in order to compute the climate index.
|  This allows some nice optimizations, for example if some spatial or
   time selections are done within icclim/xclim, it will only read and
   load in-memory the necessary data.
|  However, each task also adds some overhead and, most of the time a
   small graph will compute faster than a larger.

|  In this graph each chunk has it's own route of all the intermediary
   transformation it goes though. The more there are chunks the more
   routes are created.
|  In extreme cases, when there are a lot of chunks, the graph may take
   eons to create and the computation may never start.
|  This means that configuring a small chunk size leads to a potentially
   large graph.

|  The graph is also dependant of the actual calculation. A climate
   index like "SU" (count of days above 25°C) will obviously create a
   much simpler graph than WSDI (longest spell of at least 6 consecutive
   days where maximum daily
|  temperature is above the 90th daily percentile).
|  Finally the resampling may also play a role in the graph complexity.
   In icclim we control it with ``slice_mode`` parameter.
|  A yearly slice_mode sampling result in a simpler graph than a monthly
   sampling.

|  Beside, when starting dask on a limited system (e.g a laptop) it's
   quite easy to exhaust all available memory.
|  In that case, dask has multiple safety mechanism and can even kill
   the computing process (a.k.a the worker) once it reaches a memory
   limit (default is 95% of memory).
|  Even before this limit, the performances can deteriorate when dask
   measures a high memory use of a worker.
|  When a worker uses around 60% of its memory, dask will ask it to
   write to disk the intermediary results it has computed.
|  These i/o operations are much slower than in RAM manipulation, even
   on recent SSD disk.

Hence, there are multiple things to consider to maximize performances.

|  First, if your data (and the intermediary computation) fits in
   memory, it might be better to use Numpy backend directly.
|  To do so, simply provide the opened dataset to icclim:

.. code:: python

   ds = xarray.open_dataset("data.nc")
   icclim.index(in_files=ds, indice_name="SU", out_file="output.nc")

There will be no parallelization but, on small dataset it's unnecessary.
Numpy is natively really fast and dask overhead may slow it downs.

On the other hand when using dask we must:

-  Minimize the number of task to speed things up, thus divide data into
   **large enough chunks**.
-  Minimize the workload of each worker to avoid i/o operation, thus
   divide data into **small enough chunks**.

In the following we present a few possible configuration for dask.

*******************************************************
 Small to medium dataset (a few MB) - No configuration
*******************************************************

The first approach is to use default values. By default icclim relies on
dask's ``"auto"`` chunking and dask will be started with the threading
scheduler. This scheduler runs everything in the existing python process
and will spawn multiple threads to concurrently compute climate indices.
You can find more information on the default scheduler here:
https://docs.dask.org/en/stable/scheduling.html#local-threads

|  This can work on most cases for small to medium datasets and may
   yield the best performances.
|  However some percentiles based temperature indices (T_90p and T_10p
   families) may use a lot of memory even on medium datasets.
|  This memory footprint is caused by the bootstrapping of percentiles,
   an algorithm used to correct statistical biases.
|  This bootstrapping use a Monte Carlo simulation, which inherently use
   a lot of resources.
|  The longer the bootstrap period is, the more resources are necessary.
   The bootstrap period is the overlapping years between the period
   where percentile are computed (a.k.a "in base") and the period where
   the climate index is computed (a.k.a "out of base").

.. note::

   -  To control the "in base" period, ``icclim.index`` provides the
      ``base_period_time_range`` parameter.
   -  To control the "out of base" period, ``icclim.index`` provides the
      ``time_range`` parameter.

For these percentile based indices, we recommend to use one of the
following configuration.

******************************************************
 Medium to large dataset (~200MB) - dask LocalCluster
******************************************************

By default, dask will run on a default threaded scheduler. This behavior
can be overwritten by creating you own "cluster" running locally on your
machine. This LocalCluster is distributed in a separate dask package
called "distributed" and is not a mandatory dependency of icclim.

To install it run:

.. code:: console

   $ conda install dask distributed -c conda-forge

See the documentation for more details:
http://distributed.dask.org/en/stable/

Once installed, you can delegate the ``LocalCluster`` instantiation
to the `distributed.Client` class. This ``Client`` object creates both a
``LocalCluster`` and a web application to investigate how your
computation is going. This web dashboard is very powerful and helps to
understand where are the computation bottlenecks as well as to visualize
how dask is working. By default it runs on ``localhost:8787``, you can
print the client object to see on which port it runs.

.. code:: python

   from distributed import Client

   client = Client()
   print(client)

By default dask creates a ``LocalCluster`` with 1 worker (process), CPU
count threads and a memory limit up to the system available memory.

.. note::

   -  You can see how dask counts CPU here:
      https://github.com/dask/dask/blob/main/dask/system.py
   -  How dask measures available memory here:
      https://github.com/dask/distributed/blob/main/distributed/worker.py#L4237
   -  Depending on your OS, these values are not exactly computed the
      same way.

The cluster can be configured directly through Client arguments.

.. code:: python

   client = Client(memory_limit="16GB", n_workers=1, threads_per_worker=8)

A few notes:

-  The CLient must be started in the same python interpreter as the
   computation. This is how dask know which scheduler to use.

-  If needed, the localCluster can be started independently and the
   Client connected to a running LocalCluster. See:
   http://distributed.dask.org/en/stable/client.html

-  Each worker is an independent python process and memory_limit is set
   for each of these processes. So, if you have 16GB of RAM don't set
   ``memory_limit='16GB'`` unless you run a single worker.

-  Memory sharing is much more efficient between threads than between
   processes (workers), see `dask doc
   <http://distributed.dask.org/en/stable/worker.html#thread-pool>`_

-  On a single worker, a good threads number should be a multiple of
   your CPU cores (usually \*2).

-  All threads of the same worker are idle whenever one of the thread is
   reading or writing on disk.

-  It's useless to spawn too many threads, there are hardware limits on
   how many of them can run concurrently and if they are too numerous,
   the OS will waste time orchestrating them.

-  A dask worker may write to disk some of its data even if the memory
   limit is not reached. This seems to be a normal behavior happening
   when dask knows some intermediary results will not be used soon.
   However, this can significantly slow down the computation due to i/o.

-  Percentiles based indices may need up to **nb_thread \* chunk_size \*
   30** memory which is unusually high for a dask application. We are
   trying to reduce this memory footprint but it means some costly
   re-chunking in the middle of computation have to be made.

Knowing all these, we can consider a few scenarios.

Low memory footprint
====================

Let's suppose you want to compute indices on your laptop while continue
to work on other subjects. You should configure your local cluster to
use not too many threads and processes and to limit the amount of memory
each process (worker) has available. On my 4 cores, 16GB of RAM laptop I
would consider:

.. code:: python

   client = Client(memory_limit="10GB", n_workers=1, threads_per_worker=4)

Eventually, to reduce the amount of i/o on disk we can also increase
dask memory thresholds:

.. code:: python

   dask.config.set({"distributed.worker.memory.target": "0.8"})
   dask.config.set({"distributed.worker.memory.spill": "0.9"})
   dask.config.set({"distributed.worker.memory.pause": "0.95"})
   dask.config.set({"distributed.worker.memory.terminate": "0.98"})

These thresholds are fractions of memory_limit used by dask to take a
decision.

-  At 80% of memory the worker will write to disk its unmanaged memory.
-  At 90%, the worker will write all its memory to disk.
-  At 95%, the worker pause computation to focus on writing to disk.
-  At 98%, the worker is killed to avoid reaching memory limit.

Increasing these thresholds is risky. The memory could be filled quicker
than expected resulting in a killed worker and thus loosing all work
done by this worker. If a single worker is running and it is killed, the
whole computation will be restarted (and will likely reach the same
memory limit).

High resources use
==================

If you want to have the result as quickly as possible it's a good idea
to give dask all possible resources. This may render your computer
"laggy" thought. On my 4 cores (8 CPU threads), 16GB of RAM laptop I
would consider:

.. code:: python

   client = Client(memory_limit="16GB", n_workers=1, threads_per_worker=8)

On this kind of configuration, it can be useful to add 1 or 2 workers in
case a lot of i/o is necessary. If there are multiple workers
``memory_limit`` should be reduced accordingly. It can also be necessary
to reduce chunk size. dask default value is around 100 MB per chunk
which on some complex indices may result in a large memory usage.

It's over 9000!
===============

This configuration may put your computer to its knees, use it at your
own risk. The idea is to bypass all memory safety implemented by dask.
This may yield very good performances because there will be no i/o on
disk by dask itself. However, when your OS run out of RAM, it will use
your disk swap which is sort of similar to dask spilling mechanism but
probably much slower. And if you run out of swap, your computer will
likely crash. To roll the dices use the following configuration
``memory_limit='0'`` in :

.. code:: python

   client = Client(memory_limit="0")

Dask will spawn a worker with multiple threads without any memory
limits.

***************************************
 Large to huge dataset (1GB and above)
***************************************

If you wish to compute climate indices of a large datasets, a personal
computer may not be appropriate. In that case you can deploy a real dask
cluster as opposed to the LocalCluster seen before. You can find more
information on how to deploy dask cluster here:
https://docs.dask.org/en/stable/scheduling.html#dask-distributed-cluster

However, if you must run your computation on limited resources, you can
try to:

-  Use only one or two threads on a single worker. This will drastically
   slow down the computation but very few chunks will be in memory at
   once letting you use quite large chunks.

-  Use small chunk size, but beware the smaller they are, the more dask
   creates tasks thus, the more complex the dask graph becomes.

-  Rechunk your dataset into a zarr storage to optimize file reading and
   reduce the amount of rechunking tasks needed by dask. For this, you
   should consider the Pangeo rechunker library to ease this process:
   https://rechunker.readthedocs.io/en/latest/ A shorthand to Pangeo
   rechunker is available in icclim with
   `icclim.create_optimized_zarr_store`.

-  Split your data into smaller netcdf inputs and run the computation
   multiple times.

The last point is the most frustrating option because chunking is
supposed to do exactly that. But, sometimes it can be easier to chunk
"by hand" than to find the exact configuration that fit for the input
dataset.

**************
 Real example
**************

On CMIP6 data, when computing the percentile based indices Tx90p for 20
years and, bootstrapping on 19 years we use:

.. code:: python

   client = Client(memory_limit="16GB", n_workers=1, threads_per_worker=2)
   dask.config.set({"array.slicing.split_large_chunks": False})
   dask.config.set({"array.chunk-size": "100 MB"})
   dask.config.set({"distributed.worker.memory.target": "0.8"})
   dask.config.set({"distributed.worker.memory.spill": "0.9"})
   dask.config.set({"distributed.worker.memory.pause": "0.95"})
   dask.config.set({"distributed.worker.memory.terminate": "0.98"})

****************************************
 Troubleshooting and dashboard analysis
****************************************

This section describe common warnings and errors that dask can raise.
There are also some silent issues that only dask dashboard can expose.
To start the dashboard, run the distributed ``Client(...)``. It should
be available on ``localhost:8787`` as a web application (type
"localhost:8787" in your browser address bar to access it).

Memory overload
===============

The warning may be ``"distributed.nanny - WARNING - Restarting worker"``
or the error ``"KilledWorker"``. This means the computation uses more
memory than what is available for the worker. Keep in mind that:

-  ``memory_limit`` parameter is a limit set for each individual worker.

-  Some indices, such as percentile based indices (R__p, R__pTOT, T_90p,
   T_10p families) may use large amount of memory. This is especially
   true on temperature based indices where percentiles are bootstrapped.

-  You can reduce memory footprint by using smaller chunks.

-  Each thread may load multiple chunks in memory at once.

|  To solve this issue, you must either increase available memory per
   worker or reduce the quantity of memory used by the computation.
|  You can increase memory_limit up to your physical memory available
   (RAM) with ``Client(memory_limit="16GB")``.
|  This increase can also speed up computation by reducing writes and
   reads on disk.
|  You can reduce the number of concurrently running threads (and
   workers) in the distributed Client configuration with
|  ``Client(n_workers=1, threads_per_worker=1)``. This may slow down
   computation.
|  You can reduce the size of each chunk with
   ``dask.config.set({"array.chunk-size": "50 MB"})``, default is around
   100MB.
|  This may slow down computation as well.
|  Or you can combine the three solutions above.
|  You can read more on this issue here:
   http://distributed.dask.org/en/stable/killed.html

Garbage collection "wasting" CPU time
=====================================

|  The warning would be: ``distributed.utils_perf - WARNING - full
   garbage collections took xx% CPU time recently (threshold: 10%)``
|  This is usually accompanied by: ``distributed.worker - WARNING -
   gc.collect() took 1.259s. This is usually a sign that some tasks
   handle too many Python objects at the same time. Rechunking the work
   into smaller tasks might help.``
|  Python runs on a virtual machine (VM) which handles the memory
   allocations for us.
|  This means the VM sometimes needs to cleanup garbage objects that
   aren't referenced anymore.
|  This operation takes some CPU resource but free the RAM for other
   uses.
|  In our dask context, the warning may be raised when icclim/xclim has
   created large chunks which takes longer to be garbage collected.
|  This warning means some CPU is wasted but the computation is still
   running. It might help to re-chunk into smaller chunk.

Internal re-chunking
====================

|  The warning would be: ``PerformanceWarning: Increasing number of
   chunks by factor of xx``.
|  This warning is usually raised when computing percentiles.
|  In percentiles calculation step, the intermediary data generated to
   compute percentiles is much larger than the initial data.
|  First, because of the rolling window used to retrieve all values of
   each day, the analysed data is multiplied by window size (usually by
   5).
|  Then, on temperatures indices such as Tx90p, we compute percentiles
   for each day of year (doy).
|  This means we must read almost all chunks of time dimension.
|  To avoid consuming all RAM at once with these, icclim/xclim
   internally re-chunk data that's why dask warns that many chunks are
   being created.
|  In that case this warning can be ignored.

Computation never starts
========================

|  The error raised can be ``CancelledError``.
|  We can also acknowledge this by looking at dask dashboard and not
   seeing any task being schedule.
|  This usually means dask graph is too big and the scheduler has
   trouble creating it.
|  If your memory allows it, you can try to increase the chunk-size with
   ``dask.config.set({"array.chunk-size": "200 MB"})``.
|  This will reduce the amount of task created on dask graph.
|  To compensate, you may need to reduce the number of running threads
   with ``Client(n_workers=1, threads_per_worker=2)``.
|  This should help limit the memory footprint of the computation.

.. note::

   Beware, if the computation is fast or if the client is not started in
   the same python process as icclim, the dashboard may also look empty
   but the computation is actually running.

Disk read and write analysis - Dashboard
========================================

|  When poorly configured, the computation can spend most of its CPU
   time reading and writing chunks on disk.
|  You can visualize this case by opening dask dashboard, usually on
   ``localhost:8787``.
|  In the status page, you can see in the right panel each task
   dynamically being added.
|  In these the colourful boxes, each color represent a specific task.
|  I/O on disk is displayed as orange transparent boxes. You should also
   see all other threads of the same worker stopping when one thread is
   reading or writing on disk.
|  If there is a lot of i/o you may need to reconfigure dask.
|  The solution to this are similar to the memory overload described
   above:

   -  You can increase total available memory with
      ``Client(memory_limit="16GB")``.

   -  You can decrease memory pressure by reducing chunk size with
      ``dask.config.set({"array.chunk-size": "50 MB"})`` or by reducing
      number of threads with ``Client(n_workers=1,
      threads_per_worker=2)``.

|  Beside, you can also benefit from using multiple worker in this case.
|  Each worker is a separate non blocking process thus they are not
   locking each other when one of them need to write or read on disk.
   They are however slower than threads to share memory, this can result
   in the "chatterbox" issue presented below.

.. note::

   -  Don't instantiate multiple client with different configurations,
      put everything in the same Client constructor call.
   -  Beware, as of icclim 5.0.0, the bootstrapping of percentiles is
      known to produce **a lot** of i/o.

Worker chatterbox syndrome - Dashboard
======================================

|  In all this document, we mainly recommend to use a single worker with
   multiple threads.
|  Most of the code icclim runs is relying on dask and numpy, and both
   release the python GLI (More details on GIL here:
   https://realpython.com/python-gil/).
|  This means we can benefit from multi threading and that's why we
   usually recommend to use a single process (worker) with multiple
   threads.
|  However, some configuration can benefit from spawning multiple
   processes (workers).
|  In dask dashboard, you will see red transparent boxes representing
   the workers communicating between each other.
|  If you see a lot of these and if they do not overlap much with other
   tasks, it means the workers are spending most of their CPU times
   exchanging data.
|  This can be caused by either:

   -  Too many workers are spawned for the amount of work.
   -  The load balancer has a lot of work to do.

|  In the first case, the solution is simply to reduce the number of
   workers and eventually to increase the number of threads per worker.
|  For the second case, when a worker has been given too many task to
   do, the load balancer is charged of redistributing these task to
   other worker. It can happen when some task take significant time to
   be processed.
|  In icclim/xclim this is for example the case of the ``cal_perc``
   function used to compute percentiles.
|  There is no easy solution for this case, letting the load balancer do
   its job seems necessary.

Idle threads
============

|  When looking at dask dashboard, the task timelines should be full of
   colors.
|  If you see a lot of emptiness between colored boxes, it means the
   threads are not doing anything.
|  It could be caused by a blocking operation in progress (e.g i/o on
   disk). Read `Disk read and write analysis - Dashboard`_ above in that
   case.
|  It could also be because you have set too many threads and the work
   cannot be properly divided between each thread.
|  In that case, you can simply reduce the number of thread in Client
   configuration with ``Client(n_workers=1, threads_per_worker=4)``.

************
 Conclusion
************

|  We can't provide a single configuration which fits all possible
   datasets and climate indices.
|  In this document we tried to summarize the few configurations we
   found useful while developing icclim.
|  You still need to tailor these configurations to your own needs.

.. note::

   -  This document has been rewritten in january 2022 and the whole
      stack under icclim is evolving rapidly.
   -  Some information presented here might become outdated quickly.
