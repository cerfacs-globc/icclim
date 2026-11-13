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

.. _dcsc_trav_order:

********************************************
TRAV: the order of the variables of var_name
********************************************

``TRAV``, the mean of the daily thermal amplitude, is the mean of ``TX - TN``, the
daily maximum minus the daily minimum temperature. ``var_name`` is positional: its
**first** name is the minuend (``TX``) and its **second** name is the subtrahend
(``TN``), whatever the names of the variables. To get ``TX - TN``, call
``icclim.dcsc.trav(ds, var_name=["tasmax", "tasmin"])``.

.. code:: python

   import icclim

   # ds has tasmin = 0 degC and tasmax = 10 degC every day.

   # TX - TN: the first name is the maximum.
   icclim.dcsc.trav(ds, var_name=["tasmax", "tasmin"]).TRAV   # 10

   # TN - TX: the first name is the minimum, the amplitude is negative.
   icclim.dcsc.trav(ds, var_name=["tasmin", "tasmax"]).TRAV   # -10

   # Without var_name the variables are found in the dataset: TX - TN.
   icclim.dcsc.trav(ds).TRAV                                   # 10

====================================================  =========  ==================
Call                                                  Computes   Result for 0 and 10
====================================================  =========  ==================
``var_name=["tasmax", "tasmin"]``                     TX - TN    ``10``
``var_name=["tasmin", "tasmax"]``                     TN - TX    ``-10``
no ``var_name`` (variables found by name)             TX - TN    ``10``
====================================================  =========  ==================

The first time ``TRAV`` is computed in a process, icclim prints on stdout what it
computes, with the variables that are used, for example::

   TRAV = tasmax - tasmin (first input minus second; pass var_name=['tasmax', 'tasmin'] to control the order)

Until 7.3.x, the variables found in the dataset were used in the order ``TN``,
``TX``, so the result had the wrong sign when ``var_name`` was not given. The
calls with a ``var_name`` have always followed its order.

See :ref:`dcsc api` for the full API.
