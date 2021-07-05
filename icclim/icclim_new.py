# -*- Coding: latin-1 -*-
#  Copyright CERFACS (http://cerfacs.fr/)
#  Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
#
#  Author: Natalia Tatarinova
#  Additions from Christian Page (2015-2017)

# pyximport.install(pyimport = True)

from numpy.lib.function_base import percentile
from xarray.core.dataarray import DataArray
from icclim import indices
import xarray
from dataclasses import dataclass
from typing import Callable, List, Union
import numpy
import logging
from netCDF4 import Dataset, MFDataset
import os
from collections import OrderedDict

import numpy
import logging
import pkg_resources
import time
import datetime

import pdb

from netCDF4 import Dataset, MFDataset
from numpy.core.arrayprint import DatetimeFormat

from . import (
    maps,
    time_subset,
    calc_ind,
    set_globattr,
    set_longname_units,
    set_longname_units_custom_indices,
    calc_percentiles,
)
from .icclim_exceptions import *
from .util import (
    check,
    logging_info,
    util_nc,
    util_dt,
    files_order,
    arr_size,
    callback,
    read,
    OCGIS_tile,
    calc,
)
from .util import user_indice as ui

# Initial Config
global config_file
config_file = os.path.dirname(os.path.abspath(__file__)) + "/config_indice.json"


def get_key_by_value_from_dict(my_map, my_value):
    for key in my_map.keys():
        if my_value in my_map[key]:
            return key
    if my_value not in my_map.keys():
        return "user_indice"


@dataclass
class InputFile:
    path: str
    cf_variables: List[str]


def indice(
    in_files: Union[str, List[str]],
    var_name: List[str],
    indice_name: str = None,
    # TODO use an enumeration if it's not breaking the api
    slice_mode: str = "year",
    # TODO should be a slice instead of a List
    time_range: List[datetime.datetime] = None,
    out_file: str = check.icclim_output_file_defaults("file_name"),
    threshold: Union[float, List[float]] = None,
    N_lev: int = None,
    # TODO See if it still makes sense with xarray
    lev_dim_pos: int = 1,
    transfer_limit_Mbytes: float = None,
    callback: Callable = None,
    callback_percentage_start_value: int = 0,
    callback_percentage_total: int = 100,
    # TODO should be a slice instead of a List
    base_period_time_range: List[datetime.datetime] = None,
    window_width: int = 5,
    only_leap_years: bool = False,
    # TODO see how to use it
    ignore_Feb29th: bool = False,
    # TODO should be an enumeration
    interpolation: str = "linear",
    # TODO probably unecessary with xclim unit handling
    out_unit: str = "days",
    # TODO probably unecessary
    netcdf_version=check.icclim_output_file_defaults("netcdf_version"),
    # TODO see if we can make use of a more sophisticated type than dict
    user_indice: dict = None,
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
    da = ds[var_name]  # TODO handle multi variable
    da = build_data_array(da, time_range, ignore_Feb29th)
    freq = compute_freq(slice_mode)
    percentile_da = compute_percentile_da(da, base_period_time_range, only_leap_years)

    indices.indice_from_string(indice_name)(
        da=da,
        freq=freq,
        percentile_da=percentile_da,
        window_width=window_width,
        threshold=threshold,
    ).to_netcdf(out_file)


def build_data_array(
    da: DataArray, time_range: List[str], ignore_Feb29th: bool
) -> DataArray:
    # TODO
    return da


def compute_freq(slice_mode: str) -> str:
    freq_mode = {
        "month": "MS",
        "DJF": "QS-DEC",
        "MAM": "YS",
        "JJA": "YS",
        "SON": "YS",
        "year": "YS",
    }
    # TODO do it better
    return freq_mode[slice_mode]


def compute_percentile_da(
    da: DataArray, base_period_time_range: List[str], only_leap_years: bool
) -> DataArray:
    # TODO
    return da
