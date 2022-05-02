from datetime import datetime
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

import icclim
from icclim.icclim_logger import Verbosity
from icclim.models.constants import (
    MODIFIABLE_QUANTILE_WINDOW,
    MODIFIABLE_THRESHOLD,
    MODIFIABLE_UNIT,
    QUANTILE_BASED,
)
from icclim.models.ecad_indices import EcadIndex
from icclim.models.frequency import Frequency
from icclim.models.netcdf_version import NetcdfVersion
from icclim.models.quantile_interpolation import QuantileInterpolation
from icclim.tests.test_utils import stub_tas
from icclim.user_indices.calc_operation import CalcOperation

DEFAULT_ARGS = dict(
    in_files="pouet.nc",
    var_name=None,
    slice_mode=Frequency.YEAR,
    time_range=None,
    out_file=None,
    ignore_Feb29th=False,
    netcdf_version=NetcdfVersion.NETCDF4,
    logs_verbosity=Verbosity.LOW,
)


def build_expected_args(index):
    expected_call_args = {"index_name": index.name}
    expected_call_args.update(DEFAULT_ARGS)
    if MODIFIABLE_THRESHOLD in index.qualifiers:
        expected_call_args.update({"threshold": None})
    if QUANTILE_BASED in index.qualifiers:
        expected_call_args.update(
            {
                "base_period_time_range": None,
                "only_leap_years": False,
                "interpolation": QuantileInterpolation.MEDIAN_UNBIASED,
                "save_percentile": False,
            }
        )
    if MODIFIABLE_QUANTILE_WINDOW in index.qualifiers:
        expected_call_args.update({"window_width": 5})
    if MODIFIABLE_UNIT in index.qualifiers:
        expected_call_args.update({"out_unit": None})

    return expected_call_args


@patch("icclim.index")
def test_generated_api(generic_index_fun_mock: MagicMock):
    for i in EcadIndex:
        print(i)
        # GIVEN
        api_index_fun = eval(f"icclim.{i.name.lower()}")
        # WHEN
        api_index_fun(**DEFAULT_ARGS)
        # THEN
        expected_call_args = build_expected_args(i)
        generic_index_fun_mock.assert_called_with(**expected_call_args)


@patch("icclim.index")
def test_custom_index(index_fun_mock: MagicMock):
    user_index_args = dict(
        in_files="pouet_file.nc",
        var_name=None,
        slice_mode=Frequency.YEAR,
        time_range=None,
        out_file=None,
        base_period_time_range=None,
        only_leap_years=False,
        ignore_Feb29th=False,
        out_unit=None,
        netcdf_version=NetcdfVersion.NETCDF4,
        save_percentile=False,
        logs_verbosity=Verbosity.LOW,
        user_index={
            "index_name": "pouet",
            "calc_operation": "nb_events",
            "logical_operation": "gt",
            "thresh": 0,
            "date_event": True,
        },
    )
    icclim.custom_index(**user_index_args)
    index_fun_mock.assert_called_with(**user_index_args)


# integration test
def test_txx__season_slice_mode():
    tas = stub_tas()
    tas.loc[{"time": "2042-02-02"}] = 295
    tas.loc[{"time": "2042-01-01"}] = 303.15  # 30ºC 273.15
    res = icclim.txx(tas, slice_mode=["season", [11, 12, 1, 2]]).compute()
    np.testing.assert_array_equal(res.TXx.isel(time=0), 30)
    np.testing.assert_array_equal(
        res.time_bounds.isel(time=0),
        [np.datetime64("2041-11-01"), np.datetime64("2042-02-28")],
    )


def test_txx__months_slice_mode():
    tas = stub_tas()
    tas.loc[{"time": "2042-11-02"}] = 295
    tas.loc[{"time": "2042-01-01"}] = 303.15  # 30ºC 273.15
    res = icclim.txx(tas, slice_mode=["months", [11, 1]]).compute()
    np.testing.assert_array_equal(res.TXx.isel(time=0), 30)
    np.testing.assert_almost_equal(res.TXx.isel(time=1), 21.85)
    np.testing.assert_array_equal(
        res.time_bounds.isel(time=0),
        [np.datetime64("2042-01-01"), np.datetime64("2042-01-31")],
    )


# integration test
@pytest.mark.parametrize(
    "operator, exp_y1, exp_y2",
    [
        (CalcOperation.MIN, 303.15, 280.15),
        (CalcOperation.MAX, 303.15, 280.15),
        (CalcOperation.SUM, 303.15, 280.15),  # values below 275 are filtered out
        (CalcOperation.MEAN, 303.15, 280.15),
        (CalcOperation.EVENT_COUNT, 1, 1),
        (CalcOperation.MAX_NUMBER_OF_CONSECUTIVE_EVENTS, 1, 1),
    ],
)
def test_custom_index__season_slice_mode(operator, exp_y1, exp_y2):
    tas = stub_tas(2.0)
    tas.loc[{"time": "2042-01-01"}] = 303.15
    tas.loc[{"time": "2042-12-01"}] = 280.15
    res = icclim.custom_index(
        in_files=tas,
        slice_mode=["season", [12, 1]],
        var_name="a_name",
        user_index={
            "index_name": "pouet",
            "calc_operation": operator,
            "logical_operation": "gt",
            "thresh": 275,
        },
    ).compute()
    np.testing.assert_almost_equal(res.pouet.isel(time=0), exp_y1)
    np.testing.assert_almost_equal(res.pouet.isel(time=1), exp_y2)


# integration test
@pytest.mark.parametrize(
    "operator, exp_y1, exp_y2",
    [
        (CalcOperation.RUN_MEAN, 2, 2),
        (CalcOperation.RUN_SUM, 14, 14),
    ],
)
def test_custom_index_run_algos__season_slice_mode(operator, exp_y1, exp_y2):
    tas = stub_tas(2.0)
    res = icclim.custom_index(
        in_files=tas,
        slice_mode=["season", [12, 1]],
        var_name="a_name",
        user_index={
            "index_name": "pouet",
            "calc_operation": operator,
            "extreme_mode": "max",
            "window_width": 7,
        },
    ).compute()
    np.testing.assert_almost_equal(res.pouet.isel(time=0), exp_y1)
    np.testing.assert_almost_equal(res.pouet.isel(time=1), exp_y2)


def test_custom_index_anomaly__season_slice_mode():
    tas = stub_tas(2.0)
    tas.loc[{"time": "2045-01-01"}] = 300
    res = icclim.custom_index(
        in_files=tas,
        slice_mode=["season", [12, 1]],
        var_name="a_name",
        user_index={
            "index_name": "anomaly",
            "calc_operation": CalcOperation.ANOMALY,
            "ref_time_range": [datetime(2042, 1, 1), datetime(2044, 12, 31)],
        },
    ).compute()
    np.testing.assert_almost_equal(res.anomaly, 0.96129032)
