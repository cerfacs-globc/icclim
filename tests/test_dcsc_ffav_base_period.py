"""
DCSC FFAV, the difference of the mean wind speed to a reference period (issue #673).

The study period and the reference period come from the same input series. The
reference calculation below is written with numpy only.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim

CALENDARS = ("standard", "noleap", "360_day", "all_leap")


def _wind_cube(unit: str = "m s-1") -> xr.DataArray:
    """Three years of deterministic daily wind speed on 2x2 grid points."""
    time = pd.date_range("2000-01-01", "2002-12-31", freq="D")
    rng = np.random.default_rng(20261114)
    values = rng.weibull(2.2, (len(time), 2, 2)) * 7.0
    values[time.year == 2001] += 1.0
    values[time.year == 2002] -= 0.5
    values[time == pd.Timestamp("2002-05-05"), 1, 0] = np.nan
    data = values * 3.6 if unit == "km h-1" else values
    return xr.DataArray(
        data,
        dims=("time", "lat", "lon"),
        coords={"time": time, "lat": [45.0, 46.0], "lon": [1.0, 2.0]},
        name="sfcWind",
        attrs={"units": unit},
    )


def _in_calendar(source: xr.DataArray, calendar: str) -> xr.DataArray:
    if calendar == "standard":
        return source
    return source.convert_calendar(calendar, align_on="date", missing=np.nan)


def _reference(values: np.ndarray, years: np.ndarray) -> np.ndarray:
    """Yearly mean of 2001 and 2002 minus the mean of 2000."""
    base = np.nanmean(values[years == 2000], axis=0)
    return np.stack(
        [np.nanmean(values[years == y], axis=0) - base for y in (2001, 2002)]
    )


def _ffav(source: xr.DataArray, **kwargs) -> xr.DataArray:
    options = {
        "base_period_time_range": ["2000-01-01", "2000-12-31"],
        "time_range": ["2001-01-01", "2002-12-31"],
        "out_file": None,
        "completeness": "none",
        "logs_verbosity": "SILENT",
    }
    options.update(kwargs)
    return icclim.dcsc.ffav(source, **options).FFAV.compute()


def test_reproducer_of_issue_673() -> None:
    time = pd.date_range("2000-01-01", "2001-12-31")
    values = np.where(time.year == 2000, 5.0, 7.0)
    wind = xr.DataArray(
        values,
        dims="time",
        coords={"time": time},
        name="sfcWind",
        attrs={"units": "m s-1"},
    )
    actual = _ffav(wind, time_range=["2001-01-01", "2001-12-31"])
    np.testing.assert_allclose(actual.values, [2.0])
    assert actual.attrs["units"] == "m s-1"


@pytest.mark.parametrize(
    "chunk_size", [None, 1, 7, -1], ids=["eager", "time1", "time7", "full"]
)
@pytest.mark.parametrize("unit", ["m s-1", "km h-1"])
def test_ffav_matches_the_reference_calculation(
    unit: str, chunk_size: int | None
) -> None:
    source = _wind_cube(unit)
    if chunk_size is not None:
        size = source.sizes["time"] if chunk_size == -1 else chunk_size
        source = source.chunk({"time": size})
    actual = _ffav(source)
    values = source.compute().values / (3.6 if unit == "km h-1" else 1.0)
    expected = _reference(values, np.asarray(source.time.dt.year.values))
    np.testing.assert_allclose(
        actual.transpose("time", "lat", "lon").values,
        expected,
        rtol=1e-6,
        equal_nan=True,
    )


@pytest.mark.parametrize("calendar", CALENDARS)
def test_ffav_on_standard_and_cftime_calendars(calendar: str) -> None:
    source = _in_calendar(_wind_cube(), calendar)
    actual = _ffav(
        source,
        base_period_time_range=["2000-01-01", "2000-12-30"],
        time_range=["2001-01-01", "2002-12-30"],
    )
    assert actual.sizes["time"] == 2
    # The reference period and the study period end on 30 December, which is the last
    # day of the 360_day years: 31 December 2000 and 2002 are not in the periods.
    values = source.values
    years = np.asarray(source.time.dt.year.values)
    not_31_december = ~(
        (source.time.dt.month == 12) & (source.time.dt.day == 31)
    ).values
    base = np.nanmean(values[(years == 2000) & not_31_december], axis=0)
    expected = np.stack(
        [
            np.nanmean(values[years == 2001], axis=0) - base,
            np.nanmean(values[(years == 2002) & not_31_december], axis=0) - base,
        ]
    )
    np.testing.assert_allclose(
        actual.transpose("time", "lat", "lon").values,
        expected,
        rtol=1e-6,
        equal_nan=True,
    )


@pytest.mark.parametrize("slice_mode", ["month", "DJF"])
def test_monthly_and_seasonal_outputs_have_metadata(slice_mode: str) -> None:
    kwargs = {"slice_mode": slice_mode}
    if slice_mode == "DJF":
        kwargs["allow_partial_seasons"] = True
    actual = _ffav(_wind_cube(), **kwargs)
    assert "time" in actual.dims
    assert actual.time.size > 0
    assert actual.attrs.get("units")
    assert actual.attrs.get("long_name")
    assert actual.attrs.get("standard_name")


def test_time_range_subset_equals_full_result_slice() -> None:
    source = _wind_cube()
    full = _ffav(source)
    subset = _ffav(source, time_range=["2002-01-01", "2002-12-31"])
    xr.testing.assert_allclose(subset, full.sel(time=slice("2002-01-01", "2002-12-31")))


def test_strict_completeness_masks_a_whole_missing_grid_point() -> None:
    source = _wind_cube().copy(deep=True)
    source.loc[{"lat": 45.0, "lon": 1.0}] = np.nan
    actual = _ffav(source, completeness="strict")
    assert actual.sel(lat=45.0, lon=1.0).isnull().all()
