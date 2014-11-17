Python API
==========

First, import the ICCLIM library:

>>> import icclim


Main functions to compute climate indices
-----------------------------------------

Depending on the type of climate indice, use the appropriate function: 

+--------------------------+------------------------------------------------------------+-----------------------------------------------------------+
|                          |   Indice                                                   |   Function                                                |
+==========================+============================================================+===========================================================+
| simple indice            | TG, TX, TN, TXx, TXn, TNx, TNn, SU, TR, CSU, GD4, FD, CFD, | :ref:`indice(...) <func_indice_label>`                    |
|                          | ID, HD17,                                                  |                                                           |
|                          | CDD, CWD, RR, RR1, SDII, R10mm, R20mm, RX1day, RX5day,     |                                                           |
|                          | SD, SD1, SD5cm, SD50cm                                     |                                                           |
+--------------------------+------------------------------------------------------------+-----------------------------------------------------------+
| multivariate indice      | DTR, ETR, vDTR                                             | :ref:`indice_multivar(...) <func_indice_multivar_label>`  |
+--------------------------+------------------------------------------------------------+-----------------------------------------------------------+
| percentile-based indice  | TG10p, TX10p, TN10p, TG90p, TX90p, TN90p, WSDI, CSDI,      | :ref:`indice_perc(...) <func_indice_perc_label>`          |
|                          | R75p, R75TOT, R95p, R95TOT, R99p, R99TOT                   |                                                           |
+--------------------------+------------------------------------------------------------+-----------------------------------------------------------+
| compound                 | CD, CW, WD, WW                                             | :ref:`indice_compound(...) <func_indice_compound_label>`  |
| percentile-based indice  |                                                            |                                                           |
+--------------------------+------------------------------------------------------------+-----------------------------------------------------------+

Below is more detail about input parameters for each function. These functions return a netCDF file containing the calculated climate indice.

.. _func_indice_label:
.. automodule:: icclim
    :members: indice

.. warning:: If ``out_file`` already exists, Icclim will overwrite it! 
    
To compute the SU indice (annual time series):

>>> import glob
>>> import datetime
>>> 
>>> input_path = '/data/tatarinova/CMIP5/tasmax_day/'
>>> files = glob.glob(input_path + '*.nc')
>>> out_file = '/data/tatarinova/tmp/indice_SU_year_1860-1890.nc'
>>> 
>>> dt1 = datetime.datetime(1860,01,01)
>>> dt2 = datetime.datetime(1890,12,31)
>>> 
>>> icclim.indice(in_files=files, var='tasmax', indice_name='SU', time_range=[dt1, dt2], slice_mode='year', project='CMIP5', out_file=out_file)

The output dataset will contain the SU indice (3D array) of 31 time steps (31 years).


To get a derived indice from SU, CSU or TR indices, set the ``threshold`` parameter (in Celsius):

>>> iicclim.indice(in_files=files, var='tasmax', indice_name='SU', time_range=[dt1, dt2], slice_mode='year', project='CMIP5', out_file=out_file, threshold=30)

    
.. _func_indice_multivar_label:
.. automodule:: icclim
    :members: indice_multivar
    


>>> file_tasmax1 = 'tasmax_day_CNRM-CM5_historical_r1i1p1_19050101-19091231.nc'
>>> file_tasmax2 = 'tasmax_day_CNRM-CM5_historical_r1i1p1_19100101-19141231.nc'
>>> 
>>> file_tasmin1 = 'tasmin_day_CNRM-CM5_historical_r1i1p1_19050101-19091231.nc'
>>> file_tasmin2 = 'tasmin_day_CNRM-CM5_historical_r1i1p1_19100101-19141231.nc'
>>>
>>> dt1 = datetime.datetime(1905,01,01)
>>> dt2 = datetime.datetime(1912,12,31)
>>> 
>>> icclim.indice_multivar(in_files1=[file_tasmax1, file_tasmax2], var1='tasmax', in_files2=[file_tasmin1, file_tasmin2], var2='tasmin', indice_name='ETR', time_range=[dt1, dt2], slice_mode='year', project='CMIP5', out_file='indice_ETR_year_1905_1912.nc')    
    

    
.. _func_indice_perc_label:
.. automodule:: icclim
    :members: indice_perc

.. _func_indice_compound_label:
.. automodule:: icclim
    :members: indice_compound


.. _creation_daily_percentile_dictionary_label:

Create a daily percentile dictionary
------------------------------------

Daily percentile values are computed from values inside a reference period, named *base period* which is usually 30 years (i.e. 1961-1990).

The *window width* is an odd number of days (usually 5) which will be extracted from all years in the base period; the window is centred on a certain calendar day, for example:
    - **April 13th**, we take the values for *April 11th*, *April 12th*, *April 13th*, *April 14th* and *April 15th* of each year of the base period.
    - **January 1st**, we take all days of *December 30th*, *December 31st*, *January 1st*, *January 2nd* and *January 3rd*.

Hence, for a base period of 30 years and 5-day window width for each calendar day (except February 29th and the annual extremities: December 30th and 31st, January 1st and 2nd), there are 150 values ( 30 * 5 )
to compute its percentile value.

The function :func:`icclim.get_percentile_dict` creates a dictionary where each calendar day (key) has a corresponding 2D array with percentile values:

.. automodule:: icclim
    :members: get_percentile_dict


.. note:: The function uses the `numpy.percentile <http://docs.scipy.org/doc/numpy-dev/reference/generated/numpy.percentile.html>`_ function with "linear" interpolation method as default.
    
The ``only_leap_years`` parameter selects which of two methods to use for calculating a percentile value for the calendar day of **February 29th**:

    - if it is *True*, then we take only leap years, i.e. for example for the base period of 1980-1990 and 5-day window width, we take the values corresponding to the following dates:

        1980-02-27,
        1980-02-28,
        **1980-02-29**,
        1980-03-01,
        1980-03-02,
        
        1984-02-27,
        1984-02-28,        
        **1984-02-29**,
        1984-03-01,
        1984-03-02,
        
        1988-02-27,
        1988-02-28,        
        **1988-02-29**,
        1988-03-01,
        1988-03-02


    - if it is *False*, then for the same base period and window width, we have:

        1980-02-27,
        1980-02-28,
        **1980-02-29**,
        1980-03-01,
        1980-03-02,
        
        1981-02-27,
        1981-02-28,
        1981-03-01,
        1981-03-02,
        
        1982-02-27,
        1982-02-28,
        1982-03-01,
        1982-03-02,
        
        1983-02-27,
        1983-02-28,
        1983-03-01,
        1983-03-02,
        
        1984-02-27,
        1984-02-28,        
        **1984-02-29**,
        1984-03-01,
        1984-03-02,

        1985-02-27,
        1985-02-28,
        1985-03-01,
        1985-03-02,
        
        1986-02-27,
        1986-02-28,
        1986-03-01,
        1986-03-02,
        
        1987-02-27,
        1987-02-28,
        1987-03-01,
        1987-03-02,
        
        1988-02-27,
        1988-02-28,        
        **1988-02-29**,
        1988-03-01,
        1988-03-02

        1989-02-27,
        1989-02-28,
        1989-03-01,
        1989-03-02,
        
        1990-02-27,
        1990-02-28,
        1990-03-01,
        1990-03-02
    
    The second way is preferable, because we have more samples.

.. note:: A calendar day key of the dictionary is composed from the corresponding month and day, separated by a comma, i.e. to get for example the 2D percentile array for *April 13th* it will looks like *my_perc_dict[4,13]*.

>>> file_base1 = 'tasmin_day_CNRM-CM5_historical_r1i1p1_19510101-19701231.nc'
>>> file_base2 = 'tasmin_day_CNRM-CM5_historical_r1i1p1_19710101-19901231.nc'
>>>
>>> # time range for base period
>>> base_dt1 = datetime.datetime(1961,01,01)
>>> base_dt2 = datetime.datetime(1990,12,31)
>>>
>>> perc_dict = icclim.get_percentile_dict(in_files=[file_base1, file_base2], var='tasmin', percentile=10, time_range=[base_dt1, base_dt2])

.. note:: The dictionary with daily percentiles can be saved in `pickle <https://docs.python.org/2/library/pickle.html#>`_ file (the ``save_to_file`` parameter):

    >>> file_name = 'my_perc_dict.pkl'
    >>> perc_dict = icclim.get_percentile_dict(in_files=[file_base1, file_base2], var='tasmin', percentile=10, time_range=[base_dt1, base_dt2], save_to_file=file_name)
    
    To load the dictionary from file just do the following:
    
    >>> import pickle
    >>> with open(file_name, 'rb') as f:
    ...     pd = pickle.load(f)

.. note:: To process OPeNDAP datasets one needs to set the ``transfer_limit_bytes`` in bytes. This parameter is required to estimate an optimal data chunk size to transfer then data chunk-by-chunk in case if the request is bigger than the maximum OPeNDAP/THREDDS request limit. To know your maximum request limit, you can try to run the function without ``transfer_limit_bytes``, you will probably get an error message like: 

	**context: Error { code = 403; message = "Request too big=1875.0 Mbytes, max=500.0"^;};**
	...
	**RuntimeError: NetCDF: Malformed or inaccessible DAP DATADDS**

	That means that your maximum request limit is 500 Mbytes, so set the ``transfer_limit_bytes`` to 500000000 [bytes]. If that does not work, try to reduce it a bit to let's say 450000000 [bytes].

Callback
--------

If you want the progress bar to be printed, use the default callback function from the `callback <https://github.com/tatarinova/icclim/blob/master/icclim/callback.py>`_ module, i.e.
set the ``callback`` parameter to ``icclim.callback.defaultCallback``. (By default it is set to ``None``, i.e. the progress bar will not be printed.)


Elementary functions
--------------------


The `calc_indice.py <https://github.com/tatarinova/icclim/blob/master/icclim/calc_indice.py>`_ and `calc_indice_perc.py <https://github.com/tatarinova/icclim/blob/master/icclim/calc_indice_perc.py>`_ modules contain the elementary functions for computing indices.
These functions could be reused in other environments. Below are some of them.

.. note:: A function name is composed of an indice name and "_calculation" (example: FD_calculation).

.. note:: Input array(s) could be filled (numpy.ndarray) or masked (numpy.ma.MaskedArray). The output array type corresponds to the input array type.

.. warning::
    If input array is filled, a fill_value (parameter "fill_val") must be provided:
    
    >>> FD_calculation(my_3D_array, fill_val=99999)
    
    If input array is masked, the "fill_val" is ignored:
    
    >>> FD_calculation(my_3D_masked_array)



.. automodule:: calc_indice
    :members: TNx_calculation, CSU_calculation, DTR_calculation
   
.. automodule:: calc_indice_perc
    :members: TN10p_calculation, WSDI_calculation

.. warning:: Units of "arr" and percentile values of "percentile_dict" must be the same.


Correspondence table "indice - source variable"
-----------------------------------------------

+------------------------------------------------------------+---------------------------------------------+
|   Indice                                                   |   Source variable                           |
+============================================================+=============================================+
|TG, GD4, HD17, TG10p, TG90p                                 |  daily mean temperature                     |
+------------------------------------------------------------+---------------------------------------------+
|TN, TNx, TNn, TR, FD, CFD, TN10p, TN90p, CSDI               |  daily minimum temperature                  |
+------------------------------------------------------------+---------------------------------------------+
|TX, TXx, TXn, SU, CSU, ID, TX10p, TX90p, WSDI               |  daily maximum temperature                  |
+------------------------------------------------------------+---------------------------------------------+
|DTR, ETR, vDTR                                              |  daily minimum + daily maimum temperature   |
+------------------------------------------------------------+---------------------------------------------+
|RR, RR1, SDII, CWD, CDD, R10mm, R20mm, RX1day, RX5day,      |  daily precipitation flux (liquide phase)   |
|R75p, R75TOT, R95p, R95TOT, R99p, R99TOT                    |                                             |
+------------------------------------------------------------+---------------------------------------------+
|SD, SD1, SD5cm, SD50cm                                      |  daily snowfall flux (solid phase)          |
+------------------------------------------------------------+---------------------------------------------+
|CD, CW, WD, WW                                              |  daily mean temperature +                   |
|                                                            |  daily precipitation flux (liquide phase)   |
+------------------------------------------------------------+---------------------------------------------+

.. _icclim_regrid:

Regridding
----------
It is possible to do simple regridding, using the `regrid.py <https://github.com/tatarinova/icclim/blob/master/icclim/regrid.py>`_ module:

.. automodule:: regrid
    :members: get_regridded_var, write2netCDF_after_regridding


>>> from icclim import regrid


For example, we have 2 files with different resolutions:

>>> f1 = 'tasmax_Amon_bcc-csm1-1_historical_r1i1p1_185001-201212.nc' # source grid (64 x 128), will be regridded to the destination grid
>>> f2 = 'tasmax_day_CNRM-CM5_historical_r1i1p1_18500101-20121231.nc' # destination grid (128 x 256)
>>> arr = regrid.get_regrided_var(f_src=f1, f_dst=f2, varname='tasmax') # numpy array with spatial dimensions (128,256)
>>> f1_regridded = 'regridded_tasmax_Amon_bcc-csm1-1_historical_r1i1p1_185001-201212.nc' # name of the new netCDF file
>>> regrid.write2netCDF_after_regridding(arr, f_src=f1, f_dst=f2, f_out=f1_regridded, var_src='tasmax')

See also `more detailed example <https://github.com/tatarinova/icclim/blob/master/icclim/scripts_examples/example_regrid.py>`_.


.. warning:: The package `ESMF/ESMPy <https://www.earthsystemcog.org/projects/esmpy/>`_ must be installed.


Utility functions
-----------------

.. automodule:: spatial_stat
    :members: get_weight_matrix, multiply_to_weight_matrix
