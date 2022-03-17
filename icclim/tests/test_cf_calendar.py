import numpy as np
import pandas as pd
import pytest
import xarray as xr

from icclim.models.cf_calendar import CfCalendar


class Test_CfCalendar:
    def test_error_lookup(self):
        with pytest.raises(TypeError):
            CfCalendar.lookup("NOPE!")

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
    def test_success_lookup(self, cal):
        assert CfCalendar.lookup(cal).aliases[0] == cal

    def test_NO_LEAP(self):
        da = xr.DataArray(pd.date_range("2000", periods=100, freq="YS"), dims=["time"])
        res = CfCalendar.NO_LEAP.is_leap(da)
        np.testing.assert_array_equal(False, res)

    def test_DAYS_360(self):
        da = xr.DataArray(pd.date_range("2000", periods=100, freq="YS"), dims=["time"])
        res = CfCalendar.DAYS_360.is_leap(da)
        np.testing.assert_array_equal(False, res)

    def test_ALL_LEAP(self):
        da = xr.DataArray(pd.date_range("2000", periods=100, freq="YS"), dims=["time"])
        res = CfCalendar.ALL_LEAP.is_leap(da)
        np.testing.assert_array_equal(True, res)

    def test_PROLEPTIC_GREGORIAN(self):
        res_1 = CfCalendar.PROLEPTIC_GREGORIAN.is_leap(
            xr.DataArray(np.asarray([40, 1600]))
        )
        res_2 = CfCalendar.PROLEPTIC_GREGORIAN.is_leap(
            xr.DataArray(np.asarray([42, 1500, 1700]))
        )
        np.testing.assert_array_equal(True, res_1)
        np.testing.assert_array_equal(False, res_2)

    def test_JULIAN(self):
        res_1 = CfCalendar.JULIAN.is_leap(
            xr.DataArray(np.asarray([40, 1500, 1600, 1700]))
        )
        res_2 = CfCalendar.JULIAN.is_leap(xr.DataArray(np.asarray([42])))
        np.testing.assert_array_equal(True, res_1)
        np.testing.assert_array_equal(False, res_2)

    @pytest.mark.parametrize(
        "cal",
        [CfCalendar.STANDARD, CfCalendar.NONE],
    )
    def test_STANDARD(self, cal):
        res_1 = cal.is_leap(xr.DataArray(np.asarray([40, 1500, 1600])))
        res_2 = cal.is_leap(xr.DataArray(np.asarray([42, 1700])))
        np.testing.assert_array_equal(True, res_1)
        np.testing.assert_array_equal(False, res_2)
