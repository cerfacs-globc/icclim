.. _generic_functions_api:

############################
 Generic indices/indicators
############################

icclim 6.0 introduced the concept of generic indices. This document
present the auto-generated functions that were built base on
:py:class:`icclim.generic_indices.registry.GenericIndicatorRegistry`. The are
accessible directly from `icclim` namespace.

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

For more details on threshold and how to personalize them, see
`Threshold` documentation. We also prepared a few examples on
:ref:`generic_indices_recipes` so that you get an idea of the
capabilities of these generic indices.

The full API is now here :ref:`generic api`.
