# -*- Coding: latin-1 -*-
#  Copyright CERFACS (http://cerfacs.fr/)
#  Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
"""
Main entry point of icclim.
This module expose the index API endpoint as long as a few other functions.
"""
from __future__ import annotations

import logging
import time
from datetime import datetime
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
from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.icclim_logger import IcclimLogger, Verbosity, VerbosityRegistry
from icclim.icclim_types import InFileType
from icclim.models.climate_variable import (
    ClimateVariable,
    build_climate_vars,
    must_add_reference_var,
    to_dictionary,
)
from icclim.models.constants import ICCLIM_VERSION, UNITS_ATTRIBUTE_KEY
from icclim.models.frequency import Frequency, FrequencyLike, FrequencyRegistry
from icclim.models.index_config import IndexConfig
from icclim.models.index_group import IndexGroup, IndexGroupRegistry
from icclim.models.netcdf_version import NetcdfVersion, NetcdfVersionRegistry
from icclim.models.quantile_interpolation import (
    QuantileInterpolation,
    QuantileInterpolationRegistry,
)
from icclim.models.standard_index import StandardIndex
from icclim.models.threshold import Threshold
from icclim.models.user_index_config import UserIndexConfig
from icclim.models.user_index_dict import UserIndexDict
from icclim.user_indices.calc_operation import CalcOperationRegistry, compute_user_index
from icclim.utils import read_date

log: IcclimLogger = IcclimLogger.get_instance(VerbosityRegistry.LOW)

HISTORY_CF_KEY = "history"
SOURCE_CF_KEY = "source"


def indices(
    index_group: Literal["all"] | str | IndexGroup | Sequence[str],
    ignore_error: bool = False,
    **kwargs,
) -> Dataset:
    """
    Compute multiple indices at the same time.
    The input dataset(s) must include all the necessary variables.
    It can only be used with keyword arguments (kwargs)

    Parameters
    ----------
    index_group : "all" | str | IndexGroup | list[str]
        Either the name of an IndexGroup, a instance of IndexGroup or a list
        of index short names.
        The value "all" can also be used to compute every indices.
        Note that the input given by ``in_files`` must include all the necessary
        variables to compute the indices of this group.
    kwargs : Dict
        ``icclim.index`` keyword arguments.

    Returns
    -------
    xr.Dataset
        A Dataset with one data variable per index.

    .. notes
        If ``output_file`` is part of kwargs, the result is written in a single netCDF
        file, which will contain all the index results of this group.

    """
    if isinstance(index_group, (tuple, list)):
        indices = [EcadIndexRegistry.lookup(i) for i in index_group]
    elif index_group == IndexGroupRegistry.WILD_CARD_GROUP or (
        isinstance(index_group, str)
        and index_group.lower() == IndexGroupRegistry.WILD_CARD_GROUP.name
    ):
        indices = EcadIndexRegistry.values()
    else:
        indices = IndexGroupRegistry.lookup(index_group).get_indices()
    out = None
    if "out_file" in kwargs.keys():
        out = kwargs["out_file"]
        del kwargs["out_file"]
    acc = []
    for i in indices:
        kwargs["index_name"] = i.short_name
        if ignore_error:
            try:
                acc.append(index(**kwargs))
            except Exception:
                warn(f"Could not compute {i.short_name}.")
        else:
            acc.append(index(**kwargs))
    ds: Dataset = xr.merge(acc)
    if out is not None:
        _write_output_file(
            result_ds=ds,
            input_time_encoding=ds.time.encoding,
            netcdf_version=kwargs.get("netcdf_version", NetcdfVersionRegistry.NETCDF4),
            file_path=out,
        )
    return ds


def indice(*args, **kwargs):
    """
    Deprecated proxy for `icclim.index` function.
    To be deleted in a futur version.
    """
    log.deprecation_warning(old="icclim.indice", new="icclim.index")
    return index(*args, **kwargs)


def generic(
    in_files: InFileType,
    index_name=GenericIndicatorRegistry.CountOccurrences.name,
    **kwargs,
) -> Dataset:
    # TODO: instead of `icclim.generic`,
    #       it would make more sense to have each reducer as part of the public API.
    #       In which case, `reducer` and `index_name` could be merged together
    #       (at api level).
    return index(
        in_files=in_files,
        index_name=index_name,
        **kwargs,
    )


def index(
    in_files: InFileType,
    index_name: str | None = None,  # optional when computing user_indices
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = "year",
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    threshold: str | Threshold | Sequence[str | Threshold] = None,
    callback: Callable[[int], None] = log.callback,
    callback_percentage_start_value: int = 0,
    callback_percentage_total: int = 100,
    base_period_time_range: Sequence[datetime | str] | None = None,
    window_width: int = 5,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: str | QuantileInterpolation = "median_unbiased",
    out_unit: str | None = None,
    netcdf_version: str | NetcdfVersion = "NETCDF4",
    user_index: UserIndexDict | None = None,
    save_percentile: bool = False,
    save_thresholds: bool = False,
    logs_verbosity: Verbosity | str = "LOW",
    indice_name: str = None,
    user_indice: UserIndexDict = None,
    transfer_limit_Mbytes: float = None,
) -> Dataset:
    """
    Main entry point for icclim to compute climate indices.

    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray | InputDictionary,
        Absolute path(s) to NetCDF dataset(s), including OPeNDAP URLs,
        or path to zarr store, or xarray.Dataset or xarray.DataArray.
    index_name : str
        Climate index name.
        For ECA&D index, case insensitive name used to lookup the index.
        For user index, it's the name of the output variable.
    var_name : str | list[str] | None
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : SliceMode
        Type of temporal aggregation:
        The possibles values are ``{"year", "month", "DJF", "MAM", "JJA", "SON",
        "ONDJFM" or "AMJJAS", ("season", [1,2,3]), ("month", [1,2,3,])}``
        (where season and month lists can be customized) or any valid pandas frequency.
        A season can also be defined between two exact dates:
        ``("season", ("19 july", "14 august"))``.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime ] | list[str]  | tuple[str, str] | None
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        The dates can either be given as instance of datetime.datetime or as string
        values. For strings, many format are accepted.
        Default is ``None``.
    out_file : str | None
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    threshold : float | list[float] | None
        ``optional`` User defined threshold for certain indices.
        Default depend on the index, see their individual definition.
        When a list of threshold is provided, the index will be computed for each
        thresholds.
    transfer_limit_Mbytes : float
        Deprecated, does not have any effect.
    callback : Callable[[int], None]
        ``optional`` Progress bar printing. If ``None``, progress bar will not be
        printed.
    callback_percentage_start_value : int
        ``optional`` Initial value of percentage of the progress bar (default: 0).
    callback_percentage_total : int
        ``optional`` Total percentage value (default: 100).
    base_period_time_range : list[datetime ] | list[str]  | tuple[str, str] | None
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
    window_width : int
        ``optional`` User defined window width for related indices (default: 5).
        Ignored for non related indices.
    only_leap_years : bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation : str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "median_unbiased"}``
        Default is "median_unbiased", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    out_unit : str | None
        ``optional`` Output unit for certain indices: "days" or "%" (default: "days").
    netcdf_version : str | NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    user_index : UserIndexDict
        ``optional`` A dictionary with parameters for user defined index.
        See :ref:`Custom indices`.
        Ignored for ECA&D indices.
    save_percentile : bool
        ``optional`` True if the percentiles should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity : str | Verbosity
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    indice_name : str | None
        DEPRECATED, use index_name instead.
    user_indice : dict | None
        DEPRECATED, use user_index instead.

    """
    _setup(callback, callback_percentage_start_value, logs_verbosity)
    index_name, user_index, save_thresholds = _handle_deprecated_params(
        index_name,
        user_index,
        save_thresholds,
        indice_name,
        transfer_limit_Mbytes,
        user_indice,
        save_percentile,
    )
    del indice_name, transfer_limit_Mbytes, user_indice, save_percentile
    # -- Choose index to compute
    if user_index is None and index_name is None:
        raise InvalidIcclimArgumentError(
            "No index to compute."
            " You must provide either `user_index` to compute a customized index"
            " or `index_name` for one of the ECA&D indices."
        )
    interpolation = QuantileInterpolationRegistry.lookup(interpolation)
    build_threshold = _get_threshold_builder(
        doy_window_width=window_width,
        base_period_time_range=base_period_time_range,
        only_leap_years=only_leap_years,
        interpolation=interpolation,
    )
    indicator: GenericIndicator | None
    standard_index: StandardIndex | None = None
    if index_name is not None:
        standard_index = EcadIndexRegistry.lookup(index_name, no_error=True)
        if standard_index is None:
            indicator = GenericIndicatorRegistry.lookup(index_name)
            rename = None
            output_unit = out_unit
        else:
            indicator = standard_index.generic_indicator
            threshold = standard_index.threshold
            rename = standard_index.short_name
            output_unit = out_unit or standard_index.output_unit
    else:
        indicator = None
        rename = None
        output_unit = out_unit
    sampling_frequency = FrequencyRegistry.lookup(slice_mode)
    if isinstance(threshold, str):
        threshold = build_threshold(threshold)
    elif isinstance(threshold, Sequence):
        threshold = [build_threshold(t) for t in threshold]
    climate_vars_dict = to_dictionary(
        in_files=in_files,
        var_names=var_name,
        threshold=threshold,
        standard_index=standard_index,
    )
    # We use groupby instead of resample when there is a single variable that must be
    # compared to its reference period values.
    is_single_var = must_add_reference_var(
        threshold, climate_vars_dict, base_period_time_range
    )
    indicator_name = standard_index.short_name if standard_index else indicator.name
    climate_vars = build_climate_vars(
        climate_vars_dict=climate_vars_dict,
        ignore_Feb29th=ignore_Feb29th,
        threshold=threshold,
        time_range=time_range,
        base_period=base_period_time_range,
        standard_index=standard_index,
        indicator_name=indicator_name,
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
        window=window_width,
        out_unit=output_unit,
        netcdf_version=NetcdfVersionRegistry.lookup(netcdf_version),
        interpolation=interpolation,
        callback=callback,
        is_single_var=is_single_var,
        reference_period=reference_period,  # noqa
        indicator_name=indicator_name,
    )
    if user_index is not None:
        # todo: replace by user_index -> generic index
        result_ds = _compute_custom_climate_index(config=config, user_index=user_index)
    else:
        result_ds = _compute_standard_climate_index(
            climate_index=indicator,
            config=config,
            initial_history=climate_vars[0].global_metadata["history"],
            initial_source=climate_vars[0].global_metadata["source"],
            rename=rename,
        )
    if reset := result_ds.attrs.get("reset_coords_dict", None):
        result_ds = result_ds.rename(reset)
        del result_ds.attrs["reset_coords_dict"]
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
            UNITS_ATTRIBUTE_KEY: input_time_encoding.get(UNITS_ATTRIBUTE_KEY),
            "dtype": input_time_encoding.get("dtype"),
        }
    else:
        time_encoding = {UNITS_ATTRIBUTE_KEY: "days since 1850-1-1"}
    result_ds.to_netcdf(
        file_path,
        format=netcdf_version.name,
        encoding={"time": time_encoding},
    )


def _handle_deprecated_params(
    index_name,
    user_index,
    save_thresholds,
    indice_name,
    transfer_limit_Mbytes,
    user_indice,
    save_percentile,
) -> tuple[str, UserIndexDict, bool]:
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
    return index_name, user_index, save_thresholds


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


def _compute_custom_climate_index(
    config: IndexConfig, user_index: UserIndexDict
) -> Dataset:
    logging.info("Calculating user index.")
    result_ds = Dataset()
    deprecated_name = user_index.get("indice_name", None)
    if deprecated_name is not None:
        user_index["index_name"] = deprecated_name
        del user_index["indice_name"]
        log.deprecation_warning("indice_name", "index_name")
    user_indice_config = UserIndexConfig(
        **user_index,
        freq=config.frequency,
        climate_variables=config.climate_variables,
        is_percent=config.is_percent,
        save_percentile=config.save_thresholds,
    )
    user_indice_da = compute_user_index(user_indice_config)
    user_indice_da.attrs[UNITS_ATTRIBUTE_KEY] = _get_unit(
        config.out_unit, user_indice_da
    )
    if user_indice_config.calc_operation is CalcOperationRegistry.ANOMALY:
        # with anomaly time axis disappear
        result_ds[user_indice_config.index_name] = user_indice_da
        return result_ds
    user_indice_da, time_bounds = config.frequency.post_processing(user_indice_da)
    result_ds[user_indice_config.index_name] = user_indice_da
    result_ds["time_bounds"] = time_bounds
    return result_ds


def _get_unit(output_unit: str | None, da: DataArray) -> str | None:
    da_unit = da.attrs.get(UNITS_ATTRIBUTE_KEY, None)
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


def _compute_standard_climate_index(
    climate_index: GenericIndicator | None,
    config: IndexConfig,
    initial_history: str | None,
    initial_source: str,
    rename: str | None = None,
) -> Dataset:
    result_da = climate_index(config)
    if rename:
        result_da = result_da.rename(rename)
    else:
        result_da = result_da.rename(climate_index.identifier)
    result_da.attrs[UNITS_ATTRIBUTE_KEY] = _get_unit(config.out_unit, result_da)
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
        result_ds, climate_index, history, initial_source
    )
    return result_ds


def _add_ecad_index_metadata(
    result_ds: Dataset,
    computed_index: Indicator,
    history: str,
    initial_source: str,
) -> Dataset:
    result_ds.attrs.update(
        dict(
            title=computed_index.standard_name,
            references="ATBD of the ECA&D indices calculation"
            " (https://knmi-ecad-assets-prd.s3.amazonaws.com/documents/atbd.pdf)",
            institution="Climate impact portal (https://climate4impact.eu)",
            history=history,
            source=initial_source if initial_source is not None else "",
            Conventions="CF-1.6",
        )
    )
    result_ds.lat.encoding["_FillValue"] = None
    result_ds.lon.encoding["_FillValue"] = None
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
        f" Calculation of {indice_computed.identifier}"
        f" index ({config.frequency.adjective})"
        f" - icclim version: {ICCLIM_VERSION}"
    )


def _get_threshold_builder(
    doy_window_width: int,
    base_period_time_range: Sequence[datetime | str] | None,
    only_leap_years: bool,
    interpolation: QuantileInterpolation,
) -> Callable:
    def build_threshold(t: str | Threshold):
        if isinstance(t, Threshold):
            return t
        else:
            return Threshold(
                t,
                doy_window_width=doy_window_width,
                reference_period=base_period_time_range,
                only_leap_years=only_leap_years,
                interpolation=interpolation,
            )

    return build_threshold


def _format_thresholds_for_export(climate_vars: list[ClimateVariable]) -> Dataset:
    return xr.merge([_format_threshold(v) for v in climate_vars])


def _format_threshold(cf_var: ClimateVariable) -> DataArray:
    return cf_var.threshold.value.rename(cf_var.name + "_thresholds").reindex()
