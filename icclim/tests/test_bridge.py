import numpy as np

from icclim.models.frequency import Frequency
from icclim.models.indice_config import CfVariable
from icclim.tests.stubs import stub_pr, stub_tas, stub_user_indice
from icclim.user_indice.bridge import compute_user_indice
from icclim.user_indice.user_indice import PRECIPITATION, TEMPERATURE, LogicalOperation


class Test_compute:
    def test_simple(self):
        cf_var = CfVariable(stub_tas())
        stub = stub_user_indice([cf_var])
        stub.calc_operation = "max"
        stub.freq = Frequency.MONTH
        # WHEN
        result = compute_user_indice(stub)
        # THEN
        assert result.data[0] == 1

    def test_simple_percentile_pr(self):
        cf_var = CfVariable(da=stub_pr(5))
        cf_var.da.data[15:30] += 10
        cf_var.da.data[366 + 15 : 366 + 30] = 2  # Ignore because not in base
        cf_var.in_base_da = cf_var.da.sel(time=cf_var.da.time.dt.year == 2042)
        stub = stub_user_indice([cf_var])
        stub.calc_operation = "min"
        stub.thresh = "90p"
        stub.logical_operation = LogicalOperation.GREATER_OR_EQUAL_THAN
        stub.var_type = PRECIPITATION
        stub.freq = Frequency.YEAR
        # WHEN
        result = compute_user_indice(stub)
        # THEN
        assert result.data[0] == 5

    def test_simple_percentile_temp(self):
        cf_var = CfVariable(da=stub_tas())
        cf_var.da.data[15:30] += 10
        cf_var.in_base_da = cf_var.da.sel(
            time=cf_var.da.time.dt.year.isin([2042, 2043])
        )
        stub = stub_user_indice([cf_var])
        stub.calc_operation = "min"
        stub.thresh = "90p"
        stub.logical_operation = LogicalOperation.GREATER_OR_EQUAL_THAN
        stub.var_type = TEMPERATURE
        stub.freq = Frequency.MONTH
        # WHEN
        result = compute_user_indice(stub)
        # THEN
        assert result.data[0] == 5
