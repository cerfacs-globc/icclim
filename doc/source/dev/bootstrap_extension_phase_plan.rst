.. _dev_bootstrap_extension_phase_plan:

################################
Bootstrap extension phase plan
################################

This note defines the next meaningful bootstrap work after the current
optimization campaign.

Phase boundary
==============

The current production work is complete for its intended scope:

- supported day-of-year percentile counts have a retained compiled path;
- supported ``cftime`` day-of-year percentile counts have a retained
  exact compiled order-statistics path;
- selected value-aggregate, bounded, compound and spell families have
  already been validated and retained where they proved exact.

So the next work is not another tuning round on the existing route.
It is a new algorithm-extension phase.

Goal
====

Extend exact compiled bootstrap support to broader families, especially:

- broader ``cftime`` families beyond the original count workload;
- filtered percentile families with distinct nominal and substituted
  reference-sample semantics;
- spell families whose boolean-mask semantics must remain explicit in
  the compiled route;
- broader value-aggregate families that still depend on fallback paths.

Phase status
============

The first implementation and full-field validation round completed on
Friday, October 9, 2026. The follow-up correction and retention round
completed on Thursday, October 15, 2026. A further operational-route
extension completed on Friday, October 16, 2026.

The operational-route extension retained the following additions after
focused comparisons with the reference workflow:

- daily masks shared by extrema, standard deviation, rolling reducers,
  compound thresholds and date-event counts;
- mean substituted thresholds for ``excess`` and ``deficit``;
- filtered scalar-bounded count and value aggregates on ``cftime`` data;
- sequential exact evaluation of multiple percentiles without duplicating
  the bootstrap implementation;
- daily and other output frequencies whose groups remain within one calendar
  year, in addition to the established anchored seasonal routes;
- ``360_day``, ``365_day``/``noleap`` and
  ``366_day``/``all_leap`` calendars; and
- filtered pandas-backed spells through the shared optimized daily mask.
- weekly and other cross-calendar-year output groups whose bootstrap epoch is
  still an ordinary calendar year; and
- pandas-backed compound spells assembled from independently validated component
  masks.

The 366-day implementation follows the public percentile workflow exactly:
percentiles are calculated on days 1--365 and interpolated onto 366 target
days. The 360-day implementation instead retains its native 360-day basis.
Synthetic overlap cases for count, average and ``fraction_of_total`` match
the reference workflow on every supported non-Gregorian calendar.

Three boundaries remain deliberate. ``cftime`` spell calculations continue to
use the reference workflow because the compiled and tiled spell candidates
did not satisfy the real-data correctness and performance criteria. Arbitrary
output groups now use the compiled daily-mask route when xclim groups bootstrap
substitutions by ordinary calendar year. Frequencies whose bootstrap epoch has
a non-January anchor continue to use the exact tiled fallback unless they are
part of the previously validated seasonal routes. ``only_leap_years`` and
uncommon comparison operators also retain their established fallbacks.

Period percentiles are static components of a compound bootstrap expression.
Only day-of-year percentile components are substituted; the resulting daily
masks are then combined before reduction. Compound spell routing follows the
same rule on pandas-backed calendars. It does not introduce a separate compound
percentile algorithm.

The exact order-statistics threshold reconstruction is now shared by
the compiled reducers. The initial ``cftime`` validation retained:

- unfiltered ``sum``, ``average`` and ``fraction_of_total``;
- filtered ``sum`` with ``threshold_min_value``.

The following prototypes were not field-exact on the 65-year ACCESS-CM2
validation subset and were not retained:

- the simple spell prototype differed in one of 38,220 output cells,
  with a maximum absolute difference of ``1``;
- filtered ``fraction_of_total`` differed in 17,729 of 38,220 output
  cells, with a maximum absolute difference of about ``0.92``.

The follow-up investigation identified three implementation defects
rather than unsupported scientific cases:

- compiled spell preparation discarded the precision required by the
  ``cftime`` order-statistics calculation;
- the exact tiled spell shortcut passed fractional bootstrap masks to
  the run-length reducer without the boolean normalization used by the
  reference path;
- filtered overlap substitutions were reconstructed from the nominally
  filtered reference sample, whereas the reference algorithm rebuilds
  each substituted percentile from the raw reference years and applies
  the minimum-threshold clamp afterward.

The reducer semantics were also made explicit. Count and spell reducers
operate on the union exceedance mask produced by boolean normalization.
Filtered averages compute the mean over values selected by that union;
they do not average independently reduced substitute results.

These corrections are covered by focused Gregorian-like ``cftime``
tests for compiled and exact tiled execution. They justified full-field
evaluation of the compiled spell, filtered count, filtered average and
filtered ``fraction_of_total`` candidates.

The first corrected full-field rerun made both spell workloads exact,
but the three filtered reducers still shared a small set of differences:
208 of 38,220 annual cells and 214 of 458,640 monthly cells. That common
spatial and temporal pattern localized the remaining problem to threshold
preparation rather than reducer arithmetic.

The compiled union was being formed from 365-day substitute thresholds
before the public threshold workflow had filled missing days, aligned the
series to the target calendar and applied the floor. Those operations do
not commute with the minimum or maximum threshold used to represent a
boolean union. The corrected route prepares every substitute threshold in
target-calendar daily space first, then forms the union and performs the
family-specific reduction once.

That target-calendar correction made filtered count, average and
``fraction_of_total`` field-exact. It did not provide a sound retained
spell route: the final real-data spell comparison produced continuous
multi-year runs in some cells, and the compiled run took about four times
as long as the reference calculation. ``cftime`` spells therefore remain
on the reference path. The compiled spell helper is not part of the
retained ``cftime`` production boundary. A final production-route rerun
confirmed zero changed cells for both annual and monthly spell output.

Compiled routing covers standard and proleptic Gregorian calendars plus the
validated ``360_day``, ``365_day``/``noleap`` and
``366_day``/``all_leap`` CF calendars.

The final annual and monthly full-field comparisons for filtered count,
average and ``fraction_of_total`` all had zero changed cells and zero
maximum difference against the reference. Annual compiled wall-clock
times were about 1,069 to 1,074 seconds with scheduler ``MaxRSS`` of
about 1.33 to 1.38 GiB. The reference calculations took about 229 to
238 seconds, so the compiled route is retained for bounded memory and
graph avoidance, not as a wall-clock improvement when the reference
graph completes.

The decision rule remains unchanged: shared threshold reconstruction is
retained, but routing is widened only for consumers that pass focused
regression tests and full-field validation.

The four retained reducers were field-exact against the reference path
for both yearly and monthly real-data output. Their annual compiled
wall-clock times were about 985 to 1,101 seconds. The corresponding
exact tiled runs took about 1,109 to 1,253 seconds.

For the annual retained workloads, scheduler batch ``MaxRSS`` was about
0.99 to 2.00 GiB for the compiled runs, 2.83 to 3.22 GiB for the
reference runs and 1.59 to 2.22 GiB for the exact tiled runs. The
combined monthly current-plus-reference validation jobs peaked at about
3.10 to 3.33 GiB.

The unfiltered tiled outputs had one common leap-sensitive difference
at the 1952 output period and the same spatial cell. In all three cases,
the compiled output matched the reference output exactly. Filtered
``sum`` matched both the reference and tiled outputs. The reference path
therefore remains the scientific authority when evaluating this
``cftime`` extension; the tiled comparison remains useful for fallback
performance and for identifying tiled-path edge cases.

What the current code already makes possible
============================================

The current implementation already separates three reusable layers:

1. reference-sample preparation;
2. temporal indexing and substitute-year alignment;
3. family-specific compiled reducers.

That means the next phase does not need to redesign the whole bootstrap
workflow again. The main reusable asset is the exact compiled
``cftime`` order-statistics threshold reconstruction already retained
for counts.

The strongest next-phase direction is therefore:

- treat exact threshold reconstruction as the shared primitive;
- let broader families consume that primitive through their own exact
  reducers.

Priority order
==============

1. ``cftime`` value aggregates
==============================

This is the best next target.

Why it should come first:

- ``sum``, ``average`` and ``fraction_of_total`` already have compiled
  reducer shapes for pandas-backed workloads;
- the missing piece is the exact ``cftime`` threshold series, not an
  entirely new aggregation concept;
- value aggregates remain daywise once the threshold is known, so they
  are much closer to the current count route than spell metrics are.

Recommended design:

- factor the order-statistics threshold-series builder into a reusable
  internal service;
- let ``count``, ``sum``, ``average`` and ``fraction_of_total`` all
  consume the same exact threshold series for one cell and one
  overlap-substitution state;
- keep reducer-specific aggregation separate from threshold
  reconstruction.

Expected outcome:

- exact compiled ``cftime`` support for unfiltered
  ``sum``/``average``/``fraction_of_total``;
- one shared exact threshold engine instead of family-specific
  threshold rebuilding.

2. ``cftime`` filtered value aggregates
=======================================

This is the second target, after unfiltered value aggregates are exact.

Scientific boundary:

- ``threshold_min_value`` filters the nominal reference sample used to
  prepare the ordinary percentile;
- during an overlap bootstrap, the reference algorithm substitutes raw
  reference years, recomputes the percentile, and then clamps the
  resulting threshold to ``threshold_min_value``;
- applying the filter before substitution changes wet-day sample ranks
  and is not scientifically equivalent.

Recommended design:

- keep nominal filtered preparation separate from raw overlap
  substitution;
- apply the minimum-threshold clamp after each substituted percentile is
  reconstructed;
- validate each reducer separately, because previous work showed that
  reducer boundaries matter here.

Retention outcome:

- filtered count, ``sum``, ``average`` and ``fraction_of_total`` are
  retained on the compiled route for the validated Gregorian-like and
  non-Gregorian ``cftime`` calendars.

3. ``cftime`` spell families
============================

This is meaningful work, but it should not be the first extension.

Why it is harder:

- spell metrics are not independent daywise reductions;
- bootstrap has to preserve temporal structure after thresholding;
- the final result depends on runs, not only on daily exceedance counts
  or masked value sums.

Recommended design:

- reconstruct the daily threshold for every substitute year;
- combine the substitute comparisons into the boolean union mask used by
  the reference logical-link workflow;
- run spell detection once on that normalized daily mask.

This is the key boundary:

- do not try to reduce spell metrics to a count-style kernel;
- keep spell semantics explicit after thresholding.

Retention outcome:

- the ``cftime`` prototype was rejected by full-field validation and
  routing remains on the reference path;
- pandas-compatible simple spell families keep their previously
  validated compiled route.

4. Broader compound and filtered shapes
=======================================

This is the last priority.

Why it comes later:

- once the exact threshold engine exists for count and value-aggregate
  families, compound cases mostly become a question of composing exact
  component masks or exact component value selections;
- without that shared engine, compound extension would duplicate work.

Recommended design:

- keep compound routing explicit by component family;
- reuse exact component paths instead of adding compound-specific
  threshold logic first.

What is not worth doing
=======================

The next phase should not spend time on:

- more micro-tuning of the existing count kernels;
- more chunk-shape tweaking without a new algorithmic idea;
- widening support by special-casing individual named indices one by one;
- merging filtered, spell and value-aggregate semantics into one mixed
  kernel.

Those would increase complexity without changing the main algorithmic
boundary.

Concrete implementation order
=============================

The recommended order is:

1. extract the exact order-statistics threshold-series reconstruction
   into a reusable helper with a narrow internal API;
2. wire that helper into exact compiled ``cftime`` ``sum``,
   ``average`` and ``fraction_of_total`` prototypes;
3. validate those prototypes against the exact tiled path on synthetic
   leap-sensitive cases and representative real data;
4. retain only the families that stay field-exact;
5. then prototype spell support from exact bootstrapped daily masks,
   not from count-style reductions.

Validation standard
===================

Every new family in this phase must be validated against both the
reference path and the exact tiled fallback, not only against previous
optimized code. The reference path is the scientific authority when the
two comparison paths disagree.

The minimum standard is:

- leap-sensitive synthetic fixtures;
- representative real-data full-field comparison;
- yearly and monthly output where supported;
- changed-cell counts, maximum absolute difference, dimensions,
  coordinates and attributes;
- wall-clock time on the retained real-data workload.

Decision rule
=============

The next phase is successful if it produces at least one of:

- retained exact compiled ``cftime`` value-aggregate support beyond
  counts;
- retained exact compiled filtered percentile support beyond the current
  boundary;
- a clear exact spell-design prototype with passing synthetic and
  real-data validation.

If none of those land, the correct conclusion should again be explicit:
the boundary is algorithmic, not a lack of tuning.
