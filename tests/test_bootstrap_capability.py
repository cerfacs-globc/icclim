from __future__ import annotations

import xarray as xr

from icclim._core.climate_variable import ClimateVariable
from icclim._core.generic.bootstrap_capability import (
    BootstrapComputationFamily,
    BootstrapExecutionKind,
    BootstrapThresholdKind,
    classify_threshold_kind,
    classify_doy_percentile_count_bootstrap,
)
from icclim._core.model.standard_variable import StandardVariableRegistry
from icclim.frequency import FrequencyRegistry
from icclim.threshold.factory import build_threshold
from tests.testing_utils import K2C, stub_tas


def _build_climate_variable(
    studied_data: xr.DataArray,
    threshold: str | dict | None,
    *,
    bootstrap: bool | None = None,
) -> ClimateVariable:
    resolved_threshold = (
        build_threshold(**threshold)
        if isinstance(threshold, dict)
        else build_threshold(threshold)
        if threshold is not None
        else None
    )
    return ClimateVariable(
        name="tas",
        standard_var=StandardVariableRegistry.TAS,
        studied_data=studied_data,
        threshold=resolved_threshold,
        source_frequency=FrequencyRegistry.DAY,
        global_metadata={},
        bootstrap=bootstrap,
    )


def test_dask_day_of_year_percentile_count_uses_fast_path() -> None:
    tas = stub_tas(27 + K2C).chunk({"time": 365, "lat": 1, "lon": 1})
    climate_var = _build_climate_variable(
        tas,
        {
            "query": "> 90 doy_per",
            "doy_window_width": 1,
            "reference_period": ("2042-01-01", "2043-12-31"),
        },
    )

    decision = classify_doy_percentile_count_bootstrap(
        climate_var,
        FrequencyRegistry.MONTH,
    )

    assert decision.family == BootstrapComputationFamily.DAY_OF_YEAR_PERCENTILE_COUNT
    assert decision.execution_kind == BootstrapExecutionKind.FAST
    assert decision.reason_code == "fast_path_supported"


def test_threshold_kind_classification_covers_basic_percentile_and_bounded() -> None:
    assert classify_threshold_kind(None) == BootstrapThresholdKind.MISSING
    assert (
        classify_threshold_kind(build_threshold("> 20 degC"))
        == BootstrapThresholdKind.BASIC_THRESHOLD
    )
    assert (
        classify_threshold_kind(build_threshold("> 90 doy_per"))
        == BootstrapThresholdKind.DAY_OF_YEAR_PERCENTILE_THRESHOLD
    )
    assert (
        classify_threshold_kind(build_threshold("> 90 period_per"))
        == BootstrapThresholdKind.PERIOD_PERCENTILE_THRESHOLD
    )
    assert (
        classify_threshold_kind(
            build_threshold(
                thresholds=["> 90 doy_per", "<= 30 degC"],
                logical_link="and",
            )
        )
        == BootstrapThresholdKind.COMPOUND_THRESHOLD
    )


def test_threshold_min_value_routes_to_safe_fallback() -> None:
    pr = stub_tas(5.0).rename("pr")
    pr.attrs["units"] = "mm/day"
    pr = pr.chunk({"time": 365, "lat": 1, "lon": 1})
    climate_var = _build_climate_variable(
        pr,
        {
            "query": "> 90 doy_per",
            "threshold_min_value": "1 mm/day",
            "reference_period": ("2042-01-01", "2043-12-31"),
        },
    )

    decision = classify_doy_percentile_count_bootstrap(
        climate_var,
        FrequencyRegistry.YEAR,
    )

    assert (
        decision.family
        == BootstrapComputationFamily.FILTERED_DAY_OF_YEAR_PERCENTILE_COUNT
    )
    assert decision.execution_kind == BootstrapExecutionKind.SAFE_FALLBACK
    assert decision.reason_code == "threshold_min_value_requires_safe_fallback"


def test_cftime_routes_to_safe_fallback() -> None:
    tas = stub_tas(27 + K2C, use_cftime=True).chunk({"time": 365, "lat": 1, "lon": 1})
    climate_var = _build_climate_variable(
        tas,
        {
            "query": "> 90 doy_per",
            "doy_window_width": 1,
            "reference_period": ("2042-01-01", "2043-12-31"),
        },
    )

    decision = classify_doy_percentile_count_bootstrap(
        climate_var,
        FrequencyRegistry.YEAR,
    )

    assert decision.execution_kind == BootstrapExecutionKind.SAFE_FALLBACK
    assert decision.reason_code == "calendar_requires_safe_fallback"


def test_eager_input_uses_legacy_bootstrap_path() -> None:
    tas = stub_tas(27 + K2C)
    climate_var = _build_climate_variable(
        tas,
        {
            "query": "> 90 doy_per",
            "doy_window_width": 1,
            "reference_period": ("2042-01-01", "2043-12-31"),
        },
    )

    decision = classify_doy_percentile_count_bootstrap(
        climate_var,
        FrequencyRegistry.YEAR,
    )

    assert decision.execution_kind == BootstrapExecutionKind.LEGACY
    assert decision.reason_code == "eager_input_uses_xclim_bootstrap"


def test_bootstrap_disabled_by_user_is_not_required() -> None:
    tas = stub_tas(27 + K2C).chunk({"time": 365, "lat": 1, "lon": 1})
    climate_var = _build_climate_variable(
        tas,
        {
            "query": "> 90 doy_per",
            "doy_window_width": 1,
            "reference_period": ("2042-01-01", "2043-12-31"),
        },
        bootstrap=False,
    )

    decision = classify_doy_percentile_count_bootstrap(
        climate_var,
        FrequencyRegistry.YEAR,
    )

    assert decision.execution_kind == BootstrapExecutionKind.NOT_REQUIRED
    assert decision.reason_code == "bootstrap_disabled_by_user"


def test_bounded_threshold_is_not_routed_through_count_fast_path() -> None:
    tas = stub_tas(27 + K2C).chunk({"time": 365, "lat": 1, "lon": 1})
    climate_var = _build_climate_variable(
        tas,
        {
            "thresholds": ["> 90 doy_per", "<= 30 degC"],
            "logical_link": "and",
        },
    )

    decision = classify_doy_percentile_count_bootstrap(
        climate_var,
        FrequencyRegistry.YEAR,
    )

    assert decision.execution_kind == BootstrapExecutionKind.NOT_REQUIRED
    assert decision.reason_code == "threshold_is_compound"
