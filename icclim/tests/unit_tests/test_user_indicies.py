from icclim.models.frequency import Frequency
from icclim.models.indice_config import CfVariable
from icclim.models.user_indice_config import LogicalOperation, UserIndiceConfig
from icclim.tests.unit_tests.stubs import stub_tas


class Test_UserIndice:
    def test_simple(self):
        dico = {
            "indice_name": "my_indice",
            "calc_operation": "min",
            "logical_operation": "gt",
            "thresh": 0 + 273.15,
            "date_event": True,
        }
        tas = stub_tas()
        plop = UserIndiceConfig(**dico, freq=Frequency.MONTH, cf_vars=[CfVariable(tas)])
        assert plop.indice_name == "my_indice"
        assert plop.calc_operation == "min"
        assert plop.logical_operation == LogicalOperation.GREATER_THAN
        assert plop.thresh == 273.15
        assert plop.date_event
        assert plop.freq == Frequency.MONTH
        assert plop.cf_vars[0].da is tas
