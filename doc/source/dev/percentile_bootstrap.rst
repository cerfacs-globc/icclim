.. _dev_percentile_bootstrap:

####################
 Percentile bootstrap
####################

This note records the bootstrap optimisation state after icclim 7.1.4.
It is meant for maintainers changing the percentile-based count indices.

Current strategy
================

For dask-backed percentile count indices with bootstrap enabled, icclim
first tries a compiled fast path. If the case is unsupported, or if the
user sets ``ICCLIM_BOOTSTRAP_MODE=safe``, icclim falls back to the safe
tiled xclim path.

The goal is reliability first: users should not have to guess a dask
chunking strategy, and icclim should avoid both memory exhaustion and
very large dask graphs.

Fast path currently supports:

- annual ``YS`` and monthly ``MS`` output periods;
- single day-of-year percentile thresholds;
- simple count operators: ``>``, ``>=``, ``<`` and ``<=``;
- no ``threshold_min_value``;
- no ``only_leap_years``;
- pandas-compatible calendars.

Unsupported cases
=================

Unsupported cases intentionally fall back to the safe tiled path. The
most useful future extensions are likely:

- seasonal output periods, after validating that resample grouping and
  donor-year substitution are scientifically coherent for seasons;
- precipitation wet-day percentile thresholds using
  ``threshold_min_value``;
- non-standard calendars, once cftime grouping and leap handling are
  explicitly tested;
- spell/run-length indices, which likely need a different algorithm
  because the bootstrap cannot be reduced to independent daily counts.

Performance notes
=================

Kraken benchmarks showed that the compiled annual path is about 10 times
faster than the safe tiled path on a representative TG90p case, with
bitwise-equivalent counts up to floating-point noise.

Further large speedups are more likely to come from reducing Python,
xarray and dask preparation overhead than from micro-optimising the Numba
kernel. Promising areas:

- avoid preparing percentile thresholds twice before the fast path;
- load each spatial tile exactly once and keep unit-normalised values
  contiguous before entering the kernel;
- profile monthly and seasonal cases separately, because output grouping
  changes the amount of count work but not the bootstrap threshold work.

Validation rules
================

Do not validate bootstrap changes using mean differences only. Always
compare the full field against the safe reference path and report at
least:

- maximum absolute difference;
- number of cells above a tight tolerance such as ``1e-9``;
- dimensions, coordinates and attributes;
- memory and wall-clock time for both paths.
