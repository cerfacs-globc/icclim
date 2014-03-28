# test icclim

import icclim
from datetime import datetime
from time import time
from glob import glob

#in_file_OpenDAP = 'http://opendap.nmdc.eu/knmi/thredds/dodsC/IS-ENES/TESTSETS/tas_day_EC-EARTH_rcp26_r8i1p1_20060101-20251231.nc'
#in_file_OpenDAP2 = 'http://opendap.nmdc.eu/knmi/thredds/dodsC/IS-ENES/TESTSETS/tas_day_EC-EARTH_rcp26_r8i1p1_20260101-20501231.nc'

tas_path = '/data/tatarinova/CMIP5/tas_day/'
tas_files = glob(tas_path + '*.nc')


dt1 = datetime(1980,01,01)
dt2 = datetime(2000,12,31)

ofile = 'huuuuj.nc'

start = time()

icclim.indice(in_files = tas_files,
              out_file = ofile,
              var = 'tas',
              indice_name = 'TX',
              time_range=[dt1, dt2],
              slice_mode='month',
              project='CMIP5')

stop = time()
time1 = stop - start
print 'time: ', time1

