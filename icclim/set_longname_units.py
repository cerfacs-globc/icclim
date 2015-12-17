#  Copyright CERFACS (http://cerfacs.fr/)
#  Apache License, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0)
#
#  Author: Natalia Tatarinova


# set the attributs "long_name" and "units" of indice variable in output meta data


def TG_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Mean of daily mean temperature')
    var_nc.setncattr('units', 'K')
    
def TN_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Mean of daily minimum temperature')
    var_nc.setncattr('units', 'K')
    
def TX_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Mean of daily maximum temperature')
    var_nc.setncattr('units', 'K')

def TXx_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Max of daily maximum temperature')
    var_nc.setncattr('units', 'K')

def TNx_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Max of daily minimum temperature')
    var_nc.setncattr('units', 'K')

def TXn_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Min of daily maximum temperature')
    var_nc.setncattr('units', 'K')

def TNn_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Min of daily minimum temperature')
    var_nc.setncattr('units', 'K')
    
def DTR_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Mean of diurnal temperature range')
    var_nc.setncattr('units', 'K')
    
def ETR_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Intra-period extreme temperature range')
    var_nc.setncattr('units', 'K')
    
def vDTR_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Mean absolute day-to-day difference in DTR (DTR: mean of diurnal temperature range)')
    var_nc.setncattr('units', 'K')

def SU_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Summer days (number of days where daily maximum temperature > 25 degrees)')
    var_nc.setncattr('units', 'days')

def TR_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Tropical nights (number of days where daily minimum temperature > 20 degrees)')
    var_nc.setncattr('units', 'days')

def CSU_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Maximum number of consecutive summer days(temperature > 25 degrees)')
    var_nc.setncattr('units', 'days')

def PRCPTOT_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Precipitation sum)')
    var_nc.setncattr('units', 'mm')

def RR1_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Wet days (precipitation >= 1 mm)')
    var_nc.setncattr('units', 'days')

def CWD_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Maximum number of consecutive wet days (precipitation >= 1 mm)')
    var_nc.setncattr('units', 'days')

def CDD_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Maximum number of consecutive dry days (precipitation < 1 mm)')
    var_nc.setncattr('units', 'days')

def SDII_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Simple daily intensity index for wet days (mm/wet day)')
    var_nc.setncattr('units', 'mm')

def R10mm_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Heavy precipitation days (precipitation >= 10 mm)')
    var_nc.setncattr('units', 'days')
    
def R20mm_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Very heavy precipitation days (precipitation >= 20 mm)')
    var_nc.setncattr('units', 'days')

def RX1day_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Highest 1-day precipitation amount')
    var_nc.setncattr('units', 'mm')

def RX5day_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Highest 5-day precipitation amount')
    var_nc.setncattr('units', 'mm')

def SD_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Mean of daily snow depth')
    var_nc.setncattr('units', 'cm')

def SD1_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Number of days where the snow depth >= 1 cm')
    var_nc.setncattr('units', 'days')
    
def SD5cm_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Number of days where the snow depth >= 5 cm')
    var_nc.setncattr('units', 'days')
    
def SD50cm_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Number of days where the snow depth >= 50 cm')
    var_nc.setncattr('units', 'days')

def FD_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Frost days (minimum temperature < 0 degrees)')
    var_nc.setncattr('units', 'days')

def CFD_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Maximum number of consecutive frost days (minimum temperature < 0 degrees)')
    var_nc.setncattr('units', 'days')

def ID_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Ice days (maximum temperature < 0 degrees)')
    var_nc.setncattr('units', 'days')
    
def HD17_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Heating degree days (sum of 17 degrees - mean temperature)')
    var_nc.setncattr('units', 'K')
    
def GD4_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Growing degree days (sum of TG > 4 degrees)')
    var_nc.setncattr('units', 'K')    

def GSL_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Growing season length')
    var_nc.setncattr('units', 'days') 

def TG90p_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Number of warm days')
    var_nc.setncattr('units', 'days')
    
def TX90p_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Number of warm day-times')
    var_nc.setncattr('units', 'days')
        
def TN90p_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Number of warm nights')
    var_nc.setncattr('units', 'days')
    
def TG10p_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Number of cold days')
    var_nc.setncattr('units', 'days')
    
def TX10p_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Number of cold day-times')
    var_nc.setncattr('units', 'days')
    
def TN10p_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Number of cold nights')
    var_nc.setncattr('units', 'days')
    
def WSDI_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Warm-spell duration index')
    var_nc.setncattr('units', 'days')
    
def CSDI_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Cold-spell duration index')
    var_nc.setncattr('units', 'days')
    
def R75p_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Moderate wet days')
    var_nc.setncattr('units', 'days')
    
def R95p_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Very wet days')
    var_nc.setncattr('units', 'days')
    
def R99p_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Extremely wet days')
    var_nc.setncattr('units', 'days')
    
def R75pTOT_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Precipitation fraction due to moderate wet days')
    var_nc.setncattr('units', '%')
    
def R95pTOT_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Precipitation fraction due to very wet days')
    var_nc.setncattr('units', '%')
    
def R99pTOT_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Precipitation fraction due to extremely wet days')
    var_nc.setncattr('units', '%')

def CD_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Cold and dry days')
    var_nc.setncattr('units', 'days')
    
def CW_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Cold and wet days')
    var_nc.setncattr('units', 'days')
    
def WD_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Warm and dry days')
    var_nc.setncattr('units', 'days')
    
def WW_setvarattr(var_nc):
    var_nc.setncattr('long_name', 'Warm and wet days')
    var_nc.setncattr('units', 'days')

def TIMEAVG_setvarattr(var_nc, longname, units):
    var_nc.setncattr('long_name', 'Time Average of '+longname)
    var_nc.setncattr('units', units)
    
def SUB_setvarattr(var_nc, longname, units):
    var_nc.setncattr('long_name', 'Substraction of '+longname)
    var_nc.setncattr('units', units)
    
