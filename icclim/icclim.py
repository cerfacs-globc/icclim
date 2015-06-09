# -*- coding: latin-1 -*-

#  Copyright CERFACS (http://cerfacs.fr/)
#  Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
#
#  Author: Natalia Tatarinova
#  Additions from 2015/05/01: Christian Page

import numpy
from datetime import datetime
from netCDF4 import num2date, date2num, Dataset, MFDataset
#from netcdftime import utime

import time
import pickle
import os
from collections import OrderedDict

from calc_indice import *
from calc_indice_perc import *

import set_globattr
import set_longname_units
import set_longname_units_custom_indices
import percentile_dict

#import util.callback as callback
import util.util_dt as util_dt
import util.util_nc as util_nc
import util.arr_size as arr_size
import util.OCGIS_tile as OCGIS_tile
import util.files_order as files_order
import time_subset

import sys

   

map_indice_type =   {
                        'simple': ['TG', 'TX', 'TN', 'TXx', 'TXn', 'TNx', 'TNn', 'SU', 'TR', 'CSU', 'GD4', 'FD', 'CFD',
                                   'ID', 'HD17', 'CDD', 'CWD', 'RR', 'RR1', 'SDII', 'R10mm', 'R20mm', 'RX1day', 'RX5day',
                                   'SD', 'SD1', 'SD5cm', 'SD50cm'],
                            
                        'multivariable': ['DTR', 'ETR', 'vDTR'],

                        'multiperiod': ['SUB'],
                 
                        'simple_time_aggregation': ['TIMEAVG'],
                            
                        'percentile_based': ['TG10p', 'TX10p', 'TN10p', 'TG90p', 'TX90p', 'TN90p', 'WSDI', 'CSDI',
                                             'R75p', 'R75TOT', 'R95p', 'R95TOT', 'R99p', 'R99TOT'],
                            
                        'percentile_based_multivariable': ['CD', 'CW', 'WD', 'WW']
                    }

def get_key_by_value_from_dict(my_map, my_value):
    for key in my_map.keys():
        if my_value in my_map[key]:
            return key


       
def indice(indice_name,
           in_files,
           var_name,           
           slice_mode=None,
           time_range=None,
           out_file="./icclim_out.nc",
           threshold=None,
           N_lev=None,
           transfer_limit_Mbytes=None,
           callback=None,
           callback_percentage_start_value=0,
           callback_percentage_total=100,
           percentile_dict=None,
           in_files2=None,
           var_name2=None,
           time_range2=None,
           percentile_dict2=None):

    
    '''

    
    :param indice_name: Climate indice name. 
    :type indice_name: str    
    
    :param in_files: Absolute path(s) to NetCDF dataset(s) (including OPeNDAP URLs).
    :type in_files: list of str

    :param var_name: Target variable name to process corresponding to ``in_files``.
    :type var_name: str
         
    :param slice_mode: Type of temporal aggregation: "year", "month", "DJF", "MAM", "JJA", "SON", "ONDJFM" or "AMJJAS". If ``None``, the indice will be calculated as monthly values.
    :type slice_mode: str
    
    :param time_range: Temporal range: upper and lower bounds for temporal subsetting. If ``None``, whole period of input files will be processed.
    :type time_range: [datetime.datetime, datetime.datetime]

    :param out_file: Output NetCDF file name (default: "icclim_out.nc" in the current directory).
    :type out_file: str
       
    :param threshold: User defined threshold for certain indices.
    :type threshold: float or list of floats
    
    :param N_lev: Level number if 4D variable.
    :type N_lev: int
    
    :param transfer_limit_Mbytes: Maximum OPeNDAP/THREDDS request limit in Mbytes in case of OPeNDAP datasets.
    :type transfer_limit_Mbytes: float
    
    :param callback: Progress bar printing. If ``None``, progress bar will not be printed. 
    :type callback: :func:`callback.defaultCallback`
    
    :param callback_percentage_start_value: Initial value of percentage of the progress bar (default: 0).
    :type callback_percentage_start_value: int
    
    :param callback_percentage_total: Total persentage value (default: 100).   
    :type callback_percentage_total: int
    
    :param percentile_dict: For percentile-based indices: dictionary with calendar days as keys and 2D arrays with percentiles as values as returned from :func:`icclim.get_percentile_dict`, corresponding to ``var_name``.
    :type percentile_dict: dict 
    
    :param in_files2: Absolute path(s) to NetCDF dataset(s) (including OPeNDAP URLs).
    :type in_files2: list of str
    
    :param var_name2: Target variable name to process corresponding to ``in_files2``.
    :type var_name2: str
    
    :param time_range2: Temporal range: upper and lower bounds for temporal subsetting. If ``None``, whole period of input files will be processed.
    :type time_range2: [datetime.datetime, datetime.datetime]

    :param percentile_dict2: For percentile-based indices: dictionary with calendar days as keys and 2D arrays with percentiles as values as returned from :func:`icclim.get_percentile_dict`, corresponding to ``var_name2``.
    :type percentile_dict2: dict
    
    :rtype: path to NetCDF file

    .. warning:: If ``out_file`` already exists, Icclim will overwrite it!
    
    .. warning:: Precipitation input units are considered to be in [kg m-2 s-1].
    '''
    
    if slice_mode == None:
        slice_mode = 'month'
    
    # we define the type of selected indice
    # simple_time_aggregation and multiperiod are statistics and not indices, so threshold is ignored in those cases
    indice_type = get_key_by_value_from_dict(map_indice_type, indice_name) # 'simple'/'multivariable'/'multiperiod'/'simple_time_aggregation'/'percentile_based'/'percentile_based_multivariable'
    
    if indice_type == 'multivariable' and (    (in_files2==None or var_name2==None) ): 
        print "Error: Both parameters 'in_files2' and 'var_name2' must be provided."
        sys.exit()
    
    elif indice_type == 'multiperiod' and (    (in_files2==None or var_name2==None or time_range2==None) ): 
        print "Error: Both parameters 'in_files2' 'var_name2' and 'time_range2' must be provided."
        sys.exit()
    
    elif indice_type == 'percentile_based' and percentile_dict==None:
        print "Error: The parameter 'percentile_dict' must be provided."
        sys.exit()
        
    elif indice_type == 'percentile_based_multivariable' and (percentile_dict==None or in_files2==None or var_name2==None or percentile_dict2==None):
        print "Error: All following parameters must be provided: 'percentile_dict', 'in_files2', 'var_name2', 'percentile_dict2'."
        sys.exit()

    # we open any input file (for example, the first one) of each target variable to get necessary information 
    inc = Dataset(in_files[0], 'r')
    if indice_type == 'multivariable' or indice_type == 'percentile_based_multivariable' or indice_type == 'multiperiod':
        inc2 = Dataset(in_files2[0], 'r')
    
    global fill_val    
    fill_val = util_nc.get_att_value(inc, var_name, '_FillValue').astype('float32') # fill value (_FillValue) must be the same type as data type: float32 (line below: ind_type = 'f', i.e. float32)
    if indice_type == 'multivariable' or indice_type == 'percentile_based_multivariable' or indice_type == 'multiperiod':
        global fill_val2
        fill_val2 = util_nc.get_att_value(inc2, var_name2, '_FillValue').astype('float32')
    
    onc = Dataset(out_file, 'w' ,format="NETCDF3_CLASSIC")

    indice_dim = util_nc.copy_var_dim(inc, onc, var_name) # tuple ('time', 'lat', 'lon')
    
    indice_dim = list(indice_dim)

    if indice_type == 'multiperiod' or indice_type == 'multivariable' or indice_type == 'percentile_based_multivariable':
        indice_dim2 = util_nc.list_var_dim(inc2, var_name2) # tuple ('time', 'lat', 'lon')
    
        indice_dim2 = list(indice_dim2)

    # in case of user defined thresholds 
    global nb_user_thresholds, user_thresholds    
    
    # As default, no threshold is defined, no threshold dimension is created and added to the indice var
    # Also the case if we are not calculating an indice
    if threshold == None or indice_type == 'simple_time_aggregation' or indice_type == 'multiperiod':
        nb_user_thresholds = 0        
    
    # A threshold can be given as a unique value or as a list of values, internally we always use a list
    else:
        if(type(threshold)!=list):
            user_thresholds = [threshold] 
        else:
            user_thresholds = threshold
        
        nb_user_thresholds = len(user_thresholds)
        
        if nb_user_thresholds > 1:        
            # Create an extra dimension for the indice:
            indice_dim.insert(1,'threshold')
            onc.createDimension('threshold',nb_user_thresholds)
            thresholdvar = onc.createVariable('threshold','f8',('threshold'))
            thresholdvar[:] = user_thresholds
            thresholdvar.setncattr("units","threshold")
            thresholdvar.setncattr("standard_name","threshold")
    
    index_row = len(indice_dim)-2
    index_col = len(indice_dim)-1
    index_time = 0
    
    nb_rows = inc.variables[indice_dim[index_row]].shape[0]
    nb_columns = inc.variables[indice_dim[index_col]].shape[0]
    
    #global calend, units
    
    ncVar_time = inc.variables[indice_dim[index_time]]

    try:
       calend = ncVar_time.calendar
    except:
        calend = 'gregorian'
        
    units = ncVar_time.units

    if indice_type == 'multiperiod' or indice_type == 'multivariable' or indice_type == 'percentile_based_multivariable':
        ncVar_time2 = inc2.variables[indice_dim2[index_time]]
    
        try:
            calend2 = ncVar_time2.calendar
        except:
            calend2 = 'gregorian'
        
        units2 = ncVar_time2.units

        var_units2 = getattr(inc2.variables[var_name2],'units')

        # Units conversion
        var_add2 = 0.0
        var_scale2 = 1.0
        if var_units2 == 'degC' or var_units2 == 'Celcius': #Kelvin
            var_add2 = var_add2 + 273.15
        elif var_units2 == 'mm': # kg m-2 s-1 (mm/s)
            var_scale2 = var_scale2 / 86400.0
    
    #try:
    #    calend = util_nc.get_att_value(inc, indice_dim[index_time], 'calendar')
    #except:
    #    calend = 'gregorian'
    #
    #units = util_nc.get_att_value(inc, indice_dim[index_time], 'units')
    

    ind_type = 'f' # 'float32'
    
    #fill_val = get_att_value(inc, var_name, '_FillValue').astype(ind_type) # fill value (_FillValue) must be the same type as data type: float32 (line below: ind_type = 'f', i.e. float32)

    # Copy info from variable
    var_longname = getattr(inc.variables[var_name],'long_name')
    var_units = getattr(inc.variables[var_name],'units')
    var_standardname = getattr(inc.variables[var_name],'standard_name')

    # Units conversion
    var_add = 0.0
    var_scale = 1.0
    if var_units == 'degC' or var_units == 'Celsius': #Kelvin
        var_add = var_add + 273.15
    elif var_units == 'mm': # kg m-2 s-1 (mm/s)
        var_scale = var_scale / 86400.0

    if indice_type == 'simple_time_aggregation' or indice_type == 'multiperiod':
        ind = onc.createVariable(var_name, ind_type, indice_dim, fill_value = fill_val)
    else:
        ind = onc.createVariable(indice_name, ind_type, indice_dim, fill_value = fill_val)
    
    # Copy attributes from variable to process to indice variable, except scale_factor and _FillValue
    util_nc.copy_var_attrs(inc.variables[var_name],ind)

    if time_range == None:
        time_range = util_dt.get_time_range(in_files, temporal_var_name=indice_dim[0])
        
    else: # i.e. time_range is selected by user
        # we adjust datetime.datetime objects from time_range 
        t_arr = inc.variables[indice_dim[0]][:]
        dt = util_dt.num2date(t_arr[0], calend, units)
        del t_arr
        time_range = util_dt.adjust_time_range(time_range, dt)

    if indice_type == 'multiperiod':
        if time_range2 == None:
            time_range2 = util_dt.get_time_range(in_files2, temporal_var_name=indice_dim2[0])
        
        else: # i.e. time_range is selected by user
            # we adjust datetime.datetime objects from time_range 
            t_arr2 = inc.variables[indice_dim2[0]][:]
            dt2 = util_dt.num2date(t_arr2[0], calend2, units)
            del t_arr2
            time_range2 = util_dt.adjust_time_range(time_range2, dt2)
    
    inc.close()
    if indice_type == 'multivariable' or indice_type == 'percentile_based_multivariable' or indice_type == 'multiperiod':
        inc2.close()
    
    
    
        
    dict_files_years_to_process = files_order.get_dict_files_years_to_process_in_correct_order(files_list=in_files, time_range=time_range)
    dim_name = util_nc.check_unlimited(in_files[0])
    nc = MFDataset(dict_files_years_to_process.keys(), 'r', aggdim=dim_name) # dict_files_years_to_process.keys() = in_files
    var_time = nc.variables[indice_dim[0]]
    var = nc.variables[var_name]

    if indice_type == 'multivariable' or indice_type == 'percentile_based_multivariable':
        dict_files_years_to_process2 = files_order.get_dict_files_years_to_process_in_correct_order(files_list=in_files2, time_range=time_range)
        dim_name2 = util_nc.check_unlimited(in_files2[0])
        nc2 = MFDataset(dict_files_years_to_process2.keys(), 'r', aggdim=dim_name2) # dict_files_years_to_process.keys() = in_files2
        var_time2 = nc2.variables[indice_dim[0]]
        var2 = nc2.variables[var_name2]

    elif indice_type == 'multiperiod':
        dict_files_years_to_process2 = files_order.get_dict_files_years_to_process_in_correct_order(files_list=in_files2, time_range=time_range2)
        dim_name2 = util_nc.check_unlimited(in_files2[0])
        nc2 = MFDataset(dict_files_years_to_process2.keys(), 'r', aggdim=dim_name2) # dict_files_years_to_process.keys() = in_files2
        var_time2 = nc2.variables[indice_dim2[0]]
        var2 = nc2.variables[var_name2]
    
    if callback != None:
        global percentage_current_key        
        percentage_current_key = callback_percentage_start_value
    
    if transfer_limit_Mbytes == None: # i.e. we work with local files
        
        arrs = util_nc.get_values_arr_and_dt_arr(ncVar_temporal=var_time, ncVar_values=var, time_range=time_range, N_lev=N_lev, scale_factor=var_scale, add_offset=var_add)

        try:
            calend = var_time.calendar
        except:
            calend = 'gregorian'
        dt_arr = arrs[0]
        values_arr = arrs[1]

        if indice_type == 'multivariable' or indice_type == 'percentile_based_multivariable':
            arrs2 = util_nc.get_values_arr_and_dt_arr(ncVar_temporal=var_time2, ncVar_values=var2, time_range=time_range, N_lev=N_lev, scale_factor=var_scale2, add_offset=var_add2)
            try:
                calend2 = var_time2.calendar
            except:
                calend2 = 'gregorian'
            dt_arr2 = arrs2[0]
            values_arr2 = arrs2[1]

            if not numpy.array_equal(dt_arr, dt_arr2):
                print 'Error: Time step vectors of both file lists must be equal!'
                sys.exit()

        elif indice_type == 'multiperiod':
            arrs2 = util_nc.get_values_arr_and_dt_arr(ncVar_temporal=var_time2, ncVar_values=var2, time_range=time_range2, N_lev=N_lev, scale_factor=var_scale2, add_offset=var_add2)
            try:
                calend2 = var_time2.calendar
            except:
                calend2 = 'gregorian'
            dt_arr2 = arrs2[0]
            values_arr2 = arrs2[1]

            if not numpy.array_equal(dt_arr, dt_arr2):
                print 'Error: Time step vectors of both file lists must be equal!'
                sys.exit()

        dict_temporal_slices = time_subset.get_dict_temporal_slices(dt_arr=dt_arr, values_arr=values_arr, calend=calend, temporal_subset_mode=slice_mode, time_range=time_range)
        if indice_type == 'multivariable' or indice_type == 'percentile_based_multivariable':
            dict_temporal_slices2 = time_subset.get_dict_temporal_slices(dt_arr=dt_arr2, values_arr=values_arr2, calend=calend2, temporal_subset_mode=slice_mode, time_range=time_range)
        elif indice_type == 'multiperiod':
            dict_temporal_slices2 = time_subset.get_dict_temporal_slices(dt_arr=dt_arr2, values_arr=values_arr2, calend=calend2, temporal_subset_mode=slice_mode, time_range=time_range2)
        
        if nb_user_thresholds == 0:
                        
            if indice_type == 'simple' or indice_type == 'simple_time_aggregation':
                indice_tuple = get_indice_from_dict_temporal_slices(indice_name=indice_name,
                                                                    dict_temporal_slices=dict_temporal_slices,
                                                                    callback=callback, callback_percentage_total=callback_percentage_total) ## tuple: (dt_centroid_arr, dt_bounds_arr, indice_arr) 
                
            elif indice_type == 'multivariable' or indice_type == 'multiperiod':
                indice_tuple = get_indice_from_dict_temporal_slices(indice_name=indice_name,
                                                                    dict_temporal_slices=dict_temporal_slices,
                                                                    dict_temporal_slices2=dict_temporal_slices2,
                                                                    callback=callback, callback_percentage_total=callback_percentage_total) ## tuple: (dt_centroid_arr, dt_bounds_arr, indice_arr) 
            
            elif indice_type == 'percentile_based':
                indice_tuple = get_indice_from_dict_temporal_slices(indice_name=indice_name,
                                                                    dict_temporal_slices=dict_temporal_slices,
                                                                    percentile_dict=percentile_dict,
                                                                    callback=callback, callback_percentage_total=callback_percentage_total) ## tuple: (dt_centroid_arr, dt_bounds_arr, indice_arr) 
            
                
            elif indice_type == 'percentile_based_multivariable':
                indice_tuple = get_indice_from_dict_temporal_slices(indice_name=indice_name,
                                                                    dict_temporal_slices=dict_temporal_slices,
                                                                    percentile_dict=percentile_dict,
                                                                    dict_temporal_slices2=dict_temporal_slices2,
                                                                    percentile_dict2=percentile_dict2,
                                                                    callback=callback, callback_percentage_total=callback_percentage_total) ## tuple: (dt_centroid_arr, dt_bounds_arr, indice_arr) 
            
            
            indice_arr = indice_tuple[2]

        else:
            dict_threshold_indice_arr = OrderedDict()
            for t in user_thresholds:
                indice_tuple = get_indice_from_dict_temporal_slices(indice_name=indice_name,
                                                                    dict_temporal_slices=dict_temporal_slices,
                                                                    thresh=t,
                                                                    callback=callback, callback_percentage_total=callback_percentage_total)  ## tuple: (dt_centroid_arr, dt_bounds_arr, indice_arr)         
                dict_threshold_indice_arr[t] = indice_tuple[2]
                
        dt_centroid_arr = indice_tuple[0]
        dt_bounds_arr = indice_tuple[1]
        
        
    else: # i.e. we work with OPeNDAP datasets
        # we convert Mbytes in bytes (1 Kbyte = 1024 bytes)
        transfer_limit_bytes = transfer_limit_Mbytes * 1024 * 1024
        total_array_size_bytes_and_tile_dimension = arr_size.get_total_array_size_bytes_and_tile_dimension(dict_files_years_to_process.keys(), var_name, transfer_limit_bytes, time_range=time_range)
        array_total_size = total_array_size_bytes_and_tile_dimension[0]
                
        
        if array_total_size < transfer_limit_bytes: # the same as for the "if transfer_limit_Mbytes == None" case
            
            print "Data transfer... "

            arrs = util_nc.get_values_arr_and_dt_arr(ncVar_temporal=var_time, ncVar_values=var, time_range=time_range, N_lev=N_lev, scale_factor=var_scale, add_offset=var_add)
            try:
                calend = var_time.calendar
            except:
                calend = 'gregorian'
            dt_arr = arrs[0]
            values_arr = arrs[1]

            if indice_type == 'multivariable' or indice_type == 'percentile_based_multivariable':
                arrs2 = util_nc.get_values_arr_and_dt_arr(ncVar_temporal=var_time2, ncVar_values=var2, time_range=time_range, N_lev=N_lev, scale_factor=var_scale2, add_offset=var_add2)
                try:
                    calend2 = var_time2.calendar
                except:
                    calend2 = 'gregorian'
                dt_arr2 = arrs2[0]
                values_arr2 = arrs2[1]
    
                if not numpy.array_equal(dt_arr, dt_arr2):
                    print 'Error: Time step vectors of both file lists must be equal!'
                    sys.exit()

            elif indice_type == 'multiperiod':
                arrs2 = util_nc.get_values_arr_and_dt_arr(ncVar_temporal=var_time2, ncVar_values=var2, time_range=time_range2, N_lev=N_lev, scale_factor=var_scale2, add_offset=var_add2)
                try:
                    calend2 = var_time2.calendar
                except:
                    calend2 = 'gregorian'
                dt_arr2 = arrs2[0]
                values_arr2 = arrs2[1]
    
                if not numpy.array_equal(dt_arr, dt_arr2):
                    print 'Error: Time step vectors of both file lists must be equal!'
                    sys.exit()
            
    
            dict_temporal_slices = time_subset.get_dict_temporal_slices(dt_arr=dt_arr, values_arr=values_arr, calend=calend, temporal_subset_mode=slice_mode, time_range=time_range)
            if indice_type == 'multivariable' or indice_type == 'percentile_based_multivariable':
                dict_temporal_slices2 = time_subset.get_dict_temporal_slices(dt_arr=dt_arr2, values_arr=values_arr2, calend=calend2, temporal_subset_mode=slice_mode, time_range=time_range)
            elif indice_type == 'multiperiod':
                dict_temporal_slices2 = time_subset.get_dict_temporal_slices(dt_arr=dt_arr2, values_arr=values_arr2, calend=calend2, temporal_subset_mode=slice_mode, time_range=time_range2)

            if nb_user_thresholds == 0:
                if indice_type == 'simple' or indice_type == 'simple_time_aggregation':
                    indice_tuple = get_indice_from_dict_temporal_slices(indice_name=indice_name,
                                                                        dict_temporal_slices=dict_temporal_slices,
                                                                        callback=callback, callback_percentage_total=callback_percentage_total) ## tuple: (dt_centroid_arr, dt_bounds_arr, indice_arr) 
                    
                elif indice_type == 'multivariable' or indice_type == 'multiperiod':
                    indice_tuple = get_indice_from_dict_temporal_slices(indice_name=indice_name,
                                                                        dict_temporal_slices=dict_temporal_slices,
                                                                        dict_temporal_slices2=dict_temporal_slices2,
                                                                        callback=callback, callback_percentage_total=callback_percentage_total) ## tuple: (dt_centroid_arr, dt_bounds_arr, indice_arr) 
                
                elif indice_type == 'percentile_based':
                    indice_tuple = get_indice_from_dict_temporal_slices(indice_name=indice_name,
                                                                        dict_temporal_slices=dict_temporal_slices,
                                                                        percentile_dict=percentile_dict,
                                                                        callback=callback, callback_percentage_total=callback_percentage_total) ## tuple: (dt_centroid_arr, dt_bounds_arr, indice_arr) 
                
                    
                elif indice_type == 'percentile_based_multivariable':
                    indice_tuple = get_indice_from_dict_temporal_slices(indice_name=indice_name,
                                                                        dict_temporal_slices=dict_temporal_slices,
                                                                        percentile_dict=percentile_dict,
                                                                        dict_temporal_slices2=dict_temporal_slices2,
                                                                        percentile_dict2=percentile_dict2,
                                                                        callback=callback, callback_percentage_total=callback_percentage_total) ## tuple: (dt_centroid_arr, dt_bounds_arr, indice_arr) 
                
                indice_arr = indice_tuple[2]
                
            else:
                dict_threshold_indice_arr = OrderedDict()
                for t in user_thresholds:
                    indice_tuple = get_indice_from_dict_temporal_slices(indice_name=indice_name,
                                                                    dict_temporal_slices=dict_temporal_slices,
                                                                    thresh=t,
                                                                    callback=callback, callback_percentage_total=callback_percentage_total)  ## tuple: (dt_centroid_arr, dt_bounds_arr, indice_arr)         
                    dict_threshold_indice_arr[t] = indice_tuple[2]
                
            dt_centroid_arr = indice_tuple[0]
            dt_bounds_arr = indice_tuple[1]
            

        else:            
            # then we do chunking in space
            tile_dimension = total_array_size_bytes_and_tile_dimension[1]
            var_shape = var.shape
            var_shape1 = var_shape[1]
            var_shape2 = var_shape[2]

            
            tile_map = OCGIS_tile.get_tile_schema(nrow=var_shape1, ncol=var_shape2, tdim=tile_dimension, origin=0)
            global nb_chunks
            nb_chunks = len(tile_map)
            print str(nb_chunks) + " data chunks will be transfered."

            if nb_user_thresholds != 0:
                dict_threshold_indice_arr = OrderedDict()

            chunk_counter = 0  # chunk counter           
            for tile_id in tile_map:
                print "Data transfer: chunk " + str(int(chunk_counter+1)) + '/'+ str(len(tile_map)) + " ..."
                
                global i1_row_current_tile, i2_row_current_tile, i1_col_current_tile, i2_col_current_tile
                
                i1_row_current_tile = tile_map.get(tile_id).get('row')[0]
                i2_row_current_tile = tile_map.get(tile_id).get('row')[1]
                
                i1_col_current_tile = tile_map.get(tile_id).get('col')[0]
                i2_col_current_tile = tile_map.get(tile_id).get('col')[1]
                
                arrs_current_chunk = util_nc.get_values_arr_and_dt_arr(ncVar_temporal=var_time, ncVar_values=var, time_range=time_range, N_lev=N_lev, spatial_chunking=True, scale_factor=var_scale, add_offset=var_add,
                                                                       i1_row_current_tile=i1_row_current_tile,
                                                                       i2_row_current_tile=i2_row_current_tile,
                                                                       i1_col_current_tile=i1_col_current_tile,
                                                                       i2_col_current_tile=i2_col_current_tile)
                dt_arr = arrs_current_chunk[0]
                values_arr_current_chunk = arrs_current_chunk[1]
                
                if indice_type == 'multivariable' or indice_type == 'percentile_based_multivariable':
                    arrs_current_chunk2 = util_nc.get_values_arr_and_dt_arr(ncVar_temporal=var_time2, ncVar_values=var2, time_range=time_range, N_lev=N_lev, spatial_chunking=True, scale_factor=var_scale2, add_offset=var_add2,
                                                                            i1_row_current_tile=i1_row_current_tile,
                                                                            i2_row_current_tile=i2_row_current_tile,
                                                                            i1_col_current_tile=i1_col_current_tile,
                                                                            i2_col_current_tile=i2_col_current_tile)
                    dt_arr2 = arrs_current_chunk2[0]
                    values_arr_current_chunk2 = arrs_current_chunk2[1]  

                elif indice_type == 'multiperiod':
                    arrs_current_chunk2 = util_nc.get_values_arr_and_dt_arr(ncVar_temporal=var_time2, ncVar_values=var2, time_range=time_range2, N_lev=N_lev, spatial_chunking=True, scale_factor=var_scale2, add_offset=var_add2,
                                                                            i1_row_current_tile=i1_row_current_tile,
                                                                            i2_row_current_tile=i2_row_current_tile,
                                                                            i1_col_current_tile=i1_col_current_tile,
                                                                            i2_col_current_tile=i2_col_current_tile)
                    dt_arr2 = arrs_current_chunk2[0]
                    values_arr_current_chunk2 = arrs_current_chunk2[1]  
                
                
                
                if indice_type == 'percentile_based':
                    percentile_dict_current_chunk = get_subset_percentile_dict(percentile_dict)

                elif indice_type == 'percentile_based_multivariable':
                    percentile_dict_current_chunk = get_subset_percentile_dict(percentile_dict)
                    percentile_dict_current_chunk2 = get_subset_percentile_dict(percentile_dict2)
                    
        
                dict_temporal_slices_current_chunk = time_subset.get_dict_temporal_slices(dt_arr=dt_arr, values_arr=values_arr_current_chunk, calend=calend, temporal_subset_mode=slice_mode, time_range=time_range)
                if indice_type == 'multivariable' or indice_type == 'percentile_based_multivariable':
                    dict_temporal_slices_current_chunk2 = time_subset.get_dict_temporal_slices(dt_arr=dt_arr2, values_arr=values_arr_current_chunk2, calend=calend2, temporal_subset_mode=slice_mode, time_range=time_range)
                elif indice_type == 'multiperiod':
                    dict_temporal_slices_current_chunk2 = time_subset.get_dict_temporal_slices(dt_arr=dt_arr2, values_arr=values_arr_current_chunk2, calend=calend2, temporal_subset_mode=slice_mode, time_range=time_range2)
                
                
                
                
                if nb_user_thresholds == 0:
                    
                    if chunk_counter == 0:
                        if indice_type == 'simple_time_aggregation':
                            indice_arr = numpy.zeros( (1,var_shape1, var_shape2), dtype=ind_type )
                        else:
                            indice_arr = numpy.zeros( (len(dict_temporal_slices_current_chunk),var_shape1, var_shape2), dtype=ind_type )
                    
                    if indice_type == 'simple' or indice_type == 'simple_time_aggregation':
                        indice_tuple_current_chunk = get_indice_from_dict_temporal_slices(indice_name=indice_name,
                                                                            dict_temporal_slices=dict_temporal_slices_current_chunk,
                                                                            chunking=True,
                                                                            callback=callback, callback_percentage_total=callback_percentage_total) ## tuple: (dt_centroid_arr, dt_bounds_arr, indice_arr) 
                        
                    elif indice_type == 'multivariable' or indice_type == 'multiperiod':
                        indice_tuple_current_chunk = get_indice_from_dict_temporal_slices(indice_name=indice_name,
                                                                            dict_temporal_slices=dict_temporal_slices_current_chunk,
                                                                            dict_temporal_slices2=dict_temporal_slices_current_chunk2,
                                                                            chunking=True,
                                                                            callback=callback, callback_percentage_total=callback_percentage_total) ## tuple: (dt_centroid_arr, dt_bounds_arr, indice_arr) 
                    
                    elif indice_type == 'percentile_based':
                        indice_tuple_current_chunk = get_indice_from_dict_temporal_slices(indice_name=indice_name,
                                                                            dict_temporal_slices=dict_temporal_slices_current_chunk,
                                                                            percentile_dict=percentile_dict_current_chunk, ####### ??????????
                                                                            chunking=True,
                                                                            callback=callback, callback_percentage_total=callback_percentage_total) ## tuple: (dt_centroid_arr, dt_bounds_arr, indice_arr) 
                    
                        
                    elif indice_type == 'percentile_based_multivariable':
                        indice_tuple_current_chunk = get_indice_from_dict_temporal_slices(indice_name=indice_name,
                                                                            dict_temporal_slices=dict_temporal_slices_current_chunk,
                                                                            percentile_dict=percentile_dict_current_chunk,
                                                                            dict_temporal_slices2=dict_temporal_slices_current_chunk2,
                                                                            percentile_dict2=percentile_dict_current_chunk2,
                                                                            chunking=True,
                                                                            callback=callback, callback_percentage_total=callback_percentage_total) ## tuple: (dt_centroid_arr, dt_bounds_arr, indice_arr) 
                    

                    
                    indice_arr_current_chunk = indice_tuple_current_chunk[2]
                    if indice_type == 'simple_time_aggregation':
                        indice_arr[:, i1_row_current_tile:i2_row_current_tile, i1_col_current_tile:i2_col_current_tile] += indice_arr_current_chunk
                    else:
                    # we concatenate
                        indice_arr[:, i1_row_current_tile:i2_row_current_tile, i1_col_current_tile:i2_col_current_tile] = indice_arr_current_chunk
                                    
                else:                     
                    for t in user_thresholds:
                        if chunk_counter == 0:		      
                            dict_threshold_indice_arr[t] = numpy.zeros( (len(dict_temporal_slices_current_chunk),var_shape1, var_shape2), dtype=ind_type )
                
                        indice_tuple_current_chunk = get_indice_from_dict_temporal_slices(dict_temporal_slices = dict_temporal_slices_current_chunk, indice_name=indice_name, thresh=t, chunking=True, callback=callback, callback_percentage_total=callback_percentage_total) ## tuple: (dt_centroid_arr, dt_bounds_arr, dict_indice_arr_current_chunk)                        
                        indice_arr_current_chunk = indice_tuple_current_chunk[2]
                        # we concatenate
                        dict_threshold_indice_arr[t][:, i1_row_current_tile:i2_row_current_tile, i1_col_current_tile:i2_col_current_tile] = indice_arr_current_chunk

                if chunk_counter == 0:
                    dt_centroid_arr = indice_tuple_current_chunk[0]
                    dt_bounds_arr = indice_tuple_current_chunk[1]
                
                chunk_counter +=1

            
    
    nc.close()
    if indice_type == 'multivariable' or indice_type == 'percentile_based_multivariable' or indice_type == 'multiperiod':
        nc2.close()
    
    # we copy data to the nc variable 
    if  nb_user_thresholds == 0:
        ind[:,:,:] = indice_arr
        
    elif nb_user_thresholds == 1:
        ind[:,:,:] = dict_threshold_indice_arr[t]
    
    elif nb_user_thresholds > 1:
        for t,key in zip(range(nb_user_thresholds),dict_threshold_indice_arr.keys()):               
                ind[:,t,:,:] = dict_threshold_indice_arr[key][:,:,:]



    # set global attributes
    
    # title
    if threshold != None:
        onc.setncattr('title', 'Indice {0} with user defined threshold'.format(indice_name))
    else:
        set_globattr.title(onc, indice_name)
        
    set_globattr.references(onc)
    set_globattr.comment(onc, indice_name)
    set_globattr.institution(onc, institution_str='Climate impact portal (http://climate4impact.eu)')
    set_globattr.history2(onc, slice_mode, indice_name, time_range)
    onc.setncattr('source', '')
    onc.setncattr('Conventions','CF-1.6')
    
    
    # set variable attributes
    if indice_type == 'simple_time_aggregation' or indice_type == 'multiperiod':    
        eval('set_longname_units.' + indice_name + '_setvarattr(ind, var_longname, var_units)')
        ind.setncattr('standard_name', var_standardname)
    else:
        if threshold == None:
            eval('set_longname_units.' + indice_name + '_setvarattr(ind)')
            ind.setncattr('standard_name', 'ECA_indice')         
        else:
            eval('set_longname_units_custom_indices.' + indice_name + '_setvarattr(ind, threshold)')
            ind.setncattr('standard_name', 'ECA_indice with user defined threshold')
            
            if nb_user_thresholds > 1:
                eval('set_longname_units_custom_indices.' + indice_name + '_setthresholdattr(thresholdvar)')
        
    # for all:
    ind.missing_value = fill_val
    
        
    util_nc.set_time_values(onc, dt_centroid_arr, calend, units)
    util_nc.set_timebnds_values(onc, dt_bounds_arr, calend, units)
    
    onc.close()

    
    return out_file





def get_subset_percentile_dict(percentile_dict):
    subsetted_percentile_dict = OrderedDict()
    # we subset each 2D array and write in new dictionary
    for key in percentile_dict.keys():
        subsetted_percentile_dict[key] = percentile_dict[key][i1_row_current_tile:i2_row_current_tile, i1_col_current_tile:i2_col_current_tile]
    
    return subsetted_percentile_dict




def get_indice_from_dict_temporal_slices(indice_name, dict_temporal_slices, percentile_dict=None, dict_temporal_slices2=None, percentile_dict2=None, thresh=None, chunking=False, callback=None, callback_percentage_start_value=0, callback_percentage_total=100):
    
    indice_type = get_key_by_value_from_dict(map_indice_type, indice_name)
    
    
    if callback != None:    
        global percentage_current_key
        
        if thresh == None and chunking == False:
            percentage_key = (callback_percentage_total*1.0)/(len(dict_temporal_slices))
        elif thresh != None and chunking == False:
            percentage_key = (callback_percentage_total*1.0)/(len(dict_temporal_slices)*nb_user_thresholds)
        elif thresh == None and chunking == True:
            percentage_key = (callback_percentage_total*1.0)/(len(dict_temporal_slices)*nb_chunks)
        elif thresh != None and chunking == True:
            percentage_key = (callback_percentage_total*1.0)/(len(dict_temporal_slices)*nb_user_thresholds*nb_chunks)
    
    dt_centroid_arr = numpy.array([])
    dt_bounds_arr = numpy.array([])
    
    key_counter = 0
    for key in dict_temporal_slices.keys(): # key = temporal_slice_mode      
        
        dt_centroid_key = dict_temporal_slices[key][0]
        dt_bounds_key = dict_temporal_slices[key][1]

        #dt_arr_key = dict_temporal_slices[key][2]

        values_arr_key = dict_temporal_slices[key][3]

        if indice_type == 'multivariable' or indice_type == 'percentile_based_multivariable' or indice_type == 'multiperiod':
            values_arr_key2 = dict_temporal_slices2[key][3]
        
        # indice computing for current key
        
        if indice_type == 'simple' or indice_type == 'simple_time_aggregation':        
            if nb_user_thresholds == 0:
                indice_key = eval(indice_name + '_calculation(values_arr_key, fill_val)')
            else:
                indice_key = eval(indice_name + '_calculation(values_arr_key, fill_val, threshold=thresh)')
        
        elif indice_type == 'multivariable' or indice_type == 'multiperiod':
            indice_key = eval(indice_name + '_calculation(values_arr_key, values_arr_key2, fill_val, fill_val2)')
            
        elif indice_type == 'percentile_based':
            dt_arr_key = dict_temporal_slices[key][2]
            indice_key = eval(indice_name + '_calculation(values_arr_key, dt_arr_key, percentile_dict, fill_val)')
            
        elif indice_type == 'percentile_based_multivariable':
            dt_arr_key = dict_temporal_slices[key][2]
            indice_key = eval(indice_name + '_calculation(values_arr_key, percentile_dict, values_arr_key2, percentile_dict2, dt_arr_key, fill_val, fill_val2)')
        
        #############
        
        
        indice_key = indice_key.reshape(-1, indice_key.shape[0], indice_key.shape[1]) # 2D --> 3D
        
        if indice_type == 'simple_time_aggregation':
            if key_counter == 0:
                indice_arr = indice_key
            else:
                indice_arr += indice_key
        else:
            if key_counter == 0:
                indice_arr = indice_key
            else:
                indice_arr = numpy.concatenate((indice_arr, indice_key), axis=0)
       
        dt_centroid_arr = numpy.append(dt_centroid_arr, dt_centroid_key) # 1D
        dt_bounds_arr = numpy.concatenate((dt_bounds_arr, dt_bounds_key)) # 1D
        
        if callback != None:
            percentage_current_key = percentage_current_key + percentage_key
            callback(percentage_current_key)
            
        key_counter += 1

    if indice_type == 'simple_time_aggregation' :
        indice_arr = indice_arr / key_counter
        dt_centroid_arr = numpy.asarray([dt_centroid_arr[key_counter/2]])
        dt_bounds_arr = numpy.asarray([dt_bounds_arr[0],dt_bounds_arr[key_counter*2-1]])

    dt_bounds_arr = dt_bounds_arr.reshape(-1,2) # 1D --> 2D   

    return (dt_centroid_arr, dt_bounds_arr, indice_arr)






def get_percentile_dict(in_files, var_name, percentile, window_width=5, time_range=None, only_leap_years=False, save_to_file=None, transfer_limit_Mbytes=None, callback=None,
                        callback_percentage_start_value=0, callback_percentage_total=100, precipitation=False, N_lev=None):
    '''
    :param in_files: Absolute path(s) to NetCDF dataset(s) (including OPeNDAP URLs).
    :type in_files: list of str
    
    :param var_name: Target variable name to process.
    :type var_name: str
    
    :param percentile: Percentile value to compute which must be between 0 and 100 inclusive.
    :type percentile: int
    
    :param window_width: Window width, must be odd (default: 5).
    :type window_width: int
    
    :param time_range: Temporal range of the base period. If ``None``: whole period of input files will be processed.
    :type time_range: [datetime.datetime, datetime.datetime]
    
    :param only_leap_years: Option for February 29th (default: False).
    :type only_leap_years: bool
    
    :param save_to_file: Output file name which will contain the created daily percentiles dictionary.
    :type save_to_file: str
    
    :param transfer_limit_Mbytes: Maximum OPeNDAP/THREDDS request limit in Mbytes in case of OPeNDAP datasets.
    :type transfer_limit_Mbytes: float
    
    :param callback: Progress bar printing. If ``None``, progress bar will not be printed.  
    :type callback: :func:`callback.defaultCallback`

    :param callback_percentage_start_value: Initial value of percentage of the progress bar (default: 0).
    :type callback_percentage_start_value: int

    :param callback_percentage_total: Total persentage value (default: 100).
    :type callback_percentage_total: int
    
    :param precipitation: Parameter to inticate if the variable to process is precipitation (`True`) or not (`False`) to process data differently (default: False). 
    :type precipitation: bool
    
    :param N_lev: Level number if 4D variable.
    :type N_lev: int
    
    :rtype: dict
    
    
    .. warning:: Precipitation input units are considered to be in [kg m-2 s-1].
    '''
    
    temporal_variable = 'time'
    
    in_files.sort()
    
    nc0 = Dataset(in_files[0], 'r')
    fill_val = util_nc.get_att_value(nc0, var_name, '_FillValue')
    
    var_time =  nc0.variables[temporal_variable]
    
    #global calend, units
    try:
       calend = var_time.calendar
    except:
        calend = 'gregorian'
        
    units = var_time.units
    
    del var_time
    

    if time_range == None:
        time_range = util_dt.get_time_range(in_files, temporal_var_name=temporal_variable)
        
    else: # i.e. time_range is selected by user
        # we adjust datetime.datetime objects from time_range 
        t_arr = nc0.variables[temporal_variable][:]
        dt = util_dt.num2date(t_arr[0], calend, units)
        del t_arr
        time_range = util_dt.adjust_time_range(time_range, dt)

    
    nc0.close()
    
    
    dim_name = util_nc.check_unlimited(in_files[0])
    nc = MFDataset(in_files, 'r', aggdim=dim_name)
    var_time = nc.variables[temporal_variable]
    var = nc.variables[var_name]
    
    
    if transfer_limit_Mbytes == None: # i.e. we work with local files
        
        arrs = util_nc.get_values_arr_and_dt_arr(ncVar_temporal=var_time, ncVar_values=var, time_range=time_range, N_lev=N_lev, scale_factor=var_scale, add_offset=var_add)
        dt_base_arr = arrs[0]
        values_base_arr = arrs[1]

        if not isinstance(dt_base_arr[0], datetime):
            dt_base_arr = numpy.array([datetime(year = dt.year, month = dt.month, day = dt.day, hour = dt.hour) for dt in dt_base_arr])
        
        dic = percentile_dict.get_percentile_dict(values_base_arr, dt_base_arr, percentile=percentile, window_width=window_width, only_leap_years=only_leap_years, callback=callback,
                                                  callback_percentage_start_value = callback_percentage_start_value, callback_percentage_total = callback_percentage_total, precipitation=precipitation, fill_val=fill_val)
        
        del values_base_arr, dt_base_arr, arrs
        
        if save_to_file != None:
            with open(save_to_file, 'wb') as handle:
                pickle.dump(dic, handle)
                print "The dictionary with daily percentiles is saved in the file: " + os.path.abspath(save_to_file)
    
    
    
    else: # i.e. we work with OPeNDAP datasets
        transfer_limit_bytes = transfer_limit_Mbytes * 1024 * 1024
        total_array_size_bytes_and_tile_dimension = arr_size.get_total_array_size_bytes_and_tile_dimension(in_files, var_name, transfer_limit_bytes, time_range=time_range)
        array_total_size = total_array_size_bytes_and_tile_dimension[0]
        
        #print array_total_size
        
        if array_total_size < transfer_limit_bytes: # the same as for the "if transfer_limit_bytes == None" case

            print "Data transfer... "
            
            arrs = util_nc.get_values_arr_and_dt_arr(ncVar_temporal=var_time, ncVar_values=var, time_range=time_range, N_lev=N_lev, scale_factor=var_scale, add_offset=var_add)
            dt_base_arr = arrs[0]
            values_base_arr = arrs[1]

            dic = percentile_dict.get_percentile_dict(values_base_arr, dt_base_arr, percentile=percentile, window_width=window_width, only_leap_years=only_leap_years, callback=callback,
                                                      callback_percentage_start_value = callback_percentage_start_value, callback_percentage_total = callback_percentage_total, precipitation=precipitation, fill_val=fill_val)

            del values_base_arr, dt_base_arr, arrs
            
            if save_to_file != None:
                with open(save_to_file, 'wb') as handle:
                    pickle.dump(dic, handle)
                    print "The dictionary with daily percentiles is saved in the file: " + os.path.abspath(save_to_file)
        

            
        else:
            # then we do chunking in space
            tile_dimension = total_array_size_bytes_and_tile_dimension[1]
            #print tile_dimension
            
            var_shape = var.shape
            var_shap1 = var_shape[1]
            var_shap2 = var_shape[2]

            tile_map = OCGIS_tile.get_tile_schema(nrow=var_shap1, ncol=var_shap2, tdim=tile_dimension, origin=0)
            #global nb_chunks
            nb_chunks = len(tile_map)
            print str(nb_chunks) + " data chunks will be transfered."
            
            
            time_arr = var_time[:]
            dt_arr = numpy.array([util_dt.num2date(dt, calend=calend, units=units) for dt in time_arr])
            assert(dt_arr.ndim == 1)
            indices_base_period = util_dt.get_indices_subset(dt_arr, time_range)
            dt_base_arr = dt_arr[indices_base_period]
            del time_arr, dt_arr, indices_base_period
            ############## we initialize a glob dict ( i.e. a dict with all calend days (keys) and 2D arrays with zeros)
            ############# where we will add perc. values of each chunk
            dic_caldays = percentile_dict.get_dict_caldays(dt_base_arr)
            
            glob_percentile_dict = OrderedDict()
            for month in dic_caldays.keys():
                for day in dic_caldays[month]:
                    glob_percentile_dict[month,day] = numpy.zeros((var_shap1, var_shap2))
            
            percentage_per_chunk = callback_percentage_total/(nb_chunks*1.0)
            
            chunk_counter = 1  # chunk counter
           
            for tile_id in tile_map:
                print "Data transfer: chunk " + str(int(chunk_counter)) + '/'+ str(len(tile_map)) + " ..."
                
                global i1_row_current_tile, i2_row_current_tile, i1_col_current_tile, i2_col_current_tile
                
                i1_row_current_tile = tile_map.get(tile_id).get('row')[0]
                i2_row_current_tile = tile_map.get(tile_id).get('row')[1]
                
                i1_col_current_tile = tile_map.get(tile_id).get('col')[0]
                i2_col_current_tile = tile_map.get(tile_id).get('col')[1]
                
                arrs_current_chunk = util_nc.get_values_arr_and_dt_arr(ncVar_temporal=var_time, ncVar_values=var, time_range=time_range, N_lev=N_lev, spatial_chunking=True, scale_factor=var_scale, add_offset=var_add,
                                                                       i1_row_current_tile=i1_row_current_tile,
                                                                       i2_row_current_tile=i2_row_current_tile,
                                                                       i1_col_current_tile=i1_col_current_tile,
                                                                       i2_col_current_tile=i2_col_current_tile)
                values_base_arr_current_chunk = arrs_current_chunk[1]
                dt_base_arr = arrs_current_chunk[0] # alwayse the same for each chunk
                
                dic_current_chunk = percentile_dict.get_percentile_dict(values_base_arr_current_chunk, dt_base_arr, percentile=percentile, window_width=window_width, only_leap_years=only_leap_years,
                                                                        callback=callback, callback_percentage_start_value = callback_percentage_start_value, callback_percentage_total=percentage_per_chunk, chunk_counter=chunk_counter,
                                                                        precipitation=precipitation, fill_val=fill_val)
                
                del arrs_current_chunk, values_base_arr_current_chunk, dt_base_arr
                

                ########### we fill our glob_percentile_dict (chunk by chunk)
                for month in dic_caldays.keys():
                    for day in dic_caldays[month]:
                        glob_percentile_dict[month,day][i1_row_current_tile:i2_row_current_tile, i1_col_current_tile:i2_col_current_tile] = dic_current_chunk[month,day]

                chunk_counter += 1
                
                
                               
            
            dic = glob_percentile_dict
            
            if save_to_file != None:
                with open(save_to_file, 'wb') as handle:
                    pickle.dump(dic, handle)
                    print "The dictionary with daily percentiles is saved in the file: " + os.path.abspath(save_to_file)
            
    nc.close()        
            
    return dic
