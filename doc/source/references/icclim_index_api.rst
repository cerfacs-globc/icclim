icclim.index()
==============

icclim exposes a main entry point with :func:`icclim.index`.
It is used to compute both ECA&D indices and user defined indices.
There are quite a lot of options, but only a few of them are needed to compute simple indices.
Our :ref:`how_to` recipes are also a good start to have an idea on how to use `icclim.index`.

.. note::
    With version 5.2.0, icclim API now includes each individual index as a standalone function.
    Check :ref:`ecad_functions_api` to see how to call them.


Compute climat indices
----------------------

.. autofunction:: icclim.index(**kwargs)

.. note:: For the variable names see the :ref:`correspondence table "index - source variable" <table_index_sourceVar_label>`


Below are some additional information about input parameters.

``in_files`` and ``var_name``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``in_files`` parameter can be
    - A *string* path to a netCDF file or a zarr store
    - A *list of strings* to represent multiple netCDF files to combine
    - A *xarray.Dataset*
    - A *xarray.DataArray*
    - A python dictionary (new in 5.3)

+---------------------------------+----------------------------------------------------------+---------------------------------------------------------------------------------------------------------+
|                                 | single input file per variable                           |  several input files per variable                                                                       |
+=================================+==========================================================+=========================================================================================================+
| simple index                    |  ``var_name`` = 'tasmax'                                 |  ``var_name`` = 'tasmax'                                                                                |
| (based on a single variable)    +----------------------------------------------------------+---------------------------------------------------------------------------------------------------------+
|                                 |  ``in_files`` = 'tasmax_1990-2010.nc'                    |  ``in_files`` = ['tasmax_1990-2000.nc', 'tasmax_2000-2010.nc']                                          |
+---------------------------------+----------------------------------------------------------+---------------------------------------------------------------------------------------------------------+
| multivariable index             |  ``var_name`` = ['tas', 'pr']                            |  ``var_name`` = ['tas', 'pr']                                                                           |
| (based on several variables)    +----------------------------------------------------------+---------------------------------------------------------------------------------------------------------+
|                                 |  ``in_files`` = ['tas_1990-2010.nc', 'pr_1990-2010.nc']  |  ``in_files`` = ['tas_1990-2000.nc', 'tas_2000-2010.nc', 'pr_1990-2000.nc', 'pr_2000-2010.nc']          |
+---------------------------------+----------------------------------------------------------+---------------------------------------------------------------------------------------------------------+

New in 5.3
++++++++++

Starting with icclim 5.3, ``in_files`` can describe variable names, formerly set in ``var_name``, as dictionary format.
The dictionary keys are variable names and values are the usual in_files types (netCDF, zarr, Dataset, DataArray).

>>> in_files = {"tasmax" : "tasmax.nc", "pr": "precip.zarr"}

Moreover, this new dictionary syntax can be used to specify a different set of files for percentiles.

>>> in_files = {"tasmax" : "tasmax.nc", "thresholds": "tasmax-90p.zarr"}

The ``thresholds`` input should contain percentile thresholds that will be used will be used in place of computing them.
It allow to reuse percentiles computed and stored elsewhere easily.
For the record, you can generate percentiles with ``save_percentile`` parameter of icclim.index.

.. notes::
        Be aware that percentiles will **not** be bootstrapped. Thus, the result could be biased if the period on which percentiles
        were computed partially overlap the index studied period.
        See `<Computing percentile thresholds>`_ for more information on this topic.


.. _slice_mode:

``slice_mode``
~~~~~~~~~~~~~~
The ``slice_mode`` parameter defines a desired temporal aggregation. Thus, each index can be calculated at annual, winter half-year, summer half-year, winter, spring,
summer, autumn and monthly frequency:

+----------------------------------+-------------------------------------------+
|   Value (string)                 |    Description                            |
+==================================+===========================================+
|  ``year`` (default)              |    annual                                 |
+----------------------------------+-------------------------------------------+
|  ``month``                       |    monthly (all months)                   |
+----------------------------------+-------------------------------------------+
|  ``ONDJFM``                      |    winter half-year                       |
+----------------------------------+-------------------------------------------+
|  ``AMJJAS``                      |    summer half-year                       |
+----------------------------------+-------------------------------------------+
|  ``DJF``                         |    winter                                 |
+----------------------------------+-------------------------------------------+
|  ``MAM``                         |    spring                                 |
+----------------------------------+-------------------------------------------+
|  ``JJA``                         |    summer                                 |
+----------------------------------+-------------------------------------------+
|  ``SON``                         |    autumn                                 |
+----------------------------------+-------------------------------------------+
|  ``['month', [4,5,11]]``         |    monthly sampling filtered              |
+----------------------------------+-------------------------------------------+
|  ``['season', [4,5,6]]``         |    seasonal (1 value per season)          |
+----------------------------------+-------------------------------------------+
|                                  |    seasonal (1 value per season)          |
| ``['clipped_season', [4,5,6]]``  |    spells starting before season          |
|                                  |    start are not accounted                |
+----------------------------------+-------------------------------------------+
|  ``3W``                          |   A valid pandas frequency (3 weeks here) |
+----------------------------------+-------------------------------------------+

| The winter season (``DJF``) of 2000 is composed of December 2000, January 2001 and February 2001.
| Likewise, the winter half-year (``ONDJFM``) of 2000 includes October 2000, November 2000, December 2000, January 2001, February 2001 and March 2001.

Monthly time series filter
++++++++++++++++++++++++++
Monthly time series with months selected by user (the keyword can be either `month` or `months`):

>>> slice_mode = ['month', [4,5,11]] # index will be computed only for April, May and November

>>> slice_mode = ['month', [4]] # index will be computed only for April

User defined seasons
++++++++++++++++++++
You can either defined seasons aware of data outside their bounds (keyword `season`) or
seasons which clip all data outside their bounds (keyword `clipped_season`).
The later is most useful on indices computing spells, if you want to totally ignore spells that could
have started before your custom season.

>>> slice_mode = ['season', [4,5,6,7]] # March to July un-clipped
>>> slice_mode = ['clipped_season', [4,5,6,7]] # March to July clipped

>>> slice_mode = ['season', [11, 12, 1]] # November to January un-clipped
>>> slice_mode = ['clipped_season', ([11, 12, 1])] # November to January clipped

Additionally, you can define a season between two exact dates:

>>> slice_mode = ['season', ["07-19", "08-14"]]

>>> slice_mode = ["clipped_season", ["07-19", "08-14"]]

.. note::
    With 5.3.0 icclim now accepts pandas string frequency for slice_mode to resample the output data to a given frequency
    There are multiple combinations possible such as: "2AS-FEB" to resample data on two (2) years (A) starting (S) in February (FEB).
    For further information, refer to pandas `offset aliases <https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases>`_.


``threshold``
~~~~~~~~~~~~~
It is possible to set a user define threshold for the following indices:

* SU (default threshold: 25ºC)
* CSU (default threshold: 25ºC)
* TR (default threshold: 20ºC)
* CSDI (default 10th percentile)
* WSDI (default 90th percentile)
* TX90p (default 90th percentile)
* TG90p (default 90th percentile)
* TN90p (default 90th percentile)
* TX10p (default 10th percentile)
* TG10p (default 10th percentile)
* TN10p (default 10th percentile)


The threshold could be one value:

>>> threshold = 30

or a list of values:

>>> threshold = [20,25,30]

.. note:: thresholds should be a float, the unit is expected to be in degrees Celsius or a unit-less for percentiles.

``transfer_limit_Mbytes``
~~~~~~~~~~~~~~~~~~~~~~~~~
!Deprecated

``transfer_limit_Mbytes`` is now ignored and will be deleted in a futur version.
See :ref:`how to chunk data and parallelize computation <dask>` to configure dask chunking.

``callback``
~~~~~~~~~~~~
!Deprecated

Callback can used to output a estimated progress of the calculus.
However, when using dask, the calculus are done lazily at the very end of icclim's process.
Thus the values transmitted to ``callback`` are irrelevant with dask.


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
~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~
Computing of a percentile value could use ``linear``, also known as type 7 in other software or the interpolation proposed
by `Hyndman and Fan (1996) <https://www.amherst.edu/media/view/129116/original/Sample+Quantiles.pdf>`_, named
in *icclim* as ``hyndman_fan`` interpolation, also known as type 8.


``out_unit``
~~~~~~~~~~~~~~~
Percentile-based indices (TX10p, TX90p, TN10p, TN90p, TG10p, TG90p, R75p, R95p and R99p) could be returned as number of days (default)
or as percentage of days (``out_unit`` = "%").

Custom indices
--------------

Custom indices are now described in their own chapter: `here <custom_indices>`_


.. _table_index_sourceVar_label:

Correspondence table "index - source variable"
----------------------------------------------

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
