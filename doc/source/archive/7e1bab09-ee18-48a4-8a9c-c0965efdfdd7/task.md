### Initial Objectives
- [x] Fix linter issues for issue #320 (PR #339)
- [x] Manage metadata and Python 3.10 updates (PR #338)
- [x] Update release notes for next version (7.0.6)
- [x] Resolve all CI failures on both branches

### Detailed Tasks
- [x] **Bug Fix (#320)**
  - [x] Implement rate-to-amount conversion in `input_parsing.py`
  - [x] Improve error message in `basic.py`
  - [x] Add regression test `tests/test_snow_depth_unit_conversion.py`
- [x] **Maintenance**
  - [x] Update `pyproject.toml` to Production/Stable and Python 3.10+
  - [x] Update `environment.yml` and `installation.rst`
  - [x] Create release notes for version 7.0.6
- [ ] **CI/CD Debugging & Sync**
  - [x] Fix `TypeError` in `input_parsing.py` (`Registry.lookup`)
  - [x] Fix `AssertionError` in `test_main.py` (Celsius consistency)
  - [x] Restore missing `SND` unit conversion to `fix/issue-320`
  - [x] Fix test imports and expectations for `InvalidIcclimArgumentError` in `test_main.py`
  - [x] Resolve RTD build warnings (missing toctree and labels)
- [ ] **Branch Management**
  - [x] Consolidate `fix/issue-320` branch with all fixes
  - [x] Verify `maintenance/metadata-update` branch (Merged to master)
  - [x] Final verification of both PRs
