"""Regression tests for extrema returned with their event dates."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import pytest
import xarray as xr

from icclim._core.climate_variable import ClimateVariable
from icclim._core.generic.functions import (
    max_of_rolling_average,
    max_of_rolling_sum,
    maximum,
    min_of_rolling_average,
    min_of_rolling_sum,
    minimum,
)
from icclim._core.model.standard_variable import StandardVariableRegistry
from icclim.frequency import FrequencyRegistry

if TYPE_CHECKING:
    from collections.abc import Callable


def _climate_variable(
    values: list[float] | list[list[float]],
    *,
    chunked: bool,
) -> ClimateVariable:
    data = np.asarray(values, dtype=float)
    if data.ndim == 1:
        data = data[:, np.newaxis]
    studied_data = xr.DataArray(
        data,
        dims=("time", "station"),
        coords={
            "time": pd.date_range("2000-01-01", periods=len(data), freq="D"),
            "station": np.arange(data.shape[1]),
        },
        attrs={"units": "degC"},
    )
    if chunked:
        studied_data = studied_data.chunk({"time": 4})
    return ClimateVariable(
        name="tas",
        standard_var=StandardVariableRegistry.TAS,
        studied_data=studied_data,
        threshold=None,
        source_frequency=FrequencyRegistry.DAY,
        global_metadata={},
    )


@pytest.mark.parametrize("chunked", [False, True])
@pytest.mark.parametrize(
    ("reducer", "expected_value", "expected_date"),
    [
        (maximum, 4.0, "2000-01-02"),
        (minimum, 0.0, "2000-01-05"),
    ],
)
def test_simple_extreme_returns_value_and_event_date(
    reducer: Callable[..., xr.DataArray],
    expected_value: float,
    expected_date: str,
    chunked: bool,
) -> None:
    result = reducer(
        climate_vars=[_climate_variable([1, 4, 2, 3, 0], chunked=chunked)],
        resample_freq=FrequencyRegistry.MONTH,
        date_event=True,
    ).compute()

    np.testing.assert_array_equal(result.values, [[expected_value]])
    assert result.event_date.item() == pd.Timestamp(expected_date)


@pytest.mark.parametrize("chunked", [False, True])
@pytest.mark.parametrize(
    ("reducer", "expected_value", "expected_start", "expected_end"),
    [
        (max_of_rolling_sum, 12.0, "2000-01-03", "2000-01-05"),
        (max_of_rolling_average, 4.0, "2000-01-03", "2000-01-05"),
        (min_of_rolling_sum, 6.0, "2000-01-01", "2000-01-03"),
        (min_of_rolling_average, 2.0, "2000-01-01", "2000-01-03"),
    ],
)
def test_rolling_extreme_returns_value_and_window_dates(
    reducer: Callable[..., xr.DataArray],
    expected_value: float,
    expected_start: str,
    expected_end: str,
    chunked: bool,
) -> None:
    result = reducer(
        climate_vars=[
            _climate_variable([1, 2, 3, 4, 5, 0, 1], chunked=chunked),
        ],
        resample_freq=FrequencyRegistry.MONTH,
        rolling_window_width=3,
        date_event=True,
        source_freq_delta=np.timedelta64(1, "D"),
    ).compute()

    np.testing.assert_allclose(result.values, [[expected_value]])
    assert result.event_date_start.item() == pd.Timestamp(expected_start)
    assert result.event_date_end.item() == pd.Timestamp(expected_end)


@pytest.mark.parametrize("chunked", [False, True])
@pytest.mark.parametrize("reducer", [maximum, minimum])
def test_all_nan_cell_has_nan_value_and_no_event_date(
    reducer: Callable[..., xr.DataArray],
    chunked: bool,
) -> None:
    result = reducer(
        climate_vars=[
            _climate_variable(
                [[1, np.nan], [4, np.nan], [2, np.nan]],
                chunked=chunked,
            ),
        ],
        resample_freq=FrequencyRegistry.MONTH,
        date_event=True,
    ).compute()

    assert np.isnan(result.isel(time=0, station=1).item())
    assert pd.isna(result.event_date.isel(station=1).item())
