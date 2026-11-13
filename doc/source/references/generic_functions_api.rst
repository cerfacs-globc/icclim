.. _generic_functions_api:

############################
 Generic indices/indicators
############################

icclim 6.0 introduced the concept of generic indices. This document
presents the auto-generated functions built from
:py:class:`icclim.generic_indices.registry.GenericIndicatorRegistry`. They are
accessible directly from the ``icclim`` namespace.

As an example, you can compute the number of days where a threshold is
reached with:

.. code:: python

   import glob
   import icclim

   hot_days_ds = icclim.count_occurrences(
       in_files="netcdf_files/data*.nc",
       var_name=["tmax"],
       threshold="> 27 degree_Celsius",
   )

For more details on thresholds and how to personalize them, see the
threshold documentation. We also prepared a few examples in
:ref:`generic_indices_recipes` so that you get an idea of the
capabilities of these generic indices.

For the indices that take two variables, the order of the names of ``var_name`` is
positional: the first name is the first term of the formula. See
:ref:`two_variable_indices_order` for the indices whose result depends on it, with an
example call for each.

The full API is now here :ref:`generic api`.
