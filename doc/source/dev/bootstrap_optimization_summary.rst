.. _dev_bootstrap_optimization_summary:

##############################
Bootstrap optimization summary
##############################

This note summarizes the recent bootstrap optimization work. It
complements the more detailed maintainability and architecture notes.

Scope
=====

This note covers the bootstrap work merged after the original
graph-heavy day-of-year percentile bootstrap route became difficult to
run reliably on large dask-backed datasets.

It is meant to answer four maintainer questions:

- what changed in the runtime path;
- which algorithm families are now optimized, exact or still routed to
  fallback paths;
- how the exact ``cftime`` count redesign was integrated;
- what validation evidence supports the retained implementation.

Initial state
=============

Before this work, percentile bootstrap mainly relied on the generic
``xclim`` reference bootstrap path. That route is scientifically sound,
but on large dask-backed workloads it can build very large task graphs
and become difficult to run reliably on real datasets.

The main bottlenecks in that earlier state were:

- the bootstrap calculation was expressed through a large xarray and
  dask graph rather than a small compiled inner loop;
- time and threshold preparation work was repeated across overlap years
  and output groups;
- monthly output could trigger repeated threshold work inside the same
  year;
- fallback exact routes were reliable, but much slower on the same
  workloads.

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

Main implementation changes
===========================

The retained work is not one single kernel change. It is a set of
related changes around routing, shared preparation steps and family
specific reducers.

1. Explicit bootstrap routing
-----------------------------

Bootstrap support is now classified explicitly from threshold and
reducer properties before the runtime path is chosen.

This routing distinguishes:

- bootstrap not required;
- optimized compiled bootstrap;
- exact tiled bootstrap fallback;
- reference bootstrap path for eager or diagnostic cases.

This prevents family-specific eligibility checks from being spread
through reducers.

2. Shared bootstrap preparation
-------------------------------

The optimized implementation now separates reusable bootstrap
preparation from reducer-specific logic.

The shared preparation layer now handles:

- reference-period extraction;
- optional threshold-floor filtering;
- day-of-year sampling indexes;
- reference-year and substitute-year alignment;
- flattened array preparation for compiled kernels.

That work is concentrated in ``bootstrap_primitives.py`` instead of
being rebuilt independently inside each reducer path.

3. Optimized count path for supported pandas-backed workloads
-------------------------------------------------------------

For supported day-of-year percentile count workloads, the runtime path
now avoids the large xarray or dask bootstrap graph.

The retained count path:

- prepares study and reference arrays once per tile;
- computes nominal non-overlap thresholds inside the compiled route;
- recomputes overlap substitute thresholds only where bootstrap is
  required;
- reuses threshold work across monthly groups inside the same year.

This works because the scientific operation is still the same:

- build the reference day-of-year sample;
- replace one overlapping reference year by each substitute year;
- evaluate the percentile threshold for that adjusted sample;
- count exceedance days against that threshold.

The optimization changes how this is executed, not what is computed.
Preparation is made explicit once, the repeated inner work is moved into
compiled kernels, and threshold work is reused wherever the bootstrap
definition allows reuse.

4. Extended optimized families built from the same threshold semantics
----------------------------------------------------------------------

The same threshold generation semantics are now reused for selected
additional families:

- selected value aggregates;
- selected spell reducers;
- selected compound count shapes;
- selected bounded single-variable compositions.

Those families were retained only where full-field validation stayed
exact against the trusted reference path.

5. Exact compiled ``cftime`` count redesign
-------------------------------------------

The ``cftime`` count work did not stop at keeping the old exact tiled
route. A new exact compiled route was designed and integrated for the
supported day-of-year percentile count family.

The retained redesign uses order-statistics reasoning instead of
rebuilding a full bootstrap sample for every overlap substitution.

For one cell and one day of year, the compiled route now works from:

- a nominal sorted sample for the reference day-of-year window;
- the values removed when the target reference year is excluded;
- the substitute-aligned values inserted in its place.

The exact method-8 percentile is then recovered from the adjusted sample
through rank-based queries on those three value sets.

In practice this means:

- exact percentile semantics are preserved;
- leap-aware substitute alignment stays explicit;
- overlap-year work is reduced compared with the earlier exact
  reconstruction route;
- supported ``cftime`` count workloads now use a retained compiled path
  rather than staying on the older exact tiled fallback.

This works because one overlap substitution changes only a small part of
the day-of-year sample. The compiled order-statistics route therefore
does not rebuild the full sample buffer for every
``(target_reference_year, substitute_year, day_of_year)`` combination.
It recovers the exact method-8 percentile from:

- the base sorted sample;
- the values removed with the target year;
- the values inserted from the substitute year.

That reduces repeated overlap-year work while keeping the same
percentile semantics.

Retained production boundary
============================

The retained optimized route focuses on the mathematically simpler
families first and widens only where exact validation is established.

In production today:

- supported day-of-year percentile counts use the compiled count path;
- supported ``cftime`` day-of-year percentile counts use the exact
  compiled order-statistics count path;
- selected value aggregates reuse the same threshold semantics;
- selected spell reducers use the validated compiled union-mask route;
- selected compound families reuse component-mask composition;
- unsupported cases still fall back to exact tiled or reference paths.

This separation keeps the workflow readable in climate-index terms:
prepare the reference sample, prepare temporal indexing, compute
thresholds where needed, then aggregate the resulting exceedance
information.

Validation and results
======================

Validation was done against exact reference behavior, not summary
statistics alone.

The retained validation rule is:

- compare the full field against the exact reference path;
- report maximum absolute difference and tolerance exceedances;
- check dimensions, coordinates and attributes;
- review wall-clock time and memory on real workloads.

Validation covered:

- synthetic overlap fixtures, including leap-sensitive cases;
- full-field real-data count validation;
- monthly, yearly and anchored seasonal output groups where supported;
- alternate chunk-profile checks for optimized families that depend on
  chunk robustness;
- focused runtime tests for routing and kernel behavior.

Representative benchmark figures already established in the retained
notes are:

- annual TG90p against the exact tiled fallback: about 1473 seconds for
  the fallback versus about 146 seconds for the production fast path,
  with maximum absolute difference about ``5.7e-14``;
- annual TG90p against the older reference bootstrap graph on the
  ACCESS-CM2 validation subset: 204 seconds and 4,691,198 graph tasks
  for the reference path versus 212 seconds and 0 graph tasks for the
  retained fast path, with maximum absolute difference ``8.6e-14`` and
  MaxRSS about 4.4 GB;
- monthly TG90p on the same subset: 212 seconds and 4,696,205 graph
  tasks for the reference path versus 212 seconds and 0 graph tasks for
  the retained fast path, with maximum absolute difference ``7.2e-15``
  and MaxRSS about 4.0 GB;
- anchored seasonal TG90p on the same subset: JJA 16 seconds eager
  reference versus 12 seconds fast dask path, and ONDJFM 22 seconds
  eager reference versus 22 seconds fast dask path, both with maximum
  absolute difference ``0``;
- a discarded intermediate strategy that materialized nominal
  non-overlap thresholds took about 247 seconds instead of about 155
  seconds on the same 65-year ACCESS-CM2 case, so that route was not
  retained.

For the exact compiled ``cftime`` order-statistics redesign, the
validated phase-3 note records that the compiled prototype was exact on
synthetic overlap and leap cases, exact on real-data ``1 x 1`` and
``2 x 2`` subsets, and faster than both the earlier compiled route and
the compiled threshold-bank prototype on those validated subsets. The
subset speedups recorded there were about ``4.30x`` for ``1 x 1`` yearly,
``2.61x`` for ``2 x 2`` monthly, and ``2.57x`` for ``2 x 2`` yearly.

The production conclusion is:

- supported compiled paths remove the giant reference bootstrap graph;
- those paths are much faster than the exact tiled fallback on the same
  supported workloads;
- field equality is the release criterion, not average similarity;
- unsupported or not yet trusted cases remain on exact fallback paths.

What remains out of scope
=========================

The following areas are not yet retained as optimized production
families:

- broader filtered percentile families beyond the validated reducer
  split;
- broader ``cftime`` bootstrap families beyond supported count
  workloads;
- more complex spell families that need separate reducer semantics after
  thresholding;
- any future route whose exactness is not demonstrated against the
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

icclim has specialized part of the execution strategy, but it has not
invalidated the scientific bootstrap definition inherited from
``xclim``.

Recommended next work
=====================

Bootstrap work should now split into two separate tracks.

First track:
finish bootstrap branch cleanup, documentation cleanup and any remaining
production-ready tests around the retained implementation.

Second track:
extend the same exact compiled ``cftime`` approach only when a new
family is ready for full validation. For supported day-of-year
percentile count workloads, the order-statistics redesign is already the
retained production path. Further work should focus on broader family
coverage or materially different algorithmic opportunities, not on small
tuning patches to the current route.
