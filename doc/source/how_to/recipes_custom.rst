.. _custom_indices_recipes:

########################################
 Migrate Deprecated user_index Recipes
########################################

.. warning::

   The ``user_index`` API (also known as "User indices") is **deprecated**:
   deprecated since 7.1.8, it emits a ``FutureWarning`` since 7.5.0, and its
   support ends in icclim 7.6.0.
   Please switch to the :ref:`generic_indices_recipes` API instead.

This page is a migration aid for older code.
For new tutorials, examples, and user-facing guidance, use
:ref:`generic_indices_recipes` instead.

Each legacy recipe below is written with the current API: ``icclim.index`` with an
``index_name``, or the generic functions such as ``icclim.maximum`` or
``icclim.count_occurrences``. The legacy ``user_index`` dictionary of each recipe is
described in the correspondence table, not repeated.

Status of ``user_index``
========================

The ``user_index`` parameter of ``icclim.index`` (and the ``icclim.custom_index``
function, which is the generated form of it) is documented as deprecated since icclim
7.1.8. Since 7.5.0 each call emits one ``FutureWarning`` (reported at the line of your
code), and the support ends in icclim 7.6.0. Until then it still works, but it receives
no new feature.
Of the legacy recipes, the ones that use a percentile threshold (``"thresh": "p80"``) or
``slice_mode=None`` fail with ``user_index``, the ``anomaly`` operation needs
``sampling_method="groupby_ref_and_resample_study"``, and the ``icclim.util.callback``
module they imported does not exist any more.

Correspondence table
====================

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Legacy ``user_index`` key
     - Current API
   * - ``calc_operation: "max"``, ``"min"``, ``"mean"``, ``"sum"``
     - ``icclim.maximum``, ``icclim.minimum``, ``icclim.average``, ``icclim.sum``
       (the result is a ``Dataset``: read it with ``["sum"]``)
   * - ``calc_operation: "nb_events"``
     - ``icclim.count_occurrences``
   * - ``calc_operation: "max_nb_consecutive_events"``
     - ``icclim.max_consecutive_occurrence``
   * - ``calc_operation: "run_mean"`` or ``"run_sum"`` with ``extreme_mode``
     - ``icclim.max_of_rolling_average``, ``icclim.min_of_rolling_average``,
       ``icclim.max_of_rolling_sum``, ``icclim.min_of_rolling_sum``
       with ``rolling_window_width``
   * - ``calc_operation: "anomaly"``
     - ``icclim.index(index_name="difference_of_means", ...)`` with
       ``base_period_time_range`` and
       ``sampling_method="groupby_ref_and_resample_study"``
   * - ``logical_operation``: ``"lt"``, ``"gt"``, ``"let"``, ``"get"``, ``"e"``
     - the operator of the ``threshold`` string: ``"<"``, ``">"``, ``"<="``, ``">="``,
       ``"=="``
   * - ``thresh`` as a number (degrees Celsius for a temperature)
     - ``threshold="> 25 degC"`` (the units are converted: the data can be in Kelvin)
   * - ``thresh: "p80"`` with ``var_type: "t"``
     - ``threshold="> 80 doy_per"`` and ``base_period_time_range``
   * - ``thresh: "p85"`` with ``var_type: "p"``
     - ``threshold=build_threshold("> 85 period_per", threshold_min_value="1 mm/day")``
       and ``base_period_time_range``
   * - ``link_logical_operations: "and"``
     - one threshold per variable in ``in_files``: the thresholds are combined with AND
   * - ``window_width``
     - ``rolling_window_width``
   * - ``date_event: True``
     - ``date_event=True``
   * - ``slice_mode=None``
     - a pandas frequency as long as the period, for example ``slice_mode="20YS"``
   * - ``callback=callback.defaultCallback2``
     - nothing to pass, see the note below

.. note::

   **Progress callback.** The ``icclim.util.callback.defaultCallback2`` function of old
   icclim versions only logged the percentage of progress ("Processing: 12.50%"). The
   current ``icclim.index`` does it by default (the ``callback`` parameter has this
   function as a default, and ``logs_verbosity`` controls the other messages), so the
   recipes below do not pass a callback. A function of your own can be given to
   ``icclim.index`` with ``callback=my_function`` (it receives the percentage). The
   generic functions such as ``icclim.maximum`` have no ``callback`` parameter.

.. note::

   **Percentile thresholds** need a base period: pass ``base_period_time_range`` to
   ``icclim.index``, which gives it to each percentile threshold. The percentiles of a
   temperature (``doy_per``) are computed for each calendar day, with the bootstrapping
   procedure for the years of the base period, and the ones of a precipitation
   (``period_per`` with ``threshold_min_value="1 mm/day"``) on the wet days of the base
   period (see :ref:`here <pctl_methods_label>`).

.. note::

   **Dates of the events.** With ``date_event=True``, the result has the coordinates
   ``event_date`` (``minimum``, ``maximum``), or ``event_date_start`` and
   ``event_date_end`` (the other functions). When several events are equal (for example
   two runs of the same length), the dates are the ones of the first.

.. code:: python

   import datetime
   import icclim
   from icclim import build_threshold

****************************
 Max of tas within the year
****************************

.. code:: python

   file_tas = "tas_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"

   icclim.maximum(
       in_files=file_tas,
       var_name="tas",
       slice_mode="year",
   )

*********************************************************************
 Min of positive values within the year and the date of this minimum
*********************************************************************

Get minimum temperature which is above zero Celsius and find its date.

.. note::

   icclim automatically handles temperature conversion. Even if input data are in Kelvin,
   thresholds are typically expressed in Celsius for standard variables (tas, tasmin, tasmax).

.. note::

   An additional coordinate, ``event_date``, holds the date of the *first* occurrence of
   the minimum.

.. code:: python

   file_tasmin = "tasmin_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"

   icclim.minimum(
       in_files=file_tasmin,
       var_name="tasmin",
       threshold="> 0 degC",
       date_event=True,
       slice_mode="year",
   )

***************************
 Mean of a selected period
***************************

.. note::

   ``slice_mode=None`` is not accepted any more. To apply the operation to the whole
   selected period, use a pandas frequency as long as the period: ``"20YS"`` is one
   period of 20 years, starting at the first year of ``time_range``. The period must be
   complete: if the data do not cover it, the result is missing.

.. code:: python

   file_tas = "tas_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"

   tr = [datetime.datetime(1901, 1, 1), datetime.datetime(1920, 12, 31)]

   icclim.average(
       in_files=file_tas,
       var_name="tas",
       slice_mode="20YS",
       time_range=tr,
   )

*************************************************************
 Number of days when tas < 15 degrees Celsius of each Autumn
*************************************************************

.. note::

   To get the maximum number of consecutive days for the same condition, use
   ``icclim.max_consecutive_occurrence`` with the same arguments.

.. code:: python

   file_tas = "tas_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"

   icclim.count_occurrences(
       in_files=file_tas,
       var_name="tas",
       threshold="< 15 degC",
       slice_mode="SON",
   )

*************************************************************************
 Percentage of days when tasmax > 80th pctl and at which date it happens
*************************************************************************

.. note::

   80th pctl: 80th percentile of tasmax in base period

.. note::

   Two additional coordinates are created: ``event_date_start`` (the date of the first
   occurrence of tasmax > 80th pctl) and ``event_date_end`` (the date of the last
   occurrence).

.. code:: python

   file_tasmax = "tasmax_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"
   bp = [datetime.datetime(1960, 1, 1), datetime.datetime(1969, 12, 31)]

   icclim.index(
       index_name="count_occurrences",
       in_files=file_tasmax,
       var_name="tasmax",
       threshold="> 80 doy_per",
       base_period_time_range=bp,
       slice_mode="year",
       out_unit="%",
       date_event=True,
   )

************************************************************
 Number of days when daily precipitation amount > 85th pctl
************************************************************

.. note::

   daily precipitation amount: daily precipitation amount on a wet day
   (RR >= 1.0 mm)

.. note::

   85th pctl: percentile of precipitation on wet days in base period

.. code:: python

   file_pr = "pr_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"
   bp = [datetime.datetime(1960, 1, 1), datetime.datetime(1969, 12, 31)]

   icclim.index(
       index_name="count_occurrences",
       in_files=file_pr,
       var_name="pr",
       threshold=build_threshold("> 85 period_per", threshold_min_value="1 mm/day"),
       base_period_time_range=bp,
       slice_mode="year",
   )

***************************************************************************************
 Max number of consecutive days when tasmax >= 25 degrees Celsius + date of the events
***************************************************************************************

.. note::

   Two additional coordinates are created: ``event_date_start`` (the first date of the
   found sequence) and ``event_date_end`` (its end).

.. warning::

   If there are several sequences of the same length, the dates correspond to the
   *first* sequence.

.. note::

   Since icclim 7.4.0, a sequence that crosses the end of an output period is counted in
   the period where it ends. Pass ``run_index="first"`` to count it where it starts.

.. code:: python

   file_tasmax = "tasmax_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"

   icclim.max_consecutive_occurrence(
       in_files=file_tasmax,
       var_name="tasmax",
       threshold=">= 25 degC",
       date_event=True,
       slice_mode="year",
   )

****************************************************
 Max of sum of precipitation in 10 consecutive days
****************************************************

.. code:: python

   file_pr = "pr_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"

   icclim.max_of_rolling_sum(
       in_files=file_pr,
       var_name="pr",
       rolling_window_width=10,
       slice_mode=["season", [4, 5, 6, 7, 8]],
   )

******************************************************************
 Min of mean of tasmin in 7 consecutive days + date of the events
******************************************************************

.. note::

   Two additional coordinates are created: ``event_date_start`` (the date corresponding
   to the beginning of the "window" satisfying the condition) and ``event_date_end``
   (the date corresponding to the end of the "window").

.. warning::

   If several "windows" with the same result are found, the dates correspond to the
   *first* one.

.. code:: python

   file_tasmin = "tasmin_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"

   icclim.min_of_rolling_average(
       in_files=file_tasmin,
       var_name="tasmin",
       rolling_window_width=7,
       date_event=True,
       slice_mode=["season", [11, 12, 1, 2]],
   )

************************************************
 Anomaly of tasmax between 2 period of 30 years
************************************************

.. note::

   Result could be returned as percentage value relative to mean value
   of reference period, if ``out_unit='%'``.

.. note::

   The reference period is a part of the data given in ``in_files``: this is why
   ``icclim.index`` is used, with ``base_period_time_range``, and not the generic
   function (which has no such parameter). As the reference period is not a part of the
   studied period, ``sampling_method="groupby_ref_and_resample_study"`` is needed.

.. code:: python

   file_tasmax = "tasmax_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"
   # studied period: future period
   tr = [datetime.datetime(1971, 1, 1), datetime.datetime(2000, 12, 31)]
   # reference period: past period
   tr_base = [datetime.datetime(1901, 1, 1), datetime.datetime(1930, 12, 31)]

   icclim.index(
       index_name="difference_of_means",
       in_files=file_tasmax,
       var_name="tasmax",
       time_range=tr,
       base_period_time_range=tr_base,
       sampling_method="groupby_ref_and_resample_study",
   )

**********************************************************************************
 Number of days when tasmin >= 10 degrees Celsius and tasmax > 25 degrees Celsius
**********************************************************************************

.. note::

   Give one threshold per variable in ``in_files``. The thresholds are combined with
   AND: a day is counted when all the conditions are true.

.. note::

   To get the maximum number of consecutive days for the same conditions, use
   ``icclim.max_consecutive_occurrence`` with the same arguments.

.. code:: python

   file_tasmin = "tasmin_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"
   file_tasmax = "tasmax_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"

   icclim.count_occurrences(
       in_files={
           "tasmin": {"study": file_tasmin, "thresholds": build_threshold(">= 10 degC")},
           "tasmax": {"study": file_tasmax, "thresholds": build_threshold("> 25 degC")},
       },
       slice_mode="JJA",
   )

**************************************************************************************************
 Percentage of days when tasmin >= 10 degrees Celsius and tasmax > 90th pctl + date of the events
**************************************************************************************************

.. note::

   It is possible to use numeric and percentile threshold at the time.

.. code:: python

   file_tasmin = "tasmin_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"
   file_tasmax = "tasmax_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"
   bp = [datetime.datetime(1960, 1, 1), datetime.datetime(1969, 12, 31)]

   icclim.index(
       index_name="count_occurrences",
       in_files={
           "tasmin": {"study": file_tasmin, "thresholds": ">= 10 degC"},
           "tasmax": {"study": file_tasmax, "thresholds": "> 90 doy_per"},
       },
       base_period_time_range=bp,
       slice_mode="JJA",
       out_unit="%",
       date_event=True,
   )

.. _examples_cd_cw_wd_ww_label:

*************************************************************
 Number of days when tas < 25th pctl and precip. > 75th pctl
*************************************************************

4 compound indices defined in
https://knmi-ecad-assets-prd.s3.amazonaws.com/documents/atbd.pdf (see
the section 5.3.3 "Compound indices") are based on daily precipitation
(RR) and mean temperature (TG) variables:

   -  CD (cold/dry days): (TG < 25th pctl) and (RR < 25th pctl)
   -  CW (cold/wet days): (TG < 25th pctl) and (RR > 75th pctl)
   -  WD (warm/dry days): (TG > 75th pctl) and (RR < 25th pctl)
   -  WW (warm/wet days): (TG > 75th pctl) and (RR > 75th pctl)

These are the ECA&D indices ``icclim.cd``, ``icclim.cw``, ``icclim.wd`` and
``icclim.ww``, which take a ``base_period_time_range``. The generic form below gives the
same CW with the thresholds written by hand.

.. note::

   RR is a daily precipitation on a *wet* day, and its percentile value
   is computed from set of wet days also.

.. note::

   Percentiles thresholds computing uses differents methods as it was
   described :ref:`here <pctl_methods_label>`.

.. code:: python

   file_pr = "pr_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"
   file_tas = "tas_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"
   bp = [datetime.datetime(1960, 1, 1), datetime.datetime(1969, 12, 31)]

   icclim.index(
       index_name="count_occurrences",
       in_files={
           "tas": {"study": file_tas, "thresholds": "< 25 doy_per"},
           "pr": {
               "study": file_pr,
               "thresholds": build_threshold(
                   "> 75 period_per", threshold_min_value="1 mm/day"
               ),
           },
       },
       base_period_time_range=bp,
       slice_mode="year",
   )

***************************************************************************************
 Number of days when tasmax > 90th pctl and tasmin >= 10 and precipitation < 30th pctl
***************************************************************************************

.. code:: python

   file_pr = "pr_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"
   file_tasmax = "tasmax_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"
   file_tasmin = "tasmin_day_CNRM-CM5_historical_r1i1p1_19010101-20001231.nc"
   bp = [datetime.datetime(1960, 1, 1), datetime.datetime(1969, 12, 31)]

   icclim.index(
       index_name="count_occurrences",
       in_files={
           "tasmax": {"study": file_tasmax, "thresholds": "> 90 doy_per"},
           "tasmin": {"study": file_tasmin, "thresholds": ">= 10 degC"},
           "pr": {
               "study": file_pr,
               "thresholds": build_threshold(
                   "< 30 period_per", threshold_min_value="1 mm/day"
               ),
           },
       },
       base_period_time_range=bp,
       slice_mode="SON",
   )
