"""Golden results for non-bootstrap paths targeted by performance work."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import xarray as xr

from icclim._core.climate_variable import ClimateVariable
from icclim._core.generic.functions import (
    _reduce_and_diff_of_resampled_x_by_groupedby_y,
    count_occurrences,
    max_consecutive_occurrence,
    max_of_rolling_average,
    max_of_rolling_sum,
    maximum,
    minimum,
)
from icclim._core.model.logical_link import LogicalLinkRegistry
from icclim._core.model.standard_variable import StandardVariableRegistry
from icclim.frequency import FrequencyRegistry
from icclim.threshold.factory import build_threshold


def _climate_variable(
    values: list[float],
    threshold: str | None = None,
) -> ClimateVariable:
    data = xr.DataArray(
        np.asarray(values, dtype=float)[:, np.newaxis],
        dims=("time", "station"),
        coords={
            "time": pd.date_range("2000-01-01", periods=len(values), freq="D"),
            "station": ["A"],
        },
        attrs={"units": "degC"},
    )
    return ClimateVariable(
        name="tas",
        standard_var=StandardVariableRegistry.TAS,
        studied_data=data,
        threshold=build_threshold(threshold) if threshold is not None else None,
        source_frequency=FrequencyRegistry.DAY,
        global_metadata={},
    )


def test_count_occurrences_date_event_golden() -> None:
    result = count_occurrences(
        climate_vars=[_climate_variable([1, 3, 2, 4, 0], ">= 3 degC")],
        resample_freq=FrequencyRegistry.MONTH,
        logical_link=LogicalLinkRegistry.LOGICAL_AND,
        date_event=True,
        to_percent=False,
    ).compute()

    np.testing.assert_array_equal(result.values, [2])
    assert result.event_date_start.item() == pd.Timestamp("2000-01-02")
    assert result.event_date_end.item() == pd.Timestamp("2000-01-04")


@pytest.mark.parametrize(
    ("reducer", "event_date"),
    [
        (maximum, "2000-01-02"),
        (minimum, "2000-01-05"),
    ],
)
def test_extreme_date_event_golden_preserves_period_sum(
    reducer,
    event_date: str,
) -> None:
    result = reducer(
        climate_vars=[_climate_variable([1, 4, 2, 3, 0])],
        resample_freq=FrequencyRegistry.MONTH,
        date_event=True,
    ).compute()

    # This surprising legacy value is the period sum, not the requested extreme.
    # Performance refactors must preserve it until a dedicated correctness change.
    np.testing.assert_array_equal(result.values, [[10.0]])
    assert result.event_date.item() == pd.Timestamp(event_date)


@pytest.mark.parametrize("run_index", ["first", "last"])
def test_consecutive_occurrences_date_event_golden(run_index: str) -> None:
    result = max_consecutive_occurrence(
        climate_vars=[
            _climate_variable([3, 3, 0, 4, 4, 4, 0], ">= 3 degC"),
        ],
        resample_freq=FrequencyRegistry.MONTH,
        logical_link=LogicalLinkRegistry.LOGICAL_AND,
        date_event=True,
        source_freq_delta=np.timedelta64(1, "D"),
        run_index=run_index,
    ).compute()

    np.testing.assert_array_equal(result.values, [3.0])
    assert result.event_date_start.item() == pd.Timestamp("2000-01-04")
    assert result.event_date_end.item() == pd.Timestamp("2000-01-07")


@pytest.mark.parametrize(
    ("reducer", "expected"),
    [
        (max_of_rolling_sum, 12.0),
        (max_of_rolling_average, 4.0),
    ],
)
def test_rolling_reducer_golden(reducer, expected: float) -> None:
    result = reducer(
        climate_vars=[_climate_variable([1, 2, 3, 4, 5, 0, 1])],
        resample_freq=FrequencyRegistry.MONTH,
        rolling_window_width=3,
        date_event=False,
        source_freq_delta=np.timedelta64(1, "D"),
    ).compute()

    np.testing.assert_array_equal(result.values, [[expected]])


@pytest.mark.parametrize("reducer", [max_of_rolling_sum, max_of_rolling_average])
def test_rolling_date_event_golden_is_currently_unsupported(reducer) -> None:
    with pytest.raises(NotImplementedError, match="unknown reducer"):
        reducer(
            climate_vars=[_climate_variable([1, 2, 3, 4, 5, 0, 1])],
            resample_freq=FrequencyRegistry.MONTH,
            rolling_window_width=3,
            date_event=True,
            source_freq_delta=np.timedelta64(1, "D"),
        )


def _reference_diff_inputs() -> tuple[xr.DataArray, xr.DataArray]:
    reference_time = pd.to_datetime(
        [
            *pd.date_range("2000-01-01", "2000-02-29"),
            *pd.date_range("2001-01-01", "2001-02-28"),
        ],
    )
    reference = xr.DataArray(
        reference_time.month * 10 + reference_time.day,
        dims="time",
        coords={"time": reference_time},
        attrs={"units": "degC"},
    ).astype(float)
    study_time = pd.date_range("2002-01-01", "2002-02-28")
    study = xr.DataArray(
        study_time.month * 10 + study_time.day + 5,
        dims="time",
        coords={"time": study_time},
        attrs={"units": "degC"},
    ).astype(float)
    return study, reference


@pytest.mark.parametrize("to_percent", [False, True])
def test_daily_reference_diff_golden(to_percent: bool) -> None:
    study, reference = _reference_diff_inputs()
    study = study.sel(time=slice("2002-01-01", "2002-01-03"))
    result = _reduce_and_diff_of_resampled_x_by_groupedby_y(
        FrequencyRegistry.DAY,
        to_percent,
        study,
        reference,
        reducer=lambda value: value.mean(dim="time"),
    ).compute()

    expected = (
        np.asarray([5 / 11, 5 / 12, 5 / 13]) * 100 if to_percent else np.full(3, 5.0)
    )
    np.testing.assert_allclose(result.values, expected)
    np.testing.assert_array_equal(
        result.time.values,
        pd.date_range("2002-01-01", periods=3).values,
    )


@pytest.mark.parametrize(
    ("to_percent", "expected"),
    [
        (False, [5.0, 4.745614035087719]),
        (True, [19.230769230769234, 13.65471983846542]),
    ],
)
def test_monthly_reference_diff_golden(
    to_percent: bool,
    expected: list[float],
) -> None:
    study, reference = _reference_diff_inputs()
    result = _reduce_and_diff_of_resampled_x_by_groupedby_y(
        FrequencyRegistry.MONTH,
        to_percent,
        study,
        reference,
        reducer=lambda value: value.mean(dim="time"),
    ).compute()

    np.testing.assert_allclose(result.values, expected)
    np.testing.assert_array_equal(
        result.time.values,
        pd.to_datetime(["2002-01-01", "2002-02-01"]).values,
    )
