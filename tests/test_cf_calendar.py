from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import xarray as xr
from icclim._core.model.cf_calendar import CfCalendarRegistry
from icclim.exception import InvalidIcclimArgumentError


class TestCfCalendar:
    def test_error_lookup(self) -> None:
        with pytest.raises(InvalidIcclimArgumentError):
            CfCalendarRegistry.lookup("NOPE!")

    @pytest.mark.parametrize(
        "cal",
        [
            "noleap",
            "360_day",
            "all_leap",
            "proleptic_gregorian",
            "julian",
            "standard",
            "none",
        ],
    )
    def test_success_lookup(self, cal) -> None:
        assert CfCalendarRegistry.lookup(cal).aliases[0] == cal

    def test_no_leap(self) -> None:
        da = xr.DataArray(pd.date_range("2000", periods=100, freq="YS"), dims=["time"])
        res = CfCalendarRegistry.NO_LEAP.is_leap(da)
        np.testing.assert_array_equal(False, res)

    def test_days_360(self) -> None:
        da = xr.DataArray(pd.date_range("2000", periods=100, freq="YS"), dims=["time"])
        res = CfCalendarRegistry.DAYS_360.is_leap(da)
        np.testing.assert_array_equal(False, res)

    def test_all_leap(self) -> None:
        da = xr.DataArray(pd.date_range("2000", periods=100, freq="YS"), dims=["time"])
        res = CfCalendarRegistry.ALL_LEAP.is_leap(da)
        np.testing.assert_array_equal(True, res)

    def test_proleptic_gregorian(self) -> None:
        res_1 = CfCalendarRegistry.PROLEPTIC_GREGORIAN.is_leap(
            xr.DataArray(np.asarray([40, 1600])),
        )
        res_2 = CfCalendarRegistry.PROLEPTIC_GREGORIAN.is_leap(
            xr.DataArray(np.asarray([42, 1500, 1700])),
        )
        np.testing.assert_array_equal(True, res_1)
        np.testing.assert_array_equal(False, res_2)

    def test_julian(self) -> None:
        res_1 = CfCalendarRegistry.JULIAN.is_leap(
            xr.DataArray(np.asarray([40, 1500, 1600, 1700])),
        )
        res_2 = CfCalendarRegistry.JULIAN.is_leap(xr.DataArray(np.asarray([42])))
        np.testing.assert_array_equal(True, res_1)
        np.testing.assert_array_equal(False, res_2)

    @pytest.mark.parametrize(
        "cal",
        [CfCalendarRegistry.STANDARD, CfCalendarRegistry.NONE],
    )
    def test_standard(self, cal) -> None:
        res_1 = cal.is_leap(xr.DataArray(np.asarray([40, 1500, 1600])))
        res_2 = cal.is_leap(xr.DataArray(np.asarray([42, 1700])))
        np.testing.assert_array_equal(True, res_1)
        np.testing.assert_array_equal(False, res_2)
