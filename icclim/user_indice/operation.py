from enum import Enum
from functools import reduce
from typing import List, Union

import numpy
from xarray.core.dataarray import DataArray
from xclim.core.bootstrapping import percentile_bootstrap
from xclim.core.calendar import percentile_doy, resample_doy
from xclim.core.units import convert_units_to

from icclim.models.indice_config import CfVariable
from icclim.user_indice.user_indice import (
    PRECIPITATION,
    TEMPERATURE,
    LogicalOperation,
    UserIndiceConfig,
)

PERCENTILE_STAMP = "p"
WET_DAY_THRESHOLD = 1  # 1mm
OR_STAMP = "or"
AND_STAMP = "and"


def apply_coef(coef: float, da: DataArray) -> DataArray:
    if coef is not None:
        return da * coef
    return da


def filter_by_logical_op(
    logical_operation: LogicalOperation,
    threshold: float,
    da: DataArray,
) -> DataArray:
    if logical_operation is not None and threshold is not None:
        return da.where(logical_operation.compute(da, threshold), drop=True)
    return da


@percentile_bootstrap
def filter_by_logical_op_on_percentile(
    da: DataArray,
    percentiles: DataArray,
    logical_operation: LogicalOperation,
    freq: str = "MS",
    bootstrap: bool = False,  # noqa
) -> DataArray:
    if logical_operation is not None and percentiles is not None:
        percentiles = resample_doy(percentiles, da)
        filtered = logical_operation.compute(da, percentiles)
        filtered = filtered.where(filtered, drop=True)
        # if bootstrap: # TODO uncomment once fixed on xclim
        da = da.expand_dims(_bootstrap=filtered._bootstrap)
        #  end if
        return da.sel(time=filtered.time)
    return da


def user_indice_max(
    da: DataArray,
    coef: float = None,
    logical_operation: LogicalOperation = None,
    threshold: float = None,
    percentiles: DataArray = None,
    bootstrap=False,
    freq: str = "MS",
    date_event: bool = False,
):
    da = apply_coef(coef, da)
    if percentiles is not None:
        da = filter_by_logical_op_on_percentile(
            da, percentiles, logical_operation, freq, bootstrap
        )
    else:
        da = filter_by_logical_op(logical_operation, threshold, da)
    return da.max(dim="time")


def user_indice_min(
    da: DataArray,
    coef: float = None,
    logical_operation: LogicalOperation = None,
    threshold: float = None,
    percentiles: DataArray = None,
    bootstrap=False,
    freq: str = "MS",
    date_event: bool = False,
):
    da = apply_coef(coef, da)
    if percentiles is not None:
        da = filter_by_logical_op_on_percentile(
            da=da,
            percentiles=percentiles,
            logical_operation=logical_operation,
            freq=freq,
            bootstrap=bootstrap,
        )
    else:
        da = filter_by_logical_op(logical_operation, threshold, da)
    return da.min(dim="time")


def user_indice_sum(
    da: DataArray,
    coef: float = None,
    logical_operation: LogicalOperation = None,
    threshold: float = None,
    percentiles: DataArray = None,
    bootstrap=False,
    freq: str = "MS",
):
    da = apply_coef(coef, da)
    if percentiles is not None:
        da = filter_by_logical_op_on_percentile(
            da, percentiles, logical_operation, freq, bootstrap
        )
    else:
        da = filter_by_logical_op(logical_operation, threshold, da)
    return da.sum(dim="time")


def user_indice_mean(
    da: DataArray,
    coef: float = None,
    logical_operation: LogicalOperation = None,
    threshold: float = None,
    percentiles: DataArray = None,
    bootstrap=False,
    freq: str = "MS",
):
    da = apply_coef(coef, da)
    if percentiles is not None:
        da = filter_by_logical_op_on_percentile(
            da, percentiles, logical_operation, freq, bootstrap
        )
    else:
        da = filter_by_logical_op(logical_operation, threshold, da)
    return da.mean(dim="time")


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


def user_indice_count_events(
    data_arrays: List[DataArray],
    logical_operation: List[LogicalOperation],
    thresholds: List[float] = None,
    coef: float = None,
    link_logical_operations: str = None,
    percentiles: List[DataArray] = None,
    bootstrap=False,
    freq: str = "MS",
    date_event: bool = False,
):
    acc = []
    for i, da in enumerate(data_arrays):
        da = apply_coef(coef, da)
        if percentiles is not None:
            da = threshold_compare_on_percentiles(
                da=da,
                percentiles=percentiles[i],
                logical_operation=logical_operation[i],
                freq=freq,
                bootstrap=bootstrap,
            )
        else:
            da = logical_operation[i].compute(da, thresholds[i])
        acc.append(da)
    if len(acc) == 1:
        result = acc[0]
    elif link_logical_operations == AND_STAMP:
        result = reduce(numpy.logical_and, acc, True)
    elif link_logical_operations == OR_STAMP:
        result = reduce(numpy.logical_or, acc, False)
    else:
        raise NotImplementedError()
    return result.resample(time=freq).sum(dim="time")


@percentile_bootstrap
def threshold_count(
    da: DataArray,
    logical_operation: LogicalOperation,
    thresh: Union[float, int, DataArray],
    freq: str,
    bootstrap=False,
) -> DataArray:
    return logical_operation.compute(da, thresh).resample(time=freq).sum(dim="time")


def compute_user_indice(indice: UserIndiceConfig, cf_vars: CfVariable) -> DataArray:
    if isinstance(indice.thresh, str):
        if indice.thresh.find(PERCENTILE_STAMP) == -1:
            raise Exception(
                # TODO create a UserInputException
                "Percentile threshold not properly formatted. Use p as a prefix or suffix of the value for example 90p or p90. For non percentile threshold use a float instead of a string"
            )
        per = float(indice.thresh.replace(PERCENTILE_STAMP, ""))
        da_per = cf_vars.in_base_da
        if indice.var_type == PRECIPITATION:
            da_per = convert_units_to(cf_vars.in_base_da, "mm/d")
            da_per = da_per.where(da_per > WET_DAY_THRESHOLD, drop=True)
        percentiles = percentile_doy(arr=da_per, per=per).sel(percentiles=per)
        if indice.var_type == TEMPERATURE:
            return _compute(indice, cf_vars.da, percentiles=percentiles, bootstrap=True)
        else:
            return _compute(indice, cf_vars.da, percentiles=percentiles)
    return _compute(indice, cf_vars.da)


def _compute(
    indice: UserIndiceConfig,
    da: DataArray,
    percentiles: DataArray = None,
    bootstrap: bool = False,
):
    if indice.calc_operation == CalcOperation.MAX.value:
        return user_indice_max(
            da=da,
            coef=indice.coef,
            logical_operation=indice.logical_operation,
            threshold=indice.thresh,
            percentiles=percentiles,
            bootstrap=bootstrap,
            freq=indice.freq.panda_freq,
            date_event=indice.date_event,
        )
    elif indice.calc_operation == CalcOperation.MIN.value:
        return user_indice_min(
            da=da,
            coef=indice.coef,
            logical_operation=indice.logical_operation,
            threshold=indice.thresh,
            percentiles=percentiles,
            bootstrap=bootstrap,
            freq=indice.freq.panda_freq,
            date_event=indice.date_event,
        )
    elif indice.calc_operation == CalcOperation.MEAN.value:
        return user_indice_mean(
            da=da,
            coef=indice.coef,
            logical_operation=indice.logical_operation,
            threshold=indice.thresh,
            percentiles=percentiles,
            bootstrap=bootstrap,
            freq=indice.freq.panda_freq,
        )
    elif indice.calc_operation == CalcOperation.SUM.value:
        return user_indice_sum(
            da=da,
            coef=indice.coef,
            logical_operation=indice.logical_operation,
            threshold=indice.thresh,
            percentiles=percentiles,
            bootstrap=bootstrap,
            freq=indice.freq.panda_freq,
        )
    elif indice.calc_operation == CalcOperation.EVENT_COUNT.value:
        return user_indice_count_events(
            da=da,
            logical_operation=indice.logical_operation,
            thresholds=indice.thresh,
            coef=indice.coef,
            link_logical_operations=indice.link_logical_operations,
            percentiles=percentiles,
            bootstrap=bootstrap,
            freq=indice.freq.panda_freq,
            date_event=indice.date_event,
        )
    else:
        raise NotImplementedError("")  # TODO exc


class CalcOperation(Enum):
    MAX = "max"
    MIN = "min"
    SUM = "sum"
    MEAN = "mean"
    EVENT_COUNT = "nb_event"
