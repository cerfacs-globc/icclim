# `cftime` Exact Bootstrap Count Phase 2 Notes (2026-08-19)

Branch: `feature/bootstrap-next-phase`

## Phase boundary

The previous phase is complete for the current approach:

- full-field monthly `cftime` count validation is exact and materially faster;
- full-field yearly `cftime` count validation is exact but not materially faster.

That means the next phase is no longer “tune the existing route”.
It is “design a different exact algorithm for `cftime` bootstrap counts”.

## What phase 1 proved

Validated on Kraken on Wednesday, August 19, 2026:

- `tx90p_cftime_monthly`
  - exact tiled baseline: `4159.14s`
  - compiled experimental path: `2261.36s`
  - exact full-field comparison: `changed_cells = 0`, `max_abs_diff = 0.0`
- `tx90p_cftime_yearly`
  - exact tiled baseline: `2175.77s`
  - compiled experimental path: `2156.64s`
  - exact full-field comparison: `changed_cells = 0`, `max_abs_diff = 0.0`

So correctness is no longer the main uncertainty for count workloads.
The remaining question is algorithm shape.

## Why a new algorithm is needed

The current compiled count kernel is already much better than the xarray mask
path, but it still rebuilds threshold series inside the year loop.

For one cell it does:

1. one nominal threshold-series build for each non-overlap study year;
2. one threshold-series build for each `(target_reference_year, substitute_year)`
   pair in the overlap region.

That is exact, but it limits further gains.

## Candidate exact algorithm directions

### 1. Nominal-series reuse

For non-overlap years, the kernel currently rebuilds the same nominal threshold
series repeatedly per cell. That series can be built once per cell and reused.

This is low risk and exact, but it will only help the non-overlap portion of
the workload.

### 2. Threshold-bank algorithm

For overlap years, one option is to precompute threshold series for
`(target_reference_year, substitute_year, day_of_year, cell)` and then run
count aggregation from that bank.

This is exact, but memory may become the limiting factor.

### 3. Order-statistics reuse

The more ambitious direction is to avoid rebuilding each day-of-year quantile
from scratch when one reference year is substituted out and another is mapped
in. That likely needs a different exact order-statistics formulation rather
than another cache wrapped around the current kernel.

This is the most promising route for meaningful new gains, but also the most
complex.

## First measurement target for phase 2

Before touching runtime behavior, estimate whether a threshold-bank algorithm
is plausible at realistic domain sizes.

The helper:

- [tools/analyze_cftime_exact_count_algorithm.py](/Users/page/src/icclim/icclim/tools/analyze_cftime_exact_count_algorithm.py)

builds real bootstrap indexing on synthetic `cftime` inputs and reports:

- overlap versus non-overlap year counts;
- current threshold-series rebuild count per cell;
- estimated memory for:
  - a full threshold bank;
- a single-target threshold bank;
- a nominal-only cache.

On Wednesday, August 19, 2026, the first synthetic run was aligned to the
validated real-data shape:

- study years: `65`
- reference years: `30`
- overlap years: `30`
- non-overlap years: `35`
- spatial cells: `588` (`28 x 21`)
- output groups for monthly analysis: `780`

Measured implications:

- current compiled count work still rebuilds `905` threshold series per cell;
- a naive full threshold bank would still need `871` series per cell, so it
  barely changes the work shape;
- that full bank would cost about `1.50 GiB` in `float64`, or about
  `0.75 GiB` in `float32`, across the validated domain shape;
- a single-target threshold bank is far more plausible at about `49.8 MiB`
  in `float64`, or about `24.9 MiB` in `float32`, across the same domain;
- a nominal-only cache is tiny, but it only saves the repeated non-overlap
  rebuilds.

This already narrows the algorithm choice:

- a naive full bank is not attractive enough;
- nominal-only reuse is probably too small to be the main next-phase result;
- the promising options are either:
  - a per-target threshold-bank kernel; or
  - an exact order-statistics redesign that reduces the overlap rebuild cost.

## Success criteria for the next implementation step

Only proceed to runtime prototyping if the measurements show at least one of:

- nominal-series reuse gives a worthwhile share of current work back;
- a per-target threshold bank fits comfortably inside the intended tile memory;
- an order-statistics redesign is clearly justified by the rebuild counts.

## First prototype result

The first non-runtime prototype was added in:

- [tools/prototype_cftime_exact_count_threshold_bank.py](/Users/page/src/icclim/icclim/tools/prototype_cftime_exact_count_threshold_bank.py)

This prototype does **not** change library behavior. It:

1. builds nominal threshold series once per cell;
2. builds a per-target threshold bank for overlap years;
3. replays the count reduction from that bank;
4. compares the result with the current compiled count path.

On Thursday, August 20, 2026, it matched exactly on all synthetic
`cftime` fixtures already used in earlier validation:

- `constant`
- `leap_day_cold_spike`
- `reference_overlap_shift`

for both:

- monthly output (`MS`)
- yearly output (`YS`)

Observed result on every case/frequency pair:

- `changed_cells = 0`
- `max_abs_diff = 0.0`

That does **not** prove the algorithm is ready for runtime integration, but it
does remove one important uncertainty:

- the per-target threshold-bank shape is compatible with current exact count
  semantics on leap-sensitive synthetic cases.

## Updated phase-2 decision

The next implementation candidate should be:

1. keep the current routing unchanged;
2. prototype a compiled or partially compiled per-target bank evaluator behind
   a non-runtime or opt-in path;
3. only then compare it against the current compiled count route on real data.

## Second prototype step

On Thursday, August 20, 2026, the per-target bank shape moved from a standalone
tool into a library-internal prototype entrypoint:

- `compute_doy_percentile_bootstrap_count_threshold_bank_prototype`
  in [src/icclim/_core/generic/bootstrap.py](/Users/page/src/icclim/icclim/src/icclim/_core/generic/bootstrap.py)

This is still not used by runtime routing. Its purpose is narrower:

- make the candidate algorithm callable from normal tests;
- keep the prototype close to the real bootstrap primitives and metadata path;
- verify that the banked count reduction stays aligned with the current
  compiled count implementation.

Targeted synthetic tests now cover:

- `constant`
- `leap_day_cold_spike`
- `reference_overlap_shift`

for both:

- `MS`
- `YS`

and compare the library-internal prototype against the forced compiled count
path.

Observed result:

- `8 passed` in the focused prototype/cftime test selection;
- all synthetic comparisons remained exact.

That upgrades the phase-2 status from “external proof of concept” to
“internal prototype with regression coverage”.

## First benchmark result

On Thursday, August 20, 2026, a dedicated benchmark helper was added:

- [tools/benchmark_cftime_count_prototypes.py](/Users/page/src/icclim/icclim/tools/benchmark_cftime_count_prototypes.py)

This benchmark compares:

- the current compiled count path; and
- the library-internal threshold-bank prototype

on synthetic `cftime` workloads with the validated `65`-year study and
`30`-year reference shape.

First timing snapshots on the `reference_overlap_shift` monthly case:

- `1 x 1`
  - current compiled path: `1.396s`
  - threshold-bank prototype: `0.865s`
  - prototype is about `1.61x` faster
- `8 x 8`
  - current compiled path: `2.561s`
  - threshold-bank prototype: `28.144s`
  - prototype is about `11x` slower

Interpretation:

- the banked algorithm shape can reduce repeated threshold work;
- but the current Python-level reduction loop is not viable beyond tiny
  spatial shapes;
- so the only sensible continuation for this branch is a compiled or
  partially compiled banked reduction, not more Python-level tuning.

This result also sharpens the alternative:

- if a compiled banked reduction remains awkward or memory-bound, the next
  serious route is the deeper exact order-statistics redesign.

## Short version

Phase 2 should start by measuring threshold-bank viability and only then choose
between:

- a small exact cache improvement;
- a banked exact kernel;
- a deeper order-statistics redesign.
