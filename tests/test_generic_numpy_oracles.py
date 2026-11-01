"""Independent NumPy/pandas value oracles for every public generic indicator."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim

if TYPE_CHECKING:
    from collections.abc import Callable


VALUES = np.array([1, 4, 2, 3, 0, 5, 5, 1, 2, 4], dtype=float)
REFERENCE = np.array([0, 1, 1, 1, 2, 2, 3, 3, 5, 1], dtype=float)


def _data(values: np.ndarray = VALUES, *, units: str = "degC") -> xr.DataArray:
    return xr.DataArray(
        values,
        dims="time",
        coords={"time": pd.date_range("2001-01-01", periods=len(values), freq="D")},
        attrs={"units": units},
        name="pr" if units == "mm/day" else "tas",
    )


def _value(result: xr.Dataset, name: str) -> np.ndarray:
    return result[name].compute().values


@pytest.mark.parametrize(
    ("name", "oracle"),
    [
        ("maximum", np.max),
        ("minimum", np.min),
        ("average", np.mean),
        ("standard_deviation", np.std),
    ],
)
def test_simple_reducer_matches_numpy(
    name: str,
    oracle: Callable[[np.ndarray], float],
) -> None:
    result = getattr(icclim, name)(
        in_files=_data(), slice_mode="month", allow_missing_periods=True
    )
    np.testing.assert_allclose(_value(result, name), [oracle(VALUES)])


def test_sum_matches_numpy() -> None:
    result = icclim.sum(
        in_files=_data(units="mm/day"),
        slice_mode="month",
        allow_missing_periods=True,
    )
    np.testing.assert_allclose(_value(result, "sum"), [VALUES.sum()])


@pytest.mark.parametrize(
    ("name", "reducer"),
    [
        ("max_of_rolling_sum", "max"),
        ("min_of_rolling_sum", "min"),
        ("max_of_rolling_average", "max"),
        ("min_of_rolling_average", "min"),
    ],
)
def test_rolling_reducer_matches_pandas(name: str, reducer: str) -> None:
    rolling = pd.Series(VALUES).rolling(3)
    samples = rolling.sum() if name.endswith("sum") else rolling.mean()
    expected = getattr(samples, reducer)()
    result = getattr(icclim, name)(
        in_files=_data(),
        slice_mode="month",
        rolling_window_width=3,
        allow_missing_periods=True,
    )
    np.testing.assert_allclose(_value(result, name), [expected])


@pytest.mark.parametrize(
    ("name", "kwargs", "expected"),
    [
        ("count_occurrences", {}, np.count_nonzero(VALUES > 2)),
        ("max_consecutive_occurrence", {}, 2),
        ("sum_of_spell_lengths", {"min_spell_length": 2}, 2),
    ],
)
def test_threshold_count_reducer_matches_numpy(
    name: str, kwargs: dict[str, int], expected: float
) -> None:
    result = getattr(icclim, name)(
        in_files=_data(),
        threshold="> 2 degC",
        slice_mode="month",
        allow_missing_periods=True,
        **kwargs,
    )
    np.testing.assert_allclose(_value(result, name), [expected])


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("excess", np.maximum(VALUES - 2, 0).sum()),
        ("deficit", np.maximum(2 - VALUES, 0).sum()),
    ],
)
def test_distance_from_threshold_matches_numpy(name: str, expected: float) -> None:
    result = getattr(icclim, name)(
        in_files=_data(),
        threshold="2 degC",
        slice_mode="month",
        allow_missing_periods=True,
    )
    np.testing.assert_allclose(_value(result, name), [expected])


def test_fraction_of_total_matches_numpy() -> None:
    result = icclim.fraction_of_total(
        in_files=_data(units="mm/day"),
        threshold="> 2 mm/day",
        slice_mode="month",
        allow_missing_periods=True,
    )
    expected = VALUES[VALUES > 2].sum() / VALUES.sum()
    np.testing.assert_allclose(_value(result, "fraction_of_total"), [expected])


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("mean_of_difference", np.mean(VALUES - REFERENCE)),
        ("difference_of_extremes", np.max(VALUES) - np.min(REFERENCE)),
        (
            "mean_of_absolute_one_time_step_difference",
            np.mean(np.abs(np.diff(VALUES - REFERENCE))),
        ),
        ("difference_of_means", np.mean(VALUES) - np.mean(REFERENCE)),
    ],
)
def test_two_variable_reducer_matches_numpy(name: str, expected: float) -> None:
    result = getattr(icclim, name)(
        in_files={"study": _data(), "reference": _data(REFERENCE)},
        slice_mode="month",
        allow_missing_periods=True,
    )
    np.testing.assert_allclose(_value(result, name), [expected])


def test_percentile_matches_numpy() -> None:
    result = icclim.percentile(
        in_files=_data(),
        threshold="50 period_per",
        slice_mode="month",
        allow_missing_periods=True,
    )
    np.testing.assert_allclose(_value(result, "percentile"), [np.quantile(VALUES, 0.5)])
