*************************
Cold-Spell Duration Index
*************************

About
=====
In this tutorial, we will show you haw to calculate the :ref:`Cold-Spell Duration Index<csdi>` (CSDI), using data provided by Copernicus Climate Change Service (`C3S`_).

After preparing our environment, we will download the minimum temperature data from C3S `Climate Data Store`_, inspect them and use the :mod:`icclim` library to calculate the CSDI. Finally, we will display the CSDI using :mod:`matplotlib` to end up with the following map.

.. image:: E_OBS_csdi_index.png
    :align: center
    :alt: European map of the Cold-Spell Duration Index

.. _C3S: https://climate.copernicus.eu/
.. _Climate Data Store: https://cds.climate.copernicus.eu/