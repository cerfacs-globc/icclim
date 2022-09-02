from __future__ import annotations

import os
from datetime import datetime
from unittest.mock import MagicMock, patch

import cftime
import numpy as np
import pandas as pd
import pytest
import xarray as xr

import icclim
from icclim.ecad.ecad_indices import EcadIndexRegistry
from icclim.models.constants import (
    ICCLIM_VERSION,
    PART_OF_A_WHOLE_UNIT,
    REFERENCE_PERIOD_ID,
    UNITS_ATTRIBUTE_KEY,
)
from icclim.models.frequency import FrequencyRegistry
from icclim.models.index_group import IndexGroupRegistry
from icclim.models.threshold import Threshold
from icclim.tests.testing_utils import K2C, stub_pr, stub_tas


@patch("icclim.main.index")
@patch("icclim.icclim_logger.IcclimLogger")
def test_deprecated_indice(log_mock: MagicMock, index_mock: MagicMock):
    icclim.main.log = log_mock
    icclim.indice()
    log_mock.deprecation_warning.assert_called_once_with(
        old="icclim.indice", new="icclim.index"
    )
    index_mock.assert_called_once()


HEAT_INDICES = ["SU", "TR", "WSDI", "TG90p", "TN90p", "TX90p", "TXx", "TNx", "CSU"]


@pytest.mark.slow
class Test_Integration:
    """
    Simple integration test.
    We are not testing here the actual indices results, they are already tested in
    `test_ecad_indices.py` as well as in xclim directly.
    The goal it to make sure every the whole app can run smoothly

    These tests have side effect:
    - writing and removing of "out.nc" file

    """

    OUTPUT_FILE = "out.nc"
    TIME_RANGE = pd.date_range(start="2042-01-01", end="2045-12-31", freq="D")
    CF_TIME_RANGE = xr.cftime_range("2042-01-01", end="2045-12-31", freq="D")
    data = xr.DataArray(
        data=(np.full(len(TIME_RANGE), 20).reshape((len(TIME_RANGE), 1, 1))),
        dims=["time", "lat", "lon"],
        coords=dict(lat=[42], lon=[42], time=TIME_RANGE),
        attrs={UNITS_ATTRIBUTE_KEY: "degC"},
    )

    data_cf_time = xr.DataArray(
        data=(np.full(len(TIME_RANGE), 20).reshape((len(TIME_RANGE), 1, 1))),
        dims=["time", "lat", "lon"],
        coords=dict(lat=[42], lon=[42], time=CF_TIME_RANGE),
        attrs={UNITS_ATTRIBUTE_KEY: "degC"},
    )

    # usually, time_bounds is not properly decoded an keep a object dtype
    time_bounds = xr.DataArray(
        data=[[t, t + +np.timedelta64(1, "h")] for t in data.time.values],
        dims=["time", "bounds"],
        coords=dict(bounds=[0, 1], time=TIME_RANGE),
    ).astype("object")

    dataset_with_time_bounds = xr.Dataset(
        dict(data=data, time_bounds=time_bounds),
    )

    @pytest.fixture(autouse=True)
    def cleanup(self):
        # setup
        # ...
        yield
        # teardown
        try:
            os.remove(self.OUTPUT_FILE)
        except FileNotFoundError:
            pass

    def test_index_SU(self):
        tas = stub_tas(tas_value=26 + K2C)
        tas[:5] = 0
        res = icclim.index(
            index_name="SU", in_files=tas, out_file=self.OUTPUT_FILE, slice_mode="ms"
        )
        assert f"icclim version: {ICCLIM_VERSION}" in res.attrs["history"]
        assert res.SU.isel(time=0) == 26  # January

    def test_index_SU__on_dataset(self):
        res = icclim.index(
            index_name="SU",
            var_name="data",
            in_files=self.dataset_with_time_bounds,
            out_file=self.OUTPUT_FILE,
        )
        assert f"icclim version: {ICCLIM_VERSION}" in res.attrs["history"]
        np.testing.assert_array_equal(0, res.SU)

    def test_index_DTR(self):
        ds = self.data.to_dataset(name="toto")
        ds["tutu"] = self.data
        res = icclim.index(
            index_name="DTR",
            in_files=ds,
            out_file=self.OUTPUT_FILE,
            var_name=["toto", "tutu"],
        )
        assert f"icclim version: {ICCLIM_VERSION}" in res.attrs["history"]
        np.testing.assert_array_equal(0, res.DTR)

    def test_index_CD(self):
        ds = self.data.to_dataset(name="tas")
        ds["pr"] = self.data.copy(deep=True)
        ds["pr"].attrs[UNITS_ATTRIBUTE_KEY] = "kg m-2 d-1"
        res = icclim.index(
            index_name="CD",
            in_files=ds,
            out_file=self.OUTPUT_FILE,
        )
        assert f"icclim version: {ICCLIM_VERSION}" in res.attrs["history"]
        np.testing.assert_array_equal(0, res.CD)

    def test__preserve_initial_history(self):
        self.data.attrs["history"] = "pouet pouet cacahuête"
        res = icclim.su(in_files=self.data)
        assert "pouet pouet cacahuête" in res.attrs["history"]

    def test_index_SU__time_selection(self):
        # WHEN
        res_string_dates = icclim.index(
            index_name="SU",
            in_files=self.data,
            out_file=self.OUTPUT_FILE,
            time_range=("19 july 2042", "14 august 2044"),
        )
        res_datetime_dates = icclim.index(
            index_name="SU",
            in_files=self.data,
            out_file=self.OUTPUT_FILE,
            time_range=[datetime(2042, 7, 19), datetime(2044, 8, 14)],
        )
        # THEN
        assert res_string_dates.time_bounds[0, 0] == np.datetime64(datetime(2042, 1, 1))
        assert res_string_dates.time_bounds[0, 1] == np.datetime64(
            datetime(2042, 12, 31)
        )
        np.testing.assert_array_equal(res_string_dates.SU, res_datetime_dates.SU)
        np.testing.assert_array_equal(
            res_string_dates.time_bounds, res_datetime_dates.time_bounds
        )

    def test_index_SU__pandas_time_slice_mode(self):
        # WHEN
        res = icclim.index(
            index_name="SU",
            in_files=self.data,
            out_file=self.OUTPUT_FILE,
            slice_mode="2W-WED",
        )
        # THEN
        assert res.time_bounds[0, 0] == np.datetime64(datetime(2042, 1, 1))
        assert res.time_bounds[0, 1] == np.datetime64(datetime(2042, 1, 14))
        assert (
            res.SU.attrs["standard_name"]
            == "number_of_days_with_maximum_air_temperature_above_threshold"
        )

    def test_index_SU__monthy_sampled(self):
        res = icclim.index(
            index_name="SU",
            in_files=self.data,
            out_file=self.OUTPUT_FILE,
            slice_mode=FrequencyRegistry.MONTH,
        )
        np.testing.assert_array_equal(0, res.SU)
        np.testing.assert_array_equal(
            len(np.unique(self.TIME_RANGE.year)) * 12, len(res.time)
        )

    def test_index_SU__monthy_sampled_cf_time(self):
        res = icclim.index(
            index_name="SU",
            in_files=self.data_cf_time,
            out_file=self.OUTPUT_FILE,
            slice_mode=FrequencyRegistry.MONTH,
        )
        np.testing.assert_array_equal(0, res.SU)
        np.testing.assert_array_equal(
            len(np.unique(self.TIME_RANGE.year)) * 12, len(res.time)
        )
        assert res.time_bounds.sel(time=res.time[0])[0] == cftime.DatetimeGregorian(
            2042, 1, 1, 0, 0, 0, 0
        )
        assert res.time_bounds.sel(time=res.time[0])[1] == cftime.DatetimeGregorian(
            2042, 1, 31, 0, 0, 0, 0
        )

    def test_index_SU__DJF_cf_time(self):
        res = icclim.index(
            index_name="SU",
            in_files=self.data_cf_time,
            out_file=self.OUTPUT_FILE,
            slice_mode=FrequencyRegistry.DJF,
        )
        np.testing.assert_array_equal(res.SU.isel(time=0), np.NAN)
        np.testing.assert_array_equal(res.SU.isel(time=1), 0)
        # "+ 1" because DJF sampling create a december month with nans before first year
        np.testing.assert_array_equal(
            len(np.unique(self.TIME_RANGE.year)) + 1, len(res.time)
        )
        assert res.time_bounds.sel(time=res.time[0])[0] == cftime.DatetimeGregorian(
            2041, 12, 1, 0, 0, 0, 0
        )
        assert res.time_bounds.sel(time=res.time[0])[1] == cftime.DatetimeGregorian(
            2042, 2, 28, 0, 0, 0, 0
        )

    def test_indices__from_DataArray(self):
        res = icclim.indices(
            index_group=IndexGroupRegistry.HEAT,
            in_files=self.data,
            out_file=self.OUTPUT_FILE,
        )
        for i in HEAT_INDICES:
            assert res[i] is not None

    def test_indices__snow_indices(self):
        ds = self.data.to_dataset(name="tas")
        ds["prec"] = self.data.copy(deep=True)
        ds["prec"].attrs[UNITS_ATTRIBUTE_KEY] = "cm"
        res = icclim.indices(
            index_group=IndexGroupRegistry.SNOW, in_files=ds, out_file=self.OUTPUT_FILE
        )
        for i in filter(
            lambda i: i.group == IndexGroupRegistry.SNOW, EcadIndexRegistry.values()
        ):
            assert res[i.short_name] is not None

    def test_indices_all_from_Dataset(self):
        ds = self.data.to_dataset(name="tas")
        ds["tasmax"] = self.data
        ds["tasmin"] = self.data
        ds["pr"] = self.data.copy(deep=True)
        ds["pr"].attrs[UNITS_ATTRIBUTE_KEY] = "kg m-2 d-1"
        ds["prec"] = self.data.copy(deep=True)
        ds["prec"].attrs[UNITS_ATTRIBUTE_KEY] = "cm"
        res = icclim.indices(index_group="all", in_files=ds, out_file=self.OUTPUT_FILE)
        for i in EcadIndexRegistry.values():
            assert res[i.short_name] is not None

    def test_indices_all_from_Dataset__seasonal(self):
        ds = self.data.to_dataset(name="tas")
        ds["tasmax"] = self.data
        ds["tasmin"] = self.data
        ds["pr"] = self.data.copy(deep=True)
        ds["pr"].attrs[UNITS_ATTRIBUTE_KEY] = "kg m-2 d-1"
        ds["prec"] = self.data.copy(deep=True)
        ds["prec"].attrs[UNITS_ATTRIBUTE_KEY] = "cm"
        res = icclim.indices(
            index_group="all",
            in_files=ds,
            out_file=self.OUTPUT_FILE,
            slice_mode=["season", [1, 2, 3]],
        )
        for i in EcadIndexRegistry.values():
            assert res[i.short_name] is not None

    def test_indices_all_from_Dataset__between_dates_seasonal(self):
        ds = self.data.to_dataset(name="tas")
        ds["tasmax"] = self.data
        ds["tasmin"] = self.data
        ds["pr"] = self.data.copy(deep=True)
        ds["pr"].attrs[UNITS_ATTRIBUTE_KEY] = "kg m-2 d-1"
        ds["prec"] = self.data.copy(deep=True)
        ds["prec"].attrs[UNITS_ATTRIBUTE_KEY] = "cm"
        res = icclim.indices(
            index_group="all",
            in_files=ds,
            out_file=self.OUTPUT_FILE,
            slice_mode=["season", ["07-19", "08-14"]],
        )
        for i in EcadIndexRegistry.values():
            assert res[i.short_name] is not None

    def test_indices_all_from_Dataset__JFM_seasonal(self):
        ds = self.data.to_dataset(name="tas")
        ds["tasmax"] = self.data
        ds["tasmin"] = self.data
        ds["pr"] = self.data.copy(deep=True)
        ds["pr"].attrs[UNITS_ATTRIBUTE_KEY] = "kg m-2 d-1"
        ds["prec"] = self.data.copy(deep=True)
        ds["prec"].attrs[UNITS_ATTRIBUTE_KEY] = "cm"
        res = icclim.indices(
            index_group="all",
            in_files=ds,
            out_file=self.OUTPUT_FILE,
            slice_mode=["season", [1, 2, 3]],
        )
        for i in EcadIndexRegistry.values():
            assert res[i.short_name] is not None

    def test_indices_all_from_Dataset__between_year_season(self):
        ds = self.data.to_dataset(name="tas")
        ds["tasmax"] = self.data
        ds["tasmin"] = self.data
        ds["pr"] = self.data.copy(deep=True)
        ds["pr"].attrs[UNITS_ATTRIBUTE_KEY] = "kg m-2 d-1"
        ds["prec"] = self.data.copy(deep=True)
        ds["prec"].attrs[UNITS_ATTRIBUTE_KEY] = "cm"
        res = icclim.indices(
            index_group="all",
            in_files=ds,
            out_file=self.OUTPUT_FILE,
            slice_mode=["season", [12, 1, 2, 3]],
        )
        for i in EcadIndexRegistry.values():
            assert res[i.short_name] is not None

    def test_indices_all_ignore_error(self):
        ds = self.data.to_dataset(name="tas")
        ds["tasmax"] = self.data
        ds["tasmin"] = self.data
        ds["pr"] = self.data.copy(deep=True)
        ds["pr"].attrs[UNITS_ATTRIBUTE_KEY] = "kg m-2 d-1"
        res: xr.Dataset = icclim.indices(
            index_group="all",
            in_files=ds,
            out_file=self.OUTPUT_FILE,
            ignore_error=True,
            slice_mode="DJF",
        ).compute()
        for i in EcadIndexRegistry.values():
            # No variable in input to compute snow indices
            if i.group == IndexGroupRegistry.SNOW:
                assert res.data_vars.get(i.short_name, None) is None
            else:
                assert res[i.short_name] is not None

    def test_indices_all__error(self):
        ds = self.data.to_dataset(name="tas")
        ds["tasmax"] = self.data
        ds["tasmin"] = self.data
        ds["pr"] = self.data.copy(deep=True)
        ds["pr"].attrs[UNITS_ATTRIBUTE_KEY] = "kg m-2 d-1"
        with pytest.raises(Exception):
            icclim.indices(
                index_group="all",
                in_files=ds,
                out_file=self.OUTPUT_FILE,
                ignore_error=False,
            )

    def test_index_TR(self):
        tas = stub_tas(tas_value=26 + K2C)
        tas[:5] = 0
        res = icclim.index(
            index_name="TR", in_files=tas, out_file=self.OUTPUT_FILE, slice_mode="ms"
        )
        assert f"icclim version: {ICCLIM_VERSION}" in res.attrs["history"]
        assert res.TR.isel(time=0) == 26  # January

    def test_index_prcptot(self):
        pr = stub_pr(value=2)
        pr[:10] = 0
        res = icclim.index(
            index_name="prcptot",
            in_files=pr,
            out_file=self.OUTPUT_FILE,
            slice_mode="ms",
        )
        assert res.isel(time=0) == 42.0

    def test_index_csu(self):
        tas = stub_tas(tas_value=26 + K2C)
        tas[10:15] = 0
        res = icclim.index(
            index_name="csu", in_files=tas, out_file=self.OUTPUT_FILE, slice_mode="ms"
        )
        assert res.isel(time=0) == 16

    def test_index_gd4(self):
        tas = stub_tas(tas_value=26 + K2C)
        tas[5:15] = 0
        res = icclim.index(
            index_name="gd4", in_files=tas, out_file=self.OUTPUT_FILE, slice_mode="ms"
        )
        expected = (26 - 4) * 21
        assert (
            res.isel(time=0) == expected
        )  # 21 days in January above 4 degC (at 26degC)

    def test_index_cfd(self):
        tas = stub_tas(tas_value=26 + K2C)
        tas[5:15] = 0
        res = icclim.index(
            index_name="cfd", in_files=tas, out_file=self.OUTPUT_FILE, slice_mode="ms"
        )
        assert res.isel(time=0) == 1

    def test_index_fd(self):
        tas = stub_tas(tas_value=26 + K2C)
        tas[5:15] = 0
        tas[20:25] = 0
        res = icclim.index(
            index_name="fd", in_files=tas, out_file=self.OUTPUT_FILE, slice_mode="ms"
        )
        assert res.isel(time=0) == 15

    def test_index_hd17(self):
        tas = stub_tas(tas_value=27 + K2C)
        tas[5:10] = 0
        res = icclim.index(
            index_name="hd17", in_files=tas, out_file=self.OUTPUT_FILE, slice_mode="ms"
        )
        assert res.isel(time=0) == 5 * (17 + K2C)

    def test_index_tx90p__no_bootstrap_because_one_single_year_of_ref(self):
        tas = stub_tas(tas_value=27 + K2C)
        tas[5:15] = 0
        res = icclim.index(
            index_name="tx90p",
            in_files=tas,
            doy_window_width=5,
            base_period_time_range=("2042-01-01", "2042-12-31"),
            time_range=("2042-01-01", "2045-12-31"),
            out_file=self.OUTPUT_FILE,
            slice_mode="ms",
        )
        assert REFERENCE_PERIOD_ID not in res.TX90p.attrs
        # The 90th percentile here is clipped to the maximum of tas window (27 degC)
        # due to the "median_unbiased" interpolation.
        # Thus no value are strictly above it.
        assert res.TX90p.isel(time=0) == 0

    def test_index_tx90p__no_bootstrap_because_no_overlap(self):
        tas = stub_tas(tas_value=27 + K2C)
        tas[5:10] = 0
        res = icclim.index(
            index_name="tx90p",
            in_files=tas,
            doy_window_width=1,
            time_range=("2043-01-01", "2045-12-31"),
            base_period_time_range=("2042-01-01", "2042-12-31"),
            out_file=self.OUTPUT_FILE,
            slice_mode="ms",
        )
        assert REFERENCE_PERIOD_ID not in res.TX90p.attrs
        # resample_doy add a day where 90th per is below tas
        assert res.TX90p.isel(time=0) == 6

    def test_index_tx90p__bootstrap_2_years(self):
        tas = stub_tas(tas_value=27 + K2C)
        tas[5:10] = 0
        res = icclim.index(
            index_name="tx90p",
            in_files=tas,
            doy_window_width=1,
            time_range=("2042-01-01", "2045-12-31"),
            base_period_time_range=("2042-01-01", "2043-12-31"),
            out_file=self.OUTPUT_FILE,
            slice_mode="ms",
        )
        assert REFERENCE_PERIOD_ID in res.TX90p.attrs
        # 2042 values are compared to 2043's 90th percentile due to bootstrap
        assert res.TX90p.sel(time="2042-01") == 0
        # 2043 values are compared to 2042's 90th percentile due to bootstrap
        assert res.TX90p.sel(time="2043-01") == 5

    def test_index_wsdi__no_bootstrap_because_no_overlap(self):
        tas = stub_tas(tas_value=27 + K2C)
        tas[0:10] = 0
        res = icclim.index(
            index_name="wsdi",
            in_files=tas,
            doy_window_width=1,
            time_range=("2043-01-01", "2045-12-31"),
            base_period_time_range=("2042-01-01", "2042-12-31"),
            out_file=self.OUTPUT_FILE,
            slice_mode="ms",
        )
        assert REFERENCE_PERIOD_ID not in res.WSDI.attrs
        # 1 more day than in tas because of resample_doy that interpolate values
        assert res.WSDI.isel(time=0) == 11

    def test_index_csdi__no_bootstrap_because_no_overlap(self):
        tas = stub_tas(tas_value=2 + K2C)
        tas[0:10] = 35 + K2C
        res = icclim.index(
            index_name="csdi",
            in_files=tas,
            doy_window_width=1,
            time_range=("2043-01-01", "2045-12-31"),
            base_period_time_range=("2042-01-01", "2042-12-31"),
            out_file=self.OUTPUT_FILE,
            slice_mode="ms",
        )
        assert REFERENCE_PERIOD_ID not in res.CSDI.attrs
        print(res.CSDI.isel(time=0).compute())
        # 1 more day than in tas because of resample_doy that interpolate values
        assert res.CSDI.isel(time=0) == 11

    def test_count_occurrences__date_event(self):
        tas = stub_tas(tas_value=2 + K2C)
        tas[10] = 35 + K2C
        res = icclim.index(
            tas,
            var_name=["tmin"],
            index_name="count_occurrences",
            threshold=">= 22 degree_Celsius",
            slice_mode="month",
            date_event=True,
        ).compute()
        assert "event_date_start" in res.coords
        assert "event_date_end" in res.coords
        assert res.count_occurrences.isel(time=0).event_date_end == np.datetime64(
            "2042-01-11"
        )
        assert res.count_occurrences.isel(time=0).event_date_start == np.datetime64(
            "2042-01-11"
        )

    def test_count_occurrences__to_percent(self):
        tas = stub_tas(tas_value=2 + K2C)
        tas[10] = 35 + K2C
        res = icclim.index(
            tas,
            var_name=["tmin"],
            index_name="count_occurrences",
            threshold=">= 22 degree_Celsius",
            slice_mode="month",
            out_unit="%",
        ).compute()
        assert res.count_occurrences.attrs[UNITS_ATTRIBUTE_KEY] == "%"
        assert res.count_occurrences.isel(time=0) == 1 / 31 * 100

    def test_excess__on_doy_percentile(self):
        tas = stub_tas(tas_value=10 + K2C).rename("tas")
        tas[10] = 5 + K2C
        res = icclim.index(
            tas,
            index_name="excess",
            time_range=["2044-01-01", "2045-12-31"],
            threshold=Threshold(
                "10 doy_per",
                doy_window_width=1,
                reference_period=["2042-01-01", "2042-12-31"],
            ),
            slice_mode="month",
            save_thresholds=True,
        ).compute()
        # not exactly 5 because of resample_doy interpolation
        np.testing.assert_almost_equal(res.excess.isel(time=0), 5.01369863)
        print(res)
        assert "tas_thresholds" in res.data_vars

    def test_deficit__on_doy_percentile(self):
        tas = stub_tas(tas_value=5 + K2C).rename("tas")
        tas[10] = 10 + K2C
        res = icclim.index(
            tas,
            index_name="deficit",
            time_range=["2044-01-01", "2045-12-31"],
            threshold=Threshold(
                "10 doy_per",
                doy_window_width=1,
                reference_period=["2042-01-01", "2042-12-31"],
            ),
            slice_mode="month",
            save_thresholds=True,
        ).compute()
        # not exactly 5 because of resample_doy interpolation
        np.testing.assert_almost_equal(res.deficit.isel(time=0), 5.01369863)
        assert "tas_thresholds" in res.data_vars

    def test_fraction_of_total(self):
        tas = stub_tas(tas_value=25 + K2C).rename("tas")
        tas[tas.time.dt.date == np.datetime64("2042-06-10")] = 10 + K2C
        res = icclim.index(
            tas,
            index_name="fraction_of_total",
            threshold="> 20 degree_Celsius",
            slice_mode="jja",
        ).compute()
        np.testing.assert_almost_equal(res.fraction_of_total.isel(time=0), 0.98967164)
        assert res.fraction_of_total.isel(time=1) == 1
        assert res.fraction_of_total.attrs[UNITS_ATTRIBUTE_KEY] == PART_OF_A_WHOLE_UNIT

    def test_fraction_of_total_percent(self):
        tas = stub_tas(tas_value=25 + K2C).rename("tas")
        tas[tas.time.dt.date == np.datetime64("2042-06-10")] = 10 + K2C
        res = icclim.index(
            tas,
            index_name="fraction_of_total",
            threshold="> 20 degree_Celsius",
            out_unit="%",
            slice_mode="jja",
        ).compute()
        np.testing.assert_almost_equal(res.fraction_of_total.isel(time=0), 98.96716372)
        assert res.fraction_of_total.isel(time=1) == 100
        assert res.fraction_of_total.attrs[UNITS_ATTRIBUTE_KEY] == "%"

    def test_std(self):
        tas = stub_tas(tas_value=25 + K2C).rename("tas")
        res = icclim.index(
            tas,
            index_name="standard_deviation",
        ).compute()
        np.testing.assert_almost_equal(res.standard_deviation.isel(time=0), 0)
