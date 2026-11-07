.. _dev_non_bootstrap_benchmarking:

##################################
Non-bootstrap performance benchmark
##################################

``tools/benchmark_non_bootstrap.py`` provides the reproducible benchmark matrix
for post-7.3.0 performance and memory work. Each case runs in a fresh subprocess
so its process-lifetime peak resident set size can be measured independently.

The default matrix covers:

- baseline count and sum reducers;
- five-day rolling sum and rolling mean reducers;
- monthly max, min, count and consecutive date-event reducers;
- daily and monthly reference-difference reducers;
- one file versus many files;
- native, explicitly selected and automatic chunks.

Every result records graph construction time, Dask task count, computation and
total wall time, scheduler calls and graph sizes, absolute peak RSS and peak-RSS
growth after imports. Current failures are stored as structured results so a
complete matrix can finish and later implementations can show when a workload
becomes executable.

Initial local baseline
======================

The initial smoke baseline was recorded on October 31, 2026 with a four-year,
8 by 8 synthetic cube. Each row below is the median across single-file and
many-file inputs using native, user-selected and automatic chunks. Peak RSS is
the absolute subprocess maximum and therefore includes Python imports.

.. list-table::
   :header-rows: 1

   * - Workload
     - Wall (s)
     - Build (s)
     - Compute (s)
     - Tasks
     - Scheduler calls
     - Peak RSS (MiB)
   * - Baseline count
     - 1.053
     - 0.946
     - 0.004
     - 50
     - 1
     - 304.8
   * - Baseline sum
     - 1.066
     - 0.954
     - 0.004
     - 52
     - 1
     - 305.4
   * - Rolling five-day sum
     - 1.063
     - 0.955
     - 0.004
     - 45
     - 1
     - 304.5
   * - Rolling five-day mean
     - 1.069
     - 0.955
     - 0.004
     - 45
     - 1
     - 305.1
   * - Monthly count date-event
     - 1.292
     - 1.183
     - 0.000
     - 0
     - 48
     - 305.8
   * - Monthly consecutive date-event
     - 2.634
     - 2.490
     - 0.037
     - 765
     - 51
     - 357.4
   * - Daily reference difference
     - 3.261
     - 2.656
     - 0.491
     - 7708
     - 1
     - 383.3
   * - Monthly reference difference
     - 1.167
     - 1.044
     - 0.015
     - 289
     - 1
     - 307.8

All six max date-event cases and all six min date-event cases failed during
construction with a chunked-array-indexer ``ValueError``. The harness records
these failures rather than omitting them. This baseline confirms that monthly
date-event count currently executes one graph per period during construction,
and that the daily reference-difference loop creates a much larger graph than
the monthly case.

Local synthetic run
===================

.. code-block:: console

   python tools/benchmark_non_bootstrap.py \
     --out /tmp/icclim-non-bootstrap.json

The synthetic cube size and matrix axes can be reduced for a smoke test:

.. code-block:: console

   python tools/benchmark_non_bootstrap.py \
     --out /tmp/icclim-smoke.json \
     --workloads baseline_count,rolling_sum_5day \
     --layouts single \
     --chunk-modes user \
     --years 4 --lat-size 16 --lon-size 24

Kraken validation
=================

``tools/run_real_data_validation.py`` accepts matching real-data workloads for
the baseline sum, rolling, monthly date-event and reference-difference cases.
Use the existing ``kraken_run_real_data_validation.slurm`` launcher and set its
``WORKLOAD`` variable to the desired workload name. Run each chunk profile in a
separate Slurm job when peak RSS is being compared so process-level measurements
remain isolated.
