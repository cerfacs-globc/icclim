icclim
======

icclim (Index Calculation CLIMate) is a Python library for climate indices calculation.

This open-source project has been possible thanks to funding by the European Commission Projects FP7-IS-ENES2 (2013-2017) and FP7-CLIPC (2013-2016). It is used as a backend on the C4I platform http://climate4impact.eu and on the CLIPC Portal http://www.clipc.eu

Development is not funded at the moment, but code is still being actively developed as much as possible.
It is lead by CERFACS, a research institution located in Toulouse, France.

For documentation please visit: http://icclim.readthedocs.org

Quick Install Instructions
--------------------------

gcc -fPIC -g -c -Wall ./icclim/libC.c -o ./icclim/libC.o

gcc -shared -o ./icclim/libC.so ./icclim/libC.o

python setup.py install --user

or as root: python setup.py install
