"""Failing regression tests for bugs confirmed by the post-7.3 audit.

These tests deliberately remain failing on the audit branch.  Each test is an
independent specification suitable for moving to its own bug-fix branch.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import xarray as xr

import icclim
from icclim.threshold.factory import build_threshold


def _daily(
    values: np.ndarray | list[float],
    start: str,
    *,
    units: str,
    calendar: str | None = None,
) -> xr.DataArray:
    if calendar is None:
        time = pd.date_range(start, periods=len(values), freq="D")
    else:
        time = xr.date_range(
            start,
            periods=len(values),
            freq="D",
            calendar=calendar,
            use_cftime=True,
        )
    return xr.DataArray(
        np.asarray(values, dtype=float),
        dims="time",
        coords={"time": time},
        attrs={"units": units},
        name="input",
    )


def test_count_occurrences_percent_scales_annual_fraction_by_100() -> None:
    data = _daily(np.ones(365), "2001-01-01", units="degC")

    result = icclim.count_occurrences(
        in_files=data,
        threshold="> 0 degC",
        slice_mode="year",
        out_unit="%",
        allow_missing_periods=True,
    )

    np.testing.assert_allclose(result.count_occurrences.values, [100.0])


def test_count_occurrences_ondjfm_uses_february_year_for_denominator() -> None:
    data = _daily(np.ones(183), "1999-10-01", units="degC")

    result = icclim.count_occurrences(
        in_files=data,
        threshold="> 0 degC",
        slice_mode="ONDJFM",
        out_unit="%",
        allow_missing_periods=True,
    )

    np.testing.assert_allclose(result.count_occurrences.values, [100.0])


def test_count_occurrences_percent_supports_multiple_noleap_years() -> None:
    data = _daily(np.ones(3 * 365), "2001-01-01", units="degC", calendar="noleap")

    result = icclim.count_occurrences(
        in_files=data,
        threshold="> 0 degC",
        slice_mode="year",
        out_unit="%",
        allow_missing_periods=True,
    )

    np.testing.assert_allclose(result.count_occurrences.values, [100.0] * 3)


def test_count_occurrences_percent_uses_360_day_year_length() -> None:
    data = _daily(np.ones(360), "2001-01-01", units="degC", calendar="360_day")

    result = icclim.count_occurrences(
        in_files=data,
        threshold="> 0 degC",
        slice_mode="year",
        out_unit="%",
        allow_missing_periods=True,
    )

    np.testing.assert_allclose(result.count_occurrences.values, [100.0])


def test_max_consecutive_no_event_has_missing_event_dates() -> None:
    data = _daily(np.zeros(5), "2001-01-01", units="degC")

    result = icclim.max_consecutive_occurrence(
        in_files=data,
        threshold="> 1 degC",
        slice_mode="month",
        date_event=True,
        allow_missing_periods=True,
    ).compute()

    actual = result.max_consecutive_occurrence.isel(time=0)
    assert actual.item() == 0
    assert pd.isna(actual.event_date_start.item())
    assert pd.isna(actual.event_date_end.item())


def test_fraction_of_total_includes_values_equal_to_wet_day_minimum() -> None:
    data = _daily([1, 1, 10, 10], "2001-01-01", units="mm/day")
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

    # The numerator is 20 mm and the inclusive wet-day denominator is 22 mm.
    np.testing.assert_allclose(result.fraction_of_total.values, [20 / 22 * 100])


def test_rolling_sum_accepts_dask_time_chunks_smaller_than_window() -> None:
    data = _daily(np.arange(10), "2001-01-01", units="mm/day")
    expected = pd.Series(np.arange(10)).rolling(3).sum().max()

    result = icclim.max_of_rolling_sum(
        in_files=data.chunk({"time": 2}),
        slice_mode="year",
        rolling_window_width=3,
        allow_missing_periods=True,
    ).compute()

    np.testing.assert_allclose(result.max_of_rolling_sum.values, [expected])
