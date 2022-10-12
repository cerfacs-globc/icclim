from __future__ import annotations

from xclim.core.calendar import build_climatology_bounds

import icclim
from icclim.models.constants import (
    UNITS_KEY,
    USER_INDEX_PRECIPITATION_STAMP,
    USER_INDEX_TEMPERATURE_STAMP,
)
from icclim.models.operator import OperatorRegistry
from icclim.tests.testing_utils import stub_tas


class Test_max:
    def test_simple(self):
        da = stub_tas(use_dask=False)
        da.data[1] = 20
        # WHEN
        result = icclim.index(
            in_files=da,
            user_index=dict(
                index_name="data", calc_operation="max", coef=1, logical_operation=None
            ),
        )
        # THEN
        assert result.data[0] == 20


class Test_min:
    def test_simple(self):
        da = stub_tas(use_dask=False)
        da.data[1] = -20
        # WHEN
        result = icclim.index(
            in_files=da,
            user_index=dict(index_name="data", calc_operation="min"),
        )
        # THEN
        assert result.data[0] == -20


class Test_mean:
    def test_simple(self):
        da = stub_tas(use_dask=False)
        da[2] = 366
        # WHEN
        result = icclim.index(
            in_files=da,
            user_index=dict(index_name="data", calc_operation="mean"),
        )
        # THEN
        assert result.data[0] == 2


class Test_sum:
    def test_simple(self):
        da = stub_tas(use_dask=False)
        # WHEN
        result = icclim.index(
            in_files=da,
            user_index=dict(index_name="data", calc_operation="sum"),
            slice_mode="year",
        )
        # THEN
        assert result.data[0] == 365


class Test_count_events:
    def test_simple(self):
        # GIVEN
        da = stub_tas(10, False)
        da[1] = 15
        da[2] = 16
        # WHEN
        result = icclim.index(
            in_files=da,
            user_index=dict(
                index_name="data",
                calc_operation="nb_events",
                thresh=15,
                logical_operation=OperatorRegistry.GREATER,
            ),
            slice_mode="month",
        )
        # THEN
        assert result.data[0] == 1

    def test_simple_default_percentile(self):
        # GIVEN
        da = stub_tas(10, False)
        da[1] = 15
        da[2] = 16
        # WHEN
        result = icclim.index(
            in_files=da,
            user_index=dict(
                index_name="data",
                calc_operation="nb_events",
                thresh="50p",
                logical_operation=OperatorRegistry.GREATER,
            ),
            base_period_time_range=build_climatology_bounds(da),
            slice_mode="month",
        )
        # THEN
        assert result.data.isel(time=0) == 2

    def test_simple_period_percentile(self):
        # GIVEN
        da = stub_tas(10, False)
        da[1] = 15
        da[2] = 16
        # WHEN
        result = icclim.index(
            in_files=da,
            user_index=dict(
                index_name="data",
                calc_operation="nb_events",
                thresh="50p",
                var_type=USER_INDEX_PRECIPITATION_STAMP,
                logical_operation=OperatorRegistry.GREATER,
            ),
            base_period_time_range=build_climatology_bounds(da),
            slice_mode="month",
        )
        # THEN
        assert result.data.isel(time=0) == 2

    def test_simple_doy_percentile(self):
        # GIVEN
        da = stub_tas(10, False)
        da[1] = 15
        da[2] = 16
        # WHEN
        result = icclim.index(
            in_files=da,
            user_index=dict(
                index_name="data",
                calc_operation="nb_events",
                thresh="80p",
                var_type=USER_INDEX_TEMPERATURE_STAMP,
                logical_operation=OperatorRegistry.GREATER,
            ),
            base_period_time_range=build_climatology_bounds(da),
            slice_mode="month",
        )
        # THEN
        assert result.data.isel(time=0) == 2

    def test_multi_threshold_or(self):
        # GIVEN
        tmax = stub_tas(10, False)
        tmax[1] = 15
        tmin = stub_tas(-10, False)
        # WHEN
        result = icclim.index(
            in_files={"tmax": tmax, "tmin": tmin},
            index_name="data",
            user_index=dict(
                calc_operation="nb_events",
                thresh=[12, -20],
                var_type=USER_INDEX_TEMPERATURE_STAMP,
                logical_operation=[OperatorRegistry.GREATER, OperatorRegistry.EQUAL],
                link_logical_operations="or",
            ),
            slice_mode="month",
        )
        # THEN
        assert result.data[0] == 1

    def test_multi_threshold_and(self):
        # GIVEN
        tmax = stub_tas(10, False)
        tmax[1] = 15
        tmin = stub_tas(-10, False)
        tmin[1] = -20
        # WHEN
        result = icclim.index(
            in_files={"tmax": tmax, "tmin": tmin},
            index_name="data",
            user_index=dict(
                calc_operation="nb_events",
                thresh=[12, -20],
                var_type=USER_INDEX_TEMPERATURE_STAMP,
                logical_operation=[OperatorRegistry.GREATER, OperatorRegistry.EQUAL],
                link_logical_operations="and",
            ),
            slice_mode="month",
        )
        # THEN
        assert result.data[0] == 1


class Test_run_mean:
    def test_run_mean_min(self):
        # GIVEN
        tmax = stub_tas(10, False)
        tmax[30] = 0
        tmax[29] = 0
        tmax[28] = 0
        tmax[27] = 0
        tmax[26] = 0
        # WHEN
        result = icclim.index(
            in_files={"tmax": tmax},
            index_name="data",
            user_index=dict(
                calc_operation="run_mean",
                extreme_mode="min",
                window_width=5,
            ),
            slice_mode="month",
        )
        # THEN
        assert result.data[0] == 0
        assert result.data[1] == 2
        assert result.data[2] == 10

    def test_run_mean_max(self):
        # GIVEN
        tmax = stub_tas(10, False)
        tmax[30] = 20
        # WHEN
        result = icclim.index(
            in_files={"tmax": tmax},
            index_name="data",
            rolling_window_width=2,
            user_index=dict(
                calc_operation="run_mean",
                extreme_mode="max",
            ),
            slice_mode="month",
        )
        # THEN
        assert result.data[0] == 15
        assert result.data[1] == 15
        assert result.data[2] == 10


class Test_run_sum:
    def test_run_sum_min(self):
        # GIVEN
        tmax = stub_tas(10, False)
        tmax[30] = 0
        tmax[29] = 0
        tmax[28] = 0
        tmax[27] = 0
        tmax[26] = 0
        # WHEN
        result = icclim.index(
            in_files={"tmax": tmax},
            index_name="data",
            rolling_window_width=5,
            user_index=dict(
                calc_operation="run_sum",
                extreme_mode="min",
            ),
            slice_mode="month",
        )
        # THEN
        assert result.data[0] == 0
        assert result.data[1] == 10
        assert result.data[2] == 50

    def test_run_sum_max(self):
        # GIVEN
        tmax = stub_tas(10, False)
        tmax[30] = 20
        # WHEN
        result = icclim.index(
            in_files={"tmax": tmax},
            index_name="data",
            rolling_window_width=2,
            user_index=dict(
                calc_operation="run_sum",
                extreme_mode="max",
            ),
            slice_mode="month",
        )
        # THEN
        assert result.data[0] == 30
        assert result.data[1] == 30
        assert result.data[2] == 20


class Test_max_consecutive_event_count:
    def test_simple(self):
        # GIVEN
        tmax = stub_tas(10, False)
        tmax[30] = 15  # On 31th january
        # WHEN
        result = icclim.index(
            in_files={"tmax": tmax},
            index_name="data",
            user_index=dict(
                calc_operation="max_nb_consecutive_events",
                thresh=10.0,
                logical_operation=OperatorRegistry.EQUAL,
            ),
            slice_mode="year",
        )
        # THEN
        assert result.data[0] == 1795
        assert result.data[1].isnull()


class Test_anomaly:
    def test_simple(self):
        # GIVEN
        tmax = stub_tas(10, False)
        tmax2 = stub_tas(11, False)
        # WHEN
        result = icclim.index(
            in_files={"tmax2": tmax2, "tmax": tmax},
            index_name="data",
            user_index=dict(
                calc_operation="anomaly",
            ),
            slice_mode="year",
        )
        # THEN
        assert (result.data == 1).all()
        assert result.data.attrs[UNITS_KEY] == tmax.attrs[UNITS_KEY]

    def test_single_var(self):
        # GIVEN
        tmax = stub_tas(10, False)
        first_year = tmax.time.dt.year.min().values[()]
        tmax = tmax.where(tmax.time.dt.year <= first_year + 1, 11)  #
        ref = tmax.sel(time=slice(str(first_year), str(first_year + 1)))
        ref_bds = build_climatology_bounds(ref)
        study = tmax.where(~tmax.time.dt.year.isin(ref.time.dt.year), drop=True)
        study_bds = build_climatology_bounds(study)
        # WHEN
        result = icclim.index(
            in_files={"tmax": tmax},
            time_range=study_bds,
            base_period_time_range=ref_bds,
            index_name="data",
            sampling_method="groupby",
            user_index=dict(
                calc_operation="anomaly",
            ),
            slice_mode="month",
        )
        # THEN
        assert (result.data == 1).all()
        assert len(result.data.month) == 12
        assert result.data.attrs[UNITS_KEY] == tmax.attrs[UNITS_KEY]

    def test_simple_percent(self):
        # GIVEN
        tmax = stub_tas(10, False)
        tmax2 = stub_tas(11, False)
        # WHEN
        result = icclim.index(
            index_name="data",
            in_files={"tmax2": tmax2, "tmax": tmax},
            out_unit="%",
            user_index=dict(calc_operation="anomaly"),
        )
        # THEN
        assert (result.data == 10).all()
        assert result.data.attrs[UNITS_KEY] == "%"
