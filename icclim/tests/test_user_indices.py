import pytest

from icclim.models.frequency import Frequency
from icclim.models.index_config import CfVariable
from icclim.models.user_index_config import LogicalOperation, UserIndexConfig
from icclim.tests.test_utils import stub_tas


class Test_UserindexConfig:
    @pytest.mark.parametrize("use_dask", [True, False])
    def test_simple_from_dict(self, use_dask):
        dico = {
            "index_name": "my_index",
            "calc_operation": "min",
            "logical_operation": "gt",
            "thresh": 0 + 273.15,
            "date_event": True,
        }
        tas = stub_tas(use_dask=use_dask)
        config = UserIndexConfig(
            **dico, freq=Frequency.MONTH, cf_vars=[CfVariable("tas", tas, tas)]
        )
        assert config.index_name == "my_index"
        assert config.calc_operation == "min"
        assert config.logical_operation == LogicalOperation.GREATER_THAN
        assert config.thresh == 273.15
        assert config.date_event
        assert config.freq == Frequency.MONTH
        assert config.cf_vars[0].study_da is tas
