icclim.index(), the main entry point
====================================

icclim exposes a main entry point with :func:`icclim.index`.
It is used to compute both ECA&D indices and user defined indices.
There are quite a lot of options, but only a few of them are needed to compute simple indices.
Our :ref:`how_to` recipes are also a good start to have an idea on how to use `icclim.index`.

Compute climat indices
----------------------

.. autofunction:: icclim.index(**kwargs)

.. note:: For the variable names see the :ref:`correspondence table "index - source variable" <table_index_sourceVar_label>`


Below are some additional information about input parameters.

``in_files`` and ``var_name``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``in_files`` parameter could be *string*, *list of strings* or *list of lists of strings*:

+---------------------------------+----------------------------------------------------------+---------------------------------------------------------------------------------------------------------+
|                                 | single input file per variable                           |  several input files per variable                                                                       |
+=================================+==========================================================+=========================================================================================================+
| simple index                    |  ``var_name`` = 'tasmax'                                 |   ``var_name`` = 'tasmax'                                                                               |
| (based on a single variable)    +----------------------------------------------------------+---------------------------------------------------------------------------------------------------------+
|                                 |  ``in_files`` = 'tasmax_1990-2010.nc'                    |  ``in_files`` = ['tasmax_1990-2000.nc', 'tasmax_2000-2010.nc']                                          |
+---------------------------------+----------------------------------------------------------+---------------------------------------------------------------------------------------------------------+
| multivariable index             |  ``var_name`` = ['tas', 'pr']                            |   ``var_name`` = ['tas', 'pr']                                                                          |
| (based on several variables)    +----------------------------------------------------------+---------------------------------------------------------------------------------------------------------+
|                                 |  ``in_files`` = ['tas_1990-2010.nc', 'pr_1990-2010.nc']  |   ``in_files`` = [['tas_1990-2000.nc', 'tas_2000-2010.nc'], ['pr_1990-2000.nc'], 'pr_2000-2010.nc']]    |
+---------------------------------+----------------------------------------------------------+---------------------------------------------------------------------------------------------------------+

.. _slice_mode:

``slice_mode``
~~~~~~~~~~~~~~
The ``slice_mode`` parameter defines a desired temporal aggregation. Thus, each index can be calculated at annual, winter half-year, summer half-year, winter, spring,
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

| The winter season (``DJF``) of 2000 is composed of December 2000, January 2001 and February 2001.
| Likewise, the winter half-year (``ONDJFM``) of 2000 includes October 2000, November 2000, December 2000, January 2001, February 2001 and March 2001.

Monthly time series with months selected by user:
    >>> slice_mode = ['month',[4,5,11]] # index will be computed only for April, May and November
    or
    >>> slice_mode = ['month',[4]] # index will be computed only for April

User defined seasons:
    >>> slice_mode = ['season',[4,5,6,7]]
    or
    >>> slice_mode = ['season',([11,12],[1])]

    .. note::
        For a season composed of two years, months must be separated in *two lists* and united in a *tuple*:
        ([months of YYYY], [months of YYYY+1])

``threshold``
~~~~~~~~~~~~~
It is possible to set a user define threshold for indices **SU** (default threshold: 25), **CSU** (default threshold: 25),
**TR** (default threshold: 20).
The threshold could be one value:

>>> threshold = 30

or a list of values:

>>> threshold = [20,25,30]

.. note:: Currently, temperature thresholds are only available and should be given in degrees Celsius.

``transfer_limit_Mbytes``
~~~~~~~~~~~~~~~~~~~~~~~~~

The ``transfer_limit_Mbytes`` parameter is required to estimate the optimal data chunk size.
It is used with Dask in order to set the maximum chunk size value.
Note that multiples chunks can be in memory at the same time, a "good" transfer_limit_Mbytes is around 200MB.

>>> transfer_limit_Mbytes = 200

In addition, it is recommended to use `Dask distributed scheduler <http://distributed.dask.org/en/stable/>`_ to maximize
icclim performances.
It can also be on a local machine, to distribute the workload on multiple threads.
To use it, you must install it first:
>>> conda install dask distributed -c conda-forge

Then for a local cluster, a good starting point can be this configuration:
>>> from distributed import Client
>>> Client(memory_limit='12GB', timeout=20, n_workers=1, threads_per_worker=10)

``callback``
~~~~~~~~~~~~~
The percentage progress bar is printed if the ``callback`` parameter is set to a callback function.
The default callback functions are defined in `icclim.util.callback.py <https://github.com/cerfacs-globc/icclim/blob/master/icclim/util/callback.py>`_.

>>> from icclim.util import callback
>>> cb = callback.defaultCallback

.. _ignore_Feb29th_label:

``ignore_Feb29th``
~~~~~~~~~~~~~~~~~~
If it is ``True``, we kick out February 29th.

.. _pctl_methods_label:

Computing percentile thresholds
-------------------------------

Percentile thresholds are used as thresholds for calculation of percentile-based indices
and are computed from values inside a reference period, named *base period* which is usually 30 years (``base_period_time_range`` parameter).


There are two methods for calculation of percentile thresholds:

**1. For temperature indices**, theses thresholds are computed *for each calendar day* from samples (5-day window centred on the
calendar day in the base period) which depend on :ref:`window_width <window_width_label>`,  :ref:`only_leap_years <only_leap_years_label>`
and  :ref:`ignore_Feb29th <ignore_Feb29th_label>` parameters.



In *icclim* these thresholds represent a dictionary with 365 (if :ref:`ignore_Feb29th <ignore_Feb29th_label>` is True)
or 366 (if :ref:`ignore_Feb29th <ignore_Feb29th_label>` is False) calendar days as keys, and 2D arrays as values.

.. note:: A calendar day key of the dictionary is composed from the corresponding month and day, separated by a comma. For example, getting of the 2D array with percentiles for April 13th, looks like *my_perc_dict[4,13]*.


The percentile thresholds are different for "in-base" years (years inside the base period) and "out-of-base" years.
For "in-base" years, *icclim* uses the *bootstrapping procedure*, which is
explained in this article: `Avoiding Inhomogeneity in Percentile-Based Indices of
Temperature Extremes (Zhang et al.) <http://etccdi.pacificclimate.org/docs/Zhangetal05JumpPaper.pdf>`_  - see
the resampling algorithm in the section **4. Removing the "jump"**.

.. warning:: Computing of percentile thresholds with the bootstrapping procedure may take some time! For example, a 30-yr base period requires (30-1) times of computing percentiles for each "in-base" year!, i.e. 30*(30-1) times in total (+1 time without bootstrapping for "out-of-base" years).



**2. For precipitation indices**, the thresholds are computed from the set of wet days (i.e. days when daily precipitation amount >= 1.0 mm) in the base period. In *icclim* these thresholds represent an 2D array.



Both methods could use 2 types of :ref:`interpolation <interpolation_label>`.


The `calc_percentiles.py <https://github.com/cerfacs-globc/icclim/blob/master/icclim/calc_percentiles.py>`_ module contains *get_percentile_dict* and *get_percentile_arr* functions for the described methods.

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
Computing of a percentile value could use ``linear``, also known as type 7 in other software or the interpolation proposed
by `Hyndman and Fan (1996) <https://www.amherst.edu/media/view/129116/original/Sample+Quantiles.pdf>`_, named
in *icclim* as ``hyndman_fan`` interpolation, also known as type 8.


``out_unit``
~~~~~~~~~~~~~~~
Percentile-based indices (TX10p, TX90p, TN10p, TN90p, TG10p, TG90p, R75p, R95p and R99p) could be returned as number of days (``out_unit`` = "days")
or as percentage of days (``out_unit`` = "%").


Custom indices
--------------
You can also calculate custom climate indices by setting all necessary parameters to ``user_index``.


``user_index``
~~~~~~~~~~~~~~~~
``user_index`` is a dictionary with possible keys:

+--------------------------+-------------------------------------------+--------------------------------------------------------------------------------------+
|Key                       |Type of value                              |Description                                                                           |
+==========================+===========================================+======================================================================================+
|"index_name"              |*str*                                      |Name of custom index.                                                                 |
+--------------------------+-------------------------------------------+--------------------------------------------------------------------------------------+
|"calc_operation"          |*str*                                      |Type of calculation. See below for more details.                                      |
+--------------------------+-------------------------------------------+--------------------------------------------------------------------------------------+
|"logical_operation"       |*str*                                      |"gt", "lt", "get", "let" or "e"                                                       |
+--------------------------+-------------------------------------------+--------------------------------------------------------------------------------------+
|"thresh"                  |*float* or *str*                           |In case of percentile-based index, must be string which starts with "p" (e.g. 'p90'). |
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
|"ref_time_range"          |[*datetime.datetime*, *datetime.datetime*] |Time range of reference (baseline) period for computing anomalies.                    |
+--------------------------+-------------------------------------------+--------------------------------------------------------------------------------------+

Additional information about ``user_index`` keys are given below.


- key ``calc_operation``

=======================================	===========================================================================
value									description
=======================================	===========================================================================
'max'									maximum
'min'									minimum
'sum'									sum
'mean'									mean
'nb_events'								number of relevant events fulfilling given criteria
'max_nb_consecutive_events'             maximum number of consecutive events fulfilling given criteria
'run_mean'								max or min of running mean
'run_sum'								max or min of running sum
'anomaly'								mean(future period) - mean(past period)
=======================================	===========================================================================


- The key ``date_event`` allows to keep date(s) of the event, it if is ``True``:

    - For simple statistics (min, max) in output netCDF file will be created "date_event" variable with numerical dates of the first occurrence of the event for each pixel.

    - For other operations in output netCDF file will be created "date_event_start" and "date_event_end" variables with numerical dates of the event for each pixel.

    .. note:: The "date_event", "date_event_start" and "date_event_end" netCDF variables have the same shape as index's one.

    .. warning:: "Date_event"/"date_event_start"/"date_event_end" has no value:

            - for certain pixels, if event is not found,
            - for all pixels of "in-base" years (years in base period) for temperature percentile-based indices - it is not possible to determine the correct date of the event because of averaging of index in "in-base" year.


- The key ``var_type`` is used to chose the method for computing  percentile thresholds. The methods are different for temperature and precipitation variables (more detailed :ref:`here <pctl_methods_label>`):

    - If 't' (temperature variable), percentile thresholds are computed for each calendar day, using  *the bootstrapping procedure*.

    - If 'p' (precipitation variable), percentile threshold are calculated for whole set of values corresponding to wet days (i.e. days with daily precipitation amount >= 1.0 mm) in base period.



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
|                               |(if multivariable index),      |                       |
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

.. warning:: The 'window_width' here is a parameter for calculation of statistics in running window. Do not confuse with 'window_width' of :func:`icclim.index`, which is used for computing of temperature percentiles and set to 5 as default.

.. note:: See examples for computing custom indices :ref:`here <custom_indices>`.


.. _table_index_sourceVar_label:

Correspondence table "index - source variable"
-----------------------------------------------

Using common names for the source variable, icclim is able to lookup the proper variable in the given input to compute an index.

+------------------------------------------------------------+---------------------------------------------+
|   index                                                    |   Source variable                           |
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
