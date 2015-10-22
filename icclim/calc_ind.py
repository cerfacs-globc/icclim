from calc_indice import *


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
        
    elif indice_name == 'DTR':
        res = DTR_calculation(**kwargs)
        
    elif indice_name == 'ETR':
        res = ETR_calculation(**kwargs)
        
    elif indice_name == 'vDTR':
        res = vDTR_calculation(**kwargs)
        
    
    elif indice_name == 'SU':
        res = SU_calculation(**kwargs)
        
    elif indice_name == 'CSU':
        res = CSU_calculation(**kwargs)
        
    
    elif indice_name == 'TR':
        res = TR_calculation(**kwargs)            
       
    elif indice_name == 'FD':
        res = FD_calculation(**kwargs)            
       
    elif indice_name == 'CFD':
        res = CFD_calculation(**kwargs)            
       
       
    elif indice_name == 'ID':
        res = ID_calculation(**kwargs)            
       
    elif indice_name == 'HD17':
        res = HD17_calculation(**kwargs)            
       
    elif indice_name == 'GD4':
        res = GD4_calculation(**kwargs)            
       
       
    elif indice_name == 'PRCPTOT':
        res = PRCPTOT_calculation(**kwargs)            
       
    elif indice_name == 'RR1':
        res = RR1_calculation(**kwargs)            
       
    elif indice_name == 'SDII':
        res = SDII_calculation(**kwargs)            
       
       
    elif indice_name == 'R10mm':
        res = R10mm_calculation(**kwargs)            
       
    elif indice_name == 'R20mm':
        res = R20mm_calculation(**kwargs)            
       
    elif indice_name == 'RX1day':
        res = RX1day_calculation(**kwargs)   
        
        
    elif indice_name == 'RX5day':
        res = RX5day_calculation(**kwargs)            
       
    elif indice_name == 'CDD':
        res = CDD_calculation(**kwargs)            
       
    elif indice_name == 'CWD':
        res =CWD_calculation(**kwargs)            
       
       
    elif indice_name == 'SD':
        res = SD_calculation(**kwargs)            
       
    elif indice_name == 'SD1':
        res = SD1_calculation(**kwargs)            
       
    elif indice_name == 'SD5cm':
        res = SD5cm_calculation(**kwargs)   
        
        
    elif indice_name == 'SD50cm':
        res = SD50cm_calculation(**kwargs) 
                   
       
    elif indice_name == 'TG10p':
        res = TG10p_calculation(**kwargs)            
       
    elif indice_name == 'TG90p':
        res = TG90p_calculation(**kwargs)           
              
    elif indice_name == 'TN10p':
        res = TN10p_calculation(**kwargs)            
       
    elif indice_name == 'TN90p':
        res = TN90p_calculation(**kwargs)            
       
    elif indice_name == 'TX10p':
        res = TX10p_calculation(**kwargs) 
                
    elif indice_name == 'TX90p':
        res = TX90p_calculation(**kwargs)  
                  
       
    elif indice_name == 'WSDI':
        res = WSDI_calculation(**kwargs)            
       
    elif indice_name == 'CSDI':
        res = CSDI_calculation(**kwargs)            
       
       
    elif indice_name == 'R75p':
        res = R75p_calculation(**kwargs)            
       
    elif indice_name == 'R75pTOT':
        res = R75pTOT_calculation(**kwargs)            
       
    elif indice_name == 'R95p':
        res = R95p_calculation(**kwargs)   
        
    elif indice_name == 'R95pTOT':
        res = R95pTOT_calculation(**kwargs)            
       
    elif indice_name == 'R99p':
        res = R99p_calculation(**kwargs)            
       
    elif indice_name == 'R99pTOT':
        res = R99pTOT_calculation(**kwargs)            
       
        
    return res        