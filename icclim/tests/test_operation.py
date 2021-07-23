from icclim.user_indice.user_indice import LogicalOperation
from icclim.tests.stubs import (
    stub_da,
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
        stub = stub_user_indice()
        stub.coef = 4.0
        da = stub_da()
        # WHEN
        result = apply_coef(stub, da)
        # THEN
        assert np.testing.assert_equal(result.data, 4.0) is None


class Test_filter_by_logical_op:
    def test_simple(self):
        # GIVEN
        stub = stub_user_indice()
        stub.logical_operation = LogicalOperation.EQUAL
        stub.thresh = 1
        da = stub_da()
        # WHEN
        result = filter_by_logical_op(stub, da)
        # THEN
        assert len(result.data) == len(da)

    def test_simple(self):
        # GIVEN
        da = stub_da()
        stub = stub_user_indice()
        stub.logical_operation = LogicalOperation.GT
        stub.thresh = 1
        # WHEN
        result = filter_by_logical_op(stub, da)
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
        da = stub_da()
        stub = stub_user_indice()
        stub.calc_operation = "max"
        # WHEN
        result = compute_user_indice(stub, da)
        # THEN
        assert result.data == 1
