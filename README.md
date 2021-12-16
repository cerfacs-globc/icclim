icclim
======

icclim (Index Calculation CLIMate) is a Python library for climate indices calculation.

This open-source project has been possible thanks to funding by the European Commission Projects FP7-IS-ENES2 (2013-2017), FP7-CLIPC (2013-2016) and EUDAT2020 (2015-2018). Now under development through new funding from H2020-IS-ENES3 (2019-2022). It is used as a backend on the C4I platform https://dev.climate4impact.eu and on the CLIPC Portal http://www.clipc.eu

Development is very active at the moment, with version 5.0.0rc2 in the develop branch https://github.com/cerfacs-globc/icclim/tree/develop .
It is lead by CERFACS, a research institution located in Toulouse, France.

For documentation please visit: http://icclim.readthedocs.org

Quick Install Instructions (version 5.x and above): Recommended version but documentation not up-to-date yet
------------------------------------------------------------------------------------------------------------

Branch is https://github.com/cerfacs-globc/icclim/tree/develop

pip install icclim=5.0.0rc2

Quick Install Instructions (version 4.x and under)
--------------------------------------------------

Master https://github.com/cerfacs-globc/icclim

gcc -fPIC -g -c -Wall ./icclim/libC.c -o ./icclim/libC.o

gcc -shared -o ./icclim/libC.so ./icclim/libC.o

python setup.py install --user

or as root: python setup.py install

Indices
-------
For a detailed description of each ECA index, please visit: https://www.ecad.eu/documents/atbd.pdf
