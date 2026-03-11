### Pull Request to resolve #350
- [x] Unit tests cover the changes.
- [x] These changes were tested on real data.
- [x] The relevant documentation has been added or updated.
- [x] A short description of the changes has been added to `doc/source/references/release_notes.rst`.

### Describe the changes you made

This PR introduces support for **partial seasons** and **spatially varying seasonal bounds**, while also resolving a persistent `UserWarning` from `xclim` regarding frequency inference.

#### Key Features

- **Partial Seasons Support**: Added `allow_partial_seasons` parameter to `icclim.index`. When enabled, it allows including unfinished seasons at the time series boundaries (essential for indices like the KNMI Hellmann dataset).
- **Spatially Varying Seasons**: `slice_mode` now accepts a tuple of `(start, end)` day-of-year `DataArray` objects, enabling per-pixel seasonal definitions across a spatial grid.
- **Frequency Warning Fix**:
    - Explicitly sets the `freq` attribute on `DataArray.time` coordinates in `ClimateVariable` for better CF compliance.
    - Implemented a `_safe_to_agg_units` wrapper in `functions.py` to suppress redundant `xclim` "assuming 'D'" warnings during aggregation when the frequency is known but not automatically inferable by `xarray` (typical for irregular seasonal series).

#### Technical Details
- **climate_variable.py**: Proactively sets `time.attrs["freq"]`.
- **functions.py**: Added `_safe_to_agg_units` helper with a warning filter and replaced direct `to_agg_units` calls.
- **indicator.py**: Updated masking logic to honor `allow_partial_seasons` in `_handle_missing_values`.
- **main.py**: Exposed the new parameter and added doctests.

#### Verification
- Added `tests/test_partial_seasons.py` and `tests/test_spatially_varying_seasons.py`.
- All tests pass, and the console output is now clean of frequency inference warnings.
- Updated `release_notes.rst` and `icclim_index_api.rst`.
