# Generic Indices Documentation + Issue #109 CI Doctests

## Tasks

## Issue #109: Run doc examples in CI
- [x] Research existing CI, docstring structure, and test setup
- [x] Write implementation plan
- [x] Add `pytest --doctest-modules` configuration to `pyproject.toml`
- [x] Add `Examples` doctests to generic reducer functions
- [x] Add `Examples` doctest sections to `main.py::index`
- [x] Update `doc/source/dev/ci.rst` to mention doctests

## Generic Indices Documentation
- [x] Research existing doc structure, operators, thresholds
- [x] Create `doc/source/references/thresholds.rst` (new reference page)
- [x] Enrich `recipes_generic.rst` with in-memory examples and intro section
- [x] Add `thresholds.rst` to `references/index.rst` toctree
- [x] Verify RST builds without errors

## Test Coverage Expansion
- [x] Create `test_utils.py` and test `read_date()`
- [x] Create `test_logger.py` and test `IcclimLogger`
- [x] Expand `test_generic_functions.py` with sets of reducer tests

## Issue #170: General spatially varying seasons support
- [x] Implement `Frequency` updates for `seasonal_bounds` in `frequency.py`
- [x] Implement `_apply_seasonal_mask` in `indicator.py`
- [x] Add doctest examples to `main.py`
- [x] Add entry to `release_notes.rst`
- [x] Add user documentation to `icclim_index_api.rst`
- [x] Create tests to verify it works with spatially varying dates

## Partial Seasons Support (Issue #... )
- [x] Add `allow_partial_seasons` to `IndexConfig` in `index_config.py`
- [x] Add `allow_partial_seasons` to `icclim.index` signature in `main.py`
- [x] Update `Frequency` or `GenericIndicator` to honor `allow_partial_seasons`
- [x] Modify `_handle_missing_values` in `indicator.py` to allow incomplete last period
- [x] Add doctest/example for `allow_partial_seasons`
- [x] Update documentation and release notes
- [x] Add unit tests for partial seasons

## Frequency Warning Investigation
- [x] Investigate why `xclim` fails to infer frequency in some tests
- [x] Propose a fix (using a wrapper with warning filter)
- [x] Implement the fix to suppress the warning
- [x] Verify the fix with tests

## Linting and Code Quality
- [x] Refactor `GenericIndicator.preprocess` (C901)
- [x] Remove commented-out code (ERA001)
- [x] Remove `print` statements (T201)
- [x] Fix naming convention in tests (N801)

## Pull Request Preparation
- [x] Create a new branch `feat/partial-and-spatially-varying-seasons`
- [x] Commit changes and push to origin
- [x] Prepare PR title and description
