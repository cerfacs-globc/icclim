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
from enum import Enum
from typing import TYPE_CHECKING

import pandas as pd

from icclim._core.climate_variable import ClimateVariable, must_run_bootstrap
from icclim._core.generic.threshold.bounded import BoundedThreshold
from icclim._core.generic.threshold.percentile import PercentileThreshold
from icclim._core.model.operator import Operator

if TYPE_CHECKING:
    from xarray import DataArray

    from icclim._core.model.threshold import Threshold
    from icclim.frequency import Frequency

try:
    from enum import StrEnum
except ImportError:  # pragma: no cover - Python 3.10 compatibility

    class StrEnum(str, Enum):
        """Fallback ``StrEnum`` for Python versions older than 3.11."""


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
    DAY_OF_YEAR_PERCENTILE_VALUE_AGGREGATE = "day_of_year_percentile_value_aggregate"
    FILTERED_DAY_OF_YEAR_PERCENTILE_VALUE_AGGREGATE = (
        "filtered_day_of_year_percentile_value_aggregate"
    )
    DAY_OF_YEAR_PERCENTILE_SPELL = "day_of_year_percentile_spell"
    FILTERED_DAY_OF_YEAR_PERCENTILE_SPELL = "filtered_day_of_year_percentile_spell"
    DAY_OF_YEAR_PERCENTILE_COMPOUND = "day_of_year_percentile_compound"
    FILTERED_DAY_OF_YEAR_PERCENTILE_COMPOUND = (
        "filtered_day_of_year_percentile_compound"
    )


class BootstrapReducerKind(StrEnum):
    """Reducer families that affect bootstrap routing."""

    NOT_APPLICABLE = "not_applicable"
    COUNT = "count"
    VALUE_AGGREGATE = "value_aggregate"
    SPELL = "spell"


@dataclass(frozen=True)
class BootstrapThresholdInventory:
    """Summarize bootstrap-relevant threshold facts for one computation."""

    required_percentile_thresholds: tuple[PercentileThreshold, ...]
    has_bounded_threshold: bool
    has_filtered_percentile: bool
    has_bootstrap_disabled_percentile: bool

    @property
    def bootstrap_required(self) -> bool:
        return bool(self.required_percentile_thresholds)


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
    not_required_reason = _count_bootstrap_not_required_reason(threshold_kind)
    if not_required_reason is not None:
        return _not_required(not_required_reason)
    if not isinstance(threshold_spec, PercentileThreshold):
        return _not_required("threshold_is_not_day_of_year_percentile")
    if climate_var.bootstrap is False:
        return _not_required("bootstrap_disabled_by_user")
    if not must_run_bootstrap(
        climate_var.studied_data,
        threshold_spec,
        climate_var.bootstrap,
    ):
        return _not_required("bootstrap_not_needed_for_overlap")
    return _classify_required_optimized_percentile_bootstrap(
        family=_classify_count_family(threshold_spec),
        study=climate_var.studied_data,
        threshold_spec=threshold_spec,
        output_frequency=resample_frequency.pandas_freq,
    )


def classify_doy_percentile_value_aggregate_bootstrap(
    climate_var: ClimateVariable,
    resample_frequency: Frequency,
) -> BootstrapCapability:
    """Classify bootstrap routing for optimized percentile value aggregates."""
    threshold_spec = climate_var.threshold
    threshold_kind = classify_threshold_kind(threshold_spec)
    not_required_reason = _count_bootstrap_not_required_reason(threshold_kind)
    if not_required_reason is not None:
        return _not_required(not_required_reason)
    if not isinstance(threshold_spec, PercentileThreshold):
        return _not_required("threshold_is_not_day_of_year_percentile")
    if climate_var.bootstrap is False:
        return _not_required("bootstrap_disabled_by_user")
    if not must_run_bootstrap(
        climate_var.studied_data,
        threshold_spec,
        climate_var.bootstrap,
    ):
        return _not_required("bootstrap_not_needed_for_overlap")
    return _classify_required_optimized_percentile_bootstrap(
        family=_classify_value_aggregate_family(threshold_spec),
        study=climate_var.studied_data,
        threshold_spec=threshold_spec,
        output_frequency=resample_frequency.pandas_freq,
    )


def _classify_required_optimized_percentile_bootstrap(
    *,
    family: BootstrapComputationFamily,
    study: DataArray,
    threshold_spec: PercentileThreshold,
    output_frequency: str,
) -> BootstrapCapability:
    from xclim.core.utils import uses_dask  # noqa: PLC0415

    if not uses_dask(study):
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
        study,
        threshold_spec,
        output_frequency,
    )
    if optimized_path_blocker is not None:
        return _exact_tiled_bootstrap(family, optimized_path_blocker)
    return BootstrapCapability(
        family=family,
        execution_kind=BootstrapExecutionKind.OPTIMIZED_BOOTSTRAP,
        bootstrap_required=True,
        reason_code="optimized_bootstrap_supported",
    )


def classify_generic_indicator_bootstrap(
    *,
    indicator_name: str,
    climate_vars: list[ClimateVariable],
    resample_frequency: Frequency,
    date_event: bool = False,
) -> BootstrapCapability:
    """Classify bootstrap routing for a generic indicator computation."""
    inventory = _build_bootstrap_threshold_inventory(climate_vars)
    if not inventory.bootstrap_required:
        if inventory.has_bootstrap_disabled_percentile:
            return _not_required("bootstrap_disabled_by_user")
        return _not_required("bootstrap_not_required_for_indicator")

    reducer_kind = _classify_bootstrap_reducer_kind(indicator_name)
    if reducer_kind == BootstrapReducerKind.NOT_APPLICABLE:
        return _not_required("indicator_has_no_bootstrap_family")

    family = _classify_generic_bootstrap_family(
        reducer_kind=reducer_kind,
        inventory=inventory,
    )
    if _uses_specialized_count_routing(
        reducer_kind=reducer_kind,
        climate_vars=climate_vars,
        date_event=date_event,
        inventory=inventory,
    ):
        return classify_doy_percentile_count_bootstrap(
            climate_var=climate_vars[0],
            resample_frequency=resample_frequency,
        )
    if _uses_specialized_value_aggregate_routing(
        indicator_name=indicator_name,
        reducer_kind=reducer_kind,
        climate_vars=climate_vars,
        date_event=date_event,
        inventory=inventory,
    ):
        return classify_doy_percentile_value_aggregate_bootstrap(
            climate_var=climate_vars[0],
            resample_frequency=resample_frequency,
        )
    return _reference_bootstrap_path(
        family,
        _reference_bootstrap_reason_code(
            reducer_kind=reducer_kind,
            climate_vars=climate_vars,
            date_event=date_event,
            inventory=inventory,
        ),
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


def _classify_value_aggregate_family(
    threshold_spec: PercentileThreshold,
) -> BootstrapComputationFamily:
    if threshold_spec.threshold_min_value is not None:
        return (
            BootstrapComputationFamily.FILTERED_DAY_OF_YEAR_PERCENTILE_VALUE_AGGREGATE
        )
    return BootstrapComputationFamily.DAY_OF_YEAR_PERCENTILE_VALUE_AGGREGATE


def _classify_bootstrap_reducer_kind(
    indicator_name: str,
) -> BootstrapReducerKind:
    if indicator_name == "count_occurrences":
        return BootstrapReducerKind.COUNT
    if indicator_name in {
        "fraction_of_total",
        "excess",
        "deficit",
        "maximum",
        "minimum",
        "average",
        "sum",
        "standard_deviation",
        "max_of_rolling_sum",
        "min_of_rolling_sum",
        "max_of_rolling_average",
        "min_of_rolling_average",
    }:
        return BootstrapReducerKind.VALUE_AGGREGATE
    if indicator_name in {
        "max_consecutive_occurrence",
        "sum_of_spell_lengths",
    }:
        return BootstrapReducerKind.SPELL
    return BootstrapReducerKind.NOT_APPLICABLE


def _build_bootstrap_threshold_inventory(
    climate_vars: list[ClimateVariable],
) -> BootstrapThresholdInventory:
    required_thresholds: list[PercentileThreshold] = []
    has_bounded_threshold = False
    has_filtered_percentile = False
    has_bootstrap_disabled_percentile = False
    for climate_var in climate_vars:
        threshold_spec = climate_var.threshold
        if threshold_spec is None:
            continue
        if isinstance(threshold_spec, BoundedThreshold):
            has_bounded_threshold = True
        for percentile_threshold in _iter_percentile_thresholds(threshold_spec):
            if percentile_threshold.threshold_min_value is not None:
                has_filtered_percentile = True
            if must_run_bootstrap(
                climate_var.studied_data,
                percentile_threshold,
                climate_var.bootstrap,
            ):
                required_thresholds.append(percentile_threshold)
            elif climate_var.bootstrap is False and must_run_bootstrap(
                climate_var.studied_data,
                percentile_threshold,
                bootstrap=None,
            ):
                has_bootstrap_disabled_percentile = True
    return BootstrapThresholdInventory(
        required_percentile_thresholds=tuple(required_thresholds),
        has_bounded_threshold=has_bounded_threshold,
        has_filtered_percentile=has_filtered_percentile,
        has_bootstrap_disabled_percentile=has_bootstrap_disabled_percentile,
    )


def _iter_percentile_thresholds(
    threshold_spec: Threshold,
) -> tuple[PercentileThreshold, ...]:
    if isinstance(threshold_spec, PercentileThreshold):
        return (threshold_spec,)
    if isinstance(threshold_spec, BoundedThreshold):
        return (
            *_iter_percentile_thresholds(threshold_spec.left_threshold),
            *_iter_percentile_thresholds(threshold_spec.right_threshold),
        )
    return ()


def _classify_generic_bootstrap_family(
    *,
    reducer_kind: BootstrapReducerKind,
    inventory: BootstrapThresholdInventory,
) -> BootstrapComputationFamily:
    if inventory.has_bounded_threshold:
        family_group = "compound"
    elif reducer_kind == BootstrapReducerKind.COUNT:
        family_group = "count"
    elif reducer_kind == BootstrapReducerKind.VALUE_AGGREGATE:
        family_group = "value_aggregate"
    else:
        family_group = "spell"
    family_map = {
        (False, "compound"): BootstrapComputationFamily.DAY_OF_YEAR_PERCENTILE_COMPOUND,
        (
            True,
            "compound",
        ): BootstrapComputationFamily.FILTERED_DAY_OF_YEAR_PERCENTILE_COMPOUND,
        (False, "count"): BootstrapComputationFamily.DAY_OF_YEAR_PERCENTILE_COUNT,
        (
            True,
            "count",
        ): BootstrapComputationFamily.FILTERED_DAY_OF_YEAR_PERCENTILE_COUNT,
        (
            False,
            "value_aggregate",
        ): BootstrapComputationFamily.DAY_OF_YEAR_PERCENTILE_VALUE_AGGREGATE,
        (
            True,
            "value_aggregate",
        ): BootstrapComputationFamily.FILTERED_DAY_OF_YEAR_PERCENTILE_VALUE_AGGREGATE,
        (False, "spell"): BootstrapComputationFamily.DAY_OF_YEAR_PERCENTILE_SPELL,
        (
            True,
            "spell",
        ): BootstrapComputationFamily.FILTERED_DAY_OF_YEAR_PERCENTILE_SPELL,
    }
    return family_map[(inventory.has_filtered_percentile, family_group)]


def _uses_specialized_count_routing(
    *,
    reducer_kind: BootstrapReducerKind,
    climate_vars: list[ClimateVariable],
    date_event: bool,
    inventory: BootstrapThresholdInventory,
) -> bool:
    if reducer_kind != BootstrapReducerKind.COUNT:
        return False
    if date_event or len(climate_vars) != 1 or inventory.has_bounded_threshold:
        return False
    threshold_spec = climate_vars[0].threshold
    return isinstance(threshold_spec, PercentileThreshold) and bool(
        inventory.required_percentile_thresholds
    )


def _uses_specialized_value_aggregate_routing(
    *,
    indicator_name: str,
    reducer_kind: BootstrapReducerKind,
    climate_vars: list[ClimateVariable],
    date_event: bool,
    inventory: BootstrapThresholdInventory,
) -> bool:
    if indicator_name != "fraction_of_total":
        return False
    if reducer_kind != BootstrapReducerKind.VALUE_AGGREGATE:
        return False
    if (
        date_event
        or len(climate_vars) != 1
        or inventory.has_bounded_threshold
        or inventory.has_filtered_percentile
    ):
        return False
    threshold_spec = climate_vars[0].threshold
    return isinstance(threshold_spec, PercentileThreshold) and bool(
        inventory.required_percentile_thresholds
    )


def _reference_bootstrap_reason_code(
    *,
    reducer_kind: BootstrapReducerKind,
    climate_vars: list[ClimateVariable],
    date_event: bool,
    inventory: BootstrapThresholdInventory,
) -> str:
    if inventory.has_bounded_threshold:
        return "bounded_threshold_uses_reference_bootstrap_path"
    if len(climate_vars) > 1:
        return "multiple_climate_variables_use_reference_bootstrap_path"
    if date_event:
        return "date_event_uses_reference_bootstrap_path"
    if reducer_kind == BootstrapReducerKind.VALUE_AGGREGATE:
        return "value_aggregate_uses_reference_bootstrap_path"
    if reducer_kind == BootstrapReducerKind.SPELL:
        return "spell_uses_reference_bootstrap_path"
    return "count_uses_reference_bootstrap_path"


def _count_bootstrap_not_required_reason(
    threshold_kind: BootstrapThresholdKind,
) -> str | None:
    reasons = {
        BootstrapThresholdKind.MISSING: "missing_threshold",
        BootstrapThresholdKind.BASIC_THRESHOLD: "threshold_is_not_percentile",
        BootstrapThresholdKind.COMPOUND_THRESHOLD: "threshold_is_compound",
        BootstrapThresholdKind.PERIOD_PERCENTILE_THRESHOLD: "threshold_is_not_day_of_year_percentile",
    }
    return reasons.get(threshold_kind)


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
    blockers = [
        (
            threshold_spec.threshold_min_value is not None,
            "threshold_min_value_requires_exact_tiled_bootstrap",
        ),
        (
            not isinstance(study.indexes.get("time"), pd.DatetimeIndex),
            "calendar_requires_exact_tiled_bootstrap",
        ),
        (
            threshold_spec.only_leap_years,
            "only_leap_years_requires_exact_tiled_bootstrap",
        ),
        (
            threshold_spec.percentile_coord().size != 1,
            "multiple_percentiles_require_exact_tiled_bootstrap",
        ),
        (
            not _is_optimized_bootstrap_frequency(output_frequency),
            "output_frequency_not_supported_by_optimized_bootstrap",
        ),
        (
            _operator_code(threshold_spec.operator) < 0,
            "operator_not_supported_by_optimized_bootstrap",
        ),
        (
            not _optimized_bootstrap_is_available(),
            "optimized_bootstrap_unavailable",
        ),
    ]
    for is_blocked, reason_code in blockers:
        if is_blocked:
            return reason_code
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
