
Examples
===============================
First, import the ICCLIM library:

>>> from icclim import *

Main functions
-----------------------

The following code will calculate the SU indice:

>>> from glob import glob
>>> from datetime import datetime
>>> 
>>> input_path = '/data/tatarinova/CMIP5/tasmax_day/'
>>> input_file_list = glob(input_path + '*.nc')
>>> output_file = '/data/tatarinova/tmp/indice_SU_month_1860-1890.nc'
>>> 
>>> dt1 = datetime(1860,01,01)
>>> dt2 = datetime(1890,12,31)
>>> 
>>> indice(input_file_list, output_file, var='tasmax', indice_name='SU', time_range=[dt1, dt2], slice_mode='month', project='CMIP5', N_lev=None)

The output dataset will contain the SU indice 3D array, the time vector will contein 372 time steps (31 years x 12 months).

Utility functions
-----------------------
>>> from netCDF4 import Dataset
>>> 
>>> infile = '/data/tatarinova/CORDEX/AFR/tas_day/tas_AFR-44_CNRM-CERFACS-CNRM-CM5_historical_r1i1p1_SMHI-RCA4_v1_day_19960101-20001231.nc'
>>> ds = Dataset(infile, 'r')
>>> print get_att_value(ds, var='tas', att='_FillValue')
1e+20


...in development...

