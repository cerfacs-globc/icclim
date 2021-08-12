# -*- Coding: latin-1 -*-
#  Copyright CERFACS (http://cerfacs.fr/)
#  Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)

import datetime
from typing import Callable, List, Optional, Union
from warnings import warn

import xarray
from xarray.core.dataarray import DataArray
from xarray.core.dataset import Dataset

from icclim import indices
from icclim.indices import IndiceConfig
from icclim.models.frequency import Frequency, SliceMode
from icclim.models.netcdf_version import NetcdfVersion
from icclim.models.user_indice_config import UserIndiceConfig
from icclim.user_indices.bridge import compute_user_indice


def indice(
    in_files: Union[str, List[str]],
    var_name: Union[str, List[str]],
    indice_name: str = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: List[datetime.datetime] = None,
    out_file: str = "icclim_out.nc",
    threshold: Union[float, List[float]] = None,
    transfer_limit_Mbytes: float = None,
    callback: Callable = None,
    callback_percentage_start_value: int = 0,
    callback_percentage_total: int = 100,
    base_period_time_range: List[datetime.datetime] = None,
    window_width: int = 5,
    only_leap_years: bool = False,
    ignore_Feb29th: bool = False,
    # TODO should be an enumeration
    interpolation: str = "linear",
    out_unit: str = "days",
    # TODO maybe upgrade default value to netcdf4 ? it is the default of xarray
    netcdf_version: Union[str, NetcdfVersion] = NetcdfVersion.NETCDF3_CLASSIC,
    user_indice: dict = None,
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
    :param N_lev:
        Level number if 4D variable.
    :param lev_dim_pos:
        Position of Level dimension, either 0 or 1. 0 is leftmost dimension, 1 is second to the leftmost. Default 1.
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
    :rtype: path to NetCDF file

    .. warning:: If ``out_file`` already exists, icclim will overwrite it!

    """
    if isinstance(in_files, str):
        ds = xarray.open_dataset(in_files)
    else:
        ds = xarray.open_mfdataset(in_files)
    if isinstance(var_name, str):
        var_name = [var_name]
    config = IndiceConfig(
        base_period_time_range=base_period_time_range,
        ds=ds,
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
    )
    if user_indice is not None:
        result_ds = _build_user_indice_dataset(config, save_percentile, user_indice)
    else:
        result_ds = _build_basic_indice_dataset(config, indice_name, threshold)
    # TODO add global attributes to dataset
    result_ds.to_netcdf(out_file, format=config.netcdf_version.value)
    return result_ds


def _build_basic_indice_dataset(
    config: IndiceConfig, indice_name: str, threshold
) -> Dataset:
    if indice_name is None:
        raise Exception("indice_name must be provided.")  # user input error
    if isinstance(threshold, list):
        ds_list = []
        for th in threshold:
            config.threshold = th
            ds_list.append(_compute_indice(indice_name, config))
        return xarray.concat(ds_list, dim="threshold")
    else:
        config.threshold = threshold
        return _compute_indice(indice_name, config)


def _build_user_indice_dataset(
    config: IndiceConfig, save_percentile: bool, user_indice: dict
) -> Dataset:
    result_ds = Dataset()
    user_indice_config: UserIndiceConfig = UserIndiceConfig(
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


def _get_unit(
    user_output_unit: Optional[str], user_indice_da: DataArray
) -> Optional[str]:
    computed_unit = user_indice_da.attrs.get("units", None)
    if computed_unit is None:
        if user_output_unit is None:
            warn(
                "No unit either computed or provided for the indice. You can use out_unit parameter to fix this."
            )
            return None
        else:
            return user_output_unit
    else:
        if user_output_unit is not None:
            warn(
                f"Overriding the computed unit {user_indice_da.attrs['units']} with the user give unit {user_output_unit}"
            )
            return user_output_unit
        else:
            return computed_unit


def _compute_indice(indice_name: str, config: IndiceConfig) -> Dataset:
    result_ds = Dataset()
    da = indices.indice_from_string(indice_name).compute(config)
    da.attrs["units"] = _get_unit(config.out_unit, da)
    if config.threshold is not None:
        da.expand_dims({"threshold": config.threshold})
    if config.freq.resampler is not None:
        resampled_da, time_bounds = config.freq.resampler(da)
        result_ds[indice_name] = resampled_da
        result_ds["time_bounds"] = time_bounds
    else:
        result_ds[indice_name] = da
    return result_ds
