from enum import Enum
import xarray
from icclim.models.indice_config import CfVariable
from typing import List, Union
from xclim.core.units import convert_units_to
from xclim.core.calendar import percentile_doy, resample_doy

from xclim.core.bootstrapping import bootstrap_func, percentile_bootstrap
from icclim.user_indice.user_indice import (
    LogicalOperation,
    PRECIPITATION,
    TEMPERATURE,
    UserIndiceConfig,
)
from xarray.core.dataarray import DataArray

PERCENTILE_STAMP = "p"
WET_DAY_THRESHOLD = 1  # 1mm


def apply_coef(coef: float, da: DataArray) -> DataArray:
    if coef is not None:
        return da * coef
    return da


def filter_by_logical_op(
    logical_operation: LogicalOperation, threshold: float, da: DataArray,
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
    else:
        raise Exception("")  # TODO exc


class CalcOperation(Enum):
    MAX = "max"
    MIN = "min"
    SUM = "sum"
    MEAN = "mean"
    EVENT_COUNT = "nb_event"

