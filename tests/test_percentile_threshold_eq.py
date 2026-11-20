"""
``PercentileThreshold`` equality compares the operator and the percentile(s) (#726).

A threshold built from a query carries the operator and the value in its query, so
it was already told apart. A threshold built without a query (from precomputed
percentiles, or from the class) was not: two thresholds with another operator, another
percentile or other data compared equal, and a bounded threshold could not be built
from them ("BoundedThreshold must be built on 2 different thresholds").
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import xarray as xr
from xclim.core.calendar import percentile_doy

from icclim import build_threshold
from icclim._core.generic.threshold.bounded import BoundedThreshold
from icclim._core.generic.threshold.percentile import PercentileThreshold
from icclim._core.model.operator import OperatorRegistry
from icclim.exception import InvalidIcclimArgumentError

REFERENCE = ["2000-01-01", "2002-12-31"]


def _threshold(operator, value) -> PercentileThreshold:
    return PercentileThreshold(
        operator, value, unit="doy_per", reference_period=REFERENCE
    )


def _percentiles(shift: float, level: int) -> xr.DataArray:
    time = pd.date_range("2000-01-01", "2002-12-31")
    rng = np.random.default_rng(1)
    values = (290 + shift + rng.normal(0, 3, (len(time), 1, 1))).astype("float32")
    da = xr.DataArray(
        values,
        dims=("time", "lat", "lon"),
        coords={"time": time, "lat": [1.0], "lon": [2.0]},
        attrs={"units": "K"},
    )
    return percentile_doy(da, per=level).compute()


def test_operator_is_compared():
    greater = _threshold(OperatorRegistry.GREATER, 90)
    lower = _threshold(OperatorRegistry.LOWER, 90)
    assert greater != lower
    assert greater == _threshold(OperatorRegistry.GREATER, 90)


def test_percentile_is_compared_without_a_query():
    assert _threshold(OperatorRegistry.GREATER, 90) != _threshold(
        OperatorRegistry.GREATER, 95
    )
    assert _threshold(OperatorRegistry.GREATER, [90, 95]) != _threshold(
        OperatorRegistry.GREATER, [90, 99]
    )


def test_precomputed_percentiles_are_compared_by_operator_level_and_data():
    p90 = _percentiles(0.0, 90)
    base = build_threshold(operator=">", value=p90)
    assert base == build_threshold(operator=">", value=p90)
    assert base == build_threshold(operator=">", value=p90.copy(deep=True))
    assert base != build_threshold(operator="<", value=p90)
    assert base != build_threshold(operator=">", value=_percentiles(0.0, 99))
    assert base != build_threshold(operator=">", value=_percentiles(5.0, 90))


def test_equal_thresholds_have_the_same_hash():
    first = _threshold(OperatorRegistry.GREATER, 90)
    second = _threshold(OperatorRegistry.GREATER, 90)
    assert first == second
    assert hash(first) == hash(second)
    p90 = _percentiles(0.0, 90)
    assert hash(build_threshold(operator=">", value=p90)) == hash(
        build_threshold(operator=">", value=p90.copy(deep=True))
    )


def test_distinct_thresholds_are_distinct_set_members():
    thresholds = {
        _threshold(OperatorRegistry.GREATER, 90),
        _threshold(OperatorRegistry.LOWER, 90),
        _threshold(OperatorRegistry.GREATER, 95),
    }
    assert len(thresholds) == 3


def test_bounded_threshold_can_be_built_from_precomputed_percentiles():
    low = build_threshold(operator=">", value=_percentiles(0.0, 90))
    high = build_threshold(operator="<", value=_percentiles(0.0, 99))
    assert isinstance(low & high, BoundedThreshold)
    assert isinstance(
        build_threshold(thresholds=[low, high], logical_link="and"), BoundedThreshold
    )


def test_bounded_threshold_of_two_equal_thresholds_is_still_refused():
    first = _threshold(OperatorRegistry.GREATER, 90)
    second = _threshold(OperatorRegistry.GREATER, 90)
    with pytest.raises(InvalidIcclimArgumentError, match="2 \\*\\*different\\*\\*"):
        first & second


def test_equality_of_thresholds_built_from_a_query_is_unchanged():
    assert build_threshold("> 90 doy_per", reference_period=REFERENCE) == (
        build_threshold("> 90 doy_per", reference_period=tuple(REFERENCE))
    )
    assert build_threshold("> 90 doy_per", reference_period=REFERENCE) != (
        build_threshold("< 90 doy_per", reference_period=REFERENCE)
    )
    assert build_threshold("> 90 doy_per", reference_period=REFERENCE) != (
        build_threshold("> 95 doy_per", reference_period=REFERENCE)
    )
    first = build_threshold("> 90 doy_per", reference_period=REFERENCE)
    second = build_threshold("> 90 doy_per", reference_period=REFERENCE)
    assert hash(first) == hash(second)


def test_percentile_threshold_is_not_equal_to_another_class():
    assert _threshold(OperatorRegistry.GREATER, 90) != build_threshold("> 90 degC")
