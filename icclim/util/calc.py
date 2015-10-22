# -*- coding: latin-1 -*-

#  Copyright CERFACS (http://cerfacs.fr/)
#  Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
#
#  Author: Natalia Tatarinova

# basic function used for computing indices 

import numpy

import util_dt
from collections import OrderedDict

import ctypes
from numpy.ctypeslib import ndpointer
import os
my_rep = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0] + os.sep
libraryC = ctypes.cdll.LoadLibrary(my_rep+'libC.so')



## This function is used for user defined indices when 'date_event' param is True
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

## This function is used for user defined indices when 'date_event' param is True
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


def get_binary_arr(arr, logical_operation, thresh, dt_arr=None, fill_val=None):
    '''
    Compare "arr" with "thresh" and return a binary array with the result.
    
    :param arr: array to comparer with thresh
    :type arr: numpy.ndarray (3D)
    
    :param thresh: threshold could be a number, an array or a dictionary with daily percentiles 
    :type thresh: float or numpy.ndarray or collections.OrderedDict
    
    :param logical_operation: logical operation to compare arr with thresh ('gt', 'get', 'lt', 'let', 'e')
    :type logical_operation: str
    
    :param dt_arr: datetime vector, required if thresh is a dictionary with daily percentiles 
    :type dt_arr: numpy.ndarray (1D) with datetime.datetime objects
    
    :rtype: binary numpy.ndarray (3D)

    
    '''
    
    assert(arr.ndim == 3)
    
    arr_masked = get_masked_arr(arr, fill_val)
    
    # thresh is a dictionary with daily percentiles
    if type(thresh)==OrderedDict:
        
        binary_arr = numpy.zeros((arr.shape[0], arr.shape[1], arr.shape[2]))

        i=0
        for dt in dt_arr:
            
            # current calendar day
            m = dt.month
            d = dt.day
    
            # we take the 2D array corresponding to the current calendar day
            current_perc_arr = thresh[m,d] # thresh is a dictionary
                        
            # we are looking for the values which are g/ge/l/le/e than the XXth percentile  
            
            if logical_operation == 'gt':
                binary_arr[i,:,:] = arr_masked[i,:,:] > current_perc_arr
                
            elif logical_operation == 'get':
                    binary_arr[i,:,:] = arr_masked[i,:,:] >= current_perc_arr
                    
            elif logical_operation == 'lt':
                    binary_arr[i,:,:] = arr_masked[i,:,:] < current_perc_arr
                    
            elif logical_operation == 'let':
                    binary_arr[i,:,:] = arr_masked[i,:,:] <= current_perc_arr 
                    
            elif logical_operation == 'e':
                    binary_arr[i,:,:] = arr_masked[i,:,:] == current_perc_arr
            

            i+=1
    
    
    # thresh is an array or number    
    else:
        
        if logical_operation == 'gt':
            binary_arr = arr_masked > thresh
            
        elif logical_operation == 'get':
                binary_arr = arr_masked >= thresh
                
        elif logical_operation == 'lt':
                binary_arr = arr_masked < thresh
                
        elif logical_operation == 'let':
                binary_arr = arr_masked <= thresh 
                
        elif logical_operation == 'e':
                binary_arr = arr_masked == thresh
    
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


def simple_stat(arr, stat_operation, logical_operation=None, thresh=None, coef=1.0, fill_val=None, index_event=False):
    
    '''    
    Used for computing: TG, TX, TN, TXx, TNx, TXn, TNn, PRCPTOT, SD
    
    :param arr: input data array
    :type arr: numpy.ndarray (3D)
    
    :param stat_operation: Statistical operation to be applied to `arr`: 'min', 'max', 'mean', 'sum' 
    :type stat_operation: str
    
    :param coef: Constant for multiplying 'arr'
    :type coef: float
    
    :param fill_val: Fill value
    :type fill_val: float

    :param thresh: numerical threshold
    :type thresh: float
    
    :param logical_operation: 'gt', 'get', 'lt', 'let', 'e'
    :type logical_operation: str
    
    :param index_event: If True, returns the index where the first occurrence of the event is found (only for 'max' and 'min')
    :type index_event: bool
    
    :rtype: numpy.ndarray(2D) if index_event=False
           or [numpy.ndarray(2D), numpy.ndarray(2D)] if index_event=True
           
    ..note:: if for example logical_operation='get' and thresh=20,
    this function will fist mask all values < 20 before doing statistical operation.



    
    '''
    
    arr_masked = get_masked_arr(arr, fill_val) * coef                # numpy.ma.MaskedArray with fill_value=fill_val (if numpy.ndarray passed) or fill_value=arr.fill_value (if numpy.ma.MaskedArray is passed)
                
    # condition: arr <logical_operation> <thresh>         
    if thresh != None:
        if logical_operation=='gt':
            mask_a = arr_masked <= thresh
        elif logical_operation=='get':
            mask_a = arr_masked < thresh
        elif logical_operation=='lt':
            mask_a = arr_masked >= thresh
        if logical_operation=='let':
            mask_a = arr_masked > thresh
        
        arr_masked = numpy.ma.array(arr_masked, mask=mask_a, fill_value=arr_masked.fill_value)
    
    
    if stat_operation=="mean":
        res = arr_masked.mean(axis=0)                              # fill_value is changed: res is a new numpy.ma.MaskedArray with default fill_value=999999 (!) => next line is to keep the fill_value of arr_masked
    elif stat_operation=="min":
        res = arr_masked.min(axis=0)                              # fill_value is changed: res is a new numpy.ma.MaskedArray with default fill_value=999999 (!) => next line is to keep the fill_value of arr_masked
        if index_event==True:
            index_event_arr=numpy.argmin(arr_masked, axis=0) # numpy.argmin works as well for masked arrays
        
    elif stat_operation=="max":
        res = arr_masked.max(axis=0)                              # fill_value is changed: res is a new numpy.ma.MaskedArray with default fill_value=999999 (!) => next line is to keep the fill_value of arr_masked
        if index_event==True:
            index_event_arr=numpy.argmax(arr_masked, axis=0) # numpy.argmax works as well for masked arrays
    elif stat_operation=="sum":
        res = arr_masked.sum(axis=0)                              # fill_value is changed: res is a new numpy.ma.MaskedArray with default fill_value=999999 (!) => next line is to keep the fill_value of arr_masked

    numpy.ma.set_fill_value(res, arr_masked.fill_value)
    
    # res must be numpy.ma.MaskedArray if arr is numpy.ma.MaskedArray
    if not isinstance(arr, numpy.ma.MaskedArray):
        res = res.filled(fill_value=arr_masked.fill_value)      # numpy.ndarray filled with input fill_val
    
    if index_event==True and stat_operation in ['min', 'max']:
        return [res, index_event_arr]
    else:
        return res



### This function uses "get_run_stat_3d" function from libC.c
def get_run_stat(arr, window_width, stat_mode, extreme_mode, coef=1.0, fill_val=None, index_event=False):
    
    '''
    Used for computing: RX5day
    '''
    
    assert(arr.ndim == 3)
    
    if index_event==True:
        index_event_bounds=[]
    
    arr_masked = get_masked_arr(arr, fill_val) * coef
    arr_filled = arr_masked.filled(fill_value=arr_masked.fill_value) # array must be filled for passing in C function
    
    
    ## array data type should be 'float32' to pass it to C function  
    if arr_filled.dtype != 'float32':
        arr_filled = numpy.array(arr_filled, dtype='float32')
    
    C_get_run_stat = libraryC.get_run_stat_3d
    C_get_run_stat.restype = None
    C_get_run_stat.argtypes = [ndpointer(ctypes.c_float), # const float *indata
                                ctypes.c_int, # int _sizeT
                                ctypes.c_int, # int _sizeI
                                ctypes.c_int, # int _sizeJ
                                ndpointer(ctypes.c_double), # double *outdata
                                ctypes.c_int, # int w_width
                                ctypes.c_float, # float fill_val
                                ctypes.c_char_p, # char * stat_mode
                                ctypes.c_char_p, # char * extreme_mode
                                ndpointer(ctypes.c_int) # int *index_event                                                              
                                ]
    
    res = numpy.zeros([arr_filled.shape[1], arr_filled.shape[2]]) # reserve memory
    first_index_event = numpy.zeros([arr_filled.shape[1], arr_filled.shape[2]], dtype='int32') # reserve memory
    
    C_get_run_stat(arr_filled, 
                   arr_filled.shape[0], 
                   arr_filled.shape[1], 
                   arr_filled.shape[2], 
                   res, 
                   window_width, 
                   fill_val,
                   stat_mode, 
                   extreme_mode, 
                   first_index_event)
    
    res = res.reshape(arr_filled.shape[1], arr_filled.shape[2])
    
    # res must be numpy.ma.MaskedArray if arr is numpy.ma.MaskedArray
    if isinstance(arr, numpy.ma.MaskedArray):
        res = numpy.ma.array(res, mask=res==arr_masked.fill_value, fill_value=arr_masked.fill_value)
    
    
    if index_event==False:
        return res
    else:
        first_index_event = first_index_event.reshape(arr_filled.shape[1], arr_filled.shape[2])
        
        last_index_event = first_index_event + (window_width-1)
        last_index_event[first_index_event==-1]=-1 # first_index_event=-1, i.e. no event found ==> last_index_event=-1
  
        index_event_bounds=[first_index_event, last_index_event]
        return [res, index_event_bounds] # [2D, [2D, 2D]]

    
### This function uses "find_max_len_consec_sequence_3d" function from libC.c
def get_max_nb_consecutive_days(arr, logical_operation, thresh, coef=1.0, fill_val=None, index_event=False, out_unit="days"):

    '''
    Used for computing: CSU, CFD, CDD, CWD
    '''
    
    
    if index_event==True:
        index_event_bounds=[]
    
    arr_masked = get_masked_arr(arr, fill_val) * coef
    arr_filled = arr_masked.filled(fill_value=arr_masked.fill_value) # array must be filled for passing in C function
        
    # array data type should be 'float32' to pass it to C function  
    if arr_filled.dtype != 'float32':
        arr_filled = numpy.array(arr_filled, dtype='float32')
    
    C_find_max_len_consec_sequence_3d = libraryC.find_max_len_consec_sequence_3d
    C_find_max_len_consec_sequence_3d.restype = None
    C_find_max_len_consec_sequence_3d.argtypes = [ndpointer(ctypes.c_float), # const float *indata
                                                    ctypes.c_int, # int _sizeT
                                                    ctypes.c_int, # int _sizeI
                                                    ctypes.c_int, # int _sizeJ
                                                    ndpointer(ctypes.c_double), # double *outdata
                                                    ctypes.c_float, # float thresh
                                                    ctypes.c_float, # float fill_val
                                                    ctypes.c_char_p, # char *operation
                                                    ndpointer(ctypes.c_int), # int *index_event_start
                                                    ndpointer(ctypes.c_int), # int *index_event_end
                                                    ] 
    
    res = numpy.zeros([arr_filled.shape[1], arr_filled.shape[2]]) # reserve memory
    first_index_event = numpy.zeros([arr_filled.shape[1], arr_filled.shape[2]], dtype='int32') # reserve memory
    last_index_event = numpy.zeros([arr_filled.shape[1], arr_filled.shape[2]], dtype='int32') # reserve memory

    
    C_find_max_len_consec_sequence_3d(arr_filled, 
                                      arr_filled.shape[0], 
                                      arr_filled.shape[1], 
                                      arr_filled.shape[2], 
                                      res, 
                                      thresh, 
                                      fill_val, 
                                      logical_operation, 
                                      first_index_event, 
                                      last_index_event)

    res = res.reshape(arr_filled.shape[1], arr_filled.shape[2])
    
    
    if out_unit == "days":
        res = res
    elif out_unit == "%":
        res = res*(100./arr.shape[0])
    
    
    # res must be numpy.ma.MaskedArray if arr is numpy.ma.MaskedArray
    if isinstance(arr, numpy.ma.MaskedArray):
        res = numpy.ma.array(res, mask=res==arr_masked.fill_value, fill_value=arr_masked.fill_value)

    if index_event==False:
        return res
    else:
        first_index_event = first_index_event.reshape(arr_filled.shape[1], arr_filled.shape[2])
        last_index_event = last_index_event.reshape(arr_filled.shape[1], arr_filled.shape[2])      
        index_event_bounds=[first_index_event, last_index_event]
        return [res, index_event_bounds] # [2D, [2D, 2D]] 



    
def get_nb_events(arr, logical_operation, thresh, fill_val=None, index_event=False, out_unit="days", dt_arr=None, coef=1.0):
    # WARNING: for precipitation percentile indices (e.g. R75p) ---> arr must be already masked (we need only wet days)
    
    '''
    :param thresh: threshold could be a number, an array or a dictionary with daily percentiles 
    :type thresh: float or numpy.ndarray or collections.OrderedDict
    
    If thresh is a dictionary with daily percentiles, dt_arr is required.

    '''
    arr_masked = get_masked_arr(arr, fill_val) * coef

    
    binary_arr_3D = get_binary_arr(arr=arr_masked, 
                                   logical_operation=logical_operation,
                                   thresh=thresh,                                     
                                   dt_arr=dt_arr)
    
    
    res = numpy.sum(binary_arr_3D, axis=0)
    
    
    if out_unit == "days":
        res = res
    elif out_unit == "%":
        res = res*(100./arr.shape[0])
        
    
    # res must be numpy.ma.MaskedArray if arr is numpy.ma.MaskedArray
    if isinstance(arr, numpy.ma.MaskedArray):
        res = numpy.ma.array(res, mask=res==arr_masked.fill_value, fill_value=arr_masked.fill_value)
    
    if index_event==True:
        first_occurrence_event=get_first_occurrence(binary_arr_3D, logical_operation='e', thresh=1)
        last_occurrence_event=get_last_occurrence(binary_arr_3D, logical_operation='e', thresh=1)

        index_event_bounds=[first_occurrence_event, last_occurrence_event]
        
        return [res, index_event_bounds]   
    
    else:    
        return res



####### This function returns nb of event of max number of consecutive events for multivariable indices    
### for multivariable indices, e.g. (TX > 25 and TN > 10); (TX > 25 and TN > 20th pctl); (TX > 90th pctl and TN > 20th pctl); (TG > 90th pctl and RR > 75th pctl); etc   
def get_nb_events_multivar(bin_arrs, link_logical_operation, fill_val, index_event=False, out_unit="days", max_consecutive=False):    
    # bin_arrs: list with binary arrays
    # link_logical_operation: 'and' or 'or'
    # max_consecutive=False: we count nb of events
    # max_consecutive=True: we count max nb of consecutive events
    
    # we initialize 'bin_res' array
    bin_res = bin_arrs[0]
    i=1
    for i in range(len(bin_arrs)):
        if link_logical_operation=='and':
            bin_res = numpy.logical_and(bin_res, bin_arrs[i])
            
        elif link_logical_operation=='or':
            bin_res = numpy.logical_or(bin_res, bin_arrs[i]) 
            
        i+=1
    if  max_consecutive==False:   
        res = numpy.sum(bin_res, axis=0) 
        
    else:  ### max_consecutive==True 
        ### we pass bin_res to C function
    
        ##############
        assert(isinstance(bin_res, numpy.ndarray)) ### we check if bin_res is not a masked array

        # array data type should be 'float32' to pass it to C function  
        if bin_res.dtype != 'float32':
            bin_res = numpy.array(bin_res, dtype='float32')
        
        C_find_max_len_consec_sequence_3d = libraryC.find_max_len_consec_sequence_3d
        C_find_max_len_consec_sequence_3d.restype = None
        C_find_max_len_consec_sequence_3d.argtypes = [ndpointer(ctypes.c_float), # const float *indata
                                                        ctypes.c_int, # int _sizeT
                                                        ctypes.c_int, # int _sizeI
                                                        ctypes.c_int, # int _sizeJ
                                                        ndpointer(ctypes.c_double), # double *outdata
                                                        ctypes.c_float, # float thresh
                                                        ctypes.c_float, # float fill_val
                                                        ctypes.c_char_p, # char *operation
                                                        ndpointer(ctypes.c_int), # int *index_event_start
                                                        ndpointer(ctypes.c_int), # int *index_event_end
                                                        ] 
        
        res = numpy.zeros([bin_res.shape[1], bin_res.shape[2]]) # reserve memory
        first_index_event = numpy.zeros([bin_res.shape[1], bin_res.shape[2]], dtype='int32') # reserve memory
        last_index_event = numpy.zeros([bin_res.shape[1], bin_res.shape[2]], dtype='int32') # reserve memory
    
        
        C_find_max_len_consec_sequence_3d(bin_res, 
                                          bin_res.shape[0], 
                                          bin_res.shape[1], 
                                          bin_res.shape[2], 
                                          res, 
                                          1, ### thresh
                                          fill_val, 
                                          "e", ### we are looking for a max sequence where values==1
                                          first_index_event, 
                                          last_index_event)
    
        res = res.reshape(bin_res.shape[1], bin_res.shape[2])
        first_index_event = first_index_event.reshape(bin_res.shape[1], bin_res.shape[2])
        last_index_event = last_index_event.reshape(bin_res.shape[1], bin_res.shape[2]) 
    
    
        ##################
        
        
        
        
        
    if out_unit == "days":
        res = res
    elif out_unit == "%":
        res = res*(100./bin_arrs[0].shape[0])
        
    if index_event==True:
        
        if max_consecutive==False:         
            first_occurrence_event=get_first_occurrence(bin_res, logical_operation='e', thresh=1)
            last_occurrence_event=get_last_occurrence(bin_res, logical_operation='e', thresh=1)
            index_event_bounds=[first_occurrence_event, last_occurrence_event]
        
        else:
            index_event_bounds=[first_index_event,last_index_event]
        
        
        
        return [res, index_event_bounds]   
    
    else:    
        return res
    
    

    

def WCSDI(arr, dt_arr, percentile_dict, logical_operation, fill_val=None, N=6):
    '''
    Calculate the WSDI/CSDI indice (warm/cold-spell duration index).
    This function calls C function "WSDI_CSDI_3d" from libC.c
 
    '''

 
    arr_masked = get_masked_arr(arr, fill_val)
    
    # step1: we get a 3D binary array from arr (if arr value > pctl value: 1, else: 0)    
    binary_arr_3D = get_binary_arr(arr=arr_masked, 
                                   logical_operation=logical_operation,
                                   thresh=percentile_dict,                                     
                                   dt_arr=dt_arr)
    
    # step2: we will pass our 3D binary array (bin_arr) to C function WSDI_CSDI_3d
    
    # array data type should be 'float32' to pass it to C function  
    if binary_arr_3D.dtype != 'float32':
        binary_arr_3D = numpy.array(binary_arr_3D, dtype='float32')
    
    
    WSDI_CSDI_C = libraryC.WSDI_CSDI_3d    
    WSDI_CSDI_C.restype = None
    WSDI_CSDI_C.argtypes = [ndpointer(ctypes.c_float),
                            ctypes.c_int,
                            ctypes.c_int,
                            ctypes.c_int,
                            ndpointer(ctypes.c_double),
                            ctypes.c_int] 
        
    res = numpy.zeros([arr.shape[1], arr.shape[2]]) # reserve memory
        
    WSDI_CSDI_C(binary_arr_3D, binary_arr_3D.shape[0], binary_arr_3D.shape[1], binary_arr_3D.shape[2], res, N)
    
    res = res.reshape(arr.shape[1], arr.shape[2])
    
    # res must be numpy.ma.MaskedArray if arr is numpy.ma.MaskedArray
    if isinstance(arr, numpy.ma.MaskedArray):
        res = numpy.ma.array(res, mask=res==arr_masked.fill_value, fill_value=arr_masked.fill_value)

    return res    



def RXXpTOT(arr, percentile_arr, logical_operation='gt', pr_thresh = 1.0, fill_val=None):
    '''
    Calculate a RXXpTOT indice, where XX is a percentile value.
    '''

    wet_arr = get_wet_days(arr=arr, fill_val=fill_val) # masked array
    
    # we are looking for the values which are greater than the Xth percentile
    bin_arr = get_binary_arr(arr=wet_arr, logical_operation=logical_operation, thresh=percentile_arr)
    
    # we inverse bin_arr to get a mask (i.e. to mask values which are less or equal than the Xth percentile)
    maska_ = numpy.logical_not(bin_arr)
    
    # we apply the mask to wet_arr
    arr_ma = numpy.ma.array(wet_arr, mask=maska_, fill_value=fill_val)
    
    res = numpy.sum(arr_ma, axis=0)

    if isinstance(arr, numpy.ma.MaskedArray):
        res = numpy.ma.array(res, mask=res==fill_val, fill_value=fill_val)
        
    
    return res



def get_date_event_arr(dt_arr, index_arr, time_calendar, time_units, fill_val):
    ## dt_arr: 1D numpy array with datetime.datetime objects
    ## index_arr: 2D array with indices
    ## return: 2D array with with numeric dates 
    
    res = numpy.zeros((index_arr.shape[0], index_arr.shape[1]))
    
    for i in range(index_arr.shape[0]):
        for j in range(index_arr.shape[1]):     
            index =  index_arr[i,j] 
            
            if index==-1:
                date_num = fill_val 
            else:
                date_dt =  dt_arr[index]            
                date_num = util_dt.date2num(dt=date_dt, calend=time_calendar, units=time_units)
            res[i,j] = date_num
            
    return res


def get_anomaly(arr, arr2, fill_val, out_unit=None):
    ### arr: 3D numpy array corresponding to studied period (future)
    ### arr2: 3D numpy array corresponding to reference period (past)
    arr1_masked = get_masked_arr(arr, fill_val)
    arr2_masked = get_masked_arr(arr2, fill_val)
    
    arr1_mean = numpy.ma.mean(arr1_masked, axis=0) # future
    arr2_mean = numpy.ma.mean(arr2_masked, axis=0) # past
     
    #anomaly = abs(arr1_mean - arr2_mean)
    anomaly = arr1_mean - arr2_mean
    
    # anomaly must be numpy.ma.MaskedArray if arr and arr2 are numpy.ma.MaskedArray
    if isinstance(arr, numpy.ma.MaskedArray):
        anomaly = numpy.ma.array(anomaly, mask=anomaly==arr1_masked.fill_value, fill_value=arr1_masked.fill_value)
    
    if out_unit == "%":
        # mean of the past period is reference (100%)
        anomaly = anomaly * (100./arr2_mean)
        return anomaly
    else:
        return anomaly

def get_wet_days(arr, fill_val=None):
    '''
    wet days: days with precipitation amount >= 1.0 mm
    
    This function masks values < 1.0 mm
    
    '''
    
    arr_masked = get_masked_arr(arr, fill_val)
    
    maska = arr_masked < 1.0 

    arr_wet = numpy.ma.array(arr_masked, mask=maska, fill_value=arr_masked.fill_value)
    
    return arr_wet
