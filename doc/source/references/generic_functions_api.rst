.. _generic_functions_api:

Generic indices/indicators
==========================

icclim 6.0 introduced the concept of generic indices.
This document present the auto-generated functions that were built base on :ref:`GenericIndicatorRegistry`.
The are accessible directly from `icclim` namespace.

As an example, you can compute the number of days where a threshold is reached with:

.. code-block:: python

    import glob
    import icclim

    hot_days_ds = icclim.count_occurrences(
        in_files="netcdf_files/data*.nc",
        var_name=["tmax"],
        threshold="> 27 degree_Celsius",
    )

For more details on threshold and how to personalize them, see :ref:`threshold` documentation.
We also prepared a few examples on :ref:`generic_indices_recipes` so that you get an idea of the capabilities of
these generic indices.

Generated API
-------------

.. automodule:: icclim._generated_api
    :members:

    .. rubric:: Functions

    .. autosummary::
        .. Documentation below is auto-generated with the extract-icclim-funs.py script
        .. Generated API comment:Begin

        count_occurrences
        max_consecutive_occurrence
        sum_of_spell_lengths
        excess
        deficit
        fraction_of_total
        maximum
        minimum
        average
        sum
        standard_deviation
        max_of_rolling_sum
        min_of_rolling_sum
        max_of_rolling_average
        min_of_rolling_average
        mean_of_difference
        difference_of_extremes
        mean_of_absolute_one_time_step_difference
        difference_of_means

        .. Generated API comment:End
