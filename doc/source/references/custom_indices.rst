.. _`custom_indices`:

Create your own index with ``user_index``
-----------------------------------------
You can calculate custom climate indices by using the ``user_index`` parameters.
It is a configuration dictionary to describe how the index should be computed.
In icclim documentation we usually call them custom indices or user indices.

.. code-block:: python

    user_index_dict = dict(
        index_name="a_custom_csdi",
        calc_operation="max_nb_consecutive_events",
        logical_operation="<",
        thresh="5p",
        window_width=5,
    )
    refer_period = [datetime.datetime(1991, 1, 1), datetime.datetime(1999, 12, 31)]
    study_period = [datetime.datetime(1991, 1, 1), datetime.datetime(2010, 12, 31)]
    result = icclim.custom_index(
        in_files="netcdf_files/tasmin.nc",
        user_index=user_index_dict,
        var_name="tmin",
        slice_mode="YS",
        base_period_time_range=refer_period,
        time_range=study_period,
        out_file="custom_csdi_5.nc",
    )



``user_index`` dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~
``user_index`` is a dictionary with possible keys:

+------------------------+-------------------------------------------+--------------------------------------------------------------------------------------+
|Key                     |Type of value                              |Description                                                                           |
+========================+===========================================+======================================================================================+
|index_name              |*str*                                      |Name of custom index.                                                                 |
+------------------------+-------------------------------------------+--------------------------------------------------------------------------------------+
|calc_operation          |*str*                                      |Type of calculation. See below for more details.                                      |
+------------------------+-------------------------------------------+--------------------------------------------------------------------------------------+
|logical_operation       |*str*                                      |gt, lt, get, let or e                                                                 |
+------------------------+-------------------------------------------+--------------------------------------------------------------------------------------+
|thresh                  |*float* or *str*                           |In case of percentile-based index, must be string which starts with "p" (e.g. "p90"). |
+------------------------+-------------------------------------------+--------------------------------------------------------------------------------------+
|link_logical_operations |*str*                                      |and or or                                                                             |
+------------------------+-------------------------------------------+--------------------------------------------------------------------------------------+
|extreme_mode            |*str*                                      |min or max for computing min or max of running mean/sum.                              |
+------------------------+-------------------------------------------+--------------------------------------------------------------------------------------+
|window_width            |*int*                                      |Used for computing running mean/sum.                                                  |
+------------------------+-------------------------------------------+--------------------------------------------------------------------------------------+
|coef                    |*float*                                    |Constant for multiplying input data array.                                            |
+------------------------+-------------------------------------------+--------------------------------------------------------------------------------------+
|date_event              |*bool*                                     |To keep or not the date of event. See below for more details.                         |
+------------------------+-------------------------------------------+--------------------------------------------------------------------------------------+
|var_type                |*str*                                      |"t" or "p". See below for more details.                                               |
+------------------------+-------------------------------------------+--------------------------------------------------------------------------------------+
|ref_time_range          |[*datetime.datetime*, *datetime.datetime*] |Time range of reference (baseline) period for computing anomalies.                    |
+------------------------+-------------------------------------------+--------------------------------------------------------------------------------------+

Additional information about ``user_index`` keys are given below.


calc_operation key
++++++++++++++++++

=======================================	===========================================================================
Value									   Description
=======================================	===========================================================================
``max``								    	maximum
``min``								    	minimum
``sum``								    	sum
``mean``									mean
``nb_events``								number of relevant events fulfilling given criteria
``max_nb_consecutive_events``               maximum number of consecutive events fulfilling given criteria
``run_mean``								max or min of running mean
``run_sum``								    max or min of running sum
``anomaly``								    mean(future period) - mean(past period)
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


cal_operation parameterization
++++++++++++++++++++++++++++++

Correspondence table between ``cal_operation`` and required/optional parameters:

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

.. note:: See examples for computing custom indices :ref:`here <custom_indices_recipes>`.
