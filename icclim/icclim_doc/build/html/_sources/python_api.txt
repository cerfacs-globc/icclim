Python API
==========

Main functions
--------------

The function to calculate a simple indice (i.e. based on one variable):

.. function:: indice(in_files, out_file, var, indice_name, time_range, slice_mode, project, threshold=None):
    
    
    This function returns result NetCDF file containing a climate indice.
    
    
    :param in_files: absolute paths to NetCDF dataset (including URLs)
    :type in_files: list of str
    :param out_file: output NetCDF file
    :type out_file: str
    :param var: variable name to process
    :type var: str
    :param indice_name: climate indice name
    :type indice_name: str
    :param time_range: time range (dt1 is the first day of year/month, dt2 is the last day of year/month)
    :type time_range: list of 2 datetime objects [dt1, dt2]  
    :param slice_mode: "year" for annual values, "month" for monthly values
    :type slice_mode: str
    :param project: project name ("CMIP5" or "CORDEX")
    :type project: str
    :param threshold: user defined threshold for certain indices 
    :type threshold: float
    
    :rtype: output NetCDF file

.. note:: The list of indice names are :ref:`here <indices>`.  

To calculate a multivariate indice like ETR, DTR or vDTR, use the following function:

.. function:: indice_multivar(in_files1, var1, in_files2, var2, out_file, indice_name, time_range, slice_mode, project, N_lev=None):
    
    
    This function returns result NetCDF file containing a climate indice.
    
    
    :param in_files1: absolute paths to NetCDF dataset (including URLs) corresponding to the var1
    :type in_files1: list of str
    :param var1: variable name to process 
    :type var1: str
    :param in_files2: absolute paths to NetCDF dataset (including URLs) corresponding to the var2
    :type in_files2: list of str
    :param var2: variable name to process
    :type var2: str
    :param out_file: output NetCDF file
    :type out_file: str
    :param indice_name: climate indice name
    :type indice_name: str
    :param time_range: time range (dt1 is the first day of year/month, dt2 is the last day of year/month)
    :type time_range: list of 2 datetime objects [dt1, dt2]  
    :param slice_mode: "year" for annual values, "month" for monthly values
    :type slice_mode: str
    :param project: project name ("CMIP5" or "CORDEX")
    :type project: str
    :param N_lev: level number if 4D variable (dafault: N_lev=None)
    :type N_lev: int
    
    :rtype: output NetCDF file

.. warning:: The both file lists must be identical, i.e. each corresponding file must contain the same time step vector.

Elementary functions
--------------------


The `calc_indice.py <https://github.com/tatarinova/icclim/blob/master/icclim/calc_indice.py>`_ module contains the elementary functions computing indices.
These functions, manipulating 3D arrays, could be reused in other environments. Below some of them.

.. note:: A function name is composed from an indice name and "_calculation" (example: FD_calculation).

.. note:: Input array(s) could be filled (numpy.ndarray) or masked (numpy.ma.MaskedArray). The output array type corresponds to the input array type.

.. warning::
    If input array is filled, a fill_value (parameter "fill_val") must be provided:
    
    >>> FD_calculation(my_3D_array, fill_val=99999)
    
    If input array is masked, the "fill_val" is ignored:
    
    >>> FD_calculation(my_3D_masked_array)



.. function:: TNx_calculation(arr, fill_val=None):
  
    Calculates the TNx indice: maximum of daily minimum temperature.
    
    :param arr: daily min temperature (e.g. "tasmin")
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)


.. function:: CSU_calculation(arr, fill_val=None):

    Calculates the CSU indice: maximum number of consecutive summer days (i.e. days with daily maximum temperature > 25 degrees Celsius) [days].
    This function calls C function "find_max_len_consec_sequence_3d" from libC.c
    
    :param arr: daily maximum temperature (e.g. "tasmax") in Kelvin
    :type arr: numpy.ndarray (3D) or numpy.ma.MaskedArray (3D)
    :param fill_val: fill value 
    :type fill_val: float
    
    :rtype: numpy.ndarray (2D)        (if "arr" is numpy.ndarray)
         or numpy.ma.MaskedArray (2D) (if "arr" is numpy.ma.MaskedArray)
         
    .. warning:: Units of "arr" must be Kelvin!


.. function:: DTR_calculation(arr1, arr2, fill_val1=None, fill_val2=None):
    
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



