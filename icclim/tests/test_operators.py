import numpy as np
import pytest

from icclim.models.user_index_config import (
    ExtremeMode,
    LinkLogicalOperation,
    LogicalOperation,
)
from icclim.tests.test_utils import stub_tas
from icclim.user_indices.operators import (
    _apply_coef,
    anomaly,
    count_events,
    max,
    max_consecutive_event_count,
    mean,
    min,
    run_mean,
    run_sum,
    sum,
)


class Test_apply_coef:
    @pytest.mark.parametrize("use_dask", [True, False])
    def test_simple(self, use_dask):
        # GIVEN
        da = stub_tas(use_dask=use_dask)
        # WHEN
        result = _apply_coef(4.0, da)
        # THEN
        assert np.testing.assert_equal(result.data, 4.0) is None


class Test_max:
    @pytest.mark.parametrize("use_dask", [True, False])
    def test_simple(self, use_dask):
        da = stub_tas(use_dask=use_dask)
        da.data[1] = 20
        # WHEN
        result = max(
            da=da,
            coef=1,
            logical_operation=None,
            threshold=None,
            freq="YS",
            date_event=True,
        )
        # THEN
        assert result.data[0] == 20


class Test_min:
    @pytest.mark.parametrize("use_dask", [True, False])
    def test_simple(self, use_dask):
        da = stub_tas(use_dask=use_dask)
        da.data[1] = -20
        # WHEN
        result = min(da=da, freq="YS")
        # THEN
        assert result.data[0] == -20


class Test_mean:
    @pytest.mark.parametrize("use_dask", [True, False])
    def test_simple(self, use_dask):
        da = stub_tas(use_dask=use_dask)
        da[2] = 366
        # WHEN
        result = mean(
            da=da,
            freq="YS",
        )
        # THEN
        assert result.data[0] == 2


class Test_sum:
    @pytest.mark.parametrize("use_dask", [True, False])
    def test_simple(self, use_dask):
        da = stub_tas(use_dask=use_dask)
        # WHEN
        result = sum(da=da, freq="YS")
        # THEN
        assert result.data[0] == 365


class Test_count_events:
    @pytest.mark.parametrize("use_dask", [True, False])
    def test_simple(self, use_dask):
        # GIVEN
        da = stub_tas(10, use_dask)
        da[1] = 15
        da[2] = 16
        # WHEN
        result = count_events(
            das=[da],
            in_base_das=[None],
            logical_operation=[LogicalOperation.GREATER_THAN],
            thresholds=[15],
            freq="MS",
        )
        # THEN
        assert result[0] == 1

    @pytest.mark.parametrize("use_dask", [True, False])
    def test_simple_percentile(self, use_dask):
        # GIVEN
        da = stub_tas(10, use_dask)
        da[1] = 15
        da[2] = 16
        # WHEN
        result = count_events(
            das=[da],
            in_base_das=[da],
            logical_operation=[LogicalOperation.GREATER_THAN],
            thresholds=["80p"],
            freq="MS",
        )
        # THEN
        assert result[0] == 2

    @pytest.mark.parametrize("use_dask", [True, False])
    def test_multi_threshold_or(self, use_dask):
        # GIVEN
        tmax = stub_tas(10, use_dask)
        tmax[1] = 15
        tmin = stub_tas(-10, use_dask)
        # WHEN
        result = count_events(
            das=[tmax, tmin],
            in_base_das=[None],
            logical_operation=[LogicalOperation.GREATER_THAN, LogicalOperation.EQUAL],
            thresholds=[12, -20],
            link_logical_operations=LinkLogicalOperation.OR_STAMP,
            freq="MS",
        )
        # THEN
        assert result[0] == 1

    @pytest.mark.parametrize("use_dask", [True, False])
    def test_multi_threshold_and(self, use_dask):
        # GIVEN
        tmax = stub_tas(10, use_dask)
        tmax[1] = 15
        tmin = stub_tas(-10, use_dask)
        tmin[1] = -20
        # WHEN
        result = count_events(
            das=[tmax, tmin],
            in_base_das=[None],
            logical_operation=[LogicalOperation.GREATER_THAN, LogicalOperation.EQUAL],
            thresholds=[12, -20],
            link_logical_operations=LinkLogicalOperation.AND_STAMP,
            freq="MS",
        )
        # THEN
        assert result[0] == 1


class Test_run_mean:
    @pytest.mark.parametrize("use_dask", [True, False])
    def test_simple_min(self, use_dask):
        # GIVEN
        tmax = stub_tas(10, use_dask)
        tmax[30] = 0
        tmax[29] = 0
        tmax[28] = 0
        tmax[27] = 0
        tmax[26] = 0
        # WHEN
        result = run_mean(
            da=tmax,
            extreme_mode=ExtremeMode.MIN,
            window_width=5,
            freq="MS",
        )
        # THEN
        assert result[0] == 0
        assert result[1] == 2
        assert result[2] == 10

    @pytest.mark.parametrize("use_dask", [True, False])
    def test_simple_max(self, use_dask):
        # GIVEN
        tmax = stub_tas(10, use_dask)
        tmax[30] = 20
        # WHEN
        result = run_mean(
            da=tmax,
            extreme_mode=ExtremeMode.MAX,
            window_width=2,
            freq="MS",
        )
        # THEN
        assert result[0] == 15
        assert result[1] == 15
        assert result[2] == 10


class Test_run_sum:
    @pytest.mark.parametrize("use_dask", [True, False])
    def test_simple_min(self, use_dask):
        # GIVEN
        tmax = stub_tas(10, use_dask)
        tmax[30] = 0
        tmax[29] = 0
        tmax[28] = 0
        tmax[27] = 0
        tmax[26] = 0
        # WHEN
        result = run_sum(
            da=tmax,
            extreme_mode=ExtremeMode.MIN,
            window_width=5,
            freq="MS",
        )
        # THEN
        assert result[0] == 0
        assert result[1] == 10
        assert result[2] == 50

    @pytest.mark.parametrize("use_dask", [True, False])
    def test_simple_max(self, use_dask):
        # GIVEN
        tmax = stub_tas(10, use_dask)
        tmax[30] = 20
        # WHEN
        result = run_sum(
            da=tmax,
            extreme_mode=ExtremeMode.MAX,
            window_width=2,
            freq="MS",
        )
        # THEN
        assert result[0] == 30
        assert result[1] == 30
        assert result[2] == 20


class Test_max_consecutive_event_count:
    @pytest.mark.parametrize("use_dask", [True, False])
    def test_simple(self, use_dask):
        # GIVEN
        tmax = stub_tas(10, use_dask)
        tmax[30] = 15  # On 31th january
        # WHEN
        result = max_consecutive_event_count(
            da=tmax,
            logical_operation=LogicalOperation.EQUAL,
            threshold=10.0,
            freq="YS",
        )
        # THEN
        assert result[0] == 334
        assert result[1] == 365


class Test_anomaly:
    @pytest.mark.parametrize("use_dask", [True, False])
    def test_simple(self, use_dask):
        # GIVEN
        tmax = stub_tas(10, use_dask)
        tmax2 = stub_tas(11, use_dask)
        # WHEN
        result = anomaly(da_ref=tmax, da=tmax2, percent=False)
        # THEN
        assert result == 1

    @pytest.mark.parametrize("use_dask", [True, False])
    def test_simple_percent(self, use_dask):
        # GIVEN
        tmax = stub_tas(10, use_dask)
        tmax2 = stub_tas(11, use_dask)
        # WHEN
        result = anomaly(da_ref=tmax, da=tmax2, percent=True)
        # THEN
        assert result == 10
        assert result.attrs["units"] == "%"
