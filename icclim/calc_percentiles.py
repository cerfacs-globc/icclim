#  Copyright CERFACS (http://cerfacs.fr/)
#  Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
#
#  Author: Natalia Tatarinova

import numpy as np
#np.set_printoptions(threshold=np.nan)

from datetime import datetime
from datetime import timedelta
import datetime
from collections import OrderedDict, defaultdict
import pdb
import calendar
import cftime
import sys
import ctypes
from numpy.ctypeslib import ndpointer
import os
import cftime

from .util import calc
from .util import util_dt

my_rep = os.path.dirname(os.path.abspath(__file__)) + os.sep
libraryC = ctypes.cdll.LoadLibrary(my_rep+'libC.so')

###########################################################
############### utility functions: begin ##################

def get_dict_caldays(dt_arr):
    '''
    Create a dictionary of calendar days, where keys=months, values=days.

    :param dt_arr: time steps vector
    :type dt_arr: np.ndarray (1D) of datetime objects

    :rtype: dict

    '''

    dic = defaultdict(list)

    for dt in dt_arr:
        dic[dt.month].append(dt.day)

    for key in dic.keys():
        dic[key] = list(set(dic[key]))

    return dic


def get_masked_arr(arr, fill_val):
    '''
    If a masked array is passed, this function does nothing.
    If a filled array is passed (fill_value must be passed also), it will be transformed into a masked array.

    '''
    if isinstance(arr, np.ma.MaskedArray):               # np.ma.MaskedArray
        masked_arr = arr
    else:                                                   # np.ndarray
        if (fill_val==None):
            raise(ValueError('If input array is not a masked array, a "fill_value" must be provided.'))
        mask_arr = (arr==fill_val)
        masked_arr = np.ma.masked_array(arr, mask=mask_arr, fill_value=fill_val)

    return masked_arr


#get_list_year returns a list containing all the year except the year to be duplicated
def get_list_year(ytd, dt_arr):
    list_year = []
    if ytd != -9999:
        list_year.append(ytd)
    [list_year.append(date.year) for date in dt_arr if date.year not in list_year]
    return list_year


#The input in this function are the indexes of the days and the window we aim to perform the calculation on
#It does return all the index from a same day (e.g 10/01) for all the year within the base period
def get_index_with_window(ind_2_calc, window_wide, test):
    return np.array([np.arange(ind_date_i - window_wide, ind_date_i + window_wide+1) for ind_date_i in ind_2_calc[ind_2_calc!=test[0]]])


#get_index_for_other_years returns the indexes for the centered days t within the time series - dt_arr & dt_arr_num
def get_index_for_other_years(t_units, t, calend, list_year, ytd, dt_arr_num):
    if calend == 'all_leap' or calend == '366_day':
        same_date_other_year = [cftime._cftime.DatetimeAllLeap(year, t.month, t.day, t.hour, t.minute) for year in list_year if year!=ytd]
    elif calend == '360_day':
        same_date_other_year = [cftime._cftime.Datetime360Day(year, t.month, t.day, t.hour, t.minute) for year in list_year if year!=ytd]
    elif calend == 'gregorian':
        same_date_other_year = [cftime._cftime.DatetimeGregorian(year, t.month, t.day, t.hour, t.minute) for year in list_year if year!=ytd]
    elif calend == 'proleptic_gregorian':
        same_date_other_year = [cftime._cftime.DatetimeProlepticGregorian(year, t.month, t.day, t.hour, t.minute) for year in list_year if year!=ytd]
    elif calend == 'julian':
        same_date_other_year = [cftime._cftime.DatetimeJulian(year, t.month, t.day, t.hour, t.minute) for year in list_year if year!=ytd]
    else:
        same_date_other_year = [cftime.datetime(year, t.month, t.day, t.hour, t.minute) for year in list_year if year!=ytd]

    sdoy2num = cftime.date2num(same_date_other_year, t_units, t_calendar)

    #We change sdoy2num and dt_arr_num dtype to int to avoid unknown index because of +/- half day across year
    sdoy2num = sdoy2num.astype(np.int32)
    dt_arr_num = dt_arr_num.astype(np.int32)

    return [np.where(sdoy_ind==dt_arr_num)[0][0] for sdoy_ind in sdoy2num]


#get_leap_year returns a list containing all leap year of the time serie
def get_leap_year(list_year):
    list_year = np.array(list_year)
    return list(list_year[list_year%4==0])


#get_non_leap_year returns a list containing all the non leap year of the time serie
def get_non_leap_year(list_year):
    list_year = np.array(list_year)
    return list(list_year[list_year%4!=0]) 


#check_leap_day check if the current year is leap. If the calendar is 360 days, there is no leap year (==>29/02 & 30/02)
def check_leap_day(t_calendar, t, ytd, only_leap_years):
    if [t.month, t.day] == [2,29] and t_calendar!='360_day':
        return True
    else:
        return False


#get_first_ytd_day returns the first index (first day) of the year to duplicate
def get_first_ytd_day(dt_arr, dt_arr_num, t_units, t_calendar, ytd):
    for date in dt_arr:
        if date.year==ytd:
            date_num = cftime.date2num(date, t_units, t_calendar)
            ind_ytd_start = np.where(date_num==dt_arr_num)[0][0]
            break
    return ind_ytd_start


#get_ind_2_calc returns the indexes of the day required to perform the percentile and the indexes within the window related to it
def get_ind_2_calc(i, ind_date, len_ytd, window_wide, ind_ytd_start, bootstrapping):

    #We concatenate the indexes for the duplicated year and the other index. The second line is the duplication
    if bootstrapping:
        ind_2_calc = np.append(ind_ytd_start+i,ind_date)
        ind_2_calc = np.append(ind_2_calc, ind_ytd_start+i)
    else:
        ind_2_calc = np.array(ind_date)

    #We build the window around the centered day in this condition
    #test condition is true if the index are smaller than half of the window. i.e i=1, window_width=5 ==> window_wide=2: i<window_wide
    if i<window_wide:
        #ranging_day creates the vector with all the window centered on the day
        ranging_day = np.array([np.arange(ind_date_i - window_wide, ind_date_i + window_wide+1) for ind_date_i in ind_2_calc[ind_2_calc!=i]])#ind_2_calc[ind_2_calc!=test[0]]])
        #day_after are the day within the window and after the index 0. i.e test[0]=1 and window_wide=2; day_after=[0,1,2,3]
        day_after = np.arange(0, i+window_wide+1)
        #Following what has been done on the previous version we take the last index of the array to fulfill the missing data before the first year
        day_before = np.arange(i+len_ytd-window_wide, len_ytd)
        #We concatenate the two vector below
        day_ytd = np.concatenate([day_after,day_before])
        #We finally create the vector with all index to perform calculation
        ind_2_calc = np.concatenate([[day_ytd],ranging_day])

    #if the window center reach the end of the time vector. i.e if len_ytd=365, i=363 and window_wide = 2
    #it avoids to get index out of the bound
    elif i>=(len_ytd-window_wide) and not bootstrapping:
        #We first get all the window for every year except the last year
        ind_2_calc = np.array([np.arange(ind_date_i - window_wide, ind_date_i + window_wide+1) for ind_date_i in ind_2_calc[:-1]])
        #We generate here the window for the last day
        last_day = np.arange(ind_date[-1] - window_wide, ind_date[-1] + (len_ytd-i))
        #We finally concatenate all the year and the last year together
        ind_2_calc = np.append(ind_2_calc, last_day)

    else:
        #We generate the window centered on the day we aim to perform the percentile calculation
        ind_2_calc = np.array([np.arange(ind_date_i - window_wide, ind_date_i + window_wide+1) for ind_date_i in ind_2_calc])

    return np.reshape(ind_2_calc, -1)


#get_ind_2_calc_for_leap is similar than get_ind_2_calc but return the index for the non leap year related to 29th Feb.
#It does return a window width of ranking (n-1) compare to the leap year
#More details about leap calculation are available on the doc
def get_ind_2_calc_for_non_leap(i, ind_date, len_ytd, window_wide):
    ind_2_calc = np.array(ind_date)
    if i<window_wide:
        #ranging_day creates the vector with all the window centered on the day
        ranging_day = np.array([np.arange(ind_date_i - window_wide, ind_date_i + window_wide+1) for ind_date_i in ind_2_calc[ind_2_calc!=i]])
        #day_after are the day within the window and after the index 0. i.e test[0]=1 and window_wide=2; day_after=[0,1,2,3]
        day_after = np.arange(0, i+window_wide+1)
        #Following what has been done on the previous version we take the last index of the array to fulfill the missing data before the first year
        day_before = np.arange(i+len_ytd-window_wide, len_ytd)
        #We concatenate the two vector below
        day_ytd = np.concatenate([day_after,day_before])
        #We finally create the vector with all index to perform calculation
        ind_2_calc = np.concatenate([[day_ytd],ranging_day])

    elif i>=(len_ytd-window_wide):
        #We first get all the window for every year except the last year
        ind_2_calc = np.array([np.arange(ind_date_i - window_wide, ind_date_i + window_wide+1) for ind_date_i in ind_2_calc[:-1]])
        #We generate here the window for the last day
        last_day = np.arange(ind_date[-1] - window_wide, ind_date[-1] + (len_ytd-i))
        #We finally concatenate all the year and the last year together
        ind_2_calc = np.append(ind_2_calc, last_day)

    else:
        ind_2_calc = np.array([np.arange(ind_date_i - window_wide+1, ind_date_i + window_wide+1) for ind_date_i in ind_2_calc])

    return np.reshape(ind_2_calc, -1)


#indices_to_return_for_percentile_calc returns the indices for the percentile calculation
def indices_to_return_for_percentile_calc(dt_arr_num, dt_arr, list_year, window_wide, i, len_ytd, ytd,  
                                            t_units, t_calendar, t, 
                                            ignore_Feb29th, only_leap_years, bootstrapping,
                                            ind_ytd_start=0):

    '''
    Return the index from which we aim to compute the percentile
    :param dt_arr_num: time steps vector number
    :type dt_arr: np.ndarray (1D) of float
    :param dt_arr: time steps vector
    :type dt_arr: np.ndarray (1D) of datetime objects
    :param list_year: list of year
    :param window_wide: left or right side of the window
    :type window_wide: int
    :param i: day of a calendar day
    :type i: int
    :param len_ytd: length of the calendar year
    :type len_ytd: int
    :param t_units: netcdf time units
    :type t_units: string
    :param ignore_Feb29th: Ignore or not February 29th
    :type ignore_Feb29th: bool    
    :param only_leap_years: option for February 29th
    :type only_leap_years: bool
    :param bootstrapping: True if we have to do the bootstrapping
    :type: bool
    :param ind_ytd_start: ind for the year to duplicate. 0 if no bootstrapping
    :type: int 

    rtype: np.ndarray (2D)
    '''

    #This part returns the indices to calculate when the duplicated year is leap
    if ignore_Feb29th==False and check_leap_day(t_calendar, t, ytd, only_leap_years):

        #only_leap_years means we only take in account the leap year for calculation
        if only_leap_years:
            list_year_leap_only = get_leap_year(list_year)
            ind_date = get_index_for_other_years(t_units, t, t_calendar, list_year_leap_only, ytd, dt_arr_num)
            ind_2_calc = get_ind_2_calc(i , ind_date, 366, window_wide, ind_ytd_start, bootstrapping)
#            ind_2_calc = get_ind_2_calc(i , ind_date, len_ytd, window_wide, ind_ytd_start, bootstrapping)

        #If only_leap_years is false, we take in account all the year for calculation. See docs for more details
        else:
            list_year_leap_only = get_leap_year(list_year)
            list_year_not_leap = get_non_leap_year(list_year)

            ind_date = get_index_for_other_years(t_units, t, t_calendar, list_year_leap_only, ytd, dt_arr_num)
            ind_2_calc = get_ind_2_calc(i , ind_date, 366, window_wide, ind_ytd_start, bootstrapping)
#            ind_2_calc = get_ind_2_calc(i , ind_date, len_ytd, window_wide, ind_ytd_start, bootstrapping)
            ind_date_not_leap = get_index_for_other_years(t_units, dt_arr[ind_ytd_start+i-1], t_calendar, list_year_not_leap, ytd, dt_arr_num)
#            ind_2_calc_non_leap = get_ind_2_calc_for_non_leap(i, ind_date_not_leap, len_ytd, window_wide)
            ind_2_calc_non_leap = get_ind_2_calc_for_non_leap(i, ind_date_not_leap, 365, window_wide)

            ind_2_calc = np.append(ind_2_calc, ind_2_calc_non_leap)

    #This part returns the indices to calculate when the duplicated year is not leap

    else:
        ind_date = get_index_for_other_years(t_units, t, t_calendar, list_year, ytd, dt_arr_num)
        ind_2_calc = get_ind_2_calc_for_non_leap(i , ind_date, 365, window_wide)

    return ind_2_calc


#Main function to compute the percentile
def return_perc_array_2_compute_bootstrapping(dt_arr, arr_filled, 
                                                    t_units, t_calendar, ytd, window_width, percentile, 
                                                    interpolation, ignore_Feb29th, only_leap_years, bootstrapping):

    #Get time config
    #nc_time = cftime.utime(t_units, t_calendar)

    #From datetime to numerical format
    dt_arr_num = cftime.date2num(dt_arr, t_units, t_calendar)

    #Find first day of ytd in dt_arr_num, make it equel to ind_ytd_start
    if bootstrapping:
        ind_ytd_start = get_first_ytd_day(dt_arr, dt_arr_num, t_units, t_calendar, ytd)
    else:
        ind_ytd_start = 0

    #Get the length of the year depending on the calendar type and 29th Feb option. I.e 360, 365 ot 366 days        
    len_ytd = util_dt.check_calend(t_calendar, ignore_Feb29th)

    #List the year to be computed and duplicated ytd
    list_year = get_list_year(ytd, dt_arr)

    #Width of half of the window
    window_wide = int(window_width/2)

    #Definition of the percentile array to fill and return
    percentile_array = np.zeros((len_ytd, arr_filled.shape[1], arr_filled.shape[2]))

    #Datetime for the first index of the year to duplicate => Starting date
    t = dt_arr[ind_ytd_start]

    if check_leap_day(t_calendar, t, ytd, only_leap_years):
        len_ytd = 366
    else:
        len_ytd = 365

    #variable i to be iterated in the while statement represents each day of the year
    i=0

    #We iterate across day over all year long related to the year length
    while i<len_ytd:

        # t is the centered day which we perform the calculation on
        t = dt_arr[ind_ytd_start+i]

        #ind_2_calc returns the index we want to perform the percentile on
        ind_2_calc = indices_to_return_for_percentile_calc(dt_arr_num, dt_arr, list_year, window_wide, i, len_ytd, ytd, 
                                                            t_units, t_calendar, t, ignore_Feb29th, only_leap_years, bootstrapping,
                                                            ind_ytd_start)

        #Percentile calculation
        percentile_array[i,:,:] = np.percentile(arr_filled[ind_2_calc,:,:], percentile, axis=0, interpolation=interpolation)

        #Iteration
        i+=1

    return percentile_array


### used to get daily percentile thresholds for temperature variables
def get_percentile_dict(arr, dt_arr, percentile, window_width, reduced_base_years_list, ytd,
                        t_calendar, t_units,
                        only_leap_years=False, callback=None, callback_percentage_start_value=0,
                        callback_percentage_total=100, chunk_counter=1, fill_val=None,
                        ignore_Feb29th=False, interpolation='linear', bootstrapping=False):
    '''
    Creates a dictionary with keys=calendar day (month,day) and values=np.ndarray (2D)
    Example - to get the 2D percentile array corresponding to the 15th Mai: percentile_dict[5,15]

    :param arr: array of values
    :type arr: np.ndarray (3D) or np.ma.MaskedArray (3D) of float

    :param dt_arr: corresponding time steps vector (base period: usually 1961-1990)
    :type dt_arr: np.ndarray (1D) of datetime objects

    :param percentile: percentile to compute which must be between 0 and 100 inclusive
    :type percentile: int

    :param window_width: window width, must be odd
    :type window_width: int

    :param ytd: year duplicated
    :type ytd: int

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
    dic_caldays = get_dict_caldays(dt_arr)

    percentile_dict = OrderedDict()
    # we mask our array in case it has fill_values
    arr_masked = get_masked_arr(arr, fill_val)
    in_mask = arr_masked.mask[0, :, :]

    fill_val = arr_masked.fill_value
    arr_filled = arr_masked.filled(fill_val)
    del arr_masked

    ## we check the fill_value (we need it to be the maximum value in the array)
    if fill_val == arr_filled.max():
        pass
    else:
        fill_val_new = 1e+20
        arr_filled[arr_filled==fill_val] = fill_val_new
        fill_val = fill_val_new

    percentile_array = return_perc_array_2_compute_bootstrapping(dt_arr, arr_filled, t_units, t_calendar, ytd, window_width, percentile, interpolation, ignore_Feb29th, only_leap_years, bootstrapping)

    ind_day = 0 

    for month in dic_caldays.keys():
        for day in dic_caldays[month]:
            percentile_dict[month,day] = percentile_array[ind_day,:,:]
            ind_day+=1

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
    :type arr: np.ndarray (3D) or np.ma.MaskedArray (3D) of float

    :param dt_arr: corresponding time steps vector (base period: usually 1961-1990)
    :type dt_arr: np.ndarray (1D) of datetime objects

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

    :rtype: np.ndarray (2D)

    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.

    '''

    assert(arr.ndim == 3)

    in_fill_val = fill_val

    # we mask our array in case it has fill_values
    arr_masked = get_masked_arr(arr, fill_val)
    in_mask = arr_masked.mask[0, :, :]

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
        arr_filled = np.array(arr_filled, dtype='float32')

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

    arr_percentile = np.zeros([arr.shape[1], arr.shape[2]]) # we reserve memory

    # Need a string buffer for Python 3 compatibility.
    b_interpolation = interpolation.encode('utf-8')
    b_interpolation = ctypes.create_string_buffer(b_interpolation)

    # we compute the percentiles
    C_percentile(arr_filled, arr_filled.shape[0], arr_filled.shape[1], arr_filled.shape[2], arr_percentile, percentile, fill_val, b_interpolation)

    arr_percentile = arr_percentile.reshape(arr.shape[1], arr.shape[2])
    arr_percentile_masked = np.ma.masked_array(arr_percentile, in_mask)
    del arr_percentile
    del in_mask

    return arr_percentile_masked
