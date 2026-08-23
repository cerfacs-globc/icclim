.. _dev_bootstrap_optimization_summary:

##############################
Bootstrap optimization summary
##############################

This note is the short human-readable summary of the recent bootstrap
optimization work. It complements the more detailed maintainability and
architecture notes.

What changed
============

Before this work, percentile bootstrap mainly relied on the generic
``xclim`` reference bootstrap path. That route is scientifically sound,
but on large dask-backed workloads it can build very large task graphs
and become difficult to run reliably on real datasets.

icclim now uses explicit bootstrap routing:

- use an optimized compiled path when the case is well understood and
  fully validated;
- fall back to the exact tiled path when the optimized route is not yet
  retained;
- keep the reference bootstrap path available for diagnostics and eager
  inputs.

The goal was not to change bootstrap semantics. The goal was to keep the
same scientific result while making production runs more robust on real
data.

Method
======

The retained optimized route focuses on the mathematically simple
families first:

- day-of-year percentile counts;
- supported value aggregates built from the same exceedance-mask logic;
- validated simple spell and compound extensions.

The implementation separates three concerns that had previously been
more entangled:

- bootstrap routing and support classification;
- threshold and temporal-index preparation;
- compiled daily-mask or count kernels.

This separation keeps the workflow readable in climate-index terms:
prepare the reference sample, prepare temporal indexing, compute
thresholds where needed, then aggregate the resulting exceedance
information.

Validation and results
======================

Validation was done against exact reference behavior, not summary
statistics alone.

The retained rule is:

- compare the full field against the exact reference path;
- report maximum absolute difference and tolerance exceedances;
- check dimensions, coordinates and attributes;
- review wall-clock time and memory on real workloads.

The current production conclusion is:

- the optimized dask-backed bootstrap path removes the giant reference
  bootstrap graph on supported cases;
- it is much faster than the exact tiled fallback on those same cases;
- it is not guaranteed to beat the old graph-heavy reference path in
  every environment when that older path happens to complete cleanly;
- unsupported or not yet trusted cases still fall back to an exact
  route.

Current scope
=============

The bootstrap campaign is effectively complete for the current retained
approach.

What is in production today:

- optimized routing for supported day-of-year percentile count cases;
- validated extensions for selected value aggregates, spell reducers and
  compound count shapes;
- exact tiled fallback for cases that are not yet retained on the
  optimized route.

What remains outside the retained production scope:

- a new exact optimized ``cftime`` bootstrap-count algorithm;
- broader filtered or complex spell families not yet validated for
  production use;
- any future work whose exactness is not demonstrated against the
  reference implementation.

Impact on xclim bootstrap code
==============================

This work does not modify ``xclim`` itself.

In the supported icclim fast paths, icclim no longer executes
``xclim.core.bootstrapping.percentile_bootstrap`` for the runtime
bootstrap calculation. Instead, icclim reproduces the same bootstrap
intent through its own explicit routing, threshold preparation and
compiled aggregation path.

That means the impact on the bootstrap code originally implemented in
``xclim`` by Abel is:

- no direct behavioral change inside ``xclim``;
- reduced runtime dependence on ``xclim``'s generic decorator for
  supported dask-backed icclim cases;
- continued conceptual dependence, because the icclim exact tiled and
  reference paths are still validated against the original bootstrap
  semantics;
- a likely upstream gap: if ``xclim`` itself needs the same large-scale
  dask robustness, equivalent work would need to be designed in
  ``xclim`` rather than assumed to come from icclim automatically.

So the practical reading is simple: icclim has specialized part of the
execution strategy, but it has not invalidated the scientific bootstrap
definition inherited from ``xclim``.

Recommended next work
=====================

Bootstrap work should now split into two separate tracks.

First track:
finish bootstrap branch cleanup, documentation cleanup and any remaining
production-ready tests around the retained implementation.

Second track:
if further meaningful speedup is required for exact ``cftime`` count
workloads, start a new algorithm-design phase rather than adding more
small tuning patches to the current route.
