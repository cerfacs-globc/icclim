# Implementation Plan: Spatially Varying Seasons and Partial Seasons

This plan outlines the implementation of two major enhancements to `icclim`'s seasonal handling:
1. **Spatially Varying Seasons**: Support for `slice_mode` as a tuple of `DataArrays` (Already implemented and verified, but documenting here for completeness).
2. **Partial Seasons Support**: A new `allow_partial_seasons` parameter to include unfinished seasons at the end of the time period.

## Proposed Changes

### Configuration and API

#### [MODIFY] [index_config.py](file:///Users/page/Documents/projets/COST_FutureMed/school_2025/icclim/icclim/src/icclim/_core/model/index_config.py)
- Add `allow_partial_seasons: bool = False` to the `IndexConfig` dataclass.

#### [MODIFY] [main.py](file:///Users/page/Documents/projets/COST_FutureMed/school_2025/icclim/icclim/src/icclim/main.py)
- Update `index` function signature to include `allow_partial_seasons: bool = False`.
- Update `_build_config` and `_build_standard_index_config` to pass this new parameter.
- Update docstrings with an example of partial season usage.

### Indicator Logic

#### [MODIFY] [indicator.py](file:///Users/page/Documents/projets/COST_FutureMed/school_2025/icclim/icclim/src/icclim/_core/generic/indicator.py)
- Update `GenericIndicator.__call__` to pass `allow_partial_seasons` from `config` to `postprocess`.
- Update `postprocess` to pass it to `_handle_missing_values`.
- Modify `_handle_missing_values` to implement the logic: if `allow_partial_seasons` is `True`, the last period of the result (if it coincides with the end of the input data) should not be masked, even if it's incomplete.

## Verification Plan

### Automated Tests
- Create `tests/test_partial_seasons.py`.
- Define a dataset ending in the middle of a requested season (e.g., data ends in December, season is Nov-March).
- Verify that `icclim.index(..., allow_partial_seasons=True)` returns a value for the last year.
- Verify that with `allow_partial_seasons=False` (default), the last year is `NaN`.

### Documentation
- Verify rendered `icclim_index_api.rst`.
