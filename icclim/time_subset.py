# -*- coding: latin-1 -*-

#  Copyright CERFACS (http://cerfacs.fr/)
#  Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
#
#  Author: Natalia Tatarinova

"""
Types of temporal aggregations (slice_mode):
- 'month' (all months of year)
- 'year'
- 'DFJ'
- 'MAM'
- 'JJA'
- 'SON'
- 'ONDJFM'
- 'AMJJAS'
- user selected months
- user defined seasons
- None : whole selected period will be processed

Note: DJF 2000: December 2000 + January 2001 + February 2001

"""

import numpy 
from datetime import datetime
from collections import OrderedDict

import util.util_dt as util_dt

## This function creates a dictionary with centroid day and centroid month for each type of temporal aggregation
## except for slice_mode=None
def get_map_info_slice(slice_mode):
    map_slices={}
    map_slices[str(slice_mode)]={}
    
    
    if slice_mode=='year':
        months=None
        centroid_day=1
        centroid_month=7
        
    elif slice_mode=='month':
        months=range(1,13)
        centroid_day=16

    elif slice_mode=='DJF':
        months=([12], [1,2])

    elif slice_mode=='MAM':
        months=[3,4,5]

    elif slice_mode=='JJA':
        months=[6,7,8]

    elif slice_mode=='SON':
        months=[9,10,11]

    elif slice_mode=='ONDJFM':
        months=([10,11,12], [1,2,3])

    elif slice_mode=='AMJJAS':
        months=[4,5,6,7,8,9]

    
    elif type(slice_mode) is list:
        months=slice_mode[1]
        

    map_slices[str(slice_mode)]['months']=months
    

    if type(months) is list: # simple season like 'MAM' [3,4,5]
        months=months
    elif type(months) is tuple: # composed season like 'DJF' ([12], [1,2]) or 'ONDJFM' ([10,11,12], [1,2,3])
        months=months[0]+months[1]

    
    try:
        # centroid day
        if len(months) % 2 == 0 and slice_mode!='month':    # nb of months in season is even
            centroid_day=1
        else:                       # nb of months in season is odd 
            centroid_day=16


        # centroid month
        if slice_mode=='month' or slice_mode[0]=='month': #i.e. only for months
            centroid_month=None
    
        else:
            centroid_month=months[len(months)/2] 
    except:
        pass     
    
    map_slices[str(slice_mode)]['centroid_day']=centroid_day            
    map_slices[str(slice_mode)]['centroid_month']=centroid_month  
                
    return map_slices


            

def get_dict_temporal_slices(dt_arr, values_arr, fill_value, calend='gregorian', temporal_subset_mode=None, time_range=None):
    
    '''
    
    This function returns a dictionary with temporal slices.
    
    
    :param dt_arr: Datetime vector.
    :type dt_arr: numpy.ndarray (1D) of datetime.datetime objects
    
    :param values_arr: Corresponding to ``dt_arr`` array of values.
    :type values_arr: numpy.ndarray (3D) 
    
    :param temporal_subset_mode: Type of temporal aggregation: the same set of possible values as ``slice_mode``.
    :type temporal_subset_mode: str 
    
    :param time_range: Time range.
    :type time_range: [datetime.datetime, datetime.datetime]
    
    :rtype: dict, where key is (``temporal_subset_mode``, year) and values are grouped in a tuple with 5 elements: (dt_centroid, dt_bounds, dt_arr, values_arr, fill_value).
    
    .. note:: To view all keys of the returned dict:
    
    >>> my_dict.keys()
    
    .. note:: structure of the returned dictionary: 
    
    >>> all_slices = my_dict.keys()
    
    
    dt_centroid = my_dict['any_slice'][0]
    dt_bounds = my_dict['any_slice'][1]
    dt_arr = my_dict['any_slice'][2]
    values_arr = my_dict['any_slice'][3]
    fill_val = my_dict['any_slice'][4]
    
    
    ##################################################
    ##################################################
    
    Example:
    
    >>> import time_subset
    >>> from netCDF4 import Dataset
    >>> from datetime import datetime
    >>> import numpy
    >>> import icclim
    >>> 
    >>> f = '/data/tasmax_day_EC-EARTH_rcp26_r8i1p1_20760101-21001231.nc'
    >>> nc = Dataset(f, 'r')
    >>> 
    >>> v_arr = nc.variables['tasmax'][:,:,:]
    >>> t_arr = nc.variables['time'][:]
    >>> dt_arr = numpy.array([icclim.util_dt.num2date(dt, calend='gregorian', units='days since 2006-1-1') for dt in t_arr])
    >>> 
    >>> dict_temp_subset = time_subset.get_dict_temporal_slices(dt_arr=dt_arr, values_arr=v_arr, calend='gregorian', temporal_subset_mode='DJF', time_range=[datetime(2080,01,01), datetime(2085,12,31)])
    >>> 
    >>> for key in dict_temp_subset.keys():
    >>>     print key, '======', dict_temp_subset[key][0], '======', dict_temp_subset[key][1]
    ('DJF', 2080) ====== 2081-01-16 00:00:00 ====== [datetime.datetime(2080, 12, 1, 12, 0) datetime.datetime(2081, 3, 1, 12, 0)]
    ('DJF', 2081) ====== 2082-01-16 00:00:00 ====== [datetime.datetime(2081, 12, 1, 12, 0) datetime.datetime(2082, 3, 1, 12, 0)]
    ('DJF', 2082) ====== 2083-01-16 00:00:00 ====== [datetime.datetime(2082, 12, 1, 12, 0) datetime.datetime(2083, 3, 1, 12, 0)]
    ('DJF', 2083) ====== 2084-01-16 00:00:00 ====== [datetime.datetime(2083, 12, 1, 12, 0) datetime.datetime(2084, 3, 1, 12, 0)]
    ('DJF', 2084) ====== 2085-01-16 00:00:00 ====== [datetime.datetime(2084, 12, 1, 12, 0) datetime.datetime(2085, 3, 1, 12, 0)]
    ('DJF', 2085) ====== 2086-01-16 00:00:00 ====== [datetime.datetime(2085, 12, 1, 12, 0) datetime.datetime(2086, 3, 1, 12, 0)]
    
    >>> dict_temp_subset = time_subset.get_dict_temporal_slices(dt_arr=dt_arr, values_arr=v_arr, temporal_subset_mode='JJA', time_range=[datetime(2080,01,01), datetime(2085,12,31)])
    >>> for key in dict_temp_subset.keys():
    >>>     print key, '======', dict_temp_subset[key][0], '======', dict_temp_subset[key][1]
    ('JJA', 2080) ====== 2080-07-16 00:00:00 ====== [datetime.datetime(2080, 6, 1, 12, 0) datetime.datetime(2080, 9, 1, 12, 0)]
    ('JJA', 2081) ====== 2081-07-16 00:00:00 ====== [datetime.datetime(2081, 6, 1, 12, 0) datetime.datetime(2081, 9, 1, 12, 0)]
    ('JJA', 2082) ====== 2082-07-16 00:00:00 ====== [datetime.datetime(2082, 6, 1, 12, 0) datetime.datetime(2082, 9, 1, 12, 0)]
    ('JJA', 2083) ====== 2083-07-16 00:00:00 ====== [datetime.datetime(2083, 6, 1, 12, 0) datetime.datetime(2083, 9, 1, 12, 0)]
    ('JJA', 2084) ====== 2084-07-16 00:00:00 ====== [datetime.datetime(2084, 6, 1, 12, 0) datetime.datetime(2084, 9, 1, 12, 0)]
    ('JJA', 2085) ====== 2085-07-16 00:00:00 ====== [datetime.datetime(2085, 6, 1, 12, 0) datetime.datetime(2085, 9, 1, 12, 0)]
    
    >>> dict_temp_subset = time_subset.get_dict_temporal_slices(dt_arr=dt_arr, values_arr=v_arr, calend='gregorian', temporal_subset_mode='month', time_range=[datetime(2080,01,01), datetime(2082,12,31)])
    >>> 
    >>> for key in dict_temp_subset.keys():
    >>>     print key, '======', dict_temp_subset[key][0], '======', dict_temp_subset[key][1]
    (1, 2080) ====== 2080-01-16 00:00:00 ====== [datetime.datetime(2080, 1, 1, 12, 0) datetime.datetime(2080, 2, 1, 12, 0)]
    (2, 2080) ====== 2080-02-16 00:00:00 ====== [datetime.datetime(2080, 2, 1, 12, 0) datetime.datetime(2080, 3, 1, 12, 0)]
    (3, 2080) ====== 2080-03-16 00:00:00 ====== [datetime.datetime(2080, 3, 1, 12, 0) datetime.datetime(2080, 4, 1, 12, 0)]
    (4, 2080) ====== 2080-04-16 00:00:00 ====== [datetime.datetime(2080, 4, 1, 12, 0) datetime.datetime(2080, 5, 1, 12, 0)]
    (5, 2080) ====== 2080-05-16 00:00:00 ====== [datetime.datetime(2080, 5, 1, 12, 0) datetime.datetime(2080, 6, 1, 12, 0)]
    (6, 2080) ====== 2080-06-16 00:00:00 ====== [datetime.datetime(2080, 6, 1, 12, 0) datetime.datetime(2080, 7, 1, 12, 0)]
    (7, 2080) ====== 2080-07-16 00:00:00 ====== [datetime.datetime(2080, 7, 1, 12, 0) datetime.datetime(2080, 8, 1, 12, 0)]
    (8, 2080) ====== 2080-08-16 00:00:00 ====== [datetime.datetime(2080, 8, 1, 12, 0) datetime.datetime(2080, 9, 1, 12, 0)]
    (9, 2080) ====== 2080-09-16 00:00:00 ====== [datetime.datetime(2080, 9, 1, 12, 0) datetime.datetime(2080, 10, 1, 12, 0)]
    (10, 2080) ====== 2080-10-16 00:00:00 ====== [datetime.datetime(2080, 10, 1, 12, 0) datetime.datetime(2080, 11, 1, 12, 0)]
    (11, 2080) ====== 2080-11-16 00:00:00 ====== [datetime.datetime(2080, 11, 1, 12, 0) datetime.datetime(2080, 12, 1, 12, 0)]
    (12, 2080) ====== 2080-12-16 00:00:00 ====== [datetime.datetime(2080, 12, 1, 12, 0) datetime.datetime(2081, 1, 1, 12, 0)]
    (1, 2081) ====== 2081-01-16 00:00:00 ====== [datetime.datetime(2081, 1, 1, 12, 0) datetime.datetime(2081, 2, 1, 12, 0)]
    (2, 2081) ====== 2081-02-16 00:00:00 ====== [datetime.datetime(2081, 2, 1, 12, 0) datetime.datetime(2081, 3, 1, 12, 0)]
    (3, 2081) ====== 2081-03-16 00:00:00 ====== [datetime.datetime(2081, 3, 1, 12, 0) datetime.datetime(2081, 4, 1, 12, 0)]
    ...

    '''
    
    if type(values_arr)==list: # case of anomalies
        values_arr=values_arr[0]
        
    assert(values_arr.ndim == 3)
    assert(dt_arr.ndim == 1)
    assert(values_arr.shape[0] == dt_arr.shape[0])
    
    return_dict = OrderedDict()
    
    if temporal_subset_mode != None:
        map_info_slice=get_map_info_slice(slice_mode=temporal_subset_mode)
    ###########################
    
    ## step 1: list of all years
    
    if time_range == None:        
        years = util_dt.get_year_list(dt_arr)
        
    else:
        
        year_begin = time_range[0].year
        year_end = time_range[1].year
        
        all_years = numpy.array( util_dt.get_year_list(dt_arr) )
        
        if temporal_subset_mode in ['DJF', 'ONDJFM']:            
            # if time_range is from 1995 to 2000: the "DJF" season of 2000 will be: December 2000 + January 2001 + February 2001
            mask_years = numpy.logical_and(all_years >= year_begin, all_years <= year_end+1) 
        else: 
            mask_years = numpy.logical_and(all_years >= year_begin, all_years <= year_end)
        
        years = all_years[mask_years]
        
        
    years.sort()

    
    
    ## step 2: subset 
    
    # whole selected time range will be processed
    if temporal_subset_mode == None:
        dt_centroid = time_range[0] + (time_range[1]-time_range[0])/2
        dt_bounds = time_range
        return_dict['whole_time_range', time_range[0].year, time_range[1].year] = (dt_centroid, dt_bounds, dt_arr, values_arr, fill_value)
    
    
    # all or selected months of each year will be processed 
    elif temporal_subset_mode == 'month' or temporal_subset_mode[0] == 'month':
        
        for y in years:                          
            for m in map_info_slice[str(temporal_subset_mode)]['months']:
            
                indices_dt_arr_non_masked_i = get_indices_temp_aggregation(dt_arr, month=m, year=y, f=0)
                dt_arr_subset_i = dt_arr[indices_dt_arr_non_masked_i]
                arr_subset_i = values_arr[indices_dt_arr_non_masked_i, :, :]
                
                dt_centroid = datetime(  y, m, map_info_slice[str(temporal_subset_mode)]['centroid_day']  )
                tunits = "seconds since 1600-01-01 00:00:00"
                dtt_num_i = util_dt.date2num(dt_arr_subset_i[-1], calend, tunits)+86400.0
                dtt_i = util_dt.num2date(dtt_num_i, calend=calend, units=tunits)
                dt_bounds = numpy.array([ dt_arr_subset_i[0], dtt_i ]) # [ bnd1, bnd2 )
                
                return_dict[m, y] = (dt_centroid, dt_bounds, dt_arr_subset_i, arr_subset_i, fill_value)
        
            #print y

    # simple seasons (standard or user defined) of each year will be processed
    elif (temporal_subset_mode in ['MAM', 'JJA', 'SON', 'AMJJAS']) or (temporal_subset_mode[0] == 'season' and type(temporal_subset_mode[1]) is list):
    
        for y in years:                         
    
            indices_dt_arr_non_masked_year = get_indices_temp_aggregation(dt_arr, month=map_info_slice[str(temporal_subset_mode)]['months'], year=y, f=1)
            dt_arr_subset_i = dt_arr[indices_dt_arr_non_masked_year]

            arr_subset_i = values_arr[indices_dt_arr_non_masked_year, :, :]
            
            dt_centroid = datetime(  y, map_info_slice[str(temporal_subset_mode)]['centroid_month'], map_info_slice[str(temporal_subset_mode)]['centroid_day']  )
            tunits = "seconds since 1600-01-01 00:00:00"
            dtt_num_i = util_dt.date2num(dt_arr_subset_i[-1], calend, tunits)+86400.0
            dtt_i = util_dt.num2date(dtt_num_i, calend=calend, units=tunits)
            dt_bounds = numpy.array([ dt_arr_subset_i[0], dtt_i ]) # [ bnd1, bnd2 )
            
            return_dict[str(temporal_subset_mode), y] = (dt_centroid, dt_bounds, dt_arr_subset_i, arr_subset_i, fill_value) 
    
            #print y
        
    # composed seasons (standard or user defined) of each year will be processed
    elif (temporal_subset_mode in ['DJF', 'ONDJFM']) or (temporal_subset_mode[0] == 'season' and type(temporal_subset_mode[1]) is tuple):
        
        for y in years:

            next_year = y+1
            
            if next_year in years:
                indices_dt_arr_non_masked_first_year = get_indices_temp_aggregation(dt_arr, month=map_info_slice[str(temporal_subset_mode)]['months'][0], year=y, f=1)

                indices_dt_arr_non_masked_next_year = get_indices_temp_aggregation(dt_arr, month=map_info_slice[str(temporal_subset_mode)]['months'][1], year=next_year, f=1)

                indices_dt_arr_non_masked_current_season = numpy.concatenate((indices_dt_arr_non_masked_first_year, indices_dt_arr_non_masked_next_year))
                indices_dt_arr_non_masked_current_season.sort()
                
                dt_arr_subset_i = dt_arr[indices_dt_arr_non_masked_current_season]
                arr_subset_i = values_arr[indices_dt_arr_non_masked_current_season, :, :]
                
                dt_centroid = datetime(  next_year, map_info_slice[str(temporal_subset_mode)]['centroid_month'], map_info_slice[str(temporal_subset_mode)]['centroid_day']  )
                tunits = "seconds since 1600-01-01 00:00:00"
                dtt_num_i = util_dt.date2num(dt_arr_subset_i[-1], calend, tunits)+86400.0
                dtt_i = util_dt.num2date(dtt_num_i, calend=calend, units=tunits)
                dt_bounds = numpy.array([ dt_arr_subset_i[0], dtt_i ]) # [ bnd1, bnd2 )
                
                return_dict[str(temporal_subset_mode), y] = (dt_centroid, dt_bounds, dt_arr_subset_i, arr_subset_i, fill_value) 
            else:
                pass

    
    elif temporal_subset_mode == 'year':
        
        for y in years:                            
        
            indices_dt_arr_non_masked_i = get_indices_temp_aggregation(dt_arr, month=None, year=y, f=2)
            dt_arr_subset_i = dt_arr[indices_dt_arr_non_masked_i]
            
            arr_subset_i = values_arr[indices_dt_arr_non_masked_i, :, :]
            dt_centroid = datetime(  y, map_info_slice[str(temporal_subset_mode)]['centroid_month'], map_info_slice[str(temporal_subset_mode)]['centroid_day']  )
            tunits = "seconds since 1600-01-01 00:00:00"
            dtt_num_i = util_dt.date2num(dt_arr_subset_i[-1], calend, tunits)+86400.0
            dtt_i = util_dt.num2date(dtt_num_i, calend=calend, units=tunits)
            dt_bounds = numpy.array([ dt_arr_subset_i[0], dtt_i ]) # [ bnd1, bnd2 )
            
            return_dict[temporal_subset_mode, y] = (dt_centroid, dt_bounds, dt_arr_subset_i, arr_subset_i, fill_value)
        
            #print y
    

    return return_dict
        
        
            
def get_indices_temp_aggregation(dt_arr, month, year, f=0):    
    '''
    
    Return indices used for temporal aggregation.
    
    param dt_arr: datetime vector
    type dt_arr: numpy.ndarray (1D) of datetime.datetime objects
    
    param month: month
    type month: int or list of int
    
    param year: year
    type year: int
    
    param f: used for different kinds of temporal aggregations: ``0`` - monthly,  ``1`` - seasonal, ``2`` - annual (default: 0)
    type f: int
   
    rtype: numpy.ndarray (1D)
    
    '''
    
    
    if f == 0: # used for monthly temporal aggregation
        
        dt_arr_month = numpy.array([dt.month for dt in dt_arr])
        dt_arr_mask_month = dt_arr_month != month
        indices_non_masked_month = numpy.where(dt_arr_mask_month==False)[0]
        
        dt_arr_year = numpy.array([dt.year for dt in dt_arr])
        dt_arr_mask_year = dt_arr_year != year
        indices_non_masked_year = numpy.where(dt_arr_mask_year==False)[0]
        
        indices_non_masked = numpy.intersect1d(indices_non_masked_year, indices_non_masked_month)   
    
    
    elif f == 1: # used for seasonal temporal aggregation
        
        indices_non_masked_month_glob = []

        dt_arr_month = numpy.array([dt.month for dt in dt_arr])
            
        for m in month:
            
            dt_arr_mask_month = dt_arr_month != m
            
            indices_non_masked_month = numpy.where(dt_arr_mask_month==False)[0]
            
            indices_non_masked_month_glob.extend( list(indices_non_masked_month) )

    
        dt_arr_year = numpy.array([dt.year for dt in dt_arr])
        dt_arr_mask_year = dt_arr_year != year
        indices_non_masked_year = numpy.where(dt_arr_mask_year==False)[0]

        indices_non_masked = numpy.intersect1d(indices_non_masked_year, indices_non_masked_month_glob) 
    
    
    elif f == 2: # used for annual temporal aggregation
        
        dt_arr_year = numpy.array([dt.year for dt in dt_arr])
        dt_arr_mask_year = dt_arr_year != year
        indices_non_masked = numpy.where(dt_arr_mask_year==False)[0]
    
    
    return indices_non_masked
    
### This function is used for the bootstrapping procedure
def get_resampled_arrs(dt_arr, values_arr, year_to_eliminate, year_to_duplicate):
    
    ### "out-of-base" years ---> no resampling
    if year_to_eliminate == year_to_duplicate == -9999:
        return (dt_arr, values_arr)
    
    ### "in-base" years ---> resampling
    else:
        # step 1: we eliminate in-base year ("year_to_eliminate"), i.e. we subset our arrays (dt and values)
        
        # we define indices where dt_arr != year_to_eliminate
        dt_arr_years = numpy.array([dt.year for dt in dt_arr])
        dt_arr_mask_year = dt_arr_years == year_to_eliminate
        indices_non_masked = numpy.where(dt_arr_mask_year==False)[0]
        
        # we subset
        dt_arr_subsetted = dt_arr[indices_non_masked]
        values_arr_subsetted = values_arr[indices_non_masked, :, :] # 3D - whole array
    
    
        # step 2: we duplicate one of rest years ("year_to_duplicate")
        
        # we define indices where dt_arr_subsetted == year_to_duplicate 
        dt_arr_subsetted_years = numpy.array([dt.year for dt in dt_arr_subsetted])
        dt_arr_mask_year = dt_arr_subsetted_years == year_to_duplicate
        indices_year_to_duplicate = numpy.where(dt_arr_mask_year==True)[0]
        
        # we define array slices to duplicate
        dt_arr_year_to_duplicate = dt_arr_subsetted[indices_year_to_duplicate]    
        values_arr_year_to_duplicate = values_arr_subsetted[indices_year_to_duplicate, :, :] # 3D - whole array
        
        # we add slices to duplicate in the end
        dt_arr_result = numpy.append(dt_arr_subsetted, dt_arr_year_to_duplicate)    
        values_arr_result = numpy.append(values_arr_subsetted, values_arr_year_to_duplicate, axis=0)

        
        return (dt_arr_result, values_arr_result)
