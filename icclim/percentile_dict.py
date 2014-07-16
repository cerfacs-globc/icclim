import numpy
from datetime import datetime
from collections import OrderedDict, defaultdict
from time import time
import calendar
from netcdftime import utime

############### utility functions: begin ################## 

def num2date(num, calend, units):
    '''
    Converts numerical date to datetime object.    
    
    :param num: numerical date
    :type num: float
    :param calend: calendar attribute of variable "time" in netCDF file
    :type calend: str
    :param units: units of variable "time" in netCDF file
    :type units: str
    
    :rtype: datetime object
    '''   
    t = utime(units, calend) 
    dt = t.num2date(num) 
    return dt


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



    
def get_masked(current_date, month, day, hour, window_width, only_leap_years): 

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
        toReturn = diff > window_width/2
        
    return toReturn


def get_mask_dt_arr(dt_arr, month, day, dt_hour, window_width, only_leap_years):
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
    mask = numpy.array([get_masked(dt, month, day, dt_hour, window_width, only_leap_years) for dt in dt_arr])
    return mask


def get_year_list(dt_arr):
    '''
    Just to get a list of all years conteining in time steps vector (dt_arr).
    '''

    year_list = []
    for dt in dt_arr:
        year_list.append(dt.year)
        
    year_list = list(set(year_list))
    
    return year_list


############### utility functions: end ##################




def get_percentile_dict(arr, dt_arr, percentile, window_width, only_leap_years=False):
    '''
    Creates a dictionary with keys=calendar day (month,day) and values=numpy.ndarray (2D)
    Example - to get the 2D percentile array corresponding to the 15th Mai: percentile_dict[5,15]
    
    :param arr: array of values
    :type arr: numpy.ndarray (3D) of float
    :param dt_arr: corresponding time steps vector (base period: usually 1961-1990)
    :type dt_arr: numpy.ndarray (1D) of datetime objects
    :param percentile: percentile to compute which must be between 0 and 100 inclusive
    :type percentile: int
    :param window_width: window width, must be odd
    :type window_width: int
    :param only_leap_years: option for February 29th (default: False)
    :type only_leap_years: bool
    
    :rtype: dict

    
    '''
    
    # step1: creation of the dictionary with all calendar days:
    dic_caldays = get_dict_caldays(dt_arr)

    percentile_dict = OrderedDict()
    
    dt_hour = dt_arr[0].hour # (we get hour of a date only one time, because usually the hour is the same for all dates in input dt_arr)
    
    for month in dic_caldays.keys():
        for day in dic_caldays[month]:
            
            # step2: we do a mask for the datetime vector for current calendar day (day/month)
            dt_arr_mask = get_mask_dt_arr(dt_arr, month, day, dt_hour, window_width, only_leap_years)

            # step3: we are looking for the indices of non-masked dates (i.e. where dt_arr_mask==False) 
            indices_non_masked = numpy.where(dt_arr_mask==False)[0]
            
            # step4: we subset our arr
            arr_subset = arr[indices_non_masked, :, :].squeeze()
            
            # step5: we compute the percentile for current arr_subset
            ############## WARNING: type(arr_subset) = numpy.ndarray. Numpy.percentile does not work with masked arrays,
            ############## so if arr_subset has aberrant values like 999999 or 1e+20, the result will be wrong.
            ############## Check with numpy.nanpercentile (Numpy version 1.9) !!!            
            arr_percentille_current_calday = numpy.percentile(arr_subset, percentile, axis=0)
            
            # step6: we add to the dictionnary...
            percentile_dict[month,day] = arr_percentille_current_calday
            
        print 'Creating percentile dictionary: month ', month, '---> OK'
    
    print 'Percentile dictionary is created.'
    
    return percentile_dict





