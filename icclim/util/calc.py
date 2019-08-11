# -*- coding: latin-1 -*-

#  Copyright CERFACS (http://cerfacs.fr/)
#  Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
#
#  Author: Natalia Tatarinova

# basic function used for computing indices 

import numpy as np
import pdb
import sys
from . import util_dt
from collections import OrderedDict
from . import read
import ctypes
from numpy.ctypeslib import ndpointer
import os

my_rep = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0] + os.sep
libraryC = ctypes.cdll.LoadLibrary(my_rep+'libC.so')

def threshold_calculation(da, threshold, logical_operation):
    #Write a function to return a threshold selection
    #operations are: "<, <=, >=, >" == "lt, let, get, gt"
    if logical_operation=='gt':
        return da.where(da>threshold)
    elif logical_operation=='get':
        return da.where(da>threshold)
    elif logical_operation=='lt':
        return da.where(da<threshold)
    elif logical_operation=='let':
        return da.where(da<=threshold)



def simple_stat_2(da, freq_mode='YS', stat_operation=None):

    if stat_operation=='mean':
        return da.resample(time=freq_mode, keep_attrs=True).mean(dim='time')
        #return da.mean(dim='time2compute')
    elif stat_operation=='max':
        return da.resample(time=freq_mode, keep_attrs=True).max(dim='time')
        #return da.max(dim='time2compute')
    elif stat_operation=='min':
        return da.resample(time=freq_mode, keep_attrs=True).min(dim='time')
        #return da.min(dim='time2compute')
    elif stat_operation=='sum':
        return da.resample(time=freq_mode, keep_attrs=True).sum(dim='time')
    

## This function is used for user defined indices when 'date_event' param is True
def get_first_occurrence(arr, val=1):
    '''
    Return the first occurrence (index) of val in the 3D array along axis=0    
    
    arr is a binary (0/1) 3D array
    
    '''
    ### we are looking for the first occurence of 1 (val=1)
    res=np.argmax(arr==val, axis=0)

    '''    
    Problem:
    
    >>> a = np.zeros((4,2,3))
    >>> a[0,0,0]=1
    >>> a
    array([[[ 1.,  0.,  0.],
            [ 0.,  0.,  0.]],
    
           [[ 0.,  0.,  0.],
            [ 0.,  0.,  0.]],
    
           [[ 0.,  0.,  0.],
            [ 0.,  0.,  0.]],
    
           [[ 0.,  0.,  0.],
            [ 0.,  0.,  0.]]])
    >>> np.argmax(a==1, axis=0)
    array([[0, 0, 0],
           [0, 0, 0]])

    Solution: if event is not found we set index to -1
    i.e. the result we want:
    array([[0, -1, -1],
           [-1, -1, -1]])
        
    '''

    sum_arr = np.sum(arr, axis=0) # we have 0 if no event (1) is found 
    
    test_res = sum_arr + res
    
    ### correction
    res[test_res==0]=-1
    
    return res


## This function is used for user defined indices when 'date_event' param is True
def get_last_occurrence(arr, val=1):
    '''
    Return the last occurrence (index) of val in the 3D array along axis=0    
    
    arr is a binary (0/1) 3D array
    
    '''
    
    arr_inverted = arr[::-1,:,:]

    firs_occ=np.argmax(arr_inverted==val, axis=0)
        
    sum_arr = np.sum(arr, axis=0)
        
    test_first_occ = sum_arr + firs_occ
    
    ### last occurrence 
    res=arr.shape[0]-firs_occ-1
    
    ### correction of res
    res[test_first_occ==0]=-1
        
    return res    

def get_nb_events_2(da, freq_mode, threshold, logical_operation):

    da = threshold_calculation(da, threshold, logical_operation)

    da /= da

    return da.resample(time=freq_mode, keep_attrs=True).sum(dim='time')

def get_binary_arr(arr, logical_operation, thresh, dt_arr=None, fill_val=None):
    '''
    Compare "arr" with "thresh" and return a binary array with the result.
    
    :param arr: array to comparer with thresh
    :type arr: np.ndarray (3D)
    
    :param thresh: threshold could be a number, an array or a dictionary with daily percentiles 
    :type thresh: float or np.ndarray or collections.OrderedDict
    
    :param logical_operation: logical operation to compare arr with thresh ('gt', 'get', 'lt', 'let', 'e')
    :type logical_operation: str
    
    :param dt_arr: datetime vector, required if thresh is a dictionary with daily percentiles 
    :type dt_arr: np.ndarray (1D) with datetime.datetime objects
    
    :rtype: binary np.ndarray (3D)

    
    '''
    
    assert(arr.ndim == 3)
    
    arr_masked = get_masked_arr(arr, fill_val)
    
    # thresh is a dictionary with daily percentiles
    if type(thresh)==OrderedDict:
        
        binary_arr = np.zeros((arr.shape[0], arr.shape[1], arr.shape[2]))

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
    if isinstance(binary_arr, np.ma.MaskedArray):
        binary_arr = binary_arr.filled(0.0)
    
    return binary_arr


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


def simple_stat(arr, stat_operation, logical_operation=None, thresh=None, coef=1.0, fill_val=None, dt_arr=None, index_event=False):
    
    '''    
    Used for computing: TG, TX, TN, TXx, TNx, TXn, TNn, PRCPTOT, SD
    
    :param arr: input data array
    :type arr: np.ndarray (3D)
    

    :param stat_operation: Statistical operation to be applied to `arr`: 'min', 'max', 'mean', 'sum' 
    :type stat_operation: str
    
    :param coef: Constant for multiplying 'arr'
    :type coef: float
    
    :param fill_val: Fill value
    :type fill_val: float

    :param thresh: threshold could be a number, an array or a dictionary with daily percentiles
    :type thresh: float or np.ndarray or collections.OrderedDict
    
    :param logical_operation: 'gt', 'get', 'lt', 'let', 'e'
    :type logical_operation: str
    
    :param index_event: If True, returns the index where the first occurrence of the event is found (only for 'max' and 'min')
    :type index_event: bool
    
    :rtype: np.ndarray(2D) if index_event=False
           or [np.ndarray(2D), np.ndarray(2D)] if index_event=True
           
    ..note:: if for example logical_operation='get' and thresh=20,
    this function will fist mask all values < 20 before doing statistical operation.

    If thresh is a dictionary with daily percentiles, dt_arr is required.

    '''

    arr_masked = get_masked_arr(arr, fill_val) * coef                # np.ma.MaskedArray with fill_value=fill_val (if np.ndarray passed) or fill_value=arr.fill_value (if np.ma.MaskedArray is passed)
    # if thresh is a dictionary with daily percentiles
    mask_a = np.zeros((arr.shape[0], arr.shape[1], arr.shape[2]))
    if type(thresh)==OrderedDict:

        i=0

        for dt in dt_arr:

            # current calendar day
            m = dt.month
            d = dt.day

            # we take the 2D array corresponding to the current calendar day
            current_perc_arr = thresh[m,d] # thresh is a dictionary

            # we are looking for the values which are g/ge/l/le/e than the XXth percentile

            if logical_operation == 'gt':
                mask_a[i,:,:] = arr_masked[i,:,:] <= current_perc_arr

            elif logical_operation == 'get':
                    mask_a[i,:,:] = arr_masked[i,:,:] < current_perc_arr

            elif logical_operation == 'lt':
                    mask_a[i,:,:] = arr_masked[i,:,:] >= current_perc_arr

            elif logical_operation == 'let':
                    mask_a[i,:,:] = arr_masked[i,:,:] > current_perc_arr


            i+=1

    # condition: arr <logical_operation> <thresh>
    else:  # thresh is  a number
        if logical_operation=='gt':
            mask_a = arr_masked <= thresh
        elif logical_operation=='get':
            mask_a = arr_masked < thresh
        elif logical_operation=='lt':
            mask_a = arr_masked >= thresh
        elif logical_operation=='let':
            mask_a = arr_masked > thresh
        
    arr_masked = np.ma.array(arr_masked, mask=mask_a, fill_value=arr_masked.fill_value)
    
    
    if stat_operation=="mean":
        res = arr_masked.mean(axis=0)                              # fill_value is changed: res is a new np.ma.MaskedArray with default fill_value=999999 (!) => next line is to keep the fill_value of arr_masked
    elif stat_operation=="min":
        res = arr_masked.min(axis=0)                              # fill_value is changed: res is a new np.ma.MaskedArray with default fill_value=999999 (!) => next line is to keep the fill_value of arr_masked
        if index_event==True:
            index_event_arr=np.argmin(arr_masked, axis=0) # np.argmin works as well for masked arrays
        
    elif stat_operation=="max":
        res = arr_masked.max(axis=0)                              # fill_value is changed: res is a new np.ma.MaskedArray with default fill_value=999999 (!) => next line is to keep the fill_value of arr_masked
        if index_event==True:
            index_event_arr=np.argmax(arr_masked, axis=0) # np.argmax works as well for masked arrays
    elif stat_operation=="sum":
        res = arr_masked.sum(axis=0)                              # fill_value is changed: res is a new np.ma.MaskedArray with default fill_value=999999 (!) => next line is to keep the fill_value of arr_masked

    np.ma.set_fill_value(res, arr_masked.fill_value)
    
    # res must be np.ma.MaskedArray if arr is np.ma.MaskedArray
    if not isinstance(arr, np.ma.MaskedArray):
        res = res.filled(fill_value=arr_masked.fill_value)      # np.ndarray filled with input fill_val
    
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
    in_mask = arr_masked.mask[0, :, :]
    
    
    ## array data type should be 'float32' to pass it to C function  
    if arr_filled.dtype != 'float32':
        arr_filled = np.array(arr_filled, dtype='float32')
    
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
    
    res = np.zeros([arr_filled.shape[1], arr_filled.shape[2]]) # reserve memory
    first_index_event = np.zeros([arr_filled.shape[1], arr_filled.shape[2]], dtype='int32') # reserve memory

    if sys.version_info[0] >= 3:
        stat_mode = stat_mode.encode('ascii')
        extreme_mode = extreme_mode.encode('ascii')

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
    
    # res must be np.ma.MaskedArray if arr is np.ma.MaskedArray
    if isinstance(arr, np.ma.MaskedArray):
#        res = np.ma.array(res, mask=res==arr_masked.fill_value, fill_value=arr_masked.fill_value)
        res = np.ma.masked_array(res, mask=in_mask, fill_value=arr_masked.fill_value)
    del in_mask
    
    
    if index_event==False:
        return res
    else:
        first_index_event = first_index_event.reshape(arr_filled.shape[1], arr_filled.shape[2])
        
        last_index_event = first_index_event + (window_width-1)
        last_index_event[first_index_event==-1]=-1 # first_index_event=-1, i.e. no event found ==> last_index_event=-1
  
        index_event_bounds=[first_index_event, last_index_event]
        return [res, index_event_bounds] # [2D, [2D, 2D]]

def get_max_nb_consecutive_days_2(da, logical_operation, threshold, freq_mode='YS'):

    da = threshold_calculation(da, threshold, logical_operation)
    da /= da

    roll_arr = da.rolling(time2compute=2, min_periods=2)
    test_arr = da.sum(dim='time2compute')
    mask = test_arr > 0 

    for label, arr_window in roll_arr:
        if label==0:
            arr_sum = arr_window.sum(dim='time2compute')
            arr_max = arr_sum
            arr_sum_before = arr_sum

        else:
            res = arr_window.sum(dim='time2compute')
            previous = (res>arr_sum_before)*1
            arr_sum = (arr_sum+res.where(res<2, 1))*res.where(res<2, 1) + previous
            arr_max = np.maximum(arr_sum,arr_max) 
            arr_sum_before = res

    cond = mask & (arr_max == 0)
    arr_max.values[np.where(cond)]=1

    return arr_max




### This function uses "find_max_len_consec_sequence_3d" function from libC.c
def get_max_nb_consecutive_days(arr, logical_operation, thresh, coef=1.0, fill_val=None, index_event=False, out_unit="days"):

    '''
    Used for computing: CSU, CFD, CDD, CWD
    '''
    
    
    if index_event==True:
        index_event_bounds=[]
    
    arr_masked = get_masked_arr(arr, fill_val) * coef
    in_mask = arr_masked.mask[0, :, :]
    arr_filled = arr_masked.filled(fill_value=arr_masked.fill_value) # array must be filled for passing in C function
        
    # array data type should be 'float32' to pass it to C function  
    if arr_filled.dtype != 'float32':
        arr_filled = np.array(arr_filled, dtype='float32')
    
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
    
    res = np.zeros([arr_filled.shape[1], arr_filled.shape[2]]) # reserve memory
    first_index_event = np.zeros([arr_filled.shape[1], arr_filled.shape[2]], dtype='int32') # reserve memory
    last_index_event = np.zeros([arr_filled.shape[1], arr_filled.shape[2]], dtype='int32') # reserve memory
    logical_operation = logical_operation.encode('utf-8')

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
    
    
    # res must be np.ma.MaskedArray if arr is np.ma.MaskedArray
    if isinstance(arr, np.ma.MaskedArray):
#        res = np.ma.array(res, mask=res==arr_masked.fill_value, fill_value=arr_masked.fill_value)
        res = np.ma.masked_array(res, mask=in_mask, fill_value=arr_masked.fill_value)
    del in_mask

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
    :type thresh: float or np.ndarray or collections.OrderedDict
    
    If thresh is a dictionary with daily percentiles, dt_arr is required.

    '''
    arr_masked = get_masked_arr(arr, fill_val) * coef
    in_mask = arr_masked.mask[0, :, :]

    binary_arr_3D = get_binary_arr(arr=arr_masked, 
                                   logical_operation=logical_operation,
                                   thresh=thresh,                                     
                                   dt_arr=dt_arr)
    
    
    res = np.sum(binary_arr_3D, axis=0)
    
    
    if out_unit == "days":
        res = res
    elif out_unit == "%":
        res = res*(100./arr.shape[0])
        
    
    # res must be np.ma.MaskedArray if arr is np.ma.MaskedArray
    if isinstance(arr, np.ma.MaskedArray):
#        res = np.ma.array(res, mask=res==arr_masked.fill_value, fill_value=arr_masked.fill_value)
        res = np.ma.masked_array(res, mask=in_mask, fill_value=arr_masked.fill_value)
    del in_mask
    
    if index_event==True:

        first_occurrence_event=get_first_occurrence(binary_arr_3D)
        last_occurrence_event=get_last_occurrence(binary_arr_3D)

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
            bin_res = np.logical_and(bin_res, bin_arrs[i])
            
        elif link_logical_operation=='or':
            bin_res = np.logical_or(bin_res, bin_arrs[i]) 
            
        i+=1
    if  max_consecutive==False:   
        res = np.sum(bin_res, axis=0) 
        
    else:  ### max_consecutive==True 
        ### we pass bin_res to C function
    
        ##############
        assert(isinstance(bin_res, np.ndarray)) ### we check if bin_res is not a masked array

        # array data type should be 'float32' to pass it to C function  
        if bin_res.dtype != 'float32':
            bin_res = np.array(bin_res, dtype='float32')
        
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
        
        res = np.zeros([bin_res.shape[1], bin_res.shape[2]]) # reserve memory
        first_index_event = np.zeros([bin_res.shape[1], bin_res.shape[2]], dtype='int32') # reserve memory
        last_index_event = np.zeros([bin_res.shape[1], bin_res.shape[2]], dtype='int32') # reserve memory
    
        
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
            first_occurrence_event=get_first_occurrence(bin_res)
            last_occurrence_event=get_last_occurrence(bin_res)
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
    in_mask = arr_masked.mask[0, :, :]
    
    # step1: we get a 3D binary array from arr (if arr value > pctl value: 1, else: 0)    
    binary_arr_3D = get_binary_arr(arr=arr_masked, 
                                   logical_operation=logical_operation,
                                   thresh=percentile_dict,                                     
                                   dt_arr=dt_arr)
    
    # step2: we will pass our 3D binary array (bin_arr) to C function WSDI_CSDI_3d
    
    # array data type should be 'float32' to pass it to C function  
    if binary_arr_3D.dtype != 'float32':
        binary_arr_3D = np.array(binary_arr_3D, dtype='float32')
    
    
    WSDI_CSDI_C = libraryC.WSDI_CSDI_3d    
    WSDI_CSDI_C.restype = None
    WSDI_CSDI_C.argtypes = [ndpointer(ctypes.c_float),
                            ctypes.c_int,
                            ctypes.c_int,
                            ctypes.c_int,
                            ndpointer(ctypes.c_double),
                            ctypes.c_int] 
        
    res = np.zeros([arr.shape[1], arr.shape[2]]) # reserve memory
        
    WSDI_CSDI_C(binary_arr_3D, binary_arr_3D.shape[0], binary_arr_3D.shape[1], binary_arr_3D.shape[2], res, N)
    
    res = res.reshape(arr.shape[1], arr.shape[2])
    
    # res must be np.ma.MaskedArray if arr is np.ma.MaskedArray
    if isinstance(arr, np.ma.MaskedArray):
    #    res = np.ma.array(res, mask=res==arr_masked.fill_value, fill_value=arr_masked.fill_value)
        res = np.ma.masked_array(res, mask=in_mask, fill_value=arr_masked.fill_value)
    del in_mask

    return res    



def RXXpTOT(arr, percentile_arr, logical_operation='gt', pr_thresh = 1.0, fill_val=None):
    '''
    Calculate a RXXpTOT indice, where XX is a percentile value.
    '''

    wet_arr = get_wet_days(arr=arr, fill_val=fill_val) # masked array
    in_mask = wet_arr.mask[0, :, :]
    
    # we are looking for the values which are greater than the Xth percentile
    bin_arr = get_binary_arr(arr=wet_arr, logical_operation=logical_operation, thresh=percentile_arr)
    
    # we inverse bin_arr to get a mask (i.e. to mask values which are less or equal than the Xth percentile)
    maska_ = np.logical_not(bin_arr)
    
    # we apply the mask to wet_arr
    arr_ma = np.ma.array(wet_arr, mask=maska_, fill_value=fill_val)
    
    res = np.sum(arr_ma, axis=0)

    if isinstance(arr, np.ma.MaskedArray):
#        res = np.ma.array(res, mask=res==fill_val, fill_value=fill_val)
        res = np.ma.masked_array(res, mask=in_mask, fill_value=fill_val)
    del in_mask
        
    
    return res



def get_date_event_arr(dt_arr, index_arr, time_calendar, time_units, fill_val):
    ## dt_arr: 1D np array with datetime.datetime objects
    ## index_arr: 2D array with indices
    ## return: 2D array with with numeric dates 
    
    
    res = np.zeros((index_arr.shape[0], index_arr.shape[1]))
    for i in range(index_arr.shape[0]):
        for j in range(index_arr.shape[1]):     
            index =  index_arr[i,j] 
            
            if index==-1: #### no event was found
                date_num = fill_val ### no date
            else:
                date_dt =  dt_arr[index]            
                date_num = util_dt.date2num(dt=date_dt, calend=time_calendar, units=time_units)
            res[i,j] = date_num
            
    return res


def get_anomaly(arr, arr2, fill_val, out_unit=None):
    ### arr: 3D np array corresponding to studied period (future)
    ### arr2: 3D np array corresponding to reference period (past)
    arr1_masked = get_masked_arr(arr, fill_val)
    in_mask1 = arr1_masked.mask[0, :, :]
    arr2_masked = get_masked_arr(arr2, fill_val)
    
    arr1_mean = np.ma.mean(arr1_masked, axis=0) # future
    arr2_mean = np.ma.mean(arr2_masked, axis=0) # past
     
    #anomaly = abs(arr1_mean - arr2_mean)
    anomaly = arr1_mean - arr2_mean
    
    # anomaly must be np.ma.MaskedArray if arr and arr2 are np.ma.MaskedArray
    if isinstance(arr, np.ma.MaskedArray):
#        anomaly = np.ma.array(anomaly, mask=anomaly==arr1_masked.fill_value, fill_value=arr1_masked.fill_value)
        anomaly = np.ma.masked_array(anomaly, mask=in_mask1, fill_value=arr1_masked.fill_value)
    del in_mask1
    
    if out_unit == "%":
        # mean of the past period is reference (100%)
        anomaly = anomaly * (100./arr2_mean)
    return anomaly

def get_wet_days(arr, fill_val=None):
    '''
    wet days: days with precipitation amount >= 1.0 mm
    
    This function masks values < 1.0 mm
    
    '''
    
    arr_masked = get_masked_arr(arr, fill_val)
    
    maska = arr_masked < 1.0 

    arr_wet = np.ma.array(arr_masked, mask=maska, fill_value=arr_masked.fill_value)
    
    return arr_wet
