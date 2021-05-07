# -*- coding: latin-1 -*-
#  Copyright CERFACS (http://cerfacs.fr/)
#  Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)


import sys
import os
from collections import OrderedDict
import pdb

import numpy
import logging
import pkg_resources
import time
import xarray as xr

from . import maps
from . import calc_indice
from . import subset

from icclim.util import check
from icclim.util import util_dt
from icclim.util import metadata
from icclim.util import logging_info
from icclim.util import user_indice as ui



#Initial Config
global config_file
config_file = os.path.dirname(os.path.abspath(__file__))+"/config_indice.json"


def indice(in_files,
           var_name, 
           indice_name=None,          
           slice_mode='year',
           time_range=None,
           out_file=check.icclim_output_file_defaults('file_name'),   # was: "./icclim_out.nc",
           threshold=None,
           N_lev=None,
           lev_dim_pos=1,
           transfer_limit_Mbytes=None,
           callback=None,
           callback_percentage_start_value=0,  
           callback_percentage_total=100, 
           base_period_time_range=None,
           window_width=5,
           only_leap_years=False,
           ignore_Feb29th=False,
           interpolation='linear', 
           out_unit='days',
           netcdf_version=check.icclim_output_file_defaults('netcdf_version'),  # was: 'NETCDF3_CLASSIC',
           user_indice=None,
           save_percentile=False
           ):

    '''
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

    '''

    logging_info.start_message()

    time_start = time.perf_counter()

    #######################################################
    ########## User index check params

    ########################################
    ################# TODO move all the check into check.py
    ########################################

    var_name, in_files = ui.check_features(var_name, in_files)

    VARS_in_files = ui.get_VARS_in_files(var_name, in_files)
    
    #####    we check if output path exists
    out_path = os.path.dirname(os.path.abspath(out_file)) + os.sep
    if os.path.isdir(out_path) == False:
        raise IOError('Output directory does not exists.')
        
    ind_type = check.icclim_output_file_defaults('variable_type_str')
    
    #TODO if icclim is based on xarray, the cftime module and all the function using it will be deprecated
    #ds = xr.open_mfdataset(in_files, decode_times=False)
    #if time_range is not None:
    #    time_range_xa = util_dt.from_datetime_to_cftime(ds, time_range)

    #time_range = util_dt.get_time_range(files=VARS_in_files[var_name[0]], 
    #                                    time_range=time_range, temporal_var_name='time')
 
    ########################################################################################################################
    ###### Computing index: begin
    ########################################################################################################################
    

    #####    for each target variable
    for v in var_name:
        
        ##############################################################
        ###########CHECK AND MAP ALL THE VARIABLE#####################
        #check.py
        #map the season name
        #create a check with the time subset and slice_mode i.e DJF is a special one
        #because it's in between two different years.
        #Check if there's some missing data and fill it with fill_value
        ##############################################################

        #decode_times set up to False to fit the current icclim version
        ds = xr.open_mfdataset(in_files, decode_times=False)

        data_var_names = [*ds.data_vars]
        coor_names = [*ds.coords]

        #####TODO FOR THE BETA and ONLY for the test [0] has been added at the end. On alpha version we must be able to take a list in account for multivariable
        #var_name = [name for name in data_var_names if not name.endswith('bnds')][0]
        #TODO var_name extraction could be really instable depending on the units order - change or test this line with many different dataset
        var_name = data_var_names[-1]

        ds = ds.rename({var_name:indice_name})

        ds = subset.subset_bbox(ds, time_range)

        freq_mode = maps.map_slice_mode(slice_mode)

        ds = check.formatting_before_calculation(ds, var_name, indice_name, slice_mode)

        ds = calc_indice.get_indice_calculation(indice_name, ds, **{'freq_mode':freq_mode})
        
        #ds.to_netcdf('results.nc')
        time_elapsed = (time.perf_counter() - time_start)

        logging_info.ending_message(time_elapsed)    