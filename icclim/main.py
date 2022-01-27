# -*- Coding: latin-1 -*-
#  Copyright CERFACS (http://cerfacs.fr/)
#  Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
"""
Main module of icclim.
"""

import logging
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from warnings import warn

import xarray
import xarray as xr
import xclim
from xarray.core.dataarray import DataArray
from xarray.core.dataset import Dataset

from icclim.ecad_functions import IndexConfig
from icclim.icclim_exceptions import InvalidIcclimArgumentError
from icclim.icclim_logger import IcclimLogger, Verbosity
from icclim.models.ecad_indices import EcadIndex
from icclim.models.frequency import Frequency, SliceMode
from icclim.models.netcdf_version import NetcdfVersion
from icclim.models.quantile_interpolation import QuantileInterpolation
from icclim.models.user_index_config import UserIndexConfig
from icclim.user_indices.dispatcher import compute_user_index

__all__ = ["index"]

log: IcclimLogger = IcclimLogger.get_instance(Verbosity.LOW)


def indices():
    """
    List the available indices.
    todo: include a representation of custom indices.
    Returns
    -------
        A list of indices to be used as input of icclim.index `index_name` parameter.
    """
    return [f"{i.short_name}: {i.definition}" for i in EcadIndex]


def indice(*args, **kwargs):
    """
    Proxy for `index`
    To be deleted in 5.1
    """
    log.deprecation_warning(old="icclim.indice", new="icclim.index")
    return index(*args, **kwargs)


def index(
    in_files: Union[str, List[str], Dataset],
    index_name: str = None,  # optional when computing user_indices
    var_name: Optional[Union[str, List[str]]] = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: List[datetime] = None,
    out_file: str = "icclim_out.nc",
    threshold: Union[float, List[float]] = None,
    callback: Callable[[int], None] = log.callback,
    callback_percentage_start_value: int = 0,
    callback_percentage_total: int = 100,
    base_period_time_range: List[datetime] = None,
    window_width: int = 5,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    interpolation: Optional[
        Union[str, QuantileInterpolation]
    ] = QuantileInterpolation.MEDIAN_UNBIASED,
    out_unit: Optional[str] = None,
    netcdf_version: Union[str, NetcdfVersion] = NetcdfVersion.NETCDF4,
    # TODO do something prettier than a dict (a UserIndiceDTO or something)
    user_index: Dict[str, Any] = None,
    save_percentile: bool = False,
    logs_verbosity: Union[Verbosity, str] = Verbosity.LOW,
    # deprecated parameters
    indice_name: str = None,
    user_indice: Dict[str, Any] = None,
    transfer_limit_Mbytes: float = None,
) -> Dataset:
    """
    Parameters
    ----------
    in_files : Union[str, List[str], Dataset]
        Absolute path(s) to NetCDF dataset(s) (including OPeNDAP URLs),
        or xarray.Dataset.
    index_name : str
        Climate index name.
        For ECA&D index, case insensitive name used to lookup the index.
        For user index, it's the name of the output variable.
    var_name : str
        ``optional`` Target variable name to process corresponding to ``in_files``.
        If None (default) on ECA&D index, the variable is guessed based on the climate
        index wanted.
        Mandatory for a user index.
    slice_mode : str
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        Default is "year".
        See :ref:`slice_mode` for details.
    time_range : List[datetime.datetime]
        ``optional`` Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
        Default is ``None``.
    out_file : str
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
        Default is "icclim_out.nc".
        If the input ``in_files`` is a ``Dataset``, ``out_file`` field is ignored.
        Use the function returned value instead to retrieve the computed value.
        If ``out_file`` already exists, icclim will overwrite it!
    threshold : Union[float, List[float]]
        ``optional`` User defined threshold for certain indices.
        Default depend on the index, see their individual definition.
        When a list of threshold is provided, the index will be computed for each
        thresholds.
    transfer_limit_Mbytes : float
        ``optional`` Maximum Dask chunk size in memory.
        The value should be around 200 MB.
        If empty, no chunking is performed, the whole dataset will be in memory and the
        performance might be poor.
    callback : function
        ``optional`` Progress bar printing. If ``None``, progress bar will not be
        printed.
    callback_percentage_start_value : int
        ``optional`` Initial value of percentage of the progress bar (default: 0).
    callback_percentage_total : int
        ``optional`` Total percentage value (default: 100).
    base_period_time_range : List[datetime.datetime]
        ``optional`` Temporal range of the base period.
        Mandatory for bootstrapped indices, which are the temperature percentile based
        indices.
        Ignored for other indices.
    window_width : int
        ``optional`` User defined window width for related indices (default: 5).
        Ignored for non related indices.
    only_leap_years : bool
        ``optional`` Option for February 29th (default: False).
    ignore_Feb29th : bool
        ``optional`` Ignoring or not February 29th (default: False).
    interpolation : Union[str, QuantileInterpolation]
        ``optional`` Interpolation method to compute percentile values:
        ``{"linear", "hyndman_fan"}``
        Default is "hyndman_fan", a.k.a type 8 or method 8.
        Ignored for non percentile based indices.
    out_unit : str
        ``optional`` Output unit for certain indices: "days" or "%" (default: "days").
    netcdf_version : icclim.models.netcdf_version.NetcdfVersion
        ``optional`` NetCDF version to create (default: "NETCDF3_CLASSIC").
    user_index : Union[None, None]
        ``optional`` A dictionary with parameters for user defined index.
        See :ref:`Custom indices`.
        Ignored for ECA&D indices.
    save_percentile : bool
        ``optional`` True if the percentiles should be saved within the resulting netcdf
         file (default: False).
    logs_verbosity : Union[str, Verbosity]
        ``optional`` Configure how verbose icclim is.
        Possible values: ``{"LOW", "HIGH", "SILENT"}`` (default: "LOW")
    indice_name : Union[str, None]
        DEPRECATED, use index_name instead.
    user_indice : Union[None, None]
        DEPRECATED, use user_index instead.

    """
    # make xclim input daily check a warning instead of an error
    xclim.set_options(data_validation="warn")
    # keep attributes through xarray operations
    xr.set_options(keep_attrs=True)
    log.set_verbosity(logs_verbosity)
    log.start_message()
    callback(callback_percentage_start_value)
    # Deprecation handling
    if indice_name is not None:
        log.deprecation_warning(old="indice_name", new="index_name")
        index_name = indice_name
    if user_indice is not None:
        log.deprecation_warning(old="user_indice", new="user_index")
        user_index = user_indice
    if transfer_limit_Mbytes is not None:
        log.deprecation_warning(old="transfer_limit_Mbytes")
    index: Optional[EcadIndex]
    if user_index is None:
        index = EcadIndex.lookup(index_name)
    else:
        index = None
    # Todo: `chunk_da` forces dask to be used.
    #       Maybe add an option to use pure numpy ?
    chunk_da = True
    if isinstance(in_files, Dataset):
        input_dataset = in_files
        chunk_da = False
    elif isinstance(in_files, list):
        input_dataset = xarray.open_mfdataset(in_files, parallel=True)
    else:
        input_dataset = xarray.open_dataset(in_files)
    input_dataset, reset_coords_dict = _update_coords(input_dataset)
    if isinstance(var_name, str):
        var_name = [var_name]
    elif var_name is None and index is not None:
        var_name = _guess_variables(index, input_dataset)
    config = IndexConfig(
        base_period_time_range=base_period_time_range,
        ds=input_dataset,
        ignore_Feb29th=ignore_Feb29th,
        only_leap_years=only_leap_years,
        save_percentile=save_percentile,
        slice_mode=slice_mode,
        time_range=time_range,
        var_name=var_name,
        window_width=window_width,
        out_unit=out_unit,
        netcdf_version=netcdf_version,
        interpolation=interpolation,
        callback=callback,
        index=index,
        chunk_it=chunk_da,
    )
    if user_index is not None:
        result_ds = _compute_user_index_dataset(config, user_index)
    else:
        result_ds = _compute_ecad_index_dataset(
            config, index, threshold, input_dataset.attrs.get("history", None)
        )
    if reset_coords_dict:
        result_ds = result_ds.rename(reset_coords_dict)
    if not isinstance(in_files, Dataset):
        if input_dataset.time.encoding:
            if input_dataset.time.encoding.get("chunksizes"):
                del input_dataset.time.encoding["chunksizes"]
            time_encoding = input_dataset.time.encoding
        else:
            time_encoding = {"units": "days since 1850-1-1"}
        result_ds.to_netcdf(
            out_file,
            format=config.netcdf_version.value,
            encoding={"time": time_encoding},
        )
    callback(callback_percentage_total)
    log.ending_message(time.process_time())
    return result_ds


def _compute_ecad_index_dataset(
    config: IndexConfig,
    index: EcadIndex,
    threshold: Union[float, List[float]],
    current_history: Optional[str],
) -> Dataset:
    if isinstance(threshold, list):
        ds_list = []
        for th in threshold:
            config.threshold = th
            ds_list.append(_compute_ecad_index(index, config, current_history))
        result_ds = xarray.concat(ds_list, dim="threshold")
    else:
        config.threshold = threshold
        result_ds = _compute_ecad_index(index, config, current_history)
    return result_ds


def _compute_user_index_dataset(config: IndexConfig, user_index: dict) -> Dataset:
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
    if config.freq.post_processing is not None:
        user_indice_da, time_bounds = config.freq.post_processing(user_indice_da)
        result_ds[user_indice_config.index_name] = user_indice_da
        result_ds["time_bounds"] = time_bounds
    else:
        result_ds[user_indice_config.index_name] = user_indice_da
    return result_ds


def _get_unit(output_unit: Optional[str], da: DataArray) -> Optional[str]:
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
    index: EcadIndex, config: IndexConfig, former_history: Optional[str]
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
    result_ds = _add_basic_indice_metadata(result_ds, config, index, former_history)
    return result_ds


def _add_basic_indice_metadata(
    result_ds: Dataset,
    config: IndexConfig,
    computed_index: EcadIndex,
    former_history: str,
) -> Dataset:
    if config.threshold is not None:
        title = f"Index {computed_index.short_name} with user defined threshold"
    else:
        title = f"ECA {computed_index.group} index {computed_index.short_name}"
    result_ds.attrs["title"] = title
    result_ds.attrs[
        "references"
    ] = "ATBD of the ECA indices calculation (https://www.ecad.eu/documents/atbd.pdf)"
    result_ds.attrs["institution"] = "Climate impact portal (https://climate4impact.eu)"
    result_ds.attrs["history"] = _get_history(
        config, former_history, computed_index, result_ds
    )
    result_ds.attrs["source"] = ""
    result_ds.attrs["Conventions"] = "CF-1.6"

    result_ds.lat.encoding["_FillValue"] = None
    result_ds.lon.encoding["_FillValue"] = None

    return result_ds


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


def _guess_variables(index: EcadIndex, ds: Dataset) -> List[str]:
    """
    Try to guess the variable names using the expected kind of variable for
    the index.
    """
    res = []
    index_variables = index.variables
    for indice_var in index_variables:
        for alias in indice_var:
            # check if dataset contains this alias
            if ds.get(alias, None) is not None:
                res.append(alias)
                break
    if len(res) < len(index_variables):
        variables = list(filter(lambda x: x not in ds.coords, ds.variables.keys()))
        raise InvalidIcclimArgumentError(
            f"The necessary variable(s) were not recognized in the"
            f" input file(s) to compute `{index.short_name}` index."
            f" Use `var_name` parameter to use one the dataset non coordinate variable:"
            f" {variables}"
        )
    return res


def _update_coords(ds: Dataset) -> Tuple[Dataset, Dict]:
    # TODO see if cf-xarray could replace this
    revert = {}
    if ds.coords.get("latitude") is not None:
        ds = ds.rename({"latitude": "lat"})
        revert.update({"lat": "latitude"})
    if ds.coords.get("longitude") is not None:
        ds = ds.rename({"longitude": "lon"})
        revert.update({"lon": "longitude"})
    if ds.coords.get("t") is not None:
        ds = ds.rename({"t": "time"})
        revert.update({"time": "t"})
    return ds, revert
