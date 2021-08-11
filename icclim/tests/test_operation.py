import numpy as np

from icclim.models.frequency import Frequency
from icclim.models.indice_config import CfVariable
from icclim.tests.stubs import stub_pr, stub_tas, stub_user_indice
from icclim.user_indice.operation import (
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
from icclim.user_indice.user_indice import (
    PRECIPITATION,
    TEMPERATURE,
    ExtremeMode,
    LinkLogicalOperation,
    LogicalOperation,
)


class Test_apply_coef:
    def test_simple(self):
        # GIVEN
        da = stub_tas()
        # WHEN
        result = _apply_coef(4.0, da)
        # THEN
        assert np.testing.assert_equal(result.data, 4.0) is None


class Test_max:
    # def test_NOT_simple(self):
    #     import xarray

    #     ds = xarray.open_dataset(
    #         "/Users/aoun/workspace/icclim/climpact.sampledata.gridded.1991-2010.nc"
    #     )

    #     result = count_events(
    #         das=[ds.tmax],
    #         in_base_das=[None],
    #         logical_operation=[LogicalOperation.GREATER_THAN],
    #         thresholds=[305],
    #         freq="MS",
    #         date_event=True,
    #     )

    #     result = max(
    #         da=ds.tmax,
    #         coef=1,
    #         logical_operation=None,
    #         threshold=None,
    #         freq="MS",
    #         date_event=True,
    #     )

    def test_simple(self):
        da = stub_tas()
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
    def test_simple(self):
        da = stub_tas()
        da.data[1] = -20
        # WHEN
        result = min(
            da=da,
            freq="YS",
        )
        # THEN
        assert result.data[0] == -20


class Test_mean:
    def test_simple(self):
        da = stub_tas()
        da[2] = 366
        # WHEN
        result = mean(
            da=da,
            freq="YS",
        )
        # THEN
        assert result.data[0] == 2


class Test_sum:
    def test_simple(self):
        da = stub_tas()
        # WHEN
        result = sum(
            da=da,
            freq="YS",
        )
        # THEN
        assert result.data[0] == 365


class Test_count_events:
    def test_simple(self):
        # GIVEN
        da = stub_tas(10)
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

    def test_simple_percentile(self):
        # GIVEN
        da = stub_tas(10)
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

    def test_multi_threshold_or(self):
        # GIVEN
        tmax = stub_tas(10)
        tmax[1] = 15
        tmin = stub_tas(-10)
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

    def test_multi_threshold_and(self):
        # GIVEN
        tmax = stub_tas(10)
        tmax[1] = 15
        tmin = stub_tas(-10)
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
    def test_simple_min(self):
        # GIVEN
        tmax = stub_tas(10)
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

    def test_simple_max(self):
        # GIVEN
        tmax = stub_tas(10)
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
    def test_simple_min(self):
        # GIVEN
        tmax = stub_tas(10)
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

    def test_simple_max(self):
        # GIVEN
        tmax = stub_tas(10)
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
    def test_simple(self):
        # GIVEN
        tmax = stub_tas(10)
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
    def test_simple(self):
        # GIVEN
        tmax = stub_tas(10)
        tmax2 = stub_tas(11)
        # WHEN
        result = anomaly(da_ref=tmax, da=tmax2, percent=False)
        # THEN
        assert result == 1

    def test_simple_percent(self):
        # GIVEN
        tmax = stub_tas(10)
        tmax2 = stub_tas(11)
        # WHEN
        result = anomaly(da_ref=tmax, da=tmax2, percent=True)
        # THEN
        assert result == 10
        assert result.attrs["units"] == "%"
