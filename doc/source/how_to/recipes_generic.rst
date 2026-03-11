.. _generic_indices_recipes:

#########################
 Generic indices recipes
#########################

The generic index API lets you compute any climate indicator by combining a
**reducer function** (e.g. ``count_occurrences``, ``sum``, ``average``) with a
**threshold** (e.g. ``"> 25 degC"``).

.. seealso::

   :ref:`thresholds_reference` — full table of operators and threshold types.

***********************
 Quick-start reference
***********************

Threshold mini-cheat-sheet
==========================

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Threshold string
     - Meaning
   * - ``"> 25 degC"``
     - Fixed scalar: strictly above 25 °C
   * - ``">= 1 mm/day"``
     - Fixed scalar: at least 1 mm/day
   * - ``"> 90 doy_per"``
     - Day-of-year percentile (temperature indices): 90th per-calendar-day percentile
   * - ``"> 75 period_per"``
     - Period percentile (precip indices): 75th percentile of the whole period
   * - ``">= 18 degC AND <= 30 degC"``
     - Bounded (AND): value must satisfy both conditions simultaneously
   * - ``"< 0 degC OR > 35 degC"``
     - Bounded (OR): value must satisfy at least one condition

See :ref:`thresholds_reference` for ``threshold_min_value``, per-grid-cell thresholds,
and all available operators.

Imports and in-memory sample data
==================================

All examples below that use **in-memory data** share the same setup:

.. code:: python

   import numpy as np
   import pandas as pd
   import xarray as xr
   import icclim
   from icclim import build_threshold

   # 5 years of daily data, single grid cell
   time = pd.date_range("2000-01-01", periods=365 * 5, freq="D")

   # Temperature: 30 °C everywhere (300+ K)
   tas = xr.DataArray(
       np.full(len(time), 303.15),   # 30 °C in K
       coords={"time": time},
       dims=["time"],
       attrs={"units": "K"},
   )

   # Precipitation: alternating 5 mm/day and 0.5 mm/day
   pr_vals = np.where(np.arange(len(time)) % 2 == 0, 5e-5, 5e-6)
   pr = xr.DataArray(
       pr_vals,
       coords={"time": time},
       dims=["time"],
       attrs={"units": "kg m-2 s-1"},
   )

For file-based examples, set:

.. code:: python

   data = "netcdf_files/gridded.1991-2010.nc"

*******************
 Count occurrences
*******************

Count days per year when temperature exceeds a fixed threshold:

.. code:: python

   # In-memory example: count days when tas > 25 °C
   result = icclim.count_occurrences(
       in_files=tas,
       var_name="tas",
       threshold="> 25 degC",
   ).compute()
   print(result.count_occurrences)

Count days when both temperature AND precipitation exceed their respective thresholds
(multivariable index):

.. code:: python

   okay_temp = build_threshold(">= 20 degC") & build_threshold("<= 30 degC")
   some_rain = build_threshold("> 3 mm/day")

   result = icclim.count_occurrences(
       in_files={
           "tas": {"study": tas, "thresholds": okay_temp},
           "pr":  {"study": pr,  "thresholds": some_rain},
       }
   ).compute()

Using a day-of-year percentile threshold (equivalent to TX99p):

.. code:: python

   tx99p = icclim.count_occurrences(
       in_files=tas, var_name="tas", threshold=">= 99 doy_per"
   ).count_occurrences.compute()

Using ``out_unit="%"`` to get the result as a fraction of days:

.. code:: python

   result_pct = icclim.count_occurrences(
       in_files=tas, var_name="tas",
       threshold="> 25 degC", out_unit="%",
   ).count_occurrences.compute()

File-based example:

.. code:: python

   result_file = icclim.count_occurrences(
       in_files=data, var_name="tasmax", threshold=">= 99 doy_per"
   ).count_occurrences.compute()

*****
 Sum
*****

Sum of precipitation values above 4 mm/day per year:

.. code:: python

   # In-memory example
   rain_sum = icclim.sum(
       in_files=pr, var_name="pr", threshold="> 4 mm/day"
   ).sum.compute()

File-based:

.. code:: python

   rain_sum_file = icclim.sum(
       in_files=data, var_name="precip", threshold="> 4 mm/day"
   ).sum.compute()

********************
 Standard Deviation
********************

Interannual variability of daily temperature:

.. code:: python

   # In-memory example
   tas_std = icclim.std(in_files=tas, var_name="tas").std.compute()

File-based:

.. code:: python

   tas_std_file = icclim.std(in_files=data, var_name="tas").std.compute()

*********
 Average
*********

Annual mean temperature:

.. code:: python

   # In-memory example
   tas_avg = icclim.average(in_files=tas, var_name="tas").average.compute()

Mean of values above the 87th period percentile:

.. code:: python

   tas_hot_avg = icclim.average(
       in_files=tas, var_name="tas", threshold="> 87 period_per"
   ).average.compute()

Monthly means (``slice_mode="month"``):

.. code:: python

   tas_monthly = icclim.average(
       in_files=tas, var_name="tas", slice_mode="month"
   ).average.compute()

*********************************
 Maximum Consecutive Occurrences
*********************************

Longest dry spell per year (consecutive days when pr < 1 mm/day), equivalent to
ECA&D's CDD:

.. code:: python

   # In-memory example
   dry_spell = icclim.max_consecutive_occurrence(
       in_files=pr, var_name="pr", threshold="< 1 mm/day"
   ).max_consecutive_occurrence.compute()

Use ``run_index="last"`` to stamp the spell at its *end* date (Climdex convention):

.. code:: python

   dry_spell_last = icclim.max_consecutive_occurrence(
       in_files=pr, var_name="pr",
       threshold="< 1 mm/day", run_index="last"
   ).max_consecutive_occurrence.compute()

File-based:

.. code:: python

   CDD = icclim.max_consecutive_occurrence(
       in_files=data, var_name="precip", threshold="< 1.3 mm/day"
   ).max_consecutive_occurrence.compute()

**********************
 Sum of Spell Lengths
**********************

Total duration of all heat spells per year where tasmax > 28 °C for at least
6 consecutive days (equivalent parameter to ECA&D's WSDI):

.. code:: python

   # In-memory example: spell ≥ 3 consecutive days above 25 °C
   spell_total = icclim.sum_of_spell_lengths(
       in_files=tas,
       var_name="tas",
       threshold="> 25 degC",
       min_spell_length=3,
   ).sum_of_spell_lengths.compute()

Combine a percentile threshold via a bounded string:

.. code:: python

   custom_wsdi = icclim.sum_of_spell_lengths(
       in_files=data, var_name="tasmax", threshold="> 90 doy_per"
   ).sum_of_spell_lengths.compute()

``run_index`` is also supported here (``"first"`` or ``"last"``).

********
 Excess
********

Cumulative degree-days above a threshold (sum of ``value - threshold`` for each
exceedance day). Equivalent to ECA&D's GD4 when threshold is 4 °C.

.. code:: python

   # In-memory example: degree-days above 25 °C
   gd25 = icclim.excess(
       in_files=tas, var_name="tas",
       threshold="25 degC",
   ).excess.compute()

With a day-of-year percentile reference period:

.. code:: python

   jja_excess = icclim.excess(
       in_files=data,
       var_name="tmin",
       threshold=build_threshold(
           "22 doy_per",
           base_period_time_range=["1991-01-01", "1995-12-31"],
       ),
       slice_mode="jja",
   ).excess.compute()

*********
 Deficit
*********

Cumulative degree-days below a threshold (sum of ``threshold - value``).
Equivalent to ECA&D's HD17 when threshold is 17 °C.

.. code:: python

   # In-memory example: heating degree-days relative to 17 °C
   hd17 = icclim.deficit(
       in_files=tas, var_name="tas",
       threshold="17 degC",
   ).deficit.compute()

File-based with the ``icclim.index`` entry point:

.. code:: python

   result = icclim.index(
       in_files=data,
       var_name=["tmin"],
       index_name="deficit",
       threshold=build_threshold("17 degC"),
   ).compute()

*******************
 Fraction of Total
*******************

Fraction of total precipitation contributed by days above the 75th period percentile
(wet days only), equivalent to ECA&D's R75pTOT:

.. code:: python

   # In-memory example
   r75ptot = icclim.fraction_of_total(
       in_files=pr,
       var_name="pr",
       threshold=build_threshold("> 75 period_per", threshold_min_value="1 mm/day"),
   ).fraction_of_total.compute()

   # Return as mm instead of % using out_unit
   r75ptot_mm = icclim.fraction_of_total(
       in_files=pr,
       var_name="pr",
       threshold=build_threshold("> 75 period_per", threshold_min_value="1 mm/day"),
       out_unit="mm",
   ).fraction_of_total.compute()

File-based:

.. code:: python

   result_frac = icclim.fraction_of_total(
       in_files=data,
       var_name=["precip"],
       threshold=build_threshold("> 75 period_per", threshold_min_value="1 mm/day"),
   ).fraction_of_total.compute()

*********
 Maximum
*********

Annual maximum temperature:

.. code:: python

   # In-memory example
   txx = icclim.maximum(in_files=tas, var_name="tas").maximum.compute()

Monthly maximum with event date:

.. code:: python

   txx_monthly = icclim.maximum(
       in_files=tas, var_name="tas",
       slice_mode="month", date_event=True,
   ).compute()

*********
 Minimum
*********

Annual minimum temperature:

.. code:: python

   # In-memory example
   tnn = icclim.minimum(in_files=tas, var_name="tas").minimum.compute()

Monthly minimum:

.. code:: python

   tnn_monthly = icclim.minimum(
       in_files=data, var_name="tas", slice_mode="month"
   ).minimum.compute()

********************
 Max of Rolling Sum
********************

Maximum 5-day accumulated precipitation per year (equivalent to ECA&D's RX5day):

.. code:: python

   # In-memory example (5-day rolling window)
   rx5day = icclim.max_of_rolling_sum(
       in_files=pr,
       var_name="pr",
       rolling_window_width=5,
   ).max_of_rolling_sum.compute()

With a wet-day percentile filter:

.. code:: python

   max_rolling = icclim.max_of_rolling_sum(
       in_files=data,
       var_name="precip",
       threshold=build_threshold(">= 50 period_per", threshold_min_value="1 mm/day"),
   ).max_of_rolling_sum.compute()

********************
 Min of Rolling Sum
********************

Minimum 5-day accumulated precipitation per year:

.. code:: python

   # In-memory example
   min_rolling = icclim.min_of_rolling_sum(
       in_files=pr, var_name="pr", rolling_window_width=5,
   ).min_of_rolling_sum.compute()

************************
 Max of Rolling Average
************************

Maximum 5-day rolling mean temperature:

.. code:: python

   # In-memory example
   max_rolling_avg = icclim.max_of_rolling_average(
       in_files=tas, var_name="tas", rolling_window_width=5,
   ).max_of_rolling_average.compute()

************************
 Min of Rolling Average
************************

Minimum 5-day rolling mean temperature:

.. code:: python

   # In-memory example
   min_rolling_avg = icclim.min_of_rolling_average(
       in_files=tas, var_name="tas", rolling_window_width=5,
   ).min_of_rolling_average.compute()

********************
 Mean of difference
********************

Mean daily difference between two variables (e.g. tasmax − tasmin), equivalent to
ECA&D's DTR:

.. code:: python

   # In-memory example: mean of (tasmax - tasmin)
   tasmin = tas - 10   # artificial 10 °C spread
   tasmin.attrs["units"] = "K"

   dtr = icclim.mean_of_difference(
       in_files=xr.Dataset({"tasmax": tas, "tasmin": tasmin}),
       var_name=["tasmax", "tasmin"],
   ).mean_of_difference.compute()

File-based via ``icclim.index``:

.. code:: python

   dtr_file = icclim.index(
       in_files=data,
       index_name="mean_of_difference",
       var_name=["tmax", "tmin"],
   ).mean_of_difference.compute()

************************
 Difference of extremes
************************

Annual maximum of tasmax minus annual minimum of tasmin, equivalent to ECA&D's ETR:

.. code:: python

   # In-memory example
   tasmin = tas - 10
   tasmin.attrs["units"] = "K"

   etr = icclim.difference_of_extremes(
       in_files=xr.Dataset({"tasmax": tas, "tasmin": tasmin}),
       var_name=["tasmax", "tasmin"],
   ).difference_of_extremes.compute()

File-based:

.. code:: python

   etr_file = icclim.index(
       in_files=data,
       index_name="difference_of_extremes",
       var_name=["tmax", "tmin"],
   ).difference_of_extremes.compute()

*********************
 Difference of means
*********************

Anomaly: mean of the study period minus mean of the reference period:

.. code:: python

   # In-memory example: anomaly relative to first year
   anomaly = icclim.difference_of_means(
       in_files=tas,
       var_name="tas",
       base_period_time_range=["2000-01-01", "2000-12-31"],
   ).difference_of_means.compute()

File-based:

.. code:: python

   anomaly_file = icclim.difference_of_means(
       in_files=data,
       var_name=["tas"],
       base_period_time_range=["1991-01-01", "1995-12-31"],
   ).difference_of_means.compute()

*******************************************
 Mean Of Absolute One Time Step Difference
*******************************************

Mean day-to-day variability in the diurnal temperature range, equivalent to ECA&D's
vDTR. The formula is: ``mean(|(tasmax[t+1] - tasmin[t+1]) - (tasmax[t] - tasmin[t])|)``

.. code:: python

   # In-memory example
   tasmin = tas - 10 + xr.DataArray(
       np.random.default_rng(42).normal(0, 1, len(time)),
       coords={"time": time}, dims=["time"], attrs={"units": "K"},
   )
   vdtr = icclim.mean_of_absolute_one_time_step_difference(
       in_files=xr.Dataset({"tasmax": tas, "tasmin": tasmin}),
       var_name=["tasmax", "tasmin"],
   ).mean_of_absolute_one_time_step_difference.compute()

File-based:

.. code:: python

   vdtr_file = icclim.mean_of_absolute_one_time_step_difference(
       in_files=data,
       var_name=["tmax", "tmin"],
   ).mean_of_absolute_one_time_step_difference.compute()
