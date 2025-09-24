from __future__ import annotations

import contextlib
from collections.abc import Callable
from pathlib import Path

import numpy as np
import pandas as pd
import pint
import pytest
import xarray as xr
from icclim._core.constants import UNITS_KEY
from icclim._core.generic.threshold.basic import BasicThreshold
from icclim._core.generic.threshold.bounded import BoundedThreshold
from icclim._core.generic.threshold.percentile import PercentileThreshold
from icclim._core.input_parsing import PercentileDataArray
from icclim._core.model.logical_link import LogicalLinkRegistry
from icclim._core.model.operator import OperatorRegistry
from icclim.exception import InvalidIcclimArgumentError
from icclim.threshold.factory import build_threshold
from xclim.core.calendar import percentile_doy
from xclim.core.units import units as xc_units


# --- Patch for unit normalization in tests ---
def normalize_unit_for_test(unit: str) -> str:
    """Return a canonical string for a unit, using xclim/pint."""
    try:
        return str(xc_units(unit).units)
    except Exception:
        return unit


# ------------------- Tests -------------------
def test_value_error() -> None:
    with pytest.raises(NotImplementedError):
        build_threshold(value={"random": "stuff"})


def test_query_error() -> None:
    with pytest.raises(InvalidIcclimArgumentError):
        build_threshold("Coco l'asticot")


def test_build_threshold__from_query() -> None:
    res = build_threshold(">10degC")
    assert isinstance(res, BasicThreshold)
    assert res.operator == OperatorRegistry.GREATER
    assert res.value == 10
    assert normalize_unit_for_test(res.unit) == normalize_unit_for_test("degree_Celsius")


def test_build_bounded_threshold__from_query() -> None:
    res = build_threshold(">10degC and <20degC")
    assert isinstance(res, BoundedThreshold)
    assert res.left_threshold.operator == OperatorRegistry.GREATER
    assert res.left_threshold.value == 10
    assert normalize_unit_for_test(res.left_threshold.unit) == normalize_unit_for_test("degree_Celsius")
    assert res.logical_link == LogicalLinkRegistry.LOGICAL_AND
    assert res.right_threshold.operator == OperatorRegistry.LOWER
    assert res.right_threshold.value == 20
    assert normalize_unit_for_test(res.right_threshold.unit) == normalize_unit_for_test("degree_Celsius")


def test_build_bounded_threshold__unit_conversion() -> None:
    res = build_threshold(">10degC and <300 K")
    res.unit = "degree_Fahrenheit"
    np.testing.assert_almost_equal(res.left_threshold.value, 50)
    np.testing.assert_almost_equal(res.right_threshold.value, 80.33)
    assert normalize_unit_for_test(res.left_threshold.unit) == normalize_unit_for_test("degree_Fahrenheit")
    assert normalize_unit_for_test(res.right_threshold.unit) == normalize_unit_for_test("degree_Fahrenheit")


def test_build_bounded_threshold__unit_conversion_erorr() -> None:
    # GIVEN
    res = build_threshold(">10degC and <300 K")
    # THEN
    with pytest.raises(pint.DimensionalityError):
        # WHEN
        res.unit = "meter"


def test_build_bounded_threshold__error() -> None:
    with pytest.raises(NotImplementedError):
        build_threshold(thresholds=[">10degC", ">11degC", ">12degC"], logical_link="or")


def test_build_bounded_threshold__from_and() -> None:
    t1 = build_threshold(">10degC")
    t2 = build_threshold(">12 doy_per")
    t3 = t1 & t2
    assert isinstance(t3, BoundedThreshold)
    assert isinstance(t3.left_threshold, BasicThreshold)
    assert t3.left_threshold.operator == OperatorRegistry.GREATER
    assert t3.left_threshold.value == 10
    assert normalize_unit_for_test(t3.left_threshold.unit) == normalize_unit_for_test("degree_Celsius")
    assert t3.logical_link == LogicalLinkRegistry.LOGICAL_AND
    assert isinstance(t3.right_threshold, PercentileThreshold)
    assert t3.right_threshold.is_ready is False
    assert t3.right_threshold.operator == OperatorRegistry.GREATER
    assert t3.right_threshold._initial_unit == "doy_per"
    assert t3.right_threshold.initial_value == [12]


def test_build_bounded_threshold__from_or() -> None:
    t1 = build_threshold(">10degC")
    t2 = build_threshold(">12 doy_per")
    t3 = t1 | t2
    assert isinstance(t3, BoundedThreshold)
    assert isinstance(t3.left_threshold, BasicThreshold)
    assert t3.left_threshold.operator == OperatorRegistry.GREATER
    assert t3.left_threshold.value == 10
    assert normalize_unit_for_test(t3.left_threshold.unit) == normalize_unit_for_test("degree_Celsius")
    assert t3.logical_link == LogicalLinkRegistry.LOGICAL_OR
    assert isinstance(t3.right_threshold, PercentileThreshold)
    assert t3.right_threshold.is_ready is False
    assert t3.right_threshold.operator == OperatorRegistry.GREATER
    assert t3.right_threshold._initial_unit == "doy_per"
    assert t3.right_threshold.initial_value == [12]


def test_build_bounded_threshold__from_args() -> None:
    t1 = build_threshold(">10degC")
    t2 = build_threshold(">12 doy_per")
    t3 = build_threshold(
        thresholds=(t1, t2),
        logical_link=LogicalLinkRegistry.LOGICAL_OR,
    )
    assert isinstance(t3, BoundedThreshold)
    assert isinstance(t3.left_threshold, BasicThreshold)
    assert t3.left_threshold.operator == OperatorRegistry.GREATER
    assert t3.left_threshold.value == 10
    assert normalize_unit_for_test(t3.left_threshold.unit) == normalize_unit_for_test("degree_Celsius")
    assert t3.logical_link == LogicalLinkRegistry.LOGICAL_OR
    assert isinstance(t3.right_threshold, PercentileThreshold)
    assert t3.right_threshold.is_ready is False
    assert t3.right_threshold.operator == OperatorRegistry.GREATER
    assert t3.right_threshold._initial_unit == "doy_per"
    assert t3.right_threshold.initial_value == [12]


def test_basic_threshold_eq() -> None:
    a = build_threshold(">10degC")
    b = build_threshold(">10degC")
    c = build_threshold(">10mm")
    assert a == b
    assert a != c


def test_percentile_threshold_eq() -> None:
    a = build_threshold(">10doy_per")
    b = build_threshold(">10doy_per")
    c = build_threshold(">20doy_per")
    assert a == b
    assert a != c


def test_bounded_threshold_eq() -> None:
    a = build_threshold(">10doy_per")
    a_bis = build_threshold(">10doy_per")
    b = build_threshold(">15doy_per")
    c = build_threshold(">20doy_per")
    assert a & b == a_bis & b
    assert a & b == b & a
    assert a & b != a & c


def test_per_threshold_min_value__operand_error() -> None:
    with pytest.raises(InvalidIcclimArgumentError):
        build_threshold(">10doy_per", threshold_min_value="< 10 degC")


def test_per_threshold_min_value__type_error() -> None:
    with pytest.raises(NotImplementedError):
        build_threshold(">10doy_per", threshold_min_value={"random": "stuff"})


def test_per_threshold_min_value__string() -> None:
    a = build_threshold(">10doy_per", threshold_min_value="10 degC")
    assert a.threshold_min_value == xc_units.Quantity(10, "degC")


def test_per_threshold_min_value__quantity() -> None:
    a = build_threshold(">10doy_per", threshold_min_value=xc_units.Quantity(10, "degC"))
    assert a.threshold_min_value == xc_units.Quantity(10, "degC")


def test_per_threshold_min_value__number() -> None:
    a = build_threshold(">10doy_per", threshold_min_value=10)
    assert a.threshold_min_value.dimensionless
    assert a.threshold_min_value.magnitude == 10


def test_threshold_min_value__number() -> None:
    with pytest.raises(InvalidIcclimArgumentError):
        build_threshold(">10degC", threshold_min_value=5)


def test_threshold_min_value__error() -> None:
    with pytest.raises(NotImplementedError):
        build_threshold(None)


def test_build_per_threshold__from_query() -> None:
    res = build_threshold("<= 99 doy_per")
    assert isinstance(res, PercentileThreshold)
    assert res.operator == OperatorRegistry.LOWER_OR_EQUAL
    assert res.initial_value == [99]
    assert normalize_unit_for_test(res.unit) == normalize_unit_for_test("doy_per")  # not computed yet
    assert res._initial_unit == "doy_per"
    assert res.is_ready is False
    assert isinstance(res.prepare, Callable)
    with pytest.raises(RuntimeError):  # not computed yet
        _ = res.value


def test_build_basic_threshold__special_char_in_unit() -> None:
    t = build_threshold("< 1 mm/day")
    assert t.operator == OperatorRegistry.LOWER
    assert t.value == 1
    assert normalize_unit_for_test(t.unit) == normalize_unit_for_test("millimeter / day")
