# basic function used for computing indices 

import numpy

# import ctypes
# from numpy.ctypeslib import ndpointer
# import os
# 
# my_rep = os.path.dirname(os.path.abspath(__file__)) + os.sep
# libraryC = ctypes.cdll.LoadLibrary(my_rep+'libC.so')


def get_first_occurrence(arr, logical_operation, thresh):
    '''
    Return the first occurrence (index) of values satisfying the condition (logical_operation, thresh)
    in the 3D array along axis=0    
    '''
    
    if logical_operation == 'gt':
        res=numpy.argmax(arr>thresh, axis=0)
        
    elif logical_operation == 'get':
        res=numpy.argmax(arr>=thresh, axis=0)   
            
    elif logical_operation == 'lt':
        res=numpy.argmax(arr<thresh, axis=0)    
            
    elif logical_operation == 'let':
        res=numpy.argmax(arr<=thresh, axis=0) 
             
    elif logical_operation == 'e':
        res=numpy.argmax(arr==thresh, axis=0)
        
    return res


def get_last_occurrence(arr, logical_operation, thresh):
    '''
    Return the last occurrence (index) of values satisfying the condition (logical_operation, thresh)
    in the 3D array along axis=0    
    ''' 
    
    arr_inverted = arr[::-1,:,:]
    
    # first occurrence in the inverted array   
    if logical_operation == 'gt':
        firs_occ=numpy.argmax(arr_inverted>thresh, axis=0)
        
    elif logical_operation == 'get':
        firs_occ=numpy.argmax(arr_inverted>=thresh, axis=0)   
            
    elif logical_operation == 'lt':
        firs_occ=numpy.argmax(arr_inverted<thresh, axis=0)    
            
    elif logical_operation == 'let':
        firs_occ=numpy.argmax(arr_inverted<=thresh, axis=0) 
             
    elif logical_operation == 'e':
        firs_occ=numpy.argmax(arr_inverted==thresh, axis=0)
    
    res=arr.shape[0]-firs_occ-1
        
    return res    


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
            
    elif logical_operation == 'e':
            binary_arr = arr1 == arr2
    
    binary_arr = binary_arr.astype(int) # True/False ---> 1/0

    # if binary_arr is masked array, we fill masked values with 0
    if isinstance(binary_arr, numpy.ma.MaskedArray):
        binary_arr = binary_arr.filled(0.0)
    print binary_arr
    
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


def simple_stat(arr, stat_operation, coef=1.0, fill_val=None, thresh=None, logical_operation=None, indice_event=False):
    
    '''    
    Used for computing: TG, TX, TN, TXx, TNx, TXn, TNn, PRCPTOT, SD
    
    :param arr:
    :type arr:
    
    :param stat_operation: Statistical operation to be applied to `arr`: 'min', 'max', 'mean', 'sum' 
    :type stat_operation: str
    
    :param coef: Coefficient to be multiplied on `arr`
    :type coef: float
    
    :param fill_val: Fill value
    :type fill_val: float

    :param threshold:
    :type threshold:
    
    :param logical_operation:
    :type logical_operation:
    
    'thresh' and 'logical_operation' will filter values, 
    for example if thresh=20 and logical_operation='lt',
    this function will filter all values < 20 before doing statistical operation.
    
    
    :param indice_event: If True, returns the indice where an event is found (only for 'max' and 'min') 
    :type indice_event: bool

    
       
    
     
    
    :param
    
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
        if indice_event==True:
            indices_event_arr=numpy.argmin(arr_masked, axis=0) # numpy.argmin works as well for masked arrays
        
    elif stat_operation=="max":
        RESULT = arr_masked.max(axis=0)                              # fill_value is changed: RESULT is a new numpy.ma.MaskedArray with default fill_value=999999 (!) => next line is to keep the fill_value of arr_masked
        if indice_event==True:
            indices_event_arr=numpy.argmax(arr_masked, axis=0) # numpy.argmax works as well for masked arrays
    elif stat_operation=="sum":
        RESULT = arr_masked.sum(axis=0)                              # fill_value is changed: RESULT is a new numpy.ma.MaskedArray with default fill_value=999999 (!) => next line is to keep the fill_value of arr_masked

    numpy.ma.set_fill_value(RESULT, arr_masked.fill_value)
    
    if not isinstance(arr, numpy.ma.MaskedArray):
        RESULT = RESULT.filled(fill_value=arr_masked.fill_value)      # numpy.ndarray filled with input fill_val
    
    if indice_event==True:
        return [RESULT, indices_event_arr]
    else:
        return [RESULT]


def get_nb_days(arr, thresh, logical_operation, coef=1.0, fill_val=None, date_event=False):
    '''
    Used for computing: SU, TR, FD, ID, RR1, R10mm, R20mm, SD1, SD5cm, SD50cm
    
    :param thresh: temperature or precipitation threshold (must be the same unit as arr) 
    :type thresh: float
    '''
    
    if date_event==True:
        indices_event_bounds=[]
    
    arr_masked = get_masked_arr(arr, fill_val)
    arr_masked = arr_masked * coef
    arr_bin = get_binary_arr(arr_masked, thresh, logical_operation) # numpy.ndarray
    RESULT = arr_bin.sum(axis=0) # numpy.ndarray                    
    
    # RESULT must be numpy.ma.MaskedArray if arr is numpy.ma.MaskedArray
    if isinstance(arr, numpy.ma.MaskedArray):
        RESULT = numpy.ma.array(RESULT, mask=RESULT==arr_masked.fill_value, fill_value=arr_masked.fill_value)
    
    if date_event==True:

        first_occurrence_event=get_first_occurrence(arr_bin, logical_operation='e', thresh=1)
        last_occurrence_event=get_last_occurrence(arr_bin, logical_operation='e', thresh=1)

        indices_event_bounds=[first_occurrence_event, last_occurrence_event]
        
        return [RESULT, indices_event_bounds]
    
    
    else:
        return [RESULT]

# #arr = numpy.random.randint(100, size=(200,2,3))
# 
# arr = 200.*numpy.random.random_sample(size=(300,300,400))
# 
# 
# res = get_nb_days(arr=arr, thresh=150, logical_operation='gt', coef=1.0, fill_val=32, date_event=True)
# 
# # print res[0]
# # print res[1]



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