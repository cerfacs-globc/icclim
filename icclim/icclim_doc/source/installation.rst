Installation
============


Dependencies
------------
To use the ICCLIM you first need to install the following python libraries:
    - `NumPy <http://www.numpy.org/>`_
    - `netCDF4 (make sure you have at least version 1.2.9+) <http://unidata.github.io/netcdf4-python/>`_
    - `cftime <https://unidata.github.io/cftime/>`_ 
    - `ctypes <http://docs.python.org/2/library/ctypes.html>`_
    - `OpenClimateGIS <https://github.com/NCPP/ocgis>`_ and its dependencies if you want to use `ICCLIM inside OpenClimateGIS <https://ocgis.readthedocs.io/en/latest/computation.html?highlight=icclim#calculation-using-icclim-for-eca-indices>`_
    - `ESMPy <https://earthsystemmodeling.org/esmpy/>`_ if you want to use :ref:`regridding module <icclim_regrid>`
    
Installation (Linux, OS X)
--------------------------
.. note:: Make sure that **Python 3.6+** and **GCC** are installed.

1. Go to `<https://github.com/cerfacs-globc/icclim/releases/>`_.
2. Download the last release: click to **Source code (zip)** or **Source code (tar.gz)**.
3. Extract the file.
4. Go to extracted directory.
5. Run the following commands:

.. code-block:: sh
    
    gcc -fPIC -g -c -Wall ./icclim/libC.c -o ./icclim/libC.o
    
    gcc -shared -o ./icclim/libC.so ./icclim/libC.o
    
    [sudo] python setup.py install

or if you don't have root or sudo access, as a normal user:

.. code-block:: sh    

    python setup.py install --user
    
5. Check if the library is installed correctly:

.. code-block:: sh

    >>> from icclim import icclim
    
To get the version of installed library, do the following:

.. code-block:: sh

    >>> icclim.__version__
    4.2.16


.. note:: ICCLIM was not tested on Windows platform...
