# Goal Description
Fix issue #320 where using snow variables with a rate unit (`mm/s`) instead of an amount unit (`cm`, `mm`) causes a dimensionality error in `xclim` during `SD` index## Proposed Changes

### [Component] Core Input and Index Calculation

#### [MODIFY] [input_parsing.py](file:///Users/page/Documents/projets/COST_FutureMed/school_2025/icclim/icclim/src/icclim/_core/input_parsing.py)
- **Registry Lookup**: Ensure `Registry.lookup_no_error` is used (restore from metadata branch).
- **Snow Depth Variable**: Restore automatic rate-to-amount conversion for `SND` in `build_studied_data`.
- **Unit Updates**: Ensure `da.attrs[UNITS_KEY]` is updated after `rate2amount`.

#### [MODIFY] [test_main.py](file:///Users/page/Documents/projets/COST_FutureMed/school_2025/icclim/icclim/tests/test_main.py)
- **Accuracy**: Restore `fraction_of_total` expected values (Celsius consistency).
- **Error Expectation**: Update `test_mm_to_mmday__error_bas_standard_name` to expect `InvalidIcclimArgumentError`.
- **Imports**: Restore `pint` and `InvalidIcclimArgumentError` imports.

### [Component] Documentation

#### [MODIFY] [index.rst](file:///Users/page/Documents/projets/COST_FutureMed/school_2025/icclim/icclim/doc/source/how_to/index.rst)
- **Toctree**: Add `dask.rst` to the toctree to resolve RTD warning.

#### [MODIFY] [custom_indices.rst](file:///Users/page/Documents/projets/COST_FutureMed/school_2025/icclim/icclim/doc/source/references/custom_indices.rst)
- **Labels**: Ensure all `:ref:` links are valid (e.g., `generic_functions_api`).

---

## Verification Plan

### Automated Tests
- `pytest tests/test_main.py`
- `pytest tests/test_snow_depth_unit_conversion.py`
- `python /tmp/verify_320_real_data.py` (Verify with real data again)

### Documentation Build
- Run local sphinx-build if possible (already verified labels exist).
king that if `SND` is passed with `mm/s`, it calculates correctly without throwing `DimensionalityError`.
