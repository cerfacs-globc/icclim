icclim
======

icclim (Index Calculation CLIMate) is a Python library for climate indices calculation.

This open-source project has been possible thanks to funding by the European Commission Projects H2020-IS-ENES3 (2019-2022), H2020-DARE (2018-2020), FP7-IS-ENES2 (2013-2017) and FP7-CLIPC (2013-2016). It is used as a backend on the C4I platform http://climate4impact.eu and on the CLIPC Portal http://www.clipc.eu

Development is lead by CERFACS, a research institution located in Toulouse, France.

For documentation please visit: http://icclim.readthedocs.org

This version is an alpha version using xarray and dask, with a revamped structure.
All climate indices are not implemented yet, optimization is not done for all indices types, and bugs can still exist.

Quick Install Instructions
--------------------------

Python package requirements:
numpy
xarray (pandas; python-dateutil; pytz; six)
cftime
netcdf4

To install:
python setup.py install --user

or as root: python setup.py install
