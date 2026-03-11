import numpy as np
import pandas as pd
import xarray as xr

import icclim


def test_allow_partial_seasons():
    # Create data from 2020-01-01 to 2021-12-31
    time = pd.date_range("2020-01-01", "2021-12-31", freq="D")
    tas = xr.DataArray(
        np.full(len(time), 30.0),
        coords={"time": time},
        dims=["time"],
        attrs={"units": "degC"},
    )

    # Season from Nov 1st to March 31st
    slice_mode = ("season", ("1 november", "31 march"))
    # Seasons:
    # 0: 2019-11-01 to 2020-03-31 -> partial (91 days of study: 2020-01-01 to 2020-03-31)
    # 1: 2020-11-01 to 2021-03-31 -> full (151 days)
    # 2: 2021-11-01 to 2022-03-31 -> partial (61 days of study: 2021-11-01 to 2021-12-31)

    # 1. Without allow_partial_seasons (default False)
    res_default = icclim.index(
        in_files=tas,
        index_name="SU",
        threshold="> 0 degC",
        slice_mode=slice_mode,
        allow_partial_seasons=False,
    )
    assert np.isnan(res_default.SU.values[0])
    assert not np.isnan(res_default.SU.values[1])
    assert np.isnan(res_default.SU.values[2])

    # 2. With allow_partial_seasons=True
    res_true = icclim.index(
        in_files=tas,
        index_name="SU",
        threshold="> 0 degC",
        slice_mode=slice_mode,
        allow_partial_seasons=True,
    )
    assert res_true.SU.values[0] == 91
    assert res_true.SU.values[1] == 151
    assert res_true.SU.values[2] == 61

    # 3. With allow_partial_seasons="start"
    res_start = icclim.index(
        in_files=tas,
        index_name="SU",
        threshold="> 0 degC",
        slice_mode=slice_mode,
        allow_partial_seasons="start",
    )
    assert res_start.SU.values[0] == 91
    assert not np.isnan(res_start.SU.values[1])
    assert np.isnan(res_start.SU.values[2])

    # 4. With allow_partial_seasons="end"
    res_end = icclim.index(
        in_files=tas,
        index_name="SU",
        threshold="> 0 degC",
        slice_mode=slice_mode,
        allow_partial_seasons="end",
    )
    assert np.isnan(res_end.SU.values[0])
    assert not np.isnan(res_end.SU.values[1])
    assert res_end.SU.values[2] == 61


if __name__ == "__main__":
    test_allow_partial_seasons()
