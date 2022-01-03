Output metadata
================

Output metadata contains at least the following variables:

- lat
- lat_bnds
- lon_bnds
- lon
- time
- time_bnds
- index

lat, lon, lat_bnds, lon_bnds
---------------------------------
They are copied from source file with all their attributes.


time and time_bnds
--------------------

+----------------------+-----------------------+------------------------------------+
| Slice_mode           |  *time*               |  *time_bnds*                       |
+======================+=======================+=================+==================+
|  ``year``            |    YYYY-07-01         |    YYYY-01-01   | (YYYY+1)-01-01   |
+----------------------+-----------------------+-----------------+------------------+
|  ``month``           |    YYYY-MM-16         |    YYYY-MM-01   |  YYYY-(MM+1)-01  |
+----------------------+-----------------------+-----------------+------------------+
|  ``ONDJFM``          |    YYYY-01-01         |     YYYY-10-01  | (YYYY+1)-04-01   |
+----------------------+-----------------------+-----------------+------------------+
|  ``AMJJAS``          |    YYYY-07-01         |    YYYY-04-01   |  YYYY-10-01      |
+----------------------+-----------------------+-----------------+------------------+
|  ``DJF``             |    YYYY-01-16         |    YYYY-12-01   | (YYYY+1)-03-01   |
+----------------------+-----------------------+-----------------+------------------+
|  ``MAM``             |    YYYY-04-16         |    YYYY-03-01   |  YYYY-06-01      |
+----------------------+-----------------------+-----------------+------------------+
|  ``JJA``             |    YYYY-07-16         |    YYYY-06-01   |  YYYY-09-01      |
+----------------------+-----------------------+-----------------+------------------+
|  ``SON``             |    YYYY-10-16         |    YYYY-09-01   |  YYYY-12-01      |
+----------------------+-----------------------+-----------------+------------------+

.. note:: The second bound in time_bnds is excluded!

Example: annual time steps
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: rest

    $ ncdump -v time indice_FD_year_1950-1955.nc -t

    time = "1950-07-01", "1951-07-01", "1952-07-01", "1953-07-01",
        "1954-07-01", "1955-07-01" ;

    $ ncdump -v time_bnds indice_FD_year_1950-1955.nc -t

    time_bnds =
        "1950-01-01 12", "1951-01-01 12",
        "1951-01-01 12", "1952-01-01 12",
        "1952-01-01 12", "1953-01-01 12",
        "1953-01-01 12", "1954-01-01 12",
        "1954-01-01 12", "1955-01-01 12",
        "1955-01-01 12", "1956-01-01 12" ;


Example: monthly time steps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: rest

    $ ncdump -v time indice_FD_month_1950-1955.nc -t

    time = "1950-01-16", "1950-02-16", "1950-03-16", "1950-04-16",
        "1950-05-16", "1950-06-16", "1950-07-16", "1950-08-16",
        "1950-05-16", "1950-06-16", "1950-07-16", "1950-08-16",
        [...]

    $ ncdump -v time_bnds indice_FD_month_1950-1955.nc -t

    time_bnds =
        "1950-01-01 12", "1950-02-01 12",
        "1950-02-01 12", "1950-03-01 12",
        "1950-03-01 12", "1950-04-01 12",
        "1950-04-01 12", "1950-05-01 12",
        [...]

Example: seasonal time steps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: rest

    $ ncdump -v time indice_FD_DJF_1950-1955.nc -t

    time = "1951-01-16", "1952-01-16", "1953-01-16", "1954-01-16",
        "1955-01-16" ;

    $ ncdump -v time_bnds indice_FD_DJF_1950-1955.nc -t

    time_bnds =
        "1950-12-01 12", "1951-03-01 12",
        "1951-12-01 12", "1952-03-01 12",
        "1952-12-01 12", "1953-03-01 12",
        "1953-12-01 12", "1954-03-01 12",
        "1954-12-01 12", "1955-03-01 12" ;



.. code-block:: rest

    $ ncdump -v time indice_FD_SON_1950-1955.nc -t

    time = "1950-10-16", "1951-10-16", "1952-10-16", "1953-10-16",
        "1954-10-16", "1955-10-16" ;

    $ ncdump -v time_bnds indice_FD_SON_1950-1955.nc -t

    time_bnds =
        "1950-09-01 12", "1950-12-01 12",
        "1951-09-01 12", "1951-12-01 12",
        "1952-09-01 12", "1952-12-01 12",
        "1953-09-01 12", "1953-12-01 12",
        "1954-09-01 12", "1954-12-01 12",
        "1955-09-01 12", "1955-12-01 12" ;




index
-------

The *index* variable has the same name as index_name parameter (e.g. "FD").
It has the following attributes:

    - long_name
    - units
    - _FillValue
    - missing_value
    - ( grid_mapping )

Example:

.. code-block:: rest

    float FD(time, lat, lon) ;
            FD:_FillValue = 1.e+20f ;
            FD:long_name = "Frost days (minimum temperature < 0 degrees)" ;
            FD:units = "days" ;
            FD:missing_value = 1.e+20f ;
            FD:standard_name = "ECA_index" ;



.. note:: The *_FillValue* and *missing_value* are the same as in source files.


Global attributes
------------------

According to the CF convention, the output NetCDF file contains 6 main global attributes:
    - title
    - institution
    - source
    - history
    - references
    - comment

Example:

.. code-block:: rest

    // global attributes:
        :title = "ECA cold index FD" ;
        :institution = "Climate impact portal (https://climate4impact.eu)" ;
        :source =  ;
        :references = "ATBD of the ECA indices calculation (https://www.ecad.eu/documents/atbd.pdf)" ;
        :comment = " " ;
        :history = "2011-04-07T06:39:36Z CMOR rewrote data to comply with CF standards and CMIP5 requirements. \n",
                        "2014-04-01 12:16:03 Calculation of FD index (monthly time series) from 1950-1-1 to 1955-12-31." ;
