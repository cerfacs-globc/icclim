## Title
ENH: Run doctests in CI and expand generic reducer tests

## Description

**Context:**
This PR aims to close issue # 109 by adding inline doctests to our generic reducer functions and checking their validity as part of the pytest suite. We also introduced comprehensive sets of unit tests covering the heavily-used `functions` generic reducers which were previously lacking direct coverage.

**Proposed Changes:**
- **Pytest Doctests:** Added `pytest --doctest-modules` configuration to `pyproject` to collect and run docstrings with numpy-style examples directly in CI alongside unittests.
- **Runnable Doctests:** Refactored the docstrings of `icclim.index` in `main` and key `functions` generic reducers (`average`, `count_occurrences`, `maximum`, `minimum`, `generic_sum`, `max_consecutive_occurrence`) to contain fully runnable, in-memory `xarray.DataArray` examples.
- **Reference Doc additions:** Extracted a new explicit operator and thresholds reference page to `doc/source/references/thresholds` and converted the `recipes_generic` guides to run with isolated in-memory datasets matching the doctests.
- **Testing Expansion:** Expanded the coverage of `functions` reducers directly by adding explicit verification suites for each reducer in `test_generic_functions` checking output properties and edge-cases (e.g leap year offsets). Also created basic module unittesting for `test_logger` and `test_utils`.

**Verification:**
- `make -C doc html` builds cleanly and renders the recipes.
- `pytest tests/ src/icclim --doctest-modules` passes green with zero failures.

### Pull Request to resolve #109
- [x] Unit tests cover the changes.
- [x] These changes were tested on real data.
- [x] The relevant documentation has been added or updated.
- [x] A short description of the changes has been added to `doc/source/references/release_notes.rst`.
