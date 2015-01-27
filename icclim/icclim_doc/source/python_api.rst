Python API
==========



:func:`icclim.indice` -- Compute indice
----------------------------------------


This is the main function to compute an indice:

.. automodule:: icclim
    :members: indice


Set of required parameters varies depending on indice's type:

+----------------------+------------------------------------------------------------+----------------------------+
|                      |   Indice                                                   |   Required parameters      |
+======================+============================================================+============================+
| simple indice        | TG, TX, TN, TXx, TXn, TNx, TNn, SU, TR, CSU, GD4, FD, CFD, |  - ``indice_name``         |
|                      | ID, HD17,                                                  |  - ``in_files``            |
|                      | CDD, CWD, RR, RR1, SDII, R10mm, R20mm, RX1day, RX5day,     |  - ``var_name``            |
|                      | SD, SD1, SD5cm, SD50cm                                     |                            |
+----------------------+------------------------------------------------------------+----------------------------+
| multivariable-based  |                                                            |  - ``indice_name``         |
| indice               | DTR, ETR, vDTR                                             |  - ``in_files``            |
|                      |                                                            |  - ``var_name``            |  
|                      |                                                            |  - ``in_files2``           |
|                      |                                                            |  - ``var_name2``           |
+----------------------+------------------------------------------------------------+----------------------------+
| percentile-based     | TG10p, TX10p, TN10p, TG90p, TX90p, TN90p, WSDI, CSDI,      |  - ``indice_name``         |
| indice               | R75p, R75TOT, R95p, R95TOT, R99p, R99TOT                   |  - ``in_files``            |
|                      |                                                            |  - ``var_name``            |
|                      |                                                            |  - ``percentile_dict``     |
+----------------------+------------------------------------------------------------+----------------------------+
| multivariable        | CD, CW, WD, WW                                             |  - ``indice_name``         |
| percentile-based     |                                                            |  - ``in_files``            |
| indice               |                                                            |  - ``var_name``            |
|                      |                                                            |  - ``percentile_dict``     |
|                      |                                                            |  - ``in_files2``           |
|                      |                                                            |  - ``var_name2``           |
|                      |                                                            |  - ``percentile_dict2``    |
+----------------------+------------------------------------------------------------+----------------------------+

.. note:: For the variable names see the :ref:`correspondence table "indice - source variable" <table_indice_sourceVar_label>` 

See detailed examples in the :ref:`example section <examples_label>`.



Below some additionnal information about input parameters.


slice_mode
~~~~~~~~~~
The ``slice_mode`` parameter defines a desired temporal aggregation. Thus, each indice can be calculated as annual, winter half-year, summer half-year, winter, spring,
summer, autumn and monthly values: 

+----------------------+-----------------------+
| Value (string)       | Description           |
+======================+=======================+
|  ``year`` (default)  |    annual             |
+----------------------+-----------------------+
|  ``month``           |    monthly            |
+----------------------+-----------------------+
|  ``ONDJFM``          |    winter half-year   |
+----------------------+-----------------------+
|  ``AMJJAS``          |    summer half-year   |
+----------------------+-----------------------+
|  ``DJF``             |    winter             |
+----------------------+-----------------------+
|  ``MAM``             |    spring             |
+----------------------+-----------------------+
|  ``JJA``             |    summer             |
+----------------------+-----------------------+
|  ``SON``             |    autumn             |
+----------------------+-----------------------+

.. note:: The winter season (``DJF``) of 2000 is composed of December 2000, January 2001 and February 2001.
            Likewise, the winter half-year (``ONDJFM``) of 2000 includes October 2000, November 2000, December 2000, January 2001, February 2001 and March 2001. 


threshold
~~~~~~~~~
It is possible to set a user define threshold for indices **SU** (default threshold: 25), **CSU** (default threshold: 25), **TR** (default threshold: 20).
The threshold could be one value:

>>> threshold = 30

or a list of values:

>>> threshold = [20,25,30]

.. note:: Units of ``threshold`` must be in degrees Celsius. 

transfer_limit_Mbytes
~~~~~~~~~~~~~~~~~~~~~

In case of OPeNDAP datasets, if the request is bigger than the maximum OPeNDAP/THREDDS request limit, you will probably get an error message like:
    
        
    .. code-block:: rest
    
	context: Error { code = 403; message = "Request too big=1875.0 Mbytes, max=500.0"^;};
        
	...
        
	RuntimeError: NetCDF: Malformed or inaccessible DAP DATADDS

That means that your transfer limit is fixed to 500 Mbytes.

It is possible to realize spatial chunking (i.e. cut data spacially into chunks, where each one does not exceed the request limit)
to transfer then data chunk-by-chunk. 
The ``transfer_limit_Mbytes`` parameter, required to estimate an optimal data chunk size, should be set to the request limit:

>>> transfer_limit_Mbytes = 500

.. note:: If that does not work, try to reduce the ``transfer_limit_Mbytes`` value.


callback
~~~~~~~~
The percentage progress bar is printed if the ``callback`` parameter is set to a callback function.
The dafault callback functions are defined in `util.callback.py <link>`_. (They both displays the same message: Processing.)

>>> import util.callback as callback
>>> cb = callback.defaultCallback
 




.. _creation_daily_percentile_dictionary_label:

:func:`icclim.get_percentile_dict` -- Compute daily percentiles 
-----------------------------------------------------------------

Daily percentile values are computed from values inside a reference period, named *base period* which is usually 30 years (i.e. 1961-1990).

The *window width* is an odd number of days (usually 5) which will be extracted from all years in the base period; the window is centred on a certain calendar day, for example:
    - **April 13th**, we take the values for *April 11th*, *April 12th*, *April 13th*, *April 14th* and *April 15th* of each year of the base period.
    - **January 1st**, we take all days of *December 30th*, *December 31st*, *January 1st*, *January 2nd* and *January 3rd*.

Hence, for a base period of 30 years and 5-day window width for each calendar day (except February 29th and the annual extremities: December 30th and 31st, January 1st and 2nd), there are 150 values ( 30 * 5 )
to compute its percentile value.

The function :func:`icclim.get_percentile_dict` creates a dictionary where each calendar day (key) has a corresponding 2D array with percentile values:

.. automodule:: icclim
    :members: get_percentile_dict


.. note:: The function computed percentiles uses linear interpolation method.

.. note:: A calendar day key of the dictionary is composed from the corresponding month and day, separated by a comma, i.e. to get for example the 2D percentile array for *April 13th* it will looks like *my_perc_dict[4,13]*.

only_leap_years
~~~~~~~~~~~~~~~
    
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



>>> files = ['tasmin_day_CNRM-CM5_historical_r1i1p1_19510101-19701231.nc', 'tasmin_day_CNRM-CM5_historical_r1i1p1_19710101-19901231.nc']
>>>
>>> # time range for base period
>>> base_dt1 = datetime.datetime(1961,01,01)
>>> base_dt2 = datetime.datetime(1990,12,31)
>>>
>>> perc_dict = icclim.get_percentile_dict(in_files=files, var='tasmin', percentile=10, time_range=[base_dt1, base_dt2])

To get 2D numpy array with percentiles for *31th November*:

>>> 10th_perc_31November =  perc_dict[11,31]


save_to_file
~~~~~~~~~~~~

The dictionary with daily percentiles can be saved in `pickle <https://docs.python.org/2/library/pickle.html#>`_ file:

    >>> file_name = 'my_perc_dict.pkl'
    >>> perc_dict = icclim.get_percentile_dict(in_files=[file_base1, file_base2], var='tasmin', percentile=10, time_range=[base_dt1, base_dt2], save_to_file=file_name)
    
    To load the dictionary from file just do the following:
    
    >>> import pickle
    >>> with open(file_name, 'rb') as f:
    ...     pd = pickle.load(f)

.. _examples_label:

Examples
---------
>>> import icclim
>>> import datetime

Example 1: indice SU
~~~~~~~~~~~~~~~~~~~~~
>>> files = ['tasmax_day_CNRM-CM5_historical_r1i1p1_19950101-19991231.nc', 'tasmax_day_CNRM-CM5_historical_r1i1p1_20000101-20041231.nc', 'tasmax_day_CNRM-CM5_historical_r1i1p1_20050101-20051231.nc']
>>> dt1 = datetime.datetime(1998,1,1)
>>> dt1 = datetime.datetime(2005,12,31)
>>> out_f = 'SU_JJA_CNRM-CM5_historical_r1i1p1_1998-2005.nc' # summer season values of SU
>>> icclim.indice(indice_name='SU', in_files=files, var_name='tasmax', slice_mode='JJA', out_file=out_f)

Example 2: indice ETR
~~~~~~~~~~~~~~~~~~~~~~
>>> files_tasmax = [tasmax_day_CNRM-CM5_historical_r1i1p1_19300101-19341231.nc, tasmax_day_CNRM-CM5_historical_r1i1p1_19350101-19391231.nc]
>>> files_tasmin = [tasmin_day_CNRM-CM5_historical_r1i1p1_19300101-19341231.nc, tasmin_day_CNRM-CM5_historical_r1i1p1_19350101-19391231.nc]
>>> out_f = 'ETR_month_CNRM-CM5_historical_r1i1p1_1930-1939.nc' # monthly values of ETR
>>> icclim.indice(indice_name='ETR', in_files=files_tasmax, var_name='tasmax', slice_mode='month', in_files2=files_tasmin, var_name2='tasmin', out_file=out_f)

.. warning:: The couple of parameters ``in_files`` and ``var_name`` corresponds to daily maximum temperature. Likewise, ``in_files2`` and ``var_name2`` -- to daily minimum temperature.

Example 3: indice TG90p
~~~~~~~~~~~~~~~~~~~~~~~
>>> files = [tas_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc]
>>>
>>> ## step 1: we compute the 90th daily percetile for the base period
>>> base_dt1 = datetime.datetime(1961,01,01)
>>> base_dt2 = datetime.datetime(1990,12,31)
>>> pd90 = icclim.get_percentile_dict(in_files=files, var_name='tas', percentile=90, time_range=[base_dt1, base_dt2])
>>>
>>> ## step 2: we compute the indice
>>> dt1 = datetime.datetime(1980,01,01)
>>> dt2 = datetime.datetime(2000,12,31)
>>> out_f = 'TG90p_AMJJAS_CNRM-CM5_historical_r1i1p1_1980-2000.nc' # summer half-year values of TG90p
>>> icclim.indice(indice_name='TG90p', in_files=files, var_name='tas', slice_mode='AMJJAS', percentile_dict=pd90, out_file=out_f)

Example 4: indice CW
~~~~~~~~~~~~~~~~~~~~
>>> files_tas = [tas_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc]
>>> files_pr = [pr_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc]
>>> 
>>> base_period = [datetime.datetime(1961,01,01), datetime.datetime(1990,12,31)]
>>> 
>>> ## step 1: we compute 25th daily percentile of 'tas'
>>> pd25_tas = icclim.get_percentile_dict(in_files=files_tas, var_name='tas', percentile=25, time_range=base_period)
>>> 
>>> ## step 2: we compute 75th daily percentile of 'pr'
>>> pd75_pr = icclim.get_percentile_dict(in_files=files_pr, var_name='pr', percentile=75, time_range=base_period, precipitation=True)
>>> 
>>> ## step 3: we compute the indice
>>> tr = [datetime.datetime(1939,01,01), datetime.datetime(1945,12,31)] # monthly values of CW
>>> out_f = 'CW_month_CNRM-CM5_historical_r1i1p1_1930-1945'
>>> icclim.indice(indice_name='CW', time_range=tr, in_files=files_tas, var_name='tas', percentile_dict=pd25_tas, in_files2=files_pr, var_name2='pr', percentile_dict2=pd75_pr, out_file=out_f)

.. warning:: The set of parameters ``in_files``, ``var_name`` and ``percentile_dict`` corresponds to daily mean temperature. Likewise, ``in_files2``, ``var_name2``, ``percentile_dict2`` -- to daily precipitation flux (liquide phase).


.. _table_indice_sourceVar_label:

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



Elementary functions for computing indices
-------------------------------------------


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
    :members: TN10p_calculation, WSDI_calculation, CW_calculation

.. warning:: Units of "arr" and percentile values of "percentile_dict" must be the same.




Utility functions
-----------------

.. _icclim_regrid:

:mod:`util.regrid` -- Regridding
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
It is possible to do simple regridding, using the `util.regrid.py <https://github.com/tatarinova/icclim/blob/master/icclim/util/regrid.py>`_ module:

.. automodule:: util.regrid
    :members: get_regridded_var, write2netCDF_after_regridding


>>> import icclim.util.regrid as regrid


For example, we have 2 files with different resolutions:

>>> f1 = 'tasmax_Amon_bcc-csm1-1_historical_r1i1p1_185001-201212.nc' # source grid (64 x 128), will be regridded to the destination grid
>>> f2 = 'tasmax_day_CNRM-CM5_historical_r1i1p1_18500101-20121231.nc' # destination grid (128 x 256)
>>> arr = regrid.get_regrided_var(f_src=f1, f_dst=f2, varname='tasmax') # numpy array with spatial dimensions (128,256)
>>> f1_regridded = 'regridded_tasmax_Amon_bcc-csm1-1_historical_r1i1p1_185001-201212.nc' # name of the new netCDF file
>>> regrid.write2netCDF_after_regridding(arr, f_src=f1, f_dst=f2, f_out=f1_regridded, var_src='tasmax')

See also `more detailed example <https://github.com/tatarinova/icclim/blob/master/icclim/scripts_examples/example_regrid.py>`_.

.. warning:: The package `ESMF/ESMPy <https://www.earthsystemcog.org/projects/esmpy/>`_ must be installed.


:mod:`util.spatial_stat` -- Spatial statistics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Utility functions for spatial statistics like computing of spatial average, spatial standard deviation, etc:

1. :func:`util.spatial_stat.get_weight_matrix` computes weights, giving more weight to the pixels on the poles
2. :func:`util.spatial_stat.multiply_to_weight_matrix` returns new values to be used for spatial statistics

.. automodule:: util.spatial_stat
    :members: get_weight_matrix, multiply_to_weight_matrix

.. warning:: Only for rectangular "lat/lon" grid.
