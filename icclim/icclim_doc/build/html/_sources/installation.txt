Installation
============


Dependencies
-------------------------
To use the ICCLIM you first need to install the following python libraries:
    - `NumPy <http://www.numpy.org/>`_
    - `netCDF4 <http://netcdf4-python.googlecode.com/svn/trunk/docs/netCDF4-module.html>`_
    - `ctypes <http://docs.python.org/2/library/ctypes.html>`_
    - `OpenClimateGIS <http://ncpp.github.io/ocgis/index.html>`_ and its dependencies if you want to use :ref:`ICCLIM inside OpenClimateGIS <icclim_ocgis>`
    - `ESMPy <https://www.earthsystemcog.org/projects/esmpy/>`_ if you want to use :ref:`regridding module <icclim_regrid>`
    
Installation (Linux)
--------------------
.. note:: Make sure that **Python 2.7** and **GCC** are installed.

1. Go to `<https://github.com/tatarinova/icclim>`_.
2. Download the current version: click to **Download ZIP**.
3. Extract the file.
4. Go to extracted directory.
5. Run the following commands:

.. code-block:: sh
    
    gcc -fPIC -g -c -Wall ./icclim/libC.c -o ./icclim/libC.o
    
    gcc -shared -o ./icclim/libC.so ./icclim/libC.o
    
    [sudo] python setup.py install
    
5. Check if the library is installed correctly:

.. code-block:: sh

    >>> import icclim
    
To get the version of installed library, do the following:

.. code-block:: sh

    >>> icclim.__version__
    3.0


.. note:: ICCLIM was not tested on Windows and Mac platforms...