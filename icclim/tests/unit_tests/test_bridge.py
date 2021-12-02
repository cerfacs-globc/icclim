import pytest

from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.models.frequency import Frequency
from icclim.models.indice_config import CfVariable
from icclim.models.user_indice_config import (
    PRECIPITATION,
    TEMPERATURE,
    LogicalOperation,
)
from icclim.tests.unit_tests.test_utils import stub_pr, stub_tas, stub_user_indice
from icclim.user_indices.dispatcher import CalcOperation, compute_user_index


class Test_compute:
    def test_error_bad_operation(self):
        # GIVEN
        cf_var = CfVariable(stub_tas(), stub_tas())
        user_indice = stub_user_indice([cf_var])
        user_indice.calc_operation = "pouet pouet"
        user_indice.freq = Frequency.MONTH
        # WHEN
        with pytest.raises(InvalidIcclimArgumentError):
            compute_user_index(user_indice)

    def test_simple(self):
        # GIVEN
        cf_var = CfVariable(stub_tas(), stub_tas())
        user_indice = stub_user_indice([cf_var])
        user_indice.calc_operation = "max"
        user_indice.freq = Frequency.MONTH
        # WHEN
        result = compute_user_index(user_indice)
        # THEN
        assert result.data[0] == 1

    def test_simple_percentile_pr(self):
        # GIVEN
        cf_var = CfVariable(stub_pr(5), stub_pr(5))
        cf_var.da.data[15:30] += 10
        cf_var.da.data[366 + 15 : 366 + 30] = 2  # Ignore because not in base
        cf_var.in_base_da = cf_var.da.sel(time=cf_var.da.time.dt.year == 2042)
        user_indice = stub_user_indice([cf_var])
        user_indice.calc_operation = CalcOperation.MIN
        user_indice.thresh = "90p"
        user_indice.logical_operation = LogicalOperation.GREATER_OR_EQUAL_THAN
        user_indice.var_type = PRECIPITATION
        user_indice.freq = Frequency.YEAR
        # WHEN
        result = compute_user_index(user_indice)
        # THEN
        assert result.data[0] == 5

    def test_simple_percentile_temp(self):
        cf_var = CfVariable(stub_tas(5), stub_tas(5))
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
        result = compute_user_index(user_indice)
        # THEN
        assert result.data[0] == 1
        assert result.data[1] == 5
