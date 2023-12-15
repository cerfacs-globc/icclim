from __future__ import annotations

from typing import TypedDict

# fmt: off
# flake8: noqa

class IndicatorMetadata(TypedDict):
    standard_name: str
    long_name: str
    cell_methods: str

COMBINED_VARS_LONG_NAME = (
    "{% for i, climate_var in enumerate(climate_vars) %}"
        "{{climate_var.long_name}} is"
        " {{climate_var.threshold.long_name}}"
        "{% if i != len(climate_vars) - 1 %}"
            " And "
        "{% endif%}"
    "{% endfor %}"
    " for each {{output_freq.long_name}}."
)
COMBINED_VARS_STANDARD_NAME = (
    "{% for i, climate_var in enumerate(climate_vars) %}"
        "{{climate_var.standard_name}}"
        "_is_{{climate_var.threshold.standard_name}}"
        "{% if i != len(climate_vars) - 1 %}"
            "_and_"
        "{% endif %}"
    "{% endfor %}"
)
SINGLE_VAR_LONG_NAME = (
    "{{source_freq.adjective}}"
    " {{climate_vars[0].long_name}}"
    " related to {{climate_vars[0].threshold.value}}"
    " for each {{output_freq.long_name}}."
)
SINGLE_VAR_LONG_NAME_WITH_EXCEEDANCE = (
    "{{source_freq.adjective}}"
    " {{climate_vars[0].long_name}}"
    "{% if climate_vars[0].threshold %}"
        " when {{climate_vars[0].long_name}}"
        " is {{climate_vars[0].threshold.long_name}}"
    "{% endif %}"
    " for each {{output_freq.long_name}}."
)

INDICATORS_TEMPLATES_EN: dict[str, IndicatorMetadata] = {
    "count_occurrences": {
        "long_name":     "Number of {{source_freq.units}}"
                         f" when {COMBINED_VARS_LONG_NAME}",
        "standard_name": "number_of_{{source_freq.units}}_when"
                         f"_{COMBINED_VARS_STANDARD_NAME}",
        "cell_methods":  "time: sum over {{source_freq.units}}",
    },
    "max_consecutive_occurrence": {
        "standard_name": "spell_length_of_{{source_freq.units}}_with"
                         f"_{COMBINED_VARS_STANDARD_NAME}",
        "long_name":     "Maximum number of consecutive {{source_freq.units}} when"
                         f" {COMBINED_VARS_LONG_NAME}",
        "cell_methods":  "time: maximum over {{source_freq.units}}",
    },
    "sum_of_spell_lengths": {
        "standard_name":  # not CF
                        "spell_length_of_{{source_freq.units}}_with"
                        f"_{COMBINED_VARS_STANDARD_NAME}",
        "long_name":    "Sum of spell lengths of at least {{min_spell_length}}"
                        " {{source_freq.units}} when"
                        f" {COMBINED_VARS_LONG_NAME}",
        "cell_methods": "time: sum over {{source_freq.units}}",
    },
    "excess": {
        "standard_name": "integral_of"
                         "_{{climate_vars[0].standard_name}}"
                         "_excess_wrt_time",
        "long_name":     f"Excess of {SINGLE_VAR_LONG_NAME}",
        "cell_methods":  "time: difference over {{source_freq.units}}",
    },
    "deficit": {
        "standard_name": "integral_of_{{climate_vars[0].standard_name}}"
                         "_deficit_wrt_time",
        "long_name":     f"Deficit of {SINGLE_VAR_LONG_NAME}",
        "cell_methods":  "time: difference over {{source_freq.units}}",
    },
    "fraction_of_total": {
        "standard_name":  # not CF
                        "fraction_of_thresholded_{{climate_vars[0].standard_name}}"
                        "_on_total",
        "long_name":    f"Fraction of {SINGLE_VAR_LONG_NAME}",
        # not cf
        "cell_methods": "time: fraction over {{source_freq.units}}",
    },
    "maximum": {
        "standard_name": "{{climate_vars[0].standard_name}}",
        "long_name":     f"Maximum of {SINGLE_VAR_LONG_NAME_WITH_EXCEEDANCE}",
        "cell_methods":  "time: maximum over {{source_freq.units}}",
    },
    "minimum": {
        "standard_name":"{{climate_vars[0].standard_name}}",
        "long_name":    "Minimum of"
                        f" {SINGLE_VAR_LONG_NAME_WITH_EXCEEDANCE}",
        "cell_methods": "time: minimum over {{source_freq.units}}",
    },
    "average": {
        "standard_name": "{{climate_vars[0].standard_name}}",
        "long_name":     "Average of"
                         f" {SINGLE_VAR_LONG_NAME_WITH_EXCEEDANCE}",
        "cell_methods":  "time: mean over {{source_freq.units}}",
    },
    "sum": {
        "standard_name": "{{climate_vars[0].standard_name}}",
        "long_name":     "Sum of"
                         f" {SINGLE_VAR_LONG_NAME_WITH_EXCEEDANCE}",
        "cell_methods":  "time: sum over {{source_freq.units}}",
    },
    "standard_deviation": {
        "standard_name": "{{climate_vars[0].standard_name}}",
        "long_name":     "Standard deviation of"
                         f" {SINGLE_VAR_LONG_NAME_WITH_EXCEEDANCE}",
        "cell_methods":  "time: standard_deviation over {{source_freq.units}}",
    },
    "max_of_rolling_sum": {
        "standard_name": "{{climate_vars[0].standard_name}}",
        "long_name":     "Maximum {{rolling_window_width}}"
                         " {{source_freq.units}} rolling sum of"
                         f" {SINGLE_VAR_LONG_NAME_WITH_EXCEEDANCE}",
        "cell_methods":  "time: sum over {{source_freq.units}}",
    },
    "min_of_rolling_sum": {
        "standard_name": "{{climate_vars[0].standard_name}}",
        "long_name":     "Minimum {{rolling_window_width}}"
                         " {{source_freq.units}} rolling sum of"
                         f" {SINGLE_VAR_LONG_NAME_WITH_EXCEEDANCE}",
        "cell_methods":  "time: sum over {{source_freq.units}}",
    },
    "min_of_rolling_average": {
        "standard_name": "{{climate_vars[0].standard_name}}",
        "long_name":     "Minimum {{rolling_window_width}}"
                         " {{source_freq.units}} rolling average of"
                         f" {SINGLE_VAR_LONG_NAME_WITH_EXCEEDANCE}",
        "cell_methods":  "time: mean over {{source_freq.units}}",
    },
    "max_of_rolling_average": {
        "standard_name": "{{climate_vars[0].standard_name}}",
        "long_name":     "Maximum {{rolling_window_width}}"
                         " {{source_freq.units}} rolling average of"
                         f" {SINGLE_VAR_LONG_NAME_WITH_EXCEEDANCE}",
        "cell_methods":  "time: mean over {{source_freq.units}}",
    },
    "mean_of_difference": {
        "standard_name": "range_between_{{climate_vars[0].standard_name}}"
                         "_and_{{climate_vars[1].standard_name}}", # not CF
        "long_name":     "Mean of difference between {{climate_vars[0].long_name}}"
                         " and {{climate_vars[1].long_name}}"
                         " for each {{output_freq.long_name}}.",
        "cell_methods":  "time: range within {{source_freq.units}}"
                         " time: mean over {{source_freq.units}}",
    },
    "difference_of_extremes":  {
        "standard_name": "range_of_extremes_between_{{climate_vars[0].standard_name}}"
                         "_and_{{climate_vars[1].standard_name}}", # not CF
        "long_name":     "Difference between"
                         " maximum of {{source_freq.adjective}}"
                         " {{climate_vars[0].long_name}}"
                         " and minimum of {{source_freq.adjective}}"
                         " {{climate_vars[1].long_name}}"
                         " for each {{output_freq.long_name}}.",
        "cell_methods":  "time: range within {{source_freq.units}}"
                         " time: maximum over {{source_freq.units}}"
                         " time: minimum over {{source_freq.units}}",
    },
    "mean_of_absolute_one_time_step_difference":  {
        "standard_name": "variability_range_between_{{climate_vars[0].standard_name}}"
                         "_and_{{climate_vars[1].standard_name}}", # not CF
        "long_name":     "Average of the absolute {{source_freq.long_name}}"
                         " to {{source_freq.long_name}} difference"
                         " of the {{source_freq.adjective}} variation between"
                         " {{climate_vars[0].long_name}}"
                         " and {{climate_vars[1].long_name}}"
                         " for each {{output_freq.long_name}}.",
        "cell_methods":  "time: range within {{source_freq.units}}"
                         " time: difference over {{source_freq.units}}"
                         " time: mean over {{source_freq.units}}",
    },
    "difference_of_means":  {
        "standard_name": "{{climate_vars[0].standard_name}}"
                         "{% if not is_compared_to_reference %}"
                            "_to_{{climate_vars[1].standard_name}}"
                         "{% endif%}"
                         "_anomaly", # not CF
        "long_name":     "{{output_freq.adjective}} difference between the"
                         " averaged {{source_freq.adjective}}"
                         " {{climate_vars[0].long_name}}"
                         " and"
                         "{% if is_compared_to_reference %}"
                            " its averaged {{source_freq.adjective}} values for the"
                            " {{reference_period}} period."
                         "{% else %}"
                            " the {{output_freq.adjective}}"
                            " averaged {{source_freq.adjective}}"
                            " {{climate_vars[1].long_name}}"
                         "{% endif%}",
        "cell_methods":  "time: mean over {{source_freq.units}}"
                         " time: difference over {{source_freq.units}}",
    },
}
