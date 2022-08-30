from __future__ import annotations

from xclim.core.calendar import build_climatology_bounds

import icclim
from icclim.models.constants import UNITS_ATTRIBUTE_KEY
from icclim.models.logical_link import LogicalLinkRegistry
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

    def test_simple_percentile(self):
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
                logical_operation=OperatorRegistry.GREATER,
            ),
            base_period_time_range=build_climatology_bounds(da),
            slice_mode="month",
        ).compute()
        # THEN
        assert result.data.isel(time=0) == 2

    def test_multi_threshold_or(self):
        # GIVEN
        tmax = stub_tas(10, False)
        tmax[1] = 15
        tmin = stub_tas(-10, False)
        # WHEN
        result = count_events(
            das=[tmax, tmin],
            in_base_das=[None],
            logical_operation=[OperatorRegistry.GREATER, OperatorRegistry.EQUAL],
            thresholds=[12, -20],
            link_logical_operations=LogicalLinkRegistry.LOGICAL_OR,
            freq="MS",
        )
        # THEN
        assert result[0] == 1

    def test_multi_threshold_and(self):
        # GIVEN
        tmax = stub_tas(10, False)
        tmax[1] = 15
        tmin = stub_tas(-10, False)
        tmin[1] = -20
        # WHEN
        result = count_events(
            das=[tmax, tmin],
            in_base_das=[None],
            logical_operation=[OperatorRegistry.GREATER, OperatorRegistry.EQUAL],
            thresholds=[12, -20],
            link_logical_operations=LogicalLinkRegistry.LOGICAL_AND,
            freq="MS",
        )
        # THEN
        assert result[0] == 1


class Test_run_mean:
    def test_simple_min(self):
        # GIVEN
        tmax = stub_tas(10, False)
        tmax[30] = 0
        tmax[29] = 0
        tmax[28] = 0
        tmax[27] = 0
        tmax[26] = 0
        # WHEN
        result = run_mean(
            da=tmax,
            extreme_mode=ExtremeModeRegistry.MIN,
            window_width=5,
            freq="MS",
        )
        # THEN
        assert result[0] == 0
        assert result[1] == 2
        assert result[2] == 10

    def test_simple_max(self):
        # GIVEN
        tmax = stub_tas(10, False)
        tmax[30] = 20
        # WHEN
        result = run_mean(
            da=tmax,
            extreme_mode=ExtremeModeRegistry.MAX,
            window_width=2,
            freq="MS",
        )
        # THEN
        assert result[0] == 15
        assert result[1] == 15
        assert result[2] == 10


class Test_run_sum:
    def test_simple_min(self):
        # GIVEN
        tmax = stub_tas(10, False)
        tmax[30] = 0
        tmax[29] = 0
        tmax[28] = 0
        tmax[27] = 0
        tmax[26] = 0
        # WHEN
        result = run_sum(
            da=tmax,
            extreme_mode=ExtremeModeRegistry.MIN,
            window_width=5,
            freq="MS",
        )
        # THEN
        assert result[0] == 0
        assert result[1] == 10
        assert result[2] == 50

    def test_simple_max(self):
        # GIVEN
        tmax = stub_tas(10, False)
        tmax[30] = 20
        # WHEN
        result = run_sum(
            da=tmax,
            extreme_mode=ExtremeModeRegistry.MAX,
            window_width=2,
            freq="MS",
        )
        # THEN
        assert result[0] == 30
        assert result[1] == 30
        assert result[2] == 20


class Test_max_consecutive_event_count:
    def test_simple(self):
        # GIVEN
        tmax = stub_tas(10, False)
        tmax[30] = 15  # On 31th january
        # WHEN
        result = max_consecutive_event_count(
            da=tmax,
            logical_operation=OperatorRegistry.EQUAL,
            threshold=10.0,
            freq="YS",
        )
        # THEN
        assert result[0] == 334
        assert result[1] == 365


class Test_anomaly:
    def test_simple(self):
        # GIVEN
        tmax = stub_tas(10, False)
        tmax2 = stub_tas(11, False)
        # WHEN
        result = anomaly(da_ref=tmax, da=tmax2, percent=False)
        # THEN
        assert result == 1

    def test_simple_percent(self):
        # GIVEN
        tmax = stub_tas(10, False)
        tmax2 = stub_tas(11, False)
        # WHEN
        result = anomaly(da_ref=tmax, da=tmax2, percent=True)
        # THEN
        assert result == 10
        assert result.attrs[UNITS_ATTRIBUTE_KEY] == "%"
