import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim


def test_issue_340():
    # Recreate a minimal version of the issue
    time = pd.date_range("2000-01-01", periods=366, freq="D")
    data = np.random.rand(366)
    da = xr.DataArray(data, dims="time", coords={"time": time}, name="TG")
    da.attrs["units"] = "degC"

    # Run icclim.sum with seasonal slice_mode which adds time_bounds
    res = icclim.sum(
        in_files=da,
        var_name="TG",
        threshold="> 0 degC",
        slice_mode=("season", ([11, 12], [1, 2, 3])),
    )

    # Verify that time_bounds is in coordinates
    assert "time_bounds" in res.coords
    assert "time_bounds" not in res.data_vars

    # Verify that .sum() no longer fails
    try:
        sum_res = res.sum().compute()
        assert sum_res is not None
    except Exception as e:
        pytest.fail(f"Dataset.sum() failed with error: {e}")


if __name__ == "__main__":
    test_issue_340()
