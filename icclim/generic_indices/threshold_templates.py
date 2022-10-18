from __future__ import annotations

from typing import Any, TypedDict

# fmt: off
# flake8: noqa
from numpy import ndarray
from pint import Quantity


class ThresholdMetadata(TypedDict):
    long_name: str
    short_name: str
    standard_name: str

class ThresholdTemplateDict(TypedDict):
    single_value: ThresholdMetadata
    multiple_values: ThresholdMetadata
    single_doy_percentile: ThresholdMetadata
    multiple_doy_percentiles: ThresholdMetadata
    single_period_percentile: ThresholdMetadata
    multiple_period_percentiles: ThresholdMetadata
    bounded_threshold: ThresholdMetadata

class PercentileTemplateConfig(TypedDict, total=False):
    climatology_bounds: list[str]
    doy_window_width: int
    src_freq: Any
    operator: Any
    unit: str | None
    per_coord: ndarray | float
    threshold_min_value: Quantity | None
    must_run_bootstrap: bool

DOY_PER_METHOD = (
    "day of year percentiles were computed per grid cell, on the"
    " {{climatology_bounds}} period, with a"
    " {{doy_window_width}}"
    " {{src_freq.units}} centred window to aggregate values around each day of year")
PERIOD_PER_META = (
    "period percentiles were computed per grid cell, on the"
    " {{climatology_bounds}} period")
BOOTSTRAP_META = (
    "the bootstrap algorithm (Zhang, 2005) has been applied to compute doy"
    " percentiles for the period overlapping both the reference"
    " period and the studied period")
THRESHOLD_MIN_VALUE_TEMPLATE = (
    "(only values >= {{threshold_min_value}}"
    " {{unit}} were considered to compute thresholds)")

EN_THRESHOLD_TEMPLATE: ThresholdTemplateDict = {
    "single_value":   {
        "standard_name": "{{operator.standard_name}}_threshold",
        "long_name":     "{{operator.long_name}}"
                         " {{value.values[()]}}"
                         " {{unit}}",
        "short_name":    "{{operator.short_name}}_threshold",
    },
    "multiple_values": {
        "standard_name": "{{operator.standard_name}}_thresholds",
        "long_name":     "{{operator.long_name}}"
                         "{% if value.size < 10 %}"
                             " {{value.values}}"
                             " {{unit}}"
                         "{% else %}"
                             " per grid cell values between"
                             " {{min_value}}"
                             " {{unit}}"
                             " and {{max_value}}"
                             " {{unit}}."
                         "{% endif %}"
                         "{% if threshold_min_value %}"
                             f" {THRESHOLD_MIN_VALUE_TEMPLATE}"
                         "{% endif %}",
        "short_name":    "{{operator.short_name}}_threshold",
    },
    "single_doy_percentile": {
        "standard_name": "{{operator.standard_name}}_doy_percentile_threshold",
        "long_name":     "{{operator.long_name}}"
                         " {{per_coord}}th day of year percentile"
                         "{% if threshold_min_value %}"
                             f" {THRESHOLD_MIN_VALUE_TEMPLATE}"
                         "{% endif %}",
        "short_name":    "doy_per_threshold",
    },
    "multiple_doy_percentiles": {
        "standard_name": "{{operator.standard_name}}_doy_percentile_thresholds",
        "long_name":     "{{operator.long_name}}"
                         " {{per_coord}} day of year percentiles"
                         "{% if threshold_min_value %}"
                             f" {THRESHOLD_MIN_VALUE_TEMPLATE}"
                         "{% endif %}",
        "short_name":    "doy_per_thresholds",
    },
    "single_period_percentile": {
        "standard_name": "{{operator.standard_name}}_period_percentile_threshold",
        "long_name":     "{{operator.long_name}}"
                         " {{per_coord}}th period percentile"
                         "{% if threshold_min_value %}"
                             f" {THRESHOLD_MIN_VALUE_TEMPLATE}"
                         "{% endif %}",
        "short_name":    "period_per_threshold",
    },
    "multiple_period_percentiles": {
        "standard_name": "{{operator.standard_name}}_period_percentile_thresholds",
        "long_name":     "{{operator.long_name}}"
                         " {{per_coord}} period percentiles"
                         "{% if threshold_min_value %}"
                             f" {THRESHOLD_MIN_VALUE_TEMPLATE}"
                         "{% endif %}",
        "short_name":    "period_per_thresholds",
    },
    "bounded_threshold": {
        "standard_name": "{{left_threshold.standard_name}}"
                         "_{{logical_link.standard_name}}"
                         "_{{right_threshold.standard_name}}",
        "long_name":     "{{left_threshold.long_name}}"
                         " {{logical_link.long_name}}"
                         " {{right_threshold.long_name}}",
        "short_name":    "{{left_threshold.short_name}}"
                         "_{{logical_link.short_name}}"
                         "_{{right_threshold.short_name}}",
    },
}
