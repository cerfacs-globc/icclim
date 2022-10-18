|logo|
======

|build| |pypi| |black| |docs| |conda| |coverage| |doi|

icclim is a Python library to compute climate indices.
icclim name stands for index, calculation, climate.

Installation
------------

From pypi: ``pip install icclim``.

From conda-forge: ``conda install -c conda-forge icclim``.

From sources:
    - Clone the repository ``git clone https://github.com/cerfacs-globc/icclim.git``
    - Install icclim ``python -m setup install``

How to use icclim
-----------------

Let's count the number of days above 25°C for each year, which corresponds to the index ``SU``, from a `tasmax` variable scattered in multiple netcdf files.

`SU` is one of the many index that can be computed with icclim. See `the documentation <https://icclim.readthedocs.io/en/latest/explanation/climate_indices.html#icclim-capabilities>`_ to explore what other index you can compute with icclim.

.. code-block:: python

    import icclim

    summer_days = icclim.su(
        "netcdf_files/tasmax_1990-2100.nc", out_file="summer_days.nc"
    )

For more examples on how to use icclim, see icclim's `How to ... <https://icclim.readthedocs.io/en/latest/how_to/index.html>`_ documentation or
`our notebooks <https://gitlab.com/is-enes-cdi-c4i/notebooks/-/tree/master/>`_.


Who use icclim
--------------

icclim is part of `C4I platform <https://dev.climate4impact.eu>`_ backend and is integrated in `CLIPC Portal <http://www.clipc.eu>`_.
icclim is also used by some independent researchers.


Who made icclim
---------------

icclim has always been an open source project and was successfully made thanks to the joint effort of all its contributors.
The lead development is made at `CERFACS <https://cerfacs.fr/en/>`_, a research institution located in Toulouse, France.

Grants
~~~~~~
This open-source project has been possible thanks to funding by the European Commission projects:

* FP7-CLIPC (2013-2016)
* FP7-IS-ENES2 (2013-2017)
* EUDAT2020 (2015-2018)
* H2020-IS-ENES3 (2019-2023)

The beautiful icclim logo is a creation of `Carole Petetin <https://carolepetetin.com>`_ and has been funded by the H2020 `IS-ENES3 <https://is.enes.org>`_ project grant agreement No 824084 (2019-2023).


Indices
-------
For a detailed description of each ECA&D index, please visit: https://www.ecad.eu/documents/atbd.pdf

..
  Pytest Coverage Comment:Begin

.. |coverage| image:: https://img.shields.io/badge/Coverage-91%25-brightgreen.svg
        :target: https://github.com/cerfacs-globc/icclim/blob/master/README.rst#code-coverage
        :alt: Code coverage

..
  Pytest Coverage Comment:End


.. |docs| image:: https://readthedocs.org/projects/icclim/badge/?version=latest
        :target: https://icclim.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
        :target: https://github.com/python/black
        :alt: Python Black

.. |pypi| image:: https://img.shields.io/pypi/v/icclim.svg
        :target: https://pypi.python.org/pypi/icclim
        :alt: Python Package Index Build

.. |build| image:: https://github.com/cerfacs-globc/icclim/actions/workflows/ci.yml/badge.svg?branch=master
        :target: https://github.com/cerfacs-globc/icclim/actions/workflows/ci.yml
        :alt: Build Status

.. |conda| image:: https://img.shields.io/conda/vn/conda-forge/icclim.svg
        :target: https://anaconda.org/conda-forge/icclim
        :alt: Conda-forge Build Version

.. |doi| image:: https://zenodo.org/badge/15936714.svg
        :target: https://zenodo.org/badge/latestdoi/15936714
        :alt: D.O.I link

.. |logo| image:: https://github.com/cerfacs-globc/icclim/raw/master/doc/source/_static/logo_icclim_colored__displayed.svg
        :target: https://github.com/cerfacs-globc/icclim
        :alt: icclim
        :width: 200px
