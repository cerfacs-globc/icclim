
Output meta data
================

The output meta data conteins at least the following variables:
    - lat
    - lon
    - time
    - time_bnds
    - indice 

lat, lon
--------
We copy the *lat* and *lon* variables from source file with all their attributs.

time, time_bnds
---------------
From the *time* variable we copy only its attributs, then we recalculate its values (time steps).
We also create the *time_bnds* variable.


If *slice_mode='year'*, the time steps will be the 30th June ("AAAA-06-30") and the *time_bnds* values will be the 1st January and
the 31th December of each year ("AAAA-01-01", "AAAA-12-31"):

.. code-block:: rest

    time = "1986-06-30", "1987-06-30", "1988-06-30", "1989-06-30", "1990-06-30" ;

    time_bnds =
      "1986-01-01", "1986-12-31 23:59:59.000005",
      "1987-01-01", "1987-12-31 23:59:59.000005",
      "1988-01-01", "1988-12-31 23:59:59.000005",
      "1989-01-01", "1989-12-31 23:59:59.000005",
      "1990-01-01", "1990-12-31 23:59:59.000005" ;    


If *slice_mode='month'*, the time steps will be the 15th day of each month ("AAAA-MM-15") and the *time_bnds* values will be the 1st and
the last days of each month:

.. code-block:: rest

    time = "2010-01-15", "2010-02-15", "2010-03-15", "2010-04-15", "2010-05-15", 
        "2010-06-15", "2010-07-15", "2010-08-15", "2010-09-15", "2010-10-15", 
        "2010-11-15", "2010-12-15", "2011-01-15", "2011-02-15", "2011-03-15", 
        "2011-04-15", "2011-05-15", "2011-06-15", "2011-07-15", "2011-08-15",
        ...
    
    time_bnds =
    "2010-01-01", "2010-01-31 23:59:59.000005",
    "2010-02-01", "2010-02-28 23:59:59.000005",
    "2010-03-01", "2010-03-31 23:59:59.000005",
    "2010-04-01", "2010-04-30 23:59:59.000005",
    "2010-05-01", "2010-05-31 23:59:59.000005",
    "2010-06-01", "2010-06-30 23:59:59.000005",
    "2010-07-01", "2010-07-31 23:59:59.000005",
    "2010-08-01", "2010-08-31 23:59:59.000005",
    ...


indice
------
     
The *indice* variable has the same name as indice_name parameter (e.g. "FD").
It has the following attributs:
    - long_name
    - units 
    - _FillValue
    - missing_value
    - ( grid_mapping )

Example:

.. code-block:: rest

    float GD(time, lat, lon) ;
            GD:_FillValue = 1.e+20f ;
            GD:long_name = "Growing degree days (sum of TG > 4 degrees)" ;
            GD:units = "K" ;
            GD:missing_value = 1.e+20f ;

    

.. note:: The *_FillValue* and *missing_value* are the same as in source files.


Global attributs
----------------

According to the CF convention, the output NetCDF file contains 6 main global attributs:
    - title 
    - institution
    - source
    - history
    - references
    - comment 

Example:

.. code-block:: rest

    // global attributes:
                :title = "Cold indice GD" ;
                :institution =  ;
                :source =  ;
                :reference =  ;
                :comment =  ;
                :history = "2014-01-21 11:59:26 Calculation of GD indice (monthly) from 2080-01-01 to 2085-12-31." ;



However other global attributs can be added.


Examples
--------

Input metadata (CMIP5):

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


Output metadata (CMIP5):

.. code-block:: rest

    netcdf HD_month_CNRM-CM5_historical_r1i1p1_19000101-19101231 {
    dimensions:
            time = UNLIMITED ; // (132 currently)
            lat = 128 ;
            lon = 256 ;
            tbnds = 2 ;
    variables:
            double time(time) ;
                    time:bounds = "time_bnds" ;
                    time:units = "days since 1850-1-1" ;
                    time:calendar = "gregorian" ;
                    time:axis = "T" ;
                    time:long_name = "time" ;
                    time:standard_name = "time" ;
            double lat(lat) ;
                    lat:bounds = "lat_bnds" ;
                    lat:units = "degrees_north" ;
                    lat:axis = "Y" ;
                    lat:long_name = "latitude" ;
                    lat:standard_name = "latitude" ;
            double lon(lon) ;
                    lon:bounds = "lon_bnds" ;
                    lon:units = "degrees_east" ;
                    lon:axis = "X" ;
                    lon:long_name = "longitude" ;
                    lon:standard_name = "longitude" ;
            double time_bnds(time, tbnds) ;
                    time_bnds:units = "days since 1850-1-1" ;
                    time_bnds:calendar = "gregorian" ;
            float HD(time, lat, lon) ;
                    HD:_FillValue = 1.e+20f ;
                    HD:long_name = "Heating degree days (sum of 17 degrees - mean temperature)" ;
                    HD:units = "K" ;
                    HD:missing_value = 1.e+20f ;
    
    // global attributes:
                    :title = "Cold indice HD" ;
                    :institution =  ;
                    :source =  ;
                    :reference =  ;
                    :comment =  ;
                    :history = "2014-01-20 18:42:34 Calculation of HD indice (monthly) from 1900-01-01 to 1910-12-31." ;
                    :experiment =  ;
    }


Input metadata (CORDEX)

.. code-block:: rest

    netcdf tas_AFR-44_CNRM-CERFACS-CNRM-CM5_historical_r1i1p1_SMHI-RCA4_v1_day_19860101-19901231 {
    dimensions:
            bnds = 2 ;
            time = UNLIMITED ; // (1826 currently)
            rlon = 194 ;
            rlat = 201 ;
    variables:
            double height ;
                    height:axis = "Z" ;
                    height:long_name = "height" ;
                    height:positive = "up" ;
                    height:standard_name = "height" ;
                    height:units = "m" ;
            double time_bnds(time, bnds) ;
            double rlon(rlon) ;
                    rlon:standard_name = "grid_longitude" ;
                    rlon:long_name = "longitude in rotated pole grid" ;
                    rlon:units = "degrees" ;
                    rlon:axis = "X" ;
            double rlat(rlat) ;
                    rlat:standard_name = "grid_latitude" ;
                    rlat:long_name = "latitude in rotated pole grid" ;
                    rlat:units = "degrees" ;
                    rlat:axis = "Y" ;
            char rotated_pole ;
                    rotated_pole:grid_mapping_name = "rotated_latitude_longitude" ;
                    rotated_pole:grid_north_pole_latitude = 90. ;
                    rotated_pole:grid_north_pole_longitude = -180. ;
            double time(time) ;
                    time:standard_name = "time" ;
                    time:units = "days since 1949-12-01 00:00:00" ;
                    time:calendar = "standard" ;
                    time:long_name = "time" ;
                    time:bounds = "time_bnds" ;
                    time:axis = "T" ;
            float tas(time, rlat, rlon) ;
                    tas:grid_mapping = "rotated_pole" ;
                    tas:_FillValue = 1.e+20f ;
                    tas:standard_name = "air_temperature" ;
                    tas:long_name = "Near-Surface Air Temperature" ;
                    tas:units = "K" ;
                    tas:coordinates = "lon lat height" ;
                    tas:missing_value = 1.e+20f ;
                    tas:cell_methods = "time: mean" ;
            double lon(rlat, rlon) ;
                    lon:standard_name = "longitude" ;
                    lon:long_name = "longitude" ;
                    lon:units = "degrees_east" ;
            double lat(rlat, rlon) ;
                    lat:standard_name = "latitude" ;
                    lat:long_name = "latitude" ;
                    lat:units = "degrees_north" ;
    
    // global attributes:
                    :Conventions = "CF-1.4" ;
                    :contact = "rossby.cordex@smhi.se" ;
                    :creation_date = "2012-07-07-T22:17:14Z" ;
                    :experiment = "historical" ;
                    :experiment_id = "historical" ;
                    :driving_experiment = "CNRM-CERFACS-CNRM-CM5, historical, r1i1p1" ;
                    :driving_model_id = "CNRM-CERFACS-CNRM-CM5" ;
                    :driving_model_ensemble_member = "r1i1p1" ;
                    :driving_experiment_name = "historical" ;
                    :frequency = "day" ;
                    :institution = "Swedish Meteorological and Hydrological Institute, Rossby Centre" ;
                    :institute_id = "SMHI" ;
                    :model_id = "SMHI-RCA4" ;
                    :rcm_version_id = "v1" ;
                    :project_id = "CORDEX" ;
                    :CORDEX_domain = "AFR-44" ;
                    :product = "output" ;
                    :references = "http://www.smhi.se/en/Research/Research-departments/climate-research-rossby-centre" ;
                    :tracking_id = "7bf57394-e559-4bab-8a27-e54a0d7397bf" ;
                    :rossby_comment = "201110: CORDEX Africa 0.44 deg | RCA4 v1 | CNRM-CERFACS-CNRM-CM5 | r1i1p1 | historical | L40" ;
                    :rossby_run_id = "201110" ;
                    :rossby_grib_path = "/nobackup/rossby15/rossby/joint_exp/cordex/201110/raw/" ;
    }


Output metadata (CORDEX)

.. code-block:: rest

    netcdf HD_year_AFR-44_CNRM-CERFACS-CNRM-CM5_historical_r1i1p1_SMHI-RCA4_v1_19860101-19901231 {
    dimensions:
            time = UNLIMITED ; // (5 currently)
            rlat = 201 ;
            rlon = 194 ;
            tbnds = 2 ;
    variables:
            double time(time) ;
                    time:standard_name = "time" ;
                    time:units = "days since 1949-12-01 00:00:00" ;
                    time:calendar = "standard" ;
                    time:long_name = "time" ;
                    time:bounds = "time_bnds" ;
                    time:axis = "T" ;
            double rlat(rlat) ;
                    rlat:standard_name = "grid_latitude" ;
                    rlat:long_name = "latitude in rotated pole grid" ;
                    rlat:units = "degrees" ;
                    rlat:axis = "Y" ;
            double rlon(rlon) ;
                    rlon:standard_name = "grid_longitude" ;
                    rlon:long_name = "longitude in rotated pole grid" ;
                    rlon:units = "degrees" ;
                    rlon:axis = "X" ;
            double time_bnds(time, tbnds) ;
                    time_bnds:units = "days since 1949-12-01 00:00:00" ;
                    time_bnds:calendar = "standard" ;
            double lon(rlat, rlon) ;
                    lon:standard_name = "longitude" ;
                    lon:long_name = "longitude" ;
                    lon:units = "degrees_east" ;
            double lat(rlat, rlon) ;
                    lat:standard_name = "latitude" ;
                    lat:long_name = "latitude" ;
                    lat:units = "degrees_north" ;
            char rotated_pole ;
                    rotated_pole:grid_mapping_name = "rotated_latitude_longitude" ;
                    rotated_pole:grid_north_pole_latitude = 90. ;
                    rotated_pole:grid_north_pole_longitude = -180. ;
            float HD(time, rlat, rlon) ;
                    HD:_FillValue = 1.e+20f ;
                    HD:long_name = "Heating degree days (sum of 17 degrees - mean temperature)" ;
                    HD:units = "K" ;
                    HD:missing_value = 1.e+20f ;
    
    // global attributes:
                    :experiment = "historical" ;
                    :title = "Cold indice HD" ;
                    :institution =  ;
                    :source =  ;
                    :reference =  ;
                    :comment =  ;
                    :history = "2014-01-21 15:29:57 Calculation of HD indice (annual) from 1986-01-01 to 1990-12-31." ;
    }

