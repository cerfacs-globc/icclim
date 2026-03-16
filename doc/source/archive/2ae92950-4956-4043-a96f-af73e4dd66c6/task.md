# Fix Linting for PR

## Analysis
- [x] Read CI/CD workflow (`.github/workflows/ci.yml`)
- [x] Read pre-commit config (`.pre-commit-config.yaml`)
- [x] Read `pyproject.toml` ruff configuration

## Linting Tasks
- [x] Run `ruff check` and capture all errors
- [x] Run `ruff format --check` to find formatting issues
- [x] Fix Ruff linting errors in core modules (`logger.py`, `main.py`, etc.)
- [x] Address circular imports in `index_group.py` and `threshold.py`
- [x] Update `tools/extract_icclim_funs.py` to handle circularities in generated files
- [x] Regenerate API files and verify extraction tool success
- [x] Fix lambda assignments in `functions.py`
- [x] Fix `TypeError` in `indicator.py` (Hydro context manager)
- [x] Fix remaining core Ruff errors
    - [x] Fix dataclass `__hash__` conflict in `StandardIndex` and `IndexGroup`
    - [x] Suppress `ARG001`/`ARG002` (unused arguments) in `functions.py` and `threshold/*.py`
    - [x] Suppress `ANN401` (Any) in `functions.py`
    - [x] Fix local imports `PLC0415` in `climate_variable.py` and `threshold.py`
    - [x] Fix `ANN102` (missing `cls` annotation) in core files
    - [x] Fix `ARG001` in `tools/extract_icclim_funs.py`
    - [x] Address `doc/source/conf.py` lint errors
- [x] Verify unit tests (noting known pre-existing failures)
- [x] Final check with `ruff check src/icclim`
- [x] Verify all pre-commit hooks pass (`pre-commit run -a`)
- [x] Run full CI/CD test suite as defined in `.github/workflows/ci.yml`
 and confirm 61/62 pass (1 pre-existing failure)
- [x] Verify all pre-commit hooks pass (`pre-commit run -a`)
- [x] Run full CI/CD test suite as defined in `.github/workflows/ci.yml`
 and confirm 61/62 pass (1 pre-existing failure)
- [x] Verify all pre-commit hooks pass (`pre-commit run -a`)
- [x] Address notebook linting errors (`ANN201`, `ANN001`, `ERA001`, `PERF401`)
    - [x] Create and run `fix_notebooks.py` to programmatically update `.ipynb` files
    - [x] Add type hints to functions in notebooks
    - [x] Optimize loops with list comprehensions
    - [x] Remove dead code/comments

## Verification
- [x] Run final `ruff` check on all affected files
- [x] Fix remaining Ruff errors in notebooks (`ERA001`, `E402`, `N816`)
- [x] Fix import sorting and local imports in tests (`I001`, `PLC0415`)
- [x] Resolve `degC` vs `°C` mismatch in `test_index_dtr__with_unit_conversion`
- [x] Fix `zarr`/`numcodecs` environment issue for CI compatibility
- [x] Confirm `test_read_dataset__zarr_store_success` passes
- [x] Fix pre-existing unit test failure
- [x] Run full `pytest` suite (187/187 passed)
- [x] Update `walkthrough.md` with final results

## Flexible Dependencies
- [x] Relax `pyproject.toml` dependency constraints
- [x] Verify tests pass with flexible dependencies
- [x] Update `walkthrough.md`

## Final Compatibility & Lockfile
- [x] Update `README.rst` with compatibility info
- [x] Regenerate `requirements-lock.txt` for bleeding edge
- [x] Update `walkthrough.md`

## Automated PR Integration
- [x] Standardize CI/CD on Python 3.9
- [x] Bump pre-commit hooks (Ruff, toml-sort)
- [x] Refine Extraction tool lint rules
- [x] Audit `publish-to-pipy.yml` and PyPI/Conda readiness
- [x] Final release verification (Ruff + Pytest)

## Real-Data Validation
- [x] Run and validate `/Users/page/src/icclim/icclim_usecase/simple_icclim.py`
- [x] Verify outputs against expected results
- [x] Final confirmation of release readiness

## Release Process (v7.0.5)
- [x] Verify `__version__` in `src/icclim/__init__.py`
- [x] Update `doc/source/references/release_notes.rst` with 7.0.5 details and date
- [x] Push `release/v7.0.5` branch to origin
- [x] Notify user to create/merge Pull Request to `master`

## Final Release Audit (v7.0.5)
- [x] Audit dependencies and remove redundant `psutil`
- [x] Regenerate `requirements-lock.txt` for v7.0.5
- [x] Analyze `pytest` warnings and confirm they are non-blocking
- [x] Verify final branch state and push to origin

## Final Release Audit (v7.0.5)
- [x] Audit dependencies and remove redundant `psutil`
- [x] Regenerate `requirements-lock.txt` for v7.0.5
- [x] Analyze `pytest` warnings and confirm they are non-blocking
- [x] Verify final branch state and push to origin
