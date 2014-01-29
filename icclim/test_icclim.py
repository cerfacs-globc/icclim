# test icclim

import icclim
from datetime import datetime
from time import time


in_file_OpenDAP = 'http://opendap.nmdc.eu/knmi/thredds/dodsC/IS-ENES/TESTSETS/tas_day_EC-EARTH_rcp26_r8i1p1_20060101-20251231.nc'

dt1 = datetime(2010,01,01)
dt2 = datetime(2014,12,31)

ofile = 'huuuuj.nc'

start = time()

icclim.indice([in_file_OpenDAP], ofile, 'tas', 'SU', time_range=[dt1, dt2], slice_mode='month', project='CMIP5', N_lev=None)

stop = time()
time1 = stop - start
print 'time: ', time1
