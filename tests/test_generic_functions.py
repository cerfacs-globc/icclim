from icclim._core.climate_variable import ClimateVariable
from icclim._core.constants import GROUP_BY_METHOD
from icclim._core.generic.functions import percentile
from icclim._core.model.standard_variable import StandardVariableRegistry
from icclim.frequency import FrequencyRegistry
from icclim.threshold.factory import build_threshold

from tests.testing_utils import stub_tas


def test_percentile() -> None:
    tas = stub_tas(42)
    tas[0:10] = -5
    study = ClimateVariable(
        name="tas",
        standard_var=StandardVariableRegistry.TAS,
        studied_data=tas,
        threshold=build_threshold("> 2 period_per"),
        source_frequency=FrequencyRegistry.DAY,
        global_metadata={},
    )
    climate_vars = [study]
    result = percentile(
        climate_vars=climate_vars,
        to_percent=False,
        sampling_method=GROUP_BY_METHOD,
        resample_freq=FrequencyRegistry.MONTH,
        is_compared_to_reference=False,
    )
    assert result[0] == -5
