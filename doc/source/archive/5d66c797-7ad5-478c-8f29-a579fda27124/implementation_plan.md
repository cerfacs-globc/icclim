# Implementation Plan - Expose `run_index` parameter for RLE calculations

Allow users to specify the `run_index` parameter (e.g., "first", "last") for indices involving run-length encoding (RLE), such as `max_consecutive_occurrence` and `sum_of_spell_lengths`. Default is "first".

## Proposed Changes

### Core Configuration
#### [MODIFY] `index_config.py`
- Add `run_index: str | None` to the `IndexConfig` dataclass to store the desired RLE indexing.

### Main API
#### [MODIFY] `main.py`
- Update `index` function to accept `run_index: str | None = "first"` as a keyword argument.
- Update `_build_config`, `_build_standard_index_config`, and `_build_user_index_config` to pass through the `run_index` parameter.

### Generic Indicator Engine
#### [MODIFY] `indicator.py`
- Update `GenericIndicator.__call__` to pass `config.run_index` to the `self.process` call.

### Generic Functions
#### [MODIFY] `functions.py`
- Update `max_consecutive_occurrence` to use `kwargs.get("run_index", "first")` in the `run_length.rle` call.
- Update `sum_of_spell_lengths` to do the same.

### Documentation & Release Notes
#### [MODIFY] `release_notes.rst`
- Add a note about the new `run_index` parameter in the next release section.

#### [MODIFY] `generic_indices.rst` (or similar)
- Document the `run_index` parameter for generic indices, explaining it defaults to `"first"`.

## Verification Plan

### Automated Tests
- Run the reproduction script `/tmp/repro_issue_321.py` (updated to use `run_index`) and verify it no longer errors and respects the `run_index` parameter.
- Add a new test case in `tests/test_issue_321.py` mirroring the user's request.

### Manual Verification
- Check that the output DataArray coordinates for time are consistent with the chosen `run_index`.
