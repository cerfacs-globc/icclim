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

from icclim.eca_indices import Indice, IndiceConfig, indice_from_string
from icclim.icclim_exceptions import InvalidIcclimArgumentError, MissingIcclimInputError
from icclim.logging_info import ending_message, start_message
from icclim.models.frequency import Frequency, SliceMode
from icclim.models.netcdf_version import NetcdfVersion
from icclim.models.quantile_interpolation import QuantileInterpolation
from icclim.models.user_indice_config import UserIndiceConfig
from icclim.user_indices.bridge import compute_user_indice

__all__ = ["indice"]


def indice(
    in_files: Union[str, List[str], Dataset],
    var_name: Optional[Union[str, List[str]]] = None,
    indice_name: str = None,
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
    user_indice: Dict[str, Any] = None,
    save_percentile: bool = False,
) -> Dataset:
    """
    :param indice_name:
        Climate index name.
    :param in_files:
        Absolute path(s) to NetCDF dataset(s) (including OPeNDAP URLs).
    :param var_name:
        Target variable name to process corresponding to ``in_files``.
    :param slice_mode:
        Type of temporal aggregation: "year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS". If ``None``, the index will be calculated as monthly values.
    :param time_range:
        Temporal range: upper and lower bounds for temporal subsetting. If ``None``, whole period of input files will be processed.
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
        Interpolation method to compute percentile values: "linear" or "hyndman_fan" (default: "hyndman_fan").
    :param out_unit:
        Output unit for certain indices: "days" or "%" (default: "days").
    :param user_indice:
        A dictionary with parameters for user defined index
    :param netcdf_version:
        NetCDF version to create (default: "NETCDF3_CLASSIC").
    :param save_percentile:
        True if the percentiles should be saved within the resulting netcdf file
    :rtype: path to NetCDF file

    .. warning:: If ``out_file`` already exists, icclim will overwrite it!

    """
    # make daily check a warning instead of an error
    xclim.set_options(data_validation="warn")
    # keep attributes through xarray operations
    xr.set_options(keep_attrs=True)
    start_message()
    callback(callback_percentage_start_value)
    if isinstance(in_files, Dataset):
        input_ds = in_files
    elif isinstance(in_files, list):
        input_ds = xarray.open_mfdataset(in_files, parallel=True)
    else:
        input_ds = xarray.open_dataset(in_files)
    if isinstance(var_name, str):
        var_name = [var_name]
    elif var_name is None:
        var_name = _guess_variables(indice_name, input_ds)
    input_ds, reset_coords = _update_coords(input_ds)
    config = IndiceConfig(
        base_period_time_range=base_period_time_range,
        ds=input_ds,
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
    )
    if user_indice is not None:
        result_ds = _build_user_indice_dataset(config, save_percentile, user_indice)
    else:
        result_ds = _build_basic_indice_dataset(
            config, indice_name, threshold, input_ds.attrs.get("history", None)
        )
    if reset_coords:
        result_ds = result_ds.rename(reset_coords)
    if not isinstance(in_files, Dataset):
        result_ds.to_netcdf(
            out_file,
            format=config.netcdf_version.value,
            encoding={"time": input_ds.time.encoding},
        )
    callback(callback_percentage_total)
    ending_message(time.process_time())
    return result_ds


def _build_basic_indice_dataset(
    config: IndiceConfig,
    indice_name: str,
    threshold: Union[float, List[float]],
    current_history: Optional[str],
) -> Dataset:
    if indice_name is None:
        # user input error, avoid doing all computations for nothing
        raise MissingIcclimInputError("indice_name must be provided.")
    if isinstance(threshold, list):
        ds_list = []
        for th in threshold:
            config.threshold = th
            ds_list.append(_compute_basic_indice(indice_name, config, current_history))
        result_ds = xarray.concat(ds_list, dim="threshold")
    else:
        config.threshold = threshold
        result_ds = _compute_basic_indice(indice_name, config, current_history)
    return result_ds


def _build_user_indice_dataset(
    config: IndiceConfig, save_percentile: bool, user_indice: dict
) -> Dataset:
    logging.info("Calculating user indice.")
    result_ds = Dataset()
    user_indice_config = UserIndiceConfig(
        **user_indice,
        freq=config.freq,
        cf_vars=config.cf_variables,
        is_percent=config.is_percent,
        save_percentile=save_percentile,
    )
    user_indice_da = compute_user_indice(user_indice_config)
    user_indice_da.attrs["units"] = _get_unit(config.out_unit, user_indice_da)
    if config.freq.resampler is not None:
        user_indice_da, time_bounds = config.freq.resampler(user_indice_da)
        result_ds[user_indice_config.indice_name] = user_indice_da
        result_ds["time_bounds"] = time_bounds
    else:
        result_ds[user_indice_config.indice_name] = user_indice_da
    return result_ds


def _get_unit(output_unit: Optional[str], da: DataArray) -> Optional[str]:
    da_unit = da.attrs.get("units", None)
    if da_unit is None:
        if output_unit is None:
            warn(
                "No unit computed or provided for the indice was found. "
                "Use out_unit parameter to add one."
            )
            return ""
        else:
            return output_unit
    else:
        if output_unit is None or output_unit == da_unit:
            return da_unit
        else:
            warn(
                f'Overriding the computed unit "{da_unit}" '
                f'with the user given unit "{output_unit}"'
            )
            return output_unit


def _compute_basic_indice(
    indice_name: str, config: IndiceConfig, former_history: Optional[str]
) -> Dataset:
    logging.info(f"Calculating climate index: {indice_name}")
    result_ds = Dataset()
    indice = indice_from_string(indice_name)
    da, per = indice.compute(config)
    da.attrs["units"] = _get_unit(config.out_unit, da)
    if config.threshold is not None:
        da.expand_dims({"threshold": config.threshold})
    if config.freq.resampler is not None:
        resampled_da, time_bounds = config.freq.resampler(da)
        result_ds[indice_name] = resampled_da
        if time_bounds is not None:
            result_ds["time_bounds"] = time_bounds
            result_ds.time.attrs["bounds"] = "time_bounds"
    else:
        result_ds[indice_name] = da
    if per is not None:
        per = per.squeeze("percentiles", drop=True).rename("percentiles")
        result_ds = xr.merge([result_ds, per])
    if former_history is None:
        former_history = da.attrs["history"]
    else:
        former_history = f"{former_history}\n{da.attrs['history']}"
    del da.attrs["history"]
    result_ds = _add_basic_indice_metadata(result_ds, config, indice, former_history)
    return result_ds


def _add_basic_indice_metadata(
    result_ds: Dataset,
    config: IndiceConfig,
    indice_computed: Indice,
    former_history: str,
) -> Dataset:
    # TODO: complete with clix-meta metadata
    if config.threshold is not None:
        title = f"Index {indice_computed.indice_name} with user defined threshold"
    else:
        title = f"ECA {indice_computed.group} indice {indice_computed.indice_name}"
    result_ds.attrs["title"] = title
    result_ds.attrs[
        "references"
    ] = "ATBD of the ECA indices calculation (https://www.ecad.eu/documents/atbd.pdf)"
    result_ds.attrs["institution"] = "Climate impact portal (https://climate4impact.eu)"
    result_ds.attrs["history"] = _get_history(
        config, former_history, indice_computed, result_ds
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
        f"Calculation of {indice_computed.indice_name} "
        f"indice({config.freq.description}) "
        f"from {start_time} to {end_time}."
    )


def _guess_variables(indice_name: str, ds: Dataset):
    """
    Try to guess the variable names using the expected kind of variable for
    the indice.
    """
    res = []
    indice_variables = indice_from_string(indice_name).variables
    for indice_var in indice_variables:
        for alias in indice_var:
            # check if dataset contains this alias
            if ds.get(alias, None) is not None:
                res.append(alias)
                break
    if len(res) < len(indice_variables):
        raise InvalidIcclimArgumentError(
            f"The necessary variable(s) were not found or recognized in the"
            f" input file(s) to compute {indice_name}."
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
