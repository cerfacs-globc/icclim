# `cftime` Exact Bootstrap Count Phase 3 Notes (2026-08-21)

Branch: `feature/bootstrap-next-phase`

## Phase boundary

This phase starts after the threshold-bank branch was proved exact but was not
compelling enough on full real data to become the next production route.

That means the current question is no longer:

- can we cache more threshold series?

It is:

- can we redesign the exact overlap-year quantile evaluation so it does less
  repeated work than rebuilding a full day-of-year sample for every
  `(target_reference_year, substitute_year)` pair?

## Ground truth carried into this phase

Validated before this phase on Thursday, August 20, 2026:

- the compiled threshold-bank prototype is exact on synthetic overlap cases;
- the compiled threshold-bank prototype is also exact on full-field real
  monthly and yearly `TX90p` `cftime` runs;
- synthetic medium-size benchmarks still favor the compiled threshold-bank
  branch:
  - monthly `8 x 8`: about `1.98x` faster than the current compiled route;
  - monthly `16 x 16`: about `1.42x` faster;
  - yearly `8 x 8`: about `1.95x` faster;
  - yearly `16 x 16`: about `1.35x` faster;
- but earlier full-field real-data validation still showed the banked route
  slightly slower than the current compiled route.

So the branch is exact, but it is not yet the decisive next production
algorithm.

## Why the next exact algorithm should target order statistics

The current compiled count path still spends its overlap-year work here:

1. rebuild the full day-of-year sample for one cell;
2. apply the target-year substitution by remapping indices;
3. select the method-8 quantile from that rebuilt sample;
4. repeat for every overlap substitution and every day of year.

The threshold-bank prototype reduces some repeated counting work, but it still
stores or rebuilds full threshold series. The remaining opportunity is one
level lower:

- reuse the base order-statistics structure of a day-of-year sample;
- apply only the small delta introduced by replacing one reference year with
  another;
- recover the same exact method-8 quantile without rebuilding the whole sample.

## New phase-3 measurement

This phase adds:

- [tools/analyze_cftime_exact_order_stat_design.py](/Users/page/src/icclim/icclim/tools/analyze_cftime_exact_order_stat_design.py)

It measures the part that matters for an order-statistics redesign:

- total sample size per day of year;
- how many sample members come from one target reference year;
- how many substitute-aligned values actually need to be inserted for one
  `(target_reference_year, substitute_year)` replacement.

On Friday, August 21, 2026, on the same validated `65`-year study,
`30`-year reference, `28 x 21` domain shape:

- total sample count per day of year is about `150` in the common case;
- one target reference year contributes only a small slice of that sample per
  day of year;
- leap-aware substitute alignment can shrink that replacement slice further.

This is the key design fact:

- the overlap substitution changes only a small subset of the values that feed
  one day-of-year quantile.

That is exactly the condition where an exact delta-aware order-statistics
algorithm can be worthwhile.

## Proposed exact algorithm shape

### 1. Build one base sorted sample per `(day_of_year, cell)`

For one cell, for each day of year:

- gather the nominal valid reference values once;
- sort them once;
- keep the sorted values and the reference-year membership of each sample.

This becomes the reusable base state for all overlap substitutions.

### 2. Precompute the target-year delta, not a full threshold series

For each target reference year and day of year:

- record which base-sample members belong to that target year;
- record their values in sorted order;
- record the aligned substitute values for each substitute year.

The important point is that this delta set is small compared with the full
sample.

### 3. Recover the exact method-8 quantile from base sample plus delta

For one `(target_reference_year, substitute_year, day_of_year, cell)` pair:

- start from the base sorted sample;
- conceptually remove the target-year contribution values;
- conceptually insert the aligned substitute values;
- evaluate the exact method-8 order statistic on that adjusted multiset.

The candidate exact implementation route is:

1. compute the method-8 target ranks `k` and `k + 1` from the adjusted sample
   length;
2. answer `k` and `k + 1` with rank queries on:
   - the base sorted values;
   - the removed-value delta;
   - the inserted-value delta;
3. interpolate exactly as the current method-8 selector already does.

The key improvement is that the overlap substitution no longer rebuilds and
rescans the full sample buffer. It only queries the base sorted sample plus a
small delta set.

## First prototype result

This phase also adds:

- [tools/prototype_cftime_exact_order_stat_quantile.py](/Users/page/src/icclim/icclim/tools/prototype_cftime_exact_order_stat_quantile.py)

This first prototype is still non-runtime and Python-level. Its purpose is
more specific:

1. build one nominal sorted sample per day of year for one cell;
2. derive the removed target-year values and inserted substitute-year values;
3. recover the exact method-8 quantile from that adjusted multiset;
4. compare the resulting threshold series directly against the current
   `_build_bootstrap_threshold_series_for_cell` implementation.

Validated locally on Friday, August 21, 2026, on all current synthetic
`cftime` overlap fixtures:

- `constant`
- `leap_day_cold_spike`
- `reference_overlap_shift`

for both:

- monthly output (`MS`)
- yearly output (`YS`)

Observed result on every case/frequency pair:

- `changed_doys = 0`
- `max_abs_diff = 0.0`

On these fixtures, the overlap substitution delta is also very small:

- `max_removed_values = 1`
- `max_inserted_values = 1`

This does **not** prove the final full-domain algorithm yet, but it does
remove the main semantic uncertainty for the next step:

- the exact method-8 quantile can already be recovered from
  `base sorted sample + removed delta + inserted delta` without rebuilding the
  full per-day sample buffer.

## First full count prototype result

This phase also adds:

- [tools/prototype_cftime_exact_order_stat_count.py](/Users/page/src/icclim/icclim/tools/prototype_cftime_exact_order_stat_count.py)

This lifts the delta-aware quantile prototype one step higher:

1. build nominal threshold series from the adjusted-multiset selector;
2. build overlap substitution threshold series from the same selector;
3. run the full bootstrap count reduction from those threshold series;
4. compare the final count output against:
   - the current compiled count route;
   - the compiled threshold-bank prototype.

Validated locally on Friday, August 21, 2026, on all current synthetic
`cftime` overlap fixtures:

- `constant`
- `leap_day_cold_spike`
- `reference_overlap_shift`

for both:

- monthly output (`MS`)
- yearly output (`YS`)

Observed result on every case/frequency pair:

- `changed_cells = 0`
- `max_abs_diff = 0.0`

This is the first end-to-end result that matters for the new phase:

- the delta-aware exact order-statistics route is not only exact at the
  threshold-series level;
- it is also exact at the final bootstrap count output level on the current
  synthetic leap and overlap coverage.

The tiny local timing snapshots from this first prototype run are **not** yet
decision-grade because they are dominated by Python-level execution and local
warmup effects. At this stage they should be read only as a semantic check,
not as a performance conclusion.

## Python-level real-data validation

This phase also adds:

- [tools/benchmark_cftime_order_stat_real_data.py](/Users/page/src/icclim/icclim/tools/benchmark_cftime_order_stat_real_data.py)

This benchmark compares three exact routes on real data:

- the current compiled count route;
- the compiled threshold-bank prototype;
- the Python-level order-statistics redesign prototype.

Validated on Friday, August 21, 2026, on the real-data `TX90p` study used in
the earlier threshold-bank checks:

- `1 x 1` monthly (`MS`) and yearly (`YS`);
- `2 x 2` monthly (`MS`) and yearly (`YS`).

Observed exactness result on every validated shape and frequency:

- `changed_cells_vs_current = 0`
- `max_abs_diff_vs_current = 0.0`

Observed timing snapshots:

- `1 x 1`, `MS`:
  - current compiled: about `42.92s`;
  - compiled threshold-bank: about `24.33s`;
  - Python-level order-statistics: about `152.94s`.
- `1 x 1`, `YS`:
  - current compiled: about `24.24s`;
  - compiled threshold-bank: about `24.24s`;
  - Python-level order-statistics: about `152.74s`.
- `2 x 2`, `MS`:
  - current compiled: about `37.94s`;
  - compiled threshold-bank: about `26.80s`;
  - Python-level order-statistics: about `605.45s`.
- `2 x 2`, `YS`:
  - current compiled: about `37.91s`;
  - compiled threshold-bank: about `26.45s`;
  - Python-level order-statistics: about `617.97s`.

This closes the semantic question for the redesign on real data:

- the order-statistics route is exact on the validated real-data subsets;
- but the Python-level prototype is far too slow to be a production candidate.

So from this point onward, performance conclusions only matter for a compiled
order-statistics implementation.

## First compiled order-statistics benchmark

This phase also adds:

- [tools/benchmark_cftime_order_stat_compiled.py](/Users/page/src/icclim/icclim/tools/benchmark_cftime_order_stat_compiled.py)
- [tools/benchmark_cftime_order_stat_compiled_real_data.py](/Users/page/src/icclim/icclim/tools/benchmark_cftime_order_stat_compiled_real_data.py)

The first tool keeps the redesigned route fully inside a benchmark-oriented
Numba kernel so the question becomes narrower:

- if the order-statistics redesign is compiled, does it still preserve exact
  results;
- and does it start to recover the expected performance gain?

Validated locally on Friday, August 21, 2026:

- synthetic `constant`, monthly (`MS`), `1 x 1`:
  - `changed_cells_vs_current = 0`;
  - current compiled: about `1.64s`;
  - compiled threshold-bank: about `0.47s`;
  - compiled order-statistics: about `2.26s`.
- synthetic `reference_overlap_shift`, monthly (`MS`), `1 x 1`:
  - `changed_cells_vs_current = 0`;
  - current compiled: about `1.29s`;
  - compiled threshold-bank: about `0.46s`;
  - compiled order-statistics: about `1.25s`.
- synthetic `reference_overlap_shift`, monthly (`MS`), `4 x 4`:
  - `changed_cells_vs_current = 0`;
  - current compiled: about `1.54s`;
  - compiled threshold-bank: about `0.57s`;
  - compiled order-statistics: about `1.54s`.

These local snapshots show the expected shift:

- the compiled order-statistics redesign stays exact;
- and on the overlap-heavy synthetic case it is already roughly on par with
  the current compiled route.

## First compiled real-data result

On Friday, August 21, 2026, the compiled real-data benchmark was first
validated on `1 x 1`:

- monthly (`MS`):
  - `changed_cells_vs_current = 0`;
  - `max_abs_diff_vs_current = 0.0`;
  - current compiled: about `42.92s`;
  - compiled threshold-bank: about `24.24s`;
  - compiled order-statistics: about `8.15s`.
- yearly (`YS`):
  - `changed_cells_vs_current = 0`;
  - `max_abs_diff_vs_current = 0.0`;
  - current compiled: about `24.24s`;
  - compiled threshold-bank: about `24.11s`;
  - compiled order-statistics: about `5.64s`.

This is the first result in the whole redesign campaign that materially
changes the outlook:

- the compiled order-statistics redesign is exact on real data;
- it is about `5.26x` faster than the current compiled route on `1 x 1` monthly;
- it is about `4.30x` faster than the current compiled route on `1 x 1` yearly;
- it is also materially faster than the compiled threshold-bank prototype on
  the same real-data slice.

That means this new phase is no longer just a design exercise. It has already
produced one compiled exact real-data route that looks genuinely promising.

## Compiled real-data scaling check

The next real-data check on Friday, August 21, 2026, extended the same
compiled benchmark to `2 x 2`:

- monthly (`MS`):
  - `changed_cells_vs_current = 0`;
  - `max_abs_diff_vs_current = 0.0`;
  - current compiled: about `38.74s`;
  - compiled threshold-bank: about `26.09s`;
  - compiled order-statistics: about `14.85s`.
- yearly (`YS`):
  - `changed_cells_vs_current = 0`;
  - `max_abs_diff_vs_current = 0.0`;
  - current compiled: about `38.74s`;
  - compiled threshold-bank: about `25.81s`;
  - compiled order-statistics: about `15.05s`.

So the real-data picture now holds on both validated subset sizes:

- `1 x 1`, monthly (`MS`): compiled order-statistics is about `5.26x` faster
  than the current compiled route;
- `1 x 1`, yearly (`YS`): about `4.30x` faster;
- `2 x 2`, monthly (`MS`): about `2.61x` faster;
- `2 x 2`, yearly (`YS`): about `2.57x` faster.

It also still stays ahead of the compiled threshold-bank route on all four
validated real-data cases.

## Phase-3 conclusion

This phase started as a redesign study for a different exact `cftime`
bootstrap-count algorithm. It now has three progressively stronger results:

1. the order-statistics redesign is exact on synthetic overlap and leap cases;
2. it is exact on real-data `1 x 1` and `2 x 2` subsets;
3. once compiled, it is materially faster than both:
   - the current compiled route;
   - the compiled threshold-bank prototype
   on the validated real-data subsets.

So the honest conclusion at the end of this phase is no longer the earlier
"the redesign is valid but not yet competitive" position.

It is now:

- a new exact `cftime` bootstrap-count algorithm has been designed;
- its compiled prototype is already performance-promising on real data;
- the next phase should focus on turning that compiled prototype into a clean
  production implementation inside the runtime path, while preserving the
  exact validated semantics.

## Expected benefits

- exact semantics stay tied to the existing method-8 definition;
- leap-day substitution stays explicit instead of hidden in a larger bank;
- overlap-year work should scale with replacement-set size rather than with
  the full day-of-year sample rebuild;
- memory pressure should stay lower than a full threshold bank because the
  reusable object is a base sorted sample plus small per-target deltas, not a
  threshold series for every target/substitute pair.

## Main risks

1. Duplicated values:
   the delta-aware rank logic must treat equal values carefully so the result
   stays identical to the current exact selector.

2. Variable adjusted sample size:
   leap-aware substitute alignment can remove samples without a one-to-one
   replacement, so the method-8 ranks must be computed from the adjusted valid
   sample count, not from the nominal count.

3. Numba implementation complexity:
   the clean algorithm shape is clearer than the final low-level kernel shape.
   A reference prototype should stay Python-level or non-routed until the
   exact semantics are locked down.

## Recommended implementation order

1. Add a non-runtime prototype that computes one overlap quantile from:
   - a base sorted sample;
   - a removed delta;
   - an inserted delta.
2. Verify exact equality against `_quantile_for_doy_cell` on synthetic leap and
   overlap fixtures.
3. Lift that prototype to a full threshold-series builder for one cell.
4. Only then compare the order-statistics prototype with:
   - the current compiled route;
   - the compiled threshold-bank prototype.

## Short version

The new exact algorithm phase should not start from another threshold cache.
It should start from a delta-aware exact order-statistics design:

- one reusable base sorted sample per day of year;
- one small replacement delta per target/substitute pair;
- exact method-8 quantiles recovered from the adjusted multiset.
