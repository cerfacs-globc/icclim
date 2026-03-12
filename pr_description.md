### Pull Request to resolve #xxx
- [x] Unit tests cover the changes.
- [x] These changes were tested on real data.
- [x] The relevant documentation has been added or updated.
- [x] A short description of the changes has been added to `doc/source/references/release_notes.rst`.

### Describe the changes you made
This PR implements **lazy loading for `xclim` and its components** within `icclim`. The primary goal is to improve the initial import time of `icclim` and decouple its core logic from the eager loading of the heavy `xclim` library.

#### Key Improvements:
- **Lazy Module Imports**: DEferred core module imports in `icclim/__init__.py` using `__getattr__`.
- **Registry & Threshold Refactoring**: ECA&D registry now uses dictionary-based threshold definitions, preventing `xclim` from being imported during initialization. Full `Threshold` objects are built only upon calculation.
- **Bug Fixes**:
    - Resolved missing `run_length` import in `functions.py`.
    - Fixed `AttributeError` in `indicator.py` by using `da.name`.
    - **Bootstrapping Fix**: Corrected argument names in `__per_compute` to satisfy `xclim`'s `@percentile_bootstrap` decorator and removed a premature `.compute()` call that broke lazy chains.
- **Verification**: Confirmed **202 passing tests** and verified lazy loading behavior manually.
