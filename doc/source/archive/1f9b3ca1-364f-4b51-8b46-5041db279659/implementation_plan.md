# Fix Issue 340: time_bounds as Coordinate

The goal is to fix a `UFuncBinaryResolutionError` when calling `.sum()` on an `icclim` output Dataset. The error is caused by `time_bounds` (a `datetime64` variable) being stored as a data variable, which xarray attempts to sum. moving `time_bounds` to coordinates resolves this and aligns with CF conventions and `cf-xarray` behavior.

## Proposed Changes

### icclim Core

#### [MODIFY] [main.py](file:///Users/page/Documents/projets/COST_FutureMed/school_2025/icclim/icclim/src/icclim/main.py)

Modify `_compute_climate_index` to add `time_bounds` to `result_ds.coords` instead of `result_ds`.

```python
        if time_bounds is not None:
-            result_ds["time_bounds"] = time_bounds
+            result_ds.coords["time_bounds"] = time_bounds
             result_ds.time.attrs["bounds"] = "time_bounds"
```

## Verification Plan

### Automated Tests
- Run the reproduction script `reproduction_issue_340/example_icclim.py` and verify it no longer fails on `.sum().compute()`.
- Run existing tests to ensure no regressions:
  ```bash
  ./.venv-icclim-705/bin/pytest tests/test_main.py
  ```

### Manual Verification
- Inspect the output of the reproduction script to confirm `time_bounds` is now under "Coordinates" instead of "Data variables".
