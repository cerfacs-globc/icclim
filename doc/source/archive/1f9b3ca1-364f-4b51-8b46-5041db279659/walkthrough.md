# Walkthrough - Fix Issue 340: time_bounds as Coordinate

I have fixed issue 340 where calling `.sum()` on an `icclim` output Dataset would fail if `time_bounds` was present.

## Changes Made

### icclim Core
- Modified `src/icclim/main.py` to add `time_bounds` to `result_ds.coords` instead of `result_ds`. This ensures that xarray treat it as a coordinate and does not attempt to sum it when `.sum()` is called on the Dataset.

### Tests
- Added `tests/test_issue_340.py` which reproduces the reported issue and verifies that `.sum().compute()` completes successfully on the resulting Dataset.

## Verification Results

### Automated Tests
- **Reproduction Script**: The provided `reproduction_issue_340/example_icclim.py` now runs to completion without errors.
- **Regression Test**: `tests/test_issue_340.py` passed successfully.
- **Existing Tests**: Ran all tests in the `tests/` directory, and all 203 tests passed.

### Branch
- All changes have been committed to the new branch: `fix-340-time-bounds-coords`.
