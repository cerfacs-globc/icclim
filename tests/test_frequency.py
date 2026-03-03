from __future__ import annotations

import cftime
import numpy as np
import pandas as pd
import pytest

import icclim
from icclim.exception import InvalidIcclimArgumentError
from icclim.frequency import FrequencyRegistry, get_seasonal_time_updater
from tests.testing_utils import stub_tas


class TestBuildFrequencyOverFrequency:
    def test_simple(self) -> None:
        freq = FrequencyRegistry.lookup(FrequencyRegistry.YEAR)
        assert freq == FrequencyRegistry.YEAR


class TestBuildFrequencyOverString:
    def test_error(self) -> None:
        with pytest.raises(InvalidIcclimArgumentError):
            FrequencyRegistry.lookup("yolo")

    def test_simple(self) -> None:
        freq = FrequencyRegistry.lookup("year")
        assert freq == FrequencyRegistry.YEAR


class TestBuildFrequencyOverList:
    def test_lookup_list__keyword_error(self) -> None:
        with pytest.raises(InvalidIcclimArgumentError):
            FrequencyRegistry.lookup(["cacahuêtes"])

    def test_lookup_string_error(self) -> None:
        with pytest.raises(InvalidIcclimArgumentError):
            FrequencyRegistry.lookup("cacahuêtes")

    def test_lookup_month(self) -> None:
        freq = FrequencyRegistry.lookup(["month", [1, 4, 3]])
        assert freq.pandas_freq == "MS"
        assert freq.accepted_values == []
        assert freq.post_processing is not None

    def test_lookup_season(self) -> None:
        freq = FrequencyRegistry.lookup(["season", [1, 2, 3, 4]])
        assert freq.pandas_freq == "YS-JAN"
        assert freq.accepted_values == []
        assert freq.post_processing is not None

    def test_lookup_season_tuple(self) -> None:
        freq = FrequencyRegistry.lookup(("season", [1, 2, 3, 4]))
        assert freq.pandas_freq == "YS-JAN"
        assert freq.accepted_values == []
        assert freq.post_processing is not None

    def test_lookup_pandas_freq(self) -> None:
        freq = FrequencyRegistry.lookup("3MS")
        assert freq.pandas_freq == "3MS"
        assert freq.accepted_values == []
        assert freq.post_processing is not None

    def test_lookup_winter__deprecated_tuple(self) -> None:
        freq = FrequencyRegistry.lookup(["season", ([11, 12], [1, 2, 3, 4])])
        assert freq.pandas_freq == "YS-NOV"
        assert freq.accepted_values == []
        assert freq.post_processing is not None

    def test_lookup_error__non_consecutive_season(self) -> None:
        with pytest.raises(InvalidIcclimArgumentError):
            FrequencyRegistry.lookup(["season", ([12, 3])])

    def test_lookup_error__weird_months(self) -> None:
        with pytest.raises(InvalidIcclimArgumentError):
            FrequencyRegistry.lookup(["season", ([42, 0])])

    def test_lookup__winter(self) -> None:
        freq = FrequencyRegistry.lookup(["season", [11, 12, 1, 2]])
        assert freq.pandas_freq == "YS-NOV"
        assert freq.accepted_values == []
        assert freq.post_processing is not None

    def test_lookup_season__between_dates(self) -> None:
        freq = FrequencyRegistry.lookup(["season", ["07-19", "08-14"]])
        assert freq.pandas_freq == "YS-JUL"
        assert freq.accepted_values == []
        assert freq.post_processing is not None


class TestSeasonsResampler:
    def test_simple(self) -> None:
        # WHEN
        test_da = filter_months(stub_tas(), [4, 5, 6]).resample(time="YS").mean()
        da_res, time_bds_res = get_seasonal_time_updater(4, 6)(test_da)
        # THEN
        np.testing.assert_array_equal(1, da_res)
        assert time_bds_res[0].data[0] == pd.to_datetime("2042-04")
        assert (
            time_bds_res[0].data[1]
            == pd.to_datetime("2042-07") - pd.tseries.offsets.Day()
        )

    def test_winter(self) -> None:
        # WHEN
        test_da = filter_months(stub_tas(), [11, 12, 1]).resample(time="YS-NOV").mean()
        da_res, time_bds_res = get_seasonal_time_updater(11, 1)(test_da)
        # THEN
        np.testing.assert_array_equal(1, da_res)
        assert time_bds_res[0].data[0] == pd.to_datetime("2041-11")
        assert (
            time_bds_res[0].data[1]
            == pd.to_datetime("2042-02") - pd.tseries.offsets.Day()
        )
        assert time_bds_res[1].data[0] == pd.to_datetime("2042-11")
        assert (
            time_bds_res[1].data[1]
            == pd.to_datetime("2043-02") - pd.tseries.offsets.Day()
        )

    @pytest.mark.parametrize("use_cf", [True, False])
    def test_between_dates(self, use_cf) -> None:
        # WHEN
        test_da = (
            filter_months(stub_tas(use_cftime=use_cf), [11, 12, 1])
            .resample(time="YS-NOV")
            .mean()
        )
        da_res, time_bds_res = get_seasonal_time_updater(11, 1, 2, 30)(test_da)
        # THEN
        np.testing.assert_array_equal(1, da_res)  # data must be unchanged
        assert time_bds_res[0].data[0] == pd.to_datetime("2041-11-02")
        assert time_bds_res[0].data[1] == pd.to_datetime("2042-01-30")

    @pytest.mark.parametrize("use_cf", [True, False])
    def test_between_dates__december_ending(self, use_cf) -> None:
        # WHEN
        test_da = (
            filter_months(stub_tas(use_cftime=use_cf), [11, 12])
            .resample(time="YS-NOV")
            .mean()
        )
        da_res, time_bds_res = get_seasonal_time_updater(
            start_month=11,
            end_month=12,
            start_day=2,
        )(test_da)
        # THEN
        if use_cf:
            assert da_res.time[0] == cftime.DatetimeGregorian(2042, 12, 1, 12)
        else:
            assert da_res.time[0] == pd.to_datetime("2042-12-01 12:00")
        assert time_bds_res[0].data[0] == pd.to_datetime("2042-11-02")
        assert time_bds_res[0].data[1] == pd.to_datetime("2042-12-31")


def filter_months(da, month_list: list[int]):
    return da.sel(time=da.time.dt.month.isin(month_list))


class TestSeasonalSliceModes:
    """Regression tests for issue #323.

    Seasonal slice modes (MAM, JJA, SON, DJF, AMJJAS, ONDJFM) used to raise
    ``InvalidIcclimArgumentError: Invalid frequency: YS-MAR`` (and similar)
    when resampling in certain xarray/pandas version combinations.
    """

    @pytest.mark.parametrize("use_cf", [False, True])
    @pytest.mark.parametrize(
        "slice_mode",
        ["MAM", "JJA", "SON", "DJF", "AMJJAS", "ONDJFM"],
    )
    def test_seasonal_slice_mode_does_not_raise(
        self, slice_mode: str, use_cf: bool
    ) -> None:
        # GIVEN daily temperature data covering 5 years
        da = stub_tas(use_cftime=use_cf)
        # WHEN computing a simple index with a named seasonal slice_mode
        # it should NOT raise "Invalid frequency: YS-MAR" (or similar)
        result = icclim.index(
            index_name="TX",
            in_files=da,
            slice_mode=slice_mode,
            logs_verbosity="silent",
        )
        # THEN result is a valid dataset with a time dimension
        assert "TX" in result
        assert result.time.size >= 1

    def test_mam_values_are_correct(self) -> None:
        """MAM result should only reflect March-May data."""
        # GIVEN data where all days have value 293.15 K (= 20 degC)
        # stub_tas produces Kelvin data; icclim normalises temps to Celsius,
        # so TX output should be ~20 degC.
        da = stub_tas(tas_value=293.15)
        # WHEN computing TX with MAM slice_mode
        result = icclim.index(
            index_name="TX",
            in_files=da,
            slice_mode="MAM",
            logs_verbosity="silent",
        )
        # THEN the per-season maximum should be ~20 degrees Celsius
        assert result.TX.mean().compute().item() == pytest.approx(20.0, abs=1e-3)

    @pytest.mark.parametrize("use_cf", [False, True])
    def test_mam_time_bounds_span_march_to_may(self, use_cf: bool) -> None:
        """MAM time_bounds should start in March and end in May."""
        da = stub_tas(use_cftime=use_cf)
        result = icclim.index(
            index_name="TX",
            in_files=da,
            slice_mode="MAM",
            logs_verbosity="silent",
        )
        # Each period should start on March 1st and end on May 31st.
        # Handle both numpy.datetime64 and cftime objects.
        time_bounds = result.time_bounds.values
        for start, end in time_bounds:
            # cftime objects have .month; numpy.datetime64 need pd.Timestamp
            if hasattr(start, "month"):
                start_month = start.month
                end_month = end.month
            else:
                start_month = pd.Timestamp(start).month
                end_month = pd.Timestamp(end).month
            assert start_month == 3, f"Expected March start, got {start}"
            assert end_month == 5, f"Expected May end, got {end}"
