# -*- coding: latin-1 -*-
#  Copyright CERFACS (http://cerfacs.fr/)
#  Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)


# basic function used for computing indices

import numpy as np
import xarray

# TODO add comments to describe the function // Take the one from previous version


def threshold_calculation(da: xarray.DataArray, threshold, logical_operation):
    # TODO [Refacto] Replace with lambda
    # Write a function to return a threshold selection
    # operations are: "<, <=, >=, >" == "lt, let, get, gt"
    if logical_operation == 'gt':
        return da.where(da > threshold)
    elif logical_operation == 'get':
        return da.where(da > threshold)
    elif logical_operation == 'lt':
        return da.where(da < threshold)
    elif logical_operation == 'let':
        return da.where(da <= threshold)


def mean(da: xarray.DataArray, freq_mode='YS'):
    return _resample_by_time(da, freq_mode).mean()


def max(da: xarray.DataArray, freq_mode='YS'):
    return _resample_by_time(da, freq_mode).max()


def min(da: xarray.DataArray, freq_mode='YS'):
    return _resample_by_time(da, freq_mode).min()


def sum(da: xarray.DataArray, freq_mode='YS'):
    return _resample_by_time(da, freq_mode).sum()


def get_nb_events(da: xarray.DataArray, freq_mode, threshold, logical_operation):
    da = threshold_calculation(da, threshold, logical_operation)
    da /= da
    return da.resample(time=freq_mode, keep_attrs=True).sum(dim='time')


def sum_rolling(da: xarray.DataArray, rolling_window: int):
    return da.rolling(time=rolling_window).sum()


def get_max_nb_consecutive_days(da: xarray.DataArray, logical_operation, threshold, freq_mode='YS'):

    da = threshold_calculation(da, threshold, logical_operation)
    da /= da

    roll_arr = da.rolling(time2compute=2, min_periods=2)
    test_arr = da.sum(dim='time2compute')
    mask = test_arr > 0

    for label, arr_window in roll_arr:
        if label == 0:
            arr_sum = arr_window.sum(dim='time2compute')
            arr_max = arr_sum
            arr_sum_before = arr_sum

        else:
            res = arr_window.sum(dim='time2compute')
            previous = (res > arr_sum_before)*1
            arr_sum = (arr_sum+res.where(res < 2, 1)) * \
                res.where(res < 2, 1) + previous
            arr_max = np.maximum(arr_sum, arr_max)
            arr_sum_before = res

    cond = mask & (arr_max == 0)
    arr_max.values[np.where(cond)] = 1

    return arr_max


def _resample_by_time(da: xarray.DataArray, freq_mode='YS'):
    return da.resample(time=freq_mode, keep_attrs=True)
