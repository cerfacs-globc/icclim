Python API
==========



:func:`icclim.indice` -- Compute indice
----------------------------------------


This is the main function to compute an indice:

.. automodule:: icclim
    :members: indice




.. note:: For the variable names see the :ref:`correspondence table "indice - source variable" <table_indice_sourceVar_label>` 


Below some additional information about input parameters.

``in_files`` and ``var_name``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``in_files`` parameter could be *string*, *list of strings* or *list of lists of strings*:

+---------------------------------+----------------------------------------------------------+---------------------------------------------------------------------------------------------------------+
|                                 | single input file per variable                           |  several input files per variable                                                                       | 
+=================================+==========================================================+=========================================================================================================+
| simple indice                   |   ``var_name`` = 'tasmax'                                |   ``var_name`` = 'tasmax'                                                                               |
| (based on a single variable)    +----------------------------------------------------------+---------------------------------------------------------------------------------------------------------+
|                                 | ``in_files`` = 'tasmax_1990-2010.nc'                     |  ``in_files`` = ['tasmax_1990-2000.nc', 'tasmax_2000-2010.nc']                                          |
+---------------------------------+----------------------------------------------------------+---------------------------------------------------------------------------------------------------------+
| multivariable indice            |       ``var_name`` = ['tas', 'pr']                       |        ``var_name`` = ['tas', 'pr']                                                                     |
| (based on several variables)    +----------------------------------------------------------+---------------------------------------------------------------------------------------------------------+
|                                 |  ``in_files`` = ['tas_1990-2010.nc', 'pr_1990-2010.nc']  |   ``in_files`` = [['tas_1990-2000.nc', 'tas_2000-2010.nc'], ['pr_1990-2000.nc'], 'pr_2000-2010.nc']]    | 
+---------------------------------+----------------------------------------------------------+---------------------------------------------------------------------------------------------------------+

.. warning:: The order of variables in ``var_name``/``in_files`` must be ['tasmax', 'tasmin'] for indices DTR, ETR and vDTR and ['tas', 'pr'] for indices CD, CW, WD and WW.

``slice_mode``
~~~~~~~~~~~~~~
The ``slice_mode`` parameter defines a desired temporal aggregation. Thus, each indice can be calculated at annual, winter half-year, summer half-year, winter, spring,
summer, autumn and monthly frequency: 

+----------------------+-----------------------+
| Value (string)       | Description           |
+======================+=======================+
|  ``year`` (default)  |    annual             |
+----------------------+-----------------------+
|  ``month``           | monthly (all months)  |
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


Monthly time series with months selected by user:

	>>> slice_mode = ['month',[4,5,11]] # indice will be computed only for April, May and November
	
	or 
	
	>>> slice_mode = ['month',[4]] # indice will be computed only for April
	

User defined seasons: 

	>>> slice_mode = ['season',[4,5,6,7]]
	
	or 
	
	>>> slice_mode = ['season',([11,12],[1])]

	.. note:: For a season composed of two years, months must be separated in *two lists* and united in a *tuple*: ([months of YYYY], [months of YYYY+1])  




``threshold``
~~~~~~~~~~~~~
It is possible to set a user define threshold for indices **SU** (default threshold: 25), **CSU** (default threshold: 25), **TR** (default threshold: 20).
The threshold could be one value:

>>> threshold = 30

or a list of values:

>>> threshold = [20,25,30]

.. note:: Currently, temperature thresholds are only avaliable and units of ``threshold`` must be in degrees Celsius. 

``transfer_limit_Mbytes``
~~~~~~~~~~~~~~~~~~~~~~~~~~

In case of OPeNDAP datasets, if requested datasets exceed the transfer limit, ICCLIM applies chunking method to transfer and process.
Chunk size is dynamically adapted to the data maximum transfer size. Data cutting is realized along the time dimension (spatial chunking).
    
The ``transfer_limit_Mbytes`` parameter, required to estimate the optimal data chunksize, should be set to the request limit value:

>>> transfer_limit_Mbytes = 500

.. note:: If that does not work, try to reduce the ``transfer_limit_Mbytes`` value.


.. note:: Example of error message, if ``transfer_limit_Mbytes`` is not set or its value is overvalued:

    .. code-block:: rest
    
	context: Error { code = 403; message = "Request too big=1875.0 Mbytes, max=500.0"^;};
        
	...
        
	RuntimeError: NetCDF: Malformed or inaccessible DAP DATADDS


.. note:: If ``transfer_limit_Mbytes`` is set, chunking is applied even for local datasets that could be useful for machines with little RAM.

``callback``
~~~~~~~~~~~~~
The percentage progress bar is printed if the ``callback`` parameter is set to a callback function.
The default callback functions are defined in `util.callback.py <link>`_. 

>>> import util.callback as callback
>>> cb = callback.defaultCallback

.. _ignore_Feb29th_label:

``ignore_Feb29th``
~~~~~~~~~~~~~~~~~~~
If it is ``True``, we kick out February 29th.  

Computing daily percentile thresholds 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


``base_period_time_range``
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Daily percentile values are used as thresholds for calculation of percentile-based indices 
and are computed from values inside a reference period, named *base period* which is usually 30 years (``base_period_time_range`` parameter).

``window_width``
~~~~~~~~~~~~~~~~~

The ``window width`` is used for getting samples for percentiles computing and is set to 5: percentiles-based indices use 5-day window.
The window is centred on a certain calendar day, for example:
    - **April 13th**, we take the values for *April 11th*, *April 12th*, *April 13th*, *April 14th* and *April 15th* of each year of the base period.
    - **January 1st**, we take all days of *December 30th*, *December 31st*, *January 1st*, *January 2nd* and *January 3rd*.

Hence, for a base period of 30 years and 5-day window width for each calendar day (except February 29th), there are 150 values ( 30 * 5 )
to compute its percentile value.





``only_leap_years``
~~~~~~~~~~~~~~~~~~~~

The ``only_leap_years`` parameter selects which of two methods to use for calculating a percentile value 
for the calendar day of **February 29th**:

    - if ``True``, we take only leap years, i.e. for example for the base period of 1980-1990 and 5-day window width, we take the values corresponding to the following dates:

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


    - if ``False``, for the same base period and window width, we have:

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

.. note:: If :ref:`ignore_Feb29th <ignore_Feb29th_label>` is True, the ``only_leap_years`` does not make sense!


``interpolation``
~~~~~~~~~~~~~~~~~~~~

Computing of a percentile value could use *linear* interpolation or the interpolation proposed 
by `Hyndman and Fan (1996) <http://amherst.edu/media/view/129116/original/Sample+Quantiles.pdf>`_, named
in icclim as "hyndman_fan" interpolation.

``save_percentiles_to_file``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To save percentile thresholds in a file, the ``save_percentiles_to_file`` should be set as a list of 2 strings, 
the first one is a file name and the second one is the option: 'a' (without bootstrapping procedure) or 'b' (with and without bootstrapping procedure).

	>>> save_percentiles_to_file = ['./10th_pctl_tasmax_base_period_1961-1970', 'a']

The percentiles are saved as a big dictionary::

	>>> import pickle
	>>> with open(file_perc, 'rb') as f:
	...     pd = pickle.load(f)
 
To get 2D numpy array with percentiles for 31th November:

	>>> arr_10th_pctl_31November =  pd['tasmax']['out_of_base'][11,31]



 
``out_unit``
~~~~~~~~~~~~~~~
Indices TX10p, TX90p, TN10p, TN90p, TG10p and TG90p could be returned as number days (``out_unit`` = "days") 
or as percentage of days (``out_unit`` = "%").


Examples
---------
>>> import icclim
>>> import datetime

Example 1: indice SU
~~~~~~~~~~~~~~~~~~~~~
>>> files = ['tasmax_day_CNRM-CM5_historical_r1i1p1_19950101-19991231.nc', 'tasmax_day_CNRM-CM5_historical_r1i1p1_20000101-20041231.nc', 'tasmax_day_CNRM-CM5_historical_r1i1p1_20050101-20051231.nc']
>>>
>>> dt1 = datetime.datetime(1998,1,1)
>>> dt2 = datetime.datetime(2005,12,31)
>>>
>>> out_f = 'SU_JJA_CNRM-CM5_historical_r1i1p1_1998-2005.nc' # OUTPUT FILE: summer season values of SU
>>>
>>> icclim.indice(indice_name='SU', in_files=files, var_name='tasmax', time_range=[dt1, dt2], slice_mode='JJA', out_file=out_f)


Example 2: indice ETR
~~~~~~~~~~~~~~~~~~~~~~
>>> files_tasmax = ['tasmax_day_CNRM-CM5_historical_r1i1p1_19300101-19341231.nc', 'tasmax_day_CNRM-CM5_historical_r1i1p1_19350101-19391231.nc']
>>> files_tasmin = ['tasmin_day_CNRM-CM5_historical_r1i1p1_19300101-19341231.nc', 'tasmin_day_CNRM-CM5_historical_r1i1p1_19350101-19391231.nc']
>>>
>>> out_f = 'ETR_year_CNRM-CM5_historical_r1i1p1_1930-1939.nc' # OUTPUT FILE: annual values of ETR
>>>
>>> icclim.indice(indice_name='ETR', in_files=[files_tasmax, files_tasmin], var_name=['tasmax', 'tasmin'], slice_mode='year', out_file=out_f)

.. warning:: The order of `var_name` must be ['tasmax', 'tasmin'] and NOT ['tasmin', 'tasmax']. The same for `in_files`.


Example 3: indice TG90p with callback
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
>>> import icclim.util.callback as callback
>>>
>>> f = 'tas_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc'
>>>
>>> # base period
>>> base_dt1 = datetime.datetime(1961,01,01)
>>> base_dt2 = datetime.datetime(1970,12,31)
>>>
>>> # studied period
>>> dt1 = datetime.datetime(1980,01,01)
>>> dt2 = datetime.datetime(2000,12,31)
>>>
>>> out_f = 'TG90p_AMJJAS_CNRM-CM5_historical_r1i1p1_1980-2000.nc' # OUTPUT FILE: summer half-year values of TG90p
>>>
>>> icclim.indice(indice_name='TG90p', in_files=f, var_name='tas', slice_mode='AMJJAS', time_range=[dt1, dt2], base_period_time_range=[base_dt1, base_dt2], out_file=out_f, out_unit='%', callback=callback.defaultCallback2)

Example 4: indice CW
~~~~~~~~~~~~~~~~~~~~~~
>>> file_tas = 'tas_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc'
>>> file_pr = 'pr_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc'
>>> 
>>> base_period = [datetime.datetime(1961,01,01), datetime.datetime(1970,12,31)]
>>>
>>> tr = [datetime.datetime(1939,01,01), datetime.datetime(1945,12,31)] 
>>>
>>> out_f = 'CW_SON_CNRM-CM5_historical_r1i1p1_1930-1945' # OUTPUT FILE: automn season ('SON') values of CW
>>> 
>>> icclim.indice(indice_name='CW', time_range=tr, in_files=[file_tas, file_pr], var_name=['tas', 'pr'], slice_mode='SON', base_period_time_range=base_period, out_file=out_f)

.. warning:: The order of `var_name` must be ['tas', 'pr'] and NOT ['pr', 'tas']. The same for `in_files`.






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
|DTR, ETR, vDTR                                              |  daily maximum + daily minimum temperature  |
+------------------------------------------------------------+---------------------------------------------+
|PRCPTOT, RR1, SDII, CWD, CDD, R10mm, R20mm, RX1day, RX5day, |  daily precipitation flux (liquide phase)   |
|R75p, R75pTOT, R95p, R95pTOT, R99p, R99pTOT                 |                                             |
+------------------------------------------------------------+---------------------------------------------+
|SD, SD1, SD5cm, SD50cm                                      |  daily snowfall flux (solid phase)          |
+------------------------------------------------------------+---------------------------------------------+
|CD, CW, WD, WW                                              |  daily mean temperature +                   |
|                                                            |  daily precipitation flux (liquide phase)   |
+------------------------------------------------------------+---------------------------------------------+



Basic functions for computing indices
-------------------------------------------


The `calc_indice.py <https://github.com/tatarinova/icclim/blob/master/icclim/calc_indice.py>`_ and `calc_indice_perc.py <https://github.com/tatarinova/icclim/blob/master/icclim/calc_indice_perc.py>`_ modules contain basic routines for manipulating 3D arrays.
Below are some of them.

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
It is possible to do simple regridding (only rectangular "lat/lon" grid), using the `util.regrid.py <https://github.com/tatarinova/icclim/blob/master/icclim/util/regrid.py>`_ module:

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

Utility functions for spatial statistics such as computing of spatial average, spatial standard deviation, etc:

1. :func:`util.spatial_stat.get_weight_matrix` computes weights, giving more weight to the pixels on the poles
2. :func:`util.spatial_stat.multiply_to_weight_matrix` returns new values to be used for spatial statistics

.. automodule:: util.spatial_stat
    :members: get_weight_matrix, multiply_to_weight_matrix

.. warning:: Only for rectangular "lat/lon" grid.
