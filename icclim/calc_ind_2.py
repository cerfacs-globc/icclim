import sys
from . import maps
if sys.version_info[0] < 3:
    from calc_indice import *
else:
    from icclim.calc_indice_2 import *

import logging

# - TG 
# - TX 
# - TN 
# - TXx 
# - TNx 
# - TXn 
# - TNn 
# - DTR
# - ETR
# - vDTR
# - SU
# - CSU
# - TR
# - FD
# - CFD
# - ID
# - HD17
# - GD4
# - PRCPTOT
# - RR1
# - SDII
# - R10mm
# - R20mm
# - RX1day
# - RX5day
# - CDD
# - CWD
# - SD
# - SD1
# - SD5cm
# - SD50cm
# - TG10p
# - TX10p
# - TN10p
# - TG90p
# - TX90p
# - TN90p
# - WSDI
# - CSDI
# - R75p
# - R75pTOT
# - R95p
# - R95pTOT
# - R99p
# - R99pTOT


def get_indice_calculation(indice_name, ds, **kwargs):

    #da = ds[indice_name]
    #kwargs['da'] = da
    #ds[indice_name] = eval(indice_name+'_calculation(**kwargs)') 

    if indice_name in maps.consecutive_days_indice:
        kwargs['indice_name'] = indice_name

    kwargs['da'] = ds 
    ds = eval(indice_name+'_calculation(**kwargs)')  
    if 'time2compute' in [*ds.coords]:
        ds = ds.drop('time2compute')

    return ds        
