"""The 365 -> 366 day interpolation of calendar-day percentiles must be exact."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import xarray as xr
from xclim.core.calendar import adjust_doy_calendar

import icclim
from icclim._core.generic.threshold.percentile import _adjust_doy_calendar_exact


def _target() -> xr.DataArray:
    time = pd.date_range("2000-01-01", "2004-12-31", freq="D")  # has leap years
    return xr.DataArray(np.zeros(len(time)), dims="time", coords={"time": time})


def _source(values: np.ndarray) -> xr.DataArray:
    return xr.DataArray(
        values,
        dims=("x", "dayofyear"),
        coords={"dayofyear": np.arange(1, 366)},
        attrs={"units": "K"},
    )


@pytest.mark.parametrize("chunked", [False, True])
def test_constant_percentiles_stay_exactly_constant(chunked: bool) -> None:
    # Interpolating between equal values must not create rounding noise:
    # observations tying with the threshold would flip a `>` comparison.
    source = _source(np.full((2, 365), 10.0))
    if chunked:
        source = source.chunk({"x": 1, "dayofyear": 100})

    result = _adjust_doy_calendar_exact(source, _target()).compute()

    assert result.sizes["dayofyear"] == 366
    assert (result.values == 10.0).all()


@pytest.mark.parametrize("chunked", [False, True])
def test_matches_xclim_adjustment_and_keeps_layout(chunked: bool) -> None:
    rng = np.random.default_rng(0)
    source = _source(rng.normal(15, 5, (2, 365)))
    if chunked:
        source = source.chunk({"x": 1, "dayofyear": 100})

    result = _adjust_doy_calendar_exact(source, _target())
    expected = adjust_doy_calendar(source, _target())

    assert result.dims == source.dims
    assert result.attrs["units"] == "K"
    np.testing.assert_allclose(result.compute(), expected.compute(), rtol=1e-12)
    np.testing.assert_array_equal(result.dayofyear, np.arange(1, 367))


def test_calendar_with_same_length_is_unchanged() -> None:
    time = pd.date_range("2001-01-01", "2002-12-31", freq="D")  # 365 days only
    target = xr.DataArray(np.zeros(len(time)), dims="time", coords={"time": time})
    source = _source(np.arange(730.0).reshape(2, 365))

    result = _adjust_doy_calendar_exact(source, target)

    np.testing.assert_array_equal(result.values, source.values)


def test_constant_series_never_exceeds_its_percentile_in_a_leap_year() -> None:
    # A constant series ties with every calendar-day percentile, so no day can be
    # strictly above it. With SciPy 1.18.1 the 365-day thresholds became 300.15 plus
    # or minus rounding noise for the leap year (xclim's resample_doy), which created
    # spurious exceedance days (up to 6 per month).
    time = pd.date_range("2042-01-01", periods=365 * 5 + 1, freq="D")
    tas = xr.DataArray(
        np.full((len(time), 1, 1), 300.15),
        dims=["time", "lat", "lon"],
        coords={"time": time, "lat": [0], "lon": [0]},
        attrs={"units": "K"},
    )

    result = icclim.index(
        index_name="tx90p",
        in_files=tas,
        doy_window_width=1,
        base_period_time_range=("2042-01-01", "2042-12-31"),
        time_range=("2043-01-01", "2045-12-31"),  # 2044 is a leap year
        slice_mode="month",
        out_file=None,
    )

    assert (result.TX90p.compute().values == 0).all()
