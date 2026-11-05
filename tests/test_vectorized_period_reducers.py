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



def _ts(da):
    """Single timestamp of a one-cell array, independent of numpy/xarray version."""
    return pd.Timestamp(np.asarray(da.values).ravel()[0])

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
    assert _ts(actual.event_date.isel(station=0)) == pd.Timestamp("2000-01-02")
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
    assert _ts(actual.event_date_start.isel(station=0)) == pd.Timestamp("2000-01-01")
    assert _ts(actual.event_date_end.isel(station=0)) == pd.Timestamp("2000-01-03")
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
    assert _ts(actual.event_date_start.isel(station=0)) == pd.Timestamp("2000-01-02")
    assert _ts(actual.event_date_end.isel(station=0)) == pd.Timestamp("2000-01-05")


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


def _nan_run_lengths() -> xr.DataArray:
    # Month 1: one run of 3 days. Month 2: only missing values (no run).
    values = np.full((59, 1), np.nan)
    values[1, 0] = 3
    return xr.DataArray(
        values,
        dims=("time", "station"),
        coords={
            "time": pd.date_range("2000-01-01", periods=59, freq="D"),
            "station": ["a"],
        },
        attrs={"units": "1"},
    )


def test_consecutive_period_without_run_is_zero_not_nan() -> None:
    result = _consecutive_occurrences_with_dates(
        _nan_run_lengths().resample(time="MS"),
        np.timedelta64(1, "D"),
        "first",
    ).compute()

    # independent expectation: max of the non-missing run lengths, else 0
    np.testing.assert_array_equal(result.values, [[3.0], [0.0]])
    assert _ts(result.event_date_start.isel(station=0, time=0)) == pd.Timestamp(
        "2000-01-02"
    )
    assert pd.isna(result.event_date_start.isel(station=0, time=1).item())
    assert pd.isna(result.event_date_end.isel(station=0, time=1).item())


def _time_last(da: xr.DataArray) -> xr.DataArray:
    return da.transpose("station", "time")


def test_date_event_outputs_keep_time_first_with_time_last_input() -> None:
    source = _time_last(_data([[1, 2], [4, 1], [2, 2]]))
    mask = source > 1
    runs = _time_last(_data([[0, 0], [3, 0], [0, 0]]))

    results = {
        "extreme": _reduce_with_date_event(
            source.resample(time="MS"), DataArrayResample.max
        ),
        "count": _count_occurrences_with_date(mask.resample(time="MS")),
        "consecutive": _consecutive_occurrences_with_dates(
            runs.resample(time="MS"), np.timedelta64(1, "D"), "first"
        ),
    }

    for name, result in results.items():
        assert result.dims == ("time", "station"), name
        for coord in result.coords:
            if coord.startswith("event_date"):
                assert result[coord].dims == ("time", "station"), (name, coord)


def test_count_event_date_is_missing_when_no_occurrence() -> None:
    # Behaviour change: a period with 0 occurrences used to report the first and
    # last day of the period as event dates; it now reports no date.
    mask = _data([[0, 0], [0, 0], [0, 0]]).astype(bool)

    result = _count_occurrences_with_date(mask.resample(time="MS")).compute()

    np.testing.assert_array_equal(result.values, [[0, 0]])
    assert result.event_date_start.isnull().all()
    assert result.event_date_end.isnull().all()
