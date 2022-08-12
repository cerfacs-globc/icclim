# -*- Coding: latin-1 -*-
#  Copyright CERFACS (http://cerfacs.fr/)
#  Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
"""
Main entry point of icclim.
This module expose the index API endpoint as long as a few other functions.
"""
from __future__ import annotations

import copy
import logging
import time
from datetime import datetime
from typing import Callable, Literal, Sequence
from warnings import warn

import xarray as xr
import xclim
from xarray.core.dataarray import DataArray
from xarray.core.dataset import Dataset

from icclim.ecad.ecad_functions import IndexConfig
from icclim.ecad.ecad_indices import EcadIndexRegistry, get_season_excluded_indices
from icclim.generic_indices.generic_indicators import (
    GenericIndicatorRegistry,
    Indicator,
)
from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.icclim_logger import IcclimLogger, Verbosity, VerbosityRegistry
from icclim.models.climate_index import ClimateIndex
from icclim.models.climate_variable import read_climate_vars
from icclim.models.constants import ICCLIM_VERSION, UNITS_ATTRIBUTE_KEY
from icclim.models.frequency import Frequency, FrequencyLike, FrequencyRegistry
from icclim.models.index_group import IndexGroup, IndexGroupRegistry
from icclim.models.netcdf_version import NetcdfVersion, NetcdfVersionRegistry
from icclim.models.quantile_interpolation import QuantileInterpolationRegistry
from icclim.models.threshold import Threshold
from icclim.models.user_index_config import UserIndexConfig
from icclim.models.user_index_dict import UserIndexDict
from icclim.pre_processing.input_parsing import InFileType
from icclim.user_indices.calc_operation import CalcOperationRegistry, compute_user_index

log: IcclimLogger = IcclimLogger.get_instance(VerbosityRegistry.LOW)

HISTORY_CF_KEY = "history"
SOURCE_CF_KEY = "source"
GENERIC_THRESHOLD_KEY = "generic_threshold"


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
        and index_group.lower() == IndexGroupRegistry.WILD_CARD_GROUP.value
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
    indicator=GenericIndicatorRegistry.CountOccurrences.name,
    **kwargs,
) -> Dataset:
    # TODO: instead of `icclim.generic`,
    #       it would make more sense to have each reducer as part of the public API.
    #       In which case, `reducer` and `index_name` could be merged together
    #       (at api level).
    if kwargs.get("index_name"):
        raise InvalidIcclimArgumentError("With generic, index_name must be empty")
    return index(
        in_files=in_files,
        index_name=GENERIC_THRESHOLD_KEY,
        indicator=indicator,
        **kwargs,
    )


def index(
    in_files: InFileType,
    index_name: str | None = None,  # optional when computing user_indices
    var_name: str | Sequence[str] | None = None,
    slice_mode: FrequencyLike | Frequency = FrequencyRegistry.YEAR,
    time_range: Sequence[datetime | str] | None = None,
    out_file: str | None = None,
    threshold: str | Threshold = None,
    indicator: str | Indicator = None,
    callback: Callable[[int], None] = log.callback,
    callback_percentage_start_value: int = 0,
    callback_percentage_total: int = 100,
    base_period_time_range: Sequence[datetime | str] | None = None,
    window_width: int = 5,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: (
        str | QuantileInterpolationRegistry | None
    ) = QuantileInterpolationRegistry.MEDIAN_UNBIASED,
    out_unit: str | None = None,
    netcdf_version: str | NetcdfVersion = NetcdfVersionRegistry.NETCDF4,
    user_index: UserIndexDict | None = None,
    save_percentile: bool = False,
    logs_verbosity: Verbosity | str = VerbosityRegistry.LOW,
    # deprecated parameters
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
        ``optional`` Temporal range of the reference period on which percentiles are
        computed.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if  `time_range` is None.
        On temperature based indices relying on percentiles (TX90p, WSDI...), the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        On indices not relying on percentiles, this parameter is ignored.
        The dates can either be given as instance of datetime.datetime or as string
        values.
        For strings, many format are accepted.
    window_width : int
        ``optional`` User defined window width for related indices (default: 5).
        Ignored for non related indices.
    only_leap_years : bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation : str | QuantileInterpolation | None
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "hyndman_fan"}``
        Default is "hyndman_fan", a.k.a type 8 or method 8.
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
    index_name, user_index = _handle_deprecated_params(
        index_name, indice_name, transfer_limit_Mbytes, user_index, user_indice
    )
    # -- Choose index to compute
    if user_index is None and index_name is None:
        raise InvalidIcclimArgumentError(
            "No index to compute."
            " You must provide either `user_index` to compute a customized index"
            " or `index_name` for one of the ECA&D indices."
        )
    interpolation = QuantileInterpolationRegistry.lookup(interpolation)
    if isinstance(threshold, str):
        # merge the icclim.index flat parameters
        threshold = Threshold(
            threshold,
            doy_window_width=window_width,
            base_period_time_range=base_period_time_range,
            only_leap_years=only_leap_years,
            interpolation=interpolation,
        )
    elif isinstance(threshold, Sequence):
        threshold = [
            Threshold(
                t,
                doy_window_width=window_width,
                base_period_time_range=base_period_time_range,
                only_leap_years=only_leap_years,
                interpolation=interpolation,
            )
            for t in threshold
        ]
    if index_name is not None:
        if (
            ecad_index := EcadIndexRegistry.lookup(index_name, no_error=True)
        ) is not None:
            index = ecad_index
            if threshold is not None:
                raise InvalidIcclimArgumentError(
                    "ECAD indices threshold cannot be "
                    "configured. Use a generic index "
                    "instead."
                )
        elif index_name == GENERIC_THRESHOLD_KEY:
            index = GenericIndicatorRegistry.lookup(indicator)
        else:
            raise InvalidIcclimArgumentError(f"Unknown index {index_name}.")
    else:
        index = None
    sampling_frequency = FrequencyRegistry.lookup(slice_mode)
    climate_vars = read_climate_vars(
        ignore_Feb29th,
        in_files,
        index,
        sampling_frequency,
        threshold,
        time_range,
        var_name,
    )
    config = IndexConfig(
        save_percentile=save_percentile,
        frequency=sampling_frequency,
        climate_variables=climate_vars,
        window=window_width,
        out_unit=out_unit,
        netcdf_version=NetcdfVersionRegistry.lookup(netcdf_version),
        interpolation=interpolation,
        callback=callback,
        index=index,
    )
    if user_index is not None:
        result_ds = _compute_custom_climate_index(config=config, user_index=user_index)
    else:
        _check_valid_config(index, config)
        result_ds = _compute_standard_climate_index(
            config=config,
            climate_index=index,
            initial_history=climate_vars[0].global_metadata["history"],
            initial_source=climate_vars[0].global_metadata["source"],
        )
    if reset := result_ds.attrs.get("reset_coords_dict", None):
        result_ds = result_ds.rename(reset)
        del result_ds.attrs["reset_coords_dict"]
    if out_file is not None:
        _write_output_file(
            result_ds,
            climate_vars[0].global_metadata["time_encoding"],
            netcdf_version,
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
        format=netcdf_version.value,
        encoding={"time": time_encoding},
    )


def _handle_deprecated_params(
    index_name, indice_name, transfer_limit_Mbytes, user_index, user_indice
) -> tuple[str, UserIndexDict]:
    if indice_name is not None:
        log.deprecation_warning(old="indice_name", new="index_name")
        index_name = indice_name
    if user_indice is not None:
        log.deprecation_warning(old="user_indice", new="user_index")
        user_index = user_indice
    if transfer_limit_Mbytes is not None:
        log.deprecation_warning(old="transfer_limit_Mbytes")
    return index_name, user_index


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
        save_percentile=config.save_percentile,
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
    climate_index: Indicator,
    config: IndexConfig,
    initial_history: str | None,
    initial_source: str,
) -> Dataset:
    # todo remove config as it's very likely useless with generic indicators
    def compute(threshold: float | None = None):
        conf = copy.copy(config)
        if threshold is not None:
            conf.scalar_thresholds = threshold
        if config.frequency.time_clipping is not None:
            # xclim missing values checking system will not work with clipped time
            with xclim.set_options(check_missing="skip"):
                res = climate_index(conf)
        else:
            res = climate_index(conf)  # todo need to merge ClimateIndex and Indicator
        if isinstance(res, tuple):
            return res
        else:
            return res, None

    result_da, percentiles_da = compute()
    result_da = result_da.rename(climate_index.identifier)
    result_da.attrs[UNITS_ATTRIBUTE_KEY] = _get_unit(config.out_unit, result_da)
    if config.frequency.post_processing is not None:
        resampled_da, time_bounds = config.frequency.post_processing(result_da)
        result_ds = resampled_da.to_dataset()
        if time_bounds is not None:
            result_ds["time_bounds"] = time_bounds
            result_ds.time.attrs["bounds"] = "time_bounds"
    else:
        result_ds = result_da.to_dataset()
    if percentiles_da is not None:
        result_ds = xr.merge([result_ds, percentiles_da])
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
        initial_history = f"{initial_history}\n{result_da.attrs['history']}"
    del result_da.attrs[HISTORY_CF_KEY]
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_time = result_da.time[0].dt.strftime("%m-%d-%Y").data[()]
    end_time = result_da.time[-1].dt.strftime("%m-%d-%Y").data[()]
    return (
        f"{initial_history}\n"
        f" [{current_time}]"
        f" Calculation of {indice_computed.identifier}"
        f" index ({config.frequency.adjective})"
        f" from {start_time} to {end_time}"
        f" - icclim version: {ICCLIM_VERSION}"
    )


def _check_valid_config(index: ClimateIndex, config: IndexConfig):
    if index in get_season_excluded_indices() and config.frequency.indexer is not None:
        raise InvalidIcclimArgumentError(
            "Indices computing a spell cannot be computed on un-clipped season for now."
            " Instead, you can use a clipped_season like this:"
            "`slice_mode=['clipped_season', [12,1,2]]` (example of a DJF season)."
            " However, it will NOT take into account spells beginning before the season"
            " start!"
        )
