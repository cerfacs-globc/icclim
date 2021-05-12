# -*- coding: latin-1 -*-
#  Copyright CERFACS (http://cerfacs.fr/)
#  Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
#
#  Author: Natalia Tatarinova

import numpy
import xarray
from .util import calc
from . import maps
import pdb
'''
Basic routines for computing of climate indices:
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
- RX5day
- CDD
- CWD
- SD
- SD1
- SD5cm
- SD50cm
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

'''

'''
Note: these functions manipulate 3D arrays - numpy.ndarray or numpy.ma.MaskedArray.
Return type: the same type as the type of input array(s)

Note: A function name is composed from an indice name and "_calculation" (example: FD_calculation).

Example of function calling:
        1. if input array is a filled array (numpy.ndarray), a fill_value must be provided: FD_calculation(my_3D_array, fill_val=99999)
        2. if input array is a masked array (numpy.ma.MaskedArray), fill_values is not required: FD_calculation(my_3D_masked_array)


'''


def get_indice_calculation(indice_name, ds, **kwargs):

    #da = ds[indice_name]
    #kwargs['da'] = da
    #ds[indice_name] = eval(indice_name+'_calculation(**kwargs)')

    if indice_name in maps.consecutive_days_indice:
        kwargs['indice_name'] = indice_name

    kwargs['da'] = ds
    ds = eval(indice_name+'_calculation(**kwargs)')

    if 'time2compute' in [*ds.coords]:
        ds = ds.drop('time2compute')

    return ds

# temperature indices


def TG_calculation(da, freq_mode='YS'):
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

    TG = calc.mean(da, freq_mode=freq_mode)

    return TG


def TN_calculation(da, freq_mode='YS', fill_val=None):
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

    TN = calc.mean(da, freq_mode=freq_mode)

    return TN


def TX_calculation(da, freq_mode='YS', fill_val=None):
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
    TX = calc.mean(da, freq_mode=freq_mode)
    # From Kelvin to Celsius
    if numpy.mean(TX > 100):
        TX -= 273.15
    return TX


def TXx_calculation(da, freq_mode='YS', fill_val=None):
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

    TXx = calc.max(da, freq_mode=freq_mode)

    return TXx


def TNx_calculation(da, freq_mode='YS'):
    '''    
    Calculates the TNx indice: maximum of daily minimum temperature.

    :param arr: daily min temperature (e.g. "tasmin")
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value
    :type fill_val: float

    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)
    '''
    # .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.

    TNx = calc.max(da, freq_mode=freq_mode)

    return TNx


def TXn_calculation(da, freq_mode='YS'):
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

    TXn = calc.min(da, freq_mode=freq_mode)

    return TXn


def TNn_calculation(da, freq_mode='YS', fill_val=None):
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

    TNn = calc.min(da, freq_mode=freq_mode)

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
    # .. warning:: If "arr1" and "arr2" are masked arrays, the parameters "fill_val1" and "fill_val2" are ignored, because they have no sense in this case.

    arr1_masked = calc.get_masked_arr(arr1, fill_val1)
    arr2_masked = calc.get_masked_arr(arr2, fill_val2)

    # masked array with fill_value = fill_value of the first masked array in expression (i.e. arr1_masked)
    range_ = arr1_masked - arr2_masked
    # masked array with new fill_value
    DTR = range_.mean(axis=0)
    # we set a fill_value = fill_value of arr1_masked (or arr2_masked)
    numpy.ma.set_fill_value(DTR, arr1_masked.fill_value)

    # �or if not isinstance(arr2, numpy.ma.MaskedArray) [because the both input arrays are the same type]
    if not isinstance(arr1, numpy.ma.MaskedArray):
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

    arr1_masked = calc.get_masked_arr(arr1, fill_val1)
    arr2_masked = calc.get_masked_arr(arr2, fill_val2)

    # masked array with new fill_value (default)
    max_arr1_masked = arr1_masked.max(axis=0)
    # masked array with new fill_value (default)
    min_arr2_masked = arr2_masked.min(axis=0)
    # masked array with new fill_value (default)
    ETR = max_arr1_masked - min_arr2_masked
    numpy.ma.set_fill_value(ETR, arr1_masked.fill_value)

    if not isinstance(arr1, numpy.ma.MaskedArray):
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

    arr1_masked = calc.get_masked_arr(arr1, fill_val1)
    arr2_masked = calc.get_masked_arr(arr2, fill_val2)

    a = arr1_masked[1:] - arr2_masked[1:]
    b = arr1_masked[:-1] - arr2_masked[:-1]
    c = abs(a-b)
    vDTR = c.mean(axis=0)
    numpy.ma.set_fill_value(vDTR, arr1_masked.fill_value)

    if not isinstance(arr1, numpy.ma.MaskedArray):
        vDTR = vDTR.filled(fill_value=arr1_masked.fill_value)

    return vDTR


# heat indices

def SU_calculation(da, freq_mode='YS', threshold=25, out_unit="days"):
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

    SU = calc.get_nb_events(da, freq_mode=freq_mode,
                            logical_operation='gt', threshold=T)

    return SU


def CSU_calculation(da, indice_name, freq_mode='YS', threshold=25):
    '''
    Calculates the CSU indice: maximum number of consecutive summer days (i.e. days with daily maximum temperature > 25 degrees Celsius) [days].


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
    # .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.

    T = threshold + 273.15  # Celsius -> Kelvin
    coef = 1.0
    da = da[indice_name]
    da *= coef

    CSU = calc.get_max_nb_consecutive_days(
        da, threshold=T, logical_operation='gt')

    return CSU


def TR_calculation(da, freq_mode='YS', fill_val=None, threshold=20, out_unit="days"):
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

    TR = calc.get_nb_events(da, freq_mode=freq_mode,
                            logical_operation='gt', threshold=T)

    return TR


# cold indices

def FD_calculation(da, freq_mode='YS', fill_val=None, threshold=0, out_unit="days"):
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

    FD = calc.get_nb_events(da, freq_mode=freq_mode,
                            logical_operation='lt', threshold=T)

    return FD


def CFD_calculation(da, indice_name, freq_mode='YS', fill_val=None, threshold=0):
    '''
    Calculates the CFD indice: maximum number of consecutive frost days (i.e. days with daily minimum temperature < 0 degrees Celsius) [days].

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
    da = da[indice_name]

    CFD = calc.get_max_nb_consecutive_days(
        da, threshold=T, logical_operation='lt')

    return CFD


def ID_calculation(arr, fill_val=None, threshold=0, out_unit="days"):
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

    ID = calc.get_nb_events(arr, logical_operation='lt',
                            thresh=T, fill_val=fill_val, out_unit=out_unit)

    return ID


def HD17_calculation(da, freq_mode='YS', threshold=17):
    '''
    Calculates the HD17 indice: heating degree days (sum of (17 degrees Celsius - daily mean temperature)).
    heating degree days represent the number of days where it is required to heat an building

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
    da -= T
    da = da.where(da > 0, 0)
    HD17 = calc.sum(da, freq_mode=freq_mode)

    return HD17


def GD4_calculation(da, freq_mode, fill_val=None, threshold=4):
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

    T = threshold + 273.15
    da = da.where(da >= T)
    GD4 = calc.sum(da, freq_mode=freq_mode)
    return GD4


# draught indices

def CDD_calculation(da, indice_name, freq_mode='YS', threshold=1.0):
    '''
    Calculates the CDD indice: maximum number of consecutive dry days (i.e. days with daily precipitation amount < 1 mm) [days].

    :param arr: daily precipitation flux (e.g. "pr") in mm/day
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float


    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)

    .. warning:: Units of "arr" must be mm/day.

    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''
    coef = 1.0
    da *= coef
    da = da[indice_name]
    CDD = calc.get_max_nb_consecutive_days(
        da, threshold=threshold, logical_operation='lt')

    return CDD


# rain indices

def PRCPTOT_calculation(da, freq_mode='YS', fill_val=None):
    '''
    Calculates the PRCPTOT indice: total precipitation in wet days [mm]

    :param arr: daily precipitation (liquid form) flux (e.g. "pr") in mm/day
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float

    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)

    .. warning:: Units of "arr" must be mm/day.

    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''
    c = 1.0
    da *= c
    da = calc.threshold_calculation(da, threshold=1.0, logical_operation='get')
    PRCPTOT = calc.sum(da, freq_mode=freq_mode)

    return PRCPTOT


def RR1_calculation(da, freq_mode='YS', fill_val=None, threshold=1.0, out_unit="days"):
    '''
    Calculates the RR1 indice: number of wet days (i.e. days with daily precipitation amount > = 1 mm) [days]

    :param arr: daily precipitation (liquid form) flux (e.g. "pr") in mm/day
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float

    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)

    .. warning:: Units of "arr" must be mm/day.

    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''

    RR1 = calc.get_nb_events(da, freq_mode=freq_mode,
                             logical_operation='get', threshold=threshold)

    return RR1


def CWD_calculation(da, indice_name, freq_mode='YS', threshold=1.0):
    '''
    Calculates the CWD indice: maximum number of consecutive wet days (i.e. days with daily precipitation amount > = 1 mm) [days].

    :param arr: daily precipitation (liquid form) flux (e.g. "pr") in mm/day
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float

    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)

    .. warning:: Units of "arr" must be mm/day.

    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''

    da = da[indice_name]
    coef = 1.0

    da *= coef
    CWD = calc.get_max_nb_consecutive_days(
        da, threshold=threshold, logical_operation='get')

    return CWD


def SDII_calculation(da, freq_mode='YS'):
    '''
    Calculates the SDII (simple daily intensity index) indice:  mean precipitation amount of wet days (i.e. days with daily precipitation amount > = 1 mm) [mm]

    :param arr: daily precipitation (liquid form) flux (e.g. "pr") in mm/day
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float

    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)

    .. warning:: Units of "arr" must be mm/day.

    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''

    # mean of wet days (logical_operation='get', thresh=1.0)
    coef = 1.0
    da *= coef

    da = calc.threshold_calculation(da, threshold=1.0, logical_operation='get')

    SDII = calc.mean(da, freq_mode=freq_mode)

    return SDII


def R10mm_calculation(da, freq_mode='YS', fill_val=None, threshold=10.0, out_unit="days"):
    '''
    Calculates the R10mm indice: number of heavy precipitation days (i.e. days with daily precipitation amount > = 10 mm) [days]

    :param arr: daily precipitation (liquid form) flux (e.g. "pr") in mm/day
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float

    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)

    .. warning:: Units of "arr" must be mm/day.

    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''

    R10mm = calc.get_nb_events(
        da, freq_mode=freq_mode, logical_operation='get', threshold=threshold)

    return R10mm


def R20mm_calculation(da, freq_mode='YS', fill_val=None, threshold=20.0, out_unit="days"):
    '''
    Calculates the R20mm indice: number of very heavy precipitation days (i.e. days with daily precipitation amount > = 20 mm) [days]

    :param arr: daily precipitation (liquid form) flux (e.g. "pr") in mm/day
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float

    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)

    .. warning:: Units of "arr" must be mm/day.

    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''

    R20mm = calc.get_nb_events(
        da, freq_mode=freq_mode, logical_operation='get', threshold=threshold)

    return R20mm


def RX1day_calculation(da, freq_mode='YS', fill_val=None):
    '''
    Calculates the RX1day indice: maximum 1-day precipitation amount [mm]

    :param arr: daily precipitation (liquid form) flux (e.g. "pr") in mm/day
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float

    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)

    .. warning:: Units of "arr" must be mm/day.

    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''

    RX1day = calc.max(da, freq_mode=freq_mode)

    return RX1day


def RX5day_calculation(da: xarray.DataArray, freq_mode='YS', fill_val=None):
    '''
    Calculates the RX5day indice: maximum consecutive 5-day precipitation amount [mm]
    This function calls C function "find_max_sum_slidingwindow_3d" from libC.c

    :param arr: daily precipitation (liquid form) flux (e.g. "pr") in mm/day
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float

    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)

    .. warning:: Units of "arr" must be mm/day.

    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''
    return calc.max(
        calc.sum_rolling(da, 5),
        freq_mode
    )


# snow indices
'''
WARNING: needs to define type of input array: snowfall flux (prsn, mm/day) or snow depth (snd, m) --> ???
Currently: mm/day
'''


def SD_calculation(da, freq_mode='YS', fill_val=None):
    '''
    Calculates the SD indice: mean of daily snow depth [cm]

    :param arr: daily snowfall precipitation flux (e.g. "prsn") in mm/day
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float

    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)

    .. warning:: Units of "arr" must be ????.

    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''

    c = 0.1
    da *= c
    SD = calc.mean(da, freq_mode=freq_mode)

    return SD


def SD1_calculation(da, freq_mode='YS', fill_val=None, threshold=1.0, out_unit="days"):
    '''
    Calculates the SD1 indice: number of days with snow depth >= 1 cm [days]

    :param arr: daily snowfall precipitation flux (e.g. "prsn") in mm/day
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float

    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)

    .. warning:: Units of "arr" must be ????.

    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''

    threshold = threshold*10  # cm --> mm
    SD1 = calc.get_nb_events(da, freq_mode=freq_mode,
                             logical_operation='get', threshold=threshold)

    return SD1


def SD5cm_calculation(da, freq_mode='YS', fill_val=None, threshold=5.0, out_unit="days"):
    '''
    Calculates the SD5cm indice: number of days with snow depth >= 5 cm [days]

    :param arr: daily snowfall precipitation flux (e.g. "prsn") in mm/day
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float

    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)

    .. warning:: Units of "arr" must be ????.

    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''

    threshold = threshold*10  # cm --> mm
    SD5cm = calc.get_nb_events(
        da, freq_mode=freq_mode, logical_operation='get', threshold=threshold)

    return SD5cm


def SD50cm_calculation(da, freq_mode='YS', fill_val=None, threshold=50.0, out_unit="days"):
    '''
    Calculates the SD50cm indice: number of days with snow depth >= 50 cm [days]

    :param arr: daily snowfall precipitation flux (e.g. "prsn") in mm/day
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float

    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)

    .. warning:: Units of "arr" must be ????.

    .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.
    '''

    threshold = threshold*10  # cm --> mm
    SD50cm = calc.get_nb_events(
        da, freq_mode=freq_mode, logical_operation='get', threshold=threshold)

    return SD50cm


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

    TG90p = calc.get_nb_events(arr, logical_operation='gt', thresh=percentile_dict,
                               fill_val=fill_val, out_unit=out_unit, dt_arr=dt_arr)

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

    TX90p = calc.get_nb_events(arr, logical_operation='gt', thresh=percentile_dict,
                               fill_val=fill_val, out_unit=out_unit, dt_arr=dt_arr)

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

    TN90p = calc.get_nb_events(arr, logical_operation='gt', thresh=percentile_dict,
                               fill_val=fill_val, out_unit=out_unit, dt_arr=dt_arr)

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

    TG10p = calc.get_nb_events(arr, logical_operation='lt', thresh=percentile_dict,
                               fill_val=fill_val, out_unit=out_unit, dt_arr=dt_arr)

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

    TX10p = calc.get_nb_events(arr, logical_operation='lt', thresh=percentile_dict,
                               fill_val=fill_val, out_unit=out_unit, dt_arr=dt_arr)

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

    # .. warning:: Units of "arr" and percentile values of "percentile_dict" must be the same.
    #
    # .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.

    TN10p = calc.get_nb_events(arr, logical_operation='lt', thresh=percentile_dict,
                               fill_val=fill_val, out_unit=out_unit, dt_arr=dt_arr)

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

    # .. warning:: Units of "arr" and percentile values of "percentile_dict" must be the same.
    #
    # .. warning:: If "arr" is a masked array, the parameter "fill_val" is ignored, because it has no sense in this case.

    WSDI = calc.WCSDI(arr, dt_arr, percentile_dict,
                      logical_operation='gt', fill_val=fill_val, N=6)

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

    CSDI = calc.WCSDI(arr, dt_arr, percentile_dict,
                      logical_operation='lt', fill_val=fill_val, N=6)

    return CSDI


def R75p_calculation(arr, percentile_arr, fill_val=None, out_unit="days"):
    '''
    Calculate the R75p indice: number of moderate wet days (i.e. days with daily precipitation amount > 75th percentile of daily amount in the base period).

    :param arr: daily precipitation flux (liquid form) (e.g. "pr") in mm/day
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

    wet_arr = calc.get_wet_days(arr=arr, fill_val=fill_val)  # masked array

    R75p = calc.get_nb_events(wet_arr, logical_operation='gt',
                              thresh=percentile_arr, fill_val=fill_val, out_unit=out_unit)

    return R75p


def R95p_calculation(arr, percentile_arr, fill_val=None, out_unit="days"):
    '''
    Calculate the R95p indice: number of very wet days (i.e. days with daily precipitation amount > 95th percentile of daily amount in the base period).

    :param arr: daily precipitation flux (liquid form) (e.g. "pr") in mm/day
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

    wet_arr = calc.get_wet_days(arr=arr, fill_val=fill_val)  # masked array

    R95p = calc.get_nb_events(wet_arr, logical_operation='gt',
                              thresh=percentile_arr, fill_val=fill_val, out_unit=out_unit)

    return R95p


def R99p_calculation(arr, percentile_arr, fill_val=None, out_unit="days"):
    '''
    Calculate the R99p indice: number of extremely wet days (i.e. days with daily precipitation amount > 99th percentile of daily amount in the base period).

    :param arr: daily precipitation flux (liquid form) (e.g. "pr") in mm/day
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

    wet_arr = calc.get_wet_days(arr=arr, fill_val=fill_val)  # masked array

    R99p = calc.get_nb_events(wet_arr, logical_operation='gt',
                              thresh=percentile_arr, fill_val=fill_val, out_unit=out_unit)

    return R99p


def R75pTOT_calculation(arr, percentile_arr, fill_val=None, out_unit=None):
    '''
    Calculate the R75pTOT indice: precipitation fraction due to moderate wet days (i.e. days with daily precipitation amount > 75th percentile of daily amount in the base period) [%]

    :param arr: daily precipitation flux (liquid form) (e.g. "pr") in mm/day
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

    R75pTOT = calc.RXXpTOT(
        arr, percentile_arr, logical_operation='gt', pr_thresh=1.0, fill_val=fill_val)

    return R75pTOT


def R95pTOT_calculation(arr, percentile_arr, fill_val=None, out_unit=None):
    '''
    Calculate the R95pTOT indice: precipitation fraction due to very wet days (i.e. days with daily precipitation amount > 95th percentile of daily amount in the base period) [%]

    :param arr: daily precipitation flux (liquid form) (e.g. "pr") in mm/day
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

    R95pTOT = calc.RXXpTOT(
        arr, percentile_arr, logical_operation='gt', pr_thresh=1.0, fill_val=fill_val)

    return R95pTOT


def R99pTOT_calculation(arr, percentile_arr, fill_val=None, out_unit=None):
    '''
    Calculate the R99pTOT indice: precipitation fraction due to extremely wet days (i.e. days with daily precipitation amount > 99th percentile of daily amount in the base period) [%]

    :param arr: daily precipitation flux (liquid form) (e.g. "pr") in mm/day
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

    R99pTOT = calc.RXXpTOT(
        arr, percentile_arr, logical_operation='gt', pr_thresh=1.0, fill_val=fill_val)

    return R99pTOT
