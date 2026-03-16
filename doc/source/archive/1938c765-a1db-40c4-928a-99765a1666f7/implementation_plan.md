# Fix icclim 7.0.5 Conda-Forge Release

Release 7.0.5 was not updated on conda-forge because the automated bot was blocked by 4 stale open PRs and the recipe needs manual updates for new dependencies.

## Proposed Changes

### [icclim (Local Repository)](file:///Users/page/Documents/projets/COST_FutureMed/school_2025/icclim/icclim)

#### [MODIFY] [pyproject.toml](file:///Users/page/Documents/projets/COST_FutureMed/school_2025/icclim/icclim/pyproject.toml)
- Add `typing-extensions>=4.0` to `dependencies` as it's required for Python 3.10 and 3.11 (for `NotRequired` and `TypedDict`).

### [icclim-feedstock (GitHub)](https://github.com/conda-forge/icclim-feedstock)

#### Proposed [recipe/meta.yaml]
```yaml
{% set name = "icclim" %}
{% set version = "7.0.5" %}

package:
  name: {{ name|lower }}
  version: {{ version }}

source:
  url: https://pypi.org/packages/source/{{ name[0] }}/{{ name }}/icclim-{{ version }}.tar.gz
  sha256: 0cf1b6a8bf3a11604922eb0bf9ff69b1fc821bb10cc87e9a6edb1b81971069c6

build:
  number: 0
  noarch: python
  script: {{ PYTHON }} -m pip install . -vv

requirements:
  host:
    - python {{ python_min }}
    - pip
    - flit-core
  run:
    - python >=3.10
    - cf-xarray >=0.7.4
    - cftime >=1.5.0
    - dask-core >=2022.2.0
    - jinja2 >=3.0
    - netcdf4 >=1.5.7
    - numcodecs >=0.10.0
    - numpy >=1.21
    - pandas >=1.3.0
    - pint >=0.20
    - typing-extensions >=4.0
    - xarray >=2022.6.0
    - xclim >=0.45.0
    - zarr >=2.11.0
    - dateparser >=1.1.0
    - fsspec

test:
  requires:
    - pip
    - python {{ python_min }}
  imports:
    - icclim
    - icclim.models
  commands:
    - pip check

about:
  summary: icclim (Index Calculation CLIMate) is a python library for climate indices calculation.
  home: https://github.com/cerfacs-globc/icclim
  doc_url: https://icclim.readthedocs.io/
  dev_url: https://github.com/cerfacs-globc/icclim
  license: Apache-2.0
  license_file: LICENSE
  description: |
    icclim (Index Calculation CLIMate) is a python library for climate indices calculation.
    It wraps xclim, xarray and dask in a staight forward API. It is first meant to compute
    the ECA&D indices but also provide an API to create customized indices based on a few operators.

extra:
  recipe-maintainers:
    - pagecp
    - bzah
```

## Feedstock Action Plan
1. **Fork the Feedstock**: Fork [icclim-feedstock](https://github.com/conda-forge/icclim-feedstock) to your personal account.
2. **Create a PR from Fork**: Create a new Pull Request from your fork with the refined `meta.yaml` content.
    - Note: The bot blocked rerendering on PR #25 because it was from a branch within the feedstock.
3. **Rerender**: Comment `@conda-forge-admin, rerender` on your new PR. This will update the CI infrastructure to support Python 3.12.

## Verification Plan

### Automated Tests
- Run `pip check` locally after updating `pyproject.toml`.
- Verify the `meta.yaml` syntax using `conda-smithy lint` (if available) or by inspecting the PR build results on GitHub.

### Manual Verification
- The user (maintainer) should review the `meta.yaml` changes and the stale PR status on GitHub.
- Once the PR is submitted to the feedstock, monitor the conda-forge CI for success.
