.. icclim documentation master file, created by
   sphinx-quickstart on Tue Dec 14 14:42:00 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Icclim's documentation
======================

ICCLIM (Indice Calculation CLIMate) is a Python library for computing a number of climate indices.

Icclim documentation try to follow the diataxis principles.
It means you should find here Tutorials, "How to..." recipes, Technical references and Explanations.
This is however a work in progress.

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   explanation/climate_indices
   how_to/installation
   references/python_api
   references/output_metadata

The ICCLIM developer repository can be found here: `<https://github.com/cerfacs-globc/icclim>`_

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Notes about ICCLIM
------------------

1. Input dataserts must be compliant to the `CF convention <https://cfconventions.org/>`_.
2. Currently, *ICCLIM* doesn't support spatial subsetting, i.e. it processes whole spatial area.
3. *ICCLIM* works with unsecured OPeNDAP datasets as well.


Release notes
-------------

For release notes please look `here <https://github.com/cerfacs-globc/icclim/releases>`_

Contacts
------------------

<christian.page[at]cerfacs.fr>
<abel.aoun[at]cerfacs.fr>
