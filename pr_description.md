# PR Description: Lazy Loading for xclim Imports

## Overview
This PR implements lazy loading for `xclim` and its components within `icclim`. The primary goal is to improve the initial import time of `icclim` and decouple its core logic from the eager loading of the heavy `xclim` library.

## Key Changes
- **Lazy Module Imports**: Utilized `__getattr__` in `icclim/__init__.py` to defer imports of `main`, `indices`, `threshold`, and other core modules.
- **Registry Refactoring**: Refactored `icclim/ecad/registry.py` to use dictionary-based threshold definitions instead of eager `Threshold` objects. This prevents `xclim` from being imported during registry initialization.
- **Threshold Factory Updates**: Updated `icclim/threshold/factory.py` and `icclim/main.py` to handle these dictionary representations, initializing full `Threshold` objects only when needed for calculations.
- **Bug Fixes and Regressions**:
    - Fixed missing `run_length` import in `functions.py`.
    - Corrected `AttributeError` in `indicator.py` by accessing `da.name` instead of a non-existent `short_name`.
    - Fixed bootstrapping logic in `percentile.py` by ensuring internal arguments (`da`, `freq`, `bootstrap`) match `xclim`'s `@percentile_bootstrap` decorator expectations and removing premature `.compute()` calls.
    - Updated `tests/test_generated_api.py` to align with the new threshold building mechanism.
- **API Regeneration**: Regenerated `_ecad.py`, `_dcsc.py`, and `_generic.py` to reflect changes in the underlying registry.

## Verification
- Full test suite run (`pytest tests/`): **202 passed**.
- Manual verification of lazy loading: Confirmed that `xclim` is not imported until a calculation function (e.g., `icclim.index`) is called.

## Impact
- Significantly reduced `import icclim` overhead.
- More robust threshold handling.
- Fixed `TX90p` bootstrapping edge case.
