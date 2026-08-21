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
