
Welcome to ICCLIM's documentation!
==================================

*Index Calculation CLIMate* is a Python libary designed for calculation of climate indices and indicators. 
For the first time *ICCLIM* calculates `ECA&D climate indices <http://eca.knmi.nl/documents/atbd.pdf>`_.
Later other climate indices and indicators will be added. 



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

