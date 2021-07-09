# -*- Coding: latin-1 -*-
#  Copyright CERFACS (http://cerfacs.fr/)
#  Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
#
#  Author: Natalia Tatarinova
#  Additions from Christian Page (2015-2017)

#pyximport.install(pyimport = True)

import sys
import os
from collections import OrderedDict

import numpy
import logging
import pkg_resources
import time

import pdb

from netCDF4 import Dataset, MFDataset

from . import maps, time_subset, calc_ind, set_globattr, set_longname_units, set_longname_units_custom_indices, calc_percentiles
from .icclim_exceptions import *
from .util import check, logging_info, util_nc, util_dt, files_order, arr_size, callback, read, OCGIS_tile, calc
from .util import user_indice as ui

#Initial Config
global config_file
config_file = os.path.dirname(os.path.abspath(__file__))+"/config_indice.json"


def get_key_by_value_from_dict(my_map, my_value):
    for key in my_map.keys():
        if my_value in my_map[key]:
            return key
    if my_value not in my_map.keys():
        return 'user_indice'

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

    #######################################################
    ########## User index check params

    var_name, in_files = ui.check_features(var_name, in_files)

    VARS_in_files = ui.get_VARS_in_files(var_name, in_files)

    inc = util_nc.read_netCDF(VARS_in_files[var_name[0]][0])

    if indice_name is None:
        user_indice, indice_type = ui.check_user_indice(indice_name, user_indice, time_range, var_name, out_unit)
    else:
        indice_type = ui.get_key_by_value_from_dict_ui(maps.map_indice_type, indice_name, inc, config_file) # 'simple'/'multivariable'/'percentile_based'/'percentile_based_multivariable'

    if (indice_type in ['percentile_based', 'percentile_based_multivariable'] or indice_type.startswith('user_indice_percentile_')) and base_period_time_range is None:
        raise IOError('Time range of base period is required for percentile-based indices! Please, set the "base_period_time_range" parameter.')

    ########## User index check end
    #######################################################        

    #####    callback
    if callback != None:
        global percentage_current_slice        
        percentage_current_slice = callback_percentage_start_value
    
    #####    we check if output path exists
    out_path = os.path.dirname(os.path.abspath(out_file)) + os.sep
    if os.path.isdir(out_path) == False:
        raise IOError('Output directory does not exists.')
        
    onc = util_nc.create_output_netcdf(netcdf_version, out_file)
    ind_type = check.icclim_output_file_defaults('variable_type_str')
    
    
    ########################################
    ################# META DATA: begin
    ########################################
    
    indice_dim = util_nc.copy_var_dim(inc, onc, var_name[0], lev_dim_pos=lev_dim_pos) # tuple ('time', 'lat', 'lon')    
    indice_dim = list(indice_dim)
    ncVar = inc.variables[var_name[0]] 

#   Below is a slightly involved code for handling various ways of expressing misssing data.
#   Not at all pythonic, but we need to check typing of input data and output data
#   as checking for missing values involves exact (bit level) comparison of floating point numbers
#   that may (in the worst case) be of different types.
#
#   The netCDF4 default _FillValue for float32 and float64 can be recast back and forth between
#   the two types (which is nice), but numpy.float32(1.e20) (prescibed by CMIP(5)) is not exactly
#   the same number as numpy.float64(1.e20):
#   float32(1.e20) = 100000002004087734272 (exactly)
#   float64(1.e20) = 100000000000000000000 (exactly)

#   Currently icclim cannot deal with valid_min, valid_max, and valid_range, 
#   as they imply the possibility of a range of missing/invalid values. 

    in_valid = check.check_ncVar(ncVar)
    logging_info.wrong_variable_attribute_message(in_valid)    

    fill_val = check.check_fill_value(ncVar)

    dimensions_list_var = ncVar.dimensions
    if lev_dim_pos == 0:
        index_time = 1
    else:
        index_time = 0

    ncVar_time = inc.variables[dimensions_list_var[index_time]]
    
    ############## in case of user defined thresholds 
    global nb_user_thresholds, user_thresholds    
    
    # As default, no threshold is defined, no threshold dimension is created and added to the index var
    # Also the case if we are not calculating an index
    if threshold == None: 
        nb_user_thresholds = 0        
    
    # A threshold can be given as a unique value or as a list of values, internally we always use a list
    else:
        if(type(threshold)!=list):
            user_thresholds = [threshold] 
        else:
            user_thresholds = threshold
        
        nb_user_thresholds = len(user_thresholds)
        
        if nb_user_thresholds > 1:
            util_nc.set_threshold(onc, threshold, indice_dim)
    

    if indice_type.startswith('user_indice_'):
        indice_name=user_indice['indice_name']

    ind = onc.createVariable(indice_name, ind_type, indice_dim, fill_value = fill_val)

    #####    we copy attributes from variable to process to index variable, except scale_factor and _FillValue
    util_nc.copy_var_attrs(ncVar, ind)
    
    if indice_type.startswith('user_indice_') and user_indice['date_event']==True:
      if user_indice['calc_operation'] in ['min', 'max']:            
        date_event = onc.createVariable('date_event', 'f', indice_dim, fill_value = fill_val)
        # we set the same 'calendar' and 'units' attributes as those of netCDF var 'time'
        date_event.__setattr__('calendar', ncVar_time.calendar)
        date_event.__setattr__('units', ncVar_time.units)
        
      elif user_indice['calc_operation'] in ['nb_events', 'max_nb_consecutive_events', 'run_mean', 'run_sum']:
        date_event_start = onc.createVariable('date_event_start', 'f', indice_dim, fill_value = fill_val)
        # we set the same 'calendar' and 'units' attributes as those of netCDF var 'time'
        date_event_start.__setattr__('calendar', ncVar_time.calendar)
        date_event_start.__setattr__('units', ncVar_time.units)
        
        date_event_end = onc.createVariable('date_event_end', 'f', indice_dim, fill_value = fill_val)
        # we set the same 'calendar' and 'units' attributes as those of netCDF var 'time'
        date_event_end.__setattr__('calendar', ncVar_time.calendar)
        date_event_end.__setattr__('units', ncVar_time.units)
    
    time_range = util_dt.get_time_range(files=VARS_in_files[var_name[0]], 
                                        time_range=time_range, temporal_var_name=indice_dim[0])

    if base_period_time_range is not None:
        base_period_time_range = util_dt.harmonize_hourly_timestamp(base_period_time_range, ncVar_time.calendar, time_range[0])

    
    if indice_type.startswith('user_indice_') and user_indice['calc_operation']=='anomaly':
        time_range2 = util_dt.get_time_range(files=VARS_in_files[var_name[0]], 
                                        time_range=base_period_time_range, temporal_var_name=indice_dim[0])

    # we get nb_rows (var_shape1) and nb_cols (var_shape2) to compute in the following optimal tile_dimension 
    var_shape = ncVar.shape
    var_shape1 = var_shape[-2]
    var_shape2 = var_shape[-1]

    inc.close()
    ########################################
    ################# META DATA: end
    ########################################
    
    

    ########################################################################################################################
    ###### Computing index: begin
    ########################################################################################################################
    

    ################# we create a dictionary VARS with all necessary information about each target variable
    ################# for more detailed information about the structure of this dictionary, see the util/VARS_structure.txt
    VARS = OrderedDict()

    vars_tile_dimension = []

    for v in var_name:
        
        current_var_dict = OrderedDict({
                                'files_years': OrderedDict(), 
                                'time_calendar': [],
                                'time_units': [],
                                'fill_value': [],
                                'dt_arr': [],
                                'values_arr': [], 
                                'unit_conversion_var_add':[],
                                'unit_conversion_var_scale':[],
                                'temporal_slices': OrderedDict(), 
                                'base': OrderedDict(), 
                                'files_years_base': OrderedDict()  
                                })
        
        
        VARS[v] = current_var_dict        

        dict_files_years_to_process = files_order.get_dict_files_years_to_process_in_correct_order(files_list=VARS_in_files[v], time_range=time_range)  
        
        VARS[v]['files_years'] = dict_files_years_to_process 

        # TODO: Currently the priority in this logic:   X or Y or (Z and W)   Is this correct ?
        if indice_type in ["percentile_based", "percentile_based_multivariable"] or indice_type.startswith('user_indice_percentile_') or (indice_type.startswith('user_indice_') and user_indice['calc_operation']=='anomaly'):
            dict_files_years_to_process_base = files_order.get_dict_files_years_to_process_in_correct_order(files_list=VARS_in_files[v], time_range=base_period_time_range)
            VARS[v]['files_years_base'] = dict_files_years_to_process_base

        dim_name = util_nc.check_unlimited(VARS_in_files[v][0])
        tile_dimension = arr_size.get_tile_dimension(in_files=list(dict_files_years_to_process.keys()), 
                                                     var_name=v, 
                                                     transfer_limit_Mbytes=transfer_limit_Mbytes, 
                                                     time_range=time_range)

        vars_tile_dimension.append(tile_dimension)

    tile_dimension = min(vars_tile_dimension)

    global nb_chunks
    
    # chunk tiles    
    tile_map = OCGIS_tile.get_tile_schema(nrow=var_shape1, ncol=var_shape2, tdim=tile_dimension, origin=0)
        
    nb_chunks = len(tile_map)

    global chunk_counter
    chunk_counter = 0

    
    #####    for each chunk
    for tile_id in tile_map:
        
        if len(tile_map)>1:
            logging.info("Loading data: chunk " + str(int(chunk_counter+1)) + '/'+ str(len(tile_map)) + " ...")
        else:
            logging.info("Loading data...")
        
        #####    for each target variable
        for v in var_name:
            if chunk_counter == 0:
                filename = [name for name in VARS[v]['files_years'].keys()][0]
                inc = Dataset(filename, 'r')

                ncVar = inc.variables[v]    
                dimensions_list_current_var = ncVar.dimensions
            
                # Old code (1 line below) does not take into accound that _FillValue may not exist
                # Instead we assume that the fill_value remains as assigned earlier
                # If we cannot assume this, then a proper check of the data/variable consistency across files should be done
                # fill_val = ncVar._FillValue.astype('float32') # fill value (_FillValue) must be the same type as data type: float32 (ind_type = 'f', i.e. float32)
                VARS[v]['fill_value']=fill_val

                ncVar_time = inc.variables[dimensions_list_current_var[index_time]]
             
                try:
                    calend = ncVar_time.calendar
                except:
                    calend = 'gregorian'
                 
                units = ncVar_time.units
                
                VARS[v]['time_calendar']=calend
                VARS[v]['time_units']=units

                var_units = getattr(inc.variables[v],'units')

                # Units conversion
                var_add = 0.0
                var_scale = 1.0
                if var_units == 'degC' or var_units == 'Celsius': #Kelvin
                    var_add = var_add + 273.15
                elif var_units in ["mm/s", "mm/sec", "kg m-2 s-1"]: # mm/s --> mm/day
                    var_scale = var_scale * 86400.0
                    
                VARS[v]['unit_conversion_var_add']=var_add
                VARS[v]['unit_conversion_var_scale']=var_scale

            filename = [name for name in VARS[v]['files_years'].keys()]

            if len(filename) > 1:
                nc = MFDataset(filename, 'r', aggdim=dim_name) # VARS[v]['files_years'].keys(): files of current variable
            else:
                nc = Dataset(filename[0], 'r')
                
            var_time = nc.variables[indice_dim[0]]
            var = nc.variables[v]

            ### coordinate of current chunk:
            ### indices of the left upper corner: (i1_row_current_tile, i1_col_current_tile)
            ### indices of the right lower corner: (i2_row_current_tile, i2_col_current_tile)
            i1_row_current_tile = tile_map.get(tile_id).get('row')[0]
            i2_row_current_tile = tile_map.get(tile_id).get('row')[1]
            
            i1_col_current_tile = tile_map.get(tile_id).get('col')[0]
            i2_col_current_tile = tile_map.get(tile_id).get('col')[1]  
                        
            arrs_current_chunk = util_nc.get_values_arr_and_dt_arr(ncVar_temporal=var_time, ncVar_values=var, 
                                                                     fill_val=VARS[v]['fill_value'], 
                                                                     time_range=time_range, 
                                                                     N_lev=N_lev, 
                                                                     lev_dim_pos=lev_dim_pos,
                                                                     scale_factor=VARS[v]['unit_conversion_var_scale'], 
                                                                     add_offset=VARS[v]['unit_conversion_var_add'],
                                                                     ignore_Feb29th=ignore_Feb29th, 
                                                                     i1_row_current_tile=i1_row_current_tile,
                                                                     i2_row_current_tile=i2_row_current_tile,
                                                                     i1_col_current_tile=i1_col_current_tile,
                                                                     i2_col_current_tile=i2_col_current_tile)
            
            VARS[v]['dt_arr']=arrs_current_chunk[0]            
            VARS[v]['values_arr']=arrs_current_chunk[1]


            
            if indice_type.startswith('user_indice_') and user_indice['calc_operation']=='anomaly':
                MF_nc = [MF_nc for MF_nc in VARS[v]['files_years_base'].keys()]

                if len(MF_nc) > 1:
                    ncb = MFDataset(MF_nc, 'r', aggdim=dim_name)
                else:
                    ncb = Dataset(MF_nc[0], 'r')

                var_time = ncb.variables[indice_dim[0]]
                var = ncb.variables[v]
                arrs_current_chunk_ref = util_nc.get_values_arr_and_dt_arr(ncVar_temporal=var_time, ncVar_values=var, 
                                                                            fill_val=VARS[v]['fill_value'], 
                                                                            time_range=base_period_time_range, 
                                                                            N_lev=N_lev, 
                                                                            lev_dim_pos=lev_dim_pos,
                                                                            scale_factor=VARS[v]['unit_conversion_var_scale'], 
                                                                            add_offset=VARS[v]['unit_conversion_var_add'],
                                                                            ignore_Feb29th=ignore_Feb29th,
                                                                            i1_row_current_tile=i1_row_current_tile,
                                                                            i2_row_current_tile=i2_row_current_tile,
                                                                            i1_col_current_tile=i1_col_current_tile,
                                                                            i2_col_current_tile=i2_col_current_tile)
                
                ncb.close()

                VARS[v]['values_arr_ref']=arrs_current_chunk_ref[1] # arrs_current_chunk_ref[1]: values, arrs_current_chunk_ref[0]: dt_arr


            if indice_type in ["percentile_based", "percentile_based_multivariable"] or indice_type.startswith('user_indice_percentile_'):
                MF_nc = [MF_nc for MF_nc in VARS[v]['files_years_base'].keys()]
                
                if len(MF_nc) > 1:
                    ncb = MFDataset(MF_nc, 'r', aggdim=dim_name)
                else:
                    ncb = Dataset(MF_nc[0], 'r')
                
                var_time = ncb.variables[indice_dim[0]]
                var = ncb.variables[v]
                arrs_base_current_chunk = util_nc.get_values_arr_and_dt_arr(ncVar_temporal=var_time, ncVar_values=var, 
                                                                            fill_val=VARS[v]['fill_value'], 
                                                                            time_range=base_period_time_range, 
                                                                            N_lev=N_lev, 
                                                                            lev_dim_pos=lev_dim_pos,
                                                                            scale_factor=VARS[v]['unit_conversion_var_scale'], 
                                                                            add_offset=VARS[v]['unit_conversion_var_add'],
                                                                            ignore_Feb29th=ignore_Feb29th,
                                                                            i1_row_current_tile=i1_row_current_tile,
                                                                            i2_row_current_tile=i2_row_current_tile,
                                                                            i1_col_current_tile=i1_col_current_tile,
                                                                            i2_col_current_tile=i2_col_current_tile)
                
                ncb.close()

                VARS[v]['base']['dt_arr']=arrs_base_current_chunk[0]
                VARS[v]['base']['values_arr']=arrs_base_current_chunk[1]

            dict_temporal_slices = time_subset.get_dict_temporal_slices(dt_arr=VARS[v]['dt_arr'], 
                                                                        values_arr=VARS[v]['values_arr'],
                                                                        fill_value=VARS[v]['fill_value'],
                                                                        calend=VARS[v]['time_calendar'],
                                                                        temporal_subset_mode=slice_mode, 
                                                                        time_range=time_range)
            
            VARS[v]['temporal_slices']=dict_temporal_slices
            
            
            try:
                if indice_type.startswith('user_indice_'):
                    if type(user_indice[v]['thresh'])==str:
                        VARS[v]['var_type'] = user_indice[v]['var_type']
                else:
                    VARS[v]['var_type'] = maps.map_var_type[indice_name]
            except:
                pass
                
            nc.close()


        if nb_user_thresholds == 0:
            
            if chunk_counter == 0:
                indice_arr = numpy.ma.zeros( (len(dict_temporal_slices),var_shape1, var_shape2), dtype=ind_type )
            indice_tuple_current_chunk = get_indice_from_dict_temporal_slices(indice_name=indice_name,
                                                        vars_dict=VARS,
                                                        window_width=window_width,
                                                        only_leap_years=only_leap_years,
                                                        callback=callback, callback_percentage_total=callback_percentage_total,
                                                        ignore_Feb29th=ignore_Feb29th, interpolation=interpolation,
                                                        out_unit=out_unit,
                                                        user_indice=user_indice,
                                                        out_file=out_file,
                                                        save_percentile=save_percentile) ## tuple: (dt_centroid_arr, dt_bounds_arr, indice_arr) 
            indice_arr_current_chunk = indice_tuple_current_chunk[2]

            if indice_type.startswith('user_indice_'):
                if user_indice['date_event']==True:
                    if user_indice['calc_operation'] in ['min', 'max']:            
                        date_event_arr_current_chunk = indice_tuple_current_chunk[3]
                        
                    elif user_indice['calc_operation'] in ['nb_events', 'max_nb_consecutive_events', 'run_mean', 'run_sum']:
                        date_event_start_arr_current_chunk = indice_tuple_current_chunk[3]
                        date_event_end_arr_current_chunk = indice_tuple_current_chunk[4]
                        
                        

            indice_arr[:, i1_row_current_tile:i2_row_current_tile, i1_col_current_tile:i2_col_current_tile] = indice_arr_current_chunk
                     
            
            
        
        else:
            for t in user_thresholds:                    
                if chunk_counter == 0:              
                    dict_threshold_indice_arr = OrderedDict()
                    dict_threshold_indice_arr[t] = numpy.zeros( (len(dict_temporal_slices),var_shape1, var_shape2), dtype=ind_type )
            
                
                indice_tuple_current_chunk = get_indice_from_dict_temporal_slices(indice_name=indice_name,
                                                                    vars_dict=VARS,
                                                                    thresh=t,
                                                                    callback=callback, callback_percentage_total=callback_percentage_total,
                                                                    user_indice=user_indice,
                                                                    out_file=out_file,
                                                                    save_percentile=save_percentile)  ## tuple: (dt_centroid_arr, dt_bounds_arr, indice_arr)         
                
                
                indice_arr_current_chunk = indice_tuple_current_chunk[2]
                
                # we concatenate
                dict_threshold_indice_arr[t][:, i1_row_current_tile:i2_row_current_tile, i1_col_current_tile:i2_col_current_tile] = indice_arr_current_chunk
    
        
        if chunk_counter == 0:
                dt_centroid_arr = indice_tuple_current_chunk[0]
                dt_bounds_arr = indice_tuple_current_chunk[1]
        

        chunk_counter +=1

    

    ########################################################################################################################
    ###### Computing index: end
    ########################################################################################################################
    
    
        

    
    ###########################################################################################
    ################### Writing result to out netCDF file
    ###########################################################################################        

    ######## we write array with result to "ind" (netCDF variable containing index)   
    if  nb_user_thresholds == 0:
        ind[:,:,:] = indice_arr
        
    elif nb_user_thresholds == 1:
        ind[:,:,:] = dict_threshold_indice_arr[t]
    
    elif nb_user_thresholds > 1:
        for t,key in zip(range(nb_user_thresholds),dict_threshold_indice_arr.keys()):               
                ind[:,t,:,:] = dict_threshold_indice_arr[key][:,:,:]
    
    
    ######## we write array with dates of event to "date_event" or to "date_event_start" and "date_event_end" (netCDF variables)
    if indice_type.startswith('user_indice_'):
        if user_indice['date_event']==True:
            if user_indice['calc_operation'] in ['min', 'max']:            
                date_event[:,:,:] = date_event_arr_current_chunk
            elif user_indice['calc_operation'] in ['nb_events', 'max_nb_consecutive_events', 'run_mean', 'run_sum']:
                date_event_start[:,:,:] = date_event_start_arr_current_chunk
                date_event_end[:,:,:] = date_event_end_arr_current_chunk
            
    
    
    #### we set global attributes for standard indices (not for user defined indices)
    else:        
               
        # title
        if threshold != None:
            onc.setncattr('title', 'Index {0} with user defined threshold'.format(indice_name))
        else:
            set_globattr.title(onc, indice_name)
            
        set_globattr.references(onc)
        set_globattr.comment(onc, indice_name)
        set_globattr.institution(onc, institution_str='Climate impact portal (http://climate4impact.eu)')
        set_globattr.history2(onc, slice_mode, indice_name, time_range)
        onc.setncattr('source', '')
        onc.setncattr('Conventions','CF-1.6')
        
        

        if threshold == None:
            eval('set_longname_units.' + indice_name + '_setvarattr(ind)')
            #### ==> N.B. "ECA_index" is not a valid standard name
            #### ==> IF a standard name really is required, 
            #### ==> THEN uncomment the line below and insert a name (typed as string)
            # ind.setncattr('standard_name', 'ECA_index')  
        else:
            eval('set_longname_units_custom_indices.' + indice_name + '_setvarattr(ind, threshold)')
            #### ==> N.B. "ECA_index with user defined threshold" is not a valid standard name
            #### ==> IF a standard name really is required, 
            #### ==> THEN uncomment the line below and insert a name (typed as string)
            # ind.setncattr('standard_name', 'ECA_index with user defined threshold')
            
            if nb_user_thresholds > 1:
                eval('set_longname_units_custom_indices.' + indice_name + '_setthresholdattr(thresholdvar)')
        
    
    #### for all:
    ind.missing_value = fill_val
    
        
    util_nc.set_time_values(onc, dt_centroid_arr, calend, units)
    util_nc.set_timebnds_values(onc, dt_bounds_arr, calend, units)

    onc.close()
    
    time_cpu = time.process_time()
    logging_info.ending_message(time_cpu)

    return out_file




def get_indice_from_dict_temporal_slices(indice_name, 
                                         vars_dict,
                                         thresh=None,
                                          window_width=None, only_leap_years=False,
                                          callback=None, callback_percentage_start_value=0, callback_percentage_total=100,
                                          ignore_Feb29th=False, interpolation="linear", 
                                          out_unit="days",
                                          user_indice=None,
                                          out_file=None,
                                          save_percentile=False):

    #### list of all temporal slices    
    vars_dict_keys_temp_0 = [vars_dict_keys for vars_dict_keys in vars_dict.keys()][0]
    vars_dict_keys_0 = vars_dict[vars_dict_keys_temp_0]
    t_slices = vars_dict_keys_0['temporal_slices'].keys()
    
    if user_indice == None:   ### standard indices  
        indice_type = get_key_by_value_from_dict(maps.map_indice_type, indice_name)
    else:                     ### user indices                      
        indice_type = user_indice['type'] 
        
        # we need this information in case if date_event is True 
        t_calend = vars_dict_keys_0['time_calendar'] 
        t_units = vars_dict_keys_0['time_units']
    
    
    #### if indice_type is percentile based, we define intersecting_years (in-base years)
    for v in vars_dict.keys():
        if 'var_type' in vars_dict[v].keys(): # no matter if it is 'p' or 't'
            dt_arr_base = vars_dict[v]['base']['dt_arr']
            years_base =  util_dt.get_year_list(dt_arr_base)
            years_study = [i[1] for i in t_slices]
            years_study = list(set(years_study)) # we remove duplicate years
            intersecting_years = list( set(years_base).intersection(years_study) )
            
            break # when we found intersecting_years, we exit from the loop

    if callback != None:    
        global percentage_current_slice

        nb_t_slices = len(t_slices)
        
        if thresh == None:
            percentage_slice = (callback_percentage_total*1.0)/(nb_t_slices*nb_chunks)
        elif thresh != None:
            percentage_slice = (callback_percentage_total*1.0)/(nb_t_slices*nb_user_thresholds*nb_chunks)


    dt_centroid_arr = numpy.array([])
    dt_bounds_arr = numpy.array([])
      
    #### we want to know nb of rows and columns of array
    any_slice = [temp_slice for temp_slice in t_slices][0]
    arr_shape = vars_dict_keys_0['temporal_slices'][any_slice][3].shape 

    nb_rows = arr_shape[-2]
    nb_columns = arr_shape[-1]  
        
    slice_counter = 0      
    cnt = 0
    
    pctl_thresh = {} ### dictionary to keep pctl threshold for each target variable
    pctl_calc_method = {} ### dictionary to separate pctl thresholds: computed with bootstrapping (for in-base years) or without bootstrapping (for out-of-base years)
    
    for slice_ in t_slices: # for each temporal slice
        # datetime vector of current slice is the same for all variables
        dt_arr_= vars_dict_keys_0['temporal_slices'][slice_][2]  ###   vars_dict.keys()[0] is the first target variable in the dictionary     
        dt_centroid_ = vars_dict_keys_0['temporal_slices'][slice_][0]
        dt_bounds_ = vars_dict_keys_0['temporal_slices'][slice_][1]
        
        ###### we compute index for the current slice
        
        if indice_type == 'simple':  
            values_arr = vars_dict_keys_0['temporal_slices'][slice_][3]                        
            fill_val = vars_dict_keys_0['fill_value']  
            
            
            if nb_user_thresholds == 0:
                dic_args = {'arr': values_arr, 'fill_val': fill_val} 

            else:
                dic_args = {'arr': values_arr, 'fill_val': fill_val, 'threshold': thresh}

            
            indice_slice = calc_ind.zzz(indice_name, **dic_args)
            
            
        
        elif indice_type == 'multivariable':

            vars_dict_keys_temp_1 = [vars_dict_keys for vars_dict_keys in vars_dict.keys()][1]
            vars_dict_keys_1 = vars_dict[vars_dict_keys_temp_1]
            values_arr_tasmax = vars_dict_keys_0['temporal_slices'][slice_][3]
            values_arr_tasmin = vars_dict_keys_1['temporal_slices'][slice_][3]
             
            fill_val = vars_dict_keys_0['temporal_slices'][slice_][4]
            fill_val2 = vars_dict_keys_1['temporal_slices'][slice_][4]
            
            dic_args = {'arr1': values_arr_tasmax, 'arr2': values_arr_tasmin, 
                        'fill_val1': fill_val, 'fill_val2': fill_val2} 
 
            indice_slice = calc_ind.zzz(indice_name, **dic_args)
        
        
        elif indice_type == 'user_indice_simple':
            values_arr = vars_dict_keys_0['temporal_slices'][slice_][3]
            fill_val = vars_dict_keys_0['fill_value'] 

            if user_indice['date_event']==True:
                             
                
                dic_args = {'user_indice':user_indice, 'arr':values_arr, 
                            'fill_val':fill_val, 'vars':vars_dict.keys(),
                            'dt_arr': dt_arr_, 'out_unit':out_unit}
                
                 
                indice_ = ui.get_user_indice(**dic_args)
                indice_slice = indice_[0]
                 
                 
                if user_indice['calc_operation'] in ['min', 'max']:                
                    indice_slice_date_event = indice_[1]
                    date_event_slice = calc.get_date_event_arr(dt_arr=dt_arr_, index_arr=indice_slice_date_event, 
                                                               time_calendar=t_calend, time_units=t_units, fill_val=fill_val)
                    date_event_slice = date_event_slice.reshape(-1, date_event_slice.shape[0], date_event_slice.shape[1]) # 2D --> 3D  
                     
                else:
                    indice_slice_date_event_bounds = indice_[1] 
                    indice_slice_date_event_start =  indice_slice_date_event_bounds[0]  
                    indice_slice_date_event_end =  indice_slice_date_event_bounds[1] 
                     
                    date_event_slice_start = calc.get_date_event_arr(dt_arr=dt_arr_, index_arr=indice_slice_date_event_start, 
                                                               time_calendar=t_calend, time_units=t_units, fill_val=fill_val)
                     
                    date_event_slice_end = calc.get_date_event_arr(dt_arr=dt_arr_, index_arr=indice_slice_date_event_end, 
                                                               time_calendar=t_calend, time_units=t_units, fill_val=fill_val)
                    
                    date_event_slice_start = date_event_slice_start.reshape(-1, date_event_slice_start.shape[0], date_event_slice_start.shape[1]) # 2D --> 3D
                    date_event_slice_end = date_event_slice_end.reshape(-1, date_event_slice_end.shape[0], date_event_slice_end.shape[1]) # 2D --> 3D 
                    
                    
            else:
                
                if user_indice['calc_operation'] == 'anomaly':
                    values_arr_ref = vars_dict_keys_0['values_arr_ref']
                    
                    dic_args = {'user_indice':user_indice, 'arr':[values_arr, values_arr_ref],
                                'fill_val':fill_val, 'vars':vars_dict.keys(),
                                'out_unit':out_unit}
                    
                
                else:
                    dic_args = {'user_indice':user_indice, 'arr':values_arr, 
                                'fill_val':fill_val, 'vars':vars_dict.keys(),
                                'out_unit':out_unit}
                
                indice_slice = ui.get_user_indice(**dic_args)
        
        
        
        elif indice_type == 'user_indice_multivariable':
            arrs = {}
            fv = {}
            for v in vars_dict.keys():
                arrs[v] = vars_dict[v]['temporal_slices'][slice_][3]
                fv[v] = vars_dict[v]['fill_value']

            
            if user_indice['date_event']==True:
                
                fill_val_ = vars_dict_keys_0['fill_value']
                
                
                dic_args = {'user_indice':user_indice, 'arr':arrs, 
                            'fill_val':fv, 'vars':vars_dict.keys(),
                            'dt_arr': dt_arr_, 'out_unit':out_unit}
                
                indice_ = ui.get_user_indice(**dic_args)
                indice_slice = indice_[0]
                
                indice_slice_date_event_bounds = indice_[1] 
                indice_slice_date_event_start =  indice_slice_date_event_bounds[0]  
                indice_slice_date_event_end =  indice_slice_date_event_bounds[1] 
                 
                date_event_slice_start = calc.get_date_event_arr(dt_arr=dt_arr_, index_arr=indice_slice_date_event_start, 
                                                           time_calendar=t_calend, time_units=t_units, fill_val=fill_val_)
                 
                date_event_slice_end = calc.get_date_event_arr(dt_arr=dt_arr_, index_arr=indice_slice_date_event_end, 
                                                           time_calendar=t_calend, time_units=t_units, fill_val=fill_val_)
                
                date_event_slice_start = date_event_slice_start.reshape(-1, date_event_slice_start.shape[0], date_event_slice_start.shape[1]) # 2D --> 3D
                date_event_slice_end = date_event_slice_end.reshape(-1, date_event_slice_end.shape[0], date_event_slice_end.shape[1]) # 2D --> 3D 
                    
                
                
            else:
                
                dic_args = {'user_indice':user_indice, 'arr':arrs, 
                            'fill_val':fv, 'vars':vars_dict.keys(),
                            'out_unit':out_unit}
                
                indice_slice = ui.get_user_indice(**dic_args)
        
        
        
        else: # percentile based indices (single- or multivariable)
            
            test_v = [0]*(len(vars_dict)) ### list of zeros

            ### for out-of-base years 
            if slice_[1] not in intersecting_years: # slice[1] --> year  
                current_intersecting_year = -9999
                reduced_base_years_list = [-9999]
                cnt += 1
            
            ### for in-base years
            else:
                current_intersecting_year = slice_[1]
                reduced_base_years_list = years_base[:]
                reduced_base_years_list.remove(current_intersecting_year)
            
            ### we initialize the intermediate result (for the current slice)
            indice_slice_i = numpy.ma.zeros(( len(reduced_base_years_list), nb_rows, nb_columns))            
            
            ### bootstrapping
            ### for in-base year, we remove it [the current in-base year] from base years list (reduced_base_years_list) 
            ### and duplicate each year from reduced_base_years_list to compute intermediate result for in-base year
            ### if we have N years in base period, then we have (N-1) intermediate results for each base year
            ### then we average (N-1) intermediate results to get result for one in-base year
            
            
            ytd_counter = 0
            for ytd in reduced_base_years_list: ### ytd: year to duplicate
                
                
                i=0
                ### for each variable in the dictionary
                for v in vars_dict.keys():
                
                    if 'var_type' in vars_dict[v].keys(): # if percentile-based index, we will compute a pctl threshold
                        
                        
                        ### we want to get the percentile value:
                        if indice_type == 'percentile_based':
                            pctl_value = maps.map_indice_percentile_value[indice_name][0] ### for standard indices, we take it from "maps.map_indice_percentile_value"
                        else:
                            pctl_value = int ( (user_indice[v]['thresh'])[1:] )  ### for user index, we take it from "user_indice" dictionary
                    
                    
                        if vars_dict[v]['var_type']=='p':
                            # we compute pctl array only one time
                            if slice_counter==0 and ytd_counter==0: 

                                pctl_arr = calc_percentiles.get_percentile_arr(arr=vars_dict[v]['base']['values_arr'], 
                                                                                 percentile=pctl_value,                                                            
                                                                                 callback=callback,
                                                                                 callback_percentage_start_value=0, 
                                                                                callback_percentage_total=100, 
                                                                                chunk_counter=1, 
                                                                                precipitation=True, 
                                                                                fill_val=vars_dict[v]['fill_value'],                                                                     
                                                                                interpolation=interpolation)
                                
                                
                                # we keep percentiles_arr in dictionary for following calculation of index
                                pctl_thresh[v]=pctl_arr
    
                            
                          
                        elif vars_dict[v]['var_type']=='t':
                            
                            pctl_thresh[v] = pctl_calc_method                            
                            

                            # for "out-of-base" years we compute daily_pctl_dict ONLY one time (i.e. when cnt=1)
                            if current_intersecting_year != -9999 or cnt==1:
                                new_arrs_base = time_subset.get_resampled_arrs(dt_arr=vars_dict[v]['base']['dt_arr'],
                                                       values_arr=vars_dict[v]['base']['values_arr'],
                                                       year_to_eliminate=current_intersecting_year, 
                                                       year_to_duplicate=ytd)
                                # dictionary with daily percentiles    
                                if current_intersecting_year == -9999:
                                    logging.info("Daily Percentiles calculation for out-of-base years. Please be patient...")
                                    bootstrapping = False
                                else:
                                    logging.info("[Bootstrapping] Daily Percentiles calculation for in-base year %d for %s. Duplicating %s. Please be patient...", current_intersecting_year, str(v), str(ytd))
                                    bootstrapping = True

                                daily_pctl_dict = calc_percentiles.get_percentile_dict(arr=new_arrs_base[1], 
                                                                                    dt_arr=new_arrs_base[0], 
                                                                                    percentile=pctl_value,
                                                                                    reduced_base_years_list=reduced_base_years_list,
                                                                                    ytd=ytd, 
                                                                                    window_width=window_width,
                                                                                    t_calendar=vars_dict[v]['time_calendar'], 
                                                                                    t_units=vars_dict[v]['time_units'],          
                                                                                    only_leap_years=only_leap_years, 
                                                                                    callback=None, callback_percentage_start_value=0, callback_percentage_total=100,
                                                                                    chunk_counter=1, 
                                                                                    fill_val=vars_dict[v]['fill_value'],
                                                                                    ignore_Feb29th=ignore_Feb29th,
                                                                                    interpolation='linear',
                                                                                    bootstrapping=bootstrapping)
                            if current_intersecting_year == -9999 and cnt==1:
                                pctl_thresh[v]['without_bootstrapping'] = daily_pctl_dict
                            elif current_intersecting_year != -9999:
                                pctl_thresh[v]['bootstrapping'] = daily_pctl_dict
                    test_v[i]=1 ### we change zero on 1 in the list "test_v"
                    i+=1                   
                if  all(test_v)==1: ### if "test_v" contains only 1, i.e. we checked all variables
                    
                    
                    if indice_type in ['percentile_based', 'user_indice_percentile_based']: ### based on ONE variable
                        
                        ### even if we loop on ytd, for in-base years we compute index only one time (i.e. when ytd_counter=0)
                        if indice_name in ['R75p', 'R75pTOT', 'R95p', 'R95pTOT', 'R99p', 'R99pTOT']: 
                            
                            if ytd_counter==0:
                                va = [vars_dict_keys_0 for vars_dict_keys_0 in vars_dict.keys()][0]                                
                                dic_args = {'arr': vars_dict[va]['temporal_slices'][slice_][3], 
                                            'percentile_arr': pctl_thresh[va],
                                            'fill_val':vars_dict[va]['fill_value'], 
                                            'out_unit': out_unit}
                                
                                
                                #### indice_slice_i.shape[0] is reduced_base_years_list                             
                                #### for in-base years (reduced_base_years_list>0), 
                                #### indice_slice_i will be filled anyway by the same 2D arrays len(reduced_base_years_list) numbers
                                #### (in the following we compute average of indice_slice_i[:,:,:] along axis=0)
                                numpy.ma.set_fill_value(indice_slice_i, vars_dict[va]['fill_value'])
                                indice_slice_i[:,:,:] = calc_ind.zzz(indice_name, **dic_args) # 3D with the same  2D arrays
                            
                            else:
                                
                                continue    
                        
                    
                        elif indice_name in ['TG10p', 'TX10p', 'TN10p', 'TG90p', 'TX90p', 'TN90p', 'WSDI', 'CSDI']:
                            va = [vars_dict_keys_0 for vars_dict_keys_0 in vars_dict.keys()][0]        
                            if current_intersecting_year == -9999:
                                pd = pctl_thresh[va]['without_bootstrapping']
                                
                            else:
                                pd = pctl_thresh[va]['bootstrapping']

                            dic_args = {'arr': vars_dict[va]['temporal_slices'][slice_][3], 
                                        'dt_arr': vars_dict[va]['temporal_slices'][slice_][2],
                                        'percentile_dict': pd, 
                                        'fill_val':vars_dict[va]['fill_value'], 
                                        'out_unit': out_unit}
                        
                            
                            numpy.ma.set_fill_value(indice_slice_i, vars_dict[va]['fill_value'])
                            indice_slice_i[ytd_counter,:,:] = calc_ind.zzz(indice_name, **dic_args) # 3D
                        
                        else: ####  'user_indice_percentile_based'

                            va = [vars_dict_keys_0 for vars_dict_keys_0 in vars_dict.keys()][0]
                            if vars_dict[va]['var_type']=='p':                                
                                # we need to process only "wet" days (RR >= 1.0 mm)
                                values = calc.get_wet_days(arr=vars_dict[va]['temporal_slices'][slice_][3], fill_val=vars_dict[va]['fill_value'])
                                pt = pctl_arr
                            else: ### vars_dict[va]['var_type']=='t'
                                values = arr=vars_dict[va]['temporal_slices'][slice_][3]
                                
                                if current_intersecting_year == -9999:
                                    pt = pctl_thresh[va]['without_bootstrapping']
                                else:
                                    pt= pctl_thresh[va]['bootstrapping']
                                
                            dic_args = {'user_indice': user_indice, 'arr': values, 
                                        'fill_val': vars_dict[va]['fill_value'], 
                                        'vars': vars_dict.keys(),'out_unit':out_unit,
                                        'dt_arr': dt_arr_, 'pctl_thresh': pt} 
                            
                            indice_slice_ = ui.get_user_indice(**dic_args)
                       
                            
                            
                            if user_indice['date_event']==True:

                                numpy.ma.set_fill_value(indice_slice_i, vars_dict[va]['fill_value'])
                                indice_slice_i[ytd_counter,:,:] = indice_slice_[0]
                                
                                if ytd_counter == 0:

                                    indice_slice_date_event_bounds = indice_slice_[1] 
                                
                                    if vars_dict[va]['var_type']=='p':                                    
                                        indice_slice_date_event_start =  indice_slice_date_event_bounds[0]  
                                        indice_slice_date_event_end =  indice_slice_date_event_bounds[1] 
                                    

                                    
                                    else: ### vars_dict[va]['var_type']=='t'
                                        if current_intersecting_year == -9999: ### for out-of-base years: ok                                            
                                            indice_slice_date_event_start =  indice_slice_date_event_bounds[0]  
                                            indice_slice_date_event_end =  indice_slice_date_event_bounds[1] 
                                        
                                        
                                        else: #### in-base years
                                            ### in case of bootsrapping : it is not possible to get a correct date of event
                                            ### ==> we fill all indices by -1 to get fill_value in output date of event array for in-base years
                                            indice_slice_date_event_start = indice_slice_date_event_bounds[0]*0 -1
                                            indice_slice_date_event_end = indice_slice_date_event_bounds[1]*0 -1

                            else:
    
                                numpy.ma.set_fill_value(indice_slice_i, vars_dict[va]['fill_value'])
                                indice_slice_i[ytd_counter,:,:] = indice_slice_


                    
                    
                    
                    else: ### user MULTIVARIABLE percentile indices
                        
                        arrs = {}
                        fv = {}
                        pt = {}
                        for v in vars_dict.keys():
                            
                            fv[v] = vars_dict[v]['fill_value']

                            if 'var_type' in vars_dict[v].keys():
                                
                                if vars_dict[v]['var_type']=='p':
                                    
                                    # we need to process only "wet" days (RR >= 1.0 mm)
                                    arrs[v] = calc.get_wet_days(arr=vars_dict[v]['temporal_slices'][slice_][3], fill_val=vars_dict[v]['fill_value'])
                                    
                                    pt[v] = pctl_arr
                                    
                                elif vars_dict[v]['var_type']=='t':
                                    
                                    arrs[v] = vars_dict[v]['temporal_slices'][slice_][3]
                                    
                                    if current_intersecting_year == -9999:
                                        pt[v] = pctl_thresh[v]['without_bootstrapping']
                                    else:
                                        pt[v] = pctl_thresh[v]['bootstrapping']
                                        
                            else: ### if threshold is a number 
                                arrs[v] = vars_dict[v]['temporal_slices'][slice_][3]
                                pt[v] = user_indice[v]['thresh']

                        
                        dic_args = {'user_indice': user_indice, 'arr': arrs, 
                                    'fill_val': fv, 'vars': vars_dict.keys(),
                                    'out_unit':out_unit,
                                    'dt_arr': dt_arr_, 'pctl_thresh': pt} 


                        indice_slice_ = ui.get_user_indice(**dic_args)
                       
                        if user_indice['date_event']==True:

                            numpy.ma.set_fill_value(indice_slice_i, fv[v])
                            indice_slice_i[ytd_counter,:,:] = indice_slice_[0]
                            
                            if ytd_counter == 0:
                                indice_slice_date_event_bounds = indice_slice_[1] 
                            
                                if current_intersecting_year == -9999: ### for out-of-base years: ok  
                                    indice_slice_date_event_start =  indice_slice_date_event_bounds[0]  
                                    indice_slice_date_event_end =  indice_slice_date_event_bounds[1] 
                                
                                else: #### in-base years
                                    ### in case of bootstrapping : it is not possible to get a correct date of event
                                    ### ==> we fill all indices by -1 to get fill_value in output date of event array for in-base years
                                    indice_slice_date_event_start = indice_slice_date_event_bounds[0]*0 -1
                                    indice_slice_date_event_end = indice_slice_date_event_bounds[1]*0 -1

                        else:

                            numpy.ma.set_fill_value(indice_slice_i, fv[v])
                            indice_slice_i[ytd_counter,:,:] = indice_slice_
                        
                
                
                
                ytd_counter+=1 
            

            indice_slice = numpy.ma.mean(indice_slice_i, axis=0) # 3D --> 2D
                        
            
            #### we have INDICES of date event ==> we search for the dates in dt_arr
            if indice_type in ['user_indice_percentile_based', 'user_indice_percentile_based_multivariable'] and user_indice['date_event']==True:
                date_event_slice_start = calc.get_date_event_arr(dt_arr=dt_arr_, index_arr=indice_slice_date_event_start, 
                                                           time_calendar=t_calend, time_units=t_units, 
                                                           fill_val=vars_dict_keys_0['fill_value'])
                  
                date_event_slice_end = calc.get_date_event_arr(dt_arr=dt_arr_, index_arr=indice_slice_date_event_end, 
                                                           time_calendar=t_calend, time_units=t_units, 
                                                           fill_val=vars_dict_keys_0['fill_value'])
                 
                date_event_slice_start = date_event_slice_start.reshape(-1, date_event_slice_start.shape[0], date_event_slice_start.shape[1]) # 2D --> 3D
                date_event_slice_end = date_event_slice_end.reshape(-1, date_event_slice_end.shape[0], date_event_slice_end.shape[1]) # 2D --> 3D 
            
            
            
            #### when we average indice_slice_i, values are float
            if out_unit=='days': 
                indice_slice = numpy.ma.around(indice_slice) ### we need them to be integer for out_unit="days"
#             else:
#                 indice_slice = numpy.ma.around(indice_slice, decimals=2)

        
        
        
        ### for each slice we transform indice_slice from 2D to 3D (to concatenate in the following 3D arrays along axis=0)
        indice_slice = indice_slice.reshape(-1, indice_slice.shape[0], indice_slice.shape[1]) # 2D --> 3D
        
        ### we concatenate results into indice_arr (the final result of computed index)
        if slice_counter == 0:
            indice_arr = indice_slice
        else:                
            indice_arr = numpy.ma.concatenate((indice_arr, indice_slice), axis=0)
        
        ### we concatenate date_event_slice, date_event_slice_start, date_event_slice_end into final arrays with numerical dates   
        if indice_type.startswith('user_indice_') and user_indice['date_event']==True:
            if slice_counter == 0:
                if user_indice['calc_operation'] in ['min', 'max']: 
                    date_event_arr = date_event_slice
                else:
                    date_event_start_arr = date_event_slice_start
                    date_event_end_arr = date_event_slice_end
            else:  
                if user_indice['calc_operation'] in ['min', 'max']:       
                    date_event_arr = numpy.concatenate((date_event_arr, date_event_slice), axis=0)   
                else:
                    date_event_start_arr = numpy.concatenate((date_event_start_arr, date_event_slice_start), axis=0)
                    date_event_end_arr = numpy.concatenate((date_event_end_arr, date_event_slice_end), axis=0)
         
          
        dt_centroid_arr = numpy.append(dt_centroid_arr, dt_centroid_) # 1D
        dt_bounds_arr = numpy.concatenate((dt_bounds_arr, dt_bounds_)) # 1D
        
        
        
        if callback != None:
            percentage_current_slice = percentage_current_slice + percentage_slice
            if indice_type == 'percentile_based' or indice_type == 'percentile_based_multivariable':
                if  current_intersecting_year == -9999:
                    callback(percentage_current_slice)
             
            else:
                callback(percentage_current_slice)
        
     
        slice_counter += 1

    if save_percentile:
        percentile_array = util_dt.from_OrderedDict_to_array(pt, dt_arr_, indice_slice)
        util_nc.save_percentile_netcdf(out_file, percentile_array)

    dt_bounds_arr = dt_bounds_arr.reshape(-1,2) # 1D --> 2D

     
    if indice_type.startswith('user_indice_') and user_indice['date_event']==True:
        if user_indice['calc_operation'] in ['min', 'max']: 
            return (dt_centroid_arr, dt_bounds_arr, indice_arr, date_event_arr)
        else:
            return (dt_centroid_arr, dt_bounds_arr, indice_arr, date_event_start_arr, date_event_end_arr)
    else: 
        
        return (dt_centroid_arr, dt_bounds_arr, indice_arr)
        
        



