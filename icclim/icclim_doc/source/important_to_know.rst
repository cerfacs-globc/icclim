
Important to know
===============================
Here is an overview of some important points.

Libraries to istall
-------------------------
To use the ICCLIM you will need to install also the following python libraries:
    - `NumPy <http://www.numpy.org/>`_
    - `netCDF4 <http://netcdf4-python.googlecode.com/svn/trunk/docs/netCDF4-module.html>`_
    - `ctypes <http://docs.python.org/2/library/ctypes.html>`_

Installation (Linux)
--------------------
.. note:: Make sure that **Python 2.7** and **GCC** are installed.

1. Go to `<https://github.com/tatarinova/icclim>`_.
2. Download the current version: click to **Download ZIP**.
3. Go to extracted directory.
4. Run the following commands:

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
    0.0.1


.. note:: ICCLIM was not tested on Windows and Mac platforms...

CF convention
-------------
NetCDF files to process must be compliant to the `CF convention <http://cf-pcmdi.llnl.gov/documents/cf-conventions/>`_.


Variable to process
-------------------

.. warning:: For the moment, the library processes only 3D variables.

Needs to respect the correspondence between the variable to process and the indice to calculate.
For example, the FD indice needs '*the daily minimum temperature*' variable (e.g. "tasmin").


+------------------------------------------------------------+---------------------------------------------+
|   Indice                                                   |   Variable                                  |
+============================================================+=============================================+
|TG, GD4, GSL, HD                                            |  daily mean temperature                     |
+------------------------------------------------------------+---------------------------------------------+
|TN, TR, TNx, CFD, FD, TNn                                   |  daily minimum temperature                  |
+------------------------------------------------------------+---------------------------------------------+
|TX, SU, TXx, CSU                                            |  daily maximum temperature                  |
+------------------------------------------------------------+---------------------------------------------+
|DTR, ETR, vDTR                                              |  daily minimum + daily maimum temperature   |
+------------------------------------------------------------+---------------------------------------------+
|                                                            |                                             |
|RR, RR1, SDII, CWD, CDD, R10mm, R20mm, RX1day, RX5day       |  daily precipitation (liquide phase)        |
+------------------------------------------------------------+---------------------------------------------+
|SD, SD1, SD5cm, SD50cm                                      |  daily precipitation (solid phase)          |
+------------------------------------------------------------+---------------------------------------------+



Inputs/Outputs
---------------------

Main function:

.. function:: indice(in_files_list, out_file, var, indice_name, time_range, slice_mode, project, N_lev=None):
    
    
    This function returns result NetCDF file containing a climate indice.
    
    
    :param in_files_list: absolute paths to NetCDF dataset (including URLs)
    :type in_files_list: list of str
    :param out_file: output NetCDF file
    :type out_file: str
    :param var: variable name to process
    :type var: str
    :param indice_name: climate indice name
    :type indice_name: str
    :param time_range: time range (dt1 is the first day of year/month, dt2 is the last day of year/month)
    :type time_range: list of 2 datetime objects [dt1, dt2]  
    :param slice_mode: "year" for annual values, "month" for monthly values (soon: seasonal aggregation)
    :type slice_mode: str
    :param project: project name ("CMIP5" or "CORDEX")
    :type project: str
    :param N_lev: level number if 4D variable (dafault: N_lev=None)
    :type N_lev: int
    :rtype: output NetCDF file name

.. note:: The list of indice names are :ref:`here <indices.rst>`_ .  

Some utility functions:

.. function:: SU_calculation(a, fill_val, t=25):
    
    Calculates the indice SU: summer days (daily maximum temperature > 25 degrees Celsius).
    
    :param a: variable array to process (daily maximum temperature (e.g."tasmax"))
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    :param t: temperature threshold [degrees Celsius] (default: t = 25 degrees Celsius)
    :type t: float
    
    :rtype: numpy.ndarray (2D)
           

.. function:: CWD_calculation(a, fill_val, precip_thresh=1):

    Calculates the indice CWD: maximum number of consecutive wet days (daily precipitation >= 1 mm).
    This function calls C function "find_max_len_consec_sequence_3d" from libC.c
    
    :param a: variable array to process (daily liquide precipitation [mm/s])
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    :param precip_thresh: precipitation threshold [mm] (default: precip_thresh = 1 mm)
    :type precip_thresh: float
    
    :rtype: numpy.ndarray (2D)

    
.. function:: check_att(nc, att):
        
    Checks if a global attribut exists in dataset.
    
    :param nc: NetCDF dataset
    :type nc: netCDF4.Dataset 
    :param att: attribut name
    :type att: str
    
    :rtype: int (1 if attribut exists, 0 else)


.. function:: get_att_value(nc, var, att):
    
    Returns an attribut value of a variable in dataset.
    
    :param nc: NetCDF dataset
    :type nc: netCDF4.Dataset
    :param var: variable name in dataset
    :type var: str
    :param att: attribut name
    :type att: str
    
    :rtype: str
    

