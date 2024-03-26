from __future__ import annotations

import contextlib
import datetime as dt
from pathlib import Path
from unittest.mock import MagicMock, patch

import cftime
import icclim
import numpy as np
import pandas as pd
import pint
import pytest
import xarray as xr
from icclim import __version__ as icclim_version
from icclim._core.constants import PART_OF_A_WHOLE_UNIT, REFERENCE_PERIOD_ID, UNITS_KEY
from icclim._core.model.index_group import IndexGroupRegistry
from icclim.ecad.registry import EcadIndexRegistry
from icclim.exception import InvalidIcclimArgumentError
from icclim.frequency import FrequencyRegistry
from icclim.threshold.factory import build_threshold

from tests.testing_utils import K2C, stub_pr, stub_tas


@patch("icclim.main.index")
@patch("icclim.logger.IcclimLogger")
def test_deprecated_indice(log_mock: MagicMock, index_mock: MagicMock) -> None:
    icclim.main.log = log_mock
    icclim.indice()
    log_mock.deprecation_warning.assert_called_once_with(
        old="icclim.indice",
        new="icclim.index",
    )
    index_mock.assert_called_once()


HEAT_INDICES = ["SU", "TR", "WSDI", "TG90p", "TN90p", "TX90p", "TXx", "TNx", "CSU"]


@pytest.mark.slow()
class TestIntegration:
    """
    Integration tests.
    We are not testing here the actual indices results, they are already tested in
    `test_ecad_indices.py` as well as in xclim directly.
    The goal is to make sure the whole app can run smoothly.

    These tests have side effect:
    - writing and removing of "out.nc" file

    """

    OUTPUT_FILE = Path("out.nc")
    TIME_RANGE = pd.date_range(start="2042-01-01", end="2045-12-31", freq="D")
    CF_TIME_RANGE = xr.cftime_range("2042-01-01", end="2045-12-31", freq="D")
    data = xr.DataArray(
        data=(np.full(len(TIME_RANGE), 20).reshape((len(TIME_RANGE), 1, 1))),
        dims=["time", "lat", "lon"],
        coords={"lat": [42], "lon": [42], "time": TIME_RANGE},
        attrs={UNITS_KEY: "degC"},
    )
    full_data = data.to_dataset(name="tas")
    full_data["tasmax"] = data
    full_data["tasmin"] = data
    full_data["pr"] = data.copy(deep=True)
    full_data["pr"].attrs[UNITS_KEY] = "kg m-2 d-1"
    full_data["snd"] = data.copy(deep=True)
    full_data["snd"].attrs[UNITS_KEY] = "cm"
    full_data["DD"] = data.copy(deep=True)
    full_data["DD"].attrs[UNITS_KEY] = "degree"
    full_data["wsgs_max"] = data.copy(deep=True)
    full_data["wsgs_max"].attrs[UNITS_KEY] = "m/s"
    full_data["sfcWind"] = data.copy(deep=True)
    full_data["sfcWind"].attrs[UNITS_KEY] = "m/s"
    full_data["psl"] = data.copy(deep=True)
    full_data["psl"].attrs[UNITS_KEY] = "Pa"
    full_data["sund"] = data.copy(deep=True)
    full_data["sund"].attrs[UNITS_KEY] = "hours"
    full_data["hurs"] = data.copy(deep=True)
    full_data["hurs"].attrs[UNITS_KEY] = "%"

    data_cf_time = xr.DataArray(
        data=(np.full(len(TIME_RANGE), 20).reshape((len(TIME_RANGE), 1, 1))),
        dims=["time", "lat", "lon"],
        coords={"lat": [42], "lon": [42], "time": CF_TIME_RANGE},
        attrs={UNITS_KEY: "degC"},
    )

    # usually, time_bounds is not properly decoded an keep a object dtype
    time_bounds = xr.DataArray(
        data=[[t, t + np.timedelta64(1, "h")] for t in data.time.values],
        dims=["time", "bounds"],
        coords={"bounds": [0, 1], "time": TIME_RANGE},
    ).astype("object")

    dataset_with_time_bounds = xr.Dataset(
        {"data": data, "time_bounds": time_bounds},
    )

    not_spi_indices = tuple(
        filter(lambda x: "spi" not in x.short_name.lower(), EcadIndexRegistry.values()),
    )

    @pytest.fixture(autouse=True)
    def _cleanup(self):
        # setup
        # ...
        yield
        # teardown
        with contextlib.suppress(FileNotFoundError):
            self.OUTPUT_FILE.unlink()

    def test_index_su(self) -> None:
        tas = stub_tas(tas_value=26 + K2C)
        tas[:5] = 0
        res = icclim.index(
            index_name="SU",
            in_files=tas,
            out_file=self.OUTPUT_FILE,
            slice_mode="ms",
        )
        assert f"icclim version: {icclim_version}" in res.attrs["history"]
        assert res.SU.isel(time=0) == 26  # January

    def test_index_su__on_dataset(self) -> None:
        res = icclim.index(
            index_name="SU",
            var_name="data",
            in_files=self.dataset_with_time_bounds,
            out_file=self.OUTPUT_FILE,
        )
        assert f"icclim version: {icclim_version}" in res.attrs["history"]
        np.testing.assert_array_equal(0, res.SU)

    def test_index_dtr(self) -> None:
        ds = self.data.to_dataset(name="toto")
        ds["tutu"] = self.data + 10
        res = icclim.index(
            index_name="DTR",
            in_files=ds,
            out_file=self.OUTPUT_FILE,
            var_name=["toto", "tutu"],
        )
        assert f"icclim version: {icclim_version}" in res.attrs["history"]
        np.testing.assert_array_equal(-10, res.DTR)

    def test_index_dtr__with_unit_conversion(self) -> None:
        ds = self.data.to_dataset(name="toto")
        ds["tutu"] = self.data + 10
        ds["toto"].attrs["units"] = "K"
        ds["tutu"].attrs["units"] = "K"
        res = icclim.dtr(
            in_files=ds,
            out_file=self.OUTPUT_FILE,
            var_name=["toto", "tutu"],
        )
        assert f"icclim version: {icclim_version}" in res.attrs["history"]
        np.testing.assert_array_equal(-10, res.DTR)
        np.testing.assert_array_equal("°C", res.DTR.attrs["units"])

    def test_index_cd(self) -> None:
        ds = self.data.to_dataset(name="tas")
        ds["pr"] = self.data.copy(deep=True)
        ds["pr"].attrs[UNITS_KEY] = "kg m-2 d-1"
        res = icclim.index(
            index_name="CD",
            in_files=ds,
            out_file=self.OUTPUT_FILE,
        )
        assert f"icclim version: {icclim_version}" in res.attrs["history"]
        np.testing.assert_array_equal(0, res.CD)

    def test__preserve_initial_history(self) -> None:
        self.data.attrs["history"] = "pouet pouet cacahuête"
        res = icclim.su(in_files=self.data)
        assert "pouet pouet cacahuête" in res.attrs["history"]

    def test_index_su__time_selection(self) -> None:
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
            time_range=[
                dt.datetime(2042, 7, 19, tzinfo=dt.timezone.utc),
                dt.datetime(2044, 8, 14, tzinfo=dt.timezone.utc),
            ],
        )
        # THEN
        assert res_string_dates.time_bounds[0, 0] == np.datetime64(
            dt.datetime(2042, 1, 1, tzinfo=dt.timezone.utc),
        )
        assert res_string_dates.time_bounds[0, 1] == np.datetime64(
            dt.datetime(2042, 12, 31, tzinfo=dt.timezone.utc),
        )
        np.testing.assert_array_equal(res_string_dates.SU, res_datetime_dates.SU)
        np.testing.assert_array_equal(
            res_string_dates.time_bounds,
            res_datetime_dates.time_bounds,
        )

    def test_index_su__pandas_time_slice_mode(self) -> None:
        # WHEN
        res = icclim.index(
            index_name="SU",
            in_files=self.data,
            out_file=self.OUTPUT_FILE,
            slice_mode="2W-WED",
        )
        # THEN
        assert res.time_bounds[0, 0] == np.datetime64(
            dt.datetime(2042, 1, 1, tzinfo=dt.timezone.utc),
        )
        assert res.time_bounds[0, 1] == np.datetime64(
            dt.datetime(2042, 1, 14, tzinfo=dt.timezone.utc),
        )
        assert (
            res.SU.attrs["standard_name"]
            == "number_of_days_when_maximum_air_temperature_is_greater_than_threshold"
        )
        assert (
            res.SU.attrs["long_name"]
            == "Number of days when maximum air temperature is greater than 25"
            " degC for each 2 wednesday starting week(s)."
        )

    def test_index_su__monthy_sampled(self) -> None:
        res = icclim.index(
            index_name="SU",
            in_files=self.data,
            out_file=self.OUTPUT_FILE,
            slice_mode=FrequencyRegistry.MONTH,
        )
        np.testing.assert_array_equal(0, res.SU)
        np.testing.assert_array_equal(
            len(np.unique(self.TIME_RANGE.year)) * 12,
            len(res.time),
        )

    def test_index_su__monthy_sampled_cf_time(self) -> None:
        res = icclim.index(
            index_name="SU",
            in_files=self.data_cf_time,
            out_file=self.OUTPUT_FILE,
            slice_mode=FrequencyRegistry.MONTH,
        )
        np.testing.assert_array_equal(0, res.SU)
        np.testing.assert_array_equal(
            len(np.unique(self.TIME_RANGE.year)) * 12,
            len(res.time),
        )
        assert res.time_bounds.sel(time=res.time[0])[0] == cftime.DatetimeGregorian(
            2042,
            1,
            1,
            0,
            0,
            0,
            0,
        )
        assert res.time_bounds.sel(time=res.time[0])[1] == cftime.DatetimeGregorian(
            2042,
            1,
            31,
            0,
            0,
            0,
            0,
        )

    def test_index_su__djf_cf_time(self) -> None:
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
            len(np.unique(self.TIME_RANGE.year)) + 1,
            len(res.time),
        )
        assert res.time_bounds.sel(time=res.time[0])[0] == cftime.DatetimeGregorian(
            2041,
            12,
            1,
            0,
            0,
            0,
            0,
        )
        assert res.time_bounds.sel(time=res.time[0])[1] == cftime.DatetimeGregorian(
            2042,
            2,
            28,
            0,
            0,
            0,
            0,
        )

    def test_indices__from_dataarray(self) -> None:
        res = icclim.indices(
            index_group=IndexGroupRegistry.HEAT,
            in_files=self.data,
            out_file=self.OUTPUT_FILE,
        )
        for i in HEAT_INDICES:
            assert res[i] is not None

    def test_indices__on_var_name(self) -> None:
        res = icclim.indices(
            index_group="tasmax",
            in_files=self.data,
            out_file=self.OUTPUT_FILE,
        )
        for i in ["SU", "WSDI", "TX90p", "TXx", "CSU", "ID", "TX10p", "TXn"]:
            assert res[i] is not None

    def test_indices__on_index_name(self) -> None:
        res = icclim.indices(
            index_group="tx90p",
            in_files=self.data,
            out_file=self.OUTPUT_FILE,
        )
        for i in ["TX90p"]:
            assert res[i] is not None

    def test_indices__on_var_names(self) -> None:
        ds = self.data.to_dataset(name="tas")
        ds["pr"] = self.data.copy(deep=True)
        ds["pr"].attrs[UNITS_KEY] = "kg m-2 d-1"
        res = icclim.indices(
            index_group=["tas", "pr"],
            in_files=ds,
            out_file=self.OUTPUT_FILE,
            base_period_time_range=("2042-01-01", "2042-12-31"),
        )
        for i in [
            "TG90p",
            "GD4",
            "HD17",
            "TG10p",
            "CDD",
            "PRCPTOT",
            "RR1",
            "SDII",
            "CWD",
            "RR",
            "R10mm",
            "R20mm",
            "RX1day",
            "RX5day",
            "R75p",
            "R75pTOT",
            "R95p",
            "R95pTOT",
            "R99p",
            "R99pTOT",
            "CD",
            "CW",
            "WD",
            "WW",
        ]:
            assert res[i] is not None

    def test_indices__on_group_union(self) -> None:
        ds = self.data.to_dataset(name="tx")
        ds["tn"] = self.data.copy(deep=True)
        ds["tg"] = self.data.copy(deep=True)
        ds["snd"] = self.data.copy(deep=True)
        ds["snd"].attrs[UNITS_KEY] = "mm"
        res = icclim.indices(
            index_group=IndexGroupRegistry.HEAT | IndexGroupRegistry.SNOW,
            in_files=ds,
            out_file=self.OUTPUT_FILE,
        )
        for i in [
            "SU",
            "TR",
            "WSDI",
            "TG90p",
            "TN90p",
            "TX90p",
            "TXx",
            "TNx",
            "CSU",
            "SD",
            "SD1",
            "SD5cm",
            "SD50cm",
        ]:
            assert res[i] is not None

    def test_indices__error(self) -> None:
        ds = self.data.to_dataset(name="tx")
        with pytest.raises(InvalidIcclimArgumentError):
            icclim.indices(
                index_group="wubaluba dub dub",
                in_files=ds,
                out_file=self.OUTPUT_FILE,
            )

    def test_indices__snow_indices(self) -> None:
        ds = self.data.to_dataset(name="tas")
        ds["snd"] = self.data.copy(deep=True)
        ds["snd"].attrs[UNITS_KEY] = "cm"
        res = icclim.indices(
            index_group=IndexGroupRegistry.SNOW,
            in_files=ds,
            out_file=self.OUTPUT_FILE,
        )
        for i in filter(
            lambda i: i.group == IndexGroupRegistry.SNOW,
            EcadIndexRegistry.values(),
        ):
            assert res[i.short_name] is not None

    def test_indices_all_from_dataset(self) -> None:
        res = icclim.indices(
            index_group="all",
            in_files=self.full_data,
            out_file=self.OUTPUT_FILE,
            base_period_time_range=("2042-01-01", "2042-12-31"),
        )
        for i in EcadIndexRegistry.values():
            assert res[i.short_name] is not None

    def test_indices_all_from_dataset__seasonal_spi_error(self) -> None:
        with pytest.raises(InvalidIcclimArgumentError):
            icclim.indices(
                index_group="SPI3",
                in_files=self.full_data,
                out_file=self.OUTPUT_FILE,
                slice_mode=["season", [1, 2, 3]],
                base_period_time_range=("2042-01-01", "2042-12-31"),
            )

    def test_spi6__no_time_bounds(self) -> None:
        dataset = icclim.index(
            index_name="spi6",
            in_files=self.full_data,
            var_name="pr",
            base_period_time_range=["2042-01-01", "2042-06-01"],
        ).load()
        assert "time_bounds" not in dataset.coords

    def test_indices_all_from_dataset__seasonal(self) -> None:
        res = icclim.indices(
            index_group="all",
            in_files=self.full_data,
            out_file=self.OUTPUT_FILE,
            slice_mode=["season", [1, 2, 3]],
            ignore_error=True,
        )
        for i in self.not_spi_indices:
            assert res[i.short_name] is not None

    def test_indices_all_from_dataset__between_dates_seasonal(self) -> None:
        res = icclim.indices(
            index_group="all",
            in_files=self.full_data,
            out_file=self.OUTPUT_FILE,
            slice_mode=["season", ["07-19", "08-14"]],
            ignore_error=True,
        )
        for i in self.not_spi_indices:
            assert res[i.short_name] is not None

    def test_indices_all_from_dataset__jfm_seasonal(self) -> None:
        res = icclim.indices(
            index_group="all",
            in_files=self.full_data,
            out_file=self.OUTPUT_FILE,
            slice_mode=["season", [1, 2, 3]],
            ignore_error=True,
        )
        for i in self.not_spi_indices:
            assert res[i.short_name] is not None

    def test_indices_all_from_dataset__between_year_season(self) -> None:
        res = icclim.indices(
            index_group="all",
            in_files=self.full_data,
            out_file=self.OUTPUT_FILE,
            slice_mode=["season", [12, 1, 2, 3]],
            ignore_error=True,
        )
        for i in self.not_spi_indices:
            assert res[i.short_name] is not None

    def test_indices_all_ignore_error(self) -> None:
        no_snow = self.full_data.copy()
        del no_snow["snd"]
        res: xr.Dataset = icclim.indices(
            index_group="all",
            in_files=no_snow,
            out_file=self.OUTPUT_FILE,
            ignore_error=True,
            slice_mode="DJF",
            base_period_time_range=("2042-01-01", "2042-12-31"),
        ).compute()
        for i in EcadIndexRegistry.values():
            # No variable in input to compute snow indices
            if i.group == IndexGroupRegistry.SNOW or "spi" in i.short_name.lower():
                assert res.data_vars.get(i.short_name, None) is None
            else:
                assert res[i.short_name] is not None

    def test_indices_all__error(self) -> None:
        ds = self.data.to_dataset(name="tas")
        ds["tasmax"] = self.data
        ds["tasmin"] = self.data
        ds["pr"] = self.data.copy(deep=True)
        ds["pr"].attrs[UNITS_KEY] = "kg m-2 d-1"
        with pytest.raises(
            InvalidIcclimArgumentError,
            match=r"Index .* needs the following .*",
        ):
            icclim.indices(
                index_group="all",
                in_files=ds,
                out_file=self.OUTPUT_FILE,
                ignore_error=False,
            )

    def test_index_tr(self) -> None:
        tas = stub_tas(tas_value=26 + K2C)
        tas[:5] = 0
        res = icclim.index(
            index_name="TR",
            in_files=tas,
            out_file=self.OUTPUT_FILE,
            slice_mode="ms",
        )
        assert f"icclim version: {icclim_version}" in res.attrs["history"]
        assert res.TR.isel(time=0) == 26  # January

    def test_index_prcptot(self) -> None:
        pr = stub_pr(value=2)
        pr.attrs[UNITS_KEY] = "mm/day"
        pr[:10] = 0
        res = icclim.prcptot(
            in_files=pr,
            out_file=self.OUTPUT_FILE,
            slice_mode="MS",
        ).load()
        np.testing.assert_array_almost_equal(res.PRCPTOT.isel(time=0), 42)

    def test_index_r75ptot(self) -> None:
        # 2.32e-06 is about 0.2 mm/day
        # they will be ignore in computation because < 1 mm/day
        pr = stub_pr(value=2e-06)
        pr.attrs["units"] = "kg m-2 s-1"
        pr[:10] = 2e-04  # 10 days of ~20 mm/day
        pr[10:110] = 2e-05  # 100 days of ~2 mm/day
        res = icclim.r75ptot(
            in_files=pr,
            out_file=self.OUTPUT_FILE,
            slice_mode="year",
            save_thresholds=True,
        ).load()
        # 75th per is 2e-05
        # 50% of precip are due to the precip above the 75th percentile
        np.testing.assert_array_almost_equal(res.R75pTOT.isel(time=0), 50)

    def test_index_csu(self) -> None:
        tas = stub_tas(tas_value=26 + K2C)
        tas[10:40] = 0
        res = icclim.index(
            index_name="csu",
            in_files=tas,
            out_file=self.OUTPUT_FILE,
            slice_mode="ms",
        ).load()
        # in January there are only 10 days above 25degC
        assert res.CSU.isel(time=0) == 10
        # There are 30 days of temperature to zero, then only values above 25degC
        assert res.CSU.isel(time=1) == 1786
        # Nan because they are counted as the first run taken into account for Februar
        assert np.isnan(res.CSU.isel(time=3))

    def test_index_gd4(self) -> None:
        tas = stub_tas(tas_value=26 + K2C)
        tas[5:15] = 0
        res = icclim.index(
            index_name="gd4",
            in_files=tas,
            out_file=self.OUTPUT_FILE,
            slice_mode="ms",
        )
        expected = (26 - 4) * 21
        assert (
            res.GD4.isel(time=0) == expected
        )  # 21 days in January above 4 degC (at 26degC)

    def test_index_cfd(self) -> None:
        tas = stub_tas(tas_value=26 + K2C)
        tas[5:15] = 270  # ~ -3degC
        res = icclim.cfd(
            in_files=tas,
            out_file=self.OUTPUT_FILE,
            slice_mode="ms",
        ).load()
        # 10 days in January that are below or equal to 0degC
        assert res.CFD.isel(time=0) == 10

    def test_index_fd(self) -> None:
        tas = stub_tas(tas_value=26 + K2C)
        tas[5:15] = 0
        tas[20:25] = 0
        res = icclim.index(
            index_name="fd",
            in_files=tas,
            out_file=self.OUTPUT_FILE,
            slice_mode="ms",
        )
        assert res.FD.isel(time=0) == 15

    def test_index_hd17(self) -> None:
        tas = stub_tas(tas_value=27 + K2C)
        tas[5:10] = 0
        res = icclim.index(
            index_name="hd17",
            in_files=tas,
            out_file=self.OUTPUT_FILE,
            slice_mode="ms",
        )
        assert res.HD17.isel(time=0) == 5 * (17 + K2C)

    def test_index_tx90p__no_bootstrap_because_one_single_year_of_ref(self) -> None:
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

    def test_index_tx90p__no_bootstrap_because_no_overlap(self) -> None:
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

    def test_index_tx90p__bootstrap_2_years(self) -> None:
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

    def test_index_wsdi__no_bootstrap_because_no_overlap(self) -> None:
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

    def test_index_csdi__no_bootstrap_because_no_overlap(self) -> None:
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
        # 1 more day than in tas because of resample_doy that interpolate values
        assert res.CSDI.isel(time=0) == 11

    def test_count_occurrences__date_event(self) -> None:
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
            "2042-01-11",
        )
        assert res.count_occurrences.isel(time=0).event_date_start == np.datetime64(
            "2042-01-11",
        )

    def test_count_occurrences__to_percent(self) -> None:
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
        assert res.count_occurrences.attrs[UNITS_KEY] == "%"
        assert res.count_occurrences.isel(time=0) == 1 / 31 * 100

    def test_count_occurrences__multiple_simple_thresholds(self) -> None:
        tas = stub_tas(tas_value=2 + K2C)
        tas[10] = 35 + K2C
        res = icclim.index(
            tas,
            var_name=["tmin"],
            index_name="count_occurrences",
            threshold=build_threshold(value=[1, 30], operator=">=", unit="deg_C"),
            slice_mode="month",
            save_thresholds=True,
        ).compute()
        assert res.count_occurrences.attrs[UNITS_KEY] == "d"
        assert res.count_occurrences.isel(time=0).sel(threshold=1) == 31
        # The 5 days rolling turn the 1 day unusual value into a 5 day time lapse
        assert res.count_occurrences.isel(time=0).sel(threshold=30) == 1

    def test_count_occurrences__multiple_doy_per_thresholds(self) -> None:
        tas = stub_tas(tas_value=2 + K2C)
        tas[10] = 35 + K2C
        res = icclim.index(
            tas,
            var_name=["tmin"],
            index_name="count_occurrences",
            threshold=build_threshold(value=[10, 99], operator=">=", unit="doy_per"),
            slice_mode="month",
            save_thresholds=True,
        ).compute()
        assert res.count_occurrences.attrs[UNITS_KEY] == "d"
        assert res.count_occurrences.isel(time=0).sel(percentiles=10) == 31
        # The 5 days rolling turn the 1 day unusual value into a 5 day time lapse
        assert res.count_occurrences.isel(time=0).sel(percentiles=99) == 26

    def test_count_occurrences__multiple_period_per_thresholds(self) -> None:
        tas = stub_tas(tas_value=-20 + K2C)
        tas[10] = 35 + K2C
        res = icclim.index(
            tas,
            var_name=["tmin"],
            index_name="count_occurrences",
            threshold=build_threshold(
                value=[10, 99.95],
                operator=">=",
                unit="period_per",
            ),
            slice_mode="month",
            save_thresholds=True,
        ).compute()
        assert res.count_occurrences.attrs[UNITS_KEY] == "d"
        assert res.count_occurrences.isel(time=0).sel(percentiles=10) == 31
        assert res.count_occurrences.isel(time=0).sel(percentiles=99.95) == 1

    def test_excess__on_doy_percentile(self) -> None:
        tas = stub_tas(tas_value=10 + K2C).rename("tas")
        tas[10] = 5 + K2C
        res = icclim.index(
            tas,
            index_name="excess",
            time_range=["2044-01-01", "2045-12-31"],
            threshold=build_threshold(
                "10 doy_per",
                doy_window_width=1,
                reference_period=["2042-01-01", "2042-12-31"],
            ),
            slice_mode="month",
            save_thresholds=True,
        ).compute()
        # not exactly 5 because of resample_doy interpolation
        np.testing.assert_almost_equal(res.excess.isel(time=0), 5.01369863)
        assert "tas_thresholds" in res.data_vars

    def test_deficit__on_doy_percentile(self) -> None:
        tas = stub_tas(tas_value=5 + K2C).rename("tas")
        tas[10] = 10 + K2C
        res = icclim.index(
            tas,
            index_name="deficit",
            time_range=["2044-01-01", "2045-12-31"],
            threshold=build_threshold(
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

    def test_txnd(self) -> None:
        tas = stub_tas(tas_value=2, lat_length=10, lon_length=10)
        normal_tas = stub_tas(tas_value=1, lat_length=10, lon_length=10)
        icclim.dcsc.txnd(in_files=tas, normal=normal_tas)

    def test_fraction_of_total(self) -> None:
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
        assert res.fraction_of_total.attrs[UNITS_KEY] == PART_OF_A_WHOLE_UNIT

    def test_fraction_of_total_percent(self) -> None:
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
        assert res.fraction_of_total.attrs[UNITS_KEY] == "%"

    def test_std(self) -> None:
        tas = stub_tas(tas_value=25 + K2C).rename("tas")
        res = icclim.index(
            tas,
            index_name="standard_deviation",
        ).compute()
        np.testing.assert_almost_equal(res.standard_deviation.isel(time=0), 0)

    def test_slice_mode__between_date(self) -> None:
        time_range = xr.DataArray(
            pd.date_range("2000", periods=365, freq="D"),
            dims=["time"],
        )
        precipitation = xr.DataArray(
            np.ones(365),
            coords={"time": time_range, "lat": 1, "lon": 1},
            dims="time",
            attrs={"units": "mm/day"},
        )
        precipitation[0:5] = [0.1, 0.1, 0.1, 2, 3]
        cdd = icclim.cdd(
            in_files=precipitation,
            slice_mode=["season", ["01-02", "01-05"]],
        ).CDD
        # The 01-01 value is ignored because we clip the wanted season before computing
        # the index
        np.testing.assert_almost_equal(cdd.isel(time=0), 2)

    def test_rr_with_slice_mode__week(self) -> None:
        time_range = xr.DataArray(
            pd.date_range("2000", periods=365, freq="D"),
            dims=["time"],
        )
        precipitation = xr.DataArray(
            np.zeros(365),
            coords={"time": time_range, "lat": 1, "lon": 1},
            dims="time",
            attrs={"units": "mm/day"},
        )
        precipitation[0:5] = [0.1, 0.1, 0.1, 2, 3]
        rr = icclim.rr(in_files=precipitation, slice_mode="W").RR
        # The 01-01 value is ignored because we clip the wanted season before computing
        # the index
        np.testing.assert_almost_equal(rr.isel(time=0), 0.2)
        np.testing.assert_almost_equal(rr.isel(time=1), 5.1)

    def test_rr_with_slice_mode__4_weeks(self) -> None:
        time_range = xr.DataArray(
            pd.date_range("2000", periods=365, freq="D"),
            dims=["time"],
        )
        precipitation = xr.DataArray(
            np.zeros(365),
            coords={"time": time_range, "lat": 1, "lon": 1},
            dims="time",
            attrs={"units": "mm/day"},
        )
        precipitation[0:5] = [0.1, 0.1, 0.1, 2, 3]
        rr = icclim.rr(in_files=precipitation, slice_mode="2W-FRI")
        # The 01-01 value is ignored because we clip the wanted season before computing
        # the index
        np.testing.assert_almost_equal(rr.RR.isel(time=0), 5.3)
        np.testing.assert_almost_equal(rr.RR.isel(time=1), 0)

    def test_mm_to_mmday(self) -> None:
        # GIVEN
        time_range = xr.DataArray(
            pd.date_range("2000", periods=365, freq="D"),
            dims=["time"],
        )
        precip = xr.DataArray(
            np.ones(365),
            coords={"time": time_range, "lat": 1, "lon": 1},
            dims="time",
            attrs={"units": "mm", "standard_name": "thickness_of_rainfall_amount"},
        )
        precip.loc[{"time": slice("2000-01-01", "2000-01-05")}] = 50
        # WHEN
        r10mm = icclim.r10mm(in_files=precip, slice_mode="month")
        # THEN
        assert r10mm.isel(time=0) == 5

    def test_mm_to_mmday__error_bas_standard_name(self) -> None:
        # GIVEN
        time_range = xr.DataArray(
            pd.date_range("2000", periods=365, freq="D"),
            dims=["time"],
        )
        precip = xr.DataArray(
            np.ones(365),
            coords={"time": time_range, "lat": 1, "lon": 1},
            dims="time",
            attrs={"units": "mm", "standard_name": "HeHoCacao"},
        )
        precip.loc[{"time": slice("2000-01-01", "2000-01-05")}] = 50
        # THEN
        with pytest.raises(pint.DimensionalityError):
            # WHEN
            icclim.r10mm(in_files=precip)

    def test_ddnorth(self) -> None:
        # GIVEN
        time_range = xr.DataArray(
            pd.date_range("2000", periods=365, freq="D"),
            dims=["time"],
        )
        dd = xr.DataArray(
            np.full(365, 300),
            coords={"time": time_range, "lat": 1, "lon": 1},
            dims="time",
            attrs={"units": "degree"},
        )
        dd.loc[{"time": slice("2000-01-01", "2000-01-05")}] = 20  # north
        dd.loc[{"time": slice("2000-01-06", "2000-01-10")}] = 320  # north
        dd.loc[{"time": slice("2000-01-11", "2000-01-31")}] = 60  # east
        # WHEN
        ddnorth = icclim.ddnorth(in_files=dd, slice_mode="month").DDnorth.compute()
        # THEN
        np.testing.assert_almost_equal(ddnorth.isel(time=0), 10)

    def test_ddeast(self) -> None:
        # GIVEN
        time_range = xr.DataArray(
            pd.date_range("2000", periods=365, freq="D"),
            dims=["time"],
        )
        dd = xr.DataArray(
            np.full(365, 300),
            coords={"time": time_range, "lat": 1, "lon": 1},
            dims="time",
            attrs={"units": "degree"},
        )
        dd.loc[{"time": slice("2000-01-01", "2000-01-05")}] = 20  # north
        dd.loc[{"time": slice("2000-01-06", "2000-01-10")}] = 320  # north
        dd.loc[{"time": slice("2000-01-11", "2000-01-31")}] = 60  # east
        # WHEN
        ddeast = icclim.ddeast(in_files=dd, slice_mode="month").DDeast.compute()
        # THEN
        np.testing.assert_almost_equal(ddeast.isel(time=0), 21)

    def test_pp(self) -> None:
        time_range = xr.DataArray(
            pd.date_range("2000", periods=365, freq="D"),
            dims=["time"],
        )
        pressure = xr.DataArray(
            np.full(365, 1),
            coords={"time": time_range, "lat": 1, "lon": 1},
            dims="time",
            attrs={"units": "hPa"},
        )
        pressure.loc[{"time": slice("2000-01-01", "2000-01-30")}] = 9
        pressure.loc[{"time": "2000-01-31"}] = 40

        # WHEN
        pp = icclim.pp(in_files=pressure, slice_mode="month").PP.compute()
        # THEN
        np.testing.assert_almost_equal(pp.isel(time=0), 10)

    def test_ss(self) -> None:
        time_range = xr.DataArray(
            pd.date_range("2000", periods=365, freq="D"),
            dims=["time"],
        )
        sunshine = xr.DataArray(
            np.full(365, 1),
            coords={"time": time_range, "lat": 1, "lon": 1},
            dims="time",
            attrs={"units": "hours"},
        )
        # WHEN
        ss = icclim.ss(in_files=sunshine, slice_mode="month").SS.compute()
        # THEN
        np.testing.assert_almost_equal(ss.isel(time=0), 31)

    def test_rh(self) -> None:
        time_range = xr.DataArray(
            pd.date_range("2000", periods=365, freq="D"),
            dims=["time"],
        )
        humidity = xr.DataArray(
            np.full(365, 1),
            coords={"time": time_range, "lat": 1, "lon": 1},
            dims="time",
            attrs={"units": "%"},
        )
        humidity.loc[{"time": slice("2000-01-01", "2000-01-30")}] = 9
        humidity.loc[{"time": "2000-01-31"}] = 40
        # WHEN
        rh = icclim.rh(in_files=humidity, slice_mode="month").RH.compute()
        # THEN
        np.testing.assert_almost_equal(rh.isel(time=0), 10)
