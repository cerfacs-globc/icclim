# icclim vs cdo

from icclim import *

from glob import glob
from time import time

# CMIP5
path_tas = '/data/tatarinova/CMIP5/tas_day/'
path_tasmin = '/data/tatarinova/CMIP5/tasmin_day/'
path_tasmax = '/data/tatarinova/CMIP5/tasmax_day/'

infiles_tas = glob(path_tas + '*.nc')
infiles_tasmin = glob(path_tasmin + '*.nc')
infiles_tasmax = glob(path_tasmax + '*.nc')

outpath = '/data/tatarinova/tmp/res'
outfile =    # SU_year_period.nc


#indice(ifiles_list, ofile, var, indice_name, time_range, slice_mode, project, N_lev=None)



#of1 = '/data/tatarinova/tmp/.nc'
#
#of2 = '/data/tatarinova/tmp/.nc'
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
#print 'Coord           icclim              cdo              '
#for i in range(30):
#    lat = randint(0,160-1)
#    lon = randint(0,320-1)    
#    print '[',lat,', ', lon,']       ', v1[lat,lon], '                 ', v2[lat,lon]