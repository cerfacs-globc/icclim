.. _dcsc_functions_api:

###############
 DCSC indices
###############

icclim 6.6 adds a ``icclim.dcsc`` namespace for the DCSC indices of Meteo France.

*****
Usage
*****

.. code:: python

   import icclim

   txnd = icclim.dcsc.txnd(in_files="tas.nc", normal="tas-normal.nc", slice_mode="month").load()

   # equivalent to the follwing generic index (output metadata will be different)
   threshold=build_threshold(
            operator=">",
            value="tas-normal.nc",
            offset=" 5 delta_degree_Celsius",
        ),
   summer_days = icclim.count_occurrences(tas, threshold=threshold)

.. _dcsc_trav:

*****************************************
TRAV: always positive, whatever the order
*****************************************

``TRAV``, the mean of the daily thermal amplitude, is the **absolute value** of the
mean of ``TX - TN``, the daily maximum minus the daily minimum temperature. The daily
differences are averaged over each period, then the absolute value is taken for each
grid point. The result is **always positive** and it **does not depend on the order of
``var_name``**: the two calls below give the same result.

.. code:: python

   import icclim

   # ds has tasmin = 0 degC and tasmax = 10 degC every day.
   icclim.dcsc.trav(ds, var_name=["tasmax", "tasmin"]).TRAV   # 10
   icclim.dcsc.trav(ds, var_name=["tasmin", "tasmax"]).TRAV   # 10
   icclim.dcsc.trav(ds).TRAV                                   # 10

The absolute value is taken on the mean of the period, not on each day: when the sign
of ``TX - TN`` changes within a period, the result is not the mean of the daily
amplitudes.

The data are not checked. A ``TRAV`` computed on inconsistent data, where ``TX`` is
below ``TN`` everywhere, is positive all the same and it is not flagged.

Until 7.3.x the result was ``TN - TX``, negative, when ``var_name`` was not given or
was ``["tasmin", "tasmax"]``.

See :ref:`dcsc api` for the full API.
