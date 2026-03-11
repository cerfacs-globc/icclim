.. _thresholds_reference:

###############################
 Thresholds and Operators Reference
###############################

This page documents all available **operators** and **threshold types** that can be used
with :func:`icclim.build_threshold` and the generic index API.

.. seealso::

   :ref:`generic_indices_recipes` for examples showing thresholds in action.

*************
 Operators
*************

An **operator** defines the comparison between a variable and a threshold value.
It is expressed as a string symbol in the threshold query (e.g. ``"> 25 degC"``).

.. list-table:: Available operators
   :header-rows: 1
   :widths: 15 20 20 45

   * - Symbol(s)
     - Short name
     - Long name
     - Usage notes
   * - ``>``, ``gt``
     - ``gt``
     - greater than
     - Standard strict inequality.
   * - ``<``, ``lt``
     - ``lt``
     - lower than
     - Standard strict inequality.
   * - ``>=``, ``=>``, ``ge``, ``get``
     - ``get``
     - greater or equal to
     - Non-strict upper bound.
   * - ``<=``, ``=<``, ``le``, ``let``
     - ``let``
     - lower or equal to
     - Non-strict lower bound.
   * - ``=``, ``==``, ``eq``, ``equal``
     - ``e``
     - equal to
     - Exact equality.
   * - *(none)*
     - ``reach``
     - reaching
     - Special operator used implicitly by ``excess`` and ``deficit`` indices.
       Cannot be specified directly in a query string.

Examples
========

.. code:: python

   from icclim import build_threshold

   t1 = build_threshold("> 25 degC")         # greater than 25 °C
   t2 = build_threshold("<= 0 degC")         # at or below freezing
   t3 = build_threshold(">= 1 mm/day")       # wet-day filter
   t4 = build_threshold("== 0 degC")         # exactly 0 °C

*********************
 Threshold types
*********************

``build_threshold`` returns one of three concrete threshold types depending on the
arguments provided.

BasicThreshold
==============

A fixed scalar (or list of scalars) threshold.

.. code:: python

   from icclim import build_threshold

   # Single scalar
   t = build_threshold(">= 30 degC")

   # Multiple scalars — the index is computed once per value,
   # creating a "threshold" dimension in the output.
   t_multi = build_threshold(value=[25, 30, 35], operator=">=", unit="degC")

PercentileThreshold
===================

A percentile computed from the data itself during the run.
Two flavours exist, selected by the unit string:

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - Unit keyword
     - Type
     - Description
   * - ``doy_per``
     - Day-of-year percentile
     - Percentile computed separately for each calendar day, using a rolling window
       (``doy_window_width``). Used for temperature-based ECAD indices (e.g. TX90p, WSDI).
   * - ``period_per``
     - Period percentile
     - Percentile computed over the full reference period (or study period when no
       ``base_period_time_range`` is given). Used for precipitation-based ECAD indices
       (e.g. R75p, R95pTOT).

.. code:: python

   from icclim import build_threshold

   # 90th day-of-year percentile (like TX90p)
   doy_t = build_threshold("> 90 doy_per")

   # 75th period percentile, ignoring dry days (like R75pTOT)
   per_t = build_threshold("> 75 period_per", threshold_min_value="1 mm/day")

   # Percentile computed on a specific reference period
   ref_t = build_threshold(
       "> 90 doy_per",
       base_period_time_range=["1991-01-01", "2020-12-31"],
   )

.. note::

   When ``base_period_time_range`` overlaps with the study period (in-base years),
   icclim applies the **bootstrapping** procedure described in ETCCDI guidelines to
   avoid artificially inflated counts.

BoundedThreshold
================

Two thresholds combined with a logical link (``AND`` or ``OR``).
Useful to express a range condition.

.. code:: python

   from icclim import build_threshold

   # Temperature between 18 °C and 30 °C
   bounded = build_threshold(">= 18 degC AND <= 30 degC")

   # Equivalent using the & operator
   low  = build_threshold(">= 18 degC")
   high = build_threshold("<= 30 degC")
   bounded2 = low & high

   # Using explicit arguments
   bounded3 = build_threshold(
       thresholds=[low, high],
       logical_link="AND",
   )

   # OR condition: frost OR heat stress
   frost_or_heat = build_threshold("< 0 degC OR > 35 degC")

Per-grid-cell threshold (from a file or DataArray)
===================================================

A threshold dataset (e.g. pre-computed percentiles, climate normals) can be supplied
directly as a path to a NetCDF/Zarr file, or as an ``xarray.DataArray``.

.. code:: python

   import xarray as xr
   from icclim import build_threshold

   # From a pre-computed threshold NetCDF file
   t_file = build_threshold(operator=">=", value="path/to/tasmax_90th.nc", unit="K")

   # With a +5 K offset (e.g. 5 degrees warmer than the normal)
   t_offset = build_threshold(
       operator=">=", value="path/to/tasmax_normal.nc", unit="K", offset=5
   )

   # From an xarray DataArray of pre-computed percentile doy values
   import xclim.core.calendar
   tasmax_ds = xr.open_dataset("path/to/tasmax.nc")
   doys = xclim.core.calendar.percentile_doy(tasmax_ds.tasmax)
   t_doy = build_threshold(operator=">=", value=doys)

*****************************
 Combining thresholds (AND/OR)
*****************************

Multiple thresholds on **different variables** can be combined via the
``in_files`` dictionary syntax when calling a generic index:

.. code:: python

   import icclim

   # Count days when temperature is comfortable AND precipitation is light
   good_weather = icclim.count_occurrences(
       in_files={
           "tasmax": {
               "study": "path/to/tasmax.nc",
               "thresholds": icclim.build_threshold(">= 15 degC AND <= 28 degC"),
           },
           "pr": {
               "study": "path/to/pr.nc",
               "thresholds": icclim.build_threshold("< 5 mm/day"),
           },
       },
   )

.. note::

   The logical link **between** variables (across the ``in_files`` dictionary keys) is
   always ``AND``. To express an ``OR`` between two variables you must use
   ``BoundedThreshold`` on each variable with ``OR``, or use the ``icclim.index``
   generic API with a custom threshold list.

*****************************
 ``threshold_min_value``
*****************************

For precipitation percentile thresholds, wet-day filtering is standard practice:
percentiles are computed only from days with ``pr >= 1 mm/day``.
Use ``threshold_min_value`` to apply such a filter:

.. code:: python

   from icclim import build_threshold

   # 95th percentile of wet days only (equivalent to R95p)
   t = build_threshold("> 95 period_per", threshold_min_value="1 mm/day")

*****************************
 Quick-reference cheat sheet
*****************************

.. code:: python

   from icclim import build_threshold

   # Plain scalar
   build_threshold("> 25 degC")

   # Day-of-year percentile
   build_threshold("> 90 doy_per")

   # Period percentile on wet days
   build_threshold("> 75 period_per", threshold_min_value="1 mm/day")

   # Range (bounded AND)
   build_threshold(">= 18 degC AND <= 30 degC")

   # Range (bounded OR)
   build_threshold("< 0 degC OR > 40 degC")

   # Multiple scalar values → threshold dimension in output
   build_threshold(value=[0, 10, 20, 30], operator=">=", unit="degC")

   # External file / DataArray threshold
   build_threshold(operator=">=", value="t90_climatology.nc", unit="K")

   # With offset relative to a climatology
   build_threshold(operator=">", value="t_normal.nc", unit="K", offset=2)
