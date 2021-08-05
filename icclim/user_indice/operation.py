from enum import Enum
from functools import reduce
from typing import Any, Callable, List, Optional, Union

import numpy as np
import xarray
from xarray.core.dataarray import DataArray
from xclim.core.bootstrapping import percentile_bootstrap
from xclim.core.calendar import percentile_doy, resample_doy
from xclim.core.units import convert_units_to, to_agg_units
from xclim.indices.run_length import longest_run

from icclim.user_indice.stat import get_first_occurrence, get_longest_run_start_index
from icclim.user_indice.user_indice import (
    PERCENTILE_STAMP,
    PRECIPITATION,
    TEMPERATURE,
    WET_DAY_THRESHOLD,
    ExtremeMode,
    LinkLogicalOperation,
    LogicalOperation,
)


def max(
    da: DataArray,
    in_base_da: Optional[DataArray] = None,
    coef: Optional[float] = None,
    logical_operation: Optional[LogicalOperation] = None,
    threshold: Optional[Union[str, float, int]] = None,
    freq: str = "MS",
    date_event: bool = False,
    var_type: Optional[str] = None,
) -> DataArray:
    result = _apply_coef(coef, da)
    result = _filter_by_threshold(
        result, in_base_da, logical_operation, threshold, freq, var_type
    )
    resampled = result.resample(time=freq)
    if date_event:
        return _reduce_with_date_event(
            resampled, lambda x: x.argmax("time", keep_attrs=True)  # type:ignore
        )
    else:
        return result.max(dim="time", keep_attrs=True)


def min(
    da: DataArray,
    in_base_da: Optional[DataArray] = None,
    coef: float = None,
    logical_operation: LogicalOperation = None,
    threshold: Optional[Union[str, float, int]] = None,
    freq: str = "MS",
    date_event: bool = False,
    var_type: str = None,
) -> DataArray:
    result = _apply_coef(coef, da)
    result = _filter_by_threshold(
        result, in_base_da, logical_operation, threshold, freq, var_type
    )
    resampled = result.resample(time=freq)
    if date_event:
        return _reduce_with_date_event(
            resampled, lambda x: x.argmin("time", keep_attrs=True)  # type:ignore
        )
    else:
        return result.min(dim="time", keep_attrs=True)


def sum(
    da: DataArray,
    in_base_da: Optional[DataArray] = None,
    coef: float = None,
    logical_operation: LogicalOperation = None,
    threshold: Optional[Union[str, float, int]] = None,
    var_type: str = None,
    freq: str = "MS",
) -> DataArray:
    result = _apply_coef(coef, da)
    result = _filter_by_threshold(
        result, in_base_da, logical_operation, threshold, freq, var_type
    )
    return result.resample(time=freq).sum(dim="time", keep_attrs=True)


def mean(
    da: DataArray,
    in_base_da: Optional[DataArray] = None,
    coef: float = None,
    logical_operation: LogicalOperation = None,
    threshold: Optional[Union[str, float, int]] = None,
    var_type: str = None,
    freq: str = "MS",
) -> DataArray:
    result = _apply_coef(coef, da)
    result = _filter_by_threshold(
        result, in_base_da, logical_operation, threshold, freq, var_type
    )
    return result.resample(time=freq).mean(dim="time", keep_attrs=True)


def count_events(
    logical_operation: List[LogicalOperation],
    thresholds: List[Union[float, str]],
    das: List[DataArray],
    in_base_das: List[Optional[DataArray]],
    link_logical_operations: LinkLogicalOperation = None,
    coef: float = None,
    var_type: str = None,
    freq: str = "MS",
    date_event: bool = False,
) -> DataArray:
    percentiles = []
    for i, threshold in enumerate(thresholds):
        if isinstance(threshold, str) and len(in_base_das) > 0:
            in_base_da = in_base_das[i]
            if in_base_da is not None:
                percentiles.append(_get_percentiles(threshold, var_type, in_base_da))
    acc = []
    for i, da in enumerate(das):
        result: DataArray = _apply_coef(coef, da)
        if len(percentiles) > 0:
            result = _threshold_compare_on_percentiles(
                da=result,
                percentiles=percentiles[i],
                logical_operation=logical_operation[i],
                freq=freq,
                bootstrap=is_bootstrappable(var_type),
            )
        else:
            result = logical_operation[i].compute(result, thresholds[i])  # type:ignore
        acc.append(result)
    if len(acc) == 1:
        result = acc[0]
    elif link_logical_operations == LinkLogicalOperation.AND_STAMP:
        result = reduce(np.logical_and, acc, True)  # type:ignore
    elif link_logical_operations == LinkLogicalOperation.OR_STAMP:
        result = reduce(np.logical_or, acc, False)  # type:ignore
    else:
        raise NotImplementedError()
    resampled = result.resample(time=freq)
    if not date_event:
        return resampled.sum(dim="time")
    acc: List[DataArray] = []
    for label, value in resampled:
        first = value.isel(time=get_first_occurrence(value)).time
        value_reversed_time = value[::-1, :, :]
        last = value.isel(time=get_first_occurrence(value_reversed_time)).time
        acc.append(
            DataArray(
                data=value.sum(dim="time"),
                dims=["lat", "lon"],
                coords=dict(
                    time=label,
                    lat=value.lat,
                    lon=value.lon,
                    event_date_start=first,
                    event_date_end=last,
                ),
            )
        )
    return xarray.concat(acc, "time")


def is_bootstrappable(var_type):
    return var_type == TEMPERATURE


def max_consecutive_event_count(
    da: DataArray,
    logical_operation: LogicalOperation,
    in_base_da: Optional[DataArray] = None,
    threshold: Optional[Union[str, float, int]] = None,
    coef: float = None,
    freq: str = "MS",
    date_event: bool = False,
    var_type: Optional[str] = None,
) -> DataArray:
    result = _apply_coef(coef, da)
    if in_base_da is not None and isinstance(threshold, str):
        result = threshold_compare_on_percentiles(
            da=da,
            percentiles=_get_percentiles(threshold, var_type, in_base_da),
            logical_operation=logical_operation,
            freq=freq,
            bootstrap=is_bootstrappable(var_type),
        )
    elif isinstance(threshold, float) or isinstance(threshold, int):
        result = logical_operation.compute(da, threshold)
    resampled = result.resample(time=freq)
    if not date_event:
        return resampled.map(longest_run, dim="time")
    acc: List[DataArray] = []
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
        aggregator=lambda da: da.mean(),
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
        aggregator=lambda da: da.sum(),
    )


def anomaly(da_ref: DataArray, da: DataArray, percent: bool) -> DataArray:
    ref_mean = da_ref.mean(dim="time")
    result: DataArray = da.mean(dim="time") - ref_mean
    result._copy_attrs_from(da_ref)
    if percent:
        result = result / ref_mean * 100
        result.attrs["units"] = "%"
    return result


def _apply_coef(coef: Optional[float], da: DataArray) -> DataArray:
    if coef is not None:
        return da * coef
    return da


def _filter_by_threshold(
    da: DataArray,
    in_base_da: Optional[DataArray],
    logical_operation: Optional[LogicalOperation],
    threshold: Optional[Union[str, float, int]],
    freq: str,
    var_type: Optional[str],
) -> DataArray:
    if threshold is None and logical_operation is None:
        return da
    if isinstance(threshold, str) and in_base_da is not None:
        return _filter_by_logical_op_on_percentile(
            da=da,
            percentiles=_get_percentiles(threshold, var_type, in_base_da),
            logical_operation=logical_operation,
            freq=freq,
            bootstrap=is_bootstrappable(var_type),
        )
    elif (
        isinstance(threshold, float) or isinstance(threshold, int)
    ) and logical_operation is not None:
        return da.where(logical_operation.compute(da, threshold), drop=True)
    else:
        raise NotImplementedError(
            "threshold must be on of [str, int, float] and logical_operation must a LogicalOperation instance"
        )


@percentile_bootstrap
def _filter_by_logical_op_on_percentile(
    da: DataArray,
    percentiles: Optional[DataArray],
    logical_operation: Optional[LogicalOperation],
    freq: str = "MS",  # used by percentile_bootstrap
    bootstrap: bool = False,  # used by percentile_bootstrap
) -> DataArray:
    if logical_operation is not None and percentiles is not None:
        percentiles = resample_doy(percentiles, da)
        filtered = logical_operation.compute(da, percentiles)
        filtered = filtered.where(filtered, drop=True)
        # if bootstrap: # TODO uncomment once fixed on xclim
        result = da.expand_dims(_bootstrap=filtered._bootstrap)
        #  end if
        return result.sel(time=filtered.time)
    return da


@percentile_bootstrap
def _threshold_compare_on_percentiles(
    da: DataArray,
    percentiles: DataArray,
    logical_operation: LogicalOperation,
    freq: str = "MS",  # used by percentile_bootstrap
    bootstrap: bool = False,  # used by percentile_bootstrap
) -> DataArray:
    percentiles = resample_doy(percentiles, da)
    return logical_operation.compute(da, percentiles)


def _get_percentiles(
    thresh: str, var_type: Optional[str], in_base_da: DataArray
) -> DataArray:
    if thresh.find(PERCENTILE_STAMP) == -1:
        raise Exception(
            # TODO create a UserInputException
            "Percentile threshold not properly formatted. Use p as a prefix or suffix of the value for example 90p or p90. For non percentile threshold use a float instead of a string"
        )
    per = float(thresh.replace(PERCENTILE_STAMP, ""))
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
    aggregator: Callable[[Any], DataArray],  # Any should be DataArrayRolling
    coef: float = None,
    freq: str = "MS",
    date_event: bool = False,
) -> DataArray:
    result = _apply_coef(coef, da)
    result = result.rolling(time=window_width)
    resampled = aggregator(result).resample(time=freq)
    if extreme_mode == ExtremeMode.MIN:
        if date_event:
            return _reduce_with_date_event(
                resampled,
                lambda x: x.argmin("time", keep_attrs=True),  # type:ignore
                window=window_width,
            )
        else:
            return resampled.min(dim="time")
    elif extreme_mode == ExtremeMode.MAX:
        if date_event:
            return _reduce_with_date_event(
                resampled,
                lambda x: x.argmax("time", keep_attrs=True),  # type:ignore
                window=window_width,
            )
        else:
            return resampled.max(dim="time")
    else:
        raise NotImplementedError()


@percentile_bootstrap
def threshold_compare_on_percentiles(
    da: DataArray,
    percentiles: DataArray,
    logical_operation: LogicalOperation,
    freq: str = "MS",
    bootstrap: bool = False,
) -> DataArray:
    percentiles = resample_doy(percentiles, da)
    return logical_operation.compute(da, percentiles)


def _reduce_with_date_event(
    resampled: DataArray,
    reducer: Callable[[DataArray], DataArray],
    window: Optional[int] = None,
) -> DataArray:
    acc: List[DataArray] = []
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
