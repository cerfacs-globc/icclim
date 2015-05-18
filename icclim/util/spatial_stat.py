#  Copyright CERFACS (http://cerfacs.fr/)
#  Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
#
#  Author: Natalia Tatarinova

###'''
###Utility functions for spatial statistics like computing of spatial average, spatial standard deviation, etc
###
###We use these functions if model grid is rectilinear, for example grid "lat/lon":
###
###1. "get_weight_matrix" computes weights, giving more weight to the pixels on the poles
###2. "multiply_to_weight_matrix" returns new values to be used for spatial statistics
###
###'''

import numpy

def get_weight_matrix(lat_arr, lon_arr): #, units="rad"):  
    '''
    Computes a weight matrix for rectilinear grid.
    
    :param lat_arr: vector of latitudes in radians
    :type lat_arr: numpy.ndarray (1D)
    :param lon_arr: vector of longitudes 
    :type lon_arr: numpy.ndarray (1D)
    
    :rtype:  numpy.ndarray (2D)
    
    .. warning:: Latitudes must be in radians.
    
    '''
    
    nb_rows = len(lat_arr)
    nb_columns = len(lon_arr)
    
    w_matrix = numpy.zeros((nb_rows, nb_columns))
        
    for i in range(nb_rows):
        w_matrix[i,:]=numpy.cos(lat_arr[i])
        
    
    return w_matrix
    
    
    
############## test "get_weight_matrix"
#import time
#start1 = time.time()
#
#files = ['/home/globc/tatarinova/Downloads/tasmax_day_EC-EARTH_rcp26_r8i1p1_20800101-20841231.nc']
#
#import netCDF4
#nc = netCDF4.MFDataset(files, 'r', aggdim='time')
#lat_arr = nc.variables['lat'][:]
#lon_arr = nc.variables['lon'][:]
#
#a = get_weight_matrix(lat_arr, lon_arr)
#
#stop1 = time.time()
#time1 = stop1 - start1
#print "weight matrix time: ", time1



def multiply_to_weight_matrix(arr, weight_matrix):
    '''
    Returns the result of the multiplication of "arr" by "weight_matrix".
    
    :param arr: values
    :type arr: numpy.ndarray
    :param weight_matrix: weights 
    :type weight_matrix: numpy.ndarray (2D)
    
    :rtype: numpy.ndarray of the same shape as "arr"
    
    .. warning:: if "arr" is a 2D array, "arr" and "weight_matrix" must have the same shape;
                if "arr" is a 3D array, then arr.shape[1] = weight_matrix.shape[0] and arr.shape[2] = weight_matrix.shape[1]
    '''
    
    result = arr *  weight_matrix
    
    return result
    
