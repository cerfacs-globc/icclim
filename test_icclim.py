#input_file = '/media/natacha/Transcend/data_test/tas_day_CNRM-CM5_historical_r1i1p1_18950101-18991231.nc'
#input_path = '/media/natacha/Transcend/data_test/'
#input_file_list = glob(input_path + 'tas_Amon_CNRM-CM5_historical_r10i1p1_*.nc')
#output_file = '/media/natacha/Transcend/data_test/test_icclim.nc'

from icclim import *

from datetime import datetime

from time import time

from glob import glob

from netCDF4 import Dataset

import sys




input_file_CMIP5 = '/data/tatarinova/CMIP5/test/tas_day_EC-EARTH_rcp45_r2i1p1_20560101-21001231.nc' # 3.3 Gb

input_file_CORDEX = '/data/tatarinova/CORDEX/AFR/tas_day/tas_AFR-44_CNRM-CERFACS-CNRM-CM5_historical_r1i1p1_SMHI-RCA4_v1_day_19860101-19901231.nc'

#input_file_OpenDAP = 'http://opendap.nmdc.eu/knmi/thredds/dodsC/IS-ENES/TESTSETS/tas_day_EC-EARTH_rcp26_r8i1p1_20060101-20251231.nc'
input_file_OpenDAP = 'http://opendap.nmdc.eu/knmi/thredds/dodsC/IS-ENES/TESTSETS/tas_day_EC-EARTH_rcp26_r8i1p1_20760101-21001231.nc'


input_path = '/data/tatarinova/CMIP5/tas_day/'

input_file_list = glob(input_path + '*.nc')


output_file = '/data/tatarinova/tmp/res/HD_year_AFR-44_CNRM-CERFACS-CNRM-CM5_historical_r1i1p1_SMHI-RCA4_v1_19860101-19901231.nc'

######
#dt1 = datetime(2070,01,01)
#dt2 = datetime(2095,12,31)
dt1 = datetime(1986,01,01)
dt2 = datetime(1990,12,31)
######

start = time()

#indice(ifiles_list=[input_file], ofile=output_file, var='tas', indice_name='HD', time_range=[dt1, dt2], slice_mode='month', project='CMIP5', N_lev=None)
indice(ifiles_list=[input_file_CORDEX], ofile=output_file, var='tas', indice_name='HD', time_range=[dt1, dt2], slice_mode='year', project='CORDEX', N_lev=None)

stop = time()

time = stop - start

print 'time: ', time



#of1 = '/data/tatarinova/tmp/res/res1_HD_month.nc'
#
#of2 = '/data/tatarinova/tmp/res/test_chunking_HD_month.nc'
#
#nc1 = Dataset(of1, 'r')
#print of1
#
#v1 = nc1.variables['HD'][0,:,:]
#
#nc2 = Dataset(of2, 'r')
#print of2
#v2 = nc2.variables['HD'][0,:,:]
#
#from random import randint
#
#print 'Coord           avant_chunking              apres_chunking              '
#for i in range(30):
#    lat = randint(0,160-1)
#    lon = randint(0,320-1)    
#    print '[',lat,', ', lon,']       ', v1[lat,lon], '                 ', v2[lat,lon]