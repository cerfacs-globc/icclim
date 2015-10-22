#  Copyright CERFACS (http://cerfacs.fr/)
#  Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
#
#  Author: Natalia Tatarinova




import numpy
numpy.set_printoptions(threshold=numpy.nan)
from datetime import datetime
from collections import OrderedDict, defaultdict
import calendar
import util.calc as calc

import ctypes
from numpy.ctypeslib import ndpointer
import os
my_rep = os.path.dirname(os.path.abspath(__file__)) + os.sep
libraryC = ctypes.cdll.LoadLibrary(my_rep+'libC.so')


###########################################################
############### utility functions: begin ################## 

def get_dict_caldays(dt_arr):
    '''
    Create a dictionary of calendar days, where keys=months, values=days.
    
    :param dt_arr: time steps vector
    :type dt_arr: numpy.ndarray (1D) of datetime objects
    
    :rtype: dict
    
    '''

    dic = defaultdict(list)

    for dt in dt_arr:
        dic[dt.month].append(dt.day)

    for key in dic.keys():
        dic[key] = list(set(dic[key])) 
    
    return dic



    
def get_masked(current_date, month, day, hour, window_width, only_leap_years, ignore_Feb29th=False): 

    '''
    Returns "True" if "current_date" is not in the window centered on the given calendar day (month-day).
    Returns "False", if it enters in the window.
    
    :param current_date: current date
    :type current_date: datetime object 
    :param month: month of the corresponding calendar day
    :type month: int
    :param day: day of the corresponding calendar day
    :type day: int
    :param hour: hour of the current day
    :type hour int
    :param window_width: window width, must be odd
    :type window_width: int
    :param only_leap_years: option for February 29th 
    :type only_leap_years: bool

    :rtype: bool (if True, the date will be masked)
    
    '''
    
    yyyy = current_date.year
    

    if (day==29 and month==02):
        if calendar.isleap(yyyy):
            dt1 = datetime(yyyy,month,day,hour)
            diff = abs(current_date-dt1).days
            toReturn = diff > window_width/2
        else:
            if only_leap_years:
                toReturn=True
            else:                
                dt1 = datetime(yyyy,02,28,hour)
                diff = (current_date-dt1).days
                toReturn = (diff < (-(window_width/2) + 1)) or (diff > window_width/2)
    else:
        
        
        
        d1 = datetime(yyyy,month,day, hour)
        
        # In the case the current date is in December and calendar day (day-month) is at the beginning of year.
        # For example we are looking for dates around January 2nd, and the current date is 31 Dec 1999,
        # we will compare it with 02 Jan 2000 (1999 + 1)
        d2 = datetime(yyyy+1,month,day, hour)
        
        # In the case the current date is in January and calendar day (day-month) is at the end of year.
        # For example we are looking for dates around December 31st, and the current date is 02 Jan 2003,
        # we will compare it with 01 Jan 2002 (2003 - 1) 
        d3 = datetime(yyyy-1,month,day, hour)
        
        
        
        diff=min(abs(current_date-d1).days,abs(current_date-d2).days,abs(current_date-d3).days)    

        if ignore_Feb29th==True and calendar.isleap(yyyy) and (   abs((current_date-datetime(yyyy,02,29,hour)).days) < window_width/2 ):

            diff =  diff -1
            
            
            
        toReturn = diff > window_width/2
        
    return toReturn


def get_mask_dt_arr(dt_arr, month, day, dt_hour, window_width, only_leap_years, ignore_Feb29th=False):
    '''
    Creates a binary mask for a datetime vector for a given calendar day (month-day).
    
    :param dt_arr: time steps vector
    :type dt_arr: numpy.ndarray (1D) of datetime objects
    :param month: month of a calendar day
    :type month: int
    :param day: day of a calendar day
    :type day: int
    :param window_width: window width, must be odd
    :type window_width: int
    :param only_leap_years: option for February 29th 
    :type only_leap_years: bool
    
    :param window_width: window width, must be odd
    :type window_width: int
    
    rtype: numpy.ndarray (1D)   
    ''' 
    mask = numpy.array([get_masked(dt, month, day, dt_hour, window_width, only_leap_years, ignore_Feb29th) for dt in dt_arr])
    return mask


def get_year_list(dt_arr):
    '''
    Returns a list of all years of the time steps vector (dt_arr).
    '''

    year_list = []
    for dt in dt_arr:
        year_list.append(dt.year)
        
    year_list = list(set(year_list))
    
    return year_list

def get_masked_arr(arr, fill_val):
    '''
    If a masked array is passed, this function does nothing.
    If a filled array is passed (fill_value must be passed also), it will be transformed into a masked array.
    
    '''
    if isinstance(arr, numpy.ma.MaskedArray):               # numpy.ma.MaskedArray
        masked_arr = arr
    else:                                                   # numpy.ndarray
        if (fill_val==None):
            raise(ValueError('If input array is not a masked array, a "fill_value" must be provided.'))
        mask_arr = (arr==fill_val)
        masked_arr = numpy.ma.masked_array(arr, mask=mask_arr, fill_value=fill_val)
    
    return masked_arr

############### utility functions: end ##################
#########################################################

### used to get daily percentile thresholds for temperature variables
def get_percentile_dict(arr, dt_arr, percentile, window_width, only_leap_years=False, callback=None, callback_percentage_start_value=0, 
                        callback_percentage_total=100, chunk_counter=1, fill_val=None,
                        ignore_Feb29th=False, interpolation="hyndman_fan"):
    '''
    Creates a dictionary with keys=calendar day (month,day) and values=numpy.ndarray (2D)
    Example - to get the 2D percentile array corresponding to the 15th Mai: percentile_dict[5,15]
    
    :param arr: array of values 
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D) of float
    
    :param dt_arr: corresponding time steps vector (base period: usually 1961-1990)
    :type dt_arr: numpy.ndarray (1D) of datetime objects
    
    :param percentile: percentile to compute which must be between 0 and 100 inclusive
    :type percentile: int
    
    :param window_width: window width, must be odd
    :type window_width: int
    
    :param only_leap_years: option for February 29th (default: False)
    :type only_leap_years: bool
    
    :param callback: progress bar, if ``None`` progress bar will not be printed
    :type callback: :func:`callback.defaultCallback2`
    
    :param callback_percentage_start_value: init value for percentage of progress bar (default: 0)
    :type callback_percentage_start_value: int
    
    :param callback_percentage_total: final value for percentage of progress bar (default: 100)   
    :type callback_percentage_total: int
        
    :param chunk_counter: chunk counter in case of chunking 
    :type chunk_counter: int
    
    :param fill_val: fill value of ``arr``
    :type fill_val: float
    
    :param ignore_Feb29th: Ignoring or not February 29th (default: False)
    :type ignore_Feb29th: bool
    
    :param interpolation: type of used interpolation: "linear" or "hyndman_fan" (default: "hyndman_fan")
    :type interpolation: str
    
    :rtype: dict

    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    
    '''
    
    assert(arr.ndim == 3)
    assert(arr.shape[0]==dt_arr.shape[0])
    
    # for callback print
    nb_months = 12*1.0
    percent_one_month = ((callback_percentage_total)/nb_months) ######## callback_percentage_total default value = 100 %; set callback_percentage_total=50% for WPS: computing percentiles will be 50%  (other 50% for computing indice)
    
    percent_current_month = callback_percentage_start_value + (chunk_counter-1)*callback_percentage_total

    # step1: creation of the dictionary with all calendar days:
    dic_caldays = get_dict_caldays(dt_arr)
    
    percentile_dict = OrderedDict()
    
    dt_hour = dt_arr[0].hour # (we get hour of a date only one time, because usually the hour is the same for all dates in input dt_arr)
    
    # we mask our array in case it has fill_values
    arr_masked = get_masked_arr(arr, fill_val)
    
    fill_val = arr_masked.fill_value

    arr_filled = arr_masked.filled(fill_val)
    del arr_masked
          
    ############################## prepare calling C function   
    # data type should be 'float32' to pass it to C function
    if arr_filled.dtype != 'float32':
        arr_filled = numpy.array(arr_filled, dtype='float32')
            
    C_percentile = libraryC.percentile_3d
    C_percentile.restype = None    
    
    C_percentile.argtypes = [ndpointer(ctypes.c_float),
                                        ctypes.c_int,
                                        ctypes.c_int,
                                        ctypes.c_int,
                                        ndpointer(ctypes.c_double),
                                        ctypes.c_int,
                                        ctypes.c_float,
                                        ctypes.c_char_p]
                                                
    
    
    ## we check the fill_value (we need it to be the maximum value in the array)        
    if fill_val == arr_filled.max():
        pass
    else:
        fill_val_new = 1e+20 
        arr_filled[arr_filled==fill_val] = fill_val_new 
        fill_val = fill_val_new
        
    #############################

    for month in dic_caldays.keys():
        for day in dic_caldays[month]:

            arr_percentille_current_calday = numpy.zeros([arr.shape[1], arr.shape[2]]) # we reserve memory
            
            # step2: we do a mask for the datetime vector for current calendar day (day/month)
            dt_arr_mask = get_mask_dt_arr(dt_arr, month, day, dt_hour, window_width, only_leap_years, ignore_Feb29th)
            
            
            # step3: we are looking for the indices of non-masked dates (i.e. where dt_arr_mask==False) 
            indices_non_masked = numpy.where(dt_arr_mask==False)[0]
             
            # step4: we subset our arr
            #arr_subset = arr_filled[indices_non_masked, :, :].squeeze()
            arr_subset = arr_filled[indices_non_masked, :, :]
           
            # step5: we compute the percentile for current arr_subset           
            C_percentile(arr_subset, arr_subset.shape[0], arr_subset.shape[1], arr_subset.shape[2], arr_percentille_current_calday, percentile, fill_val, interpolation)
            
            arr_percentille_current_calday = arr_percentille_current_calday.reshape(arr.shape[1], arr.shape[2])          

            # step6: we add to the dictionary
            percentile_dict[month,day] = arr_percentille_current_calday

        
        if callback != None:
            percent_current_month =  percent_current_month + percent_one_month
            callback(percent_current_month)
        

        
    return percentile_dict



### This function computes percentiles from whole set of values ('arr').
### It is used to get percentile thresholds for precipitation variables.
### All percentile indices based on precipitation use percentile thresholds 
### computed from set of "wet" values i.e. values >=1.0 mm (i.e. precipitation=True)
### If precipitation=False: all values will be processed.
def get_percentile_arr(arr, percentile, callback=None, callback_percentage_start_value=0, 
                        callback_percentage_total=100, chunk_counter=1, precipitation=True, fill_val=None,
                        interpolation="hyndman_fan"):
    '''
    Returns an 2D array with computed percentile values. 
    
    :param arr: array of values (in case of precipitation, units must be `mm/day`)
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D) of float
    
    :param dt_arr: corresponding time steps vector (base period: usually 1961-1990)
    :type dt_arr: numpy.ndarray (1D) of datetime objects
    
    :param percentile: percentile to compute which must be between 0 and 100 inclusive
    :type percentile: int
    
    :param callback: progress bar, if ``None`` progress bar will not be printed
    :type callback: :func:`callback.defaultCallback2`
    
    :param callback_percentage_start_value: init value for percentage of progress bar (default: 0)
    :type callback_percentage_start_value: int
    
    :param callback_percentage_total: final value for percentage of progress bar (default: 100)   
    :type callback_percentage_total: int
        
    :param chunk_counter: chunk counter in case of chunking 
    :type chunk_counter: int
    
    :param precipitation: if True, only values >=1.0 mm will be processed (i.e. wet days) 
    :type precipitation: bool    
    
    :param fill_val: fill value of ``arr``
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)

    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    
    '''
    
    assert(arr.ndim == 3)

    # we mask our array in case it has fill_values
    arr_masked = get_masked_arr(arr, fill_val)
    
    fill_val = arr_masked.fill_value
    
    ### not precipitation
    if precipitation == False: 
        arr_filled = arr_masked.filled(fill_val) 

        
    ### precipitation
    else:
        
        # we process only wet days (daily precip. amount >= 1.0 mm)
        wet_arr = calc.get_wet_days(arr=arr_masked)
     
        # we fill all masked values with fill_val to pass the filled array to the C function
        arr_filled = wet_arr.filled(fill_val)

    del arr_masked

          

    ############################## prepare calling C function
    # data type should be 'float32' to pass it to C function
    if arr_filled.dtype != 'float32':
        arr_filled = numpy.array(arr_filled, dtype='float32')

    C_percentile = libraryC.percentile_3d
    C_percentile.restype = None    
    
    C_percentile.argtypes = [ndpointer(ctypes.c_float),
                                        ctypes.c_int,
                                        ctypes.c_int,
                                        ctypes.c_int,
                                        ndpointer(ctypes.c_double),
                                        ctypes.c_int,
                                        ctypes.c_float,
                                        ctypes.c_char_p]
                                                
    
    
    ## we check the fill_value (we need it to be the maximum value in the array)        
    if fill_val == arr_filled.max():
        pass
    else:
        fill_val_new = 1e+20 
        arr_filled[arr_filled==fill_val] = fill_val_new 
        fill_val = fill_val_new
        
    #############################

    arr_percentille = numpy.zeros([arr.shape[1], arr.shape[2]]) # we reserve memory
        
    # we compute the percentiles      
    C_percentile(arr_filled, arr_filled.shape[0], arr_filled.shape[1], arr_filled.shape[2], arr_percentille, percentile, fill_val, interpolation)
    
    arr_percentille = arr_percentille.reshape(arr.shape[1], arr.shape[2])

 
    return arr_percentille



