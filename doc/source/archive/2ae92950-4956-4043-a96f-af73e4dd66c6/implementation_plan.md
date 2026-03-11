# Flexible Dependency Configuration

The goal is to make `icclim` dependencies more flexible by relaxing strict upper bounds in `pyproject.toml` and creating a matching `requirements.txt` with minimum versions only.

## Proposed Changes

### Build and Dependency Layer

#### [MODIFY] [pyproject.toml](file:///Users/page/Documents/projets/COST_FutureMed/school_2025/icclim/icclim/pyproject.toml)
- Lower Python baseline to `3.9+` and relax dependency minimums.
- Maintain support for latest versions (Zarr 3.x, Pandas 3.x).

#### [MODIFY] [CI/CD Workflows](file:///Users/page/Documents/projets/COST_FutureMed/school_2025/icclim/icclim/.github/workflows/)
- Update `ci.yml` and `publish-to-pipy.yml` to use **Python 3.9** (new minimum supported version).
- Remove redundant `lint` job from `ci.yml` to rely on `pre-commit.ci`.
- **Verify `publish-to-pipy.yml`**: Ensure correctly configured for PyPI trusted publishing.

#### [MODIFY] [.pre-commit-config.yaml](file:///Users/page/Documents/projets/COST_FutureMed/school_2025/icclim/icclim/.pre-commit-config.yaml)
- Bump `ruff` to `v0.15.2+` and `toml-sort` to `v0.24.3` to match bleeding-edge environment.

#### [MODIFY] [extract_icclim_funs.py](file:///Users/page/Documents/projets/COST_FutureMed/school_2025/icclim/icclim/tools/extract_icclim_funs.py)
- Include `E501` (line length) in the automated `noqa` for generated files.

## Verification Plan

### Automated Tests
- Run `pytest` with latest dependencies.
- Verify `ruff check .` passes with new hook versions.

### Publishing Readiness
- **PyPI Audit**: Check `publish-to-pipy.yml` action versions (e.g., `pypa/gh-action-pypi-publish@v1.13.0`).
- **Conda-forge Audit**: Verify `pyproject.toml` dependencies and versioning are compatible with standard conda-forge recipe requirements. Ensure no blockers for the `icclim-feedstock`.

### Automated Tests
- Run `pytest` to ensure that the current environment (which meets the new flexible criteria) still passes all tests.
- Re-run `pip-compile` to ensure `requirements-lock.txt` can still be successfully generated from the new flexible definitions.
