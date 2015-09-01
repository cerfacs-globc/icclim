
Welcome to ICCLIM's documentation!
==================================

ICCLIM (Indice Calculation CLIMate) is a Python library for computing a number of :ref:`climate indices <climate_indices_label>`. 


Contents:

.. toctree::

    
   intro.rst
   installation.rst
   python_api.rst
   output_metadata.rst
   contact.rst     




Release notes
------------------

*21/08/2015*

(http://stackoverflow.com/questions/2862590/how-to-replace-master-branch-in-git-entirely-from-another-branch)

- New version: 3.1.0
- Percentile threshold computing is now directly inside icclim.indice() function:
	- added new parameters:
		- ``ignore_Feb29th`` (allow to ignore February 29th)
		- ``base_period_time_range`` for base period time range 
		- ``window_width``
		- ``only_leap_years``
		- ``interpolation`` (2 interpolation methods: linear and interpolation proposed by `Hyndman and Fan (1996) <http://amherst.edu/media/view/129116/original/Sample+Quantiles.pdf>`_)
		- ``save_percentiles_to_file``
		- ``out_unit`` ('days' or '%' for indices: TG10p, TG90p, TX10p, TX90p, TN10p, TN90p)
- Implemented *bootstrapping* procedure (See "Removing the “jump”" section in `this article <http://journals.ametsoc.org/doi/pdf/10.1175/JCLI3366.1>`_). 
- Possibility of setting user defined seasons. 
- `ETCCDI climate indices <http://etccdi.pacificclimate.org/list_27_indices.shtml>`_ is used now as indices definition:
	- Indices *R95pTOT* and *R99pTOT* changed their definition (removed the division in the formula).
	- Indice *RR* changed its definition (before: sum of precipitation; now: sum of precipitation only of wet days) and renamed to *PRCPTOT*.


*27/01/2015*

- New version: 3.0
- :func:`icclim.indice()` is now used for all indices (simple, multivariable, percentile-based, etc)
- Added seasonal temporal aggregations: "ONDJFM", "AMJJAS", "DJF", "MAM", "JJA" and "SON".


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

