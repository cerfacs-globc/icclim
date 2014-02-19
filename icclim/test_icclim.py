# test icclim

import icclim
from datetime import datetime
from time import time


in_files_OpenDAP = ['http://opendap.nmdc.eu/knmi/thredds/dodsC/IS-ENES/TESTSETS/tas_day_EC-EARTH_rcp26_r8i1p1_20060101-20251231.nc',
                    'http://opendap.nmdc.eu/knmi/thredds/dodsC/IS-ENES/TESTSETS/tas_day_EC-EARTH_rcp26_r8i1p1_20260101-20501231.nc',
#                   'http://opendap.nmdc.eu/knmi/thredds/dodsC/IS-ENES/TESTSETS/tas_day_EC-EARTH_rcp26_r8i1p1_20510101-20751231.nc',
#                   'http://opendap.nmdc.eu/knmi/thredds/dodsC/IS-ENES/TESTSETS/tas_day_EC-EARTH_rcp26_r8i1p1_20760101-21001231.nc'
                    ]

dt1 = datetime(2020, 01, 01)
dt2 = datetime(2040, 12, 31)

ofile = 'huuuuj.nc'

start = time()

icclim.indice(in_files_OpenDAP, ofile, 'tas', 'TG', time_range=[dt1, dt2], slice_mode='month', project='CMIP5', N_lev=None)

stop = time()
time1 = stop - start
print 'time: ', time1
