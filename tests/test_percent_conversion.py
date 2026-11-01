"""Regression tests for count-occurrence percentage conversion."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim
from icclim._core.generic.functions import _to_percent
from icclim.frequency import FrequencyRegistry


@pytest.mark.parametrize(
    ("frequency", "timestamp", "period_length"),
    [
        (FrequencyRegistry.MONTH, "2001-01-01", 31),
        (FrequencyRegistry.YEAR, "2001-01-01", 365),
        (FrequencyRegistry.AMJJAS, "2001-04-01", 183),
        (FrequencyRegistry.ONDJFM, "2000-10-01", 182),
        (FrequencyRegistry.DJF, "2000-12-01", 90),
        (FrequencyRegistry.MAM, "2001-03-01", 92),
        (FrequencyRegistry.JJA, "2001-06-01", 92),
        (FrequencyRegistry.SON, "2001-09-01", 91),
    ],
)
def test_every_builtin_percent_branch_scales_to_100(
    frequency,
    timestamp: str,
    period_length: int,
) -> None:
    counts = xr.DataArray(
        [period_length],
        dims="time",
        coords={"time": [pd.Timestamp(timestamp)]},
    )

    result = _to_percent(counts, frequency)

    np.testing.assert_allclose(result.values, [100.0])


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


@pytest.mark.parametrize(("slice_mode", "periods"), [("day", 2), ("10D", 20)])
def test_custom_daily_frequency_uses_actual_period_length(
    slice_mode: str,
    periods: int,
) -> None:
    data = xr.DataArray(
        np.ones(periods),
        dims="time",
        coords={"time": pd.date_range("2001-01-01", periods=periods, freq="D")},
        attrs={"units": "degC"},
    )

    result = icclim.count_occurrences(
        in_files=data,
        threshold="> 0 degC",
        slice_mode=slice_mode,
        out_unit="%",
        allow_missing_periods=True,
    )

    np.testing.assert_allclose(result.count_occurrences.values, 100.0)
