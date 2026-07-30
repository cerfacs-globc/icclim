"""Bootstrap routing helpers for percentile-based indices.

This module classifies bootstrap requests from threshold specifications,
not from prepared threshold fields or aligned daily threshold values.
That distinction matters because later bootstrap families will reuse the
same routing layer before any path decides how to materialize threshold
data.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import StrEnum

import pandas as pd
from xarray import DataArray

from icclim._core.climate_variable import ClimateVariable, must_run_bootstrap
from icclim._core.generic.threshold.bounded import BoundedThreshold
from icclim._core.generic.threshold.percentile import PercentileThreshold
from icclim._core.model.operator import Operator
from icclim._core.model.threshold import Threshold
from icclim.frequency import Frequency


class BootstrapThresholdKind(StrEnum):
    """Threshold specification shapes that matter for bootstrap routing."""

    MISSING = "missing"
    BASIC_THRESHOLD = "basic_threshold"
    DAY_OF_YEAR_PERCENTILE_THRESHOLD = "day_of_year_percentile_threshold"
    PERIOD_PERCENTILE_THRESHOLD = "period_percentile_threshold"
    COMPOUND_THRESHOLD = "compound_threshold"


class BootstrapComputationFamily(StrEnum):
    """High-level bootstrap computation families supported by icclim."""

    NOT_APPLICABLE = "not_applicable"
    DAY_OF_YEAR_PERCENTILE_COUNT = "day_of_year_percentile_count"
    FILTERED_DAY_OF_YEAR_PERCENTILE_COUNT = "filtered_day_of_year_percentile_count"


class BootstrapExecutionKind(StrEnum):
    """Concrete execution paths currently available inside icclim."""

    NOT_REQUIRED = "not_required"
    REFERENCE_BOOTSTRAP = "reference_bootstrap"
    EXACT_TILED_BOOTSTRAP = "exact_tiled_bootstrap"
    OPTIMIZED_BOOTSTRAP = "optimized_bootstrap"


@dataclass(frozen=True)
class BootstrapCapability:
    """Describe the bootstrap routing decision for one computation."""

    family: BootstrapComputationFamily
    execution_kind: BootstrapExecutionKind
    bootstrap_required: bool
    reason_code: str

    @property
    def uses_optimized_bootstrap(self) -> bool:
        return self.execution_kind == BootstrapExecutionKind.OPTIMIZED_BOOTSTRAP

    @property
    def uses_exact_tiled_bootstrap(self) -> bool:
        return self.execution_kind == BootstrapExecutionKind.EXACT_TILED_BOOTSTRAP

    @property
    def uses_reference_bootstrap_path(self) -> bool:
        return self.execution_kind == BootstrapExecutionKind.REFERENCE_BOOTSTRAP


def classify_doy_percentile_count_bootstrap(
    climate_var: ClimateVariable,
    resample_frequency: Frequency,
) -> BootstrapCapability:
    """Classify the current bootstrap path for day-of-year percentile counts."""
    threshold_spec = climate_var.threshold
    threshold_kind = classify_threshold_kind(threshold_spec)
    if threshold_kind == BootstrapThresholdKind.MISSING:
        return _not_required("missing_threshold")
    if threshold_kind == BootstrapThresholdKind.BASIC_THRESHOLD:
        return _not_required("threshold_is_not_percentile")
    if threshold_kind == BootstrapThresholdKind.COMPOUND_THRESHOLD:
        return _not_required("threshold_is_compound")
    if threshold_kind == BootstrapThresholdKind.PERIOD_PERCENTILE_THRESHOLD:
        return _not_required("threshold_is_not_day_of_year_percentile")
    assert isinstance(threshold_spec, PercentileThreshold)
    if climate_var.bootstrap is False:
        return _not_required("bootstrap_disabled_by_user")
    if not must_run_bootstrap(
        climate_var.studied_data,
        threshold_spec,
        climate_var.bootstrap,
    ):
        return _not_required("bootstrap_not_needed_for_overlap")

    family = _classify_count_family(threshold_spec)

    from xclim.core.utils import uses_dask  # noqa: PLC0415

    if not uses_dask(climate_var.studied_data):
        return _reference_bootstrap_path(
            family,
            "eager_input_uses_reference_bootstrap_path",
        )
    if os.environ.get("ICCLIM_BOOTSTRAP_MODE") == "default":
        return _reference_bootstrap_path(
            family,
            "reference_bootstrap_mode_forced",
        )
    if os.environ.get("ICCLIM_BOOTSTRAP_MODE") == "safe":
        return _exact_tiled_bootstrap(family, "exact_tiled_bootstrap_mode_forced")
    optimized_path_blocker = _optimized_count_path_blocker(
        climate_var.studied_data,
        threshold_spec,
        resample_frequency.pandas_freq,
    )
    if optimized_path_blocker is not None:
        return _exact_tiled_bootstrap(family, optimized_path_blocker)
    return BootstrapCapability(
        family=family,
        execution_kind=BootstrapExecutionKind.OPTIMIZED_BOOTSTRAP,
        bootstrap_required=True,
        reason_code="optimized_bootstrap_supported",
    )


def is_optimized_doy_percentile_count_supported(
    study: DataArray,
    threshold_spec: PercentileThreshold,
    output_frequency: str,
) -> bool:
    """Return whether the optimized count path supports this case."""
    return (
        _optimized_count_path_blocker(study, threshold_spec, output_frequency) is None
    )


def classify_threshold_kind(
    threshold_spec: Threshold | None,
) -> BootstrapThresholdKind:
    """Describe the structural shape of a threshold specification."""
    if threshold_spec is None:
        return BootstrapThresholdKind.MISSING
    if isinstance(threshold_spec, BoundedThreshold):
        return BootstrapThresholdKind.COMPOUND_THRESHOLD
    if not isinstance(threshold_spec, PercentileThreshold):
        return BootstrapThresholdKind.BASIC_THRESHOLD
    if threshold_spec.is_doy_per_threshold:
        return BootstrapThresholdKind.DAY_OF_YEAR_PERCENTILE_THRESHOLD
    return BootstrapThresholdKind.PERIOD_PERCENTILE_THRESHOLD


def _classify_count_family(
    threshold_spec: PercentileThreshold,
) -> BootstrapComputationFamily:
    if threshold_spec.threshold_min_value is not None:
        return BootstrapComputationFamily.FILTERED_DAY_OF_YEAR_PERCENTILE_COUNT
    return BootstrapComputationFamily.DAY_OF_YEAR_PERCENTILE_COUNT


def _not_required(reason_code: str) -> BootstrapCapability:
    return BootstrapCapability(
        family=BootstrapComputationFamily.NOT_APPLICABLE,
        execution_kind=BootstrapExecutionKind.NOT_REQUIRED,
        bootstrap_required=False,
        reason_code=reason_code,
    )


def _reference_bootstrap_path(
    family: BootstrapComputationFamily,
    reason_code: str,
) -> BootstrapCapability:
    return BootstrapCapability(
        family=family,
        execution_kind=BootstrapExecutionKind.REFERENCE_BOOTSTRAP,
        bootstrap_required=True,
        reason_code=reason_code,
    )


def _exact_tiled_bootstrap(
    family: BootstrapComputationFamily,
    reason_code: str,
) -> BootstrapCapability:
    return BootstrapCapability(
        family=family,
        execution_kind=BootstrapExecutionKind.EXACT_TILED_BOOTSTRAP,
        bootstrap_required=True,
        reason_code=reason_code,
    )


def _is_optimized_bootstrap_frequency(freq: str) -> bool:
    return freq in {"MS", "YS"} or freq.startswith("YS-")


def _optimized_count_path_blocker(
    study: DataArray,
    threshold_spec: PercentileThreshold,
    output_frequency: str,
) -> str | None:
    """Return the optimized-path blocker reason, or ``None`` when it is supported."""
    if threshold_spec.threshold_min_value is not None:
        return "threshold_min_value_requires_exact_tiled_bootstrap"
    if not isinstance(study.indexes.get("time"), pd.DatetimeIndex):
        return "calendar_requires_exact_tiled_bootstrap"
    if threshold_spec.only_leap_years:
        return "only_leap_years_requires_exact_tiled_bootstrap"
    if threshold_spec.percentile_coord().size != 1:
        return "multiple_percentiles_require_exact_tiled_bootstrap"
    if not _is_optimized_bootstrap_frequency(output_frequency):
        return "output_frequency_not_supported_by_optimized_bootstrap"
    if _operator_code(threshold_spec.operator) < 0:
        return "operator_not_supported_by_optimized_bootstrap"
    if not _optimized_bootstrap_is_available():
        return "optimized_bootstrap_unavailable"
    return None


def _optimized_bootstrap_is_available() -> bool:
    try:
        from numba import njit  # noqa: PLC0415
    except Exception:  # noqa: BLE001
        return False
    return njit is not None


def _operator_code(operator: Operator | str) -> int:
    operand = operator.operand if isinstance(operator, Operator) else str(operator)
    return {">": 0, ">=": 1, "<": 2, "<=": 3}.get(operand, -1)
