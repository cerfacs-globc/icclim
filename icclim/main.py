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

import time
from datetime import datetime
from functools import partial, reduce
from typing import Callable, Literal, Sequence
from warnings import warn

import xarray as xr
import xclim
from xarray.core.dataarray import DataArray
from xarray.core.dataset import Dataset

from icclim.ecad.ecad_indices import EcadIndexRegistry
from icclim.generic_indices.generic_indicators import (
    GenericIndicator,
    GenericIndicatorRegistry,
    Indicator,
)
from icclim.generic_indices.threshold import Threshold, build_threshold
from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.icclim_logger import IcclimLogger, Verbosity, VerbosityRegistry
from icclim.icclim_types import InFileLike, SamplingMethodLike
from icclim.models.climate_variable import (
    ClimateVariable,
    build_climate_vars,
    read_in_files,
)
from icclim.models.constants import (
    ICCLIM_VERSION,
    PERCENTILE_THRESHOLD_STAMP,
    RESAMPLE_METHOD,
    UNITS_KEY,
    USER_INDEX_PRECIPITATION_STAMP,
    USER_INDEX_TEMPERATURE_STAMP,
)
from icclim.models.frequency import Frequency, FrequencyLike, FrequencyRegistry
from icclim.models.index_config import IndexConfig
from icclim.models.index_group import IndexGroup, IndexGroupRegistry
from icclim.models.logical_link import LogicalLink, LogicalLinkRegistry
from icclim.models.netcdf_version import NetcdfVersion, NetcdfVersionRegistry
from icclim.models.operator import Operator, OperatorRegistry
from icclim.models.quantile_interpolation import (
    QuantileInterpolation,
    QuantileInterpolationRegistry,
)
from icclim.models.standard_index import StandardIndex
from icclim.models.user_index_dict import UserIndexDict
from icclim.pre_processing.in_file_dictionary import InFileDictionary
from icclim.user_indices.calc_operation import CalcOperationRegistry
from icclim.utils import read_date

log: IcclimLogger = IcclimLogger.get_instance(VerbosityRegistry.LOW)

HISTORY_CF_KEY = "history"
SOURCE_CF_KEY = "source"
ICCLIM_REFERENCE = "icclim"


def indices(
    index_group: Literal["all"] | str | IndexGroup | Sequence[str],
    ignore_error: bool = False,
    **kwargs,
) -> Dataset:
    """
    Compute multiple indices at the same time.
    The input dataset(s) must include all the necessary variables.
    It can only be used with keyword arguments (kwargs)

    .. notes
        If ``output_file`` is part of kwargs, the result is written in a single netCDF
        file, which will contain all the index results of this group.

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

    """
    indices = _get_indices_of_group(index_group)
    out = None
    if "out_file" in kwargs.keys():
        out = kwargs["out_file"]
        del kwargs["out_file"]
    acc = []
    for i in indices:
        log.info(f"Computing index '{i.short_name}'")
        kwargs["index_name"] = i.short_name
        if ignore_error:
            try:
                res = index(**kwargs)
                if "percentiles" in res.coords:
                    res = res.rename({"percentiles": i.short_name + "_percentiles"})
                if "thresholds" in res.coords:
                    res = res.rename({"thresholds": i.short_name + "_thresholds"})
                acc.append(res)
            except Exception:
                warn(f"Could not compute {i.short_name}.")
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


def _get_indices_of_group(
    query: list | tuple | str | IndexGroup | StandardIndex,
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
    indices = [EcadIndexRegistry.lookup(i, no_error=True) for i in query]
    indices = list(filter(lambda x: x is not None, indices))
    if len(indices) == len(query):
        return indices
    # -- Look for variables in standard indices (e.g. index_group='tasmax')
    indices = []
    for ecad_index in EcadIndexRegistry.values():
        has_var = True
        for var in ecad_index.input_variables:
            is_query_in_aliases = map(
                lambda standard_var: standard_var in var.aliases, query
            )
            has_var &= any(is_query_in_aliases)
        if has_var:
            indices.append(ecad_index)
    if len(indices) >= len(query):
        return indices
    # -- Look for index group (e.g. index_group='HEAT')
    groups = [IndexGroupRegistry.lookup(i, no_error=True) for i in query]
    groups = list(filter(lambda x: x is not None, groups))
    indices = map(lambda x: x.get_indices(), groups)
    indices = reduce(lambda x, y: x + y, indices, [])  # flatten list[list]
    if len(indices) >= len(query):
        return indices
    raise InvalidIcclimArgumentError(f"The index group {query} was not recognized.")


def indice(*args, **kwargs) -> Dataset:
    """
    Deprecated proxy for `icclim.index` function.
    To be deleted in a futur version.
    """
    log.deprecation_warning(old="icclim.indice", new="icclim.index")
    return index(*args, **kwargs)


def index(
    in_files: InFileLike,
    index_name: str | None = None,  # optional when computing user_indices
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    threshold: str | Threshold | Sequence[str | Threshold] = None,
    callback: Callable[[int], None] = log.callback,
    callback_percentage_start_value: int = 0,
    callback_percentage_total: int = 100,
    base_period_time_range: Sequence[datetime] | Sequence[str] | None = None,
    doy_window_width: int = 5,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
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
    indice_name: str = None,
    user_indice: UserIndexDict = None,
    transfer_limit_Mbytes: float = None,
) -> Dataset:
    """
    Main entry point for icclim to compute climate indices.

    Parameters
    ----------

    in_files: str | list[str] | Dataset | DataArray | InputDictionary
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    index_name: str
        Climate index name.
        For ECA&D index, case insensitive name used to lookup the index.
        For user index, it's the name of the output variable.
    var_name: str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode: SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range: list[datetime ] | list[str]  | tuple[str, str] | None
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
    base_period_time_range: list[datetime ] | list[str]  | tuple[str, str] | None
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
        ``optional`` Minimum spell duration to be taken into account when computing the
        sum_of_spell_lengths.
    rolling_window_width: int
        ``optional`` Window width of the rolling window for indicators such as
        `{max_of_rolling_sum, max_of_rolling_average, min_of_rolling_sum, min_of_rolling_average}`  # noqa
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
        ``optional`` Output unit for certain indices: "days" or "%" (default: "days").
    netcdf_version: str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    user_index: UserIndexDict
        ``optional`` A dictionary with parameters for user defined index.
        See :ref:`Custom indices`.
        Ignored for ECA&D indices.
    save_thresholds: bool
        ``optional`` True if the thresholds should be saved within the resulting netcdf
         file (default: False).
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
        Possible values: ``{"groupby", "resample", "groupby_ref_and_resample_study"}``
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

    """
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
        doy_window_width,
        indice_name,
        transfer_limit_Mbytes,
        user_indice,
        save_percentile,
        window_width,
    )
    del indice_name, transfer_limit_Mbytes, user_indice, save_percentile, window_width
    # -- Choose index to compute
    interpolation = QuantileInterpolationRegistry.lookup(interpolation)
    indicator: Indicator
    standard_index: StandardIndex | None
    logical_link: LogicalLink
    coef: float | None
    build_configured_threshold = partial(
        _build_threshold,
        doy_window_width=doy_window_width,
        base_period_time_range=base_period_time_range,
        only_leap_years=only_leap_years,
        interpolation=interpolation,
    )
    if user_index is not None:
        standard_index = None
        indicator = read_indicator(user_index)
        if threshold is None:
            threshold = read_thresholds(user_index, build_configured_threshold)
        logical_link = read_logical_link(user_index)
        coef = read_coef(user_index)
        date_event = read_date_event(user_index)
        rename = index_name or user_index.get("index_name", None) or "user_index"
        output_unit = out_unit
        rolling_window_width = user_index.get("window_width", rolling_window_width)
        base_period_time_range = user_index.get(
            "ref_time_range", base_period_time_range
        )
    elif index_name is not None:
        # TODO: [BoundedThreshold] read logical_link from threshold instead
        logical_link = LogicalLinkRegistry.LOGICAL_AND
        coef = None
        standard_index = EcadIndexRegistry.lookup(index_name, no_error=True)
        if standard_index is None:
            indicator = GenericIndicatorRegistry.lookup(index_name)
            rename = None
            output_unit = out_unit
        else:
            indicator = standard_index.indicator
            threshold = standard_index.threshold
            rename = standard_index.short_name
            output_unit = out_unit or standard_index.output_unit
    else:
        raise InvalidIcclimArgumentError(
            "You must fill either index_name or user_index"
            "to compute a climate index."
        )
    sampling_frequency = FrequencyRegistry.lookup(slice_mode)
    if isinstance(threshold, str):
        threshold = build_configured_threshold(threshold)
    elif isinstance(threshold, Sequence):
        threshold = [build_configured_threshold(t) for t in threshold]
    climate_vars_dict = read_in_files(
        in_files=in_files,
        var_names=var_name,
        threshold=threshold,
        standard_index=standard_index,
    )
    # We use groupby instead of resample when there is a single variable that must be
    # compared to its reference period values.
    is_compared_to_reference = _must_add_reference_var(
        climate_vars_dict, base_period_time_range
    )
    indicator_name = (
        standard_index.short_name if standard_index is not None else indicator.name
    )
    climate_vars = build_climate_vars(
        climate_vars_dict=climate_vars_dict,
        ignore_Feb29th=ignore_Feb29th,
        time_range=time_range,
        base_period=base_period_time_range,
        standard_index=standard_index,
        is_compared_to_reference=is_compared_to_reference,
    )
    if base_period_time_range is not None:
        reference_period = tuple(
            map(lambda t: read_date(t).strftime("%m-%d-%Y"), base_period_time_range)
        )
    else:
        reference_period = None
    config = IndexConfig(
        save_thresholds=save_thresholds,
        frequency=sampling_frequency,
        climate_variables=climate_vars,
        min_spell_length=min_spell_length,
        rolling_window_width=rolling_window_width,
        out_unit=output_unit,
        netcdf_version=NetcdfVersionRegistry.lookup(netcdf_version),
        interpolation=interpolation,
        callback=callback,
        is_compared_to_reference=is_compared_to_reference,
        reference_period=reference_period,
        indicator_name=indicator_name,
        logical_link=logical_link,
        coef=coef,
        date_event=date_event,
        sampling_method=sampling_method,
    )
    result_ds = _compute_climate_index(
        climate_index=indicator,
        config=config,
        initial_history=climate_vars[0].global_metadata["history"],
        initial_source=climate_vars[0].global_metadata["source"],
        rename=rename,
        reference=standard_index.reference
        if standard_index is not None
        else ICCLIM_REFERENCE,
    )
    if out_file is not None:
        _write_output_file(
            result_ds,
            climate_vars[0].global_metadata["time_encoding"],
            config.netcdf_version,
            out_file,
        )
    callback(callback_percentage_total)
    log.ending_message(time.process_time())
    return result_ds


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
            "dtype": input_time_encoding.get("dtype"),
        }
    else:
        time_encoding = {UNITS_KEY: "days since 1850-1-1"}
    result_ds.to_netcdf(
        file_path,
        format=netcdf_version.name,
        encoding={"time": time_encoding},
    )


def _handle_deprecated_params(
    index_name,
    user_index,
    save_thresholds,
    doy_window_width,
    indice_name,
    transfer_limit_Mbytes,
    user_indice,
    save_percentile,
    window_width,
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


def _setup(callback, callback_start_value, logs_verbosity):
    # make xclim input daily check a warning instead of an error
    # TODO: it might be safer to feed a context manager which will setup
    #       and teardown these confs
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
                " Use out_unit parameter to add one."
            )
            return ""
        else:
            return output_unit
    else:
        return da_unit


def _compute_climate_index(
    climate_index: Indicator | None,
    config: IndexConfig,
    initial_history: str | None,
    initial_source: str,
    reference: str,
    rename: str | None = None,
) -> Dataset:
    result_da = climate_index(config)
    if rename:
        result_da = result_da.rename(rename)
    else:
        result_da = result_da.rename(climate_index.name)
    result_da.attrs[UNITS_KEY] = _get_unit(config.out_unit, result_da)
    if config.frequency.post_processing is not None and "time" in result_da.dims:
        resampled_da, time_bounds = config.frequency.post_processing(result_da)
        result_ds = resampled_da.to_dataset()
        if time_bounds is not None:
            result_ds["time_bounds"] = time_bounds
            result_ds.time.attrs["bounds"] = "time_bounds"
    else:
        result_ds = result_da.to_dataset()
    if config.save_thresholds:
        result_ds = xr.merge(
            [result_ds, _format_thresholds_for_export(config.climate_variables)]
        )
    history = _build_history(result_da, config, initial_history, climate_index)
    result_ds = _add_ecad_index_metadata(
        result_ds, climate_index, history, initial_source, reference
    )
    return result_ds


def _add_ecad_index_metadata(
    result_ds: Dataset,
    computed_index: Indicator,
    history: str,
    initial_source: str,
    reference: str,
) -> Dataset:
    result_ds.attrs.update(
        dict(
            title=computed_index.standard_name,
            references=reference,
            institution="Climate impact portal (https://climate4impact.eu)",
            history=history,
            source=initial_source if initial_source is not None else "",
            Conventions="CF-1.6",
        )
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
    if initial_history is None:
        # get xclim history
        initial_history = result_da.attrs[HISTORY_CF_KEY]
    else:
        # append xclim history
        initial_history = f"{initial_history}\n{result_da.attrs[HISTORY_CF_KEY]}"
    del result_da.attrs[HISTORY_CF_KEY]
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return (
        f"{initial_history}\n"
        f" [{current_time}]"
        f" Calculation of {indice_computed.name}"
        f" index ({config.frequency.adjective})"
        f" - icclim version: {ICCLIM_VERSION}"
    )


def _build_threshold(
    threshold: str | Threshold,
    doy_window_width: int,
    base_period_time_range: Sequence[datetime | str] | None,
    only_leap_years: bool,
    interpolation: QuantileInterpolation,
) -> Threshold:
    if isinstance(threshold, Threshold):
        return threshold
    else:
        return build_threshold(
            threshold,
            doy_window_width=doy_window_width,
            reference_period=base_period_time_range,
            only_leap_years=only_leap_years,
            interpolation=interpolation,
        )


def _format_thresholds_for_export(climate_vars: list[ClimateVariable]) -> Dataset:
    return xr.merge([_format_threshold(v) for v in climate_vars])


def _format_threshold(cf_var: ClimateVariable) -> DataArray:
    return cf_var.threshold.value.rename(cf_var.name + "_thresholds").reindex()


# TODO move `read_indicator`, `read_threshold`, `read_logical_link`, `read_coef`,
#      `read_date_event` to a user_index_parsing module


def read_indicator(user_index: UserIndexDict) -> GenericIndicator:
    calc_op = CalcOperationRegistry.lookup(user_index["calc_operation"])
    user_index_map = {
        CalcOperationRegistry.MAX: GenericIndicatorRegistry.lookup("Maximum"),
        CalcOperationRegistry.MIN: GenericIndicatorRegistry.lookup("Minimum"),
        CalcOperationRegistry.SUM: GenericIndicatorRegistry.lookup("Sum"),
        CalcOperationRegistry.MEAN: GenericIndicatorRegistry.lookup("Average"),
        CalcOperationRegistry.EVENT_COUNT: GenericIndicatorRegistry.lookup(
            "CountOccurrences"
        ),
        CalcOperationRegistry.MAX_NUMBER_OF_CONSECUTIVE_EVENTS: GenericIndicatorRegistry.lookup(  # noqa
            "MaxConsecutiveOccurrence"
        ),
        CalcOperationRegistry.ANOMALY: GenericIndicatorRegistry.lookup(
            "DifferenceOfMeans"
        ),
    }
    if calc_op == CalcOperationRegistry.RUN_SUM:
        if user_index["extreme_mode"] == "max":
            indicator = GenericIndicatorRegistry.lookup("MaxOfRollingSum")
        elif user_index["extreme_mode"] == "min":
            indicator = GenericIndicatorRegistry.lookup("MinOfRollingSum")
        else:
            raise NotImplementedError()
    elif calc_op == CalcOperationRegistry.RUN_MEAN:
        if user_index["extreme_mode"] == "max":
            indicator = GenericIndicatorRegistry.lookup("MaxOfRollingAverage")
        elif user_index["extreme_mode"] == "min":
            indicator = GenericIndicatorRegistry.lookup("MinOfRollingAverage")
        else:
            raise NotImplementedError()
    else:
        indicator = user_index_map.get(calc_op)
    if indicator is None:
        raise InvalidIcclimArgumentError(
            f"Unknown user_index calc_operation:" f" '{user_index['calc_operation']}'"
        )
    return indicator


def read_thresholds(
    user_index: UserIndexDict, _build_threshold: Callable[[str | Threshold], Threshold]
) -> Threshold | None | Sequence[Threshold]:
    thresh = user_index.get("thresh", None)
    if thresh is None or isinstance(thresh, Threshold):
        return thresh
    # todo [BoundedThreshold] re-add below code and bind to LogicalLink
    # or (
    #     isinstance(thresh, (tuple, list))
    #     and all(map(lambda th: isinstance(th, Threshold), thresh))
    # )
    logical_operation = user_index["logical_operation"]
    if not isinstance(logical_operation, (tuple, list)):
        logical_operation = [logical_operation]
    logical_operations = [OperatorRegistry.lookup(op) for op in logical_operation]
    var_type = user_index.get("var_type", None)
    if not isinstance(thresh, (tuple, list)):
        return read_threshold(thresh, var_type, logical_operations[0], _build_threshold)
    return [
        read_threshold(t, var_type, logical_operations[i], _build_threshold)
        for i, t in enumerate(thresh)
    ]


def read_threshold(
    query: str | float,
    var_type: Literal["t", "p"] | None,
    logical_operation: Operator,
    _build_threshold: Callable[[str], Threshold],
) -> Threshold:
    if isinstance(query, str) and query.endswith(PERCENTILE_THRESHOLD_STAMP):
        if var_type == USER_INDEX_TEMPERATURE_STAMP:
            replace_unit = "doy_per"
        elif var_type == USER_INDEX_PRECIPITATION_STAMP:
            replace_unit = "period_per"
        else:
            replace_unit = "period_per"  # default to period percentiles ?
        t = query.replace(PERCENTILE_THRESHOLD_STAMP, " " + replace_unit)
    else:
        t = str(query)
    return _build_threshold(str(logical_operation.operand + t))


def read_logical_link(user_index: UserIndexDict) -> LogicalLink:
    # todo add unit test using it
    logical_link = user_index.get("link_logical_operations", None)
    if logical_link is None:
        return LogicalLinkRegistry.LOGICAL_AND
    else:
        return LogicalLinkRegistry.lookup(logical_link)


def read_coef(user_index: UserIndexDict) -> float | None:
    # todo add unit test using it
    return user_index.get("coef", None)


def read_date_event(user_index: UserIndexDict) -> float | None:
    # todo add unit test using it
    return user_index.get("date_event", False)


def _must_add_reference_var(
    climate_vars_dict: dict[str, InFileDictionary],
    reference_period: Sequence[str] | None,
) -> bool:
    """True whenever the input has no threshold and only one studied variable but there
    is a reference period.
    Example case: the anomaly of tx(1960-2100) by tx(1960-1990).
    """
    t = list(climate_vars_dict.values())[0].get("thresholds", None)
    return t is None and len(climate_vars_dict) == 1 and reference_period is not None
