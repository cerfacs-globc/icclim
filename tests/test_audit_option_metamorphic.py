"""Cross-option and metamorphic checks added by the post-7.3 audit."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim


def _cube() -> xr.DataArray:
    values = np.arange(2 * 3 * 730, dtype=float).reshape(730, 2, 3) % 17
    return xr.DataArray(
        values,
        dims=("time", "lat", "lon"),
        coords={
            "time": pd.date_range("2000-01-01", periods=730, freq="D"),
            "lat": [40, 50],
            "lon": [0, 10, 20],
        },
        attrs={"units": "degC"},
        name="tas",
    )


@pytest.mark.parametrize("slice_mode", ["month", "year", "DJF", "ONDJFM"])
@pytest.mark.parametrize("time_chunk", [31, 90, 365])
def test_count_eager_equals_multiple_dask_chunkings(
    slice_mode: str, time_chunk: int
) -> None:
    data = _cube()
    kwargs = {
        "threshold": "> 8 degC",
        "slice_mode": slice_mode,
        "allow_missing_periods": True,
        "allow_partial_seasons": True,
    }
    eager = icclim.count_occurrences(data, **kwargs).count_occurrences
    chunked = icclim.count_occurrences(
        data.chunk({"time": time_chunk, "lat": 1, "lon": 2}), **kwargs
    ).count_occurrences
    xr.testing.assert_allclose(eager.compute(), chunked.compute())


@pytest.mark.parametrize("calendar", ["standard", "noleap", "360_day", "all_leap"])
def test_count_eager_equals_chunked_on_cf_calendars(calendar: str) -> None:
    days = 360 if calendar == "360_day" else 365
    time = xr.date_range(
        "2001-01-01", periods=days, freq="D", calendar=calendar, use_cftime=True
    )
    data = xr.DataArray(
        np.arange(days) % 5,
        dims="time",
        coords={"time": time},
        attrs={"units": "degC"},
    )
    kwargs = {
        "threshold": ">= 2 degC",
        "slice_mode": "year",
        "allow_missing_periods": True,
    }
    eager = icclim.count_occurrences(data, **kwargs).count_occurrences
    chunked = icclim.count_occurrences(
        data.chunk({"time": 30}), **kwargs
    ).count_occurrences
    xr.testing.assert_allclose(eager.compute(), chunked.compute())


def test_count_is_invariant_to_equal_data_and_threshold_offset() -> None:
    data = _cube()
    original = icclim.count_occurrences(
        data,
        threshold="> 8 degC",
        slice_mode="year",
        allow_missing_periods=True,
    ).count_occurrences
    shifted = icclim.count_occurrences(
        data + 100,
        threshold="> 108 degC",
        slice_mode="year",
        allow_missing_periods=True,
    ).count_occurrences
    xr.testing.assert_equal(original, shifted)


def test_spatial_dimension_permutation_only_permutates_result() -> None:
    data = _cube()
    kwargs = {
        "threshold": "> 8 degC",
        "slice_mode": "year",
        "allow_missing_periods": True,
    }
    original = icclim.count_occurrences(data, **kwargs).count_occurrences
    permuted = icclim.count_occurrences(
        data.transpose("time", "lon", "lat"), **kwargs
    ).count_occurrences
    xr.testing.assert_equal(original, permuted.transpose(*original.dims))


def test_per_period_result_equals_same_period_from_full_run() -> None:
    data = _cube()
    kwargs = {
        "threshold": "> 8 degC",
        "slice_mode": "year",
        "allow_missing_periods": True,
    }
    full = icclim.count_occurrences(data, **kwargs).count_occurrences
    second_year = icclim.count_occurrences(
        data.sel(time=slice("2001-01-01", "2001-12-31")), **kwargs
    ).count_occurrences
    xr.testing.assert_equal(full.isel(time=slice(1, 2)), second_year)
