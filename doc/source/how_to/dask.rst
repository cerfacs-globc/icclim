Larger than memory computation
==============================

TL;DR
-----
icclim make use of dask to chunk and parallelize computations.
You can configure dask to limit the memory footprint of these calculus by instantiating a distributed Client
and by tuning dask.config options.
A configuration working well for small to medium dataset and simple climate indices is :

>>>import dask
>>>from distributed import Client
>>>client = Client(memory_limit='10GB', n_workers=1, threads_per_worker=8)
>>>dask.config.set({"array.slicing.split_large_chunks": False})
>>>dask.config.set({"array.chunk-size": "50 MB"})
>>>icclim.index(in_files="data.nc", indice_name='SU', out_file="output.nc")

------------------------------------------------------------------------------------------------

icclim uses xarray to manipulate data and xarray provides multiple backends to handle in-memory data.
By default, xarray uses numpy, this is overwritten in icclim to use dask whenever a path to a file is provided as input.
Numpy is fast and reliable for small dataset but may exhaust the memory on large dataset.
The other backend possibility is dask. dask can divide data into small chunk to minimize the memory footprint of the
computation. This chunking also enable parallel computation. This parallelization can speed up the computation but
because each parallel thread need multiple chunks to be in-memory at once, it can bring back memory issues.

In this document we first explain some concepts around dask, parallelization and performances, then we propose multiple
dask configurations to be used with icclim.
Each configuration aims to answer a specific scenario. For you own data, you will likely need to customize these
configuration to your needs.

The art of chunking
-------------------
Dask proposes a way to divide large dataset into multiple smaller chunks that fit in memory.
This process is known as chunking and with icclim there are 2 ways to control it.
First, you can open your dataset with xarray and do your own chunking:

>>>import xarray
>>>import icclim
>>>ds = xarray.open_dataset("data.nc")
>>>ds = ds.chunk({"time": 10, "lat": 20, "lon": 20})

And then use this `ds` dataset as input for icclim.

>>>icclim.index(in_files=ds, indice_name='SU', out_file="output.nc")

In that case, icclim will not rechunk your data, it is left to you to find the proper chunking.
For more information on how to properly chunk see:
- xarray guide //TODO
- xarray tips //TODO
- dask guide //TODO
Another option is to leave icclim and dask find the best chunking for each dimension.
This is the recommended way, the chunking behavior can be controlled by limiting the size of each individual chunk.

>>>import dask
>>>dask.config.set({"array.chunk-size": "50 MB"})
>>>icclim.index(in_files="data.nc", ...)

By default, the dask chunk-size is around 100MB.
You can also use ``with`` python keyword if you don't want this configuration to spread globally.
Internally, icclim will ask xarray and dask to chunk using ``"auto"`` configuration.
This usually results in a pretty good chunking. It chunks by respecting as much as possible how the data
is stored and will make chunks as large as approximately the configured chunk-size.
Moreover, some operations in icclim/xclim need to re-chunk intermediary results. We usually try to keep the chunk sizes
to their initial value but re-chunking is costly and we sometimes prefer to generate larger chunks to improve performances.
If you wish to avoid this large chunking behavior, you can use the following dask configuration:

>>>dask.config.set({"array.slicing.split_large_chunks": True})

On performances
---------------
Computation of ECA&D indices can largely be done in parallel on spatial dimensions.
Indeed, each of these indices are relying on a time series for each pixel. Thus, in a ideal world we could compute
each pixel independently but, this would usually result in a lot of chunks.
This is not optimal because the smaller each chunk is, the greater the overhead is.
By overhead, we mean here the necessary python code running to move around and handle each independent chunk.
Plus, unless running on a cloud or HPC, we are limited by the number of threads (or processes) available.
Another important aspect of dask to consider for performances is the task graph. Dask creates a graph of all the actions
(tasks) it must accomplish to compute the calculation. This graph created before the computation, shows for each chunk
the route to follow in order to compute the climat index.
This allow some nice optimizations, for example if some spatial or time selection is done, it will only read and load in
memory the selected data.
However, each task also add some overhead and, a small graph with a few tasks will likely compute faster.
Plus, each chunk has it's own route in the graph, and the more there are chunks the more routes are created.
In extreme cases, when there are a lot of chunks, the graph may take eons to create and the computation may never start.
This means that creating small chunks leads to numerous chunks and thus to a potentially large graph.

Beside, when starting dask on a limited system (e.g a laptop) it's quite easy to exhaust all available memory.
In that case, dask has multiple safety mechanism and can even kill the computing process (a.k.a the worker) once it
reaches a memory limit (default to 95% of memory).
Even before this limit, the performances can deteriorate when dask measures a high memory use of a worker.
When a worker use around 60% of it's memory, dask will ask it to write to disk the intermediary results it has computed.
These i/o operation are much slower than in RAM manipulation, even on a recent SSD disk.


Hence, there are multiple things to consider to maximize performances:
First, if your data (and the intermediary computation) fits in memory, it might be better to use Numpy backend directly.
To do so, simply provide the opened dataset to icclim:

>>>ds = xarray.open_dataset("data.nc")
>>>icclim.index(in_files=ds, indice_name='SU', out_file="output.nc")

There will be no parallelization but, on small dataset it's unnecessary, numpy is really fast.

On the other hand when using dask we must:
- Minimize the number of task to speed things up, thus divide data into large enough chunks.
- Minimize the workload of each worker to avoid i/o operation, thus divide data into small enough chunks.
In the following we present a few possible configuration for dask.


Small to medium dataset (a few MB) - No configuration
-----------------------------------------------------

The first approach is to use default values.
By default icclim rely on "auto" chunking of dask.
Dask will be started with the threading scheduler which, in the same python process will spawn multiple thread
to concurrently compute the indices.
// TODO: add link to default scheduler doc
This can work on most cases for small to medium datasets and may yield the best performances.
However some percentiles based indices (T_90p and T_10p families) may use a lot of memory even on medium
indices. This memory footprint is caused by the bootstrapping of percentiles, an algorithm used to correct
statistical biais. This algorithm rely on a Monte Carlo simulation which inherently use a lot of ressources.
The longer the bootstrap period is, the more ressources are used. The bootstrap period is the overlapping years
between the period where percentile are computed (a.k.a "in base") and the period where the climate index is computed
(a.k.a "out of base").

.. Notes::

    To control the "in base" period, ``icclim.index`` provides the ``base_period_time_range`` parameter.
    To control the "out of base", ``icclim.index`` provides the ``time_range`` parameter.

For these percentile based indices, we recommend to use one of the following configuration.

Medium to large dataset (~200MB) - dask LocalCluster
----------------------------------------------------

By default, dask will run on a default threaded scheduler.
This behavior can be overwritten by creating you own "cluster" running locally on your machine.
This LocalCluster is distributed in a separate dask package called "distributed" and is not a mandatory
dependency of icclim.
To install it run:

>>> conda install dask distributed -c conda-forge

See the documentation for more details: http://distributed.dask.org/en/stable/
Once installed, you can delegate the LocalCluster instantiation using `distributed.Client` class.
This class both create a cluster and run a web application to investigate how your computation is going.
This web dashboard is very useful to understand what is going right or wrong.
By default it runs on ``localhost:8787``, you can print the client object to see on which port it runs.

>>> from distributed import Client
>>> client = Client()
By default dask // TODO fill defaults values for Client

The cluster can be configured directly through Client arguments.

>>> client = Client(memory_limit='16GB', n_workers=1, threads_per_worker=8)

A few notes:
- The CLient must be started in the same python interpreter as the computation. This is how dask know to use
the cluster instead of the default scheduler.
- If needed, the localCluster can be started independently and the Client connected to a running LocalCluster.
See dask documentation for how to: // TODO add link
- Each worker is an independent python process and memory_limit is set for each of these process.
If you have 16GB of RAM don't set ``memory_limit='16GB'`` unless you run a single worker.
- Memory sharing is much more efficient between threads than between processes.
- Threads number is usually optimal when it's a multiple of your CPU cores (usually *2).
- All threads of the same worker are waiting whenever one of the thread is reading or writing on disk.
- It's useless to spawn too many threads, there are hardware limits on how many of them can run concurrently
and if they are numerous, the OS will waste time orchestrating them.
- A dask worker may write to disk some of their data even if it is far form reaching the memory limit.
This seems to be a normal behavior when dask knows some intermediary results will not be used soon.
This can significantly slow down the computation due to i/o.
- Percentiles based indices may use up to ``nb_thread * chunk_size * 30`` memory which is unusually high for a
dask application. We are trying to reduce this memory footprint but it means some costly rechunking in the middle of
computation have to be made.

Knowing these we can consider multiple scenarios.

Low memory footprint
~~~~~~~~~~~~~~~~~~~~

Let's suppose you want to compute indices on your laptop while continue to work on other subjects.
You should configure your local cluster to use not too many threads and processes and to limit the amount of memory
each process (worker) has.
On my 4 cores, 16GB of RAM laptop I would consider:

>>> client = Client(memory_limit='10GB', n_workers=1, threads_per_worker=4)

Eventually, to reduce the amount of i/o we can also increase dask memory thresholds:

>>> dask.config.set({"distributed.worker.memory.target": "0.8"})
>>> dask.config.set({"distributed.worker.memory.spill": "0.9"})
>>> dask.config.set({"distributed.worker.memory.pause": "0.95"})
>>> dask.config.set({"distributed.worker.memory.terminate": "0.98"})

These thresholds are fractions of memory_limit used by dask to take a decision.
Here, at 80% of memory the worker will write to disk its unmanaged memory.
At 90%, the worker will write all its memory to disk.
At 95%, the worker pause computation to focus on writing.
At 98%, the worker is killed to avoid reaching memory limit.
Increasing these threshold has a risk, because they could be filled quicker than expected resulting in a killed worker
and thus loosing all work done by this worker.
If a single worker is running, the whole computation will be restarted (and will likely reach the same memory limit).

High ressource use
~~~~~~~~~~~~~~~~~~
If you want to have the result as quickly as possible without risking
On my 4 cores, 16GB of RAM laptop I would consider:

>>>client = Client(memory_limit='16GB', n_workers=1, threads_per_worker=8)

On this kind of configuration, it can be useful to add 1 or 2 workers in case a lot of i/o is necessary.
It can also be necessary to reduce chunk size, dask default value is around 100 MB which on some indices
may fill all the memory.

It's over 9000!
~~~~~~~~~~~~~~~

This configuration may put your computer to its knees, use it at your own risk.
The idea is to bypass all memory safety implemented by dask.
This may yield very good performances because there will be no i/o on disk by dask itself.
However, when your OS run out of RAM, it will use your disk swap which is very similar to dask spilling mechanism but probably slower.
And if you run out of swap, your computer will likely crash.
To roll the dices use the following configuration
>>>client = Client(memory_limit='0')
Dask will spawn multiple processes without memory limits and each process will spawn multiple threads.

Large to huge dataset (1GB and above)
------------------------------------

If you which to compute climate indices on a large dataset a personal computer is probably be inappropriate.
In that case you can deploy a "real" dask cluster opposed to the LocalCluster.
You can find more information on how to deploy dask cluster here: //TODO add link to cloud dask

If you must run your computation on limited ressources, you can try to:
- Use only one or two threads on a single worker
This will drastically slow down the computation but very few chunks will be in memory at once letting you use quite large chunks.
- Use small chunk size, but beware the smaller they are the more complex dask graph become.
- Split you data into smaller netcdf inputs and run the computation multiple time.
This is the most frustrating option because chunking is supposed to do exactly that. But, sometimes
it can be easier to chunk "by hand" than to find the exact configuration that fit for the input dataset.

Real example
------------

On CMIP6 data, when computing the percentile based indices Tx90p for 20 years, bootstrapped on 19 years we used:
>>>client = Client(memory_limit='16GB', n_workers=1, threads_per_worker=2)
>>>dask.config.set({"array.slicing.split_large_chunks": False})
>>>dask.config.set({"array.chunk-size": "100 MB"})
>>>dask.config.set({"distributed.worker.memory.target": "0.8"})
>>>dask.config.set({"distributed.worker.memory.spill": "0.9"})
>>>dask.config.set({"distributed.worker.memory.pause": "0.95"})
>>>dask.config.set({"distributed.worker.memory.terminate": "0.98"})


Troubleshooting and dashboard analysis
--------------------------------------

This section describe common warnings and errors that dask can raise.
There are also some silent issues that dask dashboard can expose.
A dashboard is started when running the distributed ``Client(...)``.


Memory overload
~~~~~~~~~~~~~~~
The warning may be "distributed.nanny - WARNING - Restarting worker" or the error "KilledWorker".
This means the computation uses more memory than what is available.
Keep in mind that:
- memory_limit parameter is the limit of each individual workers
- Some indices, such as percentile based indices (R__p, T_90p, T_10p families) may use large amount of memory.
- You can reduce memory footprint by using smaller chunk
- Each thread may load multiple chunks in memory at once.
To solve this issue, you must either provide additional available memory or reduce the quantity of memory used.
You can increase memory_limit up to your physical memory available (RAM) with ``Client(memory_limit="16GB")``,
this may speed up computation by reducing writes and reads on disk.
You can reduce the number of concurrently running threads (and workers) in the distributed Client configuration with
``Client(n_workers=1, threads_per_worker=1)``. This may slow down computation.
You can reduce the size of each chunk with ``dask.config.set({"array.chunk-size": "50 MB"})``, default is around 100MB.
This may slow down computation as well.
Or you can combine all three solutions above.


Garbage collection "wasting" CPU time
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The warning would be: ``distributed.utils_perf - WARNING - full garbage collections took xx% CPU time recently (threshold: 10%)``
This is usually accompanied by: ``distributed.worker - WARNING - gc.collect() took 1.259s. This is usually a sign that some tasks handle too many Python objects at the same time. Rechunking the work into smaller tasks might help.``
Python runs on a virtual machine (VM) which handles the memory allocation of objects for us.
This means the VM sometimes needs to cleanup garbage objects that aren't referenced anymore.
This operation takes some CPU ressource but free the RAM for other uses.
In our dask context, the warning may be raised when icclim/xclim has created large chunks which takes longer to be garbage collected.

Internal re-chunking
~~~~~~~~~~~~~~~~~~~~
The warning would be: ``PerformanceWarning: Increasing number of chunks by factor of xx``.
This warning is usually raised when computing percentiles.
In this step, the input in base data used to compute the percentile grow significantly.
First, because of the rolling window the input data size is multiplied by window size.
Then, on temperatures indices such as Tx90p, we compute values for each day of year(doy).
This means we need for each to read all years of in_base thus usually all chunks of time dimension.
To avoid consuming all RAM at once we rechunk the doy values to the initial chunking size but
dask warns us that it creates quite a few new chunks.
This warning should not be a serious issue and can be ignored.

Computation never start
~~~~~~~~~~~~~~~~~~~~~~~
The error raised can be ``CancelledError``.
We can also acknowledge this by looking at dask dashboard and not seeing any task being schedule.
This usually means dask graph is too big and the scheduler has trouble creating it.
If your memory allows it, you can try to increase the chunk-size with ``dask.config.set({"array.chunk-size": "200 MB"})``.
This will reduce the amount of task created by dask thus reducing graph size.
To compensate, you may need to reduce the number of running threads with ``Client(n_workers=1, threads_per_worker=2)``.
This should help limit the memory footprint of the computation.

.. Note::

    Beware, if the computation is fast or if the client is not started in the same python process as icclim,
    the dashboard may also look empty.

Disk read and write analysis - Dashboard
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
When poorly configured, the computation can spend most of it's CPU time reading and writing chunks on disk.
You can visualize if it is the case for you by opening dask dashboard (it should be on ``localhost:8787``).
In the status page, you can see in the right panel each task dynamically being added.
In these the colourful boxes, each color represent a specific task.
I/O on disk is displayed as orange transparent boxes. You should also see all other thread of the same worker
stopping when on thread is reading or writing on disk.
If there are a lot of i/o you may need to reconfigure dask for futur runs.
The solution to this are similar to the memory overload described above.
You can increase total available memory with ``Client(memory_limit="16GB")``.
You can decrease memory pressure by reducing chunk size with ``dask.config.set({"array.chunk-size": "50 MB"})`` or
by reducing number of threads with ``Client(n_workers=1, threads_per_worker=2)``.
Beside, you can also benefit from using multiple worker in this case.
Each worker is a separate non blocking process thus they are not locking each other when one of them need to write or
read on disk. They are however slower than thread to share memory, this can result in the "chatterbox" issue presented
below.

.. Note::

    - Don't instantiate multiple client with different configurations, put everything in the same Client constructor call.
    - Beware, as of icclim 5.0.0, the bootstrapping of percentiles is known to produce **a lot** of i/o.

Worker chatterbox syndrome - Dashboard
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In all this document, we mainly recommend to use a single worker with multiple threads.
Most of the code icclim runs is relying on dask and numpy, and both release the python GLI (More details on GIL here: https://realpython.com/python-gil/).
This means we can benefit from multi threading and that's why we usually recommend to use a single process (worker) with
multiple threads.
However, some configuration can benefit from spawning multiple workers.
In dask dashboard, you will see red transparent boxes representing the worker communication.
If you see a lot of these and especially if they do not overlap with other task, it means the workers are
spending most of their CPU times exchanging data.
This can be caused by either:
    1. there are too many workers for the amount of work
    2. the load balancing has a lot to do.
In the first case, the solution is simply to reduce the number of workers and eventually to increase the number of
threads per worker.
// TODO verify these claims and find a source
For the second case, when a worker has been given too many task to do, the load balancer is charged of
redistributing these task to other worker. It can happen when some task take significant time to be processed.
In icclim/xclim this is for example the case of the ``cal_perc`` function used to compute percentiles.
There is no easy solution for this case, letting the load balancer do its job seems necessary.

Idle threads
~~~~~~~~~~~~
When looking at dask dashboard, the task timelines should be full of colors.
If you see a lot of emptiness between colored boxes, it means your thread are doing nothing.
It could be because a blocking operation is in progress (e.g i/o on disk).
To fix this, you may report to `Disk read and write analysis - Dashboard`_ above.
It could also be because you have too many available threads and the work cannot be properly divided
between each thread.
In that case, you can simply reduce the number of thread in Clint configuration with ``Client(n_workers=1, threads_per_worker=4)``.

Conclusion
----------

We can't provide a single configuration which fits all possible datasets.
In this document we tried to summarize the few configurations we found useful while developing icclim.
You will need to tailor these to your own needs.
