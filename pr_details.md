PR Title: Refactor for Ruff Compliance and API Robustness (#186)

PR Description:

### Pull Request to resolve #186
- [x] Unit tests cover the changes.
- [x] These changes were tested on real data.
- [x] The relevant documentation has been added or updated.
- [x] A short description of the changes has been added to doc/source/references/release_notes.rst.

### Describe the changes you made
This PR refactors several core modules to improve code quality and comply with Ruff linting rules while ensuring strict backward compatibility and functional stability.

#### Key Improvements:

1. **Ruff Compliance**:
   - Resolved multiple violations including PLR0915 (too many statements), PLR2004 (magic numbers), ARG (unused arguments), PD (pandas-specific), and N (naming conventions).
   - Achieved 0 violations for the targeted rule sets.

2. **Structural Refactoring**:
   - Decomposed the monolithic `icclim.main.index` function into a modular architecture using specialized helper functions:
     - `_build_config`, `_build_standard_index_config`, and `_build_user_index_config` for configuration management.
     - `_parse_indicator_config` for centralized indicator resolution.
     - `_rename_coords` for consistent coordinate post-processing.

3. **API Robustness and Fixes**:
   - **Backward Compatibility**: Standardized internal naming to `ignore_feb29th` while ensuring the public API still accepts and correctly maps `ignore_Feb29th`.
   - **Dependency Management**: Fixed an ImportError by properly modularizing the `ICCLIM_REFERENCE` constant into `icclim._core.constants`.
   - **Calendar Handling**: Corrected a regression in `build_studied_data` by replacing an incorrect `xclim` attribute access with the direct `xarray` `convert_calendar` method.
   - **Method Correctness**: Reverted incorrect `.isna()` calls to the compatible `.isnull()` method for xarray DataArrays.

4. **Rigorous Verification**:
   - **Functional Testing**: Full `pytest` suite execution with 229/229 tests passed.
   - **Numerical Validation**: Performed real data validation using CMIP6 and ERA5 datasets, confirming numerical consistency with v7.0.5 results.
   - **CF Calendar Support**: Verified full support for non-standard climate calendars including `360_day`, `noleap`, and `all_leap`.
