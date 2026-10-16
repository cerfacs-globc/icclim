.. _dev_percentile_bootstrap:

#####################
Percentile bootstrap
#####################

This note records the current bootstrap optimization state for
percentile-based indices. It is meant for maintainers changing the
runtime bootstrap paths and their support boundaries.

Current strategy
================

For dask-backed percentile count indices with bootstrap enabled, icclim
first tries a compiled fast path. If the case is unsupported, or if the
user sets ``ICCLIM_BOOTSTRAP_MODE=safe``, icclim falls back to the exact
tiled bootstrap path.

The goal is reliability first: users should not have to guess a dask
chunking strategy, and icclim should avoid both memory exhaustion and
very large dask graphs.

The retained compiled path does not call xclim's generic bootstrap
decorator. Instead it:

- defers full percentile-threshold materialization until a path
  actually needs the threshold field, such as ``save_thresholds`` or
  the exact tiled fallback;
- tiles the spatial domain according to an explicit memory budget;
- loads one tile at a time, avoiding a large dask bootstrap graph;
- computes nominal thresholds inside the compiled path for
  non-overlapping years, avoiding an expensive materialized xarray
  threshold field;
- recomputes substitute-year bootstrap thresholds only for years overlapping
  the reference period;
- reuses each yearly substitute threshold across all output groups in that
  year, so monthly output does not recompute thresholds twelve times.

Fast path currently supports:

- annual ``YS``, monthly ``MS`` and anchored annual ``YS-*`` seasonal
  output periods;
- single day-of-year percentile thresholds;
- simple count operators: ``>``, ``>=``, ``<`` and ``<=``;
- no ``only_leap_years``;
- pandas-compatible calendars;
- supported day-of-year percentile counts on standard and proleptic
  Gregorian ``cftime`` calendars through the exact compiled
  order-statistics route;
- unfiltered and ``threshold_min_value``-filtered ``cftime`` ``sum``,
  ``average`` and ``fraction_of_total`` reducers through the same exact
  threshold reconstruction and daily union semantics;
- validated simple one-threshold spell reducers through the compiled
  union-mask route on pandas-compatible calendars and the exact eager tiled
  route on ``cftime`` calendars;
- validated compound count workloads that reuse component-mask
  composition;
- validated same-variable bounded scalar guards such as
  ``> 90 doy_per AND <= 30 degC`` or
  ``> 90 doy_per OR <= 10 degC`` for ``count_occurrences``,
  ``average``, ``sum`` and ``fraction_of_total``;
- validated same-variable percentile combinations such as
  ``> 95 doy_per OR <= 10 doy_per`` for ``count_occurrences``,
  ``average``, ``sum`` and ``fraction_of_total``.

Unsupported cases
=================

Cases outside the retained support boundary intentionally fall back to
the exact tiled bootstrap path or the reference path, depending on the
family. The most useful future extensions are likely:

- additional non-Gregorian CF-calendar families beyond the validated
  count, common value-reducer and simple-spell routes;
- additional ``threshold_min_value`` combinations beyond the current
  single day-of-year percentile boundary;
- broader spell/run-length combinations. Simple pandas-compatible
  one-threshold spells use a boolean union mask; ``cftime`` uses the exact
  eager tiled route, while compound ``cftime`` spells use the reference path;
- spell/run-length extension beyond the currently validated simple
  day-of-year percentile cases;
- broader compound percentile shapes beyond the currently validated
  multi-variable component-mask cases, bounded scalar guards and
  same-variable percentile combinations;
- additional reducer families that still need their own exact support
  boundary analysis.

Spell/run-length bootstrap follows a two-stage design:

- compute or bootstrap a daily exceedance mask first, reusing the
  current substitute-year percentile machinery;
- normalize the substitute comparisons into the same daily boolean union
  mask as the reference logical-link workflow, then run spell detection
  once on that mask.

Performance notes
=================

Benchmarks on representative real workloads showed that the compiled
annual path can be about 10 times faster than the exact tiled fallback
on a representative TG90p case, with bitwise-equivalent counts up to
floating-point noise:

- exact tiled fallback: about 1473 seconds;
- production fast path: about 146 seconds;
- maximum absolute difference: about ``5.7e-14``.

Compared to the old reference bootstrap dask graph path, performance is
case-dependent when the old path succeeds. On the ACCESS-CM2 validation
subset (65 years, 28 latitudes, 21 longitudes), the fast path was close
to the reference bootstrap path in wall-clock time, but removed the multi-million-task
dask graph:

- annual ``TG90p``: reference bootstrap 204 seconds and 4,691,198 graph tasks; fast
  212 seconds and 0 graph tasks; maximum absolute difference
  ``8.6e-14``; MaxRSS about 4.4 GB;
- monthly ``TG90p``: reference bootstrap 212 seconds and 4,696,205 graph tasks; fast
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
giant dask graphs. It is much faster than the reliable exact tiled
fallback, but it is not guaranteed to beat the old graph path on cases
where that graph path happens to complete.

For the supported exact ``cftime`` count route, a later real-data check
against commit ``00baef3b`` on Monday, August 24, 2026 confirmed that
the retained order-statistics redesign is exact on the validated
``TX90p`` workloads while materially faster than that fair
pre-optimization baseline:

- monthly ``TX90p``: about 2226 seconds before optimization versus
  about 979 seconds now;
- yearly ``TX90p``: about 2160 seconds before optimization versus about
  1037 seconds now.

That same comparison also confirmed an important boundary for
interpretation: several broader percentile-bootstrap workloads in
``00baef3b`` still fail before completion because they predate later
bootstrap-preparation fixes. So ``00baef3b`` remains the fair timing
baseline for supported ``cftime`` counts, but not a full executable
reference for every later optimized family.

The October 2026 extension validation retained unfiltered ``cftime``
``sum``, ``average`` and ``fraction_of_total``, plus filtered ``sum``.
All four matched the reference path over the full 65-year field for
both yearly and monthly output. Annual compiled runs took about 985 to
1,101 seconds, compared with about 1,109 to 1,253 seconds for the exact
tiled path. Annual scheduler batch ``MaxRSS`` was about 0.99 to 2.00
GiB for the compiled runs, 2.83 to 3.22 GiB for the reference runs and
1.59 to 2.22 GiB for the tiled runs.

The three unfiltered tiled comparisons each differed from both the
compiled and reference result at the same leap-sensitive 1952 cell.
The compiled and reference results agreed exactly. This is why the
reference path, rather than the tiled path alone, is the final
scientific comparison for this ``cftime`` extension.

The final filtered extension rerun retained ``count_occurrences``,
``average`` and ``fraction_of_total`` for both yearly and monthly output.
All six full-field comparisons had zero changed cells and zero maximum
difference against the reference. Annual compiled runs took about 1,069
to 1,074 seconds with scheduler ``MaxRSS`` of about 1.33 to 1.38 GiB;
the corresponding reference runs took about 229 to 238 seconds. The
compiled route is therefore a bounded-memory, graph-free alternative,
not a wall-clock speedup when the reference graph completes.

The same rerun rejected the original compiled ``cftime`` spell route.
Its custom threshold reconstruction created incorrect continuous multi-year
runs and took about 989 seconds. The replacement keeps xclim's percentile and
calendar operations, evaluates bounded spatial tiles eagerly and reduces the
substitute comparisons to a boolean daily union before run-length reduction.
On the full ACCESS-CM2 subset it matched all 13,959,708 daily reference-mask
values and reduced mask construction from about 343 to 135 seconds. The routed
annual spell calculation completed eagerly in about 167 seconds.

The same mask route made the annual ``cftime`` ``average`` field-exact in all
38,220 ACCESS-CM2 output cells, with identical coordinates and attributes. It
completed in about 173 seconds locally, compared with about 76 seconds for the
reference graph and roughly 1,000 seconds for the earlier compiled batch route.

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
compare the full field against the trusted reference path and the
production fallback path, and report at
least:

- maximum absolute difference;
- number of cells above a tight tolerance such as ``1e-9``;
- dimensions, coordinates and attributes;
- memory and wall-clock time for both paths.
