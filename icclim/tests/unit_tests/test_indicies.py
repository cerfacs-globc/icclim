import pytest

from icclim.eca_indices import Indice, indice_from_string, tn10p
from icclim.models.frequency import Frequency
from icclim.models.indice_config import CfVariable, IndiceConfig
from icclim.tests.unit_tests.stubs import stub_tas


class Test_indice_from_string:
    def test_simple(self):
        res = indice_from_string("SU")
        assert res == Indice.SU

    def test_lowercase(self):
        res = indice_from_string("tx90p")
        assert res == Indice.TX90P

    def test_error(self):
        with pytest.raises(Exception):
            indice_from_string("cacahuête")


def test_tn10p():
    conf = IndiceConfig()
    conf.cf_variables = [CfVariable(da=stub_tas(), in_base_da=stub_tas())]
    conf.window = 2
    conf.save_percentile = True
    conf.freq = Frequency.MONTH
    res = tn10p(conf)
    assert res is not None
