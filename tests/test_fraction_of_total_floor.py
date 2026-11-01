"""Regression tests for percentile fraction wet-day floors."""

from __future__ import annotations

import numpy as np
import pandas as pd
import xarray as xr

import icclim
from icclim.threshold.factory import build_threshold


def test_fraction_of_total_includes_values_equal_to_wet_day_minimum() -> None:
    data = xr.DataArray(
        [1, 1, 10, 10],
        dims="time",
        coords={"time": pd.date_range("2001-01-01", periods=4, freq="D")},
        attrs={"units": "mm/day"},
        name="pr",
    )
    threshold = build_threshold(
        "> 50 period_per",
        reference_period=("2001-01-01", "2001-01-04"),
        threshold_min_value="1 mm/day",
    )

    result = icclim.fraction_of_total(
        in_files=data,
        threshold=threshold,
        slice_mode="year",
        out_unit="%",
        allow_missing_periods=True,
    )

    np.testing.assert_allclose(result.fraction_of_total.values, [20 / 22 * 100])
