# Bootstrap Next Phase Closeout (2026-08-18)

Branch: `feature/bootstrap-next-phase`

## Scope closed in this phase

- Close out `cftime` bootstrap validation for the exact tiled path.
- Close out filtered-average bootstrap routing and tuning.
- Continue optimization only where real-data profiling still showed worthwhile gains.

## Kept changes

- Keep exact `cftime` routing for day-of-year percentile count workloads.
- Keep filtered `average` on the exact tiled bootstrap path.
- Keep `ICCLIM_BOOTSTRAP_MODE=default` forcing the reference path for filtered-average baseline comparison.
- Keep reopen-aware prepared-input materialization for optimized spell workloads.
- Keep stabilized-study reuse for optimized compound value-aggregate workloads.

## Real-data validation completed

Kraken real-data validation and profiling were run on Monday, August 17, 2026.

### `cftime` validation

- Workload: `tx90p_cftime_monthly`
- Master result duration: about `703.94s`
- Current result duration: about `2726.32s`
- Current vs master compare:
  - `changed_cells = 10`
  - `max_abs_diff = 1.0`
- Current vs old August 16 rerun compare:
  - `changed_cells = 1`
- Focused cell diagnosis at `lat=51.875`, `lon=30.9375`, `time=1952-12-16`:
  - current exact path: `2.0`
  - forced old optimized path: `3.0`

Conclusion:

- The lone extra mismatch in current local state is the expected consequence of keeping `cftime` on the exact path instead of the old optimized/internal-daily path.
- The remaining `cftime` exact-path cost is still dominated by the exact tiled count computation itself.

### Filtered-average validation

- `generic_pr_average_bootstrap_yearly` stayed on the exact tiled path.
- Tile tuning was exhausted in this phase.
- Alternative chunking was worse than the default setup on Kraken.

Conclusion:

- No further worthwhile filtered-average tuning was found without changing the exact algorithm.

## Measured wins kept from the follow-up optimization phase

All timings below were measured on Kraken on Monday, August 17, 2026.

### Spell-family workloads

- `generic_tas_spell_bootstrap_yearly`: `72.10s -> 59.27s`
- `wsdi_yearly`: `58.40s -> 47.64s`
- `csdi_yearly`: `48.24s -> 45.73s`

### Compound value-aggregate workloads

- `generic_tas_compound_percentile_or_average_yearly`: `89.66s -> 65.33s`
- `generic_tas_compound_percentile_or_sum_yearly`: `66.82s`
- `generic_tas_compound_percentile_or_fraction_yearly`: `66.80s`

## Exact `cftime` deep profile

Kraken deep profile for `tx90p_cftime_yearly` on Tuesday, August 18, 2026:

- duration: `3996.70s`
- exact tiled count path total: `3990.65s`
- safe tile count: `12`
- `_compute_exceedance_mask`: `469.81s` across `12` calls

Conclusion:

- There is no hidden setup hotspot left worth tuning in the current exact `cftime` path.
- Further performance work there likely requires a new exact algorithm.

## Recommended next steps

1. Treat this bootstrap optimization phase as complete.
2. Keep the validated spell and compound value-aggregate optimizations.
3. Do not spend more time on exact `cftime` count tuning unless the goal becomes designing a new exact algorithm.
4. If optimization resumes later, open a separate phase explicitly scoped to exact `cftime` algorithm design.
5. Otherwise move to branch cleanup, commit grouping, and PR preparation.

## Suggested commit grouping

### Commit 1: validation and routing closeout

- `src/icclim/_core/generic/bootstrap_capability.py`
- `src/icclim/_core/generic/bootstrap_primitives.py`
- `src/icclim/_core/generic/threshold/percentile.py`
- `tests/test_bootstrap_capability.py`
- `tests/test_main.py`

Purpose:

- lock in exact `cftime` routing
- preserve filtered-average routing behavior
- keep the cftime-safe bootstrap primitive adjustments
- keep the threshold-units fix needed by the validated paths

### Commit 2: spell and compound bootstrap performance improvements

- `src/icclim/_core/generic/bootstrap.py`
- `src/icclim/_core/generic/functions.py`
- `tests/test_generic_functions.py`

Purpose:

- keep the spell-family reopen-aware prepared-input optimization
- keep compound value-aggregate stabilized-study reuse
- keep the shared bootstrap-kernel and dtype updates required by those wins

### Commit 3: benchmarking and validation tooling

- `tools/profile_bootstrap_phases.py`
- `tools/run_real_data_validation.py`
- `tools/summarize_real_data_validation.py`
- `tests/test_real_data_validation_tools.py`
- this closeout note

Purpose:

- preserve the real-data workloads used in this phase
- preserve the profiler instrumentation used to validate the outcomes
- preserve the branch-local closeout record for future handoff
