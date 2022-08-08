from __future__ import annotations

from functools import reduce
from typing import Callable
from warnings import warn

import dask.array
import numpy as np
import xarray
from xarray.core.dataarray import DataArray
from xarray.core.rolling import DataArrayRolling
from xclim.core.bootstrapping import percentile_bootstrap
from xclim.core.calendar import percentile_doy, resample_doy
from xclim.core.units import convert_units_to, to_agg_units
from xclim.indices.run_length import longest_run

from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.models.constants import (
    PERCENTILE_THRESHOLD_STAMP,
    PERCENTILES_COORD,
    PRECIPITATION,
    TEMPERATURE,
    UNITS_ATTRIBUTE_KEY,
    WET_DAY_THRESHOLD,
)
from icclim.models.logical_link import LogicalLink, LogicalLinkRegistry
from icclim.models.operator import Operator
from icclim.models.user_index_config import ExtremeMode, ExtremeModeRegistry
from icclim.user_indices.stat import (
    get_first_occurrence_index,
    get_longest_run_start_index,
)

__all__ = [
    "max",
    "min",
    "sum",
    "mean",
    "count_events",
    "max_consecutive_event_count",
    "run_mean",
    "run_sum",
    "anomaly",
]


def max(
    da: DataArray,
    in_base_da: DataArray | None = None,
    coef: float | None = None,
    logical_operation: Operator | None = None,
    threshold: str | float | int | None = None,
    freq: str = "MS",
    date_event: bool = False,
    var_type: str | None = None,
    save_percentile=False,
) -> DataArray:
    result = _apply_coef(coef, da)
    result = _filter_by_threshold(
        result,
        in_base_da,
        logical_operation,
        threshold,
        freq,
        var_type,
        save_percentile,
    )
    resampled = result.resample(time=freq)
    if date_event:
        return _reduce_with_date_event(
            resampled, lambda x: x.argmax("time")  # type:ignore
        )
    else:
        return resampled.max(dim="time")


def min(
    da: DataArray,
    in_base_da: DataArray | None = None,
    coef: float = None,
    logical_operation: Operator = None,
    threshold: str | float | int | None = None,
    freq: str = "MS",
    date_event: bool = False,
    var_type: str = None,
    save_percentile=False,
) -> DataArray:
    result = _apply_coef(coef, da)
    result = _filter_by_threshold(
        result,
        in_base_da,
        logical_operation,
        threshold,
        freq,
        var_type,
        save_percentile,
    )
    resampled = result.resample(time=freq)
    if date_event:
        return _reduce_with_date_event(
            resampled, lambda x: x.argmin("time")  # type:ignore
        )
    else:
        return resampled.min(dim="time")


def sum(
    da: DataArray,
    in_base_da: DataArray | None = None,
    coef: float = None,
    logical_operation: Operator = None,
    threshold: str | float | int | None = None,
    var_type: str = None,
    freq: str = "MS",
    save_percentile=False,
) -> DataArray:
    result = _apply_coef(coef, da)
    result = _filter_by_threshold(
        result,
        in_base_da,
        logical_operation,
        threshold,
        freq,
        var_type,
        save_percentile,
    )
    return result.resample(time=freq).sum(dim="time")


def mean(
    da: DataArray,
    in_base_da: DataArray | None = None,
    coef: float = None,
    logical_operation: Operator = None,
    threshold: str | float | int | None = None,
    var_type: str = None,
    freq: str = "MS",
    save_percentile=False,
) -> DataArray:
    result = _apply_coef(coef, da)
    result = _filter_by_threshold(
        result,
        in_base_da,
        logical_operation,
        threshold,
        freq,
        var_type,
        save_percentile,
    )
    return result.resample(time=freq).mean(dim="time")


def count_events(
    logical_operation: list[Operator],
    thresholds: list[float | str],
    das: list[DataArray],
    in_base_das: list[DataArray | None],
    link_logical_operations: LogicalLink = None,
    coef: float = None,
    var_type: str = None,
    freq: str = "MS",
    date_event: bool = False,
    save_percentile: bool = False,
) -> DataArray:
    percentiles = []
    for i, threshold in enumerate(thresholds):
        if isinstance(threshold, str) and len(in_base_das) > 0:
            in_base_da = in_base_das[i]
            if in_base_da is not None:
                percentiles.append(_get_percentiles(threshold, var_type, in_base_da))
    acc = []
    for i, da in enumerate(das):
        result = _apply_coef(coef, da)
        if len(percentiles) > 0:
            result = _threshold_compare_on_percentiles(
                da=result,
                percentiles=percentiles[i],
                operator=logical_operation[i],
                freq=freq,
                bootstrap=_is_bootstrappable(var_type),
            )
            if save_percentile:
                result.coords[f"percentile_{thresholds[i]}"] = resample_doy(
                    percentiles[i], result
                )
        else:
            result = logical_operation[i](result, thresholds[i])  # type:ignore
        acc.append(result)
    if len(acc) == 1:
        result = acc[0]
    elif link_logical_operations == LogicalLinkRegistry.LOGICAL_AND:
        result = reduce(np.logical_and, acc, True)  # type:ignore
    elif link_logical_operations == LogicalLinkRegistry.LOGICAL_OR:
        result = reduce(np.logical_or, acc, False)  # type:ignore
    else:
        raise NotImplementedError()
    resampled = result.resample(time=freq)
    if date_event:
        return _get_count_events_date_event(resampled)
    return resampled.sum(dim="time")


def max_consecutive_event_count(
    da: DataArray,
    logical_operation: Operator,
    in_base_da: DataArray | None = None,
    threshold: str | float | int | None = None,
    coef: float = None,
    freq: str = "MS",
    date_event: bool = False,
    var_type: str | None = None,
    save_percentile=False,
) -> DataArray:
    result = _apply_coef(coef, da)
    if in_base_da is not None and isinstance(threshold, str):
        per = _get_percentiles(threshold, var_type, in_base_da)
        result = _threshold_compare_on_percentiles(
            da=da,
            percentiles=per,
            operator=logical_operation,
            freq=freq,
            bootstrap=_is_bootstrappable(var_type),
        )
        if save_percentile:
            result.coords[PERCENTILES_COORD] = resample_doy(per, result)
    elif isinstance(threshold, float) or isinstance(threshold, int):
        result = logical_operation.compute(da, threshold)
    resampled = result.resample(time=freq)
    if not date_event:
        return resampled.map(longest_run, dim="time")
    acc: list[DataArray] = []
    for label, value in resampled:
        run_length = longest_run(value, dim="time")
        index = get_longest_run_start_index(value, dim="time")
        start = value[index.astype(int)].time
        time_shift = run_length * np.timedelta64(1, "D")
        end = start + time_shift
        coords = dict(
            time=label,
            lat=value.lat,
            lon=value.lon,
            event_date_start=start,
            event_date_end=end,
        )
        acc.append(DataArray(data=run_length, dims=["lat", "lon"], coords=coords))
    result = xarray.concat(acc, "time")
    return to_agg_units(result, da, "count")


def run_mean(
    da: DataArray,
    extreme_mode: ExtremeMode,
    window_width: int,
    coef: float = None,
    freq: str = "MS",
    date_event: bool = False,
) -> DataArray:
    return _run_aggregator(
        da=da,
        extreme_mode=extreme_mode,
        window_width=window_width,
        coef=coef,
        freq=freq,
        date_event=date_event,
        aggregator=lambda data: data.mean(),
    )


def run_sum(
    da: DataArray,
    extreme_mode: ExtremeMode,
    window_width: int,
    coef: float = None,
    freq: str = "MS",
    date_event: bool = False,
) -> DataArray:
    return _run_aggregator(
        da=da,
        extreme_mode=extreme_mode,
        window_width=window_width,
        coef=coef,
        freq=freq,
        date_event=date_event,
        aggregator=lambda data: data.sum(),
    )


def anomaly(da_ref: DataArray, da: DataArray, percent: bool) -> DataArray:
    ref_mean = da_ref.mean(dim="time")
    result: DataArray = da.mean(dim="time") - ref_mean
    result._copy_attrs_from(da_ref)
    if percent:
        result = result / ref_mean * 100
        result.attrs[UNITS_ATTRIBUTE_KEY] = "%"
    return result


def _apply_coef(coef: float | None, da: DataArray) -> DataArray:
    if coef is not None:
        return da * coef
    return da


def _filter_by_threshold(
    da: DataArray,
    in_base_da: DataArray | None,
    operator: Operator | None,
    threshold: str | float | int | None,
    freq: str,
    var_type: str | None,
    save_percentile: bool,
) -> DataArray:
    if threshold is None and operator is None:
        return da
    if isinstance(threshold, str):
        if in_base_da is None:
            raise NotImplementedError(
                "When threshold type is str for percentiles, a in_base must be provided"
            )
        per = _get_percentiles(threshold, var_type, in_base_da)
        result = _filter_by_logical_op_on_percentile(
            da=da,
            percentiles=_get_percentiles(threshold, var_type, in_base_da),
            operator=operator,
            freq=freq,
            bootstrap=_is_bootstrappable(var_type),
        )
        if save_percentile:
            result.coords[PERCENTILES_COORD] = resample_doy(per, result)
    elif (
        isinstance(threshold, float) or isinstance(threshold, int)
    ) and operator is not None:
        result = da.where(operator.compute(da, threshold))
    else:
        raise NotImplementedError(
            "threshold type must be on of [str, int, float] and logical_operation must "
            "a Operator instance"
        )
    if len(result) == 0:
        raise InvalidIcclimArgumentError(
            f"The dataset has been emptied by filtering with " f"{operator}{threshold}."
        )
    return result


@percentile_bootstrap
def _filter_by_logical_op_on_percentile(
    da: DataArray,
    percentiles: DataArray | None,
    operator: Operator | None,
    freq: str = "MS",  # noqa  # used by percentile_bootstrap
    bootstrap: bool = False,  # used by percentile_bootstrap
) -> DataArray:
    if operator is not None and percentiles is not None:
        percentiles = resample_doy(percentiles, da)
        mask = operator.compute(da, percentiles)
        result = da.where(mask, drop=True)
        if bootstrap:
            result = da.expand_dims(_bootstrap=result._bootstrap)
        return result
    return da


@percentile_bootstrap
def _threshold_compare_on_percentiles(
    da: DataArray,
    percentiles: DataArray,
    operator: Operator,
    freq: str = "MS",  # noqa  # used by percentile_bootstrap
    bootstrap: bool = False,  # noqa # used by percentile_bootstrap
) -> DataArray:
    percentiles = resample_doy(percentiles, da)
    return operator.compute(da, percentiles)


def _get_percentiles(
    thresh: str, var_type: str | None, in_base_da: DataArray
) -> DataArray:
    if thresh.find(PERCENTILE_THRESHOLD_STAMP) == -1:
        raise InvalidIcclimArgumentError(
            "Percentile threshold not properly formatted."
            " Use p as a prefix or suffix of the value for example 90p or p90."
            " For non percentile threshold use a float instead of a string"
        )
    per = float(thresh.replace(PERCENTILE_THRESHOLD_STAMP, ""))
    da_per = in_base_da
    if var_type == PRECIPITATION:
        da_per = convert_units_to(in_base_da, "mm/d")
        da_per = da_per.where(da_per > WET_DAY_THRESHOLD, drop=True)
    percentiles = percentile_doy(arr=da_per, per=per).sel(percentiles=per)
    return percentiles


def _run_aggregator(
    da: DataArray,
    extreme_mode: ExtremeMode,
    window_width: int,
    aggregator: Callable[[DataArrayRolling], DataArray],
    coef: float = None,
    freq: str = "MS",
    date_event: bool = False,
) -> DataArray:
    result = _apply_coef(coef, da)
    result = result.rolling(time=window_width)
    resampled = aggregator(result).resample(time=freq)
    if extreme_mode == ExtremeModeRegistry.MIN:
        if date_event:
            return _reduce_with_date_event(
                resampled,
                lambda x: x.argmin("time"),  # type:ignore
                window=window_width,
            )
        else:
            return resampled.min(dim="time")
    elif extreme_mode == ExtremeModeRegistry.MAX:
        if date_event:
            return _reduce_with_date_event(
                resampled,
                lambda x: x.argmax("time"),
                window=window_width,
            )
        else:
            return resampled.max(dim="time")
    else:
        raise NotImplementedError()


def _reduce_with_date_event(
    resampled: DataArray,
    reducer: Callable[[DataArray], DataArray],
    window: int | None = None,
) -> DataArray:
    acc: list[DataArray] = []
    for label, value in resampled:
        reduced_result = value.isel(time=reducer(value))
        if window is not None:
            coords = dict(
                time=label,
                lat=value.lat,
                lon=value.lon,
                event_date_start=reduced_result.time,
                event_date_end=reduced_result.time + np.timedelta64(window, "D"),
            )
        else:
            coords = dict(
                time=label,
                lat=value.lat,
                lon=value.lon,
                event_date=reduced_result.time,
            )
        acc.append(DataArray(data=reduced_result, dims=["lat", "lon"], coords=coords))
    return xarray.concat(acc, "time")


def _get_count_events_date_event(resampled):
    if isinstance(resampled, dask.array.Array):
        warn("Computing event_date_start/end when using Dask arrays can be slow.")
    acc: list[DataArray] = []
    for label, sample in resampled:
        # Fixme probably not safe to compute on huge dataset,
        #  it should be fixed with
        #  https://github.com/pydata/xarray/issues/2511
        sample = sample.compute()
        first = sample.isel(time=get_first_occurrence_index(sample)).time
        value_reversed_time = sample[::-1, :, :]
        last = sample.isel(time=get_first_occurrence_index(value_reversed_time)).time
        acc.append(
            DataArray(
                data=sample.sum(dim="time"),
                dims=["lat", "lon"],
                coords=dict(
                    time=label,
                    lat=sample.lat,
                    lon=sample.lon,
                    event_date_start=first,
                    event_date_end=last,
                ),
            )
        )
    return xarray.concat(acc, "time")


def _is_bootstrappable(var_type: str):
    return var_type == TEMPERATURE
