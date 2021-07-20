# -*- Coding: latin-1 -*-
#  Copyright CERFACS (http://cerfacs.fr/)
#  Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
#
#  Author: Natalia Tatarinova
#  Additions from Christian Page (2015-2017)

from icclim.types import SliceMode
from icclim.models.frequency import Frequency, build_frequency
from icclim.util import logging_info
from icclim.indices import IndiceConfig
from xarray.core.dataarray import DataArray
import xarray
from typing import Callable, List, Union
import indices
import datetime
import xclim.core.calendar as calendar


def indice(
    in_files: Union[str, List[str]],
    var_name: List[str],
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
    # TODO probably unecessary with xclim unit handling
    out_unit: str = "days",
    # TODO use an enum and re-add default value
    netcdf_version=None,
    # TODO see if we can make use of a more sophisticated type than dict
    user_indice: dict = None,
    # TODO ease to extract from percentile_doy
    save_percentile: bool = False,
):
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

    logging_info.start_message()
    ds = xarray.open_mfdataset(in_files)
    config = IndiceConfig()
    config.data_arrays = []
    config.data_arrays_in_base = []
    sampling_frequency = build_frequency(slice_mode)
    for cf_var in var_name:
        da = build_data_array(ds[cf_var], time_range, ignore_Feb29th)
        if sampling_frequency.resampler is not None:
            da = sampling_frequency.resampler(da)
        config.data_arrays.append()
        if base_period_time_range is not None:
            config.data_arrays_in_base.append(
                build_in_base_da(ds[cf_var], base_period_time_range, only_leap_years)
            )

    config.freq = sampling_frequency.panda_freq
    config.window = window_width
    config.threshold = to_celcius(threshold)  # TODO handle multi threshold ?
    indices.indice_from_string(indice_name).compute(**config).to_netcdf(out_file)


def build_data_array(
    da: DataArray, time_range: List[datetime.datetime], ignore_Feb29th: bool
) -> DataArray:
    if len(time_range) != 2:
        raise Exception("Not a valid time range")
    time_range = slice(time_range[0], time_range[1])
    da = da.sel(time=time_range)
    if ignore_Feb29th:
        da = calendar.convert_calendar(da, "noleap")
    return da


def build_in_base_da(
    da: DataArray,
    base_period_time_range: List[datetime.datetime],
    only_leap_years: bool,
) -> DataArray:
    if len(base_period_time_range) != 2:
        raise Exception("Not a valid time range")
    base_period_time_range = slice(base_period_time_range[0], base_period_time_range[1])
    da = da.sel(time=base_period_time_range)
    if only_leap_years:
        da = reduce_only_leap_years(da)
    return da


def reduce_only_leap_years(da: DataArray):
    reduced_list = []
    for _, val in da.groupby(da.time.dt.year):
        if val.time.dt.dayofyear.max() == 366:
            reduced_list.append(val)
    if reduced_list == []:
        raise Exception(
            "No leap year in current dataset. Do not use only_leap_years parameter."
        )
    return xarray.concat(reduced_list, "time")


def to_celcius(threshold: float) -> Union[None, str]:
    if threshold is not None:
        return f"{threshold} degC"
    return None

