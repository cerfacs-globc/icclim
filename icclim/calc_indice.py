# -*- coding: latin-1 -*-

'''
Functions to calculate indices.
Note: these functions maniputate 3D arrays
'''

import numpy


######### temperature indices

def TG_calculation(a, fill_val):
    
    '''    
    Calculates the TG indice: mean of daily mean temperature.
    
    :param a: daily mean temperature (e.g. "tas")
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)
    '''
    my_mask = (a==fill_val)
    a_masked = numpy.ma.masked_array(a, mask=my_mask)
    indice = a_masked.mean(axis=0)                              # type(indice): <class 'numpy.ma.core.MaskedArray'>
    indice = indice.filled(fill_value=fill_val)                 # <type 'numpy.ndarray'>
    return indice


def TN_calculation(a, fill_val):
    
    '''    
    Calculates the TN indice: mean of daily min temperature.
    
    :param a: daily min temperature (e.g. "tasmin")
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)
    '''
    my_mask = (a==fill_val)
    a_masked = numpy.ma.masked_array(a, mask=my_mask)
    indice = a_masked.mean(axis=0)                              # type(indice): <class 'numpy.ma.core.MaskedArray'>
    indice = indice.filled(fill_value=fill_val)                 # <type 'numpy.ndarray'>
    return indice


def TX_calculation(a, fill_val):
    
    '''    
    Calculates the TX indice: mean of daily max temperature.
    
    :param a: daily max temperature (e.g. "tasmax")
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)
    '''
    my_mask = (a==fill_val)
    a_masked = numpy.ma.masked_array(a, mask=my_mask)
    indice = a_masked.mean(axis=0)                              # type(indice): <class 'numpy.ma.core.MaskedArray'>
    indice = indice.filled(fill_value=fill_val)                 # <type 'numpy.ndarray'>
    return indice



def TXx_calculation(a, fill_val):
    
    '''    
    Calculates the TXx indice: max of daily max temperature.
    
    :param a: daily max temperature (e.g. "tasmax")
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)
    '''
    my_mask = (a==fill_val)
    a_masked = numpy.ma.masked_array(a, mask=my_mask)
    indice = a_masked.max(axis=0)                               # type(indice): <class 'numpy.ma.core.MaskedArray'>
    indice = indice.filled(fill_value=fill_val)                 # <type 'numpy.ndarray'>
    return indice

def TNx_calculation(a, fill_val):
    
    '''    
    Calculates the TNx indice: max of daily min temperature.
    
    :param a: daily min temperature (e.g. "tasmin")
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)
    '''
    my_mask = (a==fill_val)
    a_masked = numpy.ma.masked_array(a, mask=my_mask)
    indice = a_masked.max(axis=0)                               # type(indice): <class 'numpy.ma.core.MaskedArray'>
    indice = indice.filled(fill_value=fill_val)                 # <type 'numpy.ndarray'>
    return indice


def TXn_calculation(a, fill_val):    
    '''    
    Calculates the TXn indice: min of daily max temperature.
    
    :param a: daily max temperature (e.g. "tasmax")
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)
    '''    
    my_mask = (a==fill_val)
    a_masked = numpy.ma.masked_array(a, mask=my_mask)
    indice = a_masked.min(axis=0)                               # type(indice): <class 'numpy.ma.core.MaskedArray'>
    indice = indice.filled(fill_value=fill_val)                 # <type 'numpy.ndarray'>
    return indice

def TNn_calculation(a, fill_val):    
    '''    
    Calculates the TNn indice: min of daily min temperature.
    
    :param a: daily min temperature (e.g. "tasmin")
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)
    '''    
    my_mask = (a==fill_val)
    a_masked = numpy.ma.masked_array(a, mask=my_mask)
    indice = a_masked.min(axis=0)                               # type(indice): <class 'numpy.ma.core.MaskedArray'>
    indice = indice.filled(fill_value=fill_val)                 # <type 'numpy.ndarray'>
    return indice


def DTR_calculation(a, b, fill_val_a, fill_val_b):
    
    '''    
    Calculates the DTR indice: mean of diurnal temperature range.
    
    :param a: daily max temperature (e.g. "tasmax")
    :type a: numpy.ndarray (3D)
    :param b: daily min temperature (e.g. "tasmin")
    :type b: numpy.ndarray (3D)
    
    :param fill_val_a: fill value of a (ref.: function "get_att_value")
    :type fill_val_a: float
    :param fill_val_b: fill value of b (ref.: function "get_att_value")
    :type fill_val_b: float
    
    :rtype: numpy.ndarray (2D)
    '''   
      
    mask_a = (a==fill_val_a)
    mask_b = (b==fill_val_b)
    mask_ab = mask_a | mask_b           # combined mask 
    
    # we mask each array with the combined mask
    a_masked = numpy.ma.masked_array(a, mask = mask_ab)
    b_masked = numpy.ma.masked_array(b, mask = mask_ab)
    
    range_ab = a_masked - b_masked 
    indice = range_ab.mean(axis=0)                              # type(indice): <class 'numpy.ma.core.MaskedArray'>
    indice = indice.filled(fill_value=fill_val_a)               # <type 'numpy.ndarray'>
    return indice


def ETR_calculation(a, b, fill_val_a, fill_val_b):  
    '''    
    Calculates the ETR indice: intra-period extreme temperature range.
    
    :param a: daily max temperature (e.g. "tasmax")
    :type a: numpy.ndarray (3D)
    :param b: daily min temperature (e.g. "tasmin")
    :type b: numpy.ndarray (3D)
    
    :param fill_val_a: fill value of a (ref.: function "get_att_value")
    :type fill_val_a: float
    :param fill_val_b: fill value of b (ref.: function "get_att_value")
    :type fill_val_b: float
    
    :rtype: numpy.ndarray (2D)
    '''   
    
    mask_a = (a==fill_val_a)
    mask_b = (b==fill_val_b)
    mask_ab = mask_a | mask_b           # combined mask 
    
    # we mask each array with the combined mask
    a_masked = numpy.ma.masked_array(a, mask = mask_ab)
    b_masked = numpy.ma.masked_array(b, mask = mask_ab)
    
    a_masked_max = a_masked.max(axis=0)
    b_masked_min = b_masked.min(axis=0)
    indice = a_masked_max - b_masked_min                        # type(indice): <class 'numpy.ma.core.MaskedArray'>
    indice = indice.filled(fill_value=fill_val_a)               # <type 'numpy.ndarray'>
    return indice


def vDTR_calculation(a, b, fill_val_a, fill_val_b):
    '''    
    Calculates the vDTR indice: mean absolute day-to-day difference in DTR.
    
    :param a: daily max temperature (e.g. "tasmax")
    :type a: numpy.ndarray (3D)
    :param b: daily min temperature (e.g. "tasmin")
    :type b: numpy.ndarray (3D)
    
    :param fill_val_a: fill value of a (ref.: function "get_att_value")
    :type fill_val_a: float
    :param fill_val_b: fill value of b (ref.: function "get_att_value")
    :type fill_val_b: float
    
    :rtype: numpy.ndarray (2D)
    '''   
    
    mask_a = (a==fill_val_a)
    mask_b = (b==fill_val_b)
    mask_ab = mask_a | mask_b           # combined mask 
    
    # we mask each array with the combined mask
    a_masked = numpy.ma.masked_array(a, mask = mask_ab)
    b_masked = numpy.ma.masked_array(b, mask = mask_ab)
    
    c = a_masked[1:] - b_masked[1:]
    d = a_masked[:-1] - b_masked[:-1]
    e = abs(c-d)
    indice = e.mean(axis=0)                                     # type(indice): <class 'numpy.ma.core.MaskedArray'>
    indice = indice.filled(fill_value=fill_val_a)               # <type 'numpy.ndarray'>
    return indice


###### heat indices
def SU_calculation(a, fill_val):
    '''
    Calculates the SU indice: summer days (daily maximum temperature > 25 degrees Celsius) [days].
    
    :param a: daily maximum temperature (e.g. "tasmax") in Kelvin
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)
    '''
    t = 25          # temperature threshold (degree Celsius)
    T = t + 273.15  # Celsius -> Kelvin
    mask_a = (a==fill_val)
    a[a!=fill_val] = (a[a!=fill_val]>T) # values>T -> 1, values<=T -> 0, + fill_val
    a_masked = numpy.ma.masked_array(a, mask=mask_a)
    indice = a_masked.sum(axis=0)                               # type(indice): <class 'numpy.ma.core.MaskedArray'>
    indice = indice.filled(fill_value=fill_val)                 # <type 'numpy.ndarray'>
    return indice
    
   
def CSU_calculation(a, fill_val):

    '''
    Calculates the CSU indice: maximum number of consecutive summer days (daily maximum temperature > 25 degrees Celsius) [days].
    This function calls C function "find_max_len_consec_sequence_3d" from libC.c
    
    :param a: daily maximum temperature (e.g. "tasmax") in Kelvin
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)
    '''

    t = 25          # temperature threshold (degree Celsius)
    T = t + 273.15  # Celsius -> Kelvin
    
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
    
    indice = numpy.zeros([a.shape[1],a.shape[2]]) # reserve memory
    
    C_find_max_len_consec_sequence_3d(a, a.shape[0], a.shape[1], a.shape[2], indice, T, fill_val, 'gt')
    indice = indice.reshape(a.shape[1],a.shape[2])

    return indice    
    

def TR_calculation(a, fill_val):
    '''
    Calculates the TR indice: tropical nights (daily minimum temperature > 20 degrees Celsius) [days]. 
    
    :param a: daily min temperature (e.g. "tasmin") in Kelvin
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)
    '''
    t = 20          # temperature threshold (degree Celsius)
    T = t + 273.15  # Celsius -> Kelvin
    mask_a = (a==fill_val)
    a[a!=fill_val] = (a[a!=fill_val]>T) # values>T -> 1, values<=T -> 0, + fill_val
    a_masked = numpy.ma.masked_array(a, mask=mask_a)
    indice = a_masked.sum(axis=0)                               # type(indice): <class 'numpy.ma.core.MaskedArray'>
    indice = indice.filled(fill_value=fill_val)                 # <type 'numpy.ndarray'>
    return indice


###### cold indices
def FD_calculation(a, fill_val):
    '''
    Calculates the FD indice: frost days (daily minimum temperature < 0 degrees Celsius) [days].
    
    :param a: daily min temperature (e.g. "tasmin") in Kelvin
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)
    '''
    
    t = 0           # temperature threshold (degree Celsius)
    T = t + 273.15  # Celsius -> Kelvin
    
    mask_a = (a==fill_val)
    a[a!=fill_val] = (a[a!=fill_val]<T) # values<T -> 1, values>=T -> 0, + fill_val
    a_masked = numpy.ma.masked_array(a, mask=mask_a)
    indice = a_masked.sum(axis=0)                               # type(indice): <class 'numpy.ma.core.MaskedArray'>
    indice = indice.filled(fill_value=fill_val)                 # <type 'numpy.ndarray'>
    return indice
    


def CFD_calculation(a, fill_val):

    '''
    Calculates the CFD indice: maximum number of consecutive frost days (daily minimum temperature < 0 degrees Celsius) [days].
    This function calls C function "find_max_len_consec_sequence_3d" from libC.c
    
    :param a: daily min temperature (e.g. "tasmin") in Kelvin
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)
    '''

    t = 0
    T = t + 273.15  # Celsius -> Kelvin
    
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
    
    indice = numpy.zeros([a.shape[1],a.shape[2]]) # reserve memory
    
    C_find_max_len_consec_sequence_3d(a, a.shape[0], a.shape[1], a.shape[2], indice, T, fill_val, 'lt')
    indice = indice.reshape(a.shape[1],a.shape[2])

    return indice




def ID_calculation(a, fill_val):
    '''
    Calculates the ID indice: ice days (daily maximum temperature < 0 degrees Celsius) [days].
    
    :param a: daily max temperature (e.g. "tasmax") in Kelvin
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)
    '''
    
    t = 0           # temperature threshold (degree Celsius)
    T = t + 273.15  # Celsius -> Kelvin
    
    mask_a = (a==fill_val)
    a[a!=fill_val] = (a[a!=fill_val]<T) # values<T -> 1, values>=T -> 0, + fill_val
    a_masked = numpy.ma.masked_array(a, mask=mask_a)
    indice = a_masked.sum(axis=0)                               # type(indice): <class 'numpy.ma.core.MaskedArray'>
    indice = indice.filled(fill_value=fill_val)                 # <type 'numpy.ndarray'>
    return indice


def HD17_calculation(a, fill_val):
    '''
    Calculates the HD indice: heating degree days (sum of (17 degrees Celsius - daily mean temperature)).
    
    :param a: daily mean temperature (e.g. "tas") in Kelvin
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)
    '''
    
    t = 17          # temperature threshold (degree Celsius)
    T = t + 273.15  # Celsius -> Kelvin
    mask_a = (a==fill_val)
    a_masked = numpy.ma.masked_array(a, mask=mask_a)
    a_masked = T - a_masked
    a_masked[a_masked<0]=0  # on annule les valeur qui etait < 0, i.e. tas_arr > T
    indice = a_masked.sum(axis=0)                               # type(indice): <class 'numpy.ma.core.MaskedArray'>
    indice = indice.filled(fill_value=fill_val)                 # <type 'numpy.ndarray'>
    indice[indice==0]=fill_val
    return indice


# !!! 
def GD4_calculation(a, fill_val):
    '''
    Calculates the GD indice: growing degree days (sum of daily mean temperature > 4 degrees Celsius).
    
    :param a: daily mean temperature (e.g. "tas") in Kelvin
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)
    '''
    
    t = 4          # temperature threshold (degree Celsius)    
    T = t + 273.15  # Celsius -> Kelvin
    b = a - T
    b[b<0]=0   
    indice = b.sum(axis=0)
    indice[indice==0]=fill_val
    return indice

def GSL_calculation(a, fill_val):

    '''
    Calculates the GSL indice: ...
    '''

    t = 5 # temperature threshold (degree Celsius)
    T = t + 273.15 # Celsius -> Kelvin
    indexMiddleOfYear=181 # this should be calculated, this value is the normal value when size of time vector is 365. In this case, it corresponds to the 1st of July
    
    C_find_GSL_3d = libraryC.find_GSL_3d
    C_find_GSL_3d.restype = None
    C_find_GSL_3d.argtypes = [ndpointer(ctypes.c_float),
                                                    ctypes.c_int,
                                                    ctypes.c_int,
                                                    ctypes.c_int,
                                                    ndpointer(ctypes.c_double),
                                                    ctypes.c_float,
                                                    ctypes.c_float,
                                                    ctypes.c_int]
    
    indice = numpy.zeros([a.shape[1],a.shape[2]]) # reserve memory
    
    C_find_GSL_3d(a, a.shape[0], a.shape[1], a.shape[2], indice, T, fill_val, indexMiddleOfYear)
    indice = indice.reshape(a.shape[1],a.shape[2])

    return indice 


 
###### rain indices
def RR_calculation(prr_arr, fill_val):
    prr_daily = prr_arr*60*60*24 # Nb_prr_daily [mm/day]
    indice = prr_daily.sum(axis=0)
    ### 
    mask_fill_val = (prr_arr==fill_val).any(axis=0)
    indice = numpy.ma.array(indice, mask=mask_fill_val)
    ###
    return indice.filled()

def RR1_calculation(prr_arr, fill_val, precip_thresh_mm=1):
    prr_daily = prr_arr*60*60*24 # Nb_prr_daily [mm/day]
    prr_daily[prr_daily<precip_thresh_mm]=0
    prr_daily[prr_daily>=precip_thresh_mm]=1
    indice=prr_daily.sum(axis=0)
    ### 
    mask_fill_val = (prr_arr==fill_val).any(axis=0)
    indice = numpy.ma.array(indice, mask=mask_fill_val)
    ###
    return indice.filled()


# ?
def SDII_calculation(prr_arr, fill_val, precip_thresh_mm=1):
    prr_arr[prr_arr==fill_val]=0
    prr_daily = prr_arr*60*60*24 # Nb_prr_daily [mm/day]
    a = prr_daily
    a[prr_daily<precip_thresh_mm]=0
    
    b = a.sum(axis=0)
    c = (prr_daily>=precip_thresh_mm).sum(axis=0)
    indice = b/(c*1.0)
    return indice


def CDD_calculation(a, fill_val, precip_thresh=1):

    '''
    Calculates the indice CDD.
    This function calls C function "find_max_len_consec_sequence_3d" from libC.c
    
    :param a: daily precipitation [mm/s]
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    :param precip_thresh: precipitation threshold (mm, default: precip_thresh = 1 mm)
    :type precip_thresh: float
    
    :rtype: numpy.ndarray (2D)
    '''

    
    b = a*60*60*24      # [mm/s] -> [mm/day]
    
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
    
    indice = numpy.zeros([a.shape[1],a.shape[2]]) # reserve memory
    
    C_find_max_len_consec_sequence_3d(b, a.shape[0], a.shape[1], a.shape[2], indice, precip_thresh, fill_val, 'lt')
    indice = indice.reshape(a.shape[1],a.shape[2])

    return indice


def CWD_calculation(a, fill_val, precip_thresh=1):

    '''
    Calculates the indice CWD: maximum number of consecutive wet days (daily precipitation >= 1 mm).
    This function calls C function "find_max_len_consec_sequence_3d" from libC.c
    
    :param a: daily precipitation (liquide phase) [mm/s]
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    :param precip_thresh: precipitation threshold [mm] (default: precip_thresh = 1 mm)
    :type precip_thresh: float
    
    :rtype: numpy.ndarray (2D)
    '''

    
    b = a*60*60*24      # [mm/s] -> [mm/day]
    
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
    
    indice = numpy.zeros([a.shape[1],a.shape[2]]) # reserve memory
    
    C_find_max_len_consec_sequence_3d(b, a.shape[0], a.shape[1], a.shape[2], indice, precip_thresh, fill_val, 'get')
    indice = indice.reshape(a.shape[1],a.shape[2])

    return indice


def R10mm_calculation(prr_arr, fill_val):
    prr_daily = prr_arr*60*60*24 # Nb_prr_daily [mm/day]
    prr_daily[prr_daily<10]=0
    prr_daily[prr_daily>=10]=1
    indice=prr_daily.sum(axis=0)
    ### 
    mask_fill_val = (prr_arr==fill_val).any(axis=0)
    indice = numpy.ma.array(indice, mask=mask_fill_val)
    ###
    return indice.filled()

def R20mm_calculation(prr_arr, fill_val):
    prr_daily = prr_arr*60*60*24 # Nb_prr_daily [mm/day]
    prr_daily[prr_daily<20]=0
    prr_daily[prr_daily>=20]=1
    indice=prr_daily.sum(axis=0)
    ### 
    mask_fill_val = (prr_arr==fill_val).any(axis=0)
    indice = numpy.ma.array(indice, mask=mask_fill_val)
    ###
    return indice.filled()

def RX1day_calculation(prr_arr, fill_val):
    prr_daily = prr_arr*60*60*24 # Nb_prr_daily [mm/day]
    indice = prr_daily.max(axis=0)
    ### 
    mask_fill_val = (prr_arr==fill_val).any(axis=0)
    indice = numpy.ma.array(indice, mask=mask_fill_val)
    ###
    return indice.filled()


def RX5day_calculation(prr_arr, fill_val):
    print "COUCOU!!!"
    #prr_daily = prr_arr*60*60*24 # Nb_prr_daily [mm/day]
    #
    #indice = numpy.empty(shape = (prr_arr.shape[1],prr_arr.shape[2]))
    #
    #for i in range(indice.shape[1]):
    #    for j in range(indice.shape[2]):
    #        indice[i,j] = max_sum_window(prr_daily[:,i,j], 5)
    #### 
    #mask_fill_val = (prr_arr==fill_val).any(axis=0)
    #indice = numpy.ma.array(indice, mask=mask_fill_val)
    ####
    #return indice.filled()


###### snow indices    
def SD_calculation(prsn_arr, fill_val):
    prsn_daily = (prsn_arr*60*60*24)/10 # Nb_prsn_daily [cm/day]
    indice = prsn_daily.mean(axis=0)
    ### 
    mask_fill_val = (prsn_arr==fill_val).any(axis=0)
    indice = numpy.ma.array(indice, mask=mask_fill_val)
    ###
    return indice.filled()

def SD1_calculation(prsn_arr, fill_val, thresh=1):
    '''
    :param thresh: snow deph threshold [cm]
    '''
    prsn_daily = (prsn_arr*60*60*24)/10 # Nb_prsn_daily [cm/day]
    prsn_daily[prsn_daily<thresh]=0
    prsn_daily[prsn_daily>=thresh]=1
    indice=prsn_daily.sum(axis=0)
    ### 
    mask_fill_val = (prsn_arr==fill_val).any(axis=0)
    indice = numpy.ma.array(indice, mask=mask_fill_val)
    ###
    return indice.filled()

def SD5cm_calculation(prsn_arr, fill_val, thresh=5):
    '''
    :param thresh: snow deph threshold [cm]
    '''
    prsn_daily = (prsn_arr*60*60*24)/10 # Nb_prsn_daily [cm/day]
    prsn_daily[prsn_daily<thresh]=0
    prsn_daily[prsn_daily>=thresh]=1
    indice=prsn_daily.sum(axis=0)
    ### 
    mask_fill_val = (prsn_arr==fill_val).any(axis=0)
    indice = numpy.ma.array(indice, mask=mask_fill_val)
    ###
    return indice.filled()

def SD50cm_calculation(prsn_arr, fill_val, thresh=50):
    '''
    :param thresh: snow deph threshold [cm]
    '''
    prsn_daily = (prsn_arr*60*60*24)/10 # Nb_prsn_daily [cm/day]
    prsn_daily[prsn_daily<thresh]=0
    prsn_daily[prsn_daily>=thresh]=1
    indice=prsn_daily.sum(axis=0)
    ### 
    mask_fill_val = (prsn_arr==fill_val).any(axis=0)
    indice = numpy.ma.array(indice, mask=mask_fill_val)
    ###
    return indice.filled()

#########################################################################################