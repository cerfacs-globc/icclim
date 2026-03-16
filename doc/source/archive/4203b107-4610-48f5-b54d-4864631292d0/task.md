# Task: Execute icclim v7.0.5 release process

## Research and Planning
- [x] Research release documentation and previous tags <!-- id: 0 -->
- [x] Create detailed release implementation plan <!-- id: 1 -->

## Preparation
- [x] Merge PR #330 into master <!-- id: 2 -->
- [x] Adapt temperature unit handling (Kelvin/Celsius) [#319]
    - [x] Research unit conversion logic and "double conversion" risk
    - [x] Plan implementation with the user
    - [x] Implement temperature normalization in `input_parsing.py`
    - [x] Ensure threshold alignment in `indicator.py`
    - [x] Verify fix by reverting hardcoded units in `test_user_index.py`
- [x] Migrate `test_user_index.py` to generic indices API <!-- id: 4 -->
    - [x] Migrate `TestMax` <!-- id: 5 -->
    - [x] Migrate `user_index` tests to generic API
    - [x] Refactor `TestMax`, `TestMin`, `TestMean`, `TestSum` to use generic functions
    - [x] Migrate `TestCountEvents` to use `count_occurrences` and generic thresholds
    - [x] Update `TestRunMean`, `TestRunSum` and `TestMaxConsecutiveEventCount`
    - [x] Refactor `TestAnomaly` to use `difference_of_means`
- [x] Execution & Verification
    - [x] Verify all tests pass in `.venv-icclim-705`
    - [x] Address bug fixes for coordinate access and unit handling
- [x] Create v7.0.5 PR <!-- id: 0 -->
- [x] Ensure CI passes <!-- id: 1 -->
- [x] Publish to PyPI and Conda Forge <!-- id: 2 -->
- [x] Close and verify addressed issues <!-- id: 3 -->

## Release Execution
- [x] Create and push the release tag <!-- id: 5 -->
- [x] Verify GitHub Action for PyPI release <!-- id: 6 -->
- [x] Address Conda Forge release (usually manual or via bot) <!-- id: 7 -->

## Verification
- [x] Verify availability on PyPI <!-- id: 8 -->
- [x] Verify Conda Forge update <!-- id: 9 -->
- [x] Update documentation (custom_indices, examples) [#319]
- [x] Create release walkthrough <!-- id: 10 -->
- [x] Commit changes for future release
