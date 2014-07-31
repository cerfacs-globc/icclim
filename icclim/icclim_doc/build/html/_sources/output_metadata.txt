
Output metadata
================

The output metadata contains at least the following variables:
    - lat
    - lon
    - time
    - time_bnds
    - indice 

lat, lon
---------
We copy the *lat* and *lon* variables from source file with all their attributes.

time
-----
If *slice_mode='year'*, the time steps will be the 1st July of each year ("YYYY-07-01"):

.. code-block:: rest

    $ ncdump -v time indice_FD_year_19860101_19901231.nc -t
    
    [...]
    
    time = "1986-07-01", "1987-07-01", "1988-07-01", "1989-07-01", "1990-07-01" ;

If *slice_mode='month'*, the time steps will be the 16th day of each month ("YYYY-MM-16"):

.. code-block:: rest

    $ ncdump -v time indice_FD_month_19860101_19901231.nc -t
    
    [...]
    
    time = "1986-01-16", "1986-02-16", "1986-03-16", "1986-04-16", "1986-05-16", 
        "1986-06-16", "1986-07-16", "1986-08-16", "1986-09-16", "1986-10-16", 
        "1986-11-16", "1986-12-16", "1987-01-16", "1987-02-16", "1987-03-16", 
        "1987-04-16", "1987-05-16", "1987-06-16", "1987-07-16", "1987-08-16",
        ...


time_bnds
----------

If *slice_mode='year'*, the *time_bnds* values will be the 1st January of year and the 1st January of next year:

.. code-block:: rest

    $ ncdump -v time_bnds indice_FD_year_19860101_19901231.nc -t

    [...]
    
    time_bnds =
      "1986-01-01", "1987-01-01",
      "1987-01-01", "1988-01-01",
      "1988-01-01", "1989-01-01",
      "1989-01-01", "1990-01-01",
      "1990-01-01", "1991-01-01" ;    


If *slice_mode='month'*, the *time_bnds* values will be the 1st day of month and the 1st day of next month:

.. code-block:: rest

    $ ncdump -v time_bnds indice_FD_month_19860101_19901231.nc -t
    
    [...]
    
    time_bnds =
        "1986-01-01", "1986-02-01",
        "1986-02-01", "1986-03-01",
        "1986-03-01", "1986-04-01",
        "1986-04-01", "1986-05-01",
        "1986-05-01", "1986-06-01",
        "1986-06-01", "1986-07-01",
        "1986-07-01", "1986-08-01",
        "1986-08-01", "1986-09-01",
        "1986-09-01", "1986-10-01",
        ...



.. note:: The second band in time_bnds is excluded!    
    
    
    
    

indice
-------
     
The *indice* variable has the same name as indice_name parameter (e.g. "FD").
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
            FD:standard_name = "ECA_indice" ;

    

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
		:title = "ECA cold indice FD" ;
		:institution = "Climate impact portal (http://climate4impact.eu)" ;
		:source =  ;
		:references = "ATBD of the ECA indices calculation (http://eca.knmi.nl/documents/atbd.pdf)" ;
		:comment = " " ;
		:history = "2011-04-07T06:39:36Z CMOR rewrote data to comply with CF standards and CMIP5 requirements. \n",
                        "2014-04-01 12:16:03 Calculation of FD indice (monthly time series) from 1986-1-1 to 1990-12-31." ;




However other global attributes can be added.

