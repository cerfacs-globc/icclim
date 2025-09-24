"""
Implementations of the generic indices computation methods.

These functions are not meant to be called directly, they are used by the
`GenericIndicatorRegistry` class to create the generic indices.
Each function is a reducer that takes a list of `ClimateVariable` instances and returns
a `DataArray` instance.
The `ClimateVariable` instances are used to extract the data and the thresholds needed
to compute the generic index.
The `DataArray` instance is the result of the computation of the generic index.

.. note::

   You can call the respective generic index from icclim module, for example:
   `icclim.count_occurrences(...)`.
"""

from __future__ import annotations

import operator
from collections.abc import Callable
from functools import partial
from typing import TYPE_CHECKING
from warnings import warn

import xarray as xr
from numpy import abs as np_abs
from numpy import diff as np_diff
from numpy import median as np_median
from pandas import Timedelta, date_range, infer_freq, to_timedelta
from xarray import DataArray
from xarray.computation.rolling import DataArrayRolling
from xarray.core.resample import DataArrayResample
from xclim.core.calendar import build_climatology_bounds
from xclim.core.units import (
    convert_units_to,
    rate2amount,
    str2pint,
    to_agg_units,
)
from xclim.indices import run_length

from icclim._core.climate_variable import must_run_bootstrap
from icclim._core.constants import (
    GROUP_BY_METHOD,
    GROUP_BY_REF_AND_RESAMPLE_STUDY_METHOD,
    PART_OF_A_WHOLE_UNIT,
    REFERENCE_PERIOD_ID,
    RESAMPLE_METHOD,
    UNITS_KEY,
)
from icclim._core.input_parsing import PercentileDataArray
from icclim._core.model.cf_calendar import CfCalendarRegistry
from icclim._core.model.operator import OperatorRegistry
from icclim.exception import InvalidIcclimArgumentError
from icclim.frequency import RUN_INDEXER, Frequency, FrequencyRegistry

if TYPE_CHECKING:
    from datetime import timedelta

    import numpy as np
    from pint import Quantity
    from xarray.core.groupby import DataArrayGroupBy

    from icclim._core.climate_variable import ClimateVariable
    from icclim._core.generic.threshold.percentile import PercentileThreshold
    from icclim._core.model.logical_link import LogicalLink
    from icclim._core.model.threshold import Threshold


def count_occurrences(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    logical_link: LogicalLink,
    date_event: bool,
    to_percent: bool,
    **kwargs,  # noqa: ARG001
) -> DataArray:
    """
    Count the occurrences of exceedances of the threshold(s).

    Parameters
    ----------
    climate_vars : list[ClimateVariable]
        The list of climate variables containing the data and the threshold(s).
    resample_freq : Frequency
        The time frequency of the output.
    logical_link : LogicalLink
        The logical link to apply to the exceedances if multiple thresholds are
        provided.
    date_event : bool
        Whether to return the date of the event.
    to_percent : bool
        Whether to return the result in percent.
    **kwargs : dict
        Ignored keyword arguments (for compatibility).

    Returns
    -------
    DataArray
        The count of occurrences of exceedances.
    """
    if date_event:
        reducer_op = _count_occurrences_with_date
    else:
        reducer_op = partial(DataArrayResample.sum, dim="time")
    merged_exceedances = _compute_exceedances(
        climate_vars,
        resample_freq.pandas_freq,
        logical_link,
    )
    result = reducer_op(merged_exceedances.resample(time=resample_freq.pandas_freq))
    if to_percent:
        result = _to_percent(result, resample_freq)
        result.attrs[UNITS_KEY] = "%"
        return result
    freq = check_freq(climate_vars[0].studied_data, dim="time")
    return to_agg_units(result, climate_vars[0].studied_data, "count", deffreq=freq)


def max_consecutive_occurrence(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    logical_link: LogicalLink,
    date_event: bool,
    source_freq_delta: timedelta,
    **kwargs,  # noqa: ARG001
) -> DataArray:
    """
    Calculate the maximum number of consecutive occurrences of exceedances for a given set of climate variables.

    Parameters
    ----------
    climate_vars : list[ClimateVariable]
        The list of climate variables containing the data and the threshold(s).
    resample_freq : Frequency
        The time frequency of the output.
    logical_link : LogicalLink
        The logical link to apply when merging the exceedances.
    date_event : bool
        Whether to include the dates of the exceedances in the result.
    source_freq_delta : timedelta
        The time difference between consecutive data points in the source data.
    **kwargs : dict
        Ignored keyword arguments (for compatibility).

    Returns
    -------
    DataArray
        The maximum number of consecutive occurrences of exceedances.
    """  # noqa: E501
    merged_exceedances = _compute_exceedances(
        climate_vars,
        resample_freq.pandas_freq,
        logical_link,
    )
    rle = run_length.rle(merged_exceedances, dim="time", index="first")
    resampled = rle.resample(time=resample_freq.pandas_freq)
    if date_event:
        result = _consecutive_occurrences_with_dates(resampled, source_freq_delta)
    else:
        result = resampled.max(dim="time")
    freq = check_freq(climate_vars[0].studied_data, dim="time")
    return to_agg_units(result, climate_vars[0].studied_data, "count", deffreq=freq)


def sum_of_spell_lengths(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    logical_link: LogicalLink,
    min_spell_length: int,
    **kwargs,  # noqa: ARG001
) -> DataArray:
    """
    Calculate the sum of the lengths of all spells in the data.

    This function calculates the sum of the lengths of all spells in the data,
    where a spell is defined as a consecutive occurrence of exceedances.

    Parameters
    ----------
    climate_vars : list[ClimateVariable]
        The list of climate variables containing the data and the threshold(s).
    resample_freq : Frequency
        The time frequency of the output.
    logical_link : LogicalLink
        The logical link to apply when merging the exceedances.
    min_spell_length : int
        The minimum length of a spell to consider.
    **kwargs : dict
        Ignored keyword arguments (for compatibility).

    Returns
    -------
    DataArray
        The sum of the lengths of all spells in the data.
    """
    merged_exceedances = _compute_exceedances(
        climate_vars,
        resample_freq.pandas_freq,
        logical_link,
    )
    rle = run_length.rle(merged_exceedances, dim="time", index="first")
    cropped_rle = rle.where(rle >= min_spell_length, other=0)
    result = cropped_rle.resample(time=resample_freq.pandas_freq).max(dim="time")
    freq = check_freq(climate_vars[0].studied_data, dim="time")
    return to_agg_units(result, climate_vars[0].studied_data, "count", deffreq=freq)


def excess(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    **kwargs,  # noqa: ARG001
) -> DataArray:
    """
    Compute the excess of a climate variable above a threshold using the 'reach' operator.

    Parameters
    ----------
    climate_vars : list[ClimateVariable]
        List of climate variables. Only the first variable is used.
    resample_freq : Frequency
        The time frequency of the output.
    **kwargs : dict
        Ignored keyword arguments (for compatibility).

    Returns
    -------
    DataArray
        DataArray containing the computed excess values.

    Raises
    ------
    InvalidIcclimArgumentError
        If the threshold operator is not 'reach'.

    Notes
    -----
    The excess is computed by subtracting the threshold from the climate variable data.
    Only the values above the threshold are considered, and negative values are set to
    zero.
    The resulting excess values are then summed over the specified resample frequency.
    """  # noqa: E501
    study, threshold = _get_thresholded_var(climate_vars)
    if threshold.operator != OperatorRegistry.REACH:
        msg = "Excess can only be computed with 'reach' operator."
        raise InvalidIcclimArgumentError(msg)
    excesses = threshold.compute(study, override_op=operator.sub)
    res = (
        (excesses).clip(min=0).resample(time=resample_freq.pandas_freq).sum(dim="time")
    )
    res = res.assign_attrs(units=f"delta_{res.attrs['units']}")
    freq = check_freq(study, dim="time")
    return to_agg_units(res, study, "integral", deffreq=freq)


def deficit(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    **kwargs,  # noqa: ARG001
) -> DataArray:
    """
    Compute the deficit of a climate variable below a threshold using the 'reach' operator.

    Parameters
    ----------
    climate_vars : list[ClimateVariable]
        List of climate variables. Only the first variable is used.
    resample_freq : Frequency
        The time frequency of the output.
    **kwargs : dict
        Ignored keyword arguments (for compatibility).

    Returns
    -------
    DataArray
        DataArray containing the computed deficit values.

    Notes
    -----
    The deficit is computed by subtracting the climate variable data from the threshold.
    Only the values below the threshold are considered, and negative values are set to
    zero.
    The resulting deficit values are then summed over the specified resample frequency.
    """  # noqa: E501
    study, threshold = get_single_var(climate_vars)
    deficit = threshold.compute(study, override_op=lambda da, th: th - da)
    res = deficit.clip(min=0).resample(time=resample_freq.pandas_freq).sum(dim="time")
    res = res.assign_attrs(units=f"delta_{res.attrs['units']}")
    freq = check_freq(study, dim="time")
    return to_agg_units(res, study, "integral", deffreq=freq)


def fraction_of_total(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    to_percent: bool,
    **kwargs,  # noqa: ARG001
) -> DataArray:
    """
    Calculate the fraction of total for a given set of climate variables.

    Parameters
    ----------
    climate_vars : list[ClimateVariable]
        The list of climate variables containing the data and the threshold(s).
        Only one variable is expected in the list.
    resample_freq : Frequency
        The resampling frequency.
    to_percent : bool
        Flag indicating whether to convert the result to percentage.
    **kwargs : dict
        Ignored keyword arguments (for compatibility).

    Returns
    -------
    DataArray
        The fraction of total as a DataArray.

    Notes
    -----
    This function calculates the fraction of total for a given set of climate variables.
    The fraction of total is calculated by dividing the sum of values exceeding a
    threshold by the total sum of values.

    If the `to_percent` flag is set to True, the result will be multiplied by 100 and
    the units will be set to "%". Otherwise, the units will be set to the value of
    PART_OF_A_WHOLE_UNIT, which is 1.
    """
    study, threshold = get_single_var(climate_vars)
    if threshold.threshold_min_value is not None:
        min_val = threshold.threshold_min_value
        min_val = convert_units_to(min_val, study, context="hydro")
        total = (
            study.where(threshold.operator(study, min_val))
            .resample(time=resample_freq.pandas_freq)
            .sum(dim="time")
        )
    else:
        total = study.resample(time=resample_freq.pandas_freq).sum(dim="time")
    exceedance = _compute_exceedance(
        study=study,
        threshold=threshold,
        freq=resample_freq.pandas_freq,
        bootstrap=must_run_bootstrap(study, threshold),
    ).squeeze()
    over = (
        study.where(exceedance, 0)
        .resample(time=resample_freq.pandas_freq)
        .sum(dim="time")
    )
    res = over / total
    if to_percent:
        res = res * 100
        res.attrs[UNITS_KEY] = "%"
    else:
        res.attrs[UNITS_KEY] = PART_OF_A_WHOLE_UNIT
    return res


def maximum(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    date_event: bool,
    **kwargs,  # noqa: ARG001
) -> DataArray:
    """
    Calculate the maximum value of the given climate variables.

    Parameters
    ----------
    climate_vars : list[ClimateVariable]
        List of climate variables to calculate the maximum value for.
    resample_freq : Frequency
        The frequency at which to resample the data.
    date_event : bool
        Flag indicating whether the output should include the date of the events.
    **kwargs : dict
        Ignored keyword arguments (for compatibility).

    Returns
    -------
    DataArray
        The maximum value of the climate variables.
    """
    return _run_simple_reducer(
        climate_vars=climate_vars,
        resample_freq=resample_freq,
        reducer_op=DataArrayResample.max,
        date_event=date_event,
    )


def minimum(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    date_event: bool,
    **kwargs,  # noqa: ARG001
) -> DataArray:
    """
    Calculate the minimum value of the given climate variables.

    Parameters
    ----------
    climate_vars : list[ClimateVariable]
        List of climate variables to calculate the minimum value for.
    resample_freq : Frequency
        The frequency at which to resample the data.
    date_event : bool
        Flag indicating whether the output should include the date of the events.
    **kwargs : dict
        Ignored keyword arguments (for compatibility).

    Returns
    -------
    DataArray
        The minimum value of the climate variables.
    """
    return _run_simple_reducer(
        climate_vars=climate_vars,
        resample_freq=resample_freq,
        reducer_op=DataArrayResample.min,
        date_event=date_event,
    )


def average(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    **kwargs,  # noqa: ARG001
) -> DataArray:
    """
    Compute the average of the given climate variables.

    Parameters
    ----------
    climate_vars : list[ClimateVariable]
        List of climate variables to compute the average for.
    resample_freq : Frequency
        The frequency at which to resample the data.
    **kwargs
        Ignored keyword arguments (for compatibility).

    Returns
    -------
    DataArray
        The computed average as a DataArray.

    """
    return _run_simple_reducer(
        climate_vars=climate_vars,
        resample_freq=resample_freq,
        reducer_op=DataArrayResample.mean,
        date_event=False,
    )


def generic_sum(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    **kwargs,  # noqa: ARG001
) -> DataArray:
    """
    Compute the sum of the given climate variables.

    Parameters
    ----------
    climate_vars : list[ClimateVariable]
        List of climate variables to compute the sum for.
    resample_freq : Frequency
        The frequency at which to resample the data.
    **kwargs
        Ignored keyword arguments (for compatibility).

    Returns
    -------
    DataArray
        The computed sum as a DataArray.
    """
    return _run_simple_reducer(
        climate_vars=climate_vars,
        resample_freq=resample_freq,
        reducer_op=DataArrayResample.sum,
        date_event=False,
        must_convert_rate=True,
    )


def standard_deviation(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    **kwargs,  # noqa: ARG001
) -> DataArray:
    """
    Compute the standard deviation of the given climate variables.

    This function calculates the standard deviation of the provided climate variables.
    The standard deviation is a measure of the amount of variation or dispersion in the
    data.
    It quantifies the amount of variation or spread in the values of the climate
    variables.

    Parameters
    ----------
    climate_vars : list[ClimateVariable]
        List of climate variables to compute the standard deviation for.
    resample_freq : Frequency
        The frequency at which to resample the data.
    **kwargs
        Ignored keyword arguments (for compatibility).

    Returns
    -------
    DataArray
        The computed standard deviation as a DataArray.
    """
    return _run_simple_reducer(
        climate_vars,
        resample_freq,
        DataArrayResample.std,
        date_event=False,
    )


def max_of_rolling_sum(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    rolling_window_width: int,
    date_event: bool,
    source_freq_delta: timedelta,
    **kwargs,  # noqa: ARG001
) -> DataArray:
    """
    Compute the maximum value of the rolling sum of the given climate variables.

    The rolling sum is the sum of values over a specified rolling window width.
    The maximum value is the highest value obtained from the rolling sum.

    Parameters
    ----------
    climate_vars : list[ClimateVariable]
        List of climate variables to compute the maximum value of the rolling sum for.
    resample_freq : Frequency
        The frequency at which to resample the data.
    rolling_window_width : int
        The width of the rolling window, i.e., the number of values to include in each
        rolling sum.
    date_event : bool
        A flag indicating whether the date of the events should be included in the
        output.
    source_freq_delta : timedelta
        The time difference between consecutive data points in the source data.
        For daily data this is 1 day, for monthly data this is 1 month, etc.
    **kwargs
        Ignored keyword arguments (for compatibility).

    Returns
    -------
    DataArray
        The computed maximum value of the rolling sum as a DataArray.
    """
    return _run_rolling_reducer(
        climate_vars=climate_vars,
        resample_freq=resample_freq,
        rolling_window_width=rolling_window_width,
        rolling_op=DataArrayRolling.sum,
        resampled_op=DataArrayResample.max,
        date_event=date_event,
        source_freq_delta=source_freq_delta,
    )


def min_of_rolling_sum(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    rolling_window_width: int,
    date_event: bool,
    source_freq_delta: timedelta,
    **kwargs,  # noqa: ARG001
) -> DataArray:
    """
    Compute the minimum value of the rolling sum of the given climate variables.

    The rolling sum is the sum of values over a specified rolling window width.
    The minimum value is the lowest value obtained from the rolling sum.

    Parameters
    ----------
    climate_vars : list[ClimateVariable]
        List of climate variables to compute the minimum value of the rolling sum for.
    resample_freq : Frequency
        The frequency at which to resample the data.
    rolling_window_width : int
        The width of the rolling window, i.e., the number of values to include in each
        rolling sum.
    date_event : bool
        A flag indicating whether the date of the events should be included in the
        output.
    source_freq_delta : timedelta
        The time difference between consecutive data points in the source data.
        For daily data this is 1 day, for monthly data this is 1 month, etc.
    **kwargs
        Ignored keyword arguments (for compatibility).

    Returns
    -------
    DataArray
        The computed minimum value of the rolling sum as a DataArray.
    """
    return _run_rolling_reducer(
        climate_vars=climate_vars,
        resample_freq=resample_freq,
        rolling_window_width=rolling_window_width,
        rolling_op=DataArrayRolling.sum,
        resampled_op=DataArrayResample.min,
        date_event=date_event,
        source_freq_delta=source_freq_delta,
    )


def min_of_rolling_average(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    rolling_window_width: int,
    date_event: bool,
    source_freq_delta: timedelta,
    **kwargs,  # noqa: ARG001
) -> DataArray:
    """
    Compute the minimum value of the rolling average of the given climate variables.

    The rolling average is the average of values over a specified rolling window width.
    The minimum value is the lowest value obtained from the rolling average.

    Parameters
    ----------
    climate_vars : list[ClimateVariable]
        List of climate variables to compute the minimum value of the rolling average
        for.
    resample_freq : Frequency
        The frequency at which to resample the data.
    rolling_window_width : int
        The width of the rolling window, i.e., the number of values to include in each
        rolling average.
    date_event : bool
        A flag indicating whether the date of the events should be included in the
        output.
    source_freq_delta : timedelta
        The time difference between consecutive data points in the source data.
        For daily data this is 1 day, for monthly data this is 1 month, etc.
    **kwargs
        Ignored keyword arguments (for compatibility).

    Returns
    -------
    DataArray
        The computed minimum value of the rolling average as a DataArray.
    """
    return _run_rolling_reducer(
        climate_vars=climate_vars,
        resample_freq=resample_freq,
        rolling_window_width=rolling_window_width,
        rolling_op=DataArrayRolling.mean,
        resampled_op=DataArrayResample.min,
        date_event=date_event,
        source_freq_delta=source_freq_delta,
    )


def max_of_rolling_average(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    rolling_window_width: int,
    date_event: bool,
    source_freq_delta: timedelta,
    **kwargs,  # noqa: ARG001
) -> DataArray:
    """
    Compute the minimum value of the rolling average of the given climate variables.

    The rolling average is the average of values over a specified rolling window width.
    The minimum value is the lowest value obtained from the rolling average.

    Parameters
    ----------
    climate_vars : list[ClimateVariable]
        List of climate variables to compute the minimum value of the rolling average
        for.
    resample_freq : Frequency
        The frequency at which to resample the data.
    rolling_window_width : int
        The width of the rolling window, i.e., the number of values to include in each
        rolling average.
    date_event : bool
        A flag indicating whether the date of the events should be included in the
        output.
    source_freq_delta : timedelta
        The time difference between consecutive data points in the source data.
        For daily data this is 1 day, for monthly data this is 1 month, etc.
    **kwargs
        Ignored keyword arguments (for compatibility).

    Returns
    -------
    DataArray
        The computed minimum value of the rolling average as a DataArray.
    """
    return _run_rolling_reducer(
        climate_vars=climate_vars,
        resample_freq=resample_freq,
        rolling_window_width=rolling_window_width,
        rolling_op=DataArrayRolling.mean,
        resampled_op=DataArrayResample.max,
        date_event=date_event,
        source_freq_delta=source_freq_delta,
    )


def mean_of_difference(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    **kwargs,  # noqa: ARG001
) -> DataArray:
    """
    Calculate the mean of the difference between two climate variables.

    This function calculates the mean of the difference between two climate variables
    for each time step, and then resamples the resulting data based on the specified
    frequency.
    The resulting data array will have the same units as the study variable.

    Parameters
    ----------
    climate_vars : list[ClimateVariable]
        The two climate variables necessary to compute the indicator.
    resample_freq : Frequency
        Resampling frequency of the output.
    **kwargs : dict
        Ignored keyword arguments (for compatibility).

    Returns
    -------
    DataArray
        The mean of the difference as a xarray.DataArray.

    Notes
    -----
    This is a generification of ECAD's DTR climate index.
    """
    study, ref = get_couple_of_var(climate_vars, "mean_of_difference")
    mean_of_diff = (study - ref).resample(time=resample_freq.pandas_freq).mean()
    mean_of_diff.attrs["units"] = study.attrs["units"]
    return mean_of_diff


def difference_of_extremes(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    **kwargs,  # noqa: ARG001
) -> DataArray:
    """
    Calculate the difference of extremes between two climate variables.

    Parameters
    ----------
    climate_vars : list[ClimateVariable]
        A list of climate variables.
    resample_freq : Frequency
        The frequency at which to resample the data.
    **kwargs
        Ignored keyword arguments (for compatibility).

    Returns
    -------
    DataArray
        The difference of extremes between the two climate variables.

    Notes
    -----
    This function calculates the difference of extremes between two climate variables.
    It first resamples the study variable to the specified frequency and take the
    maximum per resampled chunk.
    Then it resamples the reference variable to the same frequency and take the minimum
    per resampled chunk.
    Finally, for each chunk, it calculates the differences of theses maximum and
    minimum values.
    This is a generification of ECAD's ETR climate index.
    """
    study, ref = get_couple_of_var(climate_vars, "difference_of_extremes")
    max_study = study.resample(time=resample_freq.pandas_freq).max()
    min_ref = ref.resample(time=resample_freq.pandas_freq).min()
    diff_of_extremes = max_study - min_ref
    diff_of_extremes.attrs["units"] = study.attrs["units"]
    return diff_of_extremes


def mean_of_absolute_one_time_step_difference(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    **kwargs,  # noqa: ARG001
) -> DataArray:
    """
    Mean of the absolute one-time-step difference between two climate variables.

    This function calculates the mean of the absolute difference between two climate
    variables
    for each time step, and then resamples the resulting data based on the specified
    frequency.
    The resulting data array will have the same units as the study variable.

    Parameters
    ----------
    climate_vars : list[ClimateVariable]
        The two climate variables necessary to compute the indicator.
    resample_freq : Frequency
        Resampling frequency of the output.
    **kwargs : dict
        Ignored keyword arguments (for compatibility).

    Returns
    -------
    DataArray
        The mean of the absolute one-time-step difference as a xarray.DataArray.

    Notes
    -----
    This is a generification of ECAD's vDTR climate index.
    """
    study, ref = get_couple_of_var(
        climate_vars,
        "mean_of_absolute_one_time_step_difference",
    )
    one_time_step_diff = (study - ref).diff(dim="time")
    res = abs(one_time_step_diff).resample(time=resample_freq.pandas_freq).mean()
    res.attrs["units"] = study.attrs["units"]
    return res


def difference_of_means(
    climate_vars: list[ClimateVariable],
    to_percent: bool,
    resample_freq: Frequency,
    sampling_method: str,
    is_compared_to_reference: bool,
    **kwargs,  # noqa: ARG001
) -> DataArray:
    """
    Calculate the difference of means between two climate variables.

    Parameters
    ----------
    climate_vars : list[ClimateVariable]
        A studied climate variable and a reference climate variable.
    to_percent : bool
        If True, the result will be converted to percentage.
    resample_freq : Frequency
        Resampling frequency of the output.
    sampling_method : str
        The method used for resampling. It can be either 'group_by', 'resample', or
        'group_by_ref_and_resample_study'.
        'group_by' will group the data by the specified frequency, for example every
        data of every January together.
        'resample' will resample the data to the specified frequency, for example every
        days of each month independently together.
        'group_by_ref_and_resample_study' will group the reference data by the specified
        frequency and resample the study data to the same frequency.
        This last method allows for example to compare each January, independently, of
        the study period to every January of the reference period.
        This is typically used to compare the each month of the studied period
        to a normal (the reference) of many aggregated years.
    is_compared_to_reference : bool
        If True, check if the sampling method is 'resample' and raise an error if it is.
        It does not make sense to resample the reference variable if it is already a
        subsample of the studied variable.
    **kwargs
        Ignored keyword arguments (for compatibility).

    Returns
    -------
    DataArray
        The difference of means between the two climate variables.

    Notes
    -----
    This is a generification of the anomaly climate index.
    """
    study = climate_vars[0].studied_data
    ref = climate_vars[1].studied_data
    study = convert_units_to(study, ref, context="hydro")
    return _reduce_and_diff(
        study,
        ref,
        to_percent,
        resample_freq,
        sampling_method,
        is_compared_to_reference,
        reducer=lambda x: x.mean(dim="time"),
    )


def percentile(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    **kwargs,  # noqa: ARG001
) -> DataArray:
    """
    Calculate the percentile of the given climate variable.

    Parameters
    ----------
    climate_vars : list[ClimateVariable]
        A single climate variable within a list.
    resample_freq : Frequency
        Resampling frequency of the output.
    **kwargs
        Ignored keyword arguments (for compatibility).

    Returns
    -------
    DataArray
        The calculated percentile as a DataArray.

    Notes
    -----
    This function calculates the percentile of the given climate variables
    by resampling the data based on the provided frequency and then
    calculating the corresponding quantile using the specified interpolation method.

    The resulting DataArray contains the percentiles as the 'percentiles'
    coordinate variable.
    """
    study, threshold = get_single_var(climate_vars)
    threshold: PercentileThreshold
    quantile = threshold.initial_value[0] * 0.01
    method = threshold.interpolation.name
    result = study.resample(time=resample_freq.pandas_freq).quantile(
        quantile, method=method
    )
    result.coords["quantile"] = result.coords["quantile"] * 100
    result = result.rename(quantile="percentiles")
    return PercentileDataArray.from_da(
        source=result,
        climatology_bounds=build_climatology_bounds(study),
    )


def _reduce_and_diff(
    study: DataArray,
    ref: DataArray,
    to_percent: bool,
    resample_freq: Frequency,
    sampling_method: str,
    is_compared_to_reference: bool,
    reducer: Callable[[DataArrayResample | DataArray | DataArrayGroupBy], DataArray],
    use_reduce_unit: bool = False,
    **kwargs,  # noqa: ARG001
) -> DataArray:
    if is_compared_to_reference and sampling_method == RESAMPLE_METHOD:
        msg = (
            "It does not make sense to resample the reference variable if it is"
            " already a subsample of the studied variable. Try setting"
            f" `sampling_method='{GROUP_BY_REF_AND_RESAMPLE_STUDY_METHOD}'`"
            f" instead."
        )
        raise InvalidIcclimArgumentError(msg)
    if sampling_method == GROUP_BY_METHOD:
        if resample_freq.group_by_key == RUN_INDEXER:
            reduced_study = reducer(study)
            reduced_ref = reducer(ref)
        else:
            reduced_study = reducer(study.groupby(resample_freq.group_by_key))
            reduced_ref = reducer(ref.groupby(resample_freq.group_by_key))
    elif sampling_method == RESAMPLE_METHOD:
        reduced_study = reducer(study.resample(time=resample_freq.pandas_freq))
        reduced_ref = reducer(ref.resample(time=resample_freq.pandas_freq))
    elif sampling_method == GROUP_BY_REF_AND_RESAMPLE_STUDY_METHOD:
        if (
            resample_freq.group_by_key == RUN_INDEXER
            or resample_freq == FrequencyRegistry.YEAR
        ):
            reduced_study = reducer(study.resample(time=resample_freq.pandas_freq))
            # data is already filtered with only the indexed values.
            # Thus there is only one "group".
            reduced_ref = reducer(ref)
        else:
            return _reduce_and_diff_of_resampled_x_by_groupedby_y(
                resample_freq, to_percent, study, ref, reducer=reducer
            )
    else:
        msg = f"Unknown sampling_method: '{sampling_method}'."
        raise NotImplementedError(msg)
    diff = reduced_study - reduced_ref
    if to_percent:
        diff = diff / reduced_ref * 100
        diff.attrs[UNITS_KEY] = "%"
    elif use_reduce_unit:
        diff.attrs[UNITS_KEY] = reduced_study.attrs[UNITS_KEY]
    else:
        diff.attrs[UNITS_KEY] = study.attrs[UNITS_KEY]
    return diff


def _reduce_and_diff_of_resampled_x_by_groupedby_y(
    resample_freq: Frequency,
    to_percent: bool,
    study: DataArray,
    ref: DataArray,
    reducer: Callable[
        [DataArrayResample | DataArrayGroupBy | DataArray | ClimateVariable], DataArray
    ],
) -> DataArray:
    mean_ref = reducer(ref.groupby(resample_freq.group_by_key))
    acc = []
    if resample_freq == FrequencyRegistry.MONTH:
        key = "month"
        dt_selector = lambda x: x.time.dt.month  # noqa: E731
    elif resample_freq == FrequencyRegistry.DAY:
        key = "dayofyear"
        dt_selector = lambda x: x.time.dt.dayofyear  # noqa: E731
    else:
        msg = (
            f"Can't use {GROUP_BY_REF_AND_RESAMPLE_STUDY_METHOD}"
            f" with the frequency {resample_freq.long_name}."
        )
        raise NotImplementedError(msg)
    for label, sample in study.resample(time=resample_freq.pandas_freq):
        sample_mean = reducer(sample)
        ref_group_mean = mean_ref.sel({key: dt_selector(sample).to_numpy()[0]})
        sample_diff_of_means = sample_mean - ref_group_mean
        if to_percent:
            sample_diff_of_means = sample_diff_of_means / ref_group_mean * 100
        del sample_diff_of_means[key]
        sample_diff_of_means = sample_diff_of_means.expand_dims(time=[label])
        acc.append(sample_diff_of_means)
    diff_of_means = xr.concat(acc, dim="time")
    if to_percent:
        diff_of_means.attrs["units"] = "%"
    else:
        diff_of_means.attrs["units"] = study.attrs["units"]
    return diff_of_means


def _compute_exceedance(
    study: DataArray,
    threshold: Threshold,
    freq: str,  # used by @percentile_bootstrap (don't rename, it breaks bootstrap)
    bootstrap: bool,  # used by @percentile_bootstrap
) -> DataArray:
    exceedances = threshold.compute(study, freq=freq, bootstrap=bootstrap)
    if bootstrap:
        exceedances.attrs[REFERENCE_PERIOD_ID] = threshold.value.attrs[
            "climatology_bounds"
        ]
    return exceedances


def get_couple_of_var(
    climate_vars: list[ClimateVariable],
    indicator: str,
) -> tuple[DataArray, DataArray]:
    """
    Get exactly two climate variables to compute a climate indicator.

    Parameters
    ----------
    climate_vars : list[ClimateVariable]
        A list of climate variables.
    indicator : str
        The name of the indicator to be computed.

    Returns
    -------
    tuple[DataArray, DataArray]
        A tuple containing two DataArray objects representing the study variable and
        the reference variable.

    Raises
    ------
    InvalidIcclimArgumentError
        If the number of climate variables is not equal to 2.
        If any of the two variable has a threshold.

    Notes
    -----
    This function is used to extract a couple of climate variables needed for computing
    an indicator.
    The function checks the number of climate variables and raises an error
    if it is not equal to 2 or if thresholds are present.
    """
    if len(climate_vars) != 2:
        msg = (
            f"{indicator} needs two variables **or** one variable and a "
            f"`base_period_time_range` period to extract a reference variable."
        )
        raise InvalidIcclimArgumentError(msg)
    if climate_vars[0].threshold or climate_vars[1].threshold:
        msg = f"{indicator} cannot be computed with thresholds."
        raise InvalidIcclimArgumentError(msg)
    study = climate_vars[0].studied_data
    ref = climate_vars[1].studied_data
    study = convert_units_to(study, ref, context="hydro")
    return study, ref


def _run_rolling_reducer(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    rolling_window_width: int,
    rolling_op: Callable[[DataArrayRolling], DataArray],  # sum | mean
    resampled_op: Callable[[DataArrayResample], DataArray],  # max | min
    date_event: bool,
    source_freq_delta: timedelta,
) -> DataArray:
    study, threshold = get_single_var(climate_vars)
    if threshold:
        exceedance = _compute_exceedance(
            study=study,
            freq=resample_freq.pandas_freq,
            threshold=threshold,
            bootstrap=must_run_bootstrap(study, threshold),
        ).squeeze()
        study = study.where(exceedance)
    study = rolling_op(study.rolling(time=rolling_window_width))
    study = study.resample(time=resample_freq.pandas_freq)
    if date_event:
        return _reduce_with_date_event(
            resampled=study,
            reducer=resampled_op,
            window=rolling_window_width,
            source_delta=source_freq_delta,
        )
    return resampled_op(study, dim="time")


def _run_simple_reducer(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    reducer_op: Callable[..., DataArray],
    date_event: bool,
    must_convert_rate: bool = False,
) -> DataArray:
    """
    Apply a simple reducer operation on climate variables.

    Parameters
    ----------
    climate_vars : list[ClimateVariable]
        List of climate variables to be processed.
    resample_freq : Frequency
        Frequency at which the data should be resampled.
    reducer_op : Callable[..., DataArray]
        Reducer operation to be applied on the data.
    date_event : bool
        Flag indicating whether the date when the event occurred should be added
        as a coordinate variable.
        Only works for `max` and `min` reducers.
        Defaults to False.
    must_convert_rate : bool, optional
        Flag indicating whether the data should be converted from rate to amount.
        Defaults to False.

    Returns
    -------
    DataArray
        Result of the reducer operation applied on the climate variables.
    """
    study, threshold = get_single_var(climate_vars)
    if threshold is not None:
        exceedance = _compute_exceedance(
            study=study,
            freq=resample_freq.pandas_freq,
            threshold=threshold,
            bootstrap=must_run_bootstrap(study, threshold),
        ).squeeze()
        filtered_study = study.where(exceedance)
    else:
        filtered_study = study
    if must_convert_rate and _is_rate(filtered_study):
        filtered_study = rate2amount(filtered_study)
    if date_event:
        return _reduce_with_date_event(
            resampled=filtered_study.resample(time=resample_freq.pandas_freq),
            reducer=reducer_op,
        )
    return reducer_op(
        filtered_study.resample(time=resample_freq.pandas_freq),
        dim="time",
    )


def get_single_var(
    climate_vars: list[ClimateVariable],
) -> tuple[DataArray, Threshold | None]:
    """
    Get the single variable and its threshold (if available).

    Parameters
    ----------
    climate_vars : list[ClimateVariable]
        A list of ClimateVariable objects.

    Returns
    -------
    tuple[DataArray, Threshold | None]
        A tuple containing the single variable's data array and its threshold
        (if available).
    """
    if climate_vars[0].threshold:
        return (
            climate_vars[0].studied_data,
            climate_vars[0].threshold,
        )
    return climate_vars[0].studied_data, None


def _compute_exceedances(
    climate_vars: list[ClimateVariable],
    resample_freq: str,
    logical_link: LogicalLink,
) -> DataArray:
    exceedances = [
        _compute_exceedance(
            study=climate_var.studied_data,
            threshold=climate_var.threshold,
            freq=resample_freq,
            bootstrap=must_run_bootstrap(
                climate_var.studied_data,
                climate_var.threshold,
            ),
        ).squeeze()
        for climate_var in climate_vars
    ]
    return logical_link(exceedances)


def _get_thresholded_var(
    climate_vars: list[ClimateVariable],
) -> tuple[DataArray, Threshold]:
    if climate_vars[0].threshold:
        return (
            climate_vars[0].studied_data,
            climate_vars[0].threshold,
        )
    msg = "No threshold found"
    raise InvalidIcclimArgumentError(msg)


def _reduce_with_date_event(
    resampled: DataArrayResample,
    reducer: Callable[[DataArrayResample], DataArray],
    source_delta: timedelta | None = None,
    window: int | None = None,
) -> DataArray:
    acc: list[DataArray] = []
    if reducer == DataArrayResample.max:
        group_reducer = DataArray.argmax
    elif reducer == DataArrayResample.min:
        group_reducer = DataArray.argmin
    else:
        msg = f"Can't compute `date_event` due to unknown reducer: '{reducer}'"
        raise NotImplementedError(msg)
    for label, sample in resampled:
        reduced_result = sample.isel(time=group_reducer(sample, dim="time"))
        if window is not None:
            result = _add_date_coords(
                original_sample=sample,
                result=sample.sum(dim="time"),
                start_time=reduced_result.time,
                end_time=reduced_result.time + window * source_delta,
                label=label,
            )
        else:
            result = _add_date_coords(
                original_sample=sample,
                result=sample.sum(dim="time"),
                event_date=reduced_result.time,
                label=label,
            )
        acc.append(result)
    return xr.concat(acc, "time")


def _count_occurrences_with_date(resampled: DataArrayResample) -> DataArray:
    acc: list[DataArray] = []
    for label, _sample in resampled:
        # TODO @bzah: probably not safe to compute on huge dataset,
        #              it should be fixed with
        #  https://github.com/pydata/xarray/issues/2511
        sample = _sample.compute()
        first = sample.isel(time=sample.argmax("time")).time
        reversed_time = sample.reindex(time=list(reversed(sample.time.to_numpy())))
        last = reversed_time.isel(time=reversed_time.argmax("time")).time
        dated_occurrences = _add_date_coords(
            original_sample=sample,
            result=sample.sum(dim="time"),
            start_time=first,
            end_time=last,
            label=label,
        )
        acc.append(dated_occurrences)
    return xr.concat(acc, "time")


def _consecutive_occurrences_with_dates(
    resampled: DataArrayResample,
    source_freq_delta: timedelta,
) -> DataArray:
    acc = []
    for label, _sample in resampled:
        sample = _sample.where(~_sample.isnull(), 0)
        time_index_of_max_rle = sample.argmax(dim="time")
        # TODO @bzah: `.compute` is needed until xarray merges this pr:
        # https://github.com/pydata/xarray/pull/5873
        time_index_of_max_rle = time_index_of_max_rle.compute()
        dated_longest_run = sample[{"time": time_index_of_max_rle}]
        start_time = sample.isel(
            time=time_index_of_max_rle.where(time_index_of_max_rle > 0, 0),
        ).time
        end_time = start_time + (dated_longest_run * source_freq_delta)
        dated_longest_run = _add_date_coords(
            original_sample=sample,
            result=dated_longest_run,
            start_time=start_time,
            end_time=end_time,
            label=label,
        )
        acc.append(dated_longest_run)
    return xr.concat(acc, "time")


def _add_date_coords(
    original_sample: DataArray,
    result: DataArray,
    label: str | np.datetime64,
    start_time: DataArray = None,
    end_time: DataArray = None,
    event_date: DataArray = None,
) -> DataArray:
    new_coords = {c: original_sample[c] for c in original_sample.coords if c != "time"}
    if event_date is None:
        new_coords["event_date_start"] = start_time
        new_coords["event_date_end"] = end_time
    else:
        new_coords["event_date"] = event_date
    new_coords["time"] = label
    return DataArray(data=result, coords=new_coords)


def _to_percent(da: DataArray, sampling_freq: Frequency) -> DataArray:
    if sampling_freq == FrequencyRegistry.MONTH:
        da = da / da.time.dt.daysinmonth * 100
    elif sampling_freq == FrequencyRegistry.YEAR:
        coef = xr.full_like(da, 1)
        leap_years = _is_leap_year(da)
        coef[{"time": leap_years}] = 366
        coef[{"time": ~leap_years}] = 365
        da = da / coef
    elif sampling_freq == FrequencyRegistry.AMJJAS:
        da = da / 183
    elif sampling_freq == FrequencyRegistry.ONDJFM:
        coef = xr.full_like(da, 1)
        leap_years = _is_leap_year(da)
        coef[{"time": leap_years}] = 183
        coef[{"time": ~leap_years}] = 182
        da = da / coef
    elif sampling_freq == FrequencyRegistry.DJF:
        coef = xr.full_like(da, 1)
        leap_years = _is_leap_year(da)
        coef[{"time": leap_years}] = 91
        coef[{"time": ~leap_years}] = 90
        da = da / coef
    elif sampling_freq in [FrequencyRegistry.MAM, FrequencyRegistry.JJA]:
        da = da / 92
    elif sampling_freq == FrequencyRegistry.SON:
        da = da / 91
    else:
        # TODO @bzah: improve this for custom resampling
        # https://github.com/cerfacs-globc/icclim/issues/289
        warn(
            "For now, '%' unit can only be used when `slice_mode` is one of: "
            "{MONTH, YEAR, AMJJAS, ONDJFM, DJF, MAM, JJA, SON}.",
            stacklevel=2,
        )
        return da
    da.attrs[UNITS_KEY] = PART_OF_A_WHOLE_UNIT
    return da


def _is_leap_year(da: DataArray) -> np.ndarray:
    time_index = da.indexes.get("time")
    if isinstance(time_index, xr.CFTimeIndex):
        return CfCalendarRegistry.lookup(time_index.calendar).is_leap(da.time.dt.year)
    return da.time.dt.is_leap_year


def _is_rate(query: Quantity | DataArray) -> bool:
    if isinstance(query, DataArray):
        query = str2pint(query.attrs[UNITS_KEY])
    return query.dimensionality.get("[time]", None) == -1


def check_freq(da, dim: str = "time", strict: bool = True):
    """
    Infer the sampling frequency of a DataArray along a given dimension.

    For daily climate data, always returns "D", even after seasonal slicing
    (which can break pandas' infer_freq). Falls back to pandas.infer_freq
    if not daily.
    """
    times = da[dim].values
    if len(times) < 2:
        return None

    # Compute deltas
    try:
        deltas = to_timedelta(np_diff(times))
    except Exception as e:
        if strict:
            raise ValueError(f"[icclim] Cannot compute time deltas: {e}")
        return None

    median_delta = Timedelta(np_median(deltas))

    # If ~daily, force "D"
    if np_abs(median_delta / Timedelta("1D") - 1) < 1e-6:
        return "D"

    # Otherwise, try pandas inference
    try:
        return infer_freq(
            date_range(start=times[0], periods=len(times), freq=median_delta)
        )
    except Exception as e:
        if strict:
            raise ValueError(f"[icclim] Unable to infer frequency: {e}")
        return None
