from __future__ import annotations

import os
from typing import Callable

import numpy as np
import pandas as pd
import pint
import pytest
import xarray as xr
from xclim.core.calendar import percentile_doy
from xclim.core.units import units as xc_units

from icclim.generic_indices.threshold import (
    BasicThreshold,
    BoundedThreshold,
    PercentileThreshold,
    build_threshold,
)
from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.models.constants import UNITS_KEY
from icclim.models.logical_link import LogicalLinkRegistry
from icclim.models.operator import OperatorRegistry
from icclim.pre_processing.input_parsing import PercentileDataArray


def test_value_error():
    with pytest.raises(NotImplementedError):
        build_threshold(value={"random": "stuff"})


def test_query_error():
    with pytest.raises(InvalidIcclimArgumentError):
        build_threshold("Coco l'asticot")


def test_build_threshold__from_query():
    res = build_threshold(">10degC")
    assert isinstance(res, BasicThreshold)
    assert res.operator == OperatorRegistry.GREATER
    assert res.value == 10
    assert res.unit == "degC"


def test_build_bounded_threshold__from_query():
    res = build_threshold(">10degC and <20degC")
    assert isinstance(res, BoundedThreshold)
    assert res.left_threshold.operator == OperatorRegistry.GREATER
    assert res.left_threshold.value == 10
    assert res.left_threshold.unit == "degC"
    assert res.logical_link == LogicalLinkRegistry.LOGICAL_AND
    assert res.right_threshold.operator == OperatorRegistry.LOWER
    assert res.right_threshold.value == 20
    assert res.right_threshold.unit == "degC"


def test_build_bounded_threshold__unit_conversion():
    res = build_threshold(">10degC and <300 K")
    res.unit = "degree_Fahrenheit"
    np.testing.assert_almost_equal(res.left_threshold.value, 50)
    np.testing.assert_almost_equal(res.right_threshold.value, 80.33)
    assert res.left_threshold.unit == "degree_Fahrenheit"
    assert res.right_threshold.unit == "degree_Fahrenheit"


def test_build_bounded_threshold__unit_conversion_erorr():
    # GIVEN
    res = build_threshold(">10degC and <300 K")
    # THEN
    with pytest.raises(pint.DimensionalityError):
        # WHEN
        res.unit = "meter"


def test_build_bounded_threshold__error():
    with pytest.raises(NotImplementedError):
        build_threshold(thresholds=[">10degC", ">11degC", ">12degC"], logical_link="or")


def test_build_bounded_threshold__from_and():
    t1 = build_threshold(">10degC")
    t2 = build_threshold(">12 doy_per")
    t3 = t1 & t2
    assert isinstance(t3, BoundedThreshold)
    assert isinstance(t3.left_threshold, BasicThreshold)
    assert t3.left_threshold.operator == OperatorRegistry.GREATER
    assert t3.left_threshold.value == 10
    assert t3.left_threshold.unit == "degC"
    assert t3.logical_link == LogicalLinkRegistry.LOGICAL_AND
    assert isinstance(t3.right_threshold, PercentileThreshold)
    assert t3.right_threshold.is_ready is False
    assert t3.right_threshold.operator == OperatorRegistry.GREATER
    assert t3.right_threshold._initial_unit == "doy_per"
    assert t3.right_threshold._initial_value == [12]


def test_build_bounded_threshold__from_or():
    t1 = build_threshold(">10degC")
    t2 = build_threshold(">12 doy_per")
    t3 = t1 | t2
    assert isinstance(t3, BoundedThreshold)
    assert isinstance(t3.left_threshold, BasicThreshold)
    assert t3.left_threshold.operator == OperatorRegistry.GREATER
    assert t3.left_threshold.value == 10
    assert t3.left_threshold.unit == "degC"
    assert t3.logical_link == LogicalLinkRegistry.LOGICAL_OR
    assert isinstance(t3.right_threshold, PercentileThreshold)
    assert t3.right_threshold.is_ready is False
    assert t3.right_threshold.operator == OperatorRegistry.GREATER
    assert t3.right_threshold._initial_unit == "doy_per"
    assert t3.right_threshold._initial_value == [12]


def test_build_bounded_threshold__from_args():
    t1 = build_threshold(">10degC")
    t2 = build_threshold(">12 doy_per")
    t3 = build_threshold(
        thresholds=(t1, t2), logical_link=LogicalLinkRegistry.LOGICAL_OR
    )
    assert isinstance(t3, BoundedThreshold)
    assert isinstance(t3.left_threshold, BasicThreshold)
    assert t3.left_threshold.operator == OperatorRegistry.GREATER
    assert t3.left_threshold.value == 10
    assert t3.left_threshold.unit == "degC"
    assert t3.logical_link == LogicalLinkRegistry.LOGICAL_OR
    assert isinstance(t3.right_threshold, PercentileThreshold)
    assert t3.right_threshold.is_ready is False
    assert t3.right_threshold.operator == OperatorRegistry.GREATER
    assert t3.right_threshold._initial_unit == "doy_per"
    assert t3.right_threshold._initial_value == [12]


def test_basic_threshold_eq():
    a = build_threshold(">10degC")
    b = build_threshold(">10degC")
    c = build_threshold(">10mm")
    assert a == b
    assert a != c


def test_percentile_threshold_eq():
    a = build_threshold(">10doy_per")
    b = build_threshold(">10doy_per")
    c = build_threshold(">20doy_per")
    assert a == b
    assert a != c


def test_bounded_threshold_eq():
    a = build_threshold(">10doy_per")
    a_bis = build_threshold(">10doy_per")
    b = build_threshold(">15doy_per")
    c = build_threshold(">20doy_per")
    assert a & b == a_bis & b
    assert a & b == b & a
    assert a & b != a & c


def test_per_threshold_min_value__operand_error():
    with pytest.raises(InvalidIcclimArgumentError):
        build_threshold(">10doy_per", threshold_min_value="< 10 degC")


def test_per_threshold_min_value__type_error():
    with pytest.raises(NotImplementedError):
        build_threshold(">10doy_per", threshold_min_value=dict(random="stuff"))  # noqa


def test_per_threshold_min_value__string():
    a = build_threshold(">10doy_per", threshold_min_value="10 degC")
    assert a.threshold_min_value == xc_units.Quantity(10, "degC")


def test_per_threshold_min_value__quantity():
    a = build_threshold(">10doy_per", threshold_min_value=xc_units.Quantity(10, "degC"))
    assert a.threshold_min_value == xc_units.Quantity(10, "degC")


def test_per_threshold_min_value__number():
    a = build_threshold(">10doy_per", threshold_min_value=10)
    assert a.threshold_min_value.dimensionless
    assert a.threshold_min_value.magnitude == 10


def test_threshold_min_value__number():
    with pytest.raises(InvalidIcclimArgumentError):
        build_threshold(">10degC", threshold_min_value=5)


def test_threshold_min_value__error():
    with pytest.raises(NotImplementedError):
        build_threshold(None)


def test_build_per_threshold__from_query():
    res = build_threshold("<= 99 doy_per")
    assert isinstance(res, PercentileThreshold)
    assert res.operator == OperatorRegistry.LOWER_OR_EQUAL
    assert res._initial_value == [99]
    assert res.unit == "doy_per"  # not computed yet
    assert res._initial_unit == "doy_per"
    assert res.is_ready is False
    assert isinstance(res.prepare, Callable)
    with pytest.raises(RuntimeError):  # not computed yet
        res.value  # noqa


def test_build_basic_threshold__from_dataarray():
    TIME_RANGE = pd.date_range(start="2042-01-01", end="2045-12-31", freq="D")
    data = xr.DataArray(
        data=(np.full(len(TIME_RANGE), 20).reshape((len(TIME_RANGE), 1, 1))),
        dims=["time", "lat", "lon"],
        coords=dict(lat=[42], lon=[42], time=TIME_RANGE),
        attrs={UNITS_KEY: "degC"},
        name="toto",
    )
    res = build_threshold(operator=">=", value=data, threshold_min_value="280K")
    assert isinstance(res, BasicThreshold)
    assert res.operator == OperatorRegistry.GREATER_OR_EQUAL
    xr.testing.assert_equal(res.value, data)
    assert res.unit == "degC"
    assert res.is_ready is True


def test_build_basic_threshold__from_dataset():
    TIME_RANGE = pd.date_range(start="2042-01-01", end="2045-12-31", freq="D")
    ds = xr.DataArray(
        data=(np.full(len(TIME_RANGE), 20).reshape((len(TIME_RANGE), 1, 1))),
        dims=["time", "lat", "lon"],
        coords=dict(lat=[42], lon=[42], time=TIME_RANGE),
        attrs={UNITS_KEY: "degC"},
        name="tas",
    ).to_dataset()
    ds["tutu"] = ds["tas"]
    res = build_threshold(operator=">=", value=ds, threshold_min_value="280K")
    assert isinstance(res, BasicThreshold)
    assert res.operator == OperatorRegistry.GREATER_OR_EQUAL
    xr.testing.assert_equal(res.value, ds["tas"])
    assert res.unit == "degC"
    assert res.is_ready is True


def test_build_basic_threshold__from_dataset__error():
    TIME_RANGE = pd.date_range(start="2042-01-01", end="2045-12-31", freq="D")
    ds = xr.DataArray(
        data=(np.full(len(TIME_RANGE), 20).reshape((len(TIME_RANGE), 1, 1))),
        dims=["time", "lat", "lon"],
        coords=dict(lat=[42], lon=[42], time=TIME_RANGE),
        attrs={UNITS_KEY: "degC"},
        name="toto",
    ).to_dataset()
    ds["tutu"] = ds.toto
    with pytest.raises(InvalidIcclimArgumentError):
        # multiple variable without any recognizable one
        build_threshold(operator=">=", value=ds, threshold_min_value="280K")


class Test_FileBased:
    IN_FILE_PATH = "in.nc"
    TIME_RANGE = pd.date_range(start="2042-01-01", end="2045-12-31", freq="D")

    data = xr.DataArray(
        data=(np.full(len(TIME_RANGE), 20).reshape((len(TIME_RANGE), 1, 1))),
        dims=["time", "lat", "lon"],
        coords=dict(lat=[42], lon=[42], time=TIME_RANGE),
        attrs={UNITS_KEY: "degC"},
        name="toto",
    )

    @pytest.fixture(autouse=True)
    def cleanup(self):
        # setup
        # ...
        yield
        # teardown
        try:
            os.remove(self.IN_FILE_PATH)
        except FileNotFoundError:
            pass

    def test_build_basic_threshold__from_file(self):
        self.data.to_netcdf(path=self.IN_FILE_PATH)
        res = build_threshold(operator=">=", value=self.IN_FILE_PATH)
        assert isinstance(res, BasicThreshold)
        assert res.operator == OperatorRegistry.GREATER_OR_EQUAL
        xr.testing.assert_equal(res.value, self.data)
        assert res.unit == "degC"
        assert res.is_ready is True

    def test_threshold_min_value__number_from_file(self):
        self.data.to_netcdf(path=self.IN_FILE_PATH)
        res = build_threshold(
            operator=">=", value=self.IN_FILE_PATH, threshold_min_value=5
        )
        assert res.threshold_min_value == xc_units.Quantity(5, "degC")

    def test_build_percentile_threshold__from_file(self):
        doys = percentile_doy(self.data)
        doys = PercentileDataArray.from_da(doys)
        doys.to_netcdf(path=self.IN_FILE_PATH)
        res = build_threshold(operator=">=", value=self.IN_FILE_PATH)
        assert isinstance(res, PercentileThreshold)
        assert res.operator == OperatorRegistry.GREATER_OR_EQUAL
        xr.testing.assert_equal(res.value, doys)
        assert res._initial_unit is None
        assert res.unit is None
        assert res.is_ready is True
        assert res._initial_value is None
        assert res.prepare is None
