.. _custom_indices_recipes:

Custom indices recipes
----------------------

.. note::
    Custom indices are deprecated. You should switch to :ref:`generic_indices_recipes` API.

>>> import icclim
>>> import datetime

Max of tas within the year
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from icclim.util import callback

    my_index_params = {"index_name": "my_index", "calc_operation": "max"}

    file_tas = "tas_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"
    out_f = "my_index.nc"

    icclim.index(
        user_index=my_index_params,
        in_files=file_tas,
        var_name="tas",
        slice_mode="year",
        out_file=out_f,
        callback=callback.defaultCallback2,
    )


Min of positive values within the year and the date of this minimum
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get minimum temperature which is above zero Celsius and find its date.

.. warning:: If input data are in Kelvin, then ``thresh`` must be in Kelvin too.

.. note:: An additional variable will be created in output netCDF file: "date_event" with the date of the *first* occurrence of min positive.


.. code-block:: python

    my_index_params = {
        "index_name": "my_index",
        "calc_operation": "min",
        "logical_operation": "gt",
        "thresh": 0 + 273.15,  ### input data in Kelvin ==> threshold in Kelvin!
        "date_event": True,
    }

    file_tasmin = "tasmin_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"
    out_f = "my_index.nc"

    icclim.index(
        user_index=my_index_params,
        in_files=file_tasmin,
        var_name="tasmin",
        slice_mode="year",
        out_file=out_f,
        callback=callback.defaultCallback2,
    )


Mean of a selected period
~~~~~~~~~~~~~~~~~~~~~~~~~

.. note:: ``slice_mode`` must be ``None`` to apply the operation to the whole period of selected time range.

.. code-block:: python

    my_index_params = {"index_name": "my_index", "calc_operation": "mean"}

    file_tas = "tas_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"
    out_f = "my_index.nc"

    tr = [datetime.datetime(1901, 1, 1), datetime.datetime(1920, 12, 31)]

    icclim.index(
        user_index=my_index_params,
        in_files=file_tas,
        var_name="tas",
        slice_mode=None,
        time_range=tr,
        out_file=out_f,
        callback=callback.defaultCallback2,
    )


Number of days when tas < 15 degrees Celsius of each Autumn
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note:: If 'calc_operation' is *'max_nb_consecutive_events'*, then max number of consecutive days for the same condition will be computed.

.. code-block:: python

    my_index_params = {
        "index_name": "my_index",
        "calc_operation": "nb_events",  ### 'calc_operation': 'max_nb_consecutive_events'
        "logical_operation": "lt",
        "thresh": 15 + 273.15,  ### input data in Kelvin ==> threshold in Kelvin!
    }

    file_tas = "tas_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"
    out_f = "my_index.nc"

    icclim.index(
        user_index=my_index_params,
        in_files=file_tas,
        var_name="tas",
        slice_mode="SON",
        out_unit="days",
        out_file=out_f,
        callback=callback.defaultCallback2,
    )


Percentage of days when tasmax > 80th pctl and at which date it happens
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note:: If 'calc_operation' is *'max_nb_consecutive_events'*, then max number of consecutive days for the same condition will be computed.

.. note:: 80th pctl: 80th percentile of tasmax in base period

.. note:: Two additional variables will be created in output netCDF file: "date_event_start" (the date of the first occurence of tasmax > 80th pctl) and "date_event_end" (the date of the last occurence of tasmax > 80th pctl).

.. code-block:: python

    my_index_params = {
        "index_name": "my_index",
        "calc_operation": "nb_events",  ### 'calc_operation': 'max_nb_consecutive_events'
        "logical_operation": "gt",
        "thresh": "p80",
        "var_type": "t",
        "date_event": True,
    }

    file_tasmax = "tasmax_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"
    out_f = "my_index.nc"
    bp = [datetime.datetime(1960, 1, 1), datetime.datetime(1969, 12, 31)]

    icclim.index(
        user_index=my_index_params,
        in_files=file_tasmax,
        var_name="tasmax",
        slice_mode="year",
        base_period_time_range=bp,
        out_unit="%",
        out_file=out_f,
        callback=callback.defaultCallback2,
    )


Number of days when daily precipitation amount > 85th pctl
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note:: If 'calc_operation' is *'max_nb_consecutive_events'*, then max number of consecutive days for the same condition will be computed.

.. note:: daily precipitation amount: daily precipitation amount on a wet day (RR >= 1.0 mm)

.. note:: 85th pctl: percentile of precipitation on wet days in base period

.. code-block:: python

    my_index_params = {
        "index_name": "my_index",
        "calc_operation": "nb_events",  ### 'calc_operation': 'max_nb_consecutive_events'
        "logical_operation": "gt",
        "thresh": "p85",
        "var_type": "p",
    }

    file_pr = "pr_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"
    out_f = "my_index.nc"

    icclim.index(
        user_index=my_index_params,
        in_files=file_pr,
        var_name="pr",
        slice_mode="year",
        base_period_time_range=bp,
        out_unit="days",
        out_file=out_f,
        callback=callback.defaultCallback2,
    )


Max number of consecutive days when tasmax >= 25 degrees Celsius + date of the events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note:: Two additional variables will be created in output netCDF file: "date_event_start" (the first date of the found sequence) and "date_event_end" (the last date of the found sequence).

.. warning:: If there are several sequences of the same length, the "date_event_start" and "date_event_end" will correspond to the *first* sequence.

.. code-block:: python

    my_index_params = {
        "index_name": "my_index",
        "calc_operation": "max_nb_consecutive_events",
        "logical_operation": "get",
        "thresh": 25 + 273.15,  ### input data in Kelvin ==> threshold in Kelvin!
        "date_event": True,
    }

    file_tasmax = "tasmax_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"
    out_f = "my_index.nc"

    icclim.index(
        user_index=my_index_params,
        in_files=file_tasmax,
        var_name="tasmax",
        slice_mode="year",
        out_file=out_f,
        callback=callback.defaultCallback2,
    )

Max of sum of precipitation in 10 consecutive days
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    my_index_params = {
        "index_name": "my_index",
        "calc_operation": "run_sum",
        "extreme_mode": "max",
        "window_width": 10,
    }

    file_pr = "pr_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"
    out_f = "my_index.nc"

    icclim.index(
        user_index=my_index_params,
        in_files=file_pr,
        var_name="pr",
        slice_mode=["season", [4, 5, 6, 7, 8]],
        out_file=out_f,
        callback=callback.defaultCallback2,
    )


Min of mean of tasmin in 7 consecutive days + date of the events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note:: Two additional variables will be created in output netCDF file: "date_event_start" (the date corrsponding to the beggining of the "window" satisfying the condition) and "date_event_end" (the date corrsponding to the end of the "window" satisfying the condition).

.. warning:: If several "windows" with the same result are found, the "date_event_start" and "date_event_end" will correspond to the *first* one.


.. code-block:: python

    my_index_params = {
        "index_name": "my_index",
        "calc_operation": "run_mean",
        "extreme_mode": "min",
        "window_width": 7,
        "date_event": True,
    }

    file_tasmin = "tasmin_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"
    out_f = "my_index.nc"

    icclim.index(
        user_index=my_index_params,
        in_files=file_tasmin,
        var_name="tasmin",
        slice_mode=["season", ([11, 12], [1, 2])],
        out_file=out_f,
        callback=callback.defaultCallback2,
    )

Anomaly of tasmax between 2 period of 30 years
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note:: Result could be returned as percentage value relative to mean value of reference period, if ``out_unit='%'``.

.. code-block:: python

    my_index_params = {"index_name": "my_index", "calc_operation": "anomaly"}

    file_tasmax = "tasmax_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"
    out_f = "my_index.nc"
    # studied period: future period
    tr = [datetime.datetime(1971, 1, 1), datetime.datetime(2000, 12, 31)]
    # reference period: past period
    tr_base = [datetime.datetime(1901, 1, 1), datetime.datetime(1930, 12, 31)]

    icclim.index(
        user_index=my_index_params,
        in_files=file_tasmax,
        var_name="tasmax",
        time_range=tr,
        base_period_time_range=tr_base,
        out_file=out_f,
        callback=callback.defaultCallback2,
    )


Number of days when tasmin >= 10 degrees Celsius and tasmax > 25 degrees Celsius
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note:: If 'calc_operation' is *'max_nb_consecutive_events'*, then max number of consecutive days for the same condition will be computed.

.. code-block:: python

    my_index_params = {
        "index_name": "my_index",
        "calc_operation": "nb_events",  ### 'calc_operation': 'max_nb_consecutive_events'
        "logical_operation": ["get", "gt"],
        "thresh": [
            10 + 273.15,
            25 + 273.15,
        ],  ### input data in Kelvin ==> threshold in Kelvin!
        "link_logical_operations": "and",
    }

    file_tasmin = "tasmin_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"
    file_tasmax = "tasmax_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"
    out_f = "my_index.nc"

    icclim.index(
        user_index=my_index_params,
        in_files=[file_tasmin, file_tasmax],
        var_name=["tasmin", "tasmax"],
        slice_mode="JJA",
        out_unit="days",
        out_file=out_f,
        callback=callback.defaultCallback2,
    )


Percentage of days when tasmin >= 10 degrees Celsius and tasmax > 90th pctl + date of the events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note:: If 'calc_operation' is *'max_nb_consecutive_events'*, then max number of consecutive days for the same condition will be computed.

.. note:: It is possible to use numeric and percentile threshold at the time.

.. code-block:: python

    my_index_params = {
        "index_name": "my_index",
        "calc_operation": "nb_events",  ### 'calc_operation': 'max_nb_consecutive_events'
        "logical_operation": ["get", "gt"],
        "thresh": [
            10 + 273.15,
            "p90",
        ],  ### input data in Kelvin ==> threshold in Kelvin!
        "var_type": "t",  ### or ['-','t']
        "link_logical_operations": "and",
        "date_event": True,
    }

    file_tasmin = "tasmin_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"
    file_tasmax = "tasmax_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"
    out_f = "my_index.nc"

    bp = [datetime.datetime(1960, 1, 1), datetime.datetime(1969, 12, 31)]
    icclim.index(
        user_index=my_index_params,
        in_files=[file_tasmin, file_tasmax],
        var_name=["tasmin", "tasmax"],
        slice_mode="JJA",
        base_period_time_range=bp,
        out_unit="%",
        out_file=out_f,
        callback=callback.defaultCallback2,
    )


.. _examples_CD_CW_WD_WW_label:

Number of days when tas < 25th pctl and precip. > 75th pctl
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note:: If 'calc_operation' is *'max_nb_consecutive_events'*, then max number of consecutive days for the same condition will be computed.

4 compound indices defined in https://knmi-ecad-assets-prd.s3.amazonaws.com/documents/atbd.pdf (see the section 5.3.3 "Compound indices") are
based on daily precipitation (RR) and mean temperature (TG) variables:

    - CD (cold/dry days): (TG < 25th pctl) and (RR < 25th pctl)
    - CW (cold/wet days): (TG < 25th pctl) and (RR > 75th pctl)
    - WD (warm/dry days): (TG > 75th pctl) and (RR < 25th pctl)
    - WW (warm/wet days): (TG > 75th pctl) and (RR > 75th pctl)

.. note:: RR is a daily precipitation on a *wet* day, and its percentile value is computed from set of wet days also.

.. note:: Percentiles thresholds computing uses differents methods as it was described :ref:`here <pctl_methods_label>`.


.. code-block:: python

    my_index_params = {
        "index_name": "my_index",
        "calc_operation": "nb_events",  ### 'calc_operation': 'max_nb_consecutive_events'
        "logical_operation": ["lt", "gt"],
        "thresh": ["p25", "p75"],
        "var_type": ["t", "p"],
        "link_logical_operations": "and",
    }

    file_pr = "pr_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"
    file_tas = "tas_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"
    out_f = "my_index.nc"

    bp = [datetime.datetime(1960, 1, 1), datetime.datetime(1969, 12, 31)]
    icclim.index(
        user_index=my_index_params,
        in_files=[file_tas, file_pr],
        var_name=["tas", "pr"],
        slice_mode="year",
        out_unit="days",
        base_period_time_range=bp,
        out_file=out_f,
        callback=callback.defaultCallback2,
    )

Number of days when tasmax > 90th pctl and tasmin >= 10 and precipitation < 30th pctl
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note:: If 'calc_operation' is *'max_nb_consecutive_events'*, then max number of consecutive days for the same condition will be computed.

.. code-block:: python

    my_index_params = {
        "index_name": "my_index",
        "calc_operation": "nb_events",  ### 'calc_operation': 'max_nb_consecutive_events'
        "logical_operation": ["gt", "get", "lt"],
        "thresh": ["p90", 10 + 273.15, "p30"],
        "var_type": ["t", "-", "p"],
        "link_logical_operations": "and",
    }
    file_pr = "pr_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"
    file_tasmax = "tasmax_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"
    file_tasmin = "tasmin_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"
    out_f = "my_index.nc"

    bp = [datetime.datetime(1960, 1, 1), datetime.datetime(1969, 12, 31)]
    icclim.index(
        user_index=my_index_params,
        in_files=[file_tasmax, file_tasmin, file_pr],
        var_name=["tasmax", "tasmin", "pr"],
        slice_mode="SON",
        out_unit="days",
        base_period_time_range=bp,
        out_file=out_f,
        callback=callback.defaultCallback2,
    )
