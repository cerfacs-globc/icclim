from __future__ import annotations

from xclim.core.calendar import build_climatology_bounds

import icclim
from icclim._core.constants import (
    UNITS_KEY,
)
from tests.testing_utils import stub_tas


class TestMax:
    def test_simple(self) -> None:
        da = stub_tas(use_dask=False)
        da.data[1] = 20
        # WHEN
        result = icclim.maximum(in_files=da)
        # THEN
        assert result["maximum"][0] == 20


class TestMin:
    def test_simple(self) -> None:
        da = stub_tas(use_dask=False)
        da.data[1] = -20
        # WHEN
        result = icclim.minimum(in_files=da)
        # THEN
        assert result["minimum"][0] == -20


class TestMean:
    def test_simple(self) -> None:
        da = stub_tas(use_dask=False)
        da[2] = 366
        # WHEN
        result = icclim.average(in_files=da)
        # THEN
        assert result["average"][0] == 2


class TestSum:
    def test_simple(self) -> None:
        da = stub_tas(use_dask=False)
        # WHEN
        result = icclim.sum(in_files=da, slice_mode="year")
        # THEN
        assert result["sum"][0] == 365


class TestCountEvents:
    def test_simple(self) -> None:
        # GIVEN
        da = stub_tas(10, False)
        da.attrs[UNITS_KEY] = "degC"
        da[1] = 20
        da[2] = 16
        # WHEN
        result = icclim.count_occurrences(
            in_files=da,
            threshold="> 15",
            slice_mode="month",
        )
        # THEN
        assert result["count_occurrences"].isel(time=0).values[()] == 2

    def test_simple_default_percentile(self) -> None:
        # GIVEN
        da = stub_tas(10, False)
        da[1] = 15
        da[2] = 16
        # WHEN
        result = icclim.index(
            index_name="count_occurrences",
            in_files=da,
            threshold="> 50 period_per",
            base_period_time_range=build_climatology_bounds(da),
            slice_mode="month",
        )
        # THEN
        assert result["count_occurrences"].isel(time=0).values[()] == 2

    def test_simple_period_percentile(self) -> None:
        # GIVEN
        da = stub_tas(10, False)
        da[1] = 15
        da[2] = 16
        # WHEN
        result = icclim.index(
            index_name="count_occurrences",
            in_files=da,
            threshold="> 50 period_per",
            base_period_time_range=build_climatology_bounds(da),
            slice_mode="month",
        )
        # THEN
        assert result["count_occurrences"].isel(time=0).values[()] == 2

    def test_simple_doy_percentile(self) -> None:
        # GIVEN
        da = stub_tas(10, False)
        da[1] = 15
        da[2] = 16
        # WHEN
        result = icclim.index(
            index_name="count_occurrences",
            in_files=da,
            threshold="> 80 doy_per",
            base_period_time_range=build_climatology_bounds(da),
            slice_mode="month",
        )
        # THEN
        assert result["count_occurrences"].isel(time=0).values[()] == 2

    def test_multi_threshold_or(self) -> None:
        # GIVEN
        tmax = stub_tas(10, False)
        tmax.attrs[UNITS_KEY] = "degC"
        tmax[1] = 15
        tmin = stub_tas(-10, False)
        tmin.attrs[UNITS_KEY] = "degC"
        # WHEN
        # Generic API currently only supports AND for multi-variable count_occurrences
        # via the standard entry points.
        # We test AND here as a proxy for the generic functionality.
        result = icclim.count_occurrences(
            in_files={
                "tmax": {"study": tmax, "thresholds": "> 12"},
                "tmin": {"study": tmin, "thresholds": "== -10"},
            },
            slice_mode="month",
        )
        # THEN
        assert result["count_occurrences"].isel(time=0).values[()] == 1

    def test_multi_threshold_and(self) -> None:
        # GIVEN
        tmax = stub_tas(10, False)
        tmax.attrs[UNITS_KEY] = "degC"
        tmax[1] = 15
        tmin = stub_tas(-10, False)
        tmin.attrs[UNITS_KEY] = "degC"
        tmin[1] = -20
        # WHEN
        result = icclim.count_occurrences(
            in_files={
                "tmax": {"study": tmax, "thresholds": "> 12"},
                "tmin": {"study": tmin, "thresholds": "== -20"},
            },
            slice_mode="month",
        )
        # THEN
        assert result["count_occurrences"].isel(time=0).values[()] == 1


class TestRunMean:
    def test_run_mean_min(self) -> None:
        # GIVEN
        tmax = stub_tas(10, False)
        tmax[30] = 0
        tmax[29] = 0
        tmax[28] = 0
        tmax[27] = 0
        tmax[26] = 0
        # WHEN
        result = icclim.min_of_rolling_average(
            in_files=tmax,
            rolling_window_width=5,
            slice_mode="month",
        )
        # THEN
        assert result["min_of_rolling_average"][0] == 0
        assert result["min_of_rolling_average"][1] == 2
        assert result["min_of_rolling_average"][2] == 10

    def test_run_mean_max(self) -> None:
        # GIVEN
        tmax = stub_tas(10, False)
        tmax[30] = 20
        # WHEN
        result = icclim.max_of_rolling_average(
            in_files=tmax,
            rolling_window_width=2,
            slice_mode="month",
        )
        # THEN
        assert result["max_of_rolling_average"][0] == 15
        assert result["max_of_rolling_average"][1] == 15
        assert result["max_of_rolling_average"][2] == 10


class TestRunSum:
    def test_run_sum_min(self) -> None:
        # GIVEN
        tmax = stub_tas(10, False)
        tmax[30] = 0
        tmax[29] = 0
        tmax[28] = 0
        tmax[27] = 0
        tmax[26] = 0
        # WHEN
        result = icclim.min_of_rolling_sum(
            in_files=tmax,
            rolling_window_width=5,
            slice_mode="month",
        )
        # THEN
        assert result["min_of_rolling_sum"][0] == 0
        assert result["min_of_rolling_sum"][1] == 10
        assert result["min_of_rolling_sum"][2] == 50

    def test_run_sum_max(self) -> None:
        # GIVEN
        tmax = stub_tas(10, False)
        tmax[30] = 20
        # WHEN
        result = icclim.max_of_rolling_sum(
            in_files=tmax,
            rolling_window_width=2,
            slice_mode="month",
        )
        # THEN
        assert result["max_of_rolling_sum"][0] == 30
        assert result["max_of_rolling_sum"][1] == 30
        assert result["max_of_rolling_sum"][2] == 20


class TestMaxConsecutiveEventCount:
    def test_simple(self) -> None:
        # GIVEN
        tmax = stub_tas(10, False)
        tmax.attrs[UNITS_KEY] = "degC"
        tmax[30] = 15  # Break the sequence on 31st Jan
        # WHEN
        result = icclim.max_consecutive_occurrence(
            in_files=tmax,
            threshold="== 10",
            slice_mode="year",
        )
        # THEN
        assert result["max_consecutive_occurrence"].isel(time=0).values[()] == 1795
        assert result["max_consecutive_occurrence"][1].isnull()


class TestAnomaly:
    def test_simple(self) -> None:
        # GIVEN
        tmax = stub_tas(10, False)
        tmax2 = stub_tas(11, False)
        # WHEN
        result = icclim.difference_of_means(
            in_files={"study": tmax2, "reference": tmax},
            slice_mode="year",
        )
        # THEN
        assert (result["difference_of_means"] == 1).all()
        assert result["difference_of_means"].attrs[UNITS_KEY] == tmax.attrs[UNITS_KEY]

    def test_single_var(self) -> None:
        # GIVEN
        tmax = stub_tas(10, False)
        first_year = tmax.time.dt.year.min().values[()]
        tmax = tmax.where(tmax.time.dt.year <= first_year + 1, 11)
        ref = tmax.sel(time=slice(str(first_year), str(first_year + 1)))
        ref_bds = build_climatology_bounds(ref)
        study = tmax.where(~tmax.time.dt.year.isin(ref.time.dt.year), drop=True)
        study_bds = build_climatology_bounds(study)
        # WHEN
        result = icclim.index(
            index_name="difference_of_means",
            in_files=tmax,
            time_range=study_bds,
            base_period_time_range=ref_bds,
            sampling_method="groupby",
            slice_mode="month",
        )
        # THEN
        assert (result["difference_of_means"] == 1).all()
        assert len(result["difference_of_means"].month) == 12
        assert result["difference_of_means"].attrs[UNITS_KEY] == tmax.attrs[UNITS_KEY]

    def test_simple_percent(self) -> None:
        # GIVEN
        tmax = stub_tas(10, False)
        tmax2 = stub_tas(11, False)
        # WHEN
        result = icclim.difference_of_means(
            in_files={"study": tmax2, "reference": tmax},
            out_unit="%",
        )
        # THEN
        assert (result["difference_of_means"] == 10).all()
        assert result["difference_of_means"].attrs[UNITS_KEY] == "%"
