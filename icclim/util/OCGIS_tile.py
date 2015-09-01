'''
Many thanks to Ben Koziol, the OpenClimateGIS (https://www.earthsystemcog.org/projects/openclimategis/) developer, who kindly provided this module.

Additions from 2015/08/07 by Natalia Tatarinova: added default value of "tdim" in get_tile_schema 

'''

import numpy as np
import itertools


def get_tile_schema(nrow,ncol,tdim=0,origin=0):
    ret = {}
    
    if tdim==0: # no chunking
        ret.update({0:{'row':[origin, nrow],'col':[origin, ncol]}})
        return(ret)
    
    else: # chunking    
        row_idx = np.arange(origin,nrow+tdim,step=tdim,dtype=int)
        if row_idx[-1] > nrow:
            row_idx[-1] = nrow
        col_idx = np.arange(origin,ncol+tdim,step=tdim,dtype=int)
        if col_idx[-1] > ncol:
            col_idx[-1] = ncol
        row_slices = get_slices(row_idx)
        col_slices = get_slices(col_idx)
        tile_id = 0
        for row,col in itertools.product(range(len(row_slices)),range(len(col_slices))):
            ret.update({tile_id:{'row':row_slices[row],'col':col_slices[col]}})
            tile_id += 1
        return(ret)

def get_slices(arr):
    ret = [None]*(arr.shape[0]-1)
    for idx in range(arr.shape[0]):
        try:
            start = arr[idx]
            stop = arr[idx+1]
            ret[idx] = [start,stop]
        except IndexError:
            break
    return(ret)

