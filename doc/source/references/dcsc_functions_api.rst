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

See :ref:`dcsc api` for the full API.
