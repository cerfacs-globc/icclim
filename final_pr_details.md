PR Title: feat: Spatially Varying Seasons and Partial Seasons Support

### Pull Request to resolve #350
- [x] Unit tests cover the changes.
- [x] These changes were tested on real data.
- [x] The relevant documentation has been added or updated.
- [x] A short description of the changes has been added to doc/source/references/release_notes.rst.

### Describe the changes you made
This PR introduces support for partial seasons and spatially varying seasonal bounds, resolves a numba import error in conda environments, and suppresses spurious xclim frequency warnings. It also integrates lazy loading for xclim to improve initial import performance.

#### Key Features

- Partial Seasons Support: Added allow_partial_seasons parameter to icclim.index. Supports granular control:
  - True: include both the first and last incomplete period
  - False: exclude any incomplete period (default, preserving existing behaviour)
  - "start": include only the first incomplete period
  - "end": include only the last incomplete period

  This is essential for indices like the KNMI Hellmann dataset which require including unfinished seasons at the boundaries of a time series.

- Spatially Varying Seasons: slice_mode now accepts a tuple of (start_doy, end_doy) xarray.DataArray objects, enabling per-pixel or per-cell seasonal definitions across a spatial grid.

- Lazy Loading Implementation: deferred xclim imports to reduce startup time.

- Fix conda import error: ecad/binding.py was accessing xclim.atmos attributes at class definition time, causing a RuntimeError on import icclim in conda environments. These accesses are now deferred.

- Frequency Warning Fix: Suppressed redundant xclim "Unable to infer sampling frequency" warnings during aggregation on seasonal/irregular time series.

#### Verification
- Unit tests: dedicated tests for partial seasons (tests/test_partial_seasons.py) and spatially varying seasons (tests/test_spatially_varying_seasons.py).
- Integration tests: verified all existing integration tests pass (tests/test_main.py).
- Real data validation: successfully computed indices on ERA5 and CMIP6 datasets.
- Numerical Consistency: Results compared against v7.0.5 release. SU and PRCPTOT are numerically identical; TG shows only negligible floating-point deltas (~1e-4) in min/max.
