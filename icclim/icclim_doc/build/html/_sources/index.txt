
Welcome to ICCLIM's documentation!
==================================

*Index Calculation CLIMate* is a Python libary designed for calculation of climate indices and indicators. 
*ICCLIM* calculates `ECA&D climate indices <http://eca.knmi.nl/documents/atbd.pdf>`_.
But other climate indices and indicators could be added. 



Contents:

.. toctree::

    
   intro.rst
   important_to_know.rst
   installation.rst
   python_api.rst
   output_metadata.rst
   contact.rst 
    
   icclim_ocgis.rst



**NEWS:**

*24/10/2014*

- New version: 2.2
- Added compound percentile-based indices: CD, CW, WD and WW
- Percentiles are now computed by C function to take into account fill_values

*9/10/2014*

- It is possible now to do :ref:`regridding <icclim_regrid>` (works only with rectangular "lat/lon" grid).

*8/08/2014*

- :func:`icclim.get_percentile_dict()` works now with OPeNDAP datasets (added the ``transfer_limit_bytes`` parameter)

*4/08/2014*

- Improved callback in :func:`icclim.indice()`, :func:`icclim.indice_multivar()` and :func:`icclim.indice_perc()`

*31/07/2014*

- Possibility to save a dictionary with daily percentiles in file (added the ``save_to_file`` parameter in :func:`icclim.get_percentile_dict()`)

*21/07/2014*

In :func:`icclim.indice()`, :func:`icclim.indice_multivar()` and :func:`icclim.indice_perc()`:

- Removed the ``project`` parameter
- The ``time_range`` parameter is not required, i.e. if it is None, then the whole period of input files will be processed


*17/07/2014*

- Added percentile indices
- Added utility functions for spatial statistics
- The documentation is updated


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

