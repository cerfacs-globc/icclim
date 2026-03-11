from icclim._core.climate_variable import ClimateVariable
from icclim._core.constants import GROUP_BY_METHOD
from icclim._core.generic.functions import (
    average,
    count_occurrences,
    generic_sum,
    max_consecutive_occurrence,
    maximum,
    minimum,
    percentile,
)
from icclim._core.model.logical_link import LogicalLinkRegistry
from icclim._core.model.standard_variable import StandardVariableRegistry
from icclim.frequency import FrequencyRegistry
from icclim.threshold.factory import build_threshold
from tests.testing_utils import stub_tas


def _make_clim_var(tas_val=42, thresh="> 20 degC") -> ClimateVariable:
    tas = stub_tas(tas_val)
    return ClimateVariable(
        name="tas",
        standard_var=StandardVariableRegistry.TAS,
        studied_data=tas,
        threshold=build_threshold(thresh) if thresh else None,
        source_frequency=FrequencyRegistry.DAY,
        global_metadata={},
    )


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
    result = percentile(
        climate_vars=[study],
        to_percent=False,
        sampling_method=GROUP_BY_METHOD,
        resample_freq=FrequencyRegistry.MONTH,
        is_compared_to_reference=False,
    )
    assert result[0] == -5


def test_average() -> None:
    study = _make_clim_var(25.0, None)
    result = average(
        climate_vars=[study],
        resample_freq=FrequencyRegistry.YEAR,
    )
    assert result[0] == 25.0


def test_maximum() -> None:
    study = _make_clim_var(30.0, None)
    result = maximum(
        climate_vars=[study],
        resample_freq=FrequencyRegistry.YEAR,
        date_event=False,
    )
    assert result[0] == 30.0


def test_minimum() -> None:
    study = _make_clim_var(-10.0, None)
    result = minimum(
        climate_vars=[study],
        resample_freq=FrequencyRegistry.YEAR,
        date_event=False,
    )
    assert result[0] == -10.0


def test_count_occurrences() -> None:
    # 300 K is > 20 degC (293.15 K), so it occurs every day
    study = _make_clim_var(300.0, "> 20 degC")
    result = count_occurrences(
        climate_vars=[study],
        resample_freq=FrequencyRegistry.YEAR,
        logical_link=LogicalLinkRegistry.LOGICAL_AND,
        date_event=False,
        to_percent=False,
    )
    # the first year has 365 days
    assert int(result.isel(time=0).values) == 365


def test_generic_sum() -> None:
    study = _make_clim_var(2.0, None)
    result = generic_sum(
        climate_vars=[study],
        resample_freq=FrequencyRegistry.YEAR,
    )
    # 2.0 * len(YEAR) -> > 700 usually (365 or 366 days)
    assert float(result[0].mean().values) > 700


def test_max_consecutive_occurrence() -> None:
    # 300 K is > 20 degC, so consecutive exceedances equal the year length
    study = _make_clim_var(300.0, "> 20 degC")
    result = max_consecutive_occurrence(
        climate_vars=[study],
        resample_freq=FrequencyRegistry.YEAR,
        logical_link=LogicalLinkRegistry.LOGICAL_AND,
        date_event=False,
        source_freq_delta="1D",
    )
    assert int(result.isel(time=0).values) >= 365
