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
import maps
# import xyz

import sys


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
            callback_percentage_start_value=0,  # ?
            callback_percentage_total=100,      # ?
           #time_range2=None,
            base_period_time_range=None,
            window_width=5,
            only_leap_years=False,
            ignore_Feb29th=True,
            interpolation='hyndman_fan', 
            save_percentiles_to_file=None, # [file_name, option], option: 'a', 'b'
            out_unit='days',
            ):

    
    '''

    
    :param indice_name: Climate indice name. 
    :type indice_name: str    
    
    :param in_files: Absolute path(s) to NetCDF dataset(s) (including OPeNDAP URLs).
    :type in_files: str OR list of str OR list of lists

    :param var_name: Target variable name to process corresponding to ``in_files``.
    :type var_name: str OR list of str
         
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
    
    :param save_percentiles_to_file: To save percentile thresholds as a file.
    :type save_percentiles_to_file: list of str 
    
    :param out_unit: Output unit for certain indices: "days" or "%" (default: "days").
    :type out_unit: str
    
    :rtype: path to NetCDF file

    .. warning:: If ``out_file`` already exists, Icclim will overwrite it!
    
    .. warning:: Precipitation input units are considered to be in [kg m-2 s-1]. i.e. in [mm/s].
    '''
    
    #####    we define the type of selected indice
    #####    (simple_time_aggregation and multiperiod are statistics and not indices, so threshold is ignored in those cases)
    indice_type = get_key_by_value_from_dict(maps.map_indice_type, indice_name) # 'simple'/'multivariable'/'multiperiod'/'simple_time_aggregation'/'percentile_based'/'percentile_based_multivariable'
    
    if (indice_type=='percentile_based' or indice_type=='percentile_based_multivariable') and base_period_time_range==None:
        raise IOError('Time range of base period is required for percentile-based indices! Please, set the "base_period_time_range" parameter.')
    
    #####    slice_mode
    if slice_mode == None:
        slice_mode = 'month'

    
    #####    input files and target variable names 
    if type(var_name) is not list:  # single variable        
        var_name = [var_name] 
        if  type(in_files) is not list: # single file
            in_files = [in_files]   
    else:                           # multivariable
        if type(in_files) is not list:
            raise IOError('"In_files" must be a list')
        else:
            assert (len(in_files) == len(var_name)) 
     
    
    
    #####    VARS_in_files: dictionary where to each target variable (key of the dictionary) correspond input files list
    VARS_in_files = OrderedDict()
    for i in range(len(var_name)):        
        if len(var_name)==1:
            VARS_in_files[var_name[i]] = in_files
        else:
            if type(in_files[i]) is not list:  
                in_files[i] = [in_files[i]]                
            VARS_in_files[var_name[i]] = in_files[i]
    

    #####    callback
    if callback != None:
        global percentage_current_key        
        percentage_current_key = callback_percentage_start_value
    
    #####    we check if output path exists
    out_path = os.path.dirname(os.path.abspath(out_file)) + os.sep
    if os.path.isdir(out_path) == False:
        raise IOError('Output directory does not exists.')
                     
    #####    we prepare output file
    onc = Dataset(out_file, 'w' ,format="NETCDF3_CLASSIC")
    
    #####    we define type of result indice
    ind_type = 'f' # 'float32'
    
    
    ########################################
    ################# META: begin
    ########################################
    any_in_file = VARS_in_files[var_name[0]][0] # we take any input file (for example the first one of the first one of the target variables)
   
    inc = Dataset(any_in_file, 'r')
    indice_dim = util_nc.copy_var_dim(inc, onc, var_name[0]) # tuple ('time', 'lat', 'lon')    
    indice_dim = list(indice_dim)
    ncVar = inc.variables[var_name[0]] 
    fill_val = ncVar._FillValue.astype('float32') # fill_value must be the same type as "ind_type", i.e. 'float32'
    dimensions_list_var = ncVar.dimensions
    index_time = 0
    ncVar_time = inc.variables[dimensions_list_var[index_time]]
    
    ############## in case of user defined thresholds 
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
    ##############
    
    
    #####    we create a variable in output dataset (onc)
    if indice_type == 'simple_time_aggregation' or indice_type == 'multiperiod':
        var_longname = getattr(ncVar,'long_name')
        var_standardname = getattr(ncVar,'standard_name')                              
        ind = onc.createVariable(var_name[0], ind_type, indice_dim, fill_value = fill_val) 
    else:                
        ind = onc.createVariable(indice_name, ind_type, indice_dim, fill_value = fill_val)

    #####    we copy attributes from variable to process to indice variable, except scale_factor and _FillValue
    util_nc.copy_var_attrs(ncVar, ind)

    
#     #####    we check for "time_range"
#     try:
#         calend = ncVar_time.calendar
#     except:
#         calend = 'gregorian'
#     
#     units = ncVar_time.units
# 
#     
#     if time_range == None:
#         time_range = util_dt.get_time_range(VARS_in_files[var_name[0]], temporal_var_name=indice_dim[0])
#         
#     else: # i.e. time_range is selected by user
#         # we adjust datetime.datetime objects from time_range 
#         t_arr = inc.variables[indice_dim[0]][:]
#         dt = util_dt.num2date(t_arr[0], calend, units)
#         time_range = util_dt.adjust_time_range(time_range, dt)
    
    
    time_range = util_dt.get_time_range(files=VARS_in_files[var_name[0]], time_range=time_range, temporal_var_name=indice_dim[0])
# 
#     if indice_type == 'multiperiod':            
#         time_range2 = util_dt.get_time_range(files=VARS_in_files[var_name[1]], time_range=time_range2, temporal_var_name=indice_dim[0])

    
    # we get nb_rows (var_shape1) and nb_cols (var_shape2) to compute in the following optimal tile_dimension 
    var_shape = ncVar.shape
    var_shape1 = var_shape[-2]
    var_shape2 = var_shape[-1]

    inc.close()
    ########################################
    ################# META: end
    ########################################
    
    
    
    # the dictionary to keep all necessary information about each target variable
    VARS = OrderedDict()
    


    
# # # # #     if indice_type == "percentile_based" or indice_type == "percentile_based_multivariable": 
# # # # #         intersecting_years = util_dt.get_intersecting_years(time_range1=time_range, time_range2=base_period_time_range)
# # # # #         VARS_base = OrderedDict()
# # # # #     else:
# # # # #         VARS_base=None
    
    
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
#                                     'threshold': OrderedDict(),                                    
                                })
        
        
        
        VARS[v] = current_var_dict        
        
        dict_files_years_to_process = files_order.get_dict_files_years_to_process_in_correct_order(files_list=VARS_in_files[v], time_range=time_range)  
        
        VARS[v]['files_years'] = dict_files_years_to_process 

        dim_name = util_nc.check_unlimited(VARS_in_files[v][0])
        tile_dimension = arr_size.get_tile_dimension(in_files=dict_files_years_to_process.keys(), 
                                             var_name=v, 
                                             transfer_limit_Mbytes=transfer_limit_Mbytes, 
                                             time_range=time_range)

        vars_tile_dimension.append(tile_dimension)

    tile_dimension = min(vars_tile_dimension)

    
# #### REMOVE ??? proverit' v drugom meste            
#     # we check if dt_arr of all variables are equal!!
#     if len(var_name)>1:
#         for i in range(len(var_name)-1):                                       
#             if not numpy.array_equal( VARS[var_name[i]]['arrs'][0], VARS[var_name[i+1]]['arrs'][0] ):
#                 print 'Error: Time step vectors must be equal for all variables!'
#                 sys.exit()
# #             if indice_type == 'multiperiod': only len(dt_arr) must be equal



     
    global nb_chunks
#     global i1_row_current_tile, i2_row_current_tile, i1_col_current_tile, i2_col_current_tile
    
    # chunk tiles    
    tile_map = OCGIS_tile.get_tile_schema(nrow=var_shape1, ncol=var_shape2, tdim=tile_dimension, origin=0)
        
    nb_chunks = len(tile_map)

    global chunk_counter
    chunk_counter = 0
    #####    for each chunk
    for tile_id in tile_map:
        
        if len(tile_map)>1:
            print "Loading data: chunk " + str(int(chunk_counter+1)) + '/'+ str(len(tile_map)) + " ..."
        else:
            print "Loading data..."
        
        #####    for each target variable
        for v in var_name:
            
            if chunk_counter == 0:

                inc = Dataset(VARS[v]['files_years'].keys()[0], 'r')     
                ncVar = inc.variables[v]    
                dimensions_list_current_var = ncVar.dimensions
            
 
                fill_val = ncVar._FillValue.astype('float32') # fill value (_FillValue) must be the same type as data type: float32 (ind_type = 'f', i.e. float32)
                VARS[v]['fill_value']=fill_val
    
                #global calend, units
                
                ncVar_time = inc.variables[dimensions_list_current_var[index_time]]
             
                try:
                    calend = ncVar_time.calendar
                except:
                    calend = 'gregorian'
                 
                units = ncVar_time.units
                
                VARS[v]['time_calendar']=calend
                VARS[v]['time_units']=units
#                 current_var_dict['meta'].append(calend)
#                 current_var_dict['meta'].append(units)
                
               
               
                var_units = getattr(inc.variables[v],'units')

                # Units conversion
                var_add = 0.0
                var_scale = 1.0
                if var_units == 'degC' or var_units == 'Celcius': #Kelvin
                    var_add = var_add + 273.15
                elif var_units == 'mm': # kg m-2 s-1 (mm/s)
                    var_scale = var_scale / 86400.0
                    
                VARS[v]['unit_conversion_var_add']=var_add
                VARS[v]['unit_conversion_var_scale']=var_scale
#                 current_var_dict['unit_conversion'].append(var_add)    
#                 current_var_dict['unit_conversion'].append(var_scale)
                
#                 VARS[v]=current_var_dict
        

            nc = MFDataset(VARS[v]['files_years'].keys(), 'r', aggdim=dim_name) # VARS[v]['files_years'].keys(): files of current variable
            var_time = nc.variables[indice_dim[0]]
            var = nc.variables[v]

            i1_row_current_tile = tile_map.get(tile_id).get('row')[0]
            i2_row_current_tile = tile_map.get(tile_id).get('row')[1]
            
            i1_col_current_tile = tile_map.get(tile_id).get('col')[0]
            i2_col_current_tile = tile_map.get(tile_id).get('col')[1]  
                        

            arrs_current_chunk = util_nc.get_values_arr_and_dt_arr(ncVar_temporal=var_time, ncVar_values=var, 
                                                                     fill_val=VARS[v]['fill_value'], 
                                                                     time_range=time_range, 
                                                                     N_lev=N_lev, 
                                                                     scale_factor=VARS[v]['unit_conversion_var_scale'], 
                                                                     add_offset=VARS[v]['unit_conversion_var_add'],
                                                                     ignore_Feb29th=ignore_Feb29th, 
                                                                     i1_row_current_tile=i1_row_current_tile,
                                                                     i2_row_current_tile=i2_row_current_tile,
                                                                     i1_col_current_tile=i1_col_current_tile,
                                                                     i2_col_current_tile=i2_col_current_tile)

            VARS[v]['dt_arr']=arrs_current_chunk[0]
            VARS[v]['values_arr']=arrs_current_chunk[1] 

            if indice_type == "percentile_based" or indice_type == "percentile_based_multivariable":

                arrs_base_current_chunk = util_nc.get_values_arr_and_dt_arr(ncVar_temporal=var_time, ncVar_values=var, 
                                                                            fill_val=VARS[v]['fill_value'], 
                                                                            time_range=base_period_time_range, 
                                                                              N_lev=N_lev, 
                                                                              scale_factor=VARS[v]['unit_conversion_var_scale'], 
                                                                              add_offset=VARS[v]['unit_conversion_var_add'],
                                                                              ignore_Feb29th=ignore_Feb29th,
                                                                              i1_row_current_tile=i1_row_current_tile,
                                                                             i2_row_current_tile=i2_row_current_tile,
                                                                             i1_col_current_tile=i1_col_current_tile,
                                                                             i2_col_current_tile=i2_col_current_tile)
                                                        
#                 dt_arr_base = arrs_base_current_chunk[0]    
#                 values_arr_base = arrs_base_current_chunk[1]

            
                VARS[v]['base']['dt_arr']=arrs_base_current_chunk[0]
                VARS[v]['base']['values_arr']=arrs_base_current_chunk[1]

        
            
###### REMOVE ??? proverit' v drugom meste            
#     # we check if dt_arr of all variables are equal!!
#     if len(var_name)>1:
#         for i in range(len(var_name)-1):                                       
#             if not numpy.array_equal( VARS[var_name[i]]['arrs'][0], VARS[var_name[i+1]]['arrs'][0] ):
#                 print 'Error: Time step vectors must be equal for all variables!'
#                 sys.exit()
# #             if indice_type == 'multiperiod': only len(dt_arr) must be equal
            
            
            
            
            dict_temporal_slices = time_subset.get_dict_temporal_slices(dt_arr=VARS[v]['dt_arr'], 
                                                                        values_arr=VARS[v]['values_arr'],
                                                                        fill_value=VARS[v]['fill_value'],                                                                      
                                                                        calend=VARS[v]['time_calendar'], 
                                                                        temporal_subset_mode=slice_mode, 
                                                                        time_range=time_range)
            
            
            VARS[v]['temporal_slices']=dict_temporal_slices

            nc.close()

        
        
        
        if nb_user_thresholds == 0:
            
            if chunk_counter == 0:
                if indice_type == 'simple_time_aggregation':
                    indice_arr = numpy.zeros( (1,var_shape1, var_shape2), dtype=ind_type )
                else:
                    indice_arr = numpy.zeros( (len(dict_temporal_slices),var_shape1, var_shape2), dtype=ind_type )
    
            
            
            
            ######################################
            ###################################### VARS_dict_temporal_slices, VARS_base ----> to one parameter "VARS"
            indice_tuple_current_chunk = get_indice_from_dict_temporal_slices(indice_name=indice_name,
#                                                         VARS_dict_temporal_slices=VARS_temporal_slices,
#                                                         VARS_base=VARS_base,
                                                        vars_dict=VARS,
                                                        window_width=window_width,
                                                        only_leap_years=only_leap_years,
                                                        callback=callback, callback_percentage_total=callback_percentage_total,
                                                        ignore_Feb29th=ignore_Feb29th, interpolation=interpolation,
                                                        percentiles_to_file=save_percentiles_to_file,
                                                        out_unit=out_unit) ## tuple: (dt_centroid_arr, dt_bounds_arr, indice_arr) 
    
            indice_arr_current_chunk = indice_tuple_current_chunk[2]
            
            
            if indice_type == 'simple_time_aggregation':
                indice_arr[:, i1_row_current_tile:i2_row_current_tile, i1_col_current_tile:i2_col_current_tile] += indice_arr_current_chunk
            else:
                # we concatenate
                indice_arr[:, i1_row_current_tile:i2_row_current_tile, i1_col_current_tile:i2_col_current_tile] = indice_arr_current_chunk
                     
            
            
        
        else:
            
            dict_threshold_indice_arr = OrderedDict()
            for t in user_thresholds:                    
                if chunk_counter == 0:              
                    dict_threshold_indice_arr[t] = numpy.zeros( (len(dict_temporal_slices),var_shape1, var_shape2), dtype=ind_type )
            
                
                indice_tuple_current_chunk = get_indice_from_dict_temporal_slices(indice_name=indice_name,
#                                                                     VARS_dict_temporal_slices=VARS_temporal_slices,
                                                                    vars_dict=VARS,
                                                                    thresh=t,
                                                                    callback=callback, callback_percentage_total=callback_percentage_total)  ## tuple: (dt_centroid_arr, dt_bounds_arr, indice_arr)         
                
                
                indice_arr_current_chunk = indice_tuple_current_chunk[2]
                # we concatenate
                dict_threshold_indice_arr[t][:, i1_row_current_tile:i2_row_current_tile, i1_col_current_tile:i2_col_current_tile] = indice_arr_current_chunk
    
        
        if chunk_counter == 0:
                dt_centroid_arr = indice_tuple_current_chunk[0]
                dt_bounds_arr = indice_tuple_current_chunk[1]
        
        
        
        

            
        chunk_counter +=1

            
            

            
    

    
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





# def get_subset_percentile_dict(percentile_dict):
#     subsetted_percentile_dict = OrderedDict()
#     # we subset each 2D array and write in new dictionary
#     for key in percentile_dict.keys():
#         subsetted_percentile_dict[key] = percentile_dict[key][i1_row_current_tile:i2_row_current_tile, i1_col_current_tile:i2_col_current_tile]
#     
#     return subsetted_percentile_dict





##################################################################
##################################################################

def get_indice_from_dict_temporal_slices(indice_name, 
                                         vars_dict,
#                                          VARS_dict_temporal_slices, 
#                                          VARS_base=None, 
                                         thresh=None,
                                          window_width=None, only_leap_years=None, 
#                                           chunking=False, 
                                          callback=None, callback_percentage_start_value=0, callback_percentage_total=100,
                                          ignore_Feb29th=False, interpolation="hyndman_fan", 
                                          percentiles_to_file=None,
                                          out_unit="days"):
      
  
      
    indice_type = get_key_by_value_from_dict(maps.map_indice_type, indice_name)
         
    d = vars_dict[vars_dict.keys()[0]]['temporal_slices'] # d is any temporal slices dictionary, for ex. the first one
    t_slices = d.keys() # list of temporal slices: [(1980,'year'), (1981, 'year'), (1982, 'year'), ...]
      
      
    if indice_type == "percentile_based" or indice_type == 'percentile_based_multivariable':
        
        dt_arr_base = vars_dict[vars_dict.keys()[0]]['base']['dt_arr']
        years_base =  util_dt.get_year_list(dt_arr_base)
        years_study = [i[1] for i in t_slices]
        years_study = list(set(years_study)) # we remove duplicate years
        intersecting_years = list( set(years_base).intersection(years_study) )
      
    if callback != None:    
        global percentage_current_key
        
        #nb_vars = len(vars_dict)
        nb_t_slices = len(t_slices)
        
        if thresh == None:
            percentage_key = (callback_percentage_total*1.0)/(nb_t_slices*nb_chunks)
        elif thresh != None:
            percentage_key = (callback_percentage_total*1.0)/(nb_t_slices*nb_user_thresholds*nb_chunks)


      
      
    dt_centroid_arr = numpy.array([])
    dt_bounds_arr = numpy.array([])
      
    key_counter = 0
      
    cnt = 0
    
    vars_percentiles = OrderedDict()
    percentiles_calc_method = OrderedDict()

    
    
    arr_shape = d[d.keys()[0]][3].shape 
    nb_rows = arr_shape[-2]
    nb_columns = arr_shape[-1]  
    
    
    if percentiles_to_file != None:
        file_path = percentiles_to_file[0]
        opt = percentiles_to_file[1] # 'all', 'only_without_bootstrapping'
        
        BIG_PD = OrderedDict()
        BIG_PD['param_ignore_Feb29th']=ignore_Feb29th
        BIG_PD['param_only_leap_years']=only_leap_years
        BIG_PD['param_interpolation']=interpolation
        BIG_PD['param_window_width']=window_width
        
        if opt == 'b': 
            sub_BIG_PD_inb = OrderedDict()
            
            
    for key in t_slices: # key = temporal_slice_mode
          
        
          
        dt_centroid_key = d[key][0]
        dt_bounds_key = d[key][1]
  

          
        # indice computing for current key
        if indice_type == 'simple' or indice_type == 'simple_time_aggregation':   
              
            # one variable --> we have only one key in the dictionary
            values_arr_key = d[key][3]                        
            fill_val = d[key][4]
              
            if nb_user_thresholds == 0:
                indice_key = eval(indice_name + '_calculation(values_arr_key, fill_val)')
#                 indice_key = zzz(indice_name, arr=values_arr_key, fill_val=fill_val)
                
            else:
                indice_key = eval(indice_name + '_calculation(values_arr_key, fill_val, threshold=thresh)')
          
        elif indice_type == 'multivariable' or indice_type == 'multiperiod':

            ############ TODO: 'tasmin' and 'tasmax' to generic names
            values_arr_tasmax_key = vars_dict['tasmax']['temporal_slices'][key][3]
            values_arr_tasmin_key = vars_dict['tasmin']['temporal_slices'][key][3]

            
            fill_val = vars_dict['tasmax']['temporal_slices'][key][4]
            fill_val2 = vars_dict['tasmin']['temporal_slices'][key][4]


            indice_key = eval(indice_name + '_calculation(values_arr_tasmax_key, values_arr_tasmin_key, fill_val, fill_val2)')
#             indice_key = zzz(indice_name, arr1=values_arr_tasmax_key, arr2=values_arr_tasmin_key, fill_val1=fill_val, fill_val2=fill_val2)
              
          
        elif indice_type == 'percentile_based' or indice_type == 'percentile_based_multivariable': 
            
            if indice_name in ['R75p', 'R95p', 'R99p','R75pTOT','R95pTOT','R99pTOT']:
                for v in vars_dict.keys():
                    fill_val = vars_dict[v]['temporal_slices'][key][4]
                    
                    percentiles_arr = percentile_dict.get_percentile_arr(arr=vars_dict[v]['base']['values_arr'], 
                                                                     percentile=maps.map_indice_percentile_value[indice_name][0], 
                                                                     window_width=window_width,                                                                      
                                                                     callback=None, 
                                                                     callback_percentage_start_value=0, 
                                                                    callback_percentage_total=100, 
                                                                    chunk_counter=1, 
                                                                    precipitation=True, 
                                                                    fill_val=fill_val,                                                                     
                                                                    interpolation=interpolation)
                    
                    
                    
                    values_arr_key = vars_dict[v]['temporal_slices'][key][3]
                    current_intersecting_year = -9999
                    
                    
                indice_key = eval(indice_name + '_calculation(values_arr_key, percentiles_arr, fill_val, out_unit=out_unit)')
                
                
            
            else:
              
                if key[1] not in intersecting_years: # key[1] --> year  
                    current_intersecting_year = -9999
                    reduced_base_years_list = [-9999]
                    cnt += 1
                else:
                    current_intersecting_year = key[1]
                    reduced_base_years_list = years_base[:]
                    reduced_base_years_list.remove(current_intersecting_year)
    
    
                
                indice_arr_y = numpy.zeros(( len(reduced_base_years_list), nb_rows, nb_columns))
    
                  
                i=0
                
                percentage_current_key1 = percentage_current_key
                
                for ytd in reduced_base_years_list:
                    
      
                    g=0
                    for v in vars_dict.keys():
                        vars_percentiles[v] = percentiles_calc_method
          
                        dt_arr_key = vars_dict[v]['temporal_slices'][key][2]
                        values_arr_key = vars_dict[v]['temporal_slices'][key][3]                        
                        fill_val = vars_dict[v]['temporal_slices'][key][4]
    
                          
    
      
                        new_arrs_base = time_subset.get_resampled_arrs(dt_arr=vars_dict[v]['base']['dt_arr'],
                                                                       values_arr=vars_dict[v]['base']['values_arr'],
                                                                       year_to_eliminate=current_intersecting_year, 
                                                                       year_to_duplicate=ytd)
                        
                        
                        
                        if percentiles_to_file != None and cnt==1:
                            sub_BIG_PD_v = OrderedDict()
                            BIG_PD[v] = sub_BIG_PD_v
                            
                            
                        # for not "in-base" years we compute pd ONLY one time (i.e. when cnt=1)
                        if current_intersecting_year != -9999 or cnt == 1:
    #                     if cnt == 1:  # REMOVE  
    #                         print "ZZZ"

                            pd = percentile_dict.get_percentile_dict(arr=new_arrs_base[1], 
                                                                            dt_arr=new_arrs_base[0], 
                                                                            percentile=maps.map_indice_percentile_value[indice_name][g], 
                                                                            window_width=window_width, 
                                                                            only_leap_years=only_leap_years, 
                                                                            callback=None, callback_percentage_start_value=0, callback_percentage_total=100, 
                                                                            chunk_counter=1, 
                                                                            #precipitation=maps.map_variable_precipitation[v],
                                                                            fill_val=fill_val,
                                                                            ignore_Feb29th=ignore_Feb29th,
                                                                            interpolation=interpolation)
                            
    
    
                              
                            if current_intersecting_year == -9999 and cnt==1:  
                                vars_percentiles[v]['without_bootstrapping'] = pd
                                
                                
                                
                                if percentiles_to_file != None:
                                    
                                    BIG_PD[v]['out_of_base']=pd
                                    
                                    if opt=='a':
                                        with open(file_path, 'wb') as handle:
                                            pickle.dump(BIG_PD, handle)
                                        print "The dictionary with daily percentiles is saved in the file: " + os.path.abspath(file_path)
                                
                          
                            else:
                                
                                vars_percentiles[v]['bootstrapping'] = pd
                                
                                if percentiles_to_file != None and opt=='b':
                                    
                                    BIG_PD[v]['in_base']=sub_BIG_PD_inb
                                    BIG_PD[v]['in_base'][current_intersecting_year, ytd]=pd
                        
    #                     # REMOVE            
    #                     if  current_intersecting_year != -9999:                                     
    #                         vars_percentiles[v]['bootstrapping'] = pd        
                                    
                        g+=1
                        
          
                    vars = vars_dict.keys()
                    p1 = vars_dict[vars[0]]['temporal_slices'][key][3]
    
    
                    p3 = vars_dict[vars[0]]['temporal_slices'][key][4]
                    
    
                    
                    
                    if current_intersecting_year != -9999:
                        p2 = vars_percentiles[vars[0]]['bootstrapping']
                        
                        if indice_type == 'percentile_based':
                            indice_arr_y[i,:,:] = eval(indice_name + '_calculation(p1, dt_arr_key, p2, fill_val=p3, out_unit=out_unit)') 
                        elif indice_type == 'percentile_based_multivariable':  
                            p4 = vars_dict[vars[1]]['temporal_slices'][key][3] 
                            p6 = vars_dict[vars[1]]['temporal_slices'][key][4]
                            p5 = vars_percentiles[vars[1]]['bootstrapping']
                            indice_arr_y[i,:,:] = eval(indice_name + '_calculation(p1, p2, p4, p5, dt_arr_key, fill_val1=p3, fill_val2=p6, out_unit=out_unit)')
                        
                        
                        if callback != None:
                            percentage_current_key_intersect_year = percentage_current_key1 + percentage_key/((len(intersecting_years)-1)*1.0)
                            callback(percentage_current_key_intersect_year)
                            percentage_current_key1 = percentage_current_key_intersect_year
                    else:
                        p2_ = vars_percentiles[vars[0]]['without_bootstrapping']
                        
                        if indice_type == 'percentile_based':
                            indice_arr_y[i,:,:] = eval(indice_name + '_calculation(p1, dt_arr_key, p2_, fill_val=p3, out_unit=out_unit)') 
                        elif indice_type == 'percentile_based_multivariable':  
                            p4 = vars_dict[vars[1]]['temporal_slices'][key][3] 
                            p6 = vars_dict[vars[1]]['temporal_slices'][key][4]
                            p5_ = vars_percentiles[vars[1]]['without_bootstrapping']
                            indice_arr_y[i,:,:] = eval(indice_name + '_calculation(p1, p2_, p4, p5_, dt_arr_key, fill_val1=p3, fill_val2=p6, out_unit=out_unit)')
    
                    
                          
                    i+=1
                  
                if  current_intersecting_year == -9999:  
                    indice_key = indice_arr_y
                    indice_key = indice_key.reshape(indice_key.shape[1], indice_key.shape[2]) # 3D --> 2D
                    
                else: 
                    #print  indice_arr_y[:,0,0]
                    indice_key = numpy.mean(indice_arr_y, axis=0)
                    #print '===='
    

    
#                 
#         elif indice_type == 'percentile_based_multivariable':
#             dt_arr_key = dict_temporal_slices[key][2]
#             indice_key = eval(indice_name + '_calculation(values_arr_key, percentile_dict, values_arr_key2, percentile_dict2, dt_arr_key, fill_val, fill_val2)')
#         
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
            if indice_type == 'percentile_based' or indice_type == 'percentile_based_multivariable':
                if  current_intersecting_year == -9999:
                    callback(percentage_current_key)
            
            else:
                callback(percentage_current_key)
              
        key_counter += 1
    
    
    if percentiles_to_file != None and opt=='b':
         
        with open(file_path, 'wb') as handle:
            pickle.dump(BIG_PD, handle)
            print "The dictionary with daily percentiles is saved in the file: " + os.path.abspath(file_path)
    
    
    
    if indice_type == 'simple_time_aggregation' :
        indice_arr = indice_arr / key_counter
        dt_centroid_arr = numpy.asarray([dt_centroid_arr[key_counter/2]])
        dt_bounds_arr = numpy.asarray([dt_bounds_arr[0],dt_bounds_arr[key_counter*2-1]])
  
    dt_bounds_arr = dt_bounds_arr.reshape(-1,2) # 1D --> 2D   
  
    return (dt_centroid_arr, dt_bounds_arr, indice_arr)
