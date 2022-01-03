icclim
======

|build| |pypi| |black| |docs|


icclim (Index Calculation CLIMate) is a Python library for climate indices calculation.

This open-source project has been possible thanks to funding by the European Commission Projects FP7-IS-ENES2 (2013-2017), FP7-CLIPC (2013-2016) and EUDAT2020 (2015-2018).
Now under development through new funding from H2020-IS-ENES3 (2019-2022).
It is used as a backend on the C4I platform https://dev.climate4impact.eu and on the CLIPC Portal http://www.clipc.eu

Development is very active at the moment, with version 5.0.0.
It is lead by CERFACS, a research institution located in Toulouse, France.

For documentation please visit: http://icclim.readthedocs.org

Quick Install Instructions (version 5.x and above)
--------------------------------------------------

Branch is https://github.com/cerfacs-globc/icclim/tree/master

pip install icclim

Quick Install Instructions (version 4.x and under)
--------------------------------------------------

For version 4.2.20 https://github.com/cerfacs-globc/icclim/tree/4.2.20

gcc -fPIC -g -c -Wall ./icclim/libC.c -o ./icclim/libC.o

gcc -shared -o ./icclim/libC.so ./icclim/libC.o

python setup.py install --user

or as root: python setup.py install

Indices
-------
For a detailed description of each ECA index, please visit: https://www.ecad.eu/documents/atbd.pdf


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
