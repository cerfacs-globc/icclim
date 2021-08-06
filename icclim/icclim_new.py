# -*- Coding: latin-1 -*-
#  Copyright CERFACS (http://cerfacs.fr/)
#  Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
#
#  Author: Natalia Tatarinova
#  Additions from Christian Page (2015-2017)

import datetime
from typing import Callable, List, Optional, Union

import xarray
import xclim.core.calendar as calendar
from xarray.core.dataarray import DataArray
from xarray.core.dataset import Dataset

from icclim import indices
from icclim.indices import IndiceConfig
from icclim.models.frequency import Frequency, SliceMode, build_frequency
from icclim.models.indice_config import CfVariable
from icclim.user_indice.bridge import compute_user_indice
from icclim.user_indice.user_indice import UserIndiceConfig
from icclim.util import logging_info


def indice(
    in_files: Union[str, List[str]],
    var_name: Union[str, List[str]],
    indice_name: str = None,
    slice_mode: SliceMode = Frequency.YEAR,
    time_range: List[datetime.datetime] = None,
    # TODO re-add default file name
    out_file: str = None,
    threshold: Union[float, List[float]] = None,
    N_lev: int = None,
    # TODO See if it still makes sense with xarray
    lev_dim_pos: int = 1,
    # TODO see how to go from this to Dask chunks
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
    # TODO probably unecessary with xclim unit handling, but necessary for user-indices
    out_unit: str = "days",
    # TODO use an enum and re-add default value
    netcdf_version=None,
    # TODO see if we can deprecated this
    user_indice: dict = None,
    # TODO easy to extract from percentile_doy, see if it is necessary on user-indicies
    save_percentile: bool = False,
) -> Dataset:
    """
    :param indice_name: Climate index name.
    :type indice_name: str

    :param in_files: Absolute path(s) to NetCDF dataset(s) (including OPeNDAP URLs).
    :type in_files: str OR list of str OR list of lists

    :param var_name: Target variable name to process corresponding to ``in_files``.
    :type var_name: str OR list of str

    :param slice_mode: Type of temporal aggregation: "year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS". If ``None``, the index will be calculated as monthly values.
    :type slice_mode: str

    :param time_range: Temporal range: upper and lower bounds for temporal subsetting. If ``None``, whole period of input files will be processed.
    :type time_range: [datetime.datetime, datetime.datetime]

    :param out_file: Output NetCDF file name (default: "icclim_out.nc" in the current directory).
    :type out_file: str

    :param threshold: User defined threshold for certain indices.
    :type threshold: float or list of floats

    :param N_lev: Level number if 4D variable.
    :type N_lev: int

    :param lev_dim_pos: Position of Level dimension, either 0 or 1. 0 is leftmost dimension, 1 is second to the leftmost. Default 1.
    :type lev_dim_pos: int

    :param transfer_limit_Mbytes: Maximum OPeNDAP/THREDDS request limit in Mbytes in case of OPeNDAP datasets.
    :type transfer_limit_Mbytes: float

    :param callback: Progress bar printing. If ``None``, progress bar will not be printed.
    :type callback: :func:`callback.defaultCallback`

    :param callback_percentage_start_value: Initial value of percentage of the progress bar (default: 0).
    :type callback_percentage_start_value: int

    :param callback_percentage_total: Total persentage value (default: 100).
    :type callback_percentage_total: int

    :param base_period_time_range: Temporal range of the base period.
    :type base_period_time_range: [datetime.datetime, datetime.datetime]

    :param window_width: Window width, must be odd (default: 5).
    :type window_width: int

    :param only_leap_years: Option for February 29th (default: False).
    :type only_leap_years: bool

    :param ignore_Feb29th: Ignoring or not February 29th (default: False).
    :type ignore_Feb29th: bool

    :param interpolation: Interpolation method to compute percentile values: "linear" or "hyndman_fan" (default: "hyndman_fan").
    :type interpolation: str

    :param out_unit: Output unit for certain indices: "days" or "%" (default: "days").
    :type out_unit: str

    :param user_indice: A dictionary with parameters for user defined index
    :type user_indice: dict

    :param netcdf_version: NetCDF version to create (default: "NETCDF3_CLASSIC").
    :type netcdf_version: str

    :rtype: path to NetCDF file

    .. warning:: If ``out_file`` already exists, icclim will overwrite it!

    """
    if isinstance(in_files, str):
        ds = xarray.open_dataset(in_files)
    else:
        ds = xarray.open_mfdataset(in_files)
    config = IndiceConfig()
    config.freq = build_frequency(slice_mode)
    if isinstance(var_name, str):
        var_name = [var_name]
    config.cfvariables = [
        build_cf_variable(
            ds[cf_var_name],
            time_range,
            ignore_Feb29th,
            base_period_time_range,
            only_leap_years,
        )
        for cf_var_name in var_name
    ]
    config.window = window_width
    config.save_percentile = save_percentile
    result_ds = Dataset()
    # TODO add attributes to dataset
    if user_indice is not None:
        is_percent = out_unit == "%"
        user_indice_config: UserIndiceConfig = UserIndiceConfig(
            **user_indice,
            freq=config.freq,
            cf_vars=config.cfvariables,
            is_percent=is_percent,
        )
        user_indice_da = compute_user_indice(user_indice_config)
        if config.freq.resampler is not None:
            user_indice_da, time_bounds = config.freq.resampler(user_indice_da)
            result_ds[user_indice_config.indice_name] = user_indice_da
            result_ds["time_bounds"] = time_bounds
        else:
            result_ds[user_indice_config.indice_name] = user_indice_da
    else:
        if indice_name is None:
            raise Exception("indice_name must be provided.")  # user input error
        if isinstance(threshold, list):
            for th in threshold:
                # TODO: in v4 threshold was a dimension
                # TODO Fix maybe let the indices construct the Dataset to have date_start, time_bounds, threshold, percentiles as variable or coords
                result_ds[f"{indice_name}_threshold_{th}"] = compute_indice(
                    indice_name, config, th
                )
        else:
            result_ds[indice_name] = compute_indice(indice_name, config, threshold)
    result_ds.to_netcdf(out_file)
    return result_ds


def compute_indice(indice_name: str, config: IndiceConfig, threshold: Optional[float]):
    config.threshold = to_celcius(threshold)
    da = indices.indice_from_string(indice_name).compute(config)
    if config.freq.resampler is not None:
        da = config.freq.resampler(da)
    return da


def build_cf_variable(
    da: DataArray,
    time_range: Optional[List[datetime.datetime]],
    ignore_Feb29th: bool,
    base_period_time_range: Optional[List[datetime.datetime]],
    only_leap_years: bool,
) -> CfVariable:
    cf_var = CfVariable(build_data_array(da, time_range, ignore_Feb29th))
    if base_period_time_range is not None:
        cf_var.in_base_da = build_in_base_da(
            da, base_period_time_range, only_leap_years
        )
    return cf_var


def build_data_array(
    da: DataArray, time_range: Optional[List[datetime.datetime]], ignore_Feb29th: bool
) -> DataArray:
    if time_range is not None:
        if len(time_range) != 2:
            raise Exception("Not a valid time range")
        da = da.sel(time=slice(time_range[0], time_range[1]))
    if ignore_Feb29th:
        da = calendar.convert_calendar(da, "noleap")  # type:ignore
    return da


def build_in_base_da(
    da: DataArray,
    base_period_time_range: List[datetime.datetime],
    only_leap_years: bool,
) -> DataArray:
    if len(base_period_time_range) != 2:
        raise Exception("Not a valid time range")
    da = da.sel(time=slice(base_period_time_range[0], base_period_time_range[1]))
    if only_leap_years:
        da = reduce_only_leap_years(da)
    return da


def reduce_only_leap_years(da: DataArray) -> DataArray:
    reduced_list: List[DataArray] = []
    for _, val in da.groupby(da.time.dt.year):
        if val.time.dt.dayofyear.max() == 366:
            reduced_list.append(val)
    if reduced_list == []:
        raise Exception(
            "No leap year in current dataset. Do not use only_leap_years parameter."
        )
    return xarray.concat(reduced_list, "time")


def to_celcius(threshold: Optional[float]) -> Optional[str]:
    if threshold is not None:
        return f"{threshold} degC"
    return None
