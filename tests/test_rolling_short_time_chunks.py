"""Regression tests for #526: rolling indices on Dask chunks shorter than the window."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim
from icclim._core.generic.functions import _ensure_time_chunks_cover_window


def _daily(values: np.ndarray, units: str) -> xr.DataArray:
    return xr.DataArray(
        np.asarray(values, dtype=float),
        dims="time",
        coords={"time": pd.date_range("2001-01-01", periods=len(values), freq="D")},
        attrs={"units": units},
        name="input",
    )


def test_rolling_sum_accepts_dask_time_chunks_smaller_than_window() -> None:
    data = _daily(np.arange(10), "mm/day")
    expected = pd.Series(np.arange(10)).rolling(3).sum().max()

    result = icclim.max_of_rolling_sum(
        in_files=data.chunk({"time": 2}),
        slice_mode="year",
        rolling_window_width=3,
        allow_missing_periods=True,
    ).compute()

    np.testing.assert_allclose(result.max_of_rolling_sum.values, [expected])


@pytest.mark.parametrize("chunk", [1, 2, 3, 4, 7, 100])
@pytest.mark.parametrize("window", [3, 5])
def test_rolling_results_do_not_depend_on_time_chunks(chunk: int, window: int) -> None:
    rng = np.random.default_rng(42)
    values = rng.random(23) * 10
    data = _daily(values, "mm/day")
    rolled = pd.Series(values).rolling(window)

    result_sum = icclim.max_of_rolling_sum(
        in_files=data.chunk({"time": chunk}),
        slice_mode="year",
        rolling_window_width=window,
        allow_missing_periods=True,
    ).compute()
    result_avg = icclim.min_of_rolling_average(
        in_files=data.chunk({"time": chunk}),
        slice_mode="year",
        rolling_window_width=window,
        allow_missing_periods=True,
    ).compute()

    np.testing.assert_allclose(
        result_sum.max_of_rolling_sum.values, [rolled.sum().max()]
    )
    np.testing.assert_allclose(
        result_avg.min_of_rolling_average.values, [rolled.mean().min()]
    )


def test_rolling_with_threshold_on_short_chunks() -> None:
    values = np.array([0, 5, 5, 0, 5, 5, 5, 0, 0, 5], dtype=float)
    data = _daily(values, "mm/day")
    masked = pd.Series(np.where(values > 1, values, np.nan))
    expected = masked.rolling(3).sum().max()

    result = icclim.max_of_rolling_sum(
        in_files=data.chunk({"time": 2}),
        threshold="> 1 mm/day",
        slice_mode="year",
        rolling_window_width=3,
        allow_missing_periods=True,
    ).compute()

    np.testing.assert_allclose(result.max_of_rolling_sum.values, [expected])


def test_native_chunks_are_kept_when_not_shorter_than_window() -> None:
    data = _daily(np.arange(20), "mm/day").chunk({"time": 5})

    assert _ensure_time_chunks_cover_window(data, 3).chunksizes["time"] == (5,) * 4


def test_short_chunks_are_rechunked_evenly_and_not_below_window() -> None:
    data = _daily(np.arange(10), "mm/day").chunk({"time": 2})

    sizes = _ensure_time_chunks_cover_window(data, 3).chunksizes["time"]

    assert sum(sizes) == 10
    assert min(sizes) >= 3


def test_eager_input_is_untouched() -> None:
    data = _daily(np.arange(10), "mm/day")

    assert _ensure_time_chunks_cover_window(data, 3) is data
