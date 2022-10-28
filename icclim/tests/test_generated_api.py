from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

import icclim
from icclim.ecad.ecad_indices import EcadIndexRegistry
from icclim.generic_indices.generic_indicators import GenericIndicatorRegistry
from icclim.generic_indices.threshold import build_threshold
from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.icclim_logger import VerbosityRegistry
from icclim.models.constants import QUANTILE_BASED, REFERENCE_PERIOD_INDEX
from icclim.models.frequency import FrequencyRegistry
from icclim.models.netcdf_version import NetcdfVersionRegistry
from icclim.models.quantile_interpolation import QuantileInterpolationRegistry
from icclim.models.standard_index import StandardIndex
from icclim.tests.testing_utils import stub_tas
from icclim.user_indices.calc_operation import CalcOperation, CalcOperationRegistry

DEFAULT_ARGS = dict(
    in_files="pouet.nc",
    var_name=None,
    slice_mode=FrequencyRegistry.YEAR,
    time_range=None,
    out_file=None,
    ignore_Feb29th=False,
    netcdf_version=NetcdfVersionRegistry.NETCDF4,
    logs_verbosity=VerbosityRegistry.LOW,
    date_event=False,
)


def build_expected_args(index: StandardIndex):
    expected_call_args = {"index_name": index.short_name.upper()}
    expected_call_args.update(DEFAULT_ARGS)
    qualifiers = [] if index.qualifiers is None else index.qualifiers
    if QUANTILE_BASED in qualifiers:
        expected_call_args.update(
            {
                "base_period_time_range": None,
                "only_leap_years": False,
                "interpolation": QuantileInterpolationRegistry.MEDIAN_UNBIASED.name,
                "save_thresholds": False,
            }
        )
    elif REFERENCE_PERIOD_INDEX in qualifiers:
        expected_call_args.update(
            {
                "base_period_time_range": None,
            }
        )
    if index.threshold is not None:
        if isinstance(index.threshold, str):
            t = build_threshold(index.threshold)
        elif isinstance(index.threshold, (list, tuple)):
            t = []
            for thresh in index.threshold:
                if isinstance(thresh, str):
                    t.append(build_threshold(thresh))
                else:
                    t.append(thresh)
        else:
            t = index.threshold
        expected_call_args.update({"threshold": t})
    expected_call_args.update({"out_unit": index.output_unit})
    return expected_call_args


@patch("icclim.index")
def test_generated_api(generic_index_fun_mock: MagicMock):
    for i in EcadIndexRegistry.values():
        # print(i)
        # GIVEN
        api_index_fun = eval(f"icclim.{i.short_name.lower()}")
        # WHEN
        api_index_fun(**DEFAULT_ARGS)
        # THEN
        expected_call_args = build_expected_args(i)
        generic_index_fun_mock.assert_called_with(**expected_call_args)
    for g in GenericIndicatorRegistry.values():
        print(g)
        # GIVEN
        api_index_fun = eval(f"icclim.{g.name.lower()}")
        # WHEN
        api_index_fun(**DEFAULT_ARGS)
        generic_index_fun_mock.assert_called()


@patch("icclim.index")
def test_custom_index(index_fun_mock: MagicMock):
    user_index_args = dict(
        in_files="pouet_file.nc",
        var_name=None,
        slice_mode=FrequencyRegistry.YEAR,
        time_range=None,
        out_file=None,
        base_period_time_range=None,
        only_leap_years=False,
        ignore_Feb29th=False,
        out_unit=None,
        netcdf_version=NetcdfVersionRegistry.NETCDF4,
        logs_verbosity=VerbosityRegistry.LOW,
        doy_window_width=5,
        save_thresholds=False,
        date_event=False,
        sampling_method="resample",
        min_spell_length=6,
        rolling_window_width=5,
        interpolation="median_unbiased",
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
    # GIVEN
    tas = stub_tas()
    tas.loc[{"time": "2043-02-02"}] = 295
    tas.loc[{"time": "2043-01-01"}] = 303.15  # 30°C 273.15
    # WHEN
    res = icclim.txx(tas, slice_mode=["season", [11, 12, 1, 2]]).compute()
    # THEN
    # missing values for nov, dec of first period
    np.testing.assert_array_equal(res.TXx.isel(time=0), np.NAN)
    np.testing.assert_array_equal(res.TXx.isel(time=1), 30.0)
    np.testing.assert_array_equal(
        res.time_bounds.isel(time=0),
        [np.datetime64("2041-11-01"), np.datetime64("2042-02-28")],
    )


def test_txx__months_slice_mode():
    tas = stub_tas()
    tas.loc[{"time": "2042-11-02"}] = 295
    tas.loc[{"time": "2042-01-01"}] = 303.15  # 30°C 273.15
    res = icclim.txx(tas, slice_mode=["months", [11, 1]]).compute()
    np.testing.assert_array_equal(res.TXx.isel(time=0), 30)
    np.testing.assert_array_equal(res.TXx.isel(time=1), np.NAN)
    np.testing.assert_almost_equal(res.TXx.sel(time="2042-11"), 21.85)
    np.testing.assert_array_equal(
        res.time_bounds.isel(time=0),
        [np.datetime64("2042-01-01"), np.datetime64("2042-01-31")],
    )


# integration test
@pytest.mark.parametrize(
    "operator, expectation_year_1, expectation_year_2",
    [
        (CalcOperationRegistry.MIN, 303.15, 280.15),
        (CalcOperationRegistry.MAX, 303.15, 280.15),
        (CalcOperationRegistry.SUM, 303.15, 280.15),
        # values below 275 are filtered out
        (CalcOperationRegistry.MEAN, 303.15, 280.15),
        (CalcOperationRegistry.EVENT_COUNT, 1, 1),
        (CalcOperationRegistry.MAX_NUMBER_OF_CONSECUTIVE_EVENTS, 1, 1),
    ],
)
def test_custom_index__season_slice_mode(
    operator: CalcOperation, expectation_year_1, expectation_year_2
):
    tas = stub_tas(275.0)
    tas.loc[{"time": "2043-01-01"}] = 303.15
    tas.loc[{"time": "2043-12-01"}] = 280.15
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
    # missing values algo applied for first and last years
    np.testing.assert_almost_equal(res.pouet.isel(time=0), np.NAN)
    np.testing.assert_almost_equal(res.pouet.isel(time=-1), np.NAN)
    np.testing.assert_almost_equal(res.pouet.isel(time=1), expectation_year_1)
    np.testing.assert_almost_equal(res.pouet.isel(time=2), expectation_year_2)


# integration test
@pytest.mark.parametrize(
    "operator, expectation_year_1, expectation_year_2",
    [
        (CalcOperationRegistry.RUN_MEAN, 275.0, 276.0),
        (CalcOperationRegistry.RUN_SUM, 1925.0, 1932.0),
    ],
)
def test_custom_index_run_algos__season_slice_mode(
    operator, expectation_year_1, expectation_year_2
):
    tas = stub_tas(275.0)
    tas.loc[{"time": "2043-12-01"}] = 282.0
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
    )
    # missing values algo applied for first and last years
    np.testing.assert_almost_equal(res.pouet.isel(time=0), np.NAN)
    np.testing.assert_almost_equal(res.pouet.isel(time=-1), np.NAN)
    np.testing.assert_almost_equal(res.pouet.isel(time=1), expectation_year_1)
    np.testing.assert_almost_equal(res.pouet.isel(time=2), expectation_year_2)


def test_custom_index_anomaly__error_single_var():
    tas = stub_tas(2.0)
    with pytest.raises(InvalidIcclimArgumentError):
        # error: it needs 2 vars or 1 var and a ref period
        icclim.custom_index(
            in_files=tas,
            user_index={
                "index_name": "anomaly",
                "calc_operation": CalcOperationRegistry.ANOMALY,
            },
        )


def test_custom_index_anomaly__error_():
    tas = stub_tas(2.0)
    with pytest.raises(InvalidIcclimArgumentError):
        # error: Can't resample the reference variable if it is already a
        # subsample of the studied variable. (need another sampling_method)
        icclim.custom_index(
            in_files=tas,
            slice_mode=["season", [12, 1]],
            base_period_time_range=[datetime(2042, 1, 1), datetime(2044, 12, 31)],
            user_index={
                "index_name": "anomaly",
                "calc_operation": CalcOperationRegistry.ANOMALY,
            },
        )


def test_custom_index_anomaly__datetime_ref_period():
    tas = stub_tas(2.0)
    tas.loc[{"time": "2045-01-01"}] = 300
    res = icclim.custom_index(
        in_files=tas,
        slice_mode=["season", [12, 1]],
        base_period_time_range=[datetime(2042, 1, 1), datetime(2044, 12, 31)],
        sampling_method="groupby_ref_and_resample_study",
        user_index={
            "index_name": "anomaly",
            "calc_operation": CalcOperationRegistry.ANOMALY,
        },
    ).compute()
    # missing values algo applied for first and last years
    np.testing.assert_almost_equal(res.anomaly.sel(time="2041"), np.NAN)
    np.testing.assert_almost_equal(res.anomaly.sel(time="2042"), 0)
    np.testing.assert_almost_equal(res.anomaly.sel(time="2043"), 0)
    np.testing.assert_almost_equal(res.anomaly.sel(time="2044"), 4.80645161)
    np.testing.assert_almost_equal(res.anomaly.sel(time="2045"), 0)
    np.testing.assert_almost_equal(res.anomaly.sel(time="2046"), np.NAN)


def test_custom_index_anomaly__groupby_and_resample_month():
    tas = stub_tas(2.0)
    tas.loc[{"time": "2045-01-01"}] = 300
    res = icclim.custom_index(
        in_files=tas,
        slice_mode="month",
        base_period_time_range=[datetime(2042, 1, 1), datetime(2044, 12, 31)],
        sampling_method="groupby_ref_and_resample_study",
        user_index={
            "index_name": "anomaly",
            "calc_operation": CalcOperationRegistry.ANOMALY,
        },
    ).compute()
    np.testing.assert_almost_equal(res.anomaly.sel(time="2045-01"), 9.61290323)


def test_custom_index_anomaly__groupby_and_resample_year():
    tas = stub_tas(2.0)
    tas.loc[{"time": "2045-01-01"}] = 300
    res = icclim.custom_index(
        in_files=tas,
        slice_mode="year",
        base_period_time_range=[datetime(2042, 1, 1), datetime(2044, 12, 31)],
        sampling_method="groupby_ref_and_resample_study",
        user_index={
            "index_name": "anomaly",
            "calc_operation": CalcOperationRegistry.ANOMALY,
        },
    ).compute()
    np.testing.assert_almost_equal(res.anomaly.sel(time="2045"), 0.81643836)


def test_custom_index_anomaly__groupby_and_resample_day():
    tas = stub_tas(2.0)
    tas.loc[{"time": "2045-01-01"}] = 300
    res = icclim.custom_index(
        in_files=tas,
        slice_mode="day",
        base_period_time_range=[datetime(2042, 1, 1), datetime(2044, 12, 31)],
        sampling_method="groupby_ref_and_resample_study",
        user_index={
            "index_name": "anomaly",
            "calc_operation": CalcOperationRegistry.ANOMALY,
        },
    ).compute()
    np.testing.assert_almost_equal(res.anomaly.sel(time="2045-01-01"), 298)


def test_custom_index_anomaly__groupby_and_resample_hour():
    tas = stub_tas(2.0)
    tas.loc[{"time": "2045-01-01"}] = 300
    with pytest.raises(NotImplementedError):
        icclim.custom_index(
            in_files=tas,
            slice_mode="hour",
            base_period_time_range=[datetime(2042, 1, 1), datetime(2044, 12, 31)],
            sampling_method="groupby_ref_and_resample_study",
            user_index={
                "index_name": "anomaly",
                "calc_operation": CalcOperationRegistry.ANOMALY,
            },
        )


def test_custom_index_anomaly__grouby_season():
    tas = stub_tas(2.0)
    tas.loc[{"time": "2045-01-01"}] = 300
    res = icclim.custom_index(
        in_files=tas,
        slice_mode=["season", [12, 1]],
        base_period_time_range=[datetime(2042, 1, 1), datetime(2044, 12, 31)],
        sampling_method="groupby",
        user_index={
            "index_name": "anomaly",
            "calc_operation": CalcOperationRegistry.ANOMALY,
        },
    ).compute()
    # missing values algo applied for first and last years
    np.testing.assert_almost_equal(res.anomaly, 0.96129032)


def test_custom_index_anomaly__grouby_month():
    tas = stub_tas(2.0)
    tas.loc[{"time": "2045-01-01"}] = 300
    res = icclim.custom_index(
        in_files=tas,
        slice_mode="month",
        base_period_time_range=[datetime(2042, 1, 1), datetime(2044, 12, 31)],
        sampling_method="groupby",
        user_index={
            "index_name": "anomaly",
            "calc_operation": CalcOperationRegistry.ANOMALY,
        },
    ).compute()
    # missing values algo applied for first and last years
    assert len(res.anomaly.month) == 12
    np.testing.assert_almost_equal(res.anomaly.sel(month=2), 0)
    np.testing.assert_almost_equal(res.anomaly.sel(month=1), 1.92258065)
