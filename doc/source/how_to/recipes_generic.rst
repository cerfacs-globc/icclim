.. _`generic_indices_recipes`:

Generic indices recipes
-----------------------

You will find below a few example of icclim v6 :ref:`generic_functions_api`.

.. code-block:: python

    import icclim
    from icclim import build_threshold

    # Change `data` to your own netcdf file path.
    data = "netcdf_files/gridded.1991-2010.nc"


Count occurrences
+++++++++++++++++

Occurrences of events where tas is between 20 and 30 degree Celsius and precipitation are above 3 mm/day.

.. code-block:: python

    # Equivalent to using `reasonable_temp = "<= 30 deg_C AND >= 20 deg_C"`
    reasonable_temp = build_threshold("<= 30 deg_C") & build_threshold(">= 20 deg_C")
    some_rain = icclim.build_threshold("> 3 mm/day")

    dataset = icclim.count_occurrences(
        in_files={
            "tmax": {"study": data, "thresholds": reasonable_temp},
            "precip": {"study": data, "thresholds": some_rain},
        }
    )
    # .compute must be called to ask dask to run the actual computation
    conputed_data = dataset.count_occurrences.compute()

.. code-block:: python

    tx99p_dataset = icclim.count_occurrences(
        in_files=data, var_name="tasmax", threshold=">= 99 doy_per"
    )
    # .compute must be called to ask dask to run the actual computation
    tx99p = dataset.count_occurrences.compute()

Sum
+++

Sum of precipitation that are above 4 mm/day.

.. code-block:: python

    rain_sum_above_4mm = icclim.sum(
        in_files=data, var_name="precip", threshold="> 4 mm/day"
    ).sum.compute()


Standard Deviation
++++++++++++++++++

Standard deviation of ``tas`` variable.

.. code-block:: python

    tas_std = icclim.std(in_files=data, var_name="tas").std.compute()


Average
+++++++

Average of the ``tas`` variable, per year by default.

.. code-block:: python

    tas_average = icclim.average(in_files=data, var_name="tas").average.compute()


Average of the ``tas`` values that are above the 87th period percentile (computed on the whole period here),
per year by default.

.. code-block:: python

    tas_average_above_percentile_of_period = icclim.average(
        in_files=data, var_name="tas", threshold="> 87 period_per"
    ).average.compute()


Maximum Consecutive Occurrences
+++++++++++++++++++++++++++++++

Almost equivalent to ECAD's index CDD (Consecutive Dry Days, days when pr is below 1 mm/day).

.. code-block:: python

    CDD = icclim.max_consecutive_occurrence(
        in_files=data, var_name="precip", threshold="< 1.3 mm/day"
    ).max_consecutive_occurrence.compute()


Sum of Spell Lengths
++++++++++++++++++++

Almost equivalent to ECAD's index WSDI (Warm Spell Duration Index,
maximum consecutive occurrence of tasmax > 90th doy percentile)

.. code-block:: python

    custom_wsdi = icclim.sum_of_spell_lengths(
        in_files=data, var_name="precip", threshold="> 90 doy_per AND > 28 degC"
    ).sum_of_spell_lengths.compute()

Excess
++++++

Excess of minimal daily temperature above the 22 daily percentile threshold computed overs the 1991-1995 reference
period, with a focus on the June to August periods.

.. code-block:: python

    jja_tmin_excess = (
        icclim.excess(
            climp_file,
            var_name=["tmin"],
            threshold=icclim.build_threshold(
                "22 doy_per", base_period_time_range=["1991-01-01", "1995-12-31"]
            ),
            slice_mode="jja",
        )
        .compute()
        .excess
    )


Deficit
+++++++

Deficit of minimal daily temperature below 17 degree Celsius.

.. code-block:: python

    result13 = icclim.index(
        climp_file,
        var_name=["tmin"],
        index_name="deficit",
        threshold=build_threshold("17 degC"),
    ).compute()

Fraction of Total
+++++++++++++++++

Fraction of precipitations above the 75th period percentile, where percentiles are computed only on values above 1 mm/day
This is equivalent to the ECAD's index R75pTOT.

.. code-block:: python

    result14 = (
        icclim.fraction_of_total(
            climp_file,
            var_name=["precip"],
            threshold=build_threshold(
                "> 75 period_per", threshold_min_value="1 mm/day"
            ),
        )
        .compute()
        .fraction_of_total
    )

Maximum
+++++++

Maximum of tas temperature per month.

.. code-block:: python

    max_of_tas = (
        icclim.maximum(
            climp_file,
            var_name=["tas"],
            slice_mode="month",
        )
        .compute()
        .maximum
    )

Minimum
+++++++

Minimum of tas temperature per month.

.. code-block:: python

    min_of_tas = (
        icclim.minimum(
            climp_file,
            var_name=["tas"],
            slice_mode="month",
        )
        .compute()
        .minimum
    )


Max of Rolling Sum
++++++++++++++++++

Maximum of rolling sum of precipitation that are above the period median, where the median is computed for the whole
period (default behavior when there is no `base_period_time_range`) only on values above 1mm/day.

.. code-block:: python

    max_of_rolling_sum = (
        icclim.index(
            climp_file,
            index_name="max_of_rolling_sum",
            var_name=["precip"],
            threshold=build_threshold(
                ">= 50 period_per", threshold_min_value="1 mmday"
            ),
        )
        .compute()
        .max_of_rolling_sum
    )

Min of Rolling Sum
++++++++++++++++++

Minimum of rolling sum of precipitation that are above the period median, where the median is computed for the whole
period (default behavior when there is no `base_period_time_range`) only on values above 1mm/day.

.. code-block:: python

    min_of_rolling_sum = (
        icclim.min_of_rolling_sum(
            climp_file,
            var_name=["precip"],
            threshold=build_threshold(
                ">= 50 period_per", threshold_min_value="1 mmday"
            ),
        )
        .compute()
        .min_of_rolling_sum
    )

Max of Rolling Average
++++++++++++++++++++++

Maximum of rolling average of precipitation that are above the period median, where the median is computed for the whole
period (default behavior when there is no `base_period_time_range`) only on values above 1mm/day.

.. code-block:: python

    max_of_rolling_average = (
        icclim.index(
            climp_file,
            index_name="max_of_rolling_average",
            var_name=["precip"],
            threshold=build_threshold(
                ">= 50 period_per", threshold_min_value="1 mmday"
            ),
        )
        .compute()
        .max_of_rolling_average
    )

Min of Rolling Average
++++++++++++++++++++++

Minimum of rolling average of precipitation that are above the period median, where the median is computed for the whole
period (default behavior when there is no `base_period_time_range`) only on values above 1mm/day.

.. code-block:: python

    min_of_rolling_average = (
        icclim.min_of_rolling_average(
            climp_file,
            var_name=["precip"],
            threshold=build_threshold(
                ">= 50 period_per", threshold_min_value="1 mmday"
            ),
        )
        .compute()
        .min_of_rolling_average
    )

Mean of difference
++++++++++++++++++

Mean of the difference between tasmax in tasmin.
It's a generification of ECAD's index DTR.

.. code-block:: python

    dtr = (
        icclim.index(
            climp_file,
            index_name="mean_of_difference",
            var_name=["tmax", "tmin"],
        )
        .compute()
        .mean_of_difference
    )

Difference of extremes
++++++++++++++++++++++

Difference of the maximum of tasmax and the minimum of tasmin.
It's a generification of ECAD's index ETR.

.. code-block:: python

    dtr = (
        icclim.index(
            climp_file,
            index_name="difference_of_extremes",
            var_name=["tmax", "tmin"],
        )
        .compute()
        .difference_of_extremes
    )

Difference of means
+++++++++++++++++++

Difference between averaged tas and the averaged tas values of the reference period.
Also known as the ``anomaly``.


.. code-block:: python

    anomaly = (
        icclim.difference_of_means(
            climp_file,
            var_name=["tas"],
            base_period_time_range=["1991-01-01", "1995-12-31"],
        )
        .compute()
        .difference_of_means
    )


Mean Of Absolute One Time Step Difference
+++++++++++++++++++++++++++++++++++++++++

Mean of absolute difference between tasmax and tasmin with a one time step lag (usually 1 day).
This is equivalent to the pseudo-code:

.. code-block:: python

    a = tasmax[T + 1] - tasmin[T + 1]
    b = tasmax[T] - tasmin[T]
    average(a - b)

It's a generification of ECAD's index vDTR.

.. code-block:: python

    result = (
        icclim.mean_of_absolute_one_time_step_difference(
            climp_file,
            var_name=["tmax", "tmin"],
        )
        .compute()
        .mean_of_absolute_one_time_step_difference
    )
