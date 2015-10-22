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



.. note:: If ``slice_mode`` is ``None``: whole period of time range will be processed. 


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

.. _pctl_methods_label:

**Computing percentile thresholds** 
------------------------------------

Percentile thresholds are used as thresholds for calculation of percentile-based indices 
and are computed from values inside a reference period, named *base period* which is usually 30 years (``base_period_time_range`` parameter).


There are two methods for calculation of percentile thresholds: 

**1. For temperature indices**, theses thresholds are computed *for each calendar day* from samples (5-day window centred on the 
calendar day in the base period) which depend on :ref:`window_width <window_width_label>`,  :ref:`only_leap_years <only_leap_years_label>` 
and  :ref:`ignore_Feb29th <ignore_Feb29th_label>` parameters.



In *ICCLIM* these thresholds represent a dictionary with 365 (if :ref:`ignore_Feb29th <ignore_Feb29th_label>` is True) 
or 366 (:ref:`ignore_Feb29th <ignore_Feb29th_label>` is False) calendar days as keys, and 2D arrays as values.

.. note:: A calendar day key of the dictionary is composed from the corresponding month and day, separated by a comma, i.e. to get for example the 2D array with percentiles for April 13th it will looks like *my_perc_dict[4,13]*.


The percentile thresholds are different for "in-base" years (years inside the base period) and "out-of-base" years. 
For "in-base" years, *ICCLIM* uses the *bootstrapping procedure*, which is 
explained in this article: `Avoiding Inhomogeneity in Percentile-Based Indices of 
Temperature Extremes (Zhang et al.) <http://etccdi.pacificclimate.org/docs/Zhangetal05JumpPaper.pdf>`_  - see 
the resampling algorithm in the section **4. Removing the "jump"**.

.. warning:: Computing of percentile thresholds with the bootstrapping procedure may take some time! For example, a 30-yr base period requires (30-1) times of computing percentiles for each "in-base" year!, i.e. 30*(30-1) times in total (+1 time without bootstrapping for "out-of-base" years). 



**2. For precipitation indices**, the thresholds are computed from the set of wet days (i.e. days when daily precipitation amount >= 1.0 mm) in the base period. In *ICCLIM* these thresholds represent an 2D array.  



Both methods could use 2 types of :ref:`interpolation <interpolation_label>`.


The `calc_percentiles.py <link>`_ module contains get_percentile_dict(...) and get_percentile_arr(...) for the described methods.  

.. _window_width_label:

``window_width``
~~~~~~~~~~~~~~~~~

The ``window width`` is used for getting samples for percentiles computing and is set to 5: percentiles-based indices use 5-day window.
The window is centred on a certain calendar day, for example:
    - **April 13th**, we take the values for *April 11th*, *April 12th*, *April 13th*, *April 14th* and *April 15th* of each year of the base period.
    - **January 1st**, we take all days of *December 30th*, *December 31st*, *January 1st*, *January 2nd* and *January 3rd*.

Hence, for a base period of 30 years and 5-day window width for each calendar day (except February 29th), there are 150 values ( 30 * 5 )
to compute its percentile value.


.. _only_leap_years_label:


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

.. warning:: If :ref:`ignore_Feb29th <ignore_Feb29th_label>` is True, the ``only_leap_years`` does not make sense!

.. _interpolation_label:

``interpolation``
~~~~~~~~~~~~~~~~~~~~

Computing of a percentile value could use ``linear`` interpolation or the interpolation proposed 
by `Hyndman and Fan (1996) <http://amherst.edu/media/view/129116/original/Sample+Quantiles.pdf>`_, named
in *ICCLIM* as ``hyndman_fan`` interpolation.


 
``out_unit``
~~~~~~~~~~~~~~~
Percentile-based indices (TX10p, TX90p, TN10p, TN90p, TG10p, TG90p, R75p, R95p and R99p) could be returned as number of days (``out_unit`` = "days") 
or as percentage of days (``out_unit`` = "%").


**Custom indices**
-------------------

It is possible to define custom indices setting all the necessary information to ``user_indice`` parameter. 

``user_indice``
~~~~~~~~~~~~~~~~


``user_indice`` is a dictionary with following keys:

+--------------------------+-------------------------------------------+--------------------------------------------------------------------------------------+
|Key                       |Type of value                              |Description                                                                           |
+==========================+===========================================+======================================================================================+		
|"indice_name"             |*str*                                      |Name of custom indice.                                                                |
+--------------------------+-------------------------------------------+--------------------------------------------------------------------------------------+
|"calc_operation"          |*str*                                      |Type of calculation. See below for more details.                                      |
+--------------------------+-------------------------------------------+--------------------------------------------------------------------------------------+
|"logical_operation"       |*str*                                      |"gt", "lt", "get", "let" or "e"                                                       |
+--------------------------+-------------------------------------------+--------------------------------------------------------------------------------------+
|"thresh"                  |*float* or *str*                           |In case of percentile-based indice, must be string which starts with "p" (e.g. 'p90').|
+--------------------------+-------------------------------------------+--------------------------------------------------------------------------------------+
|"link_logical_operations" |*str*                                      |"and" or "or"                                                                         |
+--------------------------+-------------------------------------------+--------------------------------------------------------------------------------------+
|"extreme_mode"            |*str*                                      |"min" or "max" for computing min or max of running mean/sum.                          |
+--------------------------+-------------------------------------------+--------------------------------------------------------------------------------------+
|"window_width"            |*int*                                      |Used for computing running mean/sum.                                                  |
+--------------------------+-------------------------------------------+--------------------------------------------------------------------------------------+
|"coef"                    |*float*                                    |Constant for multiplying input data array.                                            |
+--------------------------+-------------------------------------------+--------------------------------------------------------------------------------------+
|"date_event"              |*bool*                                     |To keep or not the date of event. See below for more details.                         |
+--------------------------+-------------------------------------------+--------------------------------------------------------------------------------------+
|"var_type"                |*str*                                      |"t" or "p". See below for more details.                                               |
+--------------------------+-------------------------------------------+--------------------------------------------------------------------------------------+
|"ref_time_range"          |[*datetime.datetime*, *datetime.datetime*] |Reference time range (past period) for anomalies computing.                           |
+--------------------------+-------------------------------------------+--------------------------------------------------------------------------------------+

Below some additional information about ``user_indice`` keys.

- key ``calc_operation``

=======================================	===========================================================================
value									description
=======================================	===========================================================================
'max'									maximum
'min'									minimum
'sum'									sum
'mean'									mean
'nb_events'								number of events satisfying the selected condition
'max_nb_consecutive_events'             maximum number of consecutive events satisfying the selected condition
'run_mean'								max or min of running mean
'run_sum'								max or min of running sum 
'anomaly'								mean(future period) - mean(past period)
=======================================	===========================================================================


- key ``date_event`` allows to keep date(s) of the event, it if is ``True``:

 	- For simple statistics (min, max) in output netCDF file will be created "date_event" variable with numerical dates of the first occurrence of the event for each pixel. 
 		
 	- For other operations in output netCDF file will be created "date_event_start" and "date_event_end" variables with numerical dates of the event for each pixel.
 
	.. note:: The "date_event", "date_event_start" and "date_event_end" netCDF variables have the same shape as indice's one.
	
	.. warning:: "Date_event"/"date_event_start"/"date_event_end" has no value:
	
			- for certain pixels, if event is not found, 
			- for all pixels of "in-base" years (years in base period) for temperature percentile-based indices - it is not possible to determine the correct date of the event because of averaging of indice in "in-base" year.   	


- key ``var_type`` is used to define the method of percentile thresholds computing. The methods are different for temperature and precipitation variables (more detailed :ref:`here <pctl_methods_label>`):

	- If 't' (temperature variable), percentile thresholds is computed for each calendar day, using  *the bootstrapping procedure*. 
		
	- If 'p' (precipitation variable), percentile threshold is calculated for whole set of values corresponding to wet days (i.e. days with daily precipitation amount >= 1.0 mm) in base period.



Correspondence table "cal_operation" -- required/optional parameters:

+-------------------------------+-------------------------------+-----------------------+
|"calc_operation" value         |  required parameters          | optional_parameters   |	
+===============================+===============================+=======================+
|'max'/'min'                    |                               |'coef',                |
|                               |                               |'logical_operation',   |						
|                               |                               |'thresh',              |
|                               |                               |'date_event'           |
+-------------------------------+-------------------------------+-----------------------+
|'mean'/'sum'                   |                               |'coef',                |
|                               |                               |'logical_operation',   |
|                               |                               |'thresh',              |
+-------------------------------+-------------------------------+-----------------------+
|'nb_events'                    |'logical_operation',           |'coef',                |
|                               |'thresh',                      |'date_event'           |
|                               |                               |                       |
|                               |'link_logical_operations'      |                       |
|                               |(if multivariable indice),     |                       |
|                               |                               |                       |
|                               |'var_type'                     |                       |
|                               |(if percentile-based indices)  |                       |
+-------------------------------+-------------------------------+-----------------------+
|'max_nb_consecutive_events'    |'logical_operation',           |'coef',                |
|                               |'thresh'                       |'date_event'           |
|                               |                               |                       |
+-------------------------------+-------------------------------+-----------------------+
|'run_mean'/'run_sum'           |'extreme_mode',                |'coef',                |
|                               |'window_width'                 |'date_event'           |
+-------------------------------+-------------------------------+-----------------------+
|'anomaly'                      |'ref_time_range'               |                       |
+-------------------------------+-------------------------------+-----------------------+

.. warning:: The 'window_width' here is a parameter for calculation of statistics in running window. Do not confuse with 'window_width' of :func:`icclim.indice`, which is used for computing of temperature percentiles and set to 5 as default. 

.. note:: See examples for computing of custom indices :ref:`here <examples_user_indices_label>`.


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



Example 4: multivariable percentile-based indices CD, CW, WD, WW
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
These indices could be computed as custom indices, see an example here :ref:`here <examples_CD_CW_WD_WW_label>`


.. _examples_user_indices_label:

Example 5: Custom indice (max)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python
	
	import icclim.util.callback as callback
	
	my_indice_params = {'indice_name': 'my_indice',
	                    'calc_operation': 'max'
	                   }
	
	file_tas = 'tas_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc'
	out_f = 'my_indice.nc'
	
	icclim.indice(user_indice=my_indice_params, in_files=file_tas, var_name='tas', slice_mode='year', out_file=out_f, callback=callback.defaultCallback2)


Example 6: Custom indice (min positive + date)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
We want to find min temperature which is > 0 degrees Celsius and to define its date of year.

.. warning:: If input data in Kelvin, then 'thresh' must be in Kelvin also.

.. note:: An additional variable will be created in output netCDF file: "date_event" with the date of the *first* occurrence of min positive.


.. code-block:: python

	my_indice_params = {'indice_name': 'my_indice',
	                    'calc_operation': 'min',
	                    'logical_operation': 'gt',
	                    'thresh': 0 + 273.15, ### input data in Kelvin ==> threshold in Kelvin! 
	                    'date_event': True
	                   }
	
	file_tasmin = 'tasmin_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc'
	out_f = 'my_indice.nc'
	
	icclim.indice(user_indice=my_indice_params, in_files=file_tasmin, var_name='tasmin', slice_mode='year', out_file=out_f, callback=callback.defaultCallback2)


Example 7: Custom indice (mean of selected period)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note:: ``slice_mode`` must be ``None`` to apply the operation to the whole period of selected time range.

.. code-block:: python

	my_indice_params = {'indice_name': 'my_indice',
	                    'calc_operation': 'mean'
	                   }
	
	file_tas = 'tas_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc'
	out_f = 'my_indice.nc'
	
	tr = [datetime.datetime(1901,01,01), datetime.datetime(1920,12,31)]
	
	icclim.indice(user_indice=my_indice_params, in_files=file_tas, var_name='tas', slice_mode=None, time_range=tr, out_file=out_f, callback=callback.defaultCallback2)


Example 8: Custom indice (number of days when tas < 15 degrees Celsius)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note:: If 'calc_operation' is *'max_nb_consecutive_events'*, then max number of consecutive days for the same condition will be computed. 

.. code-block:: python

	my_indice_params = {'indice_name': 'my_indice',
	                    'calc_operation': 'nb_events', ### 'calc_operation': 'max_nb_consecutive_events'
	                    'logical_operation': 'lt',
	                    'thresh': 15 + 273.15 ### input data in Kelvin ==> threshold in Kelvin!
	                   }

	file_tas = 'tas_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc'
	out_f = 'my_indice.nc'
	
	icclim.indice(user_indice=my_indice_params, in_files=file_tas, var_name='tas', slice_mode='SON', out_unit='days', out_file=out_f, callback=callback.defaultCallback2)


Example 9: Custom indice (percentage of days when tasmax > 80th pctl + date)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note:: If 'calc_operation' is *'max_nb_consecutive_events'*, then max number of consecutive days for the same condition will be computed. 

.. note:: 80th pctl: 80th percentile of tasmax in base period

.. note:: Two additional variables will be created in output netCDF file: "date_event_start" (the date of the first occurence of tasmax > 80th pctl) and "date_event_end" (the date of the last occurence of tasmax > 80th pctl).

.. code-block:: python

	my_indice_params = {'indice_name': 'my_indice',
	                    'calc_operation': 'nb_events', ### 'calc_operation': 'max_nb_consecutive_events'
	                    'logical_operation': 'gt',
	                    'thresh': 'p80',
	                    'var_type': 't',
	                    'date_event': True
	                   }
	
	file_tasmax = 'tasmax_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc'
	out_f = 'my_indice.nc'
	bp = [datetime.datetime(1960,01,01), datetime.datetime(1969,12,31)]
	
	icclim.indice(user_indice=my_indice_params, in_files=file_tasmax, var_name='tasmax', slice_mode='year', base_period_time_range=bp, out_unit='%', out_file=out_f, callback=callback.defaultCallback2)


Example 10: Custom indice (number of days when daily precipitation amount > 85th pctl)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note:: If 'calc_operation' is *'max_nb_consecutive_events'*, then max number of consecutive days for the same condition will be computed. 

.. note:: daily precipitation amount: daily precipitation amount on a wet day (RR >= 1.0 mm)

.. note:: 85th pctl: percentile of precipitation on wet days in base period

.. code-block:: python

	my_indice_params = {'indice_name': 'my_indice',
	                    'calc_operation': 'nb_events', ### 'calc_operation': 'max_nb_consecutive_events'
	                    'logical_operation': 'gt',
	                    'thresh': 'p85',
	                    'var_type': 'p'	                    
	                   }
	
	file_pr = 'pr_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc'
	out_f = 'my_indice.nc'
	
	icclim.indice(user_indice=my_indice_params, in_files=file_pr, var_name='pr', slice_mode='year', base_period_time_range=bp, out_unit='days', out_file=out_f, callback=callback.defaultCallback2)


Example 11: Custom indice (max number of consecutive days when tasmax >= 25 degrees Celsius + date)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note:: Two additional variables will be created in output netCDF file: "date_event_start" (the first date of the found sequence) and "date_event_end" (the last date of the found sequence). 

.. warning:: If there are several sequences of the same length, the "date_event_start" and "date_event_end" will correspond to the *first* sequence.

.. code-block:: python

	my_indice_params = {'indice_name': 'my_indice',
	                    'calc_operation': 'max_nb_consecutive_events',
	                    'logical_operation': 'get',
	                    'thresh': 25 + 273.15, ### input data in Kelvin ==> threshold in Kelvin!
	                    'date_event': True
	                   }

	file_tasmax = 'tasmax_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc'
	out_f = 'my_indice.nc'
	
	icclim.indice(user_indice=my_indice_params, in_files=file_tasmax, var_name='tasmax', slice_mode='year', out_file=out_f, callback=callback.defaultCallback2)

Example 12: Custom indice (max of sum of precipitation in 10 consecutive days)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

	my_indice_params = {'indice_name': 'my_indice',
	                    'calc_operation': 'run_sum',
			    'extreme_mode': 'max',
			    'window_width': 10
	                   }

	file_pr = 'pr_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc'
	out_f = 'my_indice.nc'
	
	icclim.indice(user_indice=my_indice_params, in_files=file_pr, var_name='pr', slice_mode=['season',[4,5,6,7,8]], out_file=out_f, callback=callback.defaultCallback2)


Example 13: Custom indice (min of mean of tasmin in 7 consecutive days + date)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note:: Two additional variables will be created in output netCDF file: "date_event_start" (the date corrsponding to the beggining of the "window" satisfying the condition) and "date_event_end" (the date corrsponding to the end of the "window" satisfying the condition).

.. warning:: If several "windows" with the same result are found, the "date_event_start" and "date_event_end" will correspond to the *first* one.


.. code-block:: python

	my_indice_params = {'indice_name': 'my_indice',
	                    'calc_operation': 'run_mean',
			    'extreme_mode': 'min',
			    'window_width': 7,
			    'date_event': True
	                   }

	file_tasmin = 'tasmin_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc'
	out_f = 'my_indice.nc'
	
	icclim.indice(user_indice=my_indice_params, in_files=file_tasmin, var_name='tasmin', slice_mode=['season',([11,12],[1,2])], out_file=out_f, callback=callback.defaultCallback2)

Example 14: Custom indice (anomaly of tasmax between 2 period of 30 years)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note:: Result could be returned as percentage value relative to mean value of reference period, if ``out_unit='%'``. 

.. code-block:: python

	my_indice_params = {'indice_name': 'my_indice',
                            'calc_operation': 'anomaly',
	                    'ref_time_range': [datetime.datetime(1901,01,01), datetime.datetime(1930,12,31)], ### reference period: past period 

	                   }

	file_tasmax = 'tasmax_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc'
	out_f = 'my_indice.nc'
	tr = [datetime.datetime(1971,01,01), datetime.datetime(2000,12,31)] ### studied period: future period
	
	icclim.indice(user_indice=my_indice_params, in_files=file_tasmax, var_name='tasmax', time_range=tr, out_file=out_f, callback=callback.defaultCallback2)


Example 15: Multivariable custom indice (number of days when tasmin >= 10 degrees Celsius and tasmax > 25 degrees Celsius)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note:: If 'calc_operation' is *'max_nb_consecutive_events'*, then max number of consecutive days for the same condition will be computed. 

.. code-block:: python

	my_indice_params = {'indice_name': 'my_indice',
	                    'calc_operation': 'nb_events', ### 'calc_operation': 'max_nb_consecutive_events'
	                    'logical_operation': ['get', 'gt'],
	                    'thresh': [10+273.15, 25+273.15], ### input data in Kelvin ==> threshold in Kelvin!
	                    'link_logical_operations': 'and'	                    
	                   }

	file_tasmin = 'tasmin_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc'
	file_tasmax = 'tasmax_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc'
	out_f = 'my_indice.nc'
	
	icclim.indice(user_indice=my_indice_params, in_files=[file_tasmin, file_tasmax], var_name=['tasmin', 'tasmax'], slice_mode='JJA', out_unit='days', out_file=out_f, callback=callback.defaultCallback2)


Example 16: Multivariable custom indice (percentage of days when tasmin >= 10 degrees Celsius and tasmax > 90th pctl   + date)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note:: If 'calc_operation' is *'max_nb_consecutive_events'*, then max number of consecutive days for the same condition will be computed. 

.. note:: It is possible to use numeric and percentile threshold at the time.

.. code-block:: python

	my_indice_params = {'indice_name': 'my_indice',
	                    'calc_operation': 'nb_events', ### 'calc_operation': 'max_nb_consecutive_events'
	                    'logical_operation': ['get', 'gt'],
	                    'thresh': [10+273.15, 'p90'], ### input data in Kelvin ==> threshold in Kelvin!
	                    'var_type': 't',  ### or ['-','t']
	                    'link_logical_operations': 'and',
	                    'date_event': True
	                   }

	file_tasmin = 'tasmin_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc'
	file_tasmax = 'tasmax_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc'
	out_f = 'my_indice.nc'
	
	bp = [datetime.datetime(1960,01,01), datetime.datetime(1969,12,31)]
	icclim.indice(user_indice=my_indice_params, in_files=[file_tasmin, file_tasmax], var_name=['tasmin', 'tasmax'], slice_mode='JJA', base_period_time_range=bp, out_unit='%', out_file=out_f, callback=callback.defaultCallback2)


.. _examples_CD_CW_WD_WW_label:

Example 17: CW as a custom indice (number of days when tas < 25th pctl and precip. > 75th pctl)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note:: If 'calc_operation' is *'max_nb_consecutive_events'*, then max number of consecutive days for the same condition will be computed. 

4 compound indices defined in http://eca.knmi.nl/documents/atbd.pdf (see the section 5.3.3 "Compound indices") are 
based on daily precipitation (RR) and mean temperature (TG) variables:

	- CD (cold/dry days): (TG < 25th pctl) and (RR < 25th pctl) 
	- CW (cold/wet days): (TG < 25th pctl) and (RR > 75th pctl)
	- WD (warm/dry days): (TG > 75th pctl) and (RR < 25th pctl)
	- WW (warm/wet days): (TG > 75th pctl) and (RR > 75th pctl)
 
.. note:: RR is a daily precipitation on a *wet* day, and its percentile value is computed from set of wet days also.

.. note:: Percentiles thresholds computing uses differents methods as it was described :ref:`here <pctl_methods_label>`.


.. code-block:: python

	my_indice_params = {'indice_name': 'my_indice',
	                    'calc_operation': 'nb_events', ### 'calc_operation': 'max_nb_consecutive_events'
	                    'logical_operation': ['lt', 'gt'],
	                    'thresh': ['p25', 'p75'], 
	                    'var_type': ['t', 'p'],
	                    'link_logical_operations': 'and'	                    
	                    }

	file_pr= 'pr_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc'
	file_tas = 'tas_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc'
	out_f = 'my_indice.nc'
	
	bp = [datetime.datetime(1960,01,01), datetime.datetime(1969,12,31)]
	icclim.indice(user_indice=my_indice_params, in_files=[file_tas, file_pr], var_name=['tas', 'pr'], slice_mode='year', out_unit='days', base_period_time_range=bp, out_file=out_f, callback=callback.defaultCallback2)

Example 18: Multivariable custom indice (number of days when tasmax > 90th pctl and tasmin >= 10 and precipitation < 30th pctl)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note:: If 'calc_operation' is *'max_nb_consecutive_events'*, then max number of consecutive days for the same condition will be computed.

.. code-block:: python

	my_indice_params = {'indice_name': 'my_indice',
                            'calc_operation': 'nb_events', ### 'calc_operation': 'max_nb_consecutive_events'
                            'logical_operation': ['gt', 'get', 'lt'],
                            'thresh': ['p90', 10+273.15, 'p30'], 
                            'var_type': ['t', '-', 'p'],
                            'link_logical_operations': 'and'                        
                            }
	file_pr= 'pr_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc'
	file_tasmax = 'tasmax_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc'
	file_tasmin = 'tasmin_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc'
	out_f = 'my_indice.nc'
	
	bp = [datetime.datetime(1960,01,01), datetime.datetime(1969,12,31)]
	icclim.indice(user_indice=my_indice_params, in_files=[file_tasmax, file_tasmin, file_pr], var_name=['tasmax', 'tasmin', 'pr'], slice_mode='SON', out_unit='days', base_period_time_range=bp, out_file=out_f, callback=callback.defaultCallback2)


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
|                                                            | daily mean temperature +                    |
|CD, CW, WD, WW                                              | daily precipitation flux (liquide phase)    |
+------------------------------------------------------------+---------------------------------------------+



Basic functions for computing indices
-------------------------------------------


The `calc_indice.py <https://github.com/tatarinova/icclim/blob/master/icclim/calc_indice.py>`_ module contains basic routines for manipulating 3D arrays.
Below are some of them.

.. note:: A function name is composed of an indice name and "_calculation" (example: FD_calculation).

.. note:: Input array(s) could be filled (numpy.ndarray) or masked (numpy.ma.MaskedArray). The output array type corresponds to the input array type.

.. warning::
    If input array is filled, a fill_value (parameter "fill_val") must be provided:
    
    >>> FD_calculation(my_3D_array, fill_val=99999)
    
    If input array is masked, the "fill_val" is ignored:
    
    >>> FD_calculation(my_3D_masked_array)



.. automodule:: calc_indice
    :members: TNx_calculation, CSU_calculation, DTR_calculation, TN10p_calculation, WSDI_calculation
   



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
