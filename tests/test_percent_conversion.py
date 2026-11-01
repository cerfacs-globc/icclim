"""Regression tests for count-occurrence percentage conversion."""

from __future__ import annotations

import numpy as np
import pandas as pd
import xarray as xr

import icclim


def test_count_occurrences_percent_scales_annual_fraction_by_100() -> None:
    data = xr.DataArray(
        np.ones(365),
        dims="time",
        coords={"time": pd.date_range("2001-01-01", periods=365, freq="D")},
        attrs={"units": "degC"},
    )

    result = icclim.count_occurrences(
        in_files=data,
        threshold="> 0 degC",
        slice_mode="year",
        out_unit="%",
        allow_missing_periods=True,
    )

    np.testing.assert_allclose(result.count_occurrences.values, [100.0])
