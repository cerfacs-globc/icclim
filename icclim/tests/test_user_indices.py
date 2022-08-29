from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from icclim.models.frequency import FrequencyRegistry
from icclim.models.operator import OperatorRegistry
from icclim.models.user_index_config import UserIndexConfig


class Test_UserindexConfig:
    @patch("icclim.models.climate_variable.ClimateVariable")
    @pytest.mark.parametrize("use_dask", [True, False])
    def test_simple_from_dict(self, climate_var_mock: MagicMock, use_dask):
        dico = {
            "index_name": "my_index",
            "calc_operation": "min",
            "logical_operation": "gt",
            "thresh": 0 + 273.15,
            "date_event": True,
        }
        config = UserIndexConfig(
            **dico,
            freq=FrequencyRegistry.MONTH,
            climate_variables=[climate_var_mock],
        )
        assert config.index_name == "my_index"
        assert config.calc_operation == "min"
        assert config.logical_operation == OperatorRegistry.GREATER
        assert config.thresh == 273.15
        assert config.date_event
        assert config.freq == FrequencyRegistry.MONTH
        assert config.climate_variables[0] is climate_var_mock
