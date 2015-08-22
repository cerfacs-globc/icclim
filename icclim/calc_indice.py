# -*- coding: latin-1 -*-

#  Copyright CERFACS (http://cerfacs.fr/)
#  Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
#
#  Author: Natalia Tatarinova

import numpy

import ctypes
from numpy.ctypeslib import ndpointer
import os

my_rep = os.path.dirname(os.path.abspath(__file__)) + os.sep

libraryC = ctypes.cdll.LoadLibrary(my_rep+'libC.so')

'''
Elementary functions computing climate indices:
- TG
- TX
- TN
- TXx
- TNx
- TXn
- TNn
- DTR
- ETR
- vDTR
- SU
- CSU
- TR
- FD
- CFD
- ID
- HD17
- GD4
- PRCPTOT
- RR1
- SDII
- R10mm
- R20mm
- RX1day
- CDD
- CWD
- SD
- SD1
- SD5cm
- SD50cm
'''


'''
Statistics elementary functions
- TIMEAVG
- SUB
'''


'''
Note: these functions maniputate 3D arrays - usual (numpy.ndarray) or masked (numpy.ma.MaskedArray).
Return type: the same type as the type of input array(s)

Note: A function name is composed from an indice name and "_calculation" (example: FD_calculation).

Example of function calling:
        1. if input array is an usual array (numpy.ndarray), a fill_value must be provided: FD_calculation(my_3D_array, fill_val=99999)
        2. if input array is a masked array (numpy.ma.MaskedArray): FD_calculation(my_3D_masked_array)

Note:
- 4 functions (CSU, CFD, CDD, CWD):
        1) transforming input array into usual array (numpy.ndarray)
        2) C function: processing -> result: usual array
        3) if input array is masked array: transforming the result into a masked array

- other functions:
        1) transforming input array into masked array (numpy.ma.MaskedArray)
        2) processing -> result: masked array
        3) if input array is usual array: transforming the result into usual array


'''



##### utility function (begin) #####
def get_binary_arr(arr1, arr2, logical_operation):
    '''
    Compare "arr1" with "arr2" and return a binary array with the result.
    
    :param arr1: array to comparer with arr2
    :type arr1: numpy.ndarray
    :param arr2: reference array or threshold 
    :type arr2: numpy.ndarray or float or int
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

##### utility function (end) #####

def simple_stat(arr, stat_operation, coef=1.0, fill_val=None, thresh=None, logical_operation='lt'):
    
    '''    
    Used for computing: TG, TX, TN, TXx, TNx, TXn, TNn, PRCPTOT, SD    
    '''
    
    arr_masked = get_masked_arr(arr, fill_val)*coef                # numpy.ma.MaskedArray with fill_value=fill_val (if numpy.ndarray passed) or fill_value=arr.fill_value (if numpy.ma.MaskedArray is passed)
    
    if thresh != None:
        if logical_operation=='gt':
            mask_a = arr_masked > thresh
        elif logical_operation=='get':
            mask_a = arr_masked >= thresh
        elif logical_operation=='lt':
            mask_a = arr_masked < thresh
        if logical_operation=='let':
            mask_a = arr_masked <= thresh
        
        arr_masked = numpy.ma.array(arr_masked, mask=mask_a, fill_value=arr_masked.fill_value)
    
    
    if stat_operation=="mean":
        RESULT = arr_masked.mean(axis=0)                              # fill_value is changed: RESULT is a new numpy.ma.MaskedArray with default fill_value=999999 (!) => next line is to keep the fill_value of arr_masked
    elif stat_operation=="min":
        RESULT = arr_masked.min(axis=0)                              # fill_value is changed: RESULT is a new numpy.ma.MaskedArray with default fill_value=999999 (!) => next line is to keep the fill_value of arr_masked
    elif stat_operation=="max":
        RESULT = arr_masked.max(axis=0)                              # fill_value is changed: RESULT is a new numpy.ma.MaskedArray with default fill_value=999999 (!) => next line is to keep the fill_value of arr_masked
    elif stat_operation=="sum":
        RESULT = arr_masked.sum(axis=0)                              # fill_value is changed: RESULT is a new numpy.ma.MaskedArray with default fill_value=999999 (!) => next line is to keep the fill_value of arr_masked

    numpy.ma.set_fill_value(RESULT, arr_masked.fill_value)
    
    if not isinstance(arr, numpy.ma.MaskedArray):
        RESULT = RESULT.filled(fill_value=arr_masked.fill_value)      # numpy.ndarray filled with input fill_val
    
    return RESULT


def get_nb_days(arr, thresh, logical_operation, coef=1.0, fill_val=None):
    '''
    Used for computing: SU, TR, FD, ID, RR1, R10mm, R20mm, SD1, SD5cm, SD50cm
    
    :param thresh: temperature or precipitation threshold (must be the same unit as arr) 
    :type thresh: float
    '''
    
    arr_masked = get_masked_arr(arr, fill_val)
    arr_masked = arr_masked * coef
    arr_bin = get_binary_arr(arr_masked, thresh, logical_operation) # numpy.ndarray
    RESULT = arr_bin.sum(axis=0) # numpy.ndarray                    
    
    # RESULT must be numpy.ma.MaskedArray if arr is numpy.ma.MaskedArray
    if isinstance(arr, numpy.ma.MaskedArray):
        RESULT = numpy.ma.array(RESULT, mask=RESULT==arr_masked.fill_value, fill_value=arr_masked.fill_value)
    
    return RESULT



def get_max_nb_consecutive_days(arr, thresh, logical_operation, coef=1.0, fill_val=None):

    '''
    Used for computing: CSU, CFD, CDD, CWD
    '''
    
    arr_masked = get_masked_arr(arr, fill_val)
    arr_masked = arr_masked * coef
    arr_demasked = arr_masked.filled(fill_value=arr_masked.fill_value)
    
    ######

        
    # array data type should be 'float32' to pass it to C function  
    if arr_demasked.dtype != 'float32':
        arr_demasked = numpy.array(arr_demasked, dtype='float32')
    
    C_find_max_len_consec_sequence_3d = libraryC.find_max_len_consec_sequence_3d
    C_find_max_len_consec_sequence_3d.restype = None
    C_find_max_len_consec_sequence_3d.argtypes = [ndpointer(ctypes.c_float),
                                                    ctypes.c_int,
                                                    ctypes.c_int,
                                                    ctypes.c_int,
                                                    ndpointer(ctypes.c_double),
                                                    ctypes.c_float,
                                                    ctypes.c_float,
                                                    ctypes.c_char_p] 
    
    RESULT = numpy.zeros([arr_demasked.shape[1], arr_demasked.shape[2]]) # reserve memory
    
    C_find_max_len_consec_sequence_3d(arr_demasked, arr_demasked.shape[0], arr_demasked.shape[1], arr_demasked.shape[2], RESULT, thresh, fill_val, logical_operation)
    RESULT = RESULT.reshape(arr_demasked.shape[1], arr_demasked.shape[2])
    
    # RESULT must be numpy.ma.MaskedArray if arr is numpy.ma.MaskedArray
    if isinstance(arr, numpy.ma.MaskedArray):
        RESULT = numpy.ma.array(RESULT, mask=RESULT==arr_masked.fill_value, fill_value=arr_masked.fill_value)

    return RESULT 





######### temperature indices

def TG_calculation(arr, fill_val=None):
    
    '''    
    Calculates the TG indice: mean of daily mean temperature.
    
    :param arr: daily mean temperature (e.g. "tas")
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value  
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)
         
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.    
    '''
    
    TG = simple_stat(arr, stat_operation="mean", fill_val=fill_val)
    
    return TG


def TN_calculation(arr, fill_val=None):
    
    '''    
    Calculates the TN indice: mean of daily minimum temperature.
    
    :param arr: daily min temperature (e.g. "tasmin")
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)
         
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''
    
    TN = simple_stat(arr, stat_operation="mean", fill_val=fill_val)     
    
    return TN


def TX_calculation(arr, fill_val=None):
    
    '''    
    Calculates the TX indice: mean of daily maximum temperature.
    
    :param arr: daily max temperature (e.g. "tasmax")
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)
         
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''
    
    TX = simple_stat(arr, stat_operation="mean", fill_val=fill_val)     
    
    return TX


def TXx_calculation(arr, fill_val=None):
    
    '''    
    Calculates the TXx indice: maximum of daily maximum temperature.
    
    :param arr: daily max temperature (e.g. "tasmax")
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)
         
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''
    
    TXx = simple_stat(arr, stat_operation="max", fill_val=fill_val)      
    
    return TXx


def TNx_calculation(arr, fill_val=None):
    
    '''    
    Calculates the TNx indice: maximum of daily minimum temperature.
    
    :param arr: daily min temperature (e.g. "tasmin")
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)
    '''     
    #.. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    
    
    TNx = simple_stat(arr, stat_operation="max", fill_val=fill_val)     
    
    return TNx


def TXn_calculation(arr, fill_val=None):
    
    '''    
    Calculates the TXn indice: minimum of daily maximum temperature.
    
    :param arr: daily max temperature (e.g. "tasmax")
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)
         
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''
    
    TXn = simple_stat(arr, stat_operation="min", fill_val=fill_val)     
    
    return TXn


def TNn_calculation(arr, fill_val=None):
    
    '''    
    Calculates the TNn indice: minimum of daily minimum temperature.
    
    :param arr: daily min temperature (e.g. "tasmin")
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)
         
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''
    
    TNn = simple_stat(arr, stat_operation="min", fill_val=fill_val)      
    
    return TNn


def DTR_calculation(arr1, arr2, fill_val1=None, fill_val2=None):
    
    '''    
    Calculates the DTR indice: mean of daily temperature range.
    
    :param arr1: daily max temperature (e.g. "tasmax")
    :type arr1: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param arr2: daily min temperature (e.g. "tasmin")
    :type arr2: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D) 
    
    :param fill_val1: fill value of arr1 
    :type fill_val1: float
    :param fill_val2: fill value of arr2 
    :type fill_val2: float
    
    :rtype: numpy.ndarray (2D)        (if "arr1" and "arr2" are numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr1" and "arr2" are numpy.ma.MaskedArray)

    .. warning:: "arr1" and "arr2" must be the same type, shape and correspond to the same time step vector.
    
    '''
    #.. warning:: If "arr1" and "arr2" are masked arrays, the parameters "fill_val1" and "fill_val2" are ignored, because they have no sense in this case.
      
    arr1_masked = get_masked_arr(arr1, fill_val1)
    arr2_masked = get_masked_arr(arr2, fill_val2)
    
    range_ = arr1_masked - arr2_masked                              # masked array with fill_value = fill_value of the first masked array in expression (i.e. arr1_masked)
    DTR = range_.mean(axis=0)                           # masked array with new fill_value
    numpy.ma.set_fill_value(DTR, arr1_masked.fill_value)      # we set a fill_value = fill_value of arr1_masked (or arr2_masked) 
    
    if not isinstance(arr1, numpy.ma.MaskedArray) :     # or if not isinstance(arr2, numpy.ma.MaskedArray) [because the both input arrays are the same type]
        DTR = DTR.filled(fill_value=arr1_masked.fill_value)      
    
    return DTR    
    
    
def ETR_calculation(arr1, arr2, fill_val1=None, fill_val2=None):
    
    '''    
    Calculates the ETR indice: intra-period extreme temperature range.
    
    :param arr1: daily max temperature (e.g. "tasmax")
    :type arr1: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param arr2: daily min temperature (e.g. "tasmin")
    :type arr2: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D) 
    
    :param fill_val1: fill value of arr1 
    :type fill_val1: float
    :param fill_val2: fill value of arr2 
    :type fill_val2: float
    
    :rtype: numpy.ndarray (2D)        (if "arr1" and "arr2" are numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr1" and "arr2" are numpy.ma.MaskedArray)
         
    .. warning:: If "arr1" and "arr2" are masked arrays, the parameters "fill_val1" and "fill_val2" are ignored, because they have no sense in this case.
    
    .. warning:: "arr1" and "arr2" must be the same type, shape and correspond to the same time step vector.
    
    '''  
    
    arr1_masked = get_masked_arr(arr1, fill_val1)
    arr2_masked = get_masked_arr(arr2, fill_val2)
    
    max_arr1_masked = arr1_masked.max(axis=0)   # masked array with new fill_value (default)
    min_arr2_masked = arr2_masked.min(axis=0)   # masked array with new fill_value (default)
    ETR = max_arr1_masked - min_arr2_masked     # masked array with new fill_value (default)
    numpy.ma.set_fill_value(ETR, arr1_masked.fill_value)
    
    if not isinstance(arr1, numpy.ma.MaskedArray) :     
        ETR = ETR.filled(fill_value=arr1_masked.fill_value)      
    
    return ETR 
    

def vDTR_calculation(arr1, arr2, fill_val1=None, fill_val2=None):
    
    '''    
    Calculates the vDTR indice: mean absolute day-to-day difference in DTR.
    
    :param arr1: daily max temperature (e.g. "tasmax")
    :type arr1: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param arr2: daily min temperature (e.g. "tasmin")
    :type arr2: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D) 
    
    :param fill_val1: fill value of arr1 
    :type fill_val1: float
    :param fill_val2: fill value of arr2 
    :type fill_val2: float
    
    :rtype: numpy.ndarray (2D)        (if "arr1" and "arr2" are numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr1" and "arr2" are numpy.ma.MaskedArray)
         
    .. warning:: If "arr1" and "arr2" are masked arrays, the parameters "fill_val1" and "fill_val2" are ignored, because they have no sense in this case.
    
    .. warning:: "arr1" and "arr2" must be the same type, shape and correspond to the same time step vector.
    
    '''  
    
    arr1_masked = get_masked_arr(arr1, fill_val1)
    arr2_masked = get_masked_arr(arr2, fill_val2)
    
    a = arr1_masked[1:] - arr2_masked[1:]
    b = arr1_masked[:-1] - arr2_masked[:-1]
    c = abs(a-b)
    vDTR = c.mean(axis=0)
    numpy.ma.set_fill_value(vDTR, arr1_masked.fill_value)
    
    if not isinstance(arr1, numpy.ma.MaskedArray) :     
        vDTR = vDTR.filled(fill_value=arr1_masked.fill_value)      
    
    return vDTR


###### heat indices

def SU_calculation(arr, fill_val=None, threshold=25):
    '''
    Calculates the SU indice: number of summer days (i.e. days with daily maximum temperature > 25 degrees Celsius) [days].
    
    :param arr: daily maximum temperature (e.g. "tasmax") in Kelvin
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float
    :param threshold: user defined temperature threshold in degrees Celsius (default: threshold=25)
    :type threshold: float

    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)
         
    .. warning:: Units of "arr" must be Kelvin.
    
    .. warning:: Units of "threshold" must be in Celsius.
    
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''
    T = threshold + 273.15
    SU = get_nb_days(arr, thresh=T, logical_operation='gt', coef=1.0, fill_val=fill_val)
        
    return SU

def CSU_calculation(arr, fill_val=None, threshold=25):

    '''
    Calculates the CSU indice: maximum number of consecutive summer days (i.e. days with daily maximum temperature > 25 degrees Celsius) [days].
    This function calls C function "find_max_len_consec_sequence_3d" from libC.c
    
    :param arr: daily maximum temperature (e.g. "tasmax") in Kelvin
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float
    :param threshold: user defined temperature threshold in degrees Celsius (default: threshold=25)
    :type threshold: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)
         
    .. warning:: Units of "arr" must be Kelvin.
        
    .. warning:: Units of "threshold" must be in Celsius.
    '''
    #.. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.

        
    T = threshold + 273.15  # Celsius -> Kelvin
    
    CSU = get_max_nb_consecutive_days(arr, thresh=T, logical_operation='gt', coef=1.0, fill_val=fill_val)
    
    return CSU    



def TR_calculation(arr, fill_val=None, threshold=20):
    '''
    Calculates the TR indice: number of tropical nights (i.e. days with daily minimum temperature > 20 degrees Celsius) [days]. 
    
    :param arr: daily min temperature (e.g. "tasmin") in Kelvin
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float
    :param threshold: user defined temperature threshold in degrees Celsius (default: threshold=20)
    :type threshold: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)
         
    .. warning:: Units of "arr" must be Kelvin.
        
    .. warning:: Units of "threshold" must be in Celsius.
       
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''
    
    T = threshold + 273.15
    TR = get_nb_days(arr, thresh=T, logical_operation='gt', coef=1.0, fill_val=fill_val)
    
    return TR


###### cold indices

def FD_calculation(arr, fill_val=None, threshold=0):
    '''
    Calculates the FD indice: number of frost days (i.e. days with daily minimum temperature < 0 degrees Celsius) [days].
    
    :param arr: daily min temperature (e.g. "tasmin") in Kelvin
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)
         
    .. warning:: Units of "arr" must be Kelvin.
    
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''
    
    T = threshold + 273.15
    FD = get_nb_days(arr, thresh=T, logical_operation='lt', coef=1.0, fill_val=fill_val)
    
    return FD


def CFD_calculation(arr, fill_val=None, threshold=0):

    '''
    Calculates the CFD indice: maximum number of consecutive frost days (i.e. days with daily minimum temperature < 0 degrees Celsius) [days].
    This function calls C function "find_max_len_consec_sequence_3d" from libC.c
    
    :param arr: daily min temperature (e.g. "tasmin") in Kelvin
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)
         
    .. warning:: Units of "arr" must be Kelvin.
    
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''

    T = threshold + 273.15  # Celsius -> Kelvin
    
    CFD = get_max_nb_consecutive_days(arr, thresh=T, logical_operation='lt', coef=1.0, fill_val=fill_val)
    
    return CFD 


def ID_calculation(arr, fill_val=None, threshold=0):
    '''
    Calculates the ID indice: number of ice days (i.e. days with daily maximum temperature < 0 degrees Celsius) [days].
    
    :param arr: daily max temperature (e.g. "tasmax") in Kelvin
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)
         
    .. warning:: Units of "arr" must be Kelvin.
    
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''
    
    T = threshold + 273.15
    ID = get_nb_days(arr, thresh=T, logical_operation='lt', coef=1.0, fill_val=fill_val)
    
    return ID


def HD17_calculation(arr, fill_val=None, threshold=17):
    '''
    Calculates the HD17 indice: heating degree days (sum of (17 degrees Celsius - daily mean temperature)).
    
    :param arr: daily mean temperature (e.g. "tas") in Kelvin
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)
         
    .. warning:: Units of "arr" must be Kelvin.
       
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''

    T = threshold + 273.15  # Celsius -> Kelvin
    
    arr_masked = get_masked_arr(arr, fill_val)
    
    a = T - arr_masked
    a[a<0] = 0  # on annule les valeurs qui etaient < 0, i.e. ou arr_masked > T
    HD17 = a.sum(axis=0)
    numpy.ma.set_fill_value(HD17, arr_masked.fill_value)
    
    if not isinstance(arr, numpy.ma.MaskedArray):
        HD17 = HD17.filled(fill_value=arr_masked.fill_value) 
    
    return HD17


def GD4_calculation(arr, fill_val=None, threshold=4):
    '''
    Calculates the GD4 indice: growing degree days (sum of daily mean temperature > 4 degrees Celsius).
    
    :param arr: daily mean temperature (e.g. "tas") in Kelvin
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)
         
    .. warning:: Units of "arr" must be Kelvin.
       
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''
        
    T = threshold + 273.15  # Celsius -> Kelvin
    
    arr_masked = get_masked_arr(arr, fill_val)
    
    new_mask = (arr_masked<=T)    
    new_arr_masked = numpy.ma.array(arr_masked, mask=new_mask, fill_value=arr_masked.fill_value) # we masked the temperatures <= 4 C 
    GD4 = new_arr_masked.sum(axis=0)
    numpy.ma.set_fill_value(GD4, arr_masked.fill_value)
    
    if not isinstance(arr, numpy.ma.MaskedArray):
        GD4 = GD4.filled(fill_value=arr_masked.fill_value) 
    
    return GD4
    

###### draught indices

def CDD_calculation(arr, fill_val=None, threshold=1.0):

    '''
    Calculates the CDD indice: maximum number of consecutive dry days (i.e. days with daily precipitation amount < 1 mm) [days].
    This function calls C function "find_max_len_consec_sequence_3d" from libC.c
    
    :param arr: daily precipitation flux (e.g. "pr") in mm/s
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)
         
    .. warning:: Units of "arr" must be mm/s.
    
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''
    
    c = 60*60*24                          # mm/s --> mm/day
    
    CDD = get_max_nb_consecutive_days(arr, thresh=threshold, logical_operation='lt', coef=c, fill_val=fill_val)

    return CDD


###### rain indices

def PRCPTOT_calculation(arr, fill_val=None):
    '''
    Calculates the PRCPTOT indice: precipitation sum [mm]
    
    :param arr: daily precipitation (liquid form) flux (e.g. "pr") in mm/s
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)
         
    .. warning:: Units of "arr" must be mm/s.
    
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''
    
    c = 60*60*24 # mm/s --> mm/day
    PRCPTOT = simple_stat(arr, stat_operation="sum", coef=c, fill_val=fill_val, thresh=1.0, logical_operation='lt')
    
    return PRCPTOT


   
def RR1_calculation(arr, fill_val=None, threshold=1.0):
    '''
    Calculates the RR1 indice: number of wet days (i.e. days with daily precipitation amount > = 1 mm) [days]
    
    :param arr: daily precipitation (liquid form) flux (e.g. "pr") in mm/s
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)
         
    .. warning:: Units of "arr" must be mm/s.
    
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''
    c = 60*60*24 # mm/s --> mm/day
    RR1 = get_nb_days(arr, thresh=threshold, logical_operation='get', coef=c, fill_val=fill_val)
    
    return RR1


def CWD_calculation(arr, fill_val=None, threshold=1.0):

    '''
    Calculates the CWD indice: maximum number of consecutive wet days (i.e. days with daily precipitation amount > = 1 mm) [days].
    This function calls C function "find_max_len_consec_sequence_3d" from libC.c
    
    :param arr: daily precipitation (liquid form) flux (e.g. "pr") in mm/s
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)
         
    .. warning:: Units of "arr" must be mm/s.
    
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''

    c = 60*60*24                          # mm/s --> mm/day
    
    CWD = get_max_nb_consecutive_days(arr, thresh=threshold, logical_operation='get', coef=c, fill_val=fill_val)

    return CWD


def SDII_calculation(arr, fill_val=None):
    '''
    Calculates the SDII (simple daily intensity index) indice:  mean precipitation amount of wet days (i.e. days with daily precipitation amount > = 1 mm) [mm]
    
    :param arr: daily precipitation (liquid form) flux (e.g. "pr") in mm/s
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)
         
    .. warning:: Units of "arr" must be mm/s.
    
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''

    pr_thresh = 1                               # precipitation threshold = 1 mm
    
    arr_masked = get_masked_arr(arr, fill_val)  # mm/s
    arr_masked = arr_masked*60*60*24            # mm/day
    
    # 1st step: we count wet days
    arr_masked_bool = (arr_masked >= pr_thresh) # array with True/False values
    RR1 = arr_masked_bool.sum(axis=0)           # days
    
    # 2nd step: we count precipitation amount of wet days
    new_mask = (arr_masked < pr_thresh)
    new_arr_masked = numpy.ma.array(arr_masked, mask=new_mask, fill_value=arr_masked.fill_value) # we have only wet days
    pr_amount_wet_days = new_arr_masked.sum(axis=0)
    
    # 3rd step: we count mean
    SDII = pr_amount_wet_days/(RR1*1.0)
    numpy.ma.set_fill_value(SDII, arr_masked.fill_value)
    
    if not isinstance(arr, numpy.ma.MaskedArray):
        SDII = SDII.filled(fill_value=arr_masked.fill_value) 
    
    return SDII


def R10mm_calculation(arr, fill_val=None, threshold=10.0):    
    '''
    Calculates the R10mm indice: number of heavy precipitation days (i.e. days with daily precipitation amount > = 10 mm) [days]
    
    :param arr: daily precipitation (liquid form) flux (e.g. "pr") in mm/s
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)
         
    .. warning:: Units of "arr" must be mm/s.
    
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''
    
    
    c = 60*60*24 # mm/s --> mm/day
    R10mm = get_nb_days(arr, thresh=threshold, logical_operation='get', coef=c, fill_val=fill_val)
    
    return R10mm
    

def R20mm_calculation(arr, fill_val=None, threshold=20.0):    
    '''
    Calculates the R20mm indice: number of very heavy precipitation days (i.e. days with daily precipitation amount > = 20 mm) [days]
    
    :param arr: daily precipitation (liquid form) flux (e.g. "pr") in mm/s
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)
         
    .. warning:: Units of "arr" must be mm/s.
    
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''
    
    c = 60*60*24 # mm/s --> mm/day
    R20mm = get_nb_days(arr, thresh=threshold, logical_operation='get', coef=c, fill_val=fill_val)
    
    return R20mm


def RX1day_calculation(arr, fill_val=None):
    '''
    Calculates the RX1day indice: maximum 1-day precipitation amount [mm]
    
    :param arr: daily precipitation (liquid form) flux (e.g. "pr") in mm/s
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)
         
    .. warning:: Units of "arr" must be mm/s.
    
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''
    
    arr_masked = get_masked_arr(arr, fill_val)  # mm/s
    arr_masked = arr_masked*60*60*24            # mm/day
    
    RX1day = arr_masked.max(axis=0)    
    numpy.ma.set_fill_value(RX1day, arr_masked.fill_value)
    
    if not isinstance(arr, numpy.ma.MaskedArray):
        RX1day = RX1day.filled(fill_value=arr_masked.fill_value) 
    
    return RX1day


def RX5day_calculation(arr, fill_val=None):
    
    '''
    Calculates the RX5day indice: maximum consecutive 5-day precipitation amount [mm]
    This function calls C function "find_max_sum_slidingwindow_3d" from libC.c
    
    :param arr: daily precipitation (liquid form) flux (e.g. "pr") in mm/s
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)
         
    .. warning:: Units of "arr" must be mm/s.
    
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''
    
    arr = arr*60*60*24                          # mm/s --> mm/day
    w_width = 5                                 # 5-day window

        
    # if "arr" is a masked array, we fill it with its fill_value to transform it into a normal array (to pass after to C function!)
    if isinstance(arr, numpy.ma.MaskedArray):
        fill_val = arr.fill_value
        arr_demasked = arr.filled(fill_value=fill_val)
    else:
        arr_demasked = arr
    
    ## array data type should be 'float32' to pass it to C function  
    if arr_demasked.dtype != 'float32':
        arr_demasked = numpy.array(arr_demasked, dtype='float32')
    
    C_find_max_sum_slidingwindow_3d = libraryC.find_max_sum_slidingwindow_3d
    C_find_max_sum_slidingwindow_3d.restype = None
    C_find_max_sum_slidingwindow_3d.argtypes = [ndpointer(ctypes.c_float),
                                                    ctypes.c_int,
                                                    ctypes.c_int,
                                                    ctypes.c_int,
                                                    ndpointer(ctypes.c_double),
                                                    ctypes.c_int,
                                                    ctypes.c_float]
    
    RX5day = numpy.zeros([arr_demasked.shape[1], arr_demasked.shape[2]]) # reserve memory
  
    C_find_max_sum_slidingwindow_3d(arr_demasked, arr_demasked.shape[0], arr_demasked.shape[1], arr_demasked.shape[2], RX5day, w_width, fill_val)
    RX5day = RX5day.reshape(arr_demasked.shape[1], arr_demasked.shape[2])
    
    if isinstance(arr, numpy.ma.MaskedArray):
        RX5day = numpy.ma.array(RX5day, mask=(RX5day==fill_val), fill_value=fill_val)

    return RX5day
 

###### snow indices
'''
WARNING: needs to define type of input array: snowfall flux (prsn, mm/s) or snow depth (snd, m) --> ???
Currently: mm/s
'''

def SD_calculation(arr, fill_val=None):
    '''
    Calculates the SD indice: mean of daily snow depth [cm]
    
    :param arr: daily snowfall precipitation flux (e.g. "prsn") in mm/s
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)
         
    .. warning:: Units of "arr" must be ????.
    
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''
    

    c = (60*60*24)*0.1 # mm/s --> cm/day
    SD = simple_stat(arr, stat_operation='mean', coef=c, fill_val=fill_val)
    
    return SD

    
def SD1_calculation(arr, fill_val=None, threshold=1.0):
    '''
    Calculates the SD1 indice: number of days with snow depth >= 1 cm [days]
    
    :param arr: daily snowfall precipitation flux (e.g. "prsn") in mm/s
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)
         
    .. warning:: Units of "arr" must be ????.
    
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''
    
    
    c = (60*60*24)*0.1 # mm/s --> cm/day
    SD1 = get_nb_days(arr, thresh=threshold, logical_operation='get', coef=c, fill_val=fill_val)
    
    return SD1


def SD5cm_calculation(arr, fill_val=None, threshold=5.0):
    '''
    Calculates the SD5cm indice: number of days with snow depth >= 5 cm [days]
    
    :param arr: daily snowfall precipitation flux (e.g. "prsn") in mm/s
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)
         
    .. warning:: Units of "arr" must be ????.
    
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''
    
    c = (60*60*24)*0.1 # mm/s --> cm/day
    SD5cm = get_nb_days(arr, thresh=threshold, logical_operation='get', coef=c, fill_val=fill_val)
    
    return SD5cm


def SD50cm_calculation(arr, fill_val=None, threshold=50.0):
    '''
    Calculates the SD50cm indice: number of days with snow depth >= 50 cm [days]
    
    :param arr: daily snowfall precipitation flux (e.g. "prsn") in mm/s
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)
         
    .. warning:: Units of "arr" must be ????.
    
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''
    
    c = (60*60*24)*0.1 # mm/s --> cm/day
    SD50cm = get_nb_days(arr, thresh=threshold, logical_operation='get', coef=c, fill_val=fill_val)
    
    return SD50cm   


######### simple statistics: aggregation over time

def TIMEAVG_calculation(arr, fill_val=None):
    
    '''    
    Calculates the average: mean of variable
    
    :param arr: daily mean 
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value  
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)
         
    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.    
    '''
    
    
    TIMEAVG = simple_stat(arr, stat_operation='mean', fill_val=fill_val)
    
    return TIMEAVG


def SUB_calculation(arr1, arr2, fill_val1=None, fill_val2=None):
    
    '''    
    Calculates the substraction of two datasets
    
    :param arr1: daily max temperature (e.g. "tasmax")
    :type arr1: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param arr2: daily min temperature (e.g. "tasmin")
    :type arr2: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D) 
    
    :param fill_val1: fill value of arr1 
    :type fill_val1: float
    :param fill_val2: fill value of arr2 
    :type fill_val2: float
    
    :rtype: numpy.ndarray (2D)        (if "arr1" and "arr2" are numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr1" and "arr2" are numpy.ma.MaskedArray)

    .. warning:: "arr1" and "arr2" must be the same type, shape and correspond to the same time step vector.
    
    '''
    #.. warning:: If "arr1" and "arr2" are masked arrays, the parameters "fill_val1" and "fill_val2" are ignored, because they have no sense in this case.
      
    arr1_masked = get_masked_arr(arr1, fill_val1)
    arr2_masked = get_masked_arr(arr2, fill_val2)
    
    SUB = arr1_masked - arr2_masked                              # masked array with fill_value = fill_value of the first masked array in expression (i.e. arr1_masked)
    numpy.ma.set_fill_value(SUB, arr1_masked.fill_value)      # we set a fill_value = fill_value of arr1_masked (or arr2_masked) 
    
    if not isinstance(arr1, numpy.ma.MaskedArray) :     # or if not isinstance(arr2, numpy.ma.MaskedArray) [because the both input arrays are the same type]
        SUB = SUB.filled(fill_value=arr1_masked.fill_value)      
    
    return SUB    
