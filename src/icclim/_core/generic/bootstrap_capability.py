"""Bootstrap routing helpers for percentile-based indices."""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import StrEnum

import pandas as pd
from xarray import DataArray

from icclim._core.climate_variable import ClimateVariable, must_run_bootstrap
from icclim._core.generic.threshold.percentile import PercentileThreshold
from icclim._core.model.operator import Operator
from icclim.frequency import Frequency


class BootstrapComputationFamily(StrEnum):
    """High-level bootstrap computation families supported by icclim."""

    NOT_APPLICABLE = "not_applicable"
    DAY_OF_YEAR_PERCENTILE_COUNT = "day_of_year_percentile_count"
    FILTERED_DAY_OF_YEAR_PERCENTILE_COUNT = "filtered_day_of_year_percentile_count"


class BootstrapExecutionKind(StrEnum):
    """Concrete execution paths currently available inside icclim."""

    NOT_REQUIRED = "not_required"
    LEGACY = "legacy"
    SAFE_FALLBACK = "safe_fallback"
    FAST = "fast"


@dataclass(frozen=True)
class BootstrapCapability:
    """Describe the bootstrap routing decision for one computation."""

    family: BootstrapComputationFamily
    execution_kind: BootstrapExecutionKind
    bootstrap_required: bool
    reason_code: str

    @property
    def uses_fast_path(self) -> bool:
        return self.execution_kind == BootstrapExecutionKind.FAST

    @property
    def uses_safe_fallback(self) -> bool:
        return self.execution_kind == BootstrapExecutionKind.SAFE_FALLBACK

    @property
    def uses_legacy_path(self) -> bool:
        return self.execution_kind == BootstrapExecutionKind.LEGACY


def classify_doy_percentile_count_bootstrap(
    climate_var: ClimateVariable,
    resample_frequency: Frequency,
) -> BootstrapCapability:
    """Classify the current bootstrap path for day-of-year percentile counts."""
    threshold = climate_var.threshold
    if threshold is None:
        return _not_required("missing_threshold")
    if not isinstance(threshold, PercentileThreshold):
        return _not_required("threshold_is_not_percentile")
    if not threshold.is_doy_per_threshold:
        return _not_required("threshold_is_not_day_of_year_percentile")
    if climate_var.bootstrap is False:
        return _not_required("bootstrap_disabled_by_user")
    if not must_run_bootstrap(
        climate_var.studied_data,
        threshold,
        climate_var.bootstrap,
    ):
        return _not_required("bootstrap_not_needed_for_overlap")

    family = _classify_count_family(threshold)

    from xclim.core.utils import uses_dask  # noqa: PLC0415

    if not uses_dask(climate_var.studied_data):
        return _legacy(family, "eager_input_uses_xclim_bootstrap")
    if os.environ.get("ICCLIM_BOOTSTRAP_MODE") == "default":
        return _legacy(family, "legacy_mode_forced")
    if os.environ.get("ICCLIM_BOOTSTRAP_MODE") == "safe":
        return _safe_fallback(family, "safe_mode_forced")
    if not is_fast_doy_percentile_count_supported(
        climate_var.studied_data,
        threshold,
        resample_frequency.pandas_freq,
    ):
        if threshold.threshold_min_value is not None:
            return _safe_fallback(
                family,
                "threshold_min_value_requires_safe_fallback",
            )
        if not isinstance(climate_var.studied_data.indexes.get("time"), pd.DatetimeIndex):
            return _safe_fallback(
                family,
                "calendar_requires_safe_fallback",
            )
        if threshold.only_leap_years:
            return _safe_fallback(
                family,
                "only_leap_years_requires_safe_fallback",
            )
        if threshold.percentile_coord().size != 1:
            return _safe_fallback(
                family,
                "multiple_percentiles_require_safe_fallback",
            )
        if not _is_fast_bootstrap_frequency(resample_frequency.pandas_freq):
            return _safe_fallback(
                family,
                "output_frequency_not_supported_by_fast_path",
            )
        if _operator_code(threshold.operator) < 0:
            return _safe_fallback(
                family,
                "operator_not_supported_by_fast_path",
            )
        return _safe_fallback(family, "fast_path_unavailable")
    return BootstrapCapability(
        family=family,
        execution_kind=BootstrapExecutionKind.FAST,
        bootstrap_required=True,
        reason_code="fast_path_supported",
    )


def is_fast_doy_percentile_count_supported(
    study: DataArray,
    threshold: PercentileThreshold,
    output_frequency: str,
) -> bool:
    """Return whether the compiled fast count path supports this case."""
    return (
        _is_fast_bootstrap_frequency(output_frequency)
        and isinstance(study.indexes.get("time"), pd.DatetimeIndex)
        and not threshold.only_leap_years
        and threshold.percentile_coord().size == 1
        and threshold.threshold_min_value is None
        and _operator_code(threshold.operator) >= 0
        and _numba_fast_path_is_available()
    )


def _classify_count_family(
    threshold: PercentileThreshold,
) -> BootstrapComputationFamily:
    if threshold.threshold_min_value is not None:
        return BootstrapComputationFamily.FILTERED_DAY_OF_YEAR_PERCENTILE_COUNT
    return BootstrapComputationFamily.DAY_OF_YEAR_PERCENTILE_COUNT


def _not_required(reason_code: str) -> BootstrapCapability:
    return BootstrapCapability(
        family=BootstrapComputationFamily.NOT_APPLICABLE,
        execution_kind=BootstrapExecutionKind.NOT_REQUIRED,
        bootstrap_required=False,
        reason_code=reason_code,
    )


def _legacy(
    family: BootstrapComputationFamily,
    reason_code: str,
) -> BootstrapCapability:
    return BootstrapCapability(
        family=family,
        execution_kind=BootstrapExecutionKind.LEGACY,
        bootstrap_required=True,
        reason_code=reason_code,
    )


def _safe_fallback(
    family: BootstrapComputationFamily,
    reason_code: str,
) -> BootstrapCapability:
    return BootstrapCapability(
        family=family,
        execution_kind=BootstrapExecutionKind.SAFE_FALLBACK,
        bootstrap_required=True,
        reason_code=reason_code,
    )


def _is_fast_bootstrap_frequency(freq: str) -> bool:
    return freq in {"MS", "YS"} or freq.startswith("YS-")


def _numba_fast_path_is_available() -> bool:
    try:
        from numba import njit  # noqa: PLC0415
    except Exception:  # noqa: BLE001
        return False
    return njit is not None


def _operator_code(operator: Operator | str) -> int:
    operand = operator.operand if isinstance(operator, Operator) else str(operator)
    return {">": 0, ">=": 1, "<": 2, "<=": 3}.get(operand, -1)
