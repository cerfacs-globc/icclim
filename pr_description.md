### Pull Request to resolve #350

- [x] Unit tests cover the changes.
- [x] These changes were tested on real data.
- [x] The relevant documentation has been added or updated.
- [x] A short description of the changes has been added to `doc/source/references/release_notes.rst`.

### Describe the changes you made

This PR introduces support for **partial seasons** and **spatially varying seasonal bounds**, resolves a `numba` import error in conda environments, and suppresses spurious `xclim` frequency warnings.

#### Key Features

- **Partial Seasons Support**: Added `allow_partial_seasons` parameter to `icclim.index`. Supports granular control:
  - `True` — include both the first and last incomplete period
  - `False` — exclude any incomplete period (default, preserving existing behaviour)
  - `"start"` — include only the first incomplete period
  - `"end"` — include only the last incomplete period

  This is essential for indices like the KNMI Hellmann dataset which require including unfinished seasons at the boundaries of a time series.

- **Spatially Varying Seasons**: `slice_mode` now accepts a tuple of `(start_doy, end_doy)` `xarray.DataArray` objects, enabling per-pixel or per-cell seasonal definitions across a spatial grid.

- **Fix conda import error**: `ecad/binding.py` was accessing `xclim.atmos.*` attributes at class definition time, causing a `RuntimeError: cannot cache function '_keetch_byram_drought_index'` on `import icclim` in conda environments where xclim is installed from a compiled package. These accesses are now deferred to first use via lazy `@property` definitions.

- **Frequency Warning Fix**: Suppressed redundant `xclim` "Unable to infer sampling frequency" warnings during aggregation on seasonal/irregular time series.

#### Technical Details

- **indicator.py**: Updated `_handle_missing_values` to honour `allow_partial_seasons`.
- **frequency.py**: Added `_build_spatially_varying_seasonal_freq` and guarded `freq_keyword` string comparisons.
- **ecad/binding.py**: Made `standard_name` a lazy `@property` on xclim-proxied indicators.
- **functions.py**: Added `_safe_to_agg_units` helper with a warning filter.
- **main.py**: Exposed `allow_partial_seasons` and `run_index` parameters; added doctests.
- **index_config.py**: Added `allow_partial_seasons` and `run_index` fields.

#### Verification

- Added `tests/test_partial_seasons.py`.
- All 229 tests pass.
- Console output is clean of frequency inference warnings.
