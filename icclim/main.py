# -*- Coding: latin-1 -*-
#  Copyright CERFACS (http://cerfacs.fr/)
#  Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
"""
Main module of icclim.
"""
from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Callable, Literal
from warnings import warn

import xarray as xr
import xclim
from xarray.core.dataarray import DataArray
from xarray.core.dataset import Dataset

from icclim.ecad_functions import IndexConfig
from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.icclim_logger import IcclimLogger, Verbosity
from icclim.models.ecad_indices import EcadIndex
from icclim.models.frequency import Frequency, SliceMode
from icclim.models.index_group import IndexGroup
from icclim.models.netcdf_version import NetcdfVersion
from icclim.models.quantile_interpolation import QuantileInterpolation
from icclim.models.user_index_config import UserIndexConfig
from icclim.models.user_index_dict import UserIndexDict
from icclim.pre_processing.input_parsing import read_dataset, update_to_standard_coords
from icclim.user_indices.calc_operation import CalcOperation, compute_user_index

log: IcclimLogger = IcclimLogger.get_instance(Verbosity.LOW)


def indices(
    index_group: Literal["all"] | str | IndexGroup | list[str],
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
    if isinstance(index_group, list):
        indices = [EcadIndex.lookup(i) for i in index_group]
    elif index_group == IndexGroup.WILD_CARD_GROUP or (
        isinstance(index_group, str)
        and index_group.lower() == IndexGroup.WILD_CARD_GROUP.value
    ):
        indices = iter(EcadIndex)
    else:
        indices = IndexGroup.lookup(index_group).get_indices()
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
            netcdf_version=kwargs.get("netcdf_version", NetcdfVersion.NETCDF4),
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


def index(
    in_files: str | list[str] | Dataset | DataArray,
    index_name: str | None = None,  # optional when computing user_indices
    var_name: str | list[str] | None = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: list[datetime] = None,
    out_file: str | None = None,
    threshold: float | list[float] | None = None,
    callback: Callable[[int], None] = log.callback,
    callback_percentage_start_value: int = 0,
    callback_percentage_total: int = 100,
    base_period_time_range: list[datetime] | None = None,
    window_width: int = 5,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: (
        str | QuantileInterpolation | None
    ) = QuantileInterpolation.MEDIAN_UNBIASED,
    out_unit: str | None = None,
    netcdf_version: str | NetcdfVersion = NetcdfVersion.NETCDF4,
    user_index: UserIndexDict = None,
    save_percentile: bool = False,
    logs_verbosity: Verbosity | str = Verbosity.LOW,
    # deprecated parameters
    indice_name: str = None,
    user_indice: UserIndexDict = None,
    transfer_limit_Mbytes: float = None,
) -> Dataset:
    """
    Parameters
    ----------
    in_files : str | list[str] | Dataset | DataArray,
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
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : list[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
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
    base_period_time_range : list[datetime.datetime]
        ``optional`` Temporal range of the reference period on which percentiles are
        computed.
        When missing, the studied period is used to compute percentiles.
        The study period is either the dataset filtered by `time_range` or the whole
        dataset if  `time_range` is None.
        On temperature based indices relying on percentiles (TX90p, WSDI...), the
        overlapping period between `base_period_time_range` and the study period is
        bootstrapped.
        On indices not relying on percentiles, this parameter is ignored.
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
    netcdf_version : str | icclim.models.netcdf_version.NetcdfVersion
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
    _setup(callback, callback_percentage_start_value, logs_verbosity, slice_mode)
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
    index: EcadIndex | None
    if index_name is not None:
        index = EcadIndex.lookup(index_name)
    else:
        index = None
    input_dataset, chunk_it, _ = read_dataset(in_files, index, var_name)
    ds, reset_coords_dict = update_to_standard_coords(input_dataset)
    config = IndexConfig(
        base_period_time_range=base_period_time_range,
        ds=ds,
        ignore_Feb29th=ignore_Feb29th,
        only_leap_years=only_leap_years,
        save_percentile=save_percentile,
        slice_mode=slice_mode,
        time_range=time_range,
        var_names=_guess_variable_names(var_name, index, ds),
        window_width=window_width,
        out_unit=out_unit,
        netcdf_version=netcdf_version,
        interpolation=interpolation,
        callback=callback,
        index=index,
        chunk_it=chunk_it,
    )
    if user_index is not None:
        result_ds = _compute_user_index_dataset(config=config, user_index=user_index)
    else:
        result_ds = _compute_ecad_index_dataset(
            config=config,
            index=index,
            threshold=threshold,
            current_history=ds.attrs.get("history", None),
        )
    if reset_coords_dict:
        result_ds = result_ds.rename(reset_coords_dict)
    if out_file is not None:
        _write_output_file(result_ds, ds.time.encoding, config.netcdf_version, out_file)
    callback(callback_percentage_total)
    log.ending_message(time.process_time())
    return result_ds


def _write_output_file(
    result_ds: xr.Dataset,
    input_time_encoding: dict,
    netcdf_version: NetcdfVersion,
    file_path: str,
) -> None:
    """
    Write `result_ds` to a netCDF file on `out_file` path.
    """
    if input_time_encoding:
        time_encoding = {
            "calendar": input_time_encoding.get("calendar"),
            "units": input_time_encoding.get("units"),
            "dtype": input_time_encoding.get("dtype"),
        }
    else:
        time_encoding = {"units": "days since 1850-1-1"}
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


def _setup(callback, callback_start_value, logs_verbosity, slice_mode):
    # make xclim input daily check a warning instead of an error
    # TODO: it might be safer to feed a context manager which will setup
    #       and teardown these confs
    xclim.set_options(data_validation="warn")
    if Frequency.is_seasonal(slice_mode):
        # for now seasonal slice_modes missing values cannot be checked
        xclim.set_options(check_missing="skip")
    # keep attributes through xarray operations
    xr.set_options(keep_attrs=True)
    log.set_verbosity(logs_verbosity)
    log.start_message()
    callback(callback_start_value)


def _compute_ecad_index_dataset(
    config: IndexConfig,
    index: EcadIndex,
    threshold: float | list[float],
    current_history: str | None,
) -> Dataset:
    if isinstance(threshold, list):
        ds_list = []
        for th in threshold:
            config.threshold = th
            ds_list.append(_compute_ecad_index(index, config, current_history))
        result_ds = xr.concat(ds_list, dim="threshold")
    else:
        config.threshold = threshold
        result_ds = _compute_ecad_index(index, config, current_history)
    return result_ds


def _compute_user_index_dataset(
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
        freq=config.freq,
        cf_vars=config._cf_variables,
        is_percent=config.is_percent,
        save_percentile=config.save_percentile,
    )
    user_indice_da = compute_user_index(user_indice_config)
    user_indice_da.attrs["units"] = _get_unit(config.out_unit, user_indice_da)
    if user_indice_config.calc_operation is CalcOperation.ANOMALY:
        # with anomaly time axis disappear
        result_ds[user_indice_config.index_name] = user_indice_da
        return result_ds
    user_indice_da, time_bounds = config.freq.post_processing(user_indice_da)
    result_ds[user_indice_config.index_name] = user_indice_da
    result_ds["time_bounds"] = time_bounds
    return result_ds


def _get_unit(output_unit: str | None, da: DataArray) -> str | None:
    da_unit = da.attrs.get("units", None)
    if da_unit is None:
        if output_unit is None:
            warn(
                "No unit computed or provided for the index was found. "
                "Use out_unit parameter to add one."
            )
            return ""
        else:
            return output_unit
    else:
        return da_unit


def _compute_ecad_index(
    index: EcadIndex, config: IndexConfig, former_history: str | None
) -> Dataset:
    logging.info(f"Calculating climate index: {index.short_name}")
    result_ds = Dataset()
    res = index.compute(config)
    if isinstance(res, tuple):
        da, per = res
    else:
        da, per = (res, None)
    da.attrs["units"] = _get_unit(config.out_unit, da)
    if config.threshold is not None:
        da.expand_dims({"threshold": config.threshold})
    if config.freq.post_processing is not None:
        resampled_da, time_bounds = config.freq.post_processing(da)
        result_ds[index.short_name] = resampled_da
        if time_bounds is not None:
            result_ds["time_bounds"] = time_bounds
            result_ds.time.attrs["bounds"] = "time_bounds"
    else:
        result_ds[index.short_name] = da
    if per is not None:
        per = per.squeeze("percentiles", drop=True).rename("percentiles")
        result_ds = xr.merge([result_ds, per])
    if former_history is None:
        former_history = da.attrs["history"]
    else:
        former_history = f"{former_history}\n{da.attrs['history']}"
    del da.attrs["history"]
    result_ds = _add_ecad_index_metadata(result_ds, config, index, former_history)
    return result_ds


def _add_ecad_index_metadata(
    result_ds: Dataset,
    config: IndexConfig,
    computed_index: EcadIndex,
    former_history: str,
) -> Dataset:
    result_ds.attrs.update(
        dict(
            title=_get_title(computed_index, config),
            references="ATBD of the ECA&D indices calculation"
            " (https://www.ecad.eu/documents/atbd.pdf)",
            institution="Climate impact portal (https://climate4impact.eu)",
            history=_get_history(config, former_history, computed_index, result_ds),
            source="",
            Conventions="CF-1.6",
        )
    )
    result_ds.lat.encoding["_FillValue"] = None
    result_ds.lon.encoding["_FillValue"] = None
    return result_ds


def _get_title(computed_index, config):
    if config.threshold is not None:
        return f"Index {computed_index.short_name} with user defined threshold"
    else:
        return f"ECA&D {computed_index.group.value} index {computed_index.short_name}"


def _get_history(config, former_history, indice_computed, result_ds):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_time = result_ds.time[0].dt.strftime("%m-%d-%Y").data[()]
    end_time = result_ds.time[-1].dt.strftime("%m-%d-%Y").data[()]
    return (
        f"{former_history}\n "
        f"{current_time} "
        f"Calculation of {indice_computed.short_name} "
        f"index({config.freq.description}) "
        f"from {start_time} to {end_time}."
    )


def _has_valid_unit(group: IndexGroup, da: DataArray) -> bool:
    if group == IndexGroup.SNOW:
        try:
            # todo: might be replaced by cf-xarray
            xclim.core.units.check_units.__wrapped__(da, "[length]")
        except xclim.core.utils.ValidationError:
            return False
    # For now we can delay to xclim other unit checks
    return True


def _guess_variable_names(
    in_var_name: str | list[str], index: EcadIndex | None, ds: Dataset
) -> list[str]:
    """
    Try to guess the variable names using the expected kind of variable for
    the index.
    """
    if isinstance(in_var_name, str):
        return [in_var_name]
    res = []
    index_variables = index.variables
    for indice_var in index_variables:
        for alias in indice_var:
            # check if dataset contains this alias
            if ds.get(alias, None) is not None and _has_valid_unit(
                index.group, ds[alias]
            ):
                res.append(alias)
                break
    if len(res) < len(index_variables):
        main_aliases = ", ".join(map(lambda v: v[0], index_variables))
        raise InvalidIcclimArgumentError(
            f"Index {index.short_name} needs the following variable(s)"
            f" [{main_aliases}], some of these were not recognized from the input."
            f" Use `var_name` parameter to explicitly use the data variable(s)"
            f" from your input dataset: {list(ds.data_vars)}."
        )
    return res
