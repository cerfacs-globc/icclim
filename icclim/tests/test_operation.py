import numpy as np
from xclim.core.calendar import percentile_doy

from icclim.models.frequency import Frequency
from icclim.models.indice_config import CfVariable
from icclim.tests.stubs import stub_da, stub_pr, stub_user_indice
from icclim.user_indice.operation import (
    AND_STAMP,
    OR_STAMP,
    apply_coef,
    compute_user_indice,
    filter_by_logical_op,
    user_indice_count_events,
    user_indice_max,
    user_indice_mean,
    user_indice_min,
    user_indice_sum,
)
from icclim.user_indice.user_indice import PRECIPITATION, TEMPERATURE, LogicalOperation


class Test_apply_coef:
    def test_simple(self):
        # GIVEN
        da = stub_da()
        # WHEN
        result = apply_coef(4.0, da)
        # THEN
        assert np.testing.assert_equal(result.data, 4.0) is None


class Test_filter_by_logical_op:
    def test_simple(self):
        # GIVEN
        da = stub_da()
        # WHEN
        result = filter_by_logical_op(LogicalOperation.GREATER_THAN, 1, da)
        # THEN
        assert len(result.data) == 0


class Test_user_indice_max:
    def test_simple(self):
        da = stub_da()
        da.data[1] = 20
        # WHEN
        stub = stub_user_indice()
        result = user_indice_max(
            da=da,
            coef=stub.coef,
            logical_operation=stub.logical_operation,
            threshold=stub.thresh,
            freq=stub.freq.panda_freq,
            date_event=stub.date_event,
        )
        # THEN
        assert np.testing.assert_equal(result.data, 20) is None


class Test_user_indice_min:
    def test_simple(self):
        da = stub_da()
        da.data[1] = -20
        stub = stub_user_indice()
        # WHEN
        result = user_indice_min(
            da=da,
            coef=stub.coef,
            logical_operation=stub.logical_operation,
            threshold=stub.thresh,
            freq=stub.freq.panda_freq,
            date_event=stub.date_event,
        )
        # THEN
        assert result.data == -20


class Test_user_indice_mean:
    def test_simple(self):
        stub = stub_user_indice()
        da = stub_da()
        # WHEN
        result = user_indice_mean(
            da=da,
            coef=stub.coef,
            logical_operation=stub.logical_operation,
            threshold=stub.thresh,
            freq=stub.freq.panda_freq,
        )
        # THEN
        assert result.data == 1


class Test_user_indice_sum:
    def test_simple(self):
        da = stub_da()
        stub = stub_user_indice()
        # WHEN
        result = user_indice_sum(
            da=da,
            coef=stub.coef,
            logical_operation=stub.logical_operation,
            threshold=stub.thresh,
            freq=stub.freq.panda_freq,
        )
        # THEN
        assert result.data == 366 * 5


class Test_user_indice_count_events:
    def test_simple(self):
        # GIVEN
        da = stub_da(10)
        da[1] = 15
        da[2] = 16
        # WHEN
        result = user_indice_count_events(
            data_arrays=[da],
            logical_operation=[LogicalOperation.GREATER_THAN],
            thresholds=[15],
            freq="MS",
        )
        # THEN
        assert result[0] == 1

    def test_simple_percentile(self):
        # GIVEN
        da = stub_da(10)
        da[1] = 15
        da[2] = 16
        per = percentile_doy(da, 5, 80).sel(percentiles=80)
        # WHEN
        result = user_indice_count_events(
            data_arrays=[da],
            logical_operation=[LogicalOperation.GREATER_THAN],
            percentiles=[per],
            freq="MS",
        )
        # THEN
        assert result[0] == 2

    def test_multi_threshold_or(self):
        # GIVEN
        tmax = stub_da(10)
        tmax[1] = 15
        tmin = stub_da(-10)
        # WHEN
        result = user_indice_count_events(
            data_arrays=[tmax, tmin],
            logical_operation=[LogicalOperation.GREATER_THAN, LogicalOperation.EQUAL],
            thresholds=[12, -20],
            link_logical_operations=OR_STAMP,
            freq="MS",
        )
        # THEN
        assert result[0] == 1

    def test_multi_threshold_and(self):
        # GIVEN
        tmax = stub_da(10)
        tmax[1] = 15
        tmin = stub_da(-10)
        tmin[1] = -20
        # WHEN
        result = user_indice_count_events(
            data_arrays=[tmax, tmin],
            logical_operation=[LogicalOperation.GREATER_THAN, LogicalOperation.EQUAL],
            thresholds=[12, -20],
            link_logical_operations=AND_STAMP,
            freq="MS",
        )
        # THEN
        assert result[0] == 1


class Test_compute:
    def test_simple(self):
        cf_var = CfVariable(stub_da())
        stub = stub_user_indice()
        stub.calc_operation = "max"
        # WHEN
        result = compute_user_indice(stub, cf_var)
        # THEN
        assert result.data == 1

    def test_simple_percentile_pr(self):
        cf_var = CfVariable(da=stub_pr(5))
        cf_var.da.data[15:30] += 10
        cf_var.da.data[366 + 15 : 366 + 30] = 2  # Ignore because not in base
        cf_var.in_base_da = cf_var.da.sel(time=cf_var.da.time.dt.year == 2042)
        stub = stub_user_indice()
        stub.calc_operation = "min"
        stub.thresh = "90p"
        stub.logical_operation = LogicalOperation.GREATER_OR_EQUAL_THAN
        stub.var_type = PRECIPITATION
        # WHEN
        result = compute_user_indice(stub, cf_var)
        # THEN
        assert result.data == 5

    def test_simple_percentile_temp(self):
        cf_var = CfVariable(da=stub_da())
        cf_var.da.data[15:30] += 10
        cf_var.in_base_da = cf_var.da.sel(
            time=cf_var.da.time.dt.year.isin([2042, 2043])
        )
        stub = stub_user_indice()
        stub.calc_operation = "min"
        stub.thresh = "90p"
        stub.logical_operation = LogicalOperation.GREATER_OR_EQUAL_THAN
        stub.var_type = TEMPERATURE
        stub.freq = Frequency.MONTH
        # WHEN
        result = compute_user_indice(stub, cf_var)
        # THEN
        assert result.data == 5
