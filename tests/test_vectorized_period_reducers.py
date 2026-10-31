"""Laziness regressions for vectorized per-period reducers."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import xarray as xr
from dask.callbacks import Callback
from xarray.core.resample import DataArrayResample

from icclim._core.generic.functions import (
    _consecutive_occurrences_with_dates,
    _count_occurrences_with_date,
    _reduce_and_diff_of_resampled_x_by_groupedby_y,
    _reduce_with_date_event,
)
from icclim.frequency import FrequencyRegistry


class _SchedulerCounter(Callback):
    def __init__(self) -> None:
        super().__init__()
        self.starts = 0

    def _start(self, dsk: Any) -> None:
        self.starts += 1


def _data(values: list[list[float]]) -> xr.DataArray:
    return xr.DataArray(
        np.asarray(values, dtype=float),
        dims=("time", "station"),
        coords={
            "time": pd.date_range("2000-01-01", periods=len(values), freq="D"),
            "station": ["event", "empty"],
        },
        attrs={"units": "1"},
    ).chunk({"time": 2, "station": 1})


def test_extreme_date_event_builds_without_scheduler_call() -> None:
    source = _data([[1, np.nan], [4, np.nan], [2, np.nan]])
    counter = _SchedulerCounter()

    with counter:
        result = _reduce_with_date_event(
            source.resample(time="MS"),
            DataArrayResample.max,
        )

    assert counter.starts == 0
    assert result.chunks is not None
    actual = result.compute()
    np.testing.assert_array_equal(actual.isel(station=0), [4])
    assert actual.event_date.isel(station=0).item() == pd.Timestamp("2000-01-02")
    assert pd.isna(actual.event_date.isel(station=1).item())


def test_count_event_dates_remain_lazy_and_handle_empty_cells() -> None:
    mask = _data([[1, 0], [0, 0], [1, 0], [0, 0]]).astype(bool)
    counter = _SchedulerCounter()

    with counter:
        result = _count_occurrences_with_date(mask.resample(time="MS"))

    assert counter.starts == 0
    assert result.chunks is not None
    actual = result.compute()
    np.testing.assert_array_equal(actual.values, [[2, 0]])
    assert actual.event_date_start.isel(station=0).item() == pd.Timestamp("2000-01-01")
    assert actual.event_date_end.isel(station=0).item() == pd.Timestamp("2000-01-03")
    assert pd.isna(actual.event_date_start.isel(station=1).item())
    assert pd.isna(actual.event_date_end.isel(station=1).item())


def test_consecutive_event_dates_build_without_scheduler_call() -> None:
    run_lengths = _data([[0, 0], [3, 0], [0, 0], [0, 0]])
    counter = _SchedulerCounter()

    with counter:
        result = _consecutive_occurrences_with_dates(
            run_lengths.resample(time="MS"),
            np.timedelta64(1, "D"),
            "first",
        )

    assert counter.starts == 0
    assert result.chunks is not None
    actual = result.compute()
    np.testing.assert_array_equal(actual.values, [[3, 0]])
    assert actual.event_date_start.isel(station=0).item() == pd.Timestamp("2000-01-02")
    assert actual.event_date_end.isel(station=0).item() == pd.Timestamp("2000-01-05")


def test_reference_diff_reduces_all_periods_in_one_lazy_graph() -> None:
    reference = xr.DataArray(
        np.arange(1, 367, dtype=float),
        dims="time",
        coords={"time": pd.date_range("2000-01-01", periods=366)},
        attrs={"units": "K"},
    ).chunk({"time": 31})
    study = xr.DataArray(
        [6.0, 7.0, 8.0],
        dims="time",
        coords={"time": pd.date_range("2001-01-01", periods=3)},
        attrs={"units": "K"},
    ).chunk({"time": 2})
    counter = _SchedulerCounter()

    with counter:
        result = _reduce_and_diff_of_resampled_x_by_groupedby_y(
            FrequencyRegistry.DAY,
            False,
            study,
            reference,
            reducer=lambda values: values.mean(dim="time"),
        )

    assert counter.starts == 0
    assert result.chunks is not None
    np.testing.assert_allclose(result.compute(), [5.0, 5.0, 5.0])
