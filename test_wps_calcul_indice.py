# -*- coding: latin-1 -*- 

import wps_calcul_indice as ProcessToTest
from pywps.Process import WPSProcess
#from pywps.Process import Status

from glob import glob


p=ProcessToTest.ProcessIndice()
#p.status=status

## Set input of pyWPS process
#p.filesIn.default='/data/tatarinova/CMIP5/tas_day/tas_day_CNRM-CM5_historical_r1i1p1_18500101-18541231.nc'
p.indiceIn.default = 'HD'

input_path = '/data/tatarinova/CMIP5/tas_day/'
p.filesIn.default = glob(input_path + '*.nc')

p.timeBeginIn.default = '1890,01,01'
p.timeEndIn.default = '1950,01,01'

p.execute() 

