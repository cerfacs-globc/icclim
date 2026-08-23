# Exact `cftime` Bootstrap Count Design Notes (2026-08-18)

Branch: `feature/bootstrap-next-phase`

## Why this phase exists

The previous bootstrap optimization phase closed with a clear boundary:
further meaningful performance work for day-of-year percentile `cftime`
counts requires a new exact algorithm, not more tuning of the exact tiled
`_compute_exceedance_mask` path.

This note records the first design-pass findings for that new phase.

## Current state

- Generic bootstrap routing still forces non-`DatetimeIndex` calendars onto
  `exact_tiled_bootstrap` with reason code
  `calendar_requires_exact_tiled_bootstrap`.
- The expensive path is the tile-local call to `_compute_exceedance_mask`
  followed by xarray resampling.
- Kraken deep profiling on Tuesday, August 18, 2026 showed the exact tiled
  count path dominating wall-clock time.

## Key code-level finding

The compiled bootstrap stack is already much closer to `cftime` support than
the dispatch layer suggests.

It already has:

- `CFTimeIndex`-aware array dtype selection in
  `src/icclim/_core/generic/bootstrap.py`;
- `month/day` substitute-year alignment in
  `substitute_indices_aligned_to_target`;
- `cftime`-compatible resample-group indexing in
  `build_bootstrap_temporal_indexing`;
- a daily-then-resample fast tiled path for `CFTimeIndex` counts in
  `_compute_fast_tiled_count_occurrences`.

So the remaining blocker is not “the optimized stack cannot represent
`cftime` bootstrap”. The blocker is that the current branch has not yet
proved that the compiled count semantics stay exact for real `cftime`
bootstrap workloads.

## Ground truth from this pass

This phase added low-risk primitive coverage rather than changing runtime
behavior:

- `build_bootstrap_temporal_indexing` now has direct `cftime` coverage;
- the Python view of `_bootstrap_count_kernel` now has a direct constant-case
  `cftime` monthly count check.

These checks do **not** prove the full algorithm is ready for release.
They do show that:

1. the bootstrap temporal indexing path already handles `cftime` grouping;
2. the compiled count kernel can reproduce simple exact `cftime` monthly
   counts once given prepared inputs.

That narrows the design problem substantially.

## Most likely mismatch locations

The remaining real-data mismatch is now most plausibly in one of these places:

1. substitute-year threshold generation around leap/non-leap alignment for
   overlapping reference years;
2. nominal versus substitute-year threshold handling for `cftime` monthly
   grouping;
3. interaction between compiled daily counts and `cftime` output label or
   aggregation semantics at the wrapper level.

The evidence is weaker for a fundamental kernel limitation.

## Recommended implementation order

1. Add a branch-local comparison helper that evaluates compiled `cftime`
   daily/yearly/monthly counts against the current exact tiled path on small
   synthetic leap and non-leap fixtures.
2. If those are exact, add an opt-in internal `cftime` count path that reuses
   `compute_doy_percentile_bootstrap_count` rather than `_compute_exceedance_mask`.
3. Keep the generic routing guard in place until:
   - synthetic leap-edge cases are exact;
   - `tx90p_cftime_yearly` and `tx90p_cftime_monthly` are exact on Kraken
     against the current trusted baseline;
   - chunk-layout sensitivity is checked again.
4. Only then consider lifting `calendar_requires_exact_tiled_bootstrap` for
   day-of-year percentile count workloads.

## What not to do

- Do not widen `cftime` support for spell or value-aggregate families yet.
- Do not remove the exact tiled fallback.
- Do not assume that passing constant-case primitives is enough for release.

## Short version

The new algorithm phase should start from the existing compiled bootstrap
count stack, not from scratch.
