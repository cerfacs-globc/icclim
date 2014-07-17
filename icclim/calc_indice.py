# -*- coding: latin-1 -*-
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
- RR
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
    
    arr_masked = get_masked_arr(arr, fill_val)                # numpy.ma.MaskedArray with fill_value=fill_val (if numpy.ndarray passed) or fill_value=arr.fill_value (if numpy.ma.MaskedArray is passed)
    
    TG = arr_masked.mean(axis=0)                              # fill_value is changed: TG is a new numpy.ma.MaskedArray with default fill_value=999999 (!) => next line is to keep the fill_value of arr_masked
    numpy.ma.set_fill_value(TG, arr_masked.fill_value)
    
    if not isinstance(arr, numpy.ma.MaskedArray):
        TG = TG.filled(fill_value=arr_masked.fill_value)      # numpy.ndarray filled with input fill_val
    
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
    
    arr_masked = get_masked_arr(arr, fill_val)                
    
    TN = arr_masked.mean(axis=0)                              
    numpy.ma.set_fill_value(TN, arr_masked.fill_value)
    
    if not isinstance(arr, numpy.ma.MaskedArray):
        TN = TN.filled(fill_value=arr_masked.fill_value)      
    
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
    
    arr_masked = get_masked_arr(arr, fill_val)                
    
    TX = arr_masked.mean(axis=0)                              
    numpy.ma.set_fill_value(TX, arr_masked.fill_value)
    
    if not isinstance(arr, numpy.ma.MaskedArray):
        TX = TX.filled(fill_value=arr_masked.fill_value)      
    
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
    
    arr_masked = get_masked_arr(arr, fill_val)                
    
    TXx = arr_masked.max(axis=0)                              
    numpy.ma.set_fill_value(TXx, arr_masked.fill_value)
    
    if not isinstance(arr, numpy.ma.MaskedArray):
        TXx = TXx.filled(fill_value=arr_masked.fill_value)      
    
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
    
    
    arr_masked = get_masked_arr(arr, fill_val)                
    
    TNx = arr_masked.max(axis=0)                              
    numpy.ma.set_fill_value(TNx, arr_masked.fill_value)
    
    if not isinstance(arr, numpy.ma.MaskedArray):
        TNx = TNx.filled(fill_value=arr_masked.fill_value)      
    
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
    
    arr_masked = get_masked_arr(arr, fill_val)                
    
    TXn = arr_masked.min(axis=0)                              
    numpy.ma.set_fill_value(TXn, arr_masked.fill_value)
    
    if not isinstance(arr, numpy.ma.MaskedArray):
        TXn = TXn.filled(fill_value=arr_masked.fill_value)      
    
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
    
    arr_masked = get_masked_arr(arr, fill_val)                
    
    TNn = arr_masked.min(axis=0)                              
    numpy.ma.set_fill_value(TNn, arr_masked.fill_value)
    
    if not isinstance(arr, numpy.ma.MaskedArray):
        TNn = TNn.filled(fill_value=arr_masked.fill_value)      
    
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

    .. warning:: "arr1" and "arr2" must be both the same type, have the same shape and be corresponding to the same time step vector.
    
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
    
    .. warning:: "arr1" and "arr2" must be both the same type, have the same shape and be corresponding to the same time step vector.
    
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
    
    .. warning:: "arr1" and "arr2" must be both the same type, have the same shape and be corresponding to the same time step vector.
    
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

def SU_calculation(arr, fill_val=None, threshold=None):
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
    
    # temperature threshold (degree Celsius)    
    if threshold==None:
        t = 25
    else:
        t = threshold
    
    T = t + 273.15  # Celsius -> Kelvin
    
    arr_masked = get_masked_arr(arr, fill_val) 
    
    arr_masked = (arr_masked>T)                     # fill_value not changed
    SU = arr_masked.sum(axis=0)                     # fill_value is changed: SU is a new numpy.ma.MaskedArray with default fill_value=999999 (!) => next line is to keep the fill_value of arr_masked 
    numpy.ma.set_fill_value(SU, arr_masked.fill_value) 
    
    if not isinstance(arr, numpy.ma.MaskedArray):
        SU = SU.filled(fill_value=arr_masked.fill_value) 
    
    return SU

def CSU_calculation(arr, fill_val=None, threshold=None):

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
    

    # temperature threshold (degree Celsius)    
    if threshold==None:
        t = 25
    else:
        t = threshold
        
    T = t + 273.15  # Celsius -> Kelvin
    
    # if "arr" is a masked array, we fill it with its fill_value to transform it into a normal array (to pass after to C function!)
    if isinstance(arr, numpy.ma.MaskedArray):
        fill_val = arr.fill_value
        arr_demasked = arr.filled(fill_value=fill_val)
    else:
        arr_demasked = arr
        
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
    
    CSU = numpy.zeros([arr_demasked.shape[1], arr_demasked.shape[2]]) # reserve memory
    
    C_find_max_len_consec_sequence_3d(arr_demasked, arr_demasked.shape[0], arr_demasked.shape[1], arr_demasked.shape[2], CSU, T, fill_val, 'gt')
    CSU = CSU.reshape(arr_demasked.shape[1], arr_demasked.shape[2])
    
    if isinstance(arr, numpy.ma.MaskedArray):
        CSU = numpy.ma.array(CSU, mask=(CSU==fill_val), fill_value=fill_val)

    return CSU    



def TR_calculation(arr, fill_val=None, threshold=None):
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
    
    # temperature threshold (degree Celsius)    
    if threshold==None:
        t = 20
    else:
        t = threshold
        
    T = t + 273.15  # Celsius -> Kelvin
    
    arr_masked = get_masked_arr(arr, fill_val)
    
    arr_masked = (arr_masked>T)
    TR = arr_masked.sum(axis=0)
    numpy.ma.set_fill_value(TR, arr_masked.fill_value)
    
    if not isinstance(arr, numpy.ma.MaskedArray):
        TR = TR.filled(fill_value=arr_masked.fill_value) 
    
    return TR


###### cold indices

def FD_calculation(arr, fill_val=None):
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
    
    t = 0           # temperature threshold (degree Celsius)
    T = t + 273.15  # Celsius -> Kelvin
    
    arr_masked = get_masked_arr(arr, fill_val)
    
    arr_masked = (arr_masked<T)
    FD = arr_masked.sum(axis=0)
    numpy.ma.set_fill_value(FD, arr_masked.fill_value)
    
    if not isinstance(arr, numpy.ma.MaskedArray):
        FD = FD.filled(fill_value=arr_masked.fill_value) 
    
    return FD


def CFD_calculation(arr, fill_val=None):

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

    t = 0          # temperature threshold (degree Celsius)
    T = t + 273.15  # Celsius -> Kelvin
    
    # if "arr" is a masked array, we fill it with its fill_value to transform it into a normal array (to pass after to C function!)
    if isinstance(arr, numpy.ma.MaskedArray):
        fill_val = arr.fill_value
        arr_demasked = arr.filled(fill_value=fill_val)
    else:
        arr_demasked = arr
        
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
    
    CFD = numpy.zeros([arr_demasked.shape[1], arr_demasked.shape[2]]) # reserve memory
    
    C_find_max_len_consec_sequence_3d(arr_demasked, arr_demasked.shape[0], arr_demasked.shape[1], arr_demasked.shape[2], CFD, T, fill_val, 'lt')
    CFD = CFD.reshape(arr_demasked.shape[1], arr_demasked.shape[2])
    
    if isinstance(arr, numpy.ma.MaskedArray):
        CFD = numpy.ma.array(CFD, mask=(CFD==fill_val), fill_value=fill_val)

    return CFD 


def ID_calculation(arr, fill_val=None):
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
    
    t = 0           # temperature threshold (degree Celsius)
    T = t + 273.15  # Celsius -> Kelvin
    
    arr_masked = get_masked_arr(arr, fill_val)
    
    arr_masked = (arr_masked<T)
    ID = arr_masked.sum(axis=0)
    numpy.ma.set_fill_value(ID, arr_masked.fill_value)
    
    if not isinstance(arr, numpy.ma.MaskedArray):
        ID = ID.filled(fill_value=arr_masked.fill_value) 
    
    return ID


def HD17_calculation(arr, fill_val=None):
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

    t = 17          # temperature threshold (degree Celsius)
    T = t + 273.15  # Celsius -> Kelvin
    
    arr_masked = get_masked_arr(arr, fill_val)
    
    a = T - arr_masked
    a[a<0] = 0  # on annule les valeurs qui etaient < 0, i.e. ou arr_masked > T
    HD17 = a.sum(axis=0)
    numpy.ma.set_fill_value(HD17, arr_masked.fill_value)
    
    if not isinstance(arr, numpy.ma.MaskedArray):
        HD17 = HD17.filled(fill_value=arr_masked.fill_value) 
    
    return HD17


def GD4_calculation(arr, fill_val=None):
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
   
    t = 4           # temperature threshold (degree Celsius)         
    T = t + 273.15  # Celsius -> Kelvin
    
    arr_masked = get_masked_arr(arr, fill_val)
    
    new_mask = (arr_masked<=T)    
    new_arr_masked = numpy.ma.array(arr_masked, mask=new_mask, fill_value=arr_masked.fill_value) # we masked the temperatures <= 4 C 
    GD4 = new_arr_masked.sum(axis=0)
    numpy.ma.set_fill_value(GD4, arr_masked.fill_value)
    
    if not isinstance(arr, numpy.ma.MaskedArray):
        GD4 = GD4.filled(fill_value=arr_masked.fill_value) 
    
    return GD4

###### draught indices

def CDD_calculation(arr, fill_val=None):

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

    pr_thresh = 1                               # precipitation threshold = 1 mm
    
    arr = arr*60*60*24                          # mm/s --> mm/day
    
    # if "arr" is a masked array, we fill it with its fill_value to transform it into a normal array (to pass after to C function!)
    if isinstance(arr, numpy.ma.MaskedArray):
        fill_val = arr.fill_value
        arr_demasked = arr.filled(fill_value=fill_val)
    else:
        arr_demasked = arr
        
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
    
    CDD = numpy.zeros([arr_demasked.shape[1], arr_demasked.shape[2]]) # reserve memory
    
    C_find_max_len_consec_sequence_3d(arr_demasked, arr_demasked.shape[0], arr_demasked.shape[1], arr_demasked.shape[2], CDD, pr_thresh, fill_val, 'lt')
    CDD = CDD.reshape(arr_demasked.shape[1], arr_demasked.shape[2])
    
    if isinstance(arr, numpy.ma.MaskedArray):
        CDD = numpy.ma.array(CDD, mask=(CDD==fill_val), fill_value=fill_val)

    return CDD


###### rain indices

def RR_calculation(arr, fill_val=None):
    '''
    Calculates the RR indice: precipitation sum [mm]
    
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
    
    RR = arr_masked.sum(axis=0)
    numpy.ma.set_fill_value(RR, arr_masked.fill_value)
    
    if not isinstance(arr, numpy.ma.MaskedArray):
        RR = RR.filled(fill_value=arr_masked.fill_value) 
    
    return RR


   
def RR1_calculation(arr, fill_val=None):
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
    
    pr_thresh = 1                               # precipitation threshold = 1 mm
    
    arr_masked = get_masked_arr(arr, fill_val)  # mm/s
    arr_masked = arr_masked*60*60*24            # mm/day
    
    arr_masked_bool = (arr_masked >= pr_thresh) # array with True/False values
    RR1 = arr_masked_bool.sum(axis=0)
    numpy.ma.set_fill_value(RR1, arr_masked.fill_value)
    
    if not isinstance(arr, numpy.ma.MaskedArray):
        RR1 = RR1.filled(fill_value=arr_masked.fill_value) 
    
    return RR1


def CWD_calculation(arr, fill_val=None):

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

    pr_thresh = 1                               # precipitation threshold = 1 mm
    
    arr = arr*60*60*24                          # mm/s --> mm/day
    
    # if "arr" is a masked array, we fill it with its fill_value to transform it into a normal array (to pass after to C function!)
    if isinstance(arr, numpy.ma.MaskedArray):
        fill_val = arr.fill_value
        arr_demasked = arr.filled(fill_value=fill_val)
    else:
        arr_demasked = arr
        
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
    
    CWD = numpy.zeros([arr_demasked.shape[1], arr_demasked.shape[2]]) # reserve memory
    
    C_find_max_len_consec_sequence_3d(arr_demasked, arr_demasked.shape[0], arr_demasked.shape[1], arr_demasked.shape[2], CWD, pr_thresh, fill_val, 'get')
    CWD = CWD.reshape(arr_demasked.shape[1], arr_demasked.shape[2])
    
    if isinstance(arr, numpy.ma.MaskedArray):
        CWD = numpy.ma.array(CWD, mask=(CWD==fill_val), fill_value=fill_val)

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


def R10mm_calculation(arr, fill_val=None):    
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
    
    pr_thresh = 10                               # precipitation threshold = 10 mm
    
    arr_masked = get_masked_arr(arr, fill_val)  # mm/s
    arr_masked = arr_masked*60*60*24            # mm/day
    
    arr_masked_bool = (arr_masked >= pr_thresh) # array with True/False values
    R10mm = arr_masked_bool.sum(axis=0)
    numpy.ma.set_fill_value(R10mm, arr_masked.fill_value)
    
    if not isinstance(arr, numpy.ma.MaskedArray):
        R10mm = R10mm.filled(fill_value=arr_masked.fill_value) 
    
    return R10mm
    

def R20mm_calculation(arr, fill_val=None):    
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
    
    pr_thresh = 20                               # precipitation threshold = 20 mm
    
    arr_masked = get_masked_arr(arr, fill_val)  # mm/s
    arr_masked = arr_masked*60*60*24            # mm/day
    
    arr_masked_bool = (arr_masked >= pr_thresh) # array with True/False values
    R20mm = arr_masked_bool.sum(axis=0)
    numpy.ma.set_fill_value(R20mm, arr_masked.fill_value)
    
    if not isinstance(arr, numpy.ma.MaskedArray):
        R20mm = R20mm.filled(fill_value=arr_masked.fill_value) 
    
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
Warning: needs to define type of input array: snowfall flux (prsn, mm/s) or snow depth (snd, m) --> ???
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
    
    arr_masked = get_masked_arr(arr, fill_val)  # mm/s
    arr_masked = (arr_masked*60*60*24)*0.1      # cm/day

    SD = arr_masked.mean(axis=0)                            
    numpy.ma.set_fill_value(SD, arr_masked.fill_value)
    
    if not isinstance(arr, numpy.ma.MaskedArray):
        SD = SD.filled(fill_value=arr_masked.fill_value) 
    
    return SD

    
def SD1_calculation(arr, fill_val=None):
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
    
    sd_thresh = 1                               # snow depth threshold = 1 cm
    
    arr_masked = get_masked_arr(arr, fill_val)  # mm/s
    arr_masked = (arr_masked*60*60*24)*0.1      # cm/day
    
    arr_masked_bool = (arr_masked >= sd_thresh) # array with True/False values
    SD1 = arr_masked_bool.sum(axis=0)
    numpy.ma.set_fill_value(SD1, arr_masked.fill_value)
    
    if not isinstance(arr, numpy.ma.MaskedArray):
        SD1 = SD1.filled(fill_value=arr_masked.fill_value) 
    
    return SD1


def SD5cm_calculation(arr, fill_val=None):
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
    
    sd_thresh = 5                               # snow depth threshold = 5 cm
    
    arr_masked = get_masked_arr(arr, fill_val)  # mm/s
    arr_masked = (arr_masked*60*60*24)*0.1      # cm/day
    
    arr_masked_bool = (arr_masked >= sd_thresh) # array with True/False values
    SD5cm = arr_masked_bool.sum(axis=0)
    numpy.ma.set_fill_value(SD5cm, arr_masked.fill_value)
    
    if not isinstance(arr, numpy.ma.MaskedArray):
        SD5cm = SD5cm.filled(fill_value=arr_masked.fill_value) 
    
    return SD5cm


def SD50cm_calculation(arr, fill_val=None):
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
    
    sd_thresh = 50                              # snow depth threshold = 50 cm
    
    arr_masked = get_masked_arr(arr, fill_val)  # mm/s
    arr_masked = (arr_masked*60*60*24)*0.1      # cm/day
    
    arr_masked_bool = (arr_masked >= sd_thresh) # array with True/False values
    SD50cm = arr_masked_bool.sum(axis=0)
    numpy.ma.set_fill_value(SD50cm, arr_masked.fill_value)
    
    if not isinstance(arr, numpy.ma.MaskedArray):
        SD50cm = SD50cm.filled(fill_value=arr_masked.fill_value) 
    
    return SD50cm   



