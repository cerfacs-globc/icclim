# -*- coding: latin-1 -*-
#  Copyright CERFACS (http://cerfacs.fr/)
#  Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)


# basic function used for computing indices 

import numpy as np

#TODO add comments to describe the function // Take the one from previous version

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



def simple_stat(da, freq_mode='YS', stat_operation=None):

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
    


def get_nb_events(da, freq_mode, threshold, logical_operation):

    da = threshold_calculation(da, threshold, logical_operation)
    da /= da
    return da.resample(time=freq_mode, keep_attrs=True).sum(dim='time')



def get_max_nb_consecutive_days(da, logical_operation, threshold, freq_mode='YS'):

    
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
