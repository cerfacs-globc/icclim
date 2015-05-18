# -*- coding: latin-1 -*-

#  Copyright CERFACS (http://cerfacs.fr/)
#  Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
#
#  Author: Natalia Tatarinova

"""
Types of temporal aggregations:
- 'month'
- 'year'
- 'DFJ'
- 'MAM'
- 'JJA'
- 'SON'
- 'ONDJFM'
- 'AMJJAS'

Note: DJF 2000: December 2000 + January 2001 + February 2001

"""

import numpy
from netCDF4 import Dataset, MFDataset
from datetime import datetime
from collections import OrderedDict, defaultdict

import util.util_dt as util_dt


map_months =   {
                'None': range(1,13),
                'month': range(1,13),
                'DJF': ([12], [1,2]),  # (year i, year i+1)
                'MAM': [3,4,5],
                'JJA': [6,7,8],
                'SON': [9,10,11],
                'ONDJFM': ([10,11,12], [1,2,3]), # (year i, year i+1)
                'AMJJAS': [4,5,6,7,8,9]
                }


map_dt_centroid_day =   {
                        'None': 16,
                        'month': 16,
                        'DJF': 16,
                        'MAM': 16,
                        'JJA': 16,
                        'SON': 16,
                        'ONDJFM': 1,
                        'AMJJAS': 1,
                        'year': 1
                        }


map_dt_centroid_month = {
                        'DJF': 1,
                        'MAM': 4,
                        'JJA': 7,
                        'SON': 10,
                        'ONDJFM': 1,
                        'AMJJAS': 7,
                        'year': 7
                        }

def get_dict_temporal_slices(dt_arr, values_arr, calend='gregorian', temporal_subset_mode=None, time_range=None):
    
    '''
    
    This function 
    Temporal aggregation: return a dictionnary with temporal slices.
    
    :param dt_arr: Datetime vector.
    :type dt_arr: numpy.ndarray (1D) of datetime.datetime objects
    
    :param values_arr: Corresponding to ``dt_arr`` array of values.
    :type values_arr: numpy.ndarray (3D) 
    
    :param temporal_subset_mode: Type of temporal aggregation: the same set of possible values as ``slice_mode``.
    :type temporal_subset_mode: str 
    
    :param time_range: Time range.
    :type time_range: [datetime.datetime, datetime.datetime]
    
    :rtype: dict, where key is (``temporal_subset_mode``, year) and values are grouped in a tuple with 4 elements: (dt_centroid, dt_bounds, dt_arr, values_arr).
    
    .. note:: 
    dt_centroid = my_dict[key][0]
    dt_bounds = my_dict[key][1]
    dt_arr = my_dict[key][2]
    values_arr = my_dict[key][3]
    
    
    Example:
    
    >>> import time_subset
    >>> from netCDF4 import Dataset
    >>> from datetime import datetime
    >>> import numpy
    >>> import icclim
    >>> 
    >>> f = '/data/tatarinova/tasmax_day_EC-EARTH_rcp26_r8i1p1_20760101-21001231.nc'
    >>> nc = Dataset(f, 'r')
    >>> 
    >>> v_arr = nc.variables['tasmax'][:,:,:]
    >>> t_arr = nc.variables['time'][:]
    >>> dt_arr = numpy.array([icclim.num2date(dt, calend='gregorian', units='days since 2006-1-1') for dt in t_arr])
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
    
    assert(values_arr.ndim == 3)
    assert(dt_arr.ndim == 1)
    
    return_dict = OrderedDict()

    
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
    #print years
    
    
    ## step 2: subset 
    
    # all months of each year will be processed 
    if temporal_subset_mode == None or temporal_subset_mode == 'month':
        
        for y in years:                            
            for m in map_months[temporal_subset_mode]:
            
                indices_dt_arr_non_masked_i = get_indices_temp_aggregation(dt_arr, month=m, year=y, f=0)
                dt_arr_subset_i = dt_arr[indices_dt_arr_non_masked_i]
                arr_subset_i = values_arr[indices_dt_arr_non_masked_i, :, :]
                
                dt_centroid = datetime(  y, m, map_dt_centroid_day[temporal_subset_mode]  )
                tunits = "seconds since 1600-01-01 00:00:00"
                dtt_num_i = util_dt.date2num(dt_arr_subset_i[-1], calend, tunits)+86400.0
                dtt_i = util_dt.num2date(dtt_num_i, calend=calend, units=tunits)
                dt_bounds = numpy.array([ dt_arr_subset_i[0], dtt_i ]) # [ bnd1, bnd2 )
                
                return_dict[m, y] = (dt_centroid, dt_bounds, dt_arr_subset_i, arr_subset_i)
        
            #print y

    
    elif temporal_subset_mode in ['MAM', 'JJA', 'SON', 'AMJJAS']:
    
        for y in years:                         
    
            indices_dt_arr_non_masked_year = get_indices_temp_aggregation(dt_arr, month=map_months[temporal_subset_mode], year=y, f=1)
            dt_arr_subset_i = dt_arr[indices_dt_arr_non_masked_year]

            arr_subset_i = values_arr[indices_dt_arr_non_masked_year, :, :]
            
            dt_centroid = datetime(  y, map_dt_centroid_month[temporal_subset_mode], map_dt_centroid_day[temporal_subset_mode]  )
            tunits = "seconds since 1600-01-01 00:00:00"
            dtt_num_i = util_dt.date2num(dt_arr_subset_i[-1], calend, tunits)+86400.0
            dtt_i = util_dt.num2date(dtt_num_i, calend=calend, units=tunits)
            dt_bounds = numpy.array([ dt_arr_subset_i[0], dtt_i ]) # [ bnd1, bnd2 )
            
            return_dict[temporal_subset_mode, y] = (dt_centroid, dt_bounds, dt_arr_subset_i, arr_subset_i) 
    
            #print y
        
    
    elif temporal_subset_mode in ['DJF', 'ONDJFM']:
        
        for y in years:

            next_year = y+1
            
            if next_year in years:
                indices_dt_arr_non_masked_first_year = get_indices_temp_aggregation(dt_arr, month=map_months[temporal_subset_mode][0], year=y, f=1)

                indices_dt_arr_non_masked_next_year = get_indices_temp_aggregation(dt_arr, month=map_months[temporal_subset_mode][1], year=next_year, f=1)

                indices_dt_arr_non_masked_current_season = numpy.concatenate((indices_dt_arr_non_masked_first_year, indices_dt_arr_non_masked_next_year))
                indices_dt_arr_non_masked_current_season.sort()
                
                dt_arr_subset_i = dt_arr[indices_dt_arr_non_masked_current_season]
                arr_subset_i = values_arr[indices_dt_arr_non_masked_current_season, :, :]
                
                dt_centroid = datetime(  next_year, map_dt_centroid_month[temporal_subset_mode], map_dt_centroid_day[temporal_subset_mode]  )
                tunits = "seconds since 1600-01-01 00:00:00"
                dtt_num_i = util_dt.date2num(dt_arr_subset_i[-1], calend, tunits)+86400.0
                dtt_i = util_dt.num2date(dtt_num_i, calend=calend, units=tunits)
                dt_bounds = numpy.array([ dt_arr_subset_i[0], dtt_i ]) # [ bnd1, bnd2 )
                
                return_dict[temporal_subset_mode, y] = (dt_centroid, dt_bounds, dt_arr_subset_i, arr_subset_i) 
            else:
                pass

    
    elif temporal_subset_mode == 'year':
        
        for y in years:                            
        
            indices_dt_arr_non_masked_i = get_indices_temp_aggregation(dt_arr, month=None, year=y, f=2)
            dt_arr_subset_i = dt_arr[indices_dt_arr_non_masked_i]
            
            arr_subset_i = values_arr[indices_dt_arr_non_masked_i, :, :]
            dt_centroid = datetime(  y, map_dt_centroid_month[temporal_subset_mode], map_dt_centroid_day[temporal_subset_mode]  )
            tunits = "seconds since 1600-01-01 00:00:00"
            dtt_num_i = util_dt.date2num(dt_arr_subset_i[-1], calend, tunits)+86400.0
            dtt_i = util_dt.num2date(dtt_num_i, calend=calend, units=tunits)
            dt_bounds = numpy.array([ dt_arr_subset_i[0], dtt_i ]) # [ bnd1, bnd2 )
            
            return_dict[temporal_subset_mode, y] = (dt_centroid, dt_bounds, dt_arr_subset_i, arr_subset_i)
        
            #print y


    return return_dict
        
        
            
def get_indices_temp_aggregation(dt_arr, month=None, year=None, f=0):    
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
    


