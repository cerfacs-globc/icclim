.. icclim_doc documentation master file, created by
   sphinx-quickstart on Thu Mar 26 15:23:24 2026.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

**********************
*icclim* documentation
**********************

**Date**: |today| **Version**: |version|

**Useful link**: Binary installer | Source Repository | Issues & Ideas |

Welcome to :mod:`icclim` documentation!
:mod:`icclim` (Index Calculation for CLIMate) is a Python library to compute climate indices. It is build on a source stack made of :mod:`xclim`, :mod:`xarray`, :mod:`dask` and of course :mod:`numpy`.

{% if not single_doc or single_doc == "index.rst" -%}
.. toctree::

   Tuto
   How to
   Ref Explanation
   
{% endif %}


