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
import os
import warnings
from collections.abc import Callable
from copy import copy
from dataclasses import replace
from functools import partial
from time import perf_counter
from typing import TYPE_CHECKING, Any, cast

import numpy as np
import xarray as xr
from numpy import abs as np_abs
from numpy import diff as np_diff
from numpy import median as np_median
from pandas import Timedelta, date_range, infer_freq, to_timedelta
from xarray import DataArray
from xarray.core.resample import DataArrayResample

# xclim imports are deferred to avoid triggering fire module load (and numba cache errors) on import.
from icclim._core.climate_variable import must_run_bootstrap
from icclim._core.constants import (
    EXPECTED_RANGE_LEN,
    FREQ_DELTA_TOLERANCE,
    GROUP_BY_METHOD,
    GROUP_BY_REF_AND_RESAMPLE_STUDY_METHOD,
    PART_OF_A_WHOLE_UNIT,
    REFERENCE_PERIOD_ID,
    RESAMPLE_METHOD,
    UNITS_KEY,
)
from icclim._core.generic.bootstrap_capability import (
    BootstrapCapability,
    BootstrapExecutionKind,
    classify_doy_percentile_count_bootstrap,
    classify_doy_percentile_mask_bootstrap,
    classify_doy_percentile_spell_bootstrap,
    classify_generic_indicator_bootstrap,
    get_optimized_scalar_bounded_bootstrap_spec,
)
from icclim._core.input_parsing import PercentileDataArray
from icclim._core.model.cf_calendar import CfCalendarRegistry
from icclim._core.model.operator import Operator, OperatorRegistry
from icclim._core.xclim_compat import get_xclim_compute
from icclim.exception import InvalidIcclimArgumentError
from icclim.frequency import (
    RUN_INDEXER,
    Frequency,
    FrequencyRegistry,
    _build_resampled_time_bounds,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from datetime import timedelta

    from pint import Quantity
    from xarray.computation.rolling import DataArrayRolling
    from xarray.core.groupby import DataArrayGroupBy

    from icclim._core.climate_variable import ClimateVariable
    from icclim._core.generic.bootstrap_primitives import BootstrapPreparedInputs
    from icclim._core.generic.threshold.percentile import PercentileThreshold
    from icclim._core.model.logical_link import LogicalLink
    from icclim._core.model.threshold import Threshold


_BOOTSTRAP_PROFILE: dict[str, float | int | str] = {}
_DEFAULT_BOOTSTRAP_SAFE_TILE_MEMORY = "2GB"
_DEFAULT_BOOTSTRAP_FAST_TILE_MEMORY = "2GB"
_BOOTSTRAP_SAFE_MEMORY_FACTOR = 12
_BOOTSTRAP_FAST_MEMORY_FACTOR = 4


def _force_reference_cftime_spell_masks(
    climate_vars: list[ClimateVariable],
) -> bool:
    return os.environ.get("ICCLIM_BOOTSTRAP_MODE") != "safe" and any(
        hasattr(climate_var.studied_data.indexes.get("time"), "calendar")
        for climate_var in climate_vars
    )


def _get_scalar_bounded_bootstrap_spec(
    threshold: Threshold | None,
) -> tuple[PercentileThreshold, float, int, int] | None:
    scalar_bounded_spec = get_optimized_scalar_bounded_bootstrap_spec(threshold)
    if scalar_bounded_spec is None:
        return None
    percentile_threshold, basic_threshold, logical_link = scalar_bounded_spec
    operator_code = _bootstrap_operator_code(basic_threshold.operator)
    if operator_code < 0:
        return None
    logical_link_code = _bootstrap_logical_link_code(logical_link.name)
    if logical_link_code < 0:
        return None
    return (
        percentile_threshold,
        float(basic_threshold.value.item()),
        operator_code,
        logical_link_code,
    )


def _bootstrap_operator_code(operator: Operator | str) -> int:
    operand = operator.operand if isinstance(operator, Operator) else str(operator)
    return {">": 0, ">=": 1, "<": 2, "<=": 3}.get(operand, -1)


def _bootstrap_logical_link_code(logical_link: str) -> int:
    return {"and": 0, "or": 1}.get(logical_link.lower(), -1)


def reset_bootstrap_profile() -> None:
    _BOOTSTRAP_PROFILE.clear()


def get_bootstrap_profile() -> dict[str, float | int | str]:
    return dict(_BOOTSTRAP_PROFILE)


def _profile_bootstrap_add(name: str, seconds: float) -> None:
    _BOOTSTRAP_PROFILE[name] = float(_BOOTSTRAP_PROFILE.get(name, 0.0)) + seconds


def _profile_bootstrap_inc(name: str, count: int = 1) -> None:
    _BOOTSTRAP_PROFILE[name] = int(_BOOTSTRAP_PROFILE.get(name, 0)) + count


def _profile_bootstrap_set(name: str, value: float) -> None:
    _BOOTSTRAP_PROFILE[name] = value


def _profile_bootstrap_note(name: str, value: str) -> None:
    _BOOTSTRAP_PROFILE[name] = value


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

    Examples
    --------
    Count days per year when temperature exceeds 25 °C:

    >>> import numpy as np
    >>> import pandas as pd
    >>> import xarray as xr
    >>> import icclim
    >>> time = pd.date_range("2000-01-01", periods=365, freq="D")
    >>> tas = xr.DataArray(
    ...     np.full(365, 303.15),
    ...     coords={"time": time},
    ...     dims=["time"],
    ...     attrs={"units": "K"},
    ... )
    >>> result = icclim.count_occurrences(
    ...     in_files=tas, var_name="tas", threshold="> 25 degC"
    ... )
    >>> int(result.count_occurrences.isel(time=0).values)
    365
    """
    _note_generic_bootstrap_capability(
        indicator_name="count_occurrences",
        climate_vars=climate_vars,
        resample_freq=resample_freq,
        date_event=date_event,
    )
    if len(climate_vars) == 1 and not date_event:
        study, threshold = get_single_var(climate_vars)
        bounded_spec = _get_scalar_bounded_bootstrap_spec(threshold)
        if bounded_spec is not None:
            (
                percentile_threshold,
                scalar_bound,
                scalar_op_code,
                logical_link_code,
            ) = bounded_spec
            optimized_bounded_count = (
                _compute_fast_tiled_scalar_bounded_bootstrap_count(
                    climate_vars[0],
                    percentile_threshold,
                    resample_freq,
                    scalar_bound,
                    scalar_op_code,
                    logical_link_code,
                    _get_fast_bootstrap_max_cells(study),
                )
            )
            if optimized_bounded_count is not None:
                if to_percent:
                    optimized_bounded_count = _to_percent(
                        optimized_bounded_count, resample_freq
                    )
                    optimized_bounded_count.attrs[UNITS_KEY] = "%"
                    return optimized_bounded_count
                freq = check_freq(climate_vars[0].studied_data, dim="time")
                return _safe_to_agg_units(
                    optimized_bounded_count,
                    climate_vars[0].studied_data,
                    "count",
                    deffreq=freq,
                )
    if len(climate_vars) == 1 and not date_event:
        safe_bootstrapped = _compute_safe_tiled_count_occurrences(
            climate_vars[0],
            resample_freq,
        )
        if safe_bootstrapped is not None:
            if to_percent:
                safe_bootstrapped = _to_percent(safe_bootstrapped, resample_freq)
                safe_bootstrapped.attrs[UNITS_KEY] = "%"
                return safe_bootstrapped
            freq = check_freq(climate_vars[0].studied_data, dim="time")
            return _safe_to_agg_units(
                safe_bootstrapped,
                climate_vars[0].studied_data,
                "count",
                deffreq=freq,
            )

    if date_event:
        reducer_op = _count_occurrences_with_date
    else:
        reducer_op = partial(DataArrayResample.sum, dim="time")
    combined_exceedance_mask = _compute_combined_exceedance_mask(
        climate_vars,
        resample_freq,
        logical_link,
    )
    result = reducer_op(
        combined_exceedance_mask.resample(time=resample_freq.pandas_freq)
    )
    if to_percent:
        result = _to_percent(result, resample_freq)
        result.attrs[UNITS_KEY] = "%"
        return result
    freq = check_freq(climate_vars[0].studied_data, dim="time")
    return _safe_to_agg_units(
        result, climate_vars[0].studied_data, "count", deffreq=freq
    )


def _run_length_encoding(
    mask: DataArray,
    resample_freq: Frequency,
    run_index: str,
    *,
    split_at_period_boundary: bool,
) -> DataArray:
    """
    Run length encode a boolean mask along time.

    By default the encoding runs on the whole series: a run that crosses the end of
    an output period is encoded once, at its first (or last, see ``run_index``) day,
    and is therefore attributed whole to a single period.
    With ``split_at_period_boundary`` the encoding restarts at the beginning of each
    output period, so a run is cut at the boundaries.
    The dimension order is the one of the default encoding in both cases, whatever
    order the installed xclim produces (it differs between xclim versions).
    """
    run_length = get_xclim_compute().run_length
    if not split_at_period_boundary:
        return run_length.rle(mask, dim="time", index=run_index)
    rle = mask.resample(time=resample_freq.pandas_freq).map(
        run_length.rle, dim="time", index=run_index
    )
    # Encoding two time steps gives the dimension order of the default path without
    # computing anything on the whole series (one step fails on Dask arrays with
    # recent xclim versions).
    default_dims = run_length.rle(
        mask.isel(time=slice(0, 2)), dim="time", index=run_index
    ).dims
    return rle.assign_coords(time=mask.time).transpose(*default_dims)


def max_consecutive_occurrence(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    logical_link: LogicalLink,
    date_event: bool,
    source_freq_delta: timedelta,
    **kwargs,
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
        ``run_index`` ("last" by default since icclim 7.4.0, or "first") selects the end of a run to
        which its whole length is attributed.
        ``split_runs_at_period_boundary`` (False by default): when True, runs are cut
        at the boundary of every output period instead of being attributed whole to
        the period where they start (or end).
        Other keyword arguments are ignored (for compatibility).

    Returns
    -------
    DataArray
        The maximum number of consecutive occurrences of exceedances.
        With ``run_index`` "first" or "last", a run is counted whole in the period
        where it starts or ends, so a value can exceed the length of its period. A
        period without any event is 0. A period that is wholly traversed by one
        continuous run attributed to another period is not reported: its value is
        NaN. With ``split_runs_at_period_boundary=True`` every period has a value.

    Examples
    --------
    Longest dry spell (consecutive days with pr < 1 mm/day), equivalent to CDD:

    >>> import numpy as np
    >>> import pandas as pd
    >>> import xarray as xr
    >>> import icclim
    >>> time = pd.date_range("2000-01-01", periods=365, freq="D")
    >>> # Dry every day
    >>> pr = xr.DataArray(
    ...     np.zeros(365),
    ...     coords={"time": time},
    ...     dims=["time"],
    ...     attrs={"units": "mm/day"},
    ... )
    >>> result = icclim.max_consecutive_occurrence(
    ...     in_files=pr, var_name="pr", threshold="< 1 mm/day", run_index="last"
    ... )
    >>> int(result.max_consecutive_occurrence.isel(time=0).values)
    365
    """
    bootstrap_capability = _note_generic_bootstrap_capability(
        indicator_name="max_consecutive_occurrence",
        climate_vars=climate_vars,
        resample_freq=resample_freq,
        date_event=date_event,
    )
    bootstrap_spell_mask = None
    if len(climate_vars) == 1 and not date_event:
        bootstrap_spell_mask = _compute_bootstrap_spell_mask(
            climate_vars[0],
            resample_freq,
            bootstrap_capability=bootstrap_capability,
        )
    if (
        bootstrap_spell_mask is None
        and not date_event
        and (
            bootstrap_capability.uses_optimized_bootstrap
            or bootstrap_capability.uses_exact_tiled_bootstrap
        )
    ):
        if bootstrap_capability.reason_code == (
            "optimized_compound_spell_bootstrap_supported"
        ):
            bootstrap_spell_mask = _compute_eager_tiled_cftime_compound_mask(
                climate_vars,
                resample_freq,
                logical_link,
            )
    if (
        bootstrap_spell_mask is None
        and not date_event
        and (
            bootstrap_capability.uses_optimized_bootstrap
            or bootstrap_capability.uses_exact_tiled_bootstrap
        )
    ):
        bootstrap_spell_mask = _compute_combined_exceedance_mask(
            climate_vars,
            resample_freq,
            logical_link,
        )
    run_index = kwargs.get("run_index", "last")
    split_runs = bool(kwargs.get("split_runs_at_period_boundary", False))
    if bootstrap_spell_mask is not None:
        spell_run_lengths = _run_length_encoding(
            bootstrap_spell_mask,
            resample_freq,
            run_index,
            split_at_period_boundary=split_runs,
        )
        result = spell_run_lengths.resample(time=resample_freq.pandas_freq).max(
            dim="time"
        )
        result = _transpose_like_study(result, climate_vars[0].studied_data)
        freq = check_freq(climate_vars[0].studied_data, dim="time")
        return _safe_to_agg_units(
            result,
            climate_vars[0].studied_data,
            "count",
            deffreq=freq,
        )
    combined_exceedance_mask = _compute_combined_exceedance_mask(
        climate_vars,
        resample_freq,
        logical_link,
        force_reference_bootstrap=_force_reference_cftime_spell_masks(climate_vars),
    )
    rle = _run_length_encoding(
        combined_exceedance_mask,
        resample_freq,
        run_index,
        split_at_period_boundary=split_runs,
    )
    resampled = rle.resample(time=resample_freq.pandas_freq)
    if date_event:
        result = _consecutive_occurrences_with_dates(
            resampled, source_freq_delta, run_index
        )
    else:
        # Results without dates follow the dimension order of the input. Dated
        # results keep ``time`` first, whatever the order of the input.
        result = _transpose_like_study(
            resampled.max(dim="time"), climate_vars[0].studied_data
        )
    freq = check_freq(climate_vars[0].studied_data, dim="time")
    return _safe_to_agg_units(
        result, climate_vars[0].studied_data, "count", deffreq=freq
    )


def sum_of_spell_lengths(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    logical_link: LogicalLink,
    min_spell_length: int,
    **kwargs,
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
        ``run_index`` ("first" by default) selects the end of a run where it is
        counted. ``split_runs_at_period_boundary`` (False by default): when True,
        runs are cut at every output period boundary first, and only the pieces of at
        least ``min_spell_length`` days are kept.

    Returns
    -------
    DataArray
        The sum of the lengths of all spells in the data.
    """
    split_runs = bool(kwargs.get("split_runs_at_period_boundary", False))
    bootstrap_capability = _note_generic_bootstrap_capability(
        indicator_name="sum_of_spell_lengths",
        climate_vars=climate_vars,
        resample_freq=resample_freq,
    )
    bootstrap_spell_mask = None
    if len(climate_vars) == 1:
        bootstrap_spell_mask = _compute_bootstrap_spell_mask(
            climate_vars[0],
            resample_freq,
            bootstrap_capability=bootstrap_capability,
        )
    if bootstrap_spell_mask is None and (
        bootstrap_capability.uses_optimized_bootstrap
        or bootstrap_capability.uses_exact_tiled_bootstrap
    ):
        if bootstrap_capability.reason_code == (
            "optimized_compound_spell_bootstrap_supported"
        ):
            bootstrap_spell_mask = _compute_eager_tiled_cftime_compound_mask(
                climate_vars,
                resample_freq,
                logical_link,
            )
    if bootstrap_spell_mask is None and (
        bootstrap_capability.uses_optimized_bootstrap
        or bootstrap_capability.uses_exact_tiled_bootstrap
    ):
        bootstrap_spell_mask = _compute_combined_exceedance_mask(
            climate_vars,
            resample_freq,
            logical_link,
        )
    if bootstrap_spell_mask is not None:
        spell_run_lengths = _run_length_encoding(
            bootstrap_spell_mask,
            resample_freq,
            kwargs.get("run_index", "first"),
            split_at_period_boundary=split_runs,
        )
        cropped_run_lengths = spell_run_lengths.where(
            spell_run_lengths >= min_spell_length,
            other=0,
        )
        result = cropped_run_lengths.resample(time=resample_freq.pandas_freq).sum(
            dim="time"
        )
        result = _transpose_like_study(result, climate_vars[0].studied_data)
        freq = check_freq(climate_vars[0].studied_data, dim="time")
        return _safe_to_agg_units(
            result,
            climate_vars[0].studied_data,
            "count",
            deffreq=freq,
        )
    combined_exceedance_mask = _compute_combined_exceedance_mask(
        climate_vars,
        resample_freq,
        logical_link,
        force_reference_bootstrap=_force_reference_cftime_spell_masks(climate_vars),
    )
    rle = _run_length_encoding(
        combined_exceedance_mask,
        resample_freq,
        kwargs.get("run_index", "first"),
        split_at_period_boundary=split_runs,
    )
    cropped_rle = rle.where(rle >= min_spell_length, other=0)
    result = cropped_rle.resample(time=resample_freq.pandas_freq).sum(dim="time")
    if split_runs:
        result = _transpose_like_study(result, climate_vars[0].studied_data)
    freq = check_freq(climate_vars[0].studied_data, dim="time")
    return _safe_to_agg_units(
        result, climate_vars[0].studied_data, "count", deffreq=freq
    )


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
    """
    bootstrap_capability = _note_generic_bootstrap_capability(
        indicator_name="excess",
        climate_vars=climate_vars,
        resample_freq=resample_freq,
    )
    study, threshold = _get_thresholded_var(climate_vars)
    if threshold.operator != OperatorRegistry.REACH:
        msg = "Excess can only be computed with 'reach' operator."
        raise InvalidIcclimArgumentError(msg)
    from icclim._core.generic.threshold.percentile import (  # noqa: PLC0415
        PercentileThreshold,
    )

    mean_threshold = None
    if bootstrap_capability.uses_optimized_bootstrap and isinstance(
        threshold, PercentileThreshold
    ):
        mean_threshold = _compute_fast_tiled_bootstrap_mean_threshold(
            climate_vars[0],
            threshold,
            resample_freq,
            _get_fast_bootstrap_max_cells(study),
        )
    excesses = (
        study - mean_threshold
        if mean_threshold is not None
        else threshold.compute(
            study,
            override_op=operator.sub,
            freq=resample_freq.pandas_freq,
            bootstrap=must_run_bootstrap(
                study,
                threshold,
                climate_vars[0].bootstrap,
            ),
        )
    )
    res = (
        (excesses).clip(min=0).resample(time=resample_freq.pandas_freq).sum(dim="time")
    )
    # The units come from the study: recent xarray versions drop the conflicting
    # attributes of a subtraction ("mm/day" and "mm d-1" are different texts).
    res = res.assign_attrs(units=f"delta_{study.attrs['units']}")
    freq = check_freq(study, dim="time")
    return _safe_to_agg_units(res, study, "integral", deffreq=freq)


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
    """
    bootstrap_capability = _note_generic_bootstrap_capability(
        indicator_name="deficit",
        climate_vars=climate_vars,
        resample_freq=resample_freq,
    )
    study, threshold = get_single_var(climate_vars)
    if threshold is None:
        msg = "No threshold found"
        raise InvalidIcclimArgumentError(msg)
    from icclim._core.generic.threshold.percentile import (  # noqa: PLC0415
        PercentileThreshold,
    )

    mean_threshold = None
    if bootstrap_capability.uses_optimized_bootstrap and isinstance(
        threshold, PercentileThreshold
    ):
        mean_threshold = _compute_fast_tiled_bootstrap_mean_threshold(
            climate_vars[0],
            threshold,
            resample_freq,
            _get_fast_bootstrap_max_cells(study),
        )
    if mean_threshold is not None:
        deficit = (mean_threshold - study).transpose(
            *(dim for dim in study.dims if dim != "time"),
            "time",
            "percentiles",
        )
    else:
        deficit = threshold.compute(
            study,
            override_op=lambda da, th: th - da,
            freq=resample_freq.pandas_freq,
            bootstrap=must_run_bootstrap(
                study,
                threshold,
                climate_vars[0].bootstrap,
            ),
        )
    res = deficit.clip(min=0).resample(time=resample_freq.pandas_freq).sum(dim="time")
    # The units come from the study: recent xarray versions drop the conflicting
    # attributes of a subtraction ("mm/day" and "mm d-1" are different texts).
    res = res.assign_attrs(units=f"delta_{study.attrs['units']}")
    freq = check_freq(study, dim="time")
    return _safe_to_agg_units(res, study, "integral", deffreq=freq)


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
    bootstrap_capability = _note_generic_bootstrap_capability(
        indicator_name="fraction_of_total",
        climate_vars=climate_vars,
        resample_freq=resample_freq,
    )
    study, threshold = get_single_var(climate_vars)
    if threshold is None:
        msg = "No threshold found"
        raise InvalidIcclimArgumentError(msg)

    optimized_fraction = _compute_optimized_fraction_of_total(
        climate_var=climate_vars[0],
        threshold=threshold,
        study=study,
        resample_freq=resample_freq,
        bootstrap_capability=bootstrap_capability,
    )
    if optimized_fraction is not None:
        return _format_fraction_of_total_result(
            optimized_fraction,
            to_percent=to_percent,
        )
    study = _materialize_study_for_optimized_compound_value_aggregate(
        study=study,
        threshold=threshold,
        bootstrap_capability=bootstrap_capability,
    )
    if threshold.threshold_min_value is not None:
        total = _sum_values_at_or_above_threshold_floor(
            study,
            threshold,
            resample_freq,
        )
    else:
        total = study.resample(time=resample_freq.pandas_freq).sum(dim="time")
    stabilized_climate_var = (
        replace(climate_vars[0], studied_data=study)
        if study is not climate_vars[0].studied_data
        else climate_vars[0]
    )
    exceedance_mask = _compute_threshold_exceedance_mask(
        climate_var=stabilized_climate_var,
        threshold=threshold,
        resample_freq=resample_freq,
        prepared_inputs_cache={},
    ).squeeze()
    over = (
        study.where(exceedance_mask, 0)
        .resample(time=resample_freq.pandas_freq)
        .sum(dim="time")
    )
    res = over / total
    return _format_fraction_of_total_result(res, to_percent=to_percent)


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

    Examples
    --------
    Annual maximum of a linearly increasing temperature series:

    >>> import numpy as np
    >>> import pandas as pd
    >>> import xarray as xr
    >>> import icclim
    >>> time = pd.date_range("2000-01-01", periods=365, freq="D")
    >>> tas = xr.DataArray(
    ...     np.arange(365, dtype=float) + 273.15,
    ...     coords={"time": time},
    ...     dims=["time"],
    ...     attrs={"units": "K"},
    ... )
    >>> result = icclim.maximum(in_files=tas, var_name="tas")
    >>> round(float(result.maximum.isel(time=0).values), 2)
    364.0
    """
    _note_generic_bootstrap_capability(
        indicator_name="maximum",
        climate_vars=climate_vars,
        resample_freq=resample_freq,
        date_event=date_event,
    )
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

    Examples
    --------
    Annual minimum of a constant 0 °C series:

    >>> import numpy as np
    >>> import pandas as pd
    >>> import xarray as xr
    >>> import icclim
    >>> time = pd.date_range("2000-01-01", periods=365, freq="D")
    >>> tas = xr.DataArray(
    ...     np.zeros(365) + 273.15,
    ...     coords={"time": time},
    ...     dims=["time"],
    ...     attrs={"units": "K"},
    ... )
    >>> result = icclim.minimum(in_files=tas, var_name="tas")
    >>> round(float(result.minimum.isel(time=0).values), 2)
    0.0
    """
    _note_generic_bootstrap_capability(
        indicator_name="minimum",
        climate_vars=climate_vars,
        resample_freq=resample_freq,
        date_event=date_event,
    )
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

    Examples
    --------
    Annual mean of a constant 20 °C temperature series:

    >>> import numpy as np
    >>> import pandas as pd
    >>> import xarray as xr
    >>> import icclim
    >>> time = pd.date_range("2000-01-01", periods=365, freq="D")
    >>> tas = xr.DataArray(
    ...     np.full(365, 293.15),
    ...     coords={"time": time},
    ...     dims=["time"],
    ...     attrs={"units": "K"},
    ... )
    >>> result = icclim.average(in_files=tas, var_name="tas")
    >>> round(float(result.average.isel(time=0).values), 2)
    20.0
    """
    bootstrap_capability = _note_generic_bootstrap_capability(
        indicator_name="average",
        climate_vars=climate_vars,
        resample_freq=resample_freq,
    )
    study, threshold = get_single_var(climate_vars)
    from icclim._core.generic.threshold.percentile import (  # noqa: PLC0415
        PercentileThreshold,
    )

    bounded_spec = _get_scalar_bounded_bootstrap_spec(threshold)
    if (
        threshold is not None
        and bounded_spec is not None
        and bootstrap_capability.uses_optimized_bootstrap
    ):
        (
            percentile_threshold,
            scalar_bound,
            scalar_op_code,
            logical_link_code,
        ) = bounded_spec
        optimized_average = (
            _compute_fast_tiled_scalar_bounded_bootstrap_exceedance_average(
                climate_vars[0],
                percentile_threshold,
                resample_freq,
                scalar_bound,
                scalar_op_code,
                logical_link_code,
                _get_fast_bootstrap_max_cells(study),
            )
        )
        if optimized_average is not None:
            return optimized_average
    if (
        threshold is not None
        and bootstrap_capability.uses_optimized_bootstrap
        and isinstance(threshold, PercentileThreshold)
    ):
        if hasattr(study.indexes.get("time"), "calendar"):
            eager_mask = _compute_eager_tiled_cftime_bootstrap_mask(
                climate_vars[0],
                resample_freq,
            )
            if eager_mask is not None:
                return (
                    study.where(eager_mask)
                    .resample(time=resample_freq.pandas_freq)
                    .mean(dim="time")
                )
        optimized_average = _compute_fast_tiled_bootstrap_exceedance_average(
            climate_vars[0],
            threshold,
            resample_freq,
            _get_fast_bootstrap_max_cells(study),
        )
        if optimized_average is not None:
            return optimized_average
    stabilized_study = _materialize_study_for_optimized_compound_value_aggregate(
        study=study,
        threshold=threshold,
        bootstrap_capability=bootstrap_capability,
    )
    if stabilized_study is not study and threshold is not None:
        stabilized_climate_var = replace(climate_vars[0], studied_data=stabilized_study)
        exceedance_mask = _compute_threshold_exceedance_mask(
            climate_var=stabilized_climate_var,
            threshold=threshold,
            resample_freq=resample_freq,
            prepared_inputs_cache={},
        ).squeeze()
        return DataArrayResample.mean(
            stabilized_study.where(exceedance_mask).resample(
                time=resample_freq.pandas_freq
            ),
            dim="time",
        )
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

    Examples
    --------
    Annual total precipitation from a constant daily rate of 2 mm/day:

    >>> import numpy as np
    >>> import pandas as pd
    >>> import xarray as xr
    >>> import icclim
    >>> time = pd.date_range("2000-01-01", periods=365, freq="D")
    >>> pr = xr.DataArray(
    ...     np.full(365, 2.0),
    ...     coords={"time": time},
    ...     dims=["time"],
    ...     attrs={"units": "mm/day"},
    ... )
    >>> result = icclim.sum(in_files=pr, var_name="pr")
    >>> int(result["sum"].isel(time=0).values)
    730
    """
    bootstrap_capability = _note_generic_bootstrap_capability(
        indicator_name="sum",
        climate_vars=climate_vars,
        resample_freq=resample_freq,
    )
    study, threshold = get_single_var(climate_vars)
    from icclim._core.generic.threshold.percentile import (  # noqa: PLC0415
        PercentileThreshold,
    )

    bounded_spec = _get_scalar_bounded_bootstrap_spec(threshold)
    if (
        threshold is not None
        and bounded_spec is not None
        and bootstrap_capability.uses_optimized_bootstrap
        and not _is_rate(study)
    ):
        (
            percentile_threshold,
            scalar_bound,
            scalar_op_code,
            logical_link_code,
        ) = bounded_spec
        optimized_sum = _compute_fast_tiled_scalar_bounded_bootstrap_exceedance_sum(
            climate_vars[0],
            percentile_threshold,
            resample_freq,
            scalar_bound,
            scalar_op_code,
            logical_link_code,
            _get_fast_bootstrap_max_cells(study),
        )
        if optimized_sum is not None:
            return optimized_sum
    if (
        threshold is not None
        and bootstrap_capability.uses_optimized_bootstrap
        and isinstance(threshold, PercentileThreshold)
        and not _is_rate(study)
    ):
        if hasattr(study.indexes.get("time"), "calendar"):
            eager_mask = _compute_eager_tiled_cftime_bootstrap_mask(
                climate_vars[0],
                resample_freq,
            )
            if eager_mask is not None:
                return (
                    study.where(eager_mask)
                    .resample(time=resample_freq.pandas_freq)
                    .sum(dim="time")
                )
        optimized_sum = _compute_fast_tiled_bootstrap_exceedance_sum(
            climate_vars[0],
            threshold,
            resample_freq,
            _get_fast_bootstrap_max_cells(study),
        )
        if optimized_sum is not None:
            return optimized_sum
    stabilized_study = _materialize_study_for_optimized_compound_value_aggregate(
        study=study,
        threshold=threshold,
        bootstrap_capability=bootstrap_capability,
    )
    if stabilized_study is not study and threshold is not None and not _is_rate(study):
        stabilized_climate_var = replace(climate_vars[0], studied_data=stabilized_study)
        exceedance_mask = _compute_threshold_exceedance_mask(
            climate_var=stabilized_climate_var,
            threshold=threshold,
            resample_freq=resample_freq,
            prepared_inputs_cache={},
        ).squeeze()
        return DataArrayResample.sum(
            stabilized_study.where(exceedance_mask).resample(
                time=resample_freq.pandas_freq
            ),
            dim="time",
        )
    return _run_simple_reducer(
        climate_vars=climate_vars,
        resample_freq=resample_freq,
        reducer_op=DataArrayResample.sum,
        date_event=False,
        must_convert_rate=True,
    )


def _compute_optimized_fraction_of_total(
    *,
    climate_var: ClimateVariable,
    threshold: Threshold,
    study: DataArray,
    resample_freq: Frequency,
    bootstrap_capability: BootstrapCapability,
) -> DataArray | None:
    if not bootstrap_capability.uses_optimized_bootstrap:
        return None
    bounded_spec = _get_scalar_bounded_bootstrap_spec(threshold)
    if bounded_spec is not None:
        (
            percentile_threshold,
            scalar_bound,
            scalar_op_code,
            logical_link_code,
        ) = bounded_spec
        return _compute_fast_tiled_scalar_bounded_bootstrap_fraction_of_total(
            climate_var,
            percentile_threshold,
            resample_freq,
            scalar_bound,
            scalar_op_code,
            logical_link_code,
            _get_fast_bootstrap_max_cells(study),
        )
    from icclim._core.generic.threshold.percentile import (  # noqa: PLC0415
        PercentileThreshold,
    )

    if not isinstance(threshold, PercentileThreshold):
        return None
    if hasattr(study.indexes.get("time"), "calendar"):
        eager_mask = _compute_eager_tiled_cftime_bootstrap_mask(
            climate_var,
            resample_freq,
        )
        if eager_mask is None:
            return None
        if threshold.threshold_min_value is None:
            total = study.resample(time=resample_freq.pandas_freq).sum(dim="time")
        else:
            total = _sum_values_at_or_above_threshold_floor(
                study,
                threshold,
                resample_freq,
            )
        selected = (
            study.where(eager_mask, 0)
            .resample(time=resample_freq.pandas_freq)
            .sum(dim="time")
        )
        return selected / total
    return _compute_fast_tiled_bootstrap_fraction_of_total(
        climate_var,
        threshold,
        resample_freq,
        _get_fast_bootstrap_max_cells(study),
    )


def _sum_values_at_or_above_threshold_floor(
    study: DataArray,
    threshold: Threshold,
    resample_freq: Frequency,
) -> DataArray:
    from xclim.core.units import convert_units_to  # noqa: PLC0415

    floor = convert_units_to(threshold.threshold_min_value, study, context="hydro")
    return (
        study.where(study >= floor)
        .resample(time=resample_freq.pandas_freq)
        .sum(dim="time")
    )


def _materialize_study_for_optimized_compound_value_aggregate(
    *,
    study: DataArray,
    threshold: Threshold | None,
    bootstrap_capability: BootstrapCapability,
) -> DataArray:
    if (
        not bootstrap_capability.uses_optimized_bootstrap
        or bootstrap_capability.reason_code
        != "optimized_compound_value_aggregate_bootstrap_supported"
    ):
        return study
    from icclim._core.generic.bootstrap_primitives import (  # noqa: PLC0415
        _materialize_bootstrap_study,
    )
    from icclim._core.generic.threshold.bounded import BoundedThreshold  # noqa: PLC0415

    if not isinstance(threshold, BoundedThreshold):
        return study
    stabilized = _materialize_bootstrap_study(study, prefer_file_reopen=True)
    if not hasattr(study.data, "chunks"):
        return stabilized
    return stabilized.chunk(
        {
            dim: chunks
            for dim, chunks in study.chunksizes.items()
            if dim in stabilized.dims
        }
    )


def _format_fraction_of_total_result(
    result: DataArray,
    *,
    to_percent: bool,
) -> DataArray:
    if to_percent:
        result = result * 100
        result.attrs[UNITS_KEY] = "%"
    else:
        result.attrs[UNITS_KEY] = PART_OF_A_WHOLE_UNIT
    return result


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
    _note_generic_bootstrap_capability(
        indicator_name="standard_deviation",
        climate_vars=climate_vars,
        resample_freq=resample_freq,
    )
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
        rolling_op=lambda x: x.sum(),
        resampled_op=lambda x: x.max(),
        extreme="max",
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
        rolling_op=lambda x: x.sum(),
        resampled_op=lambda x: x.min(),
        extreme="min",
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
        rolling_op=lambda x: x.mean(),
        resampled_op=lambda x: x.min(),
        extreme="min",
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
        rolling_op=lambda x: x.mean(),
        resampled_op=lambda x: x.max(),
        extreme="max",
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


def absolute_mean_of_difference(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    **kwargs,  # noqa: ARG001
) -> DataArray:
    """
    Calculate the absolute value of the mean of the difference of two climate variables.

    The difference of the two variables is averaged over each period, then the absolute
    value of that mean is taken for each grid point. It does not depend on the order
    of the two variables. It is the absolute value of the period mean, not the mean of
    the daily absolute differences: when the sign of the difference changes within a
    period, the two are not equal.
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
        The absolute value of the mean of the difference, never negative.

    Notes
    -----
    This is the generic function of the DCSC index TRAV. The data are not checked:
    if the first variable is below the second one everywhere, the result is positive
    all the same.
    """
    study, ref = get_couple_of_var(climate_vars, "absolute_mean_of_difference")
    mean_of_diff = (study - ref).resample(time=resample_freq.pandas_freq).mean()
    result = abs(mean_of_diff)
    result.attrs["units"] = study.attrs["units"]
    return result


# Upper latitude (degrees north) of each step of the daylength coefficient K of the
# Huglin index, ECA&D ATBD v11 table 2. Each step includes its upper boundary and the
# first one starts at the equator: the ATBD gives no value below 0 (southern hemisphere)
# nor above 50 degrees north.
_HUGLIN_K_BY_LATITUDE = (
    (40.0, 1.00),
    (42.0, 1.02),
    (44.0, 1.03),
    (46.0, 1.04),
    (48.0, 1.05),
    (50.0, 1.06),
)


def _viticulture_season(da: DataArray) -> DataArray:
    """True on the days from 1 April to 30 September."""
    return (da.time.dt.month >= 4) & (da.time.dt.month <= 9)  # noqa: PLR2004


def _get_latitude(da: DataArray, indicator: str) -> DataArray:
    """Latitude (degrees north) of the studied data, taken from its coordinates."""
    latitude = None
    try:
        latitude = da.cf["latitude"]
    except (KeyError, ValueError):
        for name in ("lat", "latitude"):
            if name in da.coords:
                latitude = da.coords[name]
                break
    if latitude is None:
        msg = (
            f"{indicator} needs the latitude of the data to compute its daylength"
            " coefficient, but no latitude coordinate was found. Name the coordinate"
            ' "lat" or "latitude", or give it the units "degrees_north" or the'
            ' standard_name "latitude".'
        )
        raise InvalidIcclimArgumentError(msg)
    return latitude


def _huglin_coefficient(latitude: DataArray) -> DataArray:
    """
    Daylength coefficient K of the Huglin index.

    It is missing at latitudes below 0 and above 50 degrees north. Each step includes
    its upper boundary (K = 1.02 at 42 degrees north, 1.03 at 44 degrees north...).
    """
    k = xr.full_like(latitude, np.nan, dtype="float64")
    in_first_step = True
    lower = 0.0
    for upper, value in _HUGLIN_K_BY_LATITUDE:
        above_lower = (latitude >= lower) if in_first_step else (latitude > lower)
        k = xr.where(above_lower & (latitude <= upper), value, k)
        in_first_step = False
        lower = upper
    return k


def huglin_index(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    **kwargs,  # noqa: ARG001
) -> DataArray:
    """
    Compute the Huglin Index (HI) of the ECA&D ATBD v11.

    ``HI = sum(((TG - 10) + (TX - 10)) / 2 * K)`` over the days from 1 April to
    30 September of each output period, in degree_Celsius day, where TG is the daily
    mean and TX the daily maximum temperature and K the daylength coefficient of the
    latitude (1.00 up to 40 N, 1.02 up to 42 N, 1.03 up to 44 N, 1.04 up to 46 N, 1.05
    up to 48 N and 1.06 up to 50 N; each band includes its upper boundary).

    The index is defined for the northern hemisphere only: the result is missing at
    latitudes below 0 (southern hemisphere) and above 50 degrees north.

    Parameters
    ----------
    climate_vars : list[ClimateVariable]
        The daily mean temperature, then the daily maximum temperature. The latitude
        is read from the coordinates of the data.
    resample_freq : Frequency
        Resampling frequency of the output.
    **kwargs : dict
        Ignored keyword arguments (for compatibility).

    Returns
    -------
    DataArray
        The Huglin Index. It is missing for the periods without any day from April to
        September, and where the latitude is below 0 or above 50 degrees north.

    Notes
    -----
    Unlike xclim's ``huglin_index``, the daily values are not clipped at 0, as in the
    ATBD formula, and K is not capped above 50 degrees north.
    """
    from xclim.core.units import convert_units_to  # noqa: PLC0415

    tas, tasmax = get_couple_of_var(climate_vars, "huglin_index")
    tas = convert_units_to(tas, "degC")
    tasmax = convert_units_to(tasmax, "degC")
    k = _huglin_coefficient(_get_latitude(tasmax, "huglin_index"))
    daily = (((tas - 10) + (tasmax - 10)) / 2 * k).where(_viticulture_season(tasmax))
    hi = daily.resample(time=resample_freq.pandas_freq).sum(min_count=1)
    hi.attrs["units"] = "degree_Celsius day"
    return hi


def biologically_effective_degree_days(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    **kwargs,  # noqa: ARG001
) -> DataArray:
    """
    Compute the Biologically Effective Degree Days (BEDD) of the ECA&D ATBD v11.

    ``BEDD = sum(min(max((TX + TN) / 2 - b, 0), 9))`` over the days from 1 April to
    30 September of each output period, in degree_Celsius day, where TX and TN are
    the daily maximum and minimum temperature and ``b = 10`` degree_Celsius.

    Parameters
    ----------
    climate_vars : list[ClimateVariable]
        The daily minimum temperature, then the daily maximum temperature.
    resample_freq : Frequency
        Resampling frequency of the output.
    **kwargs : dict
        Ignored keyword arguments (for compatibility).

    Returns
    -------
    DataArray
        The BEDD. It is missing for the periods without any valid day from April to
        September.

    Notes
    -----
    This is the definition of xclim's ``biologically_effective_degree_days`` with
    ``method="icclim"`` (no latitude coefficient, no temperature range adjustment),
    except that a period without any valid day is missing instead of 0.
    """
    from xclim.core.units import convert_units_to  # noqa: PLC0415

    tasmin, tasmax = get_couple_of_var(
        climate_vars, "biologically_effective_degree_days"
    )
    tasmin = convert_units_to(tasmin, "degC")
    tasmax = convert_units_to(tasmax, "degC")
    daily = (((tasmax + tasmin) / 2) - 10).clip(min=0, max=9)
    daily = daily.where(
        _viticulture_season(tasmax) & tasmin.notnull() & tasmax.notnull()
    )
    bedd = daily.resample(time=resample_freq.pandas_freq).sum(min_count=1)
    bedd.attrs["units"] = "degree_Celsius day"
    return bedd


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
    variables for each time step within each output period. The first time step of
    every period contributes no difference. The mean uses the number of valid
    differences as its denominator; unlike the ECA&D ATBD v11 section 5.3.11 formula,
    it does not divide by the number of days in the period.
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
    daily_range = study - ref
    res = daily_range.resample(time=resample_freq.pandas_freq).map(
        lambda period: abs(period.diff(dim="time")).mean(dim="time")
    )
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
    from xclim.core.units import convert_units_to  # noqa: PLC0415

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
    percentile_threshold = cast("PercentileThreshold", threshold)  # pragma: no mutate
    if percentile_threshold.initial_value is None:
        msg = "PercentileThreshold must have a value"
        raise InvalidIcclimArgumentError(msg)
    requested = np.asarray(percentile_threshold.initial_value)
    quantile = requested * 0.01 if requested.size > 1 else float(requested[0]) * 0.01
    method = cast("Any", percentile_threshold.interpolation.name)  # pragma: no mutate
    result = study.resample(time=resample_freq.pandas_freq).quantile(
        quantile, method=method
    )
    result.coords["quantile"] = result.coords["quantile"] * 100
    result = result.rename(quantile="percentiles")
    from xclim.core.calendar import build_climatology_bounds  # noqa: PLC0415

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
    reducer: Callable[[DataArrayResample | DataArray | DataArrayGroupBy], DataArray],
) -> DataArray:
    mean_ref = reducer(ref.groupby(resample_freq.group_by_key))
    if resample_freq == FrequencyRegistry.MONTH:
        key = "month"
    elif resample_freq == FrequencyRegistry.DAY:
        key = "dayofyear"
    else:
        msg = (
            f"Can't use {GROUP_BY_REF_AND_RESAMPLE_STUDY_METHOD}"
            f" with the frequency {resample_freq.long_name}."
        )
        raise NotImplementedError(msg)
    reduced_study = reducer(study.resample(time=resample_freq.pandas_freq))
    selector = getattr(reduced_study.time.dt, key)
    selected_ref = mean_ref.sel({key: selector}).drop_vars(key)
    diff_of_means = reduced_study - selected_ref
    if to_percent:
        diff_of_means = diff_of_means / selected_ref * 100
        diff_of_means.attrs["units"] = "%"
    else:
        diff_of_means.attrs["units"] = study.attrs["units"]
    return diff_of_means


def _compute_exceedance_mask(
    study: DataArray,
    threshold: Threshold,
    freq: str,  # used by @percentile_bootstrap (don't rename, it breaks bootstrap)
    bootstrap: bool,  # used by @percentile_bootstrap
) -> DataArray:
    exceedance_mask = threshold.compute(study, freq=freq, bootstrap=bootstrap)
    if bootstrap:
        climatology_bounds = getattr(threshold, "climatology_bounds", lambda *_: None)(
            study
        )
        if climatology_bounds is not None:
            exceedance_mask.attrs[REFERENCE_PERIOD_ID] = climatology_bounds
    return exceedance_mask


def _note_generic_bootstrap_capability(
    *,
    indicator_name: str,
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    date_event: bool = False,
) -> BootstrapCapability:
    capability = classify_generic_indicator_bootstrap(
        indicator_name=indicator_name,
        climate_vars=climate_vars,
        resample_frequency=resample_freq,
        date_event=date_event,
    )
    _profile_bootstrap_note(
        "bootstrap_execution_kind",
        capability.execution_kind.value,
    )
    _profile_bootstrap_note(
        "bootstrap_reason_code",
        capability.reason_code,
    )
    _profile_bootstrap_note(
        "bootstrap_family",
        capability.family.value,
    )
    return capability


def _compute_safe_tiled_count_occurrences(  # noqa: C901
    climate_var: ClimateVariable,
    resample_freq: Frequency,
) -> DataArray | None:
    threshold = climate_var.threshold
    if threshold is None:
        return None
    from icclim._core.generic.threshold.percentile import (  # noqa: PLC0415
        PercentileThreshold,
    )

    if (
        not isinstance(threshold, PercentileThreshold)
        or not threshold.is_doy_per_threshold
    ):
        return None

    bootstrap_capability = classify_doy_percentile_count_bootstrap(
        climate_var,
        resample_freq,
    )
    _profile_bootstrap_note(
        "bootstrap_count_execution_kind",
        bootstrap_capability.execution_kind.value,
    )
    _profile_bootstrap_note(
        "bootstrap_count_reason_code",
        bootstrap_capability.reason_code,
    )
    _profile_bootstrap_note(
        "bootstrap_count_family",
        bootstrap_capability.family.value,
    )
    if not bootstrap_capability.bootstrap_required:
        return None
    if (
        bootstrap_capability.execution_kind
        == BootstrapExecutionKind.REFERENCE_BOOTSTRAP
    ):
        return None

    safe_start = perf_counter()
    max_cells = _get_safe_bootstrap_max_cells(
        climate_var.studied_data,
        threshold,
        resample_freq,
    )
    _profile_bootstrap_set("bootstrap_safe_max_tile_cells", max_cells)
    if bootstrap_capability.uses_optimized_bootstrap:
        optimized = _compute_fast_tiled_count_occurrences(
            climate_var,
            threshold,
            resample_freq,
            _get_fast_bootstrap_max_cells(climate_var.studied_data),
        )
        if optimized is not None:
            return optimized
    while True:
        try:
            return _compute_safe_tiled_count_occurrences_with_max_cells(
                climate_var,
                threshold,
                resample_freq,
                max_cells,
                safe_start,
            )
        except Exception as err:
            if not _is_memory_like_bootstrap_error(err):
                raise
            if max_cells <= 1:
                msg = (
                    "Percentile bootstrap failed even with one spatial cell per tile. "
                    "Try reducing the time range, using fewer workers/threads, or "
                    "running with more memory."
                )
                raise MemoryError(msg) from err
            max_cells = max(1, max_cells // 2)
            _profile_bootstrap_inc("bootstrap_safe_memory_retry_count")
            _profile_bootstrap_set("bootstrap_safe_max_tile_cells", max_cells)


def _compute_safe_tiled_count_occurrences_with_max_cells(
    climate_var: ClimateVariable,
    threshold: PercentileThreshold,
    resample_freq: Frequency,
    max_cells: int,
    safe_start: float,
) -> DataArray:
    tile_results: list[DataArray] = []
    for tile_indexers in _iter_spatial_tiles(climate_var.studied_data, max_cells):
        tile_start = perf_counter()
        tile_study = climate_var.studied_data.isel(tile_indexers)
        tile_threshold = _slice_threshold_for_tile(threshold, tile_indexers)
        tile_exceedance_mask = _compute_exceedance_mask(
            tile_study,
            tile_threshold,
            freq=resample_freq.pandas_freq,
            bootstrap=True,
        )
        tile_exceedance_mask = tile_exceedance_mask.fillna(False).astype(
            bool,
            copy=False,
        )
        tile_result = tile_exceedance_mask.resample(time=resample_freq.pandas_freq).sum(
            dim="time"
        )
        if "percentiles" in tile_result.dims:
            tile_result = tile_result.squeeze("percentiles")
        tile_results.append(tile_result.load())
        _profile_bootstrap_inc("bootstrap_safe_tile_count")
        _profile_bootstrap_add(
            "bootstrap_safe_tile_seconds",
            perf_counter() - tile_start,
        )

    if len(tile_results) == 1:
        result = tile_results[0]
    else:
        result = xr.combine_by_coords(
            [tile.to_dataset(name="__icclim_bootstrap_tile") for tile in tile_results],
            combine_attrs="override",
        )["__icclim_bootstrap_tile"]
    result.attrs.update(tile_results[-1].attrs)
    _profile_bootstrap_add(
        "bootstrap_safe_total_seconds",
        perf_counter() - safe_start,
    )
    return result


def _compute_fast_tiled_count_occurrences(
    climate_var: ClimateVariable,
    threshold: PercentileThreshold,
    resample_freq: Frequency,
    max_cells: int,
) -> DataArray | None:
    from icclim._core.generic.bootstrap import (  # noqa: PLC0415
        compute_doy_percentile_bootstrap_count,
        compute_doy_percentile_bootstrap_union_exceedance_count,
    )

    fast_start = perf_counter()
    tile_results: list[DataArray] = []
    for tile_indexers in _iter_spatial_tiles(climate_var.studied_data, max_cells):
        tile_study = climate_var.studied_data.isel(tile_indexers)
        tile_threshold = _slice_threshold_for_tile(threshold, tile_indexers)
        reducer = (
            compute_doy_percentile_bootstrap_count
            if resample_freq == FrequencyRegistry.YEAR
            else compute_doy_percentile_bootstrap_union_exceedance_count
        )
        tile_result = reducer(
            tile_study,
            tile_threshold,
            resample_freq.pandas_freq,
        )
        if tile_result is None:
            return None
        tile_results.append(tile_result)
        _profile_bootstrap_inc("bootstrap_optimized_tile_count")
    if len(tile_results) == 1:
        result = tile_results[0]
    else:
        result = xr.combine_by_coords(
            [tile.to_dataset(name="__icclim_bootstrap_tile") for tile in tile_results],
            combine_attrs="override",
        )["__icclim_bootstrap_tile"]
    result.attrs.update(tile_results[-1].attrs)
    _profile_bootstrap_add(
        "bootstrap_optimized_total_seconds",
        perf_counter() - fast_start,
    )
    return result


def _compute_fast_tiled_bootstrap_exceedance_sum(
    climate_var: ClimateVariable,
    threshold: PercentileThreshold,
    resample_freq: Frequency,
    max_cells: int,
    *,
    prepared_inputs_cache: dict[tuple, BootstrapPreparedInputs] | None = None,
) -> DataArray | None:
    from icclim._core.generic.bootstrap import (  # noqa: PLC0415
        compute_doy_percentile_bootstrap_exceedance_sum,
    )
    from icclim._core.generic.bootstrap_primitives import (  # noqa: PLC0415
        build_bootstrap_prepared_inputs,
    )

    optimized_start = perf_counter()
    tile_results: list[DataArray] = []
    for tile_indexers in _iter_spatial_tiles(climate_var.studied_data, max_cells):
        tile_study = climate_var.studied_data.isel(tile_indexers)
        tile_threshold = _slice_threshold_for_tile(threshold, tile_indexers)
        prepared_inputs = None
        if prepared_inputs_cache is not None:
            cache_key = _bootstrap_tile_preparation_cache_key(
                tile_indexers,
                tile_threshold,
                resample_freq.pandas_freq,
            )
            prepared_inputs = prepared_inputs_cache.get(cache_key)
            if prepared_inputs is None:
                prepared_inputs = build_bootstrap_prepared_inputs(
                    tile_study,
                    tile_threshold,
                    resample_freq.pandas_freq,
                    dtype=np.float32,
                    prefer_file_reopen=True,
                )
                prepared_inputs_cache[cache_key] = prepared_inputs
        tile_result = compute_doy_percentile_bootstrap_exceedance_sum(
            tile_study,
            tile_threshold,
            resample_freq.pandas_freq,
            prepared_inputs=prepared_inputs,
        )
        if tile_result is None:
            return None
        tile_results.append(tile_result)
        _profile_bootstrap_inc("bootstrap_optimized_tile_count")
    if len(tile_results) == 1:
        result = tile_results[0]
    else:
        result = xr.combine_by_coords(
            [tile.to_dataset(name="__icclim_bootstrap_tile") for tile in tile_results],
            combine_attrs="override",
        )["__icclim_bootstrap_tile"]
    result.attrs.update(tile_results[-1].attrs)
    _profile_bootstrap_add(
        "bootstrap_optimized_total_seconds",
        perf_counter() - optimized_start,
    )
    return result


def _compute_fast_tiled_scalar_bounded_bootstrap_count(
    climate_var: ClimateVariable,
    threshold: PercentileThreshold,
    resample_freq: Frequency,
    scalar_bound: float,
    scalar_op_code: int,
    logical_link_code: int,
    max_cells: int,
) -> DataArray | None:
    from icclim._core.generic.bootstrap import (  # noqa: PLC0415
        compute_doy_percentile_scalar_bounded_bootstrap_count,
    )

    return _compute_fast_tiled_scalar_bounded_bootstrap_reducer(
        climate_var,
        reducer=compute_doy_percentile_scalar_bounded_bootstrap_count,
        threshold=threshold,
        resample_freq=resample_freq,
        scalar_bound=scalar_bound,
        scalar_op_code=scalar_op_code,
        logical_link_code=logical_link_code,
        max_cells=max_cells,
    )


def _compute_fast_tiled_bootstrap_exceedance_average(
    climate_var: ClimateVariable,
    threshold: PercentileThreshold,
    resample_freq: Frequency,
    max_cells: int,
) -> DataArray | None:
    from icclim._core.generic.bootstrap import (  # noqa: PLC0415
        compute_doy_percentile_bootstrap_exceedance_average,
    )

    return _compute_fast_tiled_bootstrap_reducer(
        climate_var,
        reducer=compute_doy_percentile_bootstrap_exceedance_average,
        threshold=threshold,
        resample_freq=resample_freq,
        max_cells=max_cells,
    )


def _compute_fast_tiled_scalar_bounded_bootstrap_exceedance_average(
    climate_var: ClimateVariable,
    threshold: PercentileThreshold,
    resample_freq: Frequency,
    scalar_bound: float,
    scalar_op_code: int,
    logical_link_code: int,
    max_cells: int,
) -> DataArray | None:
    from icclim._core.generic.bootstrap import (  # noqa: PLC0415
        compute_doy_percentile_scalar_bounded_bootstrap_exceedance_average,
    )

    return _compute_fast_tiled_scalar_bounded_bootstrap_reducer(
        climate_var,
        reducer=compute_doy_percentile_scalar_bounded_bootstrap_exceedance_average,
        threshold=threshold,
        resample_freq=resample_freq,
        scalar_bound=scalar_bound,
        scalar_op_code=scalar_op_code,
        logical_link_code=logical_link_code,
        max_cells=max_cells,
    )


def _compute_fast_tiled_bootstrap_fraction_of_total(
    climate_var: ClimateVariable,
    threshold: PercentileThreshold,
    resample_freq: Frequency,
    max_cells: int,
) -> DataArray | None:
    from icclim._core.generic.bootstrap import (  # noqa: PLC0415
        compute_doy_percentile_bootstrap_fraction_of_total,
    )

    return _compute_fast_tiled_bootstrap_reducer(
        climate_var,
        reducer=compute_doy_percentile_bootstrap_fraction_of_total,
        threshold=threshold,
        resample_freq=resample_freq,
        max_cells=max_cells,
    )


def _compute_fast_tiled_scalar_bounded_bootstrap_exceedance_sum(
    climate_var: ClimateVariable,
    threshold: PercentileThreshold,
    resample_freq: Frequency,
    scalar_bound: float,
    scalar_op_code: int,
    logical_link_code: int,
    max_cells: int,
) -> DataArray | None:
    from icclim._core.generic.bootstrap import (  # noqa: PLC0415
        compute_doy_percentile_scalar_bounded_bootstrap_exceedance_sum,
    )

    return _compute_fast_tiled_scalar_bounded_bootstrap_reducer(
        climate_var,
        reducer=compute_doy_percentile_scalar_bounded_bootstrap_exceedance_sum,
        threshold=threshold,
        resample_freq=resample_freq,
        scalar_bound=scalar_bound,
        scalar_op_code=scalar_op_code,
        logical_link_code=logical_link_code,
        max_cells=max_cells,
    )


def _compute_fast_tiled_scalar_bounded_bootstrap_fraction_of_total(
    climate_var: ClimateVariable,
    threshold: PercentileThreshold,
    resample_freq: Frequency,
    scalar_bound: float,
    scalar_op_code: int,
    logical_link_code: int,
    max_cells: int,
) -> DataArray | None:
    from icclim._core.generic.bootstrap import (  # noqa: PLC0415
        compute_doy_percentile_scalar_bounded_bootstrap_fraction_of_total,
    )

    return _compute_fast_tiled_scalar_bounded_bootstrap_reducer(
        climate_var,
        reducer=compute_doy_percentile_scalar_bounded_bootstrap_fraction_of_total,
        threshold=threshold,
        resample_freq=resample_freq,
        scalar_bound=scalar_bound,
        scalar_op_code=scalar_op_code,
        logical_link_code=logical_link_code,
        max_cells=max_cells,
    )


def _compute_fast_tiled_bootstrap_reducer(
    climate_var: ClimateVariable,
    reducer: Callable[[DataArray, PercentileThreshold, str], DataArray | None],
    threshold: PercentileThreshold,
    resample_freq: Frequency,
    max_cells: int,
) -> DataArray | None:
    optimized_start = perf_counter()
    tile_results: list[DataArray] = []
    for tile_indexers in _iter_spatial_tiles(climate_var.studied_data, max_cells):
        tile_study = climate_var.studied_data.isel(tile_indexers)
        tile_threshold = _slice_threshold_for_tile(threshold, tile_indexers)
        tile_result = reducer(
            tile_study,
            tile_threshold,
            resample_freq.pandas_freq,
        )
        if tile_result is None:
            return None
        tile_results.append(tile_result)
        _profile_bootstrap_inc("bootstrap_optimized_tile_count")
    if len(tile_results) == 1:
        result = tile_results[0]
    else:
        result = xr.combine_by_coords(
            [tile.to_dataset(name="__icclim_bootstrap_tile") for tile in tile_results],
            combine_attrs="override",
        )["__icclim_bootstrap_tile"]
    result.attrs.update(tile_results[-1].attrs)
    _profile_bootstrap_add(
        "bootstrap_optimized_total_seconds",
        perf_counter() - optimized_start,
    )
    return result


def _compute_fast_tiled_scalar_bounded_bootstrap_reducer(
    climate_var: ClimateVariable,
    reducer: Callable[
        [DataArray, PercentileThreshold, str, float, int, int], DataArray | None
    ],
    threshold: PercentileThreshold,
    resample_freq: Frequency,
    scalar_bound: float,
    scalar_op_code: int,
    logical_link_code: int,
    max_cells: int,
) -> DataArray | None:
    optimized_start = perf_counter()
    tile_results: list[DataArray] = []
    for tile_indexers in _iter_spatial_tiles(climate_var.studied_data, max_cells):
        tile_study = climate_var.studied_data.isel(tile_indexers)
        tile_threshold = _slice_threshold_for_tile(threshold, tile_indexers)
        tile_result = reducer(
            tile_study,
            tile_threshold,
            resample_freq.pandas_freq,
            scalar_bound,
            scalar_op_code,
            logical_link_code,
        )
        if tile_result is None:
            return None
        tile_results.append(tile_result)
        _profile_bootstrap_inc("bootstrap_optimized_tile_count")
    if len(tile_results) == 1:
        result = tile_results[0]
    else:
        result = xr.combine_by_coords(
            [tile.to_dataset(name="__icclim_bootstrap_tile") for tile in tile_results],
            combine_attrs="override",
        )["__icclim_bootstrap_tile"]
    result.attrs.update(tile_results[-1].attrs)
    _profile_bootstrap_add(
        "bootstrap_optimized_total_seconds",
        perf_counter() - optimized_start,
    )
    return result


def _compute_bootstrap_spell_mask(
    climate_var: ClimateVariable,
    resample_freq: Frequency,
    *,
    bootstrap_capability: BootstrapCapability,
) -> DataArray | None:
    from icclim._core.generic.threshold.percentile import (  # noqa: PLC0415
        PercentileThreshold,
    )

    if not bootstrap_capability.bootstrap_required:
        return None
    if not isinstance(climate_var.threshold, PercentileThreshold):
        return None
    if bootstrap_capability.uses_optimized_bootstrap:
        if hasattr(climate_var.studied_data.indexes.get("time"), "calendar"):
            return _compute_eager_tiled_cftime_bootstrap_mask(
                climate_var,
                resample_freq,
            )
        return _compute_fast_tiled_bootstrap_spell_mask(
            climate_var,
            resample_freq,
            _get_fast_bootstrap_max_cells(climate_var.studied_data),
        )
    if bootstrap_capability.uses_exact_tiled_bootstrap:
        return _compute_exact_tiled_bootstrap_spell_mask(
            climate_var,
            resample_freq,
        )
    return None


def _compute_eager_tiled_cftime_bootstrap_mask(
    climate_var: ClimateVariable,
    resample_freq: Frequency,
) -> DataArray | None:
    from concurrent.futures import ThreadPoolExecutor  # noqa: PLC0415

    from icclim._core.generic.bootstrap import (  # noqa: PLC0415
        compute_doy_percentile_bootstrap_union_mask_eager,
    )
    from icclim._core.generic.threshold.percentile import (  # noqa: PLC0415
        PercentileThreshold,
    )

    threshold = climate_var.threshold
    if not isinstance(threshold, PercentileThreshold):
        return None
    worker_count = min(3, os.cpu_count() or 1)
    memory_budget = _parse_byte_size(
        os.environ.get(
            "ICCLIM_BOOTSTRAP_SAFE_TILE_MEMORY",
            _DEFAULT_BOOTSTRAP_SAFE_TILE_MEMORY,
        )
    )
    study = climate_var.studied_data
    prepared_threshold = copy(threshold)
    prepared_threshold.ensure_ready(study)
    prepared_threshold._prepared_value = (  # noqa: SLF001
        prepared_threshold.value.copy(deep=False).load()
    )
    if study.nbytes <= memory_budget // 4:
        study = study.load()
    total_max_cells = _get_safe_bootstrap_max_cells(
        study,
        threshold,
        resample_freq,
    )
    tiles = _iter_spatial_tiles(
        study,
        max(1, total_max_cells // worker_count),
    )

    def compute_tile(
        tile_study: DataArray,
        tile_threshold: PercentileThreshold,
    ) -> DataArray | None:
        return compute_doy_percentile_bootstrap_union_mask_eager(
            tile_study,
            tile_threshold,
            resample_freq.pandas_freq,
        )

    optimized_start = perf_counter()
    with ThreadPoolExecutor(max_workers=worker_count) as pool:
        tile_results = []
        for batch_start in range(0, len(tiles), worker_count):
            batch = tiles[batch_start : batch_start + worker_count]
            loaded_tiles = [study.isel(indexers).load() for indexers in batch]
            tile_thresholds = [
                _slice_threshold_for_tile(prepared_threshold, indexers)
                for indexers in batch
            ]
            tile_results.extend(pool.map(compute_tile, loaded_tiles, tile_thresholds))
    if any(result is None for result in tile_results):
        return None
    concrete_results = cast("list[DataArray]", tile_results)
    if len(concrete_results) == 1:
        result = concrete_results[0]
    else:
        result = xr.combine_by_coords(
            [
                tile.to_dataset(name="__icclim_bootstrap_tile")
                for tile in concrete_results
            ],
            combine_attrs="override",
        )["__icclim_bootstrap_tile"]
    result.attrs.update(concrete_results[-1].attrs)
    _profile_bootstrap_inc("bootstrap_optimized_tile_count", len(tiles))
    _profile_bootstrap_add(
        "bootstrap_optimized_total_seconds",
        perf_counter() - optimized_start,
    )
    return _transpose_like_study(result, climate_var.studied_data)


def _prepare_eager_cftime_compound_threshold(
    threshold: Threshold,
    study: DataArray,
) -> Threshold:
    from icclim._core.generic.threshold.bounded import (  # noqa: PLC0415
        BoundedThreshold,
    )
    from icclim._core.generic.threshold.percentile import (  # noqa: PLC0415
        PercentileThreshold,
    )

    if not isinstance(threshold, BoundedThreshold):
        if not isinstance(threshold, PercentileThreshold):
            return threshold
        prepared = copy(threshold)
        prepared.ensure_ready(study)
        prepared._prepared_value = prepared.value.copy(deep=False).load()  # noqa: SLF001
        return prepared
    prepared = copy(threshold)
    prepared.left_threshold = _prepare_eager_cftime_compound_threshold(
        threshold.left_threshold,
        study,
    )
    prepared.right_threshold = _prepare_eager_cftime_compound_threshold(
        threshold.right_threshold,
        study,
    )
    return prepared


def _iter_compound_percentile_thresholds(
    threshold: Threshold,
) -> list[PercentileThreshold]:
    from icclim._core.generic.threshold.bounded import (  # noqa: PLC0415
        BoundedThreshold,
    )
    from icclim._core.generic.threshold.percentile import (  # noqa: PLC0415
        PercentileThreshold,
    )

    if isinstance(threshold, PercentileThreshold):
        return [threshold]
    if isinstance(threshold, BoundedThreshold):
        return [
            *_iter_compound_percentile_thresholds(threshold.left_threshold),
            *_iter_compound_percentile_thresholds(threshold.right_threshold),
        ]
    return []


def _slice_eager_cftime_compound_threshold(
    threshold: Threshold,
    indexers: dict[str, slice],
) -> Threshold:
    from icclim._core.generic.threshold.bounded import (  # noqa: PLC0415
        BoundedThreshold,
    )
    from icclim._core.generic.threshold.percentile import (  # noqa: PLC0415
        PercentileThreshold,
    )

    if isinstance(threshold, PercentileThreshold):
        return _slice_threshold_for_tile(threshold, indexers)
    if not isinstance(threshold, BoundedThreshold):
        return threshold
    sliced = copy(threshold)
    sliced.left_threshold = _slice_eager_cftime_compound_threshold(
        threshold.left_threshold,
        indexers,
    )
    sliced.right_threshold = _slice_eager_cftime_compound_threshold(
        threshold.right_threshold,
        indexers,
    )
    return sliced


def _compute_eager_cftime_compound_component_mask(
    study: DataArray,
    threshold: Threshold,
    resample_freq: Frequency,
    bootstrap: bool | None,
) -> DataArray | None:
    from icclim._core.generic.bootstrap import (  # noqa: PLC0415
        compute_doy_percentile_bootstrap_union_mask_eager,
    )
    from icclim._core.generic.threshold.bounded import (  # noqa: PLC0415
        BoundedThreshold,
    )
    from icclim._core.generic.threshold.percentile import (  # noqa: PLC0415
        PercentileThreshold,
    )

    if isinstance(threshold, BoundedThreshold):
        left = _compute_eager_cftime_compound_component_mask(
            study,
            threshold.left_threshold,
            resample_freq,
            bootstrap,
        )
        right = _compute_eager_cftime_compound_component_mask(
            study,
            threshold.right_threshold,
            resample_freq,
            bootstrap,
        )
        if left is None or right is None:
            return None
        return threshold.logical_link.compute([left, right])
    if (
        isinstance(threshold, PercentileThreshold)
        and threshold.is_doy_per_threshold
        and must_run_bootstrap(study, threshold, bootstrap)
    ):
        return compute_doy_percentile_bootstrap_union_mask_eager(
            study,
            threshold,
            resample_freq.pandas_freq,
        )
    return _compute_exceedance_mask(
        study=study,
        threshold=threshold,
        freq=resample_freq.pandas_freq,
        bootstrap=False,
    )


def _get_aligned_cftime_compound_studies(
    climate_vars: list[ClimateVariable],
) -> list[DataArray] | None:
    if not climate_vars or any(
        climate_var.threshold is None for climate_var in climate_vars
    ):
        return None
    studies = [climate_var.studied_data for climate_var in climate_vars]
    if not all(hasattr(study.indexes.get("time"), "calendar") for study in studies):
        return None
    reference = studies[0]
    for candidate in studies[1:]:
        if candidate.dims != reference.dims:
            return None
        if any(
            candidate.sizes[dim] != reference.sizes[dim]
            or not candidate.get_index(dim).equals(reference.get_index(dim))
            for dim in reference.dims
        ):
            return None
    return studies


def _compute_eager_tiled_cftime_compound_mask(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    logical_link: LogicalLink,
) -> DataArray | None:
    from concurrent.futures import ThreadPoolExecutor  # noqa: PLC0415

    studies = _get_aligned_cftime_compound_studies(climate_vars)
    if studies is None:
        return None
    study = studies[0]

    prepared_thresholds = [
        _prepare_eager_cftime_compound_threshold(
            cast("Threshold", climate_var.threshold),
            climate_var.studied_data,
        )
        for climate_var in climate_vars
    ]
    percentile_inputs = [
        (component_study, percentile_threshold)
        for component_study, prepared_threshold in zip(
            studies,
            prepared_thresholds,
            strict=True,
        )
        for percentile_threshold in _iter_compound_percentile_thresholds(
            prepared_threshold
        )
    ]
    if not percentile_inputs:
        return None
    worker_count = min(3, os.cpu_count() or 1)
    memory_budget = _parse_byte_size(
        os.environ.get(
            "ICCLIM_BOOTSTRAP_SAFE_TILE_MEMORY",
            _DEFAULT_BOOTSTRAP_SAFE_TILE_MEMORY,
        )
    )
    if sum(component_study.nbytes for component_study in studies) <= (
        memory_budget // 4
    ):
        studies = [component_study.load() for component_study in studies]
        study = studies[0]
    total_max_cells = min(
        _get_safe_bootstrap_max_cells(
            component_study,
            percentile_threshold,
            resample_freq,
        )
        for component_study, percentile_threshold in percentile_inputs
    )
    tiles = _iter_spatial_tiles(
        study,
        max(1, total_max_cells // worker_count),
    )

    def compute_tile(indexers: dict[str, slice]) -> DataArray | None:
        tile_studies = [
            component_study.isel(indexers).load() for component_study in studies
        ]
        tile_thresholds = [
            _slice_eager_cftime_compound_threshold(threshold, indexers)
            for threshold in prepared_thresholds
        ]
        masks = [
            _compute_eager_cftime_compound_component_mask(
                tile_study,
                tile_threshold,
                resample_freq,
                climate_var.bootstrap,
            )
            for climate_var, tile_study, tile_threshold in zip(
                climate_vars,
                tile_studies,
                tile_thresholds,
                strict=True,
            )
        ]
        if any(mask is None for mask in masks):
            return None
        result = logical_link.compute(cast("list[DataArray]", masks))
        result.attrs = cast("list[DataArray]", masks)[0].attrs.copy()
        tile_study = tile_studies[0]
        return result.assign_coords(
            {dim: tile_study.coords[dim] for dim in tile_study.dims}
        )

    optimized_start = perf_counter()
    with ThreadPoolExecutor(max_workers=worker_count) as pool:
        tile_results = list(pool.map(compute_tile, tiles))
    if any(result is None for result in tile_results):
        return None
    concrete_results = cast("list[DataArray]", tile_results)
    if len(concrete_results) == 1:
        result = concrete_results[0]
    else:
        result = xr.combine_by_coords(
            [
                tile.to_dataset(name="__icclim_bootstrap_tile")
                for tile in concrete_results
            ],
            combine_attrs="override",
        )["__icclim_bootstrap_tile"]
    result.name = concrete_results[-1].name
    result.attrs.update(concrete_results[-1].attrs)
    if len(climate_vars) == 1:
        result.attrs.pop(REFERENCE_PERIOD_ID, None)
    _profile_bootstrap_inc("bootstrap_optimized_tile_count", len(tiles))
    _profile_bootstrap_add(
        "bootstrap_optimized_total_seconds",
        perf_counter() - optimized_start,
    )
    return _transpose_like_study(result, study)


def _compute_fast_tiled_bootstrap_spell_mask(
    climate_var: ClimateVariable,
    resample_freq: Frequency,
    max_cells: int,
    *,
    prepared_inputs_cache: dict[tuple, BootstrapPreparedInputs] | None = None,
) -> DataArray | None:
    from icclim._core.generic.bootstrap import (  # noqa: PLC0415
        bootstrap_array_dtype,
        compute_doy_percentile_bootstrap_union_exceedance_mask,
    )
    from icclim._core.generic.bootstrap_primitives import (  # noqa: PLC0415
        build_bootstrap_prepared_inputs,
    )

    optimized_start = perf_counter()
    tile_results: list[DataArray] = []
    threshold = climate_var.threshold
    if threshold is None:
        return None
    for tile_indexers in _iter_spatial_tiles(climate_var.studied_data, max_cells):
        tile_study = climate_var.studied_data.isel(tile_indexers)
        tile_threshold = _slice_threshold_for_tile(threshold, tile_indexers)
        prepared_inputs = None
        if prepared_inputs_cache is not None:
            cache_key = _bootstrap_tile_preparation_cache_key(
                tile_indexers,
                tile_threshold,
                resample_freq.pandas_freq,
            )
            prepared_inputs = prepared_inputs_cache.get(cache_key)
            if prepared_inputs is None:
                prepared_inputs = build_bootstrap_prepared_inputs(
                    tile_study,
                    tile_threshold,
                    resample_freq.pandas_freq,
                    dtype=bootstrap_array_dtype(tile_study),
                    prefer_file_reopen=True,
                )
                prepared_inputs_cache[cache_key] = prepared_inputs
        if prepared_inputs is None:
            prepared_inputs = build_bootstrap_prepared_inputs(
                tile_study,
                tile_threshold,
                resample_freq.pandas_freq,
                dtype=bootstrap_array_dtype(tile_study),
                prefer_file_reopen=True,
            )
        tile_result = compute_doy_percentile_bootstrap_union_exceedance_mask(
            tile_study,
            tile_threshold,
            resample_freq.pandas_freq,
            prepared_inputs=prepared_inputs,
        )
        if tile_result is None:
            return None
        tile_results.append(tile_result)
        _profile_bootstrap_inc("bootstrap_optimized_tile_count")
    if len(tile_results) == 1:
        result = tile_results[0]
    else:
        result = xr.combine_by_coords(
            [tile.to_dataset(name="__icclim_bootstrap_tile") for tile in tile_results],
            combine_attrs="override",
        )["__icclim_bootstrap_tile"]
    result.attrs.update(tile_results[-1].attrs)
    _profile_bootstrap_add(
        "bootstrap_optimized_total_seconds",
        perf_counter() - optimized_start,
    )
    result = _transpose_like_study(result, climate_var.studied_data)
    if all(
        climate_var.studied_data.sizes[dim] == 1
        for dim in climate_var.studied_data.dims
        if dim != "time"
    ):
        result = result.squeeze(drop=False)
    return result


def _compute_fast_tiled_bootstrap_mean_threshold(
    climate_var: ClimateVariable,
    threshold: PercentileThreshold,
    resample_freq: Frequency,
    max_cells: int,
) -> DataArray | None:
    from icclim._core.generic.bootstrap import (  # noqa: PLC0415
        compute_doy_percentile_bootstrap_mean_threshold,
    )

    tile_results: list[DataArray] = []
    for tile_indexers in _iter_spatial_tiles(climate_var.studied_data, max_cells):
        tile_study = climate_var.studied_data.isel(tile_indexers)
        tile_threshold = _slice_threshold_for_tile(threshold, tile_indexers)
        tile_result = compute_doy_percentile_bootstrap_mean_threshold(
            tile_study,
            tile_threshold,
            resample_freq.pandas_freq,
        )
        if tile_result is None:
            return None
        tile_results.append(tile_result)
        _profile_bootstrap_inc("bootstrap_optimized_tile_count")
    if len(tile_results) == 1:
        return tile_results[0]
    result = xr.combine_by_coords(
        [tile.to_dataset(name="__icclim_bootstrap_tile") for tile in tile_results],
        combine_attrs="override",
    )["__icclim_bootstrap_tile"]
    result.attrs.update(tile_results[-1].attrs)
    return result


def _compute_exact_tiled_bootstrap_spell_mask(
    climate_var: ClimateVariable,
    resample_freq: Frequency,
) -> DataArray | None:
    threshold = climate_var.threshold
    if threshold is None:
        return None
    from icclim._core.generic.threshold.percentile import (  # noqa: PLC0415
        PercentileThreshold,
    )

    if (
        not isinstance(threshold, PercentileThreshold)
        or not threshold.is_doy_per_threshold
    ):
        return None

    spell_capability = classify_doy_percentile_spell_bootstrap(
        climate_var,
        resample_freq,
    )
    if (
        not spell_capability.bootstrap_required
        or spell_capability.execution_kind
        != BootstrapExecutionKind.EXACT_TILED_BOOTSTRAP
    ):
        return None

    exact_tiled_start = perf_counter()
    max_cells = _get_safe_bootstrap_max_cells(
        climate_var.studied_data,
        threshold,
        resample_freq,
    )
    _profile_bootstrap_set("bootstrap_safe_max_tile_cells", max_cells)
    tile_results: list[DataArray] = []
    for tile_indexers in _iter_spatial_tiles(climate_var.studied_data, max_cells):
        tile_start = perf_counter()
        tile_study = climate_var.studied_data.isel(tile_indexers).load()
        tile_climate_var = _slice_climate_var_for_tile(
            climate_var,
            tile_indexers,
            tile_study=tile_study,
        )
        tile_exceedance_mask = _compute_exceedance_mask(
            study=tile_climate_var.studied_data,
            threshold=tile_climate_var.threshold,
            freq=resample_freq.pandas_freq,
            bootstrap=True,
        )
        if "percentiles" in tile_exceedance_mask.dims:
            tile_exceedance_mask = tile_exceedance_mask.squeeze("percentiles")
        tile_results.append(tile_exceedance_mask.load())
        _profile_bootstrap_inc("bootstrap_safe_tile_count")
        _profile_bootstrap_add(
            "bootstrap_safe_tile_seconds",
            perf_counter() - tile_start,
        )

    if len(tile_results) == 1:
        result = tile_results[0]
    else:
        result = xr.combine_by_coords(
            [tile.to_dataset(name="__icclim_bootstrap_tile") for tile in tile_results],
            combine_attrs="override",
        )["__icclim_bootstrap_tile"]
    result.attrs.update(tile_results[-1].attrs)
    result = result.transpose(*climate_var.studied_data.dims)
    result = result.fillna(False).astype(bool, copy=False)
    if all(
        climate_var.studied_data.sizes[dim] == 1
        for dim in climate_var.studied_data.dims
        if dim != "time"
    ):
        result = result.squeeze(drop=False)
    _profile_bootstrap_add(
        "bootstrap_safe_total_seconds",
        perf_counter() - exact_tiled_start,
    )
    return result


def _get_fast_bootstrap_max_cells(study: DataArray) -> int:
    if max_cells := os.environ.get("ICCLIM_BOOTSTRAP_FAST_TILE_CELLS"):
        return max(1, int(max_cells))
    max_mem = _parse_byte_size(
        os.environ.get(
            "ICCLIM_BOOTSTRAP_FAST_TILE_MEMORY",
            _DEFAULT_BOOTSTRAP_FAST_TILE_MEMORY,
        )
    )
    itemsize = getattr(study.dtype, "itemsize", 8)
    bytes_per_cell = max(1, study.sizes["time"]) * itemsize
    bytes_per_cell *= _BOOTSTRAP_FAST_MEMORY_FACTOR
    _profile_bootstrap_set("bootstrap_optimized_tile_memory_bytes", max_mem)
    _profile_bootstrap_set(
        "bootstrap_optimized_estimated_bytes_per_cell",
        bytes_per_cell,
    )
    max_cells = max(1, max_mem // bytes_per_cell)
    _profile_bootstrap_set("bootstrap_optimized_max_tile_cells", max_cells)
    return max_cells


def _get_safe_bootstrap_max_cells(
    study: DataArray,
    threshold: PercentileThreshold,
    resample_freq: Frequency,
) -> int:
    if max_cells := os.environ.get("ICCLIM_BOOTSTRAP_SAFE_TILE_CELLS"):
        return max(1, int(max_cells))
    max_mem = _parse_byte_size(
        os.environ.get(
            "ICCLIM_BOOTSTRAP_SAFE_TILE_MEMORY",
            _DEFAULT_BOOTSTRAP_SAFE_TILE_MEMORY,
        )
    )
    bytes_per_cell = _estimate_bootstrap_working_bytes_per_cell(
        study,
        threshold,
        resample_freq,
    )
    _profile_bootstrap_set("bootstrap_safe_tile_memory_bytes", max_mem)
    _profile_bootstrap_set("bootstrap_safe_estimated_bytes_per_cell", bytes_per_cell)
    return max(1, max_mem // bytes_per_cell)


def _estimate_bootstrap_working_bytes_per_cell(
    study: DataArray,
    threshold: PercentileThreshold,
    resample_freq: Frequency,
) -> int:
    clim = threshold.climatology_bounds(study)
    overlap_da = study.sel(time=slice(*clim))
    overlap_groups = overlap_da.resample(
        time=_get_bootstrap_freq(resample_freq.pandas_freq)
    ).groups
    n_bootstrap = max(1, len(overlap_groups) - 1)
    itemsize = getattr(study.dtype, "itemsize", 8)
    raw_bootstrap_bytes = max(1, overlap_da.sizes["time"]) * n_bootstrap * itemsize
    return raw_bootstrap_bytes * _BOOTSTRAP_SAFE_MEMORY_FACTOR


def _get_bootstrap_freq(freq: str) -> str:
    from xclim.core.calendar import parse_offset  # noqa: PLC0415

    _, base, start_anchor, anchor = parse_offset(freq)
    bfreq = "YS" if start_anchor else "YE"
    if base in ["A", "Y", "Q"] and anchor is not None:
        bfreq = f"{bfreq}-{anchor}"
    return bfreq


def _parse_byte_size(value: str) -> int:
    normalized = value.strip().lower().replace(" ", "")
    units = {
        "b": 1,
        "kb": 1000,
        "kib": 1024,
        "mb": 1000**2,
        "mib": 1024**2,
        "gb": 1000**3,
        "gib": 1024**3,
    }
    for unit, multiplier in sorted(
        units.items(), key=lambda item: len(item[0]), reverse=True
    ):
        if normalized.endswith(unit):
            return max(1, int(float(normalized.removesuffix(unit)) * multiplier))
    return max(1, int(float(normalized)))


def _iter_spatial_tiles(
    da: DataArray,
    max_cells: int,
) -> list[dict[str, slice]]:
    spatial_dims = [dim for dim in da.dims if dim != "time"]
    if not spatial_dims:
        return [{}]

    tile_lengths = {dim: da.sizes[dim] for dim in spatial_dims}
    product = 1
    for dim in spatial_dims:
        product *= tile_lengths[dim]
    while product > max_cells:
        dim = max(tile_lengths, key=tile_lengths.get)
        old = tile_lengths[dim]
        tile_lengths[dim] = max(1, old // 2)
        product = 1
        for value in tile_lengths.values():
            product *= value
        if tile_lengths[dim] == old:
            break

    tiles: list[dict[str, slice]] = [{}]
    for dim in spatial_dims:
        dim_tiles = [
            slice(start, min(start + tile_lengths[dim], da.sizes[dim]))
            for start in range(0, da.sizes[dim], tile_lengths[dim])
        ]
        tiles = [
            {**prefix, dim: dim_tile} for prefix in tiles for dim_tile in dim_tiles
        ]
    return tiles


def _slice_threshold_for_tile(
    threshold: PercentileThreshold,
    tile_indexers: dict[str, slice],
) -> PercentileThreshold:
    sliced = copy(threshold)
    if not threshold.is_ready:
        prepare_source = getattr(threshold, "_prepare_source_data", None)
        prepare_unit = getattr(threshold, "_prepare_output_unit", None)
        if prepare_source is not None:
            sliced.set_prepare_context(
                prepare_source.isel(tile_indexers),
                prepare_unit,
            )
        return sliced
    value = threshold.value
    value_indexers = {
        dim: indexer for dim, indexer in tile_indexers.items() if dim in value.dims
    }
    if value_indexers:
        sliced._prepared_value = value.isel(value_indexers)  # noqa: SLF001
    return sliced


def _slice_climate_var_for_tile(
    climate_var: ClimateVariable,
    tile_indexers: dict[str, slice],
    *,
    tile_study: DataArray | None = None,
) -> ClimateVariable:
    if tile_study is None:
        tile_study = climate_var.studied_data.isel(tile_indexers)
    threshold = climate_var.threshold
    if threshold is None:
        sliced_threshold = None
    else:
        from icclim._core.generic.threshold.percentile import (  # noqa: PLC0415
            PercentileThreshold,
        )

        if not isinstance(threshold, PercentileThreshold):
            msg = "Exact tiled spell bootstrap currently supports one percentile threshold"
            raise NotImplementedError(msg)
        sliced_threshold = _slice_threshold_for_tile(threshold, tile_indexers)
        if not sliced_threshold.is_ready:
            prepare_unit = getattr(sliced_threshold, "_prepare_output_unit", None)
            sliced_threshold.set_prepare_context(tile_study, prepare_unit)
    return replace(
        climate_var,
        studied_data=tile_study,
        threshold=sliced_threshold,
    )


def _transpose_like_study(result: DataArray, study: DataArray) -> DataArray:
    study_dims = tuple(dim for dim in study.dims if dim in result.dims)
    extra_dims = tuple(dim for dim in result.dims if dim not in study_dims)
    ordered_dims = (*study_dims, *extra_dims)
    return result.transpose(*ordered_dims)


def _is_memory_like_bootstrap_error(err: BaseException) -> bool:
    if isinstance(err, MemoryError):
        return True
    err_type = type(err).__name__.lower()
    memory_error_types = {
        "arraymemoryerror",
        "killedworker",
        "nannyrestart",
        "reschedule",
        "workerlost",
        "workerkilled",
    }
    if err_type in memory_error_types:
        return True
    message = str(err).lower()
    memory_fragments = (
        "failed to allocate",
        "killed worker",
        "malloc",
        "memoryerror",
        "out of memory",
        "oom",
        "worker died",
        "worker exceeded",
    )
    return any(fragment in message for fragment in memory_fragments)


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
    if len(climate_vars) != EXPECTED_RANGE_LEN:
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
    from xclim.core.units import convert_units_to  # noqa: PLC0415

    study = convert_units_to(study, ref, context="hydro")
    return study, ref


def _ensure_time_chunks_cover_window(da: DataArray, window: int) -> DataArray:
    """
    Make sure no Dask time chunk is shorter than a rolling window.

    Chunks the user (or the file) chose are kept as they are unless one of them
    is shorter than `window`, which a rolling operation cannot handle.  In that
    case the time axis is rechunked in even chunks, none shorter than `window`
    (or a single chunk when the series is shorter than two windows).
    """
    if da.chunks is None or "time" not in da.dims:
        return da
    sizes = da.chunksizes["time"]
    if min(sizes) >= window:
        return da
    total = sum(sizes)
    target = max(window, *sizes)
    n_chunks = max(1, total // target)
    base, extra = divmod(total, n_chunks)
    new_sizes = tuple(base + 1 if i < extra else base for i in range(n_chunks))
    return da.chunk({"time": new_sizes})


def _run_rolling_reducer(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    rolling_window_width: int,
    rolling_op: Callable[[DataArrayRolling], DataArray],  # sum | mean
    resampled_op: Callable[[DataArrayResample], DataArray],  # max | min
    date_event: bool,
    source_freq_delta: timedelta,
    extreme: str | None = None,
) -> DataArray:
    study, threshold = get_single_var(climate_vars)
    if _is_rate(study):
        from xclim.core.units import rate2amount  # noqa: PLC0415

        src_freq = check_freq(study, dim="time", strict=False)
        study = (
            _rate_to_amount_for_daily_subseries(study)
            if src_freq == "D"
            else rate2amount(study)
        )
    study = _ensure_time_chunks_cover_window(study, rolling_window_width)
    if threshold:
        exceedance_mask = _compute_threshold_exceedance_mask(
            climate_var=climate_vars[0],
            threshold=threshold,
            resample_freq=resample_freq,
            prepared_inputs_cache={},
        ).squeeze()
        study = study.where(exceedance_mask)
        study = _ensure_time_chunks_cover_window(study, rolling_window_width)
    study = rolling_op(study.rolling(time=rolling_window_width))
    resampled = study.resample(time=resample_freq.pandas_freq)
    if date_event:
        return _reduce_with_date_event(
            resampled=resampled,
            reducer=resampled_op,
            extreme=extreme,
            window=rolling_window_width,
            source_delta=source_freq_delta,
        )
    return resampled_op(resampled)


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
        exceedance_mask = _compute_threshold_exceedance_mask(
            climate_var=climate_vars[0],
            threshold=threshold,
            resample_freq=resample_freq,
            prepared_inputs_cache={},
        ).squeeze()
        filtered_study = study.where(exceedance_mask)
    else:
        filtered_study = study
    if must_convert_rate and _is_rate(filtered_study):
        from xclim.core.units import rate2amount  # noqa: PLC0415

        src_freq = check_freq(filtered_study, dim="time", strict=False)
        if src_freq == "D":
            filtered_study = _rate_to_amount_for_daily_subseries(filtered_study)
        else:
            if src_freq is not None:
                filtered_study = filtered_study.resample(time=src_freq).asfreq()
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


def _rate_to_amount_for_daily_subseries(filtered_study: DataArray) -> DataArray:
    from xclim.core.units import rate2amount  # noqa: PLC0415

    original_time = filtered_study.time
    first_time = original_time.values[0]
    if hasattr(first_time, "calendar"):
        synthetic_time = xr.date_range(
            start="2000-01-01",
            periods=filtered_study.sizes["time"],
            freq="D",
            use_cftime=True,
            calendar=first_time.calendar,
        )
    else:
        synthetic_time = date_range(
            start="2000-01-01",
            periods=filtered_study.sizes["time"],
            freq="D",
        )
    synthetic = filtered_study.assign_coords(time=synthetic_time)
    converted = rate2amount(synthetic)
    return converted.assign_coords(time=original_time)


def _compute_combined_exceedance_mask(
    climate_vars: list[ClimateVariable],
    resample_freq: Frequency,
    logical_link: LogicalLink,
    *,
    force_reference_bootstrap: bool = False,
) -> DataArray:
    exceedance_masks = []
    for climate_var in climate_vars:
        if climate_var.threshold is None:
            msg = "No threshold found"
            raise InvalidIcclimArgumentError(msg)
        exceedance_masks.append(
            _compute_threshold_exceedance_mask(
                climate_var=climate_var,
                threshold=climate_var.threshold,
                resample_freq=resample_freq,
                prepared_inputs_cache={},
                force_reference_bootstrap=force_reference_bootstrap,
            ).squeeze()
        )
    return logical_link(exceedance_masks)


def _compute_fallback_threshold_exceedance_mask(
    climate_var: ClimateVariable,
    threshold: Threshold,
    resample_freq: Frequency,
    bootstrap_required: bool,
) -> DataArray:
    from icclim._core.generic.threshold.percentile import (  # noqa: PLC0415
        PercentileThreshold,
    )

    if (
        isinstance(threshold, PercentileThreshold)
        and bootstrap_required
        and climate_var.studied_data.chunks is None
    ):
        from icclim._core.generic.bootstrap import (  # noqa: PLC0415
            compute_doy_percentile_bootstrap_union_mask_eager,
        )

        eager_mask = compute_doy_percentile_bootstrap_union_mask_eager(
            climate_var.studied_data,
            threshold,
            resample_freq.pandas_freq,
        )
        if eager_mask is not None:
            return eager_mask
    return _compute_exceedance_mask(
        study=climate_var.studied_data,
        threshold=threshold,
        freq=resample_freq.pandas_freq,
        bootstrap=bootstrap_required,
    )


def _compute_threshold_exceedance_mask(
    *,
    climate_var: ClimateVariable,
    threshold: Threshold,
    resample_freq: Frequency,
    prepared_inputs_cache: dict[tuple, BootstrapPreparedInputs] | None = None,
    force_reference_bootstrap: bool = False,
) -> DataArray:
    from icclim._core.generic.threshold.bounded import BoundedThreshold  # noqa: PLC0415
    from icclim._core.generic.threshold.percentile import (  # noqa: PLC0415
        PercentileThreshold,
    )

    if force_reference_bootstrap:
        return _compute_exceedance_mask(
            study=climate_var.studied_data,
            threshold=threshold,
            freq=resample_freq.pandas_freq,
            bootstrap=must_run_bootstrap(
                climate_var.studied_data,
                threshold,
                climate_var.bootstrap,
            ),
        )
    if isinstance(threshold, BoundedThreshold):
        left_mask = _compute_threshold_exceedance_mask(
            climate_var=replace(climate_var, threshold=threshold.left_threshold),
            threshold=threshold.left_threshold,
            resample_freq=resample_freq,
            prepared_inputs_cache=prepared_inputs_cache,
            force_reference_bootstrap=force_reference_bootstrap,
        )
        right_mask = _compute_threshold_exceedance_mask(
            climate_var=replace(climate_var, threshold=threshold.right_threshold),
            threshold=threshold.right_threshold,
            resample_freq=resample_freq,
            prepared_inputs_cache=prepared_inputs_cache,
            force_reference_bootstrap=force_reference_bootstrap,
        )
        return _transpose_like_study(
            threshold.logical_link.compute([left_mask.squeeze(), right_mask.squeeze()]),
            climate_var.studied_data,
        )

    bootstrap_required = must_run_bootstrap(
        climate_var.studied_data,
        threshold,
        climate_var.bootstrap,
    )
    if isinstance(threshold, PercentileThreshold) and threshold.is_doy_per_threshold:
        component_climate_var = replace(climate_var, threshold=threshold)
        capability = classify_doy_percentile_mask_bootstrap(
            component_climate_var,
            resample_freq,
        )
        if capability.uses_optimized_bootstrap:
            if hasattr(climate_var.studied_data.indexes.get("time"), "calendar"):
                eager_mask = _compute_eager_tiled_cftime_bootstrap_mask(
                    component_climate_var,
                    resample_freq,
                )
                if eager_mask is not None:
                    return eager_mask
            optimized_mask = _compute_fast_tiled_bootstrap_spell_mask(
                component_climate_var,
                resample_freq,
                _get_fast_bootstrap_max_cells(climate_var.studied_data),
                prepared_inputs_cache=prepared_inputs_cache,
            )
            if optimized_mask is not None:
                return optimized_mask
        if capability.uses_exact_tiled_bootstrap:
            exact_mask = _compute_exact_tiled_bootstrap_spell_mask(
                component_climate_var,
                resample_freq,
            )
            if exact_mask is not None:
                return exact_mask
    return _compute_fallback_threshold_exceedance_mask(
        climate_var,
        threshold,
        resample_freq,
        bootstrap_required,
    )


def _bootstrap_tile_preparation_cache_key(
    tile_indexers: dict[str, slice | int],
    threshold: Threshold,
    freq: str,
) -> tuple:
    from icclim._core.generic.threshold.percentile import (  # noqa: PLC0415
        PercentileThreshold,
    )

    if not isinstance(threshold, PercentileThreshold):
        return (freq, tuple(sorted(tile_indexers.items())))
    normalized_indexers = tuple(
        (
            dim,
            indexer
            if isinstance(indexer, int)
            else (indexer.start, indexer.stop, indexer.step),
        )
        for dim, indexer in sorted(tile_indexers.items())
    )
    return (
        freq,
        normalized_indexers,
        threshold.reference_period,
        threshold.doy_window_width,
        None
        if threshold.threshold_min_value is None
        else str(threshold.threshold_min_value),
        threshold.only_leap_years,
    )


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
    reducer: Callable[..., DataArray],
    source_delta: timedelta | None = None,
    window: int | None = None,
    extreme: str | None = None,
) -> DataArray:
    """Reduce periods to their extrema and attach the corresponding dates."""
    if extreme is None:
        if reducer == DataArrayResample.max:
            extreme = "max"
        elif reducer == DataArrayResample.min:
            extreme = "min"
        else:
            msg = f"Can't compute `date_event` due to unknown reducer: '{reducer}'"
            raise NotImplementedError(msg)
    if extreme not in ("max", "min"):
        msg = f"Can't compute `date_event` due to unknown reducer: '{extreme}'"
        raise NotImplementedError(msg)
    value = getattr(resampled, extreme)(dim="time")
    event_time = resampled.map(
        _extreme_event_date,
        args=(extreme,),
        shortcut=False,
    )
    if window is None:
        return _with_event_dates(value, event_date=event_time)
    start_time = (
        event_time - (window - 1) * source_delta
        if source_delta is not None
        else event_time
    )
    return _with_event_dates(
        value,
        event_date_start=start_time,
        event_date_end=event_time,
    )


def _time_first(da: DataArray) -> DataArray:
    """Put `time` first, as the per-period concatenation always did."""
    return da.transpose("time", ...)


def _with_event_dates(value: DataArray, **event_dates: DataArray) -> DataArray:
    """Attach event dates as coordinates, with time first.

    Event dates are dates, not measurements: they must not inherit the units or
    the standard name of the studied variable, which would also prevent xarray
    from encoding them as times when writing a NetCDF file.
    """
    clean = {}
    for name, original in event_dates.items():
        dates = original.copy(deep=False)
        dates.attrs = {}
        clean[name] = dates
    return _time_first(value.assign_coords(**clean))


def _extreme_event_date(sample: DataArray, extreme: str) -> DataArray:
    fill_value = (
        np.datetime64("NaT")
        if np.issubdtype(sample.time.dtype, np.datetime64)
        else None
    )
    return getattr(sample, f"idx{extreme}")(
        dim="time",
        fill_value=fill_value,
    )


def _count_occurrences_with_date(resampled: DataArrayResample) -> DataArray:
    occurrences = resampled.sum(dim="time")
    event_dates = resampled.map(_occurrence_event_dates, shortcut=False)
    return _with_event_dates(
        occurrences,
        event_date_start=event_dates.sel(event_date_bound="start", drop=True),
        event_date_end=event_dates.sel(event_date_bound="end", drop=True),
    )


def _occurrence_event_dates(sample: DataArray) -> DataArray:
    events = sample.fillna(False).astype(bool)
    event_dates = xr.apply_ufunc(
        _first_and_last_true_time,
        events,
        input_core_dims=[["time"]],
        output_core_dims=[["event_date_bound"]],
        kwargs={"time_values": events.time.to_numpy()},
        dask="parallelized",
        output_dtypes=[events.time.dtype],
        dask_gufunc_kwargs={
            "allow_rechunk": True,
            "output_sizes": {"event_date_bound": 2},
        },
    )
    return event_dates.assign_coords(
        event_date_bound=["start", "end"],
    )


def _first_and_last_true_time(
    values: np.ndarray,
    *,
    time_values: np.ndarray,
) -> np.ndarray:
    has_event = values.any(axis=-1)
    first = values.argmax(axis=-1)
    last = values.shape[-1] - 1 - values[..., ::-1].argmax(axis=-1)
    result = np.stack((time_values[first], time_values[last]), axis=-1)
    missing_time = (
        np.datetime64("NaT")
        if np.issubdtype(time_values.dtype, np.datetime64)
        else None
    )
    result[~has_event] = missing_time
    return result


def _consecutive_occurrences_with_dates(
    resampled: DataArrayResample,
    source_freq_delta: timedelta,
    run_index: str,
) -> DataArray:
    # Missing run lengths count as "no run" (0): a period without any run must
    # give 0, not NaN.
    longest_run = resampled.max(dim="time").fillna(0)
    anchor_time = resampled.map(_longest_run_event_date, shortcut=False)
    if anchor_time.dtype == object:
        # cftime dates (non-standard calendars) do not support array arithmetic with
        # a timedelta, and the arrays can be lazy: shift them element by element.
        if run_index == "last":
            end_time = _shift_cftime_dates(anchor_time, 1, source_freq_delta)
            start_time = _shift_cftime_dates(end_time, -longest_run, source_freq_delta)
        else:
            start_time = anchor_time
            end_time = _shift_cftime_dates(start_time, longest_run, source_freq_delta)
    elif run_index == "last":
        end_time = anchor_time + source_freq_delta
        start_time = end_time - (longest_run * cast("Any", source_freq_delta))
    else:
        start_time = anchor_time
        end_time = start_time + (longest_run * cast("Any", source_freq_delta))
    has_event = longest_run > 0
    return _with_event_dates(
        longest_run,
        event_date_start=start_time.where(has_event),
        event_date_end=end_time.where(has_event),
    )


def _shift_cftime_dates(
    dates: DataArray, steps: DataArray | int, delta: timedelta
) -> DataArray:
    """Return ``dates + steps * delta`` for an array of cftime dates, lazily."""
    # cftime adds Python timedeltas only (numpy 1.24 cannot add a timedelta64).
    py_delta = Timedelta(delta).to_pytimedelta()
    return xr.apply_ufunc(
        np.frompyfunc(lambda date, n: date + float(n) * py_delta, 2, 1),
        dates,
        steps,
        dask="parallelized",
        output_dtypes=[object],
    )


def _longest_run_event_date(sample: DataArray) -> DataArray:
    return sample.fillna(0).idxmax(dim="time")


def _to_percent(da: DataArray, sampling_freq: Frequency) -> DataArray:
    if sampling_freq == FrequencyRegistry.MONTH:
        period_length = da.time.dt.daysinmonth
    elif sampling_freq == FrequencyRegistry.YEAR:
        time_index = da.indexes.get("time")
        calendar = (
            CfCalendarRegistry.lookup(time_index.calendar)
            if isinstance(time_index, xr.CFTimeIndex)
            else None
        )
        if calendar is not None and calendar.days_in_year is not None:
            period_length = xr.full_like(da, calendar.days_in_year)
        else:
            period_length = xr.full_like(da, 1)
            leap_years = _is_leap_year(da)
            period_length[{"time": leap_years}] = 366
            period_length[{"time": ~leap_years}] = 365
    elif sampling_freq == FrequencyRegistry.AMJJAS:
        period_length = 183
    elif sampling_freq == FrequencyRegistry.ONDJFM:
        period_length = xr.full_like(da, 1)
        leap_years = _is_leap_year(da, year_offset=1)
        period_length[{"time": leap_years}] = 183
        period_length[{"time": ~leap_years}] = 182
    elif sampling_freq == FrequencyRegistry.DJF:
        period_length = xr.full_like(da, 1)
        leap_years = _is_leap_year(da)
        period_length[{"time": leap_years}] = 91
        period_length[{"time": ~leap_years}] = 90
    elif sampling_freq in [FrequencyRegistry.MAM, FrequencyRegistry.JJA]:
        period_length = 92
    elif sampling_freq == FrequencyRegistry.SON:
        period_length = 91
    else:
        bounds = _build_resampled_time_bounds(da, sampling_freq.pandas_freq)
        period_length = xr.DataArray(
            [Timedelta(end - start).days + 1 for start, end in bounds],
            dims="time",
            coords={"time": da.time},
        )
    da = da / period_length * 100
    da.attrs[UNITS_KEY] = PART_OF_A_WHOLE_UNIT
    return da


def _is_leap_year(da: DataArray, year_offset: int = 0) -> np.ndarray:
    time_index = da.indexes.get("time")
    years = da.time.dt.year + year_offset
    if isinstance(time_index, xr.CFTimeIndex):
        return CfCalendarRegistry.lookup(time_index.calendar).is_leap(years)
    return (years % 4 == 0) & ((years % 100 != 0) | (years % 400 == 0))


def _is_rate(query: Quantity | DataArray) -> bool:
    if isinstance(query, DataArray):
        from xclim.core.units import str2pint  # noqa: PLC0415

        query = str2pint(query.attrs[UNITS_KEY])
    return query.dimensionality.get("[time]", None) == -1


def check_freq(da: xr.DataArray, dim: str = "time", strict: bool = True) -> str | None:
    """
    Infer the sampling frequency of a DataArray along a given dimension.

    For daily climate data, always returns "D", even after seasonal slicing
    (which can break pandas' infer_freq). Falls back to pandas.infer_freq
    if not daily.
    """
    times = da[dim].to_numpy()
    if len(times) < EXPECTED_RANGE_LEN:
        return None

    # Compute deltas
    try:
        deltas = to_timedelta(np_diff(times))
    except Exception as err:
        if strict:
            msg = "[icclim] Cannot compute time deltas"
            raise ValueError(msg) from err
        return None

    median_delta = Timedelta(np_median(deltas))

    # If ~daily, force "D"
    if np_abs(median_delta / Timedelta("1D") - 1) < FREQ_DELTA_TOLERANCE:
        return "D"

    # Otherwise, try pandas inference
    try:
        return infer_freq(
            date_range(start=times[0], periods=len(times), freq=median_delta)
        )
    except Exception as err:
        if strict:
            msg = "[icclim] Unable to infer frequency"
            raise ValueError(msg) from err
        return None


def _safe_to_agg_units(*args, **kwargs) -> DataArray:
    import inspect  # noqa: PLC0415

    from xclim.core.units import to_agg_units  # noqa: PLC0415

    supported_kwargs = {
        key: value
        for key, value in kwargs.items()
        if key in inspect.signature(to_agg_units).parameters
    }
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            category=UserWarning,
            message=".*Unable to find the sampling frequency.*",
        )
        return to_agg_units(*args, **supported_kwargs)
