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
        config = UserIndiceConfig(
            **dico, freq=Frequency.MONTH, cf_vars=[CfVariable(tas)]
        )
        assert config.indice_name == "my_indice"
        assert config.calc_operation == "min"
        assert config.logical_operation == LogicalOperation.GREATER_THAN
        assert config.thresh == 273.15
        assert config.date_event
        assert config.freq == Frequency.MONTH
        assert config.cf_vars[0].da is tas
