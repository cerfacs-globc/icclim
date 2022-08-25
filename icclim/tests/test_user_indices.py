from __future__ import annotations

import pytest

from icclim.models.frequency import FrequencyRegistry
from icclim.models.index_config import ClimateVariable
from icclim.models.operator import OperatorRegistry
from icclim.models.user_index_config import UserIndexConfig
from icclim.tests.testing_utils import stub_tas


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
            **dico,
            freq=FrequencyRegistry.MONTH,
            climate_variables=[ClimateVariable("tas", tas, tas)],
        )
        assert config.index_name == "my_index"
        assert config.calc_operation == "min"
        assert config.logical_operation == OperatorRegistry.GREATER
        assert config.thresh == 273.15
        assert config.date_event
        assert config.freq == FrequencyRegistry.MONTH
        assert config.climate_variables[0].studied_data is tas
