from generic_indices.cf_var_metadata import IndicatorMetadata

# fmt: off
# flake8: noqa

COMBINED_VARS_LONG_NAME = (
    "{% for i, climate_var in enumerate(climate_vars) %}"
        "{{climate_var.long_name}} is"
        " {{climate_var.threshold.long_name}}"
        "{% if climate_var.threshold.additional_metadata %}"
            " {{climate_var.threshold.additional_metadata}}"
        "{% endif %}"
        "{% if i != len(climate_vars) - 1 %}"
            " and "
        "{% endif%}"
    "{% endfor %}"
)
COMBINED_VARS_IDENTIFIER = (
    "{% for i, climate_var in enumerate(climate_vars) %}"
        "{{climate_var.short_name}}_is"
        "_{{climate_var.threshold.standard_name}}"
        "{% if i != len(climate_vars) - 1 %}"
            "_and_"
        "{% endif%}"
    "{% endfor %}"
)
COMBINED_VARS_STANDARD_NAME = (
    "{% for i, climate_var in enumerate(climate_vars) %}"
        "{{climate_var.standard_name}}"
        "{% if i != len(climate_vars) - 1 %}"
            "_and_"
        "{% endif %}"
    "{% endfor %}"
)
OPTIONAL_THRESHOLD_TEMPLATE = (
    "{% if climate_vars[0].threshold %}"
        "when {{climate_vars[0].long_name}} is {{climate_vars[0].threshold.long_name}}"
    "{% endif %}"
)

EN: dict[str, IndicatorMetadata] = {
    "count_occurrences":          {
        "identifier":    "number_of_{{source_freq.units}}_when"
                         f"_{COMBINED_VARS_IDENTIFIER}",
        "long_name":     "Number of {{source_freq.units}}"
                         f" when {COMBINED_VARS_LONG_NAME}"
                         " each {{output_freq.long_name}}.",
        "standard_name": "number_of_{{source_freq.units}}_with"
                         f"_{COMBINED_VARS_STANDARD_NAME}"
                         "_above_threshold",
        "cell_methods":  "time: sum over {{source_freq.units}}",
    },
    "max_consecutive_occurrence": {
        "identifier":    "max_consecutive_{{source_freq.units}}_when"
                         f"_{COMBINED_VARS_IDENTIFIER}",
        "standard_name": "spell_length_of_{{source_freq.units}}_with"
                         f"_{COMBINED_VARS_STANDARD_NAME}"
                         "_above_threshold",
        "long_name":     "Maximum number of consecutive {{source_freq.units}} when"
                         f" {COMBINED_VARS_LONG_NAME}"
                         " each {{output_freq.long_name}}.",
        "cell_methods":  "time: maximum over {{source_freq.units}}",
    },
    "sum_of_spell_lengths":       {
        "identifier":   "sum_of_spell_lengths_of_{{source_freq.units}}_when"
                        f"_{COMBINED_VARS_IDENTIFIER}",
        "standard_name":  # not cf
                        "spell_length_of_{{source_freq.units}}_with"
                        f"_{COMBINED_VARS_STANDARD_NAME}"
                        "_above_thresholds",
        "long_name":    "Sum of spell lengths of at least {{min_spell_length}}"
                        " {{source_freq.units}} when"
                        f" {COMBINED_VARS_LONG_NAME}"
                        " each {{output_freq.long_name}}.",
        "cell_methods": "time: sum over {{source_freq.units}}",
    },
    "excess":                     {
        "identifier":    "integral_of"
                         "_{{source_freq.adjective}}"
                         "_{{climate_vars[0].standard_name}}"
                         "_{{climate_vars[0].threshold.standard_name}}"
                         "_excess",
        "standard_name": "integral_of"
                         "_{{climate_vars[0].standard_name}}"
                         "_excess_wrt_time",
        "long_name":     "Excess of {{source_freq.adjective}}"
                         " {{climate_vars[0].long_name}}"
                         " related to{{climate_vars[0].threshold.long_name}}"
                         " each {{output_freq.long_name}}."
                         "{% if climate_vars[0].threshold.additional_metadata %}"
                            " {{climate_vars[0].threshold.additional_metadata}}"
                         "{% endif %}",
        "cell_methods":  "time: sum over {{source_freq.units}}",
    },
    "deficit":                    {
        "identifier":    "integral_of_{{source_freq.adjective}}"
                         "_{{climate_vars[0].standard_name}}"
                         "_{{climate_vars[0].threshold.standard_name}}"
                         "_deficit",
        "standard_name": "integral_of_{{climate_vars[0].standard_name}}"
                         "_deficit_wrt_time",
        "long_name":     "Deficit of {{source_freq.adjective}}"
                         " {{climate_vars[0].long_name}}"
                         " related to{{climate_vars[0].threshold.value}}"
                         " each {{output_freq.long_name}}."
                         "{% if climate_vars[0].threshold.additional_metadata %}"
                            " {{climate_vars[0].threshold.additional_metadata}}"
                         "{% endif %}",
        "cell_methods":  "time: sum over {{source_freq.units}}",
    },
    "fraction_of_total":          {
        "identifier":   "fraction_of_thresholded_{{climate_vars[0].standard_name}}"
                        "_on_total",
        "standard_name":  # not cf
                        "fraction_of_thresholded_{{climate_vars[0].standard_name}}"
                        "_on_total",
        "long_name":    (
            "Fraction of {{source_freq.adjective}}"
            " {{climate_vars[0].long_name}}"
            " {{climate_vars[0].threshold.long_name}}"
            " on total {{climate_vars[0].long_name}}"
            " each {{output_freq.long_name}}."
            "{% if climate_vars[0].threshold.additional_metadata %}"
                " {{climate_vars[0].threshold.additional_metadata}}"
            "{% endif %}"
        ),
        # not cf
        "cell_methods": "time: fraction over {{source_freq.units}}",
    },
    "maximum":                    {
        "identifier":    "maximum_of_{{source_freq.adjective}}"
                         "_{{climate_vars[0].standard_name}}",
        "standard_name": "{{climate_vars[0].standard_name}}",
        "long_name":     "Maximum of {{source_freq.adjective}}"
                         " {{climate_vars[0].long_name}}"
                         f" {OPTIONAL_THRESHOLD_TEMPLATE}"
                         " each {{output_freq.long_name}}.",
        "cell_methods":  "time: maximum over {{source_freq.units}}",
    },
    "minimum":                    {
        "identifier":   "minimum_of_{{source_freq.adjective}}"
                        "_{{climate_vars[0].standard_name}}",
        "standard_name":
                        "{{climate_vars[0].standard_name}}"
        ,
        "long_name":    "Minimum of {{source_freq.adjective}}"
                        " {{climate_vars[0].long_name}}"
                        f" {OPTIONAL_THRESHOLD_TEMPLATE}"
                        " each {{output_freq.long_name}}.",
        "cell_methods": "time: minimum over {{source_freq.units}}",
    },
    "average":                    {
        "identifier":    "average_of_{{source_freq.adjective}}"
                         "_{{climate_vars[0].standard_name}}",
        "standard_name": "{{climate_vars[0].standard_name}}",
        "long_name":     "Average of {{source_freq.adjective}}"
                         " {{climate_vars[0].long_name}}"
                         f" {OPTIONAL_THRESHOLD_TEMPLATE}"
                         " each {{output_freq.long_name}}.",
        "cell_methods":  "time: mean over {{source_freq.units}}",
    },
    "sum":                        {
        "identifier":    "sum_of_{{source_freq.adjective}}"
                         "_{{climate_vars[0].standard_name}}"
        ,
        "standard_name": "{{climate_vars[0].standard_name}}"
        ,
        "long_name":     "Sum of {{source_freq.adjective}}"
                         " {{climate_vars[0].long_name}}"
                         f" {OPTIONAL_THRESHOLD_TEMPLATE}"
                         " each {{output_freq.long_name}}."
        ,
        "cell_methods":  "time: sum over {{source_freq.units}}",
    },
    "std":                        {
        "identifier":    "standard_deviation_of_{{source_freq.adjective}}"
                         "_{{climate_vars[0].standard_name}}",
        "standard_name": "{{climate_vars[0].standard_name}}",
        "long_name":     "Standard deviation of {{source_freq.adjective}}"
                         " {{climate_vars[0].long_name}}"
                         f" {OPTIONAL_THRESHOLD_TEMPLATE}"
                         " each {{output_freq.long_name}}."
        ,
        "cell_methods":  "time: standard_deviation over {{source_freq.units}}",
    },
}
