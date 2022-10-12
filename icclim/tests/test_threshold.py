from __future__ import annotations

import os
from typing import Callable

import numpy as np
import pandas as pd
import pint
import pytest
import xarray as xr
from xclim.core.calendar import percentile_doy

from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.models.constants import UNITS_KEY
from icclim.models.operator import OperatorRegistry
from icclim.models.threshold import BasicThreshold, PercentileThreshold, build_threshold


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


def test_per_threshold_min_value__operand_error():
    with pytest.raises(InvalidIcclimArgumentError):
        build_threshold(">10doy_per", threshold_min_value="< 10 degC")


def test_per_threshold_min_value__type_error():
    with pytest.raises(NotImplementedError):
        build_threshold(">10doy_per", threshold_min_value=dict(random="stuff"))  # noqa


def test_per_threshold_min_value__string():
    a = build_threshold(">10doy_per", threshold_min_value="10 degC")
    assert a.threshold_min_value == pint.Quantity(10, "degC")


def test_per_threshold_min_value__quantity():
    a = build_threshold(">10doy_per", threshold_min_value=pint.Quantity(10, "degC"))
    assert a.threshold_min_value == pint.Quantity(10, "degC")


def test_per_threshold_min_value__number():
    a = build_threshold(">10doy_per", threshold_min_value=10)
    assert a.threshold_min_value.dimensionless
    assert a.threshold_min_value.magnitude == 10


def test_threshold_min_value__number():
    with pytest.raises(InvalidIcclimArgumentError):
        build_threshold(">10degC", threshold_min_value=5)


def test_build_per_threshold__from_query():
    res = build_threshold("<= 99 doy_per")
    assert isinstance(res, PercentileThreshold)
    assert res.operator == OperatorRegistry.LOWER_OR_EQUAL
    assert res._initial_value == 99
    assert res.unit == "doy_per"  # not computed yet
    assert res._initial_unit == "doy_per"
    assert res.is_ready is False
    assert isinstance(res.prepare, Callable)
    with pytest.raises(RuntimeError):  # not computed yet
        res.value  # noqa


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
        assert res.threshold_min_value == pint.Quantity(5, "degC")

    def test_build_percentile_threshold__from_file(self):
        doys = percentile_doy(self.data)
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
