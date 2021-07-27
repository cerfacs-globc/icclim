from icclim.models.frequency import Frequency
from icclim.models.indice_config import CfVariable
from icclim.user_indice.user_indice import LogicalOperation, PRECIPITATION, TEMPERATURE
from icclim.tests.stubs import (
    stub_da,
    stub_pr,
    stub_user_indice,
)
from icclim.user_indice.operation import (
    apply_coef,
    compute_user_indice,
    filter_by_logical_op,
    user_indice_max,
    user_indice_mean,
    user_indice_min,
    user_indice_sum,
)
import numpy as np


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
        result = user_indice_max(stub, da)
        # THEN
        assert np.testing.assert_equal(result.data, 20) is None


class Test_user_indice_min:
    def test_simple(self):
        da = stub_da()
        da.data[1] = -20
        stub = stub_user_indice()
        # WHEN
        result = user_indice_min(stub, da)
        # THEN
        assert result.data == -20


class Test_user_indice_mean:
    def test_simple(self):
        stub = stub_user_indice()
        da = stub_da()
        # WHEN
        result = user_indice_mean(stub, da)
        # THEN
        assert result.data == 1


class Test_user_indice_sum:
    def test_simple(self):
        da = stub_da()
        stub = stub_user_indice()
        # WHEN
        result = user_indice_sum(stub, da)
        # THEN
        assert result.data == 366 * 5


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
