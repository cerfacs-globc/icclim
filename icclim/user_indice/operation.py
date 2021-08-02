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

from icclim.models.indice_config import CfVariable
from icclim.user_indice.user_indice import (
    PRECIPITATION,
    TEMPERATURE,
    ExtremeMode,
    LinkLogicalOperation,
    LogicalOperation,
    UserIndiceConfig,
)

PERCENTILE_STAMP = "p"
WET_DAY_THRESHOLD = 1  # 1mm


class CalcOperation(Enum):
    MAX = "max"
    MIN = "min"
    SUM = "sum"
    MEAN = "mean"
    EVENT_COUNT = "nb_event"
    MAX_NUMBER_OF_CONSECUTIVE_EVENTS = "max_nb_consecutive_events"
    RUN_MEAN = "run_mean"
    RUN_SUM = "run_sum"
    ANOMALY = "anomaly"


def user_indice_max(
    da: DataArray,
    in_base_da: Optional[DataArray] = None,
    coef: Optional[float] = None,
    logical_operation: Optional[LogicalOperation] = None,
    threshold: Optional[Union[str, float]] = None,
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


def user_indice_min(
    da: DataArray,
    in_base_da: Optional[DataArray] = None,
    coef: float = None,
    logical_operation: LogicalOperation = None,
    threshold: Optional[Union[str, float]] = None,
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


def user_indice_sum(
    da: DataArray,
    in_base_da: Optional[DataArray] = None,
    coef: float = None,
    logical_operation: LogicalOperation = None,
    threshold: Optional[Union[str, float]] = None,
    var_type: str = None,
    freq: str = "MS",
):
    result = _apply_coef(coef, da)
    result = _filter_by_threshold(
        result, in_base_da, logical_operation, threshold, freq, var_type
    )
    return result.resample(time=freq).sum(dim="time", keep_attrs=True)


def user_indice_mean(
    da: DataArray,
    in_base_da: Optional[DataArray] = None,
    coef: float = None,
    logical_operation: LogicalOperation = None,
    threshold: Optional[Union[str, float]] = None,
    var_type: str = None,
    freq: str = "MS",
):
    result = _apply_coef(coef, da)
    result = _filter_by_threshold(
        result, in_base_da, logical_operation, threshold, freq, var_type
    )
    return result.resample(time=freq).mean(dim="time", keep_attrs=True)


def user_indice_count_events(
    logical_operation: List[LogicalOperation],
    thresholds: List[Union[float, str]],
    das: List[DataArray],
    in_base_das: List[Optional[DataArray]],
    link_logical_operations: LinkLogicalOperation = None,
    coef: float = None,
    var_type: str = None,
    freq: str = "MS",
    date_event: bool = False,
):
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
        result = reduce(np.logical_and, acc, True)
    elif link_logical_operations == LinkLogicalOperation.OR_STAMP:
        result = reduce(np.logical_or, acc, False)
    else:
        raise NotImplementedError()
    return result.resample(time=freq).sum(dim="time")


def is_bootstrappable(var_type):
    return var_type == TEMPERATURE


def user_indice_max_consecutive_event_count(
    da: DataArray,
    logical_operation: LogicalOperation,
    in_base_da: Optional[DataArray] = None,
    threshold: Optional[Union[str, float]] = None,
    coef: float = None,
    freq: str = "MS",
    date_event: bool = False,
    var_type: Optional[str] = None,
):
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
    result = result.resample(time=freq).map(longest_run, dim="time")
    return to_agg_units(result, da, "count")


def user_indice_run_mean(
    da: DataArray,
    extreme_mode: ExtremeMode,
    window_width: int,
    coef: float = None,
    freq: str = "MS",
    date_event: bool = False,
):
    return _user_indice_run_aggregator(
        da=da,
        extreme_mode=extreme_mode,
        window_width=window_width,
        coef=coef,
        freq=freq,
        date_event=date_event,
        aggregator=lambda da: da.mean(),
    )


def user_indice_run_sum(
    da: DataArray,
    extreme_mode: ExtremeMode,
    window_width: int,
    coef: float = None,
    freq: str = "MS",
    date_event: bool = False,
):
    return _user_indice_run_aggregator(
        da=da,
        extreme_mode=extreme_mode,
        window_width=window_width,
        coef=coef,
        freq=freq,
        date_event=date_event,
        aggregator=lambda da: da.sum(),
    )


def user_indice_anomaly(da_ref: DataArray, da: DataArray, percent: bool):
    ref_mean = da_ref.mean(dim="time")
    result: DataArray = da.mean(dim="time") - ref_mean
    result._copy_attrs_from(da_ref)
    if percent:
        result = result / ref_mean * 100
        result.attrs["units"] = "%"
    return result


def compute_user_indice(indice: UserIndiceConfig) -> DataArray:
    if indice.calc_operation == CalcOperation.MAX.value:
        # TODO check thresh is float or str, cfvars length is 1
        return user_indice_max(
            da=indice.cf_vars[0].da,
            in_base_da=indice.cf_vars[0].in_base_da,
            coef=indice.coef,
            logical_operation=indice.logical_operation,
            threshold=indice.thresh,
            freq=indice.freq.panda_freq,
            date_event=indice.date_event,
        )
    elif indice.calc_operation == CalcOperation.MIN.value:
        return user_indice_min(
            da=indice.cf_vars[0].da,
            in_base_da=indice.cf_vars[0].in_base_da,
            coef=indice.coef,
            logical_operation=indice.logical_operation,
            threshold=indice.thresh,
            freq=indice.freq.panda_freq,
            date_event=indice.date_event,
        )
    elif indice.calc_operation == CalcOperation.MEAN.value:
        return user_indice_mean(
            da=indice.cf_vars[0].da,
            in_base_da=indice.cf_vars[0].in_base_da,
            coef=indice.coef,
            logical_operation=indice.logical_operation,
            threshold=indice.thresh,
            freq=indice.freq.panda_freq,
        )
    elif indice.calc_operation == CalcOperation.SUM.value:
        return user_indice_sum(
            da=indice.cf_vars[0].da,
            in_base_da=indice.cf_vars[0].in_base_da,
            coef=indice.coef,
            logical_operation=indice.logical_operation,
            threshold=indice.thresh,
            freq=indice.freq.panda_freq,
        )
    elif indice.calc_operation == CalcOperation.EVENT_COUNT.value:
        return user_indice_count_events(
            das=list(map(lambda x: x.da, indice.cf_vars)),
            in_base_das=list(map(lambda x: x.in_base_da, indice.cf_vars)),
            logical_operation=indice.nb_event_config.logical_operation,
            link_logical_operations=indice.nb_event_config.link_logical_operations,
            thresholds=indice.nb_event_config.thresholds,
            coef=indice.coef,
            freq=indice.freq.panda_freq,
            date_event=indice.date_event,
        )
    elif indice.calc_operation == CalcOperation.MAX_NUMBER_OF_CONSECUTIVE_EVENTS.value:
        return user_indice_max_consecutive_event_count(
            da=indice.cf_vars[0].da,
            in_base_da=indice.cf_vars[0].in_base_da,
            logical_operation=indice.logical_operation,
            threshold=indice.thresh,
            coef=indice.coef,
            freq=indice.freq.panda_freq,
            date_event=indice.date_event,
        )
    elif indice.calc_operation == CalcOperation.RUN_MEAN.value:
        return user_indice_run_mean(
            da=indice.cf_vars[0].da,
            extreme_mode=indice.extreme_mode,
            window_width=indice.window_width,
            coef=indice.coef,
            freq=indice.freq.panda_freq,
            date_event=indice.date_event,
        )
    elif indice.calc_operation == CalcOperation.RUN_SUM.value:
        return user_indice_run_sum(
            da=indice.cf_vars[0].da,
            extreme_mode=indice.extreme_mode,
            window_width=indice.window_width,
            coef=indice.coef,
            freq=indice.freq.panda_freq,
            date_event=indice.date_event,
        )
    elif indice.calc_operation == CalcOperation.ANOMALY.value:
        return user_indice_anomaly(
            da=indice.cf_vars[0].da,
            da_ref=indice.da_ref,
            percent=indice.is_percent,
        )
    else:
        raise NotImplementedError("")  # TODO better exception


def _apply_coef(coef: Optional[float], da: DataArray) -> DataArray:
    if coef is not None:
        return da * coef
    return da


def _filter_by_threshold(
    da: DataArray,
    in_base_da: Optional[DataArray],
    logical_operation: Optional[LogicalOperation],
    threshold: Optional[Union[str, float]],
    freq: str,
    var_type: Optional[str],
):
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
    elif threshold is None:
        return da
    else:
        raise NotImplementedError()


@percentile_bootstrap
def _filter_by_logical_op_on_percentile(
    da: DataArray,
    percentiles: Optional[DataArray],
    logical_operation: Optional[LogicalOperation],
    freq: str = "MS",
    bootstrap: bool = False,  # noqa
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
    freq: str = "MS",
    bootstrap: bool = False,
):
    percentiles = resample_doy(percentiles, da)
    return logical_operation.compute(da, percentiles)


def _get_percentiles(thresh: str, var_type: Optional[str], in_base_da: DataArray):
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


def _user_indice_run_aggregator(
    da: DataArray,
    extreme_mode: ExtremeMode,
    window_width: int,
    aggregator: Callable[[Any], DataArray],  # Any should be DataArrayRolling
    coef: float = None,
    freq: str = "MS",
    date_event: bool = False,
):
    result = _apply_coef(coef, da)
    result = result.rolling(time=window_width)
    result = aggregator(result).resample(time=freq)
    if extreme_mode == ExtremeMode.MIN:
        return result.min(dim="time")
    elif extreme_mode == ExtremeMode.MAX:
        return result.max(dim="time")
    else:
        raise NotImplementedError()


@percentile_bootstrap
def threshold_compare_on_percentiles(
    da: DataArray,
    percentiles: DataArray,
    logical_operation: LogicalOperation,
    freq: str = "MS",
    bootstrap: bool = False,
):
    percentiles = resample_doy(percentiles, da)
    return logical_operation.compute(da, percentiles)


def _reduce_with_date_event(
    resampled: DataArray, reducer: Callable[[DataArray], DataArray]
) -> DataArray:
    acc: List[DataArray] = []
    for label, value in resampled:
        reduced_result = value.isel(time=reducer(value))
        acc.append(
            DataArray(
                data=reduced_result,
                dims=["lat", "lon"],
                coords=dict(
                    time=label,
                    lat=value.lat,
                    lon=value.lon,
                    event_date=reduced_result.time,
                ),
            )
        )
    return xarray.concat(acc, "time")
