import sys
import logging

from . import calc_indice

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



### TODO: rename this function

def zzz(indice_name, **kwargs):
    if indice_name == 'TG' :
        res = calc_indice.TG_calculation(**kwargs)
        
    elif indice_name == 'TX':
        res = calc_indice.TX_calculation(**kwargs)
        
    elif indice_name == 'TN':
        res = calc_indice.TN_calculation(**kwargs)


    elif indice_name == 'TXx':
        res = calc_indice.TXx_calculation(**kwargs)
        
    elif indice_name == 'TNx':
        res = calc_indice.TNx_calculation(**kwargs)
        
    elif indice_name == 'TXn':
        res = calc_indice.TXn_calculation(**kwargs)
        
    elif indice_name == 'TNn':
        res = calc_indice.TNn_calculation(**kwargs) 

#---
        
    elif indice_name == 'DTR':
        res = calc_indice.DTR_calculation(**kwargs)
        
    elif indice_name == 'ETR':
        res = calc_indice.ETR_calculation(**kwargs)
        
    elif indice_name == 'vDTR':
        res = calc_indice.vDTR_calculation(**kwargs)
        
    
    elif indice_name == 'SU':
        res = calc_indice.SU_calculation(**kwargs)
        
    elif indice_name == 'CSU':
        res = calc_indice.CSU_calculation(**kwargs)
        
    
    elif indice_name == 'TR':
        res = calc_indice.TR_calculation(**kwargs)            
       
    elif indice_name == 'FD':
        res = calc_indice.FD_calculation(**kwargs)            
       
    elif indice_name == 'CFD':
        res = calc_indice.CFD_calculation(**kwargs)            
       
       
    elif indice_name == 'ID':
        res = calc_indice.ID_calculation(**kwargs)            
       
    elif indice_name == 'HD17':
        res = calc_indice.HD17_calculation(**kwargs)            
       
    elif indice_name == 'GD4':
        res = calc_indice.GD4_calculation(**kwargs)            
       
       
    elif indice_name == 'PRCPTOT':
        res = calc_indice.PRCPTOT_calculation(**kwargs)            
       
    elif indice_name == 'RR1':
        res = calc_indice.RR1_calculation(**kwargs)            
       
    elif indice_name == 'SDII':
        res = calc_indice.SDII_calculation(**kwargs)            
       
       
    elif indice_name == 'R10mm':
        res = calc_indice.R10mm_calculation(**kwargs)            
       
    elif indice_name == 'R20mm':
        res = calc_indice.R20mm_calculation(**kwargs)            
       
    elif indice_name == 'RX1day':
        res = calc_indice.RX1day_calculation(**kwargs)   
        
        
    elif indice_name == 'RX5day':
        res = calc_indice.RX5day_calculation(**kwargs)            
       
    elif indice_name == 'CDD':
        res = calc_indice.CDD_calculation(**kwargs)            
       
    elif indice_name == 'CWD':
        res = calc_indice.CWD_calculation(**kwargs)            
       
       
    elif indice_name == 'SD':
        res = calc_indice.SD_calculation(**kwargs)            
       
    elif indice_name == 'SD1':
        res = calc_indice.SD1_calculation(**kwargs)            
       
    elif indice_name == 'SD5cm':
        res = calc_indice.SD5cm_calculation(**kwargs)   
        
        
    elif indice_name == 'SD50cm':
        res = calc_indice.SD50cm_calculation(**kwargs) 
                   
       
    elif indice_name == 'TG10p':
        res = calc_indice.TG10p_calculation(**kwargs)            
       
    elif indice_name == 'TG90p':
        res = calc_indice.TG90p_calculation(**kwargs)           
              
    elif indice_name == 'TN10p':
        res = calc_indice.TN10p_calculation(**kwargs)            
       
    elif indice_name == 'TN90p':
        res = calc_indice.TN90p_calculation(**kwargs)            
       
    elif indice_name == 'TX10p':
        res = calc_indice.TX10p_calculation(**kwargs) 
                
    elif indice_name == 'TX90p':
        res = calc_indice.TX90p_calculation(**kwargs)  
                  
       
    elif indice_name == 'WSDI':
        res = calc_indice.WSDI_calculation(**kwargs)            
       
    elif indice_name == 'CSDI':
        res = calc_indice.CSDI_calculation(**kwargs)            
       
       
    elif indice_name == 'R75p':
        res = calc_indice.R75p_calculation(**kwargs)            
       
    elif indice_name == 'R75pTOT':
        res = calc_indice.R75pTOT_calculation(**kwargs)            
       
    elif indice_name == 'R95p':
        res = calc_indice.R95p_calculation(**kwargs)   
        
    elif indice_name == 'R95pTOT':
        res = calc_indice.R95pTOT_calculation(**kwargs)            
       
    elif indice_name == 'R99p':
        res = calc_indice.R99p_calculation(**kwargs)            
       
    elif indice_name == 'R99pTOT':
        res = calc_indice.R99pTOT_calculation(**kwargs)            

    else:
        logging.critical("Error: unknown indice name: %s. Please check documentation.", indice_name)
        raise SystemExit()
        
    return res        
