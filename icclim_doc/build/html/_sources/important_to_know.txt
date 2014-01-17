.. XXX documentation master file, created by
   sphinx-quickstart on Sun Dec 15 22:09:57 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Important to know
===============================
Here is an overview of some important points.

Libraries to istall
-------------------------
To use the ICCLIM you will need to install also the following python libraries:
    - `NumPy <http://www.numpy.org/>`_
    - `netCDF4 <http://netcdf4-python.googlecode.com/svn/trunk/docs/netCDF4-module.html>`_
    - `ctypes <http://docs.python.org/2/library/ctypes.html>`_


CF convention
-------------
NetCDF files to process must be compliant to the `CF convention <http://cf-pcmdi.llnl.gov/documents/cf-conventions/>`_ (at least CF-1.0).

Metadata of output NetCDF file
------------------------------

ICCLIM conserves the meta data stucture of source files:

It copies from a source file the coordinate variables (e.g. "longitude" and "lattitude") and all their attributs.
It also copies the attributs of time coordinate, but does not copy its values because it will recalculate the output time steps vector (and it will also create *time_bnds* variable).
It does not copy the vertical variable if it exists.
Then a result indice variable is created.
The name of this variable is the same as indice name (e.g. "FD").
It has the following attributs:
    - long_name
    - units
    - _FillValue
    - _missing_value
    - ( grid_mapping )

According to the CF convention, the output NetCDF file contains 6 global attributs:
    - title
    - institution
    - source
    - history
    - references
    - comment 

Here's an example of an input file metadata:

.. code-block:: rest

    netcdf tas_day_CNRM-CM5_historical_r1i1p1_18500101-18541231 {
    dimensions:
            time = UNLIMITED ; // (1826 currently)
            lat = 128 ;
            lon = 256 ;
            bnds = 2 ;
    variables:
            double time(time) ;
                    time:bounds = "time_bnds" ;
                    time:units = "days since 1850-1-1" ;
                    time:calendar = "gregorian" ;
                    time:axis = "T" ;
                    time:long_name = "time" ;
                    time:standard_name = "time" ;
            double time_bnds(time, bnds) ;
            double lat(lat) ;
                    lat:bounds = "lat_bnds" ;
                    lat:units = "degrees_north" ;
                    lat:axis = "Y" ;
                    lat:long_name = "latitude" ;
                    lat:standard_name = "latitude" ;
            double lat_bnds(lat, bnds) ;
            double lon(lon) ;
                    lon:bounds = "lon_bnds" ;
                    lon:units = "degrees_east" ;
                    lon:axis = "X" ;
                    lon:long_name = "longitude" ;
                    lon:standard_name = "longitude" ;
            double lon_bnds(lon, bnds) ;
            double height ;
                    height:units = "m" ;
                    height:axis = "Z" ;
                    height:positive = "up" ;
                    height:long_name = "height" ;
                    height:standard_name = "height" ;
            float tas(time, lat, lon) ;
                    tas:standard_name = "air_temperature" ;
                    tas:long_name = "Near-Surface Air Temperature" ;
                    tas:units = "K" ;
                    tas:original_name = "tas" ;
                    tas:cell_methods = "time: mean" ;
                    tas:cell_measures = "area: areacella" ;
                    tas:history = "2011-04-07T06:39:36Z altered by CMOR: Treated scalar dimension: \'height\'." ;
                    tas:coordinates = "height" ;
                    tas:missing_value = 1.e+20f ;
                    tas:_FillValue = 1.e+20f ;
                    tas:associated_files = "baseURL: http://cmip-pcmdi.llnl.gov/CMIP5/dataLocation gridspecFile: gridspec_atmos_fx_CNRM-CM5_historical_r0i0p0.nc areacella: areacella_fx_CNRM-CM5_historical_r0i0p0.nc" ;
    
    // global attributes:
                    :institution = "CNRM (Centre National de Recherches Meteorologiques, Meteo-France, Toulouse,France) and CERFACS (Centre Europeen de Recherches et de Formation Avancee en Calcul Scientifique, Toulouse, France)" ;
                    :institute_id = "CNRM-CERFACS" ;
                    :experiment_id = "historical" ;
                    :source = "CNRM-CM5 2010 Atmosphere: ARPEGE-Climat (V5.2.1, TL127L31); Ocean: NEMO (nemo3.3.v10.6.6P, ORCA1degL42); Sea Ice: GELATO (V5.30); River Routing: TRIP (v1); Land: SURFEX (v5.1.c); Coupler : OASIS 3" ;
                    :model_id = "CNRM-CM5" ;
                    :forcing = "GHG, SA, Sl, Vl, BC, OC" ;
                    :parent_experiment_id = "piControl" ;
                    :parent_experiment_rip = "r1i1p1" ;
                    :branch_time = 146097. ;
                    :contact = "for all but decadal predictions : contact.CMIP5@meteo.fr - METEO-FRANCE, CNRM/GMGEC/ASTER, CNRS URA 1357, 42 Av. Coriolis F-31057 TOULOUSE CEDEX 1 /for decadal predictions : contact.CMIP5@cerfacs.fr - CERFACS, Climate Modelling And Global Change, URA CERFACS/CNRS No1875, 42 Av. Coriolis F-31057 TOULOUSE CEDEX 1" ;
                    :comment = "Soil layers depth scheme is specific for mrlsl and tsl - see variable-level comments. Atmosphere vertical hybrid coordinate : a_bnds and b_bnds arrays are correct, but a and b values provided are mid-sum of a_bnds and b_bnds, which is a poor approximation compared to the hydrostatic approximation actually used in the model." ;
                    :references = "See http://www.cnrm.meteo.fr/cmip5 - Follow model description link" ;
                    :initialization_method = 1 ;
                    :physics_version = 1 ;
                    :tracking_id = "cb2e6df1-075d-4bb9-a937-d9ddf8e8e56f" ;
                    :product = "output" ;
                    :experiment = "historical" ;
                    :frequency = "day" ;
                    :creation_date = "2011-04-07T06:39:40Z" ;
                    :history = "2011-04-07T06:39:36Z CMOR rewrote data to comply with CF standards and CMIP5 requirements." ;
                    :Conventions = "CF-1.4" ;
                    :project_id = "CMIP5" ;
                    :table_id = "Table day (31 January 2011) 43a867c1fea438258e3971754e4dacea" ;
                    :title = "CNRM-CM5 model output prepared for CMIP5 historical" ;
                    :parent_experiment = "pre-industrial control" ;
                    :modeling_realm = "atmos" ;
                    :realization = 1 ;
                    :cmor_version = "2.5.3" ;
    }


And here's an example of the output metadata:

.. code-block:: rest








Variable to process
-------------------
It needs to respect the correspondence between the variable to process and the indice to calculate.
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


Functions description
---------------------
Here is a description of some functions.


.. function:: indice(in_files_list, out_file, var, indice_name, time_range, slice_mode, project, N_lev=None):
    
    
    This function returns result NetCDF file containing a climate indice.
    
    
    :param in_files_list: input NetCDF files
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

.. note:: The list of indice names are :ref:`here <indices>`_ .  ############# ?????????????



.. function:: SU_indice_calculation(a, fill_val, t=25):
    
    Calculates the indice SU: summer days (daily maximum temperature > 25 degrees Celsius).
    
    :param a: variable array to process (daily maximum temperature (e.g."tasmax"))
    :type a: numpy.ndarray (3D)
    :param fill_val: fill value (ref.: function "get_att_value")
    :type fill_val: float
    :param t: temperature threshold [degrees Celsius] (default: t = 25 degrees Celsius)
    :type t: float
    
    :rtype: numpy.ndarray (2D)
           

.. function:: CWD_indice_calculation(a, fill_val, precip_thresh=1):

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
    

