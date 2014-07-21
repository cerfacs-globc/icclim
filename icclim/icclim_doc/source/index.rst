
Welcome to ICCLIM's documentation!
==================================

*Index Calculation CLIMate* is a Python libary designed for calculation of climate indices and indicators. 
For the first time ICCLIM calculates `ECA&D climate indices <http://eca.knmi.nl/documents/atbd.pdf>`_.
Later other climate indices and indicators will be added. 



Contents:

.. toctree::

    

   important_to_know.rst
   installation.rst
   python_api.rst
   output_metadata.rst
   contact.rst 
    
   icclim_ocgis.rst
    

**NEWS:**

*21/07/2014*

In the functions "icclim.indice()", "icclim.indice_multivar()" and "icclim.indice_perc()":

- Removed the "project" parameter
- The "time_range" parameter is not required, i.e. if it is None, then the whole period of input files will be processed


*17/07/2014*

- Added percentile indices
- Added utility functions for spatial statistics
- The documentation is updated


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

