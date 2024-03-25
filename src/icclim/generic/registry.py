"""Contain the registry of generic indicators."""

from __future__ import annotations

from typing import TYPE_CHECKING

from icclim._core.constants import (
    GROUP_BY_METHOD,
    GROUP_BY_REF_AND_RESAMPLE_STUDY_METHOD,
    RESAMPLE_METHOD,
)
from icclim._core.generic.functions import (
    average,
    count_occurrences,
    deficit,
    difference_of_extremes,
    difference_of_means,
    excess,
    fraction_of_total,
    generic_sum,
    max_consecutive_occurrence,
    max_of_rolling_average,
    max_of_rolling_sum,
    maximum,
    mean_of_absolute_one_time_step_difference,
    mean_of_difference,
    min_of_rolling_average,
    min_of_rolling_sum,
    minimum,
    percentile,
    standard_deviation,
    sum_of_spell_lengths,
)
from icclim._core.generic.indicator import GenericIndicator
from icclim._core.model.registry import Registry
from icclim.exception import InvalidIcclimArgumentError

if TYPE_CHECKING:
    from icclim._core.climate_variable import ClimateVariable


def _check_single_var(
    climate_vars: list[ClimateVariable], indicator: GenericIndicator
) -> None:
    if len(climate_vars) > 1:
        msg = f"{indicator.name} can only be computed on a single variable."
        raise InvalidIcclimArgumentError(msg)


def _check_couple_of_vars(
    climate_vars: list[ClimateVariable],
    indicator: GenericIndicator,
) -> None:
    if len(climate_vars) != 2:
        msg = (
            f"{indicator.name} can only be computed on two variables sharing the same"
            f" unit (e.g. 2 temperatures). You can either provide a secondary variable"
            f" with `in_files` or `var_name`, or you can let icclim compute this"
            f" second variable as a subset of the first one using"
            f" `base_period_time_range`."
        )
        raise InvalidIcclimArgumentError(msg)


class GenericIndicatorRegistry(Registry[GenericIndicator]):
    """Registry of generic indicators."""

    def __init__(self) -> None:
        super().__init__()

    _item_class = GenericIndicator

    CountOccurrences = GenericIndicator(
        "count_occurrences",
        count_occurrences,
        definition="Count occurrences when threshold(s) are met"
        " (e.g. SU, Tx90p, RR1).",
    )
    MaxConsecutiveOccurrence = GenericIndicator(
        "max_consecutive_occurrence",
        max_consecutive_occurrence,
        definition="Count the maximum number of consecutive occurrences when"
        " threshold(s) are met (e.g. CDD, CSU, CWD).",
    )
    SumOfSpellLengths = GenericIndicator(
        "sum_of_spell_lengths",
        sum_of_spell_lengths,
        definition="Sum the lengths of each consecutive occurrence spell when"
        " threshold(s) are met. The minimum spell length is controlled by"
        " `min_spell_length` (e.g. WSDI, CSDI).",
    )
    Excess = GenericIndicator(
        "excess",
        excess,
        check_vars=_check_single_var,
        definition="Compute the excess over the given threshold. The excess is"
        " `sum(x[x>t] - t)` where x is the studied variable and t the threshold"
        " (e.g. GD4).",
    )
    Deficit = GenericIndicator(
        "deficit",
        deficit,
        check_vars=_check_single_var,
        definition="Compute the deficit below the given threshold. The deficit is"
        " `sum(t - x[x<t])` where x is the studied variable and t the threshold"
        " (e.g. HD17).",
    )
    FractionOfTotal = GenericIndicator(
        "fraction_of_total",
        fraction_of_total,
        check_vars=_check_single_var,
        definition="Compute the fraction of values meeting threshold(s) over the sum of"
        " every values (e.g. R75pTOT, R95pTOT).",
    )
    Maximum = GenericIndicator(
        "maximum",
        maximum,
        definition="Maximum of values that met threshold(s), if threshold(s) are given"
        " (e.g. Txx, Tnx).",
    )
    Minimum = GenericIndicator(
        "minimum",
        minimum,
        definition="Minimum of values that met threshold(s), if threshold(s) are given"
        " (e.g. Txn, Tnn).",
    )
    Average = GenericIndicator(
        "average",
        average,
        definition="Average of values that met threshold(s), if threshold(s) are given"
        " (e.g. Tx, Tn).",
    )
    Sum = GenericIndicator(
        "sum",
        generic_sum,
        definition="Sum of values that met threshold(s), if threshold(s) are given"
        " (e.g. PRCPTOT, RR).",
    )
    StandardDeviation = GenericIndicator(
        "standard_deviation",
        standard_deviation,
        definition="Standard deviation of values that met threshold(s),"
        " if threshold(s) are given.",
    )
    MaxOfRollingSum = GenericIndicator(
        "max_of_rolling_sum",
        max_of_rolling_sum,
        check_vars=_check_single_var,
        definition="Maximum of rolling sum over time dimension"
        " (e.g. RX5DAY: maximum 5 days window of precipitation accumulation).",
    )
    MinOfRollingSum = GenericIndicator(
        "min_of_rolling_sum",
        min_of_rolling_sum,
        check_vars=_check_single_var,
        definition="Minimum of rolling sum over time dimension.",
    )
    MaxOfRollingAverage = GenericIndicator(
        "max_of_rolling_average",
        max_of_rolling_average,
        check_vars=_check_single_var,
        definition="Maximum of rolling average over time dimension.",
    )
    MinOfRollingAverage = GenericIndicator(
        "min_of_rolling_average",
        min_of_rolling_average,
        check_vars=_check_single_var,
        definition="Minimum of rolling average over time dimension.",
    )
    MeanOfDifference = GenericIndicator(
        "mean_of_difference",
        mean_of_difference,
        check_vars=_check_couple_of_vars,
        definition="Average of the difference between two variables"
        ", or one variable and it's reference period values"
        " (e.g. DTR: `mean(tasmax - tasmin)`).",
        qualifiers=["compute_diff"],
    )
    DifferenceOfExtremes = GenericIndicator(
        "difference_of_extremes",
        difference_of_extremes,
        check_vars=_check_couple_of_vars,
        definition="Difference of extremes between two variables"
        ", or one variable and it's reference period values."
        " The extremes are always `maximum` for the first variable and"
        " `minimum` for the second variable"
        " (e.g. ETR: `max(tasmax) - min(tasmin)`).",
        qualifiers=["compute_diff"],
    )
    MeanOfAbsoluteOneTimeStepDifference = GenericIndicator(
        "mean_of_absolute_one_time_step_difference",
        mean_of_absolute_one_time_step_difference,
        check_vars=_check_couple_of_vars,
        definition="Average of the absolute one time step by one time step difference"
        " between two variables,"
        " or one variable and it's reference period values"
        " (e.g. vDTR:"
        " `mean((tasmax[i] - tasmin[i]) - (tasmax[i-1] - tasmin[i-1])` ;"
        " where i is the day of measure).",
        qualifiers=["compute_diff"],
    )
    DifferenceOfMeans = GenericIndicator(
        "difference_of_means",
        difference_of_means,
        check_vars=_check_couple_of_vars,
        sampling_methods=[
            RESAMPLE_METHOD,
            GROUP_BY_METHOD,
            GROUP_BY_REF_AND_RESAMPLE_STUDY_METHOD,
        ],
        definition="Difference of the average between two variables"
        ", or one variable and it's reference period values"
        " (e.g. anomaly: `mean(tasmax) - mean(tasmax_ref]))`.",
        qualifiers=["compute_diff"],
    )
    Percentile = GenericIndicator(
        "percentile",
        percentile,
        check_vars=_check_single_var,
        definition="Percentile of a variable.",
    )
