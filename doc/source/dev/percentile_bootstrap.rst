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

The fast path is specialised for percentile-based count indices. It
does not call xclim's generic bootstrap decorator. Instead it:

- tiles the spatial domain according to an explicit memory budget;
- loads one tile at a time, avoiding a large dask bootstrap graph;
- computes nominal thresholds inside the compiled path for
  non-overlapping years, avoiding an expensive materialized xarray
  threshold field;
- recomputes donor-year bootstrap thresholds only for years overlapping
  the reference period;
- reuses each yearly donor threshold across all output groups in that
  year, so monthly output does not recompute thresholds twelve times.

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

Kraken benchmarks showed that the compiled annual path can be about 10
times faster than the safe tiled fallback on a representative TG90p case,
with bitwise-equivalent counts up to floating-point noise:

- safe tiled fallback: about 1473 seconds;
- production fast path: about 146 seconds;
- maximum absolute difference: about ``5.7e-14``.

Compared to the old xclim/dask graph path, performance is
case-dependent when the old path succeeds. On the ACCESS-CM2 validation
subset (65 years, 28 latitudes, 21 longitudes), the fast path was close
to the legacy path in wall-clock time, but removed the multi-million-task
dask graph:

- annual ``TG90p``: legacy 204 seconds and 4,691,198 graph tasks; fast
  212 seconds and 0 graph tasks; maximum absolute difference
  ``8.6e-14``; MaxRSS about 4.4 GB;
- monthly ``TG90p``: legacy 212 seconds and 4,696,205 graph tasks; fast
  212 seconds and 0 graph tasks; maximum absolute difference
  ``7.2e-15``; MaxRSS about 4.0 GB.

An intermediate experiment materialized the nominal percentile threshold
for non-overlapping years before entering the kernel. It was exact, but
large benchmarks showed a clear regression on the 65-year ACCESS-CM2
case: about 247 seconds instead of about 157 seconds on the same ``rome``
node. The retained strategy computes those nominal thresholds in the
compiled path and reuses each yearly threshold across monthly groups.

So the robust statement is that the fast path bounds memory and avoids
giant dask graphs. It is much faster than the reliable safe tiled
fallback, but it is not guaranteed to beat the old graph path on cases
where that graph path happens to complete.

Further large speedups are more likely to come from reducing Python,
xarray and dask preparation overhead than from micro-optimising the Numba
kernel. Promising areas:

- avoid preparing percentile thresholds twice before the fast path;
- load each spatial tile exactly once and keep unit-normalised values
  contiguous before entering the kernel;
- profile seasonal cases separately, because output grouping changes the
  amount of count work but not the bootstrap threshold work.

Validation rules
================

Do not validate bootstrap changes using mean differences only. Always
compare the full field against the safe reference path and report at
least:

- maximum absolute difference;
- number of cells above a tight tolerance such as ``1e-9``;
- dimensions, coordinates and attributes;
- memory and wall-clock time for both paths.
