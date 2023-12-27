..
   icclim documentation master file, created by
   sphinx-quickstart on Tue Dec 14 14:42:00 2021.

.. _dask: https://dask.org/

.. _diataxis: https://diataxis.fr/

.. _netcdf: http://www.unidata.ucar.edu/software/netcdf

.. _numpy: http://www.numpy.org

.. _xarray: https://xarray.pydata.org/en/stable/

.. _xclim: https://xclim.readthedocs.io/en/stable/

######################
 icclim documentation
######################

Welcome to icclim documentation. icclim (Index Calculation for CLIMate)
is a Python library to compute climate indices. It is built on a open
source stack made of xclim_, xarray_, dask_ and of course NumPy_.

.. note::

   icclim documentation is currently under construction. We try to
   follow the diataxis_ principles to build a comprehensive user focused
   documentation.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   tutorials/index
   how_to/index
   references/index
   explanation/index
   dev/index

**************************
 A few notes about icclim
**************************

#. Input datasets must be compliant to the `CF convention
   <https://cfconventions.org/>`_.
#. Currently, *icclim* doesn't support spatial subsetting, i.e. it
   processes whole spatial area.
#. *icclim* works with unsecured OPeNDAP datasets as well.
#. icclim developer repository can be found here:
   https://github.com/cerfacs-globc/icclim

**********
 Contacts
**********

Add If you encounter a bug or an issue while using icclim, don't
hesitate to open a ticket on our `github
<https://github.com/cerfacs-globc/icclim/issues>`_.

Maintainers
===========

-  Christian Page, `@pagecp <https://github.com/pagecp/>`_
   <christian.page[at]cerfacs.fr>
-  Abel Aoun, `@bzah <https://github.com/bzah>`_
   <abel.aoun[at]cerfacs.fr>

********
 Grants
********

This open-source project has been possible thanks to funding by the
European Commission projects:

-  FP7-CLIPC (2013-2016)
-  FP7-IS-ENES2 (2013-2017)
-  EUDAT2020 (2015-2018)
-  H2020-IS-ENES3 (2019-2023)

The beautiful icclim logo is a creation of `Carole Petetin
<https://carolepetetin.com>`_ and has been funded by the H2020 `IS-ENES3
<https://is.enes.org>`_ project grant agreement No 824084 (2019-2023).
