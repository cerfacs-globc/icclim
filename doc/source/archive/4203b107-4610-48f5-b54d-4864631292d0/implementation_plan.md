# Adapting Temperature Unit Handling and Migrating User Index Tests

Address the user's request for better temperature unit flexibility (Kelvin/Celsius) and continue/verify the migration of `user_index` tests.

## Proposed Changes

### Core Unit Handling

#### [MODIFY] [input_parsing.py](file:///Users/page/Documents/projets/COST_FutureMed/school_2025/icclim/icclim/src/icclim/_core/input_parsing.py)
- Update `build_studied_data` to ensure that for temperature variables (`TAS`, `TAS_MIN`, `TAS_MAX`), the data is normalized to a common unit (Celsius) if it's currently in Kelvin, making threshold comparisons more reliable.

#### [MODIFY] [indicator.py](file:///Users/page/Documents/projets/COST_FutureMed/school_2025/icclim/icclim/src/icclim/_core/generic/indicator.py)
- Update `GenericIndicator.preprocess` to ensure that if `studied_data` is converted to a new unit (for "diff indicators"), the associated `threshold` values are also converted to match.

### Test Verification

#### [MODIFY] [test_user_index.py](file:///Users/page/Documents/projets/COST_FutureMed/school_2025/icclim/icclim/tests/test_user_index.py)
- verify that the new automated handling correctly interprets `degC` or unitless thresholds against Kelvin data without requiring hardcoded unit changes in tests.

## Verification Plan

### Automated Tests
- Run `pytest /Users/page/Documents/projets/COST_FutureMed/school_2025/icclim/icclim/tests/test_user_index.py`
- Add a specific test case for mixed Kelvin/Celsius units in temperature indices.
