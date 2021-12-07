# -*- Coding: latin-1 -*-
#  Copyright CERFACS (http://cerfacs.fr/)
#  Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)

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


def indice(*args, **kwargs):
    """
    Proxy for `index`
    To be deleted in 5.1
    """
    log.deprecation_warning(old="icclim.indice", new="icclim.index")
    return index(*args, **kwargs)


def index(
    in_files: Union[str, List[str], Dataset],
    var_name: Optional[Union[str, List[str]]] = None,
    index_name: str = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: List[datetime] = None,
    out_file: str = "icclim_out.nc",
    threshold: Union[float, List[float]] = None,
    transfer_limit_Mbytes: float = None,
    callback: Callable[[int], None] = lambda p: logging.info(f"Processing: {p}%"),
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
    # deprecated
    indice_name: str = None,
    user_indice: Dict[str, Any] = None,
) -> Dataset:
    """
    :param index_name:
        Climate index name.
    :param in_files:
        Absolute path(s) to NetCDF dataset(s) (including OPeNDAP URLs).
    :param var_name:
        Target variable name to process corresponding to ``in_files``.
    :param slice_mode:
        Type of temporal aggregation:
        {"year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS"}.
        If ``None``, the index will be calculated as monthly values.
    :param time_range:
        Temporal range: upper and lower bounds for temporal subsetting.
        If ``None``, whole period of input files will be processed.
    :param out_file:
        Output NetCDF file name (default: "icclim_out.nc" in the current directory).
    :param threshold:
        User defined threshold for certain indices.
    :param transfer_limit_Mbytes:
        Maximum OPeNDAP/THREDDS request limit in Mbytes in case of OPeNDAP datasets.
    :param callback:
        Progress bar printing. If ``None``, progress bar will not be printed.
    :param callback_percentage_start_value:
        Initial value of percentage of the progress bar (default: 0).
    :param callback_percentage_total:
        Total persentage value (default: 100).
    :param base_period_time_range:
        Temporal range of the base period.
    :param window_width:
        Window width, must be odd (default: 5).
    :param only_leap_years:
        Option for February 29th (default: False).
    :param ignore_Feb29th:
        Ignoring or not February 29th (default: False).
    :param interpolation:
        Interpolation method to compute percentile values: "linear" or "hyndman_fan".
        default: "hyndman_fan".
    :param out_unit:
        Output unit for certain indices: "days" or "%" (default: "days").
    :param user_index:
        A dictionary with parameters for user defined index
    :param netcdf_version:
        NetCDF version to create (default: "NETCDF3_CLASSIC").
    :param save_percentile:
        True if the percentiles should be saved within the resulting netcdf file
    :rtype: path to NetCDF file

    .. warning:: If ``out_file`` already exists, icclim will overwrite it!

    """
    # make xclim input daily check a warning instead of an error
    xclim.set_options(data_validation="warn")
    # keep attributes through xarray operations
    xr.set_options(keep_attrs=True)
    log.set_verbosity(logs_verbosity)

    log.start_message()
    callback(callback_percentage_start_value)
    if indice_name is not None:
        log.deprecation_warning(old="indice_name", new="index_name")
        index_name = indice_name
    if user_indice is not None:
        log.deprecation_warning(old="user_indice", new="user_index")
        user_index = user_indice
    index: Optional[EcadIndex]
    if user_index is None:
        index = EcadIndex.lookup(index_name)
    else:
        index = None
    input_dataset, reset_coords = _read_input(in_files)
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
        transfer_limit_Mbytes=transfer_limit_Mbytes,
        out_unit=out_unit,
        netcdf_version=netcdf_version,
        interpolation=interpolation,
        callback=callback,
        index=index,
    )
    if user_index is not None:
        result_ds = _compute_user_index_dataset(config, user_index)
    else:
        result_ds = _compute_ecad_index_dataset(
            config, index, threshold, input_dataset.attrs.get("history", None)
        )
    if reset_coords:
        result_ds = result_ds.rename(reset_coords)
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


def _read_input(in_files):
    if isinstance(in_files, Dataset):
        input_dataset = in_files
    elif isinstance(in_files, list):
        input_dataset = xarray.open_mfdataset(in_files, parallel=True)
    else:
        input_dataset = xarray.open_dataset(in_files)
    input_dataset, reset_coords = _update_coords(input_dataset)
    return input_dataset, reset_coords


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
        cf_vars=config.cf_variables,
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
    logging.info(f"Calculating climate index: {index.index_name}")
    result_ds = Dataset()
    da, per = index.compute(config)
    da.attrs["units"] = _get_unit(config.out_unit, da)
    if config.threshold is not None:
        da.expand_dims({"threshold": config.threshold})
    if config.freq.post_processing is not None:
        resampled_da, time_bounds = config.freq.post_processing(da)
        result_ds[index.index_name] = resampled_da
        if time_bounds is not None:
            result_ds["time_bounds"] = time_bounds
            result_ds.time.attrs["bounds"] = "time_bounds"
    else:
        result_ds[index.index_name] = da
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
    # TODO: complete with clix-meta metadata
    if config.threshold is not None:
        title = f"Index {computed_index.index_name} with user defined threshold"
    else:
        title = f"ECA {computed_index.group} index {computed_index.index_name}"
    result_ds.attrs["title"] = title
    result_ds.attrs[
        "references"
    ] = "ATBD of the ECA indices calculation (https://www.ecad.eu/documents/atbd.pdf)"
    result_ds.attrs["institution"] = "Climate impact portal (https://climate4impact.eu)"
    result_ds.attrs["history"] = _get_history(
        config, former_history, computed_index, result_ds
    )
    # TODO make sure it should stay empty as in v4
    result_ds.attrs["source"] = ""
    # TODO make sure 1.6 is ok or use a newer version of cf
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
        f"Calculation of {indice_computed.index_name} "
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
        raise InvalidIcclimArgumentError(
            f"The necessary variable(s) were not found or recognized in the"
            f" input file(s) to compute {index.index_name}."
            f" If the variable(s) exist with non-standard names in the"
            f" file, use var_name parameter to provide their names."
        )
    return res


def _update_coords(ds: Dataset) -> Tuple[Dataset, Dict]:
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
