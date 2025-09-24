# -*- Coding: latin-1 -*-
#  Copyright CERFACS (http://cerfacs.fr/)
#  Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
"""
Main entry point of icclim.

This module expose icclim principal function, notably `index` which is use by the
generated API.
A convenience function `indices` is also exposed to compute multiple indices at once.
"""

from __future__ import annotations

import datetime as dt
import operator
import time
from collections.abc import Callable, Sequence
from functools import reduce
from typing import TYPE_CHECKING
from warnings import warn

import numpy as np
import xarray as xr
import xclim

from icclim._core.climate_variable import (
    ClimateVariable,
    build_climate_vars,
)
from icclim._core.constants import (
    RESAMPLE_METHOD,
    UNITS_KEY,
)
from icclim._core.generic.indicator import GenericIndicator
from icclim._core.input_parsing import build_input_dict
from icclim._core.legacy.user_index import parse
from icclim._core.model.index_config import IndexConfig
from icclim._core.model.index_group import IndexGroup, IndexGroupRegistry
from icclim._core.model.logical_link import LogicalLinkRegistry
from icclim._core.model.netcdf_version import NetcdfVersion, NetcdfVersionRegistry
from icclim._core.model.quantile_interpolation import (
    QuantileInterpolation,
    QuantileInterpolationRegistry,
)
from icclim._core.model.standard_index import StandardIndex
from icclim._core.model.threshold import Threshold
from icclim._core.utils import read_date
from icclim.dcsc.registry import DcscIndexRegistry
from icclim.ecad.binding import (
    StandardizedPrecipitationIndex3,
    StandardizedPrecipitationIndex6,
)
from icclim.ecad.registry import EcadIndexRegistry
from icclim.exception import InvalidIcclimArgumentError
from icclim.frequency import Frequency, FrequencyRegistry
from icclim.generic.registry import GenericIndicatorRegistry
from icclim.logger import IcclimLogger, Verbosity, VerbosityRegistry
from icclim.threshold.factory import build_threshold

if TYPE_CHECKING:
    from xarray.core.dataarray import DataArray
    from xarray.core.dataset import Dataset

    from icclim._core.legacy.user_index.model import UserIndexDict
    from icclim._core.model.icclim_types import (
        FrequencyLike,
        InFileLike,
        SamplingMethodLike,
    )
    from icclim._core.model.in_file_dictionary import InFileDictionary
    from icclim._core.model.indicator import Indicator

log: IcclimLogger = IcclimLogger.get_instance(VerbosityRegistry.LOW)

HISTORY_CF_KEY = "history"
SOURCE_CF_KEY = "source"
ICCLIM_REFERENCE = "icclim"


def indices(
    index_group: Sequence[str] | str | IndexGroup | StandardIndex,
    *,
    ignore_error: bool = False,
    **kwargs,
) -> Dataset:
    """
    Compute multiple indices at the same time.

    The input dataset(s) must include all the necessary variables.
    It can only be used with keyword arguments (kwargs).

    Parameters
    ----------
    index_group : "all" | str | IndexGroup | list[str]
        Either the name of an IndexGroup or an instance of IndexGroup or a list
        of index short names or the name(s) of standard variable(s) (such as 'tasmax').
        The value "all" can also be used to compute every indices.
        Note that the input given by ``in_files`` must include all the necessary
        variables to compute the indices of this group.
    ignore_error: bool
        When True, ignore indices that fails to compute. This is option is particularly
        useful when used with `index_group='all'` to compute everything that can be
        computed given the input.
    kwargs : Dict
        ``icclim.index`` keyword arguments.

    Returns
    -------
    xr.Dataset
        A Dataset with one data variable per index.

    Notes
    -----
    If ``output_file`` is part of kwargs, the result is written in a single netCDF
    file, which will contain all the index results of this group.
    """
    indices = _get_ecad_indices_of_group(index_group)
    out = None
    if "out_file" in kwargs:
        out = kwargs["out_file"]
        del kwargs["out_file"]
    acc = []
    for i in indices:
        log.info("Computing index %s", i.short_name)
        kwargs["index_name"] = i.short_name
        if ignore_error:
            try:
                res = index(**kwargs)
                if "percentiles" in res.coords:
                    res = res.rename({"percentiles": i.short_name + "_percentiles"})
                if "thresholds" in res.coords:
                    res = res.rename({"thresholds": i.short_name + "_thresholds"})
                acc.append(res)
            except Exception:  # noqa: BLE001 (catch everything)
                warn(f"Could not compute {i.short_name}.", stacklevel=2)
        else:
            res = index(**kwargs)
            if "percentiles" in res.coords:
                res = res.rename({"percentiles": i.short_name + "_percentiles"})
            if "thresholds" in res.coords:
                res = res.rename({"thresholds": i.short_name + "_thresholds"})
            acc.append(res)
    ds: Dataset = xr.merge(acc)
    if out is not None:
        _write_output_file(
            result_ds=ds,
            input_time_encoding=ds.time.encoding,
            netcdf_version=kwargs.get("netcdf_version", NetcdfVersionRegistry.NETCDF4),
            file_path=out,
        )
    return ds


def _get_ecad_indices_of_group(
    query: Sequence[str] | str | IndexGroup | StandardIndex,
) -> list[StandardIndex]:
    if query == IndexGroupRegistry.WILD_CARD_GROUP or (
        isinstance(query, str)
        and query.lower() == IndexGroupRegistry.WILD_CARD_GROUP.name
    ):
        # case of group="all"
        return EcadIndexRegistry.values()
    if not isinstance(query, (list, tuple)):
        query = [query]
    # -- Look for standard indices (e.g. index_group='tx90p')
    indices = [EcadIndexRegistry.lookup_no_error(i) for i in query]
    indices = list(filter(lambda x: x is not None, indices))
    if len(indices) == len(query):
        return indices
    # -- Look for variables in standard indices (e.g. index_group='tasmax')
    indices = []
    for ecad_index in EcadIndexRegistry.values():
        has_var = True
        for var in ecad_index.input_variables:
            is_query_in_aliases = (
                standard_var in var.aliases for standard_var in query
            )
            has_var &= any(is_query_in_aliases)
        if has_var:
            indices.append(ecad_index)
    if len(indices) >= len(query):
        return indices
    # -- Look for index group (e.g. index_group='HEAT')
    groups = [IndexGroupRegistry.lookup_no_error(i) for i in query]
    groups = list(filter(lambda x: x is not None, groups))
    indices = (x.get_indices() for x in groups)
    indices = reduce(operator.add, indices, [])  # flatten list[list]
    if len(indices) >= len(query):
        return indices
    msg = f"The index group {query} was not recognized."
    raise InvalidIcclimArgumentError(msg)


def indice(*args, **kwargs) -> Dataset:
    """
    Proxy for `icclim.index` function.

    Deprecated: to be deleted in a future release.
    """
    log.deprecation_warning(old="icclim.indice", new="icclim.index")
    return index(*args, **kwargs)


def index(
    in_files: InFileLike,
    index_name: str
    | GenericIndicator
    | StandardIndex
    | None = None,  # optional when computing user_indices
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[dt.datetime | str] | None = None,
    out_file: str | None = None,
    threshold: str | Threshold | Sequence[str | Threshold] | None = None,
    callback: Callable[[int], None] = log.callback,
    callback_percentage_start_value: int = 0,
    callback_percentage_total: int = 100,
    base_period_time_range: Sequence[dt.datetime] | Sequence[str] | None = None,
    doy_window_width: int = 5,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,  # noqa: N803
    interpolation: str | QuantileInterpolation = "median_unbiased",
    out_unit: str | None = None,
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    user_index: UserIndexDict | None = None,
    save_thresholds: bool = False,
    logs_verbosity: Verbosity | str = "LOW",
    date_event: bool = False,
    min_spell_length: int | None = 6,
    rolling_window_width: int | None = 5,
    sampling_method: SamplingMethodLike = RESAMPLE_METHOD,
    *,
    # deprecated params are kwargs only
    window_width: int | None = None,
    save_percentile: bool | None = None,
    indice_name: str | None = None,
    user_indice: UserIndexDict | None = None,
    transfer_limit_Mbytes: float | None = None,  # noqa: N803
) -> Dataset:
    """
    Compute climate index.

    This is the main entry point for icclim.

    Parameters
    ----------
    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    index_name: str | StandardIndex
        Climate index name.
        For ECA&D index, case insensitive name used to lookup the index.
        For user index, it's the name of the output variable.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the
        climate index wanted.
        Mandatory for a user index.
    slice_mode: FrequencyLike | Frequency
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas
        frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime.datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file: str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    threshold: float | list[float] | None
        ``optional`` User defined threshold for certain indices.
        Default depend on the index, see their individual definition.
        When a list of threshold is provided, the index will be computed for each
        thresholds.
    transfer_limit_Mbytes: float
        Deprecated, does not have any effect.
    callback: Callable[[int], None]
        ``optional`` Progress bar printing. If ``None``, progress bar will not be
        printed.
    callback_percentage_start_value: int
        ``optional`` Initial value of percentage of the progress bar (default: 0).
    callback_percentage_total: int
        ``optional`` Total percentage value (default: 100).
    base_period_time_range: list[datetime.datetime ] | list[str] | tuple[str, str] | None
        ``optional`` Temporal range of the reference period.
        The dates can either be given as instance of datetime.datetime or as string
        values.
        It is used either:
        #. to compute percentiles if threshold is filled.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if `time_range` is missing.
        For day of year percentiles (doy_per), on extreme percentiles the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        #. to compute a reference period for indices such as difference_of_mean
        (a.k.a anomaly) if a single variable is given in input.
    doy_window_width: int
        ``optional`` Window width used to aggreagte day of year values when computing
        day of year percentiles (doy_per)
        Default: 5 (5 days).
    min_spell_length: int
        ``optional`` Minimum spell duration to be taken into account when computing
        the sum_of_spell_lengths.
    rolling_window_width: int
        ``optional`` Window width of the rolling window for indicators such as
        `{max_of_rolling_sum, max_of_rolling_average, min_of_rolling_sum, min_of_rolling_average}`
    only_leap_years: bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th: bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation: str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "median_unbiased"}``
        Default is "median_unbiased", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    out_unit: str | None
        ``optional`` Output unit for certain indices: "days" or "%"
        (default: "days").
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    user_index: UserIndexDict
        ``optional`` A dictionary with parameters for user defined index.
        See :ref:`Custom indices`.
        Ignored for ECA&D indices.
    save_thresholds: bool
        ``optional`` True if the thresholds should be saved within the resulting
        netcdf file (default: False).
    date_event: bool
        When True the date of the event (such as when a maximum is reached) will be
        stored in coordinates variables.
        **warning** This option may significantly slow down computation.
    logs_verbosity: str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    sampling_method: str
        Choose whether the output sampling configured in `slice_mode` is a
        `groupby` operation or a `resample` operation (as per xarray definitions).
        Possible values:
        ``{"groupby", "resample", "groupby_ref_and_resample_study"}``
        (default: "resample")
        `groupby_ref_and_resample_study` may only be used when computing the
        `difference_of_means` (a.k.a the anomaly).
    indice_name: str | None
        DEPRECATED, use index_name instead.
    user_indice: dict | None
        DEPRECATED, use user_index instead.
    window_width: int
        DEPRECATED, use doy_window_width, min_spell_length or rolling_window_width
        instead.
    save_percentile: bool
        DEPRECATED, use save_thresholds instead.

    """  # noqa: E501
    _setup(callback, callback_percentage_start_value, logs_verbosity)
    (
        index_name,
        user_index,
        save_thresholds,
        doy_window_width,
    ) = _handle_deprecated_params(
        index_name,
        user_index,
        save_thresholds,
        indice_name,
        transfer_limit_Mbytes,
        user_indice,
        save_percentile,
        window_width,
        doy_window_width,
    )
    del indice_name, transfer_limit_Mbytes, user_indice, save_percentile, window_width
    config = _build_config(
        in_files=in_files,
        index_name=index_name,
        var_name=var_name,
        slice_mode=slice_mode,
        time_range=time_range,
        threshold=threshold,
        callback=callback,
        base_period_time_range=base_period_time_range,
        doy_window_width=doy_window_width,
        only_leap_years=only_leap_years,
        ignore_Feb29th=ignore_Feb29th,
        interpolation=interpolation,
        out_unit=out_unit,
        netcdf_version=netcdf_version,
        user_index=user_index,
        save_thresholds=save_thresholds,
        date_event=date_event,
        min_spell_length=min_spell_length,
        rolling_window_width=rolling_window_width,
        sampling_method=sampling_method,
    )
    result_ds = _compute_climate_index(
        climate_index=config.indicator,
        config=config,
        initial_history=config.climate_variables[0].global_metadata["history"],
        initial_source=config.climate_variables[0].global_metadata["source"],
        rename=config.rename,
        reference=config.reference,
    )
    if out_file is not None:
        _write_output_file(
            result_ds,
            config.climate_variables[0].global_metadata["time_encoding"],
            config.netcdf_version,
            out_file,
        )
    callback(callback_percentage_total)
    log.ending_message(time.process_time())
    return result_ds


def _build_config(
    in_files: InFileLike,
    index_name: str | GenericIndicator | StandardIndex | None,
    var_name: str | Sequence[str] | None,
    slice_mode: FrequencyLike | Frequency,
    time_range: Sequence[dt.datetime | str] | None,
    threshold: str | Threshold | Sequence[str | Threshold] | None,
    callback: Callable[[int], None],
    base_period_time_range: Sequence[dt.datetime] | Sequence[str] | None,
    doy_window_width: int,
    only_leap_years: bool,
    ignore_Feb29th: bool,  # noqa: N803
    interpolation: str | QuantileInterpolation,
    out_unit: str | None,
    netcdf_version: str | NetcdfVersion,
    user_index: UserIndexDict | None,
    save_thresholds: bool,
    date_event: bool,
    min_spell_length: int | None,
    rolling_window_width: int | None,
    sampling_method: SamplingMethodLike,
) -> IndexConfig:
    if user_index is not None and (index_name is None or isinstance(index_name, str)):
        return _build_user_index_config(
            user_index,
            in_files=in_files,
            index_name=index_name,
            var_name=var_name,
            slice_mode=slice_mode,
            time_range=time_range,
            callback=callback,
            base_period_time_range=base_period_time_range,
            doy_window_width=doy_window_width,
            only_leap_years=only_leap_years,
            ignore_Feb29th=ignore_Feb29th,
            interpolation=interpolation,
            out_unit=out_unit,
            netcdf_version=netcdf_version,
            save_thresholds=save_thresholds,
            date_event=date_event,
            min_spell_length=min_spell_length,
            rolling_window_width=rolling_window_width,
            sampling_method=sampling_method,
        )
    if index_name is not None:
        return _build_standard_index_config(
            in_files=in_files,
            index_name=index_name,
            var_name=var_name,
            slice_mode=slice_mode,
            time_range=time_range,
            threshold=threshold,
            callback=callback,
            base_period_time_range=base_period_time_range,
            doy_window_width=doy_window_width,
            only_leap_years=only_leap_years,
            ignore_Feb29th=ignore_Feb29th,
            interpolation=interpolation,
            out_unit=out_unit,
            netcdf_version=netcdf_version,
            save_thresholds=save_thresholds,
            date_event=date_event,
            min_spell_length=min_spell_length,
            rolling_window_width=rolling_window_width,
            sampling_method=sampling_method,
        )
    msg = "You must fill either index_name or user_index" "to compute a climate index."
    raise InvalidIcclimArgumentError(msg)


def _get_reference_period(
    base_period_time_range: Sequence[dt.datetime | str] | None,
) -> tuple | None:
    if base_period_time_range is not None:
        return tuple(
            (read_date(t).strftime("%m-%d-%Y") for t in base_period_time_range),
        )
    return None


def _parse_threshold(
    threshold: str | Threshold | Sequence[str | Threshold] | None,
    doy_window_width: int,
    reference_period: Sequence[dt.datetime | str] | None,
    only_leap_years: bool,
    interpolation: QuantileInterpolation,
) -> Threshold | Sequence[Threshold] | None:
    if isinstance(threshold, Threshold):
        return threshold
    if isinstance(threshold, str):
        return _build_threshold(
            threshold,
            doy_window_width=doy_window_width,
            reference_period=reference_period,
            only_leap_years=only_leap_years,
            interpolation=interpolation,
        )
    if isinstance(threshold, Sequence):
        return [
            _build_threshold(
                t,
                doy_window_width=doy_window_width,
                reference_period=reference_period,
                only_leap_years=only_leap_years,
                interpolation=interpolation,
            )
            for t in threshold
        ]
    return None


def _build_user_index_config(
    user_index: UserIndexDict,
    in_files: InFileLike,
    index_name: str | None,
    var_name: str | Sequence[str] | None,
    slice_mode: FrequencyLike | Frequency,
    time_range: Sequence[dt.datetime | str] | None,
    callback: Callable[[int], None],
    base_period_time_range: Sequence[dt.datetime] | Sequence[str] | None,
    doy_window_width: int,
    only_leap_years: bool,
    ignore_Feb29th: bool,  # noqa: N803
    interpolation: str | QuantileInterpolation,
    out_unit: str | None,
    netcdf_version: str | NetcdfVersion,
    save_thresholds: bool,
    date_event: bool,
    min_spell_length: int | None,
    rolling_window_width: int | None,
    sampling_method: SamplingMethodLike,
) -> IndexConfig:
    interpolation = QuantileInterpolationRegistry.lookup(interpolation)
    indicator = parse.read_indicator(user_index)
    sampling_frequency = FrequencyRegistry.lookup(slice_mode)
    threshold = parse.read_thresholds(
        user_index,
        doy_window_width=doy_window_width,
        reference_period=base_period_time_range,
        only_leap_years=only_leap_years,
        interpolation=interpolation,
    )
    logical_link = parse.read_logical_link(user_index)
    coef = parse.read_coef(user_index)
    date_event = parse.read_date_event(user_index)
    rename = index_name or user_index.get("index_name", None) or "user_index"
    output_unit = out_unit
    rolling_window_width = user_index.get("window_width", rolling_window_width)
    reference_period = _get_reference_period(
        user_index.get("ref_time_range", base_period_time_range)
    )
    climate_vars_dict = build_input_dict(
        in_files=in_files,
        var_names=var_name,
        threshold=threshold,
        standard_index=None,
    )
    is_compared_to_ref = _must_add_reference_var(climate_vars_dict, reference_period)
    climate_vars = build_climate_vars(
        climate_vars_dict=climate_vars_dict,
        ignore_Feb29th=ignore_Feb29th,
        time_range=time_range,
        base_period=reference_period,
        standard_index=None,
        is_compared_to_reference=is_compared_to_ref,
    )
    return IndexConfig(
        save_thresholds=save_thresholds,
        frequency=sampling_frequency,
        climate_variables=climate_vars,
        min_spell_length=min_spell_length,
        rolling_window_width=rolling_window_width,
        out_unit=output_unit,
        netcdf_version=NetcdfVersionRegistry.lookup(netcdf_version),
        interpolation=interpolation,
        callback=callback,
        is_compared_to_reference=is_compared_to_ref,
        reference_period=reference_period,
        indicator_name=indicator.name,
        logical_link=logical_link,
        coef=coef,
        date_event=date_event,
        sampling_method=sampling_method,
        rename=rename,
        indicator=indicator,
        reference=ICCLIM_REFERENCE,
    )


def _build_standard_index_config(
    in_files: InFileLike,
    index_name: str | GenericIndicator | StandardIndex,
    var_name: str | Sequence[str] | None,
    slice_mode: FrequencyLike | Frequency,
    time_range: Sequence[dt.datetime | str] | None,
    threshold: str | Threshold | Sequence[str | Threshold] | None,
    callback: Callable[[int], None],
    base_period_time_range: Sequence[dt.datetime] | Sequence[str] | None,
    doy_window_width: int,
    only_leap_years: bool,
    ignore_Feb29th: bool,  # noqa: N803
    interpolation: str | QuantileInterpolation,
    out_unit: str | None,
    netcdf_version: str | NetcdfVersion,
    save_thresholds: bool,
    date_event: bool,
    min_spell_length: int | None,
    rolling_window_width: int | None,
    sampling_method: SamplingMethodLike,
) -> IndexConfig:
    interpolation = QuantileInterpolationRegistry.lookup(interpolation)
    # logical link here link two climate_variable computations as with user_index.
    # It isalways AND for standard indices.
    logical_link = LogicalLinkRegistry.LOGICAL_AND
    sampling_frequency = FrequencyRegistry.lookup(slice_mode)
    coef = None
    index = _parse_index_kind(index_name)
    if isinstance(index, StandardIndex):
        standard_index = index.clone()
        indicator = standard_index.indicator.clone()
        threshold = standard_index.threshold
        rename = standard_index.short_name
        output_unit = out_unit or standard_index.output_unit
        reference = standard_index.reference
        indicator_name = standard_index.short_name
    elif isinstance(index, GenericIndicator):
        rename = None
        output_unit = out_unit
        standard_index = None
        indicator = index.clone()
        reference = ICCLIM_REFERENCE
        indicator_name = indicator.name
    else:
        err = f"Unknown index_name : `{index_name}`"
        raise InvalidIcclimArgumentError(err)
    reference_period = _get_reference_period(base_period_time_range)
    threshold = _parse_threshold(
        threshold,
        doy_window_width=doy_window_width,
        reference_period=reference_period,
        only_leap_years=only_leap_years,
        interpolation=interpolation,
    )
    climate_vars_dict = build_input_dict(
        in_files=in_files,
        var_names=var_name,
        threshold=threshold,
        standard_index=standard_index,
    )
    is_compared_to_ref = _must_add_reference_var(climate_vars_dict, reference_period)
    climate_vars = build_climate_vars(
        climate_vars_dict=climate_vars_dict,
        ignore_Feb29th=ignore_Feb29th,
        time_range=time_range,
        base_period=reference_period,
        standard_index=standard_index,
        is_compared_to_reference=is_compared_to_ref,
    )
    return IndexConfig(
        save_thresholds=save_thresholds,
        frequency=sampling_frequency,
        climate_variables=climate_vars,
        min_spell_length=min_spell_length,
        rolling_window_width=rolling_window_width,
        out_unit=output_unit,
        netcdf_version=NetcdfVersionRegistry.lookup(netcdf_version),
        interpolation=interpolation,
        callback=callback,
        is_compared_to_reference=is_compared_to_ref,
        reference_period=reference_period,
        indicator_name=indicator_name,
        logical_link=logical_link,
        coef=coef,
        date_event=date_event,
        sampling_method=sampling_method,
        rename=rename,
        indicator=indicator,
        reference=reference,
    )


def _parse_index_kind(
    index_name: StandardIndex | GenericIndicator | str,
) -> StandardIndex | GenericIndicator:
    if isinstance(index_name, str):
        index = EcadIndexRegistry.lookup_no_error(index_name)
        if index is None:
            index = DcscIndexRegistry.lookup_no_error(index_name)
        if index is None:
            index = GenericIndicatorRegistry.lookup(index_name)
        return index
    return index_name


def _write_output_file(
    result_ds: xr.Dataset,
    input_time_encoding: dict | None,
    netcdf_version: NetcdfVersion,
    file_path: str,
) -> None:
    """Write `result_ds` to a netCDF file on `out_file` path."""
    if input_time_encoding:
        time_encoding = {
            "calendar": input_time_encoding.get("calendar"),
            UNITS_KEY: input_time_encoding.get(UNITS_KEY),
            # Force float64 to avoid serialization warning
            "dtype": np.float64,
        }
    else:
        time_encoding = {
            UNITS_KEY: "days since 1850-1-1",
            "dtype": np.float64,  # force float
        }
    result_ds.to_netcdf(
        file_path,
        format=netcdf_version.name,
        encoding={"time": time_encoding},
    )


def _handle_deprecated_params(
    index_name: str | GenericIndicator | StandardIndex | None,
    user_index: UserIndexDict | None,
    save_thresholds: bool,
    indice_name: str | None,
    transfer_limit_Mbytes: float | None,  # noqa: N803
    user_indice: UserIndexDict | None,
    save_percentile: bool | None,
    window_width: int | None,
    doy_window_width: int | None,
) -> tuple[str, UserIndexDict, bool, int]:
    if indice_name is not None:
        log.deprecation_warning(old="indice_name", new="index_name")
        index_name = indice_name
    if user_indice is not None:
        log.deprecation_warning(old="user_indice", new="user_index")
        user_index = user_indice
    if transfer_limit_Mbytes is not None:
        log.deprecation_warning(old="transfer_limit_Mbytes")
    if save_percentile is not None:
        log.deprecation_warning(old="save_percentile", new="save_thresholds")
        save_thresholds = save_percentile
    if window_width is not None:
        log.deprecation_warning(old="window_width", new="doy_window_width")
        doy_window_width = window_width
    return index_name, user_index, save_thresholds, doy_window_width


def _setup(
    callback: Callable[[int], None],
    callback_start_value: int,
    logs_verbosity: Verbosity | str,
) -> None:
    # make xclim input daily check a warning instead of an error
    # TODO @bzah: it might be safer to feed a context manager which will setup
    #             and teardown these confs
    # https://github.com/cerfacs-globc/icclim/issues/289
    xclim.set_options(data_validation="warn")
    # keep attributes through xarray operations
    xr.set_options(keep_attrs=True)
    log.set_verbosity(logs_verbosity)
    log.start_message()
    callback(callback_start_value)


def _get_unit(output_unit: str | None, da: DataArray) -> str | None:
    da_unit = da.attrs.get(UNITS_KEY, None)
    if da_unit is None:
        if output_unit is None:
            warn(
                "No unit computed or provided for the index was found."
                " Use out_unit parameter to add one.",
                stacklevel=2,
            )
            return ""
        return output_unit
    return da_unit


def _compute_climate_index(
    climate_index: Indicator,
    config: IndexConfig,
    initial_history: str | None,
    initial_source: str | None,
    reference: str,
    rename: str | None = None,
) -> Dataset:
    result_da = climate_index(config)
    if rename:
        result_da = result_da.rename(rename)
    else:
        result_da = result_da.rename(climate_index.name)
    result_da.attrs[UNITS_KEY] = _get_unit(config.out_unit, result_da)
    if (
        config.frequency.post_processing is not None
        and "time" in result_da.dims
        and not isinstance(
            climate_index,
            (
                StandardizedPrecipitationIndex6,
                StandardizedPrecipitationIndex3,
            ),
        )
    ):
        resampled_da, time_bounds = config.frequency.post_processing(result_da)
        result_ds = resampled_da.to_dataset()
        if time_bounds is not None:
            result_ds["time_bounds"] = time_bounds
            result_ds.time.attrs["bounds"] = "time_bounds"
    else:
        result_ds = result_da.to_dataset()
    if config.save_thresholds:
        result_ds = xr.merge(
            [result_ds, _format_thresholds_for_export(config.climate_variables)],
        )
    history = _build_history(result_da, config, initial_history, climate_index)
    return _add_ecad_index_metadata(
        result_ds,
        climate_index,
        history,
        initial_source,
        reference,
    )


def _add_ecad_index_metadata(
    result_ds: Dataset,
    computed_index: Indicator,
    history: str,
    initial_source: str | None,
    reference: str,
) -> Dataset:
    result_ds.attrs.update(
        {
            "title": computed_index.standard_name,
            "references": reference,
            "institution": "Climate impact portal (https://climate4impact.eu)",
            "history": history,
            "source": initial_source if initial_source is not None else "",
            "Conventions": "CF-1.6",
        },
    )
    try:
        result_ds.lat.encoding["_FillValue"] = None
        result_ds.lon.encoding["_FillValue"] = None
    except AttributeError:
        try:
            result_ds.latitude.encoding["_FillValue"] = None
            result_ds.longitude.encoding["_FillValue"] = None
        except AttributeError:
            pass
    return result_ds


def _build_history(
    result_da: DataArray,
    config: IndexConfig,
    initial_history: str | None,
    indice_computed: Indicator,
) -> str:
    from icclim import __version__ as icclim_version

    if initial_history is None:
        # get xclim history
        initial_history = result_da.attrs[HISTORY_CF_KEY]
    else:
        # append xclim history
        initial_history = f"{initial_history}\n{result_da.attrs[HISTORY_CF_KEY]}"
    del result_da.attrs[HISTORY_CF_KEY]
    current_time = dt.datetime.now(tz=dt.timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S",
    )
    return (
        f"{initial_history}\n"
        f" [{current_time}]"
        f" Calculation of {indice_computed.name}"
        f" index ({config.frequency.adjective})"
        f" - icclim version: {icclim_version}"
    )


def _build_threshold(
    threshold: str | Threshold,
    doy_window_width: int,
    reference_period: Sequence[dt.datetime | str] | None,
    only_leap_years: bool,
    interpolation: QuantileInterpolation,
) -> Threshold:
    if isinstance(threshold, Threshold):
        return threshold
    return build_threshold(
        threshold,
        doy_window_width=doy_window_width,
        reference_period=reference_period,
        only_leap_years=only_leap_years,
        interpolation=interpolation,
    )


def _format_thresholds_for_export(climate_vars: list[ClimateVariable]) -> Dataset:
    return xr.merge([_format_threshold(v) for v in climate_vars])


def _format_threshold(cf_var: ClimateVariable) -> DataArray:
    return cf_var.threshold.value.rename(cf_var.name + "_thresholds").reindex()


def _must_add_reference_var(
    climate_vars_dict: dict[str, InFileDictionary],
    reference_period: Sequence[str] | None,
) -> bool:
    """
    Check if the reference variable must be added to the input variables.

    Return True whenever the input has no threshold and only one studied variable but
    there is a reference period.
    Example case: the anomaly of tx(1960-2100) by tx(1960-1990).
    """
    t = next(iter(climate_vars_dict.values())).get("thresholds", None)
    return t is None and len(climate_vars_dict) == 1 and reference_period is not None
