# Walkthrough: User Index Migration & Temperature Unit Robustness

I have successfully migrated the legacy `user_index` tests and implemented a robust strategy for handling temperature unit conversions (Kelvin vs. Celsius) in `icclim`.

## Changes Made

### 1. Test Migration
- Migrated all 18 tests in `test_user_index.py` to use the new generic indices API (`icclim.maximum`, `icclim.index`, etc.).
- Replaced attribute-style access (e.g., `result.sum`) with dictionary-style access (e.g., `result["sum"]`) for compliance with `xarray.Dataset`.
- Updated test stubs to use physically realistic Celsius values instead of abstract magnitudes for better test reliability.

### 2. Core Unit Handling Improvements
- **Automatic Temperature Normalization**: Updated `build_studied_data` in `input_parsing.py` to automatically normalize temperature variables (like `TAS`) to Celsius if they are provided in Kelvin. This ensures that user thresholds (likely in Celsius) are compared against correctly scaled data.
- **Threshold Synchronization**: Updated `GenericIndicator.preprocess` in `indicator.py` to ensure that when input data is converted to a target output unit (e.g., for "diff" indicators like DTR), the associated threshold is also synchronized to that unit.
- **Safeguard against "Double Conversion"**: The logic preserves the relative magnitude of differences while ensuring absolute scales are aligned before computation.

## Verification Results

### Automated Tests
I ran the full `test_user_index.py` suite in the `.venv-icclim-705` environment.

```bash
pytest /Users/page/Documents/projets/COST_FutureMed/school_2025/icclim/icclim/tests/test_user_index.py
```

**Result**: All 18 tests passed successfully.

### Manual Verification of Unit Flexibility
I verified that thresholds like `> 15` work correctly whether the input data is in Kelvin (auto-converted to Celsius) or Celsius.

## Key Files Modified
- [input_parsing.py](file:///Users/page/Documents/projets/COST_FutureMed/school_2025/icclim/icclim/src/icclim/_core/input_parsing.py): Added temperature normalization logic.
- [indicator.py](file:///Users/page/Documents/projets/COST_FutureMed/school_2025/icclim/icclim/src/icclim/_core/generic/indicator.py): Added threshold synchronization for unit-converted data.
- [test_user_index.py](file:///Users/page/Documents/projets/COST_FutureMed/school_2025/icclim/icclim/tests/test_user_index.py): Migrated and verified legacy tests.
