import warnings

import numpy as np
import pandas as pd
import pytest
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


def test_yearly_period_with_missing_months_is_masked_by_default():
    time = pd.date_range("2001-01-01", "2001-12-31", freq="D")
    time = time[~time.month.isin([4, 5, 6])]
    tas = xr.DataArray(
        np.full(len(time), 30.0),
        coords={"time": time},
        dims=["time"],
        attrs={"units": "degC"},
    )

    with pytest.warns(UserWarning, match="source time series is incomplete"):
        res_default = icclim.index(
            in_files=tas,
            index_name="SU",
            threshold="> 25 degC",
            slice_mode="year",
            logs_verbosity="SILENT",
        )
    assert np.isnan(res_default.SU.values[0])

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        res_monthly = icclim.index(
            in_files=tas,
            index_name="SU",
            threshold="> 25 degC",
            slice_mode="month",
            logs_verbosity="SILENT",
        )
    incomplete_warnings = [
        w for w in caught if "source time series is incomplete" in str(w.message)
    ]
    assert len(incomplete_warnings) == 1
    assert np.isnan(res_monthly.SU.sel(time="2001-04").values[0])
    assert np.isnan(res_monthly.SU.sel(time="2001-05").values[0])
    assert np.isnan(res_monthly.SU.sel(time="2001-06").values[0])

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        res_strict = icclim.index(
            in_files=tas,
            index_name="SU",
            threshold="> 25 degC",
            slice_mode="year",
            allow_missing_periods=False,
            logs_verbosity="SILENT",
        )
    assert np.isnan(res_strict.SU.values[0])
    assert not any("source time series is incomplete" in str(w.message) for w in caught)

    res_allowed = icclim.index(
        in_files=tas,
        index_name="SU",
        threshold="> 25 degC",
        slice_mode="year",
        allow_missing_periods=True,
        logs_verbosity="SILENT",
    )
    assert res_allowed.SU.values[0] == len(time)


if __name__ == "__main__":
    test_allow_partial_seasons()
