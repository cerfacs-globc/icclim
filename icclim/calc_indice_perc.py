#  Copyright CERFACS (http://cerfacs.fr/)
#  Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
#
#  Author: Natalia Tatarinova


import numpy

import ctypes
from numpy.ctypeslib import ndpointer
import os
import calc_indice

my_rep = os.path.dirname(os.path.abspath(__file__)) + os.sep

libraryC = ctypes.cdll.LoadLibrary(my_rep+'libC.so')


'''
Elementary functions computing percentile based indices:
- TG10p
- TX10p
- TN10p
- TG90p
- TX90p
- TN90p
- WSDI
- CSDI
- R75p
- R75pTOT
- R95p
- R95pTOT
- R99p
- R99pTOT
- CD
- CW
- WD
- WW
'''

############# utility functions: begin #############
def get_binary_arr(arr1, arr2, logical_operation):
    '''
    Compare "arr1" with "arr2" and return a binary array with the result.
    
    :param arr1: array to comparer with arr2
    :type arr1: numpy.ndarray
    :param arr2: reference array 
    :type arr2: numpy.ndarray
    :rtype: binary numpy.ndarray
    
    ..warning:: "arr1" and "arr2" must have the same shape
    
    '''

    if logical_operation == 'gt':
        binary_arr = arr1 > arr2
        
    elif logical_operation == 'get':
            binary_arr = arr1 >= arr2
            
    elif logical_operation == 'lt':
            binary_arr = arr1 < arr2
            
    elif logical_operation == 'let':
            binary_arr = arr1 <= arr2 
    
    
    binary_arr = binary_arr.astype(int) # True/False ---> 1/0

    # if binary_arr is masked array, we fill masked values with 0
    if isinstance(binary_arr, numpy.ma.MaskedArray):
        binary_arr = binary_arr.filled(0.0)

    
    return binary_arr


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

##### utility function: end #####################

def TXXXp(arr, dt_arr, percentile_dict, logical_operation, fill_val=None, out_unit="days"):
    
    TXXXp = numpy.zeros((arr.shape[1], arr.shape[2]))
    
    arr_masked = get_masked_arr(arr, fill_val)
    
    i=0
    for dt in dt_arr:
        
        # current calendar day
        m = dt.month
        d = dt.day

        # we take the 2D array corresponding to the current calendar day
        current_perc_arr = percentile_dict[m,d]
                    
        # we are looking for the values which are g/ge/l/le than the XXth percentile  
        bin_arr = get_binary_arr(arr_masked[i,:,:], current_perc_arr, logical_operation=logical_operation) 
        TXXXp = TXXXp + bin_arr
        
        i+=1
   
    if out_unit == "days":
        TXXXp = TXXXp
    elif out_unit == "%":
        print len(dt_arr)
        TXXXp = TXXXp*(100./len(dt_arr))
    
    # RESULT must be numpy.ma.MaskedArray if arr is numpy.ma.MaskedArray
    if isinstance(arr, numpy.ma.MaskedArray):
        TXXXp = numpy.ma.array(TXXXp, mask=TXXXp==arr_masked.fill_value, fill_value=arr_masked.fill_value)
        
    return TXXXp  

def WCSDI(arr, dt_arr, percentile_dict, logical_operation, fill_val=None, N=6):
    '''
    Calculate the WSDI/CSDI indice (warm/cold-spell duration index).
    This function calls C function "WSDI_CSDI_3d" from libC.c
 
    '''

 
    arr_masked = get_masked_arr(arr, fill_val)
    
    # step1: we get a 3D binary array from arr (if arr value > corresponding 90th percentile value: 1, else: 0)    
    bin_arr = numpy.zeros((arr.shape[0], arr.shape[1], arr.shape[2]))
    
    i=0
    for dt in dt_arr:
        
        # current calendar day
        m = dt.month
        d = dt.day

        current_perc_arr = percentile_dict[m,d]
        
        # we are looking for the values which are greater than the 90th percentile  
        bin_arr_current_slice = get_binary_arr(arr_masked[i,:,:], current_perc_arr, logical_operation=logical_operation) 
#         bin_arr_current_slice = bin_arr_current_slice.filled(fill_value=0) # we fill the bin_arr_current_slice with zeros
        bin_arr[i,:,:] = bin_arr_current_slice

        i+=1
    
    # step2: now we will pass our 3D binary array (bin_arr) to C function WSDI_CSDI_3d
    
    # array data type should be 'float32' to pass it to C function  
    if bin_arr.dtype != 'float32':
        bin_arr = numpy.array(bin_arr, dtype='float32')
    
    
    WSDI_CSDI_C = libraryC.WSDI_CSDI_3d    
    WSDI_CSDI_C.restype = None
    WSDI_CSDI_C.argtypes = [ndpointer(ctypes.c_float),
                            ctypes.c_int,
                            ctypes.c_int,
                            ctypes.c_int,
                            ndpointer(ctypes.c_double),
                            ctypes.c_int] 
        
    WCSDI = numpy.zeros([arr.shape[1], arr.shape[2]]) # reserve memory
        
    WSDI_CSDI_C(bin_arr, bin_arr.shape[0], bin_arr.shape[1], bin_arr.shape[2], WCSDI, N)
    
    WCSDI = WCSDI.reshape(arr.shape[1], arr.shape[2])
    
    # RESULT must be numpy.ma.MaskedArray if arr is numpy.ma.MaskedArray
    if isinstance(arr, numpy.ma.MaskedArray):
        WCSDI = numpy.ma.array(WCSDI, mask=WCSDI==arr_masked.fill_value, fill_value=arr_masked.fill_value)

    return WCSDI    

def RXXp(arr, dt_arr, percentile_dict, logical_operation='gt', pr_thresh = 1.0, fill_val=None, out_unit="days"):
    '''
    Calculate a RXXp indice, where XX is a percentile value.

    '''
    RXXp = numpy.zeros((arr.shape[1], arr.shape[2]))

    arr_masked = get_masked_arr(arr, fill_val)  # mm/s
    arr_masked = arr_masked*60*60*24            # mm/day
    
    # we need to check only wet days (i.e. days with RR >= 1 mm)
    # so, we mask all values < 1 mm with the same fill_value
    mask_arr_masked = arr_masked < pr_thresh # mask
    arr_masked_masked = numpy.ma.array(arr_masked, mask=mask_arr_masked, fill_value=arr_masked.fill_value)
      
    i=0
    for dt in dt_arr:
        
        # current calendar day
        m = dt.month
        d = dt.day

        current_perc_arr = percentile_dict[m,d]

        # we are looking for the values which are greater than the 75th percentile  
        bin_arr = get_binary_arr(arr_masked_masked[i,:,:], current_perc_arr, logical_operation=logical_operation) 
        RXXp = RXXp + bin_arr
        
        i+=1
     
    if out_unit == "days":
        RXXp = RXXp
    elif out_unit == "%":
        RXXp = RXXp*(100./len(dt_arr))
    
    # RESULT must be numpy.ma.MaskedArray if arr is numpy.ma.MaskedArray
    if isinstance(arr, numpy.ma.MaskedArray):
        RXXp = numpy.ma.array(RXXp, mask=RXXp==arr_masked.fill_value, fill_value=arr_masked.fill_value)
     
    return RXXp    


def RXXpTOT(arr, dt_arr, percentile_dict, logical_operation='let', pr_thresh = 1.0, fill_val=None):
    '''
    Calculate a RXXpTOT indice, where XX is a percentile value.
    '''

    RXXpTOT = numpy.zeros((arr.shape[1], arr.shape[2]))
    
    arr_masked = get_masked_arr(arr, fill_val)  # mm/s
    arr_masked = arr_masked*60*60*24            # mm/day
    
    # we need to check only wet days (i.e. days with RR >= 1 mm)
    # so, we mask all values < 1 mm with the same fill_value
    mask_arr_masked = arr_masked < pr_thresh
    
    arr_masked_masked = numpy.ma.array(arr_masked, mask=mask_arr_masked, fill_value=arr_masked.fill_value)
    
    
    i=0
    for dt in dt_arr:
        
        # current calendar day
        m = dt.month
        d = dt.day
#         print m, d
#         print "arr_masked, thresh=1mm: ", arr_masked_masked[i,:,:]
        
        current_perc_arr = percentile_dict[m,d]
        
#         print "currenct_calday_perc: ", current_perc_arr
        
        # we are looking for the values which are greater than the XXth percentile
        # so, we need first to mask all values <= XXth percentile
        mask = get_binary_arr(arr_masked_masked[i,:,:], current_perc_arr, logical_operation=logical_operation) 
        
#         print "bin array: ", mask
        
        arr_current_slice_masked = numpy.ma.array(arr_masked_masked[i,:,:], mask=mask, fill_value=0.0) # we mask again the arr_masked_masked 
        
#         print "res: ", arr_current_slice_masked
        
        arr_current_slice = arr_current_slice_masked.filled() # filled with 0.0 ==> array with daily precipitation amount >= 1.O mm 
        
#         print "res filled with 0: ", arr_current_slice
        
        RXXpTOT = RXXpTOT + arr_current_slice # sum of all daily precipitation amounts >= 1.O mm
        
#         print "SUM:", RXXpTOT
#         print " "
#         print '===='
#         print " "
        
        i+=1
        
    # RESULT must be numpy.ma.MaskedArray if arr is numpy.ma.MaskedArray

    if isinstance(arr, numpy.ma.MaskedArray):
        RXXpTOT = numpy.ma.array(RXXpTOT, mask=RXXpTOT==arr_masked.fill_value, fill_value=arr_masked.fill_value)
        
    
    return RXXpTOT


def CD_CW_WD_WW(t_arr, t_percentile_dict, t_logical_operation, p_arr, p_percentile_dict, p_logical_operation, dt_arr, 
                pr_thresh = 1.0, fill_val1=None, fill_val2=None, out_unit="days"):
    '''
    Calculates the CD/CW/WD/WW indices.    
    '''
    # we intitialize the indice array
    RESULT = numpy.zeros((t_arr.shape[1], t_arr.shape[2]))
        
    
    # 1) we mask both arrays: t_arr and p_arr
    t_arr_masked = get_masked_arr(t_arr, fill_val1)
    p_arr_masked = get_masked_arr(p_arr, fill_val2)

    # 2) p_arr: mm/s ---> mm/day ; we are looking only for wet days (RR > 1 mm), i.e. we mask values < 1 mm
    p_arr_masked = p_arr_masked*60*60*24            # mm/day
    mask_p_arr = p_arr_masked<pr_thresh
    p_arr_masked_masked = numpy.ma.array(p_arr_masked, mask=mask_p_arr) 

    
    i=0
    for dt in dt_arr:
        
        # current calendar day
        m = dt.month
        d = dt.day
        

        t_current_perc_arr = t_percentile_dict[m,d]
        p_current_perc_arr = p_percentile_dict[m,d]

        # 3) we compare daily mean temperature (t_arr) with its XXth percentile (t_percentile_dict)                   ==> result 1          
        t_bin_arr = get_binary_arr(t_arr_masked[i,:,:], t_current_perc_arr, logical_operation=t_logical_operation) 
        
        # 4) we compare daily precipitation amount at wet day (p_arr) with its XXth percentile (p_percentile_dict)    ==> result 2        
        p_bin_arr = get_binary_arr(p_arr_masked_masked[i,:,:], p_current_perc_arr, logical_operation=p_logical_operation) 
    
        # 5) result 1 AND result 2 ==> RESULT        
        t_bin_arr_AND_p_bin_arr = numpy.logical_and(t_bin_arr, p_bin_arr) # masked array              
        #t_bin_arr_AND_p_bin_arr_filled = t_bin_arr_AND_p_bin_arr.filled(fill_value=0)
        
#         RESULT = RESULT + t_bin_arr_AND_p_bin_arr_filled
        RESULT = RESULT + t_bin_arr_AND_p_bin_arr
        
        i+=1
    
    
    if out_unit == "days":
        RESULT = RESULT
    elif out_unit == "%":
        RESULT = RESULT*(100./len(dt_arr))
    
    # RESULT must be numpy.ma.MaskedArray if arr is numpy.ma.MaskedArray
    if isinstance(t_arr, numpy.ma.MaskedArray):
        RESULT = numpy.ma.array(RESULT, mask=RESULT==t_arr_masked.fill_value, fill_value=t_arr_masked.fill_value)
    
    
    return RESULT


##########################################


def TG90p_calculation(arr, dt_arr, percentile_dict, fill_val=None, out_unit="days"):
    '''
    Calculate the TG90p indice: number of warm days (i.e. days with daily mean temperature > 90th percentile of daily mean temperature in the base period).
    
    :param arr: daily mean temperature (e.g. "tas")
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param dt_arr: corresponding time steps vector
    :type dt_arr: numpy.ndarray (1D) of datetime objects
    :param percentile_dict: 90th percentile of daily mean temperature 
    :type percentile_dict: dict
    :param fill_val: fill value
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
        or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)    
    
    .. warning:: Units of "arr" and percentile values of "percentile_dict" must be the same.
    
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.

    '''

    TG90p = TXXXp(arr, dt_arr, percentile_dict, logical_operation='gt', fill_val=fill_val, out_unit=out_unit)    
    
    return TG90p


def TX90p_calculation(arr, dt_arr, percentile_dict, fill_val=None, out_unit="days"):
    '''
    Calculate the TX90p indice: number of warm days-times (i.e. days with daily max temperature > 90th percentile of daily max temperature in the base period).
    
    :param arr: daily max temperature (e.g. "tasmax")
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param dt_arr: corresponding time steps vector
    :type dt_arr: numpy.ndarray (1D) of datetime objects
    :param percentile_dict: 90th percentile of daily max temperature 
    :type percentile_dict: dict
    :param fill_val: fill value
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
        or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)     
    
    .. warning:: Units of "arr" and percentile values of "percentile_dict" must be the same.
    
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.

    '''

    TX90p = TXXXp(arr, dt_arr, percentile_dict, logical_operation='gt', fill_val=fill_val, out_unit=out_unit) 
    
    return TX90p
    

def TN90p_calculation(arr, dt_arr, percentile_dict, fill_val=None, out_unit="days"):
    '''
    Calculate the TN90p indice: number of warm nights (i.e. days with daily min temperature > 90th percentile of daily min temperature in the base period).
    
    :param arr: daily min temperature (e.g. "tasmin")
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param dt_arr: corresponding time steps vector
    :type dt_arr: numpy.ndarray (1D) of datetime objects
    :param percentile_dict: 90th percentile of daily min temperature 
    :type percentile_dict: dict
    :param fill_val: fill value
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
        or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)   
    
    .. warning:: Units of "arr" and percentile values of "percentile_dict" must be the same.
    
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.

    '''

    TN90p = TXXXp(arr, dt_arr, percentile_dict, logical_operation='gt', fill_val=fill_val, out_unit=out_unit)
    
    return TN90p    


    
    
def TG10p_calculation(arr, dt_arr, percentile_dict, fill_val=None, out_unit="days"):
    '''
    Calculate the TG10p indice: number of cold days (i.e. days with daily mean temperature < 10th percentile of daily mean temperature in the base period).
    
    :param arr: daily mean temperature (e.g. "tas")
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param dt_arr: corresponding time steps vector
    :type dt_arr: numpy.ndarray (1D) of datetime objects
    :param percentile_dict: 10th percentile of daily mean temperature 
    :type percentile_dict: dict
    :param fill_val: fill value
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
        or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)        
    
    .. warning:: Units of "arr" and percentile values of "percentile_dict" must be the same.
    
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.

    '''

    TG10p = TXXXp(arr, dt_arr, percentile_dict, logical_operation='lt', fill_val=fill_val, out_unit=out_unit)
    
    return TG10p      
    
    
    
def TX10p_calculation(arr, dt_arr, percentile_dict, fill_val=None, out_unit="days"):
    '''
    Calculate the TX10p indice: number of cold day-times (i.e. days with daily max temperature < 10th percentile of daily max temperature in the base period).
    
    :param arr: daily max temperature (e.g. "tasmax")
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param dt_arr: corresponding time steps vector
    :type dt_arr: numpy.ndarray (1D) of datetime objects
    :param percentile_dict: 10th percentile of daily max temperature 
    :type percentile_dict: dict
    :param fill_val: fill value
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
        or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)        
    
    .. warning:: Units of "arr" and percentile values of "percentile_dict" must be the same.
    
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.

    '''

    TX10p = TXXXp(arr, dt_arr, percentile_dict, logical_operation='lt', fill_val=fill_val, out_unit=out_unit)  
    
    return TX10p      
    

def TN10p_calculation(arr, dt_arr, percentile_dict, fill_val=None, out_unit="days"):
    '''
    Calculate the TN10p indice: number of cold nights (i.e. days with daily min temperature < 10th percentile of daily min temperature in the base period).
    
    :param arr: daily min temperature (e.g. "tasmin")
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param dt_arr: corresponding time steps vector
    :type dt_arr: numpy.ndarray (1D) of datetime objects
    :param percentile_dict: 10th percentile of daily min temperature 
    :type percentile_dict: dict
    :param fill_val: fill value
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
        or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)      
    '''
    
    #.. warning:: Units of "arr" and percentile values of "percentile_dict" must be the same.
    #
    #.. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.


    TN10p = TXXXp(arr, dt_arr, percentile_dict, logical_operation='lt', fill_val=fill_val, out_unit=out_unit)   
    
    return TN10p    


def WSDI_calculation(arr, dt_arr, percentile_dict, fill_val=None, N=6, out_unit="days"):
    '''
    Calculate the WSDI indice (warm-spell duration index): number of days where, in intervals of at least 6 consecutive days, 
    daily max temperature > 90th percentile of daily max temperature in the base period).
    
    :param arr: daily max temperature (e.g. "tasmax")
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param dt_arr: corresponding time steps vector
    :type dt_arr: numpy.ndarray (1D) of datetime objects
    :param percentile_dict: 90th percentile of daily max temperature 
    :type percentile_dict: dict
    :param fill_val: fill value
    :type fill_val: float
    :param N: number of consecutive days (default: 6)
    :type N: int
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
        or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)      
    '''
    
        
    #.. warning:: Units of "arr" and percentile values of "percentile_dict" must be the same.
    #
    #.. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
 
        
    WSDI = WCSDI(arr, dt_arr, percentile_dict, logical_operation='gt', fill_val=fill_val, N=6)

    return WSDI 


def CSDI_calculation(arr, dt_arr, percentile_dict, fill_val=None, N=6, out_unit="days"):
    '''
    Calculate the CSDI indice (cold-spell duration index): number of days where, in intervals of at least 6 consecutive days, 
    daily min temperature < 10th percentile of daily min temperature in the base period).    
    
    :param arr: daily min temperature (e.g. "tasmin")
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param dt_arr: corresponding time steps vector
    :type dt_arr: numpy.ndarray (1D) of datetime objects
    :param percentile_dict: 10th percentile of daily max temperature 
    :type percentile_dict: dict
    :param fill_val: fill value
    :type fill_val: float
    :param N: number of consecutive days (default: 6)
    :type N: int
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
        or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)       
    
    .. warning:: Units of "arr" and percentile values of "percentile_dict" must be the same.
    
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.

    '''
     
    CSDI = WCSDI(arr, dt_arr, percentile_dict, logical_operation='lt', fill_val=fill_val, N=6)

    return CSDI

    

def R75p_calculation(arr, dt_arr, percentile_dict, pr_thresh = 1.0, fill_val=None, out_unit="days"):
    '''
    Calculate the R75p indice: number of moderate wet days (i.e. days with daily precipitation amount > 75th percentile of daily amount in the base period).
    
    :param arr: daily precipitation flux (liquid form) (e.g. "pr") in mm/s
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param dt_arr: corresponding time steps vector
    :type dt_arr: numpy.ndarray (1D) of datetime objects
    :param percentile_dict: 75th percentile of daily precipitation amount at wet days in mm/day
    :type percentile_dict: dict
    :param pr_thresh: precipitation threshold (default: 1.0 mm)
    :type pr_thresh: float
    :param fill_val: fill value
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
        or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)       
    
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.

    '''
    R75p = RXXp(arr, dt_arr, percentile_dict, logical_operation='gt', pr_thresh = 1.0, fill_val=fill_val, out_unit=out_unit)
    
    return R75p    


def R95p_calculation(arr, dt_arr, percentile_dict, fill_val=None, out_unit="days"):
    '''
    Calculate the R95p indice: number of very wet days (i.e. days with daily precipitation amount > 95th percentile of daily amount in the base period).
    
    :param arr: daily precipitation flux (liquid form) (e.g. "pr") in mm/s
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param dt_arr: corresponding time steps vector
    :type dt_arr: numpy.ndarray (1D) of datetime objects
    :param percentile_dict: 95th percentile of daily precipitation amount at wet days in mm/day
    :type percentile_dict: dict
    :param fill_val: fill value
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
        or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)       
    
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.

    '''
    R95p = RXXp(arr, dt_arr, percentile_dict, logical_operation='gt', pr_thresh = 1.0, fill_val=fill_val, out_unit=out_unit)  

    return R95p


def R99p_calculation(arr, dt_arr, percentile_dict, fill_val=None, out_unit="days"):
    '''
    Calculate the R99p indice: number of extremely wet days (i.e. days with daily precipitation amount > 99th percentile of daily amount in the base period).
    
    :param arr: daily precipitation flux (liquid form) (e.g. "pr") in mm/s
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param dt_arr: corresponding time steps vector
    :type dt_arr: numpy.ndarray (1D) of datetime objects
    :param percentile_dict: 99th percentile of daily precipitation amount at wet days in mm/day
    :type percentile_dict: dict
    :param fill_val: fill value
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
        or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)       

    
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.

    '''
    R99p = RXXp(arr, dt_arr, percentile_dict, logical_operation='gt', pr_thresh = 1.0, fill_val=fill_val, out_unit=out_unit) 
    
    return R99p


def R75pTOT_calculation(arr, dt_arr, percentile_dict, fill_val=None, out_unit=None):
    '''
    Calculate the R75pTOT indice: precipitation fraction due to moderate wet days (i.e. days with daily precipitation amount > 75th percentile of daily amount in the base period) [%]
    
    :param arr: daily precipitation flux (liquid form) (e.g. "pr") in mm/s
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param dt_arr: corresponding time steps vector
    :type dt_arr: numpy.ndarray (1D) of datetime objects
    :param percentile_dict: 75th percentile of daily precipitation amount at wet days in mm/day
    :type percentile_dict: dict
    :param fill_val: fill value
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
        or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)
    
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.

    '''
    
    R75pTOT = RXXpTOT(arr, dt_arr, percentile_dict, logical_operation='let', pr_thresh = 1.0, fill_val=fill_val)
    
    return R75pTOT
    

def R95pTOT_calculation(arr, dt_arr, percentile_dict, fill_val=None, out_unit=None):
    '''
    Calculate the R95pTOT indice: precipitation fraction due to very wet days (i.e. days with daily precipitation amount > 95th percentile of daily amount in the base period) [%]
    
    :param arr: daily precipitation flux (liquid form) (e.g. "pr") in mm/s
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param dt_arr: corresponding time steps vector
    :type dt_arr: numpy.ndarray (1D) of datetime objects
    :param percentile_dict: 95th percentile of daily precipitation amount at wet days in mm/day
    :type percentile_dict: dict
    :param fill_val: fill value
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
        or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)
    
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.

    '''
       
    R95pTOT = RXXpTOT(arr, dt_arr, percentile_dict, logical_operation='let', pr_thresh = 1.0, fill_val=fill_val)
    
    return R95pTOT

def R99pTOT_calculation(arr, dt_arr, percentile_dict, fill_val=None, out_unit=None):
    '''
    Calculate the R99pTOT indice: precipitation fraction due to extremely wet days (i.e. days with daily precipitation amount > 99th percentile of daily amount in the base period) [%]
    
    :param arr: daily precipitation flux (liquid form) (e.g. "pr") in mm/s
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param dt_arr: corresponding time steps vector
    :type dt_arr: numpy.ndarray (1D) of datetime objects
    :param percentile_dict: 99th percentile of daily precipitation amount at wet days in mm/day
    :type percentile_dict: dict
    :param fill_val: fill value
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
        or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)
    
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.

    '''
        
    R99pTOT = RXXpTOT(arr, dt_arr, percentile_dict, logical_operation='let', pr_thresh = 1.0, fill_val=fill_val)
    
    return R99pTOT


def CD_calculation(t_arr, t_25th_percentile_dict, p_arr, p_25th_percentile_dict, dt_arr, fill_val1=None, fill_val2=None, out_unit="days"):
    '''
    Calculate the CD indice: number of cold and dry days.
    
    :param t_arr: daily mean temperature (e.g. "tas")
    :type t_arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param t_25th_percentile_dict: 25th percentile of daily min temperature
    :type t_25th_percentile_dict: dict
    :param p_arr: daily precipitation amount at wet day (RR >= 1.0 mm) (e.g. "pr") in mm/s
    :type p_arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param p_25th_percentile_dict: 25th percentile of daily precipitation amount at wet days in mm/day
    :type p_25th_percentile_dict: dict
    :param dt_arr: time steps vector corresponding to both input arrays (``t_arr`` and ``dt_arr``) 
    :type dt_arr: numpy.ndarray (1D) of datetime objects
    :param fill_val1: fill value of t_arr
    :type fill_val1: float
    :param fill_val2: fill value of p_arr
    :type fill_val2: float   
    
    :rtype: numpy.ndarray (2D)        (if ``t_arr`` and ``p_arr`` is numpy.ndarray) or numpy.ma.MaskedArray (2D) (if ``t_arr`` and ``p_arr`` is numpy.ma.MaskedArray)
    
    .. warning:: If "t_arr" and "p_arr" are masked arrays, the parameters "fill_val1" and "fill_val2" are ignored, because they have no sense in this case.
    
    .. note:: Both input array must be the same type.
    
    '''

    CD = CD_CW_WD_WW(t_arr=t_arr, t_percentile_dict=t_25th_percentile_dict, t_logical_operation='lt', 
                     p_arr=p_arr, p_percentile_dict=p_25th_percentile_dict, p_logical_operation='lt', 
                     dt_arr=dt_arr, pr_thresh = 1.0, fill_val1=fill_val1, fill_val2=fill_val2, out_unit=out_unit)
    
    return CD


def CW_calculation(t_arr, t_25th_percentile_dict, p_arr, p_75th_percentile_dict, dt_arr, fill_val1=None, fill_val2=None, out_unit="days"):
    '''
    Calculate the CW indice: number of cold and wet days.
    
    :param t_arr: daily mean temperature (e.g. "tas")
    :type t_arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param t_25th_percentile_dict: 25th percentile of daily min temperature
    :type t_25th_percentile_dict: dict
    :param p_arr: daily precipitation amount at wet day (RR >= 1.0 mm) (e.g. "pr") in mm/s
    :type p_arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param p_75th_percentile_dict: 75th percentile of daily precipitation amount at wet days in mm/day
    :type p_75th_percentile_dict: dict
    :param dt_arr: time steps vector corresponding to both input arrays (``t_arr`` and ``dt_arr``) 
    :type dt_arr: numpy.ndarray (1D) of datetime objects
    :param fill_val1: fill value of t_arr
    :type fill_val1: float
    :param fill_val2: fill value of p_arr
    :type fill_val2: float 
    
    :rtype: numpy.ndarray (2D)        (if ``t_arr`` and ``p_arr`` is numpy.ndarray) or numpy.ma.MaskedArray (2D) (if ``t_arr`` and ``p_arr`` is numpy.ma.MaskedArray)
    
    .. warning:: If "t_arr" and "p_arr" are masked arrays, the parameters "fill_val1" and "fill_val2" are ignored, because they have no sense in this case.
    
    .. note:: Both input array must be the same type.
    
    '''

    CW = CD_CW_WD_WW(t_arr=t_arr, t_percentile_dict=t_25th_percentile_dict, t_logical_operation='lt', 
                     p_arr=p_arr, p_percentile_dict=p_75th_percentile_dict, p_logical_operation='gt', 
                     dt_arr=dt_arr, pr_thresh = 1.0, fill_val1=fill_val1, fill_val2=fill_val2, out_unit=out_unit)
  
    
    return CW



def WD_calculation(t_arr, t_75th_percentile_dict, p_arr, p_25th_percentile_dict, dt_arr, fill_val1=None, fill_val2=None, out_unit="days"):
    '''
    Calculate the WD indice: number of warm and dry days.
    
    :param t_arr: daily mean temperature (e.g. "tas")
    :type t_arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param t_75th_percentile_dict: 75th percentile of daily min temperature
    :type t_75th_percentile_dict: dict
    :param p_arr: daily precipitation amount at wet day (RR >= 1.0 mm) (e.g. "pr") in mm/s
    :type p_arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param p_25th_percentile_dict: 25th percentile of daily precipitation amount at wet days in mm/day
    :type p_25th_percentile_dict: dict
    :param dt_arr: time steps vector corresponding to both input arrays (``t_arr`` and ``dt_arr``) 
    :type dt_arr: numpy.ndarray (1D) of datetime objects
    :param fill_val1: fill value of t_arr
    :type fill_val1: float
    :param fill_val2: fill value of p_arr
    :type fill_val2: float 
    
    :rtype: numpy.ndarray (2D)        (if ``t_arr`` and ``p_arr`` is numpy.ndarray) or numpy.ma.MaskedArray (2D) (if ``t_arr`` and ``p_arr`` is numpy.ma.MaskedArray)
    
    .. warning:: If "t_arr" and "p_arr" are masked arrays, the parameters "fill_val1" and "fill_val2" are ignored, because they have no sense in this case.
    
    .. note:: Both input array must be the same type.
    
    '''

    WD = CD_CW_WD_WW(t_arr=t_arr, t_percentile_dict=t_75th_percentile_dict, t_logical_operation='gt', 
                     p_arr=p_arr, p_percentile_dict=p_25th_percentile_dict, p_logical_operation='lt', 
                     dt_arr=dt_arr, pr_thresh = 1.0, fill_val1=fill_val1, fill_val2=fill_val2, out_unit=out_unit)
    
    return WD


def WW_calculation(t_arr, t_75th_percentile_dict, p_arr, p_75th_percentile_dict, dt_arr, fill_val1=None, fill_val2=None, out_unit="days"):
    '''
    Calculate the WW indice: number of warm and wet days.
    
    :param t_arr: daily mean temperature (e.g. "tas")
    :type t_arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param t_75th_percentile_dict: 75th percentile of daily min temperature
    :type t_75th_percentile_dict: dict
    :param p_arr: daily precipitation amount at wet day (RR >= 1.0 mm) (e.g. "pr") in mm/s
    :type p_arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param p_75th_percentile_dict: 75th percentile of daily precipitation amount at wet days in mm/day
    :type p_75th_percentile_dict: dict
    :param dt_arr: time steps vector corresponding to both input arrays (``t_arr`` and ``dt_arr``) 
    :type dt_arr: numpy.ndarray (1D) of datetime objects
    :param fill_val1: fill value of t_arr
    :type fill_val1: float
    :param fill_val2: fill value of p_arr
    :type fill_val2: float 
    
    :rtype: numpy.ndarray (2D)        (if ``t_arr`` and ``p_arr`` is numpy.ndarray) or numpy.ma.MaskedArray (2D) (if ``t_arr`` and ``p_arr`` is numpy.ma.MaskedArray)
    
    .. warning:: If "t_arr" and "p_arr" are masked arrays, the parameters "fill_val1" and "fill_val2" are ignored, because they have no sense in this case.
    
    .. note:: Both input array must be the same type.
    
    '''

    WW = CD_CW_WD_WW(t_arr=t_arr, t_percentile_dict=t_75th_percentile_dict, t_logical_operation='gt', 
                     p_arr=p_arr, p_percentile_dict=p_75th_percentile_dict, p_logical_operation='gt', 
                     dt_arr=dt_arr, pr_thresh = 1.0, fill_val1=fill_val1, fill_val2=fill_val2, out_unit=out_unit)
        
    return WW