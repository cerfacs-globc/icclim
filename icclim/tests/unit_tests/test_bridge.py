from icclim.models.frequency import Frequency
from icclim.models.indice_config import CfVariable
from icclim.models.user_indice_config import (
    PRECIPITATION,
    TEMPERATURE,
    LogicalOperation,
)
from icclim.tests.unit_tests.stubs import stub_pr, stub_tas, stub_user_indice
from icclim.user_indices.bridge import compute_user_indice


class Test_compute:
    def test_simple(self):
        # GIVEN
        cf_var = CfVariable(stub_tas())
        stub = stub_user_indice([cf_var])
        stub.calc_operation = "max"
        stub.freq = Frequency.MONTH
        # WHEN
        result = compute_user_indice(stub)
        # THEN
        assert result.data[0] == 1

    def test_simple_percentile_pr(self):
        # GIVEN
        cf_var = CfVariable(da=stub_pr(5))
        cf_var.da.data[15:30] += 10
        cf_var.da.data[366 + 15 : 366 + 30] = 2  # Ignore because not in base
        cf_var.in_base_da = cf_var.da.sel(time=cf_var.da.time.dt.year == 2042)
        user_indice = stub_user_indice([cf_var])
        user_indice.calc_operation = "min"
        user_indice.thresh = "90p"
        user_indice.logical_operation = LogicalOperation.GREATER_OR_EQUAL_THAN
        user_indice.var_type = PRECIPITATION
        user_indice.freq = Frequency.YEAR
        # WHEN
        result = compute_user_indice(user_indice)
        # THEN
        assert result.data[0] == 5

    def test_simple_percentile_temp(self):
        cf_var = CfVariable(da=stub_tas(5))
        cf_var.da.data[15:30] = 1
        cf_var.in_base_da = cf_var.da.sel(
            time=cf_var.da.time.dt.year.isin([2042, 2043])
        )
        user_indice = stub_user_indice([cf_var])
        user_indice.calc_operation = "min"
        user_indice.thresh = "10p"
        user_indice.logical_operation = LogicalOperation.LOWER_OR_EQUAL_THAN
        user_indice.var_type = TEMPERATURE
        user_indice.freq = Frequency.MONTH
        # WHEN
        result = compute_user_indice(user_indice)
        # THEN
        assert result.data[0] == 1
        assert result.data[1] == 5
