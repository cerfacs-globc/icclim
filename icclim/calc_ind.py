from calc_indice import *
from calc_indice_perc import *

# - TG -
# - TX -
# - TN -
# - TXx -
# - TNx -
# - TXn -
# - TNn -
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
# - CD
# - CW
# - WD
# - WW

# simple_stat(stat_op, coef): TG, TX, TN, TXx, TNx, TNx, TNn, PRCPTOT, SD, 

# DTR, ETR, vDTR, HD17, GD4, SDII, RX1day, RX5day

# get_nb_days (thresh, coef, logic_op): SU, TR, FD, ID, RR1, R10mm, R20mm, SD1, SD5cm, SD50cm  
# get_max_nb_consecutive_days (thresh, coef, logic_op): CSU, CFD, CDD, CWD


# def simple_stat(arr, stat_operation, coef=1.0, fill_val=None):

def zzz(indice_name, **kwargs):# arr1, fill_val1
    if indice_name == 'TG' :
        res = TG_calculation(**kwargs)
        
    elif indice_name == 'TX':
        res = TX_calculation(**kwargs)
        
    elif indice_name == 'TN':
        res = TN_calculation(**kwargs)
           
    
    
        
    elif indice_name == 'TXx':
        res = TXx_calculation(**kwargs)
        
    elif indice_name == 'TNx':
        res = TNx_calculation(**kwargs)
        
    elif indice_name == 'TXn':
        res = TXn_calculation(**kwargs)
        
    elif indice_name == 'TNn':
        res = TNn_calculation(**kwargs) 

#---
        
    if indice_name == 'DTR':
        res = DTR_calculation(**kwargs)
        
    elif indice_name == 'ETR':
        res = ETR_calculation(**kwargs)
        
    elif indice_name == 'vDTR':
        res = vDTR_calculation(**kwargs)        
       