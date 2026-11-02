"""Regression tests for percentage output on fixed CF calendars."""

import numpy as np
import xarray as xr

import icclim


def _annual_percent(calendar: str, days: int, years: int = 1) -> xr.DataArray:
    time = xr.date_range(
        "2001-01-01",
        periods=years * days,
        freq="D",
        calendar=calendar,
        use_cftime=True,
    )
    data = xr.DataArray(
        np.ones(len(time)),
        dims="time",
        coords={"time": time},
        attrs={"units": "degC"},
    )
    return icclim.count_occurrences(
        data,
        threshold="> 0 degC",
        slice_mode="year",
        out_unit="%",
        allow_missing_periods=True,
    ).count_occurrences.compute()


def test_count_occurrences_percent_supports_multiple_noleap_years() -> None:
    result = _annual_percent("noleap", 365, years=3)

    assert result.sizes["time"] == 3
    np.testing.assert_allclose(result, result.isel(time=0))


def test_count_occurrences_percent_supports_multiple_all_leap_years() -> None:
    result = _annual_percent("all_leap", 366, years=3)

    assert result.sizes["time"] == 3
    np.testing.assert_allclose(result, result.isel(time=0))


def test_count_occurrences_percent_uses_360_day_year_length() -> None:
    result_360 = _annual_percent("360_day", 360)
    result_365 = _annual_percent("noleap", 365)

    np.testing.assert_allclose(result_360, result_365)
