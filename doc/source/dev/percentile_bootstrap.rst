.. _dev_percentile_bootstrap:

#####################
Percentile bootstrap
#####################

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

- defers full percentile-threshold materialization until a path
  actually needs the threshold field, such as ``save_thresholds`` or
  the safe tiled fallback;
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

- annual ``YS``, monthly ``MS`` and anchored annual ``YS-*`` seasonal
  output periods;
- single day-of-year percentile thresholds;
- simple count operators: ``>``, ``>=``, ``<`` and ``<=``;
- no ``only_leap_years``;
- pandas-compatible calendars.

Unsupported cases
=================

Unsupported cases intentionally fall back to the safe tiled path. The
most useful future extensions are likely:

- percentile thresholds using ``threshold_min_value`` such as wet-day
  precipitation counts; Kraken validation on July 29, 2026 showed that
  the experimental fast-path implementation was materially faster but
  not field-identical to the safe tiled reference, so support remains
  disabled until donor-year bootstrap semantics are matched exactly;
- ``cftime`` calendars; Kraken validation on July 29, 2026 found a
  remaining one-cell mismatch on a Gregorian-like ``cftime`` case, so
  the release path keeps ``cftime`` on the exact safe tiled fallback
  until the fast-path semantics are field-identical;
- spell/run-length indices, which likely need a different algorithm
  because the bootstrap cannot be reduced to independent daily counts.

For spell/run-length work, the likely direction is a two-stage design:

- compute or bootstrap a daily exceedance mask first, reusing the
  current donor-year percentile machinery;
- run spell detection on the bootstrapped mask per donor year, then
  aggregate spell metrics across donors rather than trying to reduce
  spells to independent daily counts inside the current kernel.

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
case: about 247 seconds instead of about 155 seconds on the same ``rome``
node. The retained strategy computes those nominal thresholds in the
compiled path and reuses each yearly threshold across monthly groups.

Seasonal validation on the same 65-year ACCESS-CM2 subset showed that
anchored annual seasonal outputs match eager in-memory references exactly
while keeping the fast path graph-free:

- ``JJA`` ``TG90p``: eager reference 16 seconds; fast dask path 12
  seconds; maximum absolute difference ``0``;
- ``ONDJFM`` ``TG90p``: eager reference 22 seconds; fast dask path 22
  seconds; maximum absolute difference ``0``.

So the robust statement is that the fast path bounds memory and avoids
giant dask graphs. It is much faster than the reliable safe tiled
fallback, but it is not guaranteed to beat the old graph path on cases
where that graph path happens to complete.

Further large speedups are more likely to come from reducing Python,
xarray and dask preparation overhead than from micro-optimising the Numba
kernel. Promising areas:

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
