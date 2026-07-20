# Bootstrap Performance Plan (2026-07-20)

## Goal

Improve bootstrap performance for bulky percentile-based indices while preserving
the current semantics and numerical behavior.

This document is a handoff plan intended to be actionable for a medium-capability
LLM or a human contributor without requiring reconstruction of previous experiments.

## Branch And Baseline

- Working branch: `fix/bootstrap-next`
- Current checkpoint commit: `7ef205d`
- Baseline upstream behavior: `master` at `9d97cf1` / `origin/master` at `c3dd4e5`

## What Has Been Done

### Correctness and structure

1. Added `bootstrap=False` support and release-safe docs in `v7.1.3`.
2. Investigated and rejected the prepared post-DOY-state reuse approach
   (`7046c61` on older branch history): it was numerically wrong, especially
   around leap years and overlap years.
3. Added leap/common-year replacement tests in:
   - `tests/test_percentile_bootstrap.py`
4. Moved bootstrap orchestration upward into reducer logic for:
   - `count_occurrences`
   - `max_consecutive_occurrence`
   - `sum_of_spell_lengths`
5. Added overlap smoke coverage in `tests/test_main.py` for:
   - `TX90p`
   - `WSDI`
   - `CSDI`

### Benchmark tooling

Reusable benchmark helpers were added:

- `scripts/benchmark_bootstrap_tg90p.py`
- `scripts/compare_bootstrap_cached_outputs.py`
- `scripts/slurm_benchmark_bootstrap_tg90p.sh`

## What Was Learned

### Dead ends / rejected approaches

1. Threshold-level native bootstrap with donor-by-donor Python loops:
   - numerically recoverable
   - too slow
2. Prepared DOY-state reuse after year/dayofyear/window construction:
   - scientifically wrong
   - broke leap-year semantics
3. Reducer-level orchestration without donor vectorization:
   - architecturally better
   - still much too slow

### Current best local implementation

The current branch uses reducer-level orchestration plus bounded donor
vectorization using a bootstrap dimension per target year.

This is the first version that is:

- semantically much closer to the correct bootstrap model
- numerically aligned with `master`
- locally competitive enough to justify large-scale testing

## Current Validation Status

The following local tests were green at the RC checkpoint:

- `pytest tests/test_main.py -k 'bootstrap or wsdi or csdi or tg90p or tx90p'`
- `pytest tests/test_percentile_bootstrap.py`
- `pytest tests/test_generic_functions.py`

## Benchmark Summary

### Reduced laptop benchmark

Dataset:

- ACCESS-CM2 historical
- subset: `lat 45:55`, `lon 0:20`

Chunk setting A:

- `time=365, lat=16, lon=16`

Results:

- `master auto`: `35.87s`
- early branch native path: `172.58s`
- reducer engine without bounded donor vectorization: `168.46s`

Chunk setting B:

- `time=730, lat=144, lon=192`

Results:

- `master auto`: `22.98s`
- current branch (`7ef205d`) auto: `25.22s`

Numerics:

- means agree to near machine tolerance

### Larger laptop benchmark

Dataset:

- ACCESS-CM2 historical
- subset: `lat 35:70`, `lon 0:40`

Chunk setting:

- `time=730, lat=144, lon=192`

Results:

- `master auto`
  - total `51.57s`
  - compute `47.21s`
  - graph tasks `207,827`
  - max resident set about `6.47 GB`
- current branch (`7ef205d`) auto
  - total `52.67s`
  - compute `48.32s`
  - graph tasks `211,920`
  - max resident set about `7.06 GB`

Numerics:

- `master` mean `45.13441238564401`
- branch mean `45.13441238419539`

Conclusion:

- current branch is numerically good
- current branch is architecturally better
- current branch is not yet a clear performance win over `master`

## Hard Constraints

The next optimization must obey all of these:

1. Do not reintroduce donor replacement after DOY-state construction.
2. Do not change `bootstrap=False` behavior.
3. Preserve current `TX90p` 2-year and 3-year overlap behavior.
4. Preserve overlap behavior for `WSDI/CSDI`.
5. Do not accept a speedup if it introduces noticeable numeric drift.

## Immediate Optimization Target

The bottleneck is still repeated `percentile_doy(...)` work.

The next phase should focus on reducing repeated percentile construction while
keeping reducer-level orchestration.

Do **not** spend more time on high-level bootstrap orchestration refactors unless
a correctness issue is found.

## Precise Plan For A Medium Model

### Phase 1: Freeze the current baseline

1. Use `7ef205d` as the control implementation.
2. Always compare against `master` using the benchmark scripts.
3. Never evaluate a change without both:
   - reduced benchmark
   - larger laptop benchmark

### Phase 2: Profile the current branch at the right level

Add instrumentation to isolate the cost of:

1. `build_bootstrap_year_da(...)`
2. `xr.map_blocks(percentile_doy.__wrapped__, ...)`
3. `threshold._apply_percentile_op(...)`
4. `compute_from_exceedance(...)`
5. `donor_result.mean(dim=BOOTSTRAP_DIM, ...)`

Practical rule:

- profile one overlap year at a time
- do not profile the whole benchmark first

Expected outcome:

- identify whether the dominant cost is:
  - percentile construction
  - bootstrap cube construction
  - exceedance application
  - final reduction

### Phase 3: Implement cached local rolling-window reuse

This is the main algorithmic target.

Idea:

1. Precompute rolling-window views for each overlap year from the raw reference.
2. For bootstrap target year `Y`, only recompute rolling-window views for:
   - `Y - 1`
   - `Y`
   - `Y + 1`
3. Reuse the unaffected precomputed rolling-window views for all other years.
4. Only after that, rebuild the `year/dayofyear/window` structure used by
   `percentile_doy`.

Why this is safe:

- centered rolling windows only depend locally on neighboring years
- this respects the rule “replace raw year before percentile construction”
- this avoids the invalid post-DOY swap that caused earlier regressions

### Phase 4: Keep bounded donor parallelism

Keep the current structure:

- bootstrap orchestration at reducer level
- donor vectorization only within one target year

Do not build one giant all-years bootstrap cube.

If concurrency controls are added later, prefer:

- `bootstrap_jobs`
- `bootstrap_batch_size`

Avoid trying to infer available RAM from the environment.

### Phase 5: Benchmark gates

For every optimization candidate, run:

#### Reduced benchmark

```bash
python scripts/benchmark_bootstrap_tg90p.py \
  --repo /Users/page/src/icclim/icclim \
  --file-glob '/Users/page/src/icclim/icclim_usecase/data/latest/tas_day_ACCESS-CM2_historical_r1i1p1f1_gn_*.nc' \
  --lat-min 45 --lat-max 55 \
  --lon-min 0 --lon-max 20 \
  --time-chunk 730 --lat-chunk 144 --lon-chunk 192 \
  --scheduler threads \
  --bootstrap auto \
  --cache-dir /tmp/icclim-laptop-bench \
  --cache-key candidate-reduced \
  --force
```

#### Larger laptop benchmark

```bash
/usr/bin/time -l python scripts/benchmark_bootstrap_tg90p.py \
  --repo /Users/page/src/icclim/icclim \
  --file-glob '/Users/page/src/icclim/icclim_usecase/data/latest/tas_day_ACCESS-CM2_historical_r1i1p1f1_gn_*.nc' \
  --lat-min 35 --lat-max 70 \
  --lon-min 0 --lon-max 40 \
  --time-chunk 730 --lat-chunk 144 --lon-chunk 192 \
  --scheduler threads \
  --bootstrap auto \
  --cache-dir /tmp/icclim-laptop-bench \
  --cache-key candidate-large \
  --force
```

#### Numeric comparison

```bash
python scripts/compare_bootstrap_cached_outputs.py \
  --left /tmp/icclim-laptop-bench/master-auto-laptop.result.nc \
  --right /tmp/icclim-laptop-bench/candidate-reduced.result.nc \
  --label-left master_auto \
  --label-right candidate
```

### Phase 6: Acceptance criteria

A candidate is worth carrying to Kraken only if:

1. it passes all current bootstrap tests
2. it keeps reduced-benchmark numeric drift at machine-noise scale
3. it is at least clearly better on one axis:
   - faster than `master`, or
   - lower memory than `master`

Suggested threshold:

- aim for at least `10%` improvement on runtime or memory
- otherwise treat it as not good enough yet

## Tomorrow's Kraken Step

If a candidate meets the laptop acceptance criteria, run exactly the same
benchmark family on Kraken and compare:

- `master auto`
- candidate auto
- optionally `bootstrap=false` as a lower-bound reference

Kraken should only be used to validate scale, not to do first-pass debugging.

## When To Use A Stronger Model Again

Use a stronger reasoning model only if:

1. cached local rolling-window reuse proves too hard to implement safely, or
2. the next step becomes a true order-statistics update algorithm
   (pre-sorted sample replacement for percentile recomputation)

Until then, a medium model should be able to follow this plan.
