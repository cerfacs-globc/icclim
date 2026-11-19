"""
A percentile threshold built with a list or a tuple as ``reference_period`` (issue #714).

A list used to fail with ``TypeError: unhashable type: 'list'`` when the thresholds of
several variables (or a bounded threshold) were computed, because the reference period
was part of a cache key. The reference period is now a tuple whatever its input type.
"""

from __future__ import annotations

import datetime as dt

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim
from icclim import build_threshold
from icclim._core.generic.threshold.percentile import PercentileThreshold

BASE_LIST = ["2000-01-01", "2004-12-31"]
BASE_DATETIMES = [
    dt.datetime.fromisoformat("2000-01-01"),
    dt.datetime.fromisoformat("2004-12-31"),
]


def _dataset() -> xr.Dataset:
    time = pd.date_range("2000-01-01", "2009-12-31", freq="D")
    rng = np.random.default_rng(1)
    doy = time.day_of_year.to_numpy()
    tas = (
        285
        + 10 * np.sin(2 * np.pi * (doy - 110) / 365.25)
        + rng.normal(0, 3, len(time))
    )
    pr = rng.gamma(0.4, 6, len(time)) * (rng.random(len(time)) < 0.55) / 86400

    def array(name: str, units: str, values: np.ndarray) -> xr.DataArray:
        return xr.DataArray(
            values.astype("float32").reshape(len(time), 1, 1),
            dims=("time", "lat", "lon"),
            coords={"time": time, "lat": [1.0], "lon": [2.0]},
            attrs={"units": units},
            name=name,
        )

    return xr.Dataset(
        {
            "tas": array("tas", "K", tas),
            "tasmax": array("tasmax", "K", tas + 5),
            "tasmin": array("tasmin", "K", tas - 5),
            "pr": array("pr", "kg m-2 s-1", pr),
        }
    )


def _values(result: xr.Dataset) -> np.ndarray:
    return result[next(iter(result.data_vars))].values.astype("float64").ravel()


def _same(compute) -> None:
    from_list = _values(compute(list))
    from_tuple = _values(compute(tuple))
    assert np.isfinite(from_list).any()
    np.testing.assert_array_equal(from_list, from_tuple)


@pytest.mark.parametrize("reference", [BASE_LIST, BASE_DATETIMES])
def test_the_reference_period_of_a_threshold_is_a_tuple(reference) -> None:
    threshold = build_threshold("> 90 doy_per", reference_period=reference)
    assert isinstance(threshold, PercentileThreshold)
    assert threshold.reference_period == tuple(reference)
    assert isinstance(threshold.reference_period, tuple)


def test_a_threshold_without_a_reference_period_keeps_none() -> None:
    threshold = build_threshold("> 90 doy_per")
    assert threshold.reference_period is None
    threshold.reference_period = BASE_LIST
    assert threshold.reference_period == tuple(BASE_LIST)
    threshold.reference_period = None
    assert threshold.reference_period is None


def test_thresholds_with_a_list_and_a_tuple_are_equal() -> None:
    from_list = build_threshold("> 90 doy_per", reference_period=BASE_LIST)
    from_tuple = build_threshold("> 90 doy_per", reference_period=tuple(BASE_LIST))
    assert from_list == from_tuple


def test_one_variable_gives_the_same_result_with_a_list_and_a_tuple() -> None:
    ds = _dataset()
    _same(
        lambda c: icclim.count_occurrences(
            in_files=ds.tasmax,
            var_name="tasmax",
            threshold=build_threshold("> 90 doy_per", reference_period=c(BASE_LIST)),
            slice_mode="year",
        )
    )


def test_a_dictionary_of_several_variables_gives_the_same_result() -> None:
    # Regression test of issue #714: "TypeError: unhashable type: 'list'"
    ds = _dataset()
    _same(
        lambda c: icclim.count_occurrences(
            in_files={
                "tasmax": {
                    "study": ds.tasmax,
                    "thresholds": build_threshold(
                        "> 90 doy_per", reference_period=c(BASE_LIST)
                    ),
                },
                "tasmin": {
                    "study": ds.tasmin,
                    "thresholds": build_threshold(
                        "> 90 doy_per", reference_period=c(BASE_LIST)
                    ),
                },
            },
            slice_mode="year",
        )
    )


def test_a_temperature_and_a_precipitation_threshold_give_the_same_result() -> None:
    ds = _dataset()
    _same(
        lambda c: icclim.count_occurrences(
            in_files={
                "tas": {
                    "study": ds.tas,
                    "thresholds": build_threshold(
                        "< 25 doy_per", reference_period=c(BASE_LIST)
                    ),
                },
                "pr": {
                    "study": ds.pr,
                    "thresholds": build_threshold(
                        "> 75 period_per",
                        threshold_min_value="1 mm/day",
                        reference_period=c(BASE_LIST),
                    ),
                },
            },
            slice_mode="year",
        )
    )


def test_a_bounded_threshold_gives_the_same_result() -> None:
    ds = _dataset()
    _same(
        lambda c: icclim.count_occurrences(
            in_files=ds.tasmax,
            var_name="tasmax",
            threshold=build_threshold("> 90 doy_per", reference_period=c(BASE_LIST))
            & build_threshold("< 99 doy_per", reference_period=c(BASE_LIST)),
            slice_mode="year",
        )
    )


def test_the_base_period_of_icclim_index_gives_the_same_result_as_a_list_or_a_tuple() -> (
    None
):
    ds = _dataset()
    thresholds = {
        "tasmax": {"study": ds.tasmax, "thresholds": "> 90 doy_per"},
        "tasmin": {"study": ds.tasmin, "thresholds": "> 90 doy_per"},
    }
    _same(
        lambda c: icclim.index(
            index_name="count_occurrences",
            in_files=thresholds,
            base_period_time_range=c(BASE_DATETIMES),
            time_range=c(["2000-01-01", "2008-12-31"]),
            slice_mode="year",
        )
    )


def test_a_threshold_object_receives_the_base_period_as_a_tuple() -> None:
    ds = _dataset()
    threshold = build_threshold("> 90 doy_per")
    icclim.index(
        index_name="count_occurrences",
        in_files=ds.tasmax,
        var_name="tasmax",
        threshold=threshold,
        base_period_time_range=BASE_LIST,
        slice_mode="year",
    )
    # the request base period is given to a copy of the threshold: the object of the
    # caller is not changed
    assert threshold.reference_period is None
